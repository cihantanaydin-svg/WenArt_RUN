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
                            *CS.LIGHTING_CHECKS})


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


def after_findings(code_after: list[dict], before: list[dict], changed: set, building_after: Optional[dict] = None
                   ) -> list[dict]:
    """The finding list after an edit for ``accept_edit`` (module docstring): the code critic's findings on the
    changed building (``code_after``) without the ``NOT_REMEASURED`` ones, plus the ``NOT_REMEASURED`` and vision
    findings of ``before`` whose target the edit did not change (a vision finding on a changed target is re-judged
    after the re-render; a ``NOT_REMEASURED`` one is re-measured by the next round, except a ``lighting_dark`` view the
    edit's room light cannot clear, ``lighting_kept``). Every finding gets its ``cause``.

    Review of 16 Oct 2026: the ``NOT_REMEASURED`` findings come from ``before``, not from ``code_after``. The dry
    re-check rebuilds them from the round's scene and render manifests, which no edit changes, so a finding an
    earlier edit of the round had removed came back on the next edit as a new one (a new critical finding rejected an
    unrelated edit), and the lighting metrics were recomputed against factors the render had not used."""
    out = []
    for f in code_after:
        if f.get("check") in NOT_REMEASURED:
            continue
        out.append(dict(f, cause=f.get("cause") or CS.cause_of(f, building_after)))
    for f in before:
        if f.get("source") == "vision":
            if f.get("target") not in changed:
                out.append(dict(f, cause=f.get("cause") or CS.cause_of(f, building_after)))
            continue
        if f.get("check") not in NOT_REMEASURED:
            continue
        if f.get("target") in changed:
            kept = lighting_kept(f, building_after) if f.get("check") in CS.LIGHTING_CHECKS else None
            if kept is not None:
                out.append(dict(kept, cause=kept.get("cause") or CS.cause_of(kept, building_after)))
            continue
        out.append(dict(f, cause=f.get("cause") or CS.cause_of(f, building_after)))
    return out


