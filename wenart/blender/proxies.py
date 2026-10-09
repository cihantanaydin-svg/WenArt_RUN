"""Furniture proxies: a labelled box per documented furniture piece.

Real assets come in Milestone 4. Until then every ``building.furniture`` entry
becomes a box of the drawn footprint (same centre, size and rotation as the
JSON, nothing moved) with a type-dependent height from ``PROXY_HEIGHTS`` and a
small wedge on the front face that shows ``front_deg``. Proxies are only
created for pieces listed in the JSON: rooms without documented furniture stay
empty in this milestone.

The geometry description (``proxy_geometry``) is pure Python so the CPU tests
check sizes, rotation and the wedge without Blender; ``create_proxies`` needs
``bpy`` and is only called from ``build.py``.

Milestone 10 (track F): the 14 new types have type heights (``PROXY_HEIGHTS``,
the ones of ``wenart/furniture/schemas.py``); a wall-hung piece (``wall_cabinet``)
stands ``mount_bottom_m`` above the floor (``mount_bottom``: 1.45 m by the rule,
assumed, when the piece has none), its proxy box too.
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender import geom2d

# Height in metres per furniture type (docs/milestone3.md, Conventions).
# ``bed`` covers both bed_single and bed_double of the building schema.
PROXY_HEIGHTS: dict[str, float] = {
    "bed": 0.55, "bed_single": 0.55, "bed_double": 0.55,
    "sofa": 0.85, "armchair": 0.85, "table_dining": 0.75, "table_coffee": 0.45,
    "desk": 0.75, "chair": 0.9, "wardrobe": 2.1, "bookshelf": 1.8, "tv_unit": 0.5,
    "nightstand": 0.5, "dresser": 0.8, "kitchen_counter": 0.9, "kitchen_island": 0.9,
    "fridge": 1.8, "stove": 0.9, "sink_kitchen": 0.9, "washbasin": 0.85, "toilet": 0.4,
    "shower": 2.0, "bathtub": 0.55, "washing_machine": 0.85, "unknown": 0.8,
    # Milestone 7 documented-only types (docs/milestone7.md §6.4): a stair rises to the floor above
    # (the default ceiling 2.70 m of wenart/defaults.yaml + the assumed 0.15 m slab; the scene builder
    # uses the level's own ceiling), the others as wenart.furniture.schemas.HEIGHTS.
    "stair": 2.85, "side_table": 0.55, "floor_lamp": 1.6, "potted_plant": 1.0,
    # Milestone 10 (docs/milestone10.md §1.1): the 14 new types, wenart.furniture.schemas.HEIGHTS (typical
    # catalogue heights, assumed); a wall cabinet's own height, hung at its ``mount_bottom_m``.
    "sofa_corner": 0.85, "chaise": 0.8, "ottoman": 0.45, "bench": 0.45, "bar_stool": 0.75, "office_chair": 1.0,
    "console_table": 0.8, "crib": 0.9, "bunk_bed": 1.65, "sideboard": 0.8, "shoe_cabinet": 1.0,
    "display_cabinet": 1.9, "tall_cabinet": 2.1, "wall_cabinet": 0.7,
}
# Milestone 10: wall-hung types stand ``furniture.mount_bottom_m`` above the floor (the §4.4 rule: 1.45 m).
MOUNTED_TYPES: tuple[str, ...] = ("wall_cabinet",)
DEFAULT_MOUNT_BOTTOM_M = 1.45


def mount_bottom(piece: dict) -> tuple[float, bool]:
    """``(height of the piece's bottom above the floor, assumed)``: ``mount_bottom_m`` of a wall-hung piece, the
    rule's 1.45 m (assumed) for a wall cabinet without one, 0 for a piece that stands on the floor."""
    value = piece.get("mount_bottom_m")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
        return float(value), False
    if piece.get("type") in MOUNTED_TYPES:
        return DEFAULT_MOUNT_BOTTOM_M, True
    return 0.0, False

# Types rendered with a glass look instead of the grey proxy material.
GLASS_LOOK = {"shower"}

WEDGE_WIDTH = 0.2
WEDGE_DEPTH = 0.1
WEDGE_HEIGHT = 0.06


def proxy_height(ftype: str, json_height: float | None) -> tuple[float, bool]:
    """Height for a piece: the JSON ``height`` when present, else the table
    value (``assumed``). Returns ``(height, assumed)``."""
    if json_height:
        return float(json_height), False
    return PROXY_HEIGHTS.get(ftype, PROXY_HEIGHTS["unknown"]), True


COINCIDENT_LIFT = 0.005


def footprints_overlap(a: dict, b: dict) -> bool:
    """True when two footprint rectangles overlap in area (separating axis test)."""
    ca = G.rotated_rectangle(a["center"], a["size"], a["rotation_deg"])
    cb = G.rotated_rectangle(b["center"], b["size"], b["rotation_deg"])
    for poly in (ca, cb):
        for i in range(4):
            ex, ey = poly[(i + 1) % 4][0] - poly[i][0], poly[(i + 1) % 4][1] - poly[i][1]
            ax, ay = -ey, ex  # axis normal to this edge
            pa = [p[0] * ax + p[1] * ay for p in ca]
            pb = [p[0] * ax + p[1] * ay for p in cb]
            if max(pa) <= min(pb) + 1e-9 or max(pb) <= min(pa) + 1e-9:
                return False
    return True


# M11 diagnosis (real02): an ``unknown`` footprint that holds other pieces (the whole kitchen read as one 4.6 x 2.9 m
# cluster around its fridge; a rug outline under a sofa group) was a solid 0.8 m box that swallowed them. Such a
# proxy is drawn flat (an outline plate on the floor, still striped as unverified), recorded as assumed.
FLAT_PROXY_HEIGHT_M = 0.02
FLAT_MIN_SIDE_M = 1.0      # M11: a holder is drawn flat only when both sides are at least this long
HOLDS_SHARE = 0.5          # another piece counts as held when this share of its footprint area lies inside ...
HOLDER_AREA_RATIO = 2.0    # ... and the holder is at least twice its area (two overlapping drawn pieces of one
                           # size, e.g. real02's armchair and its ottoman, are no holder and its content)


def _footprint_polygon(fp: dict) -> list[tuple[float, float]]:
    """The footprint rectangle, counter-clockwise (pure Python: Blender's Python has no shapely; M11 track C: the
    shapely version stopped every build inside Blender)."""
    return geom2d.ccw(G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0)))


