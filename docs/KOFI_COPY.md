# Ko-fi page copy — draft for Damian's review (2026-10-21)

Draft for the Ko-fi account's About section, written to docs/WRITING.md's
register. Cost figures are the committed measured rates
(docs/PROPOSAL_NEXT_ARC.md: $0.09–0.16 per verified citation, $10–11 per
window; docs/REVIEW.md carries the same line). Counts are dated because this
copy lives off-site and the graph grows nightly; the alternative line below
avoids counts entirely. Scope per the 2026-10-21 decision: donations only —
no shop, no membership tiers, no tracking.

---

## Page name

The Symbolic World

## One-line tagline

A verified atlas of Jung's Collected Works — every claim cited, quoted and
machine-checked.

## About (main text)

The Symbolic World is a free, open atlas of C. G. Jung's *Collected Works*:
as of October 2026, 653 concepts joined by 2,420 claims, each one resting on
a quoted citation that was checked against the source paragraph before it
was allowed in.

The checking is the point. One AI model proposes each claim from the text. A
second model, from a different family, judges the claim against the
paragraph it cites. An auditor from a different vendor re-reads each new
batch, and a human rules on disagreements and decides what is published. The
full ledger of what passed, what was corrected and what was disputed is
public.

Mining the remaining volumes is metered work. At measured rates a fully
verified citation costs $0.09 to $0.16 in model spend, and one mining window
— about seventy paragraphs taken end to end through all the checks — costs
about $10. A tip of any size goes toward the next window. Larger support
brings whole volumes within reach.

Everything ships free either way: the atlas, the dataset (CC BY 4.0), the
method paper and the verification ledger stay public at
symbolicworld.observer. Tips change how fast the remaining volumes are
mined, nothing else.

## Alternative opening (no counts, never goes stale)

The Symbolic World is a free, open atlas of C. G. Jung's *Collected Works*:
hundreds of concepts joined by thousands of claims, each one resting on a
quoted citation that was checked against the source paragraph before it was
allowed in.

## Thank-you message (shown to a supporter after a tip)

Thank you — this goes straight into the mining. Tips fund the next window of
the *Collected Works*: about seventy paragraphs read, claimed, checked
against the text word for word, audited, and published with every receipt. A
verified citation costs 9 to 16 cents in model spend, so one coffee pays for
roughly twenty of them. Everything you help mine stays free for everyone at
symbolicworld.observer.

(The cents line restates the committed $0.09–0.16 rate; "roughly twenty" is
the conservative end of a $3 tip at that rate.)

## About you (the creator section)

I build The Symbolic World: an atlas of C. G. Jung's *Collected Works* in
which every claim carries its citation, its quote and the record of who
checked it. Models do the reading at scale; I rule on their disagreements,
decide what gets published, and answer for it. The method is published, the
dataset is open, and the ledger records the corrections as plainly as the
claims. Tips pay for model time, nothing else.

(Deliberately nothing biographical; add a personal line if you want one.)

## Notes for the account setup (Damian's steps, not the build track's)

- Ko-fi account + PayPal link (personal PayPal suffices per Ko-fi's FAQ;
  0% platform fee on donations).
- Once the page URL exists, set SUPPORT_URL in web/build-atlas.mjs and the
  site's support link goes live at the next reviewed deploy.
- The em-dash in the About cost sentence is one deliberate pair, not a
  splice; drop it if it reads wrong.
