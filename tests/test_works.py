#!/usr/bin/env python3
"""
Invariant tests for works.json, the table of works in the extracted volumes.

The table is bibliographic metadata the site reads for its work pages and date
filter, so what matters is that every row is well formed and that, within each
volume, the works' paragraph ranges tile the corpus: every extracted paragraph
falls in exactly one work, with no gap and no overlap between consecutive
works. The corpus (data/paragraphs.jsonl) is local-only; where it is absent
the coverage tests are skipped and the structural tests still run.

Run: python3 -m pytest tests/test_works.py
"""
import json
import os
import re
from collections import defaultdict

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKS = os.path.join(ROOT, "works.json")
CORPUS = os.path.join(ROOT, "data", "paragraphs.jsonl")
SEED = os.path.join(ROOT, "seed.json")

REQUIRED = {"id", "title", "volume", "first_paragraph", "last_paragraph", "year_written", "year_revised"}
OPTIONAL = {"note"}
ID = re.compile(r"^cw(5|6|7|8|9i|9ii|11|12|13|14|16)-[a-z0-9]+(-[a-z0-9]+)*$")


@pytest.fixture(scope="module")
def works():
    with open(WORKS, encoding="utf-8") as f:
        doc = json.load(f)
    assert isinstance(doc.get("works"), list) and doc["works"], "works.json carries a non-empty 'works' list"
    return doc["works"]


@pytest.fixture(scope="module")
def corpus_paragraphs():
    if not os.path.exists(CORPUS):
        pytest.skip("data/paragraphs.jsonl is local-only and absent here")
    by_volume = defaultdict(set)
    with open(CORPUS, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            by_volume[str(rec["volume"])].add(int(rec["paragraph"]))
    return by_volume


# ---------------------------------------------------------------- structure ---

def test_every_row_has_exactly_the_declared_fields(works):
    for w in works:
        keys = set(w)
        assert REQUIRED <= keys, f"{w.get('id')}: missing {sorted(REQUIRED - keys)}"
        assert keys <= REQUIRED | OPTIONAL, f"{w.get('id')}: unexpected {sorted(keys - REQUIRED - OPTIONAL)}"


def test_field_types_and_ranges(works):
    for w in works:
        assert isinstance(w["id"], str) and ID.match(w["id"]), f"bad id {w['id']!r}"
        assert isinstance(w["title"], str) and w["title"].strip(), f"{w['id']}: empty title"
        assert isinstance(w["volume"], str), f"{w['id']}: volume is a string as in seed.json"
        assert w["id"].startswith(f"cw{w['volume']}-"), f"{w['id']}: id names a different volume"
        assert isinstance(w["first_paragraph"], int) and isinstance(w["last_paragraph"], int)
        assert 1 <= w["first_paragraph"] <= w["last_paragraph"], f"{w['id']}: range out of order"
        assert isinstance(w["year_written"], int) and 1900 <= w["year_written"] <= 1961, f"{w['id']}: year_written"
        if w["year_revised"] is not None:
            assert isinstance(w["year_revised"], int), f"{w['id']}: year_revised"
            assert w["year_written"] < w["year_revised"] <= 1966, f"{w['id']}: year_revised precedes year_written"
        if "note" in w:
            assert isinstance(w["note"], str) and w["note"].strip()


def test_ids_and_titles_are_unique(works):
    ids = [w["id"] for w in works]
    assert len(ids) == len(set(ids)), "duplicate id"
    titles = [(w["volume"], w["title"]) for w in works]
    assert len(titles) == len(set(titles)), "duplicate title within a volume"


def test_ranges_within_a_volume_are_ordered_and_contiguous(works):
    """Consecutive works meet exactly: the next starts one past the last."""
    by_volume = defaultdict(list)
    for w in works:
        by_volume[w["volume"]].append(w)
    for vol, rows in by_volume.items():
        spans = sorted((w["first_paragraph"], w["last_paragraph"], w["id"]) for w in rows)
        for (f1, l1, id1), (f2, l2, id2) in zip(spans, spans[1:]):
            assert l1 < f2, f"CW {vol}: {id1} and {id2} overlap"
            assert f2 == l1 + 1, f"CW {vol}: gap between {id1} (ends §{l1}) and {id2} (starts §{f2})"
        # rows are listed in reading order too, so the file reads like a contents page
        listed = [(w["first_paragraph"], w["id"]) for w in rows]
        assert listed == sorted(listed), f"CW {vol}: rows out of paragraph order"


# ----------------------------------------------------------------- coverage ---

def test_volumes_match_the_corpus(works, corpus_paragraphs):
    assert {w["volume"] for w in works} == set(corpus_paragraphs), "works.json and the corpus name the same volumes"


def test_every_corpus_paragraph_belongs_to_exactly_one_work(works, corpus_paragraphs):
    by_volume = defaultdict(list)
    for w in works:
        by_volume[w["volume"]].append(w)
    for vol, paragraphs in corpus_paragraphs.items():
        rows = by_volume[vol]
        for p in sorted(paragraphs):
            owners = [w["id"] for w in rows if w["first_paragraph"] <= p <= w["last_paragraph"]]
            assert len(owners) == 1, f"CW {vol} §{p} belongs to {owners or 'no work'}"


def test_work_ranges_span_the_corpus_exactly(works, corpus_paragraphs):
    """The first work starts at the volume's first extracted paragraph and the
    last work ends at its last; no range reaches outside the corpus."""
    by_volume = defaultdict(list)
    for w in works:
        by_volume[w["volume"]].append(w)
    for vol, paragraphs in corpus_paragraphs.items():
        rows = by_volume[vol]
        assert min(w["first_paragraph"] for w in rows) == min(paragraphs), f"CW {vol}: first work starts late or early"
        assert max(w["last_paragraph"] for w in rows) == max(paragraphs), f"CW {vol}: last work ends short or long"


def test_every_cited_paragraph_has_a_work(works):
    """Every reference in seed.json resolves to a work, so the site can name one."""
    with open(SEED, encoding="utf-8") as f:
        seed = json.load(f)
    by_volume = defaultdict(list)
    for w in works:
        by_volume[w["volume"]].append((w["first_paragraph"], w["last_paragraph"]))
    unplaced = set()
    for e in seed["edges"]:
        for r in e.get("references", []):
            vol, p = str(r["volume"]), int(r["paragraph"])
            if not any(a <= p <= b for a, b in by_volume.get(vol, [])):
                unplaced.add((vol, p))
    assert not unplaced, f"citations outside every work: {sorted(unplaced)[:10]}"
