"""CPU tests for wenart.building (IDs, label normalisation, schema validation)
and the wenart.geometry helpers both other milestone-2 modules import."""
import json
import math
from pathlib import Path

import jsonschema
import pytest

from wenart import building as B
from wenart import geometry as G

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "examples" / "building.example.json"


# --------------------------------------------------------------------------
# building.py
# --------------------------------------------------------------------------

def test_example_validates_and_broken_copy_fails():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert B.validation_errors(example) == []
    B.validate(example)
    broken = json.loads(json.dumps(example))
    broken["walls"][0]["status"] = "maybe"
    del broken["rooms"][0]["polygon"]
    errors = B.validation_errors(broken)
    assert any("walls/0/status" in e for e in errors)
    assert any("rooms/0" in e and "polygon" in e for e in errors)
    with pytest.raises(jsonschema.ValidationError):
        B.validate(broken)


def test_empty_building_is_valid_and_complete():
    b = B.empty_building("p", "projects/p", "abc", created_utc="2026-10-01T00:00:00Z", brief={"style": "x"})
    B.validate(b)
    assert set(b) == set(B.load_schema()["required"])
    assert b["project"]["brief"] == {"style": "x"}
    assert B.empty_building("p", "projects/p", "abc")["project"]["created_utc"].endswith("Z")


def test_evidence_constructor():
    ev = B.evidence("a.dxf", "vector", 1.0, layer="DUVAR", entity="LWPOLYLINE:3F", pass_=2)
    assert ev == {"file": "a.dxf", "method": "vector", "confidence": 1.0, "layer": "DUVAR",
                  "entity": "LWPOLYLINE:3F", "pass": 2}
    with pytest.raises(ValueError):
        B.evidence("a", "guess", 1.0)
    with pytest.raises(ValueError):
        B.evidence("a", "ai", 1.5)


@pytest.mark.parametrize("raw, label, room_type, area", [
    ("SALON 24,50 m²", "Salon", "living", 24.5),
    ("SALON", "Salon", "living", None),
    ("YATAK ODASI", "Yatak Odası", "bedroom", None),
    ("ÇOCUK ODASI", "Çocuk Odası", "bedroom", None),
    ("EBEVEYN YATAK ODASI", "Ebeveyn Yatak Odası", "bedroom", None),
    ("MUTFAK 8.25 m2", "Mutfak", "kitchen", 8.25),
    ("BANYO", "Banyo", "bathroom", None),
    ("WC", "WC", "wc", None),
    ("HOL", "Hol", "hall", None),
    ("ANTRE", "Antre", "hall", None),
    ("KORİDOR", "Koridor", "hall", None),
    ("BALKON", "Balkon", "balcony", None),
    ("KİLER", "Kiler", "storage", None),
    ("DEPO", "Depo", "storage", None),
    ("ÇALIŞMA ODASI", "Çalışma Odası", "other", None),
    ("  salon   24,5 m² ", "Salon", "living", 24.5),
])
def test_normalise_room_label(raw, label, room_type, area):
    assert B.normalise_room_label(raw) == (label, room_type, area)


@pytest.mark.parametrize("raw, expected", [
    ("ZEMİN KAT PLANI", ("Zemin Kat", 0)),
    ("1. KAT PLANI", ("1. Kat", 1)),
    ("2. KAT PLANI", ("2. Kat", 2)),
    ("12.KAT PLANI", ("12. Kat", 12)),
    ("BODRUM KAT PLANI", ("Bodrum Kat", -1)),
    ("ZEMİN KAT MOBİLYA PLANI", ("Zemin Kat", 0)),
    ("MOBİLYA PLANI", None),
    ("ÖLÇEK 1/100", None),
])
def test_normalise_level_label(raw, expected):
    assert B.normalise_level_label(raw) == expected


def test_turkish_case_and_slug():
    assert B.turkish_lower("KİLER I") == "kiler ı"
    assert B.turkish_upper("kiler ı") == "KİLER I"
    assert B.slugify("Yatak Odası") == "yatak_odasi"
    assert B.slugify("Çocuk Odası") == "cocuk_odasi"
    assert B.slugify("") == "room"


def test_id_convention():
    assert B.level_id(0) == "L0" and B.level_id(1) == "L1" and B.level_id(-1) == "L-1"
    ids = B.IdCounter()
    assert [ids.next("wall", "L0") for _ in range(2)] == ["w_L0_001", "w_L0_002"]
    assert ids.next("door", "L0") == "d_L0_001"
    assert ids.next("window", "L0") == "win_L0_001"
    assert ids.next("opening", "L1") == "o_L1_001"
    assert ids.next("furniture", "L1") == "f_L1_001"
    assert ids.next("conflict") == "c_001" and ids.next("conflict") == "c_002"
    assert ids.room("L0", "Salon") == "r_L0_salon"
    assert ids.room("L0", "Kiler") == "r_L0_kiler"
    assert ids.room("L0", "Kiler") == "r_L0_kiler_2"
    assert ids.room("L0", "Kiler") == "r_L0_kiler_3"
    with pytest.raises(ValueError):
        B.element_id("wall", None, 1)


def test_save_and_load_roundtrip(tmp_path):
    b = B.empty_building("p", "projects/p", "abc", created_utc="2026-10-01T00:00:00Z")
    path = B.save(b, tmp_path / "sub" / "building.json")
    assert B.load(path) == b
    b["status"] = "broken"
    with pytest.raises(jsonschema.ValidationError):
        B.save(b, tmp_path / "x.json")


