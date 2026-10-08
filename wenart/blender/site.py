"""The site around the building (docs/milestone10.md §3.2 item 5; brief ``site: full`` / ``ground``).

What: the ground around the building at the ground level of each side (``site.ground.levels``, ``terrain:
sides`` for a sloped site; the building's outline is cut out of it), light wells in front of basement
windows below the ground, and with ``site: full`` the plot walls, paving, parking, grass and trees as drawn
(``build: true`` elements of ``building.site``). ``site: ground`` gives the ground plane and the light wells
only. Every detail no drawing gives is ``assumed`` with its reason (scene manifest).

Why: the exterior views need the building standing on its plot; the interior views see the garden
through the windows instead of the world below the horizon; real02 sits on a sloped site with its basement
open on one side.

How (pure Python, tested on the CPU; ``build_site`` makes the Blender objects):

- ``terrain_model``: the building's bounding rectangle in the building frame; each drawn side (compass side
  with its azimuth and the building's ``north_deg``, or front / back / left / right drawing-relative) is
  mapped to the nearest axis direction; a point in front of a facade takes that side's level, a point
  beyond a building corner blends the two sides by the angle around the corner (a slope, no retaining wall:
  assumed); a side without a level takes the mean of the others (assumed). ``ground_z`` evaluates it.
- ``ground_faces``: the ground region (the plot or a margin around the building, whichever is larger,
  minus the building outline and the light wells) in convex pieces on a grid (``GRID_M``), lifted to
  ``ground_z`` (triangles where the terrain is not flat).
- ``light_wells``: a window on an outer wall whose sill lies less than ``LIGHT_WELL_CLEARANCE`` above the
  ground outside it gets an open concrete light well (assumed size), unless one is drawn.
- plot walls step with the ground (segments of ``PLOT_WALL_STEP_M``); trees are a trunk and a low-poly
  crown sized from the drawn crown (height assumed); cars and other site decor are listed, not built.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.shell import outward_side  # noqa: F401 - the outward side of a wall (site and exterior use it)

GRID_M = 1.0                    # ground grid where the terrain is not flat
GRID_MAX_CELLS = 80              # per side: a large ground gets a coarser grid
MARGIN_M = 30.0                  # ground beyond the building (and at least PLOT_MARGIN_M beyond the plot)
PLOT_MARGIN_M = 15.0
GRASS_LIFT = 0.004               # draped areas stand this far above the ground (no coplanar faces)
PAVING_LIFT = 0.012
PLOT_WALL_STEP_M = 2.0
LIGHT_WELL_CLEARANCE = 0.05      # sill this little above the ground outside (or below it) -> light well
DEFAULTS = {
    "plot_wall_height": 1.2, "plot_wall_thickness": 0.2,
    "light_well_depth": 0.8, "light_well_side": 0.2, "light_well_wall": 0.1, "light_well_below_sill": 0.15,
    "light_well_curb": 0.05,
    "tree_height_factor": 1.6, "tree_min_height": 4.0, "trunk_radius": 0.12, "crown_share": 0.6,
    "plant_height": 0.8,
}
AXES = {"+x": (1.0, 0.0), "-x": (-1.0, 0.0), "+y": (0.0, 1.0), "-y": (0.0, -1.0)}
# Drawing-relative sides (no north known): the plan's bottom edge is the front.
SIDE_DIRECTIONS = {"north": "+y", "south": "-y", "east": "+x", "west": "-x",
                   "front": "-y", "back": "+y", "left": "-x", "right": "+x"}
COMPASS = {"north": 0.0, "east": 90.0, "south": 180.0, "west": 270.0}


def _value(entry) -> Optional[float]:
    if isinstance(entry, dict):
        v = entry.get("value")
        return None if v is None else float(v)
    if isinstance(entry, (int, float)) and not isinstance(entry, bool):
        return float(entry)
    return None


def north_deg(building: dict) -> tuple[float, str]:
    """``(north_deg, source)``: the compass bearing of the building's +Y axis (``site.north_deg``), else 0
    (assumed: +Y is north)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    entry = site.get("north_deg")
    v = _value(entry)
    if v is None:
        return 0.0, "assumed (+Y is north: no north arrow)"
    method = entry.get("method") if isinstance(entry, dict) else None
    return v % 360.0, f"site.north_deg ({method or 'given'})"


