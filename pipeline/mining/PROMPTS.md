# The mining chain's prompts — documented verbatim (RULES #23)

Committed 2026-08-13, answering the documentation gap: the family layer's
prompts were already in the repository (pipeline/family/OPUS_ARM_PROMPT.md,
the prompt constants in pipeline/family/sweep_gemini.py and
pipeline/family_calibration/gate.py); the mining chain's were not — they
lived in per-window agent invocations and the scheduled task's SKILL.md.
This file is the canonical record. Per-window launches adapt ONLY the batch
id, window bounds, material description, and window-specific pressure
points; everything else is fixed. A change to the fixed text is a pipeline
change and gets its own commit.

## 1. The miner (Opus family, blinded)

Structure per window: role statement (proposer only, never verifies);
orient-and-stop branch check; input file; exact output shape with the
closed claim_type set and required source field; the hard rules block —
FORM RULE (verb phrase, ≤3 hyphen tokens, ≤1 trailing preposition, never a
clause), RELATION STRENGTH (the verb must not exceed the paragraph; for CW 8
specifically: Jung building a model is not Jung asserting a mechanism),
verbatim quotes ≤25 letter-tokens on the test tokenizer, aggressive dedup
with existing_edge flags, no nominalized pseudo-entities, natural density
35-50 candidates / 50-70 refs, read only the input file. THE MINER IS
BLINDED: no metrics, no trend files, no transfer question, ever (RULES #5).
For CW 11 the hard rules block carries one addition, the EXEGESIS CLAUSE
(added 2026-10-13 per the Gemini review in docs/PROPOSAL_NEXT_ARC.md;
authorial-endorsement hallucination is the reviewer's reported dominant
failure mode in religious text): Jung expounding a dogma, scripture,
liturgy, rite, tradition or named author is REPORTING, not asserting —
extended, sympathetic, undistanced exposition included; jung-asserts is
reserved for Jung's own interpretive voice; each reference takes the
claim_type of the sentence its quote rests on; in doubt, reports. The
clause lives verbatim in pipeline/mining/build_input_cw11.py's note, so
every CW 11 input file carries it. It is a form constraint: it names no
tracked metric, so the blinding holds.
The CW 8 window-1 instance is preserved verbatim in the scheduled task file
and the session transcript of 2026-08-13.

## 2. The gate (Fable family, never substituted — RULES #2)

Structure per window: hostile-by-default role statement; the two inputs
(prechecked file + full paragraph texts, judged against the FULL paragraph);
per-reference verdict TRUE / CORRECTED (with the correction fields) / FALSE
with one-line reasons; window-specific pressure points named (attribution
risks, new-node near-miss fields, repeat-offender edges with their history);
output file only, no docs, no metrics, no paragraph text in the report,
capacity warnings verbatim.

## 3. The cross-vendor auditor (Gemini, pre-merge)

The full prompt, verbatim as sent (from the shared xv script family):

```
You are the independent cross-vendor auditor for a grounded knowledge graph of C.G. Jung's Collected Works. A separate model has already proposed and gated these claims; your job is an independent check, not a rubber stamp. Catch anything wrong, however small.

Below are references. Each has: n, subject/subject_label, relation, object/object_label, claim_type, confidence, paragraph (CW paragraph number), quote, paragraph_text (the FULL verbatim source paragraph). Where the gate corrected the original proposal, the fields already reflect the corrected (post-gate) claim — audit that claim, not the original.

For each reference, judge:
1. Does the quote appear verbatim in paragraph_text?
2. Does paragraph_text actually support subject -relation-> object (read the WHOLE paragraph, not just the quoted fragment)?
3. Is claim_type honest: "jung-asserts" only if Jung states it in his own interpretive voice; "jung-reports-parallel" if the paragraph presents it as another tradition's or author's doctrine that Jung reports; "jung-quotes-source" if it rests on a named quoted source?
4. Is subject/object the right referent — no conflation, no identity overreach (e.g. "is"/"identical-to" where the text only supports analogy or parallel)?

VERDICT per reference: "PASS" if all four hold, "FINDING" if anything is off (state which one and why in one line).

Respond with ONLY a JSON array covering every n: [{"n": <int>, "verdict": "PASS|FINDING", "reason": null or "<one line>"}]. reason is null for PASS, required for FINDING.
```

## 4. Verdict application (the merge)

Not a prompt but the fixed adjudication rules the merge scripts encode:
gate FALSE drops; xv FINDING substantive -> drop (auditor is tiebreaker);
claim-type/confidence-only -> correction applied (b-cw9ii-7 precedent);
finding vs a recorded convention -> convention wins, audit_note stamped
(b-cw9i-8 precedent, analysand-source).
