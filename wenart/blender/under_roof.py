"""Nothing built inside the house crosses the roof or the ceiling over it (30 Oct 2026; lessons UL128, UL132).

The user on real04 run 20261029-201533-full: "Some frames coming out of the roof it needs fixing" (an exterior view:
door frames, open door leaves, towels and panels of the top floor through the sloped roof) and "Door frame needs
fixing" (the play room's door d_L1_001: its jamb running up into the sloped ceiling, no head in sight). Every rule here
is general (CLAUDE.md); real04 is the test case.

What (pure, no ``bpy``):

- ``crossings(objects, building, roof_model)``: every scene manifest entry built inside a level under a sloped ceiling
  (``level["ceiling_planes"]``: furniture, proxies, decor, every door part: the opening's model, its leaf, the jamb
  lining, the head and the architrave) whose built box (``box3d``) stands over the lowest ceiling over its box's plan
  corners. Over the roof's top surface there: ``critical`` (it shows from outside); over the ceiling only: ``major``
  (it runs into the ceiling inside). A light hung from the ceiling (``HUNG_TYPES``: its canopy meets the slope at its
  cord, M14 / S5 measure it) and a box out of the roof's outline (a terrace) are not measured. One finding per
  element: a door's worst part names it.
- ``door_problems(building)``: a door the build could not fit under the slope at its wall nor slide along it
  (``door_states.apply_under_roof``: ``under_roof.fits`` False): ``major``, it needs a dormer or a raised roof.
- ``dormer_problems(building, manifest)`` (31 Oct 2026, ``dormers.py``: the build raises a dormer over such a door
  where one fits): a dormer the scene lacks (``dormer_not_built``) or one that leaves its door too low
  (``dormer_too_low``): ``major``. The crossings read the level's ceiling raised by its dormers (``ceiling_dormers``).

The model review's M31 and the build's log read both; the exterior check X2 sees the door parts too since their
manifest entries carry ``box3d`` (``build.add_box3d``). The rules that keep things under the roof: the doors
(``door_states.head_room``, ``apply_under_roof``, an open leaf tried under the ceiling over it), the furniture
(``furniture.under_roof_cap``: a model taller than the slope over its footprint gives way to the module or parametric
piece at the height the slope leaves), the decor (``build.decor_under_roof``: every hostless item, ``furniture``'s
wall art under the slope, ``rest.plan_decor``'s ``max_top_z`` for hosted items, ``bath_details`` placing the
bathroom's wall details under the slope).
"""
from __future__ import annotations

from typing import Optional, Sequence

from wenart import geometry as G

KINDS: tuple[str, ...] = ("furniture", "furniture_proxy", "decor", "door")
HUNG_TYPES: tuple[str, ...] = ("pendant_light", "ceiling_light")
CEILING_TOL_M = 0.01             # a box may touch the ceiling by this much (a bevel, a rounding)


def _levels(building: dict) -> dict:
    return {lv["id"]: lv for lv in (building or {}).get("levels") or [] if lv.get("id") and lv.get("ceiling_planes")}


def roof_of(building: dict) -> Optional[dict]:
    """The roof model the build makes (``roof.roof_model``), None without one or when it cannot be made."""
    roof = (building or {}).get("roof")
    if not isinstance(roof, dict):
        return None
    from wenart.blender import roof as R

    try:
        return R.roof_model(roof, building)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None


def element_of(o: dict) -> str:
    """The element a manifest entry belongs to: a hosted or hostless decor item's own id, else its element's."""
    if o.get("kind") == "decor" and o.get("decor_id"):
        return str(o["decor_id"])
    return str(o.get("element_id") or o.get("wenart_id") or o.get("name"))


