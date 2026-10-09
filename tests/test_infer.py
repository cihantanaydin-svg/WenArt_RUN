"""Type inference for unclear drawn pieces (docs/milestone11.md §6, CLAUDE.md "never an unexplained box";
wenart/furniture/infer.py) and the twin copies of the ingest (U16; wenart/ingest/twins.py)."""
import json

import pytest

import _m11_room as M
from wenart.furniture import infer as INF
from wenart.ingest import twins as TW


def unknown(pid, center, size, rotation=0.0, **kw):
    return M.fp(pid, "unknown", center, size, rotation=rotation, front=None, status="unverified",
                type_method="none", **kw)


def test_an_outline_around_other_pieces_is_a_rug_and_not_built():
    sofa = M.fp("s1", "sofa", (2.5, 0.47), (2.2, 0.9), rotation=180.0, front=90.0)
    table = M.fp("t1", "table_coffee", (2.5, 1.8), (1.0, 0.6), front=None)
    rug = unknown("u1", (2.5, 1.7), (3.0, 2.2))
    b = M.building(room_type="living", furniture=[sofa, table, rug])
    before = json.dumps(b, sort_keys=True)
    props = INF.infer_types(b)
    assert json.dumps(b, sort_keys=True) == before
    assert [(p["piece_id"], p["type"], p.get("build")) for p in props] == [("u1", "rug", False)]
    out = INF.apply_inferences(b, props)
    u1 = next(f for f in out["furniture"] if f["id"] == "u1")
    assert u1["build"] is False and u1["inferred"] is True and u1["inferred_as"] == "rug"
    assert u1["type"] == "unknown" and u1["evidence"][-1]["method"] == "inferred"


def test_an_outline_around_fixed_equipment_is_no_rug():
    sink = M.fp("k1", "sink_kitchen", (2.5, 3.65), (0.8, 0.5), front=270.0)
    run = unknown("u1", (2.5, 3.4), (3.0, 1.2))
    assert INF.infer_types(M.building(room_type="kitchen", furniture=[sink, run])) == []


def test_one_type_by_size_room_and_position_gets_that_type_and_a_front():
    # A 2.4 x 0.6 m box against the north wall of a bedroom: only a wardrobe has that size there.
    box = unknown("u1", (2.5, 3.68), (2.4, 0.6))
    props = INF.infer_types(M.building(furniture=[box]))
    assert [(p["piece_id"], p["type"]) for p in props] == [("u1", "wardrobe")]
    assert props[0]["confidence"] == INF.CONF_ONE and props[0]["front_deg"] == 270.0
    out = INF.apply_inferences(M.building(furniture=[box]), props)
    u1 = next(f for f in out["furniture"] if f["id"] == "u1")
    assert u1["type"] == "wardrobe" and u1["front_deg"] == 270.0 and u1["inferred"] is True
    assert u1["evidence"][-1]["method"] == "inferred" and u1["status"] == "unverified"
    # A 0.45 x 0.40 m box beside a bed: nightstand, side table or ottoman: nothing is guessed.
    bed = M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)
    small = unknown("u2", (0.22, 3.3), (0.4, 0.45), rotation=90.0)
    assert INF.infer_types(M.building(furniture=[bed, small])) == []


def test_a_part_drawn_inside_a_typed_piece_is_a_detail():
    # real02: the sink bowls inside the counter legs, one AI pass said bar stool.
    counter = M.fp("k1", "kitchen_counter", (2.5, 3.68), (2.4, 0.6), front=270.0)
    bowl = unknown("u1", (2.5, 3.7), (0.44, 0.35), type_candidates=[{"type": "bar_stool", "pass": 1}])
    props = INF.infer_types(M.building(room_type="kitchen", furniture=[counter, bowl]))
    assert [(p["piece_id"], p["type"], p["build"]) for p in props] == [("u1", "detail", False)]


