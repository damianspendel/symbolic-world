# The method — page copy (Fable-authored 2026-08-07; rewritten by Damian 2026-10-18, carried 2026-10-20)

Copy for the `#/method` route. Damian's rewrite is wired verbatim; the build
substitutes `{{token}}` values from `atlas.json` meta / method stats at build
time — these are the numbers that move. Bare numbers in the text are frozen
measured results; the build registers them in the copy assertion's
method-constants allowlist with their source noted here.

Sources for the frozen numbers: 86% — family_pass_summary.json. The dispute
count binds from disputes.json as {{disputes}}. The family-calibration figures
(19/19, 20/20, 38/40) were WITHDRAWN 2026-08-12 after the blind code
inspection (RULES.md #12) and live only in the version-bound records per
RULES.md #16. The 14-of-20 themis figure left the copy in the 2026-10-18
rewrite.

---

## What this is

The Symbolic World is a map of C. G. Jung's symbolic thought: {{nodes}}
symbols, figures and concepts, joined by {{edges}} relations, resting on
{{refs}} citations to his *Collected Works* (CW). Every claim was proposed by
one AI model (Opus 5 class) after reading the CW and judged against its source
paragraph by a different model (Fable 5 class); an auditor (Gemini) from a
different vendor re-reads each new batch in full — {{xv_pct}}% of all {{refs}}
citations have been certified this way. Every claim can be considered a
transaction in a ledger: the exact paragraph, a verbatim quote, and the record
of which model (or expert) checked what. This is a map of assertions, not a
Jungian reading.

[figure: one claim, drawn — the node `lapis` joined by the labelled relation
`is-projection-of` to the node `the-self`, with its citation chip CW 9ii §264.
The first clause of the narrative on the landing page rests on exactly this
edge.]

Reading it: the stone (lapis) is claimed to be a projection of the self, Jung
says so at paragraph 264 of *Aion*, and clicking the claim on this site shows
the verbatim citation.

## One corpus

Everything comes from a single source: the Bollingen edition of the *Collected
Works*, in English. No secondary literature, no commentary, no symbol
dictionaries. That keeps the map close to Jung's own text, at the cost of
breadth.

[figure: the works bar, as it appears at the bottom of the atlas]

The bar along the bottom of the atlas shows the corpus: one segment per
volume, sized by how much verified evidence it carries, so where mining has
gone deep is visible immediately. The segments enable scope selection: click
one and the atlas shows only that volume's claims.

## Reading the atlas

[figure: the metals legend — six node kinds, six metals]

The type of node is indicated by node colour. The palette borrows alchemy's
metals: gold for concepts, silver for symbols, copper for figures, iron for
operations, verdigris for substances, lead for motifs. Alchemy assigned its
metals to the planets; mapping node kinds is a design choice for the atlas,
and not authoritative.

- **Search** finds a symbol, a relation, a family, quote text, or a citation
  such as CW 14 §1. Typing offers completions, and choosing a symbol or a
  family opens it.
- **Click** a node to read its connections; click a connection to open the
  citation itself: relation, quote, paragraph, verdicts. **Copy link** on any
  selection gives a URL that reopens it.
- **The chips** beside the search box are the active filters: volume, family,
  voice, layer. Remove one with its ×.
- **The bar along the bottom** selects volumes; each segment is sized by the
  verified evidence that volume carries.
- Every citation shows a status dot: green, human-validated; amber, machine-verified default without human validation; red, disputed, on the record. These can be viewed in the ledger.

## How a claim gets in

Five stations.

1. **Propose.** An Opus-family model reads a collection of paragraphs and
   proposes claims, each with a verbatim citation.
2. **Check.** A machine confirms the quote is letter-exact in its paragraph and
   at most 25 words, and that the relation is well formed, i.e. structured as a
   relationship between two nodes. Failures are then excluded.
3. **Gate.** A Fable-family model judges every claim against its full source
   paragraph. It is hostile — i.e. it seeks to challenge aggressively — by
   default: the claim survives only if, in the model's judgment, the paragraph
   supports it.
4. **Audit.** A Gemini model re-reads what survived, before any of it touches
   the graph. Universal for every batch since the *Aion* arc (mid-2026).
   (Earlier material was audited by sampling, and evidenced in the ledger;
   {{xv_stamped}} of {{refs}} citations have been audited this way as at time
   of publication.) When gate and auditor disagree, the auditor wins.
5. **Merge.** The claim enters with its provenance stamped: dates, verdicts,
   corrections.

The rule underneath all five: **the model that proposes a claim is never the
model that signs it off.** Proposer and gate are different model families
(Anthropic's Opus and Fable lines); the auditor is a different vendor
altogether (Google's Gemini). This is a standing arrangement.

The checks remove real material: in the most recent window, {{last_proposed}}
proposed citations became {{last_merged}} merged ones.

## Human oversight

A person rules on disagreements, decides releases, and answers for what is
published.

- **Gold set.** {{human_chips}} claims carry a *human-validated* mark in the
  [ledger](/ledger): a person read the cited paragraph. The rest carry the
  amber dot: machine-verified without human validation.
- **Adjudication.** Two blind arms sort relations into {{families}} families:
  one Opus-family model, one Gemini, each reading the definitions document and
  the edge, neither able to see the other's answer. These arms disagree on
  {{queue}} claims today. No model is allowed to break a tie; this is
  performed by a human in the loop: a person rules, in sittings. The rulings
  land in the ledger. An assignment is recorded with the ruleset version it
  was agreed under, because a later version can retire the rule it rested on.
- **Refusals are kept apart.** *No family* means our vocabulary is short. *Text
  undecided* means Jung's own sentence hedges between two readings. Pooling them
  would let a thin vocabulary hide inside a hedge.
- **Disputes.** {{disputes}} challenges are on the record with their outcomes,
  in the [dispute log](/disputes).
- **Publication.** Releases, deploys and rulings are human decisions. Nothing
  here publishes itself.

## Confidence levels

The checks are themselves checked:

- Every one of the {{refs}} quotes is mechanically verified against the
  corpus. The verification set seeds seven deliberately corrupted claims — so
  far, all seven have been caught on every run. Whether a paragraph supports
  its claim is a judgment call made by a model. It is not a mechanical proof.
- The family layer is checked by seeding corruptions among real assignments.
  It reported catching everything planted in its early runs. A family label
  means: two models, judging independently, agreed on the assignment of the
  relation to the family. Also here, in the case of disagreement, a human
  decides.
- The classification vocabulary was checked outside this repository, against
  {{ev_works}} works of scholarship: {{ev_agrees}} of {{ev_treated}} treated
  items agreed with our families. We have also published the disagreements
  ([the check](/ontology#checked)). It tests the classification of relations
  into families, not whether a claim is true.
- The two blind classification arms agreed on 86% of {{edges_classified}}
  relations. Agreement measures whether the definitions can be followed
  consistently, not whether they are right: neither arm is authoritative.
  Definitions were drafted by one of the model families working in this
  pipeline.

What the instruments do not cover:

| Known limit | Options |
|---|---|
| One human reviewer; no second annotator yet | Independent second annotation with agreement statistics |
| A class of identity drift (two names for one thing entering as two things) is invisible to the current audit | No instrument yet |
| English translation only (Hull) | German cross-check against the *Gesammelte Werke* |
| Claims are checked at paragraph granularity; fidelity to Jung's movement of thought across an essay or volume is not checked | The graph is a map of assertions, not a reading. Opposing claims are mined where Jung himself qualifies, and the books remain the reading |

## The paper

The method was published with release v1.3.0: 248 symbols, 669 relations,
699 citations. That exact snapshot, atlas and ledger included, is preserved
unchanged at [/v1.3/](/v1.3/). The live counts at the top of every page show
how far the atlas has grown since, using the same methodology.

[citation block — wired from the repo's citation metadata; DOI
10.5281/zenodo.21631523]
