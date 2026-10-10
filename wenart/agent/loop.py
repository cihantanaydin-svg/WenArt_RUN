"""The feedback loop of the orchestrator (docs/milestone11.md §8; docs/milestone12.md §5.4 D19).

What: ``AgentLoop(project_out, model, rerun=...).run()`` runs the rounds after round 0 (the stage chain to the
previews, run by the scheduler before the loop starts):

1. code critic (``critic_code``: plausibility, exterior and view checks, and in M12 the group checks G1–G14, the
   level checks L1–L7, the scene checks S1–S6 of the build and the library gaps; CPU, milliseconds) on EVERY room,
   every round;
2. vision critic (``critic_vision``) only where an image adds something: per room its renders (looks, wrong objects,
   decor that looks wrong; built pieces only, never what code measures) and per exterior view its preview; strict
   JSON findings, screened by code (a duplicate of a code finding under a related check id is dropped);
3. planner: one session per room with a FIXABLE critical or major finding (``brief.classify``: findings no tool may
   fix are never sent as work). Rooms are ranked by the number of earlier sessions (every room gets one before any
   room gets a second, across rounds), then by fixable severity x area (``brief.fixable_weight``), then by id.
   Each session (``plan_session``) gets the room brief (``brief.room_brief``), first answers with a JSON plan
   (``prompts.PLAN_SCHEMA``) that the loop checks against the brief (``check_plan``: offered tool, fixable finding,
   allowed for its target, built target), then works the checked plan as its checklist with the tools
   (``tools.PLANNER_TOOLS``; ``dry_run`` is free; one edit per piece per reply, the next only after its result) until
   the checklist is done, ``finish``, or its ``MAX_CALLS_PER_ROOM`` = 12 tool calls are used. Up to ``workers``
   (default 4; the scheduler passes the server's sequences) sessions run in parallel on one server. A round has a
   TIME cap (``round_cap_s``, default 15 min) instead of M11's call cap (B8: the old docstring said 40 calls per
   round, the code had 120); ``max_calls`` stays as an optional cap (tests). An edit identical to one rejected
   earlier in the room is refused by the tools without validation (``memory.Memory``,
   ``orchestrator/memory.json``); open checklist steps go to the next round's brief;
4. router: the earliest stage the accepted edits touch (``route``: ``pipeline_final`` < ``layout`` < ``refit`` <
   ``build`` < ``polish``; record-only edits do not re-run anything) and the views whose scene changed
   (``changed_views``); ``rerun(from_stage, views, round, final)`` re-runs the chain from there and renders only
   those views (previews: 960x540, 32 samples);
5. stop when no critical or major finding is left, when none of them is fixable, when no edit was accepted in the
   round, after ``max_rounds`` = 4, or when ``now + estimate(final stages) > deadline - 20 min`` (checked before
   every round, every session and every re-run; the scheduler's estimate uses the throughput measured on this pod,
   B6; the edits of a round cut there stay in ``overrides.json`` and reach the final renders).

``final_round(k)`` is the one extra round after the final check: critical findings only, on the final renders.

Why: §8 of M11; §1.4 of M12 (real03 run 3: 12 of 35 rooms reached, 5 of 78 edits accepted, 53 rejections aimed at
locked or unbuilt pieces, no plan, no memory, 120 calls per round, half of them reads).

How: every event goes to ``AgentLog`` (§9; M12 adds ``plan``, ``dry_run`` and ``round`` events) and the log, the
memory and ``orchestrator/metrics.json`` (``metrics.write``) are saved after every round; the model (``MockModel``),
the critics, the re-run function, the other tracks' functions and the clock are injected in the CPU tests.
Deterministic for ``workers=1``; with parallel sessions only the interleaving of different rooms' edits in
``overrides.json`` depends on timing (each room's own sequence does not).
"""
from __future__ import annotations

import json
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

from wenart.agent import brief as BR
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import memory as MEM
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.agent.model import MAX_IMAGES, ModelError, user_message

