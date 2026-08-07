# Cloudflare Pages migration — runbook

Decided by Damian 2026-08-07. Phase order is the risk mitigation: everything
reversible first, the Mac server stays up as warm fallback until the soak
passes. Steps marked **[DAMIAN]** are his acts and are never run by an agent.

## Phase 0 — one-time setup [DAMIAN]

```bash
cd /Users/damianspendel/Documents/github/JungKG/web && npx wrangler login
```

Browser OAuth to the Cloudflare account that owns symbolicworld.observer.
No token files; wrangler stores its own credentials.

## Phase 1 — preflight (agent-safe, read-only checks)

```bash
python3 tools/pages/preflight.py
```

Rebuilds nothing. Verifies: dist manifest matches the allowlist exactly (no
unexpected files, nothing corpus-shaped), atlas counts == seed counts,
check_paper_facts green, test harness green, /v1.3/ tree checksum equals the
frozen baseline, master == origin/master. Exits non-zero on any failure —
do not proceed past a red preflight.

## Phase 2 — first deploy, to the test URL only [DAMIAN]

```bash
cd /Users/damianspendel/Documents/github/JungKG/web && npx wrangler pages project create symbolic-world --production-branch=main
```

```bash
cd /Users/damianspendel/Documents/github/JungKG/web && npx wrangler pages deploy dist --project-name=symbolic-world
```

This serves the site at https://symbolic-world.pages.dev — the real domain is
untouched.

## Phase 3 — verification against the test URL (agent-safe)

```bash
python3 tools/pages/verify.py https://symbolic-world.pages.dev
```

Fetches every file in the manifest from the deployed URL and byte-compares
its hash to the local dist copy, /v1.3/ included. Also spot-checks: the
landing HTML contains the current counts; unknown paths return 404 (noted,
not fatal — hash routing never hits the server); response headers show edge
caching active. Exits non-zero on any mismatch.

## Phase 4 — DNS flip [DAMIAN]

In the Cloudflare dashboard: Pages project symbolic-world → Custom domains →
add symbolicworld.observer (and www if used). Cloudflare rewrites the DNS
record itself and issues the cert. The old record (tunnel CNAME) is what you
are replacing; note its exact value first — it is the rollback.

Rollback at any point: delete the custom domain from the Pages project and
restore the tunnel CNAME. Seconds, not hours.

## Phase 5 — post-flip verification (agent-safe)

```bash
python3 tools/pages/verify.py https://symbolicworld.observer
```

Same byte-compare, now against the real domain. Then Damian opens the site on
his phone — the only real-device test in the chain — before any announcement.

## Phase 6 — soak, then decommission [DAMIAN]

Mac server (port 8788) and tunnel ingress stay AS THEY ARE for 24–48 h after
the flip. Only after the soak: stop the atlas server via manage.sh and remove
its ingress rule. The tunnel itself stays — other services use it.

## Redeploys (until automation is authorized)

Every subsequent publish = Phase 1 → deploy command → Phase 3 against the
production URL. Data-only automatic redeploys from the mining task require
Damian's explicit standing authorization, recorded in CLAUDE.md — not yet
given as of this writing.
