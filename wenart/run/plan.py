"""Pod plan of a full run (docs/milestone6.md §2.1 ``plan``, §8.1 time rule).

What: ``python -m wenart.run plan --projects synthetic-01,synthetic-03 [--out
run_plan.json]`` runs stage 1 (the pipeline, with the same stage record and
fingerprint reuse as the pod) for each project on the CPU and writes per
project: status, levels, rooms, empty rooms (the rooms the AI layout
furnishes), views, minutes, server starts, and a suggested pod split.

Rules (§4.1, §8.1, measured on the RTX PRO 4500 in M5):
- views per room by its area: 3 when >= 6 m², 2 when 3-6 m², 1 below 3 m²;
- minutes per project = 4 + 0.63 per view + 10 s per AI-furnished room
  (with polish, controls and gate calibration);
- server starts of a pod: 4 when a project has style photos without stored
  answers of both models, else 3 when a project has empty rooms, else 2;
- fixed minutes per pod = 7.7 (boot 1.5, setup 4.4, tests 0.7, copy 1.1) +
  4.5 per Qwen start + 2.3 per GLM start: 14.5 with 2 starts, 19.0 with 3,
  21.3 with 4;
- split: first fit, in the given order, under ``100 - fixed - 8`` minutes of
  project work per pod (77.5 / 73.0 / 70.7 with 2 / 3 / 4 starts;
  ``WENART_DEADLINE`` = entry + 100 min with ``--max-minutes 115``).

``needs_review`` projects get their report (``report.md`` of the pipeline)
and no pod time.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Optional

from wenart.run import scheduler as SC
from wenart.run.projects import check_name, public_project

MIN_PER_PROJECT = 4.0
MIN_PER_VIEW = 0.63
MIN_PER_AI_ROOM = 10.0 / 60.0
FIXED_BASE_MIN = 7.7
SERVER_START_MIN = {"qwen": 4.5, "glm": 2.3}
DEADLINE_MIN = 100.0
MARGIN_MIN = 8.0
# Server starts -> (Qwen starts, GLM starts).
STARTS = {2: (1, 1), 3: (2, 1), 4: (2, 2)}


def views_for_area(area: float) -> int:
    """§4.1: 3 views for a room of at least 6 m², 2 for 3-6 m², 1 below 3 m²."""
    area = float(area or 0.0)
    return 3 if area >= 6.0 else 2 if area >= 3.0 else 1


def building_views(building: dict) -> int:
    return sum(views_for_area(r.get("area_computed") or 0.0) for r in building.get("rooms") or [])


def project_minutes(views: int, ai_rooms: int) -> float:
    return round(MIN_PER_PROJECT + MIN_PER_VIEW * views + MIN_PER_AI_ROOM * ai_rooms, 2)


def server_starts(uncached_photos: bool, layout: bool) -> int:
    return 4 if uncached_photos else 3 if layout else 2


def fixed_minutes(starts: int) -> float:
    qwen, glm = STARTS[starts]
    return round(FIXED_BASE_MIN + qwen * SERVER_START_MIN["qwen"] + glm * SERVER_START_MIN["glm"], 2)


def limit_minutes(starts: int) -> float:
    return round(DEADLINE_MIN - fixed_minutes(starts) - MARGIN_MIN, 2)


def split(projects: list[dict]) -> list[dict]:
    """First-fit pod split of the ``ok`` projects (in order) under the per-pod limit of their server starts."""
    pods: list[dict] = []
    for p in projects:
        if p["status"] != "ok":
            continue
        placed = False
        for pod in pods:
            starts = max(pod["server_starts"], p["server_starts"])
            if pod["project_minutes"] + p["minutes"] <= limit_minutes(starts):
                pod["projects"].append(p["project"])
                pod["server_starts"] = starts
                pod["project_minutes"] = round(pod["project_minutes"] + p["minutes"], 2)
                placed = True
                break
        if not placed:
            pods.append({"projects": [p["project"]], "server_starts": p["server_starts"],
                         "project_minutes": p["minutes"]})
    for i, pod in enumerate(pods, start=1):
        pod["pod"] = i
        pod["fixed_minutes"] = fixed_minutes(pod["server_starts"])
        pod["limit_minutes"] = limit_minutes(pod["server_starts"])
        pod["job_minutes"] = round(pod["fixed_minutes"] + pod["project_minutes"], 2)
        pod["fits"] = pod["project_minutes"] <= pod["limit_minutes"]
    return pods


def project_entry(orch: "SC.Orchestrator", pr: "SC.ProjectRun") -> dict:
    """Stage 1 for one project and its numbers."""
    orch.stage_pipeline(pr)
    status = orch.status_of(pr, "pipeline")
    entry = {"project": pr.name, "status": "ok" if status in ("ok", "reused") else status,
             "stage_status": status, "levels": None, "rooms": None, "empty_rooms": None, "views": None,
             "photos": 0, "photos_cached": None, "minutes": 0.0, "server_starts": 0, "pod": None,
             "report": None, "note": (pr.records.get("pipeline").note if pr.records.get("pipeline") else None)}
    building = SC.read_json(pr.out / "building.json")
    if isinstance(building, dict):
        entry["levels"] = len(building.get("levels") or [])
        entry["rooms"] = len(building.get("rooms") or [])
    if entry["status"] != "ok" or not isinstance(building, dict):
        if (pr.out / "report.md").is_file():
            entry["report"] = SC.S.t(pr.out / "report.md")
        return entry
    mode = ((building.get("project") or {}).get("brief") or {}).get("empty_rooms", "ai")
    from wenart.furniture.layout import empty_rooms
    ai_rooms = len(empty_rooms(building)) if mode == "ai" else 0
    pr.photos = orch.photo_list(pr)
    cached = orch.photos_complete(pr) if pr.photos else None
    entry.update(empty_rooms=ai_rooms, views=building_views(building), photos=len(pr.photos), photos_cached=cached)
    entry["minutes"] = project_minutes(entry["views"], ai_rooms)
    entry["server_starts"] = server_starts(bool(pr.photos) and not cached, ai_rooms > 0)
    return entry


def make_plan(names: list[str], *, outputs: Optional[Path] = None, runner=SC.subprocess_runner,
              repo_root: Path = SC.REPO_ROOT, out=None, check_models: Optional[dict] = None) -> dict:
    opts = SC.RunOptions(projects=list(names), repo_root=Path(repo_root),
                         outputs=Path(outputs) if outputs else None, job_id="plan")
    orch = SC.Orchestrator(opts, runner=runner, out=out or (lambda line: None), check_models=check_models)
    entries = []
    for name in names:
        check_name(name)
        ref = public_project(name, orch.outputs_root, orch.repo_root)
        pr = SC.ProjectRun(replace(ref, out_dir=orch.outputs_root / name))
        SC.ST.run_dir(pr.out).mkdir(parents=True, exist_ok=True)
        entries.append(project_entry(orch, pr))
    pods = split(entries)
    for pod in pods:
        for name in pod["projects"]:
            next(e for e in entries if e["project"] == name)["pod"] = pod["pod"]
    return {"schema_version": "0.1", "kind": "run_plan", "projects": entries, "pods": pods,
            "rule": {"minutes_per_project": MIN_PER_PROJECT, "minutes_per_view": MIN_PER_VIEW,
                     "minutes_per_ai_room": round(MIN_PER_AI_ROOM, 4), "fixed_base_minutes": FIXED_BASE_MIN,
                     "server_start_minutes": SERVER_START_MIN, "deadline_minutes": DEADLINE_MIN,
                     "margin_minutes": MARGIN_MIN}}


def plan_text(plan: dict) -> str:
    lines = ["| Project | Status | Levels | Rooms | Empty rooms | Views | Photos | Minutes | Server starts | Pod |",
             "|---|---|---|---|---|---|---|---|---|---|"]

    def cell(v):
        return "-" if v is None else str(v)

    for e in plan["projects"]:
        photos = "-" if not e["photos"] else f"{e['photos']} ({'cached' if e['photos_cached'] else 'to ask'})"
        lines.append(f"| {e['project']} | {e['status']} | {cell(e['levels'])} | {cell(e['rooms'])} | "
                     f"{cell(e['empty_rooms'])} | {cell(e['views'])} | {photos} | "
                     f"{e['minutes'] if e['status'] == 'ok' else '-'} | "
                     f"{e['server_starts'] if e['status'] == 'ok' else '-'} | {cell(e['pod'])} |")
    lines += ["", "| Pod | Projects | Server starts | Fixed min | Project min | Limit min | Job min | Fits |",
              "|---|---|---|---|---|---|---|---|"]
    for pod in plan["pods"]:
        lines.append(f"| {pod['pod']} | {' '.join(pod['projects'])} | {pod['server_starts']} | "
                     f"{pod['fixed_minutes']} | {pod['project_minutes']} | {pod['limit_minutes']} | "
                     f"{pod['job_minutes']} | {'yes' if pod['fits'] else 'no (deadline cut, resume)'} |")
    review = [e for e in plan["projects"] if e["status"] != "ok"]
    if review:
        lines.append("")
        for e in review:
            lines.append(f"- {e['project']}: {e['status']}, no pod time"
                         + (f"; report {e['report']}" if e.get("report") else "") + (f" ({e['note']})" if e.get("note") else ""))
    return "\n".join(lines) + "\n"


def write_plan(plan: dict, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
