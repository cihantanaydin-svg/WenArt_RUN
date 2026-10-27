"""The architect's answers: where they come from and the actions that carry them out (user request of 25 Oct 2026:
"1 no inside window should be outside, 2 yes, 3 yes, ai on the pod needs to be clever and able to answer the
questions and make modifications accordingly").

What: every open question of the review (``wenart/blender/architect.py``) offers ``options``: the actions of
``ACTIONS`` that would settle it, with their parameters. An answer picks one option:

    {"<rule>:<element>": {"option": "<action>", "params": {...}, "answer": "<the words>", "by": "user" | "ai",
                          "where": {"level_id", "centre"}, "reason": "...", "date": "..."}}

``apply_answers(building, answers)`` carries the answers out on the building before anything is planned (pure;
``build.prepare`` calls it first): moving a window that sits in an inside wall to the room's outer wall, enlarging a
room's windows to a tenth of its floor, retyping a room, widening a door, raising a low sill; ``keep`` changes
nothing and closes the question. Every change keeps the drawn values (``drawn_wall_id``, ``drawn_center``,
``drawn_width``, ...) and carries ``corrected_by_ai`` / ``adjusted_by_ai`` with the answer and the reason; an answer
that cannot be carried out (no outer wall with room for the window, ...) leaves the question open with the reason.

Where the answers come from, a later source wins: the AI architect on the pod (``building["agent_overrides"]
["architect"]``, replayed from ``orchestrator/overrides.json``: ``wenart/agent/architect_ai.py``), the building's
``architect_answers``, the project's ``architect_answers.json`` (the user's: ``projects/<p>/architect_answers.json``,
read into the build brief by ``build.brief_args`` so a new answer rebuilds the scene). A bare text answer (the first
form) still works: "store ..." retypes the room to storage, anything else keeps.

Why: the answers must change the building the same way on every run, for every project, and be checked like every
other edit (CLAUDE.md: the AI never edits geometry by hand; code carries the edit out and the review re-checks it).
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Optional

from wenart import geometry as G

REPO_ROOT = Path(__file__).resolve().parents[2]
ANSWERS_FILE = "architect_answers.json"
SAMPLE_M = 0.10                 # the outer runs of a wall are sampled every this many metres
PROBE_M = 0.25                  # ... this far beyond each face of the wall
EDGE_MARGIN_M = 0.30            # a moved, widened or new window keeps this far from a corner and another opening
MAX_WINDOW_W = 4.0              # an enlarged window grows to at most this width ...
MAX_GROW = 2.0                  # ... and at most this times its drawn width
NEW_WINDOW_W = (0.8, 2.4)       # a window the architect adds: between these widths
LINTEL_M = 0.25                 # an enlarged window's head stays this far under the ceiling
LOW_SILL_M = 0.45               # a window onto a terrace at its floor may come down to this sill
MAX_RAISE_M = 0.60              # ... and rises at most this much
DOOR_MIN_W = 0.80               # a widened door (a WC door: 0.70)
WC_DOOR_MIN_W = 0.70
SAFE_SILL_M = 0.90              # a raised sill
WHERE_TOL_M = 1.5               # an answer's element must still be this close to where the answer saw it
MIN_WINDOW_H = 0.60
ROOM_TYPES = ("bedroom", "living", "dining", "kitchen", "bathroom", "wc", "office", "study", "storage", "laundry",
              "hall", "dressing", "closet", "other")
OPEN_AIR = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch", "garden")
DAYLIGHT_RATIO = 0.10
STORE_WORDS = ("store", "storage", "service", "depo", "kiler")

# The actions an answer may pick (``id`` -> what it does); the review offers the ones that fit each question.
ACTIONS = {
    "keep": "keep it as drawn (the question closes; nothing changes)",
    "move_window_to_outer_wall": "a reading error: move the window to the room's outer wall (same size)",
    "enlarge_windows": "enlarge the room's windows (and add one on a blank outer wall if needed) to 1/10 of its floor",
    "retype_room": "the room is another type (params: room_type)",
    "widen_door": f"widen the door to {DOOR_MIN_W:.2f} m ({WC_DOOR_MIN_W:.2f} m for a WC) where the wall allows",
    "raise_sill": f"raise the window's sill to {SAFE_SILL_M:.2f} m (the head stays)",
    "remove_piece": "the piece is not built (it does not belong there)",
    "stair_winders": "the U stair's half landing becomes winders for comfortable risers (params: count, 0 = as drawn)",
    "retype_piece": "the piece is another type (params: type)",
    # 26 Oct 2026 (user: "I need ai models to see understand and fix everything before even I look at it"): the
    # fixes of the questions that had only ``keep`` (a door into the air, a bare gap in the facade, a door off its
    # floor, a basin on the floor, a piece in a doorway); the review offers them, a safe one is its ``default``
    "door_to_window": "a reading error: nothing is outside this door or gap: a window at the floor's sill (same width "
                      "and head)",
    "french_window": "a French window: kept full height with a guard (the house's balustrade) across its whole width (1.10 m high)",
    "snap_threshold": "the door stands on its floor: its threshold at the floor of the rooms it joins",
    "mount_fixture": "the fixture at its working height (a wall-hung basin's rim at 0.85 m)",
    "move_piece": "move the piece to the nearest free place in its room, clear of the doorway or window",
    "gap_to_door": "a door the reading missed: a glazed door in a gap of the facade (sliding from 1.40 m wide); "
                   "inside the house only into a room that needs privacy (a bathroom, a WC, a bedroom): one solid "
                   "leaf; any other inside gap stays an open passage",
    "merge_openings": "one opening read twice: the two become one over both spans (params: other_id)",
    "window_to_door": "a reading error: the room has no door, this opening between two rooms is its door",
    # 26 Oct 2026 (user: "make the AI architect a lot more smart and let it take decisions more"): the decisions a
    # point had none of when its first fix could not be done (a window between two rooms with no free outer wall for
    # it, a doorway a drawn kitchen counter fills)
    "interior_glazing": "a borrowed-light window on purpose: clear glass between two dry rooms (kept where drawn)",
    "high_window": "a high borrowed-light window: its sill at 1.80 m, the head kept (privacy for a wet room)",
    "pass_through": "a serving window over the drawn counter: the doorway becomes a window at counter height between "
                    "the two rooms (the counter stays)",
    # 26 Oct 2026 (user on real06: "these sections not making sense": a 2.95 m flat oak leaf in the facade): D5
    "door_type": "the kind of door (params: kind): French doors, a glazed sliding or folding door, the entrance "
                 "door, a sectional garage door, or two leaves; never one leaf much wider than 1.2 m",
    # 27 Oct 2026 (user: "make argus fix these by itself"): the outdoor spaces (site.outdoor_spaces) as elements
    "guard_edge": "a guard (railing) on open edges of an outdoor space (params: edges [[[x0, y0], [x1, y1]], ...])",
    "cover_space": "a light roof over the part of an outdoor space no floor, space or roof above covers",
}
# The rules whose answers are carried out first (a door that becomes a window is not widened as a door)
FIRST_RULES = ("E1", "O2", "D4")
GUARD_TOP_M = 1.10              # a guard in front of a French window reaches this far over its floor
BASIN_RIM_M = 0.85              # a washbasin's rim over the floor (0.80-0.90 m)
FIXTURE_TOPS = {"washbasin": (0.78, 0.95, BASIN_RIM_M)}     # the type's working top: (low, high, target)
HIGH_SILL_M = 1.80              # a high borrowed-light window into a wet room (privacy by height)
MIN_HIGH_WINDOW_H = 0.30        # ... at least this tall
PASS_SILL_M = 0.95              # a serving window's sill: just over a 0.90 m counter top
WET_ROOMS = ("bathroom", "wc", "toilet", "shower")


CONTEXT_PARAMS = ("room_id", "window_id", "door_id", "piece_id", "away_from", "other_id")     # name the element, not the choice


def option(action: str, label: Optional[str] = None, **params) -> dict:
    """One option of an open question: ``{"id", "choice", "label", "params"}``; ``choice`` tells two options of the
    same action apart (``retype_room:storage``), the AI architect answers with it."""
    assert action in ACTIONS, action
    extra = [str(v) for k, v in params.items() if k not in CONTEXT_PARAMS and v is not None]
    return {"id": action, "choice": ":".join([action] + extra), "label": label or ACTIONS[action], "params": params}


# --------------------------------------------------------------------------
# Where the answers come from
# --------------------------------------------------------------------------

def project_dir(building: dict) -> Optional[Path]:
    folder = (building.get("project") or {}).get("source_folder")
    if not folder:
        return None
    p = Path(folder)
    return p if p.is_absolute() else REPO_ROOT / p


def project_answers(building: dict, folder=None) -> dict:
    """The user's answers of the project (``<project>/architect_answers.json``: ``{"answers": {...}}`` or the bare
    map); {} without the file."""
    d = Path(folder) if folder else project_dir(building)
    path = d / ANSWERS_FILE if d is not None else None
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    data = data.get("answers", data) if isinstance(data, dict) else {}
    return {str(k): v for k, v in data.items() if not str(k).startswith("_")}


def normalise(key: str, value) -> dict:
    """An answer as a dict (a bare text answer: "store ..." to a daylight question retypes the room to storage,
    anything else keeps)."""
    if isinstance(value, dict):
        out = dict(value)
        out.setdefault("option", "keep")
        out.setdefault("params", {})
        return out
    text = str(value)
    if key.startswith("L1:") and any(w in text.lower() for w in STORE_WORDS):
        return {"option": "retype_room", "params": {"room_type": "storage"}, "answer": text, "by": "user"}
    return {"option": "keep", "params": {}, "answer": text, "by": "user"}


def answers_of(building: dict, brief_answers: Optional[dict] = None) -> dict:
    """Every answer for this building, normalised; a later source wins: the architect's own defaults
    (``architect_defaults``, 26 Oct 2026: ``build.prepare`` carries out the safe default of every open question that
    has one), the AI's (``agent_overrides.architect``), the building's ``architect_answers``, the user's
    (``brief_answers``: the project file through the brief)."""
    out: dict = {}
    sources = (building.get("architect_defaults") or {},
               ((building.get("agent_overrides") or {}).get("architect") or {}),
               building.get("architect_answers") or {}, brief_answers or {})
    for src in sources:
        if isinstance(src, dict):
            for k, v in src.items():
                if not str(k).startswith("_"):
                    out[str(k)] = normalise(str(k), v)
    return out


AI_ANSWERS = "orchestrator/architect_answers.json"      # the AI architect's accepted answers (wenart/agent/architect_ai.py)


def answers_for_build(building_path, building: dict, folder=None) -> dict:
    """The answers a build carries out (``cli.build`` puts them into the build brief, so they enter the fingerprint):
    the AI architect's (``<out>/orchestrator/architect_answers.json`` beside the building file), then the user's
    (the project file), which win."""
    out: dict = {}
    path = Path(building_path).parent / AI_ANSWERS
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            out.update((data.get("answers", data) if isinstance(data, dict) else {}) or {})
        except (OSError, ValueError):
            pass
    out.update(project_answers(building, folder))
    return {str(k): v for k, v in out.items() if not str(k).startswith("_")}


# --------------------------------------------------------------------------
# Plan geometry: outer runs of the walls, free spans
# --------------------------------------------------------------------------

class Plan:
    """The rooms, walls and openings of a building with the lookups the actions and the rules need (pure)."""

    def __init__(self, building: dict, head_limit=None):
        self.b = building
        self.head_limit = head_limit           # opening -> the highest head over the floor (the roof), or None
        self.levels = {lv["id"]: lv for lv in building.get("levels") or []}
        self.rooms = [r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3]
        self.room = {r["id"]: r for r in self.rooms}
        self.walls = {w["id"]: w for w in building.get("walls") or []}
        self.openings = {o["id"]: o for o in building.get("openings") or []}
        self._boxes = {r["id"]: (min(p[0] for p in r["polygon"]), min(p[1] for p in r["polygon"]),
                                 max(p[0] for p in r["polygon"]), max(p[1] for p in r["polygon"])) for r in self.rooms}
        self._runs: dict = {}

    def room_at(self, pt, level_id) -> Optional[dict]:
        x, y = pt
        for r in self.rooms:
            if r.get("level_id") != level_id:
                continue
            x0, y0, x1, y1 = self._boxes[r["id"]]
            if x0 - 1e-9 <= x <= x1 + 1e-9 and y0 - 1e-9 <= y <= y1 + 1e-9 and G.point_in_polygon(pt, r["polygon"]):
                return r
        return None

    @staticmethod
    def is_outside(room: Optional[dict]) -> bool:
        return room is None or str(room.get("room_type") or "").lower() in OPEN_AIR

    @staticmethod
    def axis(wall: dict):
        (ax, ay), (bx, by) = wall["start"][:2], wall["end"][:2]
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-9:
            return (ax, ay), (1.0, 0.0), 0.0
        return (ax, ay), ((bx - ax) / length, (by - ay) / length), length

    def t_of(self, wall: dict, pt) -> float:
        a, u, _ = self.axis(wall)
        return (pt[0] - a[0]) * u[0] + (pt[1] - a[1]) * u[1]

    def at_t(self, wall: dict, t: float):
        a, u, _ = self.axis(wall)
        return a[0] + u[0] * t, a[1] + u[1] * t

    def outer_runs(self, wall: dict, room_id: str) -> list[tuple[float, float, int]]:
        """``[(t0, t1, side)]``: the stretches of ``wall`` (metres from its start) with ``room_id`` on one side and
        the outside (no room, or an open-air room) on the other; ``side`` +1 when the room lies left of the wall."""
        key = (wall["id"], room_id)
        if key in self._runs:
            return self._runs[key]
        a, u, length = self.axis(wall)
        n = (-u[1], u[0])
        reach = float(wall.get("thickness") or 0.2) / 2.0 + PROBE_M
        lid = wall.get("level_id")
        runs, cur = [], None
        steps = max(1, int(length / SAMPLE_M))
        for k in range(steps + 1):
            t = length * k / steps
            p = (a[0] + u[0] * t, a[1] + u[1] * t)
            left = self.room_at((p[0] + n[0] * reach, p[1] + n[1] * reach), lid)
            right = self.room_at((p[0] - n[0] * reach, p[1] - n[1] * reach), lid)
            side = 0
            if left is not None and left["id"] == room_id and self.is_outside(right):
                side = 1
            elif right is not None and right["id"] == room_id and self.is_outside(left):
                side = -1
            if side and cur is not None and cur[2] == side:
                cur[1] = t
            elif side:
                cur = [t, t, side]
                runs.append(cur)
            else:
                cur = None
        out = [(r[0], r[1], r[2]) for r in runs if r[1] - r[0] > SAMPLE_M]
        self._runs[key] = out
        return out

    def spans_on(self, wall: dict, skip: tuple = ()) -> list[tuple[float, float]]:
        """The stretches of ``wall`` taken by openings: its own and those of parallel walls within 0.35 m of its line
        (real04 draws the facade line and the inner face of some walls as two walls)."""
        a, u, _ = self.axis(wall)
        out = []
        for o in self.openings.values():
            if o["id"] in skip or o.get("level_id") != wall.get("level_id"):
                continue
            w2 = self.walls.get(o.get("wall_id"))
            if w2 is None:
                continue
            if w2["id"] != wall["id"]:
                _a2, u2, _ = self.axis(w2)
                if abs(u[0] * u2[1] - u[1] * u2[0]) > 0.05:
                    continue
                c = o["center"]
                if abs((c[0] - a[0]) * -u[1] + (c[1] - a[1]) * u[0]) > 0.35 + float(wall.get("thickness") or 0.2):
                    continue
            t = self.t_of(wall, o["center"])
            half = float(o.get("width") or 0.0) / 2.0
            out.append((t - half, t + half))
        return out

    def free_spans(self, wall: dict, room_id: str, skip: tuple = (), margin: float = EDGE_MARGIN_M):
        """The outer stretches of ``wall`` along ``room_id`` without openings (``margin`` from their ends and from
        every opening): ``[(t0, t1, side)]``."""
        taken = self.spans_on(wall, skip)
        out = []
        for t0, t1, side in self.outer_runs(wall, room_id):
            pieces = [(t0 + margin, t1 - margin)]
            for s0, s1 in taken:
                nxt = []
                for p0, p1 in pieces:
                    if s1 + margin <= p0 or s0 - margin >= p1:
                        nxt.append((p0, p1))
                        continue
                    if s0 - margin > p0:
                        nxt.append((p0, s0 - margin))
                    if s1 + margin < p1:
                        nxt.append((s1 + margin, p1))
                pieces = nxt
            out += [(p0, p1, side) for p0, p1 in pieces if p1 - p0 > 0.05]
        return out

    def room_walls(self, room_id: str) -> list[dict]:
        """The walls of the room's level with an outer run along the room."""
        lid = self.room[room_id].get("level_id")
        x0, y0, x1, y1 = self._boxes[room_id]
        out = []
        for w in self.walls.values():
            if w.get("level_id") != lid:
                continue
            xs, ys = (w["start"][0], w["end"][0]), (w["start"][1], w["end"][1])
            if max(xs) < x0 - 0.5 or min(xs) > x1 + 0.5 or max(ys) < y0 - 0.5 or min(ys) > y1 + 0.5:
                continue
            if self.outer_runs(w, room_id):
                out.append(w)
        return out

    def onto_open_air(self, o: dict, room_id: str) -> bool:
        """Whether window ``o`` of ``room_id`` opens onto an open-air room (a terrace, a balcony) of its level."""
        w = self.walls.get(o.get("wall_id"))
        if w is None:
            return False
        a, u, _ = self.axis(w)
        n = (-u[1], u[0])
        t = self.t_of(w, o["center"])
        p = (a[0] + u[0] * t, a[1] + u[1] * t)
        reach = float(w.get("thickness") or 0.2) / 2.0 + PROBE_M
        sides = [self.room_at((p[0] + n[0] * k * reach, p[1] + n[1] * k * reach), w.get("level_id")) for k in (1, -1)]
        ids = [(r or {}).get("id") for r in sides]
        if room_id not in ids:
            return False
        other = sides[1 - ids.index(room_id)]
        return other is not None and str(other.get("room_type") or "").lower() in OPEN_AIR

    def ceiling(self, level_id) -> float:
        lv = self.levels.get(level_id) or {}
        return float(lv.get("ceiling_height") or lv.get("height") or 2.6)

    def top(self, o: dict) -> float:
        """The highest an opening's head may reach over its floor: the ceiling, and the roof over it."""
        top = self.ceiling(o.get("level_id"))
        if self.head_limit is not None:
            lim = self.head_limit(o)
            if lim is not None:
                top = min(top, float(lim))
        return top


