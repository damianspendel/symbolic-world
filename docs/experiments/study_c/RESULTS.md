# Study C — results

Run 2026-08-30. Design: `DESIGN.md`, pre-registered 2026-08-28,
unchanged since. One run, no redraws. No arm is ground truth in C1;
disagreement is the finding.

## C1 — the second normalization arm

- items compared: **260**
- mechanical verb agreement: **0.5269** (120 exact, 17 inflection)
- remainder judged same-relation: 80, different: 43, unjudged: 0
- same-relation rate overall: **0.8346**

Qualifier presence, by kind (count of items where the arm filled the key):

| kind | arm 1 (stored) | arm 2 (Gemini) |
|---|---|---|
| carrier | 79 | 68 |
| scope | 190 | 67 |
| condition | 48 | 53 |
| modality | 196 | 76 |
| note | 218 | 169 |

Dropped-material coverage (token-overlap proxy, not a judgment): arm 1 0.8291 over 247 items, arm 2 0.8584 over 254.

### Every same-relation disagreement (43)

| # | verbatim relation | arm 1 | arm 2 | reason |
|---|---|---|---|---|
| 1 | `attributed-to-matter-what-belonged-to` | `misattributes-contents-of` | `projected-contents-of` | arm_a restricts scope to classical alchemy and hedges awareness in modality; arm_b has neither and its verb 'projected' imports a theoretical term the quote does not use |
| 4 | `must-accomplish-in-himself-process-attributed-to` | `must-replicate-process-of` | `must-mirror` | arm_a attributes the demand to Dorn/Liber Quartorum as reported parallel and adds the condition 'things are perfected by their like'; arm_b asserts a bare 'must' |
| 6 | `stands-at-beginning-and-end-of` | `stands-at-beginning-of` | `begins-and-ends` | arm_a keeps only the beginning position and splits off the end; arm_b's verb covers both beginning and end |
| 7 | `inwardly-means-spirit-imprisoned-in` | `signifies-spirit-imprisoned-in` | `represents-spirit-in` | arm_a's verb keeps 'imprisoned' and hedges as Jung's account of alchemists' meaning; arm_b's verb drops imprisonment and carries no attribution hedge |
| 15 | `must-be-made-conscious-to-open-gateway-to` | `bars-gateway-to` | `opens-gateway-to` | arm_a states the blocking (bars gateway unless made conscious); arm_b states the opening (opens gateway if dealt with first) — opposite polarity |
| 20 | `is-the-fourth-person-in-the-heavenly-drama-of` | `is-fourth-person-beside` | `is-fourth-person-of` | arm_a says 'beside' and explicitly excludes the devil from the Trinity; arm_b says 'of', making him a person of the Trinity |
| 25 | `has-constantly-been-held-up-to-western-man-in-the-model-of-the-life-of` | `is-presented-through` | `is-modelled-on` | arm_a keeps the presentational sense 'held up to Western man'; arm_b's 'is-modelled-on' claims individuation is itself modelled on Christ's life |
| 32 | `means-the-height-and-depth-of` | `means-height-of` | `represents` | arm_a drops 'depth' from the verb and splits it; arm_b keeps height and depth together |
| 33 | `is-an-archetype-inherent-in` | `is-archetype-inherent-in` | `is-inherent-in` | arm_a hedges the claim as the more probable hypothesis and scopes it to the dream-series; arm_b asserts it flatly |
| 51 | `is-the-abyss-of-impassioned-dissolution-in-the-animal-divinity-of-the-primordial` | `dissolves-distinctions-into` | `is-dissolution-within` | arm_a makes Dionysos dissolve distinctions into the psyche (agentive); arm_b makes Dionysos be dissolution within the psyche (identity) |
| 53 | `is-truly-always-an-inner-image-built-up-through` | `is-built-up-through` | `is-built-through` | arm_a marks the claim as the rimpoche's reported speech, adds the disturbed-equilibrium condition and restricts to the true mandala; arm_b has none |
| 55 | `signifies-a-psychic-centre-of-the-personality-not-to-be-identified-with` | `signifies-centre-distinct-from` | `is-not-identified-with` | arm_a's core says the signified centre is distinct from the ego with 'unless everything deceives us' hedge; arm_b's core says the mandala itself is not identified with the ego, unhedged |
| 62 | `cannot-come-into-being-unless-mans-causal-link-with-the-world-of-instinct-is-rediscovered` | `requires-rediscovered-link-with` | `None` | arm_b is empty (null relation); nothing to match arm_a's requires-rediscovered-link-with |
| 72 | `leads-to-destructive-mass-psychoses-of` | `leads-to-psychoses-of` | `causes-psychosis-in` | arm_a adds the condition (denial of autonomous systems, attribution to an outside will) and the full scope; arm_b has no condition |
| 76 | `lies-at-the-point-between-consciousness-and` | `lies-at-border-of` | `lies-between-consciousness-and` | arm_a adds the condition that the unconscious be recognized as co-determining; arm_b has only the hypothetical modality |
| 78 | `once-recognized-appears-as-something-objective-in-which-is-included` | `appears-to-include` | `includes` | arm_a hedges to appearance ('appears-to-include', not ontology); arm_b's verb asserts inclusion outright |
| 80 | `makes-the-alchemists-perceive-their-own-unconscious-contents-as-qualities-of` | `attributes-contents-to` | `projects-contents-onto` | arm_a predicates the perceptual attribution with the 'as though' hedge in modality; arm_b predicates the act of projecting with no hedge, the seeming demoted to a note |
| 92 | `represents-a-transcendent-totality-which-coincides-with` | `represents` | `coincides-with` | a says lapis represents (the totality that coincides with) the self; b says lapis coincides with the self, promoting the mediated coincidence to direct identity |
| 100 | `is-undoubtedly-paracelsuss-name-for` | `is` | `is-name-for` | b's 'is-name-for' scoped 'for Paracelsus' credits Paracelsus with the Archeus=Anthropos equation; a marks the equation as Jung's and keeps only the naming with Paracelsus |
| 102 | `accompanies-his-chemical-work-with-a-simultaneous-mental-operation-performed-by-means-of` | `performs-mental-operation-by` | `accompanies-chemical-work-with` | a adds a Paracelsist-tradition scope absent from b, and b's verb makes imaginatio the accompanying operation rather than the means by which it is performed |
| 118 | `is-the-natural-spirit-whose-strange-and-significant-workings-we-can-observe-in-the-manifestations-of` | `is-observable-in` | `manifests-in` | a says its workings are observable in the unconscious; b's 'manifests-in' claims the lumen naturae itself manifests there, more than the text's observation claim |
| 119 | `is-a-largely-autonomous-psychic-system-for-compensating-the-biases-and-aberrations-of-the-conscious-attitude-namely-of` | `compensates-biases-of` | `compensates` | a adds the 'for the most part functionally, sometimes by force' hedge in modality; b leaves compensation unhedged |
| 120 | `replaces-less-by-word-than-by-deed-the-sacraments-of-the-church-that-are-the-only-way-to-immortality-in` | `replaces-sacraments-of` | `replaces-sacraments-in` | a restricts the replacement to the Vita longa procedure ('here') and adds 'without conflict with the orthodox standpoint'; b has neither restriction |
| 123 | `is-interpreted-by-the-fairytale-as-a-pagan-god-forced-to-descend-into-the-dark-underworld-and-be-morally-disqualified-under-the-influence-of` | `is-morally-disqualified-by` | `is-forced-by` | a's predicate is the moral disqualification with the descent split off; b's predicate is the forcing (descent), a different conjunct chosen as the relation |
| 141 | `came-to-stand-in-a-tension-of-opposites-such-as-had-never-occurred-before-with` | `came-into-tension-with` | `is-in-tension-with` | a adds a condition (result of what is taught about Christ, not his teaching) absent from b, and states an event ('came into') where b states a standing state ('is in') |
| 148 | `is-the-motivating-force-and-the-goal-of` | `is-motivating-force-of` | `is-goal-of` | a predicates 'motivating force' and splits 'goal'; b predicates 'goal' and demotes 'force' to a note; different conjunct chosen as the relation |
| 150 | `is-as-a-merely-masculine-principle-quite-unfitted-to-represent-the-totality-of` | `cannot-represent-totality-of` | `is-unfitted-to-represent` | a adds the Janus-face ground as a condition and widens scope to 'God or the self'; b conditions only on the masculine principle |
| 151 | `symbolizes-owing-to-the-absence-of-the-feminine-eros-the-typical-opposition-in-a-man-between-sex-and` | `symbolizes-sex's-opposition-to` | `None` | arm_b has no relation at all (null); nothing to agree with a's 'symbolizes sex's opposition to' |
| 155 | `is-what-the-little-single-individual-becomes-namely` | `is` | `is-equivalent-to` | a adds a scope restriction 'in the apocatastasis' absent from b; identity claim otherwise the same |
| 162 | `expressed-in-the-form-of-the-red-tincture-the-healing-or-whole-making-effect-of-a-certain-kind-of` | `expressed-healing-effect-of` | `expressed-effect-of` | a carries the 'It seems as though' hedge in modality; b states the expression unhedged |
| 165 | `discovered-that-the-sacred-myth-of-the-generation-birth-and-resurrection-of-the-redeemer-was-anticipated-feature-for-feature-by` | `found-myth-anticipated-in` | `found-myth-anticipated-by` | arm_a marks the claim as Bonus's conviction that Jung judges an error; arm_b states it flat with no attribution or hedge |
| 175 | `can-show-at-the-first-meeting-the-negative-qualities-that-characterize-an-unexpected-encounter-with` | `is-first-encountered-like` | `manifests-qualities-of` | arm_a says the first encounter with the self resembles an encounter with the unconscious; arm_b says the self manifests qualities of the unconscious, a predication arm_a's note expressly rejects |
| 177 | `led-the-western-alchemist-to-regard-as-a-task-enjoined-upon-him-the-sweating-out-of-the-soul-substance-in-the-form-of` | `seemed-to-require` | `led-to-sweating-of` | arm_a keeps it at 'seemed to require' as the alchemist's own construal; arm_b's 'led-to-sweating-of' claims the sweating followed, with no modality |
| 183 | `in-the-language-of-myth-perceives-the-sufferings-of-and-gives-form-and-existence-to` | `perceives-the-sufferings-of` | `gives-form-to` | arm_a carries 'perceives the sufferings of' and splits off giving form; arm_b carries 'gives-form-to' as the verb |
| 187 | `imagines-himself-the-tormentor-whereas-in-fact-he-is-the-tormented` | `imagines-himself-tormentor-of` | `is-tormented-by` | arm_a states the imagined role (tormentor of Mercurius); arm_b states the actual role (tormented by Mercurius) |
| 192 | `identifies-the-god-image-with-the-anima-rationalis` | `identifies-god-image-with` | `identifies-with` | arm_a carries the 'so to speak' hedge and marks it as Jung's inference from Augustine; arm_b has no modality |
| 222 | `their-mixing-begets-the-power-of-choice-in-man` | `give-rise-to` | `begets` | arm_a attributes the claim to the Clementine Homilies' doctrine as summarized by Jung; arm_b asserts 'begets' with no attribution frame |
| 223 | `his-mercy-and-his-anger-confront-each-other-within-him-as` | `harbours` | `embodies` | harbours (mercy and anger within him, hedged as a quoted prayer) versus embodies the opposites, unhedged and stronger |
| 227 | `before-manichaeism-had-always-believed-in-the-substantiality-of` | `attributed-substantiality-to` | `believed-in-substantiality-of` | arm_a marks the claim as Jung's conjecture ('It is as if'); arm_b asserts the belief with only 'without clearly realizing it' as modality |
| 250 | `signifies-life-in-the-iranian-view-where-saturn-signifies-death` | `signifies-life-unlike` | `None` | arm_b produced no relation at all |
| 253 | `their-battle-is-taken-by-rashi-as-an-eschatological-event-like-the-fight-with` | `are-likened-to` | `None` | arm_b produced no relation at all |
| 254 | `his-era-follows-the-war-of-the-tanninim-which-rashi-takes-to-be` | `follows-the-war-of` | `None` | arm_b is empty: no relation and no qualifiers, so it does not restate the claim at all, while arm_a gives follows-the-war-of with carrier, scope and modality |
| 255 | `the-talmudic-prophecy-of-his-era-is-conjectured-to-rest-on` | `is-prophesied-from` | `None` | arm_b is empty: no relation and no qualifiers, while arm_a gives is-prophesied-from with the conjectural hedge and the prophecy as carrier |

