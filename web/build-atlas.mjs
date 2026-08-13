// Build step for "The Atlas": detect thematic communities, compute a STABLE baked
// layout, and project the verified graph into the shapes the v1.4 UI needs.
// Reads ../seed.json (+ page concordance, ../docs/FAMILY_DEFINITIONS.md, and any
// pending-review queue left in ../pipeline/work/). Writes only under web/.
//
//   src/atlas.json     meta · nodes · edges · clusters · pages · concordance
//   src/families.json  family definitions extracted verbatim from the doc
//   src/pending.json   the family review queue, or an explicit "absent" marker
//   public/families.html  the complete definitions document, rendered
//
//   node → { id, label, type, tradition, latin, color, cluster, register, x, y }
//   edge → { id, key, source, target, relation, relation_normalized, family,
//            layer, kind, volumes, confidence, refs }
import { readFileSync, writeFileSync, existsSync } from 'fs'
import { familyMap } from './family-map.mjs'
import { byVolume } from './query-semantics.mjs'

const here = (p) => new URL(p, import.meta.url)
const seed = JSON.parse(readFileSync(here('../seed.json')))

// Publication gate is structural: refuse to build if any reference is unverified.
for (const e of seed.edges)
  for (const r of (e.references || []))
    if (!r.verified) { console.error(`UNVERIFIED ref in ${e.subject}->${e.object} (CW${r.volume} §${r.paragraph}) — build refused`); process.exit(1) }
let pages = {}
try { pages = JSON.parse(readFileSync(here('../app/Sources/Resources/pages.json'))) } catch {}

// ---------------------------------------------------------------- palette ---
// R0.2 — the Seven Metals. Node type is coloured by its metal, so the legend is
// itself a claim about the material. One block here and one in style.css are the
// whole surface of this decision.
const TYPE_COLOR = {
  Concept:   '#d4af37',  // gold — Sol
  Symbol:    '#c2cdd6',  // silver — Luna
  Figure:    '#c58152',  // copper — Venus
  Operation: '#b5502f',  // iron — Mars
  Substance: '#63997f',  // verdigris — the oxide
  Motif:     '#8b96a5',  // lead — Saturn
  Archetype: '#d4af37'   // no live nodes; reads as Concept
}
// the three alchemical phase colours a node may override its metal with
const PHASE = { black: '#1c1c1c', white: '#e8e2d0', red: '#b23a2e' }

// ------------------------------------------------- R10.0 · the token table ---
// Every colour in the artifact resolves here. This file writes them out three
// ways so nothing has to restate a hex: src/tokens.css for the app (imported by
// style.css), public/chrome.css for the generated pages, and src/tokens.json for
// tools/build_ledger_page.py. A literal hex anywhere else is a contract breach
// and the consistency sweep greps for exactly that.

// ---- the public dataset -----------------------------------------------------
// /graph.json is the citable data download: the full verified graph as built,
// with provenance. A 76-node relic from the site's first week sat at this URL
// until 2026-08-07; this emission replaces it every build so it can never go
// stale again.
import { readFileSync as _rf, writeFileSync as _wf } from 'node:fs'
function emitPublicDataset(seed, meta) {
  const out = {
    _about: 'The Symbolic World — a verified knowledge graph of C. G. Jung\'s Collected Works. ' +
      'Every edge cites its CW volume and paragraph with a verbatim quote (max 25 words) and the ' +
      'verification provenance of a three-model chain (proposer, gate, cross-vendor auditor). ' +
      'Method: https://symbolicworld.observer/#/method',
    _license: 'Data: CC BY 4.0. Quotes are brief excerpts from the Collected Works cited under fair use.',
    _version: meta.version,
    _generated: meta.built,
    _counts: meta.counts,
    _frozen_release: meta.frozen,
    nodes: seed.nodes,
    edges: seed.edges,
  }
  _wf(new URL('./public/graph.json', import.meta.url), JSON.stringify(out, null, 1))
  console.log(`graph.json: public dataset emitted — ${seed.nodes.length} nodes, ${seed.edges.length} edges`)
}

const TOKENS = {
  ground: '#0b0a08', 'ground-2': '#100e0b', panel: '#171410',
  ink: '#eae3d2', 'ink-faint': '#9a9382', 'ink-dim': '#6f6a5d', 'ink-bright': '#ffffff',
  'ink-label': '#c9c2b0',
  gold: '#d4af37', 'gold-dim': '#94782a',
  surface: 'rgba(23, 20, 16, 0.94)', hairline: '#2b261e',
  'm-concept': TYPE_COLOR.Concept, 'm-symbol': TYPE_COLOR.Symbol, 'm-figure': TYPE_COLOR.Figure,
  'm-operation': TYPE_COLOR.Operation, 'm-substance': TYPE_COLOR.Substance, 'm-motif': TYPE_COLOR.Motif,
  sage: '#7fc9a0', rubedo: '#d0685a', amber: '#d9a84f', teal: '#9ec9c3', muted: '#888888',
  // interaction accents
  hi: '#f5d76e',            // the lit / highlighted state
  sel: '#f0cf82',           // the selected state
  'edge-idle': '#5a5245',   // an edge with no layer colour
  'layer-structural': '#4a443a',
  // chip and badge borders, keyed to the state they carry
  'b-sage': '#2f5c46', 'b-teal': '#39575c', 'b-amber': '#6b5527', 'b-rubedo': '#5c2f28',
  'b-ok': '#2f4a3c',
  // R10.10 family lenses — one hue per bridge kind, kept inside the metals range
  // (gold, silver, verdigris) so the lens never introduces a foreign palette
  'lens-symbolization': '#d4af37',   // gold, as Concept
  'lens-correspondence': '#c2cdd6',  // silver, as Symbol
  'lens-projection': '#63997f',      // verdigris, as Substance
  // the nigredo/albedo/rubedo phase colours, for nodes that carry one
  'phase-black': '#1c1c1c', 'phase-white': '#e8e2d0', 'phase-red': '#b23a2e',
  display: '"Hoefler Text", "Baskerville", "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif',
  serif: '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif',
  mono: 'ui-monospace, "SF Mono", Menlo, monospace'
}
const rootBlock = () => ':root {\n' + Object.entries(TOKENS).map(([k, v]) => `  --${k}: ${v};`).join('\n') + '\n}\n'

// V2-R10 — the site menu, in one place for JavaScript. tools/build_ledger_page.py
// holds the same list for the pages python writes, and a test compares the two
// rendered menus link for link. Order is fixed: the atlas first, then the
// surfaces that read it, then the record of how it was built.
// The taxonomy (editorial ruling, 2026-08-13): four groups, fixed order. The
// group label is a quiet signpost, not a heading — it says what kind of place
// the links under it lead to, and carries no weight of its own. Batches are
// deliberately absent: they are reached through the ledger's facet links and
// through the release entries that shipped them, and putting 57 of them behind
// a menu item is what made the ledger unwieldy in the first place.
const MENU = [
  ['explore', [['/#/atlas', 'atlas'], ['/query', 'query'], ['/#/concordance', 'concordance']]],
  ['reference', [['/families', 'families']]],
  ['provenance', [['/ledger', 'ledger'], ['/releases', 'releases'], ['/disputes', 'disputes']]],
  ['about', [['/#/method', 'method'], ['/ontology', 'ontology']]]
]
// V2-R11 — the header fragment. Row one is identical on every surface; row two
// carries whatever varies.
const siteHeader = (current, where) => `<header class="site-header">
<div class="hrow hrow-1"><a class="brand" href="/">The Symbolic World</a>${topMenu(current)}</div>
<div class="hrow hrow-2"><span class="where">${esc(where || '')}</span></div>
</header>`
const topMenu = (current) => '<nav class="topmenu">' + MENU.map(([group, items]) =>
  `<span class="mgroup">${group}</span>` + items.map(([href, label]) =>
    `<a href="${href}"${href === current ? ' aria-current="page"' : ''}>${label}</a>`).join('')
).join('') + '</nav>'

const nbr = new Map(seed.nodes.map(n => [n.id, new Set()]))
for (const e of seed.edges) {
  if (nbr.has(e.subject) && nbr.has(e.object)) { nbr.get(e.subject).add(e.object); nbr.get(e.object).add(e.subject) }
}
const deg = id => nbr.get(id).size

// --- regions = curated domains keyed off node type (stable & meaningful) ---
// Region ids are namespaced ('dom-…') so a compound region parent can never
// collide with a real node id (e.g. the CW8 concept node 'psyche').
const DOMAIN = {
  Concept:   { id: 'dom-psyche',  label: 'The Psyche',           color: TYPE_COLOR.Concept },
  Archetype: { id: 'dom-psyche',  label: 'The Psyche',           color: TYPE_COLOR.Concept },
  Operation: { id: 'dom-opus',    label: 'The Opus',             color: TYPE_COLOR.Operation },
  Substance: { id: 'dom-materia', label: 'The Materia',          color: TYPE_COLOR.Substance },
  Symbol:    { id: 'dom-symbols', label: 'The Symbols',          color: TYPE_COLOR.Symbol },
  Figure:    { id: 'dom-figures', label: 'The Figures',          color: TYPE_COLOR.Figure },
  Motif:     { id: 'dom-motifs',  label: 'Motifs & Traditions',  color: TYPE_COLOR.Motif }
}
const nodeCluster = new Map()
const sizes = new Map()
for (const n of seed.nodes) {
  const d = DOMAIN[n.type] || { id: 'dom-other', label: 'Other', color: '#888' }
  nodeCluster.set(n.id, d.id)
  sizes.set(d.id, (sizes.get(d.id) || 0) + 1)
}
const clusters = []
const seenDomain = new Set()
for (const n of seed.nodes) {
  const d = DOMAIN[n.type] || { id: 'other', label: 'Other', color: '#888' }
  if (seenDomain.has(d.id)) continue
  seenDomain.add(d.id)
  clusters.push({ id: d.id, label: d.label, color: d.color, size: sizes.get(d.id) })
}
clusters.sort((a, b) => b.size - a.size)

// --- stable regional layout: anchor each region on a ring, then place its nodes
//     on a phyllotaxis (sunflower) spiral. Deterministic and force-free, so
//     spacing is guaranteed even for nodes whose only links cross regions
//     (a force layout collapses those into a corner). Highest-degree nodes sit
//     at each region's centre; SPREAD sets the minimum gap between nodes. ---
const GOLDEN = Math.PI * (3 - Math.sqrt(5))
const SPREAD = 125
const CX = 2050, CY = 1650, RING = 2100
const anchors = {}
clusters.forEach((c, i) => {
  const a = (i / clusters.length) * 2 * Math.PI - Math.PI / 2
  anchors[c.id] = { x: CX + RING * Math.cos(a), y: CY + RING * Math.sin(a) }
})
let pos = {}
for (const c of clusters) {
  const ids = seed.nodes.filter(n => nodeCluster.get(n.id) === c.id).map(n => n.id)
    .sort((x, y) => deg(y) - deg(x))   // hubs first -> centre
  const a = anchors[c.id]
  ids.forEach((id, i) => {
    const r = SPREAD * Math.sqrt(i + 0.5)
    const th = i * GOLDEN
    pos[id] = { x: Math.round(a.x + r * Math.cos(th)), y: Math.round(a.y + r * Math.sin(th)) }
  })
}

// ------------------------------------------------------- R8.5 · registers ---
// The Concordance splits the graph into two registers. Membership is derived
// from node `type`, with two explicit lists for the nodes whose type does not
// settle it — recorded here, never inferred at runtime.
//   psyche side      Concept
//   laboratory side  Substance, Operation, Symbol
//   neither          Figure, Motif (they populate both traditions)
const LAB_CONCEPTS = new Set([
  // Concept-typed nodes that belong to the laboratory: alchemical doctrine,
  // Paracelsan physiology, and the arcane substances named as principles.
  'alchemy', 'hermetic-philosophy', 'aniadus', 'aquaster', 'archeus', 'ares',
  'axiom-of-maria', 'iliaster', 'lumen-naturae', 'mysterium-magnum', 'sapientia',
  'scaiolae', 'spiritus-mundi', 'substantia-coelestis', 'tetrameria', 'theoria',
  'unio-mentalis', 'vir-unus'
])
const PSYCHE_OPERATIONS = new Set([
  // Operation-typed nodes that are psychological technique, not laboratory work.
  'active-imagination', 'amplification', 'shadow-confrontation'
])
const registerOf = (n) => {
  if (n.type === 'Concept') return LAB_CONCEPTS.has(n.id) ? 'laboratory' : 'psyche'
  if (n.type === 'Operation') return PSYCHE_OPERATIONS.has(n.id) ? 'psyche' : 'laboratory'
  if (n.type === 'Substance' || n.type === 'Symbol') return 'laboratory'
  return ''            // Figure, Motif — no register
}

const atlasNodes = seed.nodes.map(n => ({
  id: n.id, label: n.label, type: n.type, tradition: n.tradition || '', latin: n.latin || '',
  color: n.color_phase ? PHASE[n.color_phase] : (TYPE_COLOR[n.type] || '#888'),
  cluster: nodeCluster.get(n.id), register: registerOf(n), x: pos[n.id].x, y: pos[n.id].y
}))
const registerById = Object.fromEntries(atlasNodes.map(n => [n.id, n.register]))

// --------------------------------------------------------- R3.2 · edges -----
// `relation_family` has not merged yet. Absence is carried honestly: family is
// null, and the UI renders nothing family-related rather than an empty chip.
// The merged layer records an administrative `state` alongside the family, and
// only `assigned` carries a value — a pending or refused edge has `value: null`.
// Reading the state field rather than parsing the value is what keeps R4.1's
// three states distinct: "queued for a human" and "no family carried" must never
// collapse into the same record, and neither may be mistaken for "not yet
// assigned at all" (an edge with no relation_family key).
const STATE_MAP = {
  assigned: 'family',
  'pending-adjudication': 'pending',
  'no-family': 'unclassified',
  'text-undecided': 'unclassified',
  'not-a-relation': 'not-a-relation'
}
const familyOf = (e) => {
  const raw = e.relation_family
  if (!raw) return null
  if (typeof raw === 'string') {          // legacy flat form
    const m = raw.match(/^unclassified\(([^)]+)\)$/)
    const st = raw === 'not-a-relation' ? 'not-a-relation' : m ? (m[1] === 'pending-adjudication' ? 'pending' : 'unclassified') : 'family'
    return { value: raw, state: st, reason: m ? m[1] : '', name: st === 'family' ? raw : '', assigned_by: '', assigned_date: '', reason_text: '' }
  }
  const rawState = raw.state || (raw.value || raw.family ? 'assigned' : '')
  const state = STATE_MAP[rawState] || 'unclassified'
  const name = raw.value || raw.family || ''
  // A single canonical value per edge, so chips, filters and counts agree.
  const value = state === 'family' ? name
    : rawState === 'not-a-relation' ? 'not-a-relation'
    : `unclassified(${rawState || 'unspecified'})`
  return {
    value, state, name: state === 'family' ? name : '',
    reason: state === 'family' ? '' : rawState,
    assigned_by: raw.by || raw.assigned_by || raw.proposed_by || '',
    assigned_date: raw.date || raw.assigned_date || raw.proposed_date || '',
    reason_text: raw.reason || '',
    adjudicated_by: raw.adjudicated_by || '', adjudicated_date: raw.adjudicated_date || ''
  }
}

const atlasEdges = seed.edges.map((e, i) => {
  const refs = e.references || []
  const layer = e.bridge ? 'bridge' : e.layer === 'amplification' ? 'amplification' : (!refs.length) ? 'structural' : 'spine'
  const rn = e.relation_normalized || null
  return {
    id: 'e' + i,
    key: `${e.subject}|${e.relation}|${e.object}`,
    source: e.subject, target: e.object,
    relation: e.relation,
    // R3.4 — the verbatim relation stays primary. The normalized verb phrase and
    // its qualifiers ride alongside as a layer above the verified claim.
    relation_normalized: rn ? {
      relation: rn.relation,
      qualifiers: Object.fromEntries(Object.entries(rn.qualifiers || {}).filter(([, v]) => v)),
      verified_by: rn.verified_by || '', verified_date: rn.verified_date || ''
    } : null,
    family: familyOf(e),
    layer, kind: e.kind || '',
    volumes: [...new Set(refs.map(r => String(r.volume)))],
    // Design proposal 2 — a hedged claim should not read as a flat one.
    confidence: refs.length ? (refs.some(r => r.confidence === 'medium') ? 'medium' : 'high') : '',
    refs   // full records: volume, paragraph, quote, claim_type, confidence, gates
  }
})

