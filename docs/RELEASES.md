# Releases

What changed between one release of the graph and the next, and why. The ledger
records every individual claim and the gates it passed; this page records the
release-level story.

Every entry has the same four sections in the same order — **mining status**,
**governance**, **core build**, **UI** — so two releases can be read against
each other line for line.

Every entry opens with a version pin. A graph release and a ruleset version are
deliberately separate numbers — a release *pins* the ruleset it ships with
rather than sharing its number — and the pin names the calibration record that
was binding at tag time.

**Pointers.** Artifacts inside the repository are named as repo-relative paths
in `code formatting`: the repository is not public until the release ceremony,
so they
are paths today and become links when it is. Pages on the site are given as real
links, extensionless by the site's own convention.

This file carries no typed figure. Counts are written as named tokens in double
braces and bound from the graph, the calibration records and the committed
experiment receipts by `web/build-atlas.mjs`; a token the build cannot bind
fails the build rather than shipping as literal braces.

## v1.4 — the alchemical trilogy, the archetype volumes, and the relation-family layer

status: pending — the ceremony waits on the arXiv publication of the paper. The
ruleset in the pin is whichever version is binding at tag time; {{ruleset}} is
binding today, and the v0.7.x line is still moving. Scope note: the plan of
2026-08-05 put Aion and the archetype volumes in v1.5 and kept v1.4 to the
trilogy. The arcs closed faster than the ceremony did, so this entry describes
the graph as it stands rather than the plan as it was written, and v1.5 is
re-scoped to the study the arcs were mined for.
pin: graph v1.4 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### mining status

- Five arcs mined end to end since v1.3.0: *Psychology and Alchemy* (CW 12),
  *Alchemical Studies* (CW 13) and *Mysterium Coniunctionis* (CW 14) complete the
  alchemical trilogy; *Aion* (CW 9ii §1–429) closed on 2026-08-06 with
  b-cw9ii-7; *The Archetypes and the Collective Unconscious* (CW 9i §1–718)
  closed on 2026-08-12 with b-cw9i-10, ten windows, every reference proposed by
  an Opus-family model, gated by a Fable-family model and audited across vendors
  by Gemini.
- {{nodes}} nodes, {{edges}} edges and {{refs}} references over {{batches}}
  merged batch entries. Every reference carries a verbatim quote of at most 25
  tokens and the paragraph it came from; each batch's own account of what it
  merged is on its delta page, and every claim is on the [ledger](/ledger).
- CW 9i was mined as the transfer study's falsification volume: archetype theory
  without alchemical carriers, against a graph in which a large share of nodes
  had rested on the trilogy alone. What that did to the evidence mix is on each
  node's panel in the atlas, not summarised into a claim here.
- Relation strings normalized on {{normalized}} edges. The verbatim string stays
  frozen beside the normalized one, and the family layer classifies the
  normalized form where it exists.
- The family layer covers the graph: {{assigned}} assigned, {{pending}} waiting
  on a human ruling, {{no_family}} that no family covers, {{text_undecided}}
  where the sentence itself hedges. An assignment classifies a relation that was
  already gated against its paragraph. It is not a second verification, and
  nothing on this site calls a family verified. Family by family:
  [relation families](/families).
- **Defect found in the pipeline: the clause-predicate shape.** The windowed pipeline
  built after v1.3.0 shipped carried no rule about the *shape* of a relation.
  Every gate asked whether the paragraph supported the claim; none asked whether
  the predicate was a predicate. The result was {{clause_edges}} relations whose
  predicate carries a whole proposition — found, named and measured on
  2026-08-05, starting exactly at b-cw12-1.
- The mechanism was a line in the miner's own standing briefing instructing that
  qualifiers stay inside the relation string. A watched batch tidied its
  relations in spite of it; the blind b-cw9ii-2 followed it literally and came
  back at 77% clause predicates. That is a defect that propagated through the
  instruction channel, not through the model.
- **Remediation.** The bullet was replaced with a form rule — the relation is a
  verb phrase of at most three hyphen tokens; carrier, scope, condition and
  modality belong in qualifiers or the object. b-cw9ii-3 was the test, and every
  blind batch since has run at 0% clause predicates: fifteen consecutive by the
  close of CW 9i on 2026-08-12. The affected relations were not re-mined — each
  is individually verified and true, the shape is wrong and not the fact — so
  they carry a normalization layer beside the frozen original, proposed, gated
  and sampled through the same chain as any other claim.

