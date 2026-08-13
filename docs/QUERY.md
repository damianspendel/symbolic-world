# Querying the graph

`tools/query/kg_query.py` reads `seed.json` and prints rows. It writes nothing:
not the graph, not a cache, not a derived file. Everything it computes beyond
the stored edges is computed at read time, labelled, and discarded when the
process exits.

All figures below were read from `seed.json` at commit
`f83f6bfe604b23c90dbbaefc887bf3d39a1fa9d6` on 2026-08-13, and every command
prints the graph state it actually ran against in its own footer. Take the
footer over this page whenever the two disagree.

## Running it

```
python3 tools/query/kg_query.py [filters] [--closure] [--json|--count|--quotes]
python3 tools/query/kg_query.py --walk identity --subject <node> --depth N
python3 tools/query/kg_query.py --list-families
python3 tools/query/kg_query.py --list-declarations
```

No arguments prints every edge. `--seed` and `--declarations` point the tool at
other files, which is how the tests run it against fixtures.

## Filters

Filters combine with AND. Each reads a field the graph already stores; none
computes a judgement of its own.

| Flag | Reads | Match |
|---|---|---|
| `--family` | `relation_family.value` | exact |
| `--state` | `relation_family.state` | exact |
| `--provenance` | `relation_family.by` | substring, case-insensitive |
| `--claim-type` | any reference's `claim_type` | exact |
| `--volume` | any reference's `volume` | exact |
| `--subject`, `--object` | node id | exact id, else substring of id or label |
| `--relation` | verbatim or effective relation | exact, either one |
| `--string` | verbatim relation | exact |
| `--effective` | effective relation | exact |

`--provenance` is a substring match because the stored values carry their run
context inside the string, for example `opus+gemini-agreed (v0.5)`. A search for
`human-adjudication` therefore also returns the edge whose provenance reads
`precedent (human-adjudication 2026-08-10: layer tag does not override content
family)`, which is the intended behaviour: that edge was assigned by applying a
human ruling.

`--subject` and `--object` fall back to substring because node ids are long and
labels are longer. An exact id always wins over a substring elsewhere.

### Effective relation

260 of the 1555 edges carry a `relation_normalized` layer, which holds a cleaned
relation string beside the frozen verbatim one. The *effective* relation is
`relation_normalized.relation` where that layer exists and the verbatim
`relation` otherwise, following FAMILY_DEFINITIONS v0.7.1 (line 112-114). Family
assignment classifies the effective relation, so `--family` and `--effective`
line up; `--string` reaches the frozen surface form, which is what you want when
you are auditing the normalization layer rather than reading through it.

## Families are assigned, not verified

`--family` reports what the assignment pipeline recorded on an edge. It does not
report that the assignment is right. The vocabulary discipline that binds
FAMILY_DEFINITIONS binds this tool and this page: an assignment is a proposal
that has passed the sign-off ladder in force at the time, and the document's own
sign-off condition (v0.7.1, "Sign-off condition") is not met by model agreement
alone.

The current graph carries 1555 edges. Their family states, counted 2026-08-13:

| State | Edges |
|---|---|
| assigned | 1264 |
| pending-adjudication | 248 |
| no-family | 41 |
| text-undecided | 2 |

`no-family` and `text-undecided` are the two reason codes of the `unclassified`
administrative class, and the document keeps them apart on purpose: `no-family`
is evidence about the vocabulary, `text-undecided` is a property of the corpus.
`--state` returns them separately and the tool never pools them.

24 families hold at least one assigned edge. FAMILY_DEFINITIONS defines 25;
`amplification` holds none, because the v0.7.1 re-run of the 43 `amplified-by`
edges placed none of them there. `--list-families` prints the live list with the
edge and string counts behind each, all read from `relation_family` records
rather than from any table inside the tool.

## Closure

`--closure` adds rows the ACTIVE declarations in
`pipeline/family/relation_declarations.json` license, applied to the whole graph
and then filtered like any other row. Over the current graph, closure adds 183
rows to the 1555 stored edges.

What a derived row asserts: that a stored edge can be read in the other
direction, because the document declared the two relation strings inverse or
declared one symmetric. Nothing more. The row carries the source edge's own
references and its own family assignment, and prints the edge it came from:

