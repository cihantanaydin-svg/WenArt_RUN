"""The details of the user's reference photos in the halls, living rooms and bedrooms, each room by its own scheme
(29 Oct 2026; user: "also take some inspiration from these photos", "look at all these details I want these details",
"As much detail as you can digest", "different solutions for different rooms"; lessons UL113, UL115 (hall part),
UL119; docs/reference_details_20261029.md rows H1-H8, R2-R30, R32-R34, G2, G5, V1, K13).

What (pure, deterministic; ``decor_ai.apply`` calls ``dress_details`` at the end of the decor stage, after the
professional dressing of UL106, ``wenart.furniture.dressing``; the questions and the stored AI answers are unchanged):

1. **The schemes** (``wenart.furniture.room_schemes``): every living room, bedroom, hall, dining room and home office
   gets its own scheme (V1); ``building["room_schemes"]`` records every choice and its reason, ``room["scheme"]`` what
   the build reads (the walls: one accent wall, a deep colour all round R25, a limewash texture R34; the anchor wall's
   panel: fluted, slats R13, a timber headboard panel R32, a wainscot; the dining wall's slats K13; track lights).
2. **What the scheme changes here** (``apply_scheme``):
   - the TV (R26): ``tv: wall`` hangs the TV flat on the wall at the viewer's eye height: in a bedroom in place of
     the media wall's own TV unit (a drawn unit stays and the TV hangs over it), in a living room over its unit (the
     seating group keeps its unit); every hung TV keeps the unit's place on the wall (``media_wall`` checked it);
   - the desk (R27): ``desk: floating`` makes a desk standing in a corner (its back on a wall, one end on a side wall)
     a floating corner desk (``form: floating``: a wall-hung top on an open shelf unit at its free end, our
     parametric product by design) and hangs a ``desk_wall_unit`` over it (a floating shelf, wall cabinets with an
     LED strip under them, books on the shelf) where its wall has no window;
   - the nightstands (R17, R33): ``nightstand: drum`` / ``floating`` sets the form of the nightstands at a bed's
     head (a round drum with drawers; a box hung on the wall at the mattress' height), the items on a drum moved
     onto its round top;
   - the bed wall (R16, R32): ``art_pair`` hangs two framed prints over the headboard in place of one; with a
     ``headboard_panel`` the art over the bed hangs over the panel (``min_bottom_m``); ``art`` makes sure a picture
     hangs over the bed or sofa;
   - the dining wall (K13): the wall behind a dining table (parallel to its long side, a free stretch of
     ``DINING_WALL_MIN_M``) gets the full-height slat panel (``room["scheme"]["dining_wall_at"]``, built by
     ``feature_walls``) with a large art piece on it, or the art alone;
   - track lights (H7, R14): ``lighting: track`` turns the room's general ceiling lights (the lights plan's, never
     its count or spacing) into short black ceiling tracks with three spots (``fixture: track``);
   - the living models (G5): a glass coffee table and a rattan lounge chair as the fit's preferences
     (``design.material_tags``; the refit ranks the models that show them first).
3. **The details** (the photos' rows, each a general rule; ``ADDERS``): a lit wall niche with floating shelves and
   styled objects in a hall without a console or by the scheme (H1); a round mirror over a hall's console with a vase
   of pampas grass on it (H4, R10, H5); a big floor vase with pampas grass in a free corner (H5); a round rug in a
   squarish hall, a runner in a long one (H6); a video intercom panel beside the main entrance door, 1.5 m up (H2); a
   large art frame leaning on the floor against a free wall (R5); a round wall mirror over a chest or on a free wall
   (R10; over a bedroom's dressing table an arched one, R19); one lived-in object in every bedroom (a bag on the
   floor, R29); a venetian blind behind the curtains of the
   modern families (R21); objects between the books on a bookshelf's boards (R20).

Every item is ``source: added_by_ai``, ``method: rule``, ``rule: room_details.<what>`` with its reason; floor items
pass the placer's checks (inside the room, no overlap, door swings and approaches free, windows free, the walkways);
wall items keep off doors, windows and the other wall items; nothing drawn moves. ``building["room_schemes"]
["applied"]`` lists what each room got and why a detail was left out. Build cost (UL111): each detail is one decor item
built as one mesh (its shelves, LEDs and objects together), no ray per small object.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G

RULE = "room_details"
LESSONS: tuple[str, ...] = ("UL113", "UL115", "UL119")
TAG = "29 Oct 2026, the user's reference photos: \"look at all these details I want these details\""
# = decor.DETAIL_DECOR_TYPES: the decor types this module adds (parametric until audited library models exist)
DETAIL_TYPES: tuple[str, ...] = ("wall_niche", "intercom", "floor_vase", "art_leaning", "bag", "desk_wall_unit")
FLOOR_DETAIL_TYPES: tuple[str, ...] = ("wall_niche", "floor_vase", "art_leaning", "bag")
WALL_DETAIL_TYPES: tuple[str, ...] = ("intercom", "desk_wall_unit")
DRIED_GRASS_FAMILIES: tuple[str, ...] = ("scandinavian", "japandi", "modern", "contemporary", "mediterranean",
                                         "rustic", "minimal", "modern minimal")
BLIND_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "industrial")      # R21
BLIND_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom")
# sizes of real products (designer values, assumed)
NICHE = {"widths": (1.2, 1.0, 0.8), "depth": 0.26, "height": 2.2, "ceiling_gap": 0.15, "min_stretch": 1.0}
FLOOR_VASE_SIZE = (0.40, 0.40, 1.30)          # a 0.55 m stone or terracotta vase, pampas plumes to 1.30 m
LEANING_ART = ((1.0, 0.24, 1.40), (0.8, 0.22, 1.10))     # width, footprint depth (the lean), height
BAG_SIZE = (0.55, 0.30, 0.30)                 # a weekend duffle bag
INTERCOM_SIZE = (0.13, 0.03, 0.22)            # a video door station's indoor monitor
INTERCOM_CENTRE_M = 1.50
INTERCOM_DOOR_GAP_M = 0.20                    # its edge this far from the door's opening edge (past the architrave)
ROUND_MIRROR_W = (0.8, 0.7, 0.6, 0.5)
ROUND_MIRROR_FREE_CENTRE_M = 1.55             # a round mirror on a free wall: its centre at eye height
ARCH_HOSTS: tuple[str, ...] = ("dresser", "console_table")      # a bedroom's dressing table (R19)
ARCH_MIRROR_W = (0.6, 0.5)
ARCH_MIRROR_ASPECT = 1.6
TV_WALL_CENTRE_M = {"living": 1.05, "bedroom": 1.15}     # seated eye height; propped up in bed
TV_WALL_DEPTH_M = 0.07                        # a slim panel on a flat wall bracket
TV_OVER_UNIT_M = 0.22                         # a TV hung over its unit: its bottom this far over the unit's top
TV_CEILING_GAP_M = 0.25
DESK_UNIT = {"shelf_over_m": 0.55, "height": 0.68, "depth": 0.32, "min_width": 0.8, "ceiling_gap": 0.05}
CORNER_END_M = 0.15                           # a desk end this close to a side wall stands in the corner
SHELF_UNIT_W_M = 0.40                         # the open shelf unit under a floating desk's free end
DINING_WALL_MIN_M = 1.8
DINING_WALL_REACH_M = 1.6                     # the wall behind a dining table: its long side within this of the wall
DINING_ART_BOTTOM_M = 1.25
HEADBOARD_TOP_M = 1.20                        # = feature_walls.HEADBOARD["height"]
HEADBOARD_ART_GAP_M = 0.12
ART_PAIR_SHARE = 0.75                         # the pair spans this share of the bed's width
ART_PAIR_GAP_M = 0.08
TRACK_SIZE = (1.0, 0.05, 0.12)                # a 1 m ceiling track with three spots (H7)
RUG_ROUND_D: tuple[float, ...] = (2.0, 1.8, 1.6, 1.4, 1.2)
RUG_SQUARE_ASPECT = 1.5                       # a hall up to this long for its width takes a round rug
RUNNER_W = (0.9, 0.8, 0.7)
RUG_EDGE_M = 0.15                             # a rug this far in from walls, door swings and stairs
PAMPAS_MIN_ROOM_M = 0.60                      # a vase with pampas needs this much room over its top
PAMPAS_MAX_H_M = 0.75
BLIND_DEPTH_M = 0.035
BLIND_ROLLER_ABOVE_M = 0.06
BLIND_DOWN_SHARE = 0.35
CURTAIN_BLIND_GAP_M = 0.01
STYLED_BOOK_SHARE = 0.62                      # a styled board's books take this share of the set's width
# The family's tones of the details (designer values; ``parametric.DECOR_COLOURS`` names, which are colour phrases too):
# the objects' glaze, the canvas, the bag's cloth, black or wood frames, a stone or a glazed floor vase
TONE_KEYS: tuple[str, ...] = ("objects", "art", "bag", "frame", "vase", "rug")
FAMILY_TONES: dict[str, dict[str, str]] = {   # objects, art, bag, frame, vase, rug
    "scandinavian": dict(zip(TONE_KEYS, ("sand", "sage green", "sand", "wood", "stone", "beige"))),
    "japandi": dict(zip(TONE_KEYS, ("beige", "olive", "olive", "wood", "stone", "sand"))),
    "modern": dict(zip(TONE_KEYS, ("white", "terracotta", "charcoal", "dark", "stone", "grey"))),
    "contemporary": dict(zip(TONE_KEYS, ("beige", "dusty blue", "rust", "dark", "stone", "beige"))),
    "modern minimal": dict(zip(TONE_KEYS, ("white", "sand", "charcoal", "dark", "stone", "light grey"))),
    "minimal": dict(zip(TONE_KEYS, ("white", "sand", "charcoal", "dark", "stone", "light grey"))),
    "industrial": dict(zip(TONE_KEYS, ("grey", "rust", "olive", "dark", "stone", "charcoal"))),
    "mediterranean": dict(zip(TONE_KEYS, ("terracotta", "dusty blue", "sand", "wood", "glazed", "terracotta"))),
    "classic": dict(zip(TONE_KEYS, ("cream", "navy", "beige", "wood", "stone", "navy"))),
    "rustic": dict(zip(TONE_KEYS, ("terracotta", "olive", "rust", "wood", "glazed", "rust"))),
}
DEFAULT_TONES = FAMILY_TONES["modern"]


def tones(family: str) -> dict[str, str]:
    return FAMILY_TONES.get(family) or DEFAULT_TONES


def _toned(item: Optional[dict], family: str) -> Optional[dict]:
    """The item in its family's tones (``FAMILY_TONES``; in place, returned): a colour or frame the item has is kept."""
    if item is None:
        return None
    t = tones(family)

    def put(key: str, value: str) -> None:
        if not item.get(key):
            item[key] = value
    dtype = item.get("type")
    if dtype in ("wall_niche", "desk_wall_unit"):
        put("colour", t["objects"])
    elif dtype == "floor_vase" and t["vase"] == "glazed":
        put("finish", "glazed")
        put("colour", "terracotta")
    elif dtype == "art_leaning":
        put("colour", t["art"])
        put("frame", t["frame"])
    elif dtype == "bag":
        put("colour", t["bag"])
    elif dtype == "mirror" and item.get("shape") in ("round", "arch"):
        put("frame", t["frame"])
    elif dtype == "rug":
        put("colour", t["rug"])
    return item


