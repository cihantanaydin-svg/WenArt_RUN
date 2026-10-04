"""Realism preference, info only (docs/milestone5.md §5.6).

Both models, both orders: "Which image looks more like a real photograph of
a room?" with ``{"choice": "first|second|same", "confidence"}``. Order ``pc``
shows the polished image first, ``cp`` the Cycles render first. A polished
image is ``preferred`` when at least ``check.yaml: preference.min_votes``
(3) of the 4 answers pick it. It never changes which image is final.
"""
from __future__ import annotations

from wenart.vision_check import schemas as S

ORDERS = ("pc", "cp")        # polished first / Cycles first
LABELS = ("Image 1 (first):", "Image 2 (second):")
PROMPT = ("Which image looks more like a real photograph of a room? Answer first, second or same, with your "
          "confidence from 0 to 1. Judge only how real the photo looks, not the style or the furniture.")


def schema() -> dict:
    return S.preference_schema()


def polished_vote(order: str, choice) -> bool:
    """True when ``choice`` picks the polished image for this order."""
    return (order == "pc" and choice == "first") or (order == "cp" and choice == "second")


def votes(answers: dict, keys: list, min_votes: int) -> dict:
    """``answers``: ``{order: {key: data | None}}`` -> ``{votes, answers, asked, min_votes, preferred, calls}``."""
    calls, n_votes, n_answers = {}, 0, 0
    for k in keys:
        calls[k] = {}
        for order in ORDERS:
            data = (answers.get(order) or {}).get(k)
            choice = None if data is None else data.get("choice")
            calls[k][order] = choice
            if choice is None:
                continue
            n_answers += 1
            n_votes += polished_vote(order, choice)
    return {"votes": n_votes, "answers": n_answers, "asked": 2 * len(keys), "min_votes": int(min_votes),
            "preferred": n_votes >= int(min_votes), "calls": calls}
