"""CPU tests of Milestone 11 track C (docs/milestone11.md §1.1 E1-E14, §1.3 M2/M4-M6, §4.1, §4.4, §7, §17): the
exterior checks and the override validators (wenart/blender/exterior_checks.py), the agent's overrides in the build
(wenart/blender/overrides.py, build.prepare), the brief keys of decisions D3, D5, D6, the roof from the plan's break
line (E7), the roof terraces (D5), the openings clipped under the roof (E8), the front courts (D6), the inferred site
(E11), the facade articulation (E10), the matte ground (E12), the exterior sky (E13), the exterior cameras (E14),
the kitchens (M2) and the camera-search changes (M4, M6). Pure Python; the last tests build the example building in
Blender when a binary is available (WENART_BLENDER)."""
import copy
import json
import math
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

from wenart import brief as BR
from wenart import geometry as G
from wenart.blender import build as B
from wenart.blender import camsearch as C
from wenart.blender import cameras
from wenart.blender import cli
from wenart.blender import exterior as E
from wenart.blender import exterior_checks as X
from wenart.blender import facade as FA
from wenart.blender import geom2d
from wenart.blender import lighting as L
from wenart.blender import materials as M
from wenart.blender import overrides as O
from wenart.blender import proxies as PX
from wenart.blender import render as RD
from wenart.blender import roof as R
from wenart.blender import schemas
from wenart.blender import shell
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
# real02 of pod F1b (M10), frozen: the committed results are the M11 runs now.
REAL02 = ROOT / "tests" / "fixtures" / "m11_f1b" / "real02_building_final.json.gz"
REAL02_SCENE = ROOT / "tests" / "fixtures" / "m11_f1b" / "real02_scene_manifest.json.gz"


def _gz_json(path):
    import gzip
    return json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")


@pytest.fixture(scope="module")
def real02():
    return _gz_json(REAL02)


@pytest.fixture(scope="module")
def real02_prep(real02):
    return B.prepare(copy.deepcopy(real02), "base", None)


def _example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Brief keys (D3, D5, D6)
# --------------------------------------------------------------------------

def test_m11_brief_keys_have_their_defaults_in_both_copies():
    block = yaml.safe_load((ROOT / "wenart" / "defaults.yaml").read_text(encoding="utf-8"))["brief"]
    assert block["markers_in_final"] is False and block["roof_terraces"] == "auto"
    assert block["site_options"] == {"front_court": "auto"}
    assert B.M11_BRIEF_DEFAULTS == {"markers_in_final": block["markers_in_final"],
                                    "roof_terraces": block["roof_terraces"],
                                    "site_options.front_court": block["site_options"]["front_court"]}


def test_brief_site_mapping_and_yaml_booleans():
    out = BR.merge_brief({"site": {"mode": "ground", "front_court": True}, "roof_terraces": "closed",
                          "markers_in_final": True})
    v = out["values"]
    assert v["site"] == "ground" and v["site_options"] == {"front_court": "yes"} and out["warnings"] == []
    assert v["roof_terraces"] == "closed" and v["markers_in_final"] is True
    assert BR.front_court({"values": BR.merge_brief({"site_options": {"front_court": False}})["values"]}) == "no"
    bad = BR.merge_brief({"roof_terraces": "open", "site_options": {"front_court": "maybe"}})
    assert bad["values"]["roof_terraces"] == "auto" and bad["values"]["site_options"]["front_court"] == "auto"
    assert len(bad["warnings"]) == 2 and {"roof_terraces", "site_options.front_court"} <= set(bad["assumed"])


def test_build_brief_args_carry_the_m11_keys(real02):
    args = B.brief_args(real02, {"values": {"roof_terraces": "closed", "site_options": {"front_court": True}}})
    assert args["roof_terraces"] == {"value": "closed", "assumed": False}
    assert args["site_options.front_court"]["value"] == "yes"
    assert args["markers_in_final"] == {"value": False, "assumed": True}


# --------------------------------------------------------------------------
# D3 markers
# --------------------------------------------------------------------------

def test_markers_switch_and_the_unverified_items():
    try:
        assert M.markers_on() is False                   # the D3 default
        M.set_markers(True)
        assert M.markers_on() is True
    finally:
        M.set_markers(False)
    b = {"rooms": [{"id": "r1", "status": "unverified", "level_id": "L0"}, {"id": "r2", "status": "verified"}],
         "furniture": [{"id": "f1", "status": "unverified", "level_id": "L0"},
                       {"id": "f2", "status": "unverified", "build": False}]}
    assert B.unverified_items(b) == [{"id": "r1", "kind": "room", "level_id": "L0"},
                                     {"id": "f1", "kind": "furniture", "level_id": "L0"}]


# --------------------------------------------------------------------------
# Roof: E7 break line, D5 terraces, E8 clipped openings, the agent's roof
# --------------------------------------------------------------------------

