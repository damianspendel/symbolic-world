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

V2-R3 (2026-08-13): the cards gain client-side facets over fields they already
carry, a permalink anchor per record, and an assignment-history chip that renders
only when an edge actually carries `relation_family.history`.

Writes web/public/ledger.html ONLY. web/public/v1.3/ledger.html is the frozen
published snapshot and is never written by this script.
"""
import datetime
import html
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/damianspendel/symbolic-world"
# The support link follows web/build-atlas.mjs's single knob (2026-10-21):
# read from the source so the two generators cannot disagree; empty = absent.
SUPPORT_URL = re.search(r"^const SUPPORT_URL = '([^']*)'$",
                        (ROOT / "web" / "build-atlas.mjs").read_text(), re.M).group(1)
SUPPORT_LINK = ('\n    <a href="/support">support</a>' if SUPPORT_URL else "")


def esc(s):
    return html.escape(str(s))


# V2-R10 — the site menu, in one place for Python. web/build-atlas.mjs holds the
# same list for the pages node writes, and a test compares the two rendered
# menus link for link, so a route added to one and forgotten in the other fails
# the suite rather than stranding a page.
# The taxonomy (editorial ruling, 2026-08-13): four groups, fixed order, the
# same list web/build-atlas.mjs holds for the pages node writes. Batches are
# deliberately not a menu item — they are reached from the ledger's facet links
# and from the release entries that shipped them.
MENU = [
    ("explore", [("/#/atlas", "atlas"), ("/routes", "routes"),
                 ("/query", "query"), ("/#/concordance", "concordance")]),
    ("reference", [("/concepts", "concepts"), ("/families", "families")]),
    ("provenance", [("/ledger", "ledger"), ("/releases", "releases"),
                    ("/disputes", "disputes")]),
    ("about", [("/nutshell", "in a nutshell"), ("/#/method", "method"),
               ("/ontology", "design")]
              + ([("/support", "support")] if SUPPORT_URL else [])),
]


def site_header(current="", where="", tools=""):
    """V2-R11 — the header fragment, the same structure web/build-atlas.mjs
    emits: row one is brand then menu and is identical on every surface; row two
    carries the breadcrumb, which is the part that varies."""
    return (
        '<header class="site-header">'
        '<div class="hrow hrow-1"><a class="brand" href="/">The Symbolic World</a>'
        f'{top_menu(current)}</div>'
        f'<div class="hrow hrow-2"><span class="where">{where}</span>'
        + (f'<span class="hdr-tools">{tools}</span>' if tools else "")
        + "</div></header>")


def top_menu(current=""):
    out = ['<nav class="topmenu">']
    for group, items in MENU:
        out.append(f'<span class="mgroup">{group}</span>')
        for href, label in items:
            current_mark = ' aria-current="page"' if href == current else ""
            out.append(f'<a href="{href}"{current_mark}>{label}</a>')
    out.append("</nav>")
    return "".join(out)


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


# ---------- V2-R3: facets, permalinks, assignment history ----------
# Every facet reads a field the card already shows. Nothing here aggregates into
# a claim: selecting a facet narrows the cards on screen, and the counts in the
# strip above them stay graph-wide, so a filtered view can never read as a total.

def slug(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(text).lower())).strip("-")


def record_id(edge, taken):
    """A stable anchor per record: subject, relation and object, which are the
    three fields that identify an edge everywhere else in the project. Ids are
    de-duplicated with a numeric suffix so a permalink always names one card."""
    base = f'e-{slug(edge["subject"])}-{slug(edge["relation"])}-{slug(edge["object"])}'
    ident, n = base, 1
    while ident in taken:
        n += 1
        ident = f"{base}-{n}"
    taken.add(ident)
    return ident


def parse_window(window):
    """('CW12 §321-331 + §421-446') -> [('12', 321, 331), ('12', 421, 446)]."""
    m = re.match(r"\s*CW\s*([0-9]+i*)", window or "")
    if not m:
        return []
    vol = m.group(1)
    return [(vol, int(a), int(b))
            for a, b in re.findall(r"§\s*(\d+)\s*-\s*(\d+)", window)]


def batch_windows(state):
    """[(batch id, volume, first paragraph, last paragraph)] for the batches that
    declare a paragraph window. The CW 14 sets and the incidental volumes were
    merged before the windowed pipeline and declare none, so their records carry
    no batch chip rather than a guessed one."""
    out = []
    for b in state["batches"]:
        for vol, lo, hi in parse_window(b.get("window")):
            out.append((b["id"], vol, lo, hi))
    return out


def batches_for(references, windows):
    hits = []
    for r in references:
        vol, para = str(r["volume"]), int(r["paragraph"])
        for bid, bvol, lo, hi in windows:
            if bvol == vol and lo <= para <= hi and bid not in hits:
                hits.append(bid)
    return hits


def provenance_facets(fam):
    """How this record was arrived at, read off `relation_family.by`. An
    unrecognised provenance is reported as itself rather than folded into the
    commonest case. `reassigned` is DERIVED — from a recorded history entry, or
    from a `by` string that names a re-run — and the page labels it as derived."""
    by = (fam.get("by") or "").strip()
    b = by.lower()
    keys = []
    if "precedent" in b:
        keys.append("precedent")
    elif "human" in b:
        keys.append("human-adjudication")
    elif "disputes" in b:
        keys.append("gate-disputes-agreed")
    elif b.startswith("opus+gemini-agreed"):
        keys.append("opus+gemini-agreed")
    elif "calibration-flag" in b:
        keys.append("calibration-flag")
    elif "arms-disagree" in b:
        keys.append("arms-disagree")
    elif by:
        keys.append(by)
    if fam.get("history") or re.search(r"re-?run|re-?audit", b):
        keys.append("reassigned")
    return keys


def history_chip(fam):
    """The assignment-history chip, rendered ONLY when the edge carries
    `relation_family.history`. Writing that field is the mining pipeline's job;
    until an edge has one, no chip is drawn and nothing on the page infers a
    prior assignment from anywhere else. The chip shows the latest transition
    and counts the rest, because the transition that matters to a reader is the
    one that produced what they are looking at."""
    hist = fam.get("history") or []
    if not hist:
        return ""

    def label(entry):
        value = entry.get("value") or entry.get("state") or "?"
        version = (entry.get("ruleset") or entry.get("version")
                   or entry.get("definitions_version") or "")
        return f"{value} ({version})" if version else str(value)

    previous = label(hist[-1])
    current = label({"value": fam.get("value") or fam.get("state"),
                     "version": fam.get("ruleset") or fam.get("version") or ""})
    earlier = f' · {len(hist) - 1} earlier' if len(hist) > 1 else ""
    return (f'<span class="chip f-hist" title="Every reassignment appends a '
            f'{{value, ruleset version, date, by}} entry. The text relation is '
            f'untouched by a reassignment and is not re-verified by one.">'
            f'history: {esc(previous)} → {esc(current)}{esc(earlier)}</span>')


def facet_row(label, name, items, note="", link=None):
    if not items:
        return ""
    chips = "".join(
        f'<button class="facet" type="button" data-g="{esc(name)}" data-v="{esc(value)}">'
        f'{esc(value)}{f" <span class=n>·{count}</span>" if count is not None else ""}</button>'
        + (f'<a class="flink" href="{link(value)}" title="the delta page for {esc(value)}">↗</a>'
           if link else "")
        for value, count in items)
    return (f'<div class="facetrow"><span class="lab">{esc(label)}</span>{chips}'
            f'{f"<span class=fnote>{esc(note)}</span>" if note else ""}</div>')


def volume_key(v):
    """V2-R8 — collection order, and the only place Python defines it. A CW
    volume is a position in an edition, not a string: sorted as text "11" lands
    before "5" and "9ii" before "9i", which puts Aion ahead of the Archetypes
    volume and reads as an error to anyone who knows the edition. Every list of
    volumes this generator writes sorts through here."""
    m = re.match(r"^(\d+)(i*)$", str(v))
    if not m:
        return 999.0
    return int(m.group(1)) + (0.2 if m.group(2) == "ii" else 0.1 if m.group(2) == "i" else 0.0)


# ---------- V2-R7: the per-batch delta pages ----------
# The batch history used to sit at the foot of the ledger, which put a mining
# narrative under 1,555 record cards on a page that is already long. It moves to
# one page per batch, generated here from the same pass over the same data, and
# the ledger keeps the batch facet and a link. One generator, one set of
# numbers, three places that link to it: the facet strip, the delta index, and
# the release entry that shipped the batch.

def batch_slug(batch_id):
    return f"batch-{slug(batch_id)}"


def batch_page(batch, delta, commits):
    """One batch: what it declared, what it merged, and what the graph carries
    from it now. The delta is derived — records with at least one reference
    inside the batch's declared paragraph window — so a batch that declared no
    window gets the record it wrote and no derived count, rather than a guess."""
    window = batch.get("window") or ""
    story = batch.get("result") or batch.get("note") or ""
    commit_rows = "".join(
        f'<tr><td class="n"><a href="{REPO_URL}/commit/{sha}">{sha}</a></td>'
        f'<td class="n">{esc(date)}</td><td>{esc(subject)}</td></tr>'
        for sha, date, subject in commits)

    if delta is None:
        derived_block = (
            '<h2>What the graph carries from it</h2>'
            '<p class="dim">This batch declares no paragraph window. The windowed pipeline '
            'came later, so the records it merged cannot be identified from the graph without '
            'guessing, and nothing is derived here. Its commits are below.</p>')
    else:
        fam_chips = "".join(
            f'<span class="chip">{esc(name)} <span class="n">{count}</span></span>'
            for name, count in delta["families"])
        state_rows = "".join(
            f'<tr><td>{esc(name)}</td><td class="n">{count}</td></tr>'
            for name, count in delta["states"])
        derived_block = f"""<h2>What the graph carries from it</h2>
  <div class="nums">
    <span><b>{delta["records"]}</b> records cite this window</span>
    <span><b>{delta["references"]}</b> references fall inside it</span>
    <span><b>{len(delta["families"])}</b> families over those records</span>
  </div>
  <p class="note">A record is counted here when at least one of its references falls in the
  window. A record citing two windows is counted under both, so these figures do not partition
  the graph and do not add up to it. The family layer was applied later and in its own passes:
  the mix below is what those records carry today, not what this batch decided.</p>
  <div class="tw"><table><thead><tr><th>family state</th><th>records</th></tr></thead>
  <tbody>{state_rows}</tbody></table></div>
  <div class="mix">{fam_chips}</div>"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://symbolicworld.observer/{batch_slug(batch["id"])}">
