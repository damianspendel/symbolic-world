#!/usr/bin/env python3
"""Build a b-cw5-N mining input (CW 5, Symbols of Transformation).

Same shape as build_input_cw11.py. The register note replaces the CW 11
exegesis clause with its CW 5 equivalent: comparative mythology on the
Miller fantasies — the reporting discipline bears on myth content, quoted
authors, and the Miller material itself (analysand convention). Form
constraints only; names no tracked metric, so blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw5.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw5-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '5' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '5' for r in e.get('references', []))
})

doc = {
    'volume': '5',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW5 window §{LO}-{HI}. Symbols of Transformation — comparative mythology on the '
        'Miller fantasies: libido, the hero, sacrifice, the mother, rebirth. Written before '
        'the archetype theory and before Jung read the alchemists; expect mythological '
        'vocabulary to mint alongside attaches onto the standing nodes (the-hero, libido, '
        'great-mother, rebirth). '
        'FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, '
        'plus at most one trailing preposition. Never a clause. Hedges and modality '
        'go in the confidence field and, where essential, a short note on the '
        'reference - never inside the relation string. A candidate whose relation '
        'fails this rule will be mechanically dropped at pre-check. '
        'REPORTING DISCIPLINE (hard): this volume amplifies myths and quotes sources at '
        'length. The content of a myth, saga, scripture or named author is '
        'jung-reports-parallel (or jung-quotes-source with the source named) — however '
        'extended or sympathetic the retelling. Miss Miller\'s fantasy material is '
        'jung-quotes-source with Miller named (the analysand convention). jung-asserts is '
        'reserved for Jung\'s own interpretive voice, typically about the psyche. Where a '
        'paragraph does both, each reference takes the claim_type of the sentence its '
        'quote rests on. In doubt between asserts and reports: reports.'
    ),
    'vocabulary': vocab,
    'existing_cw5_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW5 triples")
