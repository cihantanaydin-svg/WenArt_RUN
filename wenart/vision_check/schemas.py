"""Answer schemas of the final vision check (docs/milestone5.md §5.3, §5.6; docs/milestone6.md §6).

What: the categories a model may answer, their class (door, window,
furniture, fixture, decor), the strict per-view JSON schema of the element
check, the preference schema, and the post-validation that turns an
inconsistent element answer into ``unsure``. Milestone 6 adds the realism
A/B answer schema (``realism_schema``: one forced choice per aspect, no tie)
and the schemas of the realism files (``realism_pairs_file_schema``,
``realism_ab_schema``, ``realism_summary_schema``), see
``wenart/vision_check/realism.py``. Milestone 7 (docs/milestone7.md §8.2) adds
the realism v2 answer schema (``realism2_schema(order)``: one aspect per call,
the answer enum in the order the question names the images) and the v2
variants of the three file schemas (``version=2``).

Milestone 7 furniture types (docs/milestone7.md §0): ``stair``,
``side_table``, ``floor_lamp`` and ``potted_plant`` are categories like every
furniture type, but ``potted_plant`` has the **decor** class (an added
plant never rejects a polish, as the decor category ``plant`` today), and
``potted_plant``/``plant`` and ``floor_lamp``/``lamp`` name the same object
both ways round (``EQUIVALENT``): a drawn ``potted_plant`` seen as ``plant``,
or the decor ``plant`` seen as ``potted_plant``, counts as present instead of
"different" in ``normalise_answer``.

Milestone 8 (docs/milestone8.md §4): the decor stage's new types ``rug`` and
``wall_art`` are decor categories (class ``decor``: an added rug or picture
never rejects a polish, an expected one is never required, never asked as
furniture), and ``rug``/``textile`` are equivalent (the ``textile`` hint
says "curtain or rug").

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
# Furniture types that are decor for the extras (an added potted plant never rejects, as "plant").
DECOR_FURNITURE_TYPES: tuple[str, ...] = ("potted_plant",)
# Categories that name the same object in a photo, both ways round (review vision-2: the decor floor plant,
# expected "plant", is often seen as the M7 "potted_plant" with its hint "large potted plant standing on the floor").
# Milestone 8: the decor rug may be named "textile" (the extra category whose hint says "curtain or rug").
# Milestone 9: a table lamp may be named "lamp", a small potted plant "plant".
EQUIVALENT_PAIRS: tuple[tuple[str, str], ...] = (("potted_plant", "plant"), ("floor_lamp", "lamp"), ("rug", "textile"),
                                                 ("table_lamp", "lamp"), ("plant_small", "plant"))
# The expected category -> what it may also be seen as (symmetric, built from ``EQUIVALENT_PAIRS``).
EQUIVALENT: dict[str, tuple[str, ...]] = {}
for _a, _b in EQUIVALENT_PAIRS:
    EQUIVALENT[_a] = EQUIVALENT.get(_a, ()) + (_b,)
    EQUIVALENT[_b] = EQUIVALENT.get(_b, ()) + (_a,)
del _a, _b

SCHEMA_ID = "https://json-schema.org/draft/2020-12/schema"
CONFIDENCE: dict = {"type": "number", "minimum": 0, "maximum": 1}
BOX: dict = {"type": "array", "items": {"type": "number", "minimum": 0, "maximum": BOX_MAX},
             "minItems": 4, "maxItems": 4}


def category_class(category: Optional[str], box_1000=None) -> Optional[str]:
    """Class of a category: door, window, furniture, fixture or decor (None for ``nothing``/unknown).

    ``lamp`` is a fixture when its box (0..1000) ends above
    ``LAMP_FIXTURE_MAX_Y1``, else furniture (floor or table lamp);
    ``potted_plant`` is decor (``DECOR_FURNITURE_TYPES``).
    """
    if category in OPENING_TYPES:
        return category
    if category in DECOR_FURNITURE_TYPES:
        return "decor"
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

    - present: ``seen_as`` must be the expected category or an
      ``EQUIVALENT`` one (for a type-unverified piece, ``category`` None,
      anything but ``nothing``);
    - different: ``seen_as`` must name another category (not ``nothing``);
      an ``EQUIVALENT`` category (a potted plant seen as ``plant``, a decor
      plant seen as ``potted_plant``) is the same object: the answer becomes
      ``present`` (changed, raw kept);
    - absent: ``seen_as`` must be ``nothing``.
    Anything else becomes ``unsure`` (the raw answer is kept under ``raw``).
    """
    status, seen = answer.get("status"), answer.get("seen_as")
    same = () if category is None else (category,) + EQUIVALENT.get(category, ())
    if status == "different" and not type_unverified and category is not None and seen in same[1:]:
        return {"status": "present", "seen_as": seen, "confidence": answer.get("confidence"),
                "raw": dict(answer)}, True
    ok = True
    if status == "present":
        if type_unverified or category is None:
            ok = seen not in (None, NOTHING)
        else:
            ok = seen in same
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


