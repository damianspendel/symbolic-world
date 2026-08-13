# Query layer demo — 2026-08-13

Eight queries against the live graph, each with the output the command actually
produced. Nothing here is retyped or trimmed: the blocks are the tool's stdout.

**Graph state for every query below.** `seed.json` as committed at
`f83f6bfe604b23c90dbbaefc887bf3d39a1fa9d6`, read 2026-08-13: 407 nodes, 1555
edges, sha256 prefix `fc7704327caa`. Family states: 1264 assigned, 248
pending-adjudication, 41 no-family, 2 text-undecided. Declarations:
`pipeline/family/relation_declarations.json`, transcribed from
FAMILY_DEFINITIONS v0.7.1, 5 active and 1 dormant. Each command repeats that
state in its own footer, which is the copy to trust if the graph has moved since.

Quotes appear only where a command was run with `--quotes`, and they are the
graph's own stored quotes, capped at 25 words by the integrity checks.


## 1. The vocabulary as the graph carries it

`--list-families` reads every `relation_family` record and reports what it
finds. There is no family list inside the tool. 24 families hold at least one
assigned edge; FAMILY_DEFINITIONS defines 25, and `amplification` holds none
after the v0.7.1 re-run moved all 43 `amplified-by` edges elsewhere or to the
queue.

```
$ python3 tools/query/kg_query.py --list-families
archetypal-identity        124 edges over  25 effective strings
classification              47 edges over  12 effective strings
composition                 64 edges over  31 effective strings
correspondence             134 edges over  34 effective strings
dependence                  32 edges over  25 effective strings
derivation                  22 edges over  19 effective strings
doctrinal-attribution       65 edges over  56 effective strings
generation                  67 edges over  37 effective strings
instrumentality             12 edges over  12 effective strings
kinship                     16 edges over  14 effective strings
manifestation               50 edges over  19 effective strings
opposition                  34 edges over  16 effective strings
personification             37 edges over   7 effective strings
prefiguration               16 edges over   7 effective strings
privation                   24 edges over  14 effective strings
projection                  22 edges over  13 effective strings
psychic-effect             122 edges over  88 effective strings
separation                  20 edges over  17 effective strings
sequence                    20 edges over  15 effective strings
structural-position         51 edges over  39 effective strings
symbolization              198 edges over  41 effective strings
telos                       28 edges over  24 effective strings
transformation              20 edges over  14 effective strings
union                       39 edges over  17 effective strings

graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 2. A family query, and the strings it covers

The point of a family is that one query reaches relation strings that share a
sense but not a spelling. `kinship` is small enough to print whole: 16 edges over
14 distinct effective strings, so almost every edge in it uses a string of its
own. A query on any one string would return one or two rows.

```
$ python3 tools/query/kg_query.py --family kinship --quotes
The Hero                 has                  The Dual Mother                   [CW5 §494]  {kinship}
      "his birth is a rebirth from the mother-wife. That is why the hero so often has two mothers"
The Shulamite            consort-of           Anthropos / Adam Kadmon           [CW14 §609]  {kinship}
      "Adam Kadmon appears here in the classic form of the son-lover"
Anima Mundi              is-feminine-half-of  Mercurius                         [CW14 §450]  {kinship}
      "The anima mundi is the feminine half of Mercurius."
Sol                      masculine-half-of    Mercurius                         [CW14 §117]  {kinship}
      "Sol is regarded as the masculine and active half of Mercurius"
Sulphur                  companion-of         Luna                              [CW14 §134]  {kinship}
      "sulphur was the “companion of Luna.”"
Luna                     is-shadow-of         Sol                               [CW14 §172]  {kinship}
      "Luna is the “shadow of the sun, and with corruptible bodies she is consumed"
Regina (the Queen)       adopts               Rex (the King)                    [CW14 §435]  {kinship}
      "a “tutelary madonna” who adopts the king as her son"
Venus                    is-anima-of          Rex (the King)                    [CW14 §416]  {kinship}
      "Venus appears as the feminine aspect of the king, or as we should say, his anima"
Soul                     is-the-bride-of      Christ (as symbol)                [CW9ii §72]  {kinship}
      "His bride ( sponsa ) is the human soul"
The Devil / Satan        is-elder-brother-of  Christ (as symbol)                [CW9ii §77]  {kinship}
      "the doctrine of the two sons of God, of whom the elder was called Satanaël"
The Devil / Satan        is-elder-brother-of  Christ (as symbol)                [CW9ii §103, CW9ii §113, CW9ii §229]  {kinship}
      "the Ebionite notion that God had two sons, an elder one, Satan, and a younger one, Christ"
Behemoth                 is-double-of         Leviathan                         [CW9ii §185]  {kinship}
      "God’s monstrous antagonist produces a double because the God-image is incomplete and does not contain everything it logically ought to contain"
