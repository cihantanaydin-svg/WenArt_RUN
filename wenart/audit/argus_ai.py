"""Argus AI: the open-weight agent model thinks over everything the audit found and acts (26 Oct 2026, user: "use open
weight AI models for this auditor, it needs to be smart, it needs to solve the problems even without me telling it
... think outside the box").

What: ``investigate(project_out, model)`` runs on the pod after a build (and again at the end of the run):

1. **The case file.** Argus's code lines run (``report.run``: conservation, process, the model review, the inspector,
   the judge, the ledger and the plan-vs-model lines when present); the project's facts are written as lines (levels,
   rooms with labels, types, areas, doors and windows, pieces; the site's labelled areas and symbols and whether they
   are built; the warnings by rule).
2. **Triage** (``TRIAGE_BATCH`` findings per call, every finding: no cap). The agent model (Qwen3.8-27B, Apache-2.0,
   thinking off (measured: see THINKING), temperature 0, strict JSON schema) says per finding whether it is a real
   problem, its kind, the stage
   that caused it, and the fix: an architect action on one element (``FIX_ARCH``: the AI architect's typed actions),
   ``agent_round`` (the furniture agent's next round works on it), ``rerun_stage``, ``rule_needed`` (no fix in this
   run: it writes the general rule that would prevent the kind in every project) or ``not_a_problem``. The "not built:
   <reason>" notes (conservation C6) are judged too: a reason that hides a loss becomes a finding (``AI2``).
3. **Discovery** (one call per floor, with the floor's top-down view of the model when there is one): what no line
   named yet: what the documents hold that the model lacks, what makes no sense to a visitor or an architect, what a
   client would not accept. Code keeps a claim only when its target is an element id, a room or site label or a level
   of the facts (``AI1``; an unverifiable claim is logged and dropped).
4. **Action.** The architect actions go through the AI architect's checked path (``architect_ai._decision`` then
   ``_verdicts``: carried out, no new major question, the model review no worse) and, on top, Argus's own dry
   re-check: the finding it targets must be gone in the code lines run on the prepared building
   (``target_gone``); the accepted ones join ``orchestrator/architect_answers.json`` (the next build carries them
   out). ``agent_round`` findings go to the agent's work list (``work``, read by ``wenart.agent.loop``). The rules go
   to ``guards`` (the problem log and the report's prevention list; they become code or lessons between runs).
5. Everything is logged in ``orchestrator/argus_ai.json`` and ``argus_ai.md``: each verdict, decision (accepted or
   refused, with the reason), new finding, disputed finding and rule.

Why: CLAUDE.md: the AI chooses, code carries out and checks; "findings removed" is the measure. The code lines see what
they were written for; the model reads the whole case and finds the cause behind many symptoms, the reason that hides
a loss, and the problem nobody wrote a check for.
"""
from __future__ import annotations

import copy
import json
import re
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.audit import conservation as CV
from wenart.audit import inputs as I
from wenart.audit import calls as CL
from wenart.audit import kinds as K
from wenart.audit import report as R

PLAN_JSON = "plan_vs_model.json"          # the documents-vs-model line's record (``report.LINE_FILES`` reads it)
CHANGE_KIND = {"missing_in_model": "lost", "different_in_model": "misread", "extra_in_model": "misread"}
LOG_JSON = "argus_ai.json"
LOG_MD = "argus_ai.md"
FINAL_JSON = "argus_ai_final.json"       # the end of the run (``act_on`` False): the record of the first pass stays
FINAL_MD = "argus_ai_final.md"
TRIAGE_BATCH = 16              # findings per triage call (every finding is triaged: the batches cover them all)
# Pod run 20261026-195707 (real06): with thinking on, 19 of 20 triage calls thought until the 12,000-token cap at
# about 45 tokens/s and returned no JSON ("not JSON: Expecting value"), and Argus used the hour the agent's rounds
# needed. The calls are structured (a strict schema, a "why" per item): thinking off, as the critic; a call that still
# comes back empty is asked once more (the client's second try).
THINKING = False
MAX_TOKENS = 4096              # per call: the JSON of one batch (about 120 tokens a finding)
WORKERS = 4                    # calls at once (the agent server's --max-num-seqs 4)
BUDGET_S = 900                 # one investigation at most (the documents line, the triage, the discovery)
CYCLE_BUDGET_S = 420           # an investigation before a big-loop cycle (no documents line)
DISCOVER_MAX = 15              # new findings per floor per call
FACT_LINES = 140               # project fact lines in the case file
MESSAGE_CHARS = 320
CAUSES = ("reading", "recognition", "fit", "layout", "decor", "agent", "architect", "site", "roof", "build",
          "cameras", "render", "library", "scheduler", "unknown")
FIX_ARCH = ("door_to_window", "french_window", "raise_sill", "widen_door", "interior_glazing", "high_window",
            "pass_through", "gap_to_door", "window_to_door", "snap_threshold", "retype_room", "enlarge_windows",
            "move_piece", "mount_fixture", "remove_piece")
FIX_OTHER = ("agent_round", "rerun_stage", "rule_needed", "not_a_problem")
# 26 Oct 2026 (user: "make Argus fix everything itself, give it more power"): the agent's edit tools Argus may call
# itself (23; the loop runs them in Argus's session through the same registry, validators and acceptance:
# ``argus_session``)
AGENT_TOOLS = ("retype_piece", "swap_model", "place_group", "complete_group", "relayout_room", "set_room_type",
               "mark_not_furniture", "fix_fixture", "set_front", "resize_piece", "move_group", "rotate_piece",
               "set_camera", "remove_camera",
               # building-wide: Argus's session is the building session (the geometry, the exterior, the looks, the
               # levels and the entrances; each with its own validators)
               "correct_geometry", "set_exterior", "set_material", "add_camera", "set_room_floor",
               "set_ground_point", "set_entrance", "set_terrain", "set_mark_kind")
