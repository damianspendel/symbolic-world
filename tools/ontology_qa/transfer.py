#!/usr/bin/env python3
"""Measure relation-vocabulary transfer from one body of the corpus to another.

The question this answers: when mining moves into a new volume, does it reuse the
relation vocabulary the earlier volumes established, or mint new strings? That is the
evidence behind the relation-family scope decision (docs/PROPOSAL_RELATION_TYPING.md).

Usage — ALWAYS pass --window and --as-of for a batch figure:
    python3 tools/ontology_qa/transfer.py --as-of 40dee7f --target 9ii \
            --window 1-69 --since 2026-08-05 --label b-cw9ii-1 --record
    python3 tools/ontology_qa/transfer.py --as-of 31bc08b --target 9ii \
            --window 70-138 --since 2026-08-05 --label b-cw9ii-2 --record
    python3 tools/ontology_qa/transfer.py --show

TWO TRAPS THAT BOTH PRODUCE A PLAUSIBLE WRONG NUMBER, SILENTLY:

1. Date does not identify a batch. b-cw9ii-1 and b-cw9ii-2 were both verified
   2026-08-05, so `--since 2026-08-05` alone pools them and returns 116 edges at
   16.4% — a figure belonging to neither (they are 24/70.8% and 92/2.2%). Use --window.
2. A batch's figures are not stable under later merges. Attaches add references to
   older edges and retroactively change window membership: b-cw9ii-1 reads 70.8% at its
   own merge and 72.7% at HEAD, because b-cw9ii-2 attached 8 references into §1-69's
   edges. Use --as-of for anything recorded.

READ THIS BEFORE TRUSTING ANY HEADLINE NUMBER. Three different rates are computed and
they answer different questions:

- string reuse UNDER-reports transfer, because the premise of the family layer is that
  distinct strings collapse into few families;
- family fit is the metric that decides the scope question, computed over WELL-FORMED
  predicates only (pre-registered ruling, docs/PROPOSAL_RELATION_TYPING.md 2026-08-05);
- clause-predicate rate is reported first-class, because a batch minting clauses
  inflates 'new strings' with things that are not relations at all. b-cw9ii-2 minted 90
  strings for 92 edges at an 83.7% clause rate — reuse there is not a vocabulary signal.

Never pool these. A batch can be healthy on family fit and catastrophic on clauses.

Read-only with respect to the graph. Writes only pipeline/transfer_trend.jsonl, and
only with --record.

Read-only with respect to the graph. Writes only pipeline/transfer_trend.jsonl, and
only with --record.
"""
import argparse
import subprocess
import collections
import datetime
import json
import pathlib
import sys
from math import comb

ROOT = pathlib.Path(__file__).resolve().parents[2]
TREND = ROOT / "pipeline" / "transfer_trend.jsonl"

# kept identical to quality.py's P24 check, so the two never disagree
SENTENCE_SHAPED_MIN_HYPHENS = 4


def volumes(edge):
    return {str(r["volume"]) for r in edge["references"]}


def dates(edge):
    return {str(r.get("verified_date") or "") for r in edge["references"]}


def paragraphs(edge):
    return [int(r["paragraph"]) for r in edge["references"]]


def is_sentence_shaped(relation):
    return relation.count("-") >= SENTENCE_SHAPED_MIN_HYPHENS


def fisher_exact_two_sided(a, b, c, d):
    """Two-sided Fisher exact test on a 2x2 table. Returns the p-value.

    Small counts are the norm here (one mining window is ~20-30 edges), so an exact
    test rather than a chi-square approximation.
    """
    def p_table(w, x, y, z):
        return comb(w + x, w) * comb(y + z, y) / comb(w + x + y + z, w + y)

    observed = p_table(a, b, c, d)
    total = 0.0
    for i in range(0, min(a + b, a + c) + 1):
        j, k, l = a + b - i, a + c - i, d - a + i
        if j < 0 or k < 0 or l < 0:
            continue
        p = p_table(i, j, k, l)
        if p <= observed + 1e-12:
            total += p
    return total


