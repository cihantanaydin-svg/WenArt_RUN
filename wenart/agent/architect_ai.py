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

26 Oct 2026 (user: "make the AI architect a lot more smart and let it take decisions more"):

- **Retries with the reason**: a pick code refuses (it could not be done, it left the question open, it opened a
  major question) is put to the model again with what it tried and why it failed, and the choices left
  (``RETRIES`` more times); the architect's own chains (``architect.chain_of``) settle what it still leaves open.
- **It looks at the model** (``look``): after the first build, each floor's labelled top-down view of the 3D model
  (``renders/top_<level>_plan.jpg``, ceilings off) goes to the model with the floor's rooms, openings and pieces, its
  open questions, the architect's major default decisions (the AI may choose another option of that question; its
  answer wins over the default), and the typed actions it may take on any element of the floor (``LOOK_ACTIONS``:
  a door into the air becomes a window, a window between rooms a borrowed-light window, a wrong room type ...).
  A decision of its own is ``AI.<action>:<element>``; code carries it out like an answer.
- **Nothing new breaks**: every pick and decision is accepted only when it was carried out, its question (if any)
  is settled, no major question opened that was not open, and the review of the 3D model
  (``wenart.blender.model_review``) finds no more failures in any check than before (``_verdicts``).
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
RETRIES = 2                     # a refused pick is asked again this many times, with the reason and the choices left
LOOK_MAX_ITEMS = 60             # questions and decisions per floor put to the model in the look
LOOK_LINES = 90                 # facts lines per floor (rooms, openings, pieces)
AI_RULE = "AI"                  # the key prefix of the AI's own decisions: ``AI.<action>:<element>``
# The actions the AI may take on an element of its own (``look``): element kind -> actions. Never on a drawn piece's
# existence (CLAUDE.md: a drawn piece is removed only when clearly not furniture: the agent's tools judge that).
LOOK_ACTIONS = {
    "opening": ("door_to_window", "french_window", "raise_sill", "widen_door", "interior_glazing", "high_window",
                "pass_through", "gap_to_door", "window_to_door", "snap_threshold"),
    "room": ("retype_room", "enlarge_windows"),
    "piece": ("move_piece", "mount_fixture", "remove_piece"),
    # 27 Oct 2026: an outdoor space (site.outdoor_spaces): a guard on an open edge, a roof over a covered kind
    "space": ("guard_edge", "cover_space"),
}
TOPDOWN = "renders/top_{level}_plan.jpg"
LOOK_JSON = "architect_look.json"
LOOK_MD = "architect_look.md"
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
    "window: move it to that room's outer wall; when it cannot move, keep it as a borrowed-light window (clear glass "
    "between dry rooms, a high window into a bathroom). A habitable room with too little glass gets larger windows.\n"
    "- Base every choice on the facts given, never on a guess; the reason is one sentence naming the deciding fact.")


def system_prompt() -> str:
    """``SYSTEM`` and what the user taught us (``architect_lessons.prompt_text``; 25 Oct 2026)."""
    from wenart.blender import architect_lessons as LS

    extra = LS.prompt_text()
    return SYSTEM + ("\n" + extra if extra else "")


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


def prompt(batch: list[dict], building: dict, plan: AA.Plan, tried: Optional[dict] = None) -> str:
    """The questions of a batch with their choices and the element's facts; ``tried`` (``{key: [(choice, why)]}``,
    26 Oct 2026): the picks code refused, with the reason, left out of the choices."""
    tried = tried or {}
    items = []
    for q in batch:
        gone = {c for c, _why in tried.get(q["key"], [])}
        item = {"key": q["key"], "severity": q["severity"], "topic": q["topic"], "found": q["found"],
                "question": q["ask"], "why_it_matters": q["why"],
                "choices": [{"choice": o["choice"], "means": o["label"]} for o in q["options"]
                            if not (q["severity"] == "major" and o["id"] == "keep") and o["choice"] not in gone],
                "facts": facts(building, plan, q["element"])}
        if tried.get(q["key"]):
            item["tried_and_refused"] = [{"choice": c, "why": why} for c, why in tried[q["key"]]]
        items.append(item)
    head = "Answer each question with one of its choices (or \"ask_user\")"
    if tried:
        head += ("; a question with \"tried_and_refused\" was answered before and code could not carry that out or "
                 "it broke something (the reason is given): choose another of its choices")
    return head + ":\n" + json.dumps(items, indent=1, ensure_ascii=False)


