"""The build turns every piece by its front (29 Oct 2026, real06 run 100801: a dressing room wardrobe stood with its
back to the room; the fit had turned it to face the room, ``front_deg`` 180, and kept its drawn footprint, rotation 90,
and the build turned the model by the rotation alone)."""
from wenart import geometry as G
from wenart.blender.build import front_framed, furniture_building
from wenart.furniture import placer

WARDROBE = {"id": "f_L1_011", "type": "wardrobe", "front_deg": 180.0,
            "footprint": {"center": [8.1, 7.9947], "size": [2.2745, 0.6], "rotation_deg": 90.0}}


def test_a_piece_turned_by_the_fit_is_built_facing_its_front():
    got = front_framed(WARDROBE)
    assert got["footprint"]["rotation_deg"] == 270.0 and got["footprint"]["size"] == [2.2745, 0.6]
    assert G.front_direction_deg(got["footprint"]["rotation_deg"]) == 180.0      # the model's -Y faces the room
    assert got["footprint_drawn"] == WARDROBE["footprint"]                        # the drawn record rides along
    assert WARDROBE["footprint"]["rotation_deg"] == 90.0                          # the input is not changed


def test_a_quarter_turn_swaps_the_size_and_keeps_the_rectangle():
    piece = dict(WARDROBE, front_deg=90.0)
    got = front_framed(piece)
    assert got["footprint"]["size"] == [0.6, 2.2745] and got["footprint"]["rotation_deg"] == 180.0
    rot, size = placer.front_frame(WARDROBE["footprint"], 90.0)
    assert (rot, size) == (180.0, (0.6, 2.2745))
    before = G.rotated_rectangle(WARDROBE["footprint"]["center"], WARDROBE["footprint"]["size"], 90.0)
    after = G.rotated_rectangle(got["footprint"]["center"], got["footprint"]["size"], 180.0)
    assert sorted((round(x, 6), round(y, 6)) for x, y in before) == \
        sorted((round(x, 6), round(y, 6)) for x, y in after)


def test_a_piece_in_its_front_frame_or_without_a_front_is_kept():
    same = dict(WARDROBE, front_deg=0.0)
    assert front_framed(same) is same
    bare = {k: v for k, v in WARDROBE.items() if k != "front_deg"}
    assert front_framed(bare) is bare


def test_the_build_furniture_is_front_framed():
    built = furniture_building({"furniture": [WARDROBE, dict(WARDROBE, id="f2", front_deg=0.0)]})
    assert [p["footprint"]["rotation_deg"] for p in built["furniture"]] == [270.0, 90.0]


def test_argus_c8_names_a_piece_built_facing_another_way():
    from wenart.audit import conservation as C

    final = {"furniture": [WARDROBE]}
    turned = {"objects": [{"kind": "furniture", "wenart_id": "f_L1_011", "rotation_deg": 90.0}]}
    found = C.turned_in_build(final, turned)
    assert [(f["check"], f["severity"], f["kind"], f["target"]) for f in found] == \
        [("C8", "major", "geometry", "f_L1_011")]
    assert found[0]["evidence"]["built_front_deg"] == 0.0
    right = {"objects": [{"kind": "furniture", "wenart_id": "f_L1_011", "rotation_deg": 270.0}]}
    assert C.turned_in_build(final, right) == []
    assert C.audit([("final", final)], turned)["counts"]["C8"] == 1
