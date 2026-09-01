#!/usr/bin/env python3
"""Study B — the planter. Four realistic corruption classes plus clean controls.

Pre-registered design: docs/experiments/study_b/DESIGN.md. Classes, counts and
guards are fixed here BEFORE any verdict exists (RULES #11). seed.json is never
written; corruptions live only in the copies this script emits.

Classes (25 each), taken in this fixed order — scarcest class first, so a class
never starves because a commoner one consumed its candidates:

  1 analogy-to-identity  a comparison relation presented as is-identical-with / is
  2 subject-expansion    the subject widened to a superordinate node one step up
  3 hedge-deletion       a hedged reference presented as unqualified high confidence
  4 near-referent-drift  the object replaced by a node at graph distance 1

Then 100 clean controls, untouched. Every corruption is guarded against
accidentally stating something the graph already holds to be true: if the
corrupted triple already exists in seed.json the candidate is skipped.

Outputs
  pipeline/work/study_b/items.json   blind gate items, shuffled, n = 1..200
  pipeline/work/study_b/key.json     the key, withheld from the gate
  docs/experiments/study_b/plant_manifest.json   committed receipt (RULES #12)

Run from the repo root:  python3 tools/studies/study_b_plant.py
"""
import argparse
import datetime
import json
import pathlib
import random
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = ROOT / "pipeline" / "work" / "study_b"
DOCS = ROOT / "docs" / "experiments" / "study_b"

N_PER_CLASS = 25
N_CLEAN = 100
CLASS_ORDER = ["analogy-to-identity", "subject-expansion",
               "hedge-deletion", "near-referent-drift"]

# Relations that state a comparison rather than an identity. A relation
# qualifies when one of its hyphen tokens carries a comparison stem and the
# relation does not already assert identity.
COMPARISON_STEMS = re.compile(
    r"^(like|likened|resembl\w*|parallel\w*|correspond\w*|analog\w*|analogue\w*|"
    r"equivalen\w*|counterpart|likeness)$", re.I)
IDENTITY_TARGETS = ["is-identical-with", "is"]

# Relations that already state class membership: a subject-expansion on one of
# these would produce a tautology rather than an overreach.
TAXONOMIC = {"is-a", "belongs-to"}


def is_comparison(relation):
    if "identical" in relation:
        return False
    return any(COMPARISON_STEMS.match(tok) for tok in relation.split("-"))


