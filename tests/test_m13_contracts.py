"""Milestone 13 contracts (docs/milestone13.md §13.2, §13.3): the frozen interfaces of the eight tracks exist with
their signatures and constants, and the data fields between the tracks are in the schemas and the defaults. Owned by
the lead; a track that needs a change asks for it. Pure CPU: every module here imports without bpy.

Where the round-1 code differs from the §13.2 wording, the real signature is asserted and the difference is noted in
a comment (the lead's docs list them): ``fit_building`` keeps ``cap`` / ``style_family`` / ``style`` positional (the
M12 callers) before the keyword-only ``mode``; ``prepare_m13``, ``platforms``, ``hssd_candidates``, ``download``,
``drawn_demands``, ``tree_object``, ``hedge_object`` and ``grass_patch`` carry optional extras after the contract's
parameters; the per-view commercial-safe function is ``final.commercial_safe_of_view``; ``loop.accept_edit`` and
``loop.tools_for_finding`` are re-exports of ``wenart.agent.causes``; ``sheets.exterior.hedge_rows`` re-exports the
detector of ``wenart.blender.vegetation`` (Blender's Python has no shapely).
"""
from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "results" / "renders"
VIOLATION_KEYS = {"check", "severity", "target", "room_id", "message", "metrics"}   # §13.2: the one finding format


def params(fn):
    return list(inspect.signature(fn).parameters)


def default_of(fn, name):
    return inspect.signature(fn).parameters[name].default


def is_keyword_only(fn, name):
    return inspect.signature(fn).parameters[name].kind is inspect.Parameter.KEYWORD_ONLY


# --------------------------------------------------------------------------
# T1: fit and licence rules
# --------------------------------------------------------------------------

def test_catalog_licence_interfaces():
    from wenart.furniture import catalog as C

    assert C.LICENCE_MODES == ("commercial", "relaxed")
    assert C.LICENCE_FLAGS == ("none", "non_commercial", "share_alike", "no_derivatives", "research_only", "regional",
                               "tool_nc")
    assert params(C.licence_mode) == ["brief", "env"]
    assert params(C.licence_flag_of) == ["entry"]
    assert params(C.commercial_safe) == ["entry"]
    assert params(C.usable) == ["entry", "mode"] and default_of(C.usable, "mode") == "commercial"
    assert params(C.unusable_reason) == ["entry", "mode"]
    assert default_of(C.unusable_reason, "mode") == "commercial"
    # env WENART_LICENCE_MODE > brief library.licence_mode > relaxed (the user's decision of 24 Oct 2026)
    relaxed_brief = {"values": {"library": {"licence_mode": "relaxed"}}, "assumed": []}
    assert C.licence_mode(None, env={}) == "relaxed" == C.LICENCE_MODE_DEFAULT
    assert C.licence_mode({"library": {"licence_mode": "commercial"}}, env={}) == "commercial"
    assert C.licence_mode(relaxed_brief, env={}) == "relaxed"
    assert C.licence_mode(relaxed_brief, env={"WENART_LICENCE_MODE": "commercial"}) == "commercial"
    # the flag words of §13.3 from the licence text
    assert C.licence_flag_of({"licence": "CC0"}) == "none"
    assert C.licence_flag_of({"licence": "CC-BY-NC-4.0"}) == "non_commercial"
    assert C.licence_flag_of({"licence": "CC-BY-SA-4.0"}) == "share_alike"
    assert C.licence_flag_of({"licence": "CC-BY-ND-4.0"}) == "no_derivatives"
    assert C.commercial_safe({"licence": "CC0"}) and not C.commercial_safe({"licence": "CC-BY-NC-4.0"})
    # relaxed mode takes NC, never ND (CLAUDE.md library rules); commercial mode only commercial-safe entries
    assert C.usable({"licence": "CC-BY-NC-4.0"}, "relaxed") and not C.usable({"licence": "CC-BY-NC-4.0"}, "commercial")
    assert not C.usable({"licence": "CC-BY-ND-4.0"}, "relaxed")
    assert isinstance(C.unusable_reason({"licence": "CC-BY-NC-4.0"}, "commercial"), str)
    assert C.unusable_reason({"licence": "CC-BY-NC-4.0"}, "relaxed") is None


