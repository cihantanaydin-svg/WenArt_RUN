"""26 Nov 2026 (re-render of real10, pod 5n9vsxfitko5jf): an open-air room that no roof and no slab of a level above
covers is open to the sky (``build.open_sky_rooms``): the build leaves its ceiling out, as for a roof terrace cut into
the roof. A covered kind (loggia, veranda, porch) and a balcony under the slab above keep their ceiling."""
from __future__ import annotations

from wenart.blender import build as B


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _building(top_type: str = "balcony") -> dict:
    return {
        "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8},
                   {"id": "L1", "elevation": 3.0, "ceiling_height": 2.8}],
        "rooms": [
            {"id": "r_L0_salon", "level_id": "L0", "room_type": "living", "polygon": _rect(0, 0, 10, 8)},
            {"id": "r_L0_balkon", "level_id": "L0", "room_type": "balcony", "polygon": _rect(2, 8, 6, 9.5)},
            {"id": "r_L1_core", "level_id": "L1", "room_type": "stair", "polygon": _rect(4, 3, 7, 6)},
            {"id": "r_L1_teras", "level_id": "L1", "room_type": top_type, "polygon": _rect(0, 0, 4, 8)},
        ],
    }


def _slabs() -> dict:
    # the slab under L1 covers L0's footprint and its balcony
    return {"by_level": {"L0": {"under": None},
                         "L1": {"under": {"outline": _rect(0, 0, 10, 9.6), "voids": []}}}}


def _roof() -> dict:
    # a small flat roof over the stair core of L1 only
    return {"over_level_id": "L1", "outline": _rect(4, 3, 7, 6), "openings": []}


def test_top_terrace_outside_the_roof_is_open_to_the_sky():
    got = B.open_sky_rooms(_building(), _roof(), _slabs())
    assert [g["room_id"] for g in got] == ["r_L1_teras"]
    assert got[0]["covered"] == 0.0
    assert B.OPEN_SKY_RULE in got[0]["reason"]


def test_balcony_under_the_slab_above_keeps_its_ceiling():
    got = {g["room_id"] for g in B.open_sky_rooms(_building(), _roof(), _slabs())}
    assert "r_L0_balkon" not in got
    assert "r_L0_salon" not in got and "r_L1_core" not in got        # indoor rooms are never open to the sky


def test_covered_kinds_keep_their_cover():
    for kind in ("loggia", "veranda", "porch"):
        assert not B.open_sky_rooms(_building(kind), _roof(), _slabs()), kind


def test_terrace_under_the_roof_keeps_its_ceiling():
    roof = dict(_roof(), outline=_rect(0, 0, 10, 8))
    assert not B.open_sky_rooms(_building(), roof, _slabs())


def test_no_roof_and_no_slabs():
    got = {g["room_id"] for g in B.open_sky_rooms(_building(), None, None)}
    assert got == {"r_L0_balkon", "r_L1_teras"}
