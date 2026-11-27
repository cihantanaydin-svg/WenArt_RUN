"""Entrances from drawn evidence (27 Nov 2026, audit fix round 5a, rule R08).

What:

- ``open_porches(b, strokes_by_level, warn)``: a gap in an outer wall that the reading saw as a gap (no window symbol:
  an unclassified or empty gap, or one ``levels.model.facade_gaps`` typed a window by the ground outside) whose bottom
  is the floor a few steps over the ground (``DROP_MAX_M``) is an open entrance when the drawing shows one: (i) steps
  drawn outside it (a stair the reading found within ``STEP_REACH_M`` outside its face), (ii) a ground or threshold
  level mark within ``MARK_REACH_M`` outside it (``facade_gaps`` looks only 1.0 m out), or (iii) the space behind it is
  a small recess (under ``PORCH_MAX_M2``) with no label of its own whose only other openings are doors. A recess (or
  a space whose label is a porch word) is a covered porch: an open-air space under the slab above (``room_type``
  porch, never a room with a window), its unlabelled name the role name ``PORCH_NAME``, the gap an open mouth
  (``type`` opening, ``drawn_type`` kept as the gap); its inner door gets the building entrance record (steps from its
  floor down to the ground, from the marks) and is the main entrance unless a drawn entrance word or mark names another
  door. Behind a labelled room the gap is an entrance door instead (its ``site.entrances`` record with its steps).
- ``entrance_words(b, texts_by_level, warn)``: an entrance word outside the walls ('BİNA GİRİŞİ', 'GİRİŞ', 'DAİRE
  GİRİŞİ', 'ENTRANCE', 'EINGANG') names the nearest outside door within ``WORD_REACH_M`` (one door only, the nearest):
  ``entrance_word`` on the door, and the building word (bina, apartman, ana, main, haus) makes it the main entrance;
  'DÜKKAN GİRİŞİ' names a shop entrance (``entrance_of: shop``, never the building's main entrance while a building
  word names another). A word-named door the terrain stands at most ``GROUND_TOL_M`` over is a flush entrance (the
  ground is lowered to it), never a door 'below the ground'.

Why: real06's recessed porch, open to the east with three steps 3-2-1 down to the ±0.00 mark 1.64 m out, was built as
a closed 2.1 m² 'Oda (hall)' with a 1.88 m window (``facade_gaps`` looked for a mark within 1.0 m), and the main
entrance went to the 0.75 m veranda door; real17's 'BİNA GİRİŞİ' lay outside the walls, was dropped as a room label
(RC6), and the shop door became the main entrance.

How: pure on the building JSON (``completion.Level`` for what lies on either side), run by ``completion`` before and
after the core rules; every change carries its reason (``type_inferred``, ``adjusted_by_ai``, ``main_reason``).
"""
from __future__ import annotations

import math
import re
from typing import Callable, Optional

from shapely.geometry import Point

PORCH_MAX_M2 = 4.0              # a recess this small behind a facade gap is a porch
MARK_REACH_M = 2.5              # a ground or threshold mark this close outside the gap marks an entrance
STEP_REACH_M = 2.0              # a stair this close outside the gap's face is its steps
DROP_MAX_M = 1.2                # the gap's floor at most this over the ground (a few steps; levels.model's limit)
GAP_W_M = (0.8, 4.0)            # a passage's width
WORD_REACH_M = 2.0              # an entrance word names the nearest outside door this close
GROUND_TOL_M = 0.20             # a word-named door this far under the terrain is a flush entrance (ground lowered)
PORCH_NAME = "Giriş"
GROUND_KINDS = ("ground_finished", "ground", "ground_natural", "threshold")
WINDOW_CONTENT_RULES = ("no_glass", "framed_window", "glazed_facade", "sliding_window", "window_block", "size_tag")
PORCH_WORD_RE = re.compile(r"(?<![a-z])(?:sundurma|portik|porch|giris\s+sacagi|on\s+giris)(?![a-z])")
ENTRANCE_WORD_RE = re.compile(r"(?<![a-z])(?:(?:bina|apartman|daire|ana|ev|villa|konut)\s+)?giris(?:i|e)?(?![a-z])|"
                              r"(?<![a-z])(?:main\s+)?entrance(?![a-z])|(?<![a-z])(?:haus)?eingang(?![a-z])|"
                              r"(?<![a-z])entree(?![a-z])")
