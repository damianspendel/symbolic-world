# The method — page copy (Fable-authored 2026-08-07; rewritten by Damian 2026-10-18, carried 2026-10-20)

Copy for the `#/method` route. Damian's rewrite is wired verbatim; the build
substitutes `{{token}}` values from `atlas.json` meta / method stats at build
time — these are the numbers that move. Bare numbers in the text are frozen
measured results; the build registers them in the copy assertion's
method-constants allowlist with their source noted here.

Sources for the frozen numbers: the dispute count binds from disputes.json as
{{disputes}}. The 86% arm-agreement figure left the copy on 2026-11-11: its
only source, pipeline/work/family_pass_summary.json, is not committed. The family-calibration figures
(19/19, 20/20, 38/40) were WITHDRAWN 2026-08-12 after the blind code
inspection (RULES.md #12) and live only in the version-bound records per
RULES.md #16. The 14-of-20 themis figure left the copy in the 2026-10-18
rewrite.

---

## What this is

The Symbolic World is a map of C. G. Jung's symbolic thought: {{nodes}}
symbols, figures and concepts, joined by {{edges}} relations, resting on
{{refs}} citations to his *Collected Works* (CW). One AI model (Opus family)
proposed each claim from a window of paragraphs, and a model of a different
family (Fable) judged it against its source paragraph. An auditor from another
vendor (Google's Gemini) then re-read the result: {{xv_pct}}% of the {{refs}}
citations carry an audit stamp that names the audit and its date. Each claim is
a ledger entry: the exact paragraph, a verbatim quote, and a record of which
model, or which person, checked what. This is a map of assertions, not a
Jungian reading.

A relation joins two nodes. Each citation that supports it, a paragraph with
its quote, is one claim, so a relation can rest on several.

[figure: one claim, drawn — the node `lapis` joined by the labelled relation
`is-projection-of` to the node `the-self`, with its citation chip CW 9ii §264.
The first clause of the narrative on the landing page rests on exactly this
edge.]

Read it as: Jung says, at paragraph 264 of *Aion*, that the stone (lapis) is a
projection of the self. Clicking the claim in the atlas shows the quote.

## One corpus

Everything comes from a single source: the Bollingen edition of the *Collected
Works*, in English. No secondary literature, no commentary, no symbol
dictionaries. That keeps the map close to Jung's own text, at the cost of
breadth.

[figure: the works bar, as it appears at the bottom of the atlas]

Click a segment and the atlas shows only that volume's claims.

## Reading the atlas

[figure: the metals legend — six node kinds, six metals]

Node colour shows the kind of node. The palette borrows alchemy's metals: gold
for concepts, silver for symbols, copper for figures, iron for operations,
verdigris for substances, lead for motifs. Alchemy assigned its metals to the
planets. Assigning them to node kinds is our design choice and carries no
alchemical meaning.

- **Search** finds a symbol, a relation, a family, quote text, or a citation
  such as CW 14 §1. Typing offers completions, and choosing a symbol or a
  family opens it.
- **Click** a node to read its connections; click a connection to open the
  citation itself: relation, quote, paragraph, verdicts. **Copy link** on any
  selection gives a URL that reopens it.
- **The chips** beside the search box are the active filters: volume, family,
  voice, layer. Remove one with its ×.
- Every citation shows a status dot: green, human-validated; amber, machine-verified default without human validation; red, disputed, on the record. The ledger lists all three.

## How a claim gets in

1. **Propose.** An Opus-family model reads a window of consecutive paragraphs
   and proposes claims, each with a verbatim citation.
2. **Check.** A machine confirms the quote is letter-exact in its paragraph and
   at most 25 words, and that the claim has the form of one relation between
   two nodes. The pipeline drops claims that fail.
3. **Gate.** A Fable-family model judges every claim against its full source
   paragraph. Its instructions tell it to reject: a claim survives only if the
   model finds that the paragraph supports it.
4. **Audit.** A Gemini model re-reads every claim that survived the gate,
   before it enters the graph. That has been the procedure for every batch
   since mid-2026, when work on *Aion* began. Later passes audited the older
   material, by whole volumes and by samples, and each citation's stamp says
   which. {{xv_stamped}} of {{refs}} citations carry a stamp. The other
   {{unstamped}}, all in volumes mined since *Aion*, have none yet. Where gate
   and auditor disagree on whether the paragraph supports the claim, the
   auditor's verdict stands. Findings about claim type or confidence become
   corrections, and a recorded project convention can overrule the auditor;
   the claim's record then shows the override.
5. **Merge.** The claim enters with its provenance stamped: dates, verdicts,
   corrections.

At every step, the model that proposes a claim never signs it off.
Proposer and gate are different model families (Anthropic's Opus and Fable
lines) and the auditor is a different vendor (Google's Gemini).

The checks remove real material: across the {{windows_counted}} windows whose
records give both counts, {{all_proposed}} proposed citations became
{{all_merged}} merged ones.

## Human oversight

One person, the author, rules on disagreements, decides releases and answers
for everything the site publishes.

- **Gold set.** {{human_chips}} claims carry a *human-validated* mark in the
  [ledger](/ledger): a person read the cited paragraph. The rest carry the
  amber dot: machine-verified without human validation.
- **Adjudication.** Two models sort each relation into one of {{families}}
  families, working blind: one Opus-family model and one Gemini, each given the
  definitions and the claim, neither able to see the other's answer. A
  Fable-family model drafted the definitions; neither classifying model comes
  from that family. {{queue}} relations wait for a person's ruling, most because
  the two models disagreed, a few because a later check disputed their
  agreement. No model breaks a tie. A person rules on each one, and the ruling
  goes into the ledger. An assignment is recorded with the ruleset version it
  was agreed under, because a later version can retire the rule it rested on.
- **We count two kinds of unclassified relation separately.** *No family* means
  none of our families fits. *Text undecided* means Jung's sentence supports two
  readings. Counting them together would hide gaps in our vocabulary among real
  ambiguities in the text.
- **Disputes.** {{disputes}} challenges are on the record with their outcomes,
  in the [dispute log](/disputes).

## How we test the checks

- Every one of the {{refs}} quotes is mechanically verified against the
  corpus. The verification set seeds seven deliberately corrupted claims. So
  far, all seven have been caught on every run. Whether a paragraph supports
  its claim stays a model's judgment, which the gate and the auditor make
  independently.
- The family gate faces the same kind of test: we plant corrupted assignments
  among real ones. At ruleset {{ruleset}} it caught {{cal_caught}} of
  {{cal_planted}} planted errors and left {{cal_clean}} of {{cal_clean_of}}
  clean assignments alone. A family label means two models, judging
  independently, put the relation in that family, or a person ruled where they
  disagreed.
- We checked the classification vocabulary against {{ev_works}} published works
  of Jung scholarship. Where the literature discusses a relation at all
  ({{ev_treated}} cases), scholars' readings matched our family in
  {{ev_agrees}}, differed in {{ev_disagrees}} and were split in {{ev_split}}.
  [The design page](/ontology#checked) lists the disagreements and the rule
  changes they produced. The check tests our sorting of relations into
  families. It says nothing about whether a claim is true.
- Agreement between the two classifying models shows whether two readers apply
  the definitions the same way. It does not show that the definitions are
  right: neither model is authoritative.

What the instruments do not cover:

| Known limit | What would close it |
|---|---|
| One human reviewer; no second annotator yet | Independent second annotation with agreement statistics |
| A class of identity drift (two names for one thing entering as two things) is invisible to the current audit | No instrument yet |
| English translation only (Hull) | German cross-check against the *Gesammelte Werke* |
| Claims are checked at paragraph granularity; fidelity to Jung's movement of thought across an essay or volume is not checked | Partly offset: where Jung qualifies a claim, the map records the qualifying claim too. A reading of the essay or volume is still needed |

## The paper

The method was published with release v1.3.0: 248 symbols, 669 relations,
699 citations. That exact snapshot, atlas and ledger included, is preserved
unchanged at [/v1.3/](/v1.3/). The live counts at the top of every page show
how far the atlas has grown since. The checks grew too: the relation families
and the form rule for relations came after v1.3.0.

[citation block — wired from the repo's citation metadata; DOI
10.5281/zenodo.21631523]
