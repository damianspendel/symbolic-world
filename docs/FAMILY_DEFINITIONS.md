# Relation families — candidate definitions, v0.4 draft

Status: DRAFT for the step-0 tail test. Nothing here is assigned to any edge yet.

Provenance: v0.1 drafted 2026-08-06 by the Fable-family planning session from the
live graph (328 nodes / 1062 edges / 1180 references). Reviewed the same day by an
Opus-family agent per the governance rule (different-family review); verdict
RETHINK, scoped: architecture kept, 21 findings. v0.2 incorporated all of them and
was re-reviewed by the same Opus agent: verdict MINOR-REVISIONS, 12 findings, all
verified against the graph — three blockers (a type-based default in derivation, a
direction inversion in manifestation's string list, a self-contradicting seed in
separation) plus nine corrections. v0.3 lands them. Human sign-off comes from the
step-0 tail test. The test sample was drawn stratified by STRUCTURE
(singleton/normalized/volume), never by family, so the v0.2→v0.3 fixes did not
invalidate the draw.

**v0.4 is the first revision driven by measurement rather than review.** The
step-0 test ran on 2026-08-06 in four arms: the human annotator (17 items), an
Opus pass and a Gemini pass over all 60 blind, and a seeded-corruption
calibration of the family gate. Results and their consequences are in
"What the step-0 test measured" below. The headline: the gate caught 19 of 19
planted errors, the two model arms agreed 83%, and the human arm diverged mainly
where a thin UI withheld the boundary rules — so the definitions are followable
from the document, the interface was not, and the human's role changes from
classifier to adjudicator.

Companion: `docs/PROPOSAL_RELATION_TYPING.md` (design, pre-registered ruling,
assignment pipeline, cost). Measurement basis: **543 effective relation strings
over 1,061 referenced edges** — *effective* means `relation_normalized.relation`
where that layer exists (260 edges), else the verbatim `relation`. One edge
(`albedo precedes rubedo`) carries an empty references array and is excluded from
every count here; it is flagged as a graph defect to repair separately.

## Method and precedents — what is reused, what is rejected, and why

This vocabulary stands on named practice. Each line: the source, what is taken,
and the rationale for taking or refusing it (full treatment in the proposal).

| Practice | Used / rejected | Rationale |
|---|---|---|
| W3C `rdfs:subPropertyOf` two-tier pattern | **Used** as the design shape | verbatim relations as leaf properties, families as super-properties; queries over the family match the leaves; nothing is renamed — the frozen layer stays frozen |
| OBO Relation Ontology | **Used** as the structural precedent | a small, shared, state/relation-centric vocabulary whose convergence is enforced by tooling (here: fail-closed CI), which matches this corpus's symbol-centric relations |
| RO's committee governance | **Rejected** | a one-author project copying multi-institution machinery performs governance rather than exercising it (second cross-vendor review); replaced by the Wikidata rule below |
| Wikidata property governance | **Used** as the whole governance model | new family = proposal with definition + seed examples, review by a different model family, human sign-off; **proposer is never creator** — the same invariant as the mining pipeline |
| CIDOC-CRM | **Scale lesson only** | ~160 event-centric properties shows where sprawl leads; its event-centric structure is the wrong template for symbol-centric relations; hence the ≤25 family cap |
| SKOS match properties | **Rejected** (withdrawn on cross-vendor review) | SKOS maps concepts across vocabularies, not edge classes within one; the analogy misleads |
| OWL characteristics | **Sparingly used** | `owl:SymmetricProperty` for synonym-class identity; `owl:inverseOf` for declared pairs (symbolizes/symbolized-by, produces/produced-by). **Transitivity rejected**: alchemical sequences are cyclical (uroboros, the Rex cycle); a transitive `precedes` derives A-precedes-A |
| Surface-form clustering (Galárraga token overlap; CESI/CUVA embeddings) | **Rejected** | refuted by this graph's own measurements: 543 strings collapse to ~460 stems (form carries no signal), 1.9 edges/string and 463 singletons deny the redundancy those methods need; Lomaeva & Jain (ESWC 2022) observed CUVA collapsing >90% of relation phrases into one cluster — the over-collapse this layer exists to prevent |
| EDC define-then-canonicalize (Zhang & Soh 2024) | **Used** as the method | canonicalize over written DEFINITIONS, not surface strings; this document IS the definitions artifact, written to be carried by the family gate and embeddable per family |
| Fleiss' κ = 0.80 (Lomaeva & Jain's annotator pair) | **Used** as the agreement benchmark | disagreement concentrates on polysemous strings there too; the tail-test controls are expected near ceiling, singleton strata below |
| OOPS! P24 (relation encodes a proposition) | **Used** as the `not-a-relation` screen | already implemented in `tools/ontology_qa/quality.py` and the mining pre-check |
| Unanchored human passes | **Used** (internal, the E10 lesson) | anchored review anchors the reviewer; the sheet never shows a suggested family |

## What the step-0 test measured (2026-08-06)

Four arms, same 60-item structure-stratified sample, all blind to each other.

