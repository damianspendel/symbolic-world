import cytoscape from 'cytoscape'
import atlas from './atlas.json'
import families from './families.json'
import chrome from './chrome.json'
import summary from './summary.json'
import pending from './pending.json'
import method from './method.json'
import { assemble } from './assembly.js'
import { renderConcordance } from './concordance.js'
import './style.css'

// ---------------------------------------------------------------- constants ---
// R10.0 — colour resolves from :root, never from a literal in a component.
// Cytoscape's stylesheet cannot take CSS variables, so the values are read out
// of the document once at boot and handed to it; tokens.css remains the source.
const CSS = getComputedStyle(document.documentElement)
const T = name => CSS.getPropertyValue('--' + name).trim()
const LAYER = { spine: T('gold'), amplification: T('m-symbol'), bridge: T('m-substance'), structural: T('layer-structural') }
const LAYER_NOTE = {
  spine: 'A cited claim: one edge, one paragraph, one quote.',
  amplification: 'A parallel adduced to widen an image, not a relation asserted between the terms.',
  bridge: 'A link between two regions of the map.',
  structural: 'Scaffolding with no citation of its own.'
}
const CT_DESC = { 'jung-asserts': "Jung's own interpretive claim, in his own voice", 'jung-reports-parallel': 'a doctrine or tradition Jung reports without asserting it himself', 'jung-quotes-source': 'a named source Jung quotes' }

const META = atlas.meta
const FAMILY_ON = META.familyLayer.present
const FAM_BY_ID = Object.fromEntries(families.families.map(f => [f.id, f]))
const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches
// The mobile render profile. Gated on a coarse pointer OR a small viewport:
// coarse-pointer alone misses small laptops driving a touchscreen, and width
// alone misses a phone in landscape. Either signal turns the profile on, and
// nothing below changes on a desktop pointer at desktop width.
const MOBILE = window.matchMedia('(pointer: coarse)').matches || window.innerWidth <= 760

const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const $ = id => document.getElementById(id)
const labelOf = id => (atlas.nodes.find(n => n.id === id) || {}).label || id
const edgeData = id => atlas.edges.find(e => e.id === id)

// dispute history per current edge (key: "subject|relation|object") — loaded async
const DISPUTES = {}, CONFIRMS = {}, HUMANVAL = {}
const refresh = () => { const sel = cy.$(':selected'); if (sel.nonempty()) renderPanel(sel[0]) }
fetch('./validations.json').then(r => r.json()).then(d => {
  (d.validations || []).forEach(x => { HUMANVAL[x.key + '|' + x.volume + '|' + x.paragraph] = x }); refresh()
}).catch(() => {})
fetch('./disputes.json').then(r => r.json()).then(d => {
  d.disputes.forEach(x => (x.current_edges || []).forEach(k => { (DISPUTES[k] = DISPUTES[k] || []).push(x) })); refresh()
}).catch(() => {})
fetch('./confirmations.json').then(r => r.json()).then(d => {
  d.confirmations.forEach(x => (x.current_edges || []).forEach(k => { (CONFIRMS[k] = CONFIRMS[k] || []).push(x) })); refresh()
}).catch(() => {})
const page = (v, p) => atlas.pages[`${v}:${p}`]

// -------------------------------------------------------------------- graph ---
const cy = cytoscape({
  container: $('cy'),
  minZoom: 0.06, maxZoom: 12, wheelSensitivity: 0.45,
  // MOBILE RENDER PROFILE — measured on this build at 375px, publish day.
  //
  // hideEdgesOnViewport and textureOnViewport were both TRIED AND REJECTED. Each
  // leaves the last frame of a PROGRAMMATIC camera move (the landing, focusOn,
  // fitLanding, enterAtlas) on screen with the 1180 edges still hidden: the phone
  // shows a field of unconnected dots, which reads as a broken page rather than a
  // fast one. Cytoscape restores them after a user gesture but not after an
  // animated viewport change we issued, and a debounced forceRender() does not
  // clear it either — it repaints without invalidating the cached frame.
  // Both stay off until they can be tested on real hardware with a gesture
  // profile; a blank-looking graph on the primary traffic segment is not a
  // trade worth making today.
  // R13 — hideEdgesOnViewport ON for touch devices: pinch/pan redraws 1218
  // edges per frame otherwise, and that is the whole difference between janky
  // and smooth on a phone. The stale-frame failure that got this rejected on
  // publish day (programmatic moves leaving a dot field) is neutralized in the
  // settle-repaint below, which draws one full frame WITH edges after every
  // viewport change, gesture or programmatic. textureOnViewport stays off.
  hideEdgesOnViewport: MOBILE,
  textureOnViewport: false,
  // Kept, and both unconditionally safe: a 2-3x fragment reduction on a
  // high-density phone screen, and the cheap edge style below.
  ...(MOBILE ? { pixelRatio: 1 } : {}),
  elements: [
    ...atlas.clusters.map(c => ({ data: { id: c.id, label: c.label, kind: 'region', color: c.color }, classes: 'pre' })),
    ...atlas.nodes.map(n => ({ data: { id: n.id, label: n.label, type: n.type, tradition: n.tradition, register: n.register, color: n.color, parent: n.cluster }, position: { x: n.x, y: n.y }, classes: 'pre' })),
    ...atlas.edges.map(e => ({ data: { id: e.id, source: e.source, target: e.target, relation: e.relation, layer: e.layer, volumes: e.volumes, fam: e.family ? e.family.value : '', famState: e.family ? e.family.state : '' }, classes: e.layer + ' pre' }))
  ],
  layout: { name: 'preset' },
  style: [
    { selector: 'node[kind = "region"]', style: {
      'background-color': 'data(color)', 'background-opacity': 0.05,
      'border-color': 'data(color)', 'border-opacity': 0.3, 'border-width': 1.5,
      'shape': 'round-rectangle', 'padding': '80px',
      'label': 'data(label)', 'text-valign': 'top', 'text-halign': 'center', 'text-margin-y': 10,
      'font-family': 'Hoefler Text, Iowan Old Style, Palatino, Georgia, serif', 'font-size': 26, 'font-style': 'italic',
      'color': 'data(color)', 'text-opacity': 0.8, 'min-zoomed-font-size': 5, 'events': 'no', 'z-compound-depth': 'bottom'
    }},
    { selector: 'node[kind != "region"]', style: {
      'background-color': 'data(color)', 'border-color': 'data(color)', 'border-width': 2,
      'width': MOBILE ? 26 : 20, 'height': MOBILE ? 26 : 20, 'label': 'data(label)', 'color': T('ink-label'),
      'font-family': 'Iowan Old Style, Palatino, Georgia, serif', 'font-size': 11,
      'text-valign': 'bottom', 'text-margin-y': 3, 'text-wrap': 'wrap', 'text-max-width': 120,
      'text-outline-color': T('ground'), 'text-outline-width': 2, 'min-zoomed-font-size': 10
    }},
    { selector: 'node:selected', style: { 'border-color': T('sel'), 'border-width': 4, 'color': T('ink-bright'), 'width': 26, 'height': 26, 'min-zoomed-font-size': 0 }},
    { selector: 'edge', style: Object.assign({
      'width': 1.5, 'curve-style': 'straight', 'line-color': T('edge-idle'),
      'target-arrow-color': T('edge-idle'), 'arrow-scale': 0.65
    }, MOBILE
      // opaque + no arrows: the docs put opaque-with-arrows at >2x the speed of
      // semitransparent-with-arrows, and at mobile zoom the arrowheads are
      // sub-pixel decoration anyway
      ? { 'opacity': 1, 'target-arrow-shape': 'none' }
      : { 'opacity': 0.8, 'target-arrow-shape': 'triangle' })},
    { selector: 'edge.spine', style: { 'line-color': LAYER.spine, 'target-arrow-color': LAYER.spine }},
    { selector: 'edge.amplification', style: { 'line-color': LAYER.amplification, 'target-arrow-color': LAYER.amplification, 'line-style': 'dashed' }},
    { selector: 'edge.bridge', style: { 'line-color': LAYER.bridge, 'target-arrow-color': LAYER.bridge, 'width': 2.6 }},
    { selector: 'edge.structural', style: { 'line-color': LAYER.structural, 'target-arrow-color': LAYER.structural, 'line-style': 'dotted' }},
    { selector: 'edge:selected', style: { 'width': 4, 'line-color': T('sel'), 'target-arrow-color': T('sel'), 'opacity': 1 }},
    { selector: '.faded', style: { 'opacity': 0.06, 'text-opacity': 0.04 }},
    { selector: 'node:selected.faded, node.nbr', style: { 'opacity': 1, 'text-opacity': 1, 'min-zoomed-font-size': 0 }},
    // R0.4 — a node brightening means it is cited by the clause being read
    { selector: 'edge.lit', style: { 'opacity': 1, 'width': 4, 'line-color': T('hi'), 'target-arrow-color': T('hi'), 'z-index': 99 }},
    { selector: 'node.lit', style: { 'opacity': 1, 'text-opacity': 1, 'border-color': T('hi'), 'border-width': 5, 'width': 26, 'height': 26, 'min-zoomed-font-size': 0, 'z-index': 99 }},
    { selector: 'node.ignite', style: { 'border-color': T('hi'), 'border-width': 7, 'width': 30, 'height': 30, 'min-zoomed-font-size': 0 }},
    { selector: '.hidden', style: { 'display': 'none' }},
    { selector: '.pre', style: { 'display': 'none' }},
    // Regions are COMPOUND PARENTS, and cytoscape hides a parent's children when
    // the parent is not visible — `display: none` and `opacity: 0` both count.
    // A region waiting its turn was therefore hiding every node inside it, and
    // the reveal rendered as black until the regions resolved at 82%. So a
    // waiting region stays visible and paints NOTHING instead: its own fill,
    // border and label go transparent while its opacity stays 1, which is local
    // to the region and leaves its children to draw normally.
    { selector: 'node[kind = "region"].pre', style: {
      'display': 'element', 'opacity': 1,
      'background-opacity': 0, 'border-opacity': 0, 'text-opacity': 0, 'events': 'no'
    }}
  ]
})

// Dev-only handle for inspecting the viewport from the console. Vite strips this
// from production builds, so nothing is exposed on the published artifact.
const DEV = !!(import.meta.env && import.meta.env.DEV)
// Two clocks cannot be checked against each other by eye. DEV builds record when
// each stage actually fired, measured from the moment the sequence began, so the
// timings can be read off rather than guessed at from screenshots.
const trace = { boot: 0, clauseMs: [], narrationMs: 0, flightMs: 0, revealMs: 0 }
if (DEV) {
  window.__cy = cy
  window.__trace = trace
  // dev-only: lets the landing trajectory be measured directly, since a hidden
  // tab suspends both requestAnimationFrame and cytoscape's own animations and
  // the painted travel cannot be sampled there
  window.__landing = {
    clocks: () => ({ EMERGENCE_MS, IGNITE_HOLD_MS, IGNITE_ZOOM, CLAUSE_FIRST_MS, CLAUSE_STEP_MS, VEIL_FROM_MS }),
    rest: () => landingTarget(),
    dest: () => landingTarget(60, { includeUnrevealed: true }),
    // the camera trajectory as a function of milliseconds since the flight began
    at: (ms, anchor) => {
      const d = landingTarget(60, { includeUnrevealed: true })
      if (!d) return null
      const p = Math.max(0, Math.min(1, (ms - IGNITE_HOLD_MS) / (EMERGENCE_MS - IGNITE_HOLD_MS)))
      const e = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2
      const z = Math.exp(Math.log(IGNITE_ZOOM) * (1 - e) + Math.log(d.zoom) * e)
      const sx0 = cy.width() / 2 + landingOffset(), sy0 = cy.height() / 2
      const sx1 = d.zoom * anchor.x + d.pan.x, sy1 = d.zoom * anchor.y + d.pan.y
      const sx = sx0 + (sx1 - sx0) * e, sy = sy0 + (sy1 - sy0) * e
      return { p, zoom: z, pan: { x: sx - z * anchor.x, y: sy - z * anchor.y } }
    }
  }
}

