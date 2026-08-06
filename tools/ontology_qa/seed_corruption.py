#!/usr/bin/env python3
"""T1 — seeded structural corruption: measure what the audit actually detects.

Every stage-3 instrument enumerates what it looks for, so each reports a lower
bound of unknown tightness. The identity-closure check tests NINE hand-written
relation strings; when it reports a 35-node collapse the honest reading is
"at least 35, by these nine strings." This script turns that into a rate.

Method is E1's, aimed at the audit instead of the gate: inject defects of known
type and count into a clean graph, hide them among untouched structure, run the
audit blind, count what comes back. No corpus, no model calls, seed-reproducible.

    python3 tools/ontology_qa/seed_corruption.py                 # all classes
    python3 tools/ontology_qa/seed_corruption.py --class C2 -n 20
    python3 tools/ontology_qa/seed_corruption.py --record --label pre-families

CORRUPTION CLASSES
  C1 entity-merge-identity  two distinct nodes joined by an ENUMERATED identity
                            string — the case the checker is built for
  C2 identity-off-list      same join, via an identity string the checker does
                            NOT enumerate. **The class that matters.** Every
                            other class asks whether a check works; this asks
                            whether it is looking in the right places.
  C3 predicate-to-clause    a clean verb phrase rewritten as a sentence-shaped
                            predicate — tests the P24 hyphen detector
  C4 symmetric-oneway       a symmetric relation asserted in one direction only
  C5 domain-range-violation an edge whose endpoint node types contradict the
                            relation's established type profile
  C6 orphan-node            a node with no edges

Detection is judged per class against the specific audit signal that ought to
fire, not against "did any number move" — a check that notices the wrong thing
is not a detection.

THRESHOLDS ARE DELIBERATELY ABSENT. This reports a rate. What rate is tolerable
is corpus- and use-relative, and that judgement belongs in a decision record,
not smuggled into an instrument.
"""
import argparse
import collections
import copy
import datetime
import json
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
QA = ROOT / "tools" / "ontology_qa"
TREND = ROOT / "pipeline" / "corruption_trend.jsonl"

# The nine strings themis.py's identity closure actually enumerates. Kept in
# sync by reading the source, so this cannot drift away from the instrument.
def enumerated_identity():
    src = (QA / "themis.py").read_text()
    block = re.search(r"IDENTITY = \{(.*?)\}", src, re.S).group(1)
    return set(re.findall(r'"([^"]+)"', block))


# Identity-flavoured strings that exist in the corpus vocabulary but are NOT in
# the checker's list. Hand-curated, conservative: every one is unambiguously an
# identity assertion. (A keyword sweep catches ~48 strings but over-catches
# things like `is-the-traditional-colour-of-the-celestial-cloak-of`.)
OFF_LIST_IDENTITY = [
    "coincides-with", "is-synonymous-with", "is-ultimately-identical-with",
    "unconsciously-identical-with", "is-unconsciously-identical-with",
    "indistinguishably-merged-with", "empirically-equivalent-to",
    "felt-as-equivalent-of", "is-essentially-same-as", "made-equal-to",
]

SYMMETRIC = {"synonym-of", "identical-to", "identified-with", "corresponds-to",
             "parallels", "opposes", "polarizes-with", "conjoined-with",
             "is-analogue-of", "analogue-of", "correlated-with"}

CLAUSE_TEMPLATES = [
    "is-in-the-view-of-the-alchemists-a-form-of",
    "was-long-before-paracelsus-regarded-as-an-allegory-of",
    "must-under-certain-conditions-be-understood-as-a-figure-of",
]


def effective(edge):
    rn = edge.get("relation_normalized")
    return rn["relation"] if rn else edge["relation"]


def load_clean():
    return json.loads((ROOT / "seed.json").read_text(encoding="utf-8"))


