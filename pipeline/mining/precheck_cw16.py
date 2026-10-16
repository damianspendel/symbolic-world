#!/usr/bin/env python3
"""Deterministic pre-check for b-cw16-{N}.

Uses tests/test_graph.py's own tokenizer and matcher rather than a
reimplementation. The old pre-check counted whitespace words while the test
counts letter tokens, so "man's" was 1 here and 2 there; a quote passed the
pre-check and failed the canary run on b-cw13-7 because of it. Importing the
test module removes the class of bug entirely.

Failures are dropped, not argued with.

Run from the repo root:  python3 pipeline/work/precheck_b-cw16-{N}.py
"""
import json
import os
import re
import sys

sys.path.insert(0, 'tests')
import test_graph as T  # noqa: E402

import sys as _s
LO, HI, N = int(_s.argv[1]), int(_s.argv[2]), _s.argv[3]
CAND = f'pipeline/work/b-cw16-{N}_candidates.json'
OUT = f'pipeline/work/b-cw16-{N}_prechecked.json'
VALID_TYPES = {'Concept', 'Operation', 'Symbol', 'Substance', 'Figure', 'Motif'}
CLAIM_TYPES = {'jung-asserts', 'jung-reports-parallel', 'jung-quotes-source', 'jung-reports'}  # jung-reports = provisional; gate must resolve to the closed 3-value set

corpus = {}
for line in open('data/paragraphs.jsonl', encoding='utf-8'):
    p = json.loads(line)
    corpus[(str(p['volume']), p['paragraph'])] = T.words(p['text'])

seed = json.load(open('seed.json', encoding='utf-8'))
existing_ids = {n['id'] for n in seed['nodes']}
existing_triples = {(e['subject'], e['relation'], e['object']) for e in seed['edges']}

c = json.load(open(CAND, encoding='utf-8'))
# flatten per-candidate new_nodes to the top level the checker expects
if 'new_nodes' not in c:
    c['new_nodes'] = [n for x in c.get('candidates', []) for n in (x.get('new_nodes') or [])]
# miner flags attaches inline via existing_edge; route them to the attaches list
c.setdefault('attaches', [])
c['attaches'] += [x for x in c.get('candidates', []) if x.get('existing_edge')]
c['candidates'] = [x for x in c.get('candidates', []) if not x.get('existing_edge')]
seed_index = {(e['subject'], e['relation'], e['object']): e for e in seed['edges']}
new_ids = set()
node_fails = []
for n in c.get('new_nodes', []):
    if not n.get('id') or not n.get('label') or n.get('type') not in VALID_TYPES:
        node_fails.append(f"bad new_node schema: {n}")
    elif n['id'] in existing_ids:
        node_fails.append(f"new_node collides with existing id: {n['id']}")
    else:
        new_ids.add(n['id'])
known = existing_ids | new_ids


def form_ok(rel):
    PREP = {'of','to','in','with','by','into','for','from','as','on','over','through','like','beside','off','under','within','against','upon','at'}
    t = rel.split('-')
    return len(t) <= 3 or (len(t) == 4 and t[-1] in PREP)

