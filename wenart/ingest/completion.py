"""What a drawing leaves out, completed (6 Nov 2026; user on real21's structure run: "real21 only 1 floor seems to be
built you need to extrapolate what needs to be done. all floors needs to be done"; lesson UL331: "A drawing that draws
no windows ... still gets windows").

What: ``complete(build, sheets, by_level, to_building)`` runs in the pipeline once the building is assembled (rooms,
walls, openings, the outdoor spaces of ``wenart.levels``) and before the conflicts are numbered:

1. **Storeys** (``wenart.sheets.storeys`` counted them; the typical-floor copies built them): the record goes to
   ``building.level_inference.storeys`` and every inferred level carries ``storey_inference`` (rule, confidence, guess,
   reason). An inferred ground floor read from the typical plan loses its cantilevered balconies when the footprint
   is smaller than the typical floor (``cantilevers``), and its entrance is looked for at the core (``entrance``: an
   inferred door where a core hall reaches a facade that is no party wall, else an open point). A building with
   inferred storeys and no roof evidence gets an explicit inferred flat roof over its top storey.
2. **Windows** (``infer_windows``): a level whose plan draws no window at all (no window-layer geometry, no window
   block, no window tag: ``sheets.json completion``) and reads none gets inferred windows: every habitable room
   (``HABITABLE``) facing the outside on a wall that is no party wall, or a light well, one window (two on a long
   wall, ``LONG_FACE_M``); a room onto a balcony a balcony door; a wet room (``WET``) facing out or onto a light well a
   small high window. Sizes come from the project's own window tags (other plans of the documents), else
   ``DEFAULT_SIZES``. Party walls come only from a whole-label party text facing that side (``bitişik``, ``attached``, a
   joint note; never a bare ``komşu``: ``party_walls``, R46), never from the plan's shape, and never on a side with a
   drawn opening or on a low-confidence level (``party_vetoes``). A plan that draws windows never gets inferred ones: a habitable room
   there without a window is a finding (RC14), and a drawing whose windows were not read is a reading miss (RC14), never
   hidden by inference.

Every inferred item carries ``inferred: true``, evidence with ``method: inferred`` and the reason, and is listed in
``level_inference`` (``storeys``, ``windows``) and the reading check's report.

Why: real21 draws one typical floor, no window and no section: the model was a one-storey block with blank walls.
CLAUDE.md: where the documents are silent the AI infers and completes, marks every item and lists it.

How: pure geometry on the building dict (shapely): a room's faces are found by probing both sides of each wall near it
(``faces``): the far side lies outside the level's filled outline (``crossdoc.level_outline``), in a light well (a room
named or holding a light-well word, ``LIGHT_WELL_RE``), on a balcony (an outdoor space or an open-air room), or in
another room. No AI. Every change passes ``rule_guards.blocked`` first (rule keys ``party_wall``, ``party_balcony``,
``light_well``, ``below_ground``, ``window_inferred``, ``balcony_door_inferred``): a guard or a rule switched off stops
it, logged in ``level_inference.guarded``.
"""
from __future__ import annotations

import math
import re
import statistics
from typing import Callable, Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep

from wenart import building as B

HABITABLE = ("bedroom", "living", "kitchen", "office", "study", "dining")
WET = ("bathroom", "wc", "shower", "toilet")
OPEN_AIR = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch")
LIGHT_WELL_RE = re.compile(r"(?<![a-z])(?:aydinlik|isiklik|aydinlatma\s+boslugu|light\s*well|lightwell|lichthof"
                           r"|lichtschacht|courette|patio\s+de\s+luces)")
LIFT_RE = re.compile(r"(?<![a-z])(?:asansor|lift|elevator|aufzug|ascenseur)")
# R19 guards (the misfire hunters, 12 Nov 2026): a machine room (``wenart.ingest.lift_words.machine_room``, one test
# for the reader, the storey signals and this module: review MF13, CODE-05; makinesiz, makine dairesiz and MRL are a
# lift with no machine room), a lift lobby (HOL, HOLÜ, ÖNÜ, LOBİ) and a car lift (ARAÇ, OTO) are no passenger lift; a
# pit or void (KUYU, BOŞLUK) is a shaft level with no door
LIFT_LOBBY_RE = re.compile(r"(?<![a-z])(?:hol|holu|onu|lobi|lobby|lobisi)(?![a-z])")
LIFT_CAR_RE = re.compile(r"(?<![a-z])(?:arac|oto|car|vehicle|otopark)(?![a-z])")
LIFT_PIT_RE = re.compile(r"(?<![a-z])(?:kuyu|kuyusu|bosluk|boslugu|pit)(?![a-z])")
LIFT_MAX_M2 = 8.0               # a lift-named face larger than this a car is the whole core (a common hall: R16 G2)
LIFT_MIN_SIDE_M = 1.0           # ... and one under this a side is a duct named after the lift ('Elek.şoh. Asansör')
SAMPLE_M = 0.10                 # a wall is probed every this many metres
PROBE_M = 0.25                  # ... this far beyond each face
EDGE_M = 0.30                   # a window keeps this far from a corner and from another opening
MIN_FACE_M = 0.80               # a face shorter than this takes no window
LONG_FACE_M = 5.0               # a habitable room's free face this long takes two windows
PIER_M = 0.90                   # ... with this much wall between them
HEAD_M = 2.20                   # an inferred window's head over its floor (the doors' head)
PARTY_REACH_M = 3.0             # a party text this far from a facade's outer line names that facade (R46)
PARTY_ALONG_M = 0.30            # ... when its foot falls within that facade's extent (this much beyond its ends)
PARTY_FACE_TOL_M = 0.35         # a wall's outer face this close to that side's line lies on it
PARALLEL_SIN = 0.10
RUN_GAP_M = 0.40                # outline edges on one line with gaps this narrow are one facade (CS1-06) ...
RUN_JOG_M = 0.015               # ... jogs this small along it are CAD rounding (MF12)
THIN_WALL_M = 0.12              # an inner wall this thin, on a level whose outer walls are ...
OUTER_WALL_M = 0.20             # ... at least this thick, never takes an inferred window (review REG-02)
DEFAULT_SIZES = {"living": (1.80, 1.40), "dining": (1.50, 1.40), "bedroom": (1.40, 1.40), "office": (1.40, 1.40),
                 "study": (1.40, 1.40), "kitchen": (1.20, 1.20), "wet": (0.60, 0.60)}
BALCONY_DOOR = (0.90, 2.20)     # an inferred balcony door: width, height
BALCONY_DOOR_LIVING = (1.60, 2.20)  # ... of a living room: a glazed pair where the wall allows
CONFIDENCE = 0.5                # an inferred window's evidence confidence (the room and the facade are read; the
                                # window's place and size are not drawn)


# ------------------------------------------------------------------------------------------------- geometry helpers
def _poly(points) -> Optional[Polygon]:
    if not points or len(points) < 3:
        return None
    p = Polygon([tuple(q[:2]) for q in points]).buffer(0)
    if p.is_empty:
        return None
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda g: g.area)
    return p


def _axis(w: dict):
    (ax, ay), (bx, by) = w["start"][:2], w["end"][:2]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return (ax, ay), (1.0, 0.0), 0.0
    return (ax, ay), ((bx - ax) / length, (by - ay) / length), length


def _fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def is_light_well(room: dict, texts: Optional[list] = None) -> bool:
    """A light or air well (pure): its label names one, or a light-well word stands inside it (real21: an unlabelled
    face holding 'AYDINLIK')."""
    if LIGHT_WELL_RE.search(_fold(room.get("label") or room.get("label_raw"))):
        return True
    if not texts:
        return False
    p = _poly(room.get("polygon"))
    if p is None:
        return False
    return any(LIGHT_WELL_RE.search(_fold(t["text"])) and p.buffer(0.05).contains(Point(t["x"], t["y"]))
               for t in texts)


def is_lift(room: dict) -> bool:
    """A passenger lift's shaft (pure; R19 and R16 G2 guards): a lift word in its label and no machine-room, lobby or
    car-lift word, at most ``LIFT_MAX_M2`` per lift word and at least ``LIFT_MIN_SIDE_M`` a side."""
    label = _fold(room.get("label") or room.get("label_raw"))
    words = len(LIFT_RE.findall(label))
    from wenart.ingest import lift_words as LW       # 13 Nov 2026 (CODE-05): one machine-room test everywhere

    if not words or LW.machine_room(label) or LIFT_LOBBY_RE.search(label) or LIFT_CAR_RE.search(label):
        return False
    p = _poly(room.get("polygon"))
    if p is None:
        return True
    mrr = p.minimum_rotated_rectangle
    pts = list(mrr.exterior.coords)[:3] if mrr.geom_type == "Polygon" else []
    short = min(math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])) if len(pts) == 3 else 0.0
    return p.area <= LIFT_MAX_M2 * words and short >= LIFT_MIN_SIDE_M


def is_pit(room: dict) -> bool:
    """A lift's pit or pass-through void (KUYU, BOŞLUK): a shaft level with no landing door (pure)."""
    return is_lift(room) and bool(LIFT_PIT_RE.search(_fold(room.get("label") or room.get("label_raw"))))


def _ground_min(building: dict) -> Optional[float]:
    """The lowest ground z the reading knows around the building (``site.ground``: its levels, its surface), or None."""
    g = (building.get("site") or {}).get("ground") or {}
    zs = [float((x.get("z") or {}).get("value")) for x in g.get("levels") or []
          if isinstance(x, dict) and isinstance((x.get("z") or {}).get("value"), (int, float))]
    flat = (g.get("surface") or {}).get("flat_z")
    if isinstance(flat, (int, float)):
        zs.append(float(flat))
    return min(zs) if zs else None


def below_ground(building: dict, level: dict) -> Optional[str]:
    """Why a level is below ground, or None (pure; user, 6 Nov 2026: "underground floors will have no window"): a
    basement (kind ``basement`` or an order under the ground floor's), a level the reading closed as fully below ground
    (soil outside its walls: ``generic.underground``, the reading check's "fully below ground"), or a level whose floor
    and ceiling both lie under the lowest ground around the building."""
    from wenart.ingest import rule_guards as RG

    why = _below_ground(building, level)
    if why and RG.blocked("below_ground", building, {"level_id": level.get("id"), "why": why}):
        return None
    return why


def _below_ground(building: dict, level: dict) -> Optional[str]:
    lid = level.get("id")
    if level.get("kind") == "basement" or (level.get("order") or 0) < 0:
        return f"{lid} is a basement (under the ground floor)"
    if any("fully below ground" in str(w) and f"({lid})" in str(w) for w in building.get("warnings") or []):
        return f"{lid} is fully below ground (soil outside its walls)"
    gz = _ground_min(building)
    if gz is not None and isinstance(level.get("elevation"), (int, float)):
        top = float(level["elevation"]) + float(level.get("ceiling_height") or 2.7)
        if top <= gz + 1e-6:
            return f"{lid}'s floor and ceiling lie under the ground (ceiling {top:+.2f} m, ground {gz:+.2f} m)"
    return None


