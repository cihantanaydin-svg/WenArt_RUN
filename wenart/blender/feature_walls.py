"""Feature walls: a fluted wood panel or a classic wainscot on the accent wall of bedrooms and living rooms (29 Oct 2026,
lesson UL106; user, showing a professional bedroom render: "I want my renders to be as professional as these ones";
the render has vertical oak slats behind the bed head).

What:

- ``family_spec(style, room_type)``: the panel a style family puts on its accent wall (``FAMILY_FEATURE_WALLS``):
  modern, contemporary, japandi, minimal and Scandinavian homes a fluted panel (narrow vertical slats on a backing
  board, a top trim and a recessed plinth over the skirting) in the family's oak, a classic home a painted wainscot
  (a board with moulded frames and a cap rail, 1.0 m high) in its accent colour; the brief decides first
  (``feature_wall`` off, or a ``wall_accent`` of its own: a slat wall gives the fluted panel, a paint colour none).
- ``plan_feature_walls(building, level, style)``: one panel per living room and bedroom with an accent wall
  (``looks.accent_walls``: the wall behind the bed head or the sofa, else the longest wall without a window): on the
  room's face of that wall, over the stretch around the anchor piece that no door or window (``WINDOW_MARGIN_M``,
  ``DOOR_MARGIN_M``: never over an opening, clear of the curtains) and no tall piece standing against the wall
  (``TALL_M``) interrupts, at most ``MAX_WIDTH_M`` wide and at least the anchor's width + ``ANCHOR_MARGIN_M``; the
  fluted panel from the floor to the ceiling, the wainscot to ``WAINSCOT["height"]``. A room whose stretch is too
  short, or whose ceiling over it is sloped lower than ``MIN_FLUTED_H_M``, keeps its painted accent (the plan's
  ``skipped`` says why). ``decisions`` (the decor stage's ``building["dressing"]["rooms"]``, from the project's
  reference recipe) may switch a room off.
- ``panel_boxes(plan)``: the panel as boxes ``(centre, size, rotation_deg, key)`` in world coordinates (pure): no two
  boxes share a face plane where they overlap (no flicker).
- ``standoff_decor(decor, plans)``: wall art, mirrors and clocks hung on a panelled stretch stand off the panel by
  its depth (their ``wall_point`` moves; ``feature_wall_standoff_m`` records it): never buried in the slats.
- ``build_feature_walls(...)`` (bpy): one object per panel (``feature_wall_<room id>``, kind ``wall``, detail
  ``feature_wall``, pass index 0, status assumed), its materials by key (the family's veneer, the backing, the
  shadow-gap plinth; the wainscot's paint), a 2 mm bevel; the manifest entry and ``assumed`` record the plan.

29 Oct 2026 (lessons UL113, UL119; docs/reference_details_20261029.md R13, R32, K13; a different solution for each room):
a room's scheme (``room["scheme"]``, ``wenart.furniture.room_schemes``) chooses its anchor wall's panel
(``scheme_spec``): the family's fluted panel or wainscot, full-height vertical wood slats over the whole free stretch
(``slats``: R13), a timber headboard panel wider than the bed, ``HEADBOARD["height"]`` high with a ledge on top
(``headboard_panel``: R32; art hangs over it, ``standoff_decor`` keeps it on the wall), or no panel (an art pair, one
large art piece); and the wall behind a dining table may get a slat wall (``plan_dining_walls``: the scheme's
``dining_wall_at``, K13), built as ``feature_wall_<room>_dining``.

Why: the accent wall was one flat paint colour; a fluted or panelled wall is what the professional reference renders
and the real06 bedroom recipe (wall_panelling in 5 of 8 Scandinavian reference photos) show behind the bed. Real
geometry (2.6 cm deep) casts the slats' own shadows in the daylight; a normal map alone reads flat at a grazing view.
Every size is a designer value of a real product (fluted oak panels: 20-30 mm slats at a 30-40 mm pitch on a backing
board; wainscot: a dado about 1.0 m high), recorded as assumed.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

FEATURE_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom")        # = looks.ACCENT_ROOM_TYPES
OPT_OUT: tuple = (False, "none", "off", "paint")
# family -> the panel (designer values): the wood is a vocabulary veneer slug; backing ``dark`` = charcoal felt
# between the slats (an acoustic slat panel), ``wood`` = the slats' own wood
FAMILY_FEATURE_WALLS: dict[str, dict] = {
    "modern": {"kind": "fluted", "wood": "wood_veneer_oak", "backing": "dark"},
    "contemporary": {"kind": "fluted", "wood": "wood_veneer_oak", "backing": "dark"},
    "modern minimal": {"kind": "fluted", "wood": "wood_veneer_oak_light", "backing": "wood"},
    "minimal": {"kind": "fluted", "wood": "wood_veneer_oak_light", "backing": "wood"},
    "scandinavian": {"kind": "fluted", "wood": "wood_veneer_oak_light", "backing": "wood"},
    "japandi": {"kind": "fluted", "wood": "wood_veneer_oak", "backing": "dark", "slat_w": 0.040, "gap": 0.010},
    "classic": {"kind": "wainscot", "paint": "accent"},
}
FLUTED: dict[str, float] = {"slat_w": 0.022, "gap": 0.012, "slat_d": 0.018, "backing_t": 0.008, "plinth_h": 0.10,
                            "plinth_recess": 0.010, "top_h": 0.040, "top_proud": 0.004, "end_w": 0.012,
                            "wall_gap": 0.001, "ceiling_gap": 0.003, "bevel_m": 0.002}
WAINSCOT: dict[str, float] = {"height": 1.00, "board_t": 0.010, "mould_w": 0.045, "mould_d": 0.012, "cap_h": 0.035,
                              "cap_d": 0.028, "panel_w": 0.55, "gap": 0.09, "bottom": 0.17, "top_gap": 0.09,
                              "wall_gap": 0.001, "bevel_m": 0.002}
WINDOW_MARGIN_M = 0.30          # a panel ends this far from a window (the curtain rod runs 0.20 m past it)
DOOR_MARGIN_M = 0.10            # ... and from a door or a doorless opening (its frame and trim)
END_GAP_M = 0.002               # off the room's corners
TALL_M = 1.30                   # a piece this tall against the wall interrupts the panel (a wardrobe, a bookcase)
TALL_REACH_M = 0.15             # ... when its footprint comes this close to the wall face
MAX_WIDTH_M = 4.50
MIN_WIDTH_M = 1.20
ANCHOR_MARGIN_M = 0.30          # the panel is at least the anchor's width + this (the nightstands, the sofa's arms)
MIN_FLUTED_H_M = 2.10           # a fluted panel under a ceiling lower than this keeps the painted accent
FACE_REACH_M = 0.06             # a room edge lies within half the wall's thickness + this of its centre line
# 29 Oct 2026 (UL119): the scheme kinds (R13 slats over the whole free stretch, R32 the timber headboard panel)
SLATS: dict[str, float] = {"slat_w": 0.045, "gap": 0.020, "max_width": 6.0}
HEADBOARD: dict[str, float] = {"height": 1.20, "board_t": 0.020, "backing_t": 0.006, "boards": 4, "gap": 0.004,
                               "ledge_d": 0.065, "ledge_t": 0.030, "extra_m": 0.55, "wall_gap": 0.001,
                               "ceiling_gap": 0.30, "bevel_m": 0.002}
LOW_KINDS: tuple[str, ...] = ("wainscot", "headboard_panel")      # wall items hung over their top stay on the wall
NO_PANEL_FEATURES: tuple[str, ...] = ("art_pair", "art", "none")
STANDOFF_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock")
STANDOFF_REACH_M = 0.06         # a wall item whose wall point lies this close to the panel's face line is on it
CHECK = "UL106"


# --------------------------------------------------------------------------
# Which panel
# --------------------------------------------------------------------------

def _family(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def family_spec(style: Optional[dict], room_type: Optional[str]) -> tuple[Optional[dict], str]:
    """``(spec or None, why)`` of the panel on a room's accent wall (module docstring)."""
    style = style or {}
    if room_type not in FEATURE_ROOM_TYPES:
        return None, f"a {room_type} gets no feature wall"
    flag = style.get("feature_wall")
    if flag in OPT_OUT or (isinstance(flag, str) and flag.lower() in OPT_OUT):
        return None, f"the brief turns the feature wall off ({flag!r})"
    fam = _family(style)
    base = FAMILY_FEATURE_WALLS.get(fam)
    accent = style.get("wall_accent") if isinstance(style.get("wall_accent"), dict) else None
    if accent and (accent.get("material") or accent.get("colour")):
        if accent.get("material") == "wood_slat":
            spec = dict(base if base and base.get("kind") == "fluted" else FAMILY_FEATURE_WALLS["contemporary"])
            return spec, "the brief's slat accent wall built as a fluted panel"
        return None, "the brief names its own accent wall (kept as named)"
    if style.get("wall_accent") in (False, "none", "off"):
        return None, "the brief turns accent walls off"
    if base is None:
        return None, f"the {fam or 'house'} style keeps a painted accent wall"
    return dict(base), f"assumed: the {fam} style's {base['kind']} panel on the accent wall (designer value, UL106)"


