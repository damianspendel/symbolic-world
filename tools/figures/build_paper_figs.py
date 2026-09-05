#!/usr/bin/env python3
"""The v2.0 paper's three figures, drawn from one script so Figure 3 is
Figure 1 grown by one dimension, and the ladder's populations bind to the
graph rather than being typed (RULES #12, #17).

  python3 tools/figures/build_paper_figs.py            -> docs/figures/fig_v2_{1,2,3}.svg

Figure 1: the pipeline, each stage over the elements of the claim it writes
          or checks, with the tuple C = (e, s, r, o, a, m, n, f) beneath.
Figure 2: the warrant ladder, bottom to top, attested at the foundation and
          the empty human-agreed rung at the top, populations from seed.json.
Figure 3: Figure 1 plus a third dimension: the risks, placed at the stage
          where each enters.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'figures'
FACTS = ROOT / 'docs' / 'experiments' / 'paper_v2_reviews' / 'graph_facts.json'

F = "font-family=\"Helvetica,Arial,sans-serif\""
MONO = "font-family=\"Menlo,monospace\""
BG, BOX, BOXS, OVL, OVLS, GREY, GREYS, RED = '#fbfaf7', '#e9f0f7', '#5b87ab', '#f3eee4', '#a9925b', '#efefef', '#8a8a8a', '#a03c3c'

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
              'R5': 'arbitrary selection', 'R6': 'shared vendor', 'R7': 'own referee', 'R8': 'normalization drift',
              'R9': 'wrong family', 'R10': 'node role hidden', 'R11': 'coverage unstable', 'R12': 'derived read as source',
              'R13': 'anchored human'}


def pipeline(with_risks: bool) -> str:
    n = len(STAGES); W = 900; gap = 10; x0 = 24; bw = (W - 2 * x0 - gap * (n - 1)) / n
    maxk = max(len(st[6]) for st in STAGES) if with_risks else 0
    h = (178 + maxk * 18 + 74) if with_risks else 215
    s = [f'<svg viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg" {F}>',
         f'<rect width="{W}" height="{h}" fill="{BG}"/>',
         '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0L8,4L0,8z" fill="#6a7480"/></marker></defs>',
         f'<text x="{x0}" y="22" font-size="13" font-weight="bold" fill="#2b2b2b">'
         + ('The pipeline, the elements of the claim it writes, and where each risk enters' if with_risks
            else 'The pipeline, and the elements of the claim each stage writes or checks') + '</text>']
    for i, (title, who, what, els, fill, stroke, risks) in enumerate(STAGES):
        x = x0 + i * (bw + gap)
        s.append(f'<rect x="{x:.0f}" y="40" width="{bw:.0f}" height="78" rx="4" fill="{fill}" stroke="{stroke}"/>')
        s.append(f'<text x="{x + bw/2:.0f}" y="58" text-anchor="middle" font-size="11" font-weight="bold" fill="#2b2b2b">{title}</text>')
        s.append(f'<text x="{x + bw/2:.0f}" y="71" text-anchor="middle" font-size="8.5" fill="#555">{who}</text>')
        # wrap 'what' into two lines at ~24 chars
        words = what.split(); lines, cur = [], ''
        for w in words:
            if len(cur) + len(w) + 1 > 24: lines.append(cur); cur = w
            else: cur = (cur + ' ' + w).strip()
        lines.append(cur)
        for j, ln in enumerate(lines[:3]):
            s.append(f'<text x="{x + bw/2:.0f}" y="{85 + 11*j}" text-anchor="middle" font-size="7.8" fill="#444">{ln}</text>')
        if i < n - 1:
            s.append(f'<line x1="{x + bw:.0f}" y1="79" x2="{x + bw + gap:.0f}" y2="79" stroke="#6a7480" marker-end="url(#ar)"/>')
        # element band
        s.append(f'<rect x="{x:.0f}" y="128" width="{bw:.0f}" height="26" rx="3" fill="#fff" stroke="{stroke}" stroke-dasharray="3,2"/>')
        s.append(f'<text x="{x + bw/2:.0f}" y="145" text-anchor="middle" font-size="11" {MONO} fill="#3d6a8c">{els}</text>')
        if with_risks:
            for k, r in enumerate(risks):
                ry = 178 + k * 18
                s.append(f'<rect x="{x + 4:.0f}" y="{ry}" width="{bw - 8:.0f}" height="15" rx="7" fill="#f7e9e9" stroke="{RED}"/>')
                s.append(f'<text x="{x + bw/2:.0f}" y="{ry + 11}" text-anchor="middle" font-size="7.6" fill="{RED}">{r} · {RISK_LABEL[r]}</text>')
    ly = (h - 40) if with_risks else 172
    s.append(f'<text x="{x0}" y="{ly}" font-size="10.5" {MONO} fill="#3d6a8c">C = (e, s, r, o, a, m, n, f)</text>')
    s.append(f'<text x="{x0 + 230}" y="{ly}" font-size="9" fill="#6a7480">e evidence · s r o subject, relation, object · a voice · m commitment · n normalized relation · f family</text>')
    if not with_risks:
        s.append(f'<text x="{x0}" y="192" font-size="9" fill="#2b2b2b">The rule: whatever proposes never signs off. Proposer and gate are different families; the auditor is a different vendor.</text>')
        s.append(f'<text x="{x0}" y="205" font-size="9" fill="{RED}">Disclosed exception: the family calibration gate shares a vendor with one arm.</text>')
    else:
        s.append(f'<text x="{x0}" y="{h - 22}" font-size="9" fill="{RED}">R1 to R7 are v1.3\'s risks; R8 to R13 belong to the overlay, the query layer and the human review. Controls, measurements and residuals: the table in §3.</text>')
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


if __name__ == '__main__':
    facts = json.load(open(FACTS))
    (OUT / 'fig_v2_1_pipeline.svg').write_text(pipeline(False))
    (OUT / 'fig_v2_2_ladder.svg').write_text(ladder(facts))
    (OUT / 'fig_v2_3_risks.svg').write_text(pipeline(True))
    print('wrote fig_v2_1_pipeline.svg, fig_v2_2_ladder.svg, fig_v2_3_risks.svg (populations from', FACTS.name + ')')
