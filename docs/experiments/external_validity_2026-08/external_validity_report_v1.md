# External-validity check of the relation-family layer — report v1

Charter: BACKLOG.md item 4. Question: would a reader of Jungian scholarship
agree with how the graph's families classify Jung's assertions? Sample:
27 items (seed 20260812; item 25 seed 20260812+1; items 26–27 purposive on
Damian's instruction), drawn 2026-08-12 from seed.json at 407/1555,
assigned=1292, queue=220. Chain: Opus 5 executed the literature search
(worksheet: `external_validity_worksheet_opus.json`), Gemini reviewed every
item (`gemini_review_c01–03.json`), Fable finalized. Ruleset under test:
FAMILY_DEFINITIONS v0.6. Nothing here enters the graph; proposals only.

## Access limitation, stated first

Opus could not obtain four named sources: Samuels/Shorter/Plaut's *Critical
Dictionary*, Edinger's *Anatomy of the Psyche* (except one chapter) and
*Mysterium Lectures*, von Franz's *Aurora Consurgens* and *Alchemical Active
Imagination*. Fully searched: Jacobi, Edinger's *Aion Lectures*, von Franz's
*Alchemy: An Introduction*, Abraham's *Dictionary of Alchemical Imagery*
(fallback, used only where the named list is silent, flagged per item). No
JAP paper was found treating any sampled pair at relation level. So the
NOT-TREATED count partly measures access. Gemini's review supplied four
specific treatments from the missing sources (items 2, 5, 10, 19 — Critical
Dictionary s.v. Anthropos, Self, Trickster; *Anatomy of the Psyche*,
Mortificatio ch.); no arm in this chain could verify them against the
physical text, so they are reported as REVIEWER-SUPPLIED and kept out of the
headline rates. All four would flip NOT-TREATED → AGREES.

## Per-item results (final, after review and finalization)

Kind A = assigned, P = purposive, Q = queued. Finalization changes from the
Opus draft are marked ◆ with the ruling.

| # | Edge | Family under test | Cite | Final score |
|---|---|---|---|---|
| 1 | the-vessel \| symbolizes \| mercurius | archetypal-identity | 12 §338 | NOT-TREATED |
| 2 | christ \| is-a \| anthropos | archetypal-identity | 14 §565 | NOT-TREATED (reviewer-supplied: AGREES) |
| 3 | green-lion \| synonym-of \| dragon | archetypal-identity | 14 §408 | ◆ SCHOLARS-SPLIT (was AGREES; Abraham's entries render identity, his Introduction lists both among "the symbols for Mercurius" — a within-source contrary rendering blocks AGREES) |
| 4 | lapis \| is-identified-with \| homo-maximus | archetypal-identity | 9i §555 | NOT-TREATED |
| 5 | the-self \| corresponds-to \| atman | correspondence | 9ii §223 | NOT-TREATED (reviewer-supplied: AGREES) |
| 6 | the-opus \| parallels-redemptive-work-of \| christ | correspondence | 12 §453 | AGREES |
| 7 | quintessence \| corresponds-to \| anima-mundi | correspondence | 14 §450 | NOT-TREATED |
| 8 | luna \| correlated-with \| sapientia | correspondence | 14 §164 | DISAGREES (weakest in class: single Abraham entry, personification idiom) |
| 9 | tree \| represents \| the-opus | symbolization | 13 §414 | AGREES |
| 10 | raven \| symbolizes \| the-devil | symbolization | 14 §727 | NOT-TREATED (reviewer-supplied: AGREES) |
| 11 | lightning \| signifies-change-of \| psyche | symbolization | 9i §533 | NOT-TREATED |
| 12 | tree \| symbolizes \| the-unconscious | symbolization | 9i §406 | AGREES |
| 13 | tree \| is-metaphorical-form-of \| arcane-substance | doctrinal-attribution | 13 §382 | DISAGREES (lit renders the relation flatly, carrier-free → symbolization; see genre caveat below) |
| 14 | origen \| first-propounded \| privatio-boni | doctrinal-attribution | 9ii §74 | AGREES |
| 15 | paracelsus \| places-regio-nymphididica… \| individuation | doctrinal-attribution | 12 §116 | NOT-TREATED |
| 16 | luna \| amplified-by \| silver | amplification | 14 §154 | DISAGREES (→ symbolization/synonymy) |
| 17 | nigredo \| amplified-by \| raven | amplification | 14 §727 | DISAGREES (→ symbolization; lit's direction runs raven→nigredo) |
| 18 | mercurius \| amplified-by \| lion | amplification | 14 §404 | DISAGREES (→ identity/symbolization; Jung's own quote: "synonym") |
| 19 | trickster \| personifies \| the-shadow | personification (control) | 9i §484 | NOT-TREATED (reviewer-supplied: AGREES) |
| 20 | lapis \| unites \| the-opposites | union (control) | 12 §140 | AGREES |
| 26 | mandala \| is \| god-image | archetypal-identity (human ruling) | 9i §572 | ◆ DISAGREES at pair level (was SCHOLARS-SPLIT; Edinger's equivalence claim is about the Self, not the mandala — for THIS pair both Jacobi and Edinger render symbol/correspondence. Caveat: the ruling was paragraph-local and no source discusses §572 itself) |
| 27 | mandala \| indistinguishable-from \| god-image | correspondence | 9ii §60 | ◆ AGREES (was SCHOLARS-SPLIT; same ruling as 26 — Jacobi and Edinger-on-§60 both render symbol/correspondence) |

Queued items, scored per arm:

| # | Edge | Arms | Cite | Final |
|---|---|---|---|---|
| 21 | lapis \| symbolizes \| christ | corresp. vs symboliz. | 12 §451 | both arms DISAGREES — Abraham renders identification ("identified with the all-healing philosopher's stone"), a third answer. Caveat: Jung's own chapter heading is "The Lapis-Christ Parallel" and the quote's verb is "likens", favouring the correspondence arm |
| 22 | lapis \| symbolizes \| anthropos | corresp. vs symboliz. | 12 §335 | ◆ both arms DISAGREES (was NOT-TREATED; Edinger's quaternio chain relates the terms structurally → structural-position, a third answer. Caveat: one source, and Edinger is reconstructing Jung's own CW 9ii chain) |
| 23 | quintessence \| corresponds-to \| god-image | corresp. vs identity | 14 §681 | ◆ both arms NOT-TREATED (was SCHOLARS-SPLIT; the Jacobi/Edinger split is on Self\|God-image, not this pair — renderings must be of the pair) |
| 24 | personal-unconscious \| is-layer-of \| the-unconscious | compos. vs position | 9i §3 | position arm AGREES, composition arm DISAGREES — Jacobi renders layer talk as spatial "topology", a methodological overlay; the cleanest result in the sample |
| 25 | the-unconscious \| transforms \| the-trinity | psych.-effect vs transform. | 11 §107 | both arms NOT-TREATED |

## Rates, exact, per family — headline (verified renderings only)

Denominator = items the literature treats (A/D/S); NT listed beside.

| Family | AGREES | DISAGREES | SPLIT | NOT-TREATED |
|---|---|---|---|---|
| archetypal-identity (incl. item 26) | 0/2 | 1/2 | 1/2 | 3 |
| correspondence (incl. item 27) | 2/3 | 1/3 | 0/3 | 2 |
| symbolization | 2/2 | 0/2 | 0/2 | 2 |
| doctrinal-attribution | 1/2 | 1/2 | 0/2 | 1 |
| amplification | 0/3 | 3/3 | 0/3 | 0 |
| controls (personification, union) | 1/1 | 0/1 | 0/1 | 1 |
| **All assigned+purposive** | **6/13** | **6/13** | **1/13** | **9** |

With the four reviewer-supplied treatments accepted: 10/17 AGREES, 6/17
DISAGREES, 1/17 SPLIT, 5 NT. Every unverified flip is toward AGREES; the
headline rate is the conservative one.

## Findings

**F1 — amplification fails externally, 3/3, all one way.** The literature
renders every sampled `amplified-by` edge as a symbol or synonym relation
between the terms, never as material adduced from outside. Jung's own quotes
in these edges say "signifies", "is the traditional name for", "is a
synonym for". The family is tracking the relation string, not the assertion
— externally, `amplified-by` behaves as a citation-practice marker, not a
relation kind. The step-0 "100% agreement on the amplification control" now
reads as string-matching, not classification.

**F2 — the sentence-subject test has no external counterpart.** The
purposive pair was drawn to test v0.6's anchor ruling. Result: Jacobi
renders every mandala|God-image statement identically (symbol +
correspondence, identity refused on methodological grounds); Edinger
discusses §60 directly and takes nothing from the indistinguishability
clause, while asserting Self≡God-image six pages earlier. The scholarly
split (Jacobi vs Edinger) runs across both paragraphs identically rather
than between them. The two families the test assigns to §572 and §60 map
onto two scholarly camps, not two Jungian claims. This does not show either
assignment wrong — the test is paragraph-local and the literature speaks
pair-globally — but the distinction is ours, not the field's, and the
families page must say so.

**F3 — the identity/symbolization boundary is unstable in the reference
literature itself.** Abraham defines the dragon as "the dual-natured
Mercurius" and lists the dragon among "the symbols for Mercurius" — same
author, same book. The graph's sharpest boundary is one its most relevant
reference work does not hold stable over alchemical image pairs (items 3,
18, 21). Consistent with F1's direction.

**F4 — the lapis queue split has a third answer.** Abraham renders
lapis|Christ as identification, matching neither queued arm. Identity should
be a live candidate when the correspondence/symbolization split is
adjudicated — while noting Jung's own "likens"/"Parallel" framing supports
correspondence for §451 specifically.

**F5 — composition vs structural-position: external support for position.**
Jacobi states the exact distinction the boundary rule draws and lands on
position, with the further caution that the spatial reading is her
"methodological help", an overlay on a genetic picture. Directly useful for
the 13 queued items of this shape.

**F6 — dictionary genre flattens attribution.** Item 13's DISAGREES is
real under the rules but partly generic: dictionaries state relations
carrier-free. Where our family hangs on a carrier ("this remarkable text
explains…"), dictionary evidence will systematically vote against
attribution. Weigh attribution items toward discursive sources.

**F7 — process defect found in passing: normalization can strip the
carrier.** Item 13's `relation_effective` is `is-metaphorical-form-of`; the
carrier survives only in the quote. An arm classifying from the effective
relation cannot see the attribution claim. Autoclassification input should
carry the verbatim relation beside the normalized one.

**F8 — direction.** Item 17 runs nigredo→raven; the literature's relation
runs raven→nigredo. `amplified-by` invites this inversion (the adduced
image sits in object position). One case, but check the other 42.

## Ranked FAMILY_DEFINITIONS v0.7 proposals

**P1 (from F1) — amplification requires the adducing act in the quote.**
Current: "amplification adduces material to read an image by" + seeds "the
`amplified-by` edges generally, where the relation states the adducing."
Proposed: "An edge lands in amplification only when the quote asserts the
act of adducing itself. A quote asserting signification, synonymy, or
naming ('signifies', 'is a synonym for', 'is the traditional name for')
classifies by that content relation, whatever the relation string says —
the same precedence attribution already has over surface verbs."
Flips: items 16, 17, 18 (→ symbolization or identity), and predictably most
of the 43 `amplified-by` edges. Predicted two-arm effect: agreement on
amplified-by strings drops from ~100% (string-driven) to the general rate;
honest, since the current figure measures the string, not the definition.

**P2 (from F3/F4) — worked note on alchemical name-pairs at the
identity/symbolization boundary.** Current: "demand the text's own identity
assertion of the TERMS." Proposed addition: "Over alchemical image pairs
the reference literature writes identity and symbol idioms interchangeably
(Abraham on dragon/Mercurius). A synonym-class string between two
alchemical images is identity only when the quote asserts co-reference —
the two names name one referent at one stage; a likeness or 'likens'
framing is correspondence; otherwise unclassified(text-undecided)."
Flips: none in-sample (item 3 stays SPLIT; item 21's adjudication gains
identity as a candidate). Predicted effect: fewer confident identity
assignments in the alchemical register; some two-arm agreement converts to
agreed text-undecided, which is the true state.

**P3 (from F5) — anchor composition/position with Jacobi's topography.**
Current rule decides by constituency vs location. Proposed addition:
"Layer/stratum/sphere language locates within a topography and defaults to
structural-position even when the container noun suggests parthood
(external anchor: Jacobi's 'topology' reading of the layer picture)."
Flips: the 13 queued composition|structural-position items are predicted to
resolve mostly to position; no assigned in-sample item moves. Predicted
effect: removes the second-largest disagreement shape from the queue.

**P4 (from F2) — declare the sentence-subject test as internal
instrument.** Current: the test is stated as a boundary rule with worked
contrast. Proposed addition to the rule and to the families page: "This
distinction is our instrument; the secondary literature does not mark it
(checked 2026-08-12: Jacobi and Edinger render the mandala|God-image pair
identically across both paragraphs). A paragraph-local identity ruling
therefore carries its distinguishing note on the edge, and the families
page reports the boundary as externally unvalidated." Flips: nothing;
prevents the page from implying scholarly backing the check did not find.

**P5 (from F6) — clarify 'named carrier' and weigh source genre.**
Current: "an act of predication by someone… remove the carrier and the
claim collapses" with named-carrier examples. Proposed: "The carrier must
be identified — by name or by definite reference to a specific text or
author ('this treatise explains…'). Collective ascription ('the alchemists
say') stays with the content family unless the claim collapses without the
ascription." Flips: item 13 stays attribution under our rules (the quote's
claim is the text's explaining); the DISAGREES stands as a genre finding,
not a defect. Predicted effect: small; mainly stops arms from bouncing
attribution edges whose carrier is anaphoric.

**P6 (from F7/F8) — pipeline, not wording:** classify-input carries
verbatim relation beside `relation_effective`; audit the 43 `amplified-by`
edges for direction against the adduced-image-as-subject convention.

## Honesty notes

- 13 of 22 assigned/purposive items were treatable with verified renderings;
  9 NOT-TREATED, of which at least 4 are access artifacts (the reviewer
  named specific loci in the inaccessible sources). Coverage, not the
  vocabulary, is the first constraint on this check's precision.
- Abraham carries most of the alchemical stratum and is outside the
  charter's named list; every use is flagged in the worksheet.
- Item 8's DISAGREES rests on one dictionary entry read strictly; the
  weakest negative in the table.
- Items 26/22's finalization rulings (pair-level evidence only) are mine
  (Fable). Reversing them changes: 26 DISAGREES→SPLIT, 22 DISAGREES→NT;
  headline rate moves from 6/13 to 6/12 AGREES. Rulings are Damian's.
- Scoring rules were fixed before the search; no threshold moved.