// Belt and braces on mobile: repaint once the viewport settles, so a gesture
// that ends mid-animation cannot leave edges hidden.
if (MOBILE) {
  let repaint
  cy.on('viewport', () => {
    clearTimeout(repaint)
    repaint = setTimeout(() => {
      // draw one full frame with edges regardless of how the move was made:
      // flip the renderer's flag off for a single forced render, restore it.
      const r = cy.renderer()
      const keep = r.hideEdgesOnViewport
      r.hideEdgesOnViewport = false
      cy.forceRender()
      r.hideEdgesOnViewport = keep
    }, 140)
  })
}

// ------------------------------------------------- selection & permalinks ---
let routing = false
function setHash(h) { routing = true; location.hash = h; setTimeout(() => { routing = false }, 0) }

// Item 13 (editorial ruling, 2026-08-13) — the selection is reflected into the
// URL, not pushed onto history: a reader clicking through twenty nodes should
// not have to press Back twenty times to leave. replaceState does not fire
// hashchange either, so reflecting a selection cannot re-enter the router.
// #/atlas?node=<id> is the form the atlas emits; the older #/n/<id> and
// #/e/<id> permalinks are still read on arrival, so links already copied out of
// the site keep working.
function routeOf(hash) {
  const raw = (hash || '').replace(/^#/, '')
  const [path, query] = raw.split('?')
  return { path: '#' + path, params: new URLSearchParams(query || '') }
}
function reflect(hash) {
  if (location.hash === hash) return
  history.replaceState(null, '', hash || location.pathname + location.search)
}
function reflectSelection(kind, id) {
  reflect(id ? `#/atlas?${kind}=${encodeURIComponent(id)}` : '#/atlas')
}

// R9.2 — land on the REGION, not on the edge. Fit the given elements with
// generous padding and then cap the zoom, so a two-node selection does not fill
// the screen at 12× and lose every landmark around it.
function focusOn(eles, { padding = 150, cap = 0.95, duration = 560 } = {}) {
  if (!eles || !eles.length) return
  const bb = eles.boundingBox()
  const w = cy.width(), h = cy.height()
  if (!bb.w || !bb.h || !w || !h) return
  let z = Math.min((w - 2 * padding) / bb.w, (h - 2 * padding) / bb.h)
  z = Math.max(cy.minZoom(), Math.min(z, cap))
  const target = { zoom: z, pan: { x: w / 2 - z * (bb.x1 + bb.w / 2), y: h / 2 - z * (bb.y1 + bb.h / 2) } }
  cy.stop()
  if (REDUCED) { cy.viewport(target); return }
  cy.animate(target, { duration, easing: 'ease-out', queue: false })
  // rAF-driven animations do not run in a background tab; land there anyway
  setTimeout(() => { if (Math.abs(cy.zoom() - z) > 0.01) cy.viewport(target) }, duration + 400)
}
// The neighbourhood of a selection: the elements plus their first-degree context.
const around = eles => eles.reduce((acc, el) => acc.union(el.isNode() ? el.closedNeighborhood() : el.connectedNodes().union(el)), cy.collection())

// R8.3 / R9.8 — the evidence-mix strip, rendered from build-time counts. Used by
// the Concordance and by every node selection panel.
function mixStrip(id, { compact = false } = {}) {
  const m = (atlas.concordance.mix || {})[id]
  if (!m || !m.total) return ''
  const pct = Math.round((m.alchemical / m.total) * 100)
  const vols = Object.entries(m.volumes).sort((a, b) => b[1] - a[1]).map(([v, n]) => `CW ${v} ×${n}`).join(' · ')
  return `<div class="mix${compact ? ' mix-compact' : ''}">
    <div class="mix-bar">
      <span style="width:${pct}%;background:var(--m-substance)" title="alchemical: CW 12, 13, 14"></span>
      <span style="width:${100 - pct}%;background:var(--m-concept)" title="the rest of the corpus"></span>
    </div>
    <div class="mix-l">${compact ? '' : `<b>${esc(labelOf(id))}</b> — `}${pct}% of ${m.total} reference${m.total === 1 ? '' : 's'} alchemical${compact ? '' : `, ${100 - pct}% from the rest of the corpus. ${esc(vols)}`}</div>
    ${compact ? '' : `<div class="mix-legend"><span><i style="background:var(--m-substance)"></i>CW 12/13/14</span><span><i style="background:var(--m-concept)"></i>everything else</span></div>`}
  </div>`
}

// R9.2 — the selection persists into the atlas because it IS the evidence view.
// It is therefore made visible, and given a way out, as a chip in the chip row.
let SELECTION = null

function selectNode(node, { hash = true } = {}) {
  closeMode()
  cy.$(':selected').unselect(); node.select()
  cy.elements().addClass('faded'); cy.nodes('[kind = "region"]').removeClass('faded')
  const hood = node.closedNeighborhood()
  hood.removeClass('faded'); hood.nodes().addClass('nbr')
  SELECTION = { kind: 'node', id: node.id(), label: node.data('label') }
  renderPanel(node); drawChips()
  if (hash) reflectSelection('node', node.id())
}
function selectEdge(edge, { hash = true } = {}) {
  closeMode()
  cy.$(':selected').unselect(); edge.select()
  cy.elements().addClass('faded'); cy.nodes('[kind = "region"]').removeClass('faded')
  edge.removeClass('faded'); edge.connectedNodes().removeClass('faded').addClass('nbr')
  const e = edgeData(edge.id())
  SELECTION = { kind: 'edge', id: edge.id(), label: e ? `${labelOf(e.source)} ${e.relation} ${labelOf(e.target)}` : edge.id() }
  renderPanel(edge); drawChips()
  if (hash) reflectSelection('edge', edge.id())
}
function clearSelection() {
  cy.$(':selected').unselect(); cy.elements().removeClass('faded nbr lit')
  $('panel').classList.add('hidden')
  SELECTION = null
  if (typeof drawChips === 'function') drawChips()
  // clearing the selection clears the parameter, and leaves the route alone
  const here = routeOf(location.hash)
  if (here.params.has('node') || here.params.has('edge')) reflectSelection(null, null)
  else if (here.path.startsWith('#/n/') || here.path.startsWith('#/e/')) setHash('')
}
cy.on('tap', 'node[kind != "region"]', e => selectNode(e.target))
cy.on('tap', 'edge', e => selectEdge(e.target))
cy.on('tap', e => { if (e.target === cy) clearSelection() })

function copyLinkButton(hash) {
  return `<button class="copy-link" data-hash="${esc(hash)}" title="A permalink to this selection">copy link</button>`
}
function wireCopyLinks(root) {
  root.querySelectorAll('.copy-link').forEach(b => b.addEventListener('click', ev => {
    ev.stopPropagation()
    const url = location.origin + location.pathname + b.dataset.hash
    navigator.clipboard.writeText(url).then(() => {
      const t = b.textContent; b.textContent = 'copied ✓'; setTimeout(() => { b.textContent = t }, 2200)
    }).catch(() => { b.textContent = url })
  }))
}

// --------------------------------------------------------- R3/R4 · family ---
// Three states, never conflated, each with a one-line explanation on hover.
// When the family layer has not merged, nothing family-related is rendered at
// all — an empty chip would read as "no family applies", which is a different
// claim from "not yet assigned".
function familyChip(e) {
  if (!FAMILY_ON) return ''
  const f = e.family
  if (!f) return `<button class="chip chip-unclassified" data-fam="" title="${esc(families.state_note.absent)}">unassigned</button>`
  const text = f.state === 'family' ? f.value
    : f.state === 'pending' ? 'pending review'
    : f.state === 'not-a-relation' ? 'not a relation'
    : 'no family'
  return `<button class="chip chip-${f.state}" data-fam="${esc(f.value)}" title="${esc(families.state_note[f.state] || '')}">${esc(text)}</button>`
}

function openFamily(value) {
  const p = $('family-panel')
  const fam = FAM_BY_ID[value]
  closeMode()
  if (!fam) {
    const m = String(value || '').match(/^unclassified\(([^)]+)\)$/)
    const state = value === 'not-a-relation' ? 'not-a-relation' : m && m[1] === 'pending-adjudication' ? 'pending' : m ? 'unclassified' : 'absent'
    p.innerHTML = `<button class="panel-close" id="fam-close">×</button>
      <div class="p-type">Administrative class</div>
      <h2>${esc(value || 'no family layer')}</h2>
      <p>${esc(families.state_note[state] || '')}</p>
      <h3>Why this class exists</h3>
      <p>The vocabulary keeps two administrative classes beside the families, so that
      “not yet judged” and “no family applies” are never the same record. Both are
      counted and reported; neither is hidden.</p>
      <p><a href="${esc(families.doc_url)}">The complete definitions document →</a></p>
      ${familyIndexHTML()}`
  } else {
    p.innerHTML = `<button class="panel-close" id="fam-close">×</button>
      <div class="p-type">Relation family ${fam.n} of ${families.families.length} · ${esc(families.version)}</div>
      <h2>${esc(fam.name)}</h2>
      ${fam.added ? `<p class="p-count">${esc(fam.added)}</p>` : ''}
      <p>${fam.definition_html}</p>
      ${fam.boundary_html ? `<h3>Boundary</h3><p>${fam.boundary_html}</p>` : ''}
      ${fam.seeds.length ? `<h3>Seed examples</h3>${fam.seeds.map(s => `<div class="fam-seed"><code>${esc(s.text)}</code><span class="cite">${esc(s.cite ? 'CW ' + s.cite : '')}</span></div>`).join('')}` : ''}
      ${fam.notes.map(n => `<h3>${esc(n.label)}</h3><p>${n.html}</p>`).join('')}
      ${FAMILY_ON ? `<p><button class="chip" id="fam-filter">filter the graph to ${esc(fam.name)}</button></p>` : `<p class="p-count">No edge carries a family in this build, so this family cannot be filtered yet. The definitions are binding; the assignment pass has not merged.</p>`}
      <p><a href="${esc(families.doc_url)}">The complete definitions document →</a></p>
      ${familyIndexHTML()}`
  }
  p.classList.remove('hidden')
  $('fam-close').addEventListener('click', () => { p.classList.add('hidden'); if (location.hash.startsWith('#/family/')) setHash('') })
  p.querySelectorAll('[data-open-fam]').forEach(b => b.addEventListener('click', () => openFamily(b.dataset.openFam)))
  const fp = $('fam-page')
  if (fp) fp.addEventListener('click', () => { p.classList.add('hidden'); openFamiliesPage() })
  const ff = $('fam-filter')
  if (ff) ff.addEventListener('click', () => { SEL.family.clear(); SEL.family.add(value); applyFilters(); p.classList.add('hidden') })
  setHash('#/family/' + value)
}
function familyIndexHTML() {
  return `<h3>The vocabulary</h3>
    <p><button class="chip" id="fam-page">open the full vocabulary page →</button></p>
    <div class="fam-index">${families.families
      .map(f => `<button class="chip" data-open-fam="${esc(f.id)}">${esc(f.name)}</button>`).join('')}</div>`
}

