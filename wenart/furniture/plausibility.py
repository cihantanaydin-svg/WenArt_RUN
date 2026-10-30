"""Plausibility of rooms and furniture (docs/milestone11.md §4.2, §4.3, §6, contract §17.2).

What: ``score_room(building, room_id)`` and ``score_building(building)`` measure the checklist items F1–F9 and
R1–R4 that code can measure (back to the wall, fronts facing their group, groups complete, real sizes,
clearances, blocked doors and windows, floating pieces, room type vs size and fixtures). The agent's code critic,
the edit validator (``edit_ops.apply_edit``) and the tests use the same functions.

Contract (frozen; owner: track B): pure functions, no I/O, the building is never changed; under 50 ms per room.

``Violation = {"check": "F3", "severity": "critical" | "major" | "minor", "target": <piece/room/opening id>,
"room_id": <id>, "message": <one sentence>, "metrics": {<numbers that prove it>}}``

Why: no stage could see its own result (§1.4): a bed with its headboard in the room, chairs facing away from their
table, an armchair behind a sofa's back all passed every stage. One measured score per room lets the agent's critic
find them and lets the edit validator refuse an edit that makes a room worse.

How (per room; pieces with ``build: false`` are not built and are skipped; decor is a separate list):

- the orientation of a piece is its drawn front (``front_deg``); without one, the side the builder faces it
  (``(270 + rotation) mod 360``, the footprint's local -Y), reported as ``front_assumed`` in the metrics;
- F1 the type is in the room type's row (``schemas.allowed_types``; stairs, lamps, plants and side tables anywhere);
- F2 the footprint fits the type's product size range (``wenart/recognition/size_table.yaml``, +15 %, either way);
- F3 types whose back belongs on a wall (``schemas.ORIENTATION_RULES`` back ``wall``): >= 60 % of the back edge within
  ``BACK_WALL_M`` (5 cm) of the room outline and parallel to the nearest wall within 5 degrees; a sofa
  (``wall_or_group``) may stand free when its front faces its group (TV unit, coffee table);
- F4 the front does not face a wall closer than 0.3 m; and, when one of the type's ``front_to`` types stands within
  ``reach_m``, the front faces one of them (within 45 degrees) from the target's front side (not behind its back);
- F5 groups: a dining table has chairs (by its length, ``CHAIRS_BY_TABLE_LENGTH``; none = major), a bed its
  nightstands, a sofa a coffee table (rooms that may hold one), a desk a chair; an unverified host is skipped;
- F6 front clearances (``placer`` zones; a coffee table, pouf or side table may stand in front of a seat) and the
  0.9 m walkways between doors and to the windows (``placer.walkway_blame``);
- F7 a door's approach strip is blocked (critical; not by a stair, entered through its opening); a piece taller than
  the sill stands in a window band (major);
- F8 a free-standing piece (back ``free``) that touches no wall and has no group partner within ``partner_m``;
- F9 what code can see of "odd": two pieces overlapping (a chair under its table is fine), a piece through the room
  outline (not a stair: it runs into the storey opening), an unexplained ``unknown`` box that is built;
- R1 the room type fits its area and fixtures (a bathtub makes a bathroom; a 3 m² room is no bedroom);
- R2 the level's ceiling height is plausible (2.2–4.0 m); R3 every door swing into the room is free;
- R4 (finishes) is the build's business (track C): listed, not measured here.

Score = 100 − (30 per critical, 10 per major, 3 per minor), floored at 0.

Milestone 12 (docs/milestone12.md §4.6; owner: track G): the group checks of ``group_checks`` replace the counting
of F5 and run here, so the critic, the edit validator and the tests share one function: G1–G4, G5 (the side and
foot clearances; the headboard stays F3), G6–G10, G11 (the walkways: 0.60 m between doors and to every use zone,
0.80 m from the entrance door, instead of F6's 0.9 m walkway), G12 (the window bands, instead of F7's window part,
a TV unit counted with its TV) and G13 (0.80 m in front of wardrobes and other door-fronted storage). F6 keeps the
front clearances the group checks do not cover (sofas, armchairs, cribs); F7 keeps the door approach strips; G14 is
F1 (F1 reads the zone a piece stands in, ``group_checks.allowed_types_at``). F5 stays in ``CHECKS`` as replaced.
F2 no longer takes a size "either way" for a piece with a front: a footprint whose width and depth are swapped
against the type (a bed turned 90°: real02 ``f_L0_007`` after a resize) is a major F2 finding; frontless and
square types and cribs (a long side as front) still fit either way; kitchen counters, islands, wall cabinets and
stairs are built by code at any length and are not size-checked.

Milestone 13 (docs/milestone13.md §1.4, §1.8 B6, §3.0 K3; track T3): F2 runs on every drawn piece, in the scene or
not (the misread 2.55 m beds and 3.35 m tables of real04 never got a finding because the fit left them unbuilt;
the metrics carry ``built: false`` and the reason). F8 names the missing anchor: a chair, armchair or lamp that
stands around a drawn partner the fit did not build is reported as "stands around <type> <id>, which is not built
(<reason>)" with ``metrics.missing_anchor`` (the cause for the agent's tools), not as "stands alone". The room
types read the aliases of ``program.room_kind`` (``room_types``): a sofa in real04's "Oyun Aktivite Ve Dinlenme
Odası" (``other``) is no F1 finding.

Fix round after P4a (17 Oct 2026; pod P4a, real02):

- F9 no longer counts a piece a kitchen run holds as an overlap: a sink built into its run (both sides: the sink's
  ``asset.built_in`` names the run and the run's ``asset.module_plan.built_ins`` lists the sink, the rule of
  ``wenart.blender.furniture.built_in_ids``) or a stove / pinned sink in its run's gap (``module_plan.gaps``) is no
  overlap (``_run_held``). Why: P4a logged 8 major F9 findings per round for the 4 built-in sinks and 4 stoves of the
  real02 kitchens (each overlap was the whole drawn footprint, by design of the fix round after P3), and the agent
  spent 8 rejected ``swap_model`` edits on them. A sink whose run does not hold it (or that names another run), and
  any other piece, keeps its F9;
- the "through the room outline" finding carries ``metrics.depth_m``: how deep the footprint reaches past the outline
  (the largest distance of the outside part's corners from the room). Why: P4a's wardrobe f_L-1_024 reached 0.05 m²
  through the outline, a 0.020 m cut along its 2.57 m back (its S2 said the same); the area alone read like a
  misplaced piece and the agent removed the drawn anchor as "not furniture". The agent's causes route a cut below
  the S2 tolerance as within tolerance and a deeper one to the move tools (``wenart.agent.causes``).

Fix round after P4b (17 Oct 2026; pod P4b, real03). What: F1 does not flag a drawn piece of a
``DRAWN_ANYWHERE_TYPES`` type (a washing machine) in a room whose types do not list it, unless the room never holds
it (``schemas.misplaced_fixed``: a stair room or a shaft, still a major F1). Why: real03 draws a washing machine
(block "TEF - BANYO - ÇAMAŞIR MAKİNESİ") in each of the 4 entrance halls (a utility closet İŞLİK shares the hall's
face); F1 and G14 flagged them as the wrong type in every round, and the agent spent about 30 tool calls on them
(set_room_type to bathroom, complete_group bathroom_set, fix_fixture), all refused. CLAUDE.md treats drawn fixed
equipment like walls. The rows of ``schemas.ALLOWED_TYPES`` (what the AI may add to a hall) are unchanged; only this
narrow type list is skipped, so a drawn toilet in a bedroom or a drawn stove in a living room stays a finding.

29 Oct 2026 (lesson UL92, user on real06 run 20261028-154514-full: "This washing machine would not open"; the agent had
turned the drawn washer f_L1_019 to clear F4 and its door faced the toilet 0.11 m away, which no check measured): F6
also measures the access zone of every door-fronted appliance and nightstand (``fixture_use.access_problem``: its width
x its type's depth, free of walls and of every piece but light movable ones): critical when its door or drawers cannot
open (``open_m``), major when it cannot be used (``use_m``). A front into a wall within 0.3 m stays F4's; a piece of a
kitchen run is G8's (its aisle). So the edit validator refuses an edit or a placement that blocks such a front.
"""
from __future__ import annotations

