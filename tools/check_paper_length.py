#!/usr/bin/env python3
"""Word budget for the paper, enforced rather than remembered.

Damian, 2026-08-18: the v2.0 revision must say more than v1.3 in fewer words.
Budgets per section come from the agreed table of contents; the body total is
the hard cap. Run on every drafting pass and in CI before build_pdf.

    python3 tools/check_paper_length.py [path]      default docs/PAPER.md

Exit 1 if any section or the body total is over budget. Sections not in the
budget table are reported, never gated, so appendices and notes stay free.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'PAPER.md'
text = path.read_text()

BODY_CAP = 7000
BUDGET = {            # section number -> words, from Damian's 2026-09-05 restructure
    'Abstract': 160,  # "shorten by 50%"
    '1': 500,         # claims are not triples
    '2': 1000,        # how would we build a warranted atlas (reserved words, figures 1-2, the salt edge, the profile)
    '3': 700,         # risks and controls (figure 3 + the table)
    '4': 1000,        # what we measured, ending in the profile table
    '5': 500,         # six questions answered from the graph
    '6': 600,         # disagreement as an output
    '7': 500,         # limitations, with the open research questions
    '8': 600,         # related work
    '9': 300,         # conclusion
}
EM_DASH_CAP = 3       # rationed hard, per the writing rules


def words(s):
    return len(re.findall(r'\S+', s))


body = re.split(r'^## Appendix', text, maxsplit=1, flags=re.M)[0]
body = re.sub(r'^> .*$', '', body, flags=re.M)          # drafting notes
sections = re.split(r'^## ', body, flags=re.M)[1:]
failures, rows = [], []
for sec in sections:
    head = sec.split('\n', 1)[0].strip()
    m = re.match(r'(\d+)\.', head)
    key = m.group(1) if m else ('Abstract' if head.lower().startswith('abstract') else head)
    n = words(sec) - words(head)
    cap = BUDGET.get(key)
    flag = '' if cap is None else ('OVER' if n > cap else 'ok')
    rows.append((head[:48], n, cap, flag))
    if cap is not None and n > cap:
        failures.append(f'§{key} {n} words, budget {cap}')

total = sum(r[1] for r in rows)
dashes = body.count('—')
for head, n, cap, flag in rows:
    print(f'  {head:<50} {n:>5}  {"" if cap is None else f"/ {cap}":<7} {flag}')
print(f'  {"BODY TOTAL":<50} {total:>5}  / {BODY_CAP:<5} {"OVER" if total > BODY_CAP else "ok"}')
print(f'  {"em-dashes in body":<50} {dashes:>5}  / {EM_DASH_CAP:<5} {"OVER" if dashes > EM_DASH_CAP else "ok"}')
if total > BODY_CAP:
    failures.append(f'body {total} words, cap {BODY_CAP}')
if dashes > EM_DASH_CAP:
    failures.append(f'{dashes} em-dashes, cap {EM_DASH_CAP}')
if failures:
    print('PAPER LENGTH: FAIL: ' + '; '.join(failures))
    sys.exit(1)
print('PAPER LENGTH: ok')