**Arm 1 — gate calibration (the load-bearing result).** 19 deliberate errors were
planted in the Opus pass's assignments and a Gemini gate judged all 60 without the
key. Corruption classes were chosen to be meaningful rather than random: K1
near-miss across a boundary this document explicitly rules on (8), K2 far-miss (4),
K3 swap to `correspondence`, the family the human arm showed behaving as a sink (4),
K4 replacing a confident family with a refusal (3).

| | |
|---|---|
| Sensitivity | **19/19 = 100%**, including 8/8 on near-misses |
| Specificity | 35/41 = 85%, **a floor** — several "false positives" are real errors in the uncorrupted set (the gate flagged `christ is-a anthropos` as classification-should-be-identity, and both other arms agree) |

The gate cited boundary rules by name when rejecting near-misses. This is the
evidence that the assignment pipeline can run at scale: the family gate is now a
calibrated instrument rather than an assumed one.

**Arms 2 and 3 — followability.** Opus vs Gemini agreed on 83% of 60 (100% on the
amplification control, 80% on head-string controls). Two independent model families
converging at that rate is evidence the document is followable. It is NOT evidence
it is correct: no arm is ground truth, and the document's author is the Fable
session, so agreement measures consistency, not truth.

**Arm 4 — the human.** 17 items: 35% agreement with Opus, 41% with Gemini, but
80–100% on head-string controls and 0–20% in the tail. Where the human differed,
Opus and Gemini agreed with each other on 15 of 17. The interface showed twelve-word
definitions on hover and **no boundary rules and no seed examples** — precisely the
content that discriminates. The divergence is therefore attributable to the
instrument, not to the annotator or (mainly) to the definitions. Confidence was 29%
"sure" with "best fit" written four times, which is the signature of an annotator
discriminating without the means to discriminate.

**Consequence for the protocol.** The human step is redesigned: models classify, the
calibrated gate checks them, and the human adjudicates only the cases where two model
families genuinely disagree — roughly ten items rather than sixty. The step-0 test as
originally specified (a human classifying cold from the definitions) is retired; it
measured the interface as much as the vocabulary.

## The rules of the layer (fixed before any definition)

1. **Assignment is per edge, never per string.** Head strings are polysemous —
   "is" alone spans identity, classification and position. The string batches
   the work; the recorded fact is `edge → family`.
2. **The family classifies the effective relation IN ITS EDGE CONTEXT** —
   subject, object, qualifiers, quote. Qualifiers can be decisive: `the-devil
   is-equivalent-to mercurius {scope: only to Mercurius' dark half}` is
   identity-family *as scoped*. Carriers matter: `the-self lies-at-border-of
   the-unconscious {carrier: consciousness}` (13 §67) — the carrier is not the
   object; misreading it misfamilies the edge.
3. **Family is independent of voice.** `claim_type` records who speaks; the
   family records what kind of relation is claimed. Every family definition
   below is agent-neutral. The predicted amplification↔jung-asserts
   correlation is E11's hypothesis to TEST — it must not be true by definition
   (and the data already shows it is not: 28 of 43 `amplified-by` edges carry
   reported or quoted voice).
4. **Two administrative classes exist beside the families**, per the
   pre-registered ruling (committed 2026-08-05, before data):
   - `unclassified` — a well-formed relation no family fits. Licensed,
     counted, CI-ceilinged. Carries a REASON CODE: `no-family` (the vocabulary
     is short) or `text-undecided` (the text itself hedges between families,
     e.g. "identical or at least connected with"). The two are reported
     separately — only `no-family` is vocabulary evidence; `text-undecided`
     is a property of the corpus, and scoring it against the vocabulary would
     permanently loosen the CI ceiling for the wrong reason.
   - `not-a-relation` — the relation slot holds a clause (fails the P24 screen
     and the semantic test). Excluded from every family denominator. After the
     normalization pass, 11 edges — all two-model-agreed refusals.
5. **A split is always allowed; a merge of established families requires
   re-gating** of every affected assignment. Adding a family follows the
   Wikidata shape (see table). The five families added at v0.2 (manifestation,
   separation, telos, derivation, privation) entered exactly this way:
   proposed by the Opus review with ~20–30 homeless edges each as evidence,
   accepted by the drafter, pending the human test.
6. **One family per edge.** If two families compete after the qualifiers are
   read: `unclassified(text-undecided)` when the TEXT hedges;
   `unclassified(no-family)` when the vocabulary is short; and if a boundary
   rule below decides it, follow the rule.

## Boundary rules (the six the review demanded, plus placements)

