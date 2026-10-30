"""The garden on a slope as a landscape architect lays it out, and the outdoor floors as one designed set (28 Oct 2026).

Three user messages of 28 Oct 2026 on real04 run 20261028-005318-full (twin villas on a slope falling about 1:4 to
the south-west, pool terraces at -3.0 m and 0.0 m):

- "There could be better outside solutions to the grade slope": on the slope between the pool terrace and the
  garden the renders (ext_5, ext_7) showed bare concrete box planters stacked like stairs, steps that cut through
  boxes, a tilted paved ramp running diagonally down the slope with a strip of lawn inside it and grey retaining walls;
- "Better solutions needed for the elevation difference outside": a bare concrete retaining box beside the terrace
  with loose concrete bars lying across the grass like floating step treads;
- "I am not liking this is the only outside flooring": the garden path, the entrance steps, the terraces and the drive
  all in the same large grey slabs with mossy joints (``paving``, Poly Haven large_square_pattern_01).

The causes, measured on the CPU on the run's own plan (``build.prepare`` of its building_final.json reproduces the 28
platform records of its scene manifest exactly):

- the stepped terraces (``site.stepped_bands``) were planned per 3 m edge piece, each piece with its own step
  (``difference / count``): sp_001's west side got six bands side by side at -3.66, -3.91, -4.16, -4.06, -4.02 and
  -3.92 m, 1.2 m wide, each a box with walls of 0.1-0.3 m between them, and a second row at -5.31, -5.12 and -5.04 m;
  their tops were lawn with nothing planted; the band ends were left open where the neighbour had no band at that
  level (the slab's bare side);
- the platform flights (``site.platform_parts``) ran ``ceil(drop / 0.16)`` treads straight out from the edge's lowest
  ground, never checked against the ground they stand on: every tread of sp_001's and sp_004's flights was buried 5-23
  cm at its high side by the cross-falling slope (no ground hole, no cheek walls), so the lawn and the near-camera grass
  clumps showed between them, and the edge's retaining wall ran across the top of the flight;
- the architect's access paths (``architect.path_areas``, A2) were draped on the terrain: path_access_sp_001_1 rose
  2.9 m over 11.5 m (25 %) with a 31 % cross fall, path_access_sp_004_1 23 % with 18 % across, the entrance paths 14-15
  % (the "tilted paved ramp");
- the retaining walls were ``concrete_exposed`` without a coping (``site.PLATFORM_LOOKS``), while the house's base is
  stone (the facade scheme's ``stone_wall_ledgestone`` on the basement);
- every outdoor floor took ``looks["paving"]`` (``site.AREA_LOOKS``: paving, parking and path all "paving"; the steps
  ``looks["steps"] or looks["paving"]``).

What (pure Python on dicts, no shapely: it runs inside Blender too; general rules for every project, the project is
only the test case):

- ``run_steps``: consecutive platform edges stepped the same way are one terrace run; its bands share their levels
  (the run's largest difference over its count), so a side of a terrace steps down in continuous terraces, one level
  per tier; ``close_band_ends``: a band end with no band of its level beyond it gets a wall (never a bare slab side);
  ``tier_plants``: every tier is a planted bed (inferred shrubs along its middle, clear of the flights and hedges);
- ``down_flight``: a flight down from a platform runs out until its last riser lands on the ground at its foot (the
  levels' outdoor rules, ``wenart.levels.model.steps_for``: risers of at most 0.15 m, the step rule, a landing every 12
  risers, cheek walls and handrails over 0.45 m), each tread a solid block on the one below and the ground, cheek walls
  on both sides at least 0.05 m over the ground beside them, a landing pad at its foot at the highest ground under it,
  its footprint a hole in the ground (no grass between the treads) and a keep-out of its terrace's bands (no steps
  through a planter);
- ``plan_embankments`` / ``grade_z``: where the ground can be graded (a level difference up to ``embank_max_m``, room
  inside the plot, clear of the house, the other platforms, the pools and the hedges, and a natural slope gentler than
  the bank) a platform edge meets the ground by a lawn bank of at most 1:3, else a planted bank of at most 1:2; the
  terrain model carries the banks (``terrain["grading"]``), so the ground mesh, the walls, the plants and the cameras
  all see the same graded ground; a bank end that cannot run on gets a wing wall;
- ``path_plan`` / ``path_meshes``: a path is laid level across; up to 1:20 along and 2.5 % across it stays a walk on
  the ground (with an edging where it meets the lawn); up to 1:12 a sloped walk; steeper it is a stepped path of
  landings and short flights (each riser a stone step edge, edge walls where the ground beside stands higher, an edging
  elsewhere, a handrail on a flight over 0.45 m); a ramp (at most the levels' ramp slope for its rise, landings, rails
  on both sides) only on a route the brief makes accessible (an entrance with a ramp);
- ``wall_look``: retaining walls, cheek walls and wing walls take the house's base (the documents' basement face, else
  the style family's base cladding); every wall gets a coping;
- ``floor_set``: the outdoor floors by use and style family (``FLOOR_SETS``): terrace and pool deck, steps and copings,
  garden path, drive and parking, the edging; a drawn material and a style or brief paving word win;
- ``review``: the model review's M15 (rules G1-G7) finds crude grading in every future run: bare or staggered tiers,
  treads that do not sit on their risers or the ground or stand buried, steps through planters, walls or hedges, paths
  steeper than the rule, ramps steeper than their rise allows, banks steeper than their finish, bare concrete or
  uncoped walls, and a site whose every outdoor floor has one look.

Everything inferred is marked ``inferred`` with its reason (the platform and plant records, the site plan's
``assumed`` entries, the scene manifest's site block); the drawn pools, terraces, flights, level marks and materials
stay as drawn.
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

GRADE = {
    # banks: the steepest slope (rise per run) each finish holds without a wall (lawn mown at 1:3, ground cover 1:2)
    "lawn_slope": 1.0 / 3.0, "planted_slope": 1.0 / 2.0,
    "embank_max_m": 1.2,            # a taller difference is held by walls and terraces (= site.RETAINING_MAX_M)
    "embank_reach_m": 6.0,          # a bank that has not met the ground this far out is a hill: walls instead
    "embank_facade_m": 1.0,         # no grading this close to the building (light wells, basement windows, plinth)
    "embank_margin_m": 0.3,         # the zone is checked this far past the bank's toe
    "embank_pass_m": 1.5,           # ... and a way past it this wide beyond (a bank never closes a passage: real04's
                                    # bank on sp_001's north edge filled the gap between the villas, no path could pass)
    "embank_sample_m": 0.5, "embank_min_m": 1.0, "embank_share": 0.5,
    # paths
    "walk_max": 0.05,               # up to 1:20 along ...
    "cross_fall_max": 0.025,        # ... and 2.5 % across a path is a walk on the ground
    "slope_walk_max": 1.0 / 12.0,   # a garden walk slopes at most 1:12 along its length (level across)
    "path_sample_m": 0.25, "window_m": 1.0,
    "garden_tread_m": 0.35,         # a garden step's going (2 R + T of the step rule at least)
    "flight_risers_min": 3,         # a stepped path groups its risers in flights of at least 3 (never a lone step)
    "landing_min_m": 1.2, "riser_edge_m": 0.10, "end_landing_m": 1.2,
    "edge_wall_from_m": 0.05, "edge_t": 0.15, "edging_t": 0.06, "edging_up": 0.03, "edging_down": 0.12,
    "ramp_run_m": 9.0, "ramp_landing_m": 1.5,
    # terraces
    "plant_pitch_m": 1.4, "plant_crown_m": 0.7, "plant_clear_m": 0.45, "plants_max": 80,
    # flights and walls
    "foot_m": 1.0, "cheek_t": 0.15, "cheek_over_ground_m": 0.05, "coping_t": 0.05, "coping_over": 0.03,
    "tread_tol_m": 0.02,
}
CHECK = "M15"
RULES = {
    "G1": "terraces: every tier planted, the tiers of one side at one level each",
    "G2": "steps: every tread on its riser and the ground, never buried, never through a planter, wall or hedge",
    "G3": "paths: level across, at most 1:12 along unless stepped with landings",
    "G4": "ramps: only on an accessible route, at most the ramp slope of their rise",
    "G5": "banks: at most 1:3 for lawn, 1:2 planted",
    "G6": "walls: the house's base stone (never bare concrete) with a coping",
    "G7": "floors: each use its own material (terrace, steps, path, drive), never one look everywhere",
    # 30 Oct 2026 (wenart.blender.site_sense, pool_extras)
    "G8": "no stray fragments: a flight onto a surface is cut into it, a path ends where it arrives, no kerb between "
          "two surfaces",
    "G9": "a flight never meets a wall or a block and ends on a landing or the ground",
    "G10": "an outdoor stair has one continuous handrail on its open side, on posts on its steps",
    "G11": "every pool has a ladder, a deck with room has seating",
    "G12": "the paved strip at the foot of a glazed facade runs its whole glazing run",
}
CONCRETE_SLUGS = ("concrete_exposed", "concrete", "concrete_polished")

# The outdoor floors by style family (vocabulary slugs of wenart/style, each with a CC0 texture set):
# (terrace and pool deck, steps / copings / edging, garden path, drive and parking). A family not listed takes default.
FLOOR_SETS = {
    "default": ("paving_stone", "paving_stone", "gravel", "paving"),
    "modern": ("paving_stone", "paving_stone", "gravel", "paving"),
    "contemporary": ("paving_stone", "paving_stone", "gravel", "paving"),
    "modern minimal": ("tiles_large_porcelain", "paving_stone", "gravel", "paving"),
    "minimal": ("tiles_large_porcelain", "paving_stone", "gravel", "paving"),
    "scandinavian": ("decking", "paving_stone", "gravel", "paving"),
    "japandi": ("decking", "slate_floor", "gravel", "paving"),
    "industrial": ("slate_floor", "slate_floor", "gravel", "paving"),
    "mediterranean": ("travertine", "travertine", "terracotta", "paving_stone"),
    "classic": ("limestone", "limestone", "brick_red", "paving"),
    "rustic": ("paving_stone", "paving_stone", "gravel", "gravel"),
}
FLOOR_USES = ("terrace", "pool_deck", "steps", "path", "drive", "edging")


# --------------------------------------------------------------------------
# Looks
# --------------------------------------------------------------------------

def _family(style_family) -> str:
    fam = str(style_family or "").strip().lower()
    return fam if fam in FLOOR_SETS else "default"


def wall_look(building: dict, style_family: Optional[str] = None) -> dict:
    """The look of the site's retaining walls, cheek walls and wing walls (pure): the house's base, so the walls
    and the plinth are one material. A facade face the documents give the lowest level (``facade.faces`` with its
    ``level_id``, not inferred) first, else the style family's base cladding (``facade.FACADE_SCHEMES``: what the
    build puts on a basement), else the family's plinth (``facade.ARTICULATION``)."""
    from wenart.blender import facade as FA

    levels = sorted((lv for lv in building.get("levels") or [] if isinstance(lv, dict) and lv.get("id")),
                    key=lambda lv: float(lv.get("elevation") or 0.0))
    lowest = levels[0]["id"] if levels else None
    for f in ((building.get("facade") or {}).get("faces") or []) if isinstance(building.get("facade"), dict) else []:
        if isinstance(f, dict) and f.get("material") and f.get("level_id") == lowest and not f.get("inferred") \
                and f.get("source") != "inferred":
            return {"material": f["material"], "colour": f.get("colour"), "source": "documents", "assumed": False,
                    "reason": f"site walls: the drawn finish of the lowest level {lowest} ({f['material']}), one "
                              f"material with the house's base"}
    sch = FA.scheme_of({"family": style_family} if style_family else None)
    base = sch.get("base") or FA.ARTICULATION.get(_family(style_family), FA.ARTICULATION["default"])["plinth"]
    return {"material": base, "colour": None, "source": "build", "assumed": True,
            "reason": f"site walls: {base}, the base cladding of the {sch.get('family') or 'default'} facade scheme "
                      f"(one material with the house's base; never bare concrete; inferred, nothing drawn)"}