<title>{esc(batch["id"])} · a batch delta · The Symbolic World</title>
<link rel="stylesheet" href="./chrome.css">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ min-height:100vh; }}
  /* face, size and colour come from the shared scale in chrome.css; the batch
     id inside the heading keeps the mono face, because it is an identifier */
  h1 {{ margin:.3rem 0 .5rem; }}
  h1 .idtok {{ font-family:var(--mono); font-size:1.5rem; }}
  h2 {{ margin:2rem 0 .5rem; }}
  p {{ font-size:.92rem; line-height:1.62; }}
  a {{ color:var(--gold); }}
  .meta {{ font:.62rem/1.7 var(--mono); color:var(--ink-faint); }}
  .dim {{ color:var(--ink-faint); }}
  .badge {{ font:.58rem var(--mono); letter-spacing:.06em; padding:.12rem .45rem; border-radius:99px;
           border:1px solid var(--hairline); white-space:nowrap; }}
  .cite {{ font:.62rem var(--mono); color:var(--gold-dim); }}
  .story {{ border-left:2px solid var(--hairline); padding:.2rem 0 .2rem .9rem; margin:.6rem 0 1rem;
           font-size:.9rem; line-height:1.6; color:var(--ink); }}
  .nums {{ display:flex; flex-wrap:wrap; gap:.5rem 1.1rem; margin:.6rem 0; font:.62rem var(--mono); color:var(--ink-faint); }}
  .nums b {{ color:var(--ink); font-weight:400; }}
  .note {{ font-size:.82rem; color:var(--ink-faint); }}
  .mix {{ display:flex; flex-wrap:wrap; gap:.3rem; margin:.6rem 0 0; }}
  .chip {{ font:.56rem var(--mono); padding:.12rem .46rem; border-radius:99px;
          border:1px solid var(--hairline); color:var(--ink-faint); }}
  .chip .n {{ color:var(--ink-dim); }}
  .tw {{ overflow-x:auto; margin:.6rem 0 1rem; }}
  table {{ border-collapse:collapse; width:100%; font-size:.86rem; }}
  th, td {{ border-bottom:1px solid var(--hairline); padding:.35rem .5rem; text-align:left; }}
  th {{ font:.55rem var(--mono); letter-spacing:.12em; text-transform:uppercase; color:var(--ink-dim); }}
  td.n {{ font-family:var(--mono); font-size:.76rem; }}
  .sitenav {{ margin-top:3rem; border-top:1px solid var(--hairline); padding-top:1rem;
             display:flex; flex-wrap:wrap; gap:.3rem .9rem; font:.62rem var(--mono); }}
  .sitenav a {{ color:var(--ink-faint); text-decoration:none; }}
  .sitenav a:hover {{ color:var(--gold); }}