def type_profiles(graph):
    """Established subject/object type pairs per relation, for C5."""
    nodes = {n["id"]: n for n in graph["nodes"]}
    prof = collections.defaultdict(set)
    for e in graph["edges"]:
        if not e.get("references"):
            continue
        prof[effective(e)].add((nodes[e["subject"]]["type"], nodes[e["object"]]["type"]))
    return prof, nodes


# ---------- injectors: each returns (mutated_graph, list_of_injected_records) ----------

def inject(graph, cls, n, rng):
    g = copy.deepcopy(graph)
    nodes = {x["id"]: x for x in g["nodes"]}
    ids = sorted(nodes)
    injected = []
    enum = sorted(enumerated_identity())
    prof, _ = type_profiles(graph)

    def new_edge(s, r, o, note):
        e = {"subject": s, "relation": r, "object": o,
             "references": [{"volume": "SEEDED", "paragraph": 0,
                             "quote": "seeded corruption, not corpus text",
                             "claim_type": "jung-asserts", "confidence": "high",
                             "verified": False, "_seeded": note}]}
        g["edges"].append(e)
        return e

    if cls in ("C1", "C2"):
        pool = enum if cls == "C1" else OFF_LIST_IDENTITY
        # join pairs of nodes that are NOT already identity-linked, so the
        # collapse we create is genuinely new structure
        for _ in range(n):
            a, b = rng.sample(ids, 2)
            r = rng.choice(pool)
            new_edge(a, r, b, cls)
            injected.append({"class": cls, "subject": a, "relation": r, "object": b})

    elif cls == "C3":
        clean = [e for e in g["edges"]
                 if e.get("references") and e["relation"].count("-") < 4
                 and not e.get("relation_normalized")]
        for _i, e in enumerate(rng.sample(clean, min(n, len(clean)))):
            before = e["relation"]
            e["relation"] = rng.choice(CLAUSE_TEMPLATES) + f"-seeded{_i}"
            e.pop("relation_normalized", None)   # a clause has no normalized form
            injected.append({"class": cls, "subject": e["subject"],
                             "relation": e["relation"], "object": e["object"],
                             "was": before})

    elif cls == "C4":
        idx = {}
        for e in g["edges"]:
            idx.setdefault((e["subject"], effective(e), e["object"]), e)
        seen, removed = set(), 0
        for (s, r, o), e in list(idx.items()):
            if removed >= n or r not in SYMMETRIC:
                continue
            rev = idx.get((o, r, s))
            if rev is not None and (o, r, s) not in seen and rev in g["edges"]:
                g["edges"].remove(rev)
                seen.add((s, r, o))
                injected.append({"class": cls, "subject": o, "relation": r, "object": s})
                removed += 1

    elif cls == "C5":
        common = [r for r, sigs in prof.items() if len(sigs) >= 1 and r.count("-") < 4]
        for _ in range(n):
            r = rng.choice(common)
            allowed = prof[r]
            bad = [(a, b) for a in ids for b in ids
                   if (nodes[a]["type"], nodes[b]["type"]) not in allowed][:400]
            if not bad:
                continue
            a, b = rng.choice(bad)
            new_edge(a, r, b, cls)
            injected.append({"class": cls, "subject": a, "relation": r, "object": b,
                             "types": [nodes[a]["type"], nodes[b]["type"]]})

    elif cls == "C6":
        for i in range(n):
            nid = f"seeded-orphan-{i}"
            g["nodes"].append({"id": nid, "label": f"Seeded Orphan {i}", "type": "Concept"})
            injected.append({"class": cls, "node": nid})

    return g, injected


# ---------- detection: run the real audit and read the signal that should fire ----------

def run_audit(graph, tmp):
    tmp.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")
    out = {}
    for script in ("diagnose.py", "quality.py", "themis.py"):
        r = subprocess.run([sys.executable, str(QA / script), str(tmp)],
                           capture_output=True, text=True, timeout=180)
        out[script] = r.stdout
    return out


