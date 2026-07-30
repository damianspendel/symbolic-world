# Proposal: a relation-family layer, retrofitted without touching the verified layer

Status: proposal, updated 2026-07-30 with scholarship grounding, ontology-practice
grounding, and narrative-probe evidence. For the post-submission roadmap (paper §8
names this as the planned fix; scheduled as release v1.5 in docs/ROADMAP.md).
Written on the mining-away branch; publication at the return review's discretion.

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
and reported, WITH a CI ceiling (fail the build above ~10% unclassified) so the
escape valve cannot become a dumping ground — forcing every edge into a family is
how distinct meanings get silently merged, and unbounded escape is how the layer
dies of vagueness; the ceiling holds the tension.

Assignment lives at the EDGE level, not the string level (cross-vendor review
correction, 2026-07-30): relation strings in this corpus are polysemous — "is"
alone spans archetypal identity, categorization, and composition — so a global
string→family table would silently corrupt every polysemous head string. The
string is used only as a clustering heuristic to batch the work; the recorded,
CI-enforced fact is `edge → family`, one row per edge, each row carrying who
assigned it and when — the same anatomy as a reference. A derived string-level
view is published for readability (singletons collapse to it trivially; head
strings show their per-edge split). Readers dispute mappings through the existing
channel. Cost consequence: the gate reviews ~700+ edge assignments, not ~300
strings — the envelope below is revised accordingly.

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


## Grounding I — the discipline's own definitions (research 2026-07-30)

The families must be defined in classical Jungian terms, cited, because the corpus
is classical Jung and the definitions are load-bearing:

- **Symbolization** (Jung, CW 6, Definitions): a symbol is "the best possible
  description or formulation of a relatively unknown fact"; a sign stands for
  something known. The family is therefore *not* semiotic reference — "lapis
  symbolizes the Self" claims best-available-expression of something not otherwise
  formulable.
- **Amplification** (Samuels, Shorter & Plaut, *A Critical Dictionary of Jungian
  Analysis*, pp. 16-17; IAAP): the use of mythic, historical and cultural parallels
  to widen the basis on which an image's interpretation rests — metaphorical, never
  literal. Method-level: it names Jung's interpretive act, not the text's ontology.
  The miners' unprompted use of `amplified-by` matches this definition.
- **Archetypal identity** (Jung's projection thesis; Edinger, *Anatomy of the
  Psyche*): the alchemical "is" asserts one archetype behind both terms, via
  projection into matter — not logical identity. Defining the identity family this
  way also answers the referee objection that the graph asserts literal absurdities.
- **Where "mostly agreed" frays** (recorded, not hidden): the post-Jungian schools
  (Samuels' classical / developmental / archetypal division) dispute amplification's
  epistemic status (Hillman: stay with the image) and symbol theory's literalness.
  Families are defined against classical usage, and the definitions doc says so.

## Grounding II — ontology-practice precedents (research 2026-07-30)

- **The two-tier design is the W3C `rdfs:subPropertyOf` pattern**: verbatim
  relations as leaf properties, families as super-properties; queries over the
  family match the leaves; nothing is renamed. Decades of precedent, name it.
- **OBO Relation Ontology as the primary structural precedent** (cross-vendor
  review correction): RO's state/relation-centric shared vocabulary matches this
  use case; CIDOC-CRM (ISO 21127, ~160 event-centric properties) remains the
  scale lesson (keep families small, 15-25; extensions under the core) and the
  interoperability door, but its event-centric structure is the wrong template
  for symbol-centric relations.
- **Wikidata property governance**: new properties require a proposal with scope
  and constraints, community review, and — the rule worth stealing — the proposer
  may not be the creator. Adding a family here should follow the same shape:
  proposal with definition + seed examples, reviewed by a different model family,
  human sign-off.
- **OBO Relation Ontology** (biology's cure for relation sprawl): vocabularies
  converge only when convergence is enforced by tooling. Hence: CI fails on any
  unfamilied edge once the layer ships (fail-closed, as everywhere).
- **Property characteristics (OWL), used sparingly**: `owl:SymmetricProperty` for
  synonym-of and `owl:inverseOf` for symbolization pairs (symbolizes/symbolized-by
  are currently two unrelated strings). Transitivity is deliberately NOT declared:
  alchemical sequences are cyclical (the uroboros, the Rex cycle), and a transitive
  `precedes` lets an inference engine derive A-precedes-A. (An earlier draft also
  analogized family strength to SKOS match properties; withdrawn on cross-vendor
  review — SKOS match maps concepts across vocabularies, not edge classes within
  one, and the analogy misleads more than it explains.)
- **Prior art for the mapping step**: the NLP literature calls this relation
  canonicalization (clustering surface forms over open-IE output); E11's clustering
  inherits citable methods.

## Family × voice: a testable interaction

Amplification edges should skew jung-asserts (they name Jung's interpretive act);
`synonym-of` edges should skew jung-reports-parallel (they render the alchemists'
own lexicon). Once families exist, this correlation is one query — if it holds, it
is independent evidence that both layers track something real; if it fails, one of
the two layers has a definition problem — with one confound named in advance:
nested reporting (Jung quoting an alchemist who amplifies another alchemist)
legitimately breaks the correlation, so E11 excludes nested-attribution edges
before reading the result. Either way, reportable.

## Evidence from the narrative probes (2026-07-30)

Two probes support the layer's premise that relation semantics carry the graph's
meaning: an unprimed cross-vendor model reconstructed the canonical opus narrative
from labeled triples, and the fully node-anonymized run still produced the Rex
renewal drama from structure plus generic relation verbs alone. The anonymized
run's leak audit (ten relation strings carrying domain vocabulary) also demonstrated
that relation strings are semantically dense — which is the family layer's entire
premise stated as an experimental result. Formalization as E13 (blinding tiers,
leak-scan pass, judge arm) is scheduled with release v1.8.

## Human pass integration (with the HITL backlog items)

The family mapping's human check uses the drip-fed tranche mechanism (small
stratified batches on request, unanchored, progress toward a target n) and the
reviewer-identity provenance planned for the verification log — so family
validations are attributable records like every other human judgment. At v1.6 the
second annotator covers voice gold set and family mapping in one recruited session.

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
| Gate review of edge-level assignments (~700+) | ≈ $8–15 |
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
