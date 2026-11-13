"""The section's ground against the doors at grade (13 Nov 2026; review S1F-POD-P03, amended rules R04 and R03 of the
building-sense audit: "ground is the line running beyond both outer walls, drawn doors at grade are evidence, a ground
burying storeys with doors at grade is refused with a question").

What: ``apply(build)`` checks the ground the section gave (``site.ground.levels`` with the lines it read,
``z.lines``: ``wenart.sheets.heights``) against the drawn outer doors. When the lowest ground lies more than
``DOOR_UNDER_M`` over the head of a drawn door to the outside on a storey that is no basement, that ground is refused
(rule key ``ground_doors``). It is replaced by the drawn line beside the doors at grade: from the lowest storey with a
drawn door to the outside upward, the first storey with a line read by the section between ``LINE_BELOW_M`` under
and ``LINE_ABOVE_M`` over its floor (a line read on both sides, running beyond both outer walls, first; the highest
of them). With no such line, the ground is assumed one step (``STEP_M``) under the lowest non-basement storey with a
door to the outside and a question is asked (``needs_review`` ``ground_doors``). Either way the conflict is listed,
the refused value and the doors stay on record in ``level_inference.ground_doors``, and the level entry carries
``adjusted_by_ai`` (by code) with its reason.

Why: real09's section r6 draws 16 horizontal lines beside its walls; the upper one, a 1.42 m stroke at the top of the
dormer boxes beside the roof, was read as the ground (+11.11 m): four storeys with flush outer doors and windows were
buried, 11 m deep front courts inferred and an entrance said to lie 11.11 m under the ground. The line at the first
basement's floor beyond both outer walls, where the basement's doors open at grade, is the ground.

How: pure Python on the building JSON (the walls' exterior flags, the levels, the openings); called first in
``wenart.ingest.completion.complete``, before any rule reads the ground.
"""
from __future__ import annotations

from typing import Optional

DOOR_UNDER_M = 0.50      # a drawn door whose head lies this far under the ground opens into the earth
LINE_BELOW_M = 1.00      # a ground line at most this far under the floor of the storey whose doors stand at grade ...
LINE_ABOVE_M = 0.50      # ... and at most this far over it (R04: "about 0.5 m above the lowest storey with a door")
PAIR_M = 0.05            # lines of the two sides this close in height are one ground beyond both outer walls
STEP_M = 0.15            # an assumed ground lies one step under the door storey's floor
DOOR_H_M = 2.10


def _storeys(b: dict) -> list:
    return sorted((lv for lv in b.get("levels") or [] if isinstance(lv.get("elevation"), (int, float))
                   and not lv.get("base_level_id")), key=lambda lv: float(lv["elevation"]))


def _basement(lv: dict) -> bool:
    return lv.get("kind") == "basement" or (lv.get("order") or 0) < 0


def outside_doors(b: dict, lid: str) -> list:
    """The drawn doors of level ``lid`` in an outer wall with the outside beyond them (pure): no inferred or derived
    opening, no door onto a balcony, a light well or a room."""
    from wenart.ingest import completion as CP
    from wenart.ingest import core_rules as CR

    walls = {w["id"]: w for w in b.get("walls") or []}
    level = None
    out = []
    for o in b.get("openings") or []:
        if o.get("level_id") != lid or o.get("type") != "door" or CR.derived(o) or not o.get("center"):
            continue
        w = walls.get(o.get("wall_id"))
        if w is None or w.get("exterior") is not True or w.get("party"):
            continue
        level = level or CP.Level(b, lid)
        _a, u, length = CP._axis(w)
        if length <= 0:
            continue
        reach = float(w.get("thickness") or 0.15) / 2.0 + 0.25
        qs = [(o["center"][0] - u[1] * k * reach, o["center"][1] + u[0] * k * reach) for k in (1, -1)]
        kinds = [level.kind_at(q, "") for q in qs]
        if "outside" in kinds and not {"balcony", "light_well"} & set(kinds):
            out.append(o)
    return out


def _lines(level_entry: dict) -> list:
    return [ln for ln in ((level_entry.get("z") or {}).get("lines") or [])
            if isinstance(ln, dict) and isinstance(ln.get("z"), (int, float))]


def choose(lines: list, floor: float) -> Optional[dict]:
    """The line read beside a storey whose floor is ``floor`` and whose doors stand at grade (pure): between
    ``LINE_BELOW_M`` under and ``LINE_ABOVE_M`` over the floor; a height read on both sides first, then the highest.
    ``{"z", "entities", "both_sides"}`` or None."""
    near = [ln for ln in lines if floor - LINE_BELOW_M - 1e-6 <= float(ln["z"]) <= floor + LINE_ABOVE_M + 1e-6]
    if not near:
        return None
    rows = []
    for ln in near:
        same = [x for x in near if abs(float(x["z"]) - float(ln["z"])) <= PAIR_M]
        both = len({x.get("side") for x in same}) >= 2
        rows.append((both, float(ln["z"]), same))
    both, z, same = max(rows, key=lambda r: (r[0], r[1]))
    return {"z": round(z, 3), "entities": sorted({str(x.get("entity")) for x in same}), "both_sides": both}


