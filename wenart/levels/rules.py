"""The level rules the build and the levels share (pure; 28 Oct 2026).

``BUILTIN_PARAMS`` (a copy of the ``levels:`` block of wenart/defaults.yaml and the brief's ``levels:`` defaults),
``level_params`` (the rules with a brief's ``levels:`` block over them), ``steps_for`` (an outdoor or inner flight for
a rise) and ``ramp_for`` (a ramp by the slope table). ``wenart.levels.model`` re-exports them.

Why here: the site grading (``wenart.blender.grading``, user feedback on real04 run 20261028-005318-full: "Better
solutions needed for the elevation difference outside") builds garden flights and ramps by these rules inside
Blender; ``wenart.levels.model`` also reads the sheets, so the build would carry the whole sheet pipeline in its
import closure (the build fingerprint, tests/test_blender_look.py) if it imported the rules from there.
"""
from __future__ import annotations

import copy
import math
from typing import Optional


def _r(v: float, nd: int = 3) -> float:
    return round(float(v), nd) + 0.0


# A copy of the ``levels:`` block of wenart/defaults.yaml and of the brief's ``levels:`` defaults (tests pin it): the
# code runs where PyYAML is missing.
BUILTIN_PARAMS = {
    "ground_rise": 0.15, "accessible_entrance": False,
    "flush_max": 0.05, "riser_max_outdoor": 0.15, "riser_min_outdoor": 0.10, "riser_max_indoor": 0.18, "tread": 0.30,
    "tread_min": 0.28, "step_rule": [0.58, 0.66], "landing_depth": 1.20, "landing_extra_width": 0.60,
    "landing_every_risers": 12, "handrail_from": 0.45, "cheek_wall_from": 0.45,
    "ramp_slopes": [[0.15, 0.0833], [0.50, 0.0714], [1.00, 0.0625], [99.0, 0.05]], "ramp_handrail_from": 0.15,
    "ramp_width": 1.20, "door_into_air": 1.50, "door_ground_reach": 5.0, "door_mark_reach": 1.5, "ground_reach": 25.0,
    "ground_outlier": 3.0, "room_offset_max": 1.0, "plane_residual": 0.10, "terrain_blend": 20.0, "plinth_min": 0.15,
    "mark_tol": 0.02, "parapet": 0.30,
}


def _default_params() -> dict:
    out = copy.deepcopy(BUILTIN_PARAMS)
    try:
        import yaml
        from wenart.brief import DEFAULTS_PATH

        data = yaml.safe_load(DEFAULTS_PATH.read_text(encoding="utf-8")) or {}
        out.update(copy.deepcopy(data.get("levels") or {}))
        out.update(copy.deepcopy((data.get("brief") or {}).get("levels") or {}))
    except (ImportError, OSError):              # Blender's Python: the built-in copy
        pass
    return out


def _brief_values(brief: Optional[dict]) -> dict:
    from wenart.brief import levels_block

    return levels_block(brief)


def level_params(brief: Optional[dict] = None) -> dict:
    """The level rules (``wenart/defaults.yaml`` ``levels:`` and the brief's ``levels:`` defaults) with the brief's
    ``levels:`` block over them (a ``load_brief`` result or a raw brief). A brief value of the wrong type is not
    used (``_warnings``); ``_from_brief`` lists the keys the brief set."""
    params = _default_params()
    params["_from_brief"], params["_warnings"] = [], []
    for key, given in sorted(_brief_values(brief).items()):
        if key not in params or key.startswith("_"):
            params["_warnings"].append(f"brief levels.{key}: unknown key, not used")
            continue
        want = params[key]
        ok = (isinstance(want, bool) and isinstance(given, bool)) or \
            (isinstance(want, (int, float)) and not isinstance(want, bool) and isinstance(given, (int, float))
             and not isinstance(given, bool) and given >= 0) or \
            (isinstance(want, list) and isinstance(given, list) and len(given) == len(want) or
             (key == "ramp_slopes" and isinstance(given, list) and given))
        if not ok:
            params["_warnings"].append(f"brief levels.{key}: {given!r} is not a {type(want).__name__}; "
                                       f"{want!r} used")
            continue
        params[key] = copy.deepcopy(given)
        params["_from_brief"].append(key)
    return params


def steps_for(rise: float, width: float, params: dict, outdoor: bool = True) -> Optional[dict]:
    """The flight for ``rise`` (m): ``n = ceil(rise / riser_max)`` risers of ``rise / n``, ``tread`` deep, in flights
    of at most ``landing_every_risers`` (intermediate landings between them); handrails and cheek walls above their
    thresholds. None for a flush rise."""
    if rise <= float(params["flush_max"]):
        return None
    rmax = float(params["riser_max_outdoor" if outdoor else "riser_max_indoor"])
    n = max(1, int(math.ceil(rise / rmax - 1e-9)))
    riser = rise / n
    # tread: the rule's at least, deeper when low risers need it to keep 2 R + T within the step rule
    tread = max(float(params["tread"]), math.ceil((float(params["step_rule"][0]) - 2 * riser) * 100 - 1e-6) / 100.0)
    per = max(1, int(params["landing_every_risers"]))
    flights, left = [], n
    while left > 0:
        k = min(per, left)
        flights.append(k)
        left -= k
    return {"count": n, "riser": _r(riser, 4), "tread": _r(tread), "rule_2r_t": _r(2 * riser + tread, 4),
            "flights": flights, "intermediate_landings": len(flights) - 1,
            "width": _r(width), "handrails": rise > float(params["handrail_from"]),
            "cheek_walls": rise > float(params["cheek_wall_from"]),
            "run": _r((n - len(flights)) * tread + (len(flights) - 1) * float(params["landing_depth"]))}


def ramp_for(rise: float, params: dict) -> Optional[dict]:
    """The ramp for ``rise`` by the slope table (``ramp_slopes``: rise up to -> slope), None for a flush rise."""
    if rise <= float(params["flush_max"]):
        return None
    slope = None
    for limit, s in params["ramp_slopes"]:
        if rise <= float(limit) + 1e-9:
            slope = float(s)
            break
    slope = slope if slope is not None else float(params["ramp_slopes"][-1][1])
    return {"slope": _r(slope, 4), "ratio": f"1:{round(1.0 / slope):d}", "length": _r(rise / slope),
            "width": _r(params["ramp_width"]), "handrails": rise > float(params["ramp_handrail_from"]),
            "along": "facade"}
