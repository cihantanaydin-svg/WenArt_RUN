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
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# Per style family: the plinth look and height, whether the windows get surrounds (else reveals).
ARTICULATION = {
    "default": {"plinth": "concrete_exposed", "plinth_colour": None, "surround": None},
    "classic": {"plinth": "stone_cladding", "plinth_colour": None, "surround": "limestone"},
    "mediterranean": {"plinth": "stone_cladding", "plinth_colour": None, "surround": "limestone"},
    "rustic": {"plinth": "stone_wall_rubble", "plinth_colour": None, "surround": "limestone"},
}
DIMENSIONS = {"plinth_height": 0.45, "plinth_below": 0.05, "proud": 0.025, "band_height": 0.20, "band_proud": 0.03,
              "coping_height": 0.06, "coping_proud": 0.04, "surround_width": 0.12, "surround_proud": 0.03,
              "min_span": 0.15}


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
        boxes += _plinth(ground_outline, cuts, gz)     # one ground height per edge: its lower end
        assumed.append({"field": "plinth", "value": DIMENSIONS["plinth_height"], "reason": out_looks["plinth"]["reason"]})
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
            z = float(roof_model["eaves_z"])
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
    return {"boxes": boxes, "looks": out_looks, "rules": rules, "assumed": assumed}


def _plinth(ground_outline, cuts, gz) -> list[dict]:
    out = []
    pts = geom2d.ccw(ground_outline)
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        z = min(gz(*p), gz(*q))
        z0, z1 = z - DIMENSIONS["plinth_below"], z + DIMENSIONS["plinth_height"]
        length = G.distance(p, q)
        if length < DIMENSIONS["min_span"]:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = uy, -ux
        proud = DIMENSIONS["proud"]
        for a, b in _spans(length, _edge_cuts(p, q, cuts, z0, z1), DIMENSIONS["min_span"]):
            a2 = a - proud if a <= 1e-9 else a
            b2 = b + proud if b >= length - 1e-9 else b
            mid = (a2 + b2) / 2.0
            out.append({"kind": "plinth", "level_id": None,
                        "center": [p[0] + ux * mid + nx * proud / 2.0, p[1] + uy * mid + ny * proud / 2.0,
                                   (z0 + z1) / 2.0],
                        "size": [b2 - a2, proud, z1 - z0], "rotation_deg": math.degrees(math.atan2(uy, ux))})
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
            "colour": look.get("colour"), "assumed": {"reason": look.get("reason"), "inferred": True}})
        counts[kind] = len(boxes)
    for a in plan["assumed"]:
        assumed.append({"object": "facade", "field": a["field"], "value": a["value"], "reason": a["reason"],
                        "kind": "facade_detail", "parent": "facade"})
    return counts
