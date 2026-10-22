"""The audit's code checks (docs/milestone12.md §6.1, D21): what code can say about each model without a vision model.

What: ``run_checks(items, cfg, measures=None)`` -> ``{id: [record]}``; a record is ``{"check", "status", "reason",
"fix"?, "metrics"?}`` with ``status`` one of ``ok``, ``warn``, ``fix`` (a catalogue field to change), ``remove``,
``review`` (code cannot decide: the vision answer does, ``decide.py``) or ``skip`` (nothing to check).

Checks: ``licence`` (NC / SA / ND / unknown -> remove: user decision of 10 Oct 2026), ``title`` (the type and the
flags in any language, ``keywords.py``), ``title_size`` (an ABO title's size in cm vs the box), ``size`` (the box vs
the real-size table: the uniform scale to the ranges, the front convention, the up axis; ``sizes.py``), ``pivot``
(``origin_offset`` at the bottom centre; with the render's measurement, the box itself), ``up`` (``up_axis`` +Z),
``front`` (a type with a front needs a known one), ``units`` (known, guessed or normalised), ``quality`` (the M8-M10
judges), ``source`` (a generated model is no real product), ``mesh`` (crude face count; with the render: broken
meshes, open edges, parts outside the main body), ``textures`` (present, resolution, missing files) and
``duplicate`` (same type, box +- 1 cm, faces +- 1 %, same texture: the lower-ranked copies are removed).

Without ``measures`` (the CPU dry audit) the checks use the catalogue fields only; with the render's measurements
(``render.py``: ``measure/<id>.json``) the box, the pivot, the mesh and the textures are measured.

Milestone 13 gates (docs/milestone13.md §5.1 phase 2, §13.1 track T7; ``audit.yaml gates``): ``units_anchor``
(an anchor type of guessed units is removed: code evidence), ``pbr`` (the PBR maps of the model recorded per model:
``pbr_maps`` from the catalogue step's ``glbmesh.pbr_maps`` or the render's ``measure["pbr"]``, a missing base colour
a warning, the record a ``fix`` that writes the field), ``material_tags`` (every entry needs judged material tags:
``review`` until the vision answer's ``materials`` names them, decision 1a: never a removal), ``chaise``
(an L-sofa needs its chaise side: a warning the fit reads), ``licence_fields`` (the Milestone 13 licence fields of
every entry: a warning; the fields are written by ``python -m wenart.furniture licence-fields`` and the growth
entries). Decision 1a of 11 Oct 2026 stays: vision findings keep the model with ``vision_doubt``.

Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8; P3 showed a Disney CARS cushion, a "Sporting Goods"
wire rack as a bookshelf and a gold bathtub rendered as mirror metal, all audited ``keep`` or ``fix``):

- What: the title flags ``branded`` (a licensed brand or character) and ``other_use`` (a product made for another
  use than a home) are hard flags (``title_flag`` with status ``remove``: ``decide`` gives ``removed``); the check
  ``sanitary_finish`` removes a bathtub, washbasin or toilet (``SANITARY_TYPES``) whose main material is metal: the
  title names a metal finish (``keywords.metal_finish``: gold / oro, chrome, brass, copper, nickel, stainless ...)
  and no part (tap, faucet, feet ...) and no non-metal body (acrylic, ceramic, enamel ...), or the Milestone 10 slot
  judgement's largest slot (``material_slots``, share >= ``METAL_MAIN_SHARE``, both judges agreeing) is metal (a
  metal slot the judges disagree on is a note).
- Why: the audit saw licence, size, units and PBR maps but no brand, no purpose and no surface; the vision check kept
  all three (decision 1a keeps vision doubts). A licence covers the mesh, not a trademark (§2.6); glazed sanitary
  ware is ceramic (the shell's ``ceramic`` slot), a metal one renders as a mirror.
- How: code evidence from the catalogue fields the audit already reads (title, ``material_slots``); the catalogue has
  no per-material metallic factor, so a model whose title is silent and whose slots were never judged is not
  flagged (the final vision check still sees it). The status values are the audit's own (``removed``); no new one.

Fix round after P5 (22 Oct 2026; the library lens of P5: the SMEG logo readable on a fridge in
cam_r_L-1_mutfak_3, chalk lettering on the "Chalk Board Coffee Table" in the oyun views, both audited ``keep``):

- What: the check ``render_print`` reads the entry field ``render_findings`` (catalogue data: what a run's render
  showed on the model) and removes a model with a ``brand_logo`` (a maker's logo or brand name readable on the
  model) or a ``text_print`` (decorative lettering on its visible surface; the functional labels of an appliance's
  control panel are no finding). A record counts only with its evidence: the run, project and view it was seen in
  (``seen_in``) or the mesh it shares with such a model (``same_mesh_as``: faces, vertices and model box equal to the
  entry's own), and the ``sha256_glb`` of the file it was seen on. A record without evidence, of an unknown kind or
  of another file (the model was republished) is a warning, never a removal.
- Why: the audit's ``branded`` flag reads titles only (licensed characters); a manufacturer's logo modelled into
  the mesh or printed on the texture is a trademark too (docs/milestone13.md §2.6: trademarks are not licensed), and
  a text print fits no project style; no catalogue fix (front, scale, type) can take either away. The status is the
  audit's own (``removed``); the model file stays on the volume.
- How: per item, from its own fields (no vision call, no file read), so a later audit write gives the same
  decision (``decision_sha``) and keeps the model out.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from wenart.assets.audit import keywords as K
from wenart.assets.audit.items import has_front
from wenart.furniture import sizes as SZ

NOT_ALLOWED = (("-NC", "non-commercial"), ("-SA", "share-alike"), ("-ND", "no-derivatives"))
SOURCE_RANK = {"abo": 0, "polyhaven": 1, "gso": 2, "hssd": 3, "objaverse": 4, "generated": 5}   # hssd: M13
HARD_FLAGS = ("outdoor", "crude", "wrong", "part", "branded", "other_use")    # branded, other_use: fix round after P3
FLAG_TEXT = {"outdoor": "an outdoor piece", "crude": "not photoreal", "wrong": "not the object",
             "part": "a part of a piece", "scene": "several objects (a set or a scene)",
             "branded": "a licensed brand or character print (trademarks are not licensed, docs/milestone13.md §2.6)",
             "other_use": "a product made for another use than a home, not the type it is filed as"}
# Fix round after P3: sanitary ware is glazed ceramic; a metal main material renders as a mirror (sanitary_finish_check)
SANITARY_TYPES = ("bathtub", "washbasin", "toilet")
METAL_MAIN_SHARE = 0.5
# Fix round after P5 (22 Oct 2026): what a run's render showed on a model (render_print_check; entry render_findings)
RENDER_FINDINGS = {
    "brand_logo": "a maker's logo or brand name on the model",
    "text_print": "printed lettering on the model's visible surface",
}
RENDER_FINDING_WHY = {
    "brand_logo": "trademarks are not licensed (docs/milestone13.md §2.6)",
    "text_print": "a novelty print fits no project style and no catalogue fix removes it",
}
SAME_MESH_KEYS = ("polycount", "vertices", "bbox_model_m")


def rec(check: str, status: str, reason: str = "", **extra) -> dict:
    out = {"check": check, "status": status, "reason": reason}
    out.update({k: v for k, v in extra.items() if v is not None})
    return out


def _fmt(box) -> str:
    return " x ".join(f"{float(v):.2f}" for v in box)


# --------------------------------------------------------------------------
# Licence, title, source, quality
# --------------------------------------------------------------------------

def licence_reason(licence: Optional[str], flag: Optional[str] = None) -> Optional[str]:
    """The removal reason of a licence no licence mode may use (None: allowed in some mode). Milestone 13
    (docs/milestone13.md §6, §12 D1; ``wenart.furniture.catalog``): a no-derivatives licence (we scale and
    re-texture) and a licence nobody could read (unknown, Sketchfab-Standard) are never usable; a non-commercial or
    share-alike licence stays in the catalogue with its flag (``relaxed`` mode only: ``catalog.usable(entry,
    mode)`` keeps it out of ``commercial`` mode). Before Milestone 13 every NC / SA / ND licence was removed (user
    decision of 10 Oct 2026); the entries removed then stay removed until a new audit decides them."""
    from wenart.furniture import catalog as C
    lic = str(licence or "")
    f = flag if flag in C.LICENCE_FLAGS or flag == C.UNKNOWN_FLAG else C.licence_text_flag(lic)
    if f in C.NEVER_USABLE_FLAGS:
        if f == "no_derivatives":
            return f"licence {lic} forbids derivatives: never usable (we scale and re-texture; docs/milestone13.md §6)"
        return f"licence {lic or 'missing'} not shown to allow any use (unknown): never usable"
    return None


def licence_check(item: dict) -> dict:
    from wenart.furniture import catalog as C
    flag = C.licence_flag_of({k: item.get(k) for k in ("licence", "licence_flag", "source", "generated") if k in item})
    why = licence_reason(item.get("licence"), flag)
    if why:
        return rec("licence", "remove", why, metrics={"flag": flag})
    note = "" if flag == C.NO_FLAG else f" ({flag}: relaxed licence mode only, not commercial-safe)"
    return rec("licence", "ok", f"{item.get('licence')}{note}", metrics={"flag": flag})


def title_check(item: dict, known_types) -> list[dict]:
    """The title's verdict and flags (records ``title`` and ``title_flag``)."""
    chk = K.title_check(item.get("title"), item["type"], item.get("source", ""))
    out = []
    v = chk["verdict"]
    metrics = {"verdict": v, "families": chk["families"], "words": chk["words"]}
    if v == "conflict":
        sug = K.suggested_type(chk, item["kind"], known_types)
        box = item.get("bbox_m")
        if sug and box and SZ.fits(sug, box, SZ.table_tolerance()):
            out.append(rec("title", "review", f"the title names {', '.join(chk['words'])}: a {sug}, not a "
                           f"{item['type']} (retype if the vision check agrees)", metrics=dict(metrics,
                                                                                               suggested_type=sug)))
        else:
            out.append(rec("title", "remove", f"the title names {', '.join(chk['words']) or '?'}, not a "
                           f"{item['type']}", metrics=metrics))
    elif v == "near":
        out.append(rec("title", "warn", f"the title names a near type ({', '.join(chk['words'])})", metrics=metrics))
    elif v == "silent":
        out.append(rec("title", "review", "the title names no type: the type rests on the vision check (two passes)",
                       metrics=metrics))
    elif v == "generated":
        out.append(rec("title", "review", "generated: our own title, the type rests on the vision check (two passes)",
                       metrics=metrics))
    else:
        out.append(rec("title", "ok", f"the title names a {item['type']}", metrics=metrics))
    for cat, words in chk["flags"].items():
        status = "remove" if cat in HARD_FLAGS else "review"
        out.append(rec("title_flag", status, f"the title says {', '.join(words)}: {FLAG_TEXT.get(cat, cat)}",
                       metrics={"category": cat, "words": words}))
    return out


