"""CPU tests of the camera search (wenart.blender.camsearch, docs/milestone6.md §4.1).

The ray caster is checked against an independent brute-force caster of an
axis-aligned room (every label and depth of the 64 x 36 grid), the score
against hand-computed values of the §4.1 formula, then the candidate grid,
the blocked rule, the view-count and diversity rules, determinism, the plan
fields, the searched views of the synthetic projects (better than the M5
rules by the model, never blocked without the warning), the search time on
synthetic-03 (<= 60 s) and that the M5 policy still reproduces every
committed M5 camera (``git show a2adcef``) within 1 mm. No Blender needed
(one test runs the search inside Blender's Python when it is installed).
"""
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

import jsonschema
import numpy as np
import pytest

from wenart import geometry as G
from wenart.blender import cameras, camsearch as C, cli, geom2d, schemas
from wenart.blender.parametric import obstacle_rect

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
RESULTS = ROOT / "results"
M5_COMMIT = "a2adcef"
BLENDER = cli.find_blender()


# --------------------------------------------------------------------------
# Hand-made rooms
# --------------------------------------------------------------------------

def _building(width: float = 5.0, depth: float = 4.0, ceiling: float = 2.6, openings=(), furniture=(),
              polygon=None, thickness: float = 0.2) -> dict:
    """One room whose inner faces are x in [0, width], y in [0, depth] (or ``polygon``); wall centre
    lines ``thickness / 2`` outside. ``openings``: (id, type, wall s/e/n/w, centre along the wall,
    width, sill, height); ``furniture``: (id, type, centre, footprint size, rotation, library bbox)."""
    t, h = thickness, thickness / 2.0
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-t, -h], "end": [width + t, -h], "thickness": t},
        {"id": "w_e", "level_id": "L0", "start": [width + h, -t], "end": [width + h, depth + t], "thickness": t},
        {"id": "w_n", "level_id": "L0", "start": [width + t, depth + h], "end": [-t, depth + h], "thickness": t},
        {"id": "w_w", "level_id": "L0", "start": [-h, depth + t], "end": [-h, -t], "thickness": t},
    ]
    where = {"s": lambda a: [a, -h], "e": lambda a: [width + h, a], "n": lambda a: [a, depth + h],
             "w": lambda a: [-h, a]}
    ops = [{"id": oid, "level_id": "L0", "type": otype, "wall_id": f"w_{wall}", "center": where[wall](along),
            "width": w, "sill_height": sill, "height": height}
           for oid, otype, wall, along, w, sill, height in openings]
    pieces = [{"id": fid, "type": ftype, "room_id": "r", "level_id": "L0", "front_deg": 0.0,
               "footprint": {"center": list(c), "size": list(s), "rotation_deg": rot},
               "asset": {"method": "library", "bbox_m": list(bbox)}}
              for fid, ftype, c, s, rot, bbox in furniture]
    poly = polygon or [[0, 0], [width, 0], [width, depth], [0, depth]]
    return {"project": {"id": "hand"}, "status": "ok",
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": ceiling}],
            "walls": walls, "openings": ops,
            "rooms": [{"id": "r", "level_id": "L0", "label": "Oda", "room_type": "bedroom", "polygon": poly}],
            "furniture": pieces}


ROOM_A = dict(
    openings=[("win", "window", "s", 2.5, 1.6, 0.9, 1.2), ("door", "door", "e", 1.0, 0.9, 0.0, 2.1)],
    furniture=[("bed", "bed_double", (1.5, 2.9), (1.6, 2.0), 0.0, (1.6, 2.0, 0.6)),
               ("ward", "wardrobe", (4.6, 3.0), (1.2, 0.6), 90.0, (1.2, 0.6, 2.1))],
)


def _brute_force(building: dict, position, yaw_deg: float, shift_y: float, grid=(64, 36)):
    """Labels (names) and planar depths of an axis-aligned room, ray by ray in plain Python.

    Independent of camsearch: the room is the box of its rectangular polygon (exit plane of the box),
    openings are rectangles on those planes, pieces are world-axis boxes (rotation 0 or 90 only)."""
    (x0, y0), (x1, y1) = building["rooms"][0]["polygon"][0], building["rooms"][0]["polygon"][2]
    z0 = building["levels"][0]["elevation"]
    z1 = z0 + building["levels"][0]["ceiling_height"]
    plane_of = {"w_s": ("y", y0), "w_n": ("y", y1), "w_w": ("x", x0), "w_e": ("x", x1)}
    rects = []
    for o in building["openings"]:
        axis, value = plane_of[o["wall_id"]]
        along = o["center"][0] if axis == "y" else o["center"][1]
        rects.append((axis, value, along - o["width"] / 2, along + o["width"] / 2, o["sill_height"],
                      o["sill_height"] + o["height"], o["id"]))
    boxes = []
    for f in building["furniture"]:
        w, d, h = f["asset"]["bbox_m"]
        if abs(f["footprint"]["rotation_deg"] % 180 - 90) < 1e-9:
            w, d = d, w
        cx, cy = f["footprint"]["center"]
        boxes.append(((cx - w / 2, cy - d / 2, z0), (cx + w / 2, cy + d / 2, z0 + h), f["id"]))
    W, H = 1920.0, 1080.0
    fpx = 24.0 / 36.0 * W
    yaw = math.radians(yaw_deg)
    fwd, right = (math.cos(yaw), math.sin(yaw), 0.0), (math.sin(yaw), -math.cos(yaw), 0.0)
    names, depths = [], []
    ox, oy, oz = position
    for j in range(grid[1]):
        for i in range(grid[0]):
            a = ((i + 0.5) * W / grid[0] - W / 2) / fpx
            b = -((j + 0.5) * H / grid[1] - H / 2 - shift_y * W) / fpx
            d = (fwd[0] + a * right[0], fwd[1] + a * right[1], b)
            best = (math.inf, None)
            for axis, k, lo, hi in (("x", 0, x0, x1), ("y", 1, y0, y1), ("z", 2, z0, z1)):
                if d[k] > 0:
                    tt, value = (hi - position[k]) / d[k], hi
                elif d[k] < 0:
                    tt, value = (lo - position[k]) / d[k], lo
                else:
                    continue
                if tt < best[0]:
                    best = (tt, (axis, value))
            tt, (axis, value) = best
            p = (ox + tt * d[0], oy + tt * d[1], oz + tt * d[2])
            if axis == "z":
                name = "floor" if value == z0 else "ceiling"
            else:
                name = "wall"
                for r_axis, r_value, lo, hi, zlo, zhi, oid in rects:
                    along = p[1] if r_axis == "x" else p[0]
                    if r_axis == axis and r_value == value and lo <= along <= hi and zlo <= p[2] <= zhi:
                        name = oid
            for lo3, hi3, fid in boxes:
                tn, tf = -math.inf, math.inf
                for k in range(3):
                    if d[k] == 0:
                        if not lo3[k] <= position[k] <= hi3[k]:
                            tn, tf = math.inf, -math.inf
                        continue
                    ta, tb = (lo3[k] - position[k]) / d[k], (hi3[k] - position[k]) / d[k]
                    tn, tf = max(tn, min(ta, tb)), min(tf, max(ta, tb))
                if tn <= tf and tn > 1e-4 and tn < tt:
                    tt, name = tn, fid
            names.append(name)
            depths.append(tt)
    return names, np.array(depths)


