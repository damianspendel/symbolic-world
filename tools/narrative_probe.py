#!/usr/bin/env python3
"""Anonymized narrative probe (tier 2 of the narrative-probe ladder).

Question: does the graph's STRUCTURE alone — topology plus generic relation
semantics, with every domain identity hidden — still yield the journey-shaped
story that the labeled graph yields?

Blinding decisions (each one auditable here):
- Node labels -> opaque tokens (N001..), assignment order shuffled with a fixed
  seed so neither alphabet nor insertion order leaks mining history.
- Relations KEEP generic English verbs (symbolizes, precedes, contains): the
  tier-2 question includes generic semantics. They LOSE identity leakage:
  embedded proper nouns are replaced ("in-boehme-a" -> "in-one-author-a") and
  the discipline's method jargon is glossed to plain English (amplified-by ->
  paralleled-by), since the jargon alone names the domain.
- Nothing else ships: no types, no claim_types, no confidences, no citations.
- The probe prompt says only "a knowledge graph"; the full prompt is stored
  with the result. Each API call is stateless (no conversation history).

Outputs (pipeline/work/): narrative_probe_map.json (token->label),
narrative_probe_prompt.txt, narrative_probe_result.md.
"""
import json
import pathlib
import random
import re
import urllib.error
import urllib.request
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
seed = json.load(open(ROOT / 'seed.json'))
labels = {n['id']: n.get('label', n['id']) for n in seed['nodes']}

rng = random.Random(20260731)
ids = sorted(labels)
rng.shuffle(ids)
token = {nid: f"N{i+1:03d}" for i, nid in enumerate(ids)}

# identity leakage inside relation strings: proper nouns and domain jargon
REL_SCRUB = [
    (r'boehme', 'one-author'), (r'maria', 'one-author'), (r'christ', 'one-figure'),
    (r'jung', 'the-author'), (r'^amplified-by$', 'paralleled-by'),
    (r'^is-amplified-by$', 'is-paralleled-by'),
]
def scrub(rel):
    for pat, repl in REL_SCRUB:
        rel = re.sub(pat, repl, rel)
    return rel

triples = [f"{token[e['subject']]} | {scrub(e['relation']).replace('-', ' ')} | {token[e['object']]}"
           for e in seed['edges']]
rng.shuffle(triples)  # document order could leak mining sequence

PROMPT = ("Below is a knowledge graph, given only as subject | relation | object triples. "
          "Node names are opaque identifiers; you have no other context about what this "
          "graph is or where it comes from.\n\n"
          "Task: in roughly 100 words, write the story this graph tells, using the node "
          "identifiers as the names of its actors. Draw only on the triples — the "
          "structure, the recurring hubs, the sequences. Then, in one separate sentence, "
          "say what kind of thing you believe this graph is a map of.\n\nTRIPLES:\n"
          + "\n".join(triples))

json.dump({v: labels[k] for k, v in token.items()},
          open(ROOT / 'pipeline/work/narrative_probe_map.json', 'w'), ensure_ascii=False, indent=1)
(ROOT / 'pipeline/work/narrative_probe_prompt.txt').write_text(PROMPT)

KEY = open(ROOT / 'pipeline/work/gemini.key').read().strip()
body = {"contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 16000}}
req = urllib.request.Request(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
for attempt in range(1, 6):
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=600))
        break
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        if attempt == 5: raise
        print(f"attempt {attempt}: {getattr(e, 'code', e)}; retrying")
        time.sleep(40 * attempt)
text = resp["candidates"][0]["content"]["parts"][0]["text"]
(ROOT / 'pipeline/work/narrative_probe_result.md').write_text(text)
u = resp.get('usageMetadata', {})
print(text)
print(f"\n[tokens {u.get('promptTokenCount')}/{u.get('candidatesTokenCount')} | finish: {resp['candidates'][0].get('finishReason')}]")
