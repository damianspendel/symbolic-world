# v2.0 UI slice — build report, 2026-08-13

Spec: `docs/ATLAS_REQUIREMENTS.md`, section "V2 — the v2.0 UI slice" (V2-R1..R6).
Executor: Opus-family session, working in the isolated worktree
`~/Documents/github/JungKG-ui-v2` on branch `ui-v2-dev`.

Base commit: `89ba3b2064b4d585a093c16d6889e2a107ff9aae`.

Nothing was written, staged or committed in the main tree
(`~/Documents/github/JungKG`), which had an active mining session working in it
throughout. Nothing was deployed, pushed, tagged or released. `web/public/v1.3/`
is byte-identical: `git status` reports it untouched.

## Commits

| Commit | What |
|---|---|
| `1e0eb11` | V2-R1 — `/releases` generated from `docs/RELEASES.md`, plus the shared v2.0 page machinery (registry, canonical, sitemap, footer nav, copy-contract hook) |
| `dae2031` | V2-R2 — one page per relation family; `results.json` extended with the report v3 per-family table; families page links each family to its page |
| `479e4a9` | follow-up — page receipts stamp the build date, not the build commit (the commit stamp rewrote 26 pages after every commit) |
| `a049603` | V2-R3 — ledger facets, record permalinks, assignment-history chip |
| `2f239f2` | V2-R4 — `/query`, the kg_query semantics ported and run in the browser |
| `8a562a5` | V2-R5 — `/ontology`, the design, the declarations, and the pitfall scan with a stance per finding; `quality.py --json` |
| `72e1d48` | tests — `tests/test_site_generators.py`, invariants, no pinned counts |
| `5fa18e7` | this report |
| `8c80b40` | determinism — same graph in, same bytes out from both generators |

## What each requirement produced

**V2-R1 · /releases.** `docs/RELEASES.md` created with the v1.4-pending entry and
skeletons for v1.5 and v2.0. The file carries no typed figure: counts are named
tokens bound at build from `seed.json`, the binding calibration record and the
external-validity receipts, and a token the build cannot bind fails the build.
The version pin follows CLAUDE.md's ceremony rule (graph version · ruleset
version · calibration record + verdict); the build refuses to print a pin when no
PASS record exists for the ruleset `FAMILY_DEFINITIONS.md` is currently at. On
this graph the pin reads: graph v1.4 · ruleset v0.7.1 · calibration record
`pipeline/family_calibration/records/2026-08-13_v071_run6.json` (PASS).

**V2-R2 · per-family pages.** 25 pages, one per family in the ruleset, at
`/family-<name>`. Definition and boundary quoted through the same extraction the
families page uses. Family-scoped counts on one line, graph-wide totals on the
next. Relation strings with counts and the size of the tail; seeds; declarations
touching the family's strings; the queued items carrying a string it covers,
labelled as queued rather than as members; the external-validity row inside the
whole table. The build refuses if the per-family counts do not sum to the map's
assigned total. `results.json` gained `per_family`, transcribed row for row from
`external_validity_report_v3.md` with the report's own labels and fraction
strings.

**V2-R3 · faceted ledger.** Facets over volume, batch, claim type, state, family
and provenance; OR within a row, AND across rows, search on top. Counts stay
graph-wide while filtering and the page says so. A `§` permalink per record with
a stable id from subject/relation/object, de-duplicated. The history chip renders
only when an edge carries `relation_family.history` — no edge does yet, so no
chip is drawn, and a unit test exercises the rendering with a synthetic record.
`tools/build_ledger_page.py` now keeps its helpers at module level with the work
behind `build()`, so the tests can import the helpers without generating a page.

**V2-R4 · query panel.** `web/query-semantics.mjs` is a port of
`tools/query/kg_query.py` — row shapes, filters, closure, walk — copied verbatim
to `web/public/query.js` at build. `relation_declarations.json` is emitted into
`web/src` (as specified) and into `web/public` (so the page can fetch it). The
page reads `/graph.json`. Checked against the CLI on this graph: `--subject lapis
--closure` 40 stored + 6 derived in both; identity walk from `mercurius` at depth
2, 41 hops in both; whole-graph closure 200 derived rows over 1555 stored edges
in both. The receipts footer is the CLI's own footer string, and a test asserts
equality. The walk's non-transitivity header is lifted out of `kg_query.py` at
build rather than restated.