def prep_of(building: dict, brief: Optional[dict], ai_answers: dict) -> dict:
    """``build.prepare`` of ``building`` with the AI's answers in (``agent_overrides.architect``; the user's answers
    come in through the brief or the project file and win). Pure."""
    from wenart.blender import build as BU

    trial = copy.deepcopy(building)
    trial.setdefault("agent_overrides", {})
    trial["agent_overrides"] = dict(trial["agent_overrides"] or {}, architect=dict(ai_answers))
    return BU.prepare(trial, "base", brief)


def review_of(building: dict, brief: Optional[dict], ai_answers: dict) -> dict:
    """The architect's review of ``building`` with the AI's answers in (``prep_of``). Pure."""
    return prep_of(building, brief, ai_answers)["architect"]


def model_counts(prep: dict) -> dict:
    """26 Oct 2026: the failures per check of the review of the model the plan would build
    (``model_review.review`` on ``prep["building"]``; the checks that need the scene are left out). Never raises."""
    try:
        from wenart.blender import model_review as MR

        rec = MR.review(prep["building"], None, prep)
    except Exception:  # noqa: BLE001 - no measure: nothing is refused for it
        return {}
    return {k: int(v.get("failed") or 0) for k, v in (rec.get("checks") or {}).items() if v.get("status") == "ok"}


def _worse(before: dict, after: dict) -> list[str]:
    return [f"{k} {before[k]} -> {after[k]}" for k in sorted(after) if k in before and after[k] > before[k]]


def set_gaps(prep: dict) -> set:
    """26 Oct 2026: ``{(room id, message)}`` of the rooms that miss a piece of their set on the plan the build would
    make (the group checks' completeness findings: G9 a kitchen without its sink / hob / fridge, G10 a bathroom without
    its toilet, basin, shower or bath; ``furniture.group_checks``). Never raises (an empty set when it cannot tell)."""
    try:
        from wenart.furniture import group_checks as GC

        res = GC.check_building(prep["building"])
    except Exception:  # noqa: BLE001 - no measure: nothing is refused for it
        return set()
    return {(v["room_id"], v["message"]) for vs in res["rooms"].values() for v in vs
            if v.get("check") in SET_CHECKS and v.get("target") == v.get("room_id")
            and (v.get("metrics") or {}).get("missing")}


SET_CHECKS = ("G9", "G10")


def _verdicts(building: dict, brief: Optional[dict], accepted: dict, candidates: dict, base_prep: dict) -> dict:
    """``{key: (ok, why)}`` for ``candidates`` on top of ``accepted`` (module docstring "nothing new breaks"): carried
    out (and its question settled), no major question opened, the model review no worse, and (26 Oct 2026, real06:
    the AI removed the main bathroom's only shower, "the bathroom already has a shower" being the shower room's) no
    room loses a piece of its set (``set_gaps``). When the candidates together break something, each is checked on its
    own."""
    majors_before = _open_keys(base_prep["architect"], "major")
    counts_before = model_counts(base_prep)
    gaps_before = set_gaps(base_prep)

    def judge(prep: dict, keys) -> dict:
        out = {}
        new_majors = _open_keys(prep["architect"], "major") - majors_before - set(keys)
        worse = _worse(counts_before, model_counts(prep)) if counts_before else []
        new_gaps = sorted(set_gaps(prep) - gaps_before)
        for key in keys:
            ok, why = settled(prep["architect"], key)
            if ok and new_majors:
                ok, why = False, f"opened {', '.join(sorted(new_majors))}"
            elif ok and worse:
                ok, why = False, f"the model review finds more: {'; '.join(worse)}"
            elif ok and new_gaps:
                ok, why = False, "a room loses a piece of its set: " + "; ".join(f"{r}: {m}" for r, m in new_gaps)
            out[key] = (ok, why)
        return out

    together = judge(prep_of(building, brief, dict(accepted, **candidates)), candidates)
    if len(candidates) == 1 or all(ok for ok, _why in together.values()) or \
            not any(why.startswith(("opened", "the model review", "a room loses")) for _ok, why in together.values()):
        return together
    out = {}
    for key, ans in candidates.items():
        out.update(judge(prep_of(building, brief, dict(accepted, **{key: ans})), [key]))
    return out


def _open_keys(record: dict, severity: Optional[str] = None) -> set:
    return {f"{q['id']}:{a['element']}" for q in record.get("questions") or [] for a in q["answers"]
            if a.get("open") and (severity is None or q.get("severity") == severity)}


