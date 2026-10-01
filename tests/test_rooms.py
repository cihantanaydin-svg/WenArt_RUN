"""Room derivation (wenart/ingest/rooms.py): walls -> union -> faces -> labelled rooms."""
import pytest

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import rooms as R
from wenart.ingest.dxf_extract import extract_dxf
from wenart.ingest.model import TextItem, WallItem
from wenart.ingest.pdf_extract import extract_pdf_page

from conftest import PROJECTS, load_truth

CASES = [("synthetic-01", "zemin_kat.dxf", 1, "L0"), ("synthetic-03", "mobilya_plani.dxf", 1, "L0"),
         ("synthetic-01", "1_kat.pdf", 1, "L1"), ("synthetic-03", "kat_planlari.pdf", 1, "L-1"),
         ("synthetic-03", "kat_planlari.pdf", 2, "L0"), ("synthetic-03", "kat_planlari.pdf", 3, "L1"),
         ("synthetic-02", "truth/plan.pdf", 1, "L0")]


def extraction(name, file, number, level_id):
    if file.endswith(".dxf"):
        return extract_dxf(PROJECTS / name / file, level_id, file)
    return extract_pdf_page(PROJECTS / name / file, number, level_id, file)


def label_points(ex):
    anchors = [G.apply_affine(ex.transform_to_building, t.start) for t in ex.labels]
    centres = [G.apply_affine(ex.transform_to_building, G.box_center(t.box)) for t in ex.labels]
    return anchors, centres


@pytest.mark.parametrize("name, file, number, level_id", CASES, ids=[f"{c[1]}-p{c[2]}" for c in CASES])
def test_rooms_match_truth(name, file, number, level_id):
    ex = extraction(name, file, number, level_id)
    anchors, centres = label_points(ex)
    result = R.derive_rooms(level_id, ex.walls, ex.labels, anchors, centres, file)
    truth_rooms = [r for r in load_truth(name)["rooms"] if r["level_id"] == level_id]
    assert result.closed and result.warnings == [] and result.unplaced_labels == []
    assert [r["id"] for r in result.rooms] == [r["id"] for r in truth_rooms]
    for room, expected in zip(result.rooms, truth_rooms):
        assert room["label"] == expected["label"] and room["room_type"] == expected["room_type"]
        assert room["label_raw"] == expected["label_raw"] and room["area_label"] == expected["area_label"]
        assert abs(room["area_computed"] - expected["area_computed"]) <= 0.01 * expected["area_computed"]
        assert len(room["polygon"]) == len(expected["polygon"])
        assert max(G.distance(a, b) for a, b in zip(room["polygon"], expected["polygon"])) < 0.005
        assert room["status"] == "verified" and room["evidence"][0]["text"] == expected["label_raw"]
        derived = next(e for e in expected["evidence"] if e["method"] == "derived")
        assert len(result.room_walls[room["id"]]) == len(derived["entity"].split(":", 1)[1].split(","))
    # The four outer walls are exterior, the inner walls are not.
    assert [w.exterior for w in ex.walls] == [True] * 4 + [False] * (len(ex.walls) - 4)
    assert R.outer_walls_closed(ex.walls)


def square_walls(size=5.0, t=0.25):
    h = t / 2
    return [WallItem((0.0, h), (size, h), t, [0, 0, 0, 0], "a", B.evidence("x.dxf", "vector", 1.0, entity="a")),
            WallItem((size - h, 0.0), (size - h, size), t, [0, 0, 0, 0], "b", B.evidence("x.dxf", "vector", 1.0, entity="b")),
            WallItem((0.0, size - h), (size, size - h), t, [0, 0, 0, 0], "c", B.evidence("x.dxf", "vector", 1.0, entity="c")),
            WallItem((h, 0.0), (h, size), t, [0, 0, 0, 0], "d", B.evidence("x.dxf", "vector", 1.0, entity="d"))]


def label(text, at, entity="TEXT:1"):
    return TextItem(text, at, [at[0], at[1], at[0] + 1, at[1] + 0.2], 0.0, entity, 0.2, role="room_label",
                    evidence=B.evidence("x.dxf", "vector", 1.0, entity=entity, text=text))


def test_unclosed_outer_walls():
    walls = square_walls()[:3]  # left wall missing
    assert not R.outer_walls_closed(walls)
    result = R.derive_rooms("L0", walls, [label("SALON", (1, 1))], [(1, 1)], None, "x.dxf")
    assert not result.closed and result.rooms == []
    assert any("closed loop" in w or "no enclosed room" in w for w in result.warnings)


def test_room_without_label_is_unverified():
    result = R.derive_rooms("L0", square_walls(), [], [], None, "x.dxf")
    assert result.closed and len(result.rooms) == 1
    room = result.rooms[0]
    assert room["status"] == "unverified" and room["room_type"] == "unknown" and room["label_raw"] is None
    assert room["id"] == "r_L0_oda" and abs(room["area_computed"] - 4.5 * 4.5) < 1e-6
    assert any("no label" in w for w in result.warnings)


def test_label_outside_every_room_is_reported():
    lab = label("SALON", (9, 9))
    result = R.derive_rooms("L0", square_walls(), [lab], [(9, 9)], [(9.5, 9.1)], "x.dxf")
    assert result.unplaced_labels == [lab] and result.rooms[0]["status"] == "unverified"
    assert any("outside every room" in w for w in result.warnings)


def test_two_labels_in_one_room():
    labels = [label("SALON", (1, 1), "TEXT:1"), label("MUTFAK", (3, 3), "TEXT:2")]
    result = R.derive_rooms("L0", square_walls(), labels, [(1, 1), (3, 3)], None, "x.dxf")
    room = result.rooms[0]
    assert room["label"] == "Salon" and room["status"] == "unverified" and len(room["evidence"]) == 2
    assert any("more labels" in w for w in result.warnings)


def test_fallback_point_places_label():
    lab = label("SALON 20,00 m²", (-1, 1))  # anchor outside, box centre inside
    result = R.derive_rooms("L0", square_walls(), [lab], [(-1, 1)], [(2, 2)], "x.dxf")
    room = result.rooms[0]
    assert room["label"] == "Salon" and room["area_label"] == 20.0 and room["status"] == "verified"


def test_tiny_gaps_do_not_merge_rooms():
    walls = square_walls()
    # Inner wall that stops 0.3 mm short of the outer faces on both ends.
    walls.append(WallItem((2.5, 0.2503), (2.5, 4.7497), 0.1, [0, 0, 0, 0], "e", B.evidence("x.dxf", "vector", 1.0, entity="e")))
    labels = [label("SALON", (1, 1), "TEXT:1"), label("MUTFAK", (3, 3), "TEXT:2")]
    result = R.derive_rooms("L0", walls, labels, [(1, 1), (3, 3)], None, "x.dxf")
    assert [r["label"] for r in result.rooms] == ["Salon", "Mutfak"]
    assert all(r["status"] == "verified" for r in result.rooms)


def test_room_containing():
    rooms = [{"id": "a", "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]}]
    assert R.room_containing(rooms, (1, 1))["id"] == "a"
    assert R.room_containing(rooms, (3, 1)) is None
