#!/usr/bin/env python3
"""
JungKG — corpus extractor (Phase 0/1)

Turns the Collected Works epub into a stream of {volume, paragraph, text}
records, one per Jung's numbered CW paragraph (§). The paragraph number is
read mechanically from the epub markup, never inferred — this is what makes
the downstream knowledge-graph citations trustworthy.

Raw output contains the full copyrighted text and is written to data/,
which is gitignored. Only derived triples + § pointers are ever published.

Usage:
    python3 extract.py --epub /path/to/CollectedWorks.epub
"""
import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile

# Body-text file ranges per alchemy volume (front-matter, bibliography and
# index deliberately excluded — they cite [§] numbers and would create noise).
VOLUME_RANGES = {
    8: (370, 393),       # Structure & Dynamics of the Psyche (§1-997, incl. Synchronicity)
    12: (638, 660),
    13: (678, 719),
    14: (756, 773),
    "9ii": (468, 490),   # Aion (CW 9, Part II) — chapters I–XIV; biblio/index excluded
    "9i": (421, 445),    # Archetypes & the Collective Unconscious; biblio/index excluded
    16: (825, 859),      # The Practice of Psychotherapy (incl. Psychology of the Transference)
    5: (202, 218),       # Symbols of Transformation; biblio/index excluded
    11: (602, 619),      # Psychology and Religion: West and East (Trinity, Mass, Answer to Job)
    7: (306, 327),       # Two Essays on Analytical Psychology (§1-406); the appendices (earlier drafts, §407-521) excluded
    6: (260, 261),       # Psychological Types, chapters X and XI only (§556-844): the type descriptions and the Definitions
}

# A numbered paragraph opens with a bracketed superscript marker, e.g.
# <span class="vol_01_superscript2">[44]</span>. Footnote references are
# superscript too but are *unbracketed* ([N] vs N), and index/biblio back-refs
# are filtered by (a) excluding those files and (b) the monotonic check below.
# Print-page breaks are empty anchors, e.g. <a id="vol_14_page_22"></a>,
# interleaved with the paragraphs — carrying the most recent one gives each § its
# page in the digitized (Bollingen) edition: locator metadata, not text.
EVENT = re.compile(r'id="vol_[0-9a-z]+_page_(\d+)"'
                   r'|superscript\d*">\s*\[(\d+)\]\s*</span>')
TAG = re.compile(r'<[^>]+>')
WS = re.compile(r'\s+')


def clean(html_fragment: str) -> str:
    return WS.sub(' ', TAG.sub(' ', html_fragment)).strip()


def volume_files(text_dir: str, start: int, end: int):
    out = []
    for name in os.listdir(text_dir):
        m = re.search(r'part(\d+)', name)
        if m and start <= int(m.group(1)) <= end:
            out.append(name)
    return sorted(out)


def extract_volume(text_dir: str, vol, start: int, end: int):
    """Yield (vol, §, text, page) in document order, keeping only the strictly
    ascending paragraph sequence so stray bracketed numbers can't slip in.
    Footnote and cross-reference markers are small, out-of-order numbers, so
    requiring each accepted § to exceed the last one filters them out while
    tolerating the occasional gap at a file boundary. `page` is the most recent
    print-page anchor seen (None if the volume carries none)."""
    last = 0
    page = None
    for name in volume_files(text_dir, start, end):
        html = open(os.path.join(text_dir, name), encoding='utf-8',
                    errors='replace').read()
        events = list(EVENT.finditer(html))
        for i, m in enumerate(events):
            if m.group(1) is not None:          # a page-break anchor
                page = int(m.group(1))
                continue
            para = int(m.group(2))              # a paragraph-start marker
            if para > last:
                # Text runs to the next paragraph marker; any page anchors in
                # between sit inside the span and are stripped by clean().
                j = i + 1
                while j < len(events) and events[j].group(2) is None:
                    j += 1
                stop = events[j].start() if j < len(events) else len(html)
                text = clean(html[m.end():stop])
                if len(text) > 40:
                    yield (vol, para, text, page)
                    last = para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--epub', required=True)
    ap.add_argument('--out', default='data/paragraphs.jsonl')
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix='jungkg_')
    try:
        with zipfile.ZipFile(args.epub) as z:
            z.extractall(tmp)
        text_dir = os.path.join(tmp, 'text')

        os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
        total = 0
        with open(args.out, 'w', encoding='utf-8') as f:
            for vol, (start, end) in VOLUME_RANGES.items():
                count = 0
                for v, para, text, page in extract_volume(text_dir, vol, start, end):
                    rec = {'volume': v, 'paragraph': para, 'text': text}
                    if page is not None:
                        rec['page'] = page
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                    count += 1
                    total += 1
                print(f'Vol {vol}: {count} paragraphs')
        print(f'Wrote {total} paragraphs -> {args.out}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