import functools
import re
import math
from typing import Optional

from shapely.geometry import LineString, Point, Polygon


from wenart import geometry as G
from wenart.furniture import fixture_use as FU
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import placer, schemas

SEVERITIES = ("critical", "major", "minor")
WEIGHTS: dict[str, int] = {"critical": 30, "major": 10, "minor": 3}

# id -> {"severity": default severity, "what": one line, "measured": code measures it here}.
CHECKS: dict[str, dict] = {
    "F1": {"severity": "major", "what": "the piece's type is allowed in the room type (schemas.allowed_types)",
           "measured": True},
    "F2": {"severity": "major", "what": "the footprint fits the type's product size range (size table, +15 %)",
           "measured": True},
    "F3": {"severity": "major", "what": "the back stands on a wall where the type needs it (bed: critical; a sofa "
                                        "may stand free facing its group)", "measured": True},
    "F4": {"severity": "major", "what": "the front faces its group (sofa -> TV unit / coffee table, chairs -> table, "
                                        "armchairs -> coffee table / sofa) and never a wall closer than 0.3 m",
           "measured": True},
    "F5": {"severity": "minor", "what": "replaced by the group checks G1-G13 (Milestone 12: arrangements, not counts)",
           "measured": False},
    "F6": {"severity": "major", "what": "front clearances of seats and cribs (0.6 m; armchairs 0.45 m) and the access "
                                        "zone of door-fronted appliances and nightstands (critical when the door or "
                                        "drawers cannot open); the walkways are G11", "measured": True},
    "F7": {"severity": "critical", "what": "no door approach blocked (critical); the window bands are G12",
           "measured": True},
    "F8": {"severity": "major", "what": "no floating piece: a free-standing piece touches a wall or belongs to a "
                                        "group", "measured": True},
    "F9": {"severity": "major", "what": "nothing odd: overlapping pieces, a piece through the room outline, an "
                                        "unexplained unknown box", "measured": True},
    "R1": {"severity": "major", "what": "the room type fits the area and the fixtures", "measured": True},
    "R2": {"severity": "minor", "what": "the ceiling height is plausible (2.2-4.0 m)", "measured": True},
    "R3": {"severity": "critical", "what": "every door into the room swings into free space", "measured": True},
    "R4": {"severity": "minor", "what": "finishes fit the room (tiles in wet rooms, a splashback in kitchens): "
                                        "measured by the build (track C), not here", "measured": False},
}
# Milestone 12: F6's front clearances that no group check covers (beds: G5, desks: G7, storage: G13).
F6_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "crib")
# Milestone 12: the group checks that run here (G14 is F1); each violation keeps its own severity.
GROUP_CHECKS: tuple[str, ...] = tuple(f"G{i}" for i in range(1, 14))
CHECKS.update({g: {"severity": "major", "what": GC.WHAT[g], "measured": True} for g in GROUP_CHECKS})

AREA_MIN_M2 = 0.01               # intersections below this are touching (drawn pieces meet at their edges)
OVERLAP_MIN_M2 = 0.05            # F9: two pieces overlap
OUTSIDE_MIN_M2 = 0.05            # F9: a piece reaches through the room outline
BACK_SHARE = 0.6                 # F3: share of the back edge that must lie on the wall
SIDE_WALL_M = 0.10               # F8: a side this close to the outline touches a wall
UNKNOWN_LARGE_M2 = 1.0           # F9: an unknown box this large is a major oddity
ALWAYS_ALLOWED = ("stair", "floor_lamp", "potted_plant", "side_table", "unknown")
SEAT_TYPES = ("chair", "bar_stool", "office_chair", "bench")
UNDER_TYPES = ("table_dining", "desk", "kitchen_island", "table_coffee", "kitchen_counter")
TUCKED_TYPES = SEAT_TYPES + ("ottoman", "side_table")
# F6: what may stand in front of a seat besides the placer's CLEARANCE_EXEMPT (a coffee table before a sofa).
EXTRA_EXEMPT: dict[str, tuple[str, ...]] = {"sofa": ("table_coffee", "ottoman"),
                                            "sofa_corner": ("table_coffee", "ottoman")}