def floor_set(looks: Optional[dict] = None, style_family: Optional[str] = None) -> dict:
    """The outdoor floors by use (pure): ``{use: {"material", "colour", "source", "assumed", "reason"}}`` for the
    ``FLOOR_USES``. The family's set (``FLOOR_SETS``) unless the style or the brief name the paving (``looks
    ["paving"]`` not assumed: the terraces, pool decks and steps take it) or the steps (``looks["steps"]``). A drawn
    area keeps its own material (``site.area_look``)."""
    fam = _family(style_family)
    terrace, steps, path, drive = FLOOR_SETS[fam]
    looks = looks or {}

    def named(slot):
        lk = looks.get(slot)
        if isinstance(lk, dict) and lk.get("material") and not lk.get("assumed") \
                and lk.get("source") in ("documents", "brief", "style"):
            return lk
        return None

    def look(slug, use, why):
        return {"material": slug, "colour": None, "source": "build", "assumed": True,
                "reason": f"{use}: {slug.replace('_', ' ')} ({why}; inferred)"}

    out = {"terrace": look(terrace, "terrace", f"the {fam} floor set: stone or porcelain slabs, a tight joint"),
           "steps": look(steps, "steps", f"the {fam} floor set: solid treads with a tread edge, the copings and "
                                         f"edgings in the same stone"),
           "path": look(path, "garden path", f"the {fam} floor set: a garden path, not the terrace slab"),
           "drive": look(drive, "drive and parking", f"the {fam} floor set: a stronger paver for the cars")}
    p = named("paving")
    if p is not None:
        out["terrace"] = dict(p, reason=f"terrace: {p['material']} ({p.get('reason') or p.get('source')})")
        out["steps"] = dict(p, reason=f"steps: {p['material']}, the terrace floor the style names")
    s = named("steps")
    if s is not None:
        out["steps"] = dict(s, reason=f"steps: {s['material']} ({s.get('reason') or s.get('source')})")
    out["pool_deck"] = dict(out["terrace"], reason=out["terrace"]["reason"].replace("terrace", "pool deck", 1))
    out["edging"] = dict(out["steps"], reason=f"edging where a path meets the lawn: {out['steps']['material']} "
                                               f"(the steps' stone; inferred)")
    out["family"] = fam
    return out


def slab_use(pf: dict) -> str:
    """The floor use of a platform's slab: ``pool_deck``, ``terrace``, ``drive`` (parking) or ``path``."""
    if pf.get("kind") == "parking":
        return "drive"
    if pf.get("kind") == "path":
        return "path"
    return "pool_deck" if pf.get("pools") or pf.get("kind") == "pool" else "terrace"


AREA_USES = {"paving": "terrace", "parking": "drive", "path": "path"}


# --------------------------------------------------------------------------
# The levels' outdoor step rules (wenart.levels.model)
# --------------------------------------------------------------------------

_RULES_CACHE: dict = {}


def level_rules() -> dict:
    """The levels' rules (``wenart.levels.model.level_params`` without a brief: risers, treads, landings, ramps),
    read once (Blender's Python has no PyYAML: the built-in copy)."""
    if not _RULES_CACHE:
        from wenart.levels import rules as LM
        try:
            _RULES_CACHE.update(LM.level_params(None))
        except Exception:  # noqa: BLE001 - the built-in copy of the rules
            _RULES_CACHE.update(LM.BUILTIN_PARAMS)
    return _RULES_CACHE


def _steps_for(rise: float, width: float, rules: dict) -> Optional[dict]:
    from wenart.levels import rules as LM
    return LM.steps_for(rise, width, rules)


# --------------------------------------------------------------------------
# Terraces (site.stepped_bands)
# --------------------------------------------------------------------------

def run_steps(excess: Sequence, cap: float) -> dict:
    """``{edge index: step}``: the step of every stepped edge as part of its run (pure). ``excess[i]`` is ``(direction,
    difference)`` of a stepped edge or None; consecutive stepped edges of one direction (around the polygon, the last
    joining the first) are a run, and every edge of a run steps by the run's largest difference over its count
    (``ceil(difference / cap)``), so the run's bands share their levels: continuous terraces along a side, never a
    staircase of boxes at a new level every 3 m."""
    n = len(excess)
    out: dict = {}
    if n == 0:
        return out
    seen = [False] * n
    start = next((i for i in range(n) if excess[i] is None or excess[i - 1] is None
                  or excess[i - 1][0] != excess[i][0]), None)
    order = list(range(n)) if start is None else [(start + k) % n for k in range(n)]
    runs: list[list[int]] = []
    for i in order:
        if excess[i] is None or seen[i]:
            continue
        run = [i]
        seen[i] = True
        j = (i + 1) % n
        while excess[j] is not None and not seen[j] and excess[j][0] == excess[i][0]:
            run.append(j)
            seen[j] = True
            j = (j + 1) % n
        runs.append(run)
    for run in runs:
        big = max(float(excess[i][1]) for i in run)
        count = max(1, int(math.ceil(big / cap - 1e-9)))
        for i in run:
            out[i] = big / count
    return out


def close_band_ends(bands: Sequence[dict], tol: float) -> int:
    """A band's mitred end is open (``shared_edges``, no wall) only where a band of its level lies beyond it; else it
    gets its wall to the ground (pure; mutates ``shared_edges``, lists ``closed_ends``). Returns the ends closed."""
    closed = 0
    for b in bands:
        poly = b["polygon"]
        n = len(poly)
        inner = b.get("inner_edge")
        keep = []
        for j in b.get("shared_edges") or []:
            if j == inner:
                keep.append(j)
                continue
            a, c = poly[j], poly[(j + 1) % n]
            length = G.distance(a, c)
            if length < 1e-9:
                keep.append(j)
                continue
            m = G.segment_midpoint(a, c)
            nx, ny = (c[1] - a[1]) / length, -(c[0] - a[0]) / length
            probe = (m[0] + nx * 0.05, m[1] + ny * 0.05)
            if any(o is not b and abs(float(o["z"]) - float(b["z"])) <= tol and G.point_in_polygon(probe, o["polygon"])
                   for o in bands):
                keep.append(j)
            else:
                b.setdefault("closed_ends", []).append(j)
                closed += 1
        b["shared_edges"] = keep
    return closed


def _near_any(p, polys, d: float) -> bool:
    for poly in polys:
        if G.point_in_polygon(p, poly) or geom2d.distance_to_polygon_edges(p, poly) < d:
            return True
    return False


def drawn_on(tier: dict, plants: Sequence[dict]) -> list[str]:
    """The ids of the drawn trees and shrubs that stand on a tier (their centre in it or within half a crown of its
    edge): a tier planted by the documents needs no inferred plant."""
    poly = tier.get("polygon") or []
    out = []
    for t in plants or []:
        c = t.get("center")
        if not c or len(poly) < 3:
            continue
        r = max(0.3, max(float(v) for v in (t.get("size") or [1.0, 1.0])[:2])) / 2.0
        if G.point_in_polygon(c[:2], poly) or geom2d.distance_to_polygon_edges(c[:2], poly) <= r:
            out.append(str(t.get("id")))
    return out


