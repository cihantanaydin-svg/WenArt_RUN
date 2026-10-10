"""Pod plan of a full run (docs/milestone6.md §2.1 ``plan``, §8.1 time rule; docs/milestone7.md §9.3).

What: ``python -m wenart.run plan --projects synthetic-01,synthetic-03 [--gpu NAME] [--out run_plan.json]``
runs stages 1 and 2 (the sheet analysis and the pipeline, Milestone 10; with the same stage records and
fingerprint reuse as the pod) for each project on the CPU and writes per project: status,
levels, rooms, empty rooms (the rooms the AI layout furnishes), views,
recognition questions, minutes, server starts, and a suggested pod split.

Rules (§4.1, §8.1, measured on the RTX PRO 4500 in M5; M7 §9.3):
- views per room (§6.2, ``camsearch.room_view_count``): rooms the layout
  furnishes and rooms with furniture by the area of their polygon (3 from
  6 m², 2 from 3 m², else 1); a room that stays without furniture 1 view, or
  none below 2.5 m² (the pre-layout estimate of the camera search's rule);
- minutes per project = (4 + (0.63 + 1/60 window pull) per view + 10 s per
  AI-furnished room + recognition calls x 4.4 s / sequences) / GPU speed
  (with polish, controls and gate calibration);
- ``GPU_SPEED`` per GPU (1.0 = the RTX PRO 4500 of M5; larger is faster;
  the RTX PRO 6000 is measured by the prep pod, §9.2, and committed by the
  integrator; a GPU without a measured speed counts as 1.0, reported);
  ``--gpu`` names the pod's GPU (default ``GPU_PRIORITY[0]`` of
  ``scripts/gpu_run.py``, read without importing it); the scheduler divides
  its deadline estimates by the same speed;
- server starts of a pod: 4 when a project has style photos without stored
  answers of both models or recognition questions without stored (or
  committed, ``results/recognition/<p>/``) answers, else 3 when a project
  has empty rooms, else 2;
- fixed minutes per pod = 7.7 (boot 1.5, setup 4.4, tests 0.7, copy 1.1) +
  4.5 per Qwen start + 2.3 per GLM start: 14.5 with 2 starts, 19.0 with 3,
  21.3 with 4;
- split: first fit, in the given order, under ``100 - fixed - 8`` minutes of
  project work per pod (77.5 / 73.0 / 70.7 with 2 / 3 / 4 starts;
  ``WENART_DEADLINE`` = entry + 100 min with ``--max-minutes 115``).

A project whose pipeline exits 4 (``pending``: recognition questions
written, M7 §1.4) gets pod time from its pre-answer building (views
``unknown`` for a raster project without rooms); its pod row is marked not
verified. ``needs_review`` projects get their report (``report.md`` of the
pipeline) and no pod time.
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Optional

from wenart.run import scheduler as SC
from wenart.run import servers as SV
from wenart.run import stages as S
from wenart.run.projects import check_name, public_project

MIN_PER_PROJECT = 4.0
MIN_PER_VIEW = 0.63
MIN_WINDOW_PULL_PER_VIEW = 1.0 / 60.0      # M7 §9.3: + 1 s per view
MIN_PER_AI_ROOM = 10.0 / 60.0
EXTERIOR_FIXED_VIEWS = 5                   # Milestone 10 (§3.3): 4 corner views and 1 aerial view
FIXED_BASE_MIN = 7.7
SERVER_START_MIN = {"qwen": 4.5, "glm": 2.3}
DEADLINE_MIN = 100.0
MARGIN_MIN = 8.0
# Server starts -> (Qwen starts, GLM starts).
STARTS = {2: (1, 1), 3: (2, 1), 4: (2, 2)}
# Relative speed per GPU (time = time on the RTX PRO 4500 / speed). The RTX PRO 6000 is measured by the prep pod
# ($RESULTS/timing/gpu_speed.json, docs/milestone7.md §9.2) and committed here by the integrator; until then it
# counts as 1.0 and the plan says so.
GPU_SPEED = {"RTX PRO 4500": 1.0, "RTX 4090": 1.1,
             "RTX PRO 6000": 1.634}   # M7 prep pod 87xpy12z302wrz (3 Oct 2026): min of render and polish speed
DEFAULT_SPEED = 1.0
# VRAM per GPU (GB, RunPod catalog; scripts/gpu_run.py gpus): only the vLLM size tier (servers.server_seqs) uses it.
GPU_MEMORY_GB = {"RTX PRO 6000": 96, "RTX PRO 6000 WK": 96, "RTX PRO 4500": 32, "RTX 4090": 24}
GPU_RUN = SC.REPO_ROOT / "scripts" / "gpu_run.py"


def default_gpu(path: Path = GPU_RUN) -> str:
    """``GPU_PRIORITY[0]`` of ``scripts/gpu_run.py``, read with ``ast`` (the runner's network code is never
    imported); ``"RTX PRO 4500"`` when the file cannot be read."""
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return "RTX PRO 4500"
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "GPU_PRIORITY"
                                                for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                break
            if isinstance(value, (list, tuple)) and value and isinstance(value[0], str):
                return value[0]
    return "RTX PRO 4500"


def _key_of(name: Optional[str], table: dict) -> Optional[str]:
    """The longest key of ``table`` that names ``name`` (an ``nvidia-smi`` name such as ``NVIDIA RTX PRO 6000
    Blackwell Server Edition`` or a RunPod name such as ``RTX PRO 6000``), whole words, any case."""
    if not name:
        return None
    text = " ".join(str(name).upper().split())
    found = [k for k in table if re.search(rf"(?<![A-Z0-9]){re.escape(k.upper())}(?![A-Z0-9])", text)]
    return max(found, key=len) if found else None


def gpu_speed(name: Optional[str]) -> dict:
    """``{"name", "speed", "matched"}``: ``GPU_SPEED`` of the GPU ``name`` (``matched`` = the table key; None and
    speed 1.0 for an unknown or unmeasured GPU)."""
    key = _key_of(name, GPU_SPEED)
    return {"name": name, "speed": float(GPU_SPEED[key]) if key else DEFAULT_SPEED, "matched": key}


def gpu_memory_mib(name: Optional[str]) -> Optional[int]:
    key = _key_of(name, GPU_MEMORY_GB)
    return int(GPU_MEMORY_GB[key] * 1024) if key else None


def views_for_area(area: float) -> int:
    """§4.1: 3 views for a room of at least 6 m², 2 for 3-6 m², 1 below 3 m² (``camsearch.views_for_area``)."""
    from wenart.blender.camsearch import views_for_area as rule   # lazy: numpy
    return rule(float(area or 0.0))


def exterior_view_count(building: dict) -> int:
    """Milestone 10 (§3.3): the 4 corner views, the aerial view and 1 view per drawn elevation
    (``exterior.elevation_views``) of one exterior set."""
    from wenart.blender.exterior import elevation_views   # lazy: numpy
    return EXTERIOR_FIXED_VIEWS + len(elevation_views(building)[0])


def variant_rooms(building: dict) -> tuple[list, int]:
    """Milestone 10: ``(ids of the rooms rendered, exterior sets)`` over the base and every alternative
    (``views.views_for``: the base's rooms without the second twins of ``render.twin_rooms: one``, an alternative's
    changed rooms; one exterior set for the base and one for an alternative whose outside changed, with
    ``render.exterior_views``; the building's stored brief). A building without levels: every room, no set."""
    if not building.get("levels"):
        return [r.get("id") for r in building.get("rooms") or []], 0
    from wenart.building import alternative_ids
    from wenart.views import views_for
    ids: list = []
    sets = 0
    for vid in [S.BASE_VARIANT] + alternative_ids(building):
        plan = views_for(building, vid)
        ids += [rid for rid in plan["rooms"] if rid not in ids]
        sets += 1 if plan["exterior"] else 0
    return ids, sets


def building_views(building: dict, ai_rooms: Optional[list] = None) -> int:
    """Views of a building before the layout (M7 §6.2, the camera search's own rule): the rooms in ``ai_rooms``
    (the layout furnishes them) by the area of their polygon, every other room by
    ``camsearch.room_view_count(room, building)`` (its furniture decides: none -> 1 view, or 0 below 2.5 m²).
    Milestone 10: only the rooms the variants render (``variant_rooms``) plus the exterior views."""
    from wenart.blender.camsearch import room_polygon, room_view_count   # lazy: numpy
    from wenart.geometry import polygon_area
    furnished = {r.get("id") for r in ai_rooms or []}
    rendered, sets = variant_rooms(building)
    by_id = {r.get("id"): r for r in building.get("rooms") or []}
    total = 0
    for rid in rendered:
        room = by_id.get(rid)
        if room is None:
            continue
        if rid in furnished:
            total += views_for_area(polygon_area(room_polygon(room)))
        else:
            total += room_view_count(room, building)
    return total + (sets * exterior_view_count(building) if sets else 0)


def recognition_minutes(calls: dict, seqs: dict) -> float:
    """Minutes of the recognition calls ``{model key: calls}`` at ``seqs[key]`` calls at once (4.4 s per call)."""
    return sum(S.EST_VLM_CALL_S * n / max(1, int(seqs.get(k) or 1)) for k, n in calls.items()) / 60.0


def project_minutes(views: Optional[int], ai_rooms: int, recognition: float = 0.0, speed: float = 1.0) -> float:
    """§8.1 + M7 §9.3: (4 + (0.63 + 1/60) per view + 10 s per AI room + recognition minutes) / GPU speed."""
    work = (MIN_PER_PROJECT + (MIN_PER_VIEW + MIN_WINDOW_PULL_PER_VIEW) * (views or 0)
            + MIN_PER_AI_ROOM * ai_rooms + recognition)
    return round(work / (speed or 1.0), 2)


def server_starts(uncached_photos: bool, layout: bool, questions: bool = False) -> int:
    """4 with style photos or recognition questions to ask (a GLM session in phase 2), 3 with empty rooms or
    furnished rooms the layout completes (Milestone 10), else 2."""
    return 4 if (uncached_photos or questions) else 3 if layout else 2


def fixed_minutes(starts: int) -> float:
    qwen, glm = STARTS[starts]
    return round(FIXED_BASE_MIN + qwen * SERVER_START_MIN["qwen"] + glm * SERVER_START_MIN["glm"], 2)


def limit_minutes(starts: int) -> float:
    return round(DEADLINE_MIN - fixed_minutes(starts) - MARGIN_MIN, 2)


PLANNED = ("ok", "pending")     # project statuses that get pod time


def split(projects: list[dict]) -> list[dict]:
    """First-fit pod split of the ``ok`` and ``pending`` projects (in order) under the per-pod limit of their server
    starts; a pod with a pending project (or unknown views) is marked not verified."""
    pods: list[dict] = []
    for p in projects:
        if p["status"] not in PLANNED:
            continue
        placed = False
        for pod in pods:
            starts = max(pod["server_starts"], p["server_starts"])
            if pod["project_minutes"] + p["minutes"] <= limit_minutes(starts):
                pod["projects"].append(p["project"])
                pod["server_starts"] = starts
                pod["project_minutes"] = round(pod["project_minutes"] + p["minutes"], 2)
                pod["verified"] = pod["verified"] and p.get("verified", True)
                placed = True
                break
        if not placed:
            pods.append({"projects": [p["project"]], "server_starts": p["server_starts"],
                         "project_minutes": p["minutes"], "verified": p.get("verified", True)})
    for i, pod in enumerate(pods, start=1):
        pod["pod"] = i
        pod["fixed_minutes"] = fixed_minutes(pod["server_starts"])
        pod["limit_minutes"] = limit_minutes(pod["server_starts"])
        pod["job_minutes"] = round(pod["fixed_minutes"] + pod["project_minutes"], 2)
        pod["fits"] = pod["project_minutes"] <= pod["limit_minutes"]
    return pods


def project_entry(orch: "SC.Orchestrator", pr: "SC.ProjectRun", gpu: Optional[dict] = None) -> dict:
    """Stage 1 for one project and its numbers (``gpu``: ``{"speed", "seqs": {key: n}}``)."""
    gpu = gpu or {"speed": 1.0, "seqs": {}}
    # Milestone 10: the sheet analysis first, as on the pod (the pipeline's fingerprint includes sheets.json).
    orch.stage_sheets(pr)
    if orch.status_of(pr, "sheets") in ("ok", "reused", "pending"):
        orch.stage_pipeline(pr)
        status = orch.status_of(pr, "pipeline")
    else:
        status = orch.status_of(pr, "sheets")
    planned = "ok" if status in ("ok", "reused") else status
    entry = {"project": pr.name, "status": planned, "stage_status": status, "levels": None, "rooms": None,
             "empty_rooms": None, "completed_rooms": None, "views": None, "questions": None, "recognition_calls": None,
             "photos": 0, "photos_cached": None, "minutes": 0.0, "server_starts": 0, "pod": None, "verified": planned == "ok",
             "report": None, "note": next((pr.records[s].note for s in ("pipeline", "sheets") if pr.records.get(s)),
                                          None)}
    building = SC.read_json(pr.out / "building.json")
    if isinstance(building, dict):
        entry["levels"] = len(building.get("levels") or [])
        entry["rooms"] = len(building.get("rooms") or [])
    if planned not in PLANNED or not isinstance(building, dict):
        for name in ("report.md", "sheets_report.md"):        # the pipeline's report, else the sheets report
            if (pr.out / name).is_file():
                entry["report"] = S.t(pr.out / name)
                break
        return entry
    mode = ((building.get("project") or {}).get("brief") or {}).get("empty_rooms", "ai")
    from wenart.furniture import complete as CMP
    from wenart.furniture.layout import empty_rooms
    ai = empty_rooms(building) if mode == "ai" and building.get("rooms") else []
    # Milestone 10 (§2.1): the furnished rooms the layout completes ask the model too (scheduler.layout_needed).
    settings = CMP.load_settings(pr.ref.project_dir)
    completed = [r for r in CMP.furnished_rooms(building) if CMP.completion_skip_reason(r, settings) is None]
    pr.photos = orch.photo_list(pr)
    cached = orch.photos_complete(pr) if pr.photos else None
    calls = {}
    if planned == "pending":
        entry["questions"] = sum(len(orch.recognition_items(pr, q)) for q in S.QUESTION_DIRS)   # + sheet questions
        calls = {k: len(orch.recognition_missing(pr, k)) for k in orch.recognition_keys()}
        entry["recognition_calls"] = sum(calls.values())
    rooms = building.get("rooms") or []
    entry.update(empty_rooms=len(ai), completed_rooms=len(completed),
                 views=building_views(building, ai) if rooms else None, photos=len(pr.photos), photos_cached=cached)
    if not rooms:
        entry["note"] = "; ".join(n for n in (entry["note"], "views unknown: no room before the answers") if n)
    entry["minutes"] = project_minutes(entry["views"], len(ai) + len(completed),
                                       recognition_minutes(calls, gpu["seqs"]), gpu["speed"])
    entry["server_starts"] = server_starts(bool(pr.photos) and not cached, len(ai) + len(completed) > 0,
                                           bool(entry["recognition_calls"]))
    return entry


def _table(entry) -> bool:
    """A nested table of models (M12: ``check.yaml models.bakeoff``), not a model: every value is a dict."""
    return isinstance(entry, dict) and bool(entry) and all(isinstance(v, dict) for v in entry.values())


def gpu_plan(name: Optional[str], models: dict) -> dict:
    """``{"name", "speed", "speed_of", "memory_mib", "seqs": {key: n}}`` of the GPU the plan is made for."""
    speed = gpu_speed(name)
    mem = gpu_memory_mib(name)
    seqs = {k: SV.server_seqs(mem, SV.max_seqs_of(models, k)) for k in models if not _table(models[k])}
    return {"name": name, "speed": speed["speed"], "speed_of": speed["matched"], "memory_mib": mem, "seqs": seqs}


def make_plan(names: list[str], *, outputs: Optional[Path] = None, runner=SC.subprocess_runner,
              repo_root: Path = SC.REPO_ROOT, out=None, check_models: Optional[dict] = None,
              gpu: Optional[str] = None) -> dict:
    opts = SC.RunOptions(projects=list(names), repo_root=Path(repo_root),
                         outputs=Path(outputs) if outputs else None, job_id="plan")
    orch = SC.Orchestrator(opts, runner=runner, out=out or (lambda line: None), check_models=check_models)
    gpu_info = gpu_plan(gpu or default_gpu(), orch.models)
    entries = []
    for name in names:
        check_name(name)
        ref = public_project(name, orch.outputs_root, orch.repo_root)
        pr = SC.ProjectRun(replace(ref, out_dir=orch.outputs_root / name))
        SC.ST.run_dir(pr.out).mkdir(parents=True, exist_ok=True)
        entries.append(project_entry(orch, pr, gpu_info))
    pods = split(entries)
    for pod in pods:
        for name in pod["projects"]:
            next(e for e in entries if e["project"] == name)["pod"] = pod["pod"]
    return {"schema_version": "0.1", "kind": "run_plan", "gpu": gpu_info, "projects": entries, "pods": pods,
            "rule": {"minutes_per_project": MIN_PER_PROJECT, "minutes_per_view": MIN_PER_VIEW,
                     "window_pull_minutes_per_view": round(MIN_WINDOW_PULL_PER_VIEW, 4),
                     "minutes_per_ai_room": round(MIN_PER_AI_ROOM, 4), "vlm_call_seconds": S.EST_VLM_CALL_S,
                     "fixed_base_minutes": FIXED_BASE_MIN, "server_start_minutes": SERVER_START_MIN,
                     "deadline_minutes": DEADLINE_MIN, "margin_minutes": MARGIN_MIN, "gpu_speed": dict(GPU_SPEED)}}


def plan_text(plan: dict) -> str:
    gpu = plan.get("gpu") or {}
    lines = []
    if gpu:
        speed = (f"speed {gpu['speed']:g}" if gpu.get("speed_of") else
                 f"speed {gpu.get('speed', 1.0):g} (not measured: the RTX PRO 4500 times)")
        seqs = ", ".join(f"{k} {n}" for k, n in (gpu.get("seqs") or {}).items())
        lines += [f"GPU: {gpu.get('name') or '?'} ({speed}; vLLM sequences {seqs or '-'})", ""]
    lines += ["| Project | Status | Levels | Rooms | Empty rooms | Views | Photos | Questions | Minutes | "
              "Server starts | Pod |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]

    def cell(v):
        return "-" if v is None else str(v)

    for e in plan["projects"]:
        photos = "-" if not e["photos"] else f"{e['photos']} ({'cached' if e['photos_cached'] else 'to ask'})"
        questions = "-" if not e.get("questions") else f"{e['questions']} ({e['recognition_calls']} calls)"
        views = cell(e["views"]) if e["status"] not in PLANNED or e["views"] is not None else "unknown"
        lines.append(f"| {e['project']} | {e['status']} | {cell(e['levels'])} | {cell(e['rooms'])} | "
                     f"{cell(e['empty_rooms'])} | {views} | {photos} | {questions} | "
                     f"{e['minutes'] if e['status'] in PLANNED else '-'} | "
                     f"{e['server_starts'] if e['status'] in PLANNED else '-'} | {cell(e['pod'])} |")
    lines += ["", "| Pod | Projects | Server starts | Fixed min | Project min | Limit min | Job min | Fits "
                  "| Verified |",
              "|---|---|---|---|---|---|---|---|---|"]
    for pod in plan["pods"]:
        lines.append(f"| {pod['pod']} | {' '.join(pod['projects'])} | {pod['server_starts']} | "
                     f"{pod['fixed_minutes']} | {pod['project_minutes']} | {pod['limit_minutes']} | "
                     f"{pod['job_minutes']} | {'yes' if pod['fits'] else 'no (deadline cut, resume)'} | "
                     f"{'yes' if pod['verified'] else 'no (questions pending: pre-answer building)'} |")
    review = [e for e in plan["projects"] if e["status"] not in PLANNED]
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
