"""Building shell: walls with boolean-cut openings, door and window geometry,
floors and ceilings (docs/milestone3.md §3, shell.py).

Walls: one object per wall element (named by its id, so every object stays
traceable and the per-kind counts match the JSON), an extruded rectangle from
the centre line, thickness and height, grouped in one collection per level.
Faces get material slots by what they face: interior (style walls), exterior
(``plaster_exterior`` for the outward faces of exterior walls) or wet-room
(``wet_walls`` for faces looking into a bathroom / wc / kitchen).

Openings: a boolean difference per opening with a cutter box of
width x (thickness + 2 cm) x height centred on the wall centre line; doors
start at the floor, windows at the sill. The cutters are temporary objects,
the modifiers are applied through the depsgraph (``common.evaluated_mesh``),
then the cutters are deleted. The EXACT solver is the default in Blender 5.2
(solver items: FLOAT, EXACT, MANIFOLD).

Defaults for ``null`` values are recorded as ``assumed`` in the manifest:
door height 2.10 m, window sill 0.90 m, window height 1.20 m (1.40 m when the
opening is wider than 1.5 m), plain opening full height, wall height = level
ceiling height, slab thickness 0.30 m (walls of a level with a level above
it run up to the next floor so the slab zone is closed).
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender import geom2d

DEFAULTS = {
    "door_height": 2.10,
    "window_sill": 0.90,
    "window_height": 1.20,
    "window_height_wide": 1.40,
    "window_wide_threshold": 1.5,
    "slab_thickness": 0.30,
    "frame_width": 0.05,
    "leaf_thickness": 0.04,
    "glass_thickness": 0.006,
    "cutter_extra": 0.02,
}
WET_ROOM_TYPES = {"bathroom", "wc", "kitchen"}


# --------------------------------------------------------------------------
# Opening sizes (pure Python, used by shell and the tests)
# --------------------------------------------------------------------------

def opening_vertical(opening: dict, level: dict, levels_above: bool) -> tuple[float, float, dict]:
    """``(bottom_z, top_z, assumed)`` of an opening in world Z.

    ``assumed`` lists the defaults that filled ``null`` fields of the JSON."""
    floor_z = float(level["elevation"])
    ceiling = float(level["ceiling_height"])
    assumed = {}
    kind = opening["type"]
    height = opening.get("height")
    sill = opening.get("sill_height")
    if kind == "door":
        if sill is None:
            sill = 0.0
        if height is None:
            height = DEFAULTS["door_height"]
            assumed["height"] = height
    elif kind == "window":
        if sill is None:
            sill = DEFAULTS["window_sill"]
            assumed["sill_height"] = sill
        if height is None:
            wide = float(opening["width"]) > DEFAULTS["window_wide_threshold"]
            height = DEFAULTS["window_height_wide"] if wide else DEFAULTS["window_height"]
            assumed["height"] = height
    else:  # plain opening: full height unless the JSON says otherwise
        if sill is None:
            sill = 0.0
        if height is None:
            height = ceiling - float(sill)
            assumed["height"] = height
    bottom = floor_z + float(sill)
    top = min(bottom + float(height), floor_z + ceiling - 0.001)
    return bottom, top, assumed


def wall_height(wall: dict, level: dict, has_level_above: bool) -> tuple[float, dict]:
    """Wall height and the assumptions used."""
    assumed = {}
    h = wall.get("height")
    if h is None:
        h = float(level["ceiling_height"])
        assumed["height"] = h
    h = float(h)
    if has_level_above:
        h += DEFAULTS["slab_thickness"]
        assumed["slab_thickness"] = DEFAULTS["slab_thickness"]
    return h, assumed


# --------------------------------------------------------------------------
# Walls
# --------------------------------------------------------------------------

def trim_wall_overlaps(walls: list[dict]) -> dict[str, dict]:
    """Shorten wall centre lines where two wall rectangles overlap in volume
    (L-corners of exterior walls drawn as two full-length rectangles).

    Coincident faces of overlapping boxes self-shadow and z-fight in Cycles.
    Where an end edge of wall B lies entirely inside wall A's rectangle, B's
    centre line is cut back to the point where it enters A, so the union of
    the two boxes is unchanged while no faces coincide. At an L-corner both
    ends lie inside each other; the wall with the larger id is trimmed.
    Returns ``{wall_id: {"start": [..], "end": [..], "trimmed": [notes]}}``
    for every wall (untouched walls keep their JSON points).
    """
    out = {w["id"]: {"start": list(w["start"]), "end": list(w["end"]), "trimmed": []} for w in walls}
    ordered = sorted(walls, key=lambda w: w["id"])
    for b in ordered:
        for a in ordered:
            if a["id"] == b["id"]:
                continue
            if a["id"] > b["id"] and _end_inside(a, b):
                continue  # the pair is handled when the roles are swapped
            rect_a = G.centerline_to_rectangle(a["start"], a["end"], a["thickness"])
            cur = out[b["id"]]
            for which in ("start", "end"):
                other = "end" if which == "start" else "start"
                p, q = cur[which], cur[other]
                corners = _end_edge(p, q, b["thickness"])
                if not all(_in_rect(c, rect_a) for c in corners):
                    continue
                t = _exit_parameter(p, q, rect_a)
                if t is None or t <= 1e-6 or t >= 0.999:
                    continue
                new_p = G.point_along_segment(p, q, t)
                cut = G.distance(p, new_p)
                cur[which] = [G.snap(new_p[0]), G.snap(new_p[1])]
                cur["trimmed"].append(f"{which} cut back {cut:.3f} m at the overlap with {a['id']} (union unchanged)")
    return out


def _end_inside(a: dict, b: dict) -> bool:
    """True when an end edge of wall A lies inside wall B's rectangle."""
    rect_b = G.centerline_to_rectangle(b["start"], b["end"], b["thickness"])
    for p, q in ((a["start"], a["end"]), (a["end"], a["start"])):
        if all(_in_rect(c, rect_b) for c in _end_edge(p, q, a["thickness"])):
            return True
    return False


