"""The agent's memory across rounds (docs/milestone12.md §5.4 D19 "Memory across rounds", §1.4 "Planning and memory").

What: ``Memory(project_out)`` is the per-room ledger ``outputs/<p>/orchestrator/memory.json``:

    {"version": 2, "rooms": {room_id: {"visits": [{"round", "scope"}], "accepted": [entry], "rejected": [entry],
                                       "candidates_tried": [{"candidate", "scope"}], "open": {"items", "scope"},
                                       "plans": [plan record]}},
     "refused": {"scope", "n"}, "refused_repeats": n}

with ``entry = {"round", "tool", "args", "key", "reasons", "scope"}`` (``reasons``: the failed checks of a rejected
edit; ``scope``: fix round after P5, below; version 1 files hold plain rounds, candidates and open lists).

- ``edit_key(tool, args)``: the canonical text of an edit (the tool and its arguments without ``reason``, numbers
  rounded to 3 decimals, keys sorted): two edits with the same key are the same edit;
- ``repeat_of(room, tool, args, round_no)``: the earlier rejection of the same edit (any round) or None; the tools
  refuse such an edit before any validator or model call (real02 G2d: 108 of 177 rejections were exact repeats);
- ``record(room, round, tool, args, result)``: one validated edit (accepted or rejected; dry runs are not recorded);
- ``visit``, ``set_open``, ``add_plan``, ``tried``: the coverage, the open checklist of the next round, the plans
  (fix round after P4a: each plan with its status and the planner's skip list).

Fix round after P4b (17 Oct 2026; pod P4b, real03): ``no_spot(room)`` names the pieces whose ``fix_fixture``
without ``center`` and ``size`` (the code's own search within 0.5 m) was rejected "no valid spot", with the round and
the reason: the tools refuse a later ``fix_fixture`` on such a piece without a new size, and the room brief lists
its wall and outline cuts as "not yours" (for review). Why: P4b's bathtubs f_L0_184-187 got 21 guessed centres in
5 cm steps and 13 max_tries after the code had searched every spot.

Why: M11 started a fresh conversation per room and a fresh tool context per round, so every rejection was forgotten
(§1.4). The ledger is the loop's, not the model's: the room brief shows it to the model, the tools enforce it.

Fix round after P5 (22 Oct 2026; pod P5, real04): the ledger is scoped to the building and the code it was made on.
The scope (``make_scope``) is ``{"sha", "code"}``: the sha256 of ``building_decor.json`` (``overrides.source_sha``,
the scope the overrides already use; "" without one) and ``code_version()`` (the sha256 of the files whose rules
accept or refuse an edit, ``CODE_FILES``). Every record written carries it (``"scope"``): an accepted or rejected
entry, a visit (``{"round", "scope"}``), a tried candidate (``{"candidate", "scope"}``), the open checklist
(``{"items", "scope"}`` under the same ``open`` key), a plan, and the refusal counter (``refused``: ``{"scope",
"n"}``; the file's ``refused_repeats`` is the current scope's). Every reading (``room``, ``visits``, ``repeat_of``,
``no_spot``, ``summary``, ``refused_repeats``) uses only the records whose ``scope`` equals the current one (``==``:
an empty sha of a test without ``building_decor.json`` matches itself); a record without a scope (M12, P3, P5) is an
earlier run and is ignored; nothing is deleted from the file (the open checklist is replaced by the next one, as
before; a version-1 file's refusal count is kept as ``refused_repeats_legacy``). The views keep their old shapes
(rounds and candidates as ints, the open checklist as strings, records without the ``scope`` key). The loop re-reads
the sha once per round (``refresh``). An acceptance rejection that only says the round's finding list had no target
for the edit (``BOOKKEEPING_WORDS``: "no target finding", "target finding ... is not among") refuses its repeat in the
same round only: a later round has other findings (26 Oct 2026, Argus P10: and only while the round's list still has
no target for it, ``repeat_of(skip_bookkeeping=True)`` from ``tools._repeat_of``: the repeat whose reason names its
finding is validated again). Why: P5's memory.json held three runs (r_L-1_salon visits [1..6, 1,
2, 3, 1, 2, 3]); 19 of P5's 33 memory refusals cited rejections that do not exist in P5's log (M12's "round 6", P3's
remove_piece f_L1_048, M12's set_terrain), the planner skipped a relayout "tried" in M12, sessions were ordered by the
visits of all runs, and piece ids change meaning between runs (P3's floor lamp f_L-1_065 is P5's coffee table).

How: plain JSON, written atomically after every change (a pod cut by its deadline keeps it); a lock makes it safe for
the parallel room sessions of one round. Deterministic: the same edits in the same order give the same file.
"""
from __future__ import annotations

