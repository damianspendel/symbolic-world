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
The author wants plain-language breakdowns of the papers cited in docs/PAPER.md to
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

Six connected items from the 2026-08-10 adjudication sitting. Items 1–3
make the ontology legible, item 4 asks whether it is defensible, and items 5–6
keep the instrument honest over time. Publishing 1–3 without 4 would state a
position on Jung that has never been checked against anyone but ourselves.

**SEQUENCE (editorial ruling, 2026-08-10) — this order is the decision, not a suggestion:**

1. **Finish the CW 9i arc** — windows 8, 9, 10. (Window 8 is currently HELD at
   prechecked on Fable capacity; see `pipeline/state.json`.)
2. **Run the seeded-corruption pass over the family layer**, against the ruleset
   as it stands at arc close — the item 5 recalibration, using the existing
   `corrupt_family_assignments.py` harness with a fresh seed and the threshold
   set in advance.
3. **Then the codebase update** — fold v0.6 (item 1), build the map (2), write
   the page (3) under its anti-overclaim checklist, wire the version/calibration
   CI check (5) and the continuous seeding with its strip step and marker
   assertion (6).
4. **Only then further mining** — the CW 8 arc, per `docs/PROPOSAL_NEXT_ARC.md`,
   and not before the maintainer's explicit go.

The reason for this order: the codebase does not change mid-arc, so a window is
never mined under a ruleset different from the one its neighbours got; the
measurement happens before the rebuild, so the rebuild cannot be tuned to it;
and the new instruments are standing before the next arc's material — CW 8's
energetic register — arrives to stress them.

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

   **Anti-overclaim checklist — binding on the copy, and the reason this page is
   riskier than the method page.** The method page describes checks against a
   text; this page describes a classification of Jung's thought, where a confident
   register would be asserting an interpretive position we have never tested
   outside this repo. Every line below is a claim the page must NOT make, paired
   with what it says instead:

   - NOT "verified families" or any reuse of the verification vocabulary. A
     family is ASSIGNED, not verified. The word "verified" belongs to the quote
     and its paragraph, and using it twice for two different kinds of evidence is
     precisely the conflation the ledger's two row types exist to prevent.
   - NOT "the gate catches errors" full stop. It catches the errors we know how
     to plant. Say the class, say the numbers, bind them to the ruleset version
     they measured (items 5 and 6), and say plainly that a caught planted error
     is evidence about the instrument, not about Jung.
   - NOT any implication of scholarly consensus. Until item 4 runs, the page must
     state that the families are OUR classification, internally calibrated and
     externally unvalidated — no secondary literature has been consulted, and
     where scholars would disagree is unknown. If item 4 has run, report its
     disagreements on the page, not only its agreements.
   - NOT a tidy total. Show `no-family`, `text-undecided` and the pending queue
     with real counts beside the assigned ones, and show the homeless relation
     strings from (2). A vocabulary that covers everything is a vocabulary that
     has stopped discriminating.
   - NOT "families reveal the structure of Jung's thought" or similar. They
     record how WE sorted relations he wrote. The graph is a map of assertions,
     not a reading — the same sentence the method page already carries, and it
     applies harder here.
   - Model agreement is not correctness. The 86% two-arm figure means the
     document is followable, not that it is right; neither arm is ground truth
     and the definitions' author is one of the model families. Say that where the
     number appears, not in a footnote.

   Have the copy written by a family that did not author FAMILY_DEFINITIONS, and
   run the standing copy assertion over it (banned phrases, count-like literals
   bound to atlas.json tokens) before it ships.

4. **External-validity sampling against Jungian scholarship — the load-bearing
   one, and the reason to do it BEFORE publishing (2) and (3).** The author's
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

