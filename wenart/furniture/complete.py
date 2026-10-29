"""Completion of rooms with drawn furniture in functional groups (docs/milestone12.md §4.3-§4.5; Milestone 10 §2
before; CLAUDE.md furniture rules; owner: track G).

What: ``complete_building(building, style_text, client, settings)`` completes every room the documents furnish:
its program (``program.room_program``) matches the drawn pieces to groups first (a drawn sofa is the seating
anchor, a drawn bed the sleeping anchor, drawn sanitary ware the bathroom set, a drawn counter the kitchen run);
the group solver (``solver.solve_room``) keeps every drawn piece fixed and adds only what the groups miss: the
partners of a drawn anchor (nightstands at the head, a TV unit opposite a drawn sofa, chairs at a drawn table), the
missing members of a drawn set (a washbasin), a missing fridge beside a drawn run, and the groups the room type
misses whole (a wardrobe in a bedroom) - never a second anchor. The vision model picks one of the top candidates
(``layout.choose_candidate``; a failed answer takes the solver's best). Added pieces are ``added_by_ai`` with
``completes_room: true``, ``method: rule`` and their ``group``. Kitchens get wall cabinets along a drawn counter
run by rule. It returns the new building and one ``RoomCompletion`` per furnished room, written as
``completion.json``, ``completion_report.md`` and one PNG + JSON per room in the debug folder.

Why: Milestone 10/11 asked a text-only model for single pieces with coordinates and agreed type changes of drawn
pieces between two passes; the pieces were repaired one at a time and nightstands landed at mid-bed (§1.2). The
group solver places whole groups and the drawn pieces never move. Drawn pieces are not retyped or resized here any
more: reading (track R) types them and the agent's ``retype_piece`` / ``fix_fixture`` edits correct them.

How, per room (``furnished_rooms: complete``, documented furniture, a furnishable type, not in
``furnished_rooms_keep``; brief keys through ``wenart.brief.load_brief``):

1. ``classify_drawn`` sorts the drawn pieces (fixed equipment, not built, kept types, wall-mounted, changeable) for
   the record; every drawn piece is fixed for the solver.
2. The room's program and the solver's top candidates; candidates with hard failures are never applied; the choice
   of the vision model (or the solver's best); the chosen pieces are added.
3. Kitchens (and open kitchens of a living room): ``wall_cabinets_for`` hangs ``wall_cabinet`` pieces (``method:
   rule``, ``mount_bottom_m`` 1.45, ``rule: {run, z, excluded}``) along every drawn counter run against a wall,
   1.45-2.15 m, never over or within 0.3 m of a window or a door opening (measured along the wall), never over the
   stove, a tall piece (taller than 1.40 m) or another wall cabinet; runs shorter than 0.3 m are left out.
4. Looks (``apply_designs``): every piece of a completed or kept room gets ``design`` keys by rule under what it
   already holds: cabinet fronts, colour, handle and worktop from ``style.json`` ``cabinets`` (absent: none),
   ``vanity`` for a washbasin at least 0.45 m deep, ``built_in`` for a wardrobe touching walls at both ends,
   ``material_tags`` from ``style.json`` ``furniture.by_type``.
5. Groups (``tag_drawn_groups``): the drawn anchor and drawn partners of every furnished room get ``group = {group_id,
   group, role, anchor_id}`` (the program's ids, shared with the added partners; the fit reads it). Not a locked key.

Partners (asked once, §2.1): a room with ``same_as`` (an alternative level's room equal to a base room) takes its
partner's added pieces as they are; with ``render.twin_rooms: one`` a room with ``twin_of`` takes them mirrored
(``partner_transform``: the pipeline's ``rooms[].twin_transform`` when present, else the mirror about the
perpendicular bisector of the two room centroids; verified on the polygons and the drawn pieces within
``PARTNER_TOL_M``). Copied pieces carry ``mirrored_from`` and their group in this room (the group id with this
room's id, the anchor mapped onto this room's drawn piece). When a copy fails a placer check here (a door that opens
the other way in the twin) or the partner cannot be verified, the copy is not used: the room is completed itself and
the record says why (a whole group matters more than the same look in both rooms).
``copy_empty_layout`` does the same for the layout of empty rooms (user decision 7). ``completion.json`` keeps the
mode and the rooms kept as drawn (``locked.keep_rooms_of``, the refit's locked check).

Milestone 13 (docs/milestone13.md §1.4, §3.0 K3, §13.2; track T3; user decision D5 of 12 Oct 2026):

- **Code-first typing** before the solver: every drawn footprint still ``unknown`` that code can type (the twin
  room, another level, the block name, the room's missing group member: ``infer.code_types``) gets its type as a
  validated proposal (``type_proposal``, ``drawn_type`` unknown, ``adjusted_by_ai`` naming the method, the drawn
  footprint and status kept, so ``locked.check`` passes); not in ``keep`` mode and not in kept rooms. The record's
  ``typed_by_code`` and the building's warnings list them.
- **Drawn groups as one unit**: the program marks a drawn group whose anchor is missing, misread or fails the
  checks (``program.room_program`` ``resolve``); the solver re-solves it around the drawn anchor's centre (every
  member within ``groups.GROUP_MEMBER_MOVE_MAX_M``, ``adjusted_by_ai`` with the reason, ``drawn_footprint`` /
  ``drawn_front_deg`` / ``drawn_height`` kept, ``drawn_group`` written); the record's ``resolved`` lists the ids. Off
  with ``furnished_rooms: keep``, ``furnished_rooms_keep_size`` or a room in ``furnished_rooms_keep``. A twin or
  ``same_as`` partner whose completion moved its drawn group is not copied: the room is completed itself.

Fix round after P4b (17 Oct 2026; pod P4b, real03). What: after the code typing, a drawn corner sofa that carries no
L from the drawing (no ``shape``: it was typed by code, not by the L-outline rule) gets its chaise side from its drawn
coffee table (``infer.chaise_sides``): the side whose chaise leaves the table free when the other side's chaise
covers it; ``shape: L``, ``chaise_side``, ``chaise_depth``, ``inferred`` with the evidence, and a warning line. Not in
``keep`` mode and not in kept rooms. Why: real03's f_L0_190 (yasama) was typed ``sofa_corner`` by the group-member
rule, so it had no L; the fit took a right-chaise model and the scene put the chaise over the drawn coffee table
f_L0_191 (S2 0.099 m, F9 0.26 m², G2 in every agent round). With the chaise on the left the table stands in the open
corner, as in the six living rooms whose L the reading measured. The reading's own L (the ingest) stays first.

Fix round of 26 Oct 2026 (user: "fix should be general"). What: before the solver, drawn dining tables that touch
with the same axes become one table (``groups.merge_touching_tables``: the largest takes the box of all, labelled
``adjusted_by_ai`` with the drawn values kept; the others stay as drawn with ``build: false`` and ``merged_into``);
not in kept rooms and not with ``furnished_rooms_keep_size``; a warning line names each merge. The record's
``critical`` lists a kitchen the completion left without a run (``layout.empty_kitchens``). An untyped unbuilt drawn
piece is no obstacle of a copied partner's pieces either (``floor_pieces``, as in the solver).

Kitchen and dressing completion of 26 Oct 2026 (user: "fix should be general"; real06 the test case: its kitchen
rendered "a bare base cabinet with an empty worktop: no hob" and without a fridge, its "Soyunma Odası" as a bare
shell). What: (1) a counter run that misses its hob gets one built into a counter and, where no floor place passes,
an under-counter fridge (``solver.built_in_kitchen``: ``built_into``, ``built_in`` = {kind, host, reason, ...}; the
record's ``built_ins`` and the report's "Built into the kitchen runs" say what went where and why, or why not, and
which fridge: on the floor beside the run or built in); (2) ``wall_cabinets_for`` hangs wall cabinets over every
counter run against a wall, drawn or added (``hang_wall_cabinets``; the layout calls it for a run it lays in an empty
kitchen), never over the hob (and so its hood space), a window or a door; brief ``kitchen_wall_cabinets: false``
switches them off (``Settings.wall_cabinets``); (3) a dressing room (``program.room_kind`` ``dressing``: its label or
its bedroom door) is completed even when the ingest typed it storage (``completion_skip_reason`` with the building);
(4) a twin room takes a partner's built-in module into its own mapped counter (``copy_added``). Why: the solver only
looked for a floor place for a missing fridge beside a drawn run and none for the hob (every agent complete_group
was refused), and wall cabinets hung only over drawn counters.

Kitchen design of 28 Oct 2026 (user on real04's kitchen: "Kitchen design could have been a lot better this is
terrible"; the wall cabinets "hang as separate boxes of odd widths with gaps and do not line up"). What:
``wall_cabinets_for`` measures the stretches exactly (no 1 cm cells), leaves the cooker hood's span free over every
stove (``hood_region``, the cabinets flush at its sides), keeps off every window and door with their gaps, reaches
along the wall past a counter's end to meet another run's cabinets at the corner, records what ends each stretch
(``rule.ends``: hood, window, door, wall, corner_butt, corner_blind, open) for the fit's wall run of real units
(``modules.plan_wall_run``), and gives no band to a counter outline drawn inside another run
(``fit.nested_counters``); ``rule_design`` adds the family's kitchen look where ``style.json`` names none
(``looks.KITCHEN_FAMILY_LOOKS``). Why: real04's cabinets were 3.35 / 0.69 / 0.56 m boxes with a 0.76 m gap at the
stove (no hood) and a 0.25 m gap at the corner; real06's nested hob outline got a wall cabinet of its own.
"""
from __future__ import annotations

