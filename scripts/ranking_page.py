#!/usr/bin/env python3
"""The scoring page of the ranking studio (31 Oct 2026, lesson UL217; user: "page with score buttons, start with beds
sofas armchairs").

What: ``python3 scripts/ranking_page.py --ranking results/library/ranking --out <dir>/index.html`` writes one HTML page:
a tab per type, a card per model (its tile cut from the lettered sheet ``sheets/<sheet>.jpg``, the sheet and letter,
the title and size) with score buttons 0-10. The page keeps the scores in its database (collection ``scores``, one
document per model id: ``{"rank", "type", "sheet", "letter", "at"}``); Claude reads them back and merges them with
``python -m wenart.furniture.user_ranks merge``. Without the database the page keeps them in the browser and offers
them as text to copy.

How: the sheets stay files beside the page (published with it); a tile is a CSS crop of its sheet (5 x 4 tiles of
``TILE`` px under a ``HEAD`` px band, ``studio.compose_sheets``). Models that did not render are left out.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wenart.assets.audit import studio as S  # noqa: E402

COLS, ROWS, TILE, HEAD = 5, 4, int(S.SETTINGS["sheet_tile_px"]), 56
TYPE_NAMES = {"ours": "Our builds", "bed_double": "Beds", "sofa": "Sofas", "armchair": "Armchairs", "sofa_corner": "Corner sofas",
              "table_coffee": "Coffee tables", "side_table": "Side tables", "tv_unit": "TV units",
              "floor_lamp": "Floor lamps", "ottoman": "Ottomans", "bookshelf": "Bookshelves",
              "console_table": "Console tables", "sideboard": "Sideboards", "display_cabinet": "Display cabinets",
              "chaise": "Chaises", "table_dining": "Dining tables", "chair": "Chairs", "bar_stool": "Bar stools",
              "bench": "Benches", "nightstand": "Nightstands", "wardrobe": "Wardrobes", "dresser": "Dressers",
              "bed_single": "Single beds", "bunk_bed": "Bunk beds", "crib": "Cribs", "desk": "Desks",
              "office_chair": "Office chairs", "shoe_cabinet": "Shoe cabinets", "tall_cabinet": "Tall cabinets",
              "potted_plant": "Plants", "washbasin": "Washbasins", "toilet": "Toilets", "bathtub": "Bathtubs",
              "shower": "Showers", "washing_machine": "Washing machines", "stove": "Stoves",
              "sink_kitchen": "Kitchen sinks", "fridge": "Fridges"}


def models(index: dict, results: dict | None) -> list[dict]:
    rows = (results or {}).get("rows") or {}
    out = []
    for sheet in index["sheets"]:
        for i, (letter, iid) in enumerate(sheet["letters"].items()):
            r = rows.get(iid)
            if r is not None and not (r.get("ok") and r.get("rendered")):
                continue
            m = index["models"][iid]
            row, col = divmod(i, COLS)
            out.append({"id": iid, "type": m.get("type") or sheet["type"],
                        "tab": m.get("group") or m.get("type") or sheet["type"], "sheet": sheet["sheet"], "letter": letter,
                        "title": m.get("title") or "", "size": m.get("size_m"), "source": m.get("source"),
                        "x": round(100.0 * col / (COLS - 1), 4),
                        "y": round(100.0 * (HEAD + row * TILE) / (HEAD + ROWS * TILE - TILE), 4)})
    return out


PAGE = r"""<title>__TITLE__</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
/* Layout: a studio contact sheet: sticky type tabs, then a grid of model cards, each with its 0-10 scale. */
:root {
  --bg: #ecebe8; --panel: #f7f6f4; --ink: #22211f; --muted: #6d6a64; --line: #d6d3cd;
  --accent: #2f5d62; --out: #b4473a; --mid: #8a857b; --good: #3e7d4f; --chip: #22211f; --chip-ink: #f7f6f4;
  --font-ui: "Instrument Sans", "Helvetica Neue", Arial, sans-serif;
  --font-code: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #1c1c1a; --panel: #262624; --ink: #ecebe7; --muted: #a29e96; --line: #3a3936;
  --accent: #7fb3b8; --out: #e07a6c; --mid: #a29e96; --good: #7cc48d; --chip: #ecebe7; --chip-ink: #1c1c1a;
  color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #1c1c1a; --panel: #262624; --ink: #ecebe7; --muted: #a29e96; --line: #3a3936;
  --accent: #7fb3b8; --out: #e07a6c; --mid: #a29e96; --good: #7cc48d; --chip: #ecebe7; --chip-ink: #1c1c1a;
  color-scheme: dark }
