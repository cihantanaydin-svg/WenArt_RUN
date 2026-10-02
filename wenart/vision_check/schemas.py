"""Answer schemas of the final vision check (docs/milestone5.md §5.3, §5.6; docs/milestone6.md §6).

What: the categories a model may answer, their class (door, window,
furniture, fixture, decor), the strict per-view JSON schema of the element
check, the preference schema, and the post-validation that turns an
inconsistent element answer into ``unsure``. Milestone 6 adds the realism
A/B answer schema (``realism_schema``: one forced choice per aspect, no tie)
and the schemas of the realism files (``realism_pairs_file_schema``,
``realism_ab_schema``, ``realism_summary_schema``), see
``wenart/vision_check/realism.py``.

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


def realism_pairs_file_schema() -> dict:
    """``out/ab/pairs.json`` written by ``realism-pairs`` (§6.3); paths are relative to the project output."""
    pair = {"type": "object",
            "required": ["pair_id", "set", "cam", "room_id", "a", "b", "expected", "target_aspect", "a_sha256",
                         "b_sha256", "a_bytes", "b_bytes", "delta_ev"],
            "properties": {"pair_id": {"type": "string", "minLength": 3}, "set": {"enum": list(REALISM_SETS)},
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
            "properties": {"schema_version": {"const": "0.1"}, "kind": {"const": "realism_pairs"},
                           "project": {"type": "string"}, "controls": {"type": "boolean"},
                           "control_views": {"type": "array", "items": {"type": "string"}},
                           "pairs": {"type": "array", "items": pair},
                           "sets": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
                           "dropped": listed, "skipped": listed,
                           "warnings": {"type": "array", "items": {"type": "string"}}}}


def _outcome_counts() -> dict:
    return {"type": "object", "required": list(REALISM_OUTCOMES),
            "properties": {o: {"type": "integer", "minimum": 0} for o in REALISM_OUTCOMES}}


def realism_ab_schema() -> dict:
    """``check/realism/realism_ab.json`` of one project (``realism-combine``): outcomes and statistics, no decision."""
    row = {"type": "object",
           "required": ["pair_id", "set", "cam", "room_id", "room", "project", "models", "consensus"],
           "properties": {"set": {"enum": list(REALISM_SETS)},
                          "consensus": {"type": "object", "required": list(REALISM_ASPECTS),
                                        "properties": {a: {"enum": list(REALISM_OUTCOMES)}
                                                       for a in REALISM_ASPECTS}}}}
    return {"$schema": SCHEMA_ID, "title": "RealismAB", "type": "object",
            "required": ["schema_version", "kind", "project", "models", "sets", "rows", "controls", "calls", "dropped",
                         "skipped", "warnings", "contact_sheets"],
            "not": {"required": ["decision"]},
            "properties": {"schema_version": {"const": "0.1"}, "kind": {"const": "realism_ab"},
                           "project": {"type": "string"}, "models": {"type": "object"},
                           "sets": {"type": "object"}, "rows": {"type": "array", "items": row},
                           "controls": {"type": ["object", "null"]}, "calls": {"type": "array"},
                           "contact_sheets": {"type": "object",
                                              "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}


def realism_summary_schema() -> dict:
    """``realism_summary.json`` (``realism-summary``): pooled statistics and the decision per set and aspect."""
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
            "properties": {"schema_version": {"const": "0.1"}, "kind": {"const": "realism_summary"},
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
