"""RC18: the reading checked against the Turkish building and fire regulations (21 Nov 2026, user OK).

What: ``findings(building)`` returns the places where the building model breaks a limit of the Planlı Alanlar İmar
Yönetmeliği (PAİY) or of the Binaların Yangından Korunması Hakkında Yönetmelik (BYKHY), each limit read from
``regulations_tr.json`` (article, value, Turkish wording, two sources or more; the limits the sources could not settle
are listed there under ``left_out``). Every finding is shaped like ``wenart.reading_check._finding`` (``check:
"RC18"``, ``rule``, ``severity``, ``level_id``, ``message`` with the article first, ``place``, ``element_ids``) plus
``advisory: true`` and ``limit`` (the limit's id). The rules (``RULES``):

1. ``room_min_size`` (PAİY 29(1)): in each dwelling, no living room, bedroom, kitchen, bathroom or toilet reaching its
   net area and narrow side (the best room of each type is judged: the article sets the one room each dwelling must
   have);
2. ``light_air`` (PAİY 32(1)): a bedroom, or every living room of a dwelling, with no window or door straight to the
   outside (a balcony counts, a light well does not); a kitchen with none to the outside or a light well;
3. ``light_well_size`` (PAİY 32(2)-(3)): a light well under 1.50 m / 4.50 m² (2.00 m / 9.00 m² from 8 storeys), an
   air shaft under 0.60 m / 0.36 m² (21 Nov 2026: ``room_subtype`` air_shaft as the reader types it, or a label naming
   one: H.B 50/50, HAVA BACASI);
4. ``stair_width`` (PAİY 31): a storey stair's flight under 1.20 m (the common stair of a building of several
   dwellings; its half landing too) or 1.00 m (the stair inside one dwelling);
5. ``stair_steps`` (PAİY 31): a common stair's tread under 0.27 m, its riser over 0.18 m (0.16 m with no lift) or
   2r + g outside 0.60-0.64 m (risers from the drawn storey height and the drawn steps only);
6. ``lift_required`` (PAİY 34(1)): 4 storeys or more (inhabited basements counted, attics and roof terraces not) and
   no lift;
7. ``storey_height`` (PAİY 28(4)): a storey people live in whose interior height, read from a section, is under 2.60 m
   (2.40 m allowed only on parcels with an air obstacle: the finding says which side of 2.40 it is on);
8. ``corridor_width`` (BYKHY, kaçış yolu genişliği): a common hall of a building of several dwellings narrower than
   1.10 m everywhere;
9. ``entrance_door_width`` (BYKHY 47(1)): a building or dwelling entrance door under 0.70 m (the original text's
   value; the amended 0.80 m is reported in the message, not checked: the sources disagree by version);
10. ``escape_stairs`` (BYKHY 48): a residential building over 21.50 m with fewer than two storey stairs, over 51.50 m
    with no fire lobby (yangın güvenlik holü);
11. ``travel_distance`` (BYKHY 48(2)): in a residential building of more than 4 storeys, a point of a flat more than
    30 m from the flat's door (the bound with sprinklers; the reading does not know whether there are any).

Every finding is advisory: ``wenart.reading_check.check`` counts them under ``counts["regulations"]``, never in the
verdict, never in ``counts["advisory"]``, so no grade counts them until they are measured on the projects.

Why: the user (21 Nov 2026): "Make sense of the building": a building that makes no legal or architectural sense is a
reading error as often as a design one (a corridor too narrow because a wall was misplaced, a bedroom with no window
because the facade was not read), so the limits of the regulations are one more check of the reading.

How: on the building model only (no drawing, no AI): room types from ``sense.sense_type``; a room's narrow side is the
diameter of the largest circle inside its polygon (the short side of a rectangle; the wider arm of an L, so an L is
never called narrow by its notch); the faces to the outside, a balcony or a light well and the windows on them from
``wenart.ingest.completion.Level`` (as RC14's ``room_without_window``); dwellings are the groups of rooms joined by
doors once the core (stair, lift, shaft, fire lobby, light well, technical rooms) and, on a storey of two kitchens or
more, the halls at the core are taken out; a building is of several dwellings when a storey has two such groups with a
kitchen or the building has three kitchens. Every distance compared with a limit gets ``TOL_M`` (areas ``TOL_AREA``)
of slack for the reading's own error; where a value depends on cases the reading cannot tell, the bound that holds in
every case is checked. A window on an outer wall a sliver off a room (``FACADE_OFFSET_M``) is the room's own; a finding
on a room bounded by a wall the reading inferred says so (``reading_suspect``, ``inferred_walls``): the judged sample
of 21 Nov 2026 found most misses there. The rooms an undrawn ground floor was cut to (``not_drawn_rooms``) are not
judged (21 Nov 2026, the fix round). ``python -m wenart.reading_check regulations --out DIR`` prints the findings.
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import re
from pathlib import Path
from typing import Optional

import shapely
from shapely.geometry import Point

from wenart import building as B
from wenart.reading_check import sense as SN

CHECK = "RC18"
NAME = "Turkish regulations"
DATA_PATH = Path(__file__).resolve().parent / "regulations_tr.json"
RULES = {
    "room_min_size": "a dwelling whose living room, bedroom, kitchen, bathroom or toilet is under the minimum size",
    "light_air": "a bedroom, a dwelling's living room or a kitchen without the daylight and air the rules ask",
    "light_well_size": "a light well or an air shaft under its minimum size",
    "stair_width": "a stair flight or half landing narrower than the minimum",
    "stair_steps": "a common stair's riser, tread or 2r + g outside the rules",
    "lift_required": "a building of four storeys or more with no lift",
    "storey_height": "a storey people live in lower than the minimum interior height",
    "corridor_width": "a common hall narrower than an escape route may be",
    "entrance_door_width": "a building or dwelling entrance door narrower than an escape door may be",
    "escape_stairs": "a tall residential building with too few escape stairs or no fire lobby",
    "travel_distance": "a point of a flat too far from the flat's door",
}
REG_NAMES = {"PAIY": "PAİY", "BYKHY": "BYKHY"}
SEVERITY = "minor"            # advisory until measured on the projects (21 Nov 2026)
TOL_M = 0.05                  # the reading's own error on a width or a narrow side
TOL_AREA = 0.03               # ... and on an area (a share of the limit)
TOL_STEP_M = 0.01             # ... on a tread or on 2r + g
RISER_TOL_M = 0.005           # ... and on a riser (27 Nov 2026: shared with the stair formula check of the reading)
CIRCLE_TOL_M = 0.01           # the precision of the largest inscribed circle
HABITABLE = ("living", "bedroom", "kitchen")
CORE = ("stair", "lift", "shaft", "fire_lobby", "light_well", "technical")
SIZE_GROUPS = {"living": ("living",), "bedroom": ("bedroom",), "kitchen": ("kitchen",),
               "bathroom": ("bathroom", "shower"),
               # a bathroom holds a toilet: the toilet the article asks for may be the bathroom's (Madde 29(2))
               "wc": ("wc", "bathroom", "shower")}
SIZE_LIMITS = {"living": "paiy29_living", "bedroom": "paiy29_bedroom", "kitchen": "paiy29_kitchen",
               "bathroom": "paiy29_bathroom", "wc": "paiy29_wc"}
AIR_SHAFT_RE = re.compile(r"(?<![a-z])hava\s*(?:bacasi|baca|boslugu)(?![a-z])")
# 21 Nov 2026: the reader's air-shaft words (H.B 50/50, havalandırma ...), ``topology._AIR_SHAFT_PATTERN``
from wenart.ingest.generic.topology import _AIR_SHAFT_PATTERN as _TP_AIR  # noqa: E402
TP_AIR_RE = re.compile(_TP_AIR)
COMMON_HALL_RE = re.compile(r"(?<![a-z])(?:kat\s*hol|ortak|floor\s*hall|common|lobby|lobi|apartman\s*hol|bina\s*giris)")
ENTRANCE_ROOMS = ("hall", "stair", "fire_lobby", "living")
OPEN_LINK_ROOMS = ("living", "dining")     # a kitchen open to one of these takes its daylight through it
ENTRANCE_LEVEL_M = 1.6        # an outer door on a storey this close to the ground (0.0) is an entrance (RC14)
STAIR_PIECE_REACH_M = 0.5     # a stair piece this close to a shared room is the common stair
STAIR_IN_HALL_SHARE = 0.3     # a stair piece this much inside a hall stands in it (that hall is the core's)
MIN_HALL_M2 = 1.0             # halls smaller than this are a door's recess, not a corridor
# 21 Nov 2026 (the judged sample: real17's salon has its glazed door on a facade wall the reading put on the band's
# outer line, a sliver away from the room, so no face of the room reached it): a window or door on an outer wall
# this far beyond the wall's half thickness from a room, nearer to it than to any other room, is the room's own
FACADE_OFFSET_M = 0.4
SUSPECT_REACH_M = 0.15        # a room this close beyond an inferred wall's half thickness is bounded by it


# --------------------------------------------------------------------------------------------------------- helpers
def load_limits(path: Path = DATA_PATH) -> dict:
    """The ``limits`` of the data file (``regulations_tr.json``)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))["limits"]