const famStates = {}
for (const e of atlasEdges) if (e.family) famStates[e.family.state] = (famStates[e.family.state] || 0) + 1
const familyLayerPresent = atlasEdges.some(e => e.family)

// ------------------------------------------------- R8 · the Concordance -----
// R8.2 — the bridge set is selected by family once the family layer exists;
// until then every cited cross-register edge is offered and the mode is recorded
// so the UI can say which rule produced the list.
const BRIDGE_FAMILIES = new Set(['symbolization', 'correspondence', 'projection'])
const bridgeMode = familyLayerPresent ? 'family' : 'cross-register'
const bridges = atlasEdges.filter(e => {
  const a = registerById[e.source], b = registerById[e.target]
  if (!a || !b || a === b) return false
  if (!e.refs.length) return false
  if (bridgeMode === 'family') return e.family && BRIDGE_FAMILIES.has(e.family.value)
  return true
}).map(e => e.id)

// R8.3 — the evidence-mix strip: what share of a node's references come from the
// alchemical trilogy versus everything else. Computed here, never at runtime.
const VOL_GROUP = v => (['12', '13', '14'].includes(String(v)) ? 'alchemical' : 'other')
const mix = {}
for (const e of atlasEdges)
  for (const id of [e.source, e.target])
    for (const r of e.refs) {
      const m = mix[id] || (mix[id] = { alchemical: 0, other: 0, total: 0, volumes: {} })
      m[VOL_GROUP(r.volume)]++; m.total++
      m.volumes[r.volume] = (m.volumes[r.volume] || 0) + 1
    }

// R8.4 / R9.8 — the guided six. Curation selects WHICH verified edges to walk;
// it never edits what they say. Each stop is anchored to the exact citation the
// spec names, so the walk cannot silently drift onto a different edge between
// the same two nodes. A stop whose citation is not in the graph is DROPPED and
// reported, never quietly substituted.
const GUIDED = [
  ['the-self', 'lapis', '9ii', 264, 'The stone the alchemists sought is a projection of the self.'],
  ['the-unconscious', 'prima-materia', '12', 431, 'The prima materia they worked on is the unconscious under another name.'],
  ['individuation', 'the-opus', '9ii', 418, 'The work itself pictures the process, stage by stage.'],
  ['the-opposites', 'mercurius', '12', 404, 'The marriage that completes the work: what unites the opposites.'],
  ['collective-unconscious', 'mercurius', '13', 284, 'The uniting substance stands for the deepest layer of the psyche.'],
  ['anima', 'salt', '14', 321, 'So the correspondence is structural: a substance read as a person.']
]
// R10.10 — the reverse walk. The historical reader travelled the other way:
// from the substances in front of them to the psychology they turned out to be
// describing. Same verified edges, opposite direction of travel.
const GUIDED_REVERSE = [
  ['the-unconscious', 'prima-materia', '12', 431, 'Begin where the alchemist began: with the raw material in the vessel.'],
  ['the-opposites', 'mercurius', '12', 404, 'Mercurius, the substance that reconciles what will not mix.'],
  ['collective-unconscious', 'mercurius', '13', 284, 'The same substance, read as a layer of the psyche.'],
  ['anima', 'salt', '14', 321, 'Salt: its bitterness turns out to name a person.'],
  ['individuation', 'the-opus', '9ii', 418, 'The work, followed to its end, is a process of becoming whole.'],
  ['the-self', 'lapis', '9ii', 264, 'And the stone at the end of it is the self.']
]
const resolveWalk = (spec, name) => spec.map(([a, b, vol, para, gloss]) => {
  const es = atlasEdges.filter(e =>
    ((e.source === a && e.target === b) || (e.source === b && e.target === a)) &&
    e.refs.some(r => String(r.volume) === vol && Number(r.paragraph) === para))
  if (!es.length) { console.warn(`GUIDED STOP DROPPED (${name}) — ${a}/${b} CW ${vol} §${para} is not in the graph`); return null }
  return { psyche: a, laboratory: b, gloss, cite: `CW ${vol} §${para}`, edges: es.map(e => e.id) }
}).filter(Boolean)
const guided = resolveWalk(GUIDED, 'psyche-first')
const guidedReverse = resolveWalk(GUIDED_REVERSE, 'laboratory-first')

// R9.8 — the curated core. Ranked by evidence weight: reference count first,
// then the psyche-side node's bridge degree. The ranking is recorded here so
// "the load-bearing thirty" is a computed claim about the data rather than a
// hand-picked list, and "show all" is the same list unranked.
const bridgeDegree = {}
for (const id of bridges) {
  const e = atlasEdges.find(x => x.id === id)
  for (const n of [e.source, e.target]) bridgeDegree[n] = (bridgeDegree[n] || 0) + 1
}
const journeys = [
  { id: 'psyche', title: 'From the psyche', lead: 'Follow the narrative on the front page: each stop is the clause it came from, with its verified edge.', dir: 'psyche-first' },
  { id: 'laboratory', title: 'From the laboratory', lead: 'The way a historical reader travelled: start at the substances, arrive at the psychology.', dir: 'laboratory-first' }
]
const CORE_N = 30
const core = [...bridges].sort((x, y) => {
  const a = atlasEdges.find(e => e.id === x), b = atlasEdges.find(e => e.id === y)
  const psy = e => registerById[e.source] === 'psyche' ? e.source : e.target
  return b.refs.length - a.refs.length ||
    (bridgeDegree[psy(b)] || 0) - (bridgeDegree[psy(a)] || 0) ||
    a.id.localeCompare(b.id)
}).slice(0, CORE_N)

// ------------------------------------- family definitions, extracted ---------
// R3.3 — sourced from docs/FAMILY_DEFINITIONS.md, never paraphrased. The chip
// panel shows the document's own words; a mismatch here is a build failure, not
// a cosmetic one.
const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]))
const inline = s => esc(s)
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  .replace(/\*([^*]+)\*/g, '<em>$1</em>')
  .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')

let families = [], famVersion = '', boundaryRules = [], famDoc = ''
// R3.6 — the external-validity figures on the families page interpolate from
// the committed receipts, never from typed literals, so the copy cannot drift
// from the record (editorial ruling, 2026-08-12: "no drift"). Missing file = no section
// rather than stale numbers.
const evPath = here('../docs/experiments/external_validity_2026-08/results.json')
const EV = existsSync(evPath) ? JSON.parse(readFileSync(evPath, 'utf8')) : null

