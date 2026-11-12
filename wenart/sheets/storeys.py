"""The storeys a drawing does not draw (6 Nov 2026; user on real21's structure run: "real21 only 1 floor seems to be
built you need to extrapolate what needs to be done. all floors needs to be done").

What: ``infer(plans, regions, docs, values, warnings, conflict, section_storeys)`` runs after the plans got their levels
(``levels.assign_levels``) and before the variants (``variants.group``). When the documents draw fewer storeys than the
building has, it counts the storeys from the evidence and lets the top drawn plan stand for the storeys it does not
draw, through the typical-floor mechanism of real10 (``level["typical"]``: ``variants.group`` makes the copies,
``classify.typical_copies`` reads the region again for each, the pipeline marks them ``typical_of``). It returns the
record written to ``sheets.json`` (``storeys``) and, by the pipeline, to ``building.json``
(``level_inference.storeys``): the count, the rule that gave it, its confidence, every rung of the evidence ladder with
what it found, the inferred levels with their reasons, the ground floor's footprint evidence and the open point the
architect may change.

The evidence ladder (the first rung with a count wins; every rung is recorded, a disagreement is a warning):

1. ``user``: the brief's ``storeys`` (the user's number, it always wins);
2. ``section``: the storeys the sections and elevations name (``levels.storey_words``); their slab bands are listed,
   never counted (sills, parapets and landings read as bands: real15's two-storey section has nine);
3. ``title``: a text listing the floors (``1.-4. NORMAL KAT``, ``Z+4``, ``B+Z+4``, ``G+4``, ``5 KATLI``);
4. ``area_table``: a total area and a typical floor area (``TOPLAM``, ``NORMAL``, ``OTURUM``);
5. ``zoning``: ``KAT ADEDİ``, a height limit (``H=``, ``Hmax``, ``Yençok``) over the storey height, ``EMSAL`` times the
   parcel area over the typical floor area;
6. ``type_default``: what the plan shows (``TYPE_DEFAULTS``): lifts and several flats or a matching typical floor area
   make a multi-storey apartment block; several flats around a common stair a low block; a single house with a stair
   inside its upper floor. The count is then a guess (``guess: true``) and says so, so the user can give the real one.

The area table also says which floor the drawn plan is: an untitled plan whose gross area is the typical floor area
(``NORMAL``) rather than the footprint (``OTURUM``) is the typical floor; the ground floor is then inferred from it
(``ground_from_typical``) and, when the footprint is smaller than the typical floor, without the cantilevered balconies
(``cantilevers``, carried out by ``wenart.ingest.completion``). A level the drawing or the brief names is never changed:
a disagreement is a conflict and a warning.

Why: real21 draws one typical floor of a long apartment block (two lifts, a stair, six flats, ``normal 436`` beside
``oturum 390`` on its site plan); no section, no elevation, no storey count anywhere. The reading built one floor and
the renders showed a one-storey block.

How: pure text and geometry rules on the sheets' regions (no AI). Only storeys at and above the ground floor are
inferred (an undrawn basement is not); a building whose top is drawn (an attic or a roof terrace plan) gets none. The
count is an open point of the architect (``open_point``: the default and the counts it may choose; the brief's
``storeys`` or the project's ``architect_answers.json`` key ``OPEN_POINT_KEY`` settle it on the next reading).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Optional

from wenart import building as B

OPEN_POINT_KEY = "N1:storeys"         # the architect's open point (wenart/blender/architect.py, rule N1)
STOREY_M = 3.0                        # the storey height a height limit is divided by (the reading's default pitch)
HEIGHT_MIN_M = 5.5                    # a height limit under this is no building height (a ceiling, a window)
COUNT_MAX = 60
# The type defaults (rung 6). They are guesses, stated openly in the record and the reading check: the documents
# give no count. An apartment block with a lift: the ground floor and four typical floors (5); a block without a lift:
# 3; a single house with a stair inside: 2 (its upper floor).
TYPE_DEFAULTS = {"apartment_block_lift": 5, "apartment_block": 3, "house_stair": 2}
TYPE_NAMES = {"apartment_block_lift": "an apartment block with a lift", "apartment_block": "an apartment block without "
              "a lift", "house_stair": "a house with a stair inside"}
STAIR_LINES_MIN = 11                  # stair-layer entities of a stair that climbs a storey (its tread lines)
CONFIDENCE = {"user": 1.0, "architect": 0.9, "section": 0.9, "section_bands": 0.6, "title": 0.85, "area_table": 0.7,
              "zoning_count": 0.8, "zoning_height": 0.5, "zoning_far": 0.4, "type_default": 0.25}
AREA_MATCH = 0.12                     # a plan's gross area within this share of an area text is that floor
AREA_ONE_MATCH = 0.08                 # ... when the table gives only one of the two areas
CANTILEVER_SHARE = 0.03               # a footprint this much smaller than the typical floor: cantilevered parts
ROW_REACH_H = 14.0                    # an area number this many text heights right of its word is its value
ROW_TOL_H = 0.7                       # ... and this many heights up or down
SIDE_REACH_M = 6.0                    # a side text this far outside the plan's box names that side

# ----------------------------------------------------------------------------------------------- the text patterns
_NUM = r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)"
AREA_WORDS = {
    "ground": re.compile(r"\bOTURUM(?:\s+ALANI)?\b|\bTABAN\s+ALANI\b|\bTAKS\s+ALANI\b|\bFOOTPRINT\b"
                         r"|\bGROUND\s+COVERAGE\b|\bGRUNDFLACHE\b|\bEMPRISE\b"),
    "typical": re.compile(r"\bNORMAL(?:\s+KAT)?(?:\s+ALANI)?\b|\bTIP\s+KAT(?:\s+ALANI)?\b|\bTYPICAL(?:\s+FLOOR)?\b"
                          r"|\bREGELGESCHOSS\b|\bETAGE\s+COURANT\b"),
    "total": re.compile(r"\bTOPLAM(?:\s+INSAAT)?(?:\s+ALANI?)?\b|\bINSAAT\s+ALANI\b|\bTOTAL(?:\s+FLOOR)?(?:\s+AREA)?\b"
                        r"|\bGROSS\s+FLOOR\s+AREA\b|\bGFA\b|\bBGF\b"),
    "parcel": re.compile(r"\bPARSEL\s+ALANI\b|\bARSA\s+ALANI\b|\bPLOT\s+AREA\b|\bSITE\s+AREA\b"
                         r"|\bGRUNDSTUCKSFLACHE\b"),
}
_SCALE_RE = re.compile(r"\b1\s*[/:]\s*\d{2,4}\b")
_AREA_NUM_RE = re.compile(r"(?<![\d.,/])" + _NUM + r"\s*(?:M2|M²|M\^2|SQM)?(?![\d/])")
ZONING_COUNT = re.compile(r"\bKAT\s+(?:ADEDI|SAYISI)\s*[:=]?\s*(\d{1,2})\b|\b(\d{1,2})\s+KATLI\b"
                          r"|\bNUMBER\s+OF\s+(?:STOREYS|STORIES|FLOORS)\s*[:=]?\s*(\d{1,2})\b"
                          r"|\bSTOREYS\s*[:=]\s*(\d{1,2})\b|\bGESCHOSSE\s*[:=]?\s*(\d{1,2})\b")
ZONING_HEIGHT = re.compile(r"\b(?:HMAX|H\s+MAX|YENCOK|YEN\s+COK|BINA\s+YUKSEKLIGI|SACAK\s+KOTU|H)\s*[:=]\s*"
                           r"(\d{1,2}[.,]\d{1,2})\s*(?:M)?\b")
ZONING_FAR = re.compile(r"\b(?:EMSAL|KAKS|FAR|E)\s*[:=]\s*(\d[.,]\d{1,2})\b")
TITLE_ZPLUS = re.compile(r"(?<![A-Z0-9])(?:B\d?\s*\+\s*)?(?:Z|ZK|ZEMIN)\s*\+\s*(\d{1,2})(?![.,\-/]\s*\d)"
                         r"(?:\s*(?:N|NK|NORMAL)\b)?|(?<![A-Z0-9])G\s*\+\s*(\d{1,2})\b")
# a floor list before KAT, KATLAR or KATLARI ('ZEMİN+1.2.3.4.5. NORMAL KATLAR': floors 1 to 5 above the ground)
FLOOR_LIST = re.compile(r"(?<![\d.,])(\d{1,2}(?:\s*[.,\-/]+\s*\d{1,2})+)\s*\.?\s*(?:NORMAL\s+|TIP\s+)?KAT(?:LAR|LARI)?\b")
LIFT_RE = re.compile(r"\bASANSOR\b|\bLIFTS?\b|\bELEVATORS?\b|\bAUFZUG\b|\bASCENSEUR\b|\bASCENSOR\b")
FLAT_RE = re.compile(r"\bDAIRE\b|\bAPARTMENT\b|\bFLAT\s*\d|\bWOHNUNG\b|\bAPPARTEMENT\b")
KITCHEN_RE = re.compile(r"\bMUTFAK\b|\bKITCHEN\b|\bKUCHE\b|\bCUISINE\b|\bCOCINA\b|\bKITCHENETTE\b")
STAIR_RE = re.compile(r"\bMERDIVEN\b|\bSTAIRS?\b|\bSTAIRCASE\b|\bTREPPE\b|\bESCALIER\b|\bESCALERA\b")
# The side texts (``side_texts``): a party wall on that side, or the street
# (a neighbouring plot, 'komşu parsel', is no attached building: only the building or its wall is)
PARTY_RE = re.compile(r"\bBITISIK\b|\bKOMSU\b(?!\s+(?:PARSEL|ARSA|ADA|PLOT))|\bATTACHED\b|\bPARTY\s+WALL\b"
                      r"|\bADJOINING\s+BUILDING\b|\bMITOYEN(?:NE)?\b|\bBRANDWAND\b|\bGRENZBEBAUUNG\b"
                      r"|\bNACHBARGEBAUDE\b")
STREET_RE = re.compile(r"\bSOKA[GK]I?\b|\bSOK\b|\bCADDESI\b|\bCADDE\b|\bCAD\b|\bBULVARI?\b|\bYOLU\b|\bSTREET\b"
                       r"|\bROAD\b|\bAVENUE\b|\bSTRASSE\b|\bRUE\b|\bCALLE\b|\bAVENIDA\b")


def _fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).upper().split())


def _num(s: str) -> Optional[float]:
    """``'1.250,50'`` -> 1250.5, ``'436'`` -> 436.0, ``'15,50'`` -> 15.5 (pure)."""
    s = s.strip()
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?", s) and len(re.split(r"[.,]", s)[-1]) == 3:
        s = re.sub(r"[.,]", "", s)
    elif re.fullmatch(r"\d{1,3}(?:[.]\d{3})+,\d{1,2}", s):
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+\.\d{1,2}", s):
        s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _ev(t, file: Optional[str], rule: str, **extra) -> dict:
    ev = dict(getattr(t, "evidence", None) or {})
    out = {"file": ev.get("file") or file, "entity": ev.get("entity") or getattr(t, "id", None),
           "layer": ev.get("layer") or getattr(t, "layer", None), "text": getattr(t, "text", None), "rule": rule}
    out.update(extra)
    return out


# ------------------------------------------------------------------------------------------------ the texts used
def evidence_texts(regions: list, docs: list) -> list:
    """``[(Txt, file)]``: every text of the project's sheets, except the texts inside a plan the brief leaves out (a
    second building on the same sheet: real20 and real21) (pure)."""
    from wenart.sheets.model import in_box

    other = [r for r in regions if r.use == "ignored" and "plan_levels" in str(getattr(r, "ignored_reason", "") or "")]
    out = []
    for doc in docs:
        for sheet in getattr(doc, "sheets", None) or []:
            for t in getattr(sheet, "texts", None) or []:
                if any(r.file == doc.file and r.sheet is sheet and in_box(t.point, r.box) for r in other):
                    continue
                out.append((t, doc.file))
    return out


def area_items(texts: list) -> list:
    """``[{kind, value, text, evidence}]``: the area table's rows (``AREA_WORDS``): a word with a number after it in the
    same text, or a number-only text on the same row right of it (pure). Scales (``1/100``) are no area."""
    out = []
    numbers = []
    for t, f in texts:
        folded = _fold(t.text)
        m = re.fullmatch(_NUM + r"\s*(?:M2|M²)?", folded)
        if m:
            numbers.append((t, f, _num(m.group(1))))
    for t, f in texts:
        folded = _fold(t.text)
        for kind, rx in AREA_WORDS.items():
            m = rx.search(folded)
            if not m:
                continue
            rest = _SCALE_RE.sub(" ", folded[m.end():])
            vals = [_num(x) for x in _AREA_NUM_RE.findall(rest)]
            vals = [v for v in vals if v is not None and 20.0 <= v <= 200000.0]
            src = None
            if vals:
                value = vals[-1] if kind != "parcel" else vals[0]
            else:
                h = max(float(getattr(t, "height", 0.0) or 0.0), 1e-9)
                row = [(n, nf, v) for n, nf, v in numbers if nf == f and v is not None and 20.0 <= v <= 200000.0
                       and t.box[2] - h <= n.box[0] <= t.box[2] + ROW_REACH_H * h
                       and abs(n.point[1] - t.point[1]) <= ROW_TOL_H * h]
                if not row:
                    continue
                n, nf, value = min(row, key=lambda x: x[0].box[0])
                src = n
            out.append({"kind": kind, "value": round(float(value), 2), "text": t.text.strip(),
                        "point": t.point, "file": f,
                        "evidence": [_ev(t, f, "area_table")] + ([_ev(src, f, "area_table")] if src is not None
                                                                 else [])})
            break
    return out


def _first(items: list, kind: str, near=None) -> Optional[dict]:
    """The item of ``kind`` nearest the plan (``near``: ``(file, box)``; a sheet holding two buildings has two area
    tables), else the first one."""
    cands = [i for i in items if i["kind"] == kind]
    if not cands or near is None:
        return cands[0] if cands else None
    from wenart.sheets.model import point_box_distance

    file, box = near
    return min(cands, key=lambda i: (i.get("file") != file, point_box_distance(i.get("point") or (0.0, 0.0), box)))


def title_counts(texts: list) -> list:
    """``[{count, text, evidence}]`` (pure): a text listing the floors (``1.-4. NORMAL KAT`` -> 5 with the ground floor,
    ``Z+4`` -> 5, ``B+Z+4`` -> 5 above the ground, ``G+4`` -> 5, ``5 KATLI`` -> 5)."""
    from wenart.sheets import levels as LV

    out = []
    for t, f in texts:
        folded = _fold(t.text)
        listed = LV._listed_floors(folded)
        if listed is None:
            m = FLOOR_LIST.search(folded)
            listed = LV._listed_floors(f"{m.group(1)} KAT") if m else None
        if listed is not None:
            orders, _word = listed
            out.append({"count": max(orders) + 1, "text": t.text.strip(), "how": f"floors {orders} listed",
                        "evidence": [_ev(t, f, "title_floor_list")]})
            continue
        m = TITLE_ZPLUS.search(folded)
        if m:
            n = int(m.group(1) or m.group(2))
            if 1 <= n < COUNT_MAX:
                out.append({"count": n + 1, "text": t.text.strip(), "how": "ground floor + {n}".format(n=n),
                            "evidence": [_ev(t, f, "title_ground_plus")]})
    return out


def zoning_items(texts: list) -> dict:
    """``{"count": [...], "height": [...], "far": [...]}`` (pure): the zoning texts (``KAT ADEDİ 5``, ``Hmax=15.50``,
    ``EMSAL=2.00``)."""
    out = {"count": [], "height": [], "far": []}
    for t, f in texts:
        folded = _fold(t.text)
        m = ZONING_COUNT.search(folded)
        if m:
            n = int(next(g for g in m.groups() if g))
            if 1 <= n <= COUNT_MAX:
                out["count"].append({"value": n, "text": t.text.strip(), "evidence": [_ev(t, f, "zoning_count")]})
        m = ZONING_HEIGHT.search(folded)
        if m:
            v = _num(m.group(1))
            if v is not None and HEIGHT_MIN_M <= v <= 200.0:
                out["height"].append({"value": v, "text": t.text.strip(), "evidence": [_ev(t, f, "zoning_height")]})
        m = ZONING_FAR.search(folded)
        if m:
            v = _num(m.group(1))
            if v is not None and 0.1 <= v <= 12.0:
                out["far"].append({"value": v, "text": t.text.strip(), "evidence": [_ev(t, f, "zoning_far")]})
    return out


# ------------------------------------------------------------------------------------------------- the plan facts
def gross_area(r) -> Optional[float]:
    """The plan's gross area in m2: its outline (``register.outline``, the enclosing roof outlines and the section cut
    line left out) (None without a unit or an outline)."""
    if hasattr(r, "_gross_m2"):
        return r._gross_m2
    mpu = getattr(r, "metres_per_unit", None)
    if not mpu or not getattr(r, "ents", None):
        return None
    if not hasattr(r, "_gross_m2"):
        from wenart.sheets import register as RG
        try:
            poly = RG.outline(r, mpu, set(RG.enclosing_outlines(r, mpu)) | RG.cut_line_entities(r))
        except Exception:  # noqa: BLE001 - a plan without an outline has no gross area
            poly = None
        r._gross_m2 = round(poly.area * mpu * mpu, 1) if poly is not None and not poly.is_empty else None
    return r._gross_m2


def plan_signals(r) -> dict:
    """What a plan shows about its building (pure on the region's texts and features): lifts, flats (flat entrances or
    kitchens), stairs (stair blocks or layers, stair words)."""
    lifts = flats = kitchens = stair_words = 0
    for t in getattr(r, "texts", None) or []:
        folded = _fold(t.text)
        lifts += 1 if LIFT_RE.search(folded) else 0
        flats += 1 if FLAT_RE.search(folded) else 0
        kitchens += 1 if KITCHEN_RE.search(folded) else 0
        stair_words += 1 if STAIR_RE.search(folded) else 0
    stairs = int((getattr(r, "features", None) or {}).get("stairs") or 0)
    return {"lifts": lifts, "flat_words": flats, "kitchens": kitchens, "stairs": stairs, "stair_words": stair_words}


def building_type(signals: dict, typical_area_matches: bool) -> Optional[str]:
    """The type default's key (``TYPE_DEFAULTS``) of what a plan shows, or None (pure): lifts with several flats (two
    flat words or two kitchens) or a typical floor area matching the plan: an apartment block with a lift; several flats
    with a stair: a low apartment block; one flat at most, no lift and a stair: a house with an upper floor."""
    several = signals["flat_words"] >= 2 or signals["kitchens"] >= 2
    # a stair that climbs a storey: a label naming it, or a storey's tread lines on a stair layer (a few entrance or
    # terrace steps are no upper floor)
    stair = signals["stairs"] >= STAIR_LINES_MIN or signals["stair_words"] > 0
    if signals["lifts"] >= 1 and (several or typical_area_matches):
        return "apartment_block_lift"
    if several and stair:
        return "apartment_block"
    if signals["lifts"] == 0 and signals["kitchens"] <= 1 and signals["flat_words"] <= 1 and stair:
        return "house_stair"
    return None


def floor_role(gross: Optional[float], ground: Optional[float], typical: Optional[float]) -> Optional[dict]:
    """``{"role": "typical" | "ground", "share", "reason"}`` (pure): which floor a plan of gross area ``gross`` is by
    the area table (the nearer of the two areas, within ``AREA_MATCH``; ``AREA_ONE_MATCH`` with one area only), or
    None."""
    if not gross:
        return None
    cands = []
    for role, a in (("typical", typical), ("ground", ground)):
        if a:
            cands.append((abs(gross - a) / a, role, a))
    if not cands:
        return None
    share, role, a = min(cands)
    if share > (AREA_MATCH if len(cands) == 2 else AREA_ONE_MATCH):
        return None
    word = "typical floor" if role == "typical" else "footprint"
    return {"role": role, "share": round(share, 3), "area": a,
            "reason": f"its gross area {gross:.0f} m2 is the area table's {word} {a:.0f} m2 ({share * 100:.1f} % off)"
                      + (f", not the {'footprint' if role == 'typical' else 'typical floor'} "
                         f"{(ground if role == 'typical' else typical):.0f} m2" if len(cands) == 2 else "")}


# --------------------------------------------------------------------------------------------------- the ladder
def ladder(values: dict, section_storeys: dict, sections: list, texts: list, gross: Optional[float],
           signals: dict, drawn_count: int, answers: Optional[dict] = None,
           drawn_all: Optional[int] = None, near=None) -> tuple[list, dict]:
    """``(rungs, areas)`` (pure): every rung of the evidence ladder with what it found, ``{"rung", "count" | None,
    "confidence", "evidence", "note"}``, in trust order (``drawn_count``: the drawn storeys at and above the ground,
    ``drawn_all`` with the basements); ``areas`` the area table's ground, typical, total and parcel
    items."""
    rungs = []
    drawn_all = drawn_count if drawn_all is None else drawn_all
    user = values.get("storeys")
    rungs.append({"rung": "user", "count": int(user) if isinstance(user, int) and not isinstance(user, bool) and
                  1 <= user <= COUNT_MAX else None, "confidence": CONFIDENCE["user"], "evidence": [],
                  "note": "the brief's storeys" if user else "the brief gives no storey count"})
    ans = (answers or {}).get(OPEN_POINT_KEY) or {}
    n = (ans.get("params") or {}).get("count") if isinstance(ans, dict) else None
    rungs.append({"rung": "architect", "count": int(n) if isinstance(n, int) and 1 <= n <= COUNT_MAX else None,
                  "confidence": CONFIDENCE["architect"], "evidence": [],
                  "note": (f"the answer to {OPEN_POINT_KEY} ({ans.get('by', 'user')}): {ans.get('reason') or ''}"
                           if n else f"no answer to {OPEN_POINT_KEY}")})
    above = sorted(o for o in (section_storeys or {}) if o >= 0)
    if above:
        rungs.append({"rung": "section", "count": max(above) + 1, "confidence": CONFIDENCE["section"],
                      "evidence": [{"rule": "storey_words", "text": section_storeys[o]} for o in above],
                      "note": f"the sections name {len(above)} storeys at and above the ground floor"})
    else:
        # The slab bands are listed, never counted: a section's sills, parapets and landings read as bands too (a
        # two-storey house's section with 9 bands), so only the storeys a section names count
        bands = [(len(geom.bands), s.id) for s in sections for geom in [getattr(s, "_section", None)]
                 if geom is not None and getattr(geom, "bands", None) and s.cls == "section"]
        best = max(bands, default=None)
        rungs.append({"rung": "section", "count": None, "confidence": CONFIDENCE["section_bands"],
                      "evidence": [{"rule": "slab_bands", "region_id": best[1], "text": f"{best[0]} slab bands"}]
                      if best else [],
                      "note": (f"section {best[1]} names no storey; its {best[0]} slab bands are no storey count "
                               f"({drawn_all} level(s) drawn)" if best else
                               "no section or elevation names the storeys")})
    titles = title_counts(texts)
    rungs.append({"rung": "title", "count": max((t["count"] for t in titles), default=None),
                  "confidence": CONFIDENCE["title"], "evidence": [e for t in titles for e in t["evidence"]][:6],
                  "note": "; ".join(f"'{t['text']}': {t['how']}" for t in titles[:4]) or "no text lists the floors"})
    items = area_items(texts)
    areas = {k: _first(items, k, near) for k in ("ground", "typical", "total", "parcel")}
    count, note = None, "no total and typical floor area"
    g, ty, tot = (areas[k]["value"] if areas[k] else None for k in ("ground", "typical", "total"))
    if tot and ty:
        if g:
            k = 1 + round((tot - g) / ty)
            fit = abs(tot - (g + (k - 1) * ty)) <= 0.10 * ty
        else:
            k = round(tot / ty)
            fit = abs(tot - k * ty) <= 0.10 * ty
        if fit and 1 <= k <= COUNT_MAX:
            count = k
            note = (f"total {tot:.0f} m2 = " + (f"footprint {g:.0f} + " if g else "") +
                    f"{k - (1 if g else 0)} x typical {ty:.0f} m2")
        else:
            note = f"total {tot:.0f} m2 is no whole number of typical floors {ty:.0f} m2"
    elif ty or g:
        note = ("the area table gives " + ", ".join(f"{w} {v:.0f} m2" for w, v in (("footprint", g), ("typical", ty))
                                                     if v) + " but no total")
    rungs.append({"rung": "area_table", "count": count, "confidence": CONFIDENCE["area_table"],
                  "evidence": [e for i in items for e in i["evidence"]][:6], "note": note})
    zon = zoning_items(texts)
    zcount, zconf, znote, zev = None, CONFIDENCE["zoning_count"], "no zoning text gives a count", []
    if zon["count"]:
        zcount, zev = max(i["value"] for i in zon["count"]), zon["count"][0]["evidence"]
        znote = f"'{zon['count'][0]['text']}'"
    elif zon["height"]:
        h = max(i["value"] for i in zon["height"])
        zcount, zconf, zev = max(1, int(h // STOREY_M)), CONFIDENCE["zoning_height"], zon["height"][0]["evidence"]
        znote = f"height limit {h:.2f} m / {STOREY_M:.2f} m a storey"
    elif zon["far"] and areas["parcel"] and (ty or gross):
        far = max(i["value"] for i in zon["far"])
        base = ty or gross
        k = round(far * areas["parcel"]["value"] / base)
        if 1 <= k <= COUNT_MAX:
            zcount, zconf, zev = k, CONFIDENCE["zoning_far"], zon["far"][0]["evidence"] + areas["parcel"]["evidence"]
            znote = (f"emsal {far:.2f} x parcel {areas['parcel']['value']:.0f} m2 / floor {base:.0f} m2")
    rungs.append({"rung": "zoning", "count": zcount, "confidence": zconf, "evidence": zev, "note": znote})
    matches = bool(floor_role(gross, g, ty) and floor_role(gross, g, ty)["role"] == "typical")
    kind = building_type(signals, matches)
    rungs.append({"rung": "type_default", "count": TYPE_DEFAULTS.get(kind) if kind else None,
                  "confidence": CONFIDENCE["type_default"], "kind": kind,
                  "evidence": [{"rule": "plan_signals", "text": json.dumps(signals, sort_keys=True)}],
                  "note": (f"{TYPE_NAMES.get(kind, kind)}: lifts {signals['lifts']}, flat words {signals['flat_words']}, "
                           f"kitchens {signals['kitchens']}, stairs {signals['stairs'] + signals['stair_words']}"
                           + (", typical floor area matches" if matches else "") if kind else
                           "the plan shows no building type with a default storey count")})
    return rungs, areas


# --------------------------------------------------------------------------------------------------- the apply
def _label_for(order: int, base_label: str, typical_label: Optional[str], names: dict) -> str:
    if order in names:
        return names[order]
    if order == 0:
        return "Zemin Kat" if (typical_label or "Kat").endswith("Kat") else "Ground Floor"
    if typical_label:
        return f"{order}. {typical_label}" if typical_label.endswith("Kat") else f"{typical_label} {order}"
    folded = _fold(base_label)
    if "KAT" in folded or not re.search(r"FLOOR|LEVEL|GESCHOSS|ETAGE", folded):
        return f"{order}. Kat"
    return f"Level {order}"


def _project_answers(project_dir: Optional[Path]) -> dict:
    if project_dir is None:
        return {}
    p = Path(project_dir) / "architect_answers.json"
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data.get("answers", data) if isinstance(data, dict) else {}


def _own_orders(r) -> list:
    typ = (r.level or {}).get("typical")
    return list(typ["orders"]) if typ else [r.level["order"]]


def infer(plans: list, regions: list, docs: list, values: dict, warnings: list, conflict: Callable,
          section_storeys: Optional[dict] = None, project_dir: Optional[Path] = None) -> Optional[dict]:
    """The storeys record (the module docstring); the plans' levels are extended in place. None when no plan is read."""
    read = [r for r in plans if r.use == "read" and r.level]
    if not read:
        return None
    if any(r.level.get("kind") == "attic" or r.level.get("roof_terrace") for r in read):
        return {"count": None, "rule": None, "inferred": [], "note": "the top of the building is drawn (an attic or a "
                                                                      "roof terrace plan): no storey inferred"}
    if not any(o >= 0 for r in read for o in _own_orders(r)):
        return {"count": None, "rule": None, "inferred": [], "note": "only basements are drawn: no storey inferred"}
    base = max(read, key=lambda r: (max(_own_orders(r)), r.level.get("typical") is not None))
    texts = evidence_texts(regions, docs)
    gross = gross_area(base)
    signals = plan_signals(base)
    sections = [r for r in regions if r.cls in ("section", "elevation") and r.use in ("heights", "exterior")]
    names = dict(section_storeys or {})
    if not names:
        from wenart.sheets import levels as LV
        names = LV.storey_words([r for r in regions if r.cls == "elevation" and r.use == "exterior"])
    pre_drawn = sorted({o for r in read for o in _own_orders(r) if o >= 0})
    every = {o for r in read for o in _own_orders(r)}
    rungs, areas = ladder(values, names, sections, texts, gross, signals, len(pre_drawn),
                          _project_answers(project_dir), drawn_all=len(every), near=(base.file, base.box))
    g = areas["ground"]["value"] if areas["ground"] else None
    ty = areas["typical"]["value"] if areas["typical"] else None
    role = floor_role(gross, g, ty)
    rec: dict = {"count": None, "rule": None, "confidence": None, "guess": False, "base_region": base.id,
                 "drawn": [B.level_id(o) for o in pre_drawn], "gross_area_m2": gross, "signals": signals,
                 "areas": {k: ({"value": v["value"], "text": v["text"]} if v else None) for k, v in areas.items()},
                 "floor_role": role, "ladder": rungs, "inferred": [], "ground_from_typical": False,
                 "cantilevers": None, "open_point": None}
    # Which floor the drawn plan is: a level the drawing or the brief names stays; an assumed one follows the area table
    is_typical = bool(base.level.get("typical"))
    shifted = False
    if role and role["role"] == "typical" and not is_typical:
        if base.level.get("method") == "assumed":
            is_typical = True
            shifted = base.level["order"] == 0 and not any(r is not base and 1 in _own_orders(r) for r in read)
            rec["role_note"] = f"{base.id} is the typical floor: {role['reason']}"
            warnings.append(f"{base.file} {base.id}: an untitled plan read as the typical floor (inferred): "
                            f"{role['reason']}")
        else:
            text = (f"{base.file} {base.id}: the area table says the plan is the typical floor ({role['reason']}), "
                    f"its level '{base.level.get('label')}' comes from "
                    f"{'the brief' if getattr(base, 'user_level', None) else 'its title'}: the level is kept")
            conflict("other", [base.id], text, "the named level kept; the area table's reading listed")
            warnings.append(text)
            rec["role_note"] = text
    own = [1] if shifted else _own_orders(base)
    drawn = sorted({o for r in read for o in (own if r is base else _own_orders(r)) if o >= 0})
    rec["drawn"] = [B.level_id(o) for o in drawn]
    have = drawn[-1] + 1
    single = len(drawn) == 1
    # The count: the first rung with one (the user and the architect's answer first)
    chosen = next((x for x in rungs if x.get("count")), None)
    counts = {x["rung"]: x["count"] for x in rungs if x.get("count")}
    if len(set(counts.values())) > 1:
        warnings.append("storeys: the documents disagree on the storey count ("
                        + ", ".join(f"{k} {v}" for k, v in counts.items()) + f"); {chosen['rung']} wins (trust order)")
    if chosen is not None and chosen["rung"] == "type_default" and not single:
        chosen = None                         # a guess never adds to a building whose storeys are drawn
    ground = [0] if is_typical and 0 not in drawn else []
    if chosen is None:
        if not ground:
            rec["note"] = "no evidence gives a storey count: the drawn storeys are kept"
            return rec
        chosen = {"rung": "area_table", "count": have, "confidence": CONFIDENCE["area_table"] / 2, "evidence": [],
                  "note": "the typical floor stands over a ground floor (no count in the documents)"}
    count = int(chosen["count"])
    rec.update(count=count, rule=chosen["rung"], confidence=round(float(chosen["confidence"]), 2),
               guess=chosen["rung"] == "type_default", rule_note=chosen.get("note"))
    if rec["guess"]:
        rec["guess_note"] = (f"no document gives the storey count; the type default of "
                             f"{TYPE_NAMES.get(chosen.get('kind'), 'this building type')} is {count} storeys. Give the "
                             f"real number in "
                             f"the brief (storeys: N) or answer the architect's open point {OPEN_POINT_KEY}")
    if count < have:
        warnings.append(f"storeys: {chosen['rung'].replace('_', ' ')} counts {count} storeys, the plans draw {have}: "
                        f"the drawn storeys are kept")
    new_up = list(range(have, count))
    if not new_up and not ground:
        rec["note"] = f"{chosen['rung'].replace('_', ' ')} counts {count} storeys: every one is drawn"
        return rec
    _extend(base, own, new_up, ground, is_typical, not shifted, names, rec, chosen)
    rec["open_point"] = {"key": OPEN_POINT_KEY, "default": count,
                         "options": sorted({max(count - 2, 1), max(count - 1, 1), count, count + 1, count + 2}),
                         "severity": "major" if rec["guess"] else "minor",
                         "question": f"How many storeys does the building have? The documents draw {len(drawn)}; "
                                     f"{count} inferred from {chosen['rung'].replace('_', ' ')}"
                                     + (" (a guess)" if rec["guess"] else "")}
    if ground and g and ty and g < ty * (1.0 - CANTILEVER_SHARE):
        rec["cantilevers"] = {"ground_m2": g, "typical_m2": ty,
                              "reason": f"the footprint ({areas['ground']['text']}: {g:.0f} m2) is smaller than the "
                                        f"typical floor ({areas['typical']['text']}: {ty:.0f} m2): the ground floor "
                                        f"has no cantilevered balconies"}
    lv_text = ", ".join(f"{i['level_id']} {i['label']}" for i in rec["inferred"])
    warnings.append(f"storeys: {count} storeys from {chosen['rung'].replace('_', ' ')} ({chosen.get('note')}); "
                    f"{base.id} stands for the storeys the documents do not draw: {lv_text} (inferred"
                    + (", a guess" if rec["guess"] else "") + ")")
    return rec


