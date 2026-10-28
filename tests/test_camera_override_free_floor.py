"""An agent camera stands on free floor (pod P8, 11 Oct 2026, ``exterior_checks.free_floor_problems``).

real03's 1.6 x 2.5 m bathroom ``r_L0_banyo_2`` has no free floor (bathtub, shower, toilet, a door), so the camera
search used its fallback point over the bathtub. The agent moved ``cam_r_L0_banyo_2_1`` to [27.3, 4.9], 0.05 m
beside the 2 m shower glass: half the frame was the glass (depth 0.05 m at the lens, a blocked view). The move is now
refused with the nearest free point; the search's own point passes. In a room with free floor the camera keeps
0.2 m from every floor piece and free-standing decor and 0.15 m from the walls."""
from wenart.blender import exterior_checks as X

EV = [{"file": "sheet.dxf", "page": 1, "method": "vector", "confidence": 1.0}]


def piece(pid, typ, center, size, rot, height):
    return {"id": pid, "level_id": "L0", "room_id": "r_L0_banyo_2", "type": typ, "source": "from_documents",
            "footprint": {"center": center, "size": size, "rotation_deg": rot},
            "asset": {"library": "parametric", "method": "parametric", "bbox_m": [size[0], size[1], height]}}


def bathroom() -> dict:
    room = {"id": "r_L0_banyo_2", "level_id": "L0", "label": "Banyo", "room_type": "bathroom", "status": "verified",
            "polygon": [[26.4039, 3.3503], [28.0039, 3.3503], [28.0039, 5.8503], [27.0039, 5.8503],
                        [27.0039, 5.0503], [26.4039, 5.0503]], "evidence": EV}
    wall = {"id": "w_L0_146", "level_id": "L0", "start": [28.0539, 3.2503], "end": [28.0539, 10.1503],
            "thickness": 0.1, "height": 2.7, "status": "verified", "evidence": EV}
    door = {"id": "d_L0_011", "type": "door", "level_id": "L0", "wall_id": "w_L0_146", "center": [28.0539, 4.7005],
            "width": 0.6999, "height": 2.1, "swing_side": "r_L0_banyo_2", "status": "verified", "evidence": EV}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [room], "walls": [wall],
            "openings": [door], "decor": [],
            "furniture": [piece("f_L0_079", "toilet", [27.4831, 5.5543], [0.3563, 0.5324], 0.0, 0.8),
                          piece("f_L0_148", "shower", [26.8233, 4.628], [0.8457, 0.8], 0.0, 2.0),
                          piece("f_L0_187", "bathtub", [27.241, 3.773], [1.621, 0.8], 180.0, 0.7)]}


def cam(position):
    return {"action": "set", "view_id": "cam_r_L0_banyo_2_1", "kind": "interior", "room_id": "r_L0_banyo_2",
            "position": position, "target": [27.0, 3.8, 0.9], "lens_mm": 20.0, "reason": "see the bathtub"}


def test_the_p8_bathroom_camera_beside_the_shower_glass_is_refused():
    verdict = X.validate_camera_override(bathroom(), cam([27.3, 4.9, 1.5]))
    assert not verdict["ok"]
    msg = verdict["failed"][-1]
    assert "0.05 m from f_L0_148" in msg and "nearest free point" in msg, verdict


def test_the_search_fallback_point_passes():
    from wenart.blender import camsearch as CS

    b = bathroom()
    (p,), warning = CS.candidate_positions(b["rooms"][0], b)
    assert warning, "the room has no free floor"
    assert X.free_floor_problems(b, cam([p[0], p[1], 1.5])) == []


def test_a_room_with_free_floor_keeps_the_search_clearances():
    b = bathroom()
    room = b["rooms"][0]
    room["polygon"] = [[0.0, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]]
    b["walls"], b["openings"] = [], []
    sofa = dict(piece("f_1", "sofa", [2.5, 3.5], [2.0, 0.9], 180.0, 0.85), room_id=room["id"])
    plant = {"id": "dec_1", "room_id": room["id"], "type": "plant_large", "center": [1.0, 1.0], "size": [0.6, 0.6, 1.6]}
    b["furniture"], b["decor"] = [sofa], [plant]
    assert X.free_floor_problems(b, cam([2.5, 1.5, 1.4])) == []
    assert "from f_1" in X.free_floor_problems(b, cam([2.5, 2.95, 1.4]))[0]              # 0.1 m from the sofa
    assert "from floor decor" in X.free_floor_problems(b, cam([1.0, 1.4, 1.4]))[0]       # 0.1 m from the plant
    assert X.free_floor_problems(b, cam([2.5, 0.2, 1.4])) == []                          # 0.2 m from a wall
    assert "from a wall" in X.free_floor_problems(b, cam([2.5, 0.1, 1.4]))[0]


def test_a_high_view_that_looks_almost_straight_down_is_refused():
    """28 Oct 2026 (real06 run 154514: the agent's ext_4 at 18 m looked 56 degrees down onto the roof alone and rendered
    white): a high view (``HIGH_VIEW_ABOVE_RIDGE_M`` over the ridge) looks down at most ``HIGH_VIEW_MAX_DOWN_DEG``."""
    import math

    b = {"levels": [{"id": "L0", "elevation": 0.0}], "roof": {"ridge_z": 6.0}}
    steep = X.validate_camera_override(b, {"action": "set", "view_id": "ext_4", "kind": "exterior", "reason": "x",
                                           "position": [12.0, 1.6, 18.0], "target": [12.0, 10.0, 5.5]})
    down = math.degrees(math.atan2(12.5, 8.4))
    assert down > X.HIGH_VIEW_MAX_DOWN_DEG == 40.0
    assert any("degrees down" in f for f in steep["failed"]), steep
    bird = X.validate_camera_override(b, {"action": "set", "view_id": "ext_4", "kind": "exterior", "reason": "x",
                                          "position": [12.0, -14.0, 14.0], "target": [12.0, 10.0, 3.0]})
    assert not any("degrees down" in f for f in bird["failed"]), bird
