#!/usr/bin/env python3
"""Deterministic check of every countable claim in docs/PAPER.md against the
shipped artifact. The paper's thesis is that AI-drafted claims must pass
deterministic checks before publication; this script applies that thesis to the
paper itself. Run by CI on every push and by tools/build_pdf.py before every build.

Exit non-zero, listing each failure, if any asserted fact does not match the
artifact. Facts are asserted as (claim-substring-that-must-appear, computed-truth)
pairs, so a drifting dataset OR a drifting paper both fail loudly.
"""
import json
import pathlib
import re
import subprocess
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
# An optional path lets the drafting pass gate a draft before it becomes PAPER.md.
PAPER_PATH = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'PAPER.md'
paper = PAPER_PATH.read_text()

# The paper is checked against the RELEASE it cites, not the working tree: the
# artifact keeps growing under the same gates, while a published paper stays
# true of its frozen release. Living docs (README, REVIEW) track the head.
#
# One exception, and it is declared rather than inferred. A paper being revised
# for an unreleased version cites a tag that does not exist yet, and the tag
# cannot be cut until this checker is green: circular. PENDING_RELEASE names
# that one version. While it is set, a paper citing it is checked against the
# working tree. The moment the tag exists, the tag wins and this constant goes
# inert on its own — the tagged commit's seed.json IS the working tree's. An
# undeclared missing tag still fails, as before. Set to None between releases.
PENDING_RELEASE = None   # v2.0.0 tagged 2026-09-05; the tag now pins the paper

failures = []

seed_live = json.load(open(ROOT / 'seed.json'))
seed = seed_live
_m = re.search(r'release `(v[^`]+)`', paper)
if _m:
    _r = subprocess.run(['git', 'show', f'{_m.group(1)}:seed.json'],
                        capture_output=True, text=True, cwd=ROOT)
    if _r.returncode == 0:
        seed = json.loads(_r.stdout)
    elif _m.group(1) != PENDING_RELEASE:
        failures.append(f"BASELINE: paper cites release '{_m.group(1)}' "
                        f"which has no tag and is not PENDING_RELEASE")
    # else: PENDING_RELEASE, so seed stays as the working tree — declared above.
james = json.load(open(ROOT / 'james' / 'james_seed.json'))


paper_flat = re.sub(r'\s+', ' ', paper)   # markdown wraps lines; a fact may not straddle one


def require(substring, why):
    """The paper must contain this exact substring (which encodes a computed fact)."""
    if substring not in paper and re.sub(r'\s+', ' ', substring) not in paper_flat:
        failures.append(f"MISSING/WRONG: paper lacks '{substring[:90]}' ({why})")


def forbid(pattern, why):
    m = re.search(pattern, paper)
    if m:
        failures.append(f"FORBIDDEN: '{m.group(0)[:80]}' ({why})")


# ---- graph counts ----
nodes, edges = len(seed['nodes']), len(seed['edges'])
refs = sum(len(e['references']) for e in seed['edges'])
require(f"{nodes} nodes", "node count")
require(f"{edges} relations", "edge count in abstract")
require(f"{refs} references", "reference count")

ct = Counter(r['claim_type'] for e in seed['edges'] for r in e['references']
             if r.get('claim_type'))
require(f"{ct['jung-asserts']} asserts / {ct['jung-reports-parallel']} reports / "
        f"{ct['jung-quotes-source']} quotes-source", "claim mix in §6.1")

conf = Counter(r.get('confidence', 'high') for e in seed['edges'] for r in e['references'])
require(f"{conf['medium']} hedged", "medium-confidence count")

paras = {(str(r['volume']), str(r['paragraph'])) for e in seed['edges'] for r in e['references']}
require(f"{len(paras)} distinct paragraphs", "distinct cited paragraphs")

