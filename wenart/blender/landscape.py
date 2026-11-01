"""The outside areas finished as a landscape architect would (1 Nov 2026, lessons UL248, UL249).

User on real04 run 20261031-194116-full: "This section also too plain front of the house" (UL248: between the house's
glazed front and the street hedge a sloped bank, about 1.6 m down over 1.5 m, its surface the graded terrain itself in
large plain stone slabs, nothing on it) and "Outside areas needs a touch up" (UL249: the outside areas read bare and
flat).

The causes (measured on the run's own plan, ``build.prepare`` of its building_final.json):

- the terrain was paved: Argus set the material slot ``ground`` to ``paving_stone`` (agent_overrides.materials, "the
  ground slot has no real material assigned, so the terrace reads as a void"); ``exterior_checks.SLOT_KINDS`` let the
  ground slot take any look of vocabulary kind ``ground``, and that kind holds the hard finishes (paving, paving_stone,
  asphalt) next to the soft ones (grass, gravel); ``overrides.apply_looks`` put it on the garden look and
  ``site.build_site`` laid the garden look over the whole terrain mesh (the garden, every graded bank, the fields out to
  the horizon), so the bank in front of the house became a ramp of slabs;
- a bank of the natural terrain had no rule at all: the planting rules (``grading.tier_plants``) plant the terrace
  tiers and the platforms' own banks (``grading.plan_embankments``); a slope of the ground between two levels that no
  platform made (real04's front: the house's lower floor at -3.0 m, the street at -4.6 m) stayed bare (the site's
  ``grading.banks`` was empty);
- nothing finished the edges or the areas: paved strips ended raw in the lawn, beds, planters and garden lights were
  never planned.

What (pure Python on dicts, no shapely: it runs inside Blender too; general rules for every project, the project is
only the test case):

1. the terrain is never paved (``terrain_look``, ``ground_look_problems``): the ground, the garden and their banks take a
   soft finish (``SOFT_GROUND_LOOKS``: lawn or gravel); a paving look belongs on the paving slot (paths, terraces);
2. a graded bank is never a walking surface and never paved (``find_banks``): every stretch of the terrain inside the
   plot steeper than ``bank_slope`` (1:4) that rises at least ``bank_rise_m``, clear of the house, the platforms and
   their own banks, the paths, the paved areas, the steps, the doors, the pools and the hedges, is planted: up to the
   planted slope (``grading.GRADE["planted_slope"]``, 1:2) a planted bank (a gravel bed with ground cover, ornamental
   grasses and a few accent shrubs, accent boulders on a large one), steeper as terraced planting steps (fill terraces
   of low stone edging walls in the house's base stone with a coping, at most ``terrace_wall_m``, a planted gravel bed
   on each); the platforms' terraces and retaining walls keep their own rules;
3. edges: a paved area that meets the lawn or a bed gets a border band (a soldier course in a stone that contrasts with
   the paving, ``border_look``); a bed that meets the lawn gets a clean steel lawn edge; planting beds run along the
   facades of every house on the plot (``buildings``: the modelled one and its copies on the site plan) and beside the
   paths where there is room (never in a walkway, a door's approach, over a drain or a light well);
4. touches where the area's use supports them: a pair of large planters at every entrance landing and one at the
   outer corners of a terrace (never on the pool's coping or its walkway, never in a flight's way), low garden lights
   (bollards) along every path and at the foot of every flight, a feature tree with a few boulders in a large lawn.

``plan(site)`` runs at the end of ``build.prepare_once`` (after the architect's paths), ``site.build_landscape`` makes
the parts in Blender (its plants are trees of the plan, built by ``vegetation.tree_object`` with the other trees),
``review`` is the model review's G16 (``site_sense.review``).

Species (``planting_species``): the species the documents name for their shrubs first, else the climate's set
(``PLANTING``), every one marked ``inferred`` and named in the report. Every plant is a real model or generated
geometry with leaf textures (``vegetation.tree_object``: the Poly Haven scan near the cameras, leaf cards elsewhere).

Everything passes the site's code checks: nothing stands in a path, a landing, a door's approach, a drive, a flight, a
pool's coping or walkway (``keep_outs``; the model review's G14 sees the plants, G16 ``review`` sees every item), the
walk graph (G15) is untouched (no item is a surface), the terrain grading is untouched (a terraced bank is built on
the ground, its footprint cut from the lawn mesh, ``ground_holes``). Deterministic: grids, fixed orders, no random.
Every item is ``inferred`` / ``added_by_ai`` with its reason (``site["landscape"]``, the scene manifest's site block).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# 1 Nov 2026 (UL248): the finishes the terrain may take (the garden, its banks, the fields): never a paving
SOFT_GROUND_LOOKS: tuple[str, ...] = ("grass", "gravel")
TERRAIN_FALLBACK = "grass"

LANDSCAPE = {
    "cell_m": 0.5,                 # the bank grid
    "bank_slope": 0.25,            # a ground steeper than 1:4 is a bank (a lawn is mown up to 1:3, walked on far less)
    "bank_rise_m": 0.4,            # ... rising at least this much
    "bank_area_m2": 2.0,           # ... over at least this area
    "facade_m": 0.3,               # no bank cell this close to the house (the plinth, the drains)
    "terrace_bed_m": 0.6,          # a planting step's bed at least this deep where the wall height allows
    "terrace_wall_m": (0.3, 0.6),  # the low edging walls of the planting steps (lowest, highest)
    "wall_t": 0.18, "coping_t": 0.04, "coping_over": 0.03, "bed_drop_m": 0.04, "below_m": 0.3, "flush_m": 0.08,
    "plant_pitch_m": 0.75, "plant_inset_m": 0.22, "drift_m": 1.8, "accent_every": 4,
    "plants_max": 160,
    "front_bed_m": 0.8, "front_bed_min_m": 2.0, "piece_m": 0.5,
    "path_bed_m": 0.6, "path_bed_gap_m": 0.1, "path_bed_min_m": 1.5, "path_end_m": 0.8,
    "door_zone_m": (0.9, 1.6),     # a door's approach: half its width, its depth out from the facade
    "pool_keep_m": 1.0,            # past the pool's coping (site.POOL_COPING_M): the walkway round the pool
    "border_w": 0.12, "border_up": 0.006, "border_down": 0.05,
    "edge_t": 0.012, "edge_up": 0.025, "edge_down": 0.08,
    "pot": {"bottom": 0.42, "top": 0.56, "height": 0.62, "wall": 0.04, "soil": 0.05, "clear": 0.12},
    "pot_corner_m": 0.45, "pots_per_terrace": 2,
    "light": {"size": 0.14, "height": 0.62, "lens": (0.44, 0.54), "cap": 0.04, "below": 0.1},
    "light_pitch_m": 3.5, "light_offset_m": 0.35, "light_end_m": 0.6,
    "lawn_tree_clear_m": 3.0, "lawn_min_m2": 40.0, "lawn_facade_m": 4.0, "lawn_step_m": 1.0,
    "feature_crown_m": 3.0,
    "boulder_bank_m2": 6.0, "boulders_per_bank": 2,
    "flat_slope": 1.0 / 6.0,       # a bed, a planter, a light or a lawn tree stands on ground gentler than this
}
# the plant roles: crown diameter and height (m)
ROLES = {"groundcover": (0.55, 0.4), "grass": (0.5, 0.6), "accent": (0.9, 1.0), "potted": (0.6, 0.8)}
# The planting set per climate (``site.climate_of``; every name a key of vegetation.SPECIES): ground cover, ornamental
# grass, accent shrubs (in turn)
PLANTING = {
    "mediterranean": {"groundcover": ("succulent_shrub",), "grass": ("ornamental_grass",),
                      "accent": ("oleander", "privet_shrub"), "potted": ("oleander",)},
    "temperate": {"groundcover": ("privet_shrub",), "grass": ("ornamental_grass",), "accent": ("privet_shrub",),
                  "potted": ("privet_shrub",)},
}
DRIFT_ROLES = ("groundcover", "grass", "groundcover", "grass", "groundcover")
# The looks the landscape's parts take (vocabulary slugs with a CC0 texture set, or procedural metals); the walls take
# the house's base stone (``site["wall_look"]``), their coping the steps' stone (``grading.floor_set``)
LOOKS = {"bed": "gravel", "edge": "aluminium_anthracite", "pot": "concrete_polished", "bollard": "aluminium_anthracite",
         "lens": "painted_metal_white", "boulder": "rock_boulder", "border_dark": "slate_floor",
         "border_light": "paving_stone"}
BORDER_LIGHT_Y = 0.15              # a paving lighter than this (linear luminance of its flat colour) takes a dark border
DOOR_ABOVE_M = 1.2                 # an outside door this far over the ground at most (its entrance steps) opens on the
DOOR_BELOW_M = 0.3                 # garden, this far under it at most (a step down); others get no planters or approach
SOURCE = "landscape"
CHECK_RULE = "G16"
LESSONS = "UL248, UL249"


# --------------------------------------------------------------------------
# The terrain's finish (rule 1)
# --------------------------------------------------------------------------

def is_soft(slug: Optional[str]) -> bool:
    """Whether a look may cover the terrain (pure): a soft ground finish of ``SOFT_GROUND_LOOKS`` (a ``slug__asset``
    material name counts by its slug)."""
    return str(slug or "").split("__")[0] in SOFT_GROUND_LOOKS


def ground_look_problems(slot: str, look_id: str) -> list[str]:
    """Why ``look_id`` may not go on the ground or garden slot (pure; rule 1): a hard finish (paving, slabs, asphalt)
    would pave the whole terrain, its banks and the fields to the horizon; [] for a soft finish or another slot."""
    if slot not in ("ground", "garden") or is_soft(look_id):
        return []
    return [f"{slot}: {look_id} is a hard finish; the {slot} slot is the whole terrain (the garden, its banks and the "
            f"fields to the horizon), which stays soft ({' or '.join(SOFT_GROUND_LOOKS)}); a paving look belongs on the "
            f"paving slot (paths and terraces; UL248)"]


def terrain_look(look: Optional[dict]) -> tuple[dict, Optional[str]]:
    """``(look, note)``: the look the terrain takes (pure; rule 1): ``look`` when it is soft, else the lawn
    (``TERRAIN_FALLBACK``) with the reason in ``note`` (None when the look is kept)."""
    look = look or {}
    if is_soft(look.get("material")):
        return look, None
    note = (f"the terrain is never paved: the garden look {look.get('material')!r} ({look.get('source') or 'unknown'}) "
            f"is a hard finish; the ground, its banks and the fields take a lawn, the paving stays on the paths and "
            f"terraces (UL248)")
    return {"material": TERRAIN_FALLBACK, "colour": None, "rgb": None, "asset": None, "source": "build",
            "assumed": True, "reason": note, "evidence": [], "replaced": look.get("material")}, note


# --------------------------------------------------------------------------
# Small geometry
# --------------------------------------------------------------------------

def _bbox(poly) -> tuple[float, float, float, float]:
    xs = [float(p[0]) for p in poly]
    ys = [float(p[1]) for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def _keep(polys, kind: str, src: Optional[str] = None) -> list[dict]:
    out = []
    for p in polys or []:
        q = [(float(v[0]), float(v[1])) for v in p or []]
        if len(q) >= 3:
            out.append({"kind": kind, "polygon": q, "box": _bbox(q), "src": src or kind})
    return out


class KeepIndex:
    """Keep-outs bucketed on a plan grid (``bucket_m``), so a point meets only the polygons near it (pure; the bank
    grid tests some 20 000 points against a few hundred polygons). Iterates like the list it was made from."""

    def __init__(self, keep: Sequence[dict], bucket_m: float = 2.0):
        self.keep = list(keep)
        self.b = float(bucket_m)
        self.cells: dict = {}
        for n, k in enumerate(self.keep):
            x0, y0, x1, y1 = k["box"]
            for i in range(int(math.floor(x0 / self.b)), int(math.floor(x1 / self.b)) + 1):
                for j in range(int(math.floor(y0 / self.b)), int(math.floor(y1 / self.b)) + 1):
                    self.cells.setdefault((i, j), []).append(n)

    def __iter__(self):
        return iter(self.keep)

    def __len__(self):
        return len(self.keep)

    def near(self, p, margin: float = 0.0) -> list[dict]:
        x, y = float(p[0]), float(p[1])
        if margin <= 0.0:
            return [self.keep[n] for n in self.cells.get((int(math.floor(x / self.b)), int(math.floor(y / self.b))), ())]
        ids: set = set()
        for i in range(int(math.floor((x - margin) / self.b)), int(math.floor((x + margin) / self.b)) + 1):
            for j in range(int(math.floor((y - margin) / self.b)), int(math.floor((y + margin) / self.b)) + 1):
                ids.update(self.cells.get((i, j), ()))
        return [self.keep[n] for n in sorted(ids)]


def _hit(p, keep, kinds: Optional[Sequence[str]] = None, margin: float = 0.0) -> Optional[dict]:
    """The first keep-out ``p`` lies in (or within ``margin`` of), else None (pure); ``keep`` a list or a
    ``KeepIndex``."""
    x, y = float(p[0]), float(p[1])
    if isinstance(keep, KeepIndex):
        keep = keep.near(p, margin)
    for k in keep:
        if kinds is not None and k["kind"] not in kinds:
            continue
        b = k["box"]
        if x < b[0] - margin or x > b[2] + margin or y < b[1] - margin or y > b[3] + margin:
            continue
        if G.point_in_polygon((x, y), k["polygon"]):
            return k
        if margin > 0 and geom2d.distance_to_polygon_edges((x, y), k["polygon"]) < margin:
            return k
    return None


def _rect(o, u, v, s0: float, s1: float, t0: float, t1: float) -> list[tuple[float, float]]:
    """The rectangle ``[s0, s1] x [t0, t1]`` of the frame (origin ``o``, unit axes ``u``, ``v``) in plan (ccw when
    ``v`` is ``u`` turned left)."""
    pts = [(o[0] + u[0] * s + v[0] * t, o[1] + u[1] * s + v[1] * t) for s, t in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))]
    return geom2d.ccw(pts)


def _at(o, u, v, s: float, t: float) -> tuple[float, float]:
    return (o[0] + u[0] * s + v[0] * t, o[1] + u[1] * s + v[1] * t)


def site_frame(site: dict) -> dict:
    """The frame of the site's grids (pure): the house's longest facade as ``u`` (its direction made canonical, so the
    same house gives the same grid), ``v`` turned left, the origin at 0, 0."""
    outline = [tuple(map(float, p[:2])) for p in site.get("outline") or []]
    ux, uy = 1.0, 0.0
    if len(outline) >= 3:
        a, b = geom2d.longest_edge(outline)
        length = G.distance(a, b)
        if length > 1e-6:
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    if ux < -1e-9 or (abs(ux) <= 1e-9 and uy < 0):
        ux, uy = -ux, -uy
    return {"o": (0.0, 0.0), "u": (round(ux, 9), round(uy, 9)), "v": (round(-uy, 9), round(ux, 9))}


def plot_of(site: dict) -> list[tuple[float, float]]:
    """The plot a landscape is planned in (pure): the drawn plot, else the inferred one, else none."""
    plot = site.get("plot") or ((site.get("inferred") or {}).get("plot")) or []
    return geom2d.ccw([tuple(map(float, p[:2])) for p in plot]) if len(plot) >= 3 else []


# --------------------------------------------------------------------------
# What the landscape keeps clear of
# --------------------------------------------------------------------------

def buildings(site: dict) -> list[dict]:
    """The houses on the plot (pure): the modelled one (``outline``, ``outside_doors``) and every copy of it on the
    site plan (``site["copies"]``: its drawn footprint, its doors moved by its rotation and translation,
    ``copies.move_point``): ``[{"id", "ring", "doors": [{"id", "point"}], "copy"}]``."""
    out = []
    outline = [tuple(map(float, p[:2])) for p in site.get("outline") or []]
    terrain = site.get("terrain")
    doors = []
    for d in site.get("outside_doors") or []:
        if not d.get("point"):
            continue
        p = (float(d["point"][0]), float(d["point"][1]))
        if terrain and isinstance(d.get("z"), (int, float)):
            from wenart.blender import site as S
            g = S.ground_z(terrain, *p)
            if not -DOOR_BELOW_M <= float(d["z"]) - g <= DOOR_ABOVE_M:
                continue                                  # a door of an upper floor or a sunken court: no garden entrance
        doors.append({"id": str(d.get("id")), "point": p})
    if len(outline) >= 3:
        out.append({"id": "house", "ring": geom2d.ccw(outline), "doors": doors, "copy": False})
    for c in site.get("copies") or []:
        fp = [tuple(map(float, p[:2])) for p in c.get("footprint") or []]
        if len(fp) < 3:
            continue
        a = math.radians(float(c.get("rotation_deg") or 0.0))
        t = c.get("translate") or (0.0, 0.0)

        def move(p, a=a, t=t):
            return (math.cos(a) * p[0] - math.sin(a) * p[1] + float(t[0]),
                    math.sin(a) * p[0] + math.cos(a) * p[1] + float(t[1]))
        out.append({"id": str(c.get("id") or f"copy_{len(out)}"), "ring": geom2d.ccw(fp), "copy": True,
                    "doors": [{"id": f"{c.get('id')}:{d['id']}", "point": move(d["point"])} for d in doors]})
    return out


def _facade_of(ring, p) -> Optional[tuple]:
    """``(a, u, out_n, s)`` of the facade nearest ``p`` (pure): its start, direction, outward normal and ``p``'s place
    along it; None for a degenerate edge."""
    n = len(ring)
    k = min(range(n), key=lambda i: G.point_segment_distance(p, ring[i], ring[(i + 1) % n]))
    a, b = ring[k], ring[(k + 1) % n]
    length = G.distance(a, b)
    if length < 1e-6:
        return None
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    return a, u, (u[1], -u[0]), (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]   # ccw ring: the outside on the right


def door_zones(site: dict) -> list[list[tuple[float, float]]]:
    """A door's approach (pure): ``door_zone_m`` (half width, depth) in front of every outside door of every house on
    the plot, on its facade."""
    hw, depth = LANDSCAPE["door_zone_m"]
    out = []
    for bd in buildings(site):
        for d in bd["doors"]:
            f = _facade_of(bd["ring"], d["point"])
            if f is not None:
                a, u, out_n, s = f
                out.append(_rect(a, u, out_n, s - hw, s + hw, -0.05, depth))
    return out


def keep_outs(site: dict, terrain: Optional[dict] = None) -> list[dict]:
    """Everything a bed, a plant, a planter, a light or a boulder keeps clear of (pure): ``[{"kind", "polygon",
    "box"}]`` of kind ``building`` (the house and the other buildings), ``hard`` (every site area: paths, paved areas,
    parkings, roads, pavements; the platforms; the light wells and aprons; the entrance steps and landings; the
    platforms' flights and the graded paths), ``hedge``, ``door`` (``door_zones``), ``pool`` (the pool with its coping
    and walkway), ``pool_extra`` (the ladder and the seating zone), ``bank_zone`` (the platforms' own banks, planted by
    ``grading.tier_plants``) and ``walk`` (the flights' foot landings and the tops of flights up)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    terrain = terrain if terrain is not None else GR.plan_terrain(site)
    keep: list[dict] = []
    keep += _keep([site.get("outline") or []] + list(site.get("copy_holes") or []), "building")
    for a in site.get("areas") or []:
        keep += _keep([a.get("polygon")], "hard", f"area:{a.get('platform_id') or a.get('id')}")
    for pf in site.get("platforms") or []:
        keep += _keep([pf.get("polygon")], "hard", f"platform:{pf.get('id')}")
    keep += _keep([w.get("polygon") for w in site.get("wells") or []], "hard", "well")
    keep += _keep([a.get("polygon") for a in site.get("aprons") or []], "hard", "apron")
    for st in (site.get("inferred") or {}).get("steps") or []:
        keep += _keep([b.get("polygon") for b in list(st.get("blocks") or []) + list(st.get("cheeks") or [])],
                      "hard", "steps")
        if isinstance(st.get("ramp"), dict):
            keep += _keep([st["ramp"].get("polygon")], "hard", "steps")
    keep += _keep([ld["polygon"] for ld in GR.entrance_landings(site)], "hard", "landing")
    if terrain:
        from wenart.blender import architect as AR
        keep += _keep(AR.flight_footprints(site), "hard", "flight")
        try:
            keep += _keep([r["polygon"] for r in GR.graded_paths(site)], "hard", "path")
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            pass
    keep += _keep([p for h in site.get("hedges") or [] for p in S._hedge_footprints(h)], "hedge")
    keep += _keep(door_zones(site), "door")
    grow = S.POOL_COPING_M + LANDSCAPE["pool_keep_m"]
    keep += _keep([geom2d.offset_polygon(geom2d.ccw(p["polygon"]), -grow) for p in site.get("pools") or []
                   if len(p.get("polygon") or []) >= 3], "pool")
    try:
        from wenart.blender import pool_extras as PX
        zones = []
        for rec in PX.plan(site):
            if rec.get("ladder") and rec["ladder"].get("zone"):
                zones.append(rec["ladder"]["zone"])
            if rec.get("seating") and rec["seating"].get("zone"):
                zones.append(rec["seating"]["zone"])
        keep += _keep(zones, "pool_extra")
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError):
        pass
    if terrain:
        keep += _keep(GR.bank_zones(terrain), "bank_zone")
        try:
            gz = (lambda x, y: S.ground_z(terrain, x, y))
            keep += _keep([s["polygon"] for s in GR.walk_surfaces(site, gz, terrain) if s["id"].startswith(("foot:", "top:"))],
                          "walk")
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            pass
    return keep


