"""The stage table of the full run: golden command lines and the table's columns (docs/milestone6.md §2.2;
docs/milestone7.md §9.1: recognize, pipeline_final and detect, the contiguous numbers 0..20, realism v2)."""
from __future__ import annotations

import ast
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
    assert [s.number for s in S.STAGE_LIST if s.number is not None] == list(range(24))
    # Milestone 9: decor_ask (the AI decor's two passes, in the layout's Qwen session) and export (the 3D files);
    # Milestone 10: sheets (the sheet analysis before any wall is read, docs/milestone10.md §1.5).
    assert S.PROJECT_STAGES == ("intake", "sheets", "pipeline", "recognize", "pipeline_final", "photos", "style", "assets",
                                "fit", "layout", "decor_ask", "decor", "refit", "build", "render", "export",
                                "controls", "gate", "polish", "detect", "expected", "check", "combine", "report")
    fail = {s.name: s.on_failure for s in S.STAGE_LIST if s.number is not None}
    assert {n for n, v in fail.items() if v == "warning"} == {"recognize", "photos", "assets", "decor_ask", "export",
                                                             "controls", "gate", "polish", "detect"}
    reuse = {s.name: s.reuse for s in S.STAGE_LIST if s.number is not None}
    assert {n for n, v in reuse.items() if v == "fingerprint"} == {"intake", "sheets", "pipeline", "pipeline_final", "fit",
                                                                  "layout", "decor_ask", "decor", "refit"}
    assert {n for n, v in reuse.items() if v == "own"} == {"recognize", "build", "render", "export", "controls",
                                                          "gate", "polish", "detect", "check"}
    assert reuse["photos"] == "photos"
    holders = {s.name: s.holder for s in S.STAGE_LIST}
    assert {n for n, h in holders.items() if h == "vlm"} == {"recognize", "photos", "layout", "decor_ask", "check",
                                                             "ab_realism"}
    assert {n for n, h in holders.items() if h == "blender"} == {"build", "render", "export", "controls", "ab_render",
                                                                 "ab_controls"}
    assert {n for n, h in holders.items() if h == "gate"} == {"gate", "detect"} and holders["polish"] == "diffusion"
    assert holders["pipeline_final"] == "cpu"
    heavy = {s.name for s in S.STAGE_LIST if s.heavy and s.number is not None}
    assert heavy == {"recognize", "photos", "layout", "decor_ask", "build", "render", "export", "controls", "gate",
                     "polish", "detect", "check"}
    assert S.outputs_of("decor_ask", "p") == ["decor_ai_answers.json"]
    assert S.outputs_of("export", "p") == ["export/export_manifest.json"]
    assert S.AB_STAGES == ("ab_prepare", "ab_m5", "ab_render", "ab_controls", "ab_pairs", "ab_realism", "ab_combine")
    assert S.AB_NOT_COUNTED == () and set(S.STAGE_VERSION) == set(S.STAGES)
    assert S.STAGES["pipeline_final"].code == S.STAGES["pipeline"].code == S.PIPELINE_CODE == S.STAGES["sheets"].code
    assert S.outputs_of("pipeline_final", "p") == ["sheets.json", "building.json", "report.md"]
    assert S.outputs_of("sheets", "p") == ["sheets.json", "sheets_report.md"]
    assert S.QUESTION_DIRS == ("sheets", "recognition")
    assert S.outputs_of("detect", "p") == ["detect/detect_manifest.json"]
    assert S.outputs_of("ab_pairs", "p") == ["ab/pairs_v2.json"]
    assert S.outputs_of("ab_combine", "p") == ["check/realism/realism2_ab.json"]


def test_code_patterns_match_files():
    for stage in S.STAGE_LIST:
        for pattern in stage.code:
            assert ST._code_files([pattern], REPO_ROOT), (stage.name, pattern)


def _module_file(name: str):
    path = REPO_ROOT / Path(*name.split("."))
    if (path / "__init__.py").is_file():
        return path / "__init__.py"
    return path.with_suffix(".py") if path.with_suffix(".py").is_file() else None


