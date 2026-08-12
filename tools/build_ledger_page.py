#!/usr/bin/env python3
"""Generate web/public/ledger.html — the public construction & verification ledger.

Record-first: every published reference with the gates it passed (mechanical quote
check, independent gate with verifier+date, voice sweep, cross-vendor check, human
validation, dispute history), searchable client-side. Batch history follows as a
second section, with links to the underlying git commits. Carries the same
provenance disclosure the paper makes. Run after any merge; ships with the atlas.

R9.5: two record types are shown and kept visibly apart — a TEXT RELATION gated
against its cited paragraph, and a FAMILY ASSIGNMENT made over an already-verified
relation. The second is a classification of the first, never a re-verification of
the text, and the page must not let them read as the same kind of evidence.

Writes web/public/ledger.html ONLY. web/public/v1.3/ledger.html is the frozen
published snapshot and is never written by this script.
"""
import html
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/damianspendel/symbolic-world"

state = json.load(open(ROOT / "pipeline" / "state.json"))
seed = json.load(open(ROOT / "seed.json"))
labels = {n["id"]: n.get("label", n["id"]) for n in seed["nodes"]}
refs_total = sum(len(e["references"]) for e in seed["edges"])

val = json.load(open(ROOT / "web" / "public" / "validations.json"))
HUMAN = {}
for v in val.get("validations", []):
    HUMAN[(v["key"], str(v["volume"]), str(v["paragraph"]))] = v

disp = json.load(open(ROOT / "web" / "public" / "disputes.json"))
DISPUTES = {}
for d in disp.get("disputes", []):
    for k in d.get("current_edges") or []:
        DISPUTES.setdefault(k, []).append(d)


def esc(s):
    return html.escape(str(s))


# ---------- section 1: every record and its gates ----------
# R9.5 — family-assignment state, rendered as its own row class so a reader can
# never mistake a classification for a gate against the text.
FAM_STATE_NOTE = {
    "pending-adjudication": "the two model arms disagreed — queued for Human review, not yet judged",
    "no-family": "a well-formed relation the family vocabulary does not cover",
    "text-undecided": "the paragraph itself hedges between families",
    "not-a-relation": "the relation slot holds a clause; excluded from every family denominator",
}


def fam_note(fstate, by):
    """RULES.md #10: the tooltip states what THIS edge's record says, never a
    blanket claim. 'Verified' belongs to the quote layer; families are assigned."""
    if fstate != "assigned":
        return FAM_STATE_NOTE.get(fstate, "")
    b = (by or "").lower()
    # precedent is tested BEFORE human: a precedent record names the sitting it
    # came from ("precedent (human-adjudication 2026-08-10: ...)"), so testing
    # for "human" first swallows it and the tooltip claims a ruling nobody made
    if "precedent" in b:
        return "settled by a recorded precedent from Human review"
    if "human" in b:
        return "Human review: a person ruled this classification after the model arms disagreed"
    if "disputes" in b:
        return "the arms agreed but the check disputed the agreement — treat as contested"
    return "two model arms, judging independently, assigned the same family; a classification, not a re-verification of the text"
fam_counts = {}

