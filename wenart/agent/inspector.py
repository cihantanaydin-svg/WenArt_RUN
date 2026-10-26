"""The inspector's report: what the AI saw on the final renders before the user looks (26 Oct 2026, user: "there
are still problems in the final product, problems that somebody looking at it understands ... I need ai models to
see understand and fix everything before even I look at it").

What: ``report(loop, round_no)`` gathers the final round's findings on the final renders (the loop asks every room
and exterior view again there, with the visitor checks ``prompts.VISITOR_CHECKS``: a door off its floor or into the
air, a basin at knee height, a fall risk, a room that makes no sense, pieces that repeat or clash, a piece with its
back to the room, doors and windows out of style, too many downpipes), the code critic's open findings and the
architect's open points (``scene/architect.json``), and says for each what happened: fixed in the final round (an
accepted edit on its target), handed to the stage that owns it (``causes.REPORT_TO``: the architect, the openings,
the decor, the lighting), dropped with the reason, or left open. ``write(project_out, rec)`` writes
``orchestrator/inspector.json`` and ``inspector.md`` (copied with the agent's log into ``results/agent/<p>/``).

Why: nothing the AI saw stays silent. A finding no tool fixes is listed with its owner, so the next code rule is
written for it and the user is told before looking (CLAUDE.md: "Nothing changes silently").
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from wenart.agent import causes as CS
from wenart.agent import log as LG
from wenart.agent import prompts as P

REPORT_JSON = "inspector.json"
REPORT_MD = "inspector.md"
MD_MAX = 120                    # findings listed in the report (all of them are in the JSON)


def _row(f: dict, fixed: set, accepted_targets: set) -> dict:
    cause = f.get("cause") if f.get("cause") in CS.CAUSE_TOOLS else CS.cause_of(f)
    target = f.get("target")
    if target in accepted_targets or (f.get("check"), target) in fixed:
        outcome = "fixed in the final round (an accepted edit on its target)"
    elif CS.REPORT_TO.get(cause):
        outcome = f"handed to the {CS.REPORT_TO[cause]} stage: {CS.NO_TOOL_REASON.get(cause, '')}".rstrip(": ")
    elif CS.CAUSE_TOOLS.get(cause):
        outcome = "open: a tool exists (" + ", ".join(CS.CAUSE_TOOLS[cause][:3]) + ") but no edit was accepted"
    else:
        outcome = "open: " + (CS.NO_TOOL_REASON.get(cause) or "no tool for it")
    ev = f.get("evidence") if isinstance(f.get("evidence"), dict) else {}
    return {"check": f.get("check"), "severity": f.get("severity"), "target": target, "room": f.get("room_id"),
            "view": ev.get("view"), "source": f.get("source"), "message": f.get("message") or f.get("finding"),
            "cause": cause, "outcome": outcome, "visitor": str(f.get("check")) in P.VISITOR_CHECKS}


def architect_open(project_out: Path) -> list[dict]:
    """The architect's open points of the built scene (``scene/architect.json``), major first."""
    path = Path(project_out) / "scene" / "architect.json"
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for q in rec.get("questions") or []:
        for a in q.get("answers") or []:
            if a.get("open"):
                out.append({"rule": q.get("id"), "topic": q.get("topic"), "severity": q.get("severity", "minor"),
                            "element": a.get("element"), "found": a.get("found"), "note": a.get("note")})
    out.sort(key=lambda x: (x["severity"] != "major", str(x["rule"]), str(x["element"])))
    return out