def _extend(base, own: list, new_up: list, ground: list, is_typical: bool, keep_labels: bool, names: dict, rec: dict,
            chosen: dict) -> None:
    """``base``'s level stands for ``new_up`` above it and the ground floor (``ground``) below it (in place): its
    ``typical`` record (the real10 mechanism) gets the new orders, ids and labels, listed as inferred with the rule.
    ``own``: the orders the plan itself draws (a typical plan read off an assumed ground floor: [1])."""
    lev = base.level
    typ = lev.get("typical")
    orders = sorted(set(own) | set(new_up) | set(ground))
    typical_label = (typ or {}).get("label")
    if is_typical and not typical_label:
        folded = _fold(lev.get("label"))
        typical_label = "Typical Floor" if re.search(r"FLOOR|LEVEL", folded) and "GROUND" not in folded else \
            "Normal Kat"
    old_labels = (dict(zip(typ["orders"], typ["labels"])) if typ else {lev["order"]: lev["label"]}) if keep_labels \
        else {}
    labels = [old_labels.get(o) or _label_for(o, lev["label"], typical_label, names) for o in orders]
    inferred_orders = sorted(set(new_up) | set(ground))
    reason = {o: (f"the ground floor: the typical plan stands for it ({rec.get('role_note') or 'no plan of its own'})"
                  if o == 0 and ground else
                  f"storey {o + 1} of {rec['count']} ({chosen['rung'].replace('_', ' ')}: {chosen.get('note')})")
              for o in inferred_orders}
    how = (typ or {}).get("how")
    new_typ = {"label": typical_label or lev["label"], "orders": orders, "ids": [B.level_id(o) for o in orders],
               "labels": labels,
               "inferred": sorted(set((typ or {}).get("inferred") or []) | {B.level_id(o) for o in inferred_orders}),
               "how": how if how in ("section", "title") else "inferred",
               "inference": {"rule": rec["rule"], "count": rec["count"], "confidence": rec["confidence"],
                             "guess": rec["guess"]}}
    lev.update(order=orders[0], id=B.level_id(orders[0]), label=labels[0], typical=new_typ)
    for o in inferred_orders:
        rec["inferred"].append({"level_id": B.level_id(o), "order": o, "label": labels[orders.index(o)],
                                "copy_of_region": base.id, "rule": rec["rule"], "confidence": rec["confidence"],
                                "guess": rec["guess"], "reason": reason[o]})
    rec["ground_from_typical"] = bool(ground) and is_typical


