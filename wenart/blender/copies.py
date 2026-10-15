"""Several buildings on one plot in the scene (11 Oct 2026, real04; ``building.site.buildings``,
``wenart/sheets/buildings.py``).

What: the building is modelled once (the reference copy); every other copy on the site plan is a Blender collection
instance of the building's collections (levels, slabs, roof, facade details) moved by ``p' = R(rotation_deg) p +
translate`` and raised by ``dz``. Pure helpers (``copies_of``, ``move_point``, ``move_polygon``, ``footprints``,
``site_view``, ``horizon_fraction``) run anywhere; ``place_copies`` needs ``bpy``.

Why: real04 is two identical twin-villa blocks on one sloping plot (b2 18.6 m beside b1 and 3 m higher). Modelling
the second block again would double the build time; an instance renders the same and keeps one source of truth.

How: the instanced objects keep their pass index (the index pass of an exterior view marks both blocks alike; the
copies are listed in the scene manifest ``whole_building.copies``). Room lights are not instanced (the copies'
rooms stay dark: they are only seen from outside, by daylight). The ground gets a hole for every copy's footprint
(``site.site_plan``) and the exterior camera model holds every copy as an obstacle (``exterior.build_model``).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

SITE_VIEW_PITCH_DEG = 28.0            # the cap (Milestone 13 D8: the site view pitches at most 28 degrees)
SITE_VIEW_LENS_MM = 24.0
SITE_VIEW_HORIZON_FRAC = 0.78         # the horizon line's place in the frame from the bottom (above the lower third)
SITE_VIEW_MIN_HEIGHT_M = 6.0          # the camera stands at least this high over the aim point
SENSOR_MM = 36.0
ASPECT = 9.0 / 16.0


def horizon_fraction(pitch_deg: float, lens_mm: float = SITE_VIEW_LENS_MM, sensor_mm: float = SENSOR_MM,
                     aspect: float = ASPECT) -> float:
    """Where the true horizon (elevation 0) lies in the frame of a camera pitched ``pitch_deg`` down (pure): the
    fraction of the frame height from the bottom (0.5 = the middle; over 1 = above the frame, under 0 = below).
    Milestone 12's site view (24 mm, 28 degrees down) had it at 1.13: the frame top 5 degrees under the horizon,
    a black band by construction (docs/milestone13.md §1.7, bug B9)."""
    tan_v = sensor_mm / (2.0 * lens_mm) * aspect
    return 0.5 + 0.5 * math.tan(math.radians(float(pitch_deg))) / tan_v


def pitch_for_horizon(frac: float = SITE_VIEW_HORIZON_FRAC, lens_mm: float = SITE_VIEW_LENS_MM,
                      cap_deg: float = SITE_VIEW_PITCH_DEG) -> float:
    """The downward pitch that puts the horizon at ``frac`` of the frame height (pure), at most ``cap_deg``."""
    tan_v = SENSOR_MM / (2.0 * lens_mm) * ASPECT
    pitch = math.degrees(math.atan((2.0 * float(frac) - 1.0) * tan_v))
    return round(min(float(cap_deg), max(0.0, pitch)), 3)


def copies_of(building: dict) -> list[dict]:
    """The copies other than the modelled one (``site.buildings`` with ``reference`` false)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    return [c for c in site.get("buildings") or [] if isinstance(c, dict) and not c.get("reference")]


def move_point(copy: dict, p) -> tuple[float, float]:
    a = math.radians(float(copy.get("rotation_deg") or 0.0))
    t = copy.get("translate") or (0.0, 0.0)
    x, y = float(p[0]), float(p[1])
    return (math.cos(a) * x - math.sin(a) * y + float(t[0]), math.sin(a) * x + math.cos(a) * y + float(t[1]))


def move_polygon(copy: dict, poly: Sequence) -> list[tuple[float, float]]:
    return [move_point(copy, p) for p in poly]


def footprints(building: dict) -> list[list[tuple[float, float]]]:
    """Every non-reference copy's footprint (building metres, as drawn on the site plan)."""
    return [[(float(p[0]), float(p[1])) for p in c.get("footprint") or []] for c in copies_of(building)
            if len(c.get("footprint") or []) >= 3]


