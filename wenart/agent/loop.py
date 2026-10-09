"""The feedback loop of the orchestrator (docs/milestone11.md §8).

What: ``AgentLoop(project_out, model, rerun=...).run()`` runs the rounds after round 0 (the stage chain to the
previews, run by the scheduler before the loop starts):

1. code critic (``critic_code``: plausibility, exterior and view checks; CPU, milliseconds);
2. vision critic (``critic_vision``: per room the top-down image, up to 2 previews and the plan crop; per exterior
   view its preview; strict JSON findings, screened by code);
3. planner: the agent model gets the critical and major findings (minor ones as optional) and the tools
   (``tools.build_registry``), at most ``max_calls`` = 40 tool calls per round, at most ``max_tries`` = 3 edits of
   the same target; every edit is validated by code and every accepted one goes to ``overrides.json``;
4. router: the earliest stage the accepted edits touch (``route``: ``pipeline_final`` < ``layout`` < ``refit`` <
   ``build`` < ``polish``; record-only edits do not re-run anything) and the views whose scene changed
   (``changed_views``); ``rerun(from_stage, views, round, final)`` re-runs the chain from there and renders only
   those views (previews: 960x540, 32 samples);
5. stop when no critical or major finding is left, when no edit was accepted in the round, after ``max_rounds`` =
   4, or when ``now + estimate(final stages) > deadline - 20 min`` (checked before every round and before every
   re-run; the edits of a round cut there stay in ``overrides.json`` and reach the final renders).

``final_round(k)`` is the one extra round after the final check: critical findings only, on the final renders.

Why: §8; the scheduler (``wenart.run.scheduler``) owns the stages, this loop owns the decisions, and both are
driven on the CPU with fakes: the model (``MockModel``), the critics, the re-run function and the clock are
injected, like the scheduler's own runner and clock.

How: every event goes to ``AgentLog`` (§9) and the log is saved after every round; ``round()`` returns a summary
the report reads through the log.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.agent.model import MAX_IMAGES, ModelError, user_message

STAGE_ORDER = ("pipeline_final", "layout", "refit", "build", "polish")
MAX_ROUNDS = 4
MAX_CALLS = 120                 # per round (pod G2: one planner session for 252 findings fixed one room, then stopped)
MAX_CALLS_PER_ROOM = 12         # M11 pod G2: one planner session per room (or the building), worst room first
MAX_TRIES = 3
MARGIN_S = 20 * 60.0                  # stop at least 20 min before the deadline (the user's rule, §8)
STOPS = {
    "no_finding": "no critical or major finding left",
    "no_edit": "no edit accepted in this round",
    "max_rounds": "max rounds reached",
    "deadline": "time budget: the final stages need the time left before the deadline - 20 min",
    "rerun_failed": "the re-run of the changed stages failed",
    "model_error": "the agent model did not answer",
}


def route(accepted: list[dict]) -> Optional[str]:
    """The earliest stage of ``STAGE_ORDER`` the accepted edits re-run from; record-only edits (``applied:
    false``: ``correct_geometry`` in M11) re-run nothing, so a round with only those gives None."""
    stages = [a["result"].get("rerun_from") for a in accepted
              if a["result"].get("rerun_from") and a["result"].get("applied", True) is not False]
    stages = [s for s in stages if s in STAGE_ORDER]
    return min(stages, key=STAGE_ORDER.index) if stages else None


def changed_views(cameras: list[dict], accepted: list[dict], room_of: Callable[[str], Optional[str]]) -> list[str]:
    """The views whose scene the accepted edits change: the views of every room a furniture edit touched, every
    camera edit's view, every exterior view after an exterior edit, every view after a material edit."""
    rooms: set = set()
    views: set = set()
    exterior = everything = False
    for a in accepted:
        tool, args, res = a["tool"], a.get("args") or {}, a.get("result") or {}
        if tool in OV.FURNITURE_TOOLS:
            if args.get("room_id"):
                rooms.add(args["room_id"])
            for pid in [args.get("piece_id")] + list(res.get("changed_ids") or []):
                r = room_of(pid) if pid else None
                if r:
                    rooms.add(r)
        elif tool in OV.CAMERA_TOOLS:
            if tool != "remove_camera":
                views.add(args.get("view_id"))
        elif tool == "set_exterior":
            exterior = True
        elif tool == "set_material":
            everything = True
    for c in cameras:
        name = c.get("name")
        kind = c.get("kind") or ("exterior" if not c.get("room_id") else "interior")
        if everything or c.get("room_id") in rooms or (exterior and kind == "exterior"):
            views.add(name)
    return sorted(v for v in views if v)


