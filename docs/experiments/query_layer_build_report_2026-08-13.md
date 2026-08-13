# Query layer v1 — build report

Built overnight 2026-08-12/13 by an Opus-family executor, against
`docs/PLAN_QUERY_LAYER_BUILD.md` (drafted by the Fable-family validation
session). For Damian's morning review. Nothing was pushed, deployed, tagged or
merged, and nothing outside this worktree was written.

**Base commit:** `f83f6bfe604b23c90dbbaefc887bf3d39a1fa9d6`
(`audit_v071: systematic re-audit of pre-v0.7 assignments`), the committed head
of `mining-away` at kickoff.
**Branch:** `query-layer-dev`.
**Worktree:** `/Users/damianspendel/Documents/github/JungKG-query-dev`.
**Inputs read:** `seed.json` (407 nodes, 1555 edges, sha256 prefix
`fc7704327caa`), `docs/FAMILY_DEFINITIONS.md` at v0.7.1,
`tools/ontology_qa/quality.py` (for the observed-but-unruled inverse pairs).
The corpus under `data/` was not read.

## What was built

Six new files, 1891 lines, all additions. No existing file was modified, so the
diff against the base commit adds and changes nothing that the mining pipeline
owns.

| Commit | Deliverable | Path |
|---|---|---|
| `41a4c91` | D1 | `pipeline/family/relation_declarations.json` |
| `777319d` | D2 | `tools/query/kg_query.py` |
| `7b448f3` | D3 | `tests/test_query.py` |
| `47c0a7a` | D4 | `docs/QUERY.md` |
| `c09404e` | D2 follow-up | `tools/query/kg_query.py` |
| `fe51b45` | D5 | `docs/experiments/query_layer_demo_2026-08-13.md` |
| `1c65fbe` | D7 (stretch) | `tools/query/export_rdf.py`, `tests/test_query.py` |
| *(this file)* | D6 | `BUILD_REPORT.md` |

**D1** transcribes six ACTIVE declarations from FAMILY_DEFINITIONS v0.7.1, each
carrying the document line it came from: symbolizes/symbolized-by (371, 131),
produces/produced-by (131, 559), produces/originates-in restricted to generation
(559), manifests-as/is-aspect-of (393), manifests-as/is-manifestation-of (393,
dormant — the string has no edge in this graph), and synonym-of as symmetric
(415, 131). Six pairs the ontology-QA P05/P13 scan observed but the document
never ruled on sit inert in `candidates_awaiting_ruling`, each with the reason it
is not active.

**D2** is the CLI. Ten filters, `--closure`, `--walk identity --depth N`, table
/ `--json` / `--count` output, and a footer on every mode giving the node and
edge counts, the family-state tally, the `seed.json` digest and the declaration
set in force. Family membership is read from `relation_family` records at run
time; a test asserts no relation string and no family name other than the walk's
target appears as a literal in the file.

**D3** is 32 tests, no pinned counts.

**D4** documents the semantics and states the limits: families are assigned and
not verified, a derived row is not an edge and cannot compound, a walk is
exploration.

**D5** is eight queries with the output the commands actually produced, all
against the base-commit graph.

**D7** was reached: a Turtle export with families as `rdfs:subPropertyOf`
super-properties and no transitivity axiom anywhere.

## How the acceptance checks were verified

**The plan's gate: `python3 -m pytest tests/test_query.py -q` passes from the
worktree root.**

```
$ python3 -m pytest tests/test_query.py -q
................................                                         [100%]
32 passed in 0.53s
```

**The second gate: the existing suite is not made worse.** The before-state is
the baseline, and it is worth stating exactly, because it is not what it looks
like:

```
$ python3 -m pytest tests/ -q            # at f83f6bf, before any change
no tests ran in 0.00s                    # exit code 5
```

`tests/test_graph.py` is a standalone script, not a pytest module: it has no
`test_` functions and it needs `data/paragraphs.jsonl`, which this build must
not read. pytest collected nothing from it before this build and collects
nothing from it now. After:

```
$ python3 -m pytest tests/ -q
................................                                         [100%]
32 passed in 0.52s
```

Nothing regressed, because nothing was running. `tests/test_graph.py` was not
touched.

**Inherited CI state, not addressed and not to be read as this build's doing.**
The base commit is deliberately red in one respect: the v0.7.1 calibration is
HELD with five FAIL records filed (`59c575a`, "CI red by design"). That belongs
to the mining pipeline. `tools/check_paper_facts.py`, every calibration file and
every ledger were left alone, and the CI workflow was not edited.

**Read-only verified two ways.** Two tests hash `seed.json` before and after a
full closure pass, a depth-3 walk, and a Turtle export, and assert the digest is
unchanged. `git status --porcelain` in the main tree
(`/Users/damianspendel/Documents/github/JungKG`) shows only that session's own
work; nothing there was staged, committed or written by this build.

**Per-deliverable checks.**

- D1: a script re-read every `source` quote against `docs/FAMILY_DEFINITIONS.md`
  at the cited line. One citation was wrong on the first pass (the symmetry
  declaration, recorded at 416, actually at 415) and was corrected before commit.
  The same check now runs as a test, so a future edit to either file that breaks
  a citation fails.
- D2: every filter was exercised on the live graph and the row counts read off,
  before any test existed.
- D5: the file was assembled by running the CLI and pasting its stdout. Every
  block carries the tool's own footer, so the graph state is on the page next to
  the output rather than asserted above it.
- D7: `--out` was run and the result checked for statement termination, quote
  and angle balance, and undeclared prefixes: 2972 statements, 1555 edge
  triples, no failures.

## Deviations from the plan, and choices it did not answer

Practice 6 says to take the conservative reading, do it, and flag it. Nine
items.

