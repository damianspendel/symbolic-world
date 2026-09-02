#!/usr/bin/env python3
"""Study C, part C1 — the second normalization arm.

A Gemini model re-normalizes the frozen verbatim relations under the same spec
the 2026-08-05 pass ran under, blind to the stored normalization. Transport is
exactly pipeline/crossvendor_run.py's: key read from the gitignored key file,
sent as a request header, never printed.

    python3 tools/studies/study_c_c1_arm2.py <start> <count>

Resumable: per-chunk response files live under pipeline/work/study_c/ and are
skipped when present; items already in docs/experiments/study_c/arm2.jsonl are
never re-sent. Corpus paragraph text goes to the API (as every cross-vendor run
does) but never into a committed file.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from study_c_lib import (  # noqa: E402
    DOCS, ROOT, WORK, first_reference, load_population, read_jsonl,
    append_jsonl, load_state, save_state,
)

MODEL = "gemini-3.1-pro-preview"
KEY = open(ROOT / 'pipeline' / 'work' / 'gemini.key').read().strip()
CHUNK = 10

PROMPT = """You are normalizing relation strings for a grounded knowledge graph of C.G. Jung's Collected Works.

Each item is an edge: subject -relation-> object. The relation is VERBATIM from the extraction pass, and many of these relations are clause-shaped: they have swallowed the carrier, scope, condition or modality of the claim into the predicate. A short verified quote and the full source paragraph are given as context.

Rewrite each relation into two parts:

1. "relation" — a verb phrase of AT MOST 4 hyphen-joined tokens (e.g. "produces", "is-equivalent-to", "is-elder-brother-of"). A verb phrase, never a proposition and never a clause.
2. "qualifiers" — an object with exactly the keys carrier, scope, condition, modality, note. Unused keys are null. Everything the verbatim relation carried that the verb cannot hold goes here:
   - carrier: the vehicle, medium or figure the claim runs through
   - scope: the domain, tradition or restriction the claim holds within
   - condition: the if/when the claim depends on
   - modality: hedging, possibility, necessity, or whose voice the claim is in
   - note: anything else needed to keep the claim faithful

The test is entailment: subject + your relation + object + your qualifiers must state the SAME claim the verbatim edge states and the paragraph supports. Nothing added, nothing stranded in the clause you discarded. Do not make the claim stronger or weaker than the paragraph does, and do not reverse its direction.

Assign each item exactly one verdict:
- "already-a-relation" — the verbatim relation is already a verb phrase within the cap; return it unchanged as "relation" and give any qualifiers it needs
- "rescued" — the clause decomposes into relation + qualifiers with nothing lost
- "unrescuable" — no decomposition preserves the verified claim; "relation" is null