// ------------------------------------------------------- the evidence view ---
function refBlock(e, r, key) {
  const dHist = DISPUTES[key] || [], cHist = CONFIRMS[key] || []
  const hv = HUMANVAL[key + '|' + r.volume + '|' + r.paragraph]
  const ragClass = (dHist.length || (hv && hv.support !== 'supported')) ? 'rag-red' : (hv ? 'rag-green' : 'rag-amber')
  const ragTitle = ragClass === 'rag-green' ? 'Human-validated' : ragClass === 'rag-red' ? 'Disputed / contested' : 'Machine-checked (awaiting human validation)'
  const pg = page(r.volume, r.paragraph)
  const cite = `<span class="cite-toggle" title="Show verification record">CW ${esc(r.volume)} §${esc(r.paragraph)}${r.verified ? ' <span class="vcheck">✓</span>' : ''}${dHist.length ? ' <span class="dmark" title="This edge has public dispute history">⚖</span>' : ''} <span class="rag ${ragClass}" title="${ragTitle}">●</span></span>`
  const report = (extra) => encodeURIComponent(JSON.stringify(Object.assign({
    edge: `${e.source} —${e.relation}→ ${e.target}`,
    citation: `CW ${r.volume} §${r.paragraph}` + (pg ? ` (Bollingen p.${pg})` : ''),
    quote: r.quote, claim_type: r.claim_type || ''
  }, extra)))
  return `<div class="ref">
    <div class="conn-h"><span></span><span class="cite">${cite}</span></div>
    <blockquote>${esc(r.quote)}</blockquote>
    <div class="conn-f">
      ${r.claim_type ? `<span class="prov">${esc(r.claim_type)}${r.source ? ' · ' + esc(r.source) : ''}</span>` : ''}
      ${pg ? `<span class="pageref">Bollingen · p.${pg}</span>` : ''}
      ${r.confidence ? `<span class="conf conf-${esc(r.confidence)}" title="How firmly the paragraph carries the claim, recorded at proposal and checked at the gate">confidence: ${esc(r.confidence)}</span>` : ''}
    </div>
    <div class="evidence hidden">
      <div><b>Claim type:</b> ${esc(r.claim_type || '—')} — ${esc(CT_DESC[r.claim_type] || '')}</div>
      ${r.source ? `<div><b>Source:</b> ${esc(r.source)}</div>` : ''}
      <div><b>Confidence:</b> ${esc(r.confidence || '—')}</div>
      <div><b>Verification:</b> ${r.verified ? `passed independent review (${esc(r.verified_by || 'gate')}, ${esc(r.verified_date || '')}) — the full paragraph was checked for support, direction, quote fidelity, and attribution` : 'not yet independently reviewed'}</div>
      ${r.crossvendor_checked ? `<div><b>Cross-vendor audit:</b> ${esc(r.crossvendor_checked)}</div>` : ''}
      ${r.correction_note ? `<div><b>Correction:</b> ${esc(r.correction_note)}</div>` : ''}
      ${r.vocabulary_note ? `<div><b>Vocabulary note:</b> ${esc(r.vocabulary_note)}</div>` : ''}
      <div><b>Status:</b> <span class="${ragClass}">●</span> ${ragTitle}${hv ? ` (${esc(hv.date)}${hv.voice !== 'voice-correct' ? '; human corrected the voice label' : ''})` : ''}</div>
      <div><b>Check it yourself:</b> CW ${esc(r.volume)} §${esc(r.paragraph)}${pg ? `, Bollingen p.${pg}` : ''}</div>
      ${dHist.map(x => `<div class="dhist"><b>Disputed</b> (${esc(x.date)}, ${esc(x.outcome)}): ${esc(x.objection)} <span class="dhist-res">→ ${esc(x.resolution)}</span> <a href="/disputes" class="dhist-link">full log</a></div>`).join('')}
      ${cHist.length ? `<div class="chist"><b>Reader-confirmed ×${cHist.length}</b> — a human checked the cited paragraph${cHist.length > 1 ? 's' : ''} (${cHist.map(x => esc(x.date)).join(', ')}) <a href="/disputes" class="dhist-link">log</a></div>` : ''}
      <button class="confirm-btn" data-report="${report({})}">Confirm this edge — I checked the book</button>
      <button class="dispute-btn" data-report="${report({ verified_by: r.verified_by || '', verified_date: r.verified_date || '' })}">Dispute this edge — copy report</button>
    </div>
  </div>`
}

// R3.4 — the verbatim relation is the verified claim and stays primary; the
// normalized verb phrase and its qualifiers are shown as the layer above it.
function normalizedBlock(e) {
  const rn = e.relation_normalized
  if (!rn) return ''
  const q = Object.entries(rn.qualifiers || {})
  return `<span class="rel-norm"><b>normalized:</b> ${esc(rn.relation)}</span>
    ${q.length ? `<div class="qual">${q.map(([k, v]) => `<b>${esc(k)}:</b> ${esc(v)}`).join('<br>')}</div>` : ''}`
}

function renderPanel(el) {
  const p = $('panel')
  p.innerHTML = el.isEdge() ? edgePanel(el) : nodePanel(el)
  p.classList.remove('hidden')
  wirePanel(p)
}

function nodePanel(node) {
  const id = node.id()
  const conn = node.connectedEdges().filter(e => !e.hasClass('hidden'))
  const rows = conn.map(ce => {
    const e = edgeData(ce.id()); if (!e) return ''
    const other = e.source === id ? e.target : e.source
    const dir = e.source === id
      ? `<span class="rel">${esc(e.relation)} →</span> ${esc(labelOf(other))}`
      : `${esc(labelOf(other))} <span class="rel">→ ${esc(e.relation)}</span>`
    const r = e.refs[0]
    return `<div class="conn" data-node="${esc(other)}" data-edge="${esc(e.id)}">
      <div class="conn-h"><span>${dir}</span></div>
      ${normalizedBlock(e)}
      <div class="conn-f">${familyChip(e)}${e.refs.length > 1 ? `<span class="pageref">${e.refs.length} citations</span>` : ''}</div>
      ${r ? refBlock(e, r, e.key) : '<div class="qual">No citation on this edge — structural only.</div>'}
    </div>`
  }).join('')
  return `<div class="p-head"><div><div class="p-type">${esc(node.data('type'))}${node.data('tradition') ? ' · ' + esc(node.data('tradition')) : ''}</div></div>${copyLinkButton('#/n/' + id)}</div>
    <h2>${esc(node.data('label'))}</h2>
    <div class="p-count">${conn.length} connection${conn.length !== 1 ? 's' : ''} — click a link to open it, click the far term to walk on</div>
    ${mixStrip(id)}${rows}`
}

function edgePanel(edge) {
  const e = edgeData(edge.id())
  if (!e) return '<div class="p-count">This edge is not in the loaded graph.</div>'
  return `<div class="p-head"><div class="p-type">One claim · ${esc(e.layer)}</div>${copyLinkButton('#/e/' + e.id)}</div>
    <p class="claim-line"><span class="walk" data-node="${esc(e.source)}">${esc(labelOf(e.source))}</span>
      <em>${esc(e.relation)}</em>
      <span class="walk" data-node="${esc(e.target)}">${esc(labelOf(e.target))}</span></p>
    ${normalizedBlock(e)}
    <div class="conn-f" style="margin:0.6rem 0">${familyChip(e)}${e.confidence ? `<span class="conf conf-${esc(e.confidence)}">confidence: ${esc(e.confidence)}</span>` : ''}</div>
    <div class="p-count">${e.refs.length} citation${e.refs.length !== 1 ? 's' : ''}</div>
    ${e.refs.map(r => `<div class="conn">${refBlock(e, r, e.key)}</div>`).join('')}`
}

function wirePanel(p) {
  wireCopyLinks(p)
  p.querySelectorAll('.conn[data-edge]').forEach(el => el.addEventListener('click', () => {
    const ed = cy.getElementById(el.dataset.edge); if (ed.nonempty()) selectEdge(ed)
  }))
  p.querySelectorAll('.walk, .ctag').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation()
    const n = cy.getElementById(el.dataset.node)
    if (n && n.nonempty()) { selectNode(n); focusOn(around(n)) }
  }))
  p.querySelectorAll('[data-fam]').forEach(el => el.addEventListener('click', ev => { ev.stopPropagation(); openFamily(el.dataset.fam) }))
  p.querySelectorAll('.evidence').forEach(el => el.addEventListener('click', ev => ev.stopPropagation()))
  p.querySelectorAll('.cite-toggle').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation()
    const box = el.closest('.ref').querySelector('.evidence')
    if (box) box.classList.toggle('hidden')
  }))
  p.querySelectorAll('.confirm-btn').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation()
    const d = JSON.parse(decodeURIComponent(el.dataset.report))
    copyReport(el, [
      'CONFIRMATION REPORT — The Symbolic World',
      `Edge: ${d.edge}`, `Citation: ${d.citation}`, `Quote: "${d.quote}"`, `Claim type: ${d.claim_type}`, '',
      'I checked the cited paragraph in the Collected Works and confirm the edge.',
      'Edition checked: [fill in]', 'Notes (optional): [anything the record should say]', '',
      'Submit at: https://github.com/damianspendel/symbolic-world/issues/new?template=confirm.yml',
      'Confirmations become part of the edge’s public verification record.'
    ], 'Report copied ✓ — submit via the confirm template', 'Confirm this edge — I checked the book')
  }))
  p.querySelectorAll('.dispute-btn').forEach(el => el.addEventListener('click', ev => {
    ev.stopPropagation()
    const d = JSON.parse(decodeURIComponent(el.dataset.report))
    copyReport(el, [
      'DISPUTE REPORT — The Symbolic World',
      `Edge: ${d.edge}`, `Citation: ${d.citation}`, `Quote: "${d.quote}"`, `Claim type: ${d.claim_type}`,
      `Verified by: ${d.verified_by} (${d.verified_date})`, '',
      'My objection (what the cited paragraph actually says):', '  [describe here — please quote the paragraph]', '',
      'Submit at: https://github.com/damianspendel/symbolic-world/issues/new?template=dispute.yml',
      '(use the dispute template). Disputed edges are re-reviewed with this objection',
      'attached; outcomes are published at https://symbolicworld.observer/disputes'
    ], 'Report copied ✓ — submit at github.com/damianspendel/symbolic-world/issues', 'Dispute this edge — copy report')
  }))
}
function copyReport(el, lines, done, back) {
  navigator.clipboard.writeText(lines.join('\n')).then(() => {
    el.textContent = done; setTimeout(() => { el.textContent = back }, 3000)
  })
}

// ------------------------------------------- R5.5 · filters without a panel ---
// The persistent checkbox column is gone. Filtering happens in two places, both
// of which say something about the data on their own: the works bar along the
// bottom (coverage by volume) and search-token chips beside the field where the
// reader typed them.
//
// One selection set per facet. An EMPTY set means "no constraint on this axis",
// which is what lets a filter be expressed by adding a chip rather than by
// unchecking everything else.
const SEL = { volume: new Set(), family: new Set(), voice: new Set(), layer: new Set() }
const facetEmpty = () => !SEL.volume.size && !SEL.family.size && !SEL.voice.size && !SEL.layer.size

const famLabel = v => v === '' ? 'unassigned'
  : v === 'not-a-relation' ? 'not a relation'
  : v === 'unclassified(pending-adjudication)' ? 'pending review'
  : v === 'unclassified(no-family)' ? 'no family'
  : v === 'unclassified(text-undecided)' ? 'text undecided'
  : v.startsWith('unclassified(') ? 'unclassified · ' + v.slice(13, -1) : v
