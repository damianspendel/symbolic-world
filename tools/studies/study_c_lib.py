#!/usr/bin/env python3
"""Shared mechanics for Study C — normalization validation.

Design: docs/experiments/study_c/DESIGN.md (pre-registered 2026-08-28).
This module holds the population loader and every comparison rule Study C
scores on. It is committed before the first API call so that no rule can be
chosen after a result is seen (RULES #11).

Nothing here writes seed.json.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / 'seed.json'
WORK = ROOT / 'pipeline' / 'work' / 'study_c'          # gitignored
DOCS = ROOT / 'docs' / 'experiments' / 'study_c'       # committed receipts

PLANT_SEED = 20260830           # stamped into every C2 artifact (RULES #13)
QUALIFIER_KEYS = ('carrier', 'scope', 'condition', 'modality', 'note')

# ---------------------------------------------------------------- population


def edge_key(edge):
    """Stable identity for an edge: the frozen verbatim triple."""
    return f"{edge['subject']}|{edge['relation']}|{edge['object']}"


def load_population():
    """The edges carrying a relation_normalized layer, in seed.json order.

    `idx` is the Study C item number and is stable because Study C never
    writes seed.json and no mining runs remain for v2.0.
    """
    edges = json.load(open(SEED))['edges']
    pop = []
    for seed_index, edge in enumerate(edges):
        if edge.get('relation_normalized'):
            pop.append({
                'idx': len(pop),
                'seed_index': seed_index,
                'key': edge_key(edge),
                'edge': edge,
            })
    return pop


def first_reference(edge):
    """The reference the normalization was gated against: the first one."""
    return edge['references'][0]


# ------------------------------------------------------- verb comparison (C1a)

COPULA = {'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am'}

# Dropped from a verb's signature: copulas and articles only. Prepositions stay
# in — they carry direction, and "symbolizes" against "symbolized-by" must not
# come out as a match. Whatever this rule leaves unsettled goes to the Fable
# arm, which judges with a reason; a mechanical rule may not manufacture
# agreement it has not earned.
FUNCTION = COPULA | {'a', 'an', 'the', 'and', 'or', 'that', 'its', 'it', 'this'}

# Dropped when measuring content overlap between a relation and its qualifiers.
STOPWORDS = FUNCTION | {
    'of', 'to', 'by', 'in', 'as', 'with', 'for', 'on', 'at', 'into', 'from',
    'upon', 'which', 'their', 'his', 'her', 'not', 'but',
}


def tokens(text):
    """Letter tokens of a relation string, hyphens and case discarded."""
    text = unicodedata.normalize('NFKD', text or '').lower()
    return [t for t in re.split(r'[^a-z]+', text) if t]


def stem(token):
    """A deterministic suffix stripper. Not linguistics — a fixed rule so that
    'produces'/'produced'/'producing' compare equal without a judgment call."""
    if len(token) > 4 and token.endswith('ies'):
        return token[:-3] + 'y'
    for suffix in ('ing', 'ed', 'es', 's'):
        if len(token) > len(suffix) + 2 and token.endswith(suffix):
            return token[:-len(suffix)]
    return token


def verb_signature(relation):
    """Content of a verb phrase: function words dropped, each token stemmed,
    order kept."""
    return tuple(stem(t) for t in tokens(relation) if t not in FUNCTION)


def verb_agreement(a, b):
    """The mechanical first pass of C1(a).

    EXACT      — same tokens.
    INFLECTION — same content after copula/function-word drop and stemming.
    REMAINDER  — neither; goes to the Fable arm for a same-relation judgment.
    """
    if a is None or b is None:
        return 'REMAINDER'
    if tokens(a) == tokens(b):
        return 'EXACT'
    sig_a, sig_b = verb_signature(a), verb_signature(b)
    if sig_a and sig_a == sig_b:
        return 'INFLECTION'
    return 'REMAINDER'


# -------------------------------------------------- qualifier retention (C1b)


def content_tokens(text):
    """Stemmed content tokens, stopwords and one- and two-letter tokens dropped."""
    return {stem(t) for t in tokens(text) if t not in STOPWORDS and len(t) > 2}


def qualifier_presence(qualifiers):
    """Which qualifier kinds an arm filled."""
    qualifiers = qualifiers or {}
    return {k: bool(qualifiers.get(k)) for k in QUALIFIER_KEYS}


def dropped_material(relation_verbatim, arm_relation):
    """Content the verbatim relation string held that the arm's verb does not."""
    return content_tokens(relation_verbatim) - content_tokens(arm_relation)


def qualifier_coverage(relation_verbatim, arm_relation, qualifiers):
    """Token-overlap proxy for C1(b): of the material an arm's verb dropped from
    the verbatim relation, what share reappears in that arm's qualifiers.

    A proxy, not a judgment, and reported as one. Returns None when the verb
    dropped nothing (the verbatim relation was already a bare verb phrase).
    """
    dropped = dropped_material(relation_verbatim, arm_relation)
    if not dropped:
        return None
    bag = set()
    qualifiers = qualifiers or {}
    for key in QUALIFIER_KEYS:
        if qualifiers.get(key):
            bag |= content_tokens(qualifiers[key])
    return len(dropped & bag) / len(dropped)


# ------------------------------------------------------------------ C2 pools

# A reversal is only a corruption where the relation is asymmetric, so these
# are excluded from the direction-reversed class. Fixed before the draw.
SYMMETRIC_MARKERS = (
    'equivalent', 'synonym', 'parallel', 'identical', 'correspond',
    'associat', 'same-as', 'analog', 'coincid', 'interchange', 'akin',
    'related-to', 'connected', 'linked',
)

# The strengthening corruption replaces the verb with a flat identity claim, so
# relations that already assert identity are excluded from that class.
IDENTITY_MARKERS = SYMMETRIC_MARKERS + ('is-a', 'personif', 'identif')
STRENGTHENED_VERB = 'is-identical-to'


def is_symmetric(relation):
    r = (relation or '').lower()
    return any(m in r for m in SYMMETRIC_MARKERS)


def is_identity(relation):
    r = (relation or '').lower()
    if r in ('is', 'is-a', 'are'):
        return True
    return any(m in r for m in IDENTITY_MARKERS)


# ---------------------------------------------------------------- small io


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def append_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a') as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')


def load_state():
    path = WORK / 'state.json'
    if path.exists():
        return json.load(open(path))
    return {'study': 'C', 'chunks_done': [], 'c1_items_done': 0, 'c2': 'not-started'}


def save_state(state):
    WORK.mkdir(parents=True, exist_ok=True)
    json.dump(state, open(WORK / 'state.json', 'w'), indent=1)


if __name__ == '__main__':
    pop = load_population()
    print(f"population: {len(pop)} normalized edges")
    print(f"work dir:   {WORK}")
    print(f"receipts:   {DOCS}")
