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
    'validations.json',
}
ALLOW_DIRS = {'v1.3'}
# Anything matching these anywhere in dist is an instant failure.
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


print('== manifest ==')
seen = set()
for p in sorted(DIST.rglob('*')):
    if p.is_dir():
        continue
    rel = p.relative_to(DIST)
    seen.add(str(rel))
    top = rel.parts[0]
    allowed = str(rel) in ALLOW or top in ALLOW_DIRS
    if not allowed:
        check(f'unexpected file: {rel}', False)
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
