# The method — page copy (Fable-authored, 2026-08-07)

Copy for the `#/method` route. Authored by the Fable session; the build wires it
verbatim and MUST NOT edit prose. `{{token}}` values bind to `atlas.json` meta /
method stats at build time — these are the numbers that move. Bare numbers in
the text are frozen measured results; the build registers them in the copy
assertion's method-constants allowlist with their source noted here.

Sources for the frozen numbers: 19/19 — step-0 gate
calibration 2026-08-06; 20/20 and 38/40 — in-situ recalibration 2026-08-07,
seed 90507; 86% — family_pass_summary.json; 14 of 20 — themis competency run;
19 dispute rows — disputes.json; 10 rulings — family_adjudication_rulings.

---

## What this is

The Symbolic World is a map of C. G. Jung's symbolic thought: {{nodes}}
symbols, figures and concepts, joined by {{edges}} relations, resting on
{{refs}} citations to his *Collected Works*. Nothing is here because a model
said so. A claim enters this graph only after three AI models — two different
model families from one vendor, and an auditor from another — have each had a
chance to kill it, and every claim keeps the receipt: the exact paragraph, a
verbatim quote, and the record of who checked what.

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

Five stations, no exceptions.

1. **Propose.** An Opus-family model reads a window of paragraphs and proposes
   claims, each with a verbatim quote.
2. **Check.** A machine confirms the quote is letter-exact in its paragraph and
   at most 25 words, and that the relation is well formed. Failures are
   dropped, not argued with.
3. **Gate.** A Fable-family model judges every claim against its full source
   paragraph. It is hostile by default: the claim survives only if the
   paragraph actually supports it.
4. **Audit.** A Gemini model re-reads everything that survived — before any of
   it touches the graph. When gate and auditor disagree, the auditor wins.
5. **Merge.** The claim enters with its provenance stamped: dates, verdicts,
   corrections.

The rule underneath all five: **the model that proposes a claim is never the
model that signs it off.** Proposer and gate are different model families
(Anthropic's Opus and Fable lines); the auditor is a different vendor
altogether (Google's Gemini); and the roles never swap.

The stations bite. In the most recent window, {{last_proposed}} proposed
citations became {{last_merged}} merged ones; the difference is what the
checks removed.

## Where people rule

Machines verify; people decide. Three places the human hand is in the record:

- **The gold set.** {{human_chips}} claims in the [ledger](/ledger.html) carry
  a *human-validated* mark: a person read the source paragraph and confirmed
  the claim. This is the reference set the machine verdicts are measured
  against. Most claims are machine-verified only — the amber dot is the
  honest default, not a defect.
- **The dispute log.** 19 public challenges to specific claims, each with its
  outcome on the record. A graph that cannot show you its corrections is
  asking for trust it has not earned.
- **The family layer.** Relations are sorted into {{families}} families of
  meaning by two blind model arms. Where the arms disagree — {{queue}} claims
  today — no model breaks the tie. The claim is marked *pending review* and
  queued for a human ruling, and every ruling lands in the ledger signed and
  dated, the same treatment the machine verdicts get.

## Confidence levels

The checks are themselves checked:

- Every one of the {{refs}} quotes is machine-verified against the corpus; the
  harness also carries seven deliberately corrupted claims, and all seven are
  caught on every run.
- The family gate was calibrated by hiding planted errors among real
  assignments: it caught 19 of 19 in the first round, 20 of 20 in the second —
  naming the correct family every time — while wrongly flagging only 2 of 40
  clean assignments.
- The two blind classification arms agreed on 86% of {{edges_classified}}
  relations. Twenty standing questions about Jung's thought are asked of the
  graph after every change; it currently answers 14 in full.

What the instruments do not cover, stated plainly:

| Known limit | Options |
|---|---|
| One human reviewer; no second annotator yet | Independent second annotation with agreement statistics |
| A class of identity drift (two names for one thing entering as two things) is invisible to the current audit | No instrument yet — known gap, on the record |
| English translation only (Hull) | German cross-check against the *Gesammelte Werke* |

## The paper

The method was published with release v1.3.0 — 248 symbols, 669 relations,
699 citations. That exact snapshot, atlas and ledger included, is preserved
unchanged at [/v1.3/](/v1.3/), and the paper describes it. The live counts at
the top of every page show how far the atlas has grown since, under the same
gates.

[citation block — wired from the repo's citation metadata; DOI
10.5281/zenodo.21631523]
