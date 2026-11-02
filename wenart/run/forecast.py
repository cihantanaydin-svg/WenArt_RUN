"""Run-time forecast of a full pod run (2 Nov 2026; user: "is there a way to predict the total required run time?" ...
"yes, build the forecast and the render reserve").

What: ``python -m wenart.run forecast --project real10 [--building outputs/real10/building_final.json] [--measure]
[--max-minutes 240] [--gpu-speed 1.0] [--out forecast.json]`` predicts the minutes of every part of a full run
(boot, the stages 0-12, the AI architect's answers, the first build, its floor look, Argus, the second build, the
previews, the final stages, the agent rounds) against the pod's time limit and says when the renders would start and
whether they fit. Every row names where its number comes from: ``measured`` (the project's last pod stage record),
``cpu`` (measured here with ``--measure``: one plan, one seeded check, the AI questions after the typical-floor
grouping), ``rate`` (a count of the building times a rate calibrated on the pod runs) or ``assumed`` (a default).

Why: the planner of Milestones 6-7 (``wenart.run.plan``) does not know the steps added since (the build's plan, the
AI architect, its look, Argus) and counts a build as 60 s: real10's runs of 1-2 Nov 2026 spent 3 h in the build and
then 168 min in the AI steps, and neither rendered. The scheduler now keeps a render reserve (``scheduler.
render_reserve_s``) from the same estimates; this forecast shows the plan before a pod is paid for.

How: pure apart from ``measure`` (which runs ``build.prepare`` and one check on the CPU) and the file reads; the rates
are module constants with their sources. After a run, ``compare`` puts the forecast beside the stage records.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

# The parts of a run, in order (the scheduler's: stages 0-12, then the agent chain, then the final stages).
PRE_STAGES = ("sheets", "pipeline", "recognize", "pipeline_final", "photos", "style", "assets", "fit", "layout",
              "decor_ask", "decor", "refit")

# Rates (seconds), with where they come from.
POD_FIXED_S = 150.0             # boot and setup: real10 runs of 2 Nov 2026 were running after 109 s
AGENT_SERVER_S = 420.0          # stages.EST_AGENT_SERVER_START_S (the 27B agent model's server)
STAGE_DEFAULT_S = {"sheets": 130.0, "pipeline": 160.0, "recognize": 60.0, "pipeline_final": 170.0, "assets": 10.0,
                   "fit": 50.0, "layout": 320.0, "decor_ask": 500.0, "decor": 60.0, "refit": 70.0}   # real10 run 1
BUILD_FIXED_S = 250.0           # Blender start, assets, save, model review: real10 pod 1,075 s for 844 s of phases
BUILD_PER_ITEM_S = 0.5          # a furniture or decor item built: real10 0.35 s, real04 and real06 0.6 s
BUILD_PER_WALL_S = 0.07         # real10 pod: 131 s for 2,004 wall objects
BUILD_PER_CAMERA_S = 2.0        # the build's previews: real10 pod 145 s for 71 cameras
PREPARE_PER_WALL_S = 0.09       # without --measure: real10 pod's plan 181 s for 1,839 walls
TOPDOWN_S = 150.0               # real10 run 2: 147 s
TASK_CALL_S = 45.0              # one AI architect batch (12 questions, text, 27B; assumed until a run logs it)
LOOK_CALL_S = 90.0              # one floor look (an image and up to 60 items; assumed)
CHECK_DEFAULT_S = 60.0          # one seeded plan and model review (assumed without --measure)
CHECKS_PER_BATCH = 3            # the together check, the units judged at once in parallel, the plan after (_verdicts)
RETRY_SHARE = 0.5               # extra batches for the retries (architect_ai.RETRIES)
QUESTIONS_DEFAULT = 80          # architect_ai.MAX_QUESTIONS when the questions are not counted
BATCH = 12                      # architect_ai.BATCH
ARGUS_FIXED_S = 300.0           # triage of the code lines' findings (assumed)
ARGUS_PER_FLOOR_S = 240.0       # discovery, visitor and lesson calls of a floor (assumed)
PREVIEW_PER_VIEW_S = 2.5        # stages.EST_PREVIEW_PER_VIEW_S
PREVIEW_FIXED_S = 60.0
FINAL_PER_VIEW_S = 14.0         # render (8 + 1 window pull), controls, the agent's check per view: stages.est_final
FINAL_FIXED_S = 600.0           # export, expected, combine, report and the final build's overhead
ROUND_EXTRA_S = 240.0           # an agent round beyond its build: planner calls, apply, refit, changed previews
MARGIN_S = 600.0                # scheduler.RESERVE_MARGIN_S
JUDGE_MEASURE_S = 600.0         # the big loop's first measure: the judge scores every final view (BIG_LOOP_MEASURE_S)
MAX_AGENT_ROUNDS = 3            # agent.loop.MAX_ROUNDS (a round removing fewer than 3 findings is the last, 2 Nov 2026)


def _read(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def history(project: str, roots=None) -> dict:
    """``{stage: {"seconds", "source"}}``: the project's newest successful stage record of each stage under
    ``runs/*/results/run/<p>/`` and ``results/baseline/latest/run/<p>/`` (the longest step of a record: a build or a
    render that ran more than once counts its full run)."""
    roots = [Path(r) for r in roots] if roots else \
        sorted(REPO_ROOT.glob("runs/*/results/run")) + [REPO_ROOT / "results" / "baseline" / "latest" / "run"]
    best: dict = {}
    for root in roots:
        d = root / project
        if not d.is_dir():
            continue
        for f in d.glob("*.json"):
            rec = _read(f)
            if not isinstance(rec, dict) or rec.get("status") not in ("ok", "reused", "warning"):
                continue
            steps = [float(s["seconds"]) for s in rec.get("steps") or [] if isinstance(s, dict)
                     and s.get("rc") == 0 and s.get("seconds")]
            secs = max(steps) if steps else float(rec.get("seconds") or 0.0)
            if rec.get("status") == "reused" or secs <= 0:
                continue
            when = str(rec.get("started_utc") or "")
            if f.stem not in best or when > best[f.stem]["when"]:
                best[f.stem] = {"seconds": round(secs, 1), "source": str(f.relative_to(REPO_ROOT))
                                if str(f).startswith(str(REPO_ROOT)) else str(f), "when": when}
    return best


