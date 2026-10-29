"""Facade articulation of the whole building (docs/milestone11.md §1.1 E10, §4.1 X8, §7).

What: ``articulation_plan(...)`` lays out what turns a plain rendered box into a facade: a plinth band at the
foot of the walls that meet the ground, a slab band at every upper floor, a coping on a flat roof's parapet,
and, for the classic styles, stone surrounds around the windows (the modern styles keep the reveal the wall
thickness already gives). ``build_articulation`` (bpy) makes one object per kind and level.

Why: real02's facades were one plain render material with long blank walls (E10); the documents draw none of
these details, so they come from the style (``style.family``) and are listed as ``assumed`` (inferred from the
style) in the scene manifest.

How: pure Python on the level outlines (``geom2d.wall_outline``, the outer wall faces): every outline edge
gets a thin box ``proud`` metres in front of its face, cut where a door, a window or a light well / front court
crosses the band (``_spans``). The looks come from ``ARTICULATION`` per style family and the resolved outside
looks (``exterior.resolve_looks``; the agent's ``plinth`` / ``cornice`` / ``surround`` material slots override
them).

Milestone 13 (docs/milestone13.md §13.2, track T6; §1.7: "a box with bands"): the facade kit (``facade_kit``), added
to the plan only where the documents or the room types imply it, every box ``inferred`` with its reason: window
reveals (a thin frame at the outer face of every window of the modern families, which get no surround), gutters
along the roof's eaves edges and downpipes at their corners (a pitched roof drawn in the documents), an entrance
canopy and a pair of wall lights at every entrance door at grade (``site.entrances``), and a guard rail in front of
an upper-floor outside door that opens onto no balcony or terrace room (a door drawn there implies one).
``KIT`` holds the sizes; the looks are ``KIT_LOOKS`` (the agent's material slots of the same names override them).

Facade scheme (user request of 24 Oct 2026: the outside walls "seem blank concrete"): when no drawing and no brief
names the facade, the style family gives it a designed default (``FACADE_SCHEMES``, ``scheme_faces``): the main walls
in render of the family's facade colour (``exterior.resolve_looks``), the walls of the basement levels in the family's
base cladding (stone, brick), and a band of the family's accent cladding framing the main entrance door, from the
entrance floor to the floor above (``ACCENT``). Every face is ``inferred`` with its reason; the plinth band takes the
base cladding too. A face may carry a ``span`` (two plan points on its wall): only the stretch between them takes it.

29 Oct 2026 (user on real06: "Outside wall texture can be changed"; the judge: "a flat white box with no material
rhythm"): a house of two or more storeys above the ground takes the family's ``upper`` cladding on its top storey
(timber over a rendered ground floor for the Scandinavian, Japandi, modern and rustic families, fibre-cement panels
for the industrial one); the families whose look is one render (minimal, classic, Mediterranean) keep it.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# Per style family: the plinth look and height, whether the windows get surrounds (else reveals).
ARTICULATION = {
    "default": {"plinth": "stone_wall_ledgestone", "plinth_colour": None, "surround": None},
    "classic": {"plinth": "stone_cladding", "plinth_colour": None, "surround": "limestone"},
    "mediterranean": {"plinth": "stone_cladding", "plinth_colour": None, "surround": "limestone"},
    "rustic": {"plinth": "stone_wall_rubble", "plinth_colour": None, "surround": "limestone"},
}
# The facade scheme per style family (user request of 24 Oct 2026): the main walls' render colour, the base cladding
# of the basement levels and the accent cladding around the main entrance (None: no accent). Vocabulary slugs and
# colour names of wenart/style; a family not listed takes "default".
FACADE_SCHEMES = {
    "default": {"main": ("render", "off white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding",
                "upper": "wood_cladding"},
    "modern": {"main": ("render", "off white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding",
               "upper": "wood_cladding"},
    "modern minimal": {"main": ("render", "white"), "base": "stone_wall_slate", "accent": "wood_cladding",
                       "upper": None},
    "minimal": {"main": ("render", "white"), "base": "stone_wall_slate", "accent": "wood_cladding", "upper": None},
    "scandinavian": {"main": ("render", "white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding",
                     "upper": "wood_cladding"},
    "japandi": {"main": ("render", "off white"), "base": "stone_wall_slate", "accent": "wood_cladding",
                "upper": "wood_cladding"},
    "industrial": {"main": ("render", "light grey"), "base": "brick_red", "accent": None, "upper": "fibre_cement"},
    "mediterranean": {"main": ("render", "cream"), "base": "stone_wall_ashlar", "accent": None, "upper": None},
    "classic": {"main": ("render", "ivory"), "base": "stone_wall_ashlar", "accent": None, "upper": None},
    "rustic": {"main": ("render", "cream"), "base": "stone_wall_rubble", "accent": "wood_cladding",
               "upper": "wood_cladding"},
}
UPPER = {"min_storeys": 2}         # storeys above the ground for the top storey's cladding
ACCENT = {"margin_m": 1.0, "min_width_m": 2.4}      # the accent band: the door plus 1 m on each side, >= 2.4 m wide
DIMENSIONS = {"plinth_height": 0.45, "plinth_below": 0.05, "proud": 0.025, "band_height": 0.20, "band_proud": 0.03,
              "coping_height": 0.06, "coping_proud": 0.04, "surround_width": 0.12, "surround_proud": 0.03,
              "min_span": 0.15}


# Milestone 13 (T6): the facade kit sizes (metres) and looks (vocabulary slugs; a colour name or None).
KIT = {"reveal_width": 0.06, "reveal_proud": 0.015, "gutter_w": 0.12, "gutter_h": 0.10, "gutter_drop": 0.02,
       "downpipe": 0.10, "downpipe_every_m": 12.0, "downpipe_end_m": 0.4, "downpipe_both_ends_m": 4.0,
       "pipe_search_m": 3.0, "pipe_search_step_m": 0.1, "pipe_wall_tol_m": 0.15, "pipe_min_gap_m": 1.5, "eaves_tol": 0.15,
       # 26 Oct 2026 (downpipe_plan): building-wide pipes at the corners, >= pipe_gap_m apart, a gutter drains at most
       # max_drain_m to a pipe, one end of a run up to single_end_m, at most one pipe per area_per_pipe_m2 of roof
       "pipe_gap_m": 3.0, "max_drain_m": 12.0, "single_end_m": 10.0, "area_per_pipe_m2": 50.0,
       "canopy_depth": 1.0, "canopy_thick": 0.08, "canopy_side": 0.3, "canopy_above": 0.25,
       "light_w": 0.12, "light_d": 0.08, "light_h": 0.22, "light_z": 2.1, "light_offset": 0.35,
       "guard_height": 1.0, "guard_bar": 0.04, "guard_min_drop": 1.0, "guard_side": 0.05,
       # 26 Oct 2026: a guard reaches guard_top over its floor where an opening's bottom is under guard_sill
       "guard_top": 1.10, "guard_sill": 0.85, "guard_channel": 0.06, "guard_channel_h": 0.09, "guard_cap": 0.03,
       "guard_glass_t": 0.012}
KIT_LOOKS = {
    "reveal": ("render", "white", "window reveal frame at the outer face (modern family; not drawn)"),
    "gutter": ("aluminium_anthracite", None, "gutter along the eaves (a pitched roof is drawn; the gutter is not)"),
    "downpipe": ("aluminium_anthracite", None, "downpipe at the eaves corners (not drawn)"),
    "canopy": ("render", "white", "entrance canopy over the entrance door (the door is drawn; the canopy is not)"),
    "wall_light": ("steel_black", None, "wall light beside the entrance door (not drawn)"),
    "railing": ("steel_brushed", None, "guard's metal (rails, posts, bars or a glass channel) in front of an opening "
                                        "over a drop with no balcony (not drawn)"),
    "guard_glass": ("glass_guard", None, "glass guard in front of an opening over a drop with no balcony (not drawn)"),
}
KIT_KINDS = tuple(KIT_LOOKS)


def scheme_of(style: Optional[dict]) -> dict:
    """The facade scheme of the style's family (``FACADE_SCHEMES``), with ``family``."""
    fam = str((style or {}).get("family") or "").lower()
    return dict(FACADE_SCHEMES.get(fam) or FACADE_SCHEMES["default"], family=fam or "default")


