#!/usr/bin/env python3
"""OOPS!-style ontology pitfall scan for symbolic-world seed.json.

Each check maps to a numbered pitfall from the OOPS! catalogue where one applies.
Read-only. Prints findings grouped by severity.
"""
import json, re, sys
from collections import Counter, defaultdict

G = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'seed.json', encoding='utf-8'))
NODES = {n['id']: n for n in G['nodes']}
EDGES = G['edges']
rel = Counter(e['relation'] for e in EDGES)

CRIT, IMP, MINOR = [], [], []
def crit(t, m, ex=()): CRIT.append((t, m, list(ex)))
def imp(t, m, ex=()): IMP.append((t, m, list(ex)))
def minor(t, m, ex=()): MINOR.append((t, m, list(ex)))

lab = lambda i: NODES.get(i, {}).get('label', i)

# ---- P03/P22: no controlled relation vocabulary -------------------------
hapax = sorted(r for r, c in rel.items() if c == 1)
if len(hapax) / len(rel) > 0.4:
    crit("P22 no naming/vocabulary regularity",
         f"{len(hapax)}/{len(rel)} relations ({len(hapax)/len(rel)*100:.0f}%) are used exactly once. "
         f"The relation set is open-vocabulary, not an ontology property set.",
         hapax[:10])

sentence_rels = sorted(r for r in rel if r.count('-') >= 4)
if sentence_rels:
    crit("P24 relation name encodes a proposition",
         f"{len(sentence_rels)} relations are sentence-shaped — the predicate carries content that "
         f"belongs in the object or a qualifier, so it can never be queried or reasoned over.",
         sentence_rels[:8])

# ---- P02/P30: equivalent relations not declared equivalent ---------------
FAMILIES = {
    "identity/equivalence": ["synonym-of", "identical-to", "identified-with", "is-identified-with",
                             "identical-with", "equivalent-of", "is-equivalent-of", "alias-of",
                             "empirically-equivalent-to", "is-the-equivalent-of", "correlate-of",
                             "identical-or-connected-with", "coincides-with"],
    "symbolisation":       ["symbolizes", "signifies", "stands-for", "represents", "expresses",
                            "is-image-of", "image-of", "designated-as", "is-symbolic", "means",
                            "inwardly-signifies", "can-represent", "is-called"],
    "analogy/correspondence": ["corresponds-to", "parallels", "is-analogue-of", "analogue-of",
                               "is-psychic-analogue-of", "correlated-with", "likened-to",
                               "comes-nearest-to", "associated-with", "connected-to"],
    "part/containment":    ["contains", "includes", "part-of", "composed-of", "comprises",
                            "belongs-to", "aspect-of", "is-aspect-of", "chief-constituent-of",
                            "concealed-within", "harbours"],
    "generation/origin":   ["produces", "generates", "begets", "gives-birth-to", "born-of",
                            "produced-by", "produced-from", "springs-from", "derives-from",
                            "originates-in", "proceeded-from", "emerges-from", "rooted-in",
                            "is-rooted-in", "begotten-from"],
    "transformation":      ["transforms-into", "transforms", "transformed-through", "renewed-as",
                            "reborn-as", "dissolves-into", "renewed-through", "renewed-by"],
}
for fam, members in FAMILIES.items():
    present = [(m, rel[m]) for m in members if m in rel]
    if len(present) >= 3:
        tot = sum(c for _, c in present)
        crit(f"P02/P30 synonymous relations, {fam}",
             f"{len(present)} distinct relation strings express the same semantics across {tot} edges, "
             f"with no equivalence declared. A query on any one misses the rest.",
             present)

# ---- P05/P13: inverse relations present but not paired ------------------
INVERSES = [("symbolizes", "symbolized-by"), ("amplified-by", "amplifies"),
            ("precedes", "followed-by"), ("contains", "belongs-to"),
            ("produces", "produced-by"), ("mother-of", "child-of"),
            ("father-of", "child-of"), ("is-goal-of", "aims-at"),
            ("exemplified-by", "exemplifies"), ("broader", "narrower")]
