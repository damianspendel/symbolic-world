#!/usr/bin/env python3
"""Wikidata candidates for figures, source authors and source texts (v3.0.0 item 1).

  python3 tools/linking/wikidata_candidates.py [--limit N]

Reads seed.json at the v2.4.0 tag. For every Figure node, every distinct
source_author and every distinct source_text it asks Wikidata's public search
(wbsearchentities, English) for up to seven items, then fetches each
candidate's description and "instance of" (P31) labels. Writes
pipeline/work/wikidata/candidates.json. Nothing is linked here: a proposer picks
one candidate or none, a checker from another model family judges the pick, and
Damian spot-checks a sample (tools/linking/README.md).

Sends only the public labels. Generic author strings ("the alchemists",
"other") are skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "pipeline", "work", "wikidata", "candidates.json")
API = "https://www.wikidata.org/w/api.php"
UA = "SymbolicWorldLinker/0.1 (research dataset; https://symbolicworld.observer)"
GENERIC = {"the alchemists", "other", "the gnostics", "the church fathers", "chinese alchemy"}


def api(**params):
    params.update(format="json")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:  # noqa: BLE001 - retry on any network error, then give up
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"Wikidata did not answer: {params}")


def targets():
    seed = json.loads(subprocess.run(["git", "show", "v2.4.0:seed.json"], cwd=ROOT,
                                     capture_output=True, check=True).stdout)
    out = [{"kind": "figure", "key": n["id"], "label": n["label"]} for n in seed["nodes"] if n["type"] == "Figure"]
    for field, kind in (("source_author", "author"), ("source_text", "text")):
        seen = sorted({r[field] for e in seed["edges"] for r in e["references"] if r.get(field)})
        out += [{"kind": kind, "key": s, "label": s} for s in seen if s.lower() not in GENERIC]
    return out


def search_terms(t):
    """The label first, then its variants: either side of a slash, the part in
    brackets, without a leading "The", and the node id as words."""
    label = t["label"]
    terms = [label.split(" (")[0].split(" / ")[0].strip()]
    terms += [x.strip() for x in label.split(" (")[0].split(" / ")[1:]]
    if " (" in label:
        inner = label.split(" (", 1)[1].rstrip(")").strip()
        if not inner.lower().startswith(("as ", "c. ")):
            terms.append(inner)
    terms += [x[4:] for x in terms if x.lower().startswith("the ")]
    if t["kind"] == "figure":
        terms.append(t["key"].replace("-", " "))
    seen, out = set(), []
    for x in terms:
        if x and x.lower() not in seen and len(x) < 80:
            seen.add(x.lower())
            out.append(x)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    items = targets()[: args.limit or None]
    for t in items:
        t["search"] = search_terms(t)
        t["candidates"], seen = [], set()
        for term in t["search"]:
            hits = api(action="wbsearchentities", search=term, language="en", type="item", limit=5)
            for h in hits.get("search", []):
                if h["id"] not in seen:
                    seen.add(h["id"])
                    t["candidates"].append({"qid": h["id"], "label": h.get("label"),
                                            "description": h.get("description"), "found_by": term})
            time.sleep(0.2)
    qids = sorted({c["qid"] for t in items for c in t["candidates"]})
    p31 = {}
    for i in range(0, len(qids), 50):
        ents = api(action="wbgetentities", ids="|".join(qids[i:i + 50]), props="claims")["entities"]
        for q, ent in ents.items():
            p31[q] = [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id")
                      for c in ent.get("claims", {}).get("P31", [])]
        time.sleep(0.2)
    classes = sorted({c for v in p31.values() for c in v if c})
    names = {}
    for i in range(0, len(classes), 50):
        ents = api(action="wbgetentities", ids="|".join(classes[i:i + 50]), props="labels", languages="en")["entities"]
        names.update({q: e.get("labels", {}).get("en", {}).get("value", q) for q, e in ents.items()})
        time.sleep(0.2)
    for t in items:
        for c in t["candidates"]:
            c["instance_of"] = [names.get(q, q) for q in p31.get(c["qid"], []) if q]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"source": "wikidata wbsearchentities + wbgetentities", "fetched": time.strftime("%Y-%m-%d"),
               "targets": items}, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"{len(items)} targets, {sum(len(t['candidates']) for t in items)} candidates, "
          f"{sum(1 for t in items if not t['candidates'])} with none -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