</style>
</head>
<body>
{site_header("/ledger", f'<a href="/ledger">ledger</a> · {esc(batch["id"])}')}
<main class="page-main prose">
  <div class="titleband"><p class="eyebrow">batch delta</p>
  <h1><span class="idtok">{esc(batch["id"])}</span></h1></div>
  <div class="meta">{f'<span class="cite">{esc(window)}</span> · ' if window else ''}<span class="badge">{esc(batch["status"])}</span></div>
  {f'<h2>What it merged</h2><div class="story">{esc(story)}</div>' if story else ''}
  {derived_block}
  <h2>Commits</h2>
  {f'<div class="tw"><table><thead><tr><th>commit</th><th>date</th><th>subject</th></tr></thead><tbody>{commit_rows}</tbody></table></div>'
     if commit_rows else '<p class="dim">No commit names this batch.</p>'}
  <p class="note">Every claim this batch merged is on the <a href="/ledger">ledger</a> with the
  gates it passed; this page is the batch-level record around them. Releases that shipped it link
  here from <a href="/releases">the release notes</a>.</p>
  <nav class="sitenav"><a href="/">the atlas</a>
    <a href="/ledger">ledger</a>
    <a href="/releases">releases</a>
    <a href="/concepts">concepts</a>
    <a href="/families">families</a>
    <a href="/routes">routes</a>
    <a href="/query">query</a>
    <a href="/ontology">design</a>{SUPPORT_LINK}</nav>
