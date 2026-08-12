#!/usr/bin/env python3
"""Draw the family-gate calibration population from the CURRENT graph.

Successor to pipeline/work/build_calibration_input.py, moved into tracked code
under RULES #23. Draws a seeded sample of ASSIGNED edges from seed.json and
writes it with everything the gate needs (subject/relation/object, effective
relation, qualifiers, layer, citation, quote), so the gate stage joins nothing
at run time.

Edges assigned by human adjudication or by precedent are EXCLUDED: the
calibration measures the gate against MODEL-ARM assignments, and planting an
error on top of a human ruling would measure nothing about the instrument.

No fabricated fields (RULES #15). The old builder stamped confidence:"sure" on
every drawn edge; both arms agreeing IS the population's confidence basis, and
it is a property of the draw, not a per-item value, so it is stated in the
file's note and nowhere else.

Usage:  python3 pipeline/family_calibration/build_population.py [SEED] [N]
        (defaults: SEED drawn from os.urandom and printed; N=60)
"""
import json
import os
import pathlib
import random
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
W = ROOT / "pipeline" / "work"
OUT = W / "family_calibration_population.json"


def citation(ref):
    return f"CW {ref['volume']} §{ref['paragraph']}"


def build(seed, n):
    g = json.loads((ROOT / "seed.json").read_text())
    pool, skipped_no_refs = [], 0
    for e in g["edges"]:
        rf = e.get("relation_family") or {}
        if rf.get("state") != "assigned" or not rf.get("value"):
            continue
        by = str(rf.get("by", ""))
        if "human" in by or "precedent" in by:
            continue
        refs = e.get("references") or []
        if not refs:
            # the one known graph defect (an edge with an empty references
            # array); it carries no citation or quote to gate against
            skipped_no_refs += 1
            continue
        item = {
            "id": f'{e["subject"]}|{e["relation"]}|{e["object"]}',
            "family": rf["value"],
            "assigned_by": by,
            "subject": e["subject"],
            "relation": e["relation"],
            "object": e["object"],
            "citation": citation(refs[0]),
            "quote": refs[0]["quote"],
        }
        rn = e.get("relation_normalized") or {}
        # v0.7 ruling 6: the verbatim relation always travels beside the
        # effective one, and both are named — a judge sees the frozen string
        # even when a normalized form exists
        item["relation_effective"] = rn.get("relation") or e["relation"]
        if rn.get("qualifiers"):
            item["qualifiers"] = {k: v for k, v in rn["qualifiers"].items() if v}
        if e.get("layer"):
            item["layer"] = e["layer"]
        pool.append(item)

    ids = Counter(a["id"] for a in pool)
    dupes = [k for k, v in ids.items() if v > 1]
    if dupes:
        raise SystemExit(f"REFUSED: duplicate edge ids in pool: {dupes[:5]}")

    rng = random.Random(seed)
    rng.shuffle(pool)
    sample = pool[:n]

    OUT.write_text(json.dumps({
        "draw_seed": seed,
        "n": len(sample),
        "drawn_from": len(pool),
        "excluded_no_references": skipped_no_refs,
        "note": "family-gate calibration population; every item is an edge both "
                "model arms agreed on (human-adjudicated and precedent "
                "assignments excluded by construction)",
        "assignments": sample,
    }, indent=1, ensure_ascii=False))

    fams = Counter(a["family"] for a in sample)
    print(f"draw seed {seed}: {len(sample)} drawn from {len(pool)} eligible "
          f"model-arm assignments ({skipped_no_refs} skipped: no references)")
    print("families in sample:", dict(fams.most_common()))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    s = int(sys.argv[1]) if len(sys.argv) > 1 else int.from_bytes(os.urandom(4), "big")
    build(s, int(sys.argv[2]) if len(sys.argv) > 2 else 60)