def room_area(room: dict) -> float:
    poly = room["polygon"]
    return abs(0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly))))


def window_glass(o: dict, top: float) -> float:
    """Glass of a window (m2): its width times its height up to ``top`` (the ceiling or the roof over it)."""
    sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
    h = float(o.get("height") if o.get("height") is not None else 1.2)
    return float(o.get("width") or 0.0) * max(0.0, min(sill + h, top) - sill)


def outside_glass(plan: Plan, room_id: str) -> tuple[float, list[dict]]:
    """``(m2, windows)``: the room's glass to the outside (windows; a door to the outside counts half) and its
    windows to the outside."""
    room = plan.room[room_id]
    lid = room.get("level_id")
    total, wins = 0.0, []
    for o in plan.openings.values():
        w = plan.walls.get(o.get("wall_id"))
        if w is None or o.get("level_id") != lid or o.get("type") not in ("window", "door"):
            continue
        t = plan.t_of(w, o["center"])
        if not any(t0 - 0.05 <= t <= t1 + 0.05 for t0, t1, _s in plan.outer_runs(w, room_id)):
            continue
        if o["type"] == "window":
            total += window_glass(o, plan.top(o))
            wins.append(o)
        else:
            total += 0.5 * float(o.get("width") or 0.0) * min(float(o.get("height") or 2.1), plan.top(o))
    return total, wins


# --------------------------------------------------------------------------
# The actions
# --------------------------------------------------------------------------

def _keep_drawn(o: dict, *fields) -> None:
    for f in fields:
        o.setdefault(f"drawn_{f}", copy.deepcopy(o.get(f)))


def _mark(o: dict, flag: str, key: str, ans: dict, reason: str) -> None:
    o[flag] = {"by": "architect", "answer_key": key, "answer_by": ans.get("by", "user"),
               "answer": ans.get("answer"), "reason": reason}
    ev = o.setdefault("evidence", [])
    if isinstance(ev, list):              # the schema's evidence: the answer (its file), the rule, the reason
        ev.append({"file": ANSWERS_FILE if ans.get("by", "user") == "user" else AI_ANSWERS, "method": "inferred",
                   "confidence": 0.6, "rule": f"architect {key}", "text": reason})


def act_move_window(plan: Plan, key: str, ans: dict, window_id: str, room_id: Optional[str] = None):
    """The window to the outer wall of ``room_id`` (the dark room): a wall parallel to its drawn wall first (the
    reading put it on the wrong side), at the same place along it when there is room, else the nearest free
    stretch; then the other outer walls, the longest free stretch first."""
    o = plan.openings.get(window_id)
    if o is None or o.get("type") != "window":
        return False, f"no window {window_id}"
    w0 = plan.walls.get(o.get("wall_id"))
    sides = window_sides(plan, o)
    if not sides or any(Plan.is_outside(r) for r in sides):
        return True, f"{window_id} already looks outside: nothing to move"
    if room_id is None or room_id not in plan.room:
        # the dark one of its two rooms: the habitable room with the least glass to the outside
        room_id = min(sides, key=lambda r: (str(r.get("room_type") or "").lower() not in
                                            ("bedroom", "living", "kitchen", "dining", "office", "study", "other"),
                                            outside_glass(plan, r["id"])[0]))["id"]
    width = float(o.get("width") or 0.0)
    _a0, u0, _ = plan.axis(w0) if w0 else ((0, 0), (1.0, 0.0), 0)
    best = None
    for w in plan.room_walls(room_id):
        if w0 is not None and w["id"] == w0["id"]:
            continue
        _a, u, _l = plan.axis(w)
        parallel = abs(u[0] * u0[0] + u[1] * u0[1]) > 0.9
        want = plan.t_of(w, o["center"])
        for t0, t1, _side in plan.free_spans(w, room_id, skip=(window_id,)):
            if t1 - t0 + 1e-9 < width:
                continue
            t = min(max(want, t0 + width / 2.0), t1 - width / 2.0)
            score = (0 if parallel else 1, abs(t - want) if parallel else -(t1 - t0))
            if best is None or score < best[0]:
                best = (score, w, t)
    if best is None:
        return False, f"{room_id} has no outer wall with {width:.2f} m free for {window_id}"
    _score, w, t = best
    _keep_drawn(o, "wall_id", "center")
    x, y = plan.at_t(w, t)
    was = o.get("wall_id")
    o["wall_id"], o["center"] = w["id"], [round(x, 4), round(y, 4)]
    reason = (f"{window_id} sat in the inside wall {was} between two rooms; moved to the outer wall {w['id']} of "
              f"{room_id} (same size), at {x:.2f}, {y:.2f}")
    _mark(o, "corrected_by_ai", key, ans, reason)
    return True, reason


