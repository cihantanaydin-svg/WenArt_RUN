"""real02 regression of the Milestone 11 layout engine (docs/milestone11.md §10 "real02 regression"): the code
critic (plausibility) finds the known problems of §1.2 in the committed ``results/furniture/real02/
building_final.json`` (pod F1b, before the step 0 fixes), the scripted edits raise the room scores, and invalid
edits are rejected with the failed checks."""
import json
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.furniture import edit_ops as E
from wenart.furniture import plausibility as PL

PATH = Path(__file__).resolve().parents[1] / "results" / "furniture" / "real02" / "building_final.json"
pytestmark = pytest.mark.skipif(not PATH.is_file(), reason="results/furniture/real02 not committed")
META = {"round": 1, "model": "scripted"}


@pytest.fixture(scope="module")
def building():
    return json.loads(PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def critic(building):
    return PL.score_building(building)


def violations(critic, room_id, check=None, target=None):
    return [v for v in critic["rooms"][room_id]["violations"]
            if (check is None or v["check"] == check) and (target is None or v["target"] == target)]


def test_the_critic_finds_the_known_problems(critic):
    print("\n" + "\n".join(PL.summary_lines(critic)[:12]))
    # U3: the master bed stands with its headboard in the room (no drawn front: the builder faced it east).
    bed = violations(critic, "r_L0_e_yatak_odasi", "F3", "f_L0_009")
    assert bed and bed[0]["severity"] == "critical"
    # U7: the added dining chairs face away from the table.
    chairs = {v["target"] for v in violations(critic, "r_L-1_salon", "F4")}
    assert {"f_L-1_054", "f_L-1_055", "f_L-1_058"} <= chairs
    # U13: the added armchair stands behind the sofa's back, looking at it.
    arm = violations(critic, "r_L1_oyun_aktivite_ve_dinlenme_odasi", "F4", "f_L1_029")
    assert arm and "behind the back" in arm[0]["message"]
    # U4: wardrobes face the wall.
    assert violations(critic, "r_L0_yatak_odasi_3", "F4", "f_L0_011")
    # U10: the 3.35 x 1.57 m "table" is no real table size; U12: a kitchen counter in a bedroom.
    assert violations(critic, "r_L-1_salon", "F2", "f_L-1_011")
    assert [v["severity"] for v in violations(critic, "r_L0_e_yatak_odasi", "F1", "f_L0_003")] == ["major"]
    # U17 / U8 / U9: the unexplained striped boxes (56 built unknown drawn pieces), the large ones major.
    boxes = [v for r in critic["rooms"].values() for v in r["violations"]
             if v["check"] == "F9" and "unexplained" in v["message"]]
    assert len(boxes) >= 50
    assert {v["target"] for v in boxes if v["severity"] == "major"} >= {"f_L-1_001", "f_L1_003"}
    # M11 pod G1: a door blocked on one hinge side only is minor (test_plausibility), so fewer criticals than at
    # the merge (12); the reversed master bed and the other real problems stay.
    assert critic["counts"]["critical"] >= 2 and critic["mean"] < 70


def test_scripted_edits_raise_the_scores(building):
    b = building
    steps = [
        # The twin bedroom's bed faces the wall (U5): turn it so the headboard is on the wall.
        ("r_L0_yatak_odasi_2", {"op": "rotate_piece", "piece_id": "f_L0_022", "front_deg": 180,
                                "reason": "headboard on the wall, foot to the room"}),
        # The wardrobe faces the wall (U4).
        ("r_L0_yatak_odasi_3", {"op": "rotate_piece", "piece_id": "f_L0_011", "front_deg": 90,
                                "reason": "doors to the room"}),
        # The master bed with its headboard in the room (U3): the pillows are at the east wall.
        ("r_L0_e_yatak_odasi", {"op": "rotate_piece", "piece_id": "f_L0_009", "front_deg": 180,
                                "reason": "the pillows and lamps are at the east wall"}),
        # An added dining chair faces away from the table (U7).
        ("r_L-1_salon", {"op": "rotate_piece", "piece_id": "f_L-1_054", "front_deg": 0,
                         "reason": "face the dining table"}),
    ]
    for k, (room_id, edit) in enumerate(steps, start=1):
        res = E.apply_edit(b, dict(edit, log_seq=k, **META))
        assert res["accepted"], (edit, res["failed_checks"])
        assert res["penalty_after"] < res["penalty_before"], edit
        assert res["score_after"] >= res["score_before"]
        b = res["building"]
    first = E.apply_edit(building, dict(steps[0][1], log_seq=1, **META))
    assert first["score_after"] > first["score_before"] + 20
    # A floating added armchair (F8) goes onto the nearest wall of its room.
    arm = next(f for f in b["furniture"] if f["id"] == "f_L-1b_041")
    wall = _nearest_wall(b, arm)
    res = E.apply_edit(b, dict({"op": "move_piece", "piece_id": "f_L-1b_041", "snap_wall_id": wall["id"],
                                "reason": "against the wall, not alone in the room", "log_seq": 9}, **META))
    assert res["accepted"], res["failed_checks"]
    assert res["score_after"] > res["score_before"]
    assert not [v for v in PL.score_room(res["building"], "r_L-1b_oda")["violations"]
                if v["target"] == "f_L-1b_041" and v["check"] == "F8"]
    # The originals are untouched and the drawn pieces carry their drawn values.
    bed = next(f for f in b["furniture"] if f["id"] == "f_L0_022")
    assert bed["adjusted_by_ai"]["round"] == 1 and bed["drawn_front_deg"] is None and bed["front_deg"] == 180.0
    assert next(f for f in building["furniture"] if f["id"] == "f_L0_022").get("adjusted_by_ai") is None


def test_invalid_edits_are_rejected_with_the_failed_checks(building):
    into_wall = E.apply_edit(building, dict({"op": "move_piece", "piece_id": "f_L-1b_041", "center": [3.3, 9.0],
                                             "reason": "into the wall"}, **META))
    assert not into_wall["accepted"] and "f_L-1b_041: inside_room" in into_wall["failed_checks"]
    on_door = E.apply_edit(building, dict({"op": "move_piece", "piece_id": "f_L-1b_041", "center": [2.7, 8.25],
                                           "reason": "in front of the door"}, **META))
    assert not on_door["accepted"] and "f_L-1b_041: doors_free" in on_door["failed_checks"]
    fixed = E.apply_edit(building, dict({"op": "move_piece", "piece_id": "f_L0_005", "center": [2.0, 9.0],
                                         "reason": "move a washbasin"}, **META))
    assert not fixed["accepted"]


def _nearest_wall(b, item):
    c = item["footprint"]["center"]
    walls = [w for w in b["walls"] if w["level_id"] == item["level_id"]]
    return min(walls, key=lambda w: G.point_segment_distance(c, w["start"], w["end"]))
