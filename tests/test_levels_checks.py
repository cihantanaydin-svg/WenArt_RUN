"""CPU tests of the level checks L1-L7 (docs/milestone12.md §3.5; wenart/levels/checks.py): a pass and a fail case
each, on the hand-made building (tests/_levels_fixture.py) after the inference."""
import copy

import pytest

from wenart.levels import checks as C
from wenart.levels import model as M
from tests import _levels_fixture as F


def _built(**brief):
    b = F.building()
    if brief:
        b["project"]["brief"] = {"levels": brief}
    return M.infer_levels(b)


def _ids(findings, check):
    return {f["target"] for f in findings if f["check"] == check}


def test_the_inferred_building_passes_every_check():
    b = _built()
    assert C.check_levels(b) == []
    assert set(C.CHECKS) == {"L1", "L2", "L3", "L4", "L5", "L6", "L7"}
    for f in C.check_levels(_built(ground_rise=0.9)):
        assert f["severity"] not in ("critical", "major"), f


def test_l1_the_landing_must_meet_the_threshold_and_the_steps_the_ground():
    b = _built()
    e = b["site"]["entrances"][0]
    e["landing"]["z"] = -0.10
    found = C.check_levels(b)
    assert "d_front" in _ids(found, "L1") and all(set(f) == {"check", "severity", "target", "room_id", "message",
                                                               "metrics"} for f in found)
    b = _built()
    b["site"]["entrances"][0]["ground_z"] = -0.40                 # the steps no longer reach the ground
    assert "d_front" in _ids(C.check_levels(b), "L1")
    b = _built()
    b["site"]["entrances"][0].update(ground_z=0.5, threshold_z=0.0, solution="none", steps=None, landing=None)
    f = [x for x in C.check_levels(b) if x["check"] == "L1"]
    assert f and "into the ground" in f[0]["message"] and f[0]["severity"] == "critical"


def test_l2_a_raised_door_without_steps():
    b = _built()
    b["site"]["entrances"][0].update(solution="none", steps=None, landing=None)
    assert "d_front" in _ids(C.check_levels(b), "L2")
    b["site"]["entrances"][0].update(ground_z=-2.0, rise=2.0)
    assert any("into the air" in f["message"] for f in C.check_levels(b) if f["check"] == "L2")


def test_l3_a_floor_under_the_terrain_and_a_basement_window_without_a_light_well():
    b = _built()
    b["site"]["ground"]["levels"] = [{"side": "all", "z": {"value": 0.5, "method": "vector", "confidence": 1.0,
                                                           "evidence": [dict(F.EV)]}}]
    b["site"]["ground"]["surface"] = {"kind": "flat", "flat_z": 0.5}
    assert "L0" in _ids(C.check_levels(b), "L3")
    base = _built()
    base["levels"][0].update(kind="basement", label="Bodrum Kat")
    base["openings"].append(dict(base["openings"][2], id="win_2", wall_id="w_3", center=[3.0, 8.0]))   # north wall
    base["site"]["ground"]["levels"] = [{"side": "all", "z": {"value": 1.5, "method": "vector", "confidence": 1.0,
                                                              "evidence": [dict(F.EV)]}}]   # over the 0.90 m sill
    base["site"]["ground"]["surface"] = {"kind": "flat", "flat_z": 1.5}
    found = C.check_levels(base)
    # (the south side is lowered to the front door's floor by the build: win_1 there is above the ground)
    assert _ids(found, "L3") == {"win_2"}
    base["site"]["ground"]["light_wells"] = [{"opening_id": "win_2", "polygon": [[2, 8.1], [4, 8.1], [4, 9]],
                                              "source": "assumed"}]
    assert "win_2" not in _ids(C.check_levels(base), "L3")


def test_l4_built_floors_and_ground_against_the_marks():
    b = F.building()
    b["level_marks"] = [F.mark("lm_001", -0.30, kind="floor", point=(3.0, 4.0), room_id="r_living"),
                        F.mark("lm_002", -0.15, kind="ground_finished", point=(3.0, -4.0))]
    b = M.infer_levels(b)
    assert not _ids(C.check_levels(b), "L4")
    b["rooms"][0]["floor_offset_m"] = 0.0                            # the room floor no longer follows its mark
    assert _ids(C.check_levels(b), "L4") == {"lm_001"}
    b["level_marks"][0]["evidence"][0]["method"] = "ocr"            # only vector marks are checked
    assert not _ids(C.check_levels(b), "L4")


def test_l5_steps_and_ramps():
    b = _built(ground_rise=0.40)
    assert not _ids(C.check_levels(b), "L5")
    st = b["site"]["entrances"][0]["steps"]
    st.update(riser=0.20, count=2, tread=0.25)
    found = [f for f in C.check_levels(b) if f["check"] == "L5"]
    assert found and "riser 0.200" in found[0]["message"] and "tread 0.25" in found[0]["message"]
    b = _built(ground_rise=0.40, accessible_entrance=True)
    b["site"]["entrances"][0]["ramp"]["slope"] = 0.12
    assert "d_front" in _ids(C.check_levels(b), "L5")
    low = _built(ground_rise=0.07)
    f = [x for x in C.check_levels(low) if x["check"] == "L5"]
    assert f and f[0]["severity"] == "minor" and "trip" in f[0]["message"]


def test_l6_a_steep_terrain_without_a_retaining_edge():
    b = F.building()
    b["level_marks"] = [F.mark("lm_001", 0.0, kind="ground_finished", point=(-2.0, -2.0)),
                        F.mark("lm_002", -6.0, kind="ground_finished", point=(12.0, -2.0)),
                        F.mark("lm_003", 0.0, kind="ground_finished", point=(-2.0, 10.0))]
    b["project"]["brief"] = {"levels": {"ground_outlier": 10.0}}
    found = C.check_levels(M.infer_levels(b))
    assert "terrain" in _ids(found, "L6")


def test_l7_entrances_in_the_exterior_views():
    b = _built()
    assert not [f for f in C.check_levels(b) if f["check"] == "L7"]          # skipped without manifests
    man = {"cameras": [{"name": "ext_1", "kind": "exterior", "visible_openings": ["win_1"]}]}
    assert "d_front" in _ids(C.check_levels(b, scene_manifest=man), "L7")
    man["cameras"][0]["visible_openings"].append("d_front")
    assert not _ids(C.check_levels(b, scene_manifest=man), "L7")
    man["cameras"][0]["visible_objects"] = ["ground", "facade_plinth"]
    assert "d_front" in _ids(C.check_levels(b, render_manifest=man), "L7")
    man["cameras"][0]["visible_objects"].append("steps_d_front")
    assert not _ids(C.check_levels(b, render_manifest=man), "L7")


def test_checks_are_pure():
    b = _built()
    before = copy.deepcopy(b)
    C.check_levels(b, {"cameras": []}, {"renders": []})
    assert b == before