def settled(record: dict, key: str) -> tuple[bool, str]:
    """Whether the answer ``key`` was carried out and its question is no longer open (an AI decision of its own,
    ``AI.<action>:<element>``, has no question: it must have changed something)."""
    rec = next((r for r in record.get("applied") or [] if r["key"] == key), None)
    if rec is None:
        return False, "the answer was not carried out"
    if not rec.get("ok"):
        return False, f"could not be done: {rec.get('change')}"
    if key.startswith(AI_RULE + ".") and not rec.get("change"):
        return False, "it changed nothing"
    if key in _open_keys(record):
        return False, "the question is still open after the change"
    return True, rec.get("change") or "settled"


def answer_open(project_out, model, *, brief: Optional[dict] = None, building_name: str = FINAL_BUILDING,
                max_questions: int = MAX_QUESTIONS, batch: int = BATCH, time_ok: Callable[[], bool] = lambda: True,
                out: Callable[[str], None] = print, retries: int = RETRIES) -> dict:
    """Answer the open architect questions of ``project_out``'s building (module docstring). Returns the log record
    ``{"asked", "accepted", "refused", "ask_user", "entries", "seconds"}``; writes the answers and the logs. A refused
    pick is asked again ``retries`` times with the reason (26 Oct 2026)."""
    t0 = time.time()
    project_out = Path(project_out)
    building = json.loads((project_out / building_name).read_text(encoding="utf-8"))
    odir = LG.orchestrator_dir(project_out)
    accepted = dict(_saved_answers(odir))
    base_prep = prep_of(building, brief, accepted)
    base = base_prep["architect"]
    user_keys = {r["key"] for r in base.get("applied") or [] if r.get("by", "user") == "user"}
    todo = open_questions(base, set(accepted) | user_keys)[:max_questions]
    plan = AA.Plan(copy.deepcopy(building))
    entries: dict = {}
    model_name = getattr(model, "model", "")
    for k in range(0, len(todo), batch):
        part = todo[k:k + batch]
        tried: dict = {}
        pending = list(part)
        for attempt in range(1 + max(0, int(retries))):
            if not pending:
                break
            if not time_ok():
                out(f"architect AI: time is up after {k} of {len(todo)} question(s)")
                break
            base_prep = _ask_round(model, pending, building, brief, plan, accepted, base_prep, entries, tried,
                                   call_id=f"architect_{k // batch + 1}" + (f"_retry{attempt}" if attempt else ""),
                                   model_name=model_name)
            pending = _retry_list(pending, entries, tried, base_prep["architect"])
        out(f"architect AI: batch {k // batch + 1}: {sum(1 for q in part if entries.get(q['key'], {}).get('verdict') == 'accepted')} "
            f"of {len(part)} answer(s) accepted")
    rows = list(entries.values())
    rec = {"asked": len(todo), "accepted": sum(1 for e in rows if e["verdict"] == "accepted"),
           "refused": sum(1 for e in rows if e["verdict"] == "refused"),
           "ask_user": sum(1 for e in rows if e["verdict"] in ("ask_user", "no_answer")),
           "retried": sum(1 for e in rows if len(e.get("attempts") or []) > 1),
           "open_after": base_prep["architect"].get("open"), "model": model_name, "entries": rows,
           "seconds": round(time.time() - t0, 1)}
    _save_answers(odir, accepted)
    LG.write_json_atomic(odir / LOG_JSON, rec)
    (odir / LOG_MD).write_text(report_md(rec), encoding="utf-8")
    rec["review"] = base_prep["architect"]  # not logged: the architect's review after the answers (lessons check)
    return rec


def _saved_answers(odir: Path) -> dict:
    if (odir / ANSWERS_JSON).is_file():
        return (json.loads((odir / ANSWERS_JSON).read_text(encoding="utf-8")) or {}).get("answers") or {}
    return {}


def _save_answers(odir: Path, accepted: dict) -> None:
    LG.write_json_atomic(odir / ANSWERS_JSON, {"_note": "the AI architect's accepted answers (wenart/agent/"
                                               "architect_ai.py); the user's answers in the project folder win",
                                               "answers": accepted})


def _answer(opt: dict, reason: str, model_name: str, where) -> dict:
    return {"option": opt["id"], "params": dict(opt.get("params") or {}), "choice": opt["choice"], "answer": reason,
            "reason": reason, "by": "ai", "model": model_name, "where": where,
            "date": time.strftime("%Y-%m-%d", time.gmtime())}


