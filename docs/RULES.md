# The rules — a register

Every operating rule the project runs on, in one place, each with its reason.
Rules were previously scattered across CLAUDE.md, the runbooks, batch prompts
and decision records; the 2026-08-12 code inspection showed what scattering
costs. A rule that is not written here is not a rule. Last updated 2026-10-23.

Marked **[STANDING]** if in force today, **[ADOPTED 2026-08-12]** if added in
response to the inspection and binding from now on.

## Verification chain

1. **[STANDING] The model that proposes a claim never signs it off.** Proposer
   and gate are different model families; the auditor is a different vendor;
   the roles never swap. This is the claim the paper makes.
2. **[STANDING] The Fable gate is never substituted.** If capacity runs out,
   the batch holds at its reached status, recorded honestly, and waits.
3. **[STANDING] Quotes are mechanical or nothing.** Verbatim, ≤25 letter-tokens
   (the test harness's tokenizer is the only tokenizer), letter-normalized
   match against the corpus, seven corruption canaries must be caught on every
   run, builds fail closed.
4. **[STANDING] One mining pass per window, ever.** Covered ground is never
   re-mined. Overriding this is a human decision, named per window.
5. **[STANDING] The miner is blinded.** No batch prompt names tracked metrics,
   trend files, or the transfer question. Form constraints (quote cap, relation
   form rule) are allowed; targets are not.
6. **[STANDING] On support and referent facts, the cross-vendor auditor wins.**
   Claim-type/confidence-only findings become corrections, not drops
   (b-cw9ii-7 precedent). Findings that contradict a recorded project
   convention are overruled by the convention, visibly, with an audit_note on
   the reference (b-cw9i-8 precedent) — conventions decide vocabulary,
   auditors decide facts.
7. **[STANDING] Conventions are written, dated, and cross-batch.** Current:
   analysand material is jung-quotes-source with the analysand named;
   sympathetic-reportage splits default to REPORTS; vocabulary disputes get a
   vocabulary_note, never a new node; nominalized pseudo-entities forbidden.

## Family layer

8. **[STANDING] Two blind arms, symmetric.** Neither arm sees the other's
   answers; agreement assigns; no model ever breaks a tie; disagreement queues
   for human review. Human rulings land signed and dated.
9. **[STANDING] Precedent applies only where the reasoning matches.** A ruling
   retires the rule it actually ruled on; queue items whose votes rest on
   other grounds stay queued (measured 2026-08-10: a precedent expected to
   clear nine items cleared one).
10. **[ADOPTED 2026-08-12] A family label means what its record says.** UI and
    copy describing an assignment derive from the edge's own provenance
    (arms-agreed / Human review / recorded precedent), never from one blanket
    sentence. "Verified" is reserved for the quote-and-paragraph layer;
    families are *assigned*.

## Instruments and numbers

11. **[STANDING] Thresholds are set before results are seen.** Once a sample
    or calibration is drawn, its pass bar does not move (normalization step-0
    precedent; family calibration threshold 2026-08-12).
12. **[ADOPTED 2026-08-12] A published number requires committed code and
    committed receipts.** If a figure appears on the site or in a doc, the
    script that produced it and the inputs needed to re-derive it are in the
    repository (corpus text excepted — hashes stand in). No number from a
    scratchpad. The 19/19 and 20/20 family-calibration figures are WITHDRAWN
    under this rule until re-measured by the audited harness.
13. **[ADOPTED 2026-08-12] Calibration runs are provenance-bound.** The plant
    seed is stamped into every artifact of the run; the scorer refuses
    artifacts whose stamps disagree; stale chunk files are deleted on replant.
14. **[ADOPTED 2026-08-12] Detection requires diagnosis.** A gate catches a
    planted error only if it names the planted item AND the correct family.
    Soft verdicts (PARTIAL) are scored separately, never as catches.
15. **[ADOPTED 2026-08-12] No fabricated fields.** An instrument's input
    carries only values that exist in the data. A field the population does
    not have (e.g. proposer confidence) is omitted, not invented.
16. **[ADOPTED 2026-08-12] Instrument or ruleset change voids its numbers.**
    A new FAMILY_DEFINITIONS version, or a change to a harness, means the
    calibration re-runs before its figures are cited anywhere. Numbers bind to
    the version they measured, and say so where they appear.

## CI — what the build must refuse

17. **[STANDING] Counts are enforced, not remembered.** seed.json is the one
    source; atlas data, landing copy, and pinned doc counts must match it or
    the build fails, with the literal expected string printed.
18. **[ADOPTED 2026-08-12] CI numbers validation must be sound end-to-end.**
    To adopt at the step-3 codebase update: (a) no planted-corruption marker
    may survive into seed.json; (b) a FAMILY_DEFINITIONS version with no
    matching committed calibration record fails; (c) copy assertions cover
    every page that states a number, binding count-like literals to computed
    tokens; (d) the v1.3 frozen snapshot's checksum is asserted on every
    build (already standing in preflight).

## Repository and releases

19. **[STANDING] Frozen means frozen.** master, the v1.3.0 tag, docs/PAPER.md,
    the /v1.3/ snapshot (checksum-pinned) are never modified. Releases are
    one-shot; a released tag is never re-cut.
    **[AMENDED 2026-08-16 by Damian]** The freeze on `docs/PAPER.md` and
    `docs/PAPER.pdf` is lifted for the v2.0 revision, in the release chat
    only. The lift covers rewriting the paper and moving its baseline in a
    deliberate commit of its own. It covers nothing else: master, the v1.3.0
    tag, the /v1.3/ snapshot and the frozen ledger snapshot stay absolutely
    frozen, and the arXiv v1 submission is not touched. The lift closes when
    v2.0.0 is tagged, at which point the revised paper is frozen in turn.
20. **[STANDING] The corpus never leaves the machine.** data/, paragraphs.jsonl,
    the epub are local-only; no quoted corpus text in any outbound message;
    published quotes only through the verified ≤25-word channel.
21. **[STANDING] Named paths only.** No blanket git add; two sessions share
    this tree.
22. **[STANDING] Publication is a human decision.** Site data redeploys run
    under a recorded standing authorization with hard guardrails; pushes,
    tags, releases, and anything carrying UI/copy changes need explicit
    human review (the 2026-08-12 copy fix was explicitly instructed).
23. **[ADOPTED 2026-08-12] Working scripts live in the repository.** A
    scratchpad is for scratch. Anything that produced a merged artifact or a
    published number is committed the day it runs (corpus-reading scripts
    included — they contain no corpus text).
24. **[ADOPTED 2026-10-23] Notes quote Jung within the same 25-word bound.**
    Provenance and qualifier text in seed.json (correction_note,
    audit_note, note, vocabulary_note, and the normalization layer's
    carrier, scope, condition and modality) may quote the corpus, but no
    unbroken run of corpus words in one field exceeds 25 letter tokens,
    counted with tests/test_graph.py's tokenizer. Elisions are written
    "...", as in quote fields. Reason: seed.json publishes every field,
    and the 2026-10-23 pre-push audit found seven notes over the bound
    (trimmed in 619d854). Open, for Damian: whether the bound counts the
    total of quoted words in a field, as quote fields do, rather than the
    longest unbroken run. Under the total reading 21 notes fail today.
    Not yet enforced by the tests; proposed.
