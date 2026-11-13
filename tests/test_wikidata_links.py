#!/usr/bin/env python3
"""
Invariant tests for the Wikidata links in the RDF export
(tools/linking/wikidata_links.json, written by tools/query/export_rdf.py).

No pinned counts: the assertions hold whatever the links file says.

  * every skos:closeMatch in the export comes from a figure link whose check
    is "accept", and every accepted figure link is exported;
  * every subject is a real node of seed.json;
  * the VoID linkset's void:triples equals the number of closeMatch triples;
  * no author or text link is exported;
  * the export is the same on a second run.

Run: python3 -m pytest tests/test_wikidata_links.py
"""
import json
import os
import sys

import pytest
import rdflib
from rdflib.namespace import RDF, SKOS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "query"))

import kg_query  # noqa: E402
import export_rdf  # noqa: E402

SEED = os.path.join(ROOT, "seed.json")
DECLARATIONS = os.path.join(ROOT, "pipeline", "family", "relation_declarations.json")
VOID = rdflib.Namespace("http://rdfs.org/ns/void#")
WD = rdflib.Namespace(export_rdf.WIKIDATA_ENTITY)
SWN = rdflib.Namespace(export_rdf.NS["swn"])


def export_rdf_term(prefix, local):
    return rdflib.URIRef(export_rdf.NS[prefix] + local)


@pytest.fixture(scope="module")
def graph():
    return kg_query.Graph(SEED)


@pytest.fixture(scope="module")
def links():
    with open(export_rdf.LINKS_FILE, encoding="utf-8") as fh:
        return json.load(fh)["links"]


@pytest.fixture(scope="module")
def export(graph):
    declarations = kg_query.load_json(DECLARATIONS)
    declarations["_path"] = DECLARATIONS
    return export_rdf.build_all(graph, declarations)


@pytest.fixture(scope="module")
def parsed(export):
    return {name: rdflib.Graph().parse(data=text, format="turtle")
            for name, text in export.items()}


@pytest.fixture(scope="module")
def close_matches(parsed):
    return set(parsed[export_rdf.GRAPH_FILE].subject_objects(SKOS.closeMatch))


def test_every_close_match_comes_from_an_accepted_figure_link(links, close_matches):
    accepted = {(SWN[l["key"]], WD[l["qid"]]) for l in links
                if l["kind"] == "figure" and l["check"] == "accept"}
    assert close_matches, "the export carries no closeMatch"
    assert close_matches == accepted


def test_every_subject_is_a_real_node(graph, close_matches):
    nodes = {SWN[n["id"]] for n in graph.nodes}
    assert {s for s, _ in close_matches} <= nodes


def test_one_link_per_node(close_matches):
    subjects = [s for s, _ in close_matches]
    assert len(subjects) == len(set(subjects))


def test_void_linkset_counts_the_close_matches(parsed, close_matches):
    v = parsed[export_rdf.VOID_FILE]
    linksets = list(v.subjects(RDF.type, VOID.Linkset))
    assert len(linksets) == 1
    linkset = linksets[0]
    dataset = rdflib.URIRef(export_rdf.BASE + "data/graph")
    assert int(v.value(linkset, VOID.triples)) == len(close_matches)
    assert v.value(linkset, VOID.linkPredicate) == SKOS.closeMatch
    assert v.value(linkset, VOID.subjectsTarget) == dataset
    target = v.value(linkset, VOID.objectsTarget)
    assert (target, RDF.type, VOID.Dataset) in v
    assert str(v.value(target, export_rdf_term("dcterms", "title"))) == "Wikidata"
    assert (dataset, VOID.subset, linkset) in v
    description = str(v.value(linkset, export_rdf_term("dcterms", "description")))
    assert "public Wikidata search" in description
    # The spot check is stated only as the links file records it (spot_check).
    done, date = export_rdf.spot_check_state()
    if done:
        assert f"spot-checked a seeded sample on {date}" in description
    else:
        assert "awaits the maintainer's spot check" in description and "spot-checked" not in description


def test_no_author_or_text_link_is_exported(links, parsed, close_matches):
    figure_qids = {l["qid"] for l in links if l["kind"] == "figure"}
    others = [l for l in links if l["kind"] != "figure"]
    assert others, "the file holds no author or text link to test against"
    subjects = {str(s) for s, _ in close_matches}
    iris = {t for g in parsed.values() for triple in g for t in triple
            if isinstance(t, rdflib.URIRef)}
    for link in others:
        assert export_rdf.NS["swn"] + link["key"] not in subjects, link["key"]
        if link["qid"] not in figure_qids:
            assert WD[link["qid"]] not in iris, link


def test_export_is_deterministic(graph, export):
    declarations = kg_query.load_json(DECLARATIONS)
    declarations["_path"] = DECLARATIONS
    again = export_rdf.build_all(graph, declarations)
    assert again == export


def test_each_file_header_mentions_the_links(export):
    for name, text in export.items():
        head = "\n".join(line for line in text.split("\n") if line.startswith("#"))
        assert "Wikidata" in head, name