def baseline_vocabulary(edges, baseline_vols):
    """Relation strings appearing on any edge that cites the baseline volumes.

    'Touching' rather than 'entirely within': an edge citing both CW 14 and CW 9ii
    still demonstrates that the string was available in the baseline body.
    """
    vocab = collections.Counter()
    for e in edges:
        if volumes(e) & baseline_vols:
            vocab[e["relation"]] += 1
    return vocab


def select_target(edges, target_vol, since, window=None):
    """Edges wholly inside the target volume, at or after `since`, inside `window`.

    Wholly, on purpose. An edge with an older reference is an ATTACH to pre-existing
    material, not vocabulary minted by this batch, and counting attaches inflates reuse.

    PREFER --window. Date alone does not identify a batch: b-cw9ii-1 and b-cw9ii-2 were
    both verified 2026-08-05, so `--since 2026-08-05` silently pools them and returns a
    figure belonging to neither (116 edges, 16.4%, versus 24/70.8% and 92/2.2%). A batch
    is defined by its paragraph window; select on that.
    """
    lo, hi = window if window else (None, None)
    new, attaches = [], []
    for e in edges:
        vols, dts = volumes(e), dates(e)
        if target_vol not in vols:
            continue
        if lo is not None:
            paras = [int(r["paragraph"]) for r in e["references"]
                     if str(r["volume"]) == target_vol]
            if not paras or not all(lo <= p <= hi for p in paras):
                continue
        if vols == {target_vol} and all(d >= since for d in dts):
            new.append(e)
        elif any(d >= since for d in dts):
            attaches.append(e)
    return new, attaches


def measure(edges, baseline_vols, target_vol, since, split, families, window=None):
    vocab = baseline_vocabulary(edges, baseline_vols)
    new, attaches = select_target(edges, target_vol, since, window)

    reused = [e for e in new if e["relation"] in vocab]
    minted = [e for e in new if e["relation"] not in vocab]
    minted_strings = sorted({e["relation"] for e in minted})

    result = {
        "baseline_volumes": sorted(baseline_vols),
        "baseline_vocab_size": len(vocab),
        "target_volume": target_vol,
        "since": since,
        "new_edges": len(new),
        "attaches": len(attaches),
        "reused_edges": len(reused),
        "minted_edges": len(minted),
        "reuse_pct": round(100 * len(reused) / len(new), 1) if new else 0.0,
        "minted_strings": minted_strings,
        "sentence_shaped_new": sum(1 for e in new if is_sentence_shaped(e["relation"])),
        "reused_string_counts": collections.Counter(
            e["relation"] for e in reused).most_common(),
    }

    if split is not None:
        below = [e for e in new if max(paragraphs(e)) < split]
        above = [e for e in new if max(paragraphs(e)) >= split]
        rb = sum(1 for e in below if e["relation"] in vocab)
        ra = sum(1 for e in above if e["relation"] in vocab)
        result["split"] = {
            "at_paragraph": split,
            "below": {"edges": len(below), "reused": rb,
                      "pct": round(100 * rb / len(below), 1) if below else 0.0},
            "above": {"edges": len(above), "reused": ra,
                      "pct": round(100 * ra / len(above), 1) if above else 0.0},
            "fisher_p": round(
                fisher_exact_two_sided(rb, len(below) - rb, ra, len(above) - ra), 5)
            if below and above else None,
        }

    # Family fit is the metric that actually decides the scope question. Until a
    # definitions file exists there is nothing to fit against, so this stays a held
    # slot rather than a fabricated number.
    #
    # Reported at EDGE level as the headline and at minted-STRING level as a
    # diagnostic. The two differ a lot and conflating them is easy: on b-cw9ii-1 the
    # edge-level figure is 22/24 (92%) while the minted-string figure is 4/6 (67%),
    # because one minted string can carry several edges and the reused-string edges
    # are already in families. Threshold the edge-level number; at n=6 a single
    # string moves the string-level number 17 points, which is too noisy to gate on.
    if families:
        assigned = {s for fam in families.get("families", {}).values()
                    for s in fam.get("members", [])}
        # PRE-REGISTERED RULING, docs/PROPOSAL_RELATION_TYPING.md 2026-08-05:
        # clause-predicates are `not-a-relation` and leave the family-fit denominator.
        # They are NOT `unclassified` — that word is a claim about the vocabulary, and
        # this is a claim about the edge. The screen here is the mechanical one (P24,
        # >=4 hyphen tokens); the semantic test is a human/gate call the script cannot
        # make, so this figure is an upper bound on the clause count and is labelled so.
        wellformed = [e for e in new if not is_sentence_shaped(e["relation"])]
        placed_edges = [e for e in wellformed
                        if e["relation"] in vocab or e["relation"] in assigned]
        fit_strings = [s for s in minted_strings if s in assigned]
        result["family_fit"] = {
            "edges_placed": len(placed_edges),
            "edges_total": len(wellformed),
            "edges_excluded_not_a_relation": len(new) - len(wellformed),
            "edge_pct": round(100 * len(placed_edges) / len(wellformed), 1) if wellformed else 0.0,
            "minted_strings": len(minted_strings),
            "minted_strings_placed": len(fit_strings),
            "minted_string_pct": round(
                100 * len(fit_strings) / len(minted_strings), 1) if minted_strings else 0.0,
            "unplaced": [s for s in minted_strings if s not in assigned],
        }
    else:
        result["family_fit"] = None

    # minted strings staged with their evidence, in the shape the family gate consumes
    result["minted_detail"] = [
        {
            "relation": e["relation"],
            "subject": e["subject"],
            "object": e["object"],
            "paragraphs": paragraphs(e),
            "quote": e["references"][0]["quote"],
            "claim_type": e["references"][0].get("claim_type"),
        }
        for e in minted
    ]
    return result