present_pairs = [(a, b) for a, b in INVERSES if a in rel and b in rel]
if present_pairs:
    triples = {(e['subject'], e['relation'], e['object']) for e in EDGES}
    redundant, unpaired = [], []
    for a, b in present_pairs:
        for e in EDGES:
            if e['relation'] == a and (e['object'], b, e['subject']) in triples:
                redundant.append((lab(e['subject']), a, lab(e['object'])))
    imp("P05/P13 inverse relations declared but not linked",
        f"{len(present_pairs)} inverse pairs coexist in the vocabulary "
        f"({', '.join(a+'/'+b for a, b in present_pairs)}). Nothing declares them inverse, so "
        f"direction is a modelling choice made per-edge; {len(redundant)} pairs are asserted in both "
        f"directions and would be duplicates under a reasoner.",
        redundant[:5] or present_pairs)

# ---- symmetry violations -------------------------------------------------
SYMMETRIC = ["synonym-of", "identical-to", "identified-with", "corresponds-to", "parallels",
             "is-analogue-of", "polarizes-with", "opposes", "unites-with", "conjoined-with"]
triples = {(e['subject'], e['relation'], e['object']) for e in EDGES}
asym = []
for e in EDGES:
    if e['relation'] in SYMMETRIC and (e['object'], e['relation'], e['subject']) not in triples:
        asym.append((lab(e['subject']), e['relation'], lab(e['object'])))
if asym:
    imp("P25 symmetric relation asserted one-way only",
        f"{len(asym)} edges use a symmetric relation but only assert one direction. "
        f"Without a symmetry axiom, `A synonym-of B` does not answer a query for B's synonyms.",
        asym[:5])

# ---- transitivity ---------------------------------------------------------
syn = defaultdict(set)
for e in EDGES:
    if e['relation'] in ("synonym-of", "identical-to", "identified-with", "identical-with", "alias-of"):
        syn[e['subject']].add(e['object']); syn[e['object']].add(e['subject'])
comps, seen = [], set()
for k in syn:
    if k in seen: continue
    stack, comp = [k], []
    seen.add(k)
    while stack:
        c = stack.pop(); comp.append(c)
        for nb in syn[c]:
            if nb not in seen: seen.add(nb); stack.append(nb)
    if len(comp) > 2: comps.append(comp)
if comps:
    imp("P30 identity clusters not collapsed / no transitivity",
        f"{len(comps)} clusters of 3+ nodes are chained by identity-type relations without a "
        f"transitivity axiom or a canonical representative. These are candidate duplicate entities.",
        [[lab(x) for x in c] for c in comps[:4]])

# ---- P04: unconnected elements -------------------------------------------
adj = defaultdict(set)
for e in EDGES:
    adj[e['subject']].add(e['object']); adj[e['object']].add(e['subject'])
seen, parts = set(), []
for i in NODES:
    if i in seen: continue
    stack, comp = [i], []
    seen.add(i)
    while stack:
        c = stack.pop(); comp.append(c)
        for nb in adj[c]:
            if nb not in seen: seen.add(nb); stack.append(nb)
    parts.append(comp)
parts.sort(key=len, reverse=True)
if len(parts) > 1:
    imp("P04 unconnected ontology element",
        f"{len(parts)-1} component(s) detached from the main graph.",
        [[lab(x) for x in c][:2] for c in parts[1:]])

# ---- P08/P24: label quality ----------------------------------------------
long_lab = [(i, n['label']) for i, n in NODES.items() if len(n['label'].split()) > 8]
if long_lab:
    imp("P24 node label is a definition, not a term",
        f"{len(long_lab)} nodes carry a full descriptive sentence as their label. These are "
        f"assertions modelled as entities — they cannot be reused or matched across edges.",
        [l[:90] for _, l in long_lab[:4]])

norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
by_norm = defaultdict(list)
for i, nd in NODES.items(): by_norm[norm(nd['label'])].append(i)
dupe_lab = {k: v for k, v in by_norm.items() if len(v) > 1}
if dupe_lab:
    imp("P02 duplicate labels across distinct ids", f"{len(dupe_lab)} label collisions.",
        list(dupe_lab.values())[:5])

# ---- P11/P12: no declared domain/range ------------------------------------
sig = defaultdict(set)
for e in EDGES:
    if e['subject'] in NODES and e['object'] in NODES:
        sig[e['relation']].add((NODES[e['subject']]['type'], NODES[e['object']]['type']))
loose = sorted(((r, len(s), rel[r]) for r, s in sig.items() if rel[r] >= 8),
               key=lambda x: -x[1])
if loose:
    imp("P11/P12 no domain or range declared",
        f"No relation has a declared domain/range. Observed signatures are unconstrained: "
        f"`{loose[0][0]}` spans {loose[0][1]} distinct (subject-type, object-type) pairs across "
        f"{loose[0][2]} edges. Nothing can detect a mis-typed edge.",
        [f"{r}: {k} signatures over {n} edges" for r, k, n in loose[:6]])

# ---- P21: miscellaneous / catch-all class ---------------------------------
types = Counter(n['type'] for n in NODES.values())
if types.most_common(1)[0][1] / len(NODES) > 0.25:
    t, c = types.most_common(1)[0]
    minor("P21 catch-all class",
          f"`{t}` holds {c}/{len(NODES)} nodes ({c/len(NODES)*100:.0f}%) with no subdivision. "
          f"The type system carries little discriminating power.",
          [dict(types)])

# ---- P10: missing disjointness --------------------------------------------
minor("P10 missing disjointness axioms",
      f"The {len(types)} node types are never declared disjoint, and nothing forbids a node from "
      f"being conceptually two at once (e.g. Mercurius is modelled Figure but functions as Substance "
      f"and Symbol across its 52 edges). Type is a single free-text field.",
      [dict(types)])

# ---- taxonomy thinness -----------------------------------------------------
TAXO = {'is-a', 'broader', 'narrower', 'is-stage-of', 'aspect-of', 'is-aspect-of'}
taxo = [e for e in EDGES if e['relation'] in TAXO]
kids = {e['subject'] for e in taxo}
crit("P06/no backbone: taxonomy is vestigial",
     f"Only {len(taxo)}/{len(EDGES)} edges ({len(taxo)/len(EDGES)*100:.1f}%) are taxonomic and only "
     f"{len(kids)}/{len(NODES)} nodes ({len(kids)/len(NODES)*100:.0f}%) have any parent. "
     f"There is no subsumption hierarchy to inherit or reason over — this is an associative "
     f"network with a 6-way type tag, not a subsumption ontology.",
     [f"taxonomic relations present: {sorted(TAXO & set(rel))}"])

# ---- generic 'is' ----------------------------------------------------------
if 'is' in rel:
    ex = [(lab(e['subject']), lab(e['object'])) for e in EDGES if e['relation'] == 'is'][:4]
    imp("P02 ambiguous predicate `is`",
        f"`is` is used {rel['is']} times, conflating subsumption, identity and predication. "
        f"Cannot be interpreted without reading the quote.",
        ex)

# ---- evidence-side (not OOPS!, project-specific) --------------------------
noref = [e for e in EDGES if not e['references']]
if noref:
    imp("evidence gap", f"{len(noref)} edge(s) carry zero references.",
        [(lab(e['subject']), e['relation'], lab(e['object'])) for e in noref])

def show(title, items):
    print(f"\n### {title} ({len(items)})")
    for t, m, ex in items:
        print(f"\n[{t}]\n  {m}")
        for e in ex[:6]: print(f"    - {e}")

show("CRITICAL", CRIT); show("IMPORTANT", IMP); show("MINOR", MINOR)
print(f"\nTOTAL: {len(CRIT)} critical, {len(IMP)} important, {len(MINOR)} minor")