const famState = v => v === '' ? 'absent'
  : v === 'not-a-relation' ? 'not-a-relation'
  : v === 'unclassified(pending-adjudication)' ? 'pending'
  : v.startsWith('unclassified(') ? 'unclassified' : 'family'

function applyFilters() {
  cy.batch(() => {
    cy.edges().forEach(ce => {
      const e = edgeData(ce.id())
      const okVol = !SEL.volume.size || ce.data('volumes').some(v => SEL.volume.has(v))
      const okLayer = !SEL.layer.size || SEL.layer.has(ce.data('layer'))
      const okFam = !SEL.family.size || (e && e.family && SEL.family.has(e.family.value))
      const okVoice = !SEL.voice.size || (e && e.refs.some(r => SEL.voice.has(r.claim_type)))
      ce.toggleClass('hidden', !(okVol && okLayer && okFam && okVoice))
    })
    cy.nodes('[kind != "region"]').forEach(n => n.toggleClass('hidden', !n.connectedEdges().some(e => !e.hasClass('hidden'))))
    cy.nodes('[kind = "region"]').forEach(r => r.toggleClass('hidden', r.children().every(c => c.hasClass('hidden'))))
  })
  drawChips(); drawWorks(); updateStats()
}

// ---- the works bar -----------------------------------------------------------
// Width and brightness are both the reference count, taken from atlas.json at
// build time. Clicking a segment toggles that volume, so the bar and the volume
// chips are two views of one selection, never two competing controls.
const VOLS = META.volumes || []
const maxRefs = Math.max(1, ...VOLS.map(v => v.references))
const worksEl = $('works')
function drawWorks() {
  worksEl.classList.toggle('filtered', SEL.volume.size > 0)
  worksEl.querySelectorAll('.work').forEach(b => b.classList.toggle('on', SEL.volume.has(b.dataset.vol)))
}
worksEl.innerHTML = VOLS.map(v => {
  const share = v.references / maxRefs
  return `<button class="work${share < 0.3 ? ' narrow' : ''}" data-vol="${esc(v.volume)}"
      style="flex:${v.references} 1 0;opacity:${(0.3 + 0.7 * share).toFixed(2)}"
      title="CW ${esc(v.volume)}${v.label ? ' · ' + esc(v.label) : ''} — ${v.references} references over ${v.edges} relations. Click to filter to this volume; click again to clear.">
      <span class="wl">CW ${esc(v.volume)}</span><span class="wn">${v.references} refs</span></button>`
}).join('') + `<span class="work-note">coverage by volume · ${META.counts.references} references</span>`
worksEl.querySelectorAll('.work').forEach(b => b.addEventListener('click', () => {
  toggleFacet('volume', b.dataset.vol)
}))

// ---- search-token chips ------------------------------------------------------
function toggleFacet(facet, value) {
  SEL[facet].has(value) ? SEL[facet].delete(value) : SEL[facet].add(value)
  applyFilters()
}
const VOICES = Object.keys(META.voices || {})
const chipsEl = $('chips')
function chipLabel(facet, value) {
  if (facet === 'volume') return 'CW ' + value
  if (facet === 'voice') return value
  if (facet === 'layer') return value
  return famLabel(value)
}
function drawChips() {
  const rows = []
  // R9.2 — the live selection reads as a chip, with an ✕ that releases it.
  if (SELECTION) rows.push(`<span class="tok tok-selection" title="The current selection — the evidence panel is showing it. ✕ releases it.">
    <span class="k">${SELECTION.kind === 'edge' ? 'claim' : 'symbol'}</span>${esc(SELECTION.label)}
    <button data-drop-selection title="Clear the selection">×</button></span>`)
  for (const facet of ['volume', 'family', 'voice', 'layer'])
    for (const value of SEL[facet])
      rows.push(`<span class="tok tok-${facet}" title="${esc(facetNote(facet, value))}">
        ${facet === 'layer' ? `<span class="sw" style="background:${LAYER[value] || T('muted')}"></span>` : ''}
        ${esc(chipLabel(facet, value))}<span class="n">${facetCount(facet, value)}</span>
        <button data-drop-facet="${facet}" data-drop-value="${esc(value)}" title="Remove this filter">×</button></span>`)
  chipsEl.innerHTML = rows.join('')
  chipsEl.querySelectorAll('[data-drop-facet]').forEach(b => b.addEventListener('click', () => {
    SEL[b.dataset.dropFacet].delete(b.dataset.dropValue); applyFilters()
  }))
  const ds = chipsEl.querySelector('[data-drop-selection]')
  if (ds) ds.addEventListener('click', clearSelection)
}
function facetCount(facet, value) {
  if (facet === 'volume') return (VOLS.find(v => v.volume === value) || {}).references || 0
  if (facet === 'layer') return (META.layers || {})[value] || 0
  if (facet === 'voice') return (META.voices || {})[value] || 0
  return atlas.edges.filter(e => e.family && e.family.value === value).length
}
function facetNote(facet, value) {
  if (facet === 'volume') { const v = VOLS.find(x => x.volume === value) || {}; return `CW ${value}${v.label ? ' · ' + v.label : ''} — ${v.references || 0} references` }
  if (facet === 'layer') return LAYER_NOTE[value] || ''
  if (facet === 'voice') return CT_DESC[value] || ''
  return families.state_note[famState(value)] || ''
}

// A typed token becomes a filter on ↵. Everything the chip row can hold is
// recognised here, and nothing else is — an unrecognised query stays a search.
function tokenFor(raw) {
  const t = String(raw).trim()
  if (!t) return null
  const vm = t.replace(/[§¶]/g, ' ').match(/^cw\s*([0-9]+i*)$/i)
  if (vm && VOLS.some(v => v.volume === vm[1])) return { facet: 'volume', value: vm[1] }
  const n = norm(t)
  if (VOICES.some(v => norm(v) === n)) return { facet: 'voice', value: VOICES.find(v => norm(v) === n) }
  const lk = Object.keys(LAYER).find(l => norm(l) === n)
  if (lk) return { facet: 'layer', value: lk }
  const fam = atlas.edges.map(e => e.family && e.family.value).filter(Boolean)
  const fv = fam.find(v => norm(famLabel(v)) === n || norm(v) === n)
  if (fv) return { facet: 'family', value: fv }
  return null
}

// ----------------------------------------------------------------- search ---
// R5.3 — the same client-side record search web/public/ledger.html already runs
// over every reference: one lowercase blob per record, substring match, no index
// server and no fuzzy scoring to explain away a miss. Extended here to relations
// (verbatim and normalized), family names, quote text and citations.
const norm = s => String(s).toLowerCase().replace(/[§¶]/g, ' ').replace(/[-_]/g, ' ').replace(/\s+/g, ' ').trim()
const CITE_INDEX = new Map()
const RECORDS = []
for (const n of atlas.nodes) {
  RECORDS.push({ kind: 'node', id: n.id, s: norm([n.id, n.label, n.type, n.tradition, n.latin, n.register].join(' ')) })
}
for (const e of atlas.edges) {
  // R9.6 — fields are kept apart so a hit can say WHERE it matched. Full-record
  // search only reads as a feature if it can name the field it found you in.
  const f = {
    label: [labelOf(e.source), labelOf(e.target), e.source, e.target].join(' '),
    relation: [e.relation, e.relation_normalized ? e.relation_normalized.relation : ''].join(' '),
    qualifier: e.relation_normalized ? Object.values(e.relation_normalized.qualifiers || {}).join(' ') : '',
    family: e.family ? `${e.family.value} ${famLabel(e.family.value)}` : '',
    quote: e.refs.map(r => r.quote).join(' '),
    voice: e.refs.map(r => `${r.claim_type || ''} ${r.source || ''}`).join(' '),
    citation: e.refs.map(r => `cw ${r.volume} ${r.paragraph}`).join(' '),
    layer: `${e.layer} ${e.kind || ''}`
  }
  for (const r of e.refs) {
    const k = `${r.volume}:${r.paragraph}`
    if (!CITE_INDEX.has(k)) CITE_INDEX.set(k, [])
    CITE_INDEX.get(k).push(e.id)
  }
  RECORDS.push({ kind: 'edge', id: e.id, fields: Object.fromEntries(Object.entries(f).map(([k, v]) => [k, norm(v)])) })
}
const FIELD_LABEL = {
  label: 'symbol name', relation: 'relation', qualifier: 'qualifier', family: 'family',
  quote: 'quote', voice: 'voice', citation: 'citation', layer: 'layer', node: 'symbol name'
}

// ------------------------------------------------ R10.8 · the typeahead ------
// One suggestion index, grouped by kind. Families carry the first clause of
// their definition so the reader can tell symbolization from correspondence
// without opening anything.
const firstSentence = html => {
  const text = String(html).replace(/<[^>]+>/g, '')
  const m = text.match(/^(.{0,110}?)(?:[.;:]|$)/)
  return (m ? m[1] : text.slice(0, 110)).trim()
}
const SUGGESTIONS = [
  ...atlas.nodes.map(n => ({ kind: 'node', id: n.id, label: n.label, sub: n.type, s: norm(`${n.label} ${n.id} ${n.type}`) })),
  ...families.families.map(f => ({ kind: 'family', id: f.id, label: f.name, sub: firstSentence(f.definition_html), s: norm(f.name) })),
  ...[...new Set(atlas.edges.map(e => e.relation))].map(r => ({ kind: 'relation', id: r, label: r, sub: '', s: norm(r) })),
  ...(META.volumes || []).map(v => ({ kind: 'volume', id: v.volume, label: `CW ${v.volume}`, sub: v.label, s: norm(`cw ${v.volume} ${v.label}`) }))
]
const KIND_ORDER = ['node', 'family', 'relation', 'volume']
const KIND_LABEL = { node: 'symbols', family: 'families', relation: 'relations', volume: 'volumes' }

function suggestFor(q) {
  if (!q || q.length < 2) return []
  const hits = SUGGESTIONS.filter(s => s.s.includes(q))
  hits.sort((a, b) => (a.s.startsWith(q) ? 0 : 1) - (b.s.startsWith(q) ? 0 : 1) || a.label.length - b.label.length)
  const byKind = {}
  for (const h of hits) (byKind[h.kind] = byKind[h.kind] || []).push(h)
  const out = []
  for (const k of KIND_ORDER) for (const h of (byKind[k] || []).slice(0, 6)) out.push(h)
  return out.slice(0, 18)
}

// R10.8 — a match on a family or a node OPENS it; it does not merely filter.
function pickSuggestion(item) {
  if (!item) return
  if (item.kind === 'node') {
    const n = cy.getElementById(item.id)
    if (n.nonempty()) { enterAtlas(); closeMode(); selectNode(n); focusOn(around(n)) }
  } else if (item.kind === 'family') {
    openFamily(item.id)
  } else if (item.kind === 'volume') {
    enterAtlas(); closeMode(); SEL.volume.add(item.id); applyFilters()
  } else {
    enterAtlas(); closeMode()
    $('search').value = item.label
    runSearch(item.label)
  }
}

