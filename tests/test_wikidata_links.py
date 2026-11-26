#!/usr/bin/env python3
"""
Invariant tests for the Wikidata links in the RDF export
(tools/linking/wikidata_links.json, written by tools/query/export_rdf.py).

No pinned counts: the assertions hold whatever the links file says.

  * every skos:closeMatch on a node comes from an accepted figure link, and
    every accepted figure link is exported;
  * every subject is a real node of seed.json;
  * the VoID linksets' void:triples equal the closeMatch triples they describe;
  * author and text links (2026-11-26) are exported only
    on source IRIs, only with their check records, and appear on no page of the
    site; their counts agree with the links file;
  * the export is the same on a second run.

Run: python3 -m pytest tests/test_wikidata_links.py
"""
import json
import os
import re
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
SWA = rdflib.Namespace(export_rdf.NS["swauthor"])
SWX = rdflib.Namespace(export_rdf.NS["swtext"])
SW = rdflib.Namespace(export_rdf.NS["sw"])
PROV = rdflib.Namespace(export_rdf.NS["prov"])
PUBLIC = os.path.join(ROOT, "web", "public")


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
def all_close_matches(parsed):
    return set(parsed[export_rdf.GRAPH_FILE].subject_objects(SKOS.closeMatch))


@pytest.fixture(scope="module")
def close_matches(all_close_matches):
    """The node links."""
    return {(s, o) for s, o in all_close_matches if str(s).startswith(str(SWN))}


@pytest.fixture(scope="module")
def source_matches(all_close_matches):
    """The author and text links."""
    return {(s, o) for s, o in all_close_matches if str(s).startswith((str(SWA), str(SWX)))}


def test_every_close_match_is_on_a_node_or_a_source(all_close_matches, close_matches, source_matches):
    assert all_close_matches == close_matches | source_matches


def test_every_close_match_comes_from_an_accepted_figure_link(links, close_matches):
    accepted = {(SWN[l["key"]], WD[l["qid"]]) for l in links
                if l["kind"] == "figure" and export_rdf.link_accepted(l)}
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
    linksets = set(v.subjects(RDF.type, VOID.Linkset))
    linkset = rdflib.URIRef(export_rdf.BASE + "data/graph-wikidata")
    assert linksets == {linkset, rdflib.URIRef(export_rdf.BASE + "data/sources-wikidata")}
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
        assert f"spot-checked 38 links on {date}" in description and "awaits" not in description
    else:
        assert "awaits the maintainer's spot check" in description and "spot-checked" not in description


def source_iri(link):
    ns = SWA if link["kind"] == "author" else SWX
    return ns[export_rdf.source_slug(link["key"])]


def test_source_links_are_exported_only_with_check_records(links, source_matches, close_matches):
    others = [l for l in links if l["kind"] in ("author", "text")]
    assert others, "the file holds no author or text link to test against"
    accepted = {(source_iri(l), WD[l["qid"]]) for l in others if export_rdf.link_accepted(l)}
    assert source_matches == accepted
    for l in others:
        if not export_rdf.link_accepted(l):
            continue
        # the record of both families, and the maintainer's where he decided
        for field in ("proposed_by", "proposer_reason", "checked_by", "check", "check_reason", "date"):
            assert l.get(field), (l["key"], field)
        assert export_rdf.model_family(l["proposed_by"]) != export_rdf.model_family(l["checked_by"])
        if l["check"] != "accept":
            d = l.get("decision") or {}
            assert d.get("verdict") == "accept" and d.get("decided_by") and d.get("date") and d.get("reason"), l["key"]
    # a disagreement the maintainer settled with no link is exported nowhere
    linked = {s for s, _ in close_matches | source_matches}
    for record in json.load(open(export_rdf.LINKS_FILE, encoding="utf-8")).get("no_link", []):
        assert record["decision"]["verdict"] == "no link" and record["decision"]["reason"]
        assert SWN[record["key"]] not in linked and source_iri(record) not in linked, record["key"]


