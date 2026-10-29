"""Exposed timber beams under a sloped ceiling (29 Oct 2026; lessons UL113, UL115: the user's reference photos, "also
take some inspiration from these photos", "look at all these details I want these details";
docs/reference_details_20261029.md G2: "exposed timber beams under a sloped ceiling").

What (``plan_beams`` pure; ``build_ceiling_beams`` bpy, called by the build after the feature walls):

- the families that show their rafters (``BEAM_FAMILIES``: rustic, Scandinavian, farmhouse homes; the brief's
  ``ceiling_beams`` false turns it off, true asks it in any family) and the rooms under the roof's slope
  (``level["ceiling_planes"]``: the planes z = a x + b y + c the build cuts the ceiling with, under the flat
  ceiling; ``BEAM_ROOM_TYPES``);
- per sloped plane of a room: rafters along its fall line every ``PITCH_M`` across it (centred), each a timber
  ``WIDTH_M`` x ``DEPTH_M`` whose top follows the slope (``OVERLAP_M`` into the ceiling: no gap), only where that
  plane is the room's ceiling (the lowest of the planes, below the flat ceiling), inside the room by ``EDGE_M``, never
  over a tall piece that comes within the beam's depth of the slope or a light fixed to the slope (``LIGHT_CLEAR_M``);
- one mesh per room (``ceiling_beams_<room>``, kind ``ceiling``, detail ``beams``: hidden in the top-down views like
  the ceiling), in the house's timber (``shell.stair_timber_slot``), recorded as assumed (not drawn).
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

BEAM_FAMILIES: tuple[str, ...] = ("rustic", "scandinavian", "farmhouse")
BEAM_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom", "dining", "kitchen", "hall", "other", "unknown")
PITCH_M = 0.60                  # rafters 60 cm apart (centre to centre)
WIDTH_M = 0.08
DEPTH_M = 0.14
OVERLAP_M = 0.01                # the beam's top this far up into the ceiling
STEP_M = 0.05                   # the sampling step along a rafter
EDGE_M = 0.06                   # off the room's walls
MIN_RUN_M = 0.6                 # a rafter run shorter than this is left out
SLOPE_MIN = 0.08                # a plane steeper than this (rise per metre) is a slope
FLAT_GAP_M = 0.03               # a plane counts where it is this far under the flat ceiling
LIGHT_CLEAR_M = 0.25
CHECK = "UL113"


def _family(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def beams_wanted(style: Optional[dict]) -> tuple[bool, str]:
    flag = (style or {}).get("ceiling_beams")
    if flag in (False, "off", "none"):
        return False, "the brief turns the ceiling beams off"
    if flag in (True, "on", "yes"):
        return True, "the brief asks for exposed ceiling beams"
    fam = _family(style)
    if fam in BEAM_FAMILIES:
        return True, f"assumed: a {fam} home shows the rafters of its sloped ceilings (G2)"
    return False, f"a {fam or 'house'} home keeps its sloped ceilings plain"


def _z(plane, x: float, y: float) -> float:
    return float(plane[0]) * x + float(plane[1]) * y + float(plane[2])


def _inside(poly, p) -> bool:
    return G.point_in_polygon(p, poly)


def _edge_dist(poly, p) -> float:
    return min(G.point_segment_distance(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def _blocked(p, z_ceiling: float, tall: list, lights: list) -> bool:
    for corners, top in tall:
        if top > z_ceiling - DEPTH_M - 0.02 and G.point_in_polygon(p, corners):
            return True
    return any(G.distance(p, c) < LIGHT_CLEAR_M for c in lights)


def plan_beams(building: dict, level: dict, style: Optional[dict]) -> tuple[list[dict], list[str]]:
    """``(plans, notes)``: per room under the slope ``{"room_id", "beams": [{"plane", "p0", "p1", "z0", "z1"}],
    "reason"}`` (``p0`` / ``p1`` the run's ends in plan, ``z0`` / ``z1`` the slope there, world z)."""
    ok, why = beams_wanted(style)
    planes = [tuple(float(v) for v in p[:3]) for p in level.get("ceiling_planes") or [] if len(p) >= 3]
    if not ok or not planes:
        return [], ([why] if planes else [])
    flat = float(level["elevation"]) + float(level.get("ceiling_height") or 2.7)
    from wenart.blender import parametric as P

    out, notes = [], []
    for room in sorted((r for r in building.get("rooms") or [] if r.get("level_id") == level["id"]
                        and r.get("room_type") in BEAM_ROOM_TYPES and len(r.get("polygon") or []) >= 3),
                       key=lambda r: str(r["id"])):
        poly = [tuple(float(v) for v in p[:2]) for p in room["polygon"]]
        floor = float(level["elevation"]) + float(room.get("floor_offset_m") or 0.0)
        tall = []
        for f in building.get("furniture") or []:
            if f.get("room_id") != room["id"] or not f.get("footprint") or f.get("build", True) is False:
                continue
            fp = f["footprint"]
            corners = [tuple(c) for c in G.rotated_rectangle(fp["center"], fp["size"][:2],
                                                             float(fp.get("rotation_deg") or 0.0))]
            try:
                top = floor + float(P.piece_bbox(f)[2])
            except (KeyError, TypeError, ValueError):
                top = floor + 1.0
            tall.append((corners, top))
        lights = [tuple(float(v) for v in d["center"][:2]) for d in building.get("decor") or []
                  if d.get("room_id") == room["id"] and d.get("type") in ("ceiling_light", "pendant_light")
                  and d.get("center")]
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        reach = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2.0 + PITCH_M
        beams = []
        for k, pl in enumerate(planes):
            slope = math.hypot(pl[0], pl[1])
            if slope < SLOPE_MIN:
                continue
            g = (-pl[0] / slope, -pl[1] / slope)          # downhill
            t = (-g[1], g[0])                              # along the contours
            n_off = int(reach / PITCH_M) + 1
            for j in range(-n_off, n_off + 1):
                o = (cx + t[0] * j * PITCH_M, cy + t[1] * j * PITCH_M)
                run: list = []
                steps = int(2.0 * reach / STEP_M) + 1
                for i in range(steps + 1):
                    s = -reach + i * STEP_M
                    p = (o[0] + g[0] * s, o[1] + g[1] * s)
                    zc = _z(pl, *p)
                    here = (_inside(poly, p) and _edge_dist(poly, p) >= EDGE_M + WIDTH_M / 2.0
                            and zc < flat - FLAT_GAP_M and all(zc <= _z(q, *p) + 1e-6 for q in planes)
                            and not _blocked(p, zc, tall, lights))
                    if here:
                        run.append(p)
                    if (not here or i == steps) and run:
                        if G.distance(run[0], run[-1]) >= MIN_RUN_M - 1e-9:
                            beams.append({"plane": k, "p0": [round(run[0][0], 4), round(run[0][1], 4)],
                                          "p1": [round(run[-1][0], 4), round(run[-1][1], 4)],
                                          "z0": round(_z(pl, *run[0]), 4), "z1": round(_z(pl, *run[-1]), 4)})
                        run = []
        if beams:
            out.append({"room_id": room["id"], "level_id": level["id"], "beams": beams,
                        "reason": f"{len(beams)} exposed rafters {WIDTH_M * 100:.0f} x {DEPTH_M * 100:.0f} cm every "
                                  f"{PITCH_M * 100:.0f} cm under the sloped ceiling of {room['id']} ({why})"})
    return out, notes


def beam_mesh(beam: dict, plane) -> tuple[list, list]:
    """``(verts, faces)`` of one rafter (pure): a prism along its run whose top follows the plane (``OVERLAP_M`` into
    it), ``DEPTH_M`` deep under it, ``WIDTH_M`` wide; outward faces."""
    (x0, y0), (x1, y1) = beam["p0"], beam["p1"]
    L = math.hypot(x1 - x0, y1 - y0) or 1e-9
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy * WIDTH_M / 2.0, ux * WIDTH_M / 2.0
    verts = []
    for (x, y) in ((x0, y0), (x1, y1)):
        for sx in (-1.0, 1.0):
            px, py = x + sx * nx, y + sx * ny
            zt = _z(plane, px, py) + OVERLAP_M
            verts.append((px, py, zt - OVERLAP_M - DEPTH_M))
            verts.append((px, py, zt))
    # 0 a-left-bottom 1 a-left-top 2 a-right-bottom 3 a-right-top 4 b-left-bottom 5 b-left-top 6 b-right-bottom 7 ...
    faces = [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [1, 3, 7, 5], [0, 4, 6, 2]]
    # orient outwards (the order above depends on the run's direction): flip any face whose normal points inwards
    cx = sum(v[0] for v in verts) / 8.0
    cy = sum(v[1] for v in verts) / 8.0
    cz = sum(v[2] for v in verts) / 8.0
    out = []
    for f in faces:
        a, b, c = (verts[i] for i in f[:3])
        n = ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
             (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
             (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        fc = [sum(verts[i][k] for i in f) / 4.0 for k in range(3)]
        if n[0] * (fc[0] - cx) + n[1] * (fc[1] - cy) + n[2] * (fc[2] - cz) < 0:
            f = list(reversed(f))
        out.append(f)
    return verts, out


def room_mesh(plan: dict, planes: list) -> tuple[list, list]:
    """One mesh of a room's rafters (pure)."""
    verts, faces = [], []
    for b in plan["beams"]:
        v, f = beam_mesh(b, planes[b["plane"]])
        off = len(verts)
        verts += v
        faces += [[i + off for i in face] for face in f]
    return verts, faces


def build_ceiling_beams(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                        assumed: list, warnings: list) -> list[dict]:
    """Build the level's rafters (module docstring; bpy). Returns the plans built."""
    from wenart.blender import common, shell

    plans, notes = plan_beams(building, level, style)
    if not plans:
        return []
    planes = [tuple(float(v) for v in p[:3]) for p in level.get("ceiling_planes") or []]
    timber = shell.slot_material(library, shell.stair_timber_slot(style))
    built = []
    for plan in plans:
        verts, faces = room_mesh(plan, planes)
        if not faces:
            continue
        name = f"ceiling_beams_{plan['room_id']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="ceiling",
                                    status="assumed", materials=[timber], face_material_indices=[0] * len(faces))
        bevel = ob.modifiers.new(name="bevel", type="BEVEL")
        bevel.width = 0.004
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "ceiling", "status": "assumed", "level_id": level["id"],
            "element_id": plan["room_id"], "parent": plan["room_id"], "room_id": plan["room_id"], "evidence": [],
            "material": timber.name, "textured": library.textured(timber), "pass_index": None, "detail": "beams",
            "beams": {"count": len(plan["beams"]), "pitch_m": PITCH_M, "size_m": [WIDTH_M, DEPTH_M]},
            "assumed": {"detail": "beams", "reason": plan["reason"]}})
        assumed.append({"object": ob.name, "field": "ceiling_beams", "value": len(plan["beams"]),
                        "reason": plan["reason"], "parent": plan["room_id"], "kind": "ceiling_beams"})
        built.append(plan)
    warnings.extend(f"ceiling beams: {n}" for n in notes if n.startswith("the brief"))
    return built
