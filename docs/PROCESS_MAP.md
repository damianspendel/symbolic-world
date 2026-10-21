# The project's processes — a map with the gaps marked

Written 2026-10-21 at Damian's request, after the mining/build track split
(2026-10-13) and the Ko-fi launch. Six core processes, their subprocesses,
who owns each, and where the gaps are. The technical release chain is sound;
the gaps are cadence and ownership questions.

## 1. Mine — produce verified claims

Owner: the mining track (scheduled session). Cadence: nightly chain.

- 1.1 Arc and window selection: Damian rules the arc; state.json carries the
  window ladder and the stand-down marker.
- 1.2 Propose (Opus family) → 1.3 pre-check (mechanical: quote cap, form
  rule) → 1.4 gate (Fable family, hostile) → 1.5 cross-vendor audit (Gemini)
  → 1.6 merge, data-paths commit only.
- Controls that have fired and held: miner blinding; one pass per window
  ever; capacity warnings forwarded verbatim; a hold when the wrong session
  type reached the gate (b-cw11-8 held rather than gated by a non-Fable
  session, then gated properly and merged).

## 2. Classify — the family layer

Owner: mining produces arm votes; Damian rules.

- 2.1 Two blind arms → 2.2 agreement assigns, disagreement queues → 2.3
  human sittings, rulings signed and dated → 2.4 ruleset versions with a
  calibration PASS record each → 2.5 inverse/symmetric declarations
  transcribed from the document.
- State: ruleset v0.7.2 binding. **GAP 2: sittings are dormant while the
  queue grows with every window (~405 and rising). No cadence, no cap.**

## 3. Publish — the site

Owner: the build track (this session). Trigger: currently manual.

- 3.1 Build: build-atlas → ledger generator → vite. Every generated page —
  concept pages, quotes, the ledger, the indexes — recomputes from seed.json
  on every build; nothing is hand-updated.
- 3.2 Gates: copy contract; the test suite; preflight (count sync with
  seed.json, exact file manifest, frozen v1.3 checksum, size budget, poster
  facts, paper facts, quote canaries).
- 3.3 Poster re-render per deploy (ruling 2026-10-20). 3.4 Local review for
  anything UI or copy. 3.5 Deploy on Damian's explicit word. 3.6 verify.py
  against the live site. 3.7 GSC sitemap resubmit when the page set changes.
- **GAP 1 — the glaring one: no refresh trigger.** Mining merges nightly;
  the site updates only when this track builds and deploys. Quotes and
  concept pages are therefore correct but stale between deploys (the lag has
  run from hours to days). The old standing data-redeploy authorization
  predates the track split and the per-deploy poster render; nothing fires
  it now. Needs a ruling: scheduled data refresh, or an accepted manual
  cadence.

## 4. Govern — decisions and records

Owner: Damian; sessions record.

- 4.1 Rulings land in RULES.md / CLAUDE.md / FAMILY_DEFINITIONS with dates.
- 4.2 Release policy: deploy-only until the arcs finish; a versioned release
  is a ceremony (filter-repo public push, tag, Zenodo) and is one-shot.
- 4.3 Frozen artifacts stay frozen (v1.3 snapshot, the published paper).
- 4.4 Publication is a human decision; deploys need the explicit word.
- Parked by name: the arXiv v2 replacement (Damian); the next versioned
  release's preconditions, to be listed when the arcs near the end.

## 5. Communicate — copy, outreach, measurement

- 5.1 Site copy: Damian rewrites; carried verbatim with counts re-bound to
  tokens and typos listed; tests pin load-bearing strings. Working.
- 5.2 Outreach: the SEO/outreach chat owns campaigns and the GSC
  checkpoints — the +4-week decision gate is 2026-11-05 (pre-set bar: 50
  impressions or SEO build work stops). Build track has no action there.
- 5.3 Measurement: daily stats agent, mobile proxy, the Essex tripwire.

## 6. Fund — Ko-fi (new, 2026-10-21)

- 6.1 The Ko-fi page (copy in docs/KOFI_COPY.md) → 6.2 /support with the
  embedded panel, one knob (SUPPORT_URL) → 6.3 tips framed as funding the
  next window.
- Open, optional: no loop yet from tips received to windows funded (a
  transparency line, manual, if wanted later).

## The gap list, ranked

1. **Site refresh cadence** — RULED (Damian, 2026-10-21): manual,
   weekly-ish. The build track deploys on his word, aiming for roughly a
   weekly rhythm; the site may lag the graph by up to a week and that is
   accepted. No scheduled deploy.
2. **Adjudication sittings** — RULED (Damian, 2026-10-21): batch at arc
   end. The queue grows until the CW 11 arc completes, then concentrated
   sittings rule it with the whole arc in view; pending stays labelled as
   such on the site meanwhile.
3. **Vocabulary strain watch** (process 2/1): CW 11/5/16 are new registers;
   no-family and homeless-string counts exist on /families but nobody
   watches a threshold. Cheap fix: the mining report states them per merge;
   review at arc end.
4. **Open build-track debts** (process 3): I4 question-cards parked with a
   saved patch; the I5 query-builder design doc owed.
5. **Single-human bottleneck** (process 4): rulings, sittings and deploy
   words all route through Damian. By design; listed so the design is a
   choice, not an accident.