WALL_ITEM_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock", "curtain", "blind", "tv", "intercom",
                                    "desk_wall_unit", "wall_niche", "art_leaning")
FLOOR_OBSTACLE_TYPES: tuple[str, ...] = ("plant", "plant_large", "basket", "sculpture") + FLOOR_DETAIL_TYPES


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def family_of(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if r.get("id")}


def _level(building: dict, level_id) -> dict:
    return next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})


def _pieces(building: dict, room_id: str, types=None) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and f.get("footprint")
            and f.get("build", True) is not False and (types is None or f.get("type") in types)]


def _decor(building: dict, room_id: str, types=None) -> list[dict]:
    return [d for d in building.get("decor") or [] if d.get("room_id") == room_id
            and (types is None or d.get("type") in types)]


def _evidence(text: str) -> list[dict]:
    return [{"file": "building.json", "method": "inferred", "rule": RULE, "confidence": 0.7, "text": text}]


def _ceiling(building: dict, room: dict) -> float:
    return float(_level(building, room.get("level_id")).get("ceiling_height") or 2.7)


def _sloped(building: dict, room: dict, centre, size, rotation: float = 0.0) -> float:
    """The ceiling over an item's footprint: the level's flat ceiling, or the roof's slope where it is lower."""
    flat = _ceiling(building, room)
    try:
        from wenart.furniture import decor as D
        planes = D.ceiling_planes(building, room["level_id"])
        if planes:
            return min(flat, float(D.ceiling_over(building, room["level_id"], centre, size, rotation, planes=planes)))
    except Exception:  # noqa: BLE001 - without the roof's planes the flat ceiling
        pass
    return flat


def _top(piece: dict) -> float:
    from wenart.blender import parametric as P
    return float(P.piece_bbox(piece)[2])


def _rotation_into(n) -> float:
    """The rotation whose local -Y is ``n`` (into the room; local +Y on the wall), as the wall art's."""
    return round(G.normalise_angle(math.degrees(math.atan2(float(n[0]), -float(n[1])))), 3)


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


class Room:
    """One room's working context: its placer context, built pieces and decor (made once)."""

    def __init__(self, building: dict, room: dict):
        from wenart.furniture import placer

        self.building, self.room = building, room
        self.ctx = placer.room_context(building, room)
        self.pieces = _pieces(building, room["id"])
        self.level = _level(building, room.get("level_id"))
        self.panel_lines: list[tuple] = []          # the walls the build panels (``panel_lines``): no item on them

    def on_panel(self, a, b) -> bool:
        """Whether the room edge ``a``-``b`` runs along a wall the build panels (its midpoint within the wall's reach,
        parallel to it)."""
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        ex, ey = b[0] - a[0], b[1] - a[1]
        el = math.hypot(ex, ey) or 1e-9
        for p0, p1, reach in self.panel_lines:
            wx, wy = p1[0] - p0[0], p1[1] - p0[1]
            wl = math.hypot(wx, wy) or 1e-9
            if abs(ex * wy - ey * wx) / (el * wl) > math.sin(math.radians(10.0)):
                continue
            if G.point_segment_distance(mid, p0, p1) <= reach:
                return True
        return False

    def decor(self, types=None) -> list[dict]:
        return _decor(self.building, self.room["id"], types)

    def segment(self, i: int):
        a, b = self.ctx.segments[i]
        length = G.distance(a, b)
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length) if length > 1e-9 else (1.0, 0.0)
        return a, b, u, self.ctx.segment_normal(i), length

    def floor_obstacles(self) -> list[tuple]:
        out = []
        for d in self.decor(FLOOR_OBSTACLE_TYPES):
            if d.get("host_id") is None and d.get("center") and d.get("size"):
                out.append((tuple(float(v) for v in d["center"][:2]), (float(d["size"][0]), float(d["size"][1])),
                            float(d.get("rotation_deg") or 0.0)))
        return out

    def floor_failures(self, ptype: str, centre, rotation: float, size, wall_n=None) -> list[str]:
        """The placer checks a floor item fails (``decor_ai.free_corners``' rule: inside, no overlap, the doors and
        windows free, the clearance of other pieces, no walkway it blocks itself); ``wall_n`` (the inward normal of
        the wall the item stands against): the test box steps ``placer.ROOM_SHRINK_M`` off that wall (the placer's
        room is shrunk by it; the item itself stands at the wall)."""
        from wenart.furniture import placer
        from wenart.furniture import schemas

        if wall_n is not None:
            step = placer.ROOM_SHRINK_M + 0.002
            centre = (float(centre[0]) + float(wall_n[0]) * step, float(centre[1]) + float(wall_n[1]) * step)
            size = (float(size[0]) - 2.0 * step, float(size[1]))

        base = [placer.piece_from_furniture(f, i) for i, f in enumerate(self.pieces) if not schemas.off_floor(f)]
        for c, s, r in self.floor_obstacles():
            base.append(placer.Piece("plant", c, r, s, False, index=len(base)))
        cand = placer.Piece(ptype, (float(centre[0]), float(centre[1])), float(rotation),
                            (float(size[0]), float(size[1])), False, index=len(base))
        failed = placer.failed_checks(placer.check_piece(cand, base, self.ctx))
        if not failed and any(p.type in schemas.CLEARANCE_TYPES
                              and cand.polygon().intersection(p.front_zone()).area > placer.AREA_EPS for p in base):
            failed = ["clearance of another piece"]
        if not failed:
            before = set(placer.walkway_failures(base, self.ctx))
            if set(placer.walkway_failures(base + [cand], self.ctx)) - before:
                failed = ["walkway"]
        return failed

    def stretches(self, min_len: float = 1.0, front_m: float = 0.8, tall_m: float = 1.3, block_low: bool = False,
                  margin: float = 0.10, skip_ids=()) -> list[dict]:
        """The free stretches of the room's walls (``decor.free_wall_art``'s rule, longest first): no door, window
        or opening within ``margin``, no piece taller than ``tall_m`` (any piece with ``block_low``) within
        ``front_m`` in front, no wall item (``WALL_ITEM_TYPES``) and no floor item against it."""
        from wenart.furniture import placer
        from wenart.furniture import schemas

        doors, windows = placer.room_openings(self.building, self.room)
        walls = {w["id"]: w for w in self.building.get("walls") or []}
        out = []
        for i in range(len(self.ctx.segments)):
            a, _b, u, n, length = self.segment(i)
            if length < min_len or self.on_panel(a, _b):
                continue
            blocked = []
            for op in doors + windows:
                oc = (float(op["center"][0]), float(op["center"][1]))
                wall = walls.get(op.get("wall_id") or "")
                t = float(wall["thickness"]) if wall and wall.get("thickness") else placer.DEFAULT_WALL_THICKNESS_M
                if G.point_segment_distance(oc, a, _b) > t / 2.0 + 0.06:
                    continue
                s_o = (oc[0] - a[0]) * u[0] + (oc[1] - a[1]) * u[1]
                half = float(op["width"]) / 2.0 + margin
                blocked.append((s_o - half, s_o + half))
            low = []
            for f in self.pieces:
                if f["id"] in skip_ids:
                    continue
                poly = placer.piece_from_furniture(f).polygon()
                pts = list(poly.exterior.coords)
                depth = [(x - a[0]) * n[0] + (y - a[1]) * n[1] for x, y in pts]
                if min(depth) > front_m or max(depth) < -0.05:
                    continue
                along = [(x - a[0]) * u[0] + (y - a[1]) * u[1] for x, y in pts]
                s0, s1 = min(along), max(along)
                if s1 < 0.0 or s0 > length:
                    continue
                hung = schemas.off_floor(f)
                top = 0.0 if hung else _top(f)
                if block_low or hung or top > tall_m:
                    blocked.append((s0 - 0.05, s1 + 0.05))
                else:
                    low.append((s0, s1, top))
            for d in self.decor(WALL_ITEM_TYPES + FLOOR_OBSTACLE_TYPES):
                p = d.get("wall_point") or d.get("center")
                if not p or d.get("host_id"):
                    continue
                dist = (float(p[0]) - a[0]) * n[0] + (float(p[1]) - a[1]) * n[1]
                if dist < -0.1 or dist > (front_m if block_low else 0.35):
                    continue
                s = (float(p[0]) - a[0]) * u[0] + (float(p[1]) - a[1]) * u[1]
                half = max(float(v) for v in (d.get("size") or [0.4, 0.4])[:2]) / 2.0 + 0.10
                if -half <= s <= length + half:
                    blocked.append((s - half, s + half))
            from wenart.furniture import decor as D
            for s0, s1 in D._free_intervals(D.WALL_END_MARGIN_M, length - D.WALL_END_MARGIN_M, blocked):
                if s1 - s0 >= min_len - 1e-9:
                    out.append({"i": i, "a": a, "u": u, "n": n, "s0": s0, "s1": s1, "length": s1 - s0,
                                "low": [(p0, p1, top) for p0, p1, top in low if p1 > s0 and p0 < s1]})
        return sorted(out, key=lambda s: (-round(s["length"], 3), s["i"], s["s0"]))

    def wall_point(self, st: dict, s: float) -> tuple[float, float]:
        return (st["a"][0] + st["u"][0] * s, st["a"][1] + st["u"][1] * s)