def sanitary_finish_check(item: dict) -> dict:
    """Fix round after P3 (module docstring): a bathtub, washbasin or toilet whose main material is metal is removed:
    the title names a metal finish with no part word and no non-metal body word, or the largest judged material slot
    (share >= ``METAL_MAIN_SHARE``, the judges not disagreeing) is metal. A metal word next to a part or a body word,
    or a metal main slot the judges disagree on, is a note."""
    if item.get("type") not in SANITARY_TYPES or item.get("kind") == "decor":
        return rec("sanitary_finish", "skip", f"a {item.get('type')} is no sanitary ware")
    words = K.metal_finish(item.get("title"))
    slots = [sl for sl in item.get("material_slots") or [] if isinstance(sl, dict)
             and isinstance(sl.get("share"), (int, float))]
    main = max(slots, key=lambda sl: float(sl["share"])) if slots else None
    metrics = {"metal": words["metal"], "part": words["part"], "body": words["body"],
               "main_slot": ({"material": main.get("material"), "share": main.get("share")} if main else None)}
    metal_main = main is not None and main.get("material") == "metal" and float(main["share"]) >= METAL_MAIN_SHARE
    if metal_main and main.get("agreed") is not False:
        return rec("sanitary_finish", "remove", f"a {item['type']} whose main material is metal (judged slot share "
                   f"{float(main['share']):.0%}): it renders as polished metal, not glazed ceramic", metrics=metrics)
    if words["metal"] and not words["part"] and not words["body"]:
        return rec("sanitary_finish", "remove", f"a {item['type']} with a metal finish (the title says "
                   f"{', '.join(words['metal'])}): it renders as polished metal, not glazed ceramic", metrics=metrics)
    if words["metal"]:
        what = f"a part ({', '.join(words['part'])})" if words["part"] else f"a {', '.join(words['body'])} body"
        return rec("sanitary_finish", "warn", f"the title's metal word ({', '.join(words['metal'])}) names {what}, not "
                   "the main material", metrics=metrics)
    if metal_main:
        return rec("sanitary_finish", "warn", f"the largest material slot ({float(main['share']):.0%}) is judged metal "
                   "but the judges disagree: kept (the final vision check sees it)", metrics=metrics)
    return rec("sanitary_finish", "ok", "no metal main material named or judged", metrics=metrics)


