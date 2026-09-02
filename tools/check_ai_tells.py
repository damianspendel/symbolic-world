#!/usr/bin/env python3
"""AI-writing tells, swept mechanically before any prose reaches Damian.

Sources, checked 2026-08-18 and extended 2026-09-02 (see docs/WRITING.md
for the register and the reader block's rationale): Wikipedia:Signs of AI writing (vocabulary,
copula avoidance, "not X but Y", rule of three, -ing tail clauses, false
ranges, vague attributions, significance inflation, em dashes, bold, title
case, curly quotes, "X rather than Y"); Damian's own writing rules in
~/.claude/CLAUDE.md; StationX's structural study (vocabulary is the weakest
signal, so this script reports structure too: sentence-length uniformity and
"the moral stated out loud"). Detectors built only on word lists are easily
gamed, so a clean run here is necessary, not sufficient.

    python3 tools/check_ai_tells.py [path]     default docs/PAPER.md

Two severities. HARD tells fail the run. SOFT tells are printed with counts
and never fail: they are legitimate English in small doses and the reader
decides. Fenced code, tables and blockquotes are skipped.
"""
import collections
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'PAPER.md'
raw = path.read_text()

# ---- strip what is not prose ----
text = re.sub(r'```.*?```', '', raw, flags=re.S)
text = re.split(r'^### References\s*$', text, maxsplit=1, flags=re.M)[0]   # citations are not prose
lines = [l for l in text.splitlines()
         if not l.startswith('|') and not l.startswith('>') and not l.startswith('    ')]
prose = '\n'.join(lines)
lower = prose.lower()

hard, soft = [], []


def count(pattern, flags=re.I):
    return [m.group(0) for m in re.finditer(pattern, prose, flags)]


# ---- HARD: vocabulary (Wikipedia list ∪ Damian's list) ----
VOCAB = ['delve', 'tapestry', 'testament', 'pivotal', 'crucial', 'landscape',
         'meticulous', 'underscore', 'underscores', 'underscoring', 'showcase',
         'showcasing', 'foster', 'fostering', 'garner', 'vibrant', 'intricate',
         'intricacies', 'interplay', 'boasts', 'enduring', 'leverage', 'robust',
         'seamless', 'holistic', 'journey', 'resonate', 'align with', 'aligns with',
         'deep dive', 'bolstered', 'groundbreaking', 'renowned', 'nestled',
         'in the heart of', 'diverse array', 'valuable insights', 'indelible',
         'deeply rooted', 'setting the stage', 'evolving landscape', 'focal point',
         'game-changer', 'paradigm shift', 'multifaceted', 'realm', 'navigate',
         'unlock', 'elevate', 'empower', 'harness the', 'harnessing', 'streamline', 'cutting-edge',
         'transformative', 'nuanced', 'comprehensive', 'ever-evolving']
for w in VOCAB:
    hits = count(r'\b' + re.escape(w) + r'\b')
    if hits:
        hard.append(f'vocab "{w}" ×{len(hits)}')

# ---- HARD: copula avoidance ----
for w in ['serves as', 'stands as', 'functions as', 'operates as', 'marks a',
          'represents a shift', 'acts as a']:
    hits = count(r'\b' + re.escape(w) + r'\b')
    if hits:
        hard.append(f'copula-avoidance "{w}" ×{len(hits)}')

# ---- HARD: sentence-opening connectives ----
for w in ['Additionally', 'Moreover', 'Furthermore', 'Notably', 'Importantly',
          'Crucially', 'In conclusion', 'Overall', 'Ultimately', 'In summary',
          'It is worth noting', "It's worth noting", 'It is important to note',
          'Interestingly']:
    hits = count(r'(?:^|[.!?]\s+)' + re.escape(w) + r'\b', flags=re.M)
    if hits:
        hard.append(f'opener "{w}" ×{len(hits)}')

