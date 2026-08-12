#!/usr/bin/env python3
"""Score the family gate against the planted key, and write the record.

Successor to the --score half of pipeline/work/corrupt_family_assignments.py
(RULES #23), rebuilt around two rules the old scorer could not honour:

  RULES #13 — provenance binding. The key, the gated file and every gate chunk
  carry the same plant stamp, or this script REFUSES and prints no numbers.
  A replant scored against the previous run's verdicts is the failure mode.

  RULES #14 — detection requires diagnosis. A planted error counts as caught
  only if the gate returned WRONG on that item AND named the family the item
  was taken from. PARTIAL is tallied in its own column and is never a catch;
  flagged-but-misdiagnosed is reported separately.

Specificity is unchanged from the old harness: a clean item the gate flagged
(WRONG or PARTIAL) is a false positive. It is reported, never gating.

Usage:  python3 pipeline/family_calibration/score.py [--work DIR]
                 [--record pipeline/family_calibration/records/<date>_v0X.json]
"""
import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFS_PATH = ROOT / "docs" / "FAMILY_DEFINITIONS.md"
STAMP_KEYS = ("calibration_seed", "planted_at")

INDEPENDENCE_NOTE = (
    "Gate independence is NOMINAL, not cross-vendor: the gate model is the same "
    "model as one of the two production proposer arms (both gemini-3.1-pro). "
    "Within-vendor role separation only — see docs/RULES.md #1 and the "
    "2026-08-12 inspection note in BACKLOG.md item 7."
)


def refuse(msg):
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def stamp_of(d, where):
    if not isinstance(d, dict):
        refuse(f"{where} carries no provenance stamp (unstamped {type(d).__name__})")
    missing = [k for k in STAMP_KEYS if k not in d]
    if missing:
        refuse(f"{where} is missing stamp field(s) {missing}")
    return tuple(d[k] for k in STAMP_KEYS)


def norm(f):
    return str(f or "").strip().strip(".").lower()


def definitions_version(text):
    head = text.splitlines()[0]
    for tok in head.replace(",", " ").split():
        if tok.startswith("v") and tok[1:2].isdigit():
            return tok
    refuse("cannot read a version from the FAMILY_DEFINITIONS.md header")


