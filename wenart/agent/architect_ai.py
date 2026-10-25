"""The AI architect on the pod (user request of 25 Oct 2026: "ai on the pod needs to be clever and able to answer
the questions and make modifications accordingly").

What: ``answer_open(project_out, model)`` asks the architect's questions about the building the build will make
(``building_final.json``; ``build.prepare`` asks them, ``wenart/blender/architect.py``), sends the open ones the
user has not answered to the agent model in batches (``BATCH``; the major ones first, at most ``MAX_QUESTIONS``) and
lets it pick one choice of each question's options, or ``ask_user`` (strict JSON schema, temperature 0, the facts of
the element in the prompt). Code carries the picks out on a copy of the building and asks every question again (the
dry re-check): a pick is accepted only when its question is settled (no longer open, its action carried out) and no
major question opened that was not open before. ``keep`` settles a minor question only: a major one needs a change
or the user. The accepted answers go to ``orchestrator/architect_answers.json`` (``by: ai``, the model, the reason);
the build reads them beside the building (``architect_actions.answers_for_build``, through the build brief, so they
enter the build fingerprint) and carries them out; the user's answers always win. Every pick, accepted or refused
with the reason, is logged in ``orchestrator/architect_ai.json`` and ``architect_ai.md``.

Why: CLAUDE.md: the AI never edits geometry by hand; it chooses, code carries out, and "findings removed" (here:
questions settled) is the measure, checked by code. The user answers the questions the AI leaves open.
"""
from __future__ import annotations

import copy
import json
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.agent import log as LG
from wenart.blender import architect_actions as AA

BATCH = 12
MAX_QUESTIONS = 80
ASK_USER = "ask_user"
FINAL_BUILDING = "building_final.json"
ANSWERS_JSON = "architect_answers.json"
LOG_JSON = "architect_ai.json"
LOG_MD = "architect_ai.md"
SYSTEM = (
    "You are the architect of this house, reviewing its plan before it is built and rendered. Each question names "
    "one element (a room, a window, a door, a wall, a piece of furniture, a tree, a terrace), what the code found, "
    "and the choices that would settle it; code carries your choice out and checks it.\n"
    "Rules:\n"
    "- Choose exactly one of the question's choices, or \"ask_user\" when the facts do not show which is right.\n"
    "- A major question is settled only by a change; never answer it with a keep choice.\n"
    "- Choose a keep choice for a minor question when the drawing is plausible as it is (a separate kitchen, a "
    "thin wall onto a roof terrace, a planter on a terrace).\n"
    "- A window that sits between two rooms is almost always a reading error when the darker room has no other "
    "window: move it to that room's outer wall. A habitable room with too little glass gets larger windows.\n"
    "- Base every choice on the facts given, never on a guess; the reason is one sentence naming the deciding fact.")


def schema(keys: list[str], choices: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["answers"],
            "properties": {"answers": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["key", "choice", "reason"],
                "properties": {"key": {"type": "string", "enum": keys},
                               "choice": {"type": "string", "enum": sorted(set(choices) | {ASK_USER})},
                               "reason": {"type": "string", "minLength": 3}}}}}}


def facts(building: dict, plan: AA.Plan, element: str) -> dict:
    """What the model needs to know about an element (pure): its kind, size and neighbours."""
    if element in plan.room:
        r = plan.room[element]
        glass, wins = AA.outside_glass(plan, element)
        return {"kind": "room", "type": r.get("room_type"), "label": r.get("label") or r.get("name"),
                "level": r.get("level_id"), "area_m2": round(AA.room_area(r), 1),
                "ceiling_m": round(plan.ceiling(r.get("level_id")), 2), "outside_glass_m2": round(glass, 2),
                "outside_windows": [w["id"] for w in wins]}
    if element in plan.openings:
        o = plan.openings[element]
        sides = AA.window_sides(plan, o)
        w = plan.walls.get(o.get("wall_id")) or {}
        return {"kind": o.get("type"), "level": o.get("level_id"), "width_m": o.get("width"),
                "height_m": o.get("height"), "sill_m": o.get("sill_height"), "wall": w.get("id"),
                "wall_thickness_m": w.get("thickness"),
                "sides": [{"room": r["id"], "type": r.get("room_type")} if r else "outside" for r in sides]}
    if element in plan.walls:
        w = plan.walls[element]
        return {"kind": "wall", "level": w.get("level_id"), "thickness_m": w.get("thickness"),
                "length_m": round(plan.axis(w)[2], 2), "flagged_exterior_in_drawing": w.get("exterior")}
    piece = next((f for f in building.get("furniture") or [] if f.get("id") == element), None)
    if piece is not None:
        return {"kind": "furniture", "type": piece.get("type"), "room": piece.get("room_id"),
                "size_m": (piece.get("footprint") or {}).get("size"), "source": piece.get("source")}
    return {"kind": "other", "id": element}


