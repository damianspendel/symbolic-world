#!/usr/bin/env python3
"""Render a markdown draft to a PDF sized for a reMarkable 2 (157 x 210 mm
screen), for reading away from the screen. Never writes docs/PAPER.pdf.

    python3 tools/build_draft_pdf.py [in.md] [out.pdf]
    defaults: docs/PAPER_v2_draft.md -> <scratchpad or /tmp>/PAPER_v2_draft.pdf

Requires: pip install markdown; brew install weasyprint (both present for build_pdf.py).
"""
import os, pathlib, re, subprocess, sys
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'PAPER_v2_draft.md'
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(
    os.environ.get('SCRATCHPAD', '/tmp')) / (src.stem + '.pdf')
md = src.read_text()
md = re.sub(r'^> .*\n', '', md, flags=re.M)          # drafting notes stay off the page
body = markdown.markdown(md, extensions=['tables', 'fenced_code'])
css = """
@page { size: 157mm 210mm; margin: 9mm 9mm 11mm 9mm;
        @bottom-center { content: counter(page); font-size: 8pt; color: #666; } }
body { font-family: 'Iowan Old Style', 'Palatino', 'Georgia', serif; font-size: 10.5pt;
       line-height: 1.45; color: #111; }
h1 { font-size: 15pt; line-height: 1.25; margin: 0 0 6pt; }
h2 { font-size: 12pt; margin-top: 16pt; border-bottom: 0.5pt solid #999; padding-bottom: 2pt;
     page-break-after: avoid; }
h3 { font-size: 10.5pt; margin-top: 10pt; page-break-after: avoid; }
p, li { text-align: left; orphans: 3; widows: 3; }
code { font-family: Menlo, monospace; font-size: 8.5pt; }
pre { font-size: 9pt; white-space: pre-wrap; margin: 6pt 0 6pt 8pt; }
table { border-collapse: collapse; width: 100%; font-size: 7.6pt; margin: 6pt 0; }
th, td { border: 0.5pt solid #888; padding: 2.5pt 3.5pt; vertical-align: top; text-align: left; }
th { background: #eee; }
tr { page-break-inside: avoid; } thead { display: table-header-group; }
strong { font-weight: 600; }
"""
html = f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
tmp = out.with_suffix('.html')
tmp.write_text(html)
subprocess.run(['weasyprint', str(tmp), str(out)], check=True)
tmp.unlink()
print(out)
