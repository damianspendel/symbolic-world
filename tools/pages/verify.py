#!/usr/bin/env python3
"""Byte-compare a deployed Pages site against the local web/dist.

Run from the repo root:  python3 tools/pages/verify.py https://symbolic-world.pages.dev
"""
import hashlib
import pathlib
import re
import sys
import urllib.request

# Cloudflare Bot Fight Mode appends its challenge script to HTML on the wire
# (zone feature, active since the tunnel era). Strip it before comparing so the
# check measures OUR content, not Cloudflare's armour. Two observed variants
# (2026-10-08): the original iframe-wrapping `(function(){...})` form, and a
# bare `window.__CF$cv$params={...}` assignment — responses carry either, at
# Cloudflare's whim, so both must normalize away.
CF_INJECT = re.compile(rb'<script>(?:\(function\(\)\{.{0,4000}?|window\.)__CF\$cv\$params.*?</script>', re.S)


def normalize(body: bytes) -> bytes:
    return CF_INJECT.sub(b'', body)

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
    if hashlib.md5(normalize(body)).hexdigest() != hashlib.md5(p.read_bytes()).hexdigest():
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

# Item 29 — the extensionless convention is Cloudflare's to honour, not ours:
# Pages 308s every .html path to its extensionless twin, and GSC filed redirect
# errors until sitemap, canonical tags and internal links agreed on that form.
# This checks the behaviour is still in place. It is a WARNING rather than a
# failure, because it tests the host and not the artifact we built — but it
# prints either way, so a silent change of behaviour cannot pass unnoticed.
print('== extensionless redirect ==')


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


probe = '/ledger.html'
opener = urllib.request.build_opener(_NoRedirect)
try:
    req = urllib.request.Request(f'{BASE}{probe}', headers={'User-Agent': 'jungkg-verify'})
    with opener.open(req, timeout=30) as r:
        print(f'  WARNING {probe} returned {r.status} without redirecting — '
              f'the extensionless convention is not being served')
except urllib.error.HTTPError as e:
    target = e.headers.get('location', '(no location header)')
    expected = probe[: -len('.html')]
    if e.code in (301, 302, 307, 308) and target.rstrip('/').endswith(expected):
        print(f'  ok  {probe} -> {e.code} -> {target}')
    elif e.code in (301, 302, 307, 308):
        print(f'  WARNING {probe} -> {e.code} -> {target}, which is not {expected}')
    else:
        print(f'  WARNING {probe} returned {e.code}, not a redirect')
except Exception as e:
    print(f'  WARNING {probe} could not be checked: {e}')

print()
if fails:
    print(f'VERIFY FAILED: {len(fails)} file(s) differ or failed to fetch.')
    sys.exit(1)
print(f'VERIFY GREEN — {len(files)} files byte-identical at {BASE}.')