def scheme_spec(room: Optional[dict], spec: Optional[dict], why: str, style: Optional[dict]
                ) -> tuple[Optional[dict], str]:
    """``(spec, why)`` of a room's anchor-wall panel by its scheme (module docstring; 29 Oct 2026, UL119): the family's
    panel (``spec``) for a ``fluted`` scheme, a slat wall, a headboard panel, a wainscot, or none; a room without a
    scheme keeps ``spec``."""
    sc = (room or {}).get("scheme") if isinstance((room or {}).get("scheme"), dict) else None
    if not sc or "feature" not in sc or (style or {}).get("room_schemes") in (False, "off", "none"):
        return spec, why
    if spec is None and why.startswith("the brief"):
        return spec, why                                     # the brief's own accent or its "off" wins
    kind = sc.get("feature_kind")
    tag = f"the room's scheme {sc.get('key')}"
    if sc.get("feature") in NO_PANEL_FEATURES or kind is None:
        what = {"art_pair": "two framed prints over the headboard", "art": "a large art piece",
                "none": "no feature"}.get(str(sc.get("feature")), "no panel")
        return None, f"{tag}: {what} on the anchor wall, no panel (V1)"
    fam = _family(style)
    base = FAMILY_FEATURE_WALLS.get(fam) or FAMILY_FEATURE_WALLS["contemporary"]
    wood = base.get("wood") or "wood_veneer_oak"
    if kind == "fluted":
        out = dict(base if base.get("kind") == "fluted" else FAMILY_FEATURE_WALLS["contemporary"])
        return out, f"{tag}: the {fam or 'house'} family's fluted panel (UL106)"
    if kind == "wainscot":
        return dict(FAMILY_FEATURE_WALLS["classic"]), f"{tag}: a painted wainscot"
    if kind == "slats":
        return ({"kind": "slats", "wood": wood, "backing": "dark", "slat_w": SLATS["slat_w"], "gap": SLATS["gap"]},
                f"{tag}: full-height vertical wood slats over the whole free stretch (R13)")
    if kind == "headboard_panel":
        return ({"kind": "headboard_panel", "wood": wood},
                f"{tag}: a timber headboard panel wider than the bed, a ledge on top (R32)")
    return spec, why


