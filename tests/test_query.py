#!/usr/bin/env python3
"""
Invariant tests for the query layer (tools/query/kg_query.py).

Deliberately no pinned counts. seed.json changes as mining windows merge, so a
test that asserts "22 synonym-of edges" is a test that rots. Every assertion
here is a relationship that must hold whatever the graph currently says:

  * a family query returns exactly the edges independently found to carry that
    family, and nothing else;
  * closure only ever adds, every added row maps back to a real edge, and the
    row is labelled as derived;
  * every walk hop is a real edge, and the walk never claims transitivity;
  * the declarations file is internally consistent and grounded in the graph;
  * the CLI exits 0 and prints its graph state.

Run: python3 -m pytest tests/test_query.py
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "query"))

import kg_query  # noqa: E402

SEED = os.path.join(ROOT, "seed.json")
DECLARATIONS = os.path.join(ROOT, "pipeline", "family", "relation_declarations.json")
CLI = os.path.join(ROOT, "tools", "query", "kg_query.py")
FAMILY_DOC = os.path.join(ROOT, "docs", "FAMILY_DEFINITIONS.md")


# ------------------------------------------------------------- fixtures ---

@pytest.fixture(scope="module")
def graph():
    return kg_query.Graph(SEED)


@pytest.fixture(scope="module")
def declarations():
    decls = kg_query.load_json(DECLARATIONS)
    decls["_path"] = DECLARATIONS
    return decls


class Args:
    """A filled-out argparse namespace, so tests can call select() directly."""

    def __init__(self, **kwargs):
        for name in ("family", "state", "provenance", "claim_type", "volume",
                     "subject", "object", "relation", "string", "effective"):
            setattr(self, name, None)
        self.closure = False
        for key, value in kwargs.items():
            setattr(self, key, value)


def triple(row):
    return (row["subject"], row["relation"], row["object"])


def edge_triples(graph):
    return {(e["subject"], kg_query.effective_relation(e), e["object"])
            for e in graph.edges}


# -------------------------------------------------- family query is exact ---

def test_family_query_equals_independently_found_member_edges(graph, declarations):
    """For every family present, the query result is the union of the edges
    carrying that family — found here by a separate walk over seed.json."""
    families = {(e.get("relation_family") or {}).get("value") for e in graph.edges}
    families.discard(None)
    assert families, "no family assignments in the graph at all"

    for family in sorted(families):
        expected = [e for e in graph.edges
                    if (e.get("relation_family") or {}).get("value") == family]
        rows = kg_query.select(graph, declarations, Args(family=family))
        assert len(rows) == len(expected), family
        assert [r["_edge"] for r in rows] == expected, family
        assert all(r["family"] == family for r in rows), family


def test_family_membership_is_read_from_the_graph_not_hardcoded(graph):
    """The string-to-family index is derived from relation_family records, so
    every string it lists is a string some edge in this graph actually uses."""
    index = graph.family_of_string()
    live = {kg_query.effective_relation(e) for e in graph.edges}
    for family, strings in index.items():
        for string, count in strings.items():
            assert string in live, f"{family}/{string} not in the graph"
            assert count >= 1
    source = open(os.path.join(ROOT, "tools", "query", "kg_query.py"),
                  encoding="utf-8").read()
    baked_strings = sorted(s for s in live if f'"{s}"' in source)
    assert not baked_strings, f"relation strings written into the CLI: {baked_strings}"
    named_families = sorted(f for f in index if f'"{f}"' in source)
    assert named_families == [kg_query.IDENTITY_FAMILY], (
        "the only family the CLI may name is the walk's declared target; "
        f"found {named_families}")


def test_families_partition_the_assigned_edges(graph):
    index = graph.family_of_string()
    counted = sum(sum(strings.values()) for strings in index.values())
    assigned = sum(1 for e in graph.edges
                   if (e.get("relation_family") or {}).get("value") is not None)
    assert counted == assigned


# ------------------------------------------------------- closure is honest ---

def test_closure_output_is_a_superset_of_raw_output(graph, declarations):
    for filters in ({}, {"family": "symbolization"}, {"relation": "symbolized-by"},
                    {"subject": "the-self"}, {"state": "assigned"}):
        raw = kg_query.select(graph, declarations, Args(**filters))
        closed = kg_query.select(graph, declarations, Args(closure=True, **filters))
        assert len(closed) >= len(raw), filters
        raw_ids = [id(r["_edge"]) for r in raw]
        closed_graph_rows = [id(r["_edge"]) for r in closed if r["origin"] == "graph"]
        assert raw_ids == closed_graph_rows, filters


def test_every_derived_row_maps_back_to_a_real_edge(graph, declarations):
    rows = kg_query.select(graph, declarations, Args(closure=True))
    derived = [r for r in rows if r["origin"] != "graph"]
    assert derived, "closure derived nothing at all — the declarations are inert"
    present = edge_triples(graph)
    for row in derived:
        source = row["derived_from"]
        assert source is not None
        assert (source["subject"], source["relation"], source["object"]) in present
        assert row["subject"] == source["object"]
        assert row["object"] == source["subject"]
        assert row["references"] is row["_edge"]["references"]


def test_every_derived_row_is_labelled_as_derived(graph, declarations):
    rows = kg_query.select(graph, declarations, Args(closure=True))
    for row in rows:
        if row["derived_from"] is None:
            assert row["origin"] == "graph"
        else:
            assert row["origin"].startswith("derived:")
            assert (row["origin"] == "derived:symmetric"
                    or row["origin"].startswith("derived:inverse-of("))


def test_derived_rows_never_duplicate_an_asserted_edge(graph, declarations):
    rows = kg_query.select(graph, declarations, Args(closure=True))
    present = edge_triples(graph)
    derived = [triple(r) for r in rows if r["origin"] != "graph"]
    assert not [t for t in derived if t in present]
    assert len(set(derived)) == len(derived)


def test_closure_does_not_touch_the_graph(graph, declarations):
    before = kg_query.file_digest(SEED)
    edge_count = len(graph.edges)
    kg_query.select(graph, declarations, Args(closure=True))
    assert kg_query.file_digest(SEED) == before
    assert len(graph.edges) == edge_count


def test_derived_relations_come_only_from_active_declarations(graph, declarations):
    licensed = set()
    for decl in kg_query.active_declarations(declarations):
        if decl["kind"] == "inverse":
            licensed.update({decl["forward"], decl["inverse"]})
        else:
            licensed.add(decl["relation"])
    rows = kg_query.select(graph, declarations, Args(closure=True))
    for row in rows:
        if row["origin"] != "graph":
            assert row["relation"] in licensed


def test_family_restricted_declaration_is_enforced(graph, declarations):
    restricted = [d for d in kg_query.active_declarations(declarations)
                  if d.get("applies_to_family")]
    if not restricted:
        pytest.skip("no family-restricted declaration in force")
    rows = kg_query.select(graph, declarations, Args(closure=True))
    for decl in restricted:
        strings = {decl["forward"], decl["inverse"]}
        for row in rows:
            if row["origin"] == "graph" or row["relation"] not in strings:
                continue
            source_family = (row["_edge"].get("relation_family") or {}).get("value")
            other = [d for d in kg_query.active_declarations(declarations)
                     if d is not decl and d["kind"] == "inverse"
                     and row["relation"] in {d.get("forward"), d.get("inverse")}
                     and not d.get("applies_to_family")]
            if not other:
                assert source_family == decl["applies_to_family"]


# ------------------------------------------------------------ walk is real ---

def test_every_walk_hop_is_a_real_edge(graph):
    present = edge_triples(graph)
    starts = [e["subject"] for e in kg_query.identity_edges(graph)][:25]
    assert starts, "no archetypal-identity edges to walk"
    hops_seen = 0
    for start in starts:
        for level in kg_query.walk(graph, start, 3):
            for hop in level:
                edge = hop["edge"]
                assert (edge["subject"], edge["relation"], edge["object"]) in present
                assert {hop["from"], hop["to"]} == {edge["subject"], edge["object"]}
                hops_seen += 1
    assert hops_seen > 0


def test_walk_only_traverses_identity_family_edges(graph):
    identity = {id(e) for e in kg_query.identity_edges(graph)}
    start = kg_query.identity_edges(graph)[0]["subject"]
    for level in kg_query.walk(graph, start, 3):
        for hop in level:
            assert id(hop["_edge"]) in identity


def test_walk_visits_each_node_once_and_respects_depth(graph):
    start = kg_query.identity_edges(graph)[0]["subject"]
    for depth in (1, 2, 3):
        levels = kg_query.walk(graph, start, depth)
        assert len(levels) <= depth
        reached = [hop["to"] for level in levels for hop in level]
        assert len(reached) == len(set(reached))
        assert start not in reached
        for index, level in enumerate(levels, start=1):
            assert all(hop["depth"] == index for hop in level)


def test_walk_header_denies_transitivity():
    header = kg_query.WALK_HEADER.lower()
    assert "no transitive identity is asserted" in header
    assert "transitivity" in header


# ---------------------------------------------------- declarations validate ---

def test_declarations_strings_are_live_or_dormant(graph, declarations):
    live = {kg_query.effective_relation(e) for e in graph.edges}
    for decl in declarations["active"]:
        strings = ({decl["forward"], decl["inverse"]} if decl["kind"] == "inverse"
                   else {decl["relation"]})
        missing = sorted(s for s in strings if s not in live)
        if missing:
            assert decl.get("dormant") is True, f"{decl['id']} missing {missing}"
            assert set(decl.get("dormant_strings", [])) == set(missing), decl["id"]
            assert decl.get("dormant_reason")
        else:
            assert decl.get("dormant") is not True, decl["id"]


def test_no_pair_is_both_inverse_and_symmetric(declarations):
    symmetric = {d["relation"] for d in declarations["active"]
                 if d["kind"] == "symmetric"}
    for decl in declarations["active"]:
        if decl["kind"] != "inverse":
            continue
        assert decl["forward"] != decl["inverse"], decl["id"]
        assert decl["forward"] not in symmetric, decl["id"]
        assert decl["inverse"] not in symmetric, decl["id"]


def test_no_duplicate_declarations(declarations):
    ids = [d["id"] for d in declarations["active"]]
    assert len(ids) == len(set(ids))
    pairs = []
    for decl in declarations["active"]:
        key = (frozenset({decl["forward"], decl["inverse"]})
               if decl["kind"] == "inverse" else frozenset({decl["relation"]}),
               decl.get("applies_to_family"))
        pairs.append(key)
    assert len(pairs) == len(set(pairs))


def test_candidates_are_inert_and_disjoint_from_active(declarations):
    candidates = declarations["candidates_awaiting_ruling"]
    assert candidates, "the candidate list should record what the doc has not ruled on"
    active_pairs = {frozenset({d["forward"], d["inverse"]})
                    for d in declarations["active"] if d["kind"] == "inverse"}
    for candidate in candidates:
        assert frozenset({candidate["forward"], candidate["inverse"]}) not in active_pairs
        assert candidate.get("why_inert")
        assert "dormant" not in candidate
    assert kg_query.active_declarations(declarations) == [
        d for d in declarations["active"] if not d.get("dormant")]


def test_every_active_declaration_cites_its_document_line(declarations):
    if not os.path.exists(FAMILY_DOC):
        pytest.skip("FAMILY_DEFINITIONS.md not present")
    lines = open(FAMILY_DOC, encoding="utf-8").read().split("\n")
    for decl in declarations["active"]:
        assert decl["source"], decl["id"]
        for source in decl["source"]:
            window = " ".join(" ".join(lines[source["line"] - 1:source["line"] + 8]).split())
            quoted = " ".join(source["quote"].split())
            assert quoted in window, f"{decl['id']} line {source['line']}"


def test_no_transitivity_is_declared_anywhere(declarations):
    for decl in declarations["active"]:
        assert decl["kind"] in ("inverse", "symmetric")
        assert "transitive" not in json.dumps(decl).lower().replace("transitivity", "")


# -------------------------------------------------------------- the CLI runs ---

def run(*argv):
    result = subprocess.run([sys.executable, CLI, *argv],
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_cli_exits_zero_with_sane_output(graph):
    edges = f"{len(graph.edges)} edges"
    for argv in (["--count"],
                 ["--family", "symbolization", "--count"],
                 ["--state", "pending-adjudication", "--count"],
                 ["--closure", "--count"],
                 ["--list-families"],
                 ["--list-declarations"],
                 ["--limit", "5"],
                 ["--limit", "5", "--quotes"]):
        out = run(*argv)
        assert out.strip()
        assert edges in out, argv


def test_cli_json_is_valid_and_carries_its_graph_state(graph):
    payload = json.loads(run("--family", "union", "--json"))
    assert payload["row_count"] == len(payload["rows"])
    assert f"{len(graph.edges)} edges" in payload["graph_state"]
    assert all(row["family"] == "union" for row in payload["rows"])
    assert all("_edge" not in row for row in payload["rows"])


def test_cli_walk_runs_and_states_its_limits(graph):
    start = kg_query.identity_edges(graph)[0]["subject"]
    out = run("--walk", "identity", "--subject", start, "--depth", "2")
    assert "No transitive identity is asserted" in out
    assert f"{len(graph.edges)} edges" in out
    payload = json.loads(run("--walk", "identity", "--subject", start,
                             "--depth", "2", "--json"))
    assert payload["asserts_transitivity"] is False
    assert payload["start"] == start


def test_cli_closure_reports_more_rows_than_raw():
    raw = json.loads(run("--relation", "symbolized-by", "--json"))
    closed = json.loads(run("--relation", "symbolized-by", "--closure", "--json"))
    assert closed["row_count"] >= raw["row_count"]
    assert closed["closure"] is True
    assert any(row["origin"].startswith("derived:") for row in closed["rows"])


def test_cli_leaves_the_seed_file_untouched():
    before = kg_query.file_digest(SEED)
    run("--closure", "--count")
    run("--walk", "identity", "--subject", "mercurius", "--depth", "3")
    assert kg_query.file_digest(SEED) == before
