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

Milestone 13 (docs/milestone13.md §1.5, §3.0 K4, §13.2; track T4):

- acceptance by finding removal: after the validator (``edit_ops.apply_edit`` or an override check) accepts an
  edit, the loop re-runs the code critic on the changed building (``after_findings``, the dry re-check) and
  ``accept_edit`` (``causes.accept_edit``, pure) accepts the edit only when the finding it targets
  (``tools.target_findings``: the checklist step's finding ids, else the finding on the edit's target) is gone and no
  new critical finding appeared; the old "score must not drop" rule stays as a second condition. A rejected edit is
  logged with both finding lists (``evidence.acceptance``); the metric ``findings_removed`` (per round in the
  ``round`` event, the total in the ``stop`` event and ``metrics.json``) replaces "edits accepted" as the success
  number. Findings the dry re-check cannot measure (the scene checks of the build, the view checks, looks, vision)
  count as gone on the targets the edit changed and are re-measured by the next round (the log says so);
- tools by cause: ``tools_for_finding`` (``causes.tools_for_finding``) replaces the check-id mapping; a finding
  without a tool for its cause is "not yours", the vision critic's findings included (they are dropped with the
  reason in the log); building-wide tools (``causes.is_building_wide``: roof, site, sun, materials, geometry,
  levels, terrain, exterior cameras) are offered to the building session only and refused from a room session;
- round 4 (before pod P3's second attempt): the code critic's ``lighting_dark`` findings (a view above the +3 EV cap)
  are fixed by ``set_lighting`` on the view's room and count as gone on every view of that room after it (they are
  re-measured by the next render, ``NOT_REMEASURED``); the acceptance gets the pieces the edit took out of the scene
  (``causes.removed_pieces``) and refuses an edit whose dry re-check shows a new room-set finding (G9 / G10) for
  a fixture it removed;
- ``MAX_ROUNDS`` = 3 (was 6 on the real04 pod, 4 in the code): real04 removed 20 findings in 6 rounds, 136 of the
  161 round-1 findings were still there after round 6, and a round that removes no finding stops the loop anyway
  (``no_edit``); three rounds bound the GPU time to what the measured removals justify (§1.5 T9: $0.133 per removed
  finding).

Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 "Attempt 2"):

- context budget: before every planner call ``plan_session`` estimates the NEXT prompt (``ContextBudget``: the last
  answer's ``prompt_tokens`` plus the text and images added since; before the first answer, the whole text) against
  the model's ``max_model_len`` (the served key's ``--max-model-len``) minus ``CONTEXT_MARGIN_TOKENS``; when the
  prompt plus the answer budget do not fit, the tool results older than the last ``KEEP_REPLIES`` = 2 replies become
  one-line stubs, then those older than the latest reply, then the latest reply's results are cut to
  ``LATEST_RESULT_CHARS``; the answer budget is ``min(model.max_tokens, room left)``, never below
  ``MIN_REPLY_TOKENS`` (part 2: ``model.max_tokens`` is ``DEFAULT_MAX_TOKENS``, 4096). A tool result enters the
  conversation cut to ``TOOL_RESULT_CHARS`` = 6,000 characters (was 12,000). When the server still refuses the
  prompt (``ContextFullError``), everything but the latest reply is cut and the call is sent once more; a second
  refusal ends the session like a used-up budget (``context_full``, no error). The round stops ``context_full``
  when a session ended so and no edit was accepted; ``model_error`` stays for the other model errors (timeout, 5xx,
  no connection);
- measured, not predicted: the loop's printed line, the stop event and ``summary()`` report the findings the next
  round's critics measured gone (``metrics.findings_removed_metrics``); the dry re-checks' count is labelled
  "predicted" (``findings_removed_predicted``); the acceptance rule is unchanged;
- a decor piece (``building["decor"]``) belongs to its room in ``sessions_for`` (and in the code critic); an X2 on a
  decor piece has the cause ``decor_under_roof`` (no agent tool edits decor) and is logged with ``report_to:
  decor``, so the building session is not sent to fix it (P3: 4 rounds of "relayout_room on building");
- every finding event carries its ``cause``; a finding no tool fixes carries ``not_yours`` (the reason).

Why: in P3 the building session's prompt grew 6,866 -> 17,606 -> 19,745 -> 22,294 -> >=28,673 tokens with its tool
results, the 5th call passed the 32,768-token context, and the round stopped "the agent model did not answer"
although the model had answered 4 times (the same overflow ended one session in each of rounds 1-3).

Fix round after P3, part 2 (17 Oct 2026; docs/milestone13.md §14.9): the planner's answer budget is the model's
``max_tokens``, ``model.DEFAULT_MAX_TOKENS`` (4096) with thinking on or off (part 1 asked for a fixed 1536 with
thinking off), and 4096 for a model without the attribute too (was 1,024): ``ContextBudget`` cuts the old tool
results until the next prompt plus 4096 tokens fit and asks for ``min(4096, room left)``, never below
``MIN_REPLY_TOKENS``. Why: the M12 real04 log has valid planner answers of 2,740 and 1,604 tokens (r3-s4-p6,
r3-s4-p3) whose tool call comes after the prose; cut at 1,536 (``finish_reason`` "length") the call is lost and the
session ends at ``if not reply.tool_calls``. The runaway answers are stopped by the request's ``repetition_detection``
and the context budget; a "length" stop is still logged and counted (``metrics.finish_reasons``).

Fix round after P4a (17 Oct 2026; pod P4a, real02 with the M11 cameras replayed):

- a stale built box: the critical X2 "pokes through the roof" is measured on the round's scene manifest
  (``metrics.source`` ``scene_manifest``, ``MANIFEST_SOURCE``), which no edit changes; on a target the edit changed
  ``after_findings`` leaves it out (the next build re-measures it). The major X2 of the same key, re-measured on the
  building after the edit (``build.pieces_above_ceiling``), keeps the acceptance strict: a piece still under the slope
  is still rejected. Why: P4a rejected every remove and move of the bookshelf f_L1_058 (top 5.17 m from the stale box)
  for 3 rounds; that critical was the only reason the final round ran;
- an S2 WALL cut on a moved piece is predicted, not dropped (``s2_wall_kept``): the cut after the edit is the
  measured cut plus the change of the footprint's depth in that wall (``scene_checks.wall_boxes``); when the
  prediction stays over the cut's tolerance, the finding stays (so the edit that targets it is rejected). Pair cuts,
  buried kitchen members and edits that keep the footprint (``swap_model``) still count as gone and are re-measured
  by the next round. Why: 10 of 10 S2 wall moves accepted in P3 and P4a were still over tolerance when measured (a
  move along the wall cannot shrink the cut);
- plans: the plan event's status says why the default checklist ran: ``ok``, ``empty`` (a valid plan without
  steps), ``refused`` (every step refused by ``check_plan``) or ``default`` (no valid plan); the planner's ``skip``
  list and program choices are logged in the event's evidence and stored in the memory. The default checklist still
  runs for the three (no behaviour change: the skip lists are logged so a later pod can check them);
- ``set_lighting`` steps come first in every checklist (``lighting_first``): they do not depend on the furniture and
  code predicts them. The final round (critical findings only) also takes a major ``lighting_dark`` view one
  ``set_lighting`` clears (``FINAL_ROUND_LIGHTING``) when a re-render follows. Why: P4a's salon set_lighting was the
  last of 14 default steps and the session's 12 calls ran out before it; the final salon views stayed 0.42 and
  0.07 stops over the cap;
- a step whose edit the memory refused twice in the session is closed (``tools``: the refusal counts as a try and the
  result says ``step_closed``); the session ends when every step is done or closed. Why: P4a's r1-s19 sent the same
  refused move 7 times, 7 of its 12 calls;
- a vision finding about a light fixture (``causes.light_fixture``) stays in the round's list as a reported finding
  (``report_to: lighting``) instead of being dropped as "no tool";
- after a re-run, every accepted ``set_camera`` / ``add_camera`` of the round is checked against the rebuilt scene
  manifest (``camera_effects``): a view that is not at the override's pose, or has two cameras of its name, is logged
  as a ``camera_effect`` check with status ``no_effect``. Why: P4a's three accepted set_camera ext_6 edits changed
  nothing (a second ext_6 was added and Blender renamed it ext_6.001).

Fix round after P4b (17 Oct 2026; pod P4b, real03, the review of the P4a fix round and the lead's decisions of the
same day):

- S2 wall cuts (``s2_wall_kept``): the footprint's depth in the wall is exact (``footprint_wall_depth``; the 7 x 7
  grid missed the wall's axis, so real02's f_L1_024 moved 0.05 m INTO w_L1_006 was predicted 0.0016 m and accepted);
  chained edits of one round start from the depth the earlier edit predicted; a predicted cut below 0.03 m is gone
  (it would be a minor within-tolerance finding); an edit that keeps the footprint (``swap_model``) keeps the cut,
  less what another model's depth may change (``swap_depth_slack``; P4b: 4 of 5 accepted swaps for an S2 still had
  it);
- decision 1: a camera-placement finding (X6, V1) on a camera replayed from the baseline (set 1) is report-only
  (``causes.mark_replayed`` on the round's code and vision findings: cause ``replayed_camera``, reported to the
  cameras); the tools refuse to set or remove such a camera;
- ``set_exterior``: the dry re-check's critic reads the round's scene manifest with the override's sun
  (``scene_after``), so the code's X7 measures the new sun; a vision finding whose cause the override does not touch
  stays (``after_findings(override=...)``, ``exterior_kept``). Why: P4b accepted a ground and a 55 degree sun edit
  for a vision X4 "no path", and X7 "sun 55 degrees" came in round 4;