import copy
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from shapely.geometry import LineString, Point, Polygon

from wenart import building as B
from wenart import geometry as G
from wenart.furniture import locked as LK
from wenart.furniture import placer, schemas

EVIDENCE_FILE = "building.json"     # what the solver saw: the room, doors, windows and drawn pieces
PASSES = 2                          # Milestone 10 argument, accepted and not used
# Partners: the polygon and every drawn piece within this distance (the pipeline matches twins within 2 cm;
# 5 cm here leaves room for rounding), the fronts within this angle.
PARTNER_TOL_M = 0.05
PARTNER_FRONT_TOL_DEG = 2.0
# Wall cabinets (§4.4).
WALL_CABINET_DEPTH_M = 0.35
WALL_CABINET_MIN_M = 0.30
WALL_CABINET_WINDOW_GAP_M = 0.30
WALL_CABINET_DOOR_GAP_M = 0.30       # §4.4 (contract amendment 1): never over a door opening or within 0.3 m
WALL_CABINET_STEP_M = 0.01
WALL_FACE_REACH_M = 0.10             # the wall face behind a counter's back edge is looked for this far
# 28 Oct 2026 (module docstring "Kitchen design"): a wall run whose counter ends short of another run's wall cabinets
# reaches along the wall this far to meet them at the corner (a counter leg's depth and a cabinet's); an end this close
# to the room's outline ends at a wall.
WALL_CABINET_CORNER_REACH_M = 0.70
WALL_CABINET_WALL_END_M = 0.03
STATES = ("completed", "copied", "mirrored", "kept", "skipped")


# --------------------------------------------------------------------------
# Settings (brief keys, docs/milestone10.md §1.3)
# --------------------------------------------------------------------------

@dataclass
class Settings:
    mode: str = "complete"                  # furnished_rooms: keep | complete
    keep: tuple[str, ...] = ()              # furnished_rooms_keep: room ids or labels
    keep_size: bool = False                 # furnished_rooms_keep_size
    twin_rooms: str = "one"                 # render.twin_rooms: one | all
    assumed: tuple[str, ...] = ()           # the keys above taken from wenart/defaults.yaml
    brief_path: Optional[str] = None
    warnings: tuple[str, ...] = ()
    # 26 Oct 2026: brief ``kitchen_wall_cabinets: false`` leaves the counter runs without wall cabinets (default: hung)
    wall_cabinets: bool = True

    KEYS = ("furnished_rooms", "furnished_rooms_keep", "furnished_rooms_keep_size", "render.twin_rooms")

    @classmethod
    def from_brief(cls, loaded: dict) -> "Settings":
        """From a ``wenart.brief.load_brief`` result."""
        from wenart import brief as BR

        return cls(mode=str(BR.value(loaded, "furnished_rooms", "complete")),
                   keep=tuple(str(v) for v in BR.value(loaded, "furnished_rooms_keep", []) or []),
                   keep_size=bool(BR.value(loaded, "furnished_rooms_keep_size", False)),
                   twin_rooms=str(BR.value(loaded, "render.twin_rooms", "one")),
                   assumed=tuple(k for k in loaded.get("assumed", []) if k in cls.KEYS),
                   brief_path=loaded.get("path"), warnings=tuple(loaded.get("warnings", [])),
                   wall_cabinets=BR.value(loaded, "kitchen_wall_cabinets", True) is not False)

    def to_dict(self) -> dict:
        return {"furnished_rooms": self.mode, "furnished_rooms_keep": list(self.keep),
                "furnished_rooms_keep_size": self.keep_size, "render.twin_rooms": self.twin_rooms,
                "kitchen_wall_cabinets": self.wall_cabinets,
                "assumed": list(self.assumed), "brief": self.brief_path, "warnings": list(self.warnings)}

    def brief_values(self) -> dict:
        """The brief keys the program reads (Milestone 13: ``program.resolve_allowed`` switches the drawn-group
        re-solve off with ``keep`` / ``furnished_rooms_keep_size`` / a kept room)."""
        return {"furnished_rooms": self.mode, "furnished_rooms_keep": list(self.keep),
                "furnished_rooms_keep_size": self.keep_size}


def load_settings(project_dir) -> Settings:
    from wenart import brief as BR

    return Settings.from_brief(BR.load_brief(project_dir))


# --------------------------------------------------------------------------
# Rooms and partners
# --------------------------------------------------------------------------

def _label_key(text: str) -> str:
    return B.fold_ascii(B.turkish_lower(str(text))).strip()


def is_kept(room: dict, settings: Settings) -> bool:
    """The room is in ``furnished_rooms_keep`` (by id, or by label ignoring case and Turkish letters)."""
    names = {_label_key(k) for k in settings.keep}
    return room["id"] in settings.keep or _label_key(room.get("label", "")) in names


def furnished_rooms(building: dict) -> list[dict]:
    return [r for r in building["rooms"] if r.get("has_documented_furniture")]


def dressing_kind(room: dict, building: Optional[dict]) -> bool:
    """26 Oct 2026: the room is read as a dressing room or walk-in closet (``program.room_kind``: its label words or
    its bedroom door), whatever its building-schema type (storage, other)."""
    if building is None:
        return False
    from wenart.furniture import program as PR

    return PR.room_kind(building, room) == "dressing"


def completion_skip_reason(room: dict, settings: Settings, building: Optional[dict] = None) -> Optional[str]:
    """Why a furnished room is not completed (None: it is). ``building`` (26 Oct 2026): a storage room read as a
    dressing room (``dressing_kind``) is completed."""
    rtype = room.get("room_type")
    if settings.mode != "complete":
        return f"furnished_rooms: {settings.mode} (drawn furniture only restyled, Milestone 9)"
    if rtype in schemas.NOT_FURNISHED_ROOM_TYPES:
        return f"{rtype} room: never furnished by AI"
    if rtype not in schemas.ALLOWED_TYPES and not dressing_kind(room, building):
        return f"room type {rtype}: no furniture types to complete"
    if is_kept(room, settings):
        return "in furnished_rooms_keep: drawn furniture only restyled"
    return None


def partner_of(room: dict, settings: Settings) -> Optional[tuple[str, str]]:
    """``(partner room id, "same_as" | "twin")`` of a room that takes its partner's decisions, else None."""
    if room.get("same_as"):
        return room["same_as"], "same_as"
    if room.get("twin_of") and settings.twin_rooms == "one":
        return room["twin_of"], "twin"
    return None


@dataclass
class Transform:
    """The map from a partner room onto this room as an affine ``[a, b, c, d, e, f]`` (``x' = a x + b y + c``,
    ``y' = d x + e y + f``, as ``wenart.geometry.apply_affine``): the identity (``same_as``), a mirror about an
    axis (twins, derived here) or the pipeline's ``rooms[].twin_transform``."""
    kind: str                                   # identity | mirror | given
    m6: tuple = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    origin: Optional[tuple[float, float]] = None   # mirror: a point on the axis
    axis_deg: Optional[float] = None               # mirror: the direction of the axis
    deviation_m: float = 0.0                    # the largest polygon / piece distance after the map

    @classmethod
    def mirror(cls, origin, axis_deg: float) -> "Transform":
        a = math.radians(2.0 * axis_deg)
        c2, s2 = math.cos(a), math.sin(a)          # reflection matrix [[c2, s2], [s2, -c2]] about the axis
        ox, oy = float(origin[0]), float(origin[1])
        m6 = (c2, s2, ox - (c2 * ox + s2 * oy), s2, -c2, oy - (s2 * ox - c2 * oy))
        return cls("mirror", m6, (ox, oy), G.normalise_angle(axis_deg))

    @property
    def flips(self) -> bool:
        a, b, _c, d, e, _f = self.m6
        return a * e - b * d < 0

    def point(self, p) -> tuple[float, float]:
        return G.apply_affine(self.m6, (float(p[0]), float(p[1])))

    def direction(self, deg: Optional[float]) -> Optional[float]:
        if deg is None:
            return None
        a, b, _c, d, e, _f = self.m6
        r = math.radians(float(deg))
        x, y = math.cos(r), math.sin(r)
        return G.normalise_angle(round(math.degrees(math.atan2(d * x + e * y, a * x + b * y)), 9))

    def rotation(self, rotation_deg: float) -> float:
        """Footprint rotation of the mapped piece (front = local -Y: the front direction maps, the width axis
        follows)."""
        return G.normalise_angle(self.direction(G.front_direction_deg(rotation_deg)) - 270.0)

    def side(self, side: Optional[str]) -> Optional[str]:
        if side is None or not self.flips:
            return side
        return {"left": "right", "right": "left"}[side]

    def to_dict(self) -> dict:
        out = {"kind": self.kind, "affine": [round(v, 6) for v in self.m6], "deviation_m": round(self.deviation_m, 4)}
        if self.origin is not None:
            out.update(origin=[round(self.origin[0], 4), round(self.origin[1], 4)], axis_deg=round(self.axis_deg, 3))
        return out