def tier_plants(platforms: Sequence[dict], avoid: Sequence = (), pitch: Optional[float] = None,
                crown: Optional[float] = None, limit: Optional[int] = None, existing: Sequence[dict] = ()) -> list[dict]:
    """The planting of every terrace tier and planted bank (pure): shrubs (``kind: plant``) along the tier's middle
    line every ``pitch`` (wider when the site's tiers are too long for ``plants_max`` shrubs: every tier gets at least
    one), clear (``plant_clear_m``) of ``avoid`` (flights, hedges, paths, the drawn plants' crowns). Each tier gets
    ``planting`` (``{"kind": "bed", "plants": [ids], "drawn": [ids], "shared": [ids], "reason"}``: ``drawn`` the
    ``existing`` trees and shrubs of the documents standing on it, ``shared`` a neighbouring tier's shrub at its corner
    when it is too small for one of its own); the plants are ``inferred`` with their reason."""
    pitch = float(pitch or GRADE["plant_pitch_m"])
    crown = float(crown or GRADE["plant_crown_m"])
    limit = int(limit if limit is not None else GRADE["plants_max"])
    clear = GRADE["plant_clear_m"]
    out: list[dict] = []
    keep = [p for p in avoid if len(p or []) >= 3]
    lines = []
    for pf in platforms:
        if pf.get("parent") and len(pf.get("polygon") or []) == 4 and pf.get("inner_edge") is not None:
            q = pf["polygon"]
            i = pf["inner_edge"]
            a_in, b_in = q[i], q[(i + 1) % 4]
            b_out, a_out = q[(i + 2) % 4], q[(i + 3) % 4]
            lines.append((pf, pf["id"], G.segment_midpoint(a_in, a_out), G.segment_midpoint(b_in, b_out), "tier"))
        for k, e in enumerate(pf.get("embankments") or []):
            if e.get("finish") == "planted":
                ax, ay = e["a"]
                ux, uy = e["u"]
                nx, ny = e["n"]
                h = e["width_m"] / 2.0
                lines.append((pf, f"{pf['id']}_bank{k}", (ax + nx * h, ay + ny * h),
                              (ax + ux * e["length_m"] + nx * h, ay + uy * e["length_m"] + ny * h), "bank"))
    total = sum(G.distance(p0, p1) for _pf, _lid, p0, p1, _w in lines)
    # every line gets one shrub; the rest of the budget goes along the lines at the pitch (or wider)
    spare = max(0, limit - len(lines))
    step = max(pitch, total / spare) if spare and total > 0 else max(pitch, total or pitch)
    for pf, lid, p0, p1, what in lines:
        length = G.distance(p0, p1)
        m = max(1, int(length // step))
        ids = []

        def place(c, j):
            pid = f"{lid}_plant{j + 1}"
            ids.append(pid)
            out.append({"id": pid, "kind": "plant", "center": [round(c[0], 4), round(c[1], 4)],
                        "size": [crown, crown], "inferred": True, "source": "planting_bed", "build": True,
                        "parent": pf["id"],
                        "reason": f"planted {'terrace' if what == 'tier' else 'bank'} {lid}: a shrub every "
                                  f"{step:.1f} m along its middle (a landscape architect plants every tier and "
                                  f"bank; species by the climate; inferred, nothing drawn)"})

        for j in range(m):
            if len(out) >= limit:
                break
            c = G.point_along_segment(p0, p1, (j + 0.5) / m)
            if _near_any(c, keep, clear) or any(G.distance(c, o["center"]) < crown for o in out):
                continue
            place(c, j)
        if not ids and len(out) < limit:
            # a short tier (a mitred corner piece) whose middle a neighbour's shrub crowds: another point on it
            for f in (0.25, 0.75, 0.125, 0.875):
                c = G.point_along_segment(p0, p1, f)
                if not _near_any(c, keep, clear) and all(G.distance(c, o["center"]) >= 0.6 * crown for o in out):
                    place(c, m)
                    break
        if what == "tier":
            drawn = drawn_on(pf, existing)
            near = []
            if not ids and not drawn:
                # still none: the shrubs of the neighbouring tiers within half a crown of it plant its corner
                near = [o["id"] for o in out if G.point_in_polygon(o["center"], pf["polygon"])
                        or geom2d.distance_to_polygon_edges(o["center"], pf["polygon"]) <= crown / 2.0]
            pf["planting"] = {"kind": "bed", "plants": ids + drawn + near, "drawn": drawn, "shared": near,
                              "reason": f"a planted bed: {len(ids)} inferred shrub(s) along the tier"
                                        + (f", {len(drawn)} drawn ({', '.join(drawn)})" if drawn else "")
                                        + (f", planted by the neighbouring shrubs {', '.join(near)}" if near else "")}
    return out


# --------------------------------------------------------------------------
# Flights down from a platform
# --------------------------------------------------------------------------

def _rect(origin, d, start: float, end: float, half_w: float) -> list:
    ux, uy = -d[1], d[0]
    return geom2d.ccw([(origin[0] + d[0] * t + ux * s, origin[1] + d[1] * t + uy * s)
                       for t, s in ((start, -half_w), (start, half_w), (end, half_w), (end, -half_w))])


def down_flight(pf: dict, gz: Callable, rules: Optional[dict] = None) -> Optional[dict]:
    """The flight of steps down from a platform's ``steps_edge`` (pure; None for an up flight, a sloped or elevated
    platform or no steps edge): from the middle of the edge (the drawn place, width and tread of ``steps_at``) straight
    out until the last riser lands on the ground: the fewest risers of at most ``riser_max_outdoor`` (the levels'
    outdoor rules: the step rule's tread, a landing every ``landing_every_risers``) whose foot landing lies on the
    highest ground under it (the landing never under the lawn; one riser onto a landing when the ground is near, none
    when the edge meets the ground within 2 cm: None), onto the band of the edge when one is there (``edge_floor``).
    Cheek walls on both sides, each at least ``cheek_over_ground_m`` over the ground beside it (the flight is a hole in
    the lawn); a handrail on both sides over ``handrail_from``.

    ``{"edge", "mid", "out", "half_w", "count", "riser", "tread", "flights", "rise", "top", "foot_z", "blocks":
    [{"polygon", "z_top"}], "cheeks": [{"polygon", "z_top"}], "rails", "posts", "end", "foot": polygon,
    "footprint": polygon (the treads, the cheeks and the foot: a hole in the ground), "landing": the point 0.6 m
    past the last riser, "span": (t0, t1) of the edge the flight takes, "on_band", "reason"}``."""
    from wenart.blender import site as S

    i = pf.get("steps_edge")
    poly = pf.get("polygon") or []
    if i is None or len(poly) < 3 or pf.get("sloped") or pf.get("elevated") or pf.get("steps_dir") == "up":
        return None
    poly = geom2d.ccw(poly)
    n = len(poly)
    if not 0 <= int(i) < n:
        return None
    i = int(i)
    a, b = poly[i], poly[(i + 1) % n]
    length = G.distance(a, b)
    if length < 1e-6:
        return None
    rules = rules or level_rules()
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    out = (uy, -ux)                                       # counter-clockwise: the right side is outside
    mid = G.segment_midpoint(a, b)
    half_w = S.PLATFORM["step_width"] / 2.0
    z = float(pf["z"])
    at = pf.get("steps_at")
    k_drawn, tread_drawn = 0, None
    if at:
        t = (at["point"][0] - a[0]) * ux + (at["point"][1] - a[1]) * uy
        mid = (a[0] + ux * t, a[1] + uy * t)
        half_w = max(0.3, float(at["width"]) / 2.0)
        tread_drawn = float(at.get("tread") or S.PLATFORM["step_tread"])
        k_drawn = int(at.get("treads") or 0) + 1
    floors = pf.get("edge_floor") or {}
    floor = floors.get(str(i), floors.get(i))
    tol = S.PLATFORM["level_tol"]
    foot_m = GRADE["foot_m"]

    def ground_under(poly_):
        c = G.polygon_centroid(poly_)
        return [gz(*q) for q in poly_] + [gz(*c)]

    rmax = float(rules["riser_max_outdoor"])
    land = float(rules["landing_depth"])
    per = max(1, int(rules["landing_every_risers"]))
    rule_min = float(rules["step_rule"][0])

    def layout(n: int, rise: float) -> tuple[float, list[int], float]:
        """(tread, flights, run) of ``n`` risers making up ``rise`` (the step rule's tread, a landing every ``per``)."""
        r = rise / n
        tread = tread_drawn if (tread_drawn and n == k_drawn) else \
            max(float(rules["tread"]), math.ceil((rule_min - 2.0 * r) * 100.0 - 1e-6) / 100.0)
        flights, left = [], n
        while left > 0:
            flights.append(min(per, left))
            left -= flights[-1]
        return tread, flights, (n - len(flights)) * tread + (len(flights) - 1) * land

    def landed(n: int) -> Optional[float]:
        """The rise of a flight of ``n`` risers whose foot landing lies on the highest ground under it."""
        rise = n * rmax
        for _ in range(4):
            _tread, _flights, run = layout(n, max(rise, 1e-3))
            rise = z - max(ground_under(_rect(mid, out, run, run + foot_m, half_w)))
        return rise

    if floor is not None:
        rise = z - float(floor)                          # onto the band of the edge: the band is the foot
        st = _steps_for(rise, 2.0 * half_w, rules)
        if st is None:
            return None
        n = k_drawn if k_drawn > 1 and rise / k_drawn <= S.DRAWN_RISER_MAX_M else int(st["count"])
    else:
        # the fewest risers (each at most riser_max_outdoor) whose foot landing lies on the highest ground under it:
        # the flight follows the ground out until it meets it, never a tread under the lawn
        n, rise = None, None
        tries = [k_drawn] if k_drawn > 1 else []
        for k in tries + list(range(1, 41)):
            got = landed(k)
            if got is None:
                continue
            if k == 1 and got <= 0.02:
                return None                              # the ground is level with the terrace there: no flight
            ok = got > 0.02 and (got / k <= rmax + 1e-6 or (k == k_drawn and got / k <= S.DRAWN_RISER_MAX_M))
            if ok:
                n, rise = k, got
                break
        if n is None:                                    # the ground falls faster than a stair: the longest flight
            n = 40
            rise = max(landed(n), tol + 0.01)
    tread, flights, run = layout(n, rise)
    spec = {"n": n, "riser": rise / n, "tread": tread, "flights": flights, "landing": land,
            "handrails": rise > float(rules["handrail_from"]), "cheeks": True, "top": z, "ground": z - rise}
    parts = S.flight_parts(mid, out, spec, half_w)
    end = parts["end"]
    cheek = GRADE["cheek_t"]
    over = GRADE["cheek_over_ground_m"]
    u = (-out[1], out[0])
    cheeks = []
    blocks = [dict(blk) for blk in parts["blocks"]]
    # the cheeks: one per tread (and the foot), on both sides, at least ``over`` over the ground beside them
    spans = []
    for blk in blocks:
        ts = [(q[0] - mid[0]) * out[0] + (q[1] - mid[1]) * out[1] for q in blk["polygon"]]
        spans.append((min(ts), max(ts), blk["z_top"]))
    spans.append((end, end + foot_m, spec["ground"]))
    # 30 Oct 2026 (lesson UL141): the side of the foot landing a path leaves from (architect.flight_exits) has no
    # cheek: the landing opens onto the path
    open_side = pf.get("foot_open")
    for t0, t1, zt in spans:
        foot = abs(t0 - end) < 1e-9 and abs(t1 - end - foot_m) < 1e-9
        for s0, s1 in ((half_w, half_w + cheek), (-half_w - cheek, -half_w)):
            if foot and open_side == ("left" if s0 > 0 else "right"):
                continue
            cp = geom2d.ccw([(mid[0] + u[0] * s + out[0] * t, mid[1] + u[1] * s + out[1] * t)
                             for s, t in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))])
            g_out = [gz(*q) for q in cp]
            top = max(zt + S.CHEEK["above"], max(g_out) + over)
            cheeks.append({"polygon": cp, "z_top": round(top, 4), "ground_max": round(max(g_out), 4)})
    foot_z = spec["ground"]
    foot_poly = _rect(mid, out, end, end + foot_m, half_w)
    side = half_w + cheek
    footprint = _rect(mid, out, 0.0, end + foot_m, side)
    span = (max(0.0, ((mid[0] - a[0]) * ux + (mid[1] - a[1]) * uy) - side),
            min(length, ((mid[0] - a[0]) * ux + (mid[1] - a[1]) * uy) + side))
    landing = (mid[0] + out[0] * (end + 0.6), mid[1] + out[1] * (end + 0.6))
    reason = (f"a flight of {spec['n']} risers of {spec['riser']:.3f} m, tread {spec['tread']:.2f} m"
              + (f" in {len(spec['flights'])} flights with landings" if len(spec["flights"]) > 1 else "")
              + f" down {z - foot_z:.2f} m from edge {i}"
              + (" onto its band" if floor is not None else " to the ground at its foot (the count settled on the "
                                                             "ground the last riser lands on)")
              + "; each tread a solid block on the one below, cheek walls holding the ground beside it, a landing "
                "at its foot, a hole in the lawn (inferred)")
    return {"edge": i, "mid": (round(mid[0], 4), round(mid[1], 4)), "out": out, "half_w": half_w,
            "count": spec["n"], "riser": round(spec["riser"], 4), "tread": spec["tread"], "flights": spec["flights"],
            "rise": round(z - foot_z, 3), "top": z, "foot_z": round(foot_z, 4), "blocks": blocks, "cheeks": cheeks,
            "rails": parts["rails"] if spec["handrails"] else [], "posts": parts["posts"] if spec["handrails"] else [],
            "end": round(end, 4), "foot": foot_poly, "footprint": footprint, "landing": landing, "span": span,
            "on_band": floor is not None, "handrails": bool(spec["handrails"]), "foot_open": open_side,
            "reason": reason + (f"; its foot landing opens on its {open_side} side onto the path (no cheek there)"
                                if open_side else "")}


def flight_meshes(fl: dict, gz: Callable, below: float) -> dict:
    """The meshes of a ``down_flight`` (pure): ``steps`` (each tread a solid block from ``below`` under the lowest
    ground under it, the foot landing), ``walls`` (the cheek walls, from under the ground to their top) and ``rails``
    (handrails and posts as bars); ``treads``: ``[{"z_top", "z_bottom", "ground_max"}]`` as built (the review)."""
    from wenart.blender import site as S

    steps, walls, rails, treads = [], [], [], []
    for blk in fl["blocks"] + [{"polygon": fl["foot"], "z_top": fl["foot_z"], "foot": True}]:
        g = [gz(*q) for q in blk["polygon"]] + [gz(*G.polygon_centroid(blk["polygon"]))]
        zb = min(min(g), float(blk["z_top"])) - below
        steps.append(geom2d.prism(blk["polygon"], zb, float(blk["z_top"])))
        treads.append({"z_top": round(float(blk["z_top"]), 4), "z_bottom": round(zb, 4), "ground_max": round(max(g), 4),
                       "ground_min": round(min(g), 4), "foot": bool(blk.get("foot")), "in_hole": True})
    for ch in fl["cheeks"]:
        g = [gz(*q) for q in ch["polygon"]]
        walls.append(geom2d.prism(ch["polygon"], min(g) - below, float(ch["z_top"])))
    h = S.HANDRAIL
    rails += [S.bar(p, q, h["rail"], h["rail"]) for p, q in fl.get("rails") or []]
    rails += [S.bar(p, q, h["post"], h["post"]) for p, q in fl.get("posts") or []]
    return {"steps": steps, "walls": walls, "rails": rails, "treads": treads}


# --------------------------------------------------------------------------
# Banks (terrain grading)
# --------------------------------------------------------------------------

def grade_z(grading: Sequence[dict], x: float, y: float, z: float) -> float:
    """The ground ``z`` at ``(x, y)`` with the banks of ``grading`` (pure): a fill bank raises the ground to its
    surface (``z_top`` at the platform edge falling ``slope`` per metre out), a cut bank lowers it; inside the strip of
    its edge piece by the distance out, past an end with a cone (``cone_a`` / ``cone_b``: the neighbouring edge is
    banked too) by the distance to the end, else not at all (a wing wall holds that end)."""
    for g in grading:
        ax, ay = g["a"]
        ux, uy = g["u"]
        nx, ny = g["n"]
        dx, dy = x - ax, y - ay
        q = dx * nx + dy * ny
        if q < -1e-9 or q > g["width_m"]:
            continue
        t = dx * ux + dy * uy
        if t < 0.0:
            if not g.get("cone_a"):
                continue
            d = math.hypot(q, t)
        elif t > g["length_m"]:
            if not g.get("cone_b"):
                continue
            d = math.hypot(q, t - g["length_m"])
        else:
            d = q
        if d > g["width_m"]:
            continue
        if g["fill"]:
            z = max(z, g["z_top"] - d * g["slope"])
        else:
            z = min(z, g["z_top"] + d * g["slope"])
    return z


def graded(gz: Callable, grading: Sequence[dict]) -> Callable:
    """``gz`` with the banks of ``grading`` (``grade_z``)."""
    if not grading:
        return gz
    rows = list(grading)
    return lambda x, y: grade_z(rows, x, y, gz(x, y))