# ---- cross-vendor coverage ----
xv = sum(1 for e in seed['edges'] for r in e['references'] if 'crossvendor_checked' in r)
require(f"{round(100*xv/refs)}% of references", "cross-vendor coverage percent")
cw14 = [r for e in seed['edges'] for r in e['references'] if str(r['volume']) == '14']
cw14_xv = sum(1 for r in cw14 if 'crossvendor_checked' in r)
require(f"{cw14_xv} of CW 14's {len(cw14)}", "CW14 cross-vendor coverage")

# ---- vocabulary_note count ----
vn = sum(1 for e in seed['edges'] for r in e['references'] if 'vocabulary_note' in r)
require(f"{vn} convention-dependent references" if f"{vn} convention-dependent references" in paper
        else f"{vn} references", f"vocabulary_note count is {vn}")

# ---- canaries: count from the test module ----
test_src = (ROOT / 'tests' / 'test_graph.py').read_text()
canary_count = len(re.findall(r'^\s+"[a-z-]+":\s+lambda e:', test_src, re.M))
require(f"{canary_count} canaries", f"canary count is {canary_count}")
forbid(r"five \*\*corruption canaries", "stale canary count in prose")
forbid(r"\b5 canaries\b" if canary_count != 5 else r"$^", "stale canary count")

# ---- fragments: recompute exact-substring rate ----
paras_text = {}
corpus_path = ROOT / 'data' / 'paragraphs.jsonl'
corpus_lines = open(corpus_path) if corpus_path.exists() else []
for line in corpus_lines:
    p = json.loads(line)
    paras_text[(str(p['volume']), str(p['paragraph']))] = p['text']


def words(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', s).lower()
    s = re.sub(r'[‘’“”"\'`]', '', s)
    return re.findall(r'[a-z0-9]+', s)


total_frags = exact = 0
for e in seed['edges'] if paras_text else []:
    for r in e['references']:
        text = paras_text.get((str(r['volume']), str(r['paragraph'])))
        if text is None:
            continue
        norm_text = ' '.join(words(text))
        for frag in re.split(r'\.\.\.|…', r['quote']):
            fw = words(frag)
            if not fw:
                continue
            total_frags += 1
            if ' '.join(fw) in norm_text:
                exact += 1
if paras_text:
    require(f"{exact} of {total_frags} quote fragments" if f"{exact} of {total_frags}" in paper
            else f"{exact}/{total_frags}", f"fragment exactness is {exact}/{total_frags}")

# ---- james counts ----
j_edges = len(james['edges'])
require(f"{j_edges} published", f"james edge count {j_edges}")
require(f"{len(james['nodes'])} nodes · {j_edges} edges" if
        f"{len(james['nodes'])} nodes" in paper else f"{j_edges} edges", "james node/edge")

# ---- gold set (E10): recompute from the committed validation record ----
gold_path = ROOT / 'pipeline' / 'human_validations.json'
if gold_path.exists():
    gold = json.load(open(gold_path))
    MAP = {'should-be-asserts': 'jung-asserts', 'should-be-reports': 'jung-reports-parallel',
           'should-be-quotes': 'jung-quotes-source'}
    sup = Counter(r['support'] for r in gold)
    agree = per = tot = None
    per, tot = Counter(), Counter()
    for r in gold:
        pc = r['pipeline_claim_type']
        tot[pc] += 1
        if r['voice'] == 'voice-correct' or MAP.get(r['voice']) == pc:
            per[pc] += 1
    agree = sum(per.values())
    require(f"{sup['supported']}/{len(gold)} supported", "gold-set support count")
    require(f"{agree}/{len(gold)}", "gold-set voice agreement")
    require(f"asserts {per['jung-asserts']}/{tot['jung-asserts']}", "gold per-class asserts")
    require(f"reports {per['jung-reports-parallel']}/{tot['jung-reports-parallel']}", "gold per-class reports")
    require(f"quotes {per['jung-quotes-source']}/{tot['jung-quotes-source']}", "gold per-class quotes")

# ---- cross-review convention fractions (Fable r3 M1 / Gemini r5 M1) ----
xr_dir = ROOT / 'docs' / 'experiments' / 'data'
if (xr_dir / 'gemini_e6_unanchored_review.json').exists():
    e6r = json.load(open(xr_dir / 'gemini_e6_unanchored_review.json'))
    e7r = json.load(open(xr_dir / 'gemini_e7_adjudication_review.json'))
    e6_rej = sum(1 for x in e6r if x['assessment'] == 'DISAGREE')
    e7_conv = [x for x in e7r if x['assessment'] == 'DISAGREE']
    conv_total = len(e6r) + len(e7_conv)
    conv_rej = e6_rej + len(e7_conv)
    require(f"{conv_rej} of the {conv_total} convention-based rulings",
            f"convention rejections {conv_rej}/{conv_total} from review files")
    require(f"{conv_rej}/{conv_total} convention rulings", "Table 4 convention fraction")

# ---- volume coverage bands (Fable r3 M5) ----
if paras_text:
    from collections import defaultdict
    vt = Counter(); vc = defaultdict(set)
    for (vol, para) in paras_text:
        vt[vol] += 1
    for e in seed['edges']:
        for r in e['references']:
            vc[str(r['volume'])].add(str(r['paragraph']))
    thin = [v for v in vt if v not in ('14', '12') and 1.5 <= round(100*len(vc[v])/vt[v], 1) <= 3.9]
    WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}
    band_word = WORDS.get(len(thin), str(len(thin)))
    require(f"{band_word} thinly-sampled volumes", "volume band (count derived from the corpus)")
    if len(thin) == 7:   # the v1.3 paper's second phrasing of the same fact
        require("the seven other sampled volumes", "limitations volume band")
    cw12_pct = round(100 * len(vc['12']) / vt['12'])
    require(f"CW 12, at {cw12_pct}%", "conclusion CW12 coverage")
    cw14_pct = round(100 * len(vc['14']) / vt['14'])
    require(f"{cw14_pct}% of CW 14's paragraphs ({len(vc['14'])} of {vt['14']})", "Imperative 6 CW14 coverage")

