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

Milestone 12 (docs/milestone12.md §3.3-§3.4, track L): the terrain surface ``site.ground.surface`` of kind
``planar`` or ``tin`` (ground marks, ``wenart.levels.terrain``) is the ground where the pipeline wrote one
(``terrain_model`` kind ``planar`` / ``tin``, ``ground_z`` evaluates it, flat beyond the points; the basement doors'
side changes do not apply to it, a warning); the entrances come from ``site.entrances`` when the pipeline wrote them
(``wenart.levels.model``: threshold, ground, steps with their riser, tread and intermediate landings, the landing,
a ramp along the facade, handrails and cheek walls: ``entrance_steps``, ``entrance_meshes``); a light well record
of ``source: assumed`` in the building JSON (the pipeline's copy of the build's own rule) is not a drawn one.

Milestone 13 (docs/milestone13.md §13.2, track T6; CLAUDE.md vegetation and site rules, user OK of 12 Oct 2026):

- ``tree_height(crown_radius_m)`` gives the height and the size class by the crown (shrub under a 1.5 m crown
  radius, small 1.5-2.5 m -> 4-6 m, medium 2.5-4 m -> 6-10 m, large over 4 m -> 10-15 m); the 4 m minimum that
  turned real04's 0.36 m shrub symbols into 4 m trees is gone. ``climate_of`` reads the project's climate (the brief,
  else the drawing's language: Turkish labels -> Mediterranean / Anatolian species) and ``species_for`` names an
  inferred species per size class; ``tree_parts`` keeps the low-poly proxy (the camera model's obstacle) and names
  the species.
- ``hedges_of``: the building's ``site.hedges`` (the sheets stage, ``wenart.sheets.exterior.hedge_rows``), else the
  same detector over the site decor's tree symbols (the committed buildings carry none); ``hedge_parts`` is the
  hedge volume following the ground (the camera model's low obstacle and the leaf-card hedge's core).
- ``platforms(site)``: one level per drawn terrace, pool or parking polygon from the level marks inside it (else
  the ground under it), with its edge treatment (retaining walls where the ground lies below or above the level,
  kerbs, steps on the lowest edge); ``platform_parts`` builds the slab, the walls, the kerb and the steps. Pools
  get a coping ring, a basin clipped under the deck, tiles and a water slab with ripples and absorption
  (``pool_parts`` v2). The ground beyond the sloped ground's rectangle (``skirt_faces``) and a rising backdrop
  ring to the clip distance (``backdrop_faces``) keep the horizon in the image; the haze is a closed hollow mesh
  volume (``haze_box``; a World volume would kill the sun and the sky).
- ``build_site`` keeps its signature; the vegetation objects come from ``wenart.blender.vegetation`` (Poly Haven
  CC0 instances near the cameras, Sapling species-look trees elsewhere, geometry-nodes hedges and grass); the
  A/B switches of ``scripts/jobs/site_ab.sh`` are ``site_levers`` (``WENART_SITE_VARIANT``).

Round 3 (pod P1 of 15 Oct 2026, docs/milestone13.md §14.3): no retaining wall taller than ``RETAINING_MAX_M``
(``stepped_bands``: a larger level difference becomes stepped terraces with intermediate platforms, each with its own
wall; every platform record says ``wall_max_m`` and the terrain under it); the hedge core is a hull with rounded
shoulders (``hedge_hull_profile``); the lawn material gets its tiling and variation (``vegetation.lawn_material``);
``terrain_record`` never raises on a bare terrain record.

Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 attempt 2, P3's real04 exterior views):

- plants stand on the surface under them: ``stand_terrain`` gives the terrain model the flat platforms' levels
  (``stand``; ``ground_z`` of a point inside one is its level), and ``tree_parts`` / ``hedge_parts`` take it in
  ``build_site`` and in the exterior camera model. P3 built every hedge and shrub on the terrain under the
  terraces: real04's hedge_003 stood 1.2-1.8 m under the -3.0 m terrace sp_001, so its hull showed only as dark
  triangles and loose leaf cards on the terrace's retaining wall, and shrubs on the stepped bands were buried;
- ``fit_hedges`` keeps a hedge's hull on its planting side: a hedge on a terrace stays on the slab (inside its
  edges by half its width), a hedge beside a terrace or the building stays outside its retaining wall or facade;
  the polyline moves at most ``HEDGE_FIT["max_shift_m"]``, else the hedge gets narrower (never under
  ``min_width_m``); the hedge records ``fit`` (drawn polyline and width, the shift, the reason) and an ``assumed``
  entry;
- the lawn's far relief only goes down (``vegetation.LAWN_RELIEF``) and keeps every edge of the ground at its level:
  P3's +-3 cm relief pushed the lawn through the paving (lifted ``PAVING_LIFT`` = 1.2 cm) of the paths;
- ``SITE_FALLBACK_LOOKS`` names the slugs the builder puts on by itself (``exterior.build_finish_slugs``: their
  texture sets are fetched since).

Fix round part 2 (17 Oct 2026; review of part 1):

- the down-only lawn relief lowered the lawn under everything placed at terrain height (bpy 5.2.2, a sloped synthetic
  site: a draped path and a sloped parking 2.1 / 2.0 cm over the lawn with no edge under them, a shrub's and a tree's
  base 2.6 / 2.8 cm in the air). ``relief_keep`` lists the footprints the relief leaves level (the ground's holes,
  the draped areas, the sloped platforms, the inferred entrance steps, every tree, shrub and hedge), ``build_site``
  gives them to ``vegetation.lawn_relief`` with ``vegetation.relief_reach`` (the margin plus a ground cell's
  diagonal); measured again: 0 cm under the path, the parking and the shrub, 0.1 cm at the tree (the mesh's own
  interpolation);
- the near-camera grass gets the relief only when the ground got one (``summary["grass"]``: ``relief``,
  ``relief_requested``, ``relief_reason``): on a flat site the ground of convex pieces has no inner vertex, so no
  relief, and the clumps sank 2.1 cm into it; the grass surface takes the ground's keep polygons, reach and grid.

Fix round after P4b (17 Oct 2026; pod P4b, real03, the look lens's "bare paddock", verified in part): the documents
draw no planting and ``place_trees`` kept none of its 122 candidates on real03 (a 33 m bungalow with 22 outside
windows: their 8 m window bands removed 108), silently. When its first pass places fewer than ``TREE_RELAXED
["tree_min"]`` trees, a second pass narrows the window band (4 m out, 1 m on each side) and keeps every other rule
(the building, the paths, the corner views' lines of sight, the front garden; no tree at the plot corners): real03
gets 2 trees behind the building, real02 keeps its 2 first-pass trees. Every build that infers trees lists
``inferred trees: placed k of n`` with the filter that removed the most candidates (``trees_record``: an ``assumed``
entry, a site warning when short, ``inferred.tree_stats`` and the manifest's ``site.inferred.tree_stats``). The
agent's fence choice stays; the exterior framing is not changed (the camera policy of Milestone 11 stays).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.shell import outward_side
from wenart.levels import terrain as LT

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
    "tree_height_factor": 1.6, "trunk_radius": 0.12, "crown_share": 0.6,
    "plant_height": 0.8, "shrub_height_factor": 1.2,
}
# Milestone 13 (T6): the tree size classes by the crown radius (docs/milestone13.md §13.2): the height is
# tree_height_factor x the crown diameter clamped to the class range; a crown under 1.5 m radius is a shrub.
TREE_CLASSES = (("shrub", 0.0, 1.5, 0.4, 3.0), ("small", 1.5, 2.5, 4.0, 6.0), ("medium", 2.5, 4.0, 6.0, 10.0),
                ("large", 4.0, math.inf, 10.0, 15.0))      # (class, r_min, r_max, h_min, h_max)
AXES = {"+x": (1.0, 0.0), "-x": (-1.0, 0.0), "+y": (0.0, 1.0), "-y": (0.0, -1.0)}
# Drawing-relative sides (no north known): the plan's bottom edge is the front.
SIDE_DIRECTIONS = {"north": "+y", "south": "-y", "east": "+x", "west": "-x",
                   "front": "-y", "back": "+y", "left": "-x", "right": "+x"}
COMPASS = {"north": 0.0, "east": 90.0, "south": 180.0, "west": 270.0}


def tree_height(crown_radius_m: float) -> tuple[float, str]:
    """``(height_m, size_class)`` of a tree from its crown radius (pure; Milestone 13 T6): ``shrub`` under a
    1.5 m crown radius (``shrub_height_factor`` x the diameter, 0.4-3.0 m), ``small`` 1.5-2.5 m -> 4-6 m,
    ``medium`` 2.5-4 m -> 6-10 m, ``large`` over 4 m -> 10-15 m (``tree_height_factor`` x the diameter clamped to
    the class range). No 4 m minimum: a 0.36 m symbol is a 0.86 m shrub."""
    r = max(0.0, float(crown_radius_m))
    for cls, r0, r1, h0, h1 in TREE_CLASSES:
        if r0 <= r < r1:
            factor = DEFAULTS["shrub_height_factor"] if cls == "shrub" else DEFAULTS["tree_height_factor"]
            return round(min(h1, max(h0, factor * 2.0 * r)), 3), cls
    return 15.0, "large"


# The inferred species per climate and size class (user OK of 12 Oct 2026: species not named in the documents
# are inferred and named in the report). The Mediterranean / Anatolian set for Turkish projects, a temperate set
# otherwise; every name is a key of wenart.blender.vegetation.SPECIES.
SPECIES_BY_CLIMATE = {
    "mediterranean": {"shrub": "oleander", "small": "olive", "medium": "stone_pine", "large": "plane",
                      "hedge_low": "boxwood", "hedge_mid": "cherry_laurel", "hedge_high": "cypress_hedge"},
    "temperate": {"shrub": "privet_shrub", "small": "birch", "medium": "maple", "large": "oak",
                  "hedge_low": "boxwood", "hedge_mid": "privet", "hedge_high": "hornbeam"},
}
# Words of the documents (room and site labels, the brief) that tell the climate; Turkish -> Mediterranean.
CLIMATE_WORDS = {
    "mediterranean": ("salon", "mutfak", "banyo", "yatak", "oda", "hol", "otopark", "havuz", "bahce", "bahçe",
                      "teras", "giris", "giriş", "kat", "villa", "akdeniz", "mediterranean", "ege", "beykoz",
                      "istanbul", "izmir", "antalya", "mugla", "muğla", "bodrum", "türkiye", "turkiye", "turkey"),
}


def climate_of(building: dict) -> dict:
    """The project's climate for the inferred species (pure): ``{"climate": "mediterranean" | "temperate",
    "source", "inferred": True, "evidence": [words]}``. The brief (``project.brief.climate`` / ``site.climate``, or
    climate words in its style text) first, else the drawing's language (``CLIMATE_WORDS`` in the room and site
    labels: a Turkish plan is a Mediterranean / Anatolian site), else temperate."""
    project = building.get("project") if isinstance(building.get("project"), dict) else {}
    brief = project.get("brief") if isinstance(project.get("brief"), dict) else {}
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    for src, value in (("brief.climate", brief.get("climate")), ("site.climate", site.get("climate")),
                       ("brief.site.climate", (brief.get("site") or {}).get("climate")
                        if isinstance(brief.get("site"), dict) else None)):
        if isinstance(value, str) and value.strip().lower() in SPECIES_BY_CLIMATE:
            return {"climate": value.strip().lower(), "source": src, "inferred": False, "evidence": [value]}
    texts = [str(brief.get("style") or ""), str(project.get("name") or ""), str(project.get("id") or "")]
    texts += [str(r.get("label_raw") or r.get("label") or "") for r in building.get("rooms") or [] if isinstance(r, dict)]
    texts += [str(a.get("label_raw") or a.get("label") or "") for a in site.get("areas") or [] if isinstance(a, dict)]
    blob = " ".join(texts).lower()
    hits = []
    for climate, words in CLIMATE_WORDS.items():
        for w in words:
            if w and w in blob:
                hits.append(w)
        if len(hits) >= 2:
            return {"climate": climate, "source": "the drawing's language (room and site labels)", "inferred": True,
                    "evidence": sorted(set(hits))[:8]}
    return {"climate": "temperate", "source": "no climate word in the brief or the labels: temperate assumed",
            "inferred": True, "evidence": []}


def species_for(size_class: str, climate: str = "temperate", kind: str = "tree") -> str:
    """The inferred species name of a tree size class (``shrub`` / ``small`` / ``medium`` / ``large``) or a hedge
    height class (``kind`` ``hedge``: ``low`` / ``mid`` / ``high``) in a climate (``SPECIES_BY_CLIMATE``)."""
    table = SPECIES_BY_CLIMATE.get(climate) or SPECIES_BY_CLIMATE["temperate"]
    key = f"hedge_{size_class}" if kind == "hedge" else size_class
    return table.get(key) or table["small"]


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
    surface = ground.get("surface") if isinstance(ground.get("surface"), dict) else None
    if surface and surface.get("kind") in ("planar", "tin") and len(surface.get("points") or []) >= 3:
        # Milestone 12: the terrain surface from ground marks (wenart.levels.terrain).
        for axis in sorted(overrides or {}):
            warnings.append(f"{', '.join((overrides[axis].get('opening_ids') or []))}: below the drawn terrain "
                            f"surface on the {axis} side; the surface is kept")
        mid = ((rect[0] + rect[2]) / 2.0, (rect[1] + rect[3]) / 2.0)
        probe = {"+x": (rect[2] + 0.5, mid[1]), "-x": (rect[0] - 0.5, mid[1]), "+y": (mid[0], rect[3] + 0.5),
                 "-y": (mid[0], rect[1] - 0.5)}
        zs = {k: LT.surface_z(surface, *p) for k, p in probe.items()}
        if surface.get("inferred"):
            assumed.append({"field": "terrain", "value": surface["kind"],
                            "reason": surface.get("reason") or "terrain surface inferred"})
        return {"kind": surface["kind"], "z": zs, "rect": rect, "sides": sides, "assumed": assumed,
                "warnings": warnings, "north_deg": north, "north_source": north_src, "changes": [],
                "surface": surface}
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
    """The ground level at ``(x, y)`` (``terrain_model``). A model of ``stand_terrain`` (fix round after P3) gives a
    point inside one of its flat platforms that platform's level (the highest one when they overlap)."""
    for poly, level in model.get("stand") or ():
        if G.point_in_polygon((x, y), poly):
            return float(level)
    z = model["z"]
    if model["kind"] == "flat":
        return float(z["+x"])
    if model["kind"] in ("planar", "tin") and model.get("surface"):
        return LT.surface_z(model["surface"], x, y)
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


def stand_terrain(terrain: dict, platforms: Sequence[dict] = ()) -> dict:
    """The surface plants stand on (pure; fix round after P3, 16-17 Oct 2026): ``terrain`` with ``stand``, the
    polygon and level of every platform with a flat slab (``platforms``; a sloped one is draped on the terrain), the
    highest first, so ``ground_z`` gives a tree, a shrub or a hedge on a terrace the terrace's level. ``terrain``
    itself when no platform has a flat slab. The ground mesh, the walls and the platforms keep using ``terrain``."""
    stand = sorted(((geom2d.ccw([(float(p[0]), float(p[1])) for p in pf["polygon"]]), float(pf["z"]))
                    for pf in platforms or () if not pf.get("sloped") and len(pf.get("polygon") or []) >= 3),
                   key=lambda r: -r[1])
    return dict(terrain, stand=stand) if stand else terrain


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


SKIRT_STEP_M = 5.0


def skirt_faces(extent: Sequence[Sequence[float]], terrain: dict, reach: float = HORIZON_M,
                step: float = SKIRT_STEP_M) -> tuple[list, list]:
    """The ground beyond a sloped ground's rectangle to the horizon (pure; 11 Oct 2026, real04: the site view looked
    down past the 15 m margin into a black world). The inner edge follows the ground (``ground_z`` every ``step``),
    the outer edge ``reach`` away lies at the ground's level there (the surface is flat beyond its marks). Quads
    face up."""
    x0, y0 = min(p[0] for p in extent), min(p[1] for p in extent)
    x1, y1 = max(p[0] for p in extent), max(p[1] for p in extent)
    X0, Y0, X1, Y1 = x0 - reach, y0 - reach, x1 + reach, y1 + reach

    def ticks(a: float, b: float) -> list[float]:
        n = max(1, int(math.ceil((b - a) / step)))
        return [a + (b - a) * k / n for k in range(n + 1)]

    verts: list = []
    faces: list = []

    def v(x: float, y: float) -> int:
        verts.append((x, y, ground_z(terrain, x, y)))
        return len(verts) - 1

    # each side: inner points along it and their outward projections; corners join two outer points
    sides = [([(x, y0) for x in ticks(x0, x1)], (0.0, Y0 - y0)),           # south, outward -y
             ([(x1, y) for y in ticks(y0, y1)], (X1 - x1, 0.0)),           # east, outward +x
             ([(x, y1) for x in reversed(ticks(x0, x1))], (0.0, Y1 - y1)),  # north, outward +y
             ([(x0, y) for y in reversed(ticks(y0, y1))], (X0 - x0, 0.0))]  # west, outward -x
    for pts, (dx, dy) in sides:
        inner = [v(x, y) for x, y in pts]
        outer = [v(x + dx, y + dy) for x, y in pts]
        for k in range(len(pts) - 1):
            faces.append((inner[k], outer[k], outer[k + 1], inner[k + 1]))   # ccw seen from above (outside the rect)
    for cx, cy, ox, oy in ((x0, y0, X0, Y0), (x1, y0, X1, Y0), (x1, y1, X1, Y1), (x0, y1, X0, Y1)):
        a, b, c, d = v(cx, cy), v(cx, oy), v(ox, oy), v(ox, cy)
        quad = (a, b, c, d)
        area = sum(verts[quad[i]][0] * verts[quad[(i + 1) % 4]][1] - verts[quad[(i + 1) % 4]][0] * verts[quad[i]][1]
                   for i in range(4))
        faces.append(quad if area > 0 else tuple(reversed(quad)))
    return verts, faces


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
        # pre-flight of pod P3: two points of a clipped cell within the 0.1 mm key share one vertex, so a face could
        # use a vertex twice (real04: 732 ground and 112 grass faces, "Mesh ground is not valid" in the glTF export);
        # the repeated corner is dropped and a face of fewer than 3 distinct vertices is not made
        ids = [i for k, i in enumerate(ids) if i != ids[k - 1]] if len(ids) > 1 else ids
        if not tri and len(set(ids)) == len(ids) >= 3:
            faces.append(ids)
            return
        for k in range(1, len(ids) - 1):               # a fan; a piece that still repeats a vertex is fanned too
            if len({ids[0], ids[k], ids[k + 1]}) == 3:
                faces.append([ids[0], ids[k], ids[k + 1]])

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
    # Milestone 12: the pipeline's copy of this rule (``source: assumed``, inferred) is no drawn light well.
    drawn = {w.get("opening_id"): w for w in ((site.get("ground") or {}).get("light_wells") or [])
             if isinstance(w, dict) and w.get("opening_id") and w.get("source", "drawn") == "drawn"}
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
                          "sill_z": bottom, "reason": "drawn light well"})
            continue
        ux, uy = (-out[1], out[0])
        below = gz - bottom
        if front_court == "yes" or (front_court == "auto" and below > COURT["min_below"]):
            wells.append(dict(court_for(o, lv, (cx, cy), out, half_t, gz, below, front_court), sill_z=bottom))
            continue
        w = float(o["width"]) / 2.0 + DEFAULTS["light_well_side"]
        d0, d1 = half_t, half_t + DEFAULTS["light_well_depth"]
        poly = [(cx + ux * s + out[0] * d, cy + uy * s + out[1] * d) for s, d in ((-w, d0), (w, d0), (w, d1), (-w, d1))]
        wells.append({"opening_id": o["id"], "level_id": lv["id"], "polygon": geom2d.ccw(poly),
                      "floor_z": bottom - DEFAULTS["light_well_below_sill"], "top_z": gz, "outward": list(out),
                      "source": "assumed", "sill_z": bottom,
                      "reason": f"window sill {bottom:.2f} m, ground outside {gz:.2f} m: an open concrete light "
                                f"well {DEFAULTS['light_well_depth']} m deep, {2 * w:.2f} m wide (no light well drawn)"})
    return merge_courts(wells), warnings


def wells_on_platforms(wells: Sequence[dict], pfs: Sequence[dict]) -> tuple[list[dict], list[dict]]:
    """``(wells, dropped)``: the light wells and front courts the site's flat platforms leave (pure; 24 Oct 2026,
    real04: a 1 m concrete well stood 0.75 m above the pool terrace beside the basement window, made against the
    sloped ground the terrace replaces). An assumed or inferred well whose middle lies on a flat platform is dropped
    when the platform's level is at least ``LIGHT_WELL_CLEARANCE`` under the window sill (the terrace lights the
    window), else it opens at the platform's level (``top_z``); a drawn well stays as drawn."""
    flat = [pf for pf in pfs if not pf.get("sloped") and isinstance(pf.get("z"), (int, float))
            and len(pf.get("polygon") or []) >= 3]
    kept, dropped = [], []
    for w in wells:
        poly = w.get("polygon") or []
        if w.get("source") == "drawn" or not poly or w.get("sill_z") is None:
            kept.append(w)
            continue
        c = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
        pf = next((pf for pf in flat if G.point_in_polygon(c, pf["polygon"])
                   and not any(G.point_in_polygon(c, h) for h in pf.get("holes") or [])), None)
        if pf is None:
            kept.append(w)
        elif float(w["sill_z"]) >= float(pf["z"]) + LIGHT_WELL_CLEARANCE:
            dropped.append(dict(w, dropped_reason=f"the {pf.get('kind') or 'platform'} {pf['id']} at "
                                                  f"{float(pf['z']):.2f} m lies under the sill {float(w['sill_z']):.2f} m: "
                                                  f"no light well"))
        else:
            kept.append(dict(w, top_z=float(pf["z"]), platform_id=pf["id"]))
    return kept, dropped


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


def tree_parts(item: dict, terrain: dict, climate: str = "temperate") -> dict:
    """The low-poly proxy of a tree (site decor ``tree``) or bush (``plant``) on the ground (pure): trunk and crown
    meshes (the exterior camera model's obstacle; the scene's real tree comes from ``wenart.blender.vegetation``),
    the sizes and the species. Crown diameter = the drawn size; the height and the class by ``tree_height`` (a
    crown under 1.5 m radius is a shrub without a trunk); the species the item names (``species``), else the
    climate's inferred one (``species_for``). ``plant``: a bush of the drawn size, ``plant_height`` tall."""
    cx, cy = float(item["center"][0]), float(item["center"][1])
    size = [float(v) for v in (item.get("size") or [1.0, 1.0])[:2]]
    dia = max(0.3, max(size))
    gz = ground_z(terrain, cx, cy)
    if item.get("kind") == "plant":
        h = DEFAULTS["plant_height"]
        crown = _sphere((cx, cy, gz + h / 2.0), size[0] / 2.0, size[1] / 2.0, h / 2.0)
        return {"trunk": None, "crown": crown, "height": h, "diameter": dia, "ground_z": gz, "size_class": "shrub",
                "species": item.get("species") or species_for("shrub", climate), "species_inferred": not item.get("species"),
                "crown_z": [round(gz, 3), round(gz + h, 3)],
                "reason": f"bush of the drawn size, {h} m tall (height assumed)"}
    h, cls = tree_height(dia / 2.0)
    species = item.get("species") or species_for(cls, climate)
    if cls == "shrub":
        crown = _sphere((cx, cy, gz + h / 2.0), size[0] / 2.0, size[1] / 2.0, h / 2.0)
        return {"trunk": None, "crown": crown, "height": round(h, 3), "diameter": dia, "ground_z": gz,
                "size_class": cls, "species": species, "species_inferred": not item.get("species"),
                "crown_z": [round(gz, 3), round(gz + h, 3)],
                "reason": f"shrub: crown {dia:.2f} m as drawn (under a 1.5 m crown radius), {h:.2f} m tall "
                          f"(height by the crown class, assumed); species {species} (inferred)"}
    crown_h = DEFAULTS["crown_share"] * h
    trunk = _cylinder((cx, cy), DEFAULTS["trunk_radius"], gz - 0.05, gz + h - crown_h * 0.6)
    crown = _sphere((cx, cy, gz + h - crown_h / 2.0), size[0] / 2.0, size[1] / 2.0, crown_h / 2.0)
    return {"trunk": trunk, "crown": crown, "height": round(h, 3), "diameter": dia, "ground_z": gz,
            "size_class": cls, "species": species, "species_inferred": not item.get("species"),
            "crown_z": [round(gz + h - crown_h, 3), round(gz + h, 3)],
            "reason": f"{cls} tree: crown {dia:.1f} m as drawn, {h:.1f} m tall (height by the crown class, assumed); "
                      f"species {species} ({'drawn' if item.get('species') else 'inferred'})"}


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
    "tree_sightline": 1.0, "sightline_m": 40.0, "sightline_deg": 30.0,
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


def facade_openings(building: dict, levels: Sequence[dict], outline: Sequence[Sequence[float]],
                    outlines: Optional[dict] = None) -> dict:
    """The outside doors and windows of the building and of every copy on the plot in site metres (pure; 25 Oct
    2026, real04: the east pool deck took the mean ground under it, -1.40 m, half way between the basement and the
    ground floor; it buried the basement window and a front court was cut into the deck). ``{"openings": [{"id",
    "building", "type", "level_id", "bottom", "top", "probe": (x, y)}], "floors": {building: [(z, level ids)]}}``:
    ``probe`` lies 0.3 m out of the wall face, a copy's openings are the building's moved by its transform and
    raised by its ``dz`` (``copies``)."""
    from wenart.blender import copies as CP

    recs = outer_openings(building, levels, outline, outlines)
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    ref = next((c for c in site.get("buildings") or [] if isinstance(c, dict) and c.get("reference")), {})
    floors_ref: dict[float, list[str]] = {}
    for lv in levels:
        floors_ref.setdefault(round(float(lv["elevation"]), 3), []).append(str(lv["id"]))
    out: dict = {"openings": [], "floors": {}}
    for c in [None] + CP.copies_of(building):
        bid = str((c or ref).get("id") or "building")
        dz = float((c or {}).get("dz") or 0.0)
        out["floors"][bid] = [(round(z + dz, 3), ids) for z, ids in sorted(floors_ref.items())]
        for r in recs:
            (cx, cy), (ox, oy), reach = r["centre"], r["outward"], r["half_t"] + 0.3
            p = (cx + ox * reach, cy + oy * reach)
            out["openings"].append({"id": str(r["opening"]["id"]), "building": bid, "type": r["opening"]["type"],
                                    "level_id": r["level"]["id"], "bottom": round(r["bottom"] + dz, 3),
                                    "top": round(r["top"] + dz, 3),
                                    "probe": CP.move_point(c, p) if c is not None else p})
    return out


def building_facades(building: dict) -> dict:
    """``facade_openings`` of a building JSON on its own (pure): each level's wall outline as the outward test, the
    largest one as the fallback (``building_keep_out``'s outlines)."""
    outlines = {}
    for lv in building.get("levels") or []:
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lv.get("id")]
        if walls:
            outlines[lv["id"]] = geom2d.wall_outline(walls)[0]
    levels = [lv for lv in building.get("levels") or [] if lv.get("elevation") is not None
              and lv.get("ceiling_height") is not None]
    if not outlines or not levels:
        return {"openings": [], "floors": {}}
    largest = max(outlines.values(), key=lambda p: G.polygon_area(p) if len(p) >= 3 else 0.0)
    return facade_openings(building, levels, largest, outlines)