def _accent_colour(style: Optional[dict]) -> Optional[str]:
    try:
        from wenart.blender import looks as F
        acc = (style or {}).get("wall_accent") if isinstance((style or {}).get("wall_accent"), dict) else None
        return (acc or F.family_accent(style or {}) or {}).get("colour")
    except ImportError:
        return None


# --------------------------------------------------------------------------
# Where: the face of the accent wall in the room, its free stretch
# --------------------------------------------------------------------------

def _unit(dx: float, dy: float) -> tuple[float, float]:
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-12 else (0.0, 0.0)


COLLINEAR_M = 0.02              # two walls on one centre line (a straight wall drawn in segments)
JOIN_GAP_M = 0.05               # ... whose ends meet within this


def _collinear_span(wall: dict, walls: list[dict], lo: float, hi: float, edge_lo: float, edge_hi: float
                    ) -> tuple[float, float]:
    """``(lo, hi)`` of ``wall``'s station range grown over the walls on its centre line that join it (a straight
    face drawn as several wall segments), kept within the room edge's range (pure)."""
    sx, sy = float(wall["start"][0]), float(wall["start"][1])
    wu = _unit(float(wall["end"][0]) - sx, float(wall["end"][1]) - sy)
    spans = []
    for w in walls or []:
        if w is wall or w.get("id") == wall.get("id") or G.distance(w["start"], w["end"]) < 1e-6:
            continue
        ends = [(float(p[0]) - sx, float(p[1]) - sy) for p in (w["start"], w["end"])]
        if any(abs(dx * wu[1] - dy * wu[0]) > COLLINEAR_M for dx, dy in ends):
            continue
        s = sorted(dx * wu[0] + dy * wu[1] for dx, dy in ends)
        spans.append((max(s[0], edge_lo), min(s[1], edge_hi)))
    grown = True
    while grown:
        grown = False
        for a, b in spans:
            if b > a and a <= hi + JOIN_GAP_M and b >= lo - JOIN_GAP_M and (a < lo - 1e-9 or b > hi + 1e-9):
                lo, hi, grown = min(lo, a), max(hi, b), True
    return lo, hi


def face_of(room: dict, wall: dict, walls: Optional[list] = None) -> Optional[dict]:
    """The room's face of ``wall`` (pure): ``{"a", "b" (the face line's ends, the overlap of the room edge with the
    wall), "u" (a to b), "n" (into the room), "length"}``; None when no room edge runs along it. ``walls`` (the
    level's): the face runs on over the walls on the same centre line that join it along the same room edge."""
    poly = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(poly) < 3 or G.distance(wall["start"], wall["end"]) < 1e-6:
        return None
    wu = _unit(float(wall["end"][0]) - float(wall["start"][0]), float(wall["end"][1]) - float(wall["start"][1]))
    reach = float(wall.get("thickness") or 0.1) / 2.0 + FACE_REACH_M
    wlen = G.distance(wall["start"], wall["end"])
    best = None
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        if G.distance(a, b) < 1e-6:
            continue
        eu = _unit(b[0] - a[0], b[1] - a[1])
        if abs(eu[0] * wu[1] - eu[1] * wu[0]) > math.sin(math.radians(10.0)):
            continue
        if G.point_segment_distance(G.segment_midpoint(a, b), wall["start"], wall["end"]) > reach and \
                G.point_segment_distance(G.segment_midpoint(wall["start"], wall["end"]), a, b) > reach:
            continue
        s = [((p[0] - float(wall["start"][0])) * wu[0] + (p[1] - float(wall["start"][1])) * wu[1]) for p in (a, b)]
        lo, hi = max(min(s), 0.0), min(max(s), wlen)
        if hi - lo <= 0.05:
            continue
        if best is None or hi - lo > best[0]:
            best = (hi - lo, a, b, eu, lo, hi, min(s), max(s))
    if best is None:
        return None
    _len, a, b, eu, lo, hi, edge_lo, edge_hi = best
    if walls:
        lo, hi = _collinear_span(wall, walls, lo, hi, edge_lo, edge_hi)

    def on_edge(s):                     # the point of the room edge over wall station s
        wx, wy = float(wall["start"][0]) + wu[0] * s, float(wall["start"][1]) + wu[1] * s
        t = (wx - a[0]) * eu[0] + (wy - a[1]) * eu[1]
        return (a[0] + eu[0] * t, a[1] + eu[1] * t)

    pa, pb = on_edge(lo), on_edge(hi)
    u = _unit(pb[0] - pa[0], pb[1] - pa[1])
    n = (-u[1], u[0])
    mid = G.segment_midpoint(pa, pb)
    if not G.point_in_polygon((mid[0] + n[0] * 0.05, mid[1] + n[1] * 0.05), poly):
        n = (u[1], -u[0])
    return {"a": pa, "b": pb, "u": u, "n": n, "length": G.distance(pa, pb)}


def _station(face: dict, p) -> tuple[float, float]:
    """``(s along the face, distance into the room)`` of a plan point."""
    dx, dy = float(p[0]) - face["a"][0], float(p[1]) - face["a"][1]
    return dx * face["u"][0] + dy * face["u"][1], dx * face["n"][0] + dy * face["n"][1]


def _corners(fp: dict) -> list[tuple[float, float]]:
    return [tuple(c) for c in G.rotated_rectangle(fp["center"], fp["size"][:2], float(fp.get("rotation_deg") or 0.0))]


def _height(piece: dict) -> float:
    h = piece.get("height")
    if isinstance(h, (int, float)) and not isinstance(h, bool) and h > 0:
        return float(h)
    try:
        from wenart.blender import parametric as P
        return float(P.piece_bbox(piece)[2])
    except Exception:  # noqa: BLE001 - an unknown piece counts as low
        return 0.0