PANEL_KINDS: tuple[str, ...] = ("fluted", "slats", "headboard_panel", "wainscot")


def panel_lines(building: dict, room: dict, style: Optional[dict]) -> list[tuple]:
    """``[(start, end, reach)]`` of the walls the build will panel in a room (its scheme's anchor-wall panel on the
    accent wall, ``looks.accent_walls``; its dining slat wall): the details standing against a wall keep off them (a
    niche or a leaning frame would stand in the slats)."""
    sc = room.get("scheme") if isinstance(room.get("scheme"), dict) else {}
    walls = {w.get("id"): w for w in building.get("walls") or []}
    ids = []
    if sc.get("feature_kind") in PANEL_KINDS:
        try:
            from wenart.blender import looks as LK
            acc = LK.accent_walls(building, _level(building, room.get("level_id")), style or {})
            ids += [wid for wid, per in acc.items() if room.get("id") in (per or {})]
        except Exception:  # noqa: BLE001 - no accent wall: no panel line
            pass
    at = sc.get("dining_wall_at") if isinstance(sc.get("dining_wall_at"), dict) else {}
    if at.get("wall_id"):
        ids.append(at["wall_id"])
    out = []
    for wid in ids:
        w = walls.get(wid)
        if w is not None:
            out.append((tuple(w["start"][:2]), tuple(w["end"][:2]), float(w.get("thickness") or 0.15) / 2.0 + 0.08))
    return out


def _note(applied: dict, rid: str, text: str) -> None:
    applied.setdefault(rid, []).append(text)


def _drop(building: dict, item: dict, why: str) -> None:
    building["decor"] = [d for d in building.get("decor") or [] if d is not item]
    building.setdefault("decor_dropped", []).append(
        {"id": item.get("id"), "type": item.get("type"), "host_id": item.get("host_id"),
         "anchor_ids": list(item.get("anchor_ids") or []), "room_id": item.get("room_id"), "reason": why})


def _wall_behind(piece: dict, rc: Room):
    from wenart.furniture import decor as D
    return D._wall_behind(piece, rc.ctx)


# --------------------------------------------------------------------------
# 2. what the scheme changes
# --------------------------------------------------------------------------

def wall_tv(building: dict, rc: Room, scheme: dict, new_id: Callable) -> list[str]:
    """R26: the room's TV flat on the wall (module docstring, 2)."""
    from wenart.furniture import media_wall as MW

    room = rc.room
    if scheme.get("tv") != "wall":
        return []
    kind = "bedroom" if room.get("room_type") == "bedroom" else "living"
    out = []
    for unit in [f for f in rc.pieces if f.get("type") in MW.HOST_TYPES]:
        rule = unit.get("rule") if isinstance(unit.get("rule"), dict) else {}
        if rule.get("free"):
            out.append(f"the TV stays on {unit['id']}: it stands free as a room divider (no wall behind it)")
            continue
        found = _wall_behind(unit, rc)
        if found is None:
            out.append(f"the TV stays on {unit['id']}: no wall behind it")
            continue
        i, _gap = found
        a, _b, u, n, _length = rc.segment(i)
        tvs = [d for d in building.get("decor") or [] if d.get("type") == "tv" and d.get("host_id") == unit["id"]]
        inches = int(((tvs[0].get("tv") or {}).get("inches") if tvs else None) or MW.TV_DEFAULT_INCHES)
        tw, _td, th = MW.tv_box(inches)
        panel_h = th - MW.TV_STAND_H_M
        c = unit["footprint"]["center"]
        s_c = (float(c[0]) - a[0]) * u[0] + (float(c[1]) - a[1]) * u[1]
        wp = (a[0] + u[0] * s_c, a[1] + u[1] * s_c)
        remove = (kind == "bedroom" and unit.get("source") == "added_by_ai" and rule.get("name") == MW.RULE)
        bottom = TV_WALL_CENTRE_M[kind] - panel_h / 2.0
        if not remove:
            bottom = max(bottom, _top(unit) + TV_OVER_UNIT_M)
        centre = (wp[0] + n[0] * TV_WALL_DEPTH_M / 2.0, wp[1] + n[1] * TV_WALL_DEPTH_M / 2.0)
        ceiling = _sloped(building, room, centre, (tw, TV_WALL_DEPTH_M), _rotation_into(n))
        if bottom + panel_h > ceiling - TV_CEILING_GAP_M:
            out.append(f"the TV stays on {unit['id']}: {ceiling:.2f} m of wall leaves no room to hang it")
            continue
        why = (f"the room's scheme mounts the {inches}-inch TV flat on the wall (R26), "
               + ("in place of the media wall's TV unit (no unit)" if remove else f"over the TV unit {unit['id']}")
               + f", its centre {bottom + panel_h / 2.0:.2f} m up, on the wall the seat faces")
        item = _item(room, "tv", "tv_wall", why, (centre[0], centre[1], bottom), (tw, TV_WALL_DEPTH_M, panel_h),
                     _rotation_into(n), wall_point=[round(wp[0], 3), round(wp[1], 3)],
                     tv={"inches": inches, "panel_m": [tw, round(panel_h, 3)], "mount": "wall"},
                     over_unit=None if remove else unit["id"])
        for t in tvs:
            _drop(building, t, f"the TV is hung on the wall by the room's scheme (R26): {item['reason']}")
        if remove:
            for d in [d for d in building.get("decor") or [] if d.get("host_id") == unit["id"]]:
                _drop(building, d, f"its host {unit['id']} leaves: the TV hangs on the wall (R26)")
            building["furniture"] = [f for f in building.get("furniture") or [] if f is not unit]
            building.setdefault("furniture_removed", []).append(
                {"id": unit["id"], "type": unit["type"], "room_id": room["id"], "rule": f"{RULE}.tv_wall",
                 "reason": "the room's scheme mounts the TV on the wall with no unit (R26); the unit was the media "
                           "wall's own (added_by_ai), never a drawn piece"})
            rc.pieces = [f for f in rc.pieces if f is not unit]
        item["id"] = new_id(room["level_id"])
        building.setdefault("decor", []).append(item)
        where = f"unit {unit['id']} removed" if remove else f"over {unit['id']}"
        out.append(f"TV {item['id']} on the wall ({where})")
    return out


def _corner_end(desk: dict, rc: Room) -> Optional[str]:
    """The end of a desk (``-x`` / ``+x`` of its frame) that stands against a side wall, None when neither does."""
    from shapely.geometry import Point

    from wenart.furniture import group_checks as GC
    from wenart.furniture import placer

    p = placer.piece_from_furniture(desk)
    best = None
    for side, sx in (("-x", -1.0), ("+x", 1.0)):
        pts = [GC.to_world(p, (sx * p.size[0] / 2.0, ly)) for ly in (-p.size[1] / 4.0, p.size[1] / 4.0)]
        d = max(rc.ctx.ring.distance(Point(q)) for q in pts)
        if d <= CORNER_END_M and (best is None or d < best[0]):
            best = (d, side)
    return best[1] if best else None


def floating_desk(building: dict, rc: Room, scheme: dict, new_id: Callable) -> list[str]:
    """R27: a corner desk floats on the wall over an open shelf unit, wall shelves and cabinets over it."""
    room = rc.room
    if scheme.get("desk") != "floating":
        return []
    out = []
    for desk in [f for f in rc.pieces if f.get("type") == "desk"]:
        found = _wall_behind(desk, rc)
        if found is None:
            out.append(f"{desk['id']} stays freestanding: no wall behind it")
            continue
        end = _corner_end(desk, rc)
        w = float(desk["footprint"]["size"][0])
        if end is None:
            out.append(f"{desk['id']} stays freestanding: it stands in no corner (no end on a side wall)")
        else:
            desk["form"] = "floating"
            shelf_w = SHELF_UNIT_W_M if w >= 1.1 else (0.30 if w >= 0.9 else 0.0)
            desk["form_detail"] = {"wall_end": end, "support": "+x" if end == "-x" else "-x",
                                   "shelf_unit_w": shelf_w}
            desk["form_why"] = (f"the room's scheme: a floating corner desk (R27): the top hangs on the wall, its "
                                f"{'+x' if end == '-x' else '-x'} end on an open shelf unit "
                                f"{shelf_w:.2f} m wide (its footprint, height and place as before; the look only)")
            out.append(f"{desk['id']} a floating corner desk")
        unit = desk_wall_unit(building, rc, desk, found)
        if unit is None:
            out.append(f"no wall unit over {desk['id']}: a window or the ceiling leaves no room")
            continue
        unit["id"] = new_id(room["level_id"])
        building.setdefault("decor", []).append(unit)
        out.append(f"wall shelves and cabinets {unit['id']} over {desk['id']}")
    return out