def report(r):
    print(f"\n=== vocabulary transfer: CW {r['target_volume']} since {r['since']} ===")
    print(f"baseline: CW {', '.join(r['baseline_volumes'])} "
          f"({r['baseline_vocab_size']} distinct relation strings)\n")
    print(f"  new edges           {r['new_edges']}   (+{r['attaches']} attaches, excluded)")
    print(f"  reuse a baseline    {r['reused_edges']}   = {r['reuse_pct']}%")
    print(f"  mint a new string   {r['minted_edges']}   "
          f"({len(r['minted_strings'])} distinct)")
    sn = r['sentence_shaped_new']
    pct = 100 * sn / r['new_edges'] if r['new_edges'] else 0
    print(f"  CLAUSE-PREDICATES   {sn}   = {pct:.1f}%   "
          f"(P24 screen, >={SENTENCE_SHAPED_MIN_HYPHENS} hyphen tokens)")
    if pct >= 25:
        print("      ^ above 25%: read the reuse figure with care. A batch minting "
              "clauses\n        inflates 'new strings' with things that are not "
              "relations at all.")

    if r["minted_strings"]:
        print("\n  minted strings:")
        for m in r["minted_detail"]:
            print(f"    {m['relation']:<24} {m['subject']} -> {m['object']}  "
                  f"§{','.join(str(p) for p in m['paragraphs'])}")

    if r["reused_string_counts"]:
        top = ", ".join(f"{s} ({c})" for s, c in r["reused_string_counts"][:8])
        print(f"\n  reused: {top}")

    s = r.get("split")
    if s:
        print(f"\n  --- stratified at §{s['at_paragraph']} ---")
        print(f"    below  §{s['at_paragraph']:<5} {s['below']['reused']}/{s['below']['edges']}"
              f"  = {s['below']['pct']}%")
        print(f"    at/above §{s['at_paragraph']:<3} {s['above']['reused']}/{s['above']['edges']}"
              f"  = {s['above']['pct']}%")
        if s["fisher_p"] is not None:
            print(f"    Fisher exact, two-sided: p = {s['fisher_p']}")

    ff = r.get("family_fit")
    if ff:
        print(f"\n  FAMILY FIT (headline, edge level, well-formed only)  "
              f"{ff['edges_placed']}/{ff['edges_total']} = {ff['edge_pct']}%")
        print(f"  excluded as not-a-relation          "
              f"{ff['edges_excluded_not_a_relation']}")
        print(f"  minted strings placed (diagnostic)  "
              f"{ff['minted_strings_placed']}/{ff['minted_strings']} "
              f"= {ff['minted_string_pct']}%")
        if ff["unplaced"]:
            print(f"    unplaced: {', '.join(ff['unplaced'])}")
    else:
        print("\n  FAMILY FIT  not computed — no --families definitions file supplied.")
        print("    String reuse UNDER-reports transfer; family fit is the deciding metric.")
        print("    The minted strings above are staged with quotes for that judgement.")


