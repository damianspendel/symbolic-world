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

---

# Revision round — 2026-08-13, after review

Eight items came back from review of the dev build. Same branch, same worktree,
same constraints: no writes in the main tree, no deploy, no push.

**Interruption, stated plainly.** The session hit its usage window after items 1
and 4 were committed and resumed at 12:00. The tree was clean at the pause and
nothing was lost; the check on resumption was that `f4c2c53` and `60deb70` were
in and that the release-to-batch linking they depend on was finished (it was —
the links had no batch ids to bind until item 5 wrote them, and item 5's entry
now exercises seven of them).

## Commits

| Commit | Item | What |
|---|---|---|
| `f4c2c53` | 4 | V2-R8 — volumes sort in collection order, one comparator per language |
| `60deb70` | 1 | V2-R7 — batch history moves to a page per batch |
| `a7151f7` | 8 | V2-R10 — one site menu on every page |
| `1dfab7f` | 3 | ontology page: where the checks come from (the OOPS! catalogue) |
| `78054d3` | 6 | V2-R9 — heavy tables behind a headline and a native `<details>` |
| `1a8a6dd` | 5 | releases newest-first, and the v1.4 entry drafted |
| `5e96536` | 2 | depersonalize the published documents |
| `2dc2bb4` | — | chrome.css carries the menu styles it was generated with |

## Changes, old → new

1. **Batch history off the ledger** (V2-R7, added to the spec).
   - Ledger, was: `<h2>Batch history</h2>` followed by 57 cards, each carrying
     that batch's full narrative and commit list, under 1,555 record cards.
   - Ledger, now: `<h2>Batches</h2>` and one index row per batch — id linking to
     its page, window, status, and "N records · M references" — plus a `↗` on
     every batch facet chip.
   - New: `/batch-<id>`, 57 pages, written by the same generator in the same
     pass. Each carries the batch's window, status, its own account of what it
     merged, its commits, and a derived delta. The derivation is stated on the
     page: *"A record is counted here when at least one of its references falls
     in the window. A record citing two windows is counted under both, so these
     figures do not partition the graph and do not add up to it."* A batch with
     no declared window says so instead of deriving: *"This batch declares no
     paragraph window … nothing is derived here."* (24 of 57.)
   - Release entries linkify any batch id they name, from `state.json`'s own ids
     and in text nodes only.

2. **Depersonalization**, 36 occurrences, hand-read one by one.
   - `docs/FAMILY_DEFINITIONS.md`: "Rulings by Damian, 2026-08-12 evening" →
     "Editorial rulings, 2026-08-12 evening"; "ruled by Damian in the
     adjudication interface" → "ruled by the author in the adjudication
     interface".
   - `pipeline/family/relation_declarations.json`: `"ruled_by": "Damian
     (validation chat)"` → `"ruled_by": "the maintainer (validation session)"`
     (this one renders on `/ontology`); "(Damian's ruling, 2026-08-13)" →
     "(editorial ruling, 2026-08-13)".
   - `docs/QUERY.md`: "activated by Damian's ruling" → "activated by an
     editorial ruling".
   - `docs/ATLAS_REQUIREMENTS.md` (9): "taken by Damian" → "taken by the
     author"; "(DECIDED, Damian, 2026-08-06)" → "(DECIDED, editorial ruling,
     2026-08-06)"; "Damian's go of 2026-08-13" → "Editorial go-ahead of
     2026-08-13"; "waits for Damian's review" → "waits for the maintainer's
     review"; and the same pattern through R0, R8, R9 and V2-R5.
   - `BACKLOG.md` (10), `docs/experiments/` (9 across the protocol, the two
     reports, the sample, the README, the pre-arc check and the query-layer
     build report), and one comment in `web/build-atlas.mjs`.
   - Left as attribution, deliberately: `.zenodo.json`, the schema.org creator
     in `index.html`, and the method page's citation block ("Spendel, Damian").
     Left alone as out of scope: `CLAUDE.md`, git history, and `seed.json` —
     whose single occurrence is in a `_citation_key` note that no generator
     reads and that never reaches the site.

3. **Ontology page: where the checks come from.** New section before the panel —
   what a pitfall catalogue is, the OOPS! citation in one line
   (Poveda-Villalón, Gómez-Pérez and Suárez-Figueroa, IJSWIS 10(2), 2014), and a
   table of every pitfall code the scan cites, read out of the tool's findings
   and source rather than typed. Three codes are borrowed for faults of a
   different shape and a third column says so, because the catalogue was written
   for class-shaped ontologies. The page states it is a local implementation of
   a subset and not the OOPS! service.

4. **Volume ordering** (V2-R8, added to the spec). The `/query` volume dropdown
   was ordered by reference count (9i, 14, 9ii, 12, 13, 5, 11, 16, 8); it now
   reads 5, 8, 9i, 9ii, 11, 12, 13, 14, 16. `volKeyBuild` in `build-atlas.mjs`
   was a second JavaScript copy of the comparator and is gone; both JS call
   sites now import `byVolume` from `web/query-semantics.mjs`, and
   `volume_key` in the ledger builder is the one Python copy.

5. **Releases.** The generator sorts entries by the version in each heading, so
   the page reads v2.0, v1.5, v1.4 while the file stays in ascending order (a
   test asserts the two disagree, so the sort is actually exercised). The v1.4
   entry went from a five-bullet sketch to a drafted release note: five arcs
   with their closing batches linked, the family layer and its external check,
   the site launch and the URL convention, and a section on the clause-predicate
   defect — no form rule on disk, the briefing line that caused it, 77% on the
   blind batch that followed it, 0% on every blind batch since, and the decision
   not to re-mine relations that are true but mis-shaped. The clause count binds
   to the same rule `quality.py`'s P24 check applies.

6. **Progressive disclosure** (V2-R9, added to the spec). Family pages, was: the
   whole six-row external-validity table inline on all 25. Now: one headline
   line — *"Checked against 8 works of scholarship: across the sample, 8 of 16
   treated items agreed with our family. This family: 3/3 agreed …"* — with the
   table behind a native `<details>`, and the limit *outside* the fold. Ontology
   page: the 19-row findings table now sits behind *"19 findings: 7 recorded
   design decisions, 8 answered by the declarations, 4 open defects"*, with the
   four headline figures still in the open.

7. **One site menu** (V2-R10, added to the spec). Was: a single `← the atlas`
   link on each generated page, so `/query`, `/releases` and `/ontology` were
   reachable only from the sitemap. Now: atlas · query · families · ledger ·
   releases · ontology · disputes · method, in the same position on every
   generated page, on `index.html`, and on the pages python writes, with the
   current page marked and the breadcrumb keeping its slot.

## Where V2-R9 was not applied, and why

- The **declarations register** on `/ontology` and the **string map** on family
  pages: the table is what the reader came for; folding it hides the subject.
- The **batch index** on the ledger: it is already one line per batch.
- The **ledger's own record list**: it is the page, and it has facets and a
  search rather than a fold.
- The **query results**: interactive, capped at 300 rows, and already summarised
  by the count line under them.

## Ambiguities resolved

1. **v1.4 versus v1.5 scope.** The plan of 2026-08-05 put Aion and CW 9i in
   v1.5; the instruction for this entry names them under v1.4. The arcs closed
   before the ceremony did, so the entry describes the graph as it stands and
   says so in its status line, and v1.5 is re-scoped in the file to the transfer
   study the arcs were mined for. Both statements are on the page rather than
   one of them being quietly dropped.
2. **The menu duplicates three of the app's own controls** in `index.html`
   (families, ledger, disputes). The instruction was additive and explicitly not
   a restructure, so both are present. Deduplicating them is a small change to
   `index.html` and is proposed, not made.
3. **`disputes.html` is hand-maintained** — no generator writes it — so it got
   the same menu markup by hand.
4. **The footer nav on the v2.0 pages now repeats the top menu.** Left in place;
   removing it is a three-line change and is proposed, not made.
5. **`ruled_by` is a who-field**, so it takes "the maintainer" rather than an
   "editorial ruling" phrasing that would not answer the question the field
   asks. The rulings test asserts the field exists with any value and stays
   green.
