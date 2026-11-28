"""Entrances from drawn evidence (27 Nov 2026, audit fix round 5a, rule R08).

What:

- ``open_porches(b, strokes_by_level, warn, texts_by_level)``: on the entrance level only (``entrance_levels``: the
  street or ground storey, never an upper storey of a hillside house), a gap in an outer wall that the reading saw as a
  gap (no window symbol: an unclassified or empty gap, or one ``levels.model.facade_gaps`` typed a window by the
  ground outside) whose bottom is the floor a few steps over the ground (``STEP_MIN_M`` to ``DROP_MAX_M``) is an open
  entrance when the drawing shows one: (i) steps drawn in front of it (a stair run overlapping the band in front of the
  gap, outside its face), (ii) a ground or threshold level mark in front of it (within ``MARK_REACH_M`` out, at most
  half its width plus ``MARK_SIDE_M`` along the facade, at least a step under the floor, no wall between; each mark
  serves its nearest gap only; ``facade_gaps`` looks only 1.0 m out). Never the open edge of a balcony or terrace,
  never a garage's bay. The space behind is a covered porch when its label is a porch word, or when it is a small
  recess (under ``PORCH_MAX_M2``) with no label of its own (drawn or copied), of no wet, storage, shaft or service type,
  holding no fixture or furniture, whose other openings are doors only, with a mark or steps in front: an open-air
  space under the slab above (``room_type`` porch, never a room with a window), its unlabelled name the role name
  ``PORCH_NAME`` (``label_role`` porch), every evidenced gap of it an open mouth (``type`` opening, ``drawn_type``
  kept as the gap); its inner door gets the building entrance record (steps from its floor down to the ground of the
  mark or the terrain at the gap; ``drawn`` only with a mark or steps) and is the main entrance only where the building
  has none or its main door is no drawn door (a drawn main entrance is never taken). Behind any other room the gap is
  an entrance door instead (its ``site.entrances`` record with its steps). Rule keys ``open_porch``,
  ``facade_gap_entrance`` and ``entrance_word_main`` (``rule_guards``, audit id A-R08).
- ``entrance_words(b, texts_by_level, warn)``: an entrance word outside the walls ('BİNA GİRİŞİ', 'GİRİŞ', 'DAİRE
  GİRİŞİ', 'ENTRANCE', 'EINGANG') names the nearest outside door within ``WORD_REACH_M`` (one door only, the nearest):
  ``entrance_word`` on the door, and the building word (bina, apartman, ana, main, haus) or a bare entrance word makes
  it the main entrance; 'DÜKKAN GİRİŞİ' names a shop entrance (``entrance_of: shop``, never the building's main
  entrance while a building word names another); a vehicle, garage, service, garden or car-park word ('OTOPARK
  GİRİŞİ', 'ARAÇ GİRİŞİ', 'SERVİS GİRİŞİ', 'BAHÇE GİRİŞİ') names a secondary entrance, never the main one (GENERAL-9).
  A main entrance never goes to a garage door (the user's C0045: a car drives in, no steps), nor into a bedroom, a
  kitchen or a wet room (``core_rules.NOT_MAIN_TYPES``). A word-named door the terrain stands at most ``GROUND_TOL_M`` over is a flush entrance (the
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
MARK_REACH_M = 2.5              # a ground or threshold mark this far out in front of the gap marks an entrance ...
MARK_SIDE_M = 0.5               # ... at most half the gap's width plus this along the facade (ENTRANCES-1)
STEP_MIN_M = 0.10               # ... at least a step (a riser) under the floor (a mark at the floor says flush)
STEP_REACH_M = 2.0              # a stair run in the band this far out in front of the gap's face is its steps
DROP_MAX_M = 1.2                # the gap's floor at most this over the ground (a few steps; levels.model's limit)
GAP_W_M = (0.8, 4.0)            # a passage's width
WORD_REACH_M = 2.0              # an entrance word names the nearest outside door this close
GROUND_TOL_M = 0.20             # a word-named door this far under the terrain is a flush entrance (ground lowered)
PORCH_NAME = "Giriş"
GROUND_KINDS = ("ground_finished", "ground", "ground_natural", "threshold")
WINDOW_CONTENT_RULES = ("no_glass", "framed_window", "glazed_facade", "sliding_window", "window_block", "size_tag")
PORCH_WORD_RE = re.compile(r"(?<![a-z])(?:sundurma|portik|porch|giris\s+sacagi)(?![a-z])")   # never 'ön giriş'
RECESS_TYPES = ("", "unknown", "other", "hall", "corridor", "entry")   # a recess is none of wet, storage, shaft ...
NO_ENTRANCE_TYPES = ("bathroom", "wc", "shower", "toilet", "storage", "shaft", "technical", "stair")   # never entered
ENTRANCE_WORD_RE = re.compile(r"(?<![a-z])(?:(?:bina|apartman|daire|ana|ev|villa|konut)\s+)?giris(?:i|e)?(?![a-z])|"
                              r"(?<![a-z])(?:main\s+)?entrance(?![a-z])|(?<![a-z])(?:haus)?eingang(?![a-z])|"
                              r"(?<![a-z])entree(?![a-z])")
BUILDING_WORD_RE = re.compile(r"(?<![a-z])(?:bina|apartman|ana|villa|konut|main|haus)(?![a-z])")
SHOP_WORD_RE = re.compile(r"(?<![a-z])(?:dukkan|magaza|isyeri|ofis|shop|store|laden)(?![a-z])")
FLAT_WORD_RE = re.compile(r"(?<![a-z])daire(?![a-z])")
# 28 Nov 2026 (GENERAL-9, ENTRANCES-4): a vehicle, garage, service, garden or car-park entrance is never the main one
SIDE_WORD_RE = re.compile(r"(?<![a-z])(?:otopark|garaj|arac|oto|servis|bahce|yangin|acil|kazan|car|garage|parking|"
                          r"service|delivery|garden|emergency|fire|tiefgarage|garagen?)(?![a-z])")


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
    """A label of its own: drawn, or copied from a mirror twin (``label_inferred`` other than a role name; R08)."""
    li = room.get("label_inferred") if isinstance(room.get("label_inferred"), dict) else None
    return bool(room.get("label_raw")) or bool(room.get("label_inferred")) and not (li and li.get("method") == "role")


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


def entrance_levels(b: dict, texts_by_level: Optional[dict] = None) -> set:
    """The entrance level(s) (pure; 28 Nov 2026, R08 decision): a storey with an entrance word in its core, else the
    lowest base storey whose floor lies near a ground height the reading knows (``core_rules.entrance_storeys``), never
    an upper storey of a hillside house."""
    from wenart.ingest import core_rules as CR

    got = CR.entrance_storeys(b, texts_by_level)
    worded = {lv["id"] for lv, why in got if why.startswith("the entrance word")}
    if worded:
        return worded
    near = [lv for lv, _why in got if isinstance(lv.get("elevation"), (int, float))]
    return {min(near, key=lambda lv: float(lv["elevation"]))["id"]} if near else set()


def _terrain(b: dict, level, levels: list):
    """The terrain model as the levels model makes it (``blender.site.terrain_model``) around ``level``'s outline."""
    from wenart.blender import site as S

    if level.outline is None:
        return None
    geom = level.outline if level.outline.geom_type == "Polygon" else max(level.outline.geoms, key=lambda g: g.area)
    zs = [float(lv["elevation"]) for lv in levels if isinstance(lv.get("elevation"), (int, float))]
    default_z = 0.0 if not zs or min(zs) < 0 else min(zs)
    try:
        return S.terrain_model(b, [tuple(p[:2]) for p in geom.exterior.coords], default_z)
    except Exception:  # noqa: BLE001 - no terrain model: the marks and the steps decide alone
        return None


