#!/usr/bin/env python3
"""Study B — the draw. Builds the eligible reference pool, seed-reproducibly.

Pre-registered design: docs/experiments/study_b/DESIGN.md. This script does
NOT corrupt anything; it fixes the population and the order in which items
are taken, and records the seed (RULES #11 — the draw is fixed before any
result is seen; RULES #13 — the seed is stamped into every artifact of the
run).

Eligibility mirrors E1b (pipeline/calibrate.py): a reference is in the pool
if its paragraph is present in the local corpus, it is verified, and it
carries a claim_type. Each pool entry is annotated with whether the project
already judged the claim hedged (confidence medium/low per ASSUMPTIONS #8)
and whether its paragraph carries a hedge marker — the eligibility test for
the hedge-deletion class, computed here so that no corpus text has to travel
any further than this machine.

Output: pipeline/work/study_b/pool.json (gitignored — it names paragraphs).

Run from the repo root:  python3 tools/studies/study_b_draw.py
"""
import argparse
import json
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = ROOT / "pipeline" / "work" / "study_b"

SEED = 20260901

# The hedge vocabulary of the annotation protocol (docs/ANNOTATION_PROTOCOL.md
# §1 and §2.4) and of the E3 modality sweep. A paragraph counts as hedging
# when one of these appears in it; the reference must ALSO already be recorded
# below high confidence, so the project's own hedge judgment is the ground
# truth and the marker only confirms it.
HEDGE_MARKERS = [
    r"perhaps", r"it seems", r"seems", r"seem to", r"appears", r"appear to",
    r"as if", r"as though", r"may", r"might", r"possibly", r"possible that",
    r"probably", r"presumably", r"apparently", r"conjecture", r"suppose",
    r"would seem", r"it looks as", r"in all probability", r"unless",
]
HEDGE_RE = re.compile(r"\b(" + "|".join(HEDGE_MARKERS) + r")\b", re.I)

# Recorded below high confidence == the project judged the claim hedged.
HEDGED_CONFIDENCE = {"medium", "high -> medium", "low"}


def load_paragraphs():
    paras = {}
    with open(ROOT / "data" / "paragraphs.jsonl", encoding="utf-8") as fh:
        for line in fh:
            p = json.loads(line)
            paras[(str(p["volume"]), str(p["paragraph"]))] = p["text"]
    return paras


def head_commit():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def main(out):
    seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))
    paras = load_paragraphs()

    pool = []
    for ei, e in enumerate(seed["edges"]):
        for ri, r in enumerate(e["references"]):
            key = (str(r["volume"]), str(r["paragraph"]))
            if key not in paras:
                continue
            if not r.get("verified") or not r.get("claim_type"):
                continue
            text = paras[key]
            markers = sorted({m.group(1).lower() for m in HEDGE_RE.finditer(text)})
            pool.append({
                "edge": ei, "ref": ri,
                "confidence": r.get("confidence"),
                "hedged_record": r.get("confidence") in HEDGED_CONFIDENCE,
                "hedge_markers": markers,
            })

    rng = random.Random(SEED)
    rng.shuffle(pool)

    doc = {
        "study": "B",
        "study_seed": SEED,
        "commit": head_commit(),
        "graph": {"nodes": len(seed["nodes"]), "edges": len(seed["edges"]),
                  "references": sum(len(e["references"]) for e in seed["edges"])},
        "eligibility": ("paragraph present in the local corpus, reference verified, "
                        "claim_type present (mirrors E1b)"),
        "pool_size": len(pool),
        "hedge_eligible": sum(1 for p in pool if p["hedged_record"] and p["hedge_markers"]),
        "pool": pool,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"pool {len(pool)} references (seed {SEED}, commit {doc['commit'][:7]}); "
          f"{doc['hedge_eligible']} hedge-eligible -> {out}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(WORK / "pool.json"))
    sys.exit(main(pathlib.Path(ap.parse_args().out)))
