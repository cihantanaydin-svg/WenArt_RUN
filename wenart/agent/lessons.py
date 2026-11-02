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
# 2 Nov 2026 (real10 run 20261102-122729-full: "maximum context length is 32768 tokens ... your prompt contains at
# least 30721 input tokens": 9 floors of rooms and 160 lessons in one prompt): the review fits the agent model's
# context. The building facts leave out a typical floor's copies (their rooms are the typical floor's) and, when still
# over FACTS_SHARE of the budget, count the furniture and decor per type; the lessons are asked in batches that fit
# what is left. The budget: the server's context less the answer and a margin, at JSON_CHARS_PER_TOKEN.
JSON_CHARS_PER_TOKEN = 2.0       # = loop.CHARS_PER_TOKEN_ADDED: JSON is about 2.3 characters per token, counted low
PROMPT_MARGIN_TOKENS = 1500
FACTS_SHARE = 0.6
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


def prompt_chars_max() -> int:
    """The characters a review prompt may hold (the comment above)."""
    from wenart.agent import model as AM

    return int((AM.DEFAULT_MAX_MODEL_LEN - AM.CRITIC_MAX_TOKENS - PROMPT_MARGIN_TOKENS) * JSON_CHARS_PER_TOKEN)


def compact_facts(facts: dict) -> dict:
    """The facts with each room's furniture and decor counted per type (pure): ``{"type": n}``, the wood tones and
    metals of its furniture as sets."""
    rooms = []
    for r in facts.get("rooms") or []:
        furn: dict = {}
        tones, metals = set(), set()
        for f in r.get("furniture") or []:
            furn[f["type"]] = furn.get(f["type"], 0) + 1
            tones.update([f["wood_tone"]] if f.get("wood_tone") else [])
            metals.update([f["metal"]] if f.get("metal") else [])
        dec: dict = {}
        for t in r.get("decor") or []:
            dec[t] = dec.get(t, 0) + 1
        row = dict(r, furniture=furn, decor=dec)
        if tones:
            row["wood_tones"] = sorted(tones)
        if metals:
            row["metals"] = sorted(metals)
        rooms.append(row)
    return dict(facts, rooms=rooms, compact=True)


def review_batches(todo: list[dict], facts: dict, arch: Optional[dict], budget: Optional[int] = None) -> \
        tuple[dict, list[list[dict]]]:
    """``(facts, batches)``: the facts as sent (compact when the full ones pass FACTS_SHARE of the budget) and the
    lessons' prompt items in batches that fit the rest of the budget (at least one lesson a batch)."""
    budget = budget or prompt_chars_max()
    if len(json.dumps(facts)) > FACTS_SHARE * budget:
        facts = compact_facts(facts)
    room = max(budget - len(json.dumps(facts)) - len(REVIEW_SYSTEM), budget // 10)
    batches: list[list[dict]] = [[]]
    used = 0
    for x in todo:
        item = {"id": x["id"], "lesson": x["lesson"], "question": x.get("question"),
                "evidence": check_evidence(arch, x.get("checks"))}
        size = len(json.dumps(item)) + 2
        if batches[-1] and used + size > room:
            batches.append([])
            used = 0
        batches[-1].append(item)
        used += size
    return facts, [b for b in batches if b]


def building_facts(building: dict, architect: Optional[dict] = None) -> dict:
    """What the AI sees of a building (pure): rooms with their area, open-air flag, furniture (id, type, source,
    the model's wood tone and metal) and decor types; the architect's counts per rule. 2 Nov 2026: a typical floor's
    copies are left out (``typical_copies``: their ids), their rooms are the typical floor's."""
    from wenart.blender.outdoor import OPEN_AIR_ROOMS
    from wenart.run.forecast import looked_levels

    looked = set(looked_levels(building))
    copies = sorted(str(lv.get("id")) for lv in building.get("levels") or []
                    if isinstance(lv, dict) and lv.get("id") not in looked)
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
        if copies and r.get("level_id") not in looked:
            continue
        rooms.append({"id": r.get("id"), "type": r.get("room_type"), "level": r.get("level_id"),
                      "area_m2": round(_area(r.get("polygon")), 1),
                      "open_air": str(r.get("room_type") or "") in OPEN_AIR_ROOMS,
                      "furniture": sorted(furn.get(r.get("id"), []), key=lambda x: (x["type"], str(x["id"]))),
                      "decor": sorted(dec.get(r.get("id"), []))})
    counts = {q["id"]: {"status": q.get("status"), **(q.get("counts") or {})}
              for q in (architect or {}).get("questions") or []}
    out = {"rooms": rooms, "architect": counts}
    if copies:
        out["typical_copies"] = copies
    return out


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
        facts, batches = review_batches(todo, building_facts(building, arch), arch)
        rec["errors"] = []
        rec["batches"] = len(batches)
        if facts.get("compact"):
            rec["facts"] = "compact (furniture and decor counted per type: the full facts pass the context budget)"
        for n, batch in enumerate(batches, start=1):
            ids = [x["id"] for x in batch]
            reply = model.structured([{"role": "system", "content": REVIEW_SYSTEM},
                                      {"role": "user", "content": json.dumps({"lessons": batch, "building": facts})}],
                                     review_schema(ids), call_id=f"lessons_review_{n}" if n > 1 else "lessons_review",
                                     name="lessons", kind="task")
            rec["verdicts"] += [v for v in (reply.data or {}).get("verdicts") or [] if v.get("lesson") in ids]
            rec["errors"] += list(reply.errors[:3]) if getattr(reply, "errors", None) else []
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
