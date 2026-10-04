"""CPU tests of the render bookkeeping (``wenart/blender/render.py``) and the
render job: the manifest is written after every camera, a ``--cameras``
subset merges into the previous manifest, a skipped camera keeps its measured
time and recomputes its pass statistics from the EXR, a camera is reused only
when its PNG, EXR and preview exist and the scene fingerprint matches, and the
render table of pass indices equals the one of the scene manifest. The GPU
test logic (tests/gpu/test_render.py) is exercised here on the CPU output.

Tiny renders: 64x36 pixels, 4 samples, synthetic-01 level L0 (15 cameras),
flat colours. Skipped with a reason when no Blender binary is found.
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import time
from pathlib import Path

import pytest

from wenart import views as V
from wenart.blender import cli, schemas
from wenart.ingest.pipeline import build_project

ROOT = Path(__file__).resolve().parents[1]
BLENDER = cli.find_blender()
CAM_A, CAM_B, CAM_C = "cam_r_L0_salon_1", "cam_r_L0_salon_2", "cam_r_L0_salon_3"
CAM_CRASH = "cam_r_L0_yatak_odasi_1"   # sorts after CAM_C: its PNG path is made a directory
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                   "/workspace/tools/blender, /opt/wenart/blender, PATH)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(scene: Path, out: Path, cameras: str, force: bool = False) -> dict:
    cli.render(scene / "scene.blend", out, cameras=cameras, samples=4, res="64x36", device="cpu", force=force)
    return json.loads((out / "render_manifest.json").read_text(encoding="utf-8"))


def entries(manifest: dict) -> dict:
    return {r["camera"]: r for r in manifest["renders"]}


@pytest.fixture(scope="module")
def scene(tmp_path_factory):
    """synthetic-01 L0 built with flat colours; ``renders`` is shared by the tests in file order."""
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("render01")
    build_project(ROOT / "projects" / "synthetic-01", tmp / "pipeline")
    out = tmp / "scene"
    cli.build(tmp / "pipeline" / "building.json", out, level="L0", no_textures=True, preview_samples=4)
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    return {"dir": out, "manifest": manifest, "renders": tmp / "renders", "fingerprint": sha256(out / "scene.blend")}


@needs_blender
def test_manifest_carries_the_scene_fingerprint_and_the_scene_pass_table(scene):
    manifest = render(scene["dir"], scene["renders"], CAM_A)
    schemas.validate_render_manifest(manifest)
    assert manifest["scene_sha256"] == scene["fingerprint"]
    entry = entries(manifest)[CAM_A]
    assert entry["scene_sha256"] == scene["fingerprint"] and entry["skipped"] is False and entry["seconds"] > 0
    # Keyed by wenart id (frame and leaf of a door share one index), identical to the scene table.
    assert manifest["pass_index"] == scene["manifest"]["pass_index"]


@needs_blender
def test_subset_merges_into_the_previous_manifest_and_skipped_cameras_keep_their_statistics(scene):
    first = entries(render(scene["dir"], scene["renders"], CAM_A))[CAM_A]
    manifest = render(scene["dir"], scene["renders"], f"{CAM_A},{CAM_B}")
    got = entries(manifest)
    assert set(got) == {CAM_A, CAM_B}
    assert got[CAM_B]["skipped"] is False
    skipped = got[CAM_A]
    assert skipped["skipped"] is True
    assert skipped["seconds"] == first["seconds"] > 0, "the measured time of the first run must survive"
    assert skipped["depth"] == first["depth"] and skipped["index_values"] == first["index_values"]
    assert skipped["index_values"], "statistics are recomputed from the EXR, never stubbed"
    assert skipped["room_id"] == first["room_id"] == "r_L0_salon"
    # A forced re-render of one camera keeps the entries of the others.
    manifest = render(scene["dir"], scene["renders"], CAM_B, force=True)
    assert set(entries(manifest)) == {CAM_A, CAM_B}
    assert entries(manifest)[CAM_B]["skipped"] is False and entries(manifest)[CAM_A]["skipped"] is True


@needs_blender
def test_manifest_is_written_after_every_camera(scene):
    # The PNG path of the second camera is a directory, so its render fails after
    # the first camera: the manifest must already list the first one with its passes.
    out = scene["renders"]
    (out / f"{CAM_CRASH}.png").mkdir()
    with pytest.raises(RuntimeError, match="exited with"):
        render(scene["dir"], out, f"{CAM_C},{CAM_CRASH}")
    (out / f"{CAM_CRASH}.png").rmdir()
    for name in (f"{CAM_CRASH}_passes.exr", f"{CAM_CRASH}_preview.jpg"):
        if (out / name).exists():
            (out / name).unlink()
    manifest = json.loads((out / "render_manifest.json").read_text(encoding="utf-8"))
    got = entries(manifest)
    assert set(got) == {CAM_A, CAM_B, CAM_C}, "the crashed camera has no entry, the finished ones do"
    assert got[CAM_C]["skipped"] is False and got[CAM_C]["depth"] is not None and got[CAM_C]["index_values"]
    schemas.validate_render_manifest(manifest)


@needs_blender
def test_stale_or_unknown_renders_are_redone(scene):
    out = scene["renders"]
    path = out / "render_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    # The scene was rebuilt (another fingerprint recorded for CAM_A): its PNG is stale.
    for r in manifest["renders"]:
        if r["camera"] == CAM_A:
            r["scene_sha256"] = "0" * 64
    path.write_text(json.dumps(manifest), encoding="utf-8")
    got = entries(render(scene["dir"], out, f"{CAM_A},{CAM_B}"))
    assert got[CAM_A]["skipped"] is False and got[CAM_A]["scene_sha256"] == scene["fingerprint"]
    assert got[CAM_B]["skipped"] is True
    # A PNG without a preview is not a finished render.
    (out / f"{CAM_B}_preview.jpg").unlink()
    got = entries(render(scene["dir"], out, CAM_B))
    assert got[CAM_B]["skipped"] is False and (out / f"{CAM_B}_preview.jpg").exists()
    # A PNG without any manifest entry (run killed before the manifest was written) is not trusted.
    path.unlink()
    got = entries(render(scene["dir"], out, CAM_B))
    assert got[CAM_B]["skipped"] is False and set(got) == {CAM_B}


def _gpu_test_module(monkeypatch, outputs: Path):
    """tests/gpu/test_render.py imported against ``outputs`` (its env is read at import)."""
    monkeypatch.setenv("WENART_OUTPUTS", str(outputs))
    monkeypatch.setenv("RENDER_TEST_PROJECTS", "synthetic-01")
    spec = importlib.util.spec_from_file_location("gpu_test_render", ROOT / "tests" / "gpu" / "test_render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@needs_blender
def test_full_run_then_idempotent_rerun_pass_the_gpu_test_logic(scene, tmp_path, monkeypatch):
    out = scene["renders"]
    full = render(scene["dir"], out, "all")
    names = {c["name"] for c in scene["manifest"]["cameras"]}
    assert set(entries(full)) == names and len(names) == 15
    assert entries(full)[CAM_B]["skipped"] is True and entries(full)[CAM_A]["skipped"] is False
    # Second run on the same volume: everything skipped, every entry still timed and complete.
    again = render(scene["dir"], out, "all")
    assert all(r["skipped"] and r["seconds"] > 0 and r["depth"] and r["index_values"] for r in again["renders"])
    assert all(r["scene_sha256"] == scene["fingerprint"] for r in again["renders"])
    schemas.validate_render_manifest(again)
    # The GPU tests (all but the device check) must accept this resumed manifest.
    layout = tmp_path / "outputs" / "synthetic-01"
    layout.mkdir(parents=True)
    (layout / "scene").symlink_to(scene["dir"])
    (layout / "renders").symlink_to(out)
    gpu = _gpu_test_module(monkeypatch, tmp_path / "outputs")
    assert gpu.PROJECTS == ["synthetic-01"]
    project = ("synthetic-01", scene["manifest"], again)
    gpu.test_every_room_has_three_views(project)
    gpu.test_view_time_under_four_minutes(project)
    gpu.test_passes_exist_and_depth_is_plausible(project)
    gpu.test_index_pass_contains_every_visible_proxy(project)
    gpu.test_no_blocked_searched_view(project)            # Milestone 6 §4.2 (m5 cameras: blocked views allowed)
    gpu.test_cameras_render_with_their_own_lens(project)  # Milestone 8 §5 (m5 cameras: 24 mm, recorded per entry)
    assert {(r["lens_mm"], r["sensor_mm"]) for r in again["renders"]} == {(24.0, 36.0)}
    gpu.test_render_matches_the_scene_build(project)
    # Milestone 5 checks of the same module.
    gpu.test_entries_are_m5_renders_with_helper_maps(project)
    gpu.test_exposure_recorded_and_within_the_clamp(project)
    gpu.test_uint16_index_stats_match_the_index_maps(project)
    gpu.test_white_plaster_walls_are_neutral(project)
    with pytest.raises(AssertionError, match="OPTIX|CUDA|CPU"):
        gpu.test_gpu_device_and_full_resolution(project)


@needs_blender
def test_cameras_not_in_the_scene_move_to_dropped_stale_and_keep_their_files(scene):
    # Review L2: an output folder reused across a camera-policy switch holds entries and files of cameras the
    # scene no longer has. A run drops their entries (as before) and now lists them under dropped_stale with
    # the reason and the files left on disk; the files are never deleted and no reader takes them as views.
    out = scene["renders"]
    path = out / "render_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    gone = "cam_r_L0_gone_1"
    old = dict(entries(manifest)[CAM_A], camera=gone, png=f"{gone}.png", preview=f"{gone}_preview.jpg")
    manifest["renders"].append(old)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    for suffix in (".png", "_preview.jpg"):
        (out / f"{gone}{suffix}").write_bytes((out / f"{CAM_A}{suffix}").read_bytes())
    m = render(scene["dir"], out, "all")
    schemas.validate_render_manifest(m)
    assert gone not in entries(m) and len(m["renders"]) == 15 and all(r["skipped"] for r in m["renders"])
    (item,) = m["dropped_stale"]
    assert item["camera"] == gone and "no such camera in the scene" in item["reason"]
    assert item["files"] == [f"{gone}.png", f"{gone}_preview.jpg"] and item["render_key"] == old["render_key"]
    assert (out / f"{gone}.png").is_file() and (out / f"{gone}_preview.jpg").is_file()      # never deleted
    assert gone not in V.load_views(out, skip_stale=True)
    # Carried over by later runs while its files remain; not listed once they are gone.
    m = render(scene["dir"], out, CAM_A)
    assert [d["camera"] for d in m["dropped_stale"]] == [gone]
    for suffix in (".png", "_preview.jpg"):
        (out / f"{gone}{suffix}").unlink()
    assert render(scene["dir"], out, CAM_A)["dropped_stale"] == []


@needs_blender
def test_deadline_cut_drops_an_older_build_entry_it_did_not_render(scene, monkeypatch):
    # Review L2 (b): a render cut by WENART_DEADLINE kept the entry of a camera it did not re-render even when
    # that entry came from another scene build (M5 renders under the M6 camera name), and load_views returned it.
    out = scene["renders"]
    path = out / "render_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for r in manifest["renders"]:
        if r["camera"] == CAM_A:
            r["scene_sha256"] = "0" * 64
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setenv("WENART_DEADLINE", str(time.time() - 5))
    with pytest.raises(cli.BlenderFailed) as err:
        render(scene["dir"], out, "all")
    assert err.value.returncode == 3
    m = json.loads(path.read_text(encoding="utf-8"))
    schemas.validate_render_manifest(m)
    assert m["incomplete"] is True and m["not_rendered"] == [CAM_A]
    assert CAM_A not in entries(m) and len(m["renders"]) == 14
    (item,) = [d for d in m["dropped_stale"] if d["camera"] == CAM_A]
    assert "WENART_DEADLINE" in item["reason"] and item["scene_sha256"] == "0" * 64
    assert f"{CAM_A}.png" in item["files"] and (out / f"{CAM_A}.png").is_file()           # files kept
    assert CAM_A not in V.load_views(out, skip_stale=True) and CAM_B in V.load_views(out)
    # The resume renders it again and it leaves dropped_stale.
    monkeypatch.delenv("WENART_DEADLINE")
    m = render(scene["dir"], out, "all")
    assert entries(m)[CAM_A]["skipped"] is False and entries(m)[CAM_A]["scene_sha256"] == scene["fingerprint"]
    assert m["dropped_stale"] == [] and m["incomplete"] is False and len(m["renders"]) == 15


def test_render_job_passes_the_rendered_projects_to_the_gpu_tests():
    script = ROOT / "scripts" / "jobs" / "render.sh"
    subprocess.run(["bash", "-n", str(script)], check=True)
    text = script.read_text(encoding="utf-8")
    export = text.find("export RENDER_TEST_PROJECTS=")
    pytest_call = text.find("run_stage gpu-tests ")
    assert 0 < export < pytest_call, "the GPU tests must see which projects this job rendered"
    assert re.search(r'RENDERED\+=\("\$p"\)', text), "projects whose render stage ran are collected"
    # No render of a scene whose build failed in this run (the old scene.blend would be stale).
    assert re.search(r'stage_failed "build-\$p"', text)