def _ask_round(model, pending: list[dict], building: dict, brief, plan, accepted: dict, base_prep: dict,
               entries: dict, tried: dict, *, call_id: str, model_name: str) -> dict:
    """One call for the ``pending`` questions; the picks code accepts go into ``accepted`` (in place); every pick
    is logged in ``entries``; a refused pick goes into ``tried`` with the reason. Returns the plan after."""
    keys = [q["key"] for q in pending]
    choices = [o["choice"] for q in pending for o in q["options"]
               if o["choice"] not in {c for c, _w in tried.get(q["key"], [])}]
    reply = model.structured([{"role": "system", "content": system_prompt()},
                              {"role": "user", "content": prompt(pending, building, plan, tried)}],
                             schema(keys, choices), call_id=call_id, name="architect", kind="task")
    picks = {}
    for a in (reply.data or {}).get("answers") or []:
        if a.get("key") in keys and a["key"] not in picks:
            picks[a["key"]] = a
    candidates = {}
    for q in pending:
        e = entries.setdefault(q["key"], {"key": q["key"], "severity": q["severity"], "found": q["found"],
                                          "choice": None, "reason": None, "verdict": None, "why": None,
                                          "attempts": []})
        a = picks.get(q["key"])
        if a is None:
            if e["verdict"] is None:
                e.update(verdict="no_answer", why=f"the model gave no answer ({'; '.join(reply.errors[:2])})"
                         if reply.errors else "the model gave no answer")
            continue
        e["attempts"].append({"choice": a["choice"], "reason": a["reason"]})
        e.update(choice=a["choice"], reason=a["reason"])
        if a["choice"] == ASK_USER:
            e.update(verdict="ask_user", why="left for the user")
            continue
        opt = next((o for o in q["options"] if o["choice"] == a["choice"]), None)
        if opt is None:
            e.update(verdict="refused", why=f"{a['choice']!r} is not a choice of this question")
        elif opt["id"] == "keep" and q["severity"] == "major":
            e.update(verdict="refused", why="a major question is settled only by a change or by the user")
        else:
            candidates[q["key"]] = _answer(opt, a["reason"], model_name, q.get("where"))
            continue
        tried.setdefault(q["key"], []).append((a["choice"], e["why"]))
    if not candidates:
        return base_prep
    for key, (ok, why) in _verdicts(building, brief, accepted, candidates, base_prep).items():
        entries[key].update(verdict="accepted" if ok else "refused", why=why)
        entries[key]["attempts"][-1].update(verdict=entries[key]["verdict"], why=why)
        if ok:
            accepted[key] = candidates[key]
        else:
            tried.setdefault(key, []).append((candidates[key]["choice"], why))
    return prep_of(building, brief, accepted)


def _retry_list(pending: list[dict], entries: dict, tried: dict, record: dict) -> list[dict]:
    """The refused questions still open with a choice left to try (26 Oct 2026)."""
    still = _open_keys(record)
    out = []
    for q in pending:
        e = entries.get(q["key"]) or {}
        gone = {c for c, _w in tried.get(q["key"], [])}
        left = [o for o in q["options"] if o["choice"] not in gone and not (q["severity"] == "major" and o["id"] == "keep")]
        if e.get("verdict") == "refused" and q["key"] in still and left:
            out.append(q)
    return out


# --------------------------------------------------------------------------
# 26 Oct 2026: the AI architect looks at the model (module docstring)
# --------------------------------------------------------------------------

LOOK_SYSTEM = (
    "You are the architect of this house. You look at one floor of its 3D model from above, before anyone sees the "
    "renders, and you decide what this floor needs to make sense and to read as a well-designed, stylish home: doors "
    "that lead somewhere, windows that look outside or bring borrowed light on purpose, rooms of the right type, "
    "fixtures at their working height, pieces clear of doorways and windows.\n"
    "Rules:\n"
    "- Part A (questions): answer each with one of its choices, or \"ask_user\" when the facts and the image do not "
    "show which is right. A major question is settled only by a change.\n"
    "- Part B (the architect's default decisions): answer \"confirm\" to keep the decision, or choose another of its "
    "choices when the image shows it is wrong.\n"
    "- Part C (your own decisions): list only clear cases the image and the facts show, each one action from the "
    "allowed list on one element of this floor (use its id), with value = the room type for retype_room, else \"\". "
    "Code carries every decision out and refuses one that breaks something; a refused decision is reported.\n"
    "- Every reason is one sentence naming the deciding fact.")


