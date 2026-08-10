# JungKG — product backlog

Ideas parked for later, not yet scheduled. The canonical graph and its § discipline
always come first; nothing here may compromise the trust model (every canonical edge
§-anchored + independently verified).

## Human-in-the-loop process (for v1.6 "The Second Reader" and v2.0 community pilot)

- **Reviewer identity as first-class provenance.** Validation records currently carry
  `validated_by: "author"` only. Extend to stable reviewer ids with a role
  (author / second-annotator / community), so every human judgment is attributable —
  and surface the reviewer id in the public verification log and in the per-citation
  evidence view, exactly like model verifier stamps. Community reviewers could link
  an ORCID or stay pseudonymous-but-stable; the log shows who (or which id) validated
  what, when, under which tool mode (anchored/unanchored). *(Added 2026-07-31.)*

- **Drip-fed validation for the author.** The next major release needs a further
  author-validated tranche beyond the 50-item gold set. Instead of marathon sessions:
  the review tool serves small stratified tranches (~5 items) on request — "do a few
  every once in a while" — resumable, accumulating toward a target n, with progress
  shown (e.g. 35/100 toward v1.6). Could ride the session check-in cadence: a gentle
  "5 items waiting" nudge, never a blocker. Unanchored mode by default per the E10
  lesson. *(Added 2026-07-31.)*

## Paper

- **Mention the public construction log in §6.1.** The atlas now exposes the
  transaction ledger as a browsable page (`/ledger.html`, batch-by-batch with commit
  links). One clause in the §6.1 artifact paragraph — "the construction log is
  browsable from the atlas" — strengthens the inspectability claim. Post-v1.3-freeze
  edit; run the facts checker after. *(Added 2026-07-29.)*

## App

- **Explore node card collides with the bottom control bar.** The selected-node card
  (bottom of Explore) overlaps the floating Mode / search / settings pill — they sit on
  top of each other. Fix: lift the card above the control bar (bottom inset), or dock the
  card to a side, so the two never overlap. *(Added 2026-07-23.)*

- **Reference toolbar title ("Around §N") leaks into Explore.** Because both views are
  kept alive (so Explore keeps its layout), the Reference NavigationSplitView's window
  toolbar/title still shows in Explore mode, where it's meaningless. Fix: suppress the
  reference chrome (title + sidebar toggle) when `mode == .explore`, or give Explore its
  own toolbar context. *(Added 2026-07-23.)*

- **Bidirectional selection (Reference → Explore).** Selecting a claim/node in Reference
  should highlight — and centre — the corresponding node/edge in the Explore graph.
  Selection currently flows only Explore → Reference; make it symmetric so switching to
  Explore lands on (and highlights) what you were reading. *(Added 2026-07-23.)*

- **App icon — Tenets-family style.** Design a Red Thread app icon consistent with the
  Tenets app family's visual identity ⚠ *(match the real suite's icon language — corner
  radius, palette, motif treatment)*. Motif candidates: a red thread / Ariadne's thread,
  a labyrinth, or a single luminous node-and-edge. macOS + iOS sizes.

## Features

- **User-contributed amplifications.** Let people add their own amplifications — the
  images and parallels *they* see around a symbol. **Hard constraint:** these live in a
  **separate, clearly-labeled layer**, visually and structurally distinct from Jung's
  §-anchored amplifications; they never merge into the verified graph or borrow its
  authority. Optional: let a user cite their own source. Serves Theo (correspondence
  practitioner) and Dana (dreamer) especially. *(Added 2026-07-23.)*