def test_real02_mansard_uses_the_break_line_on_the_uncut_sides(real02_prep):
    roof = real02_prep["roof"]
    ids = {p["id"]: p for p in roof["planes"]}
    assert {"rp_north_lower", "rp_north_upper", "rp_south_lower", "rp_south_upper"} <= set(ids)
    assert ids["rp_south_lower"]["slope_deg"] == pytest.approx(37.69, abs=0.05)       # was the 40.4 to the ridge
    assert ids["rp_south_upper"]["slope_deg"] == pytest.approx(18.5, abs=0.05)
    assert roof["ridge_z"] == pytest.approx(6.789) and roof["convex"]
    assert R.surface_z(roof["equations"], 7.586, 1.701) == pytest.approx(5.35, abs=1e-3)   # the break line
    assert not any("vs the drawn section" in w for w in roof["warnings"])


def test_d5_terraces_auto_cut_closed(real02):
    roof = real02["roof"]
    auto, dec, warnings = R.terrace_decisions(roof, real02, "auto")
    assert [d["decision"] for d in dec] == ["cut", "cut"] and len(auto["openings"]) == 2
    assert dec[0]["doors"] == ["d_L1_003"] and "section r6 draws the roof closed" in warnings[0]
    closed, dec, warnings = R.terrace_decisions(roof, real02, "closed")
    assert closed["openings"] == [] and all(d["decision"] == "closed" and d["conflict"] for d in dec)
    # a terrace room with no door on the plan stays under the roof in auto
    b = copy.deepcopy(real02)
    b["openings"] = [o for o in b["openings"] if o["id"] not in ("d_L1_003", "d_L1_006")]
    _, dec, _ = R.terrace_decisions(roof, b, "auto")
    assert [d["decision"] for d in dec] == ["closed", "closed"] and "has no door" in dec[0]["reason"]
    # the build: brief roof_terraces closed -> no roof opening, the conflict listed
    prep = B.prepare(copy.deepcopy(real02), "base", {"values": {"roof_terraces": "closed"}})
    assert prep["roof"]["openings"] == [] and prep["open_rooms"] == set()
    assert any("draws the roof closed" in w for w in prep["warnings"])


def test_e8_assumed_openings_are_clipped_under_the_roof(real02, real02_prep):
    clips = {c["opening_id"]: c for c in real02_prep["clips"]}
    assert {"win_L1_001", "win_L1_002", "d_L1_003"} <= set(clips)
    vb = real02_prep["building"]
    lv = next(lv for lv in vb["levels"] if lv["id"] == "L1")
    cut = R.wall_cut(real02_prep["roof"])
    assert B.openings_through_roof(vb, lv, cut) == []                  # nothing pokes through any more
    w = next(o for o in vb["openings"] if o["id"] == "win_L1_001")
    assert w["height"] == clips["win_L1_001"]["height"] < 1.2 and "height" in w["assumed"] and w["clipped_by_roof"]
    # a drawn height is never changed
    b = copy.deepcopy(real02)
    for o in b["openings"]:
        if o["id"] == "win_L1_001":
            o["assumed"] = [a for a in o["assumed"] if a != "height"]
    prep = B.prepare(b, "base", None)
    assert "win_L1_001" not in {c["opening_id"] for c in prep["clips"]}
    assert any(s.startswith("win_L1_001: its top") for s in
               B.openings_through_roof(prep["building"], next(x for x in prep["building"]["levels"] if x["id"] == "L1"),
                                       R.wall_cut(prep["roof"])))


def test_agent_roof_override(real02):
    b = copy.deepcopy(real02)
    b["agent_overrides"] = {"exterior": {"roof": {"type": "hip", "pitch_deg": 30.0, "overhang_m": 0.6}}, "round": 1}
    prep = B.prepare(b, "base", None)
    assert prep["roof"]["type"] == "hip" and prep["roof"]["planes_source"] == "derived"
    assert {p["slope_deg"] for p in prep["roof"]["planes"]} == {30.0}
    assert [c["field"] for c in prep["overrides_applied"]["roof"]] == ["type", "pitch_deg", "profile", "overhang_m"]
    assert prep["overrides_applied"]["round"] == 1


# --------------------------------------------------------------------------
# Overrides: none = the M10 build; cameras, materials, sun, site
# --------------------------------------------------------------------------

def _strip(prep):
    keep = ("roof", "site", "clips", "terraces", "outlines", "ground_outline", "faces", "warnings", "assumed", "slabs")
    return json.loads(json.dumps({k: prep[k] for k in keep}, default=str))


def test_without_agent_overrides_the_build_is_unchanged(real02):
    base = B.prepare(copy.deepcopy(real02), "base", None)
    assert base["overrides_applied"] is None
    for empty in (None, {}, {"cameras": [], "exterior": {}, "materials": {}, "round": 0}):
        b = copy.deepcopy(real02)
        b["agent_overrides"] = empty
        prep = B.prepare(b, "base", None)
        assert prep["overrides_applied"] is None and _strip(prep) == _strip(base)
    style = {"walls": {"material": "plaster_white"}, "lighting": {"sun_azimuth_deg": 210}}
    assert O.apply_style(style, {}) == (style, [])
    assert O.apply_looks({"facade": {"material": "render"}}, {})[1] == []
    assert O.apply_sun(style, real02) == (style, None)
    plans = [{"name": "cam_a", "room_id": "r"}]
    assert O.apply_cameras(plans, []) == (plans, [])
    assert O.site_options(real02, "auto") == {"path": True, "fence": "hedge", "trees": 3, "front_court": "auto",
                                              "source": {"path": "default", "fence": "default", "trees": "default",
                                                         "front_court": "brief"}}


