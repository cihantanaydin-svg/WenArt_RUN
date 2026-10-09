"""Milestone 11 ingest changes (docs/milestone11.md §1.2 M8, decision D4, §6): a face the stair fills is a stair
room, the room area label is compared with the polygon minus its stair opening at 8 %, the inference runs only on
pieces whose AI answers are in, and the recognition answers follow their crops when a split renumbers the keys."""
import json
from types import SimpleNamespace

import pytest

from wenart import building as B
from wenart.ingest import pipeline as PL
from wenart.ingest import rooms as R
from wenart.ingest.generic import topology as TP
from wenart.ingest.model import WallItem
from wenart.recognition import answers as A


def square_walls(size=4.5):
    pts = [(0, 0), (size, 0), (size, size), (0, size)]
    return [WallItem(start=pts[i], end=pts[(i + 1) % 4], thickness=0.2, box=[], entity=f"w{i}",
                     evidence=B.evidence("x.dxf", "vector", 1.0)) for i in range(4)]


def stair(center, size, rotation=0.0):
    return {"type": "stair", "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation}}


# --------------------------------------------------------------------------
# M8: stair rooms
# --------------------------------------------------------------------------

def test_a_face_the_stair_fills_is_a_stair_room():
    face = [(0, 0), (2.8, 0), (2.8, 2.2), (0, 2.2)]
    assert TP.stair_fill(face, [stair((1.4, 1.1), (2.7, 2.1))]) == pytest.approx(0.92, abs=0.01)
    assert TP.stair_room_label(face, [stair((1.4, 1.1), (2.7, 2.1))]) == "Merdiven"
    assert TP.stair_room_label(face, [stair((1.4, 1.1), (2.7, 2.1))], turkish=False) == "Stair"
    big = [(0, 0), (6, 0), (6, 4), (0, 4)]
    assert TP.stair_room_label(big, [stair((1.4, 1.1), (2.7, 2.1))]) is None          # a hall with a stair in it


def test_derive_rooms_names_the_unlabelled_stair_core():
    def face_type(poly):
        return "hall", "unlabelled face holding the stair", "Merdiven"

    result = R.derive_rooms("L0", square_walls(), [], [], None, "x.dxf", face_type=face_type)
    room = result.rooms[0]
    assert room["label"] == "Merdiven" and room["room_type"] == "hall" and room["id"] == "r_L0_merdiven"
    assert room["status"] == "unverified" and room["label_raw"] is None
    # Without a label the M10 placeholder stays.
    plain = R.derive_rooms("L0", square_walls(), [], [], None, "x.dxf", face_type=lambda p: ("hall", "two doors"))
    assert plain.rooms[0]["label"] == "Oda"


# --------------------------------------------------------------------------
# D4: area label vs polygon minus the stair opening, 8 %
# --------------------------------------------------------------------------

def _check(label_area, polygon, furniture):
    from wenart import geometry as G

    build = PL.ProjectBuild(B.empty_building("p", "projects/p", "c"))
    room = {"id": "r_L0_koridor", "polygon": polygon, "area_computed": round(G.polygon_area(polygon), 3),
            "area_label": label_area, "status": "verified"}
    master = SimpleNamespace(record=SimpleNamespace(file="plan.dwg"))
    PL._check_areas(build, [room], master, furniture)
    return room, build.raw_conflicts


def test_area_label_is_compared_with_the_polygon_minus_its_stair():
    # real02: "Koridor 7 m²" on a 11.9 m² face that holds a 4.9 m² stair.
    poly = [[0, 0], [4.0, 0], [4.0, 2.975], [0, 2.975]]                        # 11.9 m²
    furniture = [dict(stair((1.4, 1.1), (2.7, 1.778)), room_id="r_L0_koridor")]   # 4.8 m²: 7.1 m² left
    room, conflicts = _check(7.0, poly, furniture)
    assert room["status"] == "verified"
    assert "minus the stair" in conflicts[0]["description"] and "within tolerance (8%)" in conflicts[0]["resolution"]
    room, conflicts = _check(7.0, poly, [])
    assert room["status"] == "unverified" and "over 8%" in conflicts[0]["resolution"]


def test_area_tolerance_is_8_percent():
    poly = [[0, 0], [5.0, 0], [5.0, 4.9], [0, 4.9]]                            # 24.5 m²
    room, _ = _check(26.0, poly, [])                                           # 6.1 %: unverified at 3 % before
    assert room["status"] == "verified"
    room, _ = _check(27.0, poly, [])                                           # 10.2 %
    assert room["status"] == "unverified"


# --------------------------------------------------------------------------
# Answers follow their crops
# --------------------------------------------------------------------------

def test_an_answer_follows_its_crop_to_a_new_key(tmp_path):
    key = A.MODEL_KEYS[0]
    models = {k: {"id": f"m{i}", "slug": f"m{i}"} for i, k in enumerate(A.MODEL_KEYS)}
    store = A.AnswerStore.for_model(tmp_path, key, models)
    item_old = {"key": "sym_L0_005", "task": "room_label", "input_sha256": "abc"}
    data = {"label": "Salon", "size_text": None, "area_text": None, "box": None}
    assert A.valid_answer("room_label", data)
    store.put("sym_L0_005", {"input_sha256": "abc", "model": "m0", "data": data})
    assert store.valid(item_old) is not None
    item_new = dict(item_old, key="sym_L0_004")                     # a split took a candidate away before it
    assert store.valid(item_new) is not None
    assert A.item_state(store, item_new) == "answered"
    assert store.valid(dict(item_new, input_sha256="other")) is None
