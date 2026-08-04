#!/usr/bin/env python3
"""Ontology diagnostics for symbolic-world seed.json.

Structural metrics + OntoQA-style schema metrics. Read-only.
"""
import json, sys
from collections import Counter, defaultdict

G = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'seed.json', encoding='utf-8'))
NODES = {n['id']: n for n in G['nodes']}
EDGES = G['edges']
REFS = [r for e in EDGES for r in e['references']]

out = []
def p(s=''): out.append(str(s))

# ---------- 1. basic structure ----------
p("== 1. STRUCTURE ==")
ids = set(NODES)
p(f"nodes {len(NODES)}  edges {len(EDGES)}  refs {len(REFS)}")
dup_ids = [k for k, v in Counter(n['id'] for n in G['nodes']).items() if v > 1]
p(f"duplicate node ids: {len(dup_ids)} {dup_ids[:5]}")

dangling = [e for e in EDGES if e['subject'] not in ids or e['object'] not in ids]
p(f"dangling edge endpoints: {len(dangling)}")
selfloop = [e for e in EDGES if e['subject'] == e['object']]
p(f"self-loops: {len(selfloop)}  {[(e['subject'], e['relation']) for e in selfloop][:5]}")

triples = Counter((e['subject'], e['relation'], e['object']) for e in EDGES)
dup_tri = [t for t, c in triples.items() if c > 1]
p(f"duplicate triples (s,r,o): {len(dup_tri)}  {dup_tri[:3]}")

pairs = Counter(frozenset((e['subject'], e['object'])) for e in EDGES)
p(f"node pairs with >1 edge: {sum(1 for c in pairs.values() if c > 1)}")

deg = Counter()
indeg, outdeg = Counter(), Counter()
for e in EDGES:
    deg[e['subject']] += 1; deg[e['object']] += 1
    outdeg[e['subject']] += 1; indeg[e['object']] += 1
iso = sorted(i for i in ids if deg[i] == 0)
p(f"isolated nodes (no edge at all): {len(iso)}  {iso[:10]}")
leaf = sorted(i for i in ids if deg[i] == 1)
p(f"degree-1 nodes: {len(leaf)}")
n = len(ids)
p(f"density (directed): {len(EDGES)/(n*(n-1)):.4f}")
p(f"avg degree: {2*len(EDGES)/n:.2f}   max degree: {deg.most_common(1)}")
p(f"top hubs: {[(NODES[i]['label'], c) for i, c in deg.most_common(8)]}")

# connected components (undirected)
adj = defaultdict(set)
for e in EDGES:
    if e['subject'] in ids and e['object'] in ids:
        adj[e['subject']].add(e['object']); adj[e['object']].add(e['subject'])
seen, comps = set(), []
for i in ids:
    if i in seen: continue
    stack, comp = [i], []
    seen.add(i)
    while stack:
        c = stack.pop(); comp.append(c)
        for nb in adj[c]:
            if nb not in seen:
                seen.add(nb); stack.append(nb)
    comps.append(comp)
comps.sort(key=len, reverse=True)
p(f"connected components: {len(comps)}  sizes {[len(c) for c in comps[:10]]}")
if len(comps) > 1:
    for c in comps[1:6]:
        p(f"   island: {[NODES[x]['label'] for x in c]}")

# ---------- 2. relation vocabulary ----------
p()
p("== 2. RELATION VOCABULARY ==")
rel = Counter(e['relation'] for e in EDGES)
hapax = [r for r, c in rel.items() if c == 1]
p(f"distinct relations: {len(rel)} over {len(EDGES)} edges")
p(f"relations used exactly once (hapax): {len(hapax)}  ({len(hapax)/len(rel)*100:.0f}% of vocabulary, {len(hapax)/len(EDGES)*100:.0f}% of edges)")
p(f"relations used >=5 times: {sum(1 for c in rel.values() if c >= 5)}")
p(f"edges covered by top-10 relations: {sum(c for _, c in rel.most_common(10))/len(EDGES)*100:.0f}%")
p(f"top 12: {rel.most_common(12)}")
p(f"vocabulary entropy proxy — mean edges/relation: {len(EDGES)/len(rel):.2f}")
multiword = [r for r in rel if r.count('-') >= 4]
p(f"relations with >=5 tokens (sentence-shaped): {len(multiword)}")
p(f"   e.g. {multiword[:6]}")