5. **Recalibration as a release gate on the ruleset — and the CI question,
   assessed.** The family gate's calibration (`corrupt_family_assignments.py`,
   19/19 on 2026-08-06, 20/20 with 38/40 specificity on 2026-08-07) has been run
   twice by hand and is wired into nothing. Both runs measured a gate reading
   FAMILY_DEFINITIONS v0.4/v0.5 — including the amplification layer-override rule
   the 2026-08-10 sitting retired, and the harness plants
   `amplification → correspondence` swaps as one of its near-miss cases. So the
   published sensitivity figures describe a ruleset that is about to change.

   **The gate, proposed:** a FAMILY_DEFINITIONS version does not ship until the
   calibration has been re-run against that exact version. Sequence at the v0.6
   fold (natural moment: the CW 9i arc close, when the accumulated rulings get
   folded anyway): fold rulings → re-run the corruption harness on a fresh seed →
   gate it with a family that did NOT author the definitions → score sensitivity
   AND specificity → commit a calibration record → only then may the version, or
   any page citing its numbers, ship. Set the pass threshold BEFORE seeing the
   result, per the standing precedent from the normalization step-0 sample; the
   near-miss class (K1) is the one that must hold, since far-misses catch
   themselves. Bind the method page's sentence to the version it measured
   ("against v0.6, dated") so it cannot silently go stale again.

   **THRESHOLD — SET 2026-08-12, BEFORE THE RUN. Does not move after the result
   is seen (editorial ruling, same rule as the normalization sample):**
   - **PASS requires every K1 near-miss caught with the correct family named**
     (measured precedent: 8/8, then 20/20 overall at recalibration). One K1
     miss = FAIL → the missed boundary's wording is sharpened in the
     definitions doc and the calibration re-runs with a fresh seed. K2/K3/K4
     misses also fail the run — a gate missing a far-miss or a sink-swap is
     broken, not miscalibrated.
   - **Specificity is reported, never gating.** Below 85% (the measured
     first-run floor) it triggers a manual look at each false flag — precedent
     says some "false" flags are real errors in the uncorrupted set — but no
     automatic verdict either way.
   - Quotas per the standing harness (8 K1 / 4 K2 / 4 K3 / 3 K4, remainder
     clean), fresh seed drawn at run time and recorded; input drawn from the
     graph's CURRENT assigned edges, not the 2026-08-06 proposer file; planter
     and gate from different model families, gate blind to the key, as before.

   **CI assessment — the calibration itself cannot live in CI, and mining volume
   is the wrong trigger.** Three hard blockers: it requires paid,
   non-deterministic model calls (CI today is fully offline and deterministic);
   it needs the Gemini key, which must never reach the repo or a runner; and its
   inputs sit in `pipeline/work/`, gitignored by design. A fourth, subtler one:
   re-running a stochastic gate on every push would produce a flapping red build
   that teaches everyone to ignore it.

   What CI CAN do, cheaply and deterministically, is refuse to let the version
   drift away from its calibration: commit a small tracked calibration record
   (version, date, seed, n, sensitivity, specificity — numbers only, no corpus,
   no keys), then extend `tools/check_paper_facts.py` with a STALE DOC check in
   its existing shape — if FAMILY_DEFINITIONS declares a version with no matching
   calibration record, fail with the literal expected string. That is the
   mechanism the tier-3 docs lacked when they drifted; the same fix applies here.

   On "does more mining change this": more windows add edges, not rules, so
   mining alone does not invalidate a calibration. But new registers stress the
   vocabulary in new ways — CW 8's energetics and CW 11's doctrinal material are
   both expected to force family revisions — and each revision bumps the version,
   which trips the gate. So the gate fires on ruleset change, and mining is what
   makes ruleset change happen. Wiring it to the version is strictly better than
   wiring it to a window count.

6. **Continuous seeded corruption during the per-window family sweep** (editorial ruling,
   2026-08-10). Item 5 makes the calibration fire on ruleset change; this makes
   it fire continuously. Plant a small number of corrupted assignments into each
   window's family stage and measure what the gate returns, so the instrument is
   watched between versions rather than trusted between them. The repo already
   runs exactly this pattern one layer down: the quote canaries plant seven
   corruptions on every test run and fail the build if any survives. The family
   layer has no equivalent, and that asymmetry is the weakest joint in the trust
   story — citations are continuously probed, their classification is not.

   **Injection point: the gate's input, never the arms'.** The two blind arms are
   proposers; corrupting what they see corrupts the proposal. What gets planted
   are wrong assignments slipped into the stream the gate reviews,
   indistinguishable from real ones. The gate is already a stateless call blind
   to any answer key, which is what makes this possible at all.

   **Contamination is the one risk that could reach the published graph**, so it
   needs three defences rather than one: every planted item carries a synthetic
   marker; a strip step keyed to that marker runs before merge, unconditionally;
   and CI asserts no marker survives in `seed.json`. That third check is
   deterministic, offline and free — so unlike the calibration in item 5, this
   design gives CI something real to enforce.

   **Read it as a trend, not a per-window verdict.** Five planted items in a
   ~40-edge window carries no statistical weight alone; fifty across ten windows
   shows whether the gate is decaying. Drift is precisely what a one-off
   calibration cannot see, so the accumulating read is the point, not a
   limitation.

   **It measures reliability, not validity — and the page must say so.** A caught
   planted error proves the gate still catches the errors WE know how to make. It
   says nothing about whether the families carve Jung's thought correctly; that is
   item 4's question and no internal instrument can answer it. Stated carelessly
   ("we plant errors and catch them all") this reads to an outsider as a far
   stronger claim than it is — the kind of overclaim the r/alchemy critic caught
   us in once already.

   **It does not replace item 5.** Live windows contain only whichever families
   that material happens to use, so coverage is opportunistic and would rarely
   hit the specific boundaries a version revision changed. Focused recalibration
   gives stratified coverage of new rules; continuous seeding watches for decay
   between versions. Two jobs, both needed.

   Cost: roughly 10–15% overhead on the gate stage per window.