```
The Self  symbolized-by  Lapis philosophorum  [CW12 §247, ...]  {symbolization}
          <derived:inverse-of(symbolizes) of lapis symbolizes the-self>
```

What a derived row does not assert:

- It is not an edge. It is never written to `seed.json`, it carries no
  independent citation, and its label says where it came from. A count of edges
  and a count of closure rows are different quantities, and the footer reports
  the edge count either way.
- It is not a chain. No declaration is transitive, and the tool applies each
  declaration once, to stored edges only. Derived rows are not fed back in, so
  closure cannot compound.
- It is not a new reading of the text. The reference behind a derived row is the
  reference behind its source edge, and the quote says what it said before.

Rows that would duplicate an edge the graph already asserts are dropped, so
`--closure` adds only what the graph does not already say. Where a declaration
carries a family restriction, the restriction is read off the source edge:
`produces`/`originates-in` is declared for generation only, so an
`originates-in` edge assigned `derivation` (`alchemy originates-in gnosticism`)
derives nothing.

Six pairs sit in `candidates_awaiting_ruling` in the same file: pairs the
ontology-QA scan found coexisting in the vocabulary that FAMILY_DEFINITIONS has
never ruled on. They are inert. `--closure` does not read them, and moving one
into `active` is an edit someone makes deliberately, with a document line to
cite.

## Walks

`--walk identity --subject X --depth N` follows `archetypal-identity` edges out
from X, breadth-first, stopping at depth N, visiting each node once. Every hop
prints the edge it crossed and that edge's citation, and hops that ran against
the edge direction say so.

The walk is exploration. It shows what the graph connects; it does not conclude
anything about the terms at the ends. Reaching Saturn from Mercurius in one hop
and Yahweh from Saturn in the next does not make Mercurius and Yahweh identical,
and the output header says so before the first hop. FAMILY_DEFINITIONS rejects
transitivity on every family (line 131): alchemical sequences are cyclical, and
a transitive relation over them derives A from A.

The walk crosses edges in both directions, because archetypal-identity is
symmetric in principle (line 415). That is a choice about traversal, not a claim
about the edges: the direction each edge was stored in is printed with the hop.

Two limits worth stating. The walk reads the family, not the relation string, so
it crosses whatever edges the pipeline assigned to `archetypal-identity`,
including the ones still carrying a disputed provenance. And the family holds
124 edges as of 2026-08-13, enough that a depth-3 walk from a well-connected
node reaches most of what it will ever reach: from Mercurius it returns 67
nodes, against the 88 the whole identity component holds, which the same walk
returns at depth 7. Depth is a budget, not a measure of closeness.

## Output

The table is the default. `--json` emits the same rows with their full reference
records, `--count` prints the totals and nothing else, `--quotes` adds each row's
first stored quote under it. The graph's quotes are capped at 25 words by the
integrity checks, so `--quotes` never prints more than the graph already holds.

Every mode ends with the same footer:

```
407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication,
41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa;
declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

The digest is over the `seed.json` bytes the command actually read. Two outputs
carrying the same digest ran against the same graph; two carrying different
digests are not comparable, whatever their row counts suggest. `5 active` counts
the declarations in force, which is the ACTIVE list minus the dormant entries.

## What this tool does not do

- It does not verify anything. Verification state lives on references
  (`verified`, `verified_by`) and the tool prints it in `--json`; it never
  recomputes it.
- It does not rank or score. Rows come out in graph order, derived rows after
  stored ones.
- It does not read the corpus. Quotes come from `seed.json`, so a quote here is
  a quote the mining pipeline already checked against the paragraph.
- It does not edit declarations. Adopting an inverse pair, or retiring one, is a
  human decision recorded in `relation_declarations.json` with the
  FAMILY_DEFINITIONS line it transcribes.

## The carried-qualifier rule (ruling of 2026-08-13)

Two doc-listed manifestation inverse strings were activated by Damian's
ruling: `aspect-of` flips losslessly; `is-dark-aspect-of` flips WITH its
qualifier carried — the derived row displays "dark aspect" beside its
origin, so the reverse reading asserts exactly as much as the stored edge.
The general principle, adopted as precedent: a derived row must carry
everything the stored row asserted; if a flip cannot carry its qualifier,
the declaration is not made. The ruling is logged in
`pipeline/family/relation_declarations.json` under `rulings`.