def main_entrance(building: dict, levels: Sequence[dict]) -> Optional[dict]:
    """The main entrance door of the building (``site.entrances``: the one marked ``main``, else the first at grade
    on the lowest level that has one), as its opening dict, or None."""
    ids = {lv["id"] for lv in levels}
    recs = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
            and r.get("level_id") in ids and not r.get("into_air") and not r.get("below_ground")]
    if not recs:
        return None
    order = {lv["id"]: float(lv["elevation"]) for lv in levels}
    rec = next((r for r in recs if r.get("main")), None) or min(recs, key=lambda r: (order[r["level_id"]],
                                                                                       float(r.get("rise") or 0.0)))
    return next((o for o in building.get("openings") or [] if o.get("id") == rec.get("door_id")), None)


def scheme_faces(building: dict, style: Optional[dict], levels: Sequence[dict]) -> list[dict]:
    """The inferred facade faces of the style's scheme (pure; the caller asks only when no drawing and no brief name
    the facade): the accent band around the main entrance first (``span`` and ``z_range``), then the base cladding
    of every basement level. Each face: ``material``, ``colour``, ``side`` all, ``level_id`` / ``wall_id``, ``source``
    ``inferred``, ``inferred`` True and its ``reason``."""
    sch = scheme_of(style)
    faces: list[dict] = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    door = main_entrance(building, order) if sch.get("accent") else None
    wall = next((w for w in building.get("walls") or [] if door and w.get("id") == door.get("wall_id")), None)
    if door is not None and wall is not None:
        (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length > 1e-6:
            ux, uy = (x1 - x0) / length, (y1 - y0) / length
            cx, cy = door["center"][:2]
            t = (cx - x0) * ux + (cy - y0) * uy
            half = max(float(door.get("width") or 0.9) / 2.0 + ACCENT["margin_m"], ACCENT["min_width_m"] / 2.0)
            t0, t1 = max(0.0, t - half), min(length, t + half)
            lv = next(lv for lv in order if lv["id"] == wall.get("level_id"))
            above = [float(x["elevation"]) for x in order if float(x["elevation"]) > float(lv["elevation"]) + 0.5]
            z1 = min(above) if above else float(lv["elevation"]) + float(lv.get("height") or 3.0)
            faces.append({"material": sch["accent"], "colour": None, "side": "all", "wall_id": wall["id"],
                          "span": [[x0 + ux * t0, y0 + uy * t0], [x0 + ux * t1, y0 + uy * t1]],
                          "z_range": [float(lv["elevation"]) - 0.5, z1], "source": "inferred", "inferred": True,
                          "reason": f"facade scheme ({sch['family']}): {sch['accent']} framing the main entrance "
                                    f"{door['id']} ({t1 - t0:.1f} m wide; not drawn)"})
    for lv in order:
        if str(lv.get("kind") or "") == "basement":
            faces.append({"material": sch["base"], "colour": None, "side": "all", "level_id": lv["id"],
                          "source": "inferred", "inferred": True,
                          "reason": f"facade scheme ({sch['family']}): {sch['base']} on the basement level "
                                    f"{lv['id']} (not drawn)"})
    top = upper_level(sch, order)
    if top is not None:
        faces.append({"material": sch["upper"], "colour": None, "side": "all", "level_id": top["id"],
                      "source": "inferred", "inferred": True, "upper": True,
                      "reason": f"facade scheme ({sch['family']}): {sch['upper']} on the top storey {top['id']} over "
                                f"the rendered floors below (not drawn)"})
    return faces


def storeys(levels: Sequence[dict]) -> list[dict]:
    """The storeys above the ground, lowest first: the levels that are neither a basement nor a roof or open-air
    level (pure)."""
    return sorted((lv for lv in levels if str(lv.get("kind") or "floor") not in ("basement", "roof", "site", "terrain")),
                  key=lambda lv: float(lv["elevation"]))


def upper_level(scheme: dict, levels: Sequence[dict]) -> Optional[dict]:
    """The storey that takes the scheme's ``upper`` cladding: the top one of at least ``UPPER["min_storeys"]``
    storeys above the ground, None for a family without one (pure)."""
    up = storeys(levels)
    return up[-1] if scheme.get("upper") and len(up) >= UPPER["min_storeys"] else None


def on_span(point, span, tol: float = 1e-3) -> bool:
    """Whether the plan ``point`` projects onto the segment ``span`` (``[[x0, y0], [x1, y1]]``)."""
    (x0, y0), (x1, y1) = span[0][:2], span[1][:2]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-9:
        return False
    t = ((float(point[0]) - x0) * (x1 - x0) + (float(point[1]) - y0) * (y1 - y0)) / length
    return -tol <= t <= length + tol


def family_rules(style: Optional[dict]) -> dict:
    fam = str((style or {}).get("family") or "").lower()
    return dict(ARTICULATION["default"], **ARTICULATION.get(fam, {}), family=fam or None)


def band_colour(facade_look: dict) -> str:
    """The slab band's colour: white on a coloured facade, light grey on a white one (a band of the facade's own
    colour only reads through its shadow)."""
    colour = str((facade_look or {}).get("colour") or "").lower()
    return "light grey" if colour in ("", "white", "off white", "warm white", "walls") else "white"


def _spans(length: float, cuts: Sequence[tuple[float, float]], min_span: float) -> list[tuple[float, float]]:
    """The stretches of ``[0, length]`` outside ``cuts`` (each ``(t0, t1)`` in metres), at least ``min_span``."""
    out, t = [], 0.0
    for a, b in sorted(cuts):
        if t >= length:
            break
        if min(a, length) > t + min_span:
            out.append((t, min(a, length)))
        t = max(t, b)
    if length - t > min_span:
        out.append((t, length))
    return out


def _edge_cuts(p, q, items: Sequence[dict], z0: float, z1: float, tol: float = 0.35) -> list[tuple[float, float]]:
    """Along the edge ``p``-``q`` the stretches that ``items`` (``{"centre", "half", "bottom", "top"}``, or
    ``{"polygon"}`` for a light well / court reaching the wall) cross between heights ``z0`` and ``z1``."""
    length = G.distance(p, q)
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    out = []
    for it in items:
        if "polygon" in it:
            near = [((x - p[0]) * ux + (y - p[1]) * uy) for x, y in it["polygon"]
                    if abs((x - p[0]) * -uy + (y - p[1]) * ux) <= tol]
            if near:
                out.append((min(near) - 0.05, max(near) + 0.05))
            continue
        c = it["centre"]
        if abs((c[0] - p[0]) * -uy + (c[1] - p[1]) * ux) > tol or it["top"] <= z0 or it["bottom"] >= z1:
            continue
        t = (c[0] - p[0]) * ux + (c[1] - p[1]) * uy
        out.append((t - it["half"] - 0.03, t + it["half"] + 0.03))
    return out


def _band_boxes(outline, z0: float, z1: float, proud: float, items, kind: str, level_id: Optional[str],
                min_span: float = DIMENSIONS["min_span"]) -> list[dict]:
    """One box per uncut stretch of every outline edge: ``proud`` in front of the face, from ``z0`` to ``z1``."""
    out = []
    pts = geom2d.ccw(outline)
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        length = G.distance(p, q)
        if length < min_span:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux                                       # counter-clockwise outline: right of the edge is out
        for a, b in _spans(length, _edge_cuts(p, q, items, z0, z1), min_span):
            # the band runs on past convex corners by its own depth, so two bands meet without a slit
            a2 = a - proud if a <= 1e-9 else a
            b2 = b + proud if b >= length - 1e-9 else b
            mid = ((a2 + b2) / 2.0)
            out.append({"kind": kind, "level_id": level_id,
                        "center": [p[0] + ux * mid + nx * proud / 2.0, p[1] + uy * mid + ny * proud / 2.0,
                                   (z0 + z1) / 2.0],
                        "size": [b2 - a2, proud, z1 - z0], "rotation_deg": math.degrees(math.atan2(uy, ux))})
    return out


def opening_items(building: dict, level: dict, outline, levels_above: bool) -> list[dict]:
    """The doors and windows of a level as band cuts: ``{"centre", "half", "bottom", "top", "id", "type"}``."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    out = []
    for o in building.get("openings") or []:
        wall = walls.get(o.get("wall_id"))
        if o.get("level_id") != level["id"] or wall is None or o.get("type") not in ("door", "window", "opening"):
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        bottom, top, _ = opening_vertical(o, level, levels_above)
        # the centre on the outer face line (the outline), so the cut test works on the face
        out.append({"centre": (cx, cy), "half": float(o["width"]) / 2.0, "bottom": bottom, "top": top,
                    "id": o["id"], "type": o["type"], "thickness": float(wall["thickness"])})
    return out


def articulation_plan(building: dict, levels: Sequence[dict], outlines: dict, ground_outline, terrain: Optional[dict],
                      roof_model: Optional[dict], style: Optional[dict], looks: Optional[dict],
                      wells: Sequence[dict] = ()) -> dict:
    """``{"boxes": [{"kind": plinth | band | coping | surround, "level_id", "center", "size", "rotation_deg"}],
    "looks": {kind: look}, "rules", "assumed": [{"field", "value", "reason"}]}`` (pure).

    - plinth: ``plinth_height`` above the ground (``site.ground_z`` at each edge; flat 0 without a terrain) along
      the ground outline, cut at doors, at windows reaching into it and at light wells and front courts;
    - band: at the floor of every level above the lowest level that meets the ground (``band_height``, centred
      on the slab under that floor), on that level's outline below it, cut at openings;
    - coping: on top of a flat roof's walls (the top level's outline at the roof's eaves height);
    - surround: for the families with ``surround`` (classic, mediterranean, rustic), a frame of
      ``surround_width`` around every outside window (head and jambs; the sill is the window's own).
    """
    from wenart.blender import site as S

    rules = family_rules(style)
    looks = looks or {}
    facade = looks.get("facade") or {"material": "render", "colour": "white"}
    out_looks = {
        "plinth": looks.get("plinth") or {"material": rules["plinth"], "colour": rules["plinth_colour"],
                                          "source": "build", "assumed": True,
                                          "reason": f"plinth band: {rules['plinth']} (style family "
                                                    f"{rules['family'] or 'default'}; not drawn)"},
        "band": looks.get("cornice") or {"material": facade.get("material") or "render", "colour": band_colour(facade),
                                         "source": "build", "assumed": True,
                                         "reason": "slab band / coping: the facade material, set off in colour "
                                                   "(not drawn)"},
        "surround": looks.get("surround") or {"material": rules["surround"] or "limestone", "colour": None,
                                              "source": "build", "assumed": True,
                                              "reason": "window surround (style family; not drawn)"},
    }
    out_looks["coping"] = out_looks["band"]
    boxes: list[dict] = []
    assumed = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: 0.0)
    if len(ground_outline or []) >= 3:
        cuts = [dict(it, bottom=it["bottom"], top=it["top"]) for lv in order
                for it in opening_items(building, lv, outlines.get(lv["id"]) or ground_outline, True)]
        cuts += [{"polygon": w["polygon"]} for w in wells or []]
        plinth = plinth_rule(building)
        boxes += _plinth(ground_outline, cuts, gz, plinth)     # one ground height per edge: its lower end
        if plinth is None:
            assumed.append({"field": "plinth", "value": DIMENSIONS["plinth_height"],
                            "reason": out_looks["plinth"]["reason"]})
        else:
            assumed.append({"field": "plinth", "value": {"top_z": plinth["top_z"], "min_height": plinth["min"]},
                            "reason": f"plinth: a raised base from the ground up to {plinth['top_z']:+.2f} m "
                                      f"({plinth['source']}), at least {plinth['min']:.2f} m high; "
                                      + out_looks["plinth"]["reason"]})
    ground_top = max(terrain["z"].values()) if terrain else 0.0
    lowest_above = next((lv for lv in order if float(lv["elevation"]) + float(lv["ceiling_height"]) > ground_top + 0.5),
                        None)
    slabs = {s.get("above_level_id"): s for s in building.get("slabs") or []}
    for i, lv in enumerate(order):
        if lowest_above is None or float(lv["elevation"]) <= float(lowest_above["elevation"]) + 1e-6:
            continue
        below = order[i - 1]
        outline = outlines.get(below["id"]) or outlines.get(lv["id"])
        if len(outline or []) < 3:
            continue
        t = float((slabs.get(lv["id"]) or {}).get("thickness") or 0.2)
        zc = float(lv["elevation"]) - t / 2.0
        h = max(DIMENSIONS["band_height"], t)
        cuts = opening_items(building, below, outline, True) + opening_items(building, lv, outline, True)
        boxes += _band_boxes(outline, zc - h / 2.0, zc + h / 2.0, DIMENSIONS["band_proud"], cuts, "band", lv["id"])
    if boxes and any(b["kind"] == "band" for b in boxes):
        assumed.append({"field": "slab_band", "value": DIMENSIONS["band_height"], "reason": out_looks["band"]["reason"]})
    if roof_model and roof_model.get("type") == "flat" and roof_model.get("over_level_id"):
        top = next((lv for lv in order if lv["id"] == roof_model["over_level_id"]), None)
        outline = outlines.get(top["id"]) if top else None
        if outline and len(outline) >= 3 and roof_model.get("eaves_z") is not None:
            z = float(roof_model["eaves_z"]) + float(roof_model.get("parapet") or 0.0)   # M12: on a flat_cut parapet
            boxes += _band_boxes(outline, z, z + DIMENSIONS["coping_height"], DIMENSIONS["coping_proud"], [], "coping",
                                 top["id"])
            assumed.append({"field": "coping", "value": DIMENSIONS["coping_height"], "reason": out_looks["band"]["reason"]})
    if rules["surround"]:
        n0 = len(boxes)
        for lv in order:
            outline = outlines.get(lv["id"])
            if len(outline or []) < 3:
                continue
            boxes += _surrounds(building, lv, outline)
        if len(boxes) > n0:
            assumed.append({"field": "surround", "value": DIMENSIONS["surround_width"],
                            "reason": out_looks["surround"]["reason"]})
    # Milestone 13 (T6): the facade kit, only where the documents or the room types imply it
    kit = facade_kit(building, levels, outlines, ground_outline, terrain, roof_model, rules, looks, style)
    boxes += kit["boxes"]
    out_looks.update(kit["looks"])
    assumed += kit["assumed"]
    return {"boxes": boxes, "looks": out_looks, "rules": rules, "assumed": assumed, "kit": kit["summary"]}


def _box(kind: str, level_id, centre, size, rot: float, parent=None, reason: str = "") -> dict:
    return {"kind": kind, "level_id": level_id, "center": [float(c) for c in centre], "size": [float(v) for v in size],
            "rotation_deg": float(rot), "inferred": True, "parent": parent, "reason": reason}


def guard_boxes(p, q, bottom: float, top: float, level_id, parent, kind: str = "glass_channel") -> list[dict]:
    """A guard from ``p`` to ``q`` in the house's one balustrade language (pure; 26 Oct 2026; 27 Oct 2026, generality
    review: it was always frameless glass, while the stairs and balconies follow ``details.balustrade_kind``): kind
    ``glass_channel`` a metal channel at the opening's bottom and one glass pane up to a cap rail at ``top``;
    ``glass_posts`` posts at most ``details.DIMS["post_every"]`` apart, a handrail and a glass pane in each bay;
    ``bars`` posts, a handrail, a bottom rail and vertical bars ``bar_pitch`` apart (box kinds ``railing`` and
    ``guard_glass``). No gap a child could pass (the 0.11 m rule)."""
    from wenart.blender import details as D

    length = G.distance(p, q)
    if length < 0.1 or top - bottom < 0.1:
        return []
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    rot = math.degrees(math.atan2(uy, ux))
    mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
    ch, chh, cap, gt = KIT["guard_channel"], KIT["guard_channel_h"], KIT["guard_cap"], KIT["guard_glass_t"]
    why, why_glass = KIT_LOOKS["railing"][2], KIT_LOOKS["guard_glass"][2]

    def at(t):
        return p[0] + ux * t, p[1] + uy * t

    if kind not in ("glass_posts", "bars"):
        out = [_box("railing", level_id, (mx, my, bottom + chh / 2.0), (length, ch, chh), rot, parent, why),
               _box("railing", level_id, (mx, my, top - cap / 2.0), (length, ch * 0.6, cap), rot, parent, why)]
        g0, g1 = bottom + chh - 0.03, top - cap + 0.01
        out.append(_box("guard_glass", level_id, (mx, my, (g0 + g1) / 2.0), (length - 0.02, gt, g1 - g0), rot, parent,
                        why_glass))
        return out
    c = D.DIMS
    post, rail = 2 * c["post_r"], 2 * c["handrail_r"]
    n = max(1, int(math.ceil(length / c["post_every"] - 1e-9)))
    stations = [post / 2.0 + (length - post) * k / n for k in range(n + 1)]
    out = [_box("railing", level_id, (mx, my, top - rail / 2.0), (length, rail, rail), rot, parent, why)]
    for t in stations:
        x, y = at(t)
        out.append(_box("railing", level_id, (x, y, (bottom + top - rail) / 2.0), (post, post, top - rail - bottom),
                        rot, parent, why))
    if kind == "glass_posts":
        for t0, t1 in zip(stations, stations[1:]):
            a, b = t0 + post / 2.0 + c["bay_gap"], t1 - post / 2.0 - c["bay_gap"]
            if b - a < 0.1:
                continue
            x, y = at((a + b) / 2.0)
            g0, g1 = bottom + c["glass_bottom"], top - rail - 0.04
            out.append(_box("guard_glass", level_id, (x, y, (g0 + g1) / 2.0), (b - a, gt, g1 - g0), rot, parent,
                            why_glass))
        return out
    zb = bottom + c["bottom_rail_z"]
    out.append(_box("railing", level_id, (mx, my, zb + c["flat_t"]), (length, c["flat_w"] * 0.6, 2 * c["flat_t"]),
                    rot, parent, why))
    z0, z1 = zb + 2 * c["flat_t"], top - rail
    for t0, t1 in zip(stations, stations[1:]):
        a, b = t0 + post / 2.0, t1 - post / 2.0
        k = max(1, int(math.ceil((b - a) / c["bar_pitch"] - 1e-9)))
        for j in range(1, k):
            x, y = at(a + (b - a) * j / k)
            out.append(_box("railing", level_id, (x, y, (z0 + z1) / 2.0), (c["bar_w"], c["bar_w"], z1 - z0), rot,
                            parent, why))
    return out


def eaves_edges(roof_model: Optional[dict]) -> list[dict]:
    """The eaves edges of a pitched roof (pure): the outline edges along which the roof's top surface stays within
    ``KIT["eaves_tol"]`` of ``eaves_z`` (a gable end rises to the ridge: no gutter there), without their runs along
    a roof opening (a roof terrace has no eaves). ``[{"p", "q", "z", "length"}]``; none for a flat roof or without
    planes."""
    if not roof_model or not roof_model.get("equations") or roof_model.get("eaves_z") is None:
        return []
    if roof_model.get("type") in ("flat", None) or roof_model.get("kind") == "flat_cut":
        return []
    from wenart.blender import roof as R

    outline = geom2d.ccw(roof_model.get("outline") or [])
    eaves = float(roof_model["eaves_z"])
    holes = [o["polygon"] for o in roof_model.get("openings") or [] if len(o.get("polygon") or []) >= 3]
    out = []
    n = len(outline)
    for i in range(n):
        p, q = outline[i], outline[(i + 1) % n]
        length = G.distance(p, q)
        if length < 0.5:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = -uy, ux                                     # ccw outline: the left normal points inward
        zs = []
        for t in (0.15, 0.5, 0.85):
            x, y = p[0] + ux * t * length + nx * 0.05, p[1] + uy * t * length + ny * 0.05
            zs.append(R.top_z(roof_model, x, y))
        if not all(abs(z - eaves) <= KIT["eaves_tol"] for z in zs):
            continue
        # 24 Oct 2026 (real04): a roof terrace cut into the roof has no eaves: the gutter ran on along its parapet
        # past the end of the roof. The edge keeps only its runs outside the roof openings.
        for t0, t1 in _runs_outside(p, (ux, uy), (nx, ny), length, holes):
            a = (p[0] + ux * t0, p[1] + uy * t0)
            b = (p[0] + ux * t1, p[1] + uy * t1)
            out.append({"p": a, "q": b, "z": eaves, "length": t1 - t0})
    return out


def _wall_point(pt, outline):
    """``(x, y, outward normal, distance)``: the nearest point of an outline's boundary to ``pt``."""
    dist, (a, b) = geom2d.nearest_edge(pt, outline)
    tt = max(0.0, min(1.0, ((pt[0] - a[0]) * (b[0] - a[0]) + (pt[1] - a[1]) * (b[1] - a[1])) /
                      max(1e-9, G.distance(a, b) ** 2)))
    wx, wy = a[0] + (b[0] - a[0]) * tt, a[1] + (b[1] - a[1]) * tt
    wn = G.unit_normal_left(a, b)
    if G.point_in_polygon((wx + wn[0] * 0.05, wy + wn[1] * 0.05), outline):
        wn = (-wn[0], -wn[1])
    return wx, wy, wn, math.hypot(pt[0] - wx, pt[1] - wy)


def _opening_spans(building: dict, level_id: str) -> list[tuple]:
    """``[(cx, cy, ux, uy, half_width, bottom, top)]`` of the doors and windows of a level (pure)."""
    from wenart.blender.shell import opening_centre_on_wall

    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level_id}
    lv = next((x for x in building.get("levels") or [] if x["id"] == level_id), None)
    out = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != level_id or w is None or o.get("type") not in ("door", "window", "opening"):
            continue
        cx, cy, _ = opening_centre_on_wall(o, w)
        length = G.distance(w["start"], w["end"]) or 1.0
        ux, uy = (w["end"][0] - w["start"][0]) / length, (w["end"][1] - w["start"][1]) / length
        floor = float(lv["elevation"]) if lv else 0.0
        sill = float((o.get("sill_height") or {}).get("value") if isinstance(o.get("sill_height"), dict)
                     else o.get("sill_height") or 0.0)
        height = float((o.get("height") or {}).get("value") if isinstance(o.get("height"), dict)
                       else o.get("height") or 2.1)
        out.append((cx, cy, ux, uy, float(o.get("width") or 0.9) / 2.0, floor + sill, floor + sill + height))
    return out


