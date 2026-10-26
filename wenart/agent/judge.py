"""The AI judge and the house score of the big loop (26 Oct 2026, user: "results are not getting better enough, need a
big loop that fixes itself for the better").

What:

- ``judge_view(model, building, view, image)``: one final render goes to the vision model as to a client's interior
  designer: a score ``client_ready_score`` 1-5 (1 embarrassing, 5 could be shown to the client), the tags of the
  Milestone 13 rubric (``TAGS``, docs/milestone13.md §1.1, with ``mismatched_set``, ``not_stylish`` and
  ``makes_no_sense`` added), a one-line note and the problems that cost the points, each on an element id of what the
  image shows (the room, its built pieces, its doors and windows; on an exterior view the outer walls and openings)
  and a check of the agent's checklist (``PROBLEM_CHECKS``), so ``causes.cause_of`` routes it to a tool or to the
  stage that owns it. A problem on an id the image does not show is dropped with the reason.
- ``house_score(...)``: one number for the state of the house, higher is better: ``RUBRIC_WEIGHT`` of the rubric
  part (the mean score 1-5 as 0-100) and the rest the defects part (``CRITICAL_POINTS`` per critical and
  ``MAJOR_POINTS`` per major finding of the code critic and of the review of the 3D model and per open major point of
  the architect, per view, as ``100 / (1 + points / DEFECT_SCALE)``: every finding counts, it never saturates). The big loop (``scheduler.improvement_loop``) keeps a cycle's edits only when the
  score does not fall by more than ``WORSE_MARGIN``, and goes on while it rises by ``MIN_GAIN``.
- ``write(project_out, rows, rec)``: ``final/rubric_per_view.json`` (the rubric file ``wenart.report.metrics13``'s
  metric 15 reads) and ``orchestrator/big_loop.json`` / ``big_loop.md`` (each cycle's score and parts).

Why: the loop's measure was "findings removed", which never saw that the living room's armchairs do not belong
together or that a room is plain: a vision model judging the whole picture as a client would, and one score over
every check, let the loop see whether the house got better and keep only what made it better.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Optional

from wenart.agent import log as LG
from wenart.agent import prompts as P

TAGS = ("missing_anchor", "empty_room", "parametric_boxy", "grey_box", "floating_or_odd_placement", "overlap_cut",
        "blocked_door_window", "bare_material", "wrong_scale", "lollipop_vegetation", "flat_outdoor", "bad_camera",
        "lighting_bad", "decor_wrong", "mismatched_set", "not_stylish", "makes_no_sense", "looks_acceptable")
PROBLEM_CHECKS = tuple(P.VISITOR_CHECKS) + ("D1", "D2", "D3", "F9", "V1", "V2")
SEVERITIES = ("critical", "major", "minor")
MAX_PROBLEMS = 6
RUBRIC_WEIGHT = 0.6             # the share of the rubric part in the house score
CRITICAL_POINTS = 10.0          # defects part: points per critical finding per view ...
MAJOR_POINTS = 3.0              # ... and per major one
DEFECT_SCALE = 5.0              # defects part = 100 / (1 + points per view / this): never saturates
WORSE_MARGIN = 2.0              # a cycle whose score falls more than this is rolled back
MIN_GAIN = 0.5                  # the loop goes on while a cycle raises the score at least this much
RUBRIC_FILE = "final/rubric_per_view.json"
LOOP_JSON = "big_loop.json"
LOOP_MD = "big_loop.md"

SYSTEM = ("You are the interior designer and architect who will show this house to the client tomorrow. You judge one "
          "render the way the client will see it: does it make sense, and does it look like a stylish, "
          "well-designed home in the project's style? Be strict and concrete: name the element (by its id) that "
          "costs points and say what is wrong with it.")

SCORES_TEXT = ("client_ready_score: 5 = could be shown to the client as it is (stylish, coherent, believable); 4 = "
               "good, one or two small flaws; 3 = acceptable but plain or with one clear flaw; 2 = several clear "
               "problems a client would point at; 1 = embarrassing (an empty or absurd room, a broken model).")
TAGS_TEXT = ("Tags (all that apply): missing_anchor (a room without its main piece: a living room without a sofa, a "
             "bedroom without a bed, a kitchen without its run), empty_room, parametric_boxy (blocky placeholder "
             "furniture), grey_box, floating_or_odd_placement, overlap_cut (pieces through each other or a wall), "
             "blocked_door_window, bare_material (flat untextured surfaces), wrong_scale, lollipop_vegetation, "
             "flat_outdoor, bad_camera (a wall, a corner or a door fills the frame), lighting_bad, decor_wrong, "
             "mismatched_set (pieces of one group that do not go together: chairs of different models, armchairs of "
             "other styles and colours), not_stylish (plain, dated or cheap-looking for the project's style), "
             "makes_no_sense (a door, step, railing, fixture or piece that has no reason to be there), "
             "looks_acceptable.")


def schema(targets: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False,
            "required": ["client_ready_score", "tags", "note", "problems"],
            "properties": {
                "client_ready_score": {"type": "integer", "minimum": 1, "maximum": 5},
                "tags": {"type": "array", "items": {"type": "string", "enum": list(TAGS)}},
                "note": {"type": "string", "minLength": 3},
                "problems": {"type": "array", "maxItems": MAX_PROBLEMS, "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["check", "severity", "target", "message"],
                    "properties": {"check": {"type": "string", "enum": list(PROBLEM_CHECKS)},
                                   "severity": {"type": "string", "enum": list(SEVERITIES)},
                                   "target": {"type": "string", "enum": sorted(targets) or ["building"]},
                                   "message": {"type": "string", "minLength": 3}}}}}}


def view_facts(building: dict, view: dict) -> tuple[str, set]:
    """(the facts of what a view shows, as lines; the ids its problems may target)."""
    from wenart.agent import critic_vision as CV

    name, room_id = view.get("name"), view.get("room_id")
    if room_id:
        allowed = CV.room_ids(building, room_id, [name])
        room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), {})
        pieces = [f"{f.get('id')} {f.get('type')}" for f in building.get("furniture") or []
                  if f.get("id") in allowed]
        openings = [f"{o.get('id')} {o.get('type')}" for o in building.get("openings") or [] if o.get("id") in allowed]
        lines = [f"Room {room_id} ({room.get('label') or room.get('name') or ''}), a {room.get('room_type')} of "
                 f"{float(room.get('area_computed') or room.get('area') or 0):.1f} m2.",
                 "Pieces: " + (", ".join(pieces[:30]) or "none"), "Doors and windows: " + (", ".join(openings[:20]) or "none")]
    else:
        allowed = CV.exterior_ids(building, name)
        lines = [f"Exterior view {name} of the house (target the building, an outer wall or an opening by its id).",
                 "Doors and windows of the facades: " + ", ".join(sorted(i for i in allowed
                                                                          if i not in (name, "building")))[:1500]]
    return "\n".join(lines), allowed


def judge_view(model, building: dict, view: dict, image: Path, *, style: str = "", call_id: str = "") -> dict:
    """One view (module docstring): ``{"row": rubric row, "findings": [...], "dropped": [...], "error"}``."""
    from wenart.agent.model import user_message

    facts, allowed = view_facts(building, view)
    text = "\n".join([f"Image 1 is the final render {view.get('name')}." + (f" The project's style: {style}." if style
                                                                             else ""),
                      facts, "", SCORES_TEXT, TAGS_TEXT,
                      "Problems: the ones that cost points, most important first, at most "
                      f"{MAX_PROBLEMS}; each names one id from the lists above as target and one check:",
                      P.checklist_text(PROBLEM_CHECKS)])
    reply = model.critic([{"role": "system", "content": SYSTEM}, user_message(text, [image], [None])],
                         schema(sorted(allowed)), call_id=call_id)
    if reply.data is None:
        return {"row": None, "findings": [], "dropped": [],
                "error": "; ".join(reply.errors[:2]) or "no answer"}
    data = reply.data
    room_type = next((r.get("room_type") for r in building.get("rooms") or [] if r.get("id") == view.get("room_id")),
                     "exterior" if not view.get("room_id") else None)
    row = {"view": view.get("name"), "room_id": view.get("room_id"), "room_type": room_type,
           "tags": [t for t in data.get("tags") or [] if t in TAGS],
           "client_ready_score": int(data["client_ready_score"]), "note": data.get("note"), "judge": "ai"}
    findings, dropped = [], []
    for i, p in enumerate(data.get("problems") or []):
        f = {"id": f"j:{call_id}:{i + 1}", "source": "judge", "check": p.get("check"), "severity": p.get("severity"),
             "target": p.get("target"), "room_id": view.get("room_id"), "message": p.get("message"),
             "evidence": {"view": view.get("name"), "image": 1, "call_id": call_id}}
        if p.get("target") not in allowed:
            f["dropped"] = f"target {p.get('target')!r} is not an id of what was shown"
            dropped.append(f)
        else:
            findings.append(f)
    row["problems"] = [{k: f[k] for k in ("check", "severity", "target", "message")} for f in findings]
    return {"row": row, "findings": findings, "dropped": dropped, "error": None}


def rubric_mean(rows: list[dict]) -> Optional[float]:
    scores = [float(r["client_ready_score"]) for r in rows or [] if isinstance(r, dict)
              and isinstance(r.get("client_ready_score"), (int, float))]
    return round(statistics.mean(scores), 3) if scores else None


def house_score(rows: list[dict], code_findings: list[dict], model_findings: list[dict], architect_open_major: int,
                views: Optional[int] = None) -> dict:
    """The house score (module docstring): ``{"score", "rubric", "rubric_part", "defects_part", "counts"}``."""
    mean = rubric_mean(rows)
    n = max(1, int(views or len(rows) or 1))
    found = list(code_findings or []) + list(model_findings or [])
    crit = sum(1 for f in found if f.get("severity") == "critical")
    major = sum(1 for f in found if f.get("severity") == "major")
    rubric_part = (mean - 1.0) / 4.0 * 100.0 if mean is not None else 50.0
    defects = (CRITICAL_POINTS * crit + MAJOR_POINTS * (major + int(architect_open_major or 0))) / n
    defects_part = 100.0 / (1.0 + defects / DEFECT_SCALE)
    score = RUBRIC_WEIGHT * rubric_part + (1.0 - RUBRIC_WEIGHT) * defects_part
    return {"score": round(score, 2), "rubric": mean, "rubric_part": round(rubric_part, 2),
            "defects_part": round(defects_part, 2),
            "counts": {"critical": crit, "major": major, "architect_open_major": int(architect_open_major or 0),
                       "views": n, "judged": len(rows or [])}}


def verdict(before: Optional[dict], after: dict) -> str:
    """``first`` | ``better`` (at least ``MIN_GAIN``) | ``same`` | ``worse`` (more than ``WORSE_MARGIN`` lower)."""
    if not before:
        return "first"
    d = float(after["score"]) - float(before["score"])
    if d < -WORSE_MARGIN:
        return "worse"
    return "better" if d >= MIN_GAIN else "same"


def write(project_out, rows: list[dict], rec: Optional[dict] = None) -> None:
    """The rubric file and the big loop's record (module docstring). Never raises."""
    project_out = Path(project_out)
    try:
        path = project_out / RUBRIC_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(rows, key=lambda r: str(r.get("view"))), indent=1, ensure_ascii=False),
                        encoding="utf-8")
        if rec is not None:
            odir = LG.orchestrator_dir(project_out)
            LG.write_json_atomic(odir / LOOP_JSON, rec)
            (odir / LOOP_MD).write_text(report_md(rec), encoding="utf-8")
    except OSError:
        pass


