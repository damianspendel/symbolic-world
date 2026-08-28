# Method poster — handoff to the v2.0 release ceremony

Written 2026-08-28 by the infographic session (jungkg-56). The poster is
FINISHED as an artifact; what remains is fact-alignment at tag time,
integration into the method page, and deployment. Those belong to the
ceremony because it owns all deployment tasks. Damian approved the handoff
2026-08-28 ("send the task over to JungKG 2.0 release ceremony").

## Files (this directory, untracked until the ceremony commits them)

| File | What |
|---|---|
| `method_poster.html` | Source, self-contained (Google Fonts only). Master, with film grain. |
| `method_poster_web.html` | Same file minus the `.grain` div — the web-render source. |
| `method_poster_print.png` | Master render, 2160×5426 @2x, 10.2 MB. Share/print only, never a page asset. |
| `method_poster_web.png` | Web asset: grain-free @2x render, 256-color quantized, 0.70 MB. |

## Placement (proposed 2026-08-28, Damian saw the proposal and said "finish")

The existing `/#/method` page — NOT a new route; the menu's about→method
entry already exists and V2-R10 stays untouched. Add a figure at the end of
the **"How a claim gets in"** section:

1. `docs/METHOD_COPY.md`: a `[figure: the method, on one page]` marker at
   the end of that section.
2. `web/build-atlas.mjs` (method-page block, ~line 940): render the marker
   as `<figure class="fig"><a href="/method-poster.png"><img
   src="/method-poster.png" alt="…"></a><figcaption>…</figcaption></figure>`.
   Suggested alt: "Poster: one real claim — lapis, is projection of, the
   self — followed through proposal, a second-family check, a cross-vendor
   audit, and human refereeing, ending with its published receipt."
   Suggested caption: "The method on one page. Counts as of v2.0, August
   2026." The build already refuses to draw the page's claim figure if the
   lapis edge leaves the graph; that same guard protects this poster's
   subject.
3. Copy `method_poster_web.png` to `web/public/method-poster.png` (vite
   copies public/ into dist; the 3 MB preflight ceiling covers only the
   inlined index.html, so no gate change).

## Facts baked into the image — CHECK THESE AGAINST TAG-TIME STATE

The numbers are pixels: no token substitution, no copy-contract scan can
see them. If any fact below has moved at tag time, edit the HTML and
re-render (commands at the bottom).

- **589 concepts · 2,091 claims · 2,678 verified quotes · 9 volumes** —
  from seed.json at 035fc38 (2026-08-28). Any merged window moves these.
- **The followed claim**: `lapis | is-projection-of | the-self`,
  CW 9ii §264, quote "we would say that the stone is a projection of the
  unified self". Verified, Gemini SUPPORTED (pre-merge, b-cw9ii-4,
  2026-08-05). Same edge as the method page's existing "One claim, drawn"
  figure — deliberate reinforcement, not an accident.
- **Map-fragment edges** (all in seed.json, all verified):
  lapis→the-self `is-projection-of`; lapis→christ `is-parallel-to`;
  lapis→mercurius `is-identical-with`; lapis→four-elements `composed-of`;
  lapis→the-opus `is-goal-of`; chaos→lapis `gives-birth-to`.
- **Pipeline naming**: proposed (Claude, Opus family) → checked (Claude,
  Fable family) → audited (Google Gemini) → refereed (a human). Matches
  the pipeline/README.md invariant.
- **Citation register**: the poster writes "Collected Works vol. 9,
  part II · ¶264" (general-reader form; "9II" in caps misread as 911).
  The page copy writes "CW 9ii §264". Kept as audience-tuning by default;
  Damian has not explicitly ruled — reversible with one re-render if he
  wants them aligned.

## Re-render commands

Skill lives at
`~/.claude/plugins/cache/epic-infographics/epic-infographics/0.2.0/skills/epic-infographics`
(deps already installed). From that directory:

    node scripts/check.mjs docs/figures/method_poster.html --preset tall
    node scripts/render.mjs docs/figures/method_poster.html method_poster_print.png --preset tall
    node scripts/render.mjs docs/figures/method_poster_web.html web2x.png --preset tall

then quantize the web render:

    python3 -c "from PIL import Image; Image.open('web2x.png').convert('RGB').quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE).save('method_poster_web.png', optimize=True)"

If you edit copy, keep `method_poster_web.html` in sync (it is the same
file minus `<div class="grain"></div>`), and re-run check.mjs before
rendering — it must come back 0 errors.

## Constraints that still bind

- This is a UI change: the standing data-only redeploy authorization does
  NOT cover it. Damian reviews before any deploy that carries it.
- Stage named paths only. The paper session's fig*.svg files share this
  directory — do not sweep them.
- The public URL convention is extensionless; the PNG is an asset, not a
  page — no sitemap or canonical entry.