def window_sides(plan: Plan, o: dict) -> list:
    """The rooms (None: outside) on the two sides of an opening at its centre."""
    w = plan.walls.get(o.get("wall_id"))
    if w is None:
        return []
    a, u, _ = plan.axis(w)
    n = (-u[1], u[0])
    t = plan.t_of(w, o["center"])
    p = (a[0] + u[0] * t, a[1] + u[1] * t)
    reach = float(w.get("thickness") or 0.2) / 2.0 + PROBE_M
    return [plan.room_at((p[0] + n[0] * k * reach, p[1] + n[1] * k * reach), w.get("level_id")) for k in (1, -1)]


def act_enlarge(plan: Plan, key: str, ans: dict, room_id: str, ratio: float = DAYLIGHT_RATIO):
    """The room's glass to ``ratio`` of its floor: its outside windows wider (within their free stretch, at most
    ``MAX_WINDOW_W`` and ``MAX_GROW`` times their drawn width), then taller (to ``LINTEL_M`` under the ceiling, at most
    ``MAX_RAISE_M``), then a new window on its longest blank outer stretch (sill and head of its windows)."""
    room = plan.room.get(room_id)
    if room is None:
        return False, f"no room {room_id}"
    area = room_area(room)
    need = ratio * area * 1.01                  # a 1 % margin: the sizes are rounded to the millimetre
    have, wins = outside_glass(plan, room_id)
    done = []
    if have + 1e-6 >= need:
        return True, f"{room_id} already has {have:.2f} m2 of glass (1/{area / have:.0f})"
    for o in sorted(wins, key=lambda o: -float(o.get("width") or 0.0)):
        if have >= need:
            break
        w = plan.walls[o["wall_id"]]
        width = float(o["width"])
        h = window_glass(o, plan.top(o)) / max(width, 1e-6)
        t = plan.t_of(w, o["center"])
        span = next(((t0, t1) for t0, t1, _s in plan.free_spans(w, room_id, skip=(o["id"],))
                     if t0 - 1e-6 <= t - width / 2.0 and t + width / 2.0 <= t1 + 1e-6), None)
        if span is None or h <= 0:
            continue
        cap = min(MAX_WINDOW_W, MAX_GROW * float(o.get("drawn_width") or width), span[1] - span[0])
        new_w = min(cap, width + (need - have) / h)
        if new_w <= width + 0.05:
            continue
        nt = min(max(t, span[0] + new_w / 2.0), span[1] - new_w / 2.0)
        _keep_drawn(o, "width", "center")
        x, y = plan.at_t(w, nt)
        o["width"], o["center"] = round(new_w, 3), [round(x, 4), round(y, 4)]
        have += (new_w - width) * h
        done.append(f"{o['id']} {width:.2f} -> {new_w:.2f} m wide")
        _mark(o, "adjusted_by_ai", key, ans, f"widened for daylight ({room_id}: glass to 1/10 of the floor)")
    for o in wins:
        if have >= need:
            break
        sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
        h = min(float(o.get("height") if o.get("height") is not None else 1.2), plan.top(o) - sill)
        top = min(plan.ceiling(o.get("level_id")) - LINTEL_M, plan.top(o), sill + h + MAX_RAISE_M)
        if top <= sill + h + 0.05:
            continue
        new_h = min(top - sill, h + (need - have) / max(float(o["width"]), 1e-6))
        _keep_drawn(o, "height")
        have += (new_h - h) * float(o["width"])
        o["height"] = round(new_h, 3)
        done.append(f"{o['id']} {h:.2f} -> {new_h:.2f} m high")
        _mark(o, "adjusted_by_ai", key, ans, f"taller for daylight ({room_id}: glass to 1/10 of the floor)")
    for o in wins:
        # a window onto a terrace or balcony at the room's floor (no drop under it) may come down to a low sill
        if have >= need or not plan.onto_open_air(o, room_id):
            continue
        sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
        if sill <= LOW_SILL_M + 0.05:
            continue
        head = min(sill + float(o.get("height") if o.get("height") is not None else 1.2), plan.top(o))
        new_sill = max(LOW_SILL_M, sill - (need - have) / max(float(o["width"]), 1e-6))
        _keep_drawn(o, "sill_height", "height")
        have += (sill - new_sill) * float(o["width"])
        o["sill_height"], o["height"] = round(new_sill, 3), round(head - new_sill, 3)
        done.append(f"{o['id']} sill {sill:.2f} -> {new_sill:.2f} m (it opens onto a terrace at its floor)")
        _mark(o, "adjusted_by_ai", key, ans, f"a lower sill onto the terrace for daylight ({room_id})")
    if have < need:
        # a new window looks like the others of its floor (their median width, sill and height): a bedroom window
        # 1.0 m wide beside 2.7 m ones reads as a mistake; the need for daylight is the least it gets
        typ = typical_window(plan, room.get("level_id"))
        sill = float(wins[0].get("sill_height") or 0.9) if wins else (typ or {}).get("sill", 0.9)
        h = float(wins[0].get("height") or 1.2) if wins else (typ or {}).get(
            "height", min(1.4, plan.ceiling(room.get("level_id")) - LINTEL_M - sill))
        wide = max(NEW_WINDOW_W[1], (typ or {}).get("width", 0.0))
        spans = sorted(((t1 - t0, w, t0, t1) for w in plan.room_walls(room_id)
                        for t0, t1, _s in plan.free_spans(w, room_id)), key=lambda s: -s[0])
        k = 0
        for length, w, t0, t1 in spans:
            if have >= need or length < NEW_WINDOW_W[0]:
                break
            x, y = plan.at_t(w, (t0 + t1) / 2.0)
            k += 1
            nid = f"win_arch_{room_id}_{k}"
            o = {"id": nid, "type": "window", "level_id": room.get("level_id"), "wall_id": w["id"],
                 "center": [round(x, 4), round(y, 4)], "width": wide, "height": round(h, 3),
                 "sill_height": round(sill, 3), "swing_side": None, "status": "unverified", "evidence": []}
            eff = max(0.0, min(sill + h, plan.top(o)) - sill)
            if eff < MIN_WINDOW_H:
                k -= 1
                continue
            new_w = min(length, max(NEW_WINDOW_W[0], (typ or {}).get("width", 0.0), (need - have) / eff))
            o["width"] = round(new_w, 3)
            _mark(o, "added_by_ai", key, ans, f"a new window for daylight ({room_id} had {have:.2f} m2 of glass)")
            plan.b.setdefault("openings", []).append(o)
            plan.openings[nid] = o
            have += new_w * eff
            done.append(f"new window {nid} {new_w:.2f} x {h:.2f} m on {w['id']}")
    text = f"{room_id}: " + "; ".join(done) + f" (glass {have:.2f} m2 = 1/{area / max(have, 1e-6):.0f} of the floor"
    if have + 1e-6 < need:
        text += f"; 1/10 needs {need:.2f} m2: the walls and the roof over them allow no more (a roof window or a " \
                f"dormer would)"
    text += ")"
    # carried out when it reached 1/10, or did all the walls and the roof allow (the shortfall is in the text)
    return bool(done), text if done else f"{room_id}: no window could grow and no outer wall is free"


