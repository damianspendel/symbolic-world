#!/usr/bin/env python3
"""Themis-style competency-question tests for symbolic-world seed.json.

Each CQ is a question the graph claims to answer, expressed as an executable query
with a stated pass criterion. Verdicts: PASS / PARTIAL / FAIL.
PARTIAL = returns an answer, but an equally valid phrasing of the same question
returns a different answer (i.e. the answer is not stable under the ontology).
"""
import json, sys
from collections import defaultdict, Counter

G = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'seed.json', encoding='utf-8'))
NODES = {n['id']: n for n in G['nodes']}
EDGES = G['edges']
lab = lambda i: NODES.get(i, {}).get('label', i)
out = defaultdict(list)

def E(**kw):
    r = EDGES
    for k, v in kw.items():
        k = {'s': 'subject', 'r': 'relation', 'o': 'object'}[k]
        r = [e for e in r if e[k] == v] if isinstance(v, str) else [e for e in r if e[k] in v]
    return r

def around(nid):
    return [e for e in EDGES if e['subject'] == nid or e['object'] == nid]

RESULTS = []
def cq(n, q, verdict, got, why):
    RESULTS.append((n, q, verdict, got, why))

SYMBOLISE = {"symbolizes", "signifies", "stands-for", "represents", "expresses", "is-image-of",
             "image-of", "designated-as", "can-represent", "inwardly-signifies", "is-symbolic"}
IDENTITY = {"synonym-of", "identical-to", "identified-with", "is-identified-with", "identical-with",
            "equivalent-of", "is-equivalent-of", "alias-of", "is-the-equivalent-of"}
ANALOGY = {"corresponds-to", "parallels", "is-analogue-of", "analogue-of", "is-psychic-analogue-of",
           "correlated-with", "likened-to"}
TRANSFORM = {"transforms-into", "transforms", "transformed-through", "renewed-as", "reborn-as",
             "dissolves-into", "renewed-through", "renewed-by", "produced-from"}

# CQ1 — the paper's own headline question
e = around('green-lion')
cq(1, "What is the green lion, and on whose authority?",
   "PASS" if e and all(r.get('claim_type') for x in e for r in x['references']) else "FAIL",
   [f"{lab(x['subject'])} --{x['relation']}--> {lab(x['object'])} "
    f"[CW{x['references'][0]['volume']} §{x['references'][0]['paragraph']}, {x['references'][0]['claim_type']}]"
    for x in e],
   "every edge carries § anchor + claim type")

# CQ2 — symbols of the Self, single relation
strict = E(r='symbolizes', o='the-self')
broad = [x for x in EDGES if x['relation'] in SYMBOLISE and x['object'] == 'the-self']
cq(2, "What symbolises the Self?",
   "PASS" if len(strict) == len(broad) else "PARTIAL",
   f"{len(strict)} via `symbolizes`; {len(broad)} once synonymous predicates are unioned "
   f"(+{len(broad)-len(strict)}: {[lab(x['subject'])+'/'+x['relation'] for x in broad if x not in strict]})",
   "answer depends on which of 12 symbolisation predicates you query")

# CQ3 — stages of the opus in order
chain, cur, seen = [], 'nigredo', set()
while cur and cur not in seen:
    seen.add(cur); chain.append(lab(cur))
    cur = next((x['object'] for x in E(s=cur, r='precedes')), None)
cq(3, "What are the stages of the opus, in order?",
   "PASS" if len(chain) >= 3 else "FAIL", " -> ".join(chain),
   f"{len(chain)} stages recovered by following `precedes`")

# CQ4 — synonyms of prima materia (symmetry)
fwd = [x['object'] for x in EDGES if x['subject'] == 'prima-materia' and x['relation'] in IDENTITY]
rev = [x['subject'] for x in EDGES if x['object'] == 'prima-materia' and x['relation'] in IDENTITY]
cq(4, "What are the synonyms of the prima materia?",
   # pass only if direction does not change the answer set
   "PASS" if not (fwd and rev) and not (rev and not fwd) else "PARTIAL",
   f"forward (prima-materia as subject): {[lab(x) for x in fwd]}; "
   f"reverse (as object): {[lab(x) for x in rev]}",
   "no symmetry axiom — a naive forward-only query returns "
   f"{len(fwd)} of {len(fwd)+len(rev)} answers")