# R1: what a fixture says about its room.
FIXTURE_ROOMS: dict[str, tuple[str, ...]] = {
    "bathtub": ("bathroom",), "shower": ("bathroom", "wc"), "toilet": ("bathroom", "wc"),
    "stove": ("kitchen", "living", "dining", "other"), "sink_kitchen": ("kitchen", "living", "dining", "other"),
    "bed_double": ("bedroom", "other", "living"), "bed_single": ("bedroom", "other", "living"),
}
ROOM_MIN_M2: dict[str, tuple[float, str]] = {"bedroom": (6.0, "major"), "living": (8.0, "minor"),
                                             "kitchen": (3.0, "minor"), "dining": (5.0, "minor")}
CEILING_RANGE_M = (2.2, 4.0)
NIGHTSTAND_REACH_M = 0.5
COFFEE_REACH_M = 2.0
CHAIR_REACH_M = 0.8
DESK_CHAIR_REACH_M = 1.0


@functools.lru_cache(maxsize=1)
def _size_table() -> dict:
    from wenart.recognition import symbols   # the M7 size table and its fit rule (lazy: PyYAML)

    return symbols.load_size_table()


def _fits(ftype: str, size) -> bool:
    from wenart.recognition import symbols

    return symbols.fits(_size_table(), ftype, size)


def _violation(check: str, target: str, room_id: str, message: str, metrics: Optional[dict] = None,
               severity: Optional[str] = None) -> dict:
    return {"check": check, "severity": severity or CHECKS[check]["severity"], "target": target, "room_id": room_id,
            "message": message, "metrics": dict(metrics or {})}


class _Room:
    """The measured facts of one room: its outline, context (doors, windows, walkways) and its built pieces in
    the frame of their fronts. Read-only views of the building."""

    def __init__(self, building: dict, room: dict):
        self.building = building
        self.room = room
        self.id = room["id"]
        self.type = room.get("room_type") or "unknown"
        self.ctx = placer.room_context(building, room)
        self.polygon: Polygon = self.ctx.polygon
        self.ring = self.polygon.exterior
        self.items = [f for f in building.get("furniture") or [] if f.get("room_id") == self.id]
        # Built: not ``build: false`` and not a library gap the fit left unbuilt (``asset.method == "none"``); unknown
        # pieces stay here for F9 (the "unknown box" finding) and are left out of the floor below.
        self.built = [f for f in self.items if f.get("build") is not False and (
            not isinstance(f.get("asset"), dict) or f["asset"].get("method") not in GR.NOT_BUILT_ASSET_METHODS)]
        self.pieces: dict[str, placer.Piece] = {}
        for i, f in enumerate(self.built):
            try:
                self.pieces[f["id"]] = placer.drawn_piece(f, i)
            except (KeyError, TypeError, ValueError):
                continue
        self.polys = {pid: p.polygon() for pid, p in self.pieces.items()}
        # Floor pieces the placer checks: built, typed, standing on the floor.
        self.floor = [f for f in self.built if f["id"] in self.pieces and f["type"] != "unknown"
                      and not schemas.off_floor(f)]

    def item(self, pid: str) -> dict:
        return next(f for f in self.built if f["id"] == pid)

    def front_dir(self, pid: str) -> tuple[float, float]:
        a = math.radians(G.front_direction_deg(self.pieces[pid].rotation_deg))
        return math.cos(a), math.sin(a)


def _assumed(item: dict) -> dict:
    return {"front_assumed": True} if item.get("front_deg") is None else {}


def _front_deg(piece: placer.Piece) -> float:
    return round(G.front_direction_deg(piece.rotation_deg), 2)


# --------------------------------------------------------------------------
# F1, F2: type and size
# --------------------------------------------------------------------------

_MULTI_LABEL = re.compile(r"one face holds the room names (.+)$")


def room_types(building: dict, room: dict) -> list[str]:
    """The room's type, plus the types of the other room names its face holds (the pipeline's conflict "one face
    holds the room names 'Açık Mutfak' and 'SALON'": real02's open kitchen is a kitchen and a living room)."""
    from wenart import building as B

    out = [room.get("room_type") or "unknown"]
    for c in building.get("conflicts") or []:
        if room["id"] not in (c.get("element_ids") or []):
            continue
        m = _MULTI_LABEL.search(c.get("description") or "")
        if not m:
            continue
        for name in re.findall(r"'([^']+)'", m.group(1)):
            t = B.room_type_for(name)
            if t and t not in out:
                out.append(t)
    if out[0] in ("other", "unknown", None, "", "storage") and room.get("id"):
        # Milestone 13: the alias kind of an ``other`` / ``unknown`` room (label words, drawn anchors); 26 Oct 2026:
        # a storage room only when it is read as a dressing room (``program.dressing_room``, its label words).
        from wenart.furniture import program as PR     # lazy: program imports this module

        kind = PR.room_kind(building, room)
        if kind and kind not in out and (out[0] != "storage" or kind == "dressing"):
            out.append(kind)
    return out


def allowed_in(building: dict, room: dict) -> set:
    """Every type the room's types allow (``room_types``), plus stand-alone lamps, plants and side tables."""
    out = set(ALWAYS_ALLOWED)
    for t in room_types(building, room):
        out |= set(schemas.allowed_types(t, room.get("room_subtype")))
    return out


# Fix round after P4b (module docstring): drawn fixed types that any room may hold unless it never holds them
# (``schemas.misplaced_fixed``: a stair room, a shaft). The rows of ``schemas.ALLOWED_TYPES`` (what the AI may add)
# stay as they are.
# Integration of the fix round after P5 (F_reading's ask): a drawn wardrobe too: the reader now types real04's
# corridor coat closets (a hanging rail with hangers, symbols.hanging_rail) as wardrobes, which F1 called "not a piece
# of a hall room" in r_L1_koridor / r_L1_koridor_2. Drawn pieces only: the hall rows (what the AI may add) are unchanged.
DRAWN_ANYWHERE_TYPES: tuple[str, ...] = ("washing_machine", "wardrobe")


def drawn_anywhere(f: dict, room_type_list) -> bool:
    """Fix round after P4b: a drawn piece of a ``DRAWN_ANYWHERE_TYPES`` type in a room none of whose types
    (``room_types``) never holds it: no wrong-room finding (F1)."""
    return (f.get("source") == "from_documents" and f.get("type") in DRAWN_ANYWHERE_TYPES
            and not any(schemas.misplaced_fixed(f["type"], t) for t in room_type_list))


