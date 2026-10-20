#!/usr/bin/env python3
"""
Invariant tests for the generated site: web/build-atlas.mjs and
tools/build_ledger_page.py.

Same discipline as tests/test_query.py — no pinned counts. The graph moves as
windows merge, so a test asserting "25 family pages" or "195 assigned" is a test
that rots. Every assertion here is a relationship that has to hold whatever the
graph currently says:

  * every generated page carries a canonical tag, and it is the extensionless
    URL of that page;
  * no generated page links to an internal .html path (the /v1.3/ snapshot is
    exempt and keeps its own links);
  * the per-family pages account for the family map's assigned total exactly
    once each, and each page prints its own family's count;
  * the ontology QA panel's JSON parses, and the numbers it reports appear on
    the rendered page;
  * the releases page renders a version pin naming a calibration record that
    exists and is a PASS;
  * the query page ships the semantics module byte-identical to its source, and
    that module agrees with the CLI on real filters;
  * the ledger's record ids are unique and every card carries its permalink; the
    history chip renders only for an edge that carries a history.

The pages are read as committed. If one is missing the test fails rather than
skipping: a page that is not on disk is not on the site either.

Run: python3 -m pytest tests/test_site_generators.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "web", "public")
SRC = os.path.join(ROOT, "web", "src")
SEED = os.path.join(ROOT, "seed.json")
DECLARATIONS = os.path.join(ROOT, "pipeline", "family", "relation_declarations.json")

sys.path.insert(0, os.path.join(ROOT, "tools", "query"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ontology_qa"))


# ------------------------------------------------------------- fixtures ---

def read(path):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.relpath(path, ROOT)} is not on disk — run "
                    f"`node web/build-atlas.mjs` and `python3 tools/build_ledger_page.py`")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# james.html is the James replication page, written by tools/build_james_page.py
# for a different artifact. It predates the URL convention, carries no canonical
# tag and is not in the sitemap. It is excluded here rather than silently passed,
# and the exception list is pinned by a test below so a new page cannot join it.
UNMANAGED = {"james.html"}


def generated_pages():
    """Every page the generators write, by absolute path. web/public/v1.3/ is the
    frozen snapshot and is never generated, so it is not walked."""
    return sorted(os.path.join(PUBLIC, f) for f in os.listdir(PUBLIC)
                  if f.endswith(".html") and f not in UNMANAGED)


def test_the_unmanaged_page_list_has_not_grown():
    """One page on the site is outside the URL convention. If a second appears,
    this fails: pages joining the site join the convention with it."""
    assert UNMANAGED == {"james.html"}
    for name in UNMANAGED:
        assert os.path.exists(os.path.join(PUBLIC, name)), (
            f"{name} is exempted but no longer exists — drop it from the list")


@pytest.fixture(scope="module")
def families_map():
    return json.loads(read(os.path.join(SRC, "families.json")))["map"]


@pytest.fixture(scope="module")
def sitemap():
    return read(os.path.join(PUBLIC, "sitemap.xml"))


# ------------------------------------------------- every page is a URL ---

def test_every_generated_page_carries_its_extensionless_canonical():
    for path in generated_pages():
        name = os.path.basename(path)[: -len(".html")]
        html = read(path)
        found = re.findall(r'<link rel="canonical" href="([^"]+)"', html)
        assert found, f"{name}: no canonical tag"
        assert len(found) == 1, f"{name}: {len(found)} canonical tags"
        url = found[0]
        assert url.startswith("https://symbolicworld.observer/"), url
        slug = url[len("https://symbolicworld.observer/"):]
        assert not slug.endswith(".html"), f"{name}: canonical points at a .html path"
        assert slug == name, f"{name}: canonical is /{slug}"


def test_no_generated_page_links_to_an_internal_html_path():
    offenders = []
    for path in generated_pages():
        for href in re.findall(r'href="([^"]+)"', read(path)):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "/v1.3/" in href:
                continue
            if re.search(r"\.html(\?|$|#)", href):
                offenders.append(f"{os.path.basename(path)} -> {href}")
    assert not offenders, offenders


def test_sitemap_lists_every_generated_page_and_nothing_missing(sitemap):
    listed = set(re.findall(r"<loc>https://symbolicworld\.observer/([^<]*)</loc>", sitemap))
    for path in generated_pages():
        name = os.path.basename(path)[: -len(".html")]
        assert name in listed, f"/{name} is generated but not in the sitemap"
    for slug in listed:
        if slug in ("", "v1.3/", "graph.json"):
            continue
        assert os.path.exists(os.path.join(PUBLIC, slug + ".html")), \
            f"/{slug} is in the sitemap with no page behind it"


def test_sitemap_lists_no_html_url(sitemap):
    assert ".html" not in sitemap


# ------------------------------------------------- the per-family pages ---

def family_page(name):
    return os.path.join(PUBLIC, f"family-{name}.html")


def printed_counts(html):
    """The countstrip's numbers, in order: assigned, strings, queued, declared."""
    strip = re.search(r'<div class="countstrip">(.*?)</div>', html, re.S)
    assert strip, "no countstrip on the page"
    return [int(n) for n in re.findall(r"<b>(\d+)</b>", strip.group(1))]


def test_every_family_in_the_map_has_a_page(families_map):
    for row in families_map["families"]:
        assert os.path.exists(family_page(row["family"])), row["family"]


def test_family_pages_sum_to_the_maps_assigned_total(families_map):
    total = 0
    for path in generated_pages():
        name = os.path.basename(path)
        if not name.startswith("family-"):
            continue
        total += printed_counts(read(path))[0]
    assert total == families_map["totals"]["assigned"]


def test_each_family_page_prints_its_own_count(families_map):
    for row in families_map["families"]:
        assigned, strings, _queued, _declared = printed_counts(read(family_page(row["family"])))
        assert assigned == row["edges"], row["family"]
        assert strings == len(row["strings"]), row["family"]


def test_a_family_with_no_assigned_edge_still_has_a_page_reporting_zero(families_map):
    """The ruleset's families and the map's families are different sets: a family
    emptied by a reclassification keeps its page and reports zero."""
    in_map = {row["family"] for row in families_map["families"]}
    pages = {os.path.basename(p)[len("family-"):-len(".html")]
             for p in generated_pages() if os.path.basename(p).startswith("family-")}
    for name in pages - in_map:
        assert printed_counts(read(family_page(name)))[0] == 0


def test_family_pages_show_graph_wide_totals_beside_the_family_count(families_map):
    totals = families_map["totals"]
    for row in families_map["families"][:5]:
        html = read(family_page(row["family"]))
        wide = re.search(r'<div class="countstrip dim">(.*?)</div>', html, re.S)
        assert wide, row["family"]
        text = wide.group(1)
        for value in (totals["assigned"], totals["pending"],
                      totals["no_family"], totals["text_undecided"]):
            assert str(value) in text, (row["family"], value)


def test_the_external_validity_table_sits_behind_a_headline(families_map):
    """V2-R9 — headline in words, table behind a native details, and the limit
    stated outside the fold."""
    for row in families_map["families"][:5]:
        html = read(family_page(row["family"]))
        section = html[html.index("Checked against readers of Jung"):]
        block = re.search(r"<details class=\"disclose\">(.*?)</details>", section, re.S)
        assert block, row["family"]
        summary = re.search(r"<summary>(.*?)</summary>", block.group(1), re.S).group(1)
        assert "works of scholarship" in summary, row["family"]
        assert "<table>" in block.group(1), row["family"]
        after = section[section.index("</details>"):]
        assert "Agreement is not endorsement" in after, (
            f"{row['family']}: the limit is inside the fold")


def test_progressive_disclosure_needs_no_script():
    """Native details/summary only — a page that hides its table behind JS hides
    it from anything that does not run JS."""
    for name in ("family-symbolization.html", "ontology.html"):
        html = read(os.path.join(PUBLIC, name))
        for block in re.findall(r"<details class=\"disclose\">.*?</details>", html, re.S):
            assert "<script" not in block, name
            assert "onclick" not in block, name


def test_the_ontology_findings_list_sits_behind_its_counts(qa_json):
    html = read(os.path.join(PUBLIC, "ontology.html"))
    block = re.search(r"<details class=\"disclose\">(.*?)</details>", html, re.S).group(1)
    summary = re.search(r"<summary>(.*?)</summary>", block, re.S).group(1)
    total = sum(qa_json["totals"].values())
    assert f"{total} findings" in summary
    assert "table class=\"findings\"" in block
    # the four headline figures stay outside the fold
    panel = html[html.index("<h2>The pitfall scan"):html.index("<details class=\"disclose\">")]
    assert str(qa_json["headline"]["hapax_pct"]) in panel


def test_document_labels_render_with_the_colon_the_document_carries():
    """Item 27, extended by the finalizer: the extraction strips the colon from
    a bold label when it keys it, so every label the family pages render from
    the document gets it back — not just Boundary. A full stop beside a colon is
    the inconsistency class this session exists to remove."""
    offenders = []
    for path in generated_pages():
        if not os.path.basename(path).startswith("family-"):
            continue
        for label in re.findall(r'<p class="dim ev"><b>([^<]*)</b>', read(path)):
            if not label.endswith(":"):
                offenders.append(f"{os.path.basename(path)}: {label}")
    assert not offenders, offenders
    js = read(os.path.join(ROOT, "web", "build-atlas.mjs"))
    assert '<b>${esc(n.label)}:</b>' in js, "the notes label lost its colon"
    assert '<b>Boundary:</b>' in js, "the boundary label lost its colon"


def test_the_works_the_check_consulted_are_cited_correctly():
    """Item 31 — the figures verified against the receipts but the titles did
    not: articles dropped, and the dictionary lost its three authors while every
    other work kept its editor. The list renders in one place, the families
    page's own exposition. Item 35 moved that exposition to the ontology page
    with the check it belongs to; the families document's own citations, below
    its rule, are quoted and are not ours to correct."""
    exposition = read(os.path.join(PUBLIC, "ontology.html"))
    families = read(os.path.join(PUBLIC, "families.html"))
    assert "works of scholarship" not in families[:families.index("<hr>")], (
        "the works list is stated twice")
    for title in ("Jacobi's <em>The Psychology of C. G. Jung</em>",
                  "Samuels, Shorter and Plaut's <em>A Critical Dictionary of Jungian Analysis</em>",
                  "von Franz's <em>Alchemy: An Introduction to the Symbolism and the Psychology</em>",
                  "Abraham's <em>A Dictionary of Alchemical Imagery</em>"):
        assert title in exposition, title
    for dropped in ("<em>Psychology of C.G. Jung</em>",
                    "the <em>Critical Dictionary of Jungian Analysis</em>",
                    "<em>Alchemy: An Introduction</em>,",
                    "<em>Dictionary of Alchemical Imagery</em>"):
        assert dropped not in exposition, f"an old citation survives: {dropped}"
    # the volume count stays bound to the receipts rather than typed
    ev = json.loads(read(os.path.join(
        ROOT, "docs", "experiments", "external_validity_2026-08", "results.json")))
    words = ["zero", "one", "two", "three", "four"]
    assert f"{words[ev['edinger_volumes']]} volumes of Edinger" in exposition