def _same_mesh(item: dict, twin: dict) -> bool:
    """The entry's own faces, vertices and model box equal the ones ``same_mesh_as`` records (box +- 1 mm)."""
    try:
        for key in SAME_MESH_KEYS:
            mine, theirs = item.get(key), twin.get(key)
            if mine is None or theirs is None:
                return False
            if key == "bbox_model_m":
                if len(mine) != 3 or len(theirs) != 3 or any(abs(float(a) - float(b)) > 1e-3
                                                             for a, b in zip(mine, theirs)):
                    return False
            elif int(mine) != int(theirs):
                return False
    except (TypeError, ValueError):
        return False                      # a malformed record is no evidence
    return True


def _render_finding_problem(item: dict, f) -> Optional[str]:
    """Why a ``render_findings`` record cannot remove the model (None: it can)."""
    if not isinstance(f, dict):
        return "not a record"
    if f.get("finding") not in RENDER_FINDINGS:
        return f"unknown finding {f.get('finding')!r} (known: {', '.join(RENDER_FINDINGS)})"
    if not str(f.get("detail") or "").strip():
        return "no detail of what is seen"
    if f.get("sha256_glb") != item.get("sha256_glb"):
        return "seen on another file (the model was republished): the new file needs a new look"
    seen, twin = f.get("seen_in"), f.get("same_mesh_as")
    if isinstance(seen, dict) and seen.get("run") and seen.get("view"):
        return None
    if isinstance(twin, dict) and twin.get("id"):
        return None if _same_mesh(item, twin) else f"the mesh differs from {twin['id']} (faces, vertices or box)"
    return "no evidence (a run view or a model of the same mesh)"


def _render_finding_where(f: dict) -> str:
    seen = f.get("seen_in")
    if isinstance(seen, dict) and seen.get("run") and seen.get("view"):
        return "seen in " + " ".join(str(v) for v in (seen["run"], seen.get("project"), seen["view"]) if v)
    twin = f["same_mesh_as"]
    return (f"the same mesh as {twin['id']} ({int(twin['polycount'])} faces, {int(twin['vertices'])} vertices, box "
            f"{_fmt(twin['bbox_model_m'])} m), whose render shows it")


