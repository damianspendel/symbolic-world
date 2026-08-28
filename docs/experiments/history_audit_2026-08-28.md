# History audit before any v2.0 push — 2026-08-28

Scope: every commit the push would publish, `origin/master (4b9dcda, the
public v1.3 tip) .. HEAD` on `mining-away`: 281 commits, 2,572 blobs, 284 MB
raw (before git compression).

## Mechanical scans, all clean

- Forbidden paths (`data/`, `pipeline/work/`, `paragraphs.jsonl`, `*.epub`,
  `*.key`, `mobile_adjudication`): zero touched anywhere in the range.
- API-key patterns (Google `AIza…`, Anthropic `sk-ant-…`, GitHub `ghp_…`):
  zero hits in all patches.
- Literal Gemini request headers with embedded keys: zero.
- The adjudication worker's secret slug: zero.
- Corpus `paragraph_text` fields: zero. 541 long added lines were
  filtered by pattern and the residue inspected by eye (66 lines carrying
  section marks got a separate pass): relation-string inventories in
  `transfer_trend.jsonl`, batch narratives whose quoted fragments stay far
  under the 25-word cap, CSS data-URIs, review-prompt text. No corpus
  paragraph leaves; this class rests on filtered inspection, not a proof.

## Findings that need a decision

1. **CLAUDE.md would go public, in full, with history.** It is not in the
   public repo today. It is the internal operating context: Damian's phone
   number (2 commits plus the current file), standing authorizations, agent
   traps, cost notes. Publishing it is not a leak of secrets, but it is an
   internal ops document and PII.
2. **The unpublished v2.0 paper draft would go public.** `docs/PAPER_v2_draft.md`
   and its review receipts (`docs/experiments/paper_v2_reviews/`,
   `paper_v2_triage…`) are tracked. Pushing publishes the draft before any
   arXiv v2 submission.
3. **Repo weight.** `web/public/ledger.html` is committed on every merge:
   112 versions over 1 MB (3+ MB each recently). Git delta-compresses text
   well, so the pushed pack will be far under 284 MB, but the public clone
   grows materially. Not a privacy issue; a hygiene one.

## Push plan (proposed)

Plan A — filter, then push (recommended):
1. `git filter-repo` over the range only, producing `public-v2` from
   `mining-away` with two path sets removed from ALL 281 commits:
   `CLAUDE.md`, and the draft set (`docs/PAPER_v2_draft.md`,
   `docs/experiments/paper_v2_reviews/`, the triage file). Pre-1.3 public
   history is untouched; the segment's SHAs change, which is acceptable
   because nothing published cites segment SHAs (the poster sidecar's
   `rendered_at_commit` is informational and will be updated at the tag).
2. Verify the filtered branch: re-run these same scans against it; diff its
   tree against `mining-away` minus the excluded paths (must be identical);
   run the full test suite and preflight on it.
3. Push `public-v2` to `origin/master` (fast-forward from 4b9dcda), tag
   v2.0.0 there, GitHub Release, Zenodo webhook.
4. `mining-away` stays local and private, keeps CLAUDE.md and the draft;
   future releases repeat the filter.

Plan B — push as-is after redacting the phone number in a new commit:
simplest, keeps one history, but publishes CLAUDE.md (with the number still
in old commits) and the paper draft. Not recommended.

The ledger-weight issue is accepted either way (rewriting it out would break
the replayability story for the batch history).

## Why push and update Zenodo at all (Damian's open question)

The published method makes two promises that a site-only release breaks:
the paper says the construction "replays commit by commit", which requires
the commits to be public; and the site and the v1.3 record say the concept
DOI "resolves to the latest release", which requires a v2.0 Zenodo version
to exist. A "reference somewhere" instead would leave the public repo and
the archived record describing a 248-node graph while the site serves 589.
The Zenodo update is one webhook firing on the GitHub release; the cost is
the audit above, which is now done.
