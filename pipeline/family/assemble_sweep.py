#!/usr/bin/env python3
"""Assemble the two blind arms of a family sweep into seed.json and the queue.

RULES #8 — two blind arms, symmetric. Agreement assigns; disagreement queues for
a human; no model ever breaks a tie, and this script has no tie-break branch by
construction.

RULES #23 — this ran inline for windows 8, 9 and 10. Reconstructed 2026-08-12
and verified against window 10's surviving arm outputs: replaying the 34 rows
reproduces the merged graph exactly (30 agreements assigned, 4 disagreements
queued, every queue entry byte-identical to the arms' own words).

The mapping, which is the whole of the logic:

  both arms name the same family      -> state "assigned",   value = that family
  both say unclassified(no-family)    -> state "no-family",  value = null
  both say text-undecided             -> state "text-undecided", value = null
  the arms differ                     -> state "pending-adjudication", value = null
                                         and a queue entry carrying BOTH votes
                                         and both stated reasons

`by` is version-bound: "opus+gemini-agreed (v0.6)" records which ruleset the
agreement was reached under, because a later ruleset can retire the rule an
assignment rested on (RULES #16). Disagreements carry `arms-disagree`.

Usage:
  python3 pipeline/family/assemble_sweep.py            # dry run: report only
  python3 pipeline/family/assemble_sweep.py --write    # write seed.json + queue
"""
import argparse
import datetime
import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
W = ROOT / "pipeline" / "work"
DEFS_PATH = ROOT / "docs" / "FAMILY_DEFINITIONS.md"

NO_FAMILY = "unclassified(no-family)"
TEXT_UNDECIDED = {"text-undecided", "unclassified(text-undecided)"}


def refuse(msg):
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def inventory(text):
    """The family names the document actually defines, plus the two refusals."""
    fams = set(re.findall(r"^### \d+\.\s+([a-z-]+)", text, re.M))
    if not fams:
        refuse("no family headings found in FAMILY_DEFINITIONS.md")
    return fams


def version(text):
    for tok in text.splitlines()[0].replace(",", " ").split():
        if tok.startswith("v") and tok[1:2].isdigit():
            return tok
    refuse("no version in the FAMILY_DEFINITIONS.md header")


def read_arms(opus_path, gem_path):
    opus = {}
    for line in opus_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            opus[row["n"]] = row
    gem = {row["n"]: row for row in json.loads(gem_path.read_text(encoding="utf-8"))}
    return opus, gem


def assemble(write, inp_path, opus_path, gem_path, queue_path):
    defs = DEFS_PATH.read_text(encoding="utf-8")
    vers, fams = version(defs), inventory(defs)
    graph = json.loads((ROOT / "seed.json").read_text())
    edges = graph["edges"]

    inp = json.loads(inp_path.read_text())
    swept = {e["n"]: e for e in inp["edges"]}
    if inp.get("version") and inp["version"] != vers:
        refuse(f"the sweep input was built against {inp['version']} but the "
               f"definitions document now reads {vers} — rebuild and re-sweep")

    opus, gem = read_arms(opus_path, gem_path)
    if set(opus) != set(swept) or set(gem) != set(swept):
        refuse(f"arm coverage does not match the input "
               f"(input {len(swept)}, opus {len(opus)}, gemini {len(gem)})")

    bad = sorted({r["family"] for r in list(opus.values()) + list(gem.values())}
                 - fams - {NO_FAMILY} - TEXT_UNDECIDED)
    if bad:
        refuse(f"an arm named families the document does not define: {bad}")

    already = [n for n in swept if edges[n].get("relation_family")]
    if already:
        refuse(f"{len(already)} swept edges already carry a family record "
               f"(first: {already[0]}) — one family pass per edge")

    for n, e in swept.items():
        live = edges[n]
        if (live["subject"], live["relation"], live["object"]) != \
           (e["subject"], e["relation"], e["object"]):
            refuse(f"n={n} is a different edge in seed.json than in the sweep "
                   f"input — the graph moved under the sweep; rebuild the input")

    today = datetime.date.today().isoformat()
    states, queued = Counter(), []
    for n in sorted(swept):
        a, b = opus[n]["family"], gem[n]["family"]
        if a == b:
            if a == NO_FAMILY:
                rf = {"value": None, "state": "no-family"}
            elif a in TEXT_UNDECIDED:
                rf = {"value": None, "state": "text-undecided"}
            else:
                rf = {"value": a, "state": "assigned"}
            rf.update(by=f"opus+gemini-agreed ({vers})", date=today)
        else:
            rf = {"value": None, "state": "pending-adjudication",
                  "by": "arms-disagree", "date": today}
            e = swept[n]
            queued.append({
                "n": n, "subject": e["subject"], "relation": e["relation"],
                "relation_effective": e["relation_effective"], "object": e["object"],
                "refs": e["refs"],
                "opus": a, "opus_reason": opus[n].get("reason", ""),
                "gemini": b, "gemini_reason": gem[n].get("reason", ""),
            })
        states[rf["state"]] += 1
        if write:
            edges[n]["relation_family"] = rf

    print(f"{len(swept)} swept against {vers}: " +
          ", ".join(f"{v} {k}" for k, v in states.most_common()))
    print(f"agreement {len(swept) - len(queued)}/{len(swept)} "
          f"({round(100 * (len(swept) - len(queued)) / len(swept))}%)")

    if not write:
        print("dry run — nothing written. Re-run with --write to merge.")
        return

    queue = json.loads(queue_path.read_text()) if queue_path.exists() else []
    known = {i["n"] for i in queue}
    queue += [q for q in queued if q["n"] not in known]
    queue_path.write_text(json.dumps(queue, indent=1, ensure_ascii=False))
    (ROOT / "seed.json").write_text(json.dumps(graph, indent=1, ensure_ascii=False))
    print(f"seed.json updated; queue now {len(queue)} items "
          f"({len(queued)} added) in {queue_path.relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="merge into seed.json and the queue (default: dry run)")
    ap.add_argument("--input", default=str(W / "family_sweep_input.json"))
    ap.add_argument("--opus", default=str(W / "family_sweep_opus.jsonl"))
    ap.add_argument("--gemini", default=str(W / "family_sweep_gemini.json"))
    ap.add_argument("--queue", default=str(W / "family_pending_queue.json"))
    a = ap.parse_args()
    assemble(a.write, pathlib.Path(a.input), pathlib.Path(a.opus),
             pathlib.Path(a.gemini), pathlib.Path(a.queue))
