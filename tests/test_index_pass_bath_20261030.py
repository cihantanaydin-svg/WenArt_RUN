"""The bathroom fixtures the index pass missed (30 Oct 2026; GPU test
tests/gpu/test_render.py::test_index_pass_contains_every_visible_proxy on real04 run 20261029-201533-full: six views,
every one a bathroom fixture planned in the frustum and absent from the index pass). CPU only.

Causes and the general rules that fix them:

- The wall-hung WCs (cam_r_L-1_banyo_2, cam_r_L0_banyo_2, cam_r_L0_e_banyo_2): the drawn WC blocks reach 1.1-1.4 cm
  into the wall line, and ``bath_parts.wall_hung_wc_parts`` put the flush plate (8 mm) on the footprint's back edge:
  inside the wall. In those close views the pan hangs below the frame, so the plate is all a frame could show, and
  the ray model saw the floor-standing WC's profile (a back slab up to 0.94 m from the floor, air in the render).
  Rule 1 (``bath_parts.seat_on_walls``): a made-to-measure bath piece's parts sit on the face of the wall behind it
  (at most 6 cm either way; the drawn footprint stays). Rule 2 (``camsearch.made_boxes``): the model holds a
  made-to-measure piece where it is built: its parts in height bands (the pan, the plate).
- cam_r_L1_banyo_1: an agent pose 0.21 m over the sloped roof ceiling rendered black; its plan listed the room's
  three fixtures. Rule 3: a lens over its ceiling lists nothing and sees the ceiling's back
  (``RoomModel.above_ceiling``), and V1 refuses such a pose (``exterior_checks.camera_problems``).
- The library tubs (cam_r_L-1_banyo_1, cam_r_L0_banyo_1): the frame's edge holds a corner of the fitted box that a
  freestanding tub's rounded end leaves empty; fixed equipment keeps the GPU test's 2 cm box slack. Rule 4: the
  build records each furniture mesh's convex plan outline (``box3d.outline``, ``geom2d.plan_outline``) and the GPU
  test allows a library piece the model does not see as that outline (``camsearch.piece_with_outline``).
"""
from __future__ import annotations

import copy
import math

import numpy as np
import pytest

import _m11_room as M
from test_blender_render import _gpu_test_module
from wenart.blender import bath_parts as BT
from wenart.blender import camsearch as CS
from wenart.blender import exterior_checks as EC
from wenart.blender import geom2d
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.furniture import bath_details as BD

# --------------------------------------------------------------------------
# real04 run 20261029-201533-full, cut to r_L-1_banyo (its door and that door's wall, the WC and the tub as the
# run's building_built.json has them; the WC's look reduced to what its builder reads). camsearch.model_shares of the
# cut equals the whole building's for the tub and the WC in the two views below.
# --------------------------------------------------------------------------

REAL04_ROOM = {"id": "r_L-1_banyo", "level_id": "L-1", "room_type": "bathroom", "label": "Banyo",
               "polygon": [[4.7181, 9.9351], [7.3861, 9.9351], [7.3861, 11.8011], [4.7181, 11.8011]]}
REAL04_WC = {"id": "f_L-1_051", "level_id": "L-1", "room_id": "r_L-1_banyo", "type": "toilet",
             "source": "from_documents", "footprint": {"center": [6.0523, 10.2673], "size": [0.5, 0.69],
                                                       "rotation_deg": 180.0},
             "front_deg": 90.0, "height": None, "asset": {"method": "parametric", "bbox_m": [0.5, 0.69, 0.8]},
             "bath_look": {"family": "modern", "wc": "wall_hung", "made_to_measure": True}}
REAL04_TUB = {"id": "f_L-1_056", "level_id": "L-1", "room_id": "r_L-1_banyo", "type": "bathtub",
              "source": "from_documents", "footprint": {"center": [6.9866, 10.884], "size": [1.8339, 0.8],
                                                        "rotation_deg": 270.0},
              "front_deg": 180.0, "height": 0.6,
              "asset": {"method": "library", "bbox_m": [1.8339, 0.7963, 0.8137]}}