function attachTypeahead(input, { onPick }) {
  let box = $('typeahead')
  if (!box) { box = document.createElement('div'); box.id = 'typeahead'; box.className = 'hidden'; document.body.appendChild(box) }
  let items = [], cursor = -1

  const close = () => { box.classList.add('hidden'); cursor = -1 }
  const place = () => {
    const r = input.getBoundingClientRect()
    box.style.left = Math.max(8, Math.min(window.innerWidth - box.offsetWidth - 8, r.left)) + 'px'
    box.style.top = (r.bottom + 6) + 'px'
  }
  const render = () => {
    if (!items.length) { close(); return }
    let html = '', last = ''
    items.forEach((it, i) => {
      if (it.kind !== last) { html += `<div class="ta-group">${KIND_LABEL[it.kind]}</div>`; last = it.kind }
      html += `<button class="ta-item ${i === cursor ? 'on' : ''}" data-i="${i}">${esc(it.label)}
        ${it.sub ? `<span class="ta-sub">${esc(it.sub)}</span>` : ''}</button>`
    })
    box.innerHTML = html
    box.classList.remove('hidden')
    place()
    box.querySelectorAll('.ta-item').forEach(b => b.addEventListener('mousedown', ev => {
      ev.preventDefault(); onPick(items[Number(b.dataset.i)]); input.value = ''; close()
    }))
  }
  input.addEventListener('input', () => { items = suggestFor(norm(input.value)); cursor = -1; render() })
  input.addEventListener('blur', () => setTimeout(close, 120))
  input.addEventListener('keydown', ev => {
    if (box.classList.contains('hidden') || !items.length) return
    if (ev.key === 'ArrowDown') { ev.preventDefault(); cursor = (cursor + 1) % items.length; render() }
    else if (ev.key === 'ArrowUp') { ev.preventDefault(); cursor = (cursor - 1 + items.length) % items.length; render() }
    else if (ev.key === 'Escape') { close() }
    else if (ev.key === 'Enter' && cursor >= 0) {
      ev.preventDefault(); ev.stopPropagation()
      onPick(items[cursor]); input.value = ''; close()
    }
  }, true)
  window.addEventListener('resize', () => { if (!box.classList.contains('hidden')) place() })
}

const CITE_RE = /^cw\s*([0-9]+i*)\s*(?:§|para\.?|par\.?)?\s*([0-9]+)$/i
function runSearch(raw) {
  const hint = $('search-hint')
  // R10.8 bug — a second search appeared dead. Two causes, both fixed: the
  // previous search's selection stayed on (so the graph did not visibly change),
  // and the hint sat underneath the chip row that the selection had just
  // created. Release the prior selection first; the hint now stacks below.
  if (SELECTION) { cy.$(':selected').unselect(); $('panel').classList.add('hidden'); SELECTION = null; drawChips() }
  cy.elements().removeClass('faded nbr lit')
  const q = norm(raw)
  if (!q) { hint.classList.add('hidden'); return }

  // R5.5 — a query that names a facet offers itself as a chip. The offer is
  // shown, never taken automatically: the reader presses ↵ to filter.
  const tok = tokenFor(raw)
  if (tok) {
    hint.classList.remove('hidden')
    hint.innerHTML = `press ↵ to filter to <b>${esc(chipLabel(tok.facet, tok.value))}</b> — ${esc(facetNote(tok.facet, tok.value))}`
    return
  }

  // R5.2 — a citation jumps to the edges resting on that paragraph
  const cm = String(raw).trim().replace(/[§¶]/g, ' ').replace(/\s+/g, ' ').match(CITE_RE)
  let nodeIds = [], edgeIds = []
  const fieldHits = {}          // R9.6 — which field each hit came from
  const bump = k => { fieldHits[k] = (fieldHits[k] || 0) + 1 }
  if (cm) {
    edgeIds = CITE_INDEX.get(`${cm[1]}:${cm[2]}`) || []
    if (edgeIds.length) fieldHits.citation = edgeIds.length
  } else {
    for (const r of RECORDS) {
      if (r.kind === 'node') { if (r.s.includes(q)) { nodeIds.push(r.id); bump('label') }; continue }
      let hit = false
      for (const [field, text] of Object.entries(r.fields))
        if (text && text.includes(q)) { if (!hit) edgeIds.push(r.id); hit = true; bump(field) }
    }
  }

  const sel = cy.collection()
  nodeIds.forEach(id => sel.merge(cy.getElementById(id)))
  edgeIds.forEach(id => { const e = cy.getElementById(id); sel.merge(e); sel.merge(e.connectedNodes()) })

  const famHit = !FAMILY_ON && families.families.some(f => norm(f.name).includes(q))
  if (!sel.length) {
    hint.classList.remove('hidden')
    hint.innerHTML = famHit
      ? `no edges — <b>${esc(raw)}</b> is a defined family, but the family layer has not merged into this build`
      : `no match for “${esc(raw)}”`
    return
  }
  cy.elements().addClass('faded'); cy.nodes('[kind = "region"]').removeClass('faded')
  sel.removeClass('faded'); sel.nodes().addClass('nbr')
  hint.classList.remove('hidden')
  // R9.6 — name the field, so "why did this match?" never needs asking.
  const where = Object.entries(fieldHits).sort((a, b) => b[1] - a[1])
    .map(([k, n]) => `${n} matched in ${FIELD_LABEL[k] || k}`).join(' · ')
  hint.innerHTML = `${nodeIds.length} symbol${nodeIds.length === 1 ? '' : 's'} · ${edgeIds.length} relation${edgeIds.length === 1 ? '' : 's'}${famHit ? ' · family layer not merged' : ''}${where ? `<br><span style="color:var(--ink-dim)">${esc(where)}</span>` : ''}`
  if (nodeIds.length === 1 && !edgeIds.length) {
    const n = cy.getElementById(nodeIds[0]); selectNode(n); focusOn(around(n))
  } else if (!nodeIds.length && edgeIds.length === 1) {
    const e = cy.getElementById(edgeIds[0]); selectEdge(e); focusOn(around(e))
  } else {
    cy.animate({ fit: { eles: sel, padding: 80 } }, { duration: 400 })
  }
}
attachTypeahead($('search'), { onPick: pickSuggestion })
$('search').addEventListener('input', e => runSearch(e.target.value))
$('search').addEventListener('keydown', ev => {
  if (ev.key !== 'Enter') return
  const tok = tokenFor(ev.target.value)
  if (!tok) return
  ev.preventDefault()
  SEL[tok.facet].add(tok.value)
  ev.target.value = ''
  runSearch('')
  applyFilters()
})

// --------------------------------------------------- R9.4 · pages, not panels ---
// A whole feature gets a page and a route. Nothing important lives only in a
// sheet floating over the graph, and every page's "back" goes to #/atlas — the
// atlas as it stands, never the landing sequence again.
const modeEl = $('mode-panel')
// Item 20 — the layer is raised by the route and lowered only when the route
// leaves the panel class. Between two panel routes it is never lowered, so a
// swap cannot expose the graph however long the incoming view takes to build.
function raiseLayer() { document.documentElement.classList.add('route-panel') }
function lowerLayer() { document.documentElement.classList.remove('route-panel') }
function closeMode() { lowerLayer(); modeEl.classList.add('hidden') }
function goAtlas() {
  enterAtlas(); closeMode()
  $('family-panel').classList.add('hidden')
  setHash('#/atlas')
}
// R10.0 / R10.6 — the breadcrumb is emitted from ONE place, so every route gets
// the same control in the same position. R10.4 — and the same search field, in
// the same slot, with the same behaviour.
// Item 12 — every in-app route renders the SAME header the generated pages
// carry, from the template build-atlas.mjs emits. #mode-panel is a fixed,
// scrolling overlay that covers the topbar, so a route that drew its own bar
// showed the reader a different set of links in a different place, and one that
// scrolled away with the content. Rendered as the panel's first child, the
// shared header sticks against the panel's own scroll.
function pageBar({ where, search = false, extra = '' } = {}) {
  // Item 15 — the tools cluster is right-aligned by the shared rule, so an
  // in-app view's search sits where the atlas's search sits. It used to inherit
  // its position from a .page-bar spacer rule that went away with the bar, and
  // came out on the left.
  const tools = `${extra}
    ${search ? `<input class="std-search page-search" type="search" autocomplete="off" spellcheck="false"
        placeholder="A symbol, a relation, a quote, CW 14 §1…">` : ''}`
  const row2 = `<span class="where">${esc(where || '')}</span>` +
    (tools.trim() ? `<span class="hdr-tools">${tools}</span>` : '')
  return chrome.header.replace('{{BRAND_HREF}}', '#/atlas').replace('{{ROW2}}', row2)
}
// Every page-bar search is the same search: the same index, the same typeahead,
// the same Enter-selects. Pages that carry a record list also filter it live.
function wirePageSearch(rootEl, { localFilter } = {}) {
  const input = rootEl.querySelector('.page-search')
  if (!input) return
  attachTypeahead(input, { onPick: pickSuggestion })
  input.addEventListener('input', () => {
    if (localFilter) localFilter(norm(input.value))
  })
}

// Item 14 — the menu marks where you are on an in-app route too. The generated
// pages get their mark at build time; a route rendering the shared template got
// none, so concordance, method, families and the queue never lit gold. Marked
// here, at the one place every route passes through, rather than in each view.
const MENU_HREF = {
  '#/atlas': '/#/atlas',
  '#/concordance': '/#/concordance',
  '#/method': '/#/method',
  '#/families': '/families',
  '#/queue': '/families'        // R10.5 — the queue is a section of families
}
function markCurrent(root, href) {
  root.querySelectorAll('.topmenu a[aria-current]').forEach(a => a.removeAttribute('aria-current'))
  if (!href) return
  const link = root.querySelector(`.topmenu a[href="${href}"]`)
  if (link) link.setAttribute('aria-current', 'page')
}
// Item 16 — mount, then reveal. The panel is the one opaque surface over the
// atlas, so the order matters: fill it while it is still display:none, mark the
// menu, and only then show it. Revealing first and filling afterwards leaves a
// frame's worth of empty panel available to paint, and any future render that
// yields would put the live graph on screen under it.
function openPage(render, route = '') {
  // The layer goes up FIRST and stays up: opaque, viewport-covering, empty at
  // worst. `html.route-panel #mode-panel` outranks `.hidden`, so raising it does
  // not depend on the panel's own class — which is what lets the content still
  // be mounted before that class is cleared (item 16's mount-then-reveal), with
  // the layer already covering the graph either way.
  raiseLayer()
  enterAtlas(); $('family-panel').classList.add('hidden')
  modeEl.scrollTop = 0
  render()
  markCurrent(modeEl, MENU_HREF[route] || '')
  modeEl.classList.remove('hidden')
}
function openEdgeFromPage(id) {
  closeMode()
  const e = cy.getElementById(id)
  if (!e.nonempty()) return
  selectEdge(e)
  focusOn(around(e))
}
function openMethod() {
  openPage(() => {
    modeEl.innerHTML = `${pageBar({ where: 'about', search: true })}<div class="page method-page">` +
      `<div class="titleband"><p class="eyebrow">about</p><h1>The method</h1>` +
      `<p class="sub">How a claim gets into this graph, and what the checks do and do not cover.</p></div>` +
      `${method.html}</div>`
    modeEl.querySelector('[data-back]').addEventListener('click', goAtlas)
    wirePageSearch(modeEl)
  }, '#/method')
  setHash('#/method')
}
function openConcordance() {
  openPage(() => { renderConcordance(modeEl, atlas, { onOpenEdge: openEdgeFromPage, onBack: goAtlas, mixStrip, pageBar }); wirePageSearch(modeEl) }, '#/concordance')
  setHash('#/concordance')
}

// The whole vocabulary as a page. The per-edge chip still opens the in-context
// side panel (R3.3's progressive disclosure); this is the feature's front door.
// R7 — the review queue, served in small tranches rather than as a wall.
const TRANCHE = 12
let queueShown = TRANCHE

