"""The agent's memory across rounds (docs/milestone12.md §5.4 D19 "Memory across rounds", §1.4 "Planning and memory").

What: ``Memory(project_out)`` is the per-room ledger ``outputs/<p>/orchestrator/memory.json``:

    {"version": 1, "rooms": {room_id: {"visits": [round, ...], "accepted": [entry], "rejected": [entry],
                                       "candidates_tried": [k, ...], "open": [str], "plans": [plan record]}},
     "refused_repeats": n}

with ``entry = {"round", "tool", "args", "key", "reasons"}`` (``reasons``: the failed checks of a rejected edit).

- ``edit_key(tool, args)``: the canonical text of an edit (the tool and its arguments without ``reason``, numbers
  rounded to 3 decimals, keys sorted): two edits with the same key are the same edit;
- ``repeat_of(room, tool, args)``: the earlier rejection of the same edit (any round) or None; the tools refuse such
  an edit before any validator or model call (real02 G2d: 108 of 177 rejections were exact repeats);
- ``record(room, round, tool, args, result)``: one validated edit (accepted or rejected; dry runs are not recorded);
- ``visit``, ``set_open``, ``add_plan``, ``tried``: the coverage, the open checklist of the next round, the plans.

Why: M11 started a fresh conversation per room and a fresh tool context per round, so every rejection was forgotten
(§1.4). The ledger is the loop's, not the model's: the room brief shows it to the model, the tools enforce it.

How: plain JSON, written atomically after every change (a pod cut by its deadline keeps it); a lock makes it safe for
the parallel room sessions of one round. Deterministic: the same edits in the same order give the same file.
"""
from __future__ import annotations

import copy
import json
import threading
from pathlib import Path
from typing import Optional

from wenart.agent import log as LG

MEMORY_JSON = "memory.json"
VERSION = 1
META = ("reason",)              # arguments that do not change what an edit does


def memory_path(project_out) -> Path:
    return LG.orchestrator_dir(project_out) / MEMORY_JSON


def _canon(value):
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return round(float(value), 3)
    if isinstance(value, dict):
        return {str(k): _canon(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_canon(v) for v in value]
    return str(value)


def edit_key(tool: str, args: Optional[dict]) -> str:
    """The canonical text of an edit: ``tool`` + its arguments without ``reason`` (numbers to 3 decimals)."""
    body = {k: v for k, v in (args or {}).items() if k not in META}
    return json.dumps({"tool": tool, "args": _canon(body)}, sort_keys=True, ensure_ascii=False)


def _empty_room() -> dict:
    return {"visits": [], "accepted": [], "rejected": [], "candidates_tried": [], "open": [], "plans": []}


class Memory:
    """``orchestrator/memory.json`` of one project output (module docstring)."""

    def __init__(self, project_out):
        self.path = memory_path(project_out)
        self.lock = threading.RLock()
        self.data: dict = {"version": VERSION, "rooms": {}, "refused_repeats": 0}
        if self.path.is_file():
            try:
                old = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(old, dict) and isinstance(old.get("rooms"), dict):
                    self.data = {"version": VERSION, "rooms": old["rooms"],
                                 "refused_repeats": int(old.get("refused_repeats") or 0)}
            except (OSError, ValueError):
                pass

    # ----- reading -----------------------------------------------------------------------------

    def room(self, room_id: Optional[str]) -> dict:
        with self.lock:
            return copy.deepcopy(self.data["rooms"].get(str(room_id), _empty_room()))

    def visits(self, room_id: Optional[str]) -> int:
        with self.lock:
            return len((self.data["rooms"].get(str(room_id)) or {}).get("visits") or [])

    def repeat_of(self, room_id: Optional[str], tool: str, args: Optional[dict]) -> Optional[dict]:
        """The earlier rejection of exactly this edit in ``room_id`` (any round), else None."""
        key = edit_key(tool, args)
        with self.lock:
            for e in (self.data["rooms"].get(str(room_id)) or {}).get("rejected") or []:
                if e.get("key") == key:
                    return copy.deepcopy(e)
        return None

    @property
    def refused_repeats(self) -> int:
        return int(self.data.get("refused_repeats") or 0)

    # ----- writing ------------------------------------------------------------------------------

    def _room(self, room_id) -> dict:
        return self.data["rooms"].setdefault(str(room_id), _empty_room())

    def visit(self, room_id: str, round_no: int) -> None:
        with self.lock:
            self._room(room_id)["visits"].append(int(round_no))
            self.save()

    def record(self, room_id: Optional[str], round_no: int, tool: str, args: Optional[dict], result: dict) -> None:
        """One validated edit (``result`` of a tool: ``accepted``, ``failed_checks``)."""
        if room_id is None:
            room_id = "building"
        entry = {"round": int(round_no), "tool": tool, "args": copy.deepcopy(dict(args or {})),
                 "key": edit_key(tool, args), "reasons": [str(f) for f in result.get("failed_checks") or []][:6]}
        with self.lock:
            self._room(room_id)["accepted" if result.get("accepted") else "rejected"].append(entry)
            self.save()

    def refused(self) -> None:
        with self.lock:
            self.data["refused_repeats"] = self.refused_repeats + 1
            self.save()

    def tried(self, room_id: str, candidate: int) -> None:
        with self.lock:
            tried = self._room(room_id)["candidates_tried"]
            if int(candidate) not in tried:
                tried.append(int(candidate))
            self.save()

    def set_open(self, room_id: str, items: list) -> None:
        with self.lock:
            self._room(room_id)["open"] = [str(i) for i in items][:20]
            self.save()

    def add_plan(self, room_id: str, round_no: int, plan: Optional[dict], ok: bool, problems: list) -> None:
        with self.lock:
            self._room(room_id)["plans"].append({"round": int(round_no), "ok": bool(ok),
                                                 "problems": [str(p) for p in problems][:10],
                                                 "steps": len((plan or {}).get("steps") or [])})
            self.save()

    def save(self) -> Path:
        with self.lock:
            return LG.write_json_atomic(self.path, self.data)

    # ----- the brief's view -----------------------------------------------------------------------

    def summary(self, room_id: str, last: int = 8) -> dict:
        """What the room brief shows: visits, the last accepted and rejected edits (tool, args, reasons), the
        candidates tried and the open checklist."""
        r = self.room(room_id)

        def short(e):
            return {"round": e.get("round"), "tool": e.get("tool"),
                    "args": {k: v for k, v in (e.get("args") or {}).items() if k not in META},
                    **({"why_rejected": e.get("reasons")} if e.get("reasons") else {})}

        return {"visits": len(r["visits"]), "accepted": [short(e) for e in r["accepted"][-last:]],
                "rejected": [short(e) for e in r["rejected"][-last:]], "candidates_tried": r["candidates_tried"],
                "open": r["open"]}