def desk_wall_unit(building: dict, rc: Room, desk: dict, found) -> Optional[dict]:
    """The wall unit over a desk (R27): as wide as the desk (at most its free wall), its shelf ``shelf_over_m`` over
    the desk's top, never over a window."""
    from wenart.furniture import placer

    room = rc.room
    i, _gap = found
    a, _b, u, n, length = rc.segment(i)
    c = desk["footprint"]["center"]
    s_c = (float(c[0]) - a[0]) * u[0] + (float(c[1]) - a[1]) * u[1]
    w = min(float(desk["footprint"]["size"][0]), 1.6)
    half = w / 2.0
    doors, windows = placer.room_openings(rc.building, room)
    for op in doors + windows:
        oc = (float(op["center"][0]), float(op["center"][1]))
        if G.point_segment_distance(oc, a, _b) > 0.35:
            continue
        s_o = (oc[0] - a[0]) * u[0] + (oc[1] - a[1]) * u[1]
        if abs(s_o - s_c) - float(op["width"]) / 2.0 - 0.10 < half:
            return None
    half = min(half, s_c - 0.05, length - 0.05 - s_c)
    if 2.0 * half < DESK_UNIT["min_width"] - 1e-9:
        return None
    top = _top(desk)
    bottom = top + DESK_UNIT["shelf_over_m"]
    wp = (a[0] + u[0] * s_c, a[1] + u[1] * s_c)
    d = DESK_UNIT["depth"]
    centre = (wp[0] + n[0] * (d / 2.0 + 0.003), wp[1] + n[1] * (d / 2.0 + 0.003))
    rot = _rotation_into(n)
    ceiling = _sloped(building, room, centre, (2.0 * half, d), rot)
    h = min(DESK_UNIT["height"], ceiling - DESK_UNIT["ceiling_gap"] - bottom)
    if h < 0.45:
        return None
    why = (f"a floating shelf and wall cabinets with an LED strip under them over the desk {desk['id']} (R27), "
           f"{bottom:.2f} m up (the desk's top + {DESK_UNIT['shelf_over_m']:.2f} m: the screen stays free)")
    return _item(room, "desk_wall_unit", "desk_wall_unit", why, (centre[0], centre[1], bottom), (2.0 * half, d, h), rot,
                 wall_point=[round(wp[0], 3), round(wp[1], 3)], desk_id=desk["id"])


def nightstand_forms(building: dict, rc: Room, scheme: dict) -> list[str]:
    """R17 / R33: the form of the nightstands at a bed's head; a drum's items onto its round top."""
    from wenart.furniture import dressing as DR

    form = scheme.get("nightstand")
    if form not in ("drum", "floating"):
        return []
    stands = [f for f in rc.pieces if f.get("type") == "nightstand"]
    out = []
    for bed in [f for f in rc.pieces if f.get("type") in ("bed_double", "bed_single")]:
        for corner in DR._head_corners(bed):
            s = min(stands, default=None, key=lambda p: G.distance(p["footprint"]["center"][:2], corner))
            if s is None or G.distance(s["footprint"]["center"][:2], corner) > DR.NIGHTSTAND_REACH_M or s.get("form"):
                continue
            s["form"] = form
            what = ("a round drum nightstand with drawers (R17)" if form == "drum"
                    else "a floating nightstand hung on the wall at the mattress height (R33)")
            s["form_why"] = (f"the room's scheme: {what} beside the bed {bed['id']} (its footprint and place as "
                             f"before; the look only)")
            out.append(f"{s['id']} a {form} nightstand")
            if form == "drum":
                out += _onto_drum(building, s)
    return out


def _onto_drum(building: dict, stand: dict) -> list[str]:
    """The items on a drum nightstand inside its round top (moved in towards its centre; one that cannot fit beside
    the others leaves, listed in ``decor_dropped``)."""
    from wenart.furniture import tabletop as TT

    fp = stand["footprint"]
    r = min(float(v) for v in fp["size"][:2]) / 2.0 - TT.TOP_MARGIN_M
    items = [d for d in building.get("decor") or [] if d.get("host_id") == stand["id"] and d.get("center")
             and ((d.get("host_frame") or {}).get("support") in (None, "top"))]
    placed, out = [], []
    for it in sorted(items, key=lambda d: (d.get("type") != "table_lamp", str(d.get("id")))):
        lx, ly, w, d = TT.local_box(stand, it)
        half = math.hypot(w, d) / 2.0
        dist = math.hypot(lx, ly)
        if half > r:
            _drop(building, it, f"the drum nightstand {stand['id']}'s round top is too small for it (R17)")
            out.append(f"{it.get('id')} off the drum {stand['id']}")
            continue
        if dist + half > r:
            k = max(0.0, r - half) / dist if dist > 1e-9 else 0.0
            lx, ly = lx * k, ly * k
        if any(math.hypot(lx - px, ly - py) < half + ph + TT.ITEM_GAP_M for px, py, ph in placed):
            _drop(building, it, f"no room beside the other items on the drum nightstand {stand['id']}'s round top")
            out.append(f"{it.get('id')} off the drum {stand['id']}")
            continue
        new = TT._world(stand, lx, ly)
        if abs(new[0] - float(it["center"][0])) > 1e-4 or abs(new[1] - float(it["center"][1])) > 1e-4:
            it["moved_for"] = {"from": list(it["center"][:2]), "slot": f"{stand['id']}.drum",
                               "reason": "onto the drum nightstand's round top (R17)"}
            it["center"] = list(new) + list(it["center"][2:])
            it.pop("host_frame", None)
        placed.append((lx, ly, half))
    return out


def _bed_art(building: dict, rid: str, bed: dict) -> list[dict]:
    return [d for d in building.get("decor") or [] if d.get("room_id") == rid and d.get("type") == "wall_art"
            and bed["id"] in (d.get("anchor_ids") or [])]


def bed_wall(building: dict, rc: Room, scheme: dict, new_id: Callable) -> list[str]:
    """R16 / R32 / art: the pictures over the bed (bedroom) or the sofa (living room) by the scheme's feature."""
    from wenart.furniture import decor as D

    room = rc.room
    feat = scheme.get("feature")
    kind = scheme.get("kind")
    anchors = (("bed_double", "bed_single") if kind == "bedroom" else ("sofa", "sofa_corner"))
    hosts = sorted((f for f in rc.pieces if f.get("type") in anchors),
                   key=lambda f: (anchors.index(f["type"]), f["id"]))
    out = []
    for host in hosts[:1]:
        arts = _bed_art(building, room["id"], host)
        if feat == "art_pair" and host["type"] == "bed_double":
            span, why = D.wall_art_for_host(host, rc.ctx, building, rc.level, width_share=ART_PAIR_SHARE,
                                           max_w=1.4, min_w=0.8)
            if span is None:
                out.append(f"no art pair over {host['id']}: {why}")
                continue
            total = float(span["size"][0])
            each = round((total - ART_PAIR_GAP_M) / 2.0, 3)
            rot = math.radians(float(span["rotation_deg"]))
            ux, uy = math.cos(rot), math.sin(rot)
            for a in arts:
                _drop(building, a, "the room's scheme hangs a pair of prints over the bed in its place (R16)")
            for k, sgn in enumerate((-1.0, 1.0)):
                off = sgn * (each + ART_PAIR_GAP_M) / 2.0
                it = dict(span)
                it["center"] = [round(span["center"][0] + ux * off, 3), round(span["center"][1] + uy * off, 3)]
                it["wall_point"] = [round(span["wall_point"][0] + ux * off, 3),
                                    round(span["wall_point"][1] + uy * off, 3)]
                it["size"] = [each, span["size"][1]]
                it.update(kind="decor", level_id=room["level_id"], room_id=room["id"], asset=None, host_id=None,
                          source="added_by_ai", method="rule", rule=f"{RULE}.art_pair", slot=f"{host['id']}.art_pair",
                          colour=None, confidence=0.7, status="verified", pair=k)
                text = (f"one of two framed prints over the headboard of {host['id']} (R16: wall art in pairs over the "
                        f"bed; {TAG})")
                it["reason"], it["evidence"] = text, _evidence(text)
                it["id"] = new_id(room["level_id"])
                building.setdefault("decor", []).append(it)
            out.append(f"an art pair over {host['id']}" + (f" in place of {', '.join(str(a.get('id')) for a in arts)}"
                                                         if arts else ""))
            continue
        if feat in ("art", "headboard_panel", "art_pair") and not arts:
            it, why = D.wall_art_for_host(host, rc.ctx, building, rc.level)
            if it is None:
                out.append(f"no art over {host['id']}: {why}")
            else:
                it.update(kind="decor", level_id=room["level_id"], room_id=room["id"], asset=None, host_id=None,
                          source="added_by_ai", method="rule", rule=f"{RULE}.art", slot=f"{host['id']}.art",
                          colour=None, confidence=0.7, status="verified")
                text = f"a large art piece over {host['id']} (the room's scheme: {feat}; {TAG})"
                it["reason"], it["evidence"] = text, _evidence(text)
                it["id"] = new_id(room["level_id"])
                building.setdefault("decor", []).append(it)
                arts = [it]
                out.append(f"art {it['id']} over {host['id']}")
        if scheme.get("feature_kind") == "headboard_panel":
            for a in arts:
                a["min_bottom_m"] = round(HEADBOARD_TOP_M + HEADBOARD_ART_GAP_M, 3)
                a["reason"] = f"{a.get('reason') or 'art'}; hung over the timber headboard panel (R32)"
                out.append(f"{a.get('id')} hung over the headboard panel")
    return out


