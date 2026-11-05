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
ALIGN_SEARCH_M = 4.0           # the facade's left end may be off by this much (a balcony, the eaves, a level mark)
ALIGN_STEP_M = 0.05            # the shifts tried, this far apart
ALIGN_FAR_SHARE = 0.5          # a shift beyond ALIGN_SEARCH_M matches at least this share of the openings
ALIGN_MIN_SHARE = 0.3          # aligned when this share of the smaller side's openings match (at least ALIGN_MIN_N)
ALIGN_MIN_N = 2
SIDE_ANGLE_DEG = 45.0          # a wall faces a side when its outward normal is within this (to_building.SIDE_ANGLE_DEG)
SLIT_CLOSE_M = 0.03            # the wall union's slits closed (topology.SLIT_CLOSE_M)
BAND_TOL_M = 0.3               # an opening's mid height this far below a level's floor still belongs to it
STACK_MATCH_M = 0.3            # the plans' facade: an outer opening on one floor and on another this close are one
NORTH_CANDIDATES_DEG = (0.0, 90.0, 180.0, 270.0)
NORTH_MARGIN_MIN = 0.20        # a north placed by fit with a smaller margin over the next axis is weak ...
NORTH_MARGIN_MIN_N = 5         # ... or fewer openings ahead of it than this
WIDTH_TOL_M = 0.5              # an elevation opening and a plan opening are alike in width within this ...
WIDTH_TOL_SHARE = 0.4          # ... or this share of the wider one, unless one lies inside the other's span
CONTAIN_TOL_M = 0.1            # ... within this
SMALL_FRAME_M = 0.5            # a frame smaller than this both ways is no window (a vent, a panel)
STRIP_X_M = 0.1                # frames one above the other within this along the facade ...
STRIP_GAP_M = 0.3              # ... with less wall than this between them are cells of one glazed strip ...
STRIP_MIN_CELLS = 3            # ... when at least this many are stacked (a door with its fanlight is no strip)
EXTENT_TOL_M = 0.5             # a column further than this beyond the facing walls' extent is outside the facade
WALL_NEAR_PLACE_M = 0.5        # the plan's wall pieces this close to a missing opening's place are named with it
WHOLE_FLOOR_MIN = 2            # a floor with at least this many frames and no plan opening on that side is major
COURT_RAY_M = 6.0              # an exterior wall's outward ray meeting another wall within this looks into a court
COURT_WALL_MIN_H_M = 1.5       # ... a wall at least this high (a balcony parapet does not hide the facade)
LOCAL_SIDES = {"right": 0.0, "back": 90.0, "left": 180.0, "front": 270.0}
# RC9
STOREY_M = (2.0, 8.0)          # a storey's floor-to-floor height outside this is no storey (UL 4 Nov 2026, real07)
LEVEL_TOL_M = 0.05             # the section's floor mark and the model's level differ by more than this
STOREY_MARK_TOL_M = 0.10       # the storeys' floor marks the section names against the model's levels
DOOR_UNDER_GROUND_M = 0.3      # an outer door whose head is this far under the section's ground opens into the earth
SLAB_BANDS_RE = re.compile(r"draws (\d+) slab bands?, the plans (\d+) levels?")
HEIGHT_CONFLICTS = {"section_width_mismatch": "minor", "level_mark_mismatch": "major"}
# RC10
# 5 Nov 2026 (review): whole words only (BLOC must not leave a K to be read as block "K"), the genitive BLOĞU / BLOKU;
# a count of dwellings (konut, mesken, dubleks, ev, daire) is no count of buildings (a zoning note): an info finding
BLOCK_WORD = r"(?:BLOCK|BLOGU|BLOKU|BLOK|BLOC)(?![A-Z])"
# 5 Nov 2026 (round 3): 'A-B BLOK' names A and B; after the word a name only when the text ends or a comma, a dash,
# a slash follows ('BLOK 19 CM', 'BLOK H=2.40' name no block)
BLOCK_NAME = r"(?:[A-Z]|\d{1,2})"
BLOCK_RES = [re.compile(r"(?<![A-Z0-9.,])(" + BLOCK_NAME + r"(?:\s*[-/,&]\s*" + BLOCK_NAME + r")*)\s*[-.]?\s*"
                        + BLOCK_WORD),
             re.compile(r"(?<![A-Z0-9])(?:BLOCK|BLOK|BLOC)(?![A-Z])\s*[-.]?\s*(" + BLOCK_NAME
                        + r")(?=\s*(?:$|[,/\-\n]))")]
