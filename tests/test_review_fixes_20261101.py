"""Fixes of the user's review of real04 run 20261031-194116-full (1 Nov 2026)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from wenart.furniture import catalog as C
from wenart.furniture import fit as F

RUN = Path("/home/user/WenArt_RUN/runs/20261031-194116-full/results/furniture/real04/building_final.json")


def test_a_front_side_only_guessed_is_not_used():
    """UL242 ("Directions of this bed could be wrong ... you can remove from the library"): a model whose front side the
    audit only guessed ("side unknown") is not used unless its front-axis confidence is high."""
    base = {"id": "m", "type": "bed_double", "audit": {"status": "keep", "notes": [
        "its front is on the wrong side for a bed_double (width along the front): turned 90 deg (side unknown: the "
        "vision check confirms)"]}, "licence_flag": "none", "commercial_safe": True}
    assert not C.usable(dict(base, front_axis_confidence="medium"), "relaxed")
    assert "only guessed" in C.unusable_reason(dict(base, front_axis_confidence="low"), "relaxed")
    assert C.front_guessed(dict(base, front_axis_confidence="medium"))
    assert not C.front_guessed(dict(base, front_axis_confidence="high"))
    assert not C.front_guessed({"id": "n", "audit": {"status": "keep", "notes": ["material tags judged"]}})


def test_a_tv_unit_added_after_the_decor_stage_gets_its_tv():
    """UL240 ("There could have been a TV on top of this"): the agent's relayout added a TV unit after the decor stage;
    the refit gives every TV unit with a wall behind it its TV, once; the first fit (no decor yet) adds none."""
    if not RUN.is_file():
        pytest.skip("the run's building is not on this machine")
    b = json.loads(RUN.read_text(encoding="utf-8"))
    out = F.tvs_for_bare_units(b)
    assert [r["host_id"] for r in out] == ["f_L1_069"]
    tv = next(d for d in b["decor"] if d["id"] == out[0]["id"])
    assert tv["type"] == "tv" and tv["host_id"] == "f_L1_069" and "UL240" in tv["reason"]
    assert F.tvs_for_bare_units(b) == []                                  # once
    assert F.tvs_for_bare_units({"furniture": b["furniture"], "rooms": b["rooms"], "decor": []}) == []


def test_a_door_under_a_low_slope_raises_that_slope_parallel_not_the_other_side():
    """UL234: a shed-like attic (one slope down to the north, a flat ceiling elsewhere): a door 1.0 m under the slope
    with no better spot makes the slope rise parallel to itself until the door has 2.0 m; a plane over no such door
    stays; the raise is recorded on the roof model."""
    from wenart.blender import build as B
    from wenart.blender import roof as RF

    roof = {"equations": [(0.0, -0.5, 9.0), (0.0, 0.5, 2.0)], "thickness": 0.2, "outline": [(0, 0), (10, 0), (10, 10),
                                                                                          (0, 10)], "convex": True}
    level = {"id": "L1", "elevation": 3.0, "ceiling_height": 2.6}
    level["ceiling_planes"] = [list(p) for p in RF.ceiling_planes(roof, level)]
    walls = [{"id": "w", "level_id": "L1", "start": [2.0, 8.0], "end": [2.0, 9.8], "thickness": 0.1}]
    rooms = [{"id": "a", "level_id": "L1", "polygon": [[0, 0], [2, 0], [2, 10], [0, 10]]},
             {"id": "b", "level_id": "L1", "polygon": [[2, 0], [10, 0], [10, 10], [2, 10]]}]
    door = {"id": "d", "type": "door", "level_id": "L1", "wall_id": "w", "center": [2.0, 9.4], "width": 0.8,
            "height": 2.1}
    b = {"walls": walls, "rooms": rooms, "openings": [door], "furniture": []}
    before = list(roof["equations"][1])
    out = B.raise_slopes_for_doors(b, level, roof)
    assert out and out[0]["plane"] == 0 and out[0]["head_room"] >= 2.0 - 1e-6
    assert list(roof["equations"][1]) == before                       # the other plane stays
    assert roof["equations"][0][1] == -0.5 and roof["slopes_raised"][0]["delta"] > 0   # same pitch, raised