def test_sizes_snap_interface():
    from wenart.furniture import sizes

    assert params(sizes.snap_size) == ["ftype", "footprint", "height"] and default_of(sizes.snap_size, "height") is None
    out = sizes.snap_size("sofa", [2.21, 0.9], 0.85)
    assert set(out) == {"footprint", "height", "product", "changed", "reason"} and out["changed"] is False
    assert isinstance(sizes.PRODUCT_GRID, dict) and sizes.PRODUCT_GRID
    assert {"bed_double", "sofa", "sofa_corner", "table_dining", "wardrobe", "chair", "desk"} <= set(sizes.PRODUCT_GRID)
    for ftype, rows in sizes.PRODUCT_GRID.items():
        assert rows and all({"w", "d", "h", "label"} <= set(r) for r in rows), ftype


def test_fit_interfaces():
    from wenart.furniture import fit

    assert params(fit.fit_piece)[:3] == ["piece", "catalog", "cap"]
    assert default_of(fit.fit_piece, "cap") == fit.NON_UNIFORM_CAP
    assert is_keyword_only(fit.fit_piece, "mode") and default_of(fit.fit_piece, "mode") == "commercial"
    # §13.2 writes fit_building(building, catalog, *, mode=None, ...); the code keeps cap / style_family / style
    # positional for the M12 callers and adds brief / settings / snap after mode (all keyword-only).
    assert params(fit.fit_building)[:2] == ["building", "catalog"]
    assert is_keyword_only(fit.fit_building, "mode") and default_of(fit.fit_building, "mode") is None
    assert fit.METHODS == ("library", "module", "parametric", "none")
    assert fit.LADDER_STEPS == ("library", "module", "parametric")


# --------------------------------------------------------------------------
# T2: module builders and families v2
# --------------------------------------------------------------------------

def test_module_and_family_interfaces():
    from wenart.blender import modules as MD, parametric as P

    assert params(MD.module_plan) == ["piece", "style"] and default_of(MD.module_plan, "style") is None
    assert params(MD.build_module) == ["plan", "piece", "materials"]
    # the §13.1 builders: wardrobe run, long table, L-sofa, kitchen run, bath set
    assert MD.MODULE_BUILDERS == {"wardrobe": "wardrobe_run", "table_dining": "table_long", "sofa_corner": "sofa_l",
                                  "kitchen_counter": "kitchen_run", "kitchen_island": "kitchen_run",
                                  "washbasin": "bath_set", "shower": "bath_set",
                                  "wall_cabinet": "wall_run"}       # 28 Oct 2026: the wall run of real units
    # pure (no bpy): a plan for a type with a builder, None for one without
    piece = {"id": "f1", "type": "wardrobe", "room_id": "r", "height": 2.1,
             "footprint": {"center": [1.0, 1.0], "size": [2.57, 0.6], "rotation_deg": 0}}
    plan = MD.module_plan(piece)
    assert plan is not None and plan["builder"] == "wardrobe_run"
    assert {"builder", "modules", "footprint_m", "height_m", "products"} <= set(plan)
    assert plan["modules"]
    assert all({"kind", "size_m", "pos_m", "rot_deg", "material"} <= set(m) for m in plan["modules"])
    assert all(len(m["size_m"]) == 3 and len(m["pos_m"]) == 2 for m in plan["modules"])
    assert plan["products"] and all(isinstance(p, str) for p in plan["products"])
    assert MD.module_plan({"id": "f2", "type": "chair", "height": 0.9,
                           "footprint": {"center": [0, 0], "size": [0.5, 0.5], "rotation_deg": 0}}) is None
    # the v2 families of §13.1 (bed with headboard, sofa, armchair, table, nightstand, desk, shelving, TV unit)
    assert {"bed", "bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee", "desk",
            "nightstand", "bookshelf", "tv_unit"} <= set(P.FAMILY_TYPES)


