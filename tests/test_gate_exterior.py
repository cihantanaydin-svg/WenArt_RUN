"""CPU tests of the change gate on exterior views (docs/milestone10.md §3.3 items 4-5).

The facade look gives the walls' albedo mode (a smooth render in a colour is flat, a brick or cladding is a
texture, an unknown slug is not guessed); the calibration of a project with an exterior view compares it with the
benign and negative controls and records every comparison with its ``view_kind``; the top-level rates count the
rooms only, the exterior block holds the exterior rates, and ``exterior_validation`` / ``exterior_polish`` turn
them into the decision that keeps the exterior views Cycles only when the exterior negatives are not rejected.
"""
import json
from pathlib import Path

import pytest

import vc_ext_toy as E
from conftest import START_THRESHOLDS
from test_gate import FakeModels
from wenart import views as V
from wenart.gate import api
from wenart.gate import calibrate as CAL
from wenart.gate import colour as GC
from wenart.gate import validate as VAL

LIMITS = {"benign_accept_min": 0.95, "negative_reject_min": 0.9}


# --------------------------------------------------------------------------
# Albedo of the facade
# --------------------------------------------------------------------------

def scene(facade=None, **extra) -> dict:
    out = {"cameras": [{"name": "ext_1", "kind": "exterior", "room_id": None},
                       {"name": "cam_a", "kind": "interior", "room_id": "r_1"}],
           "materials": {}, "style_profile": {"walls": {"material": "plaster_white"}}, "objects": []}
    if facade is not None:
        out["exterior_looks"] = {"facade": facade}
    out.update(extra)
    return out


def test_an_exterior_camera_is_told_by_its_kind_or_its_name():
    s = scene()
    assert GC.is_exterior(s, "ext_1", None) is True and GC.is_exterior(s, "cam_a", "r_1") is False
    assert GC.is_exterior({"cameras": []}, "ext_4", None) is True                    # no kind recorded: the name
    assert GC.is_exterior({"cameras": []}, "cam_x_1", None) is False
    assert GC.is_exterior(None, "ext_1", None) is True and GC.is_exterior(None, None, None) is False


@pytest.mark.parametrize("slug, mode", [("render", "flat"), ("fibre_cement", "flat"), ("brick_red", "texture"),
                                        ("stone_cladding", "texture"), ("wood_cladding", "texture"),
                                        ("brick_white_painted", "texture"), ("mystery", None), (None, None)])
def test_the_facade_decides_the_albedo_mode_of_the_walls(slug, mode):
    albedo = GC.structure_albedo(scene({"material": slug, "colour": "greige"}), None, exterior=True)
    assert albedo[GC.WALL_REGION]["albedo_mode"] == mode and albedo[GC.WALL_REGION]["slot"] == "exterior_looks.facade"
    ceiling = albedo[GC.CEILING_REGION]
    assert ceiling["albedo_mode"] is None and ceiling["material"] is None        # the soffit is no ceiling


def test_a_material_record_of_the_scene_wins_over_the_slug_tables():
    s = scene({"material": "render", "colour": "greige"},
              materials={"render__greige": {"slug": "render", "albedo_mode": "texture"}})
    assert GC.structure_albedo(s, None, exterior=True)[GC.WALL_REGION]["albedo_mode"] == "texture"
    # An interior call is unchanged by the new parameter.
    inner = GC.structure_albedo(s, "r_1")
    assert inner[GC.WALL_REGION]["material"] == "plaster_white" and inner[GC.WALL_REGION]["slot"] == "style_profile.walls"


def test_neutral_check_skips_a_textured_facade_and_measures_a_flat_one():
    flat = GC.exterior_albedo(scene({"material": "render", "colour": "greige"}))
    textured = GC.exterior_albedo(scene({"material": "brick_red", "colour": None}))
    ref = {GC.WALL_REGION: [60.0, 2.0, 8.0]}
    test = {GC.WALL_REGION: [60.0, 2.0, 14.0]}
    n = {GC.WALL_REGION: 5000}
    assert GC.neutral_metrics(ref, test, n, 10000, flat, 0.0)["regions"][GC.WALL_REGION] > 5.0
    assert GC.neutral_metrics(ref, test, n, 10000, textured, 0.0)["skipped"][GC.WALL_REGION] == "albedo_texture"


# --------------------------------------------------------------------------
# Calibration of a project with an exterior view
# --------------------------------------------------------------------------

@pytest.fixture()
def project(tmp_path):
    out = E.write_ext_project(tmp_path, size=(320, 180))
    path = out / "scene" / "scene_manifest.json"
    sc = json.loads(path.read_text(encoding="utf-8"))
    sc["exterior_looks"] = {"facade": {"material": "render", "colour": "greige", "source": "fallback"}}
    path.write_text(json.dumps(sc), encoding="utf-8")
    return out


