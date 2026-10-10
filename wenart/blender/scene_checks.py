"""Scene checks S1–S6 on the built Blender scene (docs/milestone12.md §4.6, §4.7, contract §13.2; owner: track S).

Contract (frozen 10 Oct 2026):

- ``CHECKS``: ``("S1", ..., "S6")``; ``TOLERANCES``: the numbers of §4.6/§4.7 (metres, degrees).
- ``run_scene_checks(building: dict, scene_objects: dict, out_path) -> dict``: runs inside Blender after the
  furniture and decor are built (``build.py`` calls it once per level); ``scene_objects``: ``{piece or decor id:
  bpy object}``; writes ``checks/scene.json`` (``out_path``) and returns ``{"violations": [Violation],
  "counts": {...}, "measured": {id: {...}}}``. A decor item that fails S5 after one re-placement is not built
  (``decor_not_rested``); a built item that fails S5 fails the build.
- ``measure_pure(meshes: dict, building: dict) -> dict``: the same measurements on plain triangle meshes (pure
  Python ray caster) for the CPU tests.

What (the checks, §4.6):

| Check | Rule | Tolerance |
|---|---|---|
| S1 | a floor piece's lowest vertex - its floor (level elevation + the room's ``floor_offset_m``) | -0.005 .. +0.010 m |
| S2 | no piece cuts a wall (the building's wall boxes) or another piece (sample points of one inside the other, ray parity; depth = shortest axis ray) | <= 0.010 m |
| S3 | the built front (``front_deg`` the builder records on the object, else the footprint's) vs the planned ``front_deg`` | <= 10 degrees |
| S4 | the built box in the piece frame vs ``wenart.furniture.sizes.real_range`` of its type | +-15 % per axis (height when the table has one) |
| S5 | decor rests on its host (``rest.measure_rest``: gap, penetration hard / soft host, support share) or on the floor | §4.7 |
| S6 | every built piece is a usable library model (``catalog.usable`` of its asset) or a by-design parametric type (``catalog.by_design_parametric``); never ``unknown`` | none |

Exceptions (documented, §4.6): wall-hung pieces (``wall_cabinet``, any ``mount_bottom_m``) skip S1 and the wall part
of S2; the members of a kitchen run (counter, island, sink, hob, fridge, wall cabinet, washing machine) may overlap
each other (the drawn sink and hob are inside the drawn counter run).

How: a mesh is ``{"verts", "faces"}`` in world coordinates plus optional fields the builder records on the
object: ``front_deg`` (built front), ``method`` (``library`` / ``parametric``), ``rest_footprint`` (the decor
item's resting footprint ``{center, size, rotation_deg}``), ``support``. ``run_scene_checks`` reads the evaluated
objects (modifiers applied) into that form and measures with Blender's BVH caster; ``measure_pure`` uses the numpy
caster of ``wenart.blender.rest``: the same code path, so the CPU tests cover the pod's checks. Output:
``{"violations": [Violation], "counts": {S1..S6: {"checked", "failed"}, "failed_build": bool}, "measured":
{id: {...}}}``; ``Violation = {check, severity, target, room_id, message, metrics}`` (the M11 format).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Optional

from wenart.blender.rest import REST_TOLERANCES

CHECKS: tuple[str, ...] = ("S1", "S2", "S3", "S4", "S5", "S6")
TOLERANCES: dict[str, float] = {"floor_gap_m": 0.010, "floor_sink_m": 0.005, "overlap_m": 0.010, "front_deg": 10.0,
                                "size_rel": 0.15, **REST_TOLERANCES}
SEVERITY: dict[str, str] = {"S1": "major", "S2": "major", "S3": "major", "S4": "minor", "S5": "critical",
                            "S6": "major"}
WALL_HUNG_TYPES: tuple[str, ...] = ("wall_cabinet",)
# Hosts that give under a cushion or a pillow (the soft tolerance of S5 applies on their seat, back or mattress).
SOFT_HOST_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bed_single",
                                    "bed_double", "bunk_bed", "crib")
SOFT_SUPPORTS: tuple[str, ...] = ("seat", "mattress", "back", "headboard")
FLOOR_DECOR: tuple[str, ...] = ("rug", "plant", "plant_large", "basket", "sculpture")
UNMEASURED_DECOR: tuple[str, ...] = ("wall_art", "mirror", "clock", "curtain", "blind", "pendant_light",
                                     "ceiling_light")
KITCHEN_RUN_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge",
                                      "wall_cabinet", "washing_machine")
MAX_PAIR_SAMPLES = 200


def _violation(check: str, target: str, room_id, message: str, metrics: dict) -> dict:
    return {"check": check, "severity": SEVERITY[check], "target": target, "room_id": room_id, "message": message,
            "metrics": metrics}


def floor_z_of(building: dict, piece: dict) -> float:
    """The floor a piece stands on: its level's elevation plus its room's ``floor_offset_m`` (Milestone 12 levels,
    track L; 0 when the room has none)."""
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == piece.get("level_id")), {})
    room = next((r for r in building.get("rooms") or [] if r.get("id") == piece.get("room_id")), {})
    offset = room.get("floor_offset_m")
    return float(level.get("elevation") or 0.0) + (float(offset) if isinstance(offset, (int, float)) else 0.0)


def wall_hung(piece: dict) -> bool:
    mb = piece.get("mount_bottom_m")
    return piece.get("type") in WALL_HUNG_TYPES or (isinstance(mb, (int, float)) and not isinstance(mb, bool)
                                                    and mb > 0)


def _bbox(verts) -> tuple[list[float], list[float]]:
    xs, ys, zs = zip(*((float(v[0]), float(v[1]), float(v[2])) for v in verts))
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def _boxes_overlap(a, b, margin: float) -> bool:
    return all(a[0][i] < b[1][i] - margin and b[0][i] < a[1][i] - margin for i in range(3))


def _angle_diff(a: float, b: float) -> float:
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def built_size(verts, footprint: dict) -> list[float]:
    """The built box ``[w, d, h]`` of a piece in its own frame (turned back by the footprint's rotation)."""
    r = math.radians(-float(footprint.get("rotation_deg") or 0.0))
    c, s = math.cos(r), math.sin(r)
    cx, cy = (float(v) for v in footprint["center"][:2])
    xs, ys, zs = [], [], []
    for v in verts:
        dx, dy = float(v[0]) - cx, float(v[1]) - cy
        xs.append(c * dx - s * dy)
        ys.append(s * dx + c * dy)
        zs.append(float(v[2]))
    return [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]


def size_failures(ftype: str, size, tol: float = TOLERANCES["size_rel"]) -> list[str]:
    """S4: the axes of a built box outside the type's real range by more than ``tol`` (``sizes.real_range``)."""
    from wenart.furniture import sizes

    real = sizes.real_range(ftype)
    if not real:
        return []
    out = []
    for axis, value, rng in (("width", size[0], real.get("width")), ("depth", size[1], real.get("depth")),
                             ("height", size[2], real.get("height"))):
        if not rng:
            continue
        lo, hi = float(rng[0]), float(rng[1])
        if value < lo / (1.0 + tol) - 1e-9 or value > hi * (1.0 + tol) + 1e-9:
            out.append(f"{axis} {value:.2f} m outside {lo:.2f}-{hi:.2f} m (+-{tol:.0%})")
    return out


def wall_boxes(building: dict, level_id: str) -> list[dict]:
    """The walls of a level as oriented boxes ``{id, a, b, thickness, z0, z1}`` (openings not cut: a piece in a
    door reveal counts as in the wall)."""
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})
    z0 = float(level.get("elevation") or 0.0)
    out = []
    for w in building.get("walls") or []:
        if w.get("level_id") != level_id or not w.get("start") or not w.get("end"):
            continue
        h = w.get("height")
        h = float(h.get("value") if isinstance(h, dict) else h) if h else float(level.get("ceiling_height") or 2.7)
        out.append({"id": w["id"], "a": tuple(map(float, w["start"][:2])), "b": tuple(map(float, w["end"][:2])),
                    "thickness": float(w.get("thickness") or 0.1), "z0": z0, "z1": z0 + h})
    return out