## C2 — seeded normalization corruptions

- planted: 40, caught (flagged **and** element named): **23** (0.575)
- flagged but the wrong element named: 2 — scored separately, never as catches (RULES #14)
- specificity on the 40 clean items: **0.925** (37 judged entailed)

| class | planted | caught | flagged, wrong element | missed | catch rate |
|---|---|---|---|---|---|
| verb_strengthened | 10 | 10 | 0 | 0 | 1.0 |
| scope_dropped | 10 | 1 | 0 | 9 | 0.1 |
| direction_reversed | 10 | 10 | 0 | 0 | 1.0 |
| modality_dropped | 10 | 2 | 2 | 6 | 0.2 |

### Every corruption not caught (17)

| # | class | outcome | reason |
|---|---|---|---|
| 206 | scope_dropped | not flagged | 'Asserted against' does not exceed 'asserted against the threat of'; historical framing kept in modality. |
| 196 | modality_dropped | not flagged | Consequence relation kept; 'in certain Protestant sects' survives as scope. |
| 8 | modality_dropped | flagged, named 'verb' | 'frees' asserts accomplishment where verbatim only says 'seeks liberation'; note claims modality carries 'seeks' but modality is null. |
| 214 | modality_dropped | not flagged | Elder-brother relation kept; the doctrinal frame of the two sons of God survives in carrier. |
| 115 | scope_dropped | not flagged | Flowing-together in Mercurius kept; the Wise Old Man as co-subject held in carrier. |
| 191 | scope_dropped | not flagged | 'made after Christ' carries the same 'after whose likeness' sense; Origen attribution kept in modality. |
| 7 | scope_dropped | not flagged | 'signifies spirit imprisoned in' matches 'inwardly means spirit imprisoned in'; alchemist's inward meaning kept in carrier and modality. |
| 14 | modality_dropped | not flagged | Verb restates the verbatim; 'on the person of' preserved in scope. |
| 244 | scope_dropped | not flagged | Sharing allegories with the devil is preserved; the dropped count is non-restrictive and the qualifier adds provenance only. |
| 229 | scope_dropped | not flagged | The 'only' restriction survives and antinomial terms are the opposites; direction and hedge intact. |
| 238 | modality_dropped | flagged, named 'verb' | 'is-never-matched-by' strengthens 'unmatched' into a universal temporal claim the verbatim does not make. |
| 84 | modality_dropped | not flagged | Parallels-ordering-of with the full reduction-to-order phrase in scope restates the verbatim. |
| 210 | scope_dropped | not flagged | Christ's act is kept in the verb and Gnostic teaching in modality; same claim. |
| 65 | modality_dropped | not flagged | Crops-up-near with 'as the simia Dei' in scope restates the verbatim. |
| 201 | scope_dropped | not flagged | Traces-evil-to man carries the 'first author of evil' claim with the exhortative voice in modality. |
| 235 | modality_dropped | not flagged | Priority over Christ is confined to a tendency among certain alchemists via carrier and scope. |
| 61 | scope_dropped | not flagged | Lies-hidden-in the unconscious preserves the claim; 'ocean of' is metaphor and the bravery clause is a declared split. |

### Clean items the gate flagged (3)

| # | element named | reason |
|---|---|---|
| 176 | condition | Verbatim claim is unconditional; the candidate adds a ch'i condition absent from the relation and quote, weakening and altering it. |
| 219 | verb | Verbatim has the daemonic claim to power BY the unconscious; 'produces-negative-inflation-in' relocates the inflation into the unconscious, changing its role. |
| 53 | condition | The quote says the true mandala is always built up through imagination; the candidate adds a condition restricting when, which the quote does not carry. |