BUILDING_WORD_RE = re.compile(r"(?<![a-z])(?:bina|apartman|ana|villa|konut|main|haus)(?![a-z])")
SHOP_WORD_RE = re.compile(r"(?<![a-z])(?:dukkan|magaza|isyeri|ofis|shop|store|laden)(?![a-z])")
FLAT_WORD_RE = re.compile(r"(?<![a-z])daire(?![a-z])")


def _fold(text) -> str:
    from wenart import building as B
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def _area(room: dict) -> float:
    from wenart.ingest import completion as CP

    if room.get("area_computed") is not None:
        return float(room["area_computed"])
    p = CP._poly(room.get("polygon"))
    return float(p.area) if p is not None else 0.0


def _labelled(room: dict) -> bool:
    return bool(room.get("label_raw")) and not room.get("label_inferred")


def _sides(level, o: dict) -> list:
    from wenart.ingest import core_rules as CR
    return CR._sides(level, o)


def _room_openings(level, room: dict, skip: dict) -> list:
    """The openings on the room's outline other than ``skip`` (pure)."""
    from wenart.ingest import completion as CP

    p = CP._poly(room.get("polygon"))
    if p is None:
        return []
    ring = p.exterior
    out = []
    for x in level.openings:
        if x is skip or x.get("virtual") or not x.get("center"):
            continue
        w = level.walls.get(x.get("wall_id"))
        reach = (float(w.get("thickness") or 0.2) if w else 0.2) / 2.0 + 0.15
        if ring.distance(Point(x["center"][:2])) <= reach:
            out.append(x)
    return out


def _seen_as_gap(o: dict) -> bool:
    """The reading saw a gap here, not a window symbol: an unclassified or empty gap, or a facade gap the levels model
    typed a window by the ground outside (its bottom is the floor; pure)."""
    if o.get("virtual") or o.get("lift_door"):
        return False
    if any(isinstance(e, dict) and e.get("rule") in WINDOW_CONTENT_RULES for e in o.get("evidence") or []) \
            or "window" in str(o.get("type_raw") or "").lower():
        return False                      # frame lines drawn in it: a window the reading could not confirm
    if o.get("type") == "opening" and o.get("drawn_type") in (None, "opening"):
        return True
    ti = o.get("type_inferred") if isinstance(o.get("type_inferred"), dict) else {}
    return o.get("type") == "window" and o.get("drawn_type") == "opening" and ti.get("method") == "facade_gap"


def _outside_face(level, o: dict):
    """``(face point, outward unit, inside room)`` of an opening with the outside on exactly one side, else None."""
    from wenart.ingest import completion as CP

    sides = _sides(level, o)
    kinds = [s[0] for s in sides]
    if len(sides) != 2 or kinds.count("outside") != 1:
        return None
    k = kinds.index("outside")
    room = sides[1 - k][1]
    w = level.walls.get(o.get("wall_id"))
    _a, u, _l = CP._axis(w)
    n = (-u[1], u[0])
    ow = (n[0], n[1]) if k == 0 else (-n[0], -n[1])
    half = float(w.get("thickness") or 0.2) / 2.0
    c = o["center"]
    return (c[0] + ow[0] * half, c[1] + ow[1] * half), ow, room


