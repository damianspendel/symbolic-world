#!/usr/bin/env python3
"""Gemini arm of the full relation-family assignment pass (1146 edges).

Adapted from pipeline/work/classify_gemini.py (the 60-item step-0 sample) to
the full pipeline/work/family_pass_input.json under docs/FAMILY_DEFINITIONS.md
v0.5. Sends the definitions doc plus a chunk of edges each request; classifies
the EFFECTIVE relation in its edge context. Resumable, retries failed chunks,
records chunks that never succeed instead of losing them silently.

Moved into tracked code 2026-08-12 (RULES #23) with one behavioural fix: a chunk
recorded in the failures file used to stay skipped on every later run unless
someone hand-edited that file, so a hole in the pass was permanent and nothing
downstream was forced to notice it. Failures are now a LOG — a rerun retries
them, and an entry is cleared when its chunk finally succeeds.

The PROMPT below is frozen as it ran: it names v0.5 and summarizes that
version's four adjudication refinements, which is the record of what the
1,146-edge pass was actually asked. Re-running it against a later ruleset means
rewriting that summary first — the prompt is not automatically valid for v0.6.

Run from the repo root:  python3 pipeline/family/classify_gemini_full.py
"""
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.chdir(ROOT)                       # every path below is repo-root-relative

MODEL = "gemini-3.1-pro-preview"
KEY_PATH = "pipeline/work/gemini.key"      # read at call time, header only


def api_key():
    return open(KEY_PATH, encoding="utf-8").read().strip()


INPUT_PATH = "pipeline/work/family_pass_input.json"
DEFS_PATH = "docs/FAMILY_DEFINITIONS.md"
OUT_PREFIX = "pipeline/work/family_pass_gemini_c"
FAILURES_PATH = "pipeline/work/family_pass_gemini_failures.json"

CHUNK = 40
MAX_ATTEMPTS = 3

DEFS = open(DEFS_PATH, encoding="utf-8").read()

PROMPT = """You are classifying edges of a knowledge graph of C.G. Jung's Collected Works into relation families. This is the Gemini arm of a two-model blind pass (an Opus arm runs independently, in parallel; you cannot see its answers and it cannot see yours). The definitions document below, v0.5, is BINDING for this pass.

Classify the EFFECTIVE relation (`relation_effective`) in its full edge context: subject, subject_type, object, object_type, qualifiers, layer, and the refs (each with volume, paragraph, claim_type, quote). `relation` is the frozen verbatim string and is context only — do not classify it directly. Qualifiers can be decisive (carrier, scope, condition, modality, note); read them before assigning.

For each edge assign exactly ONE value:
- one of the family names from "## The families" below, given EXACTLY as the document's own heading text (e.g. "symbolization", "archetypal-identity" — strip the leading number and any parenthetical note), or
- "unclassified(no-family)" — it is a well-formed relation but no family in the vocabulary fits, or
- "unclassified(text-undecided)" — the TEXT itself hedges between two family readings (e.g. "identical or at least connected with").

Never invent a family name. If you are unsure whether a candidate name matches the document, it does not — fall back to unclassified(no-family).

Apply the four v0.5 adjudication refinements (documented in full under "The first adjudication run" below; summarized here as a reminder, not a replacement for reading them):
1. The referent decides identity vs classification vs symbolization — the relation string never decides the family, the edge in its paragraph does. A hermeneutic/doctrinal emphasis tips even a literal "symbolizes" string into doctrinal-attribution.
2. A process classifies by its stated terminus, not its mechanism (e.g. a "dissolves-into" edge whose text states the resulting unity is `union`, not `separation`).
3. Transcendence is position, not lack: mere location beyond a boundary is structural-position; privation requires a stated absence or deficiency.
4. Characterization (how a thing appears, not what it contains or is) has no family — that is the correct answer, not a gap to force-fit.

Weigh explicitly rather than defaulting: the direction test separating symbolization from manifestation; whether correspondence is genuinely right or merely least-bad (if you reach for it because nothing else fits, prefer unclassified(no-family)).

Respond with ONLY a JSON array, one entry per edge given, covering every n:
[{"n": <int>, "family": "<exact family heading, or unclassified(no-family), or unclassified(text-undecided)>", "confidence": "sure|unsure", "reason": "<one line; required for any unclassified or unsure>"}]

=== DEFINITIONS DOCUMENT (v0.5) ===
""" + DEFS + "\n=== END DEFINITIONS ==="