def _bbox_hit(p, box) -> bool:
    return box[0] - 1e-9 <= p[0] <= box[2] + 1e-9 and box[1] - 1e-9 <= p[1] <= box[3] + 1e-9


def _blocked(p, blocks) -> bool:
    for box, poly in blocks:
        if _bbox_hit(p, box) and G.point_in_polygon(p, poly):
            return True
    return False


def _toe(p, nrm, z: float, slope: float, fill: bool, gz, reach: float, step: float = 0.1) -> Optional[float]:
    """How far out from ``p`` (along ``nrm``) a bank from ``z`` at ``slope`` meets the natural ground (None: not
    within ``reach``: the ground falls or rises as steeply as the bank)."""
    d = 0.0
    while d <= reach + 1e-9:
        g = gz(p[0] + nrm[0] * d, p[1] + nrm[1] * d)
        zb = z - d * slope if fill else z + d * slope
        if (fill and zb <= g + 1e-6) or (not fill and zb >= g - 1e-6):
            return d
        d += step
    return None


def plan_embankments(platforms: Sequence[dict], gz: Callable, keep_out: Sequence = (), plot: Sequence = (),
                     corridors: Sequence = ()) -> list[dict]:
    """The banks of the platforms (pure; module docstring): for every edge of a flat, primary platform (not facing the
    building, not its steps edge) whose ground lies at most ``embank_max_m`` under (fill) or over (cut) the level along
    the whole edge: a lawn bank (1:3), else a planted bank (1:2), when the bank meets the natural ground within
    ``embank_reach_m`` and its strip (the edge piece's longest free stretch, at least ``embank_min_m`` and
    ``embank_share`` of the edge, out to the toe + ``embank_margin_m``) stays inside the ``plot`` and out of
    ``keep_out`` (the building and the copies, grown by ``embank_facade_m``), the other platforms, ``corridors`` (the
    flights) and the platform itself. Writes ``pf["embankments"]`` and returns the grading rows (``grade_z``):
    ``{"platform", "edge", "a", "u", "n", "length_m", "width_m", "z_top", "slope", "fill", "finish", "cone_a",
    "cone_b", "toe_m", "difference_m", "reason"}``."""
    from wenart.blender import site as S

    tol = S.PLATFORM["level_tol"]
    step = GRADE["embank_sample_m"]
    grown = []
    for poly in keep_out or []:
        if len(poly or []) >= 3:
            g = geom2d.offset_polygon(geom2d.ccw(poly), -GRADE["embank_facade_m"])
            grown.append(g if len(g) >= 3 else geom2d.ccw(poly))
    base = [(G.bbox(p), p) for p in grown] + [(G.bbox(p), p) for p in corridors or [] if len(p or []) >= 3]
    plot = geom2d.ccw(plot) if len(plot or []) >= 3 else []
    rows: list[dict] = []
    for pf in platforms:
        pf["embankments"] = []
        poly = geom2d.ccw(pf.get("polygon") or [])
        # a labelled outdoor space (a veranda, porch, deck: wenart.levels.outdoor) keeps its built base; banks are the
        # garden's (terraces, pool decks, parkings)
        if pf.get("sloped") or pf.get("elevated") or pf.get("parent") or pf.get("source") == "outdoor_space" \
                or len(poly) < 3:
            continue
        n = len(poly)
        z = float(pf["z"])
        skip = set(pf.get("against_edges") or []) | set(pf.get("shared_edges") or [])
        if pf.get("steps_edge") is not None:
            skip.add(int(pf["steps_edge"]))
        if pf.get("guard_edges"):                         # a guard an answer asked for keeps its drop
            skip |= {i for i in range(n) if S.on_guard_edge(poly[i], poly[(i + 1) % n], pf["guard_edges"])}
        others = [(G.bbox(q["polygon"]), geom2d.ccw(q["polygon"])) for q in platforms
                  if q is not pf and len(q.get("polygon") or []) >= 3]
        blocks = base + others
        cands: dict = {}
        for i in range(n):
            if i in skip:
                continue
            a, b = poly[i], poly[(i + 1) % n]
            length = G.distance(a, b)
            if length < GRADE["embank_min_m"]:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            nrm = (uy, -ux)
            pts = [G.point_along_segment(a, b, f) for f in (0.0, 0.25, 0.5, 0.75, 1.0)]
            g_edge = [gz(*p) for p in pts]
            drop, rise = z - min(g_edge), max(g_edge) - z
            if max(drop, rise) <= tol or max(drop, rise) > GRADE["embank_max_m"] or (drop > tol and rise > tol):
                continue                                  # level with the ground, too tall, or the ground crosses it
            fill = drop > rise
            for finish, slope in (("lawn", GRADE["lawn_slope"]), ("planted", GRADE["planted_slope"])):
                toes = [_toe(p, nrm, z, slope, fill, gz, GRADE["embank_reach_m"]) for p in pts]
                if any(t is None for t in toes):
                    continue
                width = max(toes) + GRADE["embank_margin_m"]
                reach = width + GRADE["embank_pass_m"]          # the bank and a way past it, inside the plot
                cols = []
                k = max(2, int(math.ceil(length / step)) + 1)
                rows_q = max(2, int(math.ceil(reach / step)) + 1)
                qs = sorted({0.02 + (reach - 0.02) * r / (rows_q - 1) for r in range(rows_q)} | {width})
                for c in range(k):
                    t = length * c / (k - 1)
                    free = True
                    for qd in qs:
                        p = (a[0] + ux * t + nrm[0] * qd, a[1] + uy * t + nrm[1] * qd)
                        if _blocked(p, blocks) or G.point_in_polygon(p, poly) or \
                                (plot and not G.point_in_polygon(p, plot)):
                            free = False
                            break
                    cols.append((t, free))
                best, cur = None, None
                for t, free in cols:
                    if free:
                        cur = (cur[0], t) if cur else (t, t)
                        if best is None or cur[1] - cur[0] > best[1] - best[0]:
                            best = cur
                    else:
                        cur = None
                if best is None or best[1] - best[0] < max(GRADE["embank_min_m"], GRADE["embank_share"] * length) - 1e-6:
                    continue
                t0, t1 = best
                cands[i] = {"platform": pf["id"], "edge": i, "a": (a[0] + ux * t0, a[1] + uy * t0), "u": (ux, uy),
                            "n": nrm, "length_m": round(t1 - t0, 4), "width_m": round(width, 4), "z_top": z,
                            "slope": slope, "fill": fill, "finish": finish, "toe_m": round(max(toes), 3),
                            "difference_m": round(max(drop, rise), 3), "t0": t0, "t1": t1, "edge_length_m": length,
                            "cone_a": False, "cone_b": False}
                break
        for i, e in cands.items():
            prev, nxt = cands.get((i - 1) % n), cands.get((i + 1) % n)
            e["cone_a"] = bool(prev and prev["fill"] == e["fill"] and e["t0"] <= 1e-6
                               and prev["t1"] >= prev["edge_length_m"] - 1e-6)
            e["cone_b"] = bool(nxt and nxt["fill"] == e["fill"] and e["t1"] >= e["edge_length_m"] - 1e-6
                               and nxt["t0"] <= 1e-6)
            e["reason"] = (f"{pf['id']} edge {i}: a {e['finish']} bank of 1:{round(1.0 / e['slope']):d} "
                           f"{'down' if e['fill'] else 'up'} to the ground {e['toe_m']:.1f} m out (the ground "
                           f"{e['difference_m']:.2f} m {'under' if e['fill'] else 'over'} the level; a landscape "
                           f"architect grades the ground to the terrace where it can, no retaining wall; inferred)")
            pf["embankments"].append(e)
            rows.append(e)
        if pf["embankments"]:
            banked = {e["edge"] for e in pf["embankments"]}
            pf["railing_edges"] = [j for j in pf.get("railing_edges") or [] if j not in banked]
    return rows


def wing_walls(pf: dict, gz_natural: Callable, gz_graded: Callable, piece_m: float = 1.0) -> list[dict]:
    """The wing walls of a platform's banks (pure): at a bank end with no cone (``cone_a`` / ``cone_b`` False) a wall
    along the bank's side from the platform edge out to its toe, where the graded and the natural ground differ by more
    than the level tolerance: ``[{"p0", "p1", "z0", "z1_ends", "height_m"}]`` (its top over the higher ground, its
    foot under the lower)."""
    from wenart.blender import site as S

    tol, below = S.PLATFORM["level_tol"], S.PLATFORM["below"]
    out = []
    for e in pf.get("embankments") or []:
        ax, ay = e["a"]
        ux, uy = e["u"]
        nx, ny = e["n"]
        for end, cone in ((0.0, e["cone_a"]), (e["length_m"], e["cone_b"])):
            if cone:
                continue
            inward = 0.02 if end == 0.0 else -0.02
            k = max(1, int(math.ceil(e["width_m"] / piece_m)))
            for j in range(k):
                q0, q1 = e["width_m"] * j / k, e["width_m"] * (j + 1) / k
                p0 = (ax + ux * end + nx * q0, ay + uy * end + ny * q0)
                p1 = (ax + ux * end + nx * q1, ay + uy * end + ny * q1)
                ins = [(p[0] + ux * inward, p[1] + uy * inward) for p in (p0, p1)]
                gn = [gz_natural(*p) for p in (p0, p1)]
                gg = [gz_graded(*p) for p in ins]
                diff = max(abs(x - y) for x, y in zip(gn, gg))
                if diff <= tol:
                    continue
                tops = tuple(round(max(x, y) + 0.05, 4) for x, y in zip(gn, gg))
                out.append({"p0": p0, "p1": p1, "z0": round(min(gn + gg) - below, 4), "z1_ends": tops,
                            "height_m": round(diff, 3), "edge": e["edge"]})
    return out


def bank_zones(terrain: Optional[dict]) -> list:
    """The plan rectangles of the banks of a terrain model (pure): a path keeps off them (a walk along a 1:2 bank
    would tilt across it); a bank's cones are left out (they lie beside the platform's corners)."""
    out = []
    for e in (terrain or {}).get("grading") or []:
        ax, ay = e["a"]
        ux, uy = e["u"]
        nx, ny = e["n"]
        length, width = float(e["length_m"]), float(e["width_m"])
        out.append(geom2d.ccw([(ax, ay), (ax + ux * length, ay + uy * length),
                               (ax + ux * length + nx * width, ay + uy * length + ny * width),
                               (ax + nx * width, ay + ny * width)]))
    return out


def plan_terrain(plan: dict) -> Optional[dict]:
    """The terrain a site plan builds on: its ``terrain`` with its platforms' banks (``site_plan`` grades it already;
    a plan put together by hand, with platforms planned on the bare terrain, gets the same graded ground)."""
    terrain = plan.get("terrain")
    if not terrain or terrain.get("grading"):
        return terrain
    return graded_terrain(terrain, plan.get("platforms") or [])


def graded_terrain(terrain: dict, platforms: Sequence[dict]) -> dict:
    """The terrain model with the platforms' banks (``terrain["grading"]``, ``site.ground_z`` applies them): the
    terrain itself when no platform has a bank."""
    rows = [e for pf in platforms for e in pf.get("embankments") or []]
    if not rows:
        return terrain
    keep = ("a", "u", "n", "length_m", "width_m", "z_top", "slope", "fill", "cone_a", "cone_b", "platform", "edge",
            "finish")
    return dict(terrain, grading=[{k: e[k] for k in keep} for e in rows])


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