# --------------------------------------------------------------------------
# T3: placement
# --------------------------------------------------------------------------

def test_placement_interfaces():
    from wenart.blender import scene_checks
    from wenart.furniture import edit_ops, groups, infer, solver

    assert params(infer.type_by_code) == ["building", "piece"]
    # 26 Oct 2026: same_block (one block drawn again elsewhere in the project gets one type) after the level rule
    assert infer.CODE_TYPE_METHODS == ("twin", "level", "same_block", "block", "name_text", "zone_label",
                                       "group_member")
    assert params(groups.drawn_groups) == ["building", "room_id"]
    assert groups.GROUP_MEMBER_MOVE_MAX_M == 0.5
    assert params(solver.solve_room) == ["building", "room_id", "program", "k", "fixed_ids", "drawn_group"]
    assert default_of(solver.solve_room, "k") == 3 and default_of(solver.solve_room, "drawn_group") is None
    assert is_keyword_only(solver.solve_room, "drawn_group")
    assert params(solver.apply_candidate) == ["building", "room_id", "candidate"]
    assert scene_checks.TOLERANCES["overlap_fixture"] == 0.03
    assert scene_checks.TOLERANCES["overlap_soft"] == 0.05
    assert scene_checks.TOLERANCES["overlap_m"] == 0.010            # the M12 tolerance stays for the other classes
    assert edit_ops.S2_SWAP_MIN_M == scene_checks.TOLERANCES["overlap_fixture"]


# --------------------------------------------------------------------------
# T4: agent loop
# --------------------------------------------------------------------------

def test_agent_interfaces():
    from wenart.agent import causes, loop
    from wenart.furniture import edit_ops

    assert params(edit_ops.apply_edit) == ["building", "edit", "catalog"]
    assert params(edit_ops.dry_run) == ["building", "edit", "catalog"]
    for fn in (edit_ops.apply_edit, edit_ops.dry_run):          # §13.2: dry_run(building, edit, *, catalog=None)
        assert is_keyword_only(fn, "catalog") and default_of(fn, "catalog") is None
    assert params(edit_ops.allowed_edits) == ["building", "piece_id"]
    assert params(loop.accept_edit) == ["before", "after", "edit"] and loop.accept_edit is causes.accept_edit
    assert loop.MAX_ROUNDS == 3
    assert params(loop.tools_for_finding) == ["finding"] and loop.tools_for_finding is causes.tools_for_finding
    # accept_edit is pure: accepted only when the targeted finding is gone and no new critical finding appears
    finding = {"check": "F8", "severity": "major", "target": "r_1", "room_id": "r_1", "message": "m", "metrics": {}}
    edit = {"op": "place_group", "target_finding": {"check": "F8", "target": "r_1"}}
    ok, reason = loop.accept_edit([finding], [], edit)
    assert ok is True and isinstance(reason, str)
    assert loop.accept_edit([finding], [dict(finding)], edit)[0] is False
    critical = dict(finding, check="S2", severity="critical", target="x")
    assert loop.accept_edit([finding], [critical], edit)[0] is False
    assert loop.accept_edit([finding], [], edit) == (ok, reason)
    tools = loop.tools_for_finding(dict(finding, cause="anchor_not_built"))
    assert isinstance(tools, list) and tools
    within = {"check": "S2", "severity": "major", "target": "x", "metrics": {"depth_m": 0.02}}
    assert loop.tools_for_finding(within) == []          # S2 under 3 cm: no tool (swap_model never for it)


# --------------------------------------------------------------------------
# T5: light, materials, render, camera replay
# --------------------------------------------------------------------------

