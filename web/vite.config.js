import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

// Relative base so the built site works from any static host.
// viteSingleFile inlines JS/CSS/data into one self-contained index.html
// (shareable as an artifact; no server or separate files needed).
// The entry is atlas.html (the app, at /atlas since 2026-10-23). The root is a
// static landing page that build-atlas.mjs writes to public/index.html.
export default defineConfig({
  base: './',
  plugins: [viteSingleFile()],
  build: { rollupOptions: { input: 'atlas.html' } }
})