def depth_in_wall(point, wall: dict) -> float:
    """How far a point is inside a wall box (0 outside): the distance to the nearer long face."""
    ax, ay = wall["a"]
    bx, by = wall["b"]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9 or not wall["z0"] - 1e-9 <= point[2] <= wall["z1"] + 1e-9:
        return 0.0
    ux, uy = (bx - ax) / length, (by - ay) / length
    s = (point[0] - ax) * ux + (point[1] - ay) * uy
    n = -(point[0] - ax) * uy + (point[1] - ay) * ux
    half = wall["thickness"] / 2.0
    if not (0.0 < s < length) or abs(n) >= half:
        return 0.0
    return min(half - abs(n), s, length - s)


def usable_asset(asset: Optional[dict]) -> bool:
    from wenart.furniture import catalog as C

    return bool(asset) and C.usable(asset)


def _decor_support(item: dict, host: Optional[dict]) -> str:
    from wenart.blender import rest as R             # not wenart.furniture.decor: Blender's Python has no shapely

    return R.item_support(item, host)


def measure(meshes: dict, building: dict, caster_factory: Callable) -> dict:
    """The measurements and violations of S1-S6 for every id of ``meshes`` (the module docstring)."""
    from wenart import geometry as G
    from wenart.blender import rest as R
    from wenart.furniture import catalog as C

    tol = TOLERANCES
    pieces = {p["id"]: p for p in building.get("furniture") or []}
    decor = {d["id"]: d for d in building.get("decor") or [] if d.get("id")}
    counts = {c: {"checked": 0, "failed": 0} for c in CHECKS}
    measured: dict[str, dict] = {}
    violations: list[dict] = []
    casters: dict[str, object] = {}

    def caster(mid: str):
        if mid not in casters:
            casters[mid] = caster_factory(meshes[mid]["verts"], meshes[mid]["faces"])
        return casters[mid]

    def fail(check: str, target: str, room_id, message: str, metrics: dict) -> None:
        counts[check]["failed"] += 1
        violations.append(_violation(check, target, room_id, message, metrics))

    piece_ids = sorted(i for i in meshes if i in pieces)
    boxes = {i: _bbox(meshes[i]["verts"]) for i in piece_ids}
    walls_by_level: dict[str, list] = {}
    for pid in piece_ids:
        piece, mesh = pieces[pid], meshes[pid]
        m = measured.setdefault(pid, {"type": piece["type"]})
        room = piece.get("room_id")
        # S1 floor contact
        if not wall_hung(piece):
            counts["S1"]["checked"] += 1
            gap = boxes[pid][0][2] - floor_z_of(building, piece)
            m["floor_gap_m"] = round(gap, 4)
            if gap < -tol["floor_sink_m"] - 1e-9 or gap > tol["floor_gap_m"] + 1e-9:
                fail("S1", pid, room, f"{piece['type']} {pid}: lowest point {gap:+.3f} m from its floor "
                                      f"(allowed -{tol['floor_sink_m']} .. +{tol['floor_gap_m']} m)",
                     {"floor_gap_m": round(gap, 4)})
        # S2 walls
        if not wall_hung(piece):
            walls = walls_by_level.setdefault(piece.get("level_id"), wall_boxes(building, piece.get("level_id")))
            pts = R.sample_points(mesh["verts"], MAX_PAIR_SAMPLES)
            worst = (0.0, None)
            for w in walls:
                d = max((depth_in_wall(p, w) for p in pts), default=0.0)
                if d > worst[0]:
                    worst = (float(d), w["id"])
            counts["S2"]["checked"] += 1
            m["wall_depth_m"] = round(worst[0], 4)
            if worst[0] > tol["overlap_m"] + 1e-9:
                fail("S2", pid, room, f"{piece['type']} {pid} cuts wall {worst[1]} by {worst[0]:.3f} m",
                     {"depth_m": round(worst[0], 4), "wall_id": worst[1]})
        # S3 front
        if piece.get("front_deg") is not None:
            counts["S3"]["checked"] += 1
            built = mesh.get("front_deg")
            if built is None:
                built = G.front_direction_deg(float(piece["footprint"]["rotation_deg"]))
            diff = _angle_diff(built, piece["front_deg"])
            m["front_diff_deg"] = round(diff, 2)
            if diff > tol["front_deg"] + 1e-9:
                fail("S3", pid, room, f"{piece['type']} {pid}: built front {built:.0f} deg, planned "
                                      f"{float(piece['front_deg']):.0f} deg ({diff:.0f} deg off)",
                     {"built_front_deg": round(float(built), 2), "planned_front_deg": float(piece["front_deg"])})
        # S4 real size
        size = built_size(mesh["verts"], piece["footprint"])
        m["built_size_m"] = [round(v, 3) for v in size]
        if piece["type"] not in C.BY_DESIGN_PARAMETRIC_TYPES:
            counts["S4"]["checked"] += 1
            bad = size_failures(piece["type"], size)
            if bad:
                fail("S4", pid, room, f"{piece['type']} {pid}: {'; '.join(bad)}",
                     {"built_size_m": [round(v, 3) for v in size]})
        # S6 typed and audited, or by-design parametric
        counts["S6"]["checked"] += 1
        method = mesh.get("method") or (piece.get("asset") or {}).get("method")
        ok, why = True, ""
        if piece["type"] == "unknown":
            ok, why = False, "an untyped (unknown) piece is built"
        elif method == "library":
            if not usable_asset(piece.get("asset")):
                ok, why = False, "its library model is not usable (audit removed, or an NC/SA/ND licence)"
        elif not C.by_design_parametric(piece):
            ok, why = False, (f"a parametric {piece['type']} (parametric only for "
                              f"{', '.join(C.BY_DESIGN_PARAMETRIC_TYPES)})")
        m["s6"] = "ok" if ok else why
        if not ok:
            fail("S6", pid, room, f"{piece['type']} {pid}: {why}", {"method": method})
    # S2 between pieces
    for i, a in enumerate(piece_ids):
        for b in piece_ids[i + 1:]:
            pa, pb = pieces[a], pieces[b]
            if pa.get("level_id") != pb.get("level_id"):
                continue
            if pa["type"] in KITCHEN_RUN_TYPES and pb["type"] in KITCHEN_RUN_TYPES:
                continue
            if not _boxes_overlap(boxes[a], boxes[b], tol["overlap_m"]):
                continue
            depth = float(max(R.penetration(caster(b), R.sample_points(meshes[a]["verts"], MAX_PAIR_SAMPLES)),
                              R.penetration(caster(a), R.sample_points(meshes[b]["verts"], MAX_PAIR_SAMPLES))))
            counts["S2"]["checked"] += 1
            if depth > tol["overlap_m"] + 1e-9:
                fail("S2", a, pa.get("room_id"), f"{pa['type']} {a} and {pb['type']} {b} cut each other by "
                                                 f"{depth:.3f} m", {"depth_m": round(depth, 4), "other": b})
                measured[a].setdefault("cuts", []).append({"id": b, "depth_m": round(depth, 4)})
    # S5 decor
    for did in sorted(i for i in meshes if i in decor):
        item, mesh = decor[did], meshes[did]
        host = pieces.get(item.get("host_id")) if item.get("host_id") else None
        dtype = item.get("type")
        m = measured.setdefault(did, {"type": dtype})
        if dtype in UNMEASURED_DECOR:
            m["s5"] = "not measured (hangs on a wall or the ceiling)"
            continue
        if host is None:
            if dtype not in FLOOR_DECOR:
                m["s5"] = "not measured (no host)"
                continue
            level = next((lv for lv in building.get("levels") or [] if lv.get("id") == item.get("level_id")), {})
            room = next((r for r in building.get("rooms") or [] if r.get("id") == item.get("room_id")), {})
            off = room.get("floor_offset_m") if isinstance(room.get("floor_offset_m"), (int, float)) else 0.0
            rm = R.floor_rest(mesh["verts"], float(level.get("elevation") or 0.0) + float(off))
        else:
            host_ids = [hid for hid in (host["id"], f"{host['id']}#dressing") if hid in meshes]
            if not host_ids:
                m["s5"] = f"not measured (host {host['id']} not built)"
                continue
            host_caster = R.MultiCaster([caster(h) for h in host_ids]) if len(host_ids) > 1 else caster(host_ids[0])
            support = _decor_support(item, host)
            soft = host["type"] in SOFT_HOST_TYPES and support in SOFT_SUPPORTS
            fp = mesh.get("rest_footprint") or {"center": list(item["center"][:2]),
                                                "size": list((item.get("size") or [0.3, 0.3])[:2]),
                                                "rotation_deg": float(item.get("rotation_deg") or 0.0)}
            rm = R.measure_rest(mesh["verts"], mesh["faces"], host_caster, fp, soft)
        counts["S5"]["checked"] += 1
        ok, why = R.rest_ok(rm)
        m.update(rm)
        m["s5"] = "ok" if ok else "; ".join(why)
        if not ok:
            fail("S5", did, item.get("room_id"), f"{dtype} {did}" + (f" on {host['type']} {host['id']}" if host
                                                                       else " on the floor")
                 + f": {'; '.join(why)}", rm)
    counts["failed_build"] = counts["S5"]["failed"] > 0
    return {"violations": violations, "counts": counts, "measured": measured}


