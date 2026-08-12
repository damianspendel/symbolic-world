# Execution plan: Step 2 (calibration) and Step 3 (codebase update)

Defined 2026-08-12 by the Fable session for execution by Opus agents, on
Damian's instruction. The arc-close sequence this belongs to is recorded in
BACKLOG.md ("SEQUENCE — this order is the decision"); the findings it
remediates are BACKLOG item 7; the rules it must satisfy are docs/RULES.md
(#10–#18, #23). Judgment calls this plan does not settle go back to the main
session — an executor does not improvise on this plan.

Hard constraints for every agent, no exceptions: branch `mining-away`; never
push, tag, release, or run manage.sh; never touch master, the v1.3.0 tag,
docs/PAPER.md, or web/public/v1.3/; never commit data/, paragraphs.jsonl, the
epub, or the Gemini key (pipeline/work/gemini.key is read at call time,
request header only, never echoed); stage named paths only, never `git add
-A`; NO Cloudflare deploy from either step (Step 3's page changes are UI and
wait for Damian's review).

---

## STEP 2 — family-gate calibration on the rebuilt harness

### 2a. Relocate the harness into tracked code (RULES #23)

Create `pipeline/family_calibration/` (tracked — .gitignore covers only
pipeline/work/). Move/rewrite into it:
- `build_population.py` (from pipeline/work/build_calibration_input.py)
- `plant.py` + `score.py` (from pipeline/work/corrupt_family_assignments.py,
  split or kept as one module)
- `gate.py` (from pipeline/work/gate_family_assignments.py)
Working artifacts (population, gated file, key, chunk outputs) still go to
pipeline/work/ EXCEPT the final calibration record (see 2d).

### 2b. The six PRE-STEP-2 fixes (BACKLOG item 7, verbatim intent)

1. **Provenance binding.** plant() draws or receives a seed, stamps
   `{"calibration_seed": S, "planted_at": ISO}` into the gated-assignments
   file, the key file, AND every gate chunk output (gate.py copies the stamp
   from its input into each chunk file). score() reads all three sources and
   REFUSES (hard exit, no numbers) on any mismatch or any missing stamp.
   plant() deletes pre-existing `family_gate_c*.json` before writing.
2. **Diagnosis scoring.** A planted item counts as CAUGHT only if the gate
   flagged it AND the gate's `should_be` equals the key's `was`. Report
   flagged-but-misdiagnosed separately. PARTIAL verdicts are tallied in their
   own column and are NEVER catches. Specificity unchanged (clean items
   flagged = false positives).
3. **No fabricated fields.** build_population.py emits no `confidence` field;
   plant() eligibility is simply "every population item" (the population is
   already restricted to model-arm agreed assignments); gate.py sends the
   gate no proposer_confidence and no reasons.
4. **Superset rejection.** The shared runner must reject a model response
   whose n-set is not exactly the expected set (currently rejects only
   subsets). Patch pipeline/crossvendor_run.py `run()` — an extra/hallucinated
   n is a hard retry, same as a missing one. This is shared code: change only
   that check, nothing else in the file.
5. **Quota stall fix.** In plant(), an ineligible pick is skipped (not
   re-appended for immediate re-draw); after planting, assert every class met
   its quota (8 K1 / 4 K2 / 4 K3 / 3 K4) and hard-exit with the shortfall
   named if not.
6. **Uniform reasons.** Every entry in the gated file — clean and corrupted —
   carries `reason: ""`.

Also: the K1 ADJACENT map must cover all 25 in-use families (instrumentality→
telos was added 2026-08-12; verify coverage programmatically against
seed.json's live family values and hard-exit if any family lacks a partner).

### 2c. The run

1. Population: 60 edges, drawn seeded from seed.json edges with
   `relation_family.state == "assigned"` and `by` NOT containing "human" or
   "precedent". Record the draw seed.
2. Plant with a fresh seed drawn at run time (never reuse 20260806/90507).
3. Gate: Gemini via the shared runner, definitions document
   docs/FAMILY_DEFINITIONS.md AS IT STANDS (v0.5 + the committed rulings —
   this run is the pre-fold baseline), chunk 15, key never in any prompt.
4. Score. Print the full per-class table and per-item diagnosis.

### 2d. Threshold and record (set 2026-08-12, immovable)

- **PASS** = all 19 planted items caught WITH correct diagnosis, all classes
  at quota. One K1 miss or misdiagnosis = FAIL. Any K2/K3/K4 miss = FAIL.
- **Specificity reported, never gating**; below 85% flag each false positive
  for the main session to inspect.
- Write `pipeline/family_calibration/records/2026-08-12_v05.json` (TRACKED):
  {definitions_version, definitions_git_hash, draw_seed, plant_seed, n,
  quotas, per-class results, per-item key+verdict+diagnosis, sensitivity,
  specificity, PARTIAL tally, gate_model, verdict PASS/FAIL, note that the
  gate model equals one production arm's model (nominal independence,
  RULES.md caveat)}. Commit it with the harness scripts.
- **On FAIL: STOP.** Commit the record and the harness anyway (a failed
  calibration is a result, RULES #12), report which boundary failed, and do
  NOT proceed to Step 3. Sharpening definitions wording is not the executor's
  call.

### 2e. Verification before handing back

`python3 tests/test_graph.py` green; `python3 tools/check_paper_facts.py`
green; `git status` shows only the named new/changed paths staged; a second
`score.py` invocation reproduces the identical record from disk.

---

## STEP 3 — the codebase update (only after Step 2 reports PASS)

### 3a. Commit the family layer's working code (RULES #23)

Create `pipeline/family/` (tracked) holding runnable, documented versions of:
- `build_sweep_input.py` — the per-window unassigned-edge input builder (the
  inline version used for w8–w10 is in the session transcript; reconstruct
  from the family_sweep_input.json shape: n, subject/object + types,
  relation, relation_effective, qualifiers, layer, refs).
- `sweep_gemini.py` — the Gemini arm (a working copy exists at the session
  scratchpad path recorded in BACKLOG item 7; port it, key handling per
  constraints).
- `assemble_sweep.py` — agreement→assigned / disagreement→queue, the exact
  logic used w8–w10 (agreed unclassified→no-family, text-undecided
  preserved, by='opus+gemini-agreed (v0.5)', queue entry shape with both
  arms' votes and reasons).
- `OPUS_ARM_PROMPT.md` — the blind Opus-arm prompt as used (verbatim from the
  w10 launch), so the arm is reproducible.
- Port `classify_gemini_full.py` fix: failed chunks retry on rerun
  (remove the permanent already-failed skip; keep the failures file as log).
Also commit the surviving raw arm outputs for w8–w10 sweeps into
`pipeline/family/receipts/` labeled `preserved-artifact` (they contain only
≤25-word quotes — publishable channel), per the file-what-survived decision.

### 3b. FAMILY_DEFINITIONS v0.6 — mechanical fold ONLY

Transcribe the recorded rulings into the document; invent nothing:
1. Delete/replace the "amplification layer tag overrides the relation
   string" boundary rule with: the layer tag never overrides the content
   family (rulings of 2026-08-10, 3–0, plus one precedent application).
2. Add the sentence-subject worked contrast: CW 9i §572 mandala|is|god-image
   → archetypal-identity vs CW 9ii §60 → correspondence, with the
   distinguishing note recorded on edge 9i§572 in seed.json.
3. Add `exemplified-by` to the homeless strings beside `assimilates`.
4. Record the `underlies`/`based-on` two-rules collision (w9 Opus arm
   report) as a KNOWN AMBIGUITY awaiting a ruling — do not resolve it.
5. Version header → v0.6, dated, with a change log naming the rulings.
Anything beyond these five is out of scope. The v0.6 diff goes in the commit
message summary for Fable-session review after the fact.

### 3c. The relation-string → family map

`web/build-atlas.mjs` (or a small tracked generator it calls) derives from
seed.json: for each family, its member relation strings with edge counts;
plus the homeless strings (no-family) and pending/text-undecided counts.
Emit as data consumed by the families page. No hand-maintained copy of it
anywhere — derived on every build.

### 3d. The public families page

Rewrite the reader-facing content of `web/public/families.html` generation
(renderDoc in build-atlas.mjs) to: what a family IS (a classification OVER an
already-verified relation, never a re-verification), the map from 3c, the
real counts (assigned / pending / no-family / text-undecided), the
adjudication protocol, and worked boundary examples from v0.6. The copy is
BOUND by the anti-overclaim checklist in BACKLOG.md item 3 — all six
prohibitions. The executor being Opus satisfies the checklist's author rule
(a family that did not author FAMILY_DEFINITIONS). Run the build's copy
assertions; add the families page to their scope if not covered.

### 3e. CI teeth (RULES #18)

Extend tools/check_paper_facts.py (same fail-closed, literal-expected-string
style) with:
1. relation_family schema: state in the closed enum, value null iff state
   is not "assigned", assigned values ∈ the v0.6 inventory parsed from
   FAMILY_DEFINITIONS.md.
2. Count coherence: family states sum to edge count; queue file length ==
   pending-adjudication count in seed.json.
3. Corruption tripwire: no `calibration_seed`/plant-marker key on any edge or
   reference in seed.json.
4. Calibration handshake: the version header in FAMILY_DEFINITIONS.md has a
   matching record file in pipeline/family_calibration/records/ whose
   definitions_version equals it. (The v0.5 record from Step 2 covers the
   pre-fold doc; a v0.6 record comes from 3f.)
5. Ledger family tooltip derivation: assert build_ledger_page.py's fam_note
   branches cover every distinct `by` prefix present in seed.json (no
   unknown-by falls through to the arms-agreed wording).

### 3f. Re-calibrate against v0.6 (RULES #16)

Re-run Step 2c–2d against the folded document, fresh seeds, record to
`records/<date>_v06.json`. Same threshold, same stop-on-fail. This record is
the one the handshake check (3e.4) binds v0.6 to. On FAIL: stop, report the
boundary, leave v0.6 committed but the calibration record marked FAIL — the
definitions do not ship to the site until a pass exists (the families-page
copy must then not cite calibration at all, which under the checklist it
does not anyway).

### 3g. Verification before handing back

Full local chain: tests green, check_paper_facts green (including the five
new checks — and demonstrate each new check FAILS on a deliberately broken
input before fixing it back; a check that never failed is not a check),
`npm run build` green, `python3 tools/pages/preflight.py` GREEN, **no
deploy**. Named-path commits per component (harness/scripts, v0.6, map+page,
CI), each with a "Changes in this pass" style summary in the body. Report:
per-item outcomes, the v0.6 diff summary, both calibration records' numbers,
and anything skipped with the reason.