REAL04_BATHROOM = {
    "project": {"id": "real04"}, "status": "ok",
    "levels": [{"id": "L-1", "elevation": -3.0, "ceiling_height": 2.85}],
    "walls": [{"id": "w_L-1_010", "level_id": "L-1", "start": [4.6681, 9.9351], "end": [4.6681, 11.8011],
               "thickness": 0.1}],
    "openings": [{"id": "d_L-1_001", "type": "door", "level_id": "L-1", "wall_id": "w_L-1_010",
                  "center": [4.6681, 10.9911], "width": 0.8, "height": 2.1, "sill_height": None,
                  "swing_side": "r_L-1_banyo"}],
    "rooms": [REAL04_ROOM], "furniture": [REAL04_WC, REAL04_TUB]}
# the run's two views of the room: the searched one sees the tub's box corner, the agent's the WC from 0.75 m
SEARCHED = {"name": "cam_r_L-1_banyo_1", "kind": "interior", "room_id": "r_L-1_banyo", "level_id": "L-1",
            "position": [6.2181, 11.4351, -1.75], "target": [5.7181, 10.569075, -1.75], "lens_mm": 16.0,
            "sensor_mm": 36.0, "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": -0.1, "policy": "search"}
AGENT = {"name": "cam_r_L-1_banyo_2", "kind": "interior", "room_id": "r_L-1_banyo", "level_id": "L-1",
         "position": [5.7181, 10.9351, -1.75], "target": [6.2181, 10.069075, -1.75], "lens_mm": 16.0,
         "sensor_mm": 36.0, "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": 0.0, "policy": "agent",
         "pitch_deg": 0.0}
WALL_Y = 9.9351                              # the face of the wall behind the WC (the room outline)

# real04's top level L1 under the roof: its ceiling planes (building_built.json) and the L1 bathroom
REAL04_L1 = {"id": "L1", "elevation": 3.15, "ceiling_height": 2.451, "open_rooms": ["r_L1_teras", "r_L1_teras_2"],
             "ceiling_planes": [[-0.6371033730339123, -0.0, 13.496797535746824],
                                [0.6370454545454544, -0.0, 3.8300690607006826],
                                [-0.0, -0.6370454545454546, 11.475570083427955],
                                [-0.0, 0.6370454545454546, 3.8297505379734096],
                                [-0.0, -0.19981395348837205, 7.004830048420885],
                                [-0.0, 0.19981395348837197, 4.606662978653444],
                                [-0.19981395348837225, -0.0, 7.638559983304608],
                                [0.19981395348837228, -0.0, 4.606762885630187], [0.0, 0.0, 5.601]]}


def _l1_bathroom() -> dict:
    b = copy.deepcopy(REAL04_BATHROOM)
    b["levels"] = [copy.deepcopy(REAL04_L1)]
    b["walls"], b["openings"] = [], []
    room = dict(REAL04_ROOM, id="r_L1_banyo", level_id="L1",
                polygon=[[4.7185, 9.935], [7.3865, 9.935], [7.3865, 11.801], [4.7185, 11.801]])
    b["rooms"] = [room]
    b["furniture"] = [dict(copy.deepcopy(f), level_id="L1", room_id="r_L1_banyo") for f in b["furniture"]]
    return b


def _part(parts, role):
    return [p for p in parts if p["role"] == role]


def _world_y(piece, parts):
    """World y of every vertex of ``parts`` (a piece frame) of a piece turned by 180 degrees (real04's WC)."""
    assert piece["footprint"]["rotation_deg"] == 180.0
    return [piece["footprint"]["center"][1] - y for p in parts for _x, y, _z in p["verts"]]


# --------------------------------------------------------------------------
# Rule 1: a made-to-measure piece's back on its wall's face
# --------------------------------------------------------------------------

def test_the_wall_gap_is_measured_against_the_wall_behind_the_back():
    assert BT.wall_gap(REAL04_WC, REAL04_ROOM["polygon"]) == pytest.approx(-0.0128, abs=1e-4)   # 1.28 cm in the wall
    # the tub's back (rotation 270: +x) on the east wall: none of its length is off the face
    assert BT.wall_gap(REAL04_TUB, REAL04_ROOM["polygon"]) == pytest.approx(-0.0005, abs=1e-4)
    far = copy.deepcopy(REAL04_WC)
    far["footprint"]["center"][1] += 0.10                         # 8.7 cm off the wall: not its wall
    assert BT.wall_gap(far, REAL04_ROOM["polygon"]) is None
    gap = copy.deepcopy(REAL04_WC)
    gap["footprint"]["center"][1] += 0.03                         # 1.7 cm off the wall
    assert BT.wall_gap(gap, REAL04_ROOM["polygon"]) == pytest.approx(0.0172, abs=1e-4)
    turned = copy.deepcopy(REAL04_WC)
    turned["footprint"]["rotation_deg"] = 90.0                    # its back to the west: no wall within 6 cm
    assert BT.wall_gap(turned, REAL04_ROOM["polygon"]) is None