# ---- the family layer: schema, coherence, contamination, calibration --------
# RULES #18. Five checks, all deterministic and offline. The calibration RUN
# cannot live in CI (paid, non-deterministic, needs a key CI must never hold);
# what CI can do is refuse to let the ruleset drift away from its calibration,
# refuse a malformed family record, and refuse a planted corruption marker that
# reached the graph. Each failure prints the literal string that would satisfy it.
FAM_DOC = ROOT / 'docs' / 'FAMILY_DEFINITIONS.md'
FAM_STATES = {'assigned', 'pending-adjudication', 'no-family', 'text-undecided',
              'not-a-relation'}

if FAM_DOC.exists():
    fam_text = FAM_DOC.read_text()
    inventory = set(re.findall(r'^### \d+\.\s+([a-z-]+)', fam_text, re.M))
    if not inventory:
        failures.append("FAMILY DOC: no '### <n>. <family>' headings found — "
                        "the family inventory cannot be parsed")

    # (1) schema: closed state enum; a value iff assigned; assigned values are in
    #     the document's inventory
    state_counts = Counter()
    for e in seed_live['edges']:
        key = f"{e['subject']}|{e['relation']}|{e['object']}"
        rf = e.get('relation_family')
        if rf is None:
            state_counts['(absent)'] += 1
            continue
        if not isinstance(rf, dict):
            failures.append(f"FAMILY SCHEMA: {key} carries a non-object "
                            f"relation_family ({type(rf).__name__})")
            continue
        st, val = rf.get('state'), rf.get('value')
        state_counts[st] += 1
        if st not in FAM_STATES:
            failures.append(f"FAMILY SCHEMA: {key} has state {st!r}; expected one "
                            f"of {sorted(FAM_STATES)}")
        elif st == 'assigned':
            if not val:
                failures.append(f"FAMILY SCHEMA: {key} is 'assigned' with value "
                                f"{val!r}; an assigned edge must name a family")
            elif val not in inventory:
                failures.append(f"FAMILY SCHEMA: {key} names family {val!r}, which "
                                f"{FAM_DOC.name} does not define")
        elif val is not None:
            failures.append(f"FAMILY SCHEMA: {key} is {st!r} but carries value "
                            f"{val!r}; only 'assigned' carries a family")

    # (2) coherence: the states partition the edge set, and the queue on disk is
    #     exactly as long as the graph says it should be
    n_live = len(seed_live['edges'])
    recorded = sum(v for k, v in state_counts.items() if k in FAM_STATES)
    if recorded != n_live:
        failures.append(f"FAMILY COUNTS: the four family states account for "
                        f"{recorded} edges, expected {n_live} — "
                        f"{n_live - recorded} edge(s) carry no usable record "
                        f"(states seen: {dict(state_counts)})")
    queue_path = ROOT / 'pipeline' / 'work' / 'family_pending_queue.json'
    if queue_path.exists():
        q = json.load(open(queue_path))
        n_q = len(q if isinstance(q, list) else q.get('items', q.get('queue', [])))
        if n_q != state_counts['pending-adjudication']:
            failures.append(f"FAMILY QUEUE: the queue holds {n_q} items but "
                            f"{state_counts['pending-adjudication']} edges are "
                            f"pending-adjudication in seed.json")

    # (3) contamination tripwire: no seeded-corruption marker may survive into the
    #     published graph (BACKLOG item 6's third defence)
    MARKERS = ('calibration_seed', 'planted_at', 'planted', 'corruption_class',
               'corrupted', 'plant_seed')
    def marker_keys(d):
        return [k for k in d
                if k in MARKERS or 'calibration' in k.lower() or 'plant' in k.lower()]
    for e in seed_live['edges']:
        key = f"{e['subject']}|{e['relation']}|{e['object']}"
        for k in marker_keys(e):
            failures.append(f"CORRUPTION MARKER: edge {key} carries {k!r} — a "
                            f"planted-calibration field reached seed.json")
        for r in e['references']:
            for k in marker_keys(r):
                failures.append(f"CORRUPTION MARKER: reference on {key} "
                                f"(CW {r.get('volume')} §{r.get('paragraph')}) "
                                f"carries {k!r}")

    # (4) calibration handshake: the declared ruleset version must have a
    #     committed calibration record measured against that same version
    m = re.search(r'^# Relation families.*?(v[\d.]+)', fam_text, re.M)
    fam_version = m.group(1) if m else None
    if not fam_version:
        failures.append("FAMILY DOC: no version in the header line; expected "
                        "'# Relation families — candidate definitions, vX.Y'")
    else:
        rec_dir = ROOT / 'pipeline' / 'family_calibration' / 'records'
        matched = []
        for p in sorted(rec_dir.glob('*.json')) if rec_dir.exists() else []:
            try:
                rec = json.load(open(p))
            except (json.JSONDecodeError, OSError):
                failures.append(f"CALIBRATION RECORD: {p.name} is not readable JSON")
                continue
            if rec.get('definitions_version') == fam_version:
                matched.append((p, rec))
        if not matched:
            failures.append(
                f"STALE RULESET: {FAM_DOC.name} declares {fam_version} but no file in "
                f"pipeline/family_calibration/records/ has "
                f'"definitions_version": "{fam_version}". A ruleset version does not '
                f"ship until the calibration has been re-run against it (RULES #16).")
        else:
            for p, rec in matched:
                if rec.get('verdict') not in ('PASS', 'FAIL'):
                    failures.append(f"CALIBRATION RECORD: {p.name} has verdict "
                                    f"{rec.get('verdict')!r}; expected 'PASS' or 'FAIL'")
            # a FAIL on file is a result, but it does not license the version:
            # the ruleset ships only on a PASS (Damian 2026-08-12; RULES #16)
            if not any(rec.get('verdict') == 'PASS' for _, rec in matched):
                failures.append(
                    f"STALE RULESET: {FAM_DOC.name} declares {fam_version} and "
                    f"records exist, but none has \"verdict\": \"PASS\". A failed "
                    f"calibration is on the record and the ruleset does not ship "
                    f"until a PASS record for {fam_version} exists.")

    # (5) the ledger's family tooltip must derive from the record, not from one
    #     blanket sentence (RULES #10). Every `by` that is not an arms-agreed
    #     record must hit a branch in fam_note(); every non-assigned state must
    #     have its own note. Anything else falls through to the arms-agreed
    #     wording and describes an edge as something it is not.
    ledger_src = (ROOT / 'tools' / 'build_ledger_page.py').read_text()
    branches = set(re.findall(r'if "([a-z-]+)" in b:', ledger_src))
    noted_states = set(re.findall(r'^\s+"([a-z-]+)":\s+"', ledger_src, re.M))
    if not branches:
        failures.append("LEDGER TOOLTIP: no fam_note() branches parsed from "
                        "tools/build_ledger_page.py — the check cannot run")
    for by in sorted({str((e.get('relation_family') or {}).get('by', ''))
                      for e in seed_live['edges']}):
        st = {(e.get('relation_family') or {}).get('state')
              for e in seed_live['edges']
              if str((e.get('relation_family') or {}).get('by', '')) == by}
        if 'assigned' not in st:
            continue
        if by.startswith('opus+gemini-agreed'):
            continue                       # the intended fallthrough
        if not any(b in by.lower() for b in branches):
            failures.append(
                f"LEDGER TOOLTIP: assigned edges carry by={by!r}, which matches no "
                f"fam_note() branch {sorted(branches)} — they would render with the "
                f"two-arms-agreed wording. Add a branch or the tooltip lies.")
    for st in sorted(state_counts):
        if st in ('assigned', '(absent)'):
            continue
        if st not in noted_states:
            failures.append(f"LEDGER TOOLTIP: state {st!r} is present in seed.json "
                            f"but has no entry in FAM_STATE_NOTE; its tooltip would "
                            f"render empty")

