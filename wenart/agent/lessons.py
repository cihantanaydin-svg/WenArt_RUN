"""The user's lessons for the architect, with AI (25 Oct 2026, user: "use AI to understand what I was asking all
along and continue to develop itself with the future requests").

What:
- ``python -m wenart.agent.lessons add "<request>" [--server URL --model NAME]``: a new request or correction of the
  user becomes a lesson in ``wenart/blender/architect_lessons.json``. With a model (the agent model, OpenAI-style
  server) the AI turns the request into a general lesson (strict JSON: the lesson, its area, the question the
  architect asks every project, the rules that already check it); without one the request is stored as it is,
  ``open``. ``list`` prints them.
- ``review_lessons(project_out, model)`` (the pod, after the AI architect's answers): the open lessons (no rule checks
  them yet) are put to the agent model with the facts of the built building (the rooms, the furniture and decor per
  room, the architect's counts); it says per lesson ``ok``, ``issue`` (with the elements) or ``unknown``. The
  findings go to ``orchestrator/architect_lessons.json`` and ``.md``; nothing is changed (a finding is a question for
  the next rule or for the user).

Why: a correction the user made once is checked on every later project, by a rule when one exists, by the AI until
then.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from wenart.blender import architect_lessons as L

ADD_SYSTEM = (
    "You keep the rule book of an architect who checks house designs before they are rendered. The user (the "
    "client) sent a request or a correction. Turn it into one general lesson that applies to every future project "
    "(never to one project only), one question the architect asks of every project to check it, its area, and the "
    "ids of the existing rules that already check it (only from the list given; none when no rule fits).")
REVIEW_SYSTEM = (
    "You are the architect of this house. For each lesson the client taught us, look at the facts of the built "
    "building and say whether the building follows it: ok, issue (name the rooms or elements and what is wrong) "
    "or unknown (the facts do not show it). Each lesson carries the results of the code checks that test it "
    "(evidence: per check its question, its counts and what it found per element, open findings first): an open "
    "finding is an issue; checks that are fine or fixed mean ok unless the facts say otherwise. Answer unknown "
    "only when neither the evidence nor the facts show it. Base every verdict on the facts given, never on a "
    "guess.")
EVIDENCE_PER_CHECK = 8          # findings per check given to the AI (the open ones first)
REVIEW_JSON = "architect_lessons.json"
REVIEW_MD = "architect_lessons.md"


def add_schema(rule_ids: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False,
            "required": ["lesson", "area", "question", "checks"],
            "properties": {"lesson": {"type": "string", "minLength": 10},
                           "area": {"type": "string", "enum": list(L.AREAS)},
                           "question": {"type": "string", "minLength": 5},
                           "checks": {"type": "array", "items": {"type": "string", "enum": rule_ids}}}}


def rule_ids() -> list[str]:
    from wenart.blender import architect as AR
    return list(AR.ORDER)


def add_with_ai(request: str, model=None, path: Optional[Path] = None) -> dict:
    """The request as a lesson (the AI's general wording when a model answers, else the request itself)."""
    if model is None:
        return L.add_lesson(request, path=path)
    ids = rule_ids()
    reply = model.structured([{"role": "system", "content": ADD_SYSTEM},
                              {"role": "user", "content": json.dumps(
                                  {"request": request, "rules": ids,
                                   "existing_lessons": [x["lesson"] for x in L.lessons(path)][-30:]})}],
                             add_schema(ids), call_id="lesson_add", name="lesson", kind="task")
    data = reply.data or {}
    if not data.get("lesson"):
        return L.add_lesson(request, path=path)
    checks = [c for c in data.get("checks") or [] if c in ids]
    return L.add_lesson(request, data["lesson"], area=data.get("area") or "other", question=data.get("question"),
                        checks=checks, status="rule" if checks else "open", path=path)


def _area(poly) -> float:
    pts = [(float(p[0]), float(p[1])) for p in poly or []]
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))) / 2.0


def building_facts(building: dict, architect: Optional[dict] = None) -> dict:
    """What the AI sees of a building (pure): rooms with their area, open-air flag, furniture (id, type, source,
    the model's wood tone and metal) and decor types; the architect's counts per rule."""
    from wenart.blender.outdoor import OPEN_AIR_ROOMS
    furn: dict = {}
    for f in building.get("furniture") or []:
        if f.get("build") is not False:
            item = {"id": f.get("id"), "type": str(f.get("type")), "source": f.get("source")}
            taste = (f.get("asset") or {}).get("taste") or {}
            for k in ("wood_tone", "metal"):
                if taste.get(k):
                    item[k] = taste[k]
            furn.setdefault(f.get("room_id"), []).append(item)
    dec: dict = {}
    for d in building.get("decor") or []:
        dec.setdefault(d.get("room_id"), []).append(str(d.get("type")))
    rooms = []
    for r in building.get("rooms") or []:
        rooms.append({"id": r.get("id"), "type": r.get("room_type"), "level": r.get("level_id"),
                      "area_m2": round(_area(r.get("polygon")), 1),
                      "open_air": str(r.get("room_type") or "") in OPEN_AIR_ROOMS,
                      "furniture": sorted(furn.get(r.get("id"), []), key=lambda x: (x["type"], str(x["id"]))),
                      "decor": sorted(dec.get(r.get("id"), []))})
    counts = {q["id"]: {"status": q.get("status"), **(q.get("counts") or {})}
              for q in (architect or {}).get("questions") or []}
    return {"rooms": rooms, "architect": counts}


