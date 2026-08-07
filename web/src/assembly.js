// R0.1 / R0.4 — the assembly.
//
// The graph builds itself from the real elements at their real baked positions:
// one node ignites, edges draw outward from it, nodes bloom along them, the
// regions resolve, and the whole thing settles. Nothing here is decorative —
// every mark that appears is a claim in the graph.
//
// Two constraints govern the implementation. The reveal is capped BY TIME, not
// by element count: each frame reveals however many elements the clock says it
// should, so a slow device draws in bigger steps rather than running long. And
// `prefers-reduced-motion: reduce` skips the whole sequence and hands back the
// settled graph, which is why the caller passes `reduced` rather than the CSS
// deciding it for us.

const ORDER_CAP = 4000   // elements; beyond this we stop building the walk order

// Breadth-first from the ignition node, so the build spreads outward from it the
// way the graph was actually assembled: a node, then the claims that reach it,
// then the nodes those claims reach.
//
// R11.2 — the caller names the ignition node, and names it from the narration:
// the camera starts tight on the node the first clause is ABOUT, so the pull-back
// opens out from that noun rather than from whichever node happens to have the
// most edges. Without a named node the walk falls back to the highest-degree hub.
function walkOrder(cy, igniteId) {
  const nodes = cy.nodes('[kind != "region"]')
  if (!nodes.length) return { order: [], seed: null }
  let seed = null
  if (igniteId) {
    const named = nodes.getElementById(igniteId)
    if (named && named.length) seed = named
  }
  if (!seed) {
    seed = nodes[0]
    nodes.forEach(n => { if (n.degree(false) > seed.degree(false)) seed = n })
  }

  const order = []
  const seenNode = new Set()
  const seenEdge = new Set()
  const queue = [seed]
  seenNode.add(seed.id())

  const push = (el) => { if (order.length < ORDER_CAP) order.push(el) }

  while (queue.length) {
    const n = queue.shift()
    push(n)
    const conn = n.connectedEdges()
    for (let i = 0; i < conn.length; i++) {
      const e = conn[i]
      const other = e.source().id() === n.id() ? e.target() : e.source()
      if (seenNode.has(other.id())) {
        if (!seenEdge.has(e.id())) { seenEdge.add(e.id()); push(e) }
      } else {
        seenNode.add(other.id())
        queue.push(other)
      }
    }
  }
  // disconnected remainder, then any edge the walk never closed
  nodes.forEach(n => { if (!seenNode.has(n.id())) { seenNode.add(n.id()); push(n) } })
  cy.edges().forEach(e => { if (!seenEdge.has(e.id())) { seenEdge.add(e.id()); push(e) } })
  return { order, seed }
}

