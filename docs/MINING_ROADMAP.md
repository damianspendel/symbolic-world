# Mining roadmap — what comes after the alchemical trilogy

Draft for review, 2026-08-01, written on the mining-away branch. Nothing here
is agreed and nothing is scheduled. Mining resumes when Fable 5 capacity
returns.

## Where the corpus stands

Nine volumes are extracted to `data/paragraphs.jsonl`, 6,241 paragraphs. The
alchemical trilogy took 87% of the mining and represents 30% of the text.

| Vol | Paragraphs | Refs | Coverage | Title |
|---|---:|---:|---:|---|
| 5 | 682 | 23 | 3.4% | Symbols of Transformation |
| 8 | 997 | 19 | 1.9% | Structure and Dynamics of the Psyche |
| 9i | 715 | 24 | 3.4% | The Archetypes and the Collective Unconscious |
| 9ii | 429 | 21 | 4.9% | Aion |
| 11 | 1016 | 21 | 2.1% | Psychology and Religion: West and East |
| 12 | 565 | 223 | 39.5% | Psychology and Alchemy |
| 13 | 482 | 176 | 36.5% | Alchemical Studies |
| 14 | 791 | 413 | 52.2% | Mysterium Coniunctionis |
| 16 | 564 | 19 | 3.4% | The Practice of Psychotherapy |

The 2 to 5% figures outside the trilogy are not passes. They are amplification
targets picked up incidentally while reading alchemy, which means they are
biased toward whatever in those volumes looks alchemical. That bias matters
later: it is why the existing CW 9ii material cannot settle the relation-family
transfer question on its own.

Unmined outside the trilogy: 4,403 paragraphs.

## Cost basis

Measured, not estimated. Twelve batches carry cost telemetry: mean $2.99 per
batch, $0.116 to $0.163 per citation. The trilogy ran 40 batches over 1,838
paragraphs, so roughly 46 paragraphs per batch and about $120 for the arc.

Applying that rate, with the caveat that yield falls on less symbol-dense
material and CW 8 and 11 are considerably less symbol-dense than Mysterium:

| Arc | Paragraphs | Batches | Cost |
|---|---:|---:|---:|
| CW 9ii alone | 429 | ~9 | ~$28 |
| CW 5 alone | 682 | ~15 | ~$45 |
| CW 16 alone | 564 | ~12 | ~$36 |
| CW 9i + 9ii | 1,144 | ~25 | ~$75 |
| CW 11 | 1,016 | ~22 | ~$66 |
| CW 8 | 997 | ~22 | ~$66 |
| Everything remaining | 4,403 | ~96 | ~$290 |

## Two ways to scope an arc

**Volume-bounded.** A volume ends. You can say the arc is complete and mean it,
which is what made the trilogy's relation-family scope decision tractable.

**Thematic.** A thread followed across volumes. More interesting to read, but it
never closes: there is always another paragraph elsewhere that belongs. An
arc that cannot be declared complete cannot anchor a vocabulary or a release.

The trilogy was both at once. That is unusual and should not be assumed
available again.

## Candidate arcs

### A. The archetypal core — CW 9i + 9ii

The theory volume and its historical application. 1,144 paragraphs, ~$75.

The psychological vocabulary already dense in the graph is almost entirely
ungrounded in its own text: the-self appears in 79 references at 97% in Jung's
own voice, the-unconscious in 66 at 100%, individuation in 25 at 100%. All of
that currently rests on alchemical paragraphs. This arc would give those terms
their home ground and let the graph state the theory as well as its
application.

Coherent as a unit, closable, and already scheduled as v1.7 on the release
roadmap. It also settles the relation-family transfer question with real data
rather than the biased 42-edge sample.

Against it: Aion is alchemically adjacent, so this is the least surprising
direction and tests the pipeline least.

### B. The origin — CW 5

Symbols of Transformation, 682 paragraphs, ~$45.

1912, revised 1952. Comparative mythology on the Miller fantasies. Libido,
the hero, sacrifice, the mother, rebirth. Written before the archetype theory
existed and before Jung had read the alchemists.

