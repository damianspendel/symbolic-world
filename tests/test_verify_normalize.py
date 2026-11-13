#!/usr/bin/env python3
"""The deploy check's normalisation strips Cloudflare's injected challenge
script and nothing else (BACKLOG, "The deploy check: false alarm on /opus and
/opus-claims", 2026-11-13).

At the v2.4.0 deploy, tools/pages/verify.py reported opus.html and
opus-claims.html as differing from web/dist. Both pages end with their own
inline `(function(){...})()` script, and the old CF_INJECT pattern started
matching at that script, so the page's own script was cut along with
Cloudflare's. These tests build a synthetic page of that shape and check that
normalising the "live" copy gives back the built page exactly.

verify.py runs its comparison at import, so the test executes only the part
above `ROOT = ` (the patterns and normalize()), which needs no network and no
arguments.

Run: python3 -m unittest tests/test_verify_normalize.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY = os.path.join(ROOT, "tools", "pages", "verify.py")


def load_normalize():
    src = open(VERIFY, encoding="utf-8").read()
    head, sep, _ = src.partition("\nROOT = ")
    if not sep:
        raise AssertionError("verify.py no longer defines ROOT after normalize(); update this test")
    ns = {"__name__": "verify_head"}
    exec(compile(head, VERIFY, "exec"), ns)
    return ns["normalize"]


normalize = load_normalize()

# A page's own closing script, shaped like the one /opus and /opus-claims end with.
OWN_SCRIPT = (b"<script>(function(){var m=document.querySelector('.page-main'),"
              b"bs=[].slice.call(document.querySelectorAll('.c-chip'));if(!m)return;"
              b"bs.forEach(function(b){b.addEventListener('click',function(){"
              b"m.classList.toggle('c-hide-'+b.getAttribute('data-v'))})})})();</script>")

# Cloudflare's challenge script in its iframe-wrapping form.
CF_IFRAME = (b"<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;"
             b"if(b){var d=b.createElement('script');d.innerHTML=\"window.__CF$cv$params="
             b"{r:'8e1f2a3b4c5d6e7f',t:'MTczMTUwMDAwMC4wMDAwMDA='};var a=document.createElement('script');"
             b"a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';"
             b"document.getElementsByTagName('head')[0].appendChild(a);\";"
             b"b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){"
             b"var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';"
             b"a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';"
             b"document.body.appendChild(a);if('loading'!==document.readyState)c();"
             b"else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);"
             b"else{var e=document.onreadystatechange||function(){};document.onreadystatechange="
             b"function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();"
             b"</script>")

# Cloudflare's challenge script in its bare form.
CF_BARE = (b"<script>window.__CF$cv$params={r:'8e1f2a3b4c5d6e7f',t:'MTczMTUwMDAwMC4wMDAwMDA='};"
           b"window.__CF$cv$params.nonce='';var a=document.createElement('script');"
           b"a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';"
           b"document.getElementsByTagName('head')[0].appendChild(a);</script>")

HEAD = (b"<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        b"<title>The Rosarium pictures: every claim</title></head>\n<body>\n"
        b"<main class=\"page-main prose\">\n<p>Body text.</p>\n")
BUILT = HEAD + OWN_SCRIPT + b"\n</main></body></html>"


def live(cf):
    """The built page as Cloudflare serves it: the challenge script before </body>."""
    return HEAD + OWN_SCRIPT + b"\n</main>" + cf + b"</body></html>"


class CloudflareInjectNormalize(unittest.TestCase):
    def test_iframe_form_after_own_script_leaves_own_script(self):
        self.assertEqual(normalize(live(CF_IFRAME)), BUILT)

    def test_bare_form_after_own_script_leaves_own_script(self):
        self.assertEqual(normalize(live(CF_BARE)), BUILT)

    def test_page_without_injection_is_unchanged(self):
        self.assertEqual(normalize(BUILT), BUILT)

    def test_fixture_reproduces_the_old_false_alarm(self):
        # the pattern before 2026-11-13 also removed the page's own script
        old = re.compile(rb'<script>(?:\(function\(\)\{.{0,4000}?|window\.)__CF\$cv\$params.*?</script>', re.S)
        stripped = old.sub(b"", live(CF_IFRAME))
        self.assertNotEqual(stripped, BUILT)
        self.assertNotIn(OWN_SCRIPT, stripped)


if __name__ == "__main__":
    unittest.main()
