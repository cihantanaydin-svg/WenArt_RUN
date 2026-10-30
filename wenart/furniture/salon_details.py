"""The P16 living-dining room as general rules by style family (30 Oct 2026; user, sending photo P16: "salon
inspiration"; lesson UL153; docs/reference_details_20261029.md rows R39-R49).

What the runs had (real04 run 20261029-201533-full, r_L-1_salon): the TV stood on a library unit on legs beside a big
colourful print, nothing beside it; the 3.35 m dining table had a 1.4 m print over it (0.42 of its length) and four
wood dome pendants; a plain cream vase in its middle; a rug under the dining set only (the AI's), none under the
sofa group; a square coffee table between two armchairs; no wall decor but prints and a mirror.

What P16 shows (a modern-warm living-dining room) and what this module makes of it, each a general rule of the families
in its table, each item ``source: added_by_ai``, ``method: rule``, ``rule: salon_details.<what>`` with its reason (the
way the pipeline records inferred design details), each floor item through the placer's checks (inside the room, no
overlap, the front clearances, door swings and approaches free, windows free, no walkway it blocks), each wall item off
doors, windows, panelled walls and the other wall items; nothing drawn moves:

1. The TV wall set (R45):
   - ``console_form``: a low TV unit (top at most ``CONSOLE_MAX_TOP_M``, at least ``CONSOLE_MIN_W_M`` long) whose back
     stands on a wall becomes a floating wood console with a black fluted strip (``form: floating``, our parametric
     product by design, ``wenart.blender.salon_parts.floating_console``; its footprint, place and top as before: the
     look only); a free-standing divider or a tall media unit stays as it is.
   - ``tv_niches``: on each side of that unit, ``NICHE_GAP_M`` off it, a tall narrow black-lined lit niche with books
     and vases (a ``wall_niche`` with ``niche.style: tv_side``), where the wall has room (a free wall stretch, the floor
     in front free); both sides take the same width when both fit.
2. The dining set (R40-R43):
   - ``dining_art_width``: the art on the dining wall is about 2/3 of the table's length (``ART_SHARE``), at most
     ``ART_MAX_W_M`` and ``ART_STRETCH_SHARE`` of its free wall stretch, up to ``ART_MAX_H_M`` high (every family:
     a designer's proportion; ``room_details.dining_wall`` uses it).
   - ``dining_light``: the room's row of pendants over its dining table becomes one fixture: black mini pendants on a
     black surface track over the table where the room's scheme has track lights (``fixture: track_pendants``, the
     pendants where the row hung), or a slim black linear pendant about 2/3 of the table's length where its scheme's
     statement is linear (``fixture: linear_pendant``); the row's bottom height is kept; the row's items leave
     (``decor_dropped``); the lights plan counts the fixture as the whole row (``ceiling_lights.ROW_FIXTURES``).
   - ``dining_rug``: a rug under the dining set (the table + ``decor.DINING_CHAIR_M`` on each side for the chairs; cut
     off walls, door swings, fixed pieces and the other rugs: ``decor._rug_item``) where none lies under the table
     (every family; ``fringe: true`` in the P16 families).
   - ``centrepiece``: the dining table's centre item becomes a centrepiece set: a glass vase with dried pampas grass,
     two concrete candle holders, a low bowl (a ``vase`` with ``set: centrepiece``), along the table, between the place
     settings, under the pendants.
3. ``panel_wall`` (R39): on a free wall of the dining zone (within ``PANEL_REACH_M`` of the dining table, not the TV
   wall, not behind the chairs), full-height handle-less flat panels with an inset black-lined lit niche
   (``panel_wall``), ``PANEL_D_M`` deep, as many ``PANEL_MODULE_M`` fronts as the stretch holds (at least
   ``PANEL_MIN_MODULES``), their doors' clearance free (the placer's wardrobe check); not under a sloped ceiling.
4. The seating corner (R47, R48, R44):
   - ``drum_tables``: a near-square coffee table (sides ``DRUM_MIN_M``-``DRUM_MAX_M``, at most ``DRUM_ASPECT`` long for
     its width) becomes a round travertine drum (``form: drum``, by design; its items moved onto the round top); the
     scheme's glass preference stays on the rectangular ones.
   - ``round_rug``: a round rug with concentric stripes (``shape: round``, ``pattern: rings``) under a drum table where
     none lies, its diameter the table's plus ``ROUND_RUG_REACH_M`` on each side (reaching the chairs' front legs)
     down to ``+ ROUND_RUG_MIN_REACH_M``, inside the room shrunk by ``decor.RUG_ROOM_INSET_M``, off door swings, fixed
     pieces and the other rugs.
   - ``seating_rug``: every living room's sofa group (a sofa and the coffee table in front of it) stands on a rug where
     none lies under its table (every family; the AI's decor had left real04's salon without one).
   - ``wall_discs``: two black round wall discs on a free wall stretch (nothing taller than 1 m in front), their bottom
     ``DISC_BOTTOM_M`` up or over a low piece.

Not built here (and why): the slat column by the passage (R46: which opening is "the passage" needs the walking
routes, not yet a rule), boucle on the accent armchairs (R47: the library holds no boucle armchair and the sofas'
fabrics are another helper's), the dining rug's fringe on a library rug (a parametric rug has it; a fitted model keeps
its own edge), the black frame and line-art of the dining print (the fit picks the art model from the library).

``review`` (model review M34, Argus U38) flags a living or dining room that misses what its family takes: a sofa group
or a dining set with no rug under it, a dining print under half the table's length, a row of loose pendants where the
scheme asks one fixture, a dining table without its centrepiece, a low wall-backed TV unit not floating, a TV wall
without its niches with no recorded reason, a near-square coffee table not a drum (minor; kind ``taste``).

Why: the user's photo P16 ("salon inspiration"); the renders' living-dining rooms read as furniture placed in a room,
not as a designed room.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G

RULE = "salon_details"
LESSON = "UL153"
REVIEW_CHECKS: tuple[str, ...] = ("M34", "U38")
TAG = "30 Oct 2026, photo P16, user: \"salon inspiration\""
# The families of each detail (designer tables; P16 is a modern-warm room: modern, contemporary, minimal, japandi,
# scandinavian homes)
SALON_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "japandi", "scandinavian")
CONSOLE_FAMILIES = SALON_FAMILIES                                                # R45
TV_NICHE_FAMILIES = SALON_FAMILIES                                               # R45
PANEL_WALL_FAMILIES = SALON_FAMILIES                                             # R39
LINEAR_DINING_FAMILIES = SALON_FAMILIES + ("industrial",)                        # R42 (a linear statement)
CENTREPIECE_FAMILIES: tuple[str, ...] = SALON_FAMILIES + ("mediterranean", "rustic")      # R43 (pampas)
DRUM_TABLE_FAMILIES = SALON_FAMILIES + ("mediterranean",)                        # R48 (travertine)
RING_RUG_FAMILIES = SALON_FAMILIES                                               # R48
WALL_DISC_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "japandi")   # R44
FRINGE_FAMILIES = SALON_FAMILIES                                                 # R41
ROOM_TYPES: tuple[str, ...] = ("living", "dining")
# sizes of real products and designer proportions (assumed)
CONSOLE_MAX_TOP_M = 0.65          # a TV unit this low or lower floats (a taller one is a media cabinet)
CONSOLE_MIN_W_M = 1.0
NICHE_WIDTHS: tuple[float, ...] = (0.60, 0.50, 0.45, 0.40)
NICHE_D_M = 0.30
NICHE_GAP_M = 0.12                # the niche this far from the unit's end (or the TV's, when wider)
NICHE_GAP_MAX_M = 0.40            # ... and at most this far (beside the TV, not across the room)
NICHE_MAX_H_M = 2.40
NICHE_MIN_H_M = 1.80
NICHE_CEILING_GAP_M = 0.12
ART_SHARE = 2.0 / 3.0             # R40: the art over a dining table about 2/3 of its length
ART_MIN_W_M = 0.9
ART_MAX_W_M = 2.0
ART_STRETCH_SHARE = 0.8
ART_MAX_H_M = 1.6
ART_SMALL_SHARE = 0.5             # the review: a dining print narrower than this share of the table is small
LINEAR_MIN_M, LINEAR_MAX_M = 0.9, 1.8
LINEAR_D_M = 0.08
TRACK_D_M = 0.12
TRACK_END_M = 0.25                # the track runs this far past the outer pendants
PENDANT_OVER_TOP_M = 0.75         # = ceiling_lights.PENDANT_OVER_TOP_M
MIN_DROP_M = 0.30                 # = ceiling_lights.PENDANT_MIN_DROP_M
ROW_REACH_M = 0.2                 # = ceiling_lights.ROW_MATCH_M: a light over the table grown by this is of its row
CENTRE_TYPES: tuple[str, ...] = ("vase", "bowl", "candle", "plant_small", "fruit_bowl", "sculpture")
CENTRE_REACH_M = 0.30             # an item this close to the table's centre is its centre item
CENTRE_W_M = 0.60                 # the set along the table (= decor.MAX_DECOR_M)
CENTRE_W_SHARE = 0.35
CENTRE_DEPTHS: tuple[float, ...] = (0.26, 0.24, 0.22, 0.20, 0.18, 0.16)
CENTRE_MAX_H_M = 0.55
CENTRE_MIN_H_M = 0.30
CENTRE_MIN_TABLE_M = 1.2          # a smaller table keeps its one centre item
CENTRE_UNDER_LIGHT_M = 0.12       # the pampas tips this far under a pendant over the table
PANEL_D_M = 0.40
PANEL_MODULE_M = 0.55
PANEL_MIN_MODULES = 3
PANEL_MAX_W_M = 3.3
PANEL_REACH_M = 2.0               # a stretch whose middle is this close to the dining table's footprint is its wall
PANEL_FRONT_M = 0.9               # nothing within this of the wall (the doors open, the chairs pull out)
DRUM_MIN_M, DRUM_MAX_M = 0.55, 1.2
DRUM_ASPECT = 1.25
ROUND_RUG_REACH_M = 0.6
ROUND_RUG_MIN_REACH_M = 0.3
ROUND_RUG_MAX_M = 2.4
ROUND_RUG_STEP_M = 0.1
ROUND_RUG_SHIFT_M = 0.25          # a round rug may sit this far off its table's centre (off a wall or a door swing)
ROUND_RUG_SHIFT_STEP_M = 0.05
ARMCHAIR_REACH_M = 1.3            # an armchair this close to a drum table is of its group (the round rug's anchors)
DISC_SIZE = (0.85, 0.04, 0.72)    # two discs, 0.51 m and 0.32 m across, offset (R44)
DISC_BOTTOM_M = 1.25
DISC_OVER_LOW_M = 0.30
DISC_CEILING_GAP_M = 0.25


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if r.get("id")}


def _pieces(building: dict, room_id: str, types=None) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and f.get("footprint")
            and f.get("build", True) is not False and (types is None or f.get("type") in types)]


def _decor(building: dict, room_id: str, types=None) -> list[dict]:
    return [d for d in building.get("decor") or [] if d.get("room_id") == room_id
            and (types is None or d.get("type") in types)]


def _size(piece: dict) -> tuple[float, float]:
    return float(piece["footprint"]["size"][0]), float(piece["footprint"]["size"][1])


def _centre(piece: dict) -> tuple[float, float]:
    return float(piece["footprint"]["center"][0]), float(piece["footprint"]["center"][1])


def _rot(piece: dict) -> float:
    return float(piece["footprint"].get("rotation_deg") or 0.0)


def _long_axis(piece: dict) -> tuple[tuple[float, float], float, float]:
    """``(unit vector, length, rotation)`` of a piece's long axis (the rotation that turns local +X onto it)."""
    w, d = _size(piece)
    rot = _rot(piece)
    if d > w:
        rot += 90.0
    rad = math.radians(rot)
    return (math.cos(rad), math.sin(rad)), max(w, d), round(G.normalise_angle(rot), 3)


