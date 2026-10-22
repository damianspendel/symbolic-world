#!/usr/bin/env python3
"""
kg_query — read-only queries over seed.json.

The graph is never written. Closure rows are derived at read time from the
ACTIVE declarations in pipeline/family/relation_declarations.json, labelled as
derived, and thrown away when the process exits. Nothing here asserts
transitivity, and no derived row is ever presented as an edge.

Run `python3 tools/query/kg_query.py --help` for the flags; docs/QUERY.md has
the semantics and the limits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DEFAULT_SEED = os.path.join(ROOT, "seed.json")
DEFAULT_DECLARATIONS = os.path.join(
    ROOT, "pipeline", "family", "relation_declarations.json"
)

MAX_LABEL = 34


# ---------------------------------------------------------------- loading ---

def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def file_digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class Graph:
    """seed.json, read once, never modified."""

    def __init__(self, path):
        self.path = path
        raw = load_json(path)
        self.nodes = raw["nodes"]
        self.edges = raw["edges"]
        self.digest = file_digest(path)
        self.labels = {n["id"]: n.get("label", n["id"]) for n in self.nodes}

    def label(self, node_id):
        return self.labels.get(node_id, node_id)

    # -- the two derived indexes, both built from the graph's own records --

    def family_of_string(self):
        """{family: {effective relation string: edge count}} — derived from
        seed.json's own relation_family records, never from a hardcoded map."""
        index = {}
        for edge in self.edges:
            fam = (edge.get("relation_family") or {}).get("value")
            if fam is None:
                continue
            index.setdefault(fam, {})
            rel = effective_relation(edge)
            index[fam][rel] = index[fam].get(rel, 0) + 1
        return index

    def state_tally(self):
        tally = {}
        for edge in self.edges:
            state = (edge.get("relation_family") or {}).get("state") or "unrecorded"
            tally[state] = tally.get(state, 0) + 1
        return tally


def effective_relation(edge):
    """relation_normalized.relation where that layer exists, else the verbatim
    relation (FAMILY_DEFINITIONS v0.7.1, line 112-114)."""
    norm = edge.get("relation_normalized")
    if isinstance(norm, dict) and norm.get("relation"):
        return norm["relation"]
    return edge["relation"]


# ------------------------------------------------------------------ rows ---

def graph_rows(graph):
    """One row per edge, in file order. `origin` is 'graph'."""
    rows = []
    for edge in graph.edges:
        fam = edge.get("relation_family") or {}
        rows.append({
            "subject": edge["subject"],
            "relation": effective_relation(edge),
            "object": edge["object"],
            "verbatim_relation": edge["relation"],
            "effective_relation": effective_relation(edge),
            "family": fam.get("value"),
            "state": fam.get("state"),
            "assigned_by": fam.get("by"),
            "references": edge.get("references", []),
            "origin": "graph",
            "derived_from": None,
            "_edge": edge,
        })
    return rows


def active_declarations(declarations):
    return [d for d in declarations.get("active", []) if not d.get("dormant")]