### governance

- `docs/FAMILY_DEFINITIONS.md` reached {{ruleset}}, holding {{families}}
  families. The version is binding only while a calibration PASS record for it
  is committed under `pipeline/family_calibration/records/`; the
  version↔calibration handshake in `tools/check_paper_facts.py` refuses a
  version without one.
- The re-run of the `amplified-by` edges under ruling 1 classified those
  relations by the content of their quotes rather than by the layer tag they
  carried. Where the amplification family now stands is on
  [its own page](/family-amplification), count included, whatever that count has
  become.
- {{declarations_active}} relation declarations are active — inverse and
  symmetric pairs, each transcribed from a line of the definitions document into
  `pipeline/family/relation_declarations.json` and applied at read time only. No
  declaration asserts transitivity. The rulings behind them, and what the
  ontology deliberately does not contain, are on [the ontology page](/ontology).
- The family gate was re-calibrated against planted errors under {{ruleset}}:
  {{cal_caught}} of {{cal_planted}} planted errors caught with the right family
  named, {{cal_clean}} of {{cal_clean_of}} untouched assignments left alone
  (`{{calibration_record}}`). A caught planted error is evidence about the
  instrument, not about Jung, and the record covers only the error classes we
  know how to plant. The gate model is {{gate_model}} — the same model family as
  one of the two production classification arms, which is within-vendor role
  separation and not a cross-vendor check, and the record says so.
- The external-validity check closed on 2026-08-12 over {{ev_passes}} passes
  against {{ev_works}} works of secondary scholarship. Of {{ev_treated}} sampled
  assignments the literature treats, scholars' renderings agreed with our family
  on {{ev_agrees}}, disagreed on {{ev_disagrees}} and split among themselves on
  {{ev_split}}; {{ev_not_treated}} pairs no consulted work treats at all.
  {{ev_treated}} treated pairs is a small sample, and agreement there is not
  endorsement: no scholar reviewed this vocabulary. The disagreements produced
  {{ev_rulings}} rule changes and are published beside the agreements, family by
  family. Sample, per-item worksheets and both review passes:
  `docs/experiments/external_validity_2026-08/`.
- CI gates in force at this release, all in `tools/check_paper_facts.py` unless
  named otherwise: paper counts pinned to the `v1.3.0` tag and living-doc counts
  to head; the version↔calibration handshake above; five family checks; the
  ledger-freshness gate and the batch-manifest gate in
  `tools/pages/preflight.py`; and the copy contract in `web/build-atlas.mjs`,
  which fails the build on a count-like literal that the graph cannot account
  for. Rules are registered in `docs/RULES.md`.
- **Corrected or withdrawn.** Four treatments supplied by a reviewing model in
  the external check's first pass were put to the actual texts: one held, one
  was retracted, and two named headwords the source does not contain. None
  entered the headline rates; they are named here because they appeared in a
  draft that was circulated. Calibration figures published before August 2026
  were withdrawn when a code inspection found they could not be substantiated —
  the sections that carried them stand in the definitions document as a record
  of what was done, not as current evidence. And the b-cw9ii-1 / b-cw9ii-2
  comparison is confounded: the blinding of the miner changed between them, so
  the pair is not clean evidence about the material, and the 77% above is what
  that batch did rather than a measurement of anything else.

### core build

- The site went live on Cloudflare Pages on 2026-08-07 at
  symbolicworld.observer, with the frozen v1.3.0 snapshot preserved at
  [/v1.3/](/v1.3/) and linked from the landing page, since the paper describes
  that release and not this one. Runbook: `tools/pages/RUNBOOK.md`.
- Public URLs are extensionless by convention from 2026-08-10; the sitemap, the
  canonical tags and every internal link agree on that form.
- The generators are deterministic: the same graph in gives the same bytes out,
  so a real change is not buried in churn. `web/build-atlas.mjs` writes the
  atlas projection, the family map, the pages and the sitemap;
  `tools/build_ledger_page.py` writes the ledger and one delta page per batch in
  the same pass.