def pipe_spot(p, u, n, length: float, t: float, z_top: float, levels: Sequence[dict], outlines: dict, top_outline,
              building: dict, gz) -> Optional[dict]:
    """Where a downpipe for the eaves station ``t`` stands (pure; 25 Oct 2026, user: "rain gutters going on the air,
    they need to be connected to walls"): the nearest spot within ``pipe_search_m`` of ``t`` along the eaves whose
    wall face, on every storey the pipe passes from ``z_top`` down to the ground, lies within ``pipe_wall_tol_m`` of the
    pipe (no loggia recess, no open corner) and crosses no door or window. ``{"t", "x", "y", "normal", "z0"}`` or
    None. A pipe stands ``downpipe / 2 + 0.02`` out from the top storey's wall face."""
    if len(top_outline or []) < 3:
        return None
    d = KIT["downpipe"]
    step = KIT["pipe_search_step_m"]
    cands = [t]
    k = 1
    while k * step <= KIT["pipe_search_m"]:
        cands += [t + k * step, t - k * step]
        k += 1
    lo, hi = min(KIT["downpipe_end_m"], length / 2.0), max(length - KIT["downpipe_end_m"], length / 2.0)
    # then anywhere on the run, nearest first (a facade of loggias and ribbon windows may have one pier for it)
    far = [lo + j * step for j in range(int((hi - lo) / step) + 1)]
    cands += sorted((c for c in far if abs(c - t) > KIT["pipe_search_m"]), key=lambda c: abs(c - t))
    spans: dict = {}
    for tc in cands:
        if not lo - 1e-9 <= tc <= hi + 1e-9:
            continue
        ex, ey = p[0] + u[0] * tc, p[1] + u[1] * tc
        wx, wy, wn, _dist = _wall_point((ex, ey), top_outline)
        off = d / 2.0 + 0.02
        px, py = wx + wn[0] * off, wy + wn[1] * off
        # clear the outermost storey face under it (a pier or a band standing proud of the top wall)
        for _k in range(int(KIT["pipe_wall_tol_m"] / 0.02)):
            if not any(len(outlines.get(lv["id"]) or []) >= 3 and G.point_in_polygon((px, py), outlines[lv["id"]])
                       for lv in levels):
                break
            off += 0.02
            px, py = wx + wn[0] * off, wy + wn[1] * off
        z0 = gz(px, py) + 0.1
        if z_top - z0 < 1.0:
            continue
        ok = True
        for i, lv in enumerate(levels):
            floor = float(lv["elevation"])
            above = [float(x["elevation"]) for x in levels if float(x["elevation"]) > floor + 0.5]
            ceiling = min(above) if above else z_top
            if ceiling <= z0 + 0.05 or floor >= z_top - 0.05:
                continue                                  # the pipe does not pass this storey
            outline = outlines.get(lv["id"]) or []
            if len(outline) < 3:
                continue
            if G.point_in_polygon((px, py), outline):
                ok = False                                # the storey reaches out over the pipe
                break
            _x, _y, _n, dist = _wall_point((px, py), outline)
            if dist > d / 2.0 + 0.02 + KIT["pipe_wall_tol_m"]:
                ok = False                                # a recess (loggia) or no wall behind the pipe
                break
            if lv["id"] not in spans:
                spans[lv["id"]] = _opening_spans(building, lv["id"])
            for cx, cy, ox, oy, half, bottom, top in spans[lv["id"]]:
                along = (wx - cx) * ox + (wy - cy) * oy
                across = abs((wx - cx) * -oy + (wy - cy) * ox)
                if across < 0.4 and abs(along) < half + 0.12 and bottom < z_top and top > z0:
                    ok = False                            # a door or window under the pipe
                    break
            if not ok:
                break
        if ok:
            return {"t": tc, "x": px, "y": py, "normal": wn, "z0": z0}
    return None