def _f1(r: _Room) -> list[dict]:
    types = room_types(r.building, r.room)
    if not any(t in schemas.ALLOWED_TYPES for t in types):
        return []
    zoned = bool(r.room.get("zones"))
    allowed = allowed_in(r.building, r.room)
    out = []
    for f in r.built:
        if zoned and f["id"] in r.pieces:     # Milestone 12: the zone a piece stands in (G14)
            allowed = GC.allowed_types_at(r.building, r.room, r.pieces[f["id"]].center)
        if f["type"] not in allowed and drawn_anywhere(f, types):
            continue                          # fix round after P4b: a drawn washer in a hall or a utility closet
        if f["type"] not in allowed:
            # A drawn piece says what the room holds (its row may be narrow, e.g. a sofa in an "other" room): minor,
            # unless it is fixed equipment in the wrong room (a kitchen counter read in a bedroom wardrobe, U12).
            drawn = f.get("source") == "from_documents"
            out.append(_violation("F1", f["id"], r.id, f"{f['type']} is not a piece of a {r.type} room",
                                  {"type": f["type"], "room_type": r.type, "drawn": drawn},
                                  severity="minor" if drawn and f["type"] not in schemas.FIXED_TYPES else None))
    return out


PARAMETRIC_TYPES = ("kitchen_counter", "kitchen_island", "wall_cabinet", "stair")    # built by code at any length
# Types whose footprint fits either way: no front, square, or (a crib) a long side as its front.
EITHER_WAY_TYPES = tuple(schemas.FRONTLESS_TYPES) + ("crib", "chair", "armchair", "bar_stool", "office_chair",
                                                     "washing_machine", "shower")


def size_range(ftype: str) -> Optional[tuple[tuple[float, float], tuple[float, float]]]:
    """``((width min, max), (depth min, max))`` of a type's real sizes (the size table), None when it has none."""
    from wenart.recognition import symbols

    return symbols.normalise_table(_size_table()).get(ftype)


def oriented_fit(ftype: str, size) -> dict:
    """How a footprint ``size = (width along the front, depth)`` fits its type's ranges (size table):
    ``{"fits": with the +15 % tolerance in this orientation, "turned": the swapped footprint fits the ranges exactly
    while this one does not and its proportions are the other way round (a bed turned 90°)}``."""
    from wenart.recognition import symbols

    table = symbols.normalise_table(_size_table())
    if ftype not in table:
        return {"fits": True, "turned": False}
    (w0, w1), (d0, d1) = table[ftype]
    w, d = float(size[0]), float(size[1])
    tol = symbols.SIZE_TOLERANCE

    def inside(v, lo, hi, t=0.0):
        return lo / (1.0 + t) - 1e-9 <= v <= hi * (1.0 + t) + 1e-9

    fits = inside(w, w0, w1, tol) and inside(d, d0, d1, tol)
    strict, swapped = inside(w, w0, w1) and inside(d, d0, d1), inside(d, w0, w1) and inside(w, d0, d1)
    reversed_ = (w - d) * ((w0 + w1) / 2.0 - (d0 + d1) / 2.0) < -1e-9
    return {"fits": fits, "turned": (not strict) and swapped and reversed_}


def unbuilt_drawn(r: "_Room") -> list[dict]:
    """Milestone 13: the room's typed drawn pieces the fit left unbuilt (``asset.method`` none: a library gap) but
    that stand in the documents (``build`` not false): F2 and F8 read them."""
    built = {f["id"] for f in r.built}
    return [f for f in r.items if f["id"] not in built and f.get("source") == "from_documents"
            and f.get("build") is not False and f.get("type") not in (None, "unknown") and f.get("footprint")]


def _not_built_reason(f: dict) -> str:
    asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
    return str(f.get("not_built_reason") or asset.get("fallback_reason") or f.get("library_gap")
               or ("asset.method none" if asset.get("method") == "none" else "not built"))


def _f2(r: _Room) -> list[dict]:
    out = []
    for f in r.built + unbuilt_drawn(r):          # Milestone 13: every drawn piece, in the scene or not
        if f["type"] in ("unknown",) or f["type"] in PARAMETRIC_TYPES or f["type"] in schemas.MOUNTED_TYPES:
            continue
        size = [round(float(v), 3) for v in f["footprint"]["size"]]
        if f["type"] not in _size_table():
            continue
        built = f["id"] in r.pieces
        extra = {} if built else {"built": False, "not_built": _not_built_reason(f)}
        tail = "" if built else f" (not built: {_not_built_reason(f)[:80]})"
        if not _fits(f["type"], size):
            out.append(_violation("F2", f["id"], r.id, f"{f['type']} {size[0]:.2f} x {size[1]:.2f} m is outside the "
                                  f"type's product sizes{tail}", dict({"size": size, "type": f["type"]}, **extra)))
            continue
        if f.get("front_deg") is None or f["type"] in EITHER_WAY_TYPES:
            continue
        try:
            p = r.pieces[f["id"]] if built else placer.drawn_piece(f)
        except (KeyError, TypeError, ValueError):
            continue
        fit = oriented_fit(f["type"], p.size)
        if fit["turned"] or not fit["fits"]:
            out.append(_violation("F2", f["id"], r.id, f"{f['type']} {p.size[0]:.2f} m wide x {p.size[1]:.2f} m deep "
                                  f"(seen from its front) is turned 90° against the type's product sizes{tail}",
                                  dict({"size": [round(p.size[0], 3), round(p.size[1], 3)], "type": f["type"],
                                        "turned": True, "front_deg": f.get("front_deg")}, **extra)))
    return out


# --------------------------------------------------------------------------
# F3, F4: back and front
# --------------------------------------------------------------------------