class Level:
    """A level's rooms, walls, openings, outline, light wells and open-air polygons, with the probes (pure)."""

    def __init__(self, building: dict, lid: str, texts: Optional[list] = None):
        from wenart.reading_check.crossdoc import level_outline, level_parts

        self.lid = lid
        self.rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid and _poly(r.get("polygon"))]
        self.polys = {r["id"]: _poly(r["polygon"]) for r in self.rooms}
        self.walls = {w["id"]: w for w in building.get("walls") or []
                      if w.get("level_id") == lid and w.get("start") and w.get("end")}
        self.openings = [o for o in building.get("openings") or [] if o.get("level_id") == lid]
        try:
            self.outline = level_outline(list(self.walls.values()), self.openings)
            # every filled part (a storey of two blocks): a probe in any of them, in no room, is void (CS1-10)
            parts = level_parts(list(self.walls.values()), self.openings)
        except Exception:  # noqa: BLE001 - no outline: nothing faces the outside
            self.outline, parts = None, []
        self.wells = {r["id"] for r in self.rooms if is_light_well(r, texts)}
        air = [_poly(s.get("polygon")) for s in (building.get("site") or {}).get("outdoor_spaces") or []
               if s.get("level_id") == lid and str(s.get("kind") or "") in OPEN_AIR]
        air = [p for p in air if p is not None]
        air += [self.polys[r["id"]] for r in self.rooms if str(r.get("room_type") or "") in OPEN_AIR]
        self.open_air = air
        self._air = [(p.bounds, prep(p.buffer(1e-6))) for p in air]
        self._rooms = [(self.polys[r["id"]].bounds, prep(self.polys[r["id"]].buffer(1e-6)), r) for r in self.rooms]
        filled = unary_union(parts) if len(parts) > 1 else self.outline
        self._inside = prep(filled.buffer(-1e-6)) if filled is not None else None

    def room_at(self, q) -> Optional[dict]:
        x, y = q
        pt = Point(q)
        for (x0, y0, x1, y1), pp, r in self._rooms:
            if x0 - 1e-6 <= x <= x1 + 1e-6 and y0 - 1e-6 <= y <= y1 + 1e-6 and pp.contains(pt):
                return r
        return None

    def kind_at(self, q, own: str) -> Optional[str]:
        """What lies at probe point ``q`` seen from room ``own``: ``own``, ``light_well``, ``balcony``, ``room``,
        ``outside`` or ``void`` (inside the outline, in no room)."""
        x, y = q
        pt = Point(q)
        for (x0, y0, x1, y1), pp in self._air:
            if x0 - 1e-6 <= x <= x1 + 1e-6 and y0 - 1e-6 <= y <= y1 + 1e-6 and pp.contains(pt):
                return "balcony"
        r = self.room_at(q)
        if r is not None:
            if r["id"] == own:
                return "own"
            return "light_well" if r["id"] in self.wells else "room"
        if self._inside is None:
            return None
        return "void" if self._inside.contains(pt) else "outside"

    def faces(self, room: dict) -> list:
        """``[{wall_id, t0, t1, kind, side}]``: the stretches of the walls near ``room`` with the room on one side and
        ``outside``, a ``light_well`` or a ``balcony`` on the other (``side`` +1 when the room lies left of the wall)."""
        p = self.polys.get(room["id"])
        if p is None:
            return []
        x0, y0, x1, y1 = p.bounds
        out = []
        for w in self.walls.values():
            xs, ys = (w["start"][0], w["end"][0]), (w["start"][1], w["end"][1])
            if max(xs) < x0 - 0.6 or min(xs) > x1 + 0.6 or max(ys) < y0 - 0.6 or min(ys) > y1 + 0.6:
                continue
            a, u, length = _axis(w)
            if length < MIN_FACE_M:
                continue
            n = (-u[1], u[0])
            reach = float(w.get("thickness") or 0.15) / 2.0 + PROBE_M
            steps = max(1, int(length / SAMPLE_M))
            cur = None
            for k in range(steps + 1):
                t = length * k / steps
                c = (a[0] + u[0] * t, a[1] + u[1] * t)
                left = (c[0] + n[0] * reach, c[1] + n[1] * reach)
                right = (c[0] - n[0] * reach, c[1] - n[1] * reach)
                kind, side = None, 0
                kl, kr = self.kind_at(left, room["id"]), self.kind_at(right, room["id"])
                if kl == "own" and kr in ("outside", "light_well", "balcony"):
                    kind, side = kr, 1
                elif kr == "own" and kl in ("outside", "light_well", "balcony"):
                    kind, side = kl, -1
                if kind and cur is not None and cur["kind"] == kind and cur["side"] == side:
                    cur["t1"] = t
                elif kind:
                    cur = {"wall_id": w["id"], "t0": t, "t1": t, "kind": kind, "side": side}
                    out.append(cur)
                else:
                    cur = None
        return [f for f in out if f["t1"] - f["t0"] >= MIN_FACE_M - 2 * SAMPLE_M]

    def taken(self, wall: dict) -> list:
        """The stretches of ``wall`` its openings (and those of a parallel wall within 0.35 m) take."""
        a, u, _ = _axis(wall)
        out = []
        for o in self.openings:
            if o.get("virtual") or not o.get("center"):
                continue
            w2 = self.walls.get(o.get("wall_id"))
            if w2 is None:
                continue
            if w2["id"] != wall["id"]:
                _a2, u2, _ = _axis(w2)
                if abs(u[0] * u2[1] - u[1] * u2[0]) > 0.05:
                    continue
                c = o["center"]
                if abs((c[0] - a[0]) * -u[1] + (c[1] - a[1]) * u[0]) > 0.35 + float(wall.get("thickness") or 0.2):
                    continue
            t = (o["center"][0] - a[0]) * u[0] + (o["center"][1] - a[1]) * u[1]
            half = float(o.get("width") or 0.0) / 2.0
            out.append((t - half, t + half))
        return out

    def free(self, face: dict) -> list:
        """The free pieces ``[(t0, t1)]`` of a face (``EDGE_M`` from its ends and from every opening)."""
        wall = self.walls[face["wall_id"]]
        pieces = [(face["t0"] + EDGE_M, face["t1"] - EDGE_M)]
        for s0, s1 in self.taken(wall):
            nxt = []
            for p0, p1 in pieces:
                if s1 + EDGE_M <= p0 or s0 - EDGE_M >= p1:
                    nxt.append((p0, p1))
                    continue
                if s0 - EDGE_M > p0:
                    nxt.append((p0, s0 - EDGE_M))
                if s1 + EDGE_M < p1:
                    nxt.append((s1 + EDGE_M, p1))
            pieces = nxt
        return [(p0, p1) for p0, p1 in pieces if p1 - p0 > 0.05]

    def at(self, wall_id: str, t: float) -> list:
        a, u, _ = _axis(self.walls[wall_id])
        return [round(a[0] + u[0] * t, 4), round(a[1] + u[1] * t, 4)]


# ------------------------------------------------------------------------------------------------------ party walls
def _run(ring: list, e) -> tuple:
    """The facade an outline edge belongs to (pure; CS1-06, MF12): the outline edges on its line (jogs under
    ``RUN_JOG_M``) end to end with gaps no wider than ``RUN_GAP_M`` (a wall's thickness), as ``(start, end)``."""
    (ex0, ey0), (ex1, ey1) = e
    el = math.hypot(ex1 - ex0, ey1 - ey0)
    eu = ((ex1 - ex0) / el, (ey1 - ey0) / el)
    ivals = []
    for p, q in ring:
        if math.dist(p, q) < 1e-6:
            continue
        offs = [abs((pt[0] - ex0) * -eu[1] + (pt[1] - ey0) * eu[0]) for pt in (p, q)]
        if max(offs) > RUN_JOG_M:
            continue
        ivals.append(tuple(sorted(((pt[0] - ex0) * eu[0] + (pt[1] - ey0) * eu[1]) for pt in (p, q))))
    t0, t1 = 0.0, el
    grew = True
    while grew:
        grew = False
        for a, c in ivals:
            if a <= t1 + RUN_GAP_M and c >= t0 - RUN_GAP_M and (a < t0 - 1e-9 or c > t1 + 1e-9):
                t0, t1 = min(t0, a), max(t1, c)
                grew = True
    return ((ex0 + eu[0] * t0, ey0 + eu[1] * t0), (ex0 + eu[0] * t1, ey0 + eu[1] * t1))


def _outer_on(level: Level, w: dict, side) -> bool:
    """True when wall ``w`` is a facade wall of ``side``: beyond its outer face, at its middle within the side's
    extent, lies the outside (pure; an interior partition on the facade's line is never a party wall)."""
    (ex0, ey0), (ex1, ey1) = side
    el = math.hypot(ex1 - ex0, ey1 - ey0)
    eu = ((ex1 - ex0) / el, (ey1 - ey0) / el)
    n = (-eu[1], eu[0])
    inside = level.outline.buffer(-1e-6)
    mid = ((ex0 + ex1) / 2.0, (ey0 + ey1) / 2.0)
    out = n if not inside.contains(Point(mid[0] + n[0] * 0.3, mid[1] + n[1] * 0.3)) else (-n[0], -n[1])
    ts = sorted(((p[0] - ex0) * eu[0] + (p[1] - ey0) * eu[1]) for p in (w["start"], w["end"]))
    t = (max(ts[0], 0.0) + min(ts[1], el)) / 2.0
    q = (ex0 + eu[0] * t + out[0] * 0.15, ey0 + eu[1] * t + out[1] * 0.15)
    return not inside.contains(Point(q))


def party_walls(level: Level, side_points: list) -> dict:
    """``{wall_id: evidence}``: the facade walls of the side of the level's outline a party text names (pure; R46). A
    whole-label text (``bitişik``, ``attached``, a joint note) outside the outline, at most ``PARTY_REACH_M`` from
    a facade's outer line with its foot within that facade, names the nearest such facade, unless a street text
    faces it; the facade is the run of outline edges on that line (``_run``), and every wall along it within its
    extent whose outer face lies on it, with the outside beyond (``_on_side``, ``_outer_on``), is a party wall; the
    run is the evidence's ``side`` (the veto checks the same walls: CS1-06, MF12)."""
    out: dict = {}
    if level.outline is None:
        return out
    ring_all = list(level.outline.exterior.coords)
    ring = [(ring_all[i], ring_all[i + 1]) for i in range(len(ring_all) - 1)]
    edges = [e for e in ring if math.dist(e[0], e[1]) > 0.5]

    def facade(sp):
        """The outline edge a text faces (R46: outside the outline, at most PARTY_REACH_M from the edge, its foot
        within the edge's extent, the nearest such edge), or None."""
        q = Point(sp["at"])
        if level.outline.buffer(-1e-6).contains(q):
            return None
        best = None
        for e in edges:
            (x0, y0), (x1, y1) = e
            el = math.hypot(x1 - x0, y1 - y0)
            t = ((q.x - x0) * (x1 - x0) + (q.y - y0) * (y1 - y0)) / el
            d = LineString(e).distance(q)
            if -PARTY_ALONG_M <= t <= el + PARTY_ALONG_M and d <= PARTY_REACH_M and (best is None or d < best[0]):
                best = (d, e)
        return best[1] if best else None

    streets = {facade(sp) for sp in side_points if sp.get("kind") == "street"} - {None}
    street_runs = [_run(ring, e) for e in streets]
    for sp in side_points:
        if sp.get("kind") != "party":
            continue
        e = facade(sp)
        if e is None or e in streets:          # a side a street text faces is never a party wall (R46 veto)
            continue
        side = _run(ring, e)
        if any(math.dist(side[0], s[0]) < 0.05 and math.dist(side[1], s[1]) < 0.05 for s in street_runs):
            continue
        for w in level.walls.values():
            if not _on_side(w, side) or not _outer_on(level, w, side):
                continue
            out.setdefault(w["id"], {"text": sp["text"], "entity": sp.get("entity"), "layer": sp.get("layer"),
                                     "at": [round(sp["at"][0], 2), round(sp["at"][1], 2)],
                                     "side": [[round(side[0][0], 3), round(side[0][1], 3)],
                                              [round(side[1][0], 3), round(side[1][1], 3)]]})
    return out



