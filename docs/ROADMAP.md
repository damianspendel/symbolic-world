# Roadmap — from v1.3.0 to the second paper

Status: agreed direction, 2026-07-30 (on the mining-away branch pending the return
review). Cadence rule: milestone releases only, each cut exactly once (the Zenodo
webhook makes releases immutable), each with one key deliverable a reader can see.
The paper stays frozen at v1.3.0; its CI verifies it against that tag forever.

| Release | Name | Key deliverable | Ships | External dependency | ≈Cost |
|---|---|---|---|---|---|
| v1.4 | The Trilogy | Alchemical corpus complete (CW 12 + 13 join CW 14) | away-branch after review; CW 13 end-to-end; relation inventory export | return review | ~$30 |
| v1.5 | The Typed Trilogy *(scope option undecided: trilogy-only vs Jung-wide-after-Aion — settled by the step-0 tail test, see proposal)* | Relation-family layer, measured | `docs/PROPOSAL_RELATION_TYPING.md` executed: definitions doc, tail test, edge-level mapping with provenance, E11 query evaluation, atlas family facets + voice×family filter | family-definition sign-off | ~$25 |
| v1.6 | The Second Reader | Inter-annotator agreement | unanchored second-annotator gold set + κ; open E10 items adjudicated; E1c drift recalibration; E9 cross-vendor re-grade; **arXiv paper v2** | second annotator recruited | ~$15 + their time |
| v1.7 | Aion | Archetypal core complete + vocabulary-transfer study | CW 9ii + CW 9i end-to-end; measured fraction of Aion edges classifiable under trilogy families (family additions via governance; redefinitions barred without re-gating) | — | ~$50 |
| v1.8 | The Story | Narrative as verified UI | "The Story" tab (every clause a clickable citation); E13 narrative probe formalized (blinding tiers, leak-scan, judge arm); second-witness toggle | — | ~$5 |
| v1.9 | Deutsch | Translation-invariance measured | E12 German cross-check + Konjunktiv boundary study on disputed voice items | Gesammelte Werke corpus sourced | ~$15 |
| v2.0 | The Community Atlas | The second paper | CW 5 + selective 11/16/8; permeation markers (fourth voice annotation); community verification pilot; nanopublication serialization | pilot recruiting; review cycle | ~$60 + reviews |

## Sequencing rationale

1. **Type after the flood, within declared scope.** The family vocabulary is
   provisionally scoped to the alchemical trilogy (see the proposal's scope
   decision), so it closes when the trilogy closes — clustered once — and later
   volumes test its transfer rather than forcing re-clustering. Non-trilogy edges
   carry `pending-scope`, visibly. The cross-vendor reviewer has twice argued that
   Aion must come first; that disagreement is now resolved by measurement rather
   than argument, via the tail test that opens the assignment pipeline. If the tail
   resists the trilogy definitions, v1.7 moves ahead of v1.5 and this rationale
   inverts.
2. **One recruited human, two instruments.** Families (v1.5) precede the second
   annotator (v1.6) so a single recruited session validates the voice gold set and
   the family mapping together; the author's drip-fed tranches accumulate toward
   the same release. The paper event (arXiv v2) rides v1.6 because κ plus a second
   validated instrument is the strongest single update.
3. **Every release has a visible headline.** Content and capability releases
   alternate; each capability lands on a larger graph than the one before (E11
   over four complete volumes; the story tab after Aion's material is in).
4. **External dependencies late, lead time started early.** The German corpus and
   community recruiting gate v1.9/v2.0; both also want predecessors' outputs (the
   final disputed-item list after v1.6; maximum artifact quality before the pilot).
5. **Front-load the de-risked.** v1.4 is produced by the proven pipeline at ~$3 a
   window; unproven layers sit behind at least one release of margin.

Declared slack: v1.7 can slide behind v1.8 without dependency damage. The coupling
defended hardest is v1.5 → v1.6.

## Standing process improvements attached to this roadmap

- Reviewer identity as first-class provenance in validation records and the public
  verification log (BACKLOG: human-in-the-loop) — lands with v1.6.
- Drip-fed author validation tranches (small stratified batches, unanchored,
  progress toward target n) — mechanism lands with v1.5, accumulates for v1.6.
- One-shot releases, usage-window-aligned autonomous passes, one mining run per
  corpus window — operating rules already in force.
