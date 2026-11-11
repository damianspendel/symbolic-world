#!/usr/bin/env python3
"""Self-check for a trilogy-pass candidates file, run by the miner before it reports back.

Prints one line per problem, then totals and the minted-node dictionary. Covers the standing checks of the
per-window self-checks (existing_edge flags against the whole graph, unknown nodes, minted ids that already
exist, verbatim quotes, the 25-token cap, one ellipsis, closed sets) and the rulings of 2026-11-11: a quote
already in the graph on the same paragraph (ALREADY QUOTED), source_author and source_text on quoted and
reported claims against the controlled list (SOURCE), the names list (NAME), the cross-register flag (FLAG), and the stage data (STAGE, stages_note).

Run from the repo root:  python3 pipeline/mining/selfcheck_trilogy.py <volume> <N>
"""
import json
import re
import sys
import unicodedata

V, N = sys.argv[1], sys.argv[2]
W = "pipeline/work/"
inp = json.load(open(W + f"b-cw{V}-{N}_input.json", encoding="utf-8"))
cand = json.load(open(W + f"b-cw{V}-{N}_candidates.json", encoding="utf-8"))
seed = json.load(open("seed.json", encoding="utf-8"))
SRC = json.load(open("pipeline/mining/sources_controlled.json", encoding="utf-8"))
AUTHORS = set(SRC["authors"]) | set(SRC["traditions"]) | set(SRC["variants"])
TEXTS = set(SRC["texts"]) | set(SRC["variants"])
STG = json.load(open("pipeline/mining/stages_controlled.json", encoding="utf-8"))
STAGES, OPERATIONS, STAGE_RELS = set(STG["stages"]) | set(STG["dorn_stages"]), set(STG["operations"]), set(STG["relations"])
paras = {p["paragraph"]: p["text"] for p in inp["paragraphs"]}
vocab = {l.split("|")[0] for l in inp["vocabulary"]}
TYPES = {"Concept", "Figure", "Motif", "Operation", "Substance", "Symbol"}
CLAIMS = {"jung-asserts", "jung-reports-parallel", "jung-quotes-source"}
existing = {(e["subject"], e["relation"], e["object"]) for e in seed["edges"]}
have = {(e["subject"], e["relation"], e["object"], str(r["volume"]), r["paragraph"])
        for e in seed["edges"] for r in e["references"]}


def words(s):
    return re.findall(r"[a-z]+", s.lower())


def fold(s):
    return " ".join(unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().split())


quoted = {}
for e in seed["edges"]:
    for r in e["references"]:
        quoted.setdefault((str(r["volume"]), r["paragraph"]), []).append(tuple(words(r["quote"])))


def already_quoted(q, para):
    toks = tuple(x for part in re.split(r"\.\.\.|…", q) for x in words(part))
    for old in quoted.get((V, para), []):
        if len(toks) <= len(old) and any(old[i:i + len(toks)] == toks for i in range(len(old) - len(toks) + 1)):
            return True
    return False


seen = set(); nrefs = 0; minted = {}; flagged = 0
for c in cand["candidates"]:
    t = (c["subject"], c["relation"], c["object"])
    toks = c["relation"].split("-")
    if len(toks) > 4: print("REL LONG", t)
    if (t in existing) != bool(c.get("existing_edge")): print("FLAG existing_edge should be", t in existing, t)
    if "cross_register" in c and not isinstance(c["cross_register"], bool): print("FLAG cross_register not boolean", t)
    if c["relation"] == "stage-of" and c["object"] not in STAGES: print("STAGE stage-of must point at a stage id", t)
    if c["relation"] in ("precedes", "follows") and not ({c["subject"], c["object"]} <= STAGES | OPERATIONS): print("STAGE precedes/follows joins stage or operation ids only", t)
    flagged += 1 if c.get("cross_register") is True else 0
    for n in c.get("new_nodes", []):
        minted[n["id"]] = n.get("type")
        if n["id"] in vocab: print("MINT DUP", n["id"])
        if n.get("type") not in TYPES: print("BAD TYPE", n)
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n["id"]): print("BAD ID", n["id"])
    for x in (c["subject"], c["object"]):
        if x not in vocab and x not in minted: print("UNKNOWN", x, t)
    for r in c["references"]:
        nrefs += 1
        k = (t, r["paragraph"])
        if k in seen: print("DUP PAIR", k)
        seen.add(k)
        if t + (V, r["paragraph"]) in have: print("ALREADY CITED", k)
        if r["paragraph"] not in paras: print("OUT OF WINDOW", k); continue
        text = paras[r["paragraph"]]
        q = r["quote"]
        parts = q.split(" ... ") if " ... " in q else [q]
        if q.count("...") > 1: print("ELLIPSES", t)
        pos = 0
        for p in parts:
            i = text.find(p, pos)
            if i < 0: print("NOT VERBATIM", r["paragraph"], repr(p[:60]))
            else: pos = i + len(p)
        n = len(words(q))
        if n > 25: print("LONG", n, r["paragraph"], t)
        if already_quoted(q, r["paragraph"]): print("ALREADY QUOTED (attach rule: pick another sentence or attach without a new quote)", k)
        if r.get("claim_type") not in CLAIMS: print("BAD CLAIM TYPE", k)
        if r.get("claim_type") == "jung-quotes-source" and not r.get("source"): print("NOSRC", t)
        if r.get("claim_type") in ("jung-quotes-source", "jung-reports-parallel"):
            a, x = r.get("source_author"), r.get("source_text")
            if not a and not x: print("SOURCE missing source_author/source_text", k)
            if a and a != "other" and a not in AUTHORS: print("SOURCE author not in list (use 'other' + source)", a, k)
            if x and x != "other" and x not in TEXTS: print("SOURCE text not in list (use 'other' + source)", x, k)
            if (a == "other" or x == "other") and not r.get("source"): print("SOURCE 'other' without free-text source", k)
        if r.get("confidence") not in ("high", "medium", "low"): print("BAD CONFIDENCE", k)
        if str(r.get("volume")) != V: print("BAD VOLUME", k)
for nm in cand.get("names", []):
    node, para = nm.get("node"), nm.get("paragraph")
    if node not in vocab and node not in minted: print("NAME unknown node", node)
    if para not in paras: print("NAME paragraph outside window", nm); continue
    vals = ([nm["latin"]] if nm.get("latin") else []) + list(nm.get("aliases") or [])
    if not vals: print("NAME without latin or aliases", nm)
    for v in vals:
        if fold(v) not in fold(paras[para]): print("NAME not in paragraph", para, repr(v))
if not str(cand.get("stages_note", "")).strip(): print("STAGES missing stages_note (required; 'none in this window' is valid)")
nstage = sum(1 for c in cand["candidates"] if c["relation"] in STAGE_RELS)
print("candidates", len(cand["candidates"]), "refs", nrefs, "names", len(cand.get("names", [])), "cross_register", flagged, "stage candidates", nstage)
print(minted)
