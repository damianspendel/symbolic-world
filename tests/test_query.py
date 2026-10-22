#!/usr/bin/env python3
"""
Invariant tests for the query layer (tools/query/kg_query.py, and the Turtle
export in tools/query/export_rdf.py).

Deliberately no pinned counts. seed.json changes as mining windows merge, so a
test that asserts "22 synonym-of edges" is a test that rots. Every assertion
here is a relationship that must hold whatever the graph currently says:

  * a family query returns exactly the edges independently found to carry that
    family, and nothing else;
  * closure only ever adds, every added row maps back to a real edge, and the
    row is labelled as derived;
  * every walk hop is a real edge, and the walk never claims transitivity;
  * the declarations file is internally consistent and grounded in the graph;
  * the CLI exits 0 and prints its graph state;
  * the Turtle export declares no transitivity, asserts a super-property only
    where a string sits in one family, and withholds the family-restricted
    declaration.

Run: python3 -m pytest tests/test_query.py
"""
import json
import os
import re
import shutil
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
    # line numbers bind to the TRANSCRIPTION commit the file records, not the
    # working tree: the document moves (v0.7.2 landed within hours of v0.7.1)
    # and a citation is to the version it transcribed
    base = declarations["transcribed_from"]["base_commit"]
    try:
        doc = subprocess.run(
            ["git", "show", f"{base}:docs/FAMILY_DEFINITIONS.md"],
            capture_output=True, text=True, check=True, cwd=ROOT).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("transcription commit not reachable")
    lines = doc.split("\n")
    for decl in declarations["active"]:
        assert decl["source"], decl["id"]
        for source in decl["source"]:
            window = " ".join(" ".join(lines[source["line"] - 1:source["line"] + 8]).split())
            quoted = " ".join(source["quote"].split())
            assert quoted in window, f"{decl['id']} line {source['line']}"


def test_active_quotes_survive_in_current_document(declarations):
    # the drift alarm: if the CURRENT document no longer contains a declared
    # pair's wording anywhere, the declaration may be transcribing a retired
    # rule and needs re-transcription against the new version
    if not os.path.exists(FAMILY_DOC):
        pytest.skip("FAMILY_DEFINITIONS.md not present")
    doc = " ".join(open(FAMILY_DOC, encoding="utf-8").read().split())
    for decl in declarations["active"]:
        for source in decl["source"]:
            quoted = " ".join(source["quote"].split())
            assert quoted in doc, (
                f"{decl['id']}: its doc wording is gone from the current "
                f"FAMILY_DEFINITIONS — re-transcribe or retire the declaration")


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


# ----------------------------------------- the quote search (orientation v1) ---

NODE = shutil.which("node")
JS_PORT = os.path.join(ROOT, "web", "query-semantics.mjs")