def entrances(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
              outlines: Optional[dict] = None) -> list[dict]:
    """The entrance doors (pure): outside doors whose bottom lies from ``LIGHT_WELL_CLEARANCE`` under to
    ``entrance_max_rise`` over the ground outside (a door higher up opens onto a balcony or a terrace). Each:
    ``{"opening_id", "level_id", "centre", "outward", "axis", "width", "bottom", "ground_z", "rise", "half_t"}``;
    ``rise`` > ``LIGHT_WELL_CLEARANCE`` needs steps.

    Milestone 12: when the pipeline wrote ``site.entrances`` (``wenart.levels.model``), those are the entrances (every
    rise; a door into the air or below the ground is left out, the level checks L2 / L3 report it), each with its
    ``record``."""
    records = record_entrances(building, levels)
    if records is not None:
        return records
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


def record_entrances(building: dict, levels: Sequence[dict]) -> Optional[list[dict]]:
    """The entrances of ``site.entrances`` (Milestone 12) in the format of ``entrances``, or None when the building
    has none written (the M10/M11 rule applies then). Doors into the air and below the ground are left out."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    recs = site.get("entrances")
    if not isinstance(recs, list):
        return None
    ids = {lv["id"] for lv in levels}
    out = []
    for r in recs:
        if not isinstance(r, dict) or r.get("level_id") not in ids or r.get("into_air") or r.get("below_ground"):
            continue
        if not r.get("centre") or not r.get("outward"):
            continue
        outward = (float(r["outward"][0]), float(r["outward"][1]))
        out.append({"opening_id": r["door_id"], "level_id": r["level_id"],
                    "centre": (float(r["centre"][0]), float(r["centre"][1])), "outward": outward,
                    "axis": nearest_axis(outward), "width": float(r.get("width") or 0.9),
                    "bottom": float(r["threshold_z"]), "ground_z": float(r["ground_z"]),
                    "rise": max(0.0, float(r.get("rise") or 0.0)), "half_t": float(r.get("half_t") or 0.1),
                    "record": r})
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
    if e.get("record") is not None:
        return record_steps(e, face)
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


HANDRAIL = {"height": 0.90, "inset": 0.05, "rail": 0.05, "post": 0.05}      # our assumption (flagged in the report)
CHEEK = {"thickness": 0.15, "above": 0.10}


def record_steps(e: dict, face) -> dict:
    """The landing, flights, intermediate landings, ramp, handrails and cheek walls of a ``site.entrances`` record
    (Milestone 12, pure): ``{"opening_id", "blocks": [{"polygon", "z_top"}], "end", "count", "rise", "face",
    "risers", "intermediate_landings", "ramp": {"polygon", "z_start", "z_end", "s"} | None, "rails": [(p0, p1)],
    "posts": [(p0, p1)], "cheeks": [{"polygon", "z_top"}], "solution"}``. The flight runs straight out from the
    landing (riser and tread of the record, an intermediate landing between flights); a ramp runs along the facade
    from the landing's side, down to the ground; handrails 0.90 m above the walking line on both sides."""
    rec = e["record"]
    o = e["outward"]
    u = (-o[1], o[0])
    st = rec.get("steps") or None
    landing = rec.get("landing") or None
    ramp = rec.get("ramp") or None
    out = {"opening_id": e["opening_id"], "blocks": [], "end": 0.0, "count": 0, "rise": 0.0, "face": face,
           "risers": 0, "intermediate_landings": 0, "ramp": None, "rails": [], "posts": [], "cheeks": [],
           "solution": rec.get("solution") or "none"}
    if rec.get("solution") in (None, "none") or (st is None and ramp is None):
        return out
    top = float((landing or {}).get("z", e["bottom"]))
    ground = float(e["ground_z"])
    depth = float((landing or {}).get("depth", INFERRED["landing"]))
    width = float((landing or {}).get("width", e["width"] + 2 * INFERRED["landing_side"]))
    half_w = width / 2.0

    def at(s: float, d: float, z: float) -> tuple[float, float, float]:
        return (face[0] + u[0] * s + o[0] * d, face[1] + u[1] * s + o[1] * d, z)

    def side_cheeks(d0: float, d1: float, z_top: float) -> None:
        if st and st.get("cheek_walls"):
            for s0, s1 in ((half_w, half_w + CHEEK["thickness"]), (-half_w - CHEEK["thickness"], -half_w)):
                poly = geom2d.ccw([at(s, d, 0.0)[:2] for s, d in ((s0, d0), (s1, d0), (s1, d1), (s0, d1))])
                out["cheeks"].append({"polygon": poly, "z_top": z_top + CHEEK["above"]})

    out["blocks"].append({"polygon": _rect_along(face, o, 0.0, depth, half_w), "z_top": top})
    side_cheeks(0.0, depth, top)
    d, z = depth, top
    if st:
        n = int(st["count"])
        r = (top - ground) / n if n > 0 and top > ground else float(st["riser"])   # exact (the record rounds it)
        t = float(st["tread"])
        flights = [int(k) for k in st.get("flights") or [n]]
        done = 0
        for fi, k in enumerate(flights):
            for j in range(k):
                z -= r
                done += 1
                if done >= n:
                    break
                run = depth if j == k - 1 else t       # the last riser of a flight (not the last one): a landing
                out["blocks"].append({"polygon": _rect_along(face, o, d, d + run, half_w), "z_top": z})
                side_cheeks(d, d + run, z)
                d += run
        out.update(end=d, count=n - 1, rise=round(r, 4), risers=n, intermediate_landings=len(flights) - 1)
        if st.get("handrails"):
            for s in (half_w - HANDRAIL["inset"], -half_w + HANDRAIL["inset"]):
                h = HANDRAIL["height"]
                a, b, c = at(s, 0.0, top + h), at(s, depth, top + h), at(s, d, ground + r + h)
                out["rails"] += [(a, b), (b, c)]
                out["posts"] += [((p[0], p[1], p[2] - h), p) for p in (a, b, c)]
    if ramp:
        length, rw = float(ramp["length"]), float(ramp["width"])
        s0, s1 = half_w, half_w + length
        d0, d1 = max(0.0, depth - rw), depth
        poly = [at(s, dd, 0.0)[:2] for s, dd in ((s0, d0), (s1, d0), (s1, d1), (s0, d1))]
        out["ramp"] = {"polygon": poly, "z_start": top, "z_end": ground, "s": [s0, s1], "d": [d0, d1],
                       "length": length, "slope": ramp.get("slope")}
        if ramp.get("handrails"):
            h = HANDRAIL["height"]
            for dd in (d1 - HANDRAIL["inset"], d0 + HANDRAIL["inset"]):
                a, b = at(s0, dd, top + h), at(s1, dd, ground + h)
                out["rails"].append((a, b))
                out["posts"] += [((p[0], p[1], p[2] - h), p) for p in (a, b)]
    return out


def bar(p0: Sequence[float], p1: Sequence[float], w: float, h: float) -> tuple[list, list]:
    """A square bar ``w`` wide and ``h`` high from ``p0`` to ``p1`` (3D, may slope): 8 vertices, 6 faces."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    hl = math.hypot(dx, dy)
    if hl <= 1e-9:                                    # a vertical post: a box w x w
        return geom2d.box(((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, (p0[2] + p1[2]) / 2.0),
                          (w, w, abs(dz) + h), 0.0)
    nx, ny = -dy / hl, dx / hl
    verts = []
    for p in (p0, p1):
        for sw, sh in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append((p[0] + nx * sw * w / 2.0, p[1] + ny * sw * w / 2.0, p[2] + sh * h / 2.0))
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return verts, faces


def ramp_solid(ramp: dict, z_bottom: float) -> tuple[list, list]:
    """The ramp's solid: its polygon from ``z_bottom`` up to a top sloping from ``z_start`` (at the landing) to
    ``z_end`` (at the far end)."""
    poly = ramp["polygon"]                            # (s0, d0), (s1, d0), (s1, d1), (s0, d1)
    zt = [ramp["z_start"], ramp["z_end"], ramp["z_end"], ramp["z_start"]]
    verts = [(p[0], p[1], z_bottom) for p in poly] + [(p[0], p[1], z) for p, z in zip(poly, zt)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    if G.polygon_signed_area(poly) < 0:
        faces = [list(reversed(f)) for f in faces]
    return verts, faces


def entrance_meshes(st: dict, terrain: dict) -> list[dict]:
    """The Blender meshes of one entrance (pure): ``[{"name", "kind", "verts", "faces"}]``: ``steps_<door>``
    (kind ``site_steps``: landing, flights and cheek walls, each block from 0.1 m under the ground), ``ramp_<door>``
    (``site_ramp``) and ``handrail_<door>`` (``site_handrail``: rails and posts)."""
    out = []
    parts = []
    for blk in list(st["blocks"]) + list(st.get("cheeks") or []):
        z0 = min(ground_z(terrain, *p) for p in blk["polygon"]) - 0.1
        parts.append(geom2d.prism(blk["polygon"], z0, blk["z_top"]))
    if parts:
        v, f = geom2d.merge(parts)
        out.append({"name": f"steps_{st['opening_id']}", "kind": "site_steps", "verts": v, "faces": f})
    if st.get("ramp"):
        z0 = min(ground_z(terrain, *p) for p in st["ramp"]["polygon"]) - 0.1
        v, f = ramp_solid(st["ramp"], z0)
        out.append({"name": f"ramp_{st['opening_id']}", "kind": "site_ramp", "verts": v, "faces": f})
    rails = [bar(a, b, HANDRAIL["rail"], HANDRAIL["rail"]) for a, b in st.get("rails") or []]
    rails += [bar(a, b, HANDRAIL["post"], HANDRAIL["post"]) for a, b in st.get("posts") or []]
    if rails:
        v, f = geom2d.merge(rails)
        out.append({"name": f"handrail_{st['opening_id']}", "kind": "site_handrail", "verts": v, "faces": f})
    return out


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


# Fix round after P4b (17 Oct 2026; pod P4b, real03: a 33 x 15 m bungalow with 22 outside windows on a 6 m plot
# margin). The first pass kept none of its 122 candidates (window band 108, front zone 51, corner sightlines 36, path
# 6; a candidate counts for every filter that removes it), so the exterior showed a bare lawn and nothing said so.
# When the first pass places fewer than ``tree_min`` trees (and fewer than asked), a second pass over the same
# candidates narrows the window band to ``tree_window_reach_relaxed`` out and ``tree_window_side_relaxed`` on each
# side; the building, path, corner-sightline and front-garden rules stay (the corner and entrance views stay open,
# no tree at the plot corners). real02 (2 trees in the first pass) is unchanged.
TREE_RELAXED = {"tree_min": 2, "tree_window_reach_relaxed": 4.0, "tree_window_side_relaxed": 1.0}
TREE_FILTERS = ("building", "path", "sightline", "window", "front")


def place_trees(plot: Sequence, outline: Sequence, paths: Sequence[dict], windows: Sequence[dict], main: dict,
                count: int, stats: Optional[dict] = None) -> list[dict]:
    """Up to ``count`` inferred trees inside the plot (pure; docs/milestone11.md §1.1 E11): candidates every
    ``tree_step`` along the plot edges ``tree_inset`` inside; a candidate is kept ``tree_from_building`` clear
    of the building, ``tree_from_path`` of every path, out of the band in front of every outside window
    (``tree_window_reach`` out, its width + ``tree_window_side`` on each side) and out of the front garden
    (nothing nearer the main facade's side than ``front_zone_extra`` behind its face, so the frontal and corner
    views of the entrance stay open); picked greedily, beside the side facades first (nearest their middle), then
    behind the building, at least ``tree_spacing`` apart. Each tree is site decor ``{"id",
    "kind": "tree", "center", "size", "inferred": true, "reason"}``.

    Fix round after P4b (17 Oct 2026, ``TREE_RELAXED``): when the first pass places fewer than ``min(count,
    tree_min)`` trees, a second pass with the narrower window band (``tree_window_reach_relaxed`` /
    ``tree_window_side_relaxed``) adds trees up to ``count``; those carry ``relaxed: true`` and say so in their
    reason. ``stats`` (a dict, filled when given): ``candidates``, ``removed`` (per filter of ``TREE_FILTERS``, the
    candidates it removes in the first pass; one candidate can count for several), ``spacing`` (kept candidates
    left out for ``tree_spacing``), ``placed_first``, ``relaxed`` (the second pass ran), ``placed_relaxed``,
    ``placed``, ``count`` and ``top_filter`` (the filter that removed the most candidates, None when none)."""
    st = stats if stats is not None else {}
    st.update(candidates=0, removed={k: 0 for k in TREE_FILTERS}, spacing=0, placed_first=0, relaxed=False,
              placed_relaxed=0, placed=0, count=max(0, int(count)), top_filter=None)
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
    r = INFERRED["tree_crown"] / 2.0
    # the lines of sight of the corner views (exterior.plan_exterior, E14): from every corner of the outline's
    # rectangle, sightline_deg off each of its two facades
    rect = geom2d.oriented_rectangle(outline)
    sightlines = []
    for c in geom2d.rectangle_corners(rect):
        su = 1.0 if (c[0] - rect["center"][0]) * rect["u"][0] + (c[1] - rect["center"][1]) * rect["u"][1] > 0 else -1.0
        sv = 1.0 if (c[0] - rect["center"][0]) * rect["v"][0] + (c[1] - rect["center"][1]) * rect["v"][1] > 0 else -1.0
        n1 = (rect["u"][0] * su, rect["u"][1] * su)
        n2 = (rect["v"][0] * sv, rect["v"][1] * sv)
        ang = math.radians(INFERRED["sightline_deg"])
        for a, b in ((n1, n2), (n2, n1)):
            d = (math.cos(ang) * a[0] + math.sin(ang) * b[0], math.cos(ang) * a[1] + math.sin(ang) * b[1])
            sightlines.append((tuple(c), (c[0] + d[0] * INFERRED["sightline_m"], c[1] + d[1] * INFERRED["sightline_m"])))

    def failed(p, reach: float, side_m: float) -> list[str]:
        """The filters of ``TREE_FILTERS`` that remove the candidate ``p`` with this window band."""
        out = []
        if G.point_in_polygon(p, outline) or geom2d.distance_to_polygon_edges(p, outline) < INFERRED["tree_from_building"]:
            out.append("building")
        if any(G.point_in_polygon(p, q["polygon"]) or geom2d.distance_to_polygon_edges(p, q["polygon"])
               < INFERRED["tree_from_path"] for q in paths):
            out.append("path")
        if any(G.point_segment_distance(p, a, b) < r + INFERRED["tree_sightline"] for a, b in sightlines):
            out.append("sightline")                   # the corner views stay open (E14)
        for w in windows:
            (cx, cy), (ox, oy) = w["centre"], w["outward"]
            dx, dy = p[0] - cx, p[1] - cy
            along, side = dx * ox + dy * oy, abs(dx * -oy + dy * ox)
            if 0.0 < along < reach + r and side < float(w["opening"]["width"]) / 2.0 + side_m + r:
                out.append("window")
                break
        if p[0] * md[0] + p[1] * md[1] > front_edge - INFERRED["front_zone_extra"]:
            out.append("front")                       # the front garden and the entrance views stay open
        return out

    def ranked(reach: float, side_m: float, counting: bool) -> list:
        keep = []
        for p in sorted(set(cands)):
            why = failed(p, reach, side_m)
            if counting:
                for k in why:
                    st["removed"][k] += 1
            if why:
                continue
            pm = p[0] * md[0] + p[1] * md[1]
            pa = p[0] * -md[1] + p[1] * md[0]
            # beside the side facades first (nearest their middle), then behind the building
            rank = 0 if (pa < min(across) or pa > max(across)) else 1
            keep.append((rank, round(abs(pm - (min(proj) + max(proj)) / 2.0), 6) if rank == 0 else round(pm, 6), p))
        keep.sort()
        return keep

    def pick(keep: list, out: list, reason: str, relaxed: bool, counting: bool) -> None:
        for _rank, _key, p in keep:
            if len(out) >= count:
                break
            if all(G.distance(p, t["center"]) >= INFERRED["tree_spacing"] for t in out):
                tree = {"id": f"tree_inferred_{len(out) + 1}", "kind": "tree", "center": [p[0], p[1]],
                        "size": [INFERRED["tree_crown"], INFERRED["tree_crown"]], "inferred": True, "reason": reason}
                if relaxed:
                    tree["relaxed"] = True
                out.append(tree)
            elif counting:
                st["spacing"] += 1

    st["candidates"] = len(set(cands))
    out: list[dict] = []
    pick(ranked(INFERRED["tree_window_reach"], INFERRED["tree_window_side"], True), out,
         "no site plan: a tree clear of the windows, the paths and the front garden "
         "(inferred, docs/milestone11.md §1.1 E11)", False, True)
    st["placed_first"] = len(out)
    if len(out) < min(int(count), TREE_RELAXED["tree_min"]):
        st["relaxed"] = True
        reach, side_m = TREE_RELAXED["tree_window_reach_relaxed"], TREE_RELAXED["tree_window_side_relaxed"]
        pick(ranked(reach, side_m, False), out,
             f"no site plan: a tree clear of the paths and the front garden; the window band narrowed to {reach:g} m "
             f"out and {side_m:g} m on each side because the first pass placed {st['placed_first']} of {int(count)} "
             f"(inferred, docs/milestone11.md §1.1 E11; fix round after P4b)", True, False)
        st["placed_relaxed"] = len(out) - st["placed_first"]
    st["placed"] = len(out)
    top = max(TREE_FILTERS, key=lambda k: st["removed"][k])
    st["top_filter"] = top if st["removed"][top] > 0 else None
    return out


def trees_record(stats: dict) -> tuple[dict, Optional[str]]:
    """``(assumed entry, warning or None)`` of ``place_trees``' ``stats`` (pure; fix round after P4b, 17 Oct 2026):
    every build that infers trees lists ``inferred trees: placed k of n`` with the first and the relaxed pass and
    the filter that removed the most candidates (CLAUDE.md: everything inferred is listed; P4b's real03 got 0 of 3
    in silence); a warning when fewer than asked are placed."""
    removed = ", ".join(f"{k} {v}" for k, v in stats["removed"].items() if v) or "none"
    text = (f"inferred trees: placed {stats['placed']} of {stats['count']} ({stats['candidates']} candidates; "
            f"removed by {removed}; most by {stats['top_filter'] or 'none'}")
    if stats["relaxed"]:
        text += (f"; the first pass placed {stats['placed_first']}, the second pass with the window band narrowed to "
                 f"{TREE_RELAXED['tree_window_reach_relaxed']:g} m added {stats['placed_relaxed']}")
    text += ")"
    entry = {"field": "trees", "value": stats["placed"], "reason": text}
    return entry, (text if stats["placed"] < stats["count"] else None)


def inferred_site(building: dict, levels: Sequence[dict], terrain: dict, outline: Sequence[Sequence[float]],
                  outlines: Optional[dict], plot: Sequence, plot_source: str, options: dict,
                  drawn_trees: bool) -> dict:
    """What the build adds where the documents are silent (pure; docs/milestone11.md §1.1 E11, §7, CLAUDE.md
    evidence rules: every item ``inferred`` and listed): the plot (``inferred_plot`` when none is drawn), the
    entrances with their steps, the paths, the boundary (hedge or fence on an inferred plot), the trees (when
    none is drawn). ``options``: ``overrides.site_options``. Returns ``{"plot", "plot_inferred", "main",
    "entrances", "steps", "paths", "boundary", "trees", "assumed", "warnings", "tree_stats"}``. Fix round after P4b
    (17 Oct 2026): when it infers trees, ``assumed`` gets ``trees_record``'s entry (placed k of n, the filters) and
    ``warnings`` its warning when fewer than asked are placed; ``tree_stats`` keeps ``place_trees``' stats."""
    out = {"plot": list(plot), "plot_inferred": False, "main": None, "entrances": [], "steps": [], "paths": [],
           "boundary": [], "trees": [], "assumed": [], "warnings": [], "tree_stats": None}
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
        stats: dict = {}
        out["trees"] = place_trees(out["plot"], outline, out["paths"], windows, out["main"],
                                   int(options.get("trees", 3)), stats=stats)
        if stats.get("count"):                    # fix round after P4b: never a silent 0 (trees_record)
            entry, warning = trees_record(stats)
            out["assumed"].append(entry)
            if warning:
                out["warnings"].append(warning)
            out["tree_stats"] = stats
    return out


# --------------------------------------------------------------------------
# Milestone 13 (T6): hedges, platforms, pools v2, the backdrop and the haze (pure)
# --------------------------------------------------------------------------

# The A/B switches of scripts/jobs/site_ab.sh (docs/milestone13.md §13.3): WENART_SITE_VARIANT = all (the default
# build: everything on) | base (every lever off: the Milestone 12 site layout, but the trees keep the Milestone 13
# crown-class heights and are leaf-card trees, never the Milestone 12 ellipsoid: CLAUDE.md "never a primitive") |
# one lever on.
SITE_LEVERS = ("hedge", "instances", "sapling", "platforms", "pools", "sky")
SITE_VARIANT_ENV = "WENART_SITE_VARIANT"


def site_levers(variant: Optional[str] = None) -> dict:
    """``{lever: bool}`` of a site variant (pure): ``None`` reads ``WENART_SITE_VARIANT``; unset, ``all`` or ``""``
    turn every lever on; ``base`` / ``none`` turn every lever off; a lever name turns that one on; several names
    joined by ``+`` turn those on. An unknown name raises ValueError."""
    import os

    v = (os.environ.get(SITE_VARIANT_ENV, "") if variant is None else str(variant or "")).strip().lower()
    if v in ("", "all"):
        return {k: True for k in SITE_LEVERS}
    if v in ("base", "none"):
        return {k: False for k in SITE_LEVERS}
    names = [x for x in v.split("+") if x]
    unknown = [x for x in names if x not in SITE_LEVERS]
    if unknown:
        raise ValueError(f"{SITE_VARIANT_ENV} {v!r}: unknown lever {unknown}; one of {SITE_LEVERS}, all, base")
    return {k: k in names for k in SITE_LEVERS}