def test_the_real04_wc_flush_plate_is_built_on_the_wall_face_not_inside_it():
    """The run's WC: its plate (8 mm) and buttons (2 mm proud) lay 1.28 cm behind the wall face, so no frame saw
    them; seated, the plate's back is on the face and the pan's back too."""
    before = P.build_parts("toilet", 0.5, 0.69, 0.4, piece=REAL04_WC)
    plate = _part(before, "plate") + _part(before, "button")
    assert max(_world_y(REAL04_WC, plate)) < WALL_Y - 0.001          # the run: all inside the wall
    b = copy.deepcopy(REAL04_BATHROOM)
    recs = BT.seat_on_walls(b)
    wc = b["furniture"][0]
    assert [r["id"] for r in recs] == ["f_L-1_051"] and recs[0]["gap_m"] == pytest.approx(-0.0128)
    assert "into the wall" in recs[0]["reason"] and wc["footprint"] == REAL04_WC["footprint"]     # drawn footprint
    after = P.build_parts("toilet", 0.5, 0.69, 0.4, piece=wc)
    assert min(_world_y(wc, _part(after, "plate"))) == pytest.approx(WALL_Y, abs=1e-6)       # its back on the face
    assert min(_world_y(wc, _part(after, "button"))) > WALL_Y                                # proud of the plate
    assert min(_world_y(wc, _part(after, "back"))) == pytest.approx(WALL_Y, abs=1e-6)        # the pan on the wall
    assert BT.seat_on_walls(b) == recs and b["furniture"][0] == wc                          # idempotent
    # the tub is no made-to-measure piece: nothing recorded on it
    assert "wall_gap_m" not in (b["furniture"][1].get("bath_look") or {})


def test_every_made_to_measure_piece_of_the_layout_sits_on_its_wall():
    """The layout stage (``bath_details.plan_building``) seats the WC (1.3 cm in the wall), the shower (2 cm off it)
    and the vanity's module plan; a piece beyond the reach stays as drawn; the fluted wall's WC hangs on its face."""
    toilet = M.fp("t1", "toilet", (2.663, 0.95), (0.4, 0.7), rotation=270.0)       # back at x = 3.013 (east wall 3.0)
    shower = M.fp("s1", "shower", (2.55, 2.13), (0.9, 0.9), rotation=0.0)          # back at y = 2.58 (north wall 2.6)
    basin = M.fp("w1", "washbasin", (1.2, 2.6 - 0.225 - 0.10), (0.6, 0.45), rotation=0.0)   # 10 cm off the wall
    b = M.building(w=3.0, h=2.6, room_type="bathroom", window=None, furniture=[toilet, shower, basin])
    _b, recs = BD.plan_building(b, {"family": "japandi"})
    by = {f["id"]: f for f in b["furniture"]}
    assert by["t1"]["bath_look"]["wall_gap_m"] == pytest.approx(-0.013)
    assert by["s1"]["bath_look"]["wall_gap_m"] == pytest.approx(0.02)
    assert "wall_gap_m" not in by["w1"]["bath_look"]
    assert recs[0]["pieces"]["t1"]["wall_gap_m"] == pytest.approx(-0.013)
    # the WC on the japandi fluted wall (B24, 2 cm on the wall face): its plate on the panel's face
    assert by["t1"]["bath_look"]["wall_offset_m"] == BT.FLUTED_WALL_T_M
    parts = P.build_parts("toilet", 0.4, 0.7, 0.4, piece=by["t1"])
    plate_x = 2.663 + max(y for p in _part(parts, "plate") for _x, y, _z in p["verts"])   # rotation 270: +y -> +x
    assert plate_x == pytest.approx(3.0 - BT.FLUTED_WALL_T_M, abs=1e-6)
    # the shower's fittings move 2 cm back onto the wall (the plan's copy of the look carries the gap)
    plan = MOD.plan_bath_made(by["s1"])
    moved, drawn = MOD.module_parts(plan), BT.walk_in_shower_parts(0.9, 0.9, float(plan["modules"][1]["size_m"][2]))
    assert max(y for p in moved for _x, y, _z in p["verts"]) == pytest.approx(
        max(y for p in drawn for _x, y, _z in p["verts"]) + 0.02)
    # the build's step finds a fit's stored module plan too and clears a stale gap
    by["w1"]["bath_look"]["wall_gap_m"] = 0.05
    by["s1"]["asset"] = {"method": "module", "module_plan": copy.deepcopy(plan)}
    by["s1"]["asset"]["module_plan"]["bath_look"].pop("wall_gap_m")
    BT.seat_on_walls(b)
    assert "wall_gap_m" not in by["w1"]["bath_look"]
    assert by["s1"]["asset"]["module_plan"]["bath_look"]["wall_gap_m"] == pytest.approx(0.02)


