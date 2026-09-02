#!/usr/bin/env python3
"""Study C — collect blind Fable verdicts into the committed receipts.

  python3 tools/studies/study_c_collect.py c2   <raw.json> [...]   -> docs/experiments/study_c/c2_verdicts.jsonl
  python3 tools/studies/study_c_collect.py rem  <raw.json> [...]   -> docs/experiments/study_c/c1_remainder_verdicts.jsonl

Each raw file is the JSON array a blind Fable-family subagent returned for
one chunk. Records are stamped with the judge, the date and the chunk file
(RULES #13), duplicates by n are refused, and the expected fields are
validated before anything is written.
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "experiments" / "study_c"
KIND = {"c2": ("c2_verdicts.jsonl", {"n", "entailed", "element", "reason"}),
        "rem": ("c1_remainder_verdicts.jsonl", {"n", "judgment", "reason"})}

kind, raws = sys.argv[1], sys.argv[2:]
out_name, fields = KIND[kind]
out = DOCS / out_name
seen = set()
if out.exists():
    seen = {json.loads(l)["n"] for l in out.read_text().splitlines() if l.strip()}
stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
added = 0
with open(out, "a", encoding="utf-8") as fh:
    for raw in raws:
        for rec in json.load(open(raw)):
            missing = fields - set(rec)
            if missing:
                sys.exit(f"{raw}: n={rec.get('n')} missing {missing}")
            if rec["n"] in seen:
                sys.exit(f"{raw}: n={rec['n']} already collected")
            rec.update(judge="claude-fable-5 (blind subagent)", judged_at=stamp,
                       chunk=pathlib.Path(raw).name)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            seen.add(rec["n"]); added += 1
print(f"{kind}: appended {added} -> {out} ({len(seen)} total)")
