#!/usr/bin/env python3
"""Build a b-cw6-N mining input (CW 6, Psychological Types, chapters X and XI only).

Same shape as build_input_cw16.py. Only two chapters of the volume are in the
corpus: X, the general description of the types (§556-671), and XI, the
Definitions (§672-844). The register note carries the CW 6 reporting-discipline
clause (the Definitions cite, adopt and dispute other authors' usage), a
type-descriptions clause and the definitions clause shared with CW 7. Form
constraints only; names no tracked metric, so blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw6.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw6-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '6' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '6' for r in e.get('references', []))
})

doc = {
    'volume': '6',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW6 window §{LO}-{HI}. Psychological Types, chapters X and XI — the general description '
        'of the types (§556-671: the extraverted and the introverted attitude, the four functions '
        'in each, the eight types, the principal and auxiliary functions) and the Definitions '
        '(§672-844: Jung\'s own glossary of his terms, in alphabetical order). Expect attaches onto '
        'the standing nodes for the attitudes, the functions and the defined terms alongside '
        'minting for the types. '
        'FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, '
        'plus at most one trailing preposition. Never a clause. Hedges and modality '
        'go in the confidence field and, where essential, a short note on the '
        'reference - never inside the relation string. A candidate whose relation '
        'fails this rule will be mechanically dropped at pre-check. '
        'REPORTING DISCIPLINE (hard): where a description or a definition cites, adopts or '
        'disputes another author\'s usage (Kant, Schopenhauer, Schiller, Wundt, Lévy-Bruhl, Freud, '
        'Adler, Bleuler and others), that usage is jung-reports-parallel with the source named, or '
        'jung-quotes-source where quoted — however sympathetic. A term Jung takes over from an '
        'author stays a report of that author unless the quoted sentence gives Jung\'s own '
        'definition. jung-asserts is reserved for Jung\'s own descriptive and defining voice. '
        'Where a paragraph does both, each reference takes the claim_type of the sentence its '
        'quote rests on. In doubt between asserts and reports: reports. '
        'TYPE DESCRIPTIONS (hard): a statement about a type holds of that type, not of the '
        'function or the attitude in general and not of people in general; the subject is the '
        'type, or the function in that attitude, as the text names it. A general tendency ("as a '
        'rule", "often", "in extreme cases") takes medium or low confidence. '
        'DEFINITIONS (hard): a relation of identity or definition (is-a, is-identical-with and '
        'the like) is allowed only where the quoted sentence itself states it. A sentence that '
        'says what a thing does, resembles, tends to or is compared with takes the verb that '
        'sentence uses, never an identity. Where an entry distinguishes two terms, the relation '
        'says they are distinguished.'
    ),
    'vocabulary': vocab,
    'existing_cw6_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW6 triples")
