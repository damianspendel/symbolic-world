#!/usr/bin/env python3
"""Byte-compare a deployed Pages site against the local web/dist.

Run from the repo root:  python3 tools/pages/verify.py https://symbolic-world.pages.dev
"""
import hashlib
import pathlib
import re
import sys
import urllib.error
import urllib.request

# Cloudflare Bot Fight Mode appends its challenge script to HTML on the wire
# (zone feature, active since the tunnel era). Strip it before comparing so the
# check measures OUR content, not Cloudflare's armour. Two observed variants
# (2026-10-08): the original iframe-wrapping `(function(){...})` form, and a
# bare `window.__CF$cv$params={...}` assignment — responses carry either, at
# Cloudflare's whim, so both must normalize away. The pattern starts only at
# Cloudflare's own opening, `<script>(function(){function c(){` or
# `<script>window.__CF`, and the gap to `__CF$cv$params` may not cross a
# `</script>`: a page that ends with its own inline `(function(){...})()`
# script (opus.html, opus-claims.html) keeps that script (2026-11-13).
CF_INJECT = re.compile(rb'<script>(?:\(function\(\)\{function c\(\)\{(?:(?!</script>).){0,4000}?|window\.)__CF\$cv\$params.*?</script>', re.S)
# Cloudflare Email Address Obfuscation (zone feature; first seen 2026-10-23, on
# the /about contact link) rewrites each mailto href to an encoded
# /cdn-cgi/l/email-protection#<hex> link and injects its decoder script. The
# hex is the address XORed with its first byte, with a fresh key per response,
# so it is decoded back to the mailto rather than stripped: the check still
# proves the right address is live.
CF_EMAIL_HREF = re.compile(rb'href="/cdn-cgi/l/email-protection#([0-9a-f]+)"')
CF_EMAIL_DECODER = re.compile(rb'<script data-cfasync="false" src="/cdn-cgi/scripts/[^"]+/cloudflare-static/email-decode\.min\.js"></script>')


# Cloudflare Web Analytics (zone setting, first seen on the wire 2026-10-28)
# injects its beacon script, with a per-response integrity hash and token,
# before </body> on every HTML page.
CF_BEACON = re.compile(rb'<script[^>]*src="https://static\.cloudflareinsights\.com/beacon\.min\.js[^"]*"[^>]*data-cf-beacon=[^>]*></script>\n?')


def _cf_email(m):
    h = bytes.fromhex(m.group(1).decode())
    return b'href="mailto:' + bytes(c ^ h[0] for c in h[1:]) + b'"'


def normalize(body: bytes) -> bytes:
    body = CF_BEACON.sub(b'', body)
    body = CF_EMAIL_DECODER.sub(b'', CF_EMAIL_HREF.sub(_cf_email, body))
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
    # 404.html has no URL of its own: it is checked below, through a missing path
    if str(rel) == '404.html':
        continue
    # _redirects is read by Pages at deploy and never served: its rules are
    # checked below, one probe per line
    if str(rel) == '_redirects':
        continue
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

# 404 behaviour: an unknown path, and an unknown concept page, must answer 404
# with our not-found page. A 200 here is the soft 404 fixed on 2026-11-04.
print('== not found ==')
for probe in ('/definitely-not-a-real-path-xyz', '/concept-definitely-not-a-node'):
    req = urllib.request.Request(f'{BASE}{probe}', headers={'User-Agent': 'jungkg-verify'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            fails.append(probe)
            print(f'  FAIL {probe} returned {r.status}, not 404')
    except urllib.error.HTTPError as e:
        same = hashlib.md5(normalize(e.read())).hexdigest() == hashlib.md5((DIST / '404.html').read_bytes()).hexdigest()
        if e.code == 404 and same:
            print(f'  ok  {probe} -> 404, the not-found page')
        else:
            fails.append(probe)
            print(f'  FAIL {probe} -> {e.code}, not-found page served: {same}')

# The rules in _redirects (2026-11-11). Unlike the extensionless check below,
# these are ours, so a wrong answer fails the run.
rules = DIST / '_redirects'


class _Stop(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


rules_opener = urllib.request.build_opener(_Stop)
if rules.exists():
    print('== _redirects ==')
    for line in rules.read_text().splitlines():
        parts = line.split()
        if len(parts) != 3 or line.lstrip().startswith('#'):
            continue
        src, dst, code = parts[0], parts[1], int(parts[2])
        req = urllib.request.Request(f'{BASE}{src}', headers={'User-Agent': 'jungkg-verify'})
        try:
            with rules_opener.open(req, timeout=30) as r:
                fails.append(src)
                print(f'  FAIL {src} returned {r.status}, not {code}')
        except urllib.error.HTTPError as e:
            target = e.headers.get('location', '')
            if e.code == code and target.rstrip('/').endswith(dst):
                print(f'  ok  {src} -> {e.code} -> {target}')
            else:
                fails.append(src)
                print(f'  FAIL {src} -> {e.code} -> {target or "(no location)"}, wanted {code} -> {dst}')
        except Exception as e:
            fails.append(src)
            print(f'  FAIL {src} could not be checked: {e}')

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