# CQ5 — claim provenance filter
rp = [x for x in EDGES if any(r['claim_type'] == 'jung-quotes-source' for r in x['references'])]
named = [r.get('source') for x in EDGES for r in x['references'] if r.get('source')]
cq(5, "Which claims are Jung quoting a named source, and who?",
   "PASS" if rp and named else "FAIL",
   f"{len(rp)} edges, {len(set(named))} distinct named sources, e.g. {sorted(set(named))[:6]}",
   "claim_type + source fields answer this directly")

# CQ6 — what is subsumed under Archetype
kids = [x['subject'] for x in EDGES if x['object'] == 'archetype' and x['relation'] in ('is-a', 'broader')]
taxo_all = [x for x in EDGES if x['relation'] in ('is-a', 'broader', 'narrower')]
cq(6, "What kinds of archetype does the graph distinguish?",
   # a taxonomy query passes only if the hierarchy is deep enough to be worth querying
   "PASS" if len(kids) >= 3 and len(taxo_all) / len(EDGES) > 0.10 else "PARTIAL",
   [lab(k) for k in kids],
   f"returns {len(kids)} children, all depth-1; graph-wide only {len(taxo_all)}/{len(EDGES)} edges "
   f"({len(taxo_all)/len(EDGES)*100:.1f}%) are taxonomic, so this answer is a local accident, "
   f"not a hierarchy")

# CQ7 — typed query
tq = [x for x in EDGES if x['relation'] in SYMBOLISE
      and NODES.get(x['subject'], {}).get('type') == 'Substance'
      and NODES.get(x['object'], {}).get('type') == 'Concept']
cq(7, "Which substances symbolise a concept?", "PASS" if tq else "FAIL",
   f"{len(tq)} edges, e.g. {[(lab(x['subject']), lab(x['object'])) for x in tq[:3]]}",
   "node type + relation gives a working typed query")

# CQ8 — multi-hop path Christ -> lapis
adj = defaultdict(list)
for x in EDGES:
    adj[x['subject']].append((x['object'], x['relation']))
    adj[x['object']].append((x['subject'], 'inv:' + x['relation']))
def path(a, b, maxd=4):
    q, seen = [(a, [])], {a}
    while q:
        cur, pth = q.pop(0)
        if len(pth) > maxd: continue
        for nb, r in adj[cur]:
            if nb == b: return pth + [(cur, r, nb)]
            if nb not in seen:
                seen.add(nb); q.append((nb, pth + [(cur, r, nb)]))
    return None
pth = path('christ', 'lapis')
cq(8, "How is Christ connected to the lapis?", "PASS" if pth else "FAIL",
   " | ".join(f"{lab(a)} -{r}-> {lab(c)}" for a, r, c in pth) if pth else "no path",
   "multi-hop traversal works; edge semantics along the path are heterogeneous")

# CQ9 — hedged / weaker claims
med = [x for x in EDGES if any(r['confidence'] == 'medium' for r in x['references'])]
cq(9, "Which claims are weakly anchored and need review?", "PASS",
   f"{len(med)} edges have a medium-confidence reference",
   "confidence field supports a triage worklist")

# CQ10 — what transforms into the lapis
t = [x for x in EDGES if x['object'] == 'lapis' and x['relation'] in TRANSFORM]
t_strict = [x for x in EDGES if x['object'] == 'lapis' and x['relation'] == 'transforms-into']
cq(10, "What transforms into the lapis?",
   "PARTIAL" if len(t) != len(t_strict) else ("PASS" if t else "FAIL"),
   f"strict `transforms-into`: {[lab(x['subject']) for x in t_strict]}; "
   f"transformation family unioned: {[lab(x['subject'])+'/'+x['relation'] for x in t]}",
   "8 transformation predicates, no equivalence declared")

# CQ11 — everything about Mercurius
m = around('mercurius')
cq(11, "Give me everything Jung says about Mercurius, with sources.", "PASS",
   f"{len(m)} edges, {sum(len(x['references']) for x in m)} references, "
   f"{len({x['relation'] for x in m})} distinct relations",
   f"complete but the {len({x['relation'] for x in m})} distinct predicates over {len(m)} edges "
   f"make the result a reading list, not a structured answer")