def blocked_spans(face: dict, wall: dict, building: dict, room: dict) -> list[tuple[float, float, str]]:
    """``[(s0, s1, what)]`` along the face that no panel may cover: the openings of the wall (and of any wall whose
    opening lies on this face), widened by their margins, and the tall pieces standing against it."""
    out = []
    walls = {w.get("id"): w for w in building.get("walls") or []}
    for o in building.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or not o.get("center"):
            continue
        s, d = _station(face, o["center"])
        host = walls.get(o.get("wall_id")) or wall          # the opening's own wall (a thicker outer wall beside it)
        reach = float(host.get("thickness") or 0.1) / 2.0 + FACE_REACH_M
        if o.get("wall_id") != wall["id"] and abs(d) > reach:
            continue
        if s < -float(o.get("width") or 0.0) or s > face["length"] + float(o.get("width") or 0.0):
            continue
        margin = WINDOW_MARGIN_M if o.get("type") == "window" else DOOR_MARGIN_M
        half = float(o.get("width") or 0.0) / 2.0 + margin
        out.append((s - half, s + half, f"{o.get('type')} {o.get('id')}"))
    for f in building.get("furniture") or []:
        if f.get("room_id") != room.get("id") or not f.get("footprint") or f.get("build", True) is False:
            continue
        pts = [_station(face, c) for c in _corners(f["footprint"])]
        if min(d for _s, d in pts) > TALL_REACH_M or _height(f) < TALL_M:
            continue
        out.append((min(s for s, _d in pts), max(s for s, _d in pts), f"{f.get('type')} {f.get('id')}"))
    return out


def free_spans(length: float, blocked: list) -> list[tuple[float, float]]:
    """The stretches of ``[END_GAP_M, length - END_GAP_M]`` outside every blocked span (pure)."""
    lo, hi = END_GAP_M, length - END_GAP_M
    out, cur = [], lo
    for a, b, *_ in sorted(blocked):
        if b <= cur:
            continue
        if a > cur:
            out.append((cur, min(a, hi)))
        cur = max(cur, b)
        if cur >= hi:
            break
    if cur < hi:
        out.append((cur, hi))
    return [(a, b) for a, b in out if b - a > 1e-6]


def _anchor_of(building: dict, room: dict, wall_id: str, walls: list[dict]) -> Optional[dict]:
    try:
        from wenart.blender import looks as F
    except ImportError:
        return None
    anchors = F.ACCENT_ANCHORS.get(room.get("room_type"), ())
    pieces = sorted((f for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
                     and f.get("type") in anchors and f.get("build", True) is not False and f.get("footprint")),
                    key=lambda f: (anchors.index(f["type"]), f["id"]))
    return next((p for p in pieces if F.wall_behind(p, walls) == wall_id), None)


def _ceiling_z(level: dict, points) -> float:
    flat = float(level["elevation"]) + float(level.get("ceiling_height") or 2.7)
    planes = level.get("ceiling_planes")
    if not planes:
        return flat
    from wenart.blender import geom2d
    return min([flat] + [min(geom2d.plane_z(p, float(x), float(y)) for p in planes) for x, y in points])