def _model_names(model: C.RoomModel, labels: np.ndarray) -> list[str]:
    fixed = {C.FLOOR: "floor", C.CEILING: "ceiling", C.WALL: "wall", C.OPENING: "opening", C.NOTHING: "nothing"}
    return [fixed.get(int(v)) or model.elements[int(v) - C.FIRST_ELEMENT]["id"] for v in labels]


def _cast(building, position, yaw, shift_y=C.SHIFT_Y, grid=(64, 36)):
    model = C.RoomModel(building["rooms"][0], building)
    a, b = C.ray_grid(grid, shift_y=shift_y)
    labels, depth = model.cast(position, C.yaw_directions([yaw], a, b))
    return model, labels[0], depth[0]


# --------------------------------------------------------------------------
# Ray caster vs brute force
# --------------------------------------------------------------------------

@pytest.mark.parametrize("yaw", [0, 90, 150, 270, 300])
@pytest.mark.parametrize("shift_y", [0.0, -0.10])
def test_ray_caster_matches_a_brute_force_caster(yaw, shift_y):
    building = _building(**ROOM_A)
    position = (2.5, 1.5, 1.25)
    model, labels, depth = _cast(building, position, yaw, shift_y)
    names, ref_depth = _brute_force(building, position, yaw, shift_y)
    got = _model_names(model, labels)
    assert got == names
    assert np.allclose(depth, ref_depth, rtol=1e-9, atol=1e-9)


def test_ray_caster_sees_every_kind_of_label():
    building = _building(**ROOM_A)
    seen = set()
    for yaw in (0, 90, 270):
        model, labels, _ = _cast(building, (2.5, 1.5, 1.25), yaw)
        seen |= set(_model_names(model, labels))
    model, labels, _ = _cast(building, (4.4, 0.6, 1.25), 150, shift_y=0.0)     # the far corner: ceiling
    seen |= set(_model_names(model, labels))
    assert {"floor", "ceiling", "wall", "win", "door", "bed", "ward"} <= seen


def test_plain_openings_are_neither_wall_nor_element():
    building = _building(openings=[("arch", "opening", "n", 2.5, 1.5, 0.0, 2.2)])
    model, labels, _ = _cast(building, (2.5, 1.0, 1.25), 90)
    assert C.OPENING in labels and model.elements == []
    m = model.measure(labels[None, :], np.where(labels == labels, 3.0, 3.0)[None, :], C.border_mask())[0]
    assert m["open"] == 0.0 and m["max_single"] == 0.0


def test_camera_directions_equal_the_yaw_directions_for_pitch_zero():
    a, b = C.ray_grid(shift_y=-0.1)
    for yaw in (0, 30, 135, 270):
        pos = (1.0, 2.0, 1.25)
        tgt = (1.0 + math.cos(math.radians(yaw)), 2.0 + math.sin(math.radians(yaw)), 1.25)
        assert np.allclose(C.camera_directions(pos, tgt, a, b), C.yaw_directions([yaw], a, b)[0], atol=1e-12)


def test_ray_grid_follows_the_shift_formula_of_the_spec():
    a, b = C.ray_grid((4, 2), shift_x=0.05, shift_y=-0.10)
    fpx = 24.0 / 36.0 * 1920
    cols = (np.arange(4) + 0.5) * 1920 / 4
    rows = (np.arange(2) + 0.5) * 1080 / 2
    assert np.allclose(a.reshape(2, 4)[0], (cols - 960 + 0.05 * 1920) / fpx)
    assert np.allclose(b.reshape(2, 4)[:, 0], -(rows - 540 + 0.10 * 1920) / fpx)
    border = C.border_mask((4, 3)).reshape(3, 4)
    assert border.sum() == 10 and not border[1, 1] and not border[1, 2]


# --------------------------------------------------------------------------
# Score (§4.1 formula)
# --------------------------------------------------------------------------