function openFamiliesPage({ scrollTo = '' } = {}) {
  openPage(() => {
    drawFamilies()
    // deterministic: assign the offset rather than relying on smooth scrolling,
    // which is rAF-driven and does not run in a background tab
    if (scrollTo) setTimeout(() => {
      const el = $(scrollTo)
      if (el) modeEl.scrollTop = el.offsetTop - 56
    }, 60)
  }, scrollTo === 'queue-section' ? '#/queue' : '#/families')
  setHash(scrollTo === 'queue-section' ? '#/queue' : '#/families')
}

// R10.5 — the review queue is a SECTION of Families, not a separate destination.
// It is the same subject: the queue is where a family assignment is still
// undecided, so it belongs beside the vocabulary that would decide it.
function drawFamilies() {
  const counts = {}
  atlas.edges.forEach(e => { if (e.family) counts[e.family.value] = (counts[e.family.value] || 0) + 1 })
  const queued = (pending.items || []).length
  modeEl.innerHTML = `
    ${pageBar({ where: 'families', search: true, extra: `<a class="back" href="${esc(families.doc_url)}">the full document →</a>` })}
    <div class="page">
      <div class="titleband"><p class="eyebrow">reference</p>
      <h1>The relation-family vocabulary</h1></div>
      <p class="lede2">${families.families.length} families, ${esc(families.version)}, quoted from <code>docs/FAMILY_DEFINITIONS.md</code> — never paraphrased. A family classifies what KIND of relation an edge asserts, per edge and in its paragraph context, never per relation string. ${FAMILY_ON ? `<b>${META.familyLayer.states.family || 0}</b> edges carry a family, <b>${META.familyLayer.states.pending || 0}</b> await a human ruling, <b>${META.familyLayer.states.unclassified || 0}</b> carry none.` : 'The assignment pass has not merged, so no edge carries a family yet.'}</p>

      <div class="fam-jump">
        <button class="chip" data-jump="queue-section">awaiting review <span class="badge-count">${queued}</span></button>
      </div>

      <div id="family-list">
      ${families.families.map(f => `<div class="qitem fam-card" data-fam-search="${esc(norm(f.name + ' ' + f.definition_html.replace(/<[^>]+>/g, '')))}">
        <div class="qedge"><b>${f.n}. ${esc(f.name)}</b>${counts[f.id] ? ` <span class="fam-count">${counts[f.id]} edges</span>` : ''}</div>
        <p class="fam-def">${f.definition_html}</p>
        ${f.boundary_html ? `<p class="fam-bound"><b>Boundary:</b> ${f.boundary_html}</p>` : ''}
        ${f.seeds.length ? `<div class="qarms">${f.seeds.map(sd => `<div><code>${esc(sd.text)}</code>${sd.cite ? ` — CW ${esc(sd.cite)}` : ''}</div>`).join('')}</div>` : ''}
        ${FAMILY_ON && counts[f.id] ? `<div style="margin-top:0.4rem"><button class="chip" data-fam-filter-go="${esc(f.id)}">filter the atlas to ${esc(f.name)}</button></div>` : ''}
      </div>`).join('')}
      </div>

      <h2 id="queue-section" style="margin-top:2.6rem">Awaiting review <span class="badge-count">${queued}</span></h2>
      ${queueBody()}
    </div>`
  modeEl.querySelector('[data-back]').addEventListener('click', goAtlas)
  modeEl.querySelectorAll('[data-fam-filter-go]').forEach(b => b.addEventListener('click', () => {
    SEL.family.clear(); SEL.family.add(b.dataset.famFilterGo); goAtlas(); applyFilters()
  }))
  modeEl.querySelectorAll('[data-jump]').forEach(b => b.addEventListener('click', () => {
    const el = $(b.dataset.jump); if (el) modeEl.scrollTop = el.offsetTop - 56
    setHash('#/queue')
  }))
  wireQueueBody()
  // R10.4 — the same search field, in the same slot, behaving the same way; it
  // also filters this page's own records, which is what the page is a list of.
  wirePageSearch(modeEl, {
    localFilter: q => modeEl.querySelectorAll('.fam-card').forEach(c => {
      c.classList.toggle('hidden', !!q && !c.dataset.famSearch.includes(q))
    })
  })
}

function openQueue() { openFamiliesPage({ scrollTo: 'queue-section' }) }

function queueBody() {
  const items = pending.items || []
  const slice = items.slice(0, queueShown)
  return `<p class="lede2">Edges where the two model arms disagreed on the relation family. A human adjudicates only genuine disagreement, not every edge. Both answers are shown as competing evidence with their stated reasons and neither is marked as the default — the interface must not suggest an answer.</p>
    ${pending.present ? `<p class="lede2"><b>${slice.length} of ${items.length}</b> shown · from <code>${esc(pending.source || '')}</code>, generated ${esc(pending.generated || '')}. Read-only in ${esc(META.version)}: rulings are entered through the adjudication tool, which lands with the assignment pass.</p>
      ${slice.map(queueRow).join('')}
      ${queueShown < items.length ? `<p style="margin-top:1rem"><button class="chip" id="q-more">show the next ${Math.min(TRANCHE, items.length - queueShown)} — ${items.length - queueShown} still queued</button></p>` : ''}`
    : `<div class="empty"><b>The queue is empty because the assignment pass has not run.</b>
        No <code>family_pending_queue.json</code> was present when this build was made, so there is nothing to show —
        this is an absence of data, not a claim that every edge has been ruled on.</div>`}`
}
function wireQueueBody() {
  const more = $('q-more')
  if (more) more.addEventListener('click', () => { queueShown += TRANCHE; drawFamilies(); const el = $('queue-section'); if (el) modeEl.scrollTop = el.offsetTop - 56 })
  modeEl.querySelectorAll('[data-edge]').forEach(el => el.addEventListener('click', () => openEdgeFromPage(el.dataset.edge)))
}
// R7.5 — unanchored. The two arms are rendered identically and in the file's own
// order; nothing here marks one as the expected answer.
function queueRow(it) {
  const key = it.edge_id || it.key || `${it.subject}|${it.relation}|${it.object}`
  const id = KEY_TO_ID[key] || it.edge_id || ''
  const arms = []
  for (const [arm, reasonKey] of [['opus', 'opus_reason'], ['gemini', 'gemini_reason']])
    if (it[arm]) arms.push({ arm, family: it[arm], reason: it[reasonKey] || '' })
  const refs = it.refs || []
  return `<div class="qitem"${id ? ` data-edge="${esc(id)}"` : ''} style="cursor:${id ? 'pointer' : 'default'}">
    <div class="qedge">${esc(it.subject || '')} <span class="rel">${esc(it.relation || '')} →</span> ${esc(it.object || '')}${
      it.relation_effective && it.relation_effective !== it.relation ? `<span class="rel-norm"><b>normalized:</b> ${esc(it.relation_effective)}</span>` : ''}</div>
    ${refs.map(r => `<blockquote>${esc(r.quote)}</blockquote><div class="qarms">CW ${esc(r.volume)} §${esc(r.paragraph)}${r.claim_type ? ' · ' + esc(r.claim_type) : ''}</div>`).join('')}
    <div class="qarms">${arms.map(a => `<div><b>${esc(a.arm)}</b> — ${esc(a.family)}${a.reason ? `: ${esc(a.reason)}` : ''}</div>`).join('')}</div>
  </div>`
}

// V2-R10 (editorial ruling, 2026-08-13) — the toolbar's navigation buttons were
// removed when the site menu arrived: two navigation systems in one bar is one
// too many. The routes they opened are unchanged and are reached from the menu
// (#/concordance, /families, #/method) and from the router below, so these
// bindings are optional now — they attach if the buttons exist and are silent
// if they do not, which keeps a stale template from breaking the whole app.
$('open-concordance')?.addEventListener('click', openConcordance)
$('open-families')?.addEventListener('click', openFamiliesPage)
$('open-method')?.addEventListener('click', openMethod)

// ------------------------------------------------------- R1.4/R1.5 · counts ---
// Every live number is read from atlas.json, which is regenerated from seed.json
// on every build. The only constant is the frozen release the paper describes.
const C = META.counts, F = META.frozen
$('version').textContent = `${META.version} · ${C.nodes}/${C.edges}/${C.references} · updated ${META.built}`
$('version').title = `${META.version}, built ${META.built} — ${C.nodes} nodes, ${C.edges} relations, ${C.references} references. The paper describes ${F.version} (${F.nodes}/${F.edges}/${F.references}), preserved at ${F.url}`
$('landing-counts').textContent = `${C.nodes} symbols · ${C.edges} relations · ${C.references} cited claims · ${META.version}`
// (about panel removed)

function updateStats() {
  $('stats').textContent = `${cy.nodes('[kind != "region"]').not('.hidden').length} nodes · ${cy.edges().not('.hidden').length} edges`
}

// ------------------------------------------------------- R2 · the summary ---
// The clauses are generated from the graph through the normal proposer/gate
// chain and loaded from summary.json. Verification item 7: a clause whose edges
// are no longer in the graph must fail loudly rather than render as plain prose.
// Clauses cite edges by their STABLE key (`subject|relation|object`), not by the
// build-index `eN` id, which shifts whenever seed edge order changes. With keys
// the loud-failure case fires only when an edge is genuinely gone. A legacy
// file using `edge_ids` still resolves, so an older summary is not silently lost.
const KEY_TO_ID = Object.fromEntries(atlas.edges.map(e => [e.key, e.id]))
const clauseEdges = []
function clauseRefs(c) { return (c.edge_keys || c.edge_ids || []) }
function resolveClause(c) {
  return clauseRefs(c)
    .map(ref => KEY_TO_ID[ref] || ref)
    .filter(id => cy.getElementById(id).nonempty())
}
function buildSummary() {
  const box = $('summary')
  const broken = []
  const html = summary.clauses.map((c, i) => {
    const live = resolveClause(c)
    clauseEdges[i] = live
    if (!live.length) { broken.push({ i, c }); return `<span class="clause broken" title="This clause cites no live edge — the graph has moved under the summary.">${esc(c.text)}</span> ` }
    return `<span class="clause" data-clause="${i}" title="Click to light the evidence behind this clause">${esc(c.text)}</span> `
  }).join('')
  box.innerHTML = `<div class="sum-label">Written from the graph${summary.method ? ` — <a href="${esc(summary.method_url || '#')}">${esc(summary.method.split('—')[0].trim())}</a>` : ''}. Every clause is a citation: click one.</div>
    <div class="sum-body">${html}</div>
    ${summary.placeholder
      ? `<div class="sum-placeholder">PLACEHOLDER SUMMARY — wired to real edges so the mechanism can be tested. The generated hundred words are produced through the verification chain and replace this file wholesale.</div>`
      : `<div class="sum-verified">Written from the graph and checked${summary.generated_date ? ` · ${esc(summary.generated_date)}` : ''}</div>`}
    ${broken.length ? `<div class="clause-error">BROKEN: ${broken.length} clause${broken.length > 1 ? 's' : ''} cite${broken.length > 1 ? '' : 's'} edges that are not in this graph (${esc(broken.map(b => clauseRefs(b.c).join(', ')).join(' | '))}). The summary is stale and must be regenerated before publication.</div>` : ''}`
  box.querySelectorAll('.clause[data-clause]').forEach(el => el.addEventListener('click', () => {
    const i = Number(el.dataset.clause)
    box.querySelectorAll('.clause').forEach(c => c.classList.remove('active'))
    el.classList.add('active')
    lightClause(i)
    // R10.2 — exactly one camera gesture from here to the evidence view.
    // enterAtlas() would issue its own re-frame, so it is told to leave the
    // camera alone and this focusOn is the only move that happens.
    enterAtlas({ reframe: false })
    const els = (clauseEdges[i] || []).reduce((acc, id) => acc.union(cy.getElementById(id)), cy.collection())
    const first = cy.getElementById(clauseEdges[i][0])
    if (first.nonempty()) selectEdge(first)
    focusOn(around(els), { padding: 170 })
  }))
  return broken.length
}
// R11.2 — the ignition node. The camera opens tight on the node the FIRST CLAUSE
// is about, not on whichever node carries the most edges: clause 1 begins "The
// stone …", so the stone is what the opening frame holds and what the pull-back
// opens out from. It is read from the summary's own first citation rather than
// named here, so regenerating the narration moves the camera with it.
function ignitionNode() {
  const first = (clauseEdges[0] || [])[0]
  if (!first) return null
  const e = cy.getElementById(first)
  return e.nonempty() ? e.source().id() : null
}
function lightClause(i) {
  cy.elements().removeClass('lit')
  const els = cy.collection()
  ;(clauseEdges[i] || []).forEach(id => { const e = cy.getElementById(id); els.merge(e); els.merge(e.connectedNodes()) })
  els.addClass('lit')
}