def _end_edge(p, q, thickness: float) -> list[tuple[float, float]]:
    nx, ny = G.unit_normal_left(p, q)
    h = thickness / 2.0
    return [(p[0] + nx * h, p[1] + ny * h), (p[0] - nx * h, p[1] - ny * h)]


def _in_rect(point, rect, tol: float = 1e-6) -> bool:
    """Point inside a convex quadrilateral (or on its boundary within tol)."""
    sign = None
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        cross = (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
        if abs(cross) <= tol:
            continue
        s = cross > 0
        if sign is None:
            sign = s
        elif s != sign:
            return False
    return True


def _exit_parameter(p, q, rect) -> float | None:
    """Parameter t along p->q where the segment leaves the convex rect (p inside)."""
    best = None
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        t = _segment_intersection_t(p, q, a, b)
        if t is not None and t > 1e-9 and (best is None or t < best):
            best = t
    return best


def _segment_intersection_t(p, q, a, b) -> float | None:
    dx, dy = q[0] - p[0], q[1] - p[1]
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = dx * ey - dy * ex
    if abs(den) < 1e-12:
        return None
    t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
    u = ((a[0] - p[0]) * dy - (a[1] - p[1]) * dx) / den
    if -1e-9 <= u <= 1 + 1e-9 and 0 <= t <= 1 + 1e-9:
        return t
    return None


def build_walls(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                assumed: list, warnings: list) -> list:
    """Create the wall objects of a level with their openings cut."""
    import bpy

    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    walls = [w for w in building["walls"] if w["level_id"] == level_id]
    openings = [o for o in building["openings"] if o["level_id"] == level_id]
    rooms = [r for r in building["rooms"] if r["level_id"] == level_id]
    wall_by_id = {w["id"]: w for w in walls}

    wall_mat = library.get(style["walls"]["material"], style["walls"].get("asset"), style["walls"].get("tint"))
    ext_mat = library.get("plaster_exterior")
    wet = style.get("wet_walls") or style["walls"]
    wet_mat = library.get(wet["material"], wet.get("asset"), wet.get("tint"))
    slots = [wall_mat, ext_mat, wet_mat]

    footprint_centre = _level_centre(walls)
    trims = trim_wall_overlaps(walls)
    objects = []
    pairs = []  # (object, wall) for the face classification after the booleans
    cutters = []
    for wall in walls:
        height, wall_assumed = wall_height(wall, level, has_above)
        start, end = trims[wall["id"]]["start"], trims[wall["id"]]["end"]
        length = G.distance(start, end)
        if length < 1e-6:
            warnings.append(f"{wall['id']}: zero-length wall skipped")
            continue
        mid = G.segment_midpoint(start, end)
        angle = G.segment_angle_deg(start, end)
        verts, faces = geom2d.box((mid[0], mid[1], floor_z + height / 2.0),
                                  (length, float(wall["thickness"]), height), angle)
        ob = common.new_mesh_object(wall["id"], verts, faces, collection=collection, wenart_id=wall["id"],
                                    kind="wall", status=wall.get("status", "verified"), materials=slots)
        objects.append(ob)
        pairs.append((ob, wall))

        # Cutters for the openings of this wall.
        for opening in openings:
            if opening["wall_id"] != wall["id"]:
                continue
            bottom, top, _ = opening_vertical(opening, level, has_above)
            cz = (bottom + top) / 2.0
            extra = DEFAULTS["cutter_extra"]
            # Door cutters start a little below the floor so no coplanar faces remain.
            cv, cf = geom2d.box((opening["center"][0], opening["center"][1],
                                 cz - (extra / 2.0 if opening["type"] != "window" else 0.0)),
                                (float(opening["width"]), float(wall["thickness"]) + extra,
                                 top - bottom + (extra if opening["type"] != "window" else 0.0)), angle)
            cutter = common.new_mesh_object(f"cut_{opening['id']}", cv, cf, collection=collection,
                                            wenart_id=opening["id"], kind="opening", status="assumed")
            cutter.hide_render = True
            cutters.append(cutter)
            mod = ob.modifiers.new(name=f"cut_{opening['id']}", type="BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.object = cutter

        manifest_objects.append({
            "name": wall["id"], "wenart_id": wall["id"], "kind": "wall",
            "status": wall.get("status", "verified"), "level_id": level_id, "element_id": wall["id"],
            "evidence": wall.get("evidence", []), "material": wall_mat.name,
            "textured": library.textured(wall_mat),
            "pass_index": None, "assumed": wall_assumed,
            "trimmed": trims[wall["id"]]["trimmed"],
            "start": trims[wall["id"]]["start"], "end": trims[wall["id"]]["end"],
            "thickness": wall["thickness"], "height": height,
        })
        for field, value in wall_assumed.items():
            assumed.append({"object": wall["id"], "field": field, "value": value,
                            "reason": "wall height from the level ceiling height" if field == "height"
                            else "slab between levels"})

    # Apply the booleans through the depsgraph and classify faces.
    bpy.context.view_layer.update()
    for ob, wall in pairs:
        if ob.modifiers:
            mesh = common.evaluated_mesh(ob)
            common.replace_mesh(ob, mesh)
            # The boolean appends the cutter's (empty) material slot; drop it.
            while len(mesh.materials) > len(slots) or any(m is None for m in mesh.materials):
                idx = next((i for i, m in enumerate(mesh.materials) if m is None), len(mesh.materials) - 1)
                mesh.materials.pop(index=idx)
            common.assign_box_uvs(ob.data)
        _assign_wall_face_materials(ob, wall, rooms, footprint_centre)
    for cutter in cutters:
        common.delete_object(cutter)
    bpy.context.view_layer.update()
    return objects


def _level_centre(walls: list[dict]) -> tuple[float, float]:
    pts = [w["start"] for w in walls] + [w["end"] for w in walls]
    if not pts:
        return (0.0, 0.0)
    box = G.bbox(pts)
    return G.box_center(box)


def _assign_wall_face_materials(ob, wall: dict, rooms: list[dict], centre) -> None:
    """Slot 0 interior, 1 exterior (outward faces of exterior walls), 2 wet-room faces."""
    mesh = ob.data
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    mid = G.segment_midpoint(wall["start"], wall["end"])
    outward = (nx, ny)
    if (centre[0] - mid[0]) * nx + (centre[1] - mid[1]) * ny > 0:
        outward = (-nx, -ny)
    wet_polys = [r["polygon"] for r in rooms if r.get("room_type") in WET_ROOM_TYPES]
    for poly in mesh.polygons:
        n = poly.normal
        if abs(n.z) > 0.5 or abs(n.x * nx + n.y * ny) < 0.5:
            poly.material_index = 0  # top, bottom, jambs, end faces
            continue
        if wall.get("exterior") and (n.x * outward[0] + n.y * outward[1]) > 0.5:
            poly.material_index = 1
            continue
        c = poly.center
        probe = (c.x + n.x * 0.05, c.y + n.y * 0.05)
        poly.material_index = 2 if any(G.point_in_polygon(probe, p) for p in wet_polys) else 0


# --------------------------------------------------------------------------
# Doors and windows
# --------------------------------------------------------------------------

def build_openings(building: dict, level: dict, collection, library, style: dict, pass_indices: dict,
                   manifest_objects: list, assumed: list, warnings: list) -> list:
    """Door frame + leaf and window frame + glass per opening (plain openings
    are only the hole in the wall and get no object)."""
    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level_id}
    trim = style.get("trim") or {"material": "painted_wood_white"}
    door_style = style.get("door") or {"material": "wood_oak_light"}
    win_style = style.get("window_frame") or {"material": "painted_metal_white"}
    frame_mat = library.get(trim["material"], trim.get("asset"), trim.get("tint"))
    leaf_mat = library.get(door_style["material"], door_style.get("asset"), door_style.get("tint"))
    win_mat = library.get(win_style["material"], win_style.get("asset"), win_style.get("tint"))
    glass_mat = library.glass()

    created = []
    for opening in building["openings"]:
        if opening["level_id"] != level_id:
            continue
        wall = walls.get(opening["wall_id"])
        if wall is None:
            warnings.append(f"{opening['id']}: wall {opening['wall_id']} not found on {level_id}")
            continue
        bottom, top, op_assumed = opening_vertical(opening, level, has_above)
        for field, value in op_assumed.items():
            assumed.append({"object": opening["id"], "field": field, "value": value,
                            "reason": f"{opening['type']} {field} not in the JSON; default"})
        if opening["type"] == "opening":
            manifest_objects.append(_opening_entry(opening, None, level_id, None, False, None, op_assumed))
            continue
        angle = G.segment_angle_deg(wall["start"], wall["end"])
        cx, cy = float(opening["center"][0]), float(opening["center"][1])
        width = float(opening["width"])
        thickness = float(wall["thickness"])
        fw = DEFAULTS["frame_width"]
        height = top - bottom
        index = len(pass_indices) + 1
        pass_indices[opening["id"]] = index
        status = opening.get("status", "verified")

        if opening["type"] == "door":
            # Frame: two jambs and a head, as deep as the wall.
            parts = [
                geom2d.box((-(width / 2.0 - fw / 2.0), 0.0, height / 2.0), (fw, thickness, height)),
                geom2d.box((width / 2.0 - fw / 2.0, 0.0, height / 2.0), (fw, thickness, height)),
                geom2d.box((0.0, 0.0, height - fw / 2.0), (width - 2 * fw, thickness, fw)),
            ]
            frame = _local_to_world(parts, (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_frame", *frame, collection=collection,
                                        wenart_id=opening["id"], kind="door", status=status, materials=[frame_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, frame_mat.name,
                                                   _textured(library, frame_mat), index, op_assumed))
            # Leaf: closed (0 deg), slightly smaller than the frame opening.
            leaf = _local_to_world([geom2d.box((0.0, 0.0, (height - fw) / 2.0),
                                               (width - 2 * fw - 0.01, DEFAULTS["leaf_thickness"], height - fw - 0.01))],
                                   (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_leaf", *leaf, collection=collection,
                                        wenart_id=opening["id"], kind="door", status=status, materials=[leaf_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, leaf_mat.name,
                                                   _textured(library, leaf_mat), index, op_assumed))
        else:
            depth = min(thickness, 0.08)
            parts = [
                geom2d.box((-(width / 2.0 - fw / 2.0), 0.0, height / 2.0), (fw, depth, height)),
                geom2d.box((width / 2.0 - fw / 2.0, 0.0, height / 2.0), (fw, depth, height)),
                geom2d.box((0.0, 0.0, height - fw / 2.0), (width - 2 * fw, depth, fw)),
                geom2d.box((0.0, 0.0, fw / 2.0), (width - 2 * fw, depth, fw)),
            ]
            frame = _local_to_world(parts, (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_frame", *frame, collection=collection,
                                        wenart_id=opening["id"], kind="window", status=status, materials=[win_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, win_mat.name,
                                                   _textured(library, win_mat), index, op_assumed))
            pane = _local_to_world([geom2d.box((0.0, 0.0, height / 2.0),
                                               (width - 2 * fw, DEFAULTS["glass_thickness"], height - 2 * fw))],
                                   (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_glass", *pane, collection=collection,
                                        wenart_id=opening["id"], kind="window", status=status, materials=[glass_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, glass_mat.name, False, index, op_assumed))
    return created


def _textured(library, mat) -> bool:
    return library.textured(mat)


def _opening_entry(opening, name, level_id, material, textured, index, op_assumed) -> dict:
    return {
        "name": name or opening["id"], "wenart_id": opening["id"], "kind": opening["type"],
        "status": opening.get("status", "verified"), "level_id": level_id, "element_id": opening["id"],
        "evidence": opening.get("evidence", []), "material": material, "textured": textured,
        "pass_index": index, "assumed": dict(op_assumed), "wall_id": opening["wall_id"],
        "has_geometry": name is not None,
    }


def _local_to_world(parts, origin, angle_deg):
    """Rotate box parts given in the opening's local frame (X along the wall,
    Y across, Z up from the opening bottom) into world space."""
    verts, faces = geom2d.merge(parts)
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    world = [(origin[0] + c * x - s * y, origin[1] + s * x + c * y, origin[2] + z) for x, y, z in verts]
    return world, faces


# --------------------------------------------------------------------------
# Floors and ceilings
# --------------------------------------------------------------------------

def build_floors_ceilings(building: dict, level: dict, collection, library, style: dict,
                          manifest_objects: list, warnings: list) -> list:
    """One floor face and one ceiling face per room, material per style and
    wet-room rule; unverified rooms get the dashed-red overlay on the floor."""
    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    ceil_z = floor_z + float(level["ceiling_height"])
    created = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        wet = room.get("room_type") in WET_ROOM_TYPES
        floor_style = (style.get("wet_floor") if wet else None) or style["floor"]
        ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
        unverified = room.get("status") == "unverified"
        floor_mat = library.get(floor_style["material"], floor_style.get("asset"), floor_style.get("tint"),
                                unverified=unverified)
        ceil_mat = library.get(ceiling_style["material"], ceiling_style.get("asset"), ceiling_style.get("tint"))
        if len(room["polygon"]) < 3:
            warnings.append(f"{room['id']}: polygon with fewer than 3 points, no floor")
            continue
        fv, ff = geom2d.polygon_face(room["polygon"], floor_z, facing_up=True)
        ob = common.new_mesh_object(f"{room['id']}_floor", fv, ff, collection=collection, wenart_id=room["id"],
                                    kind="floor", status=room.get("status", "verified"), materials=[floor_mat])
        created.append(ob)
        manifest_objects.append({
            "name": ob.name, "wenart_id": room["id"], "kind": "floor", "status": room.get("status", "verified"),
            "level_id": level_id, "element_id": room["id"], "evidence": room.get("evidence", []),
            "material": floor_mat.name, "textured": _textured(library, floor_mat),
            "pass_index": None, "assumed": {}, "room_type": room.get("room_type"), "wet": wet,
        })
        cv, cf = geom2d.polygon_face(room["polygon"], ceil_z, facing_up=False)
        ob = common.new_mesh_object(f"{room['id']}_ceiling", cv, cf, collection=collection, wenart_id=room["id"],
                                    kind="ceiling", status=room.get("status", "verified"), materials=[ceil_mat])
        created.append(ob)
        manifest_objects.append({
            "name": ob.name, "wenart_id": room["id"], "kind": "ceiling", "status": room.get("status", "verified"),
            "level_id": level_id, "element_id": room["id"], "evidence": room.get("evidence", []),
            "material": ceil_mat.name, "textured": _textured(library, ceil_mat),
            "pass_index": None, "assumed": {}, "room_type": room.get("room_type"), "wet": wet,
        })
    return created


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def door_ray_checks(building: dict, level: dict, scene) -> list[dict]:
    """Cast a ray through every door centre across its wall at 1 m height and
    record what it hits. After the booleans a door ray must hit no wall (the
    closed leaf may be hit; that is kind ``door``)."""
    import bpy
    from mathutils import Vector

    level_id = level["id"]
    floor_z = float(level["elevation"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level_id}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    results = []
    for opening in building["openings"]:
        if opening["level_id"] != level_id or opening["type"] not in ("door", "opening"):
            continue
        wall = walls.get(opening["wall_id"])
        if wall is None:
            continue
        nx, ny = G.unit_normal_left(wall["start"], wall["end"])
        reach = float(wall["thickness"]) / 2.0 + 0.3
        origin = Vector((opening["center"][0] + nx * reach, opening["center"][1] + ny * reach, floor_z + 1.0))
        direction = Vector((-nx, -ny, 0.0))
        hit, _loc, _normal, _index, ob, _matrix = scene.ray_cast(depsgraph, origin, direction, distance=2 * reach)
        results.append({
            "opening_id": opening["id"], "hit": bool(hit),
            "hit_object": ob.name if hit and ob is not None else None,
            "hit_kind": ob.get("wenart_kind") if hit and ob is not None else None,
        })
    return results