def check_evidence(architect: Optional[dict], checks, limit: int = EVIDENCE_PER_CHECK) -> dict:
    """``{check id: {"question", "status", "counts", "found": [...]}}`` of the architect's rules that test a
    lesson (pure): what each check found per element, the open and changed findings first."""
    by = {q["id"]: q for q in (architect or {}).get("questions") or []}
    order = {"open": 0, "answered": 1, "changed": 2, "ok": 3}
    out = {}
    for c in checks or []:
        q = by.get(c)
        if q is None:
            continue
        answers = sorted(q.get("answers") or [], key=lambda a: order.get(str(a.get("status")), 4))
        out[c] = {"question": q.get("question"), "status": q.get("status"), "counts": q.get("counts"),
                  "found": [f"{a.get('element')}: {a.get('found')} ({a.get('status')})" for a in answers[:limit]]}
    return out


def review_schema(ids: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["verdicts"],
            "properties": {"verdicts": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["lesson", "verdict", "finding"],
                "properties": {"lesson": {"type": "string", "enum": ids},
                               "verdict": {"type": "string", "enum": ["ok", "issue", "unknown"]},
                               "elements": {"type": "array", "items": {"type": "string"}},
                               "finding": {"type": "string", "minLength": 2}}}}}}


def review_lessons(project_out, model, *, building_name: str = "building_final.json",
                   out=print, architect: Optional[dict] = None) -> dict:
    """The open lessons checked by the AI on the built building (module docstring), each with the evidence of the
    architect's checks for it (``architect``: the fresh review, else ``architect.json`` beside the building).
    Returns the record."""
    t0 = time.time()
    project_out = Path(project_out)
    from wenart.agent import log as LG

    building = json.loads((project_out / building_name).read_text(encoding="utf-8"))
    odir = LG.orchestrator_dir(project_out)
    arch = architect
    for name in (() if arch is not None else ("architect.json",)):
        for p in (project_out / "scene" / name, project_out / name):
            if p.is_file():
                arch = json.loads(p.read_text(encoding="utf-8"))
                break
    todo = [x for x in L.lessons() if x.get("status") in ("open", "rule") and x.get("area") != "process"]
    rec = {"asked": len(todo), "verdicts": [], "model": getattr(model, "model", ""), "seconds": None}
    if todo:
        ids = [x["id"] for x in todo]
        reply = model.structured([{"role": "system", "content": REVIEW_SYSTEM},
                                  {"role": "user", "content": json.dumps(
                                      {"lessons": [{"id": x["id"], "lesson": x["lesson"],
                                                    "question": x.get("question"),
                                                    "evidence": check_evidence(arch, x.get("checks"))}
                                                   for x in todo],
                                       "building": building_facts(building, arch)})}],
                                 review_schema(ids), call_id="lessons_review", name="lessons", kind="task")
        rec["verdicts"] = [v for v in (reply.data or {}).get("verdicts") or [] if v.get("lesson") in ids]
        rec["errors"] = list(reply.errors[:3]) if getattr(reply, "errors", None) else []
    rec["seconds"] = round(time.time() - t0, 1)
    LG.write_json_atomic(odir / REVIEW_JSON, rec)
    lines = ["# The user's lessons, checked by the AI architect", "",
             f"{rec['asked']} lesson(s) asked; model {rec['model']}.", "", "| Lesson | Verdict | Finding |",
             "|---|---|---|"]
    for v in rec["verdicts"]:
        el = f" ({', '.join(v.get('elements') or [])})" if v.get("elements") else ""
        lines.append(f"| {v['lesson']} | {v['verdict']} | {v['finding']}{el} |")
    (odir / REVIEW_MD).write_text("\n".join(lines) + "\n", encoding="utf-8")
    out(f"architect lessons: {sum(1 for v in rec['verdicts'] if v['verdict'] == 'issue')} issue(s) in "
        f"{rec['asked']} lesson(s)")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.agent.lessons")
    sub = ap.add_subparsers(dest="command", required=True)
    a = sub.add_parser("add", help="add a request or correction of the user as a lesson")
    a.add_argument("request")
    a.add_argument("--server", default=None, help="the agent model's OpenAI-style server (else stored as it is)")
    a.add_argument("--model", default=None)
    sub.add_parser("list", help="print the lessons")
    args = ap.parse_args(argv)
    if args.command == "list":
        for x in L.lessons():
            print(f"{x['id']} [{x.get('status')}] {x.get('lesson')}  (checks: {', '.join(x.get('checks') or []) or '-'})")
        return 0
    model = None
    if args.server and args.model:
        from wenart.agent.model import AgentModel
        model = AgentModel(args.server, args.model)
    rec = add_with_ai(args.request, model)
    print(f"{rec['id']} [{rec['status']}] {rec['lesson']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