# ------------------------------------------------------------------------------------------------------ the sizes
def sizes_from_tags(tags: list) -> tuple[dict, str]:
    """``({room kind: (width, height)}, source)`` (pure): from the documents' window tags the living room takes the
    widest, the bedroom and the work room the median width, the kitchen the narrowest, all the median height; a wet
    room the smallest tag when it is a small window (at most 0.8 m high), else the default; ``DEFAULT_SIZES`` without
    tags."""
    if not tags:
        return dict(DEFAULT_SIZES), "defaults (no window tag in the documents)"
    ws = sorted(float(t["width"]) for t in tags)
    hs = sorted(float(t["height"]) for t in tags)
    h = statistics.median(hs)
    med = statistics.median(ws)
    out = {"living": (min(ws[-1], 2.4), h), "dining": (med, h), "bedroom": (med, h), "office": (med, h),
           "study": (med, h), "kitchen": (ws[0], min(h, 1.2) if ws[0] <= 1.0 else h)}
    small = [t for t in tags if float(t["height"]) <= 0.8]
    out["wet"] = (float(small[0]["width"]), float(small[0]["height"])) if small else DEFAULT_SIZES["wet"]
    texts = sorted({t["text"] for t in tags})
    return out, (f"the documents' window tags ({len(tags)}: {', '.join(texts[:6])}"
                 f"{' ...' if len(texts) > 6 else ''}; regions {', '.join(sorted({t['region'] for t in tags}))})")


# ------------------------------------------------------------------------------------------------- the inference
def _thin_inner(level: Level, w: dict, outer_t: float) -> bool:
    """A wall clearly thinner than the level's drawn outer walls (``THIN_WALL_M`` against ``OUTER_WALL_M``, the median
    of the walls flagged exterior): a partition, never a facade, whatever the probes say (an unread room behind it reads
    as the outside; REG-02) and whatever its exterior flag says (13 Nov 2026, review FC-04: real19's leaking outline
    flags the very partitions in front of the unread salon exterior)."""
    return outer_t >= OUTER_WALL_M and 0.0 < float(w.get("thickness") or 0.0) <= THIN_WALL_M


def _new_opening(kind: str, oid: str, level: Level, wall_id: str, t: float, width: float, height: float,
                 sill: Optional[float], reason: str, room: dict, face: dict, ev_file: str, region: Optional[str],
                 size_source: str) -> dict:
    o = {"id": oid, "type": kind, "level_id": level.lid, "wall_id": wall_id, "center": level.at(wall_id, t),
         "width": round(width, 3), "height": round(height, 3), "sill_height": None if sill is None else round(sill, 3),
         "swing_side": None, "status": "unverified", "assumed": ["height"] + (["sill_height"] if sill is not None
                                                                               else []),
         "inferred": True,
         "inference": {"rule": "UL331", "room_id": room["id"], "faces": face["kind"], "reason": reason,
                       "size_source": size_source},
         "evidence": [{"file": ev_file, "method": "inferred", "confidence": CONFIDENCE, "rule": "inferred_" + kind,
                       "text": reason, "region_id": region}]}
    if kind == "door":
        o["operation"], o["operation_source"] = "swing", "assumed"
    return o


def infer_level(building: dict, lid: str, party: dict, sizes: dict, size_source: str, next_id: Callable,
                texts: Optional[list] = None, ev_file: str = "", region: Optional[str] = None) -> list:
    """The inferred openings of one level (pure but for ``next_id(kind, level)``): see the module docstring."""
    from wenart.ingest import rule_guards as RG

    level = Level(building, lid, texts)
    if level.outline is None:
        return []
    new = []
    outer = [float(w.get("thickness") or 0.0) for w in level.walls.values() if w.get("exterior")]
    outer_t = statistics.median(outer) if outer else 0.0
    for room in sorted(level.rooms, key=lambda r: r["id"]):
        rtype = str(room.get("room_type") or "")
        if room["id"] in level.wells or (rtype not in HABITABLE and rtype not in WET):
            continue
        from wenart.ingest import exterior as EX
        spans = RG.active("exterior_spans", building)
        faces = [f for f in level.faces(room) if f["wall_id"] not in party
                 and (not spans or EX.allows(level.walls[f["wall_id"]], f["t0"], f["t1"]))
                 and not _thin_inner(level, level.walls[f["wall_id"]], outer_t)]
        label = room.get("label") or room["id"]
        # a balcony door where the room opens onto a balcony
        if rtype in HABITABLE:
            onto = sorted((f for f in faces if f["kind"] == "balcony"), key=lambda f: -(f["t1"] - f["t0"]))
            for f in onto[:1]:
                pieces = sorted(level.free(f), key=lambda p: -(p[1] - p[0]))
                if not pieces or pieces[0][1] - pieces[0][0] < BALCONY_DOOR[0]:
                    continue
                p0, p1 = pieces[0]
                if RG.blocked("balcony_door_inferred", building, {"level_id": lid, "room": room["id"],
                                                                  "wall": f["wall_id"]}):
                    continue
                # a living room's balcony door is a wide glazed pair where the wall allows
                dw = BALCONY_DOOR_LIVING[0] if rtype == "living" and p1 - p0 >= BALCONY_DOOR_LIVING[0] else \
                    BALCONY_DOOR[0]
                reason = (f"{room['id']} '{label}' ({rtype}) opens onto a balcony on {f['wall_id']} and no door is drawn "
                          f"there: an inferred balcony door")
                o = _new_opening("door", next_id("door", lid), level, f["wall_id"], (p0 + p1) / 2.0, dw,
                                 BALCONY_DOOR[1], None, reason, room, f, ev_file, region, "default balcony door")
                if dw == BALCONY_DOOR_LIVING[0]:
                    o["operation"] = "double"
                new.append(o)
                level.openings.append(o)
        # the window(s): the longest free face to the outside, else onto a light well
        wet = rtype in WET
        w, h = sizes["wet"] if wet else sizes.get(rtype, DEFAULT_SIZES.get(rtype, DEFAULT_SIZES["bedroom"]))
        cands = []
        rank = {"outside": 0, "balcony": 1, "light_well": 2} if not wet else {"outside": 0, "light_well": 1}
        minimum = 0.4 if wet else 0.6
        for f in faces:
            if f["kind"] not in rank:
                continue
            for p0, p1 in level.free(f):
                if p1 - p0 >= minimum:
                    cands.append((rank[f["kind"]], -(p1 - p0), f, p0, p1))
        if not cands:
            continue
        cands.sort(key=lambda c: (c[0], c[1]))
        _, _, f, p0, p1 = cands[0]
        if RG.blocked("window_inferred", building, {"level_id": lid, "room": room["id"], "wall": f["wall_id"],
                                                    "facing": f["kind"]}):
            continue
        span = p1 - p0
        width = min(w, span)
        sill = max(0.6, HEAD_M - h) if not wet else HEAD_M - h
        count = 2 if (not wet and span >= 2 * width + PIER_M and f["t1"] - f["t0"] >= LONG_FACE_M) else 1
        where = {"outside": "the outside", "balcony": "its balcony", "light_well": "a light well"}[f["kind"]]
        for k in range(count):
            t = p0 + span * (2 * k + 1) / (2 * count)
            reason = (f"{room['id']} '{label}' ({rtype}) faces {where} on {f['wall_id']} and the drawing draws no window "
                      f"on this plan: an inferred {'small high ' if wet else ''}window"
                      + (f" ({k + 1} of 2 on a long wall)" if count == 2 else ""))
            o = _new_opening("window", next_id("window", lid), level, f["wall_id"], t, width, h, sill, reason, room, f,
                             ev_file, region, size_source)
            new.append(o)
            level.openings.append(o)
    return new


# ----------------------------------------------------------------------------------------------- the pipeline hook
def G_centre(t) -> tuple:
    """A text's centre (its box's), page units: a label's word stands in its face (its start may lie on the wall)."""
    b = getattr(t, "box", None)
    if b and len(b) == 4:
        return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)
    return tuple(t.start)


def _region_for(sheets: Optional[dict], record) -> Optional[dict]:
    regions = (sheets or {}).get("regions") or []
    if getattr(record, "region_id", None):
        return next((r for r in regions if r["id"] == record.region_id), None)
    cands = [r for r in regions if r.get("file") == record.file and r.get("page") == record.page
             and r.get("class") in ("floor_plan", "alternative_floor_plan")]
    return cands[0] if len(cands) == 1 else None