def test_camera_overrides_set_add_remove():
    plans = [{"name": "cam_r_1", "room_id": "r", "index": 1, "lens_mm": 18.0},
             {"name": "cam_r_2", "room_id": "r", "index": 2, "lens_mm": 16.0}]
    entries = [{"action": "set", "view_id": "cam_r_1", "kind": "interior", "room_id": "r", "position": [1, 2, 1.4],
                "target": [2, 2, 1.4], "reason": "show the bed"},
               {"action": "remove", "view_id": "cam_r_2", "kind": "interior", "room_id": "r", "reason": "a bare wall"},
               {"action": "add", "view_id": "cam_r_9", "kind": "interior", "room_id": "r", "position": [3, 3, 1.4],
                "target": [3, 4, 1.4], "lens_mm": 20.0, "reason": "the window"},
               {"action": "remove", "view_id": "cam_x", "kind": "interior", "room_id": "r", "reason": "x"},
               {"action": "add", "view_id": "cam_s_1", "kind": "interior", "room_id": "s", "position": [0, 0, 1.4],
                "target": [1, 0, 1.4], "reason": "another level"}]
    out, applied = O.apply_cameras(plans, entries, "L0", {"r"})
    assert [p["name"] for p in out] == ["cam_r_1", "cam_r_9"]
    assert out[0]["position"] == [1.0, 2.0, 1.4] and out[0]["lens_mm"] == 18.0 and out[0]["policy"] == "agent"
    assert out[0]["placement"] == "agent override: show the bed" and out[0]["index"] == 1
    assert out[1]["lens_mm"] == 20.0 and out[1]["shift_y"] == 0.0 and out[1]["pitch_deg"] == 0.0
    assert [a["result"] for a in applied] == ["replaced", "removed", "added", "not found"]
    b = {"agent_overrides": {"cameras": entries + [{"action": "add", "view_id": "ext_9", "position": [20, 0, 1.6],
                                                    "target": [0, 0, 1.6], "reason": "street"}]}}
    assert [e["view_id"] for e in O.camera_entries(b, "exterior")] == ["ext_9"]
    assert len(O.camera_entries(b, "interior")) == 5


def test_material_and_sun_overrides():
    style = {"walls": {"material": "plaster_white", "colour": "white"}, "window_frame": {"material": "pvc_white"},
             "lighting": {"sun_azimuth_deg": 210.0, "sun_elevation_deg": 35.0}}
    b = {"agent_overrides": {"materials": {"walls": "lime_plaster", "frames": "dark_bronze", "facade": "brick_red",
                                           "ground": "gravel"},
                             "exterior": {"sun": {"azimuth_deg": 120.0, "elevation_deg": 40.0}}}}
    mats = O.materials_of(b)
    assert mats == {"walls": "lime_plaster", "window_frame": "dark_bronze", "facade": "brick_red", "ground": "gravel"}
    new, applied = O.apply_style(style, mats)
    assert new["walls"]["material"] == "lime_plaster" and new["window_frame"]["outside"]["material"] == "dark_bronze"
    assert style["walls"]["material"] == "plaster_white"                           # the input is not changed
    looks, applied = O.apply_looks({"facade": {"material": "render"}, "garden": {"material": "grass"},
                                    "window_frame": {"material": "pvc_white"}}, mats)
    assert looks["facade"]["material"] == "brick_red" and looks["facade"]["source"] == "agent"
    assert looks["garden"]["material"] == "gravel" and looks["window_frame"]["material"] == "dark_bronze"
    lit, sun = O.apply_sun(style, b)
    assert lit["lighting"]["sun_azimuth_deg"] == 120.0 and lit["lighting"]["sun_elevation_deg"] == 40.0
    assert sun["azimuth_deg"] == {"value": 120.0, "was": 210.0}


def test_site_overrides_reach_the_site_plan(real02):
    b = copy.deepcopy(real02)
    b["agent_overrides"] = {"exterior": {"site": {"fence": "fence", "trees": 0, "front_court": "no", "path": False}}}
    prep = B.prepare(b, "base", None)
    inf = prep["site"]["inferred"]
    assert inf["trees"] == [] and inf["paths"] == [] and {s["kind"] for s in inf["boundary"]} == {"fence"}
    assert not any(w.get("kind") == "front_court" for w in prep["site"]["wells"])
    assert prep["overrides_applied"]["site"] == {"path": "agent", "fence": "agent", "trees": "agent",
                                                 "front_court": "agent"}


# --------------------------------------------------------------------------
# Site: D6 front courts, E11 inferred site
# --------------------------------------------------------------------------

def test_d6_front_courts_of_real02(real02_prep):
    wells = real02_prep["site"]["wells"]
    courts = [w for w in wells if w.get("kind") == "front_court"]
    assert len(courts) == 3 and all(w["source"] == "inferred" and w["inferred"] for w in courts)
    front = next(w for w in courts if w["outward"] == [0.0, -1.0])
    assert front["opening_ids"] == ["win_L-1_001", "win_L-1_002"]                # one court for the two windows
    assert front["floor_z"] == pytest.approx(-3.05) and front["curb"] == S.COURT["parapet"]
    assert any(a["field"].startswith("light_well:") and "front court" in a["reason"]
               for a in real02_prep["site"]["assumed"])
    # brief front_court: no -> the M10 light wells
    vb = real02_prep["building"]
    wells, _ = S.light_wells(vb, vb["levels"], real02_prep["site"]["terrain"], real02_prep["ground_outline"],
                             real02_prep["outlines"], front_court="no")
    assert len(wells) == 4 and all(w["source"] == "assumed" and "kind" not in w for w in wells)