# Kinds a planted thing may never stand in (everything but the building, whose own margin each rule sets)
NO_PLANT = ("hard", "hedge", "door", "pool", "pool_extra", "bank_zone", "walk")
# Kinds a walker meets: nothing of the landscape stands in them (review)
WALKWAYS = ("hard", "door", "pool", "walk")


# --------------------------------------------------------------------------
# Banks (rule 2)
# --------------------------------------------------------------------------

def _corner_z(cache: dict, frame: dict, gz: Callable, i: int, j: int, c: float) -> float:
    key = (i, j)
    if key not in cache:
        x, y = _at(frame["o"], frame["u"], frame["v"], i * c, j * c)
        cache[key] = float(gz(x, y))
    return cache[key]


def find_banks(site: dict, keep: Optional[Sequence[dict]] = None, terrain: Optional[dict] = None,
               cfg: Optional[dict] = None) -> list[dict]:
    """The banks of the terrain inside the plot (pure; rule 2): the cells (``cell_m`` squares of ``site_frame``) whose
    ground slopes more than ``bank_slope`` and that lie clear of every keep-out (``keep_outs`` but the trees: a drawn
    shrub on a bank is part of its planting) and ``facade_m`` off the house, joined side by side; a group that rises
    at least ``bank_rise_m`` over at least ``bank_area_m2`` is a bank: ``{"id", "frame", "cell_m", "cells": [[i, j]],
    "area_m2", "z_range", "rise_m", "slope_max", "slope_p75", "finish": planted | terraced, "reason"}``, the finish
    ``terraced`` where it is steeper than the planted slope (``grading.GRADE["planted_slope"]``)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    cfg = dict(LANDSCAPE, **(cfg or {}))
    terrain = terrain if terrain is not None else GR.plan_terrain(site)
    plot = plot_of(site)
    if not terrain or S.is_flat(terrain) or len(plot) < 3:
        return []
    keep = list(keep) if keep is not None else keep_outs(site, terrain)
    frame = site_frame(site)
    o, u, v = frame["o"], frame["u"], frame["v"]
    c = float(cfg["cell_m"])
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    ss = [(p[0] - o[0]) * u[0] + (p[1] - o[1]) * u[1] for p in plot]
    ts = [(p[0] - o[0]) * v[0] + (p[1] - o[1]) * v[1] for p in plot]
    i0, i1 = int(math.floor(min(ss) / c)), int(math.ceil(max(ss) / c))
    j0, j1 = int(math.floor(min(ts) / c)), int(math.ceil(max(ts) / c))
    margin = float(cfg["facade_m"])
    blocks = KeepIndex([k for k in keep if k["kind"] in NO_PLANT])
    house = KeepIndex([k for k in keep if k["kind"] == "building"])
    cache: dict = {}
    cells: dict = {}
    inset = 0.05
    for i in range(i0, i1):
        for j in range(j0, j1):
            probe = [_at(o, u, v, (i + 0.5) * c, (j + 0.5) * c)] + \
                [_at(o, u, v, (i + a) * c + inset * (1 - 2 * a), (j + b) * c + inset * (1 - 2 * b))
                 for a, b in ((0, 0), (1, 0), (1, 1), (0, 1))]
            if not all(G.point_in_polygon(p, plot) for p in probe):
                continue
            if any(_hit(p, blocks) for p in probe) or any(_hit(p, house, margin=margin) for p in probe):
                continue
            z00 = _corner_z(cache, frame, gz, i, j, c)
            z10 = _corner_z(cache, frame, gz, i + 1, j, c)
            z01 = _corner_z(cache, frame, gz, i, j + 1, c)
            z11 = _corner_z(cache, frame, gz, i + 1, j + 1, c)
            ds = ((z10 + z11) - (z00 + z01)) / (2.0 * c)
            dt = ((z01 + z11) - (z00 + z10)) / (2.0 * c)
            slope = math.hypot(ds, dt)
            if slope >= float(cfg["bank_slope"]) - 1e-9:
                cells[(i, j)] = {"slope": slope, "z": (z00 + z10 + z01 + z11) / 4.0,
                                 "lo": min(z00, z10, z01, z11), "hi": max(z00, z10, z01, z11), "g": (ds, dt)}
    banks = []
    seen: set = set()
    for start in sorted(cells):
        if start in seen:
            continue
        comp, todo = [], [start]
        seen.add(start)
        while todo:
            cur = todo.pop()
            comp.append(cur)
            ci, cj = cur
            for nb in ((ci + 1, cj), (ci - 1, cj), (ci, cj + 1), (ci, cj - 1)):
                if nb in cells and nb not in seen:
                    seen.add(nb)
                    todo.append(nb)
        comp.sort()
        area = len(comp) * c * c
        lo = min(cells[k]["lo"] for k in comp)
        hi = max(cells[k]["hi"] for k in comp)
        if area < float(cfg["bank_area_m2"]) - 1e-9 or hi - lo < float(cfg["bank_rise_m"]) - 1e-9:
            continue
        slopes = sorted(cells[k]["slope"] for k in comp)
        p75 = slopes[min(len(slopes) - 1, int(0.75 * len(slopes)))]
        gs = sum(cells[k]["g"][0] for k in comp) / len(comp), sum(cells[k]["g"][1] for k in comp) / len(comp)
        terraced = p75 > float(GR.GRADE["planted_slope"]) + 1e-9
        bid = f"bank_{len(banks) + 1}"
        down = (-(gs[0] * u[0] + gs[1] * v[0]), -(gs[0] * u[1] + gs[1] * v[1]))
        dl = math.hypot(*down) or 1.0
        banks.append({"id": bid, "frame": {"o": list(o), "u": list(u), "v": list(v)}, "cell_m": c,
                      "cells": [list(k) for k in comp], "area_m2": round(area, 3), "z_range": [round(lo, 4), round(hi, 4)],
                      "rise_m": round(hi - lo, 3), "slope_max": round(slopes[-1], 3), "slope_p75": round(p75, 3),
                      "downhill": [round(down[0] / dl, 4), round(down[1] / dl, 4)],
                      "finish": "terraced" if terraced else "planted",
                      "corner_z": {f"{i},{j}": round(cache[(i, j)], 4) for i, j in sorted(
                          {(ci + a, cj + b) for ci, cj in comp for a in (0, 1) for b in (0, 1)})},
                      "reason": (f"a bank of the terrain {area:.1f} m² rising {hi - lo:.2f} m at up to 1:"
                                 f"{1.0 / max(slopes[-1], 1e-6):.1f} (steeper than 1:{1.0 / float(cfg['bank_slope']):.0f}): a "
                                 f"slope between levels, not a walking surface, never paved: "
                                 + ("terraced planting steps with low stone edging walls (steeper than the planted "
                                    f"slope 1:{1.0 / float(GR.GRADE['planted_slope']):.0f})" if terraced else
                                    "a planted bank: ground cover, ornamental grasses and accent shrubs in a gravel bed")
                                 + f" ({LESSONS}; inferred)")})
    return banks


def refine_bank(bank: dict, gz: Callable, factor: int = 2) -> dict:
    """The bank on a grid ``factor`` times finer (pure): its cells split, the new corners' ground read, so a terraced
    bank's steps follow its slope closer than the detection grid does (a 1 m deep bank gets 4 rows, not 2)."""
    o, u, v = _frame_of(bank)
    c = float(bank["cell_m"]) / factor
    cells = sorted({(i * factor + a, j * factor + b) for i, j in bank["cells"] for a in range(factor)
                    for b in range(factor)})
    corners = sorted({(i + a, j + b) for i, j in cells for a in (0, 1) for b in (0, 1)})
    cz = {}
    for i, j in corners:
        x, y = _at(o, u, v, i * c, j * c)
        cz[f"{i},{j}"] = round(float(gz(x, y)), 4)
    return dict(bank, cell_m=c, cells=[list(k) for k in cells], corner_z=cz)