def strip_frame(poly) -> Optional[dict]:
    """The frame of a straight path strip (pure): a 4-corner polygon whose long sides are parallel within 2 degrees:
    ``{"a": the middle of its start end, "u": along, "n": across (left), "length", "width"}``; None otherwise."""
    pts = geom2d.clean_polygon([(float(p[0]), float(p[1])) for p in poly or []])
    if len(pts) != 4:
        return None
    pts = geom2d.ccw(pts)
    lens = [G.distance(pts[k], pts[(k + 1) % 4]) for k in range(4)]
    k = 0 if lens[0] + lens[2] >= lens[1] + lens[3] else 1       # the long sides: k and k + 2
    p0, p1 = pts[k], pts[(k + 1) % 4]
    p2, p3 = pts[(k + 2) % 4], pts[(k + 3) % 4]
    if min(lens[k], lens[(k + 2) % 4]) < 1e-6:
        return None
    u0 = ((p1[0] - p0[0]) / lens[k], (p1[1] - p0[1]) / lens[k])
    u2 = ((p3[0] - p2[0]) / lens[(k + 2) % 4], (p3[1] - p2[1]) / lens[(k + 2) % 4])
    if abs(u0[0] * u2[1] - u0[1] * u2[0]) > 0.035 or u0[0] * u2[0] + u0[1] * u2[1] > -0.99:
        return None
    a = G.segment_midpoint(p3, p0)
    b = G.segment_midpoint(p1, p2)
    length = G.distance(a, b)
    if length < 1e-6:
        return None
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    width = abs((p3[0] - p0[0]) * -u[1] + (p3[1] - p0[1]) * u[0])
    return {"a": a, "u": u, "n": (-u[1], u[0]), "length": length, "width": width}


def _slice(fr: dict, t0: float, t1: float, s0: Optional[float] = None, s1: Optional[float] = None) -> list:
    a, u, n = fr["a"], fr["u"], fr["n"]
    h = fr["width"] / 2.0
    s0 = -h if s0 is None else s0
    s1 = h if s1 is None else s1
    return geom2d.ccw([(a[0] + u[0] * t + n[0] * s, a[1] + u[1] * t + n[1] * s)
                       for t, s in ((t0, s0), (t1, s0), (t1, s1), (t0, s1))])


def _at(fr: dict, t: float, s: float = 0.0) -> tuple[float, float]:
    a, u, n = fr["a"], fr["u"], fr["n"]
    return (a[0] + u[0] * t + n[0] * s, a[1] + u[1] * t + n[1] * s)


def path_profile(fr: dict, gz: Callable) -> dict:
    """The ground along and across a path strip (pure): ``ts``, ``g`` (the centre line every ``path_sample_m``),
    ``local`` (the steepest gradient over ``window_m``), ``overall`` and ``cross`` (the steepest fall across)."""
    length, width = fr["length"], fr["width"]
    k = max(2, int(math.ceil(length / GRADE["path_sample_m"])) + 1)
    ts = [length * j / (k - 1) for j in range(k)]
    g = [gz(*_at(fr, t)) for t in ts]
    h = width / 2.0
    cross = max(abs(gz(*_at(fr, t, h)) - gz(*_at(fr, t, -h))) / max(width, 1e-6) for t in ts)
    w = GRADE["window_m"]
    local = 0.0
    for j, t in enumerate(ts):
        for m in range(j + 1, len(ts)):
            if ts[m] - t >= w - 1e-9 or m == len(ts) - 1:
                local = max(local, abs(g[m] - g[j]) / max(ts[m] - t, 1e-6))
                break
    return {"ts": ts, "g": g, "local": local, "overall": abs(g[-1] - g[0]) / max(length, 1e-6), "cross": cross}


def _interp(ts, g, t: float) -> float:
    if t <= ts[0]:
        return g[0]
    for j in range(1, len(ts)):
        if t <= ts[j]:
            f = (t - ts[j - 1]) / max(ts[j] - ts[j - 1], 1e-9)
            return g[j - 1] + (g[j] - g[j - 1]) * f
    return g[-1]