def cite(lim: dict) -> str:
    """'PAİY Madde 29(1)': the regulation and the article of a limit."""
    return f"{REG_NAMES.get(lim.get('regulation'), lim.get('regulation'))} {lim.get('article')}"


def _finding(rule: str, limit_id: str, lim: dict, level: Optional[str], message: str, place=None,
             element_ids: Optional[list] = None, **extra) -> dict:
    out = {"check": CHECK, "name": NAME, "rule": rule, "severity": SEVERITY, "level_id": level,
           "message": f"{cite(lim)}: {message}", "place": None, "element_ids": list(element_ids or []),
           "advisory": True, "limit": limit_id}
    if place is not None:
        out["place"] = [round(float(place[0]), 2), round(float(place[1]), 2)]
    out.update(extra)
    return out


def narrow_side(poly) -> float:
    """The diameter of the largest circle inside ``poly`` (pure): the short side of a rectangle, the wider arm of an
    L (an L is never called narrow by its notch)."""
    if poly is None or poly.is_empty:
        return 0.0
    return 2.0 * shapely.maximum_inscribed_circle(poly, CIRCLE_TOL_M).length


def _measure(room: dict) -> tuple:
    """``(area, narrow side)`` of a room's polygon."""
    poly = SN._poly(room.get("polygon"))
    return (SN._area(room) or 0.0), narrow_side(poly)


def _fits(area: float, narrow: float, min_area: float, min_narrow: float) -> bool:
    return area >= min_area * (1.0 - TOL_AREA) - 1e-9 and narrow >= min_narrow - TOL_M - 1e-9


def _centre(room: dict):
    return SN._centre(room)


def not_drawn_rooms(building: dict) -> list:
    """The ids of the rooms an inferred ground floor was cut to (``level_inference.storeys.ground_floor.cut``:
    ``rooms_cut``): the drawing draws them only as the typical floor's larger rooms (pure; 21 Nov 2026)."""
    gf = (((building.get("level_inference") or {}).get("storeys") or {}).get("ground_floor") or {})
    cut = gf.get("cut") if isinstance(gf, dict) else None
    return list((cut or {}).get("rooms_cut") or []) if isinstance(cut, dict) else []


def _ftf(lv: dict) -> Optional[float]:
    """The storey's drawn floor-to-floor height (a vector reading of a section), else None."""
    v = lv.get("floor_to_floor")
    if isinstance(v, dict) and v.get("method") == "vector" and isinstance(v.get("value"), (int, float)):
        return float(v["value"])
    return None


