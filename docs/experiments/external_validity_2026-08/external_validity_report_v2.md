# External-validity check — report v2 (targeted re-run with local Edinger texts)

Supplements report v1; nothing in v1 is silently replaced. Pre-registration:
`external_validity_protocol_v2_addendum.md` (scope and rules fixed before any
search). New evidence: full local text of Edinger's *Anatomy of the Psyche*
and *The Mysterium Lectures* (`JungKG/data/secondary/`, gitignored under
`data/`; MANIFEST.md records provenance). The delivered von Franz file is a
4-page fragment — excluded, replacement needed. Chain: Opus executed the
16-item re-run against the local texts, Gemini reviewed all 16 delta entries
(all CONFIRMED, including a retraction of its own v1 claim), Fable finalized.

## What moved (4 of 16 re-run items)

| # | Edge | v1 final | v2 final | Why |
|---|---|---|---|---|
| 2 | christ \| is-a \| anthropos (archetypal-identity) | NOT-TREATED | DISAGREES | Edinger renders the relation as doctrine attributed to Paul plus place-for-place correspondence in the §611 quaternity ("The Second Adam … would correspond to Adam Kadmon", Mysterium p. 257); where the figures meet it is "his analogue in matter". Never a flat identity. Caveat: the rendering is of the Paul–Adam–Anthropos chain, not one bare predication of the pair. |
| 21 | lapis \| symbolizes \| christ (queued: corresp. vs symboliz.) | both arms DISAGREES | opus arm SCHOLARS-SPLIT, gemini arm DISAGREES | Camps: identity (Abraham; Edinger, *Anatomy* ch. 3: "the Philosophers' Stone was identified with Christ") vs parallel/analogy (Edinger, *Mysterium* p. 213: "the alchemists' parallel of the Philosophers' Stone to Christ"). The split runs through one author across two books. |
| 22 | lapis \| symbolizes \| anthropos (queued) | both arms DISAGREES (v1 finalization) | opus arm AGREES, gemini arm DISAGREES | Direct pair evidence supersedes the v1 quaternio inference: both volumes render the relation as a likeness between two known terms ("the statue is the final product of the Manichaean opus just as the Philosophers' Stone…", Mysterium p. 236; *Anatomy* ch. 6 joins them with "corresponds to"). Nothing runs the symbolization direction. The same-passage "synonym for" idiom is on the statue\|lapis pair, not this one. |
| 10 | raven \| symbolizes \| the-devil | NT + reviewer-supplied AGREES | NT, reviewer claim RETRACTED | The v1 Gemini claim (Anatomy, Mortificatio ch., raven→devil) fails against the full text: the raven is rendered only against the nigredo — "A common term for the nigredo is 'corvus'" (n. 37, citing CW 14 §727). Gemini accepted the retraction on review. |

Unchanged with better evidence: items 8, 16, 17, 18 (DISAGREES, now
two-source); item 1 (substantive null — both volumes treat the vas at
length, never as Mercurius); item 23 (SPLIT both arms, now anchored on the
cited paragraph itself: Edinger predicates the imago Dei of §681's
caelum/quintessence directly, Mysterium p. 287, so the identity camp sits on
the exact pair). Confirmed nulls: 5, 15, 19 (zero hits); 4, 7, 11 silent.

## Rates v2 — headline (verified renderings only), assigned + purposive, 22 items

| Family | AGREES | DISAGREES | SPLIT | NOT-TREATED |
|---|---|---|---|---|
| archetypal-identity (incl. 26) | 0/3 | 2/3 | 1/3 | 2 |
| correspondence (incl. 27) | 2/3 | 1/3 | 0/3 | 2 |
| symbolization | 2/2 | 0/2 | 0/2 | 2 |
| doctrinal-attribution | 1/2 | 1/2 | 0/2 | 1 |
| amplification | 0/3 | 3/3 | 0/3 | 0 |
| controls | 1/1 | 0/1 | 0/1 | 1 |
| **All** | **6/14** | **7/14** | **1/14** | **8** |