def gutter_systems(edges: Sequence[dict], tol: float = 0.02) -> list[list[int]]:
    """The eaves runs joined end to start into gutter systems (pure; 26 Oct 2026): ``[[edge index, ...]]`` in the
    order of the outline; a hip roof's eaves all round are one closed system, a gable roof's two eaves two."""
    n = len(edges)
    nxt = {}
    for i, e in enumerate(edges):
        for j, f in enumerate(edges):
            if i != j and G.distance(e["q"], f["p"]) <= tol:
                nxt[i] = j
                break
    prv = {j: i for i, j in nxt.items()}
    seen: set = set()
    out = []
    for i in range(n):
        if i in seen:
            continue
        start, k = i, 0                                   # walk back to the chain's start (or round a loop)
        while start in prv and prv[start] != i and k <= n:
            start = prv[start]
            k += 1
        chain, cur = [], start
        while cur is not None and cur not in seen:
            chain.append(cur)
            seen.add(cur)
            cur = nxt.get(cur)
        out.append(chain)
    return out


def _corner_convex(e: dict, f: dict) -> bool:
    """Whether the outline turns left (an outer corner of the ccw roof outline) from edge ``e`` into edge ``f``."""
    ax, ay = e["q"][0] - e["p"][0], e["q"][1] - e["p"][1]
    bx, by = f["q"][0] - f["p"][0], f["q"][1] - f["p"][1]
    return ax * by - ay * bx > 1e-9