def given_transform(room: dict) -> Optional[Transform]:
    """The pipeline's ``rooms[].twin_transform`` (first twin -> this room) as a ``Transform``, else None. Taken as
    a 6-number affine, a 3x3 matrix or ``{"affine" | "matrix": ...}``."""
    value = room.get("twin_transform")
    if isinstance(value, dict):
        value = value.get("affine") or value.get("m6") or value.get("matrix")
    if value is None:
        return None
    try:
        if len(value) == 3 and all(isinstance(r, (list, tuple)) for r in value):
            value = G.matrix_to_affine(value)
        m6 = tuple(float(v) for v in value)
    except (TypeError, ValueError):
        return None
    return Transform("given", m6) if len(m6) == 6 else None


def _hausdorff(a: list, b: list) -> float:
    return Polygon(a).exterior.hausdorff_distance(Polygon(b).exterior)


def _pieces_in(building: dict, room_id: str, source: str = "from_documents") -> list[dict]:
    return [f for f in building["furniture"] if f.get("room_id") == room_id and f.get("source") == source]


def match_pieces(partner_pieces: list[dict], pieces: list[dict], t: Transform) -> tuple[Optional[dict], str, float]:
    """``({partner id: piece id}, reason, deviation)``: every partner piece mapped onto one piece of the same type
    and size, centre within ``PARTNER_TOL_M`` and front within ``PARTNER_FRONT_TOL_DEG``."""
    if len(partner_pieces) != len(pieces):
        return None, f"{len(partner_pieces)} drawn pieces in the partner, {len(pieces)} here", 0.0
    free = list(pieces)
    out, worst = {}, 0.0
    for p in partner_pieces:
        c = t.point(p["footprint"]["center"])
        front = t.direction(p.get("front_deg"))
        best = None
        for q in free:
            if q["type"] != p["type"]:
                continue
            d = G.distance(c, q["footprint"]["center"])
            sizes = zip(sorted(p["footprint"]["size"]), sorted(q["footprint"]["size"]))
            if d > PARTNER_TOL_M or any(abs(float(x) - float(y)) > PARTNER_TOL_M for x, y in sizes):
                continue
            qf = q.get("front_deg")
            if (front is None) != (qf is None) or (front is not None and
                                                   G.angle_difference_deg(front, qf) > PARTNER_FRONT_TOL_DEG):
                continue
            if best is None or d < best[0]:
                best = (d, q)
        if best is None:
            return None, f"drawn {p['type']} {p['id']} has no counterpart here", 0.0
        free.remove(best[1])
        out[p["id"]] = best[1]["id"]
        worst = max(worst, best[0])
    return out, "", worst


def partner_transform(room: dict, partner: dict, kind: str, building: dict) -> tuple[Optional[Transform], str]:
    """The map partner -> room, verified on the polygons and the drawn pieces; ``(None, reason)`` when it fails."""
    if kind == "same_as":
        t = Transform("identity")
    elif given_transform(room) is not None:
        t = given_transform(room)                       # the pipeline's twin_transform wins over the derivation
    else:
        ca, cb = G.polygon_centroid(partner["polygon"]), G.polygon_centroid(room["polygon"])
        if G.distance(ca, cb) < 1e-6:
            return None, "twin rooms with the same centroid: no mirror axis"
        n = math.atan2(cb[1] - ca[1], cb[0] - ca[0])
        mid = ((ca[0] + cb[0]) / 2.0, (ca[1] + cb[1]) / 2.0)
        t = Transform.mirror(mid, math.degrees(n) + 90.0)
    mapped = [t.point(p) for p in partner["polygon"]]
    dev = _hausdorff(mapped, room["polygon"])
    if dev > PARTNER_TOL_M:
        return None, f"the {kind} polygon does not map onto this room ({dev:.3f} m > {PARTNER_TOL_M} m)"
    mapping, why, worst = match_pieces(_pieces_in(building, partner["id"]), _pieces_in(building, room["id"]), t)
    if mapping is None:
        return None, f"the {kind}'s drawn furniture does not map onto this room: {why}"
    t.deviation_m = max(dev, worst)
    return t, ""


# --------------------------------------------------------------------------
# Drawn pieces and the record of one room
# --------------------------------------------------------------------------

@dataclass
class Drawn:
    item: dict                   # the building furniture dict as given
    kind: str                    # fixed | obstacle | kept | mounted | changeable | other | outline (M11)
    anchor: dict
    piece: Optional[placer.Piece] = None      # front frame; against_wall from the anchor
    unverified: bool = False

    @property
    def id(self) -> str:
        return self.item["id"]


def classify_drawn(room: dict, building: dict) -> list[Drawn]:
    """The room's drawn pieces (and any other piece already there) in building order, with their kind and anchor
    (``locked.anchor_of``); the solver keeps all of them where they are."""
    out = []
    for f in (p for p in building["furniture"] if p.get("room_id") == room["id"]):
        if f.get("source") != "from_documents":
            kind = "other"
        elif f["type"] in schemas.MOUNTED_TYPES:
            kind = "mounted"
        elif f.get("inferred_as") == "rug":
            kind = "outline"          # Milestone 11 (infer.py): a rug / zone outline: not built, no obstacle
        elif f.get("build") is False:
            kind = "obstacle"
        elif f["type"] in schemas.FIXED_TYPES:
            kind = "fixed"
        elif f["type"] in schemas.UNCHANGEABLE_TYPES:
            kind = "kept"
        else:
            kind = "changeable"
        anchor = LK.anchor_of(f, building)
        piece = placer.drawn_piece(f, len(out), against_wall=anchor["kind"] == "back_edge")
        unverified = (f.get("status") == "unverified" or f["type"] == "unknown") and kind == "changeable"
        out.append(Drawn(f, kind, anchor, piece, unverified))
    return out


@dataclass
class RoomCompletion:
    room: dict
    state: str = "completed"
    reason: str = ""
    partner: Optional[dict] = None              # {"id", "kind", "transform"}
    drawn: list = field(default_factory=list)   # Drawn
    program: Optional[dict] = None
    candidates: list = field(default_factory=list)
    choice: Optional[dict] = None
    chosen: Optional[int] = None
    changes: list = field(default_factory=list)   # Milestone 10 field, always empty now (drawn pieces never change)
    added: list = field(default_factory=list)     # final furniture dicts
    refused: list = field(default_factory=list)
    dropped: list = field(default_factory=list)
    wall_cabinets: list = field(default_factory=list)
    solve_s: float = 0.0
    context: Optional[placer.RoomContext] = None
    # Milestone 13 (D5): the drawn pieces re-solved as one unit (ids) and the pieces code typed before the solve.
    resolved: list = field(default_factory=list)
    typed_by_code: list = field(default_factory=list)
    # 26 Oct 2026: kitchens the completion left without a run (``layout.empty_kitchens``; critical findings)
    critical: list = field(default_factory=list)
    # 26 Oct 2026: what was built into the kitchen runs (a hob, an under-counter fridge; the floor fridge the solver
    # placed) and why, or why not (``solver.built_in_kitchen`` records)
    built_ins: list = field(default_factory=list)

    @property
    def room_id(self) -> str:
        return self.room["id"]

    @property
    def passes(self) -> list[dict]:
        """The model call of the room as the Milestone 10 records had it (one entry or none)."""
        c = self.choice or {}
        if not c.get("model") and not c.get("error"):
            return []
        return [{"pass": 1, "model": c.get("model"), "latency_s": c.get("latency_s", 0.0), "error": c.get("error"),
                 "transport_error": bool(c.get("transport_error"))}]

    @property
    def transport_errors(self) -> list[tuple[int, str]]:
        return [(p["pass"], p["error"]) for p in self.passes if p.get("transport_error")]

    @property
    def latency_s(self) -> float:
        return round(float((self.choice or {}).get("latency_s") or 0.0), 3)

    @property
    def missing(self) -> list[str]:
        """What the program found missing: the partner types the drawn groups lack and the required groups no
        drawn piece holds (the Milestone 10 record's ``missing``)."""
        out: list[str] = []
        for g in (self.program or {}).get("groups", []):
            if g.get("drawn"):
                out += list(g.get("missing") or [])
            elif g.get("required"):
                out.append(g["group"])
        return out

    def drawn_layout(self) -> dict:
        """``{"pieces": {id: [placer checks it fails as drawn]}}``: what the drawn layout already breaks (walkways
        are G11's), so the added pieces are not blamed for it."""
        ctx = self.context
        floor = [d for d in self.drawn if d.kind not in ("mounted", "outline") and d.piece is not None]
        if ctx is None or not floor:
            return {"pieces": {}}
        checks = placer.check_all([d.piece for d in floor], ctx, walkways=False)
        return {"pieces": {d.id: placer.failed_checks(c) for d, c in zip(floor, checks) if placer.failed_checks(c)}}

    def to_dict(self) -> dict:
        from wenart.furniture import layout as L

        return {
            "room_id": self.room_id, "label": self.room["label"], "room_type": self.room.get("room_type"),
            "room_subtype": self.room.get("room_subtype"), "state": self.state, "reason": self.reason,
            "partner": self.partner,
            "drawn": [{"id": d.id, "type": d.item["type"], "kind": d.kind, "anchor": d.anchor} for d in self.drawn],
            "program": [{k: g.get(k) for k in ("group_id", "group", "options", "drawn", "required", "missing", "note")}
                        for g in (self.program or {}).get("groups", [])],
            "candidates": [L.candidate_summary(c) for c in self.candidates], "chosen": self.chosen,
            "choice": {k: v for k, v in (self.choice or {}).items() if k not in ("prompt", "raw_text")},
            "passes": self.passes, "chosen_pass": self.chosen, "changes": self.changes,
            "added": [{"id": f["id"], "type": f["type"], "center": f["footprint"]["center"],
                       "size": f["footprint"]["size"], "rotation_deg": f["footprint"]["rotation_deg"],
                       "group": (f.get("group") or {}).get("group"), "method": f.get("method"),
                       "mirrored_from": f.get("mirrored_from")} for f in self.added],
            "refused": self.refused, "dropped": self.dropped,
            "resolved": list(self.resolved), "typed_by_code": list(self.typed_by_code),
            "critical": list(self.critical), "built_ins": list(self.built_ins),
            "wall_cabinets": [{"id": f["id"], "run": f["rule"]["run"], "size": f["footprint"]["size"],
                               "excluded": f["rule"]["excluded"]} for f in self.wall_cabinets],
            "missing": self.missing, "drawn_layout": self.drawn_layout(),
            "latency_s": self.latency_s, "solve_s": round(self.solve_s, 3),
        }