def derived_rows(graph, declarations):
    """Rows licensed by the ACTIVE declarations, applied to the whole graph.

    A derived row is a reading of a real edge in the other direction. It carries
    the source edge's references and family assignment unchanged, and its
    `origin` names the declaration and the edge relation it came from. Rows that
    would duplicate an edge the graph already asserts are dropped, so closure
    adds only what the graph does not already say.
    """
    present = {(e["subject"], effective_relation(e), e["object"]) for e in graph.edges}
    seen = set()
    out = []

    def emit(edge, new_relation, origin, carried_qualifier=None):
        triple = (edge["object"], new_relation, edge["subject"])
        if triple in present or triple in seen:
            return
        seen.add(triple)
        # the 2026-08-13 ruling: a derived row carries everything the stored row
        # asserted — a declaration's qualifier travels with the flip, visibly
        if carried_qualifier:
            origin = f"{origin} [{carried_qualifier}]"
        fam = edge.get("relation_family") or {}
        out.append({
            "subject": edge["object"],
            "relation": new_relation,
            "object": edge["subject"],
            "verbatim_relation": new_relation,
            "effective_relation": new_relation,
            "family": fam.get("value"),
            "state": fam.get("state"),
            "assigned_by": fam.get("by"),
            "references": edge.get("references", []),
            "origin": origin,
            "derived_from": {
                "subject": edge["subject"],
                "relation": effective_relation(edge),
                "object": edge["object"],
            },
            "_edge": edge,
        })

    for decl in active_declarations(declarations):
        restrict = decl.get("applies_to_family")
        for edge in graph.edges:
            if restrict is not None:
                if (edge.get("relation_family") or {}).get("value") != restrict:
                    continue
            rel = effective_relation(edge)
            cq = decl.get("carried_qualifier")
            if decl["kind"] == "inverse":
                if rel == decl["forward"]:
                    emit(edge, decl["inverse"], f"derived:inverse-of({rel})", cq)
                elif rel == decl["inverse"]:
                    emit(edge, decl["forward"], f"derived:inverse-of({rel})", cq)
            elif decl["kind"] == "symmetric":
                if rel == decl["relation"]:
                    emit(edge, rel, "derived:symmetric", cq)
    return out


# --------------------------------------------------------------- filters ---

def node_matches(graph, node_id, needle):
    """Exact id, or a case-insensitive substring of the id or the label."""
    if node_id == needle:
        return True
    low = needle.lower()
    return low in node_id.lower() or low in graph.label(node_id).lower()


# The quote search (spec-orientation-v1, item 1). It reads only the graph's
# own verbatim quotes, never the corpus: case-insensitive, accent-insensitive
# (NFD, combining marks dropped), whitespace-normalised. Every term must occur
# in the SAME quote; a double-quoted phrase is one term; a query shorter than
# two characters is no filter at all. web/query-semantics.mjs ports these
# three functions name for name.

def normalize_text(text):
    decomposed = unicodedata.normalize("NFD", str(text))
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.lower().split())


def quote_terms(query):
    """The search terms of a query: quoted phrases first, then single words."""
    text = normalize_text(query)
    if len(text) < 2:
        return []
    terms = []
    for phrase in re.findall(r'"([^"]+)"', text):
        if phrase.strip():
            terms.append(phrase.strip())
    rest = re.sub(r'"[^"]*"', " ", text)
    terms.extend(w for w in rest.split() if w)
    return terms


def quote_matches(references, terms):
    """True when some reference's quote contains every term."""
    if not terms:
        return True
    for ref in references:
        q = normalize_text(ref.get("quote") or "")
        if q and all(term in q for term in terms):
            return True
    return False


def row_matches(graph, row, args):
    if args.family is not None and row["family"] != args.family:
        return False
    if args.state is not None and row["state"] != args.state:
        return False
    if args.provenance is not None:
        by = row["assigned_by"] or ""
        if args.provenance.lower() not in by.lower():
            return False
    if args.claim_type is not None:
        if not any(r.get("claim_type") == args.claim_type for r in row["references"]):
            return False
    if args.volume is not None:
        if not any(str(r.get("volume")) == args.volume for r in row["references"]):
            return False
    if args.subject is not None and not node_matches(graph, row["subject"], args.subject):
        return False
    if args.object is not None and not node_matches(graph, row["object"], args.object):
        return False
    if args.relation is not None:
        if args.relation not in (row["verbatim_relation"], row["effective_relation"]):
            return False
    if args.string is not None and row["verbatim_relation"] != args.string:
        return False
    if args.effective is not None and row["effective_relation"] != args.effective:
        return False
    quote = getattr(args, "quote", None)
    if quote is not None:
        terms = quote_terms(quote)
        if terms and not quote_matches(row["references"], terms):
            return False
    return True


def select(graph, declarations, args):
    rows = graph_rows(graph)
    if args.closure:
        rows = rows + derived_rows(graph, declarations)
    return [r for r in rows if row_matches(graph, r, args)]


