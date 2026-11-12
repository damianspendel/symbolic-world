#!/usr/bin/env python3
"""The quotation share of a volume: quoted letter tokens over corpus letter tokens, both counted with
tests/test_graph.py's tokenizer. The cap is per volume (Damian, 2026-11-11, option B of the arc-end
report: today's level, 9 percent); precheck_cw12/13/14.py refuses a window that would take its volume
over it, and the batch record reports the share after every window.

Run from the repo root:  python3 pipeline/mining/quote_share.py [volume ...]
"""
import json
import re
import sys

CAP_PCT = 9.0


def words(s):
    return re.findall(r"[a-z]+", s.lower())


def corpus_words(volume, path='data/paragraphs.jsonl'):
    n = 0
    for line in open(path, encoding='utf-8'):
        p = json.loads(line)
        if str(p['volume']) == str(volume):
            n += len(words(p['text']))
    return n


def quoted_words(volume, seed, extra_quotes=()):
    n = sum(len(words(r.get('quote', ''))) for e in seed['edges'] for r in e.get('references', [])
            if str(r.get('volume')) == str(volume))
    return n + sum(len(words(q)) for q in extra_quotes)


def share(volume, seed, extra_quotes=(), path='data/paragraphs.jsonl'):
    c = corpus_words(volume, path)
    q = quoted_words(volume, seed, extra_quotes)
    return c, q, (100.0 * q / c if c else 0.0)


if __name__ == '__main__':
    seed = json.load(open('seed.json', encoding='utf-8'))
    vols = sys.argv[1:] or sorted({str(r['volume']) for e in seed['edges'] for r in e['references']},
                                  key=lambda v: (len(v), v))
    for v in vols:
        c, q, pct = share(v, seed)
        print(f"CW {v}: {q} quoted of {c} corpus letter tokens = {pct:.2f}% (cap {CAP_PCT}%)")
