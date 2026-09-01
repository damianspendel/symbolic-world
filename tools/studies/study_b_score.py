#!/usr/bin/env python3
"""Study B — the scorer. Pre-set rules, written before any verdict was seen.

Design: docs/experiments/study_b/DESIGN.md. Two rules govern the count and
neither moves after results (RULES #11, #14):

  A corruption is CAUGHT only if the verdict is CORRECTED or FALSE **and** the
  gate's own words name the corrupted component. Flagged-without-diagnosis is
  counted and reported separately; it is never a catch.

Naming is tested mechanically, two ways, either sufficient:
  (1) the CORRECTED verdict's `corrections` object addresses the corrupted
      field (bonus: to the true value), or
  (2) the reason contains one of this class's diagnostic terms, or names the
      true or the planted value on the corrupted end.

Mechanical matching is a floor, not a judgment: every miss is listed verbatim
in RESULTS.md so the count can be inspected against the gate's actual words.

Provenance: verdicts whose stamp disagrees with the key's are refused
(RULES #13).

Run from the repo root:  python3 tools/studies/study_b_score.py
"""
import argparse
import json
import math
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = ROOT / "pipeline" / "work" / "study_b"
DOCS = ROOT / "docs" / "experiments" / "study_b"

FLAG = {"CORRECTED", "FALSE"}

# Diagnostic terms per class — the words that count as naming the corrupted
# component. Fixed before any verdict existed.
TERMS = {
    "near-referent-drift": ["object", "referent", "refers", "refer to", "conflat",
                            "entity", "figure", "wrong node", "misidentif",
                            "identifies", "not ... but", "different node"],
    "subject-expansion": ["subject", "generaliz", "generalis", "broaden", "wider",
                          "widen", "overreach", "superordinate", "too general",
                          "narrower", "particular", "specific", "class as a whole",
                          "applies to", "not the class"],
    "hedge-deletion": ["confidence", "hedge", "medium", "tentative", "conditional",
                       "qualif", "overstate", "too strong", "modality", "seems",
                       "perhaps", "may ", "might", "possib", "not unqualified"],
    "analogy-to-identity": ["relation", "identical", "identity", "analog", "analogy",
                            "parallel", "correspond", "equival", "stronger",
                            "overreach", "likeness", "resembl", "comparison",
                            "only a"],
}
STOPWORDS = {"the", "and", "that", "with", "from", "this", "into", "unio", "sein"}


def value_tokens(value):
    if not value:
        return set()
    toks = {t for t in re.split(r"[-_\s]+", str(value).lower()) if len(t) >= 4}
    return toks - STOPWORDS


def names_component(cls, field, true_value, planted_value, verdict, corrections, reason):
    """Did the gate name the corrupted component? Returns (bool, how)."""
    if isinstance(corrections, dict):
        for k in corrections:
            if str(k).strip().lower() == field:
                return True, "corrections-field"
    low = (reason or "").lower()
    for t in TERMS[cls]:
        if t in low:
            return True, f"term:{t.strip()}"
    for tok in value_tokens(true_value) | value_tokens(planted_value):
        if tok in low:
            return True, f"value:{tok}"
    return False, ""


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(k, n):
    return 0.0 if n == 0 else 100.0 * k / n