# ---- every paragraph citation in the paper must exist in the graph ----
# Added 2026-09-02 after a renumbering script mangled "CW 8 §827" into "§2#TMP#27"
# in a draft: a paper about paragraph-anchored claims cannot cite a paragraph
# the graph does not cite. Matches "CW 9ii §264" and "CW 14 §329" forms.
cited_pairs = {(r['volume'], int(r['paragraph'])) for e in seed_live['edges'] for r in e['references']}
for m in re.finditer(r'CW\s*(\d+i{0,2})\s*§\s*(\d+)(?![\d–-])', paper):   # ranges like §111–180 are windows, not citations
    vol, para = m.group(1), int(m.group(2))
    if (vol, para) not in cited_pairs:
        failures.append(f"PARAGRAPH: paper cites CW {vol} §{para}, which no reference in the graph cites")
if re.search(r'§\d*#TMP#', paper):
    failures.append("PARAGRAPH: renumbering artifact '#TMP#' left in the paper")

# ---- release tag ----
tags = subprocess.run(['git', 'tag', '--list'], capture_output=True, text=True,
                      cwd=ROOT).stdout.split()
for m in re.finditer(r'release `(v[^`]+)`', paper):
    if m.group(1) not in tags and m.group(1) != PENDING_RELEASE:
        failures.append(f"RELEASE TAG: paper cites '{m.group(1)}' not in git tags {tags}")