def check_ref(subj, rel, obj, r, kind):
    """Return a list of failure strings for one reference."""
    tag = f"{subj} -{rel}-> {obj} (§{r.get('paragraph')}, {kind})"
    out = []
    if not form_ok(rel):
        out.append(f"[form] relation is not a verb phrase (P24): {tag}")
    key = (str(r.get('volume')), r.get('paragraph'))
    if key not in corpus:
        return [f"[anchor] paragraph not in corpus: {tag}"]
    if not (LO <= r['paragraph'] <= HI):
        out.append(f"[window] outside §{LO}-{HI}: {tag}")
    frags = [T.words(f) for f in re.split(r'\.\.\.|…', r.get('quote', '')) if T.words(f)]
    if not frags:
        return out + [f"[quote] empty: {tag}"]
    if len(frags) > 2:
        out.append(f"[quote] more than one ellipsis: {tag}")
    n_tok = sum(len(f) for f in frags)
    if n_tok > T.MAX_QUOTE_WORDS:
        out.append(f"[quote] {n_tok} > {T.MAX_QUOTE_WORDS} letter tokens: {tag}")
    err = T.quote_matches(frags, corpus[key])
    if err:
        out.append(f"[quote] {err}: {tag}")
    if r.get('claim_type') not in CLAIM_TYPES:
        out.append(f"[provenance] bad claim_type {r.get('claim_type')!r}: {tag}")
    if r.get('claim_type') == 'jung-quotes-source' and not r.get('source'):
        out.append(f"[provenance] jung-quotes-source without source: {tag}")
    if r.get('confidence') not in {'high', 'medium', 'low'}:
        out.append(f"[provenance] bad confidence {r.get('confidence')!r}: {tag}")
    if subj not in known:
        out.append(f"[node] undefined subject {subj}: {tag}")
    if obj not in known:
        out.append(f"[node] undefined object {obj}: {tag}")
    return out


kept, dropped = {'candidates': [], 'attaches': []}, []
seen = set()
for kind in ('candidates', 'attaches'):
    for ed in c.get(kind, []):
        subj, rel, obj = ed['subject'], ed['relation'], ed['object']
        triple = (subj, rel, obj)
        good_refs = []
        for r in ed.get('references', []):
            fails = check_ref(subj, rel, obj, r, kind)
            if (triple, r.get('paragraph')) in seen:
                fails.append(f"[dedup] repeated triple+paragraph: {triple} §{r.get('paragraph')}")
            if kind == 'candidates' and triple in existing_triples:
                fails.append(f"[dedup] candidate duplicates existing edge: {triple}")
            if kind == 'attaches' and triple not in existing_triples:
                fails.append(f"[attach] target edge does not exist: {triple}")
            if kind == 'attaches' and triple in existing_triples and any(
                    str(x.get('volume')) == '16' and x.get('paragraph') == r.get('paragraph')
                    for x in seed_index[triple].get('references', [])):
                fails.append(f"[dedup] paragraph already cited on edge: {triple} §{r.get('paragraph')}")
            if fails:
                dropped.append({'triple': list(triple), 'paragraph': r.get('paragraph'),
                                'reasons': fails})
            else:
                seen.add((triple, r.get('paragraph')))
                good_refs.append(r)
        if good_refs:
            kept[kind].append({'subject': subj, 'relation': rel, 'object': obj,
                               'references': good_refs})

used = {i for k in kept for ed in kept[k] for i in (ed['subject'], ed['object'])}
orphan_nodes = sorted(new_ids - used)
kept_nodes = [n for n in c.get('new_nodes', []) if n.get('id') in used]

n_refs = sum(len(e['references']) for k in kept for e in kept[k])
print(f"node schema failures: {len(node_fails)}")
for f in node_fails:
    print('  -', f)
print(f"orphaned new_nodes (dropped, no surviving edge): {orphan_nodes}")
print(f"references in:  {sum(len(e.get('references', [])) for k in ('candidates', 'attaches') for e in c.get(k, []))}")
print(f"references kept: {n_refs}")
print(f"references dropped: {len(dropped)}")
for d in dropped:
    print(f"  - {d['triple']} §{d['paragraph']}")
    for r in d['reasons']:
        print(f"      {r}")

json.dump({'batch': 'b-cw16-' + str(N), 'window': str(LO) + '-' + str(HI), 'new_nodes': kept_nodes,
           'candidates': kept['candidates'], 'attaches': kept['attaches'],
           'dropped': dropped, 'dedup_note': c.get('dedup_note', '')},
          open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\nwrote {OUT}: {len(kept['candidates'])} candidates, {len(kept['attaches'])} attaches, "
      f"{len(kept_nodes)} new nodes, {n_refs} refs")