# ------------------------------------------------------------------ walk ---

IDENTITY_FAMILY = "archetypal-identity"

WALK_HEADER = (
    "Walk over {family} edges. Each hop below is ONE edge, printed with its own\n"
    "citation. No transitive identity is asserted: a term reached in two hops is\n"
    "not thereby identical to the start. FAMILY_DEFINITIONS v0.7.1 rejects\n"
    "transitivity on every family (line 131, the uroboros argument); this walk is\n"
    "exploration of what the graph connects, not inference over it."
)


def identity_edges(graph):
    return [e for e in graph.edges
            if (e.get("relation_family") or {}).get("value") == IDENTITY_FAMILY]


def walk(graph, start, depth):
    """Breadth-first over identity-family edges from `start`, both directions.

    Both directions because the family is symmetric in principle
    (FAMILY_DEFINITIONS line 415); each hop records the edge's own direction, so
    nothing is hidden by the traversal. Returns hops grouped by depth.
    """
    adjacency = {}
    for edge in identity_edges(graph):
        adjacency.setdefault(edge["subject"], []).append((edge["object"], edge, "forward"))
        adjacency.setdefault(edge["object"], []).append((edge["subject"], edge, "reverse"))

    seen = {start}
    frontier = [start]
    levels = []
    for level in range(1, depth + 1):
        hops, nxt = [], []
        for node in frontier:
            for other, edge, direction in adjacency.get(node, []):
                if other in seen:
                    continue
                seen.add(other)
                nxt.append(other)
                hops.append({
                    "depth": level,
                    "from": node,
                    "to": other,
                    "direction": direction,
                    "edge": {
                        "subject": edge["subject"],
                        "relation": effective_relation(edge),
                        "object": edge["object"],
                    },
                    "references": edge.get("references", []),
                    "_edge": edge,
                })
        levels.append(hops)
        frontier = nxt
        if not frontier:
            break
    return levels


# ---------------------------------------------------------------- output ---

def citation(ref):
    para = ref.get("paragraph")
    return f"CW{ref.get('volume')} §{para}" if para else f"CW{ref.get('volume')} §?"


def citations(references):
    return ", ".join(citation(r) for r in references) or "(no reference)"


def first_quote(references):
    for ref in references:
        if ref.get("quote"):
            return ref["quote"]
    return ""


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def clip(text, width=MAX_LABEL):
    return text if len(text) <= width else text[: width - 1] + "…"


def footer(graph, declarations):
    tally = graph.state_tally()
    order = ["assigned", "pending-adjudication", "no-family", "text-undecided"]
    parts = [f"{tally[k]} {k}" for k in order if k in tally]
    parts += [f"{v} {k}" for k, v in sorted(tally.items()) if k not in order]
    return (
        f"graph state: {len(graph.nodes)} nodes / {len(graph.edges)} edges; "
        f"families {', '.join(parts)}; "
        f"seed.json sha256:{graph.digest[:12]}; "
        f"declarations {os.path.basename(declarations['_path'])} from "
        f"FAMILY_DEFINITIONS "
        f"{declarations.get('transcribed_from', {}).get('document_version', '?')}, "
        f"{len(active_declarations(declarations))} active"
    )


