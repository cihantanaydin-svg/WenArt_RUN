"""How full a styled room is: the decor minimums scale with the style (27 Oct 2026; review: the decor minimums,
``decor_ai.ROOM_MIN`` and ``architect_details.DECOR_MIN``, were one number per room type for every style, so a japandi
or minimal room was filled like a balanced living room of nine items and a classic one was called finished at nine;
user rule: "every fix is general").

What:

- ``decor_density(recipe, family)``: the room's decor density, a word of ``recipe.DENSITY`` (sparse, balanced,
  layered): the density its recipe measured in reference photos, else the style family's
  (``vocabulary.FAMILY_DENSITY``), else balanced; with the reason.
- ``decor_minimum(room_type, base, density)``: a balanced room's number (``base``) times the density's factor
  (``DENSITY_FACTOR``), rounded half up, never under ``LIVED_IN_MIN``: the fewest items that make a room of the type
  look lived in, in any style (a living room: a rug, a light, curtains, cushions, a plant and one thing on the table).

The decor stage fills a room to its minimum (``decor_ai.room_minimum``) and keeps it in the building
(``decor_minimum``); the architect's S3 checks the same number. Pure; kept apart from ``recipe`` (which reaches the
reference search and the fit) so the build's import closure stays small.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart.style.vocabulary import FAMILY_DENSITY

DENSITY_FACTOR: dict[str, float] = {"sparse": 0.7, "balanced": 1.0, "layered": 1.3}   # recipe.DENSITY's words
LIVED_IN_MIN: dict[str, int] = {"living": 6, "bedroom": 5, "dining": 3, "kitchen": 2, "hall": 2, "bathroom": 2,
                                "wc": 1, "other": 2}


def decor_density(recipe: Optional[dict] = None, family: Optional[str] = None) -> tuple[str, str]:
    """``(density, why)`` of a room's decor (module docstring): a recipe read from photos (not a built-in one:
    ``source`` default, or no photo) gives its measured density; else the family's; else balanced."""
    rec = recipe if isinstance(recipe, dict) else {}
    value = rec.get("density").get("value") if isinstance(rec.get("density"), dict) else None
    if rec.get("source") != "default" and int(rec.get("n") or 0) > 0 and value in DENSITY_FACTOR:
        return value, f"{value}: measured in {rec.get('n')} reference photos"
    fam = str(family or "").lower()
    if fam in FAMILY_DENSITY:
        return FAMILY_DENSITY[fam], f"{FAMILY_DENSITY[fam]}: the {fam} family"
    return "balanced", "balanced: no style family"


def decor_minimum(room_type: Optional[str], base: int, density: str = "balanced") -> int:
    """The fewest decor items of a styled room (module docstring): ``base`` x ``DENSITY_FACTOR[density]`` rounded
    half up, never under ``LIVED_IN_MIN`` of the type (nor under ``base`` when that is lower); balanced: ``base``."""
    t = str(room_type or "other").lower()
    floor = min(int(base), LIVED_IN_MIN.get(t, LIVED_IN_MIN["other"]))
    return max(floor, math.floor(int(base) * DENSITY_FACTOR.get(str(density), 1.0) + 0.5))
