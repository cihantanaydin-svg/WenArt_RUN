"""Facade articulation of the whole building (docs/milestone11.md §1.1 E10, §4.1 X8, §7).

What: ``articulation_plan(...)`` lays out what turns a plain rendered box into a facade: a plinth band at the
foot of the walls that meet the ground, a slab band at every upper floor, a coping on a flat roof's parapet,
and, for the classic styles, stone surrounds around the windows (the modern styles keep the reveal the wall
thickness already gives). ``build_articulation`` (bpy) makes one object per kind and level.

Why: real02's facades were one plain render material with long blank walls (E10); the documents draw none of
these details, so they come from the style (``style.family``) and are listed as ``assumed`` (inferred from the
style) in the scene manifest.

How: pure Python on the level outlines (``geom2d.wall_outline``, the outer wall faces): every outline edge
gets a thin box ``proud`` metres in front of its face, cut where a door, a window or a light well / front court
crosses the band (``_spans``). The looks come from ``ARTICULATION`` per style family and the resolved outside
looks (``exterior.resolve_looks``; the agent's ``plinth`` / ``cornice`` / ``surround`` material slots override
them).

Milestone 13 (docs/milestone13.md §13.2, track T6; §1.7: "a box with bands"): the facade kit (``facade_kit``), added
to the plan only where the documents or the room types imply it, every box ``inferred`` with its reason: window
reveals (a thin frame at the outer face of every window of the modern families, which get no surround), gutters
along the roof's eaves edges and downpipes at their corners (a pitched roof drawn in the documents), an entrance
canopy and a pair of wall lights at every entrance door at grade (``site.entrances``), and a guard rail in front of
an upper-floor outside door that opens onto no balcony or terrace room (a door drawn there implies one).
``KIT`` holds the sizes; the looks are ``KIT_LOOKS`` (the agent's material slots of the same names override them).

Facade scheme (user request of 24 Oct 2026: the outside walls "seem blank concrete"): when no drawing and no brief
names the facade, the style family gives it a designed default (``FACADE_SCHEMES``, ``scheme_faces``): the main walls
in render of the family's facade colour (``exterior.resolve_looks``), the walls of the basement levels in the family's
base cladding (stone, brick), and a band of the family's accent cladding framing the main entrance door, from the
entrance floor to the floor above (``ACCENT``). Every face is ``inferred`` with its reason; the plinth band takes the
base cladding too. A face may carry a ``span`` (two plan points on its wall): only the stretch between them takes it.

29 Oct 2026 (user on real06: "Outside wall texture can be changed"; the judge: "a flat white box with no material
rhythm"): a house of two or more storeys above the ground takes the family's ``upper`` cladding on its top storey
(timber over a rendered ground floor for the Scandinavian, Japandi, modern and rustic families, fibre-cement panels
for the industrial one); the families whose look is one render (minimal, classic, Mediterranean) keep it.

1 Nov 2026 (lesson UL235, user on a sloped-site house, the stacked stone on one wall of its lowest floor: "this was nice
wall it can be used all around the same floor"): one cladding all round a floor (``storey_claddings``). A cladding
(any finish that is not a render: stone, brick, wood, fibre-cement panels; ``is_cladding``) that the facade puts on an
outside wall of a floor goes on every outside wall of that floor, around the corners. It comes from an inferred facade
face on the whole of some of the floor's outside walls, or from the plinth: on a sloped site the raised base runs from
the ground up to the floor above, so where the ground lies low it clads a lower floor's wall from the ground to the next
floor (``plinth_storeys``: at least ``STOREY["min_height_m"]`` of stone on at least ``STOREY["min_length_m"]`` of the
wall) while the floor's other walls stayed render. The other outside walls of that floor take the same look as an
inferred face (``storey_cladding``, with the reason and the wall it was seen on). What stays: the openings (the glazing
stays glazing), a wall the documents or the brief give a face of its own, a wall that already carries a whole-wall
cladding, the accent band at the entrance (a span the scheme sets on purpose), a facade the documents, the brief or the
style name (the plinth then stays a base), a main facade that is a cladding already, and every other floor: each floor
follows its own faces.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# Per style family: the plinth look and height, whether the windows get surrounds (else reveals).
ARTICULATION = {
    "default": {"plinth": "stone_wall_ledgestone", "plinth_colour": None, "surround": None},
    "classic": {"plinth": "stone_cladding", "plinth_colour": None, "surround": "limestone"},
    "mediterranean": {"plinth": "stone_cladding", "plinth_colour": None, "surround": "limestone"},
    "rustic": {"plinth": "stone_wall_rubble", "plinth_colour": None, "surround": "limestone"},
}
# The facade scheme per style family (user request of 24 Oct 2026): the main walls' render colour, the base cladding
# of the basement levels and the accent cladding around the main entrance (None: no accent). Vocabulary slugs and
# colour names of wenart/style; a family not listed takes "default".
FACADE_SCHEMES = {
    "default": {"main": ("render", "off white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding",
                "upper": "wood_cladding"},
    "modern": {"main": ("render", "off white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding",
               "upper": "wood_cladding"},
    "modern minimal": {"main": ("render", "white"), "base": "stone_wall_slate", "accent": "wood_cladding",
                       "upper": None},
    "minimal": {"main": ("render", "white"), "base": "stone_wall_slate", "accent": "wood_cladding", "upper": None},
    "scandinavian": {"main": ("render", "white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding",
                     "upper": "wood_cladding"},
    "japandi": {"main": ("render", "off white"), "base": "stone_wall_slate", "accent": "wood_cladding",
                "upper": "wood_cladding"},
    "industrial": {"main": ("render", "light grey"), "base": "brick_red", "accent": None, "upper": "fibre_cement"},
    "mediterranean": {"main": ("render", "cream"), "base": "stone_wall_ashlar", "accent": None, "upper": None},
    "classic": {"main": ("render", "ivory"), "base": "stone_wall_ashlar", "accent": None, "upper": None},
    "rustic": {"main": ("render", "cream"), "base": "stone_wall_rubble", "accent": "wood_cladding",
               "upper": "wood_cladding"},
}
UPPER = {"min_storeys": 2}         # storeys above the ground for the top storey's cladding
ACCENT = {"margin_m": 1.0, "min_width_m": 2.4}      # the accent band: the door plus 1 m on each side, >= 2.4 m wide
DIMENSIONS = {"plinth_height": 0.45, "plinth_below": 0.05, "proud": 0.025, "band_height": 0.20, "band_proud": 0.03,
              "coping_height": 0.06, "coping_proud": 0.04, "surround_width": 0.12, "surround_proud": 0.03,
              "min_span": 0.15}
# 1 Nov 2026 (UL235): the plinth clads a floor's wall when it reaches that floor's top (the floor above, within
# top_tol_m) and shows at least min_height_m over the ground on at least min_length_m of the wall; a plinth stretch
# belongs to a floor's wall when its edge lies within edge_tol_m of that floor's outline
STOREY = {"min_height_m": 1.0, "min_length_m": 1.0, "top_tol_m": 0.1, "edge_tol_m": 0.3}
RENDER_KINDS = ("plaster",)        # vocabulary kinds of a render finish; any other kind outside is a cladding
NAMED_SOURCES = ("documents", "brief", "style")     # a facade look named by them keeps the plinth a base


# Milestone 13 (T6): the facade kit sizes (metres) and looks (vocabulary slugs; a colour name or None).
KIT = {"reveal_width": 0.06, "reveal_proud": 0.015, "gutter_w": 0.12, "gutter_h": 0.10, "gutter_drop": 0.02,
       "downpipe": 0.10, "downpipe_every_m": 12.0, "downpipe_end_m": 0.4, "downpipe_both_ends_m": 4.0,
       "pipe_search_m": 3.0, "pipe_search_step_m": 0.1, "pipe_wall_tol_m": 0.15, "pipe_min_gap_m": 1.5, "eaves_tol": 0.15,
       # 26 Oct 2026 (downpipe_plan): building-wide pipes at the corners, >= pipe_gap_m apart, a gutter drains at most
       # max_drain_m to a pipe, one end of a run up to single_end_m, at most one pipe per area_per_pipe_m2 of roof
       "pipe_gap_m": 3.0, "max_drain_m": 12.0, "single_end_m": 10.0, "area_per_pipe_m2": 50.0,
       "canopy_depth": 1.0, "canopy_thick": 0.08, "canopy_side": 0.3, "canopy_above": 0.25,
       "light_w": 0.12, "light_d": 0.08, "light_h": 0.22, "light_z": 2.1, "light_offset": 0.35,
       "guard_height": 1.0, "guard_bar": 0.04, "guard_min_drop": 1.0, "guard_side": 0.05,
       # 26 Oct 2026: a guard reaches guard_top over its floor where an opening's bottom is under guard_sill
       "guard_top": 1.10, "guard_sill": 0.85, "guard_channel": 0.06, "guard_channel_h": 0.09, "guard_cap": 0.03,
       "guard_glass_t": 0.012}
KIT_LOOKS = {
    "reveal": ("render", "white", "window reveal frame at the outer face (modern family; not drawn)"),
    "gutter": ("aluminium_anthracite", None, "gutter along the eaves (a pitched roof is drawn; the gutter is not)"),
    "downpipe": ("aluminium_anthracite", None, "downpipe at the eaves corners (not drawn)"),
    # 30 Oct 2026 (lesson UL171, user: "There should be better solution than these things in the house entrance
    # points make it make sense"; a flat white slab stuck out of the wall, one just under the eaves): a real canopy
    "canopy": ("aluminium_anthracite", None, "entrance canopy over the entrance door: a slim anthracite metal canopy "
                                             "with a deeper front fascia as its drip edge (the door is drawn; the "
                                             "canopy is not)"),
    "canopy_soffit": ("wood_cladding", None, "the entrance canopy's wood soffit (not drawn)"),
    "canopy_rod": ("steel_black", None, "the entrance canopy's two tie rods to wall plates above it (not drawn)"),
    "wall_light": ("steel_black", None, "wall light beside the entrance door (not drawn)"),
    "railing": ("steel_brushed", None, "guard's metal (rails, posts, bars or a glass channel) in front of an opening "
                                        "over a drop with no balcony (not drawn)"),
    "guard_glass": ("glass_guard", None, "glass guard in front of an opening over a drop with no balcony (not drawn)"),
}
KIT_KINDS = tuple(KIT_LOOKS)


def scheme_of(style: Optional[dict]) -> dict:
    """The facade scheme of the style's family (``FACADE_SCHEMES``), with ``family``."""
    fam = str((style or {}).get("family") or "").lower()
    return dict(FACADE_SCHEMES.get(fam) or FACADE_SCHEMES["default"], family=fam or "default")


def main_entrance(building: dict, levels: Sequence[dict]) -> Optional[dict]:
    """The main entrance door of the building (``site.entrances``: the one marked ``main``, else the first at grade
    on the lowest level that has one), as its opening dict, or None."""
    ids = {lv["id"] for lv in levels}
    recs = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
            and r.get("level_id") in ids and not r.get("into_air") and not r.get("below_ground")]
    if not recs:
        return None
    order = {lv["id"]: float(lv["elevation"]) for lv in levels}
    rec = next((r for r in recs if r.get("main")), None) or min(recs, key=lambda r: (order[r["level_id"]],
                                                                                       float(r.get("rise") or 0.0)))
    return next((o for o in building.get("openings") or [] if o.get("id") == rec.get("door_id")), None)