def cells_to_rects(cells: Sequence[Sequence[int]]) -> list[tuple[int, int, int, int]]:
    """``[(i0, i1, j0, j1)]`` (inclusive cell indices) covering ``cells`` (pure): the runs along ``i`` of each row,
    then the runs of equal extent in consecutive rows merged (deterministic)."""
    rows: dict = {}
    for i, j in sorted((int(a), int(b)) for a, b in cells):
        rows.setdefault(j, []).append(i)
    runs = []
    for j in sorted(rows):
        xs = rows[j]
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            runs.append((start, prev, j))
            if x is not None:
                start = prev = x
    open_: dict = {}
    out = []
    for i0, i1, j in runs:
        key = (i0, i1)
        if key in open_ and open_[key][3] == j - 1:
            r = open_[key]
            open_[key] = (r[0], r[1], r[2], j)
        else:
            if key in open_:
                out.append(open_.pop(key))
            open_[key] = (i0, i1, j, j)
    out += list(open_.values())
    return sorted(out, key=lambda r: (r[2], r[0], r[3], r[1]))


def _frame_of(rec: dict) -> tuple:
    fr = rec["frame"]
    return tuple(fr["o"]), tuple(fr["u"]), tuple(fr["v"])


def bank_rects(bank: dict, cells: Optional[Sequence] = None) -> list[list[tuple[float, float]]]:
    """The plan rectangles of a bank's cells (pure)."""
    o, u, v = _frame_of(bank)
    c = float(bank["cell_m"])
    return [_rect(o, u, v, i0 * c, (i1 + 1) * c, j0 * c, (j1 + 1) * c)
            for i0, i1, j0, j1 in cells_to_rects(cells if cells is not None else bank["cells"])]


def _cz(bank: dict, i: int, j: int) -> float:
    return float(bank["corner_z"][f"{i},{j}"])


def terrace_plan(bank: dict, cfg: Optional[dict] = None) -> dict:
    """The planting steps of a terraced bank (pure; rule 2): ``n`` tiers of equal step (the bank's rise over the
    fewest tiers whose wall stays within ``terrace_wall_m``, aiming at beds ``terrace_bed_m`` deep), each cell in the
    tier of its middle's ground; tier ``k``'s bed level ``lo + (k + 1) step`` (the top tier at the bank's top). Returns
    ``{"tiers": n, "step_m", "levels": [z], "tier_of": {"i,j": k}, "beds": [{"tier", "cells", "level"}]}``."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    lo, hi = (float(v) for v in bank["z_range"])
    rise = max(hi - lo, 1e-6)
    wmin, wmax = cfg["terrace_wall_m"]
    target = min(wmax, max(wmin, float(bank["slope_p75"]) * float(cfg["terrace_bed_m"])))
    n = max(1, int(math.ceil(rise / target - 1e-6)))
    step = rise / n
    tier_of = {}
    for i, j in bank["cells"]:
        zc = (_cz(bank, i, j) + _cz(bank, i + 1, j) + _cz(bank, i, j + 1) + _cz(bank, i + 1, j + 1)) / 4.0
        tier_of[f"{i},{j}"] = min(n - 1, max(0, int((zc - lo) / step)))
    beds = []
    for k in range(n):
        cells = [[i, j] for i, j in bank["cells"] if tier_of[f"{i},{j}"] == k]
        if cells:
            beds.append({"tier": k, "cells": cells, "level": round(lo + (k + 1) * step, 4)})
    return {"tiers": n, "step_m": round(step, 4), "levels": [round(lo + (k + 1) * step, 4) for k in range(n)],
            "tier_of": tier_of, "beds": beds}


SIDES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _side_edge(i: int, j: int, di: int, dj: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """The cell edge of cell ``(i, j)`` towards ``(di, dj)`` as two corner indices, the cell on the left going from the
    first to the second (pure)."""
    if (di, dj) == (1, 0):
        return (i + 1, j), (i + 1, j + 1)
    if (di, dj) == (-1, 0):
        return (i, j + 1), (i, j)
    if (di, dj) == (0, 1):
        return (i + 1, j + 1), (i, j + 1)
    return (i, j), (i + 1, j)


def terrace_walls(bank: dict, terr: dict, gz: Callable, cfg: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """``(walls, flush)`` of a terraced bank (pure): a wall piece on every cell edge where a tier meets a lower tier
    (its front, ``kind: front``) or the ground beside the bank more than ``flush_m`` under its bed level (``fill``) or
    over it (``cut``: the wall holds the ground back, its top following it), inside the higher side; ``flush`` the
    edges where a bed meets the ground at its level (a lawn edge there). Each piece ``{"p0", "p1", "top0", "top1",
    "bottom", "inward", "kind", "coping"}`` (its outer face on the edge, ``inward`` the unit normal into its cell)."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    o, u, v = _frame_of(bank)
    c = float(bank["cell_m"])
    tier_of = terr["tier_of"]
    levels = terr["levels"]
    below = float(cfg["below_m"])
    walls, flush = [], []
    for i, j in sorted((int(a), int(b)) for a, b in bank["cells"]):
        k = tier_of[f"{i},{j}"]
        top = levels[k]
        for di, dj in SIDES:
            nb = f"{i + di},{j + dj}"
            a, b = _side_edge(i, j, di, dj)
            p0 = _at(o, u, v, a[0] * c, a[1] * c)
            p1 = _at(o, u, v, b[0] * c, b[1] * c)
            inward = (-(u[0] * di + v[0] * dj), -(u[1] * di + v[1] * dj))
            if nb in tier_of:
                kn = tier_of[nb]
                if kn >= k:
                    continue
                walls.append({"p0": p0, "p1": p1, "top0": top, "top1": top, "bottom": levels[kn] - below,
                              "inward": inward, "kind": "front", "coping": True, "cell": [i, j]})
                continue
            out = (-inward[0] * 0.1, -inward[1] * 0.1)
            g0 = float(gz(p0[0] + out[0], p0[1] + out[1]))
            g1 = float(gz(p1[0] + out[0], p1[1] + out[1]))
            gl = min(g0, g1, _cz(bank, *a), _cz(bank, *b))
            if max(g0, g1) < top - float(cfg["flush_m"]):
                walls.append({"p0": p0, "p1": p1, "top0": top, "top1": top, "bottom": gl - below, "inward": inward,
                              "kind": "fill", "coping": True, "cell": [i, j]})
            elif min(g0, g1) > top + float(cfg["flush_m"]):
                walls.append({"p0": p0, "p1": p1, "top0": g0 + 0.05, "top1": g1 + 0.05, "bottom": top - below,
                              "inward": inward, "kind": "cut", "coping": False, "cell": [i, j]})
            else:
                flush.append({"p0": p0, "p1": p1, "cell": [i, j]})
    return walls, flush