def downpipe_plan(edges: Sequence[dict], roof_area: float) -> list[tuple[int, float]]:
    """Where the downpipes of the whole roof go (pure; 26 Oct 2026, user: "why there is that many rain gutters"):
    ``[(edge index, t along the edge)]``, best first. An architect's rule, building-wide: a pipe at the outer corners
    of each gutter system (an open run: at its end corners, one end for a run up to ``single_end_m``), a pipe added
    where a gutter would drain more than ``max_drain_m`` to its nearest pipe, never two within ``pipe_gap_m`` along
    a system, and at most ``max(2, ceil(roof area / area_per_pipe))`` pipes in all (the corners spread furthest
    apart are kept). Every station then looks for a wall face clear of the openings (``pipe_spot``)."""
    end = KIT["downpipe_end_m"]
    systems = gutter_systems(edges)
    picks: list[tuple[int, float, float]] = []            # (edge, t, position along its system)
    per_system: list[list[tuple[int, float, float]]] = []
    for chain in systems:
        closed = len(chain) > 1 and G.distance(edges[chain[-1]]["q"], edges[chain[0]]["p"]) <= 0.02
        pos, offs = 0.0, []
        for i in chain:
            offs.append(pos)
            pos += float(edges[i]["length"])
        total = pos
        cands: list[tuple[int, float, float]] = []
        for k, i in enumerate(chain):
            prev = chain[k - 1] if (k > 0 or closed) else None
            if prev is None or _corner_convex(edges[prev], edges[i]):
                cands.append((i, min(end, edges[i]["length"] / 2.0), offs[k] + min(end, edges[i]["length"] / 2.0)))
        if not closed:
            last = chain[-1]
            t = max(edges[last]["length"] - end, edges[last]["length"] / 2.0)
            if total > KIT["single_end_m"] or not cands:
                cands.append((last, t, offs[-1] + t))
        cands.sort(key=lambda c: c[2])
        keep: list[tuple[int, float, float]] = []
        for c in cands:                                   # never two pipes close together along a system
            if all(abs(c[2] - k2[2]) >= KIT["pipe_gap_m"] and (not closed or total - abs(c[2] - k2[2])
                                                                  >= KIT["pipe_gap_m"]) for k2 in keep):
                keep.append(c)
        if not keep and chain:
            i = chain[0]
            keep.append((i, min(end, edges[i]["length"] / 2.0), min(end, edges[i]["length"] / 2.0)))
        # a gutter drains at most max_drain_m to a pipe: fill the long gaps
        pts = sorted(k2[2] for k2 in keep)
        gaps = [(pts[j], pts[j + 1]) for j in range(len(pts) - 1)]
        if closed and pts:
            gaps.append((pts[-1], pts[0] + total))
        elif pts:
            gaps += [(-pts[0], pts[0]), (pts[-1], 2 * total - pts[-1])]    # an open end drains back to its pipe
        for a, b in gaps:
            if b - a <= 2 * KIT["max_drain_m"]:
                continue
            for m in range(1, int(math.ceil((b - a) / (2 * KIT["max_drain_m"])))):
                s = a + (b - a) * m / math.ceil((b - a) / (2 * KIT["max_drain_m"]))
                s = s % total if closed and total else min(max(s, 0.0), total)
                for k, i in enumerate(chain):
                    if offs[k] - 1e-9 <= s <= offs[k] + edges[i]["length"] + 1e-9:
                        keep.append((i, s - offs[k], s))
                        break
        per_system.append(keep)
        picks += keep
    cap = max(2, int(math.ceil(float(roof_area) / KIT["area_per_pipe_m2"]))) if roof_area > 0 else len(picks)
    while len(picks) > cap:
        # drop the pipe closest to another one (Euclidean), never a system's last
        best = None
        for c in picks:
            mine = next(s for s in per_system if c in s)
            if len(mine) <= 1:
                continue
            ex, ey = _edge_point(edges[c[0]], c[1])
            near = min((math.hypot(ex - fx, ey - fy) for d in picks if d is not c
                        for fx, fy in [_edge_point(edges[d[0]], d[1])]), default=1e9)
            if best is None or near < best[0]:
                best = (near, c, mine)
        if best is None:
            break
        picks.remove(best[1])
        best[2].remove(best[1])
    return [(i, t) for i, t, _pos in picks]