def import_closure(entry: str) -> set:
    """Every ``wenart`` source file that ``python -m <entry>`` may import: an ast walk over every module (imports
    inside functions included), relative imports resolved, the package ``__init__.py`` of every module and a
    package's ``__main__.py``."""
    files: dict = {}
    todo: list = []

    def add(name: str) -> None:
        parts = name.split(".")
        for i in range(1, len(parts) + 1):
            mod = ".".join(parts[:i])
            f = _module_file(mod)
            if f is not None and f not in files:
                files[f] = mod
                todo.append(f)

    add(entry)
    main = _module_file(entry)
    if main is not None and main.name == "__init__.py" and (main.parent / "__main__.py").is_file():
        files[main.parent / "__main__.py"] = entry
        todo.append(main.parent / "__main__.py")
    while todo:
        f = todo.pop()
        mod = files[f]
        package = mod if f.name in ("__init__.py", "__main__.py") else mod.rpartition(".")[0]
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] == "wenart":
                        add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = package.split(".")[:len(package.split(".")) - node.level + 1]
                    target = ".".join(base + ([node.module] if node.module else []))
                else:
                    target = node.module or ""
                if target.split(".")[0] != "wenart":
                    continue
                add(target)
                for alias in node.names:           # "from wenart.assets import models": a submodule
                    if _module_file(f"{target}.{alias.name}") is not None:
                        add(f"{target}.{alias.name}")
    return {f.relative_to(REPO_ROOT).as_posix() for f in files}


def test_the_import_closure_sees_function_level_and_relative_imports():
    fit = import_closure("wenart.furniture.fit")
    # download_fitted imports wenart.assets.models/fetch/web inside the function; parametric imports proxies.
    assert {"wenart/assets/models.py", "wenart/assets/fetch.py", "wenart/assets/web.py", "wenart/blender/proxies.py",
            "wenart/__init__.py", "wenart/furniture/__init__.py"} <= fit
    assert "wenart/synthetic/blocks.py" in import_closure("wenart.ingest.pipeline")
    assert {"wenart/gate/__main__.py", "wenart/gate/calibrate.py", "wenart/gate/validate.py"} <= \
        import_closure("wenart.gate")


def test_code_lists_cover_the_import_closure():
    """R2: a code fix in any module a fingerprinted stage imports must change the stage's fingerprint (else a
    resumed pod reuses outputs made with the old code). The gate's code hash keys the calibration reuse."""
    private = private_project("real-01", repo_root=REPO_ROOT)
    commands = {"intake": S.intake(TOOLS, private), "sheets": S.sheets(TOOLS, REF), "pipeline": S.pipeline(TOOLS, REF),
                "pipeline_final": S.pipeline_final(TOOLS, REF), "fit": S.fit(TOOLS, REF),
                "layout": S.layout(TOOLS, REF, URL), "decor": S.decor(TOOLS, REF, True),
                "decor_ask": S.decor_ask(TOOLS, REF, True, URL), "refit": S.refit(TOOLS, REF),
                "gate": S.gate_calibrate(TOOLS, REF), "detect": S.detect(TOOLS, REF)}
    assert set(commands) == {s.name for s in S.STAGE_LIST if s.reuse == "fingerprint"} | {"gate", "detect"}
    for stage, cmd in commands.items():
        assert cmd[1] == "-m", stage
        covered = {p.relative_to(REPO_ROOT).as_posix() for p in ST._code_files(S.STAGES[stage].code, REPO_ROOT)}
        missing = sorted(import_closure(cmd[2]) - covered)
        assert not missing, (stage, missing)
    # The data files the stages read are listed too.
    for stage in ("fit", "refit"):
        assert S.CATALOG in S.STAGES[stage].code and "wenart/schema/**" in S.STAGES[stage].code
        # catalog_objaverse.json (once committed) through the catalog*.json pattern (catalog.load merges it).
        assert "wenart/furniture/catalog*.json" in S.STAGES[stage].code
    for stage in ("sheets", "pipeline", "pipeline_final"):
        code = S.STAGES[stage].code
        assert "wenart/schema/**" in code and S.CHECK_YAML in code       # model ids and slugs of the answers
        covered = {p.relative_to(REPO_ROOT).as_posix() for p in ST._code_files(code, REPO_ROOT)}
        assert "wenart/recognition/size_table.yaml" in covered


def test_outputs_of():
    assert S.outputs_of("intake", "real-01") == ["input/real-01", "intake_manifest.json"]
    assert S.outputs_of("layout", "p") == ["building_furnished.json", "layout.json", "completion.json",
                                           "completion_report.md"]                     # Milestone 10: completion