def compass_to_building(azimuth_deg: float, north: float) -> tuple[float, float]:
    """Unit vector in the building frame of a compass direction (degrees clockwise from north), when the
    building's +Y axis points to the compass bearing ``north``."""
    a = math.radians(float(azimuth_deg) - float(north))
    return (math.sin(a), math.cos(a))


def nearest_axis(d: Sequence[float]) -> str:
    return max(AXES, key=lambda k: AXES[k][0] * d[0] + AXES[k][1] * d[1])


# --------------------------------------------------------------------------
# Terrain
# --------------------------------------------------------------------------

def terrain_model(building: dict, outline: Sequence[Sequence[float]], default_z: float = 0.0) -> dict:
    """The ground levels around the building (pure; see the module docstring).

    Returns ``{"kind": "flat" | "sides", "z": {axis: z}, "rect": [x0, y0, x1, y1], "sides": [{"side",
    "axis", "z", "method"}], "assumed": [{"field", "value", "reason"}], "warnings"}``."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    ground = site.get("ground") if isinstance(site.get("ground"), dict) else {}
    north, north_src = north_deg(building)
    xs = [float(p[0]) for p in outline] or [0.0]
    ys = [float(p[1]) for p in outline] or [0.0]
    rect = [min(xs), min(ys), max(xs), max(ys)]
    assumed, warnings, sides = [], [], []
    by_axis: dict[str, list[float]] = {}
    flat_z = None
    for entry in ground.get("levels") or []:
        if not isinstance(entry, dict):
            continue
        z = _value(entry.get("z"))
        if z is None:
            continue
        name = str(entry.get("side") or "all")
        method = (entry.get("z") or {}).get("method") if isinstance(entry.get("z"), dict) else None
        if method == "assumed":
            assumed.append({"field": f"ground:{name}", "value": z,
                            "reason": (entry.get("z") or {}).get("note") or "ground level assumed in the building JSON"})
        if name == "all":
            flat_z = z
            sides.append({"side": name, "axis": None, "z": z, "method": method})
            continue
        az = entry.get("azimuth_deg")
        if az is not None:
            axis = nearest_axis(compass_to_building(float(az), north))
        elif name in SIDE_DIRECTIONS:
            axis = SIDE_DIRECTIONS[name]
            if name in COMPASS and north:
                axis = nearest_axis(compass_to_building(COMPASS[name], north))
        else:
            warnings.append(f"ground side {name!r} without an azimuth: not used")
            continue
        by_axis.setdefault(axis, []).append(z)
        sides.append({"side": name, "axis": axis, "z": z, "method": method})
    if not by_axis:
        z = flat_z if flat_z is not None else default_z
        if flat_z is None:
            assumed.append({"field": "ground", "value": z, "reason": "no ground level drawn: the ground is flat at "
                                                                      f"z {z:.2f} (the lowest level above ground)"})
        return {"kind": "flat", "z": {k: z for k in AXES}, "rect": rect, "sides": sides, "assumed": assumed,
                "warnings": warnings, "north_deg": north, "north_source": north_src}
    zs = {k: sum(v) / len(v) for k, v in by_axis.items()}
    mean = sum(zs.values()) / len(zs)
    for k in AXES:
        if k not in zs:
            zs[k] = flat_z if flat_z is not None else mean
            assumed.append({"field": f"ground:{k}", "value": round(zs[k], 4),
                            "reason": "no ground level drawn on this side: the mean of the drawn sides"})
    kind = "flat" if max(zs.values()) - min(zs.values()) < 1e-6 else "sides"
    if kind == "sides":
        assumed.append({"field": "terrain_slope", "value": "between the sides",
                        "reason": "the ground between two sides of different level slopes around the building "
                                  "corner (no retaining wall drawn)"})
    return {"kind": kind, "z": zs, "rect": rect, "sides": sides, "assumed": assumed, "warnings": warnings,
            "north_deg": north, "north_source": north_src}


def ground_z(model: dict, x: float, y: float) -> float:
    """The ground level at ``(x, y)`` (``terrain_model``)."""
    z = model["z"]
    if model["kind"] == "flat":
        return float(z["+x"])
    x0, y0, x1, y1 = model["rect"]
    dx = -1 if x < x0 else (1 if x > x1 else 0)
    dy = -1 if y < y0 else (1 if y > y1 else 0)
    if dx == 0 and dy == 0:                           # under the building: the nearest side
        d = {"-x": x - x0, "+x": x1 - x, "-y": y - y0, "+y": y1 - y}
        return float(z[min(d, key=d.get)])
    if dy == 0:
        return float(z["+x" if dx > 0 else "-x"])
    if dx == 0:
        return float(z["+y" if dy > 0 else "-y"])
    cx, cy = (x1 if dx > 0 else x0), (y1 if dy > 0 else y0)
    w = math.atan2(abs(y - cy), abs(x - cx)) / (math.pi / 2.0)      # 0 along the x side, 1 along the y side
    zx, zy = float(z["+x" if dx > 0 else "-x"]), float(z["+y" if dy > 0 else "-y"])
    return (1.0 - w) * zx + w * zy


def is_flat(model: dict) -> bool:
    return model["kind"] == "flat"


# --------------------------------------------------------------------------
# Extent, ground and draped areas
# --------------------------------------------------------------------------

def plot_polygon(building: dict) -> tuple[list, str]:
    """``(polygon, source)`` of the plot: ``site.plot`` (``build`` not false), else the hull of the plot
    walls, else []."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    plot = site.get("plot")
    if isinstance(plot, dict) and plot.get("build", True) is not False and len(plot.get("polygon") or []) >= 3:
        return geom2d.ccw(plot["polygon"]), f"site.plot ({plot.get('source') or 'given'})"
    walls = [w for w in site.get("boundary_walls") or [] if w.get("kind") == "plot"]
    pts = [p for w in walls for p in (w["start"], w["end"])]
    if len(pts) >= 3:
        hull = geom2d.convex_hull(pts)
        if len(hull) >= 3:
            return hull, "the hull of the plot walls"
    return [], "none"