def test_e11_inferred_site_of_real02(real02_prep):
    inf = real02_prep["site"]["inferred"]
    assert inf["plot_inferred"] and inf["main"]["axis"] == "+y" and inf["main"]["source"] == "entrance doors"
    assert [e["opening_id"] for e in inf["entrances"]] == ["d_L0_011", "d_L0_012"] and inf["steps"] == []
    assert len(inf["paths"]) == 2 and all(p["width"] == S.INFERRED["path_width"] for p in inf["paths"])
    plot = inf["plot"]
    for p in inf["paths"]:                                       # from the door out to the plot edge
        far = max(q[1] for q in p["polygon"])
        assert far == pytest.approx(max(q[1] for q in plot) + 0.05, abs=1e-6)
    gaps = [seg for seg in inf["boundary"] if seg["kind"] == "hedge"]
    assert len(gaps) >= 6                                          # 4 edges, the +y edge cut twice by the paths
    windows = S.outer_openings(real02_prep["building"], real02_prep["building"]["levels"],
                               real02_prep["ground_outline"], real02_prep["outlines"], kinds=("window",))
    front_y = max(q[1] for q in real02_prep["ground_outline"])
    assert 1 <= len(inf["trees"]) <= 3
    # beside the side facades, off the 30 degree lines of sight of the corner views (the F1-like tree at the front
    # corner hid half of ext_1 in the first CPU render)
    assert sorted(round(t["center"][0], 1) for t in inf["trees"]) == [-3.6, 18.8]
    for t in inf["trees"]:
        x, y = t["center"]
        assert y < front_y - S.INFERRED["front_zone_extra"] + 1e-6 and t["inferred"]
        for w in windows:
            (cx, cy), (ox, oy) = w["centre"], w["outward"]
            along, side = (x - cx) * ox + (y - cy) * oy, abs((x - cx) * -oy + (y - cy) * ox)
            assert not (0 < along < S.INFERRED["tree_window_reach"] and side < float(w["opening"]["width"]) / 2 + 2.0)
    areas = [a for a in real02_prep["site"]["areas"] if a["kind"] == "path"]
    assert len(areas) == 2 and S.AREA_LOOKS["path"] == "paving"


def test_entrance_steps_for_a_door_above_the_ground():
    e = {"opening_id": "d", "centre": (0.0, 0.0), "outward": (0.0, -1.0), "width": 1.0, "bottom": 0.5,
         "ground_z": 0.0, "rise": 0.5, "half_t": 0.15}
    st = S.entrance_steps(e)
    assert st["count"] == 2 and st["rise"] == pytest.approx(0.5 / 3, abs=1e-4)
    assert [round(b["z_top"], 4) for b in st["blocks"]] == [0.5, round(0.5 - 0.5 / 3, 4), round(0.5 - 1.0 / 3, 4)]
    assert st["end"] == pytest.approx(S.INFERRED["landing"] + 2 * S.INFERRED["step_run"])
    assert S.entrance_steps(dict(e, rise=0.0))["blocks"] == []


# --------------------------------------------------------------------------
# Facade articulation (E10)
# --------------------------------------------------------------------------

def test_e10_plinth_bands_and_surrounds(real02_prep):
    vb = real02_prep["building"]
    site = real02_prep["site"]
    plan = FA.articulation_plan(vb, vb["levels"], real02_prep["outlines"], real02_prep["ground_outline"],
                                site["terrain"], real02_prep["roof"], {"family": "modern"},
                                {"facade": {"material": "render", "colour": "warm greige"}}, site["wells"])
    kinds = {b["kind"] for b in plan["boxes"]}
    assert kinds == {"plinth", "band"} and plan["looks"]["band"]["colour"] == "white"
    assert all(b["size"][0] > 0 for b in plan["boxes"])
    plinth = [b for b in plan["boxes"] if b["kind"] == "plinth"]
    assert all(b["center"][2] == pytest.approx((-FA.DIMENSIONS["plinth_below"] + FA.DIMENSIONS["plinth_height"]) / 2)
               for b in plinth)
    # the doors at grade cut the plinth: no plinth box covers a door centre on the +y facade
    for o in ("d_L0_011", "d_L0_012"):
        door = next(x for x in vb["openings"] if x["id"] == o)
        x = door["center"][0]
        assert not any(abs(b["center"][1] - 12.0) < 0.2 and abs(b["center"][0] - x) < b["size"][0] / 2 for b in plinth)
    bands = [b for b in plan["boxes"] if b["kind"] == "band"]
    # one band at the attic floor, centred on its 0.15 m slab and 0.20 m high (the band is never thinner)
    assert {b["level_id"] for b in bands} == {"L1"} and all(abs(b["center"][2] - (3.15 - 0.075)) < 1e-6
                                                           and abs(b["size"][2] - FA.DIMENSIONS["band_height"]) < 1e-9
                                                           for b in bands)
    classic = FA.articulation_plan(vb, vb["levels"], real02_prep["outlines"], real02_prep["ground_outline"],
                                   site["terrain"], real02_prep["roof"], {"family": "classic"}, {}, site["wells"])
    assert any(b["kind"] == "surround" for b in classic["boxes"]) and classic["rules"]["surround"] == "limestone"