Respond with ONLY a JSON array covering every n, no prose:
[{"n": <int>, "verdict": "already-a-relation|rescued|unrescuable", "relation": "<verb phrase or null>", "qualifiers": {"carrier": null, "scope": null, "condition": null, "modality": null, "note": null}}]"""


def load_paragraphs(wanted):
    """(volume, paragraph) -> text, for the items in hand only."""
    out = {}
    for line in open(ROOT / 'data' / 'paragraphs.jsonl'):
        rec = json.loads(line)
        key = (str(rec['volume']), int(rec['paragraph']))
        if key in wanted:
            out[key] = rec['text']
    return out


def build_items(population):
    wanted = set()
    for item in population:
        ref = first_reference(item['edge'])
        wanted.add((str(ref['volume']), int(ref['paragraph'])))
    paragraphs = load_paragraphs(wanted)

    items = []
    for item in population:
        edge, ref = item['edge'], first_reference(item['edge'])
        text = paragraphs.get((str(ref['volume']), int(ref['paragraph'])), '')
        items.append({
            'n': item['idx'],
            'subject': edge['subject'],
            'relation': edge['relation'],
            'object': edge['object'],
            'quote': ref['quote'],
            'citation': f"CW {ref['volume']} §{ref['paragraph']}",
            'paragraph_text': text,
        })
    return items


def call_gemini(items):
    body = {
        "contents": [{"parts": [{"text": PROMPT + "\n\nITEMS:\n"
                                 + json.dumps(items, ensure_ascii=False)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    try:
        out = json.loads(text)
    except json.JSONDecodeError:
        out = json.loads(text.rstrip().rstrip(',') + "]")
    expected = {it['n'] for it in items}
    got = {v.get('n') for v in out if isinstance(v, dict)}
    if got != expected:
        raise KeyError(f"response covers {len(got & expected)}/{len(expected)} items"
                       f" and invents {len(got - expected)}")
    usage = resp.get("usageMetadata", {})
    return out, usage


def run_chunk(items, out_path, max_attempts=6):
    """One chunk, with the linear backoff the cross-vendor runner uses. A hard
    stop after the last attempt: quota or 503 exhaustion HOLDS the study."""
    for attempt in range(1, max_attempts + 1):
        try:
            out, usage = call_gemini(items)
            json.dump({'model': MODEL, 'usage': usage, 'verdicts': out},
                      open(out_path, 'w'), indent=1)
            print(f"{os.path.basename(out_path)}: {len(out)} items | tokens in/out: "
                  f"{usage.get('promptTokenCount')}/{usage.get('candidatesTokenCount')}")
            return True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError, KeyError, IndexError) as exc:
            detail = ''
            if isinstance(exc, urllib.error.HTTPError):
                try:
                    detail = exc.read().decode()[:600]
                except Exception:
                    detail = ''
            label = getattr(exc, 'code', type(exc).__name__)
            if attempt == max_attempts:
                print(f"HOLD: chunk failed after {max_attempts} attempts. "
                      f"Last error: {label} {exc} {detail}", file=sys.stderr)
                return False
            wait = 30 * attempt
            print(f"attempt {attempt}: {label} {exc} — retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return False


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 90

    WORK.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    population = load_population()
    already = {rec['idx'] for rec in read_jsonl(DOCS / 'arm2.jsonl')}

    window = [p for p in population[start:start + count] if p['idx'] not in already]
    if not window:
        print("nothing to do: every item in this window is already recorded")
        return 0
    print(f"population {len(population)} | window {start}..{start + count - 1} "
          f"| {len(window)} to send")

    items = build_items(window)
    missing = [it['n'] for it in items if not it['paragraph_text']]
    if missing:
        print(f"HOLD: no paragraph text for items {missing}", file=sys.stderr)
        return 1

    by_idx = {p['idx']: p for p in window}
    written = 0
    for offset in range(0, len(items), CHUNK):
        part = items[offset:offset + CHUNK]
        out_path = WORK / f"c1_arm2_{part[0]['n']:03d}_{part[-1]['n']:03d}.json"
        if not out_path.exists():
            if not run_chunk(part, out_path):
                print(f"stopped after {written} new records; rerun to resume",
                      file=sys.stderr)
                return 1
        payload = json.load(open(out_path))
        records = []
        for verdict in payload['verdicts']:
            item = by_idx[verdict['n']]
            records.append({
                'idx': verdict['n'],
                'key': item['key'],
                'subject': item['edge']['subject'],
                'relation_verbatim': item['edge']['relation'],
                'object': item['edge']['object'],
                'verdict': verdict.get('verdict'),
                'relation': verdict.get('relation'),
                'qualifiers': verdict.get('qualifiers') or {},
                'arm': 'gemini',
                'model': payload['model'],
                'run_date': '2026-08-30',
            })
        recorded = {r['idx'] for r in read_jsonl(DOCS / 'arm2.jsonl')}
        records = [r for r in records if r['idx'] not in recorded]
        append_jsonl(DOCS / 'arm2.jsonl', records)
        written += len(records)

    state = load_state()
    state['c1_items_done'] = len(read_jsonl(DOCS / 'arm2.jsonl'))
    state['c1_total'] = len(population)
    save_state(state)
    print(f"arm2.jsonl now holds {state['c1_items_done']}/{len(population)} items")
    return 0


if __name__ == '__main__':
    sys.exit(main())