7. **Blind code inspection findings (2026-08-12) — fold into the step-3 codebase
   update; items marked PRE-STEP-2 must be fixed before the calibration runs.**
   An independent Fable agent read the family-layer code with all comments and
   docstrings mechanically stripped, no access to docs or intent. Its verdict on
   the corruption harness: "a one-shot demo, not an instrument — it proves
   flagging, not diagnosis; it measures the easy stratum by construction; and
   its evidentiary chain is already broken on disk." Findings, ranked as the
   inspector ranked them:

   - **PRE-STEP-2. No provenance binding between plant, gate, and score.** The
     chunk runner skips any chunk whose output file exists; the scorer globs
     whatever chunk files are present and checks nothing against the key. One
     concrete failure: replant with a new seed, re-run the gate (all chunks
     "already done, skipping"), score — the new key is scored against the OLD
     verdicts, silently, with plausible numbers. Fix: stamp the plant seed into
     every artifact and make score() refuse mismatches; delete stale chunks on
     replant.
   - **PRE-STEP-2. Detection is credited without diagnosis.** score() never
     compares the gate's should_be against the planted was — "flagged for any
     reason" counts as caught, and PARTIAL (defined in the prompt as "usable but
     a better family exists") is scored as full detection. The threshold set
     2026-08-12 requires "caught WITH the correct family named"; the code
     cannot currently measure that. Fix: score should_be == was, and score
     PARTIAL separately from WRONG.
   - **PRE-STEP-2. Fabricated confidence in the new population builder.**
     build_calibration_input.py stamps confidence:"sure" on every drawn edge,
     which (a) makes everything corruption-eligible, silently changing what the
     eligibility filter means, and (b) feeds a fictitious proposer_confidence
     signal to the gate. Fix: drop the fabricated field; make eligibility
     explicit (arms-agreed IS the population's confidence basis) and stop
     forwarding a proposer_confidence the population does not have.
   - **PRE-STEP-2. Hallucinated item numbers count as clean.** The runner
     rejects only missing n's; extra invented n's pass through and the scorer
     counts them toward specificity. Fix: reject supersets too.
   - **PRE-STEP-2. Quota stall.** An ineligible pick is re-appended to the end
     of the eligible list and immediately re-drawn forever, burning the rest of
     that class's quota (concrete: a correspondence tail item when K3 starts).
     Fix: skip-and-continue instead of re-append, assert quotas met.
   - **PRE-STEP-2 (cheap). Corrupted items get reason="" while clean items keep
     prose reasons** — harmless today only because the gate happens not to
     forward reasons; a perfect corrupted/clean marker if any future gate does.
     Fix: blank all reasons in the gated file.
   - **STEP-3. The ledger tooltip overclaims.** Every "assigned" edge gets
     "both model arms agreed and the calibrated gate checked the assignment" —
     including the 20 human-adjudication and 2 gate-disputes-agreed edges,
     and no committed code shows a gate run over the full production pass at
     all. LIVE OVERCLAIM on the site; text must derive from the by field.
   - **STEP-3, structural. Most of the family layer is artifact-only.** Input
     builders, the Opus arms, the 1,146-edge agreement/assembly into seed.json,
     the recalibration harness, and the per-window sweep runner/merger exist as
     outputs with no committed code (the sweep runner lived in a session
     scratchpad and was lost; recreated 2026-08-12). The calibration's own key
     files were deleted — score() currently crashes; the published 19/19 and
     20/20 rest on artifacts that cannot be regenerated from the repo. Fix:
     commit every family-layer script (they contain no corpus text); the
     step-2 rerun then supersedes the unauditable numbers with auditable ones.
   - **STEP-3. Failed Gemini full-pass chunks are never retried** without
     hand-editing the failures file, and nothing downstream is forced to
     notice the hole.
   - **NOTED, for the record: gate independence is nominal.** The calibration
     gate model is the same model as one production proposer arm (both
     gemini-3.1-pro). Within-vendor role separation, not cross-vendor. Any
     public sentence about the family gate must not imply otherwise.

## Release notes and the v2.0 milestone (added 2026-08-12, on the author's direction)

**A. Release-notes section on the website, going forward.** Every release from
the next one onward gets a notes page: what changed in the graph, the ruleset
version shipped (per the version-pin rule in CLAUDE.md), instrument changes
with their calibration records, and anything withdrawn or corrected. Same
register as the method page — the ledger tells a reader what IS; the notes
tell them what CHANGED and why. Candidate implementation: a `/releases` page
built from a `docs/RELEASES.md` that the ceremony appends to, counts bound by
the copy contract.

**B. v2.0 — the milestone sketch (the decisions are the author's; this is the candidate
scope, not a commitment).** Current sequence stands: v1.4 (trilogy + family
layer, waits on arXiv), v1.5 (Aion + the vocabulary-transfer study). v2.0 is
the right label for the release where the graph stops being only a verified
record and becomes a queryable instrument:

1. **CW 8 mined** (fourteen windows, §1–997, per PROPOSAL_NEXT_ARC.md) — the
   theoretical register in, after its pre-arc external check on
   psychic-effect / dependence / instrumentality.
2. **The query layer** *(slice 1 SHIPPED 2026-08-13: declarations with rulings log, kg_query.py with closure and walks, tests, RDF export rdflib-validated — merge 4648674; remaining: site facets, query UI)*: family-aware querying (the map as query surface),
   declared inverses and symmetry applied at read time, an upgraded query.py
   (filter by family, provenance, claim_type, volume, state), and the
   RDF/Turtle export with the families as subPropertyOf super-properties —
   the W3C shape the design already claims, made demonstrable.
3. **Family layer complete under a stable ruleset**: the amplified-by re-run
   merged (v0.7.1), the adjudication queue drained to ruled-or-recorded, and
   a second external spot-check on the families CW 8 stresses.
4. **Ontology QA items worth fixing by then**: the detached Shiva/Shakti
   component, the 19 definition-shaped node labels, the three
   both-direction inverse duplicates. The 30-node identity chain stays — the
   no-transitivity ruling is a feature; v2.0 ships the depth-bounded
   identity-walk view instead of a collapse.
5. **Release-notes page live** (item A), with v2.0 as its first full entry.
6. **Ontology page re-aligned with the v2.0 paper's §4** (added 2026-08-18,
   release chat). `/ontology` (3,250 words) predates the layered-warrant
   vocabulary. It keeps the two-tier idea and the verified/assigned split,
   which stay, but at release it must carry: the naming ("a provenance-bearing
   assertion graph with a governed semantic overlay", the deliberate
   non-goals as decisions), the four layers A–D with the `salt symbolizes
   the-self` walk-through, the warrant ladder with populations bound from the
   graph (Human-agreed at 0, stated), seven active declarations and the
   derived-row count at closure, the normalization token-cap fact (104 of 260
   over the proposal's cap, or the amended cap once Damian rules), and the
   pitfall scan re-rendered with two severity axes (conventional pitfall vs
   operational impact here; triage item F26). Copy change: needs Damian's
   review before any deploy that carries it; the data-redeploy authorization
   does not cover it. Same pass should re-read `/families` and the method
   page for the same vocabulary drift.

Not in v2.0: CW 11 (needs the exegesis clause and a minting-aware budget —
the arc after), CW 5/16, any NL query interface (verification-first: a
query layer that cites edges precedes any interface that paraphrases them).

### v2.0 candidates from the 2026-08-12 night session — ledger and families reporting (proposals only)

The author asked for thinking on ledger and families query/reporting. Recorded
here so the morning finds it; nothing below is committed scope.

1. **Assignment history on the edge.** The v0.7.1 re-run overwrote 43
   `relation_family` values in place; the prior assignment survives only in
   git. Add `relation_family.history` — each reassignment appends {value,
   ruleset version, date, by} — so the ledger can show "amplification
   (v0.6) → archetypal-identity (v0.7.1)" on the edge itself. The single
   biggest auditability gain available, and it must land before the queue's
   19 re-run splits are ruled, or their history starts incomplete.
2. **Ledger facets and permalinks.** The ledger is one long page. Add
   client-side filters (volume, batch, claim_type, verification state,
   family, provenance) and stable per-edge anchors so atlas rows and
   external citations can link straight to a ledger entry.
3. **Per-batch delta pages.** "What changed in b-cw8-3": edges added,
   families assigned, queue growth, evidence-mix shift. Generated at merge
   time by the existing ledger builder; doubles as the raw material for the
   release-notes page (item A above).
4. **Per-family pages.** Definition excerpt, live counts, string map slice,
   seed examples, pending-queue items for that family, and its
   external-validity row (extend results.json with the per-family table
   from report v3 so the numbers interpolate, not get typed).
5. **Queue analytics for sittings.** Auto-rank the pending queue by
   disagreement shape (identity|correspondence 14, composition|position 13,
   ... as of tonight) and surface the governing boundary rule beside each
   shape — the sitting starts where the mass is.
6. **Query-to-citation export.** `kg_query.py --cite` emitting an edge list
   with quotes and CW citations in a copy-pasteable scholarly form — the
   graph answering a question WITH its receipts is the whole point of the
   instrument.
7. **State-of-the-graph report generator.** One command: counts, family
   distribution and provenance mix, per-volume evidence mix, queue health,
   calibration status, external-validity status. Run at each release; its
   output is most of a release note.

## v2.1 — bug fixes and minor enhancements (opened 2026-08-14)

1. **Sort the query panel's dropdowns** — the family dropdown especially
   (alphabetical; volumes already follow collection order per V2-R8). Ruled
   by the maintainer at the v2.0 review. DONE 2026-10-31 for the family list;
   the state and claim-type lists stay in count order.

2. **Site copy pass from the humanizer review** (scheduled for the next
   release, Damian 2026-10-22; build track). Source:
   docs/SITE_COPY_REVIEW_2026-10-22.md, a page-by-page review of every text
   source on symbolicworld.observer with a suggested rewrite per hit. Four
   patterns carry most of it: the same closing sentence repeated across pages
   ("a map of assertions, not a reading" on the method page, the design page
   and all 25 family pages; "per edge in its paragraph, never per string" on
   the families index, every family page, the SPA lede and seven pitfall-table
   rows; the proposer-never-signs-off mantra in four wordings; "agreement is
   not endorsement" twice), "X, not Y" as the default way of stating a limit,
   em dashes splicing clauses on nine pages, and colon-led reveals. Files
   the pass touches: docs/METHOD_COPY.md, web/build-atlas.mjs (design,
   families, family-page, releases and support copy), web/src/main.js (the
   families lede), web/index.html (meta description), docs/RELEASES.md (the
   "(Damian, 2026-08-19)" attribution leaks to the public page), and the
   poster source in docs/figures (two dash pairs, the "marks its own homework"
   line, and a count re-render: the image says 653/2,420/3,180, the site
   661/2463/3248). Constraints: the method copy is Damian's own rewrite of
   2026-10-18, so each edit there is proposed to him, not applied; the family
   definitions stay untouched (the site quotes them verbatim and a ruleset
   change voids its numbers by rule); the batch-page mining logs are a
   register decision for Damian, not a rewrite. The copy contract and the
   poster-facts gate run as usual after the pass.
   APPLIED 2026-10-22 and deployed with v2.1 (commits 893be5b and 5934863;
   the six method edits on Damian's go). Still open from it: the two register
   rulings (batch-page mining logs, the per-card ledger line).

3. **Family pages: a second humanizer pass** (Damian, 2026-10-22, after
   reading the live correspondence page: "look like they need humanization").
   The first pass only cut the closer and the repeated catchphrases. What the
   page still carries, in two layers with two owners:
   - The page template (build track, the family-page block in the atlas
     builder): "That was already done before any of this began", "The tail is
     the informative part:", "which is not the same as belonging here", "the
     queue is not a backlog", "A row this small is the items themselves", the
     "Agreement is not endorsement" line. Contrast forms and colon reveals
     throughout. Note the anti-overclaim test requires the agreement limit
     stated outside the fold on every family page, so reword that sentence
     and keep it.
   - The quoted definition and boundary text (Track B, the family definitions
     document): the site states it quotes the document and never paraphrases
     it, so "The workhorse of the comparative method", the em dash in
     "structural likeness asserted without identity", the caps emphasis and
     the "not X; not Y; not Z" boundary triads can only change in the
     document itself. A wording-only bump (v0.7.3, changelog entry saying
     wording only, no boundary moved) still needs a fresh calibration PASS
     record, because the paper-facts check refuses any ruleset version
     without one. Decide first whether that cost is worth it or whether a
     ruleset may read like a ruleset.
   Do the template layer first; it ships as a data-free UI change under the
   usual review.

4. **"807 symbols" should say "807 concepts"** (Damian, 2026-10-31, for the
   next release). The count is every node in the graph, of six kinds
   (concept, figure, symbol, motif, operation, substance), and "symbol" names
   only one of them. The README and the concepts index already say
   "concepts". Two places in web/src/main.js: the counts line in the atlas
   header, which the landing page also shows, and `KIND_LABEL.node` in the
   search results. While there, check that the same line's "cited claims"
   matches the site's word for a reference ("citations" on the concepts
   index). A data-free UI change under the usual review.
   DONE 2026-10-31: "symbols" became "concepts" in three places, and
   "cited claims" became "citations" in two.

5. **The atlas volume bar looks blurry in the day theme** (Damian,
   2026-10-31, for the next release, with a screenshot). Cause: the bar's
   background band in web/src/style.css (`#works`) is hard-coded to the night
   ground, `rgba(11, 10, 8, 0.92)`, so in day it paints a near-black band
   across a light page, and the labels' halo (`text-shadow` in
   `var(--ground)`, light cream in day) glows around dark letters on that
   band. Fix: draw the band from the theme's own ground (for example
   `color-mix(in srgb, var(--ground) 92%, transparent)`) and check the label
   and count colours against it in both themes. A UI change under the usual
   review.
   DONE 2026-10-31: the band draws from `var(--ground)`; checked in both
   themes.