def test_the_gate_prepares_an_exterior_view_with_the_facade_albedo(project):
    gate = api.Gate(thresholds=START_THRESHOLDS, models=FakeModels(), device="cpu")
    view = V.load_views(project / "renders")["ext_1"]
    ref = gate.prepare(view, view.read_rgb())
    assert ref.albedo[GC.WALL_REGION]["albedo_mode"] == "flat"
    assert ref.albedo[GC.WALL_REGION]["material"] == "render"


def test_calibration_compares_the_exterior_view_and_keeps_its_rates_apart(project):
    gate = api.Gate(thresholds=START_THRESHOLDS, models=FakeModels(), device="cpu")
    cal = CAL.run_calibration(project, gate=gate, log=lambda *_: None)
    assert cal["views"] == ["ext_1"] and cal["incomplete"] is False
    assert {r["view_kind"] for r in cal["benign"] + cal["negative"]} == {"exterior"}
    ext = cal["exterior"]
    assert ext["cameras_rendered"] == 1 and ext["views"] == ["ext_1"] and ext["n_benign"] == 8
    assert ext["n_negative"] == len(cal["negative"]) > 8
    assert 0.5 <= ext["rates"]["benign_accept"] <= 1.0 and 0.0 <= ext["rates"]["negative_reject"] <= 1.0
    # The rooms' rates count the interior comparisons only: there are none.
    assert cal["rates"]["benign_accept"] is None and cal["rates"]["negative_reject"] is None
    objects = {o["wenart_id"] for o in cal["objects"]["ext_1"]}
    assert objects <= {"win_s1", "d_s1", "win_s2", "win_e1"} and objects
    md = (project / "gate" / "gate_calibration.md").read_text(encoding="utf-8")
    assert "## Exterior views" in md and "1 exterior view(s) rendered" in md
    # The CLI flag turns the exterior views off.
    off = CAL.run_calibration(project, gate=api.Gate(thresholds=START_THRESHOLDS, models=FakeModels(), device="cpu"),
                              out_dir=project / "gate_off", n_exterior=0, log=lambda *_: None)
    assert off["views"] == [] and off["exterior"]["cameras_rendered"] == 1 and off["exterior"]["views"] == []


def test_a_deadline_that_cuts_the_exterior_comparisons_leaves_the_rooms_calibration_complete(project):
    """The exterior views are the last CPU phase: a cut there sets only ``exterior_incomplete``."""
    gate = api.Gate(thresholds=START_THRESHOLDS, models=FakeModels(), device="cpu")
    cal = CAL.run_calibration(project, gate=gate, deadline=1.0, log=lambda *_: None)    # long past
    assert cal["incomplete"] is False and cal["exterior_incomplete"] is True
    assert cal["benign"] == [] and any("exterior comparisons were not started" in w for w in cal["warnings"])
    decision = CAL.exterior_validation(cal, VAL.load_validation_config(), START_THRESHOLDS)
    assert decision["decision"] == "not_validated" and decision["polish_allowed"] is False
    assert "## Exterior views" in (project / "gate" / "gate_calibration.md").read_text(encoding="utf-8")
    full = CAL.run_calibration(project, gate=api.Gate(thresholds=START_THRESHOLDS, models=FakeModels(), device="cpu"),
                               out_dir=project / "gate_full", log=lambda *_: None)
    assert full["incomplete"] is False and full["exterior_incomplete"] is False and full["benign"]


def test_a_calibration_that_ran_gives_an_exterior_decision_from_its_exterior_comparisons(project):
    CAL.run_calibration(project, gate=api.Gate(thresholds=START_THRESHOLDS, models=FakeModels(), device="cpu"),
                        log=lambda *_: None)
    decision = CAL.exterior_polish(project, thresholds=START_THRESHOLDS)
    assert decision["source"] == "gate_calibration.json" and decision["exterior_cameras"] == 1
    assert decision["n_benign"] == 8 and decision["limits"] == VAL.load_validation_config()
    assert decision["decision"] in VAL.DECISIONS + ("not_applicable",)
    assert decision["polish_allowed"] == (decision["decision"] in VAL.POLISH_DECISIONS)


# --------------------------------------------------------------------------
# The exterior decision (pure)
# --------------------------------------------------------------------------

def rec(kind, decision, control="shift"):
    return {"camera": "ext_1" if kind == "exterior" else "cam_a", "view_kind": kind, "control": control,
            "magnitude": 6, "decision": decision, "reasons": [], "notes": [], "metrics": {}, "small": True}


def cal_of(benign_ext, negative_ext, benign_in=(), negative_in=(), thresholds=START_THRESHOLDS, rendered=1):
    cal = {"incomplete": False, "thresholds": thresholds,
           "benign": [rec("exterior", d) for d in benign_ext] + [rec("interior", d) for d in benign_in],
           "negative": [rec("exterior", d) for d in negative_ext] + [rec("interior", d) for d in negative_in]}
    cal.update(CAL.summarise(cal, thresholds))
    cal["exterior"] = {"cameras_rendered": rendered, "views": ["ext_1"],
                       **CAL.summarise({"benign": cal["benign"], "negative": cal["negative"], "presumed_bad": []},
                                       thresholds, kind="exterior")}
    return cal