def complete(build, sheets: Optional[dict], by_level: dict, to_building: Callable) -> None:
    """The pipeline hook (the module docstring): storeys, the inferred ground floor, the roof, the windows."""
    from wenart.ingest import rule_guards as RG

    b = build.building
    if not isinstance(b.get("level_inference"), dict):
        b["level_inference"] = {}
    # the staged rules as this reading ran them (13 Nov 2026): the build reads party_eaves from here
    b["level_inference"]["rules_staged"] = {k: RG.active(k, b) for k in sorted(RG.STAGED)}
    from wenart.ingest import ground_lines as GL
    GL.apply(build)                   # 13 Nov 2026 (R04): a ground burying storeys with doors at grade is refused
    rec = (sheets or {}).get("storeys") if sheets else None
    regions = ((sheets or {}).get("completion") or {}).get("regions") or {}
    from wenart.ingest.drawn_strokes import Drawn

    texts_by_level, region_by_level, party_by_level, strokes_by_level, drawn_by_level = {}, {}, {}, {}, {}
    side_by_level = {}
    for lid, works in by_level.items():
        w = sorted(works, key=lambda w: w.rank)[0]
        ex = w.extraction
        if ex.transform_to_building is None:
            continue
        drawn = Drawn.of(ex)
        if drawn is not None:
            drawn_by_level[lid] = drawn
        texts_by_level[lid] = [{"text": t.text, "x": p[0], "y": p[1], "entity": t.entity}
                               for t in ex.texts for p in [to_building(ex, G_centre(t))]]
        reg = _region_for(sheets, w.record)
        region_by_level[lid] = reg
        info = regions.get((reg or {}).get("id")) if reg else None
        side = [dict(s, at=list(to_building(ex, tuple(s["point"])))) for s in (info or {}).get("side_texts") or []]
        side_by_level[lid] = side
        party = {w: ev for w, ev in party_walls(Level(b, lid, texts_by_level[lid]), side).items()
                 if not RG.blocked("party_wall", b, {"level_id": lid, "wall": w, "why": ev.get("text")})}
        if party:
            party_by_level[lid] = party
        runs = []
        for run in (info or {}).get("stair_strokes") or []:
            poly = _poly([list(to_building(ex, tuple(c))) for c in run.get("corners") or []])
            if poly is not None:
                runs.append(dict(run, polygon=poly))
        if runs:
            strokes_by_level[lid] = runs
    from wenart.ingest import facades as FC
    every_text = [t for ts in texts_by_level.values() for t in ts]
    for lid in list(texts_by_level) if RG.active("party_plot", b) else []:
        level = Level(b, lid, texts_by_level[lid])
        edges = FC.edges_of(level)
        for i, ev in FC.plot_party(b, level, edges, every_text).items():
            for w in level.walls.values():
                if _on_side(w, edges[i]) and not RG.blocked("party_wall", b, {"level_id": lid, "wall": w["id"],
                                                                              "why": ev["text"]}):
                    party_by_level.setdefault(lid, {}).setdefault(w["id"], ev)
    vetoed = party_vetoes(b, party_by_level)
    if vetoed:
        b["level_inference"]["party_vetoes"] = vetoed
    if rec and (rec.get("inferred") or rec.get("open_point")):
        _storeys(build, rec, texts_by_level, party_by_level, drawn_by_level, side_by_level)
    wells = _light_wells(build, texts_by_level)
    if wells:
        b["level_inference"]["light_wells"] = wells
    _mark_party(b, party_by_level)
    refused = party_openings(b) if RG.active("party_refuse", b) else []
    if refused:
        b["level_inference"]["party_refused"] = refused
        build.warn(f"party walls: {len(refused)} derived or inferred opening(s) on a party wall refused "
                   f"({', '.join(x['opening'] for x in refused[:6])})")
    dropped = party_balconies(b, party_by_level)
    if dropped:
        b["level_inference"]["party_balconies"] = dropped
        build.warn(f"party walls: {len(dropped)} balcony(ies) on an attached side left out "
                   f"({', '.join(d['id'] for d in dropped)}): {dropped[0]['reason']}")
    # 12 Nov 2026 (the architect's audit): the common core (a missed stair, lift doors, flat-core gaps) and entrances
    from wenart.ingest import core_rules as CR
    for lid in list(texts_by_level):
        lv = next((x for x in b.get("levels") or [] if x["id"] == lid), None)
        for copy in [x for x in b.get("levels") or [] if lv is not None and x.get("typical_of") == lid]:
            # a copy of a typical floor reads its floor's texts and strokes (the same plan)
            texts_by_level.setdefault(copy["id"], texts_by_level[lid])
            if lid in strokes_by_level:
                strokes_by_level.setdefault(copy["id"], strokes_by_level[lid])
            if lid in drawn_by_level:
                drawn_by_level.setdefault(copy["id"], drawn_by_level[lid])
    rules = CR.apply(build, texts_by_level, party_by_level, strokes_by_level, drawn_by_level)
    b["level_inference"]["core_rules"] = rules
    gf = (b["level_inference"].get("storeys") or {}).get("ground_floor")
    if isinstance(gf, dict):
        ent = rules["entrances"]
        gf["entrance"] = ({"door": ent["added"][0]["door"], "reason": ent["added"][0]["reason"]} if ent["added"] else
                          {"door": None, "open": True, "reason": ent["open"]} if ent["open"] else gf.get("entrance"))
    # 12 Nov 2026 (stage 2): exterior per stretch (R14) before the windows, then the facades (R45, R24) and the
    # internal party walls (R46)
    # (staged: off until their review, rule keys exterior_spans, facade_ground, party_internal; 13 Nov 2026)
    from wenart.ingest import exterior as EX
    if RG.active("exterior_spans", b):
        b["level_inference"]["exterior"] = EX.apply(build, texts_by_level)
    if RG.active("facade_ground", b):
        b["level_inference"]["facades"] = _facades(b, texts_by_level, side_by_level, party_by_level)
    internal = FC.internal_party(b) if RG.active("party_internal", b) else []
    if internal:
        walls = {w["id"]: w for w in b.get("walls") or []}
        for x in internal:
            for wid in x["walls"]:
                if wid in walls and not RG.blocked("party_wall", b, {"level_id": walls[wid]["level_id"], "wall": wid,
                                                                     "why": "internal"}):
                    walls[wid]["party_wall"] = {"inferred": True, "internal": True, "reason": x["reason"]}
        b["level_inference"]["internal_party_walls"] = internal
        build.warn(f"party walls: {len(internal)} internal party wall(s): {internal[0]['reason']}")
    _windows(build, sheets, texts_by_level, region_by_level, party_by_level)
    copies = copy_doors(b)
    if copies:
        b["level_inference"]["copy_doors"] = copies
        made = [x for x in copies if x.get("action") != "kept"]
        if made:
            build.warn(f"storeys: {len(made)} door(s) of the copied storeys open onto nothing there: windows, or "
                       f"removed where the outside lies on both sides ({', '.join(x['opening'] for x in made[:6])}; "
                       f"adjusted_by_ai)")
    core = core_record(b, texts_by_level)
    if core:
        b["level_inference"]["core"] = core
    # 12 Nov 2026 (the architect's audit, second series): shafts, stairs over nothing, balcony doors, exterior flags
    from wenart.ingest import sense_rules as SR
    b["level_inference"]["sense_rules"] = SR.apply(build, texts_by_level, drawn_by_level)


LIGHT_WELL_NAMES = {"aydinlik": "Aydınlık", "isiklik": "Işıklık"}
LIGHT_WELL_MAX_M2 = 40.0        # a face larger than this holding the word is no light well (a courtyard, a room)


def light_well_word(room: dict, texts: Optional[list]) -> Optional[dict]:
    """``{"text", "entity"}`` of the light-well word a room's label is or holds inside it (pure), else None."""
    for key in ("label_raw", "label"):
        if LIGHT_WELL_RE.search(_fold(room.get(key))):
            return {"text": str(room.get(key)), "entity": None}
    p = _poly(room.get("polygon"))
    if p is None or not texts:
        return None
    for t in texts:
        if LIGHT_WELL_RE.search(_fold(t["text"])) and p.buffer(0.05).contains(Point(t["x"], t["y"])):
            return {"text": str(t["text"]).strip(), "entity": t.get("entity")}
    return None


def _flat_roof(b: dict, top: dict, reason: str) -> dict:
    return {"type": "flat", "type_source": "assumed", "over_level_id": top["id"], "outline": None,
            "planes": [], "openings": [], "inferred": True, "note": reason, "status": "assumed",
            "assumed": ["no roof evidence: a flat roof over the top storey (height, outline and thickness assumed)"],
            "evidence": [{"file": _ev_file(b, top["id"]), "method": "inferred", "confidence": 0.3,
                          "rule": "inferred_roof", "text": reason}]}


def _light_wells(build, texts_by_level: dict) -> dict:
    """A face labelled or holding a light-well word (``LIGHT_WELL_RE``: AYDINLIK, IŞIKLIK, light well, air shaft ...)
    that no door reaches is an open-air void, whatever room the reading made of it: ``room_type`` shaft,
    ``room_subtype`` light_well, labelled by its word (``adjusted_by_ai`` by code, the old type and label kept). It is
    open to the sky through every storey: an opening of kind void in the floor slab of every storey above the ground
    floor where the storey below has the well too, and an opening of kind light_well in the roof over the top storey's
    well. Returns the record (``level_inference.light_wells``); {} without light wells."""
    from wenart.ingest import rule_guards as RG

    b = build.building
    by_level: dict = {}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        texts = texts_by_level.get(lid) or []
        doors = [o for o in b.get("openings") or [] if o.get("level_id") == lid and o.get("type") == "door"
                 and o.get("center")]
        for r in b.get("rooms") or []:
            if r.get("level_id") != lid:
                continue
            p = _poly(r.get("polygon"))
            word = light_well_word(r, texts) if p is not None and p.area <= LIGHT_WELL_MAX_M2 else None
            if word is None or any(p.distance(Point(o["center"][:2])) <= 0.25 for o in doors):
                continue
            if RG.blocked("light_well", b, {"level_id": lid, "room": r["id"], "why": word["text"]}):
                continue
            name = LIGHT_WELL_NAMES.get(_fold(word["text"]), str(word["text"]).strip().capitalize())
            if r.get("room_type") != "shaft" or r.get("room_subtype") != "light_well":
                reason = (f"'{word['text']}' labels an open-air void (a light well) that no door reaches: open to the sky "
                          f"through every storey, never furnished; read as '{r.get('label')}' ({r.get('room_type')})")
                r["adjusted_by_ai"] = {"by": "code", "rule": "light_well", "reason": reason,
                                       "changed": {"room_type": r.get("room_type"), "label": r.get("label"),
                                                   "room_subtype": r.get("room_subtype")},
                                       "evidence": {"text": word["text"], "entity": word.get("entity")}}
                r.update(room_type="shaft", room_subtype="light_well", label=name)
            by_level.setdefault(lid, []).append(r)
    if not by_level:
        return {}
    rec = {"rooms": {lid: [r["id"] for r in rs] for lid, rs in by_level.items()}, "slab_voids": [], "roof_openings": []}
    for s in b.get("slabs") or []:
        above, below = s.get("above_level_id"), s.get("below_level_id")
        if not above or not below or above not in by_level or below not in by_level:
            continue
        under = [_poly(r["polygon"]) for r in by_level[below]]
        for r in by_level[above]:
            p = _poly(r["polygon"])
            if not any(q is not None and q.intersection(p).area >= 0.5 * p.area for q in under):
                continue
            oid = f"so_{above}_lw_{len(s.setdefault('openings', [])) + 1:02d}"
            s["openings"].append({"id": oid, "kind": "void", "room_id": r["id"], "furniture_id": None,
                                  "polygon": [[round(float(x), 4), round(float(y), 4)] for x, y in r["polygon"]],
                                  "source": "derived",
                                  "reason": f"the light well {r['id']} '{r.get('label')}' runs through {below} and "
                                            f"{above}: no floor slab inside it (inferred)", "entity": None})
            rec["slab_voids"].append(oid)
    base = [lv for lv in b.get("levels") or [] if not lv.get("base_level_id")]
    top = max(base, key=lambda lv: lv.get("order") or 0) if base else None
    if top is not None and top["id"] in by_level:
        if b.get("roof") is None:
            b["roof"] = _flat_roof(b, top, f"no roof is drawn: a flat roof over the top storey {top['id']}, open over "
                                           f"its light wells (inferred)")
        roof = b["roof"]
        if roof.get("over_level_id") in (None, top["id"]):
            for r in by_level[top["id"]]:
                oid = f"ro_lw_{len(roof.setdefault('openings', [])) + 1:03d}"
                roof["openings"].append({"id": oid, "kind": "light_well", "room_id": r["id"],
                                         "polygon": [[round(float(x), 4), round(float(y), 4)] for x, y in r["polygon"]],
                                         "parapet_height": None, "parapet_wall_ids": [], "source": "derived"})
                rec["roof_openings"].append(oid)
    n = sum(len(v) for v in by_level.values())
    build.warn(f"light wells: {n} face(s) labelled as light wells are open-air voids through the storeys "
               f"({', '.join(f'{k} {len(v)}' for k, v in sorted(by_level.items()))}); {len(rec['slab_voids'])} slab "
               f"void(s), {len(rec['roof_openings'])} roof opening(s) (inferred)")
    return rec


def _on_side(w: dict, side) -> bool:
    """True when wall ``w`` lies along the outline side ``side`` (parallel, its outer face on the side's line, within
    the side's extent; pure)."""
    a, u, length = _axis(w)
    (ex0, ey0), (ex1, ey1) = side
    el = math.hypot(ex1 - ex0, ey1 - ey0)
    if length < 0.3 or el < 1e-6:
        return False
    eu = ((ex1 - ex0) / el, (ey1 - ey0) / el)
    if abs(u[0] * eu[1] - u[1] * eu[0]) > PARALLEL_SIN:
        return False
    off = (a[0] - ex0) * -eu[1] + (a[1] - ey0) * eu[0]
    if abs(abs(off) - float(w.get("thickness") or 0.15) / 2.0) > PARTY_FACE_TOL_M and abs(off) > PARTY_FACE_TOL_M:
        return False
    ts = sorted(((p[0] - ex0) * eu[0] + (p[1] - ey0) * eu[1]) for p in (w["start"], w["end"]))
    return ts[1] > 0.1 and ts[0] < el - 0.1


PARTY_BUILT_SHARE = 0.8         # a party side's walls cover at least this share of it (R46: a side fully built)


