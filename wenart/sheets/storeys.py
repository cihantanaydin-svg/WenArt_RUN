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
import math
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
# The type defaults recorded and asked, never built (a house's upper floor is no copy of its ground floor; the synthetic
# houses' truths have one storey: the reading score's gate)
UNBUILT_DEFAULTS = ("house_stair",)
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
# 13 Nov 2026 (review S1-03a, POD-03): the stems take their suffixes (MERDİVENİ, MUTFAĞI, ASANSÖRLER ...)
LIFT_RE = re.compile(r"\bASANSOR\w*|\bLIFTS?\b|\bELEVATORS?\b|\bAUFZUG\w*|\bASCENSEURS?\b|\bASCENSOR\w*")
LIFT_MACHINE_RE = re.compile(r"\bMAKIN[AE]\w*|\bMAK\.?\s*DAIR|\bMAKN\b|\bMACHINE\s+ROOM\b|\bMASCHINEN\w*|\bMOTOR\b")
FLAT_RE = re.compile(r"\bDAIRE\w*|\bAPARTMENTS?\b|\bFLAT\s*\d|\bWOHNUNG\w*|\bAPPARTEMENTS?\b")
KITCHEN_RE = re.compile(r"\bMUTFA[KG]\w*|\bKITCHENS?\b|\bKUCHE\w*|\bCUISINES?\b|\bCOCINAS?\b|\bKITCHENETTES?\b")
STAIR_RE = re.compile(r"\bMERDIVEN\w*|\bSTAIRS?\b|\bSTAIRCASES?\b|\bTREPPE\w*|\bESCALIERS?\b|\bESCALERAS?\b")
# a fire lobby or a fire stair: a building of several storeys (R33)
FIRE_RE = re.compile(r"\bGUVENLIK\s+HOL\w*|\bYANGIN\s+MERDIVEN\w*|\bYANGIN\s+HOL\w*|\bFIRE\s+(?:LOBBY|STAIRS?|ESCAPE)\b"
                     r"|\bSICHERHEITSTREPPE\w*|\bESCALIER\s+DE\s+SECOURS\b")
# what is no floor list (review MF10): a scale, a level mark, an area expression
_SCALE_FORMS_RE = re.compile(r"(?:\b(?:O|OLCEK|SCALE|MASSTAB|ECHELLE)\s*[:=.]?\s*)?\b1\s*[/:]\s*\d{2,4}\b")
_LEVEL_MARK_RE = re.compile(r"(?:[+\-±]\s*)\d{1,3}[.,]\d{2}\b")
_AREA_EXPR_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:M2|M²|M\^2|SQM)\b|/\s*\d{1,2}\s*KAT\s*=|=\s*\d+(?:[.,]\d+)?")
# a stair note (review MF11): a riser or tread number
_STAIR_NOTE_RE = re.compile(r"\b[RB]\s*[:=]\s*\d")
# The side texts (``side_texts``): a party wall on that side, or the street
# (a neighbouring plot, 'komşu parsel', is no attached building: only the building or its wall is)
# R46 (the misfire hunters, 12 Nov 2026): a whole-label party word or joint note; never a bare KOMŞU, never a phrase
PARTY_RE = re.compile(r"\bBITISIK\b|\bATTACHED\b|\bPARTY\s+WALL\b|\bADJOINING\s+BUILDING\b|\bMITOYEN(?:NE)?\b"
                      r"|\bBRANDWAND\b|\bGRENZBEBAUUNG\b|\bNACHBARGEBAUDE\b"
                      r"|\bDEPREM\s+DERZI\b|\bDILATASYON\b|^\d+\s*CM\s+DERZ$|^DERZ$")