# --------------------------------------------------------------------------------------------------------- context
class Context:
    """What every rule needs once (pure): the storeys, the room types, the dwellings of each storey, the lift, the
    building's kind and height."""

    def __init__(self, building: dict, limits: dict):
        from wenart.ingest import completion as CP

        self.b, self.limits = building, limits
        self.levels = {lv["id"]: lv for lv in building.get("levels") or []}
        self.base = SN._base_storeys(building)                       # alternatives out, typical copies in
        self.room_levels = [lv for lv in self.base if not lv.get("typical_of")]
        self.types = {}
        for lv in self.base:
            roof = SN._is_roof(lv)
            for r in SN._rooms_of(building, lv["id"]):
                self.types[r["id"]] = None if B.is_void_label(SN._label(r)) else SN.sense_type(r, roof=roof)
        self.rooms = {r["id"]: r for r in building.get("rooms") or [] if r.get("id") in self.types
                      and SN._poly(r.get("polygon")) is not None}
        # 21 Nov 2026 (the RC18 reader fix round; real20's salon judged at 10.4 m2 against the typical plan's 15.2 m2):
        # the rooms a ground floor the drawing does not draw was cut to (its footprint, ``ground_floor.cut``) have
        # inferred walls and no drawn windows on that side: their size and daylight are the inference's, not the
        # drawing's, so they are not judged (``not_judged``); the rest of that storey is the typical plan's own rooms
        self.not_judged = set(not_drawn_rooms(building))
        for rid in self.not_judged:
            self.rooms.pop(rid, None)
        self.layouts = {lv["id"]: self._layout(lv["id"]) for lv in self.room_levels}
        judged = {lv["id"] for lv in self.room_levels}
        kitchens = sum(1 for rid, t in self.types.items() if t == "kitchen" and rid in self.rooms
                       and self.rooms[rid]["level_id"] in judged)
        self.multi = any(lay["multi"] for lay in self.layouts.values()) or kitchens >= 3
        self.residential = any(t == "bedroom" for t in self.types.values())
        self.lift = any(t == "lift" for t in self.types.values()) or any(
            CP.LIFT_RE.search(SN._fold(SN._label(r))) and not CP.LIFT_CAR_RE.search(SN._fold(SN._label(r)))
            for r in self.rooms.values())
        self.storeys = self._storeys()
        g = None
        try:
            g = CP._ground_min(building, known=True)
        except Exception:  # noqa: BLE001 - no drawn ground: the reading's 0.0
            g = None
        ground = max(0.0, float(g)) if isinstance(g, (int, float)) else 0.0
        # the building's height, never more than it is: the floor of its top storey people live in over the ground
        # (any definition of yapı yüksekliği, to the roof or to the top storey, is at least this)
        self.height_m = max((SN._el(lv) for lv in self.storeys), default=0.0) - ground

    def _storeys(self) -> list:
        """The storeys the article counts (kat adedi): base storeys and typical copies; a basement only when people
        live in it (a living room, bedroom or kitchen); attics and roof terraces not (their rules are not checked)."""
        out = []
        for lv in self.base:
            if SN._is_roof(lv) or lv.get("roof_terrace") or lv.get("kind") in ("attic", "roof_terrace"):
                continue
            if lv.get("kind") == "basement" or (lv.get("order") or 0) < 0:
                src = lv.get("typical_of") or lv["id"]
                if not any(self.types.get(r["id"]) in HABITABLE for r in SN._rooms_of(self.b, src)):
                    continue
            out.append(lv)
        return out

    def _layout(self, lid: str) -> dict:
        """A storey's rooms, the links its doors make, its core and common halls, its dwellings and their doors."""
        rooms = {r["id"]: r for r in SN._rooms_of(self.b, lid) if SN._poly(r.get("polygon")) is not None}
        links = []
        for o, _wall, touched in SN.opening_rooms(self.b, lid):
            if not o.get("virtual") and o.get("type") not in ("door", "opening"):
                continue
            touched = [t for t in touched if t in rooms]
            for i in range(len(touched)):
                for j in range(i + 1, len(touched)):
                    links.append((touched[i], touched[j], o))
        nbr = {rid: set() for rid in rooms}
        for a, c, _o in links:
            nbr[a].add(c)
            nbr[c].add(a)
        core = {rid for rid in rooms if self.types.get(rid) in CORE}
        stair_polys = [p for _i, p in SN.stairs_of(self.b, lid)]
        to_stair = {rid for rid in rooms if self.types.get(rid) in ("stair", "fire_lobby")}
        halls = set()
        for rid, r in rooms.items():
            if self.types.get(rid) != "hall":
                continue
            poly = SN._poly(r["polygon"])
            # a hall of the core: named so, a stair standing in it, or a door to a stair room or a fire lobby (a door
            # to a lift is no sign: readings join a flat's room to the lift; a stair behind a wall is no sign either)
            if nbr[rid] & to_stair or COMMON_HALL_RE.search(SN._fold(SN._label(r))) or any(
                    poly.intersection(sp).area >= STAIR_IN_HALL_SHARE * sp.area for sp in stair_polys if sp.area > 0):
                halls.add(rid)

        def groups(removed: set) -> list:
            parent = {rid: rid for rid in rooms if rid not in removed}

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            for a, c, _o in links:
                if a in parent and c in parent:
                    parent[find(a)] = find(c)
            out: dict = {}
            for rid in parent:
                out.setdefault(find(rid), []).append(rid)
            return sorted((sorted(m) for m in out.values()), key=lambda m: m[0])

        cand = core | halls
        split = groups(cand)
        # the core and its halls fall into clusters (the rooms joined by doors among them); a cluster is shared when
        # two flat-like groups (three rooms or more, or a kitchen with a living room or bedroom) open onto it: a twin
        # house's two stairs and halls are each one house's own (real04), a block's floor hall is shared
        cparent = {rid: rid for rid in cand}

        def croot(x):
            while cparent[x] != x:
                cparent[x] = cparent[cparent[x]]
                x = cparent[x]
            return x
        for a, c, _o in links:
            if a in cand and c in cand:
                cparent[croot(a)] = croot(c)
        def flat_like(m: list) -> bool:
            kinds = {self.types.get(x) for x in m}
            return len(m) >= 3 or ("kitchen" in kinds and bool(kinds & {"living", "bedroom"}))
        group_of = {rid: i for i, m in enumerate(split) if flat_like(m) for rid in m}
        reach: dict = {}
        for a, c, _o in links:
            for x, y in ((a, c), (c, a)):
                if x in cand and y in group_of:
                    reach.setdefault(croot(x), set()).add(group_of[y])
        shared = {rid for rid in cand if len(reach.get(croot(rid), ())) >= 2}
        with_kitchen = [m for m in split if any(self.types.get(x) == "kitchen" for x in m)]
        multi = len(with_kitchen) >= 2
        common = (core | shared) if multi else set(core)
        dwellings = groups(common)
        doors = {}
        for i, m in enumerate(dwellings):
            ms = set(m)
            doors[i] = [o for a, c, o in links for x, y in ((a, c), (c, a)) if x in ms and y in shared
                        and self.types.get(y) in ("hall", "stair", "fire_lobby")]
        return {"rooms": rooms, "links": links, "core": core, "halls": (shared - core) if multi else set(),
                "shared": shared if multi else set(), "multi": multi, "common": common, "dwellings": dwellings,
                "doors": doors, "stairs": stair_polys}

    def common_stair(self, lid: str, piece: dict) -> bool:
        """True when a stair piece stands in or by a room of a shared cluster of its storey (the stair of several
        dwellings, not one dwelling's own)."""
        from wenart.reading_check.sense import _footprint

        lay = self.layouts.get(lid) or {}
        fp = _footprint(piece)
        if fp is None or not lay.get("shared"):
            return False
        return any(SN._poly(lay["rooms"][rid]["polygon"]).distance(fp) <= STAIR_PIECE_REACH_M + SN.EPS
                   for rid in lay["shared"] if rid in lay["rooms"])

    def flats(self) -> list:
        """``[(level id, members, entrance doors)]``: the dwellings judged one by one: on a storey of several dwellings
        each group holding a kitchen or a living room (a duplex's upper half, bedrooms only, is not judged alone); in a
        building of one dwelling the whole building (doors: none)."""
        if not self.multi:
            members = [rid for lv in self.room_levels for rid in self.layouts[lv["id"]]["rooms"]]
            return [(None, members, [])] if members else []
        out = []
        for lv in self.room_levels:
            lay = self.layouts[lv["id"]]
            for i, m in enumerate(lay["dwellings"]):
                kinds = {self.types.get(x) for x in m}
                if len(m) >= 2 and kinds & {"kitchen", "living"} and kinds & {"bathroom", "shower", "wc"}:
                    out.append((lv["id"], m, lay["doors"][i]))
        return out