6. **robots.txt: opt out of the two training tokens Cloudflare cannot block
   at the edge** (Damian, 2026-10-31, via the outreach session, for the next
   release; it ships with that release). Google and Apple train on
   what their search crawlers fetch, so the opt-out has to be a robots group.
   Add to web/public/robots.txt:

       User-agent: Google-Extended
       Disallow: /

       User-agent: Applebot-Extended
       Disallow: /

   Keep the `User-agent: *` / `Allow: /` group and the Sitemap line as they
   are. Background, checked on the live site 2026-10-31: Cloudflare AI Crawl
   Control already returns 403 to training crawlers (GPTBot, ClaudeBot) and
   200 to search and agent crawlers (OAI-SearchBot, PerplexityBot,
   Claude-User). Google documents that Google-Extended has no effect on Search
   inclusion or ranking. Bot Preference Sync stays off, so the repo's
   robots.txt remains the only source. Acceptance: the built robots.txt
   carries both groups and the `*` group, and preflight and pytest pass.

## From reader feedback: issue 2 (added 2026-10-22, on the author's direction)

Source for both items: GitHub issue 2 on damianspendel/symbolic-world, raised
2026-08-28 by an outside reader. Backlog only. Nothing here is scheduled and
nothing is to be built. Figures are as of 2026-10-22.

