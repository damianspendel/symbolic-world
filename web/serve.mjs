// Minimal zero-dependency static server for the built single-file Atlas.
// Serves web/dist (everything resolves to index.html — the build is one file).
// Usage: node serve.mjs [port]   (default 8788, the port the cloudflared
// ingress rule for the Atlas points at).
import { createServer } from 'http'
import { readFileSync, existsSync, statSync } from 'fs'
import { extname, join, normalize } from 'path'
import { fileURLToPath } from 'url'

const PORT = Number(process.argv[2] || process.env.PORT || 8788)
// fileURLToPath (not URL.pathname) so paths with spaces — e.g. ~/Library/
// "Application Support" — decode correctly instead of keeping %20.
const ROOT = fileURLToPath(new URL('./dist/', import.meta.url))
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon' }

createServer((req, res) => {
  let path
  try { path = decodeURIComponent((req.url || '/').split('?')[0]) }
  catch { res.writeHead(400); res.end('bad request'); return }
  let file = normalize(join(ROOT, path))
  // Extensionless URLs are the site's convention (CLAUDE.md, 2026-08-10) and
  // Cloudflare Pages serves /ontology from ontology.html. Do the same here, or a
  // dev build answers every generated page with the atlas shell and the reader
  // sees a landing view where a page should be — which is exactly how the
  // "the header does not hold on ontology" report reproduced.
  if (file.startsWith(ROOT) && !existsSync(file) && existsSync(file + '.html')) file += '.html'
  if (!file.startsWith(ROOT) || !existsSync(file) || statSync(file).isDirectory()) file = join(ROOT, 'index.html')
  try {
    const body = readFileSync(file)
    res.writeHead(200, { 'content-type': MIME[extname(file)] || 'application/octet-stream', 'cache-control': 'no-cache' })
    res.end(body)
  } catch (e) {
    res.writeHead(500); res.end('server error')
  }
}).listen(PORT, '127.0.0.1', () => console.log(`Atlas static server → http://127.0.0.1:${PORT}  (serving ${ROOT})`))