def test_score_table_holds_the_spec_constants():
    w = C.SCORE["type_weight"]
    for t in ("bed", "bed_double", "bed_single", "sofa", "kitchen_counter", "kitchen_island"):
        assert w[t] == 3.0
    assert w["bathtub"] == 2.5
    for t in ("table_dining", "desk", "toilet", "washbasin", "shower", "sink_kitchen"):
        assert w[t] == 2.0
    for t in ("wardrobe", "armchair", "stove", "tv_unit", "table_coffee"):
        assert w[t] == 1.5
    assert w["chair"] == 0.8 and C.type_weight("nightstand") == 1.0 and C.type_weight(None) == 1.0
    assert C.SCORE["penalties"] == {"near": (3.0, 0.08), "max_single": (3.0, 0.40), "wall": (2.0, 0.55),
                                    "window": (2.0, 0.20), "ceiling": (1.0, 0.15)}
    assert (C.SCORE["grid"], C.SCORE["near_m"], C.SCORE["blocked_near"], C.SCORE["blocked_single"]) == \
        ((64, 36), 0.9, 0.30, 0.50)
    assert (C.CAMERA_HEIGHT, C.SHIFT_X, C.SHIFT_Y, C.LENS_MM, C.GRID_STEP, C.YAW_STEP_DEG) == \
        (1.25, 0.0, -0.10, 24.0, 0.5, 30)


def test_furniture_share_by_hand():
    # bed 0.5 of the rays (capped at 0.25), a nightstand cut by the border (x 0.6), a chair 0.05.
    furn = C.furniture_share([0.5, 0.1, 0.05], [False, True, False], [3.0, 1.0, 0.8])
    assert furn == pytest.approx((3.0 * 1.0 + 1.0 * 0.4 * 0.6 + 0.8 * 0.2) / 4.8)
    assert C.furniture_share([], [], []) == 0.0
    # A piece the camera does not see still counts in the denominator.
    assert C.furniture_share([0.25, 0.0], [False, False], [3.0, 3.0]) == pytest.approx(0.5)


def test_score_terms_by_hand():
    m = {"furn": 0.5, "open": 0.06, "floor": 0.30, "wall": 0.65, "window": 0.25, "ceiling": 0.20, "near": 0.10,
         "max_single": 0.45, "d_wall": 1.5}
    s = C.score_terms(m)
    assert s["furniture"] == pytest.approx(2.0) and s["openings"] == pytest.approx(0.5)
    assert s["floor"] == pytest.approx(1.0) and s["depth"] == pytest.approx(0.5)
    assert s["penalties"] == pytest.approx(3 * 0.02 + 3 * 0.05 + 2 * 0.10 + 2 * 0.05 + 1 * 0.05)
    assert s["total"] == pytest.approx(4.0 - 0.56) and s["blocked"] is False
    assert C.score_terms(dict(m, near=0.31))["blocked"] and C.score_terms(dict(m, max_single=0.51))["blocked"]
    assert not C.score_terms(dict(m, near=0.30, max_single=0.50))["blocked"]
    assert C.score_terms(dict(m, d_wall=9.0))["depth"] == 1.0


def test_score_of_a_bare_wall_by_hand():
    # From the centre of an empty 4 x 4 room looking east (no shift): every ray hits the east wall
    # 2 m away (lateral reach 0.75 x 2 < 2 m, vertical 1.25 +- 0.42 x 2 inside 0 .. 2.6 m).
    building = _building(4.0, 4.0)
    plan = {"room_id": "r", "position": [2.0, 2.0, 1.25], "target": [3.0, 2.0, 1.25]}
    out = C.score_camera(building, plan)
    m, s = out["shares"], out["terms"]
    assert m["wall"] == 1.0 and m["floor"] == m["ceiling"] == m["near"] == 0.0 and m["d_wall"] == pytest.approx(2.0)
    assert s["total"] == pytest.approx(2.0 / 3.0 - 2.0 * 0.45)


def test_score_of_a_window_wall_by_hand():
    # Same camera, a 2.0 m window (sill 0.9, top 2.1) centred on the east wall: |a| <= 0.5 holds for
    # columns 11..52 (42 of 64), z >= 0.9 at 2 m for rows 0..24 (25 of 36): 1050 / 2304 rays.
    building = _building(4.0, 4.0, openings=[("win", "window", "e", 2.0, 2.0, 0.9, 1.2)])
    plan = {"room_id": "r", "position": [2.0, 2.0, 1.25], "target": [3.0, 2.0, 1.25]}
    out = C.score_camera(building, plan)
    m, s = out["shares"], out["terms"]
    share = 1050 / 2304
    assert m["window"] == pytest.approx(share) and m["open"] == pytest.approx(share)
    assert m["max_single"] == pytest.approx(share) and m["wall"] == pytest.approx(1 - share)
    assert s["openings"] == 1.0 and s["penalties"] == pytest.approx(2 * (share - 0.2) + 3 * (share - 0.4))
    assert s["total"] == pytest.approx(1.0 + 2.0 / 3.0 - 2 * (share - 0.2) - 3 * (share - 0.4))