xv_n = human_n = 0
edge_cards = []
for e in seed["edges"]:
    key = f'{e["subject"]}|{e["relation"]}|{e["object"]}'
    rows = []
    for r in e["references"]:
        chips = ['<span class="chip c-ok" title="Deterministic letter-normalized quote check; collage and over-elision rejected; canary-guarded">quote ✓</span>']
        chips.append(f'<span class="chip c-ok" title="Independent full-paragraph review by a different model family">gate ✓ {esc(r.get("verified_by", "?"))} · {esc(r.get("verified_date", ""))}</span>')
        if r.get("modality_swept"):
            chips.append('<span class="chip c-ok" title="Narrow voice/hedge audit (E3 sweep or stage-2 specialist)">voice ✓</span>')
        if r.get("crossvendor_checked"):
            chips.append(f'<span class="chip c-xv" title="{esc(r["crossvendor_checked"])}">cross-vendor ✓ gemini</span>')
            xv_n += 1
        hv = HUMAN.get((key, str(r["volume"]), str(r["paragraph"])))
        if hv:
            human_n += 1
            cls = {"supported": "c-hum", "partly": "c-part"}.get(hv["support"], "c-bad")
            chips.append(f'<span class="chip {cls}" title="Author gold-set validation (E10), {esc(hv["date"])}">human · {esc(hv["support"])}</span>')
        if r.get("quote_repaired"):
            chips.append('<span class="chip c-part" title="Quote repaired to strongest contiguous fragment after the 2026-07-28 elision-bound fix; re-gated">repaired + re-gated</span>')
        rows.append(f'<div class="refrow"><span class="cite">CW {esc(r["volume"])} §{esc(r["paragraph"])}</span>'
                    f'<span class="ctype">{esc(r["claim_type"])}</span>{"".join(chips)}</div>')
    dchips = "".join(
        f'<div class="drow" title="{esc(d["objection"])}">⚖ disputed ({esc(d["date"])}, {esc(d["outcome"])}) — <a href="/disputes">log</a></div>'
        for d in DISPUTES.get(key, []))

    # the family-assignment record, visually a different kind of row
    fam = e.get("relation_family")
    famrow = ""
    famsearch = ""
    if fam:
        fstate = fam.get("state") or ("assigned" if fam.get("value") else "")
        fval = fam.get("value") or fstate.replace("-", " ")
        fam_counts[fstate] = fam_counts.get(fstate, 0) + 1
        cls = "f-ok" if fstate == "assigned" else ("f-pend" if fstate == "pending-adjudication" else "f-none")
        by = fam.get("by", "")
        date = fam.get("date", "")
        famrow = (f'<div class="famrow" title="{esc(fam_note(fstate, by))}">'
                  f'<span class="flabel">family</span>'
                  f'<span class="chip {cls}">{esc(fval)}</span>'
                  f'<span class="fmeta">{esc(by)}{" · " + esc(date) if date else ""} — classification only; '
                  f'the relation above was already gated against its paragraph</span></div>')
        famsearch = f' family:{fval} {fstate}'
    edge_cards.append(
        f'<div class="ecard" data-s="{esc(labels.get(e["subject"], e["subject"]))} {esc(e["relation"])} {esc(labels.get(e["object"], e["object"]))} cw{" cw".join({str(r["volume"]) for r in e["references"]})}{esc(famsearch)}">'
        f'<div class="edge">{esc(labels.get(e["subject"], e["subject"]))} <span class="rel">{esc(e["relation"])}</span> {esc(labels.get(e["object"], e["object"]))}</div>'
        f'{"".join(rows)}{dchips}{famrow}</div>')

# ---------- section 2: batch history ----------
def commits_for(batch):
    out = subprocess.run(["git", "log", "--reverse", "--date=short", "--pretty=%h\t%ad\t%s",
                          "-F", "--grep", batch["id"]],
                         capture_output=True, text=True, cwd=ROOT).stdout.strip()
    rows = [line.split("\t", 2) for line in out.splitlines() if line]
    if not rows and batch.get("candidates"):
        out = subprocess.run(["git", "log", "--reverse", "--date=short", "--pretty=%h\t%ad\t%s",
                              "--follow", "--", batch["candidates"]],
                             capture_output=True, text=True, cwd=ROOT).stdout.strip()
        rows = [line.split("\t", 2) for line in out.splitlines() if line]
    return rows


