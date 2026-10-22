# Humanizer report: symbolicworld.observer, all text

Read on 2026-10-22 from the JungKG working tree: the site sources under web, the method copy and the poster source. I edited nothing. The project's own tell checker is written for the paper and I did not run it on the site copy.

## What was read

| Source | Words | Kind of text |
|---|---|---|
| index.html (hero, meta) | 127 | editorial |
| method (docs/METHOD_COPY.md, Damian's 2026-10-18 rewrite) | 1305 | editorial |
| in a nutshell page plus the poster image text | 540 | editorial |
| design (ontology.html) | 2603 | editorial plus scan tables |
| families index and the 25 family pages (one template) | 1058 | editorial plus quoted ruleset |
| releases | 595 | changelog |
| ledger, disputes, routes, query, concepts, support, james | 2960 | UI copy and records |
| concept pages (589, one template) and batch pages (74, one template) | 1950 | records plus mining logs |
| SPA strings in main.js (tooltips, legends, report templates) | about 300 | UI copy |
| family definitions quoted into the site (families.json) | 4279 | ruleset, quoted verbatim |

## Verdict

The site reads as careful and specific. Sentence-level vocabulary is almost clean. The tells are structural and they are visible to a reader who opens three pages in a row, which is how a site gets read. Four patterns account for most of the hits, and the first of them is the one a skeptical reader will notice.

## Site-wide patterns, strongest first

1. The same sentence closes page after page. "A map of assertions, not a reading" appears on the method page, twice on the design page, and as the final line of all 25 family pages. "Assigned to an edge in its paragraph, never to a string in the abstract" appears on the families index, every family page, the SPA lede, and seven times verbatim in the design page's pitfall table. "The model that proposes a claim is never the model that signs it off" is the home-page hero, the bolded sentence on the method page, and a variant on the poster, where "Nothing on this line marks its own homework" repeats it a fourth way. "Agreement is not endorsement: no scholar reviewed this vocabulary" is on the design page and on every family page. Your own house rule is retire aphorisms rather than repeat them. Say each once, on the page that owns it, and link to it elsewhere.

2. The site states its limits as "X, not Y" by default. The design page has 18 contrast forms in 2600 words, each family page 5, the method page 4. Some earn their place: the negative half corrects a belief a reader holds ("'Verified' means the quote is really in the book, not that Jung was right"). Most only add weight: "not a structure discovered in his thought and not a position the field has agreed on, again, it is not a reading" stacks three negatives on one claim. State the positive claim and keep one contrast per page where it corrects something.

3. Em dashes splice clauses on nine pages. Counts in body prose: poster 9, design 8, family pages 5, method 4, james 4, support 3, index meta 2, routes 2, disputes 2. The paper's house rule 9 bans this. Commas, colons and full stops do the job in every case I checked.

4. Colon-led reveals and counted openers. "The result:", "Two limits." (followed by three), "Five stations.", "The rule underneath all five:", "The tail is the informative part:". The design page has 8, the method page 7, the releases page 8. One or two per page is a voice. Eight is a rhythm applied by rule.

Lesser patterns: a bolded whole sentence on the method page. Caps for emphasis in the SPA lede ("what KIND of relation") and throughout the quoted definitions (OBJECT, SUBJECT, ONE, BY WHOEVER, LAST, NOT). One-line closers that restate the paragraph: "This is a standing arrangement." and "Nothing here publishes itself." on the method page, "endorsed by nobody" on every family page. Vocabulary: "key design decisions" (design), "key updates" (releases), "articulates our view" (design), "logged for transparency" (dispute 17).

## Page by page

### Home (index.html)

Meta description: "Every symbolic relation — the stone, the self, the anima, the prima materia — cites its exact volume and paragraph". Two dashes around a list. Suggest: "Every symbolic relation, from the stone to the anima, cites its exact volume and paragraph with Jung's verbatim words."

Hero line is the mantra. Keep it here, since this is the page that owns it. Drop the bold copy of it on the method page and the poster's two restatements.

### Method

This is Damian's rewrite and it is the cleanest long page. Remaining hits:

- "It is hostile — i.e. it seeks to challenge aggressively — by default". Dash pair plus "i.e." (twice in this list). Suggest: "By default it is hostile: the claim survives only if the model judges that the paragraph supports it."
- "The rule underneath all five: **the model that proposes a claim is never the model that signs it off.** ... This is a standing arrangement." Colon reveal, bold sentence, one-line closer. Suggest: "Under all five stations, the model that proposes a claim never signs it off. Proposer and gate are different model families (Anthropic's Opus and Fable lines) and the auditor is a different vendor (Google's Gemini)." Cut "This is a standing arrangement."
- "No model is allowed to break a tie; this is performed by a human in the loop: a person rules, in sittings." Says the same thing three ways. Suggest: "No model breaks a tie. A person rules, in sittings, and the rulings land in the ledger."
- "Nothing here publishes itself." Closer that restates "Releases, deploys and rulings are human decisions." Cut.
- "The verification set seeds seven deliberately corrupted claims — so far, all seven have been caught on every run." Dash. Suggest a full stop.
- "This is a map of assertions, not a Jungian reading." Fine here, once. It recurs in the known-limits table on the same page ("The graph is a map of assertions, not a reading"). Keep one.
- The two bulleted lists with bold labels ("Search", "Click", "Gold set", "Adjudication") are acceptable: the labels are UI names and record names, so they carry information.

### In a nutshell and the poster

- "the steps that identify, validate and evidence the citation". Forced triad with "evidence" as a verb, and "citation" twice in the sentence. Suggest: "one citation followed from the map through the checks it passed."
- Poster: "Every line on it is a claim — this concept relates to that one — resting on an exact quote". Dash pair. Suggest parentheses or a colon.
- Poster: "The atlas opens on the lapis — the philosophers' stone — so we start there too." Suggest: "The atlas opens on the lapis, the philosophers' stone, so we start there too."
- Poster: "Nothing on this line marks its own homework." Saying dressed as depth, and the fourth restatement of the mantra. Cut. The station text above it already says who rules.
- Poster: the quote-marked "Verified" sentence is a contrast that earns its place. Keep, replace the dash with a comma.
- Noticed in passing, not a prose point: the poster says 653 concepts, 2,420 claims and 3,180 quotes "as of 21 October 2026" while every other page shows 661, 2463 and 3248 as of 22 October. The handoff note says the poster's numbers are pixels. One re-render would align them.

### Design (ontology.html)

The page with the most hits.

- "This page records key design decisions". "Key" is on the vocabulary list. Suggest: "This page records the design decisions and the results of a standard pitfall scan."
- "A challenge identified is that we have many different relations. To better enable grouping of relations, we have designed two tiers." Nominalized, passive, and "enable". Suggest: "Jung's relations come in many wordings, so the graph has two tiers."
- "not a structure discovered in his thought and not a position the field has agreed on — again, it is not a reading." Triple negative plus dash plus "again". Suggest: "The families are this project's sorting of the relations Jung wrote. The field has not agreed on them and the graph does not claim they are his structure."
- "The whole graph maps what Jung asserted rather than interpreting it, and the second tier is where that limit matters most." Contrast plus "matters most". Suggest: "The second tier is where the map's limit shows: it sorts what Jung asserted and does not interpret it."
- "The below table articulates our view of the findings of the pitfall scanner." Writing about the document, and "articulates". Suggest: "Our stance on each finding follows."
- Pitfall table: seven rows carry the same stance, verbatim: "Equivalence is stated by the family layer, per edge in its paragraph rather than per string in the abstract; where the definitions document rules on a specific pair, a declaration records it and the query layer applies it at read time". Write it once above the table and let the rows say "answered by the declarations layer (see above)". The rendered table would also lose 600 words.
- "This is an associative network with a type tag, not a subsumption ontology, and the paper describes it as one. There is no hierarchy to inherit through because none was claimed." The scan finding one cell to the left already says "this is an associative network with a 6-way type tag, not a subsumption ontology". The stance repeats the finding and adds a closer. Suggest: "By design. The paper describes the graph as an associative network with a type tag."
- "The result: the literature treats 16 of the 22 sampled assignments". Colon reveal. Suggest: "The literature treats 16 of the 22 sampled assignments".
- "Two limits. Agreement here is not endorsement: ..." announces two and gives three, and the first duplicates every family page. Suggest dropping the count and keeping the three sentences.

### Families index and the 25 family pages

- "A family is assigned to an edge in its paragraph, never to a string in the abstract." Appears on the index, on every family page, and in the SPA lede. Keep it on the index and cut the others.
- Family page: "The disagreements stand beside the agreements because hiding them would make the table an argument rather than a record." Aphorism with a "rather than" tail. Suggest: "The table lists disagreements beside agreements."
- Family page: "Agreement is not endorsement: no scholar reviewed this vocabulary, and the sample is small enough to name in a sentence." Duplicate of the design page. Keep it on the design page, link from here.
- Family page closer, on all 25 pages: "These families are this project's classification. They are calibrated inside this repository, checked once against outside scholarship on a small sample, and endorsed by nobody. What the layer records is how we sorted relations Jung wrote: a map of assertions, not a reading of him." Triad, dramatic tail, catchphrase. The page's opening paragraph already says what a family is and is not. Cut the closer, or reduce it to "Checked once against outside scholarship on a small sample. No scholar has reviewed the vocabulary."
- SPA lede: "quoted from docs/FAMILY_DEFINITIONS.md — never paraphrased. A family classifies what KIND of relation an edge asserts, per edge and in its paragraph context, never per relation string." Dash, caps, and the catchphrase. Suggest: "quoted from docs/FAMILY_DEFINITIONS.md without paraphrase. A family names the kind of relation an edge asserts."
- The quoted definitions (families.json, 4279 words) carry 61 dashes, caps emphasis in most entries, and "not X (...); not Y (...); not Z (...)" boundary triads. The site states that it quotes the document and never paraphrases it, so any fix belongs in docs/FAMILY_DEFINITIONS.md, and a changed ruleset voids its numbers by rule. I would leave the definitions alone and treat them as a ruleset, which readers expect to look like one.

### Releases

- "A list of changes and key updates." Says the page is a list, and "key". Suggest: "What each release changed."
- "The v1.4 and v1.5 plans are folded in (Damian, 2026-08-19)." A working-log attribution on a public page. Cut the parenthesis.
- The release bodies are clean: verb-first, concrete, dated.

### Support, routes, james, disputes

- Support: "A mining window — about seventy paragraphs taken end to end through all the checks — costs about $10." Suggest parentheses. "Mining the remaining volumes is metered work, at measured rates a fully verified citation costs..." is a comma splice. It reads human, but a full stop after "work" helps.
- Routes meta: "shortest first, every leg quoted —" two dashes. Suggest commas.
- James: three dashes in 76 words. "Corpus public domain — the full reproduction package ships with the repository." Suggest a full stop.
- Disputes: the page copy is clean. Entry 17's "logged for transparency" is a virtue tag. Suggest "No change."

### Ledger, query, concepts, concept pages

Clean. The record vocabulary is terse and specific. One mild point: every one of the 2463 ledger cards prints "Classification only; the relation above was already gated against its paragraph". A legend line at the top would do the same job once.

### Batch pages (74)

The "What it merged" block is the mining log, published raw: ALL-CAPS headlines ("THE CW 8 ARC CLOSER", "THE CW 8 MINING ARC IS COMPLETE"), process narration ("The window note (generic boilerplate, wrong for a fifth straight window) did not match the actual paragraphs; the miner correctly followed the text"), and 12 dashes on the sampled page. These are not model tells in the humanizer sense. They are internal notes in a public place. Whether they stay as-is is a register decision, not a rewrite.

## What I did not do

I changed no file. The project's CLAUDE.md puts the site build on a separate track with its own deploy gates, and the method copy is your own rewrite from four days ago. Each suggestion above is one edit, so you can take them page by page.