def merge_runs(pieces: Sequence[dict], tol: float = 1e-6) -> list[dict]:
    """Wall pieces of one line with equal level tops joined end to end (pure; deterministic): fewer, longer walls."""
    out: list[dict] = []
    for p in sorted(pieces, key=lambda w: (w["kind"], round(w["inward"][0], 6), round(w["inward"][1], 6),
                                           round(w["top0"], 4), round(w["bottom"], 4),
                                           round(min(w["p0"][0], w["p1"][0]), 4), round(min(w["p0"][1], w["p1"][1]), 4))):
        last = out[-1] if out else None
        if last is not None and last["kind"] == p["kind"] and last["kind"] != "cut" \
                and abs(last["top0"] - p["top0"]) < tol and abs(last["bottom"] - p["bottom"]) < tol \
                and abs(last["inward"][0] - p["inward"][0]) < tol and abs(last["inward"][1] - p["inward"][1]) < tol:
            if G.distance(last["p1"], p["p0"]) < 1e-6:
                last["p1"] = p["p1"]
                continue
            if G.distance(last["p0"], p["p1"]) < 1e-6:
                last["p0"] = p["p0"]
                continue
        out.append(dict(p))
    return out


# --------------------------------------------------------------------------
# Beds and plants
# --------------------------------------------------------------------------

def planting_species(site: dict) -> dict:
    """``{role: {"species": [names], "named": bool, "source"}}`` of the planting (pure): the shrub species the documents
    name (a drawn shrub or plant with its own species) for the accent and potted shrubs first, else the climate's set
    (``PLANTING``), inferred."""
    climate = (site.get("climate") or {}).get("climate") or "temperate"
    table = PLANTING.get(climate) or PLANTING["temperate"]
    named = sorted({str(t["species"]) for t in site.get("trees") or []
                    if t.get("species") and t.get("source") != SOURCE and not t.get("species_inferred")
                    and t.get("kind") in ("plant", "tree")
                    and max([float(x) for x in (t.get("size") or [1.0, 1.0])[:2]] or [1.0]) < 3.0})
    out = {}
    for role, names in table.items():
        if named and role in ("accent", "potted"):
            out[role] = {"species": list(named), "named": True, "source": "the documents' shrubs"}
        else:
            out[role] = {"species": list(names), "named": False, "source": f"the {climate} planting set (inferred)"}
    return out


def _scatter(rect_st: tuple, o, u, v, pitch: float, inset: float) -> list[tuple[float, float, int, float]]:
    """``[(s, t, row, depth_share)]`` planting points in a frame rectangle ``(s0, s1, t0, t1)`` (pure): rows along
    ``s`` every 0.87 pitch, staggered by half a pitch; a bed too shallow for two rows gets one in its middle."""
    s0, s1, t0, t1 = rect_st
    depth = t1 - t0
    length = s1 - s0
    if depth < 0.2 or length < 0.2:
        return []
    if depth < 2 * inset + 0.05 or length < 2 * inset + pitch:
        # a shallow bed (a planting step, a narrow strip): one row along its middle
        n = max(1, int(math.floor(max(0.0, length - 2 * min(inset, length / 4.0)) / pitch)) + 1)
        span = (n - 1) * pitch
        start = s0 + (length - span) / 2.0
        return [(start + q * pitch, (t0 + t1) / 2.0, 0, 0.5) for q in range(n)]
    nrow = max(1, int(math.floor((depth - 2 * inset) / (0.87 * pitch))) + 1)
    out = []
    for r in range(nrow):
        t = (t0 + t1) / 2.0 if nrow == 1 else t0 + inset + (depth - 2 * inset) * r / (nrow - 1)
        off = (pitch / 2.0) if r % 2 else 0.0
        n = max(1, int(math.floor((length - 2 * inset - off) / pitch)) + 1)
        span = (n - 1) * pitch
        start = s0 + inset + off + max(0.0, (length - 2 * inset - off - span) / 2.0)
        for q in range(n):
            out.append((start + q * pitch, t, r, (t - t0) / depth if depth > 0 else 0.5))
    return out


class _Planter:
    """Collects the plants of the beds, spaced from each other, from the existing trees and from the keep-outs."""

    def __init__(self, site: dict, keep: Sequence[dict], species: dict, cfg: dict):
        self.site = site
        self.keep = KeepIndex([k for k in keep if k["kind"] in NO_PLANT or k["kind"] == "building"])
        self.species = species
        self.cfg = cfg
        self.discs: list[tuple[float, float, float]] = []
        for t in site.get("trees") or []:
            if t.get("center") and t.get("source") != SOURCE:
                r = max(0.3, max(float(x) for x in (t.get("size") or [1.0, 1.0])[:2])) / 2.0
                self.discs.append((float(t["center"][0]), float(t["center"][1]), r))
        self.plants: list[dict] = []
        self.turn: dict = {}

    def free(self, p, r: float) -> bool:
        if _hit(p, self.keep, margin=max(0.05, r * 0.6)):
            return False
        return all(math.hypot(p[0] - x, p[1] - y) >= 0.85 * (r + rr) for x, y, rr in self.discs)

    def block(self, p, r: float) -> None:
        self.discs.append((float(p[0]), float(p[1]), float(r)))

    def pick(self, role: str) -> str:
        names = self.species[role]["species"]
        k = self.turn.get(role, 0)
        self.turn[role] = k + 1
        return names[k % len(names)]

    def add(self, p, role: str, parent: str, z: Optional[float], why: str) -> Optional[dict]:
        if len(self.plants) >= int(self.cfg["plants_max"]):
            return None
        crown, height = ROLES[role]
        if not self.free(p, crown / 2.0):
            return None
        sp = self.pick(role)
        rec = {"id": f"ls_{parent}_p{sum(1 for q in self.plants if q['parent'] == parent) + 1}", "kind": "plant",
               "center": [round(float(p[0]), 4), round(float(p[1]), 4)], "size": [crown, crown], "height_m": height,
               "species": sp, "species_inferred": not self.species[role]["named"], "role": role,
               "z": None if z is None else round(float(z), 4), "inferred": True, "source": SOURCE, "build": True,
               "added_by_ai": True, "parent": parent,
               "reason": f"{why}: {role.replace('groundcover', 'ground cover')} {sp} "
                         f"({'named in the documents' if self.species[role]['named'] else 'inferred'}; {LESSONS})"}
        self.plants.append(rec)
        self.block(p, crown / 2.0)
        return rec


def bed_plants(planter: _Planter, bed: dict, rects_st: Sequence[tuple], frame: tuple, why: str,
               z: Optional[float] = None, roles: Sequence[str] = DRIFT_ROLES, accents: bool = True) -> int:
    """Plant one bed (pure): drifts of ground cover and grasses every ``drift_m`` along its length, an accent shrub in
    every ``accent_every``-th drift's middle (``accents``), each point clear (``_Planter.free``). Returns the count."""
    o, u, v = frame
    cfg = planter.cfg
    n0 = len(planter.plants)
    for rs in rects_st:
        pts = _scatter(rs, o, u, v, float(cfg["plant_pitch_m"]), float(cfg["plant_inset_m"]))
        if not pts:
            continue
        mid_row = max(r for _s, _t, r, _d in pts) // 2
        done_accent: set = set()
        for s, t, r, _d in pts:
            drift = int(math.floor(s / float(cfg["drift_m"])))
            role = roles[(drift + r) % len(roles)]
            if accents and drift % int(cfg["accent_every"]) == 0 and r == mid_row and drift not in done_accent:
                role = "accent"
                done_accent.add(drift)
            p = _at(o, u, v, s, t)
            if planter.add(p, role, bed["id"], z, why) is None and role == "accent":
                done_accent.discard(drift)
    return len(planter.plants) - n0


def strip_beds(keep: Sequence[dict], plot, gz: Callable, a, b, d0: float, d1: float, out_n, kind: str, bid: str,
               min_len: float, piece: float, flat_slope: float, extra_blocks: Sequence[dict] = ()) -> list[dict]:
    """The beds along a line ``a``-``b`` (pure): the strip ``d0`` to ``d1`` out (``out_n``) cut in ``piece`` lengths, a
    piece kept when its probes lie inside the plot, clear of the keep-outs (``NO_PLANT``, the building) and of
    ``extra_blocks``, on ground gentler than ``flat_slope``; runs of at least ``min_len`` become beds ``{"id", "kind",
    "frame", "rect": [s0, s1, t0, t1], "polygon"}``."""
    length = G.distance(a, b)
    if length < min_len:
        return []
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    blocks = KeepIndex([k for k in keep if k["kind"] in NO_PLANT or k["kind"] == "building"] + list(extra_blocks))
    n = int(math.floor(length / piece))
    ok = []
    for q in range(n):
        s0, s1 = q * piece, (q + 1) * piece
        probe = [_at(a, u, out_n, s, d) for s in (s0 + 0.04, (s0 + s1) / 2.0, s1 - 0.04)
                 for d in (d0 + 0.04, (d0 + d1) / 2.0, d1 - 0.04)]
        good = all(G.point_in_polygon(p, plot) for p in probe) if plot else True
        good = good and not any(_hit(p, blocks) for p in probe)
        if good:
            z = [float(gz(*p)) for p in (probe[0], probe[2], probe[6], probe[8])]
            span = max(z) - min(z)
            good = span <= flat_slope * math.hypot(piece, d1 - d0) + 0.02
        ok.append(good)
    beds = []
    q = 0
    while q < n:
        if not ok[q]:
            q += 1
            continue
        r = q
        while r + 1 < n and ok[r + 1]:
            r += 1
        s0, s1 = q * piece, (r + 1) * piece
        if s1 - s0 >= min_len - 1e-9:
            beds.append({"id": f"{bid}_{len(beds) + 1}", "kind": kind,
                         "frame": {"o": list(a), "u": list(u), "v": list(out_n)},
                         "rect": [round(s0, 4), round(s1, 4), round(d0, 4), round(d1, 4)],
                         "polygon": _rect(a, u, out_n, s0, s1, d0, d1)})
        q = r + 1
    return beds


# --------------------------------------------------------------------------
# Edges (rule 3)
# --------------------------------------------------------------------------

def _lum(slug: Optional[str]) -> Optional[float]:
    try:
        from wenart.style.vocabulary import MATERIALS
    except ImportError:
        return None
    flat = (MATERIALS.get(str(slug or "").split("__")[0]) or {}).get("flat")
    if not flat:
        return None
    return 0.2126 * float(flat[0]) + 0.7152 * float(flat[1]) + 0.0722 * float(flat[2])


def border_look(paving_slug: Optional[str]) -> str:
    """The border band's stone for a paving (pure): a dark granite course on a light paving, a light stone on a dark
    one (``BORDER_LIGHT_Y``); a paving of no known colour takes the dark course."""
    y = _lum(paving_slug)
    return LOOKS["border_dark"] if y is None or y >= BORDER_LIGHT_Y else LOOKS["border_light"]


def _outside_kind(p, keep: Sequence[dict], beds: Sequence[dict], plot) -> str:
    """What lies at ``p`` (pure): ``building`` | ``hard`` (a surface, a hedge, steps) | ``bed`` | ``outside`` (off the
    plot) | ``lawn``."""
    if plot and not G.point_in_polygon(p, plot):
        return "outside"
    k = _hit(p, keep)
    if k is not None:
        return "building" if k["kind"] == "building" else ("hard" if k["kind"] in ("hard", "hedge", "walk", "pool")
                                                           else "lawn")
    if any(G.point_in_polygon(p, bd["polygon"]) for bd in beds):
        return "bed"
    return "lawn"


