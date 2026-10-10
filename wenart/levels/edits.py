"""The agent's validated level edits (docs/milestone12.md §3.6, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026):

- ``LEVEL_EDIT_OPS``: ``("set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance", "set_terrain")``.
- ``LEVEL_EDIT_SCHEMAS``: op -> strict JSON schema of its arguments (``reason`` required; ``evidence`` where §3.6
  says so).
- ``apply_level_edit(building: dict, edit: dict) -> dict`` with the result of ``edit_ops.apply_edit``:
  ``{"accepted", "failed_checks", "score_before", "score_after", "building", "changed_ids", "rerun_from",
  "message"}``; the score is the number of critical + major L-findings (lower is better; an edit must not raise
  it); ``rerun_from`` is ``"build"``; pure.

What each edit does (on a copy; then ``model.infer_levels`` runs again and ``checks.check_levels`` judges it):

- ``set_mark_kind(mark_id, kind, reason)``: the mark's kind (``corrected_by_ai`` keeps the reason and the kind
  before); a ``floor`` mark takes the room it stands in; a section mark is never changed (geometry wins);
- ``set_room_floor(room_id, offset_m, evidence, reason)``: only from a mark (``evidence.mark_id``: its building z
  minus the level floor must equal ``offset_m`` within ``mark_tol``) or a drawn step line (``evidence.step_line``:
  the entity id or the plan crop it was read from), within ``room_offset_max``; ``floor_source: agent``;
- ``set_ground_point(x, y, z, evidence, reason)``: a ground point (an agent mark, method ``ai``, status
  ``unverified``); refused within 2 m of a drawn (vector) ground mark that says otherwise (a mark wins over the agent
  unless it is a clear error);
- ``set_entrance(door_id, solution, reason)``: ``none`` | ``steps`` | ``ramp`` | ``steps_and_ramp`` for an outside
  door of ``site.entrances`` (sized by the rules; ``adjusted_by_ai``);
- ``set_terrain(kind, reason)``: ``flat`` | ``sides`` | ``planar`` | ``tin`` from the ground marks
  (``site.ground.terrain_override``).

Every accepted edit is labelled (``corrected_by_ai`` / ``adjusted_by_ai`` / ``inferred``) and is listed in
``building["level_inference"]["edits"]``.
"""
from __future__ import annotations

import copy
from typing import Optional

from wenart import geometry as G

LEVEL_EDIT_OPS: tuple[str, ...] = ("set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance", "set_terrain")
META_KEYS = ("round", "log_seq", "model", "seq")
_REASON = {"type": "string", "minLength": 3, "maxLength": 600}
_EVIDENCE = {"type": "object", "additionalProperties": False, "minProperties": 1,
             "properties": {"mark_id": {"type": "string", "minLength": 1}, "step_line": {"type": "string", "minLength": 1},
                            "crop": {"type": "string"}, "note": {"type": "string", "maxLength": 400}}}
KINDS = ["floor", "slab_top", "ground_natural", "ground_finished", "plinth", "entrance", "threshold", "slope_top",
         "datum", "unknown"]
LEVEL_EDIT_SCHEMAS: dict[str, dict] = {
    "set_mark_kind": {"type": "object", "additionalProperties": False, "required": ["mark_id", "kind", "reason"],
                      "properties": {"mark_id": {"type": "string", "minLength": 1}, "kind": {"enum": KINDS},
                                     "reason": _REASON}},
    "set_room_floor": {"type": "object", "additionalProperties": False,
                       "required": ["room_id", "offset_m", "evidence", "reason"],
                       "properties": {"room_id": {"type": "string", "minLength": 1},
                                      "offset_m": {"type": "number", "minimum": -3.0, "maximum": 3.0},
                                      "evidence": _EVIDENCE, "reason": _REASON}},
    "set_ground_point": {"type": "object", "additionalProperties": False, "required": ["x", "y", "z", "evidence", "reason"],
                         "properties": {"x": {"type": "number"}, "y": {"type": "number"},
                                        "z": {"type": "number", "minimum": -50.0, "maximum": 50.0},
                                        "evidence": {"type": "string", "minLength": 3, "maxLength": 400},
                                        "reason": _REASON}},
    "set_entrance": {"type": "object", "additionalProperties": False, "required": ["door_id", "solution", "reason"],
                     "properties": {"door_id": {"type": "string", "minLength": 1},
                                    "solution": {"enum": ["none", "steps", "ramp", "steps_and_ramp"]},
                                    "reason": _REASON}},
    "set_terrain": {"type": "object", "additionalProperties": False, "required": ["kind", "reason"],
                    "properties": {"kind": {"enum": ["flat", "sides", "planar", "tin"]}, "reason": _REASON}},
}
SEVERE = ("critical", "major")
GROUND_MARK_GUARD_M = 2.0


class Rejected(Exception):
    pass


