#!/usr/bin/env python3
"""Derive every graph figure the v2.0 paper may state, from seed.json and the
committed declarations. Nothing typed. Output is the fact sheet handed to the
cross-vendor reviewer and the source the paper's numbers must match.

    python3 tools/paper_review/graph_facts.py > docs/experiments/paper_v2_reviews/graph_facts.json
"""
import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
seed = json.load(open(ROOT / 'seed.json'))
decl = json.load(open(ROOT / 'pipeline' / 'family' / 'relation_declarations.json'))
E = seed['edges']
R = [r for e in E for r in e['references']]
fam = [e['relation_family'] for e in E]

facts = {
    'nodes': len(seed['nodes']),
    'edges': len(E),
    'references': len(R),
    'references_attested_verified_true': sum(1 for r in R if r.get('verified') is True),
    'references_verified_by': dict(collections.Counter(r['verified_by'] for r in R)),
    'references_crossvendor_checked': sum(1 for r in R if r.get('crossvendor_checked')),
    'references_claim_type': dict(collections.Counter(r['claim_type'] for r in R)),
    'references_confidence': dict(collections.Counter(r['confidence'] for r in R)),
    'references_modality_swept': sum(1 for r in R if r.get('modality_swept')),
    'edges_with_relation_normalized': sum(1 for e in E if 'relation_normalized' in e),
    'family_state': dict(collections.Counter(f.get('state') for f in fam)),
    'family_by_human_adjudication_exact': sum(1 for f in fam if f.get('by') == 'human-adjudication'),
    'family_by_contains_human': sum(1 for f in fam if 'human' in str(f.get('by', ''))),
    'family_pending_on_arms_disagree': sum(1 for f in fam if f.get('by') == 'arms-disagree'),
    'declarations_active': len(decl.get('active', [])),
    'declarations_awaiting_ruling': len(decl.get('candidates_awaiting_ruling', [])),
    'gold_set_references_human_reviewed': 50,   # E10, pipeline/gold_sample_50.json
    'proposer_recorded_per_reference': False,   # proposer model is a batch-level ledger fact, not a reference field
}
N = [e for e in E if 'relation_normalized' in e]
facts['normalized_edges_all_refs_crossvendor_checked'] = sum(
    1 for e in N if all(r.get('crossvendor_checked') for r in e['references']))
gold = ROOT / 'pipeline' / 'gold_sample_50.json'
if gold.exists():
    g = json.load(open(gold))
    facts['gold_set_references_human_reviewed'] = len(g) if isinstance(g, list) else len(g.get('items', g))
print(json.dumps(facts, indent=2))