STAGE_ORDER = ("pipeline_final", "layout", "refit", "build", "polish")
MAX_ROUNDS = 4
MAX_CALLS_PER_ROOM = 12         # tool calls of one room session (reads included; dry_run counted, it is cheap)
MAX_TRIES = 3
WORKERS = 4                     # parallel room sessions (G1: 167 tokens/s at 4 streams vs 46 at 1)
ROUND_CAP_S = 15 * 60.0         # no new room session after this many seconds of the round's planner part
MARGIN_S = 20 * 60.0            # stop at least 20 min before the deadline (the user's rule, §8)
STOPS = {
    "no_finding": "no critical or major finding left",
    "no_fixable": "no fixable critical or major finding left (the rest is locked, not built or needs review)",
    "no_edit": "no edit accepted in this round",
    "max_rounds": "max rounds reached",
    "deadline": "time budget: the final stages need the time left before the deadline - 20 min",
    "rerun_failed": "the re-run of the changed stages failed",
    "model_error": "the agent model did not answer",
}
BUILDING = "building"


def route(accepted: list[dict]) -> Optional[str]:
    """The earliest stage of ``STAGE_ORDER`` the accepted edits re-run from; record-only edits (``applied:
    false``: ``correct_geometry``, ``report_library_gap``) re-run nothing, so a round with only those gives None."""
    stages = [a["result"].get("rerun_from") for a in accepted
              if a["result"].get("rerun_from") and a["result"].get("applied", True) is not False]
    stages = [s for s in stages if s in STAGE_ORDER]
    return min(stages, key=STAGE_ORDER.index) if stages else None


def changed_views(cameras: list[dict], accepted: list[dict], room_of: Callable[[str], Optional[str]]) -> list[str]:
    """The views whose scene the accepted edits change: the views of every room a furniture edit touched, every
    camera edit's view, every exterior view after an exterior edit, every view after a material or level edit."""
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
        elif tool == "set_material" or tool in OV.LEVEL_TOOLS:
            everything = True
        elif tool == "set_lighting" and args.get("room_id"):
            rooms.add(args["room_id"])
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


# --------------------------------------------------------------------------
# Plans (§5.4 "plan first")
# --------------------------------------------------------------------------

def default_checklist(brief: dict, wanted=("critical", "major")) -> list[dict]:
    """One step per fixable finding of the wanted severities: its first tool on its target (the room for a finding
    without a piece target)."""
    room_id = brief["room"]["id"]
    steps = []
    for f in (brief.get("findings") or {}).get("fixable") or []:
        if f.get("severity") not in wanted:
            continue
        steps.append({"finding_ids": [f["id"]], "tool": f["tools"][0], "target": f.get("target") or room_id,
                      "why": str(f.get("message") or f.get("check"))[:300]})
    return steps


def check_plan(plan: Optional[dict], brief: dict, offered: list[str]) -> tuple[list[dict], list[str]]:
    """``(checked steps, problems)``: a step stays when its tool is offered, its findings are fixable, its target is
    built and the target allows the tool (``brief.PIECE_TOOLS``: the piece's ``allowed``; group tools: a group or a
    piece of one; room tools: the room) and the tool is one of the tools of its findings. Program choices must name
    a group of the program and one of its options."""
    room_id = brief["room"]["id"]
    if not isinstance(plan, dict):
        return [], ["no valid plan: the default checklist (each fixable finding with its first tool) is used"]
    problems: list[str] = []
    fixable = {f["id"]: f for f in (brief.get("findings") or {}).get("fixable") or []}
    not_yours = {f["id"] for f in (brief.get("findings") or {}).get("not_yours") or []}
    pieces = {p["id"]: p for p in brief.get("pieces") or []}
    unbuilt = {p["id"] for p in brief.get("not_built") or []}
    groups = {g.get("group_id") for g in brief.get("groups") or []}
    spans = {s.get("id") for s in brief.get("free_wall_spans") or []}
    if plan.get("room_id") not in (room_id, None):
        problems.append(f"the plan names room {plan.get('room_id')!r}, the session is {room_id}")
    program = {g.get("group_id"): g for g in (brief.get("program") or {}).get("groups") or []}
    for ch in (plan.get("program") or {}).get("choices") or []:
        g = program.get(ch.get("group_id"))
        if g is None:
            problems.append(f"program choice {ch.get('group_id')}: no such group in the program")
        elif g.get("options") and ch.get("option") not in g.get("options"):
            problems.append(f"program choice {ch.get('group_id')}: {ch.get('option')!r} is not one of {g['options']}")
    steps = []
    for i, s in enumerate(plan.get("steps") or []):
        tool, target, ids = s.get("tool"), s.get("target"), list(s.get("finding_ids") or [])
        why = None
        bad_ids = [f for f in ids if f not in fixable]
        if tool not in offered:
            why = f"tool {tool} is not offered"
        elif bad_ids:
            why = ", ".join(f"{f} is {'not yours' if f in not_yours else 'not a fixable finding'}" for f in bad_ids)
        elif target in unbuilt:
            why = f"{target} is not built"
        elif tool in BR.PIECE_TOOLS:
            p = pieces.get(target)
            a = ((p or {}).get("allowed") or {}).get(tool) or {}
            if p is None:
                why = f"{tool} needs a built piece of the room as target, not {target!r}"
            elif not a.get("allowed"):
                why = f"{target} does not allow {tool}: {a.get('why') or 'locked'}"
        elif tool in BR.GROUP_TOOLS:
            if target not in groups and not (pieces.get(target) or {}).get("group") and target not in spans \
                    and groups:
                why = f"{tool} needs a group id of the brief, not {target!r}"
        if why is None and ids:
            tools_of = {t for f in ids for t in fixable[f].get("tools") or []}
            if tool not in tools_of and tool not in ("dry_run",):
                why = f"{tool} does not fix {', '.join(ids)} (its tools: {', '.join(sorted(tools_of))})"
        if why:
            problems.append(f"step {i + 1} ({tool} on {target}): {why}")
        else:
            steps.append(s)
    return steps, problems