body { background: var(--bg); color: var(--ink); font-family: var(--font-ui); font-size: 15px; }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10;
  background: var(--panel); }
.wrap { padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  max-width: 1500px; margin: 0 auto; }
header { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--panel);
  border-bottom: 1px solid var(--line); }
header .wrap { padding-block: 12px; display: grid; gap: 10px; }
.top { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 20px; }
h1 { font-size: 1.35rem; margin: 0; font-weight: 700; letter-spacing: -0.01em; text-wrap: balance; }
.status { font-size: 0.85rem; color: var(--muted); }
.status.bad { color: var(--out); }
.tabs { display: flex; flex-wrap: wrap; gap: 6px; }
.tab { font: 600 0.95rem var(--font-ui); border: 1px solid var(--line); background: transparent; color: var(--ink);
  padding: 7px 12px; border-radius: 999px; cursor: pointer; display: inline-flex; gap: 8px; align-items: center; }
.tab[aria-selected="true"] { background: var(--ink); color: var(--panel); border-color: var(--ink); }
.tab .count { font: 500 0.8rem var(--font-code); opacity: 0.8; font-variant-numeric: tabular-nums; }
.bar { height: 4px; background: var(--line); border-radius: 2px; overflow: hidden; }
.bar > span { display: block; height: 100%; background: var(--accent); width: 0; transition: width .3s; }
.tools { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; font-size: 0.85rem; color: var(--muted); }
.tools label { display: inline-flex; gap: 6px; align-items: center; cursor: pointer; color: var(--ink); }
.tools button { font: 600 0.82rem var(--font-ui); border: 1px solid var(--line); background: var(--bg); color: var(--ink);
  padding: 5px 10px; border-radius: 6px; cursor: pointer; }
.legend { display: inline-flex; gap: 12px; flex-wrap: wrap; }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: -1px; }
main .wrap { padding-block: 18px 48px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; display: grid;
  outline: none; min-width: 0; }
.card:focus-visible, .card.focus { box-shadow: 0 0 0 3px var(--accent); }
.card.ranked { border-color: var(--muted); }
.shot { aspect-ratio: 1; max-width: 100%; background-color: #c9c6c1; background-repeat: no-repeat;
  background-size: 500% auto; position: relative; cursor: zoom-in; }
.chip { position: absolute; left: 8px; bottom: 8px; font: 700 0.8rem var(--font-code); background: var(--chip);
  color: var(--chip-ink); padding: 3px 7px; border-radius: 5px; letter-spacing: 0.02em; }