def test_lighting_and_material_interfaces():
    from wenart.blender import lighting as L, materials as M

    # Round 3 (docs/milestone13.md §14.3): the manual's clear-sky value, decided on pod P1 (15 Oct 2026)
    assert isinstance(L.SUN_STRENGTH_WM2, float) and L.SUN_STRENGTH_WM2 == 1000.0
    assert L.LIGHT_VARIANT_ENV == "WENART_LIGHT_VARIANT"
    assert {"base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all"} <= set(L.LIGHT_VARIANTS)
    assert params(L.room_rig) == ["room_type"]
    assert L.room_rig(None) == [] and all({"kind", "source", "size_m"} <= set(f) for f in L.room_rig("bedroom"))
    assert params(L.build_lighting) == ["building", "levels", "style", "hdri_path", "collection", "manifest_objects",
                                        "assumed", "north_deg", "north_source", "ceiling_at", "exterior",
                                        "ceiling_voids"]    # fix round after P5: the slab openings above each level
    assert params(M.shell_material) == ["slot", "style", "assets"]
    assert set(M.SHELL_SLOTS) == {"ceiling", "worktop", "front", "ceramic", "metal", "tile", "plaster"}
    assert params(M.exterior_world_nodes)[:2] == ["scene", "lighting"]
    assert default_of(M.exterior_world_nodes, "sun_disc") is True
    assert {"sun_elevation_deg", "sun_azimuth_deg"} <= set(params(M.exterior_world_nodes))


def test_render_and_replay_interfaces():
    from wenart.blender import build as B, cameras as CAM, render as R
    from wenart.run import ab as AB

    assert R.EXPOSURE_LIMITS == (-2.0, 3.0) and R.EXPOSURE_LIMITS_M11 == (-2.0, 8.0)
    dark = R.lighting_dark_entry("cam_r_L0_a_1", "r_L0_a", 6.1, 3.0, R.EXPOSURE_LIMITS, 0.013)
    assert set(dark) == VIOLATION_KEYS and dark["check"] == "lighting_dark"
    assert dark["severity"] in ("major", "critical")
    assert R.lighting_dark_entry("c", "r", 2.9, 2.9, R.EXPOSURE_LIMITS) is None
    assert R.parse_white_balance("project") == ("project", None)
    # camera replay: cameras.replay_cameras gives plans with source "replayed"; build.py takes --cameras-from and
    # --cameras-extra (also from the environment) and writes cameras_from into the scene manifest
    assert params(CAM.replay_cameras) == ["manifest", "kinds", "level_id"]
    plans = CAM.replay_cameras({"cameras": [{"name": "cam_r_1", "position": [1, 1, 1.25], "target": [2, 1, 1.25],
                                             "lens_mm": 18, "room_id": "r", "level_id": "L0"}]})["plans"]
    assert len(plans) == 1 and plans[0]["source"] == "replayed"
    assert CAM.replayed_rooms(plans) == {"r"}
    assert B.CAMERAS_FROM_ENV == "WENART_CAMERAS_FROM" and B.CAMERAS_EXTRA_ENV == "WENART_CAMERAS_EXTRA"
    assert B.EXTRA_CAMERA_SUFFIX == "_s"
    ns = B.parse_args(["--building", "b", "--out", "o", "--cameras-from", "x.json", "--cameras-extra"])
    assert ns.cameras_from == "x.json" and ns.cameras_extra is True
    assert params(B.cameras_from_summary) == ["camera_file", "replay", "camera_plans", "extra"]
    # §13.2 prepare_m13(project, project_out, commit); the code adds repo_root and show (an injectable git show)
    assert params(AB.prepare_m13)[:3] == ["project", "project_out", "commit"]
    assert params(AB.cameras_check)[:2] == ["m5_scene", "ab_scene"]
    assert {"real02", "real03"} <= set(AB.M13_AB_VIEWS)
    assert all(len(v) == 8 for v in AB.M13_AB_VIEWS.values())


# --------------------------------------------------------------------------
# T6: outdoor and site
# --------------------------------------------------------------------------

