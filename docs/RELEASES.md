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

What each release changed.

Each entry opens with the graph version, the ruleset version it shipped with
(the two are deliberately separate numbers) and the calibration record in force
when the release was cut.

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

## v2.0: the graph as a queryable instrument

status: released 2026-09-05. Tag `v2.0.0`, GitHub Release, Zenodo record
[10.5281/zenodo.22339291](https://doi.org/10.5281/zenodo.22339291) under the
concept DOI; the v1.3 record is marked superseded and retained. Paper:
*Trust, Layered*, promoted to docs/PAPER.md after four cross-vendor hostile
passes. The v1.4 and v1.5 plans are folded in.
pin: graph v2.0 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined the trilogy (CW 12, 13, 14), Aion to b-cw9ii-7, CW 9i to
  b-cw9i-10, and CW 8 to b-cw8-14 (2026-08-28): five volumes end to end.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} merged batches, all on the [ledger](/ledger); {{normalized}}
  relations normalized, the verbatim string frozen beside each.
- Families: {{assigned}} assigned, {{pending}} queued, {{no_family}} no
  family, {{text_undecided}} text undecided ([families](/families)).
- Found the clause-predicate defect at b-cw12-1 ({{clause_edges}} relations
  with a proposition in the predicate), traced it to a briefing bullet, and
  replaced the bullet with a form rule at b-cw9ii-3; every blind batch since
  ran at 0%. No re-mine: the relations are verified true and carry the
  normalization layer; reuse per window is in `pipeline/transfer_trend.jsonl`.

### governance

- Moved the ruleset to {{ruleset}}, {{families}} families; every version
  carries a PASS record and `tools/check_paper_facts.py` refuses one
  without it.
- Re-ran every `amplified-by` edge under ruling 1; `amplification` now holds
  none; [the page](/family-amplification) carries the count.
- Declared {{declarations_active}} inverse and symmetric pairs, each citing
  its ruleset line.
- Calibrated the family gate: {{cal_caught}}/{{cal_planted}} planted errors
  caught, {{cal_clean}}/{{cal_clean_of}} clean left alone. Gate model
  {{gate_model}}: within-vendor role separation, not cross-vendor.
- Checked {{ev_items}} assignments against {{ev_works}} works:
  {{ev_agrees}}/{{ev_treated}} treated agreed, {{ev_disagrees}} disagreed,
  {{ev_split}} split; {{ev_rulings}} rules changed. Receipts in
  `docs/experiments/external_validity_2026-08/`.
- Withdrew four reviewer citations (one held) and the pre-August
  calibration figures; flagged b-cw9ii-1 vs b-cw9ii-2 as confounded.
- Added release checkpoints: ledger freshness, batch manifest, size budget, the
  copy contract, and the poster fact check, `tools/check_poster_facts.py`
  (the image's numbers are pixels; preflight compares its sidecar to
  seed.json).

### core build

- Launched on Cloudflare Pages 2026-08-07; extensionless URLs 2026-08-10;
  deterministic generators; emitted [/graph.json](/graph.json), the
  declarations, the batch manifest, the family map and the ontology scan.
- Shipped the query engine (`tools/query/kg_query.py`, read-only) with
  read-time closure and the Turtle export; no transitivity anywhere.

### UI

- Added [releases](/releases), [ontology](/ontology), [query](/query), a page
  per family and per batch; facets, permalinks and the assignment-history
  chip on the ledger; the taxonomy and rules V2-R7 to V2-R13 in
  `docs/ATLAS_REQUIREMENTS.md`.
- Added [in a nutshell](/nutshell), the method poster on its own page; the
  identity walk stays in `kg_query.py`, not exposed on the site.

## v2.1.0: CW 11 and the atlas as an instrument

status: released 2026-10-23. Tag `v2.1.0`, GitHub Release, Zenodo record
under the concept DOI. *Trust, Layered* still describes v2.0.0 and stays
pinned to that tag.
pin: graph v2.1.0 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined CW 11, *Psychology and Religion: West and East*, end to end:
  fourteen windows, paragraphs 1 to 1018.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} batches; {{pending}} relations await adjudication at arc end.
- Mining stops at CW 11, with CW 5 and CW 16 on hold. The mining track
  commits data and the build track deploys; preflight's count checks keep
  the two in step.

### governance

- The poster re-renders at each deploy with live counts and a dated caption.
- The legal statement's figures come from the graph at the tag.
- A citation file joins the repository, and the integrity check is green
  again; contributing and security files added.
- Batch pages fold the mining log; the ledger states the classification
  note once instead of on every card.
- Two reader-raised items from issue 2 are on the backlog: mining around
  quotations, and an editorial layer for connections Jung never states.

### core build

- A `quote contains` search in the query CLI and its browser port, over the
  graph's own quotes only, with parity tests.
- The maintainer's rewrite of every page carried into the generators, with
  a humanizer pass.
- The root is a landing page for the reader; the atlas moved to
  [/atlas](/atlas), and old links forward to it.
- The colour token table gained a day block; the atlas reads its canvas
  colours from it live.

### UI

- New: the ranked [concepts](/concepts) index, concept dossiers,
  [routes](/routes) between any two concepts, a [support](/support) page,
  an [about](/about) page.
- A day theme with a reader toggle; night is warmer and softer.
- Orientation for first visits: quote search on the query page, a pairs
  count, full list and lens filter on the concordance, zoom buttons and keys
  and a core view on the atlas, larger node targets when zoomed out.
- The footer navigation is gone; `routes` and `support` joined the menu.