def git_blob_sha1(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def load(work):
    keyf = json.loads((work / "family_corruption_key.json").read_text())
    gated = json.loads((work / "family_assignments_to_gate.json").read_text())
    s_key = stamp_of(keyf, "family_corruption_key.json")
    s_gated = stamp_of(gated, "family_assignments_to_gate.json")
    if s_key != s_gated:
        refuse("key and gated-assignments stamps disagree "
               f"({s_key[0]} vs {s_gated[0]})")

    chunks = sorted(work.glob("family_gate_c*.json"))
    if not chunks:
        refuse("no gate verdicts found (family_gate_c*.json)")
    verdicts, models = {}, set()
    for f in chunks:
        d = json.loads(f.read_text())
        s = stamp_of(d, f.name)
        if s != s_key:
            refuse(f"{f.name} was produced under a different plant "
                   f"({s[0]} vs key {s_key[0]}) — delete stale chunks and re-gate")
        models.add(d.get("gate_model"))
        for v in d.get("verdicts", []):
            verdicts[str(v["n"])] = v
    if len(models) != 1 or None in models:
        refuse(f"gate chunks disagree on the model or name none: {sorted(models)}")

    ids = {a["id"] for a in gated["assignments"]}
    extra, missing = set(verdicts) - ids, ids - set(verdicts)
    if extra or missing:
        refuse(f"verdict set does not match the gated set "
               f"({len(missing)} missing, {len(extra)} extra)")
    return keyf, gated, verdicts, models.pop()


def score(work, record_path=None):
    keyf, gated, verdicts, gate_model = load(work)
    key = keyf["key"]
    quota = keyf.get("quota", {})

    rows, per_class = [], {}
    for k, v in key.items():
        got = verdicts[k]
        verdict = str(got.get("verdict", "")).upper()
        should = got.get("should_be", "")
        right_family = norm(should) == norm(v["was"])
        if verdict == "WRONG" and right_family:
            diagnosis = "CAUGHT"
        elif verdict == "WRONG":
            diagnosis = "FLAGGED-MISDIAGNOSED"
        elif verdict == "PARTIAL":
            diagnosis = "PARTIAL-CORRECT-FAMILY" if right_family else "PARTIAL"
        else:
            diagnosis = "MISSED"
        rows.append({"id": k, "class": v["class"], "was": v["was"], "now": v["now"],
                     "verdict": verdict, "should_be": should,
                     "diagnosis": diagnosis, "gate_reason": got.get("reason", "")})
    rows.sort(key=lambda r: (r["class"], r["id"]))

    for cls in ("K1", "K2", "K3", "K4"):
        ids = [r for r in rows if r["class"] == cls]
        per_class[cls] = {
            "planted": len(ids),
            "quota": quota.get(cls),
            "caught": sum(1 for r in ids if r["diagnosis"] == "CAUGHT"),
            "flagged_misdiagnosed": sum(1 for r in ids
                                        if r["diagnosis"] == "FLAGGED-MISDIAGNOSED"),
            "partial": sum(1 for r in ids if r["diagnosis"].startswith("PARTIAL")),
            "missed": sum(1 for r in ids if r["diagnosis"] == "MISSED"),
        }

    planted = set(key)
    clean = set(verdicts) - planted
    flagged_clean = sorted(k for k in clean
                           if str(verdicts[k].get("verdict", "")).upper()
                           in ("WRONG", "PARTIAL"))
    caught = sum(1 for r in rows if r["diagnosis"] == "CAUGHT")
    partial_planted = sum(1 for r in rows if r["diagnosis"].startswith("PARTIAL"))
    partial_clean = sum(1 for k in clean
                        if str(verdicts[k].get("verdict", "")).upper() == "PARTIAL")

    quota_met = all(per_class[c]["planted"] == quota.get(c) for c in per_class) \
        if quota else False
    verdict = "PASS" if (caught == len(planted) and quota_met) else "FAIL"

    defs_text = DEFS_PATH.read_text(encoding="utf-8")
    record = {
        "run": "family-gate calibration",
        "definitions_version": definitions_version(defs_text),
        "definitions_git_hash": git_blob_sha1(DEFS_PATH),
        "draw_seed": gated.get("draw_seed"),
        "plant_seed": keyf["calibration_seed"],
        "planted_at": keyf["planted_at"],
        "n": len(verdicts),
        "n_planted": len(planted),
        "quotas": quota,
        "quotas_met": quota_met,
        "gate_model": gate_model,
        "per_class": per_class,
        "items": rows,
        "sensitivity": {"caught": caught, "of": len(planted),
                        "pct": round(100 * caught / len(planted), 1) if planted else None},
        "specificity": {"clean_left_alone": len(clean) - len(flagged_clean),
                        "of": len(clean),
                        "pct": round(100 * (len(clean) - len(flagged_clean)) / len(clean), 1)
                        if clean else None},
        "partial_tally": {"planted_items": partial_planted, "clean_items": partial_clean},
        "false_positives": [{"id": k,
                             "verdict": str(verdicts[k].get("verdict", "")).upper(),
                             "should_be": verdicts[k].get("should_be", ""),
                             "reason": verdicts[k].get("reason", "")}
                            for k in flagged_clean],
        "threshold": ("PASS = every planted item caught with the correct family named "
                      "(should_be == was) and every class at quota; one miss or "
                      "misdiagnosis in any class = FAIL. Set 2026-08-12 before the run "
                      "(RULES #11). Specificity is reported, never gating."),
        "verdict": verdict,
        "independence_note": INDEPENDENCE_NOTE,
    }

    sens, spec = record["sensitivity"], record["specificity"]
    print(f"gated {record['n']} assignments against "
          f"{record['definitions_version']} ({record['definitions_git_hash'][:10]}); "
          f"{record['n_planted']} were corrupted\n")
    print(f"  sensitivity (caught WITH correct diagnosis): "
          f"{sens['caught']}/{sens['of']} = {sens['pct']}%")
    print(f"  specificity (clean left alone):              "
          f"{spec['clean_left_alone']}/{spec['of']} = {spec['pct']}%")
    print(f"  PARTIAL verdicts: {partial_planted} on planted items, "
          f"{partial_clean} on clean items (never counted as catches)\n")
    for cls in ("K1", "K2", "K3", "K4"):
        c = per_class[cls]
        print(f"  {cls}: {c['caught']}/{c['planted']} caught  "
              f"(quota {c['quota']}, misdiagnosed {c['flagged_misdiagnosed']}, "
              f"partial {c['partial']}, missed {c['missed']})")
        for r in [x for x in rows if x["class"] == cls]:
            print(f"      [{r['id']}] {r['diagnosis']}  {r['was']} -> {r['now']}   "
                  f"gate said {r['verdict']}/{r['should_be'] or '-'}: "
                  f"{str(r['gate_reason'])[:70]}")
    if flagged_clean:
        print(f"\n  false positives ({len(flagged_clean)}) — clean assignments flagged:")
        for fp in record["false_positives"]:
            print(f"      [{fp['id']}] {fp['verdict']}/{fp['should_be'] or '-'}: "
                  f"{str(fp['reason'])[:90]}")
        if spec["pct"] is not None and spec["pct"] < 85:
            print("  specificity below 85% — each false positive above is flagged "
                  "for inspection by the main session")
    print(f"\n  VERDICT: {verdict}")

    if record_path:
        p = pathlib.Path(record_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
        print(f"  record written to {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}")
    return record


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=str(ROOT / "pipeline" / "work"))
    ap.add_argument("--record", default=None)
    a = ap.parse_args()
    score(pathlib.Path(a.work), a.record)