def paved_borders(site: dict, keep: Sequence[dict], beds: Sequence[dict], looks: Optional[dict] = None,
                  cfg: Optional[dict] = None) -> list[dict]:
    """The border bands of the paved areas (pure; rule 3): along every edge of a draped paved area (``paving`` or
    ``parking`` without a platform, and the aprons at the glazed facades), in ``piece_m`` pieces, where the ground
    just outside is lawn or a bed: ``[{"area", "slug", "pieces": [[p0, p1, inward]], "z", "reason"}]``. Paths have
    their own edging (``grading.walk_edging``), platforms their kerbs, walls and copings."""
    from wenart.blender import grading as GR

    cfg = dict(LANDSCAPE, **(cfg or {}))
    plot = plot_of(site)
    floors = GR.floor_set(looks, site.get("style_family"))
    items = []
    for a in site.get("areas") or []:
        if a.get("platform_id") or a.get("kind") not in ("paving", "parking") or len(a.get("polygon") or []) < 3:
            continue
        slug = a.get("material") or floors["terrace" if a["kind"] == "paving" else "drive"].get("material")
        items.append((str(a.get("id")), a["polygon"], a.get("z"), slug))
    for a in site.get("aprons") or []:
        if len(a.get("polygon") or []) >= 3:
            items.append((str(a.get("id")), a["polygon"], None, "concrete"))
    others = [k for k in keep if k["kind"] != "door"]
    out = []
    piece = float(cfg["piece_m"])
    for aid, poly, z, slug in items:
        ring = geom2d.ccw([tuple(map(float, p[:2])) for p in poly])
        n = len(ring)
        mine = [k for k in others if not (k["kind"] == "hard" and _same_ring(k["polygon"], ring))]
        pieces = []
        for e in range(n):
            p, q = ring[e], ring[(e + 1) % n]
            length = G.distance(p, q)
            if length < 0.2:
                continue
            ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
            inward = (-uy, ux)
            k = max(1, int(math.ceil(length / piece)))
            for m in range(k):
                s0, s1 = length * m / k, length * (m + 1) / k
                mid = (p[0] + ux * (s0 + s1) / 2.0, p[1] + uy * (s0 + s1) / 2.0)
                probe = (mid[0] - inward[0] * 0.15, mid[1] - inward[1] * 0.15)
                if _outside_kind(probe, mine, beds, plot) in ("lawn", "bed"):
                    pieces.append([[round(p[0] + ux * s0, 4), round(p[1] + uy * s0, 4)],
                                   [round(p[0] + ux * s1, 4), round(p[1] + uy * s1, 4)],
                                   [round(inward[0], 6), round(inward[1], 6)]])
        if pieces:
            look = border_look(slug)
            out.append({"area": aid, "slug": look, "paving": slug, "pieces": pieces, "z": z,
                        "reason": f"{aid}: a {float(cfg['border_w']) * 100:.0f} cm border band of {look} (a soldier "
                                  f"course contrasting with its {slug}) where it meets the lawn or a bed ({LESSONS}; "
                                  f"inferred)"})
    return out


def _same_ring(a, b, tol: float = 1e-4) -> bool:
    if len(a) != len(b):
        return False
    sa = sorted((round(p[0], 3), round(p[1], 3)) for p in a)
    sb = sorted((round(p[0], 3), round(p[1], 3)) for p in b)
    return all(abs(x[0] - y[0]) <= tol + 1e-3 and abs(x[1] - y[1]) <= tol + 1e-3 for x, y in zip(sa, sb))


def lawn_edges(beds: Sequence[dict], keep: Sequence[dict], plot, cfg: Optional[dict] = None) -> list[dict]:
    """The steel lawn edges of the beds (pure; rule 3): along the outline of every bed (a terraced bank's only where a
    bed meets the ground flush: its walls edge it elsewhere), in ``piece_m`` pieces, where the ground just outside is
    lawn: ``[{"bed", "pieces": [[p0, p1]]}]``."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    piece = float(cfg["piece_m"])
    out = []
    for bd in beds:
        if bd.get("kind") == "terraced":
            pieces = [[list(f["p0"]), list(f["p1"])] for f in bd.get("flush") or []
                      if _outside_kind(_probe_out(f["p0"], f["p1"], bd), keep, beds, plot) == "lawn"]
        else:
            pieces = []
            for poly in bd.get("rects") or [bd["polygon"]]:
                ring = geom2d.ccw(poly)
                n = len(ring)
                for e in range(n):
                    p, q = ring[e], ring[(e + 1) % n]
                    length = G.distance(p, q)
                    if length < 0.05:
                        continue
                    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
                    outn = (uy, -ux)
                    k = max(1, int(math.ceil(length / piece)))
                    for m in range(k):
                        s0, s1 = length * m / k, length * (m + 1) / k
                        mid = (p[0] + ux * (s0 + s1) / 2.0, p[1] + uy * (s0 + s1) / 2.0)
                        probe = (mid[0] + outn[0] * 0.12, mid[1] + outn[1] * 0.12)
                        if any(G.point_in_polygon(probe, r) for r in bd.get("rects") or [bd["polygon"]]):
                            continue
                        if _outside_kind(probe, keep, beds, plot) == "lawn":
                            pieces.append([[round(p[0] + ux * s0, 4), round(p[1] + uy * s0, 4)],
                                           [round(p[0] + ux * s1, 4), round(p[1] + uy * s1, 4)]])
        if pieces:
            out.append({"bed": bd["id"], "pieces": pieces})
    return out


def _probe_out(p0, p1, bed: dict) -> tuple[float, float]:
    """A point 0.12 m outside the bed beyond the edge ``p0``-``p1`` (pure)."""
    mid = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
    length = G.distance(p0, p1) or 1.0
    ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
    for sgn in (1.0, -1.0):
        q = (mid[0] + uy * 0.12 * sgn, mid[1] - ux * 0.12 * sgn)
        if not any(G.point_in_polygon(q, r) for r in bed.get("rects") or []):
            return q
    return mid


# --------------------------------------------------------------------------
# Touches (rule 4)
# --------------------------------------------------------------------------

def _free_spot(p, r: float, keep: Sequence[dict], plot, taken: Sequence[tuple], gz: Optional[Callable],
               kinds: Sequence[str] = NO_PLANT + ("building",)) -> bool:
    if plot and not G.point_in_polygon(p, plot):
        return False
    if _hit(p, keep, kinds=kinds, margin=r):
        return False
    if any(math.hypot(p[0] - x, p[1] - y) < r + rr for x, y, rr in taken):
        return False
    if gz is not None:
        zs = [float(gz(p[0] + dx, p[1] + dy)) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r))]
        if max(zs) - min(zs) > 2 * r * LANDSCAPE["flat_slope"] + 0.03:
            return False
    return True


def entrance_planters(site: dict, keep: Sequence[dict], gz: Callable, taken: list, cfg: Optional[dict] = None) -> list[dict]:
    """A pair of large planters at every entrance (pure; rule 4): beside the landing of each outside door (its steps'
    landing block, else the door's approach), against the facade, each on free, level ground: ``[{"id", "center",
    "z", "door", "reason"}]``."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    pot = cfg["pot"]
    r = float(pot["top"]) / 2.0 * math.sqrt(2.0) + float(pot["clear"])
    plot = plot_of(site)
    landings = {st.get("opening_id"): [b["polygon"] for b in st.get("blocks") or [] if len(b.get("polygon") or []) >= 3]
                for st in (site.get("inferred") or {}).get("steps") or []}
    out = []
    hw, _depth = cfg["door_zone_m"]
    for house in buildings(site):
        for d in house["doors"]:
            f = _facade_of(house["ring"], d["point"])
            if f is None:
                continue
            a, u, on, s = f
            half = hw
            for poly in landings.get(d["id"]) or []:
                ss = [(q[0] - a[0]) * u[0] + (q[1] - a[1]) * u[1] for q in poly]
                half = max(half, max(abs(x - s) for x in ss))
            for side in (-1.0, 1.0):
                for extra in (0.0, 0.25, 0.5):
                    c = _at(a, u, on, s + side * (half + extra + r), 0.12 + r)
                    if _free_spot(c, r, keep, plot, taken, gz):
                        taken.append((c[0], c[1], r))
                        out.append({"id": f"planter_{d['id'].replace(':', '_')}_{'a' if side < 0 else 'b'}",
                                    "center": [round(c[0], 4), round(c[1], 4)], "z": round(float(gz(*c)), 4),
                                    "door": d["id"], "house": house["id"],
                                    "rotation_deg": round(math.degrees(math.atan2(u[1], u[0])), 3),
                                    "reason": f"a large planter beside the landing of entrance {d['id']}, against the "
                                              f"facade, clear of its approach ({LESSONS}; added_by_ai; inferred)"})
                        break
    return out


