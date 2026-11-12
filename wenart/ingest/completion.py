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
   ``DEFAULT_SIZES``. Party walls come only from a party text on that side (``bitişik``, ``komşu``, ``attached``:
   ``party_walls``), never from the plan's shape. A plan that draws windows never gets inferred ones: a habitable room
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
SAMPLE_M = 0.10                 # a wall is probed every this many metres
PROBE_M = 0.25                  # ... this far beyond each face
EDGE_M = 0.30                   # a window keeps this far from a corner and from another opening
MIN_FACE_M = 0.80               # a face shorter than this takes no window
LONG_FACE_M = 5.0               # a habitable room's free face this long takes two windows
PIER_M = 0.90                   # ... with this much wall between them
HEAD_M = 2.20                   # an inferred window's head over its floor (the doors' head)
PARTY_REACH_M = 6.0             # a party text this far from the level's outline names its nearest side
PARTY_FACE_TOL_M = 0.35         # a wall's outer face this close to that side's line lies on it
PARALLEL_SIN = 0.10
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
    return bool(LIFT_RE.search(_fold(room.get("label") or room.get("label_raw"))))


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
        from wenart.reading_check.crossdoc import level_outline

        self.lid = lid
        self.rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid and _poly(r.get("polygon"))]
        self.polys = {r["id"]: _poly(r["polygon"]) for r in self.rooms}
        self.walls = {w["id"]: w for w in building.get("walls") or []
                      if w.get("level_id") == lid and w.get("start") and w.get("end")}
        self.openings = [o for o in building.get("openings") or [] if o.get("level_id") == lid]
        try:
            self.outline = level_outline(list(self.walls.values()), self.openings)
        except Exception:  # noqa: BLE001 - no outline: nothing faces the outside
            self.outline = None
        self.wells = {r["id"] for r in self.rooms if is_light_well(r, texts)}
        air = [_poly(s.get("polygon")) for s in (building.get("site") or {}).get("outdoor_spaces") or []
               if s.get("level_id") == lid and str(s.get("kind") or "") in OPEN_AIR]
        air = [p for p in air if p is not None]
        air += [self.polys[r["id"]] for r in self.rooms if str(r.get("room_type") or "") in OPEN_AIR]
        self.open_air = air
        self._air = [(p.bounds, prep(p.buffer(1e-6))) for p in air]
        self._rooms = [(self.polys[r["id"]].bounds, prep(self.polys[r["id"]].buffer(1e-6)), r) for r in self.rooms]
        self._inside = prep(self.outline.buffer(-1e-6)) if self.outline is not None else None

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
def party_walls(level: Level, side_points: list) -> dict:
    """``{wall_id: evidence}``: the walls on the side of the level's outline a party text names (pure). A text
    (``bitişik``, ``komşu``, ``attached`` ...) at most ``PARTY_REACH_M`` from the outline names its nearest outline
    edge; every wall parallel to that edge whose outer face lies on its line (``PARTY_FACE_TOL_M``) is a party wall."""
    out: dict = {}
    if level.outline is None:
        return out
    ring = list(level.outline.exterior.coords)
    edges = [(ring[i], ring[i + 1]) for i in range(len(ring) - 1) if math.dist(ring[i], ring[i + 1]) > 0.5]
    for sp in side_points:
        if sp.get("kind") != "party":
            continue
        q = Point(sp["at"])
        if level.outline.exterior.distance(q) > PARTY_REACH_M:
            continue
        e = min(edges, key=lambda e: LineString(e).distance(q), default=None)
        if e is None:
            continue
        (ex0, ey0), (ex1, ey1) = e
        el = math.hypot(ex1 - ex0, ey1 - ey0)
        eu = ((ex1 - ex0) / el, (ey1 - ey0) / el)
        for w in level.walls.values():
            a, u, length = _axis(w)
            if length < 0.3 or abs(u[0] * eu[1] - u[1] * eu[0]) > PARALLEL_SIN:
                continue
            off = (a[0] - ex0) * -eu[1] + (a[1] - ey0) * eu[0]          # signed distance of the wall axis to the line
            if abs(abs(off) - float(w.get("thickness") or 0.15) / 2.0) > PARTY_FACE_TOL_M and abs(off) > PARTY_FACE_TOL_M:
                continue
            out.setdefault(w["id"], {"text": sp["text"], "entity": sp.get("entity"), "layer": sp.get("layer"),
                                     "at": [round(sp["at"][0], 2), round(sp["at"][1], 2)],
                                     "side": [[round(ex0, 2), round(ey0, 2)], [round(ex1, 2), round(ey1, 2)]]})
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
    for room in sorted(level.rooms, key=lambda r: r["id"]):
        rtype = str(room.get("room_type") or "")
        if room["id"] in level.wells or (rtype not in HABITABLE and rtype not in WET):
            continue
        faces = [f for f in level.faces(room) if f["wall_id"] not in party]
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
    rec = (sheets or {}).get("storeys") if sheets else None
    regions = ((sheets or {}).get("completion") or {}).get("regions") or {}
    texts_by_level, region_by_level, party_by_level = {}, {}, {}
    for lid, works in by_level.items():
        w = sorted(works, key=lambda w: w.rank)[0]
        ex = w.extraction
        if ex.transform_to_building is None:
            continue
        texts_by_level[lid] = [{"text": t.text, "x": p[0], "y": p[1], "entity": t.entity}
                               for t in ex.texts for p in [to_building(ex, G_centre(t))]]
        reg = _region_for(sheets, w.record)
        region_by_level[lid] = reg
        info = regions.get((reg or {}).get("id")) if reg else None
        side = [dict(s, at=list(to_building(ex, tuple(s["point"])))) for s in (info or {}).get("side_texts") or []]
        party = {w: ev for w, ev in party_walls(Level(b, lid, texts_by_level[lid]), side).items()
                 if not RG.blocked("party_wall", b, {"level_id": lid, "wall": w, "why": ev.get("text")})}
        if party:
            party_by_level[lid] = party
    if rec and (rec.get("inferred") or rec.get("open_point")):
        _storeys(build, rec, texts_by_level, party_by_level)
    wells = _light_wells(build, texts_by_level)
    if wells:
        b["level_inference"]["light_wells"] = wells
    _mark_party(b, party_by_level)
    dropped = party_balconies(b, party_by_level)
    if dropped:
        b["level_inference"]["party_balconies"] = dropped
        build.warn(f"party walls: {len(dropped)} balcony(ies) on an attached side left out "
                   f"({', '.join(d['id'] for d in dropped)}): {dropped[0]['reason']}")
    # 12 Nov 2026 (the architect's audit): the common core (a missed stair, lift doors, flat-core gaps) and entrances
    from wenart.ingest import core_rules as CR
    rules = CR.apply(build, texts_by_level, party_by_level)
    b["level_inference"]["core_rules"] = rules
    gf = (b["level_inference"].get("storeys") or {}).get("ground_floor")
    if isinstance(gf, dict):
        ent = rules["entrances"]
        gf["entrance"] = ({"door": ent["added"][0]["door"], "reason": ent["added"][0]["reason"]} if ent["added"] else
                          {"door": None, "open": True, "reason": ent["open"]} if ent["open"] else gf.get("entrance"))
    _windows(build, sheets, texts_by_level, region_by_level, party_by_level)
    core = core_record(b)
    if core:
        b["level_inference"]["core"] = core
    # 12 Nov 2026 (the architect's audit, second series): shafts, stairs over nothing, balcony doors, exterior flags
    from wenart.ingest import sense_rules as SR
    b["level_inference"]["sense_rules"] = SR.apply(build, texts_by_level)


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
        if o.get("type") != "door" or w is None or not o.get("center"):
            continue
        a, u, _ = _axis(w)
        n = (-u[1], u[0])
        reach = float(w.get("thickness") or 0.15) / 2.0 + PROBE_M
        c = o["center"]
        sides = [level.kind_at((c[0] + k * n[0] * reach, c[1] + k * n[1] * reach), "") for k in (1, -1)]
        if "outside" in sides and ("room" in sides or "light_well" in sides):
            out.append(o["id"])
    return out