if PENDING_RELEASE and PENDING_RELEASE in tags:
    failures.append(f"STALE PENDING: {PENDING_RELEASE} is tagged; set PENDING_RELEASE "
                    f"to None so the paper is checked against the tag, not the tree")

# ---- companion docs must carry current counts ----
# .zenodo.json describes the archived release: pin to the paper's baseline
zd = (ROOT / '.zenodo.json').read_text()
if f"{nodes} nodes, {edges} edges, {refs} references" not in zd:
    failures.append(f"STALE DOC: .zenodo.json lacks baseline counts {nodes}/{edges}/{refs}")

refs_live = sum(len(e['references']) for e in seed_live['edges'])
for doc in ['README.md', 'docs/ABSTRACT.md', 'docs/REVIEW.md']:
    dt = (ROOT / doc).read_text()
    if str(refs_live) not in dt:
        failures.append(f"STALE DOC: {doc} lacks current reference count {refs_live}")

# docs/REVIEW.md is a standing snapshot: pin its headline numbers like the paper's
rv = (ROOT / 'docs' / 'REVIEW.md').read_text()
ct_live = Counter(r['claim_type'] for e in seed_live['edges'] for r in e['references'])
paras_live = {(str(r['volume']), str(r['paragraph'])) for e in seed_live['edges'] for r in e['references']}
for sub, why in [
    (f"{len(seed_live['nodes'])} nodes · {len(seed_live['edges'])} edges · {refs_live} references", "REVIEW graph line"),
    (f"{ct_live['jung-asserts']} jung-asserts · {ct_live['jung-reports-parallel']} jung-reports-parallel · "
     f"{ct_live['jung-quotes-source']} jung-quotes-source", "REVIEW claim mix"),
    (f"{canary_count} corruption canaries", "REVIEW canary count"),
    (f"{len(paras_live)} distinct CW paragraphs", "REVIEW distinct paragraphs"),
]:
    if sub not in rv:
        failures.append(f"STALE DOC: docs/REVIEW.md lacks '{sub[:60]}' ({why})")