This is the strongest test of whether the pipeline handles Jung when he is not
doing philology. E8 tested generalisation outside Jung using James; this tests
it inside Jung, where the failure mode is subtler because the vocabulary
overlaps while the method does not.

Against it: it connects weakly to the existing graph, so it grows the artifact
sideways rather than deepening it.

### C. The clinical bridge — CW 16

564 paragraphs, ~$36. Smaller than it looks in significance.

The Practice of Psychotherapy contains the Psychology of the Transference,
which is Jung's alchemical reading of the Rosarium Philosophorum. That essay
is continuous with the trilogy: it is coniunctio applied to the consulting
room. CW 16 already shows the second-highest reportage rate of any volume in
the graph, 32% reports-parallel, on only 19 references.

This is the arc with the clearest audience. An ISAP room cares about the
transference in a way it does not care about relation canonicalisation.

Against it: only part of the volume is relevant, so the arc is really a
chapter, and chapter-bounded scope is weaker than volume-bounded.

### D. The religious function — CW 11

1,016 paragraphs, ~$66.

The Trinity, the Mass, Job, and the Eastern material: the Tibetan Book of the
Dead, yoga, Zen. Genuinely different territory, and it engages the node that is
already the most interesting thing in the graph. Christ carries 55 references
at almost exactly even voice, which is the closest the corpus comes to a term
Jung neither owns nor disowns.

The Eastern portion also tests something no other arc does: whether the method
handles a tradition Jung approaches without the philological apparatus he
brings to alchemy.

Against it: large, and the volume is two books stapled together, so "complete"
is doing less work than it appears.

### E. The structural volume — CW 8

997 paragraphs, ~$66. Listed for completeness and not recommended.

Psychic energy, the transcendent function, synchronicity. The most technical
Jung and the least symbol-dense. A symbol graph is the wrong instrument for it,
and the yield estimate above is probably optimistic by a wide margin.

## Thematic threads, for later

These cut across volumes and cannot close, so none should be a release scope.
They are better as queries over an already-mined corpus than as mining targets.

- **Christ and Anthropos** across 12, 13, 14, 9ii, 11. The graph already shows
  this is where Jung's voice is most evenly balanced.
- **The feminine** — anima, Luna, Sophia, the mother — across 5, 9i, 14, 16.
- **Coniunctio and transference** across 14 and 16.
- **The Eastern material** in 11, as a contrast case to Western alchemy.

Each becomes available once the volumes underneath it are mined. Treating them
as mining scopes instead would produce an arc nobody can declare finished.

## What an arc costs beyond money

Every arc reopens three things that the trilogy closed.

**Relation-family scope.** The family vocabulary is scoped to CW 12/13/14.
New volumes carry `pending-scope` until families are extended under governance.
Mining before the family layer ships means a growing pool of unfamilied edges;
mining after means the transfer study has real data. This argues for doing the
family layer first, or for accepting that the next arc runs unfamilied.

**The artifact's identity.** The current object is an atlas of Jung's
alchemical thought: coherent, bounded, and described that way in the paper.
Two arcs make it an atlas of Jung, which never closes and is harder to defend
as complete.

**Verification load.** Every arc needs the same gate, cross-vendor sample, and
human validation tranche. Fable capacity, not money, is the binding constraint.

## Recommendation

Pick one arc and state what it is for. The choice follows from that.

To answer a question about the method, take CW 5. It is the only arc where a
negative result would be informative.

To build a second closable artifact, take CW 9i + 9ii. It grounds the half of
the existing graph that currently floats, and it settles the transfer question
as a side effect.

To reach an audience, take CW 16 and accept chapter-bounded scope.

Do not take everything. It is roughly $290, it costs the property that makes
the current artifact defensible, and it has no stopping point.

My own preference, stated as a preference rather than a finding: 9i + 9ii,
because the psychological vocabulary in the graph is currently asserted on
alchemical evidence alone, and that is the weakest joint in the artifact.

## Open decisions

1. Which arc, and what it is for.
2. Whether the relation-family layer ships before or after the next arc.
3. Whether a new arc gets its own branch off the merged master, or reuses
   mining-away.
4. Whether the graph keeps its alchemical framing or is renamed to reflect a
   wider scope, which is a decision about the paper as much as the atlas.