def test_ambiguous_pieces_stay_unknown():
    # A 0.8 m square in a living room: armchair, ottoman, coffee table ... several types fit: nothing is guessed.
    box = unknown("u1", (2.5, 2.0), (0.8, 0.8))
    assert INF.infer_types(M.building(room_type="living", furniture=[box])) == []
    # Two AI passes named different fitting types (kitchen_island / sofa): ambiguous.
    sofa_or_island = unknown("u2", (2.5, 2.0), (2.1, 0.9), type_candidates=[{"type": "kitchen_island", "pass": 1},
                                                                            {"type": "sofa", "pass": 2}])
    b = M.building(room_type="kitchen", furniture=[sofa_or_island])
    b["conflicts"] = [{"kind": "other", "element_ids": [M.ROOM_ID],
                       "description": f"{M.ROOM_ID}: one face holds the room names 'Mutfak' and 'SALON'"}]
    assert INF.infer_types(b) == []


def test_one_ai_named_type_that_fits_is_taken_when_no_rival_fits():
    bench = unknown("u1", (2.5, 0.32), (1.5, 0.6), type_candidates=[{"type": "unknown", "pass": 1},
                                                                    {"type": "bench", "pass": 2}])
    props = INF.infer_types(M.building(room_type="hall", furniture=[bench]))
    assert [(p["type"], p["confidence"]) for p in props] == [("bench", INF.CONF_NAMED)]


def _twins(second_type="unknown", second_front=None, second_method="none"):
    rooms = [{"id": "r_a", "level_id": "L0", "label": "Koridor", "label_raw": "KORIDOR",
              "polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]},
             {"id": "r_b", "level_id": "L0", "label": "Koridor", "label_raw": "KORIDOR",
              "polygon": [[4, 0], [7, 0], [7, 2], [4, 2]]}]
    furniture = [
        {"id": "f1", "level_id": "L0", "room_id": "r_a", "type": "bench", "source": "from_documents",
         "type_method": "ai_two_pass", "footprint": {"center": [1.0, 0.3], "size": [1.5, 0.4], "rotation_deg": 0.0},
         "front_deg": 270.0, "evidence": [{"file": "p.dwg", "method": "vector", "confidence": 1.0}]},
        {"id": "f2", "level_id": "L0", "room_id": "r_b", "type": second_type, "source": "from_documents",
         "type_method": second_method, "footprint": {"center": [6.0, 0.3], "size": [0.4, 1.5], "rotation_deg": 90.0},
         "front_deg": second_front, "evidence": [{"file": "p.dwg", "method": "vector", "confidence": 1.0}]}]
    return rooms, furniture


def test_twins_pair_although_one_piece_is_untyped_and_the_second_takes_the_agreed_type():
    # M7: real02's L1 corridor twins were not paired because one bench was untyped (U16).
    rooms, furniture = _twins()
    info = TW.twin_transforms(rooms, [], furniture)
    assert set(info) == {"r_b"}
    rooms[1].update(twin_of="r_a", twin_transform=info["r_b"]["transform"])
    copies = TW.twin_copies(rooms, furniture)
    assert [(c["piece_id"], c["type"], c["front_deg"]) for c in copies] == [("f2", "bench", 270.0)]
    lines = TW.apply_twin_copies(furniture, copies)
    f2 = furniture[1]
    assert f2["type"] == "bench" and f2["front_deg"] == 270.0 and f2["inferred"] is True
    assert f2["footprint"]["size"] == [1.5, 0.4] and f2["footprint"]["center"] == [6.0, 0.3]
    assert f2["evidence"][-1]["method"] == "inferred" and "f1" in lines[0]


def test_twins_with_two_different_agreed_types_stay_apart():
    rooms, furniture = _twins(second_type="console_table", second_method="ai_two_pass")
    assert TW.twin_transforms(rooms, [], furniture) == {}


def test_a_twin_without_a_front_takes_the_mirrored_front():
    rooms, furniture = _twins(second_type="bench", second_method="ai_two_pass")
    furniture[0]["front_deg"] = 0.0                        # facing east in r_a ...
    info = TW.twin_transforms(rooms, [], furniture)
    rooms[1].update(twin_of="r_a", twin_transform=info["r_b"]["transform"])
    copies = TW.twin_copies(rooms, furniture)
    assert [(c["piece_id"], c["front_deg"]) for c in copies] == [("f2", 180.0)]   # ... west in the mirror


def test_unlabelled_twin_faces_pair_too():
    rooms, furniture = _twins()
    for r in rooms:
        r.update(label="Oda", label_raw=None)
    furniture[1]["type"] = "bench"
    assert set(TW.twin_transforms(rooms, [], furniture)) == {"r_b"}