# ---- references integrity: every [n] cited has an entry; every entry is cited ----
cited = {int(n) for grp in re.findall(r'(?<!\d)\[(\d{1,2}(?:,\s*\d{1,2})*)\](?!\()', paper)
         for n in grp.split(',')}   # [4, 8] cites two entries
entries = {int(m.group(1)) for m in re.finditer(r'^(\d{1,2})\. .+<https?://', paper, re.M)}
if entries:
    if cited - entries:
        failures.append(f"REFERENCES: cited without entry: {sorted(cited - entries)}")
    if entries - cited:
        failures.append(f"REFERENCES: entry never cited: {sorted(entries - cited)}")
    if entries != set(range(1, max(entries) + 1)):
        failures.append("REFERENCES: entry numbering not contiguous from 1")

# ---- banned phrases (claims retired by review) ----
for pat, why in [
    (r'25-fold', "retired headline"),
    (r'rubric effect ≈ 0', "withdrawn claim"),
    (r'hard yards', "retired rhetoric"),
    (r'first published sensitivity', "retired first-ever claim"),
    (r'confound-free support', "E9 shared-instrument confound (Fable M5)"),
    (r'errors (?:run|at) 1–2%', "underivable pooled rate (Fable r2 M3)"),
    (r'human floor', "floor implies lower bound; anchored review forbids it (Gemini r4 M1)"),
    (r'blind-check', "E10 was anchored, not blind (Fable r2 M1)"),
    (r'\bfive planted corruption', "canary count is asserted above"),
    (r'confirmed by a human', "n=10 directionality is not significant (Fable r2 minor 4)"),
    (r'9/17', "wrong denominator: mixes review-set sizes with convention rulings (Gemini r5 / Fable r3)"),
    (r'1\.0% upheld residual', "friendly endpoint of the 1.0-2.2% range (Fable r3 M4)"),
    (r'eight thinly-sampled', "seven volumes are in the band; CW12 is at 14% (Fable r3 M5)"),
    (r'[Rr]ubric-free replication', "relabeled reduced-rubric (Fable r3 M3)"),
    (r'−38% to \+90%|-38% to \+90%', "not in the self-preference source; real range −0.07..+0.75 (bib challenge)"),
    (r'entirely in its own terms', "retired framing (Fable r3 M3)"),
]:
    forbid(pat, why)

if failures:
    print(f"PAPER FACTS: {len(failures)} FAILURES")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print(f"PAPER FACTS: all checks pass "
      f"({nodes}/{edges}/{refs}; mix {ct['jung-asserts']}/{ct['jung-reports-parallel']}/"
      f"{ct['jung-quotes-source']}; xv {xv}; frags {exact}/{total_frags}; "
      f"canaries {canary_count}; james {j_edges})")
