#!/usr/bin/env python3
"""Deterministic pre-check for b-cw14-{N} (trilogy second pass).

Beside the standing checks it enforces the rulings of 2026-11-11: the attach rule (a quote already in the
graph on the same paragraph is dropped), the source fields on quoted and reported claims, the names list,
the cross-register flag, and the per-volume quotation cap (quote_share.CAP_PCT): a window that would take
its volume over the cap is refused whole, nothing is written, and the miner is sent back to shorten or thin.

Uses tests/test_graph.py's own tokenizer and matcher rather than a
reimplementation. The old pre-check counted whitespace words while the test
counts letter tokens, so "man's" was 1 here and 2 there; a quote passed the
pre-check and failed the canary run on b-cw13-7 because of it. Importing the
test module removes the class of bug entirely.

Failures are dropped, not argued with.

Run from the repo root:  python3 pipeline/mining/precheck_cw14.py LO HI N
"""
import json
import os
import re
import sys

sys.path.insert(0, 'tests')
import test_graph as T  # noqa: E402
sys.path.insert(0, 'pipeline/mining')
import quote_share as QS  # noqa: E402

import sys as _s
LO, HI, N = int(_s.argv[1]), int(_s.argv[2]), _s.argv[3]
CAND = f'pipeline/work/b-cw14-{N}_candidates.json'
OUT = f'pipeline/work/b-cw14-{N}_prechecked.json'
VALID_TYPES = {'Concept', 'Operation', 'Symbol', 'Substance', 'Figure', 'Motif'}
CLAIM_TYPES = {'jung-asserts', 'jung-reports-parallel', 'jung-quotes-source', 'jung-reports'}  # jung-reports = provisional; gate must resolve to the closed 3-value set

corpus = {}
for line in open('data/paragraphs.jsonl', encoding='utf-8'):
    p = json.loads(line)
    corpus[(str(p['volume']), p['paragraph'])] = T.words(p['text'])

seed = json.load(open('seed.json', encoding='utf-8'))
existing_ids = {n['id'] for n in seed['nodes']}
existing_triples = {(e['subject'], e['relation'], e['object']) for e in seed['edges']}
# the attach rule: every quote already in the graph, by paragraph, as a token tuple
existing_quotes = {}
for e in seed['edges']:
    for r in e.get('references', []):
        existing_quotes.setdefault((str(r.get('volume')), r.get('paragraph')), []).append(tuple(T.words(r.get('quote', ''))))
SRC = json.load(open('pipeline/mining/sources_controlled.json', encoding='utf-8'))
AUTHORS = set(SRC['authors']) | set(SRC['traditions'])
TEXTS = set(SRC['texts'])
VARIANTS = SRC['variants']
SOURCED = {'jung-quotes-source', 'jung-reports-parallel'}
other_sources = []

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

def repeats_existing(frags, key):
    """True when the quote's tokens equal, or sit contiguously inside, a quote already on this paragraph."""
    toks = tuple(x for f in frags for x in f)
    for q in existing_quotes.get(key, []):
        if len(toks) <= len(q) and any(q[i:i + len(toks)] == toks for i in range(len(q) - len(toks) + 1)):
            return True
    return False


def canon(v):
    return VARIANTS.get(v, v) if isinstance(v, str) else v


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
    if repeats_existing(frags, key):
        out.append(f"[attach] quote already in the graph on this paragraph: {tag}")
    if r.get('claim_type') in SOURCED:
        a, x = canon(r.get('source_author')), canon(r.get('source_text'))
        if a is not None:
            r['source_author'] = a
        if x is not None:
            r['source_text'] = x
        if not a and not x:
            out.append(f"[source] {r.get('claim_type')} without source_author or source_text: {tag}")
        if a and a != 'other' and a not in AUTHORS:
            out.append(f"[source] source_author {a!r} is not in the controlled list (write 'other' and keep the free-text source): {tag}")
        if x and x != 'other' and x not in TEXTS:
            out.append(f"[source] source_text {x!r} is not in the controlled list (write 'other' and keep the free-text source): {tag}")
        if (a == 'other' or x == 'other') and not r.get('source'):
            out.append(f"[source] 'other' without a free-text source: {tag}")
        if a == 'other' or x == 'other':
            other_sources.append(r.get('source'))
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
        if 'cross_register' in ed and not isinstance(ed['cross_register'], bool):
            dropped.append({'triple': list(triple), 'paragraph': None, 'reasons': [f'[flag] cross_register is not a boolean: {ed["cross_register"]!r}']})
            continue
        for r in ed.get('references', []):
            fails = check_ref(subj, rel, obj, r, kind)
            if (triple, r.get('paragraph')) in seen:
                fails.append(f"[dedup] repeated triple+paragraph: {triple} §{r.get('paragraph')}")
            if kind == 'candidates' and triple in existing_triples:
                fails.append(f"[dedup] candidate duplicates existing edge: {triple}")
            if kind == 'attaches' and triple not in existing_triples:
                fails.append(f"[attach] target edge does not exist: {triple}")
            if kind == 'attaches' and triple in existing_triples and any(
                    str(x.get('volume')) == '14' and x.get('paragraph') == r.get('paragraph')
                    for x in seed_index[triple].get('references', [])):
                fails.append(f"[dedup] paragraph already cited on edge: {triple} §{r.get('paragraph')}")
            if fails:
                dropped.append({'triple': list(triple), 'paragraph': r.get('paragraph'),
                                'reasons': fails})
            else:
                seen.add((triple, r.get('paragraph')))
                good_refs.append(r)
        if good_refs:
            out_ed = {'subject': subj, 'relation': rel, 'object': obj, 'references': good_refs}
            if ed.get('cross_register') is True:
                out_ed['cross_register'] = True
            kept[kind].append(out_ed)