def test_golden_commands_cpu_stages():
    assert S.pipeline(TOOLS, REF) == ["PY", "-m", "wenart.ingest.pipeline", "projects/synthetic-04", "--out", O]
    assert S.style(TOOLS, REF) == ["PY", "-m", "wenart.style", "projects/synthetic-04", "--out", f"{O}/style.json"]
    assert S.style(TOOLS, REF, terms=True)[-2:] == ["--photo-terms", f"{O}/style_photos/terms.json"]
    assert S.assets(TOOLS, REF) == ["PY", "-m", "wenart.assets", "fetch", "--style", f"{O}/style.json", "--assets",
                                    "/workspace/assets", "--size", "2k"]
    assert S.fit(TOOLS, REF) == ["PY", "-m", "wenart.furniture.fit", f"{O}/building.json", "--catalog",
                                 "wenart/furniture/catalog.json", "--out", f"{O}/building_fitted.json", "--assets",
                                 "/workspace/assets"]
    # Milestone 9: the AI decor's agreement and checks, the rules per room without answers.
    assert S.decor(TOOLS, REF, True) == ["PY", "-m", "wenart.furniture.decor_ai", "apply",
                                         f"{O}/building_furnished.json", "--style", f"{O}/style.json", "--answers",
                                         f"{O}/decor_ai_answers.json", "--out", f"{O}/building_decor.json",
                                         "--debug", f"{O}/decor_debug"]
    assert S.decor(TOOLS, REF, False)[4] == f"{O}/building_fitted.json"
    assert S.decor_ask(TOOLS, REF, True, URL) == ["PY", "-m", "wenart.furniture.decor_ai", "ask",
                                                  f"{O}/building_furnished.json", "--style", f"{O}/style.json",
                                                  "--server", URL, "--model", TOOLS.model_id("qwen"), "--answers",
                                                  f"{O}/decor_ai_answers.json"]
    assert S.export(TOOLS, REF) == ["PY", "-m", "wenart.blender.cli", "export", "--scene", f"{O}/scene/scene.blend",
                                    "--renders", f"{O}/renders/render_manifest.json", "--out", f"{O}/export",
                                    "--name", "synthetic-04"]
    # refit: the library style filter of the final style (M7 §6.3); fit stays style-free.
    assert S.refit(TOOLS, REF) == ["PY", "-m", "wenart.furniture.fit", f"{O}/building_decor.json", "--catalog",
                                   "wenart/furniture/catalog.json", "--out", f"{O}/building_final.json",
                                   "--assets", "/workspace/assets", "--style", f"{O}/style.json"]
    assert "--style" not in S.fit(TOOLS, REF)
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
        f"{O}/layout_debug", "--passes", "2", "--project-dir", S.t(REF.project_dir)]
    # M7 §8.1: the insertion controls are asked in every full run.
    assert S.check_run(TOOLS, REF, "qwen", URL, 2) == [
        "PY", "-m", "wenart.vision_check", "run", "--project-out", O, "--model-key", "qwen", "--server", URL,
        "--kinds", "cycles,polished,controls", "--workers", "2"]
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
        "--camera-policy", "search", "--brief", S.t(REF.project_dir), "--reuse"]
    assert "--reuse" not in S.build(TOOLS, REF, force=True)
    # Milestone 8 (§5): the brief's render.lens_mm goes to the build (none for auto: the 18 / 16 mm rule).
    assert S.build(TOOLS, REF, lens_mm=20.0)[-4:] == [S.t(REF.project_dir), "--lens-mm", "20", "--reuse"]
    assert S.build(TOOLS, REF, force=True, lens_mm=22.5)[-2:] == ["--lens-mm", "22.5"]
    assert S.build(TOOLS, REF, lens_mm=None) == S.build(TOOLS, REF)
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
    # M7 §6.1: the default look is AgX - Punchy, the alternative look None (stages.ALT_LOOK).
    assert S.ALT_LOOK == "None"
    assert S.ab_render(TOOLS, REF) == [
        "PY", "-m", "wenart.blender.cli", "render", "--scene", f"{O}/ab/scene/scene.blend", "--out", f"{O}/ab/renders",
        "--cameras", "all", "--samples", "128", "--res", "1920x1080", "--exposure", "auto", "--white-balance", "auto",
        "--alt-look", "None", "--preview-quality", "85"]
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
    # Realism v2 (M7 §8.2; the CLIs of wenart.vision_check).
    assert S.realism2_pairs(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "realism2-pairs", "--project-out", O]
    ref1 = public_project("synthetic-01", Path("/r"), REPO_ROOT)
    ref3 = public_project("synthetic-03", Path("/r"), REPO_ROOT)
    assert S.realism2_pairs(TOOLS, ref1, True, [ref3.out_dir, REF.out_dir]) == [
        "PY", "-m", "wenart.vision_check", "realism2-pairs", "--project-out", "outputs/synthetic-01", "--controls",
        "--project-outs", "outputs/synthetic-03", O]
    assert S.realism2(TOOLS, REF, "glm", URL, 8) == [
        "PY", "-m", "wenart.vision_check", "realism2", "--project-out", O, "--model-key", "glm", "--server", URL,
        "--workers", "8"]
    assert S.realism2(TOOLS, REF, "glm", URL, 2, ["ctl_flat", "look_alt"])[-2:] == ["--sets", "ctl_flat,look_alt"]
    assert S.realism2_combine(TOOLS, REF) == ["PY", "-m", "wenart.vision_check", "realism2-combine",
                                              "--project-out", O]
    assert S.realism2_summary(TOOLS, [ref3, REF], ref1.out_dir, Path("/workspace/jobs/j/results/realism")) == [
        "PY", "-m", "wenart.vision_check", "realism2-summary", "--project-outs", "outputs/synthetic-03", O,
        "--controls-project", "outputs/synthetic-01", "--out", "/workspace/jobs/j/results/realism"]
    assert "--controls-project" not in S.realism2_summary(TOOLS, [REF], None, Path("/r"))


