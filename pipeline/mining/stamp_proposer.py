#!/usr/bin/env python3
"""Write the miner's exact model id into its candidates file (concordance field 7, Damian 2026-11-11).

The id is read from the miner subagent's own transcript, the way record_models.py reads it, never typed in.
The pre-check copies the field into the prechecked file; the batch record carries it again through
record_models.py, so the candidates file and the record agree.

Run from the repo root, after the miner has written the candidates file:
    python3 pipeline/mining/stamp_proposer.py b-cw14-1 --proposer-agent <agentId>
"""
import argparse
import glob
import json
import os

PROJECT = os.path.expanduser('~/.claude/projects/' + os.getcwd().replace('/', '-'))

ap = argparse.ArgumentParser()
ap.add_argument('batch')
ap.add_argument('--proposer-agent', required=True)
a = ap.parse_args()

hits = glob.glob(f'{PROJECT}/*/subagents/agent-{a.proposer_agent}.jsonl')
if len(hits) != 1:
    raise SystemExit(f'miner transcript not found under {PROJECT} ({len(hits)} matches)')
models = []
for line in open(hits[0], encoding='utf-8'):
    try:
        o = json.loads(line)
    except ValueError:
        continue
    m = (o.get('message') or {}).get('model')
    if m and not m.startswith('<') and m not in models:
        models.append(m)
if not models:
    raise SystemExit('no assistant turn in the miner transcript names a model')

path = f'pipeline/work/{a.batch}_candidates.json'
c = json.load(open(path, encoding='utf-8'))
c['proposer_model'] = models[0] if len(models) == 1 else models
c['proposer_source'] = f'miner subagent transcript agent-{a.proposer_agent}'
json.dump(c, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'{path}: proposer_model = {c["proposer_model"]}')