# --------------------------------------------------------------------------
# Ground (E12), sky (E13), sun, light under a slope
# --------------------------------------------------------------------------

def test_e12_ground_looks_are_matte_and_e13_exterior_world():
    assert M.is_ground("grass") and M.is_ground("gravel") and M.is_ground("soil") and not M.is_ground("render")
    assert M.GROUND_MIN_ROUGHNESS >= 0.85 and M.GROUND_SPECULAR <= 0.25
    rec = M.exterior_world({"mood": "warm daylight", "sun_elevation_deg": 35.0, "sun_azimuth_deg": 45.0})
    assert rec["sky_type"] == "MULTIPLE_SCATTERING" and rec["sun_disc"] is False
    assert (rec["sun_elevation_deg"], rec["sun_azimuth_deg"]) == (35.0, 45.0)
    props = {"wenart_world_exterior": "wenart_world_exterior", "wenart_world_interior": "World"}
    assert RD.world_for(props, "exterior") == "wenart_world_exterior" and RD.world_for(props, "interior") == "World"
    assert RD.world_for({}, "exterior") is None


def test_sun_from_the_main_facade_when_north_is_unknown(real02, real02_prep):
    style = {"lighting": {"sun_azimuth_deg": 210.0, "sun_elevation_deg": 35.0}}
    new, rule = B.sun_from_main_facade(style, real02_prep["main_facade"], real02)
    assert new["lighting"]["sun_azimuth_deg"] == 45.0 and "no north arrow" in rule["reason"]
    known = copy.deepcopy(real02)
    known["site"]["north_deg"] = {"value": 10.0, "method": "vector"}
    assert B.sun_from_main_facade(style, real02_prep["main_facade"], known) == (style, None)


def test_a_ceiling_light_hangs_under_the_whole_slope():
    def ceiling_at(level, x, y):
        return 4.0 - 0.8 * y                     # a slope falling to +y
    assert L.light_ceiling(ceiling_at, {}, (0.0, 1.0), 0.8, 5.0) == pytest.approx(4.0 - 0.8 * 1.4)
    assert L.light_ceiling(ceiling_at, {}, (0.0, -5.0), 0.8, 3.0) == 3.0


# --------------------------------------------------------------------------
# Exterior cameras (E14)
# --------------------------------------------------------------------------

def test_e14_exterior_cameras_of_real02(real02_prep):
    vb = real02_prep["building"]
    model = E.build_model(vb, vb["levels"], real02_prep["roof"], real02_prep["site"])
    plans, dropped = E.plan_exterior(model, vb, vb["levels"], real02_prep["site"]["plot"], variant="base")
    assert dropped == [] and [p["name"] for p in plans] == ["ext_1", "ext_2", "ext_3", "ext_4", "ext_5", "ext_6"]
    for p in plans:
        if p["view"] in ("corner", "frontal"):
            assert p["lens_mm"] == E.EYE_LENS_MM and 24.0 <= p["lens_mm"] <= 28.0
            assert E.FILL_RANGE[0] <= p["fill"] <= E.FILL_RANGE[1]
            assert p["pitch_deg"] == 0.0 and p["position"][2] == pytest.approx(E.EYE_HEIGHT)
    front = next(p for p in plans if p["view"] == "frontal")
    assert front["sides"] == ["back"] and front["main_facade"] == "+y" and front["position"][1] > 12.0
    assert front["position"][0] == pytest.approx(7.586, abs=0.01)
    for p in plans:
        if p["view"] == "corner":                    # 30 degrees off the facade it faces, not 45
            k = p["corner"]
            corner = geom2d.rectangle_corners(geom2d.oriented_rectangle(model.outline))[k - 1]
            dx, dy = p["position"][0] - corner[0], p["position"][1] - corner[1]
            ang = math.degrees(math.atan2(abs(dx), abs(dy)))           # off the +-y facade normal
            assert ang == pytest.approx(30.0, abs=0.01)


# --------------------------------------------------------------------------
# Kitchens (M2)
# --------------------------------------------------------------------------

def _kitchen(counter_rot=0.0, front=None, ctype="kitchen_counter", room_type="kitchen", center=(2.0, 0.33)):
    room = {"id": "k", "level_id": "L0", "room_type": room_type, "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    piece = {"id": "c1", "type": ctype, "room_id": "k", "level_id": "L0", "front_deg": front,
             "footprint": {"center": list(center), "size": [2.4, 0.6], "rotation_deg": counter_rot}}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [room], "furniture": [piece]}


