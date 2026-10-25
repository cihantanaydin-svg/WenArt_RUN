"""What the user taught the architect (pure; 25 Oct 2026, user: "the architect should be able to ask the questions
or corrections I was asking all along the build time of this project; use AI to understand what I was asking all
along and continue to develop itself with the future requests").

What: ``architect_lessons.json`` holds every request and correction of the user as a general lesson: the user's
words, the lesson in one sentence, the question the architect asks every project, the rules that check it
(``checks``: ``architect.ORDER`` ids, or ``build`` for what the build does by itself) and its status (``rule``,
``built``, ``open``, ``process``). ``lessons()`` loads them; ``status_rows(review)`` joins them with a review's
questions (how each lesson's rules came out on this building); ``report_md`` is the section of ``architect.md``;
``prompt_text`` is what the AI architect is told the user cares about; ``add_lesson`` appends a new one (the AI
turns a request into a lesson: ``wenart.agent.lessons``).

Why: a correction the user made once must never be needed again, on any project: each becomes a rule or, until a
rule exists, a point the AI architect checks on every run and reports.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

LESSONS_FILE = Path(__file__).with_name("architect_lessons.json")
STATUSES = ("rule", "built", "open", "process")
AREAS = ("facade", "roof", "site", "openings", "access", "process", "views", "daylight", "plan", "furniture",
         "decor", "terrace", "details", "library", "reading", "lighting", "cameras", "materials", "other")


def load(path: Optional[Path] = None) -> dict:
    p = Path(path or LESSONS_FILE)
    if not p.is_file():
        return {"version": 1, "lessons": []}
    return json.loads(p.read_text(encoding="utf-8"))


def lessons(path: Optional[Path] = None) -> list[dict]:
    return [x for x in load(path).get("lessons") or [] if isinstance(x, dict) and x.get("id")]


def status_rows(review_rec: Optional[dict], path: Optional[Path] = None) -> list[dict]:
    """One row per lesson: ``{"id", "lesson", "status", "checks", "result"}``; ``result`` says how its rules came out
    on this building (``ok`` / ``fixed`` / ``open`` / ``not asked``), ``build`` for what the build does itself."""
    by = {q["id"]: q for q in (review_rec or {}).get("questions") or []}
    rows = []
    for x in lessons(path):
        results = []
        for rid in x.get("checks") or []:
            if rid == "build":
                results.append("build")
            elif rid in by:
                q = by[rid]
                c = q.get("counts") or {}
                results.append(f"{rid} {q.get('status')}" + (f" ({c.get('open', 0)} open)" if c.get("open") else ""))
            else:
                results.append(f"{rid} not asked")
        rows.append({"id": x["id"], "lesson": x.get("lesson"), "status": x.get("status"),
                     "checks": x.get("checks") or [], "result": ", ".join(results) or x.get("status")})
    return rows


def report_md(review_rec: Optional[dict], path: Optional[Path] = None) -> list[str]:
    """The ``architect.md`` section: every lesson and how its rules came out here; open lessons are named."""
    rows = status_rows(review_rec, path)
    if not rows:
        return []
    out = ["", "## What the user taught me", "",
           f"{len(rows)} lessons from the user's requests and corrections (wenart/blender/architect_lessons.json); "
           f"each is checked on every project.", "", "| Lesson | What I check | Here |", "|---|---|---|"]
    for r in rows:
        out.append(f"| {r['id']} | {r['lesson']} | {r['result']} |")
    left = [r["id"] for r in rows if r["status"] == "open"]
    if left:
        out += ["", f"Open lessons (no rule yet; the AI architect checks them): {', '.join(left)}"]
    return out


def prompt_text(path: Optional[Path] = None, limit: int = 40) -> str:
    """The lessons as the AI architect's guidance (the user's preferences, newest first)."""
    xs = [x for x in lessons(path) if x.get("status") != "process"]
    xs.sort(key=lambda x: (str(x.get("date") or ""), x["id"]), reverse=True)
    lines = [f"- {x['lesson']}" for x in xs[:limit] if x.get("lesson")]
    return "What the user has taught us (apply it to every choice):\n" + "\n".join(lines) if lines else ""


def next_id(items: list[dict]) -> str:
    n = max([int(str(x["id"])[2:]) for x in items if str(x.get("id", "")).startswith("UL")
             and str(x["id"])[2:].isdigit()] or [0])
    return f"UL{n + 1:02d}"


def add_lesson(request: str, lesson: Optional[str] = None, *, area: str = "other", question: Optional[str] = None,
               checks: Optional[list] = None, status: str = "open", path: Optional[Path] = None,
               date: Optional[str] = None) -> dict:
    """Append one lesson (``lesson`` None: the request itself, ``open``) and write the file. Returns the record."""
    p = Path(path or LESSONS_FILE)
    data = load(p)
    items = data.setdefault("lessons", [])
    rec = {"id": next_id(items), "date": date or time.strftime("%Y-%m-%d", time.gmtime()),
           "area": area if area in AREAS else "other", "status": status if status in STATUSES else "open",
           "checks": [str(c) for c in checks or []], "request": request.strip(),
           "lesson": (lesson or request).strip(), "question": (question or "").strip() or None}
    items.append(rec)
    data["updated"] = rec["date"]
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec
