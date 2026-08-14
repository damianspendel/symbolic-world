# The method — page copy (Fable-authored, 2026-08-07)

Copy for the `#/method` route. Authored by the Fable session; the build wires it
verbatim and MUST NOT edit prose. `{{token}}` values bind to `atlas.json` meta /
method stats at build time — these are the numbers that move. Bare numbers in
the text are frozen measured results; the build registers them in the copy
assertion's method-constants allowlist with their source noted here.

Sources for the frozen numbers: 86% — family_pass_summary.json; 14 of 20 —
themis competency run. The dispute count is no longer frozen: it binds from
disputes.json as {{disputes}} (2026-08-14 — the typed 19 counted edge
attachments, of which there are 19 across 18 challenges). The
family-calibration figures (19/19, 20/20, 38/40) were WITHDRAWN 2026-08-12
after the blind code inspection (RULES.md #12) and live only in the
version-bound records per RULES.md #16.

---

## What this is

The Symbolic World is a map of C. G. Jung's symbolic thought: {{nodes}}
symbols, figures and concepts, joined by {{edges}} relations, resting on
{{refs}} citations to his *Collected Works*. Nothing is here because a model
said so. Every claim was proposed by one AI model and judged against its
source paragraph by a second, from a different model family; an auditor from a
different vendor re-reads each new batch in full, and {{xv_pct}}% of all
{{refs}} citations currently carry its stamp. Every claim keeps the receipt:
the exact paragraph, a verbatim quote, and the record of who checked what. A graph flattens: a
claim can be true to its paragraph and still lose the movement of thought
around it. This is a map of assertions, not a reading.

[figure: one claim, drawn — the node `lapis` joined by the labelled relation
`is-projection-of` to the node `the-self`, with its citation chip CW 9ii §264.
The first clause of the narrative on the landing page rests on exactly this
edge.]

Reading it: the stone (lapis) is claimed to be a projection of the self, Jung
says so at paragraph 264 of *Aion*, and clicking the claim anywhere on this
site shows the verbatim sentence.

## One corpus

Everything comes from a single source: the Bollingen edition of the *Collected
Works*, in English. No secondary literature, no commentary, no symbol
dictionaries. That choice costs breadth and buys depth.

[figure: the works bar, as it appears at the bottom of the atlas]

The bar along the bottom of the atlas is the corpus made visible: one segment
per volume, sized by how much verified evidence it carries — the alchemical
trilogy (CW 12, 13, 14) and *Aion* mined end to end, CW 9i in progress, five
further volumes represented where the deep volumes reach into them. The
segments select: click one and the atlas shows only that volume's claims.

## Reading the atlas

[figure: the metals legend — six node kinds, six metals]

Node colour is the kind of thing a node is. The palette borrows alchemy's
metals — gold for concepts, silver for symbols, copper for figures, iron for
operations, verdigris for substances, lead for motifs. Alchemy assigned its
metals to the planets; mapping node kinds onto them is this project's design
choice.

- **Search** finds a symbol, a relation, a family, quote text, or a citation
  such as CW 14 §1. Typing offers completions, and choosing a symbol or a
  family opens it.
- **Click** a node to read its connections; click a connection to open the
  claim itself — relation, quote, paragraph, verdicts. **Copy link** on any
  selection gives a URL that reopens it.
- **The chips** beside the search box are the active filters — volume, family,
  voice, layer. Remove one with its ×.
- **The bar along the bottom** selects volumes; each segment is sized by the
  verified evidence that volume carries.
- Every citation shows a status dot: green, a person validated it; amber,
  machine-verified only — the honest default; red, publicly disputed with the
  dispute on the record.

## How a claim gets in

Five stations.

1. **Propose.** An Opus-family model reads a window of paragraphs and proposes
   claims, each with a verbatim quote.
2. **Check.** A machine confirms the quote is letter-exact in its paragraph and
   at most 25 words, and that the relation is well formed. Failures are
   dropped, not argued with.
3. **Gate.** A Fable-family model judges every claim against its full source
   paragraph. It is hostile by default: the claim survives only if, in the model's
   judgment, the paragraph supports it.
4. **Audit.** A Gemini model re-reads what survived, before any of it touches
   the graph. Universal for every batch since the *Aion* arc (mid-2026);
   earlier material was audited by sampling, and each claim's receipt shows
   whether it carries the stamp — {{xv_stamped}} of {{refs}} citations do
   today. When gate and auditor disagree, the auditor wins.
5. **Merge.** The claim enters with its provenance stamped: dates, verdicts,
   corrections.

The rule underneath all five: **the model that proposes a claim is never the
model that signs it off.** Proposer and gate are different model families
(Anthropic's Opus and Fable lines); the auditor is a different vendor
altogether (Google's Gemini); and the roles never swap.

The stations bite. In the most recent window, {{last_proposed}} proposed
citations became {{last_merged}} merged ones; the difference is what the
checks removed.

## Human oversight

Machine checks are not decisions. Responsible use of AI needs human oversight: a person
rules on disagreements, decides releases, and answers for what is published.

- **Gold set.** {{human_chips}} claims carry a *human-validated* mark in the
  [ledger](/ledger): a person read the cited paragraph. The rest are
  machine-verified — the amber dot is the honest default, not a defect.
- **Adjudication.** Two blind arms sort relations into {{families}} families.
  Where they disagree — {{queue}} claims today — no model breaks the tie. A
  person rules, in sittings, and every ruling lands signed and dated.
- **Disputes.** {{disputes}} challenges are on the record with their outcomes,
  in the [dispute log](/disputes).
- **Publication.** Releases, deploys and rulings are human decisions. Nothing
  here publishes itself.

## Confidence levels

The checks are themselves checked:

- Every one of the {{refs}} quotes is mechanically verified, letter for
  letter, against the corpus (the harness also carries seven deliberately
  corrupted claims, and all seven are caught on every run). Whether a
  paragraph supports its claim is a model's judgment, not a mechanical proof
  — and the receipts show it as judgment.
- The family layer's own check — a gate tested by planting errors among real
  assignments — reported catching everything planted in its early runs. A code
  inspection we commissioned in August 2026 found that harness could not fully
  substantiate what "caught" means, so we withdrew those figures. The
  harness was rebuilt in tracked code; calibration re-runs per ruleset version,
  and its figures live in the version-bound records
  (`pipeline/family_calibration/records/`) rather than in this prose, because a
  number written here outlives the version it measured. A family label means
  this: two models, judging independently, agreed — and where they disagreed, a
  person decides.
- The classification vocabulary was checked outside this repository, against
  {{ev_works}} works of scholarship: {{ev_agrees}} of {{ev_treated}} treated
  items agreed with our family, and the disagreements are published beside them
  ([the check](/families#checked)). It tests the classification, not whether a
  claim is true.
- The two blind classification arms agreed on 86% of {{edges_classified}}
  relations. Agreement measures whether the definitions can be followed
  consistently — not whether they are right. Twenty standing questions about
  Jung's thought are asked of the graph after every change; it currently
  answers 14 in full.

What the instruments do not cover, stated plainly:

| Known limit | Options |
|---|---|
| One human reviewer; no second annotator yet | Independent second annotation with agreement statistics |
| A class of identity drift (two names for one thing entering as two things) is invisible to the current audit | No instrument yet — known gap, on the record |
| English translation only (Hull) | German cross-check against the *Gesammelte Werke* |
| Claims are checked at paragraph granularity; fidelity to Jung's movement of thought across an essay or volume is not checked | The graph is a map of assertions, not a reading — opposing claims are mined where Jung himself qualifies, and the books remain the reading |

## The paper

The method was published with release v1.3.0 — 248 symbols, 669 relations,
699 citations. That exact snapshot, atlas and ledger included, is preserved
unchanged at [/v1.3/](/v1.3/), and the paper describes it. The live counts at
the top of every page show how far the atlas has grown since, under the same
gates.

[citation block — wired from the repo's citation metadata; DOI
10.5281/zenodo.21631523]