# ------------------------------------------------------------------------------------------- 1. room minimum size
def room_min_size(ctx: Context) -> list:
    """Rule 1 (PAİY 29(1)): per dwelling and required type, the best room must reach the net area and the narrow side
    (``TOL_AREA``, ``TOL_M``); a drawn area text over the limit marks the finding ``reading_suspect``."""
    out = []
    for lid, members, _doors in ctx.flats():
        for key, group in SIZE_GROUPS.items():
            lim_id = SIZE_LIMITS[key]
            lim = ctx.limits[lim_id]
            cands = [ctx.rooms[m] for m in members if ctx.types.get(m) in group and m in ctx.rooms]
            if not cands or (key == "wc" and not any(ctx.types.get(r["id"]) == "wc" for r in cands)):
                continue
            amin, nmin = float(lim["min_area_m2"]), float(lim["min_narrow_side_m"])
            measured = [(r, *_measure(r)) for r in cands]
            if any(_fits(a, n, amin, nmin) for _r, a, n in measured):
                continue
            r, a, n = max(measured, key=lambda x: min(x[1] / amin, x[2] / nmin))
            short = [f"{a:.2f} m² net (min {amin:.2f})" if a < amin * (1.0 - TOL_AREA) else None,
                     f"narrow side {n:.2f} m (min {nmin:.2f})" if n < nmin - TOL_M else None]
            drawn = r.get("area_label")
            suspect = isinstance(drawn, (int, float)) and drawn >= amin * (1.0 - TOL_AREA) and a < amin * (1 - TOL_AREA)
            sx = _suspect(ctx, r)
            where = "the dwelling" if lid is None else f"the dwelling of {len(members)} rooms on {lid}"
            what = f"no {key} room reaches" if len(cands) > 1 else f"its only {key} room does not reach"
            out.append(_finding("room_min_size", lim_id, lim, r.get("level_id"),
                                f"{where}: {what} the minimum; the best is {r['id']} "
                                f"'{SN._label(r) or '-'}': {', '.join(s for s in short if s)}"
                                + (f"; the drawing's own area text says {drawn:.2f} m²: a reading error?" if suspect
                                   else "") + _suspect_text(sx),
                                _centre(r), [r["id"]], room_type=key, area_m2=round(a, 2), narrow_m=round(n, 2),
                                reading_suspect=bool(suspect) or sx["reading_suspect"],
                                inferred_walls=sx["inferred_walls"]))
    return out


# ------------------------------------------------------------------------------------------- 2. light and air
def lit_kinds(level, room: dict) -> set:
    """The kinds of face (``outside``, ``balcony``, ``light_well``) of ``room`` that carry a window, a door or an
    opening (the matching of RC14's ``room_without_window``)."""
    from wenart.ingest import completion as CP

    kinds = set()
    for f in level.faces(room):
        if f["kind"] in kinds:
            continue
        w = level.walls[f["wall_id"]]
        a, u, _ = CP._axis(w)
        for o in level.openings:
            if o.get("type") not in ("window", "door", "opening") or o.get("virtual") or not o.get("center"):
                continue
            w2 = level.walls.get(o.get("wall_id"))
            if w2 is None:
                continue
            c = o["center"]
            if w2["id"] != w["id"] and abs((c[0] - a[0]) * -u[1] + (c[1] - a[1]) * u[0]) > \
                    0.35 + float(w.get("thickness") or 0.2):
                continue
            t = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
            if f["t0"] - 0.2 <= t <= f["t1"] + 0.2:
                kinds.add(f["kind"])
                break
    return kinds


def offset_windows(level, room: dict) -> bool:
    """True when a window, door or opening on an outer wall stands within ``FACADE_OFFSET_M`` beyond the wall's half
    thickness of ``room`` and no other room is nearer to it (a facade read a sliver off the room)."""
    poly = level.polys.get(room["id"])
    if poly is None:
        return False
    for o in level.openings:
        if o.get("type") not in ("window", "door", "opening") or o.get("virtual") or not o.get("center"):
            continue
        w = level.walls.get(o.get("wall_id"))
        if w is None or not w.get("exterior"):
            continue
        pt = Point(tuple(o["center"][:2]))
        d = poly.distance(pt)
        if d > float(w.get("thickness") or 0.2) / 2.0 + FACADE_OFFSET_M + SN.EPS:
            continue
        if all(q.distance(pt) > d + SN.EPS for rid, q in level.polys.items() if rid != room["id"]):
            return True
    return False