import copy
import functools
import hashlib
import json
import threading
from pathlib import Path
from typing import Optional

from wenart.agent import log as LG

MEMORY_JSON = "memory.json"
VERSION = 2                     # fix round after P5: scoped records (version 1: no scope)
META = ("reason",)              # arguments that do not change what an edit does
NO_SPOT_WORDS = "no valid spot"  # fix round after P4b: edit_ops._fix_fixture's "no valid spot within 0.50 m"
# Fix round after P5 (module docstring): the code whose rules accept or refuse an edit (relative to the repository);
# an earlier rejection made by other rules is not repeated, it is validated again.
CODE_FILES = ("wenart/agent", "wenart/furniture/edit_ops.py", "wenart/levels/edits.py",
              "wenart/blender/exterior_checks.py")
# Fix round after P5: an acceptance rejection about the round's finding list, not about the edit
# (``causes.accept_edit``: "no target finding: ...", "target finding X is not among the findings before the edit");
# refused in its round only.
BOOKKEEPING_WORDS = ("acceptance: no target finding", "is not among the findings before the edit")


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


@functools.lru_cache(maxsize=1)
def code_version() -> str:
    """Fix round after P5: the sha256 (16 hex) of ``CODE_FILES`` (their ``.py`` files in path order, path and bytes);
    "" when none is found (an installed package without the sources)."""
    root = Path(__file__).resolve().parents[2]
    h = hashlib.sha256()
    found = False
    for rel in CODE_FILES:
        path = root / rel
        files = sorted(path.rglob("*.py")) if path.is_dir() else [path] if path.is_file() else []
        for f in files:
            found = True
            h.update(str(f.relative_to(root)).encode("utf-8"))
            h.update(f.read_bytes())
    return h.hexdigest()[:16] if found else ""


def make_scope(project_out) -> dict:
    """Fix round after P5: ``{"sha", "code"}`` of a project output (module docstring)."""
    from wenart.agent import overrides as OV
    return {"sha": OV.source_sha(project_out), "code": code_version()}


def bookkeeping(entry: dict) -> bool:
    """Fix round after P5: a rejection whose reasons only say the round had no target finding for it."""
    return any(any(w in str(r) for w in BOOKKEEPING_WORDS) for r in entry.get("reasons") or [])


def _plain(record: dict) -> dict:
    return {k: v for k, v in record.items() if k != "scope"}