# the names list (concordance field 1): node known, paragraph in the window, every name present in the paragraph
import unicodedata


def fold(s):
    return ' '.join(unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().split())


para_text = {}
for line in open('data/paragraphs.jsonl', encoding='utf-8'):
    p = json.loads(line)
    if str(p['volume']) == '14' and LO <= p['paragraph'] <= HI:
        para_text[p['paragraph']] = fold(p['text'])
kept_names, name_fails = [], []
for nm in c.get('names', []):
    node, para = nm.get('node'), nm.get('paragraph')
    vals = ([nm['latin']] if nm.get('latin') else []) + list(nm.get('aliases') or [])
    why = []
    if node not in known:
        why.append(f'unknown node {node}')
    if para not in para_text:
        why.append(f'paragraph {para} outside the window')
    if not vals:
        why.append('no latin and no aliases')
    for v in vals:
        if not isinstance(v, str) or (para in para_text and fold(v) not in para_text[para]):
            why.append(f'name {v!r} not in paragraph {para}')
    if why:
        name_fails.append({'name': nm, 'reasons': why})
    else:
        kept_names.append({'node': node, 'paragraph': para, **({'latin': nm['latin']} if nm.get('latin') else {}), **({'aliases': list(nm['aliases'])} if nm.get('aliases') else {})})
used = {i for k in kept for ed in kept[k] for i in (ed['subject'], ed['object'])}
used |= {nm['node'] for nm in kept_names}
orphan_nodes = sorted(new_ids - used)
kept_nodes = [n for n in c.get('new_nodes', []) if n.get('id') in used]

n_refs = sum(len(e['references']) for k in kept for e in kept[k])
# the quotation cap (Damian, 2026-11-11, option B): the window may not take its volume over the cap
new_quotes = [r['quote'] for k in kept for e in kept[k] for r in e['references']]
cw, qw, pct = QS.share('14', seed, new_quotes)
print(f"quotation share CW 14 after this window: {qw} of {cw} letter tokens = {pct:.2f}% (cap {QS.CAP_PCT}%)")
if pct > QS.CAP_PCT:
    print(f'HOLD: the window would take CW 14 over the quotation cap; nothing written. Shorten quotes or thin the window and re-run.')
    raise SystemExit(2)
print(f"node schema failures: {len(node_fails)}")
for f in node_fails:
    print('  -', f)
print(f"orphaned new_nodes (dropped, no surviving edge): {orphan_nodes}")
print(f"references in:  {sum(len(e.get('references', [])) for k in ('candidates', 'attaches') for e in c.get(k, []))}")
print(f"references kept: {n_refs}")
print(f"references dropped: {len(dropped)}")
print(f"names kept: {len(kept_names)}, names dropped: {len(name_fails)}")
for f in name_fails:
    print('  -', f['name'].get('node'), f['reasons'])
print(f"'other' sources (candidates for the controlled list): {sorted(set(s for s in other_sources if s))}")
for d in dropped:
    print(f"  - {d['triple']} §{d['paragraph']}")
    for r in d['reasons']:
        print(f"      {r}")

json.dump({'batch': 'b-cw14-' + str(N), 'window': str(LO) + '-' + str(HI), 'new_nodes': kept_nodes,
           'candidates': kept['candidates'], 'attaches': kept['attaches'], 'names': kept_names,
           'dropped': dropped, 'names_dropped': name_fails, 'dedup_note': c.get('dedup_note', ''),
           'proposer_model': c.get('proposer_model'), 'quotation_share_after': round(pct, 2)},
          open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\nwrote {OUT}: {len(kept['candidates'])} candidates, {len(kept['attaches'])} attaches, "
      f"{len(kept_nodes)} new nodes, {n_refs} refs, {len(kept_names)} names")
