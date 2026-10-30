"""The P15 terrace (30 Oct 2026, lesson UL152, user: "teras inspration"): a larger terrace gets an outdoor lounge set,
a narrow one a pair of armchairs with a side table against the house wall, a small balcony plants only; never a
dining table and chairs (UL130), never both sets."""
from shapely.geometry import Polygon

from wenart.furniture import groups as GR
from wenart.furniture import program as PR
from wenart.furniture import schemas


def _rows(poly):
    room = {"id": "r_t", "room_type": "balcony", "polygon": poly}
    p = Polygon(poly)
    return PR._rows("balcony", p.area, p, {"rooms": [room], "furniture": []}, room, None)


def test_a_wide_terrace_gets_the_lounge_set_not_the_pair():
    groups = [g for g, _r, _o in _rows([[0, 0], [5, 0], [5, 3.5], [0, 3.5]])]
    assert "terrace_lounge" in groups and "terrace_pair" not in groups and "dining" not in groups


def test_a_narrow_l_terrace_gets_the_pair_by_its_inner_width():
    poly = [[0.2, 0.2], [1.7, 0.2], [1.7, 10.3], [3.2, 10.3], [3.2, 11.8], [0.2, 11.8]]
    assert PR.inner_width(poly) < PR.TERRACE_LOUNGE_MIN_WIDTH_M <= PR.min_width(Polygon(poly))
    groups = [g for g, _r, _o in _rows(poly)]
    assert "terrace_pair" in groups and "terrace_lounge" not in groups


def test_a_small_balcony_keeps_its_plants_only():
    assert [g for g, _r, _o in _rows([[0, 0], [2.5, 0], [2.5, 1.2], [0, 1.2]])] == ["balcony"]


def test_the_lounge_pieces_are_allowed_outside_and_offered_only_by_the_program():
    assert {"armchair", "sofa", "ottoman", "side_table"} <= set(schemas.allowed_types("balcony"))
    for group in ("terrace_lounge", "terrace_pair"):
        assert GR.extra_options(group, 30.0, 10.0, 5.0) == []