1. **Attribution-aware mining around quotations** (future major release).
   Mine around the places where Jung quotes or reports another author,
   reading the neighbouring sentences to settle who is speaking and what Jung
   does with the claim. Trigger case: CW 14 §136, "Paracelsus likewise calls
   sulphur the soul", is not in the graph; Paracelsus carries 4 relations and
   5 references. Constraints: this re-mines covered ground, and the standing
   rule is one mining pass per window, ever, so each window needs the
   author's explicit override, named per window. It belongs after the first
   pass on the key volumes is complete (CW 11 is mid-arc; CW 5 and CW 16 are
   unmined). The miner-blinding rules apply to any new prompt.

2. **A human editorial layer for connections no sentence of Jung's makes,
   with a governed process.** Trigger case: "Mary (Mother of God)" (17
   relations) and "The Assumption of Mary" (3 relations) have no direct
   relation; the identity-drift gap is already listed among the known limits
   on the method page. The design question is a layer in the atlas's own
   voice, a fourth voice beside Jung asserts, Jung reports doctrine and Jung
   quotes a named source: each connection made by a person, labelled
   editorial and never attributed to Jung, with the reasoning recorded, kept
   apart from the sourced graph and switchable off by the reader. It also
   covers canonical figures with several representations. Constraints: every
   existing rule on sourced claims stays untouched, and a design document
   comes before any build.