const famPath = here('../docs/FAMILY_DEFINITIONS.md')
if (existsSync(famPath)) {
  famDoc = readFileSync(famPath, 'utf8')
  famVersion = (famDoc.match(/^# Relation families.*?(v[\d.]+)/m) || [, ''])[1]

  // the boundary-rules section, bullet by bullet
  const brSec = famDoc.split(/^## Boundary rules[^\n]*$/m)[1]
  if (brSec) {
    const body = brSec.split(/^## /m)[0]
    for (const b of body.split(/\n(?=- )/)) {
      const t = b.trim().replace(/^- /, '').replace(/\s*\n\s*/g, ' ')
      if (t) boundaryRules.push({ title: (t.match(/^\*\*([^*]+)\*\*/) || [, ''])[1].replace(/[:*]+$/, '').replace(/`/g, ''), html: inline(t) })
    }
  }

  const secs = famDoc.split(/\n(?=### )/).filter(s => /^### \d+\./.test(s))
  for (const s of secs) {
    const head = s.match(/^### (\d+)\.\s+([a-z-]+)(.*)$/m)
    if (!head) continue
    const body = s.slice(s.indexOf('\n') + 1)
    // split on the bolded labels the document uses
    const parts = body.split(/\n(?=\*\*[A-Z])/)
    const definition = parts[0].trim().replace(/\s*\n\s*/g, ' ')
    const labelled = {}
    for (const p of parts.slice(1)) {
      const m = p.match(/^\*\*([^*]+?):?\*\*\s*/)
      if (!m) continue
      labelled[m[1].replace(/:$/, '')] = p.slice(m[0].length).trim().replace(/\s*\n\s*/g, ' ')
    }
    const seedText = labelled['Seeds'] || ''
    // seeds read as `subject relation object` (CW citation) — take the first three
    const seeds = []
    for (const m of seedText.matchAll(/`([^`]+)`(?:\s*(?:\/\s*`[^`]+`\s*)*)?(?:\s*\(([^)]*§[^)]*)\))?/g)) {
      if (seeds.length >= 3) break
      if (!/\s/.test(m[1])) continue        // bare relation strings are not examples
      seeds.push({ text: m[1], cite: (m[2] || '').split(',')[0].trim() })
    }
    const notes = Object.entries(labelled)
      .filter(([k]) => k !== 'Boundary' && k !== 'Seeds')
      .map(([k, v]) => ({ label: k, html: inline(v) }))
    families.push({
      n: Number(head[1]), id: head[2], name: head[2],
      added: (head[3].match(/\*\(([^)]+)\)\*/) || [, ''])[1],
      definition_html: inline(definition),
      boundary_html: labelled['Boundary'] ? inline(labelled['Boundary']) : '',
      seeds, seeds_html: inline(seedText), notes
    })
  }
}

// The three administrative states get their explanations from the document's own
// rule 4, so R4.3's hover text is sourced rather than invented.
const STATE_NOTE = {
  family: 'Classified: this edge was assigned a relation family, checked by the calibrated gate.',
  pending: 'Pending review: the two model arms disagreed, so a human ruling is queued. Not yet judged.',
  unclassified: 'No family: a well-formed relation that the vocabulary does not cover. Counted, not hidden.',
  'not-a-relation': 'Not a relation: the relation slot holds a clause. Excluded from every family denominator.',
  absent: 'The family layer has not merged into this build. No edge carries a family yet.'
}

// R3.5 — the relation-string -> family map, derived from seed.json every build
// (web/family-map.mjs). It is emitted as data and consumed by the families page;
// no hand-maintained copy of it exists anywhere.
const famMap = familyMap(seed)
console.log(`family map: ${famMap.totals.families} families over ` +
  `${famMap.totals.assigned_strings} relation strings ` +
  `(${famMap.totals.split_strings} land in more than one), ` +
  `${famMap.totals.homeless_strings} homeless strings, ` +
  `${famMap.totals.pending} pending`)

writeFileSync(here('./src/families.json'), JSON.stringify({
  version: famVersion, source: 'docs/FAMILY_DEFINITIONS.md', doc_url: './families',
  state_note: STATE_NOTE, boundary_rules: boundaryRules, families, map: famMap
}))

// The families page: reader-facing exposition first, then the definitions
// document in full — the "full definitions" destination in R3.3. The exposition
// is kept in its own variable because the copy assertions scan it and must NOT
// scan the rendered source document (see the note above copySources).
const famPageCopy = famVersion ? familiesPageCopy(famMap, famVersion) : ''
writeFileSync(here('./public/families.html'), renderDoc(famDoc, famPageCopy))

// ------------------------------------------------ R7 · the review queue -----
// Copied in when the assignment pass leaves one behind; otherwise an explicit
// absence the UI can explain rather than a silently empty list.
const queuePath = here('../pipeline/work/family_pending_queue.json')
let pending = { present: false, generated: new Date().toISOString().slice(0, 10), items: [] }
if (existsSync(queuePath)) {
  const q = JSON.parse(readFileSync(queuePath, 'utf8'))
  const items = Array.isArray(q) ? q : (q.items || q.queue || [])
  pending = { present: true, generated: q.generated || new Date().toISOString().slice(0, 10), source: 'pipeline/work/family_pending_queue.json', items }
}
writeFileSync(here('./src/pending.json'), JSON.stringify(pending))

// ---------------------------------------------- R10.0 · the shared chrome ---
// Breadcrumb, back control and search field are defined ONCE, here, and used by
// the app and by every generated page. R10.6 wants the breadcrumb in the same
// place on every route; the only way that stays true is for there to be a single
// rule set.
const chromeBlock = () => `
.page-bar {
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; gap: 0.9rem;
  height: 3rem; padding: 0 clamp(1rem, 4vw, 2.5rem);
  background: rgba(11, 10, 8, 0.94); border-bottom: 1px solid var(--hairline);
}
.page-bar .back {
  font: 0.62rem var(--mono); letter-spacing: 0.05em; text-transform: none;
  color: var(--ink-faint); background: none; border: 0; padding: 0;
  cursor: pointer; text-decoration: none; white-space: nowrap;
}
.page-bar .back:hover, .page-bar .back:focus-visible { color: var(--gold); outline: none; }
.page-bar .where {
  font: 0.62rem var(--mono); letter-spacing: 0.05em; text-transform: none;
  color: var(--gold-dim); white-space: nowrap;
}
.page-bar .spacer { margin-left: auto; }
/* V2-R11 — the site header. One structure and one geometry everywhere: a
   fixed-width brand block, then the menu. Nothing whose width varies with the
   page may sit before the menu, so it lands on the same pixel whichever page
   you arrive on; the breadcrumb, the version chip and the app's controls go on
   the second row. Sticky, so it stays put while a long page scrolls. */
.site-header {
  position: sticky; top: 0; z-index: 60;
  background: var(--ground); border-bottom: 1px solid var(--hairline);
}
.site-header .hrow { display: flex; align-items: center; gap: 1rem; padding: 0 clamp(1rem, 4vw, 2.5rem); }
.site-header .hrow-1 { height: 3rem; }
.site-header .hrow-2 { min-height: 2.15rem; padding-bottom: 0.4rem; gap: 0.9rem; flex-wrap: wrap; }
.site-header .brand {
  flex: 0 0 13rem; font-family: var(--display); font-size: 1.05rem; font-weight: 500;
  color: var(--ink); text-decoration: none; white-space: nowrap; letter-spacing: 0.005em;
}
.site-header .brand h1 { font: inherit; margin: 0; }
.site-header .hdr-right { margin-left: auto; display: flex; align-items: center; gap: 0.9rem; }
/* The app's header is the same structure. style.css keeps #topbar fixed rather
   than sticky — the atlas body does not scroll, so fixed and sticky look the
   same there — and its id outranks this class, which is why only the box model
   is restated here. */
#topbar.site-header { display: block; height: auto; padding: 0; }
@media (max-width: 760px) {
  .site-header .brand { flex: 0 0 auto; }
  .site-header .hrow { gap: 0.6rem; padding: 0 0.75rem; }
  .site-header .hrow-1 { height: auto; padding-top: 0.45rem; flex-wrap: wrap; }
}
/* V2-R10 — the site menu. One definition, used by the app's header, by every
   generated page's header, and by the pages the python generator writes. */
.topmenu { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.15rem 0.7rem; }
.topmenu .mgroup {
  font: 0.5rem var(--mono); letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-dim); margin-left: 0.45rem;
}
.topmenu .mgroup:first-child { margin-left: 0; }
.topmenu a {
  font: 0.62rem var(--mono); letter-spacing: 0.05em; color: var(--ink-faint);
  text-decoration: none; white-space: nowrap; padding: 0.1rem 0;
}
.topmenu a:hover, .topmenu a:focus-visible { color: var(--gold); outline: none; }
.topmenu a[aria-current="page"] { color: var(--gold); }
.std-search {
  width: min(340px, 38vw);
  background: var(--surface); border: 1px solid var(--hairline); border-radius: 999px;
  padding: 0.5rem 0.9rem; color: var(--ink); font-family: var(--serif); font-size: 0.9rem; outline: none;
}
.std-search:focus { border-color: var(--gold-dim); }
`

// ------------------------------------------------- R5.5 · the works bar -----
// One segment per volume, sized and lit by that volume's REFERENCE count. The
// bar is a data statement before it is a control: it shows where the evidence
// is deep and where it is thin. Counts are computed here so the strip never
// recomputes them at runtime.
const VOL_LABEL = {
  '5': 'Symbols of Transformation', '8': 'Structure & Dynamics of the Psyche',
  '9i': 'Archetypes & the Collective Unconscious', '9ii': 'Aion',
  '11': 'Psychology & Religion', '12': 'Psychology & Alchemy',
  '13': 'Alchemical Studies', '14': 'Mysterium Coniunctionis',
  '16': 'Practice of Psychotherapy'
}
const volRefs = {}, volEdges = {}
for (const e of atlasEdges) {
  for (const r of e.refs) volRefs[String(r.volume)] = (volRefs[String(r.volume)] || 0) + 1
  for (const v of e.volumes) volEdges[v] = (volEdges[v] || 0) + 1
}
// V2-R8 — collection order, through the one comparator (web/query-semantics.mjs).
const volumes = Object.keys(volRefs).sort(byVolume)
  .map(v => ({ volume: v, label: VOL_LABEL[v] || '', references: volRefs[v], edges: volEdges[v] || 0 }))

// The voice facet (claim_type) joins the chip row; its values come from the data.
const voices = {}
for (const e of atlasEdges) for (const r of e.refs) if (r.claim_type) voices[r.claim_type] = (voices[r.claim_type] || 0) + 1

// ------------------------------------------------------------- atlas.json ---
const refCount = seed.edges.reduce((a, e) => a + (e.references || []).length, 0)
const meta = {
  version: 'v1.4-dev',
  built: new Date().toISOString().slice(0, 10),
  counts: { nodes: atlasNodes.length, edges: atlasEdges.length, references: refCount },
  // The frozen published release the paper describes. A constant because the tag
  // is frozen; the live counts above are read from the graph on every build.
  frozen: { version: 'v1.3.0', nodes: 248, edges: 669, references: 699, url: '/v1.3/' },
  familyLayer: { present: familyLayerPresent, version: famVersion, states: famStates, families: families.length },
  normalized: atlasEdges.filter(e => e.relation_normalized).length,
  bridgeMode, volumes, voices,
  layers: Object.fromEntries(['spine', 'amplification', 'bridge', 'structural']
    .map(l => [l, atlasEdges.filter(e => e.layer === l).length]))
}
writeFileSync(here('./src/atlas.json'), JSON.stringify({
  meta, nodes: atlasNodes, edges: atlasEdges, clusters, pages,
  concordance: { bridges, core, guided, guidedReverse, journeys, mix, bridgeDegree, registers: { psyche: 'The Psyche', laboratory: 'The Laboratory' } }
}))

emitPublicDataset(seed, meta)
console.log(`atlas: ${atlasNodes.length} nodes, ${atlasEdges.length} edges, ${refCount} references, ${clusters.length} regions`)
console.log('regions:', clusters.map(c => `${c.label} (${c.size})`).join(' · '))
console.log(`families: ${families.length} extracted (${famVersion || 'no version'}), ${boundaryRules.length} boundary rules`)
console.log(`family layer on edges: ${familyLayerPresent ? JSON.stringify(famStates) : 'ABSENT — no edge carries relation_family'}`)
console.log(`normalized relations: ${meta.normalized} · concordance bridges: ${bridges.length} (${bridgeMode}), core ${core.length} · walks: psyche ${guided.length}/${GUIDED.length}, laboratory ${guidedReverse.length}/${GUIDED_REVERSE.length}`)
console.log(`review queue: ${pending.present ? pending.items.length + ' items' : 'absent'}`)
console.log('works bar:', volumes.map(v => `CW ${v.volume} ${v.references}`).join(' · '))

// ---------------------------------------------------------------------------
// A small markdown renderer, sufficient for FAMILY_DEFINITIONS.md: headings,
// paragraphs, lists, tables and inline emphasis. Deliberately not a dependency.
function renderMarkdown(md) {
  const out = []
  const lines = md.split('\n')
  let i = 0, list = null
  const closeList = () => { if (list) { out.push(`</${list}>`); list = null } }
  while (i < lines.length) {
    const l = lines[i]
    if (/^\s*$/.test(l)) { closeList(); i++; continue }
    const h = l.match(/^(#{1,6})\s+(.*)$/)
    if (h) { closeList(); out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`); i++; continue }
    if (/^\|/.test(l) && /^\|[\s:|-]+\|?\s*$/.test(lines[i + 1] || '')) {
      closeList()
      const cells = r => r.replace(/^\||\|$/g, '').split('|').map(c => inline(c.trim()))
      out.push('<div class="tw"><table><thead><tr>' + cells(l).map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>')
      i += 2
      while (i < lines.length && /^\|/.test(lines[i])) { out.push('<tr>' + cells(lines[i]).map(c => `<td>${c}</td>`).join('') + '</tr>'); i++ }
      out.push('</tbody></table></div>'); continue
    }
    const li = l.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/)
    if (li) {
      const want = /^\d/.test(li[2]) ? 'ol' : 'ul'
      if (list !== want) { closeList(); out.push(`<${want}>`); list = want }
      let text = li[3]
      while (i + 1 < lines.length && /^\s{2,}\S/.test(lines[i + 1]) && !/^\s*([-*]|\d+\.)\s/.test(lines[i + 1])) { text += ' ' + lines[++i].trim() }
      out.push(`<li>${inline(text)}</li>`); i++; continue
    }
    closeList()
    let para = l
    while (i + 1 < lines.length && !/^\s*$/.test(lines[i + 1]) && !/^(#{1,6}\s|\||\s*([-*]|\d+\.)\s)/.test(lines[i + 1])) para += ' ' + lines[++i].trim()
    out.push(`<p>${inline(para)}</p>`); i++
  }
  closeList()
  return out.join('\n')
}

// ------------------------------------------- the families page · the copy ---
// BACKLOG item 3 and its anti-overclaim checklist bind every sentence below.
// Six things this page may not do, each paired with what it does instead:
//   · never "verified families" — a family is ASSIGNED; "verified" belongs to
//     the quote and its paragraph, and the page says so in as many words
//   · never "the gate catches errors" flat — it catches the classes we plant;
//     the figures are version-bound and live in the calibration records, not in
//     this copy, so they cannot go stale here
//   · never any implication of scholarly consensus — the page states that the
//     families are ours, internally calibrated and externally unvalidated
//   · never a tidy total — no-family, text-undecided, the pending queue and the
//     homeless strings are shown with real counts beside the assigned ones
//   · never "families reveal the structure of Jung's thought" — they record how
//     WE sorted relations he wrote
//   · agreement is not correctness, said where agreement is described
// Every number on the page comes from the derived map; the copy assertion at the
// foot of this file scans the rendered result and fails the build on a literal
// that atlas.json meta and the map cannot account for.
function familiesPageCopy(map, version) {
  const t = map.totals
  const num = n => `<strong>${n}</strong>`
  const stringList = (rows) => rows.map(r =>
    `<span class="sstr"><code>${esc(r.string)}</code><i>${r.edges}</i></span>`).join('')

  // V2-R2 — each family name links to its own page, where the definition is
  // quoted in full beside the family's live counts and its queued items.
  const famBlocks = map.families.map(f => `<section class="fam">
  <h3><a href="/family-${esc(f.family)}">${esc(f.family)}</a> <em>${f.edges}</em></h3>
  <div class="strs">${stringList(f.strings)}</div>
</section>`).join('\n')
  const empty = families.map(f => f.id).filter(id => !map.families.some(f => f.family === id))

  const provRows = map.provenance.map(p =>
    `<tr><td>${esc(p.kind)}</td><td>${p.edges}</td></tr>`).join('')

  const worked = boundaryRules
    .filter(r => /layer: amplification|indistinguishability/i.test(r.title))
    .map(r => `<li>${r.html}</li>`).join('\n')

  return `<h1>Relation families</h1>
<p class="sub">The classification layer, ruleset ${esc(version)} — what it claims, what it does not, and every relation string in it.</p>

<h2>What a family is</h2>
<p>A family is a classification <em>over</em> a relation that has already been checked. The claim underneath — subject, relation, object, the verbatim quote, the paragraph it came from — went through the verification chain before any of this began, and the family layer does not reopen it. It asks a second and much narrower question: what kind of relation is this one?</p>
<p>So the two words are kept apart, deliberately. A citation is <em>verified</em>: a machine confirmed the quote is letter-exact in its paragraph, and a model from a different family judged that paragraph against the claim. A family is <em>assigned</em>: two models read the definitions document and independently arrived at the same name for the relation. Different evidence, different word. There is no such thing as a verified family on this site.</p>
<p>These are our families. They record how this project sorted relations Jung wrote — not a structure discovered in his thought, and not a position the field has agreed on. The graph is a map of assertions rather than a reading, and that holds harder here than anywhere else on the site.</p>

${EV ? `<h2>Checked against readers of Jung</h2>
<p>In August 2026 we put a sample of these assignments to the secondary literature: ${EV.items} items, drawn by seeded stratification and weighted toward the contested families, checked in ${['zero','one','two','three','four'][EV.passes]} pre-registered passes against ${['zero','one','two','three','four','five','six','seven','eight','nine'][EV.works_consulted]} works of Jungian scholarship: Jacobi's <em>Psychology of C.G. Jung</em>, the <em>Critical Dictionary of Jungian Analysis</em>, von Franz's <em>Alchemy: An Introduction</em>, ${['zero','one','two','three','four'][EV.edinger_volumes]} volumes of Edinger, and Abraham's <em>Dictionary of Alchemical Imagery</em>. The question was not whether Jung's claim is true — the verification chain had already asked that. It was whether the KIND of relation we recorded is the kind a reader of the literature would say Jung asserts.</p>
<p>The result, stated exactly: the literature treats ${EV.treated} of the ${EV.assigned_purposive_scored} sampled assignments; scholars' renderings agreed with our family on ${EV.agrees} of those ${EV.treated}, disagreed on ${EV.disagrees}, and split among themselves on ${EV.scholars_split}. The other ${EV.not_treated} pairs no consulted work treats at all — Jung's image-level assertions are often simply not discussed anywhere. The disagreements were not absorbed: they produced ${['zero','one','two','three','four','five','six','seven'][EV.rulings_produced]} rule changes, folded into the ruleset as ${esc(EV.ruleset_version_produced)}, the largest of which sends every <code>amplified-by</code> edge back for reclassification because two independent reference authors read those relations as content claims, not adduced parallels.</p>
<p>Two limits. Agreement here is not endorsement: no scholar reviewed this vocabulary, and where the sample agreed it mostly agreed on the everyday families. And the check also measured the literature itself: the same reference author writes "X is Mercurius" and "X is a symbol of Mercurius" for the same pair, sometimes on one page. On the hardest boundary this layer draws, the field the check consulted does not hold a stable line either. The full record (sample, per-item worksheets, both review passes, the disagreements in full) is committed at <code>docs/experiments/external_validity_2026-08/</code> in the repository.</p>` : ''}

<h2>How an edge gets a family</h2>
<ol>
<li>Two models classify blind — one Opus-family, one Gemini — each reading the definitions document and the edge, neither able to see the other's answer.</li>
<li>Where they agree, the family is recorded with the ruleset version it was agreed under, because a later version can retire the rule an assignment rested on.</li>
<li>Where they disagree, no model breaks the tie. The edge is queued and a person rules on it, and the ruling lands signed and dated.</li>
<li>Refusals are kept apart. <em>No family</em> means our vocabulary is short. <em>Text undecided</em> means Jung's own sentence hedges between two readings. Pooling them would let a thin vocabulary hide inside a hedge.</li>
</ol>
<p>Agreement between the two arms measures whether the document can be followed consistently. It is not evidence that the document is right: neither arm is ground truth, and the definitions were drafted by one of the model families working in this pipeline.</p>
<p>A separate gate is calibrated by planting classification errors of known kind among real assignments and counting which come back correctly diagnosed. That measures the instrument — whether it still catches the sorts of mistake we know how to make — and says nothing about whether the families cut Jung's thought at the right joints. The figures are recorded per ruleset version in <code>pipeline/family_calibration/records/</code> and are not restated in this copy, because a number written into prose outlives the version it measured.</p>

<h2>Where the layer stands</h2>
<div class="tw"><table>
<thead><tr><th>State</th><th>Relations</th><th>What it means</th></tr></thead>
<tbody>
<tr><td>assigned</td><td>${t.assigned}</td><td>both arms named the same family, or a person ruled</td></tr>
<tr><td>pending a ruling</td><td>${t.pending}</td><td>the arms disagreed; queued, not guessed</td></tr>
<tr><td>no family</td><td>${t.no_family}</td><td>well-formed relation, our vocabulary does not cover it</td></tr>
<tr><td>text undecided</td><td>${t.text_undecided}</td><td>the source sentence hedges between two families</td></tr>
</tbody></table></div>
<p>That is ${num(t.assigned)} of ${num(t.edges)} relations classified, with ${num(t.pending)} still waiting on a person and ${num(t.no_family + t.text_undecided)} that no family was forced onto. The queue is not a backlog to be cleared by machine; clearing it is what the human step is for.</p>
<p>How the settled records were arrived at:</p>
<div class="tw"><table><thead><tr><th>Arrived at by</th><th>Relations</th></tr></thead><tbody>${provRows}</tbody></table></div>

<h2>The map: which relation strings land in which family</h2>
<p>The reverse index, derived from the graph on every build. ${num(t.families)} families over ${num(t.assigned_strings)} distinct relation strings; the number beside each string is how many relations carry it. ${num(t.split_strings)} of those strings appear under more than one family, which is the layer's central commitment made visible: a family is assigned to an edge in its paragraph, never to a string in the abstract. <code>is</code> alone spans identity, classification and position.</p>
${famBlocks}
${empty.length ? `<p>${empty.map(id => `<a href="/family-${esc(id)}">${esc(id)}</a>`).join(', ')} ${empty.length === 1 ? 'is a family in the ruleset that currently holds no assigned relation' : 'are families in the ruleset that currently hold no assigned relation'}, so ${empty.length === 1 ? 'it has' : 'they have'} no block above. ${empty.length === 1 ? 'The page is' : 'The pages are'} kept, and ${empty.length === 1 ? 'reports' : 'report'} the count as zero: a family emptied by a reclassification is a finding, and dropping it would hide the finding.</p>` : ''}

<h2>What fits nowhere</h2>
<p>${num(t.homeless_strings)} relation strings carry a relation that is well formed and that no family covers. They are counted rather than absorbed, because a vocabulary that covers everything has stopped discriminating:</p>
<div class="strs homeless">${stringList(map.homeless)}</div>
${map.text_undecided.length ? `<p>And the strings where the sentence itself refuses to settle — a property of the text, not of the vocabulary:</p>
<div class="strs homeless">${stringList(map.text_undecided)}</div>` : ''}

<h2>Where the boundaries are decided</h2>
<p>Two of the rules that do the discriminating, quoted from the definitions document exactly as they stand at ${esc(version)}. Each was written because a ruling forced it.</p>
<ul class="worked">
${worked}
</ul>

<h2>The definitions document, in full</h2>
<p class="docnote">What follows is the working document itself, rendered as written. It carries its own history, including measurement sections describing earlier runs of the calibration harness whose figures were withdrawn in August 2026, when a code inspection found they could not be substantiated. Those sections stand as the record of what was done, not as current evidence; the current figures are the version-bound records named above.</p>`
}

function renderDoc(md, frontCopy) {
  const version = famVersion
  const out = [frontCopy || '', '<hr>', renderMarkdown(md)]
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://symbolicworld.observer/families">
<title>Relation families ${esc(version)} — The Symbolic World</title>
<link rel="stylesheet" href="./chrome.css">
<style>
/* Page-specific only. Palette and chrome come from chrome.css (R10.0). */
* { box-sizing: border-box; }
body { line-height: 1.62; }
main { max-width: 44rem; margin: 0 auto; padding: 2rem 1.5rem 6rem; }
h1 { font-family: var(--display); font-size: 2rem; font-weight: 500; margin-bottom: .4rem; letter-spacing: -.01em; }
h2 { font-size: 1.3rem; font-weight: 500; color: var(--gold); margin: 2.6rem 0 .6rem; font-family: var(--display); }
h3 { font-size: 1.02rem; font-weight: 600; margin: 1.8rem 0 .4rem; font-variant: small-caps; letter-spacing: .06em; }
p, li { margin-bottom: .7rem; font-size: 1rem; }
ul, ol { padding-left: 1.3rem; margin-bottom: .7rem; }
code { font: .86em var(--mono); color: var(--gold); background: rgba(212, 175, 55, .07); padding: .05em .3em; border-radius: 3px; }
.tw { overflow-x: auto; margin: .8rem 0 1.2rem; }
table { border-collapse: collapse; width: 100%; font-size: .88rem; }
th, td { border: 1px solid var(--hairline); padding: .5rem .7rem; text-align: left; vertical-align: top; }
th { color: var(--gold); font-weight: 500; background: var(--panel); }
.gen { font: .68rem var(--mono); color: var(--ink-faint); margin-top: 3rem; border-top: 1px solid var(--hairline); padding-top: .8rem; }
.sub { color: var(--ink-faint); font-size: .95rem; margin-bottom: 1.6rem; }
hr { border: 0; border-top: 1px solid var(--hairline); margin: 3rem 0 2rem; }
.fam { margin: 1.1rem 0; }
.fam h3 { margin: 0 0 .35rem; color: var(--ink); }
.fam h3 em { font-style: normal; font: .7rem var(--mono); color: var(--gold-dim); margin-left: .5rem; letter-spacing: 0; }
.strs { display: flex; flex-wrap: wrap; gap: .3rem .4rem; margin-bottom: .8rem; }
.sstr { display: inline-flex; align-items: baseline; gap: .3rem; border: 1px solid var(--hairline);
  border-radius: 3px; padding: .1rem .35rem; background: var(--panel); }
.sstr code { background: none; padding: 0; font-size: .78rem; }
.sstr i { font: .64rem var(--mono); font-style: normal; color: var(--ink-dim); }
.homeless .sstr { border-color: var(--b-amber); }
.worked li { border-left: 2px solid var(--hairline); padding-left: .8rem; margin-bottom: 1rem; }
.docnote { border-left: 2px solid var(--b-amber); padding-left: .8rem; color: var(--ink-faint); font-size: .92rem; }
</style></head>
<body>
${siteHeader('/families', 'Relation families')}
<main>
${out.join('\n')}
<p class="gen">The exposition above is generated by <code>web/build-atlas.mjs</code>; every count in it is derived from <code>seed.json</code> at build time. The document below it is rendered from <code>docs/FAMILY_DEFINITIONS.md</code> as written \u2014 the atlas quotes that document, it never paraphrases it.</p>
</main></body></html>`
}

// Three emissions, one table. The app imports tokens.css from style.css; the
// generated pages link chrome.css; the Python ledger generator reads tokens.json.
writeFileSync(here('./src/tokens.css'), `/* GENERATED by build-atlas.mjs from TOKENS — do not edit. */\n${rootBlock()}${chromeBlock()}`)
writeFileSync(here('./public/chrome.css'), `/* GENERATED by build-atlas.mjs from TOKENS — do not edit. */\n${rootBlock()}${chromeBlock()}
body { background: var(--ground); color: var(--ink); font-family: var(--serif); margin: 0; }
a { color: var(--gold); }
.page-body { max-width: 900px; margin: 0 auto; padding: 1.4rem clamp(1rem, 4vw, 2.5rem) 4rem; }
`)
writeFileSync(here('./src/tokens.json'), JSON.stringify(TOKENS, null, 1))

// V2-R11 / item 12 — the header as a template, for the app. The in-app routes
// render inside #mode-panel, which covers the topbar, so before this they showed
// a different bar of their own: the menu was not merely unpinned there, it was
// not on screen. main.js now renders THIS fragment, which is the same one the
// generated pages carry, so there is one header in the project rather than one
// per surface. {{BRAND_HREF}} differs because a full page load is wrong inside
// the app; {{ROW2}} is whatever that surface puts on the second row.
writeFileSync(here('./src/chrome.json'), JSON.stringify({
  _about: 'GENERATED by build-atlas.mjs. The site header, as a template. Consumed by web/src/main.js; the same structure the generated pages carry.',
  header: `<header class="site-header">
<div class="hrow hrow-1"><a class="brand" href="{{BRAND_HREF}}" data-back>The Symbolic World</a>${topMenu('')}</div>
<div class="hrow hrow-2">{{ROW2}}</div>
</header>`,
  menu: MENU
}))


// ------------------------------------------------------ #/method · the page ---
// docs/METHOD_COPY.md is authored by the Fable session and wired VERBATIM: this
// build substitutes {{tokens}}, renders the two figures and converts markdown.
// It never edits prose. Bare numbers in the copy are frozen measured results,
// registered in the copy assertion's method-constants allowlist below with the
// sources the document itself records.
const methodPath = here('../docs/METHOD_COPY.md')
let methodHTML = '', methodTokens = {}
if (existsSync(methodPath)) {
  const raw = readFileSync(methodPath, 'utf8')
  const body = raw.slice(raw.indexOf('\n---\n') + 5)   // drop the authoring front-matter

  // {{last_proposed}} / {{last_merged}} are read from the newest merged batch in
  // pipeline/state.json, so the next window updates them without a code change.
  const st = JSON.parse(readFileSync(here('../pipeline/state.json'), 'utf8'))
  const merged = st.batches.filter(b => String(b.status || '').startsWith('merged'))
  const lastBatch = merged[merged.length - 1] || {}
  const res = String(lastBatch.result || '')
  const mProp = res.match(/Mined\s+\d+\s*candidates?\/(\d+)\s*refs/i)
  const mMerg = res.match(/\+(\d+)\s*refs/i)
  if (!mProp || !mMerg) {
    console.error(`METHOD PAGE: cannot derive last_proposed/last_merged from batch ${lastBatch.id}. ` +
      `The copy states them as measured facts, so the build refuses rather than print a stale pair.`)
    process.exit(1)
  }
  const validations = JSON.parse(readFileSync(here('./public/validations.json'), 'utf8')).validations || []

  const xvStamped = atlasEdges.reduce((n, e) => n + e.refs.filter(r => r.crossvendor_checked).length, 0)
  methodTokens = {
    nodes: meta.counts.nodes, edges: meta.counts.edges, refs: meta.counts.references,
    xv_stamped: xvStamped,
    xv_pct: Math.round(100 * xvStamped / meta.counts.references),
    last_proposed: Number(mProp[1]), last_merged: Number(mMerg[1]),
    human_chips: validations.length,
    families: families.length,
    queue: pending.items ? pending.items.length : 0,
    edges_classified: atlasEdges.filter(e => e.family).length
  }

  // the two figures, rendered in the page's own node/relation styling
  const claimEdge = atlasEdges.find(e => e.key === 'lapis|is-projection-of|the-self')
  const claimRef = claimEdge && claimEdge.refs.find(r => String(r.volume) === '9ii' && Number(r.paragraph) === 264)
  if (!claimEdge || !claimRef) {
    console.error('METHOD PAGE: the figure edge lapis|is-projection-of|the-self (CW 9ii §264) is not in the graph — refusing to draw a claim that is not there.')
    process.exit(1)
  }
  const figClaim = `<figure class="fig fig-claim">
    <div class="claim-fig">
      <span class="fig-node" data-type="Symbol">${esc(nodeLabel(claimEdge.source))}</span>
      <span class="fig-rel">${esc(claimEdge.relation)} <i>→</i></span>
      <span class="fig-node" data-type="Concept">${esc(nodeLabel(claimEdge.target))}</span>
      <span class="fig-cite">CW ${esc(claimRef.volume)} §${esc(claimRef.paragraph)}</span>
    </div>
    <figcaption>One claim, drawn. The first clause of the narrative on the landing page rests on exactly this edge.</figcaption>
  </figure>`
  // figure (c) — the metals legend. The six live node kinds in the copy's own
  // order, each swatch painted from the palette token that the DOMAIN table
  // already uses to colour that kind in the atlas. The build refuses if a token
  // has drifted from its DOMAIN colour, so the legend cannot describe a palette
  // the map is not drawing with. (Archetype is omitted: no live nodes, and it
  // reads as Concept.)
  const METALS = [
    ['Concept', 'gold'], ['Symbol', 'silver'], ['Figure', 'copper'],
    ['Operation', 'iron'], ['Substance', 'verdigris'], ['Motif', 'lead']
  ]
  for (const [kind] of METALS) {
    const token = TOKENS[`m-${kind.toLowerCase()}`]
    if (!DOMAIN[kind] || DOMAIN[kind].color !== token) {
      console.error(`METHOD PAGE: metals legend — --m-${kind.toLowerCase()} (${token}) is not the DOMAIN colour for ${kind} (${DOMAIN[kind] && DOMAIN[kind].color}). ` +
        `The legend may not name a colour the atlas does not use.`)
      process.exit(1)
    }
  }
  const figMetals = `<figure class="fig">
    <ul class="metals-fig">${METALS.map(([kind, metal]) =>
      `<li><i class="metal-dot" style="background:var(--m-${kind.toLowerCase()})"></i>` +
      `<span class="metal-kind">${esc(kind)}</span><span class="metal-name">${esc(metal)}</span></li>`).join('')}</ul>
    <figcaption>The metals legend: six node kinds, six metals.</figcaption>
  </figure>`

  const maxV = Math.max(...volumes.map(v => v.references))
  const figWorks = `<figure class="fig">
    <div class="works-fig">${volumes.map(v => `<span class="work-fig" style="flex:${v.references} 1 0;opacity:${(0.3 + 0.7 * v.references / maxV).toFixed(2)}"><span>CW ${esc(v.volume)}</span></span>`).join('')}</div>
    <figcaption>The works bar, as it appears at the bottom of the atlas: one segment per volume, sized by the verified evidence resting on it.</figcaption>
  </figure>`

  const cit = JSON.parse(readFileSync(here('../.zenodo.json'), 'utf8'))
  const figCite = `<div class="cite-block">
    <div class="cite-title">${esc(cit.title)}</div>
    <div class="cite-meta">${esc((cit.creators || []).map(c => c.name).join('; '))}</div>
    <div class="cite-doi">DOI <a href="https://doi.org/10.5281/zenodo.21631523">10.5281/zenodo.21631523</a> · concept DOI, resolves to the latest release</div>
  </div>`

  let md = body
  for (const [k, v] of Object.entries(methodTokens)) md = md.split(`{{${k}}}`).join(String(v))
  md = md.replace(/\[figure: one claim, drawn[\s\S]*?\]\n/, '@@FIG_CLAIM@@\n')
         .replace(/\[figure: the works bar[\s\S]*?\]\n/, '@@FIG_WORKS@@\n')
         .replace(/\[figure: the metals legend[\s\S]*?\]\n/, '@@FIG_METALS@@\n')
         .replace(/\[citation block[\s\S]*?\]\n?/, '@@FIG_CITE@@\n')
  const leftover = md.match(/\{\{(\w+)\}\}/)
  if (leftover) { console.error(`METHOD PAGE: unbound token {{${leftover[1]}}} in the copy`); process.exit(1) }
  methodHTML = renderMarkdown(md)
    .replace('<p>@@FIG_CLAIM@@</p>', figClaim)
    .replace('<p>@@FIG_WORKS@@</p>', figWorks)
    .replace('<p>@@FIG_METALS@@</p>', figMetals)
    .replace('<p>@@FIG_CITE@@</p>', figCite)
  // An unrendered [figure: …] bracket means the copy grew a figure the build does
  // not draw. It would ship as literal square-bracket prose, so fail instead.
  const unrendered = methodHTML.match(/\[figure:[^\]]*\]|@@FIG_\w+@@/)
  if (unrendered) {
    console.error(`METHOD PAGE: the copy carries a figure the build does not render — ${unrendered[0].slice(0, 80)}`)
    process.exit(1)
  }
  writeFileSync(here('./src/method.json'), JSON.stringify({ html: methodHTML, tokens: methodTokens, source: 'docs/METHOD_COPY.md' }))
  console.log(`method page: wired — ${Object.entries(methodTokens).map(([k, v]) => k + '=' + v).join(' · ')}`)
}
function nodeLabel(id) { const n = atlasNodes.find(x => x.id === id); return n ? n.label : id }

// ===========================================================================
// V2 — the v2.0 UI slice (docs/ATLAS_REQUIREMENTS.md, V2-R1..R6)
//
// Four generated surfaces join the site: release notes, one page per relation
// family, a query panel over the kg_query semantics, and an ontology page
// carrying the QA scan. They are built here rather than hand-written for the
// same reason the families page is: every number on them has to come from the
// graph, the committed receipts or a tool's own output, and a page whose
// figures are typed goes stale the next time a window merges.
//
// Three rules bind every page below, and the build enforces each of them:
//   · the canonical URL is extensionless (CLAUDE.md, 2026-08-10), so a page
//     registers a slug and the file name is derived from it, never the reverse;
//   · registration also writes the sitemap entry and the footer nav, so a page
//     cannot ship unreachable or unlisted;
//   · the page's prose joins the copy contract at the foot of this file.
// ===========================================================================
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readdirSync } from 'node:fs'

const repoDir = new URL('../', import.meta.url).pathname
const seedDigest = createHash('sha256').update(readFileSync(here('../seed.json'))).digest('hex')
const buildDate = new Date().toISOString().slice(0, 10)
const gitCommit = (() => {
  try { return execFileSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: repoDir, encoding: 'utf8' }).trim() }
  catch { return '' }
})()

// Pages already on the site, described here so the sitemap and the footer nav
// can be generated whole rather than maintained in two places.
const SITE_PAGES = [
  { slug: '', title: 'The atlas', nav: 'the atlas', changefreq: 'daily', priority: '1.0' },
  { slug: 'ledger', title: 'Ledger', nav: 'ledger', changefreq: 'daily', priority: '0.8' },
  { slug: 'families', title: 'Relation families', nav: 'families', changefreq: 'weekly', priority: '0.6' },
  { slug: 'disputes', title: 'Dispute log', nav: 'disputes', changefreq: 'weekly', priority: '0.5' },
  { slug: 'graph.json', title: 'The dataset', nav: null, changefreq: 'daily', priority: '0.7' },
  { slug: 'v1.3/', title: 'The frozen v1.3.0 snapshot', nav: null, changefreq: 'yearly', priority: '0.3' }
]
const NEW_PAGES = []          // { slug, title, where, style, body, nav, changefreq, priority }
const V2_COPY = []            // [name, prose] pairs for the copy contract
// Every figure these pages interpolate, collected as it is computed and handed
// to the copy contract. The check keeps its teeth: a literal that none of these
// derivations produced still fails the build.
const V2_NUMBERS = []
const derived = (...ns) => { for (const n of ns) if (Number.isFinite(Number(n))) V2_NUMBERS.push(Number(n)); return ns[0] }

// Evidence — quotes, relation strings, node labels, citations — is the graph's
// own record and is not copy. It is marked with class="ev" where it lands in a
// generated page and stripped before the copy scan, on the same reasoning the
// scan already applies to atlas.json: rewriting the record to suit a style rule
// would falsify it.
const stripEvidence = (html) => html
  .replace(/<(\w+)[^>]*class="[^"]*\bev\b[^"]*"[^>]*>[\s\S]*?<\/\1>/g, ' ')

// V2-R7 — the batch delta pages are written by tools/build_ledger_page.py, from
// the same pass over the same data that writes the ledger. They are registered
// here so the sitemap is generated whole: one list of the site's URLs, whichever
// generator produced the page behind each one. The slug rule is the ledger
// generator's, restated in one line rather than imported across languages, and
// the test that matches sitemap entries against files on disk is what keeps the
// two honest.
const batchSlug = (id) => 'batch-' + String(id).toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '')

function registerExternalPage(p) {
  SITE_PAGES.push({ slug: p.slug, title: p.title, nav: null, changefreq: p.changefreq || 'monthly', priority: p.priority || '0.3' })
}

function registerPage(p) {
  NEW_PAGES.push(p)
  SITE_PAGES.push({ slug: p.slug, title: p.title, nav: p.nav || null, changefreq: p.changefreq || 'weekly', priority: p.priority || '0.5' })
  return p
}

// The shared shell: page-bar in the fixed position R10.6 wants, chrome.css for
// the palette, an extensionless canonical, and the footer nav.
const V2_STYLE = `
* { box-sizing: border-box; margin: 0; padding: 0; }
body { min-height: 100vh; }
main { max-width: 940px; margin: 0 auto; padding: 1.6rem clamp(1rem, 4vw, 2rem) 5rem; }
h1 { font-family: var(--display); font-size: 2rem; font-weight: 500; letter-spacing: -.01em; margin: .3rem 0 .6rem; }
h2 { font-family: var(--display); font-size: 1.35rem; font-weight: 500; color: var(--gold); margin: 2.2rem 0 .5rem; }
h3 { font-family: var(--display); font-size: 1.1rem; font-weight: 500; margin: 1.4rem 0 .35rem; }
h4 { font: .6rem var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--gold-dim); margin: 1.3rem 0 .45rem; }
p { font-size: .92rem; line-height: 1.62; max-width: 68ch; }
p + p { margin-top: .6rem; }
a { color: var(--gold); }
code { font: .86em var(--mono); color: var(--gold); background: rgba(212,175,55,.07); padding: .05em .3em; border-radius: 3px; }
.eyebrow { font: .6rem/1 var(--mono); letter-spacing: .26em; text-transform: uppercase; color: var(--gold-dim); }
.dim { color: var(--ink-faint); }
.meta { font: .62rem/1.7 var(--mono); color: var(--ink-faint); }
.chip { font: .56rem var(--mono); letter-spacing: .03em; padding: .12rem .46rem; border-radius: 99px;
        border: 1px solid var(--hairline); white-space: nowrap; color: var(--ink-faint); display: inline-block; }
.f-ok { color: var(--m-substance); border-color: var(--b-ok); }
.f-pend { color: var(--amber); border-color: var(--b-amber); }
.f-none { color: var(--ink-dim); border-style: dashed; }
.receipts { margin-top: 1.1rem; border: 1px solid var(--hairline); border-left: 3px solid var(--gold-dim);
  border-radius: 0 8px 8px 0; background: rgba(11,10,8,.6); padding: .7rem .85rem;
  font: .62rem/1.75 var(--mono); color: var(--ink-faint); overflow-x: auto; }
.receipts b { color: var(--gold-dim); font-weight: 400; letter-spacing: .12em;
  text-transform: uppercase; font-size: .55rem; display: block; margin-bottom: .3rem; }
.receipts .hash { color: var(--ink-label); }
.callout { border: 1px solid var(--hairline); border-left: 3px solid var(--m-symbol); border-radius: 0 8px 8px 0;
  padding: .7rem .9rem; background: rgba(194,205,214,.045); margin-top: 1rem; }
.callout p { font-size: .85rem; color: var(--ink-label); max-width: 72ch; }
.tw { overflow-x: auto; margin: .6rem 0 1rem; }
table { border-collapse: collapse; width: 100%; font-size: .86rem; }
th, td { border-bottom: 1px solid var(--hairline); padding: .38rem .5rem; text-align: left; vertical-align: top; }
th { font: .55rem var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--ink-dim); }
td.n { font-family: var(--mono); font-size: .78rem; }
/* V2-R9 — progressive disclosure. Native details/summary: no script, and the
   page still works with the fold closed. */
.disclose { border: 1px solid var(--hairline); border-radius: 8px; padding: .55rem .8rem; margin: .6rem 0 .8rem; background: var(--surface); }
.disclose > summary { cursor: pointer; font-size: .88rem; line-height: 1.6; color: var(--ink-label); list-style: none; }
.disclose > summary::-webkit-details-marker { display: none; }
.disclose > summary::before { content: "\\25b8"; color: var(--gold-dim); margin-right: .5rem; display: inline-block; }
.disclose[open] > summary::before { transform: rotate(90deg); }
.disclose > summary .more { display: block; font: .58rem var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--gold-dim); margin-top: .25rem; }
.disclose[open] > summary { margin-bottom: .5rem; }
.sitenav { margin-top: 3.2rem; border-top: 1px solid var(--hairline); padding-top: 1rem;
  display: flex; flex-wrap: wrap; gap: .3rem .9rem; font: .62rem var(--mono); }
.sitenav a { color: var(--ink-faint); text-decoration: none; }
.sitenav a:hover { color: var(--gold); }
`

function siteNav(current) {
  return `<nav class="sitenav">` + SITE_PAGES.filter(p => p.nav)
    .map(p => p.slug === current
      ? `<span class="dim">${esc(p.nav)}</span>`
      : `<a href="/${p.slug}">${esc(p.nav)}</a>`).join('\n') + `</nav>`
}

function renderPage(p) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://symbolicworld.observer/${p.slug}">
<title>${esc(p.title)} — The Symbolic World</title>
<link rel="stylesheet" href="/chrome.css">
<style>${V2_STYLE}${p.style || ''}</style>
${p.head || ''}</head>
<body>
${siteHeader('/' + p.slug, p.where)}
<main>
${p.body}
${siteNav(p.slug)}
</main></body></html>`
}

// --------------------------------------------------- V2-R1 · /releases -----
// The page is assembled from docs/RELEASES.md. The prose is that file's; the
// figures are tokens bound here, so an entry cannot state a count the graph and
// the receipts do not currently produce, and an unbound token fails the build
// rather than shipping as literal braces.
const calibRecords = []
const calibDir = here('../pipeline/family_calibration/records')
try {
  for (const f of readdirSync(calibDir)) {
    if (!f.endsWith('.json')) continue
    const rec = JSON.parse(readFileSync(new URL(`../pipeline/family_calibration/records/${f}`, import.meta.url), 'utf8'))
    calibRecords.push({ file: `pipeline/family_calibration/records/${f}`, ...rec })
  }
} catch { /* no records directory — handled below */ }
const bindingCalib = calibRecords
  .filter(r => r.definitions_version === famVersion && r.verdict === 'PASS')
  .sort((a, b) => String(a.planted_at || a.file).localeCompare(String(b.planted_at || b.file)))
  .pop()

const declPath = here('../pipeline/family/relation_declarations.json')
const DECL = existsSync(declPath) ? JSON.parse(readFileSync(declPath, 'utf8')) : null
const activeDecls = DECL ? DECL.active.filter(d => !d.dormant) : []

const releasesPath = here('../docs/RELEASES.md')
if (existsSync(releasesPath)) {
  if (!bindingCalib) {
    console.error(`RELEASES PAGE: no calibration record with verdict PASS for ruleset ${famVersion || '(none)'} under ` +
      `pipeline/family_calibration/records/. The version pin names that record, so the build refuses rather than print a pin it cannot evidence.`)
    process.exit(1)
  }
  const state = JSON.parse(readFileSync(here('../pipeline/state.json'), 'utf8'))
  const mergedBatches = state.batches.filter(b => String(b.status || '').startsWith('merged')).length
  const relTokens = {
    ruleset: famVersion,
    calibration_record: bindingCalib.file,
    nodes: meta.counts.nodes, edges: meta.counts.edges, refs: meta.counts.references,
    batches: mergedBatches, normalized: meta.normalized,
    assigned: famMap.totals.assigned, pending: famMap.totals.pending,
    no_family: famMap.totals.no_family, text_undecided: famMap.totals.text_undecided,
    // the DOCUMENT's family count, not the map's: the map counts families that
    // currently hold an assigned edge, and a family holding none is still in
    // the ruleset (amplification, after ruling 1's re-run, is exactly that)
    families: families.length, declarations_active: activeDecls.length,
    cal_caught: bindingCalib.sensitivity.caught, cal_planted: bindingCalib.sensitivity.of,
    cal_clean: bindingCalib.specificity.clean_left_alone, cal_clean_of: bindingCalib.specificity.of,
    gate_model: bindingCalib.gate_model,
    ev_passes: EV ? EV.passes : '', ev_works: EV ? EV.works_consulted : '',
    ev_treated: EV ? EV.treated : '', ev_agrees: EV ? EV.agrees : '',
    ev_disagrees: EV ? EV.disagrees : '', ev_split: EV ? EV.scholars_split : '',
    ev_not_treated: EV ? EV.not_treated : '', ev_rulings: EV ? EV.rulings_produced : '',
    // the same rule tools/ontology_qa/quality.py applies for its P24 check: a
    // predicate of four or more hyphen tokens is carrying a proposition
    clause_edges: seed.edges.filter(e => (e.relation.match(/-/g) || []).length >= 4).length
  }
  derived(...Object.values(relTokens))
  let relMd = readFileSync(releasesPath, 'utf8')
  for (const [k, v] of Object.entries(relTokens)) relMd = relMd.split(`{{${k}}}`).join(String(v))
  const relLeft = relMd.match(/\{\{(\w+)\}\}/)
  if (relLeft) { console.error(`RELEASES PAGE: unbound token {{${relLeft[1]}}} in docs/RELEASES.md`); process.exit(1) }

  // one entry per "## " heading; `status:` and `pin:` are the two labelled
  // lines an entry opens with, and everything after a "### " is a section
  const [preamble, ...rawEntries] = relMd.split(/\n(?=## )/)
  const entries = rawEntries.map(chunk => {
    const lines = chunk.split('\n')
    const heading = lines[0].replace(/^##\s+/, '')
    const status = (chunk.match(/^status:\s*([\s\S]*?)(?=\n(?:pin:|###|$))/m) || [, ''])[1].trim().replace(/\s*\n\s*/g, ' ')
    const pin = (chunk.match(/^pin:\s*(.*)$/m) || [, ''])[1].trim()
    const sections = chunk.split(/\n(?=### )/).slice(1).map(s => ({
      title: s.split('\n')[0].replace(/^###\s+/, ''),
      body: renderMarkdown(s.slice(s.indexOf('\n') + 1))
    }))
    return { heading, status, pin, sections, future: /^skeleton/i.test(status) }
  })
  // Newest first, from the version in each heading rather than from the order
  // the file happens to be written in. An entry whose heading carries no
  // version keeps its position at the end rather than sorting as zero.
  const versionOf = (h) => {
    const m = h.match(/v(\d+)\.(\d+)(?:\.(\d+))?/)
    return m ? [Number(m[1]), Number(m[2]), Number(m[3] || 0)] : null
  }
  entries.sort((a, b) => {
    const va = versionOf(a.heading), vb = versionOf(b.heading)
    if (!va && !vb) return 0
    if (!va) return 1
    if (!vb) return -1
    return (vb[0] - va[0]) || (vb[1] - va[1]) || (vb[2] - va[2])
  })
  // V2-R7 — a batch named in a release entry links to its delta page. The link
  // is made from pipeline/state.json's own ids, in text nodes only, so a batch
  // that does not exist is left as plain text rather than linked into a 404.
  const batchIds = new Set(state.batches.map(b => b.id))
  const idPattern = /\b(b-[a-z0-9]+(?:-[a-z0-9]+)*|cw\d+_candidates\d+)\b/g
  const linkBatches = (html) => html.replace(/>([^<]+)</g, (whole, text) =>
    '>' + text.replace(idPattern, (id) =>
      batchIds.has(id) ? `<a href="/${batchSlug(id)}">${id}</a>` : id) + '<')

  const pinHtml = (pin) => `<div class="pin">` + inline(pin)
    .replace(/(graph|ruleset)\s+(v[\d.]+|pending)/g, '$1 <span class="v">$2</span>') + `</div>`
  const relBody = `<p class="eyebrow">release notes</p>
<h1>Releases</h1>
${renderMarkdown(preamble.split('\n').slice(1).join('\n'))}
${entries.map(e => `<section class="rel-entry${e.future ? ' future' : ''}">
<h2>${inline(e.heading)}</h2>
<div class="meta">${inline(e.status)}</div>
${pinHtml(e.pin)}
${e.sections.map(s => `<h4>${inline(s.title)}</h4>\n${linkBatches(s.body)}`).join('\n')}
</section>`).join('\n')}
<div class="receipts"><b>receipts</b>
prose from <code>docs/RELEASES.md</code>; counts read from seed.json <span class="hash">sha256:${seedDigest.slice(0, 12)}</span>;<br>
ruleset ${esc(famVersion)} with calibration record <code>${esc(bindingCalib.file)}</code> (${esc(bindingCalib.verdict)});<br>
external-validity figures from <code>docs/experiments/external_validity_2026-08/results.json</code>; built ${buildDate}
</div>`
  const relStyle = `
.rel-entry { border: 1px solid var(--hairline); border-radius: 10px; padding: 1rem 1.1rem; margin: 1rem 0; background: var(--surface); }
.rel-entry.future { opacity: .6; border-style: dashed; }
.rel-entry h2 { margin-top: 0; }
.pin { font: .62rem/1.7 var(--mono); color: var(--ink-label); border-left: 3px solid var(--gold-dim);
  padding: .4rem .7rem; background: rgba(212,175,55,.05); border-radius: 0 6px 6px 0; margin: .5rem 0 .8rem; overflow-x: auto; }
.pin .v { color: var(--gold); }
.rel-entry ul { list-style: none; margin: .3rem 0 .2rem; }
.rel-entry li { font-size: .89rem; line-height: 1.6; padding: .16rem 0 .16rem .95rem; position: relative; max-width: 68ch; }
.rel-entry li::before { content: "\\00b7"; position: absolute; left: .2rem; color: var(--edge-idle); }
`
  registerPage({
    slug: 'releases', title: 'Releases', where: 'releases', nav: 'releases',
    changefreq: 'monthly', priority: '0.5', style: relStyle, body: relBody
  })
  V2_COPY.push(['public/releases.html (generated from docs/RELEASES.md)', stripEvidence(relBody)])
  console.log(`releases: ${entries.length} entries — pin ruleset ${famVersion}, record ${bindingCalib.file} (${bindingCalib.verdict})`)
}

// ------------------------------------------- V2-R2 · /family-<name> -------
// One page per family in the ruleset — including a family that currently holds
// no edge, which is reported at zero rather than dropped. The definition is
// quoted from docs/FAMILY_DEFINITIONS.md through the same extraction the
// families page uses; nothing here paraphrases it. Counts come from the derived
// map, pending items from the graph, and the external-validity row from the
// committed receipts, so no figure on these pages is typed.
const effRel = (e) => (e.relation_normalized && e.relation_normalized.relation) || e.relation
const famRows = new Map(famMap.families.map(f => [f.family, f]))
const pendingRows = atlasEdges
  .filter(e => e.family && e.family.state === 'pending')
  .map(e => ({
    subject: nodeLabel(e.source), object: nodeLabel(e.target),
    rel: e.relation, eff: effRel(e),
    by: (e.family.assigned_by || '').trim(), reason: (e.family.reason_text || '').trim(),
    cite: e.refs.length ? `CW ${e.refs[0].volume} §${e.refs[0].paragraph}` : '',
    quote: e.refs.length ? (e.refs[0].quote || '') : ''
  }))

const EVROWS = (EV && EV.per_family && EV.per_family.rows) || []
const evTable = (currentFamily) => {
  if (!EVROWS.length) return ''
  const rows = EVROWS.map(r => `<tr class="${r.total ? 'total' : ''}${r.family === currentFamily ? ' this' : ''}">` +
    `<td>${esc(r.label)}</td><td class="n">${esc(r.agrees)}</td><td class="n">${esc(r.disagrees)}</td>` +
    `<td class="n">${esc(r.split)}</td><td class="n">${esc(r.not_treated)}</td></tr>`).join('\n')
  return `<div class="tw"><table>
<thead><tr><th>family</th><th>agrees</th><th>disagrees</th><th>split</th><th>not treated</th></tr></thead>
<tbody>${rows}</tbody></table></div>`
}

const famPages = []
for (const fam of families) {
  const row = famRows.get(fam.id) || { edges: 0, strings: [] }
  const strings = row.strings
  const stringSet = new Set(strings.map(s => s.string))
  const singles = strings.filter(s => s.edges === 1).length
  const pend = pendingRows.filter(p => stringSet.has(p.eff))
  const decls = activeDecls.filter(d => d.kind === 'inverse'
    ? (stringSet.has(d.forward) || stringSet.has(d.inverse))
    : stringSet.has(d.relation))
  const evRow = EVROWS.find(r => r.family === fam.id)
  derived(row.edges, strings.length, singles, pend.length, decls.length,
    ...strings.map(s => s.edges))

  const lead = strings.slice(0, 12)
  const tail = strings.slice(12)
  const stringChips = lead.map(s =>
    `<span class="chip ev${s.edges >= 5 ? ' lead' : ''}"><code>${esc(s.string)}</code> <span class="n">${s.edges}</span></span>`).join('')
    + (tail.length ? `<span class="chip f-none">and ${tail.length} more, ${tail.reduce((a, s) => a + s.edges, 0)} relations between them</span>` : '')

  const seedList = fam.seeds.length ? `<ul class="seeds">${fam.seeds.map(s =>
    `<li class="ev">${esc(s.text)}${s.cite ? ` <span class="cite">${esc(s.cite)}</span>` : ''}</li>`).join('')}</ul>`
    : `<p class="dim">The definition names no worked example, so none is shown. Inventing one here would put a claim on the page that the document does not make.</p>`

  const declBlock = decls.length ? `<h4>declared pairs</h4>
<ul class="seeds">${decls.map(d => `<li><span class="ev"><code>${esc(d.kind === 'inverse' ? `${d.forward} / ${d.inverse}` : d.relation)}</code></span> — ${esc(d.kind)}${d.applies_to_family ? `, restricted to the ${esc(d.applies_to_family)} family` : ''}, transcribed from <span class="ev">${esc(d.source[0].section)} (line ${d.source[0].line})</span></li>`).join('')}</ul>
<p class="meta">A declaration licenses a row in the other direction when the query panel's closure toggle is on, and nothing else. It is read at query time and never written into the graph.</p>` : ''

  const pendBlock = pend.length ? `<h4>pending a ruling — items carrying a string this family covers</h4>
<div class="queue">${pend.slice(0, 6).map(p => `<div class="qitem">
<div class="triple ev">${esc(p.subject)} <span class="rel">${esc(p.rel)}</span> ${esc(p.object)} <span class="cite">${esc(p.cite)}</span></div>
<div class="why ev">${esc(p.by)}${p.reason ? ` — ${esc(p.reason)}` : ''}</div>
</div>`).join('')}
${pend.length > 6 ? `<p class="meta">${pend.length - 6} more. These are edges whose two model arms did not agree, or whose agreement the calibrated gate disputed. They carry a relation string this family covers, which is not the same as belonging here — the ruling has not been made, and the queue is not a backlog to be cleared by machine.</p>`
    : `<p class="meta">These are edges whose two model arms did not agree, or whose agreement the calibrated gate disputed. Carrying a string this family covers is not the same as belonging here; the ruling has not been made.</p>`}
</div>` : `<h4>pending a ruling</h4>
<p class="dim">No queued item carries a relation string this family covers.</p>`

  // V2-R9 — headline in a line, the table behind a native <details>. The limit
  // stays outside the fold: a reader who never expands still reads what the
  // check does not show.
  const evHeadline = evRow
    ? `Checked against ${EV.works_consulted} works of scholarship: across the sample, ${EV.agrees} of ${EV.treated} treated items agreed with our family. This family: ${esc(evRow.agrees)} agreed, ${esc(evRow.disagrees)} disagreed, ${esc(evRow.split)} split, ${evRow.not_treated} not treated.`
    : `Checked against ${EV.works_consulted} works of scholarship: across the sample, ${EV.agrees} of ${EV.treated} treated items agreed with our family. The sample did not reach this family.`
  const evBlock = EVROWS.length ? `<h2>Checked against readers of Jung</h2>
<details class="disclose">
<summary>${evHeadline}<span class="more">the whole table</span></summary>
${evTable(fam.id)}
<p class="meta">Rows of three treated items are three items, and no rate over three items carries precision worth reporting. The check asked which kind of relation a reader of the literature would say Jung asserts — not whether Jung's claim is true, which the verification chain had already asked of the paragraph. The disagreements stand beside the agreements because hiding them would make the table an argument rather than a record. Full worksheets: <code>docs/experiments/external_validity_2026-08/</code>.</p>
</details>
<p class="meta">Agreement is not endorsement: no scholar reviewed this vocabulary, and the sample is small enough to name in a sentence.</p>` : ''

  const zeroNote = row.edges === 0 ? `<p>No edge in the graph currently carries this family. A family with no members stays in the ruleset and is reported at zero rather than dropped: dropping it would hide the reclassification that emptied it, and the empty count is a finding about the definition.</p>` : ''

  const body = `<p class="eyebrow">relation family</p>
<h1><span class="ev">${esc(fam.name)}</span> <span class="chip f-ok">assigned, not verified</span></h1>
<p class="sub dim">What this family covers, what it fails to cover, and every relation string in the graph that lands in it. A family is <em>assigned</em>: two models read the definitions document and named the same kind of relation, or a person ruled where they did not. <em>Verified</em> is the other layer — a quote checked letter-exact against its paragraph and judged by a model of a different family — and it was already done before any of this began.</p>
<div class="countstrip">
  <span><b>${row.edges}</b> assigned relations</span>
  <span><b>${strings.length}</b> effective relation strings</span>
  <span><b>${pend.length}</b> queued items carry a string this family covers</span>
  <span><b>${decls.length}</b> declared ${decls.length === 1 ? 'pair' : 'pairs'}</span>
</div>
<div class="countstrip dim">
  <span>graph-wide: ${famMap.totals.assigned} assigned · ${famMap.totals.pending} awaiting a ruling · ${famMap.totals.no_family} no family · ${famMap.totals.text_undecided} text undecided · ${famMap.totals.edges} relations</span>
</div>
${zeroNote}

<h2>Definition</h2>
<p class="meta">Quoted from <code>docs/FAMILY_DEFINITIONS.md</code> ${esc(famVersion)}, family ${fam.n}${fam.added ? `, ${esc(fam.added)}` : ''}. The atlas quotes that document; it never paraphrases it.</p>
<blockquote class="quotebox ev">${fam.definition_html}</blockquote>
${fam.boundary_html ? `<p class="dim ev"><b>Boundary.</b> ${fam.boundary_html}</p>` : ''}
${fam.notes.length ? fam.notes.map(n => `<p class="dim ev"><b>${esc(n.label)}.</b> ${n.html}</p>`).join('\n') : ''}

<h2>Relation strings that land here</h2>
${strings.length ? `<div class="stringmap">${stringChips}</div>
<p class="meta">The number beside a string is how many relations carry it. ${singles ? `${singles} of these strings ${singles === 1 ? 'occurs' : 'occur'} exactly once` : 'No string here occurs only once'} — the tail is the informative part, because a string used once usually carried its own qualifier in the sentence it came from. A string can appear under more than one family, and does: assignment is made to an edge in its paragraph, never to a string in the abstract.</p>`
    : `<p class="dim">No relation string lands here.</p>`}

<h4>seeds — the examples the definition names</h4>
${seedList}
${declBlock}
${pendBlock}
${evBlock}

<div class="receipts"><b>receipts</b>
counts read from seed.json <span class="hash">sha256:${seedDigest.slice(0, 12)}</span> via web/family-map.mjs;<br>
definition and seeds quoted from docs/FAMILY_DEFINITIONS.md ${esc(famVersion)};<br>
${EVROWS.length ? `external-validity row from docs/experiments/external_validity_2026-08/results.json (report v3, closed 2026-08-12);<br>` : ''}
built ${buildDate}
</div>
<div class="callout"><p>These families are this project's classification. They are calibrated inside this repository, checked once against outside scholarship on a small sample, and endorsed by nobody. What the layer records is how we sorted relations Jung wrote — a map of assertions, not a reading of him.</p></div>`

  const p = registerPage({
    slug: `family-${fam.id}`, title: `${fam.name} — a relation family`,
    where: `families · ${fam.name}`, nav: null, changefreq: 'weekly', priority: '0.4',
    style: '', body
  })
  famPages.push({ page: p, fam, edges: row.edges })
  V2_COPY.push([`public/family-${fam.id}.html (generated)`, stripEvidence(body)])
}
// The per-family pages must account for every assigned relation exactly once:
// the pages are the map, page by page, and a page that quietly dropped or
// double-counted a family would be a different claim about the layer.
const famPageTotal = famPages.reduce((a, f) => a + f.edges, 0)
if (famPageTotal !== famMap.totals.assigned) {
  console.error(`FAMILY PAGES: the per-family counts sum to ${famPageTotal}, the map's assigned total is ${famMap.totals.assigned}. ` +
    `A family in the graph has no page, or a page counts twice.`)
  process.exit(1)
}
const styleFamily = `
.sub { font-size: .92rem; margin-bottom: 1rem; }
.countstrip { display: flex; flex-wrap: wrap; gap: .5rem .9rem; margin: .7rem 0 .2rem; font: .62rem var(--mono); color: var(--ink-faint); }
.countstrip b { color: var(--ink); font-weight: 400; }
.quotebox { border-left: 2px solid var(--hairline); padding: .2rem 0 .2rem .9rem; margin: .5rem 0 .7rem; font-size: .95rem; line-height: 1.6; max-width: 68ch; }
.stringmap { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .5rem; }
.stringmap .chip code { background: none; padding: 0; font-size: .78rem; color: inherit; }
.stringmap .chip .n { color: var(--ink-dim); }
.stringmap .chip.lead { color: var(--gold); border-color: var(--b-amber); }
.seeds { list-style: none; margin-top: .5rem; }
.seeds li { padding: .22rem 0; font-size: .9rem; max-width: 68ch; }
.seeds .cite { font: .6rem var(--mono); color: var(--gold-dim); margin-left: .35rem; }
.queue { margin-top: .5rem; }
.qitem { border-left: 3px solid var(--b-amber); background: rgba(217,168,79,.05); border-radius: 0 6px 6px 0; padding: .45rem .7rem; margin: .4rem 0; }
.qitem .triple { font-size: .92rem; }
.qitem .rel { color: var(--gold); font-style: italic; }
.qitem .cite { font: .6rem var(--mono); color: var(--gold-dim); }
.qitem .why { font: .6rem/1.6 var(--mono); color: var(--ink-faint); margin-top: .2rem; }
tr.this td { color: var(--ink); background: rgba(212,175,55,.05); }
tr.total td { color: var(--ink-faint); }
`
for (const f of famPages) f.page.style = styleFamily
console.log(`family pages: ${famPages.length} written, ${famPageTotal} assigned relations accounted for ` +
  `(${famPages.filter(f => !f.edges).length} family with no assigned edge)`)

// ------------------------------------------------- V2-R4 · /query ---------
// The query panel runs the kg_query semantics in the browser: web/query-semantics.mjs
// is copied verbatim to public/query.js, the declarations travel with it, and the
// page reads the published dataset at /graph.json. Nothing is recomputed here that
// the CLI computes differently — the CLI stays the reference implementation, and
// tests/test_site_generators.py compares the two on real filters.
if (DECL) {
  const declOut = JSON.stringify({
    _emitted_by: 'web/build-atlas.mjs from pipeline/family/relation_declarations.json',
    ...DECL
  })
  writeFileSync(here('./src/relation_declarations.json'), declOut)
  writeFileSync(here('./public/relation_declarations.json'), declOut)

  const semantics = readFileSync(here('./query-semantics.mjs'), 'utf8')
  writeFileSync(here('./public/query.js'), semantics)

  // The walk's header is not restated here: it is lifted out of kg_query.py, so
  // the page cannot promise a limit the tool has stopped honouring.
  const cliSrc = readFileSync(here('../tools/query/kg_query.py'), 'utf8')
  const headerMatch = cliSrc.match(/WALK_HEADER = \(\n([\s\S]*?)\n\)/)
  const identityMatch = cliSrc.match(/IDENTITY_FAMILY = "([^"]+)"/)
  if (!headerMatch || !identityMatch) {
    console.error('QUERY PAGE: cannot lift WALK_HEADER / IDENTITY_FAMILY out of tools/query/kg_query.py. ' +
      'The page states the walk\'s limits in the tool\'s own words, so the build refuses to invent them.')
    process.exit(1)
  }
  const walkHeader = (headerMatch[1].match(/"([^"]*)"/g) || [])
    .map(s => s.slice(1, -1)).join('').replace(/\\n/g, ' ').replace(/\s+/g, ' ')
    .replace('{family}', identityMatch[1]).trim()

  // the CLI's receipts footer, in the CLI's own format
  const tally = {}
  for (const e of seed.edges) {
    const st = (e.relation_family || {}).state || 'unrecorded'
    tally[st] = (tally[st] || 0) + 1
  }
  const order = ['assigned', 'pending-adjudication', 'no-family', 'text-undecided']
  const tallyParts = order.filter(k => k in tally).map(k => `${tally[k]} ${k}`)
    .concat(Object.keys(tally).sort().filter(k => !order.includes(k)).map(k => `${tally[k]} ${k}`))
  const receiptsFooter = `graph state: ${seed.nodes.length} nodes / ${seed.edges.length} edges; ` +
    `families ${tallyParts.join(', ')}; seed.json sha256:${seedDigest.slice(0, 12)}; ` +
    `declarations relation_declarations.json from FAMILY_DEFINITIONS ` +
    `${(DECL.transcribed_from || {}).document_version || '?'}, ${activeDecls.length} active`
  derived(seed.nodes.length, seed.edges.length, ...Object.values(tally), activeDecls.length)

  const queryBody = `<p class="eyebrow">read-only</p>
<h1>Query the graph</h1>
<p>The filters <code>tools/query/kg_query.py</code> takes, given a surface. They combine with AND, exactly as the tool combines them, and each one reads a field the graph already stores rather than computing a judgement of its own. The closure toggle adds the rows the active declarations license and marks every one of them as derived.</p>
<p>Nothing on this page writes anything. The panel reads the published dataset at <a href="/graph.json">/graph.json</a> and the declarations beside it; the same query on the command line prints the same rows with a footer naming the graph it ran against. Two results carrying different seed digests are not comparable, which is why the digest sits under the results rather than in a help page.</p>

<div class="filters" id="filters">
  <div class="fld"><label for="f-family">family</label><select id="f-family"></select><span class="hint" id="h-family"></span></div>
  <div class="fld"><label for="f-state">state</label><select id="f-state"></select><span class="hint">assigned, or one of the three ways an edge carries no family</span></div>
  <div class="fld"><label for="f-subject">subject</label><input id="f-subject" placeholder="any"><span class="hint">node id, else substring of an id or a label</span></div>
  <div class="fld"><label for="f-object">object</label><input id="f-object" placeholder="any"><span class="hint">same matching rule as subject</span></div>
  <div class="fld"><label for="f-volume">volume</label><select id="f-volume"></select><span class="hint">a reference cites this CW volume</span></div>
  <div class="fld"><label for="f-claim_type">claim type</label><select id="f-claim_type"></select><span class="hint">read off the reference, not the edge</span></div>
  <div class="fld"><label for="f-provenance">provenance</label><input id="f-provenance" placeholder="e.g. human-adjudication"><span class="hint">substring of relation_family.by</span></div>
  <div class="fld"><label for="f-relation">relation</label><input id="f-relation" placeholder="verbatim or normalized"><span class="hint" id="h-normalized"></span></div>
</div>

<div class="toggles">
  <label class="tog"><input type="checkbox" id="t-closure"> closure — add the rows the active declarations license</label>
  <label class="tog"><input type="checkbox" id="t-quotes" checked> quotes — the graph's own excerpts</label>
  <button class="runbtn" type="button" id="run">run</button>
</div>

<div class="rows" id="rows"><p class="dim" id="status">Reading the dataset…</p></div>
<div class="receipts"><b>receipts</b><span id="receipts">${esc(receiptsFooter)}</span></div>

<h2>Identity walk</h2>
<div class="callout"><p id="walkhead" class="ev">${esc(walkHeader)}</p></div>
<div class="filters" style="margin-top:.8rem">
  <div class="fld"><label for="w-start">start node</label><input id="w-start" placeholder="mercurius"><span class="hint">node id, else substring of an id or a label</span></div>
  <div class="fld"><label for="w-depth">depth</label><select id="w-depth"><option>1</option><option selected>2</option><option>3</option></select><span class="hint">a budget, not a measure of closeness</span></div>
  <div class="fld" style="justify-content:end"><button class="runbtn" type="button" id="runwalk" style="margin:0">walk</button></div>
</div>
<div class="walk" id="walk"></div>

<div class="callout" style="margin-top:1.4rem"><p>A derived row is not an edge. It carries its source edge's references and no citation of its own, it is not written to the graph, and it does not compound: closure is applied once to the stored edges and never to its own output. A count of rows is therefore not a count of edges, and the line under the results says which is which.</p></div>`

  const queryStyle = `
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: .7rem .9rem; margin-top: 1rem; }
.fld { display: flex; flex-direction: column; gap: .25rem; }
.fld label { font: .55rem var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--ink-dim); }
.fld input, .fld select { background: var(--panel); color: var(--ink); border: 1px solid var(--hairline);
  border-radius: 7px; padding: .42rem .6rem; font-family: var(--serif); font-size: .88rem; appearance: none; width: 100%; }
.fld select { font-family: var(--mono); font-size: .74rem; }
.fld .hint { font: .55rem var(--mono); color: var(--ink-dim); }
.toggles { display: flex; flex-wrap: wrap; gap: 1.1rem; align-items: center; margin: .95rem 0 .2rem;
  padding-top: .8rem; border-top: 1px solid var(--hairline); }
.tog { display: flex; align-items: center; gap: .45rem; font: .62rem var(--mono); color: var(--ink-label); cursor: pointer; }
.tog input { accent-color: var(--gold-dim); width: .85rem; height: .85rem; }
.runbtn { margin-left: auto; background: transparent; color: var(--gold); border: 1px solid var(--gold-dim);
  border-radius: 999px; padding: .34rem 1.1rem; font: .62rem var(--mono); letter-spacing: .1em; cursor: pointer; }
.rows { margin-top: 1rem; border-top: 1px solid var(--hairline); }
.row { padding: .55rem .2rem .55rem .55rem; border-bottom: 1px solid var(--hairline); }
.row .triple { display: flex; flex-wrap: wrap; align-items: baseline; gap: .45rem; font-size: .96rem; }
.row .rel { color: var(--gold); font-style: italic; }
.row .cite { font: .6rem var(--mono); color: var(--gold-dim); }
.row .quote { font-size: .85rem; color: var(--ink-faint); margin-top: .22rem; }
.row.derived { border-left: 3px dashed var(--m-motif); background: rgba(139,150,165,.05);
  border-radius: 0 6px 6px 0; padding-left: .7rem; }
.row .prov { font: .58rem var(--mono); color: var(--m-motif); margin-top: .24rem; }
.c-derived { color: var(--m-motif); border-color: var(--m-motif); border-style: dashed; }
.rowcount { font: .62rem/1.7 var(--mono); color: var(--ink-faint); padding: .55rem .2rem; }
.walk .depth { font: .56rem var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--gold-dim); margin: .9rem 0 .35rem; }
.hop { display: flex; flex-wrap: wrap; align-items: baseline; gap: .4rem; padding: .3rem 0 .3rem .9rem; border-left: 1px solid var(--hairline); font-size: .9rem; }
.hop .arrow { color: var(--edge-idle); }
.hop .via { font: .6rem var(--mono); color: var(--ink-dim); }
.hop .rel { color: var(--gold); font-style: italic; }
.hop .cite { font: .6rem var(--mono); color: var(--gold-dim); }
.hop .against { font: .56rem var(--mono); color: var(--m-motif); }
`

  // The page's own script. It renders; the semantics live in query.js.
  const ROW_CAP = 300
  derived(ROW_CAP)
  const queryHead = `<script type="module">
import { select, walk, labelIndex, identityEdges, effectiveRelation, derivedRows, byVolume } from '/query.js'

const ROW_CAP = ${ROW_CAP}
const $ = (id) => document.getElementById(id)
const esc = (s) => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c])
let graph = null, decls = null, labels = {}

const cite = (refs) => refs.map(r => 'CW ' + r.volume + ' \\u00a7' + r.paragraph).join(', ')
const firstQuote = (refs) => { for (const r of refs) if (r.quote) return r.quote; return '' }

function fill (id, values, allLabel) {
  const el = $(id)
  el.innerHTML = '<option value="">' + allLabel + '</option>' +
    values.map(([v, n]) => '<option value="' + esc(v) + '">' + esc(v) + (n === null ? '' : ' \\u00b7 ' + n) + '</option>').join('')
}

function tallyBy (fn) {
  const t = new Map()
  for (const e of graph.edges) { const k = fn(e); if (k !== null && k !== undefined && k !== '') t.set(k, (t.get(k) || 0) + 1) }
  return [...t.entries()].sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0])))
}

function ready () {
  labels = labelIndex(graph)
  const fams = tallyBy(e => (e.relation_family || {}).value)
  fill('f-family', fams, 'any family')
  $('h-family').textContent = fams.length + ' families hold at least one assigned relation'
  fill('f-state', tallyBy(e => (e.relation_family || {}).state), 'any state')
  const vols = new Map(); const cts = new Map()
  for (const e of graph.edges) for (const r of (e.references || [])) {
    vols.set(String(r.volume), (vols.get(String(r.volume)) || 0) + 1)
    if (r.claim_type) cts.set(r.claim_type, (cts.get(r.claim_type) || 0) + 1)
  }
  // V2-R8 — volumes read in collection order, never by frequency or as strings
  fill('f-volume', [...vols.entries()].sort((a, b) => byVolume(a[0], b[0])), 'any volume')
  fill('f-claim_type', [...cts.entries()].sort((a, b) => b[1] - a[1]), 'any claim type')
  const normalized = graph.edges.filter(e => e.relation_normalized && e.relation_normalized.relation).length
  $('h-normalized').textContent = normalized + ' relations carry a normalized string beside the verbatim one'
  $('status').textContent = 'Ready. Run with no filter to read the whole graph.'
  run()
}

function filters () {
  const f = { closure: $('t-closure').checked }
  for (const k of ['family', 'state', 'subject', 'object', 'volume', 'claim_type', 'provenance']) f[k] = $('f-' + k).value.trim()
  f.relation = $('f-relation').value.trim()
  return f
}

function rowHtml (row) {
  const derivedRow = row.origin !== 'graph'
  const q = $('t-quotes').checked ? firstQuote(row.references) : ''
  return '<div class="row' + (derivedRow ? ' derived' : '') + '">' +
    '<div class="triple"><span>' + esc(labels[row.subject] || row.subject) + '</span> ' +
    '<span class="rel">' + esc(row.relation) + '</span> ' +
    '<span>' + esc(labels[row.object] || row.object) + '</span> ' +
    '<span class="cite">' + esc(cite(row.references)) + '</span>' +
    '<span class="chip ' + (row.family ? 'f-ok' : 'f-none') + '">' + esc(row.family || ('unclassified(' + (row.state || 'unrecorded') + ')')) + '</span>' +
    (derivedRow ? '<span class="chip c-derived">derived row \\u00b7 not an edge</span>' : '') +
    '</div>' +
    (q ? '<div class="quote">\\u201c' + esc(q) + '\\u201d</div>' : '') +
    (derivedRow ? '<div class="prov">' + esc(row.origin) + ' of ' + esc(row.derived_from.subject + ' ' + row.derived_from.relation + ' ' + row.derived_from.object) + '</div>' : '') +
    '</div>'
}

function run () {
  const f = filters()
  const rows = select(graph, decls, f)
  const stored = rows.filter(r => r.origin === 'graph').length
  const derivedCount = rows.length - stored
  const shown = rows.slice(0, ROW_CAP)
  const closureAll = f.closure ? derivedRows(graph, decls).length : null
  $('rows').innerHTML = shown.map(rowHtml).join('') +
    '<div class="rowcount"><b>' + stored + '</b> stored edges' +
    (f.closure ? ', +' + derivedCount + ' derived' : '') + '. ' +
    (rows.length > ROW_CAP ? 'The first ' + ROW_CAP + ' rows are drawn; narrow the filters, or run the same query on the command line for the whole set. ' : '') +
    (closureAll !== null ? 'Closure over the whole graph reads ' + closureAll + ' derived rows from ' + graph.edges.length + ' stored edges. ' : '') +
    'A copied number is an edge count: derived rows are readings of those edges in the other direction, not additions to them.</div>'
}

function runWalk () {
  const needle = $('w-start').value.trim()
  const depth = Number($('w-depth').value)
  const out = $('walk')
  if (!needle) { out.innerHTML = '<p class="dim">Name a start node.</p>'; return }
  const ids = Object.keys(labels)
  let start = ids.includes(needle) ? needle : ids.find(id => id.toLowerCase() === needle.toLowerCase())
  if (!start) start = ids.filter(id => id.toLowerCase().includes(needle.toLowerCase()) || String(labels[id]).toLowerCase().includes(needle.toLowerCase())).sort()[0]
  if (!start) { out.innerHTML = '<p class="dim">No node matches that.</p>'; return }
  const levels = walk(graph, start, depth)
  const family = identityEdges(graph).length
  let html = '<p class="meta">start: ' + esc(labels[start] || start) + ' (' + esc(start) + ') \\u00b7 depth ' + depth +
    ' \\u00b7 ' + family + ' edges carry the identity family</p>'
  let hops = 0
  for (const level of levels) {
    if (!level.length) continue
    html += '<div class="depth">depth ' + level[0].depth + '</div>'
    for (const hop of level) {
      hops++
      html += '<div class="hop"><span>' + esc(labels[hop.from] || hop.from) + '</span><span class="arrow">\\u2192</span>' +
        '<span>' + esc(labels[hop.to] || hop.to) + '</span>' +
        '<span class="via">via ' + esc(labels[hop.edge.subject] || hop.edge.subject) + ' <span class="rel">' + esc(hop.edge.relation) + '</span> ' + esc(labels[hop.edge.object] || hop.edge.object) + '</span>' +
        '<span class="cite">' + esc(cite(hop.references)) + '</span>' +
        (hop.direction === 'reverse' ? '<span class="against">traversed against the edge</span>' : '') + '</div>'
    }
  }
  html += '<div class="rowcount">' + hops + ' hops. Each is one edge with its own citation. Reaching a term in two hops is not identity with the start, and the paragraph above the first hop says so rather than the line under the last.</div>'
  out.innerHTML = html
}

$('run').addEventListener('click', run)
$('runwalk').addEventListener('click', runWalk)
for (const el of document.querySelectorAll('#filters input')) el.addEventListener('keydown', e => { if (e.key === 'Enter') run() })
$('w-start').addEventListener('keydown', e => { if (e.key === 'Enter') runWalk() })

Promise.all([fetch('/graph.json').then(r => r.json()), fetch('/relation_declarations.json').then(r => r.json())])
  .then(([g, d]) => { graph = g; decls = d; ready() })
  .catch(err => { $('status').textContent = 'The dataset did not load: ' + err })
</script>`

  registerPage({
    slug: 'query', title: 'Query the graph', where: 'query', nav: 'query',
    changefreq: 'daily', priority: '0.6', style: queryStyle, body: queryBody, head: queryHead
  })
  V2_COPY.push(['public/query.html (generated)', stripEvidence(queryBody)])
  console.log(`query panel: declarations ${activeDecls.length} active, walk header lifted from kg_query.py (${walkHeader.length} chars)`)
}

// ------------------------------------------------ V2-R5 · /ontology -------
// What the ontology is, what it deliberately is not, and the pitfall scan run
// fresh at build. The scan is consumed as JSON from tools/ontology_qa/quality.py
// rather than scraped from its prose, and every figure below is its output.
//
// The framing rule, from the anti-overclaim checklist: several of the scan's
// findings are decisions this project made on purpose, and one of them is the
// reason the project exists. The panel says which is which, in a column, and it
// neither counts a decision as a defect nor hides what a decision costs.
const QA_STANCE = [
  [/^P22/, 'design', 'The relation slot holds Jung\u2019s own predication, frozen verbatim. A closed property set would mean editing the claim to fit the schema, so the vocabulary stays open and the family layer classifies over it.'],
  [/^P24 relation name/, 'open', 'A predicate carrying a whole proposition is the project\u2019s named defect. New mining is constrained by a form rule, and the normalization layer repairs the old edges beside their frozen originals rather than over them.'],
  [/^P24 node label/, 'open', 'A label that is a sentence cannot be matched across edges. Counted here, not yet repaired.'],
  [/^P02\/P30 synonymous/, 'declared', 'Equivalence is stated by the family layer, per edge in its paragraph rather than per string in the abstract; where the definitions document rules on a specific pair, a declaration records it and the query layer applies it at read time.'],
  [/^P05\/P13/, 'declared', 'The declarations name the inverse pairs the document rules on. They are applied when a query asks for closure and are never written into the graph.'],
  [/^P25/, 'declared', 'Same answer: a symmetric declaration is read at query time. Asserting the second direction in the graph would put a claim in it that no paragraph was gated for.'],
  [/^P30 identity clusters/, 'design', 'Transitivity is rejected on every family. Identity chains are traversed by a depth-bounded walk that prints each hop\u2019s own citation and asserts nothing about the ends.'],
  [/^P04/, 'open', 'A detached component is a gap in what has been mined, not a decision.'],
  [/^P11\/P12/, 'design', 'No relation is given a domain or a range as a constraint. The observed signatures are a measurement of the corpus; a constraint would reject an edge because of what the schema expects rather than what the paragraph says.'],
  [/^P21/, 'open', 'The type tag is coarse and does little work. It colours the map and picks the Concordance registers; nothing rests on it.'],
  [/^P10/, 'design', 'Types are not declared disjoint. A node can function in two registers at once, and the graph would have to choose one to satisfy a disjointness axiom.'],
  [/^P06/, 'design', 'This is an associative network with a type tag, not a subsumption ontology, and the paper describes it as one. There is no hierarchy to inherit through because none was claimed.'],
  [/^P02 ambiguous/, 'design', '`is` is the word Jung used. The family assignment disambiguates it per edge, in the paragraph it came from, and the verbatim string stays as written.'],
  [/^P02 duplicate/, 'open', 'Two ids carrying the same label is a defect in the node set.'],
  [/^evidence gap/, 'design', 'The structural relations (sequence between stages) carry no citation by design and are excluded from the verified count. Any other relation without a reference is a defect and the structural check refuses it.']
]
// V2-R6 addendum (editorial review, 2026-08-13): the panel says where its checks
// come from. OOPS! numbers pitfalls; quality.py implements a subset of them and
// borrows the numbering. Two of the tool's uses are adaptations rather than the
// catalogue's literal case — the catalogue was written for class-shaped
// ontologies and this graph is relation-shaped — and the table says which, since
// a borrowed number presented as the catalogue's own finding would overclaim.
const PITFALLS = {
  P02: ['synonymous elements not declared equivalent', ''],
  P03: ['a bare `is` used where a subclass or type relation is meant', ''],
  P04: ['elements left unconnected to the rest of the ontology', ''],
  P05: ['an inverse relationship defined the wrong way round', 'read here as inverse pairs present in the vocabulary but undeclared'],
  P06: ['a defect in the class hierarchy', 'read here as the absence of a hierarchy to have a defect in'],
  P08: ['elements left without human-readable annotation', ''],
  P10: ['classes never declared disjoint', ''],
  P11: ['a property with no declared domain', ''],
  P12: ['equivalent properties not declared equivalent', ''],
  P13: ['inverse relationships not declared', ''],
  P21: ['a catch-all class doing the work of a distinction', ''],
  P22: ['no naming regularity across the vocabulary', ''],
  P24: ['a name that carries a definition instead of naming a term', 'applied here to predicates that carry a whole proposition, and to labels that are sentences'],
  P25: ['a relationship declared inverse to itself', 'read here as a symmetric relation asserted in one direction only'],
  P30: ['equivalent elements not declared equivalent', 'read here over identity chains between nodes']
}
const STANCE_LABEL = {
  design: 'recorded design decision',
  declared: 'answered by the declarations layer',
  open: 'open — recorded as a defect',
  unclassified: 'not classified'
}
let QA = null
try {
  QA = JSON.parse(execFileSync('python3',
    [`${repoDir}tools/ontology_qa/quality.py`, `${repoDir}seed.json`, '--json'],
    { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }))
} catch (err) {
  console.warn(`ontology page: the QA scan did not run (${String(err.message).split('\n')[0]}). ` +
    `The page is not written this build — a panel dated today carrying yesterday's numbers would be worse than no panel.`)
}

if (QA && DECL) {
  const h = QA.headline
  const di = h.declared_inverses || {}
  const stanceOf = (tag) => {
    const hit = QA_STANCE.find(([re]) => re.test(tag))
    return hit ? { kind: hit[1], why: hit[2] } : { kind: 'unclassified', why: 'This finding has no recorded stance. It is shown as the scan reported it.' }
  }
  const findingRows = ['critical', 'important', 'minor'].flatMap(sev =>
    QA[sev].map(f => {
      const s = stanceOf(f.tag)
      return `<tr class="st-${s.kind}">
<td class="sev">${esc(sev)}</td>
<td><div class="ev tag">${esc(f.tag)}</div><div class="ev fmsg">${esc(f.message)}</div></td>
<td><span class="chip st-${s.kind}">${esc(STANCE_LABEL[s.kind])}</span><div class="why">${esc(s.why)}</div></td>
</tr>`
    })).join('\n')
  const counts = { design: 0, declared: 0, open: 0, unclassified: 0 }
  for (const sev of ['critical', 'important', 'minor']) for (const f of QA[sev]) counts[stanceOf(f.tag).kind]++
  derived(...Object.values(counts), QA.totals.critical + QA.totals.important + QA.totals.minor,
    h.hapax_relations, h.distinct_relations, h.sentence_shaped_relations, h.sentence_shaped_edges,
    h.detached_components, h.largest_component, h.components,
    di.active_declarations, di.observed_inverse_pairs_in_vocabulary, di.observed_pairs_declared,
    di.edges_carrying_a_declared_string, DECL.candidates_awaiting_ruling.length, DECL.rulings.length)

  const declRows = activeDecls.map(d => `<tr>
<td class="ev"><code>${esc(d.kind === 'inverse' ? `${d.forward} / ${d.inverse}` : d.relation)}</code></td>
<td>${esc(d.kind)}${d.applies_to_family ? `<br><span class="dim">only where the edge carries <span class="ev">${esc(d.applies_to_family)}</span></span>` : ''}${d.carried_qualifier ? `<br><span class="dim">carries <span class="ev">${esc(d.carried_qualifier)}</span> into the derived row</span>` : ''}</td>
<td class="ev src">${d.source.map(s => `${esc(s.section)} (line ${s.line})`).join('<br>')}</td>
</tr>`).join('\n')

  const rulingRows = (DECL.rulings || []).map(r => `<tr>
<td class="n">${esc(r.date)}</td><td class="ev">${esc(r.ruled_by)}</td><td class="ev">${esc(r.ruling)}</td>
</tr>`).join('\n')

  // the codes the tool actually cites, read out of its findings and its source,
  // so the table cannot list a pitfall the scan does not implement
  const toolSrc = readFileSync(here('../tools/ontology_qa/quality.py'), 'utf8')
  const cited = [...new Set([
    ...['critical', 'important', 'minor'].flatMap(sev => QA[sev].flatMap(f => f.tag.match(/P\d{2}/g) || [])),
    ...(toolSrc.match(/P\d{2}/g) || [])
  ])].sort()
  const pitfallRows = cited.map(code => {
    const entry = PITFALLS[code]
    return `<tr><td class="n">${esc(code)}</td><td>${entry ? esc(entry[0]) : 'no gloss recorded for this code'}</td>` +
      `<td class="dim">${entry && entry[1] ? esc(entry[1]) : 'as the catalogue has it'}</td></tr>`
  }).join('\n')
  derived(cited.length)

  const ontBody = `<p class="eyebrow">the ontology</p>
<h1>What this graph is, as an ontology</h1>
<p>It is a network of asserted relations between named things, each relation carrying the paragraph it came from and a quote from it. It is not a subsumption ontology, and most of what an ontology engineer would look for is missing on purpose. This page says what the design is, what it leaves out and why, and then runs the standard pitfall scan over the graph and reports what it finds — including the findings that are these decisions showing up as defects.</p>

<h2>Two tiers</h2>
<p>The first tier is the relation as Jung's sentence phrased it. It is frozen: the string is part of the claim that was gated, and a model of a different family judged the paragraph against exactly that wording. Rewriting it into a controlled predicate would change what was verified.</p>
<p>The second tier is the family — a classification <em>over</em> the verified relation, drawn from a fixed vocabulary in a versioned document, assigned when two models reading that document independently name the same family, and ruled by a person when they do not. The second tier never reopens the first. Nothing on this site calls a family verified, and no family assignment changes a relation string.</p>
<p>Where a relation carried a whole clause, a normalization layer records a cleaned verb phrase beside the frozen original, with the qualifiers pulled out into their own fields. ${meta.normalized} relations carry that layer. The family layer classifies the normalized form where it exists, which is why the map counts effective strings rather than surface ones.</p>

<h2>The declarations</h2>
<p>Two properties are declared, and only two: which relation strings are inverses of each other, and which are symmetric. Each declaration is transcribed from a line of the definitions document, cites that line, and is applied only when a reader asks for closure — the derived row is labelled, carries its source edge's references, and is never written into the graph.</p>
<div class="tw"><table><thead><tr><th>strings</th><th>kind</th><th>transcribed from</th></tr></thead><tbody>
${declRows}
</tbody></table></div>
<p class="meta">${activeDecls.length} active. ${DECL.candidates_awaiting_ruling.length} further pairs are recorded as candidates and are inert: the document has not ruled on them, and a declaration without a document line to cite would be this build's opinion rather than the ruleset's.</p>
${rulingRows ? `<h4>rulings behind them</h4>
<div class="tw"><table><thead><tr><th>date</th><th>ruled by</th><th>ruling</th></tr></thead><tbody>
${rulingRows}
</tbody></table></div>` : ''}

<h2>Deliberately absent</h2>
<ul class="absent">
<li><b>Transitivity.</b> No family is transitive, and the identity walk says so above its first hop. Two terms joined through a third are joined through a third; the graph does not claim they are the same.</li>
<li><b>Domain and range as constraints.</b> The signatures a relation is observed with are a measurement of the corpus. As a constraint they would reject an edge for disagreeing with the schema rather than with the paragraph.</li>
<li><b>Disjoint types.</b> A node can work in two registers at once, and a disjointness axiom would force a choice the material does not make.</li>
<li><b>A subsumption backbone.</b> There is no hierarchy to inherit through, because none was claimed. The type tag is a coarse label, not a class system.</li>
<li><b>A closed relation vocabulary.</b> The predicate is Jung's phrasing. Closing the set would mean editing claims, so the set stays open and the family layer carries the classification.</li>
</ul>

<h2>Where the checks come from</h2>
<p>The scan follows the OOPS! catalogue — OntOlogy Pitfall Scanner — which numbers the modelling faults that recur across published ontologies and describes how each can be detected. A pitfall catalogue is not a standard to comply with; it is a list of the places ontologies are known to go wrong, so that an evaluation can be systematic instead of a matter of taste. <code>tools/ontology_qa/quality.py</code> implements a subset of it locally against this graph, and keeps the catalogue's numbering so a finding can be looked up in the literature. It is not the OOPS! service and does not run its full test set.</p>
<p class="meta">Poveda-Villal\u00f3n, G\u00f3mez-P\u00e9rez and Su\u00e1rez-Figueroa, "OOPS! (OntOlogy Pitfall Scanner!): An On-line Tool for Ontology Evaluation", <i>International Journal on Semantic Web and Information Systems</i> 10(2), 2014.</p>
<div class="tw"><table><thead><tr><th>pitfall</th><th>what the catalogue names</th><th>use here</th></tr></thead><tbody>
${pitfallRows}
</tbody></table></div>
<p class="meta">The catalogue was written for ontologies built out of classes and properties; this graph is built out of relations between named things. Where a number is borrowed for a fault of a different shape, the third column says so — a borrowed number presented as the catalogue's own finding would claim more agreement with the literature than there is. The standing frame holds over all of it: a finding maps to the catalogue where one applies, and several of the findings below are decisions recorded above rather than defects.</p>

<h2>The pitfall scan</h2>
<p>Run at every build by <code>tools/ontology_qa/quality.py</code>, which reads the graph and writes nothing. The four figures below are its own; the table under them is every finding it reported, with this project's stance beside each one. ${counts.design} of the ${QA.totals.critical + QA.totals.important + QA.totals.minor} findings are decisions recorded above, ${counts.declared} are answered by the declarations, and ${counts.open} are open defects carried in the record.</p>
<div class="qa">
  <div class="fig"><span class="figv ev">${h.hapax_pct}%</span><span class="figl">of relation strings are used exactly once <span class="ev">(${h.hapax_relations} of ${h.distinct_relations})</span></span></div>
  <div class="fig"><span class="figv ev">${h.sentence_shaped_relations}</span><span class="figl">sentence-shaped predicates remain, over <span class="ev">${h.sentence_shaped_edges}</span> relations</span></div>
  <div class="fig"><span class="figv ev">${di.observed_pairs_declared}/${di.observed_inverse_pairs_in_vocabulary}</span><span class="figl">inverse pairs present in the vocabulary have a declaration <span class="ev">(${di.edges_carrying_a_declared_string}</span> relations carry a declared string)</span></div>
  <div class="fig"><span class="figv ev">${h.detached_components}</span><span class="figl">component detached from the main graph <span class="ev">(${h.largest_component}</span> of ${h.nodes} nodes are in it)</span></div>
</div>
<details class="disclose">
<summary>${QA.totals.critical + QA.totals.important + QA.totals.minor} findings: ${counts.design} recorded design decisions, ${counts.declared} answered by the declarations, ${counts.open} open defects.<span class="more">every finding, with its stance</span></summary>
<div class="tw"><table class="findings"><thead><tr><th>severity</th><th>the scan's finding</th><th>stance</th></tr></thead><tbody>
${findingRows}
</tbody></table></div>
</details>
<p class="meta">A stance is not a rebuttal. Every design decision here has a cost, and the scan is a fair statement of it: an open vocabulary does make the graph hard to query by predicate, which is exactly why the family layer exists and why its coverage is published with its gaps. What the panel refuses is the other reading — that a decision taken deliberately, with a reason on record, is a defect discovered by a tool.</p>

<div class="receipts"><b>receipts</b>
scan output from <code>tools/ontology_qa/quality.py --json</code> over seed.json <span class="hash">sha256:${seedDigest.slice(0, 12)}</span>, run at build;<br>
declarations from <code>pipeline/family/relation_declarations.json</code>, transcribed from FAMILY_DEFINITIONS ${esc((DECL.transcribed_from || {}).document_version || '?')};<br>
built ${buildDate}${gitCommit ? ` at commit ${gitCommit}` : ''}
</div>`

  const ontStyle = `
.absent { list-style: none; margin: .6rem 0; }
.absent li { font-size: .92rem; line-height: 1.6; padding: .3rem 0 .3rem 1rem; border-left: 2px solid var(--hairline); margin-bottom: .4rem; max-width: 68ch; }
.qa { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: .7rem; margin: 1rem 0; }
.qa .fig { border: 1px solid var(--hairline); border-radius: 8px; padding: .6rem .75rem; background: var(--surface); }
.qa .figv { display: block; font-family: var(--display); font-size: 1.5rem; color: var(--gold); }
.qa .figl { display: block; font: .58rem/1.6 var(--mono); color: var(--ink-faint); margin-top: .2rem; }
table.findings td { font-size: .82rem; }
table.findings .sev { font: .55rem var(--mono); text-transform: uppercase; color: var(--ink-dim); white-space: nowrap; }
table.findings .tag { font: .62rem var(--mono); color: var(--ink-label); margin-bottom: .2rem; }
table.findings .fmsg { color: var(--ink-faint); font-size: .8rem; line-height: 1.5; }
table.findings .why { font-size: .78rem; line-height: 1.5; color: var(--ink-faint); margin-top: .25rem; max-width: 40ch; }
table.findings .src { font: .58rem var(--mono); }
.chip.st-design { color: var(--m-substance); border-color: var(--b-ok); }
.chip.st-declared { color: var(--teal); border-color: var(--b-teal); }
.chip.st-open { color: var(--amber); border-color: var(--b-amber); }
.chip.st-unclassified { color: var(--rubedo); border-color: var(--b-rubedo); }
.src { font: .58rem var(--mono); }
`
  registerPage({
    slug: 'ontology', title: 'The ontology and its practices', where: 'ontology',
    nav: 'ontology', changefreq: 'daily', priority: '0.5', style: ontStyle, body: ontBody
  })
  V2_COPY.push(['public/ontology.html (generated)', stripEvidence(ontBody)])
  // The scan's findings, kept for whatever reads them next (the #/method route
  // is the obvious candidate). The example lists are dropped: they come out of
  // set iteration inside the tool and are not stable between two runs over the
  // same graph, so committing them would churn a tracked file for no reading.
  writeFileSync(here('./src/ontology_qa.json'), JSON.stringify({
    ...QA,
    critical: QA.critical.map(({ tag, message }) => ({ tag, message })),
    important: QA.important.map(({ tag, message }) => ({ tag, message })),
    minor: QA.minor.map(({ tag, message }) => ({ tag, message })),
    _examples_dropped: 'the scan prints examples; their order is not stable between runs, so they are not carried into this file'
  }))
  console.log(`ontology page: scan ${QA.totals.critical}/${QA.totals.important}/${QA.totals.minor} findings — ` +
    `${counts.design} design, ${counts.declared} declared, ${counts.open} open, ${counts.unclassified} unclassified`)
}

// ------------------------------------------------ the pages are written ----
// The batch delta pages, listed from pipeline/state.json.
{
  const st = JSON.parse(readFileSync(here('../pipeline/state.json'), 'utf8'))
  for (const b of st.batches) registerExternalPage({ slug: batchSlug(b.id), title: `${b.id} — a batch delta` })
  console.log(`batch deltas: ${st.batches.length} pages listed in the sitemap (written by tools/build_ledger_page.py)`)
}

function emitPages() {
  for (const p of NEW_PAGES) writeFileSync(here(`./public/${p.slug}.html`), renderPage(p))
  const urls = SITE_PAGES.map(p =>
    `  <url><loc>https://symbolicworld.observer/${p.slug}</loc><changefreq>${p.changefreq}</changefreq><priority>${p.priority}</priority></url>`)
  writeFileSync(here('./public/sitemap.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`)
  console.log(`pages: ${NEW_PAGES.length} generated (${NEW_PAGES.map(p => '/' + p.slug).join(' ')}) · sitemap ${SITE_PAGES.length} urls`)
}
emitPages()

// ------------------------------------ R10.0 / R10.9 · the copy assertions ---
// Two rules the build enforces rather than trusts:
//  1. Every count-like number in user-facing copy must come from atlas.json meta.
//     A hardcoded "1147" survives a merge and quietly lies; the build now fails
//     on one instead.
//  2. "load-bearing" is banned from our own copy. It is NOT stripped from the
//     rendered source document (docs/FAMILY_DEFINITIONS.md uses the phrase), as
//     paraphrasing that document is a stronger prohibition.
//
// Both rules scan INTERFACE COPY only — the templates and strings we write. The
// graph's own data is deliberately not a copy source: quotes, correction_note
// and refs in atlas.json are evidence and provenance, and rewriting them to suit
// a style rule would be falsifying the record. One gate correction (edge e904,
// CW 9ii §70) legitimately uses "load-bearing" to explain what the bare relation
// drops; it renders in that claim's receipts and must never trip the ban. So do
// not add atlas.json, seed.json, families.json or validations.json to
// `copySources` — the exemption is the absence, and it is the point.
const allowedNumbers = new Set([
  ...Object.values(meta.counts), ...Object.values(meta.frozen).filter(v => typeof v === 'number'),
  ...Object.values(methodTokens || {}).filter(v => typeof v === 'number'),
  ...Object.values(meta.familyLayer.states || {}), meta.familyLayer.families, meta.normalized,
  core.length, bridges.length, guided.length, guidedReverse.length,
  ...volumes.flatMap(v => [v.references, v.edges]), ...Object.values(meta.voices || {}),
  ...Object.values(meta.layers || {}),
  // R3.5 — every count the families page prints comes from the derived map, so
  // the map's own numbers join the allowlist. A literal on that page that the
  // map cannot produce is exactly what this check exists to catch.
  ...Object.values(famMap.totals), famMap.totals.no_family + famMap.totals.text_undecided,
  ...famMap.provenance.map(p => p.edges),
  ...famMap.families.flatMap(f => [f.edges, ...f.strings.map(s => s.edges)]),
  ...famMap.homeless.map(r => r.edges), ...famMap.text_undecided.map(r => r.edges),
  // V2 — the figures the v2.0 pages interpolate, collected at the point each
  // one is computed (see `derived` above).
  ...V2_NUMBERS
].filter(n => Number.isFinite(n)))

// Frozen measured results quoted in the method copy, with the sources the copy
// document itself records. They are constants, not counts that move.
const METHOD_CONSTANTS = new Set([
  19, 20, 38, 40, 2, 86, 14, 7, 25, 5, 248, 669, 699, 5281, 21631523
])
const copySources = [
  ['docs/METHOD_COPY.md (wired verbatim)', methodHTML, METHOD_CONSTANTS],
  // The families page's own exposition (NOT the definitions document it renders
  // below the rule — that is the source, and paraphrasing it is the stronger
  // prohibition). BACKLOG item 3's checklist binds this copy, so it is scanned
  // like any other page we write.
  ['public/families.html (generated exposition)', famPageCopy],
  ['index.html', readFileSync(here('./index.html'), 'utf8')
    .replace(/<style[\s\S]*?<\/style>/g, '').replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<[^>]+>/g, ' ')],
  ['src/main.js', readFileSync(here('./src/main.js'), 'utf8')],
  ['src/concordance.js', readFileSync(here('./src/concordance.js'), 'utf8')],
  ['src/assembly.js', readFileSync(here('./src/assembly.js'), 'utf8')],
  // V2-R6 — a new page joins this scan in the commit that creates it. The
  // evidence it carries (quotes, relation strings, citations) is stripped
  // first, for the reason recorded above `stripEvidence`.
  ...V2_COPY
]
const copyProblems = []
for (const [name, text, extraAllowed] of copySources) {
  const scan = name.endsWith('.js')
    // only string and template literals carry copy; code and CSS numbers do not
    ? (text.match(/`[^`]*`|'[^'\n]*'|"[^"\n]*"/g) || []).join('\n')
    : text
  for (const m of scan.matchAll(/\b\d{3,4}\b/g)) {
    const n = Number(m[0])
    if (allowedNumbers.has(n)) continue
    if (extraAllowed && extraAllowed.has(n)) continue
    if (n >= 1900 && n <= 2100) continue            // years
    if (/(?:ms|px|rem|zoom|duration|width|height|top|left|z-index|opacity|\bcw\b|paragraph|§|zenodo|doi)/i
      .test(scan.slice(Math.max(0, m.index - 40), m.index))) continue   // geometry, timing, citations
    copyProblems.push(`${name}: literal ${n} in copy is not derived from atlas.json meta`)
  }
}
for (const [name, text] of copySources)
  if (/load-bearing/i.test(text)) copyProblems.push(`${name}: the banned phrase "load-bearing" appears in copy`)

if (copyProblems.length) {
  console.error('\nCOPY CONTRACT FAILED (R10.0/R10.9):')
  for (const p of copyProblems) console.error('  · ' + p)
  process.exit(1)
}
console.log(`copy contract: ok — ${allowedNumbers.size} meta-derived numbers allowed, no banned phrases`)