def dining_wall(building: dict, rc: Room, scheme: dict, new_id: Callable) -> list[str]:
    """K13: the wall behind a dining table: a full-height slat wall (built by ``feature_walls``) with a large art
    piece on it, or the art alone."""
    from wenart.furniture import decor as D

    room = rc.room
    what = scheme.get("dining_wall")
    if what not in ("slats", "art"):
        return []
    tables = sorted((f for f in rc.pieces if f.get("type") == "table_dining"),
                    key=lambda f: -float(f["footprint"]["size"][0]) * float(f["footprint"]["size"][1]))
    if not tables:
        return []
    t = tables[0]
    tc = (float(t["footprint"]["center"][0]), float(t["footprint"]["center"][1]))
    rot = math.radians(float(t["footprint"]["rotation_deg"]))
    w, d = (float(v) for v in t["footprint"]["size"][:2])
    long_dir = (math.cos(rot), math.sin(rot)) if w >= d else (-math.sin(rot), math.cos(rot))
    half_short = min(w, d) / 2.0
    best = None
    for st in rc.stretches(min_len=DINING_WALL_MIN_M, tall_m=1.0, front_m=0.6):
        if abs(st["u"][0] * long_dir[1] - st["u"][1] * long_dir[0]) > math.sin(math.radians(10.0)):
            continue                                   # the wall runs along the table's long side
        dist = (tc[0] - st["a"][0]) * st["n"][0] + (tc[1] - st["a"][1]) * st["n"][1] - half_short
        s_t = (tc[0] - st["a"][0]) * st["u"][0] + (tc[1] - st["a"][1]) * st["u"][1]
        if dist < 0.0 or dist > DINING_WALL_REACH_M or not st["s0"] - 0.3 <= s_t <= st["s1"] + 0.3:
            continue
        key = (dist, -st["length"])
        if best is None or key < best[0]:
            best = (key, st, s_t, dist)
    if best is None:
        return [f"no dining wall behind {t['id']}: no free wall stretch of {DINING_WALL_MIN_M:g} m along its long "
                f"side within {DINING_WALL_REACH_M:g} m"]
    _k, st, s_t, dist = best
    s_c = min(max(s_t, st["s0"] + 0.5), st["s1"] - 0.5)
    wp = rc.wall_point(st, s_c)
    out = []
    if what == "slats":
        room.setdefault("scheme", {})["dining_wall_at"] = {
            "wall_id": D._nearest_wall_id(building, room["level_id"], wp), "point": [round(wp[0], 3), round(wp[1], 3)],
            "table_id": t["id"], "stretch_m": round(st["length"], 3),
            "reason": f"the wall behind the dining table {t['id']} ({dist:.2f} m from its long side): a full-height "
                      f"slat panel over its free stretch (K13)"}
        out.append(f"a slat wall behind {t['id']} (the build's feature walls)")
    width = round(min(1.4, 0.55 * st["length"]), 3)
    bottom = DINING_ART_BOTTOM_M
    ceiling = _sloped(building, room, wp, (width, 0.04), _rotation_into(st["n"]))
    max_h = round(ceiling - 0.10 - bottom, 3)
    if any(d.get("free_wall") and d.get("type") == "wall_art"
           and G.distance(d.get("wall_point") or d.get("center"), wp) < width for d in rc.decor(("wall_art",))):
        return out + ["the dining wall already holds its art"]
    if max_h < 0.4:
        return out + ["no art on the dining wall: the ceiling leaves too little room"]
    centre = (wp[0] + st["n"][0] * 0.02, wp[1] + st["n"][1] * 0.02)
    text = (f"a large framed art piece on the dining wall behind {t['id']}"
            + (" on its slat panel (K13)" if what == "slats" else " (the room's scheme)") + f" ({TAG})")
    it = {"kind": "decor", "type": "wall_art", "level_id": room["level_id"], "room_id": room["id"], "asset": None,
          "host_id": None, "source": "added_by_ai", "method": "rule", "rule": f"{RULE}.dining_art",
          "slot": f"{room['id']}.dining_art", "colour": None, "confidence": 0.7, "status": "verified",
          "center": [round(centre[0], 3), round(centre[1], 3)], "rotation_deg": _rotation_into(st["n"]),
          "size": [width, 0.04], "wall_point": [round(wp[0], 3), round(wp[1], 3)],
          "wall_id": D._nearest_wall_id(building, room["level_id"], wp), "gap_m": D.WALL_ART_GAP_M,
          "bottom_m": bottom, "max_height_m": max_h, "free_wall": True, "reason": text, "evidence": _evidence(text)}
    it["id"] = new_id(room["level_id"])
    building.setdefault("decor", []).append(it)
    return out + [f"art {it['id']} on the dining wall"]


def track_lights(building: dict, rc: Room, scheme: dict) -> list[str]:
    """H7 / R14: the room's general ceiling lights as short black ceiling tracks with spots (count and places kept)."""
    if scheme.get("lighting") != "track":
        return []
    from wenart.furniture import ceiling_lights as CL

    room = rc.room
    flat = _ceiling(building, room)
    poly = [tuple(p[:2]) for p in room.get("polygon") or []]
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    along_x = (max(xs) - min(xs)) >= (max(ys) - min(ys)) if poly else True
    out = []
    for d in rc.decor(("ceiling_light",)):
        if not d.get("center") or d.get("anchor_ids") or d.get("fixture") not in (None, "downlight") \
                or d.get("rule") != getattr(CL, "RULE", "decor.ceiling_lights"):
            continue
        here = _sloped(building, room, d["center"][:2], TRACK_SIZE[:2], 0.0 if along_x else 90.0)
        if here < flat - 1e-6:
            continue
        d.update(type="ceiling_light", fixture="track", size=list(TRACK_SIZE),
                 rotation_deg=0.0 if along_x else 90.0,
                 center=[round(float(d["center"][0]), 3), round(float(d["center"][1]), 3),
                         round(flat - TRACK_SIZE[2], 3)])
        d["reason"] = f"{d.get('reason') or 'light'}; as a black ceiling track with three spots (H7, R14)"
        d["dressing"] = list(d.get("dressing") or []) + ["ceiling track light"]
        out.append(f"{d.get('id')} a ceiling track light")
    return out


def statement_style(building: dict, rc: Room, scheme: dict) -> list[str]:
    """R3, R4, R15, R30: the room's statement fixture in its scheme's style (globe, linear, cluster): the fit's
    preference (``fit.fixture_pool``)."""
    style = scheme.get("statement")
    if not style:
        return []
    out = []
    for d in rc.decor(("pendant_light", "ceiling_light")):
        if d.get("fixture") == "statement" and not d.get("statement_style"):
            d["statement_style"] = style
            d["reason"] = f"{d.get('reason') or 'light'}; a {style} statement fixture by the room's scheme"
            out.append(f"{d.get('id')} a {style} statement fixture")
    return out


DRAPE_COLOUR_WALLS: tuple[str, ...] = ("accent", "deep_colour", "limewash")


def drape_colours(building: dict, rc: Room, scheme: dict) -> list[str]:
    """R6: the drape layer of a room's curtains in its scheme's colour (the brief's curtain colour wins)."""
    colour = scheme.get("wall_colour")
    if scheme.get("walls") not in DRAPE_COLOUR_WALLS or not colour:
        return []
    out = []
    for d in rc.decor(("curtain",)):
        if d.get("colour_source") == "brief" or d.get("colour_scheme"):
            continue
        d["colour_scheme"] = colour
        if d.get("colour") and d["colour"] != colour:
            d["colour_ai"] = d["colour"]
        d["colour"] = colour
        out.append(f"{d.get('id')} drapes in {colour} (R6: the room's colour)")
    return out


def living_models(building: dict, rc: Room, scheme: dict) -> list[str]:
    """G5: the living room's model choices as the fit's preferences (``design.material_tags``)."""
    out = []
    want = {"table_coffee": "glass" if scheme.get("coffee_table") == "glass" else None,
            "side_table": "glass" if scheme.get("coffee_table") == "glass" else None,      # R24: a glass side table
            "armchair": "rattan" if scheme.get("lounge_chair") == "rattan" else None}
    for f in rc.pieces:
        tag = want.get(f.get("type"))
        if not tag:
            continue
        group = f.get("group") if isinstance(f.get("group"), dict) else {}
        if f["type"] == "armchair" and (not group or group.get("group") == "seating"):
            continue                    # the sofa set's armchairs match the sofa: only a lounge (accent) chair
        design = f.get("design") if isinstance(f.get("design"), dict) else {}
        tags = [t for t in design.get("material_tags") or [] if isinstance(t, str)]
        if tag in tags:
            continue
        f["design"] = dict(design, material_tags=tags + [tag])
        f["design_why"] = (f"the room's scheme: a {tag} {f['type'].replace('_', ' ')} (G5), a preference of the fit "
                           f"(the models that show it first)")
        out.append(f"{f['id']}: a {tag} {f['type'].replace('_', ' ')} preferred")
    return out


