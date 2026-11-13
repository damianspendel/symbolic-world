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

The paper, *Trust, Layered*, describes v2.0.0.

Each entry opens with the graph version, the ruleset version it shipped with
(the two are deliberately separate numbers) and the calibration record in force
when the release was cut.

## v2.4.0: the alchemical trilogy, mined a second time

status: in preparation. Tag `v2.4.0`, GitHub Release and Zenodo record under
the concept DOI once released.
pin: graph v2.4.0 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined CW 12, 13 and 14 a second time, in 26 windows of seventy
  paragraphs. The first pass predates the form rule and the reporting clause.
- References name their source author and text; nodes carry their Latin
  form and aliases. The stages of the work are in the graph as data.
- Quotations have a cap of 9% per volume.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} batches; {{pending}} relations await adjudication.

### governance

- The RDF export is rebuilt, and its VoID files name the site's Turtle
  files as their data dump.
- Three subtitles that went live after the v2.3.0 tag reach the repository.

### core build

- [/opus](/opus) replaces the concordance in the menu. The
  [concordance](/atlas#/concordance) stays, with the new terms.
- The atlas size ceiling is 6.0 MB.

### UI

- [/opus](/opus) follows Jung's reading of the ten woodcuts of the
  *Rosarium philosophorum* in CW 16, from Jung's own copy on e-rara.ch. A
  tile under each picture gathers what he says of the same figures across
  the trilogy, and [/opus-claims](/opus-claims) lists every such claim.
- [/query](/query) suggests concepts and relations as you type.
- [/method](/method) says "Validated by a person" and adds a row on recall.

## v2.3.0: CW 16, CW 7 and CW 6

status: released 2026-11-11. Tag `v2.3.0`, GitHub Release, Zenodo record
under the concept DOI.
pin: graph v2.3.0 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined three arcs end to end since v2.2.0: CW 16, *The Practice of
  Psychotherapy*; CW 7, *Two Essays on Analytical Psychology*; and CW 6,
  *Psychological Types*, chapters X and XI, paragraphs 556 to 844.
- An outside audit covered the trilogy references that had never had one; its
  findings changed three claim types and lowered one confidence.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} batches; {{pending}} relations await adjudication.
- Mining pauses until the rulings for a second pass over CW 12, 13 and 14
  are in.

### governance

- w3id.org registered the symbolicworld namespace (perma-id pull
  request 7091).
- Three names in the RDF export that repeated a quote are shorter.

### core build

- The site serves the RDF export: graph, ontology and VoID as Turtle
  under CC BY 4.0, with no quotations. Every build regenerates it, the
  release commits a copy to the repository, and preflight refuses a quotes
  file.
- `/nutshell` forwards to [/method](/method); the method poster left the site.

### UI

- [/evidence](/evidence) in three groups: how the checks work, design, data.
- The [concordance](/atlas#/concordance) and [support](/support) are back in the menu.
- Method links go to /method, and the design page has one name,
  "The design".

## v1.3.0: the published baseline

status: released and frozen. Retrospective.
pin: graph v1.3.0 · ruleset none (the family layer did not exist yet) ·
calibration record none

### mining status

- Mined CW 14 with seven incidental volumes: {{frozen_nodes}} nodes,
  {{frozen_edges}} relations, {{frozen_refs}} references.
- Ran at 0 to 0.5% clause predicates; this material predates the windowed pipeline.

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
  b-cw9i-10, and CW 8 to b-cw8-14 (2026-08-28): six volumes end to end.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} merged batches, all on the [ledger](/ledger); {{normalized}}
  relations normalized, the verbatim string frozen beside each.
- Families: {{assigned}} assigned, {{pending}} queued, {{no_family}} no
  family, {{text_undecided}} text undecided ([families](/families)).
- Found the clause-predicate defect in the first CW 12 batch, b-cw12-1:
  {{clause_edges}} relations whose predicate held a whole proposition. One
  line of the mining brief caused it. A form rule replaced that line at
  b-cw9ii-3, and no batch since has shown the defect.
- We kept the affected relations. Each had passed its check, and the
  normalization layer records a short form beside the original.

### governance

- Moved the ruleset to {{ruleset}}, {{families}} families; every version
  carries a PASS record and `tools/check_paper_facts.py` refuses one
  without it.
- Re-ran every `amplified-by` edge under ruling 1; `amplification` now holds
  none; [the page](/family-amplification) carries the count.