// --------------------------------------------------- R0.1 · one surface -----
const overlay = $('overlay'), veil = $('veil')
let inAtlas = false

// R9.1 — the graph sits to the RIGHT of the text column while the prose is up.
// The offset is computed from the viewport (and matches #prose's max-width rule),
// never a fixed pixel count, and it is undone on the way into the atlas.
let panOffset = 0
function landingOffset() {
  const vw = window.innerWidth
  if (inAtlas || vw < 900) return 0      // in the atlas the graph owns the stage
  return Math.min(vw * 0.58, 46 * 16) / 2
}
// Compute the target rather than fitting and then rewinding: cytoscape's
// animations are driven by requestAnimationFrame, so in a background tab an
// animated viewport move never runs. Anything that animates the viewport must
// therefore know its destination and be able to snap there.
// `includeUnrevealed` measures the graph the reveal is heading towards rather
// than the part of it drawn so far. The flight needs a destination that does not
// move under it while elements are still blooming; everything else wants the
// frame that fits what is actually on screen.
function landingTarget(pad = 60, { includeUnrevealed = false } = {}) {
  let bb
  if (includeUnrevealed) {
    // Unrevealed (.pre) elements are display:none and contribute nothing to
    // boundingBox, and compound regions collapse with their hidden children —
    // so the flight's destination was framing the few revealed elements and
    // the camera flew INTO the graph, with the post-landing safety check then
    // snapping out to the true rest: the visible "cut". The future bbox must
    // come from node POSITIONS, which exist regardless of display.
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity
    cy.nodes('[kind != "region"]').forEach(n => {
      const p = n.position()
      if (p.x < x1) x1 = p.x; if (p.x > x2) x2 = p.x
      if (p.y < y1) y1 = p.y; if (p.y > y2) y2 = p.y
    })
    const mgn = 40
    bb = { x1: x1 - mgn, y1: y1 - mgn, w: (x2 - x1) + 2 * mgn, h: (y2 - y1) + 2 * mgn }
  } else {
    bb = cy.elements().not('.pre').not('.hidden').boundingBox()
  }
  const w = cy.width(), h = cy.height()
  if (!bb.w || !bb.h || !w || !h) return null
  const fit = Math.min((w - 2 * pad) / bb.w, (h - 2 * pad) / bb.h)
  const z = Math.max(cy.minZoom(), Math.min(fit, cy.maxZoom()))
  const ctrX = bb.x1 + bb.w / 2, ctrY = bb.y1 + bb.h / 2
  return { zoom: z, pan: { x: w / 2 - z * ctrX + landingOffset(), y: h / 2 - z * ctrY }, ctrX, ctrY }
}

// R11.3 — TWO CLOCKS. The camera and the narration used to share the assembly's
// progress fraction, which meant neither could be timed without retiming the
// other. They are now independent, and the sequence reads as two things
// happening at once rather than one thing driving another.
//
// The graph EMERGES over EMERGENCE_MS: the ignition frame holds on the ignited
// node for IGNITE_HOLD_MS — one bright, labelled stone against near-black, the
// opening image — and then the elements bloom while the camera pulls back across
// the rest, arriving on the resting transform exactly at the end.
//
// The narration runs on its own, far shorter clock, so the words settle early
// and the graph goes on growing and opening around them.
const EMERGENCE_MS = 15000
const IGNITE_HOLD_MS = 1000
const IGNITE_ZOOM = 1.6                // the frame the hold sits at
const CLAUSE_FIRST_MS = 1000           // clause 1 writes as the pull-back starts
const CLAUSE_STEP_MS = 1500            // …and the last of four lands at 5.5s
const VEIL_FROM_MS = 250               // the veil is fully in place by CLAUSE_FIRST_MS

// The flight is driven frame by frame rather than handed to cytoscape's animator:
// a single queued animation cannot be held for a beat, cannot be interrupted
// cleanly halfway, and would fight the reveal's own repaints. Easing is
// logarithmic on zoom and linear on the centre, both through one ease-in-out, so
// the hold releases without a jerk and the arrival has no bump. A timer runs
// alongside rAF because a background tab suspends rAF entirely.
if (DEV) {
  window.__camlog = []
  for (const fn of ['viewport', 'fit', 'zoom', 'center']) {
    const orig = cy[fn].bind(cy)
    cy[fn] = (...args) => {
      if (args.length) window.__camlog.push([Math.round(performance.now()), fn, +cy.zoom().toFixed(4), new Error().stack.split('\n')[2]?.trim()])
      return orig(...args)
    }
  }
}

let flightActive = false
function flyToRest(anchor) {
  flightActive = true
  return new Promise(resolve => {
    if (!anchor) { fitLanding(); resolve(); return }
    const t0 = performance.now()
    let done = false, dest = null, destW = 0, destH = 0
    const destination = () => {
      const w = cy.width(), h = cy.height()
      if (!dest || w !== destW || h !== destH) { dest = landingTarget(60, { includeUnrevealed: true }); destW = w; destH = h }
      return dest
    }
    // smoothstep: peak slope 1.5x average (cubic in-out peaked at 3x, which
    // read as a mid-flight jump). Log-zoom + gentle ease = steady pull-back.
    const ease = p => p * p * (3 - 2 * p)
    const stop = settle => {
      if (done) return
      done = true
      flightActive = false
      if (DEV) trace.flightMs = performance.now() - t0
      clearInterval(tick)
      if (settle) {
        // at flight end everything is revealed, so the styled measurement is
        // both available and exact — prefer it over the position-space estimate
        const d = landingTarget() || destination()
        // fitLanding polls for a measurement; it is the fallback for the case
        // where the canvas was never measurable during the flight (a tab that
        // loaded hidden), which must still end at rest rather than wherever
        // cytoscape started
        if (d) { cy.stop(); cy.viewport({ zoom: d.zoom, pan: d.pan }) } else fitLanding()
        // belt and braces: assert the resting frame once the reveal has certainly
        // flushed, in case the tab was hidden for the last leg. Keep retrying
        // while the canvas is unmeasurable — a landing that cannot be computed
        // yet must still happen, not be skipped.
        let tries = 40
        const assertRest = () => {
          if (inAtlas) return
          const r = landingTarget()
          if (!r) { if (tries-- > 0) setTimeout(assertRest, 150); return }
          if (Math.abs(cy.zoom() - r.zoom) > 0.001) { cy.stop(); cy.viewport({ zoom: r.zoom, pan: r.pan }) }
        }
        setTimeout(assertRest, 400)
      }
      resolve()
    }
    const step = () => {
      if (done) return
      if (inAtlas) return stop(false)      // the reader took over; enterAtlas owns the camera
      // the clock is read before the measurement, so an unmeasurable canvas
      // delays the travel but can never swallow the landing
      const p = Math.max(0, Math.min(1, (performance.now() - t0 - IGNITE_HOLD_MS) / (EMERGENCE_MS - IGNITE_HOLD_MS)))
      if (p >= 1) return stop(true)
      const d = destination()
      if (!d) return
      const e = ease(p)
      const z = Math.exp(Math.log(IGNITE_ZOOM) * (1 - e) + Math.log(d.zoom) * e)
      // Interpolate where the stone SITS ON SCREEN, not where the camera centre
      // is in graph space. Both ends are on screen — the hold position, and
      // wherever the stone falls in the resting frame — so a straight line
      // between them keeps it in view for the whole pull-back. Centring on a
      // world-space midpoint instead lets the fixed pixel offset swing it off
      // the right edge while the zoom is still tight.
      const sx0 = cy.width() / 2 + landingOffset(), sy0 = cy.height() / 2
      const sx1 = d.zoom * anchor.x + d.pan.x, sy1 = d.zoom * anchor.y + d.pan.y
      const sx = sx0 + (sx1 - sx0) * e, sy = sy0 + (sy1 - sy0) * e
      cy.viewport({ zoom: z, pan: { x: sx - z * anchor.x, y: sy - z * anchor.y } })
    }
    const raf = () => { if (done) return; step(); requestAnimationFrame(raf) }
    const tick = setInterval(() => { if (done) clearInterval(tick); else step() }, 80)
    step()                               // paint the ignition frame now, not one frame late
    requestAnimationFrame(raf)
  })
}

// The narration's own clock. Clause starts are absolute times on it, so retiming
// the emergence cannot drag the writing with it. The veil is keyed here too: the
// prose has to be readable the moment the first clause lands, which it cannot be
// if it waits on a fraction of a fifteen-second graph.
function runNarration(clauseEls) {
  return new Promise(resolve => {
    const t0 = performance.now()
    let landed = -1, done = false
    const finishAll = () => {
      if (done) return
      done = true
      if (DEV) trace.narrationMs = performance.now() - t0
      clearInterval(tick)
      if (!inAtlas) {
        clauseEls.forEach(el => el.classList.add('shown'))
        veil.style.opacity = '0.86'
        veil.style.transition = ''       // the per-frame drive is over; hand it back to CSS
      }
      resolve()
    }
    const step = () => {
      if (done) return
      if (inAtlas) return finishAll()
      const ms = performance.now() - t0
      veil.style.opacity = String(0.86 * Math.max(0, Math.min(1, (ms - VEIL_FROM_MS) / (CLAUSE_FIRST_MS - VEIL_FROM_MS))))
      if (!clauseEls.length) { if (ms > CLAUSE_FIRST_MS) finishAll(); return }
      const want = Math.min(clauseEls.length - 1, Math.floor((ms - CLAUSE_FIRST_MS) / CLAUSE_STEP_MS))
      for (let i = landed + 1; i <= want; i++) {
        clauseEls[i].classList.add('shown')
        const ci = clauseEls[i].dataset.clause
        if (ci !== undefined) lightClause(Number(ci))
        if (DEV) trace.clauseMs.push(Math.round(ms))
        landed = i
      }
      if (landed >= clauseEls.length - 1) finishAll()
    }
    const raf = () => { if (done) return; step(); requestAnimationFrame(raf) }
    const tick = setInterval(() => { if (done) clearInterval(tick); else step() }, 60)
    step()
    requestAnimationFrame(raf)
  })
}