## v2.4.0 scope (added 2026-11-10 as v2.3.0 scope; relabelled 2026-11-11)

Damian's scope, set on 2026-11-10. On 2026-11-11 he made that day's build v2.3.0 ("I think this becomes 2.3.0 and we bump friday to 2.4.0") and moved the rest to v2.4.0 on Friday 13 November, with the /query autocomplete added ("/query autocomplete is Friday please"). The data through CW 6 and the RDF export shipped in v2.3.0. The trilogy pass and his paused rulings go to a later release. v2.4.0's data stays at v2.3.0's seed unless Damian says otherwise.

- The data through CW 6.
- The RDF export, with the vocabulary and the proposer attribution (section below).
- The work pages, behind `EMIT_WORK_PAGES` and his localhost review (section "Work pages").
- The Bookshop.org links. These wait for his affiliate ID, his edition choices and his disclosure wording.
- The glossary pass, with Vale and the declauding skill.
- The SSH Open Marketplace entry, after the DOI.

## v2.3.0: the RDF export (added 2026-11-05)

`exports/` is gitignored, because the export moves with every merged window. At the freeze, run `python3 tools/query/export_rdf.py --out-dir exports/rdf`, remove `exports/` from `.gitignore` and commit the three files, so the tag pins them. The Turtle files come to about 6.7 MB.

Quotes: Damian ruled on 2026-11-05 that readers find them elsewhere, so the export carries none (`QUOTES_MODE = "omit"` in `tools/query/export_rdf.py`). Still open: the namespace, which waits on his w3id.org registration and goes live only after `/vocabulary` is deployed, and how to handle the four names in the CC BY file that still share eight or more words with a quote (`KNOWN_NAMES_REPEATING_THE_SOURCE` in `tests/test_query.py`).

Namespace blocker cleared (2026-11-10). davidlehn merged perma-id/w3id.org PR #7091, "Create .htaccess for Symbolic World redirects", on 2026-11-06 at 19:52 UTC. The summary chat tested the redirects on 2026-11-10: `w3id.org/symbolicworld/ns` answers 303 to `/vocabulary`, `/node/anima` 303 to `/concept-anima`, `/family/privation` 303 to `/family-privation`, and `/data/` 302 to doi.org/10.5281/zenodo.21631523. Relation, edge, claim, reference, stage and agent IRIs answer 303 to `/vocabulary`. The export still uses its provisional base (`namespace_provisional: true` in `tools/query/vocabulary.json`). Switching it to the w3id base IRI is part of the v2.3.0 build. The four names that repeat words from a quote are still open.

The proposer gap (added 2026-11-06, Damian: "send the proposer gap to the build chat"). Each `sw:Claim` records its gate and its audit but not the miner run that proposed it, so a reader of the PROV-O cannot trace the rule that the proposer never signs off. The TGDK paper will point reviewers to the export. Not built: the export stays as it is until Damian decides.

What the records hold, counted over the 4,559 references at b-cw16-5:

- 221 references (b-cw9ii-3 to -7): the candidates file names the model, `claude-opus-5`.
- 1,741 references: `state.json` names the proposer as Opus, by family only, either in the batch's own note (b-cw9ii-1, b-cw11-10, b-cw16-1 to -5) or in an arc-close note that covers every window (CW 9i, CW 8).
- 1,931 references in 37 batches (CW 5, CW 11 except window 10, CW 12 windows 5 to 9, CW 13, b-cw9ii-2, b-union-2): the batch id is known from the audit string, but no record names the proposer. Only the procedure does: the mining task's brief says "Opus subagent". For b-cw11-8 the note says the firing ran steps 1 to 3, mining included, in a Haiku 5.5 session, and does not say which model the miner subagent ran on.
- 666 references from the July pipeline (CW 14, the incidental volumes, the retro gates, the E6 and E7 audits, and the 194 with no audit): no batch id in `seed.json`, and neither the candidates files nor the July commit messages name a miner.

Proposed shape:

- One `sw:Proposal` per batch, `swk:proposal-<batch>`, which already exists as a class and is used today for normalized forms. Each claim links to it with `prov:wasGeneratedBy`, which is in PROV-O and needs no new term.
- `prov:wasAssociatedWith` the model agent only where a model id is recorded (the 221). Everywhere else in the first two groups, a literal giving the record's words, such as "Opus-family miner subagent", and a second literal naming where the attribution comes from (candidates file, batch note, arc-close note).
- No date. The records give the gate and audit dates, never the mining date.
- The last two groups get no Proposal stage, as the ontology reads a missing rung: the record does not show it. Whether the mining procedure counts as a record for the 1,931 is Damian's call. Recorded today, the export could name a proposer for 1,962 of 4,559 references (43%).