def look_schema(keys: list[str], choices: list[str], actions: list[str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["answers", "decisions"],
            "properties": {
                "answers": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False, "required": ["key", "choice", "reason"],
                    "properties": {"key": {"type": "string", "enum": keys or ["none"]},
                                   "choice": {"type": "string",
                                              "enum": sorted(set(choices) | {ASK_USER, "confirm"})},
                                   "reason": {"type": "string", "minLength": 3}}}},
                "decisions": {"type": "array", "maxItems": 20, "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["action", "element", "value", "reason"],
                    "properties": {"action": {"type": "string", "enum": actions},
                                   "element": {"type": "string", "minLength": 2},
                                   "value": {"type": "string"},
                                   "reason": {"type": "string", "minLength": 3}}}}}}


def _level_of(plan: AA.Plan, building: dict, element: str) -> Optional[str]:
    if element in plan.room:
        return plan.room[element].get("level_id")
    if element in plan.openings:
        return plan.openings[element].get("level_id")
    piece = next((f for f in building.get("furniture") or [] if f.get("id") == element), None)
    if piece is None:                              # 27 Oct 2026: an outdoor space's level
        space = next((s for s in (building.get("site") or {}).get("outdoor_spaces") or [] if s.get("id") == element),
                     None)
        if space is not None:
            return space.get("level_id")
    return (piece or {}).get("level_id") or (plan.room.get((piece or {}).get("room_id")) or {}).get("level_id")


def floor_facts(built: dict, plan: AA.Plan, level_id: str, limit: int = LOOK_LINES) -> list[str]:
    """The rooms, openings and built pieces of one floor, one line each (pure)."""
    lines = []
    for r in built.get("rooms") or []:
        if r.get("level_id") != level_id:
            continue
        glass, _wins = AA.outside_glass(plan, r["id"]) if r["id"] in plan.room else (0.0, [])
        lines.append(f"- room {r['id']} ({r.get('label') or r.get('name') or ''}): {r.get('room_type')}, "
                     f"{AA.room_area(r):.1f} m2, {glass:.1f} m2 of glass to the outside")
    for o in built.get("openings") or []:
        if o.get("level_id") != level_id:
            continue
        sides = [("outside" if (r is None or AA.Plan.is_outside(r)) else f"{r['id']} ({r.get('room_type')})")
                 for r in AA.window_sides(plan, o)] if o["id"] in plan.openings else []
        sill = o.get("sill_height")
        lines.append(f"- {o['id']} {o.get('type')}: {float(o.get('width') or 0):.2f} m wide"
                     + (f", sill {float(sill):.2f} m" if sill is not None and o.get("type") == "window" else "")
                     + (f", between {' and '.join(sides)}" if sides else ""))
    for f in built.get("furniture") or []:
        room = plan.room.get(f.get("room_id")) or {}
        if room.get("level_id") != level_id or f.get("build") is False:
            continue
        size = (f.get("footprint") or {}).get("size") or [0, 0]
        lines.append(f"- {f['id']} {f.get('type')} {float(size[0]):.2f} x {float(size[1]):.2f} m in {f.get('room_id')}"
                     f" ({f.get('source') or 'from_documents'})")
    return lines[:limit]


def raw_review(building: dict, brief: Optional[dict], ai_answers: dict) -> dict:
    """The architect's review before its own defaults are carried out (``build.prepare_once``): the questions the
    defaults answered, with their options. Pure."""
    from wenart.blender import build as BU

    trial = copy.deepcopy(building)
    trial["agent_overrides"] = dict(trial.get("agent_overrides") or {}, architect=dict(ai_answers))
    return BU.prepare_once(trial, "base", brief)["architect"]


def _decided(raw: dict, defaults: dict, answered: set) -> list[dict]:
    """The architect's default decisions on major questions (part B of the look), with the options of the question
    before the default was carried out (``raw_review``): ``{"key", "element", "found", "decided", "options", "where",
    "severity", "rule", "topic"}``."""
    out = []
    for q in raw.get("questions") or []:
        if q.get("severity") != "major":
            continue
        for a in q.get("answers") or []:
            key = f"{q['id']}:{a['element']}"
            d = defaults.get(key)
            if d is None or key in answered or not a.get("open") or not a.get("options"):
                continue
            out.append({"key": key, "rule": q["id"], "topic": q["topic"], "severity": "major", "element": a["element"],
                        "found": a.get("found"), "decided": d.get("choice") or d.get("option"),
                        "options": a["options"], "where": a.get("where") or d.get("where")})
    return out


