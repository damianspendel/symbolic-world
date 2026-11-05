#!/usr/bin/env python3
"""Build a b-cw7-N mining input (CW 7, Two Essays on Analytical Psychology).

Same shape as build_input_cw16.py. The register note carries the CW 7
reporting-discipline clause: the first essay argues cases from Freud's and
Adler's standpoints before Jung gives his own, and both essays lean on case
material and literary figures. It also carries a definitions clause, because
this is the volume in which Jung says what his core terms mean. Form
constraints only; names no tracked metric, so blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw7.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw7-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '7' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '7' for r in e.get('references', []))
})

doc = {
    'volume': '7',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW7 window §{LO}-{HI}. Two Essays on Analytical Psychology — "On the Psychology of the '
        'Unconscious" (§1-201) and "The Relations between the Ego and the Unconscious" (§202-406): '
        'psychoanalysis and the Eros theory, the will to power, the attitude-types, the personal and '
        'the collective unconscious, the synthetic method, the archetypes, the persona, anima and '
        'animus, the mana-personality, individuation. Expect attaches onto the standing nodes for '
        'these terms alongside some minting. '
        'FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, '
        'plus at most one trailing preposition. Never a clause. Hedges and modality '
        'go in the confidence field and, where essential, a short note on the '
        'reference - never inside the relation string. A candidate whose relation '
        'fails this rule will be mechanically dropped at pre-check. '
        'REPORTING DISCIPLINE (hard): Freud\'s and Adler\'s theories, and any other named author '
        'or work (Nietzsche, Goethe\'s Faust, Spitteler, Wells, Rider Haggard, ethnographic reports '
        'of primitive belief), are jung-reports-parallel with the source named, or '
        'jung-quotes-source where quoted — however extended or sympathetic the exposition, and '
        'also where Jung argues a case from Freud\'s or Adler\'s standpoint in order to test it. '
        'Patient and case material (a patient\'s dreams, fantasies and statements) is '
        'jung-quotes-source with the analysand named as the text names them (the analysand '
        'convention); Jung describing or interpreting a patient\'s material in his own voice is '
        'jung-asserts. jung-asserts is reserved for Jung\'s own interpretive voice. Where a '
        'paragraph does both, each reference takes the claim_type of the sentence its quote rests '
        'on. In doubt between asserts and reports: reports. '
        'DEFINITIONS (hard): this volume states what Jung\'s terms mean. A relation of identity '
        'or definition (is-a, is-identical-with and the like) is allowed only where the quoted '
        'sentence itself states it. A sentence that says what a thing does, resembles, tends to '
        'or is compared with takes the verb that sentence uses, never an identity.'
    ),
    'vocabulary': vocab,
    'existing_cw7_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW7 triples")
