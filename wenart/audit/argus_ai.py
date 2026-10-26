"""Argus AI: the open-weight agent model thinks over everything the audit found and acts (26 Oct 2026, user: "use open
weight AI models for this auditor, it needs to be smart, it needs to solve the problems even without me telling it
... think outside the box").

What: ``investigate(project_out, model)`` runs on the pod after a build (and again at the end of the run):

1. **The case file.** Argus's code lines run (``report.run``: conservation, process, the model review, the inspector,
   the judge, the ledger and the plan-vs-model lines when present); the project's facts are written as lines (levels,
   rooms with labels, types, areas, doors and windows, pieces; the site's labelled areas and symbols and whether they
   are built; the warnings by rule).
2. **Triage** (``TRIAGE_BATCH`` findings per call, every finding: no cap). The agent model (Qwen3.8-27B, Apache-2.0,
   thinking on, temperature 0, strict JSON schema) says per finding whether it is a real problem, its kind, the stage
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
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.audit import conservation as CV
from wenart.audit import inputs as I
from wenart.audit import kinds as K
from wenart.audit import report as R

LOG_JSON = "argus_ai.json"
LOG_MD = "argus_ai.md"
FINAL_JSON = "argus_ai_final.json"       # the end of the run (``act_on`` False): the record of the first pass stays
FINAL_MD = "argus_ai_final.md"
TRIAGE_BATCH = 24              # findings per triage call (every finding is triaged: the batches cover them all)
DISCOVER_MAX = 15              # new findings per floor per call
FACT_LINES = 140               # project fact lines in the case file
MESSAGE_CHARS = 320
CAUSES = ("reading", "recognition", "fit", "layout", "decor", "agent", "architect", "site", "roof", "build",
          "cameras", "render", "library", "scheduler", "unknown")
FIX_ARCH = ("door_to_window", "french_window", "raise_sill", "widen_door", "interior_glazing", "high_window",
            "pass_through", "gap_to_door", "window_to_door", "snap_threshold", "retype_room", "enlarge_windows",
            "move_piece", "mount_fixture", "remove_piece")
FIX_OTHER = ("agent_round", "rerun_stage", "rule_needed", "not_a_problem")
FIXES = FIX_ARCH + FIX_OTHER
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
    "- Choose the fix the run can carry out now: an architect action on one element (give the element id, and a "
    "value when the action needs one, e.g. a room type), agent_round (the furniture agent's next round: collisions, "
    "walkways, orientation, a piece in the wrong place), rerun_stage, or rule_needed when nothing in this run can fix "
    "it: then write the general rule (one or two sentences, for every project, never for this one only) that would "
    "prevent this kind of problem.\n"
    "- 'not built: <reason>' lists elements a stage left out and the reason it gave: real = true when the reason hides "
    "a loss (something the documents show that the house should have), false when it is a good reason.\n"
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
                "required": ["id", "real", "severity", "kind", "cause", "fix", "element", "value", "rule", "why"],
                "properties": {"id": {"type": "string", "enum": ids},
                               "real": {"type": "boolean"},
                               "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                               "kind": {"type": "string", "enum": list(K.KINDS)},
                               "cause": {"type": "string", "enum": list(CAUSES)},
                               "fix": {"type": "string", "enum": list(FIXES)},
                               "element": {"type": "string"},
                               "value": {"type": "string"},
                               "rule": {"type": "string"},
                               "why": {"type": "string", "minLength": 5}}}}}}


def discover_schema() -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["found"],
            "properties": {"found": {"type": "array", "maxItems": DISCOVER_MAX, "items": {
                "type": "object", "additionalProperties": False,
                "required": ["target", "kind", "severity", "what", "cause", "fix", "element", "value", "rule"],
                "properties": {"target": {"type": "string", "minLength": 2},
                               "kind": {"type": "string", "enum": list(K.KINDS)},
                               "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                               "what": {"type": "string", "minLength": 5},
                               "cause": {"type": "string", "enum": list(CAUSES)},
                               "fix": {"type": "string", "enum": list(FIXES)},
                               "element": {"type": "string"},
                               "value": {"type": "string"},
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
    rows = [f for f in rep.get("findings") or [] if f.get("severity") != "info" or f.get("check") == "C6"]
    rows += [K.finding("process", "P0", "info", PR._target(w), f"a warning no rule knows: {w}", owner="process",
                       kind="other") for w in rep.get("unmatched_warnings") or []]
    rows.sort(key=lambda f: (order.get(f.get("severity"), 4), str(f.get("kind"))))
    return [dict(f, aid=f"F{i}") for i, f in enumerate(rows, 1)]


def _item_text(f: dict) -> dict:
    return {"id": f["aid"], "check": f"{f.get('line')}:{f.get('check')}", "severity": f.get("severity"),
            "kind": f.get("kind"), "target": str(f.get("target")), "what": str(f.get("message"))[:MESSAGE_CHARS],
            "owner": f.get("owner"), "code_fix": f.get("fix")}


# ---------------------------------------------------------------------------------------------------- the calls
def triage(model, items: list[dict], fact_lines: list[str], *, time_ok: Callable[[], bool] = lambda: True,
           out: Callable[[str], None] = print, errors: Optional[list] = None) -> dict:
    """``{aid: verdict}`` for every item (module docstring 2); an item the model skipped has none (``errors`` gets
    what failed)."""
    errors = errors if errors is not None else []
    verdicts: dict = {}
    for start in range(0, len(items), TRIAGE_BATCH):
        if not time_ok():
            out(f"Argus AI: time is up after {start} of {len(items)} findings")
            break
        batch = items[start:start + TRIAGE_BATCH]
        text = "\n".join(["The project as built:", *fact_lines, "",
                          f"The findings ({start + 1}-{start + len(batch)} of {len(items)}):",
                          json.dumps([_item_text(f) for f in batch], indent=1, ensure_ascii=False), "",
                          "Architect actions (fix) and what they do: " + _arch_help()])
        try:
            reply = model.structured([{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
                                     triage_schema([f["aid"] for f in batch]),
                                     call_id=f"argus_triage_{start // TRIAGE_BATCH}", name="argus_triage",
                                     kind="task", thinking=True)
        except Exception as exc:  # noqa: BLE001 - one batch that fails is logged; the others are still triaged
            errors.append(f"triage {start + 1}-{start + len(batch)}: {type(exc).__name__}: {exc}"[:300])
            continue
        if reply.errors:
            errors.append(f"triage {start + 1}-{start + len(batch)}: {'; '.join(reply.errors[:2])}"[:300])
        for v in (reply.data or {}).get("items") or []:
            verdicts.setdefault(v["id"], v)
    return verdicts


def _arch_help() -> str:
    from wenart.blender import architect_actions as AA
    return "; ".join(f"{a} ({AA.ACTIONS.get(a, '')})" for a in FIX_ARCH)


def discover(model, inp: I.Inputs, rep: dict, fact_lines: list[str], *, time_ok: Callable[[], bool] = lambda: True,
             out: Callable[[str], None] = print, errors: Optional[list] = None) -> tuple[list[dict], list[dict]]:
    """``(findings, dropped)`` of module docstring 3."""
    from wenart.agent.model import user_message

    errors = errors if errors is not None else []
    building = inp.final or {}
    known = known_targets(building)
    named = sorted({f"{f.get('target')}: {str(f.get('message'))[:90]}" for f in rep.get("findings") or []
                    if f.get("severity") in ("critical", "major")})
    found, dropped = [], []
    levels = [lv.get("id") for lv in building.get("levels") or []] or [None]
    for lv in levels:
        if not time_ok():
            break
        image = next((p for p in inp.top_plans if lv and f"top_{lv}_" in p.name), None)
        text = "\n".join([f"Floor {lv}" + (" (image 1: the 3D model of this floor from above, ceilings off, rooms "
                                           "named)" if image else "") + ".", "The project as built:", *fact_lines,
                          "", "Already found (do not repeat):", *named[:80]])
        msg = user_message(text, [image], [f"Image 1: the model of {lv} from above"]) if image else \
            {"role": "user", "content": text}
        try:
            reply = model.structured([{"role": "system", "content": DISCOVER_SYSTEM}, msg], discover_schema(),
                                     call_id=f"argus_discover_{lv}", name="argus_discover", kind="task", thinking=True)
        except Exception as exc:  # noqa: BLE001 - a floor that fails is logged; the others are still looked at
            errors.append(f"discover {lv}: {type(exc).__name__}: {exc}"[:300])
            continue
        for d in (reply.data or {}).get("found") or []:
            target = known.get(str(d.get("target") or "").strip().lower())
            if target is None:
                dropped.append(dict(d, level=lv, why="the target is no element, label or level of the project"))
                continue
            f = K.finding("argus_ai", "AI1", d["severity"], target, d["what"], owner=d.get("cause"),
                          fix=d.get("fix"), kind=d.get("kind"),
                          evidence={"level": lv, "rule": d.get("rule"), "element": d.get("element"),
                                    "value": d.get("value"), "image": image.name if image else None})
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
                discover_on: bool = True, act_on: bool = True) -> dict:
    """Module docstring. Returns the record written to ``orchestrator/argus_ai.json``. ``act_on`` False (the end of the
    run, nothing is built after it): the decisions are listed, not carried out."""
    from wenart.agent import log as LG

    t0 = time.time()
    project_out = Path(project_out)
    inp = I.pod(project_out, results)
    rep = R.run(inp)
    building = inp.stage("final") or inp.final or {}
    fact_lines = facts(building, rep)
    items = items_of(rep)
    errors: list = []
    verdicts = triage(model, items, fact_lines, time_ok=time_ok, out=out, errors=errors) if items else {}
    by_id = {f["aid"]: f for f in items}
    new, decisions, work, guards, disputed = [], [], [], [], []
    for aid, v in verdicts.items():
        f = by_id.get(aid)
        if f is None:
            continue
        if v.get("rule"):
            guards.append({"kind": v["kind"], "cause": v["cause"], "rule": v["rule"][:600], "from": aid,
                           "target": f.get("target"), "check": f"{f.get('line')}:{f.get('check')}"})
        if not v.get("real") or v.get("fix") == "not_a_problem":
            if f.get("check") not in ("C6", "P0"):
                disputed.append({"aid": aid, "target": f.get("target"), "check": f"{f.get('line')}:{f.get('check')}",
                                 "why": v.get("why")})
            continue
        if f.get("check") == "C6":           # a reason that hides a loss: a finding of its own
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
        elif v.get("fix") in ("agent_round", "rerun_stage"):
            work.append({"aid": aid, "fix": v["fix"], "check": f.get("check"), "severity": f.get("severity"),
                         "target": f.get("target"), "message": f.get("message"), "cause": v.get("cause"),
                         "why": v.get("why")})
    found, dropped = discover(model, inp, rep, fact_lines, time_ok=time_ok, out=out, errors=errors) \
        if discover_on else ([], [])
    new += found
    for f in found:
        ev = f.get("evidence") or {}
        if ev.get("rule"):
            guards.append({"kind": f["kind"], "cause": f.get("owner"), "rule": str(ev["rule"])[:600], "from": "AI1",
                           "target": f["target"], "check": "argus_ai:AI1"})
        if f.get("fix") in FIX_ARCH:
            decisions.append({"aid": "AI1", "action": f["fix"], "element": ev.get("element") or f["target"],
                              "value": ev.get("value") or "", "reason": f["message"], "finding": None})
        elif f.get("fix") == "agent_round":
            work.append({"aid": "AI1", "fix": "agent_round", "check": "AI1", "severity": f["severity"],
                         "target": f["target"], "message": f["message"], "cause": f.get("owner"), "why": ""})
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
           "accepted": sum(1 for e in entries if e["verdict"] == "accepted"), "errors": errors,
           "untriaged": [f["aid"] for f in items if f["aid"] not in verdicts],
           "seconds": round(time.time() - t0, 1)}
    odir = LG.orchestrator_dir(project_out)
    LG.write_json_atomic(odir / (LOG_JSON if act_on else FINAL_JSON), _jsonable(rec))
    (odir / (LOG_MD if act_on else FINAL_MD)).write_text(report_md(rec), encoding="utf-8")
    return rec


def _jsonable(rec: dict) -> dict:
    return json.loads(json.dumps(rec, default=str))


def work_findings(project_out) -> list[dict]:
    """The findings Argus handed to the agent (``work``), in the critic's format, for the agent's next round."""
    from wenart.agent import log as LG

    path = LG.orchestrator_dir(Path(project_out)) / LOG_JSON
    rec = I.read_json(path) if path.is_file() else None
    out = []
    for w in (rec or {}).get("work") or []:
        if w.get("fix") != "agent_round" or w.get("severity") not in ("critical", "major"):
            continue
        out.append({"check": str(w.get("check") or "AI1"), "severity": w["severity"], "target": w.get("target"),
                    "room": None, "view": None, "source": "argus", "message": f"Argus: {w.get('message')}"})
    return out


def report_md(rec: dict) -> str:
    lines = [f"# {R.NAME} AI: the auditor thinks and acts", "",
             f"{rec['triaged']} of {rec['items']} finding(s) triaged by {rec.get('model') or 'the agent model'} "
             f"(thinking on); {len(rec['findings'])} new finding(s); {rec['accepted']} of {len(rec['decisions'])} "
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