- **Identity vs correspondence on indistinguishability/equivalence:**
  indistinguishability or equivalence asserted of the terms THEMSELVES →
  `archetypal-identity`; asserted of their symbols, images, functions or roles
  → `correspondence`. So both CW 9ii §60 edges (`mandala indistinguishable-from
  god-image`, `wholeness is-psychic-analogue-of god-image` — one shared quote:
  the symbols can no longer be distinguished) are `correspondence`.
  The test is what the text predicates indistinguishability OF, not what the
  nodes are: sentence subject "the symbols of X" → correspondence; sentence
  subject X itself → identity, even when X is a Symbol-typed node (worked
  contrast: `mercurius is-identical-with saturn`, two image-terms, identity).
  Placements: `is-psychic-analogue-of`, `coincides-with`, `comes-closest-to`,
  `is-symbolical-equivalent-of`, `felt-as-equivalent-of` → correspondence;
  `is-essentially-same-as`, `revealed-identity-with`, `made-equal-to`,
  `amounts-to`, flat `is-equivalent-*` of the terms → identity;
  `identical-or-connected-with` (12 §476, Jung's own hedge) →
  `unclassified(text-undecided)`.
- **Composition vs structural-position:** if the claim entails the subject is
  materially a constituent of the object → composition; if it locates the
  subject within the object's structure without asserting constituency →
  position. Nucleus, centre, foundation default to POSITION (`is-nucleus-of`,
  `is-centre-of`, `is-foundation-of`, `chief-constituent-of` reads literally →
  composition). Totality/unity claims where the subject IS the whole
  (`the-self is-totality-of psyche`, 12 §44) → composition, whole-side;
  `unifies-…-into` as an act → union.
- **Psychic-effect vs dependence:** a standing condition ("unless X, no Y";
  "must always be dealt with first") → dependence, even when phrased as a
  blocking act — `personal-unconscious bars-gateway-to collective-unconscious`
  {condition: unless dealt with first} (12 §81) is DEPENDENCE. A dynamic act
  with an outcome → psychic-effect.
- **Psychic-effect vs opposition on compensation:** A acts on B to balance it
  → psychic-effect (`the-unconscious compensates consciousness`, 14 §184);
  a standing counter-position → opposition (`mercurius compensates christ`,
  13 §295 — the note says compensatory COUNTERPOINT, not act → opposition).
- **Sequence vs dependence on precedes:** "without X, no Y" → dependence
  (`the-shadow precedes anima/animus`, 9ii §42, whose quote says recognition
  is impossible without it); bare order → sequence.
- **`is-a` on a named-figure pair is identity, not classification** *(v0.4, from
  the gate)*. `christ is-a anthropos` was assigned classification by Opus and
  flagged WRONG by the gate, with Gemini and the human both saying identity; the
  quote ("The second Adam is Christ") asserts identity between two named figures,
  not membership of a class. Rule: when both endpoints are named Figures and the
  quote asserts they ARE one another, `is-a` is `archetypal-identity`.
  Classification requires the object to be a genuine kind or class.
- **Doctrinal-attribution outranks the relation's surface verb** *(v0.4)*. Where
  the quote frames the claim as an act of interpretation by a named tradition or
  author, attribution wins even when the relation string looks like another
  family: Gemini read `phoenix symbolizes christ` as attribution because the
  paragraph describes the reading being made ("in Christian interpretation"),
  against Opus's symbolization. Test: is the CLAIM the symbolizing, or someone's
  act of so reading it?
- **`renewed-through` / `transformed-through` are per edge** *(v0.4)*. Opus read
  `rex renewed-through the-unconscious` as dependence, Gemini as psychic-effect,
  and instrumentality now also claims it. Decide by what the quote asserts: the
  standing requirement (dependence), the acting-upon (psychic-effect), or the
  route travelled (instrumentality).
- **Per-edge caveats on promiscuous strings:** `is-a` (identity-flavoured at
  9ii §42, taxonomic at 9ii §33), `embodies` ("consists of/composed of"
  quotes → composition: `adam embodies quaternity` 14 §555; fusion/reunion
  quotes → union: `filius-regius embodies union-of-opposites` 14 §441;
  guise-of-content edges → manifestation: `christ embodies anthropos` 9ii §69;
  enacting-figure edges → personification; edges matching no cue →
  `unclassified(no-family)`: `chariot embodies quaternity` 14 §272), `symbolizes` (9 of 90 sit in the amplification layer),
  `precedes` (above). These four are the standing proof that assignment is
  edge-level.

## The families

Twenty-five candidates as of v0.4. The ≤25 figure is a design TARGET from the
CIDOC scale lesson, not a constraint: if the tail test's refusal reasons cluster
into a coherent 25th or 26th family, exceeding the target is a reportable
finding and goes through governance — a hard cap against a fail-closed CI
would deadlock. The count stands at 25 for a stated reason: the review showed that refusing the five v0.2 additions
would send ~100 well-formed edges to `unclassified` and bake a ~10% error into
the measured CI ceiling. Each entry: definition (agent-neutral), boundary,
seeds verified against the live graph.

### 1. symbolization
The subject is a symbol of the object in Jung's strict sense: "the best
possible description or formulation of a relatively unknown fact" (CW 6,
Definitions, s.v. Symbol) — not a conventional sign. Directionality test: the
OBJECT is the less formulable term; the subject is the image carrying it.
**Boundary:** not manifestation (there the SUBJECT is the less formulable term
showing itself — the direction inverts); not correspondence (two knowns); not
personification (a figure enacting).
**Seeds:** `quaternity symbolizes wholeness` (9ii §59); `fish symbolizes soul`
(9ii §187); `sol is-classical-symbol-for the-self` (12 §108, normalized);
`the-wheel is-symbol-for circulatio` (12 §214); `christ symbolized-by fish`
(9ii §147). Strings: symbolizes (90, minus the 9 amplification-layer edges),
symbolized-by (10), signifies (10), stands-for (6), represents (7).
**Inverse pair declared:** symbolizes / symbolized-by.