def back_on_wall(piece: placer.Piece, r: "_Room") -> tuple[bool, dict]:
    """(the back edge stands on a wall, metrics): >= ``BACK_SHARE`` of the edge within ``BACK_WALL_M`` of the
    room outline and the nearest outline segment parallel within ``BACK_PARALLEL_DEG``."""
    edge = piece.back_edge()
    samples = [edge.interpolate(t, normalized=True) for t in (0.05, 0.25, 0.5, 0.75, 0.95)]
    dists = [r.ring.distance(pt) for pt in samples]
    share = sum(1 for d in dists if d <= schemas.BACK_WALL_M + 0.005) / len(samples)
    mid = samples[2].coords[0]
    seg = r.ctx.segments[r.ctx.nearest_segment(mid)]
    (x0, y0), (x1, y1) = edge.coords[0], edge.coords[-1]
    edge_deg = math.degrees(math.atan2(y1 - y0, x1 - x0))
    wall_deg = G.segment_angle_deg(seg[0], seg[1])
    diff = G.angle_difference_deg(edge_deg % 180.0, wall_deg % 180.0)
    diff = min(diff, 180.0 - diff)
    ok = share >= BACK_SHARE - 1e-9 and diff <= schemas.BACK_PARALLEL_DEG + 1e-9
    return ok, {"back_wall_m": round(min(dists), 3), "back_on_wall_share": round(share, 2),
                "parallel_deg": round(diff, 1)}


def _front_mid(piece: placer.Piece, d: tuple[float, float]) -> tuple[float, float]:
    half = piece.size[1] / 2.0
    return piece.center[0] + d[0] * half, piece.center[1] + d[1] * half


def front_wall_distance(piece: placer.Piece, r: "_Room", d: tuple[float, float]) -> Optional[float]:
    """Distance from the front edge's midpoint to the room outline straight ahead (None: more than 0.3 m)."""
    m = _front_mid(piece, d)
    ray = LineString([(m[0] + d[0] * 0.005, m[1] + d[1] * 0.005),
                      (m[0] + d[0] * schemas.FRONT_WALL_MIN_M, m[1] + d[1] * schemas.FRONT_WALL_MIN_M)])
    if r.polygon.buffer(1e-4).contains(ray):
        return None
    hit = ray.intersection(r.ring)
    if hit.is_empty:
        return 0.0                                     # the front edge itself is outside the room
    return round(min(Point(m).distance(g) for g in getattr(hit, "geoms", [hit])), 3)


def behind_back(r: "_Room", pid: str, tid: str) -> bool:
    """Piece ``pid`` stands behind the back of piece ``tid`` (a target with a front) and looks at it."""
    titem = r.item(tid)
    if titem["type"] in schemas.FRONTLESS_TYPES:
        return False
    p, t = r.pieces[pid], r.pieces[tid]
    td = r.front_dir(tid)
    along = (p.center[0] - t.center[0]) * td[0] + (p.center[1] - t.center[1]) * td[1]
    if along >= -t.size[1] / 2.0 + 1e-6:
        return False
    pd = r.front_dir(pid)
    return pd[0] * td[0] + pd[1] * td[1] > 0.5           # looking the same way as the target: at its back


def faces(r: "_Room", pid: str, tid: str) -> tuple[bool, float]:
    """(piece ``pid`` faces piece ``tid``, the angle in degrees): the target's nearest point lies within
    ``FACING_DEG`` of the front, and the piece does not stand behind the target's back (a target with a front)."""
    p, t = r.pieces[pid], r.pieces[tid]
    tpoly = r.polys[tid]
    if tpoly.contains(Point(p.center)):
        goal = (tpoly.centroid.x, tpoly.centroid.y)
    else:
        from shapely.ops import nearest_points

        q = nearest_points(tpoly, Point(p.center))[0]
        goal = (q.x, q.y)
    dx, dy = goal[0] - p.center[0], goal[1] - p.center[1]
    if math.hypot(dx, dy) < 1e-6:
        return True, 0.0
    angle = G.angle_difference_deg(math.degrees(math.atan2(dy, dx)), G.front_direction_deg(p.rotation_deg))
    ok = angle <= schemas.FACING_DEG + 1e-9
    titem = r.item(tid)
    if ok and titem["type"] not in schemas.FRONTLESS_TYPES:
        td = r.front_dir(tid)
        along = (p.center[0] - t.center[0]) * td[0] + (p.center[1] - t.center[1]) * td[1]
        if along < -t.size[1] / 2.0 + 1e-6:
            ok = False                                 # behind the target's back
    return ok, round(angle, 1)


def _targets(r: "_Room", pid: str, types, reach: float) -> list[str]:
    poly = r.polys[pid]
    return sorted((tid for tid in r.pieces if tid != pid and r.item(tid)["type"] in types
                   and r.polys[tid].distance(poly) <= reach + 1e-9),
                  key=lambda tid: (round(r.polys[tid].distance(poly), 4), tid))


def _faced_group(r: "_Room", pid: str, rule: dict) -> tuple[Optional[bool], list[str]]:
    """(None when no ``front_to`` target stands within reach, else whether one is faced; the targets)."""
    if not rule["front_to"]:
        return None, []
    targets = _targets(r, pid, rule["front_to"], rule["reach_m"])
    if not targets:
        return None, []
    return any(faces(r, pid, tid)[0] for tid in targets), targets


def _f3_f4(r: _Room) -> list[dict]:
    out = []
    for f in r.built:
        pid = f["id"]
        if pid not in r.pieces or f["type"] in ("unknown", "stair") or f["type"] in schemas.MOUNTED_TYPES:
            continue
        rule = schemas.orientation_rule(f["type"])
        if rule["back"] == "skip":
            continue
        p = r.pieces[pid]
        assumed = _assumed(f)
        faced, targets = _faced_group(r, pid, rule)
        if rule["back"] in ("wall", "wall_or_group"):
            ok, metrics = back_on_wall(p, r)
            if not ok and not (rule["back"] == "wall_or_group" and faced):
                where = "the headboard stands in the room" if f["type"] in ("bed_double", "bed_single", "bunk_bed") \
                    else "its back is not on a wall"
                out.append(_violation("F3", pid, r.id, f"{f['type']}: {where} ({metrics['back_wall_m']:.2f} m off)",
                                      dict(metrics, front_deg=_front_deg(p), **assumed),
                                      severity=rule["back_severity"]))
        if f["type"] in schemas.FRONTLESS_TYPES:
            continue
        d = r.front_dir(pid)
        dist = front_wall_distance(p, r, d)
        if dist is not None:
            out.append(_violation("F4", pid, r.id, f"{f['type']} faces a wall {dist:.2f} m in front of it",
                                  dict({"front_deg": _front_deg(p), "front_wall_m": dist}, **assumed)))
            continue
        backs = [tid for tid in targets if behind_back(r, pid, tid)]
        if backs:
            # U13 (real02 f_L1_029): an armchair behind a sofa's back, looking at it, "faces" nothing it can use.
            out.append(_violation("F4", pid, r.id, f"{f['type']} stands behind the back of "
                                  f"{', '.join(backs)}, looking at it", dict({"front_deg": _front_deg(p),
                                                                              "behind": backs}, **assumed)))
        elif faced is False:
            angles = {tid: faces(r, pid, tid)[1] for tid in targets}
            out.append(_violation("F4", pid, r.id, f"{f['type']} does not face its group ({', '.join(targets)})",
                                  dict({"front_deg": _front_deg(p), "targets": targets, "angles_deg": angles},
                                       **assumed)))
    return out


