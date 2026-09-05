#!/usr/bin/env python3
"""Build docs/PAPER.pdf from docs/PAPER.md (figures inlined, footnotes, print CSS).
Usage: python3 tools/build_pdf.py   (requires: pip install markdown; brew install weasyprint)"""
import markdown, re, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
subprocess.run(["python3", str(ROOT / "tools/check_paper_facts.py")], check=True)
md = (ROOT / "docs/PAPER.md").read_text()
def _inline_svg(m):
    # markdown splits a multi-line <svg> into paragraphs; hand it one line inside a figure with its caption
    svg = (ROOT / "docs" / m.group(2)).read_text()
    return "<figure>" + re.sub(r"\s*\n\s*", " ", svg).strip() + f"<figcaption>{m.group(1)}</figcaption></figure>"
md = re.sub(r"!\[([^\]]*)\]\((figures/[^)]+)\)", _inline_svg, md)
body = markdown.markdown(md, extensions=["tables", "fenced_code", "footnotes"])
# glue "Table N" captions to their tables without forbidding page breaks inside big tables
# bottom-of-page footnotes (ACL convention): inline each definition at its
# reference point as a float:footnote span; drop the terminal endnote block
m = re.search(r'<div class="footnote">.*?</div>', body, re.S)
if m:
    defs = {}
    for li in re.finditer(r'<li id="fn:([^"]+)">\s*<p>(.*?)</p>\s*</li>', m.group(0), re.S):
        content = re.sub(r'<a class="footnote-backref".*?</a>', '', li.group(2)).replace('&#160;', ' ').strip()
        defs[li.group(1)] = content
    body = body.replace(m.group(0), '')
    body = re.sub(r'<sup id="fnref2?:([^"]+)"><a class="footnote-ref"[^>]*>\d+</a></sup>',
                  lambda mm: f'<span class="fnote">{defs[mm.group(1)]}</span>', body)
body = re.sub(r"<p><strong>(Table [AB]?\d+[^<]*)</strong>",
              r"<p class='tcap'><strong>\1</strong>", body)
css = "\n@page { size: A4; margin: 22mm 19mm; @bottom-center { content: counter(page); font-size: 9px; color: #888; } }\nbody { font-family: 'Iowan Old Style', 'Palatino', 'Georgia', serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }\nh1 { font-size: 17pt; line-height: 1.25; margin-bottom: 4pt; }\nh2 { font-size: 12.5pt; margin-top: 18pt; border-bottom: 0.5pt solid #bbb; padding-bottom: 2pt; }\nh3 { font-size: 11pt; }\np, li { text-align: justify; }\ncode { font-family: Menlo, monospace; font-size: 8.5pt; background: #f4f2ee; padding: 0 2px; }\npre { background: #f4f2ee; padding: 8px; font-size: 8pt; overflow-x: hidden; white-space: pre-wrap; }\ntable { border-collapse: collapse; width: 100%; font-size: 8.2pt; margin: 8pt 0; }\nth, td { border: 0.5pt solid #999; padding: 3.5pt 5pt; text-align: left; vertical-align: top; }\nth { background: #efece6; }\nsvg { width: 100%; height: auto; margin: 8pt 0; }\nfigure { margin: 10pt 0; page-break-inside: avoid; }\nfigcaption { font-size: 8.5pt; color: #444; margin-top: 3pt; text-align: left; }\nem { color: #333; }\nblockquote { border-left: 2pt solid #ccc; margin-left: 0; padding-left: 10pt; color: #444; }\na { color: #405a75; text-decoration: none; }\nimg { max-width: 100%; }\nhr { border: none; border-top: 0.5pt solid #bbb; margin: 14pt 0; }\n\n.fnote { float: footnote; font-size: 8pt; line-height: 1.4; text-align: left; }\n::footnote-call { content: counter(footnote); font-size: 6.5pt; vertical-align: super; }\n::footnote-marker { content: counter(footnote) '. '; font-size: 8pt; }\n@page { @footnote { border-top: 0.5pt solid #999; padding-top: 4pt; margin-top: 8pt; } }\ntr { page-break-inside: avoid; } thead { display: table-header-group; } .tcap { page-break-after: avoid; }\nh2 { page-break-after: avoid; }\n"
html = f"<!doctype html><html><head><meta charset=\'utf-8\'><style>{css}</style></head><body>{body}</body></html>"
tmp = ROOT / "docs" / ".paper_build.html"
tmp.write_text(html)
subprocess.run(["weasyprint", str(tmp), str(ROOT / "docs/PAPER.pdf")], check=True)
tmp.unlink()
print("built docs/PAPER.pdf")