PARTY_LABEL_WORDS = 4                 # a party label has at most this many words (a phrase never counts)
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
        # never a scale (1/50, Ö: 1/100), a level mark (+3.50) or an area expression (2197 m2 /6KAT=366.20M2)
        folded = " ".join(_AREA_EXPR_RE.sub(" ", _LEVEL_MARK_RE.sub(" ", _SCALE_FORMS_RE.sub(" ", folded))).split())
        listed = LV._listed_floors(folded)
        if listed is None:
            m = FLOOR_LIST.search(folded)
            listed = LV._listed_floors(f"{m.group(1)} KAT") if m else None
        if listed is not None:
            orders, _word = listed
            if orders[0] > 1 or orders != list(range(orders[0], orders[-1] + 1)) or orders[-1] + 1 > COUNT_MAX:
                continue                    # floors listed from the first, one after another, at most COUNT_MAX
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
    notes = [t for t, _f in texts if _STAIR_NOTE_RE.search(_fold(t.text))]
    for t, f in texts:
        folded = _fold(t.text)
        m = ZONING_COUNT.search(folded)
        if m:
            n = int(next(g for g in m.groups() if g))
            if 1 <= n <= COUNT_MAX:
                out["count"].append({"value": n, "text": t.text.strip(), "evidence": [_ev(t, f, "zoning_count")]})
        m = ZONING_HEIGHT.search(folded)
        if m and re.match(r"H\s*[:=]", m.group(0)) and _bare_h_is_stair(t, folded, _num(m.group(1)), notes):
            m = None                        # a riser height at a stair (H:17.6), never a height limit (review MF11)
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


def _bare_h_is_stair(t, folded: str, value: Optional[float], notes: list) -> bool:
    """A bare ``H:`` that is a stair's riser, not a height limit (pure; review MF11): a stair note (R: or B:) in it or
    within a few text heights of it, on a stair, door or window layer, in cm, or a value of 14-22 (a riser in cm)
    with a stair note anywhere."""
    if _STAIR_NOTE_RE.search(folded) or re.search(r"\bCM\b", folded):
        return True
    layer = _fold(getattr(t, "layer", "") or "")
    if any(w in layer for w in ("MERD", "STAIR", "KAPI", "DOOR", "PENC", "WINDOW")):
        return True
    h = float(getattr(t, "height", 0.0) or 0.0)
    p = getattr(t, "point", None)
    if h > 0 and p is not None and any(getattr(o, "point", None) is not None and o is not t
                                       and math.dist(p, o.point) <= 6.0 * h for o in notes):
        return True
    return value is not None and 14.0 <= value <= 22.0 and bool(notes)


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
    lifts = flats = kitchens = stair_words = fire = 0
    for t in getattr(r, "texts", None) or []:
        folded = _fold(t.text)
        lifts += 1 if LIFT_RE.search(folded) and not LIFT_MACHINE_RE.search(folded) else 0
        flats += 1 if FLAT_RE.search(folded) else 0
        kitchens += 1 if KITCHEN_RE.search(folded) else 0
        stair_words += 1 if STAIR_RE.search(folded) else 0
        fire += 1 if FIRE_RE.search(folded) else 0
    stairs = int((getattr(r, "features", None) or {}).get("stairs") or 0)
    return {"lifts": lifts, "flat_words": flats, "kitchens": kitchens, "stairs": stairs, "stair_words": stair_words,
            "fire": fire}


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
    if several and (stair or signals.get("fire")):
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
    if chosen is not None and chosen["rung"] == "type_default" and chosen.get("kind") in UNBUILT_DEFAULTS:
        # a house's upper floor guessed from a stair alone is not built: its plan would be the ground floor's, which a
        # house's upper floor never is; the count is the architect's open point and RC14 raises it (storeys_missing)
        rec.update(count=int(chosen["count"]), rule="type_default", confidence=CONFIDENCE["type_default"], guess=True,
                   built=False, rule_note=chosen.get("note"),
                   note=f"{TYPE_NAMES.get(chosen.get('kind'))}: its upper floor is not drawn; {chosen['count']} storeys "
                        f"is a guess and is not built (give the real number in the brief: storeys: N)")
        rec["open_point"] = {"key": OPEN_POINT_KEY, "default": len(drawn), "options": [len(drawn), chosen["count"]],
                             "severity": "major", "question": "How many storeys does the house have? Its plan has a "
                                                              "stair going up, no upper floor is drawn"}
        return rec
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
    if new_up:
        below = _plan_below(read, base, own)
        reg = stacks(base, below) if below is not None else None
        if reg is not None:
            rec["registration"] = reg
        if reg is not None and not reg["ok"]:
            # review REG-04: a plan that does not stack on the storey below (another design alternative, a misread
            # plan) is no typical floor of this building: no copies, the count is a question (as R08 for stairs)
            text = (f"storeys: {chosen['rung'].replace('_', ' ')} counts {count} storeys, but {base.id} does not stack "
                    f"on {below.id} ({reg['reason']}): no storey is copied from it")
            warnings.append(text)
            conflict("other", [base.id, below.id], text, "the drawn storeys kept; the storey count is a question")
            rec.update(built=False, note=text)
            rec["open_point"] = {"key": OPEN_POINT_KEY, "default": len(drawn), "options": [len(drawn), count],
                                 "severity": "major",
                                 "question": f"How many storeys does the building have? {count} counted from "
                                             f"{chosen['rung'].replace('_', ' ')}, but the top plan {base.id} does not "
                                             f"stack on {below.id} ({reg['reason']}): which plan is the typical floor?"}
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
                                        f"typical floor ({areas['typical']['text']}: {ty:.0f} m2): the typical "
                                        f"floor's balconies are left off the inferred ground floor (its outline is "
                                        f"the typical floor's, not cut to the footprint)"}
    lv_text = ", ".join(f"{i['level_id']} {i['label']}" for i in rec["inferred"])
    warnings.append(f"storeys: {count} storeys from {chosen['rung'].replace('_', ' ')} ({chosen.get('note')}); "
                    f"{base.id} stands for the storeys the documents do not draw: {lv_text} (inferred"
                    + (", a guess" if rec["guess"] else "") + ")")
    return rec