def test_m2_kitchen_walls_floor_and_splashback():
    assert "kitchen" not in shell.WET_WALL_ROOM_TYPES and "kitchen" not in shell.NO_SKIRTING_TYPES
    room = {"room_type": "kitchen"}
    style = {"floor": {"material": "wood_oak_light"}, "wet_floor": {"material": "tiles_light"}}
    assert shell.floor_style(room, style)[0]["material"] == "tiles_light"            # oak is not wet-safe
    style_tiles = {"floor": {"material": "terracotta"}, "wet_floor": {"material": "tiles_light"}}
    assert shell.floor_style(room, style_tiles)[0]["material"] == "terracotta"        # the brief's floor
    assert shell.floor_style({"room_type": "bathroom"}, style_tiles)[0]["material"] == "tiles_light"
    b = _kitchen(front=90.0)
    (band,) = shell.splashback_plan(b, b["levels"][0])
    assert band["size"] == [pytest.approx(2.4), shell.SPLASHBACK["thickness"], shell.SPLASHBACK["height"]]
    assert band["center"][2] == pytest.approx(0.9 + 0.3) and band["center"][1] == pytest.approx(0.006)
    assert band["center"][0] == pytest.approx(2.0)
    assert shell.splashback_plan(_kitchen(center=(2.0, 1.5)), b["levels"][0]) == []          # an island: none
    bed = _kitchen(room_type="bedroom")
    assert shell.splashback_plan(bed, bed["levels"][0]) == []
    from wenart.blender import looks
    style = {"walls": {"material": "plaster_white"}, "kitchen_walls": {"material": "tiles_subway"}}
    assert looks.wall_face_material(style, {"room_type": "kitchen"})["material"] == "tiles_subway"
    assert looks.wall_face_material(style, {"room_type": "bedroom"})["material"] == "plaster_white"


# --------------------------------------------------------------------------
# Camera search (M4, M6)
# --------------------------------------------------------------------------

def _room(polygon, furniture=(), openings=(), walls=None):
    walls = walls or [{"id": f"w{i}", "level_id": "L0", "start": list(polygon[i]),
                       "end": list(polygon[(i + 1) % len(polygon)]), "thickness": 0.2} for i in range(len(polygon))]
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls, "openings": list(openings),
            "rooms": [{"id": "r", "level_id": "L0", "room_type": "living", "polygon": [list(p) for p in polygon]}],
            "furniture": list(furniture)}


def test_m4_a_fallback_point_gives_one_view():
    # an 8 m2 room filled by a table: no free point; the area rule says 3 views, the fallback point gives 1
    table = {"id": "t", "type": "table_dining", "room_id": "r", "level_id": "L0", "height": 0.75,
             "footprint": {"center": [2.0, 1.0], "size": [3.6, 1.6], "rotation_deg": 0.0}}
    b = _room([(0, 0), (4, 0), (4, 2), (0, 2)], [table])
    room = b["rooms"][0]
    points, warning = C.candidate_positions(room, b)
    assert warning and len(points) == 1 and C.room_view_count(room, b) == 3
    plans, _ = C.plan_room(room, b)
    assert len(plans) == 1 and plans[0]["warning"].startswith(warning)


def test_m6_door_clearance_and_doors_beyond_the_near_distance():
    door = {"id": "d", "type": "door", "level_id": "L0", "wall_id": "w0", "center": [1.0, 0.0], "width": 0.9,
            "height": 2.1, "sill_height": 0.0}
    b = _room([(0, 0), (5, 0), (5, 4), (0, 4)], openings=[door])
    room = b["rooms"][0]
    points, _ = C.candidate_positions(room, b)
    segs = cameras.door_segments(room, b)
    assert segs and all(min(G.point_segment_distance(p, a, q)
                            for _i, a, q in segs) >= cameras.DOOR_CLEARANCE_M - 1e-9 for p in points)
    model = C.RoomModel(room, b)
    assert list(model.door_codes) == [C.FIRST_ELEMENT] and list(model.edge_codes) == [C.FIRST_ELEMENT]
    # a camera beside the door looking along the wall: the leaf is near, at the frame edge -> no opening credit,
    # an edge penalty
    a, bb = C.ray_grid(None, 18.0, shift_y=C.SHIFT_Y)
    dirs = C.yaw_directions([180.0], a, bb)
    labels, depth = model.cast((1.8, 0.5, 1.25), dirs)
    (m,) = model.measure(labels, depth, C.border_mask(), C.near_distance(18.0))
    raw = float((labels[0] == C.FIRST_ELEMENT).mean())
    assert raw > 0.05 and m["open"] < raw and m["edge_near"] > C.SCORE["penalties"]["edge_near"][1]
    assert C.score_terms(m)["penalties"] > C.score_terms(dict(m, edge_near=0.0))["penalties"]


def test_proxies_held_pieces_need_no_shapely(monkeypatch):
    monkeypatch.setitem(sys.modules, "shapely", None)
    monkeypatch.setitem(sys.modules, "shapely.geometry", None)
    holder = {"id": "u", "type": "unknown", "footprint": {"center": [0, 0], "size": [4, 3], "rotation_deg": 0}}
    inside = {"id": "a", "footprint": {"center": [0.5, 0], "size": [1, 1], "rotation_deg": 30}}
    half = {"id": "b", "footprint": {"center": [2.0, 0], "size": [1, 1], "rotation_deg": 0}}
    out = {"id": "c", "footprint": {"center": [5, 5], "size": [1, 1], "rotation_deg": 0}}
    assert PX.held_pieces(holder, [holder, inside, half, out]) == ["a", "b"]
    assert PX._convex_overlap(PX._footprint_polygon(holder["footprint"]),
                              PX._footprint_polygon(half["footprint"])) == pytest.approx(0.5)