def core_record(b: dict) -> dict:
    """The building's core (pure): the lifts and stairs per storey of the base variant, whether each lift continues
    through every storey, and what the core needs on the roof: a stair head over a stair that reaches the top storey of
    a building with several storeys, and a lift overrun over every lift shaft there (inferred; ``built`` False: the
    builder has no stair head or overrun yet, listed so they are not forgotten)."""
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
    top = storeys[-1]["id"]
    rec = {"lifts": lifts, "stairs": stairs,
           "lifts_through": all(len(lifts[lv["id"]]) == len(lifts[storeys[0]["id"]]) for lv in storeys),
           "stair_head": None, "lift_overrun": None}
    if stairs.get(top):
        rec["stair_head"] = {"needed": True, "built": False, "over": stairs[top],
                             "reason": f"the core stair reaches the top storey {top}: a stair head over it gives the "
                                       f"roof its access (inferred; the builder does not build a stair head yet)"}
    elif any(stairs.values()):
        rec["stair_head"] = {"needed": None, "built": False, "over": [],
                             "reason": f"no stair is read on the top storey {top}: the stair head cannot be placed"}
    else:
        rec["stair_head"] = {"needed": None, "built": False, "over": [],
                             "reason": "no stair is read on any storey: the core stair and its stair head are missing"}
    if lifts.get(top):
        rec["lift_overrun"] = {"needed": True, "built": False, "over": lifts[top],
                               "reason": f"{len(lifts[top])} lift shaft(s) reach the top storey {top}: each has an "
                                         f"overrun over the roof (inferred; the builder does not build it yet)"}
    return rec