def test_the_rates_of_the_rooms_do_not_count_the_exterior_comparisons():
    cal = cal_of(["reject"] * 4, ["accept"] * 4, benign_in=["accept"] * 4, negative_in=["reject"] * 4)
    assert cal["rates"]["benign_accept"] == 1.0 and cal["rates"]["negative_reject"] == 1.0
    assert cal["exterior"]["rates"]["benign_accept"] == 0.0 and cal["exterior"]["rates"]["negative_reject"] == 0.0
    # A calibration before Milestone 10 has no view_kind: every record is an interior one.
    old = {"benign": [{"control": "blur", "magnitude": 1.0, "decision": "accept", "camera": "c", "reasons": [],
                       "metrics": {}}],
           "negative": [{"control": "shift", "magnitude": 6, "decision": "reject", "camera": "c", "reasons": [],
                         "metrics": {}, "small": True}]}
    assert CAL.summarise(old, START_THRESHOLDS)["rates"]["benign_accept"] == 1.0
    assert CAL.summarise(old, START_THRESHOLDS, kind="exterior")["rates"]["benign_accept"] is None


@pytest.mark.parametrize("benign, negative, decision, allowed", [
    (["accept"] * 20, ["reject"] * 20, "ok", True),
    (["accept"] * 18 + ["reject"] * 2, ["reject"] * 20, "flagged", True),                  # 0.90 < 0.95 benign
    (["accept"] * 20, ["reject"] * 17 + ["accept"] * 3, "polish_disabled", False),         # 0.85 < 0.90 negative
    ([], ["reject"] * 5, "not_validated", False),
    (["accept"] * 5, [], "not_validated", False),
])
def test_exterior_validation_uses_the_limits_of_the_project(benign, negative, decision, allowed):
    out = CAL.exterior_validation(cal_of(benign, negative), LIMITS, START_THRESHOLDS)
    assert out["decision"] == decision and out["polish_allowed"] is allowed
    assert out["exterior_cameras"] == 1


def test_a_failed_exterior_validation_does_not_fail_the_rooms():
    cal = cal_of(["accept"] * 20, ["accept"] * 20, benign_in=["accept"] * 20, negative_in=["reject"] * 20)
    assert VAL.decide_validation(cal, LIMITS, START_THRESHOLDS)["decision"] == "ok"                 # the rooms
    assert CAL.exterior_validation(cal, LIMITS, START_THRESHOLDS)["decision"] == "polish_disabled"  # the facade


def test_no_exterior_view_is_not_applicable_and_no_calibration_is_not_validated():
    cal = cal_of([], [], rendered=0)
    out = CAL.exterior_validation(cal, LIMITS, START_THRESHOLDS)
    assert out["decision"] == "not_applicable" and out["polish_allowed"] is False
    assert CAL.exterior_validation(None, LIMITS)["decision"] == "not_validated"
    old = {"benign": [rec("interior", "accept")], "negative": [rec("interior", "reject")], "incomplete": False,
           "thresholds": START_THRESHOLDS, "rates": {"benign_accept": 1.0, "negative_reject": 1.0}}
    out = CAL.exterior_validation(old, LIMITS, START_THRESHOLDS)
    assert out["decision"] == "not_validated" and "no exterior block" in out["reasons"][0]
    cut = dict(cal_of(["accept"] * 20, ["reject"] * 20), incomplete=True)
    assert CAL.exterior_validation(cut, LIMITS, START_THRESHOLDS)["decision"] == "not_validated"
    other = dict(cal_of(["accept"] * 20, ["reject"] * 20, thresholds={"edges": {"global_min": 0.5}}))
    assert CAL.exterior_validation(other, LIMITS, START_THRESHOLDS)["decision"] == "not_validated"


def test_exterior_polish_without_a_calibration_file(tmp_path):
    out = CAL.exterior_polish(tmp_path / "outputs" / "toy", thresholds=START_THRESHOLDS)
    assert out["decision"] == "not_validated" and out["polish_allowed"] is False and out["source"] is None


def test_donors_come_from_a_view_of_the_same_kind_first():
    donors = [{"camera": "cam_a"}, {"camera": "ext_1"}, {"camera": "ext_2"}]
    kinds = {"cam_a": "interior", "ext_1": "exterior", "ext_2": "exterior"}
    assert CAL.donor_for(donors, "ext_2", kinds)["camera"] == "ext_1"
    assert CAL.donor_for(donors, "ext_1", kinds)["camera"] == "ext_2"
    assert CAL.donor_for(donors, "cam_a", kinds)["camera"] == "ext_1"              # no other interior view: any
    assert CAL.donor_for(donors, "ext_1")["camera"] == "cam_a"                      # without kinds: the first other
    assert CAL.donor_for([{"camera": "ext_1"}], "ext_1", kinds) is None
