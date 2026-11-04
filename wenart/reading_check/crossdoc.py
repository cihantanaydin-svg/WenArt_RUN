"""Cross-document findings: two drawings of one building that disagree, found by code (4 Nov 2026, Milestone 14 R5).

What: ``findings(out_dir) -> list[dict]`` reads a pipeline output (``building.json``, ``sheets.json``, the level
pages and the other regions of the converted DXF) and returns findings shaped like ``wenart.reading_check._finding``
(``check``, ``name``, ``severity`` critical | major | minor | info, ``level_id``, ``message``) plus ``sources`` (the
two documents or regions that disagree), ``place`` ``{x, y}`` in building metres when known and ``element_ids`` when
known. ``CHECKS`` names them:

- RC8 the elevations' openings against the plans, per floor and side (positions matched within ``MATCH_M`` when the
  facade's left end can be aligned); and the plans' own facade: an outer opening of a plan drawn for several floors
  that is missing on some of them (UL303);
- RC9 the sections against the levels: floor marks, storey heights (``STOREY_M``), the storeys the section names, the
  ground line, and the heights conflicts the reading already recorded;
- RC10 the site plan against the model: the buildings it names (``A BLOK``, ``2 ADET VİLLA``) or draws, the plot
  around the footprint, a pool label with no pool;
- RC11 size tags (``80/210``) against the openings read near them;
- RC12 typical floors against their copies, mirrored halves against their twins.

Why: the user (4 Nov 2026): "some AI or something else to give the feedbacks by itself instead of me". The reading
extracts evidence from several drawings and compared little of it; the user's corrections of 3 and 4 Nov (the window
on L0 only, the ground one storey off, the second villa, the pool, the 80/210 door) were each a disagreement between
two drawings that code can see.

How: pure functions per check (``rc8`` ... ``rc12``) on the building and sheets dicts and on the texts read from the
DXF (``level_texts``, ``region_texts``); ``findings`` reads the files and runs them. Run it with
``python -m wenart.reading_check.crossdoc --out DIR``. The main session wires the checks into
``wenart.reading_check.check``.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

CHECKS = {"RC8": "elevation openings against the plans, per floor",
          "RC9": "sections against the levels",
          "RC10": "site plan against the model",
          "RC11": "size tags against the openings read",
          "RC12": "typical floors and mirrored halves against each other"}

# RC8
MATCH_M = 0.5                  # an elevation opening and a plan opening this close along the facade are one opening
ALIGN_SEARCH_M = 1.5           # the facade's left end may be off by this much (a pilaster, a balcony, the roof's eaves)
ALIGN_MIN_SHARE = 0.3          # aligned when this share of the smaller side's openings match (at least ALIGN_MIN_N)
ALIGN_MIN_N = 2
SIDE_ANGLE_DEG = 45.0          # a wall faces a side when its outward normal is within this (to_building.SIDE_ANGLE_DEG)
SLIT_CLOSE_M = 0.03            # the wall union's slits closed (topology.SLIT_CLOSE_M)
BAND_TOL_M = 0.3               # an opening's mid height this far below a level's floor still belongs to it
STACK_MATCH_M = 0.3            # the plans' facade: an outer opening on one floor and on another this close are one
NORTH_CANDIDATES_DEG = (0.0, 90.0, 180.0, 270.0)
LOCAL_SIDES = {"right": 0.0, "back": 90.0, "left": 180.0, "front": 270.0}
MAJOR_EXTRA_N = 2              # a level with this many openings on the elevation only is major
# RC9
STOREY_M = (2.0, 8.0)          # a storey's floor-to-floor height outside this is no storey (UL 4 Nov 2026, real07)
LEVEL_TOL_M = 0.05             # the section's floor mark and the model's level differ by more than this
STOREY_MARK_TOL_M = 0.10       # the storeys' floor marks the section names against the model's levels
DOOR_UNDER_GROUND_M = 0.3      # an outer door whose head is this far under the section's ground opens into the earth
SLAB_BANDS_RE = re.compile(r"draws (\d+) slab bands?, the plans (\d+) levels?")
HEIGHT_CONFLICTS = {"section_width_mismatch": "minor", "level_mark_mismatch": "major"}
# RC10
BLOCK_RES = [re.compile(r"(?<![A-Z0-9])([A-Z]|\d{1,2})\s*[-.]?\s*BLO(?:K|CK|C)U?(?![A-Z])"),
             re.compile(r"(?<![A-Z0-9])BLO(?:K|CK|C)\s*[-.]?\s*([A-Z]|\d{1,2})(?![A-Z0-9])")]
COUNT_RES = [re.compile(r"(?<![\d.,])(\d{1,2})\s*ADET\s+(?:VILLA|KONUT|BINA|BLOK|EV|DUBLEKS|MESKEN|IKIZ)"),
             re.compile(r"(?<![\d.,])(\d{1,2})\s+(?:VILLAS|HOUSES|BUILDINGS|BLOCKS|DWELLINGS)(?![A-Z])")]
POOL_RE = re.compile(r"(?<![A-Z])(?:HAVUZ|HAVUZU|POOL|SWIMMING|PISCINE|PISCINA|SCHWIMMBAD|POOLS)(?![A-Z])")
PLOT_TOL_M = 0.10
# RC11: SIZE_TAG_RE is ``wenart.ingest.generic.core.SIZE_TAG_RE`` (imported in ``size_tags``; copied here only if the
# import fails): width/height in cm, "90/210", "90 / 210"
SIZE_TAG_FALLBACK_RE = re.compile(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")
TAG_REACH_M = 0.8              # a tag stands this close to a wall of its level, its opening this close to it
TAG_WIDTH_TOL_M = 0.10
TAG_SIZE_CM = ((40, 600), (40, 400))
TAG_LAYER_ROLES = ("door", "window", "glass")
TAG_NEAREST_M = 1.5            # the nearest opening named in the message
TAG_MAJOR_N = 3
# RC12
TWIN_AREA_SHARE = 0.05
TWIN_RESIDUAL_M = 0.10
ROOM_OPENING_REACH_M = 0.10    # an opening belongs to a room whose polygon is this close beyond its wall's half thickness


def _finding(check: str, severity: str, level: Optional[str], message: str, sources: list,
             place: Optional[tuple] = None, element_ids: Optional[list] = None, **extra) -> dict:
    out = {"check": check, "name": CHECKS[check], "severity": severity, "level_id": level, "message": message,
           "sources": [s for s in sources if s]}
    if place is not None:
        out["place"] = {"x": round(float(place[0]), 3), "y": round(float(place[1]), 3)}
    if element_ids:
        out["element_ids"] = list(element_ids)
    out.update(extra)
    return out


# ------------------------------------------------------------------------------------------------------------ geometry
def base_levels(building: dict) -> list[dict]:
    """The base levels (``base_level_id`` null) by elevation."""
    return sorted((lv for lv in building.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: (float(lv.get("elevation") or 0.0), lv.get("order") or 0))


def _value(v) -> Optional[float]:
    if isinstance(v, dict):
        v = v.get("value")
    return float(v) if isinstance(v, (int, float)) else None


def level_bands(levels: list[dict]) -> dict:
    """``{level_id: (floor z, next floor z)}``: up to the next base level, the top one by its floor-to-floor height
    (else its ceiling and 0.3 m)."""
    out = {}
    for k, lv in enumerate(levels):
        lo = float(lv.get("elevation") or 0.0)
        if k + 1 < len(levels):
            hi = float(levels[k + 1].get("elevation") or 0.0)
        else:
            hi = lo + (_value(lv.get("floor_to_floor")) or (float(lv.get("ceiling_height") or 2.7) + 0.3))
        out[lv["id"]] = (lo, hi)
    return out


def level_of_z(bands: dict, sill: float, head: float) -> Optional[str]:
    """The level an opening seen on an elevation (sill and head in building z) belongs to: the band holding its
    middle (``BAND_TOL_M`` below a floor still counts)."""
    mid = (sill + head) / 2.0
    for lid, (lo, hi) in bands.items():
        if lo <= mid < hi:
            return lid
    return next((lid for lid, (lo, hi) in bands.items() if lo - BAND_TOL_M <= mid < hi + BAND_TOL_M), None)


def wall_polygon(w: dict):
    line = LineString([tuple(w["start"]), tuple(w["end"])])
    if line.length <= 0:
        return None
    return line.buffer(max(float(w.get("thickness") or 0.1), 0.02) / 2.0, cap_style=2, join_style=2)


def _unit(w: dict) -> Optional[tuple[float, float]]:
    (x0, y0), (x1, y1) = w["start"], w["end"]
    L = math.hypot(x1 - x0, y1 - y0)
    return None if L <= 0 else ((x1 - x0) / L, (y1 - y0) / L)


def opening_polygon(o: dict, wall: Optional[dict]):
    """The rectangle an opening fills in its wall (its width along the wall, the wall's thickness across)."""
    if wall is None or not o.get("center") or not o.get("width"):
        return None
    u = _unit(wall)
    if u is None:
        return None
    cx, cy = o["center"]
    h = float(o["width"]) / 2.0
    line = LineString([(cx - u[0] * h, cy - u[1] * h), (cx + u[0] * h, cy + u[1] * h)])
    return line.buffer(max(float(wall.get("thickness") or 0.1), 0.02) / 2.0, cap_style=2, join_style=2)


def level_outline(walls: list[dict], openings: list[dict]):
    """The filled outer outline of a level: the walls and the openings in them united, slits closed (the equivalent of
    ``wenart.ingest.generic.topology.bridged_union`` on the building's dicts), its largest part's exterior."""
    by_id = {w["id"]: w for w in walls}
    polys = [p for p in (wall_polygon(w) for w in walls) if p is not None]
    polys += [p for p in (opening_polygon(o, by_id.get(o.get("wall_id"))) for o in openings
                          if not o.get("virtual")) if p is not None]
    if not polys:
        return None
    u = unary_union(polys).buffer(SLIT_CLOSE_M, join_style=2).buffer(-SLIT_CLOSE_M, join_style=2)
    parts = [g for g in getattr(u, "geoms", [u]) if g.geom_type == "Polygon" and not g.is_empty]
    if not parts:
        return None
    return Polygon(max(parts, key=lambda g: g.area).exterior)


def outward_deg(wall: dict, filled) -> Optional[float]:
    """The outward normal of an exterior wall, degrees ccw from +X (``to_building._outward_deg``)."""
    if filled is None:
        return None
    (x0, y0), (x1, y1) = wall["start"], wall["end"]
    L = math.hypot(x1 - x0, y1 - y0)
    if L <= 0:
        return None
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    reach = float(wall.get("thickness") or 0.1) / 2.0 + 0.05
    for sign in (1.0, -1.0):
        if not filled.contains(Point(mx + sign * nx * reach, my + sign * ny * reach)):
            return math.degrees(math.atan2(sign * ny, sign * nx)) % 360.0
    return None


def angle_gap(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


class LevelGeometry:
    """A level's walls, openings and outline, the outward normal of its exterior walls (cached)."""

    def __init__(self, building: dict, lid: str):
        self.lid = lid
        self.walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
        self.openings = [o for o in building.get("openings") or [] if o.get("level_id") == lid and not o.get("virtual")]
        self.by_id = {w["id"]: w for w in self.walls}
        self.filled = level_outline(self.walls, self.openings)
        self.normals = {w["id"]: outward_deg(w, self.filled) for w in self.walls if w.get("exterior")}

    def facing(self, normal: float) -> list[dict]:
        """The openings on the exterior walls facing ``normal``."""
        ids = {wid for wid, n in self.normals.items() if n is not None and angle_gap(n, normal) <= SIDE_ANGLE_DEG}
        return [o for o in self.openings if o.get("wall_id") in ids and o.get("center")]


def _axis(normal: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """(along, out): the facade's left-to-right direction seen from outside, and its outward normal."""
    r = math.radians(normal + 90.0)
    n = math.radians(normal)
    return (math.cos(r), math.sin(r)), (math.cos(n), math.sin(n))


def _dot(p, u) -> float:
    return p[0] * u[0] + p[1] * u[1]


def _greedy(es: list[float], ps: list[float], shift: float, tol: float) -> list[tuple[int, int]]:
    pairs = sorted(((abs(e - (p + shift)), i, j) for i, e in enumerate(es) for j, p in enumerate(ps)
                    if abs(e - (p + shift)) <= tol))
    used_i, used_j, out = set(), set(), []
    for _, i, j in pairs:
        if i not in used_i and j not in used_j:
            used_i.add(i)
            used_j.add(j)
            out.append((i, j))
    return out


# ---------------------------------------------------------------------------------------------------------------- RC8
def _elevations(building: dict, sheets: dict) -> list[dict]:
    els = (building.get("facade") or {}).get("elevations")
    if els:
        return els
    return [dict(s, region_id=s.get("region")) for s in (sheets.get("exterior") or {}).get("openings_seen") or []]


def _north(building: dict, sheets: dict) -> Optional[float]:
    n = ((sheets.get("exterior") or {}).get("north") or {}).get("value")
    if n is None:
        n = (building.get("site") or {}).get("north_deg")
        n = _value(n)
    return n


def _ground_z(sheets: dict) -> Optional[float]:
    zs = [_value(g.get("z")) for g in (sheets.get("heights") or {}).get("ground") or []]
    zs = [z for z in zs if z is not None]
    return min(zs) if zs else None


def _fmt_x(xs: list[float]) -> str:
    return ", ".join(f"{x:.2f}" for x in sorted(xs)[:8]) + (" ..." if len(xs) > 8 else "")


def rc8(building: dict, sheets: dict) -> list[dict]:
    """The elevations' openings against the plans' openings on the walls facing that side, per floor (the module
    docstring); then ``rc8_stacked``. Without a north arrow the compass sides are placed by fit: of the four building
    axes as north (``north_deg`` 0, 90, 180, 270) the one under which the most elevation openings match plan openings
    wins (``inferred``, said in an info finding); none matching, the elevations are not compared."""
    from wenart.sheets import exterior as EX

    out: list[dict] = []
    levels = base_levels(building)
    ctx = {"levels": levels, "bands": level_bands(levels), "region_of": {lv["id"]: lv.get("region_id") for lv in levels},
           "ground": _ground_z(sheets), "geo": {lv["id"]: LevelGeometry(building, lv["id"]) for lv in levels}}
    north = _north(building, sheets)
    els, empty = [], []
    for el in _elevations(building, sheets):
        rid, side, title = el.get("region_id") or el.get("region"), el.get("side"), el.get("title") or ""
        name = f"{side} elevation {rid}" + (f" ('{title.strip()}')" if title else "")
        positions = [p for p in el.get("positions_m") or [] if p.get("sill") is not None and p.get("head") is not None]
        if not positions:
            empty.append(name)
            continue
        els.append((el, name, positions))
    inferred = None
    if north is None and any(EX.normal_deg(el.get("side"), None) is None for el, _, _ in els):
        scores = {}
        for cand in NORTH_CANDIDATES_DEG:
            scores[cand] = sum(_compare_elevation(el, EX.normal_deg(el.get("side"), cand), name, positions, ctx)[1]
                               for el, name, positions in els if EX.normal_deg(el.get("side"), cand) is not None)
        best = max(NORTH_CANDIDATES_DEG, key=lambda c: scores[c])
        if scores[best] > 0 and sorted(scores.values())[-2] < scores[best]:
            north = inferred = best
            others = ", ".join(f"{c:.0f}: {v}" for c, v in scores.items() if c != best)
            out.append(_finding("RC8", "info", None, f"no north arrow read: the compass sides placed by fit, north = "
                                f"{best:.0f} deg from the building's +Y ({scores[best]} elevation openings match plan "
                                f"openings; the other axes {others}) (inferred)", ["elevations", "plans"],
                                north_inferred_deg=best))
    no_north = []
    for el, name, positions in els:
        normal = EX.normal_deg(el.get("side"), north)
        if normal is None:
            no_north.append(name)
            continue
        found, _ = _compare_elevation(el, normal, name, positions, ctx)
        if inferred is not None:
            for f in found:
                f["north_inferred_deg"] = inferred
        out += found
    if no_north:
        out.append(_finding("RC8", "info", None, "not compared with the plans: " + "; ".join(no_north)
                            + " (a compass side needs the north arrow; none was read and no axis fits)",
                            ["elevations", "site plan"]))
    if empty:
        out.append(_finding("RC8", "info", None, "no window or door read on " + "; ".join(empty)
                            + ": nothing to compare", ["elevations"]))
    return out + rc8_stacked(building)


def _compare_elevation(el: dict, normal: float, name: str, positions: list, ctx: dict) -> tuple[list, int]:
    """(findings, openings matched) of one elevation seen along ``normal`` against the plans (``rc8``)."""
    out: list[dict] = []
    levels, bands, region_of, ground, geo = (ctx["levels"], ctx["bands"], ctx["region_of"], ctx["ground"], ctx["geo"])
    rid, side, title = el.get("region_id") or el.get("region"), el.get("side"), el.get("title") or ""
    along, outv = _axis(normal)
    left = min((_dot(p, along) for g in geo.values() if g.filled is not None
                for p in g.filled.exterior.coords), default=0.0)
    front = max((_dot(p, outv) for g in geo.values() if g.filled is not None
                 for p in g.filled.exterior.coords), default=0.0)
    seen_by: dict = {}
    unplaced = []
    for p in positions:
        lid = level_of_z(bands, float(p["sill"]), float(p["head"]))
        (seen_by.setdefault(lid, []) if lid else unplaced).append(p)
    plan_by: dict = {}
    for lid, g in geo.items():
        ops = []
        for o in g.facing(normal):
            head = bands[lid][0] + float(o.get("sill_height") or 0.0) + float(o.get("height") or 0.0)
            if ground is not None and head <= ground + 0.05:
                continue                     # under the ground line: an elevation does not draw it
            ops.append((_dot(o["center"], along) - left, o))
        plan_by[lid] = ops
    # One shift per elevation: the facade's left end as drawn against the plans' outline
    es_all = [(lid, float(p["x"])) for lid, ps in seen_by.items() for p in ps]
    cand = {0.0}
    for lid, ex in es_all:
        for px, _ in plan_by.get(lid, []):
            if abs(ex - px) <= ALIGN_SEARCH_M:
                cand.add(round(ex - px, 3))

    def score(shift: float) -> int:
        return sum(len(_greedy([float(p["x"]) for p in seen_by.get(lid, [])], [x for x, _ in plan_by.get(lid, [])],
                               shift, MATCH_M)) for lid in seen_by)

    best = max(sorted(cand, key=abs), key=score)
    matched = score(best)
    n_plan = sum(len(plan_by.get(lid, [])) for lid in seen_by)
    aligned = matched >= max(ALIGN_MIN_N, ALIGN_MIN_SHARE * min(len(es_all), n_plan or 1))
    for lv in levels:
        lid = lv["id"]
        es = seen_by.get(lid, [])
        ps = plan_by.get(lid, [])
        if not es and not ps:
            continue
        src = [f"elevation {rid}" + (f" ({title.strip()})" if title else ""),
               f"plan of {lid}" + (f" ({region_of.get(lid)})" if region_of.get(lid) else "")]
        ew = sum(1 for p in es if p["kind"] == "window")
        ed = len(es) - ew
        pw = sum(1 for _, o in ps if o.get("type") == "window")
        pd = sum(1 for _, o in ps if o.get("type") == "door")
        counts = (f"{name} shows {len(es)} opening(s) on {lid} ({ew} windows, {ed} doors); the plan has {len(ps)} "
                  f"on its walls facing {side} ({pw} windows, {pd} doors, {len(ps) - pw - pd} other)")
        if aligned:
            pairs = _greedy([float(p["x"]) for p in es], [x for x, _ in ps], best, MATCH_M)
            ei = {i for i, _ in pairs}
            pj = {j for _, j in pairs}
            e_only = [float(p["x"]) for i, p in enumerate(es) if i not in ei]
            p_only = [(x, o) for j, (x, o) in enumerate(ps) if j not in pj]
            if not e_only and not p_only:
                continue
            msg = counts + f"; positions aligned (shift {best:+.2f} m, {len(pairs)} matched within {MATCH_M} m)"
            if e_only:
                msg += f"; on the elevation only at x {_fmt_x(e_only)} m from its left end"
            if p_only:
                msg += "; on the plan only: " + ", ".join(f"{o['id']} ({o.get('type')}, x {x + best:.2f} m)"
                                                         for x, o in p_only[:8])
            n_e = len(e_only)
            place = None
            if e_only:
                t = e_only[0] - best + left
                place = (along[0] * t + outv[0] * front, along[1] * t + outv[1] * front)
            elif p_only:
                place = tuple(p_only[0][1]["center"])
            ids = [o["id"] for _, o in p_only]
        else:
            if len(es) == len(ps):
                continue
            n_e = max(len(es) - len(ps), 0)
            msg = counts + " (positions not aligned: counts compared)"
            place, ids = None, []
        sev = "major" if (n_e >= MAJOR_EXTRA_N or (es and not ps)) else "minor"
        out.append(_finding("RC8", sev, lid, msg, src, place, ids, side=side, region=rid))
    if unplaced:
        out.append(_finding("RC8", "minor", None, f"{name}: {len(unplaced)} of its {len(positions)} openings stand "
                            f"at no level's height (sills " + _fmt_x([float(p['sill']) for p in unplaced])
                            + " m): the elevation's heights and the levels disagree", [f"elevation {rid}",
                                                                                        "levels"], region=rid))
    return out, (matched if aligned else 0)


def rc8_stacked(building: dict) -> list[dict]:
    """The plans' own facade (4 Nov 2026, UL303 real10: "why there is not window here", the bedroom window read on L0
    only, missing on L1 to L6 drawn by the same plan): the outer openings of the levels drawn by one plan region (a
    typical floor and its copies) per side, by position along the facade; one there on some of those floors and
    missing on others is a finding (major when missing on 2 or more floors)."""
    out = []
    levels = base_levels(building)
    groups: dict = {}
    for lv in levels:
        key = lv.get("region_id") or lv.get("typical_of") or lv["id"]
        groups.setdefault(key, []).append(lv["id"])
    for key, lids in groups.items():
        if len(lids) < 2:
            continue
        geo = {lid: LevelGeometry(building, lid) for lid in lids}
        for side, normal in LOCAL_SIDES.items():
            along, _ = _axis(normal)
            per = {lid: [(_dot(o["center"], along), o) for o in g.facing(normal) if o.get("type") in ("window", "door")]
                   for lid, g in geo.items()}
            spots: list = []                     # (x, {lid: opening})
            for lid in lids:
                for x, o in per[lid]:
                    hit = next((s for s in spots if abs(s[0] - x) <= STACK_MATCH_M and lid not in s[1]), None)
                    if hit is None:
                        spots.append([x, {lid: o}])
                    else:
                        hit[1][lid] = o
            for x, have in spots:
                missing = [lid for lid in lids if lid not in have]
                if not missing or len(have) < 1:
                    continue
                o = next(iter(have.values()))
                sev = "major" if len(missing) >= 2 else "minor"
                out.append(_finding(
                    "RC8", sev, missing[0],
                    f"the {o.get('type')} {o['id']} ({float(o.get('width') or 0):.2f} m) on the {side} facade (+X "
                    f"{normal:.0f} deg) is on {', '.join(sorted(have))} but missing on {', '.join(missing)}: all drawn "
                    f"by plan {key}, so an elevation would show it on every one of those floors",
                    [f"plan {key} as {', '.join(sorted(have))}", f"plan {key} as {', '.join(missing)}"],
                    tuple(o["center"]), sorted(v["id"] for v in have.values()), side=side, missing_levels=missing))
    return out


# ---------------------------------------------------------------------------------------------------------------- RC9
def rc9(building: dict, sheets: dict, storeys: Optional[dict] = None, storey_el: Optional[dict] = None) -> list[dict]:
    """The sections against the levels (the module docstring). ``storeys``: ``{order: label}`` the sections name
    (``wenart.sheets.levels.storey_words``); ``storey_el``: ``{order: printed floor mark}``
    (``storey_elevations``)."""
    out: list[dict] = []
    heights = sheets.get("heights") or {}
    secs = ", ".join(heights.get("section_regions") or []) or "the section"
    sec_src = f"section {secs}"
    levels = base_levels(building)
    by_id = {lv["id"]: lv for lv in levels}
    for hl in heights.get("levels") or []:
        lv = by_id.get(hl.get("level_id"))
        fz = hl.get("floor_z") or {}
        if lv is None:
            continue
        if fz.get("method") == "assumed":
            out.append(_finding("RC9", "minor", lv["id"], f"{lv['id']}: the section's heights were not used "
                                f"({fz.get('note') or 'assumed'}): the floor at {float(fz.get('value') or 0):.2f} m "
                                f"is assumed", [sec_src, f"plan of {lv['id']}"]))
            continue
        v = _value(fz)
        if v is not None and abs(v - float(lv.get("elevation") or 0.0)) > LEVEL_TOL_M:
            out.append(_finding("RC9", "major", lv["id"], f"{lv['id']}: {sec_src} puts the floor at {v:.2f} m, the "
                                f"model at {float(lv.get('elevation') or 0):.2f} m "
                                f"({lv.get('elevation_source') or 'source unknown'})", [sec_src, f"level {lv['id']}"]))
    for k, lv in enumerate(levels):
        if k + 1 < len(levels):
            h = float(levels[k + 1].get("elevation") or 0) - float(lv.get("elevation") or 0)
            how = f"to {levels[k + 1]['id']}"
        else:
            h = _value(lv.get("floor_to_floor"))
            how = "floor to floor"
        if h is not None and not STOREY_M[0] <= h <= STOREY_M[1]:
            out.append(_finding("RC9", "major", lv["id"], f"{lv['id']}: a storey of {h:.2f} m ({how}) is outside "
                                f"{STOREY_M[0]:.1f}-{STOREY_M[1]:.1f} m: no storey has it", [sec_src, "levels"]))
    # The storeys the sections name against the base levels
    orders = {lv.get("order"): lv for lv in levels if lv.get("order") is not None}
    if storeys:
        named = sorted(o for o in storeys if isinstance(o, int))
        for o in named:
            if o not in orders:
                out.append(_finding("RC9", "major", None, f"{sec_src} names {storeys[o]} (order {o}); the model has no "
                                    f"level of that order (levels {', '.join(lv['id'] for lv in levels)})",
                                    [sec_src, "levels"]))
        if named:
            gaps = [lv for o, lv in orders.items() if named[0] < o < named[-1] and o not in storeys]
            for lv in gaps:
                out.append(_finding("RC9", "minor", lv["id"], f"{lv['id']} ({lv.get('label')}) lies between the "
                                    f"storeys {sec_src} names but is not named by it", [sec_src, f"level {lv['id']}"]))
    if storey_el:
        numeric = sorted((o, v) for o, v in storey_el.items() if isinstance(o, int))
        for (o1, v1), (o2, v2) in zip(numeric, numeric[1:]):
            if v2 <= v1:
                out.append(_finding("RC9", "major", None, f"{sec_src}: the floor mark of order {o2} ({v2:+.2f}) is not "
                                    f"above order {o1}'s ({v1:+.2f})", [sec_src]))
        datum = _value(heights.get("datum"))
        if datum is None and 0 in storey_el and 0 in orders:
            datum = float(storey_el[0]) - float(orders[0].get("elevation") or 0.0)
        if datum is not None:
            for o, v in numeric:
                lv = orders.get(o)
                if lv is None:
                    continue
                want = float(v) - datum
                if abs(want - float(lv.get("elevation") or 0.0)) > STOREY_MARK_TOL_M:
                    out.append(_finding("RC9", "major", lv["id"], f"{lv['id']}: {sec_src} marks its storey at "
                                        f"{v:+.2f} (z {want:.2f} m with the datum {datum:+.2f}), the model at "
                                        f"{float(lv.get('elevation') or 0):.2f} m", [sec_src, f"level {lv['id']}"]))
    # The heights conflicts the reading recorded
    for c in building.get("conflicts") or []:
        kind, desc = c.get("kind"), str(c.get("description") or "")
        m = SLAB_BANDS_RE.search(desc)
        if kind in HEIGHT_CONFLICTS or m:
            sev = HEIGHT_CONFLICTS.get(kind, "major")
            if m and abs(int(m.group(1)) - int(m.group(2))) == 0:
                continue
            out.append(_finding("RC9", sev, None, f"{desc} ({c.get('resolution') or 'unresolved'})",
                                [sec_src, "plans"], None, list(c.get("element_ids") or []), conflict=c.get("id")))
    # The ground line
    ground = _ground_z(sheets)
    if ground is not None and levels:
        low = levels[0]
        storey = _value(low.get("floor_to_floor")) or 3.0
        if ground < float(low.get("elevation") or 0.0) - storey:
            out.append(_finding("RC9", "major", low["id"], f"{sec_src}'s ground line at {ground:.2f} m lies more than "
                                f"a storey ({storey:.2f} m) under the lowest floor ({low['id']} at "
                                f"{float(low.get('elevation') or 0):.2f} m)", [sec_src, f"level {low['id']}"]))
        out += _doors_under_ground(building, levels, ground, sec_src)
    return out


def _doors_under_ground(building: dict, levels: list[dict], ground: float, sec_src: str) -> list[dict]:
    """UL308 (real10, 4 Nov 2026: the ground read 0.15 m under L0 instead of -3.00 at the first basement, whose
    terrace doors then opened into the earth): outer doors whose head stands under the section's ground line."""
    out = []
    walls = {w["id"]: w for w in building.get("walls") or []}
    for lv in levels:
        doors = [o for o in building.get("openings") or [] if o.get("level_id") == lv["id"] and o.get("type") == "door"
                 and (walls.get(o.get("wall_id")) or {}).get("exterior")]
        under = [o for o in doors if float(lv.get("elevation") or 0) + float(o.get("sill_height") or 0)
                 + float(o.get("height") or 2.1) < ground - DOOR_UNDER_GROUND_M]
        if under:
            sev = "major" if len(under) >= 2 else "minor"
            out.append(_finding("RC9", sev, lv["id"], f"{lv['id']}: {len(under)} door(s) in its outer walls end "
                                f"under {sec_src}'s ground line at {ground:.2f} m (floor {float(lv.get('elevation') or 0):.2f}"
                                f" m): the ground or the level is misread", [sec_src, f"plan of {lv['id']}"],
                                tuple(under[0]["center"]), [o["id"] for o in under]))
    return out


# --------------------------------------------------------------------------------------------------------------- RC10
def _fold(text: str) -> str:
    from wenart import textfold as TF

    return " ".join(TF.fold_ascii(str(text or "")).upper().split())


def named_buildings(texts: list[str]) -> tuple[int, list[str]]:
    """(how many buildings the site plan's words name, the words): distinct block names (``A BLOK``, ``BLOCK B``) and
    counts (``2 ADET VİLLA``, ``2 VILLAS``); the larger wins."""
    blocks, counts, words = set(), [], []
    for t in texts:
        f = _fold(t)
        for rx in BLOCK_RES:
            for m in rx.finditer(f):
                blocks.add(m.group(1))
                words.append(str(t).strip())
        for rx in COUNT_RES:
            for m in rx.finditer(f):
                counts.append(int(m.group(1)))
                words.append(str(t).strip())
    n = max([len(blocks)] + counts)
    return n, sorted(set(words))


SPACED_LETTERS_RE = re.compile(r"^\s*(?:[^\W\d_]\s+)+[^\W\d_]\s*$")
LABEL_WORDS = ("HAVUZ", "POOL", "PISCINE", "PISCINA", "SCHWIMMBAD")


def interleaved_labels(texts: list[dict]) -> list[str]:
    """Words written letter by letter in two or more overlapping texts (4 Nov 2026, real07's site plan: 'H   V   Z'
    and 'A   U' on top of each other spell HAVUZ, the pool the user asked about, UL323): the letters of texts made of
    single letters a space apart whose boxes overlap, as one word of ``LABEL_WORDS`` when the letters are that word's
    (in any order: the overlap gives no reliable order), else in the order of their estimated x. ``texts``:
    ``{"text", "box"}``."""
    spaced = [t for t in texts if t.get("box") and SPACED_LETTERS_RE.match(str(t.get("text") or ""))]
    groups: list[list[dict]] = []
    for t in spaced:
        b = t["box"]
        hit = next((g for g in groups if any(not (b[2] < o["box"][0] or o["box"][2] < b[0] or b[3] < o["box"][1]
                                                  or o["box"][3] < b[1]) for o in g)), None)
        if hit is None:
            groups.append([t])
        else:
            hit.append(t)
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        letters = []
        for t in g:
            txt, b = str(t["text"]), t["box"]
            n = max(len(txt) - 1, 1)
            letters += [(b[0] + (b[2] - b[0]) * i / n, ch) for i, ch in enumerate(txt) if not ch.isspace()]
        word = "".join(ch for _, ch in sorted(letters))
        key = sorted(_fold(word).replace(" ", ""))
        out.append(next((w for w in LABEL_WORDS if sorted(w) == key), word))
    return out


def footprint(building: dict):
    """The model's footprint: the union of its base levels' outlines."""
    polys = []
    for lv in base_levels(building):
        g = LevelGeometry(building, lv["id"])
        if g.filled is not None:
            polys.append(g.filled)
    return unary_union(polys) if polys else None


def rc10(building: dict, sheets: dict, site_texts: list[str], plan_texts: Optional[list[str]] = None,
         site_region: Optional[str] = None) -> list[dict]:
    """The site plan against the model (the module docstring)."""
    out: list[dict] = []
    site = building.get("site") or {}
    sp = (sheets.get("exterior") or {}).get("site") or {}
    region = site_region or sp.get("region") or "the site plan"
    src = f"site plan {region}"
    copies = site.get("buildings") or []
    model_n = max(len(copies), 1)
    named, words = named_buildings(site_texts)
    if named > model_n:
        out.append(_finding("RC10", "major", None, f"{src} names {named} buildings ({'; '.join(words[:6])}), the model "
                            f"has {model_n}" + ("" if copies else " (no copy of the building found on the site plan)"),
                            [src, "the model"]))
    if sp and not sp.get("registered"):
        out.append(_finding("RC10", "minor", None, f"{src} is not registered onto the building ({sp.get('note') or ''}):"
                            f" its plot and the buildings it draws are not compared with the model", [src, "plans"]))
    plot = (site.get("plot") or {}).get("polygon") if isinstance(site.get("plot"), dict) else site.get("plot")
    fp = footprint(building)
    if plot and len(plot) >= 3 and fp is not None:
        pp = Polygon([tuple(p) for p in plot]).buffer(0)
        shapes = [("the model", fp)] + [(c.get("id") or "copy", Polygon([tuple(p) for p in c["footprint"]]))
                                        for c in copies[1:] if c.get("footprint")]
        for name, shp in shapes:
            if shp.is_empty or shp.within(pp.buffer(PLOT_TOL_M)):
                continue
            outside = shp.difference(pp).area
            c = shp.centroid
            out.append(_finding("RC10", "major", None, f"{name}'s footprint ({shp.area:.1f} m2) does not fit inside "
                                f"the plot drawn on {src} ({pp.area:.1f} m2): {outside:.1f} m2 outside",
                                [src, "plans"], (c.x, c.y)))
    pools = site.get("pools") or []
    labels = [t for t in list(site_texts) + list(plan_texts or []) if POOL_RE.search(_fold(t))]
    if labels and not pools:
        out.append(_finding("RC10", "minor", None, f"a pool label ({'; '.join(sorted(set(map(str, labels)))[:4])}) on "
                            f"the drawings, no pool in the model's site", [src, "the model's site"]))
    return out


# --------------------------------------------------------------------------------------------------------------- RC11
def size_tag_re():
    try:
        from wenart.ingest.generic.core import SIZE_TAG_RE
        return SIZE_TAG_RE
    except ImportError:                                          # pragma: no cover
        return SIZE_TAG_FALLBACK_RE


def _seg_dist(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 <= 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def _opening_span(o: dict, wall: Optional[dict]):
    c = tuple(o["center"])
    u = _unit(wall) if wall else None
    if u is None:
        return c, c
    h = float(o.get("width") or 0.0) / 2.0
    return (c[0] - u[0] * h, c[1] - u[1] * h), (c[0] + u[0] * h, c[1] + u[1] * h)


def rc11(level_id: str, tags: list[dict], walls: list[dict], openings: list[dict]) -> list[dict]:
    """Size tags against the openings read (the module docstring). ``tags``: ``{"text", "x", "y", "w", "h"}``
    (building metres; width and height in metres)."""
    by_id = {w["id"]: w for w in walls}
    spans = [(o, _opening_span(o, by_id.get(o.get("wall_id")))) for o in openings
             if not o.get("virtual") and o.get("center")]
    hits = []
    for t in tags:
        p = (t["x"], t["y"])
        near_wall = min((_seg_dist(p, tuple(w["start"]), tuple(w["end"])) - float(w.get("thickness") or 0) / 2.0
                         for w in walls), default=None)
        if near_wall is None or near_wall > TAG_REACH_M:
            continue
        dists = sorted(((_seg_dist(p, a, b), o) for o, (a, b) in spans), key=lambda x: x[0])
        if any(d <= TAG_REACH_M and abs(float(o.get("width") or 0) - t["w"]) <= TAG_WIDTH_TOL_M for d, o in dists):
            continue
        nearest = next(((d, o) for d, o in dists if d <= TAG_NEAREST_M), None)
        hits.append((t, nearest))
    out = []
    sev = "major" if len(hits) >= TAG_MAJOR_N else "minor"
    for t, nearest in hits:
        if nearest:
            d, o = nearest
            what = (f"the nearest opening is {o['id']} ({o.get('type')}" + (f", {o['type_raw']}" if o.get("type_raw")
                                                                             else "")
                    + f") {float(o.get('width') or 0):.2f} m wide, {d:.2f} m away")
            ids = [o["id"]]
        else:
            what, ids = f"no opening within {TAG_NEAREST_M:.1f} m", []
        out.append(_finding("RC11", sev, level_id, f"{level_id}: size tag '{t['text']}' ({t['w']:.2f} x {t['h']:.2f} m) "
                            f"at ({t['x']:.2f}, {t['y']:.2f}) has no opening {t['w']:.2f} m wide within "
                            f"{TAG_REACH_M:.1f} m; {what}", [f"size tag {t.get('entity') or t['text']}",
                                                             f"openings read on {level_id}"],
                            (t["x"], t["y"]), ids))
    return out


def size_tags(texts: list[dict]) -> list[dict]:
    """The size tags among a level's texts (``{"text", "x", "y", "layer", "entity"}``): ``W/H`` in cm on a door,
    window or glass layer (``wenart.ingest.generic.layer_names``), sizes in ``TAG_SIZE_CM``."""
    from wenart.ingest.generic import layer_names as LN

    rx = size_tag_re()
    out = []
    for t in texts:
        m = rx.match(str(t.get("text") or ""))
        if not m or LN.layer_role(t.get("layer")) not in TAG_LAYER_ROLES:
            continue
        w, h = int(m.group(1)), int(m.group(2))
        if not (TAG_SIZE_CM[0][0] <= w <= TAG_SIZE_CM[0][1] and TAG_SIZE_CM[1][0] <= h <= TAG_SIZE_CM[1][1]):
            continue
        out.append(dict(t, w=w / 100.0, h=h / 100.0))
    return out


# --------------------------------------------------------------------------------------------------------------- RC12
def _counts(building: dict, lid: str) -> dict:
    ops = [o for o in building.get("openings") or [] if o.get("level_id") == lid]
    return {"rooms": sum(1 for r in building.get("rooms") or [] if r.get("level_id") == lid),
            "walls": sum(1 for w in building.get("walls") or [] if w.get("level_id") == lid),
            "doors": sum(1 for o in ops if o.get("type") == "door"),
            "windows": sum(1 for o in ops if o.get("type") == "window")}


def room_openings(room: dict, walls: dict, openings: list[dict]) -> dict:
    """``{"door": [...], "window": [...]}`` of a room: openings whose wall touches the room polygon and whose centre
    lies within the wall's half thickness (and ``ROOM_OPENING_REACH_M``) of it."""
    poly = Polygon([tuple(p) for p in room.get("polygon") or []]).buffer(0)
    out = {"door": [], "window": []}
    if poly.is_empty:
        return out
    for o in openings:
        if o.get("level_id") != room.get("level_id") or o.get("type") not in out or not o.get("center"):
            continue
        w = walls.get(o.get("wall_id"))
        if w is None:
            continue
        reach = float(w.get("thickness") or 0.1) / 2.0 + ROOM_OPENING_REACH_M
        if poly.distance(Point(tuple(o["center"]))) <= reach \
                and poly.distance(LineString([tuple(w["start"]), tuple(w["end"])])) <= reach:
            out[o["type"]].append(o["id"])
    return out


def rc12(building: dict) -> list[dict]:
    """Typical floors against their copies, mirrored halves against their twins (the module docstring)."""
    out: list[dict] = []
    levels = {lv["id"]: lv for lv in building.get("levels") or []}
    copies = [lv for lv in levels.values() if lv.get("typical_of") and lv.get("typical_of") != lv["id"]]
    for lv in copies:
        base = lv["typical_of"]
        if base not in levels:
            continue
        a, b = _counts(building, base), _counts(building, lv["id"])
        if not b["rooms"] and not b["walls"]:
            out.append(_finding("RC12", "info", lv["id"], f"{lv['id']} is a copy of the typical floor {base} not "
                                f"materialised in building.json: not compared", [f"plan of {base}", lv["id"]]))
            continue
        diff = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
        if diff:
            sev = "major" if set(diff) - {"walls"} else "minor"
            out.append(_finding("RC12", sev, lv["id"], f"{lv['id']} (a copy of the typical floor {base}) differs from "
                                f"it: " + ", ".join(f"{k} {x} on {base} / {y} on {lv['id']}" for k, (x, y) in diff.items()),
                                [f"typical floor {base}", f"copy {lv['id']}"]))
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    walls = {w["id"]: w for w in building.get("walls") or []}
    openings = [o for o in building.get("openings") or [] if not o.get("virtual")]
    done = set()
    for r in rooms.values():
        t = rooms.get(r.get("twin_of") or "")
        if t is None or (t["id"], r["id"]) in done:
            continue
        done.add((r["id"], t["id"]))
        src = [f"room {r['id']} ({r.get('label')})", f"its mirrored twin {t['id']} ({t.get('label')})"]
        c = Polygon([tuple(p) for p in r.get("polygon") or [(0, 0)] * 3]).centroid
        place = (c.x, c.y) if not c.is_empty else None
        ro, to = room_openings(r, walls, openings), room_openings(t, walls, openings)
        diffs = [f"{len(ro[k])} {k}s / {len(to[k])}" for k in ("door", "window") if len(ro[k]) != len(to[k])]
        if diffs:
            out.append(_finding("RC12", "major", r.get("level_id"), f"{r['id']} and its mirrored twin {t['id']} differ "
                                f"in openings: " + ", ".join(diffs) + f" (window ids {ro['window']} / {to['window']})",
                                src, place, [r["id"], t["id"]] + ro["window"] + to["window"]))
        ar, at = float(r.get("area_computed") or 0), float(t.get("area_computed") or 0)
        if max(ar, at) > 0 and abs(ar - at) > TWIN_AREA_SHARE * max(ar, at):
            out.append(_finding("RC12", "minor", r.get("level_id"), f"{r['id']} ({ar:.2f} m2) and its mirrored twin "
                                f"{t['id']} ({at:.2f} m2) differ in area by {abs(ar - at) / max(ar, at) * 100:.0f} %",
                                src, place, [r["id"], t["id"]]))
        res = _value(r.get("twin_residual_m"))
        if res is not None and res > TWIN_RESIDUAL_M:
            out.append(_finding("RC12", "minor", r.get("level_id"), f"{r['id']} mirrors {t['id']} only to "
                                f"{res:.2f} m (over {TWIN_RESIDUAL_M:.2f} m)", src, place, [r["id"], t["id"]]))
    return out


# ------------------------------------------------------------------------------------------------------------ reading
def _texts_of(page, tf=None) -> list[dict]:
    from wenart.reading_check import _apply

    out = []
    for t in getattr(page, "texts", None) or []:
        c = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        x, y = _apply(tf, c) if tf else c
        ev = t.evidence[0] if isinstance(t.evidence, list) and t.evidence else t.evidence
        layer = ev.get("layer") if isinstance(ev, dict) else None
        out.append({"text": t.text, "x": x, "y": y, "layer": layer, "entity": t.id})
    return out


def _section_regions(out_dir: Path, sheets: dict) -> list:
    """The section regions as objects ``wenart.sheets.levels.storey_words`` / ``storey_elevations`` read (texts
    with ``text``, ``point``, ``height``, ``box``, ``id``)."""
    from wenart.reading_check import read_level_page

    out = []
    for r in sheets.get("regions") or []:
        if r.get("class") != "section":
            continue
        page = read_level_page(out_dir, sheets, {"region": r["id"], "file": r.get("file")})
        if page is None:
            continue
        texts = [SimpleNamespace(text=t.text, point=((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0),
                                 height=t.height, box=t.box, id=t.id, rotation_deg=t.rotation_deg)
                 for t in page.texts]
        out.append(SimpleNamespace(id=r["id"], texts=texts, use=r.get("use"), cls="section"))
    return out


def findings(out_dir) -> list[dict]:
    """Every cross-document finding of a pipeline output (the module docstring)."""
    from wenart.reading_check import level_pages, read_level_page
    from wenart.sheets import levels as LV

    out_dir = Path(out_dir)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sp = out_dir / "sheets.json"
    sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    res = rc8(building, sheets)
    secs = _section_regions(out_dir, sheets) if sheets else []
    storeys = LV.storey_words([s for s in secs if s.use == "heights"] or secs) if secs else {}
    try:
        storey_el = LV.storey_elevations(secs) if secs else {}
    except Exception as exc:                                     # noqa: BLE001 (a reader error is a note, not a stop)
        storey_el = {}
        res.append(_finding("RC9", "info", None, f"the sections' storey marks could not be read: {exc}", ["sections"]))
    res += rc9(building, sheets, storeys, storey_el)
    plan_texts: list[str] = []
    for lid, pg in level_pages(building).items():
        page = read_level_page(out_dir, sheets, pg)
        if page is None:
            continue
        texts = _texts_of(page, pg["tf"])
        plan_texts += [t["text"] for t in texts]
        plan_texts += interleaved_labels([{"text": t.text, "box": t.box} for t in page.texts])
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
        ops = [o for o in building.get("openings") or [] if o.get("level_id") == lid]
        res += rc11(lid, size_tags(texts), walls, ops)
    site_texts: list[str] = []
    site_region = None
    for r in sheets.get("regions") or []:
        if r.get("class") != "site_plan":
            continue
        site_region = site_region or r["id"]
        page = read_level_page(out_dir, sheets, {"region": r["id"], "file": r.get("file")})
        if page is not None:
            site_texts += [t.text for t in page.texts]
            site_texts += interleaved_labels([{"text": t.text, "box": t.box} for t in page.texts])
    if site_region is not None or (building.get("site") or {}).get("buildings"):
        res += rc10(building, sheets, site_texts, plan_texts, site_region)
    else:
        res += [f for f in rc10(building, sheets, [], plan_texts) if "pool" in f["message"]]
    res += rc12(building)
    return res


def _main(argv: Optional[list] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check.crossdoc", description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="a pipeline output folder (building.json, sheets.json, converted/)")
    ap.add_argument("--json", help="write the findings to this JSON file")
    args = ap.parse_args(argv)
    res = findings(args.out)
    for f in res:
        print(f"{f['check']:5s} {f['severity']:8s} {str(f.get('level_id') or '-'):6s} {f['message']}")
    counts = {s: sum(1 for f in res if f["severity"] == s) for s in ("critical", "major", "minor", "info")}
    print(f"{len(res)} findings: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