### 2. personification
A figure gives personal, enacting form to a content — the subject (usually
Figure-typed) is the content wearing a person, acting and speaking.
**Boundary:** not symbolization (a symbol presents; a personification acts);
not identity (`anima personifies the-unconscious` does not exhaust the
unconscious in the anima); not manifestation (the guise there need not be a
person).
**Seeds:** `anima personifies the-unconscious` (9ii §26); `maya personifies
projection-making-factor` (9ii §20); `christ personifies the-unconscious`
(13 §448, normalized). Strings: personifies (22), is-personified-by, and
`embodies` ONLY on enacting-figure edges (see boundary rules).

### 3. manifestation  *(added at v0.2 — review finding 3)*
The subject shows itself under the form of the object: one content, one
appearing guise, the subject persisting and not exhausted by any guise.
Directionality is the definiens: the SUBJECT is the less formulable term.
**Boundary:** inverts symbolization's direction test; not transformation (the
subject persists — Mercurius manifests as lumen naturae, Proteus AND Regina);
not generation (nothing new is brought forth); not personification (the guise
need not be a person: `sol manifests-as archeus`).
**Inverse pair declared:** `manifests-as` / `is-aspect-of` (with
`is-manifestation-of`) — the aspect strings run the SAME relation in the
inverse direction (the subject is the partial showing, the object the content
shown: `lilith is-aspect-of adam`), and the inverse declaration handles them
without breaking the direction test. `antichrist manifests enantiodromia` is
likewise inverse-direction and classified here.
**Seeds:** `mercurius manifests-as lumen-naturae` / `proteus` / `regina`;
`syzygy manifests-as christ-and-church` (9ii §41); `the-devil manifests-as
antichrist`; `archetype manifests-through synchronicity` (9ii §148);
`aqua-permanens is-aspect-of mercurius` (13 §370, inverse direction). Strings:
manifests-as (8), manifests, manifests-through, is-made-manifest-in,
is-figured-as, worshipped-as, is-often-represented-as, is-presented-through;
inverse: is-aspect-of, aspect-of, is-dark-aspect-of. NOT here:
`appears-as-centre-of` → structural-position (a place claim, per the
composition/position rule); `appears-as-archetype-of` (2) → classification
with a per-edge caveat (the object is what the subject is archetype OF, not a
guise).

### 4. archetypal-identity
The text asserts the two terms are ONE — via the projection thesis: a single
archetype behind both terms (Edinger, *Anatomy of the Psyche*; the answer to
the literal-absurdity objection). Includes scoped identity where a qualifier
restricts the claim. Symmetric in principle; `synonym-of` carries the
`owl:SymmetricProperty` precedent.
**Boundary:** the strongest family — demand the text's own identity assertion
of the TERMS (see the indistinguishability rule above). Watch identity
overreach, the E-series' recurring catch.
**Seeds:** `mercurius is-identical-with saturn` (13 §274, scoped: as senex);
`synonym-of` (22); `identified-with` (14), `is-identified-with` (13);
`the-devil is-equivalent-to mercurius {scope: dark half}` (14 §238);
`is-essentially-same-as` (13 §111).

### 5. correspondence
Two terms answer each other across registers or traditions — structural
likeness asserted without identity. The workhorse of the comparative method.
**Boundary:** weaker than identity (see the equivalence placements), stronger
than amplification (which is an adduced widening, not an asserted relation
between the terms).
**Seeds:** `animus corresponds-to logos` / `anima corresponds-to eros`
(9ii §29); `leviathan corresponds-to the-devil` (9ii §178); `anthropos
coincides-with the-self` (13 §268); `mandala indistinguishable-from god-image`
(9ii §60, per the boundary rule); `wholeness is-psychic-analogue-of god-image`
(9ii §60); `wholeness cannot-be-distinguished-from god-image` (9ii §73, per
the indistinguishability rule). Strings: corresponds-to (58), is-analogue-of (13), parallels (10),
is-parallel-to, agrees-with, is-psychic-analogue-of (6), comes-closest-to,
are-likened-to, coincides-with (5).

### 6. amplification
A parallel adduced to widen the interpretive basis of an image — "the use of
mythic, historical and cultural parallels … metaphorical, never literal"
(Samuels, Shorter & Plaut, *A Critical Dictionary of Jungian Analysis*,
pp. 16–17) — BY WHOEVER adduces it (agent-neutral per rule 3; 28 of the 43
`amplified-by` edges carry reported or quoted voice, so an agent-bound
definition would contradict the data and pre-decide E11).
**Boundary:** correspondence asserts a relation between the terms;
amplification adduces material to read an image by. The `layer: amplification`
field is the hand-built seed set: it tags 41 of the 43 `amplified-by` edges
(`lapis amplified-by shulamite` 14 §185 and `prima-materia amplified-by isis`
14 §16 lack the tag — a layer repair item) plus 9 `symbolizes`, 2
`symbolized-by`, 2 `parallels`, and 3 singletons: 57 edges over seven strings,
the standing proof that one string splits across families.
**Seeds:** `coniunctio amplified-by rex`; the 9 layer-tagged `symbolizes`
edges.