def report_md(rec: dict) -> str:
    lines = ["# The big loop: the house score per cycle", "",
             "Each cycle: the AI judge scores every final render 1-5 as a client would (the problems it names are "
             "the next round's work, with the code's and the inspector's), the agent fixes, the changed views are "
             "rendered again and judged again; a cycle that lowers the score is rolled back, the loop goes on while "
             f"the score rises (at least {MIN_GAIN:g}) and time is left. Score = {RUBRIC_WEIGHT:.0%} the judge's mean "
             f"(1-5 as 0-100) + {1 - RUBRIC_WEIGHT:.0%} defects (100 / (1 + points per view / {DEFECT_SCALE:g}): "
             f"{CRITICAL_POINTS:g} points per critical, {MAJOR_POINTS:g} per major finding).", "",
             "| cycle | score | judge mean | critical | major | verdict | accepted edits | views re-rendered | note |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c in rec.get("cycles") or []:
        s = c.get("score") or {}
        cnt = s.get("counts") or {}
        lines.append(f"| {c.get('cycle')} | {s.get('score')} | {s.get('rubric')} | {cnt.get('critical')} | "
                     f"{cnt.get('major')} | {c.get('verdict')} | {c.get('accepted', '')} | {c.get('views', '')} | "
                     f"{str(c.get('note') or '').replace('|', '/')} |")
    lines += ["", f"Stop: {rec.get('stop') or 'running'}.", ""]
    worst = sorted((r for r in rec.get("rows") or [] if isinstance(r.get("client_ready_score"), int)),
                   key=lambda r: r["client_ready_score"])[:10]
    if worst:
        lines += ["The lowest-scored views of the last measure:", ""]
        lines += [f"- {r['view']} ({r.get('room_type')}): {r['client_ready_score']} - {r.get('note')}" for r in worst]
    return "\n".join(lines) + "\n"