def _blocked(level, o: dict, face, p) -> bool:
    """A wall or another opening between the gap's face and ``p`` (the mark is beyond another wall; GENERAL-3)."""
    from shapely.geometry import LineString

    seg = LineString([(face[0], face[1]), (float(p[0]), float(p[1]))])
    if seg.length < 0.05:
        return False
    start = Point(face).buffer(0.08)
    for w in level.walls.values():
        if w.get("id") == o.get("wall_id") or not w.get("start") or not w.get("end"):
            continue
        ln = LineString([tuple(w["start"][:2]), tuple(w["end"][:2])])
        hit = ln.buffer(float(w.get("thickness") or 0.1) / 2.0).intersection(seg)
        if not hit.is_empty and hit.difference(start).length > 0.02:
            return True
    return False


def _band(face, ow, along, width: float, depth: float):
    """The rectangle in front of a gap: its width along the facade, ``depth`` out from the face."""
    from shapely.geometry import Polygon

    h = width / 2.0
    pts = [(face[0] + along[0] * s * h + ow[0] * d, face[1] + along[1] * s * h + ow[1] * d)
           for s, d in ((-1, 0.0), (1, 0.0), (1, depth), (-1, depth))]
    return Polygon(pts)


def entrance_evidence(b: dict, level, lv: dict, o: dict, strokes: Optional[list] = None, tm=None) -> Optional[dict]:
    """What says the gap ``o`` is an open entrance (module docstring, (i)-(iii)) with the drop under its floor, or None
    (pure). ``{"room", "face", "outward", "drop", "ground_z", "reasons": [...], "marks": [...], "drawn": bool}``. The
    recess test is made per room by ``open_porches`` (``_recess``)."""
    from wenart.blender import site as S
    from wenart.ingest import completion as CP
    from wenart.levels import model as LM

    width = float(o.get("width") or 0.0)
    if not _seen_as_gap(o) or not GAP_W_M[0] <= width <= GAP_W_M[1]:
        return None
    got = _outside_face(level, o)
    if got is None or got[2] is None:
        return None
    face, ow, room = got
    if LM._open_air(room) or str(room.get("room_type") or "") in CP.OPEN_AIR or S.room_role(room) == "garage" \
            or LM.is_garage_door(o, room) or str(room.get("room_type") or "") in NO_ENTRANCE_TYPES:
        return None                  # a balcony's or terrace's open edge, a garage's bay, a WC: no porch, no door
    z = lv.get("elevation")
    if not isinstance(z, (int, float)):
        return None
    floor = float(z)
    along = (-ow[1], ow[0])
    reasons, mark_z = [], None
    for m in b.get("level_marks") or []:
        if m.get("level_id") not in (None, lv["id"]) or not m.get("point") or m.get("door_id") \
                or m.get("kind") not in GROUND_KINDS or not isinstance(m.get("z"), (int, float)):
            continue
        dx, dy = float(m["point"][0]) - face[0], float(m["point"][1]) - face[1]
        out_d, lat = dx * ow[0] + dy * ow[1], abs(dx * along[0] + dy * along[1])
        drop = floor - float(m["z"])
        # R08 decision: in front of the gap (outside, on its side), at least a step under the floor, no wall between
        if not (0.0 < out_d <= MARK_REACH_M and lat <= width / 2.0 + MARK_SIDE_M
                and STEP_MIN_M - 1e-9 <= drop <= DROP_MAX_M):
            continue
        if level.outline is not None and level.outline.buffer(-0.02).contains(Point(m["point"][:2])):
            continue
        if _blocked(level, o, face, m["point"]):
            continue
        d = math.hypot(dx, dy)
        if mark_z is None or d < mark_z[1]:
            mark_z = (float(m["z"]), d, m)
    if mark_z is not None:
        reasons.append(f"the level mark {mark_z[2].get('raw') or mark_z[2].get('id')} {mark_z[1]:.2f} m in front of "
                       f"it, {floor - mark_z[0]:.2f} m under its floor")
    band = _band(face, ow, along, width, STEP_REACH_M)
    steps = False
    for run in strokes or []:
        poly = run.get("polygon")
        if poly is None or poly.is_empty or not poly.intersects(band):
            continue
        c = poly.centroid
        if (c.x - face[0]) * ow[0] + (c.y - face[1]) * ow[1] <= 0.05:
            continue                  # ENTRANCES-7: the run lies in front of the gap, outside its face
        if level.outline is not None and level.outline.contains(c):
            continue
        reasons.append(f"steps drawn in front of it ({poly.distance(Point(face)):.2f} m out)")
        steps = True
        break
    if mark_z is not None:
        gz, src = mark_z[0], f"the level mark {mark_z[2].get('raw') or mark_z[2].get('id')}"
    else:
        gz, src = None, None
        if tm is not None:
            probe = (face[0] + ow[0] * 0.5, face[1] + ow[1] * 0.5)
            try:
                g = float(S.ground_z(tm, *probe))
            except Exception:  # noqa: BLE001 - no terrain at the probe
                g = None
            if g is not None and STEP_MIN_M - 1e-9 <= floor - g <= DROP_MAX_M:
                gz, src = g, "the terrain at its face"
    if gz is None:
        if not PORCH_WORD_RE.search(_fold(room.get("label"))):
            return None              # ENTRANCES-8: no ground a few steps under the floor at this gap
        gz, src = floor, "no ground read: at the floor (assumed)"
    return {"room": room, "face": face, "outward": ow, "drop": round(max(0.0, floor - gz), 3), "ground_z": gz,
            "ground_source": src, "reasons": reasons, "mark": mark_z[2] if mark_z else None,
            "drawn": bool(mark_z is not None or steps), "opening": o}