6. **Files outside the given scope still carry the name**: `README.md`,
   `docs/ABSTRACT.md`, `docs/LEGAL.md`, `docs/PAPER.md`,
   `docs/PROPOSAL_RELATION_TYPING.md`, `docs/PROPOSAL_NEXT_ARC.md`,
   `docs/PLAN_QUERY_LAYER_BUILD.md`, `docs/EXECUTION_PLAN_STEPS_2_3.md`,
   `tools/pages/RUNBOOK.md`, `tools/pages/preflight.py`,
   `tools/check_paper_facts.py`, `pipeline/family_calibration/audit_v071.py`.
   Several are owned by another track and `docs/PAPER.md` is out of bounds
   entirely, so they are listed here for a decision rather than swept.

## Verification after the revision round

`node web/build-atlas.mjs` and `python3 tools/build_ledger_page.py` both clean;
copy contract green; `python3 -m pytest tests/ -q` — 99 passed;
`python3 tools/check_paper_facts.py` — all checks pass. `web/public/v1.3/`
untouched. Nothing deployed.

## The main tree has moved while this branch was built

Checked at the end of the round, read-only: the main tree is at `c1051c0`
("b-cw8-1 merged + v0.7.2 calibrated"), its graph reads 426 nodes / 1601 edges
against this worktree's 407 / 1555, and `docs/FAMILY_DEFINITIONS.md` is now
v0.7.2 with a new ruling on instrumentality. Three consequences for the merge:

- **Nothing on these pages is pinned to those numbers.** Counts derive at build,
  so a rebuild after the merge reports 426/1601 and whatever the family states
  then are. The release pin will read v0.7.2 — and will refuse to render unless
  a calibration PASS record for v0.7.2 is committed, which is the check working.
- **The depersonalization of `docs/FAMILY_DEFINITIONS.md` will conflict.** That
  file changed on both sides: three occurrences here (two swept, one new on
  their side at the v0.7.2 changelog line, "a single ruling, Damian's"). Take
  their version of the document and re-apply the three name edits on top; do not
  take this branch's copy wholesale, or the v0.7.2 ruling is lost.
- **`b-cw8-1` is a new batch.** It gets its delta page automatically on the next
  ledger build; nothing needs adding by hand.

## Item 9 — the batch pages join the deploy gate

Regeneration was already automatic: one generator writes the ledger and all 57
batch pages in one pass, so they cannot drift from each other. What was missing
was enforcement on the shipped result, and one thing worse than missing.

**The allowlist would have blocked the whole slice.** `tools/pages/preflight.py`
checks `dist` against an exact list of filenames, and every page this slice adds
— releases, query, ontology, 25 family pages, 57 batch pages, `query.js`,
`relation_declarations.json` — was an "unexpected file", which is a hard deploy
failure. Found by running the real preflight rather than reading it. Fixed here:
the fixed pages join `ALLOW`; the two generated families are admitted by pattern
*and* by vouching — a `family-<name>.html` must name a family the ruleset holds,
a `batch-<id>.html` must be listed in the manifest — so a page from a retired
family or a renamed batch is still rejected.

**A batch id can contain the word "candidates".** The pre-window CW 14 sets are
named `cw14_candidates10`, and `candidates` is one of preflight's forbidden
patterns (it exists to stop mining working files shipping). The pattern is
unchanged; the sweep now skips it only for a file the batch manifest vouches
for, which a stray candidates file cannot be — it would have to be named
`batch-<id>.html` and appear in a manifest the ledger generator wrote.

**The manifest.** `tools/build_ledger_page.py` writes
`web/public/batch_pages.json` on every run: the ids it wrote, the page filenames,
the count, and the `seed.json` node and edge counts it derived them from.

**The gate**, beside the ledger-freshness gate:
- every id in the manifest has its page in `dist`;
- no batch page in `dist` is absent from the manifest (an orphan from a renamed
  batch cannot survive a redeploy);
- the manifest's edge count equals `seed.json`'s (a lagging set cannot ship);
- the manifest's count equals its own id list.

**Verified by running it**, not by reading it. `npm run build` then
`python3 tools/pages/preflight.py`: `manifest clean` ok, and all four new gates
ok. Three failures remain and none is from this work — `pages.json` is missing
(it comes from the gitignored `app/` tree), the test harness needs
`data/paragraphs.jsonl` (the corpus is local-only by design), and the family
queue check compares `pipeline/work/family_pending_queue.json` (271 items,
copied in from the newer main tree) against this worktree's older `seed.json`
(262 pending). All three are environmental to a worktree and resolve in the main
tree. The gate's failure modes were exercised directly: a removed page, an
injected orphan, a lagging manifest and a non-batch `candidates` file each trip
the check they should.

**Sitemap decision: yes, the batch pages are in `sitemap.xml`** — they were from
the commit that created them, and the sitemap now lists 91 urls. They are public
pages with real content that the ledger links from two places; a crawler that
reaches them from the ledger will index them whether or not they are listed, and
leaving them out would only make the sitemap a partial account of the site. If
the crawl budget ever argues otherwise, the entries come from one loop in
`build-atlas.mjs` and are cheap to drop.

## Item 10 — one menu, grouped; the toolbar loses its second navigation

The topbar carried two navigation systems: the site menu added in V2-R10 and the
app's own concordance / families / ledger / disputes / about links beside it.

**The taxonomy** (editorial ruling, 2026-08-13), rendered in this order with the
group label set quietly in the mono face at `--ink-dim`, not as a heading:

| group | items |
|---|---|
| explore | atlas · query · concordance |
| reference | families |
| provenance | ledger · releases · disputes |
| about | method · ontology |

`atlas`, `concordance` and `method` are SPA routes (`/#/atlas`,
`/#/concordance`, `/#/method`); the rest are extensionless static pages. Still
one source per generator language — `MENU` in `web/build-atlas.mjs` and in
`tools/build_ledger_page.py`, now a list of groups — still no script, still
wrapping on narrow screens.

**Batches are deliberately not a menu item.** They are reached from the ledger's
facet links and from the release entries that shipped them. Nine destinations is
already the ceiling; adding a tenth that fans out to 57 pages is the thing that
made the ledger unwieldy.

**The toolbar was deduplicated.** `index.html` loses `open-concordance`,
`open-families`, `ledger-link`, `disputes-link` and `open-method` — "about"
folds into the menu's *method* and *ontology* entries — and keeps controls only:
brand, version, fit, reset, counts, search. Nothing else in the toolbar was
touched; the search field and the counts wiring are untouched.

**One consequence had to be handled.** `web/src/main.js` bound three of those
buttons unconditionally, so removing them from the template would have thrown on
load and blanked the atlas. The three bindings are now optional (`?.`), which is
the smallest change that survives the removal; the routes themselves are
unchanged and the router still serves `#/concordance`, `#/families`, `#/method`
and `#/queue`. Verified by building the app and loading it: no console errors,
the toolbar holds six control ids and no links, and all three routes open. The
same check against a build of the pre-change tree behaves identically, so
nothing in the route handling regressed.

**One discrepancy, flagged rather than resolved silently.** The instruction said
"keep the menu eight destinations", and the ruled taxonomy lists nine (the
previous menu had eight; `concordance` is the addition). The explicit list was
followed. If eight was the binding number, `concordance` is the item to
reconsider, since it is the only SPA view that has a full page elsewhere in the
in-app routes.

**Tests**: the menu contract is now the whole shape — groups, items and order —
compared across every generated page, `index.html`, and both generator sources;
plus a check that each destination appears in `index.html` exactly once, that
the removed ids are gone from the toolbar while the control ids remain, and that
the three optional bindings are guarded and their routes still exist.

## Item 11 — the header is pinned, and one structure

The menu moved between surfaces: in the app it sat after the brand block *and*
the version chip, whose width changes with the graph counts, so it landed at a
different x than on a generated page, which had no brand at all.

One header fragment per generator language now emits the same structure
everywhere — `<header class="site-header">`, row one `brand` then `topmenu`, row
two whatever varies. The brand is `flex: 0 0 13rem`, so its content cannot move
the menu; the breadcrumb, the version chip, fit/reset, the counts and the search
field all sit on the second row. The header is `position: sticky; top: 0` with
the ground colour and the hairline border from tokens. The app keeps
`position: fixed` — style.css's id rule outranks the class, and the atlas body
does not scroll, so fixed and sticky are the same picture there; only the box
model is restated for the two-row layout.