def typical_window(plan: Plan, level_id) -> Optional[dict]:
    """The median width, sill and height of the windows to the outside of a level (None without any)."""
    rows = []
    for o in plan.openings.values():
        w = plan.walls.get(o.get("wall_id"))
        if o.get("type") != "window" or o.get("level_id") != level_id or w is None or o.get("added_by_ai"):
            continue
        sides = window_sides(plan, o)
        if sides and any(Plan.is_outside(r) for r in sides):
            rows.append((float(o.get("width") or 0.0), float(o.get("sill_height") if o.get("sill_height") is not None
                                                             else 0.9), float(o.get("height") or 1.2)))
    if not rows:
        return None
    mid = lambda k: sorted(r[k] for r in rows)[len(rows) // 2]          # noqa: E731
    return {"width": mid(0), "sill": mid(1), "height": mid(2)}


GAP_APPROACH_M = 0.60          # the approach in front of a gap a drawn piece standing in it blocks
GAP_FREE_MIN_M = 0.60          # ... leaving no free stretch this wide across it (a walkway)
GAP_PIECE_MIN_M = 0.30         # drawn pieces smaller than this both ways (marks) never count
NOT_A_PIECE = ("rug", "detail", "mark", "decor")


OUTDOOR_LABEL_NEAR_M = 3.0      # an outdoor-space label this close to a passage's outside: it leads there


def outdoor_space_at(building: dict, point, level_id) -> bool:
    """Whether ``point`` (just outside a wall) lies on a drawn outdoor space of the level: an outdoor space, platform
    or site area polygon, or within ``OUTDOOR_LABEL_NEAR_M`` of a labelled site area's anchor (a balcony the reading
    has no outline for yet)."""
    from shapely.geometry import Point, Polygon

    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    pt = Point(float(point[0]), float(point[1]))
    for key in ("outdoor_spaces", "platforms", "areas", "terraces"):
        for a in site.get(key) or []:
            if not isinstance(a, dict) or (a.get("level_id") not in (None, level_id)):
                continue
            poly = a.get("polygon")
            if poly and len(poly) >= 3:
                try:
                    if Polygon([tuple(q[:2]) for q in poly]).buffer(0.05).contains(pt):
                        return True
                except Exception:  # noqa: BLE001 - a broken outline: the anchor below
                    pass
            anchor = a.get("anchor")
            if key == "areas" and anchor and a.get("label") and \
                    math.hypot(float(anchor[0]) - pt.x, float(anchor[1]) - pt.y) <= OUTDOOR_LABEL_NEAR_M:
                return True
    return False


def unsure_passage(o: dict) -> bool:
    """A passage the reading is not sure of: a gap of unclassified content, or a door read only from parallel lines
    without a swing arc (``operation`` sliding from geometry, no block name: a window's frame and glass lines draw
    the same)."""
    if o.get("type") == "opening" and str(o.get("type_raw") or "") == "unclassified gap content":
        return True
    if o.get("type") != "door" or o.get("operation") != "sliding" or o.get("operation_source") != "geometry":
        return False
    notes = " ".join(str(e.get("note") or "") for e in o.get("evidence") or [] if isinstance(e, dict))
    return "block name" not in notes


def gaps_behind_furniture(building: dict) -> list[str]:
    """27 Oct 2026 (pod run 224516, real06: the east wall's two 1.55 m windows, tagged "160/160" on the plan, were read
    as doorless gaps 2.1 m high; the architect makes them windows only at the build, so before it every drawn piece in
    front of them "blocked a door" and the drawn 3-seat sofa could not be built): a passage the reading is not sure of
    (``unsure_passage``: a gap of unclassified content, a sliding door read only from parallel lines) in a wall between
    a room and the outside, with drawn
    furniture standing across its approach (``GAP_APPROACH_M`` into the room),
    is no passage when the pieces leave no free stretch of ``GAP_FREE_MIN_M`` across its width: the drawing puts a
    piece there. It is read as a window at the level's usual sill and height
    (``typical_window``, else 0.90 / 1.20 m), ``corrected_by_ai`` by code with the pieces as evidence, the drawn values
    kept. Pure, in place; returns the reasons."""
    from shapely.geometry import Polygon, box as sbox
    from shapely.ops import unary_union

    plan = Plan(building)
    out = []
    pieces = []
    for f in building.get("furniture") or []:
        fp = f.get("footprint") or {}
        if f.get("source") != "from_documents" or f.get("build") is False or f.get("inferred_as") in NOT_A_PIECE \
                or f.get("type") in NOT_A_PIECE or not fp.get("size"):
            continue
        w, d = (float(v) for v in fp["size"][:2])
        if max(w, d) < GAP_PIECE_MIN_M:
            continue
        a = math.radians(float(fp.get("rotation_deg") or 0.0))
        c, sn = math.cos(a), math.sin(a)
        cx, cy = (float(v) for v in fp["center"][:2])
        poly = Polygon([(cx + x * c - y * sn, cy + x * sn + y * c)
                        for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])
        pieces.append((f, poly))
    for o in building.get("openings") or []:
        if not unsure_passage(o):
            continue
        wall = plan.walls.get(o.get("wall_id"))
        sides = window_sides(plan, o)
        if wall is None or len(sides) != 2 or sum(1 for r in sides if Plan.is_outside(r)) != 1:
            continue
        k = 1 if not Plan.is_outside(sides[0]) else -1
        room = sides[0] if k == 1 else sides[1]
        a0, u, _ = plan.axis(wall)
        n = (-u[1] * k, u[0] * k)
        t = plan.t_of(wall, o["center"])
        mid = (a0[0] + u[0] * t, a0[1] + u[1] * t)
        probe = (mid[0] - n[0] * (float(wall.get("thickness") or 0.2) / 2.0 + 0.5),
                 mid[1] - n[1] * (float(wall.get("thickness") or 0.2) / 2.0 + 0.5))
        if outdoor_space_at(building, probe, o.get("level_id")):
            continue                      # onto a drawn balcony, terrace or veranda: a passage
        half_w, face = float(o.get("width") or 0.0) / 2.0, float(wall.get("thickness") or 0.2) / 2.0
        corners = [(mid[0] + u[0] * s * half_w + n[0] * dd, mid[1] + u[1] * s * half_w + n[1] * dd)
                   for s, dd in ((-1, face), (1, face), (1, face + GAP_APPROACH_M), (-1, face + GAP_APPROACH_M))]
        zone = Polygon(corners)
        hits = [(f, poly) for f, poly in pieces if f.get("level_id") == o.get("level_id")
                and (f.get("room_id") in (None, room["id"])) and poly.intersects(zone)]
        if not hits or half_w <= 0:
            continue
        # the pieces' stretches along the wall inside the gap's width, merged; the widest free stretch left
        spans = []
        for _f, poly in hits:
            part = poly.intersection(zone)
            xs = [(x - mid[0]) * u[0] + (y - mid[1]) * u[1] for g in getattr(part, "geoms", [part])
                  if not g.is_empty and hasattr(g, "exterior") for x, y in g.exterior.coords]
            if xs:
                spans.append((max(min(xs), -half_w), min(max(xs), half_w)))
        spans.sort()
        free, at, span = 0.0, -half_w, 0.0
        for lo, hi in spans:
            if hi <= at:
                continue
            free = max(free, lo - at)
            span += hi - max(lo, at)
            at = hi
        free = max(free, half_w - at)
        if free >= GAP_FREE_MIN_M:
            continue                      # a walkway is left across it: it may be a passage
        typ = typical_window(plan, o.get("level_id")) or {}
        sill = float(typ.get("sill") or 0.9)
        height = float(typ.get("height") or 1.2)
        _keep_drawn(o, "type", "sill_height", "height", "threshold_z", "swing_side", "operation")
        ids = sorted(f["id"] for f, _p in hits)
        what = "gap" if o.get("type") == "opening" else "sliding door read from its lines (no swing arc)"
        reason = (f"{o['id']} (a {float(o.get('width') or 0):.2f} m {what} in the outer wall of {room['id']}): drawn "
                  f"{', '.join(ids)} stand(s) across its approach ({span:.2f} m of its width, at most {free:.2f} m free), so "
                  f"it is no passage: "
                  f"read as a window, sill {sill:.2f} m, height {height:.2f} m (the floor's windows)")
        o["type"], o["sill_height"], o["height"] = "window", round(sill, 3), round(height, 3)
        for key in ("threshold_z", "swing_side", "operation", "operation_source"):
            o.pop(key, None)
        o["corrected_by_ai"] = {"by": "code", "rule": "gap_behind_furniture", "reason": reason, "pieces": ids}
        ev = o.setdefault("evidence", [])
        if isinstance(ev, list):
            ev.append({"file": "building.json", "method": "inferred", "confidence": 0.7,
                       "rule": "gap_behind_furniture", "text": reason})
        out.append(reason)
    return out


def act_retype(plan: Plan, key: str, ans: dict, room_id: str, room_type: str):
    r = plan.room.get(room_id)
    if r is None or room_type not in ROOM_TYPES:
        return False, f"cannot retype {room_id} to {room_type!r}"
    if r.get("room_type") != room_type:
        r.setdefault("drawn_type", r.get("room_type"))
        r["room_type"] = room_type
        r["adjusted_by_ai"] = {"by": "architect", "answer_key": key, "answer_by": ans.get("by", "user"),
                               "answer": ans.get("answer"), "reason": f"the answer to {key}: a {room_type}"}
    return True, f"{room_id} is a {room_type}"


def _piece(plan: Plan, piece_id: str) -> Optional[dict]:
    return next((f for f in plan.b.get("furniture") or [] if f.get("id") == piece_id), None)


def act_stair_winders(plan: Plan, key: str, ans: dict, piece_id: str, count="auto"):
    """A U stair's half landing as winders (``count`` "auto": as many as comfortable risers need; 0: as drawn)."""
    f = _piece(plan, piece_id)
    if f is None or str(f.get("type")) != "stair":
        return False, f"no stair {piece_id}"
    data = f.get("stair") if isinstance(f.get("stair"), dict) else (f.get("details") or {}).get("stair")
    if not isinstance(data, dict):
        return False, f"{piece_id} has no stair record"
    data["winders"] = count if str(count) == "auto" else int(count)
    _mark(f, "adjusted_by_ai", key, ans, f"the answer to {key}: winders {count}")
    return True, f"{piece_id}: winders {count}"


def _space(plan: Plan, space_id: str) -> Optional[dict]:
    site = plan.b.get("site") if isinstance(plan.b.get("site"), dict) else {}
    return next((s for s in site.get("outdoor_spaces") or [] if s.get("id") == space_id or
                 s.get("area_id") == space_id), None)


def guard_segments(value) -> list[list[list[float]]]:
    """The edges of a ``guard_edge`` answer (pure): one edge ``[[x0, y0], [x1, y1]]`` or a list of them; [] when
    none is valid."""
    if not isinstance(value, (list, tuple)) or not value:
        return []
    edges = [value] if isinstance(value[0], (list, tuple)) and value[0] and \
        isinstance(value[0][0], (int, float)) else value
    out = []
    for e in edges:
        try:
            (x0, y0), (x1, y1) = [(float(p[0]), float(p[1])) for p in e]
        except (TypeError, ValueError, IndexError):
            continue
        if math.hypot(x1 - x0, y1 - y0) > 1e-3:
            out.append([[round(x0, 4), round(y0, 4)], [round(x1, 4), round(y1, 4)]])
    return out


def act_guard_edge(plan: Plan, key: str, ans: dict, space_id: str, edges):
    """27 Oct 2026 (Argus M10 O2 / O5): a guard on open edges of an outdoor space: each edge's two ends join the
    space's ``guard_edges`` (``site.platforms`` puts a railing on every platform edge on one of them, after the edges
    are split)."""
    sp = _space(plan, space_id)
    if sp is None:
        return False, f"no outdoor space {space_id}"
    segs = guard_segments(edges)
    if not segs:
        return False, f"no edge given for {space_id} (params.edges [[[x0, y0], [x1, y1]], ...])"
    guards = sp.setdefault("guard_edges", [])
    guards += [g for g in segs if g not in guards]
    _mark(sp, "adjusted_by_ai", key, ans, f"the answer to {key}: a guard on {len(segs)} edge(s)")
    return True, f"{sp['id']}: a guard on " + "; ".join(f"the edge from {g[0]} to {g[1]}" for g in segs)


def act_cover_space(plan: Plan, key: str, ans: dict, space_id: str):
    """27 Oct 2026 (Argus M10 O4): a covered kind left open gets a light roof over the part nothing above covers
    (``outdoor.roof_plan`` with cover ``roof``, the levels' outlines from the slabs) and its posts again."""
    from wenart.levels import outdoor as OD

    sp = _space(plan, space_id)
    if sp is None:
        return False, f"no outdoor space {space_id}"
    spaces = (plan.b.get("site") or {}).get("outdoor_spaces") or []
    outlines = {s.get("above_level_id"): s.get("outline") for s in plan.b.get("slabs") or []
                if s.get("above_level_id") and len(s.get("outline") or []) >= 3}
    was = sp.get("cover")
    sp["cover"] = "roof" if was not in ("roof", "glass", "pergola", "building") else was
    roof = OD.roof_plan(sp, spaces, list(plan.levels.values()), outlines, plan.b, [])
    if roof is None:
        sp["cover"] = was
        return False, f"{sp['id']}: nothing left to cover (the floors and spaces above cover it)"
    sp["roof"] = roof
    OD.assign_posts(spaces, lambda x, y: float(sp.get("z") or 0.0))
    _mark(sp, "adjusted_by_ai", key, ans, f"the answer to {key}: a light roof over {roof.get('area_m2')} m2")
    return True, f"{sp['id']}: a light roof over {roof.get('area_m2')} m2 ({roof.get('reason')})"


def act_remove_piece(plan: Plan, key: str, ans: dict, piece_id: str):
    """The piece is not built (an answer: it does not belong where it stands; 25 Oct 2026)."""
    f = _piece(plan, piece_id)
    if f is None:
        return False, f"no piece {piece_id}"
    f["build"] = False
    f["not_built_reason"] = f"the answer to {key}: not built"
    _mark(f, "adjusted_by_ai", key, ans, f"the answer to {key}: the piece is not built")
    return True, f"{piece_id} is not built"


def act_retype_piece(plan: Plan, key: str, ans: dict, piece_id: str, ftype: str):
    """The piece is another furniture type (the fit gives it a model of that type on the next fit)."""
    f = _piece(plan, piece_id)
    if f is None or not ftype:
        return False, f"cannot retype {piece_id} to {ftype!r}"
    if f.get("type") != ftype:
        f.setdefault("drawn_type", f.get("type"))
        f["type"] = ftype
        _mark(f, "adjusted_by_ai", key, ans, f"the answer to {key}: a {ftype}")
    return True, f"{piece_id} is a {ftype}"


def act_widen_door(plan: Plan, key: str, ans: dict, door_id: str, room_id: Optional[str] = None):
    o = plan.openings.get(door_id)
    w = plan.walls.get((o or {}).get("wall_id"))
    if o is None or w is None:
        return False, f"no door {door_id} on a wall"
    want = WC_DOOR_MIN_W if room_id and str(plan.room.get(room_id, {}).get("room_type")) in ("wc", "toilet") \
        else DOOR_MIN_W
    width = float(o.get("width") or 0.0)
    if width >= want:
        return True, f"{door_id} is {width:.2f} m wide"
    t = plan.t_of(w, o["center"])
    _a, _u, length = plan.axis(w)
    lo, hi = 0.1, length - 0.1
    for s0, s1 in plan.spans_on(w, skip=(door_id,)):
        if s1 <= t:
            lo = max(lo, s1 + 0.1)
        elif s0 >= t:
            hi = min(hi, s0 - 0.1)
    if hi - lo < want:
        return False, f"{door_id}: only {hi - lo:.2f} m of wall around it"
    nt = min(max(t, lo + want / 2.0), hi - want / 2.0)
    _keep_drawn(o, "width", "center")
    x, y = plan.at_t(w, nt)
    o["width"], o["center"] = want, [round(x, 4), round(y, 4)]
    _mark(o, "adjusted_by_ai", key, ans, f"widened from {width:.2f} to {want:.2f} m")
    return True, f"{door_id} {width:.2f} -> {want:.2f} m wide"


def act_raise_sill(plan: Plan, key: str, ans: dict, window_id: str):
    o = plan.openings.get(window_id)
    if o is None or o.get("type") != "window":
        return False, f"no window {window_id}"
    sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
    h = float(o.get("height") if o.get("height") is not None else 1.2)
    if sill >= SAFE_SILL_M:
        return True, f"{window_id}: sill {sill:.2f} m"
    head = sill + h
    if head - SAFE_SILL_M < MIN_WINDOW_H:
        return False, f"{window_id}: a sill at {SAFE_SILL_M:.2f} m leaves less than {MIN_WINDOW_H:.2f} m of window"
    _keep_drawn(o, "sill_height", "height")
    o["sill_height"], o["height"] = SAFE_SILL_M, round(head - SAFE_SILL_M, 3)
    _mark(o, "adjusted_by_ai", key, ans, f"sill raised from {sill:.2f} to {SAFE_SILL_M:.2f} m (head kept)")
    return True, f"{window_id}: sill {sill:.2f} -> {SAFE_SILL_M:.2f} m"


def _two_rooms(plan: Plan, o: dict) -> Optional[list]:
    """The two rooms an opening joins, or None when one side is outside (or the sides are unknown)."""
    sides = window_sides(plan, o)
    if len(sides) != 2 or any(r is None or Plan.is_outside(r) for r in sides):
        return None
    return sides


def act_interior_glazing(plan: Plan, key: str, ans: dict, window_id: str):
    """26 Oct 2026 (user: "let it take decisions more"): a window between two dry rooms is kept on purpose, a
    borrowed-light window with clear glass (``interior_glazing``); a window into a wet room needs ``high_window``."""
    o = plan.openings.get(window_id)
    if o is None or o.get("type") != "window":
        return False, f"no window {window_id}"
    rooms = _two_rooms(plan, o)
    if rooms is None:
        return False, f"{window_id} does not stand between two rooms"
    wet = [r["id"] for r in rooms if str(r.get("room_type") or "").lower() in WET_ROOMS]
    if wet:
        return False, f"{window_id} looks into the wet room {wet[0]}: it needs privacy (a high window)"
    o["interior_glazing"] = {"kind": "clear", "rooms": [r["id"] for r in rooms]}
    _mark(o, "adjusted_by_ai", key, ans, f"a borrowed-light window between {rooms[0]['id']} and {rooms[1]['id']} "
                                         f"on purpose (clear glass, kept where drawn)")
    return True, f"{window_id}: a borrowed-light window between {rooms[0]['id']} and {rooms[1]['id']}"


def act_high_window(plan: Plan, key: str, ans: dict, window_id: str):
    """26 Oct 2026: a window between a room and a wet room becomes a high borrowed-light window: its sill at
    ``HIGH_SILL_M`` (the head kept, at least ``MIN_HIGH_WINDOW_H`` of glass), so nobody looks into the bathroom."""
    o = plan.openings.get(window_id)
    if o is None or o.get("type") != "window":
        return False, f"no window {window_id}"
    rooms = _two_rooms(plan, o)
    if rooms is None:
        return False, f"{window_id} does not stand between two rooms"
    sill = float(o.get("sill_height") if o.get("sill_height") is not None else 0.9)
    head = min(sill + float(o.get("height") if o.get("height") is not None else 1.2), plan.top(o))
    if head - max(sill, HIGH_SILL_M) < MIN_HIGH_WINDOW_H:
        return False, (f"{window_id}: a sill at {HIGH_SILL_M:.2f} m under its {head:.2f} m head leaves less than "
                       f"{MIN_HIGH_WINDOW_H:.2f} m of window")
    if sill < HIGH_SILL_M:
        _keep_drawn(o, "sill_height", "height")
        o["sill_height"], o["height"] = HIGH_SILL_M, round(head - HIGH_SILL_M, 3)
    o["interior_glazing"] = {"kind": "high", "rooms": [r["id"] for r in rooms]}
    _mark(o, "adjusted_by_ai", key, ans, f"a high borrowed-light window between {rooms[0]['id']} and {rooms[1]['id']}: "
                                         f"sill {sill:.2f} -> {max(sill, HIGH_SILL_M):.2f} m (privacy), head kept")
    return True, f"{window_id}: a high window, sill {sill:.2f} -> {max(sill, HIGH_SILL_M):.2f} m"


def act_pass_through(plan: Plan, key: str, ans: dict, door_id: str):
    """26 Oct 2026: a doorway between two rooms that a drawn counter fills is a serving window over the counter: the
    door or gap becomes a window (same wall, centre and width, its head kept) with its sill at ``PASS_SILL_M``; the
    drawn values stay (``drawn_type`` ...), ``corrected_by_ai``. 27 Oct 2026 (user: "Not every opening inside the house
    requires a door or a window"): it is an open hatch, the build gives it no glass and no frame
    (``door_spacing.open_hatch``)."""
    o = plan.openings.get(door_id)
    if o is None or o.get("type") not in ("door", "opening"):
        return False, f"no door or gap {door_id}"
    rooms = _two_rooms(plan, o)
    if rooms is None:
        return False, f"{door_id} does not join two rooms"
    base = float(o.get("sill_height") or 0.0)
    head = min(base + float(o.get("height") if o.get("height") is not None else 2.1), plan.top(o))
    if head - PASS_SILL_M < MIN_WINDOW_H:
        return False, f"{door_id}: a sill at {PASS_SILL_M:.2f} m leaves less than {MIN_WINDOW_H:.2f} m of opening"
    _keep_drawn(o, "type", "sill_height", "height")
    o["type"] = "window"
    o["sill_height"], o["height"] = PASS_SILL_M, round(head - PASS_SILL_M, 3)
    o["interior_glazing"] = {"kind": "pass_through", "rooms": [r["id"] for r in rooms]}
    for k in ("swing_side", "operation", "threshold_z"):
        o.pop(k, None)
    _mark(o, "corrected_by_ai", key, ans, f"a serving window over the drawn counter between {rooms[0]['id']} and "
                                          f"{rooms[1]['id']}: sill {PASS_SILL_M:.2f} m, head {head:.2f} m")
    return True, f"{door_id}: a serving window over the counter, sill {PASS_SILL_M:.2f} m"


def act_door_to_window(plan: Plan, key: str, ans: dict, door_id: str):
    """An outside door or a bare gap with nothing outside it (a drop, no balcony, terrace or steps) becomes a window
    (26 Oct 2026, user on real06's upper floor: "are the people going to jump off from it?"): same wall, centre and
    width, its head kept, its sill at the floor's usual window sill (the median of the level's outside windows, else
    ``SAFE_SILL_M``). The drawn values stay (``drawn_type``, ``drawn_sill_height``, ...), ``corrected_by_ai``; the
    door's entrance record leaves the site (no steps, canopy or lights for a window)."""
    o = plan.openings.get(door_id)
    if o is None or o.get("type") not in ("door", "opening"):
        return False, f"no door or gap {door_id}"
    rooms = _two_rooms(plan, o)
    if rooms is not None:
        # 27 Oct 2026 (user: "Not every opening inside the house requires a door or a window"): a door or a passage
        # between two rooms of the house is never made a window (a doorway a drawn counter fills: ``pass_through``)
        return False, (f"{door_id} joins {rooms[0]['id']} and {rooms[1]['id']} inside the house: a door or passage "
                       f"between two rooms is never made a window")
    typ = typical_window(plan, o.get("level_id"))
    sill = float(typ["sill"]) if typ and 0.6 <= float(typ["sill"]) <= 1.2 else SAFE_SILL_M
    base = float(o.get("sill_height") or 0.0)
    head = min(base + float(o.get("height") if o.get("height") is not None else 2.1), plan.top(o))
    if head - sill < MIN_WINDOW_H:
        sill = max(0.6, head - MIN_WINDOW_H)
    if head - sill < MIN_WINDOW_H - 1e-6:
        return False, f"{door_id}: {head:.2f} m of wall under the ceiling leaves no window"
    was = o.get("type")
    _keep_drawn(o, "type", "sill_height", "height", "threshold_z", "operation", "swing_side")
    o["type"], o["sill_height"], o["height"] = "window", round(sill, 3), round(head - sill, 3)
    for k in ("threshold_z", "operation", "operation_source", "swing_side"):
        o.pop(k, None)
    reason = (f"{door_id} ({was}, {float(o.get('width') or 0):.2f} m) opens onto nothing outside: read as a window, "
              f"sill {sill:.2f} m, head {head:.2f} m (the floor's windows)")
    _mark(o, "corrected_by_ai", key, ans, reason)
    site = plan.b.get("site") if isinstance(plan.b.get("site"), dict) else None
    if site is not None and isinstance(site.get("entrances"), list):
        gone = [e for e in site["entrances"] if isinstance(e, dict) and e.get("door_id") == door_id]
        if gone:
            site["entrances"] = [e for e in site["entrances"] if e not in gone]
            site.setdefault("entrances_removed", []).extend(dict(e, removed_by=f"architect {key}") for e in gone)
    return True, reason


def act_gap_to_door(plan: Plan, key: str, ans: dict, door_id: str):
    """A bare gap in an outer wall at its floor onto the ground or a terrace: a glazed door (sliding from 1.40 m
    wide) the reading did not see (26 Oct 2026); the drawn type stays (``drawn_type``), ``corrected_by_ai``."""
    o = plan.openings.get(door_id)
    if o is None or o.get("type") != "opening" or o.get("virtual") or o.get("wall_id") not in plan.walls:
        return False, f"no gap {door_id} in a wall"
    width = float(o.get("width") or 0.0)
    rooms = _two_rooms(plan, o)
    if rooms is not None:
        # 27 Oct 2026 (user: "Not every opening inside the house requires a door or a window"; real06: the AI made the
        # 2.00 m passage between the two upper halls a glazed door with a guard): a gap inside the house, drawn with no
        # leaf and no swing arc, stays an open passage; it gets a door only where a room needs privacy (a bathroom, a
        # WC, a bedroom: ``door_spacing.PRIVACY_ROOMS``), one solid leaf (D5 decides a pair when it is wide), never
        # glass, and never a frame against another door
        from wenart.blender import door_spacing as DS
        private = [r["id"] for r in rooms if DS.needs_privacy(r)]
        if not private:
            return False, (f"{door_id}: an open passage between {rooms[0]['id']} and {rooms[1]['id']} (no leaf or "
                           f"swing drawn, neither room needs privacy): it stays open")
        before = copy.deepcopy(o)
        _keep_drawn(o, "type", "operation")
        o["type"], o["operation"], o["operation_source"] = "door", "swing", "architect"
        o.pop("glazed", None)
        o["privacy_door"] = {"rooms": private, "unclear_gap": DS.unclear_gap(o)}
        reason = (f"{door_id}: a {width:.2f} m gap into {', '.join(private)} with no leaf drawn"
                  + (" (unclear lines in it)" if DS.unclear_gap(o) else "") + ": a door for its privacy (one solid "
                  "swing leaf)")
        _mark(o, "corrected_by_ai", key, ans, reason)
        clash = [r for r in DS.conflicts(plan.b, ids={door_id})[0] if r["kind"] in ("overlap", "frames")]
        if clash:
            o.clear()
            o.update(before)
            return False, f"{door_id} as a door: {clash[0]['message']}"
        return True, reason
    _keep_drawn(o, "type", "operation")
    o["type"], o["operation"], o["glazed"] = "door", "sliding" if width >= 1.4 else "swing", True
    o["operation_source"] = "architect"
    reason = f"{door_id}: a bare {width:.2f} m gap in the facade at its floor: a glazed {o['operation']} door"
    _mark(o, "corrected_by_ai", key, ans, reason)
    return True, reason


def act_window_to_door(plan: Plan, key: str, ans: dict, window_id: str):
    """A window between two rooms, one of which no door reaches (a dressing room, an en-suite shower): it is that
    room's door (26 Oct 2026), at least ``WC_DOOR_MIN_W`` wide where the wall allows, 2.10 m high, on the floor
    of its rooms; the drawn values stay, ``corrected_by_ai``."""
    o = plan.openings.get(window_id)
    if o is None or o.get("type") != "window":
        return False, f"no window {window_id}"
    sides = window_sides(plan, o)
    if len(sides) != 2 or any(r is None or Plan.is_outside(r) for r in sides):
        return False, f"{window_id} is not between two rooms"
    # 27 Oct 2026 (user on real06: "doors next to each other not making sense": the AI made the windows on both sides
    # of the door between a shower room and a dressing room doors, three doors side by side): a window is the door of
    # a room no door reaches, never a second door of two rooms a door or doorway joins already, and never a door whose
    # frame touches another door (``door_spacing``: two frames of wall between two doors)
    from wenart.blender import door_spacing as DS
    joined = DS.joined_by(plan.b, [r["id"] for r in sides], skip=(window_id,))
    if joined:
        return False, (f"{window_id}: {sides[0]['id']} and {sides[1]['id']} are joined by {', '.join(joined)} already: "
                       f"a window beside their door stays a window")
    before = copy.deepcopy(o)
    _keep_drawn(o, "type", "sill_height", "height")
    floors = [z for z in (room_floor(plan, r) for r in sides) if z is not None]
    o["type"], o["sill_height"], o["height"], o["operation"] = "door", None, 2.1, "swing"
    o["threshold_z"] = round(max(floors), 4) if floors else None
    reason = f"{window_id} between {sides[0]['id']} and {sides[1]['id']}: the door of the room no door reached"
    _mark(o, "corrected_by_ai", key, ans, reason)
    if float(o.get("width") or 0.0) < WC_DOOR_MIN_W:
        act_widen_door(plan, key, ans, window_id, sides[0]["id"])
    clash = [r for r in DS.conflicts(plan.b, ids={window_id})[0] if r["kind"] in ("overlap", "frames")]
    if clash:
        o.clear()
        o.update(before)
        return False, f"{window_id} as a door: {clash[0]['message']}"
    return True, reason


def act_merge_openings(plan: Plan, key: str, ans: dict, opening_id: str, other_id: str):
    """Two openings over each other on one wall (one read twice): the first takes both spans, the second is not
    built (``drawn_*`` kept on both; 26 Oct 2026)."""
    o, p = plan.openings.get(opening_id), plan.openings.get(other_id)
    w = plan.walls.get((o or {}).get("wall_id"))
    if o is None or p is None or w is None or p.get("wall_id") != o.get("wall_id"):
        return False, f"{opening_id} and {other_id} are not on one wall"
    ends = []
    for x in (o, p):
        t, h = plan.t_of(w, x["center"]), float(x.get("width") or 0.0) / 2.0
        ends += [t - h, t + h]
    t0, t1 = min(ends), max(ends)
    _keep_drawn(o, "width", "center")
    x, y = plan.at_t(w, (t0 + t1) / 2.0)
    o["width"], o["center"] = round(t1 - t0, 3), [round(x, 4), round(y, 4)]
    _mark(o, "corrected_by_ai", key, ans, f"one opening with {other_id} (read twice): {t1 - t0:.2f} m wide")
    plan.b["openings"] = [x for x in plan.b.get("openings") or [] if x["id"] != other_id]
    plan.openings.pop(other_id, None)
    plan.b.setdefault("openings_merged", []).append(dict(p, merged_into=opening_id))
    return True, f"{opening_id} and {other_id} merged ({t1 - t0:.2f} m)"


def act_french_window(plan: Plan, key: str, ans: dict, door_id: str):
    """A full-height opening over a drop kept as a French window: a guard across its whole width, ``GUARD_TOP_M``
    over its floor, in the house's balustrade language (``facade.guard_boxes`` builds it with
    ``details.balustrade_kind``; 26 Oct 2026: two thin bars were no guard)."""
    o = plan.openings.get(door_id)
    if o is None or o.get("type") not in ("door", "opening", "window"):
        return False, f"no opening {door_id}"
    rooms = _two_rooms(plan, o)
    if rooms is not None:
        # 27 Oct 2026 (real06: the AI put glass guards across a passage and two windows between rooms of one floor): a
        # guard stands only over a drop; between two rooms whose floors differ by at most a step there is none
        from wenart.blender import door_spacing as DS
        zs = [room_floor(plan, r) or 0.0 for r in rooms]
        if abs(zs[0] - zs[1]) <= DS.STEP_M:
            return False, (f"{door_id} joins {rooms[0]['id']} and {rooms[1]['id']} on one floor: no drop, no guard "
                           f"(a guard stands only over a drop)")
    o["guard"] = {"top_m": GUARD_TOP_M, "kind": "balustrade", "reason": f"the answer to {key}: a French window with "
                                                                         f"a guard"}
    _mark(o, "adjusted_by_ai", key, ans, f"a French window: a guard {GUARD_TOP_M:.2f} m high across its width")
    return True, f"{door_id}: a guard across its width"


# --------------------------------------------------------------------------
# D5: what kind of door every outside door and every wide door is (26 Oct 2026)
# --------------------------------------------------------------------------
#
# User on real06 (26 Oct 2026, a render circled: "these sections not making sense"): the living room's 2.95 m outside
# door got no library model and the parametric builder made one flat oak leaf as wide as the opening: a garage door
# on a house that has no garage. An architect decides the kind of every outside door (the room behind it says it)
# and never draws one leaf much wider than 1.2 m; the drawn operation stays the anchor (a drawn sliding door stays a
# sliding door, now glazed panels instead of one slab). ``architect_rules.door_types`` asks, ``act_door_type`` builds.

WIDE_DOOR_M = 1.4               # from this width a door is more than one leaf (= opening_models.WIDE_DOOR_M)
LEAF_MAX_M = 1.2                # no leaf or sliding panel wider than about this
FRENCH_MAX_M = 2.4              # a pair of glazed swing leaves up to this width (two leaves of 1.2 m); wider: sliding
FOLDING_LEAF_M = 0.9            # a folding door's leaves at most this wide
GARAGE_DOOR_MIN_M = 2.2         # a door this wide into a garage, a carport or a service room: a sectional door
DOOR_FRAMES_M = 0.11            # the two jambs and the clearances of a door frame (2 x 0.05 + 0.01)
GARAGE_ROOMS = ("garage", "carport")
SERVICE_ROOMS = GARAGE_ROOMS + ("storage", "store", "technical", "plant", "boiler", "utility", "shed", "workshop",
                                "cellar", "laundry")
DOOR_KINDS = {                  # kind -> the build's door style, operation, glass and what the report says
    "french": {"style": "double", "operation": "double", "glazed": True,
               "label": "French doors: two glazed swing leaves"},
    "glazed_sliding": {"style": "glazed_sliding", "operation": "sliding", "glazed": True,
                       "label": "a glazed sliding door: glazed panels of at most 1.2 m in the frame, one fixed"},
    "glazed_folding": {"style": "folding", "operation": "folding", "glazed": True,
                       "label": "a glazed folding door: glazed leaves of at most 0.9 m"},
    "entrance": {"style": "entrance", "operation": "swing", "glazed": False,
                 "label": "the entrance door: one entrance leaf, glazed side lights where the opening is wider"},
    "garage_sectional": {"style": "sectional", "operation": "sectional", "glazed": False,
                         "label": "a sectional garage door: horizontal panels"},
    "double": {"style": "double", "operation": "double", "glazed": False, "label": "a pair of swing leaves"},
    "sliding_pair": {"style": "sliding", "operation": "sliding", "glazed": False,
                     "label": "sliding leaves of at most 1.2 m parting in the middle"},
    "folding": {"style": "folding", "operation": "folding", "glazed": False,
                "label": "a folding door: leaves of at most 0.9 m"},
}
GLAZED_KINDS = ("french", "glazed_sliding", "glazed_folding")


def drawn_operation(o: dict) -> Optional[str]:
    """The operation the drawing gives a door (``drawn_operation`` once an answer changed it), lower case; None for
    none (a gap the architect made a door)."""
    op = o.get("drawn_operation") if "drawn_operation" in o else o.get("operation")
    return str(op).lower() if op else None


def door_leaves(kind: str, width: float) -> int:
    """How many leaves or panels a door of ``kind`` gets in an opening ``width`` wide (pure): two for a pair, sliding
    panels and folding leaves no wider than ``LEAF_MAX_M`` / ``FOLDING_LEAF_M`` (at least two), one otherwise."""
    clear = max(0.0, float(width) - DOOR_FRAMES_M)
    if kind in ("french", "double"):
        return 2
    if kind in ("glazed_sliding", "sliding_pair"):
        return max(2, int(math.ceil(clear / LEAF_MAX_M - 1e-9)))
    if kind in ("glazed_folding", "folding"):
        return max(2, int(math.ceil(clear / FOLDING_LEAF_M - 1e-9)))
    return 1


def main_entrance_id(building: dict) -> Optional[str]:
    """The main entrance door (``site.entrances``: the one marked ``main``, else the first; a door into the air or
    below the ground is none), as ``opening_models.categorise`` reads it."""
    recs = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
            and not r.get("into_air") and not r.get("below_ground")]
    main = next((r.get("door_id") for r in recs if r.get("main")), None)
    return main if main is not None or not recs else recs[0].get("door_id")