def _convex_overlap(a: list, b: list) -> float:
    """Area of the overlap of two convex counter-clockwise polygons (``b`` clipped by every edge of ``a``)."""
    poly = list(b)
    n = len(a)
    for i in range(n):
        p, q = a[i], a[(i + 1) % n]
        # keep the left of p->q (inside a counter-clockwise polygon): -(cross) <= 0
        ex, ey = q[0] - p[0], q[1] - p[1]
        poly = geom2d.clip_half_plane(poly, ey, -ex, -(ey * p[0] - ex * p[1]))
        if not poly:
            return 0.0
    return G.polygon_area(poly)


def held_pieces(piece: dict, others: list[dict]) -> list[str]:
    """Ids of the ``others`` (built pieces of the level) whose footprint lies at least ``HOLDS_SHARE`` inside the
    footprint of ``piece``, which is at least ``HOLDER_AREA_RATIO`` times larger (pure)."""
    outer = _footprint_polygon(piece["footprint"])
    outer_area = G.polygon_area(outer)
    if outer_area <= 1e-9:
        return []
    out = []
    for other in others:
        if other is piece or other.get("id") == piece.get("id"):
            continue
        poly = _footprint_polygon(other["footprint"])
        area = G.polygon_area(poly)
        if (area > 1e-9 and outer_area >= HOLDER_AREA_RATIO * area
                and _convex_overlap(outer, poly) >= HOLDS_SHARE * area):
            out.append(other.get("id"))
    return out


def flat_reason(piece: dict, others: list[dict] | None) -> str | None:
    """Why the proxy of ``piece`` is drawn flat (``FLAT_PROXY_HEIGHT_M``), or None: only an ``unknown`` piece
    without a height in the JSON whose footprint holds other built pieces."""
    if piece.get("type") != "unknown" or piece.get("height") or not others:
        return None
    # M11 pod G2b (real02 f_L-1_021): a 5.5 x 0.6 m wall unit holding a small piece is no rug or room-wide outline;
    # only outlines wide in both directions (the kitchen cluster, a rug under a sofa group) are drawn flat.
    if min(float(v) for v in piece["footprint"]["size"]) < FLAT_MIN_SIDE_M:
        return None
    held = held_pieces(piece, others)
    if not held:
        return None
    return (f"unknown footprint holds {', '.join(str(h) for h in held)}: drawn flat ({FLAT_PROXY_HEIGHT_M} m) so the "
            "box does not hide them")


