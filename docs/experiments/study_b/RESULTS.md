# Study B — the gate on realistic corruptions (n=200, seed 20260901, blind)

Pre-registered design: `DESIGN.md`. Harness: `tools/studies/study_b_*.py`. Plant: `plant_manifest.json`. Verdicts: `verdicts.jsonl`. Graph commit `12635b0`. Gate: claude-fable-5, blind, judging each claim against its full source paragraph.

A corruption counts as caught only if the gate flagged it AND its reason named the corrupted component (RULES #14). Flagged-without-diagnosis is listed separately and never counted as a catch.

## Results (95% Wilson intervals)

| Class | Caught | % | 95% CI | Flagged but not diagnosed |
|---|---|---|---|---|
| near-referent-drift | 24/25 | 96% | 80–99% | 0 |
| subject-expansion | 24/25 | 96% | 80–99% | 0 |
| hedge-deletion | 10/25 | 40% | 23–59% | 2 |
| analogy-to-identity | 18/25 | 72% | 52–86% | 2 |
| **pooled sensitivity** | **76/100** | **76%** | 67–83% | 4 |
| specificity (clean controls) | 88/100 | 88% | 80–93% | — |

E1b measured the same gate on coarse seeded corruptions at 86% sensitivity (CI 78–91%) and 93% specificity. The two are stated measured-vs-measured: different corruption populations, same instrument. They are never pooled.

## Every miss

- **n=8** (hedge-deletion, not flagged) — verdict TRUE. Presented: `primitive-mentality -animates-> matter`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; Jung asserts that on the primitive level matter seems endowed with soul — the 'seems' belongs to the primitive perception, not to Jung's own hedging.
- **n=17** (analogy-to-identity, not flagged) — verdict TRUE. Presented: `true-man -is-> the-self`; relation planted `is` for `corresponds-to`.
  Gate: Quote verbatim; Jung asserts the adept's own self is the 'true man', an explicit identity in his interpretive voice.
- **n=26** (hedge-deletion, not flagged) — verdict TRUE. Presented: `oak -symbolizes-> the-vessel`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; the paragraph states the oak as trough is the vessel in Jung's own interpretive voice; referents, strength, type and confidence all hold.
- **n=35** (near-referent-drift, not flagged) — verdict TRUE. Presented: `magnet-of-the-wise -attracts-> alchemical-fish`; object planted `alchemical-fish` for `echeneis`.
  Gate: Quote verbatim; the paragraph reports the alchemical view that man's magnet exerts the attraction on the Echeneis itself; reports-parallel and high confidence fit.
- **n=48** (hedge-deletion, not flagged) — verdict TRUE. Presented: `shulamite -consort-of-> anthropos`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; the paragraph makes the Shulamite the mother-beloved and bride in whom Adam Kadmon as son-lover and bridegroom reproduces himself; consort-of holds.
- **n=57** (hedge-deletion, not flagged) — verdict TRUE. Presented: `malchuth -amplified-by-> widow`; confidence planted `high` for `medium`.
  Gate: All six hold; Jung reports the kabbalistic-alchemical narrative in which Malchuth became a widow, correctly typed as parallel.
- **n=64** (hedge-deletion, not flagged) — verdict TRUE. Presented: `salt -correlated-with-> luna`; confidence planted `high` for `medium`.
  Gate: All six hold; in the alchemical quaternity salt is correlated with the feminine, lunar side, reported as alchemical doctrine.
- **n=85** (analogy-to-identity, not flagged) — verdict TRUE. Presented: `the-self -is-> atman`; relation planted `is` for `corresponds-to`.
  Gate: All six hold; the claim_type flags it as the reported Indian doctrine, in which the Self is brahman/atman, exactly as the paragraph presents it.
- **n=89** (hedge-deletion, not flagged) — verdict TRUE. Presented: `fish -its-sudden-activation-is-conjectured-to-stem-from-a-second-source-in-> astrology`; confidence planted `high` for `medium`.
  Gate: All six hold; the conjecture is encoded in the relation, and the follow-up sentence "This source is astrology" is declarative, supporting high confidence.
- **n=94** (hedge-deletion, not flagged) — verdict TRUE. Presented: `rose-coloured-blood -expressed-in-the-form-of-the-red-tincture-the-healing-or-whole-making-effect-of-a-certain-kind-of-> eros`; confidence planted `high` for `medium`.
  Gate: All six hold; the opening is hedged but the paragraph's closing sentence asserts unhedged that the rose-coloured blood is the manifestation of a certain kind of Eros that makes whole.
- **n=96** (analogy-to-identity, not flagged) — verdict TRUE. Presented: `atman -is-> the-self`; relation planted `is` for `parallels`.
  Gate: All six hold; the paragraph presents the Indian doctrine in which the self is Atman or Purusha, correctly typed as a reported parallel.
- **n=98** (analogy-to-identity, not flagged) — verdict TRUE. Presented: `sulphur -is-> lumen-naturae`; relation planted `is` for `corresponds-to`.
  Gate: All six hold; in Dorn's doctrine, correctly typed as a reported parallel, sulphur is equated with the light of nature.
- **n=103** (hedge-deletion, not flagged) — verdict TRUE. Presented: `marriage-horoscope-experiment -exemplifies-> synchronicity`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; Jung names the experiment's meaningful chance result a synchronistic phenomenon in his own voice.
- **n=104** (subject-expansion, not flagged) — verdict TRUE. Presented: `union-of-opposites -amplified-by-> regina`; subject planted `union-of-opposites` for `coniunctio`.
  Gate: Elided quote matches; the Queen in the coniunctio pictures amplifies the supreme union of hostile opposites; reports-parallel fits the alchemical imagery.
- **n=115** (analogy-to-identity, not flagged) — verdict TRUE. Presented: `circulation-of-light -is-> circulatio`; relation planted `is` for `corresponds-to`.
  Gate: Quote verbatim; Jung asserts it is the same idea of the circular opus found independently in Chinese alchemy — sameness of idea, stated in his own voice.
- **n=134** (hedge-deletion, not flagged) — verdict TRUE. Presented: `yoga -dissolves-> the-ego`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; Jung asserts as fact ('the fact remains') that in the yogis' samadhi the unconscious has swallowed up ego-consciousness, supporting 'dissolves'.
- **n=141** (hedge-deletion, not flagged) — verdict TRUE. Presented: `reductive-function -opposes-> prospective-function`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; the paragraph states reductive dreams' effect is the very reverse of constructive and that they cannot properly be called prospective, supporting the opposition.
- **n=146** (hedge-deletion, not flagged) — verdict TRUE. Presented: `christ -appears-from-this-standpoint-as-the-archetype-of-> consciousness`; confidence planted `high` for `medium`.
  Gate: Quote verbatim; the relation carries the paragraph's own 'from this standpoint' qualifier, and the sentence is Jung's declarative interpretive assertion.
- **n=147** (hedge-deletion, flagged, diagnosis did not name the component) — verdict CORRECTED. Presented: `mother-complex -leads-to-> incest`; confidence planted `high` for `medium`.
  Gate: The subject is wrong: the paragraph explicitly says the complex need not take this course; it is the substitute overdeveloped Eros that almost invariably leads to the unconscious incestuous relationship.
- **n=152** (analogy-to-identity, flagged, diagnosis did not name the component) — verdict CORRECTED. Presented: `quintessence -is-> god-image`; relation planted `is` for `corresponds-to`.
  Gate: The claim_type is wrong: the paragraph expounds Dorn's doctrine ('Thus, he knew that...', footnoted to Dorn), not Jung's own interpretive voice.
- **n=165** (hedge-deletion, not flagged) — verdict TRUE. Presented: `dream -reveals-> individuation`; confidence planted `high` for `medium`.
  Gate: All six hold: the long dream-series spontaneously expresses the process Jung names individuation, in his own voice.
- **n=178** (analogy-to-identity, flagged, diagnosis did not name the component) — verdict CORRECTED. Presented: `benedicta-viriditas -is-> anima-mundi`; relation planted `is` for `corresponds-to`.
  Gate: The confidence is wrong: Mylius's claim-carrying clause is 'might be called the Soul of the World' — a hedged, conditional naming, warranting medium.
- **n=180** (hedge-deletion, not flagged) — verdict TRUE. Presented: `coniunctio -followed-by-> nigredo`; confidence planted `high` for `medium`.
  Gate: Both quote fragments are verbatim; the paragraph's sequence runs coniunctio to death, blackness and nigredo, supporting followed-by in Jung's interpretive voice.
- **n=193** (hedge-deletion, flagged, diagnosis did not name the component) — verdict CORRECTED. Presented: `divine-child -represents-> collective-unconscious`; confidence planted `high` for `medium`.
  Gate: The object is widened: the paragraph says the child motif represents the preconscious, childhood aspect of the collective psyche, not the collective unconscious wholesale.

## Flags on clean controls

Production references, so a flag here may be the gate finding a real nuance rather than a false positive; specificity is a lower bound.

- **n=11** CORRECTED — `solar-phallus -recurs-in-> myth`. The object is widened: this paragraph shows the solar tube recurring only in Dieterich's Mithraic liturgy text, not in myth and fairytale as a class.
- **n=24** CORRECTED — `myth -compensates-> the-christian-standpoint`. The subject is widened: 'our fairytale' — the particular German tale — describes the compensating processes; the paragraph does not assert this of myth and fairytale as a class.
- **n=36** CORRECTED — `leonardo -depicts-> dual-mother`. The confidence is too high: the claim-carrying sentence is hedged with 'in all probability', which warrants medium.
- **n=107** CORRECTED — `the-unconscious -frustrates-> will`. The subject is at fault: the claim-carrying sentence says the dream fails to obey the will and opposes conscious intentions; the unconscious is credited only with autonomy, not the frustrating.
- **n=108** CORRECTED — `four-elements -constitute-> quaternity`. The confidence is at fault: the sentence is hedged — 'a sort of second quaternity' in a passage opened by 'Cabalistic influences may be conjectured' — warranting medium, not high.
- **n=110** CORRECTED — `incest -symbolizes-> union-of-opposites`. The claim_type is at fault: the paragraph presents the symbolization as alchemy's doing — 'Alchemy... exalted... incest, into a symbol' — a tradition's doctrine, not Jung's own assertion.
- **n=121** CORRECTED — `consciousness -confuses-> imago`. The subject is at fault: the paragraph attributes the contamination of object and imago to people, who cannot distinguish God from God-image — not to consciousness as a psychic system.
- **n=133** CORRECTED — `fish -exemplifies-> chance`. The subject referent is conflated: what the paragraph rules a chance grouping is the six-fold series of fish occurrences, not the Fish/Ichthys symbol itself.
- **n=153** CORRECTED — `world-wheel -differs-from-> mandala`. The object widens a particular into its class: 'the former' the Wheel is distinguished from is the Lamaic mandala just presented, not the mandala in general.
- **n=155** FALSE — `syzygy -contradicts-> dogma`. The subject is wrong: the paragraph never names the syzygy and supports only that one monk's particular vision was heretical, widened here into a general syzygy-contradicts-dogma claim.
- **n=179** CORRECTED — `psychology -becomes-> science`. The confidence field is malformed ('high -> medium') and the paragraph itself qualifies the development as gradual and 'not complete even today', so medium.
- **n=197** CORRECTED — `artifex -seeks-liberation-of-> god-image`. The object is off: the paragraph speaks of liberating God, the deity lost and sleeping in matter — 'imago Dei' is a psychologizing substitution the paragraph does not make.
