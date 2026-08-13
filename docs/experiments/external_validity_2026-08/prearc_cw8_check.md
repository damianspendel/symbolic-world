# CW 8 pre-arc check — psychic-effect, dependence, instrumentality (2026-08-13)

Purpose: the agreed precondition before the CW 8 arc starts (CLAUDE.md;
docs/PROPOSAL_NEXT_ARC.md). CW 8's energetic register lands its relational
weight on three families: psychic-effect, dependence, instrumentality. This
pass asks whether those three definitions, at v0.7.1 BINDING, hold up
against the on-disk secondary literature before CW 8 mints assignments on
them. Method scaled down from `external_validity_protocol_v1.md` and its v2/v3
addenda; scoring rules unchanged (AGREES / DISAGREES / SCHOLARS-SPLIT /
NOT-TREATED, per family, exact fractions).

**Chain caveat, recorded up front.** The standing protocol's chain is Opus
executes, Gemini reviews, Fable finalizes — because Fable authored
FAMILY_DEFINITIONS. This mini-pass was executed end-to-end by a single
Fable-family agent on Damian's instruction, with no Opus draft and no Gemini
review. It is a screening check, not a full protocol run: its verdicts are
advisory, and any DISAGREES it had produced would have needed the full chain
before acting. It produced none.

## Sample

Drawn from `seed.json` (1555 edges) with Python `random.Random(20260813)`,
pools sorted by (subject, relation, object) before sampling. Frame: edges with
`relation_family.state == "assigned"` and `by` containing "agreed". Pool
sizes: psychic-effect 121, dependence 32, instrumentality 12. Drawn: 5 + 4 + 3.

Sources searched (all five usable texts in `data/secondary/`, per MANIFEST):
Samuels/Shorter/Plaut *Critical Dictionary*; Edinger *Anatomy of the Psyche*,
*The Mysterium Lectures*, *Ego and Archetype* (noisy OCR — both quotes used
as evidence were verified against the PDF page image, printed pp. 69/215/261);
von Franz *Alchemy: An Introduction* (full text).

## Per-item results

### psychic-effect (5 items)

| # | Edge (CW §) | Score | Evidence |
|---|---|---|---|
| 1 | chthonic-mother \| carries-out \| the-sacrifice (9i §311) | NOT-TREATED | The Kore-vision torture scene is untreated in all five texts ("Kore" absent from four of them). Nearest miss: Samuels s.v. Great Mother, pp. 62–3, reproduces §158's negative pole ("anything that devours, seduces, and poisons") — the chthonic mother as destructive agent, but that is an attribute list quoted from Jung, not a rendering of this pair. |
| 2 | dionysos \| undergoes \| rebirth (9i §195) | AGREES | Edinger, *Anatomy*, mortificatio ch.: Greek tragedy as "the ritual re-enactment of the death and rebirth of the year-spirit (equated with Dionysus)", in which the hero "undergoes suffering and defeat" before the rebirth; solutio ch.: the infant Dionysus "dismembered by the Titans". A dynamic process the god passes through — the family's `undergoes` shape. |
| 3 | mother-complex \| leads-to \| incest (9i §168) | AGREES (analogue) | Samuels s.v. incest, pp. 74–6: "Cases of actual incest result when the symbolic nature of these interactions is bypassed"; s.v. homosexuality, pp. 67–9: "an over-developed mother-complex or father-complex" produces the sexual-relational outcome, "This leads to homosexuality later on." Complex → outcome rendered as produced effect. The daughter's-Eros passage itself is not quoted by any source. |
| 4 | the-unconscious \| overwhelms \| consciousness (9i §47) | AGREES | Samuels s.v. ego, pp. 50–1: "the ego may be overwhelmed by an inner content arising out of the unconscious"; s.v. numinosum: contents "break through the constraints of the EGO and overwhelm the conscious personality", "invasions of the unconscious"; s.v. complex, pp. 33–5: "A complex may overwhelm the ego (as in PSYCHOSIS)". A dynamic act with an outcome, in three separate entries. |
| 5 | scaiolae \| …intervene-and-stimulate… \| melusina (13 §215) | NOT-TREATED | Zero occurrences of "Melusina"/"Melusine" and "Scaiolae" in all five texts. Consistent with report v3's item-15 finding that von Franz states she avoids the Paracelsus material; Samuels and Edinger mention Paracelsus but never this pair. |

Treated agreement: **3/3 AGREES, 0 DISAGREES, 2 NOT-TREATED.**

### dependence (4 items)

