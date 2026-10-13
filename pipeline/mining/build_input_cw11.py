#!/usr/bin/env python3
"""Build a b-cw11-N mining input (CW 11, Psychology and Religion: West and East).

Same shape as build_input_cw8.py. One deliberate addition, from the Gemini
cross-vendor review recorded in docs/PROPOSAL_NEXT_ARC.md: the EXEGESIS
CLAUSE, a form constraint distinguishing Jung reporting doctrine from Jung
asserting it. The reviewer, who runs this pipeline's audits, reports
authorial-endorsement hallucination as the dominant failure mode in
religious text. A form constraint names no tracked metric, so the miner
blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw11.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw11-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '11' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '11' for r in e.get('references', []))
})

doc = {
    'volume': '11',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW11 window §{LO}-{HI}. Psychology and Religion: West and East — the Trinity, '
        'the Mass, Job, and the Eastern material (Tibetan Book of the Dead, yoga, Zen). '
        'Doctrinal-theological register: expect new theological vocabulary to mint '
        'alongside attaches onto the standing religious nodes (christ, the-self, '
        'quaternity, god-image). '
        'FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, '
        'plus at most one trailing preposition. Never a clause. Hedges and modality '
        'go in the confidence field and, where essential, a short note on the '
        'reference - never inside the relation string. A candidate whose relation '
        'fails this rule will be mechanically dropped at pre-check. '
        'EXEGESIS CLAUSE (hard): this volume is Jung writing ABOUT religious doctrine. '
        'Distinguish Jung REPORTING a doctrine from Jung ASSERTING a claim of his own. '
        'When a paragraph expounds what a dogma, scripture, liturgy, rite, tradition or '
        'named author holds, the claim_type is jung-reports-parallel (or '
        'jung-quotes-source with the source named) — even where the exposition is '
        'extended, sympathetic, and carries no distancing phrase. Length and sympathy '
        'of exposition are not endorsement. jung-asserts is reserved for sentences '
        'where Jung speaks in his own interpretive voice, typically about the psyche. '
        'Where a paragraph does both, each reference takes the claim_type of the '
        'sentence its quote rests on. In doubt between asserts and reports: reports.'
    ),
    'vocabulary': vocab,
    'existing_cw11_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW11 triples")