def test_site_interfaces():
    from wenart.blender import copies as CP, exterior as X, site as S, vegetation as V
    from wenart.sheets import exterior as SX

    assert params(SX.hedge_rows) == ["circles"] and SX.hedge_rows is V.hedge_rows
    assert SX.hedge_rows([]) == []
    assert params(S.tree_height) == ["crown_radius_m"]
    # the crown classes of §13.2: shrub < 1.5 m crown; small 1.5-2.5 -> 4-6 m; medium 2.5-4 -> 6-10 m;
    # large > 4 -> 10-15 m
    assert S.tree_height(1.4)[1] == "shrub"
    classes = ((2.0, "small", 4.0, 6.0), (3.0, "medium", 6.0, 10.0), (5.0, "large", 10.0, 15.0))
    for radius, size_class, lo, hi in classes:
        height, cls = S.tree_height(radius)
        assert cls == size_class and lo <= height <= hi, (radius, height, cls)
    assert params(S.platforms)[0] == "site"              # + an optional terrain (the levels' terrain model)
    assert params(S.build_site) == ["plan", "collection", "looks", "make_material", "manifest_objects", "assumed",
                                     "glass"]
    assert params(V.tree_object)[:4] == ["species", "height_m", "seed", "near_camera"]
    assert params(V.hedge_object)[0] == "hedge"
    assert params(V.grass_patch)[:2] == ["polygon", "density"]
    assert isinstance(V.SPECIES, dict) and V.SPECIES
    for name, rec in V.SPECIES.items():
        assert set(rec["source"]) <= {"polyhaven", "sapling"} and rec["source"], name
    assert params(CP.site_view)[:3] == ["outline", "building", "z_range"]
    assert default_of(CP.pitch_for_horizon, "cap_deg") == 28.0 and 0 < CP.pitch_for_horizon() <= 28.0
    assert params(X.view_check) == ["model", "position", "target", "lens", "shift_y", "aim"]


# --------------------------------------------------------------------------
# T7: library growth and audit
# --------------------------------------------------------------------------

def test_library_growth_interfaces():
    from wenart.assets import hssd
    from wenart.assets.audit import demands

    # §13.2 hssd_candidates(demands, n_per_bin) and download(ids, dest, token_env="HF_TOKEN"); the code adds
    # optional rows / used_ids and the injectable download callables after them
    assert params(hssd.hssd_candidates)[:2] == ["demands", "n_per_bin"]
    assert params(hssd.download)[:3] == ["ids", "dest", "token_env"]
    assert default_of(hssd.download, "token_env") == "HF_TOKEN"
    assert hssd.entry_fields() == {"licence": "CC-BY-NC-4.0", "licence_flag": "non_commercial",
                                   "licence_declared_by": "publisher",
                                   "licence_url": "https://huggingface.co/datasets/hssd/hssd-models",
                                   "commercial_safe": False}
    assert hssd.DATASET["licence"] == "CC-BY-NC-4.0" and hssd.DATASET["licence_flag"] == "non_commercial"
    assert params(demands.drawn_demands)[0] == "building_paths"
    assert params(demands.size_grid) == ["demands"]
    assert params(demands.coverage) == ["catalog", "demands", "mode"]
    assert default_of(demands.coverage, "mode") == "commercial"


# --------------------------------------------------------------------------
# T8: licence plumbing, attribution, report, metrics
# --------------------------------------------------------------------------

def test_report_interfaces():
    from wenart.report import final as F, metrics13, sheets13
    from wenart.run import copy as RC

    assert params(RC.attribution_text) == ["title", "credits", "mode"]
    assert is_keyword_only(RC.attribution_text, "mode") and default_of(RC.attribution_text, "mode") == "commercial"
    assert params(RC.project_credits) == ["out_dir"]
    # the per-view commercial-safe check (§13.2: the scene manifest's objects x the catalogue flags x the view's
    # index values) is final.commercial_safe_of_view
    assert params(F.commercial_safe_of_view) == ["entry", "by_index", "catalog"]
    assert F.commercial_safe_of_view(None, {})["safe"] is True
    cs = F.FINAL_VIEW["properties"]["commercial_safe"]
    assert set(cs["required"]) == {"safe", "flagged"}
    assert {"licence", "below_library"} <= set(F.FINAL_MANIFEST["properties"])
    assert F.BELOW_LIBRARY_METHODS == ("module", "parametric")
    assert params(F.below_library) == ["building"]
    assert params(metrics13.metrics) == ["project_out", "baseline_out"]
    assert default_of(metrics13.metrics, "baseline_out") is None
    assert sorted(metrics13.METRICS) == list(range(1, 18))            # the 17 metrics of §7
    assert params(sheets13.sheets) == ["project_out", "baseline_out", "out_dir"]


