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
- ``door_terrain``: an outside door whose bottom lies below the ground outside (a basement door) puts the
  terrain of its side at its floor (``terrain_model(..., overrides=)``; assumed, in the scene manifest; the
  drawn ``site.ground`` is never changed, §1.6b row 12).
- ``light_wells``: a window on an outer wall whose sill lies less than ``LIGHT_WELL_CLEARANCE`` above the
  ground outside it gets an open concrete light well (assumed size), unless one is drawn.
- plot walls step with the ground (segments of ``PLOT_WALL_STEP_M``); trees are a trunk and a low-poly
  crown sized from the drawn crown (height assumed); cars and other site decor are listed, not built.
- ``build_site``: object kinds ``terrain``, ``light_well``, ``site_wall``, ``site_area``, ``site_decor``
  (§1.6b row 11); the looks come from ``exterior.resolve_looks`` (an area's own drawn material first).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.shell import outward_side

GRID_M = 1.0                    # ground grid where the terrain is not flat
GRID_MAX_CELLS = 80              # per side: a large ground gets a coarser grid
MARGIN_M = 30.0                  # ground beyond the building (and at least PLOT_MARGIN_M beyond the plot)
# Flat ground runs on to the horizon (exterior.CLIP_END stays beyond it): a 30 m plane ended in the middle of the
# exterior views, the HDRI's own ground showed behind its edge (the "lake shore" of real02's views) and the aerial
# view saw the plane's corner. A slope keeps MARGIN_M (its grid would get too coarse near the building).
HORIZON_M = 1000.0
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


# Drawing-relative sides (docs/milestone10.md §1.6b row 1, $defs/side): front = -Y, back = +Y, left = -X, right = +X.
DRAWING_SIDES = {"front": (0.0, -1.0), "back": (0.0, 1.0), "left": (-1.0, 0.0), "right": (1.0, 0.0)}


def side_direction(side: Optional[str], north: float = 0.0) -> Optional[tuple[float, float]]:
    """The outward unit vector in the building frame of a ``$defs/side`` (a compass side with the building's
    ``north`` bearing, or a drawing-relative one); None for ``all`` or an unknown word."""
    if side in COMPASS:
        return compass_to_building(COMPASS[side], north)
    return DRAWING_SIDES.get(str(side)) if side else None


def side_of(direction: Sequence[float], north: float = 0.0, north_known: bool = True) -> str:
    """The ``$defs/side`` an outward direction (building frame) faces within 45 degrees: a compass side when
    north is known, else front / back / left / right."""
    if north_known:
        theta = math.degrees(math.atan2(float(direction[1]), float(direction[0])))
        bearing = (float(north) + 90.0 - theta) % 360.0
        return min(COMPASS, key=lambda s: abs((bearing - COMPASS[s] + 180.0) % 360.0 - 180.0))
    return max(DRAWING_SIDES, key=lambda s: DRAWING_SIDES[s][0] * direction[0] + DRAWING_SIDES[s][1] * direction[1])


# --------------------------------------------------------------------------
# Terrain
# --------------------------------------------------------------------------

def terrain_model(building: dict, outline: Sequence[Sequence[float]], default_z: float = 0.0,
                  overrides: Optional[dict] = None) -> dict:
    """The ground levels around the building (pure; see the module docstring).

    ``overrides``: ``{axis: {"z", "reason", "opening_ids"}}`` the build's own terrain changes (``door_terrain``:
    the ground at a basement door's floor on its side; assumed); a side with a drawn level of its own keeps it
    (a warning). Returns ``{"kind": "flat" | "sides", "z": {axis: z}, "rect": [x0, y0, x1, y1], "sides":
    [{"side", "axis", "z", "method"}], "assumed": [{"field", "value", "reason"}], "warnings", "changes":
    [{"axis", "z", "reason", "opening_ids"}]}``."""
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
    changes = []
    for axis, ov in sorted((overrides or {}).items()):
        if axis in by_axis:
            warnings.append(f"{', '.join(ov.get('opening_ids') or [])}: below the drawn ground on the {axis} side; "
                            f"the drawn ground is kept")
            continue
        by_axis[axis] = [float(ov["z"])]
        sides.append({"side": None, "axis": axis, "z": float(ov["z"]), "method": "assumed"})
        assumed.append({"field": f"ground:{axis}", "value": round(float(ov["z"]), 4), "reason": ov["reason"]})
        changes.append({"axis": axis, "z": round(float(ov["z"]), 4), "reason": ov["reason"],
                        "opening_ids": list(ov.get("opening_ids") or [])})
    if not by_axis:
        z = flat_z if flat_z is not None else default_z
        if flat_z is None:
            assumed.append({"field": "ground", "value": z, "reason": "no ground level drawn: the ground is flat at "
                                                                      f"z {z:.2f} (the lowest level above ground)"})
        return {"kind": "flat", "z": {k: z for k in AXES}, "rect": rect, "sides": sides, "assumed": assumed,
                "warnings": warnings, "north_deg": north, "north_source": north_src, "changes": changes}
    zs = {k: sum(v) / len(v) for k, v in by_axis.items()}
    mean = sum(zs.values()) / len(zs)
    for k in AXES:
        if k not in zs:
            zs[k] = flat_z if flat_z is not None else mean
            if flat_z is None:                     # a drawn "all" level holds for the sides without their own
                assumed.append({"field": f"ground:{k}", "value": round(zs[k], 4),
                                "reason": "no ground level drawn on this side: the mean of the drawn sides"})
    kind = "flat" if max(zs.values()) - min(zs.values()) < 1e-6 else "sides"
    if kind == "sides":
        assumed.append({"field": "terrain_slope", "value": "between the sides",
                        "reason": "the ground between two sides of different level slopes around the building "
                                  "corner (no retaining wall drawn)"})
    return {"kind": kind, "z": zs, "rect": rect, "sides": sides, "assumed": assumed, "warnings": warnings,
            "north_deg": north, "north_source": north_src, "changes": changes}


def door_terrain(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
                 outlines: Optional[dict] = None) -> dict:
    """The build's terrain changes for outside doors below the ground (pure; §3.2 item 5): a door on an outer
    wall whose bottom lies more than ``LIGHT_WELL_CLEARANCE`` under the ground outside (a basement door) puts
    the terrain of its side at its floor: ``{axis: {"z", "reason", "opening_ids"}}`` (the lowest door of a
    side), for ``terrain_model(..., overrides=)``."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    ids = {lv["id"] for lv in levels}
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") in ids}
    out: dict = {}
    for o in building.get("openings") or []:
        lv = next((lv for lv in levels if lv["id"] == o.get("level_id")), None)
        wall = walls.get(o.get("wall_id"))
        if lv is None or wall is None or o.get("type") != "door":
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        side = outward_side(wall, (outlines or {}).get(lv["id"]) or outline, (cx, cy))     # its own level (#27)
        if side is None:
            continue
        levels_above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, _top, _ = opening_vertical(o, lv, levels_above)
        half_t = float(wall["thickness"]) / 2.0
        gz = ground_z(terrain, cx + side[0] * (half_t + 0.3), cy + side[1] * (half_t + 0.3))
        if bottom >= gz - LIGHT_WELL_CLEARANCE:
            continue
        axis = nearest_axis(side)
        rec = out.setdefault(axis, {"z": bottom, "opening_ids": []})
        rec["z"] = min(rec["z"], bottom)
        rec["opening_ids"].append(o["id"])
    for axis, rec in out.items():
        rec["reason"] = (f"outside door {', '.join(rec['opening_ids'])} below the ground: the terrain on the {axis} "
                         f"side at its floor ({rec['z']:.2f} m), sloping to the drawn ground around the building "
                         f"corners (no retaining wall drawn)")
    return out


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
        near = min(d.values())
        # A building corner belongs to two sides: the lower one (the ground never rises over a door there).
        return float(min(z[k] for k in d if d[k] <= near + 1e-9))
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


def ground_extent(outline: Sequence[Sequence[float]], plot: Sequence[Sequence[float]],
                  margin: float = MARGIN_M) -> list[tuple[float, float]]:
    """The ground rectangle: ``margin`` (default ``MARGIN_M``) around the building and ``PLOT_MARGIN_M`` around
    the plot."""
    pts = [tuple(p[:2]) for p in outline]
    x0, y0, x1, y1 = G.bbox(pts)
    x0, y0, x1, y1 = x0 - margin, y0 - margin, x1 + margin, y1 + margin
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

def light_wells(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
                outlines: Optional[dict] = None, front_court: str = "no") -> tuple[list[dict], list[str]]:
    """``(wells, warnings)``: the light wells of windows whose sill lies less than ``LIGHT_WELL_CLEARANCE``
    above the ground outside (pure). A drawn light well (``site.ground.light_wells`` with the window's
    ``opening_id``) is used as drawn; any other is assumed: ``light_well_depth`` out from the wall face,
    ``light_well_side`` wider on each side, its floor ``light_well_below_sill`` under the sill. A door below
    the ground outside is a warning (no well is made for it). Each well: ``{"opening_id", "level_id",
    "polygon", "floor_z", "top_z", "outward", "source", "reason"}``.

    Milestone 11 (docs/milestone11.md §1.1 E9, decision D6, brief ``site_options.front_court``): ``auto`` makes a
    sunken front court (``front_courts``, ``source: inferred``, ``kind: front_court``) instead of the light well in
    front of a window whose sill lies more than ``COURT["min_below"]`` under the ground, ``yes`` in front of every
    window below the ground, ``no`` (the default here, the M10 build) never; a drawn light well always wins."""
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
        out = outward_side(wall, (outlines or {}).get(lv["id"]) or outline, (cx, cy))      # its own level (#27)
        if out is None:
            continue
        levels_above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, _top, _ = opening_vertical(o, lv, levels_above)
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
        below = gz - bottom
        if front_court == "yes" or (front_court == "auto" and below > COURT["min_below"]):
            wells.append(court_for(o, lv, (cx, cy), out, half_t, gz, below, front_court))
            continue
        w = float(o["width"]) / 2.0 + DEFAULTS["light_well_side"]
        d0, d1 = half_t, half_t + DEFAULTS["light_well_depth"]
        poly = [(cx + ux * s + out[0] * d, cy + uy * s + out[1] * d) for s, d in ((-w, d0), (w, d0), (w, d1), (-w, d1))]
        wells.append({"opening_id": o["id"], "level_id": lv["id"], "polygon": geom2d.ccw(poly),
                      "floor_z": bottom - DEFAULTS["light_well_below_sill"], "top_z": gz, "outward": list(out),
                      "source": "assumed",
                      "reason": f"window sill {bottom:.2f} m, ground outside {gz:.2f} m: an open concrete light "
                                f"well {DEFAULTS['light_well_depth']} m deep, {2 * w:.2f} m wide (no light well drawn)"})
    return merge_courts(wells), warnings


# Milestone 11 (docs/milestone11.md §1.1 E9, decision D6): a sunken front court in front of a deep basement window.
COURT = {"min_below": 1.0, "depth": 3.0, "side": 0.6, "floor_below": 0.05, "parapet": 0.9, "merge_gap": 1.0}


def court_for(opening: dict, level: dict, centre, out, half_t: float, gz: float, below: float, mode: str) -> dict:
    """The inferred front court of one basement window (pure): ``COURT["depth"]`` out from the wall face,
    ``COURT["side"]`` wider than the window on each side, its paved floor ``COURT["floor_below"]`` under the
    basement floor, its retaining walls up to a ``COURT["parapet"]`` parapet above the ground (a drop of over
    1 m needs a guard)."""
    cx, cy = centre
    ux, uy = (-out[1], out[0])
    w = float(opening["width"]) / 2.0 + COURT["side"]
    d0, d1 = half_t, half_t + COURT["depth"]
    poly = [(cx + ux * s + out[0] * d, cy + uy * s + out[1] * d) for s, d in ((-w, d0), (w, d0), (w, d1), (-w, d1))]
    floor_z = float(level["elevation"]) - COURT["floor_below"]
    why = (f"window sill {below:.2f} m below the ground outside (> {COURT['min_below']:g} m)" if mode == "auto"
           else "brief site_options.front_court: yes")
    return {"opening_id": opening["id"], "opening_ids": [opening["id"]], "level_id": level["id"],
            "polygon": geom2d.ccw(poly), "floor_z": floor_z, "top_z": gz, "outward": list(out), "source": "inferred",
            "kind": "front_court", "inferred": True, "curb": COURT["parapet"],
            "reason": f"{why}: an inferred sunken front court {COURT['depth']:g} m deep, {2 * w:.2f} m wide, its floor "
                      f"at the basement floor, a {COURT['parapet']:g} m parapet (decision D6; no court drawn)"}


def merge_courts(wells: list[dict]) -> list[dict]:
    """Front courts on the same facade line whose spans overlap or lie within ``COURT["merge_gap"]`` become one
    court (pure; the other wells unchanged)."""
    courts = [w for w in wells if w.get("kind") == "front_court"]
    if len(courts) < 2:
        return wells
    rest = [w for w in wells if w.get("kind") != "front_court"]
    groups: list[dict] = []
    for c in courts:
        ox, oy = c["outward"]
        ux, uy = -oy, ox
        span = [p[0] * ux + p[1] * uy for p in c["polygon"]]
        depth = [p[0] * ox + p[1] * oy for p in c["polygon"]]
        rec = {"court": c, "u": (ux, uy), "s": (min(span), max(span)), "d": (min(depth), max(depth))}
        for g in groups:
            if g["court"]["outward"] == c["outward"] and abs(g["d"][0] - rec["d"][0]) < 0.05 \
                    and rec["s"][0] <= g["s"][1] + COURT["merge_gap"] and g["s"][0] <= rec["s"][1] + COURT["merge_gap"]:
                g["s"] = (min(g["s"][0], rec["s"][0]), max(g["s"][1], rec["s"][1]))
                g["d"] = (g["d"][0], max(g["d"][1], rec["d"][1]))
                g["court"] = dict(g["court"], opening_ids=g["court"]["opening_ids"] + c["opening_ids"],
                                  floor_z=min(g["court"]["floor_z"], c["floor_z"]), top_z=max(g["court"]["top_z"], c["top_z"]))
                break
        else:
            groups.append(rec)
    out = list(rest)
    for g in groups:
        (ux, uy), (s0, s1), (d0, d1) = g["u"], g["s"], g["d"]
        ox, oy = g["court"]["outward"]
        poly = [(ux * s + ox * d, uy * s + oy * d) for s, d in ((s0, d0), (s1, d0), (s1, d1), (s0, d1))]
        c = dict(g["court"], polygon=geom2d.ccw(poly))
        if len(c["opening_ids"]) > 1:
            c["reason"] += f"; one court for {', '.join(c['opening_ids'])}"
        out.append(c)
    return out


def light_well_faces(well: dict) -> tuple[list, list]:
    """``(verts, faces)`` of a light well: its floor and three walls (``light_well_wall`` thick) from the
    floor to ``light_well_curb`` above the ground; the side against the building stays open."""
    poly = geom2d.ccw(well["polygon"])
    t = DEFAULTS["light_well_wall"]
    z0, z1 = float(well["floor_z"]), float(well["top_z"]) + float(well.get("curb", DEFAULTS["light_well_curb"]))
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
    angle = G.segment_angle_deg(a, b)
    steps = []                                   # [t0, t1, z0, z1]; neighbours at the same heights are joined
    for i in range(k):
        p = G.point_along_segment(a, b, i / k)
        q = G.point_along_segment(a, b, (i + 1) / k)
        g = [ground_z(terrain, *p), ground_z(terrain, *q), ground_z(terrain, *G.segment_midpoint(p, q))]
        z0, z1 = round(min(g) - 0.1, 6), round(max(g) + h, 6)
        if steps and steps[-1][2:] == [z0, z1]:
            steps[-1][1] = (i + 1) / k
        else:
            steps.append([i / k, (i + 1) / k, z0, z1])
    parts, zs = [], []
    for j, (t0, t1, z0, z1) in enumerate(steps):
        mid = G.point_along_segment(a, b, (t0 + t1) / 2.0)
        # Steps overlap by the thickness so they leave no slit; every second one is 2 mm thicker so the overlapping
        # faces are never coplanar (no z-fighting stripes in Cycles).
        reach = length * (t1 - t0) + (t if len(steps) > 1 else 0.0)
        parts.append(geom2d.box((mid[0], mid[1], (z0 + z1) / 2.0), (reach, t + 0.002 * (j % 2), z1 - z0), angle))
        zs += [z0, z1]
    verts, faces = geom2d.merge(parts)
    return verts, faces, {"height": h, "height_assumed": assumed, "thickness": t, "segments": k,
                          "steps": len(steps), "z_range": [round(min(zs), 4), round(max(zs), 4)]}


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
# Milestone 11: the site no drawing gives (docs/milestone11.md §1.1 E11, §7), inferred
# --------------------------------------------------------------------------

INFERRED = {
    "plot_margin": 6.0,          # the plot = the outline's rectangle grown by this when no site plan draws one
    "path_width": 1.2, "entrance_max_rise": 1.5, "step_rise": 0.17, "step_run": 0.30, "landing": 1.2,
    "landing_side": 0.3,
    "hedge_height": 0.6, "hedge_thickness": 0.5, "fence_height": 0.9, "fence_post": 0.08, "fence_rail": 0.04,
    "fence_spacing": 2.0, "gate_gap": 0.4,
    "tree_crown": 3.5, "tree_inset": 2.5, "tree_from_building": 3.5, "tree_from_path": 2.0, "tree_window_reach": 8.0,
    "tree_window_side": 2.0, "tree_spacing": 6.0, "tree_step": 1.0, "front_zone_extra": 2.0,
}


def outer_openings(building: dict, levels: Sequence[dict], outline: Sequence[Sequence[float]],
                   outlines: Optional[dict] = None, kinds=("door", "window")) -> list[dict]:
    """The doors and windows on the outside of the building (pure): ``[{"opening", "level", "centre": (x, y),
    "outward": (x, y), "axis", "bottom", "top", "half_t"}]``, the outward side judged on the opening's own level
    outline."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    ids = {lv["id"]: lv for lv in levels}
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") in ids}
    out = []
    for o in building.get("openings") or []:
        lv = ids.get(o.get("level_id"))
        wall = walls.get(o.get("wall_id"))
        if lv is None or wall is None or o.get("type") not in kinds:
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        side = outward_side(wall, (outlines or {}).get(lv["id"]) or outline, (cx, cy))
        if side is None:
            continue
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, top, _ = opening_vertical(o, lv, above)
        out.append({"opening": o, "level": lv, "centre": (cx, cy), "outward": side, "axis": nearest_axis(side),
                    "bottom": bottom, "top": top, "half_t": float(wall["thickness"]) / 2.0})
    return out


def entrances(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
              outlines: Optional[dict] = None) -> list[dict]:
    """The entrance doors (pure): outside doors whose bottom lies from ``LIGHT_WELL_CLEARANCE`` under to
    ``entrance_max_rise`` over the ground outside (a door higher up opens onto a balcony or a terrace). Each:
    ``{"opening_id", "level_id", "centre", "outward", "axis", "width", "bottom", "ground_z", "rise", "half_t"}``;
    ``rise`` > ``LIGHT_WELL_CLEARANCE`` needs steps."""
    out = []
    for rec in outer_openings(building, levels, outline, outlines, kinds=("door",)):
        cx, cy = rec["centre"]
        ox, oy = rec["outward"]
        gz = ground_z(terrain, cx + ox * (rec["half_t"] + 0.3), cy + oy * (rec["half_t"] + 0.3))
        rise = rec["bottom"] - gz
        if rise < -LIGHT_WELL_CLEARANCE or rise > INFERRED["entrance_max_rise"]:
            continue
        out.append({"opening_id": rec["opening"]["id"], "level_id": rec["level"]["id"], "centre": (cx, cy),
                    "outward": (ox, oy), "axis": rec["axis"], "width": float(rec["opening"]["width"]),
                    "bottom": rec["bottom"], "ground_z": gz, "rise": max(0.0, rise), "half_t": rec["half_t"]})
    return out


def main_facade(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
                outlines: Optional[dict] = None) -> dict:
    """The main (entrance) facade (pure; docs/milestone11.md §4.1 X6, X7, §7): the side with the most entrance
    doors, else the one with the most outside openings, else the drawing's front (-Y). ``{"axis", "direction",
    "source", "opening_ids"}``."""
    ents = entrances(building, levels, terrain, outline, outlines) if len(outline) >= 3 else []
    counts: dict[str, list[str]] = {}
    source = "entrance doors"
    for e in ents:
        counts.setdefault(e["axis"], []).append(e["opening_id"])
    if not counts and len(outline) >= 3:
        source = "most outside openings (no entrance door at grade)"
        for rec in outer_openings(building, levels, outline, outlines):
            counts.setdefault(rec["axis"], []).append(rec["opening"]["id"])
    if not counts:
        return {"axis": "-y", "direction": AXES["-y"], "source": "assumed: the drawing's front (no outside opening)",
                "opening_ids": []}
    order = ("-y", "+y", "-x", "+x")
    axis = max(counts, key=lambda k: (len(counts[k]), -order.index(k)))
    return {"axis": axis, "direction": AXES[axis], "source": source, "opening_ids": counts[axis]}


def inferred_plot(outline: Sequence[Sequence[float]], margin: float = INFERRED["plot_margin"]) -> list:
    """The plot of a project without a site plan: the outline's rectangle grown by ``margin`` (assumed)."""
    return geom2d.ccw(geom2d.rectangle_corners(geom2d.oriented_rectangle(outline), margin))


def ray_exit(p, d, polygon) -> Optional[float]:
    """The distance from ``p`` (inside ``polygon``) along the unit direction ``d`` to the polygon boundary."""
    best = None
    n = len(polygon)
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        rx, ry = a[0] - p[0], a[1] - p[1]
        t = (rx * ey - ry * ex) / den
        s = (rx * d[1] - ry * d[0]) / den
        if t > 1e-9 and -1e-9 <= s <= 1.0 + 1e-9 and (best is None or t < best):
            best = t
    return best


def _rect_along(origin, d, start: float, end: float, half_w: float) -> list:
    ux, uy = -d[1], d[0]
    return geom2d.ccw([(origin[0] + d[0] * t + ux * s, origin[1] + d[1] * t + uy * s)
                       for t, s in ((start, -half_w), (start, half_w), (end, half_w), (end, -half_w))])


def entrance_steps(e: dict) -> dict:
    """The landing and steps in front of an entrance door above the ground (pure; assumed): a landing
    ``landing`` deep at the door's floor, then steps of at most ``step_rise`` and ``step_run`` deep down to the
    ground, as wide as the door + ``landing_side`` on each side. ``{"opening_id", "blocks": [{"polygon",
    "z_top"}], "end": distance from the wall face where the path starts, "count", "rise"}``; no blocks for a door
    at grade."""
    face = (e["centre"][0] + e["outward"][0] * e["half_t"], e["centre"][1] + e["outward"][1] * e["half_t"])
    half_w = e["width"] / 2.0 + INFERRED["landing_side"]
    if e["rise"] <= LIGHT_WELL_CLEARANCE:
        return {"opening_id": e["opening_id"], "blocks": [], "end": 0.0, "count": 0, "rise": 0.0, "face": face}
    n = max(1, int(math.ceil(e["rise"] / INFERRED["step_rise"] - 1e-9)))
    r = e["rise"] / n
    blocks = [{"polygon": _rect_along(face, e["outward"], 0.0, INFERRED["landing"], half_w), "z_top": e["bottom"]}]
    for i in range(1, n):
        a = INFERRED["landing"] + (i - 1) * INFERRED["step_run"]
        blocks.append({"polygon": _rect_along(face, e["outward"], a, a + INFERRED["step_run"], half_w),
                       "z_top": e["bottom"] - i * r})
    return {"opening_id": e["opening_id"], "blocks": blocks, "end": INFERRED["landing"] + (n - 1) * INFERRED["step_run"],
            "count": n - 1, "rise": round(r, 4), "face": face}


def entrance_paths(ents: Sequence[dict], steps: dict, plot: Sequence) -> list[dict]:
    """A path from every entrance (the end of its steps) straight out to the plot edge (pure; assumed),
    ``path_width`` wide; paths of one facade that overlap are one path. ``[{"opening_ids", "polygon", "outward",
    "length"}]``."""
    raw = []
    for e in ents:
        st = steps.get(e["opening_id"]) or {"end": 0.0, "face": e["centre"]}
        face = st["face"]
        reach = ray_exit(face, e["outward"], plot) if plot else None
        if reach is None or reach <= st["end"] + 0.2:
            continue
        half = INFERRED["path_width"] / 2.0
        raw.append({"opening_ids": [e["opening_id"]], "outward": tuple(e["outward"]), "face": face,
                    "start": st["end"], "end": reach + 0.05, "half": half})
    merged: list[dict] = []
    for p in raw:
        ux, uy = -p["outward"][1], p["outward"][0]
        s = p["face"][0] * ux + p["face"][1] * uy
        for m in merged:
            if m["outward"] == p["outward"] and abs(m["s"] - s) <= m["half"] + p["half"] + 1e-6:
                lo, hi = min(m["s"] - m["half"], s - p["half"]), max(m["s"] + m["half"], s + p["half"])
                m["s"], m["half"] = (lo + hi) / 2.0, (hi - lo) / 2.0
                m["opening_ids"] += p["opening_ids"]
                m["start"] = min(m["start"], p["start"])
                m["end"] = max(m["end"], p["end"])
                break
        else:
            merged.append(dict(p, s=s))
    out = []
    for m in merged:
        ox, oy = m["outward"]
        ux, uy = -oy, ox
        d0 = m["face"][0] * ox + m["face"][1] * oy
        origin = (ux * m["s"] + ox * d0, uy * m["s"] + oy * d0)
        out.append({"opening_ids": m["opening_ids"], "outward": list(m["outward"]),
                    "polygon": _rect_along(origin, m["outward"], m["start"], m["end"], m["half"]),
                    "length": round(m["end"] - m["start"], 3), "width": round(2 * m["half"], 3)})
    return out


def boundary_segments(plot: Sequence, paths: Sequence[dict], kind: str) -> list[dict]:
    """The plot edges of the inferred boundary (``hedge`` or ``fence``) with a gate gap where a path crosses
    (pure): ``[{"kind", "start", "end"}]``."""
    out = []
    n = len(plot)
    for i in range(n):
        a, b = plot[i], plot[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-6:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        gaps = []
        for p in paths:
            ts = [(q[0] - a[0]) * ux + (q[1] - a[1]) * uy for q in p["polygon"]]
            ds = [abs((q[0] - a[0]) * -uy + (q[1] - a[1]) * ux) for q in p["polygon"]]
            if min(ds) <= 0.2:
                gaps.append((min(ts) - INFERRED["gate_gap"] / 2.0, max(ts) + INFERRED["gate_gap"] / 2.0))
        t = 0.0
        for g0, g1 in sorted(gaps):
            if g0 > t + 0.05:
                out.append({"kind": kind, "start": (a[0] + ux * t, a[1] + uy * t),
                            "end": (a[0] + ux * min(g0, length), a[1] + uy * min(g0, length))})
            t = max(t, g1)
        if t < length - 0.05:
            out.append({"kind": kind, "start": (a[0] + ux * t, a[1] + uy * t), "end": tuple(b)})
    return out


def boundary_parts(seg: dict, terrain: dict) -> tuple[list, list, dict]:
    """``(verts, faces, info)`` of one boundary segment: a hedge is a stepped box (``plot_wall_parts``) of
    ``hedge_thickness`` x ``hedge_height``; a fence posts every ``fence_spacing`` and two rails."""
    if seg["kind"] == "hedge":
        wall = {"start": seg["start"], "end": seg["end"], "thickness": INFERRED["hedge_thickness"],
                "height": {"value": INFERRED["hedge_height"], "method": "assumed"}}
        return plot_wall_parts(wall, terrain)
    a, b = seg["start"], seg["end"]
    length = G.distance(a, b)
    angle = G.segment_angle_deg(a, b)
    h = INFERRED["fence_height"]
    parts = []
    k = max(1, int(math.ceil(length / INFERRED["fence_spacing"])))
    zs = []
    for i in range(k + 1):
        p = G.point_along_segment(a, b, i / k)
        gz = ground_z(terrain, *p)
        parts.append(geom2d.box((p[0], p[1], gz + h / 2.0 - 0.05), (INFERRED["fence_post"], INFERRED["fence_post"],
                                                                     h + 0.1), angle))
        zs += [gz - 0.1, gz + h]
    mid = G.segment_midpoint(a, b)
    gz = ground_z(terrain, *mid)
    for z in (0.35, h - 0.12):
        parts.append(geom2d.box((mid[0], mid[1], gz + z), (length, INFERRED["fence_rail"], 0.09), angle))
    verts, faces = geom2d.merge(parts)
    return verts, faces, {"height": h, "height_assumed": True, "thickness": INFERRED["fence_post"],
                          "segments": k, "steps": 1, "z_range": [round(min(zs), 4), round(max(zs), 4)]}


def place_trees(plot: Sequence, outline: Sequence, paths: Sequence[dict], windows: Sequence[dict], main: dict,
                count: int) -> list[dict]:
    """Up to ``count`` inferred trees inside the plot (pure; docs/milestone11.md §1.1 E11): candidates every
    ``tree_step`` along the plot edges ``tree_inset`` inside; a candidate is kept ``tree_from_building`` clear
    of the building, ``tree_from_path`` of every path, out of the band in front of every outside window
    (``tree_window_reach`` out, its width + ``tree_window_side`` on each side) and out of the front garden
    (nothing nearer the main facade's side than ``front_zone_extra`` behind its face, so the frontal and corner
    views of the entrance stay open); picked greedily, beside the side facades first (nearest their middle), then
    behind the building, at least ``tree_spacing`` apart. Each tree is site decor ``{"id",
    "kind": "tree", "center", "size", "inferred": true, "reason"}``."""
    if count <= 0 or len(plot) < 3 or len(outline) < 3:
        return []
    inner = geom2d.offset_polygon(plot, INFERRED["tree_inset"])
    if len(inner) < 3:
        return []
    md = main["direction"]
    proj = [p[0] * md[0] + p[1] * md[1] for p in outline]
    across = [p[0] * -md[1] + p[1] * md[0] for p in outline]
    front_edge = max(proj)
    cands = []
    n = len(inner)
    for i in range(n):
        a, b = inner[i], inner[(i + 1) % n]
        length = G.distance(a, b)
        k = max(1, int(length // INFERRED["tree_step"]))
        for j in range(k + 1):
            p = G.point_along_segment(a, b, j / k)
            cands.append((round(p[0], 6), round(p[1], 6)))
    keep = []
    r = INFERRED["tree_crown"] / 2.0
    for p in sorted(set(cands)):
        if G.point_in_polygon(p, outline) or geom2d.distance_to_polygon_edges(p, outline) < INFERRED["tree_from_building"]:
            continue
        if any(G.point_in_polygon(p, q["polygon"]) or geom2d.distance_to_polygon_edges(p, q["polygon"])
               < INFERRED["tree_from_path"] for q in paths):
            continue
        blocked = False
        for w in windows:
            (cx, cy), (ox, oy) = w["centre"], w["outward"]
            dx, dy = p[0] - cx, p[1] - cy
            along, side = dx * ox + dy * oy, abs(dx * -oy + dy * ox)
            if 0.0 < along < INFERRED["tree_window_reach"] + r and \
                    side < float(w["opening"]["width"]) / 2.0 + INFERRED["tree_window_side"] + r:
                blocked = True
                break
        if blocked:
            continue
        pm = p[0] * md[0] + p[1] * md[1]
        pa = p[0] * -md[1] + p[1] * md[0]
        if pm > front_edge - INFERRED["front_zone_extra"]:
            continue                                  # the front garden and the entrance views stay open
        # beside the side facades first (nearest their middle), then behind the building
        rank = 0 if (pa < min(across) or pa > max(across)) else 1
        keep.append((rank, round(abs(pm - (min(proj) + max(proj)) / 2.0), 6) if rank == 0 else round(pm, 6), p))
    keep.sort()
    out = []
    for _rank, _key, p in keep:
        if len(out) >= count:
            break
        if all(G.distance(p, t["center"]) >= INFERRED["tree_spacing"] for t in out):
            out.append({"id": f"tree_inferred_{len(out) + 1}", "kind": "tree", "center": [p[0], p[1]],
                        "size": [INFERRED["tree_crown"], INFERRED["tree_crown"]], "inferred": True,
                        "reason": "no site plan: a tree clear of the windows, the paths and the front garden "
                                  "(inferred, docs/milestone11.md §1.1 E11)"})
    return out


def inferred_site(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
                  outlines: Optional[dict], plot: Sequence, plot_source: str, options: dict,
                  drawn_trees: bool) -> dict:
    """What the build adds where the documents are silent (pure; docs/milestone11.md §1.1 E11, §7, CLAUDE.md
    evidence rules: every item ``inferred`` and listed): the plot (``inferred_plot`` when none is drawn), the
    entrances with their steps, the paths, the boundary (hedge or fence on an inferred plot), the trees (when
    none is drawn). ``options``: ``overrides.site_options``. Returns ``{"plot", "plot_inferred", "main",
    "entrances", "steps", "paths", "boundary", "trees", "assumed"}``."""
    out = {"plot": list(plot), "plot_inferred": False, "main": None, "entrances": [], "steps": [], "paths": [],
           "boundary": [], "trees": [], "assumed": []}
    if len(outline) < 3:
        return out
    if not plot:
        out["plot"] = inferred_plot(outline)
        out["plot_inferred"] = True
        out["assumed"].append({"field": "plot", "value": [[round(x, 3), round(y, 3)] for x, y in out["plot"]],
                               "reason": f"no site plan: the plot is the outline's rectangle + "
                                         f"{INFERRED['plot_margin']:g} m (inferred)"})
    out["main"] = main_facade(building, levels, terrain, outline, outlines)
    ents = entrances(building, levels, terrain, outline, outlines)
    out["entrances"] = [{k: (list(v) if isinstance(v, tuple) else v) for k, v in e.items()} for e in ents]
    steps = {e["opening_id"]: entrance_steps(e) for e in ents}
    out["steps"] = [s for s in steps.values() if s["blocks"]]
    for s in out["steps"]:
        out["assumed"].append({"field": f"steps:{s['opening_id']}", "value": s["count"],
                               "reason": f"entrance door {s['rise'] * (s['count'] + 1):.2f} m above the ground: a "
                                         f"landing and {s['count']} steps of {s['rise']:.3f} m (inferred)"})
    if options.get("path", True):
        out["paths"] = entrance_paths(ents, steps, out["plot"])
        for p in out["paths"]:
            out["assumed"].append({"field": f"path:{','.join(p['opening_ids'])}", "value": p["length"],
                                   "reason": "a paved path from the plot edge to the entrance (inferred)"})
    kind = options.get("fence", "hedge")
    if out["plot_inferred"] and kind in ("hedge", "fence"):
        out["boundary"] = boundary_segments(out["plot"], out["paths"], kind)
        out["assumed"].append({"field": "boundary", "value": kind,
                               "reason": f"no site plan: a low {kind} on the inferred plot boundary (inferred)"})
    if not drawn_trees:
        windows = outer_openings(building, levels, outline, outlines, kinds=("window",))
        out["trees"] = place_trees(out["plot"], outline, out["paths"], windows, out["main"], int(options.get("trees", 3)))
    return out


# --------------------------------------------------------------------------
# The plan of the site (pure) and the Blender objects
# --------------------------------------------------------------------------

def _built(items) -> list[dict]:
    return [i for i in items or [] if isinstance(i, dict) and i.get("build", True) is not False]


def set_back_levels(levels: Sequence[dict], outline: Sequence[Sequence[float]], outlines: dict, terrain: dict,
                    tol_m2: float = 0.05) -> list[str]:
    """Warnings for the levels below the ground whose own outline differs from the ground hole ``outline`` (pure;
    review #27): a basement set back from (or reaching past) the ground floor's faces leaves an open gap between
    the terrain and its walls (or walls in the earth)."""
    hole = G.polygon_area(outline) if len(outline) >= 3 else 0.0
    top = max(float(z) for z in terrain["z"].values()) if terrain.get("z") else 0.0
    out = []
    for lv in levels:
        own = outlines.get(lv["id"]) or []
        if len(own) < 3 or float(lv["elevation"]) >= top - 0.5:
            continue
        diff = G.polygon_area(own) - hole
        inside = all(G.point_in_polygon(p, outline) or geom2d.distance_to_polygon_edges(p, outline) < 1e-3
                     for p in own)
        if abs(diff) > tol_m2 or not inside:
            out.append(f"{lv['id']}: its outline ({G.polygon_area(own):.2f} m2) differs from the ground hole cut at "
                       f"the outline of the levels at the ground ({hole:.2f} m2): "
                       + ("the gap between its walls and the terrain is open" if diff < 0 and inside
                          else "part of its walls stands in the earth"))
    return out


def site_plan(building: dict, levels: Sequence[dict], outline: Sequence[Sequence[float]], mode: str = "full",
              outlines: Optional[dict] = None, options: Optional[dict] = None) -> dict:
    """Everything the site build makes (pure): ``{"mode", "terrain", "outline", "plot", "extent", "wells",
    "plot_walls", "areas": [{"id", "kind", "polygon", "z", "material", "source"}], "trees", "not_built",
    "assumed", "warnings", "ground_is_grass"}``. ``mode`` ``full`` (plot, paving, grass, plot walls,
    parking, trees as drawn) or ``ground`` (the ground plane and the light wells). ``outlines``: each level's own
    outline (review #27: a wall's outward side for its light well or basement door is judged on its level's
    outline, and a level below the ground that differs from the ground hole is a warning).

    Milestone 11 (docs/milestone11.md §1.1 E9, E11, §7): ``options`` (``overrides.site_options``: the brief's
    ``front_court`` and the agent's site keys; None = the M10 site) makes the front courts (D6) and, with
    ``site: full``, the inferred site (``inferred_site``: the plot when none is drawn, entrance steps, paths, a
    hedge or fence, trees when none is drawn), returned under ``inferred``; the paths are areas of kind ``path``,
    the inferred trees join ``trees``; every inferred item is in ``assumed``."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    lowest = min(levels, key=lambda lv: float(lv["elevation"])) if levels else None
    default_z = 0.0 if lowest is None or float(lowest["elevation"]) < 0 else float(lowest["elevation"])
    terrain = terrain_model(building, outline, default_z)
    doors = door_terrain(building, levels, terrain, outline, outlines)
    if doors:                                   # the basement doors' sides at their floor (assumed)
        terrain = terrain_model(building, outline, default_z, overrides=doors)
    plot, plot_src = plot_polygon(building) if mode == "full" else ([], "none")
    # Flat ground reaches the horizon (HORIZON_M); a sloped one keeps MARGIN_M.
    extent = ground_extent(outline, plot, HORIZON_M if is_flat(terrain) else MARGIN_M)
    court = (options or {}).get("front_court") or "no"
    wells, warnings = light_wells(building, levels, terrain, outline, outlines,
                                  front_court=court if options is not None else "no")
    warnings = list(terrain["warnings"]) + warnings + set_back_levels(levels, outline, outlines or {}, terrain)
    assumed = list(terrain["assumed"])
    for w in wells:
        if w["source"] in ("assumed", "inferred"):
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
                              "material": a.get("material"), "colour": a.get("colour"), "source": a.get("source"),
                              "area_id": a.get("area_id"), "lift": lift})
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
        for a in site.get("areas") or []:            # label records (build: false, §1.6b row 12)
            if isinstance(a, dict):
                not_built.append({"id": a.get("id"), "kind": f"area:{a.get('kind')}",
                                  "reason": "exterior label: its surface is built from site.paving / parking / grass"})
    else:
        not_built.append({"id": None, "kind": "site", "reason": "brief site: ground (the ground plane and the "
                                                                "light wells only)"})
    inferred = None
    if mode == "full" and options is not None:
        drawn_trees = any(t.get("kind") == "tree" for t in trees)
        inferred = inferred_site(building, levels, terrain, outline, outlines, plot, plot_src, options, drawn_trees)
        assumed += inferred["assumed"]
        for p in inferred["paths"]:
            areas.append({"id": f"path_{'_'.join(p['opening_ids'])}", "kind": "path", "polygon": p["polygon"],
                          "z": None, "material": None, "colour": None, "source": "assumed", "area_id": None,
                          "lift": PAVING_LIFT, "inferred": True})
        for t in inferred["trees"]:
            trees.append(t)
            assumed.append({"field": f"tree:{t['id']}", "value": t["center"], "reason": t["reason"]})
    return {"mode": mode, "terrain": terrain, "outline": geom2d.ccw(outline), "plot": plot, "plot_source": plot_src,
            "extent": extent, "wells": wells, "plot_walls": plot_walls, "areas": areas, "trees": trees,
            "not_built": not_built, "assumed": assumed, "warnings": warnings, "ground_is_grass": ground_is_grass,
            "inferred": inferred}


# The look of each built area kind (exterior.resolve_looks slots) when the area names no material of its own.
AREA_LOOKS = {"grass": "garden", "paving": "paving", "parking": "paving", "path": "paving"}


def area_look(area: dict, looks: dict) -> dict:
    """The look of a built site area (pure): its own drawn ``material`` / ``colour`` (documents), else the
    resolved look of its kind (``AREA_LOOKS``)."""
    if area.get("material"):
        return {"material": area["material"], "colour": area.get("colour"), "source": "documents",
                "assumed": False, "reason": f"site {area['kind']} {area.get('id')}: drawn material"}
    return looks[AREA_LOOKS.get(area["kind"], "paving")]


def build_site(plan: dict, collection, looks: dict, make_material, manifest_objects: list, assumed: list) -> dict:
    """The site objects of ``site_plan``: the ground (kind ``terrain``), ``lightwell_<opening>`` (kind
    ``light_well``), the plot walls (``site_wall``, their ids), the areas (``site_area``, their ids) and
    ``tree_<id>`` (``site_decor``: trunk and crown in one object, two slots). ``looks``: the resolved looks
    (``exterior.resolve_looks``: ``garden``, ``paving``, ``plot_wall``, ``light_well``, ``bark``, ``foliage``,
    ``ground``); ``make_material(look)`` gives the Blender material. Returns the summary for the scene
    manifest (with the build's terrain changes for basement doors and the light wells)."""
    from wenart.blender import common

    terrain = plan["terrain"]
    holes = [plan["outline"]] + [w["polygon"] for w in plan["wells"]]
    summary = {"built": True, "mode": plan["mode"], "objects": [],
               "reason": f"brief site: {plan['mode']} (docs/milestone10.md §3.2 item 5)", "terrain": {
        "kind": terrain["kind"], "z": {k: round(v, 4) for k, v in terrain["z"].items()}, "sides": terrain["sides"],
        "north_deg": terrain["north_deg"], "north_source": terrain["north_source"],
        "changes": terrain.get("changes") or []},
        "light_wells": [{"opening_id": w["opening_id"], "level_id": w["level_id"], "source": w["source"],
                         "floor_z": round(w["floor_z"], 4), "top_z": round(w["top_z"], 4), "reason": w["reason"],
                         **({"kind": w["kind"], "inferred": True, "opening_ids": w["opening_ids"]}
                            if w.get("kind") == "front_court" else {})}
                        for w in plan["wells"]],
        "plot_source": plan["plot_source"], "not_built": plan["not_built"], "warnings": plan["warnings"]}

    def entry(name, wid, kind, mat, status, extra):
        manifest_objects.append({"name": name, "wenart_id": wid, "kind": kind, "status": status, "level_id": None,
                                 "element_id": wid, "evidence": [], "material": mat.name if mat else None,
                                 "textured": False, "pass_index": None, **extra})
        summary["objects"].append(name)

    ground_look = looks["garden"] if plan["ground_is_grass"] or plan["mode"] == "full" else looks["ground"]
    ground_mat = make_material(ground_look)
    verts, faces = draped_faces(plan["extent"], holes, terrain)
    ob = common.new_mesh_object("ground", verts, faces, collection=collection, wenart_id="ground", kind="terrain",
                                status="assumed", materials=[ground_mat])
    zs = [v[2] for v in verts] or [0.0]
    entry(ob.name, "ground", "terrain", ground_mat, "assumed",
          {"assumed": {"extent": [list(p) for p in plan["extent"]], "terrain": terrain["kind"],
                       "reason": "ground plane around the building (the levels per side as drawn, the rest assumed)"},
           "z_range": [round(min(zs), 4), round(max(zs), 4)], "look_source": ground_look.get("source")})
    well_mat = make_material(looks["light_well"])
    for w in plan["wells"]:
        v, f = light_well_faces(w)
        name = f"{'court' if w.get('kind') == 'front_court' else 'lightwell'}_{w['opening_id']}"
        status = "verified" if w["source"] == "drawn" else "assumed"
        ob = common.new_mesh_object(name, v, f, collection=collection, wenart_id=name, kind="light_well",
                                    status=status, materials=[well_mat])
        entry(ob.name, name, "light_well", well_mat, status,
              {"assumed": {} if w["source"] == "drawn" else {"reason": w["reason"]}, "parent": w["opening_id"],
               "z_range": [round(w["floor_z"], 4),
                           round(w["top_z"] + float(w.get("curb", DEFAULTS["light_well_curb"])), 4)],
               **({"well_kind": "front_court", "inferred": True, "opening_ids": w["opening_ids"]}
                  if w.get("kind") == "front_court" else {})})
    wall_mat = make_material(looks["plot_wall"]) if plan["plot_walls"] else None
    for wall in plan["plot_walls"]:
        v, f, info = plot_wall_parts(wall, terrain)
        wid = str(wall.get("id") or f"plot_wall_{len(summary['objects'])}")
        ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site_wall",
                                    status="verified", materials=[wall_mat])
        entry(ob.name, wid, "site_wall", wall_mat, "verified",
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
        look = area_look(area, looks)
        mat = make_material(look)
        wid = str(area.get("id") or f"{area['kind']}_{len(summary['objects'])}")
        status = "assumed" if area.get("source") == "assumed" else "verified"
        ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site_area", status=status,
                                    materials=[mat])
        entry(ob.name, wid, "site_area", mat, status,
              {"assumed": {"lift_m": area["lift"]} if z is not None else {"lift_m": area["lift"], "draped": True},
               "area_kind": area["kind"], "area_id": area.get("area_id"), "slug": look.get("material"),
               "colour": look.get("colour"), "look_source": look.get("source")})
    bark, foliage = (make_material(looks["bark"]), make_material(looks["foliage"])) if plan["trees"] else (None, None)
    for item in plan["trees"]:
        parts = tree_parts(item, terrain)
        wid = f"tree_{item.get('id') or len(summary['objects'])}"
        meshes = [m for m in (parts["trunk"], parts["crown"]) if m is not None]
        v, f = geom2d.merge(meshes)
        slots = ([0] * len(parts["trunk"][1]) if parts["trunk"] else []) + [1] * len(parts["crown"][1])
        ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site_decor",
                                    status="assumed", materials=[bark, foliage], face_material_indices=slots)
        entry(ob.name, wid, "site_decor", foliage, "assumed",
              {"evidence": item.get("evidence") or [], "parent": item.get("id"),
               "assumed": {"height_m": parts["height"], "reason": parts["reason"]}, "site_kind": item.get("kind")})
        assumed.append({"object": wid, "field": "tree", "value": parts["height"], "reason": parts["reason"],
                        "parent": str(item.get("id")), "kind": "site_tree"})
    inferred = plan.get("inferred")
    if inferred:                                     # Milestone 11 E11: steps and the boundary (inferred)
        step_mat = make_material(looks.get("steps") or looks["paving"]) if inferred["steps"] else None
        for st in inferred["steps"]:
            parts = []
            for blk in st["blocks"]:
                z0 = min(ground_z(terrain, *p) for p in blk["polygon"]) - 0.1
                parts.append(geom2d.prism(blk["polygon"], z0, blk["z_top"]))
            v, f = geom2d.merge(parts)
            wid = f"steps_{st['opening_id']}"
            ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site_steps",
                                        status="assumed", materials=[step_mat])
            entry(ob.name, wid, "site_steps", step_mat, "assumed",
                  {"parent": st["opening_id"], "inferred": True,
                   "assumed": {"steps": st["count"], "rise_m": st["rise"], "reason": "entrance above the ground: a "
                                                                                     "landing and steps (inferred)"}})
        kinds = sorted({seg["kind"] for seg in inferred["boundary"]})
        for kind in kinds:
            segs = [seg for seg in inferred["boundary"] if seg["kind"] == kind]
            look = looks.get(kind) or (looks["foliage"] if kind == "hedge" else {"material": "wood_cladding",
                                                                                   "colour": None})
            mat = make_material(look)
            parts = [boundary_parts(seg, terrain)[:2] for seg in segs]
            v, f = geom2d.merge(parts)
            wid = f"boundary_{kind}"
            ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site_boundary",
                                        status="assumed", materials=[mat])
            entry(ob.name, wid, "site_boundary", mat, "assumed",
                  {"inferred": True, "boundary_kind": kind, "segments": len(segs),
                   "assumed": {"height_m": INFERRED[f"{kind}_height"], "reason": f"no site plan: a low {kind} on the "
                                                                                 f"inferred plot boundary (inferred)"}})
        summary["inferred"] = {
            "plot": [[round(x, 3), round(y, 3)] for x, y in inferred["plot"]], "plot_inferred": inferred["plot_inferred"],
            "main_facade": inferred["main"], "entrances": [e["opening_id"] for e in inferred["entrances"]],
            "steps": [{"opening_id": s["opening_id"], "count": s["count"], "rise": s["rise"]} for s in inferred["steps"]],
            "paths": [{"opening_ids": p["opening_ids"], "length": p["length"], "width": p["width"]}
                      for p in inferred["paths"]],
            "boundary": kinds[0] if kinds else None, "trees": [t["id"] for t in inferred["trees"]]}
    for a in plan["assumed"]:
        assumed.append({"object": "site", "field": a["field"], "value": a["value"], "reason": a["reason"]})
    return summary
