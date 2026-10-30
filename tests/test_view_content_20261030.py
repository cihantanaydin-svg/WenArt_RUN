"""UL185 (30 Oct 2026, real04 run 20261030-112241-full cam_r_L1_banyo_1, an Argus pose): "This render not needed not
giving any value": tiles, the sloped ceiling and the bathtub's rim, 4 % of the frame furniture. A pose holds at least
``camsearch.CONTENT_MIN_SHARE`` of furniture and fixtures when its room's camera search frames that much; the fallback
pose does too. Pure tests on a hand-made bathroom; real04 is only the test case."""
import _m11_room as M
from wenart.blender import camsearch as CS
from wenart.blender import exterior_checks as X


def _bathroom():
    pieces = [M.fp("t1", "toilet", (0.45, 3.6), (0.4, 0.6), rotation=180.0),
              M.fp("w1", "washbasin", (1.4, 3.75), (0.6, 0.45), rotation=180.0),
              M.fp("b1", "bathtub", (2.6, 3.6), (1.7, 0.75), rotation=180.0)]
    return M.building(w=3.5, h=4.0, room_type="bathroom", furniture=pieces, window=None)


def test_a_pose_at_a_bare_wall_fails_the_content_rule_and_the_fallback_has_content():
    b = _bathroom()
    bare = {"name": "cam_bare", "room_id": M.ROOM_ID, "position": [1.75, 2.6, 1.25], "target": [1.75, 1.6, 1.25],
            "lens_mm": 18.0}                                     # facing the empty south half and its door wall
    rules = [p["rule"] for p in CS.pose_problems(b, bare)]
    assert "content" in rules
    good = dict(bare, name="cam_good", position=[1.75, 0.8, 1.25], target=[1.75, 1.8, 1.25])
    assert "content" not in [p["rule"] for p in CS.pose_problems(b, good)]
    alt = CS.nearest_searched_pose(b, bare)
    assert alt is not None and not [p for p in CS.pose_problems(b, dict(bare, **{k: alt[k] for k in (
        "position", "target")})) if p["rule"] == "content"]
    assert "content" in CS.POSE_RULES and "content" in X.INTERIOR_POSE_RULES and 0.08 < CS.CONTENT_MIN_SHARE <= 0.15