def scene_cameras(project: str, roots=None) -> Optional[int]:
    """The number of cameras of the project's newest scene manifest (the views the run renders)."""
    paths = [Path(r) for r in roots] if roots else \
        sorted(REPO_ROOT.glob("runs/*/results/renders/" + project + "/scene_manifest.json"))
    for p in reversed(paths):
        d = _read(p)
        if isinstance(d, dict) and d.get("cameras") is not None:
            return len(d["cameras"])
    return None


def looked_levels(building: dict) -> list[str]:
    """The levels the AI architect's look and Argus walk: every level but a typical floor's copies (``typical_of``)."""
    levels = [lv for lv in building.get("levels") or [] if isinstance(lv, dict)]
    ids = {lv.get("id") for lv in levels}
    return [lv.get("id") for lv in levels if not (lv.get("typical_of") and lv.get("typical_of") in ids)]


def built_items(building: dict) -> int:
    """The furniture and decor items the build makes: none on a typical floor's copies left unfurnished (more than 3
    identical floors, UL254); copies of up to 3 identical floors are linked duplicates (counted as nothing)."""
    from wenart.blender import typical_copies as TC

    skip = set(TC.unfurnished_copies(building))
    levels = {lv.get("id"): lv for lv in building.get("levels") or [] if isinstance(lv, dict)}
    skip |= {lid for lid, lv in levels.items() if lv.get("typical_of") in levels}
    return sum(1 for key in ("furniture", "decor") for e in building.get(key) or []
               if isinstance(e, dict) and e.get("level_id") not in skip and e.get("build") is not False)


def views_of(building: dict) -> int:
    """The views a run renders (``plan.building_views``: by room area, the exterior views) when no scene says it."""
    try:
        from wenart.run import plan as PL
        return int(PL.building_views(building))
    except Exception:  # noqa: BLE001 - no estimate: one view a room
        return len(building.get("rooms") or [])


def build_seconds_of(building: dict, cameras: Optional[int] = None, prepare_s: Optional[float] = None) -> float:
    """Seconds of one build of ``building`` by the rates (``BUILD_*``; calibrated on real10, real04 and real06)."""
    walls = len(building.get("walls") or [])
    cams = views_of(building) if cameras is None else int(cameras)
    prep = float(prepare_s) if prepare_s is not None else PREPARE_PER_WALL_S * walls
    return BUILD_FIXED_S + BUILD_PER_ITEM_S * built_items(building) + BUILD_PER_WALL_S * walls \
        + BUILD_PER_CAMERA_S * cams + prep