def _rect(piece_or_item: dict, grow: float = 0.0) -> list[tuple[float, float]]:
    fp = piece_or_item.get("footprint") or piece_or_item
    size = [float(v) + 2.0 * grow for v in fp["size"][:2]]
    return G.rotated_rectangle(tuple(float(v) for v in fp["center"][:2]), size,
                               float(fp.get("rotation_deg") or 0.0))


def _covers(item: dict, point) -> bool:
    """A decor item's plan box (a round rug: its circle) covers ``point``."""
    if item.get("shape") == "round":
        r = min(float(v) for v in item["size"][:2]) / 2.0
        return G.distance(tuple(float(v) for v in item["center"][:2]), tuple(point[:2])) <= r + 1e-9
    return G.point_in_polygon(tuple(point[:2]), _rect({"center": item["center"], "size": item["size"],
                                                        "rotation_deg": item.get("rotation_deg") or 0.0}))


def rug_under(building: dict, room_id: str, point, ids=()) -> Optional[dict]:
    """The room's rug under ``point`` (or one anchored to a piece of ``ids``), None without one."""
    for d in _decor(building, room_id, ("rug",)):
        if not d.get("center") or not d.get("size"):
            continue
        if _covers(d, point) or set(ids) & set(d.get("anchor_ids") or []):
            return d
    return None


def _family(building: dict, style: Optional[dict] = None) -> str:
    if style and style.get("family"):
        return str(style["family"]).lower()
    for key in ("salon_details", "room_schemes"):
        fam = (building.get(key) or {}).get("family")
        if fam:
            return str(fam).lower()
    return ""


def _record(building: dict, rid: str, detail: str, done: bool, why: str, ids=()) -> str:
    rec = building.setdefault("salon_details", {"rule": RULE, "lesson": LESSON, "rooms": {}})
    rec.setdefault("rooms", {}).setdefault(rid, {})[detail] = {"done": bool(done), "why": why, "ids": list(ids)}
    return f"{detail.replace('_', ' ')}: {why}" if not done else why


def _evidence(text: str) -> list[dict]:
    return [{"file": "building.json", "method": "inferred", "rule": RULE, "confidence": 0.7, "text": text}]


def _item(room: dict, dtype: str, what: str, reason: str, centre, size, rotation: float, **extra) -> dict:
    """A rule item of this module (without its id)."""
    why = f"{reason} ({TAG})"
    out = {"kind": "decor", "type": dtype, "level_id": room["level_id"], "room_id": room["id"], "asset": None,
           "host_id": None, "source": "added_by_ai", "method": "rule", "rule": f"{RULE}.{what}",
           "slot": f"{room['id']}.{what}", "colour": None, "confidence": 0.7, "status": "verified",
           "center": [round(float(v), 3) for v in centre], "rotation_deg": round(float(rotation), 3),
           "size": [round(float(v), 3) for v in size], "evidence": _evidence(why), "reason": why}
    out.update({k: v for k, v in extra.items() if v is not None})
    return out


def _add(building: dict, item: dict, new_id: Callable) -> dict:
    item["id"] = new_id(item["level_id"])
    building.setdefault("decor", []).append(item)
    return item


def _top(piece: dict) -> float:
    from wenart.furniture import room_details as RD

    return RD._top(piece)


def _span_on(seg, piece_or_box) -> tuple[float, float]:
    """The span ``(s0, s1)`` of a piece's plan box along a wall segment ``(a, u)``."""
    a, u = seg
    pts = _rect(piece_or_box)
    s = [(x - a[0]) * u[0] + (y - a[1]) * u[1] for x, y in pts]
    return min(s), max(s)