def _recess(b: dict, level, room: dict, mouths: list) -> Optional[str]:
    """Why ``room`` behind its open mouths is a covered porch (R08 decision), or None: a porch word in its label and no
    window; or a small recess (under ``PORCH_MAX_M2``) with no label of its own (drawn or copied), of no wet, storage,
    shaft or service type, holding no fixture or furniture, whose other openings are doors only, and a mark or steps in
    front of a mouth."""
    ids = {o["id"] for o in mouths}
    others = [x for x in _room_openings(level, room, None) if x["id"] not in ids]
    if any(x.get("type") == "window" for x in others):
        return None
    doors = [x for x in others if x.get("type") == "door"]
    if PORCH_WORD_RE.search(_fold(room.get("label"))) and doors:
        return f"its label '{room.get('label')}' names a porch and its other openings are doors"
    if _labelled(room) or str(room.get("room_type") or "") not in RECESS_TYPES or _area(room) >= PORCH_MAX_M2:
        return None
    if not doors or len(doors) != len(others):
        return None
    if any(f.get("room_id") == room["id"] and f.get("build") is not False for f in b.get("furniture") or []):
        return None                  # ENTRANCES-2: a room with fixtures or furniture is a room, never a porch
    return (f"behind it a {_area(room):.1f} m² recess with no label of its own, no fixture or furniture, whose only "
            f"other opening(s) are door(s) ({', '.join(x['id'] for x in doors)})")


