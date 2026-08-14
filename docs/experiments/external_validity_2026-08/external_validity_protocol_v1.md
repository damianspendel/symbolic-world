# External-validity check — execution protocol v1 (prepared, not started)

Charter: BACKLOG.md item 4 (family layer section). Question under test: would a
reader of Jungian scholarship agree with how the graph's relation families
classify Jung's assertions? Not claim truth — family fit.

Runs only after the author confirms the sample
(`external_validity_sample_v1.json`, seed 20260812; item 25 under
supplementary seed 20260812+1).

## Model chain (trust rule: proposer ≠ signer, per family)

- **Opus 5 — executor.** Does the literature search and drafts the per-item
  worksheet entries. Opus did not author FAMILY_DEFINITIONS (author family:
  Fable), so its readings of the secondary literature are independent of the
  document under test.
- **Gemini — reviewer.** Checks every worksheet entry: citation exists and
  says what Opus claims, quote within fair use, score follows the scoring
  rule, camps named where scholars split. Verdicts per item:
  CONFIRMED / CITATION-FAILS / SCORE-UNSUPPORTED / QUOTE-OVERLONG.
- **Fable 5 — finalizer.** Resolves Gemini findings, computes per-family
  rates, writes the report and ranked v0.7 proposals. Fable authored the
  definitions, so Fable never scores an item alone: every AGREES/DISAGREES
  entering the rates must carry Opus's draft and Gemini's CONFIRMED. Fable's
  own judgment appears only in the proposals section, labeled as such.

## Per-item worksheet schema (Opus fills one per sample item)

```
item, edge (subject | relation_effective | object), family (or queue split),
citation (CW vol §para), graph quote (verbatim from sample file, ≤25 words),
sources_consulted: [author, work, locator],
scholar_rendering: how each source renders the relation Jung asserts between
  these two terms (identity / analogy / symbol / doctrine-reported / other),
  with a short fair-use quote (<25 words, attributed) or a paraphrase,
score: AGREES | DISAGREES | SCHOLARS-SPLIT | NOT-TREATED,
score_reason: one sentence tying rendering to our family definition,
boundary_rule_implicated: which FAMILY_DEFINITIONS v0.6 wording the item
  tests (verbatim phrase), or none
```

## Scoring rules (fixed before search — RULES #11 analogue)

- AGREES: at least one named source renders the relation in our family's
  sense and none renders it against.
- DISAGREES: the consulted sources consistently render it in a different
  family's sense. Names the family they imply.
- SCHOLARS-SPLIT: named sources land in different families. Name the camps.
- NOT-TREATED: none of the consulted sources treats this pair's relation.
  Requires listing which sources were checked. NOT-TREATED is data.
- Queued items (21–25) are scored against BOTH arms' answers: which arm the
  literature sides with, or neither, or split.
- Rates reported per family, never pooled; exact fractions, no rounding into
  prose quantifiers.

## Source list (priority order)

Jacobi, *The Psychology of C.G. Jung*; Samuels/Shorter/Plaut, *A Critical
Dictionary of Jungian Analysis*; von Franz (esp. *Alchemy*, *Aurora
Consurgens*); Edinger (*Anatomy of the Psyche*, *Aion* commentary);
Shamdasani (*Jung and the Making of Modern Psychology*); Journal of
Analytical Psychology; supplementary where the pair is alchemical-image
specific: Abraham, *A Dictionary of Alchemical Imagery* (flagged as outside
the charter's named list — reviewer checks it is used only where the named
list is silent).

## Hard limits

- Read-only on the repo; nothing from secondary literature enters seed.json
  or any tracked file. Single-corpus invariant holds.
- Jung text: only the sample file's own ≤25-word quotes. Secondary
  literature: short attributed quotes within fair use, one per rendering.
- Deliverable: report document to the author (per-item table, citations,
  per-family agreement rates, ranked v0.7 proposals as
  current wording → proposed wording → which items flip → predicted effect
  on two-arm agreement). Proposals only; rulings are the author's; adopted
  changes go through the calibration loop before binding.