- **Local-only note option.** A per-note "do not sync" toggle for the most sensitive
  material (Marisol's clinical case notes) — overrides CloudKit sync for that note.

- **Note export formats beyond Markdown.** BibTeX / formatted academic citation export
  for the scholar/analyst personas.

- **Multi-edition §→page concordances.** Ship Bollingen first; add other printings /
  the Gesammelte Werke so "open the paragraph" works for more owned editions.

- **Stable citable URLs (web app).** Permalink per node and per edge, for scholars who
  cite and share (Whitmore).

- **Tradition-first reverse index.** Browse the graph by tradition (Kabbalah, Gnostic,
  alchemy, Christian mysticism) rather than by psychological concept (Theo).

- **Explore mode inside the app chrome.** The dark constellation view as a mode within
  the reading companion, not just the standalone atlas.

## Verification architecture: make it declaratively manageable (added 2026-07-27)

Today the verification stack (structure gate, voice specialist, sweeps, seeded
calibrations) lives as prompt text inside orchestration calls — it works, but
it is not inspectable or tunable as a *thing*. Backlog: a small declarative layer.

- `pipeline/verifiers.yaml` — one entry per verifier stage: name, model, axis
  (structure | voice | ...), prompt template (file ref), output schema, and its
  calibration set + last measured sensitivity/specificity. Adding a specialist
  for a new corpus axis = adding a YAML block, not editing orchestration.
- `pipeline/verify.py` — single runner: takes a candidates file + stage name,
  builds the payload from the corpus, invokes the model, writes verdicts in the
  standard shape. Same runner powers production gating, sweeps, and calibrations
  (a calibration is just a run over a seeded input with a key file).
- Per-stage calibration tracked in the YAML (date, seed, scores) so "how good is
  this verifier" is data, not memory; recalibration is a one-command re-run.
- Verdict application (corrections/merge/provenance) already uniform — extract the
  apply step into `pipeline/apply_verdicts.py` so every stage shares one code path.
- Payoff: the paper's "specialist decomposition" becomes an operable pattern —
  new corpus, new axes, same machinery; and the assumptions register can link
  each verifier to its measured performance.

## Publication venues beyond arXiv (added 2026-07-27; researched 2026-07-30)
No journal is devoted to Mysterium/Jungian alchemy specifically. Target paper for
the Jungian audience: "An atlas of Mysterium" companion piece — the instrument for
scholars + the sympathetic-reportage boundary as a text-historical finding (where
Jung's voice measurably merges with the alchemists'); 1956+70 anniversary peg.
Ranked fit: 1) Phanês (Jung history, OA, peer-reviewed, ≤10k words, double-blind —
first target); 2) International Journal of Jungian Studies (Brill; academic bridge,
invites other disciplines; ScholarOne); 3) Journal of Analytical Psychology (Wiley;
flagship, prefers clinical/empirical — second wave, voice-findings-for-analysts
angle); 4) Journal of Jungian Scholarly Studies (OA, multidisciplinary); outreach
tier: Jung Journal: Culture & Psyche, Psychological Perspectives, Quadrant (also
community-pilot recruiting channels); outsider: Ambix (history of alchemy proper;
Principe/Newman line critical of Jung — frame as mapping Jung's interpretation,
which the voice layer supports). Also still: Paradigm Explorer, DH Quarterly,
Journal of Cultural Analytics. Check each venue's AI-assisted-work stance before
submitting; lead with the radical-disclosure posture.

## Reader's guide to the papers we cite (added 2026-07-27)
Damian wants plain-language breakdowns of the papers cited in docs/PAPER.md to
understand the core claims — especially the hallucination-rate and KG-extraction
benchmarks (KGGen, GraphRAG accuracy studies, citation-hallucination surveys) and
which citations are preprints/non-peer-reviewed ("nonpublications") vs published.
Deliverable: one short annotated-bibliography doc, per-paper: what it measured,
how, headline number, and how much weight it can bear.

## E7: reduced-rubric cross-vendor replication (added 2026-07-27 as 'rubric-free'; relabeled)
Re-run a cross-vendor audit sample WITHOUT the first-party rubric: the second vendor
states support + severity in its own terms; map post hoc. Motivated by Gemini's
prompt-bias critique (shared-rubric convergence). See docs/experiments/exp6_crossvendor.md.

## Hostile-review remediations (added 2026-07-27, from Gemini Reviewer-2 pass)
Priority order agreed with the hostile review's own "what would change my mind":
1. **Expand calibration sets** — seeded corruptions from n=5/class to n=25/class (~$5-8):
   turns fractions into rates with usable confidence intervals. Do before arXiv.
2. **Human ground-truth tier** — upgrade the community pilot ambition toward ~200
   human-annotated paragraphs; this is the answer to the (correct) circularity attack:
   AI extracts, AI verifies, AI audits — the buck must stop at humans.