# --------------------------------------------------------------------------
# F5 -> the group checks (Milestone 12)
# --------------------------------------------------------------------------

def _f5(r: _Room) -> list[dict]:
    """The group checks G1–G13 of the room (``group_checks``), F5's place: arrangements, not counts. The headboard
    part of G5 is left to F3 (one finding per fault)."""
    view = GC.RoomView(r.building, r.room)
    out = []
    for v in GC.check_view(view, only=GROUP_CHECKS):
        if v["check"] == "G5" and (v.get("metrics") or {}).get("part") == "headboard":
            continue
        out.append(v)
    return out


# --------------------------------------------------------------------------
# F6, F7, R3: clearances, walkways, doors, windows (the placer's zones)
# --------------------------------------------------------------------------

def _f6_f7_r3(r: _Room) -> list[dict]:
    out = []
    ids = [f["id"] for f in r.floor]
    pieces = [r.pieces[pid] for pid in ids]
    for i, p in enumerate(pieces):
        p.index = i
    polys = [r.polys[pid] for pid in ids]
    room_area = r.polygon.buffer(0.01, join_style="mitre")
    # A module built into a counter of the room (a hob, an under-counter fridge) sits inside its host: the host's own
    # F7 / R3 finding covers the door, a second one for the module would count the same counter twice.
    hosted = {f["id"] for f in r.floor if f.get("built_into") in set(ids)}
    for pid, p, poly in zip(ids, pieces, polys):
        item = r.item(pid)
        if p.type in FU.ACCESS_M and pid not in hosted:
            out += _f6_access(r, pid, p, ids, polys)
        if p.type in F6_TYPES:
            zone = p.front_zone()
            exempt = set(schemas.CLEARANCE_EXEMPT.get(p.type, ())) | set(EXTRA_EXEMPT.get(p.type, ()))
            outside = zone.difference(room_area).area
            blockers = [oid for oid, o, op in zip(ids, pieces, polys)
                        if oid != pid and o.type not in exempt and zone.intersection(op).area > AREA_MIN_M2]
            if outside > AREA_MIN_M2 or blockers:
                what = (f"blocked by {', '.join(blockers)}" if blockers else "reaches out of the room")
                out.append(_violation("F6", pid, r.id, f"{p.type}: the free zone in front of it is {what}",
                                      dict({"blockers": blockers, "outside_m2": round(outside, 3),
                                            "zone_m": schemas.CLEARANCE_DEPTH_M.get(p.type,
                                                                                    placer.CLEARANCE_FRONT_M)},
                                           **_assumed(item))))
        # a stair is entered through its opening; a hosted module is judged with its counter
        for door in (r.ctx.doors if p.type != "stair" and pid not in hosted else []):
            if poly.intersection(door.zone).area > AREA_MIN_M2:
                out.append(_violation("F7", pid, r.id, f"{p.type} blocks door {door.id}",
                                      {"door": door.id, "area_m2": round(poly.intersection(door.zone).area, 3)}))
    for door in r.ctx.doors:
        if door.swing is None or door.swing.is_empty:
            continue
        hits = [pid for pid, p, poly in zip(ids, pieces, polys) if p.type != "stair" and pid not in hosted
                and poly.intersection(door.swing).area > AREA_MIN_M2]
        if hits:
            # M11 (pod G1, synthetic-01): no drawing gives the hinge side, and the half disc covers both. Critical
            # only when the leaf hits a piece on either hinge; else minor (the leaf is built closed and the door can hinge on
            # the free jamb).
            per_hinge = [[pid for pid, p, poly in zip(ids, pieces, polys) if p.type != "stair" and pid not in hosted
                          and poly.intersection(q).area > AREA_MIN_M2] for q in door.hinge_swings()]
            free = [i for i, h in enumerate(per_hinge) if not h]
            if per_hinge and free:
                out.append(_violation("R3", door.id, r.id, f"door {door.id} swings into {', '.join(hits)} on one "
                                      "hinge side; the other hinge side is free", {"pieces": hits,
                                      "free_hinge": free[0]}, severity="minor"))
            else:
                out.append(_violation("R3", door.id, r.id, f"door {door.id} swings into {', '.join(hits)}",
                                      {"pieces": hits}))
    return out                     # Milestone 12: the walkways are G11 (group_checks), the window bands G12


def _f6_access(r: _Room, pid: str, p: placer.Piece, ids: list[str], polys: list) -> list[dict]:
    """29 Oct 2026 (lesson UL92, ``fixture_use.access_problem``): the access zone in front of a door-fronted appliance
    or a nightstand (its width x its type's access depth) free of walls, fixed pieces and furniture (light movable
    pieces and a counter it is built into aside): critical when its door or drawers cannot open, major when it cannot
    be used. A front into a wall closer than ``schemas.FRONT_WALL_MIN_M`` is F4's finding (one finding per fault); a
    piece of a kitchen counter run is G8's (the run's aisle, with its small-kitchen tiers)."""
    if front_wall_distance(p, r, r.front_dir(pid)) is not None or FU.in_run(r.item(pid), r.built):
        return []
    obstacles = [(oid, r.item(oid)["type"], [tuple(c) for c in list(op.exterior.coords)[:-1]])
                 for oid, op in zip(ids, polys) if oid != pid and getattr(op, "exterior", None) is not None]
    prob = FU.access_problem(p.type, p.center, p.rotation_deg, p.size, list(r.ring.coords), obstacles)
    if prob is None:
        return []
    item = r.item(pid)
    return [_violation("F6", pid, r.id, FU.describe(item, prob),
                       dict({"part": "access", "free_m": prob["free_m"], "open_m": prob["open_m"],
                             "use_m": prob["use_m"], "blockers": prob["blockers"], "wall": prob["wall"],
                             "front_deg": _front_deg(p)}, **_assumed(item)), severity=prob["severity"])]


