"""29 Oct 2026 (user on real06 run 20261028-154514-full: "I am not understanding this scene is there a door behind it?"):
one wall read twice is one wall (``wenart.ingest.generic.twin_walls``); a column or a pier in a wall is no copy."""
from __future__ import annotations

from wenart.ingest.generic import twin_walls as TW


def _wall(wid, a, b, t):
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "evidence": []}


def _b():
    return {"walls": [_wall("w_9", (0.45, 9.2), (4.6, 9.2), 0.3), _wall("w_10", (0.95, 9.225), (3.85, 9.225), 0.25),
                      _wall("w_col", (2.0, 9.21), (2.4, 9.21), 0.5)],
            "openings": [{"id": "o_1", "type": "opening", "level_id": "L0", "wall_id": "w_9", "center": [1.9, 9.2],
                          "width": 1.9},
                         {"id": "d_2", "type": "door", "level_id": "L0", "wall_id": "w_10", "center": [2.275, 9.225],
                          "width": 1.95},
                         {"id": "d_3", "type": "door", "level_id": "L0", "wall_id": "w_10", "center": [3.5, 9.225],
                          "width": 0.3}],
            "furniture": [{"id": "f_1", "counter_run": {"wall_id": "w_10"}}]}


def test_one_wall_read_twice_is_one_wall_with_its_openings():
    b = _b()
    assert TW.twin_of(b["walls"][0], b["walls"][1]) and not TW.twin_of(b["walls"][0], _wall("w_x", (0, 10), (4, 10), 0.3))
    got = TW.merge_twin_walls(b)
    assert got == ["w_10"] and [w["id"] for w in b["walls"]] == ["w_9", "w_col"]     # the column block stays
    assert [o["id"] for o in b["openings"]] == ["o_1", "d_3"]
    assert b["openings_merged"][0]["id"] == "d_2" and b["openings_merged"][0]["merged_into"] == "o_1"
    moved = b["openings"][1]
    assert moved["wall_id"] == "w_9" and moved["center"] == [3.5, 9.2] and moved["corrected_by_ai"]["rule"] == TW.RULE
    assert b["furniture"][0]["counter_run"]["wall_id"] == "w_9"
    assert b["walls_merged"][0]["merged_into"] == "w_9" and "read twice" in b["walls_merged"][0]["corrected_by_ai"]["reason"]


def test_two_walls_side_by_side_are_two_walls():
    b = {"walls": [_wall("a", (0, 0), (4, 0), 0.2), _wall("b", (0, 0.3), (4, 0.3), 0.2)], "openings": []}
    assert TW.merge_twin_walls(b) == [] and len(b["walls"]) == 2