3. **Public-domain mini-replication** — run the identical pipeline on a public-domain
   interpretive corpus (e.g. William James, Varieties of Religious Experience, 1902):
   answers generalizability AND gives a fully distributable reproduction package.
4. **Paragraph-hash verification pack** — publish letter-normalized hashes of all
   cited paragraphs so third parties with any edition can verify quote anchoring
   without us distributing copyrighted text.
5. ~~Semantic-diffusion terminology~~ ✅ repositioned as shorthand w/ decomposition-literature context.
Full hostile review: pipeline/work/gemini_hostile_review.json
- Review great-mother vs the-mother node split (b-union-1 §403 edge may want retargeting to the new the-mother figure node; decided 2026-07-27 when both gates rejected the convention on b-cw12-4 n9)

## The family layer: public exposition and external validity (added 2026-08-10)

Four connected ideas from Damian's 2026-08-10 adjudication sitting. They belong
together because the first three make the ontology legible and the fourth asks
whether it is defensible — publishing without the fourth would state a position
on Jung that has never been checked against anyone but ourselves.

1. **Fold the accumulated rulings into FAMILY_DEFINITIONS v0.6.** The queue has
   been ruling on questions the document does not answer. The 2026-08-10 sitting
   alone retired the "amplification layer tag overrides the relation string" rule
   (three rulings against it, one precedent application), recorded the
   sentence-subject test that separates archetypal-identity from correspondence
   at CW 9i §572 vs CW 9ii §60, and added `exemplified-by` to the homeless
   strings beside `assimilates`. Nine already-assigned edges were assigned under
   the retired rule and are queued for a two-arm re-run:
   `pipeline/work/v06_amplification_rerun_queue.json`.

2. **A relation-string → family map, published.** The reverse index: for each
   family, the relation strings that land in it (`symbolization` ← `symbolizes`,
   `symbolized-by`, `represents`, `stands-for`, …), with counts. This is the
   single most useful artifact for a reader trying to understand what the layer
   claims, and it is derivable from `seed.json` with no new judgment. It also
   exposes the strings that fit nowhere, which is the honest part.

3. **A public page explaining the families.** `families.html` currently renders
   the definitions document — written for us, not for a visitor. A reader-facing
   version would state what a relation family IS (a classification OVER an
   already-verified relation, never a re-verification of the text), show the map
   from (2), name the boundary cases with worked examples, and show the queue
   and the adjudication protocol as evidence rather than decoration. Same
   humility register as the method page.

4. **External-validity sampling against Jungian scholarship — the load-bearing
   one, and the reason to do it BEFORE publishing (2) and (3).** Damian's
   question, verbatim in substance: would a Jungian scholar agree that
   `mandala is god-image` is *archetypal-identity*, or does our ontology
   contradict what key figures actually hold? Nothing in the pipeline currently
   tests this. Every check we run is internal — two model arms against a
   document we wrote, a gate calibrated against errors we planted. The families
   could be perfectly self-consistent and still cut Jung's thought at joints no
   reader of Jung recognizes.

   Shape: draw a stratified sample of assigned edges (say 25, weighted toward
   the contested families — archetypal-identity, correspondence, symbolization,
   amplification), and for each, check the assignment against secondary
   scholarship — Jacobi, von Franz, Samuels' *Critical Dictionary*, Shamdasani,
   the Journal of Analytical Psychology — asking not "is the claim true" (the
   gate already asked that) but "is this the relation a scholar would say Jung
   asserts here". Report agreement, and report the disagreements in full: a
   family the literature consistently reads differently is a definition defect,
   not a scholarly error. Cross-vendor is the wrong instrument here — this needs
   sources outside the corpus, so it is a research task with citations, not a
   model pass.

   Two known risks to state in the write-up: the scholars disagree with each
   other (so "consensus" may not exist for some pairs — that itself is the
   finding), and secondary literature is copyrighted, so quotation stays inside
   fair-use limits and nothing enters the graph from it. The graph remains
   single-corpus; this is a check ON the ontology, not new evidence IN it.

   Until (4) runs, the family layer ships as what it is: our classification,
   internally calibrated, externally unvalidated. Say that on the page.