def print_table(graph, rows, args, declarations):
    if not rows:
        print("(no rows)")
    else:
        widths = [
            max(len(clip(graph.label(r["subject"]))) for r in rows),
            max(len(r["relation"]) for r in rows),
            max(len(clip(graph.label(r["object"]))) for r in rows),
        ]
        for row in rows:
            line = (
                f"{clip(graph.label(row['subject'])):<{widths[0]}}  "
                f"{row['relation']:<{widths[1]}}  "
                f"{clip(graph.label(row['object'])):<{widths[2]}}  "
                f"[{citations(row['references'])}]"
            )
            fam = row["family"] or f"unclassified({row['state']})"
            line += f"  {{{fam}}}"
            if row["origin"] != "graph":
                src = row["derived_from"]
                line += (
                    f"  <{row['origin']} of "
                    f"{src['subject']} {src['relation']} {src['object']}>"
                )
            print(line)
            if args.quotes:
                quote = first_quote(row["references"])
                if quote:
                    print(f'      "{quote}"')
    print()
    if args.family is not None:
        coverage = graph.family_of_string().get(args.family, {})
        strings = sorted(coverage.items(), key=lambda kv: (-kv[1], kv[0]))
        print(
            f"family '{args.family}' covers {len(strings)} effective relation "
            f"strings over {sum(coverage.values())} assigned edges "
            f"(membership read from seed.json's relation_family records): "
            + ", ".join(f"{s} ({n})" for s, n in strings)
        )
    print(f"{plural(len(rows), 'row')}.  {footer(graph, declarations)}")


def print_walk(graph, levels, start, args, declarations):
    print(WALK_HEADER.format(family=IDENTITY_FAMILY))
    print()
    print(f"start: {graph.label(start)}  ({start})")
    total = 0
    for hops in levels:
        if not hops:
            continue
        print(f"\ndepth {hops[0]['depth']}:")
        for hop in hops:
            edge = hop["edge"]
            arrow = f"{graph.label(edge['subject'])} --{edge['relation']}--> {graph.label(edge['object'])}"
            direction = "" if hop["direction"] == "forward" else "  (traversed against the edge)"
            print(f"  {graph.label(hop['from'])} → {graph.label(hop['to'])}"
                  f"   via  {arrow}   [{citations(hop['references'])}]{direction}")
            if args.quotes:
                quote = first_quote(hop["references"])
                if quote:
                    print(f'        "{quote}"')
            total += 1
    if total == 0:
        print("\n(no identity-family edges reach out of this node)")
    print()
    print(f"{plural(total, 'hop')}.  {footer(graph, declarations)}")


