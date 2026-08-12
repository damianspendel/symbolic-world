#!/usr/bin/env python3
"""Plant seeded family-assignment errors of known class and count.

Successor to the plant half of pipeline/work/corrupt_family_assignments.py
(RULES #23). Whoever plants is never the gate: the planting session is
Opus-family here, the gate is a stateless Gemini call blind to the key.

CORRUPTION CLASSES — meaningful rather than random:
  K1 near-miss    swap to an ADJACENT family across a boundary the definitions
                  explicitly rule on. The hardest and most consequential class.
  K2 far-miss     swap to a semantically distant family. A gate that misses
                  these is not functioning at all.
  K3 sink-swap    swap to `correspondence`, the family the human pass showed
                  behaving as a dumping ground — a lazy default, not an
                  implausible one.
  K4 false-refuse replace a confident family with unclassified(no-family): does
                  the gate notice a claim being abandoned when a family fits?

Clean items are left untouched, so the run yields specificity as well as
sensitivity — a gate that flags everything has caught nothing.

Provenance binding (RULES #13): the plant seed and time are stamped into the
gated file and the key, gate.py copies the stamp into every chunk output, and
score.py refuses any set of artifacts whose stamps disagree. Stale chunk files
from an earlier plant are deleted here, so a replant can never be scored
against the previous run's verdicts.

Usage:  python3 pipeline/family_calibration/plant.py [--seed N] [--work DIR]
        (a fresh seed is drawn from os.urandom when none is given, and printed)
"""
import argparse
import datetime
import json
import os
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[2]

QUOTA = {"K1": 8, "K2": 4, "K3": 4, "K4": 3}

ADJACENT = {
    "symbolization": "manifestation", "manifestation": "symbolization",
    "composition": "structural-position", "structural-position": "composition",
    "union": "separation", "separation": "union",
    "sequence": "dependence", "dependence": "sequence",
    "generation": "derivation", "derivation": "generation",
    "archetypal-identity": "correspondence", "correspondence": "archetypal-identity",
    "transformation": "generation", "prefiguration": "sequence",
    "telos": "dependence", "projection": "symbolization",
    "personification": "manifestation", "amplification": "correspondence",
    "classification": "composition", "opposition": "privation",
    "privation": "opposition", "kinship": "generation",
    "doctrinal-attribution": "derivation", "psychic-effect": "dependence",
    # the definitions rule instrumentality's boundary against telos ("telos
    # names the END pursued; instrumentality names the route") — added
    # 2026-08-12 when the coverage check below first ran
    "instrumentality": "telos",
}
FAR = ["kinship", "telos", "privation", "derivation", "projection", "sequence"]


def check_adjacent_coverage():
    """Every family in live use must have a K1 partner, or the near-miss class
    silently under-covers the boundaries it claims to test."""
    g = json.loads((ROOT / "seed.json").read_text())
    live = {(e.get("relation_family") or {}).get("value")
            for e in g["edges"]
            if (e.get("relation_family") or {}).get("state") == "assigned"}
    live.discard(None)
    missing = sorted(f for f in live if not ADJACENT.get(f))
    if missing:
        raise SystemExit(f"REFUSED: no K1 partner for live families: {missing}")
    print(f"K1 adjacency covers all {len(live)} families in live use")
    return live


def plant(seed, work):
    check_adjacent_coverage()
    pop = json.loads((work / "family_calibration_population.json").read_text())
    items = [dict(a) for a in pop["assignments"]]
    by_id = {a["id"]: a for a in items}
    if len(by_id) != len(items):
        raise SystemExit("REFUSED: duplicate ids in population")

    rng = random.Random(seed)
    # eligibility is simply "every population item" — the population is already
    # restricted to assignments both model arms agreed on (RULES #15: no
    # invented per-item confidence to filter on)
    eligible = list(by_id)
    rng.shuffle(eligible)

    key, planted_per_class = {}, {}
    for cls, n in QUOTA.items():
        got = 0
        while got < n and eligible:
            i = eligible.pop()          # skipped picks are DISCARDED, never
            was = by_id[i]["family"]    # re-appended (the old quota stall)
            if cls == "K1":
                now = ADJACENT.get(was)
                if not now or now == was:
                    continue
            elif cls == "K2":
                choices = [f for f in FAR if f != was and f != ADJACENT.get(was)]
                if not choices:
                    continue
                now = rng.choice(choices)
            elif cls == "K3":
                if was == "correspondence":
                    continue
                now = "correspondence"
            else:
                now = "unclassified(no-family)"
            by_id[i]["family"] = now
            key[i] = {"class": cls, "was": was, "now": now}
            got += 1
        planted_per_class[cls] = got

    short = {c: (QUOTA[c], planted_per_class[c])
             for c in QUOTA if planted_per_class[c] != QUOTA[c]}
    if short:
        raise SystemExit("REFUSED: quota not met (class: wanted, got) -> "
                         f"{short}; population too small or too skewed")

    stamp = {"calibration_seed": seed,
             "planted_at": datetime.datetime.now(datetime.timezone.utc)
             .replace(microsecond=0).isoformat()}

    # uniform reasons: clean and corrupted entries are indistinguishable to any
    # downstream consumer that forwards this field
    for a in items:
        a["reason"] = ""

    stale = sorted(work.glob("family_gate_c*.json"))
    for f in stale:
        f.unlink()
    if stale:
        print(f"deleted {len(stale)} stale gate chunk file(s) from an earlier plant")

    (work / "family_assignments_to_gate.json").write_text(json.dumps(
        {**stamp,
         "draw_seed": pop["draw_seed"],
         "note": "family assignments for gating; some entries are deliberately wrong",
         "assignments": items}, indent=1, ensure_ascii=False))
    (work / "family_corruption_key.json").write_text(json.dumps(
        {**stamp,
         "draw_seed": pop["draw_seed"],
         "quota": QUOTA,
         "n_corrupted": len(key),
         "key": key}, indent=1, ensure_ascii=False))

    print(f"plant seed {seed}: planted {len(key)} corruptions in {len(items)} "
          f"assignments ({len(items) - len(key)} left clean)")
    for cls in QUOTA:
        print(f"  {cls}: {planted_per_class[cls]}/{QUOTA[cls]}")
    print("key written to family_corruption_key.json — the gate must not see it")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--work", default=str(ROOT / "pipeline" / "work"))
    a = ap.parse_args()
    plant(a.seed if a.seed is not None else int.from_bytes(os.urandom(4), "big"),
          pathlib.Path(a.work))