Measured rather than asserted, at 1280px: the menu's box is x=264, y=17 with a
48px first row on `releases`, `ledger`, `ontology`, a family page, a batch page,
`query`, `disputes`, `families` **and** the app — the same numbers on all nine.
Scrolled 4,000px down the ledger the header stays at top 0 with the menu
unmoved. No console errors after the restructure.

Tests: the header's structural order (brand before menu, menu before breadcrumb,
row one before row two) compared across every generated page; the same order
asserted in `index.html` with nothing but the brand block between the row and
the menu, and every control id on the second row; and the shared class checked
for sticky, top 0, the ground and hairline tokens, and a fixed-width brand —
defined once, not once per page.

## Item 12 — the header on the app's own routes, and what "ontology" turned out to be

Reproduced all three before changing anything.

**#/method, #/concordance (and #/families, #/queue, which were not in the
report but fail the same way).** `#mode-panel` is `position: fixed; inset: 0;
z-index: 13` with its own scroll, and `#topbar` is `z-index: 10`. The panel
covers the header completely — measured `headerReachable: false` at a point
inside the header's own box — and each route drew a different bar of its own
(`.page-bar`: a back button, a breadcrumb, a search field), which is not sticky
against the panel's scroll. So the header was not merely unpinned on those
routes; it was not on screen, and what replaced it scrolled away.

**/ontology.** Not a header fault. Loaded directly it holds — `top: 0`,
menu at x=264, y=17, unchanged after scrolling 2,500px. It reproduces as a
dev-server artifact: `web/serve.mjs` answers anything it cannot find with
`index.html`, so an extensionless `/ontology` — the site's own URL convention,
which Cloudflare Pages serves from `ontology.html` — returned the atlas shell.
A reader clicking *ontology* in a dev build landed on the app's landing view,
where the topbar is deliberately invisible until the atlas takes over. Fixed in
`serve.mjs`: try `<path>.html` before the shell, which is what Pages does.

**The fix is one header, not three.** `build-atlas.mjs` now emits
`web/src/chrome.json` — the header as a template — and `main.js` renders it for
every in-app route, with the brand pointing at `#/atlas` instead of `/` and the
breadcrumb, search field and any per-route extra on the second row. Rendered as
the panel's first child, `position: sticky; top: 0` pins it against the panel's
own scroll. There is now one header fragment in the project rather than one per
surface, which is what stops the next route from regressing it.

**Measured after the fix**, at 1280px: menu box x=264, y=17 on the atlas view and
on #/method, #/concordance, #/families and #/queue — the same coordinates the
eight generated pages report — and `header.top` stays 0 with the menu unmoved
when each route's own container is scrolled 1,500px (916px on concordance, its
full height). No `.page-bar` remains in the DOM on any route, and no console
errors.

**The landing view is the one surface without the header, by design.** The
topbar is invisible until `body.atlas`; the header fades in with the atlas. That
is R0.1's staging, not a bug, and changing it would be a landing redesign.

Tests: the emitted template's order (brand before menu before row two), its menu
matching the generated pages link for link, `main.js` importing and rendering it
with no bespoke bar left behind, and the dev server's extensionless resolution.

## Item 13 — atlas stability, minimal profile

**The ruling (editorial ruling, 2026-08-13).** Layout stays fresh per visit — no
build-time positions, no stored layout. Viewport and selection survive
view-switches only, in memory; a reload may start fresh. A full re-layout per
release is fine. URL deep links: yes.

**1. The atlas across routes was already alive — measured, not assumed.** The
cytoscape instance is constructed once at module load and never destroyed; the
route views are an overlay (`#mode-panel`) that is shown and hidden over it, and
`enterAtlas()` returns early when the atlas is already up, so returning to
`#/atlas` does not re-frame. Measured on the built app: zoom, pan, node
positions, the selection and the faded/neighbour state are **bit-identical**
before and after five `#/concordance ↔ #/atlas` round-trips (`z` 0.37 → 0.37,
pan `{-40, 60}` → `{-40, 60}`, `sol` still selected). A node tap after those
round-trips fires **once**, so nothing doubles up on re-entry. The container is
covered rather than hidden with `display: none`, so no `resize()` is needed and
none was added.

**2. Deep links.** `#/atlas?node=<id>` selects on arrival and focuses the
node's neighbourhood through the existing capped zoom (R9.2), not a maximum
zoom: loading `#/atlas?node=mercurius` cold selects mercurius, opens its panel
and lands with the node on screen at zoom 0.106 — the fit its 52-edge
neighbourhood asks for. `#/atlas?edge=<id>` works the same way. Selection is now
reflected with `history.replaceState`, so three selections in a row grow history
by **0** entries (it used to push one per selection), and clearing the selection
clears the parameter back to `#/atlas`. The older `#/n/<id>` and `#/e/<id>`
permalinks are still read on arrival, so links already copied out of the site
keep working. A deep link naming a node the graph does not carry warns in the
console and leaves the atlas alone rather than half-selecting.

**3. Not done, deliberately.** No "view in atlas" links were added to the other
pages — the ruling says inbound links only for now, and that is the follow-up.

Headless tests cover the mechanism: one construction and no `destroy()`, the
early return in `enterAtlas`, `replaceState` rather than `setHash` on selection,
the parameter form read by the router with the old permalinks still matched, and
the parameter cleared when the selection is. The behavioural claims above are
browser measurements and are reported as such.

## Item 14 — three findings from the re-review

### 14.1 The current-page mark

The gold state was written at build time into generated pages and nowhere else.
The app rendered the shared header with no destination marked, so *concordance*
— and *method*, *families* and the queue — never lit. Marked now in
`openPage()`, the one place every route passes through, from a route map that
sends `#/queue` to the *families* item (R10.5 nests the queue there). Measured:
`#/concordance → /#/concordance`, `#/method → /#/method`, `#/families →
/families`, `#/queue → /families`, `#/atlas → /#/atlas`, one marked item each.

### 14.2 One heading scale

Measured before: the same heading level was 1.25rem gold on a batch page,
1.3rem ink on the ledger, 1.35rem gold on a family page, 1.45rem gold in the
method view and 1.7rem ink everywhere else in `#mode-panel`. Five settings for
one level.

The scale is now defined once, in the shared chrome block that feeds both
`chrome.css` (pages) and `tokens.css` (app): h1 display/2rem/ink, h2
display/1.35rem/gold, h3 display/1.1rem/ink, h4 mono/0.6rem/gold-dim. Every page
and view keeps only its margins. `#mode-panel h2` and `.method-page h2` in
`style.css` lost their faces, sizes and colours; the batch page's h1 keeps the
mono face for the id itself, inside a heading set like every other.

Measured after, computed styles: h2 is Hoefler Text / 21.6px / 500 / gold on
`#/method`, `#/concordance`, `#/families` and on releases, ledger, ontology, a
family page, a batch page and families; h1 is Hoefler Text / 32px / ink on all
six page types. Two deliberate exceptions, both left alone: the landing hero
(`#prose h1`) is a hero rather than a heading level, and the selection and
family side panels are components with their own scale.

### 14.3 Identity-preserving returns from every route

Diagnosed rather than guessed. Driven by hash, all four routes already
preserved. The failure is in the return path a reader actually uses: the menu's
hash destinations carry absolute hrefs (`/#/atlas`) so a generated page can load
the app, and inside the app that href is a different PATH whenever the app is not
served from exactly `/` — every dev build and every preview. Clicking *atlas*
from a route therefore reloaded the document and the graph came back
re-laid-out with the selection gone. Concordance appeared to work because its own
back control is a hash link; the menu's was not.

Fixed with one delegated click handler: any `/#/…` href is routed in place, and
real pages, modified clicks and middle clicks are left to the browser.

Measured, returning by clicking the menu's *atlas* item, with zoom 0.34, pan
`{-19, 88}` and `coniunctio` selected before each:

| route | identical on return | reloaded |
|---|---|---|
| #/concordance | yes | no |
| #/method | yes | no |
| #/families | yes | no |
| #/queue | yes | no |

Bit-identical means zoom, pan, the first six node positions, the selection and
the faded-element count. Search and filter are untouched: search still dims the
non-matching graph (1,796 elements on `mercurius`) and reset still re-fits, which
is what those actions are for.

## Item 15 — title-band and search-position audit

Enumerated first, across every surface, measured in the browser at 1280px. The
two reported symptoms were each one instance of a wider drift, and the audit
turned up a third that nobody had reported.