### 7. classification
Plain taxonomy: the subject is an instance or kind of the object.
**Boundary:** not identity (a member is not its class); not manifestation (an
aspect is not a kind — the aspect strings moved out at v0.2); `is-a` is
polysemous per the boundary rules.
**Seeds:** `animus is-a psychopomp` (9ii §33); `the-self is-a archetype`
(9ii §257). On `the-self is-a god-image` (9ii §42): the quote is disjunctive
("is a God-image, or at least cannot be distinguished from one") →
`unclassified(text-undecided)` unless the annotator judges the scope
qualifier settles it as identity.

### 8. composition
Part–whole: the subject contains, includes, or is a constituent of the object
(either direction; the verb settles which). Includes whole-side totality
claims (`the-self is-totality-of psyche`, 12 §44).
**Boundary:** the composition/position rule above (nucleus/centre/foundation
default to position); union is an act of joining, composition a standing
parthood.
**Seeds:** `the-self includes the-shadow` (9ii §76); `contains` (9); `includes`
(6); `wise-old-man completes marriage-quaternio` (9ii §42); `adam embodies
quaternity` (14 §555, per the embodies caveat).
**Concealment placement:** containment-as-concealment (`lies-hidden-in`,
`concealed-within`, `imprisoned-in`, `harbours`) → composition when the claim
is in-ness, position when the claim is where; epistemic concealment acts
(`unlocks-secret-of`, `obstructs-discovery-of`, `covers-up`) →
`unclassified(no-family)` — recorded as a candidate future family.

### 9. structural-position
The subject's place within a structure: centre, periphery, seat, abode,
between-position, schema-role, ordinal place. **The family the Aion evidence
demanded** (b-cw9ii-1 minted `is-centre-of`, `is-schema-for`; batches 3–4
added `is-abode-of`, `is-seat-of`, `is-first-fish-of`, `is-second-fish-of`,
`dwells-in`) — admitted under the seam rule as an ADDITION; no existing family
was redefined.
**Boundary:** the composition/position rule above.
**Seeds:** `christ is-centre-of christian-mandala` (9ii §69);
`marriage-quaternio is-schema-for the-self` (9ii §42); `the-north is-abode-of
the-devil` (9ii §157); `mercurius dwells-in celestial-pole` (9ii §206);
`the-self lies-at-border-of the-unconscious {carrier: consciousness}`
(13 §67); `the-devil is-fourth-person-beside the-trinity` (12 §192);
`the-ego centre-of consciousness` (9ii §11).

### 10. union
The terms are joined, married, fused — the coniunctio class, central enough
in this corpus to stand apart from composition.
**Boundary:** an act or achieved state of joining distinct terms, vs
composition's standing parthood; three-place unions ("A unites B[-and-C]")
keep the united pair in object or qualifiers.
**Seeds:** `mercurius unites the-opposites` (12 §404); `lapis unites
the-opposites` (12 §140, 13 §131); `spirit unites the-opposites` (9ii §141);
`yesod unites tifereth-malchuth` (14 §635); `the-self unites-with anima`
(14 §736); `conjoined-with`; `flows-together-in` (13 §218).

### 11. separation  *(added at v0.2 — review finding 11; reworked at v0.3)*
The separatio/solutio class, in BOTH its structures: (i) A is parted,
extracted or freed from B; (ii) A dissolves, separates or splits B. The opus's
counter-operation to union and as central.
**Boundary:** not transformation (where the subject BECOMES the object — so
`messiah splits-into the-opposites`, whose quote says the split "becomes a
complete polarity", is transformation-toward-opposition and goes per edge, not
here); not psychic-effect (separation asserts the parting itself, not a
dynamic residue — this is a definitional distinction, not just check-order).
**Seeds:** `lapis is-extracted-from man` (9ii §256); `solutio dissolves
the-body` (14 §316); `luna dissolves rex` (14 §506); `consciousness separates
the-opposites` (12 §30); `unio-mentalis achieved-by-separating the-body`
(14 §671). Strings: dissolves, is-extracted-from, separates, is-separated-from,
frees-god-from, delivered-from, splits-into (per edge), abolish-separation-from
(negated — read per edge; may be union).

### 12. transformation
The subject turns into, or is turned into, the object.
**Boundary:** not generation (the parent persists beside the offspring); not
sequence (order without becoming); not manifestation (a guise is not a
becoming — the subject persists unchanged behind it).
**Seeds:** `transforms-into` (6); `anima was-transformed-into lilith`
(13 §399); `mandala transforms chaos` (9ii §60); `hierosgamos developed-into
coniunctio` (9ii §72); `renewed-as`, `reborn-as`.

