"""The overrides file and its replay (docs/milestone11.md §2, contract §17.3).

What:

- ``Overrides``: ``outputs/<p>/orchestrator/overrides.json`` = ``{"project", "edits": [{"seq", "round", "tool",
  "args", "result", "model"}]}``, one entry per ACCEPTED edit in the order the agent made them (rejected edits are
  only in the log);
- ``apply(project_out)`` (``python -m wenart.agent apply <out_dir>``): reads ``building_decor.json``, replays the
  accepted furniture and room edits through ``wenart.furniture.edit_ops.apply_edit`` in ``seq`` order, copies the
  camera, exterior, material, geometry and re-run overrides into ``building["agent_overrides"]`` and writes
  ``building_agent.json``; ``refit`` reads that file when it exists in an orchestrated run (``wenart/run``).

Why: the agent never edits a building JSON or a ``.blend`` by hand; a re-run is deterministic because it always
starts from the decor stage's output and replays the same list. Applying twice gives the same file as applying
once, and the file's hash (a refit input) changes exactly when the accepted edits change.

How: an edit sent to ``apply_edit`` is ``{"op", <the tool's arguments>, "reason", "round", "log_seq", "model"}``
(contract §17.2); an edit that no longer validates on replay (e.g. the decor stage placed something new in the
way) is skipped and listed under ``not_replayed`` of the summary and of ``agent_overrides``, never forced.
Overrides of other tracks' data follow §17.3: cameras = a list of ``{action, view_id, ...}`` in edit order;
exterior = the edits' dicts merged in order (later keys win, nested dicts merged); materials = ``{slot:
look_id}``; ``geometry`` = the accepted ``correct_geometry`` records (record-only in M11, see ``geometry_fix``);
``reruns`` = the accepted ``rerun_stage`` settings (e.g. ``polish.enabled``).
"""
from __future__ import annotations

import copy
import hashlib
import json
import threading
from pathlib import Path
from typing import Callable, Optional

from wenart.agent import log as LG

OVERRIDES_JSON = "overrides.json"
DECOR_BUILDING = "building_decor.json"
AGENT_BUILDING = "building_agent.json"
# tool -> edit_ops op (§3.2; contract §17.2 EDIT_OPS). Milestone 12 (docs/milestone12.md §5.3, contract §13.2): the
# group-level ops of track G, named as their tools.
GROUP_OPS = ("place_group", "complete_group", "move_group", "retype_piece", "mark_not_furniture", "fix_fixture",
             "set_front")
FURNITURE_TOOLS = {"move_piece": "move", "rotate_piece": "rotate", "resize_piece": "resize",
                   "change_type": "change_type", "swap_model": "swap_model", "add_piece": "add",
                   "add_group": "add_group", "remove_piece": "remove", "relayout_room": "relayout_room",
                   "set_room_type": "set_room_type", **{op: op for op in GROUP_OPS}}
# Milestone 12 (§3.6, contract §13.2): the level edits of track L (``levels.edits.apply_level_edit``).
LEVEL_TOOLS = ("set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance", "set_terrain")
CAMERA_TOOLS = {"set_camera": "set", "add_camera": "add", "remove_camera": "remove"}
OTHER_TOOLS = ("set_material", "set_exterior", "set_lighting", "correct_geometry", "rerun_stage",
               "report_library_gap")
META_KEYS = ("reason",)          # tool arguments that are not override data
# While track G's new ops are not in ``edit_ops.EDIT_OPS`` (the M12 stubs), three of them have an M11 op that does the
# same: the edit is sent as that op (same arguments; the not-furniture kind and evidence go into the reason).
OP_FALLBACK = {"set_front": "rotate", "retype_piece": "change_type", "mark_not_furniture": "remove"}


def resolve_edit(edit: dict, ops) -> dict:
    """``edit`` for a validator that knows ``ops``: unchanged when its op is known (or has no fallback), else the
    M11 op of ``OP_FALLBACK`` with the same meaning (module docstring)."""
    op = edit.get("op")
    if op in ops or op not in OP_FALLBACK or OP_FALLBACK[op] not in ops:
        return edit
    out = {k: v for k, v in edit.items() if k not in ("kind", "evidence")}
    out["op"] = OP_FALLBACK[op]
    if op == "mark_not_furniture":
        out["reason"] = (f"not furniture ({edit.get('kind') or 'symbol'}): {edit.get('evidence') or ''}; "
                         f"{edit.get('reason') or ''}").strip()
    return out


