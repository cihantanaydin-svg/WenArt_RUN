"""A toy house for the exterior-view tests: one building, one corner camera, a numpy ray caster.

The house is 8 x 6 m (wall centre lines x = 0..8, y = 0..6, 20 cm walls, 2.7 m high, outer faces 10 cm
outside the centre lines) with a gable roof (eaves 2.7 m at y = -0.5 and 6.5, ridge 4.5 m at y = 3). The south
wall has two windows and a door, the east wall one window; glass and door leaves sit on the wall centre line
as the Blender build makes them. The camera (kind ``exterior``, no room, no level) looks at the south-east
corner from 16 m away with a 20 mm lens, so both facades show.

``render`` gives the index, planar depth and world-normal maps of any subset of the openings and the roof, so
a test can leave a window or the roof out of the render while the building JSON keeps it. ``write_ext_project``
lays out ``outputs/ext`` the way the M10 jobs do (scene manifest with an ``ext_1`` camera, ``renders/``,
``building_final.json``).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import vc_toy as T
from wenart import views as V

SIZE = (320, 180)
CAMERA = {"name": "ext_1", "kind": "exterior", "view": "corner", "room_id": None, "level_id": None, "index": 1,
          "position": [16.0, -10.0, 1.6], "target": [8.1, -0.1, 1.6], "lens_mm": 20.0, "sensor_mm": 36.0,
          "resolution": list(SIZE), "sides": ["south", "east"], "region_id": None, "variant": "base",
          "dropped_reason": None, "visible_openings": ["win_s1", "win_s2", "d_s1", "win_e1"],
          "visible_furniture": [], "warning": None, "shift_x": 0.0, "shift_y": 0.0}
EV = [{"file": "plan.dxf", "page": 1, "method": "vector", "confidence": 1.0}]
THICK = 0.2
HEIGHT = 2.7
# id -> (type, pass index, wall id, centre along the wall, width, sill, head)
OPENINGS = {
    "win_s1": ("window", 1, "w_s", 2.0, 1.2, 0.9, 2.1),
    "d_s1": ("door", 2, "w_s", 4.0, 0.9, 0.0, 2.1),
    "win_s2": ("window", 3, "w_s", 6.0, 1.2, 0.9, 2.1),
    "win_e1": ("window", 4, "w_e", 3.0, 1.2, 0.9, 2.1),
}
WALLS = {"w_s": ((0.0, 0.0), (8.0, 0.0)), "w_e": ((8.0, 0.0), (8.0, 6.0)),
         "w_n": ((8.0, 6.0), (0.0, 6.0)), "w_w": ((0.0, 6.0), (0.0, 0.0))}
ROOF = [[(-0.5, -0.5, 2.7), (8.5, -0.5, 2.7), (8.5, 3.0, 4.5), (-0.5, 3.0, 4.5)],
        [(8.5, 6.5, 2.7), (-0.5, 6.5, 2.7), (-0.5, 3.0, 4.5), (8.5, 3.0, 4.5)]]


def toy_building(elevations=None) -> dict:
    walls = [{"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": THICK, "exterior": True,
              "status": "verified", "evidence": EV} for wid, (a, b) in WALLS.items()]
    openings = []
    for oid, (otype, _pi, wid, along, width, sill, head) in OPENINGS.items():
        a, b = WALLS[wid]
        d = np.array(b) - np.array(a)
        d = d / np.linalg.norm(d)
        c = np.array(a) + d * along
        openings.append({"id": oid, "type": otype, "level_id": "L0", "wall_id": wid, "center": [float(c[0]), float(c[1])],
                         "width": width, "height": round(head - sill, 3), "sill_height": sill, "status": "verified",
                         "evidence": EV})
    return {
        "schema_version": "0.1", "status": "ok", "project": {"id": "ext", "source_folder": None},
        "documents": [], "levels": [{"id": "L0", "label": "Zemin", "order": 0, "elevation": 0.0,
                                     "ceiling_height": HEIGHT, "ceiling_height_source": "assumed_default"}],
        "walls": walls, "openings": openings,
        "rooms": [{"id": "r_salon", "level_id": "L0", "label": "Salon", "room_type": "living",
                   "polygon": [[0, 0], [8, 0], [8, 6], [0, 6]], "area_computed": 48.0, "status": "verified",
                   "evidence": EV}],
        "furniture": [], "decor": [], "conflicts": [], "unverified": [], "warnings": [],
        "roof": {"type": "gable", "type_source": "section", "over_level_id": "L0",
                 "eaves_height": {"value": 2.7, "method": "vector", "confidence": 1.0, "evidence": EV},
                 "ridge_height": {"value": 4.5, "method": "vector", "confidence": 1.0, "evidence": EV},
                 "planes": [{"id": f"rp_{k}", "points": [list(p) for p in plane], "slope_deg": 26.6,
                             "aspect_deg": 270.0 if k == 0 else 90.0, "source": "derived"}
                            for k, plane in enumerate(ROOF)],
                 "openings": [], "status": "verified", "evidence": EV},
        "facade": {"faces": [], "elevations": elevations or [], "evidence": []},
        "site": {"north_deg": {"value": 0.0, "method": "vector", "confidence": 1.0, "evidence": EV}},
    }


def toy_scene(building_path: str) -> dict:
    objects = []
    for oid, (otype, pi, wid, *_rest) in OPENINGS.items():
        for part in (("frame", "leaf") if otype == "door" else ("frame", "glass")):
            objects.append({"name": f"{oid}_{part}", "wenart_id": oid, "kind": otype, "status": "verified",
                            "level_id": "L0", "element_id": oid, "evidence": EV, "pass_index": pi, "wall_id": wid,
                            "room_ids": ["r_salon"]})
    roof = {"name": "roof", "wenart_id": "roof", "kind": "roof", "status": "verified", "level_id": "L0",
            "element_id": "roof", "evidence": [], "pass_index": None, "planes_source": "building",
            "planes": [{"id": f"rp_{k}", "points": [list(p) for p in plane]} for k, plane in enumerate(ROOF)],
            "z_range": [2.7, 4.5]}
    return {"schema_version": "0.1", "project": "ext", "building": building_path, "style_profile": {},
            "objects": objects + [roof], "cameras": [dict(CAMERA)], "pass_index": {},
            "variant": {"id": "base", "rooms_changed": [], "exterior_changed": False, "views": {}}}


def _quad(origin, a, b):
    return np.asarray(origin, float), np.asarray(a, float), np.asarray(b, float)


def _surfaces(drop=(), roof=True):
    """``[(origin, edge a, edge b, index, holes)]``: the outer wall faces (holes where openings cut them), the glass
    and door leaves on the centre line, the roof planes and the ground (index 0 = no indexed object)."""
    out = []
    faces = {"w_s": ((0.0, -0.1), (1.0, 0.0), 8.0), "w_e": ((8.1, 0.0), (0.0, 1.0), 6.0),
             "w_n": ((0.0, 6.1), (1.0, 0.0), 8.0), "w_w": ((-0.1, 0.0), (0.0, 1.0), 6.0)}
    for wid, ((ox, oy), (dx, dy), length) in faces.items():
        holes = []
        for oid, (_t, _pi, w, along, width, sill, head) in OPENINGS.items():
            if w == wid:
                holes.append((along - width / 2.0, along + width / 2.0, sill, head))
        out.append((np.array([ox, oy, 0.0]), np.array([dx, dy, 0.0]) * length, np.array([0.0, 0.0, HEIGHT]), 0, holes,
                    length))
    for oid, (_t, pi, wid, along, width, sill, head) in OPENINGS.items():
        if oid in drop:
            continue
        (ax, ay), (bx, by) = WALLS[wid]
        d = np.array([bx - ax, by - ay]) / np.hypot(bx - ax, by - ay)
        o = np.array([ax + d[0] * (along - width / 2.0), ay + d[1] * (along - width / 2.0), sill])
        out.append((o, np.array([d[0], d[1], 0.0]) * width, np.array([0.0, 0.0, head - sill]), pi, [], width))
    if roof:
        for plane in ROOF:
            p = np.array(plane, float)
            out.append((p[0], p[1] - p[0], p[3] - p[0], 0, [], 0.0))
    return out


def render(drop=(), roof=True, size=SIZE, camera=CAMERA):
    """``(index uint16, depth_mm uint16, normal HxWx3)`` of the house seen by ``camera``."""
    pos, f, r, u = T._basis(camera)
    W, H = size
    fpx = camera["lens_mm"] / camera["sensor_mm"] * W
    us = (np.arange(W) + 0.5 - W / 2.0) / fpx
    vs = -(np.arange(H) + 0.5 - H / 2.0) / fpx
    A, B = np.meshgrid(us, vs)
    d = (f[None, None, :] + A[..., None] * r[None, None, :] + B[..., None] * u[None, None, :]).reshape(-1, 3)
    n = len(d)
    t_best = np.full(n, np.inf)
    index = np.zeros(n, dtype=np.int64)
    normal = np.zeros((n, 3))
    with np.errstate(divide="ignore", invalid="ignore"):
        t = -pos[2] / d[:, 2]                                         # the ground z = 0
        ok = t > 1e-6
        t_best[ok] = t[ok]
        normal[ok] = (0, 0, 1)
        for origin, a, b, pi, holes, length in _surfaces(drop, roof):
            nrm = np.cross(a, b)
            nrm = nrm / np.linalg.norm(nrm)
            denom = d @ nrm
            t = ((origin - pos) @ nrm) / denom
            p = pos + t[:, None] * d - origin
            s = (p @ a) / (a @ a)
            q = (p @ b) / (b @ b)
            hit = (t > 1e-6) & (s >= 0) & (s <= 1) & (q >= 0) & (q <= 1) & (t < t_best)
            if holes and length:
                x = s * length
                z = q * (b[2] if b[2] else 1.0)
                for (x0, x1, z0, z1) in holes:
                    hit &= ~((x > x0) & (x < x1) & (z > z0) & (z < z1))
            t_best[hit] = t[hit]
            index[hit] = pi
            sign = np.where(denom[hit] > 0, -1.0, 1.0)
            normal[hit] = nrm[None, :] * sign[:, None]
    depth_m = np.where(np.isfinite(t_best), t_best * (d @ f), 0.0)       # planar depth
    depth_m[~np.isfinite(t_best)] = 0.0
    sky = ~(d[:, 2] < 0)                                                  # rays that miss the ground: sky
    depth_m = np.where(sky & (index == 0) & ~np.isfinite(t_best), 0.0, depth_m)
    return (index.reshape(H, W).astype(np.uint16), V.encode_depth_mm(depth_m.reshape(H, W)),
            normal.reshape(H, W, 3))


def write_ext_project(root: Path, *, drop=(), roof=True, elevations=None, size=SIZE) -> Path:
    """``root/outputs/ext`` with the scene manifest, ``building_final.json`` and one exterior render."""
    out = Path(root) / "outputs" / "ext"
    (out / "scene").mkdir(parents=True, exist_ok=True)
    building = toy_building(elevations)
    bpath = out / "building_final.json"
    bpath.write_text(json.dumps(building, indent=1), encoding="utf-8")
    scene = toy_scene(str(bpath))
    scene["cameras"][0]["resolution"] = list(size)
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene, indent=1), encoding="utf-8")
    index, depth, normal = render(drop, roof, size)
    entry = T.write_render(out / "renders", CAMERA["name"], index, depth, normal)
    entry.update(room_id=None, level_id=None)
    T.write_manifest(out / "renders", [entry])
    return out