def test_the_seat_stays_within_its_reach_and_leaves_other_pieces():
    look = {"wall_gap_m": 0.5}
    assert BT.seat_shift(look) == BT.WALL_SEAT_REACH_M and BT.seat_shift({"wall_gap_m": -0.0004}) == 0.0
    assert BT.seat_shift({"wall_gap_m": True}) == 0.0 and BT.seat_shift(None) == 0.0
    parts = [P._box(0.0, 0.0, 0.0, 0.2, 0.2, 0.2, "steel", "body")]
    assert BT.seat_parts(parts, {}) is parts
    # a drawn WC of a classic family (close-coupled, no made-to-measure look) is built as before
    classic = dict(copy.deepcopy(REAL04_WC), bath_look={"wc": "close_coupled", "wall_gap_m": -0.0128})
    assert P.build_parts("toilet", 0.5, 0.69, 0.4, piece=classic) == P.build_parts("toilet", 0.5, 0.69, 0.4)


# --------------------------------------------------------------------------
# Rule 2: the model holds a made-to-measure piece where it is built
# --------------------------------------------------------------------------

def test_the_model_of_the_wall_hung_wc_is_its_pan_and_its_plate():
    b = copy.deepcopy(REAL04_BATHROOM)
    BT.seat_on_walls(b)
    wc = b["furniture"][0]
    boxes = CS.made_boxes(wc)
    assert len(boxes) == 2
    pan, plate = boxes
    assert pan[2] == pytest.approx(BT.WC_BOTTOM_M) and pan[5] == pytest.approx(0.448, abs=1e-3)
    assert plate[2] == pytest.approx(BT.FLUSH_PLATE_Z_M) and plate[5] == pytest.approx(1.144, abs=1e-3)
    assert plate[4] == pytest.approx(0.69 / 2.0 - 0.0128, abs=1e-6)                # on the wall's face
    assert CS.made_boxes(REAL04_TUB) is None                                         # a library piece: its profile
    model = CS.RoomModel(REAL04_ROOM, b)
    code = next(CS.FIRST_ELEMENT + k for k, e in enumerate(model.elements) if e["id"] == "f_L-1_051")
    x = 6.0523

    def hit(z):                                    # a level ray from the room towards the WC's wall at height z
        labels, depth = model.cast((x, 10.9, -3.0 + z), np.array([[0.0, -1.0, 0.0]]))
        return int(labels[0]), float(depth[0])
    assert hit(0.70)[0] == CS.WALL                   # the air between the pan and the plate (the old back slab)
    lab, d = hit(1.06)
    assert lab == code and d == pytest.approx(10.9 - (WALL_Y + 0.010), abs=1e-4)    # the plate's buttons, 1 cm out
    assert hit(0.35)[0] == code                      # the pan
    cx, cy, cz = CS.model_centre(wc, -3.0)
    assert cx == pytest.approx(x) and cz == pytest.approx(-3.0 + (0.2 + 1.144) / 2.0, abs=1e-3)


