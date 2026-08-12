#!/usr/bin/env python3
"""Cross-vendor verification runner (E6). Reads the key from the gitignored
key file, sends it only as a request header, never prints it."""
import json, sys, urllib.request

MODEL = "gemini-3.1-pro-preview"
KEY = open('pipeline/work/gemini.key').read().strip()

GATE_PROMPT = """You are the independent verification gate for a grounded knowledge graph of C.G. Jung's symbolic thought. Every edge must be anchored to a real Collected Works paragraph. Catch reversed relations, wrong sources, conceptual conflations, identity overreach, and quotes taken misleadingly out of context. Be strict; a fabrication that survives you corrupts the graph.

Below are candidate edges. Each has: n, subject/subject_label, relation, object/object_label, claim_type, source, citation, quote, paragraph_text (the FULL verbatim paragraph).

For each edge judge: (1) does paragraph_text actually assert subject -relation-> object (read the WHOLE paragraph)? (2) DIRECTION correct (reversed = WRONG)? (3) quote accurate and not misleading? (4) claim_type honest - jung-asserts (his own voice) vs jung-reports-parallel (reported doctrine) vs jung-quotes-source (named source; source field should name it)? Reported doctrine miscast as jung-asserts is PARTIAL. (5) conceptual conflation or identity overreach ("is"/"identical-to" where the text has analogy)?

VERDICT per edge: SUPPORTED | PARTIAL (core link real but something off) | WRONG (unsupported/reversed/conflated beyond repair).

Respond with ONLY a JSON array: [{"n": <int>, "verdict": "SUPPORTED|PARTIAL|WRONG", "reason": "<one sentence>"}] covering every n."""

VOICE_PROMPT = """You are an attribution-modality auditor for a grounded knowledge graph of C.G. Jung's Collected Works. NARROW audit: for each reference judge ONLY (A) claim_type honesty and (B) hedge fidelity against the full paragraph. Do NOT re-litigate direction, referents, or quote accuracy.

(A) claim_type must be: "jung-asserts" ONLY if Jung states the claim in his own interpretive voice; "jung-reports-parallel" if the paragraph presents it as another tradition's/author's doctrine that Jung reports (even sympathetically); "jung-quotes-source" if it rests on a quoted named source. Watch for "the alchemists say/called", "according to", footnoted doctrine. Also flag the REVERSE error (Jung's own theses mistyped as reportage).
(B) hedges: hedged/conditional claims ("perhaps","seems","would appear","presumably", if-clauses) should carry confidence "medium"; flag "high" on clearly hedged claims.

Below are references (n, subject/relation/object, claim_type, source, confidence, citation, quote, paragraph_text).
Respond with ONLY a JSON array listing ONLY the refs needing a change: [{"n": <int>, "issue": "claim_type|hedge", "reason": "<one sentence>"}]. Correct refs get no entry."""

def run(items, prompt, out_path):
    body = {
        "contents": [{"parts": [{"text": prompt + "\n\nITEMS:\n" + json.dumps(items, ensure_ascii=False)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0}
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    try:
        verdicts = json.loads(text)
    except json.JSONDecodeError:
        # Gemini sometimes drops the closing bracket despite finishReason STOP
        verdicts = json.loads(text.rstrip().rstrip(',') + "]")
    # a salvaged (or even clean) response must cover the whole batch and NOTHING
    # ELSE — a truncated set and a hallucinated extra n are both failures, so
    # run_chunked retries instead of silently accepting either
    expected = {it['n'] for it in items if isinstance(it, dict) and 'n' in it}
    got = {v.get('n') for v in verdicts if isinstance(v, dict)}
    if expected and got != expected:
        raise KeyError(f"verdicts cover {len(got & expected)}/{len(expected)} items"
                       f" and invent {len(got - expected)}")
    json.dump(verdicts, open(out_path, "w"), indent=1)
    usage = resp.get("usageMetadata", {})
    print(f"{out_path}: {len(verdicts)} entries | tokens in/out: {usage.get('promptTokenCount')}/{usage.get('candidatesTokenCount')}")

def run_chunked(items, prompt, out_prefix, chunk=20, max_attempts=8):
    """Resumable chunked run: skips chunks whose output file already exists;
    retries each chunk with linear backoff on transient errors (503 etc.)."""
    import time, os, urllib.error
    n_chunks = (len(items) + chunk - 1) // chunk
    for c in range(n_chunks):
        out_path = f"{out_prefix}_c{c+1:02d}.json"
        if os.path.exists(out_path):
            print(f"{out_path}: already done, skipping")
            continue
        part = items[c*chunk:(c+1)*chunk]
        for attempt in range(1, max_attempts + 1):
            try:
                run(part, prompt, out_path)
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                    json.JSONDecodeError, KeyError) as e:
                code = getattr(e, 'code', type(e).__name__)
                if attempt == max_attempts:
                    print(f"chunk {c+1}/{n_chunks} FAILED after {max_attempts} attempts (last: {code})")
                    sys.exit(1)
                wait = 30 * attempt
                print(f"chunk {c+1}/{n_chunks} attempt {attempt}: HTTP {code}, retry in {wait}s")
                time.sleep(wait)
    print("all chunks complete")

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "e1":
        run(json.load(open('pipeline/work/calib_input.json')), GATE_PROMPT, 'pipeline/work/gemini_e1_verdicts.json')
    elif which == "e5":
        run(json.load(open('pipeline/work/e5_input.json')), VOICE_PROMPT, 'pipeline/work/gemini_e5_verdicts.json')
    elif which == "audit":
        run_chunked(json.load(open('pipeline/work/audit100_input.json')), GATE_PROMPT,
                    'pipeline/work/gemini_audit100')
    elif which == "e7":
        # Reduced-rubric audit (originally called rubric-free; relabeled after a
        # code-level review found retained enums — see exp7 doc):
        # no verdict enum, no claim-type definitions, no strictness persona — the
        # auditor judges support and describes problems in its own terms.
        E7_PROMPT = """You are reviewing statements that a project extracted from C.G. Jung's Collected Works. Each item claims a relationship (subject -relation-> object), gives an attribution type the project assigned (claim_type), a confidence level, a short quotation, and the full source paragraph (paragraph_text). The in_e6_sample field is bookkeeping; ignore it.

For each item, form your own judgment from the paragraph alone: does the paragraph support the claimed relationship as stated, including the attribution (whose claim the paragraph presents it as) and the confidence level? If you see any problem — of any kind — describe it in your own words and rate how serious you consider it, on your own scale of minor / moderate / serious.

Respond with ONLY a JSON array covering every n:
[{"n": <int>, "supported": "yes" | "partly" | "no", "problem": "<your own words; empty string if none>", "seriousness": "none" | "minor" | "moderate" | "serious"}]"""
        items = json.load(open('pipeline/work/e7_cw14_input.json'))
        run_chunked(items, E7_PROMPT, 'pipeline/work/gemini_e7', chunk=20)
        # reduced-rubric replay of the E1 seeded-corruption set for a sensitivity measure
        calib = json.load(open('pipeline/work/calib_input.json'))
        run_chunked(calib, E7_PROMPT, 'pipeline/work/gemini_e7_calib', chunk=20)