**V2-R5 · ontology page.** `quality.py --json` added: same findings, same order,
same messages as the prose mode, plus a `headline` block (hapax share,
sentence-shaped predicates, declared-inverse coverage, detached components). No
check logic changed — a test asserts the two modes report identical findings in
identical order. `/ontology` states the two-tier design, lists the active
declarations with the document lines they were transcribed from and the rulings
behind them, names what is deliberately absent, and prints the scan with a stance
beside every finding: on this graph 7 recorded design decisions, 8 answered by
the declarations layer, 4 open defects, 0 unclassified. If the scan cannot run,
the page is not written.

**V2-R6 · discipline.** Worktree-isolated. Tokens only — no new colour, no new
type; the pages link the generated `chrome.css`. Every new page registers a slug,
which is what writes its canonical tag, its sitemap entry and its footer nav
link, so a page cannot ship unlisted or with a `.html` URL. Every new page joins
the copy contract in the commit that creates it. No deploy.

## How it was verified

`node web/build-atlas.mjs`, tail:

```
releases: 3 entries — pin ruleset v0.7.1, record pipeline/family_calibration/records/2026-08-13_v071_run6.json (PASS)
family pages: 25 written, 1250 assigned relations accounted for (1 family with no assigned edge)
query panel: declarations 7 active, walk header lifted from kg_query.py (371 chars)
ontology page: scan 9/8/2 findings — 7 design, 8 declared, 4 open, 0 unclassified
pages: 28 generated (…) · sitemap 34 urls
copy contract: ok — 93 meta-derived numbers allowed, no banned phrases
```

`python3 tools/build_ledger_page.py` (runs standalone; it needs only
`pipeline/state.json`, `seed.json`, `validations.json` and `disputes.json`, all
of which are tracked):

```
built web/public/ledger.html: 1555 edge records, 57 batches, 50 human chips, 19 dispute rows, 80 facet chips over 33 windowed batches
```

`python3 -m pytest tests/ -q`:

```
........................................................................ [ 92%]
......                                                                   [100%]
78 passed in 0.97s
```

`python3 tools/check_paper_facts.py`:

```
PAPER FACTS: all checks pass (248/669/699; mix 470/166/63; xv 505; frags 0/0; canaries 7; james 38)
```

The query panel was also loaded in a browser against a static server over
`web/public`: the filters populate from the data, closure and the walk run, and
the console is clean. The ontology and family pages were rendered and read.

## The [DEFAULT] decisions, for review

1. **Family-scoped counts on one line, graph-wide on the next** (V2-R2, per the
   mockup). Applied. A family count can never be read as a total.
2. **The external-validity row binds to a family only where the report names
   exactly one.** The report's "controls (personif., union)" row is shown in the
   table and attributed to no family page; the personification and union pages
   say the sample did not reach them. Splitting that row across two families
   would be interpretation, and the receipts do not support it.
