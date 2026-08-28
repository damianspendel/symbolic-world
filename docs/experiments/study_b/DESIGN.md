# Study B — realistic corruption calibration of the reference gate

Pre-registered 2026-08-28, BEFORE any run (RULES #11: thresholds and
reporting rules set now, and they do not move after results are seen).
Damian approved the study and its weekend schedule 2026-08-28.

## Question (RQ1's open half)

E1b measured the gate at 86% sensitivity on COARSE seeded corruptions
(random object swaps, literal `is-identical-to`). Production audits found
SUBTLE errors instead: near-referent drift, dropped hedges, analogies
hardened into identities. What is the gate's catch rate on those?

## Population and corruption classes

Drawn seed-reproducibly (seed recorded in the run receipt) from verified
references in seed.json at the commit the run names. n=200 mirroring E1b:

- 25 × near-referent drift: the object is replaced by a node at graph
  distance 1 from the true object or subject (never random), same type
  where possible. The class production audits actually caught (Adam for
  Anthropos, filius unius diei for filius regius).
- 25 × hedge deletion: a reference whose paragraph hedges (E3's hedge
  markers) presented as an unqualified high-confidence claim.
- 25 × analogy-to-identity: a comparison relation (is-like, parallels,
  corresponds-to, is-analogous-to family strings) presented as
  is-identical-with / is.
- 25 × subject expansion: the subject widened to a superordinate node one
  step up (the observed "subject overreach" class).
- 100 × clean controls, untouched.

Corruptions live in copies; seed.json is never written.

## Instrument

The production gate: a Fable-family model, blind, judging each claim
against its full paragraph with the production gate prompt shape
(TRUE/CORRECTED/FALSE + reason). The task session runs the gate through a
Fable-family subagent; if Fable capacity is unavailable the firing HOLDS
and reports, it never substitutes (RULES #2).

## Pre-set reporting rules

- A corruption counts as CAUGHT only if the verdict is CORRECTED or FALSE
  AND the reason names the corrupted component (RULES #14: detection
  requires diagnosis).
- Report per class: caught/25 with 95% Wilson intervals; pooled
  sensitivity; specificity on the 100 controls; every miss listed.
- The E1b comparison is stated as measured-vs-measured, never blended.
- This study GATES nothing. No pass bar exists; the number is the result.
- One run. No redraws. If the run is interrupted, it resumes from its
  chunk state; it is never restarted fresh after results are partially seen.

## Mechanics

Harness in `tools/studies/study_b_*.py` (committed before the first gate
call). Working files in `pipeline/work/study_b/` (gitignored). Receipts —
draw seed, plant manifest with per-item provenance, verdicts, scores — in
`docs/experiments/study_b/`, committed. Chunked ~50 judgments per firing;
the scheduled task stands down when `docs/experiments/study_b/RESULT.json`
exists.
