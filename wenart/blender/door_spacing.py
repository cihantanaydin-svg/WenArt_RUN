"""Doors side by side (27 Oct 2026, user on real06's dressing room: "doors next to each other not making sense").

What: ``conflicts(building)`` -> ``(records, doors checked)``: one record per pair of doors of one level that a
visitor cannot use as two doors (pure, on the building JSON):

- ``overlap``: their openings overlap on one wall line (critical);
- ``frames``: their frames touch: less than ``PAIR_GAP_M`` of wall between two doors on one wall line (a frame of
  ``FRAME_M`` beside each opening), or their frames (through the wall) meet at a corner; critical when both doors join
  the same two rooms (one passage drawn or read twice), else major;
- ``same_passage``: two doors between the same two rooms on one wall line closer than a door's width (major);
- ``swing``: the leaves of two swing doors into the same room sweep over each other (the door's width deep in front
  of it on its swing side, overlapping by ``SWING_SHARE`` of the smaller; major).

Each record names both doors, the rooms each joins, the gap, and the door a decision made from another drawn type
(``made_by``: the answer key of its ``corrected_by_ai``), so the fix is clear: a door a decision made beside a door
goes back to its drawn type (Argus revokes the AI's decision, ``act_window_to_door`` refuses it), two drawn doors of
one passage become one opening (the architect's O1 merges them); a corner clash is reported.

Passages (27 Oct 2026, user: "Not every opening inside the house requires a door or a window"): ``needless(building)``
-> ``(records, openings checked)``: the openings inside the house (two rooms, neither open-air) that got what they do
not need: ``needless_leaf`` (a passage drawn with no leaf and no swing arc that a decision made a door, though neither
room needs privacy: ``PRIVACY_ROOMS``), ``needless_glass`` (such a passage made a window; a serving window over a
drawn counter is a need) and ``needless_guard`` (a guard across an opening between two rooms on one floor: no drop).
Each names the decision that gave it (``made_by``), so Argus revokes the AI's, and the architect's actions refuse them
(``act_gap_to_door``, ``act_door_to_window``, ``act_french_window``).

Why: real06's dressing room: the drawing has a door between the shower room and the dressing room with a window on
each side of it; the AI architect made both windows doors ("the door of the room no door reached") although the door
between the two rooms stood 2.5 cm away, and the code checks did not see three doors side by side. The model review
(M12) now counts it, so a decision that makes it worse is refused (``architect_ai._verdicts``) and Argus reports it in
every project.
"""
from __future__ import annotations

import math
from typing import Optional

FRAME_M = 0.05                  # a door frame (jamb and architrave) beside its opening (= parametric.DOOR_FRAME_W)
PAIR_GAP_M = 2 * FRAME_M        # two doors on one wall need at least two frames of wall between them
OVERLAP_TOL_M = 0.02            # openings that overlap by more than this overlap
LINE_TOL_M = 0.10               # two parallel walls are one wall line when their centre lines are this close (+ half
                                # their thicknesses: a facade drawn as two walls)
PARALLEL_SIN = 0.05             # parallel within about 3 degrees
SWING_SHARE = 0.25              # swing zones overlapping by this share of the smaller one: the leaves hit each other
DOORWAY_SILL_M = 0.20           # a doorless opening this low is a doorway (it joins two rooms like a door)
STEP_M = 0.20                   # two floors within this are one floor: no drop between them, no guard
# The rooms that need a door for privacy (a passage drawn unclear into one of them gets a door; any other passage
# inside the house stays open)
PRIVACY_ROOMS = ("bathroom", "wc", "toilet", "shower", "bedroom", "guest_bedroom", "master_bedroom")
UNCLEAR_GAP = "unclassified gap content"       # = ingest.generic.openings: lines in the gap no rule could read


def is_door(o: dict) -> bool:
    return o.get("type") == "door"


def is_passage(o: dict) -> bool:
    """A door, or a doorless opening at its floor (a doorway): it joins the rooms on its two sides."""
    if o.get("type") == "door":
        return True
    return o.get("type") == "opening" and float(o.get("sill_height") or 0.0) <= DOORWAY_SILL_M


def made_by(o: dict) -> Optional[dict]:
    """``{"key", "by", "drawn_type"}`` when a decision made this door from another drawn type (a window or a gap the
    architect or the AI turned into a door: ``drawn_type`` and ``corrected_by_ai``), else None."""
    drawn = o.get("drawn_type")
    rec = o.get("corrected_by_ai")
    if not is_door(o) or not drawn or drawn == "door" or not isinstance(rec, dict):
        return None
    return {"key": rec.get("answer_key") or rec.get("rule"), "by": rec.get("answer_by") or rec.get("by"),
            "drawn_type": drawn}