# --------------------------------------------------------------------------
# F8, F9
# --------------------------------------------------------------------------

def touches_wall(r: _Room, pid: str) -> bool:
    return r.polys[pid].exterior.distance(r.ring) <= SIDE_WALL_M + 1e-9


def _unbuilt_partner(r: _Room, pid: str, types, reach: float) -> Optional[dict]:
    """Milestone 13: the nearest drawn partner of ``types`` within ``reach`` that the fit did not build."""
    poly = r.polys[pid]
    best = None
    for f in unbuilt_drawn(r):
        if f["type"] not in types:
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        d = other.distance(poly)
        if d <= reach + 1e-9 and (best is None or (round(d, 4), f["id"]) < best[0]):
            best = ((round(d, 4), f["id"]), f)
    return best[1] if best else None


def _f8(r: _Room) -> list[dict]:
    out = []
    for f in r.built:
        pid = f["id"]
        if pid not in r.pieces:
            continue
        rule = schemas.orientation_rule(f["type"])
        if rule["back"] != "free" or not rule["partners"]:
            continue
        if touches_wall(r, pid) or _targets(r, pid, rule["partners"], rule["partner_m"]):
            continue
        missing = _unbuilt_partner(r, pid, rule["partners"], rule["partner_m"])
        if missing is not None:
            # Milestone 13: the finding names the real defect (the anchor the fit left unbuilt), not the chair.
            why = _not_built_reason(missing)
            out.append(_violation("F8", pid, r.id, f"{f['type']} stands around {missing['type']} {missing['id']}, "
                                  f"which is not built ({why[:100]})",
                                  {"partner_m": rule["partner_m"], "missing_anchor": missing["id"],
                                   "anchor_type": missing["type"], "cause": "anchor_not_built", "reason": why}))
            continue
        out.append(_violation("F8", pid, r.id, f"{f['type']} stands alone in the room (no wall, no "
                              f"{' / '.join(rule['partners'][:3])} within {rule['partner_m']:.1f} m)",
                              {"partner_m": rule["partner_m"]}))
    return out


def _tucked(a: str, b: str) -> bool:
    return (a in TUCKED_TYPES and b in UNDER_TYPES) or (b in TUCKED_TYPES and a in UNDER_TYPES)


def tucked_on_legs(r: "_Room", a: str, b: str) -> Optional[dict]:
    """30 Oct 2026 (lesson UL178, user on real04 run 20261030-112241-full: "Table seems to be going through the
    chairs"): the F9 of a seat tucked under a legged table that reaches into the table's corner legs
    (``clashes.on_legs``: the clash rule's measure, architect F5), None when it keeps clear of them."""
    from wenart.blender import clashes as CL

    for seat, table in ((a, b), (b, a)):
        fs, ft = r.item(seat), r.item(table)
        if fs["type"] not in CL.SEATS or ft["type"] not in CL.LEGGED_TABLES:
            continue
        depth = CL.on_legs(CL.shape(fs), ft)
        if depth > CL.LEG_TOL_M:
            return _violation("F9", seat, r.id, f"{fs['type']} {seat} stands in the corner legs of {ft['type']} "
                              f"{table} ({depth:.2f} m into a leg): tucked only between the legs",
                              {"other": table, "leg_depth_m": round(depth, 3), "cause": "table_legs"})
    return None


def _dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _run_held(r: _Room) -> set:
    """Fix round after P4a (module docstring): the pairs ``frozenset({run id, piece id})`` a kitchen run of the room
    holds by its fitted module plan: every ``plan.gaps`` record (a stove or a pinned sink standing in the run's gap)
    and every ``plan.built_ins`` record whose piece's ``asset.built_in`` names that run (both sides, as
    ``wenart.blender.furniture.built_in_ids``: a plan the agent refitted without the sink, or a sink naming another
    run, holds nothing)."""
    by_id = {f["id"]: f for f in r.floor}
    held: set = set()
    # 26 Oct 2026: a hob or an under-counter fridge the completion built into a counter (``built_into``, the solver's
    # ``built_in_kitchen``) is held by it before any fit has planned the run
    for f in r.floor:
        if f.get("built_into") in by_id and isinstance(f.get("built_in"), dict):
            held.add(frozenset((f["built_into"], f["id"])))
    for host in r.floor:
        plan = _dict(_dict(host.get("asset")).get("module_plan"))
        for rec in plan.get("gaps") or []:
            if isinstance(rec, dict) and rec.get("id") in by_id:
                held.add(frozenset((host["id"], rec["id"])))
        for rec in plan.get("built_ins") or []:
            if not isinstance(rec, dict) or rec.get("id") not in by_id:
                continue
            if _dict(by_id[rec["id"]].get("asset")).get("built_in") == host["id"]:
                held.add(frozenset((host["id"], rec["id"])))
    return held


def outside_depth(poly, outline) -> float:
    """Fix round after P4a: how far a footprint ``poly`` reaches past a room ``outline`` (metres): the largest
    distance of a corner of the part outside the outline from the outline; 0 when it stays inside."""
    part = poly.difference(outline)
    if part.is_empty:
        return 0.0
    best = 0.0
    for g in getattr(part, "geoms", [part]):
        ring = getattr(g, "exterior", None)
        coords = ring.coords if ring is not None else getattr(g, "coords", [])
        for c in coords:
            best = max(best, outline.distance(Point(c[0], c[1])))
    return best


def plan_shape(r: _Room, pid: str):
    """26 Oct 2026 (Argus consistency Y2, real06): the plan shape the clash rule (architect F5, ``blender.clashes``)
    measures: an L sofa is its two parts, not its bounding rectangle (four ottomans in the free corner of a corner
    sofa were an F9 overlap of 0.25 m² while F5 found them clear); every other piece its footprint."""
    item = r.item(pid)
    if str(item.get("type")) == "sofa_corner" or item.get("shape") == "L":
        try:
            from shapely.geometry import Polygon
            from shapely.ops import unary_union

            from wenart.blender import clashes as CL
            parts = [Polygon(q) for q in CL.shape(item)]
            if parts:
                return unary_union(parts)
        except Exception:  # noqa: BLE001 - the footprint then
            pass
    return r.polys[pid]