def test_the_close_agent_view_lists_the_wc_only_by_its_plate_on_the_wall():
    """cam_r_L-1_banyo_2 (0.75 m from the WC): the pan is below the frame. The run's WC (plate in the wall) is not
    in the model's view; the seated WC is, by its plate, the part the render shows (the Blender check of the fix:
    1718 of 129600 index pixels at 480 x 270)."""
    run = copy.deepcopy(REAL04_BATHROOM)
    assert "f_L-1_051" not in CS.frame_lists(run, AGENT)["visible_furniture"]
    BT.seat_on_walls(run)
    shares = CS.model_shares(run, AGENT)
    assert shares["f_L-1_051"] > 0.005 and "f_L-1_051" in CS.frame_lists(run, AGENT)["visible_furniture"]
    forward, right, up = CS.look_axes(AGENT["position"], AGENT["target"])
    bounds = CS.frame_bounds(16.0)
    pan, plate = CS.made_boxes(run["furniture"][0])
    fp = run["furniture"][0]["footprint"]

    def inside(box):
        x0, y0, z0, x1, y1, z1 = box
        cx, cy = fp["center"][0] - (x0 + x1) / 2.0, fp["center"][1] - (y0 + y1) / 2.0    # rotation 180
        corners = CS.box_corners(cx, cy, x1 - x0, y1 - y0, -3.0 + z0, -3.0 + z1, 180.0)
        return float(CS.box_in_frame(corners[None], AGENT["position"], forward, right, up, bounds)[0][0, 0])
    assert inside(pan) == 0.0 and inside(plate) > 0.9



# --------------------------------------------------------------------------
# Rule 3: a lens over its sloped ceiling
# --------------------------------------------------------------------------

def test_a_lens_over_its_sloped_ceiling_sees_nothing_and_v1_refuses_it():
    b = _l1_bathroom()
    over = dict(AGENT, name="cam_r_L1_banyo_1", room_id="r_L1_banyo", level_id="L1",
                position=[5.7185, 11.435, 4.4], target=[6.2185, 10.568975, 4.4])        # the run's pose
    under = dict(over, position=[5.7185, 10.935, 4.4], target=[6.2185, 10.068975, 4.4])    # the run before
    assert CS.ceiling_above_floor(REAL04_L1, over["position"][:2]) == pytest.approx(1.041, abs=1e-3)
    lists = CS.frame_lists(b, over)
    assert lists["visible_furniture"] == [] and lists["visible_openings"] == []
    assert CS.model_shares(b, over) == {}
    assert CS.frame_lists(b, under)["visible_furniture"]
    v = [x for x in EC.camera_problems(b, over) if "ceiling" in x["message"]]
    assert len(v) == 1 and v[0]["severity"] == "critical" and v[0]["metrics"]["ceiling_m"] == pytest.approx(1.041,
                                                                                                         abs=1e-3)
    # the run before's pose sees the room; it keeps less than the search's 0.30 m of headroom (camsearch.HEADROOM_M,
    # a major note of the same V1), never the critical "over its ceiling"
    assert not [x for x in EC.camera_problems(b, under) if "ceiling" in x["message"] and x["severity"] == "critical"]
    verdict = EC.validate_camera_override(b, {"view_id": over["name"], "action": "set", "kind": "interior",
                                              "room_id": "r_L1_banyo", "position": over["position"],
                                              "target": over["target"], "lens_mm": 16.0, "reason": "test"})
    assert not verdict["ok"] and any("ceiling" in f for f in verdict["failed"])
    # a roof terrace open to the sky has no ceiling to stand over
    terrace = _l1_bathroom()
    terrace["levels"][0]["open_rooms"] = ["r_L1_banyo"]
    assert CS.frame_lists(terrace, over)["visible_furniture"]
    assert not [x for x in EC.camera_problems(terrace, over) if "ceiling" in x["message"]]


# --------------------------------------------------------------------------
# Rule 4: a library mesh as its built outline
# --------------------------------------------------------------------------

def _ellipse(w, d, n=200):
    return [(w / 2.0 * math.cos(2 * math.pi * k / n), d / 2.0 * math.sin(2 * math.pi * k / n)) for k in range(n)]


def test_the_plan_outline_holds_the_mesh_and_hugs_it():
    pts = _ellipse(1.8, 0.8)
    out = geom2d.plan_outline([(x + 3.0, y - 1.0, 0.5) for x, y in pts], 0.0, (3.0, -1.0))
    assert len(out) == geom2d.OUTLINE_DIRECTIONS
    from wenart import geometry as G
    assert G.polygon_signed_area(out) > 0                                            # counter-clockwise
    for x, y in pts:                                                                # every point inside
        assert all((b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]) >= -1e-9
                   for a, b in zip(out, out[1:] + out[:1]))
    assert G.polygon_area(out) / (math.pi * 0.9 * 0.4) == pytest.approx(1.0, abs=0.015)
    box = geom2d.plan_outline([(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)], 90.0, (1.0, 0.5))
    assert G.polygon_area(box) == pytest.approx(2.0, abs=0.01)                     # turned: 1 x 2 in its frame
    assert max(abs(x) for x, _y in box) == pytest.approx(0.5, abs=2e-3)
    assert geom2d.plan_outline([], 0.0) == []