# --------------------------------------------------------------------------
# Exterior checks (X1-X8, V1, V3) and the override validators
# --------------------------------------------------------------------------

def test_override_schemas_are_strict_json_schemas():
    for schema in (X.CAMERA_OVERRIDE_SCHEMA, X.EXTERIOR_OVERRIDE_SCHEMA, X.MATERIAL_OVERRIDE_SCHEMA):
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
    assert X.validate_camera_override({}, {"action": "remove", "view_id": "cam_a", "reason": "x", "zoom": 2})["ok"] \
        is False


def test_check_exterior_finds_the_known_real02_problems_in_the_committed_f1b_scene(real02):
    scene = _gz_json(REAL02_SCENE)
    r = X.check_exterior(real02, scene)
    by = {(v["check"], v["target"]) for v in r["violations"]}
    for target in ("dec_L1_006", "dec_L1_007", "f_L1_001", "f_L1_002"):    # E3, E4: through the roof
        assert ("X2", target) in by
    assert ("X6", "exterior") in by                                  # no frontal view of the entrance facade
    assert ("X7", "sun") in by and ("X7", "sky") in by               # the sun behind, the HDRI sky
    assert ("X3", "r_L0_yatak_odasi_3") in by                        # E10: a long blank bedroom facade
    assert r["score"] == 0
    for v in r["violations"]:
        assert set(v) == {"check", "severity", "target", "room_id", "message", "metrics"}
        assert v["severity"] in ("critical", "major", "minor")


def test_check_views_v1_and_v3_on_the_committed_scene(real02):
    scene = _gz_json(REAL02_SCENE)
    r = X.check_views(real02, scene)["views"]
    assert all(any(v["check"] == "V3" for v in vs) for vs in r.values())     # stripes in every F1b view
    assert any(v["check"] == "V1" and "inside f_L0_001 (stair)" in v["message"] for v in r["cam_r_L0_oda_1"])
    clean = X.check_views(real02, dict(scene, materials={}, markers_in_final=False))["views"]
    assert not any(v["check"] == "V3" for vs in clean.values() for v in vs)


def test_validate_camera_override_interior_and_exterior(real02):
    room = next(r for r in real02["rooms"] if r["id"] == "r_L0_yatak_odasi")
    xs, ys = [p[0] for p in room["polygon"]], [p[1] for p in room["polygon"]]
    base = {"action": "set", "view_id": "cam_r_L0_yatak_odasi_1", "kind": "interior", "room_id": room["id"],
            "reason": "the bed"}
    free = None
    for i in range(1, 20):
        for j in range(1, 20):
            p = (min(xs) + (max(xs) - min(xs)) * i / 20, min(ys) + (max(ys) - min(ys)) * j / 20)
            cam = dict(base, position=[p[0], p[1], 1.4], target=[p[0] + 1, p[1], 1.4])
            if X.validate_camera_override(real02, cam)["ok"]:
                free = cam
                break
        if free:
            break
    assert free is not None
    low = X.validate_camera_override(real02, dict(free, position=[*free["position"][:2], 0.5]))
    assert not low["ok"] and any("eye height" in f for f in low["failed"])
    out = X.validate_camera_override(real02, dict(free, position=[-3.0, -3.0, 1.4], target=[0.0, 0.0, 1.4]))
    assert not out["ok"] and any("outside its room" in f for f in out["failed"])
    assert not X.validate_camera_override(real02, dict(free, position=None))["ok"]
    ext = {"action": "add", "view_id": "ext_9", "kind": "exterior", "position": [7.5, 30.0, 1.6],
           "target": [7.5, 6.0, 1.6], "lens_mm": 26.0, "reason": "street view"}
    assert X.validate_camera_override(real02, ext) == {"ok": True, "failed": []}
    inside = X.validate_camera_override(real02, dict(ext, position=[7.5, 6.0, 1.6]))
    assert not inside["ok"] and any("inside the building" in f for f in inside["failed"])
    high = X.validate_camera_override(real02, dict(ext, position=[-12.0, -9.0, 16.0]))
    assert high["ok"]
    assert X.validate_camera_override(real02, {"action": "remove", "view_id": "ext_2", "reason": "dull"})["ok"]


def test_validate_exterior_and_material_overrides(real02):
    assert X.validate_exterior_override(real02, {"roof": {"type": "hip", "pitch_deg": 30.0}})["ok"]
    assert not X.validate_exterior_override(real02, {"roof": {"pitch_deg": 80.0}})["ok"]          # schema
    steep = X.validate_exterior_override(real02, {"roof": {"type": "gable", "pitch_deg": 65.0}})
    assert not steep["ok"] and "5-60" in steep["failed"][0]
    assert not X.validate_exterior_override(real02, {"sun": {"elevation_deg": 2.0}})["ok"]
    assert X.validate_exterior_override(real02, {"ground": "gravel", "site": {"fence": "fence", "trees": 2}})["ok"]
    bad = X.validate_exterior_override(real02, {"ground": "render"})
    assert not bad["ok"] and "plaster look" in bad["failed"][0]
    assert not X.validate_exterior_override(real02, {"site": {"fence": "wall"}})["ok"]
    style = {}
    assert X.validate_material_override(style, {"floor": "wood_oak_natural", "frames": "dark_bronze"})["ok"]
    wet = X.validate_material_override(style, {"wet_floor": "wood_oak_light"})
    assert not wet["ok"]
    assert not X.validate_material_override(style, {"floor": "unobtainium"})["ok"]
    assert not X.validate_material_override(style, {"ceiling_fan": "steel_black"})["ok"]           # schema