def _built_share(walls: list, side, lid: str) -> float:
    """The share of an outline side its level's walls along it cover (pure)."""
    (ex0, ey0), (ex1, ey1) = side
    el = math.hypot(ex1 - ex0, ey1 - ey0)
    if el < 1e-6:
        return 1.0
    eu = ((ex1 - ex0) / el, (ey1 - ey0) / el)
    ivals = sorted(tuple(sorted(max(0.0, min(el, (p[0] - ex0) * eu[0] + (p[1] - ey0) * eu[1]))
                                for p in (w["start"], w["end"])))
                   for w in walls if w.get("level_id") == lid and _on_side(w, side))
    covered, t = 0.0, 0.0
    for a, c in ivals:
        a = max(a, t)
        if c > a:
            covered += c - a
            t = c
    return covered / el


def party_vetoes(b: dict, party_by_level: dict) -> list:
    """R46's vetoes (in place on ``party_by_level``; the records returned): no party wall on a level read with low
    confidence, and none on a side that carries a drawn door, entrance or window on any storey (a drawn opening shows
    the side is free; inferred and derived openings do not count)."""
    from wenart.ingest import core_rules as CR
    from wenart.ingest import rule_guards as RG

    out = []
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    for lid in list(party_by_level):
        lv = levels.get(lid) or {}
        # a copy of a typical floor is read as its floor (a storey counted by a guess is still that floor's plan)
        base = levels.get(lv.get("typical_of")) if lv.get("typical_of") else None
        if (base or lv).get("reading_confidence") == "low":
            out.append({"level_id": lid, "walls": sorted(party_by_level.pop(lid)),
                        "reason": f"{lid} is read with low confidence: no party wall is marked on it"})
    walls = [w for w in b.get("walls") or [] if w.get("start") and w.get("end")]
    drawn = {}
    for o in b.get("openings") or []:
        if o.get("type") in ("door", "window") and not o.get("virtual") and not CR.derived(o):
            drawn.setdefault(o.get("wall_id"), []).append(o)
    for lid, party in list(party_by_level.items()):
        sides = {}
        for wid, ev in party.items():
            sides.setdefault(tuple(map(tuple, ev.get("side") or [])), []).append(wid)
        for side, wids in sides.items():
            if len(side) != 2:
                continue
            short = _built_share(walls, side, lid) if RG.active("party_guards", b) else 1.0
            if short < PARTY_BUILT_SHARE:
                for wid in wids:
                    party.pop(wid, None)
                out.append({"level_id": lid, "walls": sorted(wids),
                            "reason": f"the reading built only {short * 100:.0f} % of the side: a side not fully built "
                                      f"is no party wall (R46)"})
                continue
            hit = [o for w in walls if _on_side(w, side) for o in drawn.get(w["id"]) or []]
            if hit:
                for wid in wids:
                    party.pop(wid, None)
                out.append({"level_id": lid, "walls": sorted(wids),
                            "reason": f"the side holds the drawn {hit[0]['type']} {hit[0]['id']} on "
                                      f"{hit[0].get('level_id')}: a facade with a drawn opening is no party wall"})
        if not party:
            party_by_level.pop(lid)
    return out


def _mark_party(b: dict, party_by_level: dict) -> None:
    """Every party wall carries ``party_wall`` (the text and the side that name it): no window, no balcony, never a
    facade view (pure, in place)."""
    walls = {w["id"]: w for w in b.get("walls") or []}
    for lid, party in party_by_level.items():
        for wid, ev in party.items():
            if wid in walls:
                walls[wid]["party_wall"] = {"inferred": True, "text": ev.get("text"), "entity": ev.get("entity"),
                                            "reason": f"'{ev.get('text')}' on this side: the neighbour's building is "
                                                      f"attached here (a blank party wall: no window, no balcony)"}


def party_openings(b: dict) -> list:
    """R46: a derived or inferred opening on an external party wall is refused (removed, the record returned); a drawn
    one stays (RC14 party_wall_openings asks about it)."""
    from wenart.ingest import core_rules as CR
    from wenart.ingest import rule_guards as RG

    party = {w["id"] for w in b.get("walls") or [] if isinstance(w.get("party_wall"), dict)
             and not w["party_wall"].get("internal")}
    walls = {w["id"]: w for w in b.get("walls") or [] if w.get("start") and w.get("end")}
    crossing = RG.active("party_guards", b)
    out, keep = [], []
    for o in b.get("openings") or []:
        across = _crosses_party(o, walls, party) if crossing and o.get("wall_id") not in party else None
        if (o.get("wall_id") in party or across) and not o.get("virtual") and CR.derived(o) and not RG.blocked(
                "party_wall", b, {"level_id": o.get("level_id"), "opening": o["id"], "why": "opening on a party wall"}):
            where = f"stands on the party wall {o['wall_id']}" if not across else \
                f"reaches across the party line of {across}"
            out.append({"opening": o["id"], "level_id": o.get("level_id"), "wall": o["wall_id"],
                        "reason": f"{o['id']} ({o.get('type')}, derived or inferred) {where}: refused (R46)"})
            continue
        keep.append(o)
    if out:
        b["openings"] = keep
    return out


def _crosses_party(o: dict, walls: dict, party: set) -> Optional[str]:
    """The party wall whose line an opening's span reaches across (its end within the party wall's half thickness of
    that wall's axis, on a wall of the same level that meets it), or None (pure; R46's crossing-span check)."""
    w = walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return None
    a, u, _l = _axis(w)
    half = float(o.get("width") or 0.0) / 2.0
    c = o["center"]
    ends = [(c[0] + u[0] * s * half, c[1] + u[1] * s * half) for s in (-1, 1)]
    for pid in party:
        pw = walls.get(pid)
        if pw is None or pw.get("level_id") != o.get("level_id"):
            continue
        pa, pu, pl = _axis(pw)
        if abs(u[0] * pu[1] - u[1] * pu[0]) < 0.5:
            continue                                    # parallel to it: not across its line
        reach = float(pw.get("thickness") or 0.15) / 2.0
        line = LineString([pw["start"], pw["end"]])
        if any(line.distance(Point(e)) <= reach for e in ends):
            return pid
    return None


BALCONY_TOUCH_M = 0.30          # a balcony this close to a wall's outer face leans on it


def _clip_at_party(p: Polygon, party_walls: list, inside) -> Optional[Polygon]:
    """``p`` without what lies beyond the outer face line of each party wall (on the side away from ``inside``, a point
    of the building's rooms: the half-plane the neighbour stands in), or None when nothing is cut (pure)."""
    out, cut = p, False
    for w in party_walls:
        a, u, length = _axis(w)
        if length < 1.0:
            continue
        n = (-u[1], u[0])
        # the neighbour's side: away from the building's rooms, from the wall's outer face on
        side = 1.0 if (inside[0] - a[0]) * n[0] + (inside[1] - a[1]) * n[1] < 0 else -1.0
        off = float(w.get("thickness") or 0.15) / 2.0
        big = 1000.0
        o0 = (a[0] + side * n[0] * off, a[1] + side * n[1] * off)
        far = [(o0[0] - u[0] * big, o0[1] - u[1] * big), (o0[0] + u[0] * big, o0[1] + u[1] * big)]
        half = Polygon([far[0], far[1], (far[1][0] + side * n[0] * big, far[1][1] + side * n[1] * big),
                        (far[0][0] + side * n[0] * big, far[0][1] + side * n[1] * big)])
        if out.intersects(half) and out.intersection(half).area > 0.05:
            rest = out.difference(half)
            if rest.is_empty:
                continue
            out = max(rest.geoms, key=lambda g: g.area) if rest.geom_type == "MultiPolygon" else rest
            cut = True
    return out if cut else None


def party_balconies(b: dict, party_by_level: dict) -> list:
    """The balconies (outdoor spaces of kind balcony) that lean only on party walls: removed (in place) and returned
    with the reason. A balcony on a facade that ends at the party line leans on that facade too and stays."""
    from wenart.ingest import rule_guards as RG
    from wenart.reading_check.crossdoc import wall_polygon

    site = b.get("site") or {}
    keep, out = [], []
    walls = {w["id"]: w for w in b.get("walls") or []}
    for s in site.get("outdoor_spaces") or []:
        party = party_by_level.get(s.get("level_id")) or {}
        p = _poly(s.get("polygon"))
        if not party or p is None or str(s.get("kind")) != "balcony" or RG.blocked(
                "party_balcony", b, {"level_id": s.get("level_id"), "space": s.get("id")}):
            keep.append(s)
            continue
        touching = []
        for w in walls.values():
            wp = wall_polygon(w) if w.get("level_id") == s.get("level_id") else None
            if wp is not None and p.exterior.intersection(wp.buffer(BALCONY_TOUCH_M)).length >= 0.5:
                touching.append(w)
        if touching and all(w["id"] in party for w in touching):
            out.append({"id": s["id"], "level_id": s.get("level_id"), "walls": sorted(w["id"] for w in touching),
                        "reason": f"it leans only on the party wall(s) {', '.join(sorted(w['id'] for w in touching))} "
                                  f"('{party[touching[0]['id']].get('text')}': the neighbour's building is attached "
                                  f"there): no balcony on a party wall (inferred)"})
            continue
        # a balcony on a facade never runs past the attached side: the part beyond a party wall's line is cut off
        own = [r for r in b.get("rooms") or [] if r.get("level_id") == s.get("level_id") and _poly(r.get("polygon"))]
        inside = unary_union([_poly(r["polygon"]) for r in own]).centroid.coords[0] if own else None
        clipped = _clip_at_party(p, [walls[i] for i in party if i in walls and walls[i].get("level_id") ==
                                     s.get("level_id")], inside) if inside is not None else None
        if clipped is not None and clipped.area < p.area - 0.05:
            s["drawn_polygon"] = s.get("polygon")
            s["polygon"] = [[round(x, 4), round(y, 4)] for x, y in list(clipped.exterior.coords)[:-1]]
            s["area_m2"] = round(clipped.area, 3)
            s["adjusted_by_ai"] = {"by": "code", "rule": "balcony_party_line",
                                   "reason": f"the balcony ran {p.area - clipped.area:.2f} m2 past the attached side "
                                             f"(a party wall's line): cut there"}
            out.append({"id": s["id"], "level_id": s.get("level_id"), "clipped_m2": round(p.area - clipped.area, 3),
                        "reason": s["adjusted_by_ai"]["reason"] + " (inferred)"})
        keep.append(s)
    if out:
        site["outdoor_spaces"] = keep
    return out


def outer_doors(building: dict, lid: str) -> list:
    """The doors of a level that open from a room to the outside (the far side outside the level's outline, not a
    balcony) (pure): the building's ways in at that storey."""
    level = Level(building, lid)
    if level.outline is None:
        return []
    out = []
    for o in level.openings:
        w = level.walls.get(o.get("wall_id"))
        if o.get("type") != "door" or w is None or not o.get("center") or o.get("entrance_refused"):
            continue                # a door refused as an entrance (a lost room behind it) is no way in (S1-20c)
        a, u, _ = _axis(w)
        n = (-u[1], u[0])
        reach = float(w.get("thickness") or 0.15) / 2.0 + PROBE_M
        c = o["center"]
        sides = [level.kind_at((c[0] + k * n[0] * reach, c[1] + k * n[1] * reach), "") for k in (1, -1)]
        if "outside" in sides and ("room" in sides or "light_well" in sides):
            out.append(o["id"])
    return out