def js_select(tmp_path, filters):
    harness = tmp_path / "harness.mjs"
    harness.write_text(
        "import { readFileSync } from 'fs'\n"
        f"import {{ select }} from '{JS_PORT}'\n"
        f"const graph = JSON.parse(readFileSync({json.dumps(SEED)}))\n"
        f"const decls = JSON.parse(readFileSync({json.dumps(DECLARATIONS)}))\n"
        f"const rows = select(graph, decls, {json.dumps(filters)})\n"
        "console.log(JSON.stringify(rows.map(r => [r.subject, r.relation, r.object, r.origin])))\n")
    out = subprocess.run([NODE, str(harness)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return [tuple(r) for r in json.loads(out.stdout)]


@pytest.mark.skipif(NODE is None, reason="node is not on PATH")
@pytest.mark.parametrize("query,expect_rows", [
    ("projection", True),                       # one word
    ("stone projection", True),                 # two words, same quote
    ('"projection of the unified self"', True), # a quoted phrase
    ("PROJECTION", True),                       # mixed case
    ("bohme", True),                            # accent-insensitive: matches Böhme
    ("zzzzqq", False),                          # matches nothing
])
def test_quote_search_cli_and_port_agree(tmp_path, query, expect_rows):
    """--quote reads the graph's own verbatim quotes and nothing else; the CLI
    and the JS port must return the same rows for the same query."""
    payload = json.loads(run("--quote", query, "--json"))
    reference = [(r["subject"], r["relation"], r["object"], r["origin"]) for r in payload["rows"]]
    ported = js_select(tmp_path, {"quote": query})
    assert ported == reference
    assert bool(reference) is expect_rows, (query, len(reference))


def test_quote_search_matches_within_one_quote_only():
    """Two words must appear in the SAME quote: the conjunction is per quote,
    not per row."""
    terms = kg_query.quote_terms("stone projection")
    assert terms == ["stone", "projection"]
    refs = [{"quote": "the stone of the wise"}, {"quote": "a projection of the self"}]
    assert kg_query.quote_matches(refs, terms) is False
    assert kg_query.quote_matches([{"quote": "the stone is a projection"}], terms) is True
    assert kg_query.quote_terms("x") == []          # under two characters: no filter
    assert kg_query.quote_terms('"a b" c') == ["a b", "c"]
    assert kg_query.normalize_text("  Böhme\tSAYS ") == "bohme says"


# ------------------------------------------------------- the RDF export (D7) ---

import export_rdf  # noqa: E402


@pytest.fixture(scope="module")
def turtle(graph, declarations):
    return export_rdf.build(graph, declarations)


def test_turtle_declares_no_transitivity(turtle):
    assert "TransitiveProperty" not in turtle
    assert "owl:TransitiveProperty" not in turtle
    assert "NO TRANSITIVITY AXIOM APPEARS IN THIS FILE" in turtle
    assert "uroboros" in turtle


def test_turtle_emits_one_triple_per_edge(graph, turtle):
    triples = [line for line in turtle.split("\n")
               if line.startswith("jkgn:") and line.endswith(" .")
               and " a jkg:Node" not in line]
    assert len(triples) == len(graph.edges)


def test_turtle_subproperty_only_for_unambiguous_strings(graph, turtle):
    families = graph.family_of_string()
    spread = {}
    for family, strings in families.items():
        for string in strings:
            spread.setdefault(string, set()).add(family)
    for string, fams in spread.items():
        if len(fams) > 1:
            block = f'rdfs:label "{string}" ;\n    rdfs:subPropertyOf'
            assert block not in turtle, string
    unambiguous = [s for s, f in spread.items() if len(f) == 1]
    assert unambiguous, "no unambiguous string to assert a super-property for"
    assert "rdfs:subPropertyOf" in turtle


def test_turtle_withholds_family_restricted_declarations(declarations, turtle):
    for decl in kg_query.active_declarations(declarations):
        if not decl.get("applies_to_family"):
            continue
        pair = f"jkgp:{decl['forward']} owl:inverseOf jkgp:{decl['inverse']} ."
        assert pair not in turtle
        assert f"withheld: {decl['id']}" in turtle


def test_turtle_emits_the_unrestricted_declarations(declarations, turtle):
    for decl in kg_query.active_declarations(declarations):
        if decl.get("applies_to_family"):
            continue
        if decl["kind"] == "inverse":
            assert f"jkgp:{decl['forward']} owl:inverseOf jkgp:{decl['inverse']} ." in turtle
        else:
            assert f"jkgp:{decl['relation']} a owl:SymmetricProperty ." in turtle


def test_turtle_statements_are_terminated_and_prefixes_declared(turtle):
    statements, buffer = [], []
    for line in turtle.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        buffer.append(stripped)
        if stripped.endswith("."):
            statements.append(" ".join(buffer))
            buffer = []
    assert not buffer, "a statement was left open at the end of the file"
    assert all(s.endswith(" .") for s in statements)
    assert all(s.count('"') % 2 == 0 for s in statements)
    # angle brackets must balance in IRIs; a literal may legitimately contain one ("names -> conceives")
    assert all(re.sub(r'"(?:[^"\\]|\\.)*"', "", s).count("<") == re.sub(r'"(?:[^"\\]|\\.)*"', "", s).count(">")
               for s in statements)
    declared = {name for name, _ in export_rdf.PREFIXES}
    for statement in statements:
        if statement.startswith("@prefix"):
            continue
        for match in re.finditer(r"(?<![<\w])([A-Za-z][A-Za-z0-9]*):(?![/\s])", statement):
            assert match.group(1) in declared, match.group(1)


def test_turtle_export_leaves_the_seed_file_untouched(graph, declarations):
    before = kg_query.file_digest(SEED)
    export_rdf.build(graph, declarations)
    assert kg_query.file_digest(SEED) == before


# ---- the 2026-08-13 middle ruling: aspect flips, qualifier carried ----------

def test_aspect_of_flip_derives_manifests_as(graph, declarations):
    derived = kg_query.derived_rows(graph, declarations)
    flips = {(r["subject"], r["relation"], r["object"]) for r in derived}
    assert ("individuation", "manifests-as", "transference") in flips
    assert ("adam", "manifests-as", "lilith") in flips

def test_dark_aspect_flip_carries_qualifier(graph, declarations):
    derived = kg_query.derived_rows(graph, declarations)
    rows = [r for r in derived
            if r["derived_from"]["relation"] == "is-dark-aspect-of"]
    assert rows, "the is-dark-aspect-of edge must derive a row"
    for r in rows:
        assert "[dark aspect]" in r["origin"], (
            "the ruling: the qualifier travels with the flip, visibly")

def test_carried_qualifiers_are_nonempty_strings(declarations):
    for decl in declarations["active"]:
        if "carried_qualifier" in decl:
            assert isinstance(decl["carried_qualifier"], str)
            assert decl["carried_qualifier"].strip()

def test_rulings_log_present_and_dated(declarations):
    assert declarations.get("rulings"), "an adopted declaration requires a logged ruling"
    for r in declarations["rulings"]:
        assert r.get("date") and r.get("ruled_by") and r.get("ruling")
