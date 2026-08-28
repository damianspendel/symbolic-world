# Study C — normalization validation

Pre-registered 2026-08-28, BEFORE any run (RULES #11). Damian approved the
study and its weekend schedule 2026-08-28.

## Question (RQ3)

260 relations carry a `relation_normalized` layer produced in one pass on
2026-08-05 (Opus proposed, Fable gated entailment, Gemini checked all 260
records). No instrument has ever measured the layer itself. Two parts:

**C1 — second arm.** A Gemini model independently re-normalizes the same
260 verbatim relations under the same spec (verb of at most 4 hyphen
tokens; carrier/scope/condition/modality qualifiers; the 2026-08-18
amended cap), blind to the stored normalization. Compare: (a) verb
equivalence, judged mechanically first (exact/inflection match) and the
remainder judged by a Fable-family model as same-relation/different-
relation with a stated reason; (b) qualifier retention: does each arm
carry the hedge/scope the verbatim string held.

**C2 — seeded normalization corruptions.** 40 stored normalizations
corrupted in copies (10 modality-qualifier dropped, 10 scope dropped, 10
verb direction reversed, 10 verb strengthened past the verbatim claim) +
40 clean, shuffled; the Fable entailment gate re-judges each against the
frozen verbatim relation and quote.

## Pre-set reporting rules

- C1 reports: mechanical verb agreement, judged same-relation rate,
  qualifier-retention rate per qualifier kind, and every disagreement
  listed verbatim. No arm is ground truth; disagreement is the finding.
- C2 reports: catch rate per corruption class (caught = flagged AND the
  reason names the corrupted element, RULES #14), specificity on clean.
- No pass bar. One run, no redraws, chunk-resumable, never restarted.
- Gemini quota or 503 exhaustion: HOLD and report verbatim, never push
  through (CLAUDE.md standing rule).

## Mechanics

Harness in `tools/studies/study_c_*.py` (committed before the first API
call). Working files in `pipeline/work/study_c/` (gitignored). Receipts in
`docs/experiments/study_c/`, committed. Stands down when
`docs/experiments/study_c/RESULT.json` exists.
