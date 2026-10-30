"""UL190 (30 Oct 2026, real04 run 20261030-112241-full): "mirror staying behind the door in this case door can be closed":
a round mirror on the wall the open leaf rests against. A wall-hung item and a strip of wall in front of it are in the
way of an open leaf: the door opens otherwise or stays closed. Pure tests on the hand-made house of the doors tests."""
import test_doors_open_20261029 as T
from wenart.blender import door_states as DS


def test_an_open_leaf_never_rests_over_a_mirror():
    b = T._house()
    free = DS.plan_states(b, T.SCANDI)["d_bed"]
    leaf = free["leaf_polys"][0]
    xs, ys = [p[0] for p in leaf], [p[1] for p in leaf]
    level = next(o for o in b["openings"] if o["id"] == "d_bed").get("level_id", "L0")
    wall_y = min(ys) - 0.055                                         # the wall face the open leaf lies along
    mirror = {"id": "dec_m", "type": "mirror", "level_id": level, "room_id": free["into"], "host_id": None,
              "wall_point": [sum(xs) / 4.0, wall_y], "center": [sum(xs) / 4.0, wall_y + 0.02],
              "size": [0.6, 0.04], "rotation_deg": 0.0}
    b["decor"].append(mirror)
    poly = DS.wall_hung_polys(b, level)[0][2]
    assert DS.overlap(leaf, poly) > DS.HIT_M2                        # the leaf as it stood covered the mirror
    rec = DS.plan_states(b, T.SCANDI)["d_bed"]
    assert all(DS.overlap(p, poly) <= DS.HIT_M2 for p in rec.get("leaf_polys") or [])
    assert rec["state"] == "closed" or rec["leaf_polys"] != free["leaf_polys"]
    assert "mirror" in DS.WALL_HUNG_TYPES and "wall_art" in DS.WALL_HUNG_TYPES
