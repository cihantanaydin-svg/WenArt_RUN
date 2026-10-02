"""Answer schemas of the final vision check (docs/milestone5.md §5.3, §5.6).

What: the categories a model may answer, their class (door, window,
furniture, fixture, decor), the strict per-view JSON schema of the element
check, the preference schema, and the post-validation that turns an
inconsistent element answer into ``unsure``.

Categories are generated from the enums the rest of the pipeline uses, so
prompt, schema and building JSON cannot drift: ``door``/``window`` (building
schema opening types without the plain ``opening``), the building schema's
furniture types without ``unknown``, the decor types of the decor stage
(``wenart.furniture.decor.DECOR_TYPES``), then ``lamp``, ``textile``,
``other_furniture`` and ``other_object``.

Per-view schema (compiles in xgrammar 0.2.1: only enum, number/integer
bounds, array min/maxItems, objects with ``required`` and
``additionalProperties: false``)::

    {"elements": {"E1": ELEM, ...},            # every label required, nothing else
     "extras": [{"category", "box": [x0, y0, x1, y1] (0..1000), "confidence"}],  # <= 8
     "door_count": 0..20, "window_count": 0..20}
    ELEM = {"status": present|different|absent|unsure, "seen_as": CATEGORIES + nothing,
            "confidence": 0..1}
"""
from __future__ import annotations

import copy
from typing import Any, Optional

from wenart.building import load_schema
from wenart.furniture.decor import DECOR_TYPES

_BUILDING = load_schema()
OPENING_TYPES: tuple[str, ...] = tuple(t for t in _BUILDING["$defs"]["opening"]["properties"]["type"]["enum"]
                                       if t != "opening")
FURNITURE_TYPES: tuple[str, ...] = tuple(t for t in _BUILDING["$defs"]["furniture"]["properties"]["type"]["enum"]
                                         if t != "unknown")
DECOR_CATEGORIES: tuple[str, ...] = tuple(DECOR_TYPES)
EXTRA_CATEGORIES: tuple[str, ...] = ("lamp", "textile", "other_furniture", "other_object")
CATEGORIES: tuple[str, ...] = OPENING_TYPES + FURNITURE_TYPES + DECOR_CATEGORIES + EXTRA_CATEGORIES
NOTHING = "nothing"
SEEN_AS: tuple[str, ...] = CATEGORIES + (NOTHING,)
STATUSES: tuple[str, ...] = ("present", "different", "absent", "unsure")
CLASSES: tuple[str, ...] = ("door", "window", "furniture", "fixture", "decor")
NON_DECOR_CLASSES: tuple[str, ...] = ("door", "window", "furniture", "fixture")
CHOICES: tuple[str, ...] = ("first", "second", "same")

BOX_MAX = 1000
MAX_EXTRAS = 8
MAX_COUNT = 20
# A lamp whose box ends in the upper part of the image hangs on a wall or the
# ceiling (fixture); one reaching lower stands on the floor or a table
# (furniture). Only the label depends on it: both classes reject a polish.
LAMP_FIXTURE_MAX_Y1 = 400

SCHEMA_ID = "https://json-schema.org/draft/2020-12/schema"
CONFIDENCE: dict = {"type": "number", "minimum": 0, "maximum": 1}
BOX: dict = {"type": "array", "items": {"type": "number", "minimum": 0, "maximum": BOX_MAX},
             "minItems": 4, "maxItems": 4}


def category_class(category: Optional[str], box_1000=None) -> Optional[str]:
    """Class of a category: door, window, furniture, fixture or decor (None for ``nothing``/unknown).

    ``lamp`` is a fixture when its box (0..1000) ends above
    ``LAMP_FIXTURE_MAX_Y1``, else furniture (floor or table lamp).
    """
    if category in OPENING_TYPES:
        return category
    if category in FURNITURE_TYPES or category == "other_furniture":
        return "furniture"
    if category == "lamp":
        if box_1000 is not None and max(float(box_1000[1]), float(box_1000[3])) <= LAMP_FIXTURE_MAX_Y1:
            return "fixture"
        return "furniture"
    if category in DECOR_CATEGORIES or category in ("textile", "other_object"):
        return "decor"
    return None


def element_category(kind: str, element_type: Optional[str], type_unverified: bool = False) -> Optional[str]:
    """The category an expected element should be seen as (None = any furniture: type unverified)."""
    if kind in OPENING_TYPES:
        return kind
    if kind == "furniture":
        if type_unverified or element_type not in FURNITURE_TYPES:
            return None
        return element_type
    if kind == "decor":
        return element_type if element_type in DECOR_CATEGORIES else "other_object"
    return element_type if element_type in CATEGORIES else "other_object"


def view_schema(labels) -> dict:
    """The strict per-view schema: one required verdict per label, extras and counts (§5.3)."""
    labels = list(labels)
    element = {"type": "object", "additionalProperties": False, "required": ["status", "seen_as", "confidence"],
               "properties": {"status": {"enum": list(STATUSES)}, "seen_as": {"enum": list(SEEN_AS)},
                              "confidence": CONFIDENCE}}
    return {
        "$schema": SCHEMA_ID,
        "title": "ViewCheck",
        "type": "object",
        "additionalProperties": False,
        "required": ["elements", "extras", "door_count", "window_count"],
        "properties": {
            "elements": {"type": "object", "additionalProperties": False, "required": labels,
                         "properties": {label: copy.deepcopy(element) for label in labels}},
            "extras": {"type": "array", "maxItems": MAX_EXTRAS, "items": {
                "type": "object", "additionalProperties": False, "required": ["category", "box", "confidence"],
                "properties": {"category": {"enum": list(CATEGORIES)}, "box": copy.deepcopy(BOX),
                               "confidence": CONFIDENCE}}},
            "door_count": {"type": "integer", "minimum": 0, "maximum": MAX_COUNT},
            "window_count": {"type": "integer", "minimum": 0, "maximum": MAX_COUNT},
        },
    }


PREFERENCE: dict[str, Any] = {
    "$schema": SCHEMA_ID,
    "title": "Preference",
    "type": "object",
    "additionalProperties": False,
    "required": ["choice", "confidence"],
    "properties": {"choice": {"enum": list(CHOICES)}, "confidence": CONFIDENCE},
}


def preference_schema() -> dict:
    return copy.deepcopy(PREFERENCE)


def normalise_answer(answer: dict, category: Optional[str], type_unverified: bool = False) -> tuple[dict, bool]:
    """One element answer made consistent: ``(answer, changed)``.

    - present: ``seen_as`` must be the expected category (for a
      type-unverified piece, ``category`` None, anything but ``nothing``);
    - different: ``seen_as`` must name another category (not ``nothing``);
    - absent: ``seen_as`` must be ``nothing``.
    Anything else becomes ``unsure`` (the raw answer is kept under ``raw``).
    """
    status, seen = answer.get("status"), answer.get("seen_as")
    ok = True
    if status == "present":
        if type_unverified or category is None:
            ok = seen not in (None, NOTHING)
        else:
            ok = seen == category
    elif status == "different":
        ok = seen not in (None, NOTHING) and (seen != category or type_unverified or category is None)
    elif status == "absent":
        ok = seen == NOTHING
    elif status != "unsure":
        ok = False
    if ok:
        return dict(answer), False
    out = {"status": "unsure", "seen_as": seen, "confidence": answer.get("confidence"), "raw": dict(answer)}
    return out, True
