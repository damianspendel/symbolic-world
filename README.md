# The Symbolic World

An atlas of C. G. Jung's Collected Works. Each connection between two concepts carries a verbatim quote of at most 25 words, with its volume and paragraph, so a reader can check it against the book.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21631523.svg)](https://doi.org/10.5281/zenodo.21631523)
[![integrity](https://github.com/damianspendel/symbolic-world/actions/workflows/tests.yml/badge.svg)](https://github.com/damianspendel/symbolic-world/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/damianspendel/symbolic-world)](https://github.com/damianspendel/symbolic-world/releases/latest)

Live atlas: [symbolicworld.observer](https://symbolicworld.observer). Paper: [docs/PAPER.md](docs/PAPER.md). How to cite: see [CITATION.cff](CITATION.cff).

![The atlas, showing the graph and a selected concept](docs/img/atlas.png)

The graph holds 1077 concepts, 4498 relations and 6071 citations as of 2026-11-11 on the mining branch; release v2.3.0 shipped 999 concepts, 4035 relations and 5418 citations. The live atlas grows as mining continues.

### Three ways in

- Explore the atlas at symbolicworld.observer, or start from the ranked concepts index.
- Query the graph from the command line with `tools/query/kg_query.py`.
- Dispute an edge: every citation in the atlas expands to a record and a button that copies a prefilled report. Open it as a [GitHub issue](https://github.com/damianspendel/symbolic-world/issues).

### Project status

Mining of the Collected Works has finished CW 5, 7, 8, 9i, 9ii, 11, 12, 13, 14 and 16, and CW 6 chapters X and XI. A second pass over CW 12, 13 and 14 is next. Issues get a reply within seven days.

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
| `james/` | Second-corpus replication (James, *Varieties*): full reproduction package + [visual graph](https://symbolicworld.observer/james) |
| `manage.sh` | Build / deploy / service management |

## Copyright posture

The Collected Works texts are **not** in this repository and never were. Only ≤25-word
attributed quotations, § numbers, and page numbers are published, in reliance on
quotation and fair-use exceptions. The licence terms (MIT for the code, CC BY 4.0
for the dataset's original structure and metadata, the quotations excluded from
both) are in [NOTICE](NOTICE), and the full position, including the takedown
commitment, is in [docs/LEGAL.md](docs/LEGAL.md).

## Authorship

Damian Spendel, with AI collaborators: Claude Opus 4.8 and Opus 5 (proposal),
Claude Fable 5 (verification, and the drafting of the paper), Gemini 3.1 Pro
(cross-vendor audit, and the checking of the paper's claims), Claude Code
(orchestration). See the AI-use disclosure on the paper's title page.