STACK_RMS_M = 0.5                     # a plan stacks on the storey below: its outline within this RMS (R12) ...
STACK_INSIDE = 0.8                    # ... and this share of its footprint over the storey below


def _outline_m(r):
    """A plan's outline in metres (its own frame), as ``gross_area`` measures it, or None (cached)."""
    if hasattr(r, "_outline_metres"):
        return r._outline_metres
    from shapely import affinity
    from wenart.sheets import register as RG

    mpu = getattr(r, "metres_per_unit", None)
    poly = None
    if mpu and getattr(r, "ents", None):
        try:
            poly = RG.outline(r, mpu, set(RG.enclosing_outlines(r, mpu)) | RG.cut_line_entities(r))
        except Exception:  # noqa: BLE001 - a plan without an outline cannot be compared
            poly = None
        if poly is not None and not poly.is_empty and poly.geom_type == "Polygon":
            poly = affinity.scale(poly, mpu, mpu, origin=(0.0, 0.0))
        else:
            poly = None
    r._outline_metres = poly
    return poly


def _plan_below(read: list, base, own: list):
    """The read plan of the storey right below ``base``'s lowest own storey, or None."""
    lowest = min(own)
    cands = [r for r in read if r is not base and r.level and max(_own_orders(r)) < lowest
             and not getattr(r, "base_level_id", None)]
    return max(cands, key=lambda r: max(_own_orders(r)), default=None)