# --------------------------------------------------------------------------
# 3. the details
# --------------------------------------------------------------------------

def wall_niche(building: dict, rc: Room, reason: str) -> Optional[dict]:
    """H1: a lit niche (a shallow built-out box with floating shelves, an LED strip under each, styled objects) on
    the longest free wall stretch whose floor in front is free (a floor item passing the placer's checks)."""
    room = rc.room
    for st in rc.stretches(min_len=NICHE["min_stretch"], block_low=True, front_m=0.5):
        for w in NICHE["widths"]:
            if w > st["length"] - 0.1:
                continue
            s_c = (st["s0"] + st["s1"]) / 2.0
            wp = rc.wall_point(st, s_c)
            d = NICHE["depth"]
            centre = (wp[0] + st["n"][0] * (d / 2.0 + 0.002), wp[1] + st["n"][1] * (d / 2.0 + 0.002))
            rot = _rotation_into(st["n"])
            ceiling = _sloped(building, room, centre, (w, d), rot)
            h = min(NICHE["height"], ceiling - NICHE["ceiling_gap"])
            if h < 1.6:
                continue
            if rc.floor_failures("bookshelf", centre, rot, (w, d), wall_n=st["n"]):
                continue
            return _item(room, "wall_niche", "niche", f"{reason}: a lit wall niche {w:.2f} m wide, {h:.2f} m high "
                                                     f"with floating shelves (H1)", (centre[0], centre[1], 0.0),
                         (w, d, h), rot, wall_point=[round(wp[0], 3), round(wp[1], 3)],
                         niche={"shelves": max(3, min(5, int((h - 0.5) / 0.38))), "objects": True})
    return None


def floor_vase(building: dict, rc: Room, reason: str) -> Optional[dict]:
    """H5: a big floor vase with pampas grass in a free corner (``decor_ai.free_corners``' checks)."""
    from wenart.furniture import decor_ai as DA

    room = rc.room
    w, d, h = FLOOR_VASE_SIZE
    others = [c for c, _s, _r in rc.floor_obstacles()]
    for c in DA.free_corners(room, rc.pieces, building, rc.ctx, others=tuple(others), size=(w, d), inset=0.28):
        if any(G.distance(c, o) < 0.8 for o in others):
            continue
        if _sloped(building, room, c, (w, d)) - 0.1 < h:
            continue
        return _item(room, "floor_vase", "floor_vase", f"{reason}: a big floor vase with dried pampas grass in a free "
                                                       f"corner (H5)", (c[0], c[1], 0.0), (w, d, h), 0.0,
                     stems="pampas")
    return None


def leaning_art(building: dict, rc: Room, reason: str) -> Optional[dict]:
    """R5: a large art frame leaning on the floor against a free wall (nothing in front of it)."""
    room = rc.room
    for st in rc.stretches(min_len=1.2, block_low=True, front_m=0.6):
        for w, dd, h in LEANING_ART:
            if w > st["length"] - 0.2:
                continue
            s_c = (st["s0"] + st["s1"]) / 2.0
            wp = rc.wall_point(st, s_c)
            centre = (wp[0] + st["n"][0] * (dd / 2.0 + 0.005), wp[1] + st["n"][1] * (dd / 2.0 + 0.005))
            rot = _rotation_into(st["n"])
            if _sloped(building, room, centre, (w, dd), rot) - 0.15 < h:
                continue
            if rc.floor_failures("plant", centre, rot, (w, dd), wall_n=st["n"]):
                continue
            return _item(room, "art_leaning", "leaning_art", f"{reason}: a large art frame leaning against a free "
                                                             f"wall (R5)", (centre[0], centre[1], 0.0), (w, dd, h),
                         rot, wall_point=[round(wp[0], 3), round(wp[1], 3)], lean_deg=6.0)
    return None


def round_mirror(building: dict, rc: Room, reason: str, hosts=("console_table", "dresser", "sideboard",
                                                              "shoe_cabinet")) -> Optional[dict]:
    """R10 (H4): a round mirror over a chest or console without a picture over it (R19: over a bedroom's chest, a
    dressing table, an arched one), else a round one on a free wall at eye height."""
    from wenart.furniture import decor as D

    room = rc.room
    hung = {a for d in rc.decor(("wall_art", "mirror", "clock")) for a in d.get("anchor_ids") or []}
    for host in sorted((f for f in rc.pieces if f.get("type") in hosts and f["id"] not in hung),
                       key=lambda f: (hosts.index(f["type"]), f["id"])):
        # R19: over a bedroom's chest (a dressing table) an arched mirror, as tall as 1.6 x its width where it fits
        arch = room.get("room_type") == "bedroom" and host["type"] in ARCH_HOSTS
        for w in (ARCH_MIRROR_W if arch else ROUND_MIRROR_W):
            it, _why = D.wall_art_for_host(host, rc.ctx, building, rc.level, dtype="mirror", width_share=1.0, max_w=w,
                                           gap=0.20, min_w=w - 1e-6)
            need = w * (ARCH_MIRROR_ASPECT if arch else 1.0)
            if it is None or float(it.get("max_height_m") or 0.0) < (w * 1.2 if arch else w):
                continue
            what = (f"an arched mirror over the dressing table {host['id']} (R19)" if arch
                    else f"a round mirror over {host['id']} (R10, H4)")
            out = _item(room, "mirror", "arch_mirror" if arch else "round_mirror", f"{reason}: {what}",
                        it["center"], (w, 0.04), it["rotation_deg"])
            out.update({k: it[k] for k in ("wall_point", "wall_id", "gap_m", "bottom_m") if k in it})
            out.update(shape="arch" if arch else "round", anchor_ids=[host["id"]],
                       max_height_m=round(min(need, float(it["max_height_m"])), 3))
            return out
    for st in rc.stretches(min_len=1.0, tall_m=1.0, front_m=0.5):
        w = next((x for x in ROUND_MIRROR_W if x <= st["length"] - 0.3), None)
        if w is None:
            continue
        s_c = (st["s0"] + st["s1"]) / 2.0
        wp = rc.wall_point(st, s_c)
        bottom = round(ROUND_MIRROR_FREE_CENTRE_M - w / 2.0, 3)
        under = [top for _p0, _p1, top in st["low"]]
        bottom = max([bottom] + [t + 0.25 for t in under])
        ceiling = _sloped(building, room, wp, (w, 0.04), _rotation_into(st["n"]))
        if bottom + w > ceiling - 0.15:
            continue
        centre = (wp[0] + st["n"][0] * 0.02, wp[1] + st["n"][1] * 0.02)
        it = _item(room, "mirror", "round_mirror", f"{reason}: a round mirror on a free wall at eye height (R10)",
                   centre, (w, 0.04), _rotation_into(st["n"]), shape="round", free_wall=True,
                   wall_point=[round(wp[0], 3), round(wp[1], 3)], bottom_m=round(bottom, 3), max_height_m=w,
                   gap_m=0.25, wall_id=D._nearest_wall_id(building, room["level_id"], wp))
        return it
    return None


def pampas_vase(building: dict, rc: Room, family: str, new_id: Callable) -> list[str]:
    """H4 / H5: one vase on a console, sideboard or chest of the room takes dried pampas grass (a tall vase where the
    room over the top allows: the ceiling, a window's sill); one is added on a hall console with none."""
    if family not in DRIED_GRASS_FAMILIES:
        return []
    from wenart.furniture import decor_ai as DA
    from wenart.furniture import tabletop as TT

    room = rc.room
    hosts = {f["id"]: f for f in rc.pieces
             if f.get("type") in ("console_table", "sideboard", "dresser", "shoe_cabinet")}
    if not hosts or any(d.get("stems") for d in rc.decor(("vase",))):
        return []
    for hid, host in sorted(hosts.items()):
        try:
            ceiling_room, sill_room = DA.top_room(host, room, building, rc.ctx)
        except Exception:  # noqa: BLE001 - no heights: no tall vase
            continue
        room_over = min(v for v in (ceiling_room, sill_room) if v is not None) if any(
            v is not None for v in (ceiling_room, sill_room)) else None
        if room_over is None or room_over < PAMPAS_MIN_ROOM_M:
            continue
        h = round(min(PAMPAS_MAX_H_M, room_over - 0.02), 3)
        vases = [d for d in rc.decor(("vase",)) if d.get("host_id") == hid]
        if vases:
            v = vases[0]
            v["stems"] = "pampas"
            v["size"] = [float(v["size"][0]), float(v["size"][1]), h]
            v["reason"] = f"{v.get('reason') or 'vase'}; with dried pampas grass (H4, H5)"
            return [f"{v.get('id')} on {hid} with pampas grass"]
        if room.get("room_type") != "hall":
            continue
        on = [d for d in building.get("decor") or [] if d.get("host_id") == hid and d.get("center")]
        taken = [TT.local_box(host, d) for d in on]
        spot = TT.free_spot(host, (0.18, 0.18), taken)
        if spot is None:
            continue
        it = _item(room, "vase", "pampas_vase", f"a vase of dried pampas grass on the hall console {hid} (H4)",
                   TT._world(host, *spot), (0.18, 0.18, h), float(host["footprint"]["rotation_deg"]), stems="pampas")
        it["host_id"] = hid
        it["id"] = new_id(room["level_id"])
        building.setdefault("decor", []).append(it)
        return [f"a pampas vase {it['id']} on {hid}"]
    return []