# ---------------------------------------------------------------------------------- side texts and window evidence
def side_texts(region, texts: list) -> list:
    """``[{kind: party | street, text, point (source units), entity, layer}]`` (pure): the party-wall and street texts
    near a plan (inside its box or up to ``SIDE_REACH_M`` outside it)."""
    from wenart.sheets.model import point_box_distance

    mpu = getattr(region, "metres_per_unit", None) or 0.0
    reach = SIDE_REACH_M / mpu if mpu else 0.0
    out = []
    for t, f in texts:
        if f != region.file:
            continue
        folded = _fold(t.text)
        kind = "party" if PARTY_RE.search(folded) else "street" if STREET_RE.search(folded) else None
        if kind is None or point_box_distance(t.point, region.box) > reach:
            continue
        ev = getattr(t, "evidence", None) or {}
        out.append({"kind": kind, "text": t.text.strip(), "point": [round(t.point[0], 4), round(t.point[1], 4)],
                    "entity": ev.get("entity") or t.id, "layer": ev.get("layer") or t.layer})
    return out


TAG_RE = re.compile(r"^\s*(\d{2,4})\s*/\s*(\d{2,4})\s*$")
WINDOW_BLOCK_WORDS = ("PENCERE", "PENC", "WINDOW", "FENSTER", "FENETRE", "VENTANA", "FINESTRA")