COUNT_RES = [re.compile(r"(?<![\d.,])(\d{1,2})\s*ADET\s+(?:VILLA|BINA|BLOK|IKIZ)(?![A-Z])"),
             re.compile(r"(?<![\d.,])(\d{1,2})\s+(?:VILLAS|BUILDINGS|BLOCKS)(?![A-Z])")]
DWELLING_RES = [re.compile(r"(?<![\d.,])(\d{1,3})\s*ADET\s+(?:KONUT|MESKEN|DUBLEKS|EV|DAIRE)(?![A-Z])"),
                re.compile(r"(?<![\d.,])(\d{1,3})\s+(?:DWELLINGS|FLATS|APARTMENTS|HOUSES)(?![A-Z])")]
SPACED_LETTERS_RE = re.compile(r"^\s*(?:[^\W\d_]\s+)+[^\W\d_]\s*$")
LABEL_WORDS = ("HAVUZ", "POOL", "PISCINE", "PISCINA", "SCHWIMMBAD")
POOL_RE = re.compile(r"(?<![A-Z])(?:HAVUZ|HAVUZU|POOL|SWIMMING|PISCINE|PISCINA|SCHWIMMBAD|POOLS)(?![A-Z])")
PLOT_TOL_M = 0.10
# RC11: SIZE_TAG_RE is ``wenart.ingest.generic.core.SIZE_TAG_RE`` (imported in ``size_tags``; copied here only if the
# import fails): width/height in cm, "90/210", "90 / 210"
SIZE_TAG_FALLBACK_RE = re.compile(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")
TAG_REACH_M = 0.8              # a tag stands this close to a wall of its level, its opening this close to it
TAG_WIDTH_TOL_M = 0.10
TAG_SIZE_CM = ((40, 600), (40, 400))
TAG_LAYER_ROLES = ("door", "window", "glass", "text")   # real10 writes its tags on TEXT; DOĞRAMA is a window word
TAG_WALL_FACE_M = 0.3          # a tag on a layer of no known role counts only this close to a wall face
TAG_NEAREST_M = 1.5            # the nearest opening named in the message
TAG_MAJOR_WIDTH_M = 0.5        # a tag whose nearest opening differs by more than this in width is major
# RC12
TWIN_AREA_SHARE = 0.05
TWIN_RESIDUAL_M = 0.10
ROOM_OPENING_REACH_M = 0.10    # an opening belongs to a room whose polygon is this close beyond its wall's half thickness


def _finding(check: str, severity: str, level: Optional[str], message: str, sources: list,
             place: Optional[tuple] = None, element_ids: Optional[list] = None, **extra) -> dict:
    out = {"check": check, "name": CHECKS[check], "severity": severity, "level_id": level, "message": message,
           "sources": [s for s in sources if s], "place": None, "element_ids": []}
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
        self.hidden = self._hidden()

    def _hidden(self) -> set:
        """5 Nov 2026 (round 3): exterior walls whose outward ray meets another wall of the level (at least
        ``COURT_WALL_MIN_H_M`` high) within ``COURT_RAY_M``: they look into a court or a shaft, not out of the facade."""
        from shapely.strtree import STRtree

        tall = [w for w in self.walls if float(w.get("height") or 3.0) >= COURT_WALL_MIN_H_M]
        polys = [wall_polygon(w) for w in tall]
        keep = [(w, pg) for w, pg in zip(tall, polys) if pg is not None]
        if not keep:
            return set()
        tree = STRtree([pg for _, pg in keep])
        out = set()
        for w in self.walls:
            n = self.normals.get(w["id"])
            if n is None:
                continue
            (x0, y0), (x1, y1) = w["start"], w["end"]
            mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            r = math.radians(n)
            start = float(w.get("thickness") or 0.1) / 2.0 + 0.05
            ray = LineString([(mx + math.cos(r) * start, my + math.sin(r) * start),
                              (mx + math.cos(r) * COURT_RAY_M, my + math.sin(r) * COURT_RAY_M)])
            for k in tree.query(ray):
                other, pg = keep[int(k)]
                if other["id"] != w["id"] and pg.intersects(ray):
                    out.add(w["id"])
                    break
        return out

    def facing(self, normal: float, hidden: bool = False) -> list[dict]:
        """The openings on the exterior walls facing ``normal`` (``hidden``: the ones on walls looking into a court
        or a shaft instead, which the elevation does not show)."""
        ids = {wid for wid, n in self.normals.items() if n is not None and angle_gap(n, normal) <= SIDE_ANGLE_DEG
               and (wid in self.hidden) == hidden}
        return [o for o in self.openings if o.get("wall_id") in ids and o.get("center")]

    def facing_walls(self, normal: float) -> list[dict]:
        return sorted((self.by_id[wid] for wid, n in self.normals.items() if n is not None
                       and angle_gap(n, normal) <= SIDE_ANGLE_DEG and wid not in self.hidden), key=lambda w: w["id"])


def _axis(normal: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """(along, out): the facade's left-to-right direction seen from outside, and its outward normal."""
    r = math.radians(normal + 90.0)
    n = math.radians(normal)
    return (math.cos(r), math.sin(r)), (math.cos(n), math.sin(n))


def _dot(p, u) -> float:
    return p[0] * u[0] + p[1] * u[1]


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


def z_shift(positions: list, bands: dict) -> float:
    """0.0 when most of an elevation's openings stand at a level's height; else the common vertical shift (from the
    floors less the sills, in ``ALIGN_STEP_M`` steps) that puts the most of them at one (4 Nov 2026, real07: its
    elevation heights came from a section whose marks are no storeys, sills at 7 and 10 m on a two-storey house)."""
    def placed(d: float) -> int:
        return sum(1 for p in positions if level_of_z(bands, float(p["sill"]) + d, float(p["head"]) + d))

    if not positions or placed(0.0) * 2 >= len(positions):
        return 0.0
    cands = {round(round((lo - float(p["sill"]) + k) / ALIGN_STEP_M) * ALIGN_STEP_M, 3)
             for p in positions for lo, _ in bands.values() for k in (0.0, 0.9)}
    best = max(sorted(cands, key=abs), key=placed, default=0.0)
    return best if placed(best) > placed(0.0) else 0.0


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
    # 5 Nov 2026 (review): the elevations of one set share one datum: one vertical shift for the project (the one
    # placing the most openings over all elevations); each elevation reports only its residual
    every = [p for _, _, ps in els for p in ps]
    ctx["dz"] = z_shift(every, ctx["bands"])
    if ctx["dz"]:
        out.append(_finding("RC8", "minor", None, f"the elevations' openings stand at no level's height as read (sills "
                            + _fmt_x([float(p['sill']) for p in every]) + f" m); shifted {ctx['dz']:+.2f} m they fit "
                            f"the levels (inferred): the elevations' heights and the section's disagree",
                            ["elevations", "section / levels"], z_shift_m=ctx["dz"]))
    inferred, weak, margin = None, False, 1.0
    if north is None and any(EX.normal_deg(el.get("side"), None) is None for el, _, _ in els):
        scores = {}
        for cand in NORTH_CANDIDATES_DEG:
            parts = [_compare_elevation(el, EX.normal_deg(el.get("side"), cand), name, positions, ctx)[1]
                     for el, name, positions in els if EX.normal_deg(el.get("side"), cand) is not None]
            scores[cand] = (sum(p_[0] for p_ in parts), sum(p_[1] for p_ in parts), round(sum(p_[2] for p_ in parts), 3))
        ranked = sorted(NORTH_CANDIDATES_DEG, key=lambda c: (-scores[c][0], c))
        best, nxt = ranked[0], ranked[1]
        how = ""
        if scores[best][0] == scores[nxt][0] and scores[best][0] > 0:
            # 5 Nov 2026 (round 3, real07: 9 against 9): the pairs inside wider plan openings, then the drawn width
            tied = [c for c in ranked if scores[c][0] == scores[best][0]]
            for k, label in ((1, "the openings inside wider plan openings"), (2, "the drawn facade widths")):
                tied.sort(key=lambda c: (-scores[c][k], c))
                if scores[tied[0]][k] != scores[tied[1]][k]:
                    best, nxt, how = tied[0], tied[1], f"; tie broken by {label}"
                    break
            else:
                best = None
                out.append(_finding("RC8", "info", None, f"no north arrow read and two axes fit alike ("
                                    + " and ".join(f"{c:.0f}" for c in tied[:2]) + " degrees from the building's +Y, "
                                    f"{scores[tied[0]][0]} openings each): not compared", ["elevations", "plans"]))
        second = scores[nxt][0] if best is not None else 0
        if best is not None and scores[best][0] > 0 and (second < scores[best][0] or how):
            north = inferred = best
            top = scores[best][0]
            margin = (top - second) / top
            # weak: a small share over the next axis, or a few openings only (12 against 8 on real07's four
            # elevations is no evidence for a compass); a tie broken by a second score is weak too
            weak = margin < NORTH_MARGIN_MIN or top - second < NORTH_MARGIN_MIN_N or bool(how)
            others = ", ".join(f"{c:.0f}: {v[0]}" for c, v in scores.items() if c != best)
            out.append(_finding("RC8", "info", None, f"no north arrow read: the compass sides placed by fit, north = "
                                f"{best:.0f} deg from the building's +Y ({top} elevation openings match plan "
                                f"openings against {second} on the next axis: margin {margin * 100:.0f} %{how}; the "
                                f"other axes {others}) (inferred)" + (f"; a weak fit (under {NORTH_MARGIN_MIN * 100:.0f} %, "
                                                                      f"fewer than {NORTH_MARGIN_MIN_N} openings ahead "
                                                                      f"or a tie): the findings below are minor at most"
                                                                      if weak else ""),
                                ["elevations", "plans"], north_inferred_deg=best, north_margin=round(margin, 3)))
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
                if weak and f["severity"] in ("critical", "major"):
                    f["severity"] = "minor"
                    f["message"] += (f" (minor at most: the north was placed by a weak fit, margin "
                                     f"{margin * 100:.0f} %, {scores[inferred][0] - second} openings)")
        out += found
    if no_north:
        out.append(_finding("RC8", "info", None, "not compared with the plans: " + "; ".join(no_north)
                            + " (a compass side needs the north arrow; none was read and no axis fits)",
                            ["elevations", "site plan"]))
    if empty:
        out.append(_finding("RC8", "info", None, "no window or door read on " + "; ".join(empty)
                            + ": nothing to compare", ["elevations"]))
    return out + rc8_stacked(building)


def _wide_alike(we: float, wp: float) -> bool:
    """Two openings' widths agree (``WIDTH_TOL_M`` or ``WIDTH_TOL_SHARE`` of the wider): alignment and matching only
    pair openings of about one size (real10's east side was aligned on the wrong windows by position alone)."""
    return abs(we - wp) <= max(WIDTH_TOL_M, WIDTH_TOL_SHARE * max(we, wp))


def _greedy(es: list, ps: list, shift: float, tol: float, contain: bool = True) -> list[tuple[int, int]]:
    """Pairs (i, j) of elevation items ``(x, width)`` and plan items ``(x, width)``: nearest first, within ``tol``
    along the facade after ``shift`` with widths alike, or one inside the other's span whatever the widths (an
    elevation frame inside a wider plan gap or window); further frames inside a matched plan opening pair with it.
    ``contain=False``: widths alike only (the alignment and the north fit)."""
    def contains(e, p) -> bool:
        if not contain:
            return False
        lo_e, hi_e = e[0] - e[1] / 2.0, e[0] + e[1] / 2.0
        lo_p, hi_p = p[0] + shift - p[1] / 2.0, p[0] + shift + p[1] / 2.0
        return (lo_p - CONTAIN_TOL_M <= lo_e and hi_e <= hi_p + CONTAIN_TOL_M) or \
            (lo_e - CONTAIN_TOL_M <= lo_p and hi_p <= hi_e + CONTAIN_TOL_M)

    pairs = sorted(((abs(e[0] - (p[0] + shift)), i, j) for i, e in enumerate(es) for j, p in enumerate(ps)
                    if (abs(e[0] - (p[0] + shift)) <= tol and _wide_alike(e[1], p[1])) or contains(e, p)))
    used_i, used_j, out = set(), set(), []
    for _, i, j in pairs:
        if i not in used_i and j not in used_j:
            used_i.add(i)
            used_j.add(j)
            out.append((i, j))
    # 5 Nov 2026 (review): more frames inside one wide plan opening (two leaves of a 2.44 m gap) are all that opening's
    for i, e in enumerate(es):
        if i in used_i:
            continue
        j = next((j for j in used_j if contains(e, ps[j])), None)
        if j is not None:
            used_i.add(i)
            out.append((i, j))
    return out


def _columns(items: list, tol: float) -> list[list]:
    """Items ``(x, ...)`` grouped into columns: sorted by x, a new column where an item lies more than ``tol`` from
    the column's mean (never chained by neighbours 0.45 m apart)."""
    cols: list[list] = []
    for it in sorted(items, key=lambda t: t[0]):
        if cols and it[0] - sum(c[0] for c in cols[-1]) / len(cols[-1]) <= tol:
            cols[-1].append(it)
        else:
            cols.append([it])
    return cols


def drop_strips(positions: list) -> tuple[list, list]:
    """(kept, dropped): an elevation's openings minus the frames smaller than ``SMALL_FRAME_M`` both ways and the cells
    of tall glazed strips (a stair shaft's glazing: frames one above the other at one x with less than
    ``STRIP_GAP_M`` of wall between them, at least ``STRIP_MIN_CELLS``: real10's south side); neither is a window a
    plan draws as such."""
    dropped = []
    kept = []
    for p in positions:
        if float(p.get("width") or 0) < SMALL_FRAME_M and float(p["head"]) - float(p["sill"]) < SMALL_FRAME_M:
            dropped.append((p, "smaller than %.1f m both ways" % SMALL_FRAME_M))
        else:
            kept.append(p)
    strip = set()
    for col in _columns([(float(p["x"]), k, p) for k, p in enumerate(kept)], STRIP_X_M):
        stack = sorted(col, key=lambda t: float(t[2]["sill"]))
        chain = [stack[0]] if stack else []
        for a, b in zip(stack, stack[1:]):
            if float(b[2]["sill"]) - float(a[2]["head"]) < STRIP_GAP_M:
                chain.append(b)
                continue
            if len(chain) >= STRIP_MIN_CELLS:
                strip.update(c[1] for c in chain)
            chain = [b]
        if len(chain) >= STRIP_MIN_CELLS:
            strip.update(c[1] for c in chain)
    dropped += [(p, "a cell of a tall glazed strip (no wall between it and the next frame)")
                for k, p in enumerate(kept) if k in strip]
    return [p for k, p in enumerate(kept) if k not in strip], dropped


def _compare_elevation(el: dict, normal: float, name: str, positions: list, ctx: dict) -> tuple[list, int]:
    """(findings, openings matched) of one elevation seen along ``normal`` against the plans (``rc8``): one finding
    per column of openings (within ``MATCH_M`` along the facade across the floors) the elevation and the plans do not
    share, and one per floor with openings on the elevation and none on the plan for that side."""
    out: list[dict] = []
    levels, bands, region_of, ground, geo = (ctx["levels"], ctx["bands"], ctx["region_of"], ctx["ground"], ctx["geo"])
    rid, side, title = el.get("region_id") or el.get("region"), el.get("side"), el.get("title") or ""
    src_el = f"elevation {rid}" + (f" ({title.strip()})" if title else "")
    along, outv = _axis(normal)
    left = min((_dot(p, along) for g in geo.values() if g.filled is not None
                for p in g.filled.exterior.coords), default=0.0)
    front = max((_dot(p, outv) for g in geo.values() if g.filled is not None
                 for p in g.filled.exterior.coords), default=0.0)
    positions, dropped = drop_strips(positions)
    strips = [(float(p["x"]) - float(p.get("width") or 0) / 2.0, float(p["x"]) + float(p.get("width") or 0) / 2.0)
              for p, why in dropped if "strip" in why]
    if dropped:
        why: dict = {}
        for _, reason in dropped:
            why[reason] = why.get(reason, 0) + 1
        out.append(_finding("RC8", "info", None, f"{name}: {len(dropped)} frame(s) left out of the comparison ("
                            + "; ".join(f"{n} {r}" for r, n in why.items()) + "; at x "
                            + _fmt_x(sorted({round(float(p['x']), 2) for p, _ in dropped})) + " m)", [src_el],
                            None, sorted({str(p.get("entity")) for p, _ in dropped if p.get("entity")}),
                            region=rid, dropped=len(dropped)))
    dz0 = ctx.get("dz", 0.0)
    residual = z_shift([dict(p, sill=float(p["sill"]) + dz0, head=float(p["head"]) + dz0) for p in positions], bands)
    dz = dz0 + residual
    seen_by: dict = {}
    unplaced = []
    for p in positions:
        lid = level_of_z(bands, float(p["sill"]) + dz, float(p["head"]) + dz)
        (seen_by.setdefault(lid, []) if lid else unplaced).append(p)
    if residual:
        out.append(_finding("RC8", "minor", None, f"{name}: its heights are {residual:+.2f} m off the other "
                            f"elevations' (shifted by the project's {dz0:+.2f} m and {residual:+.2f} m more they fit the "
                            f"levels, inferred)", [src_el, "the other elevations"], region=rid, z_shift_m=residual))
    plan_by: dict = {}
    court = sorted(o["id"] for g in geo.values() for o in g.facing(normal, hidden=True))
    if court:
        out.append(_finding("RC8", "info", None, f"{name}: {len(court)} plan opening(s) on walls looking into a court or "
                            f"a shaft (another wall within {COURT_RAY_M:.0f} m in front) are not required on the "
                            f"elevation (they still match a frame drawn there): "
                            + ", ".join(court[:8]) + (" ..." if len(court) > 8 else ""), [src_el, "plans"], None,
                            court, region=rid, side=side))
    # openings in a court or a shaft: never 'not drawn on the elevation', but a frame drawn at one is theirs
    court_by = {lid: [(_dot(o["center"], along) - left, float(o.get("width") or 0.0), o)
                      for o in g.facing(normal, hidden=True)] for lid, g in geo.items()}
    for lid, g in geo.items():
        ops = []
        for o in g.facing(normal):
            head = bands[lid][0] + float(o.get("sill_height") or 0.0) + float(o.get("height") or 0.0)
            if ground is not None and head <= ground + 0.05:
                continue                     # under the ground line: an elevation does not draw it
            ops.append((_dot(o["center"], along) - left, float(o.get("width") or 0.0), o))
        plan_by[lid] = ops
    es_by = {lid: [(float(p["x"]), float(p.get("width") or 0.0), p) for p in ps] for lid, ps in seen_by.items()}
    es_all = [(lid, e) for lid, es in es_by.items() for e in es]
    cand = {0.0}
    for lid, e in es_all:
        for p in plan_by.get(lid, []):
            if _wide_alike(e[1], p[1]):
                cand.add(round(round((e[0] - p[0]) / ALIGN_STEP_M) * ALIGN_STEP_M, 3))

    def score(shift: float) -> int:
        # strict pairs (widths alike) for the alignment and the north fit: a wide plan gap holding any frame would
        # make every axis fit about as well
        return sum(len(_greedy(es_by.get(lid, []), plan_by.get(lid, []), shift, MATCH_M, contain=False))
                   for lid in es_by)

    # The left end as drawn is trusted within ALIGN_SEARCH_M; a shift beyond it (the drawn left end was a sheet
    # frame, a site wall or a tree: real07) must match clearly more and at least ALIGN_FAR_SHARE of the openings.
    n_plan = sum(len(plan_by.get(lid, [])) for lid in es_by)
    smaller = min(len(es_all), n_plan or 1)
    near = [c for c in cand if abs(c) <= ALIGN_SEARCH_M]
    best = max(sorted(near, key=abs), key=score)
    far = [c for c in cand if abs(c) > ALIGN_SEARCH_M]
    if far:
        best_far = max(sorted(far, key=abs), key=score)
        if score(best_far) >= max(score(best) + ALIGN_MIN_N, ALIGN_FAR_SHARE * smaller):
            best = best_far
    matched = score(best)
    with_inside = sum(len(_greedy(es_by.get(lid, []), plan_by.get(lid, []), best, MATCH_M)) for lid in es_by)
    # the drawn width of the openings against the plan's (a tie-break of the north fit)
    e_span = [v for e in (e for es in es_by.values() for e in es) for v in (e[0] - e[1] / 2.0, e[0] + e[1] / 2.0)]
    p_span = [v for p_ in (p_ for ps in plan_by.values() for p_ in ps) for v in (p_[0] - p_[1] / 2.0, p_[0] + p_[1] / 2.0)]
    span_gap = abs((max(e_span) - min(e_span)) - (max(p_span) - min(p_span))) if e_span and p_span else 99.0
    aligned = with_inside >= max(ALIGN_MIN_N, ALIGN_MIN_SHARE * smaller)
    order = {lv["id"]: k for k, lv in enumerate(levels)}

    def floors(lids) -> str:
        return ", ".join(sorted(set(lids), key=lambda x: order.get(x, 99)))

    # A whole floor: openings on the elevation, none on the plan for that side (2 frames at least; its frames are not
    # reported again as a column)
    whole = set()
    for lid, es in es_by.items():
        if len(es) >= WHOLE_FLOOR_MIN and not plan_by.get(lid):
            whole.add(lid)
            out.append(_finding("RC8", "major", lid, f"{name} shows {len(es)} opening(s) on {lid} (x "
                                f"{_fmt_x([e[0] for e in es])} m); the plan of {lid} has none on its walls facing "
                                f"{side}", [src_el, f"plan of {lid}" + (f" ({region_of.get(lid)})" if region_of.get(lid)
                                                                         else "")], region=rid, side=side))
    if not aligned:
        diffs = [(lid, len(es_by.get(lid, [])), len(plan_by.get(lid, []))) for lid in order
                 if plan_by.get(lid) and len(es_by.get(lid, [])) != len(plan_by.get(lid, []))]
        if diffs:
            out.append(_finding("RC8", "minor", None, f"{name}: positions not aligned with the plans (only {matched} "
                                f"opening(s) match), counts compared: " + "; ".join(
                                    f"{lid} elevation {a} / plan {b}" for lid, a, b in diffs),
                                [src_el, "plans"], region=rid, side=side))
    else:
        e_only, p_only, shown = [], [], []
        for lid in sorted(es_by.keys() | plan_by.keys(), key=lambda v: (order.get(v, 99), v)):
            es, ps = es_by.get(lid, []), plan_by.get(lid, [])
            pairs = _greedy(es, ps, best, MATCH_M)
            ei, pj = {i for i, _ in pairs}, {j for _, j in pairs}
            shown += [(e[0], lid) for e in es]
            if lid not in whole:
                rest = [e for i, e in enumerate(es) if i not in ei]
                in_court = {i for i, _ in _greedy(rest, court_by.get(lid, []), best, MATCH_M)}
                e_only += [(e[0], lid, e) for i, e in enumerate(rest) if i not in in_court]
            # a plan opening behind a glazed strip left out of the comparison is that strip's
            p_only += [(p_[0] + best, lid, p_) for j, p_ in enumerate(ps) if j not in pj and es
                       and not any(a - CONTAIN_TOL_M <= p_[0] + best <= b + CONTAIN_TOL_M for a, b in strips)]
        # the facade's extent: the facing walls' span along it (elevation x), all levels
        ext = [_dot(pt, along) - left + best for g in geo.values() for wid, n in g.normals.items()
               if n is not None and angle_gap(n, normal) <= SIDE_ANGLE_DEG for pt in (g.by_id[wid]["start"],
                                                                                      g.by_id[wid]["end"])]
        outside = []
        for col in _columns(e_only, MATCH_M):
            col = sorted(col, key=lambda c: (order.get(c[1], 99), c[0]))
            xs = [c[0] for c in col]
            x = sum(xs) / len(xs)
            if ext and not (min(ext) - EXTENT_TOL_M <= x <= max(ext) + EXTENT_TOL_M):
                outside.append(x)
                continue
            missing = sorted({c[1] for c in col}, key=lambda v: (order.get(v, 99), v))
            on_el = sorted({lid for sx, lid in shown if abs(sx - x) <= MATCH_M}, key=lambda v: (order.get(v, 99), v))
            sev = "major" if len(missing) >= 2 and len(on_el) >= 3 else "minor"
            t = x - best + left
            w = sum(c[2][1] for c in col) / len(col)
            # 5 Nov 2026 (round 3): the facing walls of those floors at that x, at any depth (a set-back wall too)
            hits = []
            for lid in missing:
                for w_ in geo[lid].facing_walls(normal):
                    a, b = _dot(w_["start"], along), _dot(w_["end"], along)
                    if min(a, b) - CONTAIN_TOL_M <= t <= max(a, b) + CONTAIN_TOL_M:
                        hits.append((lid, w_))
            walls = sorted({w_["id"] for _, w_ in hits})
            if hits:
                lid0, w0 = min(hits, key=lambda h: (order.get(h[0], 99), -_dot(h[1]["start"], outv), h[1]["id"]))
                depth = front - _dot(w0["start"], outv)
                place = (along[0] * t + outv[0] * (front - depth), along[1] * t + outv[1] * (front - depth))
            else:
                place = (along[0] * t + outv[0] * front, along[1] * t + outv[1] * front)
            frames = sorted({str(c[2][2].get("entity")) for c in col if c[2][2].get("entity")})
            # no facing wall at that x on those floors (a notch, a court): minor
            notch = not hits
            if notch:
                sev = "minor"
            out.append(_finding("RC8", sev, missing[0], f"{name}: an opening {w:.2f} m wide at x {x:.2f} m from its left "
                                f"end is drawn on {floors(on_el)}; the plan has none there on {floors(missing)} (plan "
                                f"point ({place[0]:.2f}, {place[1]:.2f}); facing wall pieces there: "
                                f"{', '.join(walls[:6]) or 'none'}{' ...' if len(walls) > 6 else ''}; positions aligned, "
                                f"shift {best:+.2f} m)" + ("; no facing wall at that x (a notch or a court): minor"
                                                           if notch else ""), [src_el, "plans of " + floors(missing)],
                                place, frames + walls, region=rid, side=side, column_x=round(x, 2),
                                levels_shown=on_el, levels_missing=missing, plan_walls=walls,
                                elevation_entities=frames))
        if outside:
            out.append(_finding("RC8", "info", None, f"{name}: {len(outside)} column(s) beyond the facing walls' extent "
                                f"(x {_fmt_x(outside)} m) left out: not openings of this facade", [src_el, "plans"],
                                region=rid, side=side))
        for col in _columns(p_only, MATCH_M):
            col = sorted(col, key=lambda c: (order.get(c[1], 99), c[2][2]["id"]))
            xs = [c[0] for c in col]
            x = sum(xs) / len(xs)
            lids = [c[1] for c in col]
            ids = [c[2][2]["id"] for c in col]
            o = col[0][2][2]
            out.append(_finding("RC8", "minor", lids[0], f"{name}: the plan's {o.get('type')} at x {x:.2f} m "
                                f"({col[0][2][1]:.2f} m wide; {', '.join(ids[:6])}) on {floors(lids)} is not drawn "
                                f"there on the elevation", [f"plans of {floors(lids)}", src_el],
                                tuple(o["center"]), ids, region=rid, side=side, column_x=round(x, 2),
                                levels_missing=sorted(set(lids), key=lambda v: (order.get(v, 99), v))))
    if unplaced:
        out.append(_finding("RC8", "minor", None, f"{name}: {len(unplaced)} of its {len(positions)} openings stand "
                            f"at no level's height (sills " + _fmt_x([float(p['sill']) for p in unplaced])
                            + " m): the elevation's heights and the levels disagree", [src_el, "levels"], region=rid))
    return out, ((matched, with_inside, -span_gap) if aligned else (0, 0, -99.0))


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
    secs = ", ".join(heights.get("section_regions") or [])
    sec_src = f"section {secs}" if secs else "the levels (no section)"
    levels = base_levels(building)
    by_id = {lv["id"]: lv for lv in levels}
    for hl in heights.get("levels") or []:
        lv = by_id.get(hl.get("level_id"))
        fz = hl.get("floor_z") or {}
        if lv is None:
            continue
        if fz.get("method") == "assumed":
            if not secs:
                continue                         # no section: one info finding below
            out.append(_finding("RC9", "minor", lv["id"], f"{lv['id']}: the section's heights were not used "
                                f"({fz.get('note') or 'assumed'}): the floor at {float(fz.get('value') or 0):.2f} m "
                                f"is assumed", [sec_src, f"plan of {lv['id']}"]))
            continue
        v = _value(fz)
        if v is not None and abs(v - float(lv.get("elevation") or 0.0)) > LEVEL_TOL_M:
            out.append(_finding("RC9", "major", lv["id"], f"{lv['id']}: {sec_src} puts the floor at {v:.2f} m, the "
                                f"model at {float(lv.get('elevation') or 0):.2f} m "
                                f"({lv.get('elevation_source') or 'source unknown'})", [sec_src, f"level {lv['id']}"]))
    if not secs and levels:
        out.append(_finding("RC9", "info", None, f"no section read: the heights of {len(levels)} level(s) are assumed or "
                            f"from the plans; the storeys are checked against each other only", ["levels"]))
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
        f = _fold(t).replace("BLOĞU", "BLOGU")
        for rx in BLOCK_RES:
            for m in rx.finditer(f):
                blocks.update(n for n in re.split(r"\s*[-/,&]\s*", m.group(1).strip()) if n)
                words.append(str(t).strip())
        for rx in COUNT_RES:
            for m in rx.finditer(f):
                counts.append(int(m.group(1)))
                words.append(str(t).strip())
    n = max([len(blocks)] + counts)
    return n, sorted(set(words))


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
    dwellings = sorted({str(t).strip() for t in site_texts for rx in DWELLING_RES if rx.search(_fold(t))})
    if dwellings:
        out.append(_finding("RC10", "info", None, f"{src} counts dwellings ({'; '.join(dwellings[:4])}): a count of "
                            f"flats or houses, not of buildings, so not compared with the model", [src]))
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
        if t.get("unknown_layer") and near_wall > TAG_WALL_FACE_M:
            continue                         # a column or furniture tag ('50/50', '60/120') on a layer of no role
        dists = sorted(((_seg_dist(p, a, b), o) for o, (a, b) in spans), key=lambda x: x[0])
        if any(d <= TAG_REACH_M and abs(float(o.get("width") or 0) - t["w"]) <= TAG_WIDTH_TOL_M for d, o in dists):
            continue
        nearest = next(((d, o) for d, o in dists if d <= TAG_NEAREST_M), None)
        hits.append((t, nearest))
    out = []
    for t, nearest in hits:
        # 5 Nov 2026 (review): severity by the mismatch itself, never by the count
        sev = "minor"
        if nearest:
            d, o = nearest
            if abs(float(o.get("width") or 0) - t["w"]) > TAG_MAJOR_WIDTH_M:
                sev = "major"
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
    window, glass or text layer (``wenart.ingest.generic.layer_names``), or on a layer of no known role (marked
    ``unknown_layer``: ``rc11`` takes those only next to a wall face), sizes in ``TAG_SIZE_CM``."""
    from wenart.ingest.generic import layer_names as LN

    rx = size_tag_re()
    out = []
    for t in texts:
        m = rx.match(str(t.get("text") or ""))
        role = LN.layer_role(t.get("layer"))
        if not m or (role is not None and role not in TAG_LAYER_ROLES):
            continue
        w, h = int(m.group(1)), int(m.group(2))
        if not (TAG_SIZE_CM[0][0] <= w <= TAG_SIZE_CM[0][1] and TAG_SIZE_CM[1][0] <= h <= TAG_SIZE_CM[1][1]):
            continue
        out.append(dict(t, w=w / 100.0, h=h / 100.0, unknown_layer=role is None))
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