def terrace_planters(site: dict, keep: Sequence[dict], taken: list, cfg: Optional[dict] = None) -> list[dict]:
    """A large planter at the outer corners of every terrace (pure; rule 4): a primary, flat terrace or pool deck (no
    tier, no raised deck, no covered outdoor space), at its convex corners whose two edges are at least 1.5 m and face
    no building, ``pot_corner_m`` in from both edges, clear of the pool's coping and walkway, the flights, the seating
    and the house; the corners farthest from the house first, ``pots_per_terrace`` at most."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    pot = cfg["pot"]
    r = float(pot["top"]) / 2.0 * math.sqrt(2.0) + float(pot["clear"])
    outline = [tuple(map(float, p[:2])) for p in site.get("outline") or []]
    out = []
    for pf in site.get("platforms") or []:
        if pf.get("parent") or pf.get("elevated") or pf.get("sloped") or pf.get("kind") not in ("terrace", "pool") \
                or pf.get("source") == "outdoor_space" or pf.get("roof") or not isinstance(pf.get("z"), (int, float)):
            continue
        ring = geom2d.ccw([tuple(map(float, p[:2])) for p in pf.get("polygon") or []])
        n = len(ring)
        if n < 3:
            continue
        against = set(pf.get("against_edges") or [])
        cands = []
        for i in range(n):
            prev, cur, nxt = ring[i - 1], ring[i], ring[(i + 1) % n]
            l0, l1 = G.distance(prev, cur), G.distance(cur, nxt)
            if l0 < 1.5 or l1 < 1.5 or ((i - 1) % n) in against or i in against:
                continue
            cross = (cur[0] - prev[0]) * (nxt[1] - cur[1]) - (cur[1] - prev[1]) * (nxt[0] - cur[0])
            if cross <= 1e-9:
                continue                                  # a reflex corner
            e0 = ((cur[0] - prev[0]) / l0, (cur[1] - prev[1]) / l0)
            e1 = ((nxt[0] - cur[0]) / l1, (nxt[1] - cur[1]) / l1)
            d = float(cfg["pot_corner_m"])
            c = (cur[0] - e0[0] * d + e1[0] * d, cur[1] - e0[1] * d + e1[1] * d)
            if not G.point_in_polygon(c, ring) or any(G.point_in_polygon(c, h) for h in pf.get("holes") or []
                                                       if len(h) >= 3):
                continue
            far = min((geom2d.distance_to_polygon_edges(c, outline) if len(outline) >= 3 else 99.0), 99.0)
            cands.append((-round(far, 3), i, c))
        own = (f"platform:{pf['id']}", f"area:{pf['id']}", f"area:{pf.get('area_id')}")
        blocks = [k for k in keep if k["kind"] != "bank_zone" and k.get("src") not in own]
        placed = 0
        for _far, i, c in sorted(cands):
            if placed >= int(cfg["pots_per_terrace"]):
                break
            if _hit(c, blocks, margin=r) or any(math.hypot(c[0] - x, c[1] - y) < r + rr for x, y, rr in taken):
                continue
            taken.append((c[0], c[1], r))
            out.append({"id": f"planter_{pf['id']}_{i}", "center": [round(c[0], 4), round(c[1], 4)],
                        "z": round(float(pf["z"]), 4), "platform": pf["id"], "rotation_deg": 0.0,
                        "reason": f"a large planter at the outer corner {i} of {pf['id']}, {cfg['pot_corner_m']:.2f} m "
                                  f"in from its edges, clear of the pool's coping and walkway, its flights and seating "
                                  f"({LESSONS}; added_by_ai; inferred)"})
            placed += 1
    return out


def path_lights(site: dict, keep: Sequence[dict], gz: Callable, taken: list, cfg: Optional[dict] = None) -> list[dict]:
    """Low garden lights along the paths and at the flights (pure; rule 4): a bollard every ``light_pitch_m`` along
    every path, ``light_offset_m`` past its edge on the side with more free spots (``light_end_m`` from its ends), and
    one beside the foot landing of every flight down from a platform; each on free ground, never in a walkway:
    ``[{"id", "center", "z", "along", "reason"}]``."""
    from wenart.blender import grading as GR

    cfg = dict(LANDSCAPE, **(cfg or {}))
    lt = cfg["light"]
    r = float(lt["size"]) / 2.0 + 0.05
    plot = plot_of(site)
    out = []
    try:
        recs = [rec for rec in GR.graded_paths(site) if len(rec.get("polygon") or []) >= 3]
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        recs = []
    for rec in recs:
        fr = rec.get("frame") or GR.strip_frame(rec.get("polygon") or [])
        if fr is None or fr["length"] < 1.5:
            continue
        half = fr["width"] / 2.0 + GR.GRADE["edging_t"] + float(cfg["light_offset_m"])
        end = float(cfg["light_end_m"])
        k = max(1, int(math.floor((fr["length"] - 2 * end) / float(cfg["light_pitch_m"]))) + 1)
        ts = [end + (fr["length"] - 2 * end) * q / max(1, k - 1) for q in range(k)] if k > 1 else [fr["length"] / 2.0]
        best = None
        for side in (1.0, -1.0):
            good, mine = [], list(taken)
            for t in ts:
                for dt in (0.0, 0.4, -0.4, 0.8, -0.8):
                    if not end - 1e-9 <= t + dt <= fr["length"] - end + 1e-9:
                        continue
                    p = GR._at(fr, t + dt, side * half)
                    if _free_spot(p, r, keep, plot, mine, gz):
                        good.append(p)
                        mine.append((p[0], p[1], r))
                        break
            if best is None or len(good) > len(best):
                best = good
        for q, p in enumerate(best or []):
            taken.append((p[0], p[1], r))
            out.append({"id": f"light_{rec.get('id')}_{q + 1}", "center": [round(p[0], 4), round(p[1], 4)],
                        "z": round(float(gz(*p)), 4), "along": rec.get("id"),
                        "reason": f"a low garden light (bollard) along path {rec.get('id')}, every "
                                  f"{float(cfg['light_pitch_m']):.1f} m beside its edge ({LESSONS}; added_by_ai; "
                                  f"inferred)"})
    for pf in site.get("platforms") or []:
        if pf.get("steps_edge") is None or pf.get("steps_dir") == "up" or pf.get("parent"):
            continue
        fl = GR.down_flight(pf, gz)
        if fl is None or int(fl.get("count") or 0) < 2:
            continue
        o, mid = fl["out"], fl["mid"]
        side_w = float(fl["half_w"]) + float(GR.GRADE["cheek_t"]) + float(cfg["light_offset_m"])
        along = float(fl.get("end") or 0.0) + float(GR.GRADE["foot_m"]) / 2.0
        for side in (1.0, -1.0):
            ux, uy = -o[1], o[0]
            c = (mid[0] + o[0] * along + ux * side * side_w, mid[1] + o[1] * along + uy * side * side_w)
            if _free_spot(c, r, keep, plot, taken, gz):
                taken.append((c[0], c[1], r))
                out.append({"id": f"light_{pf['id']}_steps", "center": [round(c[0], 4), round(c[1], 4)],
                            "z": round(float(gz(*c)), 4), "along": f"flight:{pf['id']}",
                            "reason": f"a low garden light beside the foot of the flight down from {pf['id']} "
                                      f"({LESSONS}; added_by_ai; inferred)"})
                break
    return out


def lawn_feature(site: dict, keep: Sequence[dict], beds: Sequence[dict], gz: Callable, taken: list,
                 cfg: Optional[dict] = None) -> tuple[Optional[dict], list[dict]]:
    """A feature tree with a few boulders in a large lawn (pure; rule 4): the lawn points (``lawn_step_m`` grid in the
    plot, off every keep-out, bed and bank, ``lawn_facade_m`` from the house, on gentle ground) joined side by side; in
    the largest group of at least ``lawn_min_m2`` with no tree yet, at its point farthest from everything when that is
    at least ``lawn_tree_clear_m``: ``(tree, boulders)`` (the tree a plan tree record of the climate's small class)."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    plot = plot_of(site)
    if len(plot) < 3:
        return None, []
    step = float(cfg["lawn_step_m"])
    x0, y0, x1, y1 = _bbox(plot)
    trees = [(float(t["center"][0]), float(t["center"][1])) for t in site.get("trees") or [] if t.get("center")]
    pts = {}
    for i in range(int(math.floor(x0 / step)), int(math.ceil(x1 / step)) + 1):
        for j in range(int(math.floor(y0 / step)), int(math.ceil(y1 / step)) + 1):
            p = (i * step, j * step)
            if not G.point_in_polygon(p, plot) or geom2d.distance_to_polygon_edges(p, plot) < 1.5:
                continue
            if _hit(p, keep, kinds=NO_PLANT, margin=1.0) or _hit(p, keep, kinds=("building",),
                                                                 margin=float(cfg["lawn_facade_m"])):
                continue
            if any(G.point_in_polygon(p, bd["polygon"]) or geom2d.distance_to_polygon_edges(p, bd["polygon"]) < 1.0
                   for bd in beds):
                continue
            pts[(i, j)] = p
    if not pts:
        return None, []
    groups, seen = [], set()
    for start in sorted(pts):
        if start in seen:
            continue
        comp, todo = [], [start]
        seen.add(start)
        while todo:
            cur = todo.pop()
            comp.append(cur)
            for nb in ((cur[0] + 1, cur[1]), (cur[0] - 1, cur[1]), (cur[0], cur[1] + 1), (cur[0], cur[1] - 1)):
                if nb in pts and nb not in seen:
                    seen.add(nb)
                    todo.append(nb)
        groups.append(sorted(comp))
    groups.sort(key=lambda g: (-len(g), g[0]))
    for g in groups:
        if len(g) * step * step < float(cfg["lawn_min_m2"]):
            break
        ids = set(g)
        inner = [k for k in g if all(nb in ids for nb in ((k[0] + 1, k[1]), (k[0] - 1, k[1]), (k[0], k[1] + 1),
                                                            (k[0], k[1] - 1)))]
        if any(G.point_in_polygon(t, geom2d.ccw(geom2d.convex_hull([pts[k] for k in g]))) for t in trees
               if len(g) >= 3):
            continue                                      # a tree stands in this lawn already
        rim = [pts[m] for m in g if any(nb not in ids for nb in ((m[0] + 1, m[1]), (m[0] - 1, m[1]),
                                                                 (m[0], m[1] + 1), (m[0], m[1] - 1)))]
        best, best_d = None, -1.0
        for k in inner or g:
            p = pts[k]
            # the clearance: to the lawn's rim (every point past it is blocked or another lawn) plus a grid step
            d = min((math.hypot(p[0] - q[0], p[1] - q[1]) + step for q in rim), default=99.0)
            if d > best_d + 1e-9:
                best, best_d = p, d
        if best is None or best_d < float(cfg["lawn_tree_clear_m"]):
            continue
        crown = float(cfg["feature_crown_m"])
        tree = {"id": f"ls_lawn_tree_{len(g)}", "kind": "tree", "center": [round(best[0], 4), round(best[1], 4)],
                "size": [crown, crown], "inferred": True, "source": SOURCE, "build": True, "added_by_ai": True,
                "role": "feature", "parent": "lawn",
                "reason": f"a feature tree in the middle of a lawn of {len(g) * step * step:.0f} m² ({best_d:.1f} m clear "
                          f"of everything; species by the climate; {LESSONS}; inferred)"}
        taken.append((best[0], best[1], crown / 2.0))
        boulders = []
        for q, (ang, size) in enumerate(((210.0, (0.9, 0.7, 0.5)), (250.0, (0.6, 0.5, 0.35)), (300.0, (0.45, 0.4, 0.3)))):
            c = (best[0] + math.cos(math.radians(ang)) * (crown / 2.0 + 0.4),
                 best[1] + math.sin(math.radians(ang)) * (crown / 2.0 + 0.4))
            if _free_spot(c, size[0] / 2.0, keep, plot, [], None):
                boulders.append({"id": f"boulder_lawn_{q + 1}", "center": [round(c[0], 4), round(c[1], 4)],
                                 "size": list(size), "z": round(float(gz(*c)), 4), "seed": q + 1, "parent": "lawn",
                                 "reason": f"a boulder at the foot of the lawn's feature tree ({LESSONS}; inferred)"})
        return tree, boulders
    return None, []


def bank_boulders(bank: dict, bed: dict, gz: Callable, planter: _Planter, cfg: Optional[dict] = None) -> list[dict]:
    """Accent boulders on a large planted bank (pure; rule 4): up to ``boulders_per_bank`` on a bank of at least
    ``boulder_bank_m2``, in its widest rectangles' middles, half buried in the slope, clear of the plants."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    if bank["finish"] != "planted" or float(bank["area_m2"]) < float(cfg["boulder_bank_m2"]) - 1e-9:
        return []
    o, u, v = _frame_of(bank)
    c = float(bank["cell_m"])
    rects = sorted(cells_to_rects(bank["cells"]), key=lambda r: (-(r[1] - r[0] + 1) * (r[3] - r[2] + 1), r))
    out = []
    for q, (i0, i1, j0, j1) in enumerate(rects[:int(cfg["boulders_per_bank"])]):
        s = (i0 + i1 + 1) * c / 2.0 + (0.6 if q % 2 else -0.6)
        t = (j0 + j1 + 1) * c / 2.0
        p = _at(o, u, v, s, t)
        size = (0.8, 0.6, 0.45) if q == 0 else (0.55, 0.45, 0.32)
        if not planter.free(p, size[0] / 2.0):
            continue
        planter.block(p, size[0] / 2.0)
        out.append({"id": f"boulder_{bank['id']}_{q + 1}", "center": [round(p[0], 4), round(p[1], 4)],
                    "size": list(size), "z": round(float(gz(*p)), 4), "seed": 11 + q, "parent": bank["id"],
                    "reason": f"an accent boulder half buried in the planted bank {bank['id']} ({LESSONS}; inferred)"})
    return out


# --------------------------------------------------------------------------
# The plan
# --------------------------------------------------------------------------

def plan(site: dict, looks: Optional[dict] = None, cfg: Optional[dict] = None) -> dict:
    """The landscape of a site plan (pure; the module docstring): writes ``site["landscape"]`` and appends its plants
    and its feature tree to ``site["trees"]`` (a second call replaces the first's), stands the drawn plants of a
    terraced bank on their bed. Returns the landscape record: ``{"rules", "terrain_finish", "banks", "beds",
    "borders", "edges", "planters", "lights", "boulders", "plants", "species", "notes"}``."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    cfg = dict(LANDSCAPE, **(cfg or {}))
    site["trees"] = [t for t in site.get("trees") or [] if t.get("source") != SOURCE]
    for t in site["trees"]:
        if (t.get("stand") or {}).get("by") == SOURCE:
            t.pop("stand", None)
            t.pop("z", None)
    rec: dict = {"rules": ["the terrain is never paved", "a bank is planted (terraced when steep)",
                           "paved areas get a border band, beds a lawn edge, beds along the house and the paths",
                           "planters at entrances and terrace corners, lights along paths and steps, a tree in a large "
                           "lawn"],
                 "lessons": LESSONS, "banks": [], "beds": [], "borders": [], "edges": [], "planters": [], "lights": [],
                 "boulders": [], "plants": [], "notes": []}
    site["landscape"] = rec
    terrain = GR.plan_terrain(site)
    if site.get("mode") != "full" or not terrain:
        rec["notes"].append("no landscape: the site is not built in full")
        return rec
    if not (site.get("levers") or S.site_levers()).get("landscape", True):
        rec["notes"].append(f"no landscape: the site lever 'landscape' is off ({S.SITE_VARIANT_ENV})")
        rec["off"] = True
        return rec
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    keep = KeepIndex(keep_outs(site, terrain))
    plot = plot_of(site)
    species = planting_species(site)
    rec["species"] = species
    planter = _Planter(site, keep, species, cfg)
    taken: list = []
    # rule 4 first (the planters and lights claim their spots before the beds' plants)
    rec["planters"] = entrance_planters(site, keep, gz, taken, cfg) + terrace_planters(site, keep, taken, cfg)
    rec["lights"] = path_lights(site, keep, gz, taken, cfg)
    for x, y, r in taken:
        planter.block((x, y), r)
    # rule 2: the banks
    beds: list[dict] = []
    for found in find_banks(site, keep, terrain, cfg):
        brec = {k: found[k] for k in ("id", "area_m2", "z_range", "rise_m", "slope_max", "slope_p75", "finish",
                                      "reason", "frame", "cell_m", "cells", "downhill")}
        bank = refine_bank(found, gz) if found["finish"] == "terraced" else found
        o, u, v = _frame_of(bank)
        c = float(bank["cell_m"])
        bed = {"id": bank["id"], "kind": bank["finish"], "frame": bank["frame"], "cell_m": c,
               "rects": bank_rects(bank), "bank": bank["id"]}
        bed["polygon"] = bed["rects"][0]
        if bank["finish"] == "terraced":
            terr = terrace_plan(bank, cfg)
            walls, flush = terrace_walls(bank, terr, gz, cfg)
            bed["flush"] = flush
            bed["tiers"] = []
            for tb in terr["beds"]:
                rects = cells_to_rects(tb["cells"])
                bed["tiers"].append({"tier": tb["tier"], "level": tb["level"],
                                     "rects": [_rect(o, u, v, i0 * c, (i1 + 1) * c, j0 * c, (j1 + 1) * c)
                                               for i0, i1, j0, j1 in rects],
                                     "bottom": round(min(_cz(bank, i, j) for ci, cj in tb["cells"]
                                                         for i, j in ((ci, cj), (ci + 1, cj), (ci, cj + 1),
                                                                      (ci + 1, cj + 1))) - float(cfg["below_m"]), 4)})
            bed["walls"] = merge_runs(walls)
            brec.update(tiers=terr["tiers"], step_m=terr["step_m"], levels=terr["levels"], walls=len(bed["walls"]))
            surface = float(cfg["bed_drop_m"])
            n0 = len(planter.plants)
            for tb, tier in zip(terr["beds"], bed["tiers"]):
                rects = cells_to_rects(tb["cells"])
                bed_plants(planter, {"id": f"{bank['id']}_t{tb['tier'] + 1}"}, [
                    (i0 * c, (i1 + 1) * c, j0 * c, (j1 + 1) * c) for i0, i1, j0, j1 in rects], (o, u, v),
                    f"terraced planting step {tb['tier'] + 1} of {bank['id']}", z=tier["level"] - surface)
            brec["plants"] = len(planter.plants) - n0
            # the drawn plants on a terraced bank stand on their step's bed (their position kept)
            for t in site["trees"]:
                if t.get("source") == SOURCE or not t.get("center"):
                    continue
                p = (float(t["center"][0]), float(t["center"][1]))
                for tier in bed["tiers"]:
                    if any(G.point_in_polygon(p, r) for r in tier["rects"]):
                        z = round(tier["level"] - surface, 4)
                        t["z"] = z
                        t["stand"] = {"by": SOURCE, "z": z, "reason": f"stands on planting step {tier['tier'] + 1} of "
                                                                      f"{bank['id']} (its position as drawn; {LESSONS})"}
                        rec["notes"].append(f"{t.get('id')}: stands on planting step {tier['tier'] + 1} of {bank['id']} "
                                            f"at {z:+.2f} m (position as drawn)")
                        break
        else:
            rec["boulders"] += bank_boulders(bank, bed, gz, planter, cfg)
            n0 = len(planter.plants)
            bed_plants(planter, bed, [(i0 * c, (i1 + 1) * c, j0 * c, (j1 + 1) * c)
                                      for i0, i1, j0, j1 in cells_to_rects(bank["cells"])], (o, u, v),
                       f"planted bank {bank['id']}")
            brec["plants"] = len(planter.plants) - n0
        rec["banks"].append(brec)
        beds.append(bed)
    # rule 3: beds along the house and beside the paths
    bank_blocks = _keep([r for bd in beds for r in bd["rects"]], "bed")
    front = []
    for house in buildings(site):
        ring = house["ring"]
        n = len(ring)
        for e in range(n):
            a, b = ring[e], ring[(e + 1) % n]
            length = G.distance(a, b)
            if length < float(cfg["front_bed_min_m"]):
                continue
            u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
            out_n = (u[1], -u[0])
            # the house blocks only what lies in it: a bed starts 2 cm off its wall
            front += strip_beds(keep, plot, gz, a, b, 0.02, 0.02 + float(cfg["front_bed_m"]), out_n, "front",
                                f"bed_{'facade' if not house['copy'] else house['id']}_{e}",
                                float(cfg["front_bed_min_m"]), float(cfg["piece_m"]), float(cfg["bank_slope"]),
                                bank_blocks + _keep([f["polygon"] for f in front], "bed"))
    for bd in front:
        fr = bd["frame"]
        s0, s1, t0, t1 = bd["rect"]
        bed_plants(planter, bd, [(s0, s1, t0, t1)], (tuple(fr["o"]), tuple(fr["u"]), tuple(fr["v"])),
                   "a planting bed along the house", roles=("groundcover", "grass", "groundcover"),
                   accents=(s1 - s0) >= 3.0)
    beds += front
    side = []
    try:
        recs = [r for r in GR.graded_paths(site) if len(r.get("polygon") or []) >= 3]
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        recs = []
    for prec in recs:
        fr = prec.get("frame") or GR.strip_frame(prec.get("polygon") or [])
        if fr is None or fr["length"] < float(cfg["path_bed_min_m"]) + 2 * float(cfg["path_end_m"]):
            continue
        uu = tuple(fr["u"])
        nn = (-uu[1], uu[0])
        start = GR._at(fr, float(cfg["path_end_m"]), 0.0)
        stop = GR._at(fr, fr["length"] - float(cfg["path_end_m"]), 0.0)
        d0 = fr["width"] / 2.0 + GR.GRADE["edging_t"] + float(cfg["path_bed_gap_m"])
        for sgn in (1.0, -1.0):
            on = (nn[0] * sgn, nn[1] * sgn)
            a, b = (start, stop) if sgn > 0 else (start, stop)
            side += strip_beds(keep, plot, gz, a, b, d0, d0 + float(cfg["path_bed_m"]), on, "path",
                               f"bed_{prec.get('id')}_{'l' if sgn > 0 else 'r'}", float(cfg["path_bed_min_m"]),
                               float(cfg["piece_m"]), float(cfg["bank_slope"]),
                               bank_blocks + _keep([f["polygon"] for f in front + side], "bed"))
    for bd in side:
        fr = bd["frame"]
        s0, s1, t0, t1 = bd["rect"]
        bed_plants(planter, bd, [(s0, s1, t0, t1)], (tuple(fr["o"]), tuple(fr["u"]), tuple(fr["v"])),
                   "a planting bed beside the path", roles=("grass", "groundcover"), accents=False)
    beds += side
    # rule 4: the lawn's feature tree
    tree, boulders = lawn_feature(site, keep, beds, gz, taken, cfg)
    rec["boulders"] += boulders
    # rule 3: the edges
    rec["borders"] = paved_borders(site, keep, beds, looks, cfg)
    rec["edges"] = lawn_edges(beds, keep, plot, cfg)
    for bd in beds:
        out = {k: bd[k] for k in ("id", "kind", "frame") if k in bd}
        out["rects"] = [[list(map(lambda x: round(x, 4), p)) for p in r] for r in bd.get("rects") or [bd["polygon"]]]
        out["area_m2"] = round(sum(G.polygon_area(r) for r in bd.get("rects") or [bd["polygon"]]), 3)
        if bd["kind"] == "terraced":
            out["tiers"] = bd["tiers"]
            out["walls"] = bd["walls"]
            out["flush"] = bd["flush"]
        out["plants"] = sum(1 for p in planter.plants if p["parent"] == bd["id"]
                            or str(p["parent"]).startswith(f"{bd['id']}_t"))
        out["reason"] = (next((b["reason"] for b in rec["banks"] if b["id"] == bd["id"]), None)
                         or (f"a planting bed along the house's facade, {float(cfg['front_bed_m']):.1f} m deep, clear of "
                             f"its doors, light wells and paved strips ({LESSONS}; inferred)" if bd["kind"] == "front"
                             else f"a planting bed beside the path, {float(cfg['path_bed_m']):.1f} m deep, clear of its "
                                  f"joints and the walkways ({LESSONS}; inferred)"))
        rec["beds"].append(out)
    for p in planter.plants:
        site["trees"].append(p)
    rec["plants"] = [p["id"] for p in planter.plants]
    if tree is not None:
        site["trees"].append(tree)
        rec["feature_tree"] = tree["id"]
    for pot in rec["planters"]:
        crown, h = ROLES["potted"]
        sp = planter.pick("potted")
        site["trees"].append({"id": f"ls_{pot['id']}_plant", "kind": "plant", "center": list(pot["center"]),
                              "size": [crown, crown], "height_m": h, "species": sp,
                              "species_inferred": not species["potted"]["named"], "role": "potted",
                              "z": round(float(pot["z"]) + float(cfg["pot"]["height"]) - float(cfg["pot"]["soil"]), 4),
                              "inferred": True, "source": SOURCE, "build": True, "added_by_ai": True,
                              "parent": pot["id"], "reason": f"the shrub in {pot['id']}: {sp} ({LESSONS}; inferred)"})
        pot["plant"] = f"ls_{pot['id']}_plant"
    rec["counts"] = {"banks": len(rec["banks"]), "beds": len(rec["beds"]), "plants": len(planter.plants),
                     "planters": len(rec["planters"]), "lights": len(rec["lights"]), "boulders": len(rec["boulders"]),
                     "borders": sum(len(b["pieces"]) for b in rec["borders"]),
                     "edges": sum(len(e["pieces"]) for e in rec["edges"]),
                     "feature_trees": 1 if tree is not None else 0}
    return rec


def ground_holes(site: dict) -> list[list[tuple[float, float]]]:
    """The landscape's footprints the lawn mesh leaves out (pure): every bed's rectangles (a planted bed is draped in
    their place, a terraced bank stands on its own walls)."""
    out = []
    for bd in (site.get("landscape") or {}).get("beds") or []:
        for r in bd.get("rects") or []:
            if len(r) >= 3:
                out.append(geom2d.ccw([tuple(map(float, p[:2])) for p in r]))
    return out


# --------------------------------------------------------------------------
# Meshes (pure)
# --------------------------------------------------------------------------

def _prism_slots(poly, z0: float, z1: float) -> tuple[list, list, list[int]]:
    """A prism of a convex plan polygon from ``z0`` to ``z1``: ``(verts, faces, slots)``, slot 1 its top, 0 the rest."""
    pts = geom2d.ccw([tuple(map(float, p[:2])) for p in poly])
    k = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces = [list(reversed(range(k))), list(range(k, 2 * k))]
    for j in range(k):
        faces.append([j, (j + 1) % k, k + (j + 1) % k, k + j])
    return verts, faces, [0, 1] + [0] * k


def terraced_meshes(bed: dict, cfg: Optional[dict] = None) -> dict:
    """The parts of a terraced bank (pure): ``{"beds": [(verts, faces, slots)], "walls": [(v, f)], "coping": [(v, f)]}``:
    each tier's bed solids (their top the planting surface ``bed_drop_m`` under the walls, slot 1), the walls (inside
    their cell, ``wall_t`` thick, a cut wall's top following the ground) and the copings on the level walls."""
    from wenart.blender import site as S

    cfg = dict(LANDSCAPE, **(cfg or {}))
    out = {"beds": [], "walls": [], "coping": []}
    for tier in bed.get("tiers") or []:
        for r in tier["rects"]:
            out["beds"].append(_prism_slots(r, float(tier["bottom"]), float(tier["level"]) - float(cfg["bed_drop_m"])))
    t = float(cfg["wall_t"])
    for w in bed.get("walls") or []:
        p0, p1, n = w["p0"], w["p1"], w["inward"]
        length = G.distance(p0, p1)
        if length < 0.02:
            continue
        mid = ((p0[0] + p1[0]) / 2.0 + n[0] * t / 2.0, (p0[1] + p1[1]) / 2.0 + n[1] * t / 2.0)
        ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        out["walls"].append(S.sloped_box(mid, length, t, ang, float(w["bottom"]), float(w["top0"]), float(w["top1"])))
        if w.get("coping"):
            ct, over = float(cfg["coping_t"]), float(cfg["coping_over"])
            cmid = (mid[0] - n[0] * over / 2.0, mid[1] - n[1] * over / 2.0)
            out["coping"].append(geom2d.box((cmid[0], cmid[1], float(w["top0"]) + ct / 2.0),
                                            (length + 2 * over, t + over, ct), ang))
    return out


def strip_pieces(pieces: Sequence, gz: Callable, width: float, up: float, down: float, inward: bool = False,
                 z: Optional[float] = None) -> list[tuple[list, list]]:
    """A thin band along each piece (pure): ``[p0, p1(, inward)]`` pieces, the band ``width`` wide (inside the area
    when ``inward``, centred on the line otherwise), its top ``up`` over the ground (or ``z``) at each end, its foot
    ``down`` under the lower ground."""
    from wenart.blender import grading as GR

    out = []
    for pc in pieces:
        p0, p1 = pc[0], pc[1]
        length = G.distance(p0, p1)
        if length < 0.02:
            continue
        ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
        if inward and len(pc) > 2:
            n = pc[2]
            poly = [tuple(p0), tuple(p1), (p1[0] + n[0] * width, p1[1] + n[1] * width),
                    (p0[0] + n[0] * width, p0[1] + n[1] * width)]
        else:
            nx, ny = -uy * width / 2.0, ux * width / 2.0
            poly = [(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)]
        poly = geom2d.ccw(poly)
        g = [float(z) if z is not None else float(gz(*q)) for q in poly]
        out.append(GR._sloped_prism(poly, min(g) - down, [gv + up for gv in g]))
    return out


def pot_meshes(pot: dict, cfg: Optional[dict] = None) -> dict:
    """A large tapered square planter (pure): ``{"pot": (verts, faces), "soil": (verts, faces)}``: the shell (outer
    sides, rim, inner sides down to the soil) and the soil's top ``soil`` under the rim."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    p = cfg["pot"]
    cx, cy = (float(v) for v in pot["center"][:2])
    z0 = float(pot["z"])
    h, wb, wt, wall, soil = (float(p[k]) for k in ("height", "bottom", "top", "wall", "soil"))
    ang = math.radians(float(pot.get("rotation_deg") or 0.0))
    ca, sa = math.cos(ang), math.sin(ang)

    def sq(half: float, z: float) -> list:
        return [(cx + ca * x - sa * y, cy + sa * x + ca * y, z)
                for x, y in ((-half, -half), (half, -half), (half, half), (-half, half))]

    inner_t = wt / 2.0 - wall
    inner_s = inner_t - wall * 0.3
    verts = sq(wb / 2.0, z0) + sq(wt / 2.0, z0 + h) + sq(inner_t, z0 + h) + sq(inner_s, z0 + h - soil)
    faces = [[3, 2, 1, 0]]
    for k in range(4):
        a, b = k, (k + 1) % 4
        faces.append([a, b, 4 + b, 4 + a])                # outer side
        faces.append([4 + a, 4 + b, 8 + b, 8 + a])        # rim
        faces.append([8 + a, 8 + b, 12 + b, 12 + a])      # inner side
    soil_v = sq(inner_s, z0 + h - soil)
    return {"pot": (verts, faces), "soil": (soil_v, [[0, 1, 2, 3]])}


def bollard_meshes(light: dict, cfg: Optional[dict] = None) -> dict:
    """A low garden bollard (pure): ``{"body": [(v, f)], "lens": [(v, f)]}``: a square post, a light band (lens) and a
    cap."""
    cfg = dict(LANDSCAPE, **(cfg or {}))
    lt = cfg["light"]
    cx, cy = (float(v) for v in light["center"][:2])
    z0 = float(light["z"])
    w = float(lt["size"])
    l0, l1 = (float(v) for v in lt["lens"])
    h, cap, below = float(lt["height"]), float(lt["cap"]), float(lt["below"])
    post = geom2d.box((cx, cy, z0 + (l0 - below) / 2.0), (w, w, l0 + below), 0.0)
    lens = geom2d.box((cx, cy, z0 + (l0 + l1) / 2.0), (w * 0.86, w * 0.86, l1 - l0), 0.0)
    head = geom2d.box((cx, cy, z0 + (l1 + h) / 2.0), (w * 1.08, w * 1.08, h - l1), 0.0)
    top = geom2d.box((cx, cy, z0 + h + cap / 2.0 - 0.01), (w * 1.12, w * 1.12, cap * 0.5), 0.0)
    return {"body": [post, head, top], "lens": [lens]}


def boulder_mesh(b: dict, segments: int = 16, rings: int = 10) -> tuple[list, list]:
    """A boulder (pure; deterministic by its ``seed``): an ellipsoid of its ``size`` (x, y, height) whose radius is
    shaped by a few smooth lobes, flattened on its underside and set a third into the ground."""
    from wenart.blender import site as S

    sx, sy, sz = (float(v) for v in b["size"][:3])
    cx, cy = (float(v) for v in b["center"][:2])
    z0 = float(b["z"])
    seed = int(b.get("seed") or 1)
    cz = z0 + sz * 0.5 - sz * 0.33
    verts, faces = S._sphere((0.0, 0.0, 0.0), 1.0, 1.0, 1.0, segments=segments, rings=rings)
    ph = [((seed * 37 + 11 * k) % 97) / 97.0 * 2 * math.pi for k in range(6)]
    out = []
    for x, y, z in verts:
        th = math.atan2(y, x)
        el = math.asin(max(-1.0, min(1.0, z)))
        m = 1.0 + 0.10 * math.sin(2 * th + ph[0]) * math.cos(el) + 0.07 * math.sin(3 * th + ph[1]) \
            + 0.06 * math.sin(2 * el + ph[2]) + 0.04 * math.sin(5 * th + 3 * el + ph[3])
        zz = z if z > -0.35 else -0.35 - (z + 0.35) * 0.25         # a flatter underside
        out.append((cx + x * m * sx / 2.0, cy + y * m * sy / 2.0, cz + zz * m * sz / 2.0))
    return out, faces


# --------------------------------------------------------------------------
# Review: the model review's G16
# --------------------------------------------------------------------------

def _items(site: dict) -> list[tuple[str, tuple[float, float], float, tuple]]:
    """``[(name, centre, radius, own sources)]`` of the landscape's items (a terrace planter stands on its terrace)."""
    ls = site.get("landscape") or {}
    out = []
    for kind in ("planters", "lights", "boulders"):
        for it in ls.get(kind) or []:
            c = it.get("center")
            if c:
                r = 0.05 if kind == "lights" else 0.1
                own = (f"platform:{it['platform']}", f"area:{it['platform']}") if it.get("platform") else ()
                out.append((f"{kind[:-1]} {it.get('id')}", (float(c[0]), float(c[1])), r, own))
    for t in site.get("trees") or []:
        if t.get("source") == SOURCE and t.get("center") and t.get("role") != "potted":
            out.append((f"plant {t.get('id')}", (float(t["center"][0]), float(t["center"][1])), 0.0, ()))
    return out


def review(site: Optional[dict], manifest: Optional[dict] = None) -> tuple[list[dict], int]:
    """G16 (pure; ``site_sense.review`` runs it): the terrain is never paved (the plan's garden look, the scene
    manifest's ground material), every bank of the terrain is planted (``find_banks`` against the plan's
    ``landscape.banks``), nothing of the landscape stands in a walkway (a path, a paved area, a landing, a door's
    approach, a drive, a flight, a pool's coping or walkway), a paved area meets the lawn with a border band, an
    entrance has its planters and a path its lights where the plan found room. Returns ``(findings, checked)``."""
    from wenart.blender import grading as GR

    if not site or not site.get("terrain") or site.get("mode") != "full":
        return [], 0
    findings: list[dict] = []
    checked = 0
    ls = site.get("landscape")
    ground = None
    for o in (manifest or {}).get("objects") or []:
        if o.get("kind") == "terrain" and o.get("name") == "ground":
            ground = o.get("material")
            break
    if ground is None and isinstance(ls, dict):
        ground = (ls.get("terrain_finish") or {}).get("material")
    if ground is not None:
        checked += 1
        if not is_soft(ground):
            findings.append(GR._f("major", "ground", f"the terrain is paved ({str(ground).split('__')[0]}): the garden, "
                                  f"its banks and the fields stay soft (lawn or gravel); paving belongs on the paths and "
                                  f"terraces", CHECK_RULE, "taste", material=ground, lesson="UL248"))
    if isinstance(ls, dict) and ls.get("off"):
        return findings, checked                        # the A/B variant without the landscape (site lever off)
    keep = keep_outs(site)
    banks = find_banks(site, keep)
    planned = {b["id"]: b for b in (ls or {}).get("banks") or []}
    for b in banks:
        checked += 1
        p = planned.get(b["id"])
        cells = {tuple(c) for c in b["cells"]}
        same = p is not None and {tuple(c) for c in p.get("cells") or []} == cells
        rects = bank_rects(b) if same and not (p.get("plants") or p.get("walls")) else []
        drawn = any(t.get("center") and any(G.point_in_polygon(tuple(map(float, t["center"][:2])), r) for r in rects)
                    for t in site.get("trees") or [] if t.get("source") != SOURCE)
        if not same or not (p.get("plants") or p.get("walls") or drawn):
            findings.append(GR._f("major", b["id"], f"{b['id']}: a bank of {b['area_m2']:.1f} m² rising {b['rise_m']:.2f} m "
                                  f"at up to 1:{1.0 / max(b['slope_max'], 1e-6):.1f} is bare terrain (a slope between "
                                  f"levels is planted, terraced when steeper than 1:2, never paved)", CHECK_RULE, "taste",
                                  area_m2=b["area_m2"], rise_m=b["rise_m"], lesson="UL248"))
    walk = [k for k in keep if k["kind"] in WALKWAYS]
    for name, c, r, own in _items(site):
        checked += 1
        k = _hit(c, [w for w in walk if w.get("src") not in own], margin=r)
        if k is not None:
            findings.append(GR._f("major", name.split(" ", 1)[-1], f"{name} stands in a walkway ({k['kind']}: a path, a "
                                  f"paved area, a landing, a door's approach, a flight or a pool's walkway)", CHECK_RULE,
                                  "no_sense", thing=name, lesson="UL249"))
    if isinstance(ls, dict):
        bordered = {b["area"] for b in ls.get("borders") or []}
        for b in paved_borders(site, keep, [{"id": bd["id"], "polygon": bd["rects"][0]} for bd in ls.get("beds") or []
                                            if bd.get("rects")]):
            checked += 1
            if b["area"] not in bordered:
                findings.append(GR._f("minor", b["area"], f"paved area {b['area']} ends raw in the lawn: a border band "
                                      f"(a soldier course) where it meets the lawn or a bed", CHECK_RULE, "taste",
                                      lesson="UL249"))
    return findings, checked