def _where_of(plan: AA.Plan, building: dict, element: str, level_id: str) -> dict:
    if element in plan.openings:
        c = plan.openings[element].get("center") or (0, 0)
        kind = plan.openings[element].get("type") or "opening"
    elif element in plan.room:
        from wenart import geometry as G
        poly = plan.room[element].get("polygon") or [(0, 0)]
        c = G.polygon_centroid(poly) if len(poly) >= 3 else poly[0]
        kind = "room"
    else:
        piece = next((f for f in building.get("furniture") or [] if f.get("id") == element), {})
        c = (piece.get("footprint") or {}).get("center") or (0, 0)
        kind = "furniture"
        space = None if piece else next((s for s in (building.get("site") or {}).get("outdoor_spaces") or []
                                         if s.get("id") == element), None)
        if space is not None and len(space.get("polygon") or []) >= 3:      # 27 Oct 2026: an outdoor space
            from wenart import geometry as G
            c = G.polygon_centroid(space["polygon"])
            kind = "space"
    return {"kind": kind, "level_id": level_id, "centre": [round(float(c[0]), 3), round(float(c[1]), 3)]}


def _decision(d: dict, plan: AA.Plan, built: dict, level_id: str) -> tuple[Optional[str], Optional[dict], str]:
    """``(key, answer, why_not)`` of one of the AI's own decisions (``AI.<action>:<element>``), or a reason it is
    not a valid one (the element is not on this floor, the action does not fit it, a drawn piece is never removed)."""
    action, element, value = d.get("action"), str(d.get("element") or ""), str(d.get("value") or "")
    if element in plan.openings:
        kind = "opening"
    elif element in plan.room:
        kind = "room"
    elif any(f.get("id") == element for f in built.get("furniture") or []):
        kind = "piece"
    elif any(s.get("id") == element for s in (built.get("site") or {}).get("outdoor_spaces") or []):
        kind = "space"
    else:
        return None, None, f"{element} is no element of the plan"
    if action not in LOOK_ACTIONS[kind]:
        return None, None, f"{action} does not fit a {kind}"
    if _level_of(plan, built, element) != level_id:
        return None, None, f"{element} is not on {level_id}"
    params: dict = {}
    if action == "retype_room":
        if value not in AA.ROOM_TYPES:
            return None, None, f"{value!r} is no room type ({', '.join(AA.ROOM_TYPES)})"
        if str(plan.room[element].get("room_type") or "") == value:
            return None, None, f"{element} is a {value} already"
        params["room_type"] = value
    if action == "door_to_window" and kind == "opening":
        o = plan.openings[element]
        outside = any(r is None or AA.Plan.is_outside(r) for r in AA.window_sides(plan, o))
        lowest = min((float(lv.get("elevation") or 0.0) for lv in plan.levels.values()), default=0.0)
        here = float((plan.levels.get(o.get("level_id")) or {}).get("elevation") or 0.0)
        if outside and here <= lowest + 0.5:
            return None, None, (f"{element} is a ground-floor door to the outside: an entrance is never made a window "
                                f"by a decision")
    if action == "guard_edge":
        try:
            edges = AA.guard_segments(json.loads(value)) if value else []
        except ValueError:
            edges = []
        if not edges:
            return None, None, (f"guard_edge needs value [[x0, y0], [x1, y1]] (the edge) or a list of edges, "
                                f"got {value!r}")
        params["edges"] = edges
    if action == "remove_piece":
        piece = next(f for f in built.get("furniture") or [] if f.get("id") == element)
        if piece.get("source") in (None, "from_documents"):
            return None, None, f"{element} is drawn: a drawn piece is never removed by a decision (CLAUDE.md)"
    key = f"{AI_RULE}.{action}:{element}"
    opt = {"id": action, "choice": action if not value or action != "retype_room" else f"{action}:{value}",
           "params": params}
    return key, {"opt": opt, "where": _where_of(plan, built, element, level_id)}, ""