batch_cards = []
for b in reversed(state["batches"]):
    rows = commits_for(b)
    commit_html = ""
    if rows:
        links = " · ".join(f'<a href="{REPO_URL}/commit/{sha}" title="{esc(subj)}">{sha}</a>'
                           f'<span class="cdate"> {date}</span>' for sha, date, subj in rows[:6])
        more = f' <span class="cdate">(+{len(rows)-6} more)</span>' if len(rows) > 6 else ""
        commit_html = f'<div class="commits"><b>commits</b> {links}{more}</div>'
    story = b.get("result") or b.get("note") or ""
    window = f'<span class="cite">{esc(b["window"])}</span>' if b.get("window") else ""
    batch_cards.append(f"""  <div class="card">
    <div class="row2"><span class="bid">{esc(b["id"])}</span>{window}
      <span class="badge b-{esc(b["status"])}">{esc(b["status"])}</span></div>
    {f'<p class="res">{esc(story)}</p>' if story else ""}
    {commit_html}
  </div>""")

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://symbolicworld.observer/ledger">
<title>Ledger — The Symbolic World</title>
<link rel="stylesheet" href="./chrome.css">
<style>
  /* R10.0 — palette and chrome come from chrome.css, generated from the one
     token table in web/build-atlas.mjs. No colour is restated here. */
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ min-height:100vh; }}
  main {{ max-width: 900px; margin: 0 auto; padding: 2rem 1.2rem 4rem; }}
  .eyebrow {{ font:.6rem/1 var(--mono); letter-spacing:.26em; text-transform:uppercase; color:var(--gold-dim); }}
  h1 {{ color:var(--ink); font-family:var(--display); font-size:2rem; font-weight:500; margin:.3rem 0 .8rem; letter-spacing:-.01em; }}
  h2 {{ color:var(--ink); font-family:var(--display); font-size:1.3rem; font-weight:500; margin:2.4rem 0 .3rem; }}
  .kinds {{ display:grid; grid-template-columns:1fr 1fr; gap:.7rem; margin:1rem 0 1.2rem; }}
  @media (max-width:700px) {{ .kinds {{ grid-template-columns:1fr; }} }}
  .kind {{ border:1px solid var(--hairline); border-radius:8px; padding:.7rem .85rem; }}
  .kind h3 {{ font:.6rem var(--mono); letter-spacing:.16em; text-transform:uppercase; margin-bottom:.3rem; }}
  .kind.k-text {{ border-left:3px solid var(--gold); }}
  .kind.k-text h3 {{ color:var(--gold); }}
  .kind.k-fam {{ border-left:3px solid var(--m-substance); }}
  .kind.k-fam h3 {{ color:var(--m-substance); }}
  .kind p {{ font-size:.82rem; line-height:1.55; color:var(--ink-faint); }}
  .intro {{ font-size:.92rem; line-height:1.6; color:var(--ink); max-width:66ch; margin-bottom:.5rem; }}
  .meta {{ font:.62rem var(--mono); color:var(--ink-faint); margin-bottom:1rem; }}
  a {{ color:var(--gold); }}
  #q {{ width:100%; max-width:30rem; background:var(--panel); color:var(--ink); border:1px solid var(--hairline);
       border-radius:8px; padding:.5rem .8rem; font:inherit; font-size:.9rem; margin:.4rem 0 1rem; }}
  .ecard, .card {{ background:var(--surface); border:1px solid var(--hairline); border-radius:10px;
          padding:.7rem .9rem; margin:.5rem 0; }}
  .edge {{ font-size:.98rem; color:var(--ink); margin-bottom:.25rem; }}
  .rel {{ color:var(--gold); font-style:italic; }}
  .bid {{ font-size:.95rem; color:var(--ink); font-family:var(--mono); }}
  .cite {{ font:.62rem var(--mono); color:var(--gold-dim); margin-right:.55rem; white-space:nowrap; }}
  .ctype {{ font:.58rem var(--mono); color:var(--ink-faint); margin-right:.55rem; }}
  .refrow {{ display:flex; align-items:baseline; flex-wrap:wrap; gap:.3rem; padding:.18rem 0; }}
  .chip {{ font:.56rem var(--mono); letter-spacing:.03em; padding:.1rem .42rem; border-radius:99px;
          border:1px solid var(--hairline); white-space:nowrap; cursor:default; }}
  .c-ok {{ color:var(--sage); border-color:var(--b-ok); }}
  .c-xv {{ color:var(--teal); border-color:var(--b-teal); }}
  .c-hum {{ color:var(--sage); border-color:var(--b-sage); }}
  .c-part {{ color:var(--gold); border-color:var(--b-amber); }}
  .c-bad {{ color:var(--rubedo); border-color:var(--b-rubedo); }}
  .drow {{ font:.62rem var(--mono); color:var(--rubedo); margin-top:.25rem; }}
  /* R9.5 — the family-assignment record is a different kind of row and looks it:
     indented, verdigris-keyed, and captioned as classification, not gating. */
  .famrow {{ display:flex; align-items:baseline; flex-wrap:wrap; gap:.4rem;
            margin-top:.4rem; padding:.35rem .55rem; border-radius:0 6px 6px 0;
            border-left:3px solid var(--m-substance); background:rgba(99,153,127,.06); }}
  .flabel {{ font:.55rem var(--mono); letter-spacing:.14em; text-transform:uppercase; color:var(--m-substance); }}
  .fmeta {{ font:.56rem var(--mono); color:var(--ink-dim); }}
  .f-ok {{ color:var(--m-substance); border-color:var(--b-ok); }}
  .f-pend {{ color:var(--amber); border-color:var(--b-amber); }}
  .f-none {{ color:var(--ink-dim); border-style:dashed; }}
  .row2 {{ display:flex; gap:.6rem; align-items:baseline; flex-wrap:wrap; margin:.1rem 0 .3rem; }}
  .badge {{ font:.58rem var(--mono); letter-spacing:.06em; padding:.12rem .45rem; border-radius:99px;
           border:1px solid var(--hairline); white-space:nowrap; }}
  .b-merged {{ color:var(--sage); border-color:var(--b-sage); }}
  .b-complete {{ color:var(--teal); border-color:var(--b-teal); }}
  .res {{ font-size:.82rem; line-height:1.5; color:var(--ink); }}
  .commits {{ font:.62rem var(--mono); color:var(--ink-faint); margin-top:.35rem; line-height:1.8; }}
  .commits b {{ font-size:.56rem; letter-spacing:.08em; text-transform:uppercase; margin-right:.3rem; }}
  .cdate {{ color:var(--ink-faint); }}
  .hidden {{ display:none; }}