# --------------------------------------------------------------------------
# §13.3: the data between the tracks (building schema, manifest schemas, defaults and briefs)
# --------------------------------------------------------------------------

def test_building_schema_has_the_m13_fields():
    from wenart.furniture import catalog as C, fit, infer

    s = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    d = s["$defs"]
    assert s["properties"]["project"]["properties"]["licence_mode"]["enum"] == list(C.LICENCE_MODES)
    f = d["furniture"]["properties"]
    asset = f["asset"]["properties"]
    assert {"method", "licence", "licence_flag", "commercial_safe", "ladder", "module_plan"} <= set(asset)
    assert asset["method"]["enum"] == list(fit.METHODS)
    assert set(C.LICENCE_FLAGS) <= set(asset["licence_flag"]["enum"])
    assert asset["ladder"]["items"]["properties"]["step"]["enum"] == list(fit.LADDER_STEPS)
    assert set(f["size_snap"]["properties"]) == {"drawn", "snapped", "product", "reason"}
    assert set(f["drawn_group"]["properties"]) == {"anchor_id", "members", "moved_m"}
    assert set(infer.CODE_TYPE_METHODS) <= set(f["type_method"]["enum"])
    site = s["properties"]["site"]["properties"]
    assert site["hedges"]["type"] == "array" and site["platforms"]["type"] == "array"
    # the agent's retype_piece record (T4) and the solver / code labels (T3) under adjusted_by_ai
    adj = f["adjusted_by_ai"]
    assert "retype" in adj["description"] and set(adj["properties"]) >= {"reason", "by", "retype"}
    assert set(adj["properties"]["retype"]["properties"]) == {"to", "built", "method", "asset_id", "licence_mode",
                                                              "ladder_step"}
    assert adj["properties"]["retype"]["properties"]["licence_mode"]["enum"] == list(C.LICENCE_MODES)