TOOL_CAUSE = {"retype_piece": "wrong_type", "swap_model": "wrong_model", "place_group": "missing_member",
              "complete_group": "missing_member", "relayout_room": "clearance", "set_room_type": "room_type",
              "mark_not_furniture": "untyped", "fix_fixture": "fixture_place", "set_front": "orientation",
              "resize_piece": "size", "move_group": "group_layout", "rotate_piece": "orientation",
              "set_camera": "interior_camera", "remove_camera": "interior_camera", "correct_geometry": "geometry",
              "set_exterior": "site", "set_material": "material", "add_camera": "exterior_camera",
              "set_room_floor": "levels", "set_ground_point": "levels", "set_entrance": "entrance",
              "set_terrain": "terrain", "set_mark_kind": "levels"}
PIECE_TOOLS = ("retype_piece", "swap_model", "mark_not_furniture", "fix_fixture", "set_front", "resize_piece",
               "rotate_piece")
ROOM_TOOLS = ("place_group", "relayout_room", "set_room_type")
FIXES = FIX_ARCH + AGENT_TOOLS + FIX_OTHER
HISTORY_FILE = Path(__file__).resolve().parents[2] / "results" / "argus" / "problem_log.json"
HISTORY_LINES = 30             # earlier runs' recurring problems and learned rules put to the model
SYSTEM = (
    "You are Argus, the auditor of an automated pipeline that turns an architect's drawings (DWG or PDF plans, "
    "sections, elevations) into a furnished 3D house and photoreal renders. You check everything, not only the "
    "looks: what the documents hold against what the model builds, whether the house makes sense to a visitor and "
    "to an architect, and whether the run did its job. Code checks found the findings you are given; the facts are "
    "the project as built.\n"
    "Rules:\n"
    "- Think about the cause, not the symptom: many findings often have one cause (a misread wall, a missing rule); "
    "name the stage that caused it.\n"
    "- A finding is real unless the facts show it is a false alarm; then fix = not_a_problem and say why.\n"
    "- Fix it yourself whenever a tool can: choose an agent tool and give its arguments as a JSON object in args "
    "(e.g. {\"piece_id\": \"f_L1_011\", \"type\": \"bathtub\"}); you carry it out through the same code checks as "
    "the agent, so a wrong edit is refused, never built. Or an architect action on one element (the element id, and a "
    "value when the action needs one, e.g. a room type); agent_round (the furniture agent's next round decides); "
    "rerun_stage; or rule_needed when nothing in this run can fix it: then write the general rule (one or two "
    "sentences, for every project, never for this one only) that would prevent this kind of problem.\n"
    "- Prefer the fix of the cause: retype a misread piece rather than move its neighbours, build the missing piece "
    "of a room's set, swap the model that does not match its set, set the camera that shows a bare wall.\n"
    "- A finding with tried_and_refused lists edits code refused this run, with the reason: never repeat one; choose "
    "another tool or other arguments that answer the reason, or rule_needed when no tool can.\n"
    "- 'not built: <reason>' lists elements a stage left out and the reason it gave, and 'gone after the ... stage, "
    "named in ...' an element a stage dropped and the record that names it: real = true when the reason hides a loss "
    "(something the documents show that the house should have), false when it is a good reason.\n"
    "- Use only element ids, labels and levels from the facts. Never invent one.")
DISCOVER_SYSTEM = SYSTEM + (
    "\n- Now look beyond the findings: list problems no finding names yet: what the documents hold that the model "
    "lacks (a labelled terrace, balcony or veranda, drawn trees or hedges, a room, a door), what makes no sense (a "
    "room with no door, a bathroom only reachable through a bedroom of another flat, stairs that arrive nowhere, a "
    "window inside the house, a kitchen with no worktop), and what a client would not accept. Each with its target "
    "(an element id, a room or site label, or a level id from the facts).")


def triage_schema(ids: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["items"],
            "properties": {"items": {"type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["id", "real", "severity", "kind", "cause", "fix", "element", "value", "args", "rule",
                             "why"],
                "properties": {"id": {"type": "string", "enum": ids},
                               "real": {"type": "boolean"},
                               "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                               "kind": {"type": "string", "enum": list(K.KINDS)},
                               "cause": {"type": "string", "enum": list(CAUSES)},
                               "fix": {"type": "string", "enum": list(FIXES)},
                               "element": {"type": "string"},
                               "value": {"type": "string"},
                               "args": {"type": "string"},
                               "rule": {"type": "string"},
                               "why": {"type": "string", "minLength": 5}}}}}}


def discover_schema() -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["found"],
            "properties": {"found": {"type": "array", "maxItems": DISCOVER_MAX, "items": {
                "type": "object", "additionalProperties": False,
                "required": ["target", "kind", "severity", "what", "cause", "fix", "element", "value", "args", "rule"],
                "properties": {"target": {"type": "string", "minLength": 2},
                               "kind": {"type": "string", "enum": list(K.KINDS)},
                               "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                               "what": {"type": "string", "minLength": 5},
                               "cause": {"type": "string", "enum": list(CAUSES)},
                               "fix": {"type": "string", "enum": list(FIXES)},
                               "element": {"type": "string"},
                               "value": {"type": "string"},
                               "args": {"type": "string"},
                               "rule": {"type": "string"}}}}}}


# ---------------------------------------------------------------------------------------------------- the case file
def _area(r: dict) -> float:
    try:
        from wenart.blender import architect_actions as AA
        return float(AA.room_area(r))
    except Exception:  # noqa: BLE001
        return float(r.get("area_computed") or r.get("area") or 0.0)