def window_tag(text: str, layer: Optional[str]) -> Optional[tuple]:
    """``(width_m, height_m)`` of a window size tag (``150/140`` in cm, ``1500/1400`` in mm), or None: a ``W/H`` text
    whose height is a window's (at most 1.80 m; a door's ``90/210`` is no window tag), or any ``W/H`` on a window layer
    (pure)."""
    from wenart.ingest.generic import layer_names as LN

    m = TAG_RE.match(str(text or ""))
    if not m:
        return None
    w, h = int(m.group(1)), int(m.group(2))
    div = 1000.0 if max(w, h) >= 400 else 100.0
    wm, hm = w / div, h / div
    if not (0.3 <= wm <= 6.0 and 0.3 <= hm <= 3.0):
        return None
    on_layer = LN.layer_role(layer) in ("window", "glass")
    if hm > 1.80 and not on_layer:
        return None
    if LN.layer_role(layer) == "door":
        return None
    return (round(wm, 3), round(hm, 3))


def windows_drawn(region) -> dict:
    """What a plan draws of windows (pure): entities on a window or glass layer (``layer_names``), window blocks (a
    block name with a window word) and window size tags (``window_tag``)."""
    from wenart.ingest.generic import layer_names as LN

    layer_ents = blocks = 0
    for e in getattr(region, "ents", None) or []:
        if LN.layer_role(e.layer) in ("window", "glass") and e.kind not in ("TEXT", "MTEXT"):
            layer_ents += 1
        name = _fold(e.block or "")
        if name and any(w in name for w in WINDOW_BLOCK_WORDS):
            blocks += 1
    tags = sum(1 for t in getattr(region, "texts", None) or [] if window_tag(t.text, t.layer))
    return {"layer_entities": layer_ents, "blocks": blocks, "tags": tags,
            "draws_windows": bool(layer_ents or blocks or tags)}