def _tub_box(outline_pts):
    """The run's tub box3d (the built mesh: the fitted box at the footprint, 1.9 mm off) with an outline."""
    box = {"center": [6.9885, 10.884, -2.5931], "size": [1.8339, 0.7962, 0.8137], "rotation_deg": 270.0}
    r = math.radians(270.0)
    world = [(box["center"][0] + math.cos(r) * x - math.sin(r) * y, box["center"][1] + math.sin(r) * x
              + math.cos(r) * y) for x, y in outline_pts]
    box["outline"] = geom2d.plan_outline(world, 270.0, box["center"][:2])
    return box


def test_a_freestanding_tub_is_not_seen_where_its_box_corner_is():
    """cam_r_L-1_banyo_1: the model sees 0.0238 of the tub's fitted box (a corner at the frame's left edge); as a
    box-shaped outline the same; as an oval tub (its rounded ends) none."""
    shares = CS.model_shares(REAL04_BATHROOM, SEARCHED)
    assert shares["f_L-1_056"] == pytest.approx(0.0238, abs=1e-4)
    w, d = 1.8339, 0.7962
    square = CS.piece_with_outline(REAL04_TUB, _tub_box([(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2),
                                                          (-w / 2, d / 2)]))
    oval = CS.piece_with_outline(REAL04_TUB, _tub_box(_ellipse(w, d)))
    for piece, want in ((square, pytest.approx(0.0238, abs=2e-3)), (oval, 0.0)):
        model = dict(REAL04_BATHROOM, furniture=[REAL04_WC, piece])
        assert CS.model_shares(model, SEARCHED).get("f_L-1_056", 0.0) == want
    assert CS.piece_with_outline(REAL04_TUB, {"center": [0, 0, 0], "size": [1, 1, 1]}) is None


def _index_project(outputs, objects, index_values):
    import json

    path = outputs / "real04" / "building_final.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(REAL04_BATHROOM), encoding="utf-8")
    camera = dict(SEARCHED, **CS.frame_lists(REAL04_BATHROOM, SEARCHED))           # as the build records it
    assert camera["visible_furniture"] == ["f_L-1_051", "f_L-1_056"]
    scene = {"building": str(path), "pass_index": {"d_L-1_001": 1, "f_L-1_051": 45, "f_L-1_056": 50},
             "cameras": [camera], "objects": objects}
    return "real04", scene, {"renders": [{"camera": SEARCHED["name"], "index_values": index_values}]}


def _objects(box):
    return [{"wenart_id": "f_L-1_056", "kind": "furniture", "type": "bathtub", "box3d": box,
             "materials": ["Ceramic_basin"]},
            {"wenart_id": "f_L-1_051", "kind": "furniture", "type": "toilet", "materials": ["ceramic_white"]}]


def test_the_gpu_index_test_allows_the_tub_its_outline_hides(tmp_path, monkeypatch, capsys):
    """The run's searched view without the tub's index (its render had the door, the WC, the basin): allowed as an
    outline the model does not see; still a failure for a tub that fills its box (a built-in tub), a mesh built 5 cm
    off its footprint, or a box3d without an outline (a manifest of an older build)."""
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    w, d = 1.8339, 0.7962
    oval = _tub_box(_ellipse(w, d))
    gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path / "outputs", _objects(oval), [1, 45]))
    assert "('cam_r_L-1_banyo_1', 'f_L-1_056')" in capsys.readouterr().out
    square = _tub_box([(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)])
    moved = copy.deepcopy(oval)
    moved["center"][0] += 0.05
    bare = {k: v for k, v in oval.items() if k != "outline"}
    for box in (square, moved, bare):
        with pytest.raises(AssertionError, match=r"cam_r_L-1_banyo_1', \['f_L-1_056'\]"):
            gpu.test_index_pass_contains_every_visible_proxy(_index_project(tmp_path / "outputs", _objects(box),
                                                                            [1, 45]))