def test_border_pieces_count_less_and_near_rays_are_planar_depth():
    # A low bed 2.5 m ahead: the lowest rays (slope -0.56) reach the floor at 1.25 / 0.56 = 2.23 m, in
    # front of it, so the bed is inside the frame; 0.9 m ahead it fills the bottom rows (cut).
    building = _building(4.0, 4.0, furniture=[("bed", "bed", (2.0, 3.4), (1.0, 1.0), 0.0, (1.0, 1.0, 0.5))])
    model = C.RoomModel(building["rooms"][0], building)
    a, b = C.ray_grid(shift_y=C.SHIFT_Y)
    labels, depth = model.cast((2.0, 0.4, 1.25), C.yaw_directions([90], a, b))
    m = model.measure(labels, depth, C.border_mask())[0]
    assert "bed" not in m["cut"] and m["furn"] == pytest.approx(min(m["elements"]["bed"], 0.25) / 0.25)
    assert m["floor"] > 0
    labels, depth = model.cast((2.0, 2.0, 1.25), C.yaw_directions([90], a, b))
    m = model.measure(labels, depth, C.border_mask())[0]
    assert "bed" in m["cut"] and m["furn"] == pytest.approx(min(m["elements"]["bed"], 0.25) / 0.25 * 0.6)
    # near = planar depth < 0.9 m: a wall 0.85 m ahead is near over the whole frame.
    labels, depth = model.cast((3.15, 2.0, 1.25), C.yaw_directions([0], a, b))
    m = model.measure(labels, depth, C.border_mask())[0]
    assert m["near"] == 1.0 and C.is_blocked(m)


# --------------------------------------------------------------------------
# Candidates, view count, the pick
# --------------------------------------------------------------------------

def test_candidate_grid_of_an_empty_square_room():
    building = _building(4.0, 4.0)
    points, warning = C.candidate_positions(building["rooms"][0], building)
    assert warning is None
    grid = {(x, y) for x in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5) for y in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)}
    k1, k2 = round(0.45 / math.sqrt(2), 9), round(0.6 / math.sqrt(2), 9)
    corners = set()
    for cx, sx in ((0.0, 1), (4.0, -1)):
        for cy, sy in ((0.0, 1), (4.0, -1)):
            for k in (k1, k2):
                corners.add((round(cx + sx * k, 9), round(cy + sy * k, 9)))
    assert set(points) == grid | corners and len(points) == 57
    assert points == sorted(points)


def test_candidates_keep_the_obstacle_clearance():
    building = _building(4.0, 4.0, furniture=[("t", "table_dining", (2.0, 2.0), (1.0, 1.0), 0.0, (1.0, 1.0, 0.75))])
    points, _ = C.candidate_positions(building["rooms"][0], building)
    assert len(points) == 57 - 9
    for p in points:
        assert geom2d.distance_to_rect(p, (2.0, 2.0), (1.0, 1.0), 0.0) >= cameras.CAMERA_OBSTACLE_CLEARANCE - 1e-9
    # The obstacle is the fitted box when it is larger than the drawn footprint.
    big = _building(4.0, 4.0, furniture=[("t", "table_dining", (2.0, 2.0), (1.0, 1.0), 0.0, (2.0, 2.0, 0.75))])
    assert obstacle_rect(big["furniture"][0])["size"] == [2.0, 2.0]
    assert len(C.candidate_positions(big["rooms"][0], big)[0]) < len(points)


@pytest.mark.parametrize("clockwise", [False, True])
def test_only_convex_corners_get_points(clockwise):
    poly = [(0, 0), (6, 0), (6, 3), (3, 3), (3, 6), (0, 6)]
    if clockwise:
        poly = poly[::-1]
    pts = C.convex_corner_points(poly)
    assert len(pts) == 10
    for p in pts:
        assert G.point_in_polygon(p, poly) and math.dist(p, (3, 3)) > 1.0
    building = _building(polygon=[list(p) for p in poly])
    points, _ = C.candidate_positions(building["rooms"][0], building)
    for p in points:
        assert geom2d.point_is_free(p, poly, [], 0.3, 0.2)


