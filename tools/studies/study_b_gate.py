#!/usr/bin/env python3
"""Study B — the gate runner. Prepares blind chunks; collects stamped verdicts.

The instrument is the production gate: a Fable-family model judging each claim
against its FULL source paragraph, verdict TRUE / CORRECTED / FALSE with a
one-line reason (pipeline/mining/PROMPTS.md §2). It is never substituted; if
Fable capacity is unavailable the firing holds and reports (RULES #2).

The gate is blind. It receives the claim and the paragraph, never the key,
never which items were touched, never that a study is running at all.

  prepare   write the next chunk of unjudged items, with paragraph text, to
            pipeline/work/study_b/gate_input_cNN.json (gitignored), and the
            prompt to pipeline/work/study_b/GATE_PROMPT.md
  collect   validate a chunk's raw verdicts and append them, stamped, to
            docs/experiments/study_b/verdicts.jsonl (RULES #13)

Run from the repo root:
  python3 tools/studies/study_b_gate.py prepare --limit 50 --chunk 25
  python3 tools/studies/study_b_gate.py collect --raw pipeline/work/study_b/raw_c01.json
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = ROOT / "pipeline" / "work" / "study_b"
DOCS = ROOT / "docs" / "experiments" / "study_b"
VERDICTS = DOCS / "verdicts.jsonl"

VERDICT_VALUES = {"TRUE", "CORRECTED", "FALSE"}

PROMPT = """You are the gate for a grounded knowledge graph of C.G. Jung's Collected Works. A separate model proposed these references; you verify them. You never rubber-stamp: hostile by default, and a claim passes only because the paragraph makes it pass.

Each item has: n, subject/subject_label, relation, object/object_label, claim_type, confidence, citation, quote, and paragraph_text — the FULL verbatim source paragraph. Judge the claim against the WHOLE paragraph, not the quoted fragment alone.

For each item judge:
1. Does the quote appear verbatim in paragraph_text?
2. Does the paragraph support subject -relation-> object as stated?
3. Is the referent right on both ends — the entity the paragraph is actually about, with no conflation of one figure or notion with a neighbouring one, and no widening of a particular into the general class it belongs to?
4. Is the relation no stronger than the paragraph — comparison, analogy, correspondence and parallel are not identity?
5. Is claim_type honest: "jung-asserts" only where Jung states it in his own interpretive voice; "jung-reports-parallel" where the paragraph presents it as another tradition's or author's doctrine; "jung-quotes-source" where it rests on a named quoted source?
6. Does confidence match the modality of the claim-carrying sentence — a hedged or conditional sentence ("perhaps", "it seems", "as if", "may") warrants medium, not high?

VERDICT per item:
- TRUE — all six hold.
- CORRECTED — the claim survives with a fix; give the corrected field(s) and value(s) in "corrections".
- FALSE — the paragraph does not support the claim and no correction rescues it.

State in "reason", in one line, WHICH of the six is wrong and why. Name the component at fault explicitly (the object, the subject, the relation, the claim_type, the confidence) whenever you do not answer TRUE.

Respond with ONLY a JSON array covering every n given:
[{"n": <int>, "verdict": "TRUE|CORRECTED|FALSE", "corrections": null or {"<field>": "<value>"}, "reason": "<one line>"}]

Do not read any other file, do not write documentation, do not report metrics, and do not put paragraph text in your reply. If you hit a capacity or quota limit, stop and report the error message verbatim."""


def load_stamp_and_items():
    doc = json.loads((WORK / "items.json").read_text(encoding="utf-8"))
    stamp = {k: doc[k] for k in ("study", "study_seed", "planted_at", "commit")}
    return stamp, doc["items"]


def judged_ns():
    if not VERDICTS.exists():
        return set()
    return {json.loads(l)["n"] for l in VERDICTS.read_text(encoding="utf-8").splitlines() if l.strip()}


def load_paragraphs(needed):
    paras = {}
    with open(ROOT / "data" / "paragraphs.jsonl", encoding="utf-8") as fh:
        for line in fh:
            p = json.loads(line)
            k = (str(p["volume"]), str(p["paragraph"]))
            if k in needed:
                paras[k] = p["text"]
    return paras


def prepare(limit, chunk):
    stamp, items = load_stamp_and_items()
    done = judged_ns()
    todo = [it for it in items if it["n"] not in done][:limit]
    if not todo:
        print("nothing left to judge — all items have verdicts")
        return 0
    needed = {(it["volume"], str(it["paragraph"])) for it in todo}
    paras = load_paragraphs(needed)
    missing = needed - set(paras)
    if missing:
        raise RuntimeError(f"paragraphs absent from the corpus: {sorted(missing)}")

    (WORK / "GATE_PROMPT.md").write_text(PROMPT + "\n", encoding="utf-8")
    written = []
    start = len(done)
    for b in range(0, len(todo), chunk):
        part = todo[b:b + chunk]
        cid = f"c{(start + b) // chunk + 1:02d}"
        out = WORK / f"gate_input_{cid}.json"
        payload = []
        for it in part:
            row = {k: v for k, v in it.items() if k not in ("volume", "paragraph")}
            row["paragraph_text"] = paras[(it["volume"], str(it["paragraph"]))]
            payload.append(row)
        out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
        written.append((out, len(part), part[0]["n"], part[-1]["n"]))
    print(f"{len(done)}/{len(items)} already judged; prepared {len(todo)} more")
    for out, k, lo, hi in written:
        print(f"  {out}  ({k} items, n {lo}..{hi})")
    print(f"  prompt: {WORK / 'GATE_PROMPT.md'}")
    return 0


def collect(raw_path):
    stamp, items = load_stamp_and_items()
    by_n = {it["n"] for it in items}
    done = judged_ns()
    raw = json.loads(pathlib.Path(raw_path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("verdicts", raw.get("items", []))

    rows = []
    for v in raw:
        n = int(v["n"])
        if n not in by_n:
            raise ValueError(f"verdict for unknown item n={n}")
        if n in done:
            raise ValueError(f"item n={n} already has a verdict — refusing to double-judge")
        verdict = str(v["verdict"]).strip().upper()
        if verdict not in VERDICT_VALUES:
            raise ValueError(f"n={n}: verdict {verdict!r} is not TRUE/CORRECTED/FALSE")
        reason = (v.get("reason") or "").strip()
        if verdict != "TRUE" and not reason:
            raise ValueError(f"n={n}: a non-TRUE verdict needs a reason")
        rows.append({**stamp, "n": n, "verdict": verdict,
                     "corrections": v.get("corrections"), "reason": reason,
                     "gate_model": "claude-fable-5", "source_file": pathlib.Path(raw_path).name})

    DOCS.mkdir(parents=True, exist_ok=True)
    with VERDICTS.open("a", encoding="utf-8") as fh:
        for r in sorted(rows, key=lambda r: r["n"]):
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    total = len(done) + len(rows)
    print(f"appended {len(rows)} verdicts -> {VERDICTS}  ({total}/{len(items)} judged)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--chunk", type=int, default=25)
    c = sub.add_parser("collect")
    c.add_argument("--raw", required=True)
    a = ap.parse_args()
    sys.exit(prepare(a.limit, a.chunk) if a.cmd == "prepare" else collect(a.raw))
