# The Opus arm of the per-window family sweep — prompt, verbatim

RULES #23. This is the prompt as launched for window 10 of the CW 9i arc
(2026-08-12), recorded so the arm is reproducible rather than remembered. The
Gemini arm runs `pipeline/family/sweep_gemini.py` against the same input; neither
arm sees the other's file. Launch this one in its own session — a session that
has already read the sweep outputs is not blind.

Everything between the markers is the prompt. Nothing in it names a tracked
metric, an agreement rate, or a target distribution (RULES #5).

---BEGIN PROMPT---
You are one blind arm of a two-arm relation-family classification for a verified knowledge graph of C.G. Jung's Collected Works.

Working directory: /Users/damianspendel/Documents/github/JungKG (cd there; confirm branch mining-away).

Read exactly two files:
1. docs/FAMILY_DEFINITIONS.md — the complete, binding family definitions document.
2. pipeline/work/family_sweep_input.json — the verified edges awaiting family assignment.

HARD RULE — you are blind: do NOT read pipeline/work/family_sweep_gemini.json or any other family_* file; do not read seed.json; do not read any other document. Your assignment must come from the definitions document and the sweep input alone.

For EACH edge assign exactly one family from the document's inventory, or "unclassified(no-family)" if no family covers the relation, or "text-undecided" if the quoted text itself hedges between families. Judge from relation_effective, the node types, and the quotes; apply the boundary rules exactly as written. Confidence "sure" or "unsure"; one-line reason each, naming the deciding rule or seed shape where applicable.

Write pipeline/work/family_sweep_opus.jsonl — one JSON object per line, OVERWRITING the existing file:
{"n": <n>, "family": "<family>", "confidence": "sure"|"unsure", "reason": "<one line>"}

One row per input edge, same n values as the input. Write only that file. Report: counts per family, how many unsure, any edge where you seriously considered a second family (name both).
---END PROMPT---