def look(project_out, model, *, brief: Optional[dict] = None, building_name: str = FINAL_BUILDING,
         time_ok: Callable[[], bool] = lambda: True, out: Callable[[str], None] = print,
         retries: int = 1, max_items: int = LOOK_MAX_ITEMS) -> dict:
    """The AI architect looks at each floor of the model and decides (module docstring). Returns ``{"levels",
    "asked", "accepted", "refused", "decisions", "entries", "seconds"}``; the accepted answers and decisions join
    ``orchestrator/architect_answers.json`` (the next build carries them out); logs ``architect_look.json`` / ``.md``."""
    t0 = time.time()
    project_out = Path(project_out)
    building = json.loads((project_out / building_name).read_text(encoding="utf-8"))
    odir = LG.orchestrator_dir(project_out)
    accepted = dict(_saved_answers(odir))
    model_name = getattr(model, "model", "")
    base_prep = prep_of(building, brief, accepted)
    entries: list[dict] = []
    levels = [lv.get("id") for lv in base_prep["building"].get("levels") or []]
    for lv in levels:
        if not time_ok():
            out(f"architect look: time is up before {lv}")
            break
        built = base_prep["building"]
        plan = AA.Plan(copy.deepcopy(built))
        record = base_prep["architect"]
        user_keys = {r["key"] for r in record.get("applied") or [] if r.get("by", "user") == "user"}
        answered = set(accepted) | user_keys
        qs = [q for q in open_questions(record, answered) if (q.get("where") or {}).get("level_id") == lv
              or _level_of(plan, built, q["element"]) == lv]
        decided = [d for d in _decided(raw_review(building, brief, accepted), base_prep.get("architect_defaults")
                                       or {}, answered)
                   if (d.get("where") or {}).get("level_id") == lv or _level_of(plan, built, d["element"]) == lv]
        # the major questions, then the architect's major decisions, then the minor questions
        items = ([q for q in qs if q["severity"] == "major"] + decided
                 + [q for q in qs if q["severity"] != "major"])[:max_items]
        image = project_out / TOPDOWN.format(level=lv)
        actions = sorted({a for acts in LOOK_ACTIONS.values() for a in acts})
        tried: dict = {}
        refused_decisions: list[str] = []
        for attempt in range(1 + max(0, int(retries))):
            text = _look_prompt(lv, items, built, plan, tried, refused_decisions, image.is_file())
            content = text
            if image.is_file():
                from wenart.agent.model import user_message
                msg = user_message(text, [image], [f"Image 1: the model of level {lv} from above"])
            else:
                msg = {"role": "user", "content": content}
            keys = [q["key"] for q in items]
            choices = [o["choice"] for q in items for o in q["options"]]
            reply = model.structured([{"role": "system", "content": LOOK_SYSTEM + _lessons()}, msg],
                                     look_schema(keys, choices, actions), call_id=f"architect_look_{lv}"
                                     + (f"_retry{attempt}" if attempt else ""), name="architect_look", kind="task")
            data = reply.data or {}
            candidates, meta = {}, {}
            by_key = {q["key"]: q for q in items}
            for a in data.get("answers") or []:
                q = by_key.get(a.get("key"))
                if q is None or a["key"] in candidates or a["key"] in meta:
                    continue
                e = {"level": lv, "kind": "decided" if "decided" in q else "question", "key": a["key"],
                     "choice": a["choice"], "reason": a["reason"], "verdict": None, "why": None}
                meta[a["key"]] = e
                entries.append(e)
                if a["choice"] == "confirm":
                    e.update(verdict="confirmed" if "decided" in q else "refused",
                             why="the default decision stands" if "decided" in q else "confirm is no answer")
                    continue
                if a["choice"] == ASK_USER:
                    e.update(verdict="ask_user", why="left for the user")
                    continue
                opt = next((o for o in q["options"] if o["choice"] == a["choice"]), None)
                if opt is None or (opt["id"] == "keep" and q["severity"] == "major") or \
                        a["choice"] in {c for c, _w in tried.get(a["key"], [])}:
                    e.update(verdict="refused", why="not a choice of this question" if opt is None else
                             "a major question is settled only by a change" if opt["id"] == "keep" else "tried before")
                    continue
                if q.get("decided") == a["choice"]:
                    e.update(verdict="confirmed", why="the same as the default decision")
                    continue
                candidates[a["key"]] = _answer(opt, a["reason"], model_name, q.get("where"))
            for d in data.get("decisions") or []:
                key, ans, why_not = _decision(d, plan, built, lv)
                e = {"level": lv, "kind": "own", "key": key or f"{AI_RULE}.{d.get('action')}:{d.get('element')}",
                     "choice": d.get("action"), "value": d.get("value"), "reason": d.get("reason"), "verdict": None,
                     "why": None}
                entries.append(e)
                if key is None:
                    e.update(verdict="refused", why=why_not)
                    refused_decisions.append(f"{e['key']}: {why_not}")
                    continue
                if key in accepted or key in candidates:
                    e.update(verdict="refused", why="decided already")
                    continue
                meta[key] = e
                candidates[key] = dict(_answer(ans["opt"], d.get("reason") or "", model_name, ans["where"]),
                                       own=True)
            if candidates:
                for key, (ok, why) in _verdicts(building, brief, accepted, candidates, base_prep).items():
                    meta[key].update(verdict="accepted" if ok else "refused", why=why)
                    if ok:
                        accepted[key] = candidates[key]
                    elif key in by_key:
                        tried.setdefault(key, []).append((candidates[key]["choice"], why))
                    else:
                        refused_decisions.append(f"{key}: {why}")
                base_prep = prep_of(building, brief, accepted)
            items = [q for q in items if q["key"] in tried and q["key"] in _open_keys(base_prep["architect"])]
            if not items and not refused_decisions:
                break
            if attempt >= retries:
                break
        _save_answers(odir, accepted)
    rec = {"levels": levels, "asked": sum(1 for e in entries if e["kind"] != "own"),
           "decisions": sum(1 for e in entries if e["kind"] == "own"),
           "accepted": sum(1 for e in entries if e["verdict"] == "accepted"),
           "confirmed": sum(1 for e in entries if e["verdict"] == "confirmed"),
           "refused": sum(1 for e in entries if e["verdict"] == "refused"),
           "model": model_name, "entries": entries, "open_after": base_prep["architect"].get("open"),
           "seconds": round(time.time() - t0, 1)}
    LG.write_json_atomic(odir / LOOK_JSON, rec)
    (odir / LOOK_MD).write_text(look_md(rec), encoding="utf-8")
    return rec


