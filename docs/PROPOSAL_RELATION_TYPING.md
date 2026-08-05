# Proposal: a relation-family layer, retrofitted without touching the verified layer

**Scope option (2026-07-30, proposed; UNDECIDED — for the return review):** the family vocabulary would be scoped to the
ALCHEMICAL TRILOGY (CW 12/13/14) — "the alchemical corpus's relational ontology,
v1" — not to Jung's works at large. This dissolves the vocabulary-closure objection
from the cross-vendor planning review: the trilogy is a coherent relational world
and closable now. Non-trilogy edges carry an explicit `pending-scope` marker
(distinct from `unclassified`); the fail-closed CI rule applies within declared
scope. Seam rule: when later volumes arrive, families may be ADDED via governance,
but redefining an existing family to absorb new material requires re-gating its
assignments. Aion then becomes a measured vocabulary-transfer study (fraction of
CW 9ii edges classifiable under trilogy families) — generalization measured, not
assumed, mirroring what E8 did for the pipeline.

**Where that fork stands after the second cross-vendor review (2026-08-01).** The
reviewer rejected the trilogy-only scoping a second time, arguing that the 46%
singleton tail proves the alchemical corpus is not a closable relational world even
on its own terms, and that Aion (CW 9ii + 9i) must be mined before the vocabulary
closes. That inference does not hold as stated: 46% measures diversity of *strings*,
and the premise of this entire layer is that many distinct strings collapse into few
families. String sprawl is the problem families solve, not evidence that families
cannot be found. What the reviewer is right about is that nobody has measured
family-level closure at all — the coherence claim for the trilogy rests on argument,
not data. Step 0 of the assignment pipeline settles it empirically: if the human
annotator can place a stratified sample of the singleton tail using the candidate
definitions, the trilogy closes and Aion becomes the transfer study as planned; if
the tail resists classification, the reviewer's sequencing was right and Aion comes
first. The fork stays UNDECIDED, but it is now decidable by a cheap experiment
rather than by two models arguing.

Status: proposal, updated 2026-07-30 with scholarship grounding, ontology-practice
grounding, and narrative-probe evidence; revised 2026-08-01 with the post-trilogy
measurement and the second cross-vendor review. For the post-submission roadmap
(paper §8 names this as the planned fix; scheduled as release v1.5 in
docs/ROADMAP.md). Written on the mining-away branch; publication at the return
review's discretion.

## The problem, with numbers

The relation vocabulary is open and verbatim-faithful by design: an edge's relation
quotes the text's own verb ("is-in-boehme-a-concept-for", "means-concentration-on").
That is a provenance feature and a queryability cost. Current state (branch,
measured 2026-08-01 on the completed trilogy):
**468 distinct relation strings over 880 edges; 409 used exactly once.** Singletons
are now 46% of all edges, up from 34% when this proposal was drafted — the tail
grows faster than the graph. The head is thin: the top twelve strings — symbolizes
(81), corresponds-to (50), amplified-by (43), is (22), synonym-of (22), personifies
(18), is-a (13), is-analogue-of (13), identified-with (13), parallels (10),
prefigures (8), symbolized-by (8) — cover only 34% of edges. A naive stem collapse
yields 401 stems from 468 strings, so the tail is not mostly scoped variants of the
head verbs; the formulations are genuinely distinct. A reader who wants "every
identity claim about Mercurius"
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

Families are proposed bottom-up from the actual 468 strings, clustered over the
string **together with its edge context** — the quote and the paragraph it came
from. Lexical clustering on the strings alone is close to useless here and the
measurement says so: 468 strings collapse to 401 stems, so surface form carries
almost no signal about which strings mean the same thing. Clusters are then named
and bounded by hand. Expected shape, from eyeballing the head: identity/equivalence (is,
is-identical-with, synonym-of), symbolization (symbolizes, stands-for, personifies,
is-image-of), correspondence/parallel (corresponds-to, is-analogue-of, has-parallel-in),
amplification (amplified-by), composition (composed-of, contains), transformation
(transforms-into, renewed-as), sequence (precedes), attribution/derivation, scoped-
doctrine (the is-in-X-a-Y family). An explicit **`unclassified`** family is allowed
and reported, WITH a CI ceiling so the escape valve cannot become a dumping ground —
forcing every edge into a family is how distinct meanings get silently merged, and
unbounded escape is how the layer dies of vagueness; the ceiling holds the tension.

**The ceiling is set from measurement, not chosen in advance** (revision 2026-08-01).
An earlier draft named ~10% before anyone had classified a single edge. Against a
46% singleton tail that number is a guess, and a fail-closed CI threshold set by
guesswork pressures the gate into inventing family membership to keep the build
green — which manufactures exactly the over-collapse this layer exists to prevent.
So: v1.5 ships whatever the measured unclassified fraction turns out to be, publishes
the distribution, and sets the CI ceiling just above it. Tightening happens at v1.6,
after the second annotator has reviewed a stratified sample of the unclassified
bucket and confirmed those edges genuinely resist the vocabulary rather than
exposing a gap in it.