// A viewport target cannot be computed against a container that has no size yet
// — the fit would divide by a zero-width canvas and the landing would go
// nowhere. Poll until the canvas measures, then run. (Called by fitLanding
// below, which is reached from resize, leaveAtlas and the reduced-motion boot.)
function whenMeasured(fn, tries = 60) {
  if (cy.width() && cy.height()) { fn(); return }
  if (tries > 0) setTimeout(() => whenMeasured(fn, tries - 1), 50)
}
function fitLanding({ animate = false } = {}) {
  if (flightActive) return   // R11 — one camera owner: the flight recomputes its
                             // own destination on resize; nothing snaps past it
  panOffset = landingOffset()
  cy.stop()
  whenMeasured(() => {
    const t = landingTarget()
    if (!t) return
    cy.stop()
    if (!animate || REDUCED) { cy.viewport(t); return }
    cy.animate({ zoom: t.zoom, pan: t.pan }, { duration: 480, easing: 'ease-out', queue: false })
    // assert the destination once the animation should have finished, in case it
    // never ran (background tab) or was interrupted
    setTimeout(() => {
      const t2 = landingTarget()
      if (t2 && Math.abs(cy.zoom() - t2.zoom) > 0.01) { cy.stop(); cy.viewport(t2) }
    }, 700)
  })
}
function enterAtlas({ reframe = true } = {}) {
  if (inAtlas) return
  inAtlas = true
  document.body.classList.add('atlas')
  veil.style.transition = ''
  veil.style.opacity = ''
  // The text column is gone, so the graph takes the whole stage: drop the
  // landing offset and re-frame centred.
  panOffset = 0
  if (!reframe) return        // the caller owns the single camera move (R10.2)
  const t = landingTarget()   // landingOffset() is 0 once panOffset is cleared
  if (!t) return
  cy.stop()
  if (REDUCED) { cy.viewport(t); return }
  cy.animate({ zoom: t.zoom, pan: t.pan }, { duration: 620, easing: 'ease-out', queue: false })
  setTimeout(() => { const t2 = landingTarget(); if (t2 && Math.abs(cy.zoom() - t2.zoom) > 0.01) { cy.stop(); cy.viewport(t2) } }, 820)
}
function leaveAtlas() {
  inAtlas = false
  document.body.classList.remove('atlas')
  overlay.scrollTop = 0
  veil.style.transition = ''
  veil.style.opacity = '0.86'
  closeMode(); clearSelection()
  $('family-panel').classList.add('hidden')
  $('prose').style.opacity = ''; $('prose').style.transform = ''
  fitLanding()
  if (location.hash) setHash('')
}
window.addEventListener('resize', () => { if (!inAtlas) fitLanding() })

// R9.3 — the transition responds to wheel/trackpad (the overlay scrolls), to a
// click on the cue, and to the keyboard. The threshold is half a viewport so a
// short trackpad flick is enough to commit.
overlay.addEventListener('scroll', () => {
  const t = Math.min(1, overlay.scrollTop / (window.innerHeight * 0.5))
  const prose = $('prose')
  prose.style.opacity = String(Math.max(0, 1 - t * 1.35))
  prose.style.transform = `translateY(${-t * 54}px)`
  veil.style.transition = 'none'
  veil.style.opacity = String(0.86 * (1 - t))
  if (t >= 1) enterAtlas()
}, { passive: true })
// R11 — after (or during) the emergence, clicking the graph itself enters the
// atlas. The overlay owns the pointer pre-atlas, so a click that is not on the
// prose or a control is a click on the graph.
overlay.addEventListener('click', ev => {
  if (inAtlas) return
  if (ev.target.closest('#prose, #prose-more, a, button, .clause, input')) return
  enterAtlas()
})
$('scroll-cue').addEventListener('click', () => {
  if (REDUCED) { enterAtlas(); return }
  overlay.scrollTo({ top: window.innerHeight * 0.55, behavior: 'smooth' })
  setTimeout(enterAtlas, 620)
})
window.addEventListener('keydown', ev => {
  if (inAtlas) {
    if (ev.key === 'Escape') { closeMode(); $('family-panel').classList.add('hidden'); clearSelection() }
    return
  }
  if (['ArrowDown', 'PageDown', 'Enter', ' ', 'Spacebar'].includes(ev.key)) {
    if (ev.target && /^(INPUT|TEXTAREA)$/.test(ev.target.tagName)) return
    if (ev.key === 'Enter' && ev.target !== $('scroll-cue') && ev.target !== document.body) return
    ev.preventDefault(); $('scroll-cue').click()
  }
})
$('brand').addEventListener('click', leaveAtlas)

// ------------------------------------------------------------- R6 · router ---
function applyHash() {
  if (routing) return
  const h = location.hash
  if (!h || h === '#' || h === '#/') return
  enterAtlas()
  const { path, params } = routeOf(h)
  // #/atlas?node=<id> / ?edge=<id> — the form the atlas emits and the one an
  // inbound deep link uses. Selecting focuses the neighbourhood, not the node
  // alone, so the reader lands seeing where they are (R9.2's zoom cap).
  if (path === '#/atlas' && (params.get('node') || params.get('edge'))) {
    closeMode(); $('family-panel').classList.add('hidden')
    const id = params.get('node') || params.get('edge')
    const el = cy.getElementById(id)
    if (el.nonempty()) {
      if (el.isNode()) selectNode(el, { hash: false }); else selectEdge(el, { hash: false })
      focusOn(around(el))
    } else {
      console.warn(`deep link: no ${params.get('node') ? 'node' : 'edge'} "${id}" in this graph`)
    }
    return
  }
  let m
  if ((m = h.match(/^#\/n\/(.+)$/))) {
    const n = cy.getElementById(decodeURIComponent(m[1]))
    if (n.nonempty() && n.isNode()) { selectNode(n, { hash: false }); focusOn(around(n)) }
  } else if ((m = h.match(/^#\/e\/(.+)$/))) {
    const e = cy.getElementById(decodeURIComponent(m[1]))
    if (e.nonempty() && e.isEdge()) { selectEdge(e, { hash: false }); focusOn(around(e)) }
  } else if ((m = h.match(/^#\/family\/(.*)$/))) openFamily(decodeURIComponent(m[1]))
  else if (path === '#/concordance') openConcordance()
  else if (path === '#/queue') openQueue()
  else if (path === '#/families') openFamiliesPage()
  else if (path === '#/method') openMethod()
  else if (path === '#/atlas') { closeMode(); $('family-panel').classList.add('hidden') }
}
window.addEventListener('hashchange', applyHash)

// Item 14 — the menu's hash destinations are routes, not documents. Their hrefs
// are absolute (`/#/atlas`) because a generated page must be able to load the
// app; inside the app that same href is a different PATH whenever the app is not
// served from exactly `/`, so the browser reloaded the document and the graph
// came back re-laid-out with the selection gone. Delegated on the document, so
// the topbar's menu and any route panel's menu are both covered, and so a route
// added later needs nothing.
document.addEventListener('click', ev => {
  const link = ev.target.closest && ev.target.closest('.topmenu a, .brand[href]')
  if (!link || ev.defaultPrevented || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button) return
  const href = link.getAttribute('href') || ''
  const route = href.match(/^\/?(#\/.*)$/)
  if (!route) return                       // a real page: let the browser go
  ev.preventDefault()
  // Item 16 — route in THIS task. Assigning location.hash defers the route to
  // the hashchange task and the browser paints in between, so the reader gets
  // one frame of whatever they were looking at — the graph, when they clicked
  // from the atlas — after they clicked. pushState changes the URL without
  // firing hashchange, so the route runs inline and the first paint after the
  // click already carries the new view. The history entry is kept, and popstate
  // below routes the Back button that entry creates.
  if (location.hash !== route[1]) history.pushState(null, '', route[1])
  applyHash()
})
window.addEventListener('popstate', applyHash)

// ----------------------------------------------------------------- buttons ---
$('fit').addEventListener('click', () => cy.animate({ fit: { padding: 50 } }, { duration: 450 }))
$('relayout').addEventListener('click', () => {
  clearSelection(); $('search').value = ''; runSearch('')
  Object.values(SEL).forEach(s => s.clear())
  applyFilters()
  cy.animate({ fit: { padding: 50 } }, { duration: 450 })
})

// -------------------------------------------------------------------- boot ---
cy.ready(() => {
  const boot = $('boot'); if (boot) boot.remove()
  overlay.hidden = false
  drawWorks(); drawChips(); updateStats()
  const deepLink = /^#\/(n|e|family|families|concordance|queue|atlas|method)/.test(location.hash)

  if (REDUCED || deepLink) {
    // R0.4 — reduced motion renders the settled graph with the summary already
    // in place. Nothing animates, nothing is deferred.
    assemble(cy, { reduced: true }).then(() => {
      buildSummary()
      document.querySelectorAll('.clause').forEach(c => c.classList.add('shown'))
      veil.style.opacity = deepLink ? '0' : '0.86'
      updateStats()
      // same batch-flush caveat as fitLanding: measure after the tick
      // Item 16 — a deep link to a PANEL route mounts its panel in this task,
      // before the first paint. Deferring it by a tick let the assembled graph
      // paint first, so arriving at /#/method from a page flashed the atlas.
      // The node and edge deep links keep the tick: focusOn measures the
      // viewport and needs the layout flushed.
      if (deepLink) {
        enterAtlas()
        if (/^#\/(method|concordance|families|queue)/.test(location.hash)) applyHash()
        else setTimeout(applyHash, 0)
      } else fitLanding()
    })
    return
  }

  // The veil is driven per frame during the assembly, so its CSS transition is
  // switched off for the duration: re-setting a transitioned property every
  // frame restarts the ease each time and the value crawls instead of tracking.
  veil.style.transition = 'none'
  veil.style.opacity = '0'
  // R11.3 — three things start together and each finishes on its own clock: the
  // narration (~5.5s), the element reveal, and the camera flight (both 15s). None
  // of them reads another's progress, so any one can be retimed alone. Entering
  // the atlas cancels all three — `cancelled` makes the reveal finish on the spot
  // rather than leave the graph half-drawn under the reader.
  buildSummary()
  const clauseEls = [...document.querySelectorAll('.clause')]
  const ignite = ignitionNode()
  const igniteEl = ignite ? cy.getElementById(ignite) : null
  const igniteAt = igniteEl && igniteEl.nonempty()
    ? { x: igniteEl.position('x'), y: igniteEl.position('y') } : null

  if (DEV) trace.boot = performance.now()
  // R11 — the show waits for an audience. A tab loaded in the background (a
  // Reddit middle-click, or the reader glancing at another window) used to run
  // the whole sequence unseen and snap to the wide view on first look — the
  // "zoom doesn't work" bug in every one of its costumes. Nothing starts until
  // the document is actually visible.
  const startShow = () => {
  runNarration(clauseEls).then(() => {
    setTimeout(() => { if (!inAtlas) cy.elements().removeClass('lit') }, 1200)
  })
  flyToRest(igniteAt)
  assemble(cy, {
    duration: EMERGENCE_MS - IGNITE_HOLD_MS,
    hold: IGNITE_HOLD_MS,
    ignite,
    camera: false,                      // flyToRest owns the viewport for the whole sequence
    cancelled: () => inAtlas
  }).then(() => {
    if (DEV) trace.revealMs = performance.now() - trace.boot
    updateStats()
    clauseEls.forEach(el => el.classList.add('shown'))
  })
  }
  if (document.visibilityState === 'visible') startShow()
  else {
    const once = () => {
      if (document.visibilityState !== 'visible' || inAtlas) return
      document.removeEventListener('visibilitychange', once)
      startShow()
    }
    document.addEventListener('visibilitychange', once)
    // a deep link or atlas entry while hidden makes the show moot
  }
})