def run_one(items, out_path):
    body = {
        "contents": [{"parts": [{"text": PROMPT + "\n\nEDGES:\n" + json.dumps(items, ensure_ascii=False)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key()},
    )
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    try:
        results = json.loads(text)
    except json.JSONDecodeError:
        # Gemini occasionally drops the closing bracket despite finishReason STOP.
        results = json.loads(text.rstrip().rstrip(",") + "]")

    expected = {it["n"] for it in items}
    got = {r.get("n") for r in results if isinstance(r, dict)}
    if got != expected:
        raise KeyError(f"results cover {len(got)}/{len(expected)} items")

    json.dump(results, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    usage = resp.get("usageMetadata", {})
    print(f"  {out_path}: {len(results)} entries | tokens in/out: "
          f"{usage.get('promptTokenCount')}/{usage.get('candidatesTokenCount')}")


def chunk_ok(out_path, expected_ns):
    """A chunk file counts as done only if it parses and covers its edges."""
    if not os.path.exists(out_path):
        return False
    try:
        data = json.load(open(out_path, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    got = {r.get("n") for r in data if isinstance(r, dict)}
    return got >= expected_ns


def main():
    data = json.load(open(INPUT_PATH, encoding="utf-8"))
    edges = data["edges"]
    print(f"{len(edges)} edges to classify (input version {data.get('version')}, "
          f"definitions doc {len(DEFS)} chars, chunk size {CHUNK})")

    n_chunks = (len(edges) + CHUNK - 1) // CHUNK
    failures = []
    if os.path.exists(FAILURES_PATH):
        try:
            failures = json.load(open(FAILURES_PATH, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            failures = []
    if failures:
        print(f"{len(failures)} chunk(s) failed on a previous run "
              f"({sorted(f['chunk'] for f in failures)}) — retrying them")

    t_start = time.time()
    for c in range(n_chunks):
        idx = c + 1
        out_path = f"{OUT_PREFIX}{idx:02d}.json"
        part = edges[c * CHUNK:(c + 1) * CHUNK]
        expected_ns = {e["n"] for e in part}

        if chunk_ok(out_path, expected_ns):
            print(f"chunk {idx}/{n_chunks} ({out_path}): already done, skipping")
            continue

        print(f"chunk {idx}/{n_chunks}: {len(part)} edges (n={part[0]['n']}..{part[-1]['n']})")
        last_err = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                run_one(part, out_path)
                last_err = None
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                    json.JSONDecodeError, KeyError) as e:
                last_err = e
                code = getattr(e, "code", type(e).__name__)
                if attempt == MAX_ATTEMPTS:
                    print(f"  chunk {idx}/{n_chunks} FAILED after {MAX_ATTEMPTS} attempts (last: {code})")
                    break
                # longer backoff on rate limiting (429) than on other transient errors
                wait = (60 if code == 429 else 30) * attempt
                print(f"  chunk {idx}/{n_chunks} attempt {attempt}/{MAX_ATTEMPTS}: {code}, retry in {wait}s")
                time.sleep(wait)

        # the failures file is a LOG, not a skip list: a chunk that succeeds on a
        # later run clears its entry, and one that fails again refreshes it
        failures = [f for f in failures if f["chunk"] != idx]
        if last_err is not None:
            failures.append({
                "chunk": idx,
                "n_range": [part[0]["n"], part[-1]["n"]],
                "expected_ns": sorted(expected_ns),
                "error": f"{type(last_err).__name__}: {last_err}",
            })
        json.dump(failures, open(FAILURES_PATH, "w", encoding="utf-8"), indent=1)

    elapsed = time.time() - t_start
    print(f"\nall chunks attempted in {elapsed/60:.1f} min")
    report(edges, n_chunks, failures)


def report(edges, n_chunks, failures):
    expected_all = {e["n"] for e in edges}
    got_all = {}
    for c in range(n_chunks):
        idx = c + 1
        out_path = f"{OUT_PREFIX}{idx:02d}.json"
        if not os.path.exists(out_path):
            continue
        try:
            data = json.load(open(out_path, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for r in data:
            if not isinstance(r, dict) or "n" not in r:
                continue
            n = r["n"]
            got_all.setdefault(n, []).append((idx, r))

    print("\n=== COVERAGE ===")
    covered = set(got_all)
    missing = expected_all - covered
    extra = covered - expected_all
    dupes = {n: locs for n, locs in got_all.items() if len(locs) > 1}
    print(f"input edges: {len(expected_all)}")
    print(f"classified (unique n covered): {len(covered)}")
    if missing:
        print(f"MISSING {len(missing)} n's: {sorted(missing)[:20]}{' ...' if len(missing) > 20 else ''}")
    else:
        print("missing: none")
    if extra:
        print(f"UNEXPECTED {len(extra)} n's not in input: {sorted(extra)[:20]}")
    if dupes:
        print(f"DUPLICATE n's (appear in >1 chunk file) {len(dupes)}: "
              f"{[(n, [i for i, _ in locs]) for n, locs in list(dupes.items())[:10]]}")
    else:
        print("duplicates: none")

    families = {}
    unclassified_no_family = 0
    unclassified_text_undecided = 0
    unclassified_other = 0
    for n, locs in got_all.items():
        _, r = locs[0]
        fam = r.get("family", "")
        if fam == "unclassified(no-family)":
            unclassified_no_family += 1
        elif fam == "unclassified(text-undecided)":
            unclassified_text_undecided += 1
        elif isinstance(fam, str) and fam.startswith("unclassified"):
            unclassified_other += 1
        else:
            families[fam] = families.get(fam, 0) + 1

    print("\n=== FAMILY DISTRIBUTION ===")
    for fam, count in sorted(families.items(), key=lambda kv: -kv[1]):
        print(f"  {fam}: {count}")
    print(f"  unclassified(no-family): {unclassified_no_family}")
    print(f"  unclassified(text-undecided): {unclassified_text_undecided}")
    if unclassified_other:
        print(f"  unclassified(other/malformed): {unclassified_other}")

    print("\n=== FAILED CHUNKS ===")
    if failures:
        for f in failures:
            print(f"  chunk {f['chunk']}: n_range {f['n_range']}, {len(f['expected_ns'])} edges "
                  f"NOT classified — {f['error']}")
        total_lost = sum(len(f["expected_ns"]) for f in failures)
        print(f"total edges lost to failed chunks: {total_lost} (recorded in {FAILURES_PATH})")
    else:
        print("  none")


if __name__ == "__main__":
    main()