// `hold` is the beat the ignited node gets alone before the reveal starts.
// `camera: false` hands the viewport to the caller for the whole sequence — the
// module still ignites its node, but never zooms, centres, animates or lands.
// `cancelled` is polled every step: when it goes true the reveal completes
// immediately, so a reader who enters the atlas mid-sequence is never left with
// a half-drawn graph.
export function assemble(cy, { reduced = false, duration = 3500, hold = 420, onProgress, frame, ignite, camera = true, cancelled } = {}) {
  const regions = cy.nodes('[kind = "region"]')

  if (reduced) {
    cy.batch(() => cy.elements().removeClass('pre'))
    land(cy, frame, { instant: true })
    if (onProgress) onProgress(1)
    return Promise.resolve()
  }

  const { order, seed } = walkOrder(cy, ignite)
  if (!seed) { cy.elements().removeClass('pre'); return Promise.resolve() }

  // 1. Near-black. One node ignites at centre.
  seed.removeClass('pre').addClass('ignite')
  if (camera) {
    cy.zoom({ level: 1.6, position: seed.position() })
    cy.center(seed)
  }

  return new Promise(resolve => {
    // The reveal is driven by requestAnimationFrame, which browsers SUSPEND in a
    // background tab. Without a backstop a page opened in a background tab (or
    // left while it loads) comes back showing one node on a black field. The
    // time cap is therefore enforced by a timer as well as by the frame clock,
    // and finishing is idempotent so whichever gets there first wins.
    let done = false
    const finish = () => {
      if (done) return
      done = true
      cy.batch(() => cy.elements().removeClass('pre'))
      // The stone steps down slowly: border fades over 3.5s, then the class
      // (and its size override) releases. A snap here read as a blink.
      if (seed && seed.hasClass('ignite')) {
        const base = cy.nodes('[kind != "region"]').not('.ignite').first()
        const bw = base.nonempty() ? base.width() : 18
        seed.animate(
          { style: { 'border-width': 0, 'width': bw, 'height': bw } },
          { duration: 3500, easing: 'ease-out',
            complete: () => { seed.removeClass('ignite'); seed.removeStyle('border-width width height') } })
      }
      if (camera) {
        cy.stop()
        // R10.1 — the graph LANDS here, on the final resting transform. This is
        // the last leg of the SAME move, not a correction: the camera has been
        // travelling toward this target throughout. The target can only be
        // measured once cytoscape has flushed the reveal batch, so poll for it.
        land(cy, frame)
      }
      if (onProgress) onProgress(1)
      resolve()
    }
    setTimeout(finish, hold + duration + 1200)
    document.addEventListener('visibilitychange', () => {
      // returning to a tab that fell behind should not replay the whole build
      if (document.visibilityState === 'visible' && !done && performance.now() - startedAt > duration) finish()
    })
    const startedAt = performance.now()

    // The hold is a dead second for the step loop, so cancellation is watched
    // separately here — otherwise a reader who scrolls in during the opening beat
    // waits out the rest of it in front of an empty graph.
    const holdWatch = setInterval(() => {
      if (done) { clearInterval(holdWatch); return }
      if (cancelled && cancelled()) { clearInterval(holdWatch); finish() }
    }, 50)
    setTimeout(() => clearInterval(holdWatch), hold + 100)

    setTimeout(() => {
      if (done) return
      // 2/3. The graph builds itself. The reveal is capped BY TIME, so a longer
      // budget simply means each claim gets its own moment instead of arriving
      // in a crowd — the logic does not change with the duration.
      const t0 = performance.now()
      let cursor = 0
      let regionsShown = false
      let lastFit = 0

      const step = () => {
        if (done) return
        if (cancelled && cancelled()) return finish()
        const t = Math.min(1, (performance.now() - t0) / duration)
        const tt = t
        // ease-out on the count, so the first claims read individually and the
        // long tail arrives as mass — the shape of the graph's own growth
        const eased = 1 - Math.pow(1 - t, 2.1)
        const want = Math.ceil(eased * order.length)
        if (want > cursor) {
          cy.batch(() => { for (; cursor < want; cursor++) order[cursor].removeClass('pre') })
        }
        if (!regionsShown && t > 0.82) { regionsShown = true; cy.batch(() => regions.removeClass('pre')) }
        const now = performance.now()
        // queue:false — each fit REPLACES the running one. Queued fits stack up
        // behind each other and the viewport ends wherever the backlog left it.
        if (camera && now - lastFit > 300) {
          lastFit = now
          const t = frame && frame(tt)
          if (t) cy.animate({ zoom: t.zoom, pan: t.pan }, { duration: 360, easing: 'linear', queue: false })
          else cy.animate({ fit: { padding: 60 } }, { duration: 360, easing: 'linear', queue: false })
        }
        if (onProgress) onProgress(t)
        if (t < 1) { requestAnimationFrame(step); return }
        // 3. It settles: anything still held back is drawn in one batch. The
        //    caller frames the settled graph — it owns the landing offset.
        finish()
      }
      // requestAnimationFrame is suspended in a hidden tab, which would skip the
      // whole narration and hand the backstop a finished graph. step() is driven
      // by the clock, not by the frame count, so a timer can drive it too; both
      // sources are idempotent and finish() can only run once.
      requestAnimationFrame(step)
      const tick = setInterval(() => { if (done) clearInterval(tick); else step() }, 60)
    }, hold)
  })
}

// The reveal batch is not reflected in bounding boxes until cytoscape flushes
// it, so a target measured too early frames the seed node alone. Poll until the
// measurement exists, then finish the move.
function land(cy, frame, { instant = false, tries = 24 } = {}) {
  const tick = n => {
    const t = frame && frame()
    if (!t) { if (n > 0) setTimeout(() => tick(n - 1), 25); return }
    cy.stop()
    if (instant) { cy.viewport(t); return }
    cy.animate({ zoom: t.zoom, pan: t.pan }, { duration: 320, easing: 'ease-out', queue: false })
    // rAF-driven animations do not run in a background tab; land there anyway
    setTimeout(() => {
      const t2 = (frame && frame()) || t
      if (Math.abs(cy.zoom() - t2.zoom) > 0.01) { cy.stop(); cy.viewport(t2) }
    }, 420)
  }
  tick(tries)
}
