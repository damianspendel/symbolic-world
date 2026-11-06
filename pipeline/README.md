# Pipeline transaction log

`state.json` is the ledger of every mining/verification batch. Statuses:
`input-built -> mined -> pre-checked -> gated -> cross-checked -> merged`
(terminal), or `held`.

**Recovery after session loss:** read `state.json`; for any batch not
`merged`, the listed files under `batches/` (candidates/verdicts, committed)
plus the local corpus `data/paragraphs.jsonl` are sufficient to resume:
- mined/pre-checked -> run the Fable gate on candidates (full paragraphs
  come from the corpus; gate inputs under work/ are disposable derivatives)
- gated -> run the cross-vendor check (below) before anything merges
- cross-checked -> apply verdicts to seed.json (SUPPORTED as-is; PARTIAL
  with the correction; WRONG dropped), set verified+verified_by+
  verified_date+crossvendor_checked, run tests/test_graph.py and
  tools/check_paper_facts.py, sync the living docs, rebuild
  web/public/ledger.html, commit, mark merged.
Nothing merged is ever only here: seed.json + git is the source of truth.

Invariant: miner (Opus family), gate (Fable family) and cross-vendor
(Gemini) stay different model families. The model that proposes content is
never the model that signs it off. Never merge unverified, and never merge
without the cross-vendor pass — `crossvendor_run.py` (`run_chunked`,
`GATE_PROMPT`, chunk=20, resumable) is a required stage, not an optional
audit. b-cw9ii-1 merged without one because this file did not say so.

From b-cw16-6 on, each batch record carries a `models` field with the exact
model ids that ran it: `proposer`, `gate`, `auditor`, and a `source` entry
saying where each id was read. `pipeline/mining/record_models.py <batch>
--proposer-agent <agentId>` writes it once the window's record script has
appended the batch record.
The proposer and gate ids come from the session transcripts and the auditor
id from the request model in `crossvendor_run.py`. A stage that ran on more
than one model records the list. Earlier records are left as they are.

Deployment is out of scope for this runbook. Work on `mining-away` is
local-only: no push, no `./manage.sh deploy`, no tags, no releases.
Publication is a separate, explicit decision.