HEDGE_DEFAULT_HEIGHT_M = 1.2


def hedges_of(building: dict, climate: str = "temperate", detect: bool = True) -> tuple[list[dict], set]:
    """``(hedges, symbol_ids)`` of the building (pure; Milestone 13 T6): the ``site.hedges`` the sheets stage wrote
    (``wenart.sheets.exterior.hedge_rows``, ``build`` not false), else, with ``detect``, the same detector over the
    site decor's tree symbols (the committed real04 building carries 100 single trees in four rows). Every hedge:
    ``id``, ``polyline``, ``width_m``, ``height_m``, ``height_class``, ``species`` (named, else inferred by the
    climate: ``species_inferred``), ``inferred``, ``evidence``, ``source`` (``site.hedges`` | ``decor_rows``);
    ``symbol_ids`` are the decor ids of the symbols a hedge took (no longer single trees)."""
    from wenart.blender.vegetation import hedge_height_class, hedge_rows, HEDGE_HEIGHT_M

    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    out, taken = [], set()
    drawn = [h for h in site.get("hedges") or [] if isinstance(h, dict) and h.get("build", True) is not False
             and len(h.get("polyline") or []) >= 2]
    if drawn:
        for k, h in enumerate(drawn):
            width = float(h.get("width_m") or 0.7)
            cls = h.get("height_class") or hedge_height_class(width / 2.0)
            height = float(h.get("height_m") or HEDGE_HEIGHT_M.get(cls, HEDGE_DEFAULT_HEIGHT_M))
            rec = {"id": str(h.get("id") or f"hedge_{k + 1:03d}"), "polyline": [[float(x), float(y)] for x, y in h["polyline"]],
                   "width_m": width, "height_m": height, "height_class": cls,
                   "species": h.get("species") or species_for(cls, climate, kind="hedge"),
                   "species_inferred": not h.get("species"), "inferred": bool(h.get("inferred", True)),
                   "evidence": list(h.get("evidence") or []), "source": "site.hedges",
                   "symbol_ids": list(h.get("symbol_ids") or []), "reason": h.get("reason") or "site.hedges"}
            out.append(rec)
            taken |= set(rec["symbol_ids"])
        return out, taken
    if not detect:
        return [], set()
    trees = [d for d in site.get("decor") or [] if isinstance(d, dict) and d.get("kind") == "tree"
             and d.get("build", True) is not False]
    for k, row in enumerate(hedge_rows(trees)):
        ids = row["symbol_ids"]
        taken |= set(ids)
        ev = []
        for i in row["symbol_indices"][:3]:
            ev += [dict(e, rule="site_hedge_symbol") for e in (trees[i].get("evidence") or [])[:1]]
        out.append({"id": f"hedge_{k + 1:03d}", "polyline": row["polyline"], "width_m": row["width_m"],
                    "height_m": row["height_m"], "height_class": row["height_class"],
                    "species": species_for(row["height_class"], climate, kind="hedge"), "species_inferred": True,
                    "inferred": True, "evidence": ev, "source": "decor_rows", "symbol_ids": ids,
                    "reason": f"{row['count']} drawn tree symbols of radius {row['radius_m']:.2f} m at a pitch of "
                              f"{row['pitch_m']:.2f} m in one row ({row['length_m']:.1f} m): a {row['height_class']} "
                              f"hedge {row['height_m']:.1f} m high (inferred; the symbols are not single trees)"})
    return out, taken


HEDGE_TOP_ROUND_M = 0.2          # the clipped hedge's rounded shoulders (round 3; P1 'hedge' row: the core read as a box)
HEDGE_HULL_STEPS = 3             # segments per shoulder arc


def hedge_hull_profile(width_m: float, height_m: float, round_m: float = HEDGE_TOP_ROUND_M,
                       steps: int = HEDGE_HULL_STEPS) -> list[tuple[float, float]]:
    """The cross-section of a hedge hull (pure; round 3): ``[(across, z), ...]`` from z 0 (the bottom) to
    ``height_m``, ``width_m`` wide with its two top shoulders rounded by ``round_m`` (capped at half the width and
    half the height; a flat top between them). Convex, no repeated point; a box when ``round_m`` is 0."""
    w, h = float(width_m), float(height_m)
    r = max(0.0, min(float(round_m), w / 2.0, h / 2.0))
    pts = [(-w / 2.0, 0.0), (w / 2.0, 0.0)]
    if r <= 1e-6:
        return pts + [(w / 2.0, h), (-w / 2.0, h)]
    cx, cz = w / 2.0 - r, h - r
    n = max(1, int(steps))
    for k in range(n + 1):                                 # the right shoulder, 0..90°
        th = (math.pi / 2.0) * k / n
        pts.append((cx + r * math.cos(th), cz + r * math.sin(th)))
    for k in range(n + 1):                                 # the left shoulder, 90..180°
        th = math.pi / 2.0 + (math.pi / 2.0) * k / n
        pts.append((-cx + r * math.cos(th), cz + r * math.sin(th)))
    out: list[tuple[float, float]] = []
    for q in pts:
        if not out or abs(out[-1][0] - q[0]) > 1e-9 or abs(out[-1][1] - q[1]) > 1e-9:
            out.append((round(q[0], 6), round(q[1], 6)))
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out


def hedge_parts(hedge: dict, terrain: dict) -> tuple[list, list, dict]:
    """``(verts, faces, info)`` of a hedge's solid hull following the ground (pure): one closed prism per
    polyline segment and ground step (``PLOT_WALL_STEP_M``, as ``plot_wall_parts``), ``width_m`` thick, from 0.1 m
    under the ground to ``height_m`` over it, its cross-section ``hedge_hull_profile`` (rounded shoulders since
    round 3; the Milestone 13 round-1 core was a box); the exterior camera model's low obstacle and the leaf-card
    hedge's opaque core. ``info``: ``z_range``, ``segments``, ``length_m``, ``top_z``, ``core`` (``hull``),
    ``top_round_m``."""
    pts = [(float(x), float(y)) for x, y in hedge["polyline"]]
    w, h = float(hedge["width_m"]), float(hedge["height_m"])
    r = max(0.0, min(HEDGE_TOP_ROUND_M, w / 2.0, h / 2.0))
    parts, zs = [], []
    segments = 0
    for a, b in zip(pts, pts[1:]):
        length = G.distance(a, b)
        if length < 0.05:
            continue
        segments += 1
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        across = (uy, -ux)                                   # the profile's s axis: across the hedge
        k = max(1, int(math.ceil(length / PLOT_WALL_STEP_M)))
        steps = []                                           # [t0, t1, z0, z1]; equal neighbours are joined
        for i in range(k):
            p0 = G.point_along_segment(a, b, i / k)
            p1 = G.point_along_segment(a, b, (i + 1) / k)
            g = [ground_z(terrain, *p0), ground_z(terrain, *p1), ground_z(terrain, *G.segment_midpoint(p0, p1))]
            z0, z1 = round(min(g) - 0.1, 6), round(max(g) + h, 6)
            if steps and steps[-1][2:] == [z0, z1]:
                steps[-1][1] = (i + 1) / k
            else:
                steps.append([i / k, (i + 1) / k, z0, z1])
        for j, (t0, t1, z0, z1) in enumerate(steps):
            mid = G.point_along_segment(a, b, (t0 + t1) / 2.0)
            # steps overlap by the hedge width (no slit), every second one 2 mm wider (no coplanar faces)
            reach = length * (t1 - t0) + (w if len(steps) > 1 else 0.0)
            prof = [(sx + 0.001 * (j % 2) * (1 if sx > 0 else -1), z0 + z)
                    for sx, z in hedge_hull_profile(w, z1 - z0, r)]
            parts.append(geom2d.extrude_profile(prof, mid, across, reach))
            zs += [z0, z1]
    if not parts:
        return [], [], {"z_range": [0.0, 0.0], "segments": 0, "length_m": 0.0, "core": "hull", "top_round_m": r}
    verts, faces = geom2d.merge(parts)
    length = sum(G.distance(a, b) for a, b in zip(pts, pts[1:]))
    return verts, faces, {"z_range": [round(min(zs), 4), round(max(zs), 4)], "segments": segments,
                          "length_m": round(length, 3), "top_z": round(max(zs), 4), "core": "hull",
                          "top_round_m": round(r, 3)}


# Fix round after P3 (16-17 Oct 2026): a hedge's hull stays on its planting side (``fit_hedges``). real04's hedge
# rows run 0.01-0.2 m from terrace edges with a 0.72 m wide hull: hedge_003 and hedge_004 overhung their terraces'
# retaining walls by 0.16-0.22 m, hedge_001 cut 0.35 m into a stepped band.
HEDGE_FIT = {"max_shift_m": 0.5, "min_width_m": 0.3, "sample_m": 0.25, "tol_m": 0.01, "rounds": 3,
             # how far a leaf card reaches out of the hull (vegetation: a 0.18 x 0.22 m cherry-laurel card at up to
             # 1.25 x its size, tilted up to 45 degrees off the hull's normal: about 0.13 m)
             "card_reach_m": 0.15}


def _boundary_nearest(p, poly) -> tuple[float, tuple[float, float], tuple[float, float]]:
    """``(distance, nearest point, outward normal of that edge)`` of ``p`` to the edges of the ccw ``poly`` (pure)."""
    best = (math.inf, (float(p[0]), float(p[1])), (0.0, 0.0))
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l2 = dx * dx + dy * dy
        if l2 <= 0.0:
            continue
        t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2))
        q = (a[0] + t * dx, a[1] + t * dy)
        d = math.hypot(p[0] - q[0], p[1] - q[1])
        if d < best[0]:
            length = math.sqrt(l2)
            best = (d, q, (dy / length, -dx / length))            # ccw: the right side of an edge is outside
    return best


def _hedge_samples(pts: list, hw: float, step: float) -> list[tuple[tuple[float, float], int, bool]]:
    """``[(point, vertex, core)]`` along a hedge polyline (pure): a point every ``step`` (``vertex``: the polyline
    vertex it moves with, the nearer end of its segment; ``core`` True) and the hull's two ends, ``hw`` beyond the end
    points (``core`` False: they do not decide on which side of a platform the hedge stands, and they are the hull's
    edge already, so they need ``hw`` less clearance)."""
    out = []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        length = G.distance(a, b)
        if length < 1e-9:
            continue
        n = max(1, int(math.ceil(length / step)))
        for k in range(n + 1):
            t = k / n
            out.append(((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), i if t < 0.5 else i + 1, True))
    if len(pts) >= 2:
        for p, q, idx in ((pts[0], pts[1], 0), (pts[-1], pts[-2], len(pts) - 1)):
            length = G.distance(p, q)
            if length > 1e-9:
                out.append(((p[0] + (p[0] - q[0]) / length * hw, p[1] + (p[1] - q[1]) / length * hw), idx, False))
    return out


def _hedge_keeps(samples: list, hw: float, platforms_: Sequence[dict], keep_out: Sequence) -> list[dict]:
    """The sides a hedge keeps (pure): ``[{"name", "poly", "inside", "margin"}]``. A flat platform with every core
    sample inside: the hull stays on its slab (margin ``hw``; its leaf cards may spill over the edge, over the
    retaining wall outside it); a flat platform with none inside but within reach: the hull stays ``hw`` +
    ``card_reach_m`` off its edge, so no leaf card reaches through its retaining wall onto the slab; the building
    and the copies (``keep_out``) the same way with margin ``hw`` (the cards end inside the outer wall). A hedge
    that crosses a polygon is left alone for it (drawn across on purpose); a sloped platform (draped on the terrain,
    no wall) and the stepped bands of the platform a hedge stands on (they share its edge) set nothing."""
    core = [p for p, _v, c in samples if c]
    flat = [pf for pf in platforms_ or () if not pf.get("sloped") and len(pf.get("polygon") or []) >= 3]
    polys = [(pf, geom2d.ccw(pf["polygon"])) for pf in flat]
    on = {str(pf.get("id")) for pf, poly in polys if core and all(G.point_in_polygon(p, poly) for p in core)}
    related = {str(pf.get("parent")) for pf, _poly in polys if str(pf.get("id")) in on and pf.get("parent")}
    related |= {str(pf.get("id")) for pf, _poly in polys if str(pf.get("parent")) in on}
    rows = [(str(pf.get("id")), poly, str(pf.get("id")) in on, hw + HEDGE_FIT["card_reach_m"]) for pf, poly in polys
            if str(pf.get("id")) not in related]
    rows += [(f"footprint_{k}", geom2d.ccw(poly), False, hw) for k, poly in enumerate(keep_out or ()) if len(poly) >= 3]
    keeps = []
    for name, poly, is_on, out_margin in rows:
        if is_on:
            keeps.append({"name": name, "poly": poly, "inside": True, "margin": hw})
        elif not any(G.point_in_polygon(p, poly) for p in core):
            near = min(_boundary_nearest(p, poly)[0] for p, _v, _c in samples)
            if near < out_margin + HEDGE_FIT["tol_m"]:
                keeps.append({"name": name, "poly": poly, "inside": False, "margin": out_margin})
    return keeps


def _violation(p, keep, end_off: float = 0.0) -> tuple[float, tuple[float, float]]:
    """``(metres the hull crosses the keep's line, the direction that fixes it)`` for one sample (pure); ``end_off``:
    the clearance a hull end sample already is (its half-width)."""
    d, q, normal = _boundary_nearest(p, keep["poly"])
    inside = G.point_in_polygon(p, keep["poly"])
    margin = max(0.0, keep["margin"] - end_off)
    if d < 1e-6:                                                # on the line: the edge's normal says the side
        return margin, (normal if not keep["inside"] else (-normal[0], -normal[1]))
    away = ((p[0] - q[0]) / d, (p[1] - q[1]) / d)              # from the boundary to the sample
    if inside == keep["inside"]:                                # on the right side: needs ``margin`` from the line
        return margin - d, away
    return margin + d, (-away[0], -away[1])                    # on the wrong side: back across the line


def fit_hedges(hedges: Sequence[dict], platforms_: Sequence[dict] = (), keep_out: Sequence = ()
               ) -> tuple[list[dict], list[dict]]:
    """``(hedges, assumed)``: every hedge with its hull kept on its planting side (pure; fix round after P3,
    16-17 Oct 2026). A hedge on a flat terrace (every point of its polyline inside the platform) keeps its hull on
    the slab, half its width inside the edges; a hedge beside a platform keeps its hull outside the retaining wall
    (``PLATFORM["wall_t"]``); no hedge reaches into the building or a copy (``keep_out``). The polyline vertices move
    (``HEDGE_FIT["rounds"]`` rounds, each vertex at most ``max_shift_m`` from where it was drawn); what still crosses
    makes the hedge narrower (down to ``min_width_m``). A changed hedge keeps ``fit``: ``polyline_drawn``,
    ``width_m_drawn``, ``shift_m`` per vertex, ``narrowed``, ``crossing_left_m``, ``keeps`` and the reason; the
    change is ``assumed`` (a hedge row drawn along a terrace edge is planted on the terrace). Why: P3's leaf cards and
    dark hull triangles on real04's retaining walls (ext_4)."""
    out, assumed = [], []
    cfg = HEDGE_FIT
    for h in hedges or ():
        pts = [(float(x), float(y)) for x, y in h.get("polyline") or []]
        w = float(h.get("width_m") or 0.0)
        if len(pts) < 2 or w <= 0.0:
            out.append(h)
            continue
        drawn = list(pts)
        keeps = _hedge_keeps(_hedge_samples(pts, w / 2.0, cfg["sample_m"]), w / 2.0, platforms_, keep_out)
        if not keeps:
            out.append(h)
            continue
        for _ in range(int(cfg["rounds"])):
            samples = _hedge_samples(pts, w / 2.0, cfg["sample_m"])
            push = [[0.0, 0.0] for _p in pts]
            moved = False
            for keep in keeps:
                worst: dict = {}
                for p, v, c in samples:
                    amount, direction = _violation(p, keep, 0.0 if c else w / 2.0)
                    if amount > cfg["tol_m"] and amount > worst.get(v, (0.0, None))[0]:
                        worst[v] = (amount, direction)
                for v, (amount, direction) in worst.items():
                    push[v][0] += amount * direction[0]
                    push[v][1] += amount * direction[1]
                    moved = True
            if not moved:
                break
            for i, (dx, dy) in enumerate(push):
                nx, ny = pts[i][0] + dx, pts[i][1] + dy
                off = math.hypot(nx - drawn[i][0], ny - drawn[i][1])
                if off > cfg["max_shift_m"]:                   # never further than max_shift_m from the drawing
                    k = cfg["max_shift_m"] / off
                    nx, ny = drawn[i][0] + (nx - drawn[i][0]) * k, drawn[i][1] + (ny - drawn[i][1]) * k
                pts[i] = (nx, ny)

        def crossing(width):
            samples_ = _hedge_samples(pts, width / 2.0, cfg["sample_m"])
            worst_ = 0.0
            for keep in keeps:
                margin = keep["margin"] - (w - width) / 2.0     # the margin shrinks with the half-width
                for p, _v, c in samples_:
                    amount, _d = _violation(p, dict(keep, margin=margin), 0.0 if c else width / 2.0)
                    worst_ = max(worst_, amount)
            return worst_

        left = crossing(w)
        width = w
        if left > cfg["tol_m"]:
            width = max(cfg["min_width_m"], round(w - 2.0 * left, 3))
            left = crossing(width)
        shift = [round(G.distance(a, b), 3) for a, b in zip(drawn, pts)]
        if max(shift) <= cfg["tol_m"] and width == w:
            out.append(h)
            continue
        names = sorted({k["name"] for k in keeps})
        reason = (f"hedge {h.get('id')}: its {w:.2f} m hull kept on its planting side of {', '.join(names)} "
                  f"(moved up to {max(shift):.2f} m" + (f", narrowed to {width:.2f} m" if width < w else "")
                  + "; a row drawn along a terrace edge or a wall is planted beside it, inferred)")
        new = dict(h, polyline=[[round(x, 4), round(y, 4)] for x, y in pts], width_m=width,
                   fit={"polyline_drawn": [list(p) for p in drawn], "width_m_drawn": w, "shift_m": shift,
                        "narrowed": width < w, "crossing_left_m": round(max(0.0, left), 3), "keeps": names,
                        "reason": reason})
        out.append(new)
        assumed.append({"field": f"hedge:{h.get('id')}:fit", "value": {"shift_m": max(shift), "width_m": width},
                        "reason": reason})
    return out, assumed


PLATFORM = {"mark_reach": 2.0, "level_tol": 0.15, "max_spread": 1.0, "step_max_drop": 1.2, "wall_t": 0.25,
            "kerb_h": 0.12, "kerb_w": 0.15, "step_rise": 0.16, "step_tread": 0.30, "step_width": 1.2, "lip": 0.04,
            "pool_join_m": 0.5, "pool_deck_m": 0.9, "railing_drop": 0.5, "below": 0.3, "round": 0.05,
            # round 3: a stepped terrace band is this wide; at most this many bands per edge; a platform edge longer
            # than edge_split_m is split into pieces (each steps in its own direction: real04 sp_001's 11.8 m west
            # edge has the ground 1.8 m over the level at one end and 1.9 m under it at the other)
            "band_w": 1.2, "band_max": 6, "edge_split_m": 3.0,
            # a retaining wall is built in pieces of wall_piece_m that follow the ground (its top and bottom per
            # piece), so the visible face at a piece's low end is bounded by the ground span over one piece
            "wall_piece_m": 1.0,
            # review of round 3 (real04: 5 bands of sp_001 / sp_002 stood inside the basement L-1 at -2.2 .. -0.9 m,
            # 1.2-2.1 m tall blocks in its rooms, and walls stood on the terrace edges drawn 0.65 m inside the
            # building): an edge whose outside, keep_out_reach out, lies in the building outline or a copy's footprint
            # faces the building (``against_edges``: no wall, band, steps or railing: the building's wall retains
            # there); a band may reach keep_out_wall into the outline (the outer wall's thickness), no further, and
            # never into another platform (``_band_blocked``)
            "keep_out_reach": 0.3, "keep_out_wall": 0.25}
# Round 3 (docs/milestone13.md §14.3 row 'platforms'; P1 real04 ext_1 'platforms' and 'all'): the retaining wall of
# sp_001 (level -3.0 m, ground 1.86 m under and 1.79 m over it) showed as a tall white box. No retaining wall is
# taller than this: a larger level difference along an edge becomes stepped terraces (``stepped_bands``: bands of
# ``band_w`` outside the edge, each ``RETAINING_MAX_M`` or less above the next, down to the ground; a cut (the ground
# above the level) steps up the same way).
RETAINING_MAX_M = 1.2
# 25 Oct 2026: a cut wall that holds the ground more than this over the platform (only where no stepped band fits)
# carries a guard on its top (the fall from the ground outside into the platform).
GUARD_RISE_M = RETAINING_MAX_M
PLATFORM_KINDS = {"paving": "terrace", "parking": "parking", "pools": "pool", "path": "path"}
POOL_COPING_M = 0.35


def _site_ground_fn(site: dict, terrain: Optional[dict]):
    """``gz(x, y)`` for ``platforms``: the terrain model when given, else the site's surface, else its flat level."""
    if terrain is not None:
        return lambda x, y: ground_z(terrain, x, y)
    ground = site.get("ground") if isinstance(site.get("ground"), dict) else {}
    surface = ground.get("surface") if isinstance(ground.get("surface"), dict) else None
    if surface and surface.get("kind") in ("planar", "tin") and len(surface.get("points") or []) >= 3:
        return lambda x, y: LT.surface_z(surface, x, y)
    flat = 0.0
    for entry in ground.get("levels") or []:
        z = _value((entry or {}).get("z")) if isinstance(entry, dict) else None
        if z is not None:
            flat = z
            break
    return lambda x, y: flat


def subdivide_edges(poly, max_len: float) -> list[tuple[float, float]]:
    """The polygon with every edge longer than ``max_len`` cut into equal pieces of at most ``max_len`` (pure;
    collinear points added, the winding kept)."""
    pts = [(float(x), float(y)) for x, y in poly]
    out: list[tuple[float, float]] = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        out.append(a)
        length = G.distance(a, b)
        k = int(math.ceil(length / max_len - 1e-9)) if max_len > 0 else 1
        for j in range(1, max(1, k)):
            out.append(G.point_along_segment(a, b, j / k))
    return out


def _edge_samples(poly, k: int = 3) -> list[list[tuple[float, float]]]:
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        out.append([G.point_along_segment(a, b, (j + 0.5) / k) for j in range(k)])
    return out


def floor_level(poly, g: dict, facades: Optional[dict]) -> Optional[tuple[float, str, list[str]]]:
    """The floor level a terrace beside a building takes when no level mark sets it (pure; 25 Oct 2026, real04: the
    east pool deck at the mean ground, -1.40 m, buried the basement window and got a front court cut into it, while
    its mirror twin at the basement floor from a level mark let the window open onto it). ``(z, reason, opening
    ids)`` or None: the doors and windows whose outside (``facade_openings`` probe) lies on the platform, or within
    ``FLOOR_SNAP["probe_m"]`` of it, open onto it; the candidates are the floors of their buildings within
    ``FLOOR_SNAP["reach_m"]`` of the ground under the platform; a floor that buries one of them (a window sill less
    than ``LIGHT_WELL_CLEARANCE`` over it, a door under it) is out; of the rest the one most doors open onto at their
    threshold wins, then the one nearest the mean ground. None when no opening faces the platform or every floor
    buries one (the mean ground stays, with its light wells)."""
    if not facades:
        return None
    facing = [o for o in facades.get("openings") or [] if G.point_in_polygon(o["probe"], poly)
              or geom2d.distance_to_polygon_edges(o["probe"], poly) <= FLOOR_SNAP["probe_m"]]
    if not facing:
        return None
    lo, hi = float(g["min"]) - FLOOR_SNAP["reach_m"], float(g["max"]) + FLOOR_SNAP["reach_m"]
    best = None
    for bid in sorted({o["building"] for o in facing}):
        mine = [o for o in facing if o["building"] == bid]
        for z, ids in (facades.get("floors") or {}).get(bid) or []:
            if not lo <= z <= hi:
                continue
            buried = [o["id"] for o in mine if (o["type"] == "window" and o["bottom"] < z + LIGHT_WELL_CLEARANCE)
                      or (o["type"] == "door" and o["bottom"] < z - LIGHT_WELL_CLEARANCE)]
            if buried:
                continue
            served = [o["id"] for o in mine if o["type"] == "door" and abs(o["bottom"] - z) <= FLOOR_SNAP["door_step_m"]]
            key = (-len(served), abs(z - float(g["mean"])))
            if best is None or key < best[0]:
                names = "/".join(ids) + (f" of {bid}" if len(facades.get("floors") or {}) > 1 else "")
                why = (f"the floor of {names} ({z:+.2f} m): "
                       + (f"the doors {', '.join(served)} open onto it" if served else
                          f"the windows {', '.join(sorted({o['id'] for o in mine}))} open over it")
                       + f" (a terrace takes the floor its doors and windows serve; the mean ground under it "
                         f"{float(g['mean']):+.2f} m)")
                best = (key, z, why, sorted({o["id"] for o in mine}))
    return None if best is None else (round(best[1], 3), best[2], best[3])