def open_questions(record: dict, answered: set) -> list[dict]:
    """The open points of a review record the user and the AI have not answered, major first, as
    ``{"key", "rule", "severity", "found", "ask", "why", "options", "where"}``."""
    out = []
    for q in record.get("questions") or []:
        for a in q["answers"]:
            key = f"{q['id']}:{a['element']}"
            if not a.get("open") or key in answered or not a.get("options"):
                continue
            out.append({"key": key, "rule": q["id"], "topic": q["topic"], "severity": q.get("severity", "minor"),
                        "found": a["found"], "ask": a.get("ask"), "why": q.get("why"), "element": a["element"],
                        "options": a["options"], "where": a.get("where")})
    out.sort(key=lambda x: (x["severity"] != "major", x["rule"], str(x["element"])))
    return out


def prompt(batch: list[dict], building: dict, plan: AA.Plan) -> str:
    items = []
    for q in batch:
        items.append({"key": q["key"], "severity": q["severity"], "topic": q["topic"], "found": q["found"],
                      "question": q["ask"], "why_it_matters": q["why"],
                      "choices": [{"choice": o["choice"], "means": o["label"]} for o in q["options"]
                                  if not (q["severity"] == "major" and o["id"] == "keep")],
                      "facts": facts(building, plan, q["element"])})
    return ("Answer each question with one of its choices (or \"ask_user\"):\n"
            + json.dumps(items, indent=1, ensure_ascii=False))


def review_of(building: dict, brief: Optional[dict], ai_answers: dict) -> dict:
    """The architect's review of ``building`` with the AI's answers in (``agent_overrides.architect``; the user's
    answers come in through the brief or the project file and win). Pure."""
    from wenart.blender import build as BU

    trial = copy.deepcopy(building)
    trial.setdefault("agent_overrides", {})
    trial["agent_overrides"] = dict(trial["agent_overrides"] or {}, architect=dict(ai_answers))
    return BU.prepare(trial, "base", brief)["architect"]


def _open_keys(record: dict, severity: Optional[str] = None) -> set:
    return {f"{q['id']}:{a['element']}" for q in record.get("questions") or [] for a in q["answers"]
            if a.get("open") and (severity is None or q.get("severity") == severity)}


def settled(record: dict, key: str) -> tuple[bool, str]:
    """Whether the answer ``key`` was carried out and its question is no longer open."""
    rec = next((r for r in record.get("applied") or [] if r["key"] == key), None)
    if rec is None:
        return False, "the answer was not carried out"
    if not rec.get("ok"):
        return False, f"could not be done: {rec.get('change')}"
    if key in _open_keys(record):
        return False, "the question is still open after the change"
    return True, rec.get("change") or "settled"