def hall_rug(building: dict, rc: Room, scheme: dict) -> Optional[dict]:
    """H6: a round rug in a squarish hall, a runner in a long one, on the free floor (off the walls, door swings,
    stairs and furniture by ``RUG_EDGE_M``)."""
    from shapely.geometry import Point, Polygon
    from shapely.ops import polylabel, unary_union

    from wenart.furniture import placer

    room = rc.room
    if rc.decor(("rug",)):
        return None
    poly = Polygon([tuple(p[:2]) for p in room.get("polygon") or []])
    if not poly.is_valid or poly.area < 2.0:
        return None
    holes = [placer.piece_from_furniture(f).polygon() for f in rc.pieces]
    for door in rc.ctx.doors:
        if door.swing is not None:
            holes.append(door.swing)
    free = poly.buffer(-RUG_EDGE_M, join_style=2)
    if holes:
        free = free.difference(unary_union(holes).buffer(RUG_EDGE_M, join_style=2))
    if free.is_empty:
        return None
    if free.geom_type != "Polygon":
        free = max(getattr(free, "geoms", [free]), key=lambda g: g.area)
    rect = poly.minimum_rotated_rectangle
    pts = list(rect.exterior.coords)[:4]
    sides = [G.distance(pts[k], pts[k + 1]) for k in range(2)]
    aspect = max(sides) / max(1e-6, min(sides))
    want = scheme.get("rug") or ("round" if aspect <= RUG_SQUARE_ASPECT else "runner")
    if want == "round" and aspect > RUG_SQUARE_ASPECT + 0.4:
        want = "runner"
    if want == "round":
        c = polylabel(free, tolerance=0.02)
        reach = free.boundary.distance(c)
        for dia in RUG_ROUND_D:
            if dia / 2.0 <= reach + 1e-9 and Point(c.x, c.y).buffer(dia / 2.0, 48).within(free.buffer(1e-6)):
                return _item(room, "rug", "hall_rug", f"a round rug {dia:.1f} m across in the hall (H6)",
                             (c.x, c.y), (dia, dia, 0.012), 0.0, shape="round", free_floor=True)
    return _runner(room, free, pts, sides)


def _runner(room: dict, free, pts, sides) -> Optional[dict]:
    """A runner along a hall's long axis on its free floor (the longest of ``RUNNER_W`` widths that fits)."""
    from shapely.geometry import Polygon
    from shapely.ops import polylabel

    k = 0 if sides[0] >= sides[1] else 1
    (x0, y0), (x1, y1) = pts[k], pts[k + 1]
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    centres = [free.centroid, polylabel(free, tolerance=0.02)]
    for rw in RUNNER_W:
        length = max(sides) - 2.0 * RUG_EDGE_M
        while length >= 1.2:
            for c in centres:
                r = Polygon(G.rotated_rectangle((c.x, c.y), (length, rw), ang))
                if r.within(free.buffer(1e-6)):
                    return _item(room, "rug", "hall_runner", f"a runner {rw:.1f} x {length:.1f} m along the hall "
                                                             f"(H6)", (c.x, c.y), (round(length, 2), rw, 0.012), ang,
                                 free_floor=True)
            length -= 0.2
    return None


def intercoms(building: dict, new_id: Callable, style: Optional[dict] = None) -> dict[str, list[str]]:
    """H2: a video intercom panel on the wall beside every main entrance door, inside, 1.5 m up, on the side with
    free wall (no other opening, no tall piece in front)."""
    from shapely.geometry import Point

    from wenart.blender import architect_actions as AA
    from wenart.furniture import placer

    recs = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
            and not r.get("into_air") and not r.get("below_ground")]
    main = AA.main_entrance_id(building)
    doors = [r for r in recs if r.get("main")] or [r for r in recs if r.get("door_id") == main]
    rooms = _rooms(building)
    out: dict[str, list[str]] = {}
    for rec in doors:
        room = rooms.get(rec.get("room_id"))
        if room is None:
            continue
        if any(d.get("type") == "intercom" and d.get("door_id") == rec.get("door_id")
               for d in building.get("decor") or []):
            continue
        rc = Room(building, room)
        rc.panel_lines = panel_lines(building, room, style)
        zone = next((z for z in rc.ctx.doors if z.id == rec.get("door_id")), None)
        if zone is None or zone.along is None or zone.normal is None:
            out.setdefault(room["id"], []).append(f"no intercom: the entrance door {rec.get('door_id')} is not on the "
                                                  f"room's outline")
            continue
        w, d, h = INTERCOM_SIZE
        best = None
        for sgn in (1.0, -1.0):
            off = float(zone.width) / 2.0 + INTERCOM_DOOR_GAP_M + w / 2.0
            wp = (zone.inner_point[0] + zone.along[0] * sgn * off, zone.inner_point[1] + zone.along[1] * sgn * off)
            if rc.ctx.ring.distance(Point(wp)) > 0.05:
                continue
            seg = rc.ctx.segments[rc.ctx.nearest_segment(wp)]
            if rc.on_panel(*seg):
                continue                                     # a panelled wall: the other side of the door
            clash = False
            for other in list(rc.ctx.doors) + list(rc.ctx.windows):
                if other.id == zone.id:
                    continue
                if G.distance(other.inner_point, wp) < float(other.width) / 2.0 + 0.15:
                    clash = True
            for f in rc.pieces:
                if _top(f) > 1.3 and placer.piece_from_furniture(f).polygon().distance(Point(wp)) < 0.3:
                    clash = True
            if clash:
                continue
            free = min((G.distance(o.inner_point, wp) for o in list(rc.ctx.doors) + list(rc.ctx.windows)
                        if o.id != zone.id), default=9.0)
            if best is None or free > best[0]:
                best = (free, wp)
        if best is None:
            out.setdefault(room["id"], []).append(f"no intercom: no free wall beside the entrance door "
                                                  f"{rec.get('door_id')}")
            continue
        wp = best[1]
        n = zone.normal
        centre = (wp[0] + n[0] * (d / 2.0 + 0.002), wp[1] + n[1] * (d / 2.0 + 0.002))
        it = _item(room, "intercom", "intercom", f"a video intercom panel beside the entrance door "
                                                 f"{rec.get('door_id')}, {INTERCOM_CENTRE_M:.1f} m up (H2)",
                   (centre[0], centre[1], INTERCOM_CENTRE_M - h / 2.0), (w, d, h), _rotation_into(n),
                   wall_point=[round(wp[0], 3), round(wp[1], 3)], door_id=rec.get("door_id"))
        it["id"] = new_id(room["level_id"])
        building.setdefault("decor", []).append(it)
        out.setdefault(room["id"], []).append(f"intercom {it['id']} beside {rec.get('door_id')}")
    return out


def lived_in(building: dict, rc: Room) -> Optional[dict]:
    """R29: one lived-in object in a bedroom: a bag on the floor beside the foot of the bed (either side), else by
    the wardrobe or the desk, where the placer's checks pass."""
    from wenart.furniture import group_checks as GC
    from wenart.furniture import placer

    room = rc.room
    if rc.decor(("bag",)):
        return None
    w, d, _h = BAG_SIZE
    cands = []
    for bed in [f for f in rc.pieces if f.get("type") in ("bed_double", "bed_single")]:
        p = placer.piece_from_furniture(bed)
        for sx in (1.0, -1.0):
            lx = sx * (p.size[0] / 2.0 + d / 2.0 + 0.08)
            ly = -p.size[1] / 2.0 + w / 2.0 + 0.10
            cands.append((GC.to_world(p, (lx, ly)), G.normalise_angle(p.rotation_deg + 90.0), f"beside the foot of "
                                                                                              f"{bed['id']}"))
    for f in [f for f in rc.pieces if f.get("type") in ("wardrobe", "desk", "dresser")]:
        p = placer.piece_from_furniture(f)
        for sx in (1.0, -1.0):
            lx = sx * (p.size[0] / 2.0 + w / 2.0 + 0.08)
            cands.append((GC.to_world(p, (lx, p.size[1] / 2.0 - d / 2.0 - 0.02)), p.rotation_deg,
                          f"beside {f['id']}"))
    for c, rot, where in cands:
        if not rc.floor_failures("bag", c, rot, (w, d)):
            return _item(room, "bag", "lived_in", f"a lived-in touch: a weekend bag on the floor {where} (R29)",
                         (c[0], c[1], 0.0), BAG_SIZE, rot)
    return None


