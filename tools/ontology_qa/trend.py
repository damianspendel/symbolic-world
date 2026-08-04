#!/usr/bin/env python3
"""Append one QA snapshot per mining pass, so graph health can be read as a trend.

Usage:
    python3 tools/ontology_qa/trend.py --label b-cw9ii-1
    python3 tools/ontology_qa/trend.py --show

Writes one JSON object per line to pipeline/qa_trend.jsonl and prints the
delta against the previous row. Read-only with respect to the graph.
"""
import argparse, collections, datetime, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TREND = ROOT / "pipeline" / "qa_trend.jsonl"
# kept identical to themis.py's set, so the two never report different numbers
IDENTITY = {"synonym-of", "identical-to", "identified-with", "is-identified-with",
            "identical-with", "equivalent-of", "is-equivalent-of", "alias-of",
            "is-the-equivalent-of"}
SYMMETRIC = {"synonym-of", "identical-to", "identified-with", "corresponds-to",
             "parallels", "opposes", "polarizes-with", "conjoined-with",
             "is-analogue-of", "analogue-of", "correlated-with"}
TAXONOMIC = {"is-a", "aspect-of", "is-aspect-of"}


def identity_closure_max(edges):
    """Largest component if identity-type relations were treated as transitive."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in edges:
        if e["relation"] in IDENTITY:
            a, b = find(e["subject"]), find(e["object"])
            if a != b:
                parent[a] = b
    sizes = collections.Counter(find(k) for k in parent)
    return max(sizes.values()) if sizes else 0


def script_totals(seed):
    """Run the two scoring scripts and lift their headline tallies."""
    out = {}
    here = pathlib.Path(__file__).parent
    try:
        t = subprocess.run([sys.executable, str(here / "themis.py"), str(seed)],
                           capture_output=True, text=True, timeout=120).stdout
        m = re.search(r"PASS (\d+)\s+PARTIAL (\d+)\s+FAIL (\d+)", t)
        if m:
            out["cq_pass"], out["cq_partial"], out["cq_fail"] = map(int, m.groups())
    except Exception as exc:
        out["cq_error"] = str(exc)
    try:
        q = subprocess.run([sys.executable, str(here / "quality.py"), str(seed)],
                           capture_output=True, text=True, timeout=120).stdout
        m = re.search(r"TOTAL: (\d+) critical, (\d+) important, (\d+) minor", q)
        if m:
            out["crit"], out["important"], out["minor"] = map(int, m.groups())
    except Exception as exc:
        out["pitfall_error"] = str(exc)
    return out


def snapshot(seed, label, window):
    d = json.loads(pathlib.Path(seed).read_text())
    nodes, edges = d["nodes"], d["edges"]
    refs = [r for e in edges for r in e.get("references", [])]
    rel = collections.Counter(e["relation"] for e in edges)
    hapax = [r for r, c in rel.items() if c == 1]
    sentence_strings = [r for r in rel if r.count("-") >= 4]
    sentence_edges = [e for e in edges if e["relation"].count("-") >= 4]

    pairs = {(e["subject"], e["relation"], e["object"]) for e in edges}
    oneway = [e for e in edges if e["relation"] in SYMMETRIC
              and (e["object"], e["relation"], e["subject"]) not in pairs]

    row = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "label": label,
        "window": window,
        "nodes": len(nodes),
        "edges": len(edges),
        "refs": len(refs),
        # vocabulary health — the numbers mining is expected to move
        "rel_distinct": len(rel),
        "rel_hapax": len(hapax),
        "rel_hapax_pct_vocab": round(100 * len(hapax) / len(rel), 1) if rel else 0,
        "sentence_strings": len(sentence_strings),
        "sentence_edges": len(sentence_edges),
        "sentence_edges_pct": round(100 * len(sentence_edges) / len(edges), 1) if edges else 0,
        # structural risks
        "symmetric_oneway": len(oneway),
        "identity_closure_max": identity_closure_max(edges),
        "taxonomic_edges": sum(1 for e in edges if e["relation"] in TAXONOMIC),
        "edges_zero_refs": sum(1 for e in edges if not e.get("references")),
        # evidence layer
        "refs_verified": sum(1 for r in refs if r.get("verified")),
        "refs_crossvendor": sum(1 for r in refs if r.get("crossvendor_checked")),
        "claim_types": dict(collections.Counter(r.get("claim_type") for r in refs)),
        "volumes": dict(collections.Counter(str(r.get("volume")) for r in refs)),
    }
    row.update(script_totals(seed))
    return row


WATCH = ["edges", "rel_distinct", "rel_hapax", "rel_hapax_pct_vocab",
         "sentence_edges", "sentence_edges_pct", "symmetric_oneway",
         "identity_closure_max", "cq_pass", "cq_fail", "crit"]


def rows():
    if not TREND.exists():
        return []
    return [json.loads(l) for l in TREND.read_text().splitlines() if l.strip()]


def show_delta(row, prev):
    print(f"\n=== QA trend: {row['label']} ({row['window']}) ===")
    print(f"{row['nodes']} nodes · {row['edges']} edges · {row['refs']} refs\n")
    w = max(len(k) for k in WATCH)
    for k in WATCH:
        now = row.get(k)
        if prev is None or k not in prev:
            print(f"  {k:<{w}}  {now}")
            continue
        diff = round(now - prev[k], 1)
        arrow = f"{diff:+g}" if diff else "="
        print(f"  {k:<{w}}  {prev[k]:>7} -> {now:<7} {arrow}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", nargs="?", default=str(ROOT / "seed.json"))
    ap.add_argument("--label", default="manual", help="batch id, e.g. b-cw9ii-1")
    ap.add_argument("--window", default="", help="paragraph window, e.g. CW9ii §1-69")
    ap.add_argument("--show", action="store_true", help="print history, record nothing")
    a = ap.parse_args()

    history = rows()
    if a.show:
        if not history:
            print("no trend rows yet")
            return
        keys = ["label"] + WATCH
        print(" | ".join(k[:14] for k in keys))
        for r in history:
            print(" | ".join(str(r.get(k, ""))[:14] for k in keys))
        return

    row = snapshot(a.seed, a.label, a.window)
    TREND.parent.mkdir(parents=True, exist_ok=True)
    with TREND.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    show_delta(row, history[-1] if history else None)
    print(f"\nappended to {TREND.relative_to(ROOT)} ({len(history) + 1} rows)")


if __name__ == "__main__":
    main()