def answer_open(project_out, model, *, brief: Optional[dict] = None, building_name: str = FINAL_BUILDING,
                max_questions: int = MAX_QUESTIONS, batch: int = BATCH, time_ok: Callable[[], bool] = lambda: True,
                out: Callable[[str], None] = print) -> dict:
    """Answer the open architect questions of ``project_out``'s building (module docstring). Returns the log record
    ``{"asked", "accepted", "refused", "ask_user", "entries", "seconds"}``; writes the answers and the logs."""
    t0 = time.time()
    project_out = Path(project_out)
    building = json.loads((project_out / building_name).read_text(encoding="utf-8"))
    odir = LG.orchestrator_dir(project_out)
    prev = {}
    if (odir / ANSWERS_JSON).is_file():
        prev = (json.loads((odir / ANSWERS_JSON).read_text(encoding="utf-8")) or {}).get("answers") or {}
    accepted = dict(prev)
    base = review_of(building, brief, accepted)
    user_keys = {r["key"] for r in base.get("applied") or [] if r.get("by", "user") == "user"}
    todo = open_questions(base, set(accepted) | user_keys)[:max_questions]
    plan = AA.Plan(copy.deepcopy(building))
    entries = []
    model_name = getattr(model, "model", "")
    for k in range(0, len(todo), batch):
        if not time_ok():
            out(f"architect AI: time is up after {k} of {len(todo)} question(s)")
            break
        part = todo[k:k + batch]
        keys = [q["key"] for q in part]
        choices = [o["choice"] for q in part for o in q["options"]]
        reply = model.structured([{"role": "system", "content": SYSTEM},
                                  {"role": "user", "content": prompt(part, building, plan)}],
                                 schema(keys, choices), call_id=f"architect_{k // batch + 1}", name="architect",
                                 kind="task")
        picks = {}
        for a in (reply.data or {}).get("answers") or []:
            if a.get("key") in keys and a["key"] not in picks:
                picks[a["key"]] = a
        candidates = {}
        for q in part:
            a = picks.get(q["key"])
            entry = {"key": q["key"], "severity": q["severity"], "found": q["found"], "choice": None,
                     "reason": None, "verdict": None, "why": None}
            entries.append(entry)
            if a is None:
                entry.update(verdict="no_answer", why=f"the model gave no answer ({'; '.join(reply.errors[:2])})"
                             if reply.errors else "the model gave no answer")
                continue
            entry.update(choice=a["choice"], reason=a["reason"])
            if a["choice"] == ASK_USER:
                entry.update(verdict="ask_user", why="left for the user")
                continue
            opt = next((o for o in q["options"] if o["choice"] == a["choice"]), None)
            if opt is None:
                entry.update(verdict="refused", why=f"{a['choice']!r} is not a choice of this question")
                continue
            if opt["id"] == "keep" and q["severity"] == "major":
                entry.update(verdict="refused", why="a major question is settled only by a change or by the user")
                continue
            candidates[q["key"]] = {"option": opt["id"], "params": dict(opt.get("params") or {}),
                                    "answer": a["reason"], "reason": a["reason"], "by": "ai", "model": model_name,
                                    "where": q.get("where"), "date": time.strftime("%Y-%m-%d", time.gmtime())}
        if not candidates:
            continue
        majors_before = _open_keys(base, "major")
        trial = review_of(building, brief, dict(accepted, **candidates))
        new_majors = _open_keys(trial, "major") - majors_before - set(candidates)
        verdicts = {}
        if new_majors:
            # one of them opened a major question: each is checked on its own
            for key, ans in candidates.items():
                one = review_of(building, brief, dict(accepted, **{key: ans}))
                ok, why = settled(one, key)
                more = _open_keys(one, "major") - majors_before - {key}
                verdicts[key] = (ok and not more, why if not more else f"opened {', '.join(sorted(more))}")
        else:
            verdicts = {key: settled(trial, key) for key in candidates}
        for e in entries:
            if e["key"] in verdicts:
                ok, why = verdicts[e["key"]]
                e.update(verdict="accepted" if ok else "refused", why=why)
                if ok:
                    accepted[e["key"]] = candidates[e["key"]]
        base = review_of(building, brief, accepted)
        out(f"architect AI: batch {k // batch + 1}: {sum(1 for v in verdicts.values() if v[0])} of {len(part)} "
            f"answer(s) accepted")
    rec = {"asked": len(todo), "accepted": sum(1 for e in entries if e["verdict"] == "accepted"),
           "refused": sum(1 for e in entries if e["verdict"] == "refused"),
           "ask_user": sum(1 for e in entries if e["verdict"] in ("ask_user", "no_answer")),
           "open_after": base.get("open"), "model": model_name, "entries": entries,
           "seconds": round(time.time() - t0, 1)}
    LG.write_json_atomic(odir / ANSWERS_JSON, {"_note": "the AI architect's accepted answers (wenart/agent/"
                                               "architect_ai.py); the user's answers in the project folder win",
                                               "answers": accepted})
    LG.write_json_atomic(odir / LOG_JSON, rec)
    (odir / LOG_MD).write_text(report_md(rec), encoding="utf-8")
    return rec


def report_md(rec: dict) -> str:
    lines = ["# The AI architect's answers", "",
             f"{rec['asked']} open question(s) put to {rec.get('model') or 'the agent model'}: {rec['accepted']} "
             f"answered and carried out (checked by code), {rec['refused']} refused, {rec['ask_user']} left for you; "
             f"{rec.get('open_after')} open point(s) after ({rec['seconds']:.0f} s).", "",
             "| key | severity | choice | verdict | why | the model's reason |", "|---|---|---|---|---|---|"]
    for e in rec["entries"]:
        lines.append(f"| `{e['key']}` | {e['severity']} | {e.get('choice') or ''} | {e['verdict']} | "
                     f"{(e.get('why') or '').replace('|', '/')} | {(e.get('reason') or '').replace('|', '/')} |")
    lines.append("")
    return "\n".join(lines)
