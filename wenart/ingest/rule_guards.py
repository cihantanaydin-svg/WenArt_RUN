"""Guards on the completion rules (12 Nov 2026; the coordinator: the building-sense audit rules are being verified
against every real and synthetic project by misfire hunters, and their amended guards are added here, without a
rewrite of the rules).

What: every change a completion rule makes (``wenart.ingest.completion``, ``core_rules``, ``sense_rules``) passes
``blocked(rule, building, item)`` first. ``RULES`` names each rule key with the audit rules it carries and what it
changes. A change is stopped, and logged in ``building["level_inference"]["guarded"]`` with the rule, its audit ids,
the item and the reason, when

- the rule is switched off: ``OFF`` (code), the environment variable ``WENART_RULES_OFF`` (a comma list of rule keys
  or audit ids, e.g. ``R19,core_gap``: a misfire hunt reads a project with a rule off), or the building's
  ``level_inference.rules_off`` (a list, same form);
- a guard in ``GUARDS[rule]`` returns a reason: ``def guard(building, item) -> Optional[str]``, registered with
  ``@guard("lift_door_add")`` or appended to ``GUARDS[key]``.

An item is a plain dict: ``level_id`` and the ids the change touches (``opening``, ``wall``, ``room``, ``lift``,
``stair``, ``space``, ``symbol``), plus the rule's own reason (``why``) where it has one. Every change a rule makes
also stays marked ``inferred`` or ``adjusted_by_ai`` (by code) with its reason, and the RC14 checks stay advisory.

Why: the audit's rules were written from 8 buildings; until the hunters have tested them on every project, each
rule's detection must be stoppable change by change with its reason on record, and a guard must drop in as one
function. No project data, no thresholds here.

How: pure Python; the log is deduplicated (a rule asked twice about the same item logs once).
"""
from __future__ import annotations

import json
import os
from typing import Callable, Optional

# rule key -> (audit rule ids, what the rule changes)
RULES = {
    "stair_box": (("R08",), "a stroke box the reading set aside as notation becomes the missed stair"),
    "stair_typical_copy": (("R08",), "a copy of a typical floor takes its floor's stair"),
    "stair_dogleg": (("R08",), "a dog-leg stair is inferred in the core hall of a building of several flats"),
    "lift_door_remove": (("R19", "R16"), "a lift's opening into a flat's room, onto a stair flight, a sliver or a "
                                         "window in the shaft is removed"),
    "lift_door_add": (("R19",), "a lift with no opening onto the common hall gets an inferred landing door"),
    "core_gap": (("R16",), "an unclassified gap between a flat's room and the common core is closed"),
    "entrance_refuse": (("R09",), "an entrance with a lost room label behind it, or from a wet room, is refused"),
    "entrance_add": (("R09", "R43"), "a building of several flats gets an inferred entrance into its core hall"),
    "exterior_flag": (("R14",), "a wall's exterior flag is set from the building outline"),
    "stair_over_nothing": (("R18", "R25"), "a stair with no storey over it is not built upward (audit real10-5)"),
    "shaft": (("R20",), "a small face named by a shaft word is a shaft with its slab voids"),
    "balcony_door": (("R27",), "a balcony with no door gets its window as a door, or an inferred door"),
    "light_well": (("R52",), "a face named by a light-well word is an open-air void through the storeys (UL334)"),
    "party_wall": (("R46", "R45"), "a wall on the side a party text names is a blank party wall"),
    "party_balcony": (("R46",), "a balcony on an attached side is cut at the party line or left out"),
    "below_ground": (("R24",), "a level below ground takes no inferred window or balcony door (UL333)"),
    "window_inferred": (("R14", "R24", "R46"), "a habitable or wet room facing the outside on a plan that draws no "
                                                "window gets an inferred window (UL331)"),
    "balcony_door_inferred": (("R27",), "a habitable room onto a balcony on a plan that draws no window gets an "
                                        "inferred balcony door (UL331)"),
}

GUARDS: dict = {key: [] for key in RULES}
OFF: set = set()


def guard(rule: str) -> Callable:
    """Register ``fn(building, item) -> Optional[str]`` as a guard of ``rule``."""
    if rule not in RULES:
        raise KeyError(f"unknown completion rule {rule!r}")

    def deco(fn: Callable) -> Callable:
        GUARDS.setdefault(rule, []).append(fn)
        return fn
    return deco


def _names(raw) -> set:
    if isinstance(raw, str):
        raw = raw.split(",")
    return {str(x).strip() for x in raw or [] if str(x).strip()}


def switched_off(rule: str, building: Optional[dict] = None) -> Optional[str]:
    """Why ``rule`` is off (by its key or one of its audit ids), or None."""
    ids = {rule, *RULES.get(rule, ((), ""))[0]}
    li = (building or {}).get("level_inference") if isinstance(building, dict) else None
    for where, names in (("code", OFF), ("WENART_RULES_OFF", _names(os.environ.get("WENART_RULES_OFF"))),
                         ("level_inference.rules_off", _names((li or {}).get("rules_off")
                                                              if isinstance(li, dict) else None))):
        hit = ids & set(names)
        if hit:
            return f"the rule is switched off ({where}: {', '.join(sorted(hit))})"
    return None


def blocked(rule: str, building: Optional[dict], item: dict) -> Optional[str]:
    """Why this one change of ``rule`` may not be made (logged in ``level_inference.guarded``), or None."""
    why = switched_off(rule, building)
    if why is None:
        for fn in GUARDS.get(rule) or []:
            why = fn(building, item)
            if why:
                why = str(why)
                break
    if why and isinstance(building, dict):
        li = building.get("level_inference")
        if not isinstance(li, dict):
            li = building["level_inference"] = {}
        log = li.setdefault("guarded", [])
        entry = {"rule": rule, "audit": list(RULES.get(rule, ((), ""))[0]),
                 "item": {k: v for k, v in item.items() if isinstance(v, (str, int, float, bool, list)) or v is None},
                 "reason": why}
        key = json.dumps([entry["rule"], entry["item"]], sort_keys=True, default=str)
        if key not in {json.dumps([e.get("rule"), e.get("item")], sort_keys=True, default=str) for e in log}:
            log.append(entry)
    return why
