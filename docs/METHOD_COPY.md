# The method — page copy (Fable-authored 2026-08-07; rewritten by Damian 2026-10-18, carried 2026-10-20)

Copy for the `#/method` route. Damian's rewrite is wired verbatim; the build
substitutes `{{token}}` values from `atlas.json` meta / method stats at build
time — these are the numbers that move. Bare numbers in the text are frozen
measured results; the build registers them in the copy assertion's
method-constants allowlist with their source noted here.

Sources for the frozen numbers: the dispute count binds from disputes.json as
{{disputes}}. The arm agreement binds live from seed.json's relation_family.by
since 2026-11-11 (Damian: "go with the live figure"); the earlier 86% came from
pipeline/work/family_pass_summary.json, which is not committed. The family-calibration figures
(19/19, 20/20, 38/40) were WITHDRAWN 2026-08-12 after the blind code
inspection (RULES.md #12) and live only in the version-bound records per
RULES.md #16. The 14-of-20 themis figure left the copy in the 2026-10-18
rewrite.

v2.4.1 method corrections (drafted 2026-11-13, approved by Damian as drafted):
the family-gate figures bind pooled over every calibration record at the
binding ruleset, PASS and FAIL alike, with a Wilson 95% interval computed in
the build (the "Best of N" rule in docs/GLOSSARY.md; the releases pin still
names the PASS record). The gate model id comes from the records' gate_model
field. {{human_rulings}} binds live: edges whose relation_family.by starts
"human-adjudication". The audit-finding figures in step 4 (87 of 134 windows,
404 findings, 176 dropped, 88 corrected, 139 overruled, 1 deferred) are frozen:
`python3 tools/findings/ablation.py` on interim-v1 at seed sha256 42ab7afd,
overall.adjudication_outcomes and the windows table. tools/findings/ is not on
the release branch, so the build registers 134, 404, 176 and 139 in the
method-constants allowlist.

---

## What this is

The Symbolic World is a map of C. G. Jung's symbolic thought: {{nodes}}
symbols, figures and concepts, joined by {{edges}} relations, resting on
{{refs}} citations to his *Collected Works* (CW). An AI model from the Opus family
proposed each claim from a window of paragraphs, and a model of a different
family (Fable) judged it against its source paragraph. An auditor from another
vendor (Google's Gemini) then re-read the result: {{xv_pct}}% of the {{refs}}
citations carry an audit stamp, and all but {{stamps_bare}} of the stamps name the
audit and its date. Each claim is
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
   at most 25 words long, counting runs of letters, and that the claim has the form of one relation between
   two nodes. The pipeline drops claims that fail.
3. **Gate.** A Fable-family model judges every claim against its full source
   paragraph. Its instructions make rejection the default: a claim survives
   only if the model finds that the paragraph supports it.
4. **Audit.** A Gemini model re-reads each claim that survived the gate, as a
   rule before it enters the graph. The step became the rule in mid-2026, during
   work on *Aion*. The first *Aion* window entered the graph before its audit,
   which ran afterwards. Later passes audited the older material, by whole volumes
   and by samples, and each citation's stamp says which. {{xv_stamped}} of
   {{refs}} citations carry a stamp. The other {{unstamped}}, in *Aion* and the
   volumes mined after it, have none yet, and the record does not say why. Every
   finding the auditor raises goes to adjudication. In the 87 of 134 windows
   whose records hold the adjudication, the auditor raised 404 findings.
   Adjudication upheld 176 of them and dropped the claim, upheld 88 as a
   correction to the claim's type, confidence or relation, overruled 139 and
   kept the claim with the reason written on it, and deferred 1. For the other
   windows the records do not say how adjudication settled each finding.
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

- **Validated by a person.** {{human_chips}} claims carry a *human-validated* mark in the
  [ledger](/ledger): a person read the cited paragraph. The rest carry the
  amber dot: machine-verified without human validation.
- **Adjudication.** Two models sort each relation into one of {{families}}
  families, working blind: one Opus-family model and one Gemini, each given the
  definitions and the claim, neither able to see the other's answer. A
  Fable-family model drafted the definitions; neither classifying model comes
  from that family. {{queue}} relations wait for a person's ruling, most because
  the two models disagreed, a few because a later check disputed their
  agreement. No model breaks a tie. Only a person settles one, and the ruling
  goes into the ledger. {{human_rulings}} rulings are on record so far. An assignment is recorded with the ruleset version it
  was agreed under, because a later version can retire the rule it rested on.
- **We count two kinds of unclassified relation separately.** *No family* means
  none of our families fits. *Text undecided* means Jung's sentence supports two
  readings. Counting them together would hide gaps in our vocabulary among real
  ambiguities in the text.
- **Disputes.** {{disputes}} challenges are on the record with their outcomes,
  in the [dispute log](/disputes).

## How we test the checks

- Every one of the {{refs}} quotes is mechanically verified against the
  corpus. The verification set seeds seven deliberately corrupted claims. The
  test suite fails if any of the seven gets through, and it passes at this
  release. Whether a paragraph supports its claim stays a model's judgment. The
  gate makes it first. The auditor then reads the claim as the gate left it,
  without the gate's verdict or reasons.
- The family gate faces the same kind of test: we plant corrupted assignments
  among real ones. At ruleset {{ruleset}} the test ran {{cal_runs}} times, each
  with a fresh sample and {{cal_planted_per_run}} fresh planted errors, and
  {{cal_failed}} of the runs missed one error and failed the pass bar of
  catching all of them. Pooled across the runs, the gate caught {{cal_caught}}
  of {{cal_planted}} planted errors ({{cal_caught_pct}}%, 95% interval
  {{cal_caught_lo}} to {{cal_caught_hi}}%) and left {{cal_clean}} of
  {{cal_clean_of}} clean assignments alone. The family gate is
  gemini-3.1-pro-preview, the same model as one of the two classifying models,
  so this check is not cross-vendor. A family label means two models, judging
  independently, put the relation in that family, or a person ruled where they
  disagreed.
- We checked the classification vocabulary against {{ev_works}} published works
  of Jung scholarship. Where the literature discusses a relation at all
  ({{ev_treated}} cases), scholars' readings matched our family in
  {{ev_agrees}}, differed in {{ev_disagrees}} and were split in {{ev_split}}.
  [The design page](/ontology#checked) lists the disagreements and the rule
  changes they produced. The check tests our sorting of relations into
  families. It says nothing about whether a claim is true.
- The two classifying models agreed on {{arms_agreed}} of {{arms_compared}}
  relations ({{arms_pct}}%): the relations whose record shows either their
  agreement or a disagreement for a person to settle. The other {{arms_other}}
  rest on a precedent or on a later check. Agreement shows whether two readers
  apply the definitions the same way. It does not show that the definitions
  are right: neither model is authoritative.

What the instruments do not cover:

| Known limit | What would close it, or what offsets it |
|---|---|
| One human reviewer; no second annotator yet | Independent second annotation with agreement statistics |
| Nothing measures recall: every check tests what entered the map, and none estimates what Jung asserts that the map lacks | A sampled audit of recall, paragraph by paragraph |
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
