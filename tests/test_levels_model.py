"""CPU tests of the level inference (docs/milestone12.md §3.2-§3.4, D3a; wenart/levels/model.py) on a hand-made
building (tests/_levels_fixture.py), the M10 example and the brief."""
import copy
import json
from pathlib import Path

import pytest

from wenart import building as B
from wenart.levels import model as M
from tests import _levels_fixture as F

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))


def _ent(b, door="d_front"):
    return next(e for e in b["site"]["entrances"] if e["door_id"] == door)


# --------------------------------------------------------------------------
# Single drawn ground floor (U2) and D3a
# --------------------------------------------------------------------------

def test_a_single_ground_floor_becomes_a_whole_building_with_a_flat_cut_roof():
    b0 = F.building()
    b = M.infer_levels(b0)
    assert b0.get("slabs") is None and b0["site"] is None                      # pure: the input is unchanged
    assert [s["id"] for s in b["slabs"]] == ["sl_L0"] and b["slabs"][0]["inferred"] is True
    assert b["slabs"][0]["outline"] and b["slabs"][0]["thickness"] == 0.2
    roof = b["roof"]
    assert roof["type"] == "flat" and roof["kind"] == "flat_cut" and roof["inferred"] is True
    assert roof["note"] == "upper floors not drawn" and roof["over_level_id"] == "L0"
    from wenart.blender import build as BB
    assert BB.is_whole_building(b)
    assert isinstance(b["site"], dict) and b["site"]["ground"]["levels"]
    assert b["level_inference"]["single_level_whole"] is True
    assert any(i["item"] == "roof" for i in b["level_inference"]["inferred"])
    assert not B.validation_errors(b)


def test_d3a_the_ground_floor_stands_0_15_m_above_an_undrawn_ground():
    b = M.infer_levels(F.building())
    g = b["site"]["ground"]
    assert g["source"] == "D3a" and g["terrain"] == "flat"
    assert g["levels"] == [{"side": "all", "azimuth_deg": None,
                            "z": {"value": -0.15, "method": "assumed", "confidence": 0.0, "evidence": [],
                                  "note": g["levels"][0]["z"]["note"]}}]
    assert "D3a" in g["levels"][0]["z"]["note"] and g["surface"]["inferred"] is True
    e = _ent(b)
    assert e["threshold_z"] == 0.0 and e["ground_z"] == -0.15 and e["rise"] == 0.15
    assert e["solution"] == "steps" and e["steps"]["count"] == 1 and e["steps"]["riser"] == 0.15
    assert e["landing"] == {"width": 1.6, "depth": 1.2, "z": 0.0} and e["main"] and e["inferred"]
    assert e["side"] in ("front", "south")
    assert [x["door_id"] for x in b["site"]["entrances"]] == ["d_front"]       # the inner door is no entrance


def test_the_brief_changes_the_rise_and_asks_for_a_ramp():
    b = F.building()
    b["project"]["brief"] = {"levels": {"ground_rise": 0.45, "accessible_entrance": True}}
    e = _ent(M.infer_levels(b))
    assert e["rise"] == 0.45 and e["steps"]["count"] == 3 and e["steps"]["riser"] == 0.15
    assert e["solution"] == "steps_and_ramp" and e["ramp"]["ratio"] == "1:14" and e["ramp"]["length"] == 6.303
    assert e["ramp"]["handrails"] is True and e["steps"]["handrails"] is False      # 0.45 m: not above 0.45
    assert M.level_params({"values": {"levels": {"riser_max_outdoor": "high"}}})["_warnings"]
    p = M.level_params({"values": {"levels": {"riser_max_outdoor": 0.16}}})
    assert p["riser_max_outdoor"] == 0.16 and p["_from_brief"] == ["riser_max_outdoor"]