### Before

| surface | title band | computed | search / filter |
|---|---|---|---|
| app · landing | `.eyebrow` + `#prose h1` | Hoefler 65.6px ink | in header, RIGHT |
| app · atlas | brand only | Hoefler 16.8px ink | in header, RIGHT (x=900) |
| app · #/method | `h2` (first content heading) | Hoefler 21.6px **gold** | in header, **LEFT (x=109)** |
| app · #/concordance | `h2` | Hoefler 21.6px **gold** | in header, **LEFT (x=157)** |
| app · #/families | `h2` | Hoefler 21.6px **gold** | in header, **LEFT (x=287)** |
| app · #/queue | `h2` | Hoefler 21.6px **gold** | in header, **LEFT (x=287)** |
| releases | eyebrow + h1 | Hoefler 32px ink | none |
| ontology | eyebrow + h1 | Hoefler 32px ink | none |
| query | eyebrow + h1 | Hoefler 32px ink | none (form in content) |
| families | **h1 only, no eyebrow** | Hoefler 32px ink | none |
| ledger | **h1 only, no eyebrow** | Hoefler 32px ink | **in content, LEFT (x=200)** |
| disputes | **h1 only, no eyebrow** | Hoefler 32px ink | none |
| family page | eyebrow + h1 | Hoefler 32px ink | none |
| batch page | eyebrow + h1 | Hoefler 32px ink | none |
| james | no header at all | — | none |

And the finding nobody reported: **the `.where` breadcrumb had lost its styling
entirely**. The rule that set it was `.page-bar .where`, and `.page-bar` went
away with item 11's header, so on every surface it was rendering as
`Iowan Old Style / 16px / ink` — body copy at title weight, immediately under
the menu. On the three pages with no eyebrow it read as a second title. That is
almost certainly what "page titles still have inconsistent fonts" was seeing.

Two further splits: subtitle lines were `.sub` ink-faint on family pages and
`.intro` **ink** on ledger and disputes for the same role, and the eyebrow was
absent on three pages entirely.

### After

| surface | eyebrow | title | breadcrumb | search / filter |
|---|---|---|---|---|
| app · atlas | — | brand | — | RIGHT x=900 `[tools]` |
| app · #/method | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | RIGHT x=905 `[tools]` |
| app · #/concordance | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | RIGHT x=905 `[tools]` |
| app · #/families | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | RIGHT x=905 `[tools]` |
| app · #/queue | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | RIGHT x=905 `[tools]` |
| releases | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |
| ontology | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |
| query | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |
| families | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |
| ledger | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | RIGHT x=901 `[tools]` |
| disputes | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |
| family page | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |
| batch page | mono 9.6px gold-dim | Hoefler 32px ink | mono 9.92px gold-dim | none |

One number differs across the table and it is the same everywhere it appears:
the eyebrow is 9.6px in a title band and the breadcrumb 9.92px in the header —
two different components, each consistent with itself.

### What changed, at the shared level

`.titleband`, `.eyebrow`, `.sub` and `.site-header .where` are defined once in
the chrome block that feeds `chrome.css` and `tokens.css`. Every generated page
and every in-app view now emits eyebrow + h1 (+ optional sub) inside
`.titleband`; the method, concordance, families and queue views gained a real
title where they had been leading with a section heading. The band's selectors
carry one more class than a view's own paragraph rule, because `.method-page p`
was repainting its eyebrow as body text in ink.

Search and filter inputs sit in `.hdr-tools`, a right-aligned cluster in the
header's second row: the atlas search, the in-app views' searches and the
ledger's record filter, which moved out of the content. The `.page-bar .spacer`
rule that used to right-align the in-app search had gone the same way as the
breadcrumb's.

### Exceptions, named in the spec (V2-R12)

The landing hero (`.hero-eyebrow` over a 4rem hero, naming the site rather than
a kind of page — renamed so `.eyebrow` means one thing everywhere else), the
batch identifier (`.idtok`, mono inside an otherwise standard h1, because it is
a machine id), the selection and family side panels (components docked beside
the graph), and the query panel's filter grid (the page's subject, not a filter
over it).

### Tests

Every generated page carries a title band with an eyebrow and an h1; no page or
view styles `.eyebrow`, `.sub`, `.titleband` or `.where` itself; the band's
scoped selectors exist so a view cannot repaint it; every search input lives
inside the header's `.hdr-tools`, which is right-aligned by the shared rule; and
no page restyles the filter input. Drift in any of these fails the suite.

## Item 16 — the frame of graph between click and view

rAF sampling is throttled in this environment (the browser pane is backgrounded
while a tool call runs), so the panel's class and content changes were
instrumented against a task counter instead — a paint can only escape where two
steps fall in different tasks.

Measured before: `CLICK@task N`, then `SHOW` and `CONTENT` together at
`task N+1`. The swap itself was tight; the gap was in front of it. The delegated
menu handler assigned `location.hash`, which queues the route as its own task,
so the frame after the click still showed the origin surface — the graph, when
the click came from the atlas. That is the reported flash.

Three changes, all structural:

- the click routes in its own task — `history.pushState` (which fires no
  hashchange) then `applyHash()` inline, with a `popstate` listener for the Back
  button that entry creates;
- `openPage` mounts and then reveals: content in, menu marked, `.hidden`
  removed last, so an empty panel cannot paint and a future render that yields
  cannot expose the graph under it;
- a cold deep link to a panel route applies in the same task as `enterAtlas()`
  rather than a tick later, which is what made arriving at `/#/method` from a
  page flash the assembled atlas. Node and edge deep links keep the tick because
  `focusOn` measures the viewport.