def known_ops() -> tuple:
    try:
        from wenart.furniture import edit_ops
        return tuple(getattr(edit_ops, "EDIT_OPS", ()) or ())
    except ImportError:
        return ()


def sync_decor(building: dict) -> dict:
    """``decor.sync_to_hosts`` (track S, contract §13.2): the decor follows its hosts after every accepted edit."""
    from wenart.furniture import decor
    return decor.sync_to_hosts(building)


def source_sha(project_out, source: str = DECOR_BUILDING) -> str:
    """sha256 of the building the edits are made on (``building_decor.json``), "" without one. real03 (10 Oct
    2026): the overrides of an earlier run on another reading of the plan stayed on the volume; an edit is replayed
    only on the building it was made on."""
    path = Path(project_out) / source
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def overrides_path(project_out) -> Path:
    return LG.orchestrator_dir(project_out) / OVERRIDES_JSON


def merge_dict(base: dict, extra: dict) -> dict:
    """``extra`` merged into a copy of ``base``; nested dicts are merged, other values replaced."""
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_dict(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


class Overrides:
    """``orchestrator/overrides.json`` of one project output."""

    def __init__(self, project_out, project: str = ""):
        self.project_out = Path(project_out)
        self.path = overrides_path(project_out)
        self.project = project or self.project_out.name
        self.edits: list[dict] = []
        self.lock = threading.RLock()        # Milestone 12: parallel room sessions
        if self.path.is_file():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.project = data.get("project") or self.project
            self.edits = list(data.get("edits") or [])

    def next_seq(self) -> int:
        return (max(int(e["seq"]) for e in self.edits) + 1) if self.edits else 1

    def add(self, round_no: int, tool: str, args: dict, result: dict, model: str = "") -> int:
        """Store one accepted edit; its ``seq`` (the ``overrides_id`` the tool returns)."""
        keep = ("accepted", "failed_checks", "score_before", "score_after", "penalty_before", "penalty_after",
                "changed_ids", "rerun_from", "message",
                "applied", "log_seq", "metrics", "rolled_back")
        with self.lock:
            seq = self.next_seq()
            self.edits.append({"seq": seq, "round": int(round_no), "tool": tool, "args": copy.deepcopy(args),
                               "result": {k: copy.deepcopy(result.get(k)) for k in keep if k in result},
                               "model": model, "source_sha": source_sha(self.project_out)})
            self.save()
        return seq

    def save(self) -> Path:
        with self.lock:
            return LG.write_json_atomic(self.path, {"project": self.project, "edits": self.edits})

    def accepted(self) -> list[dict]:
        """The accepted edits made on the current ``building_decor.json`` (edits without a ``source_sha``, written
        before it was recorded, count as made on it)."""
        now = source_sha(self.project_out)
        return [e for e in sorted(self.edits, key=lambda e: int(e["seq"])) if (e.get("result") or {}).get("accepted")
                and (not e.get("source_sha") or not now or e["source_sha"] == now)]

    def stale(self) -> list[dict]:
        """Accepted edits made on another ``building_decor.json`` (an earlier reading of the plan): never replayed."""
        now = source_sha(self.project_out)
        return [e for e in self.edits if (e.get("result") or {}).get("accepted") and e.get("source_sha") and now
                and e["source_sha"] != now]

    def furniture_edits(self) -> list[dict]:
        """The building edits replayed in order: furniture and room edits (edit_ops) and level edits (track L)."""
        return [e for e in self.accepted() if e["tool"] in FURNITURE_TOOLS or e["tool"] in LEVEL_TOOLS]

    def agent_overrides(self) -> dict:
        """``building["agent_overrides"]`` (contract §17.3) from the accepted non-furniture edits."""
        cameras: list = []
        exterior: dict = {}
        materials: dict = {}
        geometry: list = []
        reruns: dict = {}
        lighting: dict = {}
        gaps: list = []
        rnd = 0
        for e in self.accepted():
            rnd = max(rnd, int(e.get("round") or 0))
            args = {k: v for k, v in (e.get("args") or {}).items() if k not in META_KEYS}
            reason = (e.get("args") or {}).get("reason")
            if e["tool"] in CAMERA_TOOLS:
                cameras.append(dict({"action": CAMERA_TOOLS[e["tool"]]}, **args, reason=reason, seq=e["seq"]))
            elif e["tool"] == "set_exterior":
                exterior = merge_dict(exterior, args)
            elif e["tool"] == "set_material":
                materials[str(args.get("slot"))] = args.get("look_id")
            elif e["tool"] == "set_lighting":
                lighting[str(args.get("room_id"))] = {"factor": float(args.get("factor")), "reason": reason,
                                                      "seq": e["seq"]}
            elif e["tool"] == "correct_geometry":
                geometry.append(dict(args, reason=reason, seq=e["seq"], applied=False,
                                     metrics=(e.get("result") or {}).get("metrics")))
            elif e["tool"] == "rerun_stage":
                reruns = merge_dict(reruns, {str(args.get("stage")): dict(args.get("settings") or {})})
            elif e["tool"] == "report_library_gap":
                gaps.append(dict(args, reason=reason, seq=e["seq"]))
        return {"cameras": cameras, "exterior": exterior, "materials": materials, "geometry": geometry,
                "reruns": reruns, "lighting": lighting, "library_gaps": gaps, "round": rnd}


def edit_of(entry: dict) -> dict:
    """The ``apply_edit`` (or ``apply_level_edit``) edit of one stored entry (contract §17.2, §13.2)."""
    args = dict(entry.get("args") or {})
    op = entry["tool"] if entry["tool"] in LEVEL_TOOLS else FURNITURE_TOOLS[entry["tool"]]
    edit = {"op": op, **args}
    edit.setdefault("reason", "")
    edit.update(round=int(entry.get("round") or 0), model=str(entry.get("model") or ""),
                log_seq=int((entry.get("result") or {}).get("log_seq") or entry["seq"]))
    return edit


def _default_apply_edit():
    from wenart.furniture import edit_ops
    return edit_ops.apply_edit


def _catalog():
    from wenart.furniture import catalog as CAT
    return CAT.load()


def _default_level_edit():
    from wenart.levels import edits
    return edits.apply_level_edit


def apply(project_out, *, apply_edit: Optional[Callable] = None, catalog_loader: Optional[Callable] = None,
          source: str = DECOR_BUILDING, out_name: str = AGENT_BUILDING, level_edit: Optional[Callable] = None,
          sync: Optional[Callable] = None) -> dict:
    """Replay the accepted edits on ``building_decor.json`` and write ``building_agent.json`` (module docstring).
    The summary: ``{"out", "edits", "replayed", "not_replayed"}``; FileNotFoundError without the source.
    Milestone 12: level edits replay through ``levels.edits.apply_level_edit``; after every replayed edit the decor
    follows its hosts (``decor.sync_to_hosts``, B3); an op that track G has not built yet replays as its M11
    fallback (``resolve_edit``)."""
    project_out = Path(project_out)
    src = project_out / source
    building = json.loads(src.read_text(encoding="utf-8"))
    ov = Overrides(project_out)
    furniture = ov.furniture_edits()
    fn = apply_edit or (_default_apply_edit() if any(e["tool"] in FURNITURE_TOOLS for e in furniture) else None)
    level_fn = level_edit or (_default_level_edit() if any(e["tool"] in LEVEL_TOOLS for e in furniture) else None)
    sync_fn = sync or sync_decor
    ops = known_ops() if apply_edit is None else tuple(FURNITURE_TOOLS.values())
    catalog = None
    replayed: list[int] = []
    not_replayed: list[dict] = []
    for entry in furniture:
        edit = edit_of(entry)
        try:
            if entry["tool"] in LEVEL_TOOLS:
                res = level_fn(building, edit)
            else:
                edit = resolve_edit(edit, ops)
                if edit["op"] == "swap_model" and catalog is None:
                    catalog = (catalog_loader or _catalog)()
                res = fn(building, edit, catalog=catalog)
        except NotImplementedError as exc:
            not_replayed.append({"seq": entry["seq"], "failed_checks": ["validator_unavailable"], "message": str(exc)})
            continue
        if res.get("accepted") and isinstance(res.get("building"), dict):
            building = sync_fn(res["building"])
            replayed.append(int(entry["seq"]))
        else:
            not_replayed.append({"seq": entry["seq"], "failed_checks": list(res.get("failed_checks") or []),
                                 "message": res.get("message")})
    for entry in ov.stale():
        not_replayed.append({"seq": entry["seq"], "failed_checks": ["stale_source"],
                             "message": "made on another building_decor.json (an earlier run): not replayed"})
    overrides = ov.agent_overrides()
    overrides["not_replayed"] = not_replayed
    building["agent_overrides"] = overrides
    out = project_out / out_name
    LG.write_json_atomic(out, building)
    return {"out": str(out), "edits": len(ov.accepted()), "replayed": replayed, "not_replayed": not_replayed}