def entrance_evidence(b: dict, level, lv: dict, o: dict, strokes: Optional[list] = None) -> Optional[dict]:
    """What says the gap ``o`` is an open entrance (module docstring, (i)-(iii)) with the drop under its floor, or None
    (pure). ``{"room", "face", "outward", "drop", "ground_z", "reasons": [...], "recess": bool}``."""
    from wenart.ingest import core_rules as CR

    if not _seen_as_gap(o) or not GAP_W_M[0] <= float(o.get("width") or 0.0) <= GAP_W_M[1]:
        return None
    got = _outside_face(level, o)
    if got is None or got[2] is None:
        return None
    face, ow, room = got
    z = lv.get("elevation")
    if not isinstance(z, (int, float)):
        return None
    floor = float(z)
    reasons, mark_z = [], None
    for m in b.get("level_marks") or []:
        if m.get("level_id") not in (None, lv["id"]) or not m.get("point") or m.get("door_id") \
                or m.get("kind") not in GROUND_KINDS or not isinstance(m.get("z"), (int, float)):
            continue
        dx, dy = float(m["point"][0]) - face[0], float(m["point"][1]) - face[1]
        d = math.hypot(dx, dy)
        if d <= MARK_REACH_M and dx * ow[0] + dy * ow[1] > -0.05 and -0.05 <= floor - float(m["z"]) <= DROP_MAX_M:
            if mark_z is None or d < mark_z[1]:
                mark_z = (float(m["z"]), d, m)
    if mark_z is not None:
        reasons.append(f"the level mark {mark_z[2].get('raw') or mark_z[2].get('id')} {mark_z[1]:.2f} m outside it")
    probe = Point(face[0] + ow[0] * 0.5, face[1] + ow[1] * 0.5)
    for run in strokes or []:
        poly = run.get("polygon")
        if poly is not None and not poly.is_empty and poly.distance(probe) <= STEP_REACH_M \
                and (level.outline is None or not level.outline.contains(poly.centroid)):
            reasons.append(f"steps drawn {poly.distance(probe):.2f} m outside it")
            break
    others = _room_openings(level, room, o)
    recess = (not _labelled(room) and _area(room) < PORCH_MAX_M2 and bool(others)
              and all(x.get("type") == "door" for x in others)) or bool(PORCH_WORD_RE.search(_fold(room.get("label"))))
    if recess:
        reasons.append(f"behind it a {_area(room):.1f} m² recess with no label of its own whose only other "
                       f"opening(s) are door(s) ({', '.join(x['id'] for x in others)})")
    if not reasons:
        return None
    if mark_z is not None:
        gz = mark_z[0]
    else:
        zs = [g for g in CR.ground_zs(b) if -0.05 <= floor - g <= DROP_MAX_M]
        gz = max(zs) if zs else None
    if gz is None:
        return None                          # no ground a few steps under the floor: not at floor level
    return {"room": room, "face": face, "outward": ow, "drop": round(max(0.0, floor - gz), 3), "ground_z": gz,
            "reasons": reasons, "recess": recess, "others": others}


def _entrance(b: dict, level, lv: dict, door: dict, hall: dict, why: str) -> Optional[dict]:
    """A ``site.entrances`` record for ``door`` out of ``hall`` (``core_rules._entrance_record``), replacing any it had."""
    from wenart.ingest import core_rules as CR

    sides = _sides(level, door)
    if len(sides) != 2 or door.get("wall_id") not in level.walls:
        return None
    side = 1 if (sides[0][1] or {}).get("id") == hall["id"] else -1
    ent = CR._entrance_record(b, door, level, lv, hall, {"wall_id": door["wall_id"], "side": side}, why)
    ent["drawn"] = True
    site = b.setdefault("site", {})
    site["entrances"] = [e for e in site.get("entrances") or [] if e.get("door_id") != door["id"]] + [ent]
    return ent


def _set_main(b: dict, ent: dict, why: str) -> None:
    for e in (b.get("site") or {}).get("entrances") or []:
        if e is not ent and e.get("main"):
            e["main"] = False
            e.pop("main_reason", None)
    ent["main"], ent["main_reason"] = True, why


def _word_main(b: dict) -> bool:
    """A drawn building-entrance word already names the main entrance's door."""
    ops = {o.get("id"): o for o in b.get("openings") or []}
    return any(e.get("main") and (ops.get(e.get("door_id")) or {}).get("entrance_of") == "building"
               for e in (b.get("site") or {}).get("entrances") or [])