def step_done(step: dict, tool: str, args: dict, result: dict) -> bool:
    """An accepted edit ``tool(args)`` completes a checklist step with the same tool on the same target."""
    if step.get("tool") != tool:
        return False
    target = step.get("target")
    return target in {args.get(k) for k in ("piece_id", "room_id", "group_id", "view_id", "span_id")} or \
        target in (result.get("changed_ids") or [])


class CallBudget:
    """The round's optional call cap (``max_calls``) shared by the parallel sessions."""

    def __init__(self, cap: Optional[int]):
        self.left = None if cap is None else int(cap)
        self.lock = threading.Lock()

    def take(self) -> bool:
        with self.lock:
            if self.left is None:
                return True
            if self.left <= 0:
                return False
            self.left -= 1
            return True

    def empty(self) -> bool:
        with self.lock:
            return self.left is not None and self.left <= 0


class AgentLoop:
    """Rounds, router, stop rules and the log of one project (module docstring)."""

    def __init__(self, project_out, model, *, rerun: Optional[Callable] = None, clock: Callable[[], float] = time.time,
                 deadline: Optional[float] = None, final_estimate=0.0, margin_s: float = MARGIN_S,
                 max_rounds: int = MAX_ROUNDS, max_calls: Optional[int] = None, max_tries: int = MAX_TRIES,
                 code_critic: Optional[Callable] = None, vision_critic: Optional[Callable] = None, vision: bool = True,
                 registry: Optional[TL.Registry] = None, apply_edit: Optional[Callable] = None, validators=None,
                 plausibility=None, catalog_loader: Optional[Callable] = None, out: Callable[[str], None] = print,
                 log: Optional[LG.AgentLog] = None, preview_dir: str = TL.PREVIEW_DIR, project: str = "",
                 workers: int = WORKERS, round_cap_s: float = ROUND_CAP_S, calls_per_room: int = MAX_CALLS_PER_ROOM,
                 plan_first: bool = True, brief_fns: Optional[dict] = None, level_edit: Optional[Callable] = None,
                 level_checks: Optional[Callable] = None, sync: Optional[Callable] = None,
                 groups_fn: Optional[Callable] = None, scene_dir=None):
        self.project_out = Path(project_out)
        self.model = model
        self.rerun = rerun
        self.clock = clock
        self.deadline = deadline
        self.final_estimate = final_estimate
        self.margin_s = float(margin_s)
        self.max_rounds = int(max_rounds)
        self.max_calls = None if max_calls is None else int(max_calls)
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
        self.workers = max(1, int(workers))
        self.round_cap_s = float(round_cap_s)
        self.calls_per_room = int(calls_per_room)
        self.plan_first = bool(plan_first)
        self.brief_fns = dict(brief_fns or {})
        self.level_edit = level_edit
        self.level_checks = level_checks
        self.sync = sync
        self.groups_fn = groups_fn
        self.scene_dir = Path(scene_dir) if scene_dir is not None else self.project_out / CC.SCENE_CHECKS_DIR
        self.log = log or LG.AgentLog(self.project_out, project or self.project_out.name,
                                      getattr(model, "model", ""), getattr(model, "revision", ""), clock=clock)
        if hasattr(model, "on_call") and model.on_call is None:
            model.on_call = self.log.call
        self.overrides = OV.Overrides(self.project_out, project or self.project_out.name)
        self.memory = MEM.Memory(self.project_out)
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
                                   catalog_loader=self.catalog_loader, max_tries=self.max_tries, memory=self.memory,
                                   level_edit=self.level_edit, level_checks=self.level_checks, sync=self.sync,
                                   brief_fns=self.brief_fns)

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
        if self.groups_fn is not None:
            kwargs["groups_fn"] = self.groups_fn
        if self.level_checks is not None:
            kwargs["levels_fn"] = self.level_checks
        return CC.run(building, ctx.scene, manifest, scene_dir=self.scene_dir, **kwargs)

    def critique_keys(self, ctx: TL.ToolContext, building: dict) -> list[tuple[str, str]]:
        """``[(kind, id)]`` (M12: only where an image adds something): rooms with at least one preview of their own
        views, exterior views with a preview."""
        keys = []
        cams = ctx.cameras()
        for r in building.get("rooms") or []:
            rid = r.get("id")
            if any(c.get("room_id") == rid and ctx.preview_path(c["name"]) is not None for c in cams):
                keys.append(("room", rid))
        for c in cams:
            kind = c.get("kind") or ("exterior" if not c.get("room_id") else "interior")
            if kind == "exterior" and ctx.preview_path(c["name"]) is not None:
                keys.append(("view", c["name"]))
        return keys

    def run_vision_critic(self, ctx: TL.ToolContext, code: dict, round_no: int) -> dict:
        """Kept and dropped vision findings of every room / exterior view with a render (re-asked only where the
        scene changed; the others keep their last answer)."""
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
                    res = CV.critique_room(self.model, building, key, previews=previews, topdown=None,
                                           plan_crop=ctx.plan_crop_path(key), code=code, call_id=call_id, looks=True)
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
                 label: Optional[str], findings: list[dict], room_id: Optional[str] = None) -> None:
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
                       note=result.get("message") or None, room_id=room_id)

    # ----- sessions: which rooms, in which order ------------------------------------------------------

    def building_brief(self, ctx: TL.ToolContext, findings: list[dict]) -> dict:
        """The brief of the building session (findings without a room: exterior, levels, exterior views)."""
        fixable, not_yours = BR.classify(findings, ctx.building, None, {}, {}, {})
        return {"room": {"id": BUILDING, "label": "the building and its site", "type": None},
                "findings": {"fixable": fixable, "not_yours": not_yours},
                "memory": self.memory.summary(BUILDING), "pieces": [], "not_built": [], "groups": [],
                "free_wall_spans": [], "candidates": [], "program": {"groups": []}}

    def sessions_for(self, ctx: TL.ToolContext, found: list[dict], wanted: tuple) -> tuple[list[dict], dict]:
        """``(sessions, coverage)``: one session per room (and one for the building) with a fixable finding of the
        wanted severities, in the order of the module docstring; ``coverage`` lists the rooms with fixable findings
        and how many open findings are not fixable."""
        open_ = [f for f in found if f["severity"] in wanted]
        rooms = {r.get("id"): r for r in ctx.building.get("rooms") or []}
        piece_room = {p.get("id"): p.get("room_id") for p in ctx.building.get("furniture") or []}
        by_room: dict = {}
        for f in found:
            rid = f.get("room_id") or piece_room.get(f.get("target")) or (f.get("target") if f.get("target") in rooms
                                                                         else None)
            by_room.setdefault(rid if rid in rooms else BUILDING, []).append(f)
        wanted_rooms = {(f.get("room_id") or piece_room.get(f.get("target")) or
                         (f.get("target") if f.get("target") in rooms else None)) for f in open_}
        sessions, unfixable = [], 0
        for rid, fs in by_room.items():
            if (rid if rid != BUILDING else None) not in wanted_rooms:
                continue
            ctx.findings = found
            brief = self.building_brief(ctx, fs) if rid == BUILDING else ctx.brief(rid)
            fixable = [f for f in (brief.get("findings") or {}).get("fixable") or [] if f["severity"] in wanted]
            unfixable += sum(1 for f in (brief.get("findings") or {}).get("not_yours") or []
                             if f.get("severity") in wanted)
            if not fixable:
                continue
            area = float((rooms.get(rid) or {}).get("area_computed") or 0.0) if rid != BUILDING else 1.0
            sessions.append({"room_id": rid, "brief": brief, "fixable": fixable,
                             "weight": BR.fixable_weight(fixable, area), "visits": self.memory.visits(rid)})
        sessions.sort(key=lambda s: (s["visits"], -s["weight"], s["room_id"]))
        ctx.findings = found
        return sessions, {"fixable_rooms": [s["room_id"] for s in sessions], "unfixable_open": unfixable}

    def session_tools(self, brief: dict) -> list[str]:
        """The tools offered to one session (``tools.PLANNER_TOOLS`` cut to what the session can use)."""
        named = {t for f in (brief.get("findings") or {}).get("fixable") or [] for t in f.get("tools") or []}
        if brief["room"]["id"] == BUILDING:
            pool = TL.PLANNER_READS + TL.PLANNER_BUILDING + tuple(sorted(named)) + TL.PLANNER_CONTROL
        else:
            extra = tuple(t for t in sorted(named) if t not in TL.PLANNER_ROOM_EDITS)
            pool = TL.PLANNER_READS + TL.PLANNER_ROOM_EDITS + extra + TL.PLANNER_CONTROL
        out: list[str] = []
        for t in pool:
            if t in self.registry.tools and t not in out:
                out.append(t)
        return out

    # ----- planner -------------------------------------------------------------------------------

    def plan(self, ctx: TL.ToolContext, round_no: int, sessions: list[dict], critical_only: bool = False) -> dict:
        """The planner part of one round: the sessions in their order, ``workers`` at a time; a session starts only
        before the round's time cap and while the time budget allows (the first one always). ``{"calls",
        "schema_errors", "replies", "error", "sessions", "rooms", "plans_ok"}``."""
        total = {"calls": 0, "replies": 0, "error": None, "sessions": 0, "rooms": [], "plans_ok": 0,
                 "steps_done": 0, "steps": 0}
        budget = CallBudget(self.max_calls)
        cap_at = self.clock() + self.round_cap_s
        lock = threading.Lock()
        started = {"n": 0}

        def one(index: int, item: dict) -> Optional[dict]:
            with lock:
                if started["n"] and (self.clock() > cap_at or not self.time_ok() or budget.empty()):
                    return None
                started["n"] += 1
            return self.plan_session(ctx, round_no, item, budget, critical_only, session=index, cap_at=cap_at)

        if self.workers <= 1:
            results = [one(i, s) for i, s in enumerate(sessions)]
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                futures = [ex.submit(one, i, s) for i, s in enumerate(sessions)]
                results = [f.result() for f in futures]
        for res in results:
            if res is None:
                continue
            total["sessions"] += 1
            total["rooms"].append(res["room_id"])
            for k in ("calls", "replies", "steps_done", "steps"):
                total[k] += res[k]
            total["plans_ok"] += 1 if res["plan_ok"] else 0
            if res["error"]:
                total["error"] = res["error"]
        return dict(total, schema_errors=ctx.schema_errors)

    def make_plan(self, ctx: TL.ToolContext, round_no: int, brief: dict, offered: list[str], critical_only: bool,
                  tag: str) -> tuple[list[dict], list[str], bool]:
        """The plan call (``prompts.PLAN_SCHEMA``), checked against the brief: ``(checklist, problems, plan_ok)``."""
        wanted = ("critical",) if critical_only else ("critical", "major")
        plan = None
        if self.plan_first:
            messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                        {"role": "user", "content": P.plan_prompt(round_no, brief, offered, critical_only)}]
            try:
                reply = self.model.structured(messages, P.PLAN_SCHEMA, call_id=f"{tag}-plan", name="plan",
                                              kind="plan", thinking=getattr(self.model, "planner_thinking", False))
                plan = reply.data
            except ModelError:
                plan = None
        steps, problems = check_plan(plan, brief, offered)
        plan_ok = plan is not None and bool(steps)
        if not steps:
            steps = default_checklist(brief, wanted)
        room_id = brief["room"]["id"]
        self.memory.add_plan(room_id, round_no, plan, plan_ok, problems)
        self.log.event("plan", round_no, room_id=room_id, call_id=f"{tag}-plan", status="ok" if plan_ok else
                       "default", counts={"steps": len(steps), "problems": len(problems)},
                       note="; ".join(problems)[:600] or None, model=self.log.model, revision=self.log.revision,
                       evidence={"steps": [{k: s.get(k) for k in ("tool", "target", "finding_ids")} for s in steps]})
        return steps, problems, plan_ok

    def plan_session(self, ctx: TL.ToolContext, round_no: int, item: dict, budget: CallBudget,
                     critical_only: bool = False, session: int = 0, cap_at: Optional[float] = None) -> dict:
        """One room session: the plan, then the tools on the checked checklist (module docstring)."""
        brief = item["brief"]
        room_id = item["room_id"]
        state = ctx.begin_session(room_id)
        tag = f"r{round_no}-s{session + 1}" if session else f"r{round_no}"
        t0 = self.clock()
        self.memory.visit(room_id, round_no)
        offered = self.session_tools(brief)
        checklist, problems, plan_ok = self.make_plan(ctx, round_no, brief, offered, critical_only, tag)
        findings = item["fixable"] + [f for f in ctx.findings if f.get("room_id") == room_id]
        messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                    {"role": "user", "content": P.session_task(round_no, brief, checklist, problems,
                                                               self.calls_per_room, critical_only)}]
        specs = self.registry.specs(offered)
        calls = replies = 0
        error = None
        done = [False] * len(checklist)
        try:
            while calls < self.calls_per_room and state.finished is None and not all(done or [False]) \
                    and not budget.empty():
                if cap_at is not None and replies and self.clock() > cap_at:
                    break
                if replies and not self.time_ok():
                    break
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
                edited: set = set()
                for i, tc in enumerate(reply.tool_calls):
                    call_id = f"{tag}-p{replies}-t{i + 1}"
                    tool = self.registry.tools.get(tc.name)
                    is_edit = tool is not None and tool.kind in TL.EDIT_KINDS
                    target = TL._target(tc.name, tc.parsed or {}) if is_edit else None
                    if is_edit and target in edited:
                        result = {"error": f"one edit per piece at a time: look at the result of your edit of "
                                           f"{target} before you send the next one"}
                    elif calls >= self.calls_per_room or not budget.take():
                        result = {"error": f"the budget of {self.calls_per_room} tool calls for this room is used up"}
                    else:
                        calls += 1
                        label = TL.label_for(tc.name, ctx, tc.parsed or {}) if is_edit else None
                        result = self.registry.call(ctx, tc.name, tc.parsed, tc.error)
                        if is_edit:
                            edited.add(target)
                            self.log_edit(round_no, call_id, tc.name, tc.parsed, result, label, findings, room_id)
                            if result.get("accepted"):
                                for k, step in enumerate(checklist):
                                    if not done[k] and step_done(step, tc.name, tc.parsed or {}, result):
                                        done[k] = True
                    messages.append({"role": "tool", "tool_call_id": tc.id,
                                     "content": json.dumps(result, ensure_ascii=False, default=str)[:12000]})
                if state.pending_images:
                    shown = state.pending_images[-MAX_IMAGES:]
                    labels = [f"Image from a tool: {Path(p).name}" for p in shown]
                    messages.append(user_message("The images the tools returned, newest last.", shown, labels))
                    state.pending_images.clear()
        finally:
            open_steps = [f"{s['tool']} on {s['target']}: {s.get('why', '')}"[:200]
                          for s, d in zip(checklist, done) if not d]
            open_steps += [str(x) for x in ((state.finished or {}).get("open_findings") or [])]
            self.memory.set_open(room_id, open_steps)
            ctx.end_session()
        return {"room_id": room_id, "calls": calls, "replies": replies, "error": error, "plan_ok": plan_ok,
                "steps": len(checklist), "steps_done": sum(done), "seconds": round(self.clock() - t0, 2)}

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
        ctx.findings = found
        wanted = ("critical",) if critical_only else ("critical", "major")
        open_ = [f for f in found if f["severity"] in wanted]
        summary = {"round": round_no, "final": final, "findings": {s: sum(1 for f in found if f["severity"] == s)
                                                                    for s in P.SEVERITIES},
                   "dropped": len(vision.get("dropped") or []), "accepted": 0, "rejected": 0, "calls": 0,
                   "schema_errors": 0, "rerun_from": None, "views": [], "stop": None,
                   "rooms_code": len(ctx.building.get("rooms") or []),
                   "rooms_vision": sorted({c.get("target") for c in vision.get("checks") or []
                                           if c.get("target") in {r.get("id") for r in ctx.building.get("rooms")
                                                                   or []}}),
                   "rooms_planner": [], "rooms_fixable": [], "unfixable_open": 0, "sessions": 0, "plans_ok": 0,
                   "refused_repeats": 0, "dry_runs": 0}
        self.rounds.append(summary)
        if not open_:
            summary["stop"] = "no_finding"
            return self._end_round(summary, t0)
        sessions, coverage = self.sessions_for(ctx, found, wanted)
        summary.update(rooms_fixable=coverage["fixable_rooms"], unfixable_open=coverage["unfixable_open"])
        if not sessions:
            summary["stop"] = "no_fixable"
            return self._end_round(summary, t0)
        plan = self.plan(ctx, round_no, sessions, critical_only)
        summary.update(calls=plan["calls"], schema_errors=plan["schema_errors"], accepted=len(ctx.accepted),
                       rejected=len(ctx.rejected), rooms_planner=plan["rooms"], sessions=plan["sessions"],
                       plans_ok=plan["plans_ok"], refused_repeats=ctx.refused_repeats, dry_runs=ctx.dry_runs)
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
        self.log.event("round", summary["round"], status=summary["stop"] or "done", seconds=summary["seconds"],
                       counts={k: summary[k] for k in ("accepted", "rejected", "calls", "schema_errors", "dropped",
                                                       "rooms_code", "sessions", "plans_ok", "refused_repeats",
                                                       "dry_runs", "unfixable_open")},
                       evidence={"findings": summary["findings"], "rooms_vision": summary["rooms_vision"],
                                 "rooms_planner": summary["rooms_planner"],
                                 "rooms_fixable": summary["rooms_fixable"], "final": summary["final"]})
        self.save()
        self.out(f"agent round {summary['round']}: findings {summary['findings']}, accepted {summary['accepted']}, "
                 f"rejected {summary['rejected']}, rooms {len(summary['rooms_planner'])}/"
                 f"{len(summary['rooms_fixable'])} fixable, re-run {summary['rerun_from'] or '-'} "
                 f"({len(summary['views'])} views)" + (f", stop: {STOPS[summary['stop']]}" if summary["stop"] else ""))
        return summary

    def save(self, final: bool = False) -> None:
        self.log.save(final=final)
        self.memory.save()
        try:
            from wenart.agent import metrics as MX
            MX.write(self.project_out)
        except Exception as exc:  # noqa: BLE001 - metrics never stop the loop
            self.out(f"agent metrics not written: {type(exc).__name__}: {exc}")

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
        self.save()
        return self.summary()

    def final_round(self, round_no: int) -> dict:
        """The extra round after the final check: critical findings only, on the final renders (§8 "final")."""
        if not self.time_ok():
            self.log.event("stop", round_no, reason=STOPS["deadline"], status="deadline",
                           note="final round for critical findings not started")
            self.save(final=True)
            return {"round": round_no, "stop": "deadline", "accepted": 0}
        res = self.round(round_no, critical_only=True, final=True)
        self.log.event("stop", round_no, reason="final round for critical findings done", status=res["stop"] or "done")
        self.save(final=True)
        return res

    def summary(self) -> dict:
        return {"rounds": list(self.rounds), "stop": self.stop,
                "accepted": sum(r["accepted"] for r in self.rounds),
                "rejected": sum(r["rejected"] for r in self.rounds), "log": str(self.log.dir / LG.LOG_JSON)}