def test_an_upper_floor_door_to_the_outside_is_a_door_into_the_air_of_lower_weight():
    """A two-level whole building: the first floor's door in the outer wall (a French balcony or an undrawn
    balcony) is recorded, not an entrance with steps; L2 rates it major, a ground-floor one critical."""
    from wenart.levels import checks as C
    b = F.building()
    up = copy.deepcopy(b)
    b["levels"].append(dict(b["levels"][0], id="L1", order=1, elevation=3.0, label="1. Kat"))
    for key in ("walls", "rooms", "openings"):
        for x in up[key]:
            b[key].append(dict(x, id=x["id"] + "_up", level_id="L1",
                               **({"wall_id": x["wall_id"] + "_up"} if key == "openings" else {})))
    b["slabs"] = [{"id": "sl_L0", "z_top": 0.0, "thickness": 0.2, "thickness_source": "assumed_default",
                   "outline": [[-0.1, -0.1], [10.1, -0.1], [10.1, 8.1], [-0.1, 8.1]], "evidence": [dict(F.EV)]}]
    n = M.infer_levels(b)
    ents = {e["door_id"]: e for e in n["site"]["entrances"]}
    assert ents["d_front"]["solution"] == "steps" and not ents["d_front"]["upper_floor"]
    assert ents["d_front_up"]["into_air"] and ents["d_front_up"]["upper_floor"]
    assert "French balcony" in ents["d_front_up"]["reason"]
    l2 = [f for f in C.check_levels(n) if f["check"] == "L2"]
    assert [(f["target"], f["severity"]) for f in l2] == [("d_front_up", "major")]


def test_upper_floor_or_basement_titles_are_not_made_whole():
    for label, order in (("1. Kat", 1), ("Bodrum Kat", -1), ("Normal Kat", None)):
        b = M.infer_levels(F.building(label=label, order=order, elevation=3.0 if order == 1 else 0.0))
        assert not b.get("slabs") and not isinstance(b.get("roof"), dict), label
    two = F.building()
    two["levels"].append(dict(two["levels"][0], id="L1", order=1, elevation=3.0, label="1. Kat"))
    assert not M.infer_levels(two).get("slabs")                                # two levels: not single


# --------------------------------------------------------------------------
# Steps and ramps
# --------------------------------------------------------------------------

def test_steps_sizing_and_intermediate_landings():
    p = M.level_params()
    assert M.steps_for(0.04, 1.6, p) is None                                    # flush
    st = M.steps_for(0.40, 1.6, p)
    assert st["count"] == 3 and st["riser"] == pytest.approx(0.1333, abs=1e-4) and st["tread"] == 0.32   # 2R + T >= 0.58
    assert 0.58 <= st["rule_2r_t"] <= 0.66 and st["flights"] == [3] and st["intermediate_landings"] == 0
    st = M.steps_for(2.0, 1.6, p)                                               # 14 risers: two flights
    assert st["count"] == 14 and st["flights"] == [12, 2] and st["intermediate_landings"] == 1
    assert st["handrails"] and st["cheek_walls"]
    assert M.steps_for(0.30, 1.0, p, outdoor=False)["count"] == 2               # indoor riser up to 0.18


@pytest.mark.parametrize("rise,ratio", [(0.10, "1:12"), (0.15, "1:12"), (0.30, "1:14"), (0.80, "1:16"),
                                        (1.20, "1:20")])
def test_ramp_slope_table(rise, ratio):
    r = M.ramp_for(rise, M.level_params())
    assert r["ratio"] == ratio and r["length"] == pytest.approx(rise / r["slope"], abs=1e-3)
    assert r["handrails"] is (rise > 0.15)


def test_a_door_far_above_the_ground_is_a_door_into_the_air():
    b = F.building()
    b["project"]["brief"] = {"levels": {"ground_rise": 1.5}}                    # brief limit: 1.5 m is allowed
    assert _ent(M.infer_levels(b))["solution"] == "steps"
    b = M.infer_levels(F.building())
    b["site"]["ground"]["levels"] = [{"side": "all", "z": {"value": -2.0, "method": "vector", "confidence": 1.0,
                                                           "evidence": [dict(F.EV)]}}]
    e = _ent(M.infer_levels(b))
    assert e["into_air"] is True and e["solution"] == "none" and "into the air" in e["reason"]


# --------------------------------------------------------------------------
# Ground from marks
# --------------------------------------------------------------------------

def _with_marks(*marks):
    b = F.building()
    b["level_marks"] = list(marks)
    return b


