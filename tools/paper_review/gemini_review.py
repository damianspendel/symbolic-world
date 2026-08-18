#!/usr/bin/env python3
"""Blind cross-vendor review of a paper section by Gemini. Runs ONLY on
Damian's explicit go, per CLAUDE.md (2026-08-18). Key read from the gitignored
key file, sent as a request header, never printed.

The reviewer is blind: it receives the section text and a machine-derived fact
sheet, and nothing else. No table of contents, no author critique, no prior
review. It is asked to (1) list every empirical claim in the text and check
each against the fact sheet, (2) read for argument and clarity, (3) name any
prose it would flag as machine-written. Verdicts come back as JSON and are
written to docs/experiments/paper_v2_reviews/ as the receipt.

    python3 tools/paper_review/gemini_review.py <section.md> <facts.json> <out.json>
"""
import datetime
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL = "gemini-3.1-pro-preview"
KEY = open(ROOT / 'pipeline' / 'work' / 'gemini.key').read().strip()

section = pathlib.Path(sys.argv[1]).read_text()
facts = pathlib.Path(sys.argv[2]).read_text()
out = pathlib.Path(sys.argv[3])

PROMPT = """You are an independent reviewer for a methods paper in the digital humanities. You have not seen any other part of this paper or any discussion of it. Below is a draft section, followed by a fact sheet of figures derived mechanically from the project's dataset.

Do three things and return ONLY a JSON object.

1. "claims": list every empirical claim the text makes about the dataset or the pipeline (a number, a count, a proportion, a statement that something exists or does not exist). For each give: "text" (the claim, quoted), "check" (one of SUPPORTED, CONTRADICTED, NOT-IN-FACT-SHEET), "note" (one sentence; for CONTRADICTED give the fact-sheet value).

2. "argument": an object with "thesis" (one sentence: what the section claims), "holds" (true/false: does the text earn it), "gaps" (list of specific places where the reasoning skips a step or a term is used before it is defined), "overclaims" (list of sentences that say more than the fact sheet supports), "underclaims" (list of places the text concedes more than it needs to).

3. "prose": an object with "machine_tells" (list of specific phrases or constructions you would flag as characteristic of machine writing, quoted), "verbose" (list of sentences that could be cut or halved without loss), "unclear" (list of sentences a careful reader would have to read twice), "verdict" (one of CLEAR, ACCEPTABLE, HEAVY).

Be strict and specific. Quote the text. Do not praise.

=== SECTION ===
""" + section + """

=== FACT SHEET (derived from the dataset, not typed) ===
""" + facts

body = {
    "contents": [{"parts": [{"text": PROMPT}]}],
    "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
}
req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
resp = json.load(urllib.request.urlopen(req, timeout=600))
txt = resp["candidates"][0]["content"]["parts"][0]["text"]
verdict = json.loads(txt)
record = {
    "run": "blind cross-vendor paper review",
    "model": MODEL,
    "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    "section_file": sys.argv[1],
    "facts_file": sys.argv[2],
    "usage": resp.get("usageMetadata"),
    "verdict": verdict,
}
out.write_text(json.dumps(record, indent=2, ensure_ascii=False))
print(json.dumps(verdict, indent=2, ensure_ascii=False))