# --------------------------------------------------------------------------
# Realism A/B (docs/milestone6.md §6)
# --------------------------------------------------------------------------

# The aspects in the order the model answers them (xgrammar keeps the schema's property order): the three
# evidence aspects first, the overall "photo" verdict last.
REALISM_ASPECTS: tuple[str, ...] = ("materials", "lighting", "furniture", "photo")
REALISM_WINNERS: tuple[str, ...] = ("image_1", "image_2")
REALISM_MARGINS: tuple[str, ...] = ("slight", "clear", "large")
REALISM_CUES: tuple[str, ...] = (
    "material_texture", "material_response", "contact_shadows", "light_falloff", "window_light", "exposure_colour",
    "furniture_shape", "soft_textiles", "small_objects", "imperfections", "fewer_artifacts", "camera_look",
)
REALISM_MAX_CUES = 3
# Pair sets in the order they are asked (§6.2: controls first, then m5_vs_m6, then look_alt).
REALISM_SETS: tuple[str, ...] = ("ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp", "null_identical",
                                 "null_reencode", "nuisance_ev", "m5_vs_m6", "look_alt")
# Realism v2 (docs/milestone7.md §8.2): no m5_vs_m6; look_alt = AgX - Punchy (A) vs look None (B).
REALISM2_SETS: tuple[str, ...] = ("ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp", "null_identical",
                                  "null_reencode", "nuisance_ev", "look_alt")
# The answer enum in the order the question names the images: ab "Image 1 ... Image 2", ba "Image 2 ... Image 1".
REALISM2_ENUMS: dict[str, tuple[str, ...]] = {"ab": ("image_1", "image_2"), "ba": ("image_2", "image_1")}
REALISM_OUTCOMES: tuple[str, ...] = ("W", "L", "T", "NC")
REALISM_DECISIONS: tuple[str, ...] = ("better", "worse", "no_detectable_difference", "not_measurable")
REALISM_EXPECTED: tuple = ("b", "a", "tie", None)

_SHA256: dict = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
_TEXT_OR_NULL: dict = {"type": ["string", "null"]}
_NUMBER_OR_NULL: dict = {"type": ["number", "null"]}


def realism_schema() -> dict:
    """The strict answer schema of one realism pair call (§6.1): a forced choice per aspect, no tie.

    Every aspect is ``{"winner": image_1|image_2, "margin": slight|clear|large,
    "cues": <= 3 of the 12 cues}``, inlined four times (no ``$ref``), with
    ``additionalProperties: false`` everywhere. xgrammar ignores
    ``uniqueItems``, so repeated cues are removed after the call
    (``realism.post_validate``), not by the schema.
    """
    aspect = {"type": "object", "additionalProperties": False, "required": ["winner", "margin", "cues"],
              "properties": {"winner": {"enum": list(REALISM_WINNERS)},
                             "margin": {"enum": list(REALISM_MARGINS)},
                             "cues": {"type": "array", "maxItems": REALISM_MAX_CUES,
                                      "items": {"enum": list(REALISM_CUES)}}}}
    return {"$schema": SCHEMA_ID, "title": "RealismPair", "type": "object", "additionalProperties": False,
            "required": list(REALISM_ASPECTS), "properties": {a: copy.deepcopy(aspect) for a in REALISM_ASPECTS}}