.score-badge { position: absolute; right: 8px; top: 8px; font: 700 1rem var(--font-code); padding: 3px 9px;
  border-radius: 5px; color: #fff; }
.meta { padding: 10px 10px 4px; display: grid; gap: 2px; min-width: 0; }
.title { font-size: 0.86rem; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; min-height: 2.6em; }
.dims { font: 500 0.75rem var(--font-code); color: var(--muted); font-variant-numeric: tabular-nums; }
.scale { display: grid; grid-template-columns: repeat(11, 1fr); gap: 3px; padding: 8px 10px 10px; }
.scale button { font: 700 0.78rem var(--font-code); padding: 7px 0; border: 1px solid var(--line); border-radius: 5px;
  background: var(--bg); color: var(--ink); cursor: pointer; min-width: 0; font-variant-numeric: tabular-nums; }
.scale button:hover { border-color: var(--ink); }
.scale button:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.scale button.on { color: #fff; border-color: transparent; }
.b-out { background: var(--out) !important; } .b-mid { background: var(--mid) !important; }
.b-good { background: var(--good) !important; }
.empty { padding: 40px 0; color: var(--muted); }
.intro { margin: 0 0 16px; max-width: 70ch; line-height: 1.5; color: var(--ink); }
dialog { border: none; padding: 0; background: transparent; max-width: min(92vw, 820px); }
dialog::backdrop { background: rgba(0,0,0,.7); }
dialog .big { width: min(92vw, 820px); aspect-ratio: 1; background-size: 500% auto; background-repeat: no-repeat;
  border-radius: 8px; }
.copybox { width: 100%; min-height: 120px; font: 0.8rem var(--font-code); margin-top: 8px; }
@media (prefers-reduced-motion: reduce) { .bar > span { transition: none; } }
@media (max-width: 640px) { header { position: static; } .keys { display: none; } .grid { gap: 10px; } }
</style>
<header>
  <div class="wrap">
    <div class="top">
      <h1>__TITLE__</h1>
      <span class="status" id="status">Loading saved scores…</span>
    </div>
    <div class="tabs" id="tabs" role="tablist"></div>
    <div class="bar"><span id="bar"></span></div>
    <div class="tools">
      <label><input type="checkbox" id="unranked"> Unranked only</label>
      <span class="legend">__LEGEND__</span>
      <span class="keys">Keys: select a card, press 0–9, T for 10; the next card follows.</span>
      __NAMEBOX__
      <button type="button" id="copy">__COPY__</button>
    </div>
  </div>
</header>
<main><div class="wrap">
  __INTRO__
  <div class="grid" id="grid"></div>
  <p class="empty" id="empty" hidden>Every model of this type has a score. Untick "Unranked only" to see them all.</p>
  <textarea class="copybox" id="copybox" hidden readonly></textarea>
</div></main>
<dialog id="zoom"><div class="big" id="big"></div></dialog>
<script>
const MODELS = __MODELS__;
const TYPES = __TYPES__;
const NAMES = __NAMES__;
const SHEETS = __SHEETS__;       // null: the sheets are files beside the page; else {sheet: data URI} (one file)
const STORE = __STORE__;         // "models": one document per model (scores/<id>); "rater": one per person
let raterRef = null, saveTimer = null;
const scores = {};             // id -> rank
let db = null, current = TYPES[0], focusIdx = -1;
const $ = (id) => document.getElementById(id);
const band = (r) => r <= 2 ? "b-out" : r <= 5 ? "b-mid" : "b-good";
const LS = "wenart-ranking-scores";
function loadLocal() { try { Object.assign(scores, JSON.parse(localStorage.getItem(LS) || "{}")); } catch (e) {} }
function saveLocal() { try { localStorage.setItem(LS, JSON.stringify(scores)); } catch (e) {} }
function status(text, bad) { const s = $("status"); s.textContent = text; s.classList.toggle("bad", !!bad); }

function renderTabs() {
  const tabs = $("tabs"); tabs.textContent = "";
  for (const t of TYPES) {
    const all = MODELS.filter(m => m.tab === t), done = all.filter(m => scores[m.id] !== undefined).length;
    const b = document.createElement("button");
    b.className = "tab"; b.type = "button"; b.setAttribute("role", "tab");
    b.setAttribute("aria-selected", String(t === current));
    b.append(NAMES[t] || t);
    const c = document.createElement("span"); c.className = "count"; c.textContent = done + "/" + all.length; b.append(c);
    b.onclick = () => { current = t; focusIdx = -1; renderAll(); };
    tabs.append(b);
  }
  const all = MODELS.filter(m => m.tab === current), done = all.filter(m => scores[m.id] !== undefined).length;
  $("bar").style.width = (all.length ? 100 * done / all.length : 0) + "%";
}

function visible() {
  const only = $("unranked").checked;
  return MODELS.filter(m => m.tab === current && (!only || scores[m.id] === undefined));
}

function cardFor(m) {
  const card = document.createElement("article");
  card.className = "card"; card.tabIndex = 0; card.dataset.id = m.id;
  const shot = document.createElement("div"); shot.className = "shot";
  shot.style.backgroundImage = 'url("' + (SHEETS ? SHEETS[m.sheet] : "sheets/" + m.sheet + ".jpg") + '")';
  shot.style.backgroundPosition = m.x + "% " + m.y + "%";
  shot.onclick = () => { const big = $("big"); big.style.backgroundImage = shot.style.backgroundImage;
    big.style.backgroundPosition = shot.style.backgroundPosition; $("zoom").showModal(); };
  const chip = document.createElement("span"); chip.className = "chip"; chip.textContent = m.sheet + " · " + m.letter;
  shot.append(chip);
  const badge = document.createElement("span"); badge.className = "score-badge"; badge.hidden = true; shot.append(badge);
  const meta = document.createElement("div"); meta.className = "meta";
  const title = document.createElement("div"); title.className = "title"; title.textContent = m.title || m.id;
  title.title = m.id + (m.source ? " (" + m.source + ")" : "");
  const dims = document.createElement("div"); dims.className = "dims";
  dims.textContent = m.size ? m.size.map(v => v.toFixed(2)).join(" × ") + " m" : "";
  meta.append(title, dims);
  const scale = document.createElement("div"); scale.className = "scale";
  for (let r = 0; r <= 10; r++) {
    const b = document.createElement("button"); b.type = "button"; b.textContent = r; b.dataset.r = r;
    b.setAttribute("aria-label", "Score " + r + " for " + m.sheet + " " + m.letter);
    b.onclick = (ev) => { ev.stopPropagation(); setScore(m, r, card); };
    scale.append(b);
  }
  card.append(shot, meta, scale);
  card.onfocus = () => { focusIdx = [...$("grid").children].indexOf(card); };
  paint(card, m);
  return card;
}

function paint(card, m) {
  const r = scores[m.id];
  card.classList.toggle("ranked", r !== undefined);
  for (const b of card.querySelectorAll(".scale button")) {
    const on = r !== undefined && Number(b.dataset.r) === r;
    b.className = on ? "on " + band(r) : "";
    b.setAttribute("aria-pressed", String(on));
  }
  const badge = card.querySelector(".score-badge");
  badge.hidden = r === undefined;
  if (r !== undefined) { badge.textContent = r; badge.className = "score-badge " + band(r); }
}

function renderAll() {
  renderTabs();
  const grid = $("grid"); grid.textContent = "";
  const rows = visible();
  for (const m of rows) grid.append(cardFor(m));
  $("empty").hidden = rows.length > 0;
}

let queue = Promise.resolve();
function setScore(m, r, card) {
  const clear = scores[m.id] === r;            // the same score again clears it
  if (clear) delete scores[m.id]; else scores[m.id] = r;
  saveLocal();
  paint(card, m); renderTabs();
  if (!clear) advance(card);
  if (!db) { status(STORE === "rater" ? Object.keys(scores).length + " scores kept in this browser. When you are done, press \u201cCopy my scores\u201d and send them back."
                                      : "Saved in this browser only: copy the scores as text and paste them in the chat.", STORE !== "rater"); return; }
  if (STORE === "rater") { saveRater(); return; }
  const ref = db.collection("scores").doc(m.id);
  queue = queue.then(() => clear ? ref.delete()
    : ref.set({ rank: r, type: m.type, sheet: m.sheet, letter: m.letter, at: Date.now() }))
    .then(() => status(Object.keys(scores).length + " scores saved"))
    .catch((e) => status("Not saved (" + (e && e.code || "error") + "): the score stays in this browser; copy as text.", true));
}

function saveRater() {                         // the whole map, one write per pause
  if (!raterRef) { status("Saved in this browser only: copy the scores as text and send them.", true); return; }
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    const body = { scores: Object.assign({}, scores), count: Object.keys(scores).length, at: Date.now() };
    queue = queue.then(() => raterRef.set(body))
      .then(() => status(body.count + " scores saved"))
      .catch((e) => status("Not saved (" + (e && e.code || "error") + "): the scores stay in this browser; copy them as text.", true));
  }, 600);
}