# 25 Oct 2026: a terrace that doors or windows open onto takes a floor of their building (``floor_level``): within
# reach_m of the ground under it, a door's threshold within door_step_m of it, the openings 0.3 m out of the wall face
# within probe_m of the platform.
FLOOR_SNAP = {"reach_m": 1.0, "probe_m": 0.5, "door_step_m": 0.2}


def hedge_keep_out(hedges: Sequence[dict]) -> list[tuple[str, list]]:
    """``[(hedge id, rectangle)]``: every drawn hedge's hull, one rectangle per stretch of its polyline (pure; 25 Oct
    2026: a stepped band, an inferred part, stops at a drawn hedge instead of running under it)."""
    out = []
    for h in hedges or []:
        pts, hw = h.get("polyline") or [], float(h.get("width_m") or 0.0) / 2.0
        for a, b in zip(pts, pts[1:]):
            length = G.distance(a, b)
            if length > 1e-6 and hw > 0:
                d = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
                out.append((str(h.get("id")), _rect_along(a, d, -hw, length + hw, hw)))
    return out


def platforms(site: dict, terrain: Optional[dict] = None, keep_out: Sequence = (),
              facades: Optional[dict] = None, band_keep: Sequence[tuple[str, list]] = ()) -> list[dict]:
    """One level per drawn terrace, pool or parking polygon (pure; Milestone 13 T6, docs/milestone13.md §13.2):
    ``[{"id", "polygon", "holes", "z", "kind": terrace | pool | parking | path, "edge": retaining | kerb | steps |
    none, "source", "z_source", "marks", "ground": {min, mean, max}, "drop_m", "rise_m", "sloped", "steps_edge",
    "railing_edges", "pools", "inferred": true, "reason"}]``.

    The level ``z``: the mean of the level marks (``site.ground.points`` of a ground kind) inside the polygon or
    within ``mark_reach`` of it, else the mean ground under it (``PLATFORM["round"]``); marks that spread more
    than ``max_spread`` say the area is drawn sloped (a driveway): it stays draped (``sloped``) with kerbs. A pool
    joins the terrace platform within ``pool_join_m`` of it (one deck level, the pool a hole in the slab), else it
    gets its own deck ``pool_deck_m`` wide. The edge treatment: ``none`` / ``kerb`` within ``level_tol`` of the
    ground, ``steps`` when the lowest drop of a terrace or pool deck is at most ``step_max_drop`` (the flight on the
    longest such edge, retaining walls on the others), else ``retaining``; ``railing_edges`` are the edges with a
    drop over ``railing_drop``. ``keep_out``: the building's ground outline and the copies' footprints (``site_plan``,
    ``platforms_into_building``): the edges facing them are ``against_edges`` (no wall, band, steps or railing) and no
    stepped band enters them (review of round 3)."""
    gz = _site_ground_fn(site, terrain)
    keep = [geom2d.ccw(p) for p in (keep_out or []) if len(p or []) >= 3]
    keep_inner = [q for q in (geom2d.offset_polygon(p, PLATFORM["keep_out_wall"]) for p in keep) if len(q) >= 3]
    ground = site.get("ground") if isinstance(site.get("ground"), dict) else {}
    marks = [m for m in ground.get("points") or [] if isinstance(m, dict) and m.get("z") is not None
             and str(m.get("kind") or "ground").startswith("ground")]
    reach = PLATFORM["mark_reach"]

    def level_of(poly):
        near = [m for m in marks if G.point_in_polygon((m["x"], m["y"]), poly)
                or geom2d.distance_to_polygon_edges((m["x"], m["y"]), poly) <= reach]
        samples = list(poly) + [G.polygon_centroid(poly)] + [q for seg in _edge_samples(poly) for q in seg]
        zs = [gz(x, y) for x, y in samples]
        g = {"min": round(min(zs), 3), "mean": round(sum(zs) / len(zs), 3), "max": round(max(zs), 3)}
        if near:
            vals = [float(m["z"]) for m in near]
            z = sum(vals) / len(vals)
            return (round(round(z / PLATFORM["round"]) * PLATFORM["round"], 3), "level marks",
                    [str(m.get("mark_id") or m.get("id") or k) for k, m in enumerate(near)],
                    g, max(vals) - min(vals) > PLATFORM["max_spread"])
        snap = floor_level(poly, g, facades)
        if snap is not None:
            return snap[0], snap[1], [], g, False
        return round(round(g["mean"] / PLATFORM["round"]) * PLATFORM["round"], 3), "the mean ground under it", [], g, False

    def edges_of(poly, z, kind, sloped, skip=()):
        rec = {"drop_m": 0.0, "rise_m": 0.0, "steps_edge": None, "railing_edges": [], "edge": "none"}
        if sloped:
            rec["edge"] = "kerb"
            return rec
        drops, rises = [], []
        for i, seg in enumerate(_edge_samples(poly)):
            if i in skip:                                   # a band's inner edge faces its parent, not the ground
                drops.append(0.0)
                rises.append(0.0)
                continue
            zs = [gz(x, y) for x, y in seg]
            drops.append(z - min(zs))
            rises.append(max(zs) - z)
        rec["drop_m"], rec["rise_m"] = round(max(drops), 3), round(max(rises), 3)
        rec["edge_drops"] = {i: round(v, 3) for i, v in enumerate(drops)}       # architect.access_edge reads them
        tol = PLATFORM["level_tol"]
        n = len(poly)
        rec["railing_edges"] = [i for i in range(n) if drops[i] > PLATFORM["railing_drop"]]
        if rec["drop_m"] <= tol and rec["rise_m"] <= tol:
            rec["edge"] = "kerb" if kind in ("parking", "path") else "none"
            return rec
        rec["edge_rises"] = {i: round(v, 3) for i, v in enumerate(rises) if i not in skip}
        cands = [i for i in range(n) if tol < drops[i] <= PLATFORM["step_max_drop"]
                 and G.distance(poly[i], poly[(i + 1) % n]) >= PLATFORM["step_width"]]
        # 25 Oct 2026 (real04: the east pool deck at the basement floor lies under the ground on every side): a sunken
        # terrace with no edge to step down from gets a flight up into the slope on the edge with the smallest rise
        ups = [i for i in range(n) if i not in skip and drops[i] <= tol and tol < rises[i] <= PLATFORM["step_max_drop"]
               and G.distance(poly[i], poly[(i + 1) % n]) >= PLATFORM["step_width"] + 2 * PLATFORM["wall_t"]]
        if kind in ("terrace", "pool") and cands:
            rec["steps_edge"] = max(cands, key=lambda i: (G.distance(poly[i], poly[(i + 1) % n]), -drops[i]))
            rec["edge"] = "steps"
        elif kind in ("terrace", "pool") and ups:
            ups.sort(key=lambda i: (rises[i], -G.distance(poly[i], poly[(i + 1) % n])))
            rec["steps_edge"], rec["up_edges"] = ups[0], ups
            rec["steps_dir"] = "up"
            rec["edge"] = "steps"
        else:
            rec["edge"] = "retaining"
        return rec

    out = []
    pools = [p for p in _built(site.get("pools")) if len(p.get("polygon") or []) >= 3]
    for key in ("paving", "parking"):
        for a in _built(site.get(key)):
            poly = geom2d.ccw(a.get("polygon") or [])
            if len(poly) < 3:
                continue
            kind = PLATFORM_KINDS[key]
            z, z_src, mark_ids, g, sloped = level_of(poly)
            out.append({"id": str(a.get("id") or f"{kind}_{len(out) + 1}"), "polygon": poly, "holes": [], "z": z,
                        "kind": kind, "source": a.get("source"), "area_id": a.get("area_id"), "z_source": z_src,
                        "marks": mark_ids, "ground": g, "sloped": sloped, "pools": [], "inferred": True,
                        "material": a.get("material"), "colour": a.get("colour")})
    for k, pool in enumerate(pools):
        poly = geom2d.ccw(pool["polygon"])
        pid = str(pool.get("id") or f"pool_{k + 1:03d}")
        host = None
        for pf in out:
            if pf["kind"] != "terrace" or pf["sloped"]:
                continue
            if any(G.point_in_polygon(q, pf["polygon"]) for q in poly) or \
                    min(geom2d.distance_to_polygon_edges(q, pf["polygon"]) for q in poly) <= PLATFORM["pool_join_m"]:
                host = pf
                break
        if host is not None:
            deck = geom2d.offset_polygon(poly, -POOL_COPING_M - 0.3)
            union = geom2d.polygon_union_outline([host["polygon"], deck]) if len(deck) >= 3 else []
            outer = [r for r in union if G.polygon_signed_area(r) > 0]
            if len(outer) == 1 and len(outer[0]) >= 3:
                host["polygon"] = geom2d.ccw(outer[0])
            host["holes"].append(poly)
            host["pools"].append(pid)
            continue
        deck = geom2d.ccw(geom2d.offset_polygon(poly, -PLATFORM["pool_deck_m"]))
        z, z_src, mark_ids, g, sloped = level_of(deck if len(deck) >= 3 else poly)
        out.append({"id": f"{pid}_deck", "polygon": deck if len(deck) >= 3 else poly, "holes": [poly], "z": z,
                    "kind": "pool", "source": pool.get("source"), "area_id": None, "z_source": z_src,
                    "marks": mark_ids, "ground": g, "sloped": False, "pools": [pid], "inferred": True,
                    "material": None, "colour": None})
    for pf in out:
        if not pf["sloped"]:                        # round 3: short edges, each with its own wall and bands
            pf["polygon"] = subdivide_edges(pf["polygon"], PLATFORM["edge_split_m"])
        pf["against_edges"] = [] if pf["sloped"] else against_edges(pf["polygon"], keep)
        pf.update(edges_of(pf["polygon"], pf["z"], pf["kind"], pf["sloped"], skip=pf["against_edges"]))
    for pf in out:
        if pf.get("steps_dir") != "up":
            continue
        # the flight lands on a paved area (a driveway, a path, another terrace) where one of its edges allows it,
        # else on the edge with the smallest rise (the garden)
        paved = [q["polygon"] for q in out if q is not pf]
        for i in pf.get("up_edges") or [pf["steps_edge"]]:
            fl = up_flight(dict(pf, steps_edge=i), gz=gz)
            if fl is not None and any(G.point_in_polygon(fl["landing"], q) for q in paved):
                pf["steps_edge"] = i
                pf["flight_lands_on"] = next(q["id"] for q in out if q is not pf
                                             and G.point_in_polygon(fl["landing"], q["polygon"]))
                break
        pf["flight"] = up_flight(pf, gz=gz)
    for pf in out:
        pf["reason"] = (f"{pf['kind']} {pf['id']}: one level at {pf['z']:+.2f} m ({pf['z_source']}"
                        + (f" {', '.join(pf['marks'])}" if pf["marks"] else "") + f"); ground {pf['ground']['min']:+.2f}"
                        f"..{pf['ground']['max']:+.2f} m under it; edge: {pf['edge']}"
                        + (" (the marks spread over 1 m: the area is drawn sloped and stays draped)" if pf["sloped"] else "")
                        + (f"; pools {', '.join(pf['pools'])} in the deck" if pf["pools"] else "") + " (inferred)")
    # Round 3: the stepped terraces where a retaining wall would pass RETAINING_MAX_M; every record says the tallest
    # wall it builds (wall_max_m).
    bands: list[dict] = []
    for pf in out:
        if pf["sloped"]:
            pf["wall_max_m"] = 0.0
            pf["cap_exceeded"] = []
            continue
        others = [q for q in out if q is not pf]
        # a hedge drawn on the platform itself (fit_hedges keeps it there) is planted on it, not in a band's way
        hedges_out = [(hid, poly) for hid, poly in band_keep
                      if not G.point_in_polygon(G.polygon_centroid(poly), pf["polygon"])
                      and geom2d.distance_to_polygon_edges(G.polygon_centroid(poly), pf["polygon"])
                      > HEDGE_FIT["max_shift_m"] + 0.5]
        for band in stepped_bands(pf, gz, keep_out=keep_inner + [q["polygon"] for q in others]
                                  + [poly for _, poly in hedges_out],
                                  keep_ids=["building"] * len(keep_inner) + [q["id"] for q in others]
                                  + [hid for hid, _ in hedges_out]):
            band["against_edges"] = []
            band.update(edges_of(band["polygon"], band["z"], band["kind"], False, skip=band["shared_edges"]))
            band["steps_edge"], band["railing_edges"] = None, []
            band.pop("steps_dir", None)
            band["edge"] = "retaining"
            band["wall_max_m"] = platform_wall_max(band, gz)
            # the outermost band of a chain that had no room for the next one keeps its full outer wall
            chain_by = {b["edge"]: b.get("by") for b in pf.get("band_blocked") or []}
            # a band's side (not its outer edge) never steps on: the rising ground beside a band's end is held by a
            # full wall there (with a guard on it over the cap), recorded as band_side (25 Oct 2026)
            band["cap_exceeded"] = [{"edge": i, "height_m": h,
                                     "blocked_by": chain_by.get(band["stepped_from"]["edge"])
                                     if i == band.get("outer_edge") else "band_side"}
                                    for i, h in sorted(platform_wall_edges(band, gz).items())
                                    if h > RETAINING_MAX_M + 1e-6]
            band["reason"] = (f"terrace {band['id']}: step {band['step']} of {band['parent']} at {band['z']:+.2f} m "
                              f"(stepped terrace: the ground lies {band['stepped_from']['difference_m']:.2f} m "
                              f"{'under' if band['stepped_from']['direction'] == 'down' else 'over'} the level along "
                              f"its edge {band['stepped_from']['edge']}, more than the {RETAINING_MAX_M} m retaining "
                              f"cap); ground {band['ground']['min']:+.2f}..{band['ground']['max']:+.2f} m under it; "
                              f"edge: retaining (inferred)")
            bands.append(band)
        pf["wall_max_m"] = platform_wall_max(pf, gz)
        # review of round 3: a wall over the cap stays only where a band had no room (another drawn platform or the
        # building outside the edge); it is recorded with the edge and what blocked it, never silent
        blocked_by = {b["edge"]: b.get("by") for b in pf.get("band_blocked") or []}
        pf["cap_exceeded"] = [{"edge": i, "height_m": h, "blocked_by": blocked_by.get(i)}
                              for i, h in sorted(platform_wall_edges(pf, gz).items()) if h > RETAINING_MAX_M + 1e-6]
        if pf["cap_exceeded"]:
            pf["reason"] += ("; retaining wall over the cap where no band fits: " + ", ".join(
                f"edge {c['edge']} {c['height_m']:.2f} m (next to {c['blocked_by'] or 'the plot'})"
                for c in pf["cap_exceeded"]))
        if pf.get("stepped"):
            pf["reason"] += (f"; stepped terraces on edge{'s' if len(pf['stepped']) > 1 else ''} "
                             + ", ".join(f"{st['edge']} ({st['bands']} x {st['step_m']:.2f} m {st['direction']})"
                                         for st in pf["stepped"]) + f" (retaining cap {RETAINING_MAX_M} m)")
        if pf.get("flight"):
            pf["reason"] += (f"; a flight of {pf['flight']['count']} steps up out of it on edge {pf['steps_edge']} "
                             f"({pf['flight']['rise']:.2f} m" + (f", onto {pf['flight_lands_on']}" if
                                                                 pf.get("flight_lands_on") else "") + ")")
        if pf.get("against_edges"):
            pf["reason"] += (f"; edges {', '.join(str(i) for i in pf['against_edges'])} face the building (its walls "
                             f"retain there: no wall, band or steps)")
        if pf.get("band_blocked"):
            pf["reason"] += ("; no further stepped band where it would enter the building or another platform (edge "
                             + ", ".join(f"{b['edge']} after {b['bands']}" for b in pf["band_blocked"]) + ")")
    return out + bands


def _inside_any(p, polygons) -> bool:
    return any(G.point_in_polygon(p, poly) for poly in polygons)


def against_edges(poly, keep_out: Sequence, reach: Optional[float] = None) -> list[int]:
    """The edges of a platform that face the building (pure; review of round 3): the point ``reach``
    (``PLATFORM["keep_out_reach"]``) outside the edge at a quarter, the half and three quarters of its length lies in
    a ``keep_out`` polygon (the building's ground outline, a copy's footprint) for at least two of the three. There
    the building's own wall retains the ground: no retaining wall, stepped band, steps or railing (real04 sp_001
    is drawn 0.65 m into the basement L-1: its edges along x 1.0 and 1.65 m)."""
    reach = float(PLATFORM["keep_out_reach"] if reach is None else reach)
    if not keep_out:
        return []
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-9:
            continue
        nx, ny = (b[1] - a[1]) / length, -(b[0] - a[0]) / length      # ccw: outward is to the right of the edge
        hits = 0
        for t in (0.25, 0.5, 0.75):
            p = G.point_along_segment(a, b, t)
            hits += int(_inside_any((p[0] + nx * reach, p[1] + ny * reach), keep_out))
        if hits >= 2:
            out.append(i)
    return out


def _band_blocked(quad, keep_out: Sequence) -> Optional[int]:
    """The index of the first ``keep_out`` polygon a stepped band's quad ``[a_in, b_in, b_out, a_out]`` enters, else
    None (pure; review of round 3): any of 18 points inside the quad (a 6 x 3 grid of its bilinear parameters, the
    boundary left out) lies in it. ``platforms`` passes the building outline and the copies' footprints shrunk by
    ``keep_out_wall`` (a band may end inside the outer wall) and the other platforms."""
    p00, p10, p11, p01 = quad[0], quad[1], quad[2], quad[3]
    for u in (1 / 12, 3 / 12, 5 / 12, 7 / 12, 9 / 12, 11 / 12):
        for v in (1 / 6, 3 / 6, 5 / 6):
            x = (1 - u) * (1 - v) * p00[0] + u * (1 - v) * p10[0] + u * v * p11[0] + (1 - u) * v * p01[0]
            y = (1 - u) * (1 - v) * p00[1] + u * (1 - v) * p10[1] + u * v * p11[1] + (1 - u) * v * p01[1]
            for j, poly in enumerate(keep_out):
                if G.point_in_polygon((x, y), poly):
                    return j
    return None


def _offset_corner(point, n_this, n_other, w: float, mitre: bool):
    """A corner of a band's edge moved outward by ``w`` (pure): along the bisector of this edge's outward normal
    ``n_this`` and the neighbouring edge's ``n_other`` when ``mitre`` (the neighbouring edge is stepped too, so the
    two bands meet without a gap or an overlap), else square: along ``n_this`` alone (review of round 3: the square
    branch offset along the argument that held the *next* edge's normal for the b corner, so every non-mitred b
    corner left the band skewed along the neighbouring edge)."""
    if mitre:
        dot = n_this[0] * n_other[0] + n_this[1] * n_other[1]
        if 1.0 + dot > 0.2:
            f = w / (1.0 + dot)
            return (point[0] + (n_this[0] + n_other[0]) * f, point[1] + (n_this[1] + n_other[1]) * f)
    return (point[0] + n_this[0] * w, point[1] + n_this[1] * w)


def _edge_excess(poly, i: int, z: float, gz, zone_w: float = 0.0):
    """``(direction, difference_m)`` of edge ``i`` against the ground (pure): ``down`` with the fill height when the
    ground lies under the level, ``up`` with the cut height when it lies over it (the larger of the two). With
    ``zone_w`` the ground of the band zone outside the edge (the strip ``zone_w`` wide) counts too."""
    n = len(poly)
    a, b = poly[i], poly[(i + 1) % n]
    pts = _edge_samples([a, b], 4)[0] + [a, b]
    length = G.distance(a, b)
    if zone_w > 0 and length > 1e-9:
        nx, ny = (b[1] - a[1]) / length, -(b[0] - a[0]) / length
        pts += [(x + nx * zone_w, y + ny * zone_w) for x, y in pts]
        pts += [(x + nx * zone_w / 2.0, y + ny * zone_w / 2.0) for x, y in pts[:6]]
    zs = [gz(*q) for q in pts]
    drop, rise = z - min(zs), max(zs) - z
    return ("down", drop) if drop >= rise else ("up", rise)