def rows():
    if not TREND.exists():
        return []
    return [json.loads(l) for l in TREND.read_text().splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seed", nargs="?", default=str(ROOT / "seed.json"))
    ap.add_argument("--as-of", dest="as_of", metavar="COMMIT",
                    help="measure against seed.json AT THIS COMMIT instead of the working "
                         "tree. USE THIS FOR TREND ROWS. A batch's figures are not stable "
                         "under later merges: attaches add references to older edges and "
                         "retroactively change window membership. b-cw9ii-1 reads 70.8%% "
                         "at its own merge (40dee7f) and 72.7%% at HEAD, because "
                         "b-cw9ii-2 attached 8 references into §1-69's edges.")
    ap.add_argument("--baseline", default="12,13,14",
                    help="comma-separated baseline volumes (default: the trilogy)")
    ap.add_argument("--target", help="target volume, e.g. 9ii")
    ap.add_argument("--since", default="",
                    help="only count edges whose references are all verified on/after "
                         "this ISO date, e.g. 2026-08-05")
    ap.add_argument("--window", help="paragraph window LO-HI, e.g. 70-138. PREFER THIS: "
                    "date alone does not identify a batch (b-cw9ii-1 and b-cw9ii-2 share "
                    "2026-08-05 and pool silently without it)")
    ap.add_argument("--split", type=int,
                    help="paragraph number to stratify on; runs a Fisher exact test")
    ap.add_argument("--families", help="path to a family definitions JSON, once one exists")
    ap.add_argument("--label", default="manual", help="batch id, e.g. b-cw9ii-2")
    ap.add_argument("--record", action="store_true",
                    help="append the row to pipeline/transfer_trend.jsonl")
    ap.add_argument("--show", action="store_true", help="print history, measure nothing")
    a = ap.parse_args()

    if a.show:
        history = rows()
        if not history:
            print("no transfer rows yet")
            return
        for r in history:
            s = r.get("split") or {}
            extra = (f"  split §{s['at_paragraph']}: {s['below']['pct']}% / "
                     f"{s['above']['pct']}%  p={s['fisher_p']}") if s else ""
            print(f"{r['label']:<12} CW{r['target_volume']:<5} "
                  f"{r['reused_edges']}/{r['new_edges']} = {r['reuse_pct']}%  "
                  f"minted {len(r['minted_strings'])}{extra}")
        return

    if not a.target:
        ap.error("--target is required (e.g. --target 9ii)")

    if a.as_of:
        proc = subprocess.run(["git", "show", f"{a.as_of}:seed.json"],
                              capture_output=True, text=True, cwd=ROOT)
        if proc.returncode:
            sys.exit(f"cannot read seed.json at {a.as_of}: {proc.stderr.strip()}")
        graph = json.loads(proc.stdout)
    else:
        graph = json.loads(pathlib.Path(a.seed).read_text(encoding="utf-8"))
    families = json.loads(pathlib.Path(a.families).read_text()) if a.families else None

    win = None
    if a.window:
        lo, hi = a.window.split("-")
        win = (int(lo), int(hi))
    r = measure(graph["edges"], set(a.baseline.split(",")), a.target, a.since,
                a.split, families, win)
    r["window"] = a.window or ""
    if not r["new_edges"]:
        print(f"no edges matched CW {a.target} since '{a.since}' — nothing to measure")
        sys.exit(1)

    report(r)

    if a.record:
        r["ts"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        r["label"] = a.label
        r.pop("minted_detail", None)  # keep the trend file small; detail is re-derivable
        TREND.parent.mkdir(parents=True, exist_ok=True)
        with TREND.open("a") as fh:
            fh.write(json.dumps(r) + "\n")
        print(f"\nappended to {TREND.relative_to(ROOT)} ({len(rows())} rows)")


if __name__ == "__main__":
    main()
