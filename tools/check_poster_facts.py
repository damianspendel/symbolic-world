#!/usr/bin/env python3
"""The method poster's facts are pixels; this is the check that sees them.

RULING (Damian, 2026-10-20, superseding the 2026-10-13 freeze): the poster
REGENERATES at each release/deploy with the live counts and a dated caption,
so this check compares the sidecar to live seed.json again — it passes by
construction right after a re-render and goes red the moment mining moves the
counts, which is the intended deploy blocker. On failure: re-render per
docs/figures/METHOD_POSTER_HANDOFF.md, update the sidecar, re-run.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
facts = json.load(open(ROOT / 'docs' / 'figures' / 'method_poster_facts.json'))
seed = json.load(open(ROOT / 'seed.json'))
E = seed['edges']
R = [r for e in E for r in e['references']]
fails = []

live = {'nodes': len(seed['nodes']), 'edges': len(E), 'references': len(R),
        'volumes': len({r['volume'] for r in R})}
for k, baked in facts['counts'].items():
    if live[k] != baked:
        fails.append(f'{k}: poster shows {baked}, graph has {live[k]}')

def find(s, rel, o):
    return next((e for e in E if (e['subject'], e['relation'], e['object']) == (s, rel, o)), None)

c = facts['claim']
edge = find(c['subject'], c['relation'], c['object'])
if edge is None:
    fails.append('the followed claim is no longer in the graph')
else:
    ref = next((r for r in edge['references']
                if r['volume'] == c['volume'] and r['paragraph'] == c['paragraph']), None)
    if ref is None:
        fails.append(f"the claim no longer cites CW {c['volume']} §{c['paragraph']}")
    elif c['quote'] not in ref['quote']:
        fails.append('the claim quote changed')
    elif c['crossvendor_contains'] not in str(ref.get('crossvendor_checked')):
        fails.append('the claim cross-vendor stamp changed')

for s, rel, o in facts['map_edges']:
    e = find(s, rel, o)
    if e is None:
        fails.append(f'map edge gone: {s}|{rel}|{o}')
    elif not all(r['verified'] for r in e['references']):
        fails.append(f'map edge unverified: {s}|{rel}|{o}')

if fails:
    print('POSTER FACTS: STALE — the image shows facts the graph no longer holds:')
    for f in fails:
        print('  -', f)
    print('re-render per docs/figures/METHOD_POSTER_HANDOFF.md, update '
          'docs/figures/method_poster_facts.json, re-run')
    sys.exit(1)
print(f"POSTER FACTS: ok — pixels match seed.json "
      f"({live['nodes']}/{live['edges']}/{live['references']}/{live['volumes']}, "
      f"rendered at {facts['rendered_at_commit']})")