def _result(accepted: bool, failed: list, before: float, after: float, building, changed: list, message: str) -> dict:
    return {"accepted": accepted, "failed_checks": list(failed), "score_before": float(before),
            "score_after": float(after), "building": building, "changed_ids": list(changed), "rerun_from": "build",
            "message": message}


def normalise(edit: dict) -> tuple[Optional[str], dict, dict]:
    """``(op, arguments, meta)`` of an edit: ``{"op" | "tool": ..., "args": {...}}`` or flat."""
    edit = edit if isinstance(edit, dict) else {}
    op = edit.get("op") or edit.get("tool")
    raw = dict(edit["args"]) if isinstance(edit.get("args"), dict) else {k: v for k, v in edit.items()
                                                                         if k not in ("op", "tool")}
    meta = {k: raw.pop(k) for k in list(raw) if k in META_KEYS}
    meta.update({k: edit[k] for k in META_KEYS if k in edit and isinstance(edit.get("args"), dict)})
    return op, raw, meta


def schema_errors(op: str, args: dict) -> list[str]:
    import jsonschema

    v = jsonschema.Draft202012Validator(LEVEL_EDIT_SCHEMAS[op])
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<args>'}: {e.message}"
            for e in sorted(v.iter_errors(args), key=lambda e: list(e.absolute_path))]


def score(findings: list[dict]) -> int:
    """Critical + major L-findings (lower is better)."""
    return sum(1 for f in findings if f.get("severity") in SEVERE)


def _set_mark_kind(b: dict, a: dict, meta: dict) -> list[str]:
    m = next((x for x in b.get("level_marks") or [] if x.get("id") == a["mark_id"]), None)
    if m is None:
        raise Rejected(f"exists: no level mark {a['mark_id']!r}")
    if m.get("placement") == "section":
        raise Rejected("anchor: a section's level mark is geometry; its kind is not changed")
    if m.get("kind") == a["kind"]:
        raise Rejected(f"no_change: {a['mark_id']} is {a['kind']} already")
    before = m.get("kind")
    m["kind"] = a["kind"]
    m["corrected_by_ai"] = {"reason": a["reason"], "before": {"kind": before}, **meta}
    if a["kind"] in ("floor", "entrance") and m.get("point") is not None:
        room = next((r for r in b.get("rooms") or [] if r.get("level_id") == m.get("level_id")
                     and len(r.get("polygon") or []) >= 3 and G.point_in_polygon(tuple(m["point"]), r["polygon"])), None)
        m["room_id"] = room["id"] if room else None
    if a["kind"] not in ("floor", "entrance", "plinth", "slab_top"):
        m["room_id"] = None
    return [m["id"]]


def _set_room_floor(b: dict, a: dict, meta: dict, params: dict) -> list[str]:
    from wenart.levels import model as M

    room = next((r for r in b.get("rooms") or [] if r.get("id") == a["room_id"]), None)
    if room is None:
        raise Rejected(f"exists: no room {a['room_id']!r}")
    if abs(float(a["offset_m"])) > float(params["room_offset_max"]):
        raise Rejected(f"range: a room floor more than {float(params['room_offset_max']):.2f} m off its level floor")
    ev = a["evidence"]
    level = next((lv for lv in b.get("levels") or [] if lv["id"] == room["level_id"]), None)
    if ev.get("mark_id"):
        m = next((x for x in b.get("level_marks") or [] if x.get("id") == ev["mark_id"]), None)
        if m is None or m.get("z") is None:
            raise Rejected(f"evidence: no level mark {ev['mark_id']!r} with a level")
        want = float(m["z"]) - float((level or {}).get("elevation") or 0.0)
        if abs(want - float(a["offset_m"])) > float(params["mark_tol"]):
            raise Rejected(f"evidence: the mark {ev['mark_id']} gives {want:+.2f} m, not {float(a['offset_m']):+.2f} m")
        evidence = [dict(e) for e in m.get("evidence") or []][:2]
    elif ev.get("step_line"):
        evidence = [{"file": M._file_of(b), "method": "ai", "confidence": 0.5, "entity": ev["step_line"],
                     "text": ev.get("note") or a["reason"], "rule": "step_line"}]
    else:
        raise Rejected("evidence: a room floor needs a level mark or a drawn step line")
    room["floor_offset_m"] = round(float(a["offset_m"]), 3) + 0.0
    room["floor_source"] = "agent"
    room["floor_evidence"] = evidence
    room["floor_corrected_by_ai"] = {"reason": a["reason"], "evidence": dict(ev), **meta}
    return [room["id"]]


