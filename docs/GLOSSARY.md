# Glossary

**What this file is.** Plain-language definitions of the terms this project runs on, one
entry per concept, alphabetical.

**Where it came from.** It was not written from the documentation. Across the project's
chats Damian kept stopping the work to ask for the ELI5: what does this mean, explain it
in simple terms, where does seeded corruption actually happen, what is the calibration
layer again. The answers he was given are the only place the working vocabulary was ever
explained without jargon, and they were scattered across a dozen transcripts. This file
collects them. The analogies here are the ones that were actually used at the time: the
smoke detector's test button, the fire drill, the teacher's trick, two students agreeing
on one exam.

Project terminology only. Nothing from the Collected Works is quoted here.

Written 2026-08-14.

---

### Adjudication queue

When the two blind arms disagree about which family an edge belongs to, no model breaks
the tie. The edge goes into a queue and waits for Damian to rule on it in a sitting.
A third kind of item lands there too: edges where both arms agreed but the calibrated
gate disputed their agreement, so "pending" does not always mean the arms split. Rulings
are signed and dated, and most of them force a sentence into the rulebook rather than
just settling the one item. Precedent then applies only where the reasoning matches: a
ruling once expected to clear nine queue items cleared exactly one, because the other
eight rested on different grounds.

### Amplification

One of the relation families. The edge is there because Jung adduces outside material to
widen the reading of an image, not because he asserts a relation between the two things.
It emptied. When sampled assignments were checked against eight works of Jungian
secondary literature, the reference authors read every sampled `amplified-by` edge as an
ordinary content relation, so the rule tightened: the adducing act has to be visible in
the quote, and the relation string alone never routes an edge here. All 43 `amplified-by`
edges were then re-classified blind under the new rule, and neither arm put a single one
back. The family keeps its definition and has no members, which is what a rule that got
stricter is supposed to look like.

### Analysand-source convention

When Jung reports a patient's dream, vision or picture-series commentary, the claim's
voice is `jung-quotes-source` and the source field names the analysand rather than Jung.
It exists because the failure mode that matters most in that material is putting Jung's
own interpretation into the patient's mouth. The convention is written down and dated, and
it outranks the cross-vendor auditor: an audit finding that contradicts it is overruled by
it, visibly, with a note stamped on the reference. Conventions decide vocabulary; auditors
decide facts.

### Atlas

The public site at symbolicworld.observer, and the thing all this feeds. Its data is never
hand-edited: a build script regenerates the atlas file from `seed.json`, so mining a
window, merging it and rebuilding is the whole path from a paragraph of Jung to something
a reader can click. Every link on the map carries the volume, the paragraph number and the
exact words, which is the first thing a sceptical reader tests.

### Blind arms (the two of them)

Family labels are proposed by two models that never see each other's answers. Where they
agree, the edge is assigned; where they disagree, it queues for a human. Neither arm gets
a thumb on the scale even when one of them has been right more often, because the moment
you prefer the usually-right arm, the second arm stops being a check and becomes
decoration. Two students agreeing is not the same as being right, though, which is why the
human rulings on the hard cases matter more than the agreement rate does.

### Blinding (of the miner)

The batch prompt that goes to the proposer never names a number this project tracks: no
vocabulary counts, no reuse percentages, no mention of the transfer question, no trend
files. Form constraints are allowed, because a rule about shape names no target; the quote
cap and the form rule both pass that test. Everything measured is measured after the merge,
by someone else. Without this, the miner would be tuning itself to the scoreboard instead
of reading the paragraph, and every batch-to-batch comparison would be worthless.

### Calibration loop

Plant, gate, score, diagnose, sharpen, re-run. It works like a fire drill: take a set of
real, correct family labels, secretly sabotage some of them in known ways, and see what the
gate catches while it has no sight of the answer key. Score it, read what it got wrong,
sharpen whatever rulebook sentence turned out to be fuzzy, and run the drill again. A
failed calibration is the loop working, since the failures point at exactly which boundary
needs a better sentence; the drill that never ran is the quiet lie. The whole thing takes
an afternoon, and it must re-run whenever the rulebook or the harness changes.

### Canaries

Seven deliberately broken copies of a real, verified edge, made in memory before every
test run: a quote that appears nowhere in the corpus, a paragraph number that does not
exist, a node outside the vocabulary, a reference with its provenance stripped, a claim
type outside the closed set, a collage of real words from the real paragraph glued into a
new order, and that same collage joined with ellipses. All seven must be rejected or the
run fails. It is the smoke-detector rule: you do not trust the detector because it is
quiet, you trust it because you press the test button and it screams. The canaries test
whether the validator has quietly rotted, not whether the graph is good, and the
corruption lives in a copy so the real data never sees it.