</main>
</body>
</html>
"""


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


def build():
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

    windows = batch_windows(state)
    by_batch = {}          # V2-R7 — the derived delta behind each batch page
    fam_counts = {}
    facet_counts = {g: {} for g in ("vol", "batch", "ct", "state", "family", "prov")}

    def tally(group, value):
        facet_counts[group][value] = facet_counts[group].get(value, 0) + 1

    xv_n = human_n = 0
    edge_cards = []
    taken_ids = set()
    for e in seed["edges"]:
        key = f'{e["subject"]}|{e["relation"]}|{e["object"]}'
        ident = record_id(e, taken_ids)
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
            f'<div class="drow" title="{esc(d["objection"])}">⚖ disputed ({esc(d["date"])}, {esc(d["outcome"])}): <a href="/disputes">log</a></div>'
            for d in DISPUTES.get(key, []))

        # the family-assignment record, visually a different kind of row
        fam = e.get("relation_family")
        famrow = ""
        famsearch = ""
        fstate = ""
        if fam:
            fstate = fam.get("state") or ("assigned" if fam.get("value") else "")
            fval = fam.get("value") or fstate.replace("-", " ")
            fam_counts[fstate] = fam_counts.get(fstate, 0) + 1
            cls = "f-ok" if fstate == "assigned" else ("f-pend" if fstate == "pending-adjudication" else "f-none")
            rowcls = "" if fstate == "assigned" else (" pend" if fstate == "pending-adjudication" else " none")
            by = fam.get("by", "")
            date = fam.get("date", "")
            famrow = (f'<div class="famrow{rowcls}" title="{esc(fam_note(fstate, by))}">'
                      f'<span class="flabel">family</span>'
                      f'<span class="chip {cls}">{esc(fval)}</span>'
                      f'{history_chip(fam)}'
                      f'<span class="fmeta">{esc(by)}{" · " + esc(date) if date else ""}. Classification only; '
                      f'the relation above was already gated against its paragraph</span></div>')
            famsearch = f' family:{fval} {fstate}'

        # facet values, all read off fields the card already displays
        vols = sorted({str(r["volume"]) for r in e["references"]}, key=volume_key)
        ctypes = sorted({r["claim_type"] for r in e["references"] if r.get("claim_type")})
        bids = batches_for(e["references"], windows)
        for bid in bids:
            d = by_batch.setdefault(bid, {"records": 0, "references": 0,
                                          "families": {}, "states": {}})
            d["records"] += 1
            d["references"] += sum(
                1 for r in e["references"]
                for wbid, wvol, lo, hi in windows
                if wbid == bid and wvol == str(r["volume"]) and lo <= int(r["paragraph"]) <= hi)
            key = (fam or {}).get("value")
            if key:
                d["families"][key] = d["families"].get(key, 0) + 1
            st = (fam or {}).get("state") or "unrecorded"
            d["states"][st] = d["states"].get(st, 0) + 1
        provs = provenance_facets(fam or {})
        fvalue = (fam or {}).get("value") or ""
        for v in vols:
            tally("vol", v)
        for b in bids:
            tally("batch", b)
        for c in ctypes:
            tally("ct", c)
        for p in provs:
            tally("prov", p)
        if fstate:
            tally("state", fstate)
        if fvalue:
            tally("family", fvalue)

        edge_cards.append(
            f'<div class="ecard" id="{ident}"'
            f' data-vol="{esc(" ".join(vols))}" data-batch="{esc(" ".join(bids))}"'
            f' data-ct="{esc(" ".join(ctypes))}" data-state="{esc(fstate)}"'
            f' data-family="{esc(fvalue)}" data-prov="{esc(" ".join(provs))}"'
            # the volume list is sorted: an unordered set made this page differ
            # between two builds of the same graph, which buries a real change
            f' data-s="{esc(labels.get(e["subject"], e["subject"]))} {esc(e["relation"])} {esc(labels.get(e["object"], e["object"]))} cw{" cw".join(vols)}{esc(famsearch)}">'
            f'<a class="anchor" href="#{ident}" title="permalink to this record"><span class="id">#{ident}</span>§</a>'
            f'<div class="edge">{esc(labels.get(e["subject"], e["subject"]))} <span class="rel">{esc(e["relation"])}</span> {esc(labels.get(e["object"], e["object"]))}</div>'
            f'{"".join(rows)}{dchips}{famrow}</div>')

    def ordered(group, key=None, limit=None):
        items = sorted(facet_counts[group].items(),
                       key=key or (lambda kv: (-kv[1], kv[0])))
        return items[:limit] if limit else items

    facets = "".join([
        facet_row("volume", "vol", sorted(facet_counts["vol"].items(),
                                          key=lambda kv: volume_key(kv[0]))),
        facet_row("batch", "batch", ordered("batch", key=lambda kv: kv[0]),
                  "windowed batches only; earlier batches declare no paragraph range. "
                  "↗ opens the batch's delta page",
                  link=lambda bid: "/" + batch_slug(bid)),
        facet_row("claim type", "ct", ordered("ct")),
        facet_row("state", "state", ordered("state")),
        facet_row("family", "family", ordered("family")),
        facet_row("provenance", "prov", ordered("prov"),
                  "reassigned is derived from the provenance string or a recorded history entry"),
    ])

    # V2-R7 — one delta page per batch, and an index row per batch for the
    # ledger. The batch narrative leaves this page; what stays is the facet and
    # the link.
    batch_rows = []
    written_ids = []
    written = 0
    for b in reversed(state["batches"]):
        has_window = bool(parse_window(b.get("window")))
        delta = None
        if has_window:
            d = by_batch.get(b["id"], {"records": 0, "references": 0, "families": {}, "states": {}})
            delta = {
                "records": d["records"], "references": d["references"],
                "families": sorted(d["families"].items(), key=lambda kv: (-kv[1], kv[0])),
                "states": sorted(d["states"].items(), key=lambda kv: (-kv[1], kv[0])),
            }
        (ROOT / "web" / "public" / f'{batch_slug(b["id"])}.html').write_text(
            batch_page(b, delta, commits_for(b)))
        written_ids.append(b["id"])
        written += 1
        window = f'<span class="cite">{esc(b["window"])}</span>' if b.get("window") else ""
        counts = (f'<span class="bnums">{delta["records"]} records · {delta["references"]} references</span>'
                  if delta else '<span class="bnums dimmer">no declared window</span>')
        batch_rows.append(
            f'  <div class="brow"><a class="bid" href="/{batch_slug(b["id"])}">{esc(b["id"])}</a>'
            f'{window}<span class="badge b-{esc(b["status"])}">{esc(b["status"])}</span>{counts}</div>')

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://symbolicworld.observer/ledger">
<meta name="description" content="The build ledger of The Symbolic World, a verified knowledge graph of Jung&#39;s Collected Works: every verified reference in the graph, with the batch that added it and its verification record.">
<title>Ledger · The Symbolic World</title>
<link rel="stylesheet" href="./chrome.css">
<style>
  /* R10.0 — palette and chrome come from chrome.css, generated from the one
     token table in web/build-atlas.mjs. No colour is restated here. */
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ min-height:100vh; }}
  /* face, size and colour come from the shared scale in chrome.css */
  h1 {{ margin:.3rem 0 .8rem; }}
  h2 {{ margin:2.4rem 0 .3rem; }}
  .kinds {{ display:grid; grid-template-columns:1fr 1fr; gap:.7rem; margin:1rem 0 1.2rem; }}
  @media (max-width:700px) {{ .kinds {{ grid-template-columns:1fr; }} }}
  .kind {{ border:1px solid var(--hairline); border-radius:8px; padding:.7rem .85rem; }}
  .kind h3 {{ font:.6rem var(--mono); letter-spacing:.16em; text-transform:uppercase; margin-bottom:.3rem; }}
  .kind.k-text {{ border-left:3px solid var(--gold); }}
  .kind.k-text h3 {{ color:var(--gold); }}
  .kind.k-fam {{ border-left:3px solid var(--m-substance); }}
  .kind.k-fam h3 {{ color:var(--m-substance); }}
  .kind p {{ font-size:.82rem; line-height:1.55; color:var(--ink-faint); }}
  .intro {{ font-size:.92rem; line-height:1.6; color:var(--ink); margin-bottom:.5rem; }}
  .meta {{ font:.62rem var(--mono); color:var(--ink-faint); margin-bottom:1rem; }}
  a {{ color:var(--gold); }}
  /* the filter input is styled by the shared .std-search rule in chrome.css */
  /* V2-R3 — the facet strip. Facets filter; they never aggregate into a claim. */
  .facets {{ display:flex; flex-direction:column; gap:.4rem; margin:.3rem 0 1rem;
            padding-bottom:.9rem; border-bottom:1px solid var(--hairline); }}
  .facetrow {{ display:flex; flex-wrap:wrap; align-items:center; gap:.32rem; }}
  .facetrow .lab {{ font:.55rem var(--mono); letter-spacing:.13em; text-transform:uppercase;
                   color:var(--ink-dim); width:5.6rem; flex:none; }}
  .facet {{ font:.58rem var(--mono); padding:.16rem .5rem; border-radius:99px;
           border:1px solid var(--hairline); color:var(--ink-faint); background:transparent; cursor:pointer; }}
  .facet.on {{ color:var(--gold); border-color:var(--gold-dim); background:rgba(212,175,55,.08); }}
  .facet .n {{ color:var(--ink-dim); }}
  .fnote {{ font:.55rem var(--mono); color:var(--ink-dim); }}
  .facthow {{ font:.6rem/1.7 var(--mono); color:var(--ink-faint); margin:-.5rem 0 1rem; }}
  .ecard, .card {{ background:var(--surface); border:1px solid var(--hairline); border-radius:10px;
          padding:.7rem .9rem; margin:.5rem 0; }}
  .ecard {{ position:relative; }}
  .ecard:target {{ border-color:var(--gold-dim); }}
  .anchor {{ position:absolute; top:.55rem; right:.7rem; text-decoration:none;
            color:var(--ink-dim); font:.8rem var(--mono); }}
  .anchor:hover {{ color:var(--gold); }}
  .anchor .id {{ font:.52rem var(--mono); color:var(--ink-dim); margin-right:.3rem; opacity:0; }}
  .ecard:hover .anchor .id {{ opacity:1; }}
  .edge {{ font-size:.98rem; color:var(--ink); margin-bottom:.25rem; padding-right:1.6rem; }}
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
  .famrow.pend {{ border-left-color:var(--amber); background:rgba(217,168,79,.06); }}
  .famrow.none {{ border-left-color:var(--ink-dim); background:rgba(111,106,93,.06); }}
  .flabel {{ font:.55rem var(--mono); letter-spacing:.14em; text-transform:uppercase; color:var(--m-substance); }}
  .famrow.pend .flabel {{ color:var(--amber); }}
  .famrow.none .flabel {{ color:var(--ink-dim); }}
  .fmeta {{ font:.56rem var(--mono); color:var(--ink-dim); }}
  .f-ok {{ color:var(--m-substance); border-color:var(--b-ok); }}
  .f-pend {{ color:var(--amber); border-color:var(--b-amber); }}
  .f-none {{ color:var(--ink-dim); border-style:dashed; }}
  .f-hist {{ color:var(--m-motif); border-color:var(--m-motif); }}
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
  .flink {{ font:.62rem var(--mono); color:var(--ink-dim); text-decoration:none; margin:0 .35rem 0 -.1rem; }}
  .flink:hover {{ color:var(--gold); }}
  .brows {{ display:flex; flex-direction:column; gap:.15rem; margin-top:.6rem; }}
  .brow {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:.55rem;
          padding:.35rem .2rem; border-bottom:1px solid var(--hairline); }}
  .brow .bid {{ font:.78rem var(--mono); color:var(--gold); text-decoration:none; min-width:11rem; }}
  .brow .bid:hover {{ text-decoration:underline; }}
  .bnums {{ font:.6rem var(--mono); color:var(--ink-faint); margin-left:auto; }}
  .bnums.dimmer {{ color:var(--ink-dim); }}
  .sitenav {{ margin-top:3rem; border-top:1px solid var(--hairline); padding-top:1rem;
             display:flex; flex-wrap:wrap; gap:.3rem .9rem; font:.62rem var(--mono); }}
  .sitenav a {{ color:var(--ink-faint); text-decoration:none; }}
  .sitenav a:hover {{ color:var(--gold); }}
</style>
</head>
<body>
{site_header("/ledger", "ledger")}
<main class="page-main records">
  <div class="titleband"><p class="eyebrow">provenance</p>
  <h1>Ledger</h1>
  <p class="sub">Every published record and the gates it passed.</p></div>
  <p class="intro">Two different kinds of record appear on every card below:</p>
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
      <p>A classification of a relation that is <em>already</em> verified: which kind of relation it
      is, drawn from a fixed vocabulary. Two model arms classify blind, a calibrated gate checks them,
      and a human rules where they disagree. It says nothing new about the text and never re-opens the
      gate above it.</p>
    </div>
  </div>
  <p class="intro">Each reference shows its full verification trail: the deterministic
  <b>quote</b> check, the independent <b>gate</b> (verifier and date), the narrow <b>voice</b> audit,
  the <b>cross-vendor</b> check, and, where a person has checked the paragraph,
  <b>human</b> validation from the gold set. Disputed records link to the
  <a href="/disputes">dispute log</a>.</p>
  <div class="meta">{len(seed["nodes"])} nodes · {len(seed["edges"])} edges · {refs_total} references ·
    100% gate-verified · {xv_n} cross-vendor checked · {human_n} human-validated ·
    {len(disp.get("disputes", []))} disputes on record ·
    {fam_counts.get("assigned", 0)} family-assigned · {fam_counts.get("pending-adjudication", 0)} awaiting a ruling ·
    {fam_counts.get("no-family", 0) + fam_counts.get("text-undecided", 0)} unclassified ·
    <a href="{REPO_URL}/commits/master">full commit history</a></div>

  <h2>Records</h2>
  <div class="facets">
    <div class="facetrow"><span class="lab">filter</span>
      <input id="q" class="std-search facet-filter" type="search"
             placeholder="a symbol, a relation, a family, cw14…" autocomplete="off"></div>
{facets}
  </div>
  <p class="facthow">The text filter is the broadest control here and the rows under it narrow
  further: chips in one row combine with OR, rows combine with AND, and the filter applies to
  whatever they leave. The counts beside a chip are graph-wide and do not change as you
  filter, so a filtered view can never read as a total. A volume count is records citing that
  volume, so a record with references in two volumes is counted under both. Every card carries a
  § permalink.</p>
  <div id="records">
{chr(10).join(edge_cards)}
  </div>

  <h2>Batches</h2>
  <p class="intro">Each batch is one passage through the pipeline (<i>input-built → mined →
  pre-checked → gated → merged</i>). The narrative, the commits behind it and what the graph
  carries from it are on the batch's own page; the batch facet above filters these records to
  the ones it merged. Experiment entries record audits and calibrations against the published
  graph; designs and results are in the <a href="{REPO_URL}/blob/master/docs/PAPER.md">paper</a>.</p>
  <div class="brows">
{chr(10).join(batch_rows)}
  </div>
  <nav class="sitenav"><a href="/">the atlas</a>
    <a href="/concepts">concepts</a>
    <a href="/families">families</a>
    <a href="/releases">releases</a>
    <a href="/routes">routes</a>
    <a href="/query">query</a>
    <a href="/ontology">design</a>
    <a href="/disputes">disputes</a>{SUPPORT_LINK}</nav>
</main>
<script>
const q = document.getElementById('q');
const cards = Array.from(document.querySelectorAll('.ecard'));
const chosen = {{}};   // group -> Set of selected values

function apply() {{
  const t = q.value.trim().toLowerCase();
  for (const card of cards) {{
    let show = !t || card.dataset.s.toLowerCase().includes(t);
    for (const [group, values] of Object.entries(chosen)) {{
      if (!show || !values.size) continue;
      const carried = (card.dataset[group] || '').split(' ').filter(Boolean);
      show = carried.some(v => values.has(v));
    }}
    card.classList.toggle('hidden', !show);
  }}
}}

q.addEventListener('input', apply);
for (const button of document.querySelectorAll('.facet')) {{
  button.addEventListener('click', () => {{
    const group = button.dataset.g, value = button.dataset.v;
    const values = chosen[group] || (chosen[group] = new Set());
    if (values.has(value)) {{ values.delete(value); button.classList.remove('on'); }}
    else {{ values.add(value); button.classList.add('on'); }}
    apply();
  }});
}}
</script>
</body>
</html>
"""
    # V2-R7 / item 9 — the manifest the deploy preflight gates on. It records
    # what this run wrote and the graph it wrote it from, so a dist carrying a
    # stale or incomplete set of batch pages cannot pass the gate. It is not a
    # second source of truth: state.json remains the list of batches, and this
    # file is the receipt for one run of this generator.
    manifest = {
        "_about": "Batch delta pages written by tools/build_ledger_page.py. "
                  "tools/pages/preflight.py refuses a deploy whose dist does not "
                  "carry exactly these pages, derived from this many edges.",
        "generated": datetime.date.today().isoformat(),
        "source": "tools/build_ledger_page.py",
        "seed_edges": len(seed["edges"]),
        "seed_nodes": len(seed["nodes"]),
        "count": len(written_ids),
        "ids": written_ids,
        "pages": [f"{batch_slug(bid)}.html" for bid in written_ids],
    }
    (ROOT / "web" / "public" / "batch_pages.json").write_text(
        json.dumps(manifest, indent=1) + "\n")

    out = ROOT / "web" / "public" / "ledger.html"
    out.write_text(page)
    print(f"built {out.relative_to(ROOT)}: {len(seed['edges'])} edge records, {written} batch delta pages, "
          f"{human_n} human chips, {sum(len(v) for v in DISPUTES.values())} dispute rows, "
          f"{sum(len(v) for v in facet_counts.values())} facet chips over "
          f"{len([1 for c in facet_counts['batch']])} windowed batches")
    return page


if __name__ == "__main__":
    build()