def prune_images(messages: list, keep: int = MAX_IMAGES) -> None:
    """Keep only the ``keep`` newest images of the conversation (the server takes at most 4 per call); older image
    parts become a short text."""
    seen = 0
    for m in reversed(messages):
        content = m.get("content")
        if not isinstance(content, list):
            continue
        for i in range(len(content) - 1, -1, -1):
            part = content[i]
            if isinstance(part, dict) and part.get("type") == "image_url":
                seen += 1
                if seen > keep:
                    content[i] = {"type": "text", "text": "[an older image was removed: at most 4 images per call]"}


class AgentLoop:
    """Rounds, router, stop rules and the log of one project (module docstring)."""

    def __init__(self, project_out, model, *, rerun: Optional[Callable] = None, clock: Callable[[], float] = time.time,
                 deadline: Optional[float] = None, final_estimate=0.0, margin_s: float = MARGIN_S,
                 max_rounds: int = MAX_ROUNDS, max_calls: int = MAX_CALLS, max_tries: int = MAX_TRIES,
                 code_critic: Optional[Callable] = None, vision_critic: Optional[Callable] = None, vision: bool = True,
                 registry: Optional[TL.Registry] = None, apply_edit: Optional[Callable] = None, validators=None,
                 plausibility=None, catalog_loader: Optional[Callable] = None, out: Callable[[str], None] = print,
                 log: Optional[LG.AgentLog] = None, preview_dir: str = TL.PREVIEW_DIR, project: str = ""):
        self.project_out = Path(project_out)
        self.model = model
        self.rerun = rerun
        self.clock = clock
        self.deadline = deadline
        self.final_estimate = final_estimate
        self.margin_s = float(margin_s)
        self.max_rounds = int(max_rounds)
        self.max_calls = int(max_calls)
        self.max_tries = int(max_tries)
        self.code_critic = code_critic
        self.vision_critic = vision_critic
        self.vision = vision
        self.registry = registry or TL.build_registry()
        self.apply_edit = apply_edit
        self.validators = validators
        self.plausibility = plausibility
        self.catalog_loader = catalog_loader
        self.out = out
        self.preview_dir = preview_dir
        self.log = log or LG.AgentLog(self.project_out, project or self.project_out.name,
                                      getattr(model, "model", ""), getattr(model, "revision", ""), clock=clock)
        if hasattr(model, "on_call") and model.on_call is None:
            model.on_call = self.log.call
        self.overrides = OV.Overrides(self.project_out, project or self.project_out.name)
        self.vision_cache: dict = {}         # room/view key -> kept vision findings of the last critique
        self.stale_keys: Optional[set] = None   # keys to critique again (None: all)
        self.rounds: list[dict] = []
        self.stop: Optional[dict] = None

    # ----- time ------------------------------------------------------------------------

    def estimate(self) -> float:
        return float(self.final_estimate() if callable(self.final_estimate) else self.final_estimate or 0.0)

    def time_ok(self) -> bool:
        """``now + estimate(final stages) <= deadline - margin`` (§8)."""
        if self.deadline is None:
            return True
        return self.clock() + self.estimate() <= float(self.deadline) - self.margin_s

    # ----- context ------------------------------------------------------------------------

    def context(self, round_no: int, preview_dir: Optional[str] = None) -> TL.ToolContext:
        return TL.ToolContext.load(self.project_out, round=round_no, model_id=getattr(self.model, "model", ""),
                                   log=self.log, overrides=self.overrides,
                                   preview_dir=preview_dir or self.preview_dir, apply_edit=self.apply_edit,
                                   validators=self.validators, plausibility=self.plausibility,
                                   catalog_loader=self.catalog_loader, max_tries=self.max_tries)

    def rendered_building(self, ctx: TL.ToolContext) -> dict:
        """What the renders show: ``building_final.json`` (after refit), else the working building."""
        return TL.read_json(self.project_out / "building_final.json") or ctx.building

    def render_manifest(self, preview_dir: str) -> Optional[dict]:
        return TL.read_json(self.project_out / preview_dir / "render_manifest.json")

    # ----- critics ---------------------------------------------------------------------------

    def run_code_critic(self, ctx: TL.ToolContext, preview_dir: str) -> dict:
        building = self.rendered_building(ctx)
        manifest = self.render_manifest(preview_dir)
        if self.code_critic is not None:
            return self.code_critic(building, ctx.scene, manifest)
        kwargs = {}
        if self.plausibility is not None:
            kwargs["plausibility_fn"] = self.plausibility.score_building
        if self.validators is not None:
            kwargs["exterior_fn"] = self.validators.check_exterior
            kwargs["views_fn"] = self.validators.check_views
        return CC.run(building, ctx.scene, manifest, **kwargs)

    def critique_keys(self, ctx: TL.ToolContext, building: dict) -> list[tuple[str, str]]:
        """``[(kind, id)]``: rooms with pieces or views, exterior views with a preview."""
        keys = []
        cams = ctx.cameras()
        for r in building.get("rooms") or []:
            rid = r.get("id")
            has_piece = any(f.get("room_id") == rid for f in building.get("furniture") or [])
            has_view = any(c.get("room_id") == rid for c in cams)
            if has_piece or has_view:
                keys.append(("room", rid))
        for c in cams:
            kind = c.get("kind") or ("exterior" if not c.get("room_id") else "interior")
            if kind == "exterior" and ctx.preview_path(c["name"]) is not None:
                keys.append(("view", c["name"]))
        return keys

    def run_vision_critic(self, ctx: TL.ToolContext, code: dict, round_no: int) -> dict:
        """Kept and dropped vision findings of every room / exterior view (re-asked only where the scene changed;
        the others keep their last answer)."""
        if self.vision_critic is not None:
            return self.vision_critic(self, ctx, code, round_no)
        if not self.vision:
            return {"kept": [], "dropped": [], "checks": []}
        building = self.rendered_building(ctx)
        kept, dropped, checks = [], [], []
        n = 0
        for kind, key in self.critique_keys(ctx, building):
            cache_key = f"{kind}:{key}"
            if self.stale_keys is not None and cache_key not in self.stale_keys and cache_key in self.vision_cache:
                kept += self.vision_cache[cache_key]
                continue
            n += 1
            call_id = f"r{round_no}-v{n}"
            try:
                if kind == "room":
                    views = [c["name"] for c in ctx.cameras() if c.get("room_id") == key]
                    previews = [(v, ctx.preview_path(v)) for v in views if ctx.preview_path(v) is not None]
                    topdown = ctx.topdown(key, building, what="critic")
                    res = CV.critique_room(self.model, building, key, previews=previews, topdown=topdown,
                                           plan_crop=ctx.plan_crop_path(key), code=code, call_id=call_id)
                else:
                    res = CV.critique_exterior(self.model, building, key, preview=ctx.preview_path(key),
                                               plan_crop=None, code=code, call_id=call_id)
            except ModelError as exc:
                checks.append({"source": "vision", "target": key, "status": "error", "note": str(exc),
                               "call_id": call_id})
                continue
            images = [self.image_ref(p) for p in res.get("images") or []]
            checks.append({"source": "vision", "target": key, "status": "error" if res["error"] else "ok",
                           "note": res["error"], "call_id": call_id, "images": images,
                           "counts": {"kept": len(res["kept"]), "dropped": len(res["dropped"])}})
            for f in res["kept"] + res["dropped"]:
                f["evidence"]["images"] = images
            self.vision_cache[cache_key] = res["kept"]
            kept += res["kept"]
            dropped += res["dropped"]
        return {"kept": kept, "dropped": dropped, "checks": checks}

    # ----- logging helpers ---------------------------------------------------------------------

    def image_ref(self, path) -> str:
        """An image of the log: relative to ``orchestrator/`` (its own images), else ``../<path in the project
        output>`` (previews, plan crops), never an absolute path."""
        p = Path(path).resolve()
        try:
            return p.relative_to(self.log.dir.resolve()).as_posix()
        except ValueError:
            pass
        try:
            return "../" + p.relative_to(self.project_out.resolve()).as_posix()
        except ValueError:
            return p.name

    def log_findings(self, round_no: int, code: dict, vision: dict) -> None:
        for c in code.get("checks") or []:
            self.log.event("check", round_no, source="code", tool=c["source"], status=c["status"], note=c.get("note"),
                           counts=c.get("counts"))
        for c in vision.get("checks") or []:
            self.log.event("check", round_no, source="vision", target=c.get("target"), status=c["status"],
                           note=c.get("note"), counts=c.get("counts"), call_id=c.get("call_id"),
                           model=self.log.model, revision=self.log.revision,
                           evidence={"images": c.get("images") or []})
        for f in (code.get("findings") or []) + (vision.get("kept") or []) + (vision.get("dropped") or []):
            self.log.event("finding", round_no, source=f["source"], checklist=f["check"], severity=f["severity"],
                           target=f["target"], room_id=f.get("room_id"), finding=f["message"],
                           evidence=f.get("evidence"), dropped=f.get("dropped"),
                           call_id=(f.get("evidence") or {}).get("call_id"),
                           model=self.log.model if f["source"] != "code" else None,
                           revision=self.log.revision if f["source"] != "code" else None)

    def log_edit(self, round_no: int, call_id: str, tool: str, args: Optional[dict], result: dict,
                 label: Optional[str], findings: list[dict]) -> None:
        target = TL._target(tool, args or {})
        match = next((f for f in findings if f.get("target") == target), None) or next(
            (f for f in findings if f.get("room_id") and f.get("room_id") == (args or {}).get("room_id")), None)
        accepted = bool(result.get("accepted"))
        failed = list(result.get("failed_checks") or ([] if accepted else [str(result.get("error") or "rejected")]))
        self.log.event("edit" if accepted else "rejected_edit", round_no, model=self.log.model or "unknown",
                       revision=self.log.revision, call_id=call_id, tool=tool, args=dict(args or {}),
                       target=target, checklist=match["check"] if match else None,
                       severity=match["severity"] if match else None, finding=match["message"] if match else None,
                       validation={"accepted": accepted, "failed_checks": failed,
                                   "score_before": result.get("score_before"),
                                   "score_after": result.get("score_after")},
                       label=label, reason=str((args or {}).get("reason") or "no reason given"),
                       before=result.get("before_image"), after=result.get("after_image"),
                       rerun_from=result.get("rerun_from"), overrides_id=result.get("overrides_id"),
                       note=result.get("message") or None)

    # ----- planner -------------------------------------------------------------------------------

    def plan(self, ctx: TL.ToolContext, round_no: int, findings: list[dict], minor: list[dict],
             critical_only: bool = False) -> dict:
        """The planner of one round: one session per room (findings without a room: one "building" session), the
        room with the most critical, then major findings first; each session gets at most ``MAX_CALLS_PER_ROOM``
        tool calls, the round at most ``max_calls``, and no session starts after the time budget. (Pod G2, real02:
        one session for 252 findings fixed one room and called finish.) ``{"calls", "schema_errors", "replies",
        "error", "sessions"}``."""
        groups: dict[str, list[dict]] = {}
        for f in findings:
            groups.setdefault(str(f.get("room_id") or "building"), []).append(f)
        rank = {"critical": 0, "major": 1, "minor": 2}

        def key(item):
            room, fs = item
            return (-sum(1 for f in fs if f["severity"] == "critical"), -len(fs), room)

        total = {"calls": 0, "replies": 0, "error": None, "sessions": 0}
        for room, fs in sorted(groups.items(), key=key):
            budget = min(MAX_CALLS_PER_ROOM, self.max_calls - total["calls"])
            if budget <= 0 or (total["sessions"] and not self.time_ok()):
                break
            room_minor = [m for m in minor if str(m.get("room_id") or "building") == room]
            fs = sorted(fs, key=lambda f: rank.get(f["severity"], 3))
            ctx.finished = None
            res = self.plan_session(ctx, round_no, fs, room_minor, budget, critical_only, session=total["sessions"])
            total["sessions"] += 1
            total["calls"] += res["calls"]
            total["replies"] += res["replies"]
            if res["error"]:
                total["error"] = res["error"]
                if not ctx.accepted:
                    break
        ctx.finished = ctx.finished or {"open_findings": []}
        return dict(total, schema_errors=ctx.schema_errors)

    def plan_session(self, ctx: TL.ToolContext, round_no: int, findings: list[dict], minor: list[dict], budget: int,
                     critical_only: bool = False, session: int = 0) -> dict:
        """One planner conversation (one room); ``{"calls", "replies", "error"}``."""
        messages = [{"role": "system", "content": P.PLANNER_SYSTEM},
                    {"role": "user", "content": P.planner_task(round_no, findings, minor, budget, critical_only)}]
        specs = self.registry.specs()
        calls = replies = 0
        error = None
        tag = f"r{round_no}-s{session + 1}" if session else f"r{round_no}"
        while calls < budget and ctx.finished is None:
            replies += 1
            prune_images(messages)
            try:
                reply = self.model.chat(messages, specs, call_id=f"{tag}-p{replies}")
            except ModelError as exc:
                error = str(exc)
                break
            messages.append(reply.assistant_message())
            if not reply.tool_calls:
                break
            for i, tc in enumerate(reply.tool_calls):
                call_id = f"{tag}-p{replies}-t{i + 1}"
                if calls >= budget:
                    result = {"error": f"the budget of {budget} tool calls for these findings is used up"}
                else:
                    calls += 1
                    tool = self.registry.tools.get(tc.name)
                    label = TL.label_for(tc.name, ctx, tc.parsed or {}) if tool and tool.kind in TL.EDIT_KINDS \
                        else None
                    result = self.registry.call(ctx, tc.name, tc.parsed, tc.error)
                    if tool is not None and tool.kind in TL.EDIT_KINDS:
                        self.log_edit(round_no, call_id, tc.name, tc.parsed, result, label, findings + minor)
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": json.dumps(result, ensure_ascii=False, default=str)[:12000]})
            if ctx.pending_images:
                shown = ctx.pending_images[-MAX_IMAGES:]
                labels = [f"Image from a tool: {Path(p).name}" for p in shown]
                messages.append(user_message("The images the tools returned, newest last.", shown, labels))
                ctx.pending_images.clear()
        return {"calls": calls, "replies": replies, "error": error}

    # ----- one round ---------------------------------------------------------------------------------

    def copy_previews(self, views: list[str], round_no: int, when: str, preview_dir: str) -> dict:
        out = {}
        for v in views:
            src = self.project_out / preview_dir / f"{v}_preview.jpg"
            if src.is_file():
                dst = self.log.images_dir / f"r{round_no}_{v}_{when}.jpg"
                shutil.copyfile(src, dst)
                out[v] = self.log.rel(dst)
        return out

    def round(self, round_no: int, *, critical_only: bool = False, final: bool = False) -> dict:
        t0 = self.clock()
        preview_dir = TL.FINAL_RENDER_DIR if final else self.preview_dir
        ctx = self.context(round_no, preview_dir)
        code = self.run_code_critic(ctx, preview_dir)
        ctx.violations = list(code.get("findings") or [])
        vision = self.run_vision_critic(ctx, code, round_no)
        self.log_findings(round_no, code, vision)
        found = list(code.get("findings") or []) + list(vision.get("kept") or [])
        wanted = ("critical",) if critical_only else ("critical", "major")
        open_ = [f for f in found if f["severity"] in wanted]
        minor = [f for f in found if f["severity"] not in wanted]
        summary = {"round": round_no, "final": final, "findings": {s: sum(1 for f in found if f["severity"] == s)
                                                                    for s in P.SEVERITIES},
                   "dropped": len(vision.get("dropped") or []), "accepted": 0, "rejected": 0, "calls": 0,
                   "schema_errors": 0, "rerun_from": None, "views": [], "stop": None}
        self.rounds.append(summary)
        if not open_:
            summary["stop"] = "no_finding"
            return self._end_round(summary, t0)
        plan = self.plan(ctx, round_no, open_, minor, critical_only)
        summary.update(calls=plan["calls"], schema_errors=plan["schema_errors"], accepted=len(ctx.accepted),
                       rejected=len(ctx.rejected))
        if plan["error"] and not ctx.accepted:
            summary["stop"] = "model_error"
            return self._end_round(summary, t0)
        if not ctx.accepted:
            summary["stop"] = "no_edit"
            return self._end_round(summary, t0)
        stage = route(ctx.accepted)
        before_building = TL.read_json(TL.working_building_path(self.project_out)) or {}

        def room_of(pid):
            for b in (before_building, ctx.building):
                p = next((f for f in b.get("furniture") or [] if f.get("id") == pid), None)
                if p is not None:
                    return p.get("room_id")
            return None

        views = changed_views(ctx.cameras(), ctx.accepted, room_of)
        summary.update(rerun_from=stage, views=views)
        rooms = {c.get("room_id") for c in ctx.cameras() if c.get("name") in views and c.get("room_id")}
        rooms |= {a["args"].get("room_id") for a in ctx.accepted if a["args"].get("room_id")}
        rooms |= {room_of(a["args"].get("piece_id")) for a in ctx.accepted if a["args"].get("piece_id")}
        self.stale_keys = {f"room:{r}" for r in rooms if r} | {f"view:{v}" for v in views}
        if stage is None:
            self.log.event("rerun", round_no, rerun_from=None, status="skipped",
                           note="record-only edits: nothing to re-run")
            return self._end_round(summary, t0)
        if not self.time_ok():
            summary["stop"] = "deadline"
            self.log.event("rerun", round_no, rerun_from=stage, status="skipped", views=views,
                           note="time budget: the accepted edits reach the final renders")
            return self._end_round(summary, t0)
        before = self.copy_previews(views, round_no, "before", preview_dir)
        if self.rerun is None:
            res = {"status": "skipped", "views": [], "note": "no re-run function"}
        else:
            res = self.rerun(stage, views, round_no, final) or {}
        status = str(res.get("status") or "ok")
        self.log.event("rerun", round_no, rerun_from=stage, status=status, views=views,
                       seconds=res.get("seconds"), note=res.get("note"))
        after = self.copy_previews(views, round_no, "after", preview_dir)
        for v in views:
            if v in before or v in after:
                self.log.event("render", round_no, views=[v], before=before.get(v), after=after.get(v),
                               status="final" if final else "preview")
        if status not in ("ok", "reused", "warning", "skipped"):
            summary["stop"] = "rerun_failed"
        return self._end_round(summary, t0)

    def _end_round(self, summary: dict, t0: float) -> dict:
        summary["seconds"] = round(self.clock() - t0, 1)
        self.log.save()
        self.out(f"agent round {summary['round']}: findings {summary['findings']}, accepted {summary['accepted']}, "
                 f"rejected {summary['rejected']}, re-run {summary['rerun_from'] or '-'} "
                 f"({len(summary['views'])} views)" + (f", stop: {STOPS[summary['stop']]}" if summary["stop"] else ""))
        return summary

    # ----- the loop --------------------------------------------------------------------------------------

    def run(self, start_round: int = 1) -> dict:
        """Rounds ``start_round`` .. ``max_rounds`` with the stop rules (module docstring)."""
        stop = None
        last = start_round - 1
        for k in range(start_round, self.max_rounds + 1):
            if not self.time_ok():
                stop = "deadline"
                break
            last = k
            res = self.round(k)
            if res["stop"]:
                stop = res["stop"]
                break
        if stop is None:
            stop = "max_rounds"
        self.stop = {"round": last, "reason": stop}
        self.log.event("stop", last, reason=STOPS[stop], status=stop,
                       note=f"{sum(r['accepted'] for r in self.rounds)} edits accepted in {len(self.rounds)} rounds")
        self.log.save()
        return self.summary()

    def final_round(self, round_no: int) -> dict:
        """The extra round after the final check: critical findings only, on the final renders (§8 "final")."""
        if not self.time_ok():
            self.log.event("stop", round_no, reason=STOPS["deadline"], status="deadline",
                           note="final round for critical findings not started")
            self.log.save(final=True)
            return {"round": round_no, "stop": "deadline", "accepted": 0}
        res = self.round(round_no, critical_only=True, final=True)
        self.log.event("stop", round_no, reason="final round for critical findings done", status=res["stop"] or "done")
        self.log.save(final=True)
        return res

    def summary(self) -> dict:
        return {"rounds": list(self.rounds), "stop": self.stop,
                "accepted": sum(r["accepted"] for r in self.rounds),
                "rejected": sum(r["rejected"] for r in self.rounds), "log": str(self.log.dir / LG.LOG_JSON)}