def _entrance(b: dict, level, lv: dict, door: dict, hall: dict, why: str, ev: Optional[dict] = None) -> Optional[dict]:
    """A ``site.entrances`` record for ``door`` out of ``hall`` (``core_rules._entrance_record``, the ground of the
    evidence: the mark or the terrain at the gap), replacing any it had; ``drawn`` only when a mark or steps are drawn
    (ENTRANCES-11)."""
    from wenart.ingest import core_rules as CR

    sides = _sides(level, door)
    if len(sides) != 2 or door.get("wall_id") not in level.walls:
        return None
    side = 1 if (sides[0][1] or {}).get("id") == hall["id"] else -1
    ground = (float(ev["ground_z"]), ev["ground_source"]) if ev and ev.get("ground_source") else None
    ent = CR._entrance_record(b, door, level, lv, hall, {"wall_id": door["wall_id"], "side": side}, why,
                              ground=ground)
    ent["drawn"] = bool(ev and ev.get("drawn"))
    site = b.setdefault("site", {})
    site["entrances"] = [e for e in site.get("entrances") or [] if e.get("door_id") != door["id"]] + [ent]
    return ent


def _main_now(b: dict) -> Optional[dict]:
    return next((e for e in (b.get("site") or {}).get("entrances") or [] if e.get("main")), None)


