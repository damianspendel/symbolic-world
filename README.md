# The Symbolic World

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21631523.svg)](https://doi.org/10.5281/zenodo.21631523)

**A verified knowledge graph of C. G. Jung's *Collected Works* — every connection
anchored to a specific paragraph (§), mechanically checked, independently reviewed,
and cross-vendor audited.**

Live atlas: **[symbolicworld.observer](https://symbolicworld.observer)**
Paper: [docs/PAPER.md](docs/PAPER.md) · One-page summary: [docs/ABSTRACT.md](docs/ABSTRACT.md)

## What this is

653 symbols, figures, and concepts joined by 2420 relations, each backed by one or
more of 3430 references. Every reference names its exact CW paragraph and Bollingen
page, carries a verbatim quote of ≤25 words, and is typed by **whose claim it is**:
Jung's own assertion, doctrine he reports, or a named source he quotes. 100% of
references passed an independent verification gate; the whole of CW 14 was
additionally re-audited by a second vendor's model, and the author hand-validated
a 50-item gold sample against the source paragraphs (E10).

## Why it's different

Nothing enters this graph without passing, in order:

1. **Mechanical verbatim check** — the quote must exist, letter-for-letter, in the
   cited paragraph (excludes fabricated citations, within stated and canary-guarded bounds);
2. **Independent structure gate** — a model from a different family than the
   proposer reviews the full paragraph (support, direction, referent, conflation);
3. **Voice specialist** — a narrow second review of attribution and hedging;
4. **Standing cross-vendor audit** — a different vendor's model re-audits published
   samples, blind, including a reduced-rubric mode closer to its own terms.

Error rates are measured and published, not hidden: see the experiments in
[docs/experiments/](docs/experiments/) (seeded-corruption calibration, adversarial
audits, stability probes, cross-vendor audits E6–E7, the human gold set E10) and the standing review in
[docs/REVIEW.md](docs/REVIEW.md).

## Dispute an edge

Every citation in the atlas expands to its verification record and a **dispute
button** that copies a prefilled report. Submit it as a
[GitHub issue](https://github.com/damianspendel/symbolic-world/issues) — disputed
edges are re-reviewed with your objection attached, and outcomes (upheld /
corrected / removed) are published here. If a cited paragraph does not support
its edge, that finding falsifies the edge, publicly.

## Repository map

| Path | Contents |
|---|---|
| `seed.json` | The graph: nodes, edges, references with full verification provenance |
| `docs/PAPER.md` | Research paper (methods, experiments E0–E10, results) |
| `docs/experiments/` | Every experiment: designs, keys, verdicts, adjudications |
| `docs/ASSUMPTIONS.md` | 16-item assumptions register + community-verification protocol |
| `docs/LEGAL.md` | Legal statement (quotation basis, licensing, takedown) |
| `pipeline/` | Construction pipeline: runners, transaction ledger (`state.json`), batches |
| `tests/test_graph.py` | Integrity validators + 7 self-testing corruption canaries |
| `web/` | The atlas web app (Vite + Cytoscape) |
| `james/` | Second-corpus replication (James, *Varieties*): full reproduction package + [visual graph](https://symbolicworld.observer/james.html) |
| `manage.sh` | Build / deploy / service management |

## Copyright posture

The Collected Works texts are **not** in this repository and never were: the epub
and extracted corpus (`data/`) are gitignored and local-only. Only ≤25-word
attributed quotations, § numbers, and page numbers are published, in reliance on
quotation and fair-use exceptions — the full position, including licensing
(MIT code / CC BY 4.0 data, quotes excluded) and takedown commitment, is in
[docs/LEGAL.md](docs/LEGAL.md).

## Authorship

Damian Spendel, with AI collaborators: Claude Opus 4.8 and Opus 5 (proposal),
Claude Fable 5 (verification, and the drafting of the paper), Gemini 3.1 Pro
(cross-vendor audit, and the checking of the paper's claims), Claude Code
(orchestration). See the AI-use disclosure on the paper's title page.