def window_sizes(regions: list) -> list:
    """``[{width, height, text, region, entity}]``: the window size tags of every region of the documents (a plan the
    brief leaves out included: the project's own windows, real20's beside real21's) (pure)."""
    out = []
    for r in regions:
        for t in getattr(r, "texts", None) or []:
            wh = window_tag(t.text, t.layer)
            if wh:
                out.append({"width": wh[0], "height": wh[1], "text": t.text.strip(), "region": r.id,
                            "entity": (getattr(t, "evidence", None) or {}).get("entity") or t.id})
    return out


def completion_record(regions: list, docs: list) -> dict:
    """``sheets.json`` ``completion``: per plan region its window evidence and side texts, and the documents' window
    size tags (``wenart.ingest.completion`` reads them)."""
    texts = None
    per = {}
    for r in regions:
        if r.cls not in ("floor_plan", "alternative_floor_plan", "furniture_plan") or r.kind == "raster":
            continue
        if texts is None:
            texts = [(t, doc.file) for doc in docs for s in getattr(doc, "sheets", None) or []
                     for t in getattr(s, "texts", None) or []]
        per[r.id] = {"windows": windows_drawn(r), "side_texts": side_texts(r, texts)}
    return {"regions": per, "window_sizes": window_sizes(regions)}