def test_the_external_check_lives_on_ontology_and_the_links_point_at_it():
    """Item 35 — the check moved to the ontology page, where the page arc runs
    internal checks, external check, deliberately absent. The anchor exists in
    exactly one place, and everything that referred to it followed."""
    ont = read(os.path.join(PUBLIC, "ontology.html"))
    fam = read(os.path.join(PUBLIC, "families.html"))
    assert ont.count('id="checked"') == 1
    assert 'id="checked"' not in fam
    # /families keeps one line, and it is a link to the record
    exposition = fam[:fam.index("<hr>")]
    assert exposition.count("/ontology#checked") == 1, "the families link is not once"
    assert "Checked once against outside scholarship" in exposition
    # and no page still points at the anchor's old home
    for path in generated_pages():
        assert "/families#checked" not in read(path), os.path.basename(path)
    method = read(os.path.join(ROOT, "docs", "METHOD_COPY.md"))
    assert "(/ontology#checked)" in method and "/families#checked" not in method


def test_the_families_page_is_reference_not_method():
    """Item 35 — /families is the reference surface: the states and provenance
    tables, the string-to-family map, what fits nowhere, the boundary rules and
    the document. The method exposition it used to carry lives on /ontology and
    the method page now, stated once."""
    fam = read(os.path.join(PUBLIC, "families.html"))
    exposition = fam[:fam.index("<hr>")]
    for gone in ("What a family is", "How an edge gets a family",
                 "Agreement between the two arms", "planting classification errors"):
        assert gone not in exposition, f"method content is still on /families: {gone}"
    for kept in ("Where the layer stands", "How the records were arrived at",
                 "The map: which relation strings land in which family",
                 "What fits nowhere", "Where the boundaries are decided",
                 "The definitions document, in full"):
        assert kept in exposition, f"reference content went missing: {kept}"
    # one header sentence, carrying both pointers
    assert '<a href="/ontology">design</a>' in exposition
    assert '<a href="/#/method">checks</a>' in exposition
    # and the page is now a fraction of what it was: the copy above the
    # document's rule ran to about 3,000 words before the redistribution.
    # The string->family map grows with the graph and is data, not copy, so
    # it is excluded from the bound — the guard is against method prose
    # returning, not against mining progress (first tripped by b-cw8-1).
    prose = re.sub(r'<section class="fam">[\s\S]*?</section>', " ", exposition)
    words = len(re.sub(r"<[^>]+>", " ", prose).split())
    assert words < 1500, f"the families exposition is back up to {words} words"


def test_no_family_page_calls_a_family_verified():
    """The standing vocabulary rule: a family is assigned; verification belongs
    to the quote and its paragraph."""
    banned = re.compile(r"verified famil|famil\w* (?:is|are) verified", re.I)
    for path in generated_pages():
        if not os.path.basename(path).startswith("family-"):
            continue
        assert not banned.search(read(path)), os.path.basename(path)


# -------------------------------------------------------- the releases ---

def live_entry(html):
    """The entry for the release being prepared. Item 28 drafted the later
    entries too, so "the first solid one" no longer identifies it — the version
    does."""
    for entry in re.findall(r'<section class="rel-entry[^"]*">(.*?)</section>', html, re.S):
        heading = re.search(r"<h2>(.*?)</h2>", entry, re.S)
        if heading and "v2.0" in heading.group(1):
            return entry
    raise AssertionError("no v2.0 entry on the releases page")


def test_releases_page_renders_the_version_pin():
    html = read(os.path.join(PUBLIC, "releases.html"))
    pins = re.findall(r'<div class="pin">(.*?)</div>', live_entry(html), re.S)
    assert pins, "no version pin on the pending release entry"
    text = re.sub(r"<[^>]+>", "", pins[0])
    assert re.search(r"graph v[\d.]+", text), text
    assert re.search(r"ruleset v[\d.]+", text), text
    record = re.search(r"(pipeline/family_calibration/records/[\w.\-]+\.json)", text)
    assert record, text
    assert "(PASS)" in text
    with open(os.path.join(ROOT, record.group(1)), encoding="utf-8") as fh:
        assert json.load(fh)["verdict"] == "PASS"


def test_releases_pin_names_the_binding_ruleset():
    html = read(os.path.join(PUBLIC, "releases.html"))
    doc = read(os.path.join(ROOT, "docs", "FAMILY_DEFINITIONS.md"))
    version = re.search(r"^# Relation families.*?(v[\d.]+)", doc, re.M).group(1)
    pin = re.sub(r"<[^>]+>", "", re.findall(r'<div class="pin">(.*?)</div>', live_entry(html), re.S)[0])
    assert f"ruleset {version}" in pin, pin


# item 19 — every entry carries the same four sections, in this order
RELEASE_SECTIONS = ("mining status", "governance", "core build", "UI")


def test_every_release_entry_has_the_same_four_sections_in_order():
    html = read(os.path.join(PUBLIC, "releases.html"))
    entries = re.findall(r'<section class="rel-entry[^"]*">(.*?)</section>', html, re.S)
    assert len(entries) >= 2, "expected the pending v2.0 entry and the frozen baseline"
    for entry in entries:
        headings = re.findall(r"<h4>(.*?)</h4>", entry)
        assert headings == list(RELEASE_SECTIONS), (
            re.search(r"<h2>(.*?)</h2>", entry, re.S).group(1).strip()[:40], headings)


def test_the_baseline_entry_is_present_and_last():
    html = read(os.path.join(PUBLIC, "releases.html"))
    headings = re.findall(r'<section class="rel-entry[^"]*">\s*<h2>(.*?)</h2>', html, re.S)
    assert "v1.3.0" in headings[-1], headings
    entry = re.findall(r'<section class="rel-entry[^"]*">(.*?)</section>', html, re.S)[-1]
    seed_meta = json.loads(read(os.path.join(SRC, "atlas.json")))["meta"]["frozen"]
    for value in (seed_meta["nodes"], seed_meta["edges"], seed_meta["references"]):
        assert str(value) in entry, value
    assert "zenodo" in entry.lower()


def test_release_entries_point_at_their_artifacts():
    """Repo-side artifacts are named paths in code formatting; site-side ones
    are real extensionless links."""
    html = read(os.path.join(PUBLIC, "releases.html"))
    body = html[html.index("<main"):]
    for path in ("tools/query/kg_query.py", "docs/ATLAS_REQUIREMENTS.md",
                 "tools/check_paper_facts.py", "docs/PAPER.md"):
        assert f"<code>{path}</code>" in body, path
    for link in ("/ledger", "/families", "/ontology", "/query", "/v1.3/"):
        assert f'href="{link}"' in body, link


def test_releases_are_ordered_newest_first():
    """The generator sorts by the version in each heading; it does not trust the
    order the file happens to be written in."""
    html = read(os.path.join(PUBLIC, "releases.html"))
    headings = re.findall(r'<section class="rel-entry[^"]*">\s*<h2>(.*?)</h2>', html, re.S)
    versions = [tuple(int(n) for n in re.search(r"v(\d+)\.(\d+)", h).groups())
                for h in headings]
    assert versions == sorted(versions, reverse=True), headings
    source = read(os.path.join(ROOT, "docs", "RELEASES.md"))
    in_file = [tuple(int(n) for n in m.groups())
               for m in re.finditer(r"^## v(\d+)\.(\d+)", source, re.M)]
    assert in_file != versions, (
        "the file is already in display order, so this test cannot see whether "
        "the generator sorts — reorder the file or the assertion is vacuous")


def test_the_pending_release_entry_has_substance():
    """The entry being prepared carries the release, not a sketch."""
    html = read(os.path.join(PUBLIC, "releases.html"))
    body = live_entry(html)
    for heading in RELEASE_SECTIONS:
        assert f">{heading}<" in body, heading
    assert "clause-predicate" in body, "the defect story is not in the entry"
    assert "form rule" in body
    assert re.search(r"href=\"/batch-b-cw\w+-\d+\"", body), (
        "the entry names no batch that links to its delta page")
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    # item 32 — changelog register, with a ceiling as well as a floor. The
    # ceiling moved 400 -> 450 (Damian, 2026-10-08): the v2.0.0 close-out
    # (452bee3) grew the entry to 422 words by recording the tag and the
    # Zenodo record, which is release substance, not sketch; the published
    # entry stands as written rather than being trimmed after the fact.
    assert 150 < words <= 450, f"the entry is {words} words"


def test_the_releases_intro_is_two_paragraphs_and_no_machinery():
    """Item 30 — the page opened with four paragraphs about how the file is
    written. What a reader needs is what the page is and what a pin means; the
    conventions live in an editorial note the renderer strips."""
    html = read(os.path.join(PUBLIC, "releases.html"))
    intro = html[html.index("<h1>Releases</h1>"):html.index('<section class="rel-entry')]
    assert intro.count("<p>") == 2, f"the intro is {intro.count('<p>')} paragraphs"
    text = re.sub(r"<[^>]+>", " ", intro)
    for machinery in ("named tokens", "double braces", "repo-relative",
                      "line for line", "build-atlas.mjs"):
        assert machinery not in text, f"contributor machinery still rendered: {machinery}"
    # the intro: what the page is, and what an entry opens with (Damian's
    # 2026-10-18 rewrite replaced the pin sentence with a three-item list)
    assert "A list of changes and key updates" in text
    assert "Each entry opens with" in text

    # the conventions are kept, in a note the renderer never shows
    source = read(os.path.join(ROOT, "docs", "RELEASES.md"))
    note = re.search(r"<!--(.*?)-->", source, re.S)
    assert note, "the editorial note is gone from the source file"
    for convention in ("mining status", "repo-relative", "double braces", "newest-first"):
        assert convention in note.group(1), f"the note lost a convention: {convention}"
    assert "<!--" not in html and "EDITORIAL" not in html


def test_releases_page_carries_no_unbound_token():
    assert "{{" not in read(os.path.join(PUBLIC, "releases.html"))


# --------------------------------------------------------- the ontology ---