3. **A family with no assigned edge keeps its page and reports zero**
   (amplification, after ruling 1's re-run). Dropping it would hide the
   reclassification.
4. **History chip: latest transition plus "n earlier"** (V2-R3). Applied,
   untested against real data because no edge carries `history` yet.
5. **`reassigned` facet included and labelled derived** (V2-R3). It is derived
   from a recorded history entry or from a `by` string naming a re-run; the facet
   row says so. 69 records carry it today, all from the `by` string.
6. **Facet combination: OR within a row, AND across rows.** Stated under the
   strip rather than left to be discovered.
7. **Headline count on /query is stored edges, with "+N derived"** (V2-R4).
   Applied, with a line saying a copied number is an edge count.
8. **The results list draws at most 300 rows** and says so, pointing at the CLI
   for the whole set. A 1,755-row list is not a result a reader can read.
9. **Page receipts stamp the build date, not the build commit.** The commit stamp
   dirtied 26 pages on every build after every commit. The build commit stays on
   the ontology panel, where V2-R5 asks for it.

## Deviations from the spec, with reasons

1. **V2-R5 says "the method/about page gains a section"; the section shipped as
   its own page, `/ontology`.** `docs/METHOD_COPY.md` is authored by the Fable
   session and wired verbatim — the builder is explicitly forbidden from editing
   that prose, and the file is outside this slice's edit boundary. A separate
   page keeps the method copy untouched. If you would rather it lived inside
   #/method, the copy needs a section written on that side and the panel can be
   injected at the same anchor; the QA JSON is already emitted to
   `web/src/ontology_qa.json` for exactly that.

2. **The new pages are not linked from the atlas topbar.** The topbar lives in
   `web/index.html`, which this slice may not edit. The pages are reachable from
   the footer nav on every generated page, from the families page (each family
   links to its page), and from the sitemap. Adding `/releases`, `/query` and
   `/ontology` to the topbar is a three-line change to `index.html` and is the
   obvious next step if you want them found from inside the atlas.

3. **`web/src/relation_declarations.json` is emitted as specified, and a second
   copy goes to `web/public/`.** A page served from `web/public` cannot read
   `web/src`, which Vite bundles. The `src` copy is there for the app to adopt.

4. **`tools/build_ledger_page.py` was restructured** so its helpers are importable
   without side effects (the work moved into `build()`). The generated page is
   otherwise the same page plus the facets, anchors and history chip.

5. **`james.html` is exempted from the URL-convention sweep.** It predates the
   convention, carries no canonical tag and is not in the sitemap. The exemption
   is pinned by a test, so a second unmanaged page fails the suite.

## Open questions

1. **The pending-queue artifacts must not be rebuilt from this worktree.**
   `pipeline/work/` is gitignored and does not exist here, so a build run in this
   worktree writes `web/src/pending.json` as absent and drops the queue count
   from `web/src/method.json` (262 → 0). Those three files were restored and are
   deliberately not in any commit on this branch. After merging, rebuild in the
   main tree — where `pipeline/work/family_pending_queue.json` exists — before
   any deploy. The per-family pages' queued items read `seed.json`, not that
   file, so they are unaffected.

2. **`relation_family.history` does not exist yet.** The ledger is ready for it
   and renders nothing without it. Writing it is the mining pipeline's change;
   until it lands, the v0.7.1 re-run's prior assignments survive only in git.

3. **The batch facet covers 33 of 57 batches.** Only the windowed `b-*` batches
   declare a paragraph range; the CW 14 sets and the incidental volumes do not,
   so their records carry no batch chip. Adding windows to those entries in
   `pipeline/state.json` would close the gap, but that file is the mining track's.

4. **The releases entry for v1.4 is prose I wrote from CLAUDE.md and the
   committed receipts.** It is the one place in this slice where the wording is
   not derived from a document the project already owns. It should be read as a
   draft of the release note rather than as a record.

5. **`/ontology` names the commit it was built at, which is the commit before
   the one that commits it.** V2-R5 asks the panel for a date and a commit, and a
   page cannot name the commit that contains it. The stamp reads as "generated
   from this tree state", which is what it is, but it means the page is one
   commit behind after every rebuild-and-commit cycle. Two builds of an unchanged
   graph are otherwise byte-identical — `8c80b40` fixed the two places where they
   were not.

6. **The ruleset may have moved.** This worktree built against the committed
   `FAMILY_DEFINITIONS.md` at v0.7.1. The main tree has that file modified. If
   the version has moved, `/releases` and every family page will say so on the
   next build, and the pin will refuse to render without a PASS record for the
   new version.

## Recovery

If this branch is not wanted:

```
git -C ~/Documents/github/JungKG worktree remove ~/Documents/github/JungKG-ui-v2 --force
git -C ~/Documents/github/JungKG branch -D ui-v2-dev
```

Nothing outside that worktree and that branch was written.
