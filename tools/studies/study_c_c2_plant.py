#!/usr/bin/env python3
"""Study C, part C2 — plant the normalization corruptions.

40 stored normalizations corrupted in copies (10 modality dropped, 10 scope
dropped, 10 direction reversed, 10 verb strengthened past the verbatim claim)
plus 40 untouched, shuffled. The Fable entailment gate then re-judges each
candidate against the frozen verbatim relation and its quote.

    python3 tools/studies/study_c_c2_plant.py

Writes pipeline/work/study_c/c2_items.json (what the gate sees; no answers)
and pipeline/work/study_c/c2_truth.json (the key). Both gitignored. seed.json
is never written — every corruption lives in a copy. The plant seed is stamped
into both artifacts (RULES #13).
"""
import copy
import json
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from study_c_lib import (  # noqa: E402
    PLANT_SEED, STRENGTHENED_VERB, WORK, first_reference, is_identity,
    is_symmetric, load_population,
)

CLASSES = ('modality_dropped', 'scope_dropped', 'direction_reversed',
           'verb_strengthened')
PER_CLASS = 10
CLEAN = 40


def eligible(item, cls):
    """Pre-set eligibility, fixed before the draw: a corruption that would not
    change the claim is not a corruption."""
    norm = item['edge']['relation_normalized']
    quals = norm.get('qualifiers') or {}
    if cls == 'modality_dropped':
        return bool(quals.get('modality'))
    if cls == 'scope_dropped':
        return bool(quals.get('scope'))
    if cls == 'direction_reversed':
        return not is_symmetric(norm.get('relation'))
    if cls == 'verb_strengthened':
        return not is_identity(norm.get('relation'))
    raise ValueError(cls)


def candidate(item, cls=None):
    """The normalization as the gate sees it, corrupted or not."""
    edge = item['edge']
    norm = copy.deepcopy(edge['relation_normalized'])
    quals = norm.get('qualifiers') or {}
    subject, obj = edge['subject'], edge['object']
    relation = norm.get('relation')

    if cls == 'modality_dropped':
        quals['modality'] = None
    elif cls == 'scope_dropped':
        quals['scope'] = None
    elif cls == 'direction_reversed':
        subject, obj = obj, subject
    elif cls == 'verb_strengthened':
        relation = STRENGTHENED_VERB

    return {
        'candidate_subject': subject,
        'candidate_relation': relation,
        'candidate_object': obj,
        'candidate_qualifiers': {k: quals.get(k) for k in
                                 ('carrier', 'scope', 'condition', 'modality', 'note')},
    }


def main():
    population = load_population()
    rng = random.Random(PLANT_SEED)

    pools = {cls: [p for p in population if eligible(p, cls)] for cls in CLASSES}
    for cls, pool in pools.items():
        print(f"{cls}: {len(pool)} eligible")
        if len(pool) < PER_CLASS:
            print(f"HOLD: pool for {cls} is smaller than {PER_CLASS}", file=sys.stderr)
            return 1

    taken, planted = set(), []
    for cls in CLASSES:
        pool = [p for p in pools[cls] if p['idx'] not in taken]
        pool.sort(key=lambda p: p['idx'])
        chosen = rng.sample(pool, PER_CLASS)
        for item in chosen:
            taken.add(item['idx'])
            planted.append((item, cls))

    rest = sorted([p for p in population if p['idx'] not in taken],
                  key=lambda p: p['idx'])
    clean = rng.sample(rest, CLEAN)
    rows = planted + [(item, None) for item in clean]
    rng.shuffle(rows)

    items, truth = [], []
    for position, (item, cls) in enumerate(rows, start=1):
        edge, ref = item['edge'], first_reference(item['edge'])
        row = {
            'n': position,
            'subject': edge['subject'],
            'relation_verbatim': edge['relation'],
            'object': edge['object'],
            'quote': ref['quote'],
            'citation': f"CW {ref['volume']} §{ref['paragraph']}",
            'claim_type': ref.get('claim_type'),
            'confidence': ref.get('confidence'),
        }
        row.update(candidate(item, cls))
        items.append(row)
        truth.append({'n': position, 'idx': item['idx'], 'key': item['key'],
                      'corruption': cls or 'clean'})

    WORK.mkdir(parents=True, exist_ok=True)
    json.dump({'plant_seed': PLANT_SEED, 'items': items},
              open(WORK / 'c2_items.json', 'w'), indent=1, ensure_ascii=False)
    json.dump({'plant_seed': PLANT_SEED, 'truth': truth},
              open(WORK / 'c2_truth.json', 'w'), indent=1, ensure_ascii=False)
    print(f"planted {len(planted)} corruptions + {len(clean)} clean = {len(items)} items"
          f" (seed {PLANT_SEED})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