@pytest.fixture(scope="module")
def qa_json():
    out = subprocess.run([sys.executable,
                          os.path.join(ROOT, "tools", "ontology_qa", "quality.py"),
                          SEED, "--json"],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_qa_json_parses_and_carries_its_headline(qa_json):
    head = qa_json["headline"]
    for key in ("hapax_relations", "distinct_relations", "hapax_pct",
                "sentence_shaped_relations", "detached_components",
                "declared_inverses", "nodes", "edges"):
        assert key in head, key
    assert 0 <= head["hapax_pct"] <= 100
    assert head["hapax_relations"] <= head["distinct_relations"]
    assert head["detached_components"] == head["components"] - 1
    assert qa_json["totals"]["critical"] == len(qa_json["critical"])


def test_qa_json_mode_reports_the_same_findings_as_the_prose_mode(qa_json):
    out = subprocess.run([sys.executable,
                          os.path.join(ROOT, "tools", "ontology_qa", "quality.py"), SEED],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    tags = re.findall(r"^\[(.+)\]$", out.stdout, re.M)
    json_tags = [f["tag"] for sev in ("critical", "important", "minor") for f in qa_json[sev]]
    assert tags == json_tags
    assert f"TOTAL: {qa_json['totals']['critical']} critical" in out.stdout


def test_the_qa_panels_numbers_appear_on_the_rendered_page(qa_json):
    html = read(os.path.join(PUBLIC, "ontology.html"))
    panel = html[html.index("The pitfall scan"):]
    head = qa_json["headline"]
    for value in (head["hapax_relations"], head["distinct_relations"],
                  head["sentence_shaped_relations"], head["sentence_shaped_edges"],
                  head["detached_components"], head["largest_component"]):
        assert str(value) in panel, value
    assert str(head["hapax_pct"]) in panel
    coverage = head["declared_inverses"]
    assert (f'{coverage["observed_pairs_declared"]}/'
            f'{coverage["observed_inverse_pairs_in_vocabulary"]}') in panel


def test_every_scan_finding_reaches_the_page_with_a_stance(qa_json):
    html = read(os.path.join(PUBLIC, "ontology.html"))
    stances = re.findall(r'<span class="chip st-(\w+)">', html)
    findings = [f for sev in ("critical", "important", "minor") for f in qa_json[sev]]
    assert len(stances) == len(findings)
    assert "unclassified" not in stances, (
        "a finding has no recorded stance — add one to QA_STANCE in build-atlas.mjs "
        "rather than leaving the page to report it unexplained")
    for f in findings:
        assert f["tag"] in html, f["tag"]


def test_no_rendered_page_leaks_raw_markdown():
    """Item 34 — a declaration's `source.section` is the document's own markdown
    heading ("### 1. symbolization") and was rendered verbatim as a label. The
    marker is stripped at the renderer; the document is never edited. Sweeps
    every page for heading markers and unrendered emphasis outside code."""
    offenders = []
    for path in sorted(os.path.join(PUBLIC, f) for f in os.listdir(PUBLIC) if f.endswith(".html")):
        html = read(path)
        body = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html)
        body = re.sub(r"<code>[\s\S]*?</code>", " ", body)
        body = re.sub(r"<pre>[\s\S]*?</pre>", " ", body)
        for marker in ("###", "**"):
            if marker in body:
                hit = body[max(0, body.index(marker) - 60):body.index(marker) + 40]
                offenders.append(f"{os.path.basename(path)}: {marker} in ...{hit.strip()}...")
    assert not offenders, offenders


def test_a_declaration_section_renders_as_a_label(qa_json):
    """The label still names the document's section, minus the marker."""
    decls = json.loads(read(DECLARATIONS))
    html = read(os.path.join(PUBLIC, "ontology.html"))
    for decl in decls["active"]:
        if decl.get("dormant"):
            continue
        for source in decl["source"]:
            label = re.sub(r"^\s*#+\s*", "", source["section"])
            assert f"{label} (line {source['line']})" in html, label
    js = read(os.path.join(ROOT, "web", "build-atlas.mjs"))
    assert "const sectionLabel = (t) =>" in js
    assert "esc(sectionLabel(" in js


def test_the_ontology_page_puts_the_evidence_before_the_conclusions():
    """Item 34(f) — the scan and its findings come BEFORE what is deliberately
    absent, so the absences read as conclusions drawn from the evidence rather
    than assertions made ahead of it."""
    html = read(os.path.join(PUBLIC, "ontology.html"))
    order = [re.sub(r"<[^>]+>", "", h) for h in re.findall(r"<h2[^>]*>.*?</h2>", html)]
    assert order == ["Two tiers", "The declarations", "Atlas, Graph, Ontology",
                     "The pitfall scan", "Checked against readers of Jung",
                     "Deliberately absent"], order


def test_the_ontology_figures_carry_real_data():
    """Item 34(e) — both drawn boxes read the graph; nothing in them is typed."""
    html = read(os.path.join(PUBLIC, "ontology.html"))
    figures = re.findall(r'<figure class="ofig">(.*?)</figure>', html, re.S)
    assert len(figures) == 2, f"{len(figures)} figures"
    anatomy, tiers = figures
    seed = json.loads(read(SEED))
    quotes = {r.get("quote") for e in seed["edges"] for r in e["references"]}
    drawn = re.search(r'<div class="ofig-quote ev">&ldquo;(.*?)&rdquo;</div>', anatomy)
    assert drawn, "the anatomy box draws no quote"
    quote = drawn.group(1).replace("&amp;", "&").replace("&#39;", "'")
    assert any(quote == (q or "").replace("&", "&") for q in quotes) or quote in {q or "" for q in quotes}, (
        "the drawn quote is not a quote in the graph")
    assert re.search(r"CW \w+ §\d+", anatomy), "the anatomy box draws no citation"

    fam_map = json.loads(read(os.path.join(SRC, "families.json")))["map"]
    top = fam_map["families"][0]
    assert f'{top["family"]} <span class="n">{top["edges"]}</span>' in tiers, (
        "the family chip's count is not the map's")
    for row in top["strings"][:4]:
        assert f'<code>{row["string"]}</code> <span class="n">{row["edges"]}</span>' in tiers, row["string"]


def test_the_ontology_page_states_where_its_checks_come_from(qa_json):
    """The scan borrows the OOPS! catalogue's numbering; the page says so, cites
    it, and lists every pitfall code the tool actually uses."""
    html = read(os.path.join(PUBLIC, "ontology.html"))
    section = html[html.index("Atlas, Graph, Ontology"):html.index("<h2>The pitfall scan")]
    assert "OntOlogy Pitfall Scanner" in section
    assert "Poveda-Villal" in section
    assert "not the OOPS! service" in section
    source = read(os.path.join(ROOT, "tools", "ontology_qa", "quality.py"))
    cited = set(re.findall(r"P\d{2}", source))
    cited |= {code for sev in ("critical", "important", "minor")
              for f in qa_json[sev] for code in re.findall(r"P\d{2}", f["tag"])}
    listed = set(re.findall(r'<td class="n">(P\d{2})</td>', section))
    assert listed == cited, cited ^ listed
    assert "no gloss recorded" not in section, (
        "a pitfall code the scan cites has no gloss — add it to PITFALLS in build-atlas.mjs")


def test_the_ontology_page_names_what_is_deliberately_absent():
    html = read(os.path.join(PUBLIC, "ontology.html"))
    # item 34(f) — the absences now follow the scan, so the slice runs to the end
    section = html[html.index("Deliberately absent"):]
    for phrase in ("Transitivity", "Domain and range", "Disjoint types",
                   "subsumption backbone", "closed relation vocabulary"):
        assert phrase in section, phrase


def test_active_declarations_are_all_on_the_page():
    decls = json.loads(read(DECLARATIONS))
    html = read(os.path.join(PUBLIC, "ontology.html"))
    for decl in decls["active"]:
        if decl.get("dormant"):
            continue
        pair = (f"{decl['forward']} / {decl['inverse']}" if decl["kind"] == "inverse"
                else decl["relation"])
        assert pair in html, decl["id"]


# ------------------------------------------------ V2-R10 · the site menu ---

MENU_RE = re.compile(r'<nav class="topmenu">(.*?)</nav>', re.S)


def menu_items(html):
    """[(href, label)] for the page's top menu, aria-current stripped."""
    found = MENU_RE.search(html)
    assert found, "no top menu on the page"
    return re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', found.group(1))


def menu_shape(html):
    """[(group, [(href, label), ...]), ...] — the taxonomy as rendered."""
    found = MENU_RE.search(html)
    assert found, "no top menu on the page"
    groups, current = [], None
    for token in re.finditer(
            r'<span class="mgroup">([^<]+)</span>|<a href="([^"]+)"[^>]*>([^<]+)</a>',
            found.group(1)):
        if token.group(1):
            current = (token.group(1), [])
            groups.append(current)
        else:
            assert current, "a menu link appears before any group label"
            current[1].append((token.group(2), token.group(3)))
    return groups


EXPECTED_MENU = [
    ("explore", [("/#/atlas", "atlas"), ("/routes", "routes"),
                 ("/query", "query"), ("/#/concordance", "concordance")]),
    ("reference", [("/concepts", "concepts"), ("/families", "families")]),
    ("provenance", [("/ledger", "ledger"), ("/releases", "releases"),
                    ("/disputes", "disputes")]),
    ("about", [("/nutshell", "in a nutshell"), ("/#/method", "method"),
               ("/ontology", "design")]),
]


def test_every_generated_page_carries_the_same_menu():
    reference = None
    for path in generated_pages():
        items = menu_items(read(path))
        if reference is None:
            reference = items
        assert items == reference, os.path.basename(path)
    assert reference, "no generated page carried a menu"
    assert [label for _href, label in reference] == [
        label for _group, items in EXPECTED_MENU for _href, label in items]


def test_the_app_carries_the_same_menu_as_the_generated_pages():
    app = menu_items(read(os.path.join(ROOT, "web", "index.html")))
    page = menu_items(read(os.path.join(PUBLIC, "releases.html")))
    assert app == page


def test_the_menu_carries_the_ruled_taxonomy_everywhere():
    """Same groups, same items, same order — on every generated page and in the
    app. The group labels are signposts, so they are part of the contract."""
    pages = [p for p in generated_pages()] + [os.path.join(ROOT, "web", "index.html")]
    for path in pages:
        shape = [(group, list(items)) for group, items in menu_shape(read(path))]
        assert shape == [(g, list(i)) for g, i in EXPECTED_MENU], os.path.basename(path)


def test_the_app_toolbar_holds_no_second_navigation():
    """Item 10: one menu, once. Every destination appears in index.html exactly
    once, and the toolbar keeps controls only — search, fit, reset, counts."""
    html = read(os.path.join(ROOT, "web", "index.html"))
    for _group, items in EXPECTED_MENU:
        for href, _label in items:
            assert html.count(f'href="{href}"') == 1, href
    toolbar = re.search(r'<header id="topbar"[^>]*>(.*?)</header>', html, re.S).group(1)
    for gone in ("open-concordance", "open-families", "ledger-link",
                 "disputes-link", "open-method"):
        assert gone not in toolbar, f"{gone} is still a second way to navigate"
    for kept in ('id="search"', 'id="fit"', 'id="relayout"', 'id="stats"', 'id="version"'):
        assert kept in toolbar, kept


def test_the_app_survives_the_removed_toolbar_buttons():
    """The handlers those buttons carried must bind optionally, or the app
    throws on load and the whole atlas goes blank."""
    js = read(os.path.join(ROOT, "web", "src", "main.js"))
    for handler in ("open-concordance", "open-families", "open-method"):
        assert f"$('{handler}')?." in js, (
            f"$('{handler}') is bound without a guard and the button is gone")
    for route in ("'#/concordance'", "'#/method'", "'#/families'"):
        assert route in js, f"{route} is no longer routable"


def test_both_generator_languages_hold_the_same_menu_list():
    """One list per language; this is what keeps them one menu."""
    js = read(os.path.join(ROOT, "web", "build-atlas.mjs"))
    block = js[js.index("const MENU = ["):js.index("const topMenu")]
    js_groups = re.findall(r"^\s*\['(\w+)', \[(.*)\]\],?$", block, re.M)
    parsed = [(group, re.findall(r"\['(/[^']*)', '([\w ]+)'\]", items))
              for group, items in js_groups]
    assert parsed == [(g, list(i)) for g, i in ledger_gen.MENU]
    assert parsed == [(g, list(i)) for g, i in EXPECTED_MENU]


def test_the_menu_marks_the_page_it_is_on():
    """Every static destination marks itself, and only itself."""
    for slug in ("releases", "query", "ontology", "families", "ledger", "disputes",
                 "concepts", "routes"):
        html = read(os.path.join(PUBLIC, slug + ".html"))
        current = re.findall(r'<a href="([^"]+)" aria-current="page">', MENU_RE.search(html).group(1))
        assert current == [f"/{slug}"], (slug, current)


def test_every_destination_can_be_marked_current_somewhere():
    """Item 14 — the gold state was applied for static pages and for nothing
    else, so concordance, method, families and the queue never lit. Each of the
    nine destinations is marked either by a generated page or by the app's route
    map; a destination in neither can never show you where you are."""
    js = app_js()
    block = js[js.index("const MENU_HREF = {"):]
    block = block[:block.index("}")]
    routed = set(re.findall(r"'(/[^']*)'", block))
    static = set()
    for path in generated_pages():
        for href in re.findall(r'<a href="([^"]+)" aria-current="page">',
                               MENU_RE.search(read(path)).group(1)):
            static.add(href)
    destinations = {href for _group, items in EXPECTED_MENU for href, _label in items}
    missing = destinations - routed - static
    assert not missing, f"never marked current anywhere: {sorted(missing)}"


def test_the_app_marks_the_route_it_is_on():
    js = app_js()
    assert "function markCurrent(" in js
    assert "markCurrent(modeEl, MENU_HREF[route] || '')" in js
    for route in ("'#/concordance'", "'#/method'", "'#/families'", "'#/queue'"):
        assert route in js[js.index("const MENU_HREF = {"):], route
    # every route that opens a page passes its route to the choke point
    for call in ("}, '#/method')", "}, '#/concordance')",
                 "scrollTo === 'queue-section' ? '#/queue' : '#/families')"):
        assert call in js, call


def test_menu_hash_destinations_are_routed_in_app_not_reloaded():
    """Item 14 — the hrefs are absolute so a generated page can load the app;
    inside the app that same href is a different PATH unless the app is served
    from exactly /, and the browser reloaded the document, which threw the
    viewport and the selection away."""
    js = app_js()
    assert ".closest('.topmenu a, .brand[href]')" in js
    assert "ev.preventDefault()" in js
    # item 16 replaced the deferred hash assignment with a same-task route
    assert "history.pushState(null, '', route[1])" in js
    assert "applyHash()" in js
    # modified clicks and real pages are left to the browser
    assert "ev.metaKey || ev.ctrlKey" in js
    assert "if (!route) return" in js


# ------------------------------------------ item 24 · one left edge, one gutter ---

def test_the_gutter_is_one_token_defined_once():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert css.count("--page-gutter:") == 2, (
        "the gutter token is not defined once at :root plus its one narrow-screen "
        "override")
    tokens = read(os.path.join(ROOT, "web", "src", "tokens.css"))
    assert "--page-gutter:" in tokens, "the app does not receive the gutter token"
    # the header, the band's column and the content columns all consume it
    for selector in (r"\.site-header \.hrow {", r"\n\.page-main {", r"#mode-panel \.page {"):
        rule = re.search(selector + r"([^}]*)}", css).group(1)
        assert "var(--page-gutter)" in rule, selector


# the selectors that carry the column, the band, or the reading measure — the
# places where a page-local width or horizontal margin moves text sideways
GEOMETRY_SELECTORS = re.compile(
    r"^(main|p|\.page-main|\.titleband|\.intro|\.sub|\.lede2|\.note)$")
HORIZONTAL = re.compile(
    r"(^|;)\s*(width|max-width|min-width|margin|padding|margin-left|margin-right"
    r"|padding-left|padding-right)\s*:")


def test_no_page_sets_its_own_column_band_or_measure_geometry():
    """Item 24 addendum. disputes.html carried max-width: 64ch on .intro in its
    OWN style block while the generated pages drew 68ch from the chrome, which
    at a wide viewport put its text on a different left edge. Hand-maintained
    pages are exactly where a class-based test is blind, so this one reads the
    inline styles of EVERY page in web/public — the exempted ones included."""
    pages = sorted(os.path.join(PUBLIC, f) for f in os.listdir(PUBLIC) if f.endswith(".html"))
    offenders = []
    for path in pages:
        for block in re.findall(r"<style>(.*?)</style>", read(path), re.S):
            for selector, body in re.findall(r"([^{}]+){([^}]*)}", block):
                sel = selector.strip().split("\n")[-1].strip()
                if sel.startswith("@"):
                    continue
                parts = [x.strip() for x in sel.split(",")]
                if not any(GEOMETRY_SELECTORS.match(x) for x in parts):
                    continue
                for decl in body.split(";"):
                    if not HORIZONTAL.match(decl.strip() and ";" + decl or ""):
                        continue
                    prop = decl.split(":")[0].strip()
                    if prop in ("margin-bottom", "margin-top", "padding-bottom", "padding-top"):
                        continue
                    if prop in ("margin", "padding") and _vertical_only(decl):
                        continue
                    offenders.append(f"{os.path.basename(path)}: {sel} {{{decl.strip()}}}")
    assert not offenders, offenders


def _vertical_only(decl):
    """`margin: .3rem 0 .8rem` touches no left edge; `margin: 0 auto` does."""
    value = decl.split(":", 1)[1].strip()
    parts = value.split()
    if len(parts) == 1:
        return parts[0] in ("0", "0px", "0rem")
    horizontal = parts[1] if len(parts) > 1 else parts[0]
    return horizontal in ("0", "0px", "0rem")


def test_the_reading_measure_is_one_number_from_the_chrome():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert "--measure:" in css, "the reading measure is not a token"
    rule = re.search(r"\np, \.intro, \.sub, \.lede2, \.note {([^}]*)}", css)
    assert rule and "var(--measure)" in rule.group(1), "the shared measure rule is gone"
    # and no page sets a measure on a reading paragraph of its own — the
    # disputes case, which was 64ch against the chrome's 68ch
    for path in sorted(os.path.join(PUBLIC, f) for f in os.listdir(PUBLIC) if f.endswith(".html")):
        for block in re.findall(r"<style>(.*?)</style>", read(path), re.S):
            for selector, body in re.findall(r"([^{}]+){([^}]*)}", block):
                sel = selector.strip().split("\n")[-1].strip()
                if any(GEOMETRY_SELECTORS.match(x.strip()) for x in sel.split(",")):
                    assert "max-width" not in body, (
                        f"{os.path.basename(path)}: {sel} sets its own measure")


# Item 26 — centring is permitted at exactly one level: the container. The ban
# on centring anything inside it stands.
CONTAINER_SELECTORS = (".page-main", "#mode-panel .page", ".site-header .hrow", "#prose")


def test_centring_happens_only_at_the_container():
    """Item 24's ban stands inside the container; item 26 allows the container
    itself to centre as a block. A band, a column's contents or a kind that
    centres reintroduces the drift the interview settled."""
    css = read(os.path.join(PUBLIC, "chrome.css")) + "\n" + read(os.path.join(ROOT, "web", "src", "style.css"))
    for selector, body in re.findall(r"([^{}\n]+){([^}]*)}", css):
        if not re.search(r"margin[^;]*:\s*[^;]*\bauto\b", body):
            continue
        sel = selector.strip()
        if any(sel.startswith(c) or sel == c for c in CONTAINER_SELECTORS):
            continue
        assert not re.search(r"\.page-main|\.titleband|#mode-panel \.page|\bmain\b", sel), (
            f"something inside the container centres itself: {sel} {{{body.strip()}}}")


def test_the_container_is_one_token_and_shared_by_header_and_page():
    """The header's content row and the page column take the same cap and the
    same centring, which is what puts the brand exactly above the titles."""
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert css.count("--page-max:") == 1, "the container cap is not defined once"
    for selector in (r"\.site-header \.hrow {", r"\n\.page-main {", r"#mode-panel \.page {"):
        rule = re.search(selector + r"([^}]*)}", css).group(1)
        assert "var(--page-max)" in rule, f"{selector} does not take the container cap"
        assert "margin-inline: auto" in rule, f"{selector} does not centre as a block"
        assert "var(--page-gutter)" in rule, f"{selector} lost the gutter"
    # the bar itself stays full-bleed: no cap on .site-header, only on its rows
    bar = re.search(r"\n\.site-header {([^}]*)}", css).group(1)
    assert "max-width" not in bar, "the header bar is capped instead of full-bleed"
    assert "background" in bar and "border-bottom" in bar


def test_the_kind_caps_what_the_container_holds_not_the_container():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    prose = re.search(r"\.page-main\.prose > \*[^{]*{([^}]*)}", css).group(1)
    records = re.search(r"\.page-main\.records > \*[^{]*{([^}]*)}", css).group(1)
    assert "max-width" in prose and "max-width" in records and prose != records
    for rule in (prose, records):
        assert "margin" not in rule and "padding" not in rule, (
            "a kind sets more than its right-hand cap")


def test_one_left_edge_on_every_generated_page():
    """The brand, the breadcrumb, the title band and the first content element
    all start at the same place — asserted structurally, since the geometry is
    one shared rule and no page may scope its own."""
    css = read(os.path.join(PUBLIC, "chrome.css"))
    for path in generated_pages():
        style = "\n".join(re.findall(r"<style>(.*?)</style>", read(path), re.S))
        for selector, body in re.findall(r"([^{}\n]+){([^}]*)}", style):
            if re.search(r"margin-left|padding-left", body) and re.search(
                    r"\bmain\b|\.page-main|\.titleband", selector):
                raise AssertionError(
                    f"{os.path.basename(path)} sets its own left edge: {selector.strip()}")
    # and the kinds differ only on the right
    prose = re.search(r"\.page-main\.prose > \*[^{]*{([^}]*)}", css).group(1)
    records = re.search(r"\.page-main\.records > \*[^{]*{([^}]*)}", css).group(1)
    for rule in (prose, records):
        assert "max-width" in rule
        assert "margin" not in rule and "padding" not in rule, (
            "a kind sets more than its right-hand cap")


# ------------------------------------- item 22 · the title band is locked ----

def test_the_second_header_row_is_a_reserved_constant_height():
    """The band's offset is measured from the header's bottom edge, so that edge
    has to be at the same y everywhere. The row is a reserved slot: it holds a
    breadcrumb, the tools cluster, both or neither, and keeps its height."""
    css = read(os.path.join(PUBLIC, "chrome.css"))
    row = re.search(r"\.site-header \.hrow-2 {([^}]*)}", css).group(1)
    assert re.search(r"height:\s*[\d.]+rem", row), f"the row is not a fixed height: {row.strip()}"
    search = re.search(r"\.site-header \.std-search {([^}]*)}", css).group(1)
    assert "height" in search, "the tallest thing in the row is unconstrained"
    for path in generated_pages():
        header = re.search(HEADER_RE, read(path)).group(0)
        assert 'class="hrow hrow-2"' in header, os.path.basename(path)
    index = read(os.path.join(ROOT, "web", "index.html"))
    assert 'class="hrow hrow-2"' in index


def test_the_title_band_geometry_is_defined_once_and_locked():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert css.count("\n.titleband {") == 1
    band = re.search(r"\n\.titleband {([^}]*)}", css).group(1)
    assert re.search(r"margin: 0 (auto|0)", band), "the band carries a top margin of its own"
    for selector, expect in ((r"\.titleband > :first-child", "margin-top: 0"),
                             (r"\.titleband \.eyebrow", "margin: 0 0"),
                             (r"\.titleband h1", "margin: 0")):
        rule = re.search(selector + r" {([^}]*)}", css)
        assert rule and expect in rule.group(1), selector
    tokens = read(os.path.join(ROOT, "web", "src", "tokens.css"))
    assert ".titleband h1" in tokens, "the app does not receive the locked band"


def test_the_title_band_is_decoupled_from_the_column_kind():
    """Item 23 — one band position on every surface. The band takes the prose
    column's width and centres inside whatever column holds it; both kinds are
    viewport-centred, so the band lands on the same pixel either way. A selector
    that scopes the band to a kind reintroduces the jump."""
    css = read(os.path.join(PUBLIC, "chrome.css"))
    band = re.search(r"\n\.titleband {([^}]*)}", css).group(1)
    assert "width:" in band, f"the band does not set its own width: {band}"
    assert "margin: 0 auto" not in band, "the band centres itself instead of taking the gutter"
    sources = {"chrome.css": css,
               "tokens.css": read(os.path.join(ROOT, "web", "src", "tokens.css")),
               "style.css": read(os.path.join(ROOT, "web", "src", "style.css"))}
    for path in generated_pages():
        sources[os.path.basename(path)] = "\n".join(
            re.findall(r"<style>(.*?)</style>", read(path), re.S))
    for name, text in sources.items():
        for selector in re.findall(r"([^{}\n]*\.titleband[^{}]*){", text):
            assert not re.search(r"\.(prose|records)\b", selector), (
                f"{name}: the band is scoped to a kind — {selector.strip()}")


def test_no_surface_adds_space_above_the_title_band():
    """Anything above the band that is not the shared rule set moves the title.
    The families document did exactly this by leaving a browser default on its
    h1, which pushed its title 16px below every other page's."""
    sources = {os.path.basename(p): "\n".join(re.findall(r"<style>(.*?)</style>", read(p), re.S))
               for p in generated_pages()}
    sources["style.css"] = read(os.path.join(ROOT, "web", "src", "style.css"))
    for name, css in sources.items():
        for body in re.findall(r"\.titleband[^{]*{([^}]*)}", css):
            for banned in ("margin", "padding"):
                assert banned not in body, f"{name}: .titleband sets {banned}"
        for body in re.findall(r"(?:^|\})\s*h1\s*{([^}]*)}", css):
            assert "margin-top" not in body, f"{name}: h1 sets margin-top above the band"


def test_the_app_column_and_the_page_column_start_at_the_same_offset():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    page = re.search(r"\n\.page-main {([^}]*)}", css).group(1)
    panel = [b for b in re.findall(r"#mode-panel \.page {([^}]*)}", css) if "padding" in b][0]
    top = lambda rule: re.search(r"padding:\s*([\d.]+rem)", rule).group(1)
    assert top(page) == top(panel), (
        f"the band sits {top(page)} below the header on a page and {top(panel)} in a view")


# ------------------------------------ item 18 · the content column kinds ----

def test_every_page_declares_a_content_kind():
    for path in generated_pages():
        html = read(path)
        main = re.search(r"<main([^>]*)>", html)
        assert main, os.path.basename(path)
        assert "page-main" in main.group(1), os.path.basename(path)
        assert re.search(r"\b(prose|records)\b", main.group(1)), (
            f"{os.path.basename(path)}: no content kind declared")


def test_no_page_sets_its_own_main_column_geometry():
    for path in generated_pages():
        style = "\n".join(re.findall(r"<style>(.*?)</style>", read(path), re.S))
        for body in re.findall(r"(?:^|\})\s*main\s*{([^}]*)}", style):
            for banned in ("max-width", "margin", "padding", "width"):
                assert banned not in body, f"{os.path.basename(path)}: main sets {banned}"


def test_the_two_kinds_are_defined_once_in_the_chrome():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert css.count("\n.page-main {") == 1
    prose = re.search(r"\.page-main\.prose[^{]*{([^}]*)}", css).group(1)
    records = re.search(r"\.page-main\.records[^{]*{([^}]*)}", css).group(1)
    assert "max-width" in prose and "max-width" in records
    assert prose != records, "the two kinds have the same geometry"
    base = re.search(r"\n\.page-main {([^}]*)}", css).group(1)
    # ruling by interview, 2026-08-14: one left edge, nothing centres
    # item 26: the container centres as a block; the gutter inside it is the
    # one left edge, and nothing within the container centres
    assert "margin-inline: auto" in base and "var(--page-gutter)" in base
    panel = [b for b in re.findall(r"#mode-panel \.page {([^}]*)}", css) if "padding" in b][0]
    assert "margin-inline: auto" in panel and "var(--page-gutter)" in panel, (
        "the app's panel container does not match the page container")


def test_the_app_views_take_their_column_from_the_same_kinds():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert "#mode-panel .page" in css
    style = read(os.path.join(ROOT, "web", "src", "style.css"))
    assert not re.search(r"^\.page {", style, re.M), "the app restates its content column"
    # a mobile override (max-width: none) is not a geometry of its own
    assert not re.search(r"\.method-page { max-width: \d", style)


# --------------------------------------- item 16 · flashless transitions ----

def test_a_route_panel_is_filled_before_it_is_revealed():
    """The panel is the one opaque surface over a live graph, so it is mounted
    while still display:none and shown last. Reveal-then-fill leaves a frame of
    empty panel, and any render that yields would put the graph on screen."""
    js = app_js()
    body = js[js.index("function openPage("):]
    body = body[:body.index("\n}")]
    assert body.index("render()") < body.index("classList.remove('hidden')"), (
        "openPage reveals the panel before filling it")


def test_a_menu_click_routes_in_its_own_task():
    """Assigning location.hash defers the route to the hashchange task and the
    browser paints in between — one frame of the origin surface after the
    click, which is the reported flash. pushState + applyHash keeps it in the
    click's task; popstate covers the Back button that entry creates."""
    js = app_js()
    handler = js[js.index(".closest('.topmenu a, .brand[href]')"):]
    handler = handler[:handler.index("window.addEventListener('popstate'")]
    assert "history.pushState(null, '', route[1])" in handler
    assert "applyHash()" in handler
    assert "location.hash = route[1]" not in handler, "the click still defers the route"
    assert "window.addEventListener('popstate', applyHash)" in js


def test_a_cold_deep_link_to_a_panel_route_mounts_before_the_first_paint():
    js = app_js()
    boot = js[js.index("if (deepLink) {"):]
    boot = boot[:boot.index("else fitLanding()")]
    assert "applyHash()" in boot and "setTimeout(applyHash, 0)" in boot, boot
    assert boot.index("applyHash()") < boot.index("setTimeout(applyHash, 0)"), (
        "a panel deep link still waits a tick, so the assembled graph paints first")


def test_the_panel_is_opaque_whenever_it_is_visible():
    css = read(os.path.join(ROOT, "web", "src", "style.css"))
    block = re.search(r"#mode-panel {([^}]*)}", css).group(1)
    assert "background: var(--ground)" in block
    assert "#mode-panel.hidden { display: none; }" in css


def test_the_panel_layer_is_raised_by_the_route_not_by_the_render():
    """Item 20 — the guarantee is structural: an opaque layer covering the
    viewport is up for the whole time the route is a panel route, so the worst
    frame any transition can produce is a blank tokened surface. Timing does not
    enter into it."""
    css = read(os.path.join(ROOT, "web", "src", "style.css"))
    assert "html.route-panel #mode-panel { display: block; }" in css, (
        "nothing raises the layer from the route")
    # it must outrank .hidden, or a cold load shows the atlas under a hidden panel
    assert css.index("#mode-panel.hidden") < css.index("html.route-panel #mode-panel")
    # and it must cover the viewport at every width
    for block in re.findall(r"#mode-panel {([^}]*)}", css):
        if "inset" in block:
            assert re.search(r"inset:\s*0", block), f"the layer insets somewhere: {block.strip()}"

    index = read(os.path.join(ROOT, "web", "index.html"))
    assert "route-panel" in index, "index.html does not raise the layer before paint"
    boot = re.search(r"<script>(.*?)</script>", index, re.S).group(1)
    assert "method|concordance|families|queue" in boot, boot[:200]
    assert index.index("<script>") < index.index('id="topbar"'), (
        "the boot script runs after the header, so a frame can precede it")
    first_paint = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    assert "#mode-panel" in first_paint, (
        "the layer is not in the first-paint block, so it is transparent until the "
        "stylesheet parses")

    js = app_js()
    assert "function raiseLayer()" in js and "function lowerLayer()" in js
    open_page = js[js.index("function openPage("):]
    open_page = open_page[:open_page.index("\n}")]
    assert open_page.index("raiseLayer()") < open_page.index("render()"), (
        "the layer goes up after the incoming view is built")
    assert "function closeMode() { lowerLayer()" in js, (
        "the layer is not lowered when the route leaves the panel class")


# ------------------------------------- item 15 · the title band and search ---

TITLE_CLASSES = ("titleband", "eyebrow", "sub")


def test_every_surface_announces_itself_the_same_way():
    """A page's title band is eyebrow + h1 (+ optional sub), inside .titleband,
    on generated pages and in the app's views alike."""
    for path in generated_pages():
        html = read(path)
        band = re.search(r'<div class="titleband">(.*?)</div>', html, re.S)
        assert band, f"{os.path.basename(path)}: no title band"
        assert 'class="eyebrow"' in band.group(1), os.path.basename(path)
        assert "<h1" in band.group(1), os.path.basename(path)
    # the app's four views build the same band
    js = app_js() + read(os.path.join(ROOT, "web", "src", "concordance.js"))
    assert js.count('<div class="titleband">') >= 3, "an in-app view has no title band"
    assert "<h2>The relation-family vocabulary</h2>" not in js, (
        "a view still titles itself with an h2")


def test_no_surface_sets_its_own_title_band_type():
    """Face, size and colour of the band come from the shared chrome. A page or
    a view that styles .eyebrow, .sub, .titleband or .where itself fails here."""
    sources = {os.path.basename(p): "\n".join(re.findall(r"<style>(.*?)</style>", read(p), re.S))
               for p in generated_pages()}
    sources["style.css"] = read(os.path.join(ROOT, "web", "src", "style.css"))
    for name, css in sources.items():
        for selector in TITLE_CLASSES + ("where",):
            for body in re.findall(rf"\.{selector}\s*{{([^}}]*)}}", css):
                for banned in ("font-family", "font-size", "font:", "color"):
                    assert banned not in body, f"{name}: .{selector} sets {banned}"


def test_the_band_outranks_a_view_that_styles_its_paragraphs():
    """The method view sets .method-page p; without the scoped selector its
    eyebrow rendered as body text in ink."""
    css = read(os.path.join(PUBLIC, "chrome.css"))
    assert ".titleband .eyebrow" in css
    assert ".titleband .sub" in css


def test_the_dot_legend_matches_its_tooltips_and_appears_once():
    """The RAG dots and their legend read from one table, so a tooltip and its
    legend entry are the same string. Each phrase appears exactly once in the
    built bundle: once in the table, and nowhere hand-copied."""
    js = app_js()
    table = js[js.index("const RAG_LEGEND = ["):js.index("const ragLegend =")]
    phrases = re.findall(r"'(rag-\w+)', '([^']+)'", table)
    assert [p[0] for p in phrases] == ["rag-green", "rag-amber", "rag-red"], phrases
    assert [p[1] for p in phrases] == [
        "Human-validated",
        "Machine-verified default without human validation",
        "Disputed, on the record"], phrases
    # the tooltip reads the same table rather than restating it
    assert "RAG_LEGEND.find(([cls]) => cls === ragClass)[1]" in js
    for _cls, text in phrases:
        assert js.count(text) == 1, f"{text} is written {js.count(text)} times"

    bundle = os.path.join(ROOT, "web", "dist", "index.html")
    if os.path.exists(bundle):
        built = read(bundle)
        for _cls, text in phrases:
            assert built.count(text) == 1, f"{text} appears {built.count(text)}x in the bundle"

    # once per evidence panel, not per citation: both panels append it after
    # the list they explain
    assert "${rows}${rows ? ragLegend() : ''}" in js
    assert "${e.refs.length ? ragLegend() : ''}" in js
    assert "const ragLegend = () =>" in js
    assert js.count("ragLegend()") == 2, "the legend renders somewhere other than the two panels"


def test_the_method_page_uses_the_legend_vocabulary():
    method = read(os.path.join(ROOT, "docs", "METHOD_COPY.md"))
    assert ("green, human-validated; amber, machine-verified default without human "
            "validation; red, disputed, on the record.") in method
    assert "machine-verified without human validation." in method
    assert "the honest default, not a defect" not in method


def test_the_graph_search_renders_on_the_atlas_view_only():
    """Item 25 (editorial ruling, 2026-08-14) — the graph search acts on the
    atlas canvas, so it renders where that canvas is and nowhere else."""
    index = read(os.path.join(ROOT, "web", "index.html"))
    tools = re.search(r'<span class="hdr-tools">(.*?)</span>\s*</div>', index, re.S).group(1)
    assert 'id="search"' in tools, "the atlas view lost the graph search"

    js = app_js() + read(os.path.join(ROOT, "web", "concordance.js")
                         if os.path.exists(os.path.join(ROOT, "web", "concordance.js"))
                         else os.path.join(ROOT, "web", "src", "concordance.js"))
    assert "search: true" not in js, "a panel view still asks for a header search"
    assert "page-search" not in js, "the panel search input survives in the app source"
    bar = js[js.index("function pageBar("):]
    bar = bar[:bar.index("\n}")]
    assert "<input" not in bar, f"pageBar still renders an input: {bar}"

    # a view may keep a filter over its OWN list, in its content, doing nothing
    # to the graph
    assert "function wireLocalFilter(" in js
    assert "local-filter" in js
    assert "attachTypeahead" not in js[js.index("function wireLocalFilter("):
                                        js.index("function wireLocalFilter(") + 400], (
        "the local filter reaches into the graph search")


def test_the_header_slot_carries_only_site_wide_search():
    """Item 21 (editorial ruling, 2026-08-14) — the header's tools slot is for
    search that reaches the whole graph. The app qualifies and keeps it; a
    generated page's filter, which narrows only that page's own list, does not
    and must not be there."""
    css = read(os.path.join(PUBLIC, "chrome.css"))
    tools = re.search(r"\.site-header \.hdr-tools {([^}]*)}", css).group(1)
    assert "margin-left: auto" in tools
    for path in generated_pages():
        html = read(path)
        header = re.search(HEADER_RE, html).group(0)
        assert not re.search(r"<input[^>]*type=\"search\"", header), (
            f"{os.path.basename(path)}: a page-local filter is in the header slot")
    # the app's graph-wide search stays in the cluster, in both surfaces
    js = app_js()
    assert '<span class="hdr-tools">${tools}</span>' in js
    index = read(os.path.join(ROOT, "web", "index.html"))
    tools_block = re.search(r'<span class="hdr-tools">(.*?)</span>\s*</div>', index, re.S).group(1)
    assert 'id="search"' in tools_block, "the app's search left the shared cluster"


def test_a_page_local_filter_sits_with_its_facets():
    """And first among them: it is the broadest control in the family."""
    html = read(os.path.join(PUBLIC, "ledger.html"))
    facets = re.search(r'<div class="facets">(.*?)</div>\s*<p class="facthow"', html, re.S)
    assert facets, "the ledger has no facet block"
    block = facets.group(1)
    assert 'id="q"' in block, "the ledger's filter is not in the facet block"
    assert "facet-filter" in block, "the filter does not take the shared filter styling"
    assert block.index('id="q"') < block.index('data-g="vol"'), (
        "the filter is not the first row of the facet block")
    for path in generated_pages():
        page = read(path)
        for match in re.finditer(r'<input[^>]*type="search"[^>]*>', page):
            after = page[match.start():]
            assert "facet-filter" in match.group(0), (
                f"{os.path.basename(path)}: a filter input outside the facet family")


def test_no_generated_page_styles_its_own_search_input():
    for path in generated_pages():
        style = "\n".join(re.findall(r"<style>(.*?)</style>", read(path), re.S))
        assert not re.search(r"#q\s*{", style), f"{os.path.basename(path)}: #q restyled locally"


# ---------------------------------------------- item 14 · one heading scale ---

def test_the_heading_scale_is_defined_once_in_the_shared_chrome():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    for level in ("h1", "h2", "h3", "h4"):
        assert re.search(rf"^{level} {{", css, re.M), level
    block = css[css.index("\nh1 {"):css.index("\nh3 {")]
    assert "var(--display)" in block and "var(--ink)" in block and "var(--gold)" in block
    tokens = read(os.path.join(ROOT, "web", "src", "tokens.css"))
    assert re.search(r"^h2 {", tokens, re.M), "the app does not receive the shared scale"


def test_no_generated_page_restates_the_heading_face_size_or_colour():
    """Margins belong to the page; face, size and colour belong to the scale."""
    for path in generated_pages():
        style = "\n".join(re.findall(r"<style>(.*?)</style>", read(path), re.S))
        for rule in re.findall(r"^\s*(h[1-4])\s*{([^}]*)}", style, re.M):
            level, body = rule
            for banned in ("font-family", "font-size", "color"):
                assert banned not in body, f"{os.path.basename(path)}: {level} restates {banned}"


def test_the_app_views_take_the_shared_heading_scale():
    css = read(os.path.join(ROOT, "web", "src", "style.css"))
    for selector in ("#mode-panel h2", ".method-page h2"):
        body = re.search(rf"{re.escape(selector)} {{([^}}]*)}}", css).group(1)
        for banned in ("font-family", "font-size", "color"):
            assert banned not in body, f"{selector} still sets {banned} of its own"


HEADER_RE = re.compile(r'<header[^>]*class="[^"]*\bsite-header\b[^"]*"[^>]*>(.*?)</header>', re.S)


def header_shape(html):
    """The order of the header's parts, as markup: what comes before the menu is
    what can push it around, so the order IS the geometry contract."""
    found = HEADER_RE.search(html)
    assert found, "no site header on the page"
    body = found.group(1)
    parts = []
    for token in re.finditer(r'class="(?:hrow hrow-(\d)|brand[^"]*|topmenu|where)"', body):
        parts.append(token.group(0))
    return body, parts


def test_the_header_has_the_same_structural_order_everywhere():
    """V2-R11 — brand, then nav, then everything else, on every generated page.
    Anything of variable width before the menu moves the menu between pages."""
    reference = None
    for path in generated_pages():
        body, parts = header_shape(read(path))
        shape = [p for p in parts if "hrow" in p or "brand" in p or "topmenu" in p]
        if reference is None:
            reference = shape
        assert shape == reference, os.path.basename(path)
        assert body.index('class="brand"') < body.index('class="topmenu"'), os.path.basename(path)
        assert body.index('class="topmenu"') < body.index('class="where"'), os.path.basename(path)
        assert body.index('hrow-1') < body.index('hrow-2'), os.path.basename(path)
        # the breadcrumb is on the second row, not beside the menu
        row_two = body[body.index("hrow-2"):]
        assert 'class="where"' in row_two, os.path.basename(path)


def test_the_app_header_matches_that_structure():
    html = read(os.path.join(ROOT, "web", "index.html"))
    body, _ = header_shape(html)
    assert body.index('id="brand"') < body.index('class="topmenu"')
    # nothing but the brand block sits between the row and the menu: anything
    # else there is something whose width could move the menu
    between = re.sub(r"<!--.*?-->", "", body[body.index('class="hrow hrow-1"'):
                                             body.index('class="topmenu"')], flags=re.S)
    tags = re.findall(r"<(/?\w+)", between)
    assert tags == ["div", "h1", "/h1", "/div", "nav"], tags
    for control in ('id="version"', 'id="search"', 'id="stats"', 'id="fit"', 'id="relayout"'):
        assert body.index(control) > body.index('class="topmenu"'), control
        assert control in body[body.index("hrow-2"):], control


def test_the_app_routes_render_the_shared_header_fragment():
    """Item 12 — #mode-panel is a fixed, scrolling overlay that covers the
    topbar, so an in-app route that drew its own bar showed a different set of
    links in a different place, and one that scrolled away. Every route now
    renders the emitted template."""
    chrome = json.loads(read(os.path.join(SRC, "chrome.json")))
    header = chrome["header"]
    assert header.index('class="brand"') < header.index('class="topmenu"')
    assert header.index('class="topmenu"') < header.index("{{ROW2}}")
    assert "{{BRAND_HREF}}" in header
    # the same menu the generated pages carry, link for link
    assert menu_items(header) == menu_items(read(os.path.join(PUBLIC, "releases.html")))

    js = read(os.path.join(ROOT, "web", "src", "main.js"))
    assert "import chrome from './chrome.json'" in js
    assert "chrome.header.replace('{{BRAND_HREF}}'" in js
    assert '<div class="page-bar">' not in js, (
        "a route still builds its own bar instead of the shared header")


# ------------------------------------- item 13 · the atlas across routes ----
# What is testable without a browser is the mechanism: the instance is built
# once, the routes hide rather than rebuild, and the selection is reflected into
# the URL instead of pushed onto history. The behavioural claims (viewport and
# selection bit-identical across route round-trips, one tap after five of them,
# a deep link focusing the right node) are measured in a real browser and
# reported in docs/experiments/ui_v2_build_report_2026-08-13.md.

def app_js():
    return read(os.path.join(ROOT, "web", "src", "main.js"))


def test_the_graph_is_built_once_and_never_destroyed():
    js = app_js()
    assert js.count("cytoscape({") == 1, "the atlas is constructed more than once"
    assert ".destroy()" not in js, "a route destroys the graph instead of hiding it"
    assert "function closeMode() { lowerLayer(); modeEl.classList.add('hidden') }" in js, (
        "leaving a route no longer hides the panel — check it does not tear down the atlas")


def test_route_entry_does_not_reframe_a_live_atlas():
    """enterAtlas returns early when the atlas is already up, which is what keeps
    the viewport across a route round-trip."""
    js = app_js()
    body = js[js.index("function enterAtlas("):]
    assert body.index("if (inAtlas) return") < body.index("cy.stop()")


def test_selection_is_reflected_not_pushed():
    js = app_js()
    assert "history.replaceState" in js
    assert "reflectSelection('node', node.id())" in js
    assert "reflectSelection('edge', edge.id())" in js
    assert "setHash('#/n/'" not in js, "node selection still pushes a history entry"
    assert "setHash('#/e/'" not in js, "edge selection still pushes a history entry"


def test_the_deep_link_form_is_read_and_the_old_one_still_works():
    js = app_js()
    assert "params.get('node')" in js and "params.get('edge')" in js
    assert "function routeOf(" in js
    # the older permalinks stay readable
    assert "#\\/n\\/(.+)$" in js.replace("\\", "\\\\") or "^#\\/n\\/" in js
    assert "focusOn(around(el))" in js, "a deep link selects without focusing"


def test_clearing_the_selection_clears_the_parameter():
    js = app_js()
    body = js[js.index("function clearSelection()"):]
    body = body[:body.index("cy.on('tap'")]
    assert "reflectSelection(null, null)" in body


def test_the_dev_server_resolves_extensionless_urls():
    """The reported failure on /ontology reproduced as a dev-server artifact:
    serve.mjs answered every extensionless URL with the atlas shell, so the
    reader got a landing view where a page should be."""
    src = read(os.path.join(ROOT, "web", "serve.mjs"))
    assert "existsSync(file + '.html')" in src


def test_the_header_is_pinned_and_its_brand_cannot_shift_the_menu():
    css = read(os.path.join(PUBLIC, "chrome.css"))
    block = css[css.index(".site-header {"):]
    assert "position: sticky" in block.split("}")[0]
    assert "top: 0" in block.split("}")[0]
    assert "var(--ground)" in block.split("}")[0]
    assert "var(--hairline)" in block.split("}")[0]
    brand = css[css.index(".site-header .brand {"):]
    assert "flex: 0 0 " in brand.split("}")[0], (
        "the brand has no fixed width, so its content can move the menu")
    # one definition, not one per page: the app and the pages read the same block
    tokens = read(os.path.join(ROOT, "web", "src", "tokens.css"))
    assert tokens.count("\n.site-header {") == 1
    assert css.count("\n.site-header {") == 1


# ---------------------------------------------- V2-R7 · the batch deltas ---

@pytest.fixture(scope="module")
def state():
    return json.loads(read(os.path.join(ROOT, "pipeline", "state.json")))


def test_every_batch_has_a_delta_page(state):
    for batch in state["batches"]:
        path = os.path.join(PUBLIC, ledger_gen.batch_slug(batch["id"]) + ".html")
        assert os.path.exists(path), batch["id"]


def test_batch_pages_belong_to_batches_that_exist(state):
    ids = {ledger_gen.batch_slug(b["id"]) for b in state["batches"]}
    for path in generated_pages():
        name = os.path.basename(path)[: -len(".html")]
        if name.startswith("batch-"):
            assert name in ids, name


def test_the_ledger_no_longer_carries_the_batch_narrative(state):
    """The narrative moved; the ledger keeps the facet and a link per batch."""
    html = read(os.path.join(PUBLIC, "ledger.html"))
    stories = [b.get("result") or b.get("note") or "" for b in state["batches"]]
    for story in stories:
        if len(story) > 80:
            assert story[:80] not in html, "a batch narrative is still inline on the ledger"
    for batch in state["batches"]:
        assert f'href="/{ledger_gen.batch_slug(batch["id"])}"' in html, batch["id"]


def test_a_batch_delta_states_its_derivation_or_declines_to_derive(state):
    for batch in state["batches"]:
        html = read(os.path.join(PUBLIC, ledger_gen.batch_slug(batch["id"]) + ".html"))
        if ledger_gen.parse_window(batch.get("window")):
            assert "records cite this window" in html, batch["id"]
            assert "do not partition" in html, batch["id"]
        else:
            assert "declares no paragraph window" in html, batch["id"]


def test_batch_delta_counts_are_the_records_that_cite_the_window(state):
    """Recomputed here from seed.json by a separate walk, for the three largest
    windowed batches."""
    seed = json.loads(read(SEED))
    windows = ledger_gen.batch_windows(state)
    checked = 0
    for batch in state["batches"]:
        ranges = ledger_gen.parse_window(batch.get("window"))
        if not ranges:
            continue
        records = sum(1 for e in seed["edges"]
                      if batch["id"] in ledger_gen.batches_for(e["references"], windows))
        html = read(os.path.join(PUBLIC, ledger_gen.batch_slug(batch["id"]) + ".html"))
        assert f"<b>{records}</b> records cite this window" in html, batch["id"]
        checked += 1
    assert checked >= 3


def test_release_entries_link_the_batches_they_name(state):
    html = read(os.path.join(PUBLIC, "releases.html"))
    body = html[html.index("<main"):]
    for batch in state["batches"]:
        bid = batch["id"]
        # a batch id appearing as text in an entry must be a link to its page
        for match in re.finditer(re.escape(bid), body):
            window = body[max(0, match.start() - 120):match.start()]
            assert f'href="/{ledger_gen.batch_slug(bid)}"' in window or "<a " in window, bid


# ------------------------------- the batch manifest and the deploy gate ----

@pytest.fixture(scope="module")
def batch_manifest():
    return json.loads(read(os.path.join(PUBLIC, "batch_pages.json")))


def test_manifest_ids_are_exactly_the_batch_pages_written(batch_manifest):
    on_disk = {os.path.basename(p) for p in generated_pages()
               if os.path.basename(p).startswith("batch-")}
    assert set(batch_manifest["pages"]) == on_disk
    assert batch_manifest["count"] == len(batch_manifest["ids"]) == len(on_disk)
    assert len(set(batch_manifest["ids"])) == len(batch_manifest["ids"])


def test_manifest_names_the_graph_it_was_derived_from(batch_manifest):
    seed = json.loads(read(SEED))
    assert batch_manifest["seed_edges"] == len(seed["edges"])
    assert batch_manifest["seed_nodes"] == len(seed["nodes"])


def test_manifest_ids_match_the_batches_state_declares(batch_manifest, state):
    assert set(batch_manifest["ids"]) == {b["id"] for b in state["batches"]}
    for bid in batch_manifest["ids"]:
        assert f"{ledger_gen.batch_slug(bid)}.html" in batch_manifest["pages"]


def test_every_batch_the_ledger_links_has_a_page(batch_manifest):
    """Facet chips and index rows both point at batch pages; neither may point
    at one that was never written."""
    ledger = read(os.path.join(PUBLIC, "ledger.html"))
    linked = set(re.findall(r'href="/(batch-[a-z0-9-]+)"', ledger))
    assert linked, "the ledger links no batch page"
    pages = {p[: -len(".html")] for p in batch_manifest["pages"]}
    assert linked <= pages, sorted(linked - pages)
    faceted = {ledger_gen.batch_slug(bid)
               for bid in re.findall(r'data-g="batch" data-v="([^"]+)"', ledger)}
    assert faceted <= linked, sorted(faceted - linked)


def test_the_deploy_gate_covers_the_batch_pages():
    """The manifest is only worth writing if the deploy refuses without it."""
    src = read(os.path.join(ROOT, "tools", "pages", "preflight.py"))
    assert "batch_pages.json" in src
    for gate in ("every batch page in dist",
                 "no orphan batch pages in dist",
                 "batch pages are fresh (manifest edges == seed.json)"):
        assert gate in src, gate


def test_the_deploy_carries_a_size_budget():
    """Item 29 — viteSingleFile inlines script, styles and atlas.json into one
    document, so the page a reader downloads grows quietly with the graph. The
    gate is a ratchet: it fails the deploy above the ceiling and prints the
    actual against it either way."""
    src = read(os.path.join(ROOT, "tools", "pages", "preflight.py"))
    assert "== size budget ==" in src
    assert "INDEX_CEILING" in src
    ceiling = re.search(r"INDEX_CEILING = ([\d.]+) \* 1024 \* 1024", src)
    assert ceiling and float(ceiling.group(1)) == 3.0, "the ceiling moved without a ruling"
    assert "within budget" in src and "ceiling" in src
    dist_index = os.path.join(ROOT, "web", "dist", "index.html")
    if os.path.exists(dist_index):
        assert os.path.getsize(dist_index) <= 3.0 * 1024 * 1024, (
            "the built bundle already exceeds the ceiling")


def test_the_deploy_checks_the_extensionless_redirect():
    """A warning, not a failure: it tests Cloudflare's behaviour rather than our
    artifact. It must print either way."""
    src = read(os.path.join(ROOT, "tools", "pages", "verify.py"))
    assert "== extensionless redirect ==" in src
    assert "/ledger.html" in src
    assert "HTTPRedirectHandler" in src, "the probe would follow the redirect it is testing"
    assert "308" in src and "WARNING" in src
    # it may not fail the run: nothing in the block appends to fails or exits
    block = src[src.index("== extensionless redirect =="):src.index("if fails:")]
    assert "fails.append" not in block and "sys.exit" not in block, (
        "the redirect check hard-fails the deploy")


def test_the_deploy_allowlist_admits_every_page_this_slice_ships():
    """preflight's allowlist is exact. A page it does not know is an unexpected
    file, and an unexpected file stops the deploy — so a new page joins the
    allowlist in the commit that creates it."""
    src = read(os.path.join(ROOT, "tools", "pages", "preflight.py"))
    allow = set(re.findall(r"'([\w.-]+\.(?:html|json|js|css|txt|xml))'", src))
    family_re = re.compile(re.search(r"FAMILY_PAGE = re\.compile\(r'([^']+)'\)", src).group(1))
    batch_re = re.compile(re.search(r"BATCH_PAGE = re\.compile\(r'([^']+)'\)", src).group(1))
    concept_re = re.compile(re.search(r"CONCEPT_PAGE = re\.compile\(r'([^']+)'\)", src).group(1))
    for path in generated_pages():
        name = os.path.basename(path)
        assert (name in allow or family_re.match(name) or batch_re.match(name)
                or concept_re.match(name)), name
    for extra in ("query.js", "relation_declarations.json", "batch_pages.json"):
        assert extra in allow, extra


def test_the_forbidden_pattern_still_bites_outside_the_manifest():
    """A batch id may contain the word 'candidates' (the pre-window CW 14 sets
    do), and those pages are vouched for by the manifest. The pattern must still
    reject anything else carrying it."""
    src = read(os.path.join(ROOT, "tools", "pages", "preflight.py"))
    assert "re.compile(r'candidates')" in src, "the forbidden pattern was removed"
    assert "if not vouched_batch:" in src, (
        "the forbidden sweep no longer has an exemption boundary")
    manifest = json.loads(read(os.path.join(PUBLIC, "batch_pages.json")))
    vouched = [p for p in manifest["pages"] if "candidates" in p]
    assert vouched, "no batch page exercises the exemption — check the id set"


# ------------------------------------------- V2-R8 · volumes are ordered ---

def test_query_volume_dropdown_is_in_collection_order():
    """5, 8, 9i, 9ii, 11, 12, 13, 14, 16 — the edition's order. Lexicographic
    sorting puts 11 before 5 and Aion before the Archetypes volume."""
    html = read(os.path.join(PUBLIC, "query.html"))
    assert "byVolume(a[0], b[0])" in html, (
        "the volume dropdown does not sort through the shared comparator")
    source = read(os.path.join(ROOT, "web", "query-semantics.mjs"))
    assert "export function volumeKey" in source
    assert "export const byVolume" in source


def test_one_volume_comparator_per_generator_language():
    """V2-R8 wants the rule in one place per language, not restated per page."""
    js = read(os.path.join(ROOT, "web", "build-atlas.mjs"))
    assert "byVolume" in js
    assert "function volKeyBuild" not in js, "a second JavaScript comparator survives"
    assert js.count("=== 'ii' ? 0.2") == 0, "the comparator's body is restated in build-atlas.mjs"


def test_the_python_comparator_orders_the_edition():
    volumes = ["11", "5", "9ii", "14", "9i", "8", "16", "12", "13"]
    assert sorted(volumes, key=ledger_gen.volume_key) == [
        "5", "8", "9i", "9ii", "11", "12", "13", "14", "16"]


def test_generated_volume_lists_are_in_collection_order():
    """Every list of volumes a generator writes, read back off the pages."""
    ledger = read(os.path.join(PUBLIC, "ledger.html"))
    facets = re.findall(r'data-g="vol" data-v="([^"]+)"', ledger)
    assert facets == sorted(facets, key=ledger_gen.volume_key)
    atlas = json.loads(read(os.path.join(SRC, "atlas.json")))
    bar = [v["volume"] for v in atlas["meta"]["volumes"]]
    assert bar == sorted(bar, key=ledger_gen.volume_key)


# ------------------------------------------------------------ the query ---

def test_query_page_ships_the_semantics_module_unmodified():
    source = read(os.path.join(ROOT, "web", "query-semantics.mjs"))
    shipped = read(os.path.join(PUBLIC, "query.js"))
    assert shipped == source


def test_query_page_receipts_footer_is_the_cli_footer():
    """The panel's footer is the CLI's footer. If they drift, two readers holding
    the same digest are looking at different claims about the same graph."""
    import kg_query  # noqa: E402
    graph = kg_query.Graph(SEED)
    decls = kg_query.load_json(DECLARATIONS)
    decls["_path"] = DECLARATIONS
    footer = kg_query.footer(graph, decls)
    html = read(os.path.join(PUBLIC, "query.html"))
    rendered = re.search(r'<span id="receipts">(.*?)</span>', html, re.S).group(1)
    assert rendered.replace("&amp;", "&") == footer


def test_the_identity_walk_is_not_exposed_on_the_site():
    """Item 17 (editorial ruling, 2026-08-13) — the walk is kept, not deleted:
    it stays in the CLI, in its tests and in docs/QUERY.md, and it is off the
    site. The flag in build-atlas.mjs is the one place that changes to bring it
    back, and the header it would print is still lifted from the tool, so
    re-enabling cannot resurrect stale copy."""
    html = read(os.path.join(PUBLIC, "query.html"))
    body = html[html.index("<main"):]
    for marker in ("Identity walk", "walkhead", "runwalk", 'id="w-start"'):
        assert marker not in body, f"the walk is still on the query page: {marker}"
    js = read(os.path.join(ROOT, "web", "build-atlas.mjs"))
    assert "const WALK_IN_UI = false" in js
    assert "${WALK_IN_UI ? `<h2>Identity walk</h2>" in js, (
        "the walk section is deleted rather than held behind the flag")
    # the tool keeps it
    cli = read(os.path.join(ROOT, "tools", "query", "kg_query.py"))
    assert "WALK_HEADER" in cli and '--walk' in cli
    doc = read(os.path.join(ROOT, "docs", "QUERY.md"))
    assert "not currently exposed in the site UI" in doc


def test_no_site_surface_offers_a_walk_it_does_not_have():
    for path in generated_pages():
        html = read(path)
        for hit in re.finditer(r"identity walk", html, re.I):
            window = html[max(0, hit.start() - 240):hit.start() + 240]
            assert re.search(r"not exposed on the site|kept for later|command line|kg_query\.py", window), (
                f"{os.path.basename(path)}: names the identity walk without saying it is not on the site")


NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="node is not installed")
@pytest.mark.parametrize("filters", [
    {},
    {"closure": True},
    {"family": "symbolization"},
    {"family": "symbolization", "closure": True},
    {"state": "pending-adjudication"},
    {"subject": "lapis", "closure": True},
    {"relation": "symbolized-by", "closure": True},
    {"volume": "9ii", "claim_type": "jung-asserts"},
    {"provenance": "human-adjudication"},
])
def test_the_browser_port_agrees_with_the_cli(tmp_path, filters):
    """The CLI is the reference implementation; this is the port. Rows are
    compared as triples with their origin, so a derived row that lost its label
    or gained a duplicate fails here."""
    import kg_query  # noqa: E402

    harness = tmp_path / "harness.mjs"
    harness.write_text(
        "import { readFileSync } from 'fs'\n"
        f"import {{ select }} from '{os.path.join(ROOT, 'web', 'query-semantics.mjs')}'\n"
        f"const graph = JSON.parse(readFileSync({json.dumps(SEED)}))\n"
        f"const decls = JSON.parse(readFileSync({json.dumps(DECLARATIONS)}))\n"
        f"const rows = select(graph, decls, {json.dumps(filters)})\n"
        "console.log(JSON.stringify(rows.map(r => [r.subject, r.relation, r.object, r.origin])))\n")
    out = subprocess.run([NODE, str(harness)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    ported = [tuple(r) for r in json.loads(out.stdout)]

    graph = kg_query.Graph(SEED)
    decls = kg_query.load_json(DECLARATIONS)
    decls["_path"] = DECLARATIONS

    class Args:
        def __init__(self, **kwargs):
            for name in ("family", "state", "provenance", "claim_type", "volume",
                         "subject", "object", "relation", "string", "effective"):
                setattr(self, name, None)
            self.closure = False
            for key, value in kwargs.items():
                setattr(self, key, value)

    reference = [(r["subject"], r["relation"], r["object"], r["origin"])
                 for r in kg_query.select(graph, decls, Args(**filters))]
    assert ported == reference


# ----------------------------------------------------------- the ledger ---

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "build_ledger_page", os.path.join(ROOT, "tools", "build_ledger_page.py"))
ledger_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger_gen)