### CI handshake

The build refuses to pass if the family rulebook's version number has no matching
calibration record committed beside it. Before the handshake existed, the method page could
cite a catch rate measured against a rulebook that had since been rewritten, and nothing
noticed. Now a new version of the definitions cannot ship until the drill has been re-run
and passed against that exact version, and the number binds to the version it measured
wherever it appears. The same check enforces that the counts in the docs match `seed.json`
and that the frozen snapshot's checksum has not moved.

### Claim type

Every reference records whose voice the claim is in, from a closed set of three:
`jung-asserts` when Jung says it himself, `jung-reports-parallel` when he reports someone
else's material as a parallel, and `jung-quotes-source` when he quotes a source, which then
has to be named. It is a separate question from whether the claim is true, and it is the
axis that goes wrong most often, because attribution is easy to blur when a paragraph
moves between Jung's reading and the material he is reading. See also the
analysand-source convention.

### Clause predicate

An arrow label that swallowed a whole sentence instead of holding a verb. The relation slot
is meant to carry something like `symbolizes`; a clause predicate carries the entire
proposition, qualifiers and all. Every one of them was individually checked and true. The
shape was wrong, not the facts: you could read the graph, you could not query it. 271 edges
had it, the cause was traced to one instruction in the miner's briefing telling it to keep
qualifiers inside the relation string, and the fix was the form rule.

### Cross-vendor audit

The third stage. After the gate has passed a batch, a model from a different company reads
every surviving reference again before anything merges. It is a tiebreaker, not an
advisory: on questions of whether the paragraph supports the claim and what the words
refer to, the auditor wins. Findings that only concern claim type or confidence become
corrections rather than drops, and findings that contradict a recorded project convention
are overruled by the convention with the override stamped on the record.

### Family (relation family)

A bucket that groups relations by what kind of claim they make, so a reader can search for
identity claims or symbolization claims without knowing every verb the text happens to use.
There are 25 of them, defined in a rulebook that is versioned and pinned. Assignment
happens per edge, not per relation string, because the same verb can make different claims
in different paragraphs. Families are *assigned*, never called verified: "verified" is
reserved for the quote-and-paragraph layer, where a mechanical check can settle it.

### Form rule

The instruction that fixed the clause predicates: a relation is a verb phrase of at most
three hyphen tokens, and carrier, scope, condition and modality go in the qualifiers or the
object, never in the predicate. It is a rule about shape, so it names no tracked metric and
the miner's blinding survives it. One bullet swapped for another took a blind batch from
83.7% clause predicates to zero, and it has held at zero across every blind batch since.
The mechanical filter added alongside it has never had to fire, which is the cleanest
evidence that the instruction did the work.

### Gate

The second stage. A model from a different family than the proposer reads each claim
against its full source paragraph and rules on it, seeing the evidence and nothing of the
proposer's reasoning. It is never substituted: if capacity runs out, the batch holds at
whatever status it reached, that gets recorded honestly, and it waits. Swapping in a
convenient third model would break the one thing the published method actually claims.

### Instrumentality

A relation family covering cases where one thing is the means by which another is reached
or made possible. Its definition used to pin the means to the object slot while its own
worked examples put the means in either slot, so the sentence and the seeds disagreed about
geometry. Nothing was misfiled, but a strict reading could have routed future edges away
from the family, and CW 8 is thick with by-means-of constructions. The definition now says
the means may sit in either slot, and because editing a definition voids its numbers, the
change carried a version bump and a fresh calibration run before it could bind.

### Invisible mode

The working branch has no remote and never gets one. No push, no tag, no release, no
deploy of anything but data. It exists so that months of unfinished work can accumulate
without any of it appearing to be published, and so that publication stays a decision
somebody makes out loud rather than a side effect of a commit. Its known cost: the branch
lives on one machine, so backup has to be arranged separately, by bundle rather than by
pushing.

### Ledger

The public construction log. Every batch appears in it with what was proposed, what the
gate ruled, what the audit found and what merged, and disputes raised by readers appear
there too with their outcomes. It carries two visually distinct kinds of row, because
conflating them would misrepresent the gating: a relation drawn from the text and checked
against its paragraph is a different claim, checked by a different chain, than a family
assignment laid over an already-verified relation. It is rebuilt from the data on every
batch, so it cannot drift from what actually happened.

### One pass per window

Ground that has been mined is never mined again. It keeps the graph from silently
accumulating multiple versions of the same paragraph's claims, and it means a batch that
goes wrong is repaired by correction rather than by re-running it. Overriding it is a human
decision, named for a specific window. This is also why a schema omission in ten records
was fixed by sending those records back for their missing fields rather than by re-mining
the window.

