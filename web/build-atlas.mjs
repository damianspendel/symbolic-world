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

writeFileSync(here('./src/families.json'), JSON.stringify({
  version: famVersion, source: 'docs/FAMILY_DEFINITIONS.md', doc_url: './families.html',
  state_note: STATE_NOTE, boundary_rules: boundaryRules, families
}))

// The complete document, rendered — the "full definitions" destination in R3.3.
writeFileSync(here('./public/families.html'), renderDoc(famDoc, famVersion))

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
const volumes = Object.keys(volRefs)
  .sort((a, b) => volKeyBuild(a) - volKeyBuild(b))
  .map(v => ({ volume: v, label: VOL_LABEL[v] || '', references: volRefs[v], edges: volEdges[v] || 0 }))
function volKeyBuild(v) {
  const m = String(v).match(/^(\d+)(i*)$/)
  return m ? parseInt(m[1], 10) + (m[2] === 'ii' ? 0.2 : m[2] === 'i' ? 0.1 : 0) : 999
}

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

function renderDoc(md, version) {
  const out = [renderMarkdown(md)]
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
</style></head>
<body>
<div class="page-bar"><a class="back" href="./#/atlas">\u2190 the atlas</a><span class="where">Relation families</span></div>
<main>
${out.join('\n')}
<p class="gen">Rendered from <code>docs/FAMILY_DEFINITIONS.md</code> at build time. The atlas quotes this document; it never paraphrases it.</p>
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

  methodTokens = {
    nodes: meta.counts.nodes, edges: meta.counts.edges, refs: meta.counts.references,
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
  ...Object.values(meta.familyLayer.states || {}), meta.familyLayer.families, meta.normalized,
  core.length, bridges.length, guided.length, guidedReverse.length,
  ...volumes.flatMap(v => [v.references, v.edges]), ...Object.values(meta.voices || {}),
  ...Object.values(meta.layers || {})
].filter(n => Number.isFinite(n)))

// Frozen measured results quoted in the method copy, with the sources the copy
// document itself records. They are constants, not counts that move.
const METHOD_CONSTANTS = new Set([
  19, 20, 38, 40, 2, 86, 14, 7, 25, 5, 248, 669, 699, 5281, 21631523
])
const copySources = [
  ['docs/METHOD_COPY.md (wired verbatim)', methodHTML, METHOD_CONSTANTS],
  ['index.html', readFileSync(here('./index.html'), 'utf8')
    .replace(/<style[\s\S]*?<\/style>/g, '').replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<[^>]+>/g, ' ')],
  ['src/main.js', readFileSync(here('./src/main.js'), 'utf8')],
  ['src/concordance.js', readFileSync(here('./src/concordance.js'), 'utf8')],
  ['src/assembly.js', readFileSync(here('./src/assembly.js'), 'utf8')]
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