@pytest.mark.parametrize("fn, args, want", [
    (S.est_render, (30,), 330.0), (S.est_controls, (5,), 40.0), (S.est_polish, (10,), 200.0),
    (S.est_detect, (10,), 90.0), (S.est_realism2, (35, 8, 8), 4.4 * (8 * 27 / 8 + 8 * 8)),
    (S.est_calls, (10, 2), 22.0), (S.est_calls, (10, 4), 11.0), (S.est_server, ("qwen",), 300.0),
    (S.est_server, ("glm",), 150.0)])
def test_estimates(fn, args, want):
    assert fn(*args) == pytest.approx(want)
    assert S.EST_BUILD_S == 60.0 and S.EST_GATE_S == 150.0


def test_golden_commands_milestone_7():
    """M7 §9.1: the pipeline again with the answers, the recognition passes, the alt look of an A/B project's
    render, the detector."""
    assert S.pipeline_final(TOOLS, REF) == ["PY", "-m", "wenart.ingest.pipeline", "projects/synthetic-04", "--out", O,
                                            "--answers", f"{O}/recognition"]
    assert S.pipeline_final(TOOLS, REF, no_ai=True)[-3:] == ["--answers", f"{O}/recognition", "--no-ai"]
    assert S.pipeline_final(TOOLS, REF, answers=False, no_ai=True)[-1] == "--no-ai"     # the smoke profile
    assert "--answers" not in S.pipeline_final(TOOLS, REF, answers=False, no_ai=True)
    seeds = S.recognition_seeds(REF)
    assert seeds == REPO_ROOT / "results" / "recognition" / "synthetic-04"
    assert S.recognize(TOOLS, REF, "glm", URL, 8, seeds) == [
        "PY", "-m", "wenart.recognition.answers", "ask", f"{O}/recognition", "--model-key", "glm", "--server", URL,
        "--workers", "8", "--seed-answers", "results/recognition/synthetic-04"]
    assert S.recognize(TOOLS, REF, "qwen", None, None, seeds) == [
        "PY", "-m", "wenart.recognition.answers", "ask", f"{O}/recognition", "--model-key", "qwen",
        "--seed-answers", "results/recognition/synthetic-04"]
    private = private_project("real-01", repo_root=REPO_ROOT)
    assert S.recognition_seeds(private) is None
    assert S.render(TOOLS, REF, alt_look=True)[-2:] == ["--alt-look", "None"]
    assert S.render(TOOLS, REF, force=True, alt_look=True)[-3:] == ["--alt-look", "None", "--force"]
    assert "--alt-look" not in S.render(TOOLS, REF)
    assert S.detect(TOOLS, REF) == ["POLISH_PY", "-m", "wenart.gate", "detect", O, "--manifest",
                                    f"{O}/polish/polish_manifest.json", "--out", f"{O}/detect"]
    assert S.detect(TOOLS, REF, force=True)[-1] == "--force"