def render_print_check(item: dict) -> dict:
    """Fix round after P5 (module docstring): a model whose ``render_findings`` record a brand logo or a text print
    seen in a run's render (or on a model of the same mesh) is removed; a record without evidence, of an unknown kind
    or seen on another file is a warning."""
    records = item.get("render_findings")
    if not records:
        return rec("render_print", "skip", "no render finding recorded")
    if not isinstance(records, list):
        records = [records]
    found, problems = [], []
    for f in records:
        why = _render_finding_problem(item, f)
        if why:
            problems.append(why)
        else:
            found.append(f)
    metrics = {"findings": [f["finding"] for f in found], "not_used": problems}
    if not found:
        return rec("render_print", "warn", "render finding(s) not used: " + "; ".join(problems), metrics=metrics)
    reasons = [f"{RENDER_FINDINGS[f['finding']]}: {str(f['detail']).strip()}; {_render_finding_where(f)}; "
               f"{RENDER_FINDING_WHY[f['finding']]}" for f in found]
    return rec("render_print", "remove", " / ".join(reasons), metrics=metrics)


_SIZE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:cm)?\s*[xX×]\s*(\d+(?:[.,]\d+)?)(?:\s*(?:cm)?\s*[xX×]\s*"
                      r"(\d+(?:[.,]\d+)?))?\s*(cm|mm|m\b)", re.I)


def title_size(title: Optional[str]) -> Optional[list[float]]:
    """The size an ABO title gives in cm / mm / m ("195 x 100 x 80cm", "114,3 x 49,53 x 76,454 cm") in metres, in the
    title's order; None when it gives none (inches and feet are not read)."""
    m = _SIZE_RE.search(str(title or ""))
    if not m:
        return None
    unit = {"cm": 0.01, "mm": 0.001, "m": 1.0}[m.group(4).lower()]
    return [round(float(g.replace(",", ".")) * unit, 4) for g in m.groups()[:3] if g]


def title_size_error(dims: list[float], box) -> float:
    """The smallest worst relative error of the title's dimensions against the box sides (any order)."""
    from itertools import permutations
    box = [float(v) for v in box]
    best = math.inf
    for perm in permutations(range(3), len(dims)):
        best = min(best, max(abs(box[p] - v) / v for p, v in zip(perm, dims)))
    return best


def title_size_check(item: dict) -> dict:
    dims = title_size(item.get("title"))
    if not dims or not item.get("bbox_m"):
        return rec("title_size", "skip")
    err = title_size_error(dims, item["bbox_m"])
    metrics = {"title_m": dims, "box_m": item["bbox_m"], "error": round(err, 3)}
    if err > 0.15:
        return rec("title_size", "warn", f"the title says {_fmt(dims)} m, the box is {_fmt(item['bbox_m'])} m "
                   f"({err:.0%} off: the listing of another variant?)", metrics=metrics)
    return rec("title_size", "ok", f"the title's size matches the box within {err:.0%}", metrics=metrics)


def source_check(item: dict) -> dict:
    if item.get("source") == "generated":
        return rec("source", "warn", "generated (TRELLIS.2 or Infinigen): no real product")
    return rec("source", "ok", item.get("source", ""))


def quality_check(item: dict, cfg: dict) -> dict:
    q = item.get("quality")
    if not isinstance(q, list) or not q:
        return rec("quality", "skip")
    floor = int((cfg.get("quality") or {}).get("fallback_min", 3))
    if min(q) <= floor:
        return rec("quality", "remove", f"the M8-M10 judges' quality {q} (<= {floor})", metrics={"quality": q})
    return rec("quality", "ok", f"M8-M10 judges {q}", metrics={"quality": q})


# --------------------------------------------------------------------------
# Size, pivot, up axis, front, units
# --------------------------------------------------------------------------

AXES = ("-Y", "+X", "+Y", "-X")          # clockwise seen from above: -Y -> +X is +90 degrees about Z


def rotate_axis(axis: str, quarter_turns: int) -> str:
    return AXES[(AXES.index(axis) + quarter_turns) % 4]


_GEO_FRONT = re.compile(r"geometry: [^;]*?front ([+-][XY])")
_GEO_BACK = re.compile(r"back_taller: the top \d+ % of the vertices sit toward ([+-][XY])")


def geometric_front(item: dict) -> Optional[str]:
    """The front the M8-M10 geometric rule found (``front_axis_note``: "... : front +X", or the side the top
    vertices sit toward is the back), None when the note says nothing."""
    note = str(item.get("front_axis_note") or "")
    m = _GEO_FRONT.search(note)
    if m:
        return m.group(1)
    m = _GEO_BACK.search(note)
    if m:
        back = m.group(1)
        return ("+" if back[0] == "-" else "-") + back[1]
    return None


def quarter_turns_to_side(item: dict) -> tuple[int, str]:
    """1 or 3 quarter turns of ``front_axis`` to a side: toward the geometric front when it is one of the two
    sides, else 1 (the vision check names the front afterwards)."""
    geo = geometric_front(item)
    front = item.get("front_axis") or "-Y"
    if front in AXES and geo in AXES:
        for turns in (1, 3):
            if rotate_axis(front, turns) == geo:
                return turns, f"to the geometric front {geo}"
    return 1, "side unknown: the vision check confirms"