def test_manifest_schemas_take_the_m13_keys():
    """The scene and render manifest validators accept the committed M11 manifests and the keys the Milestone 13 build
    and render write (camera source, cameras_from, light_variant, lighting_dark, white_balance_project)."""
    import jsonschema

    from wenart.blender import build as B, cameras as CAM, render as R, schemas

    assert schemas.CAMERA_SOURCES == ("searched", "replayed")
    assert set(schemas.LIGHTING_DARK["required"]) == VIOLATION_KEYS
    scene_path = RENDERS / "real02" / "scene_manifest.json"
    render_path = RENDERS / "real02" / "render_manifest.json"
    if not (scene_path.is_file() and render_path.is_file()):
        pytest.skip("the committed real02 manifests are not here")
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    render = json.loads(render_path.read_text(encoding="utf-8"))
    schemas.validate_scene_manifest(scene)
    schemas.validate_render_manifest(render)
    # a build with --cameras-from: the replayed records plus a searched extra camera, the summary and the variant
    replay = CAM.replay_cameras(scene)
    record = B.camera_file_record(str(scene_path))
    built = copy.deepcopy(scene)
    built["cameras"] = replay["plans"] + [dict(scene["cameras"][0], name="cam_x_1_s", source="searched", extra=True)]
    built["cameras_from"] = B.cameras_from_summary(record, replay, built["cameras"], True)
    built["light_variant"] = "sun300"
    schemas.validate_scene_manifest(built)
    assert built["cameras_from"]["replayed"] == len(replay["plans"]) and built["cameras_from"]["extra"] is True
    bad = copy.deepcopy(built)
    bad["cameras"][0]["source"] = "typed"
    with pytest.raises(jsonschema.ValidationError):
        schemas.validate_scene_manifest(bad)
    # §13.2 build.py: a record is recreated from "target or rotation"; replay_cameras keeps a null target next to
    # the rotation, and the camera is valid with the rotation alone; a camera with neither is not
    turned = CAM.replay_cameras({"cameras": [dict(scene["cameras"][0], target=None,
                                                  rotation_euler_deg=[80.0, 0.0, 30.0])]})["plans"]
    assert len(turned) == 1 and turned[0]["target"] is None and turned[0]["rotation_euler_deg"] == [80.0, 0.0, 30.0]
    with_rotation = copy.deepcopy(built)
    with_rotation["cameras"] = turned + [{k: v for k, v in turned[0].items() if k != "target"}]
    with_rotation["cameras"][1]["name"] = "cam_rot_2"
    schemas.validate_scene_manifest(with_rotation)
    neither = copy.deepcopy(built)
    neither["cameras"][0].pop("target", None)
    neither["cameras"][0].pop("rotation_euler_deg", None)
    with pytest.raises(jsonschema.ValidationError):
        schemas.validate_scene_manifest(neither)
    # a render under the cap with a dark view, the project whitepoint and the variant
    dark = R.lighting_dark_entry("cam_r_L-1_salon_1", "r_L-1_salon", 6.1, 3.0, R.EXPOSURE_LIMITS, 0.013)
    rendered = copy.deepcopy(render)
    entry = rendered["renders"][0]
    entry["lighting_dark"] = entry["exposure"]["lighting_dark"] = dark
    entry["exposure"]["wb_source"] = "metered on cam_r_L-1_salon_1"
    entry["sun_hidden"] = False
    entry["vram_mib"] = 4100
    rendered["lighting_dark"] = [dark]
    rendered["white_balance_project"] = {"whitepoint": [1.05, 1.0, 0.92], "from_camera": "cam_r_L-1_salon_1",
                                         "source": "metered on cam_r_L-1_salon_1", "residual": 0.1}
    rendered["light_variant"] = {"render": None, "build": "sun300"}
    rendered["exposure_limits"] = list(R.EXPOSURE_LIMITS)
    schemas.validate_render_manifest(rendered)
    rendered["white_balance_project"] = {"whitepoint": None, "from_camera": None, "source": "kelvin:5600",
                                         "residual": None, "kelvin": 5600.0}
    schemas.validate_render_manifest(rendered)
    # the per-view record of the Milestone 13 white balance (every pod job renders --white-balance project, a brief
    # with render.white_balance_k renders kelvin:K): wb_mode is one of render.WB_MODES, also from (--look-from)
    assert {"project", "kelvin"} <= set(R.WB_MODES)
    for wb_mode in list(R.WB_MODES) + ["from"]:
        entry["exposure"]["wb_mode"] = wb_mode
        schemas.validate_render_manifest(rendered)
    entry["exposure"]["wb_mode"] = "typed"
    with pytest.raises(jsonschema.ValidationError):
        schemas.validate_render_manifest(rendered)
    entry["exposure"]["wb_mode"] = "project"
    # render.py fills exposure.limits in mode auto only; a --look-from or --exposure fixed record keeps it null
    for mode, limits in (("from", None), ("fixed", None), ("off", None), ("auto", list(R.EXPOSURE_LIMITS))):
        entry["exposure"].update(mode=mode, limits=limits)
        schemas.validate_render_manifest(rendered)
    entry["exposure"]["limits"] = [-2.0]
    with pytest.raises(jsonschema.ValidationError):
        schemas.validate_render_manifest(rendered)
    entry["exposure"]["limits"] = list(R.EXPOSURE_LIMITS)
    rendered["lighting_dark"] = [{"check": "lighting_dark"}]
    with pytest.raises(jsonschema.ValidationError):
        schemas.validate_render_manifest(rendered)