def copy_doors(b: dict) -> list:
    """The doors of a copied storey (a storey counted, not drawn: ``typical_of`` and ``storey_inference``, above the
    ground floor, not at the ground) that open onto nothing there (review POD-02: a copy is never a door into the air;
    rule key ``copy_door_window``):

    - a door from a room to the true outside (no balcony, no terrace, no room label the reading lost beyond it)
      becomes a window of the same width with its head at the door's (``adjusted_by_ai``, ``drawn_type`` door);
    - a door with the outside on both sides (a door in a wall piece standing in the air, or off its wall) is removed
      from the copy; its wall is flagged ``facade_remnant`` for review (13 Nov 2026, review S1F-POD-P02);
    - a door from a room onto a room label the reading lost stays the drawn door: the room exists in the drawing (13 Nov 2026,
      review S1F-POD-R01, FC-05: real20's right flat lost its front door, a bedroom's and a bathroom's on 4 storeys);
      one ``needs_review`` item per copy names the doors and the lost labels;
    - never the building's entrance: a copied storey within ``ENTRANCE_LEVEL_M`` of a ground height is skipped, and so
      is a door the entrance rule inferred or a main entrance record names (review CODE-02).

    Returns the records (pure but for the openings, the walls' flags and ``needs_review``)."""
    from wenart.ingest import core_rules as CR
    from wenart.ingest import rule_guards as RG

    out = []
    ground = CR.ground_zs(b)
    entrance_doors = {e.get("door_id") for e in (b.get("site") or {}).get("entrances") or [] if e.get("main")}
    for lv in b.get("levels") or []:
        if not lv.get("typical_of") or not lv.get("storey_inference") or (lv.get("order") or 0) <= 0:
            continue
        if isinstance(lv.get("elevation"), (int, float)) and \
                any(abs(float(lv["elevation"]) - g) <= CR.ENTRANCE_LEVEL_M for g in ground):
            continue                          # a storey at the ground: its doors are no doors into the air
        level = Level(b, lv["id"])
        if level.outline is None:
            continue
        lost = [p for p in lv.get("reading_places") or [] if p.get("kind") == "unplaced_label" and p.get("at")]
        kept, drop = [], set()
        for o in level.openings:
            if o.get("type") != "door" or o.get("virtual") or o.get("lift_door") or o["id"] in entrance_doors or \
                    (o.get("inference") or {}).get("rule") == "inferred_entrance":
                continue
            sides = CR._sides(level, o)
            kinds = [s[0] for s in sides]
            if "outside" not in kinds:
                continue
            q = next(s[2] for s in sides if s[0] == "outside")
            near = sorted(((math.dist(q, p["at"][:2]), k, p) for k, p in enumerate(lost)
                           if math.dist(q, p["at"][:2]) <= CR.LABEL_REACH_M + 1.0), key=lambda x: x[:2])
            both_outside = all(k == "outside" for k in kinds)
            if near and not both_outside:
                kept.append((o, near[0][2]))
                out.append({"opening": o["id"], "level_id": lv["id"], "action": "kept",
                            "reason": f"{o['id']} on {lv['id']} opens onto the room label '{near[0][2].get('text')}' "
                                      f"the reading lost: the drawn door stays (the room exists in the drawing)"})
                continue
            if not both_outside and not any(s[1] is not None for s in sides):
                continue                      # a door onto a balcony or a terrace
            what = ("the outside on both sides (a wall piece standing in the air"
                    + (f"; the reading lost the room label '{near[0][2].get('text')}' beside it" if near else "") + ")"
                    if both_outside else "the outside (no balcony or terrace on this storey)")
            if RG.blocked("copy_door_window", b, {"level_id": lv["id"], "opening": o["id"], "why": what}):
                continue
            head = float(o.get("height") or 2.1)
            if both_outside:
                reason = (f"{o['id']} on {lv['id']}, a storey copied from {lv['typical_of']} (counted, not drawn), has "
                          f"{what}: removed from the copy; its wall {o.get('wall_id')} is a facade remnant to review")
                drop.add(o["id"])
                w = level.walls.get(o.get("wall_id"))
                if w is not None:
                    w["facade_remnant"] = {"by": "code", "rule": "copy_door_window", "reason": reason}
                out.append({"opening": o["id"], "level_id": lv["id"], "action": "removed",
                            "reason": reason + " (adjusted_by_ai)"})
                continue
            sill = 0.9
            reason = (f"{o['id']} on {lv['id']}, a storey copied from {lv['typical_of']} (counted, not drawn), opens "
                      f"onto {what}: a window of its width there" + ("" if CR.derived(o) else " (the drawn door kept)"))
            o.update(drawn_type="door", type="window", sill_height=sill, height=round(max(0.6, head - sill), 3),
                     operation=None, operation_source=None, swing_side=None,
                     adjusted_by_ai={"by": "code", "rule": "copy_door_window", "reason": reason,
                                     "changed": {"type": "door", "height": head}})
            out.append({"opening": o["id"], "level_id": lv["id"], "action": "window",
                        "reason": reason + " (adjusted_by_ai)"})
        if drop:
            CR._to_merged(b, [o for o in b["openings"] if o["id"] in drop], "copy_door_window",
                          {x["opening"]: x["reason"] for x in out if x.get("action") == "removed"})
            b["openings"] = [o for o in b["openings"] if o["id"] not in drop]
        if kept:
            labels = sorted({str(p.get("text")) for _o, p in kept})
            b.setdefault("needs_review", []).append({
                "id": f"copy_doors:{lv['id']}", "kind": "copy_door_lost_room", "crop": None, "room_id": None,
                "level_id": lv["id"],
                "reason": f"{lv['id']} (copied from {lv['typical_of']}): {len(kept)} drawn door(s) open onto room "
                          f"label(s) the reading lost ({', '.join(labels)}): the doors stay "
                          f"({', '.join(o['id'] for o, _p in kept[:8])}); the rooms are to recover"})
    gone = {x["opening"] for x in out if x.get("action") in ("window", "removed")}
    if gone and isinstance(b.get("site"), dict) and b["site"].get("entrances"):
        b["site"]["entrances"] = [e for e in b["site"]["entrances"] if e.get("door_id") not in gone]
    return out


ROOF_ACCESS_RE = re.compile(r"(?<![a-z])(?:catiya\s+cikis|cati\s+cikisi|cati\s+kapagi|cati\s+kapak|roof\s+hatch|"
                            r"roof\s+access|dachluke|trappe\s+de\s+toit)")
PITCHED = ("hip", "gable", "shed", "mansard", "gambrel", "pitched", "gable_hip", "butterfly", "saltbox", "dome")


def core_record(b: dict, texts_by_level: Optional[dict] = None) -> dict:
    """The building's core (pure): the lifts and stairs per storey of the base variant, whether each lift continues
    through every storey, and what the core needs on the roof (R18; review REG-08, S1-all-a): a stair head only over
    a flat roof that is used (a roof terrace or an open space on the top storey) or over a stair that rises from the
    top storey (not the arrival of the flight below, not a copy of the storey below's stair); never under a pitched
    roof or over an attic; a roof-access text on the top plan (çatıya çıkış, çatı kapağı) is a ceiling hatch; a lift
    overrun over every lift shaft there (inferred; ``built`` False: the builder has no stair head or overrun yet)."""
    storeys = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                     key=lambda lv: (lv.get("order") or 0, lv["id"]))
    if len(storeys) < 2:
        return {}
    lifts, stairs = {}, {}
    for lv in storeys:
        lid = lv["id"]
        lifts[lid] = [r["id"] for r in b.get("rooms") or [] if r.get("level_id") == lid and is_lift(r)]
        stairs[lid] = ([f["id"] for f in b.get("furniture") or [] if f.get("level_id") == lid and f.get("type") == "stair"]
                       + [r["id"] for r in b.get("rooms") or [] if r.get("level_id") == lid
                          and r.get("room_type") == "stair"])
    if not any(lifts.values()) and not any(stairs.values()):
        return {}
    top_lv = storeys[-1]
    top, below = top_lv["id"], storeys[-2]["id"]
    rec = {"lifts": lifts, "stairs": stairs,
           "lifts_through": all(len(lifts[lv["id"]]) == len(lifts[storeys[0]["id"]]) for lv in storeys),
           "stair_head": None, "lift_overrun": None}
    roof = b.get("roof") if isinstance(b.get("roof"), dict) else {}
    rtype = str(roof.get("type") or "")
    pitched = rtype in PITCHED or (rtype not in ("", "flat") and rtype != "flat_cut")
    below_fps = [f["footprint"] for f in b.get("furniture") or [] if f.get("level_id") == below
                 and f.get("type") == "stair" and f.get("footprint")]

    def rising(f):
        """A stair on the top storey that rises from it: built upward, not the copy of the storey below's."""
        if f.get("build") is False or f.get("rule") == "stair_upper_plan" or top_lv.get("typical_of"):
            return False
        fp = f.get("footprint") or {}
        if not fp.get("center"):
            return False
        return not any(math.dist(fp["center"][:2], g["center"][:2]) <= 0.5 for g in below_fps)
    top_stairs = [f for f in b.get("furniture") or [] if f.get("level_id") == top and f.get("type") == "stair"]
    up = [f["id"] for f in top_stairs if rising(f)]
    used = [r["id"] for r in b.get("rooms") or [] if r.get("level_id") == top
            and str(r.get("room_type") or "") in ("roof_terrace", "terrace")] + \
        [s["id"] for s in (b.get("site") or {}).get("outdoor_spaces") or []
         if s.get("level_id") == top and str(s.get("kind") or "") in ("roof_terrace", "terrace")]
    hatch = next((t for t in (texts_by_level or {}).get(top) or [] if ROOF_ACCESS_RE.search(_fold(t.get("text")))),
                 None)
    if hatch is not None:
        rec["roof_access"] = {"kind": "ceiling_hatch_ladder", "inferred": True, "level_id": top,
                              "evidence": {"text": hatch.get("text"), "entity": hatch.get("entity"),
                                           "at": [round(hatch["x"], 2), round(hatch["y"], 2)]},
                              "reason": f"'{hatch.get('text')}' on the top plan: the roof is reached by a ceiling hatch "
                                        f"(inferred)"}
    if not stairs.get(top) and not used:
        why = (f"no stair is read on the top storey {top}: the stair head cannot be placed" if any(stairs.values()) else
               "no stair is read on any storey: the core stair and its stair head are missing")
        rec["stair_head"] = {"needed": None, "built": False, "over": [], "reason": why}
    elif pitched or top_lv.get("kind") == "attic":
        what = f"a pitched roof ({rtype}, from {roof.get('type_source') or 'the reading'})" if pitched else "an attic"
        rec["stair_head"] = {"needed": False, "built": False, "over": [],
                             "reason": f"the top storey's stair is the arrival under {what}: no stair head (R18)"}
    elif hatch is not None:
        rec["stair_head"] = {"needed": False, "built": False, "over": [],
                             "reason": "the roof is reached by a ceiling hatch (the top plan says so): no stair head"}
    elif up or used:
        rec["stair_head"] = {"needed": True, "built": False, "over": up or stairs.get(top) or [],
                             "reason": (f"the stair {', '.join(up)} rises from the top storey {top}" if up else
                                        f"the flat roof is used ({', '.join(used)} on {top})")
                             + ": a stair head over it gives the roof its access (inferred; the builder does not build "
                               "a stair head yet)"}
    else:
        rec["stair_head"] = {"needed": False, "built": False, "over": [],
                             "reason": f"the stair on the top storey {top} is the arrival of the flight below and the "
                                       f"roof is not used: no stair head (R18; a roof terrace or a stair drawn rising "
                                       f"would need one)"}
    if lifts.get(top):
        rec["lift_overrun"] = {"needed": True, "built": False, "over": lifts[top],
                               "reason": f"{len(lifts[top])} lift shaft(s) reach the top storey {top}: each has an "
                                         f"overrun over the roof (inferred; the builder does not build it yet)"}
    return rec