def _edge_point(e: dict, t: float) -> tuple[float, float]:
    length = float(e["length"]) or 1.0
    return (e["p"][0] + (e["q"][0] - e["p"][0]) * t / length, e["p"][1] + (e["q"][1] - e["p"][1]) * t / length)


def downpipe_stations(length: float) -> list[float]:
    """Where the downpipes of an eaves run stand (pure): ``downpipe_end_m`` in from its start, then every
    ``downpipe_every_m``, and (24 Oct 2026) one ``downpipe_end_m`` in from its end when the run is longer than
    ``downpipe_both_ends_m`` (a gutter drains to both ends)."""
    end = KIT["downpipe_end_m"]
    out = []
    t = end
    while t <= length - 0.2:
        out.append(t)
        t += KIT["downpipe_every_m"]
    last = length - end
    if length > KIT["downpipe_both_ends_m"] and out and last - out[-1] > 1.0:
        out.append(last)
    return out


def _runs_outside(p, u, n, length: float, holes, step: float = 0.05, min_run: float = 0.5) -> list[tuple]:
    """``[(t0, t1)]``: the stretches of the edge from ``p`` along ``u`` whose points just inside (``n``, 5 cm) lie in
    none of ``holes`` (pure), at least ``min_run`` long."""
    if not holes:
        return [(0.0, length)]
    count = max(1, int(math.ceil(length / step)))
    free = []
    for k in range(count + 1):
        t = min(length, k * step)
        x, y = p[0] + u[0] * t + n[0] * 0.05, p[1] + u[1] * t + n[1] * 0.05
        free.append(not any(G.point_in_polygon((x, y), h) for h in holes))
    runs, start = [], None
    for k, ok in enumerate(free):
        t = min(length, k * step)
        if ok and start is None:
            start = t
        if (not ok or k == count) and start is not None:
            end = t if ok else max(start, t - step)
            if end - start >= min_run:
                runs.append((start, end))
            start = None
    return runs