def test_a_site_note_gives_the_ground_and_wins_over_d3a():
    b = M.infer_levels(_with_marks(F.mark("lm_001", 0.0, kind="ground_finished", note=True,
                                          raw="TESVİYE 0.00 KOTU : 93.20", absolute=93.2)))
    g = b["site"]["ground"]
    assert g["source"] == "site_note" and g["levels"][0]["z"]["value"] == 0.0
    assert g["levels"][0]["z"]["method"] == "vector" and g["levels"][0]["from_mark"] == "lm_001"
    e = _ent(b)
    assert e["rise"] == 0.0 and e["solution"] == "none"                         # flush, as drawn
    assert "ground" in b["level_marks"][0]["used_for"]


def test_three_ground_marks_give_a_planar_terrain_and_the_ground_at_the_door():
    b = M.infer_levels(_with_marks(F.mark("lm_001", -0.45, kind="ground_finished", point=(8.0, -3.0)),
                                   F.mark("lm_002", -0.45, kind="ground_finished", point=(-3.0, -3.0)),
                                   F.mark("lm_003", -0.05, kind="ground_finished", point=(-3.0, 11.0))))
    g = b["site"]["ground"]
    assert g["source"] == "marks" and g["terrain"] == "planar" and len(g["points"]) == 3
    assert g["surface"]["kind"] == "planar" and g["surface"]["inferred"] is False
    e = _ent(b)
    assert e["ground_z"] == -0.45 and e["ground_source"] == "ground mark lm_001"   # the mark within 5 m
    assert e["steps"]["count"] == 3
    from wenart.blender import site as S
    assert S.terrain_model(b, [(-0.1, -0.1), (10.1, -0.1), (10.1, 8.1), (-0.1, 8.1)])["kind"] == "planar"


def test_one_ground_mark_sets_its_side_and_an_outlier_is_listed():
    b = M.infer_levels(_with_marks(F.mark("lm_001", -0.30, kind="ground_finished", point=(5.0, -4.0)),
                                   F.mark("lm_002", -9.0, kind="ground_natural", point=(5.0, -6.0)),
                                   F.mark("lm_003", -0.30, kind="ground_finished", point=(5.0, -4.2))))
    g = b["site"]["ground"]
    assert [p["used"] for p in g["points"]] == [True, True, False]
    assert any("lm_002" in w and "median" in w for w in b["level_inference"]["warnings"])
    assert [(x["side"], x["z"]["value"]) for x in g["levels"]] == [("front", -0.3)]
    assert _ent(b)["ground_z"] == -0.3


def test_a_mark_far_from_the_building_is_not_ground():
    b = M.infer_levels(_with_marks(F.mark("lm_001", 44.8, kind="ground_finished", point=(200.0, 0.0))))
    assert b["site"]["ground"]["source"] == "D3a" and b["site"]["ground"]["points"] == []


# --------------------------------------------------------------------------
# Rooms, thresholds, level elevations
# --------------------------------------------------------------------------

def test_room_floor_offsets_and_thresholds_from_floor_marks():
    b = M.infer_levels(_with_marks(F.mark("lm_001", -0.30, kind="floor", point=(3.0, 4.0), room_id="r_living"),
                                   F.mark("lm_002", 0.0, kind="floor", point=(8.0, 4.0), room_id="r_hall")))
    rooms = {r["id"]: r for r in b["rooms"]}
    assert rooms["r_living"]["floor_offset_m"] == -0.3 and rooms["r_living"]["floor_source"] == "mark"
    assert rooms["r_living"]["floor_evidence"] and rooms["r_hall"]["floor_offset_m"] == 0.0
    ops = {o["id"]: o for o in b["openings"]}
    assert ops["d_inner"]["threshold_z"] == 0.0 and ops["d_front"]["threshold_z"] == 0.0
    assert "threshold_z" not in ops["win_1"]
    assert b["level_inference"]["inner_steps"] == [{"opening_id": "d_inner", "rise": 0.3, "low_room": "r_living",
                                                    "risers": 2, "riser": 0.15}]
    assert b["levels"][0]["elevation_source"] == "level_mark"                  # the most common floor mark: 0.00