def open_porches(b: dict, strokes_by_level: Optional[dict] = None, warn: Optional[Callable] = None) -> list[dict]:
    """The open entrances and porches (module docstring), in place; one record per gap changed."""
    from wenart.ingest import completion as CP

    out: list[dict] = []
    for lv in b.get("levels") or []:
        lid = lv["id"]
        if lv.get("base_level_id") or not isinstance(lv.get("elevation"), (int, float)):
            continue
        level = CP.Level(b, lid)
        if level.outline is None:
            continue
        for o in list(level.openings):
            ev = entrance_evidence(b, level, lv, o, (strokes_by_level or {}).get(lid))
            if ev is None:
                continue
            room = ev["room"]
            why = (f"{o['id']} ({float(o.get('width') or 0):.2f} m) is a gap in the outer wall at the floor of "
                   f"{room['id']}, {ev['drop']:.2f} m over the ground ({ev['ground_z']:+.2f} m): "
                   + "; ".join(ev["reasons"]))
            if o.get("type") == "window":
                for k in ("sill_height", "height"):
                    if "drawn_" + k in o:
                        o[k] = o.get("drawn_" + k)
                for k in ("guard", "french_window", "sill_height_source"):
                    o.pop(k, None)
            o["drawn_type"] = "opening"
            if ev["recess"]:
                why += f": an open entrance porch, {o['id']} its open mouth (R08)"
                o["type"], o["sill_height"] = "opening", None
                o["type_inferred"] = {"method": "open_porch", "reason": why}
                before = {"room_type": room.get("room_type"), "label": room.get("label")}
                room["room_type"] = "porch"
                room["covered"] = True
                if not _labelled(room):
                    room["label"] = PORCH_NAME
                    room["label_inferred"] = {"method": "role", "role": "porch", "reason": "an unlabelled open porch (R08, R28)"}
                room["adjusted_by_ai"] = {"by": "code", "rule": "open_porch", "reason": why, "changed": before}
                doors = [x for x in ev["others"] if x.get("type") == "door"]
                for d in doors:
                    s = _sides(level, d)
                    hall = next((x[1] for x in s if x[1] is not None and x[1]["id"] != room["id"]), None)
                    if hall is None:
                        continue
                    ent = _entrance(b, level, lv, d, hall, f"{d['id']} opens from {hall['id']} onto the open porch "
                                                            f"{room['id']}; " + why)
                    if ent is not None and len(doors) == 1 and not _word_main(b):
                        _set_main(b, ent, f"{d['id']}, the door in the open porch {room['id']} (drawn "
                                          f"{'; '.join(ev['reasons'])}): the building entrance (R08, inferred)")
                out.append({"opening": o["id"], "level_id": lid, "porch": room["id"], "reason": why})
            else:
                why += f": an entrance door (R08)"
                o["type"], o["sill_height"] = "door", None
                if o.get("height") is None:
                    o["height"] = 2.1
                o["type_inferred"] = {"method": "facade_gap_entrance", "reason": why}
                _entrance(b, level, lv, o, room, why)
                out.append({"opening": o["id"], "level_id": lid, "door": o["id"], "reason": why})
            if warn:
                warn(f"entrances: {why}")
    return out


def _word_kind(text: str) -> Optional[str]:
    f = _fold(text)
    if not ENTRANCE_WORD_RE.search(f) or re.search(r"(?<![a-z])giris\s+(?:holu|hol|kat|katı|kati)(?![a-z])", f):
        return None                         # 'GİRİŞ HOLÜ' / 'GİRİŞ KATI' name a room or a storey
    if SHOP_WORD_RE.search(f):
        return "shop"
    if FLAT_WORD_RE.search(f):
        return "flat"
    if BUILDING_WORD_RE.search(f):
        return "building"
    return "entrance"


QUALIFIER_REACH_M = 0.8         # a qualifier word ('BİNA', 'DÜKKAN', 'DAİRE') this close to an entrance word is its own