def plan_feature_walls(building: dict, level: dict, style: Optional[dict],
                       decisions: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """``(plans, skipped)`` of the level (module docstring). A plan: ``room_id``, ``wall_id``, ``kind``, ``spec``,
    ``p`` / ``q`` (the panel's ends on the face line), ``u``, ``n``, ``z0``, ``z1``, ``width_m``, ``depth_m``,
    ``anchor_id``, ``blocked`` (what narrowed it) and ``reason``; skipped: ``{"room_id", "reason"}``."""
    try:
        from wenart.blender import looks as F
    except ImportError:
        return [], []
    decisions = decisions if isinstance(decisions, dict) else {}
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]]
    by_id = {w["id"]: w for w in walls}
    rooms = {r["id"]: r for r in building.get("rooms") or [] if r.get("level_id") == level["id"]}
    plans, skipped = [], []
    for wid, per_room in sorted((F.accent_walls(building, level, style or {}) or {}).items()):
        for rid, look in sorted((per_room or {}).items()):
            room, wall = rooms.get(rid), by_id.get(wid)
            if room is None or wall is None:
                continue
            spec, why = family_spec(style, room.get("room_type"))
            spec, why = scheme_spec(room, spec, why, style)
            dec = decisions.get(rid) if isinstance(decisions.get(rid), dict) else {}
            if spec is not None and "feature_wall" in dec and not dec["feature_wall"]:
                spec, why = None, dec.get("feature_wall_why") or "the decor stage keeps a painted accent"
            if spec is None:
                skipped.append({"room_id": rid, "wall_id": wid, "reason": why})
                continue
            if dec.get("feature_wall_why"):
                why += f"; {dec['feature_wall_why']}"
            face = face_of(room, wall, walls)
            if face is None:
                skipped.append({"room_id": rid, "wall_id": wid, "reason": "no room edge along the accent wall"})
                continue
            blocked = blocked_spans(face, wall, building, room)
            spans = free_spans(face["length"], blocked)
            anchor = _anchor_of(building, room, wid, walls)
            lo_a = hi_a = None
            if anchor is not None:
                ss = [_station(face, c)[0] for c in _corners(anchor["footprint"])]
                lo_a, hi_a = min(ss), max(ss)
                centre = (lo_a + hi_a) / 2.0
                span = next((sp for sp in spans if sp[0] - 1e-6 <= centre <= sp[1] + 1e-6), None)
                if span is None and spans:
                    span = max(spans, key=lambda sp: min(sp[1], hi_a) - max(sp[0], lo_a))
            else:
                span = max(spans, key=lambda sp: sp[1] - sp[0]) if spans else None
                centre = (span[0] + span[1]) / 2.0 if span else 0.0
            need = max(MIN_WIDTH_M, (hi_a - lo_a + ANCHOR_MARGIN_M) if anchor is not None else 0.0)
            plan = _plan_span(room, wall, level, face, spec, why, look, blocked, spans, span, centre, need,
                              lo_a, hi_a, anchor)
            if isinstance(plan, str):
                skipped.append({"room_id": rid, "wall_id": wid, "reason": plan})
                continue
            if plan is not None:
                plans.append(plan)
                continue
            if span is None or span[1] - span[0] < need - 1e-9:
                skipped.append({"room_id": rid, "wall_id": wid, "reason": (
                    f"the accent wall leaves {0.0 if span is None else span[1] - span[0]:.2f} m between "
                    f"{', '.join(b[2] for b in blocked) or 'its ends'} (the panel needs {need:.2f} m)")})
                continue
            s0, s1 = span
            if s1 - s0 > MAX_WIDTH_M:
                s0 = min(max(span[0], centre - MAX_WIDTH_M / 2.0), span[1] - MAX_WIDTH_M)
                s1 = s0 + MAX_WIDTH_M
            gap = FLUTED["wall_gap"] if spec["kind"] == "fluted" else WAINSCOT["wall_gap"]
            a, u, n = face["a"], face["u"], face["n"]
            p = (a[0] + u[0] * s0 + n[0] * gap, a[1] + u[1] * s0 + n[1] * gap)
            q = (a[0] + u[0] * s1 + n[0] * gap, a[1] + u[1] * s1 + n[1] * gap)
            z0 = float(level["elevation"]) + float(room.get("floor_offset_m") or 0.0)
            if spec["kind"] == "fluted":
                z1 = _ceiling_z(level, (p, q, G.segment_midpoint(p, q))) - FLUTED["ceiling_gap"]
                if z1 - z0 < MIN_FLUTED_H_M:
                    skipped.append({"room_id": rid, "wall_id": wid, "reason": (
                        f"the ceiling over the accent wall is {z1 - z0:.2f} m high (a fluted panel needs "
                        f"{MIN_FLUTED_H_M} m): painted accent kept")})
                    continue
                depth = FLUTED["backing_t"] + FLUTED["slat_d"] + FLUTED["top_proud"]
            else:
                z1 = z0 + WAINSCOT["height"]
                depth = WAINSCOT["cap_d"]
            spec = dict(spec)
            if spec["kind"] == "wainscot":
                spec["colour"] = _accent_colour(style)
            plans.append({"room_id": rid, "level_id": level["id"], "wall_id": wid, "kind": spec["kind"], "spec": spec,
                          "p": [round(p[0], 4), round(p[1], 4)], "q": [round(q[0], 4), round(q[1], 4)],
                          "u": [round(u[0], 6), round(u[1], 6)], "n": [round(n[0], 6), round(n[1], 6)],
                          "z0": round(z0, 4), "z1": round(z1, 4), "width_m": round(s1 - s0, 3),
                          "depth_m": round(depth + gap, 4), "front_m": round(depth, 4),
                          "anchor_id": anchor["id"] if anchor else None,
                          "blocked": [b[2] for b in blocked if b[1] > s0 - 0.5 and b[0] < s1 + 0.5],
                          "reason": f"{spec['kind']} panel {s1 - s0:.2f} m wide on {look.get('reason') or wid}: "
                                    f"{why}"})
    return plans, skipped


def _plan_span(room: dict, wall: dict, level: dict, face: dict, spec: dict, why: str, look: dict, blocked: list,
               spans: list, span, centre: float, need: float, lo_a, hi_a, anchor: Optional[dict]):
    """The plan of a scheme kind (``slats``, ``headboard_panel``; 29 Oct 2026, UL119) on its free stretch, a reason
    (str) when it does not fit, None for the other kinds (planned as before)."""
    kind = spec.get("kind")
    if kind not in ("slats", "headboard_panel"):
        return None
    if span is None:
        return f"the anchor wall has no free stretch for the {kind.replace('_', ' ')}"
    s0, s1 = span
    z0 = float(level["elevation"]) + float(room.get("floor_offset_m") or 0.0)
    if kind == "slats":
        if s1 - s0 < max(MIN_WIDTH_M, need) - 1e-9:
            return (f"the anchor wall leaves {s1 - s0:.2f} m between {', '.join(b[2] for b in blocked) or 'its ends'} "
                    f"(the slat wall needs {max(MIN_WIDTH_M, need):.2f} m)")
        if s1 - s0 > SLATS["max_width"]:
            s0 = min(max(span[0], centre - SLATS["max_width"] / 2.0), span[1] - SLATS["max_width"])
            s1 = s0 + SLATS["max_width"]
        gap = FLUTED["wall_gap"]
        p, q, u, n = _ends(face, s0, s1, gap)
        z1 = _ceiling_z(level, (p, q, G.segment_midpoint(p, q))) - FLUTED["ceiling_gap"]
        if z1 - z0 < MIN_FLUTED_H_M:
            return f"the ceiling over the anchor wall is {z1 - z0:.2f} m high (a slat wall needs {MIN_FLUTED_H_M} m)"
        depth = FLUTED["backing_t"] + FLUTED["slat_d"] + FLUTED["top_proud"]
    else:
        width = (hi_a - lo_a if anchor is not None else 1.6) + 2.0 * HEADBOARD["extra_m"]
        lo, hi = centre - width / 2.0, centre + width / 2.0
        lo, hi = max(lo, s0), min(hi, s1)
        if hi - lo < max(MIN_WIDTH_M, (hi_a - lo_a + ANCHOR_MARGIN_M) if anchor is not None else 0.0) - 1e-9:
            return f"the bed wall leaves {hi - lo:.2f} m for the headboard panel"
        s0, s1 = lo, hi
        gap = HEADBOARD["wall_gap"]
        p, q, u, n = _ends(face, s0, s1, gap)
        ceil = _ceiling_z(level, (p, q, G.segment_midpoint(p, q)))
        z1 = z0 + min(HEADBOARD["height"], ceil - z0 - HEADBOARD["ceiling_gap"])
        if z1 - z0 < 0.8:
            return f"the ceiling over the bed wall leaves {ceil - z0:.2f} m (a headboard panel needs 1.1 m)"
        depth = HEADBOARD["ledge_d"]
    return {"room_id": room["id"], "level_id": level["id"], "wall_id": wall["id"], "kind": kind, "spec": dict(spec),
            "p": [round(p[0], 4), round(p[1], 4)], "q": [round(q[0], 4), round(q[1], 4)],
            "u": [round(u[0], 6), round(u[1], 6)], "n": [round(n[0], 6), round(n[1], 6)],
            "z0": round(z0, 4), "z1": round(z1, 4), "width_m": round(s1 - s0, 3),
            "depth_m": round(depth + gap, 4), "front_m": round(depth, 4),
            "anchor_id": anchor["id"] if anchor else None,
            "blocked": [b[2] for b in blocked if b[1] > s0 - 0.5 and b[0] < s1 + 0.5],
            "reason": f"{kind.replace('_', ' ')} {s1 - s0:.2f} m wide on {look.get('reason') or wall['id']}: {why}"}