New terms: two datatype properties on `sw:Proposal`, a proposer-as-recorded literal and an attribution-source literal, in `tools/query/vocabulary.json` (which writes both the OWL file and `/vocabulary`). The comment on `sw:Proposal` and the export header both say claims have no Proposal stage, and both change. The notes for the TGDK paper say the same and need the new count. For the forward fix, the mining task can write the miner's model id into each candidates file, as the five Aion files did, so new batches land in the first group.

Ruled and built (Damian, 2026-11-06: "yes to both proposer decisions"). The documented procedure counts as a source, labelled as such. The table is `tools/query/proposers.json`, and each attribution in it is tested against the record it cites. In the export, a claim links by `prov:wasGeneratedBy` to `swk:proposal-<batch>`, which carries `sw:batch`, `sw:proposerAsRecorded` and `sw:attributionSource`. Counts at b-cw16-5: "record" 1,962 claims (221 with the agent `claude-opus-5`, 1,741 by family only), "procedure" 1,871, none 726 (the 666 July references and b-cw11-8's 60). `sw:batch` now has the domain `sw:Stage`. Still open: a new batch counts as "procedure" until it gets a "records" entry, so once the mining task writes the miner's model id, adding that entry is a step of each merge.

## v2.4.0: book links to Bookshop.org (added 2026-11-06 for v2.3.0; moved 2026-11-11)

Damian's decision: "add the book links (Bookshop.org) to the build backlog for 2.3.0." Backlog entry only, nothing built yet. It is the site's first revenue feature.

- One "get this volume" link per Collected Works volume, placed where a citation names its volume: the concept pages, and the works bar in the atlas, which is the only volume list today. A page links each volume once, however many of its citations come from it.
- The links carry Damian's Bookshop.org affiliate ID. He signs up for the programme himself, and the build waits for his ID.
- Bookshop.org runs separate US and UK sites and does not cover Switzerland. For each volume Damian picks the site and the edition (Princeton/Bollingen or Routledge), and the map records both beside the link.
- A one-line affiliate disclosure on the site, in Damian's wording.
- The map covers the same volumes as the volume title map, `VOL_LABEL` in `web/build-atlas.mjs`. That map has CW 5, 8, 9i, 9ii, 11, 12, 13, 14 and 16 today. The mining chat needs CW 6 and CW 7 added to it before the first deploy that carries citations from them, and the book-link map gets the same two entries at the same time.
- Plain links only. No tracking script, and nothing beyond the affiliate parameter in the URL.

## After the v2.3.0 DOI: list the dataset in the SSH Open Marketplace (added 2026-11-06)

Damian's decision: "add to 2.3". The entry goes on marketplace.sshopencloud.eu as entry type Datasets.

- Damian signs in with MyAccessID and submits the entry himself. Nothing in the build submits it.
- It waits until the v2.3.0 tag and GitHub Release have minted the Zenodo version DOI, so the entry can cite that DOI beside the concept DOI, 10.5281/zenodo.21631523.
- The fields: licence (CC BY 4.0 for the data, with the quotation exclusion as NOTICE states it), maintainer, both DOIs, and https://symbolicworld.observer.
- The build's part is the text Damian pastes in: title, short description, keywords, licence line and DOIs. The description goes through Vale before he gets it.
- Before preparing that text, re-read the live contribute page on the marketplace. The earlier research read it from a mirror, so the field list may differ.

## v2.4.0: run Vale over the glossary (added 2026-11-06 for v2.3.0; moved 2026-11-11)

Damian's decision: "add to backlog for 2.3.0 to run vale over the glossary entries". Backlog entry only, nothing edited yet.

- The file is `docs/GLOSSARY.md`, 39 entries. Vale reported 78 hits on 2026-11-06, all in the entries written in August and September. The mining trends entry added that day has none.
- By rule: 55 passives, 18 filler adverbs, 3 antithesis tags and 2 contrast lines.
- The glossary's opening says the entries keep the words Damian got at the time. So the pass proposes each rewrite to him, old wording beside new, and changes an entry only on his yes.
- A passive stays where the entry does not care who acts. Those hits get a note saying why, and no edit.
- No definition changes meaning. The pass is wording only, and it ends with the hook run again and the remaining hits listed.
- 2026-11-10, Damian: "update to 3, the vale pass, this skill https://github.com/oaustegard/claude-skills/tree/main/declauding". The pass now runs Vale and the declauding skill. Install and run the skill as the section "Prose review by Fable 5.2 with the declauding skill" sets out.

## Work pages (added 2026-11-10)

Damian's decision on item A5 of spec-reader-v1: "backlog work pages, until we've mined CW 6 and before the trilogy". Backlog entry only, nothing built.

- One page per work at `/work-<id>`: title, volume, years written and revised, coverage as "claims from N of M paragraphs", the most-cited concepts in the work's paragraph range, and the claims in paragraph order. An index at `/works`. Each concept page gains an "appears in" line.
- The data exists: `works.json` at the repo root (commit 9da0c608, 73 works over the eleven extracted volumes, with a tiling test).
- Timing: after the mining chat finishes CW 6, before the trilogy. Build it behind a gate `EMIT_WORK_PAGES`, switched off until Damian has reviewed it on localhost.

## Prose review by Fable 5.2 with the declauding skill (added 2026-11-10)

Damian's words: "apparently Fable 5.2 has better prose. add to the backlog, for Fable 5.2 to install the skill 'declauding' and review AI generated text." Backlog entry only. Nothing installed, no review started.

- A Fable 5.2 session installs the declauding skill and reviews the AI-generated prose. On the site that is `docs/METHOD_COPY.md`, the concept-page template in `web/build-atlas.mjs`, the vocabulary page and `docs/GLOSSARY.md`. In the docs it is `README.md` and the release notes (`docs/RELEASES.md`, `docs/releases/`).
- Nobody has found the skill yet. It is not in `~/.claude/skills`, and a search of the claude.ai skills catalog for "declauding" returns nothing. Before any session installs it, Damian names its source and someone reads the skill in full.
  - Answered 2026-11-10. Damian named the source: github.com/oaustegard/claude-skills, folder `declauding`, MIT licence, latest commit 6baa7290 (10 Nov 2026). The summary chat read its README and hook that day, and these points come from that reading.
  - The folder holds `SKILL.md`, references, five Python scripts and `hooks/hooks.json`. The hook is a Stop hook that runs `scripts/fresh_eyes.py hook` when someone installs the folder as a plugin. Install the skill folder alone, without the hook, unless Damian decides otherwise.
  - `declaude_review.py` sends headers and opening and closing sentences to Gemini when `GEMINI_API_KEY` is set, or to Claude when `ANTHROPIC_API_KEY` is set. With neither set, it prints the prompt for an agent to answer. Run it with neither key set.
  - `declaude_rank.py` needs torch and transformers. Leave it out.
  - Pin the commit you install. Read `SKILL.md` and every script in full before installing: the summary chat has not read them.
- Fable 5.2 reviewing text Opus wrote keeps proposer and verifier in different model families. Text Fable wrote needs a reviewer from another family. `docs/METHOD_COPY.md` is one such file: the Fable session authored it, per the comment beside `methodPath` in `web/build-atlas.mjs`.
- The review proposes edits only. Damian approves each change, and the approved set comes with a "Changes in this pass" list.

## Concordance redesign, for the build after the trilogy re-mine (added 2026-11-10)

Damian's decision: "put the link to the existing stuff back tomorrow. Add the rest as backlog items for the build that comes after alchemical remining." The interim build of 11 November returns the concordance menu link only. The items below come from a read-only Fable 5.2 review of 10 November (`concordance-review-2026-11-10.md` in the summary chat's notes folder). The summary chat checked five of its figures against `seed.json` and `web/src/atlas.json`. The grades are the review's.

