# Where things stand — 2026-08-04

## Three branches, three jobs

| Branch | What's on it | State |
|---|---|---|
| `master` | Published paper, v1.3.0, 248/669/699 | Frozen. Never touch. |
| `mining-away` | Trilogy mined complete, 288/880/939 | Unpublished, ready for a decision |
| `ontology-qa-tooling` | 3 QA scripts (diagnose/quality/themis) | Built against the *wrong* graph — measures frozen v1.3.0, not mining-away |

Ran the QA scripts against mining-away's real numbers today. Old baseline (v1.3.0):
13 pass / 5 partial / 2 fail. Current (mining-away): **12 pass / 5 partial / 3 fail** —
one extra failure, from tripling the edge count. Same two structural problems, worse:
- **35 symbols collapse into one** if identity relations are ever treated as transitive
- **25 edges are prose, not data** — unreadable by a machine
- relation vocabulary: 468 distinct strings, 409 used once

## Two tracks

- **Track A** — build a generic version of this QA method, prove it on a corpus that
  isn't Jung. Corpus not chosen yet, on purpose — still hunting for the right one.
- **Track B** — fix Jung's own graph using what Track A's instruments found.

## Priorities, in order

1. **Move the QA tooling onto mining-away.** It's currently measuring a graph three
   months out of date. Nothing else is trustworthy until this is fixed. *Small, do first.*
2. **Build the relation-family layer (T1).** This is Track B's actual work — turns 468
   loose strings into ~20 families, fixes the transitivity trap, flags the 25 unreadable
   edges. Gated on Fable capacity returning (Aug 5).
3. **Decide the next mining arc**, once the family layer exists — not before, or you
   remap the same edges twice. Candidates already written up in `MINING_ROADMAP.md`.
   Leaning: CW 9i + 9ii, grounds the psychological vocabulary currently floating on
   alchemical evidence alone.
4. **Track A corpus and framework.** Not urgent — genuinely open. Considerations below.

## Track A — the generic risk framework

**Two different frameworks are in play. Keep them straight.**

| | Paper | Measures | Our layer |
|---|---|---|---|
| **DRAI** | Hiniduma, Byna & Bez, *Data Readiness for AI: A 360-Degree Survey* (arXiv 2404.05779 → ACM Computing Surveys) | is a **dataset** fit to be used? | (a) corpus intake |
| **Zaveri** | Zaveri, Rula, Maurino, Pietrobon, Lehmann & Auer, *Quality assessment for Linked Data: A survey* (Semantic Web Journal) | is a **graph** any good once built? | (b) and (c) |

These are not the same paper and not the same authors — worth stating because they were
conflated once already. They also don't compete: DRAI sits at the front of the pipeline,
Zaveri at the back. Track A needs both.

**Practical note on DRAI:** the handoff flags that its PDF was read twice through a
summarising fetch with contradictory results, and makes reading it directly a blocking
prerequisite. Before hand-porting its dimensions to text, look at **AIDRIN** (AI Data
Readiness Inspector) from the same group — it's an implementation of the DRAI metrics
rather than a taxonomy on paper, so the code may settle faster what the prose didn't.

**On the graph side, the taxonomy already exists, better specified.** Zaveri et al. name
18 quality dimensions in 4 categories: Intrinsic, Contextual, Representational,
Accessibility. Our three layers map onto three of the four almost exactly:

| Our layer | Zaveri category | Zaveri dimensions that match |
|---|---|---|
| (a) input fitness | **Contextual** | timeliness (= staleness), relevancy, trustworthiness |
| (a), partly | **Intrinsic** | conciseness (= near-duplication/redundancy) |
| (b) claim fidelity | **Intrinsic** | accuracy / semantic correctness — already done, frozen |
| (c) structural coherence | **Representational** | interpretability, versatility — exactly what diagnose/quality/themis measure |

Zaveri's fourth category, **Accessibility** (licensing, availability, security), isn't
part of the risk taxonomy at all here — it's already handled separately by
`docs/LEGAL.md`. Worth naming so it isn't accidentally folded back in later.

**What this buys.** A citable academic anchor instead of a half-verified porting
exercise, and a sharper claim: Track A isn't inventing dimensions, it's the first
attempt to run Zaveri's *contextual* and *intrinsic* dimensions and a competency-question
suite together, on the same corpus, with a measured residual reported at each layer.
That "stack" claim from the handoff is real — but check it against papers that cite
Zaveri before asserting nobody's done it; several likely combine two of the three.

**Three design questions Track A has to answer, not later:**

- **One score or three?** Recommend three, kept separate. A blended risk number hides
  which layer actually failed — Zaveri's own literature argues the same, dimensions
  are reported individually, not averaged into "quality."
- **Fixed thresholds or corpus-relative ones?** The one existing result — a readability
  measure that works on Brown and fails on James — already answers this: thresholds
  are corpus-relative, calibrate per corpus, don't hardcode a pass bar.
- **Risk framing or quality framing?** These sound the same but aren't. "Quality
  assessment" (Zaveri's own language) suits a semantic-web audience. "Risk framework"
  (likelihood × impact, residual risk, ISO 31000-shaped) suits a compliance/governance
  audience — which is exactly the shape of a regulatory corpus. The corpus choice and
  the target venue should be picked together, because they imply different framings of
  the same three measurements.

**Where ROT fits — one candidate instrument, not a fourth layer.** ROT (Redundant /
Obsolete / Trivial, ~85% of enterprise content by volume — see the Databerg Report) is
a records-management term for triaging documents *before* they're kept at all. It's not
a new dimension; it's a practical way to operationalize the Contextual layer at intake:
Redundant → near-duplication, Obsolete → staleness/supersession, Trivial → the one gap
in the current criteria — content with no extractable value, closer to what archival
appraisal calls "no enduring value" than anything Jungian. Fits a standards/regulatory
corpus cleanly, doesn't fit Jung at all (single author, no disposition question).

**Corpus-selection criteria, as they stand** (from the earlier handoff, unchanged):
≥3 independent sources · multi-decade span with dated documents · natural
near-duplication · a stable citable unit (paragraph/clause numbering) · recurring
entity-relation structure worth a schema · redistributable or quotable under the same
≤25-word posture as the Jung corpus. A standards/regulatory body of documents satisfies
all six; that's a shape, not a pick — no corpus is committed to yet.

## Don't lose sight of

- v1.3.0 stays byte-identical, forever. Nothing above touches it.
- Nothing gets tagged or pushed today. This is a status file, not an action.