### 13. generation
The subject brings forth or begets the object — psychological or mythological
parenthood, the parent persisting beside the offspring.
**Boundary:** not transformation; not derivation (historical/doctrinal
descent is family 14, split out at v0.2 — the same verb "originates" serves
both, so read the terms: traditions derive, beings beget); kinship ROLES
(brother, consort) are family 20.
**Seeds:** `produces` (8); `begets` (3); `four-elements give-rise-to will`
(9ii §100); `fish is-son-of great-mother` (9ii §173); `brings-forth`.
**Inverse pair declared:** `produces` / `originates-in` (alongside
produces/produced-by) — `projection originates-in the-unconscious` (9ii §17)
and `god-image originates-in psychoid` (14 §787) are generation,
inverse direction; only tradition-to-tradition `originates-in` (per §14's
relation test) is derivation.

### 14. derivation  *(added at v0.2 — review finding 13)*
Doctrinal, historical or textual transmission: one tradition, doctrine, text
or figure draws from, descends from, influences or supplants another.
**Boundary:** generation begets beings; derivation transmits ideas and forms.
The RELATION itself must assert transmission (draws from, descends from,
influences, supplants, continues). Subject type is evidence, never a default —
a tradition-subject edge whose relation asserts telos, privation, expression or
opposition takes THAT family (`alchemy reached-its-summit-in faust` → telos;
`privatio-boni makes-evil-diminution-of good` → privation; `dogma expresses
collective-unconscious` → symbolization).
**Seeds:** `alchemy originates-in gnosticism` (9ii §267); `yahweh influenced
jakob-boehme {scope: through the Cabala}` (9ii §111); `paracelsus
draws-knowledge-from lumen-naturae` (13 §148); `lapis-christ-parallel
was-bridge-into alchemy` (13 §387); `the-opus replaces-sacraments-of
christianity` (13 §232). Strings: derives-…-from, has-roots-in, rooted-in,
springs-from, proceeded-from, has-a-source-in, probably-chief-source-of,
forerunner-of, has-precursor-in, continues-doctrine-of, takes-the-place-of,
based-on, develops-on-basis-of, shares-allegories-with.

### 15. sequence
Temporal or processual order without becoming, begetting or requirement.
**Boundary:** transformation/generation entail order — assign the stronger
family when the text supports it; "without X, no Y" is dependence (see
boundary rules). NO transitivity (uroboros argument).
**Seeds:** `the-opus begins-with nigredo` (9ii §231); `is-first-stage-of`
(9ii §42); `rubedo immediately-preceded-completion-of the-opus` (12 §269);
`followed-by`. (`precedes` distributes per edge — see boundary rules; the
sixth `precedes` edge, albedo→rubedo, is the empty-references defect.)

### 16. prefiguration
Typological anticipation: the subject foreshadows the object as type to
antitype — the pattern exists earlier and points forward.
**Boundary:** not sequence (order without pointing); not correspondence
(alignment without the temporal arrow). "Anticipation" language is the cue.
**Seeds:** `prefigures` (8); `son-of-man is-anticipation-of the-self`
(12 §314); `jupiter heralds messiah {carrier: Saturn, condition: in Pisces}`
(9ii §128); `foreshadows`.

### 17. telos  *(added at v0.2 — review finding 12; widened at v0.3)*
Goal-direction AND goal-attainment: the subject aims at, strives toward,
culminates in, reaches, or attains the object as its end. The teleology of
the opus — one of the corpus's main axes.
**Boundary:** a goal is not the next term (sequence) and not a requirement
(dependence). Against psychic-effect: telos claims an end pursued or reached
BY the subject on its own arc; psychic-effect claims one term acting on the
other. Attainment of one's own end is telos, not effect.
**Seeds:** `self-knowledge aims-at the-self` (9ii §252); `the-self goal-of
individuation` (9i §278); `lapis is-goal-of the-opus` (14 §759);
`night-sea-journey aims-at rebirth` (12 §436 normalized); `alchemy
reached-its-summit-in faust` (12 §558); `the-self fulfils-itself-in
wholeness` (9ii §123). Strings: aims-at, aimed-at, goal-of, is-goal-of,
culminates-in (2), attains (2), destined-for, tends-towards,
is-movement-toward, fulfils-itself-in, is-consummated-on, reaches.

### 18. opposition
The terms stand against each other: enmity, polarity, contradiction, standing
counter-position (including compensatory counterpoint — see boundary rules).
**Boundary:** not mere difference or lack — negation without enmity is
privation (family 19); the text must set the terms AGAINST each other.
**Seeds:** `antichrist opposes christ` (9ii §69); `leviathan opposes behemoth`
(9ii §181); `is-equivalent-opposite-of` (9ii §84/98); `polarizes-with` (4);
`mercurius compensates christ` (13 §295, per the compensation rule);
`came-into-tension-with` (13 §290).