def size_check(item: dict, cfg: dict, box=None) -> dict:
    """The box (``bbox_m``, or the measured piece-frame size) against the type's real ranges: the uniform scale
    nearest 1 that puts it inside (``sizes.scale_to_fit``). Within ``size.ok``: ok; up to ``size.fix``: fix by
    rescaling; further: fix when the units are unknown (the unit guess was wrong), remove for a known-unit product.
    No scale fits: the front turned 90 degrees may fit (fix ``front_axis``), the model may lie on its side (remove:
    the up axis is no catalogue field), else the proportions are wrong (remove)."""
    ftype = item["type"]
    box = [float(v) for v in (box or item.get("bbox_m") or [])]
    r = SZ.real_range(ftype)
    if r is None or len(box) != 3:
        return rec("size", "skip", f"no real size for {ftype}" if r is None else "no box")
    sc = cfg.get("size") or {}
    ok, fix, slack = float(sc.get("ok", 0.15)), float(sc.get("fix", 0.30)), float(sc.get("slack", 0.03))
    fronted = has_front(ftype) and item.get("front_axis_confidence") != "low"
    metrics = {"box_m": [round(v, 3) for v in box], "width": r["width"], "depth": r["depth"], "height": r["height"],
               "oriented": fronted}
    s = SZ.scale_to_fit(ftype, box, oriented=fronted, slack=slack)
    turned = False
    if s is None and fronted:
        s = SZ.scale_to_fit(ftype, [box[1], box[0], box[2]], oriented=True, slack=slack)
        turned = s is not None
    if s is None and SZ.scale_to_fit(ftype, box, oriented=False, slack=ok) is None:
        # clearly out (even with the size tolerance on every range): another axis up may fit
        for perm in ((0, 2, 1), (2, 1, 0), (1, 2, 0), (2, 0, 1)):
            alt = [box[i] for i in perm]
            if SZ.scale_to_fit(ftype, alt, oriented=False, slack=slack) is not None:
                return rec("size", "remove", f"{_fmt(box)} m fits a {ftype} only with another axis up: the model "
                           "lies on its side", metrics=metrics)
    if s is None:
        return rec("size", "remove", f"proportions {_fmt(box)} m fit no real {ftype} (width {r['width']}, depth "
                   f"{r['depth']}, height {r['height']})", metrics=metrics)
    off = max(s, 1.0 / s) - 1.0
    metrics.update(scale=round(s, 4), off=round(off, 4))
    fixes: dict = {}
    reasons = []
    if turned:
        turns, how = quarter_turns_to_side(item)
        fixes["front_quarter_turns"] = turns
        reasons.append(f"its front is on the wrong side for a {ftype} (width along the front): turned "
                       f"{turns * 90} deg ({how})")
    if off <= ok:
        if turned:
            return rec("size", "fix", "; ".join(reasons), fix=fixes, metrics=metrics)
        return rec("size", "ok", f"{_fmt(box)} m fits a real {ftype}" + (f" ({off:.0%} off)" if off > 0 else ""),
                   metrics=metrics)
    if item.get("units_known") and r["height"][0] * (1 - slack) <= box[2] <= r["height"][1] * (1 + slack) \
            and off <= fix and not turned:
        # pod P3: a real product of known units whose height is right is a small (or large) one of its type, not a
        # unit error: a uniform rescale would make it too tall (a 0.71 m school desk became 1.08 m high); kept
        return rec("size", "warn", f"a real product {off:.0%} off the {ftype} table ({_fmt(box)} m): kept at its "
                   "real size", metrics=metrics)
    if off <= fix or not item.get("units_known"):
        fixes["rescale"] = round(s, 4)
        why = ("the unit guess put it" if not item.get("units_known") else "it is")
        reasons.append(f"{why} {off:.0%} off a real {ftype}: rescaled x{s:.3f}")
        return rec("size", "fix", "; ".join(reasons), fix=fixes, metrics=metrics)
    return rec("size", "remove", f"a product of known units {off:.0%} off a real {ftype} ({_fmt(box)} m): not a "
               f"{ftype}", metrics=metrics)


def expected_origin(bmin, bmax) -> list[float]:
    return [round((bmin[0] + bmax[0]) / 2, 4), round((bmin[1] + bmax[1]) / 2, 4), round(bmin[2], 4)]


def pivot_check(item: dict, cfg: dict, measure: Optional[dict] = None) -> dict:
    """``origin_offset`` must be the bottom centre of the model-frame box (the scene builder puts that point on the
    piece origin); with the render's measurement the box itself is checked (a stale box after a GLB change)."""
    tol = float(cfg.get("pivot_tol_m", 0.01))
    bmin, bmax = item.get("bbox_min_m"), item.get("bbox_max_m")
    if measure and measure.get("model_box_min") and measure.get("model_box_max"):
        mmin, mmax = measure["model_box_min"], measure["model_box_max"]
        if bmin and bmax and max(abs(a - b) for a, b in zip(list(bmin) + list(bmax), list(mmin) + list(mmax))) > tol:
            fixes = {"bbox_min_m": mmin, "bbox_max_m": mmax, "origin_offset": expected_origin(mmin, mmax)}
            return rec("pivot", "fix", f"the measured box {mmin} .. {mmax} differs from the catalogue's", fix=fixes)
        bmin, bmax = mmin, mmax
    if not (bmin and bmax and item.get("origin_offset")):
        return rec("pivot", "skip")
    want = expected_origin(bmin, bmax)
    if max(abs(a - b) for a, b in zip(want, item["origin_offset"])) > tol:
        return rec("pivot", "fix", f"origin_offset {item['origin_offset']} is not the bottom centre {want}",
                   fix={"origin_offset": want})
    return rec("pivot", "ok", "origin_offset at the bottom centre of the box")