def stacks(top, below) -> Optional[dict]:
    """``{ok, rms_m, inside, reason}``: whether plan ``top`` stacks on plan ``below`` (pure; review REG-04): its outline
    fits the one below (``register.fit_ring``) within ``STACK_RMS_M`` and at least ``STACK_INSIDE`` of its footprint
    stands over it; None when either has no outline."""
    from shapely import affinity
    from wenart.sheets import register as RG

    a, b = _outline_m(top), _outline_m(below)
    if a is None or b is None or a.area <= 0 or b.area <= 0:
        return None
    fit = RG.fit_ring(a, b)
    moved = affinity.translate(affinity.rotate(a, fit["rotation_deg"], origin=(0.0, 0.0)), *fit["shift"])
    inside = moved.intersection(b).area / moved.area
    ok = fit["rms_m"] <= STACK_RMS_M and inside >= STACK_INSIDE
    return {"ok": ok, "below_region": below.id, "rms_m": fit["rms_m"], "inside": round(inside, 3),
            "reason": f"outline RMS {fit['rms_m']:.2f} m, {inside * 100:.0f} % of its footprint over {below.id}"
                      + ("" if ok else f" (needs at most {STACK_RMS_M} m and {STACK_INSIDE * 100:.0f} %)")}


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
def side_texts(region, texts: list, others: tuple = ()) -> list:
    """``[{kind: party | street, text, point (source units), entity, layer}]`` (pure): the party-wall and street texts
    near a plan (inside its box or up to ``SIDE_REACH_M`` outside it), never one inside another drawing's region box
    (``others``: R45, R46) nor a road level mark or an escape route (YOL KOTU, KAÇIŞ YOLU)."""
    from wenart.sheets.model import point_box_distance

    mpu = getattr(region, "metres_per_unit", None) or 0.0
    reach = SIDE_REACH_M / mpu if mpu else 0.0
    out = []
    for t, f in texts:
        if f != region.file:
            continue
        folded = " ".join(_fold(t.text).split())
        kind = ("party" if PARTY_RE.search(folded) and len(folded.split()) <= PARTY_LABEL_WORDS else
                "street" if STREET_RE.search(folded) and not re.search(r"\bYOL\s+KOTU\b|\bKACIS\s+YOLU\b", folded)
                else None)
        if kind is None or point_box_distance(t.point, region.box) > reach:
            continue
        if point_box_distance(t.point, region.box) > 0 and any(point_box_distance(t.point, o) <= 0 for o in others):
            continue                                   # inside another drawing's region box
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


TREAD_PITCH_M = (0.22, 0.35)          # the tread lines of a flight: this far apart (R08 G3) ...
TREAD_LEN_M = (0.75, 3.0)             # ... each this long ...
TREAD_RUN_MIN = 5                     # ... at least this many in a run
TREAD_ANGLE_DEG = 2.0                 # lines within this angle are parallel