def stepped_bands(pf: dict, gz, cap: float = RETAINING_MAX_M, keep_out: Sequence = (),
                  keep_ids: Sequence = ()) -> list[dict]:
    """The intermediate terraces of a platform (pure; round 3): for every edge whose ground lies more than ``cap``
    under (fill) or over (cut) the level, bands ``PLATFORM["band_w"]`` wide outside the edge, each a step of at most
    ``cap`` below (or above) the one before, until the outermost band's own wall to the ground is within the cap
    (at most ``band_max`` bands). Band ends are mitred where the neighbouring edge is stepped the same way, square
    (on this edge's normal) elsewhere and for the whole edge when a mitred band would be a bow-tie
    (``_band_quad_ok``; the record says ``mitred``). Writes
    ``pf["stepped"]`` (``[{edge, bands, step_m, direction}]``) and ``pf["edge_floor"]`` (edge index as a string ->
    the first band's level: the parent's wall on that edge ends there) and returns the band records: ``id``
    ``<parent>_s<k>e<edge>``, ``parent``, ``step``, ``kind`` ``terrace``, ``z``, ``polygon``, ``shared_edges`` (the
    inner edge and a mitred end edge: the parent or the neighbouring band is there, no wall), ``edge_floor`` (an
    intermediate band's outer edge ends at the next band), ``bottom_z`` (the slab's bottom: the parent's level minus
    ``below``), ``ground``, ``stepped_from``. A sloped (draped) platform gets none. Review of round 3: an edge in
    ``pf["against_edges"]`` (it faces the building) gets no band, and a band whose quad enters a ``keep_out`` polygon
    (``_band_blocked``) is not built: the edge keeps the bands before it (``pf["band_blocked"]``: edge, bands, the
    blocking polygon's ``keep_ids`` entry)."""
    poly = geom2d.ccw(pf["polygon"])
    n = len(poly)
    z = float(pf["z"])
    pf["stepped"] = []
    pf["edge_floor"] = {}
    pf["band_blocked"] = []
    against = set(pf.get("against_edges") or [])
    if pf.get("sloped") or n < 3:
        return []
    band_w = PLATFORM["band_w"]
    normals, excess = [], []
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-9:
            normals.append((0.0, 0.0))
            excess.append(None)
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        normals.append((uy, -ux))                              # ccw: outward is to the right of the edge
        direction, diff = _edge_excess(poly, i, z, gz, zone_w=band_w)
        excess.append((direction, diff) if diff > cap + 1e-9 and length >= band_w / 2.0 and i not in against
                      else None)
    bands = []
    for i in range(n):
        if excess[i] is None:
            continue
        direction, diff = excess[i]
        sign = -1.0 if direction == "down" else 1.0
        count = max(1, int(math.ceil(diff / cap - 1e-9)))
        step = diff / count
        prev_i, next_i = (i - 1) % n, (i + 1) % n
        same_a = excess[prev_i] is not None and excess[prev_i][0] == direction
        same_b = excess[next_i] is not None and excess[next_i][0] == direction
        a, b = poly[i], poly[next_i]

        # Mitred ends where the neighbouring edge steps the same way; square ends for the whole edge when a mitred
        # band would be a bow-tie (a reflex corner, or an edge shorter than the mitre: real04 sp_001 edge 16 is
        # 0.67 m long and its band's offset corners crossed, a twisted slab of 0.4 m² over a 0.08 m² polygon) or
        # would enter a keep-out polygon that square ends miss (review of round 3: real04 sp_002 edge 14, whose
        # mitred end reached into the parking spk_001).
        def attempt(mitre_a: bool, mitre_b: bool):
            mine: list[dict] = []
            k = 0
            while k < PLATFORM["band_max"]:
                k += 1
                zk = round(z + sign * k * step, 3)
                w_in, w_out = (k - 1) * band_w, k * band_w
                a_in = _offset_corner(a, normals[i], normals[prev_i], w_in, mitre_a) if w_in > 0 else a
                b_in = _offset_corner(b, normals[i], normals[next_i], w_in, mitre_b) if w_in > 0 else b
                a_out = _offset_corner(a, normals[i], normals[prev_i], w_out, mitre_a)
                b_out = _offset_corner(b, normals[i], normals[next_i], w_out, mitre_b)
                if not _band_quad_ok(a_in, b_in, b_out, a_out):
                    return mine, "bow-tie", None
                hit = _band_blocked([a_in, b_in, b_out, a_out], keep_out)
                if hit is not None:                             # it would enter the building or another platform
                    return mine, "blocked", hit
                # 25 Oct 2026 (real04 sp_004 at its floor level: the bands of two short edges of a notch overlapped):
                # a band never enters this platform's earlier bands; the first band of an edge whose place an earlier
                # band at its level already takes is served by it (the edge's wall ends at that band)
                own = _band_blocked([a_in, b_in, b_out, a_out], [q["polygon"] for q in bands])
                if own is not None:
                    if k == 1 and abs(float(bands[own]["z"]) - zk) <= PLATFORM["level_tol"]:
                        return mine, "served", own
                    return mine, "blocked_own", own
                quad = geom2d.ccw([a_in, b_in, b_out, a_out])

                def edge_index(p0, p1):
                    m = G.segment_midpoint(p0, p1)
                    return next((j for j in range(len(quad))
                                 if G.distance(G.segment_midpoint(quad[j], quad[(j + 1) % len(quad)]), m) < 1e-6), None)

                shared = [j for j in (edge_index(a_in, b_in), edge_index(a_in, a_out) if mitre_a else None,
                                      edge_index(b_in, b_out) if mitre_b else None) if j is not None]
                outer_idx = edge_index(a_out, b_out)
                if mine and mine[-1].get("outer_edge") is not None:
                    mine[-1]["edge_floor"][str(mine[-1]["outer_edge"])] = zk   # the band before ends at this level
                samples = list(quad) + [G.polygon_centroid(quad)] + [q for seg in _edge_samples(quad) for q in seg]
                zs = [gz(x, y) for x, y in samples]
                ground = {"min": round(min(zs), 3), "mean": round(sum(zs) / len(zs), 3), "max": round(max(zs), 3)}
                outer = [gz(*q) for q in _edge_samples([a_out, b_out], 4)[0]] + [gz(*a_out), gz(*b_out)]
                left = (zk - min(outer)) if direction == "down" else (max(outer) - zk)
                mine.append({"id": f"{pf['id']}_s{k}e{i}", "parent": pf["id"], "step": k, "polygon": quad,
                             "holes": [], "z": zk, "kind": "terrace", "source": "stepped", "area_id": pf.get("area_id"),
                             "z_source": "stepped terrace", "marks": [], "ground": ground, "sloped": False,
                             "pools": [], "inferred": True, "material": pf.get("material"), "colour": pf.get("colour"),
                             "shared_edges": shared, "outer_edge": outer_idx, "edge_floor": {},
                             "bottom_z": round(z - PLATFORM["below"], 3), "mitred": [bool(mitre_a), bool(mitre_b)],
                             "stepped_from": {"edge": i, "direction": direction, "difference_m": round(diff, 3),
                                              "step_m": round(step, 3)}})
                if left <= cap + 1e-9:
                    return mine, "done", None
            return mine, "band_max", None                   # band_max bands and the outermost wall still over the cap

        chosen = None
        for mitre_a, mitre_b in [(same_a, same_b)] + ([(False, False)] if same_a or same_b else []):
            mine, status, hit = attempt(mitre_a, mitre_b)
            complete = status in ("done", "band_max", "served")
            if chosen is None or complete or len(mine) > len(chosen[0]):
                chosen = (mine, status, hit, mitre_a, mitre_b)
            if complete:
                break
        mine, status, hit, mitre_a, mitre_b = chosen
        if status == "served":
            pf["edge_floor"][str(i)] = float(bands[hit]["z"])
            pf.setdefault("band_served", []).append({"edge": i, "by": bands[hit]["id"]})
            continue
        if status == "blocked_own":
            pf["band_blocked"].append({"edge": i, "bands": len(mine), "direction": direction, "by": bands[hit]["id"]})
        elif status in ("blocked", "band_max"):
            by = "band_max" if status == "band_max" else (keep_ids[hit] if hit is not None and hit < len(keep_ids)
                                                           else "keep_out")
            pf["band_blocked"].append({"edge": i, "bands": len(mine), "direction": direction, "by": by})
        if not mine:
            continue
        bands += mine
        pf["stepped"].append({"edge": i, "bands": len(mine), "step_m": round(step, 3), "direction": direction,
                              "mitred": [bool(mitre_a), bool(mitre_b)]})
        pf["edge_floor"][str(i)] = round(z + sign * step, 3)
    return bands


def _segments_cross(p0, p1, q0, q1) -> bool:
    """Whether the open segments ``p0``-``p1`` and ``q0``-``q1`` cross each other (pure; a shared end is no
    crossing)."""
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(q0, q1, p0), orient(q0, q1, p1)
    d3, d4 = orient(p0, p1, q0), orient(p0, p1, q1)
    return d1 * d2 < -1e-12 and d3 * d4 < -1e-12


def _band_quad_ok(a_in, b_in, b_out, a_out) -> bool:
    """A stepped band's quad is a proper strip (pure): its outer edge runs the way of its inner edge, its two end
    edges do not cross and it has an area. A mitred band at a reflex corner, or on an edge shorter than its mitre,
    fails (a bow-tie) and the edge gets square ends instead."""
    ux, uy = b_in[0] - a_in[0], b_in[1] - a_in[1]
    if (b_out[0] - a_out[0]) * ux + (b_out[1] - a_out[1]) * uy <= 1e-9:
        return False
    if abs(G.polygon_signed_area([a_in, b_in, b_out, a_out])) < 1e-6:
        return False
    return not _segments_cross(a_in, a_out, b_in, b_out)


def sloped_box(centre, length: float, thickness: float, angle_deg: float, z0: float, z1_start: float,
               z1_end: float, z0_end: Optional[float] = None) -> tuple[list, list]:
    """``(verts, faces)`` of a wall, kerb or rail piece (pure): ``length`` along ``angle_deg``, ``thickness``
    across, its bottom from ``z0`` (the start end) to ``z0_end`` (default ``z0``: flat) and its top from
    ``z1_start`` to ``z1_end`` (25 Oct 2026: pieces with flat tops stepped like teeth along a slope)."""
    z0_end = z0 if z0_end is None else z0_end
    lo, top = min(z0, z0_end), max(z1_start, z1_end)
    v, f = geom2d.box((centre[0], centre[1], (lo + top) / 2.0), (length, thickness, top - lo), angle_deg)
    v = [list(p) for p in v]
    for k, zb in ((0, z0), (3, z0), (1, z0_end), (2, z0_end)):
        v[k][2] = zb
    for k, zt, zb in ((4, z1_start, z0), (7, z1_start, z0), (5, z1_end, z0_end), (6, z1_end, z0_end)):
        v[k][2] = max(zt, zb + 0.01)
    return [tuple(p) for p in v], f


def guard_parts(p0, p1, z_start: float, z_end: float) -> tuple[list, list, list]:
    """``(rails, panels, posts)`` of a guard on a sloping wall top from ``p0`` (standing at ``z_start``) to ``p1``
    (``z_end``) (pure; ``shell.RAILING`` sizes: a rail, a glass panel and a post at ``p0``; 25 Oct 2026)."""
    from wenart.blender.shell import RAILING as R

    length = G.distance(p0, p1)
    if length <= 1e-6:
        return [], [], []
    mid, angle = G.segment_midpoint(p0, p1), G.segment_angle_deg(p0, p1)
    h, r = float(R["height"]), float(R["rail"])
    rail = sloped_box(mid, length, r, angle, z_start + h - r, z_start + h, z_end + h, z_end + h - r)
    panel = sloped_box(mid, length, float(R["panel"]), angle, z_start + float(R["panel_bottom"]), z_start + h - r,
                       z_end + h - r, z_end + float(R["panel_bottom"]))
    post = geom2d.box((p0[0], p0[1], z_start + (h - r) / 2.0), (float(R["post"]), float(R["post"]), h - r), angle)
    return [rail], [panel], [post]


def wall_pieces(a, b, z: float, gz, floor: Optional[float] = None, piece_m: Optional[float] = None) -> list[dict]:
    """The retaining wall pieces along one platform edge (pure; round 3): the edge cut into pieces of at most
    ``piece_m`` (``PLATFORM["wall_piece_m"]``); a piece gets a wall when the ground along it lies more than
    ``level_tol`` under the level (fill) or over it (cut), from ``below`` under its lowest ground (or the level) to
    the level + ``lip`` (fill) or its highest ground + 0.1 (cut). With ``floor`` (a stepped band outside the edge)
    the piece's ground is the band's level and the wall ends there. ``height_m`` is the face a viewer can see:
    ``max(z, ground max) - min(z, ground min)`` over the piece (the fill height, the cut height, or the ground span
    where the ground crosses the level). ``[{"p0", "p1", "zs", "drop", "rise", "z0", "z1", "height_m", "to_band"}]``."""
    piece_m = float(piece_m or PLATFORM["wall_piece_m"])
    length = G.distance(a, b)
    if length < 0.05:
        return []
    k = max(1, int(math.ceil(length / piece_m - 1e-9)))
    tol, lip, below = PLATFORM["level_tol"], PLATFORM["lip"], PLATFORM["below"]
    out = []
    for j in range(k):
        p0, p1 = G.point_along_segment(a, b, j / k), G.point_along_segment(a, b, (j + 1) / k)
        if floor is not None:
            zs = [float(floor)]
        else:
            zs = [gz(*q) for q in _edge_samples([p0, p1], 4)[0]] + [gz(*p0), gz(*p1)]
        drop, rise = z - min(zs), max(zs) - z
        if drop <= tol and rise <= tol:
            continue
        z0 = min(z, min(zs)) - below
        z1 = max(z + lip, max(zs) + (lip if floor is not None else 0.1)) if rise > tol else z + lip
        # 25 Oct 2026 (real04 ext_7: the cut wall beside the driveway read as a saw-tooth): a cut piece's top follows
        # the ground from one end to the other (its ends' ground + 0.1, never under the level + lip)
        if rise > tol and floor is None:
            ends = tuple(round(max(z + lip, gz(*q) + 0.1), 4) for q in (p0, p1))
        else:
            ends = (round(z1, 4), round(z1, 4))
        out.append({"p0": p0, "p1": p1, "zs": zs, "drop": round(drop, 4), "rise": round(rise, 4), "z0": round(z0, 4),
                    "z1": round(z1, 4), "z1_ends": ends, "height_m": round(max(z, max(zs)) - min(z, min(zs)), 3),
                    "to_band": floor is not None, "piece": j})
    return out


def platform_wall_max(pf: dict, gz) -> float:
    """The tallest retaining wall face a platform record builds (pure; round 3): the ``wall_pieces`` of every edge
    that is not a band's inner edge, with the first band's level on a stepped edge (``edge_floor``). Sloped
    platforms build no wall."""
    return round(max(platform_wall_edges(pf, gz).values() or [0.0]), 3)


def platform_wall_edges(pf: dict, gz) -> dict[int, float]:
    """``{edge index: the tallest wall face on it}`` of a platform record (pure): the ``wall_pieces`` of every edge
    that is not a band's inner edge or an edge facing the building (``against_edges``), with the first band's level
    on a stepped edge (``edge_floor``); edges without a wall are left out. Sloped platforms build no wall."""
    if pf.get("sloped"):
        return {}
    poly = geom2d.ccw(pf["polygon"])
    n = len(poly)
    z = float(pf["z"])
    floors = pf.get("edge_floor") or {}
    shared = set(pf.get("shared_edges") or []) | set(pf.get("against_edges") or [])
    out: dict[int, float] = {}
    for i in range(n):
        if i in shared:
            continue
        floor = float(floors[str(i)]) if str(i) in floors else None
        for piece in wall_pieces(poly[i], poly[(i + 1) % n], z, gz, floor):
            out[i] = round(max(out.get(i, 0.0), piece["height_m"]), 3)
    return out


def slab_with_holes(outer, holes, z_top: float, z_bottom: float) -> tuple[list, list]:
    """A closed slab (pure): the region ``outer`` minus ``holes`` as top and bottom faces with vertical sides along
    every loop (the hole sides face into the hole)."""
    outer = geom2d.ccw(outer)
    hs = [geom2d.ccw(h) for h in holes if len(h) >= 3]
    top_planes = [(0.0, 0.0, z_top)]
    bottom_planes = [(0.0, 0.0, z_bottom)]
    vt, ft = geom2d.polygon_faces(outer, hs, z_top, facing_up=True)
    vb, fb = geom2d.polygon_faces(outer, hs, z_bottom, facing_up=False)
    parts = [(vt, ft), (vb, fb)]
    loops = [outer] + [list(reversed(h)) for h in hs]
    for loop in loops:
        quads = geom2d.side_faces(loop, top_planes, bottom_planes)
        if quads:
            verts, faces = [], []
            for q in quads:
                base = len(verts)
                verts += [tuple(v) for v in q]
                faces.append([base + i for i in range(len(q))])
            parts.append((verts, faces))
    return geom2d.merge(parts)


def railing_runs(a, b, i: int, pf: dict) -> list[tuple]:
    """The stretches of a platform's railing on edge ``i`` (pure): the whole edge, or (25 Oct 2026, architect A2: a
    railing closed real04's pool-deck steps) the two pieces beside the flight when the edge is in ``railing_gaps``."""
    if i not in (pf.get("railing_gaps") or []) or i != pf.get("steps_edge"):
        return [(a, b)]
    from wenart.blender.architect import STEP_GAP_M
    length = G.distance(a, b)
    if length <= 1e-6:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    half = PLATFORM["step_width"] / 2.0 + STEP_GAP_M
    t0, t1 = length / 2.0 - half, length / 2.0 + half
    out = []
    if t0 > 0.2:
        out.append((a, (a[0] + ux * t0, a[1] + uy * t0)))
    if length - t1 > 0.2:
        out.append(((a[0] + ux * t1, a[1] + uy * t1), b))
    return out


def up_flight(pf: dict, terrain: Optional[dict] = None, gz=None) -> Optional[dict]:
    """The flight of steps up out of a sunken platform (``steps_dir: up``; pure, 25 Oct 2026): from the middle of its
    steps edge out into the slope until the treads reach the ground. ``{"edge", "mid", "out", "count", "rise",
    "length", "half_w", "footprint", "landing"}``: ``footprint`` is the flight with its cheek walls (a hole in the
    ground), ``landing`` the ground point past its top step. None for any other platform."""
    i = pf.get("steps_edge")
    poly = pf.get("polygon") or []
    if pf.get("steps_dir") != "up" or i is None or len(poly) < 3 or pf.get("sloped"):
        return None
    if gz is None:
        if terrain is None:
            return None
        gz = lambda x, y: ground_z(terrain, x, y)          # noqa: E731
    a, b = poly[i], poly[(i + 1) % len(poly)]
    length = G.distance(a, b)
    if length <= 1e-6:
        return None
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    out = (uy, -ux)                                          # counter-clockwise: the right side is outside
    mid = G.segment_midpoint(a, b)
    z, tread = float(pf["z"]), PLATFORM["step_tread"]
    count = 1
    for _ in range(4):                                       # the ground rises further out: settle the count
        d = count * tread
        g = gz(mid[0] + out[0] * d, mid[1] + out[1] * d)
        count = max(1, min(12, int(math.ceil((g - z) / PLATFORM["step_rise"] - 1e-9))))
    d = count * tread
    rise = max(PLATFORM["level_tol"], gz(mid[0] + out[0] * d, mid[1] + out[1] * d) - z)
    half_w = PLATFORM["step_width"] / 2.0
    t = PLATFORM["wall_t"]
    return {"edge": i, "mid": mid, "out": out, "count": count, "rise": round(rise, 3), "length": round(d, 3),
            "half_w": half_w, "footprint": _rect_along(mid, out, 0.0, d, half_w + t),
            "landing": (mid[0] + out[0] * (d + 0.6), mid[1] + out[1] * (d + 0.6)), "span": (length / 2.0 - half_w - t,
                                                                                            length / 2.0 + half_w + t)}


def up_flight_parts(fl: dict, z: float, gz) -> tuple[list, list]:
    """``(steps, cheeks)`` meshes of an up flight (pure): ``count`` treads rising from the platform to the ground and
    a cheek wall on each side holding the slope back, its top 0.1 m over the ground."""
    mid, out, n, tread = fl["mid"], fl["out"], fl["count"], PLATFORM["step_tread"]
    r = fl["rise"] / n
    below, t = PLATFORM["below"], PLATFORM["wall_t"]
    steps = [geom2d.prism(_rect_along(mid, out, (j - 1) * tread, j * tread, fl["half_w"]), z - below, z + j * r)
             for j in range(1, n + 1)]
    cheeks = []
    side = (-out[1], out[0])
    angle = math.degrees(math.atan2(out[1], out[0]))
    for sgn in (-1.0, 1.0):
        off = sgn * (fl["half_w"] + t / 2.0)
        p0 = (mid[0] + side[0] * off, mid[1] + side[1] * off)
        p1 = (p0[0] + out[0] * fl["length"], p0[1] + out[1] * fl["length"])
        c = G.segment_midpoint(p0, p1)
        cheeks.append(sloped_box(c, fl["length"], t, angle, z - below, max(z + 0.05, gz(*p0) + 0.1),
                                 max(z + fl["rise"] + 0.05, gz(*p1) + 0.1)))
    return steps, cheeks


def platform_parts(pf: dict, terrain: dict) -> list[dict]:
    """The meshes of one platform (pure): ``[{"part": slab | wall | kerb | steps | railing, "verts", "faces"}]``.
    The slab is a closed block from ``PLATFORM["below"]`` under its lowest ground (or ``bottom_z``: a band's slab
    reaches down to its parent's level) to ``z`` (its holes are the pools); a retaining wall skin (``wall_t``) stands
    outside every edge where the ground lies more than ``level_tol`` under the level (fill) or over it (cut: the wall
    holds the slope back up to the ground), with a ``lip`` over the slab; on an edge with a stepped band
    (``edge_floor``, round 3) the wall ends at the band's level, so it is never taller than ``RETAINING_MAX_M``; a
    band's ``shared_edges`` (its inner edge) get no wall, kerb or steps; kerbs along the edges of a parking, a path
    or a sloped area; the flight of steps on ``steps_edge`` down to the ground (or the band); a railing (rail and
    panel, ``shell.railing_parts``) on the ``railing_edges`` of a terrace or pool deck that is not a band. The
    ``wall`` part carries ``walls``: ``[{edge, height_m, z0, z1}]`` (the visible height over the floor)."""
    from wenart.blender import details as D

    poly = geom2d.ccw(pf["polygon"])
    z = float(pf["z"])
    out = []
    n = len(poly)
    floors = {int(k): float(v) for k, v in (pf.get("edge_floor") or {}).items()}
    # a band's inner edge (the parent is there) and an edge facing the building (its wall retains there; review of
    # round 3) get no wall, kerb, steps or railing
    shared = set(pf.get("shared_edges") or []) | set(pf.get("against_edges") or [])
    if pf.get("sloped"):
        v, f = draped_faces(poly, pf.get("holes") or [], terrain, lift=PAVING_LIFT)
        out.append({"part": "slab", "verts": v, "faces": f})
    else:
        zmin = min(ground_z(terrain, x, y) for x, y in poly)
        bottom = min(z, zmin) - PLATFORM["below"]
        if pf.get("bottom_z") is not None:
            bottom = min(bottom, float(pf["bottom_z"]))
        v, f = slab_with_holes(poly, pf.get("holes") or [], z, bottom)
        out.append({"part": "slab", "verts": v, "faces": f})
    tol = PLATFORM["level_tol"]
    walls, kerbs, steps, rails, panels, wall_recs = [], [], [], [], [], []
    flight = up_flight(pf, terrain)
    if flight is not None and flight["edge"] not in shared:
        st, ch = up_flight_parts(flight, z, lambda x, y: ground_z(terrain, x, y))
        steps += st
        walls += ch
    for i in range(n):
        if i in shared:
            continue
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        if length < 0.05:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = uy, -ux                                        # ccw: the right side of the edge is outside
        mid = G.segment_midpoint(a, b)
        angle = G.segment_angle_deg(a, b)
        if not pf.get("sloped"):
            # the wall in pieces that follow the ground (wall_pieces); pieces overlap by the thickness, every
            # second one 2 mm thicker (no coplanar faces); an up flight's edge has a gap for the flight
            gzf = lambda x, y: ground_z(terrain, x, y)          # noqa: E731
            if flight is not None and i == flight["edge"]:
                s0, s1 = flight["span"]
                pieces = [dict(pc, piece=pc["piece"] + 100 * k) for k, (q0, q1) in
                          enumerate(((a, G.point_along_segment(a, b, max(0.0, s0) / length)),
                                     (G.point_along_segment(a, b, min(length, s1) / length), b)))
                          for pc in wall_pieces(q0, q1, z, gzf, floors.get(i))]
            else:
                pieces = wall_pieces(a, b, z, gzf, floors.get(i))
            t = PLATFORM["wall_t"]
            for piece in pieces:
                pm = G.segment_midpoint(piece["p0"], piece["p1"])
                reach = G.distance(piece["p0"], piece["p1"]) + t
                c = (pm[0] + nx * (t / 2.0 + 0.001), pm[1] + ny * (t / 2.0 + 0.001))
                walls.append(sloped_box(c, reach, t + 0.002 * (piece["piece"] % 2), angle, piece["z0"],
                                        *piece.get("z1_ends", (piece["z1"], piece["z1"]))))
                wall_recs.append({"edge": i, "piece": piece["piece"], "height_m": piece["height_m"], "z0": piece["z0"],
                                  "z1": piece["z1"], "to_band": piece["to_band"]})
                if piece["rise"] > GUARD_RISE_M and not piece["to_band"]:
                    # 25 Oct 2026: the ground over a wall taller than the cap (no band fits there, e.g. a driveway
                    # beside a sunken pool deck) is a fall into the deck: a guard on the wall top
                    off = t / 2.0
                    ga = (piece["p0"][0] + nx * off, piece["p0"][1] + ny * off)
                    gb = (piece["p1"][0] + nx * off, piece["p1"][1] + ny * off)
                    rl, pn, po = guard_parts(ga, gb, *piece["z1_ends"])
                    rails += rl + po
                    panels += pn
                    wall_recs[-1]["guard"] = True
        if pf.get("edge") == "kerb" or pf.get("kind") in ("parking", "path"):
            kh, kw = PLATFORM["kerb_h"], PLATFORM["kerb_w"]
            if pf.get("sloped"):
                k = max(1, int(math.ceil(length / PLOT_WALL_STEP_M)))
                for j in range(k):
                    p0, p1 = G.point_along_segment(a, b, j / k), G.point_along_segment(a, b, (j + 1) / k)
                    m2 = G.segment_midpoint(p0, p1)
                    # review of round 3 (P1 real04 ext_5: the parking's kerb pieces floated as bars over the slope):
                    # each piece reaches down to 2 cm under the lowest ground of its footprint (the piece's ends
                    # with the kw/2 overlap, on both faces), its top kh over the highest
                    ends = [(p0[0] - ux * kw / 2.0, p0[1] - uy * kw / 2.0), (p1[0] + ux * kw / 2.0, p1[1] + uy * kw / 2.0)]
                    g_end = [[ground_z(terrain, q[0] + nx * off, q[1] + ny * off) for off in (0.0, kw)] for q in ends]
                    g = [ground_z(terrain, *m2)] + g_end[0] + g_end[1]
                    # 25 Oct 2026 (real04 ext_7: the kerb pieces read as teeth): the top follows the slope
                    zb = min(g) - 0.02
                    kerbs.append(sloped_box((m2[0] + nx * kw / 2.0, m2[1] + ny * kw / 2.0), G.distance(p0, p1) + kw,
                                            kw, angle, zb, max(g_end[0]) + PAVING_LIFT + kh,
                                            max(g_end[1]) + PAVING_LIFT + kh))
            else:
                kerbs.append(geom2d.box((mid[0] + nx * kw / 2.0, mid[1] + ny * kw / 2.0, z + kh / 2.0 - 0.02),
                                        (length + kw, kw, kh + 0.04), angle))
        if i in (pf.get("railing_edges") or []) and pf.get("kind") in ("terrace", "pool") and not pf.get("parent"):
            for ra, rb in railing_runs(a, b, i, pf):
                metal, panes = D.balustrade(ra, rb, z, 1.0, pf.get("balustrade") or D.DEFAULT_KIND)
                rails += metal
                panels += panes
    if pf.get("steps_edge") is not None and not pf.get("sloped") and pf["steps_edge"] not in shared \
            and pf.get("steps_dir") != "up":
        i = pf["steps_edge"]
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = uy, -ux
        mid = G.segment_midpoint(a, b)
        half_w = PLATFORM["step_width"] / 2.0
        gz_edge = floors[i] if i in floors else min(ground_z(terrain, *q) for q in _edge_samples([a, b], 4)[0])
        drop = z - gz_edge
        count = max(1, int(math.ceil(drop / PLATFORM["step_rise"] - 1e-9)))
        r = drop / count
        for j in range(1, count + 1):
            d0 = (j - 1) * PLATFORM["step_tread"]
            top = z - j * r
            block = _rect_along(mid, (nx, ny), d0, d0 + PLATFORM["step_tread"], half_w)
            zb = (floors[i] if i in floors else min(ground_z(terrain, *q) for q in block)) - PLATFORM["below"]
            if top > zb:
                steps.append(geom2d.prism(block, zb, top))
    for part, meshes in (("wall", walls), ("kerb", kerbs), ("steps", steps), ("railing", rails + panels)):
        if meshes:
            v, f = geom2d.merge(meshes)
            rec = {"part": part, "verts": v, "faces": f}
            if part == "railing":
                # The rails and posts in metal (slot 0), the panels in glass (slot 1): one material made real04's
                # terrace guard a solid steel slab beside the basement (24 Oct 2026).
                rec["slots"] = [0] * sum(len(m[1]) for m in rails) + [1] * sum(len(m[1]) for m in panels)
            if part == "wall":
                rec["walls"] = wall_recs
            out.append(rec)
    return out