A, B and C need no mining. The review put them first, and Damian deferred them to this build by his own choice. The review's seven proposals for the miner brief go to the mining chat, not here.

- **A. A static `/concordance` page in landing-page style, replacing the app view.** High. One indexable page with the pairs grouped by alchemical term. Each row shows the term, the psychological concept, the relation, CW and paragraph, and one quote already on the site. Needs code in `build-atlas.mjs` only, emitting from the existing `concordance` object, and the landing card and menu repointed. About a day. It removes 424 lines and the bridge payload from the atlas page. If repeating quotes across pages matters, show the citation and link the concept page.
- **B. An "In the concordance" block on alchemical concept pages.** High. Each laboratory-side page lists the psychological concepts Jung reads it through, linked both ways to `/concordance#term`. Site code only, about half a day. No per-pair pages: the review counts about 217 thin URLs against them.
- **C. A register for figures.** High. Mercurius, Filius Philosophorum, Rex and the Anthropos on the laboratory side, Anima and Animus on the psyche side. Needs an explicit list in the build, like `LAB_CONCEPTS`, with each assignment ruled by Damian, about 30 figures. An hour of code plus his review.
- **D. Latin names and aliases in titles, descriptions and search.** High. "arbor philosophica" as a searchable name, and "also called" lines from the 22 `synonym-of` edges. Needs `latin` on about 250 laboratory nodes. The build can lift about 20 from labels now, and the re-mine supplies the rest. Low cost for the first 20, medium after.
- **E. The opus as an ordered route.** Medium now, high after the re-mine. One ordered section on `/concordance`: nigredo, albedo, citrinitas where the data has it, rubedo, each with its operations and psychological reading, replacing the two guided walks. Needs stage and sequence data, most of which the re-mine has to supply. Medium cost.
- **F. An index of the alchemists and texts Jung cites.** Medium. A section on `/concordance`, not a new page: Dorn, Maier, Khunrath, Zosimos, the Rosarium and others, each with the claims Jung quotes or reports from them. Needs a normalized source field. Today 383 of 5,292 references carry a free-text `source`. Low cost for the code, and the data comes from the re-mine.