v1 was 6/13 / 6/13 / 1/13 / 9 NT. The move is one NT→DISAGREES (item 2).
Reviewer-supplied unverified claims drop from 4 to 3 (all Critical
Dictionary; one of the four was checked against text and failed — a measured
33%-checked failure rate that justifies keeping them out of the headline).

Queued v2: 21 opus-SPLIT / gemini-DISAGREES; 22 opus-AGREES /
gemini-DISAGREES; 23 both SPLIT (anchored); 24 position-AGREES /
composition-DISAGREES; 25 both NT.

## Findings — new or strengthened

**F1 (amplification) strengthened, now two-source.** The Mysterium Lectures
are a paragraph-by-paragraph commentary on CW 14 — these edges' home ground
— and Edinger treats the material as equations, synonymies and namings,
never as adduced parallels. His lecture on §154 organizes Luna under seven
headings and drops silver entirely. One v1 sub-claim is withdrawn: the
direction complaint on item 17 (Edinger runs nigredo as sentence subject,
matching the graph edge). P1 stands, minus the direction rider; F8 shrinks
to a one-case observation.

**F3 generalized: the idiom instability is within authors, not between
them.** v1 recorded Abraham writing identity and symbol idioms
interchangeably. Edinger does the same, more tightly: a section headed "The
Symbolic Equation Between Luna and the Church" opens with "are equated with
the moon" and reaches "comparable to Selene" on the same page; lapis|Christ
is identity in *Anatomy* and "parallel" in *Mysterium*. The
identity/symbolization/correspondence boundary the graph enforces has no
stable counterpart inside either reference author. Consequence for v0.7:
secondary-literature idiom cannot anchor identity assignments; only the
primary text's own predication can — which is what the sentence-subject
test already tries to do internally.

**F9 (new): the named-figure is-a rule loses its external anchor.** v0.6's
boundary rule "is-a on a named-figure pair is identity" was built on
`christ is-a anthropos` (gate catch, human-confirmed). Item 2 now scores
DISAGREES: Edinger renders the relation through attribution (Paul) and
correspondence, never flat identity. The rule's own worked example is
externally unsupported. Proposal P7 below.

**F10 (new): the identity↔correspondence queue shape may be genuinely
undecidable by scholarship.** Item 23's split is now anchored on the exact
pair and paragraph: Edinger states identity where Jacobi's method refuses
it. For the 14 queued items of this shape, the literature offers camps, not
a tiebreak — adjudication should expect to rule, not to find consensus.

**Lapis queue guidance sharpened:** for §451 (lapis|christ) the literature
is split between identity and parallel — neither queued arm is cleanly
backed; for §335 (lapis|anthropos) correspondence — the Opus arm — is the
supported answer.

## Proposal updates (report v1's P1–P6 otherwise stand)

**P1 — unchanged, strengthened.** Two independent reference authors treat
the `amplified-by` material as content relations. Drop the v1 direction
rider.

**P7 (new, from F9) — narrow the named-figure is-a rule.** Current: "when
both endpoints are named Figures and the quote asserts they ARE one
another, `is-a` is `archetypal-identity`." Proposed: add "…and the
predication is the quote's own, not a doctrine the paragraph attributes (an
attributed equation goes to doctrinal-attribution per the existing
precedence rule)." Flips: possibly item 2's edge, depending on how CW 14
§565's "The second Adam is Christ" reads under claim_type; queues it for
adjudication rather than auto-identity. Predicted effect: small volume,
but removes the one identity rule whose worked example now carries external
counter-evidence.

**P2 — extended by F3.** The worked note should state that identity idioms
in the reference literature (Abraham's definitions, Edinger's "symbolic
equation") do not license identity assignments; within-author instability
is the measured norm.

## Standing gaps after v2

- Critical Dictionary still missing: 3 unverified reviewer claims (items 2,
  5, 19) hang on it; item 2 would likely become SCHOLARS-SPLIT if the
  claimed s.v. 'Anthropos' rendering verifies, given Edinger now sits on
  the other side.
- von Franz *Alchemy* file is a fragment; v1's renderings from it came from
  web fragments and stand unverified against full text.
- Items 4, 7, 11, 15 remain NOT-TREATED with no known source that treats
  them; likely true silences.