def backdrop_faces(inner: Sequence[Sequence[float]], terrain: dict, outer_reach: float = 1800.0,
                   rise: float = 25.0) -> tuple[list, list]:
    """The rising ground ring beyond ``inner`` (the rectangle where the ground or its skirt ends; pure, Milestone 13
    T6): its inner edge at the ground's level there, its outer edge ``outer_reach`` further out and ``rise`` higher,
    so a soft hill line stands at the horizon within the cameras' clip distance (a flat ground to 1000 m still left
    a black band between its edge and the sky's horizon). Quads face up."""
    x0, y0 = min(p[0] for p in inner), min(p[1] for p in inner)
    x1, y1 = max(p[0] for p in inner), max(p[1] for p in inner)
    X0, Y0, X1, Y1 = x0 - outer_reach, y0 - outer_reach, x1 + outer_reach, y1 + outer_reach
    verts: list = []
    faces: list = []

    def v(x: float, y: float, dz: float) -> int:
        verts.append((x, y, ground_z(terrain, x, y) + dz))
        return len(verts) - 1

    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    outers = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    for k in range(4):
        a, b = corners[k], corners[(k + 1) % 4]
        oa, ob = outers[k], outers[(k + 1) % 4]
        ia, ib = v(*a, 0.0), v(*b, 0.0)
        ja, jb = v(*oa, rise), v(*ob, rise)
        quad = (ia, ja, jb, ib)
        area = sum(verts[quad[i]][0] * verts[quad[(i + 1) % 4]][1] - verts[quad[(i + 1) % 4]][0] * verts[quad[i]][1]
                   for i in range(4))
        faces.append(quad if area > 0 else tuple(reversed(quad)))
    return verts, faces


HAZE = {"reach_m": 1200.0, "below_m": 50.0, "above_m": 250.0, "hole_above_m": 80.0, "hole_below_m": 5.0,
        "density": 0.0009, "anisotropy": 0.3, "colour": (0.78, 0.84, 0.92)}
# Fix round part 3 (17 Oct 2026): the haze object's reserved pass index (Blender's ``Object.pass_index`` maximum; the
# build's indices count up from 1), recorded in its manifest entry. Cycles writes the haze shell into the depth and
# index passes on a random half of the rays that cross it (bpy 5.2.2: real02's terrace and ext_2 at 16 and 128 spp),
# so ``render.sky_mask`` reads a hit with this index and no normal behind it as sky; the render keeps the index out of
# its helper maps and its pass index table (the haze is no object in view).
HAZE_PASS_INDEX = 32767


def haze_box(near: Sequence[Sequence[float]], z_range: tuple[float, float], cfg: Optional[dict] = None
             ) -> tuple[list, list]:
    """A closed hollow box (pure; Milestone 13 T6): the haze volume around the site, an outer box ``reach_m`` beyond
    the near ground rectangle and an inner hole over the near rectangle itself (the building, its plot and the
    cameras stand in clear air; the far ground, the backdrop and the horizon are seen through the haze). The outer
    shell faces out, the inner shell faces in (Cycles treats the space between them as the volume); a World
    volume would switch the sun and the sky off (the 5.2 manual)."""
    c = dict(HAZE, **(cfg or {}))
    x0, y0 = min(p[0] for p in near), min(p[1] for p in near)
    x1, y1 = max(p[0] for p in near), max(p[1] for p in near)
    zb, zt = float(z_range[0]), float(z_range[1])
    outer = geom2d.box(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (zb - c["below_m"] + zt + c["above_m"]) / 2.0),
                       (x1 - x0 + 2 * c["reach_m"], y1 - y0 + 2 * c["reach_m"], zt + c["above_m"] - zb + c["below_m"]))
    inner = geom2d.box(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (zb - c["hole_below_m"] + zt + c["hole_above_m"]) / 2.0),
                       (x1 - x0, y1 - y0, zt + c["hole_above_m"] - zb + c["hole_below_m"]))
    iv, if_ = inner
    return geom2d.merge([outer, (iv, [list(reversed(f)) for f in if_])])


POOL_WATER_BOTTOM_M = 0.02                   # the water slab starts this far above the basin floor


def pool_parts(pool: dict, terrain: dict, deck_z: Optional[float] = None) -> dict:
    """A pool (pure): its edge at ``deck_z`` (the platform's level; else the highest ground of its corners), the
    basin clipped under the edge (walls inward, floor) down to ``depth``, the water as a closed slab from
    ``POOL_WATER_BOTTOM_M`` over the floor up to ``POOL_WATER_DROP_M`` under the edge (a volume: absorption needs a
    closed mesh), and a coping ring ``POOL_COPING_M`` wide standing ``lip`` over the deck with a 3 cm overhang over
    the water. ``{"basin": (verts, faces), "water", "coping", "edge_z", "floor_z", "water_z", "coping_z"}``."""
    poly = geom2d.ccw([(float(p[0]), float(p[1])) for p in pool["polygon"]])
    edge = float(deck_z) if deck_z is not None else max(ground_z(terrain, x, y) for x, y in poly)
    floor = edge - float(pool.get("depth") or POOL_DEPTH_M)
    inner = geom2d.offset_polygon(poly, 0.01)                      # 1 cm inside the slab's hole: no coplanar faces
    inner = inner if len(inner) >= 3 else poly
    n = len(inner)
    verts = [(x, y, floor) for x, y in inner] + [(x, y, edge) for x, y in inner]
    faces = [tuple(range(n))]                                    # floor (ccw seen from above: up)
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, n + i, n + j, j))                     # inward-facing walls of a ccw outline
    water_z = edge - POOL_WATER_DROP_M
    wv, wf = geom2d.prism(inner, floor + POOL_WATER_BOTTOM_M, water_z)
    lip = PLATFORM["lip"]
    coping_z = edge + lip
    ring_out = geom2d.offset_polygon(poly, -POOL_COPING_M)
    ring_in = geom2d.offset_polygon(poly, 0.03)
    coping = slab_with_holes(ring_out, [ring_in], coping_z, edge - 0.02) if len(ring_out) >= 3 and len(ring_in) >= 3 \
        else ([], [])
    return {"basin": (verts, faces), "water": (wv, wf), "coping": coping, "edge_z": edge, "floor_z": floor,
            "water_z": water_z, "coping_z": coping_z, "coping_width": POOL_COPING_M}


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


POOL_DEPTH_M = 1.5
POOL_WATER_DROP_M = 0.12                     # the water stands this far under the pool's edge