def test_defaults_and_briefs_carry_the_m13_settings():
    from wenart import brief as BR

    block = yaml.safe_load((ROOT / "wenart" / "defaults.yaml").read_text(encoding="utf-8"))["brief"]
    assert block["library"]["licence_mode"] == "relaxed"                 # every library model (user, 24 Oct 2026)
    assert block["render"]["white_balance_k"] is None                    # K5: the project whitepoint, metered once
    assert {"library.licence_mode", "render.white_balance_k"} <= set(BR.VALUE_RULES)
    assert BR.white_balance_arg(None) == "project"
    for project in ("real02", "real03", "real04"):                       # D1: the PoC projects use relaxed mode
        path = ROOT / "projects" / project / "brief.yaml"
        if not path.is_file():
            pytest.skip(f"{path} is not here")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        assert raw.get("library", {}).get("licence_mode") == "relaxed", project
        assert BR.load_brief(path.parent)["values"]["library"]["licence_mode"] == "relaxed"


# --------------------------------------------------------------------------
# Round 2 (the wiring agents' new interfaces: HSSD as a library source, the attribution helpers, the module split
# label and the uniform-scale placement of wall-backed pieces)
# --------------------------------------------------------------------------

def test_round2_hssd_source_and_licence_constants():
    from wenart.assets import models
    from wenart.blender import furniture
    from wenart.furniture import catalog as C, fit as F
    from wenart.run import copy as CP

    assert "hssd" in C.SOURCES and "hssd" in C.LIBRARY_SOURCES
    assert C.SOURCE_LICENCES["hssd"] == ("CC-BY-NC-4.0",)
    assert C.LICENCE_DECLARED_BY["hssd"] == "publisher"
    assert F.SOURCE_ORDER == ("abo", "polyhaven", "hssd", "gso", "3dwh", "objaverse", "generated")
    assert models.LIBRARY_SOURCES == CP.LIBRARY_SOURCES == C.LIBRARY_SOURCES
    assert furniture.MODEL_LICENCES["hssd"] == ("CC-BY-NC-4.0",)
    assert furniture.SOURCE_FLAGS["hssd"] == "non_commercial"
    # an HSSD entry is relaxed-mode only (CC BY-NC 4.0): never usable in commercial mode
    entry = {"source": "hssd", "licence": "CC-BY-NC-4.0", "licence_flag": "non_commercial", "commercial_safe": False,
             "audit": {"decision": "keep"}}
    assert C.licence_flag_of(entry) == "non_commercial" and not C.commercial_safe(entry)
    assert not C.usable(entry, "commercial")


def test_round2_attribution_helpers():
    from wenart.run import copy as CP

    notice = CP.hssd_notice()
    assert isinstance(notice, str) and "HSSD" in notice and "hssd/hssd-models" in notice
    assert params(CP.vegetation_credits) == ["out_dir"]
    assert CP.vegetation_credits(Path("/nonexistent/wenart_round2")) == []


def test_round2_split_label_and_uniform_scale_placement():
    from wenart.blender import furniture
    from wenart.furniture import fit as F

    assert params(F.split_label) == ["piece", "plan"]
    assert params(F.apply_split_label) == ["piece", "asset"] and default_of(F.apply_split_label, "asset") is None
    assert F.split_label({"footprint": {"size": [2.0, 1.0]}}, {"builder": "table_long"}) is None   # no split
    piece = {"id": "f1", "footprint": {"size": [2.4, 1.8]}, "asset": {"adjusted_by_ai": None}}
    assert F.apply_split_label(piece) is False and "adjusted_by_ai" not in piece
    assert params(furniture.fit_vertices) == ["verts", "asset", "footprint", "floor_z", "target_size", "align"]
    assert default_of(furniture.fit_vertices, "align") == "centre"
    assert params(furniture.depth_alignment) == ["piece", "asset"]
    assert params(furniture.fit_mismatch_warnings) == ["piece_id", "asset", "footprint_size", "bbox_m"]
