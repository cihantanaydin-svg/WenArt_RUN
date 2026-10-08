"""Exterior rules of the sheets stage (docs/milestone10.md §1.6b rows 1, 12, 13): sides, the viewer's direction of an
elevation, compass sides, the ridge of a gable read from a section."""
from __future__ import annotations

import pytest

from wenart.sheets import exterior as EX


def test_side_words_and_no_unknown_side():
    assert EX.side_of("GÜNEY GÖRÜNÜŞÜ") == "south"
    assert EX.side_of("East elevation") == "east"
    assert EX.side_of("ARKA CEPHE") == "back"
    assert EX.side_of("GÖRÜNÜŞ") is None and EX.side_of(None) is None


@pytest.mark.parametrize("side, north, normal, view", [
    ("south", 0.0, 270.0, 90.0),            # the sheets example: south facade, viewer looks north (+Y)
    ("east", 0.0, 0.0, 180.0),
    ("north", 90.0, 180.0, 0.0),            # +Y points east: north is -X
    ("front", None, 270.0, 90.0),           # front = -Y without a north
    ("right", None, 0.0, 180.0),
    ("south", None, None, None),            # a compass side needs the north
    ("all", 0.0, None, None),
])
def test_normal_and_view_bearing(side, north, normal, view):
    assert EX.normal_deg(side, north) == (None if normal is None else pytest.approx(normal))
    assert EX.view_bearing_deg(side, north) == (None if view is None else pytest.approx(view))


def test_compass_of_a_normal():
    assert EX.compass_of(270.0, 0.0) == ("south", 180.0)       # -Y with +Y north
    assert EX.compass_of(270.0, 330.0) == ("south", 150.0)     # +Y 30 deg west of north
    assert EX.compass_of(0.0, 90.0) == ("south", 180.0)        # +X when +Y points east


def test_gable_ridge_runs_across_the_cut():
    roof = {"outline": [[-0.5, -0.5], [10.75, -0.5], [10.75, 8.75], [-0.5, 8.75]]}
    heights = {"cut_axis": "y", "roof": {"profile": [[-0.5, 3.65], [4.125, 6.888], [8.75, 3.65]]}}
    assert EX.ridge_lines(roof, heights, None) == [[[-0.5, 4.125], [10.75, 4.125]]]
    heights["cut_axis"] = "x"
    assert EX.ridge_lines(roof, heights, None) == [[[4.125, -0.5], [4.125, 8.75]]]
    heights["cut_axis"] = None
    assert EX.ridge_lines(roof, heights, None) == []


@pytest.mark.parametrize("label, kind", [
    ("OTOPARK", "parking"), ("Car porch", "parking"), ("BAHÇE", "garden"), ("Lawn", "garden"), ("TERAS", "terrace"),
    ("KALDIRIM", "paving"), ("Courtyard", "paving"), ("HAVUZ", "pool"), ("SALON", None), ("Yatak Odası", None),
])
def test_area_kinds_of_site_labels(label, kind):
    # building.schema site.areas[].kind: the labels.py site words (Turkish, English, German, French).
    assert EX.area_kind(label) == kind