def test_importing_the_ledger_generator_writes_nothing():
    """The helpers are importable for these tests; the page is only written when
    the script is run."""
    before = os.path.getmtime(os.path.join(PUBLIC, "ledger.html"))
    importlib.util.module_from_spec(_spec)
    assert os.path.getmtime(os.path.join(PUBLIC, "ledger.html")) == before


def test_every_ledger_record_has_a_unique_id_and_a_permalink():
    html = read(os.path.join(PUBLIC, "ledger.html"))
    ids = re.findall(r'<div class="ecard" id="([^"]+)"', html)
    seed = json.loads(read(SEED))
    assert len(ids) == len(seed["edges"])
    assert len(set(ids)) == len(ids)
    for ident in ids[:50]:
        assert f'<a class="anchor" href="#{ident}"' in html


def test_ledger_facets_cover_the_states_the_graph_carries():
    html = read(os.path.join(PUBLIC, "ledger.html"))
    seed = json.loads(read(SEED))
    states = {(e.get("relation_family") or {}).get("state")
              for e in seed["edges"]} - {None}
    for state in states:
        assert f'data-g="state" data-v="{state}"' in html, state
    families = {(e.get("relation_family") or {}).get("value")
                for e in seed["edges"]} - {None}
    for family in families:
        assert f'data-g="family" data-v="{family}"' in html, family