Measured after, from every warm origin — atlas→method, atlas→concordance,
method→concordance, concordance→method, families→method, queue→concordance:
`CONTENT` then `SHOW`, both in the click's own task, zero frames with the graph
exposed. The in-app families and queue views have no menu link of their own (the
menu's *families* is the static page), so those origins were driven by hash and
measured the same. App→static navigation is a document load: the browser holds
the old page until the new one paints, and no graph is involved.

## Item 17 — the identity walk, kept and unexposed

The walk section on `/query` sits behind `WALK_IN_UI`, a named flag set false in
`web/build-atlas.mjs`; one line re-enables it, and the non-transitivity header it
prints is still lifted from `tools/query/kg_query.py` at build, so re-enabling
cannot resurrect stale copy. The tool, its `--walk` flag, its CLI tests and the
`docs/QUERY.md` section are untouched, and that section now opens with its
status. Swept: the ontology page named the walk twice as the site's answer to
transitivity and now says it is a command-line tool in this release; the v2.0
skeleton in `docs/RELEASES.md` records it as built and kept for later; the
repo-side demo carries the same note above its walk output.

## Item 18 — the content column

### Before, measured at 1280px

| surface | main x | width | max-width | first character |
|---|---|---|---|---|
| releases | 168 | 940 | 940px | 200 |
| ontology | 168 | 940 | 940px | 200 |
| query | 168 | 940 | 940px | 200 |
| family page | 168 | 940 | 940px | 200 |
| families | 286 | 704 | 44rem | 310 |
| ledger | 188 | 900 | 900px | 207 |
| disputes | 208 | 860 | 860px | 227 |
| batch page | 228 | 820 | 820px | 247 |
| app · method | — | 672 | 42rem | 344 |
| app · concordance | — | 1100 | 1100px | 130 |
| app · families | — | 1100 | 1100px | 130 |

Five widths, six different left edges, and the header's brand at x=40 on every
one of them — so no page's text lined up with its own header, and moving between
the ledger and disputes shifted the column by 20px.

### After

| surface | kind | width | first character | brand |
|---|---|---|---|---|
| releases · ontology · families · disputes · family page · batch page | prose | 816 | 40 | 40 |
| query · ledger | records | 1104 | 40 | 40 |
| app · method | prose | 816 | 40 | 40 |
| app · concordance · families · queue | records | 1104 | 40 | 40 |

Two kinds, defined once in the chrome block. Both are capped on the right rather
than centred and take the header's own gutter, so the first character of every
surface sits directly under the brand and nothing moves as you cross between
pages. Recorded as V2-R13 with the kinds named.

Tests: every page declares a kind, no page sets its own main-column width or
padding, the two kinds are defined once and differ from each other, the base
rule is uncentred with the header's gutter, and the app's views take the same
kinds rather than restating them.

## Item 19 — one structure for every release entry

`docs/RELEASES.md` now runs the same four sections in the same order on every
entry: **mining status** (arcs, counts, verification chain, defects in the
material or the pipeline and their remediations — the clause-predicate story
lives here), **governance** (rules and rulings, CI gates, calibration, external
checks, and the corrected-or-withdrawn material folded in, because honesty is
governance), **core build** (Pages, URL convention, generator determinism,
emitted data artifacts, the query engine and the Turtle export as tools), and
**UI** (surfaces added or changed, design rules adopted, and what is
deliberately not exposed).

The v1.4 entry was rearranged into the template, not rewritten: every sentence
it had is still there, token binding untouched. v1.5 and v2.0 carry the same
four headings as skeletons. A **v1.3.0 retrospective** was added at the bottom so
the published baseline reads in the same shape; its counts bind from the frozen
constants CI already pins the paper's assertions to, and its artifacts are the
paper, the concept DOI and the `/v1.3/` snapshot.

Pointers follow one convention, stated at the top of the file: repo-side
artifacts are repo-relative paths in code formatting — the repository is not
public until the ceremony, so they are paths today and become links then — while
site-side artifacts are real extensionless links.

Order is unchanged: newest first, sorted by the version in each heading, so the
retrospective sits last without any special casing. Tests now assert the
four-section template on every entry, the baseline entry's presence and its
frozen counts, and that the entries point at their artifacts in both conventions.

## Item 20 — the panel layer, and centring restored

### 20.1 Why no panel route can flash now, by construction

The item-16 fixes were timing fixes: they closed the gaps I could measure, and
they missed whatever Safari does with a heavy view. This one does not depend on
timing at all.

`#mode-panel` is a persistent element that already existed and was already
opaque. Three changes make it a layer rather than a rendered result:

1. **The route raises it, not the render.** `html.route-panel #mode-panel {
   display: block }` outranks `#mode-panel.hidden`, and an inline classic script
   in `index.html` — placed before the header, ahead of the module bundle — sets
   `route-panel` on `<html>` from `location.hash`. On a cold load of
   `/#/concordance` the opaque surface is therefore up in the first frame,
   before cytoscape is constructed and before any view is built.
2. **It is opaque in the first-paint block.** `#mode-panel` now carries its
   `position/inset/z-index/background` in `index.html`'s inline style, so it is
   opaque even before the stylesheet is parsed.
3. **It covers the viewport at every width.** One media query inset it to
   `3.2rem 0.5rem 2.4rem`, which left the live graph visible around its edges;
   that is now `inset: 0` like every other width.

`openPage` raises the layer before it does anything else and never lowers it
between panel routes; `closeMode` lowers it, and only when the route leaves the
panel class. Item 16's improvements are kept — the click still routes in its own
task, and the content is still mounted before `.hidden` is cleared — but they
are no longer load-bearing.

**The structural argument.** From the instant the URL names a panel route until
the instant it stops naming one, an opaque element at `z-index: 13` covers the
viewport. Nothing in the transition path removes it: the incoming view is built
inside it, the outgoing view's DOM is replaced inside it, and the layer's
`display` is a function of the route, not of any render finishing. So the worst
frame a transition can produce is that layer with stale or no content — a blank
tokened surface. The graph sits at `z-index: 2` underneath and cannot be
reached, whatever the scheduler does, however heavy concordance is to build, and
whether the arrival is cold, warm from the atlas, or warm from another panel.
That is the property Damian's eye is the acceptance test for; I cannot capture
frames here, so the guarantee is stated as a covering invariant rather than as a
frame count.

Checked on every route and origin: cold load of `#/method`, `#/concordance` and
`#/queue` (layer up, `route-panel` set, opaque `rgb(11, 10, 8)`, covering, and
the viewport centre reading panel content); atlas→each of the four; each of the
four→atlas (layer lowered, class cleared, the graph revealed with no blank
frame); and the panel→panel round: concordance→method→families→queue→
concordance, layer up throughout.

### 20.2 Centring restored, and measured

V2-R13 is reversed: both kinds centre in the viewport at their own max-width,
`margin: 0 auto`, identical centring math on every page and in the app's views.

| width | prose pages | records pages | app views |
|---|---|---|---|
| 1280px | centre 638, width 816 | centre 638, width 1104 | centre 640 |
| 1024px | centre 510, width 816 | centre 510, width 1020 | — |

Prose pages measured: releases, ontology, families, disputes, a family page, a
batch page. Records: query, ledger. The column's centre is the viewport's centre
on every surface and at both widths, so moving between pages — or between kinds
— never shifts it. The tests now require `margin: 0 auto` in both the page rule
and the app's panel rule; "no page defines its own column geometry" stands
unchanged.

## Item 21 — the ledger's filter joins its facets

Editorial ruling, 2026-08-14. The filtering system was in two places: chips in a
block under *Records*, and a text box in the header that filtered the same
cards. The rule (V2-R12) is refined rather than reversed — the header's
`.hdr-tools` slot is for SITE- or GRAPH-WIDE search, which the atlas search and
the in-app views' searches are and keep; a PAGE-LOCAL filter, which narrows only
what that page lists, belongs with its facets. Position: **first row of the
facet block**, above the chips, because it is the broadest control in the family
and every row under it narrows further. The caption now reads that way too.

Same styling tokens: the input keeps `.std-search` and takes its width from a
shared `.facet-filter` rule rather than anything page-local. Checked on the
built page: the header carries no input, the filter is the first facet row, and
the controls still compose — `mercurius` alone leaves 88 of 1,555 cards, with
the CW 14 chip on top of it 32, and clearing both restores 1,555.

The query page needed nothing: its filter grid is page content and was already
correct. Tests: a search input in a generated page's header slot now fails, the
app's graph-wide search in the cluster is the asserted state, and the ledger's
filter is asserted inside the facet block and first among its rows.

## Item 22 — the title band, locked

Measured first, at 1280px, as offsets from the header's bottom edge.

### Before

| surface | header h | band top | h1 top | eyebrow→h1 | band left |
|---|---|---|---|---|---|
| app · method | 93 | 19 | 34 | 6 | 272 |
| app · concordance / families / queue | 93 | 19 | 34 | 6 | 128 |
| releases · ontology · disputes · family · batch | 83 | 26 | 41 | 6 | 270 |
| query · ledger | 83 | 26 | 41 | 6 | 126 |
| **families (the definitions document)** | 83 | 26 | **57** | **21** | 270 |

Three causes, none of them the band itself:

1. **The header's own height moved.** The second row was `min-height`, so a
   surface carrying the search input made it taller: 93 in the app against 83 on
   a page. Everything below inherited the 10px.
2. **The content column's top padding differed** — `1.2rem` in the panel,
   `1.6rem` on a page — so the band sat 19 below the header in a view and 26 on
   a page, in opposite compensation to the first.
3. **The families document left a browser default on its h1**: 21px of UA
   `margin-top` where every other surface had none, which is why "Relation
   families" sat 16px lower than every other title. That is the one Damian
   named, and it was a page-local default rather than a rule.

### After

| surface | header h | row 2 | band top | h1 top | eyebrow→h1 | band left |
|---|---|---|---|---|---|---|
| app · method (prose) | 95 | 46 | 26 | 41 | 6 | 272 |
| app · concordance / families / queue (records) | 95 | 46 | 26 | 41 | 6 | 128 |
| releases (prose, top level) | 95 | 46 | 26 | 41 | 6 | 272 |
| ledger (records, top level) | 95 | 46 | 26 | 41 | 6 | 128 |
| ontology · query · families · disputes · family · batch | 95 | 46 | 26 | 41 | 6 | by kind |

Same header height, same row-2 height, same band offset, same eyebrow→title gap
on every surface; the band's left edge is the content column's left edge, which
is the kind's and nothing else's.

The lock, all in the chrome block: the second row is a **reserved slot** at a
fixed height whether it carries a breadcrumb, the tools cluster, both or neither,
with the search input given a height so nothing in the row can stretch it; the
band carries no margin of its own and neither do its children (`> :first-child`,
`.eyebrow`, `h1`, `.sub` are all set here, so a page-local default cannot push
the title down); and the panel's content column takes the page column's
padding-top. `scrollbar-gutter: stable` is reserved on both the document and the
panel layer, so a centred column does not shift by a scrollbar's width when a
reader crosses from a page into a view.

One measurement note: the before/after page rows were taken in an iframe harness
and the app rows at top level, which differ by 2px on the centred column because
of scrollbar rendering. The after table's page rows were re-measured at top
level for that reason — `releases` and `ledger` above are real navigations, and
they match their app counterparts exactly.

Tests: the reserved row is a fixed height and every surface renders it; the band
geometry is defined once and locked; no page or view adds margin or padding
above the band, and no surface may set `h1 { margin-top }`; and the app's column
and a page's column start at the same offset.

## Item 23 — one title position, no per-kind footnote

Item 22 locked the band inside each kind and left the kinds themselves 144px
apart: prose titles at 272, records titles at 128. Crossing from the ledger to
disputes, or method to concordance, moved the title across the page.

The band is now decoupled from the kind. It takes the prose column's inner width
(46rem) and centres itself inside whatever column holds it; both kinds are
already centred on the viewport, so a band centred in either lands on the same
pixel. The kind governs only the content below the band, which is where a
records page needs its width.

That is one rule in the chrome block rather than a restructure of every
generator's body — the same guarantee, and it cannot be defeated by a page
forgetting to wrap its band, because there is no wrapper to forget. The rule
carries no kind in its selector, and a test fails the build if any stylesheet
ever scopes `.titleband` to `.prose` or `.records`.

### After, at 1280px

| surface | kind | h1 top | h1 left | band width | content column |
|---|---|---|---|---|---|
| app · method | prose | 41 | 272 | 736 | 232 / 816 |
| app · concordance | records | 41 | 272 | 736 | 88 / 1104 |
| app · families | records | 41 | 272 | 736 | 88 / 1104 |
| app · queue | records | 41 | 272 | 736 | 88 / 1104 |
| releases (top level) | prose | 41 | 272 | 736 | 232 / 816 |
| ledger (top level) | records | 41 | 272 | 736 | 88 / 1104 |
| disputes | prose | 41 | 270* | 736 | — |
| families | prose | 41 | 270* | 736 | — |
| ontology | prose | 41 | 270* | 736 | — |
| family page | prose | 41 | 270* | 736 | — |
| batch page | prose | 41 | 270* | 736 | — |
| query | records | 41 | 270* | 736 | — |

\* measured in the iframe harness, whose scrollbar renders 2px differently from
a real navigation; the two pages measured at top level — one of each kind — both
read 272, matching the app views exactly. The harness rows are internally
consistent and are what shows records and prose now agreeing.

Title top and left are the same number on every surface and in both kinds. The
breadcrumb needed nothing: it sits in the header's gutter at 40 on all twelve,
and never varied by kind.

## Items 24 and 25 — the interview ruling: one left edge, and the search where its target is

### What the interview settled, and why two rounds preceded it

The original complaint — "releases page is thoroughly left aligned, other pages
somewhat central, but not consistent" — was about INCONSISTENCY. It was read as a
preference for centring, which produced item 20.2 (both kinds centred) and then
item 23 (the band self-centring so it would land in one place across kinds).
Both were solving the wrong problem correctly. The interview settles it:
**left-aligned is the design**, and consistency comes from a single left edge
rather than from shared centring math. Items 20.2 and 23 are superseded; item
22's vertical lock stands untouched.

### The rule now

One gutter, `--page-gutter: 4.5rem`, defined once as a token and consumed by the
header rows, the title band and every content column. The brand, the menu, the
breadcrumb, the title, every paragraph, table, facet block and card start on it.
The readable cap is measured from that gutter, so the two kinds differ **only in
their right-hand cap** and never in their left edge. Nothing centres. The
landing hero is the sole exception, because it is the site's opening statement
rather than a page; a test fails the build if any other column or band centres
itself, and the narrow-screen override changes the one token rather than any
rule.

### After — every surface, both viewports

| surface | kind | brand | breadcrumb | h1 | first paragraph | first table/facet | right cap |
|---|---|---|---|---|---|---|---|
| app · atlas | — | 72 | — | — | — | — | — |
| app · method | prose | 72 | 72 | 72 | 72 | 72 | — |
| app · concordance | records | 72 | 72 | 72 | 72 | 72 | — |
| app · families | records | 72 | 72 | 72 | 72 | 72 | — |
| app · queue | records | 72 | 72 | 72 | 72 | 72 | — |
| releases | prose | 72 | 72 | 72 | 72 | 72 | 880 |
| disputes | prose | 72 | 72 | 72 | 72 | — | 880 |
| families | prose | 72 | 72 | 72 | 72 | 72 | 880 |
| ontology | prose | 72 | 72 | 72 | 72 | 72 | 880 |
| family page | prose | 72 | 72 | 72 | 72 | 72 | 880 |
| batch page | prose | 72 | 72 | 72 | 72 | 72 | 880 |
| query | records | 72 | 72 | 72 | 72 | 72 | 1168 |
| ledger | records | 72 | 72 | 72 | 72 | 72 | 1168 |

At 1024px every left-edge number is the same 72; the right caps become 880 for
prose and 1020 for records, which is the viewport binding rather than the cap
changing. One number per viewport across every surface, both kinds, app and
generated pages alike.

### Item 25 — the graph search renders on the atlas only

The search dims and focuses the atlas canvas, so on method, concordance,
families or the queue it was an instrument pointing at a target the reader
cannot see. `pageBar` no longer renders an input at all; the header's second row
on a panel view carries the breadcrumb and, where a view genuinely owns one, a
link. The atlas view keeps the search in the header's tools cluster.

One consequence handled rather than dropped: the families view's field was doing
two jobs — graph search and a filter over its own family cards. The filter
survives as a plain local control in the view's content beside the list it
filters, per item 21's rule for page-local filters, and it touches nothing but
those cards: no typeahead into the graph, no selection, no camera. Measured:
no header input on any of the four panel views or any of the eight generated
pages, and the search present on the atlas view.

### Item 24 addendum — the page-local measure on disputes

Reported and confirmed on disk: `disputes.html` carried `max-width: 64ch` on
`.intro` inside its own `<style>` block while the generated pages drew 68ch from
the shared chrome. Different measure plus centring meant a different left edge at
a wide viewport — invisible in a narrow review pane, plain on a full screen. The
new left-alignment ruling makes left edges independent of width, so it resolves
either way; the local rule is gone regardless, because a page-local geometry rule
is the fault, not its symptom.

It was not the only one: the ledger's `.intro` was 66ch and the v2 pages' bare
`p` was 68ch, three numbers for one paragraph role. The reading measure is now a
token — `--measure: 68ch` — with one shared rule (`p, .intro, .sub, .lede2,
.note`) in the chrome block, and the components that deliberately differ
(`.callout p`, the findings table's `.why`) are unchanged and still say so
locally.

**The test now reads inline styles.** A class-based check is blind to exactly
the surface that broke here, so the geometry scan opens every `<style>` block in
`web/public` — the hand-maintained pages and the exempted `james.html`
included — and fails on a `width`, `max-width` or horizontal `margin`/`padding`
set on a column, a band or a bare reading paragraph. Vertical rhythm is left
alone.

**disputes, measured as a real navigation at 1280px:**

| surface | brand | breadcrumb | h1 | first paragraph | first card | right cap | own width rules |
|---|---|---|---|---|---|---|---|
| disputes | 72 | 72 | 72 | 72 | 72 | 880 | 0 |

Its `.intro` now computes to 556.7px — 68ch from the chrome — and its style block
contains no `max-width` at all.

## Item 26 — the hybrid: one capped container, everything inside unchanged

`--page-max: 1400px`, defined once. The page content and the header's content
rows share one container: capped at that width and centred as a block. The
header BAR stays full-bleed — background and hairline edge to edge, sticky as
before — while its rows align inside the container, which is what puts the brand
exactly above the titles at any viewport. The kind's cap moved off the container
onto what the container holds, so prose and records still differ only on the
right.

Measured, in the harness at three widths:

| viewport | container | left / right margin | brand | h1 | first paragraph | first table or facet |
|---|---|---|---|---|---|---|
| 1280 (prose) | 0 → 1276 | 0 / 0 | 72 | 72 | 72 | 72 |
| 1280 (records) | 0 → 1276 | 0 / 0 | 72 | 72 | 72 | 72 |
| 1500 (prose) | 48 → 1448 | 48 / 48 | 120 | 120 | 120 | 120 |
| 1500 (records) | 48 → 1448 | 48 / 48 | 120 | 120 | 120 | 120 |
| 1920 (prose) | 258 → 1658 | 258 / 258 | 330 | 330 | 330 | 330 |
| 1920 (records) | 258 → 1658 | 258 / 258 | 330 | 330 | 330 | 330 |

Margins are symmetric within the client box; the harness reports 4px more on the
right at each width because the iframe's scrollbar takes it out of the viewport
number, not out of the container. The header bar spans the full client width at
every one, and the header's row starts at the container's left on every one.

**At 1280 the numbers are identical to the item-24 table** — 72 for brand,
title, first paragraph and first block, on both kinds. The container binds to the
viewport below its cap, so the hybrid changes nothing until there is room to
spare.

The app measured the same way at 1500: brand, title, first paragraph and first
block all at 122 on method and concordance, with the panel's container at
50 → 1450. The atlas view is unchanged and still a full-viewport canvas.

Tests: `--page-max` defined once; the header row, the page column and the panel
column all take it with `margin-inline: auto` and the gutter; the bar itself
carries no cap, so it stays full-bleed; the kinds cap the container's children
rather than the container; and centring is permitted at the container level
only — anything inside it that centres fails, which is item 24's ban intact.

## Item 27 — text pass, design frozen

Twelve edits, no design change. Review provenance: a Fable editorial pass
proposed 10; a Gemini pass run BLIND to those edits found 7; the two sets
overlapped on 1. Gemini then reviewed Fable's set, and Fable finalized. Two of
the blind findings — spacing on a summary line, and a bare "is" — were dismissed
after checking the source: extraction artifacts, the generators are clean. One
blind fix was rejected as factually wrong: it proposed changing 22 to 27 in the
external-validity sentence, which would have falsified the record, since 22 is
the assigned-plus-purposive set that was scored and the remaining 5 of 27 were
queued arm-disagreements. That distinction is now stated on the page instead,
with both numbers derived from the receipts rather than typed.

Applied: /releases — "this file records the release-level story" → "this page…"
(the later "This file carries no typed figure" keeps *file*, since it describes
the source file's contract, and Gemini's reject was right); "until the ceremony"
→ "until the release ceremony". /query — "given a surface" → "as a web page".
/families — "the KIND of relation" → "the *kind* of relation"; the queued-items
parenthetical above; "Those sections stand as the record … not as current
evidence" → "are the record … not current evidence" (the banned "stand as", a
blind catch); "dropping it would hide the finding" → "dropping the page…".
/ledger — "verification passage" → "verification trail"; "the second-vendor
cross-vendor check" → "the cross-vendor check". Family pages — the
three-treated-items sentence is static text that renders on pages whose rows
differ, so it now reads "A row this small is the items themselves; no rate over
a handful of items carries precision worth reporting", which is true for any
family's row; the h1 was a single string carrying the name AND the status chip,
so the chip moved to the `.sub` line and the heading is the family name alone;
"Boundary." → "Boundary:" in the renderer, restoring the colon the document's
own bold label carries, without touching the quoted document.

Not adopted, recorded: Fable's E8 (numeral-initial sentences on /ontology) —
Gemini rejected it, digits are house style, and the rejection was accepted.

One adjacent case left alone deliberately: the family pages' *other* bold labels
(the document's "Notes", "Seeds" and so on) render with a full stop by the same
renderer line that T12 fixed for Boundary. The ruling named Boundary; the
sibling is flagged rather than swept.

### Item 27, finalizer — the sibling labels

T12 extended, as ruled: the colon now comes back on every bold label the family
pages render from the definitions document, not only Boundary. The extraction
strips the document's colon when it keys a label, so the renderers restore it;
"Boundary:" beside "Inverse pair declared." was the same inconsistency class in
one page. Quoted document untouched. A test reads the labels off the rendered
pages and fails on any that ends in something other than a colon.

## Item 29 — two gates adopted from the pre-deploy checklist

Provenance: a Gemini pass produced an 18-item pre-deploy checklist, blind to the
existing gates. Eleven were already covered by preflight, the copy contract or
the suite; two are adopted here as permanent gates; two are ceremony one-offs
and belong in the runbook rather than in code; the rest were rejected or sent to
the backlog.

**Size budget**, in `tools/pages/preflight.py`. `viteSingleFile` inlines the
script, the styles and `atlas.json` into one document, so the page a reader
downloads grows quietly as the graph does. The gate fails a deploy whose
`dist/index.html` exceeds 3.0 MB and prints the actual against the ceiling
either way, so the trend is in the log rather than in someone's memory. Current
build: 2.15 MB against 3.0 MB.

**Extensionless redirect**, in `tools/pages/verify.py`. Pages 308s every `.html`
path to its extensionless twin, and Search Console filed redirect errors until
sitemap, canonical tags and internal links agreed on that form. After the byte
comparison, verify now requests `/ledger.html` WITHOUT following redirects and
reports the status and target. It is a warning rather than a failure, because it
tests the host's behaviour and not the artifact we built — but it prints in
every run, so a silent change cannot pass unnoticed. Exercised both ways against
a local server: a redirecting host prints `ok /ledger.html -> 308 -> /ledger`,
and a host that serves the `.html` directly prints the warning.

Tests assert the shape of both: the ceiling's value, that the budget prints, that
the redirect probe does not follow redirects, and that nothing in the redirect
block appends to `fails` or exits — a warning must stay a warning.

## Item 30 — the releases intro stops explaining itself

The page opened with four paragraphs about how the FILE is written: the
four-section structure, the pointer convention, and the token binding. Those are
instructions for whoever edits `docs/RELEASES.md`, rendered at whoever reads
`/releases`. The intro is now two short paragraphs — what the page is, and what
the pin's two version numbers mean, since every entry opens with one.

Nothing was deleted. The conventions moved to an editorial note at the top of
the source file, inside an HTML comment, and the generator now strips comments
before it parses or renders anything — the simplest mechanism, and one that
works wherever a note sits in the file. The note carries the structure, the
pointers, the figures rule and the newest-first ordering, so the next person
editing the file still meets them.

A test holds both halves: the rendered intro is two paragraphs and carries none
of the machinery vocabulary, and the source file still contains a note with the
conventions in it that never reaches the page.

**Addendum — a record, not a roadmap.** v1.5's UI section read "Nothing new is
planned" and now reads "No changes": a section states what changed, even when
the answer is none. Its sibling in v2.0 — "the surfaces this entry will ship" —
became "the surfaces this entry carries", since those pages are built and in the
branch rather than intended. The one genuinely forward-looking line is left
alone: CW 8's remaining windows are a plan and say so, and v1.3.0 carries no
such phrasing.

## Item 31 — the works are cited properly

The external-validity figures verified against the receipts row for row, but the
list of works did not: titles had lost their articles and the dictionary had
lost its three authors while every other work kept its editor. Corrected on
/families to Jacobi's *The Psychology of C. G. Jung*, Samuels, Shorter and
Plaut's *A Critical Dictionary of Jungian Analysis*, von Franz's *Alchemy: An
Introduction to the Symbolism and the Psychology*, four volumes of Edinger, and
Abraham's *A Dictionary of Alchemical Imagery*.

The list renders in exactly one place — the families page's own exposition — so
there was one edit to make. The other mentions on that page and on the
amplification family's page are the definitions document's own citations, quoted
verbatim above and below the rule; the atlas quotes that document and does not
correct it, and the repo-side reports and receipts stay as records.

Edinger's volume count stays bound to `results.json` rather than typed, so the
word still comes from the receipts. A test holds the corrected titles, fails on
any of the four old ones, and checks the bound count.

## Item 32 — the entries in changelog register

All four rewritten verb-first, one fact per line, no connective tissue. Where a
line needed depth it links the artifact — a batch page, the experiment
directory, the family page, the ledger — instead of explaining. Honesty riders
survive as clauses: "calibration 19/19 (measures the instrument, not Jung)",
"gate model gemini-3.1-pro — within-vendor role separation, not cross-vendor",
"assigned, not verified".

Word counts, against the targets:

| entry | before | after | target |
|---|---|---|---|
| v1.4 | 1,426 | 398 | ≤ 400 |
| v2.0 | 480 | 170 | ≤ 200 |
| v1.5 | 156 | 65 | ≤ 80 |
| v1.3.0 | 244 | 96 | ≤ 100 |

Kept: the four sections, the pin, tokens for every count, newest-first, and the
two-paragraph intro from item 30. The cut material is not re-homed on the page —
it is in this file's git history and in the artifacts the lines now link.

`{{ev_items}}` was added as a token so "checked 27 assignments" derives from the
receipts rather than being typed.

Three tests moved with the register: the substance check now has a ceiling as
well as a floor (150 < words ≤ 400), the artifact-pointer check names the paths
the compressed entries actually cite, and the newest-first check needed the
source file OUT of display order to stay meaningful — the file is now v1.4,
v1.5, v2.0, v1.3.0, and the page renders v2.0, v1.5, v1.4, v1.3.0, so the sort
is doing visible work. A stray copy of the old v1.4 entry, left behind by the
item-28 splice, was found by the same check and removed.

## Item 33 — the disputes intro

Two clause-heavy paragraphs replaced with the three ruled ones: what the log is
and what each outcome means; how to dispute, with the admissibility rule in one
clause; how to confirm. 158 words down to 95. The bold on *upheld*,
*both-defensible* and *not-upheld* dropped in cleanly, so it stayed. The GitHub
issue anchor is on the same phrase it was; "atlas" was never a link on this page
and is left as text.

Dropped by the ruling and gone from the file: "the falsification offer working
in public", "without adjudication", and "the machine gates are the floor;
readers are the ceiling". Everything from the disputes-on-record line down is
untouched, including both log sections and the fetch that fills them. No test
asserted the old sentences.

## Item 34 — method and ontology

**(a) Heading.** "Where people rule" → "Human oversight".

**(b) Section rewritten** in the releases razor: four labelled facts, no
connective tissue, links for depth — gold set ({{human_chips}} claims,
human-validated in the ledger), adjudication (two blind arms, {{queue}} claims
queued, a person rules in sittings, rulings signed and dated), disputes
({{disputes}} on the record with outcomes), publication (releases, deploys and
rulings are human decisions; nothing publishes itself). Every fact kept.

**(c) Confidence levels** gained the external check: the vocabulary checked
against {{ev_works}} works of scholarship, {{ev_agrees}} of {{ev_treated}}
treated items agreeing, disagreements published beside them, linked to
[/families#checked]. Phrased as a check on the classification, not on whether a
claim is true. The anchor is new: the families page's "Checked against readers
of Jung" heading now carries `id="checked"`.

**(d) Number provenance.**
1. The stale sentence said the harness "is being rebuilt" and the calibration
   "will be re-run and published". It was rebuilt: the copy now says calibration
   re-runs per ruleset version and its figures live in the version-bound records
   under `pipeline/family_calibration/records/` rather than in prose.
2. "19 public challenges" was typed and disagreed with the disputes page. The
   count now binds from `disputes.json`, the same file that page reads, as
   `{{disputes}}` = **18**. The reconciliation: there are **18 challenges**
   carrying **19 edge attachments** — a dispute may attach to two edges, and the
   typed 19 had counted attachments as challenges. The disputes page was right.
3. `METHOD_CONSTANTS` audited. **Moved to tokens:** the dispute count.
   **Removed as inert:** 19, 20, 38, 40, 2, 86, 14, 7, 25, 5 — the copy scan
   only reads 3- and 4-digit literals, so every sub-100 entry in that list was
   enforcing nothing. **Stayed, with reason:** 248/669/699, the release the
   paper describes, pinned to the `v1.3.0` tag by CI and quoted as frozen; and
   5281/21631523, the two parts of the concept DOI. Nothing derivable from live
   data remains typed.

**(e) Two drawn figures** on the ontology page, in the method page's claim-box
idiom, tokens and existing chip classes only. The **edge anatomy** box draws a
real edge — subject, the relation as Jung's sentence phrased it, object, its
citation chip and its own ≤25-word quote. The **two-tier** box draws the largest
family's top four relation strings with their real counts, arrowed into the
family chip with its own count, captioned that the family classifies and does
not re-verify. Both read the graph at build; a test compares the drawn quote and
every count against `seed.json` and the derived map.

**(f) Reordered.** The page now runs: what this is → two tiers → the
declarations → where the checks come from → the pitfall scan → deliberately
absent. The absences open with a derived line — "7 of the findings above are
these decisions, showing up as defects because the catalogue has no way to tell
a choice from an oversight" — so they read as conclusions after the evidence. A
test pins the order.

**Addendum.** The stance paragraph is the re-ruled text exactly: "A stance is
not a rebuttal of the finding. An open vocabulary is hard to query by predicate,
which is why the family layer exists. That was a conscious design decision."

**The `###` leak.** Found: a declaration's `source.section` is the definitions
document's own markdown heading ("### 1. symbolization"), rendered verbatim as a
label on the family pages' declared-pairs list and in the ontology page's
declarations table. Fixed at the renderer with one `sectionLabel` helper that
strips the marker; the document and the transcription are untouched. The sweep
found it on seven family pages and seven times on the ontology page, not the two
reported. No `**` or raw backticks leak anywhere. A test now sweeps every page
for heading markers and unrendered emphasis outside code elements, and a second
checks the label still names the document's section.

## Item 3 (final round) — the editorial sweep

One pass over every content page, applying the accumulated rules together.

### Em-dashes

Zero remain in our copy, on every page:

| page | before | after | em-dashes before → after |
|---|---|---|---|
| ontology | 2,013 | 2,004 | 10 → 0 |
| families exposition | 2,992 | 2,468 | 16 → 0 |
| family page (symbolization) | 586 | 576 | 9 → 0 |
| query | 292 | 290 | 2 → 0 |
| releases | 823 | 809 | 19 → 0 |
| disputes | 101 | 101 | 0 → 0 |
| ledger intro | 279 | 276 | 3 → 0 |
| batch page | 201 | 164 | 1 → 0 |
| method (in-app) | 1,312 | 1,296 | 17 → 0 |

The families and batch drops are larger than the sweep alone: the measurement
now also excludes the boundary rules quoted from the definitions document and
the git commit subjects on a batch page, which are records rather than our copy
and keep their punctuation.

Restructured with colons where a list or gloss followed ("the active filters:
volume, family, voice, layer"), semicolons where two clauses were joined
("carries the stamp; 1653 of 1847 citations do today"), full stops where the
sentence was doing two jobs ("The family layer's own check is a gate tested by
planting errors among real assignments. It reported catching everything
planted"), and parentheses where the aside was genuinely parenthetical ("the
ruleset version it shipped with (deliberately separate numbers)"). Page titles
now use a middle dot rather than an em-dash.

### Negative parallelisms

Killed as rhetoric: "which is exactly why the family layer exists" (already gone
with the item-34 stance rewrite), "not a structure discovered in his thought"
reset to its own sentence, and the announce-then-explain shape in the ontology
intro.

Kept as vocabulary, and flagged here as borderline calls rather than decided
silently:

- **"assigned, not verified"** — the site's central distinction; it appears on
  every family page and in the ledger. Kept everywhere.
- **"a map of assertions, not a reading"** — the standing claim about what the
  graph is. Kept.
- **"a model's judgment, not a mechanical proof"** — states what the gate does
  and does not prove. Kept.
- **"measures whether the definitions can be followed consistently, not whether
  they are right"** — the agreement/correctness distinction. Kept, em-dash
  replaced with a comma.
- **"the honest default, not a defect"** (the amber dot) — borderline: it is
  half rhetoric. Kept because it tells a reader how to read the dot, which
  nothing else on that page does.
- **"classification only; the relation above was already gated"** (ledger family
  row) — kept, punctuation changed.

### Self-description and connective tissue

Cut: "and then runs the standard pitfall scan over the graph and reports what it
finds" became "It then runs...", "What the instruments do not cover, stated
plainly:" lost "stated plainly", and the deliberate-absences section lost its
announcement in the previous commit.

### AI-tells

Swept every page and the method copy against the banned list (delve, tapestry,
pivotal, crucial, leverage, robust, seamless, holistic, "serves as", "stands
as", "it is worth", "in other words", "which is exactly why") plus the
self-description patterns: **0 hits**.

No content added, no number changed, no design touched. Copy contract green,
165 tests green.