def _stepped_slices(length: float, width: float, ts, g, rules: dict) -> tuple[list[dict], dict]:
    """The landings and flights of a stepped path from its lower end (t = 0) up (pure): ``(slices, info)``; a slice is
    ``{"t0", "t1", "z0", "z1", "kind": landing | tread, "riser": bool}`` (``riser``: a riser rises at its start)."""
    end = min(GRADE["end_landing_m"], max(width, 0.6), length / 4.0)
    z0 = _interp(ts, g, end / 2.0)
    z1 = _interp(ts, g, length - end / 2.0)
    rise = max(0.0, z1 - z0)
    rmax = float(rules["riser_max_outdoor"])
    n = max(1, int(math.ceil(rise / rmax - 1e-9)))
    r = rise / n
    tread = max(GRADE["garden_tread_m"], float(rules["step_rule"][0]) - 2.0 * r)
    inner = length - 2.0 * end
    lmin = GRADE["landing_min_m"]
    per_max = max(1, int(rules["landing_every_risers"]))
    kmin = min(n, GRADE["flight_risers_min"])
    pick = None
    for k in range(kmin, per_max + 1):
        f = int(math.ceil(n / k))
        if (n - f) * tread + (f - 1) * lmin <= inner + 1e-9:
            pick = k
            break
    info = {"risers": n, "riser": round(r, 4), "tread": round(tread, 3), "rise": round(rise, 3), "too_steep": False}
    if pick is None:
        pick = per_max
        f = int(math.ceil(n / pick))
        left = inner - (f - 1) * lmin
        tread = left / max(1, n - f) if n > f else tread
        info["tread"] = round(tread, 3)
        if tread < float(rules["tread_min"]) - 1e-9:
            info["too_steep"] = True
    f = int(math.ceil(n / pick))
    sizes = [n // f + (1 if j < n % f else 0) for j in range(f)]
    runs = [(s - 1) * tread for s in sizes]
    # place each flight where the ground climbs through its middle level, then keep the landings between them
    starts = []
    level = z0
    for j, s in enumerate(sizes):
        target = level + s * r / 2.0
        tc = next((t for t, z in zip(ts, g) if z >= target and end <= t <= length - end), None)
        tc = tc if tc is not None else end + sum(runs[:j]) + j * lmin + runs[j] / 2.0
        starts.append(tc - runs[j] / 2.0)
        level += s * r
    lo = end
    for j in range(f):                                   # forward: after the landing before
        starts[j] = max(starts[j], lo)
        lo = starts[j] + runs[j] + lmin
    hi = length - end
    for j in range(f - 1, -1, -1):                       # backward: before the landing after
        starts[j] = min(starts[j], hi - runs[j])
        hi = starts[j] - lmin
    slices = []
    level, t = z0, 0.0
    for j, s in enumerate(sizes):
        a = max(starts[j], t)
        slices.append({"t0": t, "t1": a, "z0": level, "z1": level, "kind": "landing", "riser": j > 0})
        for m in range(1, s):
            slices.append({"t0": a + (m - 1) * tread, "t1": a + m * tread, "z0": level + m * r,
                           "z1": level + m * r, "kind": "tread", "riser": True})
        t = a + (s - 1) * tread
        level += s * r
    slices.append({"t0": t, "t1": length, "z0": level, "z1": level, "kind": "landing", "riser": True})
    slices = [sl for sl in slices if sl["t1"] - sl["t0"] > 1e-4]
    info.update(flights=sizes, landings=max(0, f - 1), flight_rises=[round(s * r, 3) for s in sizes])
    return slices, info


def path_plan(area: dict, gz: Callable, accessible: bool = False, rules: Optional[dict] = None) -> dict:
    """How a path meets the slope (pure; module docstring): ``{"id", "graded", "kind": walk | sloped_walk | stepped |
    ramp, "frame", "slices", "local", "cross", "rise", "reason", ...}``. ``slices`` run along the strip from its
    start (``t`` 0 at ``frame["a"]``), each level across: ``{"t0", "t1", "z0", "z1", "kind", "riser"}``."""
    rules = rules or level_rules()
    rec = {"id": area.get("id"), "graded": False, "kind": "walk", "slices": [], "polygon": area.get("polygon")}
    fr = strip_frame(area.get("polygon") or [])
    if fr is None:
        rec["reason"] = "not a straight strip: draped on the ground as drawn"
        return rec
    prof = path_profile(fr, gz)
    rec.update(frame=fr, local=round(prof["local"], 4), cross=round(prof["cross"], 4), overall=round(prof["overall"], 4),
               length=round(fr["length"], 3), width=round(fr["width"], 3))
    ts, g = prof["ts"], prof["g"]
    if prof["local"] <= GRADE["walk_max"] + 1e-9 and prof["cross"] <= GRADE["cross_fall_max"] + 1e-9:
        rec["reason"] = (f"a walk: at most 1:20 along ({prof['local'] * 100:.1f} %) and "
                         f"{prof['cross'] * 100:.1f} % across, on the ground with an edging")
        return rec
    rev = g[-1] < g[0]
    if rev:                                          # work from the lower end
        ts_r = [fr["length"] - t for t in reversed(ts)]
        g_r = list(reversed(g))
    else:
        ts_r, g_r = ts, g
    rise = g_r[-1] - g_r[0]
    rec["rise"] = round(rise, 3)
    from wenart.levels import rules as LM
    ramp = LM.ramp_for(rise, rules) if accessible else None
    slices: list[dict] = []
    if accessible and ramp is not None and prof["overall"] <= float(ramp["slope"]) + 1e-9:
        # an accessible route: a ramp of uniform slope with level landings every ramp_run_m, rails on both sides
        run_max, land = GRADE["ramp_run_m"], GRADE["ramp_landing_m"]
        k = max(1, int(math.ceil(fr["length"] / (run_max + land))))
        ramp_len = fr["length"] - (k - 1) * land
        slope = rise / max(ramp_len, 1e-6)
        t, z = 0.0, g_r[0]
        for j in range(k):
            seg = ramp_len / k
            slices.append({"t0": t, "t1": t + seg, "z0": z, "z1": z + slope * seg, "kind": "ramp", "riser": False})
            t, z = t + seg, z + slope * seg
            if j < k - 1:
                slices.append({"t0": t, "t1": t + land, "z0": z, "z1": z, "kind": "landing", "riser": False})
                t += land
        rec.update(kind="ramp", slope=round(slope, 4), ratio=ramp["ratio"],
                   handrails=rise > float(rules["ramp_handrail_from"]),
                   reason=f"an accessible route: a ramp of {slope * 100:.1f} % (at most {ramp['ratio']} for a "
                          f"{rise:.2f} m rise) in {k} run(s) with landings, level across, rails on both sides (inferred)")
    elif prof["local"] <= GRADE["slope_walk_max"] + 1e-9:
        k = max(1, int(math.ceil(fr["length"] / GRADE["window_m"])))
        for j in range(k):
            t0, t1 = fr["length"] * j / k, fr["length"] * (j + 1) / k
            slices.append({"t0": t0, "t1": t1, "z0": _interp(ts_r, g_r, t0), "z1": _interp(ts_r, g_r, t1),
                           "kind": "slope", "riser": False})
        rec.update(kind="sloped_walk", reason=f"a sloped walk: {prof['local'] * 100:.1f} % along (at most 1:12), laid "
                                                f"level across ({prof['cross'] * 100:.1f} % of cross fall taken by its "
                                                f"edges; inferred)")
    else:
        slices, info = _stepped_slices(fr["length"], fr["width"], ts_r, g_r, rules)
        rec.update(kind="stepped", **{k: v for k, v in info.items()},
                   handrails=any(x > float(rules["handrail_from"]) + 1e-9 for x in info["flight_rises"]),
                   reason=f"a stepped path: {prof['local'] * 100:.0f} % along is steeper than 1:12, so "
                          f"{info['risers']} risers of {info['riser']:.3f} m in {len(info['flights'])} flight(s) "
                          f"({'/'.join(str(s) for s in info['flights'])}) with level landings, treads "
                          f"{info['tread']:.2f} m, level across, stone step edges"
                          + ("; a handrail on the flights over 0.45 m" if any(
                              x > float(rules["handrail_from"]) + 1e-9 for x in info["flight_rises"]) else "")
                          + (" (steeper than a stair can follow: treads under the rule)" if info["too_steep"] else "")
                          + " (inferred)")
        if accessible:
            rec["accessible_open"] = (f"an accessible route rises {rise:.2f} m over {fr['length']:.1f} m "
                                      f"({prof['overall'] * 100:.1f} %): a straight ramp needs "
                                      f"{(rise / float(ramp['slope'])) if ramp else 0.0:.1f} m; steps built")
    if rev:                                          # back to the strip's own direction
        L = fr["length"]
        slices = [{"t0": L - s["t1"], "t1": L - s["t0"], "z0": s["z1"], "z1": s["z0"], "kind": s["kind"],
                   "riser_end": s["riser"], "riser": False} for s in reversed(slices)]
    else:
        for s in slices:
            s["riser_end"] = False
    rec["slices"] = slices
    rec["graded"] = True
    return rec


def accessible_paths(plan: dict) -> set:
    """The ids of the path areas on an accessible route (pure): the inferred paths of the doors whose entrance has a
    ramp (the brief's ``levels.accessible_entrance``, a drawn ramp)."""
    inf = plan.get("inferred") or {}
    doors = set()
    for st in inf.get("steps") or []:
        if st.get("ramp"):
            doors |= {str(d) for d in st.get("doors") or [st.get("opening_id")]}
    out = set()
    for p in inf.get("paths") or []:
        ids = [str(x) for x in p.get("opening_ids") or []]
        if doors & set(ids):
            out.add(f"path_{'_'.join(ids)}")
    return out


def graded_paths(plan: dict) -> list[dict]:
    """``path_plan`` of every path area of a site plan without a platform, in the order of ``plan["areas"]``
    (``index``); a slice whose middle lies in the building, a copy, a pool, a light well, a flat platform or an earlier
    graded path is not built (``skip``: the other one builds that ground)."""
    from wenart.blender import site as S

    terrain = plan_terrain(plan)
    if not terrain:
        return []
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    acc = accessible_paths(plan)
    holes = [h for h in [plan.get("outline") or []] + list(plan.get("copy_holes") or [])
             + [p["polygon"] for p in plan.get("pools") or []] + [w["polygon"] for w in plan.get("wells") or []]
             + [pf["polygon"] for pf in plan.get("platforms") or [] if not pf.get("sloped")] if len(h or []) >= 3]
    out = []
    earlier: list = []
    for k, a in enumerate(plan.get("areas") or []):
        if a.get("kind") != "path" or a.get("platform_id") or len(a.get("polygon") or []) < 3:
            continue
        rec = path_plan(a, gz, accessible=str(a.get("id")) in acc)
        rec["index"] = k
        if rec["graded"]:
            fr = rec["frame"]
            for s in rec["slices"]:
                c = _at(fr, (s["t0"] + s["t1"]) / 2.0)
                s["skip"] = any(G.point_in_polygon(c, h) for h in holes) or any(G.point_in_polygon(c, h) for h in earlier)
            earlier.append(geom2d.ccw(a["polygon"]))
        out.append(rec)
    return out


def walkable(plan: dict) -> list:
    """The polygons a path may run into without an edging across its way (pure): the other paths, the platforms, the
    parkings, the flights' footprints and the entrance steps."""
    from wenart.blender import site as S

    out = [a["polygon"] for a in plan.get("areas") or [] if len(a.get("polygon") or []) >= 3
           and a.get("kind") in ("path", "paving", "parking")]
    out += [pf["polygon"] for pf in plan.get("platforms") or [] if len(pf.get("polygon") or []) >= 3]
    terrain = plan_terrain(plan)
    if terrain:
        gz = (lambda x, y: S.ground_z(terrain, x, y))
        for pf in plan.get("platforms") or []:
            fl = down_flight(pf, gz)
            if fl is not None:
                out.append(fl["footprint"])
            up = S.up_flight(pf, terrain)
            if up is not None:
                out.append(up["footprint"])
    for st in (plan.get("inferred") or {}).get("steps") or []:
        out += S.steps_footprint(st)
    return out


def _sloped_prism(poly, z_bottom: float, z_tops: Sequence[float]) -> tuple[list, list]:
    verts = [(p[0], p[1], z_bottom) for p in poly] + [(p[0], p[1], zt) for p, zt in zip(poly, z_tops)]
    k = len(poly)
    faces = [list(reversed(range(k))), list(range(k, 2 * k))]
    for j in range(k):
        a, b = j, (j + 1) % k
        faces.append([a, b, k + b, k + a])
    return verts, faces


# 30 Oct 2026 (lesson UL144): an outdoor stair's handrail, one rail along its open side
RAIL = {"height": 0.90, "extend_m": 0.30, "post_max_m": 1.4, "post_min_m": 1.2, "inset": 0.05}


def _level_at(slices: Sequence[dict], t: float) -> Optional[float]:
    """The top of the slice under ``t`` (pure; the highest one at a slice border), None off the slices."""
    zs = [max(s["z0"], s["z1"]) if abs(s["z1"] - s["z0"]) < 1e-9 else
          s["z0"] + (s["z1"] - s["z0"]) * (t - s["t0"]) / max(s["t1"] - s["t0"], 1e-9)
          for s in slices if s["t0"] - 1e-6 <= t <= s["t1"] + 1e-6]
    return max(zs) if zs else None


def stair_rail(rec: dict, gz: Optional[Callable] = None) -> Optional[dict]:
    """The handrail of a stepped path (pure; lesson UL144): one continuous rail on its open side, ``RAIL["height"]``
    over the nosing line, following the pitch along each flight and level over the landings, reaching
    ``RAIL["extend_m"]`` past the bottom and the top nosing, on posts every ``post_min_m``-``post_max_m`` (and at its
    ends) standing on the treads and landings ``inset`` inside the path's edge, never on the ground beside it. The open
    side: the side where the ground beside the flights stands less over the treads (no edge wall there; ``gz``),
    else the left. None when no flight rises over the levels' ``handrail_from`` (``rec["handrails"]``) or the path
    has no risers. ``{"side", "points": [(x, y, z)], "posts": [((x, y, z_foot), (x, y, z_top))], "nosings",
    "flights", "t_range", "reason"}``."""
    if rec.get("kind") != "stepped" or not rec.get("handrails") or not rec.get("frame"):
        return None
    fr = rec["frame"]
    slices = sorted((s for s in rec.get("slices") or [] if not s.get("skip")), key=lambda s: s["t0"])
    if len(slices) < 2:
        return None
    # the risers: a level change between two slices, its nosing on the upper tread's edge
    risers = []
    for a, b in zip(slices, slices[1:]):
        za, zb = max(a["z0"], a["z1"]), max(b["z0"], b["z1"])
        if abs(zb - za) > 0.01:
            risers.append({"t": a["t1"], "z": max(za, zb), "up": zb > za, "after": b["kind"], "before": a["kind"]})
    if not risers:
        return None
    # the flights: risers joined by treads (a landing between two risers parts them)
    flights, cur = [], [risers[0]]
    for r0, r1 in zip(risers, risers[1:]):
        between = next((s for s in slices if abs(s["t0"] - r0["t"]) < 1e-6), None)
        if between is not None and between["kind"] == "landing":
            flights.append(cur)
            cur = []
        cur.append(r1)
    flights.append(cur)
    tread = float(rec.get("tread") or GRADE["garden_tread_m"])
    riser = float(rec.get("riser") or 0.15)
    H = RAIL["height"]
    # the nosing line: the nosings of each flight, the pitch carried one going past them onto the landings
    pts: list[tuple[float, float]] = []
    for k, fl in enumerate(flights):
        sign = 1.0 if fl[0]["up"] else -1.0
        slope = (fl[-1]["z"] - fl[0]["z"]) / (fl[-1]["t"] - fl[0]["t"]) if len(fl) > 1 else sign * riser / tread
        if k == 0:
            pts.append((fl[0]["t"] - RAIL["extend_m"], fl[0]["z"]))      # level past the first nosing
        else:
            prev = flights[k - 1]
            land = _level_at(slices, (prev[-1]["t"] + fl[0]["t"]) / 2.0)
            land = prev[-1]["z"] if land is None else land
            # the pitch of the flight before, carried down or up to the landing; and the next one's from it
            p_slope = (prev[-1]["z"] - prev[0]["z"]) / (prev[-1]["t"] - prev[0]["t"]) if len(prev) > 1 else slope
            ta = prev[-1]["t"] + ((land - prev[-1]["z"]) / p_slope if abs(p_slope) > 1e-9 else 0.0)
            tb = fl[0]["t"] - ((fl[0]["z"] - land) / slope if abs(slope) > 1e-9 else 0.0)
            if prev[-1]["t"] - 1e-6 <= ta <= tb <= fl[0]["t"] + 1e-6:
                pts += [(ta, land), (tb, land)]
        pts += [(r["t"], r["z"]) for r in fl]
    pts.append((flights[-1][-1]["t"] + RAIL["extend_m"], flights[-1][-1]["z"]))
    t_lo, t_hi = 0.02, float(fr["length"]) - 0.02
    pts = [(min(max(t, t_lo), t_hi), z) for t, z in pts]
    clean = []
    for t, z in pts:
        if clean and abs(t - clean[-1][0]) < 1e-4:
            clean[-1] = (t, max(z, clean[-1][1]))
            continue
        clean.append((t, z))
    # the open side: less ground over the treads beside the flights
    h = fr["width"] / 2.0
    side = 1.0
    if gz is not None:
        def over(sg: float) -> float:
            tot = 0.0
            for r in risers:
                p = _at(fr, r["t"], sg * (h + GRADE["edge_t"] / 2.0))
                tot += max(0.0, gz(*p) - r["z"])
            return tot
        side = 1.0 if over(1.0) <= over(-1.0) + 1e-6 else -1.0
    s_off = side * (h - RAIL["inset"])
    points = [(*_at(fr, t, s_off), z + H) for t, z in clean]
    # the posts: at the ends and every post_max_m at most along the plan, each on the tread or landing under it
    total = clean[-1][0] - clean[0][0]
    n = max(1, int(math.ceil(total / RAIL["post_max_m"] - 1e-9)))
    posts = []
    for j in range(n + 1):
        t = clean[0][0] + total * j / n
        z_rail = _interp([p[0] for p in clean], [p[1] for p in clean], t) + H
        foot = _level_at(slices, t)
        if foot is None:
            continue
        xy = _at(fr, t, s_off)
        posts.append(((xy[0], xy[1], foot), (xy[0], xy[1], z_rail)))
    return {"side": "left" if side > 0 else "right", "points": points, "posts": posts,
            "nosings": [(round(r["t"], 3), round(r["z"], 3)) for r in risers], "flights": len(flights),
            "t_range": (round(clean[0][0], 3), round(clean[-1][0], 3)), "spacing_m": round(total / n, 3),
            "reason": f"one handrail on the {'left' if side > 0 else 'right'} (open) side, {H:.2f} m over the nosings "
                      f"of its {len(flights)} flight(s), level over the landings, {RAIL['extend_m']:.2f} m past the "
                      f"first and last step, on {len(posts)} posts every {total / n:.2f} m set on the steps "
                      f"(lesson UL144; inferred)"}


def path_meshes(rec: dict, gz: Callable, below: float, walk: Sequence = ()) -> dict:
    """The meshes of a graded path (pure): ``tread`` (its landings, treads, sloped walks and ramps in the path's
    floor), ``step_edge`` (a stone step edge ``riser_edge_m`` deep at every riser: the riser face and the tread's
    nosing), ``edge_wall`` (where the ground beside stands ``edge_wall_from_m`` over the path: a low wall holding it,
    ``edge_t`` thick), ``edging`` (elsewhere a stone edging ``edging_t`` wide, ``edging_up`` over the higher of the
    path and the ground) and ``rail`` (a handrail on a flight that rises over ``handrail_from``, a ramp's rails on
    both sides). No edging or edge wall where ``walk`` (``walkable``) adjoins the side. ``records``: per slice its
    top, bottom and highest ground (the review)."""
    from wenart.blender import site as S

    fr = rec["frame"]
    rules = level_rules()
    out = {"tread": [], "step_edge": [], "edge_wall": [], "edging": [], "rail": [], "records": []}
    h = fr["width"] / 2.0
    hr = S.HANDRAIL
    edge_d = GRADE["riser_edge_m"]
    slices = [s for s in rec["slices"] if not s.get("skip")]
    for s in slices:
        t0, t1 = s["t0"], s["t1"]
        stone = None
        if s.get("riser") and t1 - t0 > edge_d + 0.05:
            stone = (t0, t0 + edge_d)
            t0 = t0 + edge_d
        elif s.get("riser_end") and t1 - t0 > edge_d + 0.05:
            stone = (t1 - edge_d, t1)
            t1 = t1 - edge_d
        poly = _slice(fr, t0, t1)
        g = [gz(*q) for q in poly] + [gz(*_at(fr, (t0 + t1) / 2.0))]
        zb = min(min(g), s["z0"], s["z1"]) - below
        if abs(s["z1"] - s["z0"]) > 1e-6:
            # a sloped slice: its top runs from z0 at t0 to z1 at t1 (the corners of _slice in ccw order)
            tops = []
            for q in poly:
                tq = (q[0] - fr["a"][0]) * fr["u"][0] + (q[1] - fr["a"][1]) * fr["u"][1]
                f = (tq - s["t0"]) / max(s["t1"] - s["t0"], 1e-9)
                tops.append(s["z0"] + (s["z1"] - s["z0"]) * f)
            out["tread"].append(_sloped_prism(poly, zb, tops))
        else:
            out["tread"].append(geom2d.prism(poly, zb, s["z0"]))
        out["records"].append({"t0": round(s["t0"], 3), "t1": round(s["t1"], 3), "z_top": round(max(s["z0"], s["z1"]), 4),
                               "z_bottom": round(zb, 4), "ground_max": round(max(g), 4), "kind": s["kind"]})
        if stone is not None:
            sp = _slice(fr, stone[0], stone[1])
            gs = [gz(*q) for q in sp]
            out["step_edge"].append(geom2d.prism(sp, min(min(gs), s["z0"]) - below, s["z0"]))
        # the two sides: an edge wall where the ground stands over the path, else an edging; none against a walk
        for side in (1.0, -1.0):
            for c0, c1 in ((s["t0"], (s["t0"] + s["t1"]) / 2.0), ((s["t0"] + s["t1"]) / 2.0, s["t1"])):
                if c1 - c0 < 1e-4:
                    continue
                probe = _at(fr, (c0 + c1) / 2.0, side * (h + 0.1))
                if any(G.point_in_polygon(probe, w) for w in walk):
                    continue
                ends = [_at(fr, c, side * (h + GRADE["edge_t"] / 2.0)) for c in (c0, c1)]
                ground = [gz(*p) for p in ends]
                ztop = [s["z0"] + (s["z1"] - s["z0"]) * (c - s["t0"]) / max(s["t1"] - s["t0"], 1e-9) for c in (c0, c1)]
                high = max(gv - zt for gv, zt in zip(ground, ztop))
                wall = high > GRADE["edge_wall_from_m"]
                t = GRADE["edge_t"] if wall else GRADE["edging_t"]
                s_in, s_out = side * h, side * (h + t)
                piece = _slice(fr, c0, c1, min(s_in, s_out), max(s_in, s_out))
                gp = [gz(*q) for q in piece]
                zb2 = min(min(gp), min(ztop)) - GRADE["edging_down"]
                tops = []
                for q in piece:
                    tq = (q[0] - fr["a"][0]) * fr["u"][0] + (q[1] - fr["a"][1]) * fr["u"][1]
                    f = (tq - s["t0"]) / max(s["t1"] - s["t0"], 1e-9)
                    zt = s["z0"] + (s["z1"] - s["z0"]) * f
                    tops.append(max(zt, gz(*q)) + (0.05 if wall else GRADE["edging_up"]))
                out["edge_wall" if wall else "edging"].append(_sloped_prism(piece, zb2, tops))
    # the handrails: a flight (a run of treads) rising over handrail_from, or a ramp's runs (both sides)
    runs, cur = [], []
    for s in slices:
        if s["kind"] in ("tread", "ramp"):
            cur.append(s)
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    # 30 Oct 2026 (lesson UL144, user on real04: "These handrails here not making that much sense": each flight of the
    # stepped paths had its own short rail, two posts and a bar standing like a loose frame beside the stair): a
    # stepped path gets one continuous handrail on its open side (``stair_rail``)
    if rec.get("kind") == "stepped":
        rail = stair_rail(rec, gz)
        out["rail_plan"] = rail
        if rail is not None:
            pts = rail["points"]
            for p, q in zip(pts, pts[1:]):
                out["rail"].append(S.bar(p, q, hr["rail"], hr["rail"]))
            for foot, top in rail["posts"]:
                out["rail"].append(S.bar(foot, top, hr["post"], hr["post"]))
        runs = []
    for run in runs:
        t0, t1 = run[0]["t0"], run[-1]["t1"]
        z_lo = min(min(s["z0"], s["z1"]) for s in run)
        z_hi = max(max(s["z0"], s["z1"]) for s in run)
        if run[0]["kind"] == "ramp":
            want, sides = rec.get("handrails"), (1.0, -1.0)
            za, zc = run[0]["z0"], run[-1]["z1"]
        else:
            # a flight of s risers has s - 1 treads: its rise is their spread and two risers
            want = (z_hi - z_lo) + 2.0 * float(rec.get("riser") or 0.15) > float(rules["handrail_from"]) + 1e-6
            sides = (1.0,)
            first, last = run[0], run[-1]
            za, zc = first["z0"], last["z0"]
        if not want:
            continue
        for side in sides:
            s_off = side * (h - hr["inset"])
            p0 = (*_at(fr, t0, s_off), za + hr["height"])
            p1 = (*_at(fr, t1, s_off), zc + hr["height"])
            out["rail"].append(S.bar(p0, p1, hr["rail"], hr["rail"]))
            for p in (p0, p1):
                out["rail"].append(S.bar((p[0], p[1], p[2] - hr["height"]), p, hr["post"], hr["post"]))
    return out


def walk_edging(area: dict, gz: Callable, walk: Sequence = (), piece_m: float = 2.0) -> list:
    """The edging of a path left on the ground (a walk): a stone strip ``edging_t`` wide along both long sides,
    following the ground (``edging_up`` over it, ``edging_down`` under it), in pieces of ``piece_m``; none against
    ``walk`` (pure)."""
    from wenart.blender import site as S

    fr = strip_frame(area.get("polygon") or [])
    if fr is None:
        return []
    h = fr["width"] / 2.0
    t = GRADE["edging_t"]
    out = []
    k = max(1, int(math.ceil(fr["length"] / piece_m)))
    for j in range(k):
        c0, c1 = fr["length"] * j / k, fr["length"] * (j + 1) / k
        for side in (1.0, -1.0):
            if any(G.point_in_polygon(_at(fr, (c0 + c1) / 2.0, side * (h + 0.1)), w) for w in walk):
                continue
            piece = _slice(fr, c0, c1, min(side * h, side * (h + t)), max(side * h, side * (h + t)))
            g = [gz(*q) for q in piece]
            out.append(_sloped_prism(piece, min(g) - GRADE["edging_down"],
                                     [gv + S.PAVING_LIFT + GRADE["edging_up"] for gv in g]))
    return out


# --------------------------------------------------------------------------
# Review: the model review's M15
# --------------------------------------------------------------------------

def _f(severity: str, target, message: str, rule: str, kind: str, **metrics) -> dict:
    """One finding in the model review's shape (``model_review._v``), built here so the site and the architect do not
    import the model review (and the build) through this module."""
    out = {"check": CHECK, "severity": severity, "target": target, "room_id": None, "message": message,
           "metrics": dict(metrics, rule=rule, model_review=True)}
    if kind:
        out["kind"] = kind
    return out


def _quad_overlap(a, b) -> bool:
    from wenart.blender import site as S
    return S.convex_overlap(a, b, tol=0.01)


def review(site: Optional[dict], manifest: Optional[dict] = None) -> tuple[list[dict], int]:
    """M15: the grading of the site as a landscape architect would check it (pure; module docstring), on the site
    plan of ``build.prepare`` (``prep["site"]``, the architect's paths in) and, when given, the scene manifest's site
    block (the materials as built). Returns ``(findings, checked)``; every finding names its rule (``metrics.rule``:
    G1-G7) and its element."""
    from wenart.blender import site as S

    findings: list[dict] = []
    if not site or not site.get("terrain"):
        return findings, 0
    terrain = plan_terrain(site)
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    tol = S.PLATFORM["level_tol"]
    pfs = list(site.get("platforms") or [])
    bands = [pf for pf in pfs if pf.get("parent")]
    checked = 0
    # G1: every tier planted; the tiers of one side at one level each (no staircase of boxes)
    for b in bands:
        checked += 1
        plants = (b.get("planting") or {}).get("plants") or drawn_on(b, site.get("trees") or [])
        if not plants:
            findings.append(_f("major", b["id"], f"terrace tier {b['id']} of {b['parent']} at {float(b['z']):+.2f} m is "
                               f"a bare box: no planting on it (a landscape architect plants every terrace)",
                               "G1", "taste", parent=b["parent"]))
    for i, b in enumerate(bands):
        for o in bands[i + 1:]:
            if o["parent"] != b["parent"] or o.get("step") != b.get("step") or \
                    (o.get("stepped_from") or {}).get("direction") != (b.get("stepped_from") or {}).get("direction"):
                continue
            dz = abs(float(o["z"]) - float(b["z"]))
            if dz > tol and S.convex_gap(b["polygon"], o["polygon"]) < 0.02:
                findings.append(_f("major", b["id"], f"terrace tiers {b['id']} ({float(b['z']):+.2f} m) and {o['id']} "
                                   f"({float(o['z']):+.2f} m) of one side of {b['parent']} sit side by side at levels "
                                   f"{dz:.2f} m apart: boxes stacked like stairs (one level per tier along a side)",
                                   "G1", "taste", other=o["id"], dz_m=round(dz, 3)))
    # G2: every tread on its riser and the ground, never buried by the ground, never through a planter, wall or hedge
    holes = S.ground_holes(site)
    pools = [p["polygon"] for p in site.get("pools") or [] if len(p.get("polygon") or []) >= 3]
    tt = GRADE["tread_tol_m"]
    parts_of = {pf["id"]: S.platform_parts(pf, terrain) for pf in pfs if not pf.get("sloped")}
    for pf in pfs:
        if pf.get("steps_edge") is None or pf.get("sloped") or pf.get("elevated"):
            continue
        checked += 1
        parts = parts_of.get(pf["id"]) or []
        recs = next((q.get("treads") for q in parts if q["part"] == "steps"), None) or []
        up = S.up_flight(pf, terrain)
        if pf.get("steps_dir") != "up" and not recs:
            recs = _legacy_treads(parts, gz)
        foot = down_flight(pf, gz) if pf.get("steps_dir") != "up" else None
        footprint = (foot or {}).get("footprint") or (up or {}).get("footprint")
        in_hole = bool(footprint) and any(_same(footprint, h) for h in holes)
        findings += tread_findings(f"the flight on {pf['id']} edge {pf['steps_edge']}", pf["id"], recs, in_hole)
        if footprint:
            others = [(q["id"], q["polygon"]) for q in pfs if q is not pf and q.get("parent") != pf["id"]
                      and not q.get("sloped")]
            others += [(q["id"], q["polygon"]) for q in bands if q.get("parent") == pf["id"]
                       and not (foot and foot.get("on_band") and abs(float(q["z"]) - float(foot["foot_z"])) <= tol)]
            hit = next((qid for qid, poly in others if _quad_overlap(footprint, poly)), None)
            hit = hit or next((f"hedge {h}" for h, poly in ((h.get("id"), p) for h in site.get("hedges") or []
                                                           for p in S._hedge_footprints(h))
                               if _quad_overlap(footprint, poly)), None)
            hit = hit or next((f"pool {j}" for j, poly in enumerate(pools) if _quad_overlap(footprint, poly)), None)
            if hit:
                findings.append(_f("major", pf["id"], f"the flight on {pf['id']} edge {pf['steps_edge']} runs through "
                                   f"{hit} (steps never cut through a planter, a wall or a hedge)", "G2", "geometry",
                                   through=hit))
    for st in (site.get("inferred") or {}).get("steps") or []:
        checked += 1
        for blk in st.get("blocks") or []:
            g = [gz(*q) for q in blk["polygon"]]
            if float(blk["z_top"]) < max(g) - tt and len(blk["polygon"]) >= 3:
                findings.append(_f("major", st.get("opening_id"), f"a tread of the entrance steps of "
                                   f"{st.get('opening_id')} lies {max(g) - float(blk['z_top']):.2f} m under the ground "
                                   f"beside it", "G2", "geometry"))
                break
    # G3 / G4: paths level across, at most 1:12 along unless stepped; ramps on accessible routes only, within the rule
    acc = accessible_paths(site)
    rules = level_rules()
    for rec in graded_paths(site):
        checked += 1
        pid = rec.get("id")
        if not rec["graded"]:
            if rec.get("frame") is None and len(rec.get("polygon") or []) >= 3:
                # a path drawn as no straight strip stays draped: it may not lie on a slope steeper than a walk's
                poly = [tuple(map(float, q[:2])) for q in rec["polygon"]]
                pts = poly + [G.polygon_centroid(poly)]
                zs = [gz(*q) for q in pts]
                grade = max((abs(zs[i] - zs[j]) / max(G.distance(pts[i], pts[j]), 0.5)
                             for i in range(len(pts)) for j in range(i + 1, len(pts))), default=0.0)
                if grade > GRADE["slope_walk_max"] + 1e-6:
                    findings.append(_f("major", pid, f"path {pid} is draped on a {grade * 100:.0f} % slope (no straight "
                                       f"strip the grading can lay level across and step)", "G3", "no_sense",
                                       grade=round(grade, 3)))
            continue
        if rec["kind"] == "stepped":
            if rec.get("too_steep"):
                findings.append(_f("major", pid, f"path {pid}: the slope is steeper than a stair can follow (treads "
                                   f"{rec.get('tread', 0):.2f} m)", "G3", "no_sense", local=rec.get("local")))
            if any(s > int(rules["landing_every_risers"]) for s in rec.get("flights") or []):
                findings.append(_f("major", pid, f"path {pid}: a flight of more than {rules['landing_every_risers']} "
                                   f"risers without a landing", "G3", "no_sense"))
        if rec["kind"] == "ramp" and str(pid) not in acc:
            findings.append(_f("major", pid, f"path {pid} is a ramp on a route no accessibility asks for", "G4",
                               "no_sense"))
        if rec["kind"] == "ramp":
            from wenart.levels import rules as LM
            want = LM.ramp_for(float(rec.get("rise") or 0.0), rules)
            if want and float(rec.get("slope") or 0.0) > float(want["slope"]) + 1e-6:
                findings.append(_f("major", pid, f"ramp {pid}: {float(rec['slope']) * 100:.1f} % is steeper than "
                                   f"{want['ratio']} for its {rec.get('rise'):.2f} m rise", "G4", "no_sense"))
        if rec.get("accessible_open"):
            findings.append(_f("minor", pid, f"path {pid}: {rec['accessible_open']}", "G4", "no_sense"))
    # as built: a path object the scene manifest says was draped on the ground (a build before 28 Oct 2026) on a
    # slope the rule lays level across or steps is the tilted strip the user saw (real04's 25 % access paths)
    areas = {str(a.get("id")): a for a in site.get("areas") or []}
    for o in (manifest or {}).get("objects") or []:
        if o.get("kind") != "site_area" or o.get("area_kind") != "path" or not (o.get("assumed") or {}).get("draped"):
            continue
        a = areas.get(str(o.get("wenart_id")))
        if a is None:
            continue
        rec = path_plan(a, gz)
        if rec.get("graded"):
            findings.append(_f("major", a.get("id"), f"path {a.get('id')} was built draped on the slope: "
                               f"{float(rec.get('local') or 0) * 100:.0f} % along and "
                               f"{float(rec.get('cross') or 0) * 100:.0f} % across, a tilted strip (level across, "
                               f"stepped where steeper than 1:12)", "G3", "no_sense", local=rec.get("local"),
                               cross=rec.get("cross")))
    # G5: banks no steeper than their finish
    for row in terrain.get("grading") or []:
        checked += 1
        limit = GRADE["lawn_slope"] if row.get("finish") == "lawn" else GRADE["planted_slope"]
        if float(row["slope"]) > limit + 1e-6:
            findings.append(_f("major", row.get("platform"), f"the {row.get('finish')} bank of {row.get('platform')} "
                               f"edge {row.get('edge')} is 1:{1.0 / float(row['slope']):.1f}, steeper than "
                               f"1:{1.0 / limit:.0f}", "G5", "no_sense"))
    # G6: walls in the house's base stone with a coping
    # the build's own rule when the plan carries no wall look (build_site: grading.wall_look of the style family)
    wl = (site.get("wall_look") or wall_look({}, site.get("style_family"))).get("material")
    built_walls = [pf for pf in pfs if not pf.get("sloped") and not pf.get("elevated")
                   and any(q["part"] == "wall" for q in parts_of.get(pf["id"]) or [])]
    if built_walls:
        checked += 1
        built_mat = None
        for p in ((manifest or {}).get("site") or {}).get("platforms") or []:
            m = (p.get("materials") or {}).get("wall")
            if m:
                built_mat = str(m)
                break
        slug = (built_mat or wl or S.PLATFORM_LOOKS["wall"][0]).split("__")[0]
        if slug in CONCRETE_SLUGS:
            findings.append(_f("major", "site walls", f"the retaining walls of {len(built_walls)} platform(s) are bare "
                               f"{slug} while the house's base is stone: walls in the base stone or render with a "
                               f"coping", "G6", "taste", material=slug))
        uncoped = [pf["id"] for pf in built_walls if not any(q["part"] == "coping" for q in parts_of.get(pf["id"]) or [])]
        built = [o for o in (manifest or {}).get("objects") or [] if o.get("site_part") == "platform"]
        if built and not any(o.get("part") == "coping" for o in built):
            uncoped = uncoped or [pf["id"] for pf in built_walls]          # as built: no coping object at all
        if uncoped:
            findings.append(_f("major", uncoped[0], f"{len(uncoped)} platform(s) build retaining walls without a "
                               f"coping ({', '.join(uncoped[:4])})", "G6", "taste", platforms=uncoped))
    # G7: each use its own floor (never one look everywhere)
    floors = ((manifest or {}).get("site") or {}).get("floors")
    uses: dict = {}
    objs = [o for o in (manifest or {}).get("objects") or [] if o.get("slug")]
    if floors and floors.get("built"):
        for use, slug in floors["built"].items():
            uses.setdefault(str(slug), set()).add(use)
    elif objs:
        # a build before 28 Oct 2026 (no floor record): the floors as built, by the slugs of the site's objects
        for o in objs:
            use = None
            if o.get("kind") == "site_area":
                use = AREA_USES.get(str(o.get("area_kind")))
            elif o.get("site_part") == "platform" and o.get("part") == "slab" and not o.get("platform_parent"):
                use = {"parking": "drive", "path": "path"}.get(o.get("platform_kind"), "terrace")
            elif o.get("site_part") == "platform" and o.get("part") == "steps":
                use = "steps"
            if use:
                uses.setdefault(str(o["slug"]).split("__")[0], set()).add(use)
    else:
        fs = floor_set(None, site.get("style_family"))
        kinds = {"terrace": any(slab_use(pf) == "terrace" for pf in pfs if not pf.get("parent")),
                 "pool_deck": any(slab_use(pf) == "pool_deck" for pf in pfs if not pf.get("parent")),
                 "drive": any(pf.get("kind") == "parking" for pf in pfs),
                 "path": any(a.get("kind") == "path" for a in site.get("areas") or []),
                 "steps": any(pf.get("steps_edge") is not None for pf in pfs)}
        for use, present in kinds.items():
            if present:
                uses.setdefault(fs[use]["material"], set()).add(use)
    n_uses = sum(len(v) for v in uses.values())
    if n_uses >= 3:
        checked += 1
        if len(uses) == 1:
            slug = next(iter(uses))
            findings.append(_f("major", "site floors", f"every outdoor floor ({', '.join(sorted(next(iter(uses.values()))))}) "
                               f"is {slug}: the terrace, the steps, the path and the drive each get their own "
                               f"material (one language with the house's base)", "G7", "taste", material=slug))
    # 30 Oct 2026 (lessons UL129, UL141-UL144): G8-G12, site elements only where they make sense (site_sense)
    from wenart.blender import site_sense as SS

    more, n = SS.review(site, manifest)
    return findings + more, checked + n


def grading_problems(site_or_prep: Optional[dict], manifest: Optional[dict] = None) -> list[dict]:
    """The crude grading of a site in a plain list (pure; for Argus's lessons line, 28 Oct 2026): ``site_or_prep`` is
    the site plan (``build.prepare(...)["site"]``) or the whole ``build.prepare`` record (its ``site``); ``manifest``
    the scene manifest when there is one (the floors and wall materials as built). One dict per problem: ``{"target":
    platform / tier / flight / path / wall id, "message", "severity": major | minor, "rule": G1-G7, "kind"}`` (the
    rules of ``review``: G1 bare terrace boxes or tiers of a side at different levels, G2 loose treads that do not sit on
    their riser or the ground, or steps through a planter, wall, hedge or pool, G3 a path draped on a slope steeper than
    1:12 or a stair too steep, G4 a ramp off an accessible route or steeper than its rise allows, G5 a bank steeper than
    its finish, G6 bare concrete retaining walls or walls without a coping, G7 one floor look for every outdoor use).
    An empty list when the record holds no site plan."""
    rec = site_or_prep or {}
    site = rec.get("site") if isinstance(rec.get("site"), dict) and "terrain" not in rec else rec
    if not isinstance(site, dict) or not site.get("terrain"):
        return []
    found, _n = review(site, manifest)
    return [{"target": f.get("target"), "message": f.get("message"), "severity": f.get("severity"),
             "rule": (f.get("metrics") or {}).get("rule"), "kind": f.get("kind")} for f in found]


def tread_findings(name: str, target, treads: Sequence[dict], in_hole: bool) -> list[dict]:
    """G2 for one flight's treads as built (pure; ``treads``: ``{"z_top", "z_bottom", "ground_min", "ground_max"}``):
    a tread whose block ends over the ground under it floats (a loose bar or slab over the grass); a tread whose top
    lies ``tread_tol_m`` under the ground beside it while the flight is no hole in the ground (with cheek walls holding
    it) is buried, the lawn between the treads. The first such tread of the flight is the finding."""
    tt = GRADE["tread_tol_m"]
    for k, r in enumerate(treads):
        floating = float(r["z_bottom"]) > float(r["ground_min"]) + 0.01
        buried = float(r["z_top"]) < float(r["ground_max"]) - tt and not (in_hole and r.get("in_hole", in_hole))
        if floating or buried:
            what = (f"floats over the ground (its block ends {float(r['z_bottom']) - float(r['ground_min']):.2f} m "
                    f"over it): a loose slab over the grass" if floating else
                    f"lies {float(r['ground_max']) - float(r['z_top']):.2f} m under the ground beside it with no hole "
                    f"and no cheek wall: a loose tread in the grass")
            return [_f("major", target, f"step {k + 1} of {name} {what}", "G2", "geometry", tread=k + 1,
                       z_top=r["z_top"], ground_max=r["ground_max"], floating=floating)]
    return []


def _same(a, b) -> bool:
    if len(a) != len(b):
        return False
    return all(min(G.distance(p, q) for q in b) < 1e-6 for p in a)


def _legacy_treads(parts: Sequence[dict], gz: Callable) -> list[dict]:
    """The treads of a ``steps`` part built before 28 Oct 2026 (prisms of 8 vertices): top, bottom and ground."""
    st = next((q for q in parts if q["part"] == "steps"), None)
    if st is None:
        return []
    v = st["verts"]
    out = []
    for k in range(0, len(v) - 7, 8):
        box = v[k:k + 8]
        xy = [(p[0], p[1]) for p in box[4:]]
        c = (sum(p[0] for p in xy) / 4.0, sum(p[1] for p in xy) / 4.0)
        g = [gz(*p) for p in xy] + [gz(*c)]
        out.append({"z_top": max(p[2] for p in box), "z_bottom": min(p[2] for p in box), "ground_max": max(g),
                    "ground_min": min(g), "in_hole": False})
    return out
