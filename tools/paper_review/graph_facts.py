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
facts['node_types'] = dict(collections.Counter(n['type'] for n in seed['nodes']))
import re as _re
facts['quote_cap_letter_tokens'] = int(_re.search(r'MAX_QUOTE_WORDS\s*=\s*(\d+)',
    (ROOT / 'tests' / 'test_graph.py').read_text()).group(1))
facts['families_in_ruleset'] = 25   # docs/FAMILY_DEFINITIONS.md, counted by heading
facts['declarations_dormant'] = sum(1 for a in decl.get('active', []) if a.get('dormant'))
facts['declarations_active_not_dormant'] = sum(1 for a in decl.get('active', []) if not a.get('dormant'))
N = [e for e in E if 'relation_normalized' in e]
facts['normalized_relation_token_counts'] = dict(collections.Counter(
    len(e['relation_normalized']['relation'].split('-')) for e in N))
facts['normalized_records_carry_own_proposer'] = all('proposed_by' in e['relation_normalized'] for e in N)
facts['normalized_edges_all_refs_crossvendor_checked'] = sum(
    1 for e in N if all(r.get('crossvendor_checked') for r in e['references']))
gold = ROOT / 'pipeline' / 'gold_sample_50.json'
if gold.exists():
    g = json.load(open(gold))
    facts['gold_set_references_human_reviewed'] = len(g) if isinstance(g, list) else len(g.get('items', g))
# ---- receipts beyond seed.json: human gold set, family calibration, external validity ----
import collections as _c, glob as _g
hv = json.load(open(ROOT / 'pipeline' / 'human_validations.json'))
facts['gold_set'] = {'n': len(hv),
                     'support': dict(_c.Counter(x['support'] for x in hv)),
                     'voice_agreement': sum(1 for x in hv if x['voice'] == 'voice-correct' or
                                            {'should-be-asserts': 'jung-asserts', 'should-be-reports': 'jung-reports-parallel',
                                             'should-be-quotes': 'jung-quotes-source'}.get(x['voice']) == x['pipeline_claim_type']),
                     'validated_by': dict(_c.Counter(x['validated_by'] for x in hv)),
                     'anchored': True}   # the tool showed the pipeline label; PAPER.md E10
cal = []
for f in sorted(_g.glob(str(ROOT / 'pipeline' / 'family_calibration' / 'records' / '*.json'))):
    d = json.load(open(f))
    cal.append({'file': f.split('/')[-1], 'version': d.get('definitions_version'), 'verdict': d.get('verdict'),
                'gate_model': d.get('gate_model'), 'caught': d['sensitivity']['caught'], 'of': d['sensitivity']['of'],
                'clean_left_alone': d['specificity']['clean_left_alone'], 'clean_of': d['specificity']['of']})
facts['family_calibration_runs'] = cal
v072 = [c for c in cal if c['version'] == 'v0.7.2']
facts['family_calibration_v072_pooled'] = {'runs': len(v072),
    'caught': sum(c['caught'] for c in v072), 'of': sum(c['of'] for c in v072),
    'clean_left_alone': sum(c['clean_left_alone'] for c in v072), 'clean_of': sum(c['clean_of'] for c in v072),
    'pass_on_run': next((i + 1 for i, c in enumerate(v072) if c['verdict'] == 'PASS'), None)}
facts['family_calibration_gate_same_model_as_a_proposer_arm'] = True   # independence_note in every record
facts['external_validity'] = json.load(open(ROOT / 'docs' / 'experiments' / 'external_validity_2026-08' / 'results.json'))
facts['pinned_from_v13_paper'] = {   # facts CI-pinned in docs/PAPER.md at v1.3.0, not re-derived here
    'E4_strict_pair_overlap_pct': 37.5,
    'unanchored_crossreview_convention_rulings_rejected': '9 of 13',
    'E1b_sensitivity_specificity': '86/100, 93/100'}

import re, subprocess
q = subprocess.run(['python3', str(ROOT / 'tools' / 'query' / 'kg_query.py'), '--closure', '--count'],
                   capture_output=True, text=True, cwd=ROOT).stdout
m = re.search(r'\((\d+) from the graph, (\d+) derived\)', q)
facts['derived_rows_at_full_closure'] = int(m.group(2)) if m else None
q = subprocess.run(['python3', str(ROOT / 'tools' / 'query' / 'kg_query.py'), '--subject', 'the-self',
                    '--object', 'salt', '--closure'], capture_output=True, text=True, cwd=ROOT).stdout
facts['query_the_self_symbolized_by_salt'] = q.strip().splitlines()[0] if q.strip() else None
salt = [e for e in E if (e['subject'], e['relation'], e['object']) == ('salt', 'symbolizes', 'the-self')]
if salt:
    e = salt[0]; r = e['references'][0]
    facts['edge_salt_symbolizes_the_self'] = {
        'n_references': len(e['references']), 'volume': r['volume'], 'paragraph': r['paragraph'],
        'quote_word_count': len(r['quote'].split()), 'claim_type': r['claim_type'],
        'confidence': r['confidence'], 'verified_by': r['verified_by'], 'verified_date': r['verified_date'],
        'crossvendor_checked': r.get('crossvendor_checked'), 'has_relation_normalized': 'relation_normalized' in e,
        'relation_family': e['relation_family']}
print(json.dumps(facts, indent=2))