# --------------------------------------------------------------------------
# Wall cabinets along a drawn counter run (§4.4, rule)
# --------------------------------------------------------------------------

def _opening_box(op: dict, building: dict) -> Polygon:
    """The opening's plan rectangle through its wall (width x wall thickness + 2 cm): a gap to it is measured
    along the wall."""
    c = (float(op["center"][0]), float(op["center"][1]))
    wall = next((w for w in building.get("walls", []) if w["id"] == op.get("wall_id")), None)
    if wall is not None and G.distance(wall["start"], wall["end"]) > 1e-9:
        a = math.atan2(wall["end"][1] - wall["start"][1], wall["end"][0] - wall["start"][0])
        t = float(wall.get("thickness") or placer.DEFAULT_WALL_THICKNESS_M)
    else:
        a, t = 0.0, placer.DEFAULT_WALL_THICKNESS_M
    h = float(op["width"]) / 2.0
    start = (c[0] - math.cos(a) * h, c[1] - math.sin(a) * h)
    end = (c[0] + math.cos(a) * h, c[1] + math.sin(a) * h)
    return Polygon(G.centerline_to_rectangle(start, end, t + 0.02))


def _height(item: dict) -> float:
    h = item.get("height")
    return float(h) if h is not None else schemas.HEIGHTS.get(item["type"], 1.0)


def _x_extent(c, rot: float, geom) -> Optional[tuple[float, float]]:
    """The extent along a frame's local x (centre ``c``, rotation ``rot``) of a polygonal geometry, None if empty."""
    if geom is None or geom.is_empty or geom.area <= placer.AREA_EPS:
        return None
    r = math.radians(rot)
    xs = [(pt[0] - c[0]) * math.cos(r) + (pt[1] - c[1]) * math.sin(r)
          for g in getattr(geom, "geoms", [geom]) if hasattr(g, "exterior") for pt in g.exterior.coords]
    return (min(xs), max(xs)) if xs else None


def hood_region(stove: dict) -> Optional[Polygon]:
    """28 Oct 2026 (module docstring "Kitchen design"): the plan area of the cooker hood over a stove: the stove's
    footprint widened to the hood's width (``modules.hood_width_for``, centred on the stove) and reaching
    ``WALL_FACE_REACH_M`` + a wall cabinet's depth behind it (the wall band the wall cabinets hang in)."""
    from wenart.blender import modules as MOD

    try:
        rot, size = placer.front_frame(stove["footprint"], stove.get("front_deg"))
        c = (float(stove["footprint"]["center"][0]), float(stove["footprint"]["center"][1]))
    except (KeyError, TypeError, ValueError):
        return None
    hw = MOD.hood_width_for(float(size[0]))
    return placer._local_box(c, rot, -hw / 2.0, hw / 2.0, -size[1] / 2.0,
                             size[1] / 2.0 + WALL_FACE_REACH_M + WALL_CABINET_DEPTH_M)


def _spans_minus(lo: float, hi: float, spans: list) -> list[tuple[float, float, str, str]]:
    """The free stretches of ``[lo, hi]`` between the blocking ``spans`` ``(x0, x1, kind, name)``, each with the kind
    of what ends it on either side (``end`` at ``lo`` / ``hi``)."""
    out, x, kind = [], lo, "end"
    for s0, s1, k, _n in sorted(spans):
        if s0 - x > 1e-6:
            out.append((x, min(s0, hi), kind, k))
            x, kind = s1, k
        elif s1 > x:
            x, kind = s1, k
    if hi - x > 1e-6:
        out.append((x, hi, kind, "end"))
    return out