def facade_kit(building: dict, levels: Sequence[dict], outlines: dict, ground_outline, terrain: Optional[dict],
               roof_model: Optional[dict], rules: dict, looks: Optional[dict] = None,
               style: Optional[dict] = None) -> dict:
    """The facade kit (pure; Milestone 13 T6): ``{"boxes", "looks", "assumed", "summary"}``. Reveals around the
    windows of the families without surrounds; gutters along the eaves edges of a pitched roof and a downpipe
    ``KIT["downpipe_end_m"]`` from each eaves edge's start corner plus one every ``downpipe_every_m``, from the eaves
    down the wall to the ground; a canopy and two wall lights at every entrance door at grade; a guard rail in front
    of an upper-floor outside door (its sill over ``guard_min_drop`` above the ground) that opens onto no balcony or
    terrace room. Every box is ``inferred`` with its reason; the summary counts per kind."""
    from wenart.blender import site as S
    from wenart.blender.shell import outward_side

    looks = looks or {}
    boxes: list[dict] = []
    assumed: list[dict] = []
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: 0.0)
    out_looks = {}
    for kind, (slug, colour, reason) in KIT_LOOKS.items():
        out_looks[kind] = looks.get(kind) or {"material": slug, "colour": colour, "source": "build", "assumed": True,
                                              "reason": reason, "inferred": True}
    # 1. reveals (modern families: no surround)
    if not rules.get("surround"):
        w_, proud = KIT["reveal_width"], KIT["reveal_proud"]
        for lv in order:
            outline = outlines.get(lv["id"])
            if len(outline or []) < 3:
                continue
            walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == lv["id"]}
            for it in opening_items(building, lv, outline, True):
                if it["type"] != "window":
                    continue
                o = next(x for x in building["openings"] if x["id"] == it["id"])
                side = outward_side(walls[o["wall_id"]], outline, it["centre"])
                if side is None:
                    continue
                ox, oy = side
                ux, uy = -oy, ox
                face = it["thickness"] / 2.0 + proud / 2.0
                cx, cy = it["centre"][0] + ox * face, it["centre"][1] + oy * face
                rot = math.degrees(math.atan2(uy, ux))
                h = it["top"] - it["bottom"]
                why = KIT_LOOKS["reveal"][2]
                boxes.append(_box("reveal", lv["id"], (cx, cy, it["top"] + w_ / 2.0), (2 * it["half"] + 2 * w_, proud, w_),
                                  rot, it["id"], why))
                for sgn in (-1.0, 1.0):
                    off = sgn * (it["half"] + w_ / 2.0)
                    boxes.append(_box("reveal", lv["id"], (cx + ux * off, cy + uy * off, (it["bottom"] + it["top"]) / 2.0),
                                      (w_, proud, h), rot, it["id"], why))
    # 2. gutters and downpipes along the eaves of a pitched roof
    edges = eaves_edges(roof_model)
    pipe_notes: list[dict] = []
    top_level = next((lv for lv in order if roof_model and lv["id"] == roof_model.get("over_level_id")), None)
    wall_outline = outlines.get(top_level["id"]) if top_level else ground_outline
    gw, gh = KIT["gutter_w"], KIT["gutter_h"]
    for e in edges:
        p, q, z, length = e["p"], e["q"], e["z"], e["length"]
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux                                      # outward (ccw outline)
        mid = G.segment_midpoint(p, q)
        rot = math.degrees(math.atan2(uy, ux))
        boxes.append(_box("gutter", top_level["id"] if top_level else None,
                          (mid[0] + nx * gw / 2.0, mid[1] + ny * gw / 2.0, z - KIT["gutter_drop"] - gh / 2.0),
                          (length + gw, gw, gh), rot, None, KIT_LOOKS["gutter"][2]))
    # 26 Oct 2026: the downpipes are planned for the whole roof (downpipe_plan: at the corners, >= 3 m apart, as
    # many as the roof area needs), no longer per run (real06: 20 pipes, two on the same spot)
    roof_area = G.polygon_area(roof_model.get("outline") or []) if roof_model and \
        len(roof_model.get("outline") or []) >= 3 else 0.0
    placed_xy: list[tuple[float, float]] = []
    served: set = set()
    for ei, t in downpipe_plan(edges, roof_area):
        e = edges[ei]
        p, q, z, length = e["p"], e["q"], e["z"], e["length"]
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux
        z1 = z - KIT["gutter_drop"] - KIT["gutter_h"]
        d = KIT["downpipe"]
        spot = pipe_spot(p, (ux, uy), (nx, ny), length, t, z1, order, outlines, wall_outline, building, gz)
        if spot is None or any(math.hypot(spot["x"] - x, spot["y"] - y) < KIT["pipe_gap_m"] for x, y in placed_xy):
            if spot is None:
                pipe_notes.append({"edge": [list(p), list(q)], "station_m": round(t, 2),
                                   "reason": "no wall face runs down to the ground near this station"})
            continue
        placed_xy.append((spot["x"], spot["y"]))
        served.add(ei)
        ex, ey = p[0] + ux * spot["t"], p[1] + uy * spot["t"]
        px, py, wn, z0 = spot["x"], spot["y"], spot["normal"], spot["z0"]
        boxes.append(_box("downpipe", top_level["id"] if top_level else None, (px, py, (z0 + z1) / 2.0), (d, d, z1 - z0),
                          math.degrees(math.atan2(wn[1], wn[0])), None, KIT_LOOKS["downpipe"][2]))
        # 24 Oct 2026: the outlet from the gutter back to the pipe on the wall (the overhang stood between them:
        # the pipe ended under the soffit, the gutter ran alone at the roof edge)
        gx, gy = ex + nx * gw / 2.0, ey + ny * gw / 2.0
        reach = math.hypot(px - gx, py - gy)
        if reach > d:
            boxes.append(_box("downpipe", top_level["id"] if top_level else None,
                              ((gx + px) / 2.0, (gy + py) / 2.0, z1 - d / 2.0), (reach + d, d, d),
                              math.degrees(math.atan2(py - gy, px - gx)), None,
                              "downpipe outlet from the gutter to the wall (not drawn)"))
    for chain in gutter_systems(edges):
        if edges and not any(i in served for i in chain):
            e = edges[chain[0]]
            pipe_notes.append({"edge": [list(e["p"]), list(e["q"])], "station_m": None,
                               "reason": "this gutter system found no wall to take a downpipe"})
    # 3. canopy and wall lights at the entrance doors at grade
    ents = []
    if len(ground_outline or []) >= 3 and terrain is not None:
        try:
            ents = S.entrances(building, levels, terrain, ground_outline, outlines)
        except (KeyError, TypeError, ValueError):
            ents = []
    openings = {o["id"]: o for o in building.get("openings") or []}
    for e in ents:
        o = openings.get(e["opening_id"])
        lv = next((x for x in levels if x["id"] == e["level_id"]), None)
        if o is None or lv is None:
            continue
        from wenart.blender.shell import opening_vertical
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, top, _ = opening_vertical(o, lv, above)
        ox, oy = e["outward"]
        ux, uy = -oy, ox
        rot = math.degrees(math.atan2(uy, ux))
        face = (e["centre"][0] + ox * e["half_t"], e["centre"][1] + oy * e["half_t"])
        depth, thick = KIT["canopy_depth"], KIT["canopy_thick"]
        boxes.append(_box("canopy", lv["id"], (face[0] + ox * depth / 2.0, face[1] + oy * depth / 2.0,
                                               top + KIT["canopy_above"] + thick / 2.0),
                          (e["width"] + 2 * KIT["canopy_side"], depth, thick), rot, e["opening_id"],
                          KIT_LOOKS["canopy"][2]))
        for sgn in (-1.0, 1.0):
            off = sgn * (e["width"] / 2.0 + KIT["light_offset"])
            boxes.append(_box("wall_light", lv["id"], (face[0] + ux * off + ox * KIT["light_d"] / 2.0,
                                                       face[1] + uy * off + oy * KIT["light_d"] / 2.0,
                                                       bottom + KIT["light_z"]),
                              (KIT["light_w"], KIT["light_d"], KIT["light_h"]), rot, e["opening_id"],
                              KIT_LOOKS["wall_light"][2]))
    # 4. guards in front of the openings over a drop (26 Oct 2026, user on real06: "are the people going to jump
    # off from it?"): every outside door, gap or window whose bottom is less than guard_sill over its floor, over a
    # drop of guard_min_drop, opening onto no balcony or terrace, and every opening the architect gave a ``guard``
    # (a French window): a guard across its whole width in the house's balustrade language (details.balustrade_kind,
    # as the stairs and balconies), reaching guard_top over the floor. Two thin bars 0.5 m apart had been "the guard".
    from wenart.blender import details as D

    guard_kind = D.balustrade_kind(style)
    rooms = [r for r in building.get("rooms") or [] if isinstance(r, dict) and len(r.get("polygon") or []) >= 3]
    for rec in (S.outer_openings(building, levels, ground_outline, outlines, kinds=("door", "window", "opening"))
                if len(ground_outline or []) >= 3 else []):
        lv, o = rec["level"], rec["opening"]
        cx, cy = rec["centre"]
        ox, oy = rec["outward"]
        floor = float(lv["elevation"])
        asked = isinstance(o.get("guard"), dict)
        if not asked and rec["bottom"] - floor >= KIT["guard_sill"]:
            continue
        drop = rec["bottom"] - gz(cx + ox * 1.0, cy + oy * 1.0)
        if drop < KIT["guard_min_drop"] and not asked:
            continue
        probe = (cx + ox * (rec["half_t"] + 0.5), cy + oy * (rec["half_t"] + 0.5))
        if any(r.get("level_id") == lv["id"] and str(r.get("room_type") or "") in ("balcony", "terrace", "loggia",
                                                                                   "roof_terrace")
               and G.point_in_polygon(probe, r["polygon"]) for r in rooms):
            continue
        top = floor + float((o.get("guard") or {}).get("top_m") or KIT["guard_top"])
        if top <= rec["bottom"] + 0.05:
            continue
        ux, uy = -oy, ox
        w = float(o.get("width") or 0.9) + 2 * KIT["guard_side"]
        off = rec["half_t"] + KIT["guard_channel"] / 2.0 + 0.01
        fx, fy = cx + ox * off, cy + oy * off
        p = (fx - ux * w / 2.0, fy - uy * w / 2.0)
        q = (fx + ux * w / 2.0, fy + uy * w / 2.0)
        boxes += guard_boxes(p, q, rec["bottom"], top, lv["id"], o["id"], guard_kind)
    counts: dict[str, int] = {}
    for b in boxes:
        counts[b["kind"]] = counts.get(b["kind"], 0) + 1
    for kind, n in sorted(counts.items()):
        assumed.append({"field": f"kit:{kind}", "value": n, "reason": KIT_LOOKS[kind][2] + " (inferred)"})
    used = {k: v for k, v in out_looks.items() if k in counts}
    return {"boxes": boxes, "looks": used, "assumed": assumed,
            "summary": {"counts": counts, "eaves_edges": len(edges), "entrances": [e["opening_id"] for e in ents],
                        "downpipes_not_placed": pipe_notes}}


