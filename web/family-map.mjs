// The relation-string -> family map, derived from seed.json on every build.
//
// BACKLOG item 2: "the reverse index: for each family, the relation strings that
// land in it, with counts ... It also exposes the strings that fit nowhere, which
// is the honest part." Nothing here is hand-maintained — if this file and
// seed.json disagree, seed.json is right and this recomputes.
//
// The string counted is the EFFECTIVE relation: relation_normalized.relation
// where that layer exists, else the frozen verbatim relation. That is the string
// the family was assigned to, and the same choice docs/FAMILY_DEFINITIONS.md
// makes when it counts strings.
//
// A string can appear under more than one family, and that is the point rather
// than a defect: assignment is per edge, never per string (rule 1 of the layer).
// `split_strings` counts how often that actually happens, so the claim is
// measured instead of asserted.

const effective = (e) =>
  (e.relation_normalized && e.relation_normalized.relation) || e.relation

const bump = (m, k) => m.set(k, (m.get(k) || 0) + 1)

// The four ways a settled record is arrived at. An unrecognised `by` string is
// reported as itself rather than folded into the commonest case, so a new
// provenance cannot hide inside the arms-agreed count.
function byKind (by) {
  const b = String(by || '').toLowerCase()
  // precedent BEFORE human: the precedent records name the human sitting they
  // came from ("precedent (human-adjudication 2026-08-10: ...)"), so a
  // human-first test swallows them and the page reports a ruling nobody made
  if (b.includes('precedent')) return 'recorded precedent'
  if (b.includes('human')) return 'human ruling'
  if (b.includes('disputes')) return 'arms agreed, the check disputed it'
  if (b.startsWith('opus+gemini-agreed')) return 'two blind arms agreed'
  return by || '(no provenance recorded)'
}
const rows = (m) => [...m.entries()]
  .map(([string, edges]) => ({ string, edges }))
  .sort((a, b) => b.edges - a.edges || a.string.localeCompare(b.string))

export function familyMap(seed) {
  const perFamily = new Map()      // family -> Map(string -> count)
  const homeless = new Map()       // no-family
  const undecided = new Map()      // text-undecided
  const pending = new Map()        // queued for a human ruling
  const stateCount = { assigned: 0, 'pending-adjudication': 0, 'no-family': 0, 'text-undecided': 0 }
  const provenance = new Map()     // how each SETTLED record was arrived at
  let unrecorded = 0

  for (const e of seed.edges) {
    const rf = e.relation_family
    const s = effective(e)
    if (!rf || !rf.state) { unrecorded++; continue }
    if (rf.state in stateCount) stateCount[rf.state]++
    // RULES #10 — a family label means what its record says. The page describes
    // how records were arrived at from the `by` field, never from one sentence.
    if (rf.state !== 'pending-adjudication') bump(provenance, byKind(rf.by))
    if (rf.state === 'assigned' && rf.value) {
      if (!perFamily.has(rf.value)) perFamily.set(rf.value, new Map())
      bump(perFamily.get(rf.value), s)
    } else if (rf.state === 'no-family') bump(homeless, s)
    else if (rf.state === 'text-undecided') bump(undecided, s)
    else if (rf.state === 'pending-adjudication') bump(pending, s)
  }

  const families = [...perFamily.entries()]
    .map(([family, strings]) => ({
      family,
      edges: [...strings.values()].reduce((a, b) => a + b, 0),
      strings: rows(strings)
    }))
    .sort((a, b) => b.edges - a.edges || a.family.localeCompare(b.family))

  // how many distinct strings the assigned layer touches, and how many of them
  // land in more than one family
  const seen = new Map()
  for (const f of families) for (const r of f.strings) bump(seen, r.string)
  const split = [...seen.values()].filter((n) => n > 1).length

  return {
    source: 'seed.json',
    derived: 'web/family-map.mjs at build time — no hand-maintained copy exists',
    counts_relation: 'effective (relation_normalized.relation where present, else relation)',
    totals: {
      edges: seed.edges.length,
      assigned: stateCount.assigned,
      pending: stateCount['pending-adjudication'],
      no_family: stateCount['no-family'],
      text_undecided: stateCount['text-undecided'],
      unrecorded,
      families: families.length,
      assigned_strings: seen.size,
      split_strings: split,
      homeless_strings: homeless.size
    },
    provenance: [...provenance.entries()]
      .map(([kind, edges]) => ({ kind, edges }))
      .sort((a, b) => b.edges - a.edges),
    families,
    homeless: rows(homeless),
    text_undecided: rows(undecided),
    pending: { edges: stateCount['pending-adjudication'], strings: rows(pending).length }
  }
}
