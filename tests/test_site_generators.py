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
    """The pending entry — the one that is not a skeleton. Entries are ordered
    newest first, and the newest is a skeleton, so position is not the test."""
    entry = re.search(r'<section class="rel-entry">(.*?)</section>', html, re.S)
    assert entry, "no pending (non-skeleton) entry on the page"
    return entry.group(1)


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
    """A skeleton is allowed to be a skeleton; the pending entry is not."""
    html = read(os.path.join(PUBLIC, "releases.html"))
    entry = re.search(r'<section class="rel-entry">(.*?)</section>', html, re.S)
    assert entry, "no pending (non-skeleton) entry on the page"
    body = entry.group(1)
    for heading in ("the graph", "ruleset", "instruments and calibration",
                    "checked outside the repository", "corrected or withdrawn"):
        assert f">{heading}<" in body, heading
    assert "clause-predicate" in body, "the defect story is not in the entry"
    assert "form rule" in body
    assert re.search(r"href=\"/batch-b-cw\w+-\d+\"", body), (
        "the entry names no batch that links to its delta page")
    assert len(re.sub(r"<[^>]+>", "", body).split()) > 400, "the entry is thin"


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


def test_the_ontology_page_states_where_its_checks_come_from(qa_json):
    """The scan borrows the OOPS! catalogue's numbering; the page says so, cites
    it, and lists every pitfall code the tool actually uses."""
    html = read(os.path.join(PUBLIC, "ontology.html"))
    section = html[html.index("Where the checks come from"):html.index("<h2>The pitfall scan")]
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
    section = html[html.index("Deliberately absent"):html.index("The pitfall scan")]
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


def test_every_generated_page_carries_the_same_menu():
    reference = None
    for path in generated_pages():
        items = menu_items(read(path))
        if reference is None:
            reference = items
        assert items == reference, os.path.basename(path)
    assert reference, "no generated page carried a menu"
    assert [label for _href, label in reference] == [
        "atlas", "query", "families", "ledger", "releases",
        "ontology", "disputes", "method"]


def test_the_app_carries_the_same_menu_as_the_generated_pages():
    app = menu_items(read(os.path.join(ROOT, "web", "index.html")))
    page = menu_items(read(os.path.join(PUBLIC, "releases.html")))
    assert app == page


def test_both_generator_languages_hold_the_same_menu_list():
    """One list per language; this is what keeps them one menu."""
    js = read(os.path.join(ROOT, "web", "build-atlas.mjs"))
    js_menu = re.findall(r"\['(/[^']*)', '(\w+)'\]", js[js.index("const MENU = ["):])
    assert js_menu[:len(ledger_gen.MENU)] == [tuple(x) for x in ledger_gen.MENU]


def test_the_menu_marks_the_page_it_is_on():
    for slug in ("releases", "query", "ontology", "families", "ledger"):
        html = read(os.path.join(PUBLIC, slug + ".html"))
        current = re.findall(r'<a href="([^"]+)" aria-current="page">', MENU_RE.search(html).group(1))
        assert current == [f"/{slug}"], (slug, current)


def test_the_breadcrumb_keeps_its_place_beside_the_menu():
    """R10.6 — the menu did not displace the breadcrumb."""
    for path in generated_pages():
        html = read(path)
        bar = re.search(r'<div class="page-bar">(.*?)</div>\s*<main', html, re.S)
        assert bar, os.path.basename(path)
        assert '<nav class="topmenu">' in bar.group(1), os.path.basename(path)
        assert 'class="where"' in bar.group(1), os.path.basename(path)
        assert bar.group(1).index("topmenu") < bar.group(1).index('class="where"')


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
    body = html[html.index("<main>"):]
    for batch in state["batches"]:
        bid = batch["id"]
        # a batch id appearing as text in an entry must be a link to its page
        for match in re.finditer(re.escape(bid), body):
            window = body[max(0, match.start() - 120):match.start()]
            assert f'href="/{ledger_gen.batch_slug(bid)}"' in window or "<a " in window, bid


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


def test_query_page_states_the_walks_limits_in_the_tools_own_words():
    import kg_query  # noqa: E402
    html = read(os.path.join(PUBLIC, "query.html"))
    head = re.search(r'<p id="walkhead"[^>]*>(.*?)</p>', html, re.S).group(1)
    expected = " ".join(kg_query.WALK_HEADER.format(
        family=kg_query.IDENTITY_FAMILY).split())
    assert " ".join(head.split()) == expected


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
