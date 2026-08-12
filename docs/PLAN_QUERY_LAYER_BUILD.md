# Query layer v1 — overnight build plan

Drafted by the Fable-family validation session, 2026-08-12 ~21:00, on
Damian's instruction. Executor: an Opus-family agent, overnight
2026-08-12/13. Reviewer of the result: Damian (morning), with the
Fable session's pre-check. Merge is Damian's decision; nothing here
lands on `mining-away` before that.

Backlog anchor: the v2.0 milestone, item 2 (BACKLOG.md, 2026-08-12
section). This build is its first slice: the read-only query instrument.

## Why a worktree, stated once

The mining chat owns the main working tree overnight (CW 8 windows, the
v0.7.1 close-out was mid-flight uncommitted at planning time). The build
therefore runs in an ISOLATED git worktree on its own branch. Hard rules:

- Branch `query-layer-dev`, created from the COMMITTED head of
  `mining-away` at kickoff time. Record that base hash in the build report.
- Worktree path: a sibling directory, never inside this repo.
- The executor never writes, stages, or commits ANYTHING in the main
  working tree, and never touches: `seed.json`, `pipeline/state.json`,
  `web/build-atlas.mjs`, `CLAUDE.md`, `docs/FAMILY_DEFINITIONS.md`,
  ledgers, anything under `web/public/`. All new code lives in new files.
- No deploys, no pushes, no tags, no `manage.sh`. Nothing leaves the
  machine. The corpus is not needed and must not be read.

## Deliverables, each its own commit on the branch

**D1 — `pipeline/family/relation_declarations.json`.** The inverse and
symmetry declarations as data, transcribed from FAMILY_DEFINITIONS
(current version at kickoff; record which). ACTIVE entries only for pairs
the document itself declares (symbolizes/symbolized-by,
produces/produced-by, produces/originates-in inverse-direction generation,
manifests-as/is-aspect-of with is-manifestation-of, `synonym-of` as
symmetric). Every entry carries a `source` field quoting the doc line it
transcribes. Pairs the ontology-QA scan observed but the doc never ruled
on (precedes/followed-by, mother-of/child-of, father-of/child-of,
is-goal-of/aims-at, exemplified-by/exemplifies, contains/belongs-to) go in
a separate `candidates_awaiting_ruling` list, inert, so adopting one is a
visible human decision, not a build side effect.

**D2 — `tools/query/kg_query.py`.** Read-only CLI over `seed.json`:
- filters: `--family`, `--state`, `--provenance` (assigned-by),
  `--claim-type`, `--volume`, `--subject`, `--object`, `--relation`,
  `--string` (verbatim), `--effective` (normalized-else-verbatim);
- `--closure`: expand matches over ACTIVE declarations at read time; every
  derived row is labeled `derived:inverse-of(...)` or `derived:symmetric` —
  the graph itself is never rewritten and derived rows never masquerade as
  edges;
- `--walk identity --depth N`: depth-bounded traversal over
  archetypal-identity edges, each hop printed with its edge and citation;
  the output header states that no transitive identity is asserted (the
  uroboros rule);
- output: table (default), `--json`, `--count`; a footer line stating the
  seed.json edge count and the graph state it ran against.
- family filtering derives string→family membership from seed.json's own
  `relation_family` records, never from a hardcoded map.

**D3 — `tests/test_query.py`.** Invariant tests, NOT absolute counts —
seed.json will change overnight as CW 8 merges, so any pinned number is a
test that rots by morning. Assert: a family query equals the union of its
member edges found independently; closure output is a superset of raw
output and every derived row maps back to a real edge; every walk hop is a
real edge; declarations validate (every string exists in the live graph or
is marked `dormant`, no pair is both inverse and symmetric, no duplicates);
the CLI exits 0 with sane output on the current graph. Tests must pass with
`python3 -m pytest tests/test_query.py` from the worktree root.

**D4 — `docs/QUERY.md`.** Usage, semantics, and limits. Must state plainly:
what closure does and does not assert; that families are ASSIGNED not
verified (the standing vocabulary discipline binds this doc too); that
walks are exploration, not inference. Prose follows the no-AI-tell rules
(Damian's global writing standards); no number appears without being
derived or dated.

**D5 — `docs/experiments/query_layer_demo_2026-08-13.md`.** Six to eight
canned queries with their real output from the build's graph state, each
labeled with the seed.json state (edge count + base commit) it ran
against. Include at least: one family query showing multi-string
coverage; the same query with and without `--closure`; one identity walk
depth 2; one provenance filter (human-adjudication); one pending-queue
listing. Quotes shown are only the graph's own ≤25-word quotes.

**D6 — `BUILD_REPORT.md`** (worktree root, committed). What was built,
commit-by-commit; how each acceptance check was verified (paste the test
run tail); deviations from this plan with reasons; open questions for the
morning review; and the recovery block: the exact commands to inspect
(`git worktree list`, `git log query-layer-dev`), to discard entirely
(`git worktree remove <path>; git branch -D query-layer-dev`), and to
merge (Damian's call only).

**Stretch, only if D1–D6 are green with time to spare:**
`tools/query/export_rdf.py` emitting Turtle with families as
`rdfs:subPropertyOf` super-properties, no transitivity axioms, header
comment stating why. If not reached, say so in the report — an honest
"not reached" beats a rushed exporter.

## Practices binding the executor

1. Hygiene: new files only; one deliverable per commit, named paths; no
   drive-by edits, no refactors of existing code, no formatting churn.
2. Auditability: every number in any produced doc is derived from data in
   the same commit or labeled with its source and date (RULES #12 spirit).
3. Traceability: D1 entries cite their doc lines; the demo cites its graph
   state; the report cites its base hash.
4. Recoverability: the branch is the whole blast radius; the report's
   recovery block makes discard a two-command operation.
5. Documentation current: QUERY.md ships in the same build, not "later";
   BACKLOG's v2.0 item is NOT edited (that status change happens at merge,
   in the main tree, after review).
6. If anything forces a choice this plan does not answer, choose the
   conservative reading, do it, and flag it prominently in the report —
   do not block waiting for a human at 3am, and do not widen scope.

## Rides along at merge time (main tree, after review — NOT overnight)

Approved by Damian 2026-08-12 evening: when the branch merges, the same
commit series also wires the ledger-freshness assertion into
`tools/check_paper_facts.py` — the rendered `web/public/ledger.html`'s
stated node/edge/reference counts must equal seed.json's, failing closed
like every other count check. Deferred past the overnight deliberately:
CI must not change under the mining pipeline's active windows.

## Acceptance for the morning review

The dev build is reviewable if: the branch exists with D1–D6 committed;
tests pass from a clean run in the worktree; the demo file shows real
output; the report is honest about anything skipped. The 08:00 update to
Damian reports exactly that state, plus the mining chat's overnight
progress, and hides nothing that failed.