def scheme_faces(building: dict, style: Optional[dict], levels: Sequence[dict]) -> list[dict]:
    """The inferred facade faces of the style's scheme (pure; the caller asks only when no drawing and no brief name
    the facade): the accent band around the main entrance first (``span`` and ``z_range``), then the base cladding
    of every basement level. Each face: ``material``, ``colour``, ``side`` all, ``level_id`` / ``wall_id``, ``source``
    ``inferred``, ``inferred`` True and its ``reason``."""
    sch = scheme_of(style)
    faces: list[dict] = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    door = main_entrance(building, order) if sch.get("accent") else None
    wall = next((w for w in building.get("walls") or [] if door and w.get("id") == door.get("wall_id")), None)
    if door is not None and wall is not None:
        (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length > 1e-6:
            ux, uy = (x1 - x0) / length, (y1 - y0) / length
            cx, cy = door["center"][:2]
            t = (cx - x0) * ux + (cy - y0) * uy
            half = max(float(door.get("width") or 0.9) / 2.0 + ACCENT["margin_m"], ACCENT["min_width_m"] / 2.0)
            t0, t1 = max(0.0, t - half), min(length, t + half)
            lv = next(lv for lv in order if lv["id"] == wall.get("level_id"))
            above = [float(x["elevation"]) for x in order if float(x["elevation"]) > float(lv["elevation"]) + 0.5]
            z1 = min(above) if above else float(lv["elevation"]) + float(lv.get("height") or 3.0)
            faces.append({"material": sch["accent"], "colour": None, "side": "all", "wall_id": wall["id"],
                          "span": [[x0 + ux * t0, y0 + uy * t0], [x0 + ux * t1, y0 + uy * t1]],
                          "z_range": [float(lv["elevation"]) - 0.5, z1], "source": "inferred", "inferred": True,
                          "reason": f"facade scheme ({sch['family']}): {sch['accent']} framing the main entrance "
                                    f"{door['id']} ({t1 - t0:.1f} m wide; not drawn)"})
    for lv in order:
        if str(lv.get("kind") or "") == "basement":
            faces.append({"material": sch["base"], "colour": None, "side": "all", "level_id": lv["id"],
                          "source": "inferred", "inferred": True,
                          "reason": f"facade scheme ({sch['family']}): {sch['base']} on the basement level "
                                    f"{lv['id']} (not drawn)"})
    top = upper_level(sch, order)
    if top is not None:
        faces.append({"material": sch["upper"], "colour": None, "side": "all", "level_id": top["id"],
                      "source": "inferred", "inferred": True, "upper": True,
                      "reason": f"facade scheme ({sch['family']}): {sch['upper']} on the top storey {top['id']} over "
                                f"the rendered floors below (not drawn)"})
    return faces


def storeys(levels: Sequence[dict]) -> list[dict]:
    """The storeys above the ground, lowest first: the levels that are neither a basement nor a roof or open-air
    level (pure)."""
    return sorted((lv for lv in levels if str(lv.get("kind") or "floor") not in ("basement", "roof", "site", "terrain")),
                  key=lambda lv: float(lv["elevation"]))


def upper_level(scheme: dict, levels: Sequence[dict]) -> Optional[dict]:
    """The storey that takes the scheme's ``upper`` cladding: the top one of at least ``UPPER["min_storeys"]``
    storeys above the ground, None for a family without one (pure)."""
    up = storeys(levels)
    return up[-1] if scheme.get("upper") and len(up) >= UPPER["min_storeys"] else None


def on_span(point, span, tol: float = 1e-3) -> bool:
    """Whether the plan ``point`` projects onto the segment ``span`` (``[[x0, y0], [x1, y1]]``)."""
    (x0, y0), (x1, y1) = span[0][:2], span[1][:2]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-9:
        return False
    t = ((float(point[0]) - x0) * (x1 - x0) + (float(point[1]) - y0) * (y1 - y0)) / length
    return -tol <= t <= length + tol


def family_rules(style: Optional[dict]) -> dict:
    fam = str((style or {}).get("family") or "").lower()
    return dict(ARTICULATION["default"], **ARTICULATION.get(fam, {}), family=fam or None)


def band_colour(facade_look: dict) -> str:
    """The slab band's colour: white on a coloured facade, light grey on a white one (a band of the facade's own
    colour only reads through its shadow)."""
    colour = str((facade_look or {}).get("colour") or "").lower()
    return "light grey" if colour in ("", "white", "off white", "warm white", "walls") else "white"


def _spans(length: float, cuts: Sequence[tuple[float, float]], min_span: float) -> list[tuple[float, float]]:
    """The stretches of ``[0, length]`` outside ``cuts`` (each ``(t0, t1)`` in metres), at least ``min_span``."""
    out, t = [], 0.0
    for a, b in sorted(cuts):
        if t >= length:
            break
        if min(a, length) > t + min_span:
            out.append((t, min(a, length)))
        t = max(t, b)
    if length - t > min_span:
        out.append((t, length))
    return out


def _edge_cuts(p, q, items: Sequence[dict], z0: float, z1: float, tol: float = 0.35) -> list[tuple[float, float]]:
    """Along the edge ``p``-``q`` the stretches that ``items`` (``{"centre", "half", "bottom", "top"}``, or
    ``{"polygon"}`` for a light well / court reaching the wall) cross between heights ``z0`` and ``z1``."""
    length = G.distance(p, q)
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    out = []
    for it in items:
        if "polygon" in it:
            near = [((x - p[0]) * ux + (y - p[1]) * uy) for x, y in it["polygon"]
                    if abs((x - p[0]) * -uy + (y - p[1]) * ux) <= tol]
            if near:
                out.append((min(near) - 0.05, max(near) + 0.05))
            continue
        c = it["centre"]
        if abs((c[0] - p[0]) * -uy + (c[1] - p[1]) * ux) > tol or it["top"] <= z0 or it["bottom"] >= z1:
            continue
        t = (c[0] - p[0]) * ux + (c[1] - p[1]) * uy
        out.append((t - it["half"] - 0.03, t + it["half"] + 0.03))
    return out


BAND_CLEAN_M = 0.10      # 4 Nov 2026 (UL310): jogs and notches of the outline under 2 x this are straightened for the bands


def band_outline(outline) -> list:
    """4 Nov 2026 (lesson UL310, user on real10: "Make these details better", the floor bands): the outline a floor band
    runs on: the jogs and notches under ``2 x BAND_CLEAN_M`` of the outer walls (walls of different thickness, frame
    pieces) straightened (closed by a mitred grow and shrink), so a band runs on in one piece instead of breaking into
    short boxes with ends standing out as loose blocks; the outline itself without shapely."""
    try:
        from shapely.geometry import Polygon
    except ImportError:
        return outline
    poly = Polygon(outline).buffer(0)
    if poly.is_empty:
        return outline
    clean = poly.buffer(BAND_CLEAN_M, join_style=2, mitre_limit=5.0).buffer(-BAND_CLEAN_M, join_style=2,
                                                                         mitre_limit=5.0).simplify(0.002)
    if clean.is_empty:
        return outline
    if clean.geom_type != "Polygon":
        clean = max(clean.geoms, key=lambda g: g.area)
    pts = _drop_jogs(geom2d.ccw([tuple(q) for q in list(clean.exterior.coords)[:-1]]), 2.0 * BAND_CLEAN_M)
    return [[round(x, 4), round(y, 4)] for x, y in pts]


def _drop_jogs(pts: list, tol: float) -> list:
    """A counter-clockwise outline with its steps under ``tol`` gone (pure): a short edge between two parallel edges
    running the same way is a jog; the inner of the two moves out onto the outer one's line."""
    pts = [tuple(q) for q in pts]
    for _ in range(len(pts)):
        n = len(pts)
        if n < 5:
            break
        changed = False
        for i in range(n):
            a, b, c, d = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
            bc, ab, cd = G.distance(b, c), G.distance(a, b), G.distance(c, d)
            if bc >= tol or ab <= bc or cd <= bc or ab < 1e-9 or cd < 1e-9:
                continue
            u1 = ((b[0] - a[0]) / ab, (b[1] - a[1]) / ab)
            u2 = ((d[0] - c[0]) / cd, (d[1] - c[1]) / cd)
            if u1[0] * u2[0] + u1[1] * u2[1] < math.cos(math.radians(5.0)):
                continue
            nx, ny = u1[1], -u1[0]                                   # outward of a counter-clockwise outline
            s1, s2 = a[0] * nx + a[1] * ny, c[0] * nx + c[1] * ny
            if s1 >= s2:                                             # cd is inner: onto ab's line
                k = s1 - s2
                c, d = (c[0] + nx * k, c[1] + ny * k), (d[0] + nx * k, d[1] + ny * k)
                pts[(i + 1) % n], pts[(i + 2) % n] = c, d
            else:
                k = s2 - s1
                a, b = (a[0] + nx * k, a[1] + ny * k), (b[0] + nx * k, b[1] + ny * k)
                pts[i - 1], pts[i] = a, b
            changed = True
            break
        if not changed:
            break
        # drop repeated and collinear points
        out = []
        for q in pts:
            if not out or G.distance(out[-1], q) > 1e-6:
                out.append(q)
        if len(out) > 1 and G.distance(out[0], out[-1]) <= 1e-6:
            out.pop()
        keep = []
        for i, q in enumerate(out):
            a, c = out[i - 1], out[(i + 1) % len(out)]
            cross = (q[0] - a[0]) * (c[1] - q[1]) - (q[1] - a[1]) * (c[0] - q[0])
            if abs(cross) > 1e-9 * max(1.0, G.distance(a, c)):
                keep.append(q)
        pts = keep
    return pts


PIER_FRONT_MAX_M = 0.9    # 4 Nov 2026 (user on real10: "all these details ... not good enough"): a pilaster's face ...
PIER_DEPTH_MAX_M = 0.6    # ... standing this far out of the facade at most ...
BAND_STUB_M = 0.25        # ... and any other outline edge this short gets no band piece (no knots on the facade)


def _turn(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])


