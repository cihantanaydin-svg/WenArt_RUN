"""The stage table of the full run: golden command lines and the table's columns (docs/milestone6.md §2.2)."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from wenart.run import stages as S
from wenart.run import state as ST
from wenart.run.projects import REPO_ROOT, private_project, public_project

MODELS = {"qwen": {"id": "Qwen/Qwen3-VL-8B-Instruct", "revision": "r1", "slug": "qwen3-vl-8b"},
          "glm": {"id": "zai-org/GLM-4.6V-Flash", "revision": "r2", "slug": "glm-4.6v-flash"}}
TOOLS = S.Tools(py="PY", polish_py="POLISH_PY", assets=Path("/workspace/assets"), render_samples=128,
                check_models=MODELS)
SMOKE = replace(TOOLS, smoke=True)
REF = public_project("synthetic-04", Path("/workspace/jobs/j/results"), REPO_ROOT)
O = "outputs/synthetic-04"
URL = "http://127.0.0.1:8001/v1"


def test_the_table_columns():
    assert [s.number for s in S.STAGE_LIST if s.number is not None] == list(range(18))
    assert S.PROJECT_STAGES == ("intake", "pipeline", "photos", "style", "assets", "fit", "layout", "decor", "refit",
                                "build", "render", "controls", "gate", "polish", "expected", "check", "combine",
                                "report")
    fail = {s.name: s.on_failure for s in S.STAGE_LIST if s.number is not None}
    assert {n for n, v in fail.items() if v == "warning"} == {"photos", "assets", "controls", "gate", "polish"}
    reuse = {s.name: s.reuse for s in S.STAGE_LIST if s.number is not None}
    assert {n for n, v in reuse.items() if v == "fingerprint"} == {"intake", "pipeline", "fit", "layout", "decor",
                                                                  "refit"}
    assert {n for n, v in reuse.items() if v == "own"} == {"build", "render", "controls", "gate", "polish", "check"}
    assert reuse["photos"] == "photos"
    holders = {s.name: s.holder for s in S.STAGE_LIST}
    assert {n for n, h in holders.items() if h == "vlm"} == {"photos", "layout", "check", "ab_realism", "ab_look_alt"}
    assert {n for n, h in holders.items() if h == "blender"} == {"build", "render", "controls", "ab_render",
                                                                 "ab_controls"}
    assert holders["gate"] == "gate" and holders["polish"] == "diffusion"
    heavy = {s.name for s in S.STAGE_LIST if s.heavy and s.number is not None}
    assert heavy == {"photos", "layout", "build", "render", "controls", "gate", "polish", "check"}
    assert S.AB_NOT_COUNTED == ("ab_look_alt",) and set(S.STAGE_VERSION) == set(S.STAGES)


def test_code_patterns_match_files():
    for stage in S.STAGE_LIST:
        for pattern in stage.code:
            assert ST._code_files([pattern], REPO_ROOT), (stage.name, pattern)


def test_outputs_of():
    assert S.outputs_of("intake", "real-01") == ["input/real-01", "intake_manifest.json"]
    assert S.outputs_of("layout", "p") == ["building_furnished.json", "layout.json"]


def test_golden_commands_cpu_stages():
    assert S.pipeline(TOOLS, REF) == ["PY", "-m", "wenart.ingest.pipeline", "projects/synthetic-04", "--out", O]
    assert S.style(TOOLS, REF) == ["PY", "-m", "wenart.style", "projects/synthetic-04", "--out", f"{O}/style.json"]
    assert S.style(TOOLS, REF, terms=True)[-2:] == ["--photo-terms", f"{O}/style_photos/terms.json"]
    assert S.assets(TOOLS, REF) == ["PY", "-m", "wenart.assets", "fetch", "--style", f"{O}/style.json", "--assets",
                                    "/workspace/assets", "--size", "2k"]
    assert S.fit(TOOLS, REF) == ["PY", "-m", "wenart.furniture.fit", f"{O}/building.json", "--catalog",
                                 "wenart/furniture/catalog.json", "--out", f"{O}/building_fitted.json", "--assets",
                                 "/workspace/assets"]
    assert S.decor(TOOLS, REF, True) == ["PY", "-m", "wenart.furniture.decor", f"{O}/building_furnished.json",
                                         "--out", f"{O}/building_decor.json"]
    assert S.decor(TOOLS, REF, False)[3] == f"{O}/building_fitted.json"
    assert S.refit(TOOLS, REF) == ["PY", "-m", "wenart.furniture.fit", f"{O}/building_decor.json", "--catalog",
                                   "wenart/furniture/catalog.json", "--out", f"{O}/building_final.json",
                                   "--assets", "/workspace/assets"]
    assert S.expected(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "expected", "--project-out", O]
    assert S.plan_crops(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "plan-crops", "--project-out", O]
    assert S.combine(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "combine", "--project-out", O]
    assert S.calibrate(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "calibrate", "--project-out", O]
    assert S.report(TOOLS, REF) == ["PY", "-m", "wenart.report", "final", "--project-out", O]


def test_golden_commands_private_intake(tmp_path):
    ref = private_project("real-01", repo_root=REPO_ROOT)
    assert S.intake(TOOLS, ref) == ["PY", "-m", "wenart.intake", "stage", "real-01", "--out",
                                    "/workspace/outputs-private/real-01/input/real-01"]
    assert S.pipeline(TOOLS, ref) == ["PY", "-m", "wenart.ingest.pipeline",
                                      "/workspace/outputs-private/real-01/input/real-01", "--out",
                                      "/workspace/outputs-private/real-01"]
    tools = replace(TOOLS, private_root=tmp_path / "pp")
    assert S.intake(tools, ref)[-2:] == ["--root", str(tmp_path / "pp")]
    # The report of a private project names plan crops and debug images, never copies them (§7.4).
    assert S.report(TOOLS, ref) == ["PY", "-m", "wenart.report", "final", "--project-out",
                                    "/workspace/outputs-private/real-01", "--private"]


def test_golden_commands_vlm_stages():
    photos = [REPO_ROOT / "projects" / "synthetic-04" / "style_photos" / "a.jpg"]
    assert S.photos_read(TOOLS, REF, "glm", URL, photos) == [
        "PY", "-m", "wenart.style.photos", "read", "projects/synthetic-04/style_photos/a.jpg", "--model-key", "glm",
        "--server", URL, "--out", f"{O}/style_photos/passes.json"]
    assert S.photos_combine(TOOLS, REF) == ["PY", "-m", "wenart.style.photos", "combine",
                                            f"{O}/style_photos/passes.json", "--out", f"{O}/style_photos/terms.json"]
    assert S.layout(TOOLS, REF, URL) == [
        "PY", "-m", "wenart.furniture.layout", f"{O}/building_fitted.json", "--style", f"{O}/style.json", "--server",
        URL, "--model", "Qwen/Qwen3-VL-8B-Instruct", "--out", f"{O}/building_furnished.json", "--debug",
        f"{O}/layout_debug", "--passes", "2"]
    assert S.check_run(TOOLS, REF, "qwen", URL, 2) == [
        "PY", "-m", "wenart.vision_check", "run", "--project-out", O, "--model-key", "qwen", "--server", URL,
        "--kinds", "cycles,polished", "--workers", "2"]
    assert S.preference(TOOLS, REF, "glm", URL, 4) == [
        "PY", "-m", "wenart.vision_check", "preference", "--project-out", O, "--model-key", "glm", "--server", URL,
        "--kinds", "polished", "--workers", "4"]
    assert S.style_photo_test(TOOLS, REF, "qwen", URL) == [
        "PY", "-m", "wenart.vision_check", "style-photo", "--project-out", O, "--model-key", "qwen", "--server", URL,
        "--photo", "tests/fixtures/style_photo_synthetic-03_salon.jpg", "--out", f"{O}/check/style_photo_test.json"]
    assert (REPO_ROOT / S.STYLE_TEST_PHOTO).is_file()


def test_golden_commands_gpu_stages():
    assert S.build(TOOLS, REF) == [
        "PY", "-m", "wenart.blender.cli", "build", "--building", f"{O}/building_final.json", "--style",
        f"{O}/style.json", "--assets", "/workspace/assets", "--out", f"{O}/scene", "--preview-samples", "32",
        "--camera-policy", "search", "--reuse"]
    assert "--reuse" not in S.build(TOOLS, REF, force=True)
    # Smoke profile (§2.5): the top-down previews of the builds with 4 samples on the CPU.
    for cmd in (S.build(SMOKE, REF), S.ab_build(SMOKE, REF), S.ab_build(SMOKE, REF, "ctl_flat")):
        assert cmd[cmd.index("--preview-samples") + 1] == "4"
    assert S.render(TOOLS, REF) == [
        "PY", "-m", "wenart.blender.cli", "render", "--scene", f"{O}/scene/scene.blend", "--out", f"{O}/renders",
        "--cameras", "all", "--samples", "128", "--res", "1920x1080", "--exposure", "auto", "--white-balance", "auto"]
    assert S.render(TOOLS, REF, force=True)[-1] == "--force"
    assert S.render(SMOKE, REF)[8:] == ["--cameras", "all", "--samples", "16", "--res", "480x270", "--exposure",
                                        "auto", "--white-balance", "auto", "--device", "cpu"]
    assert S.select_controls(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "select-controls", "--project-out", O]
    assert S.control_render(TOOLS, REF, "cam_a:f1;cam_b:w1+plug") == [
        "PY", "-m", "wenart.blender.cli", "render", "--scene", f"{O}/scene/scene.blend", "--out", f"{O}/controls",
        "--hide-sets", "cam_a:f1;cam_b:w1+plug", "--look-from", f"{O}/renders/render_manifest.json", "--samples",
        "128", "--res", "1920x1080"]
    assert S.gate_calibrate(TOOLS, REF) == ["POLISH_PY", "-m", "wenart.gate", "calibrate", "--project-out", O]
    assert S.gate_validate(TOOLS, REF) == ["PY", "-m", "wenart.gate", "validate", "--project-out", O]
    assert S.polish(TOOLS, REF) == ["POLISH_PY", "-m", "wenart.polish", "run", "--project-out", O]
    assert S.polish(TOOLS, REF, force=True)[-1] == "--force"
    assert S.CUDA_ALLOC == {"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}


def test_hide_sets_limit():
    assert S.limit_hide_sets("a:1;b:2+plug;c:3", 2) == "a:1;b:2+plug"
    assert S.limit_hide_sets("a:1;b:2", None) == "a:1;b:2"
    assert S.limit_hide_sets("", 2) == "" and S.limit_hide_sets(None, None) == ""


def test_golden_commands_ab():
    assert S.ab_m5(TOOLS, REF) == ["PY", "-m", "wenart.run", "ab-m5", "--project", "synthetic-04", "--project-out",
                                   O, "--commit", S.M5_LOOK_COMMIT]
    assert S.M5_LOOK_COMMIT == "a2adcef58ede7e4f9e92dd6a847e1e4692075131"
    assert S.ab_build(TOOLS, REF) == [
        "PY", "-m", "wenart.blender.cli", "build", "--building", f"{O}/ab/building_m5.json", "--style",
        f"{O}/style.json", "--assets", "/workspace/assets", "--out", f"{O}/ab/scene", "--preview-samples", "32",
        "--camera-policy", "m5", "--reuse"]
    assert S.ab_build(TOOLS, REF, "ctl_flat")[-4:] == ["--camera-policy", "m5", "--no-textures", "--reuse"]
    assert S.ab_build(TOOLS, REF, "ctl_proxy")[11] == f"{O}/ab/ctl_proxy/scene"
    assert S.ab_build(TOOLS, REF, "ctl_proxy")[-2] == "--proxies"
    assert S.ab_render(TOOLS, REF) == [
        "PY", "-m", "wenart.blender.cli", "render", "--scene", f"{O}/ab/scene/scene.blend", "--out", f"{O}/ab/renders",
        "--cameras", "all", "--samples", "128", "--res", "1920x1080", "--exposure", "auto", "--white-balance", "auto",
        "--alt-look", "AgX - Punchy", "--preview-quality", "85"]
    assert S.ab_render(SMOKE, REF, ["c1", "c2"])[8:10] == ["--cameras", "c1,c2"]
    cams = ["c1", "c2"]
    base = ["PY", "-m", "wenart.blender.cli", "render"]
    look = ["--look-from", f"{O}/ab/renders/render_manifest.json", "--preview-quality", "85"]
    assert S.ab_control_render(TOOLS, REF, "ctl_flat", cams) == base + [
        "--scene", f"{O}/ab/ctl_flat/scene/scene.blend", "--out", f"{O}/ab/ctl_flat/renders", "--cameras", "c1,c2",
        "--samples", "128", "--res", "1920x1080"] + look
    assert S.ab_control_render(TOOLS, REF, "ctl_direct", cams)[-2:] == ["--max-bounces", "0"]
    assert S.ab_control_render(TOOLS, REF, "ctl_direct", cams)[5] == f"{O}/ab/scene/scene.blend"
    lowspp = S.ab_control_render(TOOLS, REF, "ctl_lowspp", cams)
    assert lowspp[lowspp.index("--samples") + 1] == "4" and lowspp[-1] == "--no-denoise"
    assert S.ab_control_render(TOOLS, REF, "nuisance_ev", cams)[-2:] == ["--ev-offset", "0.3"]
    assert S.ab_control_render(SMOKE, REF, "ctl_proxy", cams)[10:16] == ["--samples", "16", "--res", "480x270",
                                                                         "--device", "cpu"]
    assert S.realism_pairs(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "realism-pairs", "--project-out", O]
    assert S.realism_pairs(TOOLS, REF, True)[-1] == "--controls"
    assert S.realism(TOOLS, REF, "glm", URL, 2) == [
        "PY", "-m", "wenart.vision_check", "realism", "--project-out", O, "--model-key", "glm", "--server", URL,
        "--workers", "2"]
    assert S.realism(TOOLS, REF, "glm", URL, 2, ["ctl_flat", "m5_vs_m6"])[-2:] == ["--sets", "ctl_flat,m5_vs_m6"]
    assert S.realism_combine(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "realism-combine", "--project-out", O]
    ref1 = public_project("synthetic-01", Path("/r"), REPO_ROOT)
    assert S.realism_summary(TOOLS, [ref1, REF], "synthetic-01", Path("/workspace/jobs/j/results/realism")) == [
        "PY", "-m", "wenart.vision_check", "realism-summary", "--project-outs", "outputs/synthetic-01", O,
        "--controls-project", "synthetic-01", "--out", "/workspace/jobs/j/results/realism"]


@pytest.mark.parametrize("fn, args, want", [
    (S.est_render, (30,), 300.0), (S.est_controls, (5,), 40.0), (S.est_polish, (10,), 200.0),
    (S.est_calls, (10, 2), 22.0), (S.est_calls, (10, 4), 11.0), (S.est_server, ("qwen",), 300.0),
    (S.est_server, ("glm",), 150.0)])
def test_estimates(fn, args, want):
    assert fn(*args) == pytest.approx(want)
    assert S.EST_BUILD_S == 60.0 and S.EST_GATE_S == 150.0