# --------------------------------------------------------------------------
# Blender: the example building, whole, with the M11 exterior
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def example_scene(tmp_path_factory):
    if BLENDER is None:
        pytest.skip("no Blender binary (WENART_BLENDER)")
    tmp = tmp_path_factory.mktemp("m11_example")
    path = tmp / "building.json"
    path.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--out", str(out), "--no-textures",
                                             "--no-preview", "--no-glb", "--camera-policy", "search"],
                    log_path=out / "build.log")
    probe = tmp / "probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    cli.run_blender(probe, [str(tmp / "probe.json")], blend=str(out / "scene.blend"))
    return {"manifest": json.loads((out / "scene_manifest.json").read_text(encoding="utf-8")),
            "probe": json.loads((tmp / "probe.json").read_text(encoding="utf-8"))}


PROBE = """
import bpy, json, sys
out = sys.argv[sys.argv.index("--") + 1]
scene = bpy.context.scene
g = bpy.data.objects.get("ground")
mat = g.data.materials[0] if g else None
nodes = mat.node_tree.nodes if mat else []
bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
w = bpy.data.worlds.get(scene.get("wenart_world_exterior") or "")
sky = next((n for n in w.node_tree.nodes if n.bl_idname == "ShaderNodeTexSky"), None) if w else None
json.dump({"ground_max": any(n.bl_idname == "ShaderNodeMath" and n.operation == "MAXIMUM" for n in nodes),
           "ground_spec": bsdf.inputs["Specular IOR Level"].default_value if bsdf else None,
           "world_exterior": w.name if w else None, "world": scene.world.name,
           "sky": sky.sky_type if sky else None, "sun_disc": sky.sun_disc if sky else None,
           "stripes": any(n.bl_idname == "ShaderNodeTexWave" for m in bpy.data.materials if m.use_nodes and m.node_tree
                          for n in m.node_tree.nodes),
           "objects": sorted(o.name for o in bpy.data.objects)}, open(out, "w"))
"""


@needs_blender
def test_example_build_has_the_m11_exterior(example_scene):
    m, p = example_scene["manifest"], example_scene["probe"]
    schemas.validate_scene_manifest(m)
    assert p["ground_max"] and p["ground_spec"] == pytest.approx(M.GROUND_SPECULAR)         # E12
    assert p["world_exterior"] == "wenart_world_exterior" and p["sky"] == "MULTIPLE_SCATTERING"   # E13
    assert p["sun_disc"] is False and p["world"] != p["world_exterior"]
    assert m["lighting"]["world_exterior"]["kind"] == "sky"
    assert m["markers_in_final"] is False and not p["stripes"]                                 # D3
    kinds = {o["kind"] for o in m["objects"]}
    assert "facade_detail" in kinds                                                           # E10
    assert "splashback_r_L-1_mutfak" in p["objects"]                                          # M2
    assert m["whole_building"]["facade_details"]
    assert m["agent_overrides"] is None
    ext = [c for c in m["cameras"] if c.get("kind") == "exterior"]
    assert any(c["view"] == "corner" and c["lens_mm"] == E.EYE_LENS_MM for c in ext)


@needs_blender
def test_example_build_applies_the_agent_overrides(tmp_path):
    """§17.3: the build reads building["agent_overrides"]: a fixed exterior camera added, an interior camera removed,
    the roof turned into a hip roof, the facade material set; the manifest records what was applied."""
    b = _example()
    b["agent_overrides"] = {
        "round": 2,
        "cameras": [{"action": "add", "view_id": "ext_20", "kind": "exterior", "position": [5.0, -25.0, 1.6],
                     "target": [5.0, 4.0, 1.6], "lens_mm": 26.0, "reason": "street view"},
                    {"action": "remove", "view_id": "cam_r_L0_banyo_1", "kind": "interior", "room_id": "r_L0_banyo",
                     "reason": "a bare wall"}],
        "exterior": {"roof": {"type": "hip"}, "site": {"trees": 0}},
        "materials": {"facade": "brick_red"}}
    path = tmp_path / "building.json"
    path.write_text(json.dumps(b), encoding="utf-8")
    out = tmp_path / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--out", str(out), "--no-textures",
                                             "--no-preview", "--no-glb", "--camera-policy", "search"],
                    log_path=out / "build.log")
    m = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_scene_manifest(m)
    names = {c["name"]: c for c in m["cameras"]}
    assert "ext_20" in names and names["ext_20"]["policy"] == "agent" and names["ext_20"]["sides"]
    assert "cam_r_L0_banyo_1" not in names
    applied = m["agent_overrides"]
    assert applied["round"] == 2 and sorted(c["result"] for c in applied["cameras"]) == ["added", "removed"]
    assert [c["field"] for c in applied["roof"]] == ["type"] and m["whole_building"]["roof"]["type"] == "hip"
    assert m["exterior_looks"]["facade"]["material"] == "brick_red" and m["exterior_looks"]["facade"]["source"] == "agent"
    assert applied["site"] == {"trees": "agent"}