def up_check(item: dict) -> dict:
    if item.get("up_axis", "+Z") != "+Z":
        return rec("up", "remove", f"up axis {item.get('up_axis')} (the catalogue needs +Z; a GLB rotation is no "
                   "catalogue fix)")
    return rec("up", "ok", "+Z")


def front_check(item: dict) -> dict:
    if not has_front(item["type"]):
        return rec("front", "skip", f"a {item['type']} has no front")
    conf = item.get("front_axis_confidence")
    if conf == "low":
        return rec("front", "review", f"front {item.get('front_axis')} unknown (confidence low): the vision check "
                   "names it")
    judged = item.get("judged") or {}
    views = {k: (v or {}).get("front_view") for k, v in judged.items() if isinstance(v, dict)}
    if len({v for v in views.values() if v is not None}) > 1:
        return rec("front", "warn", f"the M8-M10 judges named different fronts {views}")
    return rec("front", "ok", f"front {item.get('front_axis')} ({conf})")


def units_check(item: dict) -> dict:
    if item.get("units_known"):
        return rec("units", "ok", "units known (metres)")
    note = str(item.get("unit_note") or "")
    if "normalised" in note:
        return rec("units", "warn", "units unknown: scaled to a typical footprint of the type (normalised)")
    return rec("units", "warn", f"units guessed (x{item.get('unit_scale')})")


# --------------------------------------------------------------------------
# Mesh and textures
# --------------------------------------------------------------------------

def mesh_check(item: dict, cfg: dict, measure: Optional[dict] = None) -> list[dict]:
    mc = cfg.get("mesh") or {}
    out = []
    faces = (measure or {}).get("faces", item.get("polycount"))
    crude = int(mc.get("crude_faces", 3000))
    if item["kind"] == "furniture" and isinstance(faces, int) and faces < crude:
        out.append(rec("crude", "review", f"{faces} triangles (< {crude}): crude unless the vision quality is high",
                       metrics={"faces": faces}))
    if not measure:
        return out or [rec("mesh", "skip", "not measured (no render yet)")]
    if not measure.get("ok"):
        return out + [rec("mesh", "remove", f"broken: {measure.get('error') or 'no geometry'}")]
    m = measure
    if m.get("flipped_share", 0) > float(mc.get("broken_flipped_share", 0.3)):
        out.append(rec("mesh", "remove", f"broken: {m['flipped_share']:.0%} of the edges join flipped faces",
                       metrics={"flipped_share": m["flipped_share"]}))
    if m.get("zero_area_share", 0) > float(mc.get("broken_zero_area_share", 0.2)):
        out.append(rec("mesh", "remove", f"broken: {m['zero_area_share']:.0%} of the faces have no area",
                       metrics={"zero_area_share": m["zero_area_share"]}))
    if m.get("nonmanifold_share", 0) > 0.05:
        out.append(rec("mesh", "warn", f"{m['nonmanifold_share']:.0%} non-manifold edges"))
    if m.get("boundary_share", 0) > float(mc.get("warn_boundary_share", 0.25)):
        out.append(rec("mesh", "warn", f"{m['boundary_share']:.0%} open edges"))
    parts = m.get("outside_parts") or []
    if parts:
        sides = sorted({s for p in parts for s in p.get("sides", [])})
        status = "review" if m.get("front_outside") and item["kind"] == "furniture" else "warn"
        out.append(rec("outside_parts", status, f"{len(parts)} part(s) stick out of the main body ({', '.join(sides)}"
                       f", up to {max(p['sticks_out_m'] for p in parts):.2f} m): an open drawer or a separate prop?",
                       metrics={"parts": parts}))
    if not out:
        out.append(rec("mesh", "ok", f"{m.get('faces')} faces, {m.get('parts')} part(s)"))
    return out


def texture_check(item: dict, cfg: dict, measure: Optional[dict] = None) -> dict:
    if not measure:
        if item.get("textured") is False and not item.get("vertex_colours"):
            return rec("textures", "warn", "untextured (material colours only)")
        return rec("textures", "skip", "not measured (no render yet)")
    tx = measure.get("textures") or {}
    if tx.get("missing"):
        return rec("textures", "remove", f"missing texture files: {', '.join(tx['missing'][:3])}")
    if not tx.get("images") and not measure.get("colour_attributes"):
        return rec("textures", "warn", "untextured (material colours only)")
    low = int((cfg.get("textures") or {}).get("min_px", 512))
    if tx.get("max_px") and tx["max_px"] < low:
        return rec("textures", "warn", f"largest texture {tx['max_px']} px (< {low})")
    return rec("textures", "ok", f"{tx.get('images', 0)} image(s), up to {tx.get('max_px')} px")


# --------------------------------------------------------------------------
# Milestone 13 gates
# --------------------------------------------------------------------------