def pier_edges(pts: list) -> set:
    """The edges of a counter-clockwise outline that belong to a pilaster (pure): a front of at most
    ``PIER_FRONT_MAX_M`` between two sides of at most ``PIER_DEPTH_MAX_M`` square to it, standing out (both of the
    front's corners convex, the sides' outer corners concave). A floor band dies into a pilaster's sides instead of
    wrapping it in short pieces, so the pilaster runs on uninterrupted (real10: the knots at every band and pilaster)."""
    n = len(pts)
    out: set = set()
    if n < 6:
        return out
    L = [G.distance(pts[i], pts[(i + 1) % n]) for i in range(n)]
    for i in range(n):
        f, s1, s2 = i, (i - 1) % n, (i + 1) % n
        if not (L[f] <= PIER_FRONT_MAX_M and L[s1] <= PIER_DEPTH_MAX_M and L[s2] <= PIER_DEPTH_MAX_M):
            continue
        a, b, c, d = pts[s1], pts[f], pts[s2], pts[(i + 2) % n]
        before, after = pts[(i - 2) % n], pts[(i + 3) % n]
        if _turn(a, b, c) > 0 and _turn(b, c, d) > 0 and _turn(before, a, b) < 0 and _turn(c, d, after) < 0:
            u = ((c[0] - b[0]) / max(L[f], 1e-9), (c[1] - b[1]) / max(L[f], 1e-9))
            v = ((b[0] - a[0]) / max(L[s1], 1e-9), (b[1] - a[1]) / max(L[s1], 1e-9))
            if abs(u[0] * v[0] + u[1] * v[1]) < 0.2:                   # the sides square to the front
                out |= {s1, f, s2}
    return out


def _band_boxes(outline, z0: float, z1: float, proud: float, items, kind: str, level_id: Optional[str],
                min_span: float = DIMENSIONS["min_span"], inset: float = 0.0, piers: bool = False) -> list[dict]:
    """One box per uncut stretch of every outline edge: ``proud`` in front of the face, from ``z0`` to ``z1``;
    ``inset`` (4 Nov 2026): the box reaches this far behind the face line too (into the wall, where a straightened
    jog lets the wall step back), so the band never floats. ``piers`` (4 Nov 2026): no piece on a pilaster
    (``pier_edges``) nor on an edge under ``BAND_STUB_M``: the band dies into the pilaster's sides."""
    out = []
    pts = geom2d.ccw(outline)
    n = len(pts)
    skip = pier_edges(pts) if piers else set()
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        length = G.distance(p, q)
        if length < min_span or i in skip or (piers and length < BAND_STUB_M):
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux                                       # counter-clockwise outline: right of the edge is out
        for a, b in _spans(length, _edge_cuts(p, q, items, z0, z1), min_span):
            # the band runs on past convex corners by its own depth, so two bands meet without a slit
            a2 = a - proud if a <= 1e-9 else a
            b2 = b + proud if b >= length - 1e-9 else b
            mid = ((a2 + b2) / 2.0)
            off = (proud - inset) / 2.0
            out.append({"kind": kind, "level_id": level_id,
                        "center": [p[0] + ux * mid + nx * off, p[1] + uy * mid + ny * off, (z0 + z1) / 2.0],
                        "size": [b2 - a2, proud + inset, z1 - z0], "rotation_deg": math.degrees(math.atan2(uy, ux))})
    return out


def opening_items(building: dict, level: dict, outline, levels_above: bool) -> list[dict]:
    """The doors and windows of a level as band cuts: ``{"centre", "half", "bottom", "top", "id", "type"}``."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    out = []
    for o in building.get("openings") or []:
        wall = walls.get(o.get("wall_id"))
        if o.get("level_id") != level["id"] or wall is None or o.get("type") not in ("door", "window", "opening"):
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        bottom, top, _ = opening_vertical(o, level, levels_above)
        # the centre on the outer face line (the outline), so the cut test works on the face
        out.append({"centre": (cx, cy), "half": float(o["width"]) / 2.0, "bottom": bottom, "top": top,
                    "id": o["id"], "type": o["type"], "thickness": float(wall["thickness"])})
    return out


def plinth_look(style: Optional[dict], looks: Optional[dict]) -> dict:
    """The plinth's look (pure): the resolved ``plinth`` look (the agent's slot), else the style family's plinth
    (``ARTICULATION``)."""
    rules = family_rules(style)
    return (looks or {}).get("plinth") or {"material": rules["plinth"], "colour": rules["plinth_colour"],
                                           "source": "build", "assumed": True,
                                           "reason": f"plinth band: {rules['plinth']} (style family "
                                                     f"{rules['family'] or 'default'}; not drawn)"}


def plinth_cuts(building: dict, order: Sequence[dict], outlines: dict, ground_outline, wells: Sequence[dict] = ()
                ) -> list[dict]:
    """What cuts the plinth (pure): the doors and windows of every level and the light wells / front courts."""
    cuts = [dict(it, bottom=it["bottom"], top=it["top"]) for lv in order
            for it in opening_items(building, lv, outlines.get(lv["id"]) or ground_outline, True)]
    return cuts + [{"polygon": w["polygon"]} for w in wells or []]


def articulation_plan(building: dict, levels: Sequence[dict], outlines: dict, ground_outline, terrain: Optional[dict],
                      roof_model: Optional[dict], style: Optional[dict], looks: Optional[dict],
                      wells: Sequence[dict] = ()) -> dict:
    """``{"boxes": [{"kind": plinth | band | coping | surround, "level_id", "center", "size", "rotation_deg"}],
    "looks": {kind: look}, "rules", "assumed": [{"field", "value", "reason"}]}`` (pure).

    - plinth: ``plinth_height`` above the ground (``site.ground_z`` at each edge; flat 0 without a terrain) along
      the ground outline, cut at doors, at windows reaching into it and at light wells and front courts;
    - band: at the floor of every level above the lowest level that meets the ground (``band_height``, centred
      on the slab under that floor), on that level's outline below it, cut at openings;
    - coping: on top of a flat roof's walls (the top level's outline at the roof's eaves height);
    - surround: for the families with ``surround`` (classic, mediterranean, rustic), a frame of
      ``surround_width`` around every outside window (head and jambs; the sill is the window's own).
    """
    from wenart.blender import site as S

    rules = family_rules(style)
    looks = looks or {}
    facade = looks.get("facade") or {"material": "render", "colour": "white"}
    out_looks = {
        "plinth": plinth_look(style, looks),
        "band": looks.get("cornice") or {"material": facade.get("material") or "render", "colour": band_colour(facade),
                                         "source": "build", "assumed": True,
                                         "reason": "slab band / coping: the facade material, set off in colour "
                                                   "(not drawn)"},
        "surround": looks.get("surround") or {"material": rules["surround"] or "limestone", "colour": None,
                                              "source": "build", "assumed": True,
                                              "reason": "window surround (style family; not drawn)"},
    }
    out_looks["coping"] = out_looks["band"]
    if (roof_model or {}).get("type") == "flat" and not looks.get("coping"):
        # 4 Nov 2026 (real07, user: "give some more modern details"): a flat roof's coping is a slim anthracite metal
        # cap like its fascia, not a render block
        mat, colour, _why = KIT_LOOKS["gutter"]
        out_looks["coping"] = {"material": mat, "colour": colour, "source": "build", "assumed": True,
                               "reason": "a flat roof's coping: slim anthracite aluminium, like its fascia (not drawn)"}
    boxes: list[dict] = []
    assumed = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: 0.0)
    if len(ground_outline or []) >= 3:
        cuts = plinth_cuts(building, order, outlines, ground_outline, wells)
        plinth = plinth_rule(building)
        boxes += _plinth(ground_outline, cuts, gz, plinth)     # one ground height per edge: its lower end
        if plinth is None:
            assumed.append({"field": "plinth", "value": DIMENSIONS["plinth_height"],
                            "reason": out_looks["plinth"]["reason"]})
        else:
            assumed.append({"field": "plinth", "value": {"top_z": plinth["top_z"], "min_height": plinth["min"]},
                            "reason": f"plinth: a raised base from the ground up to {plinth['top_z']:+.2f} m "
                                      f"({plinth['source']}), at least {plinth['min']:.2f} m high; "
                                      + out_looks["plinth"]["reason"]})
    ground_top = max(terrain["z"].values()) if terrain else 0.0
    lowest_above = next((lv for lv in order if float(lv["elevation"]) + float(lv["ceiling_height"]) > ground_top + 0.5),
                        None)
    slabs = {s.get("above_level_id"): s for s in building.get("slabs") or []}
    for i, lv in enumerate(order):
        if lowest_above is None or float(lv["elevation"]) <= float(lowest_above["elevation"]) + 1e-6:
            continue
        below = order[i - 1]
        outline = outlines.get(below["id"]) or outlines.get(lv["id"])
        if len(outline or []) < 3:
            continue
        t = float((slabs.get(lv["id"]) or {}).get("thickness") or 0.2)
        zc = float(lv["elevation"]) - t / 2.0
        h = max(DIMENSIONS["band_height"], t)
        cuts = opening_items(building, below, outline, True) + opening_items(building, lv, outline, True)
        # 4 Nov 2026 (UL310): on the straightened outline, reaching into the wall where the wall steps back
        boxes += _band_boxes(band_outline(outline), zc - h / 2.0, zc + h / 2.0, DIMENSIONS["band_proud"], cuts, "band",
                             lv["id"], inset=BAND_CLEAN_M, piers=True)
    if boxes and any(b["kind"] == "band" for b in boxes):
        assumed.append({"field": "slab_band", "value": DIMENSIONS["band_height"], "reason": out_looks["band"]["reason"]})
    if roof_model and roof_model.get("type") == "flat" and roof_model.get("over_level_id"):
        top = next((lv for lv in order if lv["id"] == roof_model["over_level_id"]), None)
        outline = outlines.get(top["id"]) if top else None
        # 4 Nov 2026 (real10, roof terrace): a roof with its own outline (the stair house's) gets its coping there, not
        # round the whole top level at the stair house's height
        if len(roof_model.get("outline") or []) >= 3:
            outline = roof_model["outline"]
        if outline and len(outline) >= 3 and roof_model.get("eaves_z") is not None:
            z = float(roof_model["eaves_z"]) + float(roof_model.get("parapet") or 0.0)   # M12: on a flat_cut parapet
            boxes += _band_boxes(outline, z, z + DIMENSIONS["coping_height"], DIMENSIONS["coping_proud"], [], "coping",
                                 top["id"])
            assumed.append({"field": "coping", "value": DIMENSIONS["coping_height"], "reason": out_looks["band"]["reason"]})
    if rules["surround"]:
        n0 = len(boxes)
        for lv in order:
            outline = outlines.get(lv["id"])
            if len(outline or []) < 3:
                continue
            boxes += _surrounds(building, lv, outline)
        if len(boxes) > n0:
            assumed.append({"field": "surround", "value": DIMENSIONS["surround_width"],
                            "reason": out_looks["surround"]["reason"]})
    # Milestone 13 (T6): the facade kit, only where the documents or the room types imply it
    kit = facade_kit(building, levels, outlines, ground_outline, terrain, roof_model, rules, looks, style)
    boxes += kit["boxes"]
    out_looks.update(kit["looks"])
    assumed += kit["assumed"]
    return {"boxes": boxes, "looks": out_looks, "rules": rules, "assumed": assumed, "kit": kit["summary"]}


def _box(kind: str, level_id, centre, size, rot: float, parent=None, reason: str = "") -> dict:
    return {"kind": kind, "level_id": level_id, "center": [float(c) for c in centre], "size": [float(v) for v in size],
            "rotation_deg": float(rot), "inferred": True, "parent": parent, "reason": reason}


CANOPY = {"eaves_gap_m": 0.5, "probe_m": 0.6, "window_gap_m": 0.15, "min_over_door_m": 0.10, "fascia_h": 0.14,
          "fascia_t": 0.02, "soffit_t": 0.015, "rod_r": 0.012, "rod_rise": 0.6, "rod_in": 0.15, "rod_back": 0.06,
          "plate": (0.08, 0.012, 0.16)}


def canopy_height(e: dict, o: dict, lv: dict, door_top: float, building: dict, levels: Sequence[dict],
                  roof_model: Optional[dict], face) -> tuple[Optional[float], str]:
    """``(top z, reason)`` of an entrance door's canopy, or ``(None, why not)`` (pure; lesson UL171): none where the
    roof's eaves pass less than ``eaves_gap_m`` over it or a balcony or the floor above reaches out over the door (they
    shelter it already); under a window above the door's span it sits ``window_gap_m`` under that window's sill, and
    none when that leaves less than ``min_over_door_m`` over the door."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    ox, oy = e["outward"]
    want = door_top + KIT["canopy_above"] + KIT["canopy_thick"]
    probe = (face[0] + ox * CANOPY["probe_m"], face[1] + oy * CANOPY["probe_m"])
    if roof_model and roof_model.get("equations") and len(roof_model.get("outline") or []) >= 3 \
            and G.point_in_polygon(probe, roof_model["outline"]):
        from wenart.blender import roof as R
        try:
            under = float(R.underside_z(roof_model, *probe))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            under = None
        if under is not None and under - want < CANOPY["eaves_gap_m"]:
            return None, (f"no canopy over {e['opening_id']}: the roof's eaves pass {max(0.0, under - door_top):.2f} m "
                          f"over the door and shelter it (lesson UL171)")
    elev = float(lv["elevation"])
    above = [x["id"] for x in levels if float(x["elevation"]) > elev]
    for r in building.get("rooms") or []:
        if r.get("level_id") in above and len(r.get("polygon") or []) >= 3 and G.point_in_polygon(probe, r["polygon"]):
            return None, (f"no canopy over {e['opening_id']}: {r['id']} on the floor above reaches out over the door "
                          f"and shelters it (lesson UL171)")
    walls = {w["id"]: w for w in building.get("walls") or []}
    ux, uy = -oy, ox
    s0 = e["centre"][0] * ux + e["centre"][1] * uy
    half = e["width"] / 2.0 + KIT["canopy_side"]
    line = e["centre"][0] * ox + e["centre"][1] * oy
    z_top = want
    for q in building.get("openings") or []:
        if q.get("id") == o.get("id") or q.get("wall_id") not in walls:
            continue
        qlv = next((x for x in levels if x["id"] == q.get("level_id")), None)
        if qlv is None:
            continue
        try:
            cx, cy, _ = opening_centre_on_wall(q, walls[q["wall_id"]])
            qb, _qt, _ = opening_vertical(q, qlv, any(float(x["elevation"]) > float(qlv["elevation"]) for x in levels))
        except (KeyError, TypeError, ValueError):
            continue
        if abs(cx * ox + cy * oy - line) > 0.3:
            continue                                        # another wall line
        qs = cx * ux + cy * uy
        if abs(qs - s0) > half + float(q.get("width") or 0.0) / 2.0 or qb <= door_top:
            continue
        z_top = min(z_top, qb - CANOPY["window_gap_m"])
    if z_top - KIT["canopy_thick"] < door_top + CANOPY["min_over_door_m"]:
        return None, (f"no canopy over {e['opening_id']}: a window over the door leaves no room for one under its sill "
                      f"(lesson UL171)")
    return z_top, ("entrance canopy" + (" under the window above" if z_top < want - 1e-6 else ""))