def model_review(project_out: Path) -> Optional[dict]:
    """The review of the 3D model as built (``scene/model_review.json``, ``wenart.blender.model_review``)."""
    try:
        return json.loads((Path(project_out) / "scene" / "model_review.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def report(project_out, round_no: int, findings: dict, accepted: list[dict]) -> dict:
    """The record (module docstring). ``findings``: ``{"code": [...], "vision_kept": [...], "vision_dropped":
    [...]}`` of the final round; ``accepted``: its accepted edits (``{"tool", "args", ...}``)."""
    targets = set()
    for a in accepted or []:
        args = a.get("args") or {}
        targets |= {v for k, v in args.items() if k in ("piece_id", "room_id", "target", "camera") and v}
    fixed = {(a.get("finding_check"), a.get("finding_target")) for a in accepted or []}
    kept = [_row(f, fixed, targets) for f in findings.get("vision_kept") or []]
    code = [_row(f, fixed, targets) for f in findings.get("code") or []
            if f.get("severity") in ("critical", "major")]
    dropped = [dict(_row(f, fixed, targets), outcome=f"dropped: {f.get('dropped') or f.get('reason') or 'screened'}")
               for f in findings.get("vision_dropped") or []]
    arch = architect_open(Path(project_out))
    rows = kept + code
    counts = {"seen": len(kept) + len(dropped), "visitor": sum(1 for r in kept if r["visitor"]),
              "fixed": sum(1 for r in rows if r["outcome"].startswith("fixed")),
              "handed": sum(1 for r in rows if r["outcome"].startswith("handed")),
              "open": sum(1 for r in rows if r["outcome"].startswith("open")),
              "dropped": len(dropped), "architect_open": len(arch),
              "architect_open_major": sum(1 for a in arch if a["severity"] == "major")}
    model = model_review(Path(project_out))
    if model is not None:
        counts["model_checks"] = {k: v.get("failed") for k, v in (model.get("checks") or {}).items()}
        counts["model_open"] = sum(1 for r in code if str(r.get("check", "")).startswith("M"))
    return {"round": round_no, "counts": counts, "vision": kept, "code": code, "dropped": dropped,
            "architect_open": arch, "model_review": model}


def report_md(rec: dict, project: str = "") -> str:
    c = rec["counts"]
    lines = [f"# What the AI inspector saw on the final renders{': ' + project if project else ''}", "",
             f"Round {rec['round']} (the final round: every room and exterior view asked again on the final renders, "
             f"with the visitor checks Q1-Q9). {c['seen']} vision finding(s) ({c['visitor']} visitor), "
             f"{c['fixed']} fixed in this round, {c['handed']} handed to the stage that owns them, {c['open']} open, "
             f"{c['dropped']} dropped by code; the architect leaves {c['architect_open']} open point(s) "
             f"({c['architect_open_major']} major).", "",
             "Visitor checks: " + "; ".join(f"{k} {P.CHECKLIST[k]['what'].split(':')[0]}" for k in P.VISITOR_CHECKS),
             ""]
    model = rec.get("model_review")
    if isinstance(model, dict):
        # 26 Oct 2026: the model as built is reviewed first (every element measured, not only what a camera frames)
        lines += ["## The 3D model, measured (every element, every floor)", "",
                  "; ".join(f"{k}: {v.get('checked', '-')} checked, {v.get('failed', '-')} failed"
                            for k, v in sorted((model.get("checks") or {}).items()) if v.get("status") == "ok")
                  + " (M1 doors on their floors, M2 working heights, M3 guards, M4 doors into the air, M5 rain water, "
                    "M6 one door and window language, M7 rooms that make sense, M8 entrances that make sense; "
                    "`scene/model_review.md`).", ""]
    order = {"critical": 0, "major": 1, "minor": 2}
    rows = sorted(rec["vision"] + rec["code"], key=lambda r: (order.get(r.get("severity"), 3), not r["visitor"]))
    if rows:
        lines += ["| severity | check | where | target | what | outcome |", "|---|---|---|---|---|---|"]
        for r in rows[:MD_MAX]:
            where = r.get("view") or r.get("room") or ""
            msg = str(r.get("message") or "").replace("|", "/").replace("\n", " ")[:160]
            lines.append(f"| {r.get('severity')} | {r.get('check')} | {where} | {r.get('target')} | {msg} | "
                         f"{r['outcome'][:140]} |")
        if len(rows) > MD_MAX:
            lines.append(f"| ... | | | | {len(rows) - MD_MAX} more in {REPORT_JSON} | |")
    else:
        lines.append("No open finding on the final renders.")
    if rec["architect_open"]:
        lines += ["", "## The architect's open points (no safe default; the AI architect and you decide)", ""]
        for a in rec["architect_open"][:60]:
            lines.append(f"- **{a['rule']} {a['topic']}** ({a['severity']}) {a['element']}: {a['found']}"
                         + (f" ({a['note']})" if a.get("note") else ""))
    if rec["dropped"]:
        lines += ["", f"{len(rec['dropped'])} vision finding(s) dropped by code (in {REPORT_JSON} with the reason)."]
    return "\n".join(lines) + "\n"


def write(project_out, rec: dict, project: str = "") -> Optional[Path]:
    odir = LG.orchestrator_dir(Path(project_out))
    LG.write_json_atomic(odir / REPORT_JSON, rec)
    path = odir / REPORT_MD
    path.write_text(report_md(rec, project), encoding="utf-8")
    return path