def pool_materials(ripples: bool = True):
    """The pool's tiles and water (bpy; procedural, no texture: assumed looks). Milestone 13 (T6): the tiles are a
    light mosaic with a grout grid (Brick texture), the water a Principled glass (transmission 1, IOR 1.33) with
    ripples from a Wave texture through a Bump node and Volume Absorption in the water slab (the 5.2 manual:
    ``Volume Absorption`` for water and coloured glass, its ``Density`` input); ``ripples`` False keeps the
    Milestone 12 flat water (the ``pools`` lever off)."""
    import bpy

    def principled(name, colour, roughness, transmission=0.0, ior=1.45):
        mat = bpy.data.materials.get(name)
        if mat is not None:
            return mat
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
            bsdf.inputs["Roughness"].default_value = roughness
            for key in ("Transmission Weight", "Transmission"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = transmission
                    break
            if "IOR" in bsdf.inputs:
                bsdf.inputs["IOR"].default_value = ior
        return mat

    tiles = principled("pool_tiles", (0.62, 0.80, 0.86), 0.25)
    if ripples and "pool_tiles_grid" not in tiles:
        tree = tiles.node_tree
        bsdf = tree.nodes.get("Principled BSDF")
        if bsdf is not None and "Brick Texture" not in tree.nodes:
            coord = tree.nodes.new("ShaderNodeTexCoord")
            brick = tree.nodes.new("ShaderNodeTexBrick")
            brick.inputs["Scale"].default_value = 20.0                     # 5 cm mosaic tiles
            brick.inputs["Mortar Size"].default_value = 0.04
            brick.inputs["Color1"].default_value = (0.62, 0.80, 0.86, 1.0)
            brick.inputs["Color2"].default_value = (0.52, 0.74, 0.84, 1.0)
            brick.inputs["Mortar"].default_value = (0.85, 0.87, 0.88, 1.0)
            tree.links.new(coord.outputs["Object"], brick.inputs["Vector"])
            tree.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
            bump = tree.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.3
            tree.links.new(brick.outputs["Fac"], bump.inputs["Height"])
            tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
            if "Coat Weight" in bsdf.inputs:
                bsdf.inputs["Coat Weight"].default_value = 0.5                # glazed tiles
            tiles["pool_tiles_grid"] = True
    water = principled("pool_water", (0.55, 0.85, 0.90), 0.02, transmission=1.0, ior=1.33)
    if ripples and "pool_water_ripples" not in water:
        tree = water.node_tree
        bsdf = tree.nodes.get("Principled BSDF")
        out = next((n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial"), None)
        if bsdf is not None and out is not None:
            bsdf.inputs["Base Color"].default_value = (0.9, 0.97, 1.0, 1.0)
            coord = tree.nodes.new("ShaderNodeTexCoord")
            wave = tree.nodes.new("ShaderNodeTexWave")
            wave.inputs["Scale"].default_value = 1.5
            wave.inputs["Distortion"].default_value = 6.0
            wave.inputs["Detail"].default_value = 3.0
            wave.inputs["Detail Scale"].default_value = 2.0
            tree.links.new(coord.outputs["Object"], wave.inputs["Vector"])
            noise = tree.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 3.0
            noise.inputs["Detail"].default_value = 4.0
            tree.links.new(coord.outputs["Object"], noise.inputs["Vector"])
            mix = tree.nodes.new("ShaderNodeMix")
            mix.data_type = "FLOAT"
            mix.inputs["Factor"].default_value = 0.5
            tree.links.new(wave.outputs["Fac"], mix.inputs[2])
            tree.links.new(noise.outputs["Fac"], mix.inputs[3])
            bump = tree.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.08
            bump.inputs["Distance"].default_value = 0.02
            tree.links.new(mix.outputs[0], bump.inputs["Height"])
            tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
            absorb = tree.nodes.new("ShaderNodeVolumeAbsorption")
            absorb.inputs["Color"].default_value = (0.45, 0.8, 0.85, 1.0)
            absorb.inputs["Density"].default_value = 0.6
            tree.links.new(absorb.outputs["Volume"], out.inputs["Volume"])
            water["pool_water_ripples"] = True
    return tiles, water


def haze_material():
    """The haze volume's material (bpy; Milestone 13 T6): Volume Scatter (``Density`` ``HAZE["density"]`` per
    metre, ``Anisotropy`` forward) on the material's Volume output, no surface (a transparent surface so the shell
    itself is invisible); the 5.2 manual's Volume Scatter node (fog) and ``volume_step_rate`` of the material."""
    import bpy

    mat = bpy.data.materials.get("site_haze")
    if mat is not None:
        return mat
    mat = bpy.data.materials.new("site_haze")
    mat.use_nodes = True
    tree = mat.node_tree
    for n in list(tree.nodes):
        tree.nodes.remove(n)
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    clear = tree.nodes.new("ShaderNodeBsdfTransparent")
    tree.links.new(clear.outputs["BSDF"], out.inputs["Surface"])
    scatter = tree.nodes.new("ShaderNodeVolumeScatter")
    scatter.inputs["Color"].default_value = (*HAZE["colour"], 1.0)
    scatter.inputs["Density"].default_value = HAZE["density"]
    scatter.inputs["Anisotropy"].default_value = HAZE["anisotropy"]
    tree.links.new(scatter.outputs["Volume"], out.inputs["Volume"])
    if hasattr(mat, "cycles") and hasattr(mat.cycles, "volume_step_rate"):
        mat.cycles.volume_step_rate = 4.0                       # a thin, even fog needs few steps
    mat["wenart_haze"] = True
    return mat


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
    the inferred trees join ``trees``; every inferred item is in ``assumed``.

    Milestone 13 (T6): ``climate`` (``climate_of``), ``levers`` (``site_levers``), ``hedges`` (``hedges_of``: the
    symbols of a hedge leave ``trees``), ``platforms`` (``platforms``: an area with a platform carries its
    ``platform_id`` and is not draped), the pools with their deck level (``deck_z``), ``near_extent`` (the ground
    rectangle around the building and the plot: the clear-air hole of the haze and the near-camera grass) and
    ``species`` (tree id -> species, size class, inferred)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    climate = climate_of(building)
    levers = site_levers()
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
        warnings += inferred["warnings"]           # fix round after P4b: fewer inferred trees than asked
        for p in inferred["paths"]:
            areas.append({"id": f"path_{'_'.join(p['opening_ids'])}", "kind": "path", "polygon": p["polygon"],
                          "z": None, "material": None, "colour": None, "source": "assumed", "area_id": None,
                          "lift": PAVING_LIFT, "inferred": True})
        for t in inferred["trees"]:
            trees.append(t)
            assumed.append({"field": f"tree:{t['id']}", "value": t["center"], "reason": t["reason"]})
    # 11 Oct 2026 (real04): the other buildings on the plot (the ground has a hole for each) and the drawn pools.
    from wenart.blender import copies as CP
    copy_holes = [geom2d.ccw(fp) for fp in CP.footprints(building)]
    pools = []
    if mode == "full":
        for k, pool in enumerate(_built(site.get("pools"))):
            poly = geom2d.ccw(pool.get("polygon") or [])
            if len(poly) >= 3:
                depth = float(((pool.get("depth") or {}).get("value")) or POOL_DEPTH_M)
                pools.append({"id": str(pool.get("id") or f"pool_{k + 1:03d}"), "polygon": poly, "depth": depth,
                              "evidence": pool.get("evidence") or [], "deck_z": None})
                if ((pool.get("depth") or {}).get("method")) in (None, "assumed"):
                    assumed.append({"field": f"pool:{pools[-1]['id']}:depth", "value": depth,
                                    "reason": "no pool section drawn: the depth is assumed"})
    # Milestone 13 (T6): hedges (rows of tree symbols), platforms (one level per terrace / pool / parking), species.
    hedges: list[dict] = []
    pfs: list[dict] = []
    species: dict = {}
    if mode == "full":
        hedges, taken = hedges_of(building, climate["climate"], detect=levers["hedge"])
        if taken:
            trees = [t for t in trees if str(t.get("id")) not in taken]
        for h in hedges:
            assumed.append({"field": f"hedge:{h['id']}", "value": [h["height_m"], h["species"]],
                            "reason": h["reason"] + f"; species {h['species']} "
                                      f"({'inferred' if h.get('species_inferred') else 'named'})"})
        if levers["platforms"]:
            pfs = platforms(site, terrain, keep_out=[geom2d.ccw(outline)] + copy_holes,
                            facades=facade_openings(building, levels, outline, outlines),
                            band_keep=hedge_keep_out(hedges))
            wells, gone = wells_on_platforms(wells, pfs)
            for w in gone:
                assumed[:] = [a for a in assumed if a.get("field") != f"light_well:{w['opening_id']}"]
                assumed.append({"field": f"light_well:{w['opening_id']}", "value": None, "reason": w["dropped_reason"]})
            by_pool = {pid: pf for pf in pfs for pid in pf["pools"]}
            for pool in pools:
                if pool["id"] in by_pool:
                    pool["deck_z"] = by_pool[pool["id"]]["z"]
                    pool["platform_id"] = by_pool[pool["id"]]["id"]
            by_area = {pf["id"]: pf for pf in pfs}
            for a in areas:
                if a.get("id") in by_area:
                    a["platform_id"] = a["id"]
            for pf in pfs:
                assumed.append({"field": f"platform:{pf['id']}", "value": pf["z"], "reason": pf["reason"]})
        if hedges:                                   # fix round after P3: every hull on its planting side
            hedges, fit_assumed = fit_hedges(hedges, pfs, [geom2d.ccw(outline)] + copy_holes)
            assumed += fit_assumed
        for t in trees:
            parts = tree_parts(t, terrain, climate["climate"])
            species[str(t.get("id"))] = {"species": parts["species"], "size_class": parts["size_class"],
                                        "height_m": parts["height"], "inferred": parts["species_inferred"]}
    if climate.get("inferred"):
        assumed.append({"field": "climate", "value": climate["climate"], "reason": f"{climate['source']} "
                        f"(inferred; the species of trees and hedges follow it): {', '.join(climate['evidence'])}"})
    near_extent = ground_extent(outline, plot, MARGIN_M)
    return {"mode": mode, "terrain": terrain, "outline": geom2d.ccw(outline), "plot": plot, "plot_source": plot_src,
            "extent": extent, "wells": wells, "plot_walls": plot_walls, "areas": areas, "trees": trees,
            "not_built": not_built, "assumed": assumed, "warnings": warnings, "ground_is_grass": ground_is_grass,
            "inferred": inferred, "copy_holes": copy_holes, "pools": pools, "hedges": hedges, "platforms": pfs,
            "climate": climate, "levers": levers, "near_extent": near_extent, "species": species}


# The look of each built area kind (exterior.resolve_looks slots) when the area names no material of its own.
AREA_LOOKS = {"grass": "garden", "paving": "paving", "parking": "paving", "path": "paving"}


def area_look(area: dict, looks: dict) -> dict:
    """The look of a built site area (pure): its own drawn ``material`` / ``colour`` (documents), else the
    resolved look of its kind (``AREA_LOOKS``)."""
    if area.get("material"):
        return {"material": area["material"], "colour": area.get("colour"), "source": "documents",
                "assumed": False, "reason": f"site {area['kind']} {area.get('id')}: drawn material"}
    return looks[AREA_LOOKS.get(area["kind"], "paving")]


# Milestone 13 (T6): the object kinds of the new site parts. ``common.KINDS`` (the closed list of object kinds) and
# ``schemas.WHOLE_BUILDING_KINDS`` (the scene-manifest schema's kinds) both list them since round 2; until both do,
# a part takes the nearest Milestone 10-12 kind (``site_kind``) and says its own in ``site_part``, so a built manifest
# always validates.
SITE_KINDS = {"platform": ("site_platform", "site_area"), "hedge": ("site_hedge", "site_boundary"),
              "grass": ("site_grass", "site_decor"), "haze": ("atmosphere", "site_decor"), "backdrop": ("terrain", "terrain")}


def site_kind(part: str) -> str:
    """The manifest kind of a Milestone 13 site part: its own name when ``common.KINDS`` and the scene-manifest
    schema (``schemas.WHOLE_BUILDING_KINDS``) both know it, else the fallback (``SITE_KINDS``)."""
    from wenart.blender import common, schemas

    own, fallback = SITE_KINDS[part]
    return own if own in common.KINDS and own in schemas.WHOLE_BUILDING_KINDS else fallback


PLATFORM_LOOKS = {"slab": {"terrace": "paving", "pool": "paving", "parking": "paving", "path": "paving"},
                  "wall": ("concrete_exposed", None, "retaining wall: exposed concrete (not drawn)"),
                  "kerb": ("concrete_exposed", None, "kerb: concrete (not drawn)"),
                  "steps": None, "railing": None}
# Fix round after P3 (16-17 Oct 2026). What: the slugs the site builder puts on by itself when no look names one: the
# railing and the fence of the inferred boundary, the neutral concrete of a retaining wall whose concrete_exposed
# resolved to the facade material. Why: P3's real04 retaining, terrace and pool walls were flat boxes (concrete_exposed
# names Poly Haven concrete_wall_001, which the assets stage never fetched: the style names none of these). How:
# exterior.build_finish_slugs lists these with PLATFORM_LOOKS, so wenart.assets.fetch fetches their texture sets and
# build.referenced_asset_ids follows them; build_site reads the slugs from here.
SITE_FALLBACK_LOOKS = {"railing": "painted_metal_white", "fence": "wood_cladding", "retaining": "concrete"}


def terrain_record(terrain: dict) -> dict:
    """The scene manifest's terrain block of a terrain model (pure; round 3): a ``terrain_model`` result carries
    ``kind``, ``z``, ``sides``, the north and ``changes``; a bare record (``{kind, z}`` of a test or a caller, or a
    planar / tin record with its ``surface`` and no ``sides``) gets empty ``sides`` and ``changes`` and no north,
    never a KeyError (pod P1: tests/gpu/test_m13_site.py::test_hedge_tree_sources_and_pool_in_blender raised
    ``KeyError: 'sides'`` in ``build_site``)."""
    zs = terrain.get("z") if isinstance(terrain.get("z"), dict) else {}
    return {"kind": terrain.get("kind") or "flat", "z": {k: round(float(v), 4) for k, v in zs.items()},
            "sides": list(terrain.get("sides") or []), "north_deg": terrain.get("north_deg"),
            "north_source": terrain.get("north_source"), "changes": list(terrain.get("changes") or [])}


# Fix round part 2 (17 Oct 2026; review of part 1). What: the lawn relief (``vegetation.lawn_relief``, down only since
# part 1) leaves the ground at its level under and around everything that stands on the terrain: ``relief_keep``
# lists those footprints for ``build_site`` (the ground's holes, the draped areas, the sloped platforms, the inferred
# entrance steps, every tree, shrub and hedge). Why: measured in the bpy 5.2.2 module on a sloped synthetic site, the
# relief lowered the lawn 1.8 cm on average (up to 3.4 cm) under the draped path and parking, which kept their level
# (2.1 cm mean gap with no edge under them), and under the shrubs and trees (bases 2.6-2.8 cm in the air). How: pure
# polygons (trees as ``disc_polygon``); ``vegetation.relief_weights`` keeps every ground vertex within
# ``vegetation.relief_reach`` of one level (the margin plus a ground cell's diagonal); the grass surface gets the same
# polygons and reach on the ground's grid, and the relief only where the ground got one.
RELIEF_KEEP_TREE_BASE_M = 0.75      # a tree's footprint for the relief: the trunk with its root flare (assumed)
RELIEF_KEEP_DISC_SIDES = 12


def disc_polygon(center: Sequence[float], radius: float, sides: int = RELIEF_KEEP_DISC_SIDES
                 ) -> list[tuple[float, float]]:
    """A regular polygon around the circle of ``radius`` at ``center`` (pure; its edges touch the circle), ccw."""
    n = max(3, int(sides))
    r = max(0.0, float(radius)) / math.cos(math.pi / n)
    cx, cy = float(center[0]), float(center[1])
    return [(cx + r * math.cos(2.0 * math.pi * k / n), cy + r * math.sin(2.0 * math.pi * k / n)) for k in range(n)]


def ground_holes(plan: dict) -> list:
    """The holes of the ground mesh (pure; ``build_site``): the building's outline, the light wells, the other
    buildings (``copy_holes``), the pools no platform holds and every platform with a flat slab."""
    pfs = list(plan.get("platforms") or [])
    pooled = {pid for pf in pfs for pid in pf.get("pools") or []}
    return [plan["outline"]] + [w["polygon"] for w in plan.get("wells") or []] + list(plan.get("copy_holes") or []) \
        + [p["polygon"] for p in plan.get("pools") or [] if p["id"] not in pooled] \
        + [pf["polygon"] for pf in pfs if not pf.get("sloped")] \
        + [fl["footprint"] for fl in (up_flight(pf, plan.get("terrain")) for pf in pfs) if fl is not None]


def hedge_records(plan: dict, levers: Optional[dict] = None) -> list[dict]:
    """The hedges ``build_site`` builds (pure): the plan's hedge rows (``hedges_of`` fitted by ``fit_hedges``) and,
    with the ``hedge`` lever and an inferred site, a low hedge on every inferred boundary segment of kind ``hedge``
    (Milestone 11 E11, Milestone 13 T6)."""
    levers = levers if levers is not None else (plan.get("levers") or site_levers())
    out = list(plan.get("hedges") or [])
    inferred = plan.get("inferred")
    if inferred and levers.get("hedge"):
        segs = [seg for seg in inferred["boundary"] if seg["kind"] == "hedge"]
        for k, seg in enumerate(segs):
            out.append({"id": f"boundary_hedge_{k + 1:02d}", "polyline": [list(seg["start"]), list(seg["end"])],
                        "width_m": INFERRED["hedge_thickness"], "height_m": INFERRED["hedge_height"],
                        "height_class": "low", "species": species_for("low", (plan.get("climate") or {}).get(
                            "climate", "temperate"), kind="hedge"), "species_inferred": True, "inferred": True,
                        "evidence": [], "source": "inferred_boundary", "symbol_ids": [],
                        "reason": "no site plan: a low hedge on the inferred plot boundary (inferred)"})
    return out


def _hedge_footprints(hedge: dict) -> list[list[tuple[float, float]]]:
    """One rectangle per polyline segment of a hedge: half its width to each side, half its width past each end
    (``hedge_parts`` overlaps its steps by the width)."""
    pts = [(float(x), float(y)) for x, y in hedge.get("polyline") or []]
    hw = float(hedge.get("width_m") or 0.0) / 2.0
    out = []
    for a, b in zip(pts, pts[1:]):
        length = G.distance(a, b)
        if length < 0.05:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -uy * hw, ux * hw
        a0, b0 = (a[0] - ux * hw, a[1] - uy * hw), (b[0] + ux * hw, b[1] + uy * hw)
        out.append(geom2d.ccw([(a0[0] - nx, a0[1] - ny), (b0[0] - nx, b0[1] - ny), (b0[0] + nx, b0[1] + ny),
                               (a0[0] + nx, a0[1] + ny)]))
    return out


def relief_keep(plan: dict, hedges: Optional[Sequence[dict]] = None) -> list[dict]:
    """The places the lawn relief leaves at the ground's level (pure; fix round part 2, 17 Oct 2026):
    ``[{"kind", "id", "polygon"}]`` of kind ``hole`` (``ground_holes``), ``area`` (the draped areas: paths, paving,
    parking and grass without a platform), ``sloped_platform``, ``steps`` (the inferred entrance steps' landings,
    flights, cheek walls and ramps), ``shrub`` (a shrub's or bush's drawn crown), ``tree`` (``RELIEF_KEEP_TREE_BASE_M``
    around the trunk) and ``hedge`` (``_hedge_footprints``). ``hedges``: the hedges ``build_site`` builds (default
    ``hedge_records``)."""
    out: list[dict] = []
    for k, hole in enumerate(ground_holes(plan)):
        out.append({"kind": "hole", "id": f"hole_{k}", "polygon": [tuple(map(float, q[:2])) for q in hole]})
    for a in plan.get("areas") or []:
        if not a.get("platform_id") and len(a.get("polygon") or []) >= 3:
            out.append({"kind": "area", "id": a.get("id"), "polygon": [tuple(map(float, q[:2])) for q in a["polygon"]]})
    for pf in plan.get("platforms") or []:
        if pf.get("sloped") and len(pf.get("polygon") or []) >= 3:
            out.append({"kind": "sloped_platform", "id": pf.get("id"),
                        "polygon": [tuple(map(float, q[:2])) for q in pf["polygon"]]})
    for st in (plan.get("inferred") or {}).get("steps") or []:
        polys = [b["polygon"] for b in list(st.get("blocks") or []) + list(st.get("cheeks") or [])]
        if st.get("ramp"):
            polys.append(st["ramp"]["polygon"])
        for poly in polys:
            if len(poly) >= 3:
                out.append({"kind": "steps", "id": st.get("opening_id"),
                            "polygon": [tuple(map(float, q[:2])) for q in poly]})
    for item in plan.get("trees") or []:
        size = [float(v) for v in (item.get("size") or [1.0, 1.0])[:2]]
        dia = max(0.3, max(size))
        _h, cls = tree_height(dia / 2.0)
        shrub = item.get("kind") == "plant" or cls == "shrub"
        radius = dia / 2.0 if shrub else RELIEF_KEEP_TREE_BASE_M
        out.append({"kind": "shrub" if shrub else "tree", "id": item.get("id"),
                    "polygon": disc_polygon(item["center"], radius)})
    for h in hedge_records(plan) if hedges is None else hedges:
        for poly in _hedge_footprints(h):
            out.append({"kind": "hedge", "id": h.get("id"), "polygon": poly})
    return out


def build_site(plan: dict, collection, looks: dict, make_material, manifest_objects: list, assumed: list,
               glass=None) -> dict:
    """The site objects of ``site_plan``: the ground (kind ``terrain``), ``lightwell_<opening>`` (kind
    ``light_well``), the plot walls (``site_wall``, their ids), the areas (``site_area``, their ids) and
    ``tree_<id>`` (``site_decor``). ``looks``: the resolved looks (``exterior.resolve_looks``: ``garden``, ``paving``,
    ``plot_wall``, ``light_well``, ``bark``, ``foliage``, ``ground``); ``make_material(look)`` gives the Blender
    material. Returns the summary for the scene manifest (with the build's terrain changes for basement doors and
    the light wells).

    Milestone 13 (T6, under the ``levers`` of the plan): ``ground_backdrop`` (kind ``terrain``: the rising ring
    to the horizon) and ``haze`` (kind ``atmosphere``: the closed hollow volume) with the ``sky`` lever;
    ``platform_<id>_<part>`` (kind ``site_platform``: slab, wall, kerb, steps, railing) with ``platforms``;
    ``<pool>_basin`` / ``_water`` / ``_coping`` (kind ``site_pool``; the coping and the rippled, absorbing water
    with ``pools``); ``hedge_<id>`` (kind ``site_hedge``: the leaf-card hedge of ``vegetation.hedge_object``, its
    box core when the vegetation module cannot build it) with ``hedge``, the inferred boundary hedge the same way;
    every tree through ``vegetation.tree_object`` (a Poly Haven instance near the cameras with ``instances``, a
    Sapling tree with ``sapling``, else the leaf-card tree; never the Milestone 12 ellipsoid) and the near-camera
    grass (``vegetation.grass_patch``) with ``instances``. Every object's manifest entry says which source built it
    (``veg_method``, ``asset``, ``licence``) and the species (``inferred``)."""
    from wenart.blender import common
    from wenart.blender import vegetation as VG

    terrain = plan["terrain"]
    levers = plan.get("levers") or site_levers()
    pfs = [pf for pf in plan.get("platforms") or []]
    holes = ground_holes(plan)
    # the hedges (drawn rows and the inferred boundary) before the ground: the lawn relief keeps their footprints
    hedge_recs = hedge_records(plan, levers)
    summary = {"built": True, "mode": plan["mode"], "objects": [],
               "reason": f"brief site: {plan['mode']} (docs/milestone10.md §3.2 item 5)",
               "terrain": terrain_record(terrain),
        "light_wells": [{"opening_id": w["opening_id"], "level_id": w["level_id"], "source": w["source"],
                         "floor_z": round(w["floor_z"], 4), "top_z": round(w["top_z"], 4), "reason": w["reason"],
                         **({"kind": w["kind"], "inferred": True, "opening_ids": w["opening_ids"]}
                            if w.get("kind") == "front_court" else {})}
                        for w in plan["wells"]],
        "plot_source": plan["plot_source"], "not_built": plan["not_built"], "warnings": plan["warnings"],
        "levers": dict(levers), "climate": plan.get("climate"), "hedges": [], "platforms": [], "vegetation": []}

    def entry(name, wid, kind, mat, status, extra):
        manifest_objects.append({"name": name, "wenart_id": wid, "kind": kind, "status": status, "level_id": None,
                                 "element_id": wid, "evidence": [], "material": mat.name if mat else None,
                                 "textured": False, "pass_index": None, **extra})
        summary["objects"].append(name)

    ground_look = looks["garden"] if plan["ground_is_grass"] or plan["mode"] == "full" else looks["ground"]
    ground_mat = make_material(ground_look)
    lawn = None
    if ground_look is looks["garden"]:
        # round 3 (P1: the lawn rendered as a flat saturated green): tiling at 1-2 m, an albedo variation, a bump
        try:
            lawn = VG.lawn_material(ground_mat)
        except Exception as exc:  # noqa: BLE001 - the ground keeps its plain material; the reason is recorded
            lawn = {"applied": False, "reason": f"{type(exc).__name__}: {exc}"}
    verts, faces = draped_faces(plan["extent"], holes, terrain)
    ob = common.new_mesh_object("ground", verts, faces, collection=collection, wenart_id="ground", kind="terrain",
                                status="assumed", materials=[ground_mat])
    zs = [v[2] for v in verts] or [0.0]
    entry(ob.name, "ground", "terrain", ground_mat, "assumed",
          {"assumed": {"extent": [list(p) for p in plan["extent"]], "terrain": terrain.get("kind"),
                       "reason": "ground plane around the building (the levels per side as drawn, the rest assumed)"},
           "z_range": [round(min(zs), 4), round(max(zs), 4)], "look_source": ground_look.get("source"),
           "lawn": lawn})
    summary["lawn"] = lawn
    keep: list = []
    if levers.get("instances") and plan["mode"] == "full":
        # the far lawn: a gentle displacement (no blades); down only, its edges kept; fix round part 2: level under
        # and around everything that stands on the terrain (relief_keep)
        keep = relief_keep(plan, hedge_recs)
        rec = VG.lawn_relief(ob, keep=[k["polygon"] for k in keep], reach=VG.relief_reach(grid_step(plan["extent"])))
        kinds: dict = {}
        for k in keep:
            kinds[k["kind"]] = kinds.get(k["kind"], 0) + 1
        summary["lawn_relief"] = dict(rec or {}, range_m=list(VG.relief_range()), edges_kept=True, keep=kinds)
    outer_rect = list(plan["extent"])
    if not is_flat(terrain):                     # 11 Oct 2026 (real04): a sloped ground reaches the horizon too
        sv, sf = skirt_faces(plan["extent"], terrain)
        ob = common.new_mesh_object("ground_skirt", sv, sf, collection=collection, wenart_id="ground_skirt",
                                    kind="terrain", status="assumed", materials=[ground_mat])
        entry(ob.name, "ground_skirt", "terrain", ground_mat, "assumed",
              {"assumed": {"reason": "the ground beyond the sloped ground's rectangle to the horizon, at the ground's "
                                     "level there"}, "look_source": ground_look.get("source")})
        x0, y0 = min(p[0] for p in plan["extent"]), min(p[1] for p in plan["extent"])
        x1, y1 = max(p[0] for p in plan["extent"]), max(p[1] for p in plan["extent"])
        outer_rect = [(x0 - HORIZON_M, y0 - HORIZON_M), (x1 + HORIZON_M, y0 - HORIZON_M),
                      (x1 + HORIZON_M, y1 + HORIZON_M), (x0 - HORIZON_M, y1 + HORIZON_M)]
    if levers.get("sky"):
        bv, bf = backdrop_faces(outer_rect, terrain)
        ob = common.new_mesh_object("ground_backdrop", bv, bf, collection=collection, wenart_id="ground_backdrop",
                                    kind="terrain", status="assumed", materials=[ground_mat])
        entry(ob.name, "ground_backdrop", "terrain", ground_mat, "assumed",
              {"assumed": {"reason": "a rising ground ring to the clip distance: a soft hill line at the horizon "
                                     "(inferred; no context drawn)"}, "inferred": True,
               "look_source": ground_look.get("source")})
        near = plan.get("near_extent") or plan["extent"]
        z_lo = min(ground_z(terrain, x, y) for x, y in near)
        z_hi = max(ground_z(terrain, x, y) for x, y in near) + 15.0
        hv, hf = haze_box(near, (z_lo, z_hi))
        haze_mat = haze_material()
        ob = common.new_mesh_object("haze", hv, hf, collection=collection, wenart_id="haze", kind=site_kind("haze"),
                                    status="assumed", materials=[haze_mat])
        ob.display_type = "WIRE"
        ob.visible_shadow = False
        ob.pass_index = HAZE_PASS_INDEX              # fix round part 3: the render's sky mask knows the shell by it
        entry(ob.name, "haze", site_kind("haze"), haze_mat, "assumed",
              {"site_part": "haze", "pass_index": HAZE_PASS_INDEX,       # fix round part 3: the reserved index
               "assumed": {"reason": "distance haze: a closed hollow mesh volume (Volume Scatter) beyond the near "
                                     "ground, not a World volume (that disables the sun and the sky)",
                           "density_per_m": HAZE["density"]}, "inferred": True})
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
        if area.get("platform_id"):
            continue                                  # Milestone 13: built as a platform below
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
    # Milestone 13 (T6): the platforms (one level each with retaining walls, kerbs, steps and railings)
    if pfs:
        # Round 3 (P1 'platforms' row): retaining walls and kerbs are a neutral concrete (PLATFORM_LOOKS), the steps
        # the style's exterior steps or paving; never the facade material (the facade look is checked by name).
        facade_name = getattr(make_material(looks["facade"]), "name", None) if looks.get("facade") else None
        concrete = make_material({"material": PLATFORM_LOOKS["wall"][0], "colour": None, "source": "build",
                                  "assumed": True, "reason": PLATFORM_LOOKS["wall"][2]})
        if facade_name and getattr(concrete, "name", None) == facade_name:
            concrete = make_material({"material": SITE_FALLBACK_LOOKS["retaining"], "colour": "grey", "source": "build",
                                      "assumed": True,
                                      "reason": "retaining wall: neutral concrete (the vocabulary slug resolved to "
                                                "the facade material)"})
        step_mat = make_material(looks.get("steps") or looks["paving"])
        rail_mat = make_material(looks.get("railing") or {"material": SITE_FALLBACK_LOOKS["railing"], "colour": None})
        for pf in pfs:
            # 25 Oct 2026 (real04 ext_7: the stepped bands read as paved concrete boxes): a stepped band is a planted
            # terrace of the garden, its top the garden's look
            slab_area = {"kind": "grass" if pf.get("parent") else
                         "paving" if pf["kind"] in ("terrace", "pool", "path") else "parking",
                         "id": pf["id"], "material": None if pf.get("parent") else pf.get("material"),
                         "colour": None if pf.get("parent") else pf.get("colour")}
            slab_look = area_look(slab_area, looks)
            mats = {"slab": make_material(slab_look), "wall": concrete, "kerb": concrete, "steps": step_mat,
                    "railing": rail_mat}
            parts = platform_parts(dict(pf, balustrade=plan.get("balustrade")) if plan.get("balustrade") else pf,
                                   terrain)
            wall_part = next((q for q in parts if q["part"] == "wall"), None)
            built_walls = (wall_part or {}).get("walls") or []
            wall_max = max([w["height_m"] for w in built_walls] or [0.0])
            for part in parts:
                name = f"platform_{pf['id']}_{part['part']}"
                mat = mats[part["part"]]
                slots = part.get("slots") if glass is not None else None
                ob = common.new_mesh_object(name, part["verts"], part["faces"], collection=collection, wenart_id=name,
                                            kind=site_kind("platform"), status="assumed",
                                            materials=[mat, glass] if slots else [mat],
                                            face_material_indices=slots)
                zz = [v[2] for v in part["verts"]] or [pf["z"]]
                entry(ob.name, name, site_kind("platform"), mat, "assumed",
                      {"site_part": "platform", "parent": pf["id"], "platform_kind": pf["kind"], "part": part["part"], "level_z": pf["z"],
                       "edge": pf["edge"], "inferred": True, "z_range": [round(min(zz), 4), round(max(zz), 4)],
                       "assumed": {"reason": pf["reason"]}, "area_id": pf.get("area_id"),
                       "ground_z": pf.get("ground"), "step": pf.get("step"), "platform_parent": pf.get("parent"),
                       **({"walls": part["walls"]} if part["part"] == "wall" else {}),
                       "slug": slab_look.get("material") if part["part"] == "slab" else mats[part["part"]].name})
            summary["platforms"].append({"id": pf["id"], "kind": pf["kind"], "z": pf["z"], "edge": pf["edge"],
                                         "z_source": pf["z_source"], "marks": pf["marks"], "sloped": pf["sloped"],
                                         "parts": [q["part"] for q in parts], "pools": pf["pools"],
                                         "drop_m": pf["drop_m"], "rise_m": pf["rise_m"],
                                         # round 3: the terrain under it, the stepped terraces, the tallest wall built
                                         "ground_z": pf.get("ground"), "parent": pf.get("parent"), "step": pf.get("step"),
                                         "stepped": pf.get("stepped") or [], "edge_floor": pf.get("edge_floor") or {},
                                         # review of round 3: the edges facing the building (no wall, no band), the
                                         # bands that had no room and the walls left over the cap there
                                         "against_edges": pf.get("against_edges") or [],
                                         "band_blocked": pf.get("band_blocked") or [],
                                         "cap_exceeded": pf.get("cap_exceeded") or [],
                                         "wall_max_m": round(wall_max, 3), "retaining_cap_m": RETAINING_MAX_M,
                                         "walls": built_walls,
                                         "materials": {k: getattr(m, "name", None) for k, m in mats.items()
                                                       if k in {q["part"] for q in parts}}})
            # pre-flight of pod P3 (16 Oct 2026): the scene manifest schema needs ``parent`` with ``kind``
            # (schemas.ASSUMED_ENTRY); without it the 28 real04 platforms made validate_scene_manifest fail
            assumed.append({"object": f"platform_{pf['id']}", "field": "level", "value": pf["z"],
                            "reason": pf["reason"], "parent": str(pf["id"]), "kind": "site_platform"})
    # 24 Oct 2026 (user request: "start using the new library items for the outside items, plants cars etc"): parked
    # library cars on the drawn parkings
    summary["cars"] = build_cars(plan, collection, manifest_objects, assumed, glass)
    summary["objects"] += [c["name"] for c in summary["cars"]]
    if plan.get("pools"):                           # 11 Oct 2026 (real04): the drawn pools; Milestone 13: coping, water
        tile, water = pool_materials(ripples=bool(levers.get("pools")))
        for pool in plan["pools"]:
            parts = pool_parts(pool, terrain, deck_z=pool.get("deck_z"))
            built = [("basin", tile, "basin"), ("water", water, "water")]
            if levers.get("pools") and parts["coping"][1]:
                built.append(("coping", step_mat if pfs else make_material(looks["paving"]), "coping"))
            for part, mat, suffix in built:
                v, f = parts[part]
                name = f"{pool['id']}_{suffix}"
                ob = common.new_mesh_object(name, v, f, collection=collection, wenart_id=pool["id"], kind="site_pool",
                                            status="verified", materials=[mat])
                entry(ob.name, pool["id"], "site_pool", mat, "verified",
                      {"evidence": pool.get("evidence") or [], "part": suffix,
                       "z_range": [round(parts["floor_z"], 4), round(parts["coping_z"] if suffix == "coping"
                                                                     else parts["edge_z"], 4)],
                       "deck_z": pool.get("deck_z"), "platform": pool.get("platform_id"),
                       "assumed": {"depth": pool["depth"], "reason": "no pool section drawn"
                                   + ("; coping, tiles and rippled water assumed" if levers.get("pools") else "")}})
    # Milestone 13 (T6): hedges (drawn rows and the inferred boundary: hedge_records above) and the trees through the
    # vegetation module
    inferred = plan.get("inferred")
    foliage_mat = make_material(looks["foliage"]) if hedge_recs or plan["trees"] else None
    # fix round after P3: hedges, trees and shrubs stand on the surface under them (a terrace's level, not the
    # terrain under the terrace: P3 buried real04's terrace hedges and the shrubs of the stepped bands)
    stand = stand_terrain(terrain, pfs)
    for h in hedge_recs:
        v, f, info = hedge_parts(h, stand)
        if not f:
            continue
        name = f"hedge_{h['id']}" if not h["id"].startswith(("hedge_", "boundary_")) else h["id"]
        ob, rec = None, None
        if levers.get("hedge"):
            try:
                ob, rec = VG.hedge_object(dict(h, core_verts=v, core_faces=f, ground_z=info["z_range"][0]),
                                          collection=collection, name=name)
            except Exception as exc:                 # the box core stands in; the reason is in the manifest
                rec = {"method": "box", "error": f"{type(exc).__name__}: {exc}"}
                ob = None
        if ob is None:
            ob = common.new_mesh_object(name, v, f, collection=collection, wenart_id=name, kind=site_kind("hedge"),
                                        status="assumed", materials=[foliage_mat])
            rec = dict(rec or {}, method=(rec or {}).get("method", "box"))
        entry(ob.name, name, site_kind("hedge"), foliage_mat if rec.get("method") == "box" else None, "assumed",
              {"site_part": "hedge", "evidence": h.get("evidence") or [], "inferred": True, "height_m": h["height_m"],
               "width_m": h["width_m"], "length_m": info["length_m"], "height_class": h["height_class"],
               "species": h["species"], "species_inferred": h.get("species_inferred", True),
               "symbol_ids": h.get("symbol_ids") or [], "source": h.get("source"), "veg_method": rec.get("method"),
               # round 2: the leaf atlas the hedge really used (``vegetation.hedge_object`` records it as ``atlas``)
               # and its licence, so ``wenart.run.copy.vegetation_credits`` credits that one
               "asset": rec.get("asset") or rec.get("atlas"), "licence": rec.get("licence"),
               "cards": rec.get("cards"), "material": rec.get("material") or (foliage_mat.name if foliage_mat else None),
               # round 3: the density, card size and cover behind the card count, the hull core
               "cards_per_m2": rec.get("density"), "card_m": rec.get("card_m"), "cover_layers": rec.get("cover_layers"),
               "core": info.get("core"), "top_round_m": info.get("top_round_m"),
               "z_range": info["z_range"], "assumed": {"reason": h["reason"], **({"error": rec["error"]}
                                                                                   if rec.get("error") else {})}})
        summary["hedges"].append({"id": name, "length_m": info["length_m"], "height_m": h["height_m"],
                                  "species": h["species"], "method": rec.get("method"), "symbols": len(h.get("symbol_ids") or []),
                                  "cards": rec.get("cards"), "cards_per_m2": rec.get("density"),
                                  "card_m": rec.get("card_m"), "cover_layers": rec.get("cover_layers"),
                                  "atlas": rec.get("atlas"), "core": info.get("core"),
                                  # fix round after P3: the hull kept on its planting side (fit_hedges), the level
                                  # it stands on (stand_terrain)
                                  "fit": {k: v for k, v in (h.get("fit") or {}).items() if k != "polyline_drawn"}
                                  or None, "z_range": info["z_range"]})
        # pre-flight of pod P3: ``parent`` with ``kind`` (schemas.ASSUMED_ENTRY), as the trees below
        assumed.append({"object": name, "field": "hedge", "value": [h["height_m"], h["species"]], "reason": h["reason"],
                        "parent": str(h["id"]), "kind": "site_hedge"})
    climate = (plan.get("climate") or {}).get("climate", "temperate")
    bark = make_material(looks["bark"]) if plan["trees"] else None
    near_pts = plan.get("near_extent") or plan["extent"]
    for k, item in enumerate(plan["trees"]):
        parts = tree_parts(item, stand, climate)
        wid = f"tree_{item.get('id') or len(summary['objects'])}"
        cx, cy = float(item["center"][0]), float(item["center"][1])
        near = geom2d.distance_to_polygon_edges((cx, cy), plan["outline"]) <= VG.NEAR_CAMERA_M \
            or G.point_in_polygon((cx, cy), plan["outline"])
        ob, rec = None, None
        try:
            ob, rec = VG.tree_object(parts["species"], parts["height"], k, bool(near), collection=collection,
                                     name=wid, position=(cx, cy, parts["ground_z"]), levers=levers,
                                     crown_m=parts["diameter"])
        except Exception as exc:
            rec = {"method": "proxy", "error": f"{type(exc).__name__}: {exc}"}
            ob = None
        if ob is None:                               # the low-poly proxy only when the vegetation module failed
            meshes = [m for m in (parts["trunk"], parts["crown"]) if m is not None]
            v, f = geom2d.merge(meshes)
            slots = ([0] * len(parts["trunk"][1]) if parts["trunk"] else []) + [1] * len(parts["crown"][1])
            ob = common.new_mesh_object(wid, v, f, collection=collection, wenart_id=wid, kind="site_decor",
                                        status="assumed", materials=[bark, foliage_mat], face_material_indices=slots)
        entry(ob.name, wid, "site_decor", None, "assumed",
              {"evidence": item.get("evidence") or [], "parent": item.get("id"), "site_kind": item.get("kind"),
               "species": parts["species"], "species_inferred": parts["species_inferred"],
               "size_class": parts["size_class"], "height_m": parts["height"], "crown_m": parts["diameter"],
               # ``asset``: the Poly Haven model of an instance, else the leaf atlas of a card or Sapling tree
               # (recorded as ``atlas``; round 2, for ``copy.vegetation_credits``); None for a palm or a proxy
               "near_camera": bool(near), "veg_method": rec.get("method"),
               "asset": rec.get("asset") or rec.get("atlas"),
               "licence": rec.get("licence"), "material": rec.get("material"), "inferred": True,
               # round 3: a Sapling tree's leaf faces (never 0: 0 falls back to the leaf-card crown with the reason)
               "leaf_faces": rec.get("leaf_faces"), "cards": rec.get("cards"),
               "fallback_from": rec.get("fallback_from"), "fallback_reason": rec.get("fallback_reason"),
               "assumed": {"height_m": parts["height"], "reason": parts["reason"],
                           **({"error": rec["error"]} if rec.get("error") else {}),
                           **({"fallback": f"{rec['fallback_from']}: {rec.get('fallback_reason')}"}
                              if rec.get("fallback_from") else {})}})
        summary["vegetation"].append({"id": wid, "kind": "tree", "species": parts["species"],
                                      "size_class": parts["size_class"], "height_m": parts["height"],
                                      "method": rec.get("method"), "asset": rec.get("asset"),
                                      "near_camera": bool(near), "leaf_faces": rec.get("leaf_faces"),
                                      "cards": rec.get("cards"), "atlas": rec.get("atlas"),
                                      # pre-flight of P3: the reason travels with the fallback (vegetation.missing_source)
                                      "fallback_from": rec.get("fallback_from"),
                                      "fallback_reason": rec.get("fallback_reason")})
        assumed.append({"object": wid, "field": "tree", "value": parts["height"], "reason": parts["reason"],
                        "parent": str(item.get("id")), "kind": "site_tree"})
    if plan["mode"] == "full" and levers.get("instances"):
        lawn = plan["plot"] if len(plan["plot"]) >= 3 else geom2d.offset_polygon(plan["outline"], -8.0)
        lawn_holes = holes + [pf["polygon"] for pf in pfs if pf.get("sloped")] \
            + [a["polygon"] for a in plan["areas"] if not a.get("platform_id")]
        # fix round part 2 (17 Oct 2026): the clumps' surface gets the relief only when the ground got one (a flat
        # ground of convex pieces gets none: its clumps sank 2 cm into the lawn), with the ground's keep polygons and
        # on the ground's grid, so the clumps follow the lawn under them
        ground_relief = summary.get("lawn_relief") or {}
        relief_on = bool(ground_relief.get("weighted"))
        relief_reason = (f"the ground got the relief ({ground_relief.get('weighted')} vertices move): the clumps' "
                         f"surface follows it" if relief_on else
                         "the ground got no relief (no vertex away from its edges and the keep polygons: a flat ground "
                         "of convex pieces): the clumps' surface keeps the ground's level")
        try:
            gob, grec = VG.grass_patch(lawn, VG.GRASS_DENSITY_NEAR, collection=collection, terrain=terrain,
                                       holes=lawn_holes, name="grass_near", relief=relief_on,
                                       keep=[k["polygon"] for k in keep], step=grid_step(plan["extent"]),
                                       reach=VG.relief_reach(grid_step(plan["extent"])))
        except Exception as exc:
            gob, grec = None, {"method": "none", "error": f"{type(exc).__name__}: {exc}"}
        grec = dict(grec, relief_requested=relief_on, relief_reason=relief_reason)
        if gob is not None:
            entry(gob.name, "grass_near", site_kind("grass"), None, "assumed",
                  {"site_part": "grass", "inferred": True, "veg_method": grec.get("method"), "asset": grec.get("asset"),
                   "licence": grec.get("licence"), "density_per_m2": grec.get("density"), "clumps": grec.get("count"),
                   "assumed": {"reason": "lawn near the cameras: scattered grass clumps over the grass texture "
                                         "(inferred; no planting drawn)"}})
        summary["grass"] = grec
    if inferred:                                     # Milestone 11 E11: steps and the fence (inferred)
        step_mat = make_material(looks.get("steps") or looks["paving"]) if inferred["steps"] else None
        rail_mat = make_material(looks.get("railing") or {"material": SITE_FALLBACK_LOOKS["railing"],
                                                          "colour": None}) \
            if any(st.get("rails") for st in inferred["steps"]) else None
        for st in inferred["steps"]:
            # Milestone 12: landing, flights, cheek walls, a ramp and handrails (entrance_meshes); one object each.
            for mesh in entrance_meshes(st, terrain):
                wid = mesh["name"]
                mat = rail_mat if mesh["kind"] == "site_handrail" else step_mat
                ob = common.new_mesh_object(wid, mesh["verts"], mesh["faces"], collection=collection, wenart_id=wid,
                                            kind=mesh["kind"], status="assumed", materials=[mat])
                entry(ob.name, wid, mesh["kind"], mat, "assumed",
                      {"parent": st["opening_id"], "inferred": True, "entrance": st["opening_id"],
                       "assumed": {"steps": st["count"], "risers": st.get("risers"), "rise_m": st["rise"],
                                   "solution": st.get("solution"), "reason": "entrance above the ground: a landing "
                                                                             "and steps (inferred)"}})
        kinds = sorted({seg["kind"] for seg in inferred["boundary"]})
        for kind in kinds:
            if kind == "hedge" and levers.get("hedge"):
                continue                              # built above as leaf-card hedges
            segs = [seg for seg in inferred["boundary"] if seg["kind"] == kind]
            look = looks.get(kind) or (looks["foliage"] if kind == "hedge"
                                       else {"material": SITE_FALLBACK_LOOKS["fence"], "colour": None})
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
            "steps": [{"opening_id": s["opening_id"], "count": s["count"], "rise": s["rise"],
                       "solution": s.get("solution"), "risers": s.get("risers"),
                       "intermediate_landings": s.get("intermediate_landings"), "ramp": bool(s.get("ramp")),
                       "handrails": bool(s.get("rails"))} for s in inferred["steps"]],
            "paths": [{"opening_ids": p["opening_ids"], "length": p["length"], "width": p["width"]}
                      for p in inferred["paths"]],
            "boundary": kinds[0] if kinds else None, "trees": [t["id"] for t in inferred["trees"]],
            # fix round after P4b (17 Oct 2026): how the trees were placed (place_trees' stats), never a silent 0
            "tree_stats": inferred.get("tree_stats"),
            "trees_relaxed": [t["id"] for t in inferred["trees"] if t.get("relaxed")]}
    for a in plan["assumed"]:
        assumed.append({"object": "site", "field": a["field"], "value": a["value"], "reason": a["reason"]})
    summary["vegetation_counts"] = vegetation_counts(summary)       # Milestone 13 (T8 metric 11): per source
    return summary


# --------------------------------------------------------------------------
# Milestone 13: the vegetation records of the scene manifest, the instances of the 3D export, the building's
def parkings(plan: dict) -> list[dict]:
    """The parkings of a site plan (pure): ``[{"id", "polygon", "z"}]`` from the parking platforms (``z`` None for a
    sloped one: draped on the terrain) and the parking areas that are no platform (``z`` None: on the terrain)."""
    out = []
    for pf in plan.get("platforms") or []:
        if pf.get("kind") == "parking" and len(pf.get("polygon") or []) >= 3:
            flat = not pf.get("sloped") and isinstance(pf.get("z"), (int, float))
            out.append({"id": str(pf["id"]), "polygon": pf["polygon"], "z": float(pf["z"]) if flat else None})
    for area in plan.get("areas") or []:
        if area.get("kind") == "parking" and not area.get("platform_id") and len(area.get("polygon") or []) >= 3:
            z = area.get("z") if isinstance(area.get("z"), (int, float)) else None
            out.append({"id": str(area.get("id")), "polygon": area["polygon"], "z": z})
    return out


CAR_MAX_SLOPE = 0.2            # a bay steeper than 20 % (a steep driveway) gets no car
CAR_LIFT_M = 0.02              # over a draped parking (its own lift)


def car_ground(plan: dict, lot: dict, slot: dict) -> Optional[tuple[float, float, float]]:
    """``(z at the bay centre, dz/dx, dz/dy)`` of a car's bay (pure): the lot's level when flat, else the terrain's
    plane through the bay's corners (None when steeper than ``CAR_MAX_SLOPE``)."""
    if lot.get("z") is not None:
        return float(lot["z"]), 0.0, 0.0
    t = plan["terrain"]
    x, y = slot["center"]
    r = 1.5
    gx = (ground_z(t, x + r, y) - ground_z(t, x - r, y)) / (2 * r)
    gy = (ground_z(t, x, y + r) - ground_z(t, x, y - r)) / (2 * r)
    if math.hypot(gx, gy) > CAR_MAX_SLOPE:
        return None
    return ground_z(t, x, y) + CAR_LIFT_M, gx, gy


def build_cars(plan: dict, collection, manifest_objects: list, assumed: list, glass=None) -> list[dict]:
    """Library cars parked on the drawn parkings (bpy; ``site_models.car_models`` / ``car_slots``): one model per
    bay, the models taken in turn, each scaled to ``CAR_WIDTH_M`` (kind ``site_decor``, ``inferred``). Off with
    ``WENART_SITE_LIBRARY=off``; [] without a parking, a usable car or its file."""
    import os

    from wenart.blender import furniture as F
    from wenart.blender import site_models as SM
    from wenart.blender import vegetation as VG

    if str(os.environ.get("WENART_SITE_LIBRARY") or "").strip().lower() in ("off", "0", "no", "false"):
        return []
    lots = parkings(plan)
    if not lots:
        return []
    VG.library_plant("olive")                       # loads the catalogue's extras once
    mode = str(os.environ.get("WENART_LICENCE_MODE") or "relaxed").strip().lower()
    folder = VG.assets_dir()
    cars = []
    for c in SM.car_models(VG._LIBRARY.get("extras") or [], mode):
        path, _why = F.resolve_asset(c["asset"], str(folder) if folder else None)
        if path is not None:
            cars.append((c, path))
    out: list[dict] = []
    cache: dict = {}
    k = 0
    for lot in lots:
        for i, slot in enumerate(SM.car_slots(lot["polygon"])):
            if not cars:
                return out
            c, path = cars[k % len(cars)]
            k += 1
            try:
                geo = F._cached_geometry(path, collection, cache)
            except Exception as exc:  # a broken file never stops the site
                print(f"car {c['asset']['asset_id']}: import failed ({exc})")
                continue
            if not geo.get("verts"):
                continue
            ground = car_ground(plan, lot, slot)
            if ground is None:
                continue
            z0, gx, gy = ground
            w, length, h = c["size"]
            verts, info = F.fit_vertices(geo["verts"], c["asset"], {"center": slot["center"], "size": [w, length],
                                                                     "rotation_deg": slot["rotation_deg"]},
                                         z0, target_size=[w, length, h])
            if gx or gy:                      # on a draped parking: the car follows the slope (a small shear)
                sx, sy = slot["center"]
                verts = [(x, y, z + gx * (x - sx) + gy * (y - sy)) for x, y, z in verts]
            name = f"car_{lot['id']}_{i}"
            ob = F._mesh_object(name, verts, geo["faces"], geo["materials"], geo["face_materials"], collection,
                                name, "site_decor", "assumed", uvs=geo.get("uvs"), uv_name=geo.get("uv_name"),
                                fallback_material=glass)
            reason = (f"library car {c['asset']['asset_id']} ({str(c['asset'].get('title') or '')[:30]!r}) on the "
                      f"drawn parking {lot['id']} ({slot['layout']} bay; the documents draw the parking, not a car)")
            rec = {"name": ob.name, "parking": lot["id"], "asset": c["asset"]["asset_id"],
                   "licence": c["asset"].get("licence"), "licence_flag": c["asset"].get("licence_flag"),
                   "attribution": c["asset"].get("attribution"), "layout": slot["layout"], "fit": info,
                   "inferred": True, "reason": reason}
            manifest_objects.append({"name": ob.name, "wenart_id": name, "kind": "site_decor", "status": "assumed",
                                     "level_id": None, "element_id": name, "evidence": [], "material": None,
                                     "textured": True, "pass_index": None, "site_part": "car", "veg_method": "library",
                                     "asset": c["asset"]["asset_id"], "licence": c["asset"].get("licence"),
                                     "inferred": True, "reason": reason,
                                     "assumed": {"detail": "car", "reason": reason}})
            assumed.append({"object": ob.name, "field": "car", "value": c["asset"]["asset_id"], "reason": reason,
                            "parent": lot["id"], "kind": "site_car"})
            out.append(rec)
    return out


# site.platforms (the pipeline_final hook)
# --------------------------------------------------------------------------

# The methods vegetation.tree_object / hedge_object / grass_patch record, grouped by source for the manifest's
# ``site.vegetation_counts`` (docs/milestone13.md §7 metric 11: trees as real geometry, never a primitive).
VEGETATION_SOURCES = {"library": ("library",), "polyhaven_instances": ("polyhaven",), "sapling": ("sapling",),
                      "leaf_card": ("cards", "palm"), "proxy": ("proxy", "none", "", None)}


def vegetation_counts(summary: dict) -> dict:
    """Per-source counts of what ``build_site`` built (pure; the scene manifest's ``site.vegetation_counts``):
    ``polyhaven_instances`` (collection instances of the CC0 hero models), ``sapling`` (Sapling Tree Gen trees),
    ``leaf_card`` (card trees and palms), ``proxy`` (the low-poly stand-in when the module failed), ``trees`` (all),
    ``hedges`` and ``hedges_leaf_card`` (the ``site.hedges`` built, those with leaf cards), ``grass_patches``
    (the near-camera lawn patch when it was built)."""
    trees = [r for r in summary.get("vegetation") or [] if isinstance(r, dict)]
    hedges = [r for r in summary.get("hedges") or [] if isinstance(r, dict)]
    grass = summary.get("grass") if isinstance(summary.get("grass"), dict) else None
    out = {key: sum(1 for r in trees if r.get("method") in methods) for key, methods in VEGETATION_SOURCES.items()}
    out["trees"] = len(trees)
    out["hedges"] = len(hedges)
    out["hedges_leaf_card"] = sum(1 for r in hedges if r.get("method") == "cards")
    built_grass = bool(grass) and grass.get("method") not in (None, "", "none") and not grass.get("error")
    out["grass_patches"] = 1 if built_grass else 0
    return out


# The polygon cap of ``realize_site_instances`` (env ``WENART_REALIZE_CAP``): the leaf cards of the hedges and card
# trees and the grass clumps are geometry-nodes instances; the glTF export writes an object's evaluated mesh only
# (export_apply), so the instances reach the .glb only when realized (or through the exporter's experimental
# Geometry Nodes Instances option, docs.blender.org/manual/en/5.2/addons/scene_gltf2.html). A cap keeps the .glb
# deliverable: 1 M polygons as the documented choice (the lead may change it after P3).
REALIZE_CAP_POLYS = 1_000_000
REALIZE_CAP_ENV = "WENART_REALIZE_CAP"
VEGETATION_GROUP_PREFIX = "veg_"                # vegetation.scatter_group names every vegetation node group so


def realize_cap(env: Optional[dict] = None) -> int:
    """The polygon cap (pure): ``WENART_REALIZE_CAP`` (a non-negative integer; 0 = realize nothing), else
    ``REALIZE_CAP_POLYS``."""
    import os
    text = str((os.environ if env is None else env).get(REALIZE_CAP_ENV) or "").strip()
    if text.isdigit():
        return int(text)
    return REALIZE_CAP_POLYS


def instance_budget(items: Sequence[dict], cap_polys: int) -> dict:
    """Which vegetation node groups the export realizes under the polygon cap (pure). ``items``: one per node
    group, ``{"group", "objects": [names], "instances": n, "polygons": the polygons of all its instances}``.
    The smallest groups first (the most vegetation reaches the .glb), each taken while the running total stays
    within ``cap_polys``; the rest stay instances (in the .blend, not in the .glb). Returns ``{"cap",
    "realize": [items], "skipped": [items with "reason"], "polygons": the realized total, "polygons_all"}``."""
    cap = max(0, int(cap_polys))
    realize, skipped, total = [], [], 0
    for item in sorted(items, key=lambda it: (int(it.get("polygons") or 0), str(it.get("group")))):
        polys = int(item.get("polygons") or 0)
        if total + polys <= cap:
            realize.append(dict(item))
            total += polys
        else:
            skipped.append(dict(item, reason=f"{polys} polygons would pass the cap of {cap} ({total} realized)"))
    return {"cap": cap, "realize": realize, "skipped": skipped, "polygons": total,
            "polygons_all": sum(int(it.get("polygons") or 0) for it in items)}


def vegetation_instance_items(depsgraph, objects) -> list[dict]:
    """The ``instance_budget`` items of the scene (bpy): for every object with a NODES modifier on a vegetation
    node group (``VEGETATION_GROUP_PREFIX``), the instances the depsgraph generates for it and their polygons
    (``DepsgraphObjectInstance``: ``is_instance``, ``parent``, ``object``), summed per node group (a group is
    shared by the hedges of one species: realizing it realizes every user)."""
    by_object: dict[str, list] = {}
    for ob in objects:
        for mod in ob.modifiers:
            ng = getattr(mod, "node_group", None) if mod.type == "NODES" else None
            if ng is not None and str(ng.name).startswith(VEGETATION_GROUP_PREFIX):
                by_object.setdefault(ob.name, []).append(ng.name)
    if not by_object:
        return []
    counts: dict[str, list] = {name: [0, 0] for name in by_object}
    for inst in depsgraph.object_instances:
        if not inst.is_instance or inst.parent is None:
            continue
        parent = inst.parent.original.name if hasattr(inst.parent, "original") else inst.parent.name
        if parent not in counts:
            continue
        data = getattr(inst.object, "data", None)
        polys = len(data.polygons) if data is not None and hasattr(data, "polygons") else 0
        counts[parent][0] += 1
        counts[parent][1] += polys
    items: dict[str, dict] = {}
    for ob_name, groups in by_object.items():
        for gname in groups:
            item = items.setdefault(gname, {"group": gname, "objects": [], "instances": 0, "polygons": 0})
            item["objects"].append(ob_name)
            item["instances"] += counts[ob_name][0]
            item["polygons"] += counts[ob_name][1]
    return [items[k] for k in sorted(items)]


def realize_node_group(ng) -> bool:
    """A Realize Instances node before the group output of a vegetation node group (bpy): the instances become
    mesh geometry for the export. Idempotent (``ng["wenart_realized"]``); False when the group has no linked
    output."""
    if ng.get("wenart_realized"):
        return True
    go = next((n for n in ng.nodes if n.type == "GROUP_OUTPUT"), None)
    if go is None or not go.inputs or not go.inputs[0].links:
        return False
    link = go.inputs[0].links[0]
    src = link.from_socket
    real = ng.nodes.new("GeometryNodeRealizeInstances")
    ng.links.remove(link)
    ng.links.new(src, real.inputs["Geometry"])
    ng.links.new(real.outputs["Geometry"], go.inputs[0])
    ng["wenart_realized"] = True
    return True


def realize_site_instances(cap_polys: Optional[int] = None, objects=None) -> dict:
    """Realize the vegetation instances for a glTF export (bpy; Milestone 13 T6, the 3D pack): the leaf cards of
    the hedges and card trees and the grass clumps are geometry-nodes instances that ``export_apply`` leaves out
    of the .glb; this adds a Realize Instances node to every vegetation node group that fits under the polygon
    cap (``instance_budget``, smallest first; ``cap_polys`` None = ``realize_cap()``). Call it after the .blend is
    saved (the renders keep the light instances) and before ``bpy.ops.export_scene.gltf``. The Poly Haven hero
    trees are collection instances, not geometry nodes: the cap does not apply to them. Returns the budget with
    ``realized`` (the group names changed), ``cap``, ``polygons`` and the skipped groups with their reasons."""
    import bpy
    cap = realize_cap() if cap_polys is None else int(cap_polys)
    objects = list(objects) if objects is not None else list(bpy.data.objects)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    items = vegetation_instance_items(depsgraph, objects)
    budget = instance_budget(items, cap)
    realized = []
    for item in budget["realize"]:
        ng = bpy.data.node_groups.get(item["group"])
        if ng is not None and realize_node_group(ng):
            realized.append(item["group"])
    if realized:
        bpy.context.view_layer.update()
    budget["realized"] = realized
    budget["groups"] = len(items)
    return budget


def building_keep_out(building: dict) -> list[list[tuple[float, float]]]:
    """The polygons no platform edge builds against and no stepped band enters (pure; review of round 3): the
    building's ground outline (the rule of ``build.ground_outline`` over each level's wall outline, as
    ``build.prepare`` cuts the ground: the largest outline of the levels at or below the highest drawn ground level
    + 0.5 m, else the lowest level's; restated here because site.py must not import build.py, the stage code lists
    of ``wenart.run.stages``) and the copies' footprints (``copies.footprints``, the ground holes of ``site_plan``)."""
    from wenart.blender import copies as CP

    outlines = {}
    for lv in building.get("levels") or []:
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lv.get("id")]
        if walls:
            outlines[lv["id"]] = geom2d.wall_outline(walls)[0]
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    zs = [((g.get("z") or {}).get("value")) for g in ((site.get("ground") or {}).get("levels") or [])
          if isinstance(g, dict)]
    top = max([float(z) for z in zs if z is not None] or [0.0])
    levels = sorted(building.get("levels") or [], key=lambda lv: float(lv["elevation"]))
    touching = [lv for lv in levels if float(lv["elevation"]) <= top + 0.5 and len(outlines.get(lv["id"]) or []) >= 3]
    if not touching:
        touching = [lv for lv in levels if len(outlines.get(lv["id"]) or []) >= 3][:1]
    ground = max((outlines[lv["id"]] for lv in touching), key=G.polygon_area) if touching else []
    return ([geom2d.ccw(ground)] if len(ground) >= 3 else []) + [geom2d.ccw(fp) for fp in CP.footprints(building)]


def platforms_into_building(building: dict) -> dict:
    """``site.platforms`` of the building JSON (pure; docs/milestone13.md §13.3, the hook after the levels stage):
    the records of ``platforms(site)`` on the site's own ground surface (the levels stage's model, as the build
    reads it without the door overrides) written into ``building["site"]["platforms"]`` (an earlier run's list is
    replaced; a site without terrace, pool or parking polygons gets ``[]``), with the building and its copies as the
    keep-out (``building_keep_out``, as ``site_plan`` passes them). Returns ``{"count", "ids", "kinds"}``;
    a building without a site dict is left alone (``count`` None)."""
    import json
    site = building.get("site") if isinstance(building.get("site"), dict) else None
    if site is None:
        return {"count": None, "ids": [], "kinds": {}}
    hedges = hedges_of(building, climate_of(building)["climate"], detect=site_levers()["hedge"])[0] \
        if site_levers()["platforms"] else []
    pfs = json.loads(json.dumps(platforms(site, keep_out=building_keep_out(building),
                                          facades=building_facades(building), band_keep=hedge_keep_out(hedges))))
    site["platforms"] = pfs
    kinds: dict[str, int] = {}
    for pf in pfs:
        kinds[pf["kind"]] = kinds.get(pf["kind"], 0) + 1
    return {"count": len(pfs), "ids": [pf["id"] for pf in pfs], "kinds": kinds}


def main(argv=None) -> int:
    """``python -m wenart.blender.site platforms <building.json> [--out PATH]`` (CPU, no bpy): the hook of the
    pipeline_final stage that writes ``site.platforms`` into the building (in place without ``--out``). Exit 0;
    2 for a file that is not a building JSON."""
    import argparse
    import json
    import sys
    from pathlib import Path

    ap = argparse.ArgumentParser(prog="python -m wenart.blender.site")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("platforms", help="write site.platforms (one level per terrace / pool / parking) into the building")
    p.add_argument("building")
    p.add_argument("--out", default=None, help="where to write (default: the building file itself)")
    args = ap.parse_args(argv)
    path = Path(args.building)
    try:
        building = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"site platforms: {path}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(building, dict):
        print(f"site platforms: {path}: not a building JSON", file=sys.stderr)
        return 2
    rec = platforms_into_building(building)
    out = Path(args.out) if args.out else path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(building, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"SITE_PLATFORMS {out} count={rec['count']} kinds={rec['kinds']}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