def _axis(wall: dict):
    (ax, ay), (bx, by) = wall["start"][:2], wall["end"][:2]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return (float(ax), float(ay)), (1.0, 0.0)
    return (float(ax), float(ay)), ((bx - ax) / length, (by - ay) / length)


def _rect(c, u, along: float, across: float, off: float = 0.0) -> list[tuple[float, float]]:
    """The rectangle ``along`` x ``across`` centred ``off`` from ``c`` across ``u`` (``u`` the long side)."""
    n = (-u[1], u[0])
    cx, cy = c[0] + n[0] * off, c[1] + n[1] * off
    hu, hn = along / 2.0, across / 2.0
    return [(cx - u[0] * hu - n[0] * hn, cy - u[1] * hu - n[1] * hn),
            (cx + u[0] * hu - n[0] * hn, cy + u[1] * hu - n[1] * hn),
            (cx + u[0] * hu + n[0] * hn, cy + u[1] * hu + n[1] * hn),
            (cx - u[0] * hu + n[0] * hn, cy - u[1] * hu + n[1] * hn)]


def _area(poly) -> float:
    n = len(poly)
    return abs(0.5 * sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n)))


def _ccw(poly) -> list:
    n = len(poly)
    s = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    return list(poly) if s >= 0 else list(poly)[::-1]


def overlap_area(a, b) -> float:
    """The area two convex polygons share (pure; ``a`` clipped by every edge of ``b``)."""
    from wenart.blender.geom2d import clip_half_plane
    out = _ccw(a)
    b = _ccw(b)
    n = len(b)
    for i in range(n):
        if len(out) < 3:
            return 0.0
        (x0, y0), (x1, y1) = b[i], b[(i + 1) % n]
        # inside a counter-clockwise polygon = left of each edge: (x1-x0)(y-y0) - (y1-y0)(x-x0) >= 0
        out = clip_half_plane(out, (y1 - y0), -(x1 - x0), -(y1 - y0) * x0 + (x1 - x0) * y0)
    return _area(out) if len(out) >= 3 else 0.0


class _Door:
    def __init__(self, o: dict, wall: dict, sides: list):
        self.o, self.id, self.wall = o, o["id"], wall
        self.a, self.u = _axis(wall)
        c = (float(o["center"][0]), float(o["center"][1]))
        self.t = (c[0] - self.a[0]) * self.u[0] + (c[1] - self.a[1]) * self.u[1]
        self.c = (self.a[0] + self.u[0] * self.t, self.a[1] + self.u[1] * self.t)
        self.width = float(o.get("width") or 0.0)
        self.thick = float(wall.get("thickness") or 0.2)
        self.sides = sides                                  # [room on +n, room on -n] (None: outside)
        self.rooms = sorted(r["id"] for r in sides if r is not None)
        self.frame = _rect(self.c, self.u, self.width + 2 * FRAME_M, self.thick)

    def swing_zone(self) -> Optional[list]:
        """The floor a swing leaf sweeps (its width deep, a pair half of it) on its ``swing_side``, None when the side
        is unknown or the door does not swing."""
        o = self.o
        if not is_door(o) or str(o.get("operation") or "swing").lower() not in ("swing", "double", "unknown"):
            return None
        side = o.get("swing_side")
        ids = [(r or {}).get("id") for r in self.sides]
        if not side or side not in ids:
            return None
        k = 1.0 if ids.index(side) == 0 else -1.0
        depth = self.width / (2.0 if str(o.get("operation") or "").lower() == "double" or
                              int(o.get("leaves") or 1) >= 2 else 1.0)
        return _rect(self.c, self.u, self.width, depth, k * (self.thick / 2.0 + depth / 2.0))


def _doors(building: dict) -> list[_Door]:
    from wenart.blender import architect_actions as AA
    plan = AA.Plan(building)
    out = []
    for o in building.get("openings") or []:
        w = plan.walls.get(o.get("wall_id"))
        if not is_door(o) or w is None or not o.get("center") or float(o.get("width") or 0.0) <= 0:
            continue
        out.append(_Door(o, w, AA.window_sides(plan, o) or [None, None]))
    return out