def main(pool_path, out_items, out_key, out_manifest):
    pool_doc = json.loads(pool_path.read_text(encoding="utf-8"))
    seed = json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))
    edges = seed["edges"]

    node_type = {n["id"]: n.get("type") for n in seed["nodes"]}
    node_label = {n["id"]: n.get("label", n["id"]) for n in seed["nodes"]}
    triples = {(e["subject"], e["relation"], e["object"]) for e in edges}

    adjacency = defaultdict(set)
    parents = defaultdict(set)
    for e in edges:
        adjacency[e["subject"]].add(e["object"])
        adjacency[e["object"]].add(e["subject"])
        if e["relation"] in TAXONOMIC:
            parents[e["subject"]].add(e["object"])

    rng = random.Random(pool_doc["study_seed"])
    pool = pool_doc["pool"]
    used = set()

    def base(entry):
        e = edges[entry["edge"]]
        r = e["references"][entry["ref"]]
        item = {"subject": e["subject"], "relation": e["relation"],
                "object": e["object"],
                "subject_label": node_label.get(e["subject"], e["subject"]),
                "object_label": node_label.get(e["object"], e["object"]),
                "claim_type": r["claim_type"],
                "confidence": r.get("confidence"),
                "citation": f"CW{r['volume']} §{r['paragraph']}",
                "volume": str(r["volume"]), "paragraph": r["paragraph"],
                "quote": r["quote"]}
        if r.get("source"):
            item["source"] = r["source"]
        return item

    def plant(cls, entry):
        """Return (item, record) or None when this entry cannot carry cls."""
        e = edges[entry["edge"]]
        it = base(entry)
        rec = {"class": cls}

        if cls == "analogy-to-identity":
            if not is_comparison(e["relation"]):
                return None
            targets = [t for t in IDENTITY_TARGETS
                       if (e["subject"], t, e["object"]) not in triples]
            if not targets:
                return None
            new = rng.choice(targets) if len(targets) > 1 else targets[0]
            rec.update(field="relation", true_value=e["relation"], planted_value=new)
            it["relation"] = new

        elif cls == "subject-expansion":
            if e["relation"] in TAXONOMIC:
                return None
            cands = sorted(p for p in parents.get(e["subject"], ())
                           if p != e["object"]
                           and (p, e["relation"], e["object"]) not in triples)
            if not cands:
                return None
            new = rng.choice(cands)
            rec.update(field="subject", true_value=e["subject"], planted_value=new,
                       superordinate_via="is-a/belongs-to")
            it["subject"] = new
            it["subject_label"] = node_label.get(new, new)

        elif cls == "hedge-deletion":
            if not (entry["hedged_record"] and entry["hedge_markers"]):
                return None
            rec.update(field="confidence", true_value=it["confidence"],
                       planted_value="high",
                       paragraph_hedge_markers=len(entry["hedge_markers"]))
            it["confidence"] = "high"

        elif cls == "near-referent-drift":
            near = (adjacency[e["object"]] | adjacency[e["subject"]]) - {e["subject"], e["object"]}
            near = sorted(c for c in near
                          if (e["subject"], e["relation"], c) not in triples)
            if not near:
                return None
            same = [c for c in near if node_type.get(c) == node_type.get(e["object"])]
            chosen_from = same or near
            new = rng.choice(chosen_from)
            rec.update(field="object", true_value=e["object"], planted_value=new,
                       distance_basis=("neighbour-of-object" if new in adjacency[e["object"]]
                                       else "neighbour-of-subject"),
                       type_matched=bool(same))
            it["object"] = new
            it["object_label"] = node_label.get(new, new)

        else:
            raise ValueError(cls)
        return it, rec

    planted, records = [], []
    for cls in CLASS_ORDER:
        taken = 0
        for j, entry in enumerate(pool):
            if taken == N_PER_CLASS:
                break
            if j in used:
                continue
            got = plant(cls, entry)
            if got is None:
                continue
            used.add(j)
            it, rec = got
            rec.update(edge=entry["edge"], ref=entry["ref"], citation=it["citation"],
                       quote=it["quote"])
            planted.append(it)
            records.append(rec)
            taken += 1
        if taken < N_PER_CLASS:
            raise RuntimeError(f"pool exhausted for {cls}: only {taken}/{N_PER_CLASS}")

    controls = 0
    for j, entry in enumerate(pool):
        if controls == N_CLEAN:
            break
        if j in used:
            continue
        used.add(j)
        it = base(entry)
        planted.append(it)
        records.append({"class": "clean", "field": None, "edge": entry["edge"],
                        "ref": entry["ref"], "citation": it["citation"],
                        "quote": it["quote"]})
        controls += 1
    if controls < N_CLEAN:
        raise RuntimeError(f"pool exhausted for controls: only {controls}/{N_CLEAN}")

    order = list(range(len(planted)))
    rng.shuffle(order)

    planted_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = {"study": "B", "study_seed": pool_doc["study_seed"],
             "planted_at": planted_at, "commit": pool_doc["commit"]}

    items, key, manifest = [], {}, []
    for n, idx in enumerate(order, 1):
        it = dict(planted[idx])
        rec = records[idx]
        # The gate sees the claim and nothing about the plant.
        gate_item = {"n": n}
        for k in ("subject", "subject_label", "relation", "object", "object_label",
                  "claim_type", "confidence", "source", "citation", "quote"):
            if k in it:
                gate_item[k] = it[k]
        gate_item["volume"] = it["volume"]
        gate_item["paragraph"] = it["paragraph"]
        items.append(gate_item)
        key[str(n)] = {"status": "clean" if rec["class"] == "clean" else "corrupt",
                       "class": None if rec["class"] == "clean" else rec["class"],
                       "field": rec.get("field"),
                       "true_value": rec.get("true_value"),
                       "planted_value": rec.get("planted_value"),
                       "edge": rec["edge"], "ref": rec["ref"],
                       "subject": it["subject"], "relation": it["relation"],
                       "object": it["object"]}
        manifest.append({"n": n, **{k: v for k, v in rec.items() if k not in ("edge", "ref")},
                         "edge_index": rec["edge"], "ref_index": rec["ref"],
                         "presented": {"subject": it["subject"], "relation": it["relation"],
                                       "object": it["object"],
                                       "claim_type": it["claim_type"],
                                       "confidence": it["confidence"]}})

    out_items.parent.mkdir(parents=True, exist_ok=True)
    out_items.write_text(json.dumps({**stamp, "items": items}, indent=1,
                                    ensure_ascii=False), encoding="utf-8")
    out_key.write_text(json.dumps({**stamp, "key": key}, indent=1), encoding="utf-8")

    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(json.dumps({
        **stamp,
        "design": "docs/experiments/study_b/DESIGN.md (pre-registered 2026-08-28)",
        "harness": ["tools/studies/study_b_draw.py", "tools/studies/study_b_plant.py",
                    "tools/studies/study_b_gate.py", "tools/studies/study_b_score.py"],
        "graph": pool_doc["graph"],
        "pool_size": pool_doc["pool_size"],
        "class_order": CLASS_ORDER,
        "counts": {"per_class": N_PER_CLASS, "clean": N_CLEAN, "total": len(items)},
        "note": ("Corruption classes are taken scarcest-first from one shuffled pool, "
                 "so controls are drawn from what the four classes left. Corrupted "
                 "triples that already exist in seed.json are skipped, so no planted "
                 "item states something the graph holds true."),
        "items": manifest}, indent=1, ensure_ascii=False), encoding="utf-8")

    counts = {c: sum(1 for m in manifest if m["class"] == c)
              for c in CLASS_ORDER + ["clean"]}
    print(f"planted {len(items)} items {counts} (seed {stamp['study_seed']}, {planted_at})")
    print(f"  {out_items}\n  {out_key}\n  {out_manifest}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=str(WORK / "pool.json"))
    ap.add_argument("--items", default=str(WORK / "items.json"))
    ap.add_argument("--key", default=str(WORK / "key.json"))
    ap.add_argument("--manifest", default=str(DOCS / "plant_manifest.json"))
    a = ap.parse_args()
    sys.exit(main(pathlib.Path(a.pool), pathlib.Path(a.items),
                  pathlib.Path(a.key), pathlib.Path(a.manifest)))
