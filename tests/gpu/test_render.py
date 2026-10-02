"""Milestone 3 GPU tests: run on the pod by scripts/jobs/render.sh after the
renders (pytest -m gpu tests/gpu/test_render.py). They read the manifests the
job wrote under $WENART_OUTPUTS (default /workspace/repo/outputs) for the
projects in $RENDER_TEST_PROJECTS (the job exports the projects whose render
stage ran; default synthetic-01 synthetic-03):

- Cycles used the GPU (OPTIX or CUDA), every camera of every room rendered at
  1920x1080, one view takes under 4 minutes on an A5000-class card (measured
  in this run or carried over from the run that rendered the view);
- the passes exist, the depth pass has a sensible indoor range;
- the object index pass of every view contains the index of every proxy the
  camera plan lists as inside its frustum;
- every render comes from the scene.blend of this build (fingerprint) and the
  two pass index tables agree;
- previews are small enough to copy into the results.
"""
import hashlib
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("RENDER_TEST_PROJECTS", "synthetic-01 synthetic-03").split() if p]
MAX_SECONDS_PER_VIEW = 240.0


def _load(project: str, name: str) -> dict:
    path = OUTPUTS / project / name
    assert path.exists(), (f"{path} missing: did the job run the build/render stages for {project}? "
                           f"(RENDER_TEST_PROJECTS={' '.join(PROJECTS)})")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    scene = _load(request.param, "scene/scene_manifest.json")
    render = _load(request.param, "renders/render_manifest.json")
    return request.param, scene, render


def test_gpu_device_and_full_resolution(project):
    name, _scene, render = project
    assert render["device"] in ("OPTIX", "CUDA"), f"{name}: Cycles rendered on {render['device']}"
    assert render["resolution"] == [1920, 1080]
    assert render["samples"] >= 128
    assert render["denoiser"] == "OPENIMAGEDENOISE"


def test_every_room_has_three_views(project):
    name, scene, render = project
    rendered = {r["camera"] for r in render["renders"]}
    planned = {c["name"] for c in scene["cameras"]}
    assert planned <= rendered, f"{name}: missing renders {sorted(planned - rendered)}"
    rooms = {c["room_id"] for c in scene["cameras"]}
    for room in rooms:
        assert {f"cam_{room}_{i}" for i in (1, 2, 3)} <= rendered


def test_view_time_under_four_minutes(project):
    name, _scene, render = project
    # A skipped view keeps the seconds of the run that rendered it, so a resumed or
    # idempotent re-run is judged on the same measured times.
    timed = [r for r in render["renders"] if isinstance(r.get("seconds"), (int, float)) and r["seconds"] > 0]
    untimed = sorted(r["camera"] for r in render["renders"] if r not in timed)
    assert timed and not untimed, (f"{name}: views without a measured time {untimed}; "
                                   f"re-render them with FORCE_RENDER=1")
    slow = [(r["camera"], r["seconds"]) for r in timed if r["seconds"] > MAX_SECONDS_PER_VIEW]
    assert not slow, f"{name}: views over {MAX_SECONDS_PER_VIEW}s: {slow}"


def test_render_matches_the_scene_build(project):
    name, scene, render = project
    blend = OUTPUTS / name / "scene" / "scene.blend"
    fingerprint = hashlib.sha256(blend.read_bytes()).hexdigest()
    assert render["scene_sha256"] == fingerprint, f"{name}: render_manifest.json is not from this scene.blend"
    stale = sorted(r["camera"] for r in render["renders"] if r.get("scene_sha256") != fingerprint)
    assert not stale, f"{name}: renders of another scene build (re-render them): {stale}"
    assert render["pass_index"] == scene["pass_index"], f"{name}: the two pass index tables differ"


def test_passes_exist_and_depth_is_plausible(project):
    name, _scene, render = project
    out = OUTPUTS / name / "renders"
    for r in render["renders"]:
        assert (out / r["png"]).exists() and (out / r["exr"]).exists(), r["camera"]
        assert (out / r["preview"]).stat().st_size <= 300_000, r["camera"]
        depth = r["depth"]
        assert depth is not None, f"{r['camera']}: no depth statistics"
        assert 0.1 < depth["min"] < depth["max"] < 60.0, (r["camera"], depth)
        assert depth["coverage"] > 0.9, (r["camera"], depth)


def test_index_pass_contains_every_visible_proxy(project):
    name, scene, render = project
    table = scene["pass_index"]
    plans = {c["name"]: c for c in scene["cameras"]}
    missing = []
    for r in render["renders"]:
        # Milestone 4 keys furniture by its id (proxies by proxy:<id>): accept both.
        expected = {table[k] for f in plans[r["camera"]]["visible_furniture"]
                    for k in (f, f"proxy:{f}") if k in table}
        seen = set(r["index_values"])
        if not expected <= seen:
            missing.append((r["camera"], sorted(expected - seen)))
    assert not missing, f"{name}: proxies planned in the frustum but absent from the index pass: {missing}"