def measure(building: dict, brief: Optional[dict] = None) -> dict:
    """CPU measurements here (``--measure``): one full plan (``build.prepare``), one seeded check (a plan with the
    first search as seed and the model review, as every AI answer is checked) and the AI architect's questions after
    the typical-floor grouping (``architect_ai.typical_questions``)."""
    from wenart.agent import architect_ai as AIA

    t0 = time.time()
    base = AIA.prep_of(building, brief, {})
    prepare_s = time.time() - t0
    t1 = time.time()
    prep = AIA.prep_of(building, brief, {})
    AIA.model_counts(prep)
    check_s = time.time() - t1
    record = base["architect"]
    user = {r["key"] for r in record.get("applied") or [] if r.get("by", "user") == "user"}
    asked, copies = AIA.typical_questions(building, AIA.open_questions(record, user))
    return {"prepare_s": round(prepare_s, 1), "check_s": round(check_s, 1),
            "questions": min(len(asked), AIA.MAX_QUESTIONS), "copies": sum(len(v) for v in copies.values()),
            "open": record.get("open")}


def forecast(project: str, building: dict, *, max_minutes: float = 300.0, gpu_speed: float = 1.0,
             hist: Optional[dict] = None, cpu: Optional[dict] = None, cameras: Optional[int] = None,
             reuse_stages: bool = False) -> dict:
    """The forecast of a full run of ``project`` (module docstring): ``{"rows": [{"part", "seconds", "source",
    "note"}], "total_s", "limit_s", "render_start_s", "renders_fit", "agent_rounds", "verdict"}``. Pure.
    ``reuse_stages``: the stages 0-12 are reused from the volume (their code and inputs unchanged)."""
    hist = hist or {}
    cpu = cpu or {}
    rows: list[dict] = []

    def add(part: str, seconds: float, source: str, note: str = "") -> None:
        rows.append({"part": part, "seconds": round(float(seconds), 1), "source": source, "note": note})

    add("boot and setup", POD_FIXED_S, "measured", "real10 runs of 2 Nov 2026")
    pre = 0.0
    for st in PRE_STAGES:
        if reuse_stages:
            continue
        if st in hist:
            pre += hist[st]["seconds"]
        else:
            pre += STAGE_DEFAULT_S.get(st, 0.0)
    measured_pre = all(st in hist for st in PRE_STAGES if st in STAGE_DEFAULT_S)
    add("stages 0-12 (reading to refit)", pre, "reused" if reuse_stages else ("measured" if measured_pre else "rate"),
        "reused from the volume" if reuse_stages else "the project's last stage records" if measured_pre else
        "real10 run 1 where no record")
    add("agent model server", AGENT_SERVER_S, "assumed", "stages.EST_AGENT_SERVER_START_S")
    cams = cameras if cameras is not None else views_of(building)
    check = float(cpu.get("check_s") or CHECK_DEFAULT_S)
    questions = int(cpu.get("questions") if cpu.get("questions") is not None else QUESTIONS_DEFAULT)
    batches = math.ceil(questions / BATCH) * (1.0 + RETRY_SHARE) if questions else 0.0
    add("AI architect: open questions", batches * (TASK_CALL_S + CHECKS_PER_BATCH * check),
        "cpu" if cpu else "assumed",
        f"{questions} question(s) after the typical-floor grouping, {batches:.1f} batch(es) with retries, "
        f"a check {check:.0f} s")
    if "build" in hist:
        build_s, bsrc, bnote = hist["build"]["seconds"], "measured", hist["build"]["source"]
    else:
        build_s = build_seconds_of(building, cams, cpu.get("prepare_s"))
        bsrc, bnote = "rate", f"{built_items(building)} items, {len(building.get('walls') or [])} walls, {cams} cameras"
    add("first build", build_s, bsrc, bnote)
    floors = looked_levels(building)
    add("top-down views", TOPDOWN_S, "measured", "real10 run 2")
    add("AI architect: floor look", len(floors) * (LOOK_CALL_S + CHECKS_PER_BATCH * check),
        "cpu" if cpu else "assumed", f"{len(floors)} floor(s): {', '.join(floors)} (copies of a typical floor skipped)")
    add("Argus", ARGUS_FIXED_S + ARGUS_PER_FLOOR_S * len(floors), "assumed", f"{len(floors)} floor(s) walked")
    add("second build (the decisions)", build_s, bsrc, "when the look or Argus accepted a decision")
    previews = hist.get("agent_previews", {}).get("seconds") or (PREVIEW_FIXED_S + PREVIEW_PER_VIEW_S * cams) / gpu_speed
    add("previews (round 0)", previews, "measured" if "agent_previews" in hist else "rate", f"{cams} view(s)")
    render_start = sum(r["seconds"] for r in rows)
    final = sum(hist[s]["seconds"] for s in ("render", "export", "controls", "check") if s in hist) \
        if "render" in hist else (FINAL_FIXED_S + FINAL_PER_VIEW_S * cams) / gpu_speed
    final += build_s                                       # the final round's build
    add("final stages (build, render, export, controls, check, report)", final,
        "measured" if "render" in hist else "rate", f"{cams} view(s)")
    add("judge's score of every final view (big loop measure, no cycles)", JUDGE_MEASURE_S, "assumed",
        "scheduler.BIG_LOOP_MEASURE_S; the cycles are off by default since 2 Nov 2026")
    limit = float(max_minutes) * 60.0
    used = sum(r["seconds"] for r in rows)
    spare = limit - MARGIN_S - used
    round_s = build_s + ROUND_EXTRA_S
    rounds = min(MAX_AGENT_ROUNDS, max(0, int(spare // round_s))) if spare > 0 else 0
    if rounds:
        add(f"agent rounds (up to {rounds})", rounds * round_s, "rate", f"a round {round_s / 60:.0f} min: its build "
            f"and {ROUND_EXTRA_S / 60:.0f} min of calls, apply and changed previews; fewer when a round removes fewer "
            f"than 3 findings")
    total = sum(r["seconds"] for r in rows)
    fits = render_start + final + MARGIN_S <= limit
    verdict = (f"the renders start at about {render_start / 60:.0f} min and the final stages end at about "
               f"{(render_start + final) / 60:.0f} min of {max_minutes:.0f}; {rounds} agent round(s) fit"
               if fits else
               f"the final stages would end at about {(render_start + final) / 60:.0f} min, past the {max_minutes:.0f} min "
               f"limit: the render reserve skips AI steps (the look, Argus, then the answers) to render first")
    return {"project": project, "rows": rows, "total_s": round(total, 1), "limit_s": limit,
            "render_start_s": round(render_start, 1), "final_s": round(final, 1), "renders_fit": fits,
            "agent_rounds": rounds, "verdict": verdict, "cpu": cpu, "cameras": cams,
            "made_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def compare(fc: dict, hist: dict) -> list[dict]:
    """The forecast beside what a run measured (``history`` of that run): ``[{"part", "forecast_s", "measured_s"}]``
    for the parts a stage record measures (the stages 0-12, the build, the previews, the render)."""
    pick = {"first build": "build", "previews (round 0)": "agent_previews"}
    out = []
    for r in fc.get("rows") or []:
        st = pick.get(r["part"])
        if r["part"].startswith("stages 0-12"):
            got = sum(hist[s]["seconds"] for s in PRE_STAGES if s in hist) or None
        else:
            got = hist.get(st, {}).get("seconds") if st else None
        out.append({"part": r["part"], "forecast_s": r["seconds"], "measured_s": got})
    return out


def text(fc: dict) -> str:
    """The forecast as a small table (minutes)."""
    lines = [f"Forecast of a full run of {fc['project']} ({fc['limit_s'] / 60:.0f} min limit)", "",
             "| part | min | source | note |", "|---|---|---|---|"]
    for r in fc["rows"]:
        lines.append(f"| {r['part']} | {r['seconds'] / 60:.1f} | {r['source']} | {r['note']} |")
    lines += [f"| **total** | **{fc['total_s'] / 60:.0f}** | | |", "", fc["verdict"]]
    return "\n".join(lines)


def main(args) -> int:
    """``python -m wenart.run forecast`` (``__main__``)."""
    project = args.project
    bpath = Path(args.building) if args.building else None
    if bpath is None:
        cands = sorted(REPO_ROOT.glob(f"runs/*/results/furniture/{project}/building_decor.json")) + \
            [REPO_ROOT / "outputs" / project / "building_final.json"]
        bpath = next((p for p in reversed(cands) if p.is_file()), None)
    if bpath is None or not bpath.is_file():
        print(f"no building for {project}: pass --building (a building_final.json or a run's building_decor.json)")
        return 2
    building = json.loads(bpath.read_text(encoding="utf-8"))
    cpu = measure(building) if args.measure else None
    fc = forecast(project, building, max_minutes=args.max_minutes, gpu_speed=args.gpu_speed, hist=history(project),
                  cpu=cpu, cameras=scene_cameras(project), reuse_stages=args.reuse_stages)
    fc["building"] = str(bpath)
    print(text(fc))
    if args.out:
        Path(args.out).write_text(json.dumps(fc, indent=1) + "\n", encoding="utf-8")
    return 0