def main(partial):
    keydoc = json.loads((WORK / "key.json").read_text(encoding="utf-8"))
    key = keydoc["key"]
    stamp = {k: keydoc[k] for k in ("study_seed", "planted_at")}

    path = DOCS / "verdicts.jsonl"
    verdicts = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        v = json.loads(line)
        if {k: v.get(k) for k in stamp} != stamp:
            raise RuntimeError(f"n={v.get('n')}: verdict stamp disagrees with the key "
                               f"({ {k: v.get(k) for k in stamp} } vs {stamp}) — refusing to score")
        verdicts[int(v["n"])] = v

    missing = sorted(int(n) for n in key if int(n) not in verdicts)
    if missing and not partial:
        print(f"{len(verdicts)}/{len(key)} judged; {len(missing)} outstanding "
              f"(first: {missing[:8]}). Not scoring — run with --partial to see a "
              f"progress read.", file=sys.stderr)
        return 1

    per_class = defaultdict(lambda: {"n": 0, "caught": 0, "flagged": 0})
    misses, undiagnosed, control_flags = [], [], []
    tn = fp = 0

    for ns, k in sorted(key.items(), key=lambda kv: int(kv[0])):
        n = int(ns)
        if n not in verdicts:
            continue
        v = verdicts[n]
        flagged = v["verdict"] in FLAG
        if k["status"] == "clean":
            if flagged:
                fp += 1
                control_flags.append({"n": n, "verdict": v["verdict"],
                                      "citation": f"{k['subject']} -{k['relation']}-> {k['object']}",
                                      "reason": v["reason"]})
            else:
                tn += 1
            continue

        cls = k["class"]
        row = per_class[cls]
        row["n"] += 1
        named, how = names_component(cls, k["field"], k["true_value"],
                                     k["planted_value"], v["verdict"],
                                     v.get("corrections"), v.get("reason"))
        if flagged:
            row["flagged"] += 1
        if flagged and named:
            row["caught"] += 1
            continue
        entry = {"n": n, "class": cls, "verdict": v["verdict"],
                 "field": k["field"], "true_value": k["true_value"],
                 "planted_value": k["planted_value"],
                 "claim": f"{k['subject']} -{k['relation']}-> {k['object']}",
                 "reason": v["reason"]}
        if flagged and not named:
            entry["why_not_caught"] = "flagged, diagnosis did not name the component"
            undiagnosed.append(entry)
        else:
            entry["why_not_caught"] = "not flagged"
        misses.append(entry)

    tp = sum(r["caught"] for r in per_class.values())
    corrupt_n = sum(r["n"] for r in per_class.values())
    lo, hi = wilson(tp, corrupt_n)
    slo, shi = wilson(tn, tn + fp)

    result = {
        **{k: keydoc[k] for k in ("study", "study_seed", "planted_at", "commit")},
        "design": "docs/experiments/study_b/DESIGN.md",
        "scored_items": len(verdicts),
        "partial": bool(missing),
        "gate_model": "claude-fable-5",
        "sensitivity": {"caught": tp, "n": corrupt_n, "pct": round(pct(tp, corrupt_n), 1),
                        "ci95": [round(100 * lo, 1), round(100 * hi, 1)]},
        "specificity": {"clean_true": tn, "n": tn + fp, "pct": round(pct(tn, tn + fp), 1),
                        "ci95": [round(100 * slo, 1), round(100 * shi, 1)]},
        "by_class": {},
        "flagged_not_diagnosed": len(undiagnosed),
        "misses": misses,
        "control_flags": control_flags,
    }
    for cls in TERMS:
        r = per_class.get(cls)
        if not r:
            continue
        clo, chi = wilson(r["caught"], r["n"])
        result["by_class"][cls] = {
            "caught": r["caught"], "n": r["n"], "pct": round(pct(r["caught"], r["n"]), 1),
            "ci95": [round(100 * clo, 1), round(100 * chi, 1)],
            "flagged": r["flagged"],
            "flagged_not_diagnosed": r["flagged"] - r["caught"]}

    if missing:
        print(json.dumps({k: result[k] for k in
                          ("scored_items", "sensitivity", "specificity", "by_class")}, indent=1))
        return 0

    (DOCS / "RESULT.json").write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                      encoding="utf-8")
    (DOCS / "RESULTS.md").write_text(render(result), encoding="utf-8")
    print(f"SENSITIVITY {tp}/{corrupt_n} = {pct(tp, corrupt_n):.0f}% "
          f"(95% CI {100*lo:.0f}-{100*hi:.0f}%)")
    print(f"SPECIFICITY {tn}/{tn+fp} = {pct(tn, tn+fp):.0f}% "
          f"(95% CI {100*slo:.0f}-{100*shi:.0f}%)")
    for cls, c in result["by_class"].items():
        print(f"  {cls:22s} {c['caught']}/{c['n']} = {c['pct']:.0f}% "
              f"(CI {c['ci95'][0]:.0f}-{c['ci95'][1]:.0f}%), "
              f"flagged-not-diagnosed {c['flagged_not_diagnosed']}")
    print(f"wrote {DOCS/'RESULT.json'} and {DOCS/'RESULTS.md'}")
    return 0


def render(r):
    s = r["sensitivity"]
    sp = r["specificity"]
    out = [f"# Study B — the gate on realistic corruptions (n={r['scored_items']}, "
           f"seed {r['study_seed']}, blind)", "",
           f"Pre-registered design: `DESIGN.md`. Harness: `tools/studies/study_b_*.py`. "
           f"Plant: `plant_manifest.json`. Verdicts: `verdicts.jsonl`. Graph commit "
           f"`{r['commit'][:7]}`. Gate: {r['gate_model']}, blind, judging each claim "
           f"against its full source paragraph.", "",
           "A corruption counts as caught only if the gate flagged it AND its reason "
           "named the corrupted component (RULES #14). Flagged-without-diagnosis is "
           "listed separately and never counted as a catch.", "",
           "## Results (95% Wilson intervals)", "",
           "| Class | Caught | % | 95% CI | Flagged but not diagnosed |",
           "|---|---|---|---|---|"]
    for cls, c in r["by_class"].items():
        out.append(f"| {cls} | {c['caught']}/{c['n']} | {c['pct']:.0f}% | "
                   f"{c['ci95'][0]:.0f}–{c['ci95'][1]:.0f}% | {c['flagged_not_diagnosed']} |")
    out += [f"| **pooled sensitivity** | **{s['caught']}/{s['n']}** | **{s['pct']:.0f}%** | "
            f"{s['ci95'][0]:.0f}–{s['ci95'][1]:.0f}% | {r['flagged_not_diagnosed']} |",
            f"| specificity (clean controls) | {sp['clean_true']}/{sp['n']} | "
            f"{sp['pct']:.0f}% | {sp['ci95'][0]:.0f}–{sp['ci95'][1]:.0f}% | — |", "",
            "E1b measured the same gate on coarse seeded corruptions at 86% sensitivity "
            "(CI 78–91%) and 93% specificity. The two are stated measured-vs-measured: "
            "different corruption populations, same instrument. They are never pooled.",
            "", "## Every miss", ""]
    if not r["misses"]:
        out.append("None.")
    for m in r["misses"]:
        out += [f"- **n={m['n']}** ({m['class']}, {m['why_not_caught']}) — verdict "
                f"{m['verdict']}. Presented: `{m['claim']}`; {m['field']} planted "
                f"`{m['planted_value']}` for `{m['true_value']}`.",
                f"  Gate: {m['reason'] or '(no reason — TRUE)'}"]
    out += ["", "## Flags on clean controls", "",
            "Production references, so a flag here may be the gate finding a real "
            "nuance rather than a false positive; specificity is a lower bound.", ""]
    if not r["control_flags"]:
        out.append("None.")
    for c in r["control_flags"]:
        out.append(f"- **n={c['n']}** {c['verdict']} — `{c['citation']}`. {c['reason']}")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--partial", action="store_true",
                    help="print a progress read without writing RESULT.json")
    sys.exit(main(ap.parse_args().partial))