def _set_ground_point(b: dict, a: dict, meta: dict, params: dict) -> list[str]:
    p = (float(a["x"]), float(a["y"]))
    for m in b.get("level_marks") or []:
        if m.get("kind") in ("ground_natural", "ground_finished", "slope_top") and m.get("point") is not None \
                and m.get("z") is not None and any(e.get("method") == "vector" for e in m.get("evidence") or []) \
                and G.distance(p, m["point"]) <= GROUND_MARK_GUARD_M \
                and abs(float(m["z"]) - float(a["z"])) > float(params["mark_tol"]):
            raise Rejected(f"anchor: the drawn ground mark {m['id']} ({float(m['z']):+.2f} m) is "
                           f"{G.distance(p, m['point']):.1f} m away: the mark wins")
    marks = b.setdefault("level_marks", [])
    n = sum(1 for m in marks if str(m.get("id", "")).startswith("lm_ai_")) + 1
    mid = f"lm_ai_{n:03d}"
    from wenart.levels import model as M
    gl = M.ground_level(b)
    marks.append({"id": mid, "value": round(float(a["z"]), 4), "relative": True, "absolute": None,
                  "kind": "ground_finished", "point": [round(p[0], 4), round(p[1], 4)],
                  "level_id": gl["id"] if gl else None, "room_id": None, "side": None, "raw": f"agent {a['z']:+.2f}",
                  "used_for": [], "status": "unverified", "placement": "spot", "note": False,
                  "z": round(float(a["z"]), 4), "inferred": True,
                  "evidence": [{"file": M._file_of(b), "method": "ai", "confidence": 0.5, "text": a["evidence"],
                                "rule": "set_ground_point"}],
                  "adjusted_by_ai": {"reason": a["reason"], **meta}})
    return [mid]


def _set_entrance(b: dict, a: dict, meta: dict) -> list[str]:
    ents = [e for e in (b.get("site") or {}).get("entrances") or [] if isinstance(e, dict)]
    e = next((x for x in ents if x.get("door_id") == a["door_id"]), None)
    if e is None:
        raise Rejected(f"exists: {a['door_id']!r} is no outside door of site.entrances")
    if e.get("solution") == a["solution"] and not (e.get("adjusted_by_ai") or {}):
        raise Rejected(f"no_change: {a['door_id']} has {a['solution']} already")
    b["site"].setdefault("entrance_overrides", {})[a["door_id"]] = {"solution": a["solution"], "reason": a["reason"],
                                                                    **meta}
    return [a["door_id"]]


def _set_terrain(b: dict, a: dict, meta: dict) -> list[str]:
    site = b.get("site") if isinstance(b.get("site"), dict) else None
    if site is None:
        raise Rejected("exists: the building has no site")
    ground = site.setdefault("ground", {})
    pts = [p for p in ground.get("points") or [] if p.get("used", True)]
    if a["kind"] in ("planar", "tin") and len(pts) < 3:
        raise Rejected(f"evidence: a {a['kind']} terrain needs 3 or more ground points ({len(pts)})")
    if (ground.get("terrain_override") or {}).get("kind") == a["kind"]:
        raise Rejected(f"no_change: the terrain is {a['kind']} already")
    ground["terrain_override"] = {"kind": a["kind"], "reason": a["reason"], **meta}
    return ["site.ground"]


def apply_level_edit(building: dict, edit: dict) -> dict:
    """One level edit on a copy of ``building`` (module docstring); the input is never changed."""
    from wenart.levels import checks as C
    from wenart.levels import model as M

    op, args, meta = normalise(edit)
    if op not in LEVEL_EDIT_SCHEMAS:
        return _result(False, [f"op: unknown level edit {op!r} (one of {', '.join(LEVEL_EDIT_OPS)})"], 0, 0, None, [],
                       "unknown edit")
    errors = schema_errors(op, args)
    if errors:
        return _result(False, [f"schema: {e}" for e in errors], 0, 0, None, [], "the arguments do not match the "
                                                                                 "edit's schema")
    params = M.level_params(M._brief_of(building, None))
    before_findings = C.check_levels(building)
    before = score(before_findings)
    b = copy.deepcopy(building)
    try:
        if op == "set_mark_kind":
            changed = _set_mark_kind(b, args, meta)
        elif op == "set_room_floor":
            changed = _set_room_floor(b, args, meta, params)
        elif op == "set_ground_point":
            changed = _set_ground_point(b, args, meta, params)
        elif op == "set_entrance":
            changed = _set_entrance(b, args, meta)
        else:
            changed = _set_terrain(b, args, meta)
    except Rejected as exc:
        return _result(False, [str(exc)], before, before, None, [], f"{op} rejected")
    b = M.infer_levels(b)
    after_findings = C.check_levels(b)
    after = score(after_findings)
    if after > before:
        new = [f"{f['check']} {f['target']}: {f['message']}" for f in after_findings if f.get("severity") in SEVERE
               and not any(g["check"] == f["check"] and g["target"] == f["target"] for g in before_findings)]
        return _result(False, ["score: the level findings rise from "
                               f"{before} to {after}"] + new[:5], before, after, None, changed,
                       f"{op} makes the levels worse")
    b["level_inference"].setdefault("edits", []).append({"op": op, "args": args, **meta, "changed": changed})
    return _result(True, [], before, after, b, changed, f"{op} applied")