def door_kind(width: float, rooms: list, outer: bool, main: bool, op: Optional[str]
              ) -> tuple[Optional[str], str, list]:
    """``(kind, why, other kinds)`` of a door (pure): ``rooms`` the types of the rooms it joins (an outside door: the
    room behind it), ``outer`` to the outside or an open-air room, ``main`` the main entrance, ``op`` its drawn
    operation. ``kind`` None: one leaf is right (``why`` says so).

    - an outside door into a garage, a carport or a service room (``SERVICE_ROOMS``): ``GARAGE_DOOR_MIN_M`` or wider a
      sectional garage door; from ``WIDE_DOOR_M`` a pair of leaves (a drawn sliding or folding door keeps its way);
    - the main entrance (not drawn sliding, folding or double): the entrance door (side lights when it is wider);
    - an outside door of ``WIDE_DOOR_M`` or more into any other room: glazed: a drawn sliding door a glazed sliding
      door, a drawn folding door a glazed folding door, a drawn pair French doors, else French doors up to
      ``FRENCH_MAX_M`` and a glazed sliding door when wider;
    - an inside door of ``WIDE_DOOR_M`` or more: two sliding leaves for a drawn sliding door, folding leaves for a
      drawn folding door, a pair of swing leaves otherwise (a drawn pocket door stays one leaf)."""
    w = float(width)
    op = (op or "").lower() or None
    as_drawn = "one leaf" if op in (None, "swing", "unknown") else f"its drawn {op} door"
    if outer:
        t = str((rooms or [""])[0] or "").lower()
        if t in SERVICE_ROOMS:
            if w + 1e-6 >= GARAGE_DOOR_MIN_M:
                return "garage_sectional", (f"a {w:.2f} m outside door into the {t}: a sectional garage door, "
                                            f"never one leaf"), ["double"]
            if w + 1e-6 >= WIDE_DOOR_M:
                k = {"sliding": "sliding_pair", "folding": "folding"}.get(op or "", "double")
                return k, f"a {w:.2f} m outside door into the {t}: {DOOR_KINDS[k]['label']}", \
                    [x for x in ("double", "garage_sectional") if x != k]
            return None, f"a {w:.2f} m outside door into the {t}: {as_drawn}", []
        if main and op in (None, "swing", "unknown"):
            return "entrance", (f"the main entrance ({w:.2f} m, into the {t or 'house'}): the entrance door"
                                + (", glazed side lights beside one leaf" if w - DOOR_FRAMES_M > LEAF_MAX_M + 0.05
                                   else "")), ["french"] if w + 1e-6 >= WIDE_DOOR_M else []
        if w + 1e-6 < WIDE_DOOR_M:
            return None, f"a {w:.2f} m outside door{' (the main entrance)' if main else ''}: {as_drawn}", []
        note = f" (the main entrance record names this drawn {op} door)" if main else ""
        if op == "sliding":
            k = "glazed_sliding"
        elif op == "folding":
            k = "glazed_folding"
        elif op == "double" or w <= FRENCH_MAX_M + 1e-6:
            k = "french"
        else:
            k = "glazed_sliding"
        why = (f"a {w:.2f} m outside door into the {t or 'room'}{note}"
               + (f", drawn {op}" if op in ("sliding", "folding", "double") else "")
               + f": {DOOR_KINDS[k]['label']}, never one leaf as wide as the opening")
        return k, why, [x for x in GLAZED_KINDS if x != k]
    if w + 1e-6 < WIDE_DOOR_M or op == "pocket":
        return None, f"a {w:.2f} m inside door: {as_drawn}", []
    k = {"sliding": "sliding_pair", "folding": "folding"}.get(op or "", "double")
    names = " and ".join(str(x or "?") for x in rooms) or "two rooms"
    return k, f"a {w:.2f} m inside door between {names}: {DOOR_KINDS[k]['label']}, never one leaf as wide as the " \
              f"opening", [x for x in ("double", "sliding_pair", "french", "glazed_sliding") if x != k]