class Memory:
    """``orchestrator/memory.json`` of one project output (module docstring)."""

    def __init__(self, project_out):
        self.project_out = Path(project_out)
        self.path = memory_path(project_out)
        self.lock = threading.RLock()
        self.data: dict = {"version": VERSION, "rooms": {}, "refused_repeats": 0}
        if self.path.is_file():
            try:
                old = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(old, dict) and isinstance(old.get("rooms"), dict):
                    self.data = {"version": VERSION, "rooms": old["rooms"],
                                 "refused_repeats": int(old.get("refused_repeats") or 0)}
                    if isinstance(old.get("refused"), dict):
                        self.data["refused"] = old["refused"]
                    legacy = old.get("refused_repeats_legacy")
                    if legacy is None and not isinstance(old.get("refused"), dict) and old.get("refused_repeats"):
                        legacy = old["refused_repeats"]       # fix round after P5: a version-1 file's count, kept
                    if legacy is not None:
                        self.data["refused_repeats_legacy"] = int(legacy)
            except (OSError, ValueError):
                pass
        self.scope: dict = make_scope(self.project_out)
        self._sync_refused()

    def refresh(self) -> dict:
        """Fix round after P5: re-read the scope (the loop calls it once per round: a re-run of the decor stage on
        other inputs makes another building, and the overrides of the old one are not replayed either)."""
        with self.lock:
            self.scope = make_scope(self.project_out)
            self._sync_refused()
            return dict(self.scope)

    def _sync_refused(self) -> None:
        rec = self.data.get("refused") if isinstance(self.data.get("refused"), dict) else None
        n = int(rec.get("n") or 0) if rec is not None and rec.get("scope") == self.scope else 0
        self.data["refused"] = {"scope": dict(self.scope), "n": n}
        self.data["refused_repeats"] = n

    def mine(self, record) -> bool:
        """Fix round after P5: a record of the current scope (module docstring)."""
        return isinstance(record, dict) and record.get("scope") == self.scope

    # ----- reading -----------------------------------------------------------------------------

    def _raw(self, room_id) -> dict:
        return self.data["rooms"].get(str(room_id)) or {}

    def room(self, room_id: Optional[str]) -> dict:
        """The room's records of the current scope in the old shapes (module docstring)."""
        with self.lock:
            r = self._raw(room_id)
            opened = r.get("open")
            return {"visits": [int(v.get("round") or 0) for v in r.get("visits") or [] if self.mine(v)],
                    "accepted": [_plain(copy.deepcopy(e)) for e in r.get("accepted") or [] if self.mine(e)],
                    "rejected": [_plain(copy.deepcopy(e)) for e in r.get("rejected") or [] if self.mine(e)],
                    "candidates_tried": [int(c.get("candidate")) for c in r.get("candidates_tried") or []
                                         if self.mine(c) and c.get("candidate") is not None],
                    "open": list(opened.get("items") or []) if self.mine(opened) else [],
                    "plans": [_plain(copy.deepcopy(p)) for p in r.get("plans") or [] if self.mine(p)]}

    def visits(self, room_id: Optional[str]) -> int:
        with self.lock:
            return sum(1 for v in self._raw(room_id).get("visits") or [] if self.mine(v))

    def repeat_of(self, room_id: Optional[str], tool: str, args: Optional[dict],
                  round_no: Optional[int] = None, skip_bookkeeping: bool = False) -> Optional[dict]:
        """The earlier rejection of exactly this edit in ``room_id`` (any round of the current scope), else None.
        Fix round after P5: a ``bookkeeping`` rejection counts only in its own round (``round_no``; None: any).
        26 Oct 2026 (Argus P10): ``skip_bookkeeping`` leaves every ``bookkeeping`` rejection out (the tools pass it
        when the round's finding list now holds a target for the edit, ``tools._repeat_of``)."""
        key = edit_key(tool, args)
        with self.lock:
            for e in self._raw(room_id).get("rejected") or []:
                if e.get("key") != key or not self.mine(e):
                    continue
                if bookkeeping(e) and (skip_bookkeeping or (round_no is not None
                                                            and int(e.get("round") or 0) != int(round_no))):
                    continue
                return _plain(copy.deepcopy(e))
        return None

    def no_spot(self, room_id: Optional[str]) -> dict:
        """Fix round after P4b (module docstring): ``{piece_id: {"round", "reason"}}`` of the room's rejected
        ``fix_fixture`` edits without ``center`` and ``size`` whose reasons say "no valid spot" (the first one).
        Fix round after P5: of the current scope."""
        out: dict = {}
        with self.lock:
            for e in self._raw(room_id).get("rejected") or []:
                args = e.get("args") or {}
                if e.get("tool") != "fix_fixture" or args.get("center") is not None or args.get("size") is not None \
                        or not self.mine(e):
                    continue
                why = next((str(r) for r in e.get("reasons") or [] if NO_SPOT_WORDS in str(r)), None)
                pid = args.get("piece_id")
                if why and pid and str(pid) not in out:
                    out[str(pid)] = {"round": e.get("round"), "reason": why}
        return out

    @property
    def refused_repeats(self) -> int:
        """The memory refusals of the current scope (fix round after P5)."""
        with self.lock:
            rec = self.data.get("refused") if isinstance(self.data.get("refused"), dict) else {}
            return int(rec.get("n") or 0) if rec.get("scope") == self.scope else 0

    # ----- writing ------------------------------------------------------------------------------

    def _room(self, room_id) -> dict:
        room = self.data["rooms"].setdefault(str(room_id), _empty_room())
        for key, empty in _empty_room().items():
            room.setdefault(key, empty)
        return room

    def visit(self, room_id: str, round_no: int) -> None:
        with self.lock:
            self._room(room_id)["visits"].append({"round": int(round_no), "scope": dict(self.scope)})
            self.save()

    def record(self, room_id: Optional[str], round_no: int, tool: str, args: Optional[dict], result: dict) -> None:
        """One validated edit (``result`` of a tool: ``accepted``, ``failed_checks``)."""
        if room_id is None:
            room_id = "building"
        entry = {"round": int(round_no), "tool": tool, "args": copy.deepcopy(dict(args or {})),
                 "key": edit_key(tool, args), "reasons": [str(f) for f in result.get("failed_checks") or []][:6],
                 "scope": dict(self.scope)}
        with self.lock:
            self._room(room_id)["accepted" if result.get("accepted") else "rejected"].append(entry)
            self.save()

    def refused(self) -> None:
        with self.lock:
            n = self.refused_repeats + 1
            self.data["refused"] = {"scope": dict(self.scope), "n": n}
            self.data["refused_repeats"] = n
            self.save()

    def tried(self, room_id: str, candidate: int) -> None:
        with self.lock:
            tried = self._room(room_id)["candidates_tried"]
            if not any(self.mine(c) and c.get("candidate") == int(candidate) for c in tried):
                tried.append({"candidate": int(candidate), "scope": dict(self.scope)})
            self.save()

    def set_open(self, room_id: str, items: list) -> None:
        with self.lock:
            self._room(room_id)["open"] = {"items": [str(i) for i in items][:20], "scope": dict(self.scope)}
            self.save()

    def add_plan(self, room_id: str, round_no: int, plan: Optional[dict], ok: bool, problems: list,
                 status: Optional[str] = None) -> None:
        """One plan of a session. Fix round after P4a: with the loop's ``status`` (ok / empty / refused / default;
        without one: ok or default) and the planner's ``skip`` list (``finding_id``, ``why``)."""
        plan = plan if isinstance(plan, dict) else None
        skip = [{"finding_id": str(s.get("finding_id")), "why": str(s.get("why") or "")[:300]}
                for s in ((plan or {}).get("skip") or []) if isinstance(s, dict)][:20]
        with self.lock:
            self._room(room_id)["plans"].append({"round": int(round_no), "ok": bool(ok),
                                                 "status": str(status or ("ok" if ok else "default")),
                                                 "problems": [str(p) for p in problems][:10],
                                                 "steps": len((plan or {}).get("steps") or []), "skip": skip,
                                                 "scope": dict(self.scope)})
            self.save()

    def save(self) -> Path:
        with self.lock:
            self.data["version"] = VERSION
            return LG.write_json_atomic(self.path, self.data)

    # ----- the brief's view -----------------------------------------------------------------------

    def summary(self, room_id: str, last: int = 8) -> dict:
        """What the room brief shows: visits, the last accepted and rejected edits (tool, args, reasons), the
        candidates tried and the open checklist (fix round after P5: of the current scope)."""
        r = self.room(room_id)

        def short(e):
            return {"round": e.get("round"), "tool": e.get("tool"),
                    "args": {k: v for k, v in (e.get("args") or {}).items() if k not in META},
                    **({"why_rejected": e.get("reasons")} if e.get("reasons") else {})}

        return {"visits": len(r["visits"]), "accepted": [short(e) for e in r["accepted"][-last:]],
                "rejected": [short(e) for e in r["rejected"][-last:]], "candidates_tried": r["candidates_tried"],
                "open": r["open"]}