def ground_extent(outline: Sequence[Sequence[float]], plot: Sequence[Sequence[float]]) -> list[tuple[float, float]]:
    """The ground rectangle: ``MARGIN_M`` around the building and ``PLOT_MARGIN_M`` around the plot."""
    pts = [tuple(p[:2]) for p in outline]
    x0, y0, x1, y1 = G.bbox(pts)
    x0, y0, x1, y1 = x0 - MARGIN_M, y0 - MARGIN_M, x1 + MARGIN_M, y1 + MARGIN_M
    if plot:
        px0, py0, px1, py1 = G.bbox([tuple(p[:2]) for p in plot])
        x0, y0 = min(x0, px0 - PLOT_MARGIN_M), min(y0, py0 - PLOT_MARGIN_M)
        x1, y1 = max(x1, px1 + PLOT_MARGIN_M), max(y1, py1 + PLOT_MARGIN_M)
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def grid_step(polygon: Sequence[Sequence[float]]) -> float:
    x0, y0, x1, y1 = G.bbox([tuple(p[:2]) for p in polygon])
    return max(GRID_M, max(x1 - x0, y1 - y0) / GRID_MAX_CELLS)


def draped_faces(outer, holes, terrain: dict, lift: float = 0.0, z: Optional[float] = None,
                 step: Optional[float] = None) -> tuple[list, list]:
    """``(verts, faces)`` of a region (``outer`` minus ``holes``) on the ground (``ground_z`` + ``lift``),
    or flat at ``z`` + ``lift`` when ``z`` is given. Flat regions keep the convex pieces; on a slope every
    piece is cut on a grid (``step``, default ``grid_step``) and fanned into triangles."""
    pieces = geom2d.convex_pieces(geom2d.ccw(outer), [geom2d.ccw(h) for h in holes if len(h) >= 3])
    verts: list = []
    faces: list = []
    index: dict = {}
    flat = z is not None or is_flat(terrain)
    zf = (float(z) if z is not None else ground_z(terrain, 0.0, 0.0)) + lift

    def add(poly, tri: bool):
        if flat:
            pts = [(x, y, zf) for x, y in poly]
        else:
            pts = [(x, y, ground_z(terrain, x, y) + lift) for x, y in poly]
        ids = []
        for p in pts:                                # vertices shared by position (0.1 mm)
            key = (round(p[0], 4), round(p[1], 4))
            if key not in index:
                index[key] = len(verts)
                verts.append(p)
            ids.append(index[key])
        if tri:
            for k in range(1, len(ids) - 1):
                faces.append([ids[0], ids[k], ids[k + 1]])
        else:
            faces.append(ids)

    if flat:
        for piece in pieces:
            add(piece, False)
        return verts, faces
    step = float(step) if step else grid_step(outer)
    for piece in pieces:
        bx0, by0, bx1, by1 = G.bbox(piece)
        i0, i1 = math.floor(bx0 / step), math.ceil(bx1 / step)
        j0, j1 = math.floor(by0 / step), math.ceil(by1 / step)
        for i in range(i0, i1):
            for j in range(j0, j1):
                cell = piece
                for a, b, c in ((-1.0, 0.0, i * step), (1.0, 0.0, -(i + 1) * step),
                                (0.0, -1.0, j * step), (0.0, 1.0, -(j + 1) * step)):
                    cell = geom2d.clip_half_plane(cell, a, b, c)
                    if not cell:
                        break
                if len(cell) >= 3 and G.polygon_area(cell) > 1e-6:
                    add(geom2d.ccw(cell), True)
    return verts, faces


