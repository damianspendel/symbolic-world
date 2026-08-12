#!/usr/bin/env python3
"""Gemini arm of the per-window family sweep.

RULES #23 — ported into the repository 2026-08-12 from the working copy that ran
windows 8, 9 and 10 out of a session scratchpad. Two changes on the port, both
mechanical: the key travels as a request header rather than a URL query
parameter (the convention pipeline/crossvendor_run.py already follows), and it
is read at call time instead of at import. Neither touches what the arm is asked.

BLIND. This arm reads exactly two things: pipeline/work/family_sweep_input.json
and docs/FAMILY_DEFINITIONS.md. It never reads the other arm's output, seed.json,
the queue, or any tracked metric. The Opus arm runs under
pipeline/family/OPUS_ARM_PROMPT.md with the same blindness in the other
direction.

Run from anywhere:  python3 pipeline/family/sweep_gemini.py
"""
import argparse
import json
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
KEY_PATH = ROOT / "pipeline" / "work" / "gemini.key"
MODEL = "gemini-3.1-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

DEFS = (ROOT / "docs" / "FAMILY_DEFINITIONS.md").read_text(encoding="utf-8")

PROMPT = """You are one blind arm of a two-arm relation-family classification for a knowledge graph of C.G. Jung's Collected Works. Below is the complete, binding family definitions document, then a list of verified edges. For EACH edge, assign exactly one family from the document's inventory, or "unclassified(no-family)" if no family covers it, or "text-undecided" if the quoted text itself hedges between families. Judge from the relation string, the node types, and the quotes. Apply the document's boundary rules exactly as written.

Respond with ONLY a JSON array, one object per edge, in the same order:
[{"n": <n>, "family": "<family>", "confidence": "sure"|"unsure", "reason": "<one line>"}]

=== FAMILY DEFINITIONS (binding) ===
""" + DEFS + """
=== EDGES ===
"""


def call(items, attempt_max=8):
    """One chunk. The response must cover exactly the n's sent — a short set and
    an invented n are both retried, never accepted (the superset rule that
    pipeline/crossvendor_run.py adopted 2026-08-12)."""
    body = json.dumps({
        "contents": [{"parts": [{"text": PROMPT + json.dumps(items, ensure_ascii=False, indent=1)}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
    }).encode()
    want = {i["n"] for i in items}
    for attempt in range(1, attempt_max + 1):
        try:
            req = urllib.request.Request(
                URL, data=body,
                headers={"Content-Type": "application/json",
                         # read at call time; header only; never printed
                         "x-goog-api-key": KEY_PATH.read_text(encoding="utf-8").strip()})
            with urllib.request.urlopen(req, timeout=300) as r:
                out = json.load(r)
            rows = json.loads(out["candidates"][0]["content"]["parts"][0]["text"])
            got = {r["n"] for r in rows if isinstance(r, dict) and "n" in r}
            if got != want:
                raise ValueError(f"covers {len(got & want)}/{len(want)} and invents "
                                 f"{len(got - want)}")
            return [r for r in rows if r["n"] in want]
        except Exception as e:                       # noqa: BLE001 — retry anything
            wait = 30 * attempt
            print(f"  attempt {attempt}: {e.__class__.__name__} {e}; retry in {wait}s",
                  flush=True)
            time.sleep(wait)
    raise SystemExit("chunk failed after retries — hold the window, do not merge")


def main(inp_path, out_path, chunk):
    edges = json.loads(inp_path.read_text())["edges"]
    rows = []
    for c in range(0, len(edges), chunk):
        part = edges[c:c + chunk]
        print(f"chunk {c // chunk + 1}: {len(part)} edges", flush=True)
        rows += call(part)
    out_path.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    print(f"wrote {out_path.relative_to(ROOT)}: {len(rows)} rows")


if __name__ == "__main__":
    W = ROOT / "pipeline" / "work"
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(W / "family_sweep_input.json"))
    ap.add_argument("--out", default=str(W / "family_sweep_gemini.json"))
    ap.add_argument("--chunk", type=int, default=24)
    a = ap.parse_args()
    main(pathlib.Path(a.input), pathlib.Path(a.out), a.chunk)
