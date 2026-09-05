#!/usr/bin/env python3
"""The v2.0 paper's six figures, drawn from one script so that four of them
are the same pipeline drawing carrying different annotations, and every
population or record value binds to graph_facts.json rather than being
typed (RULES #12, #17).

  python3 tools/figures/build_paper_figs.py   -> docs/figures/fig_v2_{1..6}_*.svg

Figure 1: the pipeline, each stage over the elements of the claim it writes
          or checks, with the tuple C = (e, s, r, o, a, m, n, f) beneath.
Figure 2: the warrant ladder, bottom to top, attested at the foundation and
          the empty human-agreed rung at the top, populations from seed.json.
Figure 3: one claim (salt symbolizes the-self): its eight parts, the stored
          value of each, and the rung each part has reached.
Figure 4: Figure 1 plus a third dimension: the risks, placed at the stage
          where each enters.
Figure 5: Figure 4 after measurement: each risk coloured by what §4 could
          establish (the rubric is in STATUS and in the legend).
Figure 6: related work mapped onto the pipeline: what each neighbour covers,
          and the cells where this work differs.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'figures'
FACTS = ROOT / 'docs' / 'experiments' / 'paper_v2_reviews' / 'graph_facts.json'

F = "font-family=\"Helvetica,Arial,sans-serif\""
MONO = "font-family=\"Menlo,monospace\""
BG, BOX, BOXS, OVL, OVLS, GREY, GREYS, RED = '#fbfaf7', '#e9f0f7', '#5b87ab', '#f3eee4', '#a9925b', '#efefef', '#8a8a8a', '#a03c3c'
GREEN, GREENS, AMBER, AMBERS, GOLD = '#e3f1e3', '#3f7d3f', '#fbf0d9', '#b7791f', '#c9a227'

STAGES = [
    # (title, who, what, elements, fill, stroke, risks)
    ('proposer', 'Opus family', 'drafts the claim and its quote from a ~70-paragraph window', 'e s r o a m', BOX, BOXS, ['R1', 'R3', 'R4', 'R5', 'R10', 'R11']),
    ('quote check', 'a script', 'the quote must be in the paragraph; any failure stops the build', 'e', '#eef4ee', '#5b8a5b', ['R2']),
    ('gate', 'Fable family', 'judges the paragraph against the claim; what passes is frozen', 's r o a m', BOX, BOXS, ['R6', 'R7']),
    ('cross-vendor', 'Gemini', 're-judges the batch blind before it merges', 's r o a m', BOX, BOXS, ['R6']),
    ('normalize', 'Opus, Fable, Gemini', 'a short verb beside the frozen string, with qualifiers', 'n', OVL, OVLS, ['R8']),
    ('families', 'two arms, then a person', 'two vendors file blind; agreement assigns, disagreement waits', 'f', OVL, OVLS, ['R9', 'R13']),
    ('query', 'read time', 'inverse and symmetric rows derived, labelled, never stored', 'r (derived)', GREY, GREYS, ['R12']),
]
RISK_LABEL = {'R1': 'wrong claim', 'R2': 'fabricated quote', 'R3': 'wrong meaning', 'R4': 'wrong voice',
              'R5': 'arbitrary pick', 'R6': 'shared vendor', 'R7': 'own referee', 'R8': 'norm. drift',
              'R9': 'wrong family', 'R10': 'node role hidden', 'R11': 'coverage unstable', 'R12': 'derived as source',
              'R13': 'anchored human'}
# Figure 5's rubric, applied to the §3 table's Control / Measured / Residual columns:
#   green  a control exists, §4 measured it, and the residual is small or excluded by construction
#   amber  a control exists, and the residual is either measured and material, or not measurable in principle
#   red    no control beyond a design choice, and no measurement
STATUS = {'R1': 'green', 'R2': 'green', 'R3': 'green', 'R12': 'green',
          'R4': 'amber', 'R5': 'amber', 'R6': 'amber', 'R7': 'amber', 'R8': 'amber', 'R9': 'amber', 'R11': 'amber', 'R13': 'amber',
          'R10': 'red'}
STATUS_STYLE = {'green': (GREEN, GREENS, '●'), 'amber': (AMBER, AMBERS, '◐'), 'red': ('#f7e9e9', RED, '○')}


def wrap(text, width):
    lines, cur = [], ''
    for w in text.split():
        if len(cur) + len(w) + 1 > width: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    lines.append(cur)
    return lines


def pipeline(with_risks: bool, status: dict | None = None, mid: str = 'ar') -> str:
    n = len(STAGES); W = 900; gap = 10; x0 = 24; bw = (W - 2 * x0 - gap * (n - 1)) / n
    maxk = max(len(st[6]) for st in STAGES) if with_risks else 0
    h = (178 + maxk * 18 + (92 if status else 74)) if with_risks else 215
    if status: title = 'The risks of Figure 4, coloured by what §4 could establish'
    elif with_risks: title = 'The pipeline, the elements of the claim it writes, and where each risk enters'
    else: title = 'The pipeline, and the elements of the claim each stage writes or checks'
    s = [f'<svg viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg" {F}>',
         f'<rect width="{W}" height="{h}" fill="{BG}"/>',
         f'<defs><marker id="{mid}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0L8,4L0,8z" fill="#6a7480"/></marker></defs>',
         f'<text x="{x0}" y="22" font-size="13" font-weight="bold" fill="#2b2b2b">{title}</text>']
    for i, (title_, who, what, els, fill, stroke, risks) in enumerate(STAGES):
        x = x0 + i * (bw + gap)
        s.append(f'<rect x="{x:.0f}" y="40" width="{bw:.0f}" height="78" rx="4" fill="{fill}" stroke="{stroke}"/>')
        s.append(f'<text x="{x + bw/2:.0f}" y="58" text-anchor="middle" font-size="11" font-weight="bold" fill="#2b2b2b">{title_}</text>')
        s.append(f'<text x="{x + bw/2:.0f}" y="71" text-anchor="middle" font-size="8.5" fill="#555">{who}</text>')
        for j, ln in enumerate(wrap(what, 24)[:3]):
            s.append(f'<text x="{x + bw/2:.0f}" y="{85 + 11*j}" text-anchor="middle" font-size="7.8" fill="#444">{ln}</text>')
        if i < n - 1:
            s.append(f'<line x1="{x + bw:.0f}" y1="79" x2="{x + bw + gap:.0f}" y2="79" stroke="#6a7480" marker-end="url(#{mid})"/>')
        s.append(f'<rect x="{x:.0f}" y="128" width="{bw:.0f}" height="26" rx="3" fill="#fff" stroke="{stroke}" stroke-dasharray="3,2"/>')
        s.append(f'<text x="{x + bw/2:.0f}" y="145" text-anchor="middle" font-size="11" {MONO} fill="#3d6a8c">{els}</text>')
        if with_risks:
            for k, r in enumerate(risks):
                ry = 178 + k * 18
                if status:
                    cf, cs, glyph = STATUS_STYLE[status[r]]
                    label = f'{glyph} {r} · {RISK_LABEL[r]}'
                else:
                    cf, cs, label = '#f7e9e9', RED, f'{r} · {RISK_LABEL[r]}'
                s.append(f'<rect x="{x + 4:.0f}" y="{ry}" width="{bw - 8:.0f}" height="15" rx="7" fill="{cf}" stroke="{cs}"/>')
                s.append(f'<text x="{x + bw/2:.0f}" y="{ry + 11}" text-anchor="middle" font-size="{8 if status else 8}" fill="{cs}">{label}</text>')
    ly = (h - (58 if status else 40)) if with_risks else 172
    s.append(f'<text x="{x0}" y="{ly}" font-size="10.5" {MONO} fill="#3d6a8c">C = (e, s, r, o, a, m, n, f)</text>')
    s.append(f'<text x="{x0 + 230}" y="{ly}" font-size="9" fill="#6a7480">e evidence · s r o subject, relation, object · a voice · m commitment · n normalized relation · f family</text>')
    if status:
        counts = {k: sum(1 for v in status.values() if v == k) for k in ('green', 'amber', 'red')}
        s.append(f'<text x="{x0}" y="{h - 38}" font-size="9" fill="{GREENS}">● green ({counts["green"]}): a control exists, §4 measured it, the residual is small or excluded by construction.</text>')
        s.append(f'<text x="{x0}" y="{h - 25}" font-size="9" fill="{AMBERS}">◐ amber ({counts["amber"]}): a control exists; the residual is measured and material, or cannot be measured in principle.</text>')
        s.append(f'<text x="{x0}" y="{h - 12}" font-size="9" fill="{RED}">○ red ({counts["red"]}): no control beyond a design choice, and no measurement. Each colour follows from the §3 table\'s columns, not from a judgement made here.</text>')
    elif with_risks:
        s.append(f'<text x="{x0}" y="{h - 22}" font-size="9" fill="{RED}">R1 to R7 are v1.3\'s risks; R8 to R13 belong to the overlay, the query layer and the human review. Controls, measurements and residuals: the table in §3.</text>')
    else:
        s.append(f'<text x="{x0}" y="192" font-size="9" fill="#2b2b2b">The rule: whatever proposes never signs off. Proposer and gate are different families; the auditor is a different vendor.</text>')
        s.append(f'<text x="{x0}" y="205" font-size="9" fill="{RED}">Disclosed exception: the family calibration gate shares a vendor with one arm.</text>')
    s.append('</svg>')
    return '\n'.join(s)


def ladder(facts: dict) -> str:
    fs = facts['family_state']
    rungs = [  # bottom first
        ('attested', 'the quote is in the paragraph', f"{facts['references']}/{facts['references']}", BOX, BOXS),
        ('model-supported', 'a gate of another family passed the claim', f"{facts['references']}/{facts['references']}", BOX, BOXS),
        ('cross-checked', 'an auditor of another vendor agreed', f"{facts['references_crossvendor_checked']}/{facts['references']}", BOX, BOXS),
        ('normalized', 'a reviewed verb beside the frozen string', f"{facts['edges_with_relation_normalized']}/{facts['edges']}", OVL, OVLS),
        ('family-assigned', 'filed under the versioned ruleset', f"{fs['assigned']}/{facts['edges']}", OVL, OVLS),
        ('derived', 'read-time inverse or symmetry, labelled', f"{facts['derived_rows_at_full_closure']} rows at closure", GREY, GREYS),
        ('contested', 'an admissible evaluation still open', f"{fs['pending-adjudication']} queued", GREY, GREYS),
        ('human-reviewed', 'one person read it against the paragraph', f"{facts['gold_set']['n']} refs · {facts['arm_agreement']['human_ruled_former_disagreements']} families", '#efe9dc', OVLS),
        ('human-agreed', 'two people, independent, unanchored', '0', '#fff', RED),
    ]
    W, rh, gap, top = 900, 30, 8, 44
    H = top + len(rungs) * (rh + gap) + 40
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" {F}>', f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         '<text x="24" y="24" font-size="13" font-weight="bold" fill="#2b2b2b">The warrant ladder, read from the foundation up · population in the released graph</text>']
    for i, (name, meaning, pop, fill, stroke) in enumerate(rungs):
        y = top + (len(rungs) - 1 - i) * (rh + gap)   # bottom rung drawn lowest
        dash = ' stroke-dasharray="5,3" stroke-width="1.5"' if name == 'human-agreed' else ''
        s.append(f'<rect x="24" y="{y}" width="852" height="{rh}" rx="4" fill="{fill}" stroke="{stroke}"{dash}/>')
        s.append(f'<text x="36" y="{y + 19}" font-size="11" font-weight="bold" fill="#2b2b2b">{name}</text>')
        s.append(f'<text x="190" y="{y + 19}" font-size="10" fill="#444">{meaning}</text>')
        col = RED if name == 'human-agreed' else '#3d6a8c'
        s.append(f'<text x="864" y="{y + 19}" text-anchor="end" font-size="10.5" {MONO} fill="{col}">{pop}</text>')
    s.append(f'<text x="24" y="{H - 14}" font-size="9" fill="#6a7480">Passing one rung warrants nothing about the next. The top rung is empty on purpose: no item has two independent human judgements.</text>')
    s.append('</svg>')
    return '\n'.join(s)


def claim(facts: dict) -> str:
    """One claim, three rows: the part and its question; the stored value; the rung reached."""
    e = facts['edge_salt_symbolizes_the_self']; fam = e['relation_family']
    gate_d, cv_d = e['verified_date'], e['crossvendor_checked'].split(',')[-1].strip().rstrip(')')
    parts = [  # (letter, name, question, value lines, rung lines, fill, stroke)
        ('e', 'evidence', 'which words, where?', [f"CW {e['volume']} §{e['paragraph']}", f"{e['quote_word_count']}-word quote"], ['attested', 'every build'], BOX, BOXS),
        ('s', 'subject', 'about what?', ['salt'], ['model-supported', f'gate {gate_d}', 'cross-checked', f'auditor {cv_d}'], BOX, BOXS),
        ('r', 'relation', 'says what of it?', ['symbolizes'], ['model-supported', f'gate {gate_d}', 'cross-checked', f'auditor {cv_d}'], BOX, BOXS),
        ('o', 'object', 'to what?', ['the-self'], ['model-supported', f'gate {gate_d}', 'cross-checked', f'auditor {cv_d}'], BOX, BOXS),
        ('a', 'voice', 'who says so?', [e['claim_type']], ['model-supported', f'gate {gate_d}', 'cross-checked', f'auditor {cv_d}'], BOX, BOXS),
        ('m', 'commitment', 'how firmly?', [e['confidence']], ['model-supported', f'gate {gate_d}', 'cross-checked', f'auditor {cv_d}'], BOX, BOXS),
        ('n', 'normalized', 'the same, as a verb?', ['none:', 'already a verb'], ['not normalized'], '#fff', GREYS),
        ('f', 'family', 'what kind of relation?', [fam['value']], ['family-assigned', f"{fam['by']}", fam['date'], 'gate audit ' + fam['audit'].split()[-1]], OVL, OVLS),
    ]
    n = len(parts); W = 900; gap = 8; x0 = 24; cw = (W - 2 * x0 - gap * (n - 1)) / n
    H = 300
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" {F}>', f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<text x="{x0}" y="22" font-size="13" font-weight="bold" fill="#2b2b2b">One claim: salt symbolizes the-self · its eight parts, the stored value of each, and the rung each has reached</text>']
    for i, (L, name, q, vals, rungs, fill, stroke) in enumerate(parts):
        x = x0 + i * (cw + gap); cx = x + cw / 2
        s.append(f'<rect x="{x:.0f}" y="38" width="{cw:.0f}" height="52" rx="4" fill="#fff" stroke="{stroke}"/>')
        s.append(f'<text x="{cx:.0f}" y="58" text-anchor="middle" font-size="15" {MONO} fill="#3d6a8c">{L}</text>')
        s.append(f'<text x="{cx:.0f}" y="72" text-anchor="middle" font-size="9" font-weight="bold" fill="#2b2b2b">{name}</text>')
        s.append(f'<text x="{cx:.0f}" y="84" text-anchor="middle" font-size="7.6" fill="#555">{q}</text>')
        s.append(f'<rect x="{x:.0f}" y="98" width="{cw:.0f}" height="40" rx="4" fill="{fill}" stroke="{stroke}"/>')
        for j, v in enumerate(vals):
            s.append(f'<text x="{cx:.0f}" y="{114 + 13*j}" text-anchor="middle" font-size="9" {MONO} fill="#2b2b2b">{v}</text>')
        dash = ' stroke-dasharray="3,2"' if rungs == ['not normalized'] else ''
        s.append(f'<rect x="{x:.0f}" y="146" width="{cw:.0f}" height="70" rx="4" fill="{fill}" stroke="{stroke}"{dash}/>')
        for j, r in enumerate(rungs):
            bold = ' font-weight="bold"' if j % 2 == 0 and rungs != ['not normalized'] else ''
            col = GREYS if rungs == ['not normalized'] else '#2b2b2b'
            s.append(f'<text x="{cx:.0f}" y="{160 + 13*j}" text-anchor="middle" font-size="7.8"{bold} fill="{col}">{r}</text>')
    for y, t in ((40 + 26, 'the part'), (98 + 22, 'stored value'), (146 + 37, 'rung reached')):
        s.append(f'<text x="{W - 6}" y="{y}" text-anchor="end" font-size="7.5" fill="#6a7480" transform="rotate(-90 {W - 6} {y})">{t}</text>')
    s.append(f'<rect x="{x0}" y="228" width="{W - 2*x0}" height="22" rx="4" fill="#fff" stroke="{RED}" stroke-dasharray="5,3"/>')
    s.append(f'<text x="{x0 + 10}" y="243" font-size="9" fill="{RED}">Not reached by any part: human-reviewed, human-agreed. No person has read this claim against its paragraph.</text>')
    s.append(f'<rect x="{x0}" y="256" width="{W - 2*x0}" height="22" rx="4" fill="{GREY}" stroke="{GREYS}"/>')
    s.append(f'<text x="{x0 + 10}" y="271" font-size="9" fill="#444">At read time: <tspan {MONO}>the-self symbolized-by salt</tspan>, one row, labelled <tspan {MONO}>derived: inverse-of(symbolizes)</tspan>, stored nowhere.</text>')
    s.append(f'<text x="{x0}" y="{H - 8}" font-size="9" fill="#6a7480">Profile: attested, model-supported, cross-checked, family-assigned by agreement, not normalized, not human-reviewed, derivable. Every value above is read from the released record (Appendix B).</text>')
    s.append('</svg>')
    return '\n'.join(s)


COLS = ['proposer', 'quote check', 'gate', 'cross-vendor', 'normalize', 'families', 'query', 'the record']
# related work rows: (label, {col: (fill_kind, note)}) — 'full' covers the stage, 'part' is adjacent or partial
RELATED = [
    ('LLM knowledge-graph extractors [5]; research agents [6]; aggregate accuracy as the report [7]', {'proposer': ('full', 'extract; 30 to 66% accuracy'), 'the record': ('part', 'one aggregate figure')}),
    ('Attributed generation [8, 9]', {'proposer': ('full', 'quotes at generation time'), 'quote check': ('part', 'model-side, not a dataset check')}),
    ('Per-triplet verification [10]', {'gate': ('part', 'single family, uncalibrated')}),
    ('Self-preference and judge reliability [11, 12, 13, 14]', {'gate': ('part', 'judges favour their own outputs'), 'cross-vendor': ('part', 'asks for published catch rates')}),
    ('Voice annotation: FactBank, PDTB, private states [15, 16, 17]', {'proposer': ('part', 'voice on text, not on graph claims')}),
    ('PhilKG [18]; Darshana Graph [19]', {'proposer': ('full', 'LLM extraction'), 'gate': ('part', 'same-ecosystem review of a selection')}),
    ('Ontology engineering for scholarly corpora [20]', {'normalize': ('full', 'standard'), 'families': ('full', 'standard; inherits the status beneath')}),
    ('Nanopublications [21]; provenance-enhanced statements [23]', {'the record': ('full', 'one claim, its provenance, its publication record')}),
    ('ARAS concordance [25]; digital edition [26]', {'proposer': ('part', 'search over the corpus, no relations')}),
]
THIS = {'proposer': 'voice and commitment on every claim', 'quote check': 'dataset-level, model-independent, canaries',
        'gate': 'different family, catch rates published', 'cross-vendor': 'different vendor, every batch',
        'normalize': 'frozen string kept beside it', 'families': 'no inherited warrant; assigned only',
        'query': 'derived rows labelled, never stored', 'the record': 'a warrant profile per part'}
GAP = {'quote check', 'gate', 'cross-vendor', 'families', 'the record'}   # cells where no neighbour does what this work does


def related() -> str:
    W = 900; x0 = 24; lab = 214; gap = 5; n = len(COLS); cw = (W - x0 - 12 - lab - gap * (n - 1)) / n
    rh, top = 44, 62
    H = top + (len(RELATED) + 1) * (rh + 4) + 52
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" {F}>', f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<text x="{x0}" y="22" font-size="13" font-weight="bold" fill="#2b2b2b">Related work on the pipeline: what each neighbour covers, and where this work differs</text>']
    for j, c in enumerate(COLS):
        x = x0 + lab + j * (cw + gap)
        fill, stroke = (GREY, GREYS) if c in ('query', 'the record') else ((OVL, OVLS) if c in ('normalize', 'families') else (BOX, BOXS))
        s.append(f'<rect x="{x:.0f}" y="36" width="{cw:.0f}" height="20" rx="3" fill="{fill}" stroke="{stroke}"/>')
        s.append(f'<text x="{x + cw/2:.0f}" y="50" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#2b2b2b">{c}</text>')
    rows = RELATED + [('this work', None)]
    for i, (label, cells) in enumerate(rows):
        y = top + i * (rh + 4)
        last = cells is None
        if last:
            s.append(f'<rect x="{x0 - 6}" y="{y - 3}" width="{W - 2*x0 + 12}" height="{rh + 6}" rx="5" fill="#fffdf5" stroke="{GOLD}" stroke-width="1.2"/>')
        bold = ' font-weight="bold"' if last else ''
        for k, ln in enumerate(wrap(label, 44)[:3]):
            s.append(f'<text x="{x0}" y="{y + 14 + 11*k}" font-size="8.2"{bold} fill="#2b2b2b">{ln}</text>')
        for j, c in enumerate(COLS):
            x = x0 + lab + j * (cw + gap)
            if last:
                gapc = c in GAP
                s.append(f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{rh}" rx="3" fill="{GREEN if gapc else "#eef3ee"}" stroke="{GOLD if gapc else GREENS}" stroke-width="{2 if gapc else 0.8}"/>')
                for k, ln in enumerate(wrap(THIS[c], 15)[:3]):
                    s.append(f'<text x="{x + cw/2:.0f}" y="{y + 13 + 11*k}" text-anchor="middle" font-size="8.2" fill="#1f4d1f">{ln}</text>')
                continue
            s.append(f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{rh}" rx="3" fill="#fff" stroke="#ddd"/>')
            if c in cells:
                kind, note = cells[c]
                full = kind == 'full'
                cf, sw, dash = ('#e9f0f7', 1.4, '') if full else ('#fff', 0.9, ' stroke-dasharray="3,2"')
                s.append(f'<rect x="{x + 3:.0f}" y="{y + 3}" width="{cw - 6:.0f}" height="{rh - 6}" rx="3" fill="{cf}" stroke="{BOXS}" stroke-width="{sw}"{dash}/>')
                for k, ln in enumerate(wrap(note, 15)[:3]):
                    s.append(f'<text x="{x + cw/2:.0f}" y="{y + 13 + 11*k}" text-anchor="middle" font-size="8.2" fill="#2b4f6e">{ln}</text>')
    ly = H - 34
    s.append(f'<rect x="{x0}" y="{ly - 9}" width="12" height="12" fill="#e9f0f7" stroke="{BOXS}" stroke-width="1.4"/><text x="{x0 + 17}" y="{ly + 1}" font-size="8.5" fill="#444">covers the stage</text>')
    s.append(f'<rect x="{x0 + 120}" y="{ly - 9}" width="12" height="12" fill="#fff" stroke="{BOXS}" stroke-dasharray="3,2"/><text x="{x0 + 137}" y="{ly + 1}" font-size="8.5" fill="#444">adjacent or partial</text>')
    s.append(f'<rect x="{x0 + 260}" y="{ly - 9}" width="12" height="12" fill="{GREEN}" stroke="{GOLD}" stroke-width="2"/><text x="{x0 + 277}" y="{ly + 1}" font-size="8.5" fill="#444">the gap: no neighbour does this at this stage</text>')
    s.append(f'<text x="{x0}" y="{H - 12}" font-size="9" fill="#6a7480">Numbers are reference-list entries. The baseline row is the report this pipeline exists to beat; the last row states what differs, not that it is better.</text>')
    s.append('</svg>')
    return '\n'.join(s)


if __name__ == '__main__':
    facts = json.load(open(FACTS))
    files = {'fig_v2_1_pipeline.svg': pipeline(False, mid='ar1'), 'fig_v2_2_ladder.svg': ladder(facts),
             'fig_v2_3_claim.svg': claim(facts), 'fig_v2_4_risks.svg': pipeline(True, mid='ar4'),
             'fig_v2_5_status.svg': pipeline(True, STATUS, mid='ar5'), 'fig_v2_6_related.svg': related()}
    for name, svg in files.items():
        (OUT / name).write_text(svg)
    print('wrote', ', '.join(files), '(values from', FACTS.name + ')')