def crossings(objects: Sequence[dict], building: dict, roof_model: Optional[dict] = None) -> list[dict]:
    """The crossings (module docstring): ``[{"target", "name", "kind", "type", "room_id", "level_id", "top_m",
    "ceiling_m", "roof_m", "over_m", "through_roof", "severity", "message"}]``, heights over the level's floor, one
    per element (its worst part), in the order of ``objects``."""
    from wenart.blender import geom2d

    levels = _levels(building)
    if not levels:
        return []
    model = roof_model if roof_model is not None else roof_of(building)
    if model is not None:
        from wenart.blender import roof as R
    worst: dict = {}
    order: list = []
    for o in objects or ():
        if not isinstance(o, dict) or o.get("kind") not in KINDS or o.get("type") in HUNG_TYPES:
            continue
        level = levels.get(o.get("level_id"))
        box = o.get("box3d")
        if level is None or not isinstance(box, dict) or not box.get("size") \
                or (o.get("room_id") and o.get("room_id") in (level.get("open_rooms") or ())):
            continue                                       # no ceiling over a room open to the sky
        cx, cy, cz = (float(v) for v in box["center"])
        w, d, h = (float(v) for v in box["size"])
        top = cz + h / 2.0
        pts = list(G.rotated_rectangle((cx, cy), (max(w, 1e-4), max(d, 1e-4)), float(box.get("rotation_deg") or 0.0)))
        if model is not None:
            pts = [p for p in pts if R.covers(model, float(p[0]), float(p[1]))]
            if not pts:
                continue                                   # out of the roof's outline: under the sky
        # 31 Oct 2026: under a dormer its ceiling (the level's ``ceiling_dormers``, dormers.py)
        ceiling = min(geom2d.raised_surface_z(level["ceiling_planes"], float(x), float(y),
                                              level.get("ceiling_dormers")) for x, y in pts)
        if top <= ceiling + CEILING_TOL_M:
            continue
        roof_top = min(R.top_z(model, float(x), float(y)) for x, y in pts) if model is not None else None
        through = roof_top is not None and top > roof_top + CEILING_TOL_M
        floor = float(level.get("elevation") or 0.0)
        target = element_of(o)
        rec = {"target": target, "name": o.get("name"), "kind": o.get("kind"), "type": o.get("type"),
               "room_id": o.get("room_id"), "level_id": o.get("level_id"), "top_m": round(top - floor, 3),
               "ceiling_m": round(ceiling - floor, 3), "roof_m": None if roof_top is None else round(roof_top - floor, 3),
               "over_m": round(top - ceiling, 3), "through_roof": through,
               "severity": "critical" if through else "major"}
        what = f"door {target} ({o.get('name')})" if o.get("kind") == "door" else \
            f"{o.get('type') or o.get('kind')} {target}"
        rec["message"] = (f"{what} reaches {rec['top_m']:.2f} m over its floor where the sloped ceiling over it is "
                          f"{rec['ceiling_m']:.2f} m high" + (f" and the roof's top {rec['roof_m']:.2f} m: it pokes "
                                                             "through the roof" if through else
                                                             ": it runs into the ceiling")
                          + " (UL128: nothing inside crosses the roof)")
        if target not in worst:
            order.append(target)
            worst[target] = rec
        elif rec["over_m"] > worst[target]["over_m"]:
            worst[target] = rec
    return [worst[t] for t in order]


def dormer_problems(building: dict, manifest: Optional[dict] = None) -> list[dict]:
    """31 Oct 2026 (dormers.py): every opening a dormer serves (its ``dormer`` record) whose dormer the scene does not
    hold (``dormer_not_built``: a scene manifest with the roof built and no object of detail ``dormer`` of that id) or
    whose door still reaches over the ceiling at its frame (``dormer_too_low``: ``door_states.head_room`` with the
    level's ``ceiling_dormers``). ``[{"target", "severity", "problem", "level_id", "message"}]``, major (pure)."""
    from wenart.blender import door_states as DS

    objs = (manifest or {}).get("objects") or []
    built = {o.get("wenart_id") for o in objs if o.get("detail") == "dormer"} \
        if any(o.get("wenart_id") == "roof" for o in objs) else None
    levels = {lv.get("id"): lv for lv in (building or {}).get("levels") or []}
    walls = {w.get("id"): w for w in (building or {}).get("walls") or []}
    out = []
    for o in (building or {}).get("openings") or []:
        rec = o.get("dormer") if isinstance(o.get("dormer"), dict) else None
        if rec is None:
            continue
        if built is not None and rec.get("id") not in built:
            out.append({"target": o.get("id"), "severity": "major", "problem": "dormer_not_built",
                        "level_id": o.get("level_id"),
                        "message": f"{o.get('type')} {o.get('id')} keeps its height for the dormer {rec.get('id')}, "
                                   f"which the scene does not hold: it crosses the roof"})
            continue
        lv, wall = levels.get(o.get("level_id")), walls.get(o.get("wall_id"))
        if o.get("type") != "door" or lv is None or wall is None:
            continue
        room = DS.head_room(o, wall, lv)
        if room is not None and DS.door_height_of(o) > room + DS.HEIGHT_TOL_M:
            out.append({"target": o.get("id"), "severity": "major", "problem": "dormer_too_low",
                        "level_id": o.get("level_id"),
                        "message": f"door {o.get('id')} is {DS.door_height_of(o):.2f} m high under its dormer "
                                   f"{rec.get('id')}, whose ceiling leaves it {room:.2f} m at its frame"})
    return out


def door_problems(building: dict) -> list[dict]:
    """The doors the build could not fit under the slope at their wall nor slide (module docstring)."""
    from wenart.blender import door_states as DS

    out = []
    for o in (building or {}).get("openings") or []:
        rec = o.get("under_roof") if isinstance(o.get("under_roof"), dict) else None
        if o.get("type") != "door" or rec is None or rec.get("fits") is not False:
            continue
        out.append({"target": o.get("id"), "severity": "major", "level_id": o.get("level_id"),
                    "message": f"door {o.get('id')} is only {float(rec.get('height') or 0.0):.2f} m high under the "
                               f"sloped ceiling at its wall (a usable door needs {DS.MIN_CLEAR_M:.2f} m): it needs a "
                               f"dormer or a raised roof ({rec.get('reason')})"})
    return out