def _tv_units(rc) -> list[dict]:
    return sorted((f for f in rc.pieces if f.get("type") == "tv_unit"),
                  key=lambda f: (-max(_size(f)), str(f["id"])))


def _dining_table(rc) -> Optional[dict]:
    tables = [f for f in rc.pieces if f.get("type") == "table_dining"]
    return max(tables, key=lambda f: (_size(f)[0] * _size(f)[1], str(f["id"]))) if tables else None


# --------------------------------------------------------------------------
# 1. the TV wall set (R45)
# --------------------------------------------------------------------------

def console_form(building: dict, rc, sc: dict, fam: str) -> list[str]:
    """R45: a low wall-backed TV unit becomes a floating console (module docstring, 1)."""
    from wenart.furniture import room_details as RD

    room = rc.room
    if room.get("room_type") not in ROOM_TYPES:
        return []
    if fam not in CONSOLE_FAMILIES:
        return [_record(building, room["id"], "tv_console", False, f"a {fam or 'unknown'} home keeps its TV unit")] \
            if _tv_units(rc) else []
    out = []
    for unit in _tv_units(rc):
        if unit.get("form"):
            continue
        rule = unit.get("rule") if isinstance(unit.get("rule"), dict) else {}
        if rule.get("free"):
            out.append(_record(building, room["id"], "tv_console", False,
                               f"{unit['id']} stands free as a room divider: it stays on its feet"))
            continue
        if RD._wall_behind(unit, rc) is None:
            out.append(_record(building, room["id"], "tv_console", False, f"{unit['id']} has no wall behind it"))
            continue
        top = _top(unit)
        if top > CONSOLE_MAX_TOP_M + 1e-9 or max(_size(unit)) < CONSOLE_MIN_W_M - 1e-9:
            out.append(_record(building, room["id"], "tv_console", False,
                               f"{unit['id']} ({max(_size(unit)):.2f} m long, {top:.2f} m high) is no low console: "
                               f"it stays standing"))
            continue
        unit["form"] = "floating"
        unit["form_why"] = (f"P16 (R45): the TV unit as a low floating wood console with a black fluted strip, hung on "
                            f"its wall under its top (its footprint, place and top as before: the look only; {TAG})")
        out.append(_record(building, room["id"], "tv_console", True, f"{unit['id']} a floating console (R45)",
                           [unit["id"]]))
    return out


def _tv_span(building: dict, rc, unit: dict, seg) -> tuple[float, float]:
    """The span along the unit's wall of the unit and of its TV (a TV hung over it may be wider)."""
    s0, s1 = _span_on(seg, unit)
    for d in building.get("decor") or []:
        if d.get("type") != "tv" or not d.get("center") or not d.get("size"):
            continue
        if d.get("host_id") == unit["id"] or d.get("over_unit") == unit["id"]:
            t0, t1 = _span_on(seg, {"center": d["center"][:2], "size": d["size"][:2],
                                    "rotation_deg": d.get("rotation_deg") or 0.0})
            s0, s1 = min(s0, t0), max(s1, t1)
    return s0, s1


WALL_ART_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock")


def tv_wall_art(building: dict, rc, unit: dict) -> list[tuple[dict, float, float]]:
    """``[(item, s0, s1)]``: the pictures, mirrors and clocks hung on the TV unit's wall over the TV wall set's zone
    (the TV's span and ``NICHE_GAP_MAX_M`` + the widest niche on each side), with their span along the wall."""
    from wenart.furniture import room_details as RD

    found = RD._wall_behind(unit, rc)
    if found is None:
        return []
    a, _b, u, n, length = rc.segment(found[0])
    lo, hi = _tv_span(building, rc, unit, (a, u))
    reach = NICHE_GAP_MAX_M + max(NICHE_WIDTHS)
    out = []
    for d in rc.decor(WALL_ART_TYPES):
        p = d.get("wall_point") or d.get("center")
        if not p or d.get("host_id") or not d.get("size"):
            continue
        off = (float(p[0]) - a[0]) * n[0] + (float(p[1]) - a[1]) * n[1]
        s = (float(p[0]) - a[0]) * u[0] + (float(p[1]) - a[1]) * u[1]
        half = float(d["size"][0]) / 2.0
        if abs(off) > 0.15 or s + half < -0.05 or s - half > length + 0.05:
            continue
        if s + half > lo - reach and s - half < hi + reach:
            out.append((d, s - half, s + half))
    return out


def niche_spots(building: dict, rc, unit: dict, skip=()) -> tuple[dict, list[str]]:
    """``({side: (s0, width, stretch)}, notes)``: where a niche fits on each side (-1, +1) of a TV unit along its wall
    (pure planning: no item made); ``skip``: decor ids the wall's stretches ignore (the TV wall's pictures)."""
    from wenart.furniture import room_details as RD

    found = RD._wall_behind(unit, rc)
    if found is None:
        return {}, [f"{unit['id']} has no wall behind it"]
    i, _gap = found
    a, _b, u, n, _length = rc.segment(i)
    lo, hi = _tv_span(building, rc, unit, (a, u))
    stretches = [st for st in rc.stretches(min_len=NICHE_WIDTHS[-1], block_low=True, front_m=0.6, skip_ids=skip)
                 if st["i"] == i]
    rot = RD._rotation_into(n)
    spots, notes = {}, []
    for side in (-1, 1):
        got = None
        for w in NICHE_WIDTHS:
            for st in stretches:
                if side > 0:
                    s0 = max(hi + NICHE_GAP_M, st["s0"])
                    ok = s0 - hi <= NICHE_GAP_MAX_M + 1e-9 and s0 + w <= st["s1"] + 1e-9
                else:
                    s1 = min(lo - NICHE_GAP_M, st["s1"])
                    s0 = s1 - w
                    ok = lo - s1 <= NICHE_GAP_MAX_M + 1e-9 and s0 >= st["s0"] - 1e-9
                if not ok:
                    continue
                wp = rc.wall_point(st, s0 + w / 2.0)
                centre = (wp[0] + n[0] * (NICHE_D_M / 2.0 + 0.002), wp[1] + n[1] * (NICHE_D_M / 2.0 + 0.002))
                if rc.floor_failures("bookshelf", centre, rot, (w, NICHE_D_M), wall_n=n):
                    continue
                got = (s0, w, st)
                break
            if got is not None:
                break
        if got is None:
            notes.append(f"no niche on the {'right' if side > 0 else 'left'} of {unit['id']}: no free wall or floor "
                         f"beside it")
        else:
            spots[side] = got
    return spots, notes