def stair_strokes(region) -> list:
    """``[{corners (source units), lines, pitch_m, length_m}]`` (pure): runs of at least ``TREAD_RUN_MIN`` parallel line
    segments of ``TREAD_LEN_M`` at a pitch of ``TREAD_PITCH_M``, each overlapping the one before along its length by at
    least half the shorter: the tread lines of a flight (R08 guard G3), on any layer and inside nested blocks (DIM
    included). Hatch patterns never count, and two crossing runs in one place are a tile grid, not a stair. A segment
    sits in its angle bin and the next one over (a flight drawn at an odd whole degree lies on a bin edge: review
    CS1-07); a run found twice is kept once."""
    import bisect
    import math

    mpu = getattr(region, "metres_per_unit", None)
    if not mpu:
        return []
    bins = int(180 / TREAD_ANGLE_DEG)
    by_angle: dict = {}
    segs_all = []
    for e in getattr(region, "ents", None) or []:
        if e.kind == "HATCH":
            continue
        for st in e.strokes:
            if st.arc or len(st.pts) < 2:
                continue
            for p, q in zip(st.pts, st.pts[1:]):
                length = math.dist(p, q) * mpu
                if not TREAD_LEN_M[0] <= length <= TREAD_LEN_M[1]:
                    continue
                ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0
                x = ang / TREAD_ANGLE_DEG
                near = round(x)
                k0, k1 = int(near) % bins, (int(near) + (1 if x >= near else -1)) % bins
                idx = len(segs_all)
                segs_all.append((p, q))
                for k in {k0, k1}:
                    by_angle.setdefault(k, []).append(idx)
    runs, seen = [], []
    for key, idxs in sorted(by_angle.items()):
        ang = math.radians(key * TREAD_ANGLE_DEG)
        u, n = (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))
        items = []
        for i in idxs:
            p, q = segs_all[i]
            a0, a1 = sorted(((p[0] * u[0] + p[1] * u[1]) * mpu, (q[0] * u[0] + q[1] * u[1]) * mpu))
            off = ((p[0] + q[0]) / 2.0 * n[0] + (p[1] + q[1]) / 2.0 * n[1]) * mpu
            items.append((off, a0, a1, i))
        items.sort()
        offs = [it[0] for it in items]
        chain = [1] * len(items)
        prev = [-1] * len(items)
        for i, (off, a0, a1, _i) in enumerate(items):
            lo = bisect.bisect_left(offs, off - TREAD_PITCH_M[1])
            hi = bisect.bisect_right(offs, off - TREAD_PITCH_M[0])
            for j in range(lo, hi):
                _, b0, b1, _j = items[j]
                if min(a1, b1) - max(a0, b0) >= 0.5 * min(a1 - a0, b1 - b0) and chain[j] + 1 > chain[i]:
                    chain[i], prev[i] = chain[j] + 1, j
        used = set()
        for i in sorted(range(len(items)), key=lambda k: -chain[k]):
            if chain[i] < TREAD_RUN_MIN or i in used:
                continue
            members, k = [], i
            while k >= 0 and k not in used:
                members.append(items[k])
                used.add(k)
                k = prev[k]
            if len(members) < TREAD_RUN_MIN:
                continue
            ids = frozenset(m[3] for m in members)
            if any(ids <= s for s in seen):
                continue                    # the same run found in the next bin over
            gone = [j for j, s in enumerate(seen) if s < ids]
            for j in reversed(gone):
                seen.pop(j)
                runs.pop(j)
            seen.append(ids)
            o0, o1 = min(m[0] for m in members), max(m[0] for m in members)
            s0, s1 = min(m[1] for m in members), max(m[2] for m in members)
            corners = [[(s * u[0] + o * n[0]) / mpu, (s * u[1] + o * n[1]) / mpu]
                       for s, o in ((s0, o0), (s1, o0), (s1, o1), (s0, o1))]
            pitches = sorted(members[k][0] - members[k + 1][0] for k in range(len(members) - 1))
            runs.append({"corners": [[round(x, 4), round(y, 4)] for x, y in corners], "lines": len(members),
                         "pitch_m": round(pitches[len(pitches) // 2], 3),
                         "length_m": round(sorted(m[2] - m[1] for m in members)[len(members) // 2], 3),
                         "angle": key})
    # a tile grid: two runs crossing each other at right angles in one place
    from shapely.geometry import Polygon
    polys = [Polygon(r["corners"]).buffer(0) for r in runs]
    grid = set()
    for i, a in enumerate(runs):
        for j in range(i + 1, len(runs)):
            turn = abs(a["angle"] - runs[j]["angle"]) * TREAD_ANGLE_DEG % 180.0
            if abs(turn - 90.0) <= 2 * TREAD_ANGLE_DEG and polys[i].intersects(polys[j]) and \
                    polys[i].intersection(polys[j]).area >= 0.5 * min(polys[i].area, polys[j].area):
                grid |= {i, j}
    return [dict((k, v) for k, v in r.items() if k != "angle") for i, r in enumerate(runs) if i not in grid]



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
        others = tuple(o.box for o in regions if o is not r and getattr(o, "file", None) == r.file
                       and getattr(o, "kind", "drawing") == "drawing" and getattr(o, "box", None) is not None)
        per[r.id] = {"windows": windows_drawn(r), "side_texts": side_texts(r, texts, others),
                     "stair_strokes": stair_strokes(r)}
    return {"regions": per, "window_sizes": window_sizes(regions)}
