#!/usr/bin/env python3
"""Build the b-cw8-2 mining input (CW 8 §70-138).

Same shape as b-cw8-1_input.json, with one deliberate change: `vocabulary`
carries id|label|type rather than bare ids. New nodes must declare a type from
a closed set, and dedup is better informed when the miner can see what a
standing node actually is.

Run from the repo root:  python3 pipeline/work/build_input_b-cw8-2.py
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw8-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '8' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '8' for r in e.get('references', []))
})

doc = {
    'volume': '8',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW8 window §{LO}-{HI}. The Structure and Dynamics of the Psyche: archetype theory, anima, mother, rebirth, the Kore, and the spirit/trickster essays. '
        'Adjacent to the alchemical trilogy but not alchemy. Expect existing nodes '
        'to gain references (attaches) rather than every candidate minting an edge. '
        'FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, '
        'plus at most one trailing preposition. Never a clause. Hedges and modality '
        'go in the confidence field and, where essential, a short note on the '
        'reference - never inside the relation string. A candidate whose relation '
        'fails this rule will be mechanically dropped at pre-check.'
    ),
    'vocabulary': vocab,
    'existing_cw8_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW8 triples")