def _pair(a: _Door, b: _Door) -> Optional[dict]:
    """The conflict of two doors of one level (module docstring), None when they work as two doors."""
    same = len(a.rooms) == 2 and a.rooms == b.rooms
    cross = abs(a.u[0] * b.u[1] - a.u[1] * b.u[0])
    gap = None
    if cross < PARALLEL_SIN:
        n = (-a.u[1], a.u[0])
        off = abs((b.c[0] - a.c[0]) * n[0] + (b.c[1] - a.c[1]) * n[1])
        if off <= (a.thick + b.thick) / 2.0 + LINE_TOL_M:
            tb = (b.c[0] - a.a[0]) * a.u[0] + (b.c[1] - a.a[1]) * a.u[1]
            gap = abs(tb - a.t) - (a.width + b.width) / 2.0
    kind, sev = None, None
    if gap is not None:
        if gap < -OVERLAP_TOL_M:
            kind, sev = "overlap", "critical"
        elif gap < PAIR_GAP_M - 1e-6:
            kind, sev = "frames", "critical" if same else "major"
        elif same and gap < min(a.width, b.width):
            kind, sev = "same_passage", "major"
    elif overlap_area(a.frame, b.frame) > 1e-6:
        kind, sev = "frames", "critical" if same else "major"
    share = None
    if kind is None:
        za, zb = a.swing_zone(), b.swing_zone()
        if za is not None and zb is not None and a.o.get("swing_side") == b.o.get("swing_side"):
            small = min(_area(za), _area(zb))
            share = overlap_area(za, zb) / small if small > 1e-9 else 0.0
            if share >= SWING_SHARE:
                kind, sev = "swing", "major"
    if kind is None:
        return None
    made = {d.id: made_by(d.o) for d in (a, b) if made_by(d.o)}
    target = next(iter(made), max(a.id, b.id))
    rooms = " and ".join(a.rooms) if same else f"{' / '.join(a.rooms) or 'outside'} and " \
                                               f"{' / '.join(b.rooms) or 'outside'}"
    what = {"overlap": f"overlap on one wall ({-gap:.2f} m)" if gap is not None else "overlap",
            "frames": (f"stand {max(gap, 0.0):.2f} m apart on one wall: their frames touch (two doors need "
                       f"{PAIR_GAP_M:.2f} m of wall between them)") if gap is not None else
                      "meet at a corner: their frames run into each other",
            "same_passage": f"stand {gap:.2f} m apart on one wall, closer than a door's width" if gap is not None
                            else "",
            "swing": f"swing into {a.o.get('swing_side')} over each other ({share or 0.0:.0%} of a leaf's sweep)"}[kind]
    joins = f"both between {rooms}" if same else f"joining {rooms}"
    made_txt = "; ".join(f"{i} was a drawn {m['drawn_type']} a decision made a door ({m['key']})"
                         for i, m in made.items())
    message = f"{a.id} and {b.id} {what}, {joins}" + (f"; {made_txt}" if made_txt else "") + \
              (": one passage drawn or read twice" if same and kind != "swing" and not made else "")
    return {"kind": kind, "severity": sev, "doors": [a.id, b.id], "target": target, "other": b.id if target == a.id
            else a.id, "rooms": {a.id: a.rooms, b.id: b.rooms}, "same_rooms": same,
            "gap_m": None if gap is None else round(gap, 3), "share": None if share is None else round(share, 3),
            "made_by": made, "level_id": a.o.get("level_id"), "room_id": (a.rooms or b.rooms or [None])[0],
            "message": message}


def conflicts(building: dict, ids: Optional[set] = None) -> tuple[list[dict], int]:
    """``(records, doors checked)`` of the doors of ``building`` (module docstring); ``ids``: only the pairs with one
    of these doors (a decision's dry check)."""
    doors = _doors(building)
    out = []
    for i, a in enumerate(doors):
        for b in doors[i + 1:]:
            if a.o.get("level_id") != b.o.get("level_id"):
                continue
            if ids is not None and a.id not in ids and b.id not in ids:
                continue
            rec = _pair(a, b)
            if rec is not None:
                out.append(rec)
    return out, len(doors)


def joined_by(building: dict, room_ids, skip=()) -> list[str]:
    """The doors and doorways of ``building`` that join exactly the two rooms ``room_ids``, but those in ``skip``."""
    from wenart.blender import architect_actions as AA
    plan = AA.Plan(building)
    want = sorted(room_ids)
    out = []
    for o in building.get("openings") or []:
        if o.get("id") in skip or not is_passage(o) or o.get("wall_id") not in plan.walls:
            continue
        sides = AA.window_sides(plan, o)
        if len(sides) == 2 and all(r is not None for r in sides) and sorted(r["id"] for r in sides) == want:
            out.append(o["id"])
    return out


# --------------------------------------------------------------------------------------------- passages (27 Oct 2026)

def needs_privacy(room: Optional[dict]) -> bool:
    """Whether a room needs a door for privacy (``PRIVACY_ROOMS``: a bathroom, a WC, a shower room, a bedroom)."""
    return str((room or {}).get("room_type") or "").lower() in PRIVACY_ROOMS


