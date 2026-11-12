"""The storey count as an open point of the architect (6 Nov 2026; real21: one typical floor drawn, no count anywhere).

What: ``review(building)`` returns the architect's question N1 (``QUESTION``) about the storeys the reading inferred
(``level_inference.storeys``, ``wenart/sheets/storeys.py``): one answer on the element ``storeys`` with what was found
(the count, the rule that gave it, a guess said so), the options (``keep`` the inferred count, its ``default``, or
``storey_count`` with another count) and the question for the user; nothing when no storey was inferred.
``act_storey_count(building, key, ans, count)`` carries an answer out: the count is recorded on the building
(``level_inference.storeys.answer``); the storeys themselves are read, not built, so the next reading builds that many
(it reads the brief's ``storeys`` and the project's ``architect_answers.json`` key ``N1:storeys``).

Why: CLAUDE.md: the architect carries out the safe default of every open point and the AI architect may change a
default; the storey count of a building whose documents do not give it is such a decision, and the user must be able
to give the real number.

How: pure; the severity is the record's (major for a type default's guess, minor for a count from the documents).
"""
from __future__ import annotations

from typing import Optional

from wenart.blender import architect_actions as AA

QUESTION = {"id": "N1", "topic": "storeys",
            "question": "How many storeys does the building have? The documents draw fewer than the evidence says; the "
                        "reading inferred the rest (the top drawn plan repeats on them).",
            "why": "a block built one storey high, or two storeys too high, is the first thing the exterior views show"}


def review(building: dict) -> Optional[dict]:
    """The N1 question record (the module docstring), or None without inferred storeys."""
    st = (building.get("level_inference") or {}).get("storeys") or {}
    op = st.get("open_point") or {}
    if not op or not (st.get("inferred") or st.get("built") is False):
        return None
    q = dict(QUESTION, severity=op.get("severity") or "minor", answers=[], status="ok")
    count = int(op.get("default") or st.get("count") or 0)
    built = [i["level_id"] for i in st.get("inferred") or [] if i.get("built", True)]
    answer = st.get("answer")
    found = (f"{count} storeys from {str(st.get('rule')).replace('_', ' ')} (confidence {st.get('confidence')})"
             + (f", a guess: {st.get('guess_note')}" if st.get("guess") else "")
             + f"; inferred: {', '.join(built) or 'none'}")
    if answer:
        q["answers"].append({"element": "storeys", "found": found, "change": f"answered: {answer['count']} storeys "
                             f"({answer.get('by')}); the next reading builds them", "open": False})
        return q
    opts = [AA.option("keep", f"keep the inferred {count} storeys")]
    opts += [AA.option("storey_count", f"{n} storeys", count=n) for n in op.get("options") or [] if n != count]
    q["answers"].append({"element": "storeys", "found": found, "change": None, "open": True, "where": None,
                         "options": opts, "default": "keep",
                         "ask": f"{op.get('question')}. Give the real number in the brief (storeys: N) or answer "
                                f"{op.get('key')}."})
    q["status"] = "open"
    return q


def act_storey_count(building: dict, key: str, ans: dict, count) -> tuple[bool, str]:
    """An answer's count recorded on the building (the module docstring); False with the reason for a bad count."""
    st = (building.get("level_inference") or {}).get("storeys")
    if not isinstance(st, dict) or not st.get("open_point"):
        return False, "no storey count to answer"
    try:
        n = int(count)
    except (TypeError, ValueError):
        return False, f"not a storey count: {count!r}"
    if not 1 <= n <= 60:
        return False, f"not a storey count: {n}"
    st["answer"] = {"count": n, "by": ans.get("by", "user"), "key": key, "reason": ans.get("reason") or ans.get("answer")}
    return True, (f"the building has {n} storeys (was {st.get('count')}): recorded; the storeys are read, so the next "
                  f"reading builds them (brief storeys: {n}, or architect_answers.json {key})")
