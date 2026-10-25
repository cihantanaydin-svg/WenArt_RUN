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
}


CONTEXT_PARAMS = ("room_id", "window_id", "door_id", "piece_id")     # name the element, not the choice


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
    """Every answer for this building, normalised; a later source wins: the AI's (``agent_overrides.architect``),
    the building's ``architect_answers``, the user's (``brief_answers``: the project file through the brief)."""
    out: dict = {}
    sources = (((building.get("agent_overrides") or {}).get("architect") or {}),
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
    for key in sorted(answers):
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
                else:
                    ok, text = False, f"unknown option {opt!r}"
            except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
                ok, text = False, f"{opt} failed: {type(exc).__name__}: {exc}"
            rec.update(ok=bool(ok), change=text)
        out.append(rec)
    return out