def _ends(face: dict, s0: float, s1: float, gap: float):
    a, u, n = face["a"], face["u"], face["n"]
    p = (a[0] + u[0] * s0 + n[0] * gap, a[1] + u[1] * s0 + n[1] * gap)
    q = (a[0] + u[0] * s1 + n[0] * gap, a[1] + u[1] * s1 + n[1] * gap)
    return p, q, u, n


def plan_dining_walls(building: dict, level: dict, style: Optional[dict], taken: Optional[set] = None
                      ) -> tuple[list[dict], list[dict]]:
    """``(plans, skipped)``: the slat walls behind the dining tables of the level's rooms whose scheme names one
    (``room["scheme"]["dining_wall_at"]``: the wall, a point on it; K13), over the free stretch around the point (at
    most ``SLATS["max_width"]``), never on a wall a panel of the room takes already (``taken``: (room, wall))."""
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]]
    by_id = {w["id"]: w for w in walls}
    plans, skipped = [], []
    if (style or {}).get("room_schemes") in (False, "off", "none"):
        return plans, skipped
    for room in sorted((r for r in building.get("rooms") or [] if r.get("level_id") == level["id"]),
                       key=lambda r: str(r.get("id"))):
        at = ((room.get("scheme") or {}).get("dining_wall_at") if isinstance(room.get("scheme"), dict) else None)
        if not isinstance(at, dict) or not at.get("point"):
            continue
        wall = by_id.get(at.get("wall_id"))
        if wall is None:
            skipped.append({"room_id": room["id"], "reason": f"the dining wall {at.get('wall_id')} is not built"})
            continue
        if (room["id"], wall["id"]) in (taken or set()):
            skipped.append({"room_id": room["id"], "reason": f"the dining wall {wall['id']} holds the room's panel"})
            continue
        face = face_of(room, wall, walls)
        if face is None:
            skipped.append({"room_id": room["id"], "reason": f"no room edge along the dining wall {wall['id']}"})
            continue
        blocked = blocked_spans(face, wall, building, room)
        spans = free_spans(face["length"], blocked)
        centre = _station(face, at["point"])[0]
        span = next((sp for sp in spans if sp[0] - 1e-6 <= centre <= sp[1] + 1e-6), None)
        spec = {"kind": "slats", "wood": (FAMILY_FEATURE_WALLS.get(_family(style)) or
                                          FAMILY_FEATURE_WALLS["contemporary"]).get("wood") or "wood_veneer_oak",
                "backing": "dark", "slat_w": SLATS["slat_w"], "gap": SLATS["gap"]}
        why = f"the room's scheme: a full-height slat wall behind the dining table {at.get('table_id')} (K13)"
        plan = _plan_span(room, wall, level, face, spec, why, {"reason": f"the dining wall of {room['id']}"},
                          blocked, spans, span, centre, MIN_WIDTH_M + 0.6, None, None, None)
        if isinstance(plan, str) or plan is None:
            skipped.append({"room_id": room["id"], "reason": plan or "no slat wall"})
            continue
        plan["dining"] = True
        plans.append(plan)
    return plans, skipped


# --------------------------------------------------------------------------
# The panel as boxes (pure)
# --------------------------------------------------------------------------

def _box(plan: dict, s0: float, s1: float, d0: float, d1: float, z0: float, z1: float, key: str) -> tuple:
    """A box of the panel's frame: along the face ``s0..s1`` from ``p``, ``d0..d1`` into the room, ``z0..z1``."""
    (px, py), (ux, uy), (nx, ny) = plan["p"], plan["u"], plan["n"]
    sm, dm = (s0 + s1) / 2.0, (d0 + d1) / 2.0
    centre = (px + ux * sm + nx * dm, py + uy * sm + ny * dm, (z0 + z1) / 2.0)
    return centre, (s1 - s0, d1 - d0, z1 - z0), math.degrees(math.atan2(uy, ux)), key