- Declared {{declarations_active}} inverse and symmetric pairs, each citing
  its ruleset line.
- Calibrated the family gate: {{cal_caught}}/{{cal_planted}} planted errors
  caught, {{cal_clean}}/{{cal_clean_of}} clean left alone. The gate is a
  Gemini model ({{gate_model}}), as is one of the two classifying models: they
  share a vendor and differ only in role.
- Checked {{ev_items}} assignments against {{ev_works}} works:
  {{ev_agrees}}/{{ev_treated}} treated agreed, {{ev_disagrees}} disagreed,
  {{ev_split}} split; {{ev_rulings}} rules changed. Receipts in
  `docs/experiments/external_validity_2026-08/`.
- Withdrew the calibration figures from before August, which the original
  harness could not support. Marked the comparison of the first two *Aion*
  batches as confounded: the first miner was watched and the second ran
  blind.
- Added release checks: ledger freshness, the batch manifest, the size budget,
  the copy contract, and a check of the poster's numbers against the graph.

### core build

- Launched on Cloudflare Pages 2026-08-07; emitted [/graph.json](/graph.json),
  the declarations, the batch manifest, the family map and the ontology scan.
- Shipped the query engine (`tools/query/kg_query.py`, read-only) with
  read-time closure and the Turtle export; no transitivity anywhere.

### UI

- Added [releases](/releases), [ontology](/ontology), [query](/query), a page
  per family and per batch; facets, permalinks and the assignment-history
  chip on the ledger.
- Added in a nutshell, the method poster on its own page (retired on
  2026-11-11, and `/nutshell` now redirects to `/method`).

## v2.1.0: CW 11 and the atlas as an instrument

status: released 2026-10-23. Tag `v2.1.0`, GitHub Release, Zenodo record
under the concept DOI.
pin: graph v2.1.0 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined CW 11, *Psychology and Religion: West and East*, end to end:
  fourteen windows, paragraphs 1 to 1018.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} batches; {{pending}} relations awaited adjudication when mining
  finished the volume.
- Mining stops at CW 11, with CW 5 and CW 16 on hold.

### governance

- The poster re-renders at each deploy with live counts and a dated caption.
- The legal statement's figures come from the graph at the tag.
- A citation file joins the repository, and the integrity check is green
  again; contributing and security files added.
- Two reader-raised items from issue 2 are on the backlog: mining around
  quotations, and an editorial layer for connections Jung never states.

### core build

- A `quote contains` search in the query CLI and its browser port, over the
  graph's own quotes only, with parity tests.
- The maintainer's rewrite of every page carried into the generators.
- The root is a landing page for the reader; the atlas moved to
  [/atlas](/atlas), and old links forward to it.

### UI

- New: the ranked [concepts](/concepts) index, concept dossiers,
  [routes](/routes) between any two concepts, a [support](/support) page,
  an [about](/about) page.
- A day theme with a reader toggle; night is warmer and softer.
- Orientation for first visits: quote search on the query page, a pairs
  count, full list and lens filter on the concordance, zoom buttons and keys
  and a core view on the atlas, larger node targets when zoomed out.
- The footer navigation is gone; `routes` and `support` joined the menu.

## v2.2.0: CW 5, *Symbols of Transformation*

status: released 2026-10-31. Tag `v2.2.0`, GitHub Release, Zenodo record
under the concept DOI.
pin: graph v2.2.0 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Mined CW 5, *Symbols of Transformation*, end to end: ten windows,
  paragraphs 1 to 685.
- Graph: {{nodes}} nodes, {{edges}} relations, {{refs}} references over
  {{batches}} batches; {{pending}} relations await adjudication.
- One CW 11 reference, to paragraph 960, waited for a ruling after the auditor
  objected to its ellipsis. A Fable-family ruling upheld it and lowered its
  confidence from high to medium.
- Mining resumes with CW 16, one window nightly.

### governance

- A standing rule on what goes public: the repository tracks only the
  published artifact, and a release push needs the history audit and
  approval of the files added since the last tag.
- Sixteen working notes, superseded plans and unused figures left the
  tracked tree.
- NOTICE names a contact for removal requests.

### core build

- The deploy check sets aside Cloudflare's analytics beacon and email
  encoding before it compares the live site with the build.

### UI

- Concept pages link to the atlas, and a concept selected on the atlas links
  back to its page.
- The about page ends with a contact line for concerns.