def facts(building: dict, rep: Optional[dict] = None, limit: int = FACT_LINES) -> list[str]:
    """The project as built, one line per fact (pure)."""
    b = building or {}
    lines = [f"levels: " + ", ".join(f"{lv.get('id')} at {float(lv.get('elevation') or 0):.2f} m"
                                     for lv in b.get("levels") or [])]
    ops = b.get("openings") or []
    furn = [f for f in b.get("furniture") or [] if f.get("build") is not False]
    for r in b.get("rooms") or []:
        doors = [o["id"] for o in ops if o.get("type") == "door" and r["id"] in (o.get("rooms") or ())]
        pieces = sorted({str(f.get("type")) for f in furn if f.get("room_id") == r["id"]})
        lines.append(f"room {r['id']} '{r.get('label') or r.get('name') or ''}' on {r.get('level_id')}: "
                     f"{r.get('room_type')}, {_area(r):.1f} m2" + (f", doors {', '.join(doors)}" if doors else "")
                     + (f"; pieces: {', '.join(pieces)}" if pieces else "; no pieces"))
    by_level: dict = {}
    for o in ops:
        by_level.setdefault((o.get("level_id"), o.get("type")), []).append(o["id"])
    lines += [f"{t}s on {lv}: {', '.join(ids)}" for (lv, t), ids in sorted(by_level.items(), key=str)]
    site = b.get("site") or {}
    for a in site.get("areas") or []:
        lines.append(f"site area {a.get('id')} '{a.get('label') or ''}' ({a.get('kind')}): "
                     + ("built" if a.get("build") is not False and a.get("polygon") else
                        f"NOT built ({a.get('not_built_reason') or 'no outline'})"))
    kinds: dict = {}
    for d in site.get("decor") or []:
        kinds[str(d.get("kind"))] = kinds.get(str(d.get("kind")), 0) + 1
    if kinds:
        lines.append("site symbols drawn: " + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())))
    for key in ("trees", "pools", "platforms"):
        if site.get(key):
            lines.append(f"site {key}: {len(site[key])}")
    roof = b.get("roof") or {}
    if roof:
        lines.append(f"roof: {roof.get('kind') or roof.get('type')}, ridge {roof.get('ridge_height')}")
    if rep and rep.get("warning_counts"):
        lines.append("warnings by rule: " + ", ".join(f"{k} {v}" for k, v in sorted(rep["warning_counts"].items())))
    return lines[:limit]


def known_targets(building: dict) -> dict:
    """``{lower-case name: canonical}`` of everything a claim may target: element ids, room and site labels, levels."""
    out = {"building": "building", "site": "site", "roof": "roof"}
    b = building or {}
    for coll, path in CV.COLLECTIONS:
        for el in CV._items(b, path):
            out[str(el["id"]).lower()] = el["id"]
            for k in ("label", "label_raw", "name"):
                if el.get(k):
                    out[str(el[k]).lower()] = el["id"]
    for lv in b.get("levels") or []:
        if lv.get("id"):
            out[str(lv["id"]).lower()] = lv["id"]
    return out


def items_of(rep: dict) -> list[dict]:
    """The findings put to triage: every open one (critical, major, minor), the not-built notes (C6) and every warning
    no rule knows (``P0``: Argus reads them all; the batches cover any number)."""
    from wenart.audit import process as PR

    order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    rows = [f for f in rep.get("findings") or [] if f.get("severity") != "info" or f.get("check") in ("C1", "C6")]
    rows += [K.finding("process", "P0", "info", PR._target(w), f"a warning no rule knows: {w}", owner="process",
                       kind="other") for w in rep.get("unmatched_warnings") or []]
    rows.sort(key=lambda f: (order.get(f.get("severity"), 4), str(f.get("kind"))))
    return [dict(f, aid=f"F{i}") for i, f in enumerate(rows, 1)]


def _item_text(f: dict) -> dict:
    out = {"id": f["aid"], "check": f"{f.get('line')}:{f.get('check')}", "severity": f.get("severity"),
           "kind": f.get("kind"), "target": str(f.get("target")), "what": str(f.get("message"))[:MESSAGE_CHARS],
           "owner": f.get("owner"), "code_fix": f.get("fix")}
    if f.get("tried"):
        out["tried_and_refused"] = f["tried"]
    if f.get("piece"):
        out["piece"] = f["piece"]
    if f.get("models"):
        out["models_it_may_take"] = f["models"]
    return out


def piece_notes(items: list[dict], valid: "CL.Valid") -> None:
    """27 Oct 2026: a finding on a piece carries the piece (type, size, room, model) and the catalogue models it may
    swap to (``Valid.model_options``), so a swap names a real model (pod run 224516: 13 invented model ids)."""
    for f in items:
        p = valid.pieces.get(str(f.get("target")))
        if not p:
            continue
        size = (p.get("footprint") or {}).get("size") or []
        asset = p.get("asset") if isinstance(p.get("asset"), dict) else {}
        f["piece"] = (f"{p.get('type')}" + (" %.2f x %.2f m" % tuple(size[:2]) if len(size) >= 2 else "")
                      + f" in {p.get('room_id')}" + (f", model {asset.get('asset_id')}" if asset.get("asset_id") else "")
                      + (", not built" if p.get("build") is False else ""))
        f["models"] = valid.model_options(p)


TRIED_MAX = 4                  # refused edits per target shown to the model


def tried_by_target(agent_log: Optional[dict]) -> dict:
    """``{target: ["tool: why refused", ...]}`` of this run's refused edits (the agent's and Argus's), so Argus does
    not try the same again: it picks another tool or another argument (``process._run_events``, ``_refusal``)."""
    from wenart.audit import process as PR

    out: dict = {}
    for e in PR._run_events(agent_log):
        if e.get("kind") != "rejected_edit" or not e.get("target"):
            continue
        line = f"{e.get('tool')}: {PR._refusal(e)[:140]}"
        lst = out.setdefault(str(e["target"]), [])
        if line not in lst and len(lst) < TRIED_MAX:
            lst.append(line)
    return out