def slat_layout(width: float, spec: dict) -> list[tuple[float, float]]:
    """``[(s0, s1)]`` of the fluted panel's slats between its end boards (pure): ``slat_w`` wide, as many as fit at
    a pitch of ``slat_w + gap``, the gaps evened out."""
    sw = float(spec.get("slat_w") or FLUTED["slat_w"])
    gap = float(spec.get("gap") or FLUTED["gap"])
    end = FLUTED["end_w"]
    inner = width - 2.0 * end
    n = max(1, int((inner + gap * 0.5) // (sw + gap)))
    g = (inner - n * sw) / n
    return [(end + g / 2.0 + k * (sw + g), end + g / 2.0 + k * (sw + g) + sw) for k in range(n)]


def panel_boxes(plan: dict) -> list[tuple]:
    """The boxes of a planned panel (module docstring): keys ``wood`` (slats, end boards, top trim), ``backing``,
    ``plinth`` (fluted); ``paint`` (wainscot board, mouldings, cap rail)."""
    w = float(plan["width_m"])
    z0, z1 = float(plan["z0"]), float(plan["z1"])
    spec = plan.get("spec") or {}
    out = []
    if plan["kind"] == "headboard_panel":          # 29 Oct 2026 (R32): boards on a dark backing, a ledge on top
        k = HEADBOARD
        bt, ft = k["backing_t"], k["board_t"]
        top = z1 - k["ledge_t"]
        out.append(_box(plan, 0.0, w, 0.0, bt, z0 + 0.0005, top, "backing"))
        n = max(2, int(k["boards"]))
        bh = (top - z0 - 0.001 - (n - 1) * k["gap"]) / n
        for i in range(n):
            b0 = z0 + 0.001 + i * (bh + k["gap"])
            out.append(_box(plan, 0.0005, w - 0.0005, bt, bt + ft, b0, b0 + bh, "wood"))
        out.append(_box(plan, 0.0, w, 0.0, k["ledge_d"], top, z1, "wood"))
        return out
    if plan["kind"] in ("fluted", "slats"):
        f = FLUTED
        bt, sd = f["backing_t"], f["slat_d"]
        zb, zt = z0 + f["plinth_h"], z1 - f["top_h"]
        out.append(_box(plan, 0.0, w, 0.0, bt, zb, zt, "backing"))
        out.append(_box(plan, 0.0, w, 0.0, bt + sd - f["plinth_recess"], z0 + 0.001, zb, "plinth"))
        out.append(_box(plan, 0.0, w, 0.0, bt + sd + f["top_proud"], zt, z1, "wood"))
        for s0, s1 in ((0.0, f["end_w"]), (w - f["end_w"], w)):
            out.append(_box(plan, s0, s1, 0.0, bt + sd, zb + 0.0005, zt - 0.0005, "wood"))
        for s0, s1 in slat_layout(w, spec):
            out.append(_box(plan, s0, s1, bt + 0.0005, bt + sd, zb + 0.0005, zt - 0.0005, "wood"))
        return out
    k = WAINSCOT
    bt, md = k["board_t"], k["mould_d"]
    top = z1 - k["cap_h"]
    out.append(_box(plan, 0.0, w, 0.0, bt, z0 + 0.0005, top, "paint"))
    out.append(_box(plan, 0.0, w, 0.0, k["cap_d"], top, z1, "paint"))
    gap, mw = k["gap"], k["mould_w"]
    n = max(1, int(round((w - gap) / (k["panel_w"] + gap))))
    fw = (w - gap * (n + 1)) / n
    zb, zt = z0 + k["bottom"], top - k["top_gap"]
    if fw > 2.5 * mw and zt - zb > 2.5 * mw:
        for i in range(n):
            s0 = gap + i * (fw + gap)
            s1 = s0 + fw
            out.append(_box(plan, s0, s0 + mw, bt, bt + md, zb, zt, "paint"))
            out.append(_box(plan, s1 - mw, s1, bt, bt + md, zb, zt, "paint"))
            out.append(_box(plan, s0 + mw, s1 - mw, bt, bt + md, zb, zb + mw, "paint"))
            out.append(_box(plan, s0 + mw, s1 - mw, bt, bt + md, zt - mw, zt, "paint"))
    return out


# --------------------------------------------------------------------------
# Wall items stand off a panel
# --------------------------------------------------------------------------

def standoff_decor(decor: list[dict], plans: list[dict]) -> tuple[list[dict], list[str]]:
    """``(decor, notes)``: wall art, mirrors and clocks whose wall point lies on a panel (its face line, within its
    width, and below the panel's top when the panel is a dado) moved off it by the panel's depth (copies; the others
    unchanged)."""
    out, notes = [], []
    for item in decor or []:
        if item.get("type") not in STANDOFF_TYPES or not item.get("wall_point"):
            out.append(item)
            continue
        moved = None
        for plan in plans:
            if (item.get("level_id") and plan.get("level_id") and item["level_id"] != plan["level_id"]) or \
                    (item.get("room_id") and item["room_id"] != plan["room_id"]):
                continue                                   # stacked floors share their x and y
            p, u, n = plan["p"], plan["u"], plan["n"]
            wx, wy = float(item["wall_point"][0]), float(item["wall_point"][1])
            s = (wx - p[0]) * u[0] + (wy - p[1]) * u[1]
            d = (wx - p[0]) * n[0] + (wy - p[1]) * n[1]
            if abs(d) > STANDOFF_REACH_M or not -0.05 <= s <= float(plan["width_m"]) + 0.05:
                continue
            bottom = item.get("bottom_m")
            if isinstance(item.get("min_bottom_m"), (int, float)):
                bottom = max(float(bottom or 0.0), float(item["min_bottom_m"]))
            if plan["kind"] in LOW_KINDS and isinstance(bottom, (int, float)) and \
                    float(bottom) >= float(plan["z1"]) - float(plan["z0"]) - 1e-6:
                continue                                   # hung above the dado or headboard panel: on the wall
            off = float(plan.get("front_m", plan["depth_m"])) - d     # to the panel's front (from its base line)
            if off <= 0.0:
                continue
            new = dict(item, wall_point=[round(wx + n[0] * off, 4), round(wy + n[1] * off, 4)],
                       feature_wall_standoff_m=round(off, 4))
            if item.get("center") and len(item["center"]) >= 2:
                c = list(item["center"])
                c[0], c[1] = round(float(c[0]) + n[0] * off, 4), round(float(c[1]) + n[1] * off, 4)
                new["center"] = c
            moved = new
            notes.append(f"{item.get('type')} {item.get('id')}: {off * 100:.1f} cm off the {plan['kind']} panel of "
                         f"{plan['room_id']}")
            break
        out.append(moved or item)
    return out, notes


def finish_depth_at(room: Optional[dict], point, z: float) -> float:
    """How far the room's built feature panel (``room["feature_wall"]``) stands off the wall at a plan ``point`` on
    the wall face and height ``z`` (pure): its depth there, 0 elsewhere (a wall sconce on a panelled head wall)."""
    rec = (room or {}).get("feature_wall") if isinstance((room or {}).get("feature_wall"), dict) else None
    if not rec or not all(k in rec for k in ("p", "u", "n", "width_m", "depth_m", "z0", "z1")):
        return 0.0
    p, u, n = rec["p"], rec["u"], rec["n"]
    s = (float(point[0]) - p[0]) * u[0] + (float(point[1]) - p[1]) * u[1]
    d = (float(point[0]) - p[0]) * n[0] + (float(point[1]) - p[1]) * n[1]
    if abs(d) > STANDOFF_REACH_M or not -0.05 <= s <= float(rec["width_m"]) + 0.05:
        return 0.0
    if not float(rec["z0"]) - 1e-6 <= float(z) <= float(rec["z1"]) + 1e-6:
        return 0.0
    return max(0.0, float(rec.get("front_m", rec["depth_m"])) - d)


def summary(plan: dict) -> dict:
    """The record of a built panel on its room (``feature_wall``; the lighting rig's sconce and Argus read it)."""
    return {k: plan[k] for k in ("kind", "wall_id", "p", "q", "u", "n", "z0", "z1", "width_m", "depth_m",
                                 "front_m", "anchor_id") if k in plan}


# --------------------------------------------------------------------------
# bpy
# --------------------------------------------------------------------------

def _materials(library, plan: dict) -> dict:
    """``{key: material}`` of a panel (bpy)."""
    try:
        from wenart.style import vocabulary as V
        fm = V.FURNITURE_MATERIALS
    except Exception:  # noqa: BLE001
        fm = {}
    spec = plan.get("spec") or {}
    if plan["kind"] == "wainscot":
        return {"paint": library.get("painted_wood_white", None, colour=spec.get("colour"))}
    wood_slug = spec.get("wood") or "wood_veneer_oak"
    wood = library.get(wood_slug, (fm.get(wood_slug) or {}).get("asset"))
    backing = wood if spec.get("backing") == "wood" else library.get(
        "fabric_linen", (fm.get("fabric_linen") or {}).get("asset"), colour="charcoal")
    return {"wood": wood, "backing": backing, "plinth": library.get("lacquer_dark")}


def build_feature_walls(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                        assumed: list, warnings: list) -> list[dict]:
    """Build the level's panels (module docstring); returns the plans built (each room records ``feature_wall``)."""
    from wenart.blender import common, geom2d

    dressing = building.get("dressing") if isinstance(building.get("dressing"), dict) else {}
    plans, skipped = plan_feature_walls(building, level, style, dressing.get("rooms"))
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    for s in skipped:
        if s["room_id"] in rooms:
            rooms[s["room_id"]].pop("feature_wall", None)
            rooms[s["room_id"]]["feature_wall_skipped"] = s["reason"]
    # 29 Oct 2026 (K13): the slat walls behind the dining tables the rooms' schemes name
    dining, dining_skipped = plan_dining_walls(building, level, style, {(p["room_id"], p["wall_id"]) for p in plans})
    for s in dining_skipped:
        if s["room_id"] in rooms:
            rooms[s["room_id"]]["dining_wall_skipped"] = s["reason"]
    plans = plans + dining
    built = []
    for plan in plans:
        boxes = panel_boxes(plan)
        if not boxes:
            continue
        mats = _materials(library, plan)
        keys = list(dict.fromkeys(b[3] for b in boxes))
        parts, slots = [], []
        for centre, size, rot, key in boxes:
            v, f = geom2d.box(centre, size, rot)
            parts.append((v, f))
            slots += [keys.index(key)] * len(f)
        verts, faces = geom2d.merge(parts)
        name = f"feature_wall_{plan['room_id']}" + ("_dining" if plan.get("dining") else "")
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="wall",
                                    status="assumed", materials=[mats[k] for k in keys], face_material_indices=slots)
        ob.pass_index = 0
        bevel = ob.modifiers.new(name="bevel", type="BEVEL")
        bevel.width = FLUTED["bevel_m"] if plan["kind"] in ("fluted", "slats") else WAINSCOT["bevel_m"]
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
        record = dict(summary(plan), reason=plan["reason"], blocked=plan["blocked"], spec=plan["spec"],
                      boxes=len(boxes), materials={k: mats[k].name for k in keys}, lesson=CHECK)
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "wall", "status": "assumed", "level_id": level["id"],
            "element_id": plan["room_id"], "parent": plan["room_id"], "room_id": plan["room_id"], "evidence": [],
            "material": mats[keys[0]].name, "textured": library.textured(mats[keys[0]]), "pass_index": 0,
            "detail": "feature_wall", "feature_wall": record,
            "assumed": {"detail": "feature_wall", "reason": plan["reason"]}})
        assumed.append({"object": ob.name, "field": "feature_wall", "value": f"{plan['kind']} {plan['width_m']} m",
                        "reason": plan["reason"], "parent": plan["room_id"], "kind": "feature_wall"})
        if plan["room_id"] in rooms and plan.get("dining"):
            rooms[plan["room_id"]]["dining_wall"] = summary(plan)
            rooms[plan["room_id"]].pop("dining_wall_skipped", None)
        elif plan["room_id"] in rooms:
            rooms[plan["room_id"]]["feature_wall"] = summary(plan)
            rooms[plan["room_id"]].pop("feature_wall_skipped", None)
        built.append(plan)
    return built
