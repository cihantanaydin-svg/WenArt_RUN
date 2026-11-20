"""Structural rules of 20 Nov 2026 (the user: "focus on real structural problems"; every fix general): synthetic cases,
none taken from a project.

- a level the reading adds after the variants were written is built (``views.building_variants``) and RC1 names a
  level no build takes (``views.levels_not_built``);
"""
from __future__ import annotations

from wenart import views as V


def _level(lid, elev, **kw):
    return dict({"id": lid, "label": lid, "elevation": elev, "variant": "base"}, **kw)


def _variants_building():
    return {"levels": [_level("L-1", -3.0, kind="basement"), _level("L0", 0.0), _level("L1", 3.0),
                       _level("L1b", 3.0, base_level_id="L1", variant="alt")],
            "variants": [{"id": "base", "base": True, "levels": ["L0", "L1"], "changes": []},
                         {"id": "alt", "base": False, "levels": ["L0", "L1b"],
                          "changes": [{"replaces": "L1", "level_id": "L1b"}]}],
            "walls": [{"id": "w1", "level_id": "L-1", "start": [0, 0], "end": [4, 0], "thickness": 0.2}],
            "openings": [], "rooms": []}


def test_a_level_added_after_the_variants_is_built():
    b = _variants_building()
    base = V.variant_record(b, "base")
    assert base["levels"] == ["L-1", "L0", "L1"] and base["levels_added"] == ["L-1"]
    assert V.variant_record(b, "alt")["levels"] == ["L0", "L1b"]          # an alternative variant is unchanged
    view = V.variant_building(b, "base")
    assert [lv["id"] for lv in view["levels"]] == ["L-1", "L0", "L1"] and view["walls"]
    assert V.levels_not_built(b) == []
    assert b["variants"][0]["levels"] == ["L0", "L1"]                      # the building itself is not changed


def test_rc1_names_a_level_no_build_takes():
    b = _variants_building()
    b["levels"].append(_level("L2x", 6.0, variant="other"))                 # a variant id no record carries
    left = V.levels_not_built(b)
    assert [x["id"] for x in left] == ["L2x"] and "lists it in no variant" in left[0]["reason"]
