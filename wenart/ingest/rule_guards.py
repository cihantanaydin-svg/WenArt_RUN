"""Guards on the completion rules (12 Nov 2026; the coordinator: the building-sense audit rules are being verified
against every real and synthetic project by misfire hunters, and their amended guards are added here, without a
rewrite of the rules).

What: every change a completion rule makes (``wenart.ingest.completion``, ``core_rules``, ``sense_rules``) passes
``blocked(rule, building, item)`` first. ``RULES`` names each rule key with the audit rules it carries and what it
changes. A change is stopped, and logged in ``building["level_inference"]["guarded"]`` with the rule, its audit ids,
the item and the reason, when

- the rule is switched off: ``OFF`` (code), the environment variable ``WENART_RULES_OFF`` (a comma list of rule keys
  or audit ids, e.g. ``R19,core_gap``: a misfire hunt reads a project with a rule off), the brief's ``rules_off``
  (``building.project.brief``) or the building's ``level_inference.rules_off`` (a list, same form);
- the rule is a staged one (``STAGED``: written, not reviewed yet) and nothing switches it on: ``ON`` (code), the
  environment variable ``WENART_RULES_ON``, the brief's ``rules_on`` or ``level_inference.rules_on``. Code that
  branches on a staged rule asks ``active(rule, building)``;
- a guard in ``GUARDS[rule]`` returns a reason: ``def guard(building, item) -> Optional[str]``, registered with
  ``@guard("core_gap")`` or appended to ``GUARDS[key]``.

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
    "stair_box": (("R08",), "a stroke box the reading set aside as notation, with stair strokes inside, becomes the "
                            "missed stair"),
    "stair_typical_copy": (("R08",), "a copy of a typical floor takes its floor's stair"),
    "stair_signs": (("R08",), "a stair-size box beside the core with a well line or a break diagonal drawn in it is an "
                              "inferred stair (the coordinator's decision of 12 Nov 2026)"),
    # 19 Nov 2026 (merge of reader A: the landing door is the reader's one rule, twins.lift_doors): lift_door_unmark,
    # lift_door_merge, lift_door_remove, lift_door_retype and lift_door_add are gone with the completion's own steps
    "core_gap": (("R16",), "an unclassified gap between a flat's room and the common core is closed"),
    "entrance_refuse": (("R09",), "an entrance with a lost room label behind it, or from a wet room, is refused"),
    "entrance_add": (("R09", "R43"), "a building of several flats gets an inferred entrance into its core hall"),
    "entrance_tags": (("R37", "R09"), "an outer door tagged as a window is a window; an outer gap tagged as a door "
                                      "into a hall is the entrance door"),
    "exterior_flag": (("R14",), "a wall's exterior flag is set from the building outline"),
    "stair_over_nothing": (("R18", "R25"), "a stair with no storey over it is not built upward (audit real10-5)"),
    "shaft": (("R20",), "a small face named by a shaft word is a shaft with its slab voids"),
    "balcony_door": (("R27",), "a balcony with no door gets its window as a door, or an inferred door"),
    # 22 Nov 2026 (S3, the user's pick "build S5, S3, S4, S6")
    "door_onto_nothing": (("R37",), "an upper-storey door onto nothing, with no swing or door block drawn, on a window "
                                     "layer or with a window's tag is a window (else a question)"),
    # 23 Nov 2026 (UL371, the user's C0097 on real15)
    "narrow_door": (("R37",), "an upper-storey door onto nothing narrower than any door (0.60 m), with no swing, door "
                              "block or door-high tag, is no door: the wall runs on"),
    "fire_stair_closed": (("R16",), "a fire stair's enclosure has no doorless opening: an empty gap in it is wall"),
    "light_well": (("R52",), "a face named by a light-well word is an open-air void through the storeys (UL334)"),
    "party_wall": (("R46", "R45"), "a wall on the side a party text names is a blank party wall"),
    "party_balcony": (("R46",), "a balcony on an attached side is cut at the party line or left out"),
    "below_ground": (("R24",), "a level, or a facade buried by soil labels or terrain, takes no inferred window or "
                              "balcony door (UL333)"),
    "window_inferred": (("R14", "R24", "R46"), "a habitable or wet room facing the outside on a plan that draws no "
                                                "window gets an inferred window (UL331)"),
    "balcony_door_inferred": (("R27",), "a habitable room onto a balcony on a plan that draws no window gets an "
                                        "inferred balcony door (UL331)"),
    "cantilever_drop": (("R10",), "a ground floor read from a typical floor leaves out the typical floor's balconies"),
    "storey_roof": (("R18",), "storeys added by the storey count get a flat roof over the new top storey"),
    "ground_cut": (("R10",), "a ground floor read from the typical plan is cut to the drawn footprint"),
    "entrance_hall": (("R43",), "an inferred ground floor whose core reaches no street gets an entrance hall from the "
                                "street facade into the core"),
    "copy_door_window": (("R10",), "a door of a copied storey from a room to the true outside becomes a window of its "
                                   "width; one with the outside on both sides is removed (its wall a facade remnant)"),
    "ground_doors": (("R04", "R03"), "a section ground that buries a storey with drawn outer doors is refused; the drawn "
                                     "line beside the doors at grade, or an assumed ground with a question, replaces it"),
    "core_flat_door": (("R09",), "a door from the common core into a flat's habitable room that has its own door from "
                                 "the flat's hall is refused (removed into openings_merged, the wall kept)"),
    "basement_footprint": (("R10",), "a basement a document lists and no plan draws is built as the ground floor's "
                                        "footprint with its core (stairs, lifts), no window, no outside door"),
    # 20 Nov 2026 (real20's 16-degree street facade read as axis stubs; the user: "focus on real structural problems")
    "angled_wall": (("R35",), "a wall drawn at an angle off the plan's axes stays at its angle: its face pair is one "
                              "wall at that angle, and the gaps of its line are read in its own frame"),
    # 20 Nov 2026 (real20's kitchen-to-balcony door: its gap closed by the wall's cut lines, a door block with no arc)
    "cut_span_door": (("R53",), "a door size tag or door block at a wall span framed by two jamb lines across the wall "
                                "with door strokes inside is that door: the lines along it are the section edge"),
    # staged rules (``STAGED``): written and tested, off until their review (the coordinator, 13 Nov 2026)
    "exterior_spans": (("R14",), "the exterior flag is read per stretch of a wall before the windows; a level or a "
                                 "stretch that does not qualify takes no inferred window"),
    "facade_ground": (("R24", "R45"), "each facade is read buried or exposed (soil labels, exposure, terrain) with its "
                                      "margin notes; a buried facade takes no inferred window"),
    "party_plot": (("R46",), "a wall on a plot line a party text names is a blank party wall"),
    "party_internal": (("R46",), "a wall between two blocks of one building is an internal party wall"),
    "party_refuse": (("R46",), "a derived or inferred opening on a party wall is refused"),
    "party_eaves": (("R46",), "a roof has no eaves over a party side"),
    "margin_join": (("R45", "R46"), "the stacked lines of a margin note are read as one text before its words count"),
    "party_guards": (("R46",), "a side the reading did not fully build is no party wall; a derived or inferred opening "
                               "whose span crosses a party line is refused"),
}

# the staged rules: off unless switched on (stage 2, not reviewed yet; the coordinator, 13 Nov 2026)
STAGED = {"exterior_spans", "facade_ground", "party_plot", "party_internal", "party_refuse", "party_eaves",
          "margin_join", "party_guards"}

GUARDS: dict = {key: [] for key in RULES}
OFF: set = set()
ON: set = set()


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


def _sources(building: Optional[dict], which: str) -> list:
    """``[(where, names)]``: the places that switch rules off (``which`` = "off") or on ("on")."""
    li = building.get("level_inference") if isinstance(building, dict) else None
    project = building.get("project") if isinstance(building, dict) else None
    brief = project.get("brief") if isinstance(project, dict) else None
    key = f"rules_{which}"
    return [("code", OFF if which == "off" else ON),
            (f"WENART_RULES_{which.upper()}", _names(os.environ.get(f"WENART_RULES_{which.upper()}"))),
            (f"brief {key}", _names(brief.get(key) if isinstance(brief, dict) else None)),
            (f"level_inference.{key}", _names(li.get(key) if isinstance(li, dict) else None))]


def switched_off(rule: str, building: Optional[dict] = None) -> Optional[str]:
    """Why ``rule`` is off (by its key or one of its audit ids), or None; a staged rule (``STAGED``) is off unless
    something switches it on by its key."""
    ids = {rule, *RULES.get(rule, ((), ""))[0]}
    for where, names in _sources(building, "off"):
        hit = ids & set(names)
        if hit:
            return f"the rule is switched off ({where}: {', '.join(sorted(hit))})"
    if rule in STAGED and not any(rule in names for _, names in _sources(building, "on")):
        return "a staged rule, not reviewed yet: off unless switched on (rules_on)"
    return None


def active(rule: str, building: Optional[dict] = None) -> bool:
    """Whether ``rule`` runs at all (not switched off; a staged rule switched on): for code that branches on a rule
    rather than stopping one change (nothing logged)."""
    return switched_off(rule, building) is None


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
