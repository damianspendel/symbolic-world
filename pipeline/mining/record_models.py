#!/usr/bin/env python3
"""Write the exact model ids that ran a batch into its state.json record.

Added 2026-11-06 (Damian: "yes to both proposer decisions"). Until this
window the batch notes named the proposer by family at best, and b-cw11-8
ran its mining in a Haiku session with nothing in the record to show it.

Every id is read from what the run left behind, never assumed:

- proposer: the `message.model` of each assistant turn in the miner
  subagent's own transcript.
- gate: the same field in the parent session's transcript, for the turns
  after the miner's last turn. The gate, the audit launch, the merge and the
  chores all happen in that span.
- auditor: the MODEL the cross-vendor request is addressed to in
  pipeline/crossvendor_run.py. The script does not keep the model version
  the API reports back, so this is the id asked for.

A stage that ran on one model takes a string. A stage that ran on more than
one (a model switch mid-window) takes the list, in order of first use, and
the script says so on stderr. Nothing is corrected or dropped here.

The record gains one field:

    "models": {"proposer": ..., "gate": ..., "auditor": ...,
               "source": {"proposer": ..., "gate": ..., "auditor": ...}}

Refuses to run twice on a batch. Past batch records are never rewritten.

Run from the repo root, after the batch record is appended:
    python3 pipeline/mining/record_models.py b-cw16-6 --proposer-agent <agentId>
    python3 pipeline/mining/record_models.py b-cw16-6 --proposer-desc "Mine CW 16 window 6"
Add --dry-run to print the field without writing it.
"""
import argparse
import glob
import json
import os
import re
import sys

STATE = 'pipeline/state.json'
XV = 'pipeline/crossvendor_run.py'
PROJECT = os.path.expanduser('~/.claude/projects/' + os.getcwd().replace('/', '-'))


def turns(path):
    """(timestamp, model) for each assistant turn that names a real model."""
    out = []
    for line in open(path, encoding='utf-8'):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        m = (o.get('message') or {}).get('model')
        if m and not m.startswith('<'):
            out.append((o.get('timestamp') or '', m))
    return out


def distinct(models):
    seen = []
    for m in models:
        if m not in seen:
            seen.append(m)
    return seen


def value(stage, models):
    ids = distinct(models)
    if not ids:
        raise SystemExit(f'{stage}: no assistant turn names a model; nothing recorded')
    if len(ids) > 1:
        print(f'WARNING {stage} ran on more than one model: {ids}', file=sys.stderr)
        return ids
    return ids[0]


def find_agent(agent_id, desc):
    if agent_id:
        hits = glob.glob(f'{PROJECT}/*/subagents/agent-{agent_id}.jsonl')
    else:
        hits = []
        for meta in glob.glob(f'{PROJECT}/*/subagents/agent-*.meta.json'):
            if desc in json.load(open(meta, encoding='utf-8')).get('description', ''):
                hits.append(meta[:-len('.meta.json')] + '.jsonl')
        hits.sort(key=os.path.getmtime)
        hits = hits[-1:]
    if len(hits) != 1:
        raise SystemExit(f'miner transcript not found under {PROJECT} ({len(hits)} matches)')
    return hits[0]


ap = argparse.ArgumentParser()
ap.add_argument('batch')
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--proposer-agent', help="the miner subagent's agentId")
g.add_argument('--proposer-desc', help="a substring of the miner subagent's description (newest match)")
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()

d = json.load(open(STATE, encoding='utf-8'))
rec = [b for b in d['batches'] if b.get('id') == a.batch]
if not a.dry_run:
    if len(rec) != 1:
        raise SystemExit(f'{a.batch}: {len(rec)} records in {STATE}; append the batch record first')
    if 'models' in rec[0]:
        raise SystemExit(f'{a.batch} already records its models')

miner_path = find_agent(a.proposer_agent, a.proposer_desc)
miner = turns(miner_path)
agent = os.path.basename(miner_path)[len('agent-'):-len('.jsonl')]
session = os.path.basename(os.path.dirname(os.path.dirname(miner_path)))
mined_at = max(t for t, _ in miner) if miner else ''
gate = [(t, m) for t, m in turns(f'{PROJECT}/{session}.jsonl') if t > mined_at]
auditor = re.search(r'^MODEL\s*=\s*["\']([^"\']+)["\']', open(XV, encoding='utf-8').read(), re.M)
if not auditor:
    raise SystemExit(f'no MODEL constant in {XV}')

models = {
    'proposer': value('proposer', [m for _, m in miner]),
    'gate': value('gate', [m for _, m in gate]),
    'auditor': auditor.group(1),
    'source': {
        'proposer': f'miner subagent transcript agent-{agent}, {len(miner)} assistant turns',
        'gate': f'session transcript {session}, {len(gate)} assistant turns after the miner finished at {mined_at}',
        'auditor': f'request model in {XV}',
    },
}
print(json.dumps(models, indent=1, ensure_ascii=False))
if a.dry_run:
    raise SystemExit(0)
rec[0]['models'] = models
open(STATE, 'w', encoding='utf-8').write(json.dumps(d, indent=1, ensure_ascii=False) + '\n')
print(f'recorded models for {a.batch}')