def _rod(p0, p1, r: float) -> tuple[list, list]:
    """A square rod from ``p0`` to ``p1`` (3D), wound outwards (pure)."""
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    ln = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-9
    ux, uy, uz = dx / ln, dy / ln, dz / ln
    ax = (0.0, 0.0, 1.0) if abs(uz) < 0.9 else (1.0, 0.0, 0.0)
    e1 = (ax[1] * uz - ax[2] * uy, ax[2] * ux - ax[0] * uz, ax[0] * uy - ax[1] * ux)
    m = math.sqrt(sum(c * c for c in e1)) or 1e-9
    e1 = tuple(c / m for c in e1)
    e2 = (uy * e1[2] - uz * e1[1], uz * e1[0] - ux * e1[2], ux * e1[1] - uy * e1[0])
    ring = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    verts = [tuple(p[k] + (e1[k] * a + e2[k] * b) * r for k in range(3)) for p in (p0, p1) for a, b in ring]
    faces = [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)] + [[7, 6, 5, 4], [0, 1, 2, 3]]
    return geom2d.convex_solid(verts, faces)


def canopy_parts(face, out, width: float, z_top: float, level_id, parent) -> list[dict]:
    """An entrance canopy as a real product (pure; lesson UL171): a slim anthracite metal canopy ``KIT["canopy_depth"]``
    deep, its front and side fascias ``fascia_h`` deep (the drip edge, taller than the canopy), a wood soffit under it,
    and two black steel tie rods from its front corners up to wall plates ``rod_rise`` over it (kinds ``canopy``,
    ``canopy_soffit``, ``canopy_rod``; a rod carries its own ``mesh``)."""
    ox, oy = out
    ux, uy = -oy, ox
    rot = math.degrees(math.atan2(uy, ux))
    depth, thick = KIT["canopy_depth"], KIT["canopy_thick"]
    ft, fh = CANOPY["fascia_t"], CANOPY["fascia_h"]

    def at(s, d):
        return face[0] + ux * s + ox * d, face[1] + uy * s + oy * d

    why = KIT_LOOKS["canopy"][2]
    c = at(0.0, depth / 2.0)
    out_boxes = [_box("canopy", level_id, (c[0], c[1], z_top - thick / 2.0), (width, depth, thick), rot, parent, why)]
    f = at(0.0, depth - ft / 2.0)
    out_boxes.append(_box("canopy", level_id, (f[0], f[1], z_top - fh / 2.0), (width + 2 * ft, ft, fh), rot, parent,
                          "the canopy's front fascia, its drip edge (not drawn)"))
    for sgn in (-1.0, 1.0):
        sc = at(sgn * (width / 2.0 + ft / 2.0), depth / 2.0)
        out_boxes.append(_box("canopy", level_id, (sc[0], sc[1], z_top - fh / 2.0), (ft, depth, fh), rot, parent,
                              "the canopy's side fascia (not drawn)"))
    st = CANOPY["soffit_t"]
    sf = at(0.0, (depth - ft) / 2.0)
    out_boxes.append(_box("canopy_soffit", level_id, (sf[0], sf[1], z_top - thick - st / 2.0),
                          (width - 0.002, depth - ft - 0.002, st), rot, parent, KIT_LOOKS["canopy_soffit"][2]))
    pw, pd, ph = CANOPY["plate"]
    for sgn in (-1.0, 1.0):
        s = sgn * (width / 2.0 - CANOPY["rod_in"])
        a = at(s, depth - CANOPY["rod_back"])
        b = at(s, pd + CANOPY["rod_r"])
        p0 = (a[0], a[1], z_top)
        p1 = (b[0], b[1], z_top + CANOPY["rod_rise"])
        v, fcs = _rod(p0, p1, CANOPY["rod_r"])
        xs, ys, zs = zip(*v)
        rod = _box("canopy_rod", level_id, ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0,
                                            (min(zs) + max(zs)) / 2.0),
                   (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)), 0.0, parent, KIT_LOOKS["canopy_rod"][2])
        rod["mesh"] = [list(v), [list(x) for x in fcs]]
        out_boxes.append(rod)
        pc = at(s, pd / 2.0)
        out_boxes.append(_box("canopy_rod", level_id, (pc[0], pc[1], z_top + CANOPY["rod_rise"]), (pw, pd, ph), rot,
                              parent, "the tie rod's wall plate (not drawn)"))
    return out_boxes


def guard_boxes(p, q, bottom: float, top: float, level_id, parent, kind: str = "glass_channel") -> list[dict]:
    """A guard from ``p`` to ``q`` in the house's one balustrade language (pure; 26 Oct 2026; 27 Oct 2026, generality
    review: it was always frameless glass, while the stairs and balconies follow ``details.balustrade_kind``): kind
    ``glass_channel`` a metal channel at the opening's bottom and one glass pane up to a cap rail at ``top``;
    ``glass_posts`` posts at most ``details.DIMS["post_every"]`` apart, a handrail and a glass pane in each bay;
    ``bars`` posts, a handrail, a bottom rail and vertical bars ``bar_pitch`` apart (box kinds ``railing`` and
    ``guard_glass``). No gap a child could pass (the 0.11 m rule)."""
    from wenart.blender import details as D

    length = G.distance(p, q)
    if length < 0.1 or top - bottom < 0.1:
        return []
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    rot = math.degrees(math.atan2(uy, ux))
    mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
    ch, chh, cap, gt = KIT["guard_channel"], KIT["guard_channel_h"], KIT["guard_cap"], KIT["guard_glass_t"]
    why, why_glass = KIT_LOOKS["railing"][2], KIT_LOOKS["guard_glass"][2]

    def at(t):
        return p[0] + ux * t, p[1] + uy * t

    if kind not in ("glass_posts", "bars"):
        out = [_box("railing", level_id, (mx, my, bottom + chh / 2.0), (length, ch, chh), rot, parent, why),
               _box("railing", level_id, (mx, my, top - cap / 2.0), (length, ch * 0.6, cap), rot, parent, why)]
        g0, g1 = bottom + chh - 0.03, top - cap + 0.01
        out.append(_box("guard_glass", level_id, (mx, my, (g0 + g1) / 2.0), (length - 0.02, gt, g1 - g0), rot, parent,
                        why_glass))
        return out
    c = D.DIMS
    post, rail = 2 * c["post_r"], 2 * c["handrail_r"]
    n = max(1, int(math.ceil(length / c["post_every"] - 1e-9)))
    stations = [post / 2.0 + (length - post) * k / n for k in range(n + 1)]
    out = [_box("railing", level_id, (mx, my, top - rail / 2.0), (length, rail, rail), rot, parent, why)]
    for t in stations:
        x, y = at(t)
        out.append(_box("railing", level_id, (x, y, (bottom + top - rail) / 2.0), (post, post, top - rail - bottom),
                        rot, parent, why))
    if kind == "glass_posts":
        for t0, t1 in zip(stations, stations[1:]):
            a, b = t0 + post / 2.0 + c["bay_gap"], t1 - post / 2.0 - c["bay_gap"]
            if b - a < 0.1:
                continue
            x, y = at((a + b) / 2.0)
            g0, g1 = bottom + c["glass_bottom"], top - rail - 0.04
            out.append(_box("guard_glass", level_id, (x, y, (g0 + g1) / 2.0), (b - a, gt, g1 - g0), rot, parent,
                            why_glass))
        return out
    zb = bottom + c["bottom_rail_z"]
    out.append(_box("railing", level_id, (mx, my, zb + c["flat_t"]), (length, c["flat_w"] * 0.6, 2 * c["flat_t"]),
                    rot, parent, why))
    z0, z1 = zb + 2 * c["flat_t"], top - rail
    for t0, t1 in zip(stations, stations[1:]):
        a, b = t0 + post / 2.0, t1 - post / 2.0
        k = max(1, int(math.ceil((b - a) / c["bar_pitch"] - 1e-9)))
        for j in range(1, k):
            x, y = at(a + (b - a) * j / k)
            out.append(_box("railing", level_id, (x, y, (z0 + z1) / 2.0), (c["bar_w"], c["bar_w"], z1 - z0), rot,
                            parent, why))
    return out