def _ev_file(b: dict, lid: str) -> str:
    lv = next((x for x in b.get("levels") or [] if x["id"] == lid), {})
    return next((e.get("file") for e in lv.get("evidence") or [] if e.get("file")), "") or ""


def _storeys(build, rec: dict, texts_by_level: dict, party_by_level: dict) -> None:
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
    built = [i["level_id"] for i in rec.get("inferred") or [] if i.get("built")]
    if built:
        build.warn(f"storeys: {len(built)} storey(s) the documents do not draw inferred ({', '.join(built)}; "
                   f"{rec.get('rule')}, confidence {rec.get('confidence')}" + (", a guess" if rec.get("guess") else "")
                   + ")")
    ground = levels.get("L0") if rec.get("ground_from_typical") else None
    if ground is not None and "L0" in built:
        out["ground_floor"] = _ground_floor(build, ground, rec, texts_by_level.get("L0"), party_by_level.get("L0") or {})
    if b.get("roof") is None and built:
        top = max((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: lv.get("order") or 0)
        reason = (f"no roof is drawn and the storeys above the drawn plan are inferred: a flat roof over the top "
                  f"storey {top['id']} ({top['label']}), outline, height and thickness assumed")
        b["roof"] = _flat_roof(b, top, reason)
        out["roof"] = reason
        build.warn(f"roof: {reason} (inferred)")
    b["level_inference"]["storeys"] = out


def _ground_floor(build, ground: dict, rec: dict, texts: Optional[list], party: dict) -> dict:
    """The inferred ground floor read from the typical plan: no cantilevered balconies when the footprint is smaller
    than the typical floor. Its entrance comes from the general entrance rule (``core_rules.fix_entrances``), written
    into ``entrance`` by ``complete``."""
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
                    p.difference(level.outline).area >= 0.5 * p.area:
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
    under = below_ground(building, level)
    if under:
        return False, f"{under}: no window is inferred (user, 6 Nov 2026: underground floors have no window)"
    return True, "the plan draws no window"


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
        new = infer_level(b, lid, party, sizes, size_source, build.ids.next, texts_by_level.get(lid),
                          _ev_file(b, lid), (reg or {}).get("id"))
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
           "lift doors removed": [x["reason"] for x in lift.get("removed") or []],
           "lift doors added": [x["reason"] for x in lift.get("added") or []],
           "gaps closed": [x["reason"] for x in cr.get("core_gaps") or []],
           "entrances refused": [x["reason"] for x in ent.get("refused") or []],
           "entrances added": [x["reason"] for x in ent.get("added") or []],
           "entrance open point": [ent["open"]] if ent.get("open") else []}
    out = {k: v for k, v in out.items() if v}
    return out or None