def realism2_schema(order: str) -> dict:
    """The strict answer schema of one realism v2 call (docs/milestone7.md §8.2): one aspect, a forced choice.

    ``{"winner": enum, "confidence": 0..1}``; the enum lists the images in the
    order the question names them (``REALISM2_ENUMS``: ``ab`` ``[image_1,
    image_2]``, ``ba`` ``[image_2, image_1]``). KeyError for another order.
    """
    return {"$schema": SCHEMA_ID, "title": "RealismAspect", "type": "object", "additionalProperties": False,
            "required": ["winner", "confidence"],
            "properties": {"winner": {"enum": list(REALISM2_ENUMS[order])}, "confidence": copy.deepcopy(CONFIDENCE)}}


def _kind(base: str, version: int) -> str:
    """File kind of a realism file: ``realism_<x>`` (v1) or ``realism2_<x>`` (v2)."""
    return base if int(version) == 1 else base.replace("realism_", "realism2_", 1)


def realism_pairs_file_schema(version: int = 1) -> dict:
    """``out/ab/pairs.json`` written by ``realism-pairs`` (§6.3), or (``version=2``) ``out/ab/pairs_v2.json`` of
    ``realism2-pairs``; paths are relative to the project output."""
    sets = REALISM_SETS if int(version) == 1 else REALISM2_SETS
    pair = {"type": "object",
            "required": ["pair_id", "set", "cam", "room_id", "a", "b", "expected", "target_aspect", "a_sha256",
                         "b_sha256", "a_bytes", "b_bytes", "delta_ev"],
            "properties": {"pair_id": {"type": "string", "minLength": 3}, "set": {"enum": list(sets)},
                           "cam": {"type": "string", "minLength": 1}, "room_id": _TEXT_OR_NULL,
                           "a": {"type": "string"}, "b": {"type": "string"},
                           "expected": {"enum": list(REALISM_EXPECTED)},
                           "target_aspect": {"enum": list(REALISM_ASPECTS) + [None]},
                           "a_sha256": _SHA256, "b_sha256": _SHA256,
                           "a_bytes": {"type": "integer", "minimum": 1}, "b_bytes": {"type": "integer", "minimum": 1},
                           "delta_ev": _NUMBER_OR_NULL}}
    listed = {"type": "array", "items": {"type": "object", "required": ["cam", "reason"]}}
    return {"$schema": SCHEMA_ID, "title": "RealismPairs", "type": "object",
            "required": ["schema_version", "kind", "project", "controls", "control_views", "pairs", "sets", "dropped",
                         "skipped", "warnings"],
            "properties": {"schema_version": {"const": "0.1"}, "kind": {"const": _kind("realism_pairs", version)},
                           "project": {"type": "string"}, "controls": {"type": "boolean"},
                           "control_views": {"type": "array", "items": {"type": "string"}},
                           "pairs": {"type": "array", "items": pair},
                           "sets": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
                           "dropped": listed, "skipped": listed,
                           "warnings": {"type": "array", "items": {"type": "string"}}}}


def _outcome_counts() -> dict:
    return {"type": "object", "required": list(REALISM_OUTCOMES),
            "properties": {o: {"type": "integer", "minimum": 0} for o in REALISM_OUTCOMES}}


