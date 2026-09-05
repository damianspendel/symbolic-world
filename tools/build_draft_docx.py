#!/usr/bin/env python3
"""Render a markdown draft to Word (.docx) for review outside the repo.
Never writes docs/PAPER.docx or anything under docs/.

    python3 tools/build_draft_docx.py [in.md] [out.docx]
    defaults: docs/PAPER_v2_draft.md -> <scratchpad or /tmp>/PAPER_v2_draft.docx

Figures: the draft embeds SVGs, which Word handles badly, so each is rendered
to PNG first (weasyprint -> pdftoppm, the same path build_draft_pdf uses) and
the markdown handed to pandoc points at the PNGs. Requires pandoc, weasyprint,
pdftoppm (poppler).
"""
import os, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'PAPER_v2_draft.md'
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(
    os.environ.get('SCRATCHPAD', '/tmp')) / (src.stem + '.docx')
md = src.read_text()
md = re.sub(r'^> .*\n', '', md, flags=re.M)          # drafting notes stay off the page

work = pathlib.Path(tempfile.mkdtemp(prefix='draft_docx_'))


def _png(m):
    cap, rel = m.group(1), m.group(2)
    svg = (src.parent / rel)
    stem = work / svg.stem
    html = stem.with_suffix('.html')
    html.write_text("<html><head><meta charset='utf-8'><style>@page{size:900px 2000px;margin:0}"
                    "body{margin:0;width:900px}svg{width:900px;height:auto}</style></head><body>"
                    + svg.read_text() + "</body></html>")
    subprocess.run(['weasyprint', str(html), str(stem.with_suffix('.pdf'))], check=True,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['pdftoppm', '-png', '-r', '220', '-singlefile', '-cropbox',
                    str(stem.with_suffix('.pdf')), str(stem)], check=True)
    # trim the tall page down to the drawing: pdftoppm keeps the page box, so crop white rows
    try:
        from PIL import Image, ImageChops
        im = Image.open(stem.with_suffix('.png')).convert('RGB')
        bg = Image.new('RGB', im.size, (255, 255, 255))
        box = ImageChops.difference(im, bg).getbbox()
        if box:
            im.crop((0, 0, im.width, box[3] + 8)).save(stem.with_suffix('.png'))
    except ImportError:
        pass
    return f'![{cap}]({stem.with_suffix(".png")})'


md = re.sub(r'!\[([^\]]*)\]\((figures/[^)]+)\)', _png, md)
md_path = work / 'draft.md'
md_path.write_text(md)
subprocess.run(['pandoc', str(md_path), '-f', 'markdown+pipe_tables+smart', '-t', 'docx',
                '--resource-path', str(work), '-o', str(out)], check=True)
print(out)
