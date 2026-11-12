#!/usr/bin/env python3
"""Merge a trilogy-pass window into seed.json from its receipts and the gate session's adjudication file.

Receipts (all in pipeline/work): b-cw<V>-<N>_prechecked.json, _gate.json (verdicts: subject, relation, object,
paragraph, verdict TRUE|CORRECTED|FALSE, corrections, reason), _crossvendor.json (results: PASS|FINDING), and
_adjudication.json written by the gate session after reading the auditor's findings:

    {"before": [nodes, edges, refs],
     "correct_claimtype": {"subject|relation|object|paragraph": "jung-asserts", ...},
     "correct_confidence": {"...": "medium"},
     "upheld_notes": {"...": "cross-vendor finding overruled: ..."},
     "substantive": ["..."],
     "correct_relation": {"...": "belongs-to"},
     "labels": {"node-id": "Label the gate set"},
     "names_reject": ["node|paragraph", ...]}

Rules as in every merge since b-cw9i-8: gate FALSE drops; a FINDING is applied as a claim-type or confidence
correction, a relation correction (the auditor's reading of the relation string, applied with a note), overruled
with an audit note, or dropped as substantive (the auditor is the tiebreaker); an
unadjudicated FINDING stops the merge. The 2026-11-11 fields ride along: source_author and source_text on the
reference, cross_register on the edge (with the batch that set it), and the names list onto the nodes (latin
where the node has none, aliases appended, name_refs recording volume, paragraph and batch).

Run from the repo root:  python3 pipeline/mining/merge_trilogy.py <volume> <N> [--dry-run]
"""
import argparse
import json
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument('volume')
ap.add_argument('n', type=int)
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()
V, BATCH = a.volume, f'b-cw{a.volume}-{a.n}'
DATE = subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()
W = 'pipeline/work/'

pre = json.load(open(W + f'{BATCH}_prechecked.json', encoding='utf-8'))
gate = json.load(open(W + f'{BATCH}_gate.json', encoding='utf-8'))
xv = json.load(open(W + f'{BATCH}_crossvendor.json', encoding='utf-8'))
adj = json.load(open(W + f'{BATCH}_adjudication.json', encoding='utf-8'))


def k4(s):
    p = s.split('|')
    return (p[0], p[1], p[2], int(p[3]))


gate_v = {(v['subject'], v['relation'], v['object'], v['paragraph']): v for v in gate['verdicts']}
xv_v = {(v['subject'], v['relation'], v['object'], v['paragraph']): v for v in xv['results']}
CORRECT_CLAIMTYPE = {k4(k): v for k, v in adj.get('correct_claimtype', {}).items()}
CORRECT_CONFIDENCE = {k4(k): v for k, v in adj.get('correct_confidence', {}).items()}
UPHELD_NOTES = {k4(k): v for k, v in adj.get('upheld_notes', {}).items()}
SUBSTANTIVE = {k4(k) for k in adj.get('substantive', [])}
CORRECT_RELATION = {k4(k): v for k, v in adj.get('correct_relation', {}).items()}
LABELS = adj.get('labels', {})
NAMES_REJECT = {(p.split('|')[0], int(p.split('|')[1])) for p in adj.get('names_reject', [])}
REF_CORRECTIONS = ('claim_type', 'confidence', 'source', 'source_author', 'source_text', 'note')

seed = json.load(open('seed.json', encoding='utf-8'))
before = (len(seed['nodes']), len(seed['edges']), sum(len(e.get('references', [])) for e in seed['edges']))
assert list(before) == list(adj['before']), f"seed.json moved since orientation: {before} != {adj['before']}"
if any(BATCH in str(r.get('crossvendor_checked', '')) and DATE in str(r.get('crossvendor_checked', '')) for e in seed['edges'] for r in e.get('references', [])):
    raise SystemExit(f'seed.json already carries {BATCH} audit tags: {BATCH} looks merged')
node_by_id = {n['id']: n for n in seed['nodes']}
index = {(e['subject'], e['relation'], e['object']): e for e in seed['edges']}
standing = set(index)