# ---------- 3. OntoQA-style schema metrics ----------
p()
p("== 3. ONTOQA SCHEMA METRICS ==")
TAXO = {'is-a', 'broader', 'narrower', 'is-stage-of', 'aspect-of', 'is-aspect-of'}
taxo_edges = [e for e in EDGES if e['relation'] in TAXO]
p(f"taxonomic (subclass-ish) edges: {len(taxo_edges)}")
p(f"relationship richness  |non-taxo| / |all|  = {(len(EDGES)-len(taxo_edges))/len(EDGES):.3f}  (1.0 = no hierarchy at all)")
types = Counter(x['type'] for x in G['nodes'])
p(f"node types (classes): {dict(types)}")
p(f"inheritance richness (avg subclasses per class): {len(taxo_edges)/len(types):.2f}")
attrs = Counter(k for x in G['nodes'] for k in x if k not in ('id', 'type', 'label'))
p(f"attribute richness (non-core props per node): {sum(attrs.values())/len(NODES):.3f}   props: {dict(attrs)}")
p(f"class utilization: {len(types)}/{len(types)} types populated")

# taxonomy depth + cycles
parent = defaultdict(list)
for e in taxo_edges:
    parent[e['subject']].append(e['object'])
def depth(nid, path=()):
    if nid in path: return ('CYCLE', path + (nid,))
    if nid not in parent: return (0, None)
    best = 0; cyc = None
    for par in parent[nid]:
        d = depth(par, path + (nid,))
        if d[0] == 'CYCLE': return d
        if d[0] + 1 > best: best = d[0] + 1
    return (best, cyc)
depths, cycles = [], []
for i in ids:
    d = depth(i)
    if d[0] == 'CYCLE': cycles.append(d[1])
    else: depths.append(d[0])
p(f"max taxonomy depth: {max(depths) if depths else 0}   mean: {sum(depths)/len(depths):.2f}")
p(f"taxonomy cycles: {len(cycles)}  {cycles[:3]}")
p(f"nodes with any taxonomic parent: {len(parent)} / {len(ids)} ({len(parent)/len(ids)*100:.0f}%)")

# ---------- 4. domain/range coherence ----------
p()
p("== 4. DOMAIN / RANGE COHERENCE ==")
sig = defaultdict(Counter)
for e in EDGES:
    if e['subject'] in ids and e['object'] in ids:
        sig[e['relation']][(NODES[e['subject']]['type'], NODES[e['object']]['type'])] += 1
loose = []
for r, c in sig.items():
    if rel[r] >= 5:
        loose.append((r, rel[r], len(c), c.most_common(3)))
loose.sort(key=lambda x: -x[2])
p("relations used >=5x, by number of distinct (subjectType,objectType) signatures:")
for r, tot, k, top in loose[:12]:
    p(f"   {r:<22} n={tot:<4} {k} signatures   {top}")

# ---------- 5. provenance ----------
p()
p("== 5. PROVENANCE / EVIDENCE ==")
p(f"refs per edge: min {min(len(e['references']) for e in EDGES)}  "
  f"mean {len(REFS)/len(EDGES):.2f}  max {max(len(e['references']) for e in EDGES)}")
p(f"edges with 0 refs: {sum(1 for e in EDGES if not e['references'])}")
p(f"verified true: {sum(1 for r in REFS if r.get('verified'))}/{len(REFS)}")
p(f"confidence: {Counter(r.get('confidence') for r in REFS)}")
p(f"claim_type: {Counter(r.get('claim_type') for r in REFS)}")
p(f"crossvendor_checked: {sum(1 for r in REFS if r.get('crossvendor_checked'))}/{len(REFS)} "
  f"({sum(1 for r in REFS if r.get('crossvendor_checked'))/len(REFS)*100:.0f}%)")
p(f"volumes: {Counter(r['volume'] for r in REFS).most_common()}")
p(f"distinct paragraphs cited: {len({(r['volume'], r['paragraph']) for r in REFS})}")
para_reuse = Counter((r['volume'], r['paragraph']) for r in REFS)
p(f"most-reused paragraphs: {para_reuse.most_common(5)}")
p(f"quote length (words): mean {sum(len(r['quote'].split()) for r in REFS)/len(REFS):.1f}  "
  f"max {max(len(r['quote'].split()) for r in REFS)}")

# evidence concentration: how much of the graph rests on few paragraphs
top10 = sum(c for _, c in para_reuse.most_common(10))
p(f"share of refs from top-10 paragraphs: {top10/len(REFS)*100:.1f}%")

print('\n'.join(out))