def test_source_iris_and_their_claims(graph, parsed, source_matches):
    g = parsed[export_rdf.GRAPH_FILE]
    sources = export_rdf.source_entities(graph)
    for kind, ns, cls, prop in (("author", SWA, PROV.Agent, SW.sourceAuthor),
                                ("text", SWX, SW.SourceText, SW.sourceText)):
        minted = set(g.subjects(RDF.type, cls)) if kind == "text" else \
            {s for s in g.subjects(RDF.type, PROV.Agent) if str(s).startswith(str(ns))}
        assert minted == {ns[slug] for slug, _ in sources[kind].values()}
        for string, (slug, _) in sources[kind].items():
            assert str(g.value(ns[slug], rdflib.RDFS.label)) == string
            assert string.lower() not in export_rdf.GENERIC_SOURCES
        field = "source_author" if kind == "author" else "source_text"
        expected = sum(1 for e in graph.edges for r in e.get("references") or []
                       if r.get(field) in sources[kind])
        assert len(list(g.subject_objects(prop))) == expected
        assert {o for _, o in g.subject_objects(prop)} <= minted


def test_source_counts_agree_with_the_links_file(graph, links, parsed, export, source_matches):
    accepted = [l for l in links if l["kind"] in ("author", "text") and export_rdf.link_accepted(l)]
    n_auth = sum(1 for l in accepted if l["kind"] == "author")
    n_text = sum(1 for l in accepted if l["kind"] == "text")
    assert len(source_matches) == n_auth + n_text
    authors, linked_authors, texts, linked_texts = export_rdf.source_counts(export_rdf.source_entities(graph))
    assert (linked_authors, linked_texts) == (n_auth, n_text)
    v = parsed[export_rdf.VOID_FILE]
    linkset = rdflib.URIRef(export_rdf.BASE + "data/sources-wikidata")
    assert int(v.value(linkset, VOID.triples)) == n_auth + n_text
    assert v.value(linkset, VOID.linkPredicate) == SKOS.closeMatch
    assert (rdflib.URIRef(export_rdf.BASE + "data/graph"), VOID.subset, linkset) in v
    description = str(v.value(linkset, export_rdf_term("dcterms", "description")))
    assert f"{n_auth} of {authors} authors and {n_text} of {texts} texts" in description
    assert "not on the website" in description
    head = " ".join(line[1:].strip() for line in export[export_rdf.GRAPH_FILE].split("\n") if line.startswith("#"))
    assert f"{n_auth} of the authors and {n_text} of the texts carry skos:closeMatch" in head


def test_no_author_or_text_link_appears_on_a_page_of_the_site(links):
    """The source links are data only. No generated page, script or
    data file the site serves names one; the Turtle downloads are the export."""
    figure_qids = {l["qid"] for l in links if l["kind"] == "figure"}
    source_qids = {l["qid"] for l in links if l["kind"] in ("author", "text")} - figure_qids
    assert source_qids
    pattern = re.compile(r"(?<![0-9A-Za-z])(Q[1-9][0-9]*)(?![0-9])")
    seen = 0
    for base, _, files in os.walk(PUBLIC):
        for name in files:
            if name.endswith(".ttl") or not name.endswith((".html", ".json", ".txt", ".xml", ".js")):
                continue
            path = os.path.join(base, name)
            text = open(path, encoding="utf-8", errors="replace").read()
            seen += 1
            found = set(pattern.findall(text)) & source_qids
            assert not found, (os.path.relpath(path, ROOT), sorted(found))
            assert export_rdf.NS["swauthor"] not in text and export_rdf.NS["swtext"] not in text, path
    assert seen > 1000, "web/public was not built"


def test_export_is_deterministic(graph, export):
    declarations = kg_query.load_json(DECLARATIONS)
    declarations["_path"] = DECLARATIONS
    again = export_rdf.build_all(graph, declarations)
    assert again == export


def test_each_file_header_mentions_the_links(export):
    for name, text in export.items():
        head = "\n".join(line for line in text.split("\n") if line.startswith("#"))
        assert "Wikidata" in head, name
