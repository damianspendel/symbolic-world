#!/usr/bin/env python3
"""Build a b-cw16-N mining input (CW 16, The Practice of Psychotherapy).

Same shape as build_input_cw11.py. The register note carries the CW 16
equivalent of the exegesis clause: the clinical volume quotes the Rosarium
Philosophorum and case material — alchemical source text is quoted source,
patient material follows the analysand convention. Form constraints only;
names no tracked metric, so blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw16.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw16-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '16' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '16' for r in e.get('references', []))
})

doc = {
    'volume': '16',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW16 window §{LO}-{HI}. The Practice of Psychotherapy — the clinical volume: '
        'principles of practical psychotherapy, abreaction, dream analysis in treatment, '
        'and the Psychology of the Transference (Jung\'s commentary on the Rosarium '
        'Philosophorum). Expect attaches onto the standing clinical and alchemical nodes '
        '(transference, coniunctio, hierosgamos) alongside clinical minting. '
        'FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, '
        'plus at most one trailing preposition. Never a clause. Hedges and modality '
        'go in the confidence field and, where essential, a short note on the '
        'reference - never inside the relation string. A candidate whose relation '
        'fails this rule will be mechanically dropped at pre-check. '
        'REPORTING DISCIPLINE (hard): the Rosarium text, other alchemical sources and '
        'any named author are jung-quotes-source with the source named (or '
        'jung-reports-parallel where reported without quotation) — however extended or '
        'sympathetic the exposition. Patient and case material is jung-quotes-source '
        'with the analysand named (the analysand convention); Jung describing a '
        'patient\'s material in his own interpretive voice is jung-asserts. jung-asserts '
        'is reserved for Jung\'s own interpretive voice. Where a paragraph does both, '
        'each reference takes the claim_type of the sentence its quote rests on. In '
        'doubt between asserts and reports: reports.'
    ),
    'vocabulary': vocab,
    'existing_cw16_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW16 triples")