function advance(card) {
  if ($("unranked").checked) {                 // the card leaves the list: focus the one that takes its place
    const grid = $("grid"), i = [...grid.children].indexOf(card);
    card.remove();
    const next = grid.children[i] || grid.children[i - 1];
    if (next) next.focus(); else $("empty").hidden = false;
    return;
  }
  const next = card.nextElementSibling; if (next) next.focus();
}

document.addEventListener("keydown", (ev) => {
  const card = document.activeElement && document.activeElement.closest && document.activeElement.closest(".card");
  if (!card || ev.metaKey || ev.ctrlKey || ev.altKey) return;
  let r = null;
  if (/^[0-9]$/.test(ev.key)) r = Number(ev.key); else if (ev.key === "t" || ev.key === "T") r = 10;
  if (r === null) return;
  ev.preventDefault();
  const m = MODELS.find(x => x.id === card.dataset.id); if (m) setScore(m, r, card);
});
$("unranked").onchange = () => renderAll();
$("copy").onclick = async () => {
  const lines = [];
  for (const t of TYPES) {
    const bySheet = {};
    for (const m of MODELS.filter(x => x.tab === t && scores[x.id] !== undefined))
      (bySheet[m.sheet] = bySheet[m.sheet] || []).push(m.letter + scores[m.id]);
    for (const [s, v] of Object.entries(bySheet)) lines.push(s + ": " + v.join(" "));
  }
  const who = $("rater") ? ($("rater").value || "").trim() : "";
  if (STORE === "rater" && !who) { status("Write your name first, so your scores can be told apart.", true); $("rater").focus(); return; }
  const text = (who ? "Name: " + who + "\n" : "") + (lines.join("\n") || "(no scores yet)");
  const box = $("copybox"); box.value = text; box.hidden = false;
  try { await navigator.clipboard.writeText(text); status("Scores copied"); } catch (e) { box.select(); }
};
$("zoom").onclick = () => $("zoom").close();