- Data artifacts emitted at build: the public dataset at
  [/graph.json](/graph.json), the declarations at
  `web/public/relation_declarations.json`, the batch-page manifest at
  `web/public/batch_pages.json` (which the deploy gate reads), the derived
  string-to-family map, and the ontology scan's JSON from
  `tools/ontology_qa/quality.py --json`.
- Tools, read-only and shipping with the release: `tools/query/kg_query.py` (the
  query engine — writes nothing, labels every derived row, prints the graph
  state and seed digest it ran against) and `tools/query/export_rdf.py` (the
  Turtle export, which declares no transitivity).

### UI

- Pages added in this release: [release notes](/releases), a page per relation
  family, a page per batch, the [query panel](/query) and
  [the ontology page](/ontology). The [ledger](/ledger) gained facets, record
  permalinks and an assignment-history chip; the batch narrative moved off it
  onto the per-batch pages.
- Design rules adopted, all in the V2 section of `docs/ATLAS_REQUIREMENTS.md`:
  one site menu with a fixed taxonomy (V2-R10), a pinned header with constant
  geometry (V2-R11), one title band and one search position (V2-R12), two
  content-column kinds that do not wander (V2-R13), progressive disclosure on
  heavy pages (V2-R9), volumes in collection order (V2-R8), and per-batch delta
  pages (V2-R7).
- Deliberately not exposed: the depth-bounded identity walk. It is built and
  tested in `tools/query/kg_query.py` and documented in `docs/QUERY.md`, and it
  is kept for later rather than shipped in this release's UI.
- Nothing in this set is deployed by the build that made it. A deploy carrying
  UI waits for review.

## v1.5 — the vocabulary-transfer study

status: skeleton — populated at the ceremony from the batch deltas and whichever
calibration record is binding then. Re-scoped: the arcs it was to carry closed
into v1.4, and what remains is the question they were mined to answer — whether
the relation vocabulary learned on the alchemical volumes transfers to archetype
theory written without alchemical carriers.
pin: graph v1.5 · ruleset pending · calibration record pending

### mining status

- Placeholder.

### governance

- Placeholder.

### core build

- Placeholder.

### UI

- Placeholder.

## v2.0 — the graph as a queryable instrument

status: skeleton — populated at the ceremony
pin: graph v2.0 · ruleset pending · calibration record pending

### mining status

- Planned: CW 8 mined.

### governance

- Planned: the family layer under a stable ruleset with the queue drained to
  ruled-or-recorded.

### core build

- Planned: the query layer with its declared inverses and the Turtle export as
  published artifacts rather than tools alone.

### UI

- Planned: the surfaces that the query layer earns. The depth-bounded identity
  walk is built and tested in `tools/query/kg_query.py` and is kept for later:
  it is not exposed in the site UI, and exposing it is a decision for a later
  release. No natural-language interface — a query layer that cites edges comes
  before any interface that paraphrases them.

## v1.3.0 — the published baseline

status: released, and frozen. This entry is a retrospective, written in the same
shape as the entries above so the baseline can be read against them. The
snapshot it describes is preserved byte-for-byte and is never rebuilt.
pin: graph v1.3.0 · ruleset none — the relation-family layer did not exist yet ·
calibration record none

### mining status

- {{frozen_nodes}} nodes, {{frozen_edges}} edges and {{frozen_refs}} references:
  CW 14 mined with seven incidental volumes around it, every reference proposed
  by one model family and gated by another against its own paragraph.
- The clause-predicate defect had not yet appeared: this material predates the
  windowed pipeline that introduced it, and ran at 0–0.5% clause predicates.

### governance

- The verification chain and its provenance disclosure are stated in
  `docs/PAPER.md`, which describes this release and no later one.
- Counts are pinned to the `v1.3.0` tag by `tools/check_paper_facts.py`, which
  is why they can be bound here as constants rather than derived: the paper's
  assertions and the live graph are checked against different baselines on
  purpose.

### core build

- Released to Zenodo under the concept DOI
  [10.5281/zenodo.21631523](https://doi.org/10.5281/zenodo.21631523), which
  resolves to the latest release; the record for this one is fixed.
- The snapshot — atlas, ledger, dispute log and dataset as they stood — is
  served at [/v1.3/](/v1.3/) and is never written by any generator.

### UI

- The atlas as it was at publication, with its own ledger and dispute log. Every
  surface added since is described in the entries above; none of them touch this
  snapshot.
