#!/usr/bin/env python3
"""Study C, part C1 — the mechanical comparison of the two normalization arms.

Runs the pre-set verb rule over every item both arms have answered, and writes
the remainder — the pairs no mechanical rule settles — as the input a Fable
model judges same-relation / different-relation on, with a reason.

    python3 tools/studies/study_c_compare.py

Writes docs/experiments/study_c/c1_mechanical.json (committed receipt) and
pipeline/work/study_c/c1_remainder_input.json (gitignored working file).
No arm is ground truth; disagreement is the finding, not an error.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from study_c_lib import (  # noqa: E402
    DOCS, QUALIFIER_KEYS, WORK, first_reference, load_population,
    qualifier_coverage, qualifier_presence, read_jsonl, verb_agreement,
)


def main():
    population = {p['idx']: p for p in load_population()}
    arm2 = read_jsonl(DOCS / 'arm2.jsonl')
    if not arm2:
        print("nothing to compare: arm2.jsonl is empty", file=sys.stderr)
        return 1

    rows, remainder = [], []
    for rec in sorted(arm2, key=lambda r: r['idx']):
        item = population[rec['idx']]
        edge = item['edge']
        stored = edge['relation_normalized']
        verbatim = edge['relation']

        agreement = verb_agreement(stored.get('relation'), rec.get('relation'))
        row = {
            'idx': rec['idx'],
            'key': item['key'],
            'subject': edge['subject'],
            'relation_verbatim': verbatim,
            'object': edge['object'],
            'arm1_relation': stored.get('relation'),
            'arm2_relation': rec.get('relation'),
            'arm2_verdict': rec.get('verdict'),
            'verb_agreement': agreement,
            'arm1_qualifiers_present': qualifier_presence(stored.get('qualifiers')),
            'arm2_qualifiers_present': qualifier_presence(rec.get('qualifiers')),
            'arm1_dropped_coverage': qualifier_coverage(
                verbatim, stored.get('relation'), stored.get('qualifiers')),
            'arm2_dropped_coverage': qualifier_coverage(
                verbatim, rec.get('relation'), rec.get('qualifiers')),
        }
        rows.append(row)

        if agreement == 'REMAINDER':
            ref = first_reference(edge)
            remainder.append({
                'n': rec['idx'],
                'subject': edge['subject'],
                'relation_verbatim': verbatim,
                'object': edge['object'],
                'quote': ref['quote'],
                'citation': f"CW {ref['volume']} §{ref['paragraph']}",
                'arm_a': {'relation': stored.get('relation'),
                          'qualifiers': {k: (stored.get('qualifiers') or {}).get(k)
                                         for k in QUALIFIER_KEYS}},
                'arm_b': {'relation': rec.get('relation'),
                          'qualifiers': {k: (rec.get('qualifiers') or {}).get(k)
                                         for k in QUALIFIER_KEYS}},
            })

    counts = {}
    for row in rows:
        counts[row['verb_agreement']] = counts.get(row['verb_agreement'], 0) + 1

    presence = {}
    for arm in ('arm1', 'arm2'):
        presence[arm] = {
            k: sum(1 for r in rows if r[f'{arm}_qualifiers_present'][k])
            for k in QUALIFIER_KEYS
        }

    def mean_coverage(arm):
        vals = [r[f'{arm}_dropped_coverage'] for r in rows
                if r[f'{arm}_dropped_coverage'] is not None]
        return (round(sum(vals) / len(vals), 4), len(vals)) if vals else (None, 0)

    summary = {
        'items_compared': len(rows),
        'verb_agreement_counts': counts,
        'mechanical_agreement_rate': round(
            (counts.get('EXACT', 0) + counts.get('INFLECTION', 0)) / len(rows), 4),
        'qualifier_presence_counts': presence,
        'dropped_material_coverage_mean': {
            'arm1': mean_coverage('arm1'), 'arm2': mean_coverage('arm2')},
        'arm2_verdicts': {v: sum(1 for r in rows if r['arm2_verdict'] == v)
                          for v in sorted({r['arm2_verdict'] for r in rows})},
        'remainder_for_fable': len(remainder),
    }

    DOCS.mkdir(parents=True, exist_ok=True)
    json.dump({'summary': summary, 'rows': rows},
              open(DOCS / 'c1_mechanical.json', 'w'), indent=1, ensure_ascii=False)
    WORK.mkdir(parents=True, exist_ok=True)
    json.dump(remainder, open(WORK / 'c1_remainder_input.json', 'w'),
              indent=1, ensure_ascii=False)

    print(json.dumps(summary, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