def unclear_gap(o: dict) -> bool:
    """Whether a drawn gap holds lines no rule could read (``UNCLEAR_GAP``): the drawing does not say whether it is a
    passage or an opening with something in it; an empty gap is a clear open passage."""
    if str(o.get("type_raw") or "").lower() == UNCLEAR_GAP:
        return True
    return any(str((e or {}).get("note") or "").lower().startswith(UNCLEAR_GAP) for e in o.get("evidence") or []
               if isinstance(e, dict))


def drawn_kind(o: dict) -> str:
    """The type the drawing gives an opening (``drawn_type`` once a decision changed it)."""
    return str(o.get("drawn_type") or o.get("type") or "")


def _key_of(rec) -> Optional[str]:
    if not isinstance(rec, dict):
        return None
    return rec.get("answer_key") or rec.get("rule")


def guard_key(o: dict) -> Optional[str]:
    """The answer that put a guard across an opening (``guard.reason`` "the answer to <key>: ..."), else None."""
    import re
    g = o.get("guard") if isinstance(o.get("guard"), dict) else None
    m = re.search(r"answer to ([A-Za-z0-9_.]+:[A-Za-z0-9_]+)", str((g or {}).get("reason") or ""))
    return m.group(1) if m else None


def _floor_z(plan, room: dict) -> float:
    lv = plan.levels.get(room.get("level_id")) or {}
    return float(lv.get("elevation") or 0.0) + float(room.get("floor_offset_m") or 0.0)


def needless(building: dict) -> tuple[list[dict], int]:
    """``(records, inside openings checked)``: the openings between two rooms that got a leaf, glass or a guard they
    do not need (module docstring "Passages"); each record as ``conflicts``' (``kind``, ``severity``, ``target``,
    ``made_by``, ``message``)."""
    from wenart.blender import architect_actions as AA
    plan = AA.Plan(building)
    out, n = [], 0
    for o in building.get("openings") or []:
        w = plan.walls.get(o.get("wall_id"))
        if w is None or not o.get("center"):
            continue
        sides = AA.window_sides(plan, o)
        if len(sides) != 2 or any(r is None or AA.Plan.is_outside(r) for r in sides):
            continue
        n += 1
        rooms = [r["id"] for r in sides]
        between = f"between {rooms[0]} and {rooms[1]}"
        private = [r["id"] for r in sides if needs_privacy(r)]
        recs = []
        if drawn_kind(o) == "opening" and o.get("type") == "door" and not private:
            key = _key_of(o.get("corrected_by_ai"))
            leaf = f"{'glazed ' if o.get('glazed') else ''}{o.get('operation') or 'swing'} door"
            recs.append(("needless_leaf", "major", key,
                         f"{o['id']} is drawn as an open passage {between} (no leaf, no swing arc) and neither room "
                         f"needs privacy, yet {key or 'a decision'} gave it a {leaf}: an open passage needs no leaf"))
        elif drawn_kind(o) == "opening" and o.get("type") == "window" and \
                (o.get("interior_glazing") or {}).get("kind") != "pass_through":
            key = _key_of(o.get("corrected_by_ai"))
            recs.append(("needless_glass", "major", key,
                         f"{o['id']} is drawn as an open passage {between} (no leaf, no swing arc), yet "
                         f"{key or 'a decision'} made it a window: an open passage needs no glass"))
        if isinstance(o.get("guard"), dict):
            zs = [_floor_z(plan, r) for r in sides]
            if abs(zs[0] - zs[1]) <= STEP_M:
                key = guard_key(o) or _key_of(o.get("adjusted_by_ai"))
                top = float(o["guard"].get("top_m") or 0.0)
                recs.append(("needless_guard", "major", key,
                             f"{o['id']} {between} has a guard {top:.2f} m high across it, though both rooms lie on "
                             f"one floor (no drop): a guard only stands over a drop"))
        for kind, sev, key, msg in recs:
            out.append({"kind": kind, "severity": sev, "doors": [o["id"]], "target": o["id"], "other": None,
                        "rooms": {o["id"]: sorted(rooms)}, "same_rooms": False, "gap_m": None, "share": None,
                        "made_by": {o["id"]: {"key": key, "by": None, "drawn_type": drawn_kind(o)}} if key else {},
                        "level_id": o.get("level_id"), "room_id": rooms[0], "message": msg})
    return out, n


def open_hatch(o: dict) -> bool:
    """A serving hatch over a drawn counter (``architect_actions.act_pass_through``: a doorway a drawn counter fills):
    the wall under the counter top closes it, the rest stays open: the build makes no glass and no frame
    (27 Oct 2026, user: "Not every opening inside the house requires a door or a window")."""
    return o.get("type") == "window" and (o.get("interior_glazing") or {}).get("kind") == "pass_through"
