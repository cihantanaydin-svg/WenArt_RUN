"""30 Oct 2026: the fixes after real04 run 20261029-201533-full (CPU; the run's files are the committed latest baseline,
results/baseline/latest, and tests/fixtures/wall_items_real04_20261030.json, cut from its building as built).

1. An agent or Argus camera pose is held to the camera search's own rules (``camsearch.pose_problems``: inside its
   room, eye height, headroom under the roof's sloped ceiling, a frame that is not blocked, the room's main pieces in
   the frame) on the building with its roof's ceilings (``camsearch.with_roof_ceilings``); a refused pose falls back to
   the nearest searched pose, in the agent's tool (``tools.searched_fallback``) and in the build
   (``build.check_agent_interior_plans``). Argus's cam_r_L1_banyo_1 stood 0.21 m over the sloped attic ceiling.
2. The see-through wardrobe's contents (lesson UL135, ``wardrobe_contents``): garments with sleeves and collars on
   hangers, woven fabrics in the room's palette, folded stacks, shoes and boxes, a light in every bay.
3. The rig light of a view's white point as its walls get it (``render.wall_rig_mix``) and the orange check's paints
   (``looks.wall_paint_key``).
4. The design-detail GPU test reads the feature walls from the build's records.
5. Wall items clear of openings, other wall items and what stands in front (lessons UL134, UL139, ``wall_items``).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import math
import os
from pathlib import Path

import pytest

from wenart.blender import build as BD
from wenart.blender import camsearch as CSR
from wenart.blender import exterior_checks as EC
from wenart.blender import looks
from wenart.blender import modules as MOD
from wenart.blender import render as R
from wenart.blender import wall_items as WI
from wenart.blender import wardrobe_contents as WC
from wenart.blender import wardrobe_fronts as WF

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "baseline" / "latest"
FIXTURE = ROOT / "tests" / "fixtures" / "wall_items_real04_20261030.json"
ARGUS_POSE = {"view_id": "cam_r_L1_banyo_1", "action": "set", "kind": "interior", "room_id": "r_L1_banyo",
              "position": [5.7185, 11.435, 4.4], "target": [6.2185, 10.568975, 4.4], "lens_mm": 16.0,
              "reason": "Argus: a black frame; move it to a free point with headroom (fixes a:F288)"}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real04():
    path = BASE / "furniture" / "real04" / "building_final.json"
    if not path.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    return _json(path)


# 30 Oct 2026: the cameras and exposures these tests read are run 20261029-201533-full's, frozen (a later promotion of
# the latest baseline changes them)
FROZEN = ROOT / "tests" / "fixtures" / "real04_201533_cameras_exposure.json"


@pytest.fixture(scope="module")
def scene04():
    path = BASE / "renders" / "real04" / "scene_manifest.json"
    if not path.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    return _json(path)


# ------------------------------------------------------------------------------------------- 1. agent camera poses

def test_the_roof_gives_the_top_level_its_sloped_ceiling(real04):
    b = CSR.with_roof_ceilings(real04)
    l1 = next(lv for lv in b["levels"] if lv["id"] == "L1")
    assert l1["ceiling_planes"] and l1["open_rooms"] == ["r_L1_teras", "r_L1_teras_2"]
    assert not any("ceiling_planes" in lv for lv in real04["levels"])               # the input stays as it was
    assert CSR.with_roof_ceilings(b) is b                                          # a prepared building: as it is
    room = next(r for r in b["rooms"] if r["id"] == "r_L1_banyo")
    model = CSR.RoomModel(room, b)
    assert model.ceiling_at(5.7185, 11.435) - 3.15 == pytest.approx(1.041, abs=0.01)   # 1.04 m over the floor there


def test_a_lens_over_the_ceiling_is_blocked_in_the_ray_model(real04):
    b = CSR.with_roof_ceilings(real04)
    s = CSR.score_camera(b, dict(ARGUS_POSE, name="cam_r_L1_banyo_1"))
    assert s["terms"]["blocked"] and s["shares"]["min_depth"] < CSR.SCORE["blocked_min_depth"]
    # the same pose on the furniture stage's building (no ceiling planes) was free: the Argus edit was accepted
    flat = copy.deepcopy(real04)
    for lv in flat["levels"]:
        lv["ceiling_planes"] = []
    assert not CSR.score_camera(flat, dict(ARGUS_POSE, name="x"))["terms"]["blocked"]


def test_the_argus_pose_over_the_sloped_ceiling_is_refused_with_the_search_rules(real04):
    verdict = EC.validate_camera_override(real04, ARGUS_POSE)
    assert not verdict["ok"] and verdict["pose_failed"] == verdict["failed"]
    assert any("sloped ceiling is 1.04 m over the floor" in f and "inside the ceiling or the roof" in f
               for f in verdict["failed"]), verdict
    rules = {p["rule"] for p in CSR.pose_problems(real04, ARGUS_POSE)}
    assert {"headroom", "frame"} <= rules
    # the nearest searched pose: inside the room, with headroom, a free frame
    best = CSR.nearest_searched_pose(real04, ARGUS_POSE)
    assert best is not None and best["moved_m"] < 1.5
    moved = dict(ARGUS_POSE, position=best["position"], target=best["target"], lens_mm=best["lens_mm"])
    assert CSR.pose_problems(real04, moved) == [] and EC.validate_camera_override(real04, moved)["ok"]
    b = CSR.with_roof_ceilings(real04)
    room = next(r for r in b["rooms"] if r["id"] == "r_L1_banyo")
    assert CSR.RoomModel(room, b).ceiling_at(*best["position"][:2]) - best["position"][2] >= CSR.HEADROOM_M - 1e-9


def test_the_build_moves_a_refused_agent_pose_to_the_nearest_searched_pose(real04):
    b = CSR.with_roof_ceilings(real04)
    plans = [copy.deepcopy(c) for c in _json(FROZEN)["scene_cameras"] if c.get("kind") == "interior"
             and c["room_id"] in ("r_L1_banyo", "r_L0_banyo")]
    lines = BD.check_agent_interior_plans(plans, b)
    cam = next(p for p in plans if p["name"] == "cam_r_L1_banyo_1")
    assert cam["policy"] == "search" and cam["agent_refused"]["position"] == ARGUS_POSE["position"]
    assert cam["position"] != ARGUS_POSE["position"] and CSR.pose_problems(b, cam) == []
    assert cam["anchors_in_frame"] and "refused by the camera search's rules" in cam["placement"]
    assert any(line.startswith("cam_r_L1_banyo_1:") for line in lines)
    # the agent's bathroom view that framed none of the fixtures moves too; a searched plan is never touched
    other = next(p for p in plans if p["name"] == "cam_r_L0_banyo_2")
    assert other["policy"] == "search" and other["anchors_in_frame"]
    kept = next(p for p in plans if p["name"] == "cam_r_L0_banyo_1")
    assert "agent_refused" not in kept


def test_the_agent_tool_falls_back_to_the_nearest_searched_pose(tmp_path):
    from test_argus_calls_20261027 import _ctx
    from wenart.agent import tools as TL

    ctx = _ctx(tmp_path, validators=EC)
    res = TL.build_registry().call(ctx, "set_camera", {
        "view_id": "cam_r1_1", "kind": "interior", "room_id": "r1", "position": [3.0, 1.0, 2.3],
        "target": [1.0, 3.0, 2.3], "reason": "a high view of the bed"})
    assert res["accepted"], res
    fb = res["fallback"]
    assert any("eye height 2.30 m" in f for f in fb["refused"]) and fb["to"]["position"][2] == pytest.approx(1.25)
    assert "the nearest searched pose of r1 is used instead" in res["message"]
    stored = ctx.overrides.agent_overrides()["cameras"][-1]
    assert stored["position"] == fb["to"]["position"] and "nearest searched pose" in stored["reason"]
    entry = {k: v for k, v in stored.items() if k != "seq"}                        # the override as the tool sent it
    assert EC.validate_camera_override(ctx.building, entry)["ok"]


# ------------------------------------------------------------------------------------- 2. see-through wardrobes

def _robe(width=3.1, palette=None):
    st = {"kind": "slats"}
    if palette:
        st["palette"] = palette
    return {"id": "f_robe", "type": "wardrobe", "height": 2.3, "room_id": "r_bed", "see_through": st,
            "footprint": {"center": [0, 0], "size": [width, 0.6], "rotation_deg": 0.0}}


def test_the_garments_have_shoulders_sleeves_collars_hangers_and_their_fabrics():
    from wenart.style import colours as C

    palette = WF.garment_palette({"family": "modern"}, {"wall_colour": "dark sage"})
    assert "sage" in palette and all(c in C.COLOURS for c in palette)
    plan = MOD.module_plan(_robe(palette=palette))
    assert plan["see_through"]["palette"] == palette
    parts = MOD.module_parts(plan)
    roles = {p["role"] for p in parts}
    assert {"garment", "sleeve", "collar", "hanger", "rail", "folded", "led", "shelf", "slat"} <= roles
    kinds = {p.get("garment") for p in parts if p["role"] == "garment"}
    assert len(kinds) >= 4, kinds                                                   # shirts, jackets, knits ...
    cloth = {p["key"] for p in parts if p["key"].startswith(WC.CLOTH_PREFIX)}
    looks_used = {WC.parse_cloth_key(k)[0] for k in cloth}
    assert looks_used <= set(WC.LOOKS) and len(looks_used) >= 3
    assert {WC.parse_cloth_key(k)[1] for k in cloth} <= set(palette) | set(WC.SHOE_COLOURS) | set(WC.BOX_COLOURS)
    # deterministic, cheap: one mesh with the run, each bay's contents a few thousand faces
    assert MOD.module_parts(MOD.module_plan(_robe(palette=palette))) == parts
    per_bay = WC.faces_per_bay(parts)
    assert len(per_bay) == len([m for m in plan["modules"] if m["kind"] == "frame"])
    assert all(800 <= n <= 4000 for n in per_bay.values()), per_bay
    # the garments vary: lengths by kind, small turns (no two garments with the same hem)
    hems = [round(min(v[2] for v in p["verts"]), 3) for p in parts if p["role"] == "garment"]
    assert len(set(hems)) > len(hems) * 0.6


def test_every_bay_has_its_light_bright_enough_to_read_through_the_slats():
    plan = MOD.module_plan(_robe())
    lights = MOD.bay_lights(plan)
    frames = [m for m in plan["modules"] if m["kind"] == "frame"]
    boards = MOD.bay_boards(plan)
    assert len(lights) == sum(len(b) for b in boards) and {li["bay"] for li in lights} == set(range(len(frames)))
    for light in lights:
        m = frames[light["bay"]]
        lm = WC.SHELF_LM_PER_M if light["board"] == "shelf" else WC.LED_LM_PER_M
        assert light["lumens"] == pytest.approx(lm * light["size_m"][0])
        assert light["energy_w"] > 2.0 and light["temperature_k"] == WC.LED_K and light["direction"] == [0, 0, -1]
        assert abs(light["center"][0] - m["pos_m"][0]) < 1e-6 and light["center"][1] < -0.1          # the front
        z = next(bz for bz, where in boards[light["bay"]] if where == light["board"])
        assert light["center"][2] == pytest.approx(z - 0.02)                                         # under its board
    # every bay its top strip; a hanging bay's garments their own strip under the hat shelf (it shades them)
    assert {li["bay"] for li in lights if li["board"] == "top"} == set(range(len(frames)))
    assert any(li["board"] == "hat_shelf" for li in lights)
    narrow = MOD.module_plan(_robe(width=1.2))                                       # a shelf bay: a strip per shelf
    assert any(li["board"] == "shelf" for li in MOD.bay_lights(narrow)) or \
        all(float(m["size_m"][0]) >= MOD.SEE_THROUGH["hanging_min_m"] for m in narrow["modules"] if m["kind"] == "frame")
    # the strip glows as an LED (not a lamp shade's bedding glow)
    assert any(p["key"] == "led" and p["role"] == "led" for p in MOD.module_parts(plan))
    assert MOD.bay_lights(dict(plan, see_through=None)) == []
    # the light's place in the world follows the run's footprint (the module mesh's own transform)
    from wenart.blender import furniture as F
    w = F.bay_light_world({"center": [1.0, -0.2, 2.0]}, {"center": [5.0, 3.0], "rotation_deg": 90.0}, 3.15)
    assert w == pytest.approx([5.2, 4.0, 5.15])


def test_a_cloth_key_takes_its_woven_fabric():
    from wenart.blender import furniture as F

    keys = {"fabric": 1, "textile_cotton": 1, "textile_wool": 1, "textile_knit": 1, "textile_linen": 1}
    assert F.cloth_material_key("cloth:wool:navy", keys) == "textile_wool"
    assert F.cloth_colour("cloth:wool:navy") == "navy"
    assert F.cloth_material_key("cloth:navy", keys) == "fabric" and F.cloth_colour("cloth:light grey") == "light grey"
    assert F.cloth_material_key("cloth:denim:navy", keys) == "fabric"                # an unknown look: the fabric


# ------------------------------------------------------------------------------ 3. white balance and the orange check

def _exposure(render_manifest: dict, cam: str) -> dict:
    return next(r["exposure"] for r in render_manifest["renders"] if r["camera"] == cam)


def test_the_rig_light_on_the_walls_takes_the_corridors_cast_out():
    rm = _json(FROZEN)["render_manifest"]

    def rb(v):
        return float(v[0]) / float(v[2])
    casts = {}
    for cam, before in (("cam_r_L1_koridor_1", 1.683), ("cam_r_L-1_koridor_2_1", 1.477)):
        e = _exposure(rm, cam)
        light = e["wb_walls"]["light_rgb"]
        assert rb(light) / rb(e["whitepoint"]) == pytest.approx(before, abs=0.002)        # the run's cast (lamp mix)
        rgb, share, source = R.wall_rig_mix(e["wb_walls"], e["wb_rig_whitepoint"], e["wb_rig_share"])
        assert source == "walls" and share == pytest.approx(e["wb_walls"]["rig_share"])
        wp = R.mixed_whitepoint(e["wb_project_whitepoint"], rgb, share, 0.35, R.WB_RIG_RESIDUAL)
        casts[cam] = rb(light) / rb(wp)
        assert casts[cam] < before - 0.15, (cam, casts[cam])
    # the corridors' walls keep no more cast than the project's daylight bedrooms keep on theirs (1.30-1.61)
    days = [rb(_exposure(rm, c)["wb_walls"]["light_rgb"]) / rb(_exposure(rm, c)["whitepoint"])
            for c in ("cam_r_L0_yatak_odasi_1", "cam_r_L0_yatak_odasi_2", "cam_r_L0_yatak_odasi_3",
                      "cam_r_L0_e_yatak_odasi_1", "cam_r_L0_e_yatak_odasi_2")]
    assert max(casts.values()) <= max(days) + 1e-6, (casts, days)
    # no wall metering, or walls under the share: the lamp's colour by the frame's share, as before
    lamp = [1.4, 0.92, 0.53]
    assert R.wall_rig_mix(None, lamp, 0.5) == (lamp, 0.5, "lamp")
    assert R.wall_rig_mix({"rig_rgb": [1.5, 0.9, 0.4], "rig_share": 0.5, "share": 0.02}, lamp, 0.5)[2] == "lamp"


def _gpu_render():
    spec = importlib.util.spec_from_file_location("gpu_render_30", ROOT / "tests" / "gpu" / "test_render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_orange_check_compares_views_of_one_paint():
    gpu = _gpu_render()
    style = _json(FROZEN)["style_profile"]         # 30 Oct 2026: run 201533's, frozen (run 112241 clad its walls in slats)
    rooms = {r["id"]: r for r in _json(FROZEN)["rooms"]}
    kind = {c: gpu._paint_kind({"room_id": rid, "room_type": rooms[rid]["room_type"]}, {}, style, rooms)
            for c, rid in (("hall", "r_L1_koridor"), ("bed", "r_L0_yatak_odasi_3"), ("deep", "r_L0_e_yatak_odasi"),
                           ("lime", "r_L0_yatak_odasi"), ("bath", "r_L1_banyo"))}
    assert kind == {"hall": "painted", "bed": "painted+accent:pale dusty blue", "deep": "paint:dark sage",
                    "lime": "lime_plaster:warm greige", "bath": "tiled"}
    assert all(gpu._judged_kind(k) for k in kind.values()) and not gpu._judged_kind("wood")
    # no daylight view of the halls' paint in real04: the fixed bound, not the blue-walled bedrooms' median
    assert gpu._orange_bound(0.53, None, None, 4000.0) == (gpu.RIG_ROOM_MAX_RB, "fixed")
    assert looks.wall_paint_key(None, style) == "painted"


# ------------------------------------------------------------------------------- 4. the design details GPU test

def test_the_design_details_test_reads_the_feature_walls_from_the_records(scene04):
    os.environ.setdefault("RENDER_TEST_PROJECTS", "real04")
    spec = importlib.util.spec_from_file_location("gpu_look_30", ROOT / "tests" / "gpu" / "test_look_m6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rooms = {r["id"]: r for r in _json(FIXTURE)["room_records"]}
    details = [o for o in scene04["objects"] if o["kind"] == "wall" and o.get("parent")]
    skirting = sorted(o["parent"] for o in details if mod._detail(o) == "skirting")
    assert skirting == sorted(a["parent"] for a in mod._assumed(scene04, "skirting")) and len(skirting) == 20
    built, expected, unrecorded = mod._feature_walls(scene04, details, rooms)
    assert built == expected == ["r_L0_yatak_odasi", "r_L0_yatak_odasi_2"] and unrecorded == []
    assert sorted(a["parent"] for a in mod._assumed(scene04, "feature_wall")) == built
    # the old expectation ("every wall detail is a skirting run") is what failed on the pod
    assert sorted(o["parent"] for o in details) != skirting


# --------------------------------------------------------------------------------------------- 5. wall items

@pytest.fixture()
def items04():
    return _json(FIXTURE)


def test_the_real04_wall_items_over_the_window_and_behind_the_tv_are_found(items04):
    got = {(c["target"], c["kind"], c["other"]): c for c in WI.clashes(items04)}
    assert ("dec_L0_093", "opening", "win_arch_r_L0_yatak_odasi_3_1") in got         # the desk's wall unit
    assert ("dec_L0_030", "opening", "win_arch_r_L0_yatak_odasi_3_1") in got         # the picture over the bed
    assert ("dec_L-1_007", "covered", "dec_L-1_010") in got                          # the TV hides the picture
    c = got[("dec_L-1_007", "covered", "dec_L-1_010")]
    assert c["severity"] == "major" and c["lesson"] == "UL139" and "covered by the tv_unit f_L-1_101" in c["message"]
    assert got[("dec_L0_093", "opening", "win_arch_r_L0_yatak_odasi_3_1")]["lesson"] == "UL134"
    # the model review's M32 and Argus' U35 read the same rule
    findings, n = WI.review(items04, check="M32")
    assert n >= 5 and {f["check"] for f in findings} == {"M32"} and len(findings) == len(got)
    from wenart.audit import kinds as K
    from wenart.audit import lessons as L
    u35 = L.wall_items_clear(items04)
    assert {f["check"] for f in u35} == {"U35"} and len(u35) == len(got)
    assert K.kind_of(u35[0]) == "no_sense" and L.CHECK_LESSONS["U35"] == ("UL134", "UL139")


def test_the_wall_items_are_raised_moved_or_left_out(items04):
    b = copy.deepcopy(items04)
    res = WI.resolve(b, stage="build")
    by = {d["id"]: d for d in b["decor"]}
    # 1. the picture over the TV unit: raised 0.15-0.25 m over the TV's top, at most eye height
    raised = {r["id"]: r for r in res["raised"]}
    tv_top = next(s["top"] for s in WI.stacks(b, next(r for r in b["rooms"] if r["id"] == "r_L-1_salon"),
                                              WI.room_lines(b, next(r for r in b["rooms"]
                                                                     if r["id"] == "r_L-1_salon")))
                  if s["by"] == "dec_L-1_010")
    art = by["dec_L-1_007"]
    assert "dec_L-1_007" in raised and 0.15 <= art["min_bottom_m"] - tv_top <= 0.25
    assert art["wall_clear"]["how"] == "raised"
    # 2. the picture in front of the architect's window: on another free wall of the room
    moved = {r["id"]: r for r in res["moved"]}
    assert moved["dec_L0_030"]["to"] == "another wall" and "anchor_ids" not in by["dec_L0_030"]
    # the intercom 3 cm too close to the resized entrance door's architrave: slid along its wall
    assert moved["dec_L0_099"]["to"] == "along its wall" and moved["dec_L0_099"]["moved_m"] < 0.05
    # 3. the desk's wall unit: no stretch of the desk's span is free of the window: left out with the reason
    dropped = {r["id"]: r for r in res["dropped"]}
    assert "dec_L0_093" in dropped and "dec_L0_093" not in by
    assert "win_arch_r_L0_yatak_odasi_3_1" in dropped["dec_L0_093"]["reason"]
    assert any(d["id"] == "dec_L0_093" for d in b["decor_dropped"])
    assert WI.clashes(b) == []                                                       # nothing left
    # deterministic and idempotent
    again = copy.deepcopy(b)
    assert WI.resolve(again, stage="build") == {"raised": [], "moved": [], "dropped": [], "furniture": []}


def test_the_build_records_every_change():
    b = _json(FIXTURE)
    assumed, warnings = [], []
    info = BD.clear_wall_items(b, assumed, warnings)
    assert {a["kind"] for a in assumed} == {"wall_item_clear"} and all(a["parent"] == a["object"] for a in assumed)
    assert {a["value"] for a in assumed} == {"raised", "moved"} and len(info["dropped"]) == 1
    assert any("dec_L0_093" in w and "left out" in w for w in warnings)


def _wall_room():
    """A 6 x 4 m room with a 1.2 m window in the middle of its north wall and a picture planned over it."""
    def wall(wid, a, b):
        return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": 0.2, "height": 2.7}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "rooms": [{"id": "r", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]]}],
            "walls": [wall("s", (-0.1, -0.1), (6.1, -0.1)), wall("e", (6.1, -0.1), (6.1, 4.1)),   # the room on
                      wall("n", (6.1, 4.1), (-0.1, 4.1)), wall("w", (-0.1, 4.1), (-0.1, -0.1))],     # their faces
            "openings": [{"id": "win", "type": "window", "level_id": "L0", "wall_id": "n", "center": [3.0, 4.1],
                          "width": 1.2, "height": 1.4, "sill_height": 0.9}],
            "furniture": [],
            "decor": [{"id": "art", "kind": "decor", "type": "wall_art", "room_id": "r", "level_id": "L0",
                       "center": [3.2, 3.98], "wall_point": [3.2, 4.0], "size": [0.8, 0.04], "bottom_m": 1.2,
                       "rotation_deg": 0.0, "host_frame": {"support": "wall"}},
                      {"id": "cur", "kind": "decor", "type": "curtain", "room_id": "r", "level_id": "L0",
                       "center": [3.0, 3.9, 0.0], "wall_point": [3.0, 4.0], "size": [1.6, 0.1, 2.5]}]}


def test_a_picture_over_a_window_slides_to_the_nearest_free_stretch_and_a_curtain_stays():
    b = _wall_room()
    assert [(c["target"], c["kind"]) for c in WI.clashes(b)] == [("art", "opening")]   # the curtain is exempt
    res = WI.resolve(b)
    art = next(d for d in b["decor"] if d["id"] == "art")
    assert res["moved"][0]["to"] == "along its wall" and WI.clashes(b) == []
    # clear of the window's frame by the margin: 3.0 + 0.6 + 0.05 + 0.10 + 0.4 = 4.15 m along x at least
    assert art["wall_point"][1] == pytest.approx(4.0) and abs(art["wall_point"][0] - 3.0) >= 1.15 - 1e-6
    assert art["wall_clear"]["reason"].startswith("over the window win")
    # an item standing on a piece's top, or a curtain, is no wall item
    assert not WI.is_wall_item({"type": "vase", "host_id": "f1", "host_frame": {"support": "top"}})
    assert not WI.is_wall_item({"type": "curtain", "wall_point": [0, 0]})
    assert WI.is_wall_item({"type": "desk_wall_unit", "wall_point": [0, 0], "host_frame": {"support": "floor"}})


def test_a_facade_override_keeps_the_family_scheme():
    """30 Oct 2026 (real04 run 20261030-043021-full: Argus set the facade slot to stone_cladding for a flat base texture
    and every wall turned to rustic stone): the facade slot is the main walls; under the family scheme they stay
    rendered, unless the brief or the style names the facade."""
    from wenart.blender import exterior_checks as EC

    fallback = {"family": "modern", "exterior": {"facade": {"material": "render", "source": "fallback",
                                                            "assumed": True}}}
    refused = EC.validate_material_override(fallback, {"facade": "stone_cladding"})
    assert not refused["ok"] and "every wall" in refused["failed"][0]
    assert EC.validate_material_override(fallback, {"facade": "render"})["ok"]
    named = {"family": "modern", "exterior": {"facade": {"material": "stone_cladding", "source": "brief",
                                                         "assumed": False}}}
    assert EC.validate_material_override(named, {"facade": "stone_cladding"})["ok"]
