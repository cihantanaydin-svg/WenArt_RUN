"""Camera points keep away from free-standing floor decor (pod P5, 11 Oct 2026, ``camsearch.floor_decor_rects``):
real03's ``cam_r_L0_yasama_7_1`` stood inside the 1.6 m plant ``dec_L0_071`` (the depth pass read 0.05 m at the
lens; the view was a wall of leaves)."""
import math

from wenart.blender import camsearch as CS

EV = [{"file": "sheet.dxf", "page": 1, "method": "vector", "confidence": 1.0}]


def building(decor):
    room = {"id": "r_1", "level_id": "L0", "label": "Salon", "room_type": "living",
            "polygon": [[0.0, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]], "status": "verified", "evidence": EV}
    sofa = {"id": "f_1", "room_id": "r_1", "level_id": "L0", "type": "sofa", "source": "added_by_ai",
            "footprint": {"center": [2.5, 3.5], "size": [2.0, 0.9], "rotation_deg": 180.0}, "height": 0.85}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [room], "walls": [],
            "openings": [], "furniture": [sofa], "decor": decor}


def test_a_floor_plant_keeps_the_camera_points_away():
    plant = {"id": "dec_1", "room_id": "r_1", "type": "plant_large", "center": [0.5, 0.5], "size": [0.6, 0.6, 1.6]}
    before, _ = CS.candidate_positions(building([])["rooms"][0], building([]))
    after, _ = CS.candidate_positions(building([plant])["rooms"][0], building([plant]))
    near = [p for p in before if math.dist(p, (0.5, 0.5)) < 0.3]
    assert near, "the free room has a camera point at the plant's place"
    assert all(math.dist(p, (0.5, 0.5)) >= 0.3 for p in after)
    assert set(after) < set(before)


def test_hosted_and_hanging_decor_are_no_floor_obstacles():
    hosted = {"id": "dec_2", "room_id": "r_1", "host_id": "f_1", "type": "cushion", "center": [0.5, 0.5],
              "size": [0.5, 0.15, 0.5]}
    pendant = {"id": "dec_3", "room_id": "r_1", "type": "pendant_light", "center": [0.5, 0.5, 2.0],
               "size": [0.45, 0.45, 0.7]}
    curtain = {"id": "dec_4", "room_id": "r_1", "type": "curtain", "center": [2.0, 0.05, 0.01],
               "size": [2.0, 0.08, 2.24]}
    rects = CS.floor_decor_rects(building([])["rooms"][0], building([hosted, pendant, curtain]))
    assert rects == [{"center": [2.0, 0.05], "size": [2.0, 0.08], "rotation_deg": 0.0}]