def wall_cabinets_for(room: dict, building: dict, items: list[dict]) -> list[dict]:
    """Wall cabinet runs ``{"run", "center", "size", "rotation_deg", "excluded", "ends"}`` along every drawn counter
    run against a wall in ``room`` (``items``: the room's final furniture dicts).

    28 Oct 2026 (module docstring "Kitchen design"; user on real04's kitchen: the wall cabinets "hang as separate boxes
    of odd widths with gaps and do not line up"). What: the free stretches are measured exactly (no 1 cm cells): the
    wall band of each counter minus every window and door with its gap (``WALL_CABINET_WINDOW_GAP_M``: never a cabinet
    over any part of a window or glazed door), every tall piece and the cooker hood's span over every stove
    (``hood_region``: the hood's width, the cabinets stop at its sides, the hood between them); a stretch whose
    counter ends short of another run's wall cabinets reaches along the wall to meet them at the corner (at most
    ``WALL_CABINET_CORNER_REACH_M``, over free wall inside the room). Each stretch records what ends it on either
    side (``ends``, the cabinet's frame: ``hood``, ``window``, ``door``, ``wall`` (a wall or a tall unit's side),
    ``corner_butt`` (it ends against another run's front), ``corner_blind`` (it runs into the corner behind the other
    run), ``open``): the fit builds it of real wall units lined up with the base units (``modules.plan_wall_run``)."""
    room_poly = Polygon(room["polygon"])
    ring = room_poly.exterior
    doors, windows = placer.room_openings(building, room)
    blocked = [(f"window {w['id']}", _opening_box(w, building).buffer(WALL_CABINET_WINDOW_GAP_M, join_style="mitre"),
                "window") for w in windows]
    blocked += [(f"door {d['id']}", _opening_box(d, building).buffer(WALL_CABINET_DOOR_GAP_M, join_style="mitre"),
                 "door") for d in doors]
    blocked += [(f"{f['type']} {f['id']}", placer.drawn_piece(f).polygon(), "wall") for f in items
                if f["type"] not in schemas.MOUNTED_TYPES and f.get("build") is not False and f["type"] != "stove"
                and _height(f) > schemas.WALL_CABINET_Z[0] - 0.05]
    blocked += [(f"stove {f['id']}", region, "hood") for f in items
                if f["type"] == "stove" and f.get("build") is not False and f.get("footprint")
                for region in [hood_region(f)] if region is not None]
    # 29 Oct 2026 (wenart.blender.kitchen_details, K1): the tall units a counter run's plan holds (a fridge or oven
    # column to the ceiling) end a wall cabinet as a tall piece does
    from wenart.blender import kitchen_details as KD
    blocked += [(f"tall unit of {f['id']}", Polygon(G.rotated_rectangle(c, s, r)), "wall") for f in items
                if f["type"] in ("kitchen_counter", "kitchen_island") and f.get("build") is not False
                for c, s, r in KD.tall_unit_rects(f)]
    # 26 Oct 2026 (user: "fix should be general"): every built counter run against a wall, drawn or added (a run the
    # solver laid in an empty kitchen, a compact fallback run); before, only drawn counters got wall cabinets
    # 28 Oct 2026: a counter outline drawn inside another run is part of it (``fit.nested_counters``): no band of its own
    from wenart.furniture import fit as FT
    nested = FT.nested_counters(dict(building, furniture=items))
    counters = [f for f in items if f["type"] == "kitchen_counter" and f.get("source") in ("from_documents",
                                                                                          "added_by_ai")
                and f.get("build") is not False and f.get("front_deg") is not None and f.get("footprint")
                and f["id"] not in nested]
    bands = []
    for counter in sorted(counters, key=lambda f: f["id"]):
        if LK.anchor_of(counter, building)["kind"] != "back_edge":
            continue
        rot, size = placer.front_frame(counter["footprint"], counter.get("front_deg"))
        c = (float(counter["footprint"]["center"][0]), float(counter["footprint"]["center"][1]))
        w, d = size
        mid = placer.back_edge_midpoint(c, rot, size)
        back = math.radians(rot + 90.0)
        ray = LineString([mid, (mid[0] + math.cos(back) * WALL_FACE_REACH_M, mid[1] + math.sin(back) * WALL_FACE_REACH_M)])
        hit = ray.intersection(ring)
        offset = 0.0 if hit.is_empty else Point(mid).distance(hit)     # the cabinet's back on the wall face
        y1 = d / 2.0 + offset
        bands.append({"counter": counter, "c": c, "rot": rot, "w": w, "y0": y1 - WALL_CABINET_DEPTH_M, "y1": y1})

    def strip(band, xa, xb):
        return placer._local_box(band["c"], band["rot"], xa, xb, band["y0"], band["y1"])

    def spans_in(band, xa, xb, extra=()):
        region = strip(band, xa, xb)
        out = []
        for name, geom, kind in list(blocked) + list(extra):
            ext = _x_extent(band["c"], band["rot"], region.intersection(geom))
            if ext is not None:
                out.append((ext[0], ext[1], kind, name))
        return out

    stretches: list[dict] = []
    for band in bands:
        taken = [(f"wall cabinet over {s['band']['counter']['id']}", s["poly"], "corner_butt") for s in stretches]
        spans = spans_in(band, -band["w"] / 2.0, band["w"] / 2.0, taken)
        excluded = sorted({n for _a, _b, _k, n in spans})
        for x0, x1, k0, k1 in _spans_minus(-band["w"] / 2.0, band["w"] / 2.0, spans):
            if x1 - x0 < WALL_CABINET_MIN_M - 1e-9:
                continue
            stretches.append({"band": band, "x0": x0, "x1": x1, "ends": [k0, k1], "excluded": excluded,
                              "poly": strip(band, x0, x1)})
    # a stretch that stops at its counter's end short of another run's wall cabinets reaches along the wall to them
    for s in stretches:
        band = s["band"]
        for side in (0, 1):
            if s["ends"][side] != "end":
                continue
            edge = s["x1"] if side else s["x0"]
            far = edge + WALL_CABINET_CORNER_REACH_M if side else edge - WALL_CABINET_CORNER_REACH_M
            region = strip(band, min(edge, far), max(edge, far))
            near = None
            for t in stretches:
                if t["band"] is band:
                    continue
                ext = _x_extent(band["c"], band["rot"], region.intersection(t["poly"]))
                if ext is not None:
                    near = (min(near, ext[0]) if near is not None else ext[0]) if side else \
                        (max(near, ext[1]) if near is not None else ext[1])
            if near is None or abs(near - edge) < 1e-6:
                continue
            reach = strip(band, min(edge, near), max(edge, near))
            if spans_in(band, min(edge, near), max(edge, near)) or not room_poly.buffer(0.02).contains(reach):
                continue
            if side:
                s["x1"] = near
            else:
                s["x0"] = near
            s["poly"] = strip(band, s["x0"], s["x1"])
            s["ends"][side] = "corner_butt"
    # what ends each stretch: another run's cabinets (a butt, and a blind corner on the run behind it), a wall, open
    for s in stretches:
        band = s["band"]
        for side in (0, 1):
            x = s["x1"] if side else s["x0"]
            point = Point(G.rotate_point((band["c"][0] + x, band["c"][1] + (band["y0"] + band["y1"]) / 2.0),
                                         band["rot"], band["c"]))
            others = [t for t in stretches if t["band"] is not band and t["poly"].distance(point) < 0.02]
            if others and s["ends"][side] in ("end", "corner_butt"):
                s["ends"][side] = "corner_butt"
                for t in others:
                    tb = t["band"]
                    for tside in (0, 1):
                        tx = t["x1"] if tside else t["x0"]
                        tp = Point(G.rotate_point((tb["c"][0] + tx, tb["c"][1] + (tb["y0"] + tb["y1"]) / 2.0),
                                                  tb["rot"], tb["c"]))
                        if s["poly"].distance(tp) <= WALL_CABINET_DEPTH_M + 0.05 and t["ends"][tside] in ("end",
                                                                                                         "wall"):
                            t["ends"][tside] = "corner_blind"
            elif s["ends"][side] == "end":
                beyond = Point(G.rotate_point((band["c"][0] + x + (WALL_CABINET_WALL_END_M if side else
                                                                   -WALL_CABINET_WALL_END_M),
                                               band["c"][1] + (band["y0"] + band["y1"]) / 2.0), band["rot"], band["c"]))
                s["ends"][side] = "open" if room_poly.contains(beyond) else "wall"
    out = []
    for s in stretches:
        band = s["band"]
        x0, x1, c, rot = s["x0"], s["x1"], band["c"], band["rot"]
        centre = G.rotate_point((c[0] + (x0 + x1) / 2.0, c[1] + (band["y0"] + band["y1"]) / 2.0), rot, c)
        out.append({"run": band["counter"]["id"], "center": [round(centre[0], 4), round(centre[1], 4)],
                    "size": [round(x1 - x0, 4), WALL_CABINET_DEPTH_M], "rotation_deg": round(rot, 4),
                    "excluded": s["excluded"], "ends": [("open" if k == "end" else k) for k in s["ends"]],
                    "design": {k: v for k, v in (band["counter"].get("design") or {}).items()
                               if k in ("front_style", "colour", "handle")}})
    return out


def add_wall_cabinets(rec: RoomCompletion, building: dict, out: dict) -> None:
    rec.wall_cabinets += hang_wall_cabinets(rec.room, building, out)


def hang_wall_cabinets(room: dict, building: dict, out: dict) -> list[dict]:
    """The wall cabinets of ``wall_cabinets_for`` added to ``out`` (changed in place) for every counter run of
    ``room`` against a wall; returns the new pieces. Nothing when the room has drawn wall cabinets (the documents
    decide) or already holds added ones (asked twice)."""
    items = [f for f in out["furniture"] if f.get("room_id") == room["id"]]
    if any(f["type"] == "wall_cabinet" for f in items):
        return []                       # drawn wall cabinets: the documents decide; added ones: hung already
    from wenart.furniture import layout as L

    added = []
    number = L._next_furniture_number(out, room["level_id"])
    for spec in wall_cabinets_for(room, building, items):
        lo, hi = schemas.WALL_CABINET_Z
        f = {"id": B.element_id("furniture", room["level_id"], number), "level_id": room["level_id"],
             "room_id": room["id"], "type": "wall_cabinet", "type_raw": None, "source": "added_by_ai",
             "footprint": {"center": spec["center"], "size": spec["size"], "rotation_deg": spec["rotation_deg"]},
             "front_deg": G.front_direction_deg(spec["rotation_deg"]), "height": round(hi - lo, 3), "asset": None,
             "status": "verified", "completes_room": True, "method": "rule", "mount_bottom_m": lo,
             "evidence": [B.evidence(EVIDENCE_FILE, "derived", 1.0, text=(
                 f"wall cabinets along the counter run {spec['run']} (rule, docs/milestone10.md §4.4), {lo:.2f}-"
                 f"{hi:.2f} m" + (f"; left free: {', '.join(spec['excluded'])}" if spec["excluded"] else "")))],
             "rule": {"run": spec["run"], "z": [lo, hi], "excluded": spec["excluded"],
                      # 28 Oct 2026: what ends the stretch on either side (modules.plan_wall_run reads it)
                      "ends": list(spec.get("ends") or ["open", "open"])}}
        if spec["design"]:
            f["design"] = spec["design"]
        out["furniture"].append(f)
        added.append(f)
        number += 1
    return added


# --------------------------------------------------------------------------
# Completing one room
# --------------------------------------------------------------------------

def complete_room(room: dict, building: dict, out: dict, style_text: str, client, settings: Settings,
                  passes: int = PASSES, family: Optional[str] = None, image_dir: Optional[Path] = None
                  ) -> RoomCompletion:
    """Program, solver, choice and labels of one room; ``out`` (the building being written) is changed in place.
    ``passes`` and ``family`` are accepted for the Milestone 10 callers and not used."""
    from wenart.furniture import layout as L

    rec = RoomCompletion(room)
    rec.context = placer.room_context(building, room)
    rec.drawn = classify_drawn(room, out)
    lay = L.layout_room(room, out, style_text, client, image_dir, purpose="complete", settings=settings)
    rec.program, rec.candidates, rec.choice, rec.chosen, rec.solve_s = (lay.program, lay.candidates, lay.choice,
                                                                        lay.chosen, lay.solve_s)
    rec.added = list(lay.pieces)
    rec.resolved = list(lay.resolved)
    rec.critical = list(lay.critical)          # 26 Oct 2026: a kitchen left without a run (layout.empty_kitchens)
    rec.built_ins = list(lay.built_ins)        # 26 Oct 2026: the hob / fridge built into a run (or why not)
    if lay.skipped:
        rec.reason = lay.skipped
    elif not rec.added:
        rec.reason = "nothing to add"
    for c in rec.candidates[:1]:
        rec.dropped += [{"type": x["group"], "reason": x["reason"], "group_id": x["group_id"]}
                        for x in c.get("not_placed", [])]
    if settings.wall_cabinets:                  # any room with a counter run (a kitchen, an open kitchen)
        add_wall_cabinets(rec, building, out)
    return rec


# --------------------------------------------------------------------------
# Partners: copied (same_as) or mirrored (twin) rooms
# --------------------------------------------------------------------------

def _map_footprint(fp: dict, t: Transform) -> dict:
    c = t.point(fp["center"])
    return {"center": [round(c[0], 4), round(c[1], 4)], "size": list(fp["size"]),
            "rotation_deg": round(t.rotation(float(fp["rotation_deg"])), 4)}