### Proposer

The first stage. A model reads a window of paragraphs and writes candidate nodes, edges and
quotes into a file. It proposes; it never signs anything off. The handoff is a file rather
than a conversation on purpose, so the next stage sees the claim, the quote and the source
paragraph without seeing any of the reasoning that produced them.

### Receipts

Anything published has to be re-derivable by someone else. If a figure appears on the site
or in a document, the script that produced it and the inputs needed to reproduce it are
committed, and calibration runs stamp their plant seed into every artifact so a scorer can
refuse files whose stamps disagree. A scratchpad is for scratch: work that produced a merged
artifact or a published number gets committed the day it runs. The rule was adopted after
two calibration figures had to be withdrawn for want of exactly this.

### Reuse (also: transfer)

The share of an incoming batch's relation labels that already existed in the graph, as
against freshly minted ones. It is the instrument behind the open question of whether an
open vocabulary keeps sprawling as more material lands or settles down. For a while the
answer looked like sprawl, until it turned out that one defective batch's ninety new
strings were carrying the whole trend; take that process artifact out and vocabulary grows
more slowly than the graph does. The measurement is why the miner is blinded, since a miner
told to reuse labels would supply the answer instead of the evidence.

### Seeded corruption

Making a broken copy, seeing whether the checker notices, and never touching the real
thing. It is the teacher's trick: slip some answers you already know are wrong into the
pile and count how many the grader catches, because a grader that has silently stopped
paying attention looks exactly like a good one from the outside. It happens in two places
here. The canaries do it to the mechanical quote validator on every single test run. The
family calibration does it to the family gate, planting four kinds of error, and the two
answer different questions: does the code still work, versus is this judge any good. In
both cases the one who plants the errors is never the one who grades them, and no planted
error has ever touched published data.

### Stale answer key, and the re-audit

The first two family calibrations were run by hand, scored loosely, and their keys were not
kept. The catch rates they produced were then quoted on the site in the present tense while
the rulebook they had measured was being rewritten underneath them. When this was noticed
the figures came off the site rather than staying up with a footnote, because the honest
description was not "it works" but "nothing suggests it is broken, and the evidence is
weaker than we said." No mass re-run followed, for a structural reason rather than a thrifty
one: the published labels never rested on that gate, they rest on two independent models
agreeing, which is its own evidence and is receipted per edge. What was withdrawn was a
claim about the checker, not confidence in the checked.

### Three layers: assignment, gate, calibration

These get conflated constantly, so keep them apart. *Assignment* is two blind arms deciding
which family an edge belongs to, with a human ruling on disagreement. *The gate* is a
separate model checking assignments and saying right or wrong. *Calibration* is the drill
that measures whether the gate itself is any good, by planting errors it cannot see the key
to. Each layer checks the one before it, and the last one is the only one that can tell you
whether the middle one has gone to sleep.

### Thresholds set before results

The pass mark is written down while no result exists. The alternative is human nature: run
the test, see seventeen out of twenty, and start explaining why seventeen is actually fine.
The rule has been applied to the normalization sample's rescue bar and to the family
calibration's near-miss bar, and once a sample is drawn its threshold does not move. Which
class the bar binds to is part of the same decision: near-misses count, since they are the
mistakes the rulebook exists to prevent, while false alarms get reported without deciding
anything, because last time several of them turned out to be real errors nobody had
spotted.

### v1.3 snapshot (frozen)

The published release, 248 nodes / 669 edges / 699 references, and the copy of the site
that describes it. It is supposed to say old numbers. The facts checker deliberately
measures the paper and its snapshot against the release tag while measuring the living
documents against today's graph, because those documents describe two different things.
Its checksum is asserted on every build, and nothing is ever written into it.

### Verification chain

Three models in fixed roles: one proposes a claim with its verbatim quote, one from a
different model family gates it against the source paragraph, and one from a different
vendor audits the batch before anything merges. The roles never swap, and the reason is the
whole point rather than a preference: a model that has already written its own
justification cannot then be the one that judges it. It applies to the people running it
too. Whoever writes the family definitions does not classify edges against them, and
whoever plants a corruption does not grade the catch.

### Window

A block of paragraphs, roughly seventy, that is mined as one batch and moves through the
chain as one unit. Volumes are cut into windows so that a failure costs one window rather
than a volume, so cost is predictable per batch, and so a batch can hold at whatever stage
it reached when something upstream is unavailable. A window's whole life is one row in the
ledger.
