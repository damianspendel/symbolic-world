#!/usr/bin/env python3
"""Build a b-cw14-N mining input (CW 14, Mysterium Coniunctionis): the trilogy second pass.

Second pass over a volume the July pipeline and the first windowed batches mined thinly (Damian, 2026-11-10: all 26 trilogy windows, RULE 4 overridden by name). The register note carries the attach rule and the reporting-and-attribution clause with the borrowed-terms sentence, the source fields, the names list and the cross-register flag (all ruled by Damian, 2026-11-11). Form constraints only; names no tracked metric, so blinding (RULES #5) holds.

Run from the repo root:  python3 pipeline/mining/build_input_cw14.py LO HI N
"""
import json

import sys
LO, HI = int(sys.argv[1]), int(sys.argv[2])
OUT = f'pipeline/work/b-cw14-{sys.argv[3]}_input.json'

paras = []
for line in open('data/paragraphs.jsonl'):
    p = json.loads(line)
    if str(p['volume']) == '14' and LO <= p['paragraph'] <= HI:
        paras.append({'paragraph': p['paragraph'], 'text': p['text']})
paras.sort(key=lambda x: x['paragraph'])

seed = json.load(open('seed.json'))
vocab = sorted(
    f"{n['id']}|{n.get('label', n['id'])}|{n.get('type', '?')}" for n in seed['nodes']
)

triples = sorted({  # P24-filtered: clause predicates excluded from the pool

    (e['subject'], e['relation'], e['object'])
    for e in seed['edges']
    if e['relation'].count('-') < 4 and any(str(r.get('volume')) == '14' for r in e.get('references', []))
})

doc = {
    'volume': '14',
    'window': f'{LO}-{HI}',
    'note': (
        f'CW14 window §{LO}-{HI}. Mysterium Coniunctionis, §1-792: the components of the coniunctio (§1-35), the paradoxa (§36-103), the personification of the opposites: Sol, sulphur, Luna, sal (§104-348), Rex and Regina (§349-543), Adam and Eve (§544-653), the conjunction and its stages (§654-789) and the epilogue (§790-792). Expect many attaches onto standing nodes and edges from the first pass alongside minting where the first pass left a term unnamed. '
        'This window is a SECOND PASS over ground the graph already covers from an earlier pipeline; the existing_cw14_triples list is long and the attach rule below binds. FORM RULE (hard): the relation is a VERB PHRASE of at most 3 hyphen tokens, plus at most one trailing preposition. Never a clause. Hedges and modality go in the confidence field and, where essential, a short note on the reference - never inside the relation string. A candidate whose relation fails this rule will be mechanically dropped at pre-check. ATTACH RULE (hard): a claim already in the graph attaches to its standing edge ("existing_edge": true) and never repeats a quote already in the graph; a quote that stands in the graph is a self-check failure and is dropped at pre-check. A standing edge whose relation fits the sentence takes an attach, never a near-synonym twin. REPORTING DISCIPLINE AND ATTRIBUTION (hard; ruled by Damian, 2026-11-11): the alchemists (Dorn, Khunrath, Paracelsus, Ripley, Maier, Mylius, Zosimos, the Rosarium philosophorum, the Turba, the Aurora consurgens, the Visio Arislei and the rest), the Church Fathers, the Gnostic and Hermetic texts and any other named author or tradition are jung-quotes-source where the words are the source\'s own and jung-reports-parallel where Jung paraphrases, with the source named, however extended or sympathetic the exposition. Where a paragraph quotes or reports a source, read the sentences before and after it before choosing subject, source and claim_type. The reported claim is itself a candidate, typed to its source. Where Jung then adopts, qualifies or disputes it in his own voice, that is a separate candidate, jung-asserts, whose quote rests on Jung\'s own sentence. jung-asserts is reserved for Jung\'s own interpretive voice; a claim whose only support is the reported sentence never takes it. BORROWED TERMS: where Jung uses another author\'s term for his own concept, the claim is jung-asserts when the sentence is Jung\'s own definition or comparison, and a report of that author only when the sentence states the author\'s usage. In doubt between asserts and reports: reports. SOURCE FIELDS (hard): every jung-quotes-source and jung-reports-parallel reference carries "source_author" (a value from the input\'s sources.authors or sources.traditions, or "other") and, where the words come from a named text, "source_text" (a value from sources.texts, or "other"); the free-text "source" field stays and carries the fuller attribution (an author quoted inside another text, a chapter, a footnote). RELATION STRENGTH (hard): analogy is not identity; a parallel, a comparison or a "corresponds to" never becomes "is"; a relation of identity is allowed only where the quoted sentence itself states it. NAMES (hard): where a paragraph gives a Latin or Greek name or another alias for a node, standing or new, record it in the top-level "names" list as {"node": "<id>", "latin": "<Latin name or omitted>", "aliases": ["<other names>"], "paragraph": N} with the paragraph where Jung gives the name and no quote; each name must appear in that paragraph as written. CROSS-REGISTER FLAG (hard): a candidate whose sentence reads an alchemical term, operation, substance or figure as a psychological fact carries "cross_register": true on the candidate; a candidate that stays inside one register carries no flag. STAGES AND OPERATIONS (expectation): where Jung names an operation (calcinatio, solutio, separatio, coagulatio, sublimatio, mortificatio, putrefactio and the rest), assigns a symbol or operation to a stage (nigredo, albedo, citrinitas, rubedo) or orders them, propose the node and the relation (stage-of, precedes, follows) as ordinary candidates with quotes.'
    ),
    'vocabulary': vocab,
    'sources': {k: json.load(open('pipeline/mining/sources_controlled.json'))[k] for k in ('authors', 'traditions', 'texts')},
    'existing_cw14_triples': [list(t) for t in triples],
    'paragraphs': paras,
}

json.dump(doc, open(OUT, 'w'), indent=1, ensure_ascii=False)
chars = sum(len(p['text']) for p in paras)
print(f"{OUT}: {len(paras)} paragraphs (§{paras[0]['paragraph']}-{paras[-1]['paragraph']}), "
      f"{chars} chars, {len(vocab)} vocabulary entries, {len(triples)} existing CW14 triples")