### 19. privation  *(added at v0.2 — review finding 14)*
Lack, absence, negated identity or negated capacity: A lacks B, A is not B,
A cannot be/represent B. The privatio-boni axis — Aion's spine — lives here.
**Boundary:** opposition requires enmity; privation only absence or
non-identity. Negated-modal identity ("cannot be distinguished") is NOT here —
it follows the indistinguishability rule (identity or correspondence).
**Seeds:** `christ lacks the-shadow` (9ii §79); `god-image lacks man`
(9ii §185); `the-trinity lacks the-devil` (11 §103); `putissimus-homo
cannot-be christ` (13 §390); `animus cannot-represent-totality-of the-self`
(13 §342); `privatio-boni makes-evil-diminution-of good` (9ii §74);
`evil does-not-lead-to manichaean-dualism` (9ii §99); `archetypal-image
distinct-from archetype` (8 §417); `christ is-never-matched-by the-self`
(9ii §124); `the-centre occupies-different-plane-from the-ego` (12 §135).

### 20. kinship  *(added at v0.2 — review finding 15)*
Standing familial or consort roles at the mythologem level: sibling, spouse,
bride, companion, double, contrasexual counterpart.
**Boundary:** generation covers parent/child acts of begetting; kinship covers
the standing role. Not union (a consort is a role, not an act of joining).
**Seeds:** `the-devil is-elder-brother-of christ` (9ii §77, §103);
`shulamite consort-of anthropos` (14 §609); `soul is-the-bride-of christ`
(9ii §72); `behemoth is-double-of leviathan` (9ii §185); `is-feminine-half-of`,
`masculine-half-of`, `is-anima-of`, `companion-of`; `is-shadow-of` per edge
(`luna is-shadow-of sol` 14 §172 = contrasexual counterpart, here;
`leviathan is-shadow-of yahweh` 9ii §183 = the shadow-relation, opposition).