# ---- HARD: negative parallelism ----
for pat, name in [(r"\bnot (?:just|only|merely|simply)\b[^.]{0,80}\bbut\b", "not just X but Y"),
                  (r"\b(?:it|this|that)['’]s not\b[^.]{0,60}\b(?:it|this|that)['’]s\b", "it's not X, it's Y")]:
    hits = count(pat)
    if hits:
        hard.append(f'{name} ×{len(hits)}: {hits[0][:60]!r}')

# ---- HARD: -ing tail clauses of superficial analysis ----
ING = r',\s+(?:highlighting|underscoring|emphasizing|emphasising|reflecting|showcasing|ensuring|fostering|demonstrating|illustrating|signaling|signalling|symbolizing|symbolising|cementing|solidifying|marking|revealing|contributing to)\b'
hits = count(ING)
if hits:
    hard.append(f'-ing tail clause ×{len(hits)}: {hits[0]!r}')

# ---- HARD: significance inflation ----
for w in ['plays a vital role', 'plays a crucial role', 'plays a key role',
          'a testament to', 'cannot be overstated', 'stands out as',
          'key turning point', 'lasting impact', 'profound impact']:
    hits = count(re.escape(w))
    if hits:
        hard.append(f'inflation "{w}" ×{len(hits)}')

# ---- HARD: vague attribution ----
for w in ['experts argue', 'experts say', 'observers have', 'some critics',
          'many scholars', 'it is widely', 'studies show', 'research shows']:
    hits = count(re.escape(w))
    if hits:
        hard.append(f'vague attribution "{w}" ×{len(hits)}')

# ---- HARD: formatting ----
if lower.count('**') // 2 > 12:
    hard.append(f'bold spans ×{lower.count("**")//2} (>12)')
for h in re.findall(r'^#{2,4}\s+(.+)$', prose, flags=re.M):   # H1 title exempt
    if '*' in h:                                                  # book titles exempt
        continue
    ws = [w for w in re.findall(r'[A-Za-z]+', h) if len(w) > 3]
    if len(ws) >= 3 and all(w[0].isupper() for w in ws):
        hard.append(f'title-case heading {h!r}')
if re.search(r'^\s*[\U0001F300-\U0001FAFF☀-➿]', prose, flags=re.M):
    hard.append('emoji used as list marker')

# ---- SOFT: reported, never gating ----
soft.append(f'em-dashes: {prose.count("—")} (length checker gates these)')
n_rt = len(count(r"\brather than\b"))
soft.append(f'"rather than": {n_rt}')
fr = count(r'\bfrom\s+\w+(?:\s+\w+){0,3}\s+to\s+\w+')
soft.append(f'"from X to Y" ranges: {len(fr)} (inspect for false ranges)')
tri = count(r'\b\w+,\s+\w+,?\s+and\s+\w+\b')
soft.append(f'possible tricolons: {len(tri)}')
colon = count(r'^[A-Z][^.:\n]{0,40}:\s+[A-Za-z]', flags=re.M)
soft.append(f'colon-led reveals ("The result: ..."): {len(colon)}')
curly = len(re.findall(r'[“”‘’]', prose))
soft.append(f'curly quotes/apostrophes: {curly}')
sents = [s for s in re.split(r'(?<=[.!?])\s+', re.sub(r'\s+', ' ', prose)) if len(s.split()) > 2]
if len(sents) > 5:
    L = [len(s.split()) for s in sents]
    soft.append(f'sentence length: mean {statistics.mean(L):.1f}, sd {statistics.pstdev(L):.1f} '
                f'(sd < 6 on a long text reads as uniform rhythm)')
moral = count(r'\b(?:the (?:lesson|takeaway|point) (?:is|here)|in other words|what this means is|the upshot)\b')
soft.append(f'moral-stated-aloud phrases: {len(moral)}')