def _f9(r: _Room) -> list[dict]:
    out = []
    ids = [f["id"] for f in r.floor]
    held = _run_held(r)
    for i, a in enumerate(ids):
        ta = r.item(a)["type"]
        for b in ids[i + 1:]:
            tb = r.item(b)["type"]
            # fix round after P4a: a sink built into its run or a stove in its run's gap is no overlap
            if _tucked(ta, tb):
                legs = tucked_on_legs(r, a, b)
                if legs is not None:
                    out.append(legs)
                continue
            if frozenset((a, b)) in held:
                continue
            area = plan_shape(r, a).intersection(plan_shape(r, b)).area
            if area > OVERLAP_MIN_M2:
                out.append(_violation("F9", b, r.id, f"{tb} {b} overlaps {ta} {a} by {area:.2f} m²",
                                      {"other": a, "overlap_m2": round(area, 3)}))
    for f in (x for x in r.floor if x["type"] != "stair"):         # a stair runs into the storey opening
        outside = r.polys[f["id"]].difference(r.polygon).area
        if outside > OUTSIDE_MIN_M2:
            depth = outside_depth(r.polys[f["id"]], r.polygon)       # fix round after P4a: the cut's depth
            out.append(_violation("F9", f["id"], r.id, f"{f['type']} reaches {outside:.2f} m² through the room "
                                  f"outline, up to {depth:.3f} m deep",
                                  {"outside_m2": round(outside, 3), "depth_m": round(depth, 4)}))
    for f in r.built:
        if f["type"] != "unknown" or f["id"] not in r.polys:
            continue
        area = r.polys[f["id"]].area
        out.append(_violation("F9", f["id"], r.id, f"an unexplained drawn box ({area:.2f} m², type unknown) is built",
                              {"area_m2": round(area, 3)}, severity="major" if area >= UNKNOWN_LARGE_M2 else "minor"))
    return out


# --------------------------------------------------------------------------
# R1, R2
# --------------------------------------------------------------------------

def _r1(r: _Room) -> list[dict]:
    out = []
    area = float(r.room.get("area_computed") or r.polygon.area)
    floor = ROOM_MIN_M2.get(r.type)
    if floor is not None and area < floor[0]:
        out.append(_violation("R1", r.id, r.id, f"a {area:.1f} m² room is too small for a {r.type}",
                              {"area_m2": round(area, 2), "min_m2": floor[0]}, severity=floor[1]))
    if r.type in ("unknown",):
        return out
    seen = set()
    for f in r.built:
        rooms = FIXTURE_ROOMS.get(f["type"])
        if rooms is None or r.type in rooms or f["type"] in seen or f.get("source") != "from_documents":
            continue
        seen.add(f["type"])
        out.append(_violation("R1", r.id, r.id, f"a drawn {f['type']} ({f['id']}) says this is not a {r.type}",
                              {"fixture": f["id"], "room_types": list(rooms)}))
    return out


def _r2(r: _Room) -> list[dict]:
    level = next((lv for lv in r.building.get("levels") or [] if lv.get("id") == r.room.get("level_id")), None)
    if level is None or level.get("ceiling_height") is None:
        return []
    h = float(level["ceiling_height"])
    lo, hi = CEILING_RANGE_M
    if lo <= h <= hi:
        return []
    return [_violation("R2", r.id, r.id, f"ceiling height {h:.2f} m is outside {lo}-{hi} m", {"ceiling_m": h})]


# --------------------------------------------------------------------------
# Scores
# --------------------------------------------------------------------------

def penalty_of(violations: list[dict]) -> int:
    """The sum of the violations' weights (critical 30, major 10, minor 3)."""
    return sum(WEIGHTS[v["severity"]] for v in violations)


def score_of(violations: list[dict]) -> float:
    """100 minus the weights of the violations, floored at 0."""
    return float(max(0, 100 - penalty_of(violations)))


def room_violations(building: dict, room: dict) -> list[dict]:
    """Every violation of one room (see the module docstring), in check order."""
    if len(room.get("polygon") or []) < 3:
        return []
    r = _Room(building, room)
    out = []
    for fn in (_f1, _f2, _f3_f4, _f5, _f6_f7_r3, _f8, _f9, _r1, _r2):
        out.extend(fn(r))
    order = {k: i for i, k in enumerate(CHECKS)}
    return sorted(out, key=lambda v: (order.get(v["check"], 99), str(v["target"])))


def score_room(building: dict, room_id: str) -> dict:
    """``{"room_id", "score": 0..100, "violations": [Violation]}``; also ``penalty`` (the weights before the floor
    at 0: a room far below 0 still shows an edit that removes one violation)."""
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    violations = room_violations(building, room)
    return {"room_id": room_id, "score": score_of(violations), "violations": violations,
            "penalty": penalty_of(violations)}


def score_building(building: dict) -> dict:
    """``{"rooms": {room_id: score_room(...)}, "mean": float, "counts": {"critical": n, "major": n, "minor": n}}``."""
    rooms = {}
    counts = {s: 0 for s in SEVERITIES}
    for room in building.get("rooms") or []:
        res = score_room(building, room["id"])
        rooms[room["id"]] = res
        for v in res["violations"]:
            counts[v["severity"]] += 1
    mean = round(sum(r["score"] for r in rooms.values()) / len(rooms), 2) if rooms else 100.0
    return {"rooms": rooms, "mean": mean, "counts": counts}


def summary_lines(result: dict) -> list[str]:
    """A short text summary of ``score_building`` (rooms worst first, counts per check)."""
    by_check: dict[str, int] = {}
    for res in result["rooms"].values():
        for v in res["violations"]:
            by_check[v["check"]] = by_check.get(v["check"], 0) + 1
    lines = [f"mean score {result['mean']:.1f}; critical {result['counts']['critical']}, major "
             f"{result['counts']['major']}, minor {result['counts']['minor']}",
             "per check: " + ", ".join(f"{k} {by_check[k]}" for k in CHECKS if k in by_check)]
    for rid, res in sorted(result["rooms"].items(), key=lambda kv: (kv[1]["score"], kv[0])):
        lines.append(f"{rid}: {res['score']:.0f} ({len(res['violations'])} violations)")
    return lines
