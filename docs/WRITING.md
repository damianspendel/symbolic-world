# Writing for readers — the house register

Damian's rule (2026-09-02): it is an academic paper, and it does not write
to exclude people. Everything below serves that. `tools/check_ai_tells.py`
enforces the mechanical part on every pass; the rest is judgement, and the
sources say why.

## Three ideas the sources agree on

**The curse of knowledge** (Pinker, *The Sense of Style*). The main cause of
bad expert prose is not laziness but the writer's inability to imagine not
knowing what they know. Symptoms: a term used before the thing it names has
been shown; a step of reasoning skipped because it is obvious to the author;
abbreviations and project names dropped in as if shared. Remedy: instance
before rule; name a thing only after the reader has seen it; test a draft on
a reader who was not in the room. In this project that reader is a scheduled
blind cross-vendor pass, and the checker flags undefined abbreviations.

**Classic style** (Thomas and Turner, via Pinker). Write as if pointing at
something the reader can see: the object of study, not the activity of
studying it. Prefer things and actions to *metaconcepts* (framework,
approach, aspect, dimension, notion, perspective, level, process) and to
what Sword calls **zombie nouns**: nominalizations that swallow the verb
("the implementation of a verification of the claim" for "we verified the
claim"). The checker counts nominalization density and metaconcept density
and reports them; a rising count is the signal to rewrite.

**Uniformity is the tell.** The strongest machine signals are structural,
not lexical (StationX 2026; a 2026 Oxford stylometry study found
ChatGPT essays cluster tightly on function-word use while human essays
disperse). Same-length sentences, every paragraph the same shape, every
thread tied off, the moral stated aloud, definitions packed before any
instance. Vocabulary lists (Wikipedia's *Signs of AI writing*) catch the
easy layer; the checker reports sentence-length spread, paragraph-length
spread and sentence-opener variety because those are the harder layer.

## The register, in rules

1. Instance before rule. Show the thing, then name it.
2. One defined term per sentence where you can manage it; never three.
3. Verbs over nominalizations; "we verified" over "verification was performed".
4. Plain word first, term of art second, in the same sentence, once.
5. No abbreviation without its expansion at first use (CW, RQ, E-numbers
   included; the checker allows only those the text has defined).
6. Vary sentence length on purpose. A one-clause sentence after a long one
   is not a stylistic tic; it is how a reader breathes.
7. State what was measured before any number, and the number once.
8. Cut the flourish that restates the thesis. Retire aphorisms rather than
   repeat them.
9. No em-dashes to splice clauses; commas, colons, full stops.
10. A plain-language summary sits under the abstract: four short paragraphs
    (what the problem is, what was done, what was found, what it means),
    written for a reader outside the field (Springer/Sage/T&F PLS practice).

## What the checker does with this

Hard (fails the run): AI vocabulary, copula avoidance, sentence-opening
connectives, negative parallelism, -ing tail clauses, significance
inflation, vague attribution, bold density, title-case headings, emoji
markers, and undefined abbreviations.

Soft (reported, never gating): em-dashes, "rather than", from-X-to-Y ranges,
tricolons, colon-led reveals, curly quotes, sentence-length mean and spread,
paragraph-length spread, sentence-opener variety, nominalization density,
metaconcept density, passive-voice share, hedge stacks, Flesch reading ease,
and the moral-stated-aloud count. The soft numbers are for the eye: the
sources give no thresholds worth pretending to, so the checker prints them
beside the previous pass's numbers when it can, and the direction is the
verdict.

## Sources

- Wikipedia, *Signs of AI writing* (vocabulary, structure, formatting).
- StationX, *AI Writing Patterns* (2026): structural tells discriminate,
  vocabulary is easily gamed.
- Steven Pinker, *The Sense of Style* (2014); Harvard Gazette, "Exorcising
  the curse of knowledge" (2012).
- Helen Sword, "Zombie Nouns", *New York Times* (2012); *Stylish Academic
  Writing* (2012).
- Tricontinental, "A systematic method for controlling AI writing style"
  (2026): the seven-layer stylistics profile.
- Digital Scholarship in the Humanities (2026): function-word stylometry,
  4,346 essays, AI texts' "striking stylistic uniformity".
- Springer Nature, Sage, Taylor & Francis: plain-language-summary guidance.
