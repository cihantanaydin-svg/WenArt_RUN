"""Integration of the fix round after P3 (16-17 Oct 2026): the cross-track asks the lead applied.

What: CPU tests of the small changes made for the tracks' asks: wall decor under the sloped roof (decor stage), the
render manifest schema of the deeper window pull and the sky pull, the build's camera room types and built-in list,
the scheduler's measured/predicted note, the agent report's 'reported to other stages' and context-budget lines.
Why: every behaviour change of the integration step gets a test that fails on the code of the P3 results commit.
How: committed data (results/furniture/real04) and small hand-made inputs; no Blender, no model server.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.blender import schemas
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import placer

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_furnished.json"

# P3's f_L1_049 (runs/20261016-172855-full, building_decor.json): the console the mirror dec_L1_009 hung above.
P3_CONSOLE = {"id": "f_L1_049", "level_id": "L1", "room_id": "r_L1_koridor", "type": "console_table",
              "footprint": {"center": [4.7895, 11.6291], "size": [0.9, 0.3], "rotation_deg": 0.0},
              "front_deg": 270.0, "height": 0.8, "asset": None, "status": "verified", "source": "added_by_ai"}


def _real04_with_console():
    building = json.loads(REAL04.read_text(encoding="utf-8"))
    building["furniture"] = [p for p in building["furniture"] if p.get("room_id") != "r_L1_koridor"]
    building["furniture"].append(copy.deepcopy(P3_CONSOLE))
    room = next(r for r in building["rooms"] if r["id"] == "r_L1_koridor")
    level = next(lv for lv in building["levels"] if lv["id"] == "L1")
    return building, room, level


def test_p3_the_mirror_over_the_console_under_the_l1_roof_is_left_out():
    # P3: dec_L1_009 had bottom 1.05 m and max_height_m 1.301 (the flat 2.451 m ceiling), but the slope over its wall
    # is 0.80 m high: the mirror poked through the roof in every agent round
    building, room, level = _real04_with_console()
    planes = D.ceiling_planes(building, "L1")
    assert planes, "real04's L1 lies under the roof"
    ctx = placer.room_context(building, room)
    host = building["furniture"][-1]
    item, why = DA._wall_item(host, ctx, building, level, "mirror")
    assert item is None and "sloped ceiling" in why
    for dtype in ("wall_art", "clock"):                            # the same geometry hangs the picture and the clock
        assert DA._wall_item(host, ctx, building, level, dtype)[0] is None


def test_wall_decor_is_kept_under_a_slope_that_leaves_room_and_flat_ceilings_keep_the_old_rule(monkeypatch):
    building, room, level = _real04_with_console()
    ctx = placer.room_context(building, room)
    host = building["furniture"][-1]
    floor = float(level["elevation"])
    # a slope 2.0 m above the floor over the whole room: the mirror is kept, lower than under the flat ceiling
    monkeypatch.setattr(D, "ceiling_planes", lambda b, level_id: [[0.0, 0.0, floor + 2.0]])
    item, why = DA._wall_item(host, ctx, building, level, "mirror")
    assert item is not None, why
    assert item["max_height_m"] == pytest.approx(2.0 - D.WALL_ART_CEILING_M - item["bottom_m"], abs=1e-3)
    assert "kept under the sloped ceiling" in item["reason"]
    # no roof over the level: the flat ceiling height as before (P3's 1.301 m)
    monkeypatch.setattr(D, "ceiling_planes", lambda b, level_id: [])
    flat, _why = DA._wall_item(host, ctx, building, level, "mirror")
    assert flat["max_height_m"] == pytest.approx(float(level["ceiling_height"]) - D.WALL_ART_CEILING_M
                                                 - flat["bottom_m"], abs=1e-3)
    assert flat["max_height_m"] > item["max_height_m"] and "sloped" not in flat["reason"]


def _render_manifest(**entry_extra):
    exposure = {"mode": "auto", "ev": 3.5, "ev_raw": 3.52, "at_limit": False, "target": 0.9, "incident_p50": 0.08,
                "whitepoint": [1.05, 0.99, 0.95], "wb_temperature": 5600.0, "wb_tint": 10.0, "residual": 0.35,
                "window_clip_frac": 0.4, "meter_seconds": 0.9, "source": None}
    entry = {"camera": "cam", "png": "cam.png", "exr": "cam_passes.exr", "preview": "cam_preview.jpg",
             "seconds": 1.0, "samples": 16, "resolution": [320, 180], "depth": {"min": 1.0, "max": 5.0, "mean": 2.0},
             "index_values": [1], "index_stats": {"1": {"pixels": 10, "box": [0, 0, 5, 2]}},
             "files": {"index": "cam_index.png", "depth_mm": "cam_depth_mm.png", "normal": "cam_normal.png"},
             "render_key": "0123456789abcdef", "exposure": exposure, "hidden": [], "plugged": []}
    entry.update(entry_extra)
    return {"schema_version": "0.1", "scene": "../scene/scene.blend", "device": "CPU", "device_requested": "auto",
            "blender_version": "5.2.2", "samples": 16, "resolution": [320, 180], "denoiser": "OPENIMAGEDENOISE",
            "pass_index": {"proxy_f": 1}, "renders": [entry]}


def test_the_render_schema_takes_a_window_pull_of_up_to_ten_stops_and_the_sky_pull():
    from wenart.blender import render as R

    pull = {"ev": -7.0, "k": 7, "pane_ev": -3.5, "clip_before": 0.3, "clip_after": 0.0, "pane_px": 1200,
            "pane_median": 0.93, "pane_p90": 0.99, "pane_p90_after": 0.81, "wall_median": 0.4, "rule": "r",
            "targets": {"p90_max": R.PULL_P90_MAX}}
    assert max(R.PULL_STEPS) == 10
    schemas.validate_render_manifest(_render_manifest(window_pull=pull))          # k 7 was refused (enum 0..4)
    with pytest.raises(Exception):
        schemas.validate_render_manifest(_render_manifest(window_pull=dict(pull, k=11)))
    sky = {"ev": -2.0, "k": 2, "sky_ev": 1.5, "sky_px": 4000, "sky_share": 0.3, "median_before": 0.95,
           "median_after": 0.7, "saturation_before": 0.05, "saturation_after": 0.15, "rule": "r",
           "targets": {}, "tried": []}
    schemas.validate_render_manifest(_render_manifest(sky_pull=sky, room_type="balcony", open_air=True))
    schemas.validate_render_manifest(_render_manifest(sky_pull=None, room_type=None, open_air=False))
    with pytest.raises(Exception):
        schemas.validate_render_manifest(_render_manifest(sky_pull=dict(sky, k=max(R.SKY_PULL_STEPS) + 1)))
    with pytest.raises(Exception):
        schemas.validate_render_manifest(_render_manifest(open_air="yes"))
    wb = dict(_render_manifest()["renders"][0]["exposure"], wb_project_whitepoint=[1.1, 1.0, 0.9],
              wb_rig_share=0.83, wb_rig_kelvin=2700.0, wb_rig_whitepoint=[2.41, 1.0, 0.24],
              wb_view_rule="mixed", wb_view_shift_mired=80.5, wb_day_incident_p50=0.01)
    schemas.validate_render_manifest(_render_manifest(exposure=wb))
    with pytest.raises(Exception):
        schemas.validate_render_manifest(_render_manifest(exposure=dict(wb, wb_rig_share=1.5)))


def test_the_build_passes_the_room_types_to_the_cameras_and_keeps_the_built_in_list():
    # build.py needs Blender; the two lines the tracks asked for are checked in its source (the Blender test of the
    # whole build runs on the pod)
    src = (ROOT / "wenart" / "blender" / "build.py").read_text(encoding="utf-8")
    assert 'room_types={r["id"]: r.get("room_type") for r in building["rooms"]}' in src
    assert '("decor_not_rested", "dressed_beds", "built_in")' in src


def _real04_kitchen():
    building = json.loads((ROOT / "results" / "furniture" / "real04" / "building.json").read_text(encoding="utf-8"))
    return dict(building, furniture=[p for p in building["furniture"] if p.get("room_id") == "r_L-1_mutfak"],
                decor=[])


def test_an_agent_refit_of_a_kitchen_run_keeps_its_drawn_sink_and_stove_gap():
    # G_geometry's ask: an agent refit (edit_ops._build_retyped, the only fit_piece call of the agent edits) passes
    # the run's hints as fit_building does; before, the refit dropped the sink unit and the stove gap
    from wenart.furniture import catalog as C
    from wenart.furniture import edit_ops as EO
    from wenart.furniture import fit as F

    catalog = C.load()
    b = F.fit_building(_real04_kitchen(), catalog, style_family="modern", mode="relaxed")
    by_id = {p["id"]: p for p in b["furniture"]}
    for pid in ("f_L-1_003", "f_L-1_002"):
        by_id[pid].pop("asset", None)                              # as after a retype: no asset yet
    run = EO._build_retyped(b, by_id["f_L-1_003"], {"type": "kitchen_counter"}, catalog)
    assert run["method"] == "module" and run["module_hints"]["sink_piece"] == "f_L-1_067"
    assert [x["id"] for x in run["module_plan"]["built_ins"]] == ["f_L-1_067"]
    stove_run = EO._build_retyped(b, by_id["f_L-1_002"], {"type": "kitchen_counter"}, catalog)
    # 28 Oct 2026 (kitchen design): the drawn stove is the run's hob (built in at its drawn span), no gap any more
    assert "gaps" not in stove_run["module_plan"]
    assert [x["id"] for x in stove_run["module_plan"]["built_ins"]] == ["f_L-1_008"]
    assert not [p for p in b["furniture"] if "module_hints" in p]           # never on the building piece
    # the sink its run's plan holds is refitted as the built-in, not as a free-standing sink model
    sink = EO._build_retyped(b, by_id["f_L-1_067"], {"type": "sink_kitchen"}, catalog)
    assert (sink["method"], sink["built_in"]) == ("module", "f_L-1_003")


def test_the_agent_report_lists_findings_sent_to_other_stages_the_context_budget_and_measured_removals(tmp_path):
    from wenart.agent import log as LG
    from wenart.report import agent as AG

    out = tmp_path / "toy"
    log = LG.AgentLog(out, "toy", "Qwen/Qwen3.8-27B-FP8", "017b", clock=lambda: 1_760_000_000.0)
    for rnd in (1, 2):
        # P3: the mirror through the L1 roof, a decor piece no agent tool edits, seen in every round
        log.event("finding", rnd, source="code", checklist="X2", severity="critical", target="dec_L1_009",
                  room_id="r_L1_koridor", finding="dec_L1_009 pokes through the roof", cause="decor_under_roof",
                  not_yours="a decor piece: the decor stage places it", report_to="decor")
        log.event("finding", rnd, source="code", checklist="F3", severity="major", target=f"f{rnd}", finding="x",
                  cause="orientation")
    log.event("round", 1, counts={"findings_removed": 3})
    log.event("round", 2, counts={"findings_removed": 0})
    log.event("check", 1, source="code", tool="context_budget", target=None, call_id="r1-p5", status="context_full",
              counts={"cuts": 2, "chars_removed": 41000, "max_model_len": 32768})
    log.event("stop", 2, reason="the rounds are used up", status="max_rounds")
    log.save(final=True)
    block = AG.agent_block(out, out / "final", building={"furniture": [], "rooms": []})
    (rep,) = block["reported"]
    assert (rep["target"], rep["report_to"], rep["cause"], rep["rounds"]) == ("dec_L1_009", "decor",
                                                                              "decor_under_roof", [1, 2])
    (ctx,) = block["context"]
    assert ctx["status"] == "context_full" and ctx["chars_removed"] == 41000 and ctx["max_model_len"] == 32768
    md = "\n".join(AG.agent_lines({"agent": block}))
    assert "### Reported to other stages" in md and "| decor |" in md
    assert "### Context budget of the planner sessions" in md and "context_full" in md
    # f1 is gone in round 2 (measured 1); the dry re-check of round 1 predicted 3
    assert "1 measured; 3 predicted" in md


def test_the_log_schema_documents_the_new_call_and_finding_fields(tmp_path):
    from wenart.agent import log as LG

    log = LG.AgentLog(tmp_path / "toy", "toy", "m", "r", clock=lambda: 1_760_000_000.0)
    log.event("finding", 1, source="code", checklist="X2", severity="critical", target="dec_1", finding="x",
              cause="decor_under_roof", not_yours="the decor stage places it", report_to="decor")
    log.call({"call_id": "r1-p1", "kind": "chat", "model": "m", "revision": "r", "seconds": 1.0, "attempts": 1,
              "finish_reason": "length", "max_tokens": 1536})
    log.save(final=True)
    data = json.loads((tmp_path / "toy" / "orchestrator" / "log.json").read_text(encoding="utf-8"))
    assert LG.validate_log(data) == []
    assert data["calls"][0]["finish_reason"] == "length" and data["calls"][0]["max_tokens"] == 1536
    bad = copy.deepcopy(data)
    bad["calls"][0]["max_tokens"] = "1536"
    bad["events"][0]["report_to"] = 7
    assert len(LG.validate_log(bad)) >= 2                          # typed since the fix round after P3
