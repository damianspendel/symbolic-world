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

## v1.4 — the alchemical trilogy, with the relation-family layer

status: pending — the ceremony waits on the arXiv publication of the paper
pin: graph v1.4 · ruleset {{ruleset}} · calibration record {{calibration_record}} (PASS)

### the graph

- CW 12, 13 and 14 mined end to end, with Aion and CW 9i closed after them:
  {{nodes}} nodes, {{edges}} edges and {{refs}} references over {{batches}}
  merged batch entries, each reference carrying a verbatim quote and the
  paragraph it came from.
- Relation strings normalized on {{normalized}} edges. The verbatim string stays
  frozen beside the normalized one, and the family layer classifies the
  normalized form where it exists.
- The family layer covers the graph: {{assigned}} assigned, {{pending}} waiting
  on a human ruling, {{no_family}} that no family covers, {{text_undecided}}
  where the sentence itself hedges. An assignment classifies a relation that was
  already gated against its paragraph. It is not a second verification, and
  nothing on this site calls a family verified.

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

- The external-validity check closed over {{ev_passes}} passes against
  {{ev_works}} works of secondary scholarship. Of {{ev_treated}} sampled
  assignments the literature treats, scholars' renderings agreed with our family
  on {{ev_agrees}}, disagreed on {{ev_disagrees}} and split among themselves on
  {{ev_split}}; {{ev_not_treated}} pairs no consulted work treats at all.
- {{ev_treated}} treated pairs is a small sample, and agreement there is not
  endorsement: no scholar reviewed this vocabulary. The disagreements produced
  {{ev_rulings}} rule changes and are published beside the agreements, family by
  family.

### corrected or withdrawn

- Four treatments supplied by a reviewing model in the check's first pass were
  put to the actual texts: one held, one was retracted, and two named headwords
  the source does not contain. None entered the headline rates. They are named
  here because they appeared in a draft that was circulated.
- Calibration figures published before August 2026 were withdrawn when a code
  inspection found they could not be substantiated. The sections that carried
  them stand in the definitions document as a record of what was done, not as
  current evidence.

## v1.5 — Aion, and the vocabulary-transfer study

status: skeleton — populated at the ceremony from the batch deltas and whichever
calibration record is binding then
pin: graph v1.5 · ruleset pending · calibration record pending

### the graph

- Placeholder. The four headings above are the shape every entry takes.

## v2.0 — the graph as a queryable instrument

status: skeleton — populated at the ceremony
pin: graph v2.0 · ruleset pending · calibration record pending

### the graph

- Placeholder. Planned: CW 8 mined; the query layer with its declared inverses
  and the Turtle export; the family layer under a stable ruleset with the queue
  drained to ruled-or-recorded; the depth-bounded identity walk. No
  natural-language interface — a query layer that cites edges comes before any
  interface that paraphrases them.