def gates_of(cfg: dict) -> dict:
    return dict(cfg.get("gates") or {})


def units_anchor_check(item: dict, cfg: dict) -> dict:
    """An anchor type (``gates.known_units_anchor_types``) must carry known units (metres from the source): a bed,
    sofa, table, wardrobe or fixture of guessed or normalised units is removed (the fit would scale a guess)."""
    types = gates_of(cfg).get("known_units_anchor_types") or ()
    if item["type"] not in types or item.get("kind") == "decor":
        return rec("units_anchor", "skip", f"a {item['type']} is no anchor of the gate")
    if item.get("units_known"):
        return rec("units_anchor", "ok", "an anchor of known units")
    note = str(item.get("unit_note") or "")
    how = "normalised to a typical footprint" if "normalised" in note else f"guessed (x{item.get('unit_scale')})"
    return rec("units_anchor", "remove", f"an anchor ({item['type']}) of units {how}: the Milestone 13 gate needs known "
               "units for anchors", metrics={"unit_scale": item.get("unit_scale")})


def pbr_record(item: dict, measure: Optional[dict] = None) -> Optional[dict]:
    """The PBR map record of a model: the catalogue's ``pbr_maps``, else the render's ``measure["pbr"]``."""
    rec_ = item.get("pbr_maps")
    if isinstance(rec_, dict) and rec_:
        return rec_
    m = (measure or {}).get("pbr")
    return m if isinstance(m, dict) and m else None


def pbr_check(item: dict, cfg: dict, measure: Optional[dict] = None) -> list[dict]:
    """``pbr``: the maps present (``pbr_maps_required`` missing: warn, flat colours; ``pbr_maps_wanted`` missing: a
    note); ``pbr_record``: a ``fix`` that writes the record into the entry when it has none yet."""
    maps = pbr_record(item, measure)
    if not maps:
        return [rec("pbr", "skip", "PBR maps not recorded (no measurement of the file yet)")]
    g = gates_of(cfg)
    required = [m for m in (g.get("pbr_maps_required") or ["base_colour"]) if not maps.get(m)]
    wanted = [m for m in (g.get("pbr_maps_wanted") or []) if not maps.get(m)]
    present = [m for m in ("base_colour", "metallic_roughness", "normal", "occlusion", "emissive") if maps.get(m)]
    metrics = {"maps": present, "missing_required": required, "missing_wanted": wanted,
               "materials": maps.get("materials"), "images": maps.get("images")}
    out = []
    if required:
        out.append(rec("pbr", "warn", f"no {', '.join(required)} map: flat material colours only "
                       f"({maps.get('materials')} material(s), {maps.get('images')} image(s))", metrics=metrics))
    elif wanted:
        out.append(rec("pbr", "ok", f"maps {', '.join(present)}; no {', '.join(wanted)} map (ranked lower by the fit)",
                       metrics=metrics))
    else:
        out.append(rec("pbr", "ok", f"maps {', '.join(present)}", metrics=metrics))
    if not (isinstance(item.get("pbr_maps"), dict) and item["pbr_maps"]):
        out.append(rec("pbr_record", "fix", "the PBR map record is written into the catalogue entry (M13 gate)",
                       fix={"pbr_maps": {k: maps.get(k) for k in ("base_colour", "metallic_roughness", "normal",
                                                                  "occlusion", "emissive", "materials", "images")}}))
    return out


def material_tags_check(item: dict, cfg: dict) -> dict:
    """Every entry needs judged material tags (the Milestone 10 slot judgement, or the Milestone 13 vision answer's
    ``materials``): ``review`` until the answer names them (never a removal)."""
    if not gates_of(cfg).get("material_tags_required", False):
        return rec("material_tags", "skip", "gate off")
    tags = item.get("material_tags")
    if isinstance(tags, list) and tags:
        return rec("material_tags", "ok", f"material tags {', '.join(str(t) for t in tags)}")
    return rec("material_tags", "review", "no material tags: the vision answer's materials name them (M13 gate)")


def chaise_check(item: dict, cfg: dict, measure: Optional[dict] = None) -> dict:
    """An L-sofa (``gates.chaise_side_types``) needs its chaise side (left / right) for the fit to match a drawn L:
    a ``fix`` when the measurement found it, else a warning."""
    if item["type"] not in (gates_of(cfg).get("chaise_side_types") or ()):
        return rec("chaise", "skip", f"a {item['type']} has no chaise")
    side = item.get("chaise_side")
    if side in ("left", "right"):
        return rec("chaise", "ok", f"chaise on the {side}")
    measured = (measure or {}).get("chaise_side")
    if measured in ("left", "right"):
        return rec("chaise", "fix", f"chaise side {measured} from the measured footprint", fix={"chaise_side": measured})
    return rec("chaise", "warn", "chaise side unknown: the fit cannot match a drawn L's side (M13 gate); the footprint "
               "measurement of the catalogue step names it for new models")