kept, dropped = [], []
for kind in ('candidates', 'attaches'):
    for ed in pre[kind]:
        for r in ed['references']:
            k = (ed['subject'], ed['relation'], ed['object'], r['paragraph'])
            g = gate_v.get(k)
            if g is None:
                raise SystemExit(f'no gate verdict for {k}')
            if g['verdict'] == 'FALSE':
                dropped.append((k, 'gate FALSE: ' + g['reason']))
                continue
            subj, rel, obj = ed['subject'], ed['relation'], ed['object']
            ref = dict(r)
            note = None
            if g['verdict'] == 'CORRECTED':
                c = g.get('corrections') or {}
                rel = c.get('relation', rel)
                for f in REF_CORRECTIONS:
                    if f in c:
                        ref[f] = c[f]
                if c.get('claim_type') == 'jung-asserts':
                    for f in ('source', 'source_author', 'source_text'):
                        ref.pop(f, None)
                subj = c.get('subject', subj)
                obj = c.get('object', obj)
                note = 'gate correction: ' + g['reason']
            xk = (subj, rel, obj, r['paragraph'])
            x = xv_v.get(xk) or xv_v.get(k)
            if x is None:
                raise SystemExit(f'no cross-vendor verdict for {xk}')
            if x['verdict'] == 'FINDING':
                if xk in CORRECT_CLAIMTYPE:
                    ref['claim_type'] = CORRECT_CLAIMTYPE[xk]
                    if ref['claim_type'] == 'jung-asserts':
                        for f in ('source', 'source_author', 'source_text'):
                            ref.pop(f, None)
                    ref['correction_note'] = 'cross-vendor correction: ' + (x['reason'] or '')
                elif xk in CORRECT_CONFIDENCE:
                    ref['confidence'] = CORRECT_CONFIDENCE[xk]
                    ref['correction_note'] = 'cross-vendor correction: ' + (x['reason'] or '')
                elif xk in UPHELD_NOTES:
                    ref['audit_note'] = UPHELD_NOTES[xk]
                elif xk in CORRECT_RELATION:
                    ref['correction_note'] = 'cross-vendor correction (relation): ' + (x['reason'] or '')
                    rel = CORRECT_RELATION[xk]
                elif xk in SUBSTANTIVE:
                    dropped.append((xk, 'xv FINDING (substantive): ' + (x['reason'] or '')))
                    continue
                else:
                    raise SystemExit(f'unadjudicated cross-vendor finding: {xk}')
            if note:
                ref['correction_note'] = (ref.get('correction_note', '') + ' | ' + note).strip(' |')
            kept.append(((subj, rel, obj), ref, x['verdict'], ed.get('cross_register') is True))

names = [nm for nm in pre.get('names', []) if (nm['node'], nm['paragraph']) not in NAMES_REJECT]
used = {i for (k, _, _, _) in kept for i in (k[0], k[2])} | {nm['node'] for nm in names}
added_nodes = []
for n in pre['new_nodes']:
    if n['id'] in used and n['id'] not in node_by_id:
        node = {'id': n['id'], 'label': LABELS.get(n['id'], n['label']), 'type': n['type']}
        seed['nodes'].append(node)
        node_by_id[n['id']] = node
        added_nodes.append(n['id'])
stranded = sorted({n['id'] for n in pre['new_nodes'] if n['id'] not in used})

new_edges = attached_standing = attached_own = flagged = 0
for key, r, xvv, flag in kept:
    ref = {
        'volume': V,
        'paragraph': r['paragraph'],
        'quote': r['quote'],
        'claim_type': r['claim_type'],
        'confidence': r['confidence'],
        'verified': True,
        'verified_by': 'claude-fable-5',
        'verified_date': DATE,
        'crossvendor_checked': f"gemini-3.1-pro (pre-merge, {BATCH}, {'PASS' if xvv == 'PASS' else 'FINDING-adjudicated'}, {DATE})",
    }
    for f in ('source', 'source_author', 'source_text', 'correction_note', 'audit_note', 'note'):
        if r.get(f):
            ref[f] = r[f]
    if key in index:
        edge = index[key]
        edge['references'].append(ref)
        if key in standing:
            attached_standing += 1
        else:
            attached_own += 1
    else:
        edge = {'subject': key[0], 'relation': key[1], 'object': key[2], 'references': [ref]}
        seed['edges'].append(edge)
        index[key] = edge
        new_edges += 1
    if flag and not edge.get('cross_register'):
        edge['cross_register'] = {'value': True, 'by': f'proposer, {BATCH}', 'date': DATE}
        flagged += 1

named = []
for nm in names:
    node = node_by_id.get(nm['node'])
    if node is None:
        raise SystemExit(f"names entry for a node that is not in the graph: {nm}")
    if nm.get('latin') and not node.get('latin'):
        node['latin'] = nm['latin']
    if nm.get('aliases'):
        node['aliases'] = sorted(set(node.get('aliases', [])) | set(nm['aliases']))
    node.setdefault('name_refs', []).append({'volume': V, 'paragraph': nm['paragraph'], 'batch': BATCH})
    named.append(nm['node'])

after = (len(seed['nodes']), len(seed['edges']), sum(len(e.get('references', [])) for e in seed['edges']))
if not a.dry_run:
    json.dump(seed, open('seed.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open('seed.json', 'a', encoding='utf-8').write('\n')
print(('DRY RUN ' if a.dry_run else '') + f"nodes {before[0]} -> {after[0]} (+{len(added_nodes)}): {added_nodes}")
print(f"stranded new_nodes not added: {stranded}")
print(f"edges {before[1]} -> {after[1]} (+{new_edges} new; {attached_standing} refs attached to standing edges, "
      f"{attached_own} further refs on this window's new edges); cross_register set on {flagged} edges")
print(f"refs  {before[2]} -> {after[2]} (+{after[2] - before[2]})")
print(f"names applied: {len(named)} on {sorted(set(named))}")
print(f"dropped {len(dropped)}:")
for k, why in dropped:
    print(f"  - {k[0]} -{k[1]}-> {k[2]} §{k[3]}: {why}")