def apply(build) -> Optional[dict]:
    """The rule (the module docstring); returns its record or None."""
    from wenart.ingest import rule_guards as RG

    b = build.building
    if not RG.active("ground_doors", b):
        return None
    g = (b.get("site") or {}).get("ground") or {}
    levels = [x for x in g.get("levels") or [] if isinstance(x, dict) and _lines(x)
              and isinstance((x.get("z") or {}).get("value"), (int, float))]
    if not levels or (g.get("surface") or {}).get("source") == "marks":
        return None
    gz = min(float(x["z"]["value"]) for x in levels)
    storeys = _storeys(b)
    doors = {lv["id"]: outside_doors(b, lv["id"]) for lv in storeys}
    buried = []
    for lv in storeys:
        if _basement(lv):
            continue
        for o in doors[lv["id"]]:
            head = float(lv["elevation"]) + float(o.get("sill_height") or 0.0) + float(o.get("height") or DOOR_H_M)
            if head < gz - DOOR_UNDER_M:
                buried.append((lv, o))
    if not buried:
        return None
    lids = sorted({lv["id"] for lv, _o in buried})
    if RG.blocked("ground_doors", b, {"level_id": lids[0], "why": f"ground {gz:+.2f} m buries the doors of "
                                                                     f"{', '.join(lids)}"}):
        return None
    lines = [ln for x in levels for ln in _lines(x)]
    chosen, at = None, None
    # the storeys whose doors may stand at grade: up to the lowest storey with a door to the outside that is no
    # basement (a ground over it would bury that door again)
    top = next((float(lv["elevation"]) for lv in storeys if doors[lv["id"]] and not _basement(lv)), None)
    for lv in storeys:
        if not doors[lv["id"]] or (top is not None and float(lv["elevation"]) > top + 1e-6):
            continue
        chosen = choose(lines, float(lv["elevation"]))
        if chosen is not None:
            at = lv
            break
    old = [dict(x["z"], side=x.get("side")) for x in levels]
    for z in old:
        z.pop("lines", None)
    why = (f"the section's ground ({gz:+.2f} m) lies more than {DOOR_UNDER_M:.2f} m over the head of "
           f"{len(buried)} drawn door(s) to the outside on {', '.join(lids)} (e.g. {buried[0][1]['id']}): a ground that "
           f"buries storeys with doors at grade is refused (R04)")
    ev0 = dict(((levels[0]["z"].get("evidence") or [{}])[0]) or {})
    if chosen is not None:
        z = chosen["z"]
        how = (f"the line{'s' if len(chosen['entities']) > 1 else ''} {', '.join(chosen['entities'])} at {z:+.2f} m "
               f"{'beyond both outer walls ' if chosen['both_sides'] else ''}beside the doors at grade of {at['id']} "
               f"(floor {float(at['elevation']):+.2f} m) is the ground")
        value = {"value": z, "method": "vector", "confidence": 0.7,
                 "evidence": [dict(ev0, entity=e, rule="ground_line") for e in chosen["entities"]][:4],
                 "note": f"{why}; {how}"}
    else:
        floor = next((float(lv["elevation"]) for lv in storeys if doors[lv["id"]] and not _basement(lv)),
                     float(buried[0][0]["elevation"]))
        z = round(floor - STEP_M, 3)
        how = (f"no line the section read lies beside a storey's doors at grade: the ground is assumed one step "
               f"({STEP_M:.2f} m) under the lowest storey with a door to the outside ({z:+.2f} m); asked")
        value = {"value": z, "method": "assumed", "confidence": 0.0, "evidence": [], "note": f"{why}; {how}"}
    entry = {"side": "all", "azimuth_deg": None, "z": value,
             "adjusted_by_ai": {"by": "code", "rule": "ground_doors", "reason": f"{why}; {how}"}}
    g["levels"] = [x for x in g.get("levels") or [] if x not in levels] + [entry]
    surface = g.get("surface")
    if isinstance(surface, dict):
        surface.update(flat_z=z, kind="flat" if len(g["levels"]) == 1 else surface.get("kind"),
                       reason=f"{surface.get('reason') or ''}; ground_doors: {how}".lstrip("; "))
    rec = {"refused": old, "z": z, "chosen": chosen, "at": at["id"] if at else None,
           "doors": [o["id"] for _lv, o in buried][:20], "storeys": lids, "reason": f"{why}; {how}"}
    li = b.setdefault("level_inference", {})
    li["ground_doors"] = rec
    if callable(getattr(build, "conflict", None)):
        build.conflict("other", lids, why, how)
    warn = getattr(build, "warn", None)
    if callable(warn):
        warn(f"ground_doors: {why}; {how}")
    if chosen is None:
        b.setdefault("needs_review", []).append({"id": "ground:doors", "kind": "ground_doors", "reason": f"{why}; {how}",
                                                 "crop": None, "room_id": None, "level_id": lids[0]})
    return rec
