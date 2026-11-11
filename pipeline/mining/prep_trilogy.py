#!/usr/bin/env python3
"""Step-1 chores for a trilogy-pass window: set the IN FLIGHT marker and dump the window's paragraphs for the gate.

Refuses to run unless the marker reads "CW<V>-DUE: window <N>" and the window matches trilogy_windows.json.

Run from the repo root:  python3 pipeline/mining/prep_trilogy.py <volume> <N> [--by "the mining chat"]
"""
import argparse
import datetime
import json

ap = argparse.ArgumentParser()
ap.add_argument('volume')
ap.add_argument('n', type=int)
ap.add_argument('--by', default='the mining chat')
a = ap.parse_args()

tab = json.load(open('pipeline/mining/trilogy_windows.json', encoding='utf-8'))
LO, HI = tab['windows'][a.volume][a.n - 1]
batch = f'b-cw{a.volume}-{a.n}'
today = datetime.date.today().isoformat()
MARK = f"{batch} (§{LO}-{HI}) IN FLIGHT by {a.by} {today} — further firings stand down"

s = json.load(open('pipeline/state.json', encoding='utf-8'))
assert s['next'].startswith(f'CW{a.volume}-DUE: window {a.n} '), s['next']
s['next'] = MARK
open('pipeline/state.json', 'w', encoding='utf-8').write(json.dumps(s, indent=1, ensure_ascii=False) + '\n')

inp = json.load(open(f'pipeline/work/{batch}_input.json', encoding='utf-8'))
assert inp['window'] == f'{LO}-{HI}', (inp['window'], LO, HI)
with open(f'pipeline/work/{batch}_paras.txt', 'w', encoding='utf-8') as f:
    for p in inp['paragraphs']:
        f.write(f"=== §{p['paragraph']} ===\n{p['text']}\n\n")
print('marker set:', MARK)
print('paras written:', len(inp['paragraphs']), 'window', LO, HI)