def _map_group(group, room_id: str, partner_id: str, ids: dict):
    """The partner's group membership in this room: the group id with this room's id, the anchor id mapped
    (``ids``: partner piece id -> piece id here; an anchor without a counterpart is dropped)."""
    if not isinstance(group, dict):
        return group
    g = dict(group)
    gid = str(g.get("group_id") or "")
    if gid.startswith(partner_id + "."):
        g["group_id"] = room_id + gid[len(partner_id):]
    if g.get("anchor_id") is not None:
        g["anchor_id"] = ids.get(g["anchor_id"])
    return g


def copy_added(room: dict, partner_id: str, partner_added: list[dict], t: Transform, obstacles: list[placer.Piece],
               out: dict, ctx: placer.RoomContext, ids: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """The partner's added pieces mapped into ``room``; each must pass the placer's checks here with the drawn pieces
    as obstacles (no repairs: a failing copy is dropped and listed). ``ids`` maps the partner's drawn pieces onto this
    room's (group anchors). Returns ``(added dicts, dropped)``.
    Fix round after P6a (22 Oct 2026): under a sloped ceiling a copy also needs the solver's headroom
    (``solver.headroom_short``: its type's height + 0.05 m under the ceiling over its footprint); a copy without it
    is dropped like any failing copy, so the room is completed itself. Why: the twin of a room under the roof takes
    its pieces through the placer's checks, not the solver's (P6a real04: the mirrored bookshelf f_L1_056)."""
    from wenart.furniture import layout as L
    from wenart.furniture import solver as SV

    fixed = placer.obstacles_for(obstacles, ctx)
    room_ctx = placer.drawn_context(ctx, fixed) if fixed else ctx
    copies = []
    built = []                 # 26 Oct 2026: modules built into a counter (a hob, an under-counter fridge)
    for f in partner_added:
        if f.get("built_into"):
            built.append(f)
            continue
        fp = _map_footprint(f["footprint"], t)
        piece = placer.Piece(f["type"], tuple(fp["center"]), float(fp["rotation_deg"]),
                             (float(fp["size"][0]), float(fp["size"][1])),
                             bool((f.get("layout") or {}).get("against_wall", False)))
        if f.get("shape") == "L":
            piece.shape, piece.chaise_side, piece.chaise_depth = "L", t.side(f.get("chaise_side")), f.get("chaise_depth")
            piece.seat_depth, piece.chaise_width = f.get("seat_depth"), f.get("chaise_width")
        copies.append((f, fp, piece))
    dropped = []
    planes = SV.headroom_planes(out, room["level_id"])         # fix round after P6a: [] under a flat ceiling
    if planes:
        fitting = []
        for f, fp, piece in copies:
            why = SV.headroom_short(out, room["level_id"], f["type"], piece.polygon(), planes)
            if why is None:
                fitting.append((f, fp, piece))
            else:
                dropped.append({"type": f["type"], "mirrored_from": f["id"], "center": f["footprint"]["center"],
                                "reason": f"the copy lacks headroom here: {why}"})
        copies = fitting
    checks: list[dict] = []
    while True:
        pieces = fixed + [p for _f, _fp, p in copies]
        checks = placer.obstacle_checks(pieces, room_ctx)[len(fixed):]
        bad = [i for i, c in enumerate(checks) if placer.failed_checks(c)]
        if not bad:
            break
        f, _fp, _p = copies.pop(bad[-1])
        dropped.append({"type": f["type"], "mirrored_from": f["id"], "center": f["footprint"]["center"],
                        "reason": "the copy fails " + ", ".join(placer.failed_checks(checks[bad[-1]])) + " here"})
    # 26 Oct 2026: a built-in module goes into the counter its host maps onto (``ids``: the partner's drawn pieces ->
    # this room's), never through the floor checks (it lies in its counter); it must lie in that counter here
    ids = dict(ids or {})
    here = {f["id"]: f for f in out["furniture"] if f.get("room_id") == room["id"]}
    built_copies = []
    for f in built:
        fp = _map_footprint(f["footprint"], t)
        host = here.get(ids.get(f["built_into"]) or "")
        poly = placer.drawn_piece({"type": f["type"], "footprint": fp, "front_deg": None}).polygon()
        if host is None:
            why = f"its counter {f['built_into']} has no counterpart here"
        elif not placer.drawn_piece(host).polygon().buffer(0.01, join_style="mitre").contains(poly):
            why = f"it does not lie in the counter {host['id']} here"
        else:
            built_copies.append((f, fp, host["id"]))
            continue
        dropped.append({"type": f["type"], "mirrored_from": f["id"], "center": f["footprint"]["center"],
                        "reason": f"the built-in copy fails here: {why}"})
    number = L._next_furniture_number(out, room["level_id"])
    for f, _fp, _p in copies:
        ids[f["id"]] = B.element_id("furniture", room["level_id"], number)
        number += 1
    for f, _fp, _host in built_copies:
        ids[f["id"]] = B.element_id("furniture", room["level_id"], number)
        number += 1
    copies += [(f, fp, None) for f, fp, _host in built_copies]
    checks = list(checks) + [{name: True for name in placer.CHECKS} for _ in built_copies]
    hosts = {f["id"]: host for f, _fp, host in built_copies}
    added = []
    for (f, fp, _p), c in zip(copies, checks):
        g = copy.deepcopy(f)
        g.update(id=ids[f["id"]], level_id=room["level_id"], room_id=room["id"], footprint=fp,
                 front_deg=G.front_direction_deg(fp["rotation_deg"]), checks=dict(c), mirrored_from=f["id"], asset=None)
        if "group" in f:
            g["group"] = _map_group(f.get("group"), room["id"], partner_id, ids)
        if isinstance(g.get("layout"), dict):
            g["layout"] = dict(g["layout"], copied_from=f["id"])
        if f.get("shape") == "L":
            g["chaise_side"] = t.side(f.get("chaise_side"))
        if f["id"] in hosts:
            g["built_into"] = hosts[f["id"]]
            g["built_in"] = dict(g.get("built_in") or {}, host=hosts[f["id"]])
            if isinstance(g.get("layout"), dict):
                g["layout"]["built_into"] = hosts[f["id"]]
        out["furniture"].append(g)
        added.append(g)
    return added, dropped


def floor_pieces(drawn: list[Drawn]) -> list[placer.Piece]:
    """The drawn pieces that stand on the floor (obstacles of copies), in building order. 26 Oct 2026: not an
    untyped unbuilt piece (``solver.untyped_unbuilt``: in no render, no obstacle of the solver either)."""
    from wenart.furniture import solver as SV

    return [d.piece for d in drawn if d.kind not in ("mounted", "outline") and not SV.untyped_unbuilt(d.item)]


def copy_room(room: dict, partner_rec: RoomCompletion, kind: str, t: Transform, building: dict, out: dict,
              settings: Settings) -> RoomCompletion:
    """This room takes the partner's completion: the partner's added pieces mapped here (their group anchors mapped
    onto this room's drawn pieces), the wall cabinet rule run here. Drawn pieces never change."""
    rec = RoomCompletion(room, state="mirrored" if kind == "twin" else "copied")
    rec.partner = {"id": partner_rec.room_id, "kind": kind, "transform": t.to_dict()}
    rec.reason = f"decisions of {partner_rec.room_id} ({kind}), not asked again"
    ctx = placer.room_context(building, room)
    rec.context = ctx
    rec.drawn = classify_drawn(room, out)
    mapping, _why, _dev = match_pieces(_pieces_in(building, partner_rec.room_id), _pieces_in(building, room["id"]), t)
    rec.added, rec.dropped = copy_added(room, partner_rec.room_id, list(partner_rec.added), t, floor_pieces(rec.drawn),
                                        out, ctx, ids=mapping)
    if settings.wall_cabinets:                  # any room with a counter run (a kitchen, an open kitchen)
        add_wall_cabinets(rec, building, out)
    return rec


def copy_empty_layout(room: dict, partner: dict, kind: str, partner_pieces: list[dict], building: dict,
                      out: dict) -> tuple[Optional[list[dict]], list[dict], dict]:
    """Layout of an empty partner room mapped into ``room`` (user decision 7).
    Returns ``(added dicts or None when the partner does not map, dropped, record)``."""
    t, why = partner_transform(room, partner, kind, building)
    if t is None:
        return None, [], {"room": partner["id"], "kind": kind, "reason": why}
    ctx = placer.room_context(building, room)
    added, dropped = copy_added(room, partner["id"], partner_pieces, t, [], out, ctx)
    return added, dropped, {"room": partner["id"], "kind": kind, "transform": t.to_dict()}


# --------------------------------------------------------------------------
# Looks (furniture.design, docs/milestone10.md §1.6b row 15, §4.4)
# --------------------------------------------------------------------------

def _slot(style: Optional[dict], *keys):
    cur = style
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def spans_wall_to_wall(item: dict, building: dict) -> bool:
    """A wardrobe whose two ends (the midpoints of its side edges) touch a wall or the room outline within 5 cm:
    a built-in wardrobe (§4.4)."""
    rot, size = placer.front_frame(item["footprint"], item.get("front_deg"))
    c = (float(item["footprint"]["center"][0]), float(item["footprint"]["center"][1]))
    ends = [Point(G.rotate_point((c[0] + sx * size[0] / 2.0, c[1]), rot, c)) for sx in (-1.0, 1.0)]
    shapes = [shape for _id, shape in LK._wall_shapes(building, item.get("level_id"))]
    room = next((r for r in building.get("rooms", []) if r["id"] == item.get("room_id")), None)
    if room is not None and len(room.get("polygon") or []) >= 3:
        shapes.append(Polygon(room["polygon"]).exterior)
    return bool(shapes) and all(min(sh.distance(e) for sh in shapes) <= placer.WALL_TOUCH_M + 1e-9 for e in ends)


def rule_design(item: dict, building: dict, style: Optional[dict]) -> dict:
    """The look keys a piece gets by rule: cabinet fronts, colour, handle and worktop from ``style.json``
    ``cabinets`` (absent: none); ``vanity`` for a washbasin at least 0.45 m deep; ``built_in`` for a wardrobe
    from wall to wall; ``material_tags`` from ``style.json`` ``furniture.by_type.<type>.material_tags`` (the
    schema's tags only). Values of the wrong kind are left out, never guessed."""
    out: dict = {}
    ftype = item["type"]
    cab = _slot(style, "cabinets")
    if ftype in schemas.CABINET_TYPES and isinstance(cab, dict):
        front = cab.get("front_style", cab.get("front"))
        if front in schemas.FRONT_STYLES:
            out["front_style"] = front
        if isinstance(cab.get("colour"), str) and cab["colour"].strip():
            out["colour"] = cab["colour"].strip()
        if cab.get("handle") in schemas.HANDLES:
            out["handle"] = cab["handle"]
        if ftype in schemas.WORKTOP_TYPES and cab.get("worktop") in schemas.WORKTOPS:
            out["worktop"] = cab["worktop"]
    # 28 Oct 2026 (user on real04's kitchen: the fronts and handles "look plain"): where style.json names no cabinet
    # look, the family's kitchen look (looks.KITCHEN_FAMILY_LOOKS; the build applies the same)
    if ftype in schemas.CABINET_TYPES:
        from wenart.blender import looks as LO
        extra, _notes = LO.kitchen_family_look(ftype, style, out)
        out.update({k: v for k, v in extra.items() if v in schemas.FRONT_STYLES + schemas.HANDLES + schemas.WORKTOPS})
    if ftype == "washbasin":
        _rot, size = placer.front_frame(item["footprint"], item.get("front_deg"))
        if size[1] >= schemas.VANITY_MIN_DEPTH_M - 1e-9:
            out["vanity"] = True
    if ftype == "wardrobe" and spans_wall_to_wall(item, building):
        out["built_in"] = True
    tags = _slot(style, "furniture", "by_type", ftype, "material_tags")
    if isinstance(tags, list):
        clean = [t for t in dict.fromkeys(str(v) for v in tags) if t in schemas.MATERIAL_TAGS]
        if clean:
            out["material_tags"] = clean
    return out


def apply_designs(out: dict, records: list[RoomCompletion], style: Optional[dict]) -> int:
    """``design`` for every piece of a completed, copied, mirrored or kept room: the rule keys under what the piece
    already holds (the agreed AI style and colour win). Returns the number of pieces given a look."""
    rooms = {r.room_id for r in records if r.state in ("completed", "copied", "mirrored", "kept")}
    n = 0
    for f in out["furniture"]:
        if f.get("room_id") not in rooms:
            continue
        extra = rule_design(f, out, style)
        if extra:
            f["design"] = {**extra, **(f.get("design") or {})}
            n += 1
    return n


# --------------------------------------------------------------------------
# Whole building
# --------------------------------------------------------------------------

def complete_building(building: dict, style_text: str, client, settings: Settings, passes: int = PASSES,
                      debug_dir: Optional[Path] = None, family: Optional[str] = None,
                      style: Optional[dict] = None) -> tuple[dict, list[RoomCompletion]]:
    """Complete every furnished room (new dict; the input is not changed). Rooms whose partner is completed take
    the partner's added pieces; a partner that does not map is reported and the room is completed itself. ``style``
    (the ``style.json`` profile) gives the looks (``apply_designs``). ``passes`` and ``family`` are accepted for
    the Milestone 10 callers and not used."""
    out = copy.deepcopy(building)
    image_dir = Path(debug_dir) if debug_dir is not None else None
    records: dict[str, RoomCompletion] = {}
    order: list[str] = []
    pending: list[tuple[dict, tuple[str, str]]] = []
    rooms_by_id = {r["id"]: r for r in out["rooms"]}
    # Milestone 13 (T3): code-first typing of the drawn footprints still untyped (twin / level / block / missing
    # group member) before the solver sees them: an untyped piece is never built and blocks its room. Not in
    # ``keep`` mode and not in kept rooms (their drawn pieces stay byte-equal); the type is a proposal with the
    # drawn footprint and status kept (``locked.check``).
    typed: dict[str, list] = {}
    if settings.mode != "keep":
        from wenart.furniture import infer as INF

        kept_ids = {r["id"] for r in out["rooms"] if is_kept(r, settings)}
        props = [p for p in INF.code_types(out) if next((f.get("room_id") for f in out["furniture"]
                                                         if f["id"] == p["piece_id"]), None) not in kept_ids]
        if props:
            by_id = {f["id"]: f for f in out["furniture"]}
            for p in props:
                INF._apply_code_type(by_id[p["piece_id"]], p, proposal=True)
                typed.setdefault(by_id[p["piece_id"]].get("room_id"), []).append(
                    {"id": p["piece_id"], "type": p["type"], "method": p["type_method"], "reason": p["reason"]})
            out["warnings"] = list(out.get("warnings", [])) + [
                f"{p['piece_id']}: typed {p['type']} by code ({p['type_method']}): {p['reason']}" for p in props]
        # Fix round after P4b (module docstring): the chaise side of a drawn corner sofa without the drawing's L
        chaise = [p for p in INF.chaise_sides(out) if next((f.get("room_id") for f in out["furniture"]
                                                            if f["id"] == p["piece_id"]), None) not in kept_ids]
        if chaise:
            INF.apply_chaise_sides(out, chaise)
            out["warnings"] = list(out.get("warnings", [])) + [
                f"{p['piece_id']}: inferred {p['reason']}" for p in chaise]
        # 26 Oct 2026 (fix C): drawn tables that touch are one table (groups.merge_touching_tables); not in kept rooms
        # and not with furnished_rooms_keep_size (program.resolve_allowed: the drawn sizes stay)
        from wenart.furniture import groups as GR
        from wenart.furniture import program as PR

        rooms = [r["id"] for r in out["rooms"] if r["id"] not in kept_ids
                 and PR.resolve_allowed(out, r, settings.brief_values())[0]]
        for m in GR.merge_touching_tables(out, rooms):
            out["warnings"] = list(out.get("warnings", [])) + [f"{m['table_id']}: adjusted_by_ai: {m['reason']}"]

    def solve(room: dict) -> RoomCompletion:
        rec = complete_room(room, building, out, style_text, client, settings, passes, family, image_dir)
        rec.typed_by_code = list(typed.get(room["id"], []))
        return rec

    for room in furnished_rooms(out):
        order.append(room["id"])
        skip = completion_skip_reason(room, settings, out)
        if skip:
            records[room["id"]] = RoomCompletion(room, state="kept" if "keep" in skip else "skipped", reason=skip)
            continue
        partner = partner_of(room, settings)
        if partner is not None and partner[0] in rooms_by_id:
            pending.append((room, partner))
            continue
        records[room["id"]] = solve(room)
    while pending:
        progress = False
        for item in list(pending):
            room, (pid, kind) = item
            prec = records.get(pid)
            if prec is None and any(r[0]["id"] == pid for r in pending):
                continue                                         # the partner is a copy itself: later
            pending.remove(item)
            progress = True
            if prec is not None and prec.state not in ("completed", "copied", "mirrored"):
                records[room["id"]] = RoomCompletion(room, state="kept", reason=(
                    f"partner {pid} ({kind}) not completed ({prec.reason}): kept as drawn so both stay the same"))
                continue
            if prec is not None and prec.resolved:
                # Milestone 13: the partner moved its drawn group; a copy would leave this room's drawn pieces where
                # they are drawn, so the room is re-solved itself.
                rec = solve(room)
                rec.reason = (rec.reason + "; " if rec.reason else "") + (
                    f"partner {pid} ({kind}) not used: it re-solved its drawn group ({', '.join(prec.resolved[:4])}); "
                    "completed itself")
                records[room["id"]] = rec
                continue
            t, why = (None, f"{pid} has no drawn furniture") if prec is None else \
                partner_transform(room, rooms_by_id[pid], kind, building)
            if t is None:
                rec = solve(room)
                note = f"partner {pid} ({kind}) not used: {why}; completed itself"
                rec.reason = (rec.reason + "; " if rec.reason else "") + note
                records[room["id"]] = rec
                continue
            count = len(out["furniture"])
            rec = copy_room(room, prec, kind, t, building, out, settings)
            if rec.dropped:                                      # a copy would lose pieces: completed itself
                del out["furniture"][count:]
                dropped = rec.dropped
                rec = solve(room)
                note = (f"partner {pid} ({kind}) not used: {len(dropped)} of {len(prec.added)} copied pieces fail a "
                        "check here (" + "; ".join(f"{x['type']}: {x['reason']}" for x in dropped) + "); completed "
                        "itself")
                rec.reason = (rec.reason + "; " if rec.reason else "") + note
            records[room["id"]] = rec
        if not progress:                                         # a cycle of partners: complete the first one
            room, (pid, kind) = pending.pop(0)
            rec = solve(room)
            rec.reason = f"partner {pid} ({kind}) is itself waiting (a cycle): completed itself"
            records[room["id"]] = rec
    result = [records[rid] for rid in order]
    tag_drawn_groups(out, result)
    apply_designs(out, result, style)
    out["warnings"] = list(out.get("warnings", []))
    for rec in result:
        if rec.state == "completed" and rec.reason and not rec.added and not rec.wall_cabinets:
            out["warnings"].append(f"{rec.room_id}: completion added nothing, {rec.reason}")
        if debug_dir is not None:
            write_room_debug(rec, out, Path(debug_dir))
    return out, result


def tag_drawn_groups(out: dict, records: list[RoomCompletion]) -> int:
    """The drawn pieces of every furnished room get their group (``group = {group_id, group, role, anchor_id}``, the
    ids of the room's program, so the added partners and the drawn anchor share one group id; the fit picks related
    types by it). An unverified anchor is not tagged; a piece that already holds a group keeps it. Returns the count."""
    from wenart.furniture import program as PR

    by_id = {f["id"]: f for f in out["furniture"]}
    count = 0
    for rec in records:
        prog = rec.program if rec.program is not None else PR.room_program(out, rec.room_id)
        for entry in prog.get("groups", []):
            if not entry.get("drawn") or str(entry.get("note") or "").startswith("unverified"):
                continue
            anchor = entry.get("anchor_id")
            for pid, role in [(anchor, "anchor")] + [(m, "partner") for m in entry.get("members") or []]:
                f = by_id.get(pid)
                if f is None or f.get("source") != "from_documents" or isinstance(f.get("group"), dict):
                    continue
                f["group"] = {"group_id": entry["group_id"], "group": entry["group"], "role": role, "anchor_id": anchor}
                count += 1
    return count


# --------------------------------------------------------------------------
# Outputs: completion.json, completion_report.md, debug PNG + JSON per room
# --------------------------------------------------------------------------

def summary(records: list[RoomCompletion], building: dict, settings: Settings, server: str, model: str,
            violations: list[str]) -> dict:
    """``completion.json``: the mode and the kept rooms are what the refit's locked check reads
    (``locked.keep_rooms_of``)."""
    return {"kind": "completion", "project": building["project"]["id"], "server": server, "model": model,
            "settings": settings.to_dict(),
            "rooms": [r.to_dict() for r in records],
            "rooms_completed": sum(r.state == "completed" for r in records),
            "rooms_copied": sum(r.state in ("copied", "mirrored") for r in records),
            "changes_applied": 0,
            "pieces_added": sum(len(r.added) for r in records),
            "wall_cabinets": sum(len(r.wall_cabinets) for r in records),
            "locked_violations": list(violations),
            "latency_s": round(sum(r.latency_s for r in records), 3),
            "solve_s": round(sum(r.solve_s for r in records), 3)}


def _fmt_size(size) -> str:
    return " x ".join(f"{float(v):.2f}" for v in size)


def report(records: list[RoomCompletion], building: dict, settings: Settings, violations: list[str]) -> str:
    lines = [f"# AI completion of furnished rooms: {building['project']['id']}", "",
             f"Mode `furnished_rooms: {settings.mode}`, keep size {str(settings.keep_size).lower()}, twin rooms "
             f"`{settings.twin_rooms}`" + (f" (assumed: {', '.join(settings.assumed)})" if settings.assumed else "")
             + ". Drawn pieces stay as drawn; the group solver adds only what the room's groups miss (the partners "
             "of a drawn anchor, the missing members of a drawn set, the groups the room type misses whole); the "
             "vision model picks one of its top candidates (else the solver's best). Wall cabinets follow the rule "
             "of docs/milestone10.md §4.4.", "",
             "| Room | Type | State | Drawn groups | Candidates (score, hard) | Chosen | By | Added | Solve s | Note |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in records:
        drawn = ", ".join(g["group"] for g in (r.program or {}).get("groups", []) if g.get("drawn")) or "-"
        cands = ", ".join(f"#{c['rank']} {c['score']:.1f} {len(c['hard_failures'])}" for c in r.candidates) or "-"
        added = ", ".join(f["type"] for f in r.added + r.wall_cabinets) or "-"
        by = (r.choice or {}).get("by", "-")
        lines.append(f"| {r.room['label']} ({r.room_id}) | {r.room.get('room_type')} | {r.state} | {drawn} | {cands} | "
                     f"{r.chosen or '-'} | {by} | {added} | {r.solve_s:.2f} | {r.reason or '-'} |")
    added = [(r, f) for r in records for f in r.added + r.wall_cabinets]
    lines += ["", f"## Added pieces ({len(added)})", ""]
    if added:
        lines += ["| Room | Piece | Type | Group | Centre | Size | Method | From |", "|---|---|---|---|---|---|---|---|"]
        for r, f in added:
            c = f["footprint"]["center"]
            g = f.get("group") or {}
            group = f"{g.get('group')} ({g.get('role')}, anchor {g.get('anchor_id') or '-'})" if g else "-"
            lines.append(f"| {r.room_id} | {f['id']} | {f['type']} | {group} | [{c[0]:.2f}, {c[1]:.2f}] | "
                         f"{_fmt_size(f['footprint']['size'])} | {f.get('method')} | {f.get('mirrored_from') or '-'} |")
    built = [(r, b) for r in records for b in r.built_ins]
    if built:
        # 26 Oct 2026: what the kitchen runs took into themselves (or the floor fridge beside them), and why not
        lines += ["", f"## Built into the kitchen runs ({sum(1 for _r, b in built if b.get('placed'))} placed)", "",
                  "| Room | Module | Piece | Into | How | Reason |", "|---|---|---|---|---|---|"]
        for r, b in built:
            how = b.get("how") or ("built in" if b.get("placed") else "none")
            lines.append(f"| {r.room_id} | {b['kind']} | {b.get('id') or '-'} | {b.get('host') or '-'} | "
                         f"{how.replace('_', ' ')} | {b.get('reason') or '-'} |")
    choices = [(r, r.choice) for r in records if r.choice and r.choice.get("by") == "vlm"]
    if choices:
        lines += ["", "## Choices of the vision model", ""]
        lines += [f"- {r.room_id}: candidate {c['rank']}: {c.get('reason')}" for r, c in choices]
    missed = [(r, x) for r in records for x in r.dropped + r.refused]
    if missed:
        lines += ["", f"## Groups not completed and copies dropped ({len(missed)})", ""]
        for r, x in missed:
            where = f" at {x['center']}" if x.get("center") is not None else ""
            lines.append(f"- {r.room_id}: {x['type']}{where}: {x['reason']}")
    lines += ["", f"## Locked check: {'pass' if not violations else f'{len(violations)} violation(s)'}", ""]
    lines += [f"- {v}" for v in violations]
    return "\n".join(lines) + "\n"


def write_room_debug(rec: RoomCompletion, building: dict, debug_dir: Path) -> None:
    from wenart.furniture import layout as L

    debug_dir.mkdir(parents=True, exist_ok=True)
    record = rec.to_dict()
    record["program_full"] = rec.program
    record["candidates_full"] = list(rec.candidates)
    (debug_dir / f"{rec.room_id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        if rec.candidates:
            source = dict(building, furniture=[f for f in building["furniture"] if f.get("source") == "from_documents"])
            L.draw_candidates_png(source, rec.room, rec.candidates, debug_dir / f"{rec.room_id}.png", rec.chosen)
        else:
            draw_room_png(rec, building, debug_dir / f"{rec.room_id}.png")
    except ImportError as exc:   # matplotlib missing: the JSON is the record, the PNG is a convenience
        print(f"complete: debug PNG for {rec.room_id} skipped ({exc})", file=sys.stderr)
    except Exception as exc:     # noqa: BLE001 - real03: an odd geometry must not fail the stage over a picture
        print(f"complete: debug PNG for {rec.room_id} not drawn ({type(exc).__name__}: {exc})", file=sys.stderr)


def draw_room_png(rec: RoomCompletion, building: dict, path: Path) -> None:
    """The room as completed: drawn pieces grey, added pieces (copies, wall cabinets) in their group's colour."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from wenart.furniture import layout as L

    source = dict(building, furniture=[f for f in building["furniture"] if f.get("source") == "from_documents"])
    fig, ax = plt.subplots(figsize=(6, 6))
    L._draw_room(ax, source, rec.room, {"pieces": rec.added + rec.wall_cabinets},
                 f"{rec.room['label']} ({rec.room_id}) {rec.state}: grey drawn, colour added")
    for x in rec.dropped:
        if x.get("center") is not None:
            ax.text(x["center"][0], x["center"][1], f"x {x['type']}", color="tab:red", ha="center", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)
