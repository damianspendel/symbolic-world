// R8 / R9.8 / R10.10 — the Concordance: psychology against alchemy, as a page.
//
// Nothing here is a new dataset. Every arc is an edge already in seed.json, with
// its citation, and clicking one opens it in the atlas under the normal evidence
// view. Register membership is decided in build-atlas.mjs from node type plus two
// explicit lists; the curated core, its ranking and both journeys are computed
// there too. This module draws and explains — it never selects.
//
// R10.10's defect to fix: you could not tell which arrow carried which
// relationship. Three things now say it — the arc names its relation at the
// cursor, choosing a concept lists its crossings by relation, and hovering a
// crossing lights exactly one arc.

const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const cssEsc = s => String(s).replace(/["\\]/g, '\\$&')
const WALK_SEEN = 'sw-concordance-walk-seen'
const LENSES = ['symbolization', 'correspondence', 'projection']

export function renderConcordance(root, atlas, { onOpenEdge, onBack, mixStrip, pageBar }) {
  const nodeById = Object.fromEntries(atlas.nodes.map(n => [n.id, n]))
  const edgeById = Object.fromEntries(atlas.edges.map(e => [e.id, e]))
  const conc = atlas.concordance
  const label = id => (nodeById[id] || {}).label || id
  const degree = conc.bridgeDegree || {}

  const rowFor = (id) => {
    const e = edgeById[id]
    if (!e) return null
    const psyche = (nodeById[e.source] || {}).register === 'psyche' ? e.source : e.target
    const lab = psyche === e.source ? e.target : e.source
    const r = e.refs[0] || {}
    return {
      id, e, psyche, lab, inverted: psyche !== e.source,
      family: e.family ? e.family.value : '',
      cite: r.volume ? `CW ${r.volume} §${r.paragraph}` : ''
    }
  }
  const allRows = conc.bridges.map(rowFor).filter(Boolean)
  const coreRows = (conc.core || []).map(rowFor).filter(Boolean)

  const walks = {
    'psyche-first': conc.guided || [],
    'laboratory-first': conc.guidedReverse || []
  }
  const journeys = conc.journeys || []

  let showAll = false
  let picked = ''                 // a chosen concept, whose crossings get listed
  let lens = new Set()            // R10.10 family lenses
  let walkId = localStorage.getItem(WALK_SEEN) ? '' : (journeys[0] || {}).dir || ''
  let walkAt = 0
  const markWalkSeen = () => { try { localStorage.setItem(WALK_SEEN, '1') } catch {} }
  const currentWalk = () => walks[walkId] || []

  // ---- the journey box (FIXED height, R10.10) --------------------------------
  function walkHTML() {
    const w = currentWalk()
    if (!walkId || !w.length) return ''
    const g = w[Math.min(walkAt, w.length - 1)]
    const e = edgeById[g.edges[0]]
    const r = (e && e.refs.find(x => `CW ${x.volume} §${x.paragraph}` === g.cite)) || (e && e.refs[0]) || {}
    const j = journeys.find(x => x.dir === walkId) || {}
    const first = walkId === 'laboratory-first' ? g.laboratory : g.psyche
    const second = walkId === 'laboratory-first' ? g.psyche : g.laboratory
    return `<div class="gwalk">
      <div class="walk-body">
        <div class="walk-step">${esc(j.title || 'A guided crossing')} · stop ${walkAt + 1} of ${w.length}</div>
        <h3>${esc(label(first))}<i>·</i>${esc(label(second))}</h3>
        <p class="gloss">${esc(g.gloss)}</p>
        ${e ? `<div class="walk-rel">${esc(e.source === g.psyche ? '' : '← ')}${esc(e.relation)}${e.source === g.psyche ? ' →' : ''}</div>` : ''}
        ${r.quote ? `<blockquote>${esc(r.quote)}</blockquote><div class="wcite">${esc(g.cite)}${r.claim_type ? ' · ' + esc(r.claim_type) : ''}</div>` : ''}
      </div>
      <div class="walk-nav">
        <button data-walk="prev"${walkAt === 0 ? ' disabled' : ''}>← back</button>
        <button data-walk="next">${walkAt === w.length - 1 ? 'finish' : 'next →'}</button>
        <button data-walk="open">open this edge in the atlas</button>
        <span class="walk-dots">${w.map((_, i) => `<i class="${i === walkAt ? 'on' : ''}"></i>`).join('')}</span>
        <button class="skip" data-walk="skip">close the walk ✕</button>
      </div>
    </div>`
  }

  function journeyTiles() {
    if (!journeys.length) return ''
    return `<div class="journeys">${journeys.map(j => `
      <button class="jtile ${j.dir === 'laboratory-first' ? 'reverse' : ''} ${walkId === j.dir ? 'on' : ''}" data-journey="${esc(j.dir)}">
        <span class="jt">${esc(j.title)}</span>
        <span class="jd">${esc(j.lead)}</span>
      </button>`).join('')}</div>`
  }

  // ---- the board -------------------------------------------------------------
  function visibleRows() { return showAll ? allRows : coreRows }

  function draw() {
    const rows = visibleRows()
    const psyIds = [...new Set(rows.map(r => r.psyche))].sort((a, b) => (degree[b] || 0) - (degree[a] || 0) || label(a).localeCompare(label(b)))
    const labIds = [...new Set(rows.map(r => r.lab))].sort((a, b) => (degree[b] || 0) - (degree[a] || 0) || label(a).localeCompare(label(b)))
    const modeNote = atlas.meta.bridgeMode === 'family'
      ? 'Selected by family — the symbolization, correspondence and projection families crossing from one register to the other. New crossings appear here as they are mined and classified.'
      : 'Selected by register — every cited edge that crosses between the two sides.'
    const onlyTrilogy = Object.values(conc.mix || {}).filter(m => m.total && !m.other).length
    const pickedRows = picked ? allRows.filter(r => r.psyche === picked || r.lab === picked) : []

    root.innerHTML = `
      ${pageBar({ where: 'concordance', search: true })}
      <div class="page">
      <h2>Psychology against alchemy</h2>
      <p class="lede2">Jung's thesis is that alchemy is the psyche describing itself in projected form. The site does not have to assert that: the graph already holds it as verified edges. ${modeNote}</p>
      <p class="lede2">${allRows.length} crossings in all · <b>${onlyTrilogy} of ${atlas.nodes.length}</b> nodes in the atlas rest only on alchemical evidence, which is also an honest map of where this picture of the psychology comes from.</p>

      ${journeyTiles()}
      ${walkHTML()}

      <div class="conc-actions">
        <button data-core class="${showAll ? '' : 'on'}">the central ${coreRows.length}</button>
        <button data-all class="${showAll ? 'on' : ''}">show all ${allRows.length}</button>
        <span class="mix-l" style="margin:0">ranked by evidence weight: reference count, then how many crossings the concept carries</span>
      </div>

      <div class="lenses">
        <span class="mix-l" style="margin:0">lenses</span>
        ${LENSES.map(f => `<button class="lens ${lens.has(f) ? 'on' : ''}" data-lens="${f}" style="${lens.has(f) ? `color:var(--lens-${f})` : ''}">
          <i style="background:var(--lens-${f})"></i>${f}</button>`).join('')}
        ${lens.size ? '<button class="lens" data-lens-clear>clear</button>' : ''}
      </div>

      <div class="conc-board" id="conc-board">
        <svg class="conc-arcs" id="conc-arcs" preserveAspectRatio="none"></svg>
        <div class="conc-col left">
          <div class="conc-colhead">The Psyche</div>
          ${psyIds.map(id => `<button class="cnode ${picked === id ? 'hot' : ''}" data-node="${esc(id)}">${esc(label(id))} <span class="deg">${degree[id] || 0}</span></button>
            ${mixStrip ? mixStrip(id, { compact: true }) : ''}`).join('')}
        </div>
        <div class="conc-mid">
          ${picked ? `<div class="conc-colhead" style="text-align:center">${esc(label(picked))} · ${pickedRows.length} claim${pickedRows.length === 1 ? '' : 's'}</div>
          ${pickedRows.map(r => `<button class="conc-rel" data-edge="${esc(r.id)}">${r.inverted ? '←&nbsp;' : ''}${esc(r.e.relation)}${r.inverted ? '' : '&nbsp;→'}<span class="cite">${esc(label(r.psyche === picked ? r.lab : r.psyche))} · ${esc(r.cite)}</span></button>`).join('')}
          ${mixStrip ? mixStrip(picked) : ''}` : `<div class="conc-colhead" style="text-align:center;color:var(--ink-dim)">select a concept</div>`}
        </div>
        <div class="conc-col right">
          <div class="conc-colhead">The Laboratory</div>
          ${labIds.map(id => `<button class="cnode ${picked === id ? 'hot' : ''}" data-node="${esc(id)}">${esc(label(id))} <span class="deg">${degree[id] || 0}</span></button>`).join('')}
        </div>
      </div>
    </div>`

    wire(rows)
    setTimeout(() => drawArcs(rows), 0)
  }

  // ---- the arcs --------------------------------------------------------------
  function drawArcs(rows) {
    const board = root.querySelector('#conc-board')
    const svg = root.querySelector('#conc-arcs')
    if (!board || !svg) return
    const bb = board.getBoundingClientRect()
    // viewBox tracks the measured box, so browser zoom (which changes the box in
    // CSS pixels) rescales the drawing with the rest of the page (R10.10).
    svg.setAttribute('viewBox', `0 0 ${Math.round(bb.width)} ${Math.round(bb.height)}`)
    svg.setAttribute('width', Math.round(bb.width))
    svg.setAttribute('height', Math.round(bb.height))
    const anchor = (sel, side) => {
      const el = board.querySelector(sel)
      if (!el) return null
      const r = el.getBoundingClientRect()
      return { x: (side === 'right' ? r.right : r.left) - bb.left, y: r.top + r.height / 2 - bb.top }
    }
    const parts = []
    const arcRows = picked ? allRows.filter(r => r.psyche === picked || r.lab === picked) : rows
    const labelYs = []
    for (const row of arcRows) {
      const a = anchor(`.conc-col.left .cnode[data-node="${cssEsc(row.psyche)}"]`, 'right')
      const b = anchor(`.conc-col.right .cnode[data-node="${cssEsc(row.lab)}"]`, 'left')
      if (!a || !b) continue
      const mx = (a.x + b.x) / 2
      const d = `M ${a.x.toFixed(1)} ${a.y.toFixed(1)} C ${mx.toFixed(1)} ${a.y.toFixed(1)}, ${mx.toFixed(1)} ${b.y.toFixed(1)}, ${b.x.toFixed(1)} ${b.y.toFixed(1)}`
      const lensCls = lens.size
        ? (lens.has(row.family) ? `lens-${row.family}` : 'lens-dim')
        : ''
      parts.push(`<path d="${d}" stroke="transparent" stroke-width="12" style="pointer-events:stroke;cursor:pointer" data-hit="${esc(row.id)}"></path>`)
      parts.push(`<path d="${d}" class="${lensCls}" data-arc="${esc(row.id)}"></path>`)
    }
    svg.innerHTML = parts.join('')
    svg.querySelectorAll('[data-hit]').forEach(p => {
      const id = p.dataset.hit
      p.addEventListener('click', () => onOpenEdge(id))
      // R10.10 — the arc names its relation at the cursor
      p.addEventListener('mousemove', ev => showTip(ev, id))
      p.addEventListener('mouseenter', () => hot(id, true))
      p.addEventListener('mouseleave', () => { hot(id, false); hideTip() })
    })
  }

  // ---- the cursor tooltip ----------------------------------------------------
  function tipEl() {
    let t = document.getElementById('arc-tip')
    if (!t) { t = document.createElement('div'); t.id = 'arc-tip'; document.body.appendChild(t) }
    return t
  }
  function showTip(ev, edgeId) {
    const row = allRows.find(r => r.id === edgeId)
    if (!row) return
    const t = tipEl()
    t.classList.remove('hidden')
    t.innerHTML = `${esc(label(row.psyche))} ${row.inverted ? '←' : '—'} <b>${esc(row.e.relation)}</b> ${row.inverted ? '—' : '→'} ${esc(label(row.lab))}
      <span class="t2">${esc(row.cite)}${row.family ? ' · ' + esc(row.family) : ''}</span>`
    const pad = 14
    const w = t.offsetWidth, h = t.offsetHeight
    t.style.left = Math.min(window.innerWidth - w - 8, ev.clientX + pad) + 'px'
    t.style.top = Math.max(8, ev.clientY - h - pad) + 'px'
  }
  function hideTip() { const t = document.getElementById('arc-tip'); if (t) t.classList.add('hidden') }

  // ---- highlighting ----------------------------------------------------------
  function hot(edgeId, on) {
    const row = allRows.find(r => r.id === edgeId)
    root.querySelectorAll(`[data-arc="${cssEsc(edgeId)}"]`).forEach(p => p.classList.toggle('hot', on))
    root.querySelectorAll(`.conc-rel[data-edge="${cssEsc(edgeId)}"]`).forEach(p => p.classList.toggle('hot', on))
    root.querySelectorAll(`.crossrow[data-cross="${cssEsc(edgeId)}"]`).forEach(p => p.classList.toggle('hot', on))
    if (!row) return
    for (const id of [row.psyche, row.lab])
      root.querySelectorAll(`.cnode[data-node="${cssEsc(id)}"]`).forEach(el => el.classList.toggle('hot', on))
  }
  function hotNode(nodeId, on) {
    root.querySelectorAll(`.cnode[data-node="${cssEsc(nodeId)}"]`).forEach(el => el.classList.toggle('hot', on))
    for (const r of visibleRows())
      if (r.psyche === nodeId || r.lab === nodeId) {
        root.querySelectorAll(`[data-arc="${cssEsc(r.id)}"]`).forEach(p => p.classList.toggle('hot', on))
        root.querySelectorAll(`.conc-rel[data-edge="${cssEsc(r.id)}"]`).forEach(p => p.classList.toggle('hot', on))
      }
  }

  function wire(rows) {
    const back = root.querySelector('[data-back]')
    if (back) back.addEventListener('click', onBack)
    const core = root.querySelector('[data-core]'), all = root.querySelector('[data-all]')
    if (core) core.addEventListener('click', () => { showAll = false; draw() })
    if (all) all.addEventListener('click', () => { showAll = true; draw() })

    root.querySelectorAll('[data-lens]').forEach(b => b.addEventListener('click', () => {
      const f = b.dataset.lens
      lens.has(f) ? lens.delete(f) : lens.add(f)
      draw()
    }))
    const lc = root.querySelector('[data-lens-clear]')
    if (lc) lc.addEventListener('click', () => { lens.clear(); draw() })

    root.querySelectorAll('.conc-rel[data-edge]').forEach(el => {
      el.addEventListener('click', () => onOpenEdge(el.dataset.edge))
      el.addEventListener('mouseenter', () => hot(el.dataset.edge, true))
      el.addEventListener('mouseleave', () => hot(el.dataset.edge, false))
    })
    // R10.10 — hovering a listed crossing lights exactly its arc
    root.querySelectorAll('.crossrow[data-cross]').forEach(el => {
      el.addEventListener('click', () => onOpenEdge(el.dataset.cross))
      el.addEventListener('mouseenter', () => hot(el.dataset.cross, true))
      el.addEventListener('mouseleave', () => hot(el.dataset.cross, false))
    })
    root.querySelectorAll('.cnode[data-node]').forEach(el => {
      el.addEventListener('mouseenter', () => hotNode(el.dataset.node, true))
      el.addEventListener('mouseleave', () => hotNode(el.dataset.node, false))
      el.addEventListener('click', () => { picked = picked === el.dataset.node ? '' : el.dataset.node; draw() })
    })
    root.querySelectorAll('[data-journey]').forEach(b => b.addEventListener('click', () => {
      const d = b.dataset.journey
      walkId = walkId === d ? '' : d
      walkAt = 0
      if (!walkId) markWalkSeen()
      draw()
    }))
    root.querySelectorAll('[data-walk]').forEach(b => b.addEventListener('click', () => {
      const a = b.dataset.walk, w = currentWalk()
      if (a === 'skip') { walkId = ''; markWalkSeen() }
      else if (a === 'prev') walkAt = Math.max(0, walkAt - 1)
      else if (a === 'next') { if (walkAt + 1 >= w.length) { markWalkSeen(); walkId = '' } else walkAt++ }
      else if (a === 'open') { markWalkSeen(); onOpenEdge(w[walkAt].edges[0]); return }
      draw()
    }))
  }

  // browser zoom and window resize both change the measured board box
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(() => drawArcs(visibleRows()))
    setTimeout(() => { const b = root.querySelector('#conc-board'); if (b) ro.observe(b) }, 0)
  }

  draw()
}