def test_disagreeing_marks_in_a_room_are_a_conflict_and_far_marks_are_not_the_floor():
    b = M.infer_levels(_with_marks(F.mark("lm_001", 0.15, kind="floor", point=(3.0, 4.0), room_id="r_living"),
                                   F.mark("lm_002", 0.10, kind="floor", point=(4.0, 4.0), room_id="r_living"),
                                   F.mark("lm_003", 1.6, kind="floor", point=(8.0, 4.0), room_id="r_hall")))
    li = b["level_inference"]
    assert any(c["kind"] == "level_mark_mismatch" and "r_living" in c["element_ids"] for c in li["conflicts"])
    rooms = {r["id"]: r for r in b["rooms"]}
    assert rooms["r_living"]["floor_offset_m"] == pytest.approx(0.125, abs=1e-3)
    assert rooms["r_hall"]["floor_offset_m"] == 0.0 and any("r_hall" in w for w in li["warnings"])


def test_an_assumed_level_elevation_takes_the_floor_marks():
    b = F.building(label="1. Kat", order=1, elevation=3.0)
    b["levels"].insert(0, dict(b["levels"][0], id="L00", order=0, elevation=0.0, label="Zemin Kat"))
    b["level_marks"] = [F.mark("lm_001", 3.20, kind="floor", point=(3.0, 4.0), room_id="r_living"),
                        F.mark("lm_002", 3.20, kind="floor", point=(8.0, 4.0), room_id="r_hall")]
    n = M.infer_levels(b)
    lv = next(x for x in n["levels"] if x["id"] == "L0")
    assert lv["elevation"] == 3.2 and lv["elevation_source"] == "level_mark"
    assert all(r["floor_offset_m"] == 0.0 for r in n["rooms"])
    b["levels"][1]["elevation_source"] = "section"                               # a section's level is kept
    assert next(x for x in M.infer_levels(b)["levels"] if x["id"] == "L0")["elevation"] == 3.0


# --------------------------------------------------------------------------
# Plinth, basements, the M10 example
# --------------------------------------------------------------------------

def test_plinth_from_an_sb_mark_else_the_ground_floor():
    b = M.infer_levels(F.building())
    p = b["site"]["plinth"]
    assert p["top_z"] == 0.0 and p["source"] == "inferred" and p["min_height"] == 0.15
    assert {s["axis"]: s["height"] for s in p["sides"]} == {"+x": 0.15, "+y": 0.15, "-x": 0.15, "-y": 0.15}
    b = M.infer_levels(_with_marks(F.mark("lm_001", 0.45, kind="plinth", note=True, raw="SB. KOTU : 93.65")))
    p = b["site"]["plinth"]
    assert p["top_z"] == 0.45 and p["source"] == "mark" and p["sides"][0]["height"] == pytest.approx(0.6)


def test_the_m10_example_keeps_its_drawn_ground_and_records_the_basement():
    before = copy.deepcopy(EXAMPLE)
    b = M.infer_levels(EXAMPLE)
    assert EXAMPLE == before
    li = b["level_inference"]
    assert li["ground_source"] == "section" and not li["single_level_whole"]
    assert b["site"]["ground"]["levels"][0]["z"]["method"] == "vector"
    ents = {e["door_id"]: e for e in b["site"]["entrances"]}
    assert ents["d_L-1_001"]["terrain_lowered"] and ents["d_L-1_001"]["solution"] == "none"
    assert ents["d_L0_001"]["solution"] == "none" and ents["d_L0_001"]["rise"] == 0.0
    assert li["basements"] and li["basements"][0]["level_id"] == "L-1"
    p = b["site"]["plinth"]
    assert p["floors"] == [-3.0, 0.0] and {s["axis"]: s["height"] for s in p["sides"]}["-y"] == 0.15
    assert not B.validation_errors(b)


def test_infer_levels_is_idempotent():
    once = M.infer_levels(_with_marks(F.mark("lm_001", -0.30, kind="ground_finished", point=(5.0, -4.0))))
    twice = M.infer_levels(once)
    assert twice["site"]["ground"] == once["site"]["ground"] and twice["site"]["entrances"] == once["site"]["entrances"]
    assert twice["slabs"] == once["slabs"] and twice["roof"] == once["roof"]


def test_builtin_params_match_defaults_yaml():
    import yaml
    data = yaml.safe_load((ROOT / "wenart" / "defaults.yaml").read_text(encoding="utf-8"))
    assert {**data["levels"], **data["brief"]["levels"]} == M.BUILTIN_PARAMS