def tv_niches(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R45: tall narrow black-lined lit niches beside the TV (module docstring, 1)."""
    from wenart.furniture import room_details as RD

    room = rc.room
    units = [u for u in _tv_units(rc) if not ((u.get("rule") if isinstance(u.get("rule"), dict) else {}).get("free"))]
    if room.get("room_type") not in ROOM_TYPES or not units:
        return []
    if fam not in TV_NICHE_FAMILIES:
        return [_record(building, room["id"], "tv_niches", False, f"a {fam or 'unknown'} home has no TV niches")]
    if any((d.get("niche") or {}).get("style") == "tv_side" for d in rc.decor(("wall_niche",))):
        return []
    unit = units[0]
    arts = tv_wall_art(building, rc, unit)
    spots, notes = niche_spots(building, rc, unit, skip={d.get("id") for d, _s0, _s1 in arts})
    if not spots:
        return [_record(building, room["id"], "tv_niches", False, "; ".join(notes))]
    width = min(w for _s0, w, _st in spots.values())
    made, spans = [], []
    for k, (side, (s0, w, st)) in enumerate(sorted(spots.items())):
        if side < 0:
            s0 = s0 + w - width                                 # the narrower width keeps its gap to the unit
        spans.append((s0, s0 + width))
        wp = rc.wall_point(st, s0 + width / 2.0)
        n = st["n"]
        centre = (wp[0] + n[0] * (NICHE_D_M / 2.0 + 0.002), wp[1] + n[1] * (NICHE_D_M / 2.0 + 0.002))
        rot = RD._rotation_into(n)
        ceiling = RD._sloped(building, room, centre, (width, NICHE_D_M), rot)
        h = round(min(NICHE_MAX_H_M, ceiling - NICHE_CEILING_GAP_M), 3)
        if h < NICHE_MIN_H_M:
            notes.append(f"no niche beside {unit['id']}: {ceiling:.2f} m of wall is too low")
            continue
        item = _item(room, "wall_niche", "tv_niche",
                     f"P16 (R45): a tall narrow black-lined lit niche {width:.2f} m wide, {h:.2f} m high on the "
                     f"{'right' if side > 0 else 'left'} of the TV unit {unit['id']}, books and vases on its boards",
                     (centre[0], centre[1], 0.0), (width, NICHE_D_M, h), rot,
                     wall_point=[round(wp[0], 3), round(wp[1], 3)], anchor_ids=[unit["id"]],
                     niche={"style": "tv_side", "shelves": max(3, min(5, int((h - 0.42) / 0.40))), "objects": True,
                            "base_m": 0.42, "seed": k})
        RD._toned(item, fam)
        made.append(_add(building, item, new_id)["id"])
    if not made:
        return [_record(building, room["id"], "tv_niches", False, "; ".join(notes))]
    # the TV wall stays plain (P16): a picture over the TV or where a niche stands leaves the wall (logged)
    found = RD._wall_behind(unit, rc)
    a, _b, u, _n, _length = rc.segment(found[0])
    lo, hi = _tv_span(building, rc, unit, (a, u))
    gone = []
    for d, s0, s1 in arts:
        if any(s1 > n0 - 0.1 and s0 < n1 + 0.1 for n0, n1 in spans + [(lo, hi)]):
            RD._drop(building, d, f"the TV wall stays plain: its lit niches {', '.join(made)} carry the decor (P16, "
                                  f"R45)")
            gone.append(str(d.get("id")))
    text = (f"lit niches {', '.join(made)} beside the TV unit {unit['id']} (R45)"
            + (f"; the TV wall's {', '.join(gone)} left it (a plain TV wall)" if gone else "")
            + (f"; {'; '.join(notes)}" if notes else ""))
    return [_record(building, room["id"], "tv_niches", True, text, made)]


# --------------------------------------------------------------------------
# 2. the dining set (R40-R43)
# --------------------------------------------------------------------------

def dining_art_width(table_len: float, stretch_len: float) -> float:
    """R40 (pure): the width of the art over a dining table: ``ART_SHARE`` of the table's length within
    ``ART_MIN_W_M``-``ART_MAX_W_M``, at most ``ART_STRETCH_SHARE`` of the free wall stretch."""
    w = min(max(ART_MIN_W_M, ART_SHARE * float(table_len)), ART_MAX_W_M, ART_STRETCH_SHARE * float(stretch_len))
    return round(max(0.0, w), 3)


def _row_over(building: dict, rc, table: dict) -> list[dict]:
    rect = _rect(table, ROW_REACH_M)
    return [d for d in rc.decor(("pendant_light",)) if d.get("center")
            and (table["id"] in (d.get("anchor_ids") or [])
                 or G.point_in_polygon((float(d["center"][0]), float(d["center"][1])), rect))]


def dining_fixture_kind(sc: dict, fam: str) -> Optional[str]:
    """R42 (pure): the one fixture over a dining table the room's scheme asks: ``track_pendants`` (track lights),
    ``linear_pendant`` (a linear statement in the families that hang one), else None (the row stays)."""
    if (sc or {}).get("lighting") == "track":
        return "track_pendants"
    if (sc or {}).get("statement") == "linear" and fam in LINEAR_DINING_FAMILIES:
        return "linear_pendant"
    return None


def dining_light(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R42: one fixture over the dining table in place of its row of pendants (module docstring, 2)."""
    from wenart.furniture import ceiling_lights as CL
    from wenart.furniture import room_details as RD

    room = rc.room
    table = _dining_table(rc)
    if room.get("room_type") not in ROOM_TYPES or table is None:
        return []
    kind = dining_fixture_kind(sc, fam)
    row = _row_over(building, rc, table)
    if kind is None:
        return [_record(building, room["id"], "dining_light", False,
                        f"the scheme's {sc.get('statement') or 'statement'} light and "
                        f"{sc.get('lighting') or 'downlights'}: the row of pendants over {table['id']} stays")]
    if any(d.get("fixture") in CL.ROW_FIXTURES for d in row):
        return []
    if any(d.get("fixture") == "statement" for d in row):
        return [_record(building, room["id"], "dining_light", False,
                        f"the statement fixture hangs over {table['id']}: it stays")]
    if not row:
        return [_record(building, room["id"], "dining_light", False, f"no pendant hangs over {table['id']} (its "
                                                                     f"ceiling or its blockers)")]
    axis, length, rot = _long_axis(table)
    tc = _centre(table)
    top = _top(table)
    bottom = min(float(d["center"][2]) for d in row if len(d["center"]) > 2) if all(
        len(d["center"]) > 2 for d in row) else top + PENDANT_OVER_TOP_M
    offs = sorted(round((float(d["center"][0]) - tc[0]) * axis[0] + (float(d["center"][1]) - tc[1]) * axis[1], 3)
                  for d in row)
    if kind == "linear_pendant":
        w = min(max(LINEAR_MIN_M, round(ART_SHARE * length / 0.05) * 0.05), LINEAR_MAX_M, max(0.6, length - 0.2))
        d = LINEAR_D_M
        what = (f"a slim black linear pendant {w:.2f} m long over the {length:.2f} m dining table {table['id']} "
                f"(R42: the scheme's linear statement)")
        extra = {}
    else:
        span = (offs[-1] - offs[0]) if len(offs) > 1 else 0.0
        w = min(max(1.0, span + 2.0 * TRACK_END_M), length + 0.2)
        d = TRACK_D_M
        what = (f"a black surface track {w:.2f} m long with {len(offs)} black mini pendants over the dining table "
                f"{table['id']} where its row of pendants hung (R42: the scheme's track lights, H7)")
        extra = {"track": {"pendants": len(offs), "offsets": offs, "spots": 2}}
    ceiling = RD._sloped(building, room, tc, (w, d), rot)
    drop = ceiling - bottom
    if drop < MIN_DROP_M - 1e-9:
        return [_record(building, room["id"], "dining_light", False,
                        f"the ceiling over {table['id']} leaves {drop:.2f} m: the row stays")]
    item = _item(room, "pendant_light", "dining_light", what, (tc[0], tc[1], round(bottom, 3)),
                 (w, d, round(drop, 3)), rot, fixture=kind, anchor_ids=[table["id"]], colour="black",
                 light_on=next((x.get("light_on") for x in row if isinstance(x.get("light_on"), bool)), None), **extra)
    for x in row:
        RD._drop(building, x, f"the row's light is one fixture over {table['id']} now (P16, R42: {kind})")
    made = _add(building, item, new_id)
    return [_record(building, room["id"], "dining_light", True,
                    f"{made['id']} {kind.replace('_', ' ')} in place of {', '.join(str(x.get('id')) for x in row)}",
                    [made["id"]])]


def dining_rug(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R41: a rug under the dining set where none lies (module docstring, 2)."""
    from wenart.furniture import decor as D

    room = rc.room
    table = _dining_table(rc)
    if room.get("room_type") not in ROOM_TYPES or table is None:
        return []
    have = rug_under(building, room["id"], _centre(table), (table["id"],))
    if have is not None:
        return [_record(building, room["id"], "dining_rug", True, f"rug {have.get('id')} under {table['id']}",
                        [have.get("id")])]
    if not D._usable_anchor(table):
        return [_record(building, room["id"], "dining_rug", False, f"{table['id']}'s type or place is not sure (the "
                                                                   f"decor rules' trust): no rug")]
    tw, td = _size(table)
    region = (-tw / 2.0 - D.DINING_CHAIR_M, -td / 2.0 - D.DINING_CHAIR_M, tw / 2.0 + D.DINING_CHAIR_M,
              td / 2.0 + D.DINING_CHAIR_M)
    rugs = [D.rug_polygon(d) for d in rc.decor(("rug",)) if d.get("center") and d.get("size")]
    got, why = D._rug_item(rc.ctx, table, [table], region, (0.0, 0.0), rc.pieces, rugs,
                           f"P16 (R41): a rug under the dining set {table['id']} (+ {D.DINING_CHAIR_M} m each side for "
                           f"the chairs)")
    if got is None:
        return [_record(building, room["id"], "dining_rug", False, f"no rug under {table['id']}: {why}")]
    item = _item(room, "rug", "dining_rug", got["reason"], got["center"], got["size"], got["rotation_deg"],
                 anchor_ids=got["anchor_ids"], fringe=True if fam in FRINGE_FAMILIES else None)
    from wenart.furniture import room_details as RD

    RD._toned(item, fam)
    made = _add(building, item, new_id)
    return [_record(building, room["id"], "dining_rug", True, f"rug {made['id']} under {table['id']}", [made["id"]])]


def _centre_items(building: dict, table: dict) -> list[dict]:
    from wenart.furniture import tabletop as TT

    out = []
    for d in building.get("decor") or []:
        if d.get("host_id") != table["id"] or d.get("type") not in CENTRE_TYPES or not d.get("center"):
            continue
        lx, ly, _w, _d = TT.local_box(table, d)
        if math.hypot(lx, ly) <= CENTRE_REACH_M + 1e-9:
            out.append(d)
    return out


def _light_bottom_over(building: dict, rc, table: dict) -> Optional[float]:
    """The lowest bottom of a light hanging over the table (None without one)."""
    rect = _rect(table, ROW_REACH_M)
    lows = [float(d["center"][2]) for d in rc.decor(("pendant_light",)) if d.get("center") and len(d["center"]) > 2
            and G.point_in_polygon((float(d["center"][0]), float(d["center"][1])), rect)]
    return min(lows) if lows else None


def centrepiece(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R43: the dining table's centrepiece set (module docstring, 2)."""
    from wenart.furniture import room_details as RD
    from wenart.furniture import tabletop as TT

    room = rc.room
    table = _dining_table(rc)
    if room.get("room_type") not in ROOM_TYPES or table is None:
        return []
    if fam not in CENTREPIECE_FAMILIES:
        return [_record(building, room["id"], "centrepiece", False, f"a {fam or 'unknown'} home keeps its table's "
                                                                    f"centre item")]
    if any(d.get("set") == "centrepiece" for d in building.get("decor") or [] if d.get("host_id") == table["id"]):
        return []
    from wenart.furniture import decor as D

    if not D._usable_anchor(table):
        return [_record(building, room["id"], "centrepiece", False, f"{table['id']}'s type or place is not sure (the "
                                                                    f"decor rules' trust): no set")]
    _axis, length, rot = _long_axis(table)
    if length < CENTRE_MIN_TABLE_M - 1e-9:
        return [_record(building, room["id"], "centrepiece", False, f"{table['id']} ({length:.2f} m) is too small for "
                                                                    f"a centrepiece set: its centre item stays")]
    old = _centre_items(building, table)
    others = [d for d in building.get("decor") or [] if d.get("host_id") == table["id"] and d.get("center")
              and d not in old]
    taken = [TT.local_box(table, d) for d in others]
    w, dd = _size(table)
    sw = round(min(CENTRE_W_M, CENTRE_W_SHARE * length), 3)
    got = None
    for sd in CENTRE_DEPTHS:
        box = (0.0, 0.0, sw, sd) if w >= dd else (0.0, 0.0, sd, sw)
        if TT.inside_top(table, box) and all(TT.boxes_clear(box, t) for t in taken):
            got = sd
            break
    if got is None:
        return [_record(building, room["id"], "centrepiece", False, f"no free strip in the middle of {table['id']} "
                                                                    f"between its place settings")]
    top = _top(table)
    room_over = RD._sloped(building, room, _centre(table), (w, dd), _rot(table)) - top - 0.15
    light = _light_bottom_over(building, rc, table)
    if light is not None:
        room_over = min(room_over, light - top - CENTRE_UNDER_LIGHT_M)
    h = round(min(CENTRE_MAX_H_M, room_over), 3)
    if h < CENTRE_MIN_H_M:
        return [_record(building, room["id"], "centrepiece", False, f"only {room_over:.2f} m over {table['id']} "
                                                                    f"under its light")]
    centre = TT._world(table, 0.0, 0.0)
    item = _item(room, "vase", "centrepiece",
                 f"P16 (R43): the dining table {table['id']}'s centrepiece: a glass vase of dried pampas grass, two "
                 f"concrete candle holders, a low bowl, along the table between the place settings",
                 centre[:2], (sw, got, h), rot, set="centrepiece", stems="pampas", colour="sand")
    item["host_id"] = table["id"]
    for d in old:
        RD._drop(building, d, "the table's centre takes the centrepiece set (P16, R43)")
    made = _add(building, item, new_id)
    was = f" in place of {', '.join(str(d.get('id')) for d in old)}" if old else ""
    return [_record(building, room["id"], "centrepiece", True, f"centrepiece {made['id']} on {table['id']}{was}",
                    [made["id"]])]


# --------------------------------------------------------------------------
# 3. the panel wall (R39)
# --------------------------------------------------------------------------

def _tv_segments(rc) -> set:
    from wenart.furniture import room_details as RD

    out = set()
    for unit in _tv_units(rc):
        found = RD._wall_behind(unit, rc)
        if found is not None:
            out.add(found[0])
    return out


def panel_wall(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R39: full-height handle-less panels with a lit niche on a free dining wall (module docstring, 3)."""
    from shapely.geometry import Point

    from wenart.furniture import decor as D
    from wenart.furniture import placer
    from wenart.furniture import room_details as RD

    room = rc.room
    table = _dining_table(rc)
    if room.get("room_type") not in ROOM_TYPES or table is None:
        return []
    if fam not in PANEL_WALL_FAMILIES:
        return [_record(building, room["id"], "panel_wall", False, f"a {fam or 'unknown'} home has no panel wall")]
    if rc.decor(("panel_wall",)):
        return []
    tpoly = placer.piece_from_furniture(table).polygon()
    tv_walls = _tv_segments(rc)
    min_w = PANEL_MIN_MODULES * PANEL_MODULE_M
    why = f"no free wall of {min_w:.2f} m within {PANEL_REACH_M:g} m of {table['id']}"
    for st in rc.stretches(min_len=min_w + 0.2, block_low=True, front_m=PANEL_FRONT_M):
        if st["i"] in tv_walls:
            continue
        mid = rc.wall_point(st, (st["s0"] + st["s1"]) / 2.0)
        if tpoly.distance(Point(mid)) > PANEL_REACH_M + 1e-9:
            continue
        n_mod = max(PANEL_MIN_MODULES, int(math.floor(min(st["length"] - 0.2, PANEL_MAX_W_M) / PANEL_MODULE_M
                                                      + 1e-6)))
        w = round(n_mod * PANEL_MODULE_M, 3)
        if w > st["length"] - 0.2 + 1e-9:
            continue
        s_c = (st["s0"] + st["s1"]) / 2.0
        wp = rc.wall_point(st, s_c)
        n = st["n"]
        centre = (wp[0] + n[0] * (PANEL_D_M / 2.0 + 0.002), wp[1] + n[1] * (PANEL_D_M / 2.0 + 0.002))
        rot = RD._rotation_into(n)
        flat = RD._ceiling(building, room)
        here = RD._sloped(building, room, centre, (w, PANEL_D_M), rot)
        if here < flat - 1e-6:
            why = "the wall stands under a sloped ceiling: no full-height panels"
            continue
        fails = rc.floor_failures("wardrobe", centre, rot, (w, PANEL_D_M), wall_n=n)
        if fails:
            why = f"the panels' floor or their doors' clearance fails ({', '.join(fails)})"
            continue
        h = round(flat - 0.005, 3)
        item = _item(room, "panel_wall", "panel_wall",
                     f"P16 (R39): full-height handle-less flat panels (push-to-open, {n_mod} fronts of "
                     f"{PANEL_MODULE_M:.2f} m) with an inset black-lined lit niche on the free dining wall by "
                     f"{table['id']}", (centre[0], centre[1], 0.0), (w, PANEL_D_M, h), rot,
                     wall_point=[round(wp[0], 3), round(wp[1], 3)],
                     wall_id=D._nearest_wall_id(building, room["level_id"], wp), anchor_ids=[table["id"]],
                     panel={"module_m": PANEL_MODULE_M, "niche": True, "niche_bottom_m": 0.95, "niche_h_m": 0.5,
                            "seed": 1})
        made = _add(building, item, new_id)
        return [_record(building, room["id"], "panel_wall", True,
                        f"panel wall {made['id']} ({w:.2f} m) by {table['id']} (R39)", [made["id"]])]
    return [_record(building, room["id"], "panel_wall", False, why)]


# --------------------------------------------------------------------------
# 4. the seating corner (R44, R47, R48)
# --------------------------------------------------------------------------

def drum_candidate(piece: dict) -> bool:
    """A near-square coffee table that reads as a round drum (pure; module docstring, 4)."""
    if piece.get("type") != "table_coffee" or piece.get("form"):
        return False
    w, d = _size(piece)
    lo, hi = min(w, d), max(w, d)
    return DRUM_MIN_M - 1e-9 <= lo and hi <= DRUM_MAX_M + 1e-9 and hi <= DRUM_ASPECT * lo + 1e-9


def drum_tables(building: dict, rc, sc: dict, fam: str) -> list[str]:
    """R48: near-square coffee tables become round travertine drums (module docstring, 4)."""
    from wenart.furniture import room_details as RD

    room = rc.room
    tables = [f for f in rc.pieces if drum_candidate(f)]
    if room.get("room_type") not in ROOM_TYPES or not tables:
        return []
    if fam not in DRUM_TABLE_FAMILIES:
        return [_record(building, room["id"], "drum_table", False, f"a {fam or 'unknown'} home keeps its coffee "
                                                                   f"table")]
    out = []
    for t in tables:
        t["form"] = "drum"
        t["form_why"] = (f"P16 (R48): a near-square coffee table as a round travertine drum ({min(_size(t)):.2f} m "
                         f"across, inside its footprint: the look only; {TAG})")
        design = t.get("design") if isinstance(t.get("design"), dict) else {}
        tags = [x for x in design.get("material_tags") or [] if x != "glass"]
        if design.get("material_tags") and tags != list(design.get("material_tags") or []):
            t["design"] = dict(design, material_tags=tags)
            t["design_why"] = "the drum's stone in place of the scheme's glass (R48); the glass stays on the others"
        moved = RD._onto_drum(building, t)
        out.append(_record(building, room["id"], "drum_table", True,
                           f"{t['id']} a travertine drum (R48)" + (f"; {'; '.join(moved)}" if moved else ""),
                           [t["id"]]))
    return out


def round_rug_spot(allowed, centre, table_d: float) -> Optional[tuple[float, tuple[float, float]]]:
    """``(diameter, centre)`` of the largest round rug under a round table of diameter ``table_d`` at ``centre`` that
    ``allowed`` (a shapely area) holds: from the table + ``ROUND_RUG_REACH_M`` on each side (at most
    ``ROUND_RUG_MAX_M``) down to + ``ROUND_RUG_MIN_REACH_M``, centred on the table or moved off it by up to
    ``ROUND_RUG_SHIFT_M`` (the table still ``ROUND_RUG_MIN_REACH_M`` in from the rug's edge all round), None when
    none fits."""
    from shapely.geometry import Point

    diam = min(ROUND_RUG_MAX_M, table_d + 2.0 * ROUND_RUG_REACH_M)
    while diam >= table_d + 2.0 * ROUND_RUG_MIN_REACH_M - 1e-9:
        room = min(ROUND_RUG_SHIFT_M, diam / 2.0 - table_d / 2.0 - ROUND_RUG_MIN_REACH_M)
        offsets = [(0.0, 0.0)]
        k = ROUND_RUG_SHIFT_STEP_M
        while k <= room + 1e-9:
            offsets += [(k * math.cos(math.radians(a)), k * math.sin(math.radians(a))) for a in range(0, 360, 45)]
            k += ROUND_RUG_SHIFT_STEP_M
        for dx, dy in offsets:
            c = (float(centre[0]) + dx, float(centre[1]) + dy)
            if allowed.contains(Point(c).buffer(diam / 2.0, 64)):
                return round(diam, 3), (round(c[0], 3), round(c[1], 3))
        diam -= ROUND_RUG_STEP_M
    return None


def round_rug(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R48: a round rug with concentric stripes under every drum table where none lies (module docstring, 4)."""
    from shapely.geometry import Point

    from wenart.furniture import decor as D
    from wenart.furniture import room_details as RD

    room = rc.room
    out = []
    for t in [f for f in rc.pieces if f.get("type") == "table_coffee" and f.get("form") == "drum"]:
        c = _centre(t)
        have = rug_under(building, room["id"], c, (t["id"],))
        if have is not None:
            out.append(_record(building, room["id"], "round_rug", True, f"rug {have.get('id')} under {t['id']}",
                               [have.get("id")]))
            continue
        if not D._usable_anchor(t):
            out.append(_record(building, room["id"], "round_rug", False, f"{t['id']}'s type or place is not sure "
                                                                         f"(the decor rules' trust): no rug"))
            continue
        allowed = rc.ctx.polygon.buffer(-D.RUG_ROOM_INSET_M, join_style="mitre")
        rugs = [D.rug_polygon(d) for d in rc.decor(("rug",)) if d.get("center") and d.get("size")
                and d.get("shape") != "round"]
        rugs += [Point(tuple(float(v) for v in d["center"][:2])).buffer(min(float(v) for v in d["size"][:2]) / 2.0, 48)
                 for d in rc.decor(("rug",)) if d.get("shape") == "round" and d.get("center") and d.get("size")]
        forbidden = D._rug_forbidden(rc.ctx, rc.pieces, rugs)
        if forbidden is not None:
            allowed = allowed.difference(forbidden)
        dt = min(_size(t))
        spot = round_rug_spot(allowed, c, dt)
        if spot is None:
            out.append(_record(building, room["id"], "round_rug", False,
                               f"no round rug under {t['id']}: no circle of {dt + 2.0 * ROUND_RUG_MIN_REACH_M:.2f} m "
                               f"stays off walls, door swings, fixed pieces and the other rugs"))
            continue
        got, rc_centre = spot
        chairs = [f["id"] for f in rc.pieces if f.get("type") == "armchair"
                  and G.distance(_centre(f), c) <= ARMCHAIR_REACH_M + 1e-9]
        rings = fam in RING_RUG_FAMILIES
        shift = G.distance(rc_centre, c)
        item = _item(room, "rug", "round_rug",
                     f"P16 (R48): a round rug {got:.2f} m across"
                     + (" with concentric stripes" if rings else "")
                     + f" under the drum table {t['id']}" + (f" and the armchairs {', '.join(chairs)}" if chairs
                                                             else "")
                     + (f", {shift:.2f} m off the table's centre to keep off a wall, a door swing or a fixed piece"
                        if shift > 1e-3 else ""),
                     rc_centre, (got, got), 0.0, shape="round", pattern="rings" if rings else None,
                     anchor_ids=[t["id"]] + chairs)
        RD._toned(item, fam)
        made = _add(building, item, new_id)
        out.append(_record(building, room["id"], "round_rug", True, f"round rug {made['id']} under {t['id']}",
                           [made["id"]]))
    return out


def seating_group(pieces: list[dict]) -> Optional[tuple[dict, dict, tuple[float, float]]]:
    """``(sofa, coffee table, the table's centre in the sofa's frame)`` of a living room (``decor.rugs_for_room``'s
    rule: the widest sofa with a coffee table in front of it within ``decor.COFFEE_TABLE_REACH_M``), None without
    one."""
    from shapely.geometry import Point

    from wenart.furniture import decor as D
    from wenart.furniture import placer

    usable = [f for f in pieces if D._usable_anchor(f)]
    tables = [f for f in usable if f["type"] == "table_coffee"]
    for sofa in sorted((f for f in usable if f["type"] in D.LIVING_RUG_SOFAS),
                       key=lambda f: (-float(f["footprint"]["size"][0]), f["id"])):
        fp = sofa["footprint"]
        sw, sd = (float(v) for v in fp["size"])
        near = []
        for t in tables:
            lx, ly = D._to_local(Point(t["footprint"]["center"]), fp["center"], float(fp["rotation_deg"])).coords[0]
            if ly < -sd / 2.0 and -ly - sd / 2.0 <= D.COFFEE_TABLE_REACH_M and abs(lx) <= sw / 2.0 + 0.3:
                near.append((-ly, t["id"], t, (lx, ly)))
            elif sofa["type"] == "sofa_corner" and abs(lx) <= sw / 2.0 and ly < sd / 2.0 and \
                    placer.piece_from_furniture(sofa).polygon().intersection(
                        placer.piece_from_furniture(t).polygon()).area < 1e-6:
                # 30 Oct 2026 (real04's salon): a corner sofa's table stands in the L's open corner, inside its box
                near.append((sd / 2.0 - ly, t["id"], t, (lx, ly)))
        if near:
            _d, _id, table, key = min(near, key=lambda n: (n[0], n[1]))
            return sofa, table, key
    return None


def seating_rug(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """A rug under every living room's sofa group where none lies (module docstring, 4; every family)."""
    from wenart.furniture import decor as D
    from wenart.furniture import room_details as RD

    room = rc.room
    if room.get("room_type") != "living":
        return []
    group = seating_group(rc.pieces)
    if group is None:
        if any(f.get("type") in ("sofa", "sofa_corner") for f in rc.pieces):
            return [_record(building, room["id"], "seating_rug", False,
                            "no coffee table in front of a sofa the decor rules trust (the rules' rug in front of a "
                            "lone sofa stays theirs)")]
        return []
    sofa, table, key = group
    have = rug_under(building, room["id"], _centre(table), (sofa["id"], table["id"]))
    if have is not None:
        return [_record(building, room["id"], "seating_rug", True, f"rug {have.get('id')} under {sofa['id']} + "
                                                                   f"{table['id']}", [have.get("id")])]
    fp = sofa["footprint"]
    region = D._local_bounds([sofa, table], fp["center"], float(fp["rotation_deg"]))
    if sofa["type"] == "sofa_corner":
        region = D.inner_corner_region(sofa, table)
    rugs = [D.rug_polygon(d) for d in rc.decor(("rug",)) if d.get("center") and d.get("size")]
    got, why = D._rug_item(rc.ctx, sofa, [sofa, table], region, key, rc.pieces, rugs,
                           "a rug under the sofa and coffee table group (UL106 a large rug; P16 R48)")
    if got is None:
        return [_record(building, room["id"], "seating_rug", False, f"no rug under {sofa['id']} + {table['id']}: "
                                                                    f"{why}")]
    item = _item(room, "rug", "seating_rug", got["reason"], got["center"], got["size"], got["rotation_deg"],
                 anchor_ids=got["anchor_ids"])
    RD._toned(item, fam)
    made = _add(building, item, new_id)
    return [_record(building, room["id"], "seating_rug", True, f"rug {made['id']} under {sofa['id']} + "
                                                               f"{table['id']}", [made["id"]])]


def wall_discs(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """R44: two black round wall discs on a free wall (module docstring, 4)."""
    from wenart.furniture import decor as D
    from wenart.furniture import room_details as RD

    room = rc.room
    if room.get("room_type") != "living":
        return []
    if fam not in WALL_DISC_FAMILIES:
        return [_record(building, room["id"], "wall_discs", False, f"a {fam or 'unknown'} home hangs no wall discs")]
    if rc.decor(("wall_discs",)):
        return []
    w, dd, h = DISC_SIZE
    tv_walls = _tv_segments(rc)                  # the TV wall stays plain (P16): no discs over or beside the TV
    for st in rc.stretches(min_len=w + 0.3, tall_m=1.0, front_m=0.5):
        if st["i"] in tv_walls:
            continue
        s_c = (st["s0"] + st["s1"]) / 2.0
        wp = rc.wall_point(st, s_c)
        bottom = max([DISC_BOTTOM_M] + [top + DISC_OVER_LOW_M for _p0, _p1, top in st["low"]])
        rot = RD._rotation_into(st["n"])
        ceiling = RD._sloped(building, room, wp, (w, dd), rot)
        if bottom + h > ceiling - DISC_CEILING_GAP_M:
            continue
        centre = (wp[0] + st["n"][0] * (dd / 2.0 + 0.002), wp[1] + st["n"][1] * (dd / 2.0 + 0.002))
        item = _item(room, "wall_discs", "wall_discs",
                     "P16 (R44): two black round wall discs (0.51 m and 0.32 m) on a free wall", (centre[0], centre[1],
                                                                                                  round(bottom, 3)),
                     (w, dd, h), rot, wall_point=[round(wp[0], 3), round(wp[1], 3)], colour="black",
                     wall_id=D._nearest_wall_id(building, room["level_id"], wp))
        made = _add(building, item, new_id)
        return [_record(building, room["id"], "wall_discs", True, f"wall discs {made['id']} (R44)", [made["id"]])]
    return [_record(building, room["id"], "wall_discs", False, "no free wall stretch of 1.15 m with nothing tall in "
                                                               "front")]


# --------------------------------------------------------------------------
# the pass (room_details.dress_room calls these)
# --------------------------------------------------------------------------

def start(building: dict, fam: str) -> dict:
    """The pass's record (``building["salon_details"]``), fresh for this decor stage."""
    building["salon_details"] = {"rule": RULE, "lesson": LESSON, "family": fam or None, "rooms": {}}
    return building["salon_details"]


def safe(step: Callable, building: dict, rc, *args) -> list[str]:
    """One step; its failure is a note and a warning (the room's other details still come), never the stage's end."""
    try:
        return step(building, rc, *args)
    except Exception as exc:  # noqa: BLE001 - one detail's failure never ends the room's details
        why = f"{RULE}.{step.__name__} failed: {type(exc).__name__}: {exc}"[:240]
        building["warnings"] = list(building.get("warnings") or []) + [f"{rc.room.get('id')}: {why}"]
        return [why]


def before_extras(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """The details that take a wall or the floor before the scheme's extras (a mirror, a leaning frame, a floor vase,
    a niche): the TV niches, the panel wall, the dining fixture, the rugs."""
    out: list[str] = []
    for step in (tv_niches, panel_wall, dining_light, round_rug, seating_rug, dining_rug):
        out += safe(step, building, rc, sc, fam, new_id)
    return out


def after_extras(building: dict, rc, sc: dict, fam: str, new_id: Callable) -> list[str]:
    """The details after the scheme's extras: the centrepiece (after the pampas vase of a sideboard), the wall discs
    (on what wall is left)."""
    return safe(centrepiece, building, rc, sc, fam, new_id) + safe(wall_discs, building, rc, sc, fam, new_id)


# --------------------------------------------------------------------------
# the review (model review M34, Argus U38)
# --------------------------------------------------------------------------

def _explained(building: dict, rid: str, detail: str) -> bool:
    rec = (((building.get("salon_details") or {}).get("rooms") or {}).get(rid) or {}).get(detail)
    return isinstance(rec, dict) and not rec.get("done") and bool(rec.get("why"))


def _finding(check: str, rid: str, target, problem: str, message: str, severity: str = "minor") -> dict:
    return {"check": check, "severity": severity, "target": target, "room_id": rid, "problem": problem,
            "lesson": LESSON, "kind": "taste", "message": message}


def _trusted() -> Callable[[dict], bool]:
    """The decor rules' trust in a piece (``decor.trusted_host``: verified, or typed by code from the drawing); in the
    build's Python (no schema library) a verified piece."""
    try:
        from wenart.furniture import decor as D

        return D.trusted_host
    except ImportError:
        return lambda f: f.get("status") == "verified"


def _near_sofa_table(building: dict, rid: str) -> Optional[tuple[dict, dict]]:
    """A sofa and the coffee table in front of it (pure, no placer: the table's centre in the sofa's frame); only
    pieces the decor rules trust (a rug goes only around those)."""
    trusted = _trusted()
    sofas = [f for f in _pieces(building, rid, ("sofa", "sofa_corner")) if trusted(f)]
    tables = [f for f in _pieces(building, rid, ("table_coffee",)) if trusted(f)]
    for sofa in sorted(sofas, key=lambda f: (-_size(f)[0], f["id"])):
        sw, sd = _size(sofa)
        rad = math.radians(_rot(sofa))
        sc = _centre(sofa)
        for t in sorted(tables, key=lambda f: f["id"]):
            dx, dy = _centre(t)[0] - sc[0], _centre(t)[1] - sc[1]
            lx = dx * math.cos(rad) + dy * math.sin(rad)
            ly = -dx * math.sin(rad) + dy * math.cos(rad)
            if ly < -sd / 2.0 and -ly - sd / 2.0 <= 1.5 and abs(lx) <= sw / 2.0 + 0.3:
                return sofa, t
            if sofa.get("type") == "sofa_corner" and abs(lx) <= sw / 2.0 and ly < sd / 2.0 - 0.3:
                return sofa, t                                 # in the L's open corner
    return None


def review(building: dict, manifest: Optional[dict] = None, check: str = "M34") -> tuple[list[dict], int]:
    """``(findings, rooms checked)``: the living and dining rooms against P16 (module docstring). Pure: no placer, no
    schema (it runs in the build's Python too)."""
    out: list[dict] = []
    fam = _family(building)
    trusted = _trusted()
    n = 0
    schemes = ((building.get("room_schemes") or {}).get("rooms") or {})
    for room in sorted((r for r in building.get("rooms") or [] if r.get("room_type") in ROOM_TYPES),
                       key=lambda r: str(r.get("id"))):
        rid = room["id"]
        if not _pieces(building, rid):
            continue
        n += 1
        sc = schemes.get(rid) if isinstance(schemes.get(rid), dict) else (room.get("scheme") or {})
        group = _near_sofa_table(building, rid) if room.get("room_type") == "living" else None
        if group is not None:
            sofa, t = group
            if rug_under(building, rid, _centre(t), (sofa["id"], t["id"])) is None and not _explained(
                    building, rid, "seating_rug"):
                out.append(_finding(check, rid, sofa["id"], "seating_rug",
                                    f"{rid}: the sofa group {sofa['id']} + {t['id']} stands on no rug (UL106, P16 "
                                    f"R48)"))
        tables = [f for f in _pieces(building, rid, ("table_dining",)) if trusted(f)]
        table = max(tables, key=lambda f: (_size(f)[0] * _size(f)[1], str(f["id"]))) if tables else None
        if table is not None:
            _axis, length, _r = _long_axis(table)
            if rug_under(building, rid, _centre(table), (table["id"],)) is None and not _explained(
                    building, rid, "dining_rug"):
                out.append(_finding(check, rid, table["id"], "dining_rug",
                                    f"{rid}: the dining set {table['id']} stands on no rug (P16 R41)"))
            arts = [d for d in _decor(building, rid, ("wall_art",)) if d.get("rule") == "room_details.dining_art"]
            for a in arts:
                aw = float(a["size"][0])
                if aw < ART_SMALL_SHARE * length - 1e-6 and aw < ART_MAX_W_M - 0.05:
                    out.append(_finding(check, rid, a.get("id"), "dining_art_small",
                                        f"{rid}: the print {a.get('id')} over the dining table is {aw:.2f} m wide, "
                                        f"{aw / length:.2f} of the {length:.2f} m table (P16 R40: about 2/3)"))
            kind = dining_fixture_kind(sc, fam)
            rect = _rect(table, ROW_REACH_M)
            over = [d for d in _decor(building, rid, ("pendant_light",)) if d.get("center")
                    and G.point_in_polygon((float(d["center"][0]), float(d["center"][1])), rect)]
            loose = [d for d in over if d.get("fixture") not in ("linear_pendant", "track_pendants", "statement")]
            if kind is not None and len(loose) >= 2 and len(loose) == len(over) and not _explained(
                    building, rid, "dining_light"):
                out.append(_finding(check, rid, table["id"], "dining_light",
                                    f"{rid}: {len(loose)} loose pendants over {table['id']} where the scheme asks one "
                                    f"{kind.replace('_', ' ')} (P16 R42)"))
            if fam in CENTREPIECE_FAMILIES and length >= CENTRE_MIN_TABLE_M - 1e-9 and not _explained(
                    building, rid, "centrepiece"):
                on = [d for d in building.get("decor") or [] if d.get("host_id") == table["id"]]
                if not any(d.get("set") == "centrepiece" for d in on):
                    out.append(_finding(check, rid, table["id"], "centrepiece",
                                        f"{rid}: the dining table {table['id']} has no centrepiece set (P16 R43: a "
                                        f"vase of pampas grass, candle holders, a bowl)"))
        if fam in CONSOLE_FAMILIES:
            for unit in _pieces(building, rid, ("tv_unit",)):
                rule = unit.get("rule") if isinstance(unit.get("rule"), dict) else {}
                if unit.get("form") or rule.get("free") or _explained(building, rid, "tv_console"):
                    continue
                h = unit.get("height")
                if max(_size(unit)) >= CONSOLE_MIN_W_M and (h is None or float(h) <= CONSOLE_MAX_TOP_M):
                    out.append(_finding(check, rid, unit["id"], "tv_console",
                                        f"{rid}: the TV unit {unit['id']} stands on the floor; P16 (R45) floats a low "
                                        f"console under the TV"))
            units = [u for u in _pieces(building, rid, ("tv_unit",))
                     if not (u.get("rule") if isinstance(u.get("rule"), dict) else {}).get("free")]
            niches = [d for d in _decor(building, rid, ("wall_niche",)) if (d.get("niche") or {}).get("style")
                      == "tv_side"]
            if units and fam in TV_NICHE_FAMILIES and not niches and not _explained(building, rid, "tv_niches"):
                out.append(_finding(check, rid, units[0]["id"], "tv_niches",
                                    f"{rid}: no lit shelf niche beside the TV unit {units[0]['id']} and no reason "
                                    f"recorded (P16 R45)"))
        if fam in DRUM_TABLE_FAMILIES:
            for t in _pieces(building, rid, ("table_coffee",)):
                if drum_candidate(t) and not _explained(building, rid, "drum_table"):
                    out.append(_finding(check, rid, t["id"], "drum_table",
                                        f"{rid}: the near-square coffee table {t['id']} is no round drum (P16 R48)"))
    return out, n