PLINTH_BASE_DEPTH = 0.10        # Milestone 12: the raised base reaches this far in under the outer wall face


def plinth_rule(building: dict) -> Optional[dict]:
    """Milestone 12 (docs/milestone12.md §3.3-§3.4, track L): the plinth the pipeline wrote (``site.plinth``:
    ``top_z`` from the ``SB.`` mark or the ground floor, ``min_height``), as ``{"top_z", "min", "source"}``; None
    without one (the Milestone 11 band of ``plinth_height`` stays)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    p = site.get("plinth")
    if not isinstance(p, dict) or p.get("top_z") is None:
        return None
    floors = sorted(float(f) for f in p.get("floors") or [p["top_z"]])
    return {"top_z": float(p["top_z"]), "min": float(p.get("min_height") or 0.15), "floors": floors,
            "source": "SB. mark" if p.get("source") == "mark" else "the ground floor"}


def plinth_top(rule: dict, ground: float, flush: float = 0.05) -> float:
    """The plinth top over ground ``ground``: the lowest floor at or above it (a basement opened by a sloped site
    takes its own floor), at least ``rule["min"]`` above the ground."""
    top = min([f for f in rule.get("floors") or [] if f >= ground - flush] or [float(rule["top_z"])])
    return max(top, ground + float(rule["min"]))


def _plinth(ground_outline, cuts, gz, rule: Optional[dict] = None) -> list[dict]:
    """The plinth boxes along the ground outline. Without ``rule`` (Milestone 11): a band ``plinth_height`` above
    the ground, ``proud`` in front of the face. With it (Milestone 12): a raised base from the ground up to
    ``rule["top_z"]`` (the floor; at least ``rule["min"]`` above the ground), ``proud`` in front of the face and
    reaching ``PLINTH_BASE_DEPTH`` in under the wall, so no gap shows between the ground and a floor above it."""
    out = []
    pts = geom2d.ccw(ground_outline)
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        z = min(gz(*p), gz(*q))
        if rule is None:
            z0, z1 = z - DIMENSIONS["plinth_below"], z + DIMENSIONS["plinth_height"]
        else:
            z0, z1 = z - DIMENSIONS["plinth_below"], plinth_top(rule, z)
        length = G.distance(p, q)
        if length < DIMENSIONS["min_span"]:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux
        proud = DIMENSIONS["proud"]
        inner = PLINTH_BASE_DEPTH if rule is not None else 0.0
        for a, b in _spans(length, _edge_cuts(p, q, cuts, z0, z1), DIMENSIONS["min_span"]):
            a2 = a - proud if a <= 1e-9 else a
            b2 = b + proud if b >= length - 1e-9 else b
            mid = (a2 + b2) / 2.0
            off = (proud - inner) / 2.0                 # the box centre off the face line (out positive)
            out.append({"kind": "plinth", "level_id": None,
                        "center": [p[0] + ux * mid + nx * off, p[1] + uy * mid + ny * off, (z0 + z1) / 2.0],
                        "size": [b2 - a2, proud + inner, z1 - z0], "rotation_deg": math.degrees(math.atan2(uy, ux))})
    return out


def _surrounds(building: dict, level: dict, outline) -> list[dict]:
    """Head and jambs of a stone surround around every outside window of ``level``."""
    from wenart.blender.shell import outward_side

    w_ = DIMENSIONS["surround_width"]
    proud = DIMENSIONS["surround_proud"]
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    out = []
    for it in opening_items(building, level, outline, True):
        if it["type"] != "window":
            continue
        o = next(x for x in building["openings"] if x["id"] == it["id"])
        wall = walls[o["wall_id"]]
        side = outward_side(wall, outline, it["centre"])
        if side is None:
            continue
        ox, oy = side
        ux, uy = -oy, ox
        face = it["thickness"] / 2.0 + proud / 2.0
        cx, cy = it["centre"][0] + ox * face, it["centre"][1] + oy * face
        rot = math.degrees(math.atan2(uy, ux))
        h = it["top"] - it["bottom"]
        out.append({"kind": "surround", "level_id": level["id"], "parent": it["id"],
                    "center": [cx, cy, it["top"] + w_ / 2.0], "size": [2 * it["half"] + 2 * w_, proud, w_],
                    "rotation_deg": rot})
        for s in (-1.0, 1.0):
            off = s * (it["half"] + w_ / 2.0)
            out.append({"kind": "surround", "level_id": level["id"], "parent": it["id"],
                        "center": [cx + ux * off, cy + uy * off, (it["bottom"] + it["top"]) / 2.0],
                        "size": [w_, proud, h], "rotation_deg": rot})
    return out


def build_articulation(plan: dict, collection, make_material, manifest_objects: list, assumed: list) -> dict:
    """One mesh object per kind (``facade_plinth``, ``facade_band``, ``facade_coping``, ``facade_surround``; kind
    ``facade_detail``, status assumed) from ``articulation_plan``; returns ``{kind: boxes}`` counts."""
    from wenart.blender import common

    counts: dict[str, int] = {}
    by_kind: dict[str, list] = {}
    for b in plan["boxes"]:
        by_kind.setdefault(b["kind"], []).append(b)
    for kind, boxes in sorted(by_kind.items()):
        mat = make_material(plan["looks"][kind])
        verts, faces = geom2d.merge([geom2d.box(b["center"], b["size"], b["rotation_deg"]) for b in boxes])
        name = f"facade_{kind}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="facade_detail",
                                    status="assumed", materials=[mat])
        ob.pass_index = 0
        look = plan["looks"][kind]
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "facade_detail", "status": "assumed", "level_id": None,
            "element_id": None, "evidence": [], "material": mat.name if mat else None, "textured": False,
            "pass_index": None, "detail": kind, "boxes": len(boxes), "slug": look.get("material"),
            "colour": look.get("colour"), "assumed": {"reason": look.get("reason"), "inferred": True},
            "inferred": True, "kit": kind in KIT_KINDS,
            "parents": sorted({str(b.get("parent")) for b in boxes if b.get("parent")})[:12]})
        counts[kind] = len(boxes)
    for a in plan["assumed"]:
        assumed.append({"object": "facade", "field": a["field"], "value": a["value"], "reason": a["reason"],
                        "kind": "facade_detail", "parent": "facade"})
    return counts