def eaves_edges(roof_model: Optional[dict]) -> list[dict]:
    """The eaves edges of a pitched roof (pure): the outline edges along which the roof's top surface stays within
    ``KIT["eaves_tol"]`` of ``eaves_z`` (a gable end rises to the ridge: no gutter there), without their runs along
    a roof opening (a roof terrace has no eaves). ``[{"p", "q", "z", "length"}]``; none for a flat roof or without
    planes."""
    if not roof_model or not roof_model.get("equations") or roof_model.get("eaves_z") is None:
        return []
    if roof_model.get("type") in ("flat", None) or roof_model.get("kind") == "flat_cut":
        return []
    from wenart.blender import roof as R

    outline = geom2d.ccw(roof_model.get("outline") or [])
    eaves = float(roof_model["eaves_z"])
    holes = [o["polygon"] for o in roof_model.get("openings") or [] if len(o.get("polygon") or []) >= 3]
    # 31 Oct 2026: a dormer on its facade cuts the eaves in front of it (dormers.py): no gutter across its front
    holes += [d["hole"] for d in roof_model.get("dormers") or [] if d.get("flush") and len(d.get("hole") or []) >= 3]
    out = []
    n = len(outline)
    for i in range(n):
        p, q = outline[i], outline[(i + 1) % n]
        length = G.distance(p, q)
        if length < 0.5:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = -uy, ux                                     # ccw outline: the left normal points inward
        zs = []
        for t in (0.15, 0.5, 0.85):
            x, y = p[0] + ux * t * length + nx * 0.05, p[1] + uy * t * length + ny * 0.05
            zs.append(R.top_z(roof_model, x, y))
        # 1 Nov 2026 (UL234): a slope raised for a door lifts its eaves; that edge is an eaves at its own height (level
        # along the edge, no higher than the lowest eaves plus the largest raise); a gable end still rises along it
        raise_max = max([float(r.get("delta") or 0.0) for r in roof_model.get("slopes_raised") or []] + [0.0])
        z_edge = sum(zs) / len(zs)
        if max(zs) - min(zs) > 2 * KIT["eaves_tol"] or not (eaves - KIT["eaves_tol"] <= z_edge
                                                             <= eaves + raise_max + KIT["eaves_tol"]):
            continue
        # 24 Oct 2026 (real04): a roof terrace cut into the roof has no eaves: the gutter ran on along its parapet
        # past the end of the roof. The edge keeps only its runs outside the roof openings.
        for t0, t1 in _runs_outside(p, (ux, uy), (nx, ny), length, holes):
            a = (p[0] + ux * t0, p[1] + uy * t0)
            b = (p[0] + ux * t1, p[1] + uy * t1)
            out.append({"p": a, "q": b, "z": eaves if abs(z_edge - eaves) <= KIT["eaves_tol"] else round(z_edge, 4),
                        "length": t1 - t0})
    return out


def _wall_point(pt, outline):
    """``(x, y, outward normal, distance)``: the nearest point of an outline's boundary to ``pt``."""
    dist, (a, b) = geom2d.nearest_edge(pt, outline)
    tt = max(0.0, min(1.0, ((pt[0] - a[0]) * (b[0] - a[0]) + (pt[1] - a[1]) * (b[1] - a[1])) /
                      max(1e-9, G.distance(a, b) ** 2)))
    wx, wy = a[0] + (b[0] - a[0]) * tt, a[1] + (b[1] - a[1]) * tt
    wn = G.unit_normal_left(a, b)
    if G.point_in_polygon((wx + wn[0] * 0.05, wy + wn[1] * 0.05), outline):
        wn = (-wn[0], -wn[1])
    return wx, wy, wn, math.hypot(pt[0] - wx, pt[1] - wy)


def _opening_spans(building: dict, level_id: str) -> list[tuple]:
    """``[(cx, cy, ux, uy, half_width, bottom, top)]`` of the doors and windows of a level (pure)."""
    from wenart.blender.shell import opening_centre_on_wall

    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level_id}
    lv = next((x for x in building.get("levels") or [] if x["id"] == level_id), None)
    out = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != level_id or w is None or o.get("type") not in ("door", "window", "opening"):
            continue
        cx, cy, _ = opening_centre_on_wall(o, w)
        length = G.distance(w["start"], w["end"]) or 1.0
        ux, uy = (w["end"][0] - w["start"][0]) / length, (w["end"][1] - w["start"][1]) / length
        floor = float(lv["elevation"]) if lv else 0.0
        sill = float((o.get("sill_height") or {}).get("value") if isinstance(o.get("sill_height"), dict)
                     else o.get("sill_height") or 0.0)
        height = float((o.get("height") or {}).get("value") if isinstance(o.get("height"), dict)
                       else o.get("height") or 2.1)
        out.append((cx, cy, ux, uy, float(o.get("width") or 0.9) / 2.0, floor + sill, floor + sill + height))
    return out


def pipe_spot(p, u, n, length: float, t: float, z_top: float, levels: Sequence[dict], outlines: dict, top_outline,
              building: dict, gz) -> Optional[dict]:
    """Where a downpipe for the eaves station ``t`` stands (pure; 25 Oct 2026, user: "rain gutters going on the air,
    they need to be connected to walls"): the nearest spot within ``pipe_search_m`` of ``t`` along the eaves whose
    wall face, on every storey the pipe passes from ``z_top`` down to the ground, lies within ``pipe_wall_tol_m`` of the
    pipe (no loggia recess, no open corner) and crosses no door or window. ``{"t", "x", "y", "normal", "z0"}`` or
    None. A pipe stands ``downpipe / 2 + 0.02`` out from the top storey's wall face."""
    if len(top_outline or []) < 3:
        return None
    d = KIT["downpipe"]
    step = KIT["pipe_search_step_m"]
    cands = [t]
    k = 1
    while k * step <= KIT["pipe_search_m"]:
        cands += [t + k * step, t - k * step]
        k += 1
    lo, hi = min(KIT["downpipe_end_m"], length / 2.0), max(length - KIT["downpipe_end_m"], length / 2.0)
    # then anywhere on the run, nearest first (a facade of loggias and ribbon windows may have one pier for it)
    far = [lo + j * step for j in range(int((hi - lo) / step) + 1)]
    cands += sorted((c for c in far if abs(c - t) > KIT["pipe_search_m"]), key=lambda c: abs(c - t))
    spans: dict = {}
    for tc in cands:
        if not lo - 1e-9 <= tc <= hi + 1e-9:
            continue
        ex, ey = p[0] + u[0] * tc, p[1] + u[1] * tc
        wx, wy, wn, _dist = _wall_point((ex, ey), top_outline)
        off = d / 2.0 + 0.02
        px, py = wx + wn[0] * off, wy + wn[1] * off
        # clear the outermost storey face under it (a pier or a band standing proud of the top wall)
        for _k in range(int(KIT["pipe_wall_tol_m"] / 0.02)):
            if not any(len(outlines.get(lv["id"]) or []) >= 3 and G.point_in_polygon((px, py), outlines[lv["id"]])
                       for lv in levels):
                break
            off += 0.02
            px, py = wx + wn[0] * off, wy + wn[1] * off
        z0 = gz(px, py) + 0.1
        if z_top - z0 < 1.0:
            continue
        ok = True
        for i, lv in enumerate(levels):
            floor = float(lv["elevation"])
            above = [float(x["elevation"]) for x in levels if float(x["elevation"]) > floor + 0.5]
            ceiling = min(above) if above else z_top
            if ceiling <= z0 + 0.05 or floor >= z_top - 0.05:
                continue                                  # the pipe does not pass this storey
            outline = outlines.get(lv["id"]) or []
            if len(outline) < 3:
                continue
            if G.point_in_polygon((px, py), outline):
                ok = False                                # the storey reaches out over the pipe
                break
            _x, _y, _n, dist = _wall_point((px, py), outline)
            if dist > d / 2.0 + 0.02 + KIT["pipe_wall_tol_m"]:
                ok = False                                # a recess (loggia) or no wall behind the pipe
                break
            if lv["id"] not in spans:
                spans[lv["id"]] = _opening_spans(building, lv["id"])
            for cx, cy, ox, oy, half, bottom, top in spans[lv["id"]]:
                along = (wx - cx) * ox + (wy - cy) * oy
                across = abs((wx - cx) * -oy + (wy - cy) * ox)
                if across < 0.4 and abs(along) < half + 0.12 and bottom < z_top and top > z0:
                    ok = False                            # a door or window under the pipe
                    break
            if not ok:
                break
        if ok:
            return {"t": tc, "x": px, "y": py, "normal": wn, "z0": z0}
    return None


def gutter_systems(edges: Sequence[dict], tol: float = 0.02) -> list[list[int]]:
    """The eaves runs joined end to start into gutter systems (pure; 26 Oct 2026): ``[[edge index, ...]]`` in the
    order of the outline; a hip roof's eaves all round are one closed system, a gable roof's two eaves two."""
    n = len(edges)
    nxt = {}
    for i, e in enumerate(edges):
        for j, f in enumerate(edges):
            if i != j and G.distance(e["q"], f["p"]) <= tol:
                nxt[i] = j
                break
    prv = {j: i for i, j in nxt.items()}
    seen: set = set()
    out = []
    for i in range(n):
        if i in seen:
            continue
        start, k = i, 0                                   # walk back to the chain's start (or round a loop)
        while start in prv and prv[start] != i and k <= n:
            start = prv[start]
            k += 1
        chain, cur = [], start
        while cur is not None and cur not in seen:
            chain.append(cur)
            seen.add(cur)
            cur = nxt.get(cur)
        out.append(chain)
    return out


def _corner_convex(e: dict, f: dict) -> bool:
    """Whether the outline turns left (an outer corner of the ccw roof outline) from edge ``e`` into edge ``f``."""
    ax, ay = e["q"][0] - e["p"][0], e["q"][1] - e["p"][1]
    bx, by = f["q"][0] - f["p"][0], f["q"][1] - f["p"][1]
    return ax * by - ay * bx > 1e-9