1. **`--relation` vs `--string` vs `--effective`.** The plan lists all three
   without distinguishing the first. `--string` matches the verbatim relation and
   `--effective` the normalized-else-verbatim one, as the plan says; `--relation`
   was made the forgiving flag that matches either. That keeps all three
   meaningful. If the intent was that `--relation` be an alias for one of the
   others, it is a two-line change.

2. **`--provenance` is a substring match, not exact.** The stored values carry
   run context inside the string (`opus+gemini-agreed (v0.5)`), so exact matching
   would make the flag nearly useless. A consequence worth knowing: searching
   `human-adjudication` returns 21 rows, not the 20 edges whose `by` is exactly
   `human-adjudication`, because it also catches the one assigned by
   `precedent (human-adjudication 2026-08-10: ...)`. That edge was assigned by
   applying a human ruling, so including it is right, but the count differs from
   an exact match and the demo says so.

3. **The ACTIVE list is exactly the plan's enumeration, and the document lists
   more.** FAMILY_DEFINITIONS line 405 names `aspect-of` and `is-dark-aspect-of`
   beside `is-aspect-of` as inverse-direction manifestation strings. The plan's
   enumeration names only `is-aspect-of` and `is-manifestation-of`, so the other
   two sit in a third list, `doc_listed_not_adopted`, inert, with the line and the
   reason. Each has one edge in the current graph. **This is the item most likely
   to want a ruling.**

4. **Only `produces`/`originates-in` carries a family restriction.** The document
   restricts that one itself (line 559: only tradition-to-tradition
   `originates-in` is derivation). The others are declared on the strings, in the
   precedents table, so they are applied to the strings. One consequence:
   `symbolized-by` edges assigned `doctrinal-attribution` under the
   attribution-outranks-the-verb rule still derive an inverse row. The row carries
   its source's family, so nothing is misreported, but if the intent was that the
   declaration be read as symbolization-only, that is a one-field change.

5. **Derived rows that duplicate an asserted edge are dropped.** The plan does
   not say. Dropping them means closure adds only what the graph does not already
   say, which keeps a closure count meaningful. It also means a symmetric pair
   asserted in both directions produces no derived row at all.

6. **The identity walk crosses edges in both directions.** The plan does not say.
   The document calls archetypal-identity symmetric in principle (line 415), and a
   one-directional walk would answer a question nobody asked. Each hop prints the
   stored direction, and hops crossed against it are marked, so the traversal
   choice never hides the data.

7. **Four flags beyond the plan's list:** `--list-families`, `--list-declarations`,
   `--quotes`, `--limit`. `--list-families` is how the string-to-family derivation
   is inspectable rather than merely claimed; `--quotes` is what makes the demo's
   quotes come from the graph; `--limit` keeps demo output readable. All are
   read-only.

8. **One extra commit.** `c09404e` fixes "1 rows" / "1 hops" in the count lines,
   found while producing D5. It touches only wording in `kg_query.py`.

9. **D7's three restraints**, all stated in the emitted Turtle header:
   `rdfs:subPropertyOf` is asserted only for the relation strings that sit in
   exactly one family (27 of the assigned strings split across families, and a
   string-level super-property would be false for those); the family-restricted
   declaration is withheld from `owl:inverseOf` because OWL cannot scope an
   inverse; and the base IRI is marked PROVISIONAL, because this repository has a
   DOI and a site but has never minted a term namespace and that is not a build
   decision.

## Known limits

- **The Turtle was not parsed.** `rdflib` is not installed and the plan bars
  network access, so D7's syntax was checked structurally (termination, quote and
  angle balance, prefix declaration) rather than by a parser. Run it through one
  before trusting the file.
- **A plain triple carries no family**, so D7's edge block loses the per-edge
  assignment. The header says so and points at `seed.json`.
- **The demo is a snapshot.** Its numbers are true of the base-commit graph and
  will not be true after the next merge. Every block carries the digest it ran
  against, which is how you tell.
- **`--subject` and `--object` fall back to substring matching**, so a short
  needle can over-match. Exact node ids always match exactly.

## Open questions for the morning review

1. Should `aspect-of` and `is-dark-aspect-of` (deviation 3) join the ACTIVE list?
   The document lists them; the plan's enumeration did not.
2. Should `symbolizes`/`symbolized-by` be restricted to the symbolization family
   (deviation 4), given that the attribution rule places some `symbolized-by`
   edges in `doctrinal-attribution`?
3. Should closure derive rows from edges whose family state is
   `pending-adjudication` or `no-family`? It currently does, and prints the state
   as `unclassified(...)` on the row. The alternative is to derive only from
   assigned edges, which would make closure quieter and less complete.
4. Is `--relation` matching either layer (deviation 1) the behaviour you want?
5. Is the provisional namespace in D7 acceptable as a placeholder, or should the
   exporter refuse to run until one is minted?

## Recovery

**Inspect.**

```
git worktree list
git -C /Users/damianspendel/Documents/github/JungKG-query-dev log --oneline f83f6bf..query-layer-dev
git -C /Users/damianspendel/Documents/github/JungKG-query-dev diff --stat f83f6bf..query-layer-dev
```

**Discard entirely.** Two commands, from the main tree. Nothing else on disk is
affected, because every file in this build is new.

```
git worktree remove /Users/damianspendel/Documents/github/JungKG-query-dev
git branch -D query-layer-dev
```

**Merge.** Damian's decision, not the executor's, and not before review. When it
happens, the plan's ride-along applies: the same commit series also wires the
ledger-freshness assertion into `tools/check_paper_facts.py`, and BACKLOG's v2.0
item 2 changes status in the main tree at that point. Neither was done overnight,
deliberately: CI must not change under the mining pipeline's active windows.