def _ev_file(b: dict, lid: str) -> str:
    lv = next((x for x in b.get("levels") or [] if x["id"] == lid), {})
    return next((e.get("file") for e in lv.get("evidence") or [] if e.get("file")), "") or ""


def _storeys(build, rec: dict, texts_by_level: dict, party_by_level: dict, drawn_by_level: Optional[dict] = None,
             side_by_level: Optional[dict] = None) -> None:
    from wenart.ingest import rule_guards as RG

    b = build.building
    out = {k: v for k, v in rec.items() if k != "ladder"}
    out["ladder"] = [{k: v for k, v in r.items() if k != "evidence"} | {"evidence": (r.get("evidence") or [])[:3]}
                     for r in rec.get("ladder") or []]
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    for item in rec.get("inferred") or []:
        lv = levels.get(item["level_id"])
        if lv is None:
            item["built"] = False
            continue
        item["built"] = True
        lv["storey_inference"] = {"inferred": True, "rule": item["rule"], "confidence": item["confidence"],
                                  "guess": item["guess"], "reason": item["reason"]}
        if item.get("guess") and (lv.get("order") or 0) > 0:
            # the coordinator's decision of 12 Nov 2026: a storey only a guess (the type default) counts is inferred
            # with low reading confidence until a document or the user gives the count (the architect's N1)
            lv["reading_confidence"] = "low"
            lv["reading_review"] = list(lv.get("reading_review") or []) + [
                f"storey counted by a guess ({item['rule']}): no document gives the storey count"]
    built = [i["level_id"] for i in rec.get("inferred") or [] if i.get("built")]
    if built:
        build.warn(f"storeys: {len(built)} storey(s) the documents do not draw inferred ({', '.join(built)}; "
                   f"{rec.get('rule')}, confidence {rec.get('confidence')}" + (", a guess" if rec.get("guess") else "")
                   + ")")
    ground = levels.get("L0") if rec.get("ground_from_typical") else None
    if ground is not None and "L0" in built:
        out["ground_floor"] = _ground_floor(build, ground, rec, texts_by_level.get("L0"), party_by_level.get("L0") or {},
                                            (drawn_by_level or {}).get("L0"), (side_by_level or {}).get("L0"))
    rebased = _rebase_roof(build, b, set(built))
    if rebased:
        out["roof_rebased"] = rebased
    eaves = _plan_roof_eaves(build, b, set(built))       # 20 Nov 2026 (R13 guard, review BP-03)
    if eaves:
        out["roof_eaves_assumed"] = eaves
    if b.get("roof") is None and built and not RG.blocked("storey_roof", b, {"level_id": built[-1],
                                                                            "why": "storeys added: a flat roof"}):
        top = max((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: lv.get("order") or 0)
        reason = (f"no roof is drawn and the storeys above the drawn plan are inferred: a flat roof over the top "
                  f"storey {top['id']} ({top['label']}), outline, height and thickness assumed")
        b["roof"] = _flat_roof(b, top, reason)
        out["roof"] = reason
        build.warn(f"roof: {reason} (inferred)")
    b["level_inference"]["storeys"] = out


def _val(v) -> Optional[float]:
    if isinstance(v, dict):
        v = v.get("value")
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


STOREY_OFFSET_M = 3.0           # a section's eaves this far over the drawn top ceiling come from another datum (FC-09)
KNEE_M = 0.30                   # ... with no rise read, the eaves sit this far over the new top ceiling (assumed)
RISE_NOTE_RE = re.compile(r"(-?\d+(?:\.\d+)?) m above the top floor")


def _rise_above_top(v) -> Optional[float]:
    """The section's own rise of a roof height above its top floor (``wenart.sheets.heights``' note), or None."""
    m = RISE_NOTE_RE.search(str((v or {}).get("note") or "")) if isinstance(v, dict) else None
    return float(m.group(1)) if m else None


def _plan_roof_eaves(build, b: dict, built: set) -> Optional[str]:
    """20 Nov 2026 (R13 guard, review BP-03: real20's plan-lines roof with no height sat 0.7 m over the inferred top
    storey's floor and its windows cut through it): a roof read from the plan's lines with no eaves height over a storey
    the storey rule counted puts its eaves on that storey's ceiling, marked assumed with the reason, so a counted storey
    never becomes an attic. Returns the reason, or None."""
    roof = b.get("roof")
    if not isinstance(roof, dict) or roof.get("inferred") or not built or _val(roof.get("eaves_height")) is not None \
            or roof.get("type_source") != "plan_roof_lines":
        return None
    storeys = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                     key=lambda lv: (lv.get("order") or 0, lv["id"]))
    top = storeys[-1] if storeys else None
    if top is None or top["id"] not in built or not isinstance(top.get("elevation"), (int, float)):
        return None
    z = round(float(top["elevation"]) + float(top.get("ceiling_height") or 2.7), 3)
    reason = (f"the roof read from the top plan's lines gives no eaves height and stands over {top['id']}, a storey the "
              f"storey rule counted: its eaves on that storey's ceiling ({z:+.2f} m, assumed)")
    roof["eaves_height"] = {"value": z, "method": "assumed", "confidence": 0.0, "evidence": [], "note": reason}
    roof["over_level_id"] = top["id"]
    if isinstance(roof.get("assumed", []), list):
        roof.setdefault("assumed", []).append(reason)
    build.warn(f"roof: {reason}")
    return reason


def _rebase_roof(build, b: dict, built: set) -> Optional[str]:
    """A roof read from a section (absolute eaves and ridge) over storeys the storey rule added on top (review REG-05):
    when its eaves lie under the new top storey's ceiling, the roof keeps its drawn rise above the highest drawn storey
    and stands on the new top storey (heights, planes and profile shifted, marked assumed with the reason; a
    conflict). Returns the reason, or None."""
    roof = b.get("roof")
    if not isinstance(roof, dict) or roof.get("inferred") or not built:
        return None
    storeys = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                     key=lambda lv: (lv.get("order") or 0, lv["id"]))
    top = storeys[-1] if storeys else None
    drawn = [lv for lv in storeys if lv["id"] not in built]
    if top is None or top["id"] not in built or not drawn or roof.get("over_level_id") not in (None, drawn[-1]["id"]):
        return None
    old = drawn[-1]
    eaves = _val(roof.get("eaves_height"))
    if eaves is None or not isinstance(top.get("elevation"), (int, float)) or \
            not isinstance(old.get("elevation"), (int, float)):
        return None
    ceiling = float(top["elevation"]) + float(top.get("ceiling_height") or 2.7)
    if eaves >= ceiling - 0.05:
        return None
    dz = float(top["elevation"]) - float(old["elevation"])
    # 13 Nov 2026 (review FC-09: real16's section r9 has another datum; its eaves stood 7.9 m over the drawn top
    # ceiling and the shift carried that up): when the section's storey heights were rejected or its eaves stand more
    # than a storey over the drawn top ceiling, the roof keeps the section's own rise above its top floor (the eaves
    # note), else it sits on an assumed knee wall over the new top ceiling
    old_ceiling = float(old["elevation"]) + float(old.get("ceiling_height") or 2.7)
    rejected = any("the section's heights are no storeys" in str(w) for w in b.get("warnings") or [])
    datum = ""
    if rejected or eaves - old_ceiling > STOREY_OFFSET_M:
        rise = _rise_above_top(roof.get("eaves_height"))
        target = float(top["elevation"]) + rise if rise is not None else ceiling + KNEE_M
        dz = target - eaves
        why = "its storey heights were rejected" if rejected else \
            f"its eaves stood {eaves - old_ceiling:.2f} m over the drawn top ceiling"
        datum = (f"; the section's datum is not the plans' ({why}): "
                 + (f"the eaves keep the section's own rise of {rise:.2f} m above its top floor" if rise is not None
                    else f"the eaves sit on an assumed {KNEE_M:.2f} m knee wall over the top ceiling"))
    for key in ("eaves_height", "ridge_height"):
        v = roof.get(key)
        if isinstance(v, dict) and _val(v) is not None:
            roof[key] = dict(v, value=round(_val(v) + dz, 3))
        elif _val(v) is not None:
            roof[key] = round(_val(v) + dz, 3)
    for pl in roof.get("planes") or []:
        pl["points"] = [[p[0], p[1], round(float(p[2]) + dz, 4)] for p in pl.get("points") or []]
    prof = roof.get("profile")
    if isinstance(prof, dict) and prof.get("points"):
        prof["points"] = [[p[0], round(float(p[1]) + dz, 4)] for p in prof["points"]]
    reason = (f"the roof read from the section had its eaves at {eaves:+.2f} m, under the ceiling of the top storey "
              f"{top['id']} the storey rule added ({ceiling:+.2f} m): " +
              (f"it keeps its drawn rise above {old['id']} and stands {dz:.2f} m higher, on {top['id']} (assumed)"
               if not datum else f"it stands {dz:+.2f} m off, on {top['id']}{datum} (assumed)"))
    roof["over_level_id"] = top["id"]
    if isinstance(roof.get("assumed", []), list):
        roof.setdefault("assumed", []).append(reason)
    roof["rebased"] = {"dz": round(dz, 3), "from_level": old["id"], "to_level": top["id"], "reason": reason}
    if callable(getattr(build, "conflict", None)):
        build.conflict("other", [old["id"], top["id"]], reason, "the roof rebased on the top storey (assumed)")
    build.warn(f"roof: {reason}")
    return reason


