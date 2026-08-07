# The Symbolic World — one-page summary

**A map of Jung's symbolic thought where every connection can be checked against the book.**

[symbolicworld.observer](https://symbolicworld.observer) · Damian Spendel, with AI collaborators (see paper) · July 2026

---

**What it is.** An interactive atlas of 349 symbols, figures, and concepts from C. G. Jung's *Collected Works*, joined by 1218 relations — *Mercurius is the masculine half of Sol and Luna's pair; the Shulamite corresponds to Malchuth; the experience of the self is a defeat for the ego.* Every one of the 1404 citations behind those relations names its exact paragraph (§) and Bollingen page and carries a verbatim quotation of at most 25 words. Jung's alchemical trilogy — CW 12, 13 and 14, including *Mysterium Coniunctionis*, his last and densest major work — is covered end-to-end; six further volumes are represented and growing.

**Why it exists.** Jung's twenty volumes are famously cross-referential: the same symbol means systematically different things in different places, on different authorities. Word search (the existing digital tooling) finds *occurrences*, not *relations* — it cannot tell you what Jung said the green lion *is*, or whether he said it himself or was quoting a seventeenth-century alchemist. And asking an AI chatbot produces fluent answers with fabricated citations — published studies find 11–57% of citations in deployed AI systems don't check out, and standard AI knowledge-extraction tools are wrong about a third of the time. For a scholarly corpus, that's worse than nothing.

**What's different here.** Three rules, enforced by machinery rather than good intentions:

1. **Nothing enters without a source.** Every relation must carry a verbatim quote mechanically verified to exist in its cited paragraph.
2. **Nothing enters without an independent check.** One AI model proposes relations; a *different* model family reviews each against the full paragraph and can correct or reject it. Rejections are deleted and logged publicly. (Same-model self-review is known to be biased — that's why two families.)
3. **Whose claim is it?** Every citation is typed: Jung's own assertion (761), doctrine he reports without endorsing (242), or a named source he quotes (80 — Dorn, Khunrath, Paracelsus…). Reportage is never silently converted into endorsement.

**And the error rate is published, not hidden.** When early, unreviewed material was re-audited, ~25% needed correction — the honest baseline for unverified AI extraction. After full verification, an adversarial audit (a reviewer instructed to *break* each of 30 randomly sampled links) found **zero factual or directional errors**; four links (13%) needed minor attribution refinements, which were applied. The remaining known weakness — nuance of attribution and hedging — is stated on the record, with a roadmap for driving it down (seeded-corruption tests of the verifier itself, cross-vendor audits — a first one, by a Google model blind-auditing 100 links, found zero unsupported links — and a standing offer: any reader who finds a link unsupported by its cited paragraph can falsify it publicly).

**Why it matters beyond Jung.** The pipeline — verbatim anchoring, cross-family verification as a publication gate, typed voice provenance, published error bars, and a fully replayable construction log — generalizes to any authored corpus where *who said what, exactly where* is the whole game: patristics, philosophy, law, history of science. It is a working answer to a current problem: how to use AI to structure humanistic knowledge *without* asking anyone to take the AI's word for it.

*Full paper: `docs/PAPER.md` · DOI: [10.5281/zenodo.21631523](https://doi.org/10.5281/zenodo.21631523)*
