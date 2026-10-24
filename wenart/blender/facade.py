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
    "default": {"main": ("render", "off white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding"},
    "modern": {"main": ("render", "off white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding"},
    "modern minimal": {"main": ("render", "white"), "base": "stone_wall_slate", "accent": "wood_cladding"},
    "minimal": {"main": ("render", "white"), "base": "stone_wall_slate", "accent": "wood_cladding"},
    "scandinavian": {"main": ("render", "white"), "base": "stone_wall_ledgestone", "accent": "wood_cladding"},
    "japandi": {"main": ("render", "off white"), "base": "stone_wall_slate", "accent": "wood_cladding"},
    "industrial": {"main": ("render", "light grey"), "base": "brick_red", "accent": None},
    "mediterranean": {"main": ("render", "cream"), "base": "stone_wall_ashlar", "accent": None},
    "classic": {"main": ("render", "ivory"), "base": "stone_wall_ashlar", "accent": None},
    "rustic": {"main": ("render", "cream"), "base": "stone_wall_rubble", "accent": "wood_cladding"},
}
ACCENT = {"margin_m": 1.0, "min_width_m": 2.4}      # the accent band: the door plus 1 m on each side, >= 2.4 m wide
DIMENSIONS = {"plinth_height": 0.45, "plinth_below": 0.05, "proud": 0.025, "band_height": 0.20, "band_proud": 0.03,
              "coping_height": 0.06, "coping_proud": 0.04, "surround_width": 0.12, "surround_proud": 0.03,
              "min_span": 0.15}


# Milestone 13 (T6): the facade kit sizes (metres) and looks (vocabulary slugs; a colour name or None).
KIT = {"reveal_width": 0.06, "reveal_proud": 0.015, "gutter_w": 0.12, "gutter_h": 0.10, "gutter_drop": 0.02,
       "downpipe": 0.10, "downpipe_every_m": 12.0, "downpipe_end_m": 0.4, "eaves_tol": 0.15,
       "canopy_depth": 1.0, "canopy_thick": 0.08, "canopy_side": 0.3, "canopy_above": 0.25,
       "light_w": 0.12, "light_d": 0.08, "light_h": 0.22, "light_z": 2.1, "light_offset": 0.35,
       "guard_height": 1.0, "guard_bar": 0.04, "guard_min_drop": 1.5, "guard_side": 0.1}
KIT_LOOKS = {
    "reveal": ("render", "white", "window reveal frame at the outer face (modern family; not drawn)"),
    "gutter": ("aluminium_anthracite", None, "gutter along the eaves (a pitched roof is drawn; the gutter is not)"),
    "downpipe": ("aluminium_anthracite", None, "downpipe at the eaves corners (not drawn)"),
    "canopy": ("render", "white", "entrance canopy over the entrance door (the door is drawn; the canopy is not)"),
    "wall_light": ("steel_black", None, "wall light beside the entrance door (not drawn)"),
    "railing": ("steel_black", None, "guard rail in front of an upper-floor outside door with no balcony (not drawn)"),
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
    return faces


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
    kit = facade_kit(building, levels, outlines, ground_outline, terrain, roof_model, rules, looks)
    boxes += kit["boxes"]
    out_looks.update(kit["looks"])
    assumed += kit["assumed"]
    return {"boxes": boxes, "looks": out_looks, "rules": rules, "assumed": assumed, "kit": kit["summary"]}


def _box(kind: str, level_id, centre, size, rot: float, parent=None, reason: str = "") -> dict:
    return {"kind": kind, "level_id": level_id, "center": [float(c) for c in centre], "size": [float(v) for v in size],
            "rotation_deg": float(rot), "inferred": True, "parent": parent, "reason": reason}


def eaves_edges(roof_model: Optional[dict]) -> list[dict]:
    """The eaves edges of a pitched roof (pure): the outline edges along which the roof's top surface stays within
    ``KIT["eaves_tol"]`` of ``eaves_z`` (a gable end rises to the ridge: no gutter there). ``[{"p", "q", "z"}]``;
    none for a flat roof or without planes."""
    if not roof_model or not roof_model.get("equations") or roof_model.get("eaves_z") is None:
        return []
    if roof_model.get("type") in ("flat", None) or roof_model.get("kind") == "flat_cut":
        return []
    from wenart.blender import roof as R

    outline = geom2d.ccw(roof_model.get("outline") or [])
    eaves = float(roof_model["eaves_z"])
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
            zs.append(R.surface_z(roof_model["equations"], x, y))
        if all(abs(z - eaves) <= KIT["eaves_tol"] for z in zs):
            out.append({"p": p, "q": q, "z": eaves, "length": length})
    return out


def facade_kit(building: dict, levels: Sequence[dict], outlines: dict, ground_outline, terrain: Optional[dict],
               roof_model: Optional[dict], rules: dict, looks: Optional[dict] = None) -> dict:
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
    top_level = next((lv for lv in order if roof_model and lv["id"] == roof_model.get("over_level_id")), None)
    wall_outline = outlines.get(top_level["id"]) if top_level else ground_outline
    for e in edges:
        p, q, z, length = e["p"], e["q"], e["z"], e["length"]
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux                                      # outward (ccw outline)
        mid = G.segment_midpoint(p, q)
        rot = math.degrees(math.atan2(uy, ux))
        gw, gh = KIT["gutter_w"], KIT["gutter_h"]
        boxes.append(_box("gutter", top_level["id"] if top_level else None,
                          (mid[0] + nx * gw / 2.0, mid[1] + ny * gw / 2.0, z - KIT["gutter_drop"] - gh / 2.0),
                          (length + gw, gw, gh), rot, None, KIT_LOOKS["gutter"][2]))
        count = 1 + int(length // KIT["downpipe_every_m"])
        for k in range(count):
            t = KIT["downpipe_end_m"] + k * KIT["downpipe_every_m"]
            if t > length - 0.2:
                break
            ex, ey = p[0] + ux * t, p[1] + uy * t
            # the wall face under the eaves edge: the nearest point of the wall outline, then the pipe outside it
            if len(wall_outline or []) >= 3:
                _d, (a, b) = geom2d.nearest_edge((ex, ey), wall_outline)
                tt = max(0.0, min(1.0, ((ex - a[0]) * (b[0] - a[0]) + (ey - a[1]) * (b[1] - a[1])) /
                                  max(1e-9, G.distance(a, b) ** 2)))
                wx, wy = a[0] + (b[0] - a[0]) * tt, a[1] + (b[1] - a[1]) * tt
                wn = G.unit_normal_left(a, b)
                wn = (-wn[0], -wn[1]) if G.point_in_polygon((wx + wn[0] * 0.2, wy + wn[1] * 0.2), wall_outline) else wn
            else:
                wx, wy, wn = ex, ey, (nx, ny)
            d = KIT["downpipe"]
            px, py = wx + wn[0] * (d / 2.0 + 0.02), wy + wn[1] * (d / 2.0 + 0.02)
            z0 = gz(px, py) + 0.1
            z1 = z - KIT["gutter_drop"] - KIT["gutter_h"]
            if z1 - z0 < 1.0:
                continue
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
    # 4. guard rails in front of upper-floor outside doors that open onto no balcony or terrace room
    rooms = [r for r in building.get("rooms") or [] if isinstance(r, dict) and len(r.get("polygon") or []) >= 3]
    for rec in (S.outer_openings(building, levels, ground_outline, outlines, kinds=("door",))
                if len(ground_outline or []) >= 3 else []):
        lv = rec["level"]
        cx, cy = rec["centre"]
        ox, oy = rec["outward"]
        drop = rec["bottom"] - gz(cx + ox * 1.0, cy + oy * 1.0)
        if drop < KIT["guard_min_drop"]:
            continue
        probe = (cx + ox * (rec["half_t"] + 0.5), cy + oy * (rec["half_t"] + 0.5))
        if any(r.get("level_id") == lv["id"] and str(r.get("room_type") or "") in ("balcony", "terrace")
               and G.point_in_polygon(probe, r["polygon"]) for r in rooms):
            continue
        ux, uy = -oy, ox
        rot = math.degrees(math.atan2(uy, ux))
        w = float(rec["opening"]["width"]) + 2 * KIT["guard_side"]
        bar = KIT["guard_bar"]
        fx, fy = cx + ox * (rec["half_t"] + bar / 2.0 + 0.02), cy + oy * (rec["half_t"] + bar / 2.0 + 0.02)
        z0 = rec["bottom"]
        why = KIT_LOOKS["railing"][2]
        boxes.append(_box("railing", lv["id"], (fx, fy, z0 + KIT["guard_height"] - bar / 2.0), (w, bar, bar), rot,
                          rec["opening"]["id"], why))
        boxes.append(_box("railing", lv["id"], (fx, fy, z0 + 0.5 * KIT["guard_height"]), (w, bar, bar), rot,
                          rec["opening"]["id"], why))
        for sgn in (-1.0, 1.0):
            off = sgn * (w / 2.0 - bar / 2.0)
            boxes.append(_box("railing", lv["id"], (fx + ux * off, fy + uy * off, z0 + KIT["guard_height"] / 2.0),
                              (bar, bar, KIT["guard_height"]), rot, rec["opening"]["id"], why))
    counts: dict[str, int] = {}
    for b in boxes:
        counts[b["kind"]] = counts.get(b["kind"], 0) + 1
    for kind, n in sorted(counts.items()):
        assumed.append({"field": f"kit:{kind}", "value": n, "reason": KIT_LOOKS[kind][2] + " (inferred)"})
    used = {k: v for k, v in out_looks.items() if k in counts}
    return {"boxes": boxes, "looks": used, "assumed": assumed,
            "summary": {"counts": counts, "eaves_edges": len(edges), "entrances": [e["opening_id"] for e in ents]}}


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
