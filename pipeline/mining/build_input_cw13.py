#!/usr/bin/env python3
"""Build a b-cw13-N mining input (CW 13, Alchemical Studies): the trilogy second pass.

Second pass over a volume the July pipeline and the first windowed batches mined thinly (Damian, 2026-11-10: all 26 trilogy windows, RULE 4 overridden by name). The register note carries the attach rule and the trilogy reporting-and-attribution clause (PROVISIONAL until Damian's ruling). Form constraints only; names no tracked metric, so blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw13.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw13-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '13' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '13' for r in e.get('references', []))
})

doc = {
    'volume': '13',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW13 window §{LO}-{HI}. Alchemical Studies, §1-482: the commentary on The Secret of the Golden Flower (§1-84), the visions of Zosimos (§85-144), Paracelsus as a spiritual phenomenon (§145-238), the spirit Mercurius (§239-303) and the philosophical tree (§304-482). Expect many attaches onto standing nodes and edges from the first pass alongside minting where the first pass left a term unnamed. '
        'This window is a SECOND PASS over ground the graph already covers from an earlier pipeline; the existing_cw13_triples list is long and the attach rule below binds. FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, plus at most one trailing preposition. Never a clause. Hedges and modality go in the confidence field and, where essential, a short note on the reference - never inside the relation string. A candidate whose relation fails this rule will be mechanically dropped at pre-check. ATTACH RULE (hard): a claim already in the graph attaches to its standing edge ("existing_edge": true) and never repeats a quote already in the graph; a quote that stands in the graph is a self-check failure. A standing edge whose relation fits the sentence takes an attach, never a near-synonym twin. REPORTING DISCIPLINE AND ATTRIBUTION (hard) [PROVISIONAL: text pending Damian\'s ruling of 2026-11-13]: the alchemists (Dorn, Khunrath, Paracelsus, Ripley, Maier, Mylius, Zosimos, the Rosarium philosophorum, the Turba, the Aurora consurgens, the Visio Arislei and the rest), the Church Fathers, the Gnostic and Hermetic texts and any other named author or tradition are jung-quotes-source where the words are the source\'s own and jung-reports-parallel where Jung paraphrases, with the source named, however extended or sympathetic the exposition. Where a paragraph quotes or reports a source, read the sentences before and after it before choosing subject, source and claim_type. The reported claim is itself a candidate, typed to its source. Where Jung then adopts, qualifies or disputes it in his own voice, that is a separate candidate, jung-asserts, whose quote rests on Jung\'s own sentence. jung-asserts is reserved for Jung\'s own interpretive voice; a claim whose only support is the reported sentence never takes it. In doubt between asserts and reports: reports. RELATION STRENGTH (hard): analogy is not identity; a parallel, a comparison or a "corresponds to" never becomes "is"; a relation of identity is allowed only where the quoted sentence itself states it.'
    ),
    'vocabulary': vocab,
    'existing_cw13_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW13 triples")