def _takes_main(b: dict, ent: dict) -> bool:
    """The porch's door becomes the main entrance (R08 decision: one main entrance, never the drawn one lost): when
    the building has none, or when its main entrance is no entrance the documents name (an entrance word on its door,
    a mark naming it: ``levels.model.main_tier`` 0) and ranks no better than the porch's door by the levels model's own
    ``main_tier`` (a door into a hall before a door into a room before a garden door)."""
    from wenart.levels import model as LM

    cur = _main_now(b)
    if cur is None:
        return True
    ops = {o.get("id"): o for o in b.get("openings") or []}
    rooms = {r.get("id"): r for r in b.get("rooms") or []}
    door = ops.get(cur.get("door_id")) or {}
    if door.get("entrance_word") or door.get("entrance_of") == "building" \
            or "marked as the entrance in the documents" in str(cur.get("main_reason") or ""):
        return False                     # the documents name the main entrance: it stays
    try:
        t_cur = LM.main_tier(cur, door, rooms.get(cur.get("room_id")), False)[0]
        t_new = LM.main_tier(ent, ops.get(ent.get("door_id")), rooms.get(ent.get("room_id")), False)[0]
    except Exception:  # noqa: BLE001 - a record the tiers cannot read: the main entrance stays
        return False
    return t_new <= t_cur


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


def open_porches(b: dict, strokes_by_level: Optional[dict] = None, warn: Optional[Callable] = None,
                 texts_by_level: Optional[dict] = None) -> list[dict]:
    """The open entrances and porches (module docstring), in place; one record per gap changed. Only on the entrance
    level (``entrance_levels``); the evidence of every gap of a level is read first, each mark used once (by its
    nearest gap), then each room decides once (a corner porch with two mouths is one porch: ENTRANCES-10)."""
    from wenart.ingest import completion as CP
    from wenart.ingest import rule_guards as RG

    out: list[dict] = []
    entry = entrance_levels(b, texts_by_level)
    levels = [lv for lv in b.get("levels") or [] if not lv.get("base_level_id")]
    for lv in levels:
        lid = lv["id"]
        if lid not in entry or not isinstance(lv.get("elevation"), (int, float)):
            continue
        level = CP.Level(b, lid)
        if level.outline is None:
            continue
        tm = _terrain(b, level, levels)
        evs = [ev for o in list(level.openings)
               for ev in [entrance_evidence(b, level, lv, o, (strokes_by_level or {}).get(lid), tm)] if ev is not None]
        # each mark serves its nearest gap only (ENTRANCES-1)
        best: dict = {}
        for ev in evs:
            m = ev.get("mark")
            if m is not None:
                d = math.dist(m["point"][:2], ev["face"])
                k = id(m)
                if k not in best or d < best[k][0]:
                    best[k] = (d, ev["opening"]["id"])
        kept = []
        for ev in evs:
            m = ev.get("mark")
            if m is not None and best[id(m)][1] != ev["opening"]["id"]:
                ev = dict(ev, mark=None, reasons=[r for r in ev["reasons"] if not r.startswith("the level mark")])
                if not ev["reasons"] and not PORCH_WORD_RE.search(_fold(ev["room"].get("label"))):
                    continue
            kept.append(ev)
        by_room: dict = {}
        for ev in kept:
            by_room.setdefault(ev["room"]["id"], []).append(ev)
        for rid, group in sorted(by_room.items()):
            room = group[0]["room"]
            mouths = [ev["opening"] for ev in group]
            recess = _recess(b, level, room, mouths)
            if recess is None and not any(ev["drawn"] for ev in group):
                continue                 # no mark or steps in front, no porch: nothing to read
            if recess is not None and not any(ev["drawn"] for ev in group) \
                    and not PORCH_WORD_RE.search(_fold(room.get("label"))):
                continue                 # ENTRANCES-2: a recess needs a mark or steps in front of it
            out += _decide(b, level, lv, room, group, recess, warn, RG)
    return out