def blinds_with_curtains(building: dict, rc: Room, family: str, new_id: Callable) -> list[str]:
    """R21: in the modern families a window with curtains also gets a slatted blind behind them (inside the curtain
    track, the curtain moved out by the blind's depth where they would meet)."""
    if family not in BLIND_FAMILIES or rc.room.get("room_type") not in BLIND_ROOM_TYPES:
        return []
    from wenart.furniture import decor_ai as DA
    from wenart.furniture import placer

    room = rc.room
    doors, windows = placer.room_openings(building, room)
    by_id = {o["id"]: o for o in windows}
    have = {d.get("window_id") for d in rc.decor(("blind",))}
    out = []
    for cur in rc.decor(("curtain",)):
        wid = cur.get("window_id")
        op = by_id.get(wid)
        if op is None or wid in have or not cur.get("wall_point") or not cur.get("center"):
            continue
        sill, top = DA._window_heights(op, None)
        rot = math.radians(float(cur.get("rotation_deg") or 0.0))
        n = (math.sin(rot), -math.cos(rot))                # local -Y into the room
        wp = (float(cur["wall_point"][0]), float(cur["wall_point"][1]))
        oc = (float(op["center"][0]), float(op["center"][1]))
        ux, uy = math.cos(rot), math.sin(rot)
        s = (oc[0] - wp[0]) * ux + (oc[1] - wp[1]) * uy
        bp = (wp[0] + ux * s, wp[1] + uy * s)
        flat = _ceiling(building, room)
        btop = min(top + BLIND_ROLLER_ABOVE_M, flat - 0.02)
        drop = (top - sill) * BLIND_DOWN_SHARE + BLIND_ROLLER_ABOVE_M
        bw = float(op["width"]) + 0.06
        centre = (bp[0] + n[0] * (BLIND_DEPTH_M / 2.0 + 0.005), bp[1] + n[1] * (BLIND_DEPTH_M / 2.0 + 0.005))
        if _sloped(building, room, centre, (bw, BLIND_DEPTH_M), math.degrees(rot)) < btop + 0.02:
            continue
        it = _item(room, "blind", "blind", f"a slatted blind behind the curtains of window {wid} (R21)",
                   (centre[0], centre[1], round(btop - drop, 3)), (bw, BLIND_DEPTH_M, drop), math.degrees(rot),
                   window_id=wid, wall_point=[round(bp[0], 3), round(bp[1], 3)], blind_kind="slats",
                   colour="charcoal")
        it["id"] = new_id(room["level_id"])
        building.setdefault("decor", []).append(it)
        # the curtain's box starts past the blind's
        depth = float(cur["size"][1])
        cx, cy = float(cur["center"][0]), float(cur["center"][1])
        dist = (cx - wp[0]) * n[0] + (cy - wp[1]) * n[1]
        need = 0.005 + BLIND_DEPTH_M + CURTAIN_BLIND_GAP_M + depth / 2.0
        if dist < need - 1e-6:
            mv = need - dist
            cur["center"] = [round(cx + n[0] * mv, 3), round(cy + n[1] * mv, 3)] + list(cur["center"][2:])
            cur["reason"] = f"{cur.get('reason') or 'curtain'}; {mv * 100:.1f} cm off the wall for the blind (R21)"
        out.append(f"a slatted blind {it['id']} behind the curtains of {wid}")
    return out


def styled_shelves(building: dict, rc: Room) -> list[str]:
    """R20: objects between the books: every second board's book set of a bookshelf holds a small object beside its
    books (one mesh: ``styled``)."""
    out = []
    for host in [f for f in rc.pieces if f.get("type") == "bookshelf"]:
        sets = [d for d in building.get("decor") or []
                if d.get("host_id") == host["id"] and d.get("type") == "book_set"]
        for k, d in enumerate(sorted(sets, key=lambda d: (int((d.get("host_frame") or {}).get("shelf", 0)),
                                                         float((d.get("host_frame") or {}).get("u", 0.0)),
                                                         str(d.get("id"))))):
            if k % 2 == 1 and not d.get("styled"):
                d["styled"] = {"books_share": STYLED_BOOK_SHARE, "object": ("vase", "sculpture", "bowl")[k // 2 % 3]}
                d["reason"] = f"{d.get('reason') or 'books'}; a small object between the books (R20)"
                out.append(f"{d.get('id')} on {host['id']} styled")
    return out


# --------------------------------------------------------------------------
# the pass
# --------------------------------------------------------------------------

def _partners(building: dict) -> dict[str, str]:
    try:
        from wenart.furniture import decor as D
        targets, _notes = D.copy_targets(building)
        return {rid: pid for rid, (pid, _k, _t) in targets.items()}
    except Exception:  # noqa: BLE001 - without the partner map every room is planned itself
        return {}


def _no_panel(building: dict) -> set:
    rooms = ((building.get("dressing") or {}).get("rooms") or {})
    return {rid for rid, dec in rooms.items() if isinstance(dec, dict) and dec.get("feature_wall") is False}


def dress_room(building: dict, room: dict, sc: dict, fam: str, new_id: Callable, applied: dict,
               decor_on: bool = True, style: Optional[dict] = None) -> None:
    """One room's scheme changes and details (module docstring, 2 and 3; in place, notes in ``applied``)."""
    from wenart.furniture import decor as D
    from wenart.furniture import room_schemes as RS

    rid = room["id"]
    rc = Room(building, room)
    rc.panel_lines = panel_lines(building, room, style)
    for step in (wall_tv, floating_desk):
        for t in step(building, rc, sc, new_id):
            _note(applied, rid, t)
    for t in nightstand_forms(building, rc, sc):
        _note(applied, rid, t)
    if decor_on:
        for t in bed_wall(building, rc, sc, new_id) if sc.get("kind") in ("bedroom", "living") else []:
            _note(applied, rid, t)
        for t in dining_wall(building, rc, sc, new_id):
            _note(applied, rid, t)
    for t in track_lights(building, rc, sc) + living_models(building, rc, sc) + statement_style(building, rc, sc):
        _note(applied, rid, t)
    if not decor_on:
        return
    for t in drape_colours(building, rc, sc):
        _note(applied, rid, t)
    rc.pieces = _pieces(building, rid)
    rc.panel_lines = panel_lines(building, room, style)          # the dining wall may be planned now
    extras = list(sc.get("extras") or ())
    if sc.get("kind") == "hall":
        consoles = [f for f in rc.pieces if f.get("type") in RS.CONSOLE_TYPES]
        if sc.get("hall") == "niche" or not consoles:
            extras = ["niche"] + [e for e in extras if e != "niche"]
        if sc.get("hall") == "console" and consoles:
            extras = ["round_mirror"] + extras
        if sc.get("hall") == "gallery" and consoles:
            host = sorted(consoles, key=lambda f: f["id"])[0]
            if not any(host["id"] in (d.get("anchor_ids") or []) for d in rc.decor(("wall_art", "mirror"))):
                it, why = D.wall_art_for_host(host, rc.ctx, building, rc.level)
                if it is not None:
                    it.update(kind="decor", level_id=room["level_id"], room_id=rid, asset=None, host_id=None,
                              source="added_by_ai", method="rule", rule=f"{RULE}.hall_art",
                              slot=f"{host['id']}.art", colour=None, confidence=0.7, status="verified")
                    text = f"art over the hall console {host['id']} (the hall's scheme: gallery; {TAG})"
                    it["reason"], it["evidence"] = text, _evidence(text)
                    it["id"] = new_id(room["level_id"])
                    building.setdefault("decor", []).append(it)
                    _note(applied, rid, f"art {it['id']} over {host['id']}")
                else:
                    _note(applied, rid, f"no art over {host['id']}: {why}")
    for extra in extras:
        maker = {"niche": wall_niche, "floor_vase": floor_vase, "leaning_art": leaning_art,
                 "round_mirror": round_mirror}.get(extra)
        if maker is None:
            continue
        it = _toned(maker(building, rc, f"the room's scheme '{sc.get('bundle')}'"), fam)
        if it is None:
            _note(applied, rid, f"no {extra.replace('_', ' ')}: no free place passes the checks")
            continue
        it["id"] = new_id(room["level_id"])
        building.setdefault("decor", []).append(it)
        what = "arched mirror" if it.get("shape") == "arch" else extra.replace("_", " ")
        _note(applied, rid, f"{what} {it['id']}")
    if sc.get("kind") == "hall":
        rug = _toned(hall_rug(building, rc, sc), fam)
        if rug is not None:
            rug["id"] = new_id(room["level_id"])
            building.setdefault("decor", []).append(rug)
            _note(applied, rid, f"{rug.get('shape') or 'runner'} rug {rug['id']}")
    for t in pampas_vase(building, rc, fam, new_id):
        _note(applied, rid, t)
    if room.get("room_type") == "bedroom":
        bag = _toned(lived_in(building, rc), fam)
        if bag is not None:
            bag["id"] = new_id(room["level_id"])
            building.setdefault("decor", []).append(bag)
            _note(applied, rid, f"a bag {bag['id']} on the floor (lived-in)")
    for t in blinds_with_curtains(building, rc, fam, new_id) + styled_shelves(building, rc):
        _note(applied, rid, t)


def dress_details(building: dict, style: Optional[dict], new_id: Callable) -> tuple[dict, list[str]]:
    """The whole pass (module docstring; in place): ``(building, notes)``. A room whose details fail (a broken
    outline) keeps what it had: the failure is a note and a warning, never the decor stage's end."""
    from wenart.furniture import decor as D
    from wenart.furniture import room_schemes as RS

    fam = family_of(style)
    schemes = RS.plan(building, style, _no_panel(building), _partners(building))
    RS.record(building, schemes, style)
    applied: dict[str, list[str]] = {}
    decor_on = D.decor_allowed(building)
    rooms = _rooms(building)
    for rid in sorted(schemes):
        room = rooms.get(rid)
        if room is None or not D.room_takes_decor(room) or len(room.get("polygon") or []) < 3:
            continue
        try:
            dress_room(building, room, schemes[rid], fam, new_id, applied, decor_on, style)
        except Exception as exc:  # noqa: BLE001 - one room's failure never ends the decor stage
            why = f"room details failed: {type(exc).__name__}: {exc}"[:240]
            _note(applied, rid, why)
            building["warnings"] = list(building.get("warnings") or []) + [f"{rid}: {why}"]
    if decor_on:
        try:
            for rid, texts in intercoms(building, new_id, style).items():
                for t in texts:
                    _note(applied, rid, t)
        except Exception as exc:  # noqa: BLE001
            building["warnings"] = list(building.get("warnings") or []) + [
                f"intercom: {type(exc).__name__}: {exc}"[:240]]
    building["room_schemes"]["applied"] = applied
    notes = [f"{rid}: {t}" for rid, texts in sorted(applied.items()) for t in texts]
    building["room_schemes"]["notes"] = notes
    return building, notes