def act_door_type(plan: Plan, key: str, ans: dict, door_id: str, kind: str):
    """D5: the door becomes a door of ``kind`` (``DOOR_KINDS``): ``door_type``, the build's ``door_style``,
    ``glazed``, ``leaves`` (``door_leaves``), ``sidelights`` (the entrance) and the operation of the kind (the drawn
    one kept in ``drawn_operation``); ``door_decision`` records the rule, whether it is an outside door (its glazed
    leaves or panels take the windows' frame finish, ``looks.door_look``), the answer and the reason. A door another
    answer made a window has nothing to decide."""
    o = plan.openings.get(door_id)
    spec = DOOR_KINDS.get(kind)
    if o is None:
        return False, f"no door {door_id}"
    if o.get("type") != "door":
        return True, None
    if spec is None:
        return False, f"{door_id}: unknown door kind {kind!r}"
    width = float(o.get("width") or 0.0)
    sides = window_sides(plan, o)
    outs = [Plan.is_outside(r) for r in sides]
    outer = len(sides) == 2 and outs[0] != outs[1]
    leaves = door_leaves(kind, width)
    if o.get("operation") != spec["operation"]:
        _keep_drawn(o, "operation", "operation_source")
        o["operation"], o["operation_source"] = spec["operation"], "architect"
    for f in ("door_style", "glazed", "leaves", "sidelights"):
        if f in o:
            _keep_drawn(o, f)
    o["door_type"], o["door_style"], o["glazed"], o["leaves"] = kind, spec["style"], spec["glazed"], leaves
    if kind == "entrance":
        o["sidelights"] = True
    else:
        o.pop("sidelights", None)
    reason = (f"{door_id} ({width:.2f} m, {'an outside door' if outer else 'an inside door'}): {spec['label']}"
              + (f", {leaves} {'panels' if kind == 'glazed_sliding' else 'leaves'}" if leaves > 1 else ""))
    o["door_decision"] = {"by": "architect", "rule": "architect D5", "kind": kind, "outer": outer,
                          "answer_key": key, "answer_by": ans.get("by", "user"), "answer": ans.get("answer"),
                          "found": ans.get("reason"), "reason": reason}
    if isinstance(o.get("adjusted_by_ai"), dict) or isinstance(o.get("corrected_by_ai"), dict):
        ev = o.setdefault("evidence", [])                # an earlier answer's record stays; this one is the decision
        if isinstance(ev, list):
            ev.append({"file": ANSWERS_FILE if ans.get("by", "user") == "user" else AI_ANSWERS, "method": "inferred",
                       "confidence": 0.6, "rule": f"architect {key}", "text": reason})
    else:
        _mark(o, "adjusted_by_ai", key, ans, reason)
    return True, reason


def room_floor(plan: Plan, room: Optional[dict]) -> Optional[float]:
    """A room's floor z (its level's elevation + ``floor_offset_m``), None for no room."""
    if room is None:
        return None
    lv = plan.levels.get(room.get("level_id")) or {}
    return float(lv.get("elevation") or 0.0) + float(room.get("floor_offset_m") or 0.0)


def act_snap_threshold(plan: Plan, key: str, ans: dict, door_id: str):
    """The door's threshold at the floor of its rooms (the higher one where they differ): a threshold that matches
    neither floor is a reading error (26 Oct 2026, user: "why doors are up")."""
    o = plan.openings.get(door_id)
    if o is None or o.get("type") not in ("door", "opening"):
        return False, f"no door {door_id}"
    floors = [z for z in (room_floor(plan, r) for r in window_sides(plan, o)) if z is not None]
    if not floors:
        return False, f"{door_id}: no room beside it"
    want = round(max(floors), 4)
    old = o.get("threshold_z")
    if old is not None and abs(float(old) - want) <= 0.005:
        return True, f"{door_id}: threshold {want:+.2f} m"
    _keep_drawn(o, "threshold_z")
    o["threshold_z"] = want
    _mark(o, "corrected_by_ai", key, ans, f"threshold {float(old or 0):+.2f} -> {want:+.2f} m (the floor of its rooms)")
    return True, f"{door_id}: threshold {float(old or 0):+.2f} -> {want:+.2f} m"


def fitted_height(f: dict) -> Optional[float]:
    """The height of the library model built for a piece (the fit's ``asset.bbox_m``), None without one (a
    parametric or module piece is built at its working heights by its builder)."""
    a = f.get("asset") if isinstance(f.get("asset"), dict) else {}
    if str(a.get("asset_id") or "").startswith("parametric") or a.get("method") not in (None, "library"):
        return None
    bb = a.get("bbox_m")
    if isinstance(bb, (list, tuple)) and len(bb) >= 3 and bb[2]:
        return float(bb[2])
    return None


def act_mount_fixture(plan: Plan, key: str, ans: dict, piece_id: str):
    """A fixture at its working height: a wall-hung washbasin model (shorter than its rim height) hangs with its
    rim at ``BASIN_RIM_M`` (``mount_bottom_m``; the build hangs it there). A bowl too shallow to hang alone (a
    vessel basin under 0.30 m) cannot: the piece needs another model or a vanity."""
    f = _piece(plan, piece_id)
    if f is None:
        return False, f"no piece {piece_id}"
    rule = FIXTURE_TOPS.get(str(f.get("type") or ""))
    h = fitted_height(f)
    if rule is None or h is None:
        return False, f"{piece_id}: no working height to check"
    low, high, target = rule
    top = h + float(f.get("mount_bottom_m") or 0.0)
    if top >= low:
        return True, f"{piece_id}: top at {top:.2f} m"
    if h < 0.30:
        return False, f"{piece_id}: a {h:.2f} m bowl needs a vanity or another model (it cannot hang alone)"
    _keep_drawn(f, "mount_bottom_m")
    f["mount_bottom_m"] = round(target - h, 3)
    _mark(f, "adjusted_by_ai", key, ans, f"hung with its top at {target:.2f} m (the model is {h:.2f} m tall; it "
                                        f"stood on the floor with its rim at {top:.2f} m)")
    return True, f"{piece_id}: rim {top:.2f} -> {target:.2f} m"