### 21. doctrinal-attribution
A carrier names, defines, translates, teaches, interprets or classifies — the
relation records an act of predication by someone, not an ontology between
subject and object.
**Boundary:** the decisive test — remove the carrier and the claim collapses.
Voice often co-varies but never decides (rule 3). Tradition-to-tradition
transmission is derivation; a single carrier's predication is attribution.
**Seeds:** `hun is-translated-as animus {carrier: Wilhelm}` (13 §57);
`prima-materia was-designated-as mercurius` (12 §517); `the-wheel
is-in-boehme-a-concept-for wholeness` (12 §216); `augustine
identifies-god-image-with soul` (9ii §71); `origen locates-imago-dei-in soul`
(9ii §70); `aniadus is-defined-as inner-man {carrier: Ruland}` (13 §194);
`basil-the-great denies-god-authorship-of evil` (9ii §82 — an attributed
denial: the carrier's act, not a privation between the terms).

### 22. projection
Psychic contents relocated into an outer carrier — the central explanatory
mechanism for alchemy. Includes withdrawal edges.
**Boundary:** not symbolization (a symbol formulates; a projection relocates
and is later withdrawn); not manifestation (the archetype showing itself is
not relocated by a psyche).
**Seeds:** `mercurius is-projection-of the-unconscious` (13 §259); `lapis
is-projection-of the-self` (9ii §264); `artifex projected individuation
{scope: into the phenomena of chemical change}` (12 §564); `tree-nymph
is-a-projection-of anima` (13 §458); `consciousness develops-through-withdrawal-of
projection` (13 §122).

### 23. dependence
Requirement, precondition, subordination, rulership: one term needs,
presupposes or is governed by the other — a STANDING condition.
**Boundary:** the dependence rules above absorb conditional "precedes" and
blocking-phrased requirements (`bars-gateway-to`).
**Seeds:** `coniunctio is-prerequisite-for wholeness` (9ii §58); `the-ego
subordinate-to the-self` (9ii §9); `aeon-of-the-fishes is-ruled-by
hostile-brothers` (9ii §142); `wholeness requires anima` (12 §295);
`the-shadow precedes anima` (9ii §42, per the precedes rule);
`are-necessary-conditions-of` (9ii §112); `personal-unconscious
bars-gateway-to collective-unconscious` (12 §81).

### 24. psychic-effect
One term acts dynamically on the other: overpowers, activates, stimulates,
suppresses, heals, endangers, produces a state in. Deliberately the LAST
family checked — if any more specific family fits, take it. Exists so genuine
dynamics do not leak into `unclassified`; the tail test watches whether it
becomes a dumping ground.
**Boundary:** all the rules above drain this family first (dependence,
opposition-as-counterpoint, separation, telos).
**Seeds:** `consciousness is-overpowered-by the-unconscious` (12 §438);
`the-unconscious compensates consciousness` (14 §184); `soul
produces-negative-inflation-in the-unconscious` (9ii §114); `projection
leads-to-psychoses-of mass-psyche` (13 §52); `artifex activates
the-unconscious` (13 §220); `mediates` (4); `undergoes` (5);
`consciousness leads-to-crucifixion-of the-ego` (9ii §79).

### 25. instrumentality  *(added at v0.4 — earned by measured refusal)*
The object is the MEANS by which the subject is reached, enabled, effected or
made possible. Not what happens, but what it happens *through*.
**Boundary:** telos names the END pursued; instrumentality names the route to it
(`homo-maximus is-approached-through the-opus` — the opus is the road, the homo
maximus the destination). Not dependence: a precondition must be satisfied
*before*, a means is used *to*. Not psychic-effect: the subject is not acted upon
by the object, it travels by it.
**Evidence for the addition:** both model arms of the step-0 test refused items
this family now covers, independently and with converging reasons — Gemini on
`homo-maximus is-approached-through the-opus` ("an instrument/means relation is
not covered by the existing families") and both arms on `temenos
enables-meeting-with the-unconscious` ("an instrumental/affordance relation does
not fit structural-position, dependence, or psychic-effect"). 13 strings and 13
edges in the live vocabulary carry the sense.
**Seeds:** `homo-maximus is-approached-through the-opus` (13 §203);
`temenos enables-meeting-with the-unconscious` (12 §63); `imaginatio
unlocks-secret-of the-opus` (12 §400); `mandala is-built-up-through
active-imagination` (12 §123); `rex renewed-through the-unconscious`;
`unio-mentalis achieved-by-separating the-body` (14 §671, per edge — the
separation reading may win where the parting itself is the claim).

## What is deliberately NOT here

- **No transitivity on any family**; symmetry and inverses only as declared
  (see the precedents table).
- **No family for "is" as such** — the copula distributes by context; the
  canonical argument for edge-level assignment.
- **No voice-derived families** (rule 3).
- **No manifestation/appearance merger into symbolization** — the direction
  test separates them and 19 edges depend on it.


### Considered at v0.4 and NOT added

Two further gaps surfaced in the step-0 refusals. Both are recorded rather than
adopted, because the evidence does not yet meet the bar the instrumentality
addition cleared.

- **property-attribution** (`is-characterized-by`, `possesses`, `has-affinity-with`).
  One arm refused one item. 5 strings / 7 edges. A family for "A has quality B"
  is a different shape from every family here — the object is a property, not a
  participant — and adopting it would invite every adjective in the corpus. Route
  these to `unclassified(no-family)` for now and revisit if the full assignment
  pass produces a cluster.
- **governing-principle** (`is-principle-of`, `orders`). Both arms refused
  `ares is-principle-of individuation`, which is real evidence, but the class is
  3 strings / 4 edges — too thin to earn a family, and plausibly absorbed by
  structural-position (a governing role is a place in a structure) or by
  instrumentality (a principle by which something proceeds). Route to
  `unclassified(no-family)` and let the assignment pass decide.

Recording refusals as refusals, with their counts, is how the `unclassified`
reason codes stay meaningful: a `no-family` on `is-principle-of` is now a known
gap under review, not an unexplained miss.

## Expected coverage, stated before the test

The 24 families were derived from the head (≥4 uses), the normalized layer,
the Aion mints, and the review's sweep of the homeless verb classes. The
singleton tail is the test. Pre-registered expectation: most well-formed
singletons land in a family (b-cw9ii-1 ran 22/24 at edge level); refusals
above ~30% of the well-formed tail sample mean the vocabulary is short, and
the refusal reasons say where. That outcome ships as a finding, not a failure.

## The adjudication protocol (replaces the step-0 tail test)

The original protocol asked a human to classify 60 items cold. It ran on
2026-08-06 and is **retired**: it measured the interface as much as the
vocabulary, and 60 cold classifications is the wrong use of the only scarce
resource in the pipeline. What replaces it:

1. **Two model arms classify, blind to each other** — one Opus-family, one Gemini.
   Neither may be the family that authored the definitions.
2. **The calibrated gate checks both.** Sensitivity 19/19 and specificity ≥85%
   are measured, not assumed, and both are re-measured whenever the definitions
   change materially (the corruption harness is seed-reproducible:
   `pipeline/work/corrupt_family_assignments.py`).
3. **The human adjudicates only genuine disagreement** — cases where the two model
   arms differ, plus any the gate marks WRONG on an uncorrupted assignment. On the
   60-item sample that was ~10 items, not 60.
4. **Refusals are routed, not pooled.** `unclassified(no-family)` clusters go to
   the family-addition path in rule 5; `unclassified(text-undecided)` is recorded
   against the corpus, never against the vocabulary.

The adjudication interface must show, at the point of decision: the edge with its
qualifiers and quote, **both model answers with their stated reasons**, the
competing family definitions in full, the governing boundary rule, and the seed
examples. The v0.3 interface showed twelve-word hovers and none of that, which is
the measured cause of the human arm's divergence — 80–100% agreement on head
controls, 0–20% in the tail where boundary rules decide.

Retained from the original protocol: unanchored presentation (no suggested
answer), per-stratum reporting never pooled, a required one-line reason on every
refusal, and Fleiss' κ = 0.80 as the agreement benchmark — now applied to the two
model arms rather than to a human pair, with 83% observed on the first run.

## Sign-off condition

The definitions bind the family gate when: the two model arms agree at or above
the benchmark on the controls; the gate's calibration has been re-run against the
current definitions; and the human has adjudicated the disagreement set. None of
those is satisfied by model agreement alone — consistency is not correctness, and
the author family is not eligible to judge its own document.