def downpipe_plan(edges: Sequence[dict], roof_area: float) -> list[tuple[int, float]]:
    """Where the downpipes of the whole roof go (pure; 26 Oct 2026, user: "why there is that many rain gutters"):
    ``[(edge index, t along the edge)]``, best first. An architect's rule, building-wide: a pipe at the outer corners
    of each gutter system (an open run: at its end corners, one end for a run up to ``single_end_m``), a pipe added
    where a gutter would drain more than ``max_drain_m`` to its nearest pipe, never two within ``pipe_gap_m`` along
    a system, and at most ``max(2, ceil(roof area / area_per_pipe))`` pipes in all (the corners spread furthest
    apart are kept). Every station then looks for a wall face clear of the openings (``pipe_spot``)."""
    end = KIT["downpipe_end_m"]
    systems = gutter_systems(edges)
    picks: list[tuple[int, float, float]] = []            # (edge, t, position along its system)
    per_system: list[list[tuple[int, float, float]]] = []
    for chain in systems:
        closed = len(chain) > 1 and G.distance(edges[chain[-1]]["q"], edges[chain[0]]["p"]) <= 0.02
        pos, offs = 0.0, []
        for i in chain:
            offs.append(pos)
            pos += float(edges[i]["length"])
        total = pos
        cands: list[tuple[int, float, float]] = []
        for k, i in enumerate(chain):
            prev = chain[k - 1] if (k > 0 or closed) else None
            if prev is None or _corner_convex(edges[prev], edges[i]):
                cands.append((i, min(end, edges[i]["length"] / 2.0), offs[k] + min(end, edges[i]["length"] / 2.0)))
        if not closed:
            last = chain[-1]
            t = max(edges[last]["length"] - end, edges[last]["length"] / 2.0)
            if total > KIT["single_end_m"] or not cands:
                cands.append((last, t, offs[-1] + t))
        cands.sort(key=lambda c: c[2])
        keep: list[tuple[int, float, float]] = []
        for c in cands:                                   # never two pipes close together along a system
            if all(abs(c[2] - k2[2]) >= KIT["pipe_gap_m"] and (not closed or total - abs(c[2] - k2[2])
                                                                  >= KIT["pipe_gap_m"]) for k2 in keep):
                keep.append(c)
        if not keep and chain:
            i = chain[0]
            keep.append((i, min(end, edges[i]["length"] / 2.0), min(end, edges[i]["length"] / 2.0)))
        # a gutter drains at most max_drain_m to a pipe: fill the long gaps
        pts = sorted(k2[2] for k2 in keep)
        gaps = [(pts[j], pts[j + 1]) for j in range(len(pts) - 1)]
        if closed and pts:
            gaps.append((pts[-1], pts[0] + total))
        elif pts:
            gaps += [(-pts[0], pts[0]), (pts[-1], 2 * total - pts[-1])]    # an open end drains back to its pipe
        for a, b in gaps:
            if b - a <= 2 * KIT["max_drain_m"]:
                continue
            for m in range(1, int(math.ceil((b - a) / (2 * KIT["max_drain_m"])))):
                s = a + (b - a) * m / math.ceil((b - a) / (2 * KIT["max_drain_m"]))
                s = s % total if closed and total else min(max(s, 0.0), total)
                for k, i in enumerate(chain):
                    if offs[k] - 1e-9 <= s <= offs[k] + edges[i]["length"] + 1e-9:
                        keep.append((i, s - offs[k], s))
                        break
        per_system.append(keep)
        picks += keep
    cap = max(2, int(math.ceil(float(roof_area) / KIT["area_per_pipe_m2"]))) if roof_area > 0 else len(picks)
    while len(picks) > cap:
        # drop the pipe closest to another one (Euclidean), never a system's last
        best = None
        for c in picks:
            mine = next(s for s in per_system if c in s)
            if len(mine) <= 1:
                continue
            ex, ey = _edge_point(edges[c[0]], c[1])
            near = min((math.hypot(ex - fx, ey - fy) for d in picks if d is not c
                        for fx, fy in [_edge_point(edges[d[0]], d[1])]), default=1e9)
            if best is None or near < best[0]:
                best = (near, c, mine)
        if best is None:
            break
        picks.remove(best[1])
        best[2].remove(best[1])
    return [(i, t) for i, t, _pos in picks]


def _edge_point(e: dict, t: float) -> tuple[float, float]:
    length = float(e["length"]) or 1.0
    return (e["p"][0] + (e["q"][0] - e["p"][0]) * t / length, e["p"][1] + (e["q"][1] - e["p"][1]) * t / length)


def downpipe_stations(length: float) -> list[float]:
    """Where the downpipes of an eaves run stand (pure): ``downpipe_end_m`` in from its start, then every
    ``downpipe_every_m``, and (24 Oct 2026) one ``downpipe_end_m`` in from its end when the run is longer than
    ``downpipe_both_ends_m`` (a gutter drains to both ends)."""
    end = KIT["downpipe_end_m"]
    out = []
    t = end
    while t <= length - 0.2:
        out.append(t)
        t += KIT["downpipe_every_m"]
    last = length - end
    if length > KIT["downpipe_both_ends_m"] and out and last - out[-1] > 1.0:
        out.append(last)
    return out


def _runs_outside(p, u, n, length: float, holes, step: float = 0.05, min_run: float = 0.5) -> list[tuple]:
    """``[(t0, t1)]``: the stretches of the edge from ``p`` along ``u`` whose points just inside (``n``, 5 cm) lie in
    none of ``holes`` (pure), at least ``min_run`` long."""
    if not holes:
        return [(0.0, length)]
    count = max(1, int(math.ceil(length / step)))
    free = []
    for k in range(count + 1):
        t = min(length, k * step)
        x, y = p[0] + u[0] * t + n[0] * 0.05, p[1] + u[1] * t + n[1] * 0.05
        free.append(not any(G.point_in_polygon((x, y), h) for h in holes))
    runs, start = [], None
    for k, ok in enumerate(free):
        t = min(length, k * step)
        if ok and start is None:
            start = t
        if (not ok or k == count) and start is not None:
            end = t if ok else max(start, t - step)
            if end - start >= min_run:
                runs.append((start, end))
            start = None
    return runs