def proxy_geometry(piece: dict, floor_z: float, lift: float = 0.0, flat: bool = False) -> dict:
    """Geometry description of one proxy: the box and, when ``front_deg`` is
    known, the wedge on the front face. ``lift`` adds to the height (used
    when a piece sits on another of the same height, e.g. a stove drawn on
    the kitchen counter: coincident top faces render black in Cycles).
    ``flat``: the box is ``FLAT_PROXY_HEIGHT_M`` high (``flat_reason``).

    Returns ``{"box": (verts, faces), "wedge": (verts, faces) | None,
    "height": h, "height_assumed": bool, "center": [x, y, z], ...}``.
    """
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    rot = float(fp["rotation_deg"])
    height, assumed = proxy_height(piece["type"], piece.get("height"))
    if flat:
        height, assumed = FLAT_PROXY_HEIGHT_M, True
    height += lift
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    base, _ = mount_bottom(piece)              # Milestone 10: a wall cabinet hangs above the floor
    floor_z = floor_z + base
    cz = floor_z + height / 2.0
    box = geom2d.box((cx, cy, cz), (w, d, height), rot)

    wedge = None
    front = piece.get("front_deg")
    if front is not None:
        # Direction of the front in the piece's own frame (0 = +X, ccw).
        local_deg = G.normalise_angle(float(front) - rot)
        a = math.radians(local_deg)
        cos_a, sin_a = math.cos(a), math.sin(a)
        # Distance from the centre to the box boundary along that direction.
        candidates = []
        if abs(cos_a) > 1e-9:
            candidates.append((w / 2.0) / abs(cos_a))
        if abs(sin_a) > 1e-9:
            candidates.append((d / 2.0) / abs(sin_a))
        reach = min(candidates)
        fx, fy = G.rotate_point((cx + reach * cos_a, cy + reach * sin_a), rot, (cx, cy))
        wedge_z = floor_z + min(height / 2.0, 0.4)
        # The wedge apex points to local -Y; -Y is the direction 270 deg, so
        # rotating by (front - 270) makes the apex point along ``front``.
        wedge = geom2d.wedge((fx, fy, wedge_z), WEDGE_WIDTH, WEDGE_DEPTH, WEDGE_HEIGHT,
                             float(front) - 270.0)
    return {
        "box": box, "wedge": wedge, "height": height, "height_assumed": assumed,
        "center": [cx, cy, cz], "size": [w, d, height], "rotation_deg": rot,
        "front_deg": None if front is None else float(front), "mount_bottom_m": base,
    }


def create_proxies(building: dict, level: dict, collection, materials: dict, pass_indices: dict,
                   manifest_objects: list, assumed: list, others: list | None = None) -> list:
    """Create one Blender object per furniture piece of ``level``.

    ``materials`` maps ``"proxy"``, ``"proxy_glass"`` and ``"proxy_unverified"``
    to Blender materials. ``pass_indices`` is the id -> object-index table
    that render.py's Object Index pass uses; it is extended here.
    ``others``: every built piece of the level (``flat_reason``; default: the proxies themselves).
    """
    from wenart.blender import common  # bpy inside

    floor_z = float(level["elevation"])
    created = []
    placed: list[tuple[dict, float]] = []  # (footprint, height) of the proxies made so far
    for piece in building.get("furniture", []):
        if piece["level_id"] != level["id"]:
            continue
        flat = flat_reason(piece, others if others is not None else building.get("furniture", []))
        height = FLAT_PROXY_HEIGHT_M if flat else proxy_height(piece["type"], piece.get("height"))[0]
        lift = 0.0
        for other_fp, other_h in placed:
            if abs(other_h - height) < 1e-3 and footprints_overlap(piece["footprint"], other_fp):
                lift = COINCIDENT_LIFT
                break
        geo = proxy_geometry(piece, floor_z, lift, flat=bool(flat))
        placed.append((piece["footprint"], geo["height"]))
        parts = [geo["box"]]
        if geo["wedge"] is not None:
            parts.append(geo["wedge"])
        verts, faces = geom2d.merge(parts)
        status = piece.get("status", "verified")
        if status == "unverified":
            mat = materials["proxy_unverified"]
        elif piece["type"] in GLASS_LOOK:
            mat = materials["proxy_glass"]
        else:
            mat = materials["proxy"]
        name = f"proxy_{piece['id']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection,
                                    wenart_id=f"proxy:{piece['id']}", kind="furniture_proxy",
                                    status=status, materials=[mat])
        ob["wenart_type"] = piece["type"]
        ob["wenart_room"] = piece.get("room_id") or ""
        index = len(pass_indices) + 1
        pass_indices[f"proxy:{piece['id']}"] = index
        ob.pass_index = index
        entry = {
            "name": name, "wenart_id": f"proxy:{piece['id']}", "kind": "furniture_proxy",
            "status": status, "level_id": level["id"], "element_id": piece["id"],
            "room_id": piece.get("room_id"), "type": piece["type"], "source": piece.get("source"),
            "evidence": piece.get("evidence", []), "material": mat.name, "textured": False,
            "pass_index": index, "center": geo["center"], "size": geo["size"],
            "rotation_deg": geo["rotation_deg"], "front_deg": geo["front_deg"],
            "assumed": {},
        }
        if geo["height_assumed"]:
            entry["assumed"]["height"] = geo["height"]
            assumed.append({"object": name, "field": "height", "value": geo["height"],
                            "reason": flat or f"no height in the JSON; proxy table value for {piece['type']}"})
        if flat:
            entry["flat"] = flat
        if lift:
            entry["assumed"]["height_lift"] = lift
            assumed.append({"object": name, "field": "height_lift", "value": lift,
                            "reason": "footprint overlaps another piece of the same height; "
                                      "lifted so the top faces do not coincide"})
        manifest_objects.append(entry)
        created.append(ob)
    return created