def _ground_floor(build, ground: dict, rec: dict, texts: Optional[list], party: dict, drawn=None,
                  side: Optional[list] = None) -> dict:
    """The inferred ground floor read from the typical plan: no cantilevered balconies when the footprint is smaller
    than the typical floor; cut to the drawn footprint, with an entrance hall from the street into the core
    (``ground_floor.apply``, 13 Nov 2026). Its entrance otherwise comes from the general entrance rule
    (``core_rules.fix_entrances``), written into ``entrance`` by ``complete``."""
    from wenart.ingest import rule_guards as RG

    b = build.building
    lid = ground["id"]
    level = Level(b, lid, texts)
    done = {"dropped": [], "entrance": None}
    if rec.get("cantilevers") and level.outline is not None:
        site = b.get("site") or {}
        keep = []
        for s in site.get("outdoor_spaces") or []:
            p = _poly(s.get("polygon"))
            if s.get("level_id") == lid and str(s.get("kind")) == "balcony" and p is not None and \
                    p.difference(level.outline).area >= 0.5 * p.area and \
                    not RG.blocked("cantilever_drop", b, {"level_id": lid, "space": s["id"],
                                                          "why": rec["cantilevers"]["reason"]}):
                done["dropped"].append({"id": s["id"], "label": s.get("label"), "area_m2": s.get("area_m2"),
                                        "reason": rec["cantilevers"]["reason"]})
                continue
            keep.append(s)
        if done["dropped"]:
            site["outdoor_spaces"] = keep
            gone = {d["id"] for d in done["dropped"]}
            li = b.get("level_inference") or {}
            li["inferred"] = [i for i in li.get("inferred") or []
                              if not any(str(i.get("item", "")).endswith(g) for g in gone)]
            li["inferred"].append({"item": f"{lid} cantilevered balconies", "value": sorted(gone),
                                   "reason": rec["cantilevers"]["reason"] + " (inferred)"})
            dropped_polys = [_poly(s.get("polygon")) for s in (b.get("site") or {}).get("outdoor_spaces") or []]
            for a in site.get("areas") or []:
                anchor = a.get("anchor")
                sp = a.get("space")
                if a.get("level_id") == lid and isinstance(sp, dict) and sp.get("built") and anchor and \
                        any(g.startswith(str(sp.get("id"))) for g in gone) and \
                        not any(p is not None and p.buffer(0.05).contains(Point(anchor)) for p in dropped_polys):
                    a["space"] = dict(a["space"], built=False, reason=rec["cantilevers"]["reason"])
            build.warn(f"{lid}: {len(gone)} cantilevered balcony(ies) left out on the inferred ground floor "
                       f"({', '.join(sorted(gone))}): {rec['cantilevers']['reason']}")
    # 13 Nov 2026 (S1-21a, S1-20b, R10 (4), R43): the ground floor keeps to the drawn footprint and gets an entrance
    # hall from the street into the core (wenart/ingest/ground_floor.py)
    from wenart.ingest import ground_floor as GF
    done.update(GF.apply(build, ground, rec, texts, drawn, side))
    # without a drawn footprint the ground floor is the typical floor's outline: a conflict, never claimed handled
    cant = rec.get("cantilevers") or {}
    if cant and level.outline is not None and cant.get("ground_m2") and not done.get("footprint"):
        built = float(level.outline.area)
        if built > float(cant["ground_m2"]) * 1.05:
            text = (f"{lid}, the ground floor read from the typical plan, keeps the typical floor's outline "
                    f"({built:.0f} m2) though the footprint is {float(cant['ground_m2']):.0f} m2: no drawn footprint "
                    f"outline cuts it (the parts past the footprint stand on the ground; to review)")
            done["footprint_conflict"] = text
            if callable(getattr(build, "conflict", None)):
                build.conflict("other", [lid], text, "the typical outline kept; the footprint not drawn on the plan")
            b.setdefault("needs_review", []).append({"id": f"ground_floor:{lid}", "kind": "ground_floor_footprint",
                                                     "reason": text, "crop": None, "room_id": None, "level_id": lid})
    # the entrance at the core: the general entrance rule (core_rules.fix_entrances) after the core is complete
    return done


def window_decision(building: dict, level: dict, read: int, drawing: Optional[dict]) -> tuple[bool, str]:
    """``(infer, why)`` for one level (pure): windows are inferred only when the level reads none, its plan draws none
    (``drawing``: the sheets stage's ``windows_drawn``; None when the plan has no record: nothing is inferred, a reading
    miss is never covered) and it is not below ground (``below_ground``; user, 6 Nov 2026: "underground floors will
    have no window")."""
    if read:
        return False, f"{read} window(s) read: none inferred (a habitable room without one is a finding)"
    if drawing is None:
        return False, "no sheets record of the plan's windows: none inferred"
    if drawing.get("draws_windows"):
        return False, ("the plan draws windows that were not read: none inferred (a reading miss, never covered by "
                       "inference)")
    from wenart.ingest import exterior as EX
    from wenart.ingest import rule_guards as RG
    ok, why = EX.level_ok(building, level.get("id")) if RG.active("exterior_spans", building) else (True, [])
    if not ok:
        return False, f"the level does not qualify for inferred windows (R14: {'; '.join(why)})"
    rows = ((building.get("level_inference") or {}).get("facades") or {}).get(level.get("id"))
    under = below_ground(building, level)
    if rows is not None and rows and all(r.get("buried") in (True, "partly", "unknown") for r in rows):
        return False, (f"every facade is buried ({rows[0].get('ground_why')}): no window is inferred (user, 6 Nov 2026: "
                       f"underground floors have no window)")
    if rows is None and under:
        return False, f"{under}: no window is inferred (user, 6 Nov 2026: underground floors have no window)"
    return True, "the plan draws no window" + (" (windows only on its exposed facades, R24)" if under else "")


def _facades(b: dict, texts_by_level: dict, side_by_level: dict, party_by_level: dict) -> dict:
    """Per level its facades (``facades.read``: the margin notes of R45, buried or exposed of R24); the record for
    ``level_inference.facades`` (pure but for the record)."""
    from wenart.ingest import facades as FC
    from wenart.ingest import rule_guards as RG

    out = {}
    entrance = FC.entrance_storey(b, texts_by_level)
    for lv in b.get("levels") or []:
        lid = lv["id"]
        texts = texts_by_level.get(lid)
        level = Level(b, lid, texts)
        edges = FC.edges_of(level)
        if not edges:
            continue
        notes = FC.notes(level, edges, texts, side_by_level.get(lid))
        grounds = FC.ground(b, level, lv, edges, texts, notes, entrance)
        rows = []
        for (p, q), note, g in zip(edges, notes, grounds):
            walls = sorted(w["id"] for w in level.walls.values() if _on_side(w, (p, q)))
            if g["buried"] is True and RG.blocked("below_ground", b, {"level_id": lid, "walls": walls, "why": g["why"]}):
                g = dict(g, buried=False)
            rows.append(dict({"edge": [[round(p[0], 2), round(p[1], 2)], [round(q[0], 2), round(q[1], 2)]],
                              "walls": walls, "buried": g["buried"], "ground": g["rung"], "ground_why": g["why"]},
                             **note))
        if sum(1 for r in rows if r.get("street")) >= 2:
            for r in rows:
                r["corner_plot"] = True                 # two street fronts: a corner plot (R45)
        out[lid] = rows
    if entrance:
        out["_entrance_storey"] = entrance
    return out


def buried_walls(b: dict, lid: str) -> set:
    """The walls of a level on its buried facades (R24; pure on the record)."""
    rows = ((b.get("level_inference") or {}).get("facades") or {}).get(lid) or []
    return {w for r in rows if r.get("buried") in (True, "partly", "unknown") for w in r.get("walls") or []}


def _windows(build, sheets: Optional[dict], texts_by_level: dict, region_by_level: dict, party_by_level: dict) -> None:
    b = build.building
    comp = (sheets or {}).get("completion") or {}
    regions = comp.get("regions") or {}
    sizes, size_source = sizes_from_tags(comp.get("window_sizes") or [])
    record = {"levels": {}, "party_walls": {}, "size_source": size_source, "sizes": {k: list(v) for k, v in
                                                                                       sizes.items()}}
    any_drawn = False
    for lv in sorted(b.get("levels") or [], key=lambda x: (x.get("order") or 0, x["id"])):
        lid = lv["id"]
        reg = region_by_level.get(lid)
        info = regions.get((reg or {}).get("id")) if reg else None
        party = party_by_level.get(lid) or {}
        if party:
            record["party_walls"][lid] = party
        read = sum(1 for o in b.get("openings") or [] if o.get("level_id") == lid and o.get("type") == "window")
        drawn = (info or {}).get("windows") or {}
        entry = {"region": (reg or {}).get("id"), "windows_read": read, "drawing": drawn,
                 "party_walls": sorted(party), "inferred": []}
        record["levels"][lid] = entry
        go, why = window_decision(b, lv, read, drawn if info is not None else None)
        any_drawn = any_drawn or bool(read or drawn.get("draws_windows"))
        if not go:
            entry["note"] = why
            if "below ground" in why or "under the ground" in why or "basement" in why:
                entry["below_ground"] = True
            continue
        blocked = set(party) | buried_walls(b, lid)
        new = infer_level(b, lid, {w: party.get(w, {"buried": True}) for w in blocked}, sizes, size_source,
                          build.ids.next, texts_by_level.get(lid), _ev_file(b, lid), (reg or {}).get("id"))
        b["openings"].extend(new)
        entry["inferred"] = [o["id"] for o in new]
        entry["note"] = (f"the plan draws no window (no window-layer geometry, no window block, no window tag): "
                         f"{sum(1 for o in new if o['type'] == 'window')} window(s) and "
                         f"{sum(1 for o in new if o['type'] == 'door')} balcony door(s) inferred")
        if new:
            build.warn(f"{lid}: {entry['note']} (UL331; sizes: {size_source})")
    record["any_drawn"] = any_drawn
    if record["levels"]:
        b["level_inference"]["windows"] = record


def summary(building: dict) -> dict:
    """What the reading inferred, for the reading check's report (pure): the inferred storeys with their evidence and
    the inferred windows and doors per level."""
    li = building.get("level_inference") or {}
    st = li.get("storeys") or {}
    wins = li.get("windows") or {}
    per = {}
    for o in building.get("openings") or []:
        if o.get("inferred"):
            k = per.setdefault(o["level_id"], {"windows": 0, "doors": 0})
            k["windows" if o.get("type") == "window" else "doors"] += 1
    return {"storeys": {"count": st.get("count"), "rule": st.get("rule"), "confidence": st.get("confidence"),
                        "guess": st.get("guess"), "guess_note": st.get("guess_note"),
                        "inferred": [{k: i.get(k) for k in ("level_id", "label", "reason", "built")}
                                     for i in st.get("inferred") or []],
                        "ladder": [{"rung": r.get("rung"), "count": r.get("count"), "note": r.get("note")}
                                   for r in st.get("ladder") or []],
                        "ground_floor": st.get("ground_floor"), "roof": st.get("roof"),
                        "open_point": st.get("open_point")} if st else None,
            "openings": per, "window_sizes": wins.get("size_source"),
            "party_walls": {lid: sorted(v) for lid, v in (wins.get("party_walls") or {}).items()},
            "below_ground": sorted(lid for lid, e in (wins.get("levels") or {}).items() if e.get("below_ground")),
            "light_wells": li.get("light_wells") or None,
            "core": {k: (v.get("reason") if isinstance(v, dict) else v) for k, v in (li.get("core") or {}).items()
                     if k in ("stair_head", "lift_overrun", "lifts_through")} or None,
            "core_rules": _rules_summary(li.get("core_rules") or {})}


def _rules_summary(cr: dict) -> Optional[dict]:
    """The core rules' changes in short (pure): ``{kind: [reason, ...]}`` without the empty kinds."""
    if not cr:
        return None
    lift, ent = cr.get("lift_doors") or {}, cr.get("entrances") or {}
    out = {"stairs": [s["reason"] for s in cr.get("stairs") or []],
           "stairs not drawn (a question)": [s["reason"] for s in cr.get("stairs_open") or []],
           "lift door marks undone": [x["reason"] for x in lift.get("unmarked") or []],
           "lift door pieces merged": [x["reason"] for x in lift.get("merged") or []],
           "lift doors removed": [x["reason"] for x in lift.get("removed") or []],
           "lift openings to review (drawn)": [x["reason"] for x in lift.get("review") or []],
           "lift openings made doors": [x["reason"] for x in lift.get("retyped") or []],
           "lift doors added": [x["reason"] for x in lift.get("added") or []],
           "gaps closed": [x["reason"] for x in cr.get("core_gaps") or []],
           "gaps kept as their drawn window": [x["reason"] for x in cr.get("core_gap_windows") or []],
           "gaps to review": [x["reason"] for x in cr.get("core_gap_review") or []],
           "entrances refused": [x["reason"] for x in ent.get("refused") or []],
           "outer doors tagged as windows (R37)": [x["reason"] for x in ent.get("windows") or []],
           "outer gaps tagged as doors": [x["reason"] for x in ent.get("tagged") or []],
           "main entrance changed": [ent["main"]["reason"]] if ent.get("main") else [],
           "entrances added": [x["reason"] for x in ent.get("added") or []],
           "entrance open point": [ent["open"]] if ent.get("open") else []}
    out = {k: v for k, v in out.items() if v}
    return out or None
