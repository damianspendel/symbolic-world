#!/usr/bin/env python3
"""Append a trilogy-pass batch record to pipeline/state.json, refresh the counts and set the next marker.

The result prose is read from pipeline/work/b-cw<V>-<N>_result.txt, written by the gate session; it must
contain "Mined N candidates/N refs", "+N refs", "strain:", "Fable spend:" and "quotation share" (the per-volume
share after the merge, from quote_share.py). The next marker comes from trilogy_windows.json: the next window
of the volume, the first window of the next volume in order, or the completion marker after the last.
Refuses to run twice; refuses a seed.json that carries a '[...]' elision (RULES #24).

Run from the repo root:  python3 pipeline/mining/record_trilogy.py <volume> <N> --expect NODES EDGES REFS
"""
import argparse
import datetime
import json
import re

ap = argparse.ArgumentParser()
ap.add_argument('volume')
ap.add_argument('n', type=int)
ap.add_argument('--expect', nargs=3, type=int, required=True, metavar=('NODES', 'EDGES', 'REFS'))
a = ap.parse_args()
V, N, BATCH = a.volume, a.n, f'b-cw{a.volume}-{a.n}'
PATH = 'pipeline/state.json'

tab = json.load(open('pipeline/mining/trilogy_windows.json', encoding='utf-8'))
LO, HI = tab['windows'][V][N - 1]
d = json.load(open(PATH, encoding='utf-8'))
if any(b.get('id') == BATCH for b in d['batches']):
    raise SystemExit(f'{BATCH} is already recorded')

raw = open('seed.json', encoding='utf-8').read()
assert '[...]' not in raw, "seed.json carries a '[...]' elision (RULES #24)"
seed = json.loads(raw)
nodes, edges = len(seed['nodes']), len(seed['edges'])
refs = sum(len(e.get('references', [])) for e in seed['edges'])
assert (nodes, edges, refs) == tuple(a.expect), ((nodes, edges, refs), a.expect)

RESULT = open(f'pipeline/work/{BATCH}_result.txt', encoding='utf-8').read().strip()
for needle in ('Mined ', ' candidates/', ' refs', '+', 'strain:', 'Fable spend:', 'quotation share'):
    assert needle in RESULT, f'result prose lacks {needle!r}'
assert re.search(r'Mined \d+ candidates/\d+ refs', RESULT) and re.search(r'\+\d+ refs', RESULT), 'method-page figures missing'

wins = tab['windows'][V]
if N < len(wins):
    lo, hi = wins[N]
    nxt = f'CW{V}-DUE: window {N + 1} (§{lo}-{hi})'
else:
    order = tab['order']
    i = order.index(V)
    if i + 1 < len(order):
        v2 = order[i + 1]
        lo, hi = tab['windows'][v2][0]
        nxt = f'CW{v2}-DUE: window 1 (§{lo}-{hi})'
    else:
        nxt = tab['complete_marker']

today = datetime.date.today().isoformat()
d['batches'].append({
    'id': BATCH,
    'status': 'merged (branch mining-away, unpublished)',
    'window': f'CW{V} §{LO}-{HI}',
    'result': RESULT,
})
d['updated'] = today
d['as_of'] = today
d['nodes'], d['edges'], d['refs'] = nodes, edges, refs
d['next'] = nxt
open(PATH, 'w', encoding='utf-8').write(json.dumps(d, indent=1, ensure_ascii=False) + '\n')
print(f"recorded {BATCH}; batches {len(d['batches'])}; top-level {nodes}/{edges}/{refs}; next = {nxt}")