def licence_fields_check(item: dict, cfg: dict) -> dict:
    """The Milestone 13 licence fields of every entry (``gates.licence_fields``): a warning when one is missing (the
    fields are written by ``python -m wenart.furniture licence-fields`` and by the growth entries)."""
    fields = gates_of(cfg).get("licence_fields") or ()
    if not fields:
        return rec("licence_fields", "skip", "gate off")
    missing = [k for k in fields if k not in item or item.get(k) in (None, "")]
    if missing:
        return rec("licence_fields", "warn", f"licence fields missing: {', '.join(missing)} (M13 gate: written by "
                   "python -m wenart.furniture licence-fields)", metrics={"missing": missing})
    return rec("licence_fields", "ok", f"licence {item.get('licence')} flag {item.get('licence_flag')}, "
               f"commercial-safe {item.get('commercial_safe')}")


# --------------------------------------------------------------------------
# Duplicates
# --------------------------------------------------------------------------

def texture_key(item: dict, measure: Optional[dict] = None) -> Optional[str]:
    """What the model looks like: the measured texture hash, else the material colours of recolour.py (an ABO colour
    variant has the same mesh and other colours), else None (unknown)."""
    if measure and (measure.get("textures") or {}).get("hash"):
        return "tex:" + measure["textures"]["hash"]
    slots = item.get("material_slots")
    if slots:
        return "rgb:" + ";".join(str(s.get("colour_rgb")) for s in slots)
    return None


def rank_key(item: dict) -> tuple:
    q = item.get("quality") or []
    mean = sum(q) / len(q) if q else 0.0
    return (SOURCE_RANK.get(item.get("source"), 9), -mean, str(item["id"]))


def duplicates(items: list[dict], cfg: dict, measures: Optional[dict] = None) -> dict:
    """``{id: record}`` for every lower-ranked copy: the same GLB (sha256), or the same type, every box side within
    ``duplicates.box_m``, the face count within ``duplicates.faces_share`` and the same texture key."""
    dc = cfg.get("duplicates") or {}
    box_tol, face_tol = float(dc.get("box_m", 0.01)), float(dc.get("faces_share", 0.01))
    measures = measures or {}
    out: dict = {}
    ordered = sorted(items, key=rank_key)
    seen_sha: dict = {}
    for it in ordered:
        sha = it.get("sha256_glb")
        if sha and sha in seen_sha:
            out[it["id"]] = rec("duplicate", "remove", f"the same GLB as {seen_sha[sha]}",
                                metrics={"of": seen_sha[sha]})
        elif sha:
            seen_sha[sha] = it["id"]
    by_type: dict = {}
    for it in ordered:
        by_type.setdefault((it["kind"], it["type"]), []).append(it)
    for group in by_type.values():
        kept: list = []
        for it in group:
            if it["id"] in out:
                continue
            m = measures.get(it["id"])
            box = (m or {}).get("size") or it.get("bbox_m")
            faces = (m or {}).get("faces", it.get("polycount"))
            key = texture_key(it, m)
            twin = None
            for k in kept:
                km = measures.get(k["id"])
                kbox = (km or {}).get("size") or k.get("bbox_m")
                kfaces = (km or {}).get("faces", k.get("polycount"))
                if not (box and kbox and faces and kfaces):
                    continue
                if max(abs(float(a) - float(b)) for a, b in zip(box, kbox)) > box_tol:
                    continue
                if abs(faces - kfaces) > face_tol * max(faces, kfaces):
                    continue
                kkey = texture_key(k, km)
                if key is None or kkey is None or key != kkey:
                    continue
                twin = k
                break
            if twin is not None:
                out[it["id"]] = rec("duplicate", "remove", f"a copy of {twin['id']} (box +-{box_tol * 100:.0f} cm, "
                                    f"faces +-{face_tol:.0%}, same texture)", metrics={"of": twin["id"]})
            else:
                kept.append(it)
    return out


# --------------------------------------------------------------------------
# All checks
# --------------------------------------------------------------------------

def item_checks(item: dict, cfg: dict, known_types, measure: Optional[dict] = None) -> list[dict]:
    box = (measure or {}).get("size") if measure and measure.get("ok") else None
    out = [licence_check(item)]
    out += title_check(item, known_types)
    out.append(title_size_check(item))
    out.append(source_check(item))
    out.append(quality_check(item, cfg))
    out.append(size_check(item, cfg, box))
    out.append(pivot_check(item, cfg, measure))
    out.append(up_check(item))
    out.append(front_check(item))
    out.append(units_check(item))
    out += mesh_check(item, cfg, measure)
    out.append(texture_check(item, cfg, measure))
    # Milestone 13 gates
    out.append(units_anchor_check(item, cfg))
    out += pbr_check(item, cfg, measure)
    out.append(material_tags_check(item, cfg))
    out.append(chaise_check(item, cfg, measure))
    out.append(licence_fields_check(item, cfg))
    # fix round after P3
    out.append(sanitary_finish_check(item))
    # fix round after P5: a brand logo or a text print a run's render showed (entry render_findings)
    out.append(render_print_check(item))
    return out


def run_checks(items: list[dict], cfg: dict, measures: Optional[dict] = None) -> dict:
    """``{id: [record]}`` for every item, the duplicate records included."""
    measures = measures or {}
    known = set(SZ.types()) | set(SZ.decor_types())
    out = {it["id"]: item_checks(it, cfg, known, measures.get(it["id"])) for it in items}
    for iid, r in duplicates(items, cfg, measures).items():
        out[iid].append(r)
    return out