Assignment lives at the EDGE level, not the string level (cross-vendor review
correction, 2026-07-30): relation strings in this corpus are polysemous — "is"
alone spans archetypal identity, categorization, and composition — so a global
string→family table would silently corrupt every polysemous head string. The
string is used only as a clustering heuristic to batch the work; the recorded,
CI-enforced fact is `edge → family`, one row per edge, each row carrying who
assigned it and when — the same anatomy as a reference. A derived string-level
view is published for readability (singletons collapse to it trivially; head
strings show their per-edge split). Readers dispute mappings through the existing
channel. Cost consequence: the gate reviews 880 edge assignments and rising, not
~300 strings — the envelope below is revised accordingly.

## Assignment pipeline — the same gates, pointed at a new layer

0. **Definitions first, tested on the tail** (added 2026-08-01). Before any
   automated pass touches 880 edges, the human annotator classifies a stratified
   sample drawn deliberately from the SINGLETON tail using the candidate family
   definitions, cold. If a person cannot reliably place the tail with these
   definitions, no gate will either, and the failure is in the vocabulary rather
   than in the model. Cheap, and it fails before the expensive step rather than
   after it.
1. **Propose**: head strings first, then the tail. A batched pass assigns families
   over the concentrated head (twelve strings, 34% of edges) where clusters are
   obvious. The singleton tail is then handled as its own step: each singleton edge
   is offered the established families and may explicitly REJECT them into
   `unclassified`. Asking a model to cluster 409 singletons from scratch produces
   either a junk "miscellaneous" bucket or invented similarities; offering a settled
   vocabulary with a licensed refusal does not.
2. **Gate**: a dedicated family gate, not the structure gate wearing a second hat.
   Ontological classification (does this edge context belong to this family?) is a
   different task from extraction fidelity (does this quote say what the edge
   claims?), and the gate prompt therefore carries the family definitions document
   rather than the extraction rules. Independent model family, as everywhere.
3. **Cross-vendor**: Gemini re-judges a stratified sample of assignments.
4. **Human anchor**: a gold-set-style pass — stratified over families, the
   annotator sees the edge with its quote and picks the family cold (unanchored
   tool mode, learned the hard way).
5. **CI**: tests enforce the closed enum, one family per edge, no orphan mapping
   rows, and the published family counts; the facts checker pins whatever numbers
   any doc claims about families.

Per-batch afterwards: the miner proposes `relation_family` at mint time (the
vocabulary then exists to choose from), and the family gate checks it alongside
the structure gate — marginal cost near zero.

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
  human sign-off. This is the whole of the governance model, deliberately. RO runs
  on committees, issue trackers and cross-institutional consensus; a project with
  one author and one recruited annotator that copied that machinery would be
  performing governance rather than exercising it. Proposer ≠ creator, enforced by
  the model-family rule, is what actually binds here.
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
  re-clustering after every tranche. One backfill after the mining arc closes
  types the graph once. Note the tension the 2026-08-01 measurement creates: string
  growth has NOT flattened (46% of edges now carry a singleton string, up from 34%),
  so "wait for stabilization" is not a plan that terminates on its own. Whatever
  scope is declared, the layer gets built against a moving tail, and the seam rule
  below is what absorbs the movement.
- The gold-set finding applies directly: the human pass on mappings should be
  unanchored from day one, and a second annotator can take the mapping table and
  the voice gold set in one sitting.
- Paper impact is post-freeze by construction: a v1.4 section plus E11, with the
  frozen v1.3.0 untouched.

## Cost envelope

Revised 2026-08-01. The previous version of this table listed $2–4 + $8–15 + $0.50
+ $3–5 and then declared a total of "≈ $10", which is wrong by its own arithmetic;
it also costed a graph of ~700 edges that is now 880 and still growing.

| Step | Estimate | Basis |
|---|---|---|
| Head clustering + proposal pass | ≈ $3–6 | ~880 edges × ~300 tokens of context, Opus rates, two passes (head, then tail) |
| Family gate over 880 assignments | ≈ $8–25 | Fable rates; the spread is entirely whether the gate needs the full paragraph (~2.9k tokens/edge, as the structure gate does) or the quote plus definitions (~400) |
| Cross-vendor sample | < $0.50 | stratified, as in E6 |
| E11 evaluation runs | ≈ $3–5 | ~20 benchmark queries plus seeded mis-familied calibration |
| Human pass | author time, ~1–2 h | definitions test on the tail, then a ≈60-row stratified anchor |
| Per-batch marginal thereafter | cents | family proposed at mint time |

**Total ≈ $15–35 of API spend**, most likely near $25, plus one short human session.
The single lever that moves it is how much context the family gate needs per edge —
worth measuring on a 40-edge pilot before committing to the full run. Still cheaper
than one hostile review round, for the artifact's largest unaddressed usability gap.

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
