# Releases

<!-- EDITORIAL NOTE — for whoever edits this file. Not rendered: the releases
     generator strips HTML comments before it parses or renders anything, so
     these conventions stay with the file without being read at the reader.

     STRUCTURE. Every entry carries the same four sections in the same order —
     mining status, governance, core build, UI — so two releases can be read
     against each other line for line. An entry opens with a `status:` line and
     a `pin:` line, in that order.

     POINTERS. Artifacts inside the repository are named as repo-relative paths
     in `code formatting`: the repository is not public until the release
     ceremony, so they are paths today and become links when it is. Pages on the
     site are given as real links, extensionless by the site's own convention.

     FIGURES. This file carries no typed figure. Counts are written as named
     tokens in double braces and bound from the graph, the calibration records
     and the committed experiment receipts by web/build-atlas.mjs; a token the
     build cannot bind fails the build rather than shipping as literal braces.
     Where a number is small and not count-like, write the word.

     ORDER. Entries are sorted newest-first by the version in their heading, so
     a new entry can be appended anywhere in the file. -->

What changed between one release of the graph and the next, and why. The ledger
records every individual claim and the gates it passed; this page records the
release-level story.

Each entry opens with a pin: the graph version, the ruleset version it shipped
with (deliberately separate numbers), and the calibration record binding at tag
time.

## v1.4: the alchemical trilogy, the archetype volumes, and the relation-family layer

status: pending. The ceremony waits on the arXiv publication of the paper.
Scope: the 2026-08-05 plan put Aion and CW 9i in v1.5; the arcs closed first, so
they are here.
pin: graph v1.4 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined CW 12, 13 and 14; the alchemical trilogy is complete.
- Mined Aion (§1–429), closed at b-cw9ii-7 on 2026-08-06.
- Mined CW 9i (§1–718) over ten windows, closed at b-cw9i-10 on 2026-08-12.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} merged batches, all on the [ledger](/ledger).
- Normalized {{normalized}} relation strings; the verbatim string stays frozen
  beside each.
- Assigned families: {{assigned}} assigned, {{pending}} queued,
  {{no_family}} no family, {{text_undecided}} text undecided (assigned, not
  verified; [families](/families)).
- Found the clause-predicate defect at b-cw12-1: {{clause_edges}} relations
  carrying a proposition in the predicate.
- Traced it to a briefing bullet; replaced the bullet with a form rule at
  b-cw9ii-3. Fifteen blind batches at 0% since.
- Did not re-mine: each affected relation is verified true, so it carries a
  normalization layer instead.

### governance

- Moved the ruleset to {{ruleset}}, {{families}} families; every version carries
  a calibration PASS record and CI refuses a version without one.
- Re-ran every `amplified-by` edge under ruling 1; `amplification` now holds
  none; [the page](/family-amplification) carries the count.
- Declared {{declarations_active}} inverse and symmetric pairs, each citing a
  document line. No transitivity.
- Calibrated the family gate: {{cal_caught}}/{{cal_planted}} planted errors
  caught, {{cal_clean}}/{{cal_clean_of}} clean assignments left alone (measures
  the instrument, not Jung). Gate model {{gate_model}}: within-vendor role
  separation, not cross-vendor.
- Checked {{ev_items}} assignments against {{ev_works}} works over
  {{ev_passes}} passes: {{ev_agrees}}/{{ev_treated}} treated items agreed,
  {{ev_disagrees}} disagreed, {{ev_split}} split, {{ev_not_treated}} untreated;
  {{ev_rulings}} rules changed. Receipts in
  `docs/experiments/external_validity_2026-08/`.
- Withdrew four reviewer-supplied citations (one held) and the pre-August
  calibration figures.
- Flagged b-cw9ii-1 against b-cw9ii-2 as confounded: the blinding changed
  between them.

### core build

- Launched the site on Cloudflare Pages, 2026-08-07.
- Adopted extensionless URLs, 2026-08-10.
- Made the generators deterministic.
- Emitted [/graph.json](/graph.json), the declarations, the batch manifest, the
  family map and the ontology scan.
- Shipped `tools/query/kg_query.py` and `tools/query/export_rdf.py`, read-only.

### UI

- Added [releases](/releases), [ontology](/ontology), [query](/query), a page per
  relation family, a page per batch.
- Added facets, record permalinks and the assignment-history chip to the ledger;
  moved the batch narrative onto the batch pages.
- Adopted the design rules recorded as V2-R7 to V2-R13 in
  `docs/ATLAS_REQUIREMENTS.md`.

## v1.5: the vocabulary-transfer study

status: pending. Runs after v1.4's ceremony.
pin: graph v1.5 · ruleset pending · calibration record pending

### mining status

- Mined the material already: CW 9i and Aion are in the graph.

### governance

- Asks whether the vocabulary learned on the alchemical volumes transfers to
  archetype theory mined without alchemical carriers.

### core build

- No new pipeline. Measures over the committed graph.

### UI

- No changes.

## v2.0: the graph as a queryable instrument

status: pending. Populated finally at the ceremony.
pin: graph v2.0 · ruleset pending · calibration record pending

### mining status

- Opened CW 8 under a freshly ruled ruleset.
- Merged window one (§1–71) of fourteen.
- Scheduled the remaining windows, one per firing, each gated on green CI.

### governance

- Carried every ruleset version since v0.7 with its own calibration PASS record.
- Closed the external-validity check; figures in v1.4 below.
- Added gates: ledger freshness, batch manifest, size budget, inline-style
  geometry scan, copy contract on every page.

### core build

- Shipped the query engine: {{declarations_active}} declarations, read-time
  closure, carried qualifiers.
- Shipped the Turtle export, which declares no transitivity.
- Built the ledger and its per-batch pages from one generator in one pass.
- Made the builds deterministic.

### UI

- Carried [releases](/releases), [ontology](/ontology), [query](/query), a page
  per family, a page per batch.
- Adopted the menu taxonomy and the single-gutter layout.
- Held the identity walk out of the UI: built and tested in
  `tools/query/kg_query.py`, not exposed on the site.

## v1.3.0: the published baseline

status: released and frozen. Retrospective.
pin: graph v1.3.0 · ruleset none (the family layer did not exist yet) ·
calibration record none

### mining status

- Mined CW 14 with seven incidental volumes: {{frozen_nodes}} nodes,
  {{frozen_edges}} relations, {{frozen_refs}} references.
- Ran at 0–0.5% clause predicates; this material predates the windowed pipeline.

### governance

- Pinned these counts to the `v1.3.0` tag in `tools/check_paper_facts.py`.
- Published the method in `docs/PAPER.md`.

### core build

- Released to Zenodo, concept DOI
  [10.5281/zenodo.21631523](https://doi.org/10.5281/zenodo.21631523).
- Froze the snapshot at [/v1.3/](/v1.3/); no generator writes it.

### UI

- The atlas as published, with its own ledger and dispute log.