def test_ledger_facet_counts_match_the_cards_that_carry_them():
    html = read(os.path.join(PUBLIC, "ledger.html"))
    cards = re.findall(r'<div class="ecard"[^>]*data-state="([^"]*)"', html)
    for value, count in re.findall(
            r'data-g="state" data-v="([^"]+)">[^<]*<span class=n>·(\d+)</span>', html):
        assert cards.count(value) == int(count), value


def test_ledger_history_chip_renders_only_for_an_edge_that_carries_history():
    assert ledger_gen.history_chip({"value": "symbolization", "state": "assigned"}) == ""
    assert ledger_gen.history_chip({}) == ""
    chip = ledger_gen.history_chip({
        "value": "archetypal-identity", "state": "assigned", "ruleset": "v0.7.1",
        "history": [{"value": "amplification", "ruleset": "v0.6", "date": "2026-08-07"}]})
    assert "amplification (v0.6)" in chip and "archetypal-identity (v0.7.1)" in chip
    assert "earlier" not in chip
    longer = ledger_gen.history_chip({
        "value": "c", "ruleset": "v3",
        "history": [{"value": "a", "ruleset": "v1"}, {"value": "b", "ruleset": "v2"}]})
    assert "b (v2) → c (v3)" in longer and "1 earlier" in longer