# --------------------------------------------------------------------------
# Light wells
# --------------------------------------------------------------------------

def light_wells(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]]
                ) -> tuple[list[dict], list[str]]:
    """``(wells, warnings)``: the light wells of windows whose sill lies less than ``LIGHT_WELL_CLEARANCE``
    above the ground outside (pure). A drawn light well (``site.ground.light_wells`` with the window's
    ``opening_id``) is used as drawn; any other is assumed: ``light_well_depth`` out from the wall face,
    ``light_well_side`` wider on each side, its floor ``light_well_below_sill`` under the sill. A door below
    the ground outside is a warning (no well is made for it). Each well: ``{"opening_id", "level_id",
    "polygon", "floor_z", "top_z", "outward", "source", "reason"}``."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    drawn = {w.get("opening_id"): w for w in ((site.get("ground") or {}).get("light_wells") or [])
             if isinstance(w, dict) and w.get("opening_id")}
    wells, warnings = [], []
    ids = {lv["id"] for lv in levels}
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") in ids}
    for o in building.get("openings") or []:
        lv = next((lv for lv in levels if lv["id"] == o.get("level_id")), None)
        wall = walls.get(o.get("wall_id"))
        if lv is None or wall is None or o.get("type") not in ("window", "door"):
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        out = outward_side(wall, outline, (cx, cy))
        if out is None:
            continue
        levels_above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, top, _ = opening_vertical(o, lv, levels_above)
        half_t = float(wall["thickness"]) / 2.0
        probe = (cx + out[0] * (half_t + 0.3), cy + out[1] * (half_t + 0.3))
        gz = ground_z(terrain, *probe)
        if o["type"] == "door":
            if bottom < gz - LIGHT_WELL_CLEARANCE:
                warnings.append(f"{o['id']}: door bottom {bottom:.2f} m below the ground outside ({gz:.2f} m); "
                                f"no light well for a door")
            continue
        if bottom >= gz + LIGHT_WELL_CLEARANCE:
            continue
        if o["id"] in drawn and len(drawn[o["id"]].get("polygon") or []) >= 3:
            d = drawn[o["id"]]
            depth = float(d.get("depth") or (gz - bottom + DEFAULTS["light_well_below_sill"]))
            wells.append({"opening_id": o["id"], "level_id": lv["id"], "polygon": geom2d.ccw(d["polygon"]),
                          "floor_z": gz - depth, "top_z": gz, "outward": list(out), "source": "drawn",
                          "reason": "drawn light well"})
            continue
        ux, uy = (-out[1], out[0])
        w = float(o["width"]) / 2.0 + DEFAULTS["light_well_side"]
        d0, d1 = half_t, half_t + DEFAULTS["light_well_depth"]
        poly = [(cx + ux * s + out[0] * d, cy + uy * s + out[1] * d) for s, d in ((-w, d0), (w, d0), (w, d1), (-w, d1))]
        wells.append({"opening_id": o["id"], "level_id": lv["id"], "polygon": geom2d.ccw(poly),
                      "floor_z": bottom - DEFAULTS["light_well_below_sill"], "top_z": gz, "outward": list(out),
                      "source": "assumed",
                      "reason": f"window sill {bottom:.2f} m, ground outside {gz:.2f} m: an open concrete light "
                                f"well {DEFAULTS['light_well_depth']} m deep, {2 * w:.2f} m wide (no light well drawn)"})
    return wells, warnings


def light_well_faces(well: dict) -> tuple[list, list]:
    """``(verts, faces)`` of a light well: its floor and three walls (``light_well_wall`` thick) from the
    floor to ``light_well_curb`` above the ground; the side against the building stays open."""
    poly = geom2d.ccw(well["polygon"])
    t = DEFAULTS["light_well_wall"]
    z0, z1 = float(well["floor_z"]), float(well["top_z"]) + DEFAULTS["light_well_curb"]
    parts = [geom2d.polygon_face(poly, z0, facing_up=True)]
    ox, oy = well["outward"]
    nearest = min(x * ox + y * oy for x, y in poly)
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        mid = G.segment_midpoint(p, q)
        nx, ny = G.unit_normal_left(p, q)           # counter-clockwise: into the well
        # The edge on the wall face (parallel to it, nearest the building) is the building wall: no wall.
        if abs(nx * ox + ny * oy) > 0.9 and mid[0] * ox + mid[1] * oy <= nearest + 1e-6:
            continue
        length = G.distance(p, q)
        # A box along the edge, outside the well.
        cx, cy = mid[0] - nx * t / 2.0, mid[1] - ny * t / 2.0
        parts.append(geom2d.box((cx, cy, (z0 + z1) / 2.0), (length + 2 * t, t, z1 - z0),
                                G.segment_angle_deg(p, q)))
    return geom2d.merge(parts)


# --------------------------------------------------------------------------
# Plot walls and trees
# --------------------------------------------------------------------------

def plot_wall_parts(wall: dict, terrain: dict) -> tuple[list, list, dict]:
    """``(verts, faces, info)`` of a plot wall stepping with the ground: segments of at most
    ``PLOT_WALL_STEP_M``, each from 0.1 m under its lowest ground to its highest ground + the height
    (drawn, else ``plot_wall_height`` assumed)."""
    h = _value(wall.get("height"))
    assumed = h is None or (isinstance(wall.get("height"), dict) and wall["height"].get("method") == "assumed")
    h = DEFAULTS["plot_wall_height"] if h is None else h
    t = float(wall.get("thickness") or DEFAULTS["plot_wall_thickness"])
    a, b = wall["start"], wall["end"]
    length = G.distance(a, b)
    k = max(1, int(math.ceil(length / PLOT_WALL_STEP_M)))
    parts, zs = [], []
    angle = G.segment_angle_deg(a, b)
    for i in range(k):
        p = G.point_along_segment(a, b, i / k)
        q = G.point_along_segment(a, b, (i + 1) / k)
        g = [ground_z(terrain, *p), ground_z(terrain, *q), ground_z(terrain, *G.segment_midpoint(p, q))]
        z0, z1 = min(g) - 0.1, max(g) + h
        mid = G.segment_midpoint(p, q)
        # Segments overlap by the thickness so the steps leave no slit.
        parts.append(geom2d.box((mid[0], mid[1], (z0 + z1) / 2.0), (length / k + (t if k > 1 else 0.0), t, z1 - z0),
                                angle))
        zs += [z0, z1]
    verts, faces = geom2d.merge(parts)
    return verts, faces, {"height": h, "height_assumed": assumed, "thickness": t, "segments": k,
                          "z_range": [round(min(zs), 4), round(max(zs), 4)]}


def _sphere(center, rx: float, ry: float, rz: float, segments: int = 10, rings: int = 6) -> tuple[list, list]:
    cx, cy, cz = center
    verts = [(cx, cy, cz - rz)]
    for r in range(1, rings):
        phi = math.pi * r / rings - math.pi / 2.0
        for s in range(segments):
            th = 2.0 * math.pi * s / segments
            verts.append((cx + rx * math.cos(phi) * math.cos(th), cy + ry * math.cos(phi) * math.sin(th),
                          cz + rz * math.sin(phi)))
    verts.append((cx, cy, cz + rz))
    top = len(verts) - 1
    faces = []
    for s in range(segments):
        faces.append([0, 1 + (s + 1) % segments, 1 + s])
    for r in range(rings - 2):
        b0, b1 = 1 + r * segments, 1 + (r + 1) * segments
        for s in range(segments):
            faces.append([b0 + s, b0 + (s + 1) % segments, b1 + (s + 1) % segments, b1 + s])
    last = 1 + (rings - 2) * segments
    for s in range(segments):
        faces.append([last + s, last + (s + 1) % segments, top])
    return verts, faces


def _cylinder(center, radius: float, z0: float, z1: float, segments: int = 8) -> tuple[list, list]:
    cx, cy = center
    ring = [(cx + radius * math.cos(2 * math.pi * s / segments), cy + radius * math.sin(2 * math.pi * s / segments))
            for s in range(segments)]
    return geom2d.prism(ring, z0, z1)


def tree_parts(item: dict, terrain: dict) -> dict:
    """A parametric tree (site decor ``tree``) or bush (``plant``) on the ground: trunk and crown meshes and
    the assumed sizes. Tree: crown diameter = the drawn size, total height ``tree_height_factor`` x the
    diameter (at least ``tree_min_height``), the crown the top ``crown_share`` of it; plant: a bush of the
    drawn size, ``plant_height`` tall."""
    cx, cy = float(item["center"][0]), float(item["center"][1])
    size = [float(v) for v in (item.get("size") or [1.0, 1.0])[:2]]
    dia = max(0.3, max(size))
    gz = ground_z(terrain, cx, cy)
    if item.get("kind") == "plant":
        h = DEFAULTS["plant_height"]
        crown = _sphere((cx, cy, gz + h / 2.0), size[0] / 2.0, size[1] / 2.0, h / 2.0)
        return {"trunk": None, "crown": crown, "height": h, "diameter": dia, "ground_z": gz,
                "reason": f"bush of the drawn size, {h} m tall (height assumed)"}
    h = max(DEFAULTS["tree_min_height"], DEFAULTS["tree_height_factor"] * dia)
    crown_h = DEFAULTS["crown_share"] * h
    trunk = _cylinder((cx, cy), DEFAULTS["trunk_radius"], gz - 0.05, gz + h - crown_h * 0.6)
    crown = _sphere((cx, cy, gz + h - crown_h / 2.0), size[0] / 2.0, size[1] / 2.0, crown_h / 2.0)
    return {"trunk": trunk, "crown": crown, "height": round(h, 3), "diameter": dia, "ground_z": gz,
            "crown_z": [round(gz + h - crown_h, 3), round(gz + h, 3)],
            "reason": f"parametric tree: crown {dia:.1f} m as drawn, {h:.1f} m tall (height assumed)"}


# --------------------------------------------------------------------------
# The plan of the site (pure) and the Blender objects
# --------------------------------------------------------------------------

def _built(items) -> list[dict]:
    return [i for i in items or [] if isinstance(i, dict) and i.get("build", True) is not False]


def site_plan(building: dict, levels: Sequence[dict], outline: Sequence[Sequence[float]], mode: str = "full"
              ) -> dict:
    """Everything the site build makes (pure): ``{"mode", "terrain", "outline", "plot", "extent", "wells",
    "plot_walls", "areas": [{"id", "kind", "polygon", "z", "material", "source"}], "trees", "not_built",
    "assumed", "warnings", "ground_is_grass"}``. ``mode`` ``full`` (plot, paving, grass, plot walls,
    parking, trees as drawn) or ``ground`` (the ground plane and the light wells)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    lowest = min(levels, key=lambda lv: float(lv["elevation"])) if levels else None
    default_z = 0.0 if lowest is None or float(lowest["elevation"]) < 0 else float(lowest["elevation"])
    terrain = terrain_model(building, outline, default_z)
    plot, plot_src = plot_polygon(building) if mode == "full" else ([], "none")
    extent = ground_extent(outline, plot)
    wells, warnings = light_wells(building, levels, terrain, outline)
    warnings = list(terrain["warnings"]) + warnings
    assumed = list(terrain["assumed"])
    for w in wells:
        if w["source"] == "assumed":
            assumed.append({"field": f"light_well:{w['opening_id']}", "value": [round(w["floor_z"], 3),
                                                                                round(w["top_z"], 3)],
                            "reason": w["reason"]})
    plot_walls, areas, trees, not_built = [], [], [], []
    ground_is_grass = False
    if mode == "full":
        for w in _built(site.get("boundary_walls")):
            plot_walls.append(w)
        for key, kind, lift in (("grass", "grass", GRASS_LIFT), ("paving", "paving", PAVING_LIFT),
                                ("parking", "parking", PAVING_LIFT)):
            for a in _built(site.get(key)):
                poly = geom2d.ccw(a.get("polygon") or [])
                if len(poly) < 3:
                    continue
                if kind == "grass" and plot and G.polygon_area(poly) >= 0.98 * G.polygon_area(plot):
                    ground_is_grass = True          # the grass covers the plot: the ground takes it
                    continue
                areas.append({"id": a.get("id"), "kind": kind, "polygon": poly, "z": a.get("z"),
                              "material": a.get("material"), "source": a.get("source"), "lift": lift})
        for item in _built(site.get("decor")):
            if item.get("kind") in ("tree", "plant"):
                trees.append(item)
            else:
                not_built.append({"id": item.get("id"), "kind": item.get("kind"),
                                  "reason": f"site decor of kind {item.get('kind')!r} is not built (no model)"})
        for item in site.get("openings") or []:
            if isinstance(item, dict):
                not_built.append({"id": item.get("id"), "kind": "site_opening",
                                  "reason": "gates in the plot walls are not built (the wall is closed)"})
        for a in _built(site.get("areas")):
            not_built.append({"id": a.get("id"), "kind": f"area:{a.get('kind')}",
                              "reason": "exterior label: its surface is built from site.paving / parking / grass"})
    else:
        not_built.append({"id": None, "kind": "site", "reason": "brief site: ground (the ground plane and the "
                                                                "light wells only)"})
    return {"mode": mode, "terrain": terrain, "outline": geom2d.ccw(outline), "plot": plot, "plot_source": plot_src,
            "extent": extent, "wells": wells, "plot_walls": plot_walls, "areas": areas, "trees": trees,
            "not_built": not_built, "assumed": assumed, "warnings": warnings, "ground_is_grass": ground_is_grass}