def site_view(outline: Sequence, building: dict, z_range: tuple[float, float], plot: Sequence = ()) -> Optional[dict]:
    """The camera that shows every building on the plot (pure): above the plot, looking at the centre of all copies
    from the side of the modelled building's main garden (its lowest ground), far enough that every footprint
    fits ``SITE_VIEW_LENS_MM``. Milestone 13 (D8, bug B9): the pitch is the one that keeps the horizon line in the
    frame at ``SITE_VIEW_HORIZON_FRAC`` of its height (``pitch_for_horizon``; at most ``SITE_VIEW_PITCH_DEG``), the
    camera at least ``SITE_VIEW_MIN_HEIGHT_M`` over the aim point (further out when the pitch would put it lower).
    ``{"position", "target", "lens_mm", "pitch_deg", "horizon_frac", "reason"}`` or None without copies."""
    cps = copies_of(building)
    if not cps or len(outline) < 3:
        return None
    pts = [tuple(p) for p in outline] + [p for fp in footprints(building) for p in fp]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    dz = [float(c.get("dz") or 0.0) for c in cps]
    zc = (z_range[0] + z_range[1]) / 2.0 + (sum(dz) / len(dz)) / 2.0
    radius = max(math.dist((cx, cy), p) for p in pts)
    # look from the side away from the copies' mean offset turned 90 degrees: both blocks side by side in the frame
    mx = sum(float(c["translate"][0]) for c in cps) / len(cps)
    my = sum(float(c["translate"][1]) for c in cps) / len(cps)
    n = math.hypot(mx, my) or 1.0
    side = (my / n, -mx / n)
    half_fov = math.atan(SENSOR_MM / 2.0 / SITE_VIEW_LENS_MM)
    dist = (radius + 4.0) / math.tan(half_fov * 0.85)
    pitch = pitch_for_horizon(SITE_VIEW_HORIZON_FRAC, SITE_VIEW_LENS_MM)
    h = dist * math.sin(math.radians(pitch))
    if h < SITE_VIEW_MIN_HEIGHT_M:                    # keep the pitch: stand further out and higher
        h = SITE_VIEW_MIN_HEIGHT_M
        dist = h / max(math.sin(math.radians(pitch)), 1e-6)
    horiz = dist * math.cos(math.radians(pitch))
    pos = (cx + side[0] * horiz, cy + side[1] * horiz, zc + h)
    return {"position": [round(v, 4) for v in pos], "target": [round(cx, 4), round(cy, 4), round(zc, 4)],
            "lens_mm": SITE_VIEW_LENS_MM, "pitch_deg": pitch,
            "horizon_frac": round(horizon_fraction(pitch, SITE_VIEW_LENS_MM), 4),
            "reason": f"every building on the plot ({len(cps) + 1}): {dist:.1f} m from their centre, "
                      f"{pitch:g} degrees down (the horizon at {SITE_VIEW_HORIZON_FRAC:.0%} of the frame height)"}


def place_copies(building: dict, collections: Sequence, parent_collection, manifest_objects: list,
                 assumed: list) -> list[dict]:
    """One collection-instance empty per copy (bpy). ``collections``: the building's collections (levels, roof,
    facade details); they are gathered in one collection that is not linked to the scene. Returns the summary."""
    import bpy
    from mathutils import Matrix

    cps = copies_of(building)
    if not cps:
        return []
    src = bpy.data.collections.get("building_instance") or bpy.data.collections.new("building_instance")
    for col in collections:
        if col is not None and col.name not in src.children:
            src.children.link(col)
    out = []
    for c in cps:
        name = f"building_copy_{c['id']}"
        ob = bpy.data.objects.new(name, None)
        ob.instance_type = "COLLECTION"
        ob.instance_collection = src
        t = c.get("translate") or (0.0, 0.0)
        ob.matrix_world = (Matrix.Translation((float(t[0]), float(t[1]), float(c.get("dz") or 0.0)))
                           @ Matrix.Rotation(math.radians(float(c.get("rotation_deg") or 0.0)), 4, "Z"))
        ob["wenart_id"] = c["id"]
        ob["wenart_kind"] = "building_copy"
        parent_collection.objects.link(ob)
        ev = [e for e in c.get("evidence") or [] if isinstance(e, dict)]
        manifest_objects.append({"name": name, "wenart_id": c["id"], "kind": "building_copy", "status": "verified"
                                 if c.get("orientation") == "entrances" else "assumed", "level_id": None,
                                 "element_id": c["id"], "evidence": ev, "material": None, "textured": False,
                                 "pass_index": None, "assumed": {} if c.get("orientation") == "entrances" else
                                 {"orientation": "ambiguous (180 degrees)"},
                                 "rotation_deg": c.get("rotation_deg"), "translate": list(t), "dz": c.get("dz")})
        if c.get("orientation") != "entrances":
            assumed.append({"object": name, "field": "orientation", "value": c.get("rotation_deg"),
                            "reason": c.get("note") or "orientation ambiguous"})
        if c.get("dz_note"):
            assumed.append({"object": name, "field": "dz", "value": c.get("dz"), "reason": c["dz_note"]})
        out.append({"id": c["id"], "object": name, "rotation_deg": c.get("rotation_deg"), "translate": list(t),
                    "dz": c.get("dz"), "orientation": c.get("orientation"),
                    "collections": [col.name for col in collections if col is not None]})
    return out