def facade_kit(building: dict, levels: Sequence[dict], outlines: dict, ground_outline, terrain: Optional[dict],
               roof_model: Optional[dict], rules: dict, looks: Optional[dict] = None,
               style: Optional[dict] = None) -> dict:
    """The facade kit (pure; Milestone 13 T6): ``{"boxes", "looks", "assumed", "summary"}``. Reveals around the
    windows of the families without surrounds; gutters along the eaves edges of a pitched roof and a downpipe
    ``KIT["downpipe_end_m"]`` from each eaves edge's start corner plus one every ``downpipe_every_m``, from the eaves
    down the wall to the ground; a canopy and two wall lights at every entrance door at grade; a guard rail in front
    of an upper-floor outside door (its sill over ``guard_min_drop`` above the ground) that opens onto no balcony or
    terrace room. Every box is ``inferred`` with its reason; the summary counts per kind."""
    from wenart.blender import site as S
    from wenart.blender.shell import outward_side

    looks = looks or {}
    boxes: list[dict] = []
    assumed: list[dict] = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: 0.0)
    out_looks = {}
    for kind, (slug, colour, reason) in KIT_LOOKS.items():
        out_looks[kind] = looks.get(kind) or {"material": slug, "colour": colour, "source": "build", "assumed": True,
                                              "reason": reason, "inferred": True}
    # 1. reveals (modern families: no surround)
    if not rules.get("surround"):
        w_, proud = KIT["reveal_width"], KIT["reveal_proud"]
        for lv in order:
            outline = outlines.get(lv["id"])
            if len(outline or []) < 3:
                continue
            walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == lv["id"]}
            for it in opening_items(building, lv, outline, True):
                if it["type"] != "window":
                    continue
                o = next(x for x in building["openings"] if x["id"] == it["id"])
                side = outward_side(walls[o["wall_id"]], outline, it["centre"])
                if side is None:
                    continue
                ox, oy = side
                ux, uy = -oy, ox
                face = it["thickness"] / 2.0 + proud / 2.0
                cx, cy = it["centre"][0] + ox * face, it["centre"][1] + oy * face
                rot = math.degrees(math.atan2(uy, ux))
                h = it["top"] - it["bottom"]
                why = KIT_LOOKS["reveal"][2]
                boxes.append(_box("reveal", lv["id"], (cx, cy, it["top"] + w_ / 2.0), (2 * it["half"] + 2 * w_, proud, w_),
                                  rot, it["id"], why))
                for sgn in (-1.0, 1.0):
                    off = sgn * (it["half"] + w_ / 2.0)
                    boxes.append(_box("reveal", lv["id"], (cx + ux * off, cy + uy * off, (it["bottom"] + it["top"]) / 2.0),
                                      (w_, proud, h), rot, it["id"], why))
    # 2. gutters and downpipes along the eaves of a pitched roof
    edges = eaves_edges(roof_model)
    pipe_notes: list[dict] = []
    top_level = next((lv for lv in order if roof_model and lv["id"] == roof_model.get("over_level_id")), None)
    wall_outline = outlines.get(top_level["id"]) if top_level else ground_outline
    gw, gh = KIT["gutter_w"], KIT["gutter_h"]
    for e in edges:
        p, q, z, length = e["p"], e["q"], e["z"], e["length"]
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux                                      # outward (ccw outline)
        mid = G.segment_midpoint(p, q)
        rot = math.degrees(math.atan2(uy, ux))
        boxes.append(_box("gutter", top_level["id"] if top_level else None,
                          (mid[0] + nx * gw / 2.0, mid[1] + ny * gw / 2.0, z - KIT["gutter_drop"] - gh / 2.0),
                          (length + gw, gw, gh), rot, None, KIT_LOOKS["gutter"][2]))
    # 26 Oct 2026: the downpipes are planned for the whole roof (downpipe_plan: at the corners, >= 3 m apart, as
    # many as the roof area needs), no longer per run (real06: 20 pipes, two on the same spot)
    roof_area = G.polygon_area(roof_model.get("outline") or []) if roof_model and \
        len(roof_model.get("outline") or []) >= 3 else 0.0
    placed_xy: list[tuple[float, float]] = []
    served: set = set()
    for ei, t in downpipe_plan(edges, roof_area):
        e = edges[ei]
        p, q, z, length = e["p"], e["q"], e["z"], e["length"]
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux
        z1 = z - KIT["gutter_drop"] - KIT["gutter_h"]
        d = KIT["downpipe"]
        spot = pipe_spot(p, (ux, uy), (nx, ny), length, t, z1, order, outlines, wall_outline, building, gz)
        if spot is None or any(math.hypot(spot["x"] - x, spot["y"] - y) < KIT["pipe_gap_m"] for x, y in placed_xy):
            if spot is None:
                pipe_notes.append({"edge": [list(p), list(q)], "station_m": round(t, 2),
                                   "reason": "no wall face runs down to the ground near this station"})
            continue
        placed_xy.append((spot["x"], spot["y"]))
        served.add(ei)
        ex, ey = p[0] + ux * spot["t"], p[1] + uy * spot["t"]
        px, py, wn, z0 = spot["x"], spot["y"], spot["normal"], spot["z0"]
        boxes.append(_box("downpipe", top_level["id"] if top_level else None, (px, py, (z0 + z1) / 2.0), (d, d, z1 - z0),
                          math.degrees(math.atan2(wn[1], wn[0])), None, KIT_LOOKS["downpipe"][2]))
        # 24 Oct 2026: the outlet from the gutter back to the pipe on the wall (the overhang stood between them:
        # the pipe ended under the soffit, the gutter ran alone at the roof edge)
        gx, gy = ex + nx * gw / 2.0, ey + ny * gw / 2.0
        reach = math.hypot(px - gx, py - gy)
        if reach > d:
            boxes.append(_box("downpipe", top_level["id"] if top_level else None,
                              ((gx + px) / 2.0, (gy + py) / 2.0, z1 - d / 2.0), (reach + d, d, d),
                              math.degrees(math.atan2(py - gy, px - gx)), None,
                              "downpipe outlet from the gutter to the wall (not drawn)"))
    for chain in gutter_systems(edges):
        if edges and not any(i in served for i in chain):
            e = edges[chain[0]]
            pipe_notes.append({"edge": [list(e["p"]), list(e["q"])], "station_m": None,
                               "reason": "this gutter system found no wall to take a downpipe"})
    # 3. canopy and wall lights at the entrance doors at grade
    ents = []
    if len(ground_outline or []) >= 3 and terrain is not None:
        try:
            ents = S.entrances(building, levels, terrain, ground_outline, outlines)
        except (KeyError, TypeError, ValueError):
            ents = []
    openings = {o["id"]: o for o in building.get("openings") or []}
    canopies = []
    for e in ents:
        o = openings.get(e["opening_id"])
        lv = next((x for x in levels if x["id"] == e["level_id"]), None)
        if o is None or lv is None:
            continue
        from wenart.blender.shell import opening_vertical
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, top, _ = opening_vertical(o, lv, above)
        ox, oy = e["outward"]
        ux, uy = -oy, ox
        rot = math.degrees(math.atan2(uy, ux))
        face = (e["centre"][0] + ox * e["half_t"], e["centre"][1] + oy * e["half_t"])
        # 30 Oct 2026 (UL171): a canopy only where nothing shelters the door already, under a window above it, as a
        # real product (canopy_parts)
        z_top, why_not = canopy_height(e, o, lv, top, building, levels, roof_model, face)
        if z_top is None:
            assumed.append({"field": f"canopy:{e['opening_id']}", "value": None, "reason": why_not})
        else:
            limit = z_top if "under the window" in why_not else None
            canopies.append({"e": e, "lv": lv, "face": face, "z": z_top, "limit": limit, "door_top": top})
        for sgn in (-1.0, 1.0):
            off = sgn * (e["width"] / 2.0 + KIT["light_offset"])
            boxes.append(_box("wall_light", lv["id"], (face[0] + ux * off + ox * KIT["light_d"] / 2.0,
                                                       face[1] + uy * off + oy * KIT["light_d"] / 2.0,
                                                       bottom + KIT["light_z"]),
                              (KIT["light_w"], KIT["light_d"], KIT["light_h"]), rot, e["opening_id"],
                              KIT_LOOKS["wall_light"][2]))
    # the canopies of one wall line at one height (the highest; one under a window keeps its own limit)
    for c in canopies:
        ox, oy = c["e"]["outward"]
        line = c["e"]["centre"][0] * ox + c["e"]["centre"][1] * oy
        mates = [k for k in canopies if k["e"]["outward"] == c["e"]["outward"] and k["lv"]["id"] == c["lv"]["id"]
                 and abs(k["e"]["centre"][0] * ox + k["e"]["centre"][1] * oy - line) < 0.3]
        z = max(k["z"] for k in mates)
        if c["limit"] is not None:
            z = min(z, c["limit"])
        boxes += canopy_parts(c["face"], (ox, oy), c["e"]["width"] + 2 * KIT["canopy_side"], z, c["lv"]["id"],
                              c["e"]["opening_id"])
    # 4. guards in front of the openings over a drop (26 Oct 2026, user on real06: "are the people going to jump
    # off from it?"): every outside door, gap or window whose bottom is less than guard_sill over its floor, over a
    # drop of guard_min_drop, opening onto no balcony or terrace, and every opening the architect gave a ``guard``
    # (a French window): a guard across its whole width in the house's balustrade language (details.balustrade_kind,
    # as the stairs and balconies), reaching guard_top over the floor. Two thin bars 0.5 m apart had been "the guard".
    from wenart.blender import details as D

    guard_kind = D.balustrade_kind(style)
    rooms = [r for r in building.get("rooms") or [] if isinstance(r, dict) and len(r.get("polygon") or []) >= 3]
    for rec in (S.outer_openings(building, levels, ground_outline, outlines, kinds=("door", "window", "opening"))
                if len(ground_outline or []) >= 3 else []):
        lv, o = rec["level"], rec["opening"]
        cx, cy = rec["centre"]
        ox, oy = rec["outward"]
        floor = float(lv["elevation"])
        asked = isinstance(o.get("guard"), dict)
        if not asked and rec["bottom"] - floor >= KIT["guard_sill"]:
            continue
        drop = rec["bottom"] - gz(cx + ox * 1.0, cy + oy * 1.0)
        if drop < KIT["guard_min_drop"] and not asked:
            continue
        probe = (cx + ox * (rec["half_t"] + 0.5), cy + oy * (rec["half_t"] + 0.5))
        if any(r.get("level_id") == lv["id"] and str(r.get("room_type") or "") in ("balcony", "terrace", "loggia",
                                                                                   "roof_terrace")
               and G.point_in_polygon(probe, r["polygon"]) for r in rooms):
            continue
        top = floor + float((o.get("guard") or {}).get("top_m") or KIT["guard_top"])
        if top <= rec["bottom"] + 0.05:
            continue
        ux, uy = -oy, ox
        w = float(o.get("width") or 0.9) + 2 * KIT["guard_side"]
        off = rec["half_t"] + KIT["guard_channel"] / 2.0 + 0.01
        fx, fy = cx + ox * off, cy + oy * off
        p = (fx - ux * w / 2.0, fy - uy * w / 2.0)
        q = (fx + ux * w / 2.0, fy + uy * w / 2.0)
        boxes += guard_boxes(p, q, rec["bottom"], top, lv["id"], o["id"], guard_kind)
    counts: dict[str, int] = {}
    for b in boxes:
        counts[b["kind"]] = counts.get(b["kind"], 0) + 1
    # UL171: a canopy is one product of several parts: its kinds count the canopies (one per door)
    for kind in ("canopy", "canopy_soffit", "canopy_rod"):
        if kind in counts:
            counts[kind] = len({b.get("parent") for b in boxes if b["kind"] == kind})
    for kind, n in sorted(counts.items()):
        assumed.append({"field": f"kit:{kind}", "value": n, "reason": KIT_LOOKS[kind][2] + " (inferred)"})
    used = {k: v for k, v in out_looks.items() if k in counts}
    return {"boxes": boxes, "looks": used, "assumed": assumed,
            "summary": {"counts": counts, "eaves_edges": len(edges), "entrances": [e["opening_id"] for e in ents],
                        "downpipes_not_placed": pipe_notes}}


PLINTH_BASE_DEPTH = 0.10        # Milestone 12: the raised base reaches this far in under the outer wall face


def plinth_rule(building: dict) -> Optional[dict]:
    """Milestone 12 (docs/milestone12.md §3.3-§3.4, track L): the plinth the pipeline wrote (``site.plinth``:
    ``top_z`` from the ``SB.`` mark or the ground floor, ``min_height``), as ``{"top_z", "min", "source"}``; None
    without one (the Milestone 11 band of ``plinth_height`` stays)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    p = site.get("plinth")
    if not isinstance(p, dict) or p.get("top_z") is None:
        return None
    floors = sorted(float(f) for f in p.get("floors") or [p["top_z"]])
    return {"top_z": float(p["top_z"]), "min": float(p.get("min_height") or 0.15), "floors": floors,
            "source": "SB. mark" if p.get("source") == "mark" else "the ground floor"}


def plinth_top(rule: dict, ground: float, flush: float = 0.05) -> float:
    """The plinth top over ground ``ground``: the lowest floor at or above it (a basement opened by a sloped site
    takes its own floor), at least ``rule["min"]`` above the ground."""
    top = min([f for f in rule.get("floors") or [] if f >= ground - flush] or [float(rule["top_z"])])
    return max(top, ground + float(rule["min"]))


def plinth_edges(ground_outline, gz, rule: Optional[dict] = None) -> list[dict]:
    """Per edge of the ground outline (counter-clockwise, at least ``min_span`` long) the plinth's height (pure):
    ``{"p", "q", "length", "ground_z", "z0", "z1"}``; the ground of an edge is its lower end. Without ``rule`` the
    Milestone 11 band of ``plinth_height``, with it the raised base up to ``plinth_top``."""
    out = []
    pts = geom2d.ccw(ground_outline)
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        length = G.distance(p, q)
        if length < DIMENSIONS["min_span"]:
            continue
        z = min(gz(*p), gz(*q))
        z1 = z + DIMENSIONS["plinth_height"] if rule is None else plinth_top(rule, z)
        out.append({"p": p, "q": q, "length": length, "ground_z": z, "z0": z - DIMENSIONS["plinth_below"], "z1": z1})
    return out


def is_cladding(slug: Optional[str]) -> bool:
    """Whether a look slug is a cladding on an outside wall (pure): a vocabulary look whose kind is not a render's
    (``RENDER_KINDS``): stone, brick, wood, fibre-cement panels ...; False for a render, a paint and an unknown slug."""
    from wenart.style.profile import _entry

    kind = (_entry(slug) or {}).get("kind") if slug else None
    return bool(kind) and kind not in RENDER_KINDS


def storey_top(level: dict, levels: Sequence[dict]) -> Optional[float]:
    """The top of a floor's walls (pure): the floor of the next level above it (more than 0.5 m higher), None for the
    top level."""
    e = float(level["elevation"])
    above = [float(x["elevation"]) for x in levels if float(x["elevation"]) > e + 0.5]
    return min(above) if above else None


def plinth_storeys(building: dict, levels: Sequence[dict], outlines: dict, ground_outline, terrain: Optional[dict],
                   wells: Sequence[dict] = ()) -> dict[str, list[dict]]:
    """1 Nov 2026 (UL235): the floors whose outside wall the plinth clads (pure): ``{level id: [{"p", "q", "height_m",
    "length_m"}]}``. A plinth edge (``plinth_edges`` with the pipeline's ``site.plinth`` rule; none without it: the
    Milestone 11 band is a band) clads a floor when its top is that floor's top (``storey_top``, within
    ``STOREY["top_tol_m"]``), it shows at least ``STOREY["min_height_m"]`` over the ground on that floor (from the
    ground, or the floor when the ground lies lower, up to the top) on at least ``STOREY["min_length_m"]`` of uncut
    stretches (``plinth_cuts``), and its edge lies on that floor's outline (``STOREY["edge_tol_m"]``)."""
    from wenart.blender import site as S

    rule = plinth_rule(building)
    if rule is None or len(ground_outline or []) < 3:
        return {}
    every = sorted(building.get("levels") or levels, key=lambda lv: float(lv["elevation"]))
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: 0.0)
    cuts = plinth_cuts(building, order, outlines, ground_outline, wells)
    out: dict[str, list[dict]] = {}
    for e in plinth_edges(ground_outline, gz, rule):
        shown = sum(b - a for a, b in _spans(e["length"], _edge_cuts(e["p"], e["q"], cuts, e["z0"], e["z1"]),
                                              DIMENSIONS["min_span"]))
        if shown < STOREY["min_length_m"]:
            continue
        mid = ((e["p"][0] + e["q"][0]) / 2.0, (e["p"][1] + e["q"][1]) / 2.0)
        for lv in order:
            top = storey_top(lv, every)
            outline = outlines.get(lv["id"]) or []
            if top is None or abs(e["z1"] - top) > STOREY["top_tol_m"] or len(outline) < 3:
                continue
            height = e["z1"] - max(e["ground_z"], float(lv["elevation"]))
            if height < STOREY["min_height_m"] or geom2d.distance_to_polygon_edges(mid, outline) > STOREY["edge_tol_m"]:
                continue
            out.setdefault(lv["id"], []).append({"p": [round(float(e["p"][0]), 3), round(float(e["p"][1]), 3)],
                                                 "q": [round(float(e["q"][0]), 3), round(float(e["q"][1]), 3)],
                                                 "height_m": round(height, 3), "length_m": round(shown, 3)})
    return out