def strip_private(obj):
    if isinstance(obj, dict):
        return {k: strip_private(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [strip_private(v) for v in obj]
    return obj


# ------------------------------------------------------------------ main ---

def build_parser():
    p = argparse.ArgumentParser(
        prog="kg_query",
        description="Read-only queries over seed.json. The graph is never written.",
    )
    p.add_argument("--seed", default=DEFAULT_SEED, help="path to seed.json")
    p.add_argument("--declarations", default=DEFAULT_DECLARATIONS,
                   help="path to relation_declarations.json")

    f = p.add_argument_group("filters (combined with AND)")
    f.add_argument("--family", help="relation_family.value, exact")
    f.add_argument("--state", help="relation_family.state, exact "
                                   "(assigned | pending-adjudication | no-family | text-undecided)")
    f.add_argument("--provenance", help="substring of relation_family.by, case-insensitive")
    f.add_argument("--claim-type", dest="claim_type",
                   help="a reference carries this claim_type")
    f.add_argument("--volume", help="a reference cites this CW volume, e.g. 9ii")
    f.add_argument("--subject", help="node id, or a substring of an id or label")
    f.add_argument("--object", help="node id, or a substring of an id or label")
    f.add_argument("--relation", help="matches the verbatim OR the effective relation")
    f.add_argument("--string", help="the verbatim relation only")
    f.add_argument("--quote", help="words that must all appear in one of the row's own "
                   "verbatim quotes (case- and accent-insensitive; \"a phrase\" matches "
                   "as a phrase; never reads the corpus)")
    f.add_argument("--effective", help="the effective relation only "
                                       "(normalized where that layer exists, else verbatim)")

    m = p.add_argument_group("modes")
    m.add_argument("--closure", action="store_true",
                   help="also read rows licensed by the ACTIVE declarations; every such "
                        "row is labelled derived and names the edge it came from")
    m.add_argument("--walk", choices=["identity"],
                   help="depth-bounded traversal over archetypal-identity edges; "
                        "needs --subject as the start node")
    m.add_argument("--depth", type=int, default=2, help="walk depth (default 2)")
    m.add_argument("--list-families", action="store_true",
                   help="list the families and their string coverage, then exit")
    m.add_argument("--list-declarations", action="store_true",
                   help="list the ACTIVE declarations with their sources, then exit")

    o = p.add_argument_group("output")
    o.add_argument("--json", action="store_true", help="JSON instead of a table")
    o.add_argument("--count", action="store_true", help="counts only")
    o.add_argument("--quotes", action="store_true",
                   help="print each row's first quote (the graph's own ≤25-word quotes)")
    o.add_argument("--limit", type=int, help="print at most this many rows")
    return p


def resolve_start(graph, needle):
    if needle in graph.labels:
        return needle
    hits = [n for n in graph.labels if node_matches(graph, n, needle)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        return None
    exact = [n for n in hits if graph.label(n).lower() == needle.lower()]
    return exact[0] if len(exact) == 1 else sorted(hits)[0]


def main(argv=None):
    args = build_parser().parse_args(argv)
    graph = Graph(args.seed)
    declarations = load_json(args.declarations)
    declarations["_path"] = args.declarations

    if args.list_declarations:
        payload = []
        for decl in declarations.get("active", []):
            payload.append({
                "id": decl["id"],
                "kind": decl["kind"],
                "dormant": bool(decl.get("dormant")),
                "applies_to_family": decl.get("applies_to_family"),
                "sources": [f"{s['section']} (line {s['line']})" for s in decl["source"]],
            })
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            for entry in payload:
                mark = " [dormant]" if entry["dormant"] else ""
                scope = (f" restricted to family {entry['applies_to_family']}"
                         if entry["applies_to_family"] else "")
                print(f"{entry['id']}{mark}{scope}")
                for src in entry["sources"]:
                    print(f"    source: {src}")
            print()
            print(f"{len(declarations.get('candidates_awaiting_ruling', []))} candidate pairs "
                  f"await a ruling and are inert.  {footer(graph, declarations)}")
        return 0

    if args.list_families:
        index = graph.family_of_string()
        payload = {fam: dict(sorted(strings.items(), key=lambda kv: (-kv[1], kv[0])))
                   for fam, strings in sorted(index.items())}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            for fam, strings in payload.items():
                print(f"{fam:24s} {sum(strings.values()):5d} edges over "
                      f"{len(strings):3d} effective strings")
            print()
            print(footer(graph, declarations))
        return 0

    if args.walk:
        if not args.subject:
            print("--walk needs --subject to name the start node", file=sys.stderr)
            return 2
        start = resolve_start(graph, args.subject)
        if start is None:
            print(f"no node matches --subject {args.subject!r}", file=sys.stderr)
            return 2
        levels = walk(graph, start, max(0, args.depth))
        if args.json:
            print(json.dumps({
                "walk": IDENTITY_FAMILY,
                "start": start,
                "depth": args.depth,
                "asserts_transitivity": False,
                "hops": strip_private([h for lv in levels for h in lv]),
                "graph_state": footer(graph, declarations),
            }, indent=2, ensure_ascii=False))
        elif args.count:
            print(f"{plural(sum(len(lv) for lv in levels), 'hop')}.  "
                  f"{footer(graph, declarations)}")
        else:
            print_walk(graph, levels, start, args, declarations)
        return 0

    rows = select(graph, declarations, args)
    if args.limit is not None:
        rows = rows[: args.limit]

    if args.json:
        print(json.dumps({
            "rows": strip_private(rows),
            "row_count": len(rows),
            "closure": bool(args.closure),
            "graph_state": footer(graph, declarations),
        }, indent=2, ensure_ascii=False))
    elif args.count:
        derived = sum(1 for r in rows if r["origin"] != "graph")
        print(f"{plural(len(rows), 'row')} ({len(rows) - derived} from the graph, "
              f"{derived} derived).  {footer(graph, declarations)}")
    else:
        print_table(graph, rows, args, declarations)
    return 0


if __name__ == "__main__":
    sys.exit(main())
