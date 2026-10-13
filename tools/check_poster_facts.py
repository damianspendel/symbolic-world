#!/usr/bin/env python3
"""The method poster's facts are pixels; this is the check that sees them.

RULING (Damian, 2026-10-13): the poster is the v2.0 release artifact its own
caption claims ("Counts as of v2.0, August 2026"). With mining reopened, the
live counts move with every merged window, so the counts check pins to the
frozen v2.0.0 release — the pattern that pins paper facts to their tag —
rather than to live seed.json, and the poster re-renders at the next release
ceremony, not per merge. The claim and map-edge checks still run against the
live graph: the poster may show v2.0 counts, but it must never cite a claim
the graph no longer holds. Run by preflight. On failure: re-render per
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

# The frozen v2.0.0 release the poster depicts (tag 6cfcd36, 2026-09-05).
V2_FROZEN = {'nodes': 589, 'edges': 2091, 'references': 2678, 'volumes': 9}
for k, baked in facts['counts'].items():
    if V2_FROZEN[k] != baked:
        fails.append(f"{k}: poster shows {baked}, the v2.0.0 release it claims to depict had {V2_FROZEN[k]}")

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
print(f"POSTER FACTS: ok — the render is the v2.0.0 artifact its caption claims "
      f"({V2_FROZEN['nodes']}/{V2_FROZEN['edges']}/{V2_FROZEN['references']}, "
      f"rendered at {facts['rendered_at_commit']}); its claim and map edges are in the live graph")