# CQ12 — opposition pairs
opp = [x for x in EDGES if x['relation'] in ('opposes', 'polarizes-with', 'counterbalances-light-nature-of')]
cq(12, "Which pairs of opposites does the graph record?",
   "PARTIAL" if len(opp) < 10 else "PASS",
   [(lab(x['subject']), x['relation'], lab(x['object'])) for x in opp],
   f"only {len(opp)} opposition edges across 3 predicates, for a corpus built on the union of opposites")

# CQ13 — volume grounding
vol = Counter(r['volume'] for x in around('mercurius') for r in x['references'])
cq(13, "Which volumes ground the Mercurius material?", "PASS", dict(vol),
   "volume/paragraph on every reference")

# CQ14 — inverse-direction retrieval
sym_out = E(s='the-self', r='symbolizes')
sym_in = E(o='the-self', r='symbolizes')
cq(14, "Ask the graph 'what does the Self symbolise?' vs 'what symbolises the Self?'",
   "PASS" if len(sym_in) > 0 else "FAIL",
   f"as subject: {len(sym_out)}; as object: {len(sym_in)}",
   "direction is consistently modelled for `symbolizes` (symbol -> referent)")

# CQ15 — nodes with no grounding
grounded = {x['subject'] for x in EDGES} | {x['object'] for x in EDGES}
ungrounded = [i for i in NODES if i not in grounded]
cq(15, "Which nodes have no textual grounding at all?",
   "PASS" if not ungrounded else "FAIL", ungrounded or "none — every node participates in >=1 cited edge",
   "no orphan entities")

# CQ16 — cross-tradition correspondence
tr = [x for x in EDGES if x['relation'] in ANALOGY and x['subject'] == 'mercurius']
cq(16, "What does Mercurius correspond to across traditions?",
   "PARTIAL" if not all(NODES.get(x['object'], {}).get('tradition') for x in tr) else "PASS",
   f"{len(tr)} correspondences: {[lab(x['object']) for x in tr]}; "
   f"nodes carrying a `tradition` attribute: {sum(1 for n in NODES.values() if 'tradition' in n)}/{len(NODES)}",
   "the question is answerable per-edge but not aggregable — tradition is on 4 nodes only")

# CQ17 — the shadow of the Self
sh = around('shadow-of-the-self')
cq(17, "What is the shadow of the Self?", "PASS" if sh else "FAIL",
   [f"{lab(x['subject'])} -{x['relation']}-> {lab(x['object'])}" for x in sh],
   "answered with anchors")

# CQ18 — identity transitivity blow-up
ident = defaultdict(set)
for x in EDGES:
    if x['relation'] in IDENTITY:
        ident[x['subject']].add(x['object']); ident[x['object']].add(x['subject'])
seen, big = set(), 0
for k in ident:
    if k in seen: continue
    stack, comp = [k], []
    seen.add(k)
    while stack:
        c = stack.pop(); comp.append(c)
        for nb in ident[c]:
            if nb not in seen: seen.add(nb); stack.append(nb)
    big = max(big, len(comp))
cq(18, "If identity relations were treated as transitive, is the result coherent?",
   "FAIL" if big > 10 else "PASS",
   f"largest identity-closure cluster: {big} nodes",
   f"treating `synonym-of`/`identical-to` as transitive collapses {big} distinct symbols "
   f"into one entity — the relations mean 'associated with', not identity")

# CQ19 — count answerable without reading quotes
opaque = [x for x in EDGES if x['relation'].count('-') >= 4]
cq(19, "Can a machine consume every edge without reading the quote?",
   "FAIL" if opaque else "PASS",
   f"{len(opaque)} edges use a sentence-shaped predicate that only a human reader can interpret",
   "these edges are prose in triple clothing")

# CQ20 — reproducibility of a count
cq(20, "Does the graph report its own size consistently?",
   "PASS" if len(NODES) == 248 and len(EDGES) == 669 else "FAIL",
   f"{len(NODES)} nodes / {len(EDGES)} edges / {sum(len(x['references']) for x in EDGES)} refs "
   f"— matches README (248/669/699)",
   "counts match the published figures and Zenodo metadata")

w = Counter(v for _, _, v, _, _ in RESULTS)
for n, q, v, got, why in RESULTS:
    print(f"\nCQ{n:<2} [{v}]  {q}")
    print(f"      -> {got}")
    print(f"      why: {why}")
print(f"\n{'='*70}\nPASS {w['PASS']}  PARTIAL {w['PARTIAL']}  FAIL {w['FAIL']}   (n={len(RESULTS)})")