def _decide(b: dict, level, lv: dict, room: dict, group: list, recess: Optional[str], warn, RG) -> list[dict]:
    out = []
    lid = lv["id"]
    for ev in group:
        o = ev["opening"]
        reasons = list(ev["reasons"]) + ([recess] if recess else [])
        why = (f"{o['id']} ({float(o.get('width') or 0):.2f} m) is a gap in the outer wall at the floor of "
               f"{room['id']}, {ev['drop']:.2f} m over the ground ({ev['ground_z']:+.2f} m, {ev['ground_source']}): "
               + "; ".join(reasons))
        item = {"level_id": lid, "opening": o["id"], "room": room["id"], "why": why}
        if (RG.blocked("open_porch", b, item) if recess else RG.blocked("facade_gap_entrance", b, item)):
            continue
        if o.get("type") == "window":
            for k in ("sill_height", "height"):
                if "drawn_" + k in o:
                    o[k] = o.get("drawn_" + k)
            for k in ("guard", "french_window", "sill_height_source"):
                o.pop(k, None)
        o["drawn_type"] = "opening"
        if recess:
            why += f": an open entrance porch, {o['id']} its open mouth (R08)"
            o["type"], o["sill_height"] = "opening", None
            o["type_inferred"] = {"method": "open_porch", "reason": why}
            out.append({"opening": o["id"], "level_id": lid, "porch": room["id"], "reason": why})
        else:
            why += ": an entrance door (R08)"
            o["type"], o["sill_height"] = "door", None
            if o.get("height") is None:
                o["height"] = 2.1
            o["type_inferred"] = {"method": "facade_gap_entrance", "reason": why}
            _entrance(b, level, lv, o, room, why, ev)
            out.append({"opening": o["id"], "level_id": lid, "door": o["id"], "reason": why})
        if warn:
            warn(f"entrances: {why}")
    if not recess or not out:
        return out
    before = {"room_type": room.get("room_type"), "label": room.get("label")}
    why = out[0]["reason"]
    room["room_type"] = "porch"
    room["covered"] = True
    if not _labelled(room):
        room["label"] = PORCH_NAME
        room["label_role"] = True
        room["label_inferred"] = {"method": "role", "role": "porch", "reason": "an unlabelled open porch (R08, R28)"}
    room["adjusted_by_ai"] = {"by": "code", "rule": "open_porch", "reason": why, "changed": before}
    mouths = {ev["opening"]["id"] for ev in group}
    doors = [x for x in _room_openings(level, room, None) if x.get("type") == "door" and x["id"] not in mouths]
    ev0 = next((ev for ev in group if ev["drawn"]), group[0])
    for d in doors:
        s = _sides(level, d)
        hall = next((x[1] for x in s if x[1] is not None and x[1]["id"] != room["id"]), None)
        if hall is None:
            continue
        ent = _entrance(b, level, lv, d, hall, f"{d['id']} opens from {hall['id']} onto the open porch {room['id']}; "
                                              + why, ev0)
        if ent is not None and len(doors) == 1 and _takes_main(b, ent) and not RG.blocked(
                "entrance_word_main", b, {"level_id": lid, "opening": d["id"], "why": why}):
            _set_main(b, ent, f"{d['id']}, the door in the open porch {room['id']} (drawn "
                              f"{'; '.join(ev0['reasons']) or 'its porch label'}): the building entrance (R08, inferred)")
    return out


