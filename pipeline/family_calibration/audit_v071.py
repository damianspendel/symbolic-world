#!/usr/bin/env python3
"""Systematic re-audit of pre-v0.7 family assignments under the binding doc.

Damian's option A (2026-08-12): five calibration runs against v0.7.1 all
failed because the answer key — assignments made under v0.5/v0.6 — is stale
where v0.7's rulings moved boundaries (measured contest rate ~5-10%). This
audit runs the calibrated gate (same PROMPT, same tightened verdict
semantics) over EVERY pre-v0.7 assignment, so the contested set is found
once, systematically, instead of six-at-a-time by random draw.

Population: state == assigned, by is a model-arms record that predates v0.7
(human rulings and precedents stand as ground truth; the 24 v0.7-rerun
assignments are already current). SUPPORTED/PARTIAL → the label stands,
stamped audited. WRONG → the edge goes to the contested set for a blind
two-arm re-run (the amplified-by pattern); the gate's opinion is recorded
but never assigns by itself — one model's judgment is a flag, not a ruling.

Run from the repo root:  python3 pipeline/family_calibration/audit_v071.py
Chunks are resumable; a rerun continues where it stopped. Outputs:
  pipeline/work/family_audit_c*.json   (gate verdicts, chunked)
  pipeline/work/family_audit_v071.json (summary + contested set)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
W = ROOT / "pipeline" / "work"
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "pipeline" / "family_calibration"))

from crossvendor_run import run_chunked  # noqa: E402
from gate import PROMPT, CARRY, MODEL  # noqa: E402


def citation(ref):
    return f"CW {ref['volume']} §{ref['paragraph']}"


def population():
    g = json.loads((ROOT / "seed.json").read_text())
    pool, excluded = [], {"human": 0, "precedent": 0, "v0.7": 0, "no_refs": 0}
    for e in g["edges"]:
        rf = e.get("relation_family") or {}
        if rf.get("state") != "assigned" or not rf.get("value"):
            continue
        by = str(rf.get("by", ""))
        for k in ("human", "precedent", "v0.7"):
            if k in by:
                excluded[k] += 1
                break
        else:
            refs = e.get("references") or []
            if not refs:
                excluded["no_refs"] += 1
                continue
            item = {
                "id": f'{e["subject"]}|{e["relation"]}|{e["object"]}',
                "family": rf["value"], "assigned_by": by,
                "subject": e["subject"], "relation": e["relation"],
                "object": e["object"],
                "citation": citation(refs[0]), "quote": refs[0]["quote"],
            }
            rn = e.get("relation_normalized") or {}
            item["relation_effective"] = rn.get("relation") or e["relation"]
            if rn.get("qualifiers"):
                item["qualifiers"] = {k: v for k, v in rn["qualifiers"].items() if v}
            if e.get("layer"):
                item["layer"] = e["layer"]
            pool.append(item)
    return pool, excluded


def main():
    pool, excluded = population()
    ids = {a["id"] for a in pool}
    if len(ids) != len(pool):
        raise SystemExit("REFUSED: duplicate edge ids in audit pool")
    print(f"audit population: {len(pool)} pre-v0.7 assignments "
          f"(excluded: {excluded})")

    items = [{"n": a["id"], **{k: a[k] for k in CARRY if k in a},
              "assigned_family": a["family"]} for a in pool]
    run_chunked(items, PROMPT, str(W / "family_audit"), chunk=15)

    verdicts = {}
    for f in sorted(W.glob("family_audit_c*.json")):
        d = json.loads(f.read_text())
        rows = d["verdicts"] if isinstance(d, dict) else d
        for v in rows:
            verdicts[str(v["n"])] = v
    missing = ids - set(verdicts)
    if missing:
        raise SystemExit(f"coverage incomplete: {len(missing)} unaudited "
                         f"(rerun to resume): {sorted(missing)[:3]}")

    by_id = {a["id"]: a for a in pool}
    contested, stands = [], []
    for i, v in verdicts.items():
        if i not in by_id:
            continue
        if str(v.get("verdict", "")).upper() == "WRONG":
            contested.append({**by_id[i], "gate_should_be": v.get("should_be", ""),
                              "gate_reason": v.get("reason", "")})
        else:
            stands.append(i)
    out = {"date": "2026-08-12", "definitions": "v0.7.1 (blob at run time)",
           "gate_model": MODEL, "population": len(pool),
           "stands": len(stands), "contested": len(contested),
           "contested_edges": contested}
    (W / "family_audit_v071.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False))
    print(f"AUDIT COMPLETE: {len(stands)} stand, {len(contested)} contested "
          f"-> pipeline/work/family_audit_v071.json")
    from collections import Counter
    print("contested by recorded family:",
          Counter(c["family"] for c in contested).most_common())


if __name__ == "__main__":
    main()