def test_views_per_room_by_area():
    assert [C.views_for_area(a) for a in (0.5, 2.99, 3.0, 5.99, 6.0, 40.0)] == [1, 1, 2, 2, 3, 3]
    assert C.room_view_count({"polygon": [[0, 0], [2, 0], [2, 1.4], [0, 1.4], [0, 0]]}) == 1
    assert C.room_view_count({"polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]}) == 2
    assert C.room_view_count({"polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]}) == 3


def _cand(total, x, y, yaw, blocked=False):
    return {"total": total, "x": x, "y": y, "yaw": yaw, "blocked": blocked}


def test_select_views_greedy_diversity_and_drop_rules():
    cands = [_cand(3.0, 1.0, 1.0, 0), _cand(2.9, 1.0, 1.0, 30), _cand(2.8, 1.5, 1.0, 40),
             _cand(2.7, 1.0, 1.0, 60), _cand(2.6, 2.0, 1.0, 10), _cand(2.5, 3.0, 3.0, 200)]
    picks, warning = C.select_views(cands, 3)
    assert warning is None
    # 30 deg at the same point and 40 deg at 0.5 m are too similar; 60 deg is enough; then 1.0 m away.
    assert [(p["yaw"], p["x"]) for p in picks] == [(0, 1.0), (60, 1.0), (10, 2.0)]
    assert len(C.select_views(cands, 1)[0]) == 1
    # Exactly 50 deg or exactly 1.0 m is enough.
    picks, _ = C.select_views([_cand(3.0, 1.0, 1.0, 0), _cand(2.9, 1.0, 1.0, 50), _cand(2.8, 2.0, 1.0, 0)], 3)
    assert len(picks) == 3
    # Below half the best score: dropped, even when diverse.
    picks, _ = C.select_views([_cand(4.0, 1.0, 1.0, 0), _cand(1.99, 3.0, 3.0, 180), _cand(2.0, 3.0, 3.0, 90)], 3)
    assert [p["yaw"] for p in picks] == [0, 90]
    # A negative best keeps one view only.
    assert len(C.select_views([_cand(-0.5, 1.0, 1.0, 0), _cand(-0.6, 3.0, 3.0, 180)], 3)[0]) == 1
    assert C.select_views([], 3) == ([], None)


def test_select_views_ties_and_blocked_candidates():
    # Equal scores (to 1e-6): lower x, then y, then yaw first.
    cands = [_cand(2.0 + 1e-9, 2.0, 1.0, 0), _cand(2.0, 1.0, 2.0, 90), _cand(2.0, 1.0, 1.0, 180),
             _cand(2.0, 1.0, 1.0, 90)]
    assert [(p["x"], p["y"], p["yaw"]) for p in C.select_views(cands, 1)[0]] == [(1.0, 1.0, 90)]
    # A blocked candidate is never picked while an unblocked one exists, whatever its score.
    picks, warning = C.select_views([_cand(5.0, 1.0, 1.0, 0, True), _cand(1.0, 2.0, 2.0, 90)], 3)
    assert [p["yaw"] for p in picks] == [90] and warning is None
    # Only blocked candidates: the best one, with the warning.
    picks, warning = C.select_views([_cand(1.0, 1.0, 1.0, 0, True), _cand(2.0, 2.0, 2.0, 90, True)], 3)
    assert [p["yaw"] for p in picks] == [90] and warning == C.BLOCKED_WARNING == "blocked unavoidable"


def test_a_tiny_room_gets_one_blocked_view_with_the_warning():
    # Milestone 7 (§6.2): a tiny room with a piece to show still gets its one (blocked) view ...
    building = _building(1.2, 1.2, furniture=[("wb", "washbasin", (0.6, 0.95), (0.5, 0.4), 0.0, (0.5, 0.4, 0.85))])
    plans = cameras.plan_cameras(building, "L0", policy="search")
    assert len(plans) == 1 and plans[0]["warning"] == "blocked unavoidable" and plans[0]["score"]["blocked"]
    assert C.rooms_without_view(building) == []


def test_rooms_without_furniture_get_one_view_or_none_below_2_5_m2():
    # Milestone 7 (docs/milestone7.md §6.2, user decision 8).
    assert (C.EMPTY_ROOM_VIEWS, C.MIN_EMPTY_ROOM_AREA_M2) == (1, 2.5)
    big = _building(5.0, 4.0, openings=ROOM_A["openings"])            # 20 m2, nothing to show: one view
    plans = cameras.plan_cameras(big, "L0", policy="search")
    assert [p["name"] for p in plans] == ["cam_r_1"] and C.room_view_count(big["rooms"][0], big) == 1
    assert C.room_view_count(big["rooms"][0]) == 3                      # the area rule alone (pre-layout estimate)
    assert C.rooms_without_view(big) == []
    tiny = _building(1.2, 1.2)                                        # 1.44 m2, empty: no view, listed
    assert cameras.plan_cameras(tiny, "L0", policy="search") == []
    assert C.plan_room(tiny["rooms"][0], tiny) == ([], 0)
    (row,) = C.rooms_without_view(tiny, "L0")
    assert row["room_id"] == "r" and row["level_id"] == "L0" and row["label"] == "Oda" and row["area_m2"] == 1.44
    assert row["reason"].startswith("no furniture after layout and decor and 1.44 m2 < 2.5 m2")
    assert cameras.rooms_without_view(tiny, "L0", "search") == [row] and cameras.rooms_without_view(tiny, "L0") == []
    assert len(cameras.plan_cameras(tiny, "L0")) == 3                    # the m5 policy is unchanged
    assert C.room_view_count(_building(2.5, 1.0)["rooms"][0], _building(2.5, 1.0)) == 1   # exactly 2.5 m2: one view
    # Decor and build: false pieces do not count as something to show (and are not in the model).
    shown = _building(5.0, 4.0, furniture=[("sym", "unknown", (2.0, 2.0), (0.6, 0.6), 0.0, (0.6, 0.6, 0.8)),
                                           ("cush", "cushion", (3.0, 2.0), (0.4, 0.2), 0.0, (0.4, 0.2, 0.2))])
    shown["furniture"][0]["build"] = False
    shown["furniture"][1]["kind"] = "decor"
    assert C.shown_pieces(shown["rooms"][0], shown) == [] and C.RoomModel(shown["rooms"][0], shown).pieces == []
    plans = cameras.plan_cameras(shown, "L0", policy="search")
    assert len(plans) == 1 and plans[0]["visible_furniture"] == []
    assert all("sym" not in p["visible_furniture"] for p in cameras.plan_cameras(shown, "L0"))
    shown["furniture"][0]["build"] = True
    assert len(C.shown_pieces(shown["rooms"][0], shown)) == 1 and C.room_view_count(shown["rooms"][0], shown) == 3


def test_a_room_without_a_free_point_gets_the_fallback_with_a_warning():
    # A low bed leaves no free point: the M5 fallback puts the camera at the centroid (above the bed,
    # clear of every box at least as tall as the camera) and every view says so.
    building = _building(3.0, 3.0, furniture=[("b", "bed", (1.5, 1.5), (2.6, 2.6), 0.0, (2.6, 2.6, 0.6))])
    points, warning = C.candidate_positions(building["rooms"][0], building)
    assert points == [(1.5, 1.5)] and "no free camera point" in warning and "room's inner point" in warning
    plans = cameras.plan_cameras(building, "L0", policy="search")
    assert 1 <= len(plans) <= 3
    for p in plans:
        assert p["position"][:2] == [1.5, 1.5] and p["warning"].startswith("no free camera point")
    # A tall wardrobe filling the room: nothing is clear of it; the warning says the camera is inside.
    full = _building(3.0, 3.0, furniture=[("w", "wardrobe", (1.5, 1.5), (2.8, 2.8), 0.0, (2.8, 2.8, 2.1))])
    plans = cameras.plan_cameras(full, "L0", policy="search")
    assert plans and all("INSIDE a proxy" in p["warning"] for p in plans)


L_SHAFT = [[0, 0], [3, 0], [3, 0.5], [0.5, 0.5], [0.5, 3], [0, 3]]           # legs 0.5 m wide
L_CLOSET = [[0, 0], [3, 0], [3, 1.0], [1.0, 1.0], [1.0, 3], [0, 3]]          # legs 1.0 m wide
CLOSET_WARDROBES = [("w1", "wardrobe", (1.5, 0.3), (3.0, 0.6), 0.0, (3.0, 0.6, 2.1)),
                    ("w2", "wardrobe", (0.3, 1.5), (3.0, 0.6), 90.0, (3.0, 0.6, 2.1))]


@pytest.mark.parametrize("polygon, furniture, inside_proxy", [(L_SHAFT, [], False),
                                                              (L_CLOSET, CLOSET_WARDROBES, True)])
def test_fallback_camera_of_an_l_shaped_room_stays_inside_the_room(polygon, furniture, inside_proxy):
    # Review C1: the centroid of an L lies in the notch, outside the room. The fallback is anchored at the
    # room's inner point (lighting.polylabel), so the camera stays in the room, the cramped view is flagged
    # "blocked unavoidable" and the warning says where the camera is (inside a proxy only when it is).
    building = _building(3.0, 3.0, polygon=polygon, furniture=furniture)
    assert not G.point_in_polygon(G.polygon_centroid(polygon), polygon)
    plans = cameras.plan_cameras(building, "L0", policy="search")
    assert len(plans) == 1
    (plan,) = plans
    assert G.point_in_polygon(plan["position"][:2], polygon)
    assert plan["score"]["blocked"] and C.BLOCKED_WARNING in plan["warning"]
    assert "room's inner point" in plan["warning"] and "centroid" not in plan["warning"]
    assert ("INSIDE a proxy" in plan["warning"]) is inside_proxy
    if not inside_proxy:
        assert "m from the nearest wall" in plan["warning"]
    # The M5 policy keeps its own fallback, byte for byte (cameras._Search is unchanged).
    m5 = cameras.plan_cameras(building, "L0")
    assert all("centroid" in p["warning"] for p in m5)


# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------

def _search(building, level="L0"):
    return cameras.plan_cameras(building, level, policy="search")


def _strip(plans):
    return [{k: v for k, v in p.items() if k != "search_seconds"} for p in plans]


def test_search_plans_carry_the_spec_fields():
    building = _building(**ROOM_A)
    plans = _search(building)
    assert [p["name"] for p in plans] == ["cam_r_1", "cam_r_2", "cam_r_3"]      # 20 m2: 3 views
    validator = jsonschema.Draft202012Validator(schemas.SCENE_CAMERA)
    for i, p in enumerate(plans, start=1):
        assert not list(validator.iter_errors(p)), p["name"]
        assert p["index"] == i and p["room_id"] == "r" and p["level_id"] == "L0"
        assert p["policy"] == "search" and p["shift_x"] == 0.0 and p["shift_y"] == -0.10
        assert p["lens_mm"] == 24.0 and p["sensor_mm"] == 36.0 and p["resolution"] == [1920, 1080]
        assert p["position"][2] == p["target"][2] == pytest.approx(1.25)
        yaw = math.radians(p["score"]["yaw_deg"])
        assert p["target"][0] - p["position"][0] == pytest.approx(math.cos(yaw), abs=2e-6)
        assert p["target"][1] - p["position"][1] == pytest.approx(math.sin(yaw), abs=2e-6)
        assert p["anchor"] is None and p["warning"] is None and not p["score"]["blocked"]
        s = p["score"]
        assert set(s) >= {"total", "furniture", "openings", "floor", "depth", "penalties", "blocked"}
        assert s["total"] == pytest.approx(s["furniture"] + s["openings"] + s["floor"] + s["depth"] - s["penalties"],
                                           abs=5e-4)
        assert p["placement"].startswith(f"search: score {s['total']:.3f} = furniture {s['furniture']:.3f}")
        assert p["search_seconds"] >= 0 and p["search_seconds"] == plans[0]["search_seconds"]
        assert geom2d.point_is_free(p["position"][:2], [tuple(v) for v in building["rooms"][0]["polygon"]],
                                    [obstacle_rect(f) for f in building["furniture"]], 0.3, 0.2)
    assert [p["score"]["total"] for p in plans] == sorted((p["score"]["total"] for p in plans), reverse=True)
    assert C.level_search_seconds(plans) == {"L0": plans[0]["search_seconds"]}
    # The bed (type weight 3) fills a good part of the best view (its centre may lie below the frame).
    seen = C.score_camera(building, plans[0])["shares"]["elements"]
    assert seen.get("bed", 0.0) >= 0.1 and plans[0]["score"]["shares"]["furn"] > 0.5


def test_frustum_lists_use_the_shift():
    building = _building(**ROOM_A)
    for p in _search(building):
        tangents = geom2d.frustum_tangents(24.0, 36.0, (1920, 1080))
        for f in building["furniture"]:
            centre = (*f["footprint"]["center"], f["asset"]["bbox_m"][2] / 2.0)
            inside = geom2d.point_in_frustum(centre, p["position"], p["target"], tangents, shift_y=-0.10)
            assert (f["id"] in p["visible_furniture"]) == inside
        for o in building["openings"]:
            inside = geom2d.point_in_frustum((*o["center"], 1.0), p["position"], p["target"], tangents, shift_y=-0.1)
            assert (o["id"] in p["visible_openings"]) == inside


def test_search_is_deterministic_and_independent_of_input_order():
    building = json.loads((PROJECTS / "synthetic-01" / "truth" / "building.json").read_text(encoding="utf-8"))
    first = _strip(_search(building))
    assert first == _strip(_search(building))
    shuffled = json.loads(json.dumps(building))
    rng = random.Random(7)
    rng.shuffle(shuffled["furniture"])
    rng.shuffle(shuffled["openings"])
    again = {p["name"]: p for p in _strip(_search(shuffled))}
    assert set(again) == {p["name"] for p in first}
    for p in first:
        q = again[p["name"]]
        assert q["position"] == p["position"] and q["target"] == p["target"] and q["score"] == p["score"]
        assert sorted(q["visible_furniture"]) == sorted(p["visible_furniture"])


def test_m5_stays_the_default_policy():
    building = json.loads((PROJECTS / "synthetic-01" / "truth" / "building.json").read_text(encoding="utf-8"))
    default = cameras.plan_cameras(building, "L0")
    assert default == cameras.plan_cameras(building, "L0", policy="m5")
    assert all("policy" not in p and "shift_y" not in p and "score" not in p for p in default)
    with pytest.raises(ValueError):
        cameras.plan_cameras(building, "L0", policy="best")


# --------------------------------------------------------------------------
# Synthetic projects
# --------------------------------------------------------------------------

def _truth(name):
    return json.loads((PROJECTS / name / "truth" / "building.json").read_text(encoding="utf-8"))


def _final(name):
    return json.loads((RESULTS / "furniture" / name / "building_final.json").read_text(encoding="utf-8"))


SEARCH_BUILDINGS = [("truth", "synthetic-01"), ("truth", "synthetic-02"), ("truth", "synthetic-03"),
                    ("final", "synthetic-01"), ("final", "synthetic-03")]


@pytest.fixture(scope="module", params=SEARCH_BUILDINGS, ids=lambda p: f"{p[0]}-{p[1]}")
def searched(request):
    kind, name = request.param
    building = _truth(name) if kind == "truth" else _final(name)
    plans = []
    for level in building["levels"]:
        plans.extend(_search(building, level["id"]))
    return name, building, plans


def test_synthetic_search_views_per_room(searched):
    name, building, plans = searched
    by_room = {}
    for p in plans:
        by_room.setdefault(p["room_id"], []).append(p)
    without = {r["room_id"] for r in C.rooms_without_view(building)}
    assert set(by_room) == {r["id"] for r in building["rooms"]} - without and not set(by_room) & without, name
    for room in building["rooms"]:
        if room["id"] in without:
            assert not C.shown_pieces(room, building) and G.polygon_area(C.room_polygon(room)) < 2.5, room["id"]
            continue
        views = by_room[room["id"]]
        assert 1 <= len(views) <= C.room_view_count(room, building) <= C.room_view_count(room), room["id"]
        if not C.shown_pieces(room, building):
            assert len(views) == 1, room["id"]                           # Milestone 7: nothing to show, one view
        assert [p["name"] for p in views] == [f"cam_{room['id']}_{i}" for i in range(1, len(views) + 1)]


def test_synthetic_search_cameras_are_free_and_unblocked(searched):
    name, building, plans = searched
    rooms = {r["id"]: r for r in building["rooms"]}
    blocked = []
    for p in plans:
        room = rooms[p["room_id"]]
        poly = C.room_polygon(room)
        obstacles = [obstacle_rect(f) for f in building["furniture"]
                     if f.get("room_id") == room["id"] and f.get("kind") != "decor"]
        if not p["warning"]:
            assert geom2d.point_is_free(p["position"][:2], poly, obstacles, 0.3, 0.2), p["name"]
        assert G.point_in_polygon(p["position"][:2], poly), p["name"]
        if p["score"]["blocked"]:
            blocked.append(p["name"])
            assert p["warning"] and "blocked unavoidable" in p["warning"], p["name"]
    print(f"{name}: {len(plans)} views, blocked unavoidable: {blocked}")


def test_synthetic_search_beats_the_m5_cameras_by_the_model(searched):
    name, building, plans = searched
    m5 = [p for level in building["levels"] for p in cameras.plan_cameras(building, level["id"])]
    m5_scores = [C.score_camera(building, p) for p in m5]
    mean_m5 = sum(s["terms"]["total"] for s in m5_scores) / len(m5_scores)
    mean_search = sum(p["score"]["total"] for p in plans) / len(plans)
    blocked_m5 = sum(s["terms"]["blocked"] for s in m5_scores)
    floor_m5 = sum(s["shares"]["floor"] for s in m5_scores) / len(m5_scores)
    floor_search = sum(p["score"]["shares"]["floor"] for p in plans) / len(plans)
    print(f"{name}: model score m5 {mean_m5:.2f} -> search {mean_search:.2f}; floor {floor_m5:.3f} -> "
          f"{floor_search:.3f}; blocked m5 {blocked_m5}")
    assert mean_search > mean_m5 + 1.0 and floor_search > floor_m5
    # The best view of every room scores at least as well as the best M5 view of that room.
    best_m5 = {}
    for p, s in zip(m5, m5_scores):
        best_m5[p["room_id"]] = max(best_m5.get(p["room_id"], -9.0), s["terms"]["total"])
    for p in plans:
        if p["index"] == 1:
            assert p["score"]["total"] >= best_m5[p["room_id"]] - 1e-3, p["name"]


def test_plan_count_of_the_committed_buildings_follows_the_area_rule():
    # docs/milestone6.md §8.1: 29 views for synthetic-01 and 50 for synthetic-03 by the area rule.
    assert sum(C.room_view_count(r) for r in _final("synthetic-01")["rooms"]) == 29
    assert sum(C.room_view_count(r) for r in _final("synthetic-03")["rooms"]) == 50
    # Milestone 7 (§6.2): synthetic-03's two storage rooms and the balcony have nothing to show (3 + 2 + 1 -> 1
    # each); synthetic-01's furnished rooms keep the area rule. No committed room is empty and under 2.5 m2.
    final = {name: _final(name) for name in ("synthetic-01", "synthetic-03")}
    assert sum(C.room_view_count(r, final["synthetic-01"]) for r in final["synthetic-01"]["rooms"]) == 29
    assert sum(C.room_view_count(r, final["synthetic-03"]) for r in final["synthetic-03"]["rooms"]) == 44
    assert [r["id"] for r in final["synthetic-03"]["rooms"] if not C.shown_pieces(r, final["synthetic-03"])] == \
        ["r_L-1_kiler", "r_L-1_kiler_2", "r_L1_balkon"]
    assert all(C.rooms_without_view(b) == [] for b in final.values())


def test_search_time_of_synthetic_03_is_within_budget():
    building = _final("synthetic-03")
    t0 = time.perf_counter()
    plans = []
    for level in building["levels"]:
        plans.extend(_search(building, level["id"]))
    seconds = time.perf_counter() - t0
    recorded = sum(C.level_search_seconds(plans).values())
    print(f"synthetic-03: {len(plans)} views searched in {seconds:.1f} s")
    assert seconds <= 60.0 and 0 < recorded <= seconds + 0.01      # recorded per level, rounded to 1 ms
    assert set(C.level_search_seconds(plans)) == {lv["id"] for lv in building["levels"]}


# --------------------------------------------------------------------------
# M5 policy: the committed M5 cameras, 1 mm
# --------------------------------------------------------------------------

def _git_show(path: str):
    try:
        out = subprocess.run(["git", "show", f"{M5_COMMIT}:{path}"], cwd=ROOT, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"git not usable: {exc}")
    if out.returncode != 0:
        pytest.skip(f"{M5_COMMIT}:{path} not in this clone (shallow?): {out.stderr.decode()[-200:]}")
    return json.loads(out.stdout.decode("utf-8"))


@pytest.mark.parametrize("name", ["synthetic-01", "synthetic-03"])
def test_m5_policy_reproduces_the_committed_m5_cameras(name):
    scene = _git_show(f"results/renders/{name}/scene_manifest.json")
    building = _git_show(f"results/furniture/{name}/building_final.json")
    plans = {p["name"]: p for level in building["levels"]
             for p in cameras.plan_cameras(building, level["id"], policy="m5")}
    committed = {c["name"]: c for c in scene["cameras"]}
    assert set(plans) == set(committed) and len(committed) in (30, 57)
    for cam, c in committed.items():
        for key in ("position", "target"):
            assert max(abs(a - b) for a, b in zip(plans[cam][key], c[key])) <= 0.001, (cam, key)
        assert plans[cam]["room_id"] == c["room_id"] and plans[cam]["index"] == c["index"]
    # Byte for byte: every field of every plan (warnings, anchors, frustum lists) is the committed one.
    assert [cam for cam, c in committed.items() if plans[cam] != c] == []


# --------------------------------------------------------------------------
# Imports, CLI, Blender's Python
# --------------------------------------------------------------------------

def test_camsearch_imports_no_blender_shapely_cv2_or_pil():
    code = ("import sys, wenart.blender.camsearch; "
            "print(','.join(m for m in ('bpy', 'shapely', 'cv2', 'PIL', 'scipy', 'yaml') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


def test_cli_writes_the_plans_and_a_report(tmp_path, capsys):
    path = tmp_path / "building.json"
    path.write_text(json.dumps(_building(**ROOM_A)), encoding="utf-8")
    rc = C.main([str(path), "--out", str(tmp_path / "cams.json"), "--report", str(tmp_path / "cams.md")])
    assert rc == 0
    out = json.loads((tmp_path / "cams.json").read_text(encoding="utf-8"))
    assert out["policy"] == "search" and len(out["cameras"]) == 3 and set(out["search_seconds"]) == {"L0"}
    md = (tmp_path / "cams.md").read_text(encoding="utf-8")
    assert "| cam_r_1 | r |" in md and "blocked unavoidable: none" in capsys.readouterr().out
    assert C.main([str(path), "--out", str(tmp_path / "x.json"), "--level", "L9"]) == 2


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_search_runs_inside_blender_python_with_the_same_result(tmp_path):
    src = PROJECTS / "synthetic-01" / "truth" / "building.json"
    out = tmp_path / "plans.json"
    expr = (f"import sys, json; sys.path.insert(0, {str(ROOT)!r})\n"
            "from wenart.blender import cameras\n"
            f"b = json.load(open({str(src)!r}))\n"
            "plans = [p for lv in b['levels'] for p in cameras.plan_cameras(b, lv['id'], policy='search')]\n"
            f"json.dump(plans, open({str(out)!r}, 'w'))\n")
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", expr],
                          capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    inside = _strip(json.loads(out.read_text(encoding="utf-8")))
    building = _truth("synthetic-01")
    here = _strip([p for lv in building["levels"] for p in _search(building, lv["id"])])
    assert [p["name"] for p in inside] == [p["name"] for p in here]
    for a, b in zip(inside, here):
        assert a["position"] == pytest.approx(b["position"], abs=1e-9) and a["target"] == pytest.approx(b["target"])
        assert a["score"]["total"] == pytest.approx(b["score"]["total"], abs=1e-6)