The Devil / Satan        is-brother-of        Christ (as symbol)                [CW9ii §401]  {kinship}
      "we have the “hostile brothers,” Christ and the devil, who were regarded as brothers in the Jewish-Christian tradition"
Moses                    is-accompanied-by    The shadow                        [CW9i §244]  {kinship}
      "On this pilgrimage he is accompanied by his “shadow,” the “servant” or “lower” man"
Khidr (the Verdant One)  pairs-with           Dhulqarnein (the Two-horned One)  [CW9i §253]  {kinship}
      "Khidr and Dhulqarnein are the great pair of friends, altogether comparable to the Dioscuri, as Vollers rightly emphasizes"
Demeter                  pairs-with           The Kore (the maiden)             [CW9i §306, CW9i §316]  {kinship}
      "Not only is the figure of Demeter and the Kore in its threefold aspect as maiden, mother, and Hecate"

family 'kinship' covers 14 effective relation strings over 16 assigned edges (membership read from seed.json's relation_family records): is-elder-brother-of (2), pairs-with (2), adopts (1), companion-of (1), consort-of (1), has (1), is-accompanied-by (1), is-anima-of (1), is-brother-of (1), is-double-of (1), is-feminine-half-of (1), is-shadow-of (1), is-the-bride-of (1), masculine-half-of (1)
16 rows.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 3. The same question, closure off

What is the Self symbolized by? The graph stores that relation in both
directions, and asking in one direction finds only what happens to be written
that way.

```
$ python3 tools/query/kg_query.py --subject the-self --relation symbolized-by
The Self  symbolized-by  The quaternity  [CW9ii §117]  {symbolization}
The Self  symbolized-by  Mandala         [CW9ii §208, CW9ii §379, CW9ii §426]  {symbolization}

2 rows.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 4. The same question, closure on

`--closure` reads the declared inverse `symbolizes` / `symbolized-by`
(FAMILY_DEFINITIONS line 371) and adds the other direction, labelled. Two stored
rows become 22. The 20 added rows are readings of edges that already exist: each
prints the edge it came from, carries that edge's citations, and is not written
back to the graph.

```
$ python3 tools/query/kg_query.py --subject the-self --relation symbolized-by --closure
The Self  symbolized-by  The quaternity                      [CW9ii §117]  {symbolization}
The Self  symbolized-by  Mandala                             [CW9ii §208, CW9ii §379, CW9ii §426]  {symbolization}
The Self  symbolized-by  Lapis philosophorum                 [CW12 §247, CW9ii §426, CW9ii §257, CW9ii §387, CW9ii §418]  {symbolization}  <derived:inverse-of(symbolizes) of lapis symbolizes the-self>
The Self  symbolized-by  Christ (as symbol)                  [CW9ii §123, CW11 §231, CW12 §452, CW9ii §70, CW9ii §79, CW9ii §115, CW9ii §123, CW9ii §171, CW9ii §321]  {symbolization}  <derived:inverse-of(symbolizes) of christ symbolizes the-self>
The Self  symbolized-by  Rebis / Hermaphrodite               [CW9ii §426]  {symbolization}  <derived:inverse-of(symbolizes) of rebis symbolizes the-self>
The Self  symbolized-by  Salt (Sal)                          [CW14 §329]  {symbolization}  <derived:inverse-of(symbolizes) of salt symbolizes the-self>
The Self  symbolized-by  Mercurius                           [CW13 §296]  {symbolization}  <derived:inverse-of(symbolizes) of mercurius symbolizes the-self>
The Self  symbolized-by  The Philosophical Tree (arbor phi…  [CW13 §304]  {symbolization}  <derived:inverse-of(symbolizes) of philosophical-tree symbolizes the-self>
The Self  symbolized-by  The opposites                       [CW14 §4]  {symbolization}  <derived:inverse-of(symbolizes) of the-opposites symbolizes the-self>
The Self  symbolized-by  Sulphur                             [CW14 §145]  {symbolization}  <derived:inverse-of(symbolizes) of sulphur symbolizes the-self>
The Self  symbolized-by  One Scintilla / Monad               [CW8 §388]  {symbolization}  <derived:inverse-of(symbolizes) of one-scintilla-monad symbolizes the-self>
The Self  symbolized-by  Adam                                [CW14 §558]  {symbolization}  <derived:inverse-of(symbolizes) of adam symbolizes the-self>
The Self  symbolized-by  Substantia coelestis (Dorn)         [CW14 §736]  {unclassified(pending-adjudication)}  <derived:inverse-of(symbolizes) of substantia-coelestis symbolizes the-self>
The Self  symbolized-by  Caelum (Dorn's heaven / quintesse…  [CW14 §765]  {symbolization}  <derived:inverse-of(symbolizes) of caelum symbolizes the-self>
The Self  symbolized-by  Squaring of the Circle              [CW14 §776]  {symbolization}  <derived:inverse-of(symbolizes) of squaring-of-the-circle symbolizes the-self>
The Self  symbolized-by  The Chariot (currus / Merkabah)     [CW14 §261]  {symbolization}  <derived:inverse-of(symbolizes) of chariot symbolizes the-self>
The Self  symbolized-by  Paradise (Garden of Eden)           [CW14 §276]  {symbolization}  <derived:inverse-of(symbolizes) of paradise symbolizes the-self>
The Self  symbolized-by  Echeneis / remora (the sucking-fi…  [CW9ii §219, CW9ii §223]  {symbolization}  <derived:inverse-of(symbolizes) of echeneis symbolizes the-self>
The Self  symbolized-by  Arcane substance (arcanum)          [CW9ii §224]  {symbolization}  <derived:inverse-of(symbolizes) of arcane-substance symbolizes the-self>
The Self  symbolized-by  Rex (the King)                      [CW9ii §310]  {symbolization}  <derived:inverse-of(symbolizes) of rex symbolizes the-self>
The Self  symbolized-by  Khidr (the Verdant One)             [CW9i §247]  {symbolization}  <derived:inverse-of(symbolizes) of khidr symbolizes the-self>
The Self  symbolized-by  The star                            [CW9i §683, CW9i §706]  {symbolization}  <derived:inverse-of(symbolizes) of star symbolizes the-self>

22 rows.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 5. An identity walk, depth 2

Rex, two hops out over `archetypal-identity` edges. The header states the
limit before the first hop, and hops crossed against the stored direction say so.
Nine hops, nine real edges, each carrying the citations that edge stores.

```
$ python3 tools/query/kg_query.py --walk identity --subject rex --depth 2
Walk over archetypal-identity edges. Each hop below is ONE edge, printed with its own
citation. No transitive identity is asserted: a term reached in two hops is
not thereby identical to the start. FAMILY_DEFINITIONS v0.7.1 rejects
transitivity on every family (line 131, the uroboros argument); this walk is
exploration of what the graph connects, not inference over it.

start: Rex (the King)  (rex)

depth 1:
  Rex (the King) → Sol   via  Rex (the King) --synonym-of--> Sol   [CW14 §501]
  Rex (the King) → Gold (aurum)   via  Rex (the King) --symbolizes--> Gold (aurum)   [CW14 §354]
  Rex (the King) → Ancient of Days (Antiquus dierum)   via  Rex (the King) --identified-with--> Ancient of Days (Antiquus dierum)   [CW14 §374]
  Rex (the King) → Adam   via  Adam --identified-with--> Rex (the King)   [CW14 §546]  (traversed against the edge)

depth 2:
  Gold (aurum) → Chelidonia (celandine)   via  Chelidonia (celandine) --synonym-of--> Gold (aurum)   [CW14 §698]  (traversed against the edge)
  Adam → Prima materia   via  Adam --identified-with--> Prima materia   [CW14 §570, CW14 §552]
  Adam → Mercurius   via  Adam --synonym-of--> Mercurius   [CW14 §565]
  Adam → The inner man   via  Adam --is--> The inner man   [CW14 §606]
  Adam → Christ (as symbol)   via  Adam --is-identical-with--> Christ (as symbol)   [CW9ii §307, CW9ii §313]

9 hops.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 6. What a human actually ruled on

`--provenance` matches a substring of `relation_family.by`, so this returns
the edges assigned by the adjudication sittings plus the one assigned by applying
a sitting's precedent. These are the assignments with the strongest provenance in
the graph, and there are 21 of them against 1555 edges.

```
$ python3 tools/query/kg_query.py --provenance human-adjudication
Individuation                       is-a                         Coniunctio                          [CW9ii §117, CW9ii §117]  {archetypal-identity}
Christ (as symbol)                  is-a                         God-image (imago Dei)               [CW9ii §71, CW9ii §71, CW9ii §72]  {archetypal-identity}
The quaternity                      exemplified-by               The four elements                   [CW14 §261]  {unclassified(no-family)}
Dragon                              symbolizes                   Unconsciousness (initial state)     [CW13 §118]  {symbolization}
Squaring of the Circle              leads-to                     The unconscious                     [CW12 §167]  {sequence}
Mercurius                           is-identified-with           Hermes                              [CW12 §172]  {archetypal-identity}
Mercurius                           is-a                         Psychopomp                          [CW12 §409]  {classification}
Rex (the King)                      renewed-through              The unconscious                     [CW14 §471]  {dependence}
Christ (as symbol)                  is-a                         Anthropos / Adam Kadmon             [CW14 §565, CW14 §484]  {archetypal-identity}
Salt (Sal)                          symbolizes                   Sapientia / Wisdom                  [CW14 §324]  {symbolization}
Trickster                           forerunner-of                Christ (as symbol)                  [CW9i §472]  {prefiguration}
Mandala                             is                           God-image (imago Dei)               [CW9i §572]  {archetypal-identity}
Leviathan                           symbolizes                   The unconscious                     [CW14 §277]  {symbolization}
Phoenix                             symbolizes                   Christ (as symbol)                  [CW14 §474]  {doctrinal-attribution}
Archetype (archetype-as-such)       transcends                   The psyche                          [CW8 §420]  {structural-position}
The fourth or 'inferior' function…  is-contaminated-with         The unconscious                     [CW12 §193, CW12 §145]  {psychic-effect}
Dionysus                            dissolves-distinctions-into  The psyche                          [CW12 §118]  {union}
Alchemy                             is-concretization-of         Individuation                       [CW13 §140]  {projection}
Homo maximus                        is-approached-through        The alchemical opus (opus alchymi…  [CW13 §203]  {telos}
The Messiah                         is-prophesied-from           Astrology                           [CW9ii §135]  {derivation}
The celestial Pole                  is-characterized-by          The quaternity                      [CW9ii §206]  {unclassified(no-family)}

21 rows.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 7. The pending queue

248 edges are `pending-adjudication`. This is the Aion slice of that queue,
the first ten rows, showing what the two model arms could not agree on in CW 9ii.

```
$ python3 tools/query/kg_query.py --state pending-adjudication --volume 9ii --limit 10
Privatio boni                    led-to-elimination-of                                                          The Devil / Satan      [CW9ii §74]  {unclassified(pending-adjudication)}
Summum Bonum                     is-effective-source-of                                                         Privatio boni          [CW9ii §80, CW9ii §94]  {unclassified(pending-adjudication)}
Unconsciousness (initial state)  does-not-distinguish                                                           Evil (malum)           [CW9ii §97]  {unclassified(pending-adjudication)}
The psyche                       is-suspected-birthplace-of                                                     Evil (malum)           [CW9ii §114]  {unclassified(pending-adjudication)}
Yahweh                           his-mercy-is-named-his-right-hand-and-his-justice-his-left                     The opposites          [CW9ii §107]  {unclassified(pending-adjudication)}
Evil (malum)                     does-not-endanger                                                              God-image (imago Dei)  [CW9ii §99]  {unclassified(pending-adjudication)}
The opposites                    are-united-in-the-pre-manichaean-god-image-just-as-yang-and-yin-are-united-in  Tao                    [CW9ii §104]  {unclassified(pending-adjudication)}
The Self                         is-describable-only-through                                                    The opposites          [CW9ii §115]  {unclassified(pending-adjudication)}
Lapis philosophorum              is-given-priority-over                                                         Christ (as symbol)     [CW9ii §123]  {unclassified(pending-adjudication)}
Lapis philosophorum              may-take-precedence-over                                                       Christ (as symbol)     [CW9ii §122]  {unclassified(pending-adjudication)}

10 rows.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## 8. A declaration that knows where it stops

`produces` / `originates-in` is declared for the generation family only:
FAMILY_DEFINITIONS line 559 says only tradition-to-tradition `originates-in` is
derivation, and a doctrine descending from another is not a begetting run
backwards. The restriction is enforced on the source edge, so the two queries
below differ although the relation string is the same.

Who produces projection? The graph never says so in those words. `projection originates-in the-unconscious` is assigned generation, so the declaration licenses the reading, and the derived row names the edge it read.

```
$ python3 tools/query/kg_query.py --object projection --relation produces --closure
The unconscious  produces  Projection  [CW9ii §17]  {generation}  <derived:inverse-of(originates-in) of projection originates-in the-unconscious>

1 row.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

Same question of alchemy, whose `alchemy originates-in gnosticism` edge is assigned derivation. Closure returns nothing: gnosticism did not beget alchemy, it transmitted to it, and the declaration stops at the family line.

```
$ python3 tools/query/kg_query.py --object alchemy --relation produces --closure
(no rows)

0 rows.  graph state: 407 nodes / 1555 edges; families 1264 assigned, 248 pending-adjudication, 41 no-family, 2 text-undecided; seed.json sha256:fc7704327caa; declarations relation_declarations.json from FAMILY_DEFINITIONS v0.7.1, 5 active
```

## What these eight do not show

The demo runs the instrument, not the graph's correctness. Every family shown is
an assignment on record, not a verified fact; the 248 pending edges are pending
because two model arms disagreed, and the 1264 assigned ones carry whatever
provenance their `by` field states. Section 6 is the only slice of the eight
where a human made the call.