def inferred_walls(ctx: Context, room: dict) -> list:
    """The ids of the walls the reading inferred (evidence method ``inferred``) along ``room`` (half a metre of its
    outline within half their thickness plus ``SUSPECT_REACH_M``): a finding on such a room may be the inference's,
    not the drawing's."""
    from shapely.geometry import LineString

    poly = SN._poly(room.get("polygon"))
    if poly is None:
        return []
    out = []
    for w in SN._walls_of(ctx.b, room.get("level_id")):
        if not (w.get("inferred") or any(isinstance(e, dict) and e.get("method") == "inferred"
                                         for e in w.get("evidence") or [])):
            continue
        reach = float(w.get("thickness") or 0.2) / 2.0 + SUSPECT_REACH_M
        line = LineString([tuple(w["start"][:2]), tuple(w["end"][:2])])
        if poly.distance(line) <= reach + SN.EPS and poly.boundary.intersection(line.buffer(reach)).length >= 0.5:
            out.append(w["id"])
    return out


def _suspect(ctx: Context, room: dict) -> dict:
    """``{reading_suspect, inferred_walls}`` of a finding on ``room``."""
    ids = inferred_walls(ctx, room)
    return {"reading_suspect": bool(ids), "inferred_walls": ids}


def _suspect_text(extra: dict) -> str:
    ids = extra.get("inferred_walls") or []
    return (f"; bounded by the inferred wall{'s' if len(ids) > 1 else ''} {', '.join(ids[:3])}: a reading error?"
            if ids else "")


def light_air(ctx: Context) -> list:
    """Rule 2 (PAİY 32(1)): every bedroom straight to the outside (a window or door on a face to the outside or a
    balcony); at least one living room of each dwelling so; a kitchen to the outside or a light well unless it is open
    to a living or dining room. Storeys below ground, typical copies and storeys the exterior record does not qualify
    (R14) are left out, as in RC14."""
    from wenart.ingest import completion as CP
    from wenart.ingest import exterior as EX

    lim_id = "paiy32_light_air"
    lim = ctx.limits[lim_id]
    facades = (ctx.b.get("level_inference") or {}).get("facades")
    lit: dict = {}
    for lv in ctx.room_levels:
        lid = lv["id"]
        if not EX.level_ok(ctx.b, lid)[0]:
            continue
        if (facades is None or lid not in facades) and CP.below_ground(ctx.b, lv):
            continue
        level = CP.Level(ctx.b, lid, None)
        if level.outline is None:
            continue
        lay = ctx.layouts[lid]
        for room in level.rooms:
            if ctx.types.get(room["id"]) in HABITABLE and room["id"] not in level.wells and room["id"] in ctx.rooms:
                kinds = lit_kinds(level, room)
                if not kinds & {"outside", "balcony"} and offset_windows(level, room):
                    kinds.add("outside")
                lit[room["id"]] = kinds
    out = []
    direct = ("outside", "balcony")
    for rid, kinds in lit.items():
        r = ctx.rooms.get(rid)
        if r is None:
            continue
        t = ctx.types.get(rid)
        if t == "bedroom" and not kinds & set(direct):
            why = "its only window is onto a light well" if "light_well" in kinds else \
                "no window or door of it opens to the outside or a balcony"
            sx = _suspect(ctx, r)
            out.append(_finding("light_air", lim_id, lim, r["level_id"], f"bedroom {rid} '{SN._label(r) or '-'}' gets "
                                f"no light and air straight from outside: {why}{_suspect_text(sx)}", _centre(r), [rid],
                                part="bedroom", **sx))
        elif t == "kitchen" and not kinds & {"outside", "balcony", "light_well"}:
            lay = ctx.layouts.get(r["level_id"]) or {}
            open_to = any(o.get("virtual") or o.get("type") == "opening"
                          for a, c, o in lay.get("links") or [] if rid in (a, c)
                          and ctx.types.get(c if a == rid else a) in OPEN_LINK_ROOMS)
            if open_to:
                continue
            sx = _suspect(ctx, r)
            out.append(_finding("light_air", lim_id, lim, r["level_id"], f"kitchen {rid} '{SN._label(r) or '-'}' has no "
                                f"window to the outside or onto a light well{_suspect_text(sx)}", _centre(r), [rid],
                                part="kitchen", **sx))
    for lid, members, _doors in ctx.flats():
        livings = [m for m in members if ctx.types.get(m) == "living" and m in lit]
        if not livings or any(lit[m] & set(direct) for m in livings):
            continue
        big = max(livings, key=lambda m: SN._area(ctx.rooms[m]) or 0.0)
        r = ctx.rooms[big]
        sx = _suspect(ctx, r)
        out.append(_finding("light_air", lim_id, lim, r["level_id"],
                            f"no living room of the dwelling ({', '.join(livings[:4])}) gets light and air straight "
                            f"from outside (at least one must){_suspect_text(sx)}", _centre(r), livings, part="living",
                            **sx))
    return out


# ------------------------------------------------------------------------------------------- 3. light wells
def light_well_size(ctx: Context) -> list:
    """Rule 3 (PAİY 32(2)-(3)): a light well under 1.50 m / 4.50 m² (2.00 m / 9.00 m² from
    ``high_from_storeys_safe`` storeys, true whichever version splits at 6 or 7); an air shaft (named so) under
    0.60 m / 0.36 m²."""
    out = []
    wl_id, as_id = "paiy32_light_well", "paiy32_air_shaft"
    wl, ash = ctx.limits[wl_id], ctx.limits[as_id]
    high = len(ctx.storeys) >= int(wl.get("high_from_storeys_safe") or 8)
    band = wl["high"] if high else wl["low"]
    for lv in ctx.room_levels:
        for rid in ctx.layouts[lv["id"]]["rooms"]:
            r = ctx.rooms.get(rid)
            if r is None:
                continue
            # 21 Nov 2026 (the RC18 fix round): the reader types air shafts (``room_subtype`` air_shaft: an air-shaft
            # word such as H.B 50/50, or an unnamed doorless face under 1.0 m across); a label naming one counts too
            air = r.get("room_subtype") == "air_shaft" or bool(AIR_SHAFT_RE.search(SN._fold(SN._label(r)))) or (
                r.get("room_subtype") != "light_well" and bool(TP_AIR_RE.search(SN._fold(SN._label(r)))))
            if ctx.types.get(rid) != "light_well" and not air:
                continue
            lim_id, lim = (as_id, ash) if air else (wl_id, wl)
            amin = float((lim if air else band)["min_area_m2"])
            nmin = float((lim if air else band)["min_narrow_side_m"])
            a, n = _measure(r)
            if _fits(a, n, amin, nmin):
                continue
            what = "air shaft" if air else "light well"
            sx = _suspect(ctx, r)
            out.append(_finding("light_well_size", lim_id, lim, lv["id"],
                                f"{what} {rid} '{SN._label(r) or '-'}' is {a:.2f} m² with a narrow side of {n:.2f} m; "
                                f"the minimum is {amin:.2f} m² and {nmin:.2f} m"
                                + ("" if air else f" ({len(ctx.storeys)} storeys)") + _suspect_text(sx),
                                _centre(r), [rid], area_m2=round(a, 2), narrow_m=round(n, 2), **sx))
    return out