def measure_pure(meshes: dict, building: dict) -> dict:
    """``measure`` with the numpy ray caster (``rest.MeshCaster``): the CPU tests' scene checks."""
    from wenart.blender import rest as R

    return measure(meshes, building, R.MeshCaster)


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

def object_mesh(ob, depsgraph=None) -> dict:
    """World-space ``{"verts", "faces"}`` of an object's evaluated mesh (modifiers applied), plus the fields the
    builder recorded on it (``wenart_front_deg``, ``wenart_method``, ``wenart_rest_footprint``)."""
    import bpy

    depsgraph = depsgraph or bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        mw = ob.matrix_world
        verts = [tuple(mw @ v.co) for v in me.vertices]
        faces = [list(p.vertices) for p in me.polygons]
    finally:
        ev.to_mesh_clear()
    out = {"verts": verts, "faces": faces}
    if "wenart_front_deg" in ob.keys():
        out["front_deg"] = float(ob["wenart_front_deg"])
    if "wenart_method" in ob.keys():
        out["method"] = str(ob["wenart_method"])
    if "wenart_rest_footprint" in ob.keys():
        try:
            out["rest_footprint"] = json.loads(str(ob["wenart_rest_footprint"]))
        except ValueError:
            pass
    return out


def merge_meshes(meshes: list[dict]) -> dict:
    verts, faces = [], []
    out = {}
    for m in meshes:
        off = len(verts)
        verts.extend(m["verts"])
        faces.extend([[i + off for i in f] for f in m["faces"]])
        for k in ("front_deg", "method", "rest_footprint"):
            if k in m and k not in out:
                out[k] = m[k]
    out.update(verts=verts, faces=faces)
    return out


def run_scene_checks(building: dict, scene_objects: dict, out_path) -> dict:
    """S1-S6 of the objects of one level (``{piece or decor id: object or [objects]}``; a piece's bedding the build
    added is registered as ``<id>#dressing``) with Blender's BVH caster; writes the report to ``out_path``."""
    import bpy

    from wenart.blender import rest as R

    depsgraph = bpy.context.evaluated_depsgraph_get()
    meshes = {}
    for oid, obs in sorted(scene_objects.items()):
        obs = obs if isinstance(obs, (list, tuple)) else [obs]
        parts = [object_mesh(ob, depsgraph) for ob in obs if ob is not None and getattr(ob, "type", "") == "MESH"]
        parts = [p for p in parts if p["verts"] and p["faces"]]
        if parts:
            meshes[oid] = merge_meshes(parts)
    report = measure(meshes, building, R.BVHCaster)
    write_report(report, out_path)
    return report


def write_report(report: dict, out_path) -> None:
    if out_path is None:
        return
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
