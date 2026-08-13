# Releases

What changed between one release of the graph and the next, and why. The ledger
records every individual claim and the gates it passed; this file records the
release-level story: the graph, the ruleset, the instruments, what was checked
outside this repository, and what was corrected or withdrawn.

Every entry opens with a version pin. A graph release and a ruleset version are
deliberately separate numbers — a release *pins* the ruleset it ships with
rather than sharing its number — and the pin names the calibration record that
was binding at tag time.

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

### the graph

- Five arcs mined end to end since v1.3.0: *Psychology and Alchemy* (CW 12),
  *Alchemical Studies* (CW 13) and *Mysterium Coniunctionis* (CW 14) complete the
  alchemical trilogy; *Aion* (CW 9ii §1–429) closed on 2026-08-06 with
  b-cw9ii-7; *The Archetypes and the Collective Unconscious* (CW 9i §1–718)
  closed on 2026-08-12 with b-cw9i-10, ten windows, every reference proposed by
  an Opus-family model, gated by a Fable-family model and audited across vendors
  by Gemini.
- {{nodes}} nodes, {{edges}} edges and {{refs}} references over {{batches}}
  merged batch entries. Every reference carries a verbatim quote of at most 25
  tokens and the paragraph it came from; the per-batch pages carry each batch's
  own account of what it merged.
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
  nothing on this site calls a family verified.

### the clause-predicate defect, and the form rule

- The windowed pipeline built after v1.3.0 shipped carried no rule about the
  *shape* of a relation. Every gate asked whether the paragraph supported the
  claim; none asked whether the predicate was a predicate. The result was
  {{clause_edges}} relations whose predicate carries a whole proposition —
  found, named and measured on 2026-08-05, starting exactly at b-cw12-1.
- The mechanism was a line in the miner's own standing briefing instructing that
  qualifiers stay inside the relation string. A watched batch tidied its
  relations in spite of it; the blind b-cw9ii-2 followed it literally and came
  back at 77% clause predicates. That is a defect that propagated through the
  instruction channel, not through the model.
- The bullet was replaced with a form rule — the relation is a verb phrase of at
  most three hyphen tokens; carrier, scope, condition and modality belong in
  qualifiers or the object. b-cw9ii-3 was the test, and every blind batch since
  has run at 0% clause predicates: fifteen consecutive by the close of CW 9i on
  2026-08-12.
- The affected relations were not re-mined. Each is individually verified and
  true — the shape is wrong, not the fact — so they carry a normalization layer
  beside the frozen original instead, proposed, gated and sampled through the
  same chain as any other claim.

### ruleset

- `docs/FAMILY_DEFINITIONS.md` reached {{ruleset}}, holding {{families}}
  families. The version is binding only while a calibration PASS record for it
  is committed; CI refuses a version without one.
- The re-run of the `amplified-by` edges under ruling 1 classified those
  relations by the content of their quotes rather than by the layer tag they
  carried. Where the amplification family now stands is on its own page, count
  included, whatever that count has become.
- {{declarations_active}} relation declarations are active — inverse and
  symmetric pairs, each transcribed from a line of the definitions document and
  applied at read time only. No declaration asserts transitivity.

### instruments and calibration

- The family gate was re-calibrated against planted errors under {{ruleset}}:
  {{cal_caught}} of {{cal_planted}} planted errors caught with the right family
  named, {{cal_clean}} of {{cal_clean_of}} untouched assignments left alone. A
  caught planted error is evidence about the instrument, not about Jung, and the
  record covers only the error classes we know how to plant.
- The gate model is {{gate_model}} — the same model family as one of the two
  production classification arms. That is within-vendor role separation, not a
  cross-vendor check, and the record says so.
- `tools/query/kg_query.py` ships read-only. It writes nothing, labels every
  derived row, and prints the graph state and seed digest it ran against.

### checked outside the repository

- The external-validity check closed on 2026-08-12 over {{ev_passes}} passes
  against {{ev_works}} works of secondary scholarship. Of {{ev_treated}} sampled
  assignments the literature treats, scholars' renderings agreed with our family
  on {{ev_agrees}}, disagreed on {{ev_disagrees}} and split among themselves on
  {{ev_split}}; {{ev_not_treated}} pairs no consulted work treats at all.
- {{ev_treated}} treated pairs is a small sample, and agreement there is not
  endorsement: no scholar reviewed this vocabulary. The disagreements produced
  {{ev_rulings}} rule changes and are published beside the agreements, family by
  family. The sample, the per-item worksheets and both review passes are
  committed under `docs/experiments/external_validity_2026-08/`.

### published

- The site went live on Cloudflare Pages on 2026-08-07 at
  symbolicworld.observer: the atlas, the ledger, the dispute log and the
  families document, with the frozen v1.3.0 snapshot preserved at `/v1.3/` and
  linked from the landing page, since the paper describes that release and not
  this one.
- Public URLs are extensionless by convention from 2026-08-10; the sitemap,
  the canonical tags and every internal link agree on that form.
- This release adds the release notes, a page per relation family, a page per
  batch, the query panel and the ontology page. Nothing in that set is deployed
  by the build that made it.

### corrected or withdrawn

- Four treatments supplied by a reviewing model in the check's first pass were
  put to the actual texts: one held, one was retracted, and two named headwords
  the source does not contain. None entered the headline rates. They are named
  here because they appeared in a draft that was circulated.
- Calibration figures published before August 2026 were withdrawn when a code
  inspection found they could not be substantiated. The sections that carried
  them stand in the definitions document as a record of what was done, not as
  current evidence.
- The b-cw9ii-1 and b-cw9ii-2 comparison is confounded: the blinding of the
  miner changed between them, so the pair is not clean evidence about the
  material, and the 77% figure above is reported as what that batch did rather
  than as a measurement of anything else.

## v1.5 — the vocabulary-transfer study

status: skeleton — populated at the ceremony from the batch deltas and whichever
calibration record is binding then. Re-scoped: the arcs it was to carry closed
into v1.4, and what remains is the question they were mined to answer — whether
the relation vocabulary learned on the alchemical volumes transfers to archetype
theory written without alchemical carriers.
pin: graph v1.5 · ruleset pending · calibration record pending

### the graph

- Placeholder. The headings above are the shape every entry takes.

## v2.0 — the graph as a queryable instrument

status: skeleton — populated at the ceremony
pin: graph v2.0 · ruleset pending · calibration record pending

### the graph

- Placeholder. Planned: CW 8 mined; the query layer with its declared inverses
  and the Turtle export; the family layer under a stable ruleset with the queue
  drained to ruled-or-recorded; the depth-bounded identity walk. No
  natural-language interface — a query layer that cites edges comes before any
  interface that paraphrases them.