# ------------------------------------------------------------------------------------------- 4-5. stairs
def _storey_stairs(ctx: Context) -> list:
    """``[(level, piece)]``: the stair pieces that climb a storey (``sense.storey_stairs``, false stairs out) on the
    storeys whose rooms are judged."""
    try:
        _f, false_ids = SN.false_stairs(ctx.b)
    except Exception:  # noqa: BLE001 - no false-stair test: every stair counts
        false_ids = set()
    pieces = {f.get("id"): f for f in ctx.b.get("furniture") or [] if f.get("type") == "stair"}
    out = []
    for lv in ctx.room_levels:
        for sid, _p in SN.storey_stairs(ctx.b, lv["id"], false_ids):
            if sid in pieces and pieces[sid].get("build") is not False:
                out.append((lv, pieces[sid]))
    return out


def stair_width(ctx: Context) -> list:
    """Rule 4 (PAİY 31): residential buildings only; each storey stair's narrowest flight against 1.20 m (a building of
    several dwellings, ``Context.common_stair``) or 1.00 m (the stair inside one dwelling); the common stair's half
    landing against 1.20 m when it is drawn (not assumed)."""
    if not ctx.residential:
        return []
    lim_id = "paiy31_stair_width"
    lim = ctx.limits[lim_id]
    out = []
    for lv, f in _storey_stairs(ctx):
        common = ctx.common_stair(lv["id"], f)
        need = float(lim["common_residential_min_m"] if common else lim["in_unit_min_m"])
        kind = "common stair" if common else "stair inside the dwelling"
        st = f.get("stair") or {}
        widths = [float(fl["width"]) for fl in st.get("flights") or [] if isinstance(fl.get("width"), (int, float))
                  and (fl.get("lines") or 0) >= 3]
        c = (f.get("footprint") or {}).get("center")
        if widths and min(widths) < need - TOL_M:
            out.append(_finding("stair_width", lim_id, lim, lv["id"],
                                f"{kind} {f['id']}: a flight is {min(widths):.2f} m wide; the minimum is {need:.2f} m",
                                c, [f["id"]], part="flight", width_m=round(min(widths), 2)))
        land = st.get("landing") or {}
        if common and land and not st.get("landing_assumed") and isinstance(land.get("depth"), (int, float)) \
                and float(land["depth"]) < need - TOL_M:
            out.append(_finding("stair_width", lim_id, lim, lv["id"],
                                f"common stair {f['id']}: its half landing is {float(land['depth']):.2f} m deep; the "
                                f"minimum is {need:.2f} m", c, [f["id"]], part="landing",
                                width_m=round(float(land["depth"]), 2)))
    return out