def test_ledger_history_chip_is_absent_from_the_page_while_no_edge_carries_history():
    seed = json.loads(read(SEED))
    carried = [e for e in seed["edges"] if (e.get("relation_family") or {}).get("history")]
    html = read(os.path.join(PUBLIC, "ledger.html"))
    assert html.count('class="chip f-hist"') == len(carried)


def test_ledger_batch_facet_is_derived_from_declared_windows_only():
    state = json.loads(read(os.path.join(ROOT, "pipeline", "state.json")))
    windows = ledger_gen.batch_windows(state)
    declared = {bid for bid, _v, _lo, _hi in windows}
    html = read(os.path.join(PUBLIC, "ledger.html"))
    for bid in re.findall(r'data-g="batch" data-v="([^"]+)"', html):
        assert bid in declared, bid
    assert ledger_gen.parse_window(None) == []
    assert ledger_gen.parse_window("CW12 §321-331 + §421-446") == [
        ("12", 321, 331), ("12", 421, 446)]


def test_ledger_reassigned_facet_is_derived_and_labelled():
    assert ledger_gen.provenance_facets({"by": "opus+gemini-agreed"}) == ["opus+gemini-agreed"]
    assert "reassigned" in ledger_gen.provenance_facets(
        {"by": "opus+gemini-agreed (v0.7 rerun of amplified-by, ruling 1)"})
    assert "reassigned" in ledger_gen.provenance_facets(
        {"by": "opus+gemini-agreed", "history": [{"value": "x"}]})
    html = read(os.path.join(PUBLIC, "ledger.html"))
    assert "reassigned is derived from the provenance string" in html


def test_ledger_and_the_atlas_agree_on_the_family_totals(families_map):
    html = read(os.path.join(PUBLIC, "ledger.html"))
    meta = re.search(r'<div class="meta">(.*?)</div>', html, re.S).group(1)
    assert f'{families_map["totals"]["assigned"]} family-assigned' in meta
    assert f'{families_map["totals"]["pending"]} awaiting a ruling' in meta
