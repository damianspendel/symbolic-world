# The Symbolic World — Standing Review

**Date:** 2026-07-30 · **State:** v1.3 + batch b-cw12-5 merged (first fully pre-merge cross-vendor-checked batch after the E10 gold set)
**Live:** [symbolicworld.observer](https://symbolicworld.observer) · Paper: `docs/PAPER.md` · Ledger: `pipeline/state.json`

## 0. Snapshot

| | |
|---|---|
| Graph | **400 nodes · 1521 edges · 1790 references**, 1206 distinct CW paragraphs, 9 volumes |
| Verification | **1083/1083 (100%)** gate-verified with model+date provenance; 889 (82%) also cross-vendor checked (412 of CW 14's 413, everything since the pre-merge mandate) |
| Claim provenance | 1339 jung-asserts · 339 jung-reports-parallel · 112 jung-quotes-source (116 named-source strings) · 182 hedged |
| Coverage | Alchemical trilogy end-to-end: CW 14 (413 refs), CW 12 (223 refs), CW 13 (176 refs). CW 9ii (Aion) in progress (165 refs, §1-138 mined); five further volumes sampled |
| Human validation | **E10 gold set complete**: support 44/50 · voice agreement 40/50 (single-annotator, anchored — see caveats) |
| Replication | James's *Varieties* pilot: 38 edges, full public package (`james/`) |
| Cost to date | ≈ $85–115 total model spend; ≈ **$0.09–0.14 per fully verified citation** |

## 1. Methodology

Every batch follows one pipeline, recorded in a committed transaction ledger
(`pipeline/state.json`; statuses `input-built → mined → pre-checked → gated → merged`,
one commit per transition — git history *is* the audit log):

1. **Mine** (Claude Opus 4.8): propose 12–22 edges from a contiguous paragraph
   window, verbatim quotes ≤25 words, node-vocabulary reuse, claim-typing rules.
2. **Mechanical pre-check** (deterministic): every quote must be an in-order,
   letter-normalized, near-contiguous token run of its cited paragraph (bounded
   gaps; 30-token elision bound across ellipses); node existence; no duplicate
   triples. Excludes fabricated quotes within the stated bounds.
3. **Structure gate** (Claude Fable 5 — different model family by design):
   full-paragraph review per edge → SUPPORTED / PARTIAL (with correction) / WRONG.
4. **Voice gate** (Fable 5, narrow brief): claim-type and hedge fidelity only.
5. **Cross-vendor check** (Gemini 3.1 Pro — different vendor): re-judges every new
   batch pre-merge; also audits the published graph at every dataset release.
6. **Adjudicated merge → integrity tests → deploy → commit.** Tests re-validate
   every quote, anchor, claim type, and provenance field, and run **7 corruption
   canaries that must be caught** on every build; builds fail closed.

**Claim-type provenance** is first-class: every citation is typed by *whose claim
it is* (Jung's own voice / reported doctrine / quoted named source) under a
published annotation protocol (`docs/ANNOTATION_PROTOCOL.md`).

## 2. Architecture

```
epub ──extract.py──▶ data/paragraphs.jsonl (local only, never published)
                          │
     miner (Opus) ─▶ candidates ─▶ pre-check ─▶ structure gate ─▶ voice gate
                          ▲          (pipeline/ ledger, committed)      │
                          └────── corrections loop ◀── cross-vendor check
                                                                        │
seed.json ──build-atlas.mjs──▶ atlas.json ──vite──▶ single-file Atlas ◀─┘
   │                                                    │
tests/test_graph.py + tools/check_paper_facts.py   launchd service :8788
(validators, canaries, paper-claims CI)            ─▶ Cloudflare tunnel
                                                   ─▶ symbolicworld.observer
```

- **Corpus:** paragraph records extracted mechanically from epub markup (§ numbers
  never inferred); Bollingen page concordance carried per §; copyrighted text stays
  local — only ≤25-word verified quotes ship.
- **Atlas UI:** six typed regions; search; click-to-walk; **evidence view** (every
  citation expands to its verification record); RAG status dots
  (human-validated / AI-verified / disputed); gated reader **dispute** and
  **confirm** channels through the public issue tracker, with a published log.
- **CI:** every push re-runs the graph validators, the James checks, and a facts
  checker that recomputes every countable claim in the paper from the artifacts.

## 3. Findings (all experiments; details in `docs/PAPER.md` Appendix A)

| Experiment | n | Result |
|---|---|---|
| **E0 — Retro-verification** (all pre-gate edges) | 238 | 178 confirmed · 54 corrected · 6 deleted → **25.2% flaw rate in ungated extraction** |
| **E1/E1b — Gate calibration** (seeded corruption, blind) | 40 → 200 | **Sens 86% (CI 78–91) / spec 93% (CI 86–97)**; reversal 23/25 · swap 24/25 · overreach 21/25 · voice-flip 18/25. Coarse seeded errors only; near-referent drift unseeded |
| **E2 — Adversarial audit** (break-each-edge) | 30 | **0 content/direction/fabrication errors**; 4 modality refinements, applied |
| **E3 — Modality sweep** (full graph at sweep time) | 634 | **65 flagged (10.3%)**, 75 corrections applied; age gradient 18.9% → 5.6% |
| **E4 — Stability probe** (blind re-mine) | 2×20 | **37.5% strict pair overlap**; core theses stable; benign-non-overlap reading pending human coding |
| **E5/E5b — Voice specialist** (paired calibration) | 25+25 | Specialist 20/25 vs generalist 18/25 — direction consistent across five measurements, **not statistically established** |
| **E6 — Cross-vendor audit** (Gemini, full rubric) | 100 | **89/11/0**; 4 upheld and corrected; both vendors miss the *same* voice items |
| **E7 — Reduced-rubric audit** (Gemini, full CW 14) | 407 | **356/47/4**; upheld residual **1.0–2.2%** by adjudication stance; unanchored cross-review endorses all corrections, rejects 6/10 convention rulings |
| **E8 — James replication** (public domain, ships complete) | 38 edges | Gate 90% sens / 100% spec (n=60); voice again the weak axis (7/10) |
| **E9 — Teaching test** (held-out window, blind) | 20/arm | Taught 15% vs untaught 35% flagged — directionally as predicted, **statistically unresolved** (p ≈ 0.27); shared-instrument confound remains |
| **E10 — Human gold set** (author, stratified 50) | 50 | **Support 44/50 · voice 40/50** (asserts 24/26 · quotes 8/9 · reports 8/15); 8/10 disagreements over-credit Jung's voice; 6 expose a source-specificity failure no model audit surfaced. Single annotator, anchored review — favorable estimate |

**Findings worth publishing:**

1. **Unverified LLM extraction ran 25.2% flawed on this corpus** — verification is
   where most of the value is created.
2. **Error classes are sharply asymmetric.** Coarse structural errors are caught at
   92–96% in calibration; the surviving axis is *attribution modality* — whose
   claim is it, how firmly said.
3. **Voice is the genuinely hard problem, for machines and probably for people.**
   Sympathetic reportage defeats every model configuration across two vendors, and
   the human gold set adds a second hard boundary the models never flagged:
   reports vs quotes (named sources under-credited).
4. **Fabrication is the easiest problem** — excluded mechanically, within stated
   and canary-guarded bounds.
5. **Anchoring inflates agreement** — measured in the cross-reviews, then found in
   our own gold-set tool (disclosed; the tool now defaults to unanchored).

## 4. Mitigations in force → remaining risks

| Risk | Mitigation in force | Residual / next |
|---|---|---|
| Fabricated citations | Mechanical verbatim check + 7 canaries + CI | Excluded within stated bounds |
| Reversed/wrong-referent edges | Calibrated gate + cross-vendor audits | None observed post-gate; near-referent drift calibration pending |
| Voice/modality drift | Taxonomy + specialist gate + full sweep + **human gold set (E10)** | The dominant residual: reports class 8/15; second annotator (unanchored) next |
| Validator regression | 7 corruption canaries (must-catch) in CI | — |
| Shared-substrate blind spots | Family separation at gate; **vendor separation at pre-merge check + release audits (E6/E7)** | Mandatory gate still single-vendor |
| Selection subjectivity | Stability probe (37.5% strict overlap); union-mining | Tier-2 claims sampled, not complete |
| Reader trust | Evidence view; published error rates; **live gated dispute/confirm channels + public log** | 0 reader confirmations yet; community pilot queued |
| Adjudication discretion | Rulings published; unanchored cross-review | Convention rulings don't survive independent review → human adjudication |
| Translation dependence | Documented (assumption #1) | German GW cross-check — deferred |

## 5. Immediate queue

1. Second annotator for the gold set (unanchored tool ready: `tools/review_server.py`) + independent human review of the three open E10 items (gold_id 12, 14, 19).
2. E1c re-calibration with realistic near-referent drift corruptions.
3. E9 cross-vendor re-grade (removes the shared-instrument confound).
4. Community verification pilot per `docs/ASSUMPTIONS.md` §E.
5. arXiv submission (endorser engaged; paper v1.3 under final author review).