def stair_steps(ctx: Context) -> list:
    """Rule 5 (PAİY 31): the common stairs (``Context.common_stair``): the drawn tread (the flights' tread
    spacing) under 0.27 m; the riser, from the drawn storey height over the drawn steps (n or n + 1 risers: a finding
    only when both counts break the rule), over 0.18 m (0.16 m with no lift) or 2r + g outside 0.60-0.64 m."""
    if not ctx.residential:
        return []
    lim_id = "paiy31_steps"
    lim = ctx.limits[lim_id]
    gmin = float(lim["min_tread_m"])
    rmax = riser_limit(ctx.limits, ctx.lift)
    lo, hi = (float(x) for x in lim["two_r_plus_g_m"])
    out = []
    for lv, f in _storey_stairs(ctx):
        if not ctx.common_stair(lv["id"], f):
            continue
        st = f.get("stair") or {}
        treads = sorted(float(fl["spacing"]) for fl in st.get("flights") or []
                        if isinstance(fl.get("spacing"), (int, float)) and (fl.get("lines") or 0) >= 3)
        if not treads:
            continue
        g = treads[len(treads) // 2]
        c = (f.get("footprint") or {}).get("center")
        probs = []
        if g < gmin - TOL_STEP_M:
            probs.append(f"tread {g:.3f} m (min {gmin:.2f})")
        h, n = _ftf(lv), st.get("steps_drawn")
        if h and isinstance(n, int) and n >= 8:
            r_hi, r_lo = h / n, h / (n + 1)
            if r_lo > rmax + RISER_TOL_M:
                probs.append(f"riser {r_lo:.3f}-{r_hi:.3f} m (max {rmax:.2f}{'' if ctx.lift else ', no lift'})")
            s_lo, s_hi = 2 * r_lo + g, 2 * r_hi + g
            if s_hi < lo - TOL_STEP_M or s_lo > hi + TOL_STEP_M:
                probs.append(f"2r + g {s_lo:.3f}-{s_hi:.3f} m (0.60-0.64)")
        if probs:
            out.append(_finding("stair_steps", lim_id, lim, lv["id"], f"common stair {f['id']}: {'; '.join(probs)}",
                                c, [f["id"]], tread_m=round(g, 3)))
    return out


def riser_limit(limits: dict, lift: bool) -> float:
    """PAİY 31 (``paiy31_steps``): a common stair's highest riser, 0.18 m in a building with a lift, 0.16 m without
    (pure; the one source of this limit, 27 Nov 2026)."""
    lim = limits["paiy31_steps"]
    return float(lim["max_riser_with_lift_m"] if lift else lim["max_riser_no_lift_m"])


def steep_common_riser(ctx: "Context", level_id: str, piece: dict, riser: float) -> Optional[str]:
    """27 Nov 2026 (audit fix round 4b, item 3): the finding of a common stair (``Context.common_stair``) of a
    residential building whose riser (its formula's) is over ``riser_limit`` (``RISER_TOL_M`` of slack), else None
    (pure). A stair inside one dwelling is never judged (``in_unit_stair_steps``)."""
    if not ctx.residential or not ctx.common_stair(level_id, piece):
        return None
    rmax = riser_limit(ctx.limits, ctx.lift)
    if riser <= rmax + RISER_TOL_M:
        return None
    return (f"risers of {riser:.3f} m over {rmax:.2f} m ({cite(ctx.limits['paiy31_steps'])}: a common stair"
            f"{'' if ctx.lift else ' of a building with no lift'})")


# ------------------------------------------------------------------------------------------- 6. lift
def lift_required(ctx: Context) -> list:
    """Rule 6 (PAİY 34(1)): 4 storeys or more (``Context._storeys``) and no lift (a room of sense type lift or named
    after one, a car lift not counted)."""
    lim_id = "paiy34_lift"
    lim = ctx.limits[lim_id]
    n = len(ctx.storeys)
    if n < int(lim["min_storeys"]) or ctx.lift:
        return []
    names = ", ".join(lv["id"] for lv in ctx.storeys)
    return [_finding("lift_required", lim_id, lim, None, f"the building has {n} storeys ({names}; inhabited basements "
                     f"counted, attics and roof terraces not) and no lift is read", None, [], storeys=n)]


# ------------------------------------------------------------------------------------------- 7. storey height
def storey_height(ctx: Context) -> list:
    """Rule 7 (PAİY 28(4)): a storey people live in (a living room, bedroom or kitchen; attics and roof terraces out)
    whose interior height comes from a section and is under 2.60 m; ``part`` says whether it is under 2.40 m too (a
    breach in every case) or between (a breach unless the parcel has an air obstacle)."""
    lim_id = "paiy28_interior_height"
    lim = ctx.limits[lim_id]
    hmin, hair = float(lim["min_interior_height_m"]), float(lim["min_interior_height_air_obstacle_m"])
    out = []
    for lv in ctx.room_levels:
        if lv not in ctx.storeys or lv.get("ceiling_height_source") != "section":
            continue
        if not any(ctx.types.get(r) in HABITABLE for r in ctx.layouts[lv["id"]]["rooms"]):
            continue
        h = lv.get("ceiling_height")
        if not isinstance(h, (int, float)) or h >= hmin - TOL_STEP_M:
            continue
        low = h < hair - TOL_STEP_M
        out.append(_finding("storey_height", lim_id, lim, lv["id"],
                            f"{lv['id']} {lv.get('label') or ''}: interior height {h:.2f} m from the section; the "
                            f"minimum is {hmin:.2f} m" + (f" (and {hair:.2f} m even on a parcel with an air obstacle)"
                                                          if low else f" ({hair:.2f} m only on a parcel with an air "
                                                                      f"obstacle)"),
                            None, [], part="below_air_obstacle_min" if low else "below_min", height_m=round(h, 2)))
    return out


# ------------------------------------------------------------------------------------------- 8. corridors
def corridor_width(ctx: Context) -> list:
    """Rule 8 (BYKHY): a common hall (a hall at the core on a storey of several dwellings) whose largest inscribed
    circle is under 1.10 m: the whole hall is narrower than an escape route may be."""
    lim_id = "bykhy_corridor"
    lim = ctx.limits[lim_id]
    need = float(lim["min_width_m"])
    out = []
    for lv in ctx.room_levels:
        for rid in sorted(ctx.layouts[lv["id"]]["halls"]):
            r = ctx.rooms.get(rid)
            if r is None:
                continue
            a, n = _measure(r)
            if a < MIN_HALL_M2 or n >= need - TOL_M:
                continue
            out.append(_finding("corridor_width", lim_id, lim, lv["id"],
                                f"common hall {rid} '{SN._label(r) or '-'}' ({a:.1f} m²) is at most {n:.2f} m wide; an "
                                f"escape corridor may not be narrower than {need:.2f} m", _centre(r), [rid],
                                width_m=round(n, 2)))
    return out


# ------------------------------------------------------------------------------------------- 9. entrance doors
def _entrance_doors(ctx: Context) -> list:
    """``[(level id, opening, what)]``: each dwelling's doors onto the common rooms (a building of several dwellings)
    and the doors on an outer wall of a storey near the ground into a hall, a stair, a fire lobby or (one dwelling) a
    living room."""
    out, seen = [], set()
    for lid, _m, doors in ctx.flats():
        for o in doors:
            if o.get("type") == "door" and o.get("id") not in seen:
                seen.add(o.get("id"))
                out.append((lid, o, "dwelling entrance door"))
    for lv in ctx.room_levels:
        if abs(SN._el(lv)) > ENTRANCE_LEVEL_M + SN.EPS:
            continue
        for o, wall, touched in SN.opening_rooms(ctx.b, lv["id"]):
            if o.get("type") != "door" or o.get("virtual") or wall is None or not wall.get("exterior") \
                    or len(touched) != 1 or o.get("id") in seen:
                continue
            t = ctx.types.get(touched[0])
            if t in ENTRANCE_ROOMS and (t != "living" or not ctx.multi):
                seen.add(o.get("id"))
                out.append((lv["id"], o, "building entrance door"))
    return out


def entrance_door_width(ctx: Context) -> list:
    """Rule 9 (BYKHY 47(1)): an entrance door (``_entrance_doors``) whose modelled width (at least its clear width) is
    under ``checked_below_m`` (0.70 m, the original text; the amended text's 0.80 m is named, not checked)."""
    lim_id = "bykhy47_door"
    lim = ctx.limits[lim_id]
    need = float(lim["checked_below_m"])
    out = []
    for lid, o, what in _entrance_doors(ctx):
        w = o.get("width")
        if not isinstance(w, (int, float)) or w >= need - 0.005:
            continue
        out.append(_finding("entrance_door_width", lim_id, lim, lid,
                            f"{what} {o.get('id')} is {w:.2f} m wide; an escape door's clear width may not be under "
                            f"{need:.2f} m (0.80 m in the amended text)", o.get("center"), [o.get("id")],
                            width_m=round(float(w), 2)))
    return out


# ------------------------------------------------------------------------------------------- 10. escape stairs
def escape_stairs(ctx: Context) -> list:
    """Rule 10 (BYKHY 48): a residential building whose height (``Context.height_m``, a lower bound) is over 21.50 m
    with no storey holding two storey stairs; over 51.50 m with no fire lobby."""
    lim_id = "bykhy48_stairs_by_height"
    lim = ctx.limits[lim_id]
    if not ctx.residential:
        return []
    out = []
    h = ctx.height_m
    if h > float(lim["two_stairs_from_m"]):
        per = {}
        for lv, f in _storey_stairs(ctx):
            per.setdefault(lv["id"], []).append(f["id"])
        most = max((len(v) for v in per.values()), default=0)
        if most < 2:
            out.append(_finding("escape_stairs", lim_id, lim, None,
                                f"the building is at least {h:.1f} m high (its top storey's floor over the ground) and "
                                f"no storey has two storey stairs ({most} at most): over 21.50 m a dwelling building "
                                f"needs two, one of them protected, both reached from every flat", None,
                                sorted({i for v in per.values() for i in v}), part="two_stairs", height_m=round(h, 2)))
    if h > float(lim["fire_lobby_from_m"]) and not any(t == "fire_lobby" for t in ctx.types.values()):
        out.append(_finding("escape_stairs", lim_id, lim, None,
                            f"the building is at least {h:.1f} m high and no fire lobby (yangın güvenlik holü) is read: "
                            f"over 51.50 m its escape stairs need fire lobbies and pressurisation", None, [],
                            part="fire_lobby", height_m=round(h, 2)))
    return out


# ------------------------------------------------------------------------------------------- 11. travel distance
def _centre_of(o: dict):
    if o.get("center"):
        return tuple(o["center"][:2])
    line = o.get("line") or []
    if len(line) >= 2:
        return ((line[0][0] + line[-1][0]) / 2.0, (line[0][1] + line[-1][1]) / 2.0)
    return None


def flat_distance(ctx: Context, lid: str, members: list, doors: list) -> tuple:
    """``(metres, room id)``: the farthest point of a flat from its doors, never more than it is: straight lines from
    door to door inside each room and from a door to the room's farthest corner (pure)."""
    lay = ctx.layouts[lid]
    ms = set(members)
    by_room: dict = {m: [] for m in members}
    for a, c, o in lay["links"]:
        for x in (a, c):
            if x in ms and _centre_of(o) is not None:
                by_room[x].append(o)
    dist = {}
    heap = []
    for o in doors:
        if _centre_of(o) is not None:
            dist[o.get("id")] = 0.0
            heap.append((0.0, o.get("id"), o))
    heapq.heapify(heap)
    while heap:
        d, oid, o = heapq.heappop(heap)
        if d > dist.get(oid, math.inf) + 1e-9:
            continue
        p = _centre_of(o)
        for m, ops in by_room.items():
            if not any(x.get("id") == oid for x in ops):
                continue
            for o2 in ops:
                q = _centre_of(o2)
                nd = d + math.dist(p, q)
                if nd < dist.get(o2.get("id"), math.inf) - 1e-9:
                    dist[o2.get("id")] = nd
                    heapq.heappush(heap, (nd, o2.get("id"), o2))
    best, where = 0.0, None
    for m, ops in by_room.items():
        poly = SN._poly(ctx.rooms[m]["polygon"]) if m in ctx.rooms else None
        if poly is None:
            continue
        reach = [(dist[o.get("id")], _centre_of(o)) for o in ops if o.get("id") in dist]
        if not reach:
            continue
        far = max(min(d + math.dist(q, pt) for d, q in reach) for pt in list(poly.exterior.coords))
        if far > best:
            best, where = far, m
    return best, where


def travel_distance(ctx: Context) -> list:
    """Rule 11 (BYKHY 48(1)-(2)): residential, several dwellings, more than ``exempt_max_storeys`` storeys: a flat
    whose farthest point (``flat_distance``, a lower bound) is more than ``checked_over_m`` (30 m) from its doors."""
    lim_id = "bykhy48_travel"
    lim = ctx.limits[lim_id]
    if not (ctx.residential and ctx.multi) or len(ctx.storeys) <= int(lim["exempt_max_storeys"]):
        return []
    need = float(lim["checked_over_m"])
    out = []
    for lid, members, doors in ctx.flats():
        if not doors:
            continue
        d, where = flat_distance(ctx, lid, members, doors)
        if d <= need + TOL_M or where is None:
            continue
        r = ctx.rooms[where]
        out.append(_finding("travel_distance", lim_id, lim, lid,
                            f"a point of {where} '{SN._label(r) or '-'}' is at least {d:.1f} m from its flat's door "
                            f"({', '.join(str(o.get('id')) for o in doors[:3])}); the most is 30 m with sprinklers "
                            f"(20 m without)", _centre(r), [where] + [o.get("id") for o in doors[:3]],
                            distance_m=round(d, 1)))
    return out


# --------------------------------------------------------------------------------------------------------- run
RULE_FUNCS = (room_min_size, light_air, light_well_size, stair_width, stair_steps, lift_required, storey_height,
              corridor_width, entrance_door_width, escape_stairs, travel_distance)


def findings(building: dict, limits: Optional[dict] = None) -> list:
    """Every RC18 finding of a building model (the module docstring); a rule that fails writes one info finding."""
    limits = limits or load_limits()
    ctx = Context(building, limits)
    out = []
    for fn in RULE_FUNCS:
        try:
            out += fn(ctx)
        except Exception as exc:  # noqa: BLE001 - an advisory check never stops the reading check
            out.append({"check": CHECK, "name": NAME, "rule": fn.__name__, "severity": "info", "level_id": None,
                        "message": f"the rule {fn.__name__} did not run: {type(exc).__name__}: {str(exc)[:200]}",
                        "place": None, "element_ids": [], "advisory": True, "limit": None})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check regulations",
                                 description="RC18: the reading against the Turkish building and fire regulations")
    ap.add_argument("--out", required=True, help="a pipeline output (holds building.json)")
    ap.add_argument("--json", action="store_true", help="print the findings as JSON")
    a = ap.parse_args(argv)
    building = json.loads((Path(a.out) / "building.json").read_text(encoding="utf-8"))
    found = findings(building)
    if a.json:
        print(json.dumps(found, ensure_ascii=False, indent=1))
        return 0
    for f in found:
        print(f"[{f['rule']}] {f.get('level_id') or '-'}: {f['message']}")
    print(f"{len(found)} finding(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