MOVE_NEAR_M = 1.0                 # a piece this close to an opening's centre is in its doorway or window strip


def _strip_of(plan: Plan, o: dict) -> list:
    """The doorway (``clashes.DOOR_DEPTH_M`` deep) or window strip (0.5 m) of opening ``o`` on both faces of its
    wall, as rectangles (pure); [] without its wall."""
    from wenart.blender import architect_rules as RR
    from wenart.blender import clashes as CL

    w = plan.walls.get(o.get("wall_id"))
    if w is None:
        return []
    _a, u, _l = plan.axis(w)
    n = (-u[1], u[0])
    c = plan.at_t(w, plan.t_of(w, o["center"]))
    half_t = float(w.get("thickness") or 0.2) / 2.0
    depth = CL.DOOR_DEPTH_M if o.get("type") != "window" else 0.5
    return [RR._box((c[0] + n[0] * sgn * half_t, c[1] + n[1] * sgn * half_t), u, (n[0] * sgn, n[1] * sgn),
                    float(o.get("width") or 0.9), depth) for sgn in (1.0, -1.0)]


def move_targets(plan: Plan, piece_id: str, text: str = "") -> list[str]:
    """What a ``move_piece`` answer moves the piece away from (pure; 27 Oct 2026, run 180412: every move decision of
    the AI failed with "no opening None": the decision never carried its opening): the openings and the other pieces
    of its level that ``text`` (the answer's value and reason) names, in order; else the openings of its level within
    ``MOVE_NEAR_M`` of the piece's plan shape, nearest first."""
    import re

    from shapely.geometry import Point, Polygon

    from wenart.blender import clashes as CL

    f = _piece(plan, piece_id)
    if f is None or not f.get("footprint"):
        return []
    lv = f.get("level_id")
    pieces = {g.get("id"): g for g in plan.b.get("furniture") or [] if g.get("level_id") == lv and g is not f}
    out = []
    for tok in re.findall(r"[A-Za-z0-9_\-]+", text or ""):
        if tok in out or tok == piece_id:
            continue
        if (plan.openings.get(tok) or {}).get("level_id") == lv or tok in pieces:
            out.append(tok)
    if out:
        return out
    parts = [Polygon(q) for q in CL.shape(f) if len(q) >= 3]
    near = []
    for o in plan.openings.values():
        if o.get("level_id") != lv or not o.get("center"):
            continue
        d = min((pp.distance(Point(o["center"][:2])) for pp in parts), default=1e9)
        if d <= MOVE_NEAR_M:
            near.append((round(d, 6), o["id"]))
    return [i for _d, i in sorted(near)]


def act_move_piece(plan: Plan, key: str, ans: dict, piece_id: str, away_from=None):
    """The piece moved the shortest way out of the doorway or the window strip of the openings ``away_from`` names
    and off the pieces it names (ids, a list or comma separated; 27 Oct 2026: a piece too, e.g. a basin over a
    drawn bath) to a free place in its room (``clashes.find_unit_place``: inside the room, clear of the other pieces
    and the doorways; at most 0.5 m for a drawn piece, 1 m for an added one)."""
    from wenart.blender import clashes as CL

    f = _piece(plan, piece_id)
    if f is None or not f.get("footprint"):
        return False, f"no piece {piece_id}"
    ids = [x.strip() for x in (away_from.split(",") if isinstance(away_from, str) else away_from or []) if x.strip()]
    box = []
    for i in ids:
        if i in plan.openings:
            box += _strip_of(plan, plan.openings[i])
        else:
            g = _piece(plan, i)
            if g is not None and g is not f and g.get("footprint"):
                box += CL.shape(g)
    if not box:
        return False, f"{piece_id}: no opening or piece {away_from} to move away from"
    away_from = ", ".join(ids)
    room = plan.room.get(f.get("room_id"))
    peers = [(g, CL.shape(g)) for g in plan.b.get("furniture") or [] if g is not f and g.get("build") is not False
             and g.get("footprint") and g.get("level_id") == f.get("level_id")
             and str(g.get("type") or "") not in CL.FLOOR_ONLY + CL.SKIP_TYPES]
    doors = [d for d in CL.doorways(plan.b, f.get("level_id"))]
    move = CL.find_unit_place([f], box, peers, {f.get("room_id"): room["polygon"]} if room else {}, doors)
    if move is None:
        return False, f"{piece_id}: no free place within the move limit clear of {away_from}"
    dx, dy, dist = move
    reason = f"moved {dist:.2f} m clear of {away_from} (the answer to {key})"
    f.setdefault("drawn_footprint", copy.deepcopy(f["footprint"]))
    f["footprint"] = CL._moved(f, dx, dy)["footprint"]
    _mark(f, "adjusted_by_ai", key, ans, reason)
    for d in plan.b.get("decor") or []:
        if d.get("host_id") == piece_id and d.get("center"):
            cc = list(d["center"])
            cc[0], cc[1] = round(float(cc[0]) + dx, 4), round(float(cc[1]) + dy, 4)
            d["center"] = cc
    return True, f"{piece_id}: {reason}"


# --------------------------------------------------------------------------
# Carrying the answers out
# --------------------------------------------------------------------------

def centre_of(plan: Plan, element: str):
    if element in plan.room:
        poly = plan.room[element]["polygon"]
        return sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    if element in plan.openings:
        return tuple(plan.openings[element]["center"][:2])
    return None


def resolve(plan: Plan, element: str, where: Optional[dict]) -> Optional[str]:
    """The element an answer names: its id, when it is still where the answer saw it (``where``, within
    ``WHERE_TOL_M``); else (ids change between readings of the plan) the room or opening of the same level at or
    nearest to ``where`` (within 1 m); None when nothing is there."""
    here = centre_of(plan, element)
    if here is None and (not isinstance(where, dict) or where.get("kind") not in ("room", "window", "door")):
        return element                  # a wall, a piece, a tree, a platform, the plan: by its id
    if here is not None:
        if not isinstance(where, dict) or not where.get("centre") or (
                G.distance(here, where["centre"][:2]) <= WHERE_TOL_M
                and where.get("level_id") in (None, (plan.room.get(element) or plan.openings.get(element) or {})
                                              .get("level_id"))):
            return element
    if not isinstance(where, dict) or not where.get("centre"):
        return None
    cx, cy = where["centre"][:2]
    lid = where.get("level_id")
    if where.get("kind") == "room":
        r = plan.room_at((cx, cy), lid)
        return r["id"] if r else None
    best = None
    for o in plan.openings.values():
        if o.get("level_id") == lid and where.get("kind") in (None, o.get("type")):
            d = G.distance(o["center"], (cx, cy))
            if d <= 1.0 and (best is None or d < best[0]):
                best = (d, o["id"])
    return best[1] if best else None


def apply_answers(building: dict, answers: dict, head_limit=None) -> list[dict]:
    """Carry ``answers`` (``answers_of``) out on ``building`` (pure; in place), in the order of their keys; windows
    are sized under ``head_limit(opening)`` (the roof over them: ``roof.opening_head_limit``; None: the ceiling).
    Returns ``[{"key", "option", "ok", "change", "by", "element"}]``; an answer whose element is gone or whose
    action fails has ``ok`` False and the reason."""
    out = []
    plan = Plan(building, head_limit)
    for key in sorted(answers, key=lambda k: (k.partition(":")[0] not in FIRST_RULES, k)):
        ans = answers[key]
        rule, _sep, element = key.partition(":")
        opt = ans.get("option") or "keep"
        params = dict(ans.get("params") or {})
        rec = {"key": key, "rule": rule, "option": opt, "by": ans.get("by", "user"), "answer": ans.get("answer")}
        target = resolve(plan, element, ans.get("where"))
        rec["element"] = target or element
        if target is None:
            rec.update(ok=False, skipped=True, change=f"{element} is not in this reading of the plan (nothing at the "
                                                      f"place the answer named)")
        elif opt == "keep":
            rec.update(ok=True, change=None)
        else:
            try:
                if opt == "move_window_to_outer_wall":
                    ok, text = act_move_window(plan, key, ans, params.get("window_id") or target,
                                               params.get("room_id") or (target if target in plan.room else None))
                elif opt == "enlarge_windows":
                    ok, text = act_enlarge(plan, key, ans, params.get("room_id") or target)
                elif opt == "retype_room":
                    ok, text = act_retype(plan, key, ans, params.get("room_id") or target,
                                          str(params.get("room_type") or ""))
                elif opt == "widen_door":
                    ok, text = act_widen_door(plan, key, ans, params.get("door_id") or target, params.get("room_id"))
                elif opt == "raise_sill":
                    ok, text = act_raise_sill(plan, key, ans, params.get("window_id") or target)
                elif opt == "stair_winders":
                    ok, text = act_stair_winders(plan, key, ans, params.get("piece_id") or target,
                                                 params.get("count", "auto"))
                elif opt == "remove_piece":
                    ok, text = act_remove_piece(plan, key, ans, params.get("piece_id") or target)
                elif opt == "retype_piece":
                    ok, text = act_retype_piece(plan, key, ans, params.get("piece_id") or target,
                                                str(params.get("type") or ""))
                elif opt == "door_to_window":
                    ok, text = act_door_to_window(plan, key, ans, params.get("door_id") or target)
                elif opt == "french_window":
                    ok, text = act_french_window(plan, key, ans, params.get("door_id") or target)
                elif opt == "snap_threshold":
                    ok, text = act_snap_threshold(plan, key, ans, params.get("door_id") or target)
                elif opt == "mount_fixture":
                    ok, text = act_mount_fixture(plan, key, ans, params.get("piece_id") or target)
                elif opt == "window_to_door":
                    ok, text = act_window_to_door(plan, key, ans, params.get("window_id") or target)
                elif opt == "gap_to_door":
                    ok, text = act_gap_to_door(plan, key, ans, params.get("door_id") or target)
                elif opt == "merge_openings":
                    ok, text = act_merge_openings(plan, key, ans, params.get("door_id") or target,
                                                  str(params.get("other_id") or ""))
                elif opt == "move_piece":
                    ok, text = act_move_piece(plan, key, ans, params.get("piece_id") or target,
                                              params.get("away_from"))
                elif opt == "interior_glazing":
                    ok, text = act_interior_glazing(plan, key, ans, params.get("window_id") or target)
                elif opt == "high_window":
                    ok, text = act_high_window(plan, key, ans, params.get("window_id") or target)
                elif opt == "pass_through":
                    ok, text = act_pass_through(plan, key, ans, params.get("door_id") or target)
                elif opt == "door_type":
                    ok, text = act_door_type(plan, key, ans, params.get("door_id") or target,
                                             str(params.get("kind") or ""))
                elif opt == "guard_edge":
                    ok, text = act_guard_edge(plan, key, ans, params.get("space_id") or target,
                                              params.get("edges") or params.get("edge"))
                elif opt == "cover_space":
                    ok, text = act_cover_space(plan, key, ans, params.get("space_id") or target)
                else:
                    ok, text = False, f"unknown option {opt!r}"
            except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
                ok, text = False, f"{opt} failed: {type(exc).__name__}: {exc}"
            rec.update(ok=bool(ok), change=text)
        out.append(rec)
    return out