def default_checklist(brief: dict, wanted=("critical", "major")) -> list[dict]:
    """One step per fixable finding of the wanted severities: its first tool on its target (the room for a finding
    without a piece target)."""
    room_id = brief["room"]["id"]
    groups = [g for g in brief.get("groups") or [] if g.get("group_id")]
    steps = []
    for f in (brief.get("findings") or {}).get("fixable") or []:
        if f.get("severity") not in wanted:
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
                 groups_fn: Optional[Callable] = None, scene_dir=None, recheck: Optional[Callable] = None,
                 acceptance: bool = True):
        self.project_out = Path(project_out)
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
        return TL.ToolContext.load(self.project_out, round=round_no, model_id=getattr(self.model, "model", ""),
                                   log=self.log, overrides=self.overrides,
                                   preview_dir=preview_dir or self.preview_dir, apply_edit=self.apply_edit,
                                   validators=self.validators, plausibility=self.plausibility,
                                   catalog_loader=self.catalog_loader, max_tries=self.max_tries, memory=self.memory,
                                   level_edit=self.level_edit, level_checks=self.level_checks, sync=self.sync,
                                   brief_fns=self.brief_fns, acceptance=self.acceptance if self.use_acceptance else None)

    # ----- acceptance (Milestone 13) ------------------------------------------------------------------

    def code_findings(self, building: dict, ctx: TL.ToolContext, manifest: Optional[dict]) -> list[dict]:
        """The code critic's findings of ``building`` (the dry re-check: ``recheck`` when injected, else the code
        critic of the round, else ``critic_code.run`` with the same functions as ``run_code_critic``)."""
        if self.recheck is not None:
            got = self.recheck(building, ctx.scene, manifest)
        elif self.code_critic is not None:
            got = self.code_critic(building, ctx.scene, manifest)
        else:
            got = CC.run(building, ctx.scene, manifest, scene_dir=self.scene_dir or CC.scene_checks_dir(self.project_out),
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
        code_after = self.code_findings(building_after, ctx, self.render_manifest(ctx.preview_dir))
        after = after_findings(code_after, before, changed, building_after)
        # round 4: the pieces the edit took out of the scene, for the acceptance's room-set rule (a fixture removed)
        edit = {"target_finding": [{"check": f.get("check"), "target": f.get("target")} for f in targets],
                "penalty_before": result.get("penalty_before"), "penalty_after": result.get("penalty_after"),
                "score_before": result.get("score_before"), "score_after": result.get("score_after"),
                "removed": CS.removed_pieces(ctx.building, building_after)}
        ok, reason = accept_edit(before, after, edit)
        room = TL.edit_room(ctx, args)
        scope = set(changed) | {f.get("target") for f in targets}

        def mine(f: dict) -> bool:
            return f.get("room_id") == room or f.get("target") in scope or (room == BUILDING and not f.get("room_id"))

        carried = sorted({f"{f['check']}:{f.get('target')}" for f in after
                          if f.get("target") in changed and (f.get("source") == "vision"
                                                             or f.get("check") in NOT_REMEASURED)})
        note = None
        if ok and any(f.get("target") in changed and (f.get("source") == "vision" or f.get("check") in NOT_REMEASURED)
                      for f in before):
            note = "findings the dry re-check cannot measure on the changed target (scene, view, look or vision) " \
                   "count as gone and are re-measured by the next round"
        return {"accepted": ok, "reason": reason, "target": [f"{f.get('check')}:{f.get('target')}" for f in targets],
                "target_findings": targets, "before": CS.key_list([f for f in before if mine(f)]),
                "after": CS.key_list([f for f in after if mine(f)]), "removed": findings_removed(before, after),
                "after_findings": after, "note": note, "carried": carried}

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
                                               plan_crop=None, code=code, call_id=call_id, camera=ctx.camera(key))
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

    def sessions_for(self, ctx: TL.ToolContext, found: list[dict], wanted: tuple) -> tuple[list[dict], dict]:
        """``(sessions, coverage)``: one session per room (and one for the building) with a fixable finding of the
        wanted severities, in the order of the module docstring; ``coverage`` lists the rooms with fixable findings
        and how many open findings are not fixable."""
        open_ = [f for f in found if f["severity"] in wanted]
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
        """The tools offered to one session (``offered_tools``)."""
        return offered_tools(self.registry, brief)

    # ----- planner -------------------------------------------------------------------------------

    def plan(self, ctx: TL.ToolContext, round_no: int, sessions: list[dict], critical_only: bool = False) -> dict:
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
            total["context_full"] += 1 if res.get("context_full") else 0
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
        state.checklist = list(checklist)          # Milestone 13: the steps name the findings an edit targets
        findings = item["fixable"] + [f for f in ctx.findings if f.get("room_id") == room_id]
        messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                    {"role": "user", "content": P.session_task(round_no, brief, checklist, problems,
                                                               self.calls_per_room, critical_only)}]
        specs = self.registry.specs(offered)
        calls = replies = 0
        error = None
        context_full = False
        # fix round after P3: the next prompt is budgeted against the served context (module docstring); part 2: the
        # answer budget is the model's max_tokens (DEFAULT_MAX_TOKENS, 4096), lowered to the room left
        window = ContextBudget(getattr(self.model, "max_model_len", None),
                               int(getattr(self.model, "max_tokens", 0) or DEFAULT_MAX_TOKENS), specs)
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
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_result_text(result)})
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
                "steps": len(checklist), "steps_done": sum(done), "seconds": round(self.clock() - t0, 2),
                "context_full": context_full}

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
        for f in code.get("findings") or []:
            f["cause"] = CS.cause_of(f, rendered)
        ctx.violations = list(code.get("findings") or [])
        vision = self.run_vision_critic(ctx, code, round_no)
        # Milestone 13: the vision critic's findings are work only where a tool exists for the cause
        kept = []
        for f in list(vision.get("kept") or []):
            f["cause"] = CS.cause_of(f, rendered)
            if CS.tools_for_finding(f):
                kept.append(f)
            else:
                vision.setdefault("dropped", []).append(dict(f, dropped=f"no agent tool for the cause "
                                                                         f"{f['cause']}: {CS.no_tool_reason(f)}"))
        vision["kept"] = kept
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
                   "refused_repeats": 0, "dry_runs": 0, "findings_removed": 0, "context_full": 0}
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
        if status not in ("ok", "reused", "warning", "skipped"):
            summary["stop"] = "rerun_failed"
        return self._end_round(summary, t0)

    def _end_round(self, summary: dict, t0: float) -> dict:
        summary["seconds"] = round(self.clock() - t0, 1)
        self.log.event("round", summary["round"], status=summary["stop"] or "done", seconds=summary["seconds"],
                       counts={k: summary.get(k) for k in ("accepted", "rejected", "calls", "schema_errors",
                                                           "dropped", "rooms_code", "sessions", "plans_ok",
                                                           "refused_repeats", "dry_runs", "unfixable_open",
                                                           "findings_removed", "context_full")},
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