- decision 6: ``FINAL_ROUND_LIGHTING`` is off (the final round stays critical-only; the mechanism stays);
- the exterior critic gets the round's scene manifest (``critic_vision.critique_exterior(scene=...)``: the camera's
  measured eye height and role); a checklist step closed by a tool says why (``closed_why``: the memory refused its
  edit twice, or the code's fix_fixture search found no valid spot).

Pass before P5 (17 Oct 2026; the review of the fix round after P4b): a ``set_exterior`` keeps the vision finding it
targets with the reason (``exterior_kept``: "the edit does not change what the finding is about") whatever its
target: ``tools.changed_targets`` leaves an untouched target out of ``changed``, so the finding was kept through the
"target not changed" branch without the reason, and the model was not told that a sun or ground edit cannot fix a
"no path" finding (``after_findings(targets=...)``; the other vision findings keep their message).

Fix round after P5 (22 Oct 2026; pod P5, real04, the review of its agent log):

- the dry re-check measures the fitted boxes the round's critic measured (``fitted_view``): ``AgentLoop.acceptance``
  gives every piece of the building after the edit that matches its piece in ``building_final.json`` (same id, type,
  footprint size, ``asset_pin`` and build flag; ``fit_key``) that piece's fitted ``asset`` record, and fits a built
  piece without a match (added, retyped, resized, re-pinned) with ``fit.fit_piece`` in the licence mode and style
  family of ``building_final.json`` (``dry_fit``, cached per piece state; a failed fit keeps the box it had; the
  working building's first fit has no style family). Only the dry re-check's copy
  changes; the validators, ``ctx.building`` and the overrides replay do not. A refit is a prediction (the refit's
  choice among equal models can differ) and the acceptance says so (``fitted``). Why: the working building
  (``building_agent.json``) carries no fitted asset for the decor stage's 54 pieces and the first, style-free fit for
  the rest, so the console table f_L1_049 measured 0.80 m in the dry re-check and 0.84 m (under a 0.82 m slope, X2) in
  the critic's: its X2 vanished after the first accepted edit of round 1, its remove_piece was rejected "no target
  finding" and refused by the memory after that, and the shoe cabinet f_L1_050 got a false X2 at its 1.00 m proxy
  height (fitted 0.44 m);
- an edit that removes the piece of its target finding and adds a piece of the same type in the same room
  (``causes.added_pieces``; ``edit["added"]``) keeps the finding when the dry re-check has the same check on the added
  piece (``causes.accept_edit``): P5's relayout_room "removed" X2:f_L1_049 by re-creating the console table at the same
  centre as f_L1_056, and round 4 measured X2:f_L1_056 at the same 0.84 / 0.82 m;
- a finding measured on the round's scene manifest (``manifest_measured``) is left out of ``code_after`` on every
  target an accepted edit of the round changed (``ctx.round_changed``, filled where a verdict is applied:
  ``tools.apply_verdict``), and, while the edit keeps the roof (``roof_kept``), whenever its key is not among the
  findings before the edit: the boxes are the round's and only a roof change can make one of them new. Why: after the
  accepted remove_piece f_L1_056 (seq 4681) its stale manifest box came back as "new critical finding X2:f_L1_056" in
  every later dry re-check and rejected 8 edits in four other rooms (plus 3 memory echoes and 9 dry runs). A roof
  override still meets every manifest box: a lower roof over an untouched piece or decor box is a new critical;
- the memory is scoped to the building and the code (``memory.Memory``; ``context`` refreshes the scope every round);
- a session ends after ``REFUSALS_END_SESSION`` = 2 edits in a row refused without validation (max tries, the memory,
  the code's fix_fixture search, a frozen camera) on targets this session had already been refused for; a
  ``max_tries`` refusal closes every checklist step on its target (``tools._too_many``). Why: P5's r2-s13 sent
  move_piece f_L1_024 six times after its max_tries refusal (about 17-20k prompt tokens each).

Why: §8 of M11; §1.4 of M12 (real03 run 3: 12 of 35 rooms reached, 5 of 78 edits accepted, 53 rejections aimed at
locked or unbuilt pieces, no plan, no memory, 120 calls per round, half of them reads).

How: every event goes to ``AgentLog`` (§9; M12 adds ``plan``, ``dry_run`` and ``round`` events) and the log, the
memory and ``orchestrator/metrics.json`` (``metrics.write``) are saved after every round; the model (``MockModel``),
the critics, the re-run function, the other tracks' functions and the clock are injected in the CPU tests.
Deterministic for ``workers=1``; with parallel sessions only the interleaving of different rooms' edits in
``overrides.json`` depends on timing (each room's own sequence does not).
"""
from __future__ import annotations

import copy
import json
import math
import re
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import memory as MEM
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.agent.causes import accept_edit, cause_of, findings_removed, tools_for_finding  # noqa: F401 (§13.2)
from wenart.agent.model import (DEFAULT_MAX_TOKENS, MAX_IMAGES, ContextFullError, ModelError, count_images,
                                 user_message)

STAGE_ORDER = ("pipeline_final", "layout", "refit", "build", "polish")
# Milestone 13: 3 rounds (module docstring): real04 removed 20 findings in 6 rounds and 84.5 % of the round-1
# findings were still there at the end; acceptance by finding removal makes a round without a removal the last one.
MAX_ROUNDS = 3
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
    # fix round after P3: a model error other than a full context (a full context is ``context_full``)
    "model_error": "the agent model did not answer (a timeout, a server error or no connection)",
    # fix round after P3: a session's prompt no longer fit the server's context, even after cutting old tool results
    "context_full": "a session's conversation no longer fit the agent model's context and no edit was accepted",
}
BUILDING = "building"
# Fix round after P3 (module docstring): the context budget of a planner session.
CONTEXT_MARGIN_TOKENS = 1024     # kept free under the server's --max-model-len (chat template, estimate error)
CHARS_PER_TOKEN_ADDED = 2.0      # text added since the last answer (P3's JSON tool results: about 2.3 per token)
CHARS_PER_TOKEN_REMOVED = 4.0    # text cut out: counted low, so a cut never looks bigger than it is
IMAGE_TOKENS = 1500              # an image added since the last answer (a 1280-px render is about 1,000 tokens)
TOOL_RESULT_CHARS = 6000         # a tool result as it enters the conversation (was 12,000)
TOOL_STUB_CHARS = 200            # what an old tool result keeps when the context is full
LATEST_RESULT_CHARS = 2000       # the latest reply's tool results when cutting the older ones was not enough
MIN_REPLY_TOKENS = 1024          # the planner's answer budget never goes below this
KEEP_REPLIES = 2                 # the tool results of the last 2 replies stay whole while the older ones are cut
STUB_NOTE = "[older tool result removed to fit the context; call the tool again if you need it]"
CONTEXT_CHECK = "context_budget"  # the ``check`` event of a session whose context was cut or full (tool field)
CUT_NOTE = "[cut to fit the context]"
# Fix round after P4a (module docstring): the final round also takes a major lighting_dark view one set_lighting clears.
# Fix round after P4b: off (decision 6 of 17 Oct 2026, the lead: FINAL_ROUND_LIGHTING stays off); the mechanism stays.
FINAL_ROUND_LIGHTING = False
CAMERA_EFFECT_CHECK = "camera_effect"   # the ``check`` event of an accepted camera edit checked after the re-run
# Fix round after P5 (module docstring): edits in a row refused without validation on already-refused targets that end
# a session, and the ``check`` event that says so.
REFUSALS_END_SESSION = 2
REFUSALS_CHECK = "session_refusals"


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


CAMERA_POSE_TOOLS = ("set_camera", "add_camera")


def camera_effects(scene_manifest: Optional[dict], accepted: list[dict]) -> list[dict]:
    """Fix round after P4a (module docstring): per accepted ``set_camera`` / ``add_camera`` (``[{tool, args}]``),
    whether the rebuilt scene manifest has exactly one camera of its view id, at the override's pose
    (``tools.same_pose``): ``[{view_id, status: ok | no_effect, cameras, note, override, poses}]``. Pure."""
    cams = [c for c in (scene_manifest or {}).get("cameras") or [] if isinstance(c, dict)]
    last: dict = {}                     # the last camera edit of each view counts (an earlier one was overridden)
    for a in accepted:
        if a.get("tool") in CAMERA_POSE_TOOLS:
            last.pop((a.get("args") or {}).get("view_id"), None)
            last[(a.get("args") or {}).get("view_id")] = a
    out = []
    for a in last.values():
        args = a.get("args") or {}
        vid = args.get("view_id")
        same = [c for c in cams if c.get("name") == vid]
        hit = [c for c in same if TL.same_pose(args, c)]
        if len(same) == 1 and hit:
            status, note = "ok", f"{vid} is rendered at the override's pose"
        elif not same:
            status, note = "no_effect", f"{vid} is not in the rebuilt scene manifest: the override had no effect"
        elif len(same) > 1:
            status, note = "no_effect", (f"{len(same)} cameras are named {vid} in the rebuilt scene manifest (Blender "
                                         f"renames the second one {vid}.001, the view {vid} keeps the first): the "
                                         f"override did not replace the camera")
        else:
            status, note = "no_effect", f"{vid} is rendered at another pose than the override's: it had no effect"
        out.append({"view_id": vid, "status": status, "cameras": len(same), "note": note,
                    "override": {k: args.get(k) for k in ("position", "target", "lens_mm") if args.get(k) is not None},
                    "poses": [{k: c.get(k) for k in ("position", "target", "lens_mm")} for c in same]})
    return out


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
# The context budget of a session (fix round after P3)
# --------------------------------------------------------------------------

def message_chars(message: dict) -> int:
    """The text characters of one message: its text content, its text parts and its tool calls' names and
    arguments (images are counted apart, ``count_images``)."""
    content = message.get("content")
    n = 0
    if isinstance(content, str):
        n += len(content)
    elif isinstance(content, list):
        n += sum(len(str(part.get("text") or "")) for part in content
                 if isinstance(part, dict) and part.get("type") == "text")
    for tc in message.get("tool_calls") or []:
        fn = (tc or {}).get("function") or {}
        n += len(str(fn.get("name") or "")) + len(str(fn.get("arguments") or ""))
    return n


def conversation_chars(messages: list) -> int:
    return sum(message_chars(m) for m in messages)


def tool_result_text(result) -> str:
    """A tool result as it enters the conversation: JSON, cut to ``TOOL_RESULT_CHARS`` with ``CUT_NOTE``."""
    text = json.dumps(result, ensure_ascii=False, default=str)
    if len(text) <= TOOL_RESULT_CHARS:
        return text
    return text[:TOOL_RESULT_CHARS] + f" ... {CUT_NOTE}"


def cut_tool_results(messages: list, keep_replies: int, cap: int, stub: bool) -> int:
    """Cut the tool results of every reply but the last ``keep_replies`` (a tool message belongs to the assistant
    message before it): to a one-line stub with ``STUB_NOTE``, the tool's name and its first ``cap`` characters
    (``stub``), else to its first ``cap`` characters with ``CUT_NOTE``. In place; the characters removed."""
    names: dict = {}
    reply_of: list = []
    replies = 0
    for m in messages:
        if m.get("role") == "assistant":
            replies += 1
            for tc in m.get("tool_calls") or []:
                names[str((tc or {}).get("id"))] = str(((tc or {}).get("function") or {}).get("name") or "tool")
        reply_of.append(replies)
    last_cut = replies - int(keep_replies)
    removed = 0
    for m, reply in zip(messages, reply_of):
        if m.get("role") != "tool" or reply > last_cut or not isinstance(m.get("content"), str):
            continue
        text = m["content"]
        if text.startswith(STUB_NOTE):
            continue
        if stub:
            new = f"{STUB_NOTE} {names.get(str(m.get('tool_call_id')), 'tool')}: {text[:cap]}"
        else:
            if text.endswith(CUT_NOTE) and len(text) <= cap + len(CUT_NOTE) + 8:
                continue
            new = f"{text[:cap]} ... {CUT_NOTE}"
        if len(new) < len(text):
            removed += len(text) - len(new)
            m["content"] = new
    return removed


class ContextBudget:
    """The context budget of one planner session (module docstring, fix round after P3). ``max_model_len`` None:
    no budget (a model without the attribute). ``want``: the answer budget the model asks for by default (part 2:
    ``DEFAULT_MAX_TOKENS``, 4096, the model's ``max_tokens``); ``fit`` asks for ``min(want, room left)``, never
    below ``MIN_REPLY_TOKENS``."""

    def __init__(self, max_model_len: Optional[int], want: int = DEFAULT_MAX_TOKENS, specs: Optional[list] = None):
        self.limit = int(max_model_len) - CONTEXT_MARGIN_TOKENS if max_model_len else None
        self.want = max(1, int(want))
        self.spec_chars = len(json.dumps(specs or [], ensure_ascii=False, default=str))
        self.last: Optional[dict] = None      # the last measured prompt: tokens, messages, characters
        self.cuts: list[dict] = []           # what was cut, for the log

    def measured(self, messages: list, prompt_tokens) -> None:
        """The server's prompt size for ``messages`` (an answer's ``usage.prompt_tokens``, or the size a context-full
        refusal names)."""
        try:
            tokens = int(prompt_tokens)
        except (TypeError, ValueError):
            return
        if tokens > 0:
            self.last = {"tokens": tokens, "n": len(messages), "chars": conversation_chars(messages)}

    def estimate(self, messages: list) -> int:
        """The NEXT prompt's tokens: the last measured prompt, plus the text (2 characters a token) and images added
        since, minus the text cut out of it since (4 characters a token); before any measure, the whole text and the
        tool specs at 2 characters a token plus the images."""
        if self.last is None:
            return int((conversation_chars(messages) + self.spec_chars) / CHARS_PER_TOKEN_ADDED
                       + count_images(messages) * IMAGE_TOKENS)
        n = self.last["n"]
        old, new = messages[:n], messages[n:]
        removed = max(0, self.last["chars"] - conversation_chars(old))
        return int(self.last["tokens"] + conversation_chars(new) / CHARS_PER_TOKEN_ADDED
                   + count_images(new) * IMAGE_TOKENS - removed / CHARS_PER_TOKEN_REMOVED)

    def fits(self, messages: list, tokens: Optional[int] = None) -> bool:
        return self.limit is None or self.estimate(messages) + int(tokens or self.want) <= self.limit

    def fit(self, messages: list, force: bool = False) -> int:
        """Cut old tool results until the next prompt plus the answer budget fit (module docstring); ``force`` (after
        a context-full refusal): cut everything but the latest reply first. Returns the ``max_tokens`` to ask for:
        ``min(want, room left)``, never below ``MIN_REPLY_TOKENS`` (nor above ``want``)."""
        if self.limit is None:
            return self.want
        steps = ((KEEP_REPLIES, TOOL_STUB_CHARS, True), (1, TOOL_STUB_CHARS, True), (0, LATEST_RESULT_CHARS, False))
        for i, (keep, cap, stub) in enumerate(steps):
            if not (force and i < 2) and self.fits(messages):
                break
            removed = cut_tool_results(messages, keep, cap, stub)
            if removed:
                self.cuts.append({"keep_replies": keep, "chars_removed": removed,
                                  "estimate": self.estimate(messages)})
        room = self.limit - self.estimate(messages)
        return int(min(self.want, max(room, min(self.want, MIN_REPLY_TOKENS))))


# --------------------------------------------------------------------------
# Plans (§5.4 "plan first")
# --------------------------------------------------------------------------

def offered_tools(registry, brief: dict) -> list[str]:
    """The tools offered to one room session (``tools.PLANNER_TOOLS`` cut to what the session can use): the reads,
    the room edits (or the building edits for the building session), the tools its fixable findings name, the
    control tools; only those of ``registry``. Also the bake-off's T5 (``bakeoff``). Milestone 13: a room session
    never gets a building-wide tool (``causes.BUILDING_WIDE_TOOLS``), whatever its findings name."""
    named = {t for f in (brief.get("findings") or {}).get("fixable") or [] for t in f.get("tools") or []}
    if brief["room"]["id"] == BUILDING:
        pool = TL.PLANNER_READS + TL.PLANNER_BUILDING + tuple(sorted(named)) + TL.PLANNER_CONTROL
    else:
        extra = tuple(t for t in sorted(named) if t not in TL.PLANNER_ROOM_EDITS)
        pool = TL.PLANNER_READS + TL.PLANNER_ROOM_EDITS + extra + TL.PLANNER_CONTROL
        pool = tuple(t for t in pool if t not in CS.BUILDING_WIDE_TOOLS)
    out: list[str] = []
    for t in pool:
        if t in registry.tools and t not in out:
            out.append(t)
    return out


# Checks the dry re-check cannot measure on the changed building: the scene checks of the build (S1-S6), the view
# checks of the render manifest (V1-V3, X6, L7), the looks (R4, R5, X8). On a target the edit changed they count as
# gone (the validator passed) and the next round's critics re-measure them; elsewhere they stay as they are.
# Round 4: the render's lighting_dark (a view above the +3 EV cap) is measured by the next render only; a
# set_lighting on its room changes its view (``tools.changed_targets``).
NOT_REMEASURED = frozenset({"S1", "S2", "S3", "S4", "S5", "S6", "V1", "V2", "V3", "X6", "L7", "R4", "R5", "X8",
                            *CS.LIGHTING_CHECKS, CS.CAMERA_BLOCKED_CHECK})      # fix round after P5: + blocked view


def lighting_kept(finding: Optional[dict], building_after: Optional[dict]) -> Optional[dict]:
    """A ``lighting_dark`` finding of the round (``finding``, from the render) that the edit's room light does not
    clear, with the prediction in its metrics and message; None when the new factor reaches the factor the view needs
    or nothing can be predicted (no finding, no building). Why (16 Oct 2026, before pod P3 attempt 2): only a render
    re-meters a view, so a changed view's lighting_dark counted as gone after any set_lighting; real04's basement
    salon needs about x10, set_lighting gives up to x3, and the x3 edit was counted as a removed finding. The render
    metered the view at ``lighting_factor_now`` and the view needs ``set_lighting_factor`` (= that factor x 2 ** the
    stops over the cap, ``critic_code.lighting_items``; the round's findings carry it in ``evidence.metrics``,
    ``causes._metrics``); the building after the edit carries the new factor (``wenart.blender.overrides.lighting_of``;
    ``tools.t_set_lighting`` passes its trial building with the edit's factor)."""
    if finding is None or not isinstance(building_after, dict):
        return None
    metrics = CS._metrics(finding)
    room = finding.get("room_id")
    try:
        want = float(metrics["set_lighting_factor"])
    except (KeyError, TypeError, ValueError):
        return None
    if not room:
        return None
    from wenart.blender.overrides import lighting_of

    after = float((lighting_of(building_after).get(str(room)) or {}).get("factor") or 1.0)
    if after >= want - 1e-6:
        return None
    evidence = finding.get("evidence") if isinstance(finding.get("evidence"), dict) else {}
    predicted = dict(metrics, predicted_factor_after=after)
    # the prediction leads the message: the acceptance's reason quotes its first 160 characters, and the planner
    # needs the factor to ask for next
    return dict(finding, metrics=predicted, evidence=dict(evidence, metrics=predicted),
                message=f"after the edit the room has x{after:g} of the x{want:g} the view needs (predicted, not "
                        f"re-rendered); " + str(finding.get("message") or ""))


# Fix round after P4a (module docstring): ``metrics.source`` of a finding measured on the round's scene manifest
# (``wenart.blender.exterior_checks.SCENE_MANIFEST_SOURCE``: the critical X2 of a built box through the roof).
MANIFEST_SOURCE = "scene_manifest"
S2_DEFAULT_TOLERANCE_M = 0.010   # scene_checks.TOLERANCES["overlap_m"]: an S2 without its tolerance_m


def manifest_measured(finding: dict) -> bool:
    """Fix round after P4a: a finding measured on the round's scene manifest (``MANIFEST_SOURCE``)."""
    return CS._metrics(finding).get("source") == MANIFEST_SOURCE


def _roof_state(building: Optional[dict]) -> str:
    b = building if isinstance(building, dict) else {}
    ext = (b.get("agent_overrides") or {}).get("exterior") if isinstance(b.get("agent_overrides"), dict) else None
    return json.dumps([b.get("roof"), (ext or {}).get("roof") if isinstance(ext, dict) else None], sort_keys=True,
                      default=str)


def roof_kept(override: Optional[dict], building_before: Optional[dict], building_after: Optional[dict]) -> bool:
    """Fix round after P5 (module docstring): the edit leaves the roof as it was: no ``roof`` in a ``set_exterior``
    override and the same roof (``roof``, ``agent_overrides.exterior.roof``) before and after."""
    if (override or {}).get("roof"):
        return False
    return building_before is None or _roof_state(building_before) == _roof_state(building_after)


def fit_key(piece: dict) -> str:
    """Fix round after P5: what makes a fitted asset reusable for a piece: its id, type, footprint size (mm), pin and
    build flag (a move or a turn keeps the asset; a reused id of another type or size does not)."""
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else {}
    size = [round(float(v), 3) for v in (fp.get("size") or [])[:2]]
    return json.dumps([piece.get("id"), piece.get("type"), size, piece.get("asset_pin"),
                       piece.get("build", True) is not False], sort_keys=True, default=str)


def _fitted(asset) -> bool:
    return isinstance(asset, dict) and asset.get("method") not in (None, "none")


def fitted_view(building_after: Optional[dict], final: Optional[dict],
                fit: Optional[Callable[[dict, dict], Optional[dict]]] = None) -> tuple[Optional[dict], dict]:
    """Fix round after P5 (module docstring): ``(building, note)``: ``building_after`` as the round's critic would
    measure it after the refit. A piece whose ``fit_key`` matches its piece in ``final`` (``building_final.json``) gets
    that piece's fitted ``asset`` record (a deep copy); a built, typed piece without a match gets ``fit(piece,
    building_after)`` (None or a failed fit keeps its box) when ``final`` holds fitted pieces at all. ``note``:
    ``{"overlaid": n, "refit": [ids]}``. ``building_after`` itself is returned unchanged when nothing applies (no
    ``final``, a test project without fitted assets); otherwise a shallow copy with new piece dicts for the changed
    pieces only."""
    note = {"overlaid": 0, "refit": []}
    if not isinstance(building_after, dict) or not isinstance(final, dict):
        return building_after, note
    fin = {p.get("id"): p for p in final.get("furniture") or [] if isinstance(p, dict) and p.get("id")}
    fitted_final = any(_fitted(p.get("asset")) for p in fin.values())
    out: list = []
    changed = False
    for p in building_after.get("furniture") or []:
        if not isinstance(p, dict):
            out.append(p)
            continue
        q = fin.get(p.get("id"))
        if q is not None and isinstance(q.get("asset"), dict) and fit_key(p) == fit_key(q):
            if p.get("asset") != q["asset"]:
                p = dict(p, asset=copy.deepcopy(q["asset"]))
                changed = True
            note["overlaid"] += 1
        elif fit is not None and fitted_final and CS.in_scene(p) and p.get("type") not in (None, "unknown"):
            try:
                asset = fit(p, building_after)
            except Exception:  # noqa: BLE001 - a prediction only: the box the piece had stays
                asset = None
            if _fitted(asset):
                p = dict(p, asset=asset)
                changed = True
                note["refit"].append(str(p.get("id")))
        out.append(p)
    if not changed:
        return building_after, note
    return dict(building_after, furniture=out), note


def _piece_of(building: Optional[dict], pid) -> Optional[dict]:
    if not isinstance(building, dict) or not pid:
        return None
    return next((f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("id") == pid), None)


def _footprint_state(piece: dict) -> tuple:
    fp = piece.get("footprint") or {}
    return (piece.get("level_id"), tuple(round(float(v), 4) for v in (fp.get("center") or [])[:2]),
            tuple(round(float(v), 4) for v in (fp.get("size") or [])[:2]), round(float(fp.get("rotation_deg") or 0), 3))


def footprint_corners(fp: dict) -> list[tuple[float, float]]:
    """The 4 corners of a footprint ``{center, size, rotation_deg}`` in order (a convex polygon)."""
    from wenart import geometry as G
    cx, cy = (float(v) for v in fp["center"][:2])
    w, d = (float(v) for v in fp["size"][:2])
    rot = float(fp.get("rotation_deg") or 0.0)
    return [G.rotate_point((cx + u * w / 2.0, cy + v * d / 2.0), rot, (cx, cy))
            for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _clip(poly: list, keep: Callable[[tuple], float]) -> list:
    """Sutherland-Hodgman: the part of the convex polygon ``poly`` where ``keep(p) >= 0`` (``keep`` linear)."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        kp, kq = keep(p), keep(q)
        if kp >= 0:
            out.append(p)
        if (kp >= 0) != (kq >= 0):
            t = kp / (kp - kq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def _inside(poly: list, p: tuple, eps: float = 1e-9) -> bool:
    """``p`` in the convex polygon ``poly`` (either winding; edges included)."""
    sign = 0
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if abs(cross) <= eps:
            continue
        s = 1 if cross > 0 else -1
        if sign and s != sign:
            return False
        sign = s
    return True


def footprint_wall_depth(piece: dict, wall: dict) -> Optional[float]:
    """How deep a piece's footprint reaches into a wall box (``scene_checks.wall_boxes``), signed and exact: the
    largest ``min(thickness / 2 - |n|, s, length - s)`` over the footprint's part beside the wall (``s`` along the
    wall's axis, ``n`` across it; the depth of ``scene_checks.depth_in_wall``, negative: the gap to the wall's face);
    None when no part of the footprint stands beside the wall's length.

    Fix round after P4b (17 Oct 2026; review of the P4a fix round): the footprint is convex and the depth is a concave
    piecewise-linear function of the point, so its maximum lies on a vertex of the footprint clipped to the wall's
    length, where an edge crosses a break line of the function (the axis ``n = 0``, the diagonals at the wall ends,
    the middle of the wall), or where two break lines cross inside it. All of them are tried. The 7 x 7 grid before
    missed the axis: real02's f_L1_024 moved 0.05 m INTO w_L1_006 was predicted 0.0016 m deep and accepted."""
    ax, ay = (float(v) for v in wall["a"])
    bx, by = (float(v) for v in wall["b"])
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return None
    ux, uy = (bx - ax) / length, (by - ay) / length
    half = float(wall["thickness"]) / 2.0
    local = [((x - ax) * ux + (y - ay) * uy, -(x - ax) * uy + (y - ay) * ux)
             for x, y in footprint_corners(piece["footprint"])]
    poly = _clip(_clip(local, lambda p: p[0]), lambda p: length - p[0])
    if len(poly) < 2 or max(p[0] for p in poly) - min(p[0] for p in poly) < 1e-9:
        return None                                    # nothing beside the wall's length (or only an end point)

    def depth(p) -> float:
        return min(half - abs(p[1]), p[0], length - p[0])

    # the break lines of ``depth``, as (a, b, c): a * s + b * n = c
    lines = [(0.0, 1.0, 0.0), (1.0, 1.0, half), (-1.0, 1.0, half - length), (1.0, -1.0, half),
             (1.0, 1.0, length - half), (1.0, 0.0, length / 2.0)]
    cands = list(poly)
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        for a, b, c in lines:
            fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
            if (fp <= 0 <= fq or fq <= 0 <= fp) and abs(fp - fq) > 1e-12:
                t = fp / (fp - fq)
                cands.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    for i, (a1, b1, c1) in enumerate(lines):
        for a2, b2, c2 in lines[i + 1:]:
            det = a1 * b2 - a2 * b1
            if abs(det) < 1e-12:
                continue
            p = ((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det)
            if _inside(poly, p):
                cands.append(p)
    return max(depth(p) for p in cands)


# Fix round after P4b (17 Oct 2026): the metrics key of the measured S2 message a predicted copy rebuilds from.
S2_MEASURED_MESSAGE = "message_measured"


def swap_depth_slack(piece: dict, wall: dict) -> float:
    """Fix round after P4b: how much a wall cut of ``piece`` can shrink when only its model changes (the footprint
    kept, ``swap_model``). The fit scales a model to the footprint's WIDTH (``fit.scale_for``, Milestone 13 K2), so a
    cut across the width (the wall's normal along the piece's local x) cannot change: 0. The model's depth may differ
    from the drawn depth up to ``fit.NON_UNIFORM_CAP`` (x1.10), so a cut across the depth can shrink by at most
    ``depth x (1 - 1 / cap)``. P4b: the bathtub f_L0_184 (a width cut, 0.049 m) and the washers f_L0_075 / 077 (depth
    cuts of 0.14-0.16 m, slack 0.055 m) kept their cuts after the swaps; the shower f_L0_180 (a depth cut of 0.041 m,
    slack 0.088 m) lost it."""
    try:
        from wenart.furniture.fit import NON_UNIFORM_CAP as cap
    except ImportError:                    # the fit's value on 17 Oct 2026
        cap = 1.10
    ax, ay = (float(v) for v in wall["a"])
    bx, by = (float(v) for v in wall["b"])
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return 0.0
    nx, ny = -(by - ay) / length, (bx - ax) / length
    rot = math.radians(float(piece["footprint"].get("rotation_deg") or 0.0))
    along_x = abs(nx * math.cos(rot) + ny * math.sin(rot))
    along_y = abs(-nx * math.sin(rot) + ny * math.cos(rot))
    if along_x >= along_y:
        return 0.0
    return float(piece["footprint"]["size"][1]) * (1.0 - 1.0 / float(cap))


def s2_wall_kept(finding: Optional[dict], building_before: Optional[dict], building_after: Optional[dict]
                 ) -> Optional[dict]:
    """Fix round after P4a (module docstring): an S2 WALL cut of the round (``finding``: ``metrics.wall_id`` and
    ``depth_m``, no ``other``, no ``kitchen_run``) that the edit does not clear, with the prediction in its metrics
    and message; None when the finding counts as gone: the piece was removed or is not built, its type changed (the
    next round measures the new model), nothing can be predicted, or the predicted cut (the cut before the edit plus
    the change of ``footprint_wall_depth``) is within the cut's ``tolerance_m`` or below ``causes.S2_TOLERANCE_M``.
    Why: the mesh cut and the footprint differ by up to 0.05 m, but a move changes both by the same amount; a move
    along the wall (P4a edit 332, real02 f_L1_024) cannot shrink the cut.

    Fix round after P4b (17 Oct 2026; the review of the P4a fix round and the P4b analysis):

    - the depth is exact (``footprint_wall_depth``), not sampled on a grid;
    - the cut before the edit is the round's measured ``depth_m``, or the ``predicted_depth_after`` an earlier
      accepted edit of the round left on the finding (``building_before`` is the building after that edit): two
      chained moves are predicted from where the first one left the piece, and the message is rebuilt from the
      measured text (``S2_MEASURED_MESSAGE``) instead of stacking another prefix;
    - a predicted cut below ``causes.S2_TOLERANCE_M`` (0.03 m) counts as gone, the rule of
      ``critic_code.within_tolerance_minor``: such a cut is a minor finding no tool is asked to fix, so a move that
      leaves 0.02 m is no longer rejected (and stored in the memory as a rejection);
    - an edit that keeps the footprint and the type (``swap_model``: the model is fitted to the kept footprint;
      ``set_front``) keeps the cut, less what another model's depth may change (``swap_depth_slack``): P4b accepted 5
      swaps for an S2 wall cut and 4 cuts were still there (the bathtub f_L0_184 at 0.049 m twice)."""
    if finding is None or not isinstance(building_before, dict) or not isinstance(building_after, dict):
        return None
    metrics = CS._metrics(finding)
    wall_id = metrics.get("wall_id")
    if not wall_id or metrics.get("other") or metrics.get("kitchen_run"):
        return None
    try:
        depth = float(metrics["predicted_depth_after"] if metrics.get("predicted_depth_after") is not None
                      else metrics["depth_m"])
        tolerance = float(metrics.get("tolerance_m") if metrics.get("tolerance_m") is not None
                          else S2_DEFAULT_TOLERANCE_M)
    except (KeyError, TypeError, ValueError):
        return None
    pid = finding.get("target")
    old, new = _piece_of(building_before, pid), _piece_of(building_after, pid)
    if old is None or new is None or not CS.in_scene(new) or not old.get("footprint") or not new.get("footprint"):
        return None
    if old.get("type") != new.get("type"):
        return None                        # retyped: another model and class tolerance, the next round measures it
    from wenart.blender import scene_checks as SC
    try:
        wall = next((w for w in SC.wall_boxes(building_before, old.get("level_id")) if w["id"] == wall_id), None)
        if wall is None:
            return None
        if _footprint_state(old) == _footprint_state(new):
            slack = swap_depth_slack(new, wall)
            d_old = d_new = None
        else:
            d_old, d_new = footprint_wall_depth(old, wall), footprint_wall_depth(new, wall)
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    if d_old is None and d_new is None:
        # fix round after P4b: the footprint is kept (swap_model); the cut can shrink only by what another model's
        # depth may differ (swap_depth_slack), so ``predicted`` is the least cut after the edit
        predicted = depth - slack
        size = [float(v) for v in (new["footprint"].get("size") or [0, 0])[:2]]
        what = (f"the edit keeps the footprint {size[0]:.2f} x {size[1]:.2f} m (the model is fitted to its width"
                + (f", its depth within {slack:.3f} m" if slack > 0 else "") + f"), so the cut into {wall_id} stays "
                f"at least {predicted:.3f} m")
    else:
        if d_old is None:
            return None                        # the footprint never stood beside the wall: no prediction
        if d_new is None:
            return None                        # moved off the wall's length: the next round measures it
        predicted = depth + (d_new - d_old)
        what = f"after the edit the cut into {wall_id} is about {predicted:.3f} m"
    if predicted <= tolerance + 1e-9 or predicted < CS.S2_TOLERANCE_M - 1e-9:
        return None
    evidence = finding.get("evidence") if isinstance(finding.get("evidence"), dict) else {}
    original = str(metrics.get(S2_MEASURED_MESSAGE) or finding.get("message") or "")
    kept_metrics = dict(metrics, predicted_depth_after=round(predicted, 4), **{S2_MEASURED_MESSAGE: original})
    return dict(finding, metrics=kept_metrics, evidence=dict(evidence, metrics=kept_metrics),
                message=f"{what} (predicted from the footprint, not rebuilt; allowed "
                        f"{max(tolerance, CS.S2_TOLERANCE_M):.3f} m); " + original)


def exterior_kept(finding: dict, cause: str, override: dict) -> dict:
    """Fix round after P4b: a vision finding a ``set_exterior`` override does not touch (``causes.override_touches``),
    kept with the reason leading its message (the acceptance quotes it)."""
    slots = ", ".join(sorted(CS.override_slots(override))) or "nothing"
    wants = " or ".join(CS.EXTERIOR_SLOTS_OF_CAUSE.get(cause, ())) or "no exterior slot"
    return dict(finding, cause=cause,
                message=f"the edit does not change what the finding is about (the override sets {slots}; the cause "
                        f"{cause} needs {wants}); " + str(finding.get("message") or ""))


def scene_after(scene: Optional[dict], tool: str, args: Optional[dict], building: Optional[dict]) -> dict:
    """Fix round after P4b: the round's scene manifest as the dry re-check's critic reads it after the edit: a
    ``set_exterior`` sun override is written into a copy (``lighting.sun``: ``elevation_deg``, the compass
    ``azimuth_deg`` and ``azimuth_building_deg`` with ``site.north_deg``), so the code's X7 measures the new sun
    (P4b's 55 degree sun was accepted and X7 came in the next round); any other edit gets ``scene`` itself."""
    sun = (args or {}).get("sun") if tool == "set_exterior" else None
    if not isinstance(sun, dict) or not sun:
        return scene if scene is not None else {}
    from wenart.blender import lighting as LT
    from wenart.blender import site as S
    out = dict(scene or {})
    lighting = dict(out.get("lighting") or {})
    now = dict(lighting.get("sun") or {})
    if isinstance(sun.get("elevation_deg"), (int, float)):
        now["elevation_deg"] = float(sun["elevation_deg"])
    if isinstance(sun.get("azimuth_deg"), (int, float)):
        north = S.north_deg(building or {})[0]
        now["azimuth_deg"] = float(sun["azimuth_deg"])
        now["azimuth_building_deg"] = LT.building_azimuth(float(sun["azimuth_deg"]), north)
    now["source"] = "agent"
    lighting["sun"] = now
    out["lighting"] = lighting
    return out


def after_findings(code_after: list[dict], before: list[dict], changed: set, building_after: Optional[dict] = None,
                   building_before: Optional[dict] = None, override: Optional[dict] = None,
                   targets: Optional[list] = None, round_changed: Optional[set] = None) -> list[dict]:
    """The finding list after an edit for ``accept_edit`` (module docstring): the code critic's findings on the
    changed building (``code_after``) without the ``NOT_REMEASURED`` ones, plus the ``NOT_REMEASURED`` and vision
    findings of ``before`` whose target the edit did not change (a vision finding on a changed target is re-judged
    after the re-render; a ``NOT_REMEASURED`` one is re-measured by the next round, except a ``lighting_dark`` view the
    edit's room light cannot clear, ``lighting_kept``, and an S2 wall cut the new footprint does not clear,
    ``s2_wall_kept``, which needs ``building_before``). Every finding gets its ``cause``.

    Review of 16 Oct 2026: the ``NOT_REMEASURED`` findings come from ``before``, not from ``code_after``. The dry
    re-check rebuilds them from the round's scene and render manifests, which no edit changes, so a finding an
    earlier edit of the round had removed came back on the next edit as a new one (a new critical finding rejected an
    unrelated edit), and the lighting metrics were recomputed against factors the render had not used.

    Fix round after P4a: a ``code_after`` finding measured on the round's scene manifest (``manifest_measured``: the
    critical X2 of a built box through the roof) is left out on a changed target, for the same reason; the finding
    re-measured on the building after the edit (the major X2 under the slope, same key) stays.

    Fix round after P4b: ``override`` (a ``set_exterior``'s) keeps every vision finding whose cause it does not touch
    (``exterior_kept``), whatever its target: a building-wide edit changes ``building`` and the views, so a ground
    or sun edit counted the vision X4 "no path to the entrance" as gone (P4b seq 951 and 1357; it came back).

    Pass before P5: ``targets`` (the edit's target findings, ``tools.target_findings``): a vision target the
    override does not touch is kept through ``exterior_kept`` (with the reason) also when its target is not in
    ``changed`` (``tools.changed_targets`` leaves it out); the other vision findings keep their message, so the
    round's list (an accepted edit's ``after_findings``) carries no reason of an edit that was not about them.

    Fix round after P5 (module docstring): a ``manifest_measured`` finding of ``code_after`` is also left out on a
    target an accepted edit of the round changed (``round_changed``, ``ctx.round_changed``), and when its key is not
    among ``before`` while the edit keeps the roof (``roof_kept``): the round's boxes are fixed, so only a roof change
    can make one new (P5: the box of the removed f_L1_056 came back as a new critical in every later dry re-check)."""
    target_keys = {CS.finding_key(t) for t in targets or [] if isinstance(t, dict)}
    before_keys = {CS.finding_key(f) for f in before}
    stale = set(changed) | set(round_changed or ())
    same_roof = roof_kept(override, building_before, building_after)
    out = []
    for f in code_after:
        if f.get("check") in NOT_REMEASURED:
            continue
        if manifest_measured(f) and (f.get("target") in stale
                                     or (same_roof and CS.finding_key(f) not in before_keys)):
            continue
        out.append(dict(f, cause=f.get("cause") or CS.cause_of(f, building_after)))
    for f in before:
        if f.get("source") == "vision":
            cause = f.get("cause") or CS.cause_of(f, building_after)
            untouched = override is not None and not CS.override_touches(cause, override)
            if untouched and (f.get("target") in changed or CS.finding_key(f) in target_keys):
                out.append(exterior_kept(f, cause, override))
            elif f.get("target") not in changed:
                out.append(dict(f, cause=cause))
            continue
        if f.get("check") not in NOT_REMEASURED:
            continue
        if f.get("target") in changed:
            kept = None
            if f.get("check") in CS.LIGHTING_CHECKS:
                kept = lighting_kept(f, building_after)
            elif f.get("check") == "S2":
                kept = s2_wall_kept(f, building_before, building_after)
            if kept is not None:
                out.append(dict(kept, cause=kept.get("cause") or CS.cause_of(kept, building_after)))
            continue
        out.append(dict(f, cause=f.get("cause") or CS.cause_of(f, building_after)))
    return out


def lighting_first(steps: list[dict]) -> list[dict]:
    """Fix round after P4a: the ``set_lighting`` steps first, the others in their order (module docstring)."""
    return [s for s in steps if s.get("tool") == "set_lighting"] + [s for s in steps if s.get("tool") != "set_lighting"]


def final_lighting(finding: dict) -> bool:
    """Fix round after P4a: a critical or major ``lighting_dark`` view that one ``set_lighting`` clears (cause
    ``lighting``): the final round takes it too (``FINAL_ROUND_LIGHTING``)."""
    cause = finding.get("cause") if finding.get("cause") in CS.CAUSE_TOOLS else CS.cause_of(finding)
    return str(finding.get("check")) in CS.LIGHTING_CHECKS and finding.get("severity") in ("critical", "major") \
        and cause == "lighting"


def is_wanted(finding: dict, wanted, lighting: bool = False) -> bool:
    """A finding of the round's work: a wanted severity, or (``lighting``, the final round) ``final_lighting``."""
    return finding.get("severity") in wanted or (lighting and final_lighting(finding))


def default_checklist(brief: dict, wanted=("critical", "major"), lighting: bool = False) -> list[dict]:
    """One step per fixable finding of the wanted severities (``lighting``: and the final round's ``final_lighting``
    views): its first tool on its target (the room for a finding without a piece target). Fix round after P4a: the
    ``set_lighting`` steps come first (``lighting_first``)."""
    room_id = brief["room"]["id"]
    groups = [g for g in brief.get("groups") or [] if g.get("group_id")]
    steps = []
    for f in (brief.get("findings") or {}).get("fixable") or []:
        if not is_wanted(f, wanted, lighting):
            continue
        tool, target = f["tools"][0], BR.step_target(f, room_id)
        if tool == "complete_group" and target not in {g["group_id"] for g in groups}:
            # A G9 names the kitchen (the room or its kitchen zone, ``<zone_id>``), not a group; complete_group needs
            # the group id: the brief's group of that kitchen that misses something (``<target>.kitchen_run``).
            # Without it the default step always failed "no group" (CPU pre-flight of 16 Oct 2026, real04 G9).
            own = [g for g in groups if str(g["group_id"]).startswith(f"{target}.") and g.get("missing")]
            # A G9 / G10 on a room id: the room's other groups share the prefix (an eat-in kitchen's dining group
            # missing a chair), so the group that misses what the finding names comes first ("... has no fridge
            # (fridge)", "bathroom without a toilet"); the order is otherwise the brief's.
            words = set(re.findall(r"[a-z_]+", str(f.get("message") or "").lower()))
            own.sort(key=lambda g: not (set(map(str, g.get("missing") or [])) & words))
            if own:
                target = own[0]["group_id"]
        steps.append({"finding_ids": [f["id"]], "tool": tool, "target": target,
                      "why": str(f.get("message") or f.get("check"))[:300]})
    return lighting_first(steps)


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
        # round 2: a step may act on an unbuilt piece when one of its findings names it (the untyped piece of an
        # NR finding, the unbuilt anchor of an F8: ``edit_target``); the brief checked the anchor's locks
        named = {t for fid in ids if fid in fixable
                 for t in (fixable[fid].get("edit_target"), fixable[fid].get("target")) if t}
        if tool not in offered:
            why = f"tool {tool} is not offered"
        elif bad_ids:
            why = ", ".join(f"{f} is {'not yours' if f in not_yours else 'not a fixable finding'}" for f in bad_ids)
        elif target in unbuilt and target not in named:
            why = f"{target} is not built"
        elif tool in BR.PIECE_TOOLS and target not in unbuilt:
            p = pieces.get(target)
            if p is None:
                why = f"{tool} needs a built piece of the room as target, not {target!r}"
            elif not BR.is_allowed(p, tool):
                why = f"{target} does not allow {tool}: {(p.get('allowed') or {}).get(tool) or 'locked'}"
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


PLAN_STATUSES = ("ok", "empty", "refused", "default")


def plan_status(plan, checked: list[dict]) -> str:
    """Fix round after P4a: why a session runs the checklist it runs: ``ok`` (the checked plan has steps),
    ``empty`` (a valid plan without steps), ``refused`` (a valid plan whose steps ``check_plan`` all refused) or
    ``default`` (no valid plan: a model error or an answer outside the schema)."""
    if not isinstance(plan, dict):
        return "default"
    if checked:
        return "ok"
    return "refused" if plan.get("steps") else "empty"


def plan_skip(plan) -> list[dict]:
    """Fix round after P4a: the planner's ``skip`` list (``prompts.PLAN_SCHEMA``: ``finding_id``, ``why``), for the log
    and the memory (at most 20, ``why`` cut to 300 characters)."""
    items = plan.get("skip") if isinstance(plan, dict) else None
    return [{"finding_id": str(s.get("finding_id")), "why": str(s.get("why") or "")[:300]}
            for s in (items if isinstance(items, list) else []) if isinstance(s, dict)][:20]


def plan_choices(plan) -> list[dict]:
    """Fix round after P4a: the plan's program choices (``group_id``, ``option``), for the log."""
    program = plan.get("program") if isinstance(plan, dict) else None
    items = program.get("choices") if isinstance(program, dict) else None
    return [{"group_id": c.get("group_id"), "option": c.get("option")}
            for c in (items if isinstance(items, list) else []) if isinstance(c, dict)][:8]


def step_hit(step: dict, tool: str, args: dict, result: dict) -> bool:
    """An edit ``tool(args)`` is the one of a checklist step: the same tool on the step's target."""
    if step.get("tool") != tool:
        return False
    target = step.get("target")
    return target in {args.get(k) for k in ("piece_id", "room_id", "group_id", "view_id", "span_id")} or \
        target in (result.get("changed_ids") or [])


def step_done(step: dict, tool: str, args: dict, result: dict, findings: Optional[list] = None) -> bool:
    """An accepted edit ``tool(args)`` completes a checklist step with the same tool on the same target. Review of
    16 Oct 2026: a ``set_lighting`` step stays open while its finding is still in ``findings`` (the round's list after
    the edit): every dark view of a room is a step on the room, and a factor that clears one view may leave another
    (``lighting_kept``), whose step then still asks for its own factor."""
    if step.get("tool") != tool:
        return False
    if tool == "set_lighting" and findings is not None:
        open_ids = {f.get("id") for f in findings if f.get("id")}
        if any(fid in open_ids for fid in step.get("finding_ids") or []):
            return False
    return step_hit(step, tool, args, result)


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
                 groups_fn: Optional[Callable] = None, scene_dir=None, recheck: Optional[Callable] = None,
                 acceptance: bool = True, fit_fn: Optional[Callable] = None):
        self.project_out = Path(project_out)
        # fix round after P5: ``fit_fn(piece, building) -> asset`` fits a piece the refit has not fitted yet for the
        # dry re-check (``fitted_view``; default ``dry_fit``); the fitted ``building_final.json`` is read once per file
        self.fit_fn = fit_fn
        self._final: tuple = (None, None)
        self._fit_cache: dict = {}
        self._fit_lock = threading.Lock()
        # Milestone 13: ``recheck(building, scene, render_manifest) -> [findings]`` is the dry re-check after an
        # edit (default: the code critic on the changed building); ``acceptance`` False keeps the M12 rule (replay).
        self.recheck = recheck
        self.use_acceptance = bool(acceptance)
        self.findings_removed = 0
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
        self.scene_dir = Path(scene_dir) if scene_dir is not None else None     # None: CC.scene_checks_dir per round
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
        self.overrides.reload()              # the scheduler's rollbacks between rounds (``Overrides.reload``)
        if hasattr(self.memory, "refresh"):
            self.memory.refresh()            # fix round after P5: the memory's scope (the building and the code)
        return TL.ToolContext.load(self.project_out, round=round_no, model_id=getattr(self.model, "model", ""),
                                   log=self.log, overrides=self.overrides,
                                   preview_dir=preview_dir or self.preview_dir, apply_edit=self.apply_edit,
                                   validators=self.validators, plausibility=self.plausibility,
                                   catalog_loader=self.catalog_loader, max_tries=self.max_tries, memory=self.memory,
                                   level_edit=self.level_edit, level_checks=self.level_checks, sync=self.sync,
                                   brief_fns=self.brief_fns, acceptance=self.acceptance if self.use_acceptance else None)

    # ----- acceptance (Milestone 13) ------------------------------------------------------------------

    def code_findings(self, building: dict, ctx: TL.ToolContext, manifest: Optional[dict],
                      scene: Optional[dict] = None) -> list[dict]:
        """The code critic's findings of ``building`` (the dry re-check: ``recheck`` when injected, else the code
        critic of the round, else ``critic_code.run`` with the same functions as ``run_code_critic``). Fix round
        after P4b: ``scene`` (default the round's ``ctx.scene``) is the scene manifest the critic reads."""
        scene = ctx.scene if scene is None else scene
        if self.recheck is not None:
            got = self.recheck(building, scene, manifest)
        elif self.code_critic is not None:
            got = self.code_critic(building, scene, manifest)
        else:
            got = CC.run(building, scene, manifest, scene_dir=self.scene_dir or CC.scene_checks_dir(self.project_out),
                         **self.critic_kwargs())
        if isinstance(got, dict):
            got = got.get("findings") or []
        return [dict(f) for f in got or []]

    def critic_kwargs(self) -> dict:
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
        return kwargs

    def acceptance(self, ctx: TL.ToolContext, tool: str, args: dict, result: dict, building_after: dict) -> dict:
        """The acceptance of one validated edit (module docstring): the findings it targets
        (``tools.target_findings``), the dry re-check on ``building_after`` (``after_findings``) and
        ``accept_edit``. Returns ``{"accepted", "reason", "target", "target_findings", "before", "after", "removed",
        "after_findings"}``; the tools apply the verdict and the loop logs it."""
        targets = TL.target_findings(ctx, tool, args)
        before = list(ctx.findings)
        changed = TL.changed_targets(tool, args, result, targets, findings=before)
        # fix round after P5: the fitted boxes the round's critic measured (fitted_view)
        measured, fitted = self.fitted_after(ctx, building_after)
        # fix round after P4b: the critic reads the sun a set_exterior sets (scene_after)
        code_after = self.code_findings(measured, ctx, self.render_manifest(ctx.preview_dir),
                                        scene=scene_after(ctx.scene, tool, args, ctx.building))
        # fix round after P4a: the building before the edit predicts an S2 wall cut of a moved piece (s2_wall_kept);
        # fix round after P4b: a set_exterior keeps the vision findings it does not touch; fix round after P5: the
        # stale boxes of the round's earlier accepted edits (round_changed)
        override = {k: v for k, v in (args or {}).items() if k != "reason"} if tool == "set_exterior" else None
        after = after_findings(code_after, before, changed, measured, building_before=ctx.building,
                               override=override, targets=targets,
                               round_changed=set(getattr(ctx, "round_changed", None) or ()))
        # round 4: the pieces the edit took out of the scene, for the acceptance's room-set rule (a fixture removed);
        # fix round after P4a: the metrics name an S2's cut (``causes.finding_key``); fix round after P5: the pieces it
        # added (a re-created piece keeps its finding)
        edit = {"target_finding": [{"check": f.get("check"), "target": f.get("target"), "metrics": CS._metrics(f)}
                                   for f in targets],
                "penalty_before": result.get("penalty_before"), "penalty_after": result.get("penalty_after"),
                "score_before": result.get("score_before"), "score_after": result.get("score_after"),
                "removed": CS.removed_pieces(ctx.building, building_after),
                "added": CS.added_pieces(ctx.building, building_after)}
        ok, reason = accept_edit(before, after, edit)
        room = TL.edit_room(ctx, args)
        scope = set(changed) | {f.get("target") for f in targets}

        def mine(f: dict) -> bool:
            return f.get("room_id") == room or f.get("target") in scope or (room == BUILDING and not f.get("room_id"))

        carried = sorted({CS._fmt(CS.finding_key(f)) for f in after
                          if f.get("target") in changed and (f.get("source") == "vision"
                                                             or f.get("check") in NOT_REMEASURED)})
        note = None
        if ok and any(f.get("target") in changed and (f.get("source") == "vision" or f.get("check") in NOT_REMEASURED
                                                      or manifest_measured(f))
                      for f in before):
            note = "findings the dry re-check cannot measure on the changed target (scene, view, look, vision or " \
                   "the built scene's boxes) count as gone and are re-measured by the next round"
        if fitted["refit"]:
            # fix round after P5: a piece the refit has not fitted yet was fitted for the dry re-check
            note = (note + "; " if note else "") + (f"fitted for the dry re-check (predicted; the refit may choose "
                                                    f"another model): {', '.join(fitted['refit'][:8])}")
        return {"accepted": ok, "reason": reason, "target": [CS._fmt(CS.finding_key(f)) for f in targets],
                "target_findings": targets, "before": CS.key_list([f for f in before if mine(f)]),
                "after": CS.key_list([f for f in after if mine(f)]), "removed": findings_removed(before, after),
                "after_findings": after, "note": note, "carried": carried, "changed": sorted(map(str, changed)),
                "fitted": fitted}

    # ----- the fitted boxes of the dry re-check (fix round after P5) ------------------------------------------

    def final_building(self) -> Optional[dict]:
        """``building_final.json`` (the refit's building the round's critic measured), read again only when the file
        changed; None without one."""
        path = self.project_out / "building_final.json"
        try:
            stamp = path.stat().st_mtime_ns
        except OSError:
            return None
        if self._final[0] != stamp:
            self._final = (stamp, TL.read_json(path))
        return self._final[1]

    def dry_fit(self, ctx: TL.ToolContext, piece: dict, building: dict, fitted: Optional[dict] = None
                ) -> Optional[dict]:
        """The asset ``fit.fit_piece`` gives ``piece`` in the licence mode and style family of the fitted building
        ``fitted`` (``building_final.json``: the working building's first fit had no style family, P5: None against
        the refit's "modern"), else of ``building``, as ``edit_ops``' retype refit reads them
        (``licence_mode_of``, ``_style_family_of``); cached per piece state; None when the fit fails or builds
        nothing."""
        key = fit_key(piece) + json.dumps([piece.get("room_id"), piece.get("level_id")], default=str)
        with self._fit_lock:
            if key in self._fit_cache:
                return copy.deepcopy(self._fit_cache[key])
        if self.fit_fn is not None:
            asset = self.fit_fn(piece, building)
        else:
            from wenart.furniture import edit_ops as EO
            from wenart.furniture import fit as F
            source = fitted if isinstance(fitted, dict) else building
            try:
                asset = F.fit_piece(dict(piece, build=True), ctx.catalog(), mode=EO.licence_mode_of(source),
                                    style_family=EO._style_family_of(source))
            except Exception:  # noqa: BLE001 - a prediction only: the piece keeps its box
                asset = None
        asset = asset if _fitted(asset) else None
        with self._fit_lock:
            self._fit_cache[key] = copy.deepcopy(asset)
        return asset

    def fitted_after(self, ctx: TL.ToolContext, building_after: dict) -> tuple[dict, dict]:
        """``fitted_view`` of ``building_after`` against ``building_final.json`` with ``dry_fit`` (in the final
        building's licence mode and style family)."""
        final = self.final_building()
        return fitted_view(building_after, final,
                           fit=lambda piece, building: self.dry_fit(ctx, piece, building, fitted=final))

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
        return CC.run(building, ctx.scene, manifest, scene_dir=self.scene_dir or CC.scene_checks_dir(self.project_out),
                      **self.critic_kwargs())

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
                                               plan_crop=None, code=code, call_id=call_id, camera=ctx.camera(key),
                                               scene=ctx.scene)
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
            # fix round after P3: the cause, and for a finding no agent tool fixes the reason and the stage it is
            # reported to (``causes.REPORT_TO``: a decor piece through the roof goes back to the decor stage)
            cause = f.get("cause")
            no_tool = cause in CS.CAUSE_TOOLS and not CS.CAUSE_TOOLS[cause] and not f.get("dropped")
            self.log.event("finding", round_no, source=f["source"], checklist=f["check"], severity=f["severity"],
                           target=f["target"], room_id=f.get("room_id"), finding=f["message"],
                           evidence=f.get("evidence"), dropped=f.get("dropped"),
                           call_id=(f.get("evidence") or {}).get("call_id"),
                           model=self.log.model if f["source"] != "code" else None,
                           revision=self.log.revision if f["source"] != "code" else None,
                           cause=cause, not_yours=CS.no_tool_reason(f) if no_tool else None,
                           report_to=CS.REPORT_TO.get(cause) if no_tool else None)

    def log_edit(self, round_no: int, call_id: str, tool: str, args: Optional[dict], result: dict,
                 label: Optional[str], findings: list[dict], room_id: Optional[str] = None) -> None:
        target = TL._target(tool, args or {})
        verdict = result.get("acceptance") if isinstance(result.get("acceptance"), dict) else None
        targeted = list((verdict or {}).get("target_findings") or [])
        match = (targeted[0] if targeted else None) or next(
            (f for f in findings if f.get("target") == target), None) or next(
            (f for f in findings if f.get("room_id") and f.get("room_id") == (args or {}).get("room_id")), None)
        accepted = bool(result.get("accepted"))
        failed = list(result.get("failed_checks") or ([] if accepted else [str(result.get("error") or "rejected")]))
        evidence = None
        if verdict is not None:
            # Milestone 13: both finding lists (the room's critical / major keys before and after the dry re-check)
            evidence = {"acceptance": {k: verdict.get(k) for k in ("accepted", "reason", "target", "before", "after",
                                                                   "removed", "note", "carried")
                                       if verdict.get(k) is not None}}
        # fix round after P3: the seq the tool reserved for this edit (its ``log_seq`` in overrides.json)
        self.log.event("edit" if accepted else "rejected_edit", round_no, seq=result.get("log_seq") or None,
                       model=self.log.model or "unknown",
                       revision=self.log.revision, call_id=call_id, tool=tool, args=dict(args or {}),
                       target=target, checklist=match["check"] if match else None,
                       severity=match["severity"] if match else None, finding=match["message"] if match else None,
                       validation={"accepted": accepted, "failed_checks": failed,
                                   "score_before": result.get("score_before"),
                                   "score_after": result.get("score_after")},
                       label=label, reason=str((args or {}).get("reason") or "no reason given"),
                       before=result.get("before_image"), after=result.get("after_image"),
                       rerun_from=result.get("rerun_from"), overrides_id=result.get("overrides_id"),
                       note=result.get("message") or None, room_id=room_id, evidence=evidence)

    # ----- sessions: which rooms, in which order ------------------------------------------------------

    def building_brief(self, ctx: TL.ToolContext, findings: list[dict]) -> dict:
        """The brief of the building session (findings without a room: exterior, levels, exterior views)."""
        fixable, not_yours = BR.classify(findings, ctx.building, None, {}, {}, {})
        return {"room": {"id": BUILDING, "label": "the building and its site", "type": None},
                "findings": {"fixable": fixable, "not_yours": not_yours},
                "memory": self.memory.summary(BUILDING), "pieces": [], "not_built": [], "groups": [],
                "free_wall_spans": [], "candidates": [], "program": {"groups": []}}

    def sessions_for(self, ctx: TL.ToolContext, found: list[dict], wanted: tuple, lighting: bool = False
                     ) -> tuple[list[dict], dict]:
        """``(sessions, coverage)``: one session per room (and one for the building) with a fixable finding of the
        wanted severities (``lighting``, the final round: and the ``final_lighting`` views), in the order of the
        module docstring; ``coverage`` lists the rooms with fixable findings and how many open findings are not
        fixable."""
        open_ = [f for f in found if is_wanted(f, wanted, lighting)]
        rooms = {r.get("id"): r for r in ctx.building.get("rooms") or []}
        # fix round after P3: a decor piece belongs to its room too (P3: an X2 on the mirror dec_L1_009 had no room
        # and went to the building session, whose relayout_room on "building" was refused for 4 rounds)
        piece_room = {p.get("id"): p.get("room_id") for p in (ctx.building.get("decor") or [])
                      + (ctx.building.get("furniture") or []) if isinstance(p, dict)}
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
            fixable = [f for f in (brief.get("findings") or {}).get("fixable") or [] if is_wanted(f, wanted, lighting)]
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
        """The tools offered to one session (``offered_tools``)."""
        return offered_tools(self.registry, brief)

    # ----- planner -------------------------------------------------------------------------------

    def plan(self, ctx: TL.ToolContext, round_no: int, sessions: list[dict], critical_only: bool = False,
             lighting: bool = False) -> dict:
        """The planner part of one round: the sessions in their order, ``workers`` at a time; a session starts only
        before the round's time cap and while the time budget allows (the first one always). ``{"calls",
        "schema_errors", "replies", "error", "sessions", "rooms", "plans_ok", "context_full"}`` (fix round after P3:
        ``error`` is a model error other than a full context; ``context_full`` counts the sessions it ended)."""
        total = {"calls": 0, "replies": 0, "error": None, "sessions": 0, "rooms": [], "plans_ok": 0,
                 "steps_done": 0, "steps": 0, "context_full": 0}
        budget = CallBudget(self.max_calls)
        cap_at = self.clock() + self.round_cap_s
        lock = threading.Lock()
        started = {"n": 0}

        def one(index: int, item: dict) -> Optional[dict]:
            with lock:
                if started["n"] and (self.clock() > cap_at or not self.time_ok() or budget.empty()):
                    return None
                started["n"] += 1
            return self.plan_session(ctx, round_no, item, budget, critical_only, session=index, cap_at=cap_at,
                                     lighting=lighting)

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
            total["context_full"] += 1 if res.get("context_full") else 0
            if res["error"]:
                total["error"] = res["error"]
        return dict(total, schema_errors=ctx.schema_errors)

    def make_plan(self, ctx: TL.ToolContext, round_no: int, brief: dict, offered: list[str], critical_only: bool,
                  tag: str, lighting: bool = False) -> tuple[list[dict], list[str], bool]:
        """The plan call (``prompts.PLAN_SCHEMA``), checked against the brief: ``(checklist, problems, plan_ok)``.
        Fix round after P4a: the plan event's status is ``plan_status`` (ok / empty / refused / default) and its
        evidence holds the planner's ``skip`` list and program ``choices`` (the memory stores both); the default
        checklist still runs for every status but ok; the ``set_lighting`` steps come first (``lighting_first``)."""
        wanted = ("critical",) if critical_only else ("critical", "major")
        plan = None
        if self.plan_first:
            messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                        {"role": "user", "content": P.plan_prompt(round_no, brief, offered, critical_only,
                                                                  lighting=lighting)}]
            try:
                reply = self.model.structured(messages, P.PLAN_SCHEMA, call_id=f"{tag}-plan", name="plan",
                                              kind="plan", thinking=getattr(self.model, "planner_thinking", False))
                plan = reply.data
            except ModelError:
                plan = None
        steps, problems = check_plan(plan, brief, offered)
        status = plan_status(plan, steps)
        plan_ok = status == "ok"
        if not steps:
            steps = default_checklist(brief, wanted, lighting)
        steps = lighting_first(steps)
        room_id = brief["room"]["id"]
        skip, choices = plan_skip(plan), plan_choices(plan)
        self.memory.add_plan(room_id, round_no, plan, plan_ok, problems, status=status)
        self.log.event("plan", round_no, room_id=room_id, call_id=f"{tag}-plan", status=status,
                       counts={"steps": len(steps), "problems": len(problems)},
                       note="; ".join(problems)[:600] or None, model=self.log.model, revision=self.log.revision,
                       evidence={"steps": [{k: s.get(k) for k in ("tool", "target", "finding_ids")} for s in steps],
                                 "skip": skip, "choices": choices})
        return steps, problems, plan_ok

    def plan_session(self, ctx: TL.ToolContext, round_no: int, item: dict, budget: CallBudget,
                     critical_only: bool = False, session: int = 0, cap_at: Optional[float] = None,
                     lighting: bool = False) -> dict:
        """One room session: the plan, then the tools on the checked checklist (module docstring). Fix round after
        P4a: a step whose edit the memory refused twice (``step_closed`` in the tool result) is closed; the session
        ends when every step is done or closed. Fix round after P5: a ``max_tries`` refusal closes every step on its
        target, and ``REFUSALS_END_SESSION`` edits in a row refused without validation (``tools.refused_unvalidated``)
        on targets refused before in the session end it (a ``check`` event ``REFUSALS_CHECK``)."""
        brief = item["brief"]
        room_id = item["room_id"]
        state = ctx.begin_session(room_id)
        tag = f"r{round_no}-s{session + 1}" if session else f"r{round_no}"
        t0 = self.clock()
        self.memory.visit(room_id, round_no)
        offered = self.session_tools(brief)
        checklist, problems, plan_ok = self.make_plan(ctx, round_no, brief, offered, critical_only, tag,
                                                      lighting=lighting)
        state.checklist = list(checklist)          # Milestone 13: the steps name the findings an edit targets
        findings = item["fixable"] + [f for f in ctx.findings if f.get("room_id") == room_id]
        messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                    {"role": "user", "content": P.session_task(round_no, brief, checklist, problems,
                                                               self.calls_per_room, critical_only,
                                                               lighting=lighting)}]
        specs = self.registry.specs(offered)
        calls = replies = 0
        error = None
        context_full = False
        # fix round after P3: the next prompt is budgeted against the served context (module docstring); part 2: the
        # answer budget is the model's max_tokens (DEFAULT_MAX_TOKENS, 4096), lowered to the room left
        window = ContextBudget(getattr(self.model, "max_model_len", None),
                               int(getattr(self.model, "max_tokens", 0) or DEFAULT_MAX_TOKENS), specs)
        done = [False] * len(checklist)
        closed = [False] * len(checklist)          # fix round after P4a: refused twice by the memory
        refused_targets: set = set()               # fix round after P5: targets refused without validation
        stale_refusals = 0
        ended_by_refusals = False
        try:
            while calls < self.calls_per_room and state.finished is None and not ended_by_refusals \
                    and not all([d or c for d, c in zip(done, closed)] or [False]) and not budget.empty():
                if cap_at is not None and replies and self.clock() > cap_at:
                    break
                if replies and not self.time_ok():
                    break
                replies += 1
                prune_images(messages)
                ask = window.fit(messages)
                try:
                    try:
                        reply = self.model.chat(messages, specs, call_id=f"{tag}-p{replies}", max_tokens=ask)
                    except ContextFullError as exc:
                        # the server's own count: cut everything but the latest reply and ask once more
                        window.measured(messages, getattr(exc, "prompt_tokens", None))
                        ask = window.fit(messages, force=True)
                        reply = self.model.chat(messages, specs, call_id=f"{tag}-p{replies}-cut", max_tokens=ask)
                except ContextFullError:
                    context_full = True            # like a used-up budget: the session ends, no model error
                    break
                except ModelError as exc:
                    error = str(exc)
                    break
                window.measured(messages, (reply.usage or {}).get("prompt_tokens"))
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
                                    if not done[k] and step_done(step, tc.name, tc.parsed or {}, result,
                                                                 findings=ctx.findings):
                                        done[k] = True
                            elif result.get("step_closed"):
                                # fix round after P4a: the memory refused this edit twice in the session; fix round
                                # after P4b: or the code's fix_fixture search found no valid spot; fix round after
                                # P5: or the target used its tries (every step on it closes)
                                spent = result.get("max_tries_target")
                                for k, step in enumerate(checklist):
                                    if not done[k] and (step_hit(step, tc.name, tc.parsed or {}, result)
                                                        or (spent is not None and step.get("target") == spent)):
                                        closed[k] = str(result.get("closed_why")
                                                        or "the memory refused its edit twice")
                            # fix round after P5 (module docstring): refusals in a row on refused targets end it
                            if TL.refused_unvalidated(result):
                                stale_refusals = stale_refusals + 1 if target in refused_targets else 0
                                refused_targets.add(target)
                            else:
                                stale_refusals = 0
                            if stale_refusals >= REFUSALS_END_SESSION:
                                ended_by_refusals = True
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_result_text(result)})
                if state.pending_images:
                    shown = state.pending_images[-MAX_IMAGES:]
                    labels = [f"Image from a tool: {Path(p).name}" for p in shown]
                    messages.append(user_message("The images the tools returned, newest last.", shown, labels))
                    state.pending_images.clear()
        finally:
            open_steps = [(f"{s['tool']} on {s['target']}: {s.get('why', '')}"[:180]
                           + (f" [closed: {c if isinstance(c, str) else 'the memory refused its edit twice'}]"
                              if c else ""))
                          for s, d, c in zip(checklist, done, closed) if not d]
            open_steps += [str(x) for x in ((state.finished or {}).get("open_findings") or [])]
            self.memory.set_open(room_id, open_steps)
            ctx.end_session()
        if ended_by_refusals:
            # fix round after P5: the session sent edits the tools had refused already (logged)
            self.log.event("check", round_no, source="code", tool=REFUSALS_CHECK, target=room_id,
                           call_id=f"{tag}-p{replies}", status="session_end", model=self.log.model,
                           revision=self.log.revision,
                           note=(f"{REFUSALS_END_SESSION} edits in a row were refused without validation on targets "
                                 f"refused before in this session "
                                 f"({', '.join(sorted(map(str, refused_targets)))[:200]}): the session ends"),
                           counts={"refused_targets": len(refused_targets), "calls": calls})
        if context_full or window.cuts:
            # fix round after P3: what the context budget cut, and a session ended by a full context (logged)
            self.log.event("check", round_no, source="code", tool=CONTEXT_CHECK, target=room_id,
                           call_id=f"{tag}-p{replies}",
                           status="context_full" if context_full else "cut", model=self.log.model,
                           revision=self.log.revision,
                           note=("the conversation no longer fit the model's context after cutting the old tool "
                                 "results: the session ends like a used-up budget" if context_full else
                                 "old tool results cut to fit the model's context"),
                           counts={"cuts": len(window.cuts),
                                   "chars_removed": sum(int(c["chars_removed"]) for c in window.cuts),
                                   "max_model_len": getattr(self.model, "max_model_len", None)})
        return {"room_id": room_id, "calls": calls, "replies": replies, "error": error, "plan_ok": plan_ok,
                "steps": len(checklist), "steps_done": sum(done), "steps_closed": sum(1 for c in closed if c),
                "seconds": round(self.clock() - t0, 2), "context_full": context_full,
                "ended_by_refusals": ended_by_refusals}

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
        rendered = self.rendered_building(ctx)
        # fix round after P4b, decision 1: a placement finding on a replayed (set 1) camera is report-only
        CS.mark_replayed(code.get("findings") or [], ctx.cameras())
        for f in code.get("findings") or []:
            f["cause"] = CS.cause_of(f, rendered)
        ctx.violations = list(code.get("findings") or [])
        vision = self.run_vision_critic(ctx, code, round_no)
        # Milestone 13: the vision critic's findings are work only where a tool exists for the cause
        kept = []
        CS.mark_replayed(vision.get("kept") or [], ctx.cameras())
        for f in list(vision.get("kept") or []):
            f["cause"] = CS.cause_of(f, rendered)
            if CS.tools_for_finding(f):
                kept.append(f)
            elif CS.REPORT_TO.get(f["cause"]):
                # fix round after P4a: a finding the critic re-routed to another stage (a light fixture's look) is
                # reported like a code finding (not_yours, report_to), not dropped
                kept.append(f)
            else:
                vision.setdefault("dropped", []).append(dict(f, dropped=f"no agent tool for the cause "
                                                                         f"{f['cause']}: {CS.no_tool_reason(f)}"))
        vision["kept"] = kept
        self.log_findings(round_no, code, vision)
        found = list(code.get("findings") or []) + list(vision.get("kept") or [])
        ctx.findings = found
        wanted = ("critical",) if critical_only else ("critical", "major")
        # fix round after P4a: the final round also lights a view one set_lighting clears, when a re-render follows
        lighting = bool(final and critical_only and FINAL_ROUND_LIGHTING and self.rerun is not None)
        open_ = [f for f in found if is_wanted(f, wanted, lighting)]
        summary = {"round": round_no, "final": final, "findings": {s: sum(1 for f in found if f["severity"] == s)
                                                                    for s in P.SEVERITIES},
                   "dropped": len(vision.get("dropped") or []), "accepted": 0, "rejected": 0, "calls": 0,
                   "schema_errors": 0, "rerun_from": None, "views": [], "stop": None,
                   "rooms_code": len(ctx.building.get("rooms") or []),
                   "rooms_vision": sorted({c.get("target") for c in vision.get("checks") or []
                                           if c.get("target") in {r.get("id") for r in ctx.building.get("rooms")
                                                                   or []}}),
                   "rooms_planner": [], "rooms_fixable": [], "unfixable_open": 0, "sessions": 0, "plans_ok": 0,
                   "refused_repeats": 0, "dry_runs": 0, "findings_removed": 0, "context_full": 0,
                   "camera_no_effect": 0}
        self.rounds.append(summary)
        if not open_:
            summary["stop"] = "no_finding"
            return self._end_round(summary, t0)
        sessions, coverage = self.sessions_for(ctx, found, wanted, lighting=lighting)
        summary.update(rooms_fixable=coverage["fixable_rooms"], unfixable_open=coverage["unfixable_open"])
        if not sessions:
            summary["stop"] = "no_fixable"
            return self._end_round(summary, t0)
        plan = self.plan(ctx, round_no, sessions, critical_only, lighting=lighting)
        removed = sum(int(((a.get("result") or {}).get("acceptance") or {}).get("removed") or 0)
                      for a in ctx.accepted)
        self.findings_removed += removed
        summary.update(calls=plan["calls"], schema_errors=plan["schema_errors"], accepted=len(ctx.accepted),
                       rejected=len(ctx.rejected), rooms_planner=plan["rooms"], sessions=plan["sessions"],
                       plans_ok=plan["plans_ok"], refused_repeats=ctx.refused_repeats, dry_runs=ctx.dry_runs,
                       findings_removed=removed, context_full=int(plan.get("context_full") or 0))
        if plan["error"] and not ctx.accepted:
            summary["stop"] = "model_error"
            return self._end_round(summary, t0)
        if plan.get("context_full") and not ctx.accepted:
            # fix round after P3: the model answered; a conversation outgrew the context (not "did not answer")
            summary["stop"] = "context_full"
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
        if status in ("ok", "reused", "warning"):
            summary["camera_no_effect"] = self.check_camera_effects(round_no, ctx.accepted)
        if status not in ("ok", "reused", "warning", "skipped"):
            summary["stop"] = "rerun_failed"
        return self._end_round(summary, t0)

    def check_camera_effects(self, round_no: int, accepted: list[dict]) -> int:
        """Fix round after P4a: the accepted camera edits of the round against the rebuilt scene manifest
        (``camera_effects``), one ``camera_effect`` check event per edit; the number with no effect."""
        edits = [a for a in accepted if a.get("tool") in CAMERA_POSE_TOOLS]
        if not edits:
            return 0
        scene = TL.read_json(self.project_out / "scene" / "scene_manifest.json")
        if scene is None:
            return 0
        n = 0
        for rec in camera_effects(scene, edits):
            n += rec["status"] == "no_effect"
            self.log.event("check", round_no, source="code", tool=CAMERA_EFFECT_CHECK, target=rec["view_id"],
                           status=rec["status"], note=rec["note"], counts={"cameras": rec["cameras"]},
                           evidence={"override": rec["override"], "poses": rec["poses"]})
        return n

    def _end_round(self, summary: dict, t0: float) -> dict:
        summary["seconds"] = round(self.clock() - t0, 1)
        self.log.event("round", summary["round"], status=summary["stop"] or "done", seconds=summary["seconds"],
                       counts={k: summary.get(k) for k in ("accepted", "rejected", "calls", "schema_errors",
                                                           "dropped", "rooms_code", "sessions", "plans_ok",
                                                           "refused_repeats", "dry_runs", "unfixable_open",
                                                           "findings_removed", "context_full", "camera_no_effect")},
                       evidence={"findings": summary["findings"], "rooms_vision": summary["rooms_vision"],
                                 "rooms_planner": summary["rooms_planner"],
                                 "rooms_fixable": summary["rooms_fixable"], "final": summary["final"]})
        self.save()
        # fix round after P3: the dry re-checks' count is a prediction (the next round's critics measure it)
        self.out(f"agent round {summary['round']}: findings {summary['findings']}, findings removed "
                 f"{summary['findings_removed']} (predicted by the dry re-check), accepted {summary['accepted']}, "
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
        # fix round after P3: the measured number (the next round's critics) leads; the dry re-checks' is "predicted"
        measured = self.measured_removed()
        accepted = sum(r["accepted"] for r in self.rounds)
        self.log.event("stop", last, reason=STOPS[stop], status=stop,
                       note=f"{measured['total']} findings removed by {accepted} accepted edits in "
                            f"{len(self.rounds)} rounds (measured by the next round's critics; the dry re-checks "
                            f"predicted {self.findings_removed})",
                       counts={"findings_removed": measured["total"],
                               "findings_removed_predicted": self.findings_removed, "accepted": accepted})
        self.save()
        return self.summary()

    def measured_removed(self) -> dict:
        """Fix round after P3: ``{"total", "per_round"}`` of this run: the critical / major findings of a round that
        the next round's critics no longer found (``metrics.findings_removed_metrics``, the success number); zeros
        when the log cannot be read."""
        try:
            from wenart.agent import metrics as MX
            got = MX.compute(self.log.data()).get("findings_removed") or {}
            return {"total": int(got.get("total") or 0), "per_round": dict(got.get("per_round") or {})}
        except Exception:  # noqa: BLE001 - the numbers never stop the loop
            return {"total": 0, "per_round": {}}

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
        """The loop's summary. Fix round after P3: ``findings_removed`` is the measured number (``measured_removed``;
        the scheduler's "N finding(s) removed" line), ``findings_removed_predicted`` the dry re-checks' sum."""
        measured = self.measured_removed()
        return {"rounds": list(self.rounds), "stop": self.stop,
                "accepted": sum(r["accepted"] for r in self.rounds),
                "rejected": sum(r["rejected"] for r in self.rounds),
                "findings_removed": measured["total"],
                "findings_removed_per_round": measured["per_round"],
                "findings_removed_predicted": sum(int(r.get("findings_removed") or 0) for r in self.rounds),
                "log": str(self.log.dir / LG.LOG_JSON)}
