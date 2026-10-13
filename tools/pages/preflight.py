#!/usr/bin/env python3
"""Pages deploy preflight. Read-only. Non-zero exit on any failure.

Run from the repo root:  python3 tools/pages/preflight.py
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'web' / 'dist'
V13_BASELINE = '7b48c26b350cf3956fce568de3a948a4'

# Exact allowlist of what may ship. Directories mean "this subtree".
ALLOW = {
    'index.html', 'ledger.html', 'disputes.html', 'families.html',
    'james.html', 'chrome.css',
    'graph.json', 'pages.json', 'confirmations.json', 'disputes.json',
    'validations.json', 'robots.txt', 'sitemap.xml',
    # the v2.0 slice: release notes, the query panel and its two data files,
    # the ontology page, and the manifest of batch pages gated below
    'releases.html', 'query.html', 'query.js', 'ontology.html',
    'relation_declarations.json', 'batch_pages.json',
    # the method-page poster (2026-08-28): a static page asset, not a page —
    # extensionless convention does not apply, no sitemap entry
    'method-poster.png', 'nutshell.html',
    # the static twin of the SPA's #/method view (spec-concept-pages-v1)
    'method.html',
}
ALLOW_DIRS = {'v1.3'}
# Generated page families. A file matching one of these is allowed only if the
# generator that writes it vouches for it: a family page must name a family the
# ruleset holds, and a batch page must be listed in batch_pages.json. A blanket
# `family-*.html` glob would let a page from a retired family ride along.
FAMILY_PAGE = re.compile(r'^family-([a-z-]+)\.html$')
BATCH_PAGE = re.compile(r'^batch-([a-z0-9-]+)\.html$')
# spec-concept-pages-v1: one page per atlas node, vouched against the node ids
# in web/src/atlas.json — a page whose id the atlas does not hold is a stray.
# Emission is gated by EMIT_CONCEPT_PAGES in web/build-atlas.mjs; the flag is
# read from that source below so a disabled build stays green with no concept
# page in dist, and an enabled build must ship every node's page.
CONCEPT_PAGE = re.compile(r'^concept-([a-z0-9-]+)\.html$')
# Anything matching these anywhere in dist is an instant failure — unless the
# batch manifest vouches for the exact file. A batch id may legitimately contain
# the word "candidates" (the pre-window CW 14 sets are named that way), and the
# manifest is written by the ledger generator from state.json, so a stray mining
# candidates file cannot hide behind it: it would have to be named
# batch-<id>.html AND be listed in a manifest this build wrote.
FORBIDDEN = [
    re.compile(r'paragraphs\.jsonl'), re.compile(r'\.epub$'),
    re.compile(r'gemini\.key'), re.compile(r'\.token$'),
    re.compile(r'resume_notes'), re.compile(r'_input\.json$'),
    re.compile(r'candidates'),
]

fails = []


def check(name, ok, detail=''):
    print(f"  {'ok ' if ok else 'FAIL'} {name}" + (f' — {detail}' if detail else ''))
    if not ok:
        fails.append(name)


# What the generators say they wrote. Read before the sweep, because the sweep
# asks each file whether a generator vouches for it.
batch_manifest = {}
bm_path = ROOT / 'web' / 'public' / 'batch_pages.json'
if bm_path.exists():
    batch_manifest = json.loads(bm_path.read_text())
batch_pages_expected = set(batch_manifest.get('pages', []))
ruleset_families = set()
fam_path = ROOT / 'web' / 'src' / 'families.json'
if fam_path.exists():
    ruleset_families = {f['id'] for f in json.loads(fam_path.read_text()).get('families', [])}
# the concept-page vouching set and the emission flag, read from the generator's
# own source so the gate cannot disagree with the build that wrote dist
atlas_node_ids = set()
atlas_path = ROOT / 'web' / 'src' / 'atlas.json'
if atlas_path.exists():
    atlas_node_ids = {n['id'] for n in json.loads(atlas_path.read_text()).get('nodes', [])}
build_src = (ROOT / 'web' / 'build-atlas.mjs').read_text()
flag_match = re.search(r'^const EMIT_CONCEPT_PAGES = (true|false)$', build_src, re.M)
if not flag_match:
    check('EMIT_CONCEPT_PAGES readable from web/build-atlas.mjs', False,
          'the constant is missing or no longer a literal — the gate cannot tell '
          'whether concept pages should be in dist')
emit_concept_pages = bool(flag_match) and flag_match.group(1) == 'true'
# spec-instrument-v1, stage I1: the /concepts ranked index, gated the same way.
# While the gate is on the page is REQUIRED (it joins ALLOW, so the missing-file
# check bites); while it is off a lingering concepts.html fails as unexpected.
ci_match = re.search(r'^const EMIT_CONCEPTS_INDEX = (true|false)$', build_src, re.M)
if not ci_match:
    check('EMIT_CONCEPTS_INDEX readable from web/build-atlas.mjs', False,
          'the constant is missing or no longer a literal — the gate cannot tell '
          'whether the concepts index should be in dist')
if ci_match and ci_match.group(1) == 'true':
    ALLOW.add('concepts.html')
# spec-instrument-v1, stage I3: the /routes page, gated the same way.
ri_match = re.search(r'^const ROUTES_IN_UI = (true|false)$', build_src, re.M)
if not ri_match:
    check('ROUTES_IN_UI readable from web/build-atlas.mjs', False,
          'the constant is missing or no longer a literal — the gate cannot tell '
          'whether the routes page should be in dist')
if ri_match and ri_match.group(1) == 'true':
    ALLOW.add('routes.html')

print('== manifest ==')
seen = set()
dist_batch_pages = set()
dist_concept_pages = set()
for p in sorted(DIST.rglob('*')):
    if p.is_dir():
        continue
    rel = p.relative_to(DIST)
    seen.add(str(rel))
    top = rel.parts[0]
    name = rel.name
    fam_hit = FAMILY_PAGE.match(name) if len(rel.parts) == 1 else None
    batch_hit = BATCH_PAGE.match(name) if len(rel.parts) == 1 else None
    concept_hit = CONCEPT_PAGE.match(name) if len(rel.parts) == 1 else None
    vouched_batch = bool(batch_hit) and name in batch_pages_expected
    if batch_hit:
        dist_batch_pages.add(name)
    if concept_hit:
        dist_concept_pages.add(name)
    allowed = (str(rel) in ALLOW or top in ALLOW_DIRS
               or (fam_hit and fam_hit.group(1) in ruleset_families)
               or vouched_batch
               # a concept page is vouched only while emission is on AND its id
               # is a node the atlas holds — a disabled build with a lingering
               # concept page fails as an unexpected file
               or (concept_hit and emit_concept_pages
                   and concept_hit.group(1) in atlas_node_ids))
    if not allowed:
        check(f'unexpected file: {rel}', False)
    if not vouched_batch:
        for pat in FORBIDDEN:
            if pat.search(str(rel)):
                check(f'forbidden pattern in dist: {rel}', False)
missing = ALLOW - seen
check('all expected files present', not missing, f'missing: {sorted(missing)}' if missing else '')
check('manifest clean', not any(f.startswith(('unexpected', 'forbidden')) for f in fails))

print('== counts ==')
seed = json.loads((ROOT / 'seed.json').read_text())
sc = (len(seed['nodes']), len(seed['edges']),
      sum(len(e.get('references', [])) for e in seed['edges']))
atlas = json.loads((ROOT / 'web' / 'src' / 'atlas.json').read_text())
ac = (len(atlas['nodes']), len(atlas['edges']))
check('atlas nodes/edges == seed', ac == sc[:2], f'atlas {ac} vs seed {sc[:2]}')
idx = (DIST / 'index.html').read_text(errors='replace')
check('dist carries current counts', all(str(n) in idx for n in sc),
      f'expected {sc[0]}/{sc[1]}/{sc[2]} in landing copy')
# Ledger freshness (Damian, 2026-08-13): the ledger regenerates per merged
# batch by practice; this gate makes a stale one undeployable. The rendered
# ledger's stated counts must equal seed.json's, or the deploy stops here.
ldg_path = DIST / 'ledger.html'
if ldg_path.exists():
    ldg = ldg_path.read_text(errors='replace')
    stated = all(s in ldg for s in
                 (f'{sc[0]} nodes', f'{sc[1]} edges', f'{sc[2]} references'))
    check('ledger is fresh (counts == seed.json)', stated,
          f'expected "{sc[0]} nodes", "{sc[1]} edges", "{sc[2]} references" in ledger.html')
else:
    check('ledger present in dist', False, 'ledger.html missing from dist')

# Batch pages (item 9, 2026-08-13): they regenerate with the ledger by
# construction — one generator, one pass — so what this gates is the shipped
# result: a dist that lacks a batch page, lags seed.json, or carries an orphan
# from a renamed batch does not deploy.
if not batch_manifest:
    check('batch page manifest present', False,
          'web/public/batch_pages.json missing — run tools/build_ledger_page.py')
else:
    missing_batches = sorted(batch_pages_expected - dist_batch_pages)
    check('every batch page in dist', not missing_batches,
          f'missing from dist: {missing_batches[:5]}' if missing_batches else '')
    orphans = sorted(dist_batch_pages - batch_pages_expected)
    check('no orphan batch pages in dist', not orphans,
          f'in dist but not in the manifest: {orphans[:5]}' if orphans else '')
    check('batch pages are fresh (manifest edges == seed.json)',
          batch_manifest.get('seed_edges') == sc[1],
          f'manifest {batch_manifest.get("seed_edges")} vs seed {sc[1]}')
    check('manifest count == manifest ids',
          batch_manifest.get('count') == len(batch_manifest.get('ids', [])))

# Concept pages (spec-concept-pages-v1), shaped like the batch checks: with
# emission on, every atlas node has a page in dist and every concept page in
# dist belongs to a node. With emission off both checks skip — the walker above
# already fails any concept page that lingers in a disabled build.
if emit_concept_pages:
    expected_concepts = {f'concept-{nid}.html' for nid in atlas_node_ids}
    missing_concepts = sorted(expected_concepts - dist_concept_pages)
    check('every concept page in dist', not missing_concepts,
          f'missing from dist: {missing_concepts[:5]}' if missing_concepts else '')
    orphan_concepts = sorted(dist_concept_pages - expected_concepts)
    check('no orphan concept pages in dist', not orphan_concepts,
          f'in dist but not in the atlas: {orphan_concepts[:5]}' if orphan_concepts else '')
else:
    print('  ok  concept pages: EMIT_CONCEPT_PAGES is false — checks skipped')

# Item 29 — a size budget on the single-file app. viteSingleFile inlines the
# script, the styles and atlas.json into one document, so the page a reader
# downloads grows quietly with the graph. This is a ratchet, not a limit anyone
# is near: it fails the deploy if the bundle crosses the ceiling, and prints the
# actual against it either way so the trend is visible in the log.
print('== size budget ==')
INDEX_CEILING = 3.0 * 1024 * 1024
idx_path = DIST / 'index.html'
if idx_path.exists():
    actual = idx_path.stat().st_size
    check(f'dist/index.html within budget', actual <= INDEX_CEILING,
          f'{actual / 1024 / 1024:.2f} MB against a {INDEX_CEILING / 1024 / 1024:.1f} MB ceiling')
else:
    check('dist/index.html present', False, 'missing from dist')

print('== frozen snapshot ==')
h = hashlib.md5()
for p in sorted((DIST / 'v1.3').rglob('*')):
    if p.is_file():
        h.update(hashlib.md5(p.read_bytes()).hexdigest().encode() + b'\n')
# compare against the repo copy, which is itself checked against baseline
rh = hashlib.md5()
for p in sorted((ROOT / 'web' / 'public' / 'v1.3').rglob('*')):
    if p.is_file():
        rh.update(hashlib.md5(p.read_bytes()).hexdigest().encode() + b'\n')
check('dist /v1.3 == repo /v1.3', h.hexdigest() == rh.hexdigest())
proc = subprocess.run(
    'find web/public/v1.3 -type f -exec md5 {} \\; | sort | md5',
    shell=True, capture_output=True, text=True, cwd=ROOT)
check('repo /v1.3 == frozen baseline', proc.stdout.strip() == V13_BASELINE,
      proc.stdout.strip())

print('== gates ==')
for name, cmd in [('paper facts', 'python3 tools/check_paper_facts.py'),
                  ('poster facts (v2.0 pin; claim vs live graph)', 'python3 tools/check_poster_facts.py'),
                  ('test harness', 'python3 tests/test_graph.py')]:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
    check(name, p.returncode == 0, (p.stdout + p.stderr).strip().splitlines()[-1] if (p.stdout or p.stderr) else '')
p = subprocess.run('git rev-parse master origin/master', shell=True,
                   capture_output=True, text=True, cwd=ROOT)
check('master == origin/master', len(set(p.stdout.split())) == 1)

print()
if fails:
    print(f'PREFLIGHT FAILED ({len(fails)}): do not deploy.')
    sys.exit(1)
print('PREFLIGHT GREEN — safe to deploy web/dist.')