def outer_walls(building: dict, level: dict, outline) -> list[dict]:
    """The outside walls of a floor (pure): its walls with an outward side against the floor's outline
    (``shell.outward_side`` at the wall's middle, as ``build.facade_faces`` finds them)."""
    from wenart.blender import shell

    if len(outline or []) < 3:
        return []
    return [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]
            and shell.outward_side(w, outline, G.segment_midpoint(w["start"], w["end"])) is not None]


def _inferred(face: dict) -> bool:
    return bool(face.get("inferred")) or face.get("source") == "inferred"


def _whole_wall_cladding(face: dict) -> bool:
    """An inferred face that clads the whole wall: no span, no height band, no side of its own, a cladding look."""
    return _inferred(face) and not face.get("span") and not face.get("z_range") and not face.get("direction") \
        and is_cladding(face.get("material"))


def _nearest_wall(walls: Sequence[dict], point) -> Optional[str]:
    best = min(walls, key=lambda w: G.point_segment_distance(point, w["start"][:2], w["end"][:2]), default=None)
    return best["id"] if best else None


def storey_claddings(building: dict, levels: Sequence[dict], outlines: dict, faces_by_wall: Optional[dict],
                     plinth: Optional[dict] = None, plinth_look_: Optional[dict] = None,
                     facade_look: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """1 Nov 2026 (lesson UL235, "this was nice wall it can be used all around the same floor"): the faces that carry a
    floor's cladding to every outside wall of that floor (pure). ``(faces, records)``.

    Per floor (``levels``) and its outside walls (``outer_walls``): the claddings it shows on part of them are the
    inferred whole-wall cladding faces of ``faces_by_wall`` (``{wall id: [face]}``, the drawn faces and the scheme's,
    as ``build.facade_faces`` maps them), then the plinth's look (``plinth_look_``) where the plinth clads the floor
    (``plinth``: ``plinth_storeys``), unless the documents, the brief or the style name the facade (``facade_look``'s
    source in ``NAMED_SOURCES``: the plinth stays a base). Every outside wall of the floor without a face the documents
    or the brief give it and without a whole-wall cladding takes the first of them: a face ``{"material", "colour",
    "side": "all", "wall_id", "level_id", "source": "inferred", "inferred": True, "storey_cladding": True, "reason"}``.
    Nothing when the main facade (``facade_look``) is a cladding itself. ``records``: one per floor that got faces,
    ``{"level_id", "material", "colour", "from": facade | plinth, "seen_on", "walls", "reason"}``."""
    facade_look = facade_look or {}
    if is_cladding(facade_look.get("material")):
        return [], []                                    # the main walls carry a cladding all round already
    named = facade_look.get("source") in NAMED_SOURCES
    faces_by_wall = faces_by_wall or {}
    faces: list[dict] = []
    records: list[dict] = []
    for lv in sorted(levels, key=lambda x: float(x["elevation"])):
        outer = outer_walls(building, lv, outlines.get(lv["id"]) or [])
        if not outer:
            continue
        own = {w["id"]: faces_by_wall.get(w["id"]) or [] for w in outer}
        taken = {wid for wid, fs in own.items() if any(not _inferred(f) or _whole_wall_cladding(f) for f in fs)}
        cands: list[dict] = []
        seen: dict = {}
        for w in outer:
            for f in own[w["id"]]:
                if _whole_wall_cladding(f):
                    seen.setdefault((f["material"], f.get("colour")), []).append(w["id"])
        for (material, colour), ids in seen.items():
            cands.append({"material": material, "colour": colour, "from": "facade", "seen_on": sorted(set(ids)),
                          "why": f"the facade puts it on {', '.join(sorted(set(ids)))}"})
        stretches = (plinth or {}).get(lv["id"]) or []
        if stretches and not named and is_cladding((plinth_look_ or {}).get("material")):
            tall = max(stretches, key=lambda s: (s["height_m"], s["length_m"]))
            mid = ((tall["p"][0] + tall["q"][0]) / 2.0, (tall["p"][1] + tall["q"][1]) / 2.0)
            wall = _nearest_wall(outer, mid)
            cands.append({"material": plinth_look_["material"], "colour": plinth_look_.get("colour"), "from": "plinth",
                          "seen_on": [wall] if wall else [], "stretches": stretches,
                          "why": f"the plinth's raised base clads {wall or 'a wall'} from the ground up to the floor "
                                 f"above ({tall['height_m']:.2f} m over {tall['length_m']:.1f} m)"})
        for cand in cands:
            todo = [w["id"] for w in outer if w["id"] not in taken]
            if not todo:
                break
            reason = (f"storey cladding (UL235): {cand['material']} on every outside wall of {lv['id']} "
                      f"({', '.join(todo)}): {cand['why']} (one cladding all round a floor; not drawn)")
            for wid in todo:
                faces.append({"material": cand["material"], "colour": cand["colour"], "side": "all", "wall_id": wid,
                              "level_id": lv["id"], "source": "inferred", "inferred": True, "storey_cladding": True,
                              "reason": reason})
            taken.update(todo)
            records.append({"level_id": lv["id"], "material": cand["material"], "colour": cand["colour"],
                            "from": cand["from"], "seen_on": cand["seen_on"], "walls": todo, "reason": reason,
                            **({"stretches": cand["stretches"]} if cand.get("stretches") else {})})
    return faces, records


def _plinth(ground_outline, cuts, gz, rule: Optional[dict] = None) -> list[dict]:
    """The plinth boxes along the ground outline. Without ``rule`` (Milestone 11): a band ``plinth_height`` above
    the ground, ``proud`` in front of the face. With it (Milestone 12): a raised base from the ground up to
    ``rule["top_z"]`` (the floor; at least ``rule["min"]`` above the ground), ``proud`` in front of the face and
    reaching ``PLINTH_BASE_DEPTH`` in under the wall, so no gap shows between the ground and a floor above it."""
    out = []
    for e in plinth_edges(ground_outline, gz, rule):
        p, q, length, z0, z1 = e["p"], e["q"], e["length"], e["z0"], e["z1"]
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux
        proud = DIMENSIONS["proud"]
        inner = PLINTH_BASE_DEPTH if rule is not None else 0.0
        for a, b in _spans(length, _edge_cuts(p, q, cuts, z0, z1), DIMENSIONS["min_span"]):
            a2 = a - proud if a <= 1e-9 else a
            b2 = b + proud if b >= length - 1e-9 else b
            mid = (a2 + b2) / 2.0
            off = (proud - inner) / 2.0                 # the box centre off the face line (out positive)
            out.append({"kind": "plinth", "level_id": None,
                        "center": [p[0] + ux * mid + nx * off, p[1] + uy * mid + ny * off, (z0 + z1) / 2.0],
                        "size": [b2 - a2, proud + inner, z1 - z0], "rotation_deg": math.degrees(math.atan2(uy, ux))})
    return out


def _surrounds(building: dict, level: dict, outline) -> list[dict]:
    """Head and jambs of a stone surround around every outside window of ``level``."""
    from wenart.blender.shell import outward_side

    w_ = DIMENSIONS["surround_width"]
    proud = DIMENSIONS["surround_proud"]
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    out = []
    for it in opening_items(building, level, outline, True):
        if it["type"] != "window":
            continue
        o = next(x for x in building["openings"] if x["id"] == it["id"])
        wall = walls[o["wall_id"]]
        side = outward_side(wall, outline, it["centre"])
        if side is None:
            continue
        ox, oy = side
        ux, uy = -oy, ox
        face = it["thickness"] / 2.0 + proud / 2.0
        cx, cy = it["centre"][0] + ox * face, it["centre"][1] + oy * face
        rot = math.degrees(math.atan2(uy, ux))
        h = it["top"] - it["bottom"]
        out.append({"kind": "surround", "level_id": level["id"], "parent": it["id"],
                    "center": [cx, cy, it["top"] + w_ / 2.0], "size": [2 * it["half"] + 2 * w_, proud, w_],
                    "rotation_deg": rot})
        for s in (-1.0, 1.0):
            off = s * (it["half"] + w_ / 2.0)
            out.append({"kind": "surround", "level_id": level["id"], "parent": it["id"],
                        "center": [cx + ux * off, cy + uy * off, (it["bottom"] + it["top"]) / 2.0],
                        "size": [w_, proud, h], "rotation_deg": rot})
    return out


def build_articulation(plan: dict, collection, make_material, manifest_objects: list, assumed: list) -> dict:
    """One mesh object per kind (``facade_plinth``, ``facade_band``, ``facade_coping``, ``facade_surround``; kind
    ``facade_detail``, status assumed) from ``articulation_plan``; returns ``{kind: boxes}`` counts."""
    from wenart.blender import common

    counts: dict[str, int] = {}
    by_kind: dict[str, list] = {}
    for b in plan["boxes"]:
        by_kind.setdefault(b["kind"], []).append(b)
    for kind, boxes in sorted(by_kind.items()):
        mat = make_material(plan["looks"][kind])
        # 30 Oct 2026 (UL171): a part with its own mesh (a canopy's tie rod) keeps it
        verts, faces = geom2d.merge([(b["mesh"][0], b["mesh"][1]) if b.get("mesh") else
                                     geom2d.box(b["center"], b["size"], b["rotation_deg"]) for b in boxes])
        name = f"facade_{kind}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="facade_detail",
                                    status="assumed", materials=[mat])
        ob.pass_index = 0
        look = plan["looks"][kind]
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "facade_detail", "status": "assumed", "level_id": None,
            "element_id": None, "evidence": [], "material": mat.name if mat else None, "textured": False,
            "pass_index": None, "detail": kind, "boxes": len(boxes), "slug": look.get("material"),
            "colour": look.get("colour"), "assumed": {"reason": look.get("reason"), "inferred": True},
            "inferred": True, "kit": kind in KIT_KINDS,
            "parents": sorted({str(b.get("parent")) for b in boxes if b.get("parent")})[:12]})
        counts[kind] = len(boxes)
    for a in plan["assumed"]:
        assumed.append({"object": "facade", "field": a["field"], "value": a["value"], "reason": a["reason"],
                        "kind": "facade_detail", "parent": "facade"})
    return counts