loadLocal();
if ($("rater")) {
  try { $("rater").value = localStorage.getItem(LS + "-name") || ""; } catch (e) {}
  $("rater").oninput = () => { try { localStorage.setItem(LS + "-name", $("rater").value); } catch (e) {} };
}
renderAll();
(async () => {
  db = window.claude && window.claude.use ? await window.claude.use("db") : null;
  if (!db) { status(STORE === "rater" ? "Your scores stay in this browser. When you are done, press \u201cCopy my scores\u201d and send them back."
                                      : "Scores are kept in this browser; copy them as text to send them.", !SHEETS); return; }
  let timer = setTimeout(() => status("Saved scores can't be reached yet; new scores are kept.", true), 10000);
  if (STORE === "rater") {
    const user = window.claude && window.claude.use ? await window.claude.use("user") : null;
    const uid = user ? await user.id() : null;
    if (!uid) { clearTimeout(timer); status("Sign in to save your scores; until then they stay in this browser.", true); return; }
    raterRef = db.collection("ratings").doc(uid);
    let first = true;
    raterRef.onSnapshot((snap) => {
      if (first) {                               // your saved scores, once; later snapshots echo your own writes
        const v = snap.exists ? snap.data() : null;
        if (v && v.scores) for (const [k, r] of Object.entries(v.scores)) if (Number.isInteger(r)) scores[k] = r;
        if (!snap.metadata || !snap.metadata.fromCache) { first = false; clearTimeout(timer);
          status(Object.keys(scores).length + " scores saved"); }
        saveLocal();
        for (const card of $("grid").children) { const m = MODELS.find(x => x.id === card.dataset.id); if (m) paint(card, m); }
        renderTabs();
        if (!first && v && Object.keys(scores).length > Object.keys(v.scores || {}).length) saveRater();
      }
    }, (e) => { clearTimeout(timer); status("Saving unavailable (" + (e && e.code) + "); your scores stay in this browser.", true); });
    return;
  }
  db.collection("scores").onSnapshot((snap) => {
    for (const d of snap.docs) { const v = d.data(); if (v && Number.isInteger(v.rank)) scores[d.id] = v.rank; }
    if (!snap.metadata || !snap.metadata.fromCache) { clearTimeout(timer); status(snap.size + " scores saved"); }
    saveLocal();
    for (const card of $("grid").children) { const m = MODELS.find(x => x.id === card.dataset.id); if (m) paint(card, m); }
    renderTabs();
  }, (e) => { clearTimeout(timer); status("Saved scores unavailable (" + (e && e.code) + "); new scores stay in this browser.", true); });
})();
</script>
"""


OWNER_LEGEND = ('<span><i style="background:var(--out)"></i>0–2 never used</span>'
                '<span><i style="background:var(--mid)"></i>3–5 kept, below unranked at 5</span>'
                '<span><i style="background:var(--good)"></i>6–10 preferred</span>')
RATER_LEGEND = ('<span><i style="background:var(--out)"></i>0 = would never pick it</span>'
                '<span><i style="background:var(--good)"></i>10 = love it</span>')
RATER_INTRO = ('<p class="intro">Score each piece from 0 to 10, purely on how it looks to you. There are no wrong '
               'answers. Your scores save as you go, so you can stop and come back on the same device. Click a picture '
               'to see it bigger. When you are done, write your name and press \u201cCopy my scores\u201d, then send the '
               'copied text back to the person who asked you.</p>')
# 31 Oct 2026 (user: "For the old one give another link i will send to some one else to get opinion 2 opinions will
# avarage later"): the rater page: one document per person (ratings/<viewer id> = {"scores": {model id: rank}}), the
# owner reads every person's document, a person only their own.
RATER_RULES = [{"path": "ratings", "read": "admin", "write": "owner"},
               {"path": "ratings/{self}", "read": "view", "write": "interact"}]


NAMEBOX = ('<label for="rater">Your name <input id="rater" type="text" autocomplete="name" maxlength="40" '
           'style="font:inherit;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);'
           'color:var(--ink);width:12em"></label>')


def sheet_uris(folder: Path, sheets: list[str]) -> dict:
    """``{sheet: data URI}`` of the sheet JPEGs (the one-file page)."""
    import base64
    return {s: "data:image/jpeg;base64," + base64.b64encode((folder / f"{s}.jpg").read_bytes()).decode("ascii")
            for s in sheets}


def page(rows: list[dict], types: list[str], rater: bool = False, sheets: dict | None = None) -> str:
    title = "Furniture Look Survey" if rater else "Furniture Ranking"
    return (PAGE.replace("__SHEETS__", json.dumps(sheets) if sheets else "null")
            .replace("__NAMEBOX__", NAMEBOX if rater else "")
            .replace("__COPY__", "Copy my scores" if rater else "Copy scores as text")
            .replace("__MODELS__", json.dumps(rows, separators=(",", ":")))
            .replace("__TYPES__", json.dumps(types)).replace("__NAMES__", json.dumps(TYPE_NAMES))
            .replace("__STORE__", json.dumps("rater" if rater else "models")).replace("__TITLE__", title)
            .replace("__LEGEND__", RATER_LEGEND if rater else OWNER_LEGEND)
            .replace("__INTRO__", RATER_INTRO if rater else ""))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranking", default="results/library/ranking")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rater", action="store_true", help="a page for another person's opinion (one document each)")
    ap.add_argument("--types", default="", help="only these types (comma list)")
    ap.add_argument("--inline", action="store_true", help="one file: the sheets inside the page (to send by mail)")
    a = ap.parse_args(argv)
    rk = Path(a.ranking)
    # 31 Oct 2026: the library's index and our builds' (ranking_index_<tag>.json, first: the tab to score now)
    pairs = []
    for f in sorted(rk.glob("ranking_index_*.json")) + [rk / "ranking_index.json"]:
        suffix = f.stem[len("ranking_index"):]
        res_path = rk / f"studio_results{suffix}.json"
        pairs.append((json.loads(f.read_text(encoding="utf-8")),
                      json.loads(res_path.read_text(encoding="utf-8")) if res_path.is_file() else None))
    index = {"types": [t for i, _r in pairs for t in (["ours"] if any(m.get("group") for m in i["models"].values())
                                                       else i["types"])]}
    rows = [m for i, r in pairs for m in models(i, r)]
    if a.types:
        rows = [m for m in rows if m["tab"] in a.types.split(",")]
    types = [t for t in dict.fromkeys(index["types"]) if any(m["tab"] == t for m in rows)]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    inline = sheet_uris(rk / "sheets", sorted({m["sheet"] for m in rows})) if a.inline else None
    out.write_text(page(rows, types, a.rater, inline), encoding="utf-8")
    sheets = sorted({m["sheet"] for m in rows})
    print(json.dumps({"page": str(out), "models": len(rows), "types": types, "sheets": sheets}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