| # | Edge (CW §) | Score | Evidence |
|---|---|---|---|
| 6 | the-unconscious \| demands \| the-sacrifice (9i §433) | AGREES | Samuels s.v. sacrifice, pp. 132–3: "Sacrifice is the price we pay for CONSCIOUSNESS"; "the necessity for sacrifice … an essential part of the cost"; "the SELF requires it of me". S.v. regression, pp. 129–30: "The cost or SACRIFICE inherent in progression is a loss of the security that merger with a parent figure provides" — release from unconscious merger has sacrifice as its standing price. Requirement language throughout, never act language. |
| 7 | artifex \| is-not-the-master-of-the-stone-but-rather-the-minister-of \| lapis (12 §142) | AGREES (analogue) | The dictum itself is untreated verbatim. The analogue is anchored by the sources' own equations: Samuels' alchemy glossary, pp. 13–15, "Adept: … symbolic of ego"; Edinger, *E&A* p. 261 (PDF-verified), "the Philosophers' Stone is a symbol for the Self". On that pair both render subordination: *E&A* p. 69, "a transpersonal center to which the ego is subordinate"; p. 215, "the ego is subordinated to the Self"; Samuels s.v. self, pp. 135–7, "the supraordinate personality". Subordination is dependence's own defining word. |
| 8 | great-mother \| presides-over \| rebirth (9i §158) | AGREES | Samuels s.v. Great Mother, pp. 62–3, reproduces §158's characterization including "the magical authority of the female" and "all that cherishes and sustains, that fosters growth and fertility" — authority over the transformation sphere. Edinger uses the identical presiding shape for a cognate deity-process pair: "Eris … presides over separatio" (*Anatomy*, separatio ch.). Noted, not counted against: Edinger's solutio ch. renders "a return to the womb for rebirth" — mother-as-medium, an instrumentality-shaped rendering, but of a different pair (solutio \| rebirth); pair-level discipline excludes it, as in report v3 item 27. |
| 9 | luna \| borrows-light-from \| sol (14 §117) | AGREES | von Franz, *Alchemy*, p. 149: "the sun has light while the moon only borrows from the sun". Edinger, *Mysterium*, pp. 114–15: the moon "receives the light of the sun"; Plotinus' moon "which receives its light from the sun"; "the ego as receiver of the transpersonal energy … is analogous to the moon". Both render a standing derivative condition; neither renders a dynamic act. |

Treated agreement: **4/4 AGREES, 0 DISAGREES, 0 NOT-TREATED.**

### instrumentality (3 items)

| # | Edge (CW §) | Score | Evidence |
|---|---|---|---|
| 10 | artifex \| …performed-by-means-of \| imaginatio (13 §173) | AGREES | von Franz, *Alchemy*, p. 78: alchemy is "something like active imagination, performed with chemical substances"; "Active imagination can be done … by collecting substances and mixing them. That is what these people did." The imagination as the operative means of the work. |
| 11 | the-self \| is-perceived-through \| projection (9i §315) | AGREES | Samuels s.v. projection, pp. 113–14: "projection as the means by which the contents of the inner world are made available to ego-consciousness"; "without the carrier there would be no meeting". S.v. rebirth, pp. 126–7: "The inner figure that personifies the larger self is traditionally found in PROJECTION." The literal word is "means". |
| 12 | temenos \| is-taboo-area-where-dreamer-can-meet \| the-unconscious (12 §63) | AGREES | Samuels s.v. temenos, pp. 148–9: an analytic precinct, synonym "the hermetically sealed vessel", "the closed container within which OPPOSITES transform"; the circumambulation entry: "the containment necessary during ANALYSIS in order to withstand the tensions produced by the meeting of OPPOSITES". Edinger, *Mysterium*, p. 118: a temenos "centers, focuses and delimits the attention and energy being poured into the procedure". Enabling precinct — the means of the meeting. |

Treated agreement: **3/3 AGREES, 0 DISAGREES, 0 NOT-TREATED.**

## The boundaries under load

The sample happens to exercise both boundaries CW 8 will lean on, and the
scholars' own language sorts the same way the rules do:

- **psychic-effect vs dependence** (items 4 and 6): Samuels uses invasion
  language for the one ("invasions of the unconscious … overwhelm") and price
  language for the other ("requires", "necessity", "the price we pay") — the
  act/standing-condition line falls exactly where the v0.7.1 boundary rule
  draws it.
- **dependence vs instrumentality** (items 9 and 10): von Franz renders the
  borrowed light as a standing condition and the imagination as a means used
  *to* work, in the same book, without strain against either definition.

## Verdicts

| Family | Treated | Agreement | Verdict |
|---|---|---|---|
| psychic-effect | 3 of 5 | 3/3 | **HOLDS** |
| dependence | 4 of 4 | 4/4 | **HOLDS** |
| instrumentality | 3 of 3 | 3/3 | **HOLDS** |

No DISAGREES, no SCHOLARS-SPLIT. The two NOT-TREATED items are the two
CW 9i mythological-case items (the Kore torture vision; the Paracelsian
Melusina pair) — the on-disk stack is alchemy- and general-theory-weighted,
and the Critical Dictionary carried 7 of the 10 treated items. Worth knowing
for CW 8: its psychic-energy register is closer to Samuels' territory than
CW 9i's mythography was, so coverage should be no worse.

## One PROPOSAL (wording, not defect — Damian's ruling)

The check found no external misfit, but item 12 sits on an internal wording
gap worth closing before CW 8 mints edges on it. Instrumentality's opening
sentence fixes the means to one slot:

- Current: "The object is the MEANS by which the subject is reached, enabled,
  effected or made possible."
- Proposed: "One term is the MEANS by which the other is reached, enabled,
  effected or made possible; the means term may sit in either slot (see
  seeds)."

The family's own seed list already carries both directions (`temenos
enables-meeting-with the-unconscious` has the means as subject; `mandala
is-built-up-through active-imagination` has it as object), and the sampled
temenos edge follows the seeds, not the sentence. The literature is
indifferent to slot — Samuels renders the temenos-as-means relation exactly
as the family does. The risk is internal: a CW 8 miner or arm reading the
sentence strictly could route subject-as-means edges away from the family.
"On the Nature of the Psyche" is thick with by-means-of constructions, so the
gap would get traffic. No item flips under the proposal; predicted effect on
two-arm agreement is neutral-to-positive on instrumentality candidates.

## Recommendation

**GO** for the CW 8 arc on the external-validity criterion: all three target
families hold against the literature on this sample, 10/10 treated items
AGREES. The wording proposal above is independent of the GO — it can be
ruled on before or during the arc, but a ruling before the first CW 8 batch
would be cheapest.