def _with_qualifier(t: dict, texts: list) -> str:
    """The entrance word with the qualifier written as a text of its own beside or above it ('BİNA' over 'GİRİŞİ'):
    'BİNA GİRİŞİ' (pure); the text alone when it is no bare entrance word or no qualifier stands near."""
    text = str(t.get("text") or "")
    f = _fold(text)
    if not ENTRANCE_WORD_RE.search(f) or BUILDING_WORD_RE.search(f) or SHOP_WORD_RE.search(f) or FLAT_WORD_RE.search(f):
        return text
    best = None
    for x in texts or []:
        if x is t or x.get("x") is None:
            continue
        g = _fold(x.get("text"))
        if len(g.split()) > 2 or not (BUILDING_WORD_RE.search(g) or SHOP_WORD_RE.search(g) or FLAT_WORD_RE.search(g)):
            continue
        d = math.hypot(float(x["x"]) - float(t["x"]), float(x["y"]) - float(t["y"]))
        if d <= QUALIFIER_REACH_M and (best is None or d < best[0]):
            best = (d, str(x.get("text") or ""))
    return f"{best[1]} {text}" if best else text


def entrance_words(b: dict, texts_by_level: Optional[dict], warn: Optional[Callable] = None) -> list[dict]:
    """The entrance words outside the walls (module docstring), in place; one record per word bound to a door."""
    from wenart.ingest import completion as CP

    out: list[dict] = []
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    ents = {e.get("door_id"): e for e in (b.get("site") or {}).get("entrances") or []}
    for lid, texts in sorted((texts_by_level or {}).items()):
        if lid not in levels:
            continue
        level = None
        words = [(t, _with_qualifier(t, texts)) for t in texts or [] if t.get("x") is not None]
        words = [(t, k, full) for t, full in words for k in [_word_kind(full)] if k is not None]
        if not words:
            continue
        level = CP.Level(b, lid)
        if level.outline is None:
            continue
        doors = []
        for o in level.openings:
            if o.get("type") != "door" or o.get("virtual") or o.get("lift_door") or not o.get("center"):
                continue
            kinds = [s[0] for s in _sides(level, o)]
            if kinds.count("outside") == 1 or ("balcony" in kinds and "room" in kinds):
                doors.append(o)
        used: set = set()
        for t, kind, full in words:
            p = Point(float(t["x"]), float(t["y"]))
            if level.room_at((p.x, p.y)) is not None or level.outline.buffer(-0.05).contains(p):
                continue                    # inside the walls: a room's label, not an entrance mark
            near = sorted((p.distance(Point(o["center"][:2])), o["id"], o) for o in doors)
            near = [x for x in near if x[0] <= WORD_REACH_M]
            if not near or near[0][1] in used:
                continue
            d, oid, o = near[0]
            used.add(oid)
            o["entrance_word"] = {"text": " ".join(str(full).split()), "entity": t.get("entity"),
                                  "distance": round(d, 3), "kind": kind}
            o["entrance_of"] = "shop" if kind == "shop" else ("flat" if kind == "flat" else "building")
            rec = {"opening": oid, "level_id": lid, "word": o["entrance_word"]["text"], "kind": kind}
            e = ents.get(oid)
            if e is not None and kind in ("building", "entrance") and not e.get("into_air") \
                    and not e.get("upper_floor"):
                if e.get("below_ground") and -float(e.get("rise") or 0.0) <= GROUND_TOL_M + 1e-9 and \
                        float(e.get("ground_z") or 0.0) - float(e.get("threshold_z") or 0.0) <= GROUND_TOL_M + 1e-9:
                    e["below_ground"], e["terrain_lowered"] = False, True
                    e["reason"] = (f"{e.get('reason') or ''}; the entrance word '{o['entrance_word']['text']}' names "
                                   f"it: the ground in front is lowered to its threshold (a flush entrance, R08)")
                if not e.get("below_ground") and not (_word_main(b) and kind == "entrance"):
                    _set_main(b, e, f"{oid}, named '{o['entrance_word']['text']}' outside the walls {d:.2f} m from "
                                    f"it: the building entrance (R08, drawn)")
                    rec["main"] = True
            out.append(rec)
            if warn:
                warn(f"entrances: the word '{o['entrance_word']['text']}' outside the walls names {oid} "
                     f"({kind} entrance){' : the main entrance' if rec.get('main') else ''}")
    return out
