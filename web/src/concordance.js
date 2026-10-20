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
      ? 'Here, the symbolization, correspondence and projection families crossing from the alchemical register to the depth psychology register.'
      : 'Selected by register — every cited edge that crosses between the two sides.'
    const pickedRows = picked ? allRows.filter(r => r.psyche === picked || r.lab === picked) : []

    root.innerHTML = `
      ${pageBar({ where: 'concordance' })}
      <div class="page">
      <div class="titleband"><p class="eyebrow">explore</p>
      <h1>Psychology against alchemy</h1></div>
      <p class="lede2">Jung's thesis is that alchemy is the psyche describing itself in projected form. ${modeNote}</p>

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

      ${picked ? `<div class="wheel" id="wheel">
        <svg class="wheel-svg" id="wheel-svg"></svg>
        <button class="wheel-back" data-unpick>← all terms</button>
      </div>` : `<div class="conc-board" id="conc-board">
        <svg class="conc-arcs" id="conc-arcs" preserveAspectRatio="none"></svg>
        <div class="conc-col left">
          <div class="conc-colhead">The Psyche</div>
          ${psyIds.map(id => `<button class="cnode" data-node="${esc(id)}">${esc(label(id))} <span class="deg">${degree[id] || 0}</span></button>
            ${mixStrip ? mixStrip(id, { compact: true }) : ''}`).join('')}
        </div>
        <div class="conc-col right">
          <div class="conc-colhead">The Laboratory</div>
          ${labIds.map(id => `<button class="cnode" data-node="${esc(id)}">${esc(label(id))} <span class="deg">${degree[id] || 0}</span></button>`).join('')}
        </div>
      </div>`}
    </div>`

    wire(rows)
    if (picked) setTimeout(() => drawWheel(), 0)
    else setTimeout(() => drawArcs(rows), 0)
  }

  // ---- the wheel: the picked term at centre, every relation a labelled spoke.
  // Psyche partners take the left half, laboratory partners the right, so the
  // two-register geometry survives the change of form. Nodes fade in from the
  // centre outward; not a perfect wheel, an honest one.
  // spoke labels are signage: the normalized verb phrase where one exists;
  // the evidence panel keeps the verbatim relation as primary (R3.4)
  function spokeRel(e) { return (e.relation_normalized && e.relation_normalized.relation) || e.relation }

  function drawWheel() {
    const host = root.querySelector('#wheel')
    const svg = root.querySelector('#wheel-svg')
    if (!host || !svg || !picked) return
    const rows = allRows.filter(r => r.psyche === picked || r.lab === picked)
    // group by partner: one node per partner, one spoke per claim
    const partners = new Map()
    for (const r of rows) {
      const partner = r.psyche === picked ? r.lab : r.psyche
      if (!partners.has(partner)) partners.set(partner, [])
      partners.get(partner).push(r)
    }
    function regOf(id) { return allRows.some(r => r.psyche === id) ? 'psyche' : 'lab' }
    const left = [...partners.keys()].filter(p => regOf(p) === 'psyche')
    const right = [...partners.keys()].filter(p => regOf(p) !== 'psyche')
    const W = host.clientWidth
    const dense = Math.max(left.length, right.length)
    const H = Math.max(460, Math.min(760, 140 + dense * 62))
    host.style.height = H + 'px'
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`)
    svg.setAttribute('width', W); svg.setAttribute('height', H)
    const cx = W / 2, cy = H / 2
    const rx = Math.min(W * 0.40, 480), ry = H / 2 - 48
    // partners on each half-arc; alternate radius slightly so neighbouring
    // labels breathe — an honest wheel, not a perfect one
    const place = (list, side) => list.map((id, i) => {
      const n = list.length
      const a = n === 1 ? 0 : (i / (n - 1) - 0.5) * Math.PI * 0.94
      const wob = 1 + (i % 2 ? 0.045 : -0.045)
      const x = cx + Math.cos(a) * rx * wob * side, y = cy + Math.sin(a) * ry * wob
      return { id, x, y }
    })
    const pos = [...place(left, -1), ...place(right, 1)]
    // curved spokes: one quadratic per claim, fanned by curvature; labels ride
    // the curve and are collision-nudged so they cover neither nodes nor each other
    const spokes = []
    const labelBoxes = []
    const qp = (t, ax, ay, cxp, cyp, bx, by) => ({
      x: (1 - t) * (1 - t) * ax + 2 * (1 - t) * t * cxp + t * t * bx,
      y: (1 - t) * (1 - t) * ay + 2 * (1 - t) * t * cyp + t * t * by,
    })
    pos.forEach((p, pi) => {
      const claims = partners.get(p.id) || []
      const dx = p.x - cx, dy = p.y - cy
      const len = Math.hypot(dx, dy) || 1
      const nx = -dy / len, ny = dx / len          // unit normal
      claims.forEach((r, i) => {
        const fan = (i - (claims.length - 1) / 2) * 30
        const wiggle = (pi % 2 ? 12 : -12)
        const bend = fan + wiggle
        const mx2 = cx + dx * 0.5 + nx * bend, my2 = cy + dy * 0.5 + ny * bend
        const d = `M ${cx.toFixed(1)} ${cy.toFixed(1)} Q ${mx2.toFixed(1)} ${my2.toFixed(1)} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`
        const lensCls = lens.size ? (lens.has(r.family) ? `lens-${r.family}` : 'lens-dim') : ''
        // label: ride the curve, nudge along it until clear of neighbours
        let t = 0.55, L = null
        const nearNode = pt => pos.some(q => Math.abs(pt.y - q.y) < 24 && Math.abs(pt.x - q.x) < 95)
          || (Math.abs(pt.y - cy) < 26 && Math.abs(pt.x - cx) < 110)
        for (let tries = 0; tries < 7; tries++) {
          const pt = qp(t, cx, cy, mx2, my2, p.x, p.y)
          const clash = labelBoxes.some(b => Math.abs(b.y - pt.y) < 14 && Math.abs(b.x - pt.x) < 118) || nearNode(pt)
          if (!clash) { L = pt; break }
          t -= 0.06
        }
        if (!L) { const pt = qp(0.55, cx, cy, mx2, my2, p.x, p.y); L = { x: pt.x, y: pt.y - 14 } }
        labelBoxes.push(L)
        spokes.push(`<path d="${d}" class="spoke ${lensCls}" data-arc="${esc(r.id)}"></path>
          <path d="${d}" fill="none" stroke="transparent" stroke-width="14" style="pointer-events:stroke;cursor:pointer" data-hit="${esc(r.id)}"></path>
          <text x="${L.x.toFixed(1)}" y="${(L.y - 5).toFixed(1)}" text-anchor="middle" class="spoke-label" data-spoke-label="${esc(r.id)}">${esc(r.inverted ? '← ' + spokeRel(r.e) : spokeRel(r.e) + ' →')}</text>`)
      })
    })
    svg.innerHTML = spokes.join('')
    // nodes as absolutely-positioned buttons over the svg
    const nodeBtns = pos.map(p =>
      `<button class="wnode ${regOf(p.id) === 'psyche' ? 'wp' : 'wl'}" data-node="${esc(p.id)}" style="left:${p.x}px;top:${p.y}px">${esc(label(p.id))}</button>`)
    host.insertAdjacentHTML('beforeend',
      `<button class="wnode wcenter ${regOf(picked) === 'psyche' ? 'wp' : 'wl'}" data-unpick style="left:${cx}px;top:${cy}px">${esc(label(picked))} <span class="deg">${rows.length}</span></button>` +
      nodeBtns.join(''))
    // entrance: everything starts at the centre and flies out
    const els = [...host.querySelectorAll('.wnode:not(.wcenter)')]
    els.forEach(el => { el.style.transform = `translate(-50%,-50%) translate(${cx - parseFloat(el.style.left)}px, ${cy - parseFloat(el.style.top)}px)`; el.style.opacity = '0' })
    svg.style.opacity = '0'
    requestAnimationFrame(() => requestAnimationFrame(() => {
      els.forEach(el => { el.style.transform = 'translate(-50%,-50%)'; el.style.opacity = '1' })
      svg.style.opacity = '1'
    }))
    // wiring: spoke click opens the claim; partner click re-centres the wheel
    svg.querySelectorAll('[data-hit]').forEach(pth => {
      const id = pth.dataset.hit
      pth.addEventListener('click', () => onOpenEdge(id))
      pth.addEventListener('mousemove', ev => showTip(ev, id))
      pth.addEventListener('mouseenter', () => hot(id, true))
      pth.addEventListener('mouseleave', () => { hot(id, false); hideTip() })
    })
    host.querySelectorAll('.wnode[data-node]').forEach(b => b.addEventListener('click', () => { picked = b.dataset.node; draw() }))
    host.querySelectorAll('[data-unpick]').forEach(b => b.addEventListener('click', () => { picked = null; draw() }))
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