def _word_kind(text: str) -> Optional[str]:
    f = _fold(text)
    if not ENTRANCE_WORD_RE.search(f) or re.search(r"(?<![a-z])giris\s+(?:holu|hol|kat|katı|kati)(?![a-z])", f):
        return None                         # 'GİRİŞ HOLÜ' / 'GİRİŞ KATI' name a room or a storey
    if SHOP_WORD_RE.search(f):
        return "shop"
    if SIDE_WORD_RE.search(f):
        return "side"                       # GENERAL-9: a secondary entrance, never the main one
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
    if not ENTRANCE_WORD_RE.search(f) or BUILDING_WORD_RE.search(f) or SHOP_WORD_RE.search(f) \
            or FLAT_WORD_RE.search(f) or SIDE_WORD_RE.search(f):
        return text
    best = None
    for x in texts or []:
        if x is t or x.get("x") is None:
            continue
        g = _fold(x.get("text"))
        if len(g.split()) > 2 or not (BUILDING_WORD_RE.search(g) or SHOP_WORD_RE.search(g) or FLAT_WORD_RE.search(g)
                                      or SIDE_WORD_RE.search(g)):
            continue
        d = math.hypot(float(x["x"]) - float(t["x"]), float(x["y"]) - float(t["y"]))
        if d <= QUALIFIER_REACH_M and (best is None or d < best[0]):
            best = (d, str(x.get("text") or ""))
    return f"{best[1]} {text}" if best else text


def entrance_words(b: dict, texts_by_level: Optional[dict], warn: Optional[Callable] = None) -> list[dict]:
    """The entrance words outside the walls (module docstring), in place; one record per word bound to a door."""
    from wenart.ingest import completion as CP
    from wenart.ingest import core_rules as CR
    from wenart.ingest import rule_guards as RG
    from wenart.levels import model as LM

    out: list[dict] = []
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    ents = {e.get("door_id"): e for e in (b.get("site") or {}).get("entrances") or []}
    rooms = {r.get("id"): r for r in b.get("rooms") or []}
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
            o["entrance_of"] = {"shop": "shop", "flat": "flat", "side": "side"}.get(kind, "building")
            rec = {"opening": oid, "level_id": lid, "word": o["entrance_word"]["text"], "kind": kind}
            e = ents.get(oid)
            room = rooms.get((e or {}).get("room_id"))
            # ENTRANCES-4: the room-type rules fix_entrances has run already, asked again: never a garage door (C0045:
            # its drive stays), never into a bedroom, a kitchen or a wet room
            bad = e is not None and (e.get("solution") == "drive" or LM.is_garage_door(o, room)
                                     or str((room or {}).get("room_type") or "") in CR.NOT_MAIN_TYPES)
            if bad:
                rec["not_main"] = "a garage door or a door into a room that is never the building's entrance"
            if e is not None and kind in ("building", "entrance") and not e.get("into_air") \
                    and not e.get("upper_floor") and not bad:
                if e.get("below_ground") and -float(e.get("rise") or 0.0) <= GROUND_TOL_M + 1e-9 and \
                        float(e.get("ground_z") or 0.0) - float(e.get("threshold_z") or 0.0) <= GROUND_TOL_M + 1e-9:
                    e["below_ground"], e["terrain_lowered"] = False, True
                    e["reason"] = (f"{e.get('reason') or ''}; the entrance word '{o['entrance_word']['text']}' names "
                                   f"it: the ground in front is lowered to its threshold (a flush entrance, R08)")
                if not e.get("below_ground") and not (_word_main(b) and kind == "entrance") and not RG.blocked(
                        "entrance_word_main", b, {"level_id": lid, "opening": oid, "why": o["entrance_word"]["text"]}):
                    _set_main(b, e, f"{oid}, named '{o['entrance_word']['text']}' outside the walls {d:.2f} m from "
                                    f"it: the building entrance (R08, drawn)")
                    rec["main"] = True
            out.append(rec)
            if warn:
                warn(f"entrances: the word '{o['entrance_word']['text']}' outside the walls names {oid} "
                     f"({kind} entrance){' : the main entrance' if rec.get('main') else ''}")
    return out
