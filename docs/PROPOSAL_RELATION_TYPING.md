# Proposal: a relation-family layer, retrofitted without touching the verified layer

Status: proposal, 2026-07-30. For the post-submission roadmap (paper §8 names this
as the planned fix). Written on the mining-away branch; publication with the rest
of the branch, at the return review's discretion.

## The problem, with numbers

The relation vocabulary is open and verbatim-faithful by design: an edge's relation
quotes the text's own verb ("is-in-boehme-a-concept-for", "means-concentration-on").
That is a provenance feature and a queryability cost. Current state (branch):
**287 distinct relation strings over 692 edges; 233 used exactly once.** The head is
concentrated — symbolizes (81), corresponds-to (50), amplified-by (43), synonym-of
(22) — and the tail grows roughly linearly with mining, because each new window's
prose mints its own verbs. A reader who wants "every identity claim about Mercurius"
today must know, or guess, a dozen relation spellings. The paper states this gap
honestly (§8: "unevaluated at query level"); this proposal is the fix.

## The one constraint everything follows from

**The verbatim relation is part of the verified claim.** It passed the structure
gate as-worded; renaming it would invalidate the stamp and force re-gating of the
whole graph. So typing must be a **layer above**, never an edit below:

- `relation` — verbatim, frozen, gate-verified. Untouched forever.
- `relation_family` — new field, closed vocabulary (target: 15–25 families),
  assigned later, carrying its own provenance.

Nothing about the existing trust chain changes; the family layer gets its own.

## Family vocabulary: derived from the data, not invented

Families are proposed bottom-up from the actual 287 strings (lexical + embedding
clustering over relation strings with their edge contexts), then named and bounded
by hand. Expected shape, from eyeballing the head: identity/equivalence (is,
is-identical-with, synonym-of), symbolization (symbolizes, stands-for, personifies,
is-image-of), correspondence/parallel (corresponds-to, is-analogue-of, has-parallel-in),
amplification (amplified-by), composition (composed-of, contains), transformation
(transforms-into, renewed-as), sequence (precedes), attribution/derivation, scoped-
doctrine (the is-in-X-a-Y family). An explicit **`unclassified`** family is allowed
and reported — forcing every string into a family is how distinct meanings get
silently merged.

The mapping (relation string → family) is published as a table in the repo, one row
per string, each row carrying who assigned it and when — the same anatomy as a
reference. Readers can dispute a mapping through the existing channel.

## Assignment pipeline — the same gates, pointed at a new layer

1. **Propose**: one batched model pass assigns a family per relation string
   (string + 3 sample edges with quotes as context).
2. **Gate**: an independent model family reviews every mapping row
   (agree / disagree-with-correction), full-table because the table is small.
3. **Cross-vendor**: Gemini re-judges a stratified sample of mappings.
4. **Human anchor**: a gold-set-style pass — stratified over families, the
   annotator sees string + sample edges and picks the family cold (unanchored
   tool mode, learned the hard way).
5. **CI**: tests enforce the closed enum, one family per edge, no orphan mapping
   rows, and the published family counts; the facts checker pins whatever numbers
   any doc claims about families.

Per-batch afterwards: the miner proposes `relation_family` at mint time (the
vocabulary then exists to choose from), and the structure gate checks it as an
eighth judgment — marginal cost near zero.

## Evaluation — closing the §8 gap, not just decorating the schema

Define ~20 benchmark queries a reader actually asks ("all identity claims about
mercurius", "everything the self transforms into", "all scoped-doctrine claims
sourced to Böhme"). Measure retrieval with relation-string matching vs family
matching. That difference is the measured value of the layer, reportable as **E11**
with the usual design: seeded mis-familied edges to calibrate whatever gate checks
families, catch rates with intervals, adjudications published. No headline without
a calibrated instrument behind it.

## Timing: why later is genuinely better, not deferral

- Family vocabularies stabilize as string growth flattens; typing now means
  re-clustering after every tranche. One backfill after the current mining arc
  (CW 12 complete + CW 9ii started) types ~300 strings once.
- The gold-set finding applies directly: the human pass on mappings should be
  unanchored from day one, and a second annotator can take the mapping table and
  the voice gold set in one sitting.
- Paper impact is post-freeze by construction: a v1.4 section plus E11, with the
  frozen v1.3.0 untouched.

## Cost envelope

| Step | Estimate |
|---|---|
| Clustering + proposal pass (~300 strings, batched) | ≈ $2–4 |
| Gate review of full table | ≈ $2–3 |
| Cross-vendor sample | < $0.50 |
| Human pass | author time, ~1–2 h (≈60-row stratified sample) |
| Per-batch marginal thereafter | cents |
| E11 evaluation runs | ≈ $3–5 |

Total ≈ $10 of API spend plus one short human session — cheaper than any single
hostile review round, for the artifact's largest unaddressed usability gap.

## Risks, named

- **Over-collapse** — distinct meanings merged into one family. Mitigations: the
  `unclassified` escape valve, dispute channel on mapping rows, and the rule that
  a family split is always allowed but a merge of established families needs
  re-gating of affected rows.
- **Layer drift** — new mining mints strings faster than they get familied.
  Mitigation: CI fails when any edge lacks a family once the layer ships (same
  fail-closed pattern as verification).
- **Silent semantics creep** — family definitions shifting between releases.
  Mitigation: the family vocabulary is versioned with the dataset releases, and
  the mapping table is release-stamped like everything else.
