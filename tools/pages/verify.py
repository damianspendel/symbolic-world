#!/usr/bin/env python3
"""Byte-compare a deployed Pages site against the local web/dist.

Run from the repo root:  python3 tools/pages/verify.py https://symbolic-world.pages.dev
"""
import hashlib
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'web' / 'dist'

if len(sys.argv) != 2:
    sys.exit('usage: verify.py <base-url>')
BASE = sys.argv[1].rstrip('/')

fails = []
files = [p for p in sorted(DIST.rglob('*')) if p.is_file()]
print(f'comparing {len(files)} files against {BASE}')
edge_cached = False
for p in files:
    rel = p.relative_to(DIST)
    url = f'{BASE}/{rel}' if rel.name != 'index.html' or len(rel.parts) > 1 \
        else f'{BASE}/'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'jungkg-verify'})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            if 'cf-cache-status' in {k.lower() for k in r.headers}:
                edge_cached = True
    except Exception as e:
        fails.append(str(rel))
        print(f'  FAIL {rel} — fetch error: {e}')
        continue
    if hashlib.md5(body).hexdigest() != hashlib.md5(p.read_bytes()).hexdigest():
        fails.append(str(rel))
        print(f'  FAIL {rel} — content differs from local dist')
print(f'  edge caching headers observed: {edge_cached}')

# 404 behaviour (informational): hash routing never hits the server,
# but a real missing path should not silently 200 with the wrong file.
try:
    req = urllib.request.Request(f'{BASE}/definitely-not-a-real-path-xyz',
                                 headers={'User-Agent': 'jungkg-verify'})
    urllib.request.urlopen(req, timeout=30)
    print('  note: unknown path returned 200 (SPA fallback present)')
except urllib.error.HTTPError as e:
    print(f'  note: unknown path returns {e.code}')

print()
if fails:
    print(f'VERIFY FAILED: {len(fails)} file(s) differ or failed to fetch.')
    sys.exit(1)
print(f'VERIFY GREEN — {len(files)} files byte-identical at {BASE}.')