# ---- reader block (docs/WRITING.md): the curse of knowledge, zombie nouns, uniformity ----
words_all = re.findall(r"[A-Za-z][A-Za-z'-]*", prose)
nw = max(1, len(words_all))
NOMINAL = re.compile(r"\b\w{4,}(?:tion|sion|ment|ance|ence|ity|ness|ization|isation)s?\b", re.I)
nominal = len(NOMINAL.findall(prose))
soft.append(f'nominalizations (zombie nouns): {nominal} per {nw} words = {100*nominal/nw:.1f} per 100')
META = ['framework', 'approach', 'aspect', 'dimension', 'notion', 'perspective', 'level', 'process',
        'context', 'factor', 'paradigm', 'construct']
meta = sum(len(re.findall(r'\b' + m + r's?\b', prose, re.I)) for m in META)
soft.append(f'metaconcepts (framework/approach/aspect/...): {meta} = {100*meta/nw:.2f} per 100 words')
passive = len(re.findall(r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?\w+(?:ed|en)\b", prose))
soft.append(f'passive constructions (heuristic): {passive} in {len(sents)} sentences')
hedges = re.findall(r"\b(?:may|might|could|seems? to|appears? to|arguably|perhaps|possibly|likely|tends? to)\b", prose, re.I)
soft.append(f'hedges: {len(hedges)} ({100*len(hedges)/nw:.2f} per 100 words)')
if len(sents) > 5:
    opener = collections.Counter(s.split()[0].strip('*_"').lower() for s in sents if s.split())
    top = opener.most_common(1)[0]
    soft.append(f'sentence openers: {len(opener)} distinct of {len(sents)}; commonest "{top[0]}" x{top[1]}')
paras = [p for p in re.split(r'\n\s*\n', prose) if len(p.split()) > 15]
if len(paras) > 3:
    PL = [len(p.split()) for p in paras]
    soft.append(f'paragraph length: mean {statistics.mean(PL):.0f}, sd {statistics.pstdev(PL):.0f} words over {len(paras)} paragraphs')
syll = sum(max(1, len(re.findall(r'[aeiouy]+', w.lower()))) for w in words_all)
if sents:
    flesch = 206.835 - 1.015 * (nw / len(sents)) - 84.6 * (syll / nw)
    soft.append(f'Flesch reading ease: {flesch:.0f} (60+ plain, 30-50 academic, <30 dense)')
# undefined abbreviations: an ALLCAPS token 2-5 letters must appear expanded somewhere:
# either "(ABC)" after words, or "ABC (" before an expansion, or be in the allow list
ALLOW_ABBR = {'AI', 'CI', 'API', 'JSON', 'PDF', 'URL', 'DOI', 'CSS', 'HTML', 'ID', 'UI', 'RDF', 'KV',
              'PASS', 'FAIL', 'TRUE', 'FALSE', 'CORRECTED', 'SUPPORTED', 'PARTIAL', 'WRONG', 'HOLD',
              'GPT', 'ACL', 'ICLR', 'ICML', 'NAACL', 'EMNLP', 'IEEE', 'MDPI', 'LDC', 'PLOS', 'PMC', 'ARAS', 'DOI'}   # product and venue names
abbrs = set(re.findall(r'\b[A-Z]{2,5}\b', prose)) - ALLOW_ABBR
defined = set(re.findall(r'\(([A-Z]{2,5})\)', prose)) | set(re.findall(r'\b([A-Z]{2,5})\s*\(', prose))
undefined = sorted(a for a in abbrs if a not in defined and not re.fullmatch(r'E\d+|RQ\d*|CW|R\d+', a))
if undefined:
    hard.append(f'undefined abbreviations (define at first use): {", ".join(undefined[:8])}')

for s in soft:
    print('  soft  ', s)
for h in hard:
    print('  HARD  ', h)
if hard:
    print(f'AI TELLS: FAIL ({len(hard)} hard)')
    sys.exit(1)
print('AI TELLS: ok (no hard tells)')