</style>
</head>
<body>
<div class="page-bar"><a class="back" href="/#/atlas">← the atlas</a><span class="where">ledger</span></div>
<main>
  <h1>Ledger</h1>
  <p class="intro">Every published record and the gates it passed. Nothing entered this graph by an
  unrecorded path.</p>
  <p class="intro">Two different kinds of record appear on every card below, and they are not the
  same kind of evidence:</p>
  <div class="kinds">
    <div class="kind k-text">
      <h3>Text relation</h3>
      <p>A claim about what Jung wrote, gated against the paragraph it cites. The quote is checked
      mechanically, then a model of a different family reads the full paragraph and judges whether it
      supports the claim, in the right direction, in the right voice. This is the verification the
      project's method claim is about.</p>
    </div>
    <div class="kind k-fam">
      <h3>Family assignment</h3>
      <p>A classification of a relation that is <em>already</em> verified — which kind of relation it
      is, drawn from a fixed vocabulary. Two model arms classify blind, a calibrated gate checks them,
      and a human rules where they disagree. It says nothing new about the text and never re-opens the
      gate above it.</p>
    </div>
  </div>
  <p class="intro">Each reference shows its full verification passage: the deterministic
  <b>quote</b> check, the independent <b>gate</b> (verifier and date), the narrow <b>voice</b> audit,
  the second-vendor <b>cross-vendor</b> check, and — where a person has checked the paragraph —
  <b>human</b> validation from the gold set. Disputed records link to the
  <a href="/disputes">dispute log</a>. Hover any chip for detail.</p>
  <p class="intro">Disclosure, mirrored from the paper: verification timestamps for batches gated
  before 2026-07-26 were batch-backfilled rather than recorded per-operation (the verification is
  real; those timestamps are reconstructions). Since then, stamps are written by the operations
  they describe, and any post-verification edit triggers re-gating.</p>
  <div class="meta">{len(seed["nodes"])} nodes · {len(seed["edges"])} edges · {refs_total} references ·
    100% gate-verified · {xv_n} cross-vendor checked · {human_n} human-validated ·
    {len(disp.get("disputes", []))} disputes on record ·
    {fam_counts.get("assigned", 0)} family-assigned · {fam_counts.get("pending-adjudication", 0)} awaiting a ruling ·
    {fam_counts.get("no-family", 0) + fam_counts.get("text-undecided", 0)} unclassified ·
    <a href="{REPO_URL}/commits/master">full commit history</a></div>

  <h2>Records</h2>
  <input id="q" type="search" placeholder="Filter records — try a symbol, a relation, or cw14…" autocomplete="off">
  <div id="records">
{chr(10).join(edge_cards)}
  </div>

  <h2>Batch history</h2>
  <p class="intro">The batch-level transaction log: each entry is one batch's passage
  through the pipeline (<i>input-built → mined → pre-checked → gated → merged</i>), with the
  underlying commits. Experiment entries record audits and calibrations against the published
  graph; designs and results are in the <a href="{REPO_URL}/blob/master/docs/PAPER.md">paper</a>.</p>
{chr(10).join(batch_cards)}
</main>
<script>
const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const t = q.value.trim().toLowerCase();
  document.querySelectorAll('.ecard').forEach(c => {{
    c.classList.toggle('hidden', t && !c.dataset.s.toLowerCase().includes(t));
  }});
}});
</script>
</body>
</html>
"""
out = ROOT / "web" / "public" / "ledger.html"
out.write_text(page)
print(f"built {out.relative_to(ROOT)}: {len(seed['edges'])} edge records, {len(state['batches'])} batches, "
      f"{human_n} human chips, {sum(len(v) for v in DISPUTES.values())} dispute rows")