def realism_ab_schema(version: int = 1) -> dict:
    """``check/realism/realism_ab.json`` of one project (``realism-combine``; ``version=2``: ``realism2_ab.json``
    of ``realism2-combine``): outcomes and statistics, no decision."""
    sets = REALISM_SETS if int(version) == 1 else REALISM2_SETS
    row = {"type": "object",
           "required": ["pair_id", "set", "cam", "room_id", "room", "project", "models", "consensus"],
           "properties": {"set": {"enum": list(sets)},
                          "consensus": {"type": "object", "required": list(REALISM_ASPECTS),
                                        "properties": {a: {"enum": list(REALISM_OUTCOMES)}
                                                       for a in REALISM_ASPECTS}}}}
    return {"$schema": SCHEMA_ID, "title": "RealismAB", "type": "object",
            "required": ["schema_version", "kind", "project", "models", "sets", "rows", "controls", "calls", "dropped",
                         "skipped", "warnings", "contact_sheets"],
            "not": {"required": ["decision"]},
            "properties": {"schema_version": {"const": "0.1"}, "kind": {"const": _kind("realism_ab", version)},
                           "project": {"type": "string"}, "models": {"type": "object"},
                           "sets": {"type": "object"}, "rows": {"type": "array", "items": row},
                           "controls": {"type": ["object", "null"]}, "calls": {"type": "array"},
                           "contact_sheets": {"type": "object",
                                              "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}


def realism_summary_schema(version: int = 1) -> dict:
    """``realism_summary.json`` (``realism-summary``; ``version=2``: ``realism2_summary.json`` of
    ``realism2-summary``): pooled statistics and the decision per set and aspect."""
    aspect = {"type": "object",
              "required": ["decision", "models", "consensus", "n", "decisive", "decisive_rooms", "win_rate",
                           "sign_p", "rooms", "rooms_sign_p", "net_win_ci95"],
              "properties": {"decision": {"enum": list(REALISM_DECISIONS)}, "consensus": _outcome_counts(),
                             "sign_p": {"type": "number", "minimum": 0, "maximum": 1},
                             "net_win_ci95": {"type": "array", "minItems": 2, "maxItems": 2,
                                              "items": _NUMBER_OR_NULL}}}
    one_set = {"type": "object", "required": ["decision", "single_model", "consensus_models", "pairs", "aspects"],
               "properties": {"decision": {"enum": list(REALISM_DECISIONS)}, "single_model": {"type": "boolean"},
                              "consensus_models": {"type": "array", "items": {"type": "string"}},
                              "pairs": {"type": "integer", "minimum": 0},
                              "aspects": {"type": "object", "required": list(REALISM_ASPECTS),
                                          "properties": {a: aspect for a in REALISM_ASPECTS}}}}
    return {"$schema": SCHEMA_ID, "title": "RealismSummary", "type": "object",
            "required": ["schema_version", "kind", "projects", "controls_project", "models", "controls", "signal",
                         "measurable", "single_model", "consensus_models", "sets", "position_bias", "ev_flags",
                         "top_cues", "calls", "notes", "warnings"],
            "properties": {"schema_version": {"const": "0.1"}, "kind": {"const": _kind("realism_summary", version)},
                           "projects": {"type": "array", "items": {"type": "object", "required": ["project", "found"]}},
                           "controls_project": _TEXT_OR_NULL, "models": {"type": "object"},
                           "controls": {"type": ["object", "null"]},
                           "signal": {"type": "object", "additionalProperties": {"type": "boolean"}},
                           "measurable": {"type": "boolean"}, "single_model": {"type": "boolean"},
                           "consensus_models": {"type": "array", "items": {"type": "string"}},
                           "sets": {"type": "object", "additionalProperties": one_set},
                           "ev_flags": {"type": "object", "required": ["active", "threshold", "pairs"]},
                           "calls": {"type": "array"},
                           "notes": {"type": "array", "items": {"type": "string"}},
                           "warnings": {"type": "array", "items": {"type": "string"}}}}
