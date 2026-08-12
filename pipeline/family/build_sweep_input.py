#!/usr/bin/env python3
"""Build the per-window family-sweep input: every edge that carries no family yet.

RULES #23 — this ran inline for windows 8, 9 and 10 and produced merged
artifacts; it belongs in the repository. Reconstructed 2026-08-12 from the shape
of pipeline/work/family_sweep_input.json and verified field-for-field against
window 10's surviving input (34 edges, exact match on every field).

`n` is the edge's INDEX in seed.json's edges array, zero-based. Every downstream
stage — both arms, the queue, the assembler — joins on that index, so the input
must be built from the same seed.json the assembler will write back to. A merge
between the two renumbers everything.

The two arms are blind to each other and receive exactly this file plus
docs/FAMILY_DEFINITIONS.md. Nothing here names a family, a count, or a target.

Usage:  python3 pipeline/family/build_sweep_input.py [--out PATH] [--limit N]
"""
import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "pipeline" / "work" / "family_sweep_input.json"


def sweep_item(n, edge, types):
    """One edge as the arms see it: the frozen relation, the effective relation,
    the qualifiers that can decide a boundary, node types, layer, and the refs."""
    rn = edge.get("relation_normalized") or {}
    quals = {k: v for k, v in (rn.get("qualifiers") or {}).items() if v}
    return {
        "n": n,
        "subject": edge["subject"],
        "subject_type": types.get(edge["subject"]),
        "relation": edge["relation"],
        "relation_effective": rn.get("relation") or edge["relation"],
        "qualifiers": quals or None,
        "object": edge["object"],
        "object_type": types.get(edge["object"]),
        "layer": edge.get("layer"),
        "refs": [{"volume": r["volume"], "paragraph": r["paragraph"],
                  "claim_type": r.get("claim_type"), "quote": r["quote"]}
                 for r in edge.get("references", [])],
    }


def unassigned(graph):
    """An edge is in the sweep when it carries no relation_family record at all.
    An edge already assigned, queued, or refused is NOT re-swept: one family pass
    per edge, the same discipline as one mining pass per window."""
    for n, e in enumerate(graph["edges"]):
        if not e.get("relation_family"):
            yield n, e


def main(out_path, limit):
    graph = json.loads((ROOT / "seed.json").read_text())
    types = {node["id"]: node["type"] for node in graph["nodes"]}
    defs_version = _defs_version()

    items = [sweep_item(n, e, types) for n, e in unassigned(graph)]
    if limit:
        items = items[:limit]
    if not items:
        raise SystemExit("nothing to sweep: every edge already carries a "
                         "relation_family record")

    out_path.write_text(json.dumps({
        "definitions": "docs/FAMILY_DEFINITIONS.md",
        "version": defs_version,
        "n_edges": len(items),
        "edges": items,
    }, indent=1, ensure_ascii=False))
    print(f"{len(items)} unassigned edges (n {items[0]['n']}..{items[-1]['n']}) "
          f"written to {out_path.relative_to(ROOT)} against {defs_version}")


def _defs_version():
    head = (ROOT / "docs" / "FAMILY_DEFINITIONS.md").read_text(
        encoding="utf-8").splitlines()[0]
    for tok in head.replace(",", " ").split():
        if tok.startswith("v") and tok[1:2].isdigit():
            return tok
    raise SystemExit("REFUSED: no version in the FAMILY_DEFINITIONS.md header")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--limit", type=int, default=0,
                    help="cap the window (0 = every unassigned edge)")
    a = ap.parse_args()
    main(pathlib.Path(a.out), a.limit)