def build_site(plan: dict, collection, materials: dict, manifest_objects: list, assumed: list) -> dict:
    """The site objects of ``site_plan`` (kind ``site``): ``ground``, ``lightwell_<opening>``, the plot walls
    (their ids), the areas (their ids) and ``tree_<id>`` (trunk and crown in one object, two slots).
    ``materials``: Blender materials by look name (``ground``, ``grass``, ``paving``, ``parking``,
    ``plot_wall``, ``light_well``, ``bark``, ``foliage``). Returns the summary for the scene manifest."""
    from wenart.blender import common

    terrain = plan["terrain"]
    holes = [plan["outline"]] + [w["polygon"] for w in plan["wells"]]
    summary = {"built": True, "mode": plan["mode"], "objects": [],
               "reason": f"brief site: {plan['mode']} (docs/milestone10.md §3.2 item 5)", "terrain": {
        "kind": terrain["kind"], "z": {k: round(v, 4) for k, v in terrain["z"].items()}, "sides": terrain["sides"],
        "north_deg": terrain["north_deg"], "north_source": terrain["north_source"]},
        "plot_source": plan["plot_source"], "not_built": plan["not_built"], "warnings": plan["warnings"]}

    def entry(name, wid, mat, status, extra):
        manifest_objects.append({"name": name, "wenart_id": wid, "kind": "site", "status": status, "level_id": None,
                                 "element_id": wid, "evidence": [], "material": mat.name if mat else None,
                                 "textured": False, "pass_index": None, **extra})
        summary["objects"].append(name)

    ground_mat = materials["grass" if plan["ground_is_grass"] or plan["mode"] == "full" else "ground"]
    verts, faces = draped_faces(plan["extent"], holes, terrain)
    ob = common.new_mesh_object("ground", verts, faces, collection=collection, wenart_id="ground", kind="site",
                                status="assumed", materials=[ground_mat])
    zs = [v[2] for v in verts] or [0.0]
    entry(ob.name, "ground", ground_mat, "assumed",
          {"assumed": {"extent": [list(p) for p in plan["extent"]], "terrain": terrain["kind"],
                       "reason": "ground plane around the building (the levels per side as drawn, the rest assumed)"},
           "z_range": [round(min(zs), 4), round(max(zs), 4)]})
    for w in plan["wells"]:
        v, f = light_well_faces(w)
        name = f"lightwell_{w['opening_id']}"
        ob = common.new_mesh_object(name, v, f, collection=collection, wenart_id=name, kind="site",
                                    status="verified" if w["source"] == "drawn" else "assumed",
                                    materials=[materials["light_well"]])
        entry(ob.name, name, materials["light_well"], "verified" if w["source"] == "drawn" else "assumed",
              {"assumed": {} if w["source"] == "drawn" else {"reason": w["reason"]}, "parent": w["opening_id"],
               "z_range": [round(w["floor_z"], 4), round(w["top_z"] + DEFAULTS["light_well_curb"], 4)]})
    for wall in plan["plot_walls"]:
        v, f, info = plot_wall_parts(wall, terrain)
        wid = str(wall.get("id") or f"plot_wall_{len(summary['objects'])}")
        ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site",
                                    status="verified", materials=[materials["plot_wall"]])
        entry(ob.name, wid, materials["plot_wall"], "verified",
              {"evidence": wall.get("evidence") or [], "z_range": info["z_range"], "segments": info["segments"],
               "assumed": {"height": info["height"]} if info["height_assumed"] else {}})
        if info["height_assumed"]:
            assumed.append({"object": wid, "field": "height", "value": info["height"],
                            "reason": "plot wall height not drawn"})
    for area in plan["areas"]:
        z = area["z"]
        v, f = draped_faces(area["polygon"], holes, terrain, lift=area["lift"], z=z)
        if not f:
            continue
        mat = materials[area["kind"]]
        wid = str(area.get("id") or f"{area['kind']}_{len(summary['objects'])}")
        status = "assumed" if area.get("source") == "assumed" else "verified"
        ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site", status=status,
                                    materials=[mat])
        entry(ob.name, wid, mat, status, {"assumed": {"lift_m": area["lift"]} if z is not None else
                                          {"lift_m": area["lift"], "draped": True},
                                          "area_kind": area["kind"], "slug": area.get("material")})
    for item in plan["trees"]:
        parts = tree_parts(item, terrain)
        wid = f"tree_{item.get('id') or len(summary['objects'])}"
        meshes = [m for m in (parts["trunk"], parts["crown"]) if m is not None]
        v, f = geom2d.merge(meshes)
        slots = ([0] * len(parts["trunk"][1]) if parts["trunk"] else []) + [1] * len(parts["crown"][1])
        ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site", status="assumed",
                                    materials=[materials["bark"], materials["foliage"]], face_material_indices=slots)
        entry(ob.name, wid, materials["foliage"], "assumed",
              {"evidence": item.get("evidence") or [], "parent": item.get("id"),
               "assumed": {"height_m": parts["height"], "reason": parts["reason"]}, "site_kind": item.get("kind")})
        assumed.append({"object": wid, "field": "tree", "value": parts["height"], "reason": parts["reason"],
                        "parent": str(item.get("id")), "kind": "site_tree"})
    for a in plan["assumed"]:
        assumed.append({"object": "site", "field": a["field"], "value": a["value"], "reason": a["reason"]})
    return summary