def _lessons() -> str:
    from wenart.blender import architect_lessons as LS

    extra = LS.prompt_text()
    return ("\n" + extra) if extra else ""


def _look_prompt(level_id: str, items: list[dict], built: dict, plan: AA.Plan, tried: dict, refused: list[str],
                 with_image: bool) -> str:
    qa, qb = [], []
    for q in items:
        gone = {c for c, _w in tried.get(q["key"], [])}
        item = {"key": q["key"], "topic": q["topic"], "found": q["found"],
                "choices": [{"choice": o["choice"], "means": o["label"]} for o in q["options"]
                            if not (q["severity"] == "major" and o["id"] == "keep") and o["choice"] not in gone]}
        if tried.get(q["key"]):
            item["tried_and_refused"] = [{"choice": c, "why": why} for c, why in tried[q["key"]]]
        if "decided" in q:
            item["decided"] = q["decided"]
            qb.append(item)
        else:
            item["question"] = q.get("ask")
            qa.append(item)
    acts = "; ".join(f"{a} ({AA.ACTIONS[a]})" for kind, acts_ in LOOK_ACTIONS.items() for a in acts_
                     if a in AA.ACTIONS)
    parts = [(f"Image 1 is the 3D model of level {level_id} seen from above at an angle: ceilings off, walls cut, "
              "rooms named, windows are blue lines with their ids." if with_image else
              f"Level {level_id} (no image of it: decide from the facts)."),
             "", f"The floor (rooms, doors and windows, pieces):", *floor_facts(built, plan, level_id),
             "", "Part A, questions:", json.dumps(qa, indent=1, ensure_ascii=False) if qa else "none",
             "", "Part B, the architect's default decisions (confirm or change):",
             json.dumps(qb, indent=1, ensure_ascii=False) if qb else "none",
             "", "Part C, your own decisions: allowed actions by element (opening / room / piece): " + acts]
    if refused:
        parts += ["", "Decisions of yours code refused before (do not repeat them): " + "; ".join(refused[:20])]
    return "\n".join(parts)


def look_md(rec: dict) -> str:
    lines = ["# The AI architect looks at the model", "",
             f"{rec['asked']} question(s) and default decision(s) put to {rec.get('model') or 'the agent model'} with "
             f"each floor's view of the model, {rec['decisions']} decision(s) of its own: {rec['accepted']} carried "
             f"out (checked by code: settled, no new major point, the model review no worse), {rec['confirmed']} "
             f"default(s) confirmed, {rec['refused']} refused; {rec.get('open_after')} open point(s) after "
             f"({rec['seconds']:.0f} s).", "",
             "| level | kind | key | choice | verdict | why | the model's reason |", "|---|---|---|---|---|---|---|"]
    for e in rec["entries"]:
        choice = e.get("choice") or ""
        if e.get("value"):
            choice += f" ({e['value']})"
        lines.append(f"| {e['level']} | {e['kind']} | `{e['key']}` | {choice} | {e['verdict']} | "
                     f"{str(e.get('why') or '').replace('|', '/')} | {str(e.get('reason') or '').replace('|', '/')} |")
    lines.append("")
    return "\n".join(lines)


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
