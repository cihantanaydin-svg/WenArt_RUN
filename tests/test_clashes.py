"""Furniture clashes planned apart before the build (wenart/blender/clashes.py; user note of 25 Oct 2026: "it's
unacceptable to see clashing furniture at this stage"). CPU, pure."""
import json
from pathlib import Path

from wenart.blender import clashes as C

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"
ROOM = [[0.0, 0.0], [8.0, 0.0], [8.0, 6.0], [0.0, 6.0]]


def _piece(pid, ptype, center, size, rot=0.0, source="from_documents", **kw):
    return dict({"id": pid, "type": ptype, "level_id": "L0", "room_id": "r", "source": source, "build": True,
                 "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot}}, **kw)


def _building(*pieces, decor=()):
    return {"levels": [{"id": "L0", "elevation": 0.0}], "walls": [], "openings": [],
            "rooms": [{"id": "r", "level_id": "L0", "room_type": "living", "polygon": ROOM}],
            "furniture": list(pieces), "decor": list(decor)}


def _clear(b):
    return not C.remaining([f for f in b["furniture"] if f.get("build") is not False])


def test_a_side_table_under_an_armchair_moves_out_and_its_tray_follows():
    arm = _piece("a", "armchair", (2.0, 2.0), (0.8, 0.8))
    table = _piece("t", "side_table", (2.5, 2.0), (0.5, 0.5))
    tray = {"id": "d", "type": "tray", "host_id": "t", "center": [2.5, 2.0, 0.5]}
    b = _building(arm, table, decor=[tray])
    out = C.resolve(b)
    assert [x["id"] for x in out["fixed"]] == ["t"] and out["fixed"][0]["action"] == "moved"
    assert arm["footprint"]["center"] == [2.0, 2.0]                       # the armchair stays
    assert table["drawn_footprint"]["center"] == [2.5, 2.0] and table["adjusted_by_ai"]["rule"] == "architect F5"
    assert abs(tray["center"][0] - table["footprint"]["center"][0]) < 1e-6 and _clear(b)


def test_a_chair_pushed_through_its_table_is_pulled_out_to_a_tucked_stand():
    table = _piece("t", "table_dining", (4.0, 3.0), (1.6, 0.9))
    chair = _piece("c", "chair", (4.0, 3.2), (0.45, 0.5), front_deg=270.0)  # its back through the table top
    tucked = _piece("k", "chair", (4.0, 2.45), (0.45, 0.5), front_deg=90.0)  # 0.2 m under: by design
    b = _building(table, chair, tucked)
    out = C.resolve(b)
    assert [x["id"] for x in out["fixed"]] == ["c"] and tucked["footprint"]["center"] == [4.0, 2.45]
    assert 0.25 < out["fixed"][0]["distance_m"] <= C.MAX_MOVE_M and _clear(b)


def test_one_cupboard_read_twice_is_built_once():
    wardrobe = _piece("w", "wardrobe", (3.0, 5.6), (2.1, 0.6))
    dresser = _piece("x", "dresser", (3.3, 5.6), (1.45, 0.6), type_raw="dolap")
    b = _building(wardrobe, dresser)
    out = C.resolve(b)
    assert dresser["build"] is False and "read twice" in dresser["not_built_reason"] and wardrobe.get("build")
    assert out["fixed"][0]["action"] == "not_built"


def test_a_bed_never_moves_for_a_lamp_and_a_lamp_with_no_place_is_not_built():
    room = [[0.0, 0.0], [2.2, 0.0], [2.2, 2.6], [0.0, 2.6]]
    bed = _piece("b", "bed_double", (1.1, 1.3), (2.2, 2.6))
    lamp = _piece("l", "floor_lamp", (1.8, 2.3), (0.4, 0.4))
    b = _building(bed, lamp)
    b["rooms"][0]["polygon"] = room
    out = C.resolve(b)
    assert bed["footprint"]["center"] == [1.1, 1.3] and lamp["build"] is False
    assert out["fixed"][0]["action"] == "not_built" and not out["left"]


def test_two_table_sets_back_to_back_move_as_units():
    """real04's L-1b bistro sets: a chair pulled out of its table met the next set's chair; the set moves as one."""
    t1 = _piece("t1", "table_dining", (3.0, 3.0), (0.7, 0.7))
    c1 = _piece("c1", "chair", (3.45, 3.0), (0.45, 0.5), rot=90.0, front_deg=180.0)
    t2 = _piece("t2", "table_dining", (4.35, 3.0), (0.7, 0.7))
    c2 = _piece("c2", "chair", (3.85, 3.0), (0.45, 0.5), rot=270.0, front_deg=0.0)
    b = _building(t1, c1, t2, c2)
    out = C.resolve(b)
    assert _clear(b) and not out["left"]
    assert any(len(x["members"]) > 1 for x in out["fixed"]) or all(x["action"] == "moved" for x in out["fixed"])


def test_an_l_sofa_is_its_two_parts():
    sofa = _piece("s", "sofa_corner", (4.0, 3.0), (3.0, 2.0), shape="L", chaise_side="right", chaise_width=0.9,
                  chaise_depth=2.0, seat_depth=0.9)
    in_corner = _piece("t", "table_coffee", (3.4, 2.45), (0.8, 0.5))        # the L's open corner: no clash
    assert C.shape_depth(C.shape(sofa), C.shape(in_corner)) == 0.0
    on_chaise = _piece("u", "side_table", (5.05, 2.3), (0.4, 0.4))          # on the chaise: a clash
    assert C.shape_depth(C.shape(sofa), C.shape(on_chaise)) > C.CLASH_TOL_M


def test_real04_has_no_clash_left_and_the_input_stays_as_it_was():
    from wenart.blender import build as BU

    b = json.loads(REAL04.read_text(encoding="utf-8"))
    before = json.dumps(b, sort_keys=True)
    for variant in ("base", "l-1b-acik-mutfak"):
        prep = BU.prepare(b, variant, None)
        assert prep["clashes"]["fixed"] and not prep["clashes"]["left"], prep["clashes"]["left"]
        built = [f for f in prep["building"]["furniture"] if f.get("build") is not False
                 and str(f.get("type")) not in C.SKIP_TYPES + C.FLOOR_ONLY and f.get("footprint")]
        for lid in {f.get("level_id") for f in built}:
            assert not C.remaining([f for f in built if f.get("level_id") == lid])
    assert json.dumps(b, sort_keys=True) == before
    f5 = next(q for q in BU.prepare(b, "base", None)["architect"]["questions"] if q["id"] == "F5")
    assert f5["counts"]["changed"] > 0 and f5["counts"]["open"] == 0