# --------------------------------------------------------------------------
# geometry.py
# --------------------------------------------------------------------------

def test_polygon_area_and_point_in_polygon():
    square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert G.polygon_area(square) == 4.0
    assert G.polygon_signed_area(list(reversed(square))) == -4.0
    assert G.polygon_centroid(square) == (1.0, 1.0)
    assert G.point_in_polygon((1, 1), square)
    assert G.point_in_polygon((2, 1), square)  # on the edge counts as inside
    assert not G.point_in_polygon((3, 1), square)
    concave = [(0, 0), (4, 0), (4, 4), (2, 4), (2, 2), (0, 2)]
    assert G.point_in_polygon((1, 1), concave) and not G.point_in_polygon((1, 3), concave)


def test_segments_and_angles():
    assert G.segment_length((0, 0), (3, 4)) == 5.0
    assert G.segment_midpoint((0, 0), (2, 4)) == (1.0, 2.0)
    assert G.segment_angle_deg((0, 0), (0, 1)) == 90.0
    assert G.segment_angle_deg((1, 1), (0, 1)) == 180.0
    assert G.normalise_angle(-90) == 270.0 and G.normalise_angle(360) == 0.0
    assert G.angle_difference_deg(350, 10) == 20.0
    assert G.point_segment_distance((1, 1), (0, 0), (2, 0)) == 1.0
    assert G.point_segment_distance((5, 0), (0, 0), (2, 0)) == 3.0
    assert G.unit_normal_left((0, 0), (1, 0)) == (0.0, 1.0)
    x, y = G.rotate_point((1, 0), 90)
    assert abs(x) < 1e-12 and abs(y - 1) < 1e-12
    assert G.point_at_distance((0, 0), (10, 0), 2.5) == (2.5, 0.0)


def test_rectangle_centerline_roundtrip():
    start, end, t = G.rectangle_to_centerline([(0, 0), (9.6, 0), (9.6, 0.25), (0, 0.25)])
    assert start == (0.0, 0.125) and end == (9.6, 0.125) and abs(t - 0.25) < 1e-12
    # Any corner order and an explicit closing point give the same answer.
    start2, end2, t2 = G.rectangle_to_centerline([(9.6, 0.25), (9.6, 0), (0, 0), (0, 0.25), (9.6, 0.25)])
    assert (start2, end2) == (start, end) and abs(t2 - t) < 1e-12
    corners = G.centerline_to_rectangle((5.3, 0.25), (5.3, 6.95), 0.1)
    s, e, t = G.rectangle_to_centerline(corners)
    assert s == (5.3, 0.25) and e == (5.3, 6.95) and abs(t - 0.1) < 1e-9
    with pytest.raises(ValueError):
        G.rectangle_to_centerline([(0, 0), (1, 0), (1, 1)])


def test_rotated_rectangle_and_front():
    corners = G.rotated_rectangle((1, 1), (2, 1), 90)
    xs = sorted(round(c[0], 9) for c in corners)
    ys = sorted(round(c[1], 9) for c in corners)
    assert xs == [0.5, 0.5, 1.5, 1.5] and ys == [0.0, 0.0, 2.0, 2.0]
    assert G.front_direction_deg(0) == 270.0 and G.front_direction_deg(90) == 0.0


def test_boxes():
    assert G.bbox([(1, 2), (-1, 5), (3, 0)]) == [-1, 0, 3, 5]
    assert G.box_iou([0, 0, 2, 2], [1, 1, 3, 3]) == pytest.approx(1 / 7)
    assert G.box_iou([0, 0, 1, 1], [2, 2, 3, 3]) == 0.0
    assert G.box_iou([0, 0, 1, 1], [0, 0, 1, 1]) == 1.0
    assert G.box_center([0, 0, 2, 4]) == (1.0, 2.0)
    with pytest.raises(ValueError):
        G.bbox([])


def test_affine_and_homography():
    a = G.affine_from_scale_translate(28.3465, 28.3465, 200, 150)
    p = G.apply_affine(a, (3.3, 4.4))
    back = G.apply_affine(G.invert_affine(a), p)
    assert back == pytest.approx((3.3, 4.4))
    flip = [1, 0, 0, 0, -1, 10]
    composed = G.compose_affine(flip, a)  # a first, then flip
    assert G.apply_affine(composed, (1, 1)) == pytest.approx(G.apply_affine(flip, G.apply_affine(a, (1, 1))))
    m = G.affine_to_matrix(a)
    assert G.matrix_to_affine(m) == a
    assert G.apply_homography(m, (1, 2)) == pytest.approx(G.apply_affine(a, (1, 2)))
    flat = [v for row in m for v in row]
    assert G.apply_homography(flat, (1, 2)) == pytest.approx(G.apply_affine(a, (1, 2)))
    h = [[1, 0.1, 5], [0.05, 1, 7], [0.001, 0.002, 1]]
    q = G.apply_homography(h, (10, 20))
    assert G.apply_homography(G.invert_homography(h), q) == pytest.approx((10, 20))
    assert G.transform_box(a, [0, 0, 1, 1]) == pytest.approx([200, 150, 228.3465, 178.3465])
    with pytest.raises(ValueError):
        G.matrix_to_affine(h)
    with pytest.raises(ZeroDivisionError):
        G.invert_affine([1, 2, 0, 2, 4, 0])
    assert math.isclose(G.snap(0.1 + 0.2), 0.3) and G.snap(-1e-9) == 0.0