# ---------------------------------------------------------------------------------------------------- the calls
def triage(model, items: list[dict], fact_lines: list[str], *, time_ok: Callable[[], bool] = lambda: True,
           out: Callable[[str], None] = print, errors: Optional[list] = None, project: str = "",
           tools: Optional[list] = None, values: Optional[list] = None) -> dict:
    """``{aid: verdict}`` for every item (module docstring 2); an item the model skipped has none (``errors`` gets
    what failed). ``tools``: the tool help (``_tool_help``), ``values``: the valid values (``calls.Valid.lines``)."""
    errors = errors if errors is not None else []
    verdicts: dict = {}
    batches = [items[s:s + TRIAGE_BATCH] for s in range(0, len(items), TRIAGE_BATCH)]
    history = history_lines(project)
    tools = _tool_help() if tools is None else tools
    values = values or []

    def one(n: int, batch: list[dict]):
        if not time_ok():
            return n, None, "time is up"
        start = n * TRIAGE_BATCH
        text = "\n".join(["The project as built:", *fact_lines, *history, "",
                          f"The findings ({start + 1}-{start + len(batch)} of {len(items)}):",
                          json.dumps([_item_text(f) for f in batch], indent=1, ensure_ascii=False), "",
                          "Agent tools (fix; their arguments go in args as one JSON object; * required):", *tools,
                          *values, "", "Architect actions (fix) and what they do: " + _arch_help()])
        try:
            reply = model.structured([{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
                                     triage_schema([f["aid"] for f in batch]), call_id=f"argus_triage_{n}",
                                     name="argus_triage", kind="task", thinking=THINKING, max_tokens=MAX_TOKENS)
        except Exception as exc:  # noqa: BLE001 - one batch that fails is logged; the others are still triaged
            return n, None, f"{type(exc).__name__}: {exc}"
        return n, reply, "; ".join(reply.errors[:2]) if reply.errors else None

    for n, reply, err in _parallel(one, batches):
        lo = n * TRIAGE_BATCH + 1
        if err:
            errors.append(f"triage {lo}-{lo + len(batches[n]) - 1}: {err}"[:300])
        for v in ((reply.data if reply is not None else None) or {}).get("items") or []:
            verdicts.setdefault(v["id"], v)
    if any(e.endswith("time is up") for e in errors):
        out(f"Argus AI: time is up before every finding was triaged ({len(verdicts)} of {len(items)})")
    return verdicts


def _parallel(fn, jobs: list) -> list:
    """``fn(n, job)`` for every job, ``WORKERS`` at once, in the jobs' order."""
    from concurrent.futures import ThreadPoolExecutor

    if len(jobs) <= 1 or WORKERS <= 1:
        return [fn(n, j) for n, j in enumerate(jobs)]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        return list(ex.map(lambda nj: fn(*nj), list(enumerate(jobs))))


def _registry():
    try:
        from wenart.agent import tools as TL
        return TL.build_registry()
    except Exception:  # noqa: BLE001 - no registry here: no tool help, no vetting
        return None


def _tool_help(reg=None) -> list[str]:
    """One line per agent tool Argus may call: every argument with its type, allowed values and range (``*``
    required) and what the tool does (``calls.tool_help``: 27 Oct 2026, the names alone gave 0 valid calls of 94)."""
    reg = reg if reg is not None else _registry()
    return CL.tool_help(reg, AGENT_TOOLS) if reg is not None else []


def history_lines(project: str, path: Path = HISTORY_FILE, limit: int = HISTORY_LINES) -> list[str]:
    """26 Oct 2026 (user: "give it more power"): what Argus learned in earlier runs (the problem log of the repository,
    ``report.update_log``): this project's recurring problems and the general rules proposed before, as prompt lines."""
    log = I.read_json(path) if Path(path).is_file() else None
    if not log:
        return []
    rec = R.recurring(log, project) if project else []
    lines = [f"- seen in {len(v['runs'])} runs: {s.split('|', 1)[-1]}: {str(v.get('message'))[:140]}"
             for s, v in rec[:limit]]
    rules = sorted((g for g in (log.get("guards") or {}).values() if g.get("rule")),
                   key=lambda g: -len(g.get("runs") or []))[:max(0, limit - len(lines))]
    lines += [f"- rule learned ({len(g.get('runs') or [])} runs): {str(g['rule'])[:200]}" for g in rules]
    return (["", "From earlier runs (fix the cause of what keeps coming back):"] + lines) if lines else []


def cause_for_tool(tool: str) -> Optional[str]:
    """A cause of ``causes.CAUSE_TOOLS`` that ``tool`` fixes (``TOOL_CAUSE`` first): the cause Argus's work finding
    carries, so the loop routes it to that tool and the edit may target it."""
    from wenart.agent import causes as CS
    c = TOOL_CAUSE.get(tool)
    if c in CS.CAUSE_TOOLS and tool in CS.CAUSE_TOOLS[c]:
        return c
    return next((c for c, ts in sorted(CS.CAUSE_TOOLS.items()) if tool in ts), None)


def parse_args(text: str, tool: str, target: str) -> tuple[Optional[dict], str]:
    """``(args, why_not)`` of the model's ``args`` text for an agent tool: a JSON object; the piece or room the
    finding names fills ``piece_id`` / ``room_id`` / ``view_id`` when the model left it out."""
    try:
        args = json.loads(text) if str(text or "").strip() else {}
    except ValueError as exc:
        return None, f"args are not JSON: {exc}"
    if not isinstance(args, dict):
        return None, "args are not a JSON object"
    t = str(target or "")
    if tool in PIECE_TOOLS and "piece_id" not in args and t.startswith("f_"):
        args["piece_id"] = t
    if tool in ROOM_TOOLS and "room_id" not in args and t.startswith("r_"):
        args["room_id"] = t
    if tool in ("set_camera", "remove_camera") and "view_id" not in args and t.startswith(("cam_", "ext_")):
        args["view_id"] = t
    return args, ""


def _action(aid: str, tool: str, args: dict, f: dict, why: str, source: str) -> tuple[dict, dict]:
    """``(action, work finding)``: the tool call Argus makes and the finding it fixes (critic format, id ``a:<aid>``,
    the tool's cause), which joins the round's findings so the edit has its target."""
    fid = f"a:{aid}"
    cause = cause_for_tool(tool)
    work = {"id": fid, "check": str(f.get("check") or "AI"), "severity": f.get("severity") if f.get("severity") in
            ("critical", "major") else "major", "target": args.get("piece_id") or args.get("room_id") or
            args.get("view_id") or f.get("target"), "room_id": args.get("room_id"), "view": None, "source": "argus",
            "message": f"Argus: {str(f.get('message') or '')[:300]}", "argus_cause": cause, "fix": "argus_tool"}
    act = {"id": f"{source}:{aid}:{tool}:{work['target']}", "tool": tool, "args": args, "finding_id": fid,
           "why": str(why or "")[:240], "source": source, "cause": cause}
    return act, work


def bath_or_shower(piece: dict) -> str:
    size = sorted(float(v) for v in ((piece.get("footprint") or {}).get("size") or [0, 0])[:2])
    return "bathtub" if size and size[-1] >= 1.40 else "shower"


def code_actions(rep: dict, building: dict) -> tuple[list[dict], list[dict], list[str]]:
    """The fixes Argus's code lines name exactly, as tool calls with no model (``(actions, work, revoke keys)``):
    the ledger's ``type_piece`` (a furniture name written beside an untyped piece), N5 (a room missing a piece of
    its set holds an untyped drawn piece: typed as that piece, a bath or a shower by its length; or a piece an AI
    decision took out: that decision is revoked)."""
    pieces = {f.get("id"): f for f in building.get("furniture") or []}
    actions, work, revoke = [], [], []
    for n, f in enumerate(rep.get("findings") or [], 1):
        fix = f.get("fix")
        if isinstance(fix, dict) and fix.get("action") == "type_piece" and fix.get("element_id") in pieces \
                and fix.get("type"):
            a, w = _action(f"c{n}", "retype_piece", {"piece_id": fix["element_id"], "type": fix["type"],
                                                     "reason": f"the plan names it: {f.get('message')}"[:300]},
                           f, f.get("message"), "code")
            actions.append(a)
            work.append(w)
        if f.get("check") == "N5" or "sense:N5" in (f.get("seen_by") or []):
            p = pieces.get(f.get("target")) or {}
            reason = str(p.get("not_built_reason") or "")
            m = re.search(r"answer to (AI\.[a-z_]+:[A-Za-z0-9_]+)", reason)
            if m:
                revoke.append(m.group(1))
                continue
            missing = str((f.get("evidence") or {}).get("missing") or "")
            if str(p.get("type")) in ("unknown", "other", ""):
                ftype = bath_or_shower(p) if missing == "shower|bathtub" else missing.split("|")[0]
                if ftype:
                    a, w = _action(f"c{n}", "retype_piece", {"piece_id": p["id"], "type": ftype,
                                                             "reason": f"the room misses its {ftype}: "
                                                                       f"{f.get('message')}"[:300]},
                                   f, f.get("message"), "code")
                    actions.append(a)
                    work.append(w)
    return actions, work, revoke


def revoke_decisions(project_out, keys: list[str]) -> list[dict]:
    """Take out decisions of the AI (``by`` ai or argus, never the user's or the architect's defaults) from
    ``orchestrator/architect_answers.json``: the next build no longer carries them out. ``[{key, done, why}]``."""
    from wenart.agent import architect_ai as AIA
    from wenart.agent import log as LG

    odir = LG.orchestrator_dir(Path(project_out))
    saved = dict(AIA._saved_answers(odir))
    out = []
    for key in dict.fromkeys(keys):
        ans = saved.get(key)
        if ans is None:
            out.append({"key": key, "done": False, "why": "not among the saved AI decisions"})
        elif ans.get("by") not in ("ai", "argus"):
            out.append({"key": key, "done": False, "why": f"decided by {ans.get('by')}: only the AI's are revoked"})
        else:
            saved.pop(key)
            out.append({"key": key, "done": True, "why": "it left a room without a piece of its set"})
    if any(r["done"] for r in out):
        AIA._save_answers(odir, saved)
    return out


def _arch_help() -> str:
    from wenart.blender import architect_actions as AA
    return "; ".join(f"{a} ({AA.ACTIONS.get(a, '')})" for a in FIX_ARCH)


def discover(model, inp: I.Inputs, rep: dict, fact_lines: list[str], *, time_ok: Callable[[], bool] = lambda: True,
             out: Callable[[str], None] = print, errors: Optional[list] = None, tools: Optional[list] = None,
             values: Optional[list] = None) -> tuple[list[dict], list[dict]]:
    """``(findings, dropped)`` of module docstring 3 (``tools``, ``values``: as ``triage``)."""
    from wenart.agent.model import user_message

    errors = errors if errors is not None else []
    tools = list(tools or [])
    values = list(values or [])
    building = inp.final or {}
    known = known_targets(building)
    named = sorted({f"{f.get('target')}: {str(f.get('message'))[:90]}" for f in rep.get("findings") or []
                    if f.get("severity") in ("critical", "major")})
    found, dropped = [], []
    levels = [lv.get("id") for lv in building.get("levels") or []] or [None]

    def one(_n: int, lv):
        if not time_ok():
            return lv, None, None, "time is up"
        image = next((p for p in inp.top_plans if lv and f"top_{lv}_" in p.name), None)
        text = "\n".join([f"Floor {lv}" + (" (image 1: the 3D model of this floor from above, ceilings off, rooms "
                                           "named)" if image else "") + ".", "The project as built:", *fact_lines,
                          "", "Already found (do not repeat):", *named[:80]]
                         + (["", "Agent tools (fix; their arguments go in args as one JSON object; * required):",
                             *tools, *values] if tools else []))
        msg = user_message(text, [image], [f"Image 1: the model of {lv} from above"]) if image else \
            {"role": "user", "content": text}
        try:
            reply = model.structured([{"role": "system", "content": DISCOVER_SYSTEM}, msg], discover_schema(),
                                     call_id=f"argus_discover_{lv}", name="argus_discover", kind="task",
                                     thinking=THINKING, max_tokens=MAX_TOKENS)
        except Exception as exc:  # noqa: BLE001 - a floor that fails is logged; the others are still looked at
            return lv, image, None, f"{type(exc).__name__}: {exc}"
        return lv, image, reply, None

    for lv, image, reply, err in _parallel(one, levels):
        if err:
            errors.append(f"discover {lv}: {err}"[:300])
            continue
        for d in (reply.data or {}).get("found") or []:
            target = known.get(str(d.get("target") or "").strip().lower())
            if target is None:
                dropped.append(dict(d, level=lv, why="the target is no element, label or level of the project"))
                continue
            f = K.finding("argus_ai", "AI1", d["severity"], target, d["what"], owner=d.get("cause"),
                          fix=d.get("fix"), kind=d.get("kind"),
                          evidence={"level": lv, "rule": d.get("rule"), "element": d.get("element"),
                                    "value": d.get("value"), "args": d.get("args"),
                                    "image": image.name if image else None})
            found.append(f)
    return found, dropped


# ---------------------------------------------------------------------------------------------------- the actions
def target_gone(finding: dict, prep: dict) -> Optional[bool]:
    """Argus's dry re-check of one finding on the prepared building (``build.prepare`` with the decision in): True when
    the code line that found it no longer finds it, False when it still does, None when no code line can tell
    (vision and process findings: the architect's verdicts decide)."""
    b = prep.get("building") or {}
    if finding.get("line") == "conservation" and finding.get("check") in ("C4", "C5"):
        return not any(f.get("target") == finding.get("target") for f in CV.untyped(b))
    if finding.get("line") in ("model", "inspector") and str(finding.get("check") or "").startswith("M"):
        try:
            from wenart.blender import model_review as MR
            rec = MR.review(b, None, prep)
        except Exception:  # noqa: BLE001
            return None
        return not any(f.get("check") == finding.get("check") and str(f.get("target")) == str(finding.get("target"))
                       for f in rec.get("findings") or [])
    return None


def act(project_out, building: dict, brief: Optional[dict], decisions: list[dict], model_name: str) -> list[dict]:
    """Carry out the architect actions (module docstring 4). ``decisions``: ``{"aid", "action", "element", "value",
    "reason", "finding"}``. Returns one entry per decision with its verdict."""
    from wenart.agent import architect_ai as AIA
    from wenart.agent import log as LG
    from wenart.blender import architect_actions as AA

    odir = LG.orchestrator_dir(Path(project_out))
    accepted = dict(AIA._saved_answers(odir))
    base = AIA.prep_of(building, brief, accepted)
    built = base["building"]
    plan = AA.Plan(copy.deepcopy(built))
    entries = []
    for d in decisions:
        e = {"aid": d.get("aid"), "action": d["action"], "element": d["element"], "value": d.get("value"),
             "reason": d.get("reason"), "verdict": None, "why": None}
        entries.append(e)
        level = AIA._level_of(plan, built, d["element"])
        key, ans, why_not = AIA._decision(d, plan, built, level)
        if key is None:
            e.update(verdict="refused", why=why_not)
            continue
        e["key"] = key
        if key in accepted:
            e.update(verdict="refused", why="decided already")
            continue
        cand = {key: dict(AIA._answer(ans["opt"], d.get("reason") or "", model_name, ans["where"]), own=True,
                          by="argus")}
        ok, why = AIA._verdicts(building, brief, accepted, cand, base)[key]
        if ok and d.get("finding"):
            prep = AIA.prep_of(building, brief, dict(accepted, **cand))
            gone = target_gone(d["finding"], prep)
            if gone is False:
                ok, why = False, "the finding it targets is still there in the dry re-check"
        e.update(verdict="accepted" if ok else "refused", why=why)
        if ok:
            accepted.update(cand)
            base = AIA.prep_of(building, brief, accepted)
            built = base["building"]
            plan = AA.Plan(copy.deepcopy(built))
    AIA._save_answers(odir, accepted)
    return entries


def investigate(project_out, model, *, brief: Optional[dict] = None, results=None,
                time_ok: Callable[[], bool] = lambda: True, out: Callable[[str], None] = print,
                discover_on: bool = True, act_on: bool = True, documents: bool = True,
                budget_s: Optional[float] = None) -> dict:
    """Module docstring. Returns the record written to ``orchestrator/argus_ai.json``. ``act_on`` False (the end of the
    run, nothing is built after it): the decisions are listed, not carried out."""
    from wenart.agent import log as LG

    t0 = time.time()
    project_out = Path(project_out)
    errors: list = []
    limit = float(budget_s if budget_s is not None else (BUDGET_S if documents else CYCLE_BUDGET_S))
    outer_ok = time_ok

    def time_ok() -> bool:                 # the run's time and Argus's own budget (the agent's rounds need the rest)
        return outer_ok() and time.time() - t0 < limit
    if act_on and documents and time_ok():
        documents_vs_model(model, project_out, errors=errors)
    inp = I.pod(project_out, results)
    rep = R.run(inp)
    building = inp.stage("final") or inp.final or {}
    fact_lines = facts(building, rep)
    items = items_of(rep)
    tried = tried_by_target(inp.agent_log)
    for f in items:
        if str(f.get("target")) in tried:
            f["tried"] = tried[str(f.get("target"))]
    reg = _registry()
    valid = CL.Valid(inp.stage("build") or building, inp.manifest)
    tools = _tool_help(reg)
    values = valid.lines()
    piece_notes(items, valid)
    verdicts = triage(model, items, fact_lines, time_ok=time_ok, out=out, errors=errors,
                      project=inp.project, tools=tools, values=values) if items else {}
    by_id = {f["aid"]: f for f in items}
    new, decisions, work, guards, disputed = [], [], [], [], []
    actions: list = []
    for aid, v in verdicts.items():
        f = by_id.get(aid)
        if f is None:
            continue
        if v.get("rule"):
            guards.append({"kind": v["kind"], "cause": v["cause"], "rule": v["rule"][:600], "from": aid,
                           "target": f.get("target"), "check": f"{f.get('line')}:{f.get('check')}"})
        if not v.get("real") or v.get("fix") == "not_a_problem":
            if f.get("severity") != "info":
                disputed.append({"aid": aid, "target": f.get("target"), "check": f"{f.get('line')}:{f.get('check')}",
                                 "why": v.get("why")})
            continue
        if f.get("check") in ("C1", "C6") and f.get("severity") == "info":   # a reason that hides a loss
            new.append(K.finding("argus_ai", "AI2", v.get("severity") or "major", f.get("target"),
                                 f"left out for a reason that hides a loss: {f.get('message')} ({v.get('why')})",
                                 owner=v.get("cause"), fix=v.get("fix"), kind=v.get("kind"),
                                 evidence=dict(f.get("evidence") or {}, rule=v.get("rule"))))
        elif f.get("check") == "P0":         # a warning no rule knows that names a real problem
            new.append(K.finding("argus_ai", "AI3", v.get("severity") or "major", f.get("target"),
                                 f"{f.get('message')} ({v.get('why')})", owner=v.get("cause"), fix=v.get("fix"),
                                 kind=v.get("kind"), evidence={"rule": v.get("rule")}))
        if v.get("fix") in FIX_ARCH:
            decisions.append({"aid": aid, "action": v["fix"], "element": v.get("element") or str(f.get("target")),
                              "value": v.get("value") or "", "reason": v.get("why"), "finding": f})
        elif v.get("fix") in AGENT_TOOLS:
            args, why_not = parse_args(v.get("args"), v["fix"], v.get("element") or str(f.get("target")))
            if args is None:
                errors.append(f"{aid} {v['fix']}: {why_not}"[:300])
            else:
                act_, w = _action(aid, v["fix"], args, f, v.get("why"), "argus_ai")
                actions.append(act_)
                work.append(w)
        elif v.get("fix") in ("agent_round", "rerun_stage"):
            work.append({"aid": aid, "fix": v["fix"], "check": f.get("check"), "severity": f.get("severity"),
                         "target": f.get("target"), "message": f.get("message"), "cause": v.get("cause"),
                         "why": v.get("why")})
    found, dropped = discover(model, inp, rep, fact_lines, time_ok=time_ok, out=out, errors=errors, tools=tools,
                              values=values) if discover_on else ([], [])
    new += found
    for f in found:
        ev = f.get("evidence") or {}
        if ev.get("rule"):
            guards.append({"kind": f["kind"], "cause": f.get("owner"), "rule": str(ev["rule"])[:600], "from": "AI1",
                           "target": f["target"], "check": "argus_ai:AI1"})
        if f.get("fix") in FIX_ARCH:
            decisions.append({"aid": "AI1", "action": f["fix"], "element": ev.get("element") or f["target"],
                              "value": ev.get("value") or "", "reason": f["message"], "finding": None})
        elif f.get("fix") in AGENT_TOOLS:
            n = len(actions) + 1
            args, why_not = parse_args(ev.get("args"), f["fix"], ev.get("element") or f["target"])
            if args is None:
                errors.append(f"AI1 {f['fix']}: {why_not}"[:300])
            else:
                act_, w = _action(f"N{n}", f["fix"], args, f, f["message"], "argus_ai")
                actions.append(act_)
                work.append(w)
        elif f.get("fix") == "agent_round":
            work.append({"aid": "AI1", "fix": "agent_round", "check": "AI1", "severity": f["severity"],
                         "target": f["target"], "message": f["message"], "cause": f.get("owner"), "why": ""})
    # the fixes the code lines name exactly: no model needed (they run even when the model failed)
    c_actions, c_work, revoke = code_actions(rep, inp.stage("build") or building)
    have = {(x["tool"], json.dumps(x["args"], sort_keys=True)) for x in actions}
    for x, w in zip(c_actions, c_work):
        if (x["tool"], json.dumps(x["args"], sort_keys=True)) not in have:
            actions.append(x)
            work.append(w)
    # 27 Oct 2026: every call checked by code before the agent loop runs it; the invalid ones repaired (code, then
    # one model call) or dropped with their reasons (their findings stay in the work list for the agent's round)
    vetted = {"calls": len(actions)}
    if reg is not None and actions:
        actions, vetted = CL.vet_all(model, actions, valid, reg, {w["id"]: w for w in work if w.get("id")},
                                     help_lines=tools, errors=errors, time_ok=time_ok, thinking=THINKING)
    revoked = revoke_decisions(project_out, revoke) if act_on and revoke else \
        [{"key": k, "done": False, "why": "the end of the run: not carried out"} for k in revoke]
    if act_on:
        entries = act(project_out, building, brief, decisions, getattr(model, "model", "")) if decisions else []
    else:
        entries = [{"aid": d.get("aid"), "action": d["action"], "element": d["element"], "value": d.get("value"),
                    "reason": d.get("reason"), "verdict": "proposed", "why": "the end of the run: not carried out"}
                   for d in decisions]
    rec = {"name": R.NAME, "model": getattr(model, "model", ""), "score_before": rep["score"],
           "severity_before": rep["severity"], "triaged": len(verdicts), "items": len(items),
           "findings": new, "decisions": entries, "work": work, "guards": guards, "disputed": disputed,
           "dropped": dropped, "verdicts": [dict(v, target=str(by_id.get(k, {}).get("target"))) for k, v in
                                            verdicts.items()],
           "actions": actions, "calls": vetted, "revoked": revoked,
           "accepted": sum(1 for e in entries if e["verdict"] == "accepted") + sum(1 for r in revoked if r["done"]),
           "errors": errors,
           "untriaged": [f["aid"] for f in items if f["aid"] not in verdicts],
           "seconds": round(time.time() - t0, 1)}
    odir = LG.orchestrator_dir(project_out)
    LG.write_json_atomic(odir / (LOG_JSON if act_on else FINAL_JSON), _jsonable(rec))
    (odir / (LOG_MD if act_on else FINAL_MD)).write_text(report_md(rec), encoding="utf-8")
    return rec


def documents_vs_model(model, project_out, *, errors: Optional[list] = None) -> Optional[dict]:
    """The documents against the model (``plan_vs_model.audit_project``: each floor's source plan beside the model's
    top-down view, the elevations beside the exterior renders; every claim checked by code), its findings given their
    kind (``CHANGE_KIND``) and written to ``orchestrator/plan_vs_model.json``, where the report reads them. Never
    raises (``errors`` gets the reason)."""
    from wenart.agent import log as LG
    from wenart.audit import plan_vs_model as PV

    errors = errors if errors is not None else []
    try:
        res = PV.audit_project(model, project_out, call_prefix="argus_documents")
    except Exception as exc:  # noqa: BLE001 - the other lines still run
        errors.append(f"documents vs model: {type(exc).__name__}: {exc}"[:300])
        return None
    for f in res.get("findings") or []:
        f["kind"] = CHANGE_KIND.get((f.get("evidence") or {}).get("change"), "lost")
    ev = res.get("elevations") or {}
    rec = {"findings": res.get("findings") or [], "dropped": res.get("dropped") or [],
           "checked": {"levels": len(res.get("levels") or []), "elevation_calls": ev.get("calls"),
                       "plans": {r.get("level"): r.get("plan_method") for r in res.get("levels") or []}},
           "note": res.get("error") or ev.get("note")}
    LG.write_json_atomic(LG.orchestrator_dir(Path(project_out)) / PLAN_JSON, _jsonable(rec))
    return rec


def _jsonable(rec: dict) -> dict:
    return json.loads(json.dumps(rec, default=str))


def _record(project_out) -> Optional[dict]:
    from wenart.agent import log as LG

    path = LG.orchestrator_dir(Path(project_out)) / LOG_JSON
    return I.read_json(path) if path.is_file() else None


def work_findings(project_out) -> list[dict]:
    """The findings Argus handed to the agent (``work``), in the critic's format, for the agent's rounds: its own
    tool calls' targets (``argus_tool``: an id ``a:<aid>`` and the cause its tool fixes, ``argus_cause``) and the
    critical / major ones it left to the agent's next round (``agent_round``)."""
    out = []
    for w in (_record(project_out) or {}).get("work") or []:
        if w.get("fix") == "argus_tool":
            out.append(dict(w))
        elif w.get("fix") == "agent_round" and w.get("severity") in ("critical", "major"):
            out.append({"check": str(w.get("check") or "AI1"), "severity": w["severity"], "target": w.get("target"),
                        "room": None, "view": None, "source": "argus", "message": f"Argus: {w.get('message')}"})
    return out


def tool_actions(project_out) -> list[dict]:
    """The tool calls Argus makes itself (``investigate``'s ``actions``: the model's and the code lines'), for the
    loop's ``argus_session``."""
    return [a for a in (_record(project_out) or {}).get("actions") or []
            if isinstance(a, dict) and a.get("tool") and isinstance(a.get("args"), dict)]


def report_md(rec: dict) -> str:
    lines = [f"# {R.NAME} AI: the auditor thinks and acts", "",
             f"{rec['triaged']} of {rec['items']} finding(s) triaged by {rec.get('model') or 'the agent model'} "
             f"(thinking {'on' if THINKING else 'off'}); {len(rec['findings'])} new finding(s); {rec['accepted']} of "
             f"{len(rec['decisions'])} "
             f"decision(s) carried out (code-checked); {len(rec['work'])} handed to the agent; {len(rec['guards'])} "
             f"rule(s) proposed; {len(rec['disputed'])} disputed; {len(rec['dropped'])} claim(s) dropped (no such "
             f"target). Score before: {rec.get('score_before')}.", ""]
    if rec.get("untriaged") or rec.get("errors"):
        lines += [f"Not triaged: {', '.join(rec.get('untriaged') or []) or 'none'}; errors: "
                  f"{'; '.join(rec.get('errors') or []) or 'none'}.", ""]
    if rec["findings"]:
        lines += ["## New findings", "", "| severity | kind | target | what | fix |", "|---|---|---|---|---|"]
        lines += [f"| {f['severity']} | {f['kind']} | {R._cell(f['target'])} | {R._cell(f['message'][:300])} | "
                  f"{R._cell(f.get('fix'))} |" for f in rec["findings"]]
    if rec["decisions"]:
        lines += ["", "## Decisions", "", "| finding | action | element | verdict | why |", "|---|---|---|---|---|"]
        lines += [f"| {e.get('aid')} | {e['action']} | {e['element']} | {e['verdict']} | {R._cell(e.get('why'))} |"
                  for e in rec["decisions"]]
    c = rec.get("calls") or {}
    if c.get("calls"):
        lines += ["", f"Own calls: {c.get('calls')} chosen, {c.get('valid', c.get('calls'))} valid "
                      f"({c.get('code_repaired', 0)} repaired by code, {c.get('model_repaired', 0)} by the model), "
                      f"{c.get('duplicates', 0)} duplicate(s), {c.get('dropped', 0)} dropped (errors above)."]
    if rec.get("actions"):
        lines += ["", "## Argus's own edits (run in the agent loop through the same checks)", "",
                  "| source | tool | arguments | fixes | repaired | why |", "|---|---|---|---|---|---|"]
        lines += [f"| {x['source']} | {x['tool']} | {R._cell(json.dumps(x['args'], ensure_ascii=False)[:160])} | "
                  f"{x['finding_id']} | {R._cell('; '.join(x.get('repaired') or [])[:160])} | "
                  f"{R._cell(x.get('why'))} |" for x in rec["actions"]]
    if rec.get("revoked"):
        lines += ["", "## AI decisions revoked", ""]
        lines += [f"- {r['key']}: {'revoked' if r['done'] else 'kept'} ({r['why']})" for r in rec["revoked"]]
    if rec["work"]:
        lines += ["", "## Handed to the agent", ""]
        lines += [f"- {w['severity']} {w['target']}: {R._cell(str(w['message'])[:200])}" for w in rec["work"]]
    if rec["guards"]:
        lines += ["", "## Rules proposed (prevention)", ""]
        lines += [f"- [{g['kind']}, {g['cause']}] {g['rule']} (from {g['check']} {g['target']})" for g in rec["guards"]]
    if rec["disputed"]:
        lines += ["", "## Disputed findings", ""]
        lines += [f"- {d['check']} {d['target']}: {R._cell(d.get('why'))}" for d in rec["disputed"]]
    return "\n".join(lines) + "\n"