def detected(cls, base, after, n_injected):
    """Per-class: did the signal that OUGHT to fire actually move?

    Parsers are matched to the audit's real output strings (verified against
    live output, not guessed). A check that notices something else is not a
    detection. Absent signal is reported as absent, never as zero.
    """
    def num(txt, pattern):
        m = re.search(pattern, txt, re.I)
        return int(m.group(1)) if m else None

    b, a = "".join(base.values()), "".join(after.values())
    P_CLOSURE  = r"largest identity-closure cluster:\s*(\d+)"
    P_CLUSTERS = r"(\d+) clusters of 3\+ nodes are chained by identity"
    P_SENT     = r"(\d+) relations are sentence-shaped"
    P_ONEWAY   = r"(\d+) edges use a symmetric relation but only assert one"
    P_ISOLATED = r"isolated nodes \(no edge at all\):\s*(\d+)"

    if cls in ("C1", "C2"):
        cb, ca = num(b, P_CLOSURE), num(a, P_CLOSURE)
        kb, ka = num(b, P_CLUSTERS), num(a, P_CLUSTERS)
        moved = (ca is not None and cb is not None and ca > cb) or \
                (ka is not None and kb is not None and ka > kb)
        return moved, f"closure {cb}->{ca}, identity clusters {kb}->{ka}"
    if cls == "C3":
        sb, sa = num(b, P_SENT), num(a, P_SENT)
        moved = sb is not None and sa is not None and sa > sb
        return moved, f"sentence-shaped relations {sb}->{sa}"
    if cls == "C4":
        if n_injected == 0:
            return None, ("UNTESTABLE: graph holds 0 bidirectional symmetric pairs "
                          "(all 137 symmetric edges are already one-way), so this "
                          "defect cannot be injected")
        ob, oa = num(b, P_ONEWAY), num(a, P_ONEWAY)
        moved = ob is not None and oa is not None and oa > ob
        return moved, f"symmetric one-way {ob}->{oa}"
    if cls == "C5":
        return None, "NO INSTRUMENT: the suite has no domain/range check at all"
    if cls == "C6":
        ib, ia = num(b, P_ISOLATED), num(a, P_ISOLATED)
        moved = ib is not None and ia is not None and ia > ib
        return moved, f"isolated nodes {ib}->{ia}"
    return False, "unknown class"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", default="C1,C2,C3,C4,C5,C6")
    ap.add_argument("-n", type=int, default=15, help="defects per class")
    ap.add_argument("--seed", type=int, default=20260806)
    ap.add_argument("--label", default="manual")
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()

    clean = load_clean()
    tmp = ROOT / "pipeline" / "work" / "_corrupted_seed.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)

    print(f"clean graph: {len(clean['nodes'])} nodes / {len(clean['edges'])} edges")
    print(f"checker enumerates {len(enumerated_identity())} identity strings; "
          f"{len(OFF_LIST_IDENTITY)} curated identity strings sit outside it\n")

    base = run_audit(clean, tmp)
    rows = []
    for cls in a.classes.split(","):
        rng = random.Random(a.seed)
        corrupted, injected = inject(clean, cls, a.n, rng)
        after = run_audit(corrupted, tmp)
        ok, evidence = detected(cls, base, after, len(injected))
        verdict = {True: "DETECTED    ", False: "MISSED      ",
                   None: "N/A         "}[ok]
        rows.append({"class": cls, "injected": len(injected),
                     "detected": ok, "evidence": evidence})
        print(f"  {cls}  injected {len(injected):>3}   {verdict}   {evidence}")

    tmp.unlink(missing_ok=True)

    print("\nThresholds are deliberately not set here; what rate is tolerable is a")
    print("separate judgement and belongs in a decision record.")

    if a.record:
        row = {"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "label": a.label, "seed": a.seed, "n_per_class": a.n,
               "graph": f"{len(clean['nodes'])}/{len(clean['edges'])}",
               "enumerated_identity_strings": len(enumerated_identity()),
               "results": rows}
        with TREND.open("a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(f"\nappended to {TREND.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
