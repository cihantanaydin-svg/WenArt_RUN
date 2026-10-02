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

Milestone 5 (docs/milestone5.md §2, §9), on the new renders only:

- every entry is an M5 entry (schema: render key, index statistics, helper
  maps, exposure record) and its helper maps exist;
- the exposure was metered and recorded, within the clamp, on 1/6 stops,
  with a whitepoint of luminance 1;
- the uint16 index statistics agree with ``index_values`` and with the
  index map on disk;
- synthetic-01's white plaster walls look white: wall pixels of the rooms
  with plaster walls have a display R/B of at most 1.10.

Milestone 6 (docs/milestone6.md §4.2), cameras by policy (a scene-manifest
camera without ``policy`` is an M5 camera):

- policy ``m5``: three views per room; policy ``search``: 1-3 views per room
  by the area rule (``camsearch.room_view_count``) and every room of the
  building at least one;
- no searched view is blocked (index pass: one element over 0.55 of the
  frame, or depth pass: over 0.35 of the pixels nearer than 0.9 m) unless its
  plan carries the warning ``blocked unavoidable`` (listed); the share of
  views with under 10 % object pixels is printed, with the correlation of the
  ray-cast model's object share against the index pass;
- a piece planned inside a searched camera's frustum may be missing from the
  index pass only when the ray-cast model also sees none of it (hidden
  behind another piece; listed).
"""
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("RENDER_TEST_PROJECTS", "synthetic-01 synthetic-03").split() if p]
MAX_SECONDS_PER_VIEW = 240.0
WHITE_WALL_MAX_RB = 1.10
BLOCKED_SINGLE = 0.55        # one element over this share of the frame (index pass)
BLOCKED_NEAR = 0.35          # over this share of the pixels nearer than NEAR_MM (depth pass)
NEAR_MM = 900
LOW_OBJECT_SHARE = 0.10
MODEL_HIDDEN_SHARE = 0.005   # a piece the ray-cast model sees on less than this share (192 x 108 rays) is hidden


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


def _policy(camera: dict) -> str:
    return camera.get("policy") or "m5"


def _building(name: str, scene: dict) -> dict:
    from wenart import views

    path = views._resolve_repo_path(scene.get("building"), OUTPUTS / name)
    if path is None or not path.is_file():
        path = OUTPUTS / name / "building_final.json"
    assert path.is_file(), f"{name}: building JSON of the scene not found ({scene.get('building')})"
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_room_has_three_views(project):
    """By camera policy (docs/milestone6.md §4.2; the M5 name is kept, tests/test_blender_render.py calls it):
    ``m5`` three views per room, ``search`` 1-3 views per room by the area rule, every room at least one."""
    from wenart.blender import camsearch

    name, scene, render = project
    rendered = {r["camera"] for r in render["renders"]}
    planned = {c["name"] for c in scene["cameras"]}
    assert planned <= rendered, f"{name}: missing renders {sorted(planned - rendered)}"
    by_room: dict = {}
    for c in scene["cameras"]:
        by_room.setdefault(c["room_id"], []).append(c)
    policies = {_policy(c) for c in scene["cameras"]}
    assert len(policies) == 1, f"{name}: cameras of two policies in one scene: {sorted(policies)}"
    if policies == {"m5"}:
        for room in by_room:
            assert {f"cam_{room}_{i}" for i in (1, 2, 3)} <= rendered
        return
    building = _building(name, scene)
    levels = {lv["id"] for lv in scene["levels"]}
    rooms = {r["id"]: r for r in building["rooms"] if r["level_id"] in levels}
    assert set(by_room) == set(rooms), f"{name}: rooms without a view {sorted(set(rooms) - set(by_room))}"
    for room_id, cams in by_room.items():
        n = camsearch.room_view_count(rooms[room_id])
        names = sorted(c["name"] for c in cams)
        assert 1 <= len(cams) <= n, f"{name}: {room_id} has {len(cams)} views, the area rule allows 1..{n}"
        assert names == sorted(f"cam_{room_id}_{i}" for i in range(1, len(cams) + 1)), names


def _blocked(render_entry: dict, out: Path) -> dict:
    """Index/depth measures of one view: largest element share, near share, object share."""
    from wenart import views

    W, H = render_entry["resolution"]
    total = float(W * H)
    shares = {int(k): v["pixels"] / total for k, v in render_entry["index_stats"].items() if int(k) != 0}
    depth = views.read_depth_mm(out / render_entry["files"]["depth_mm"])
    near = float(((depth > 0) & (depth < NEAR_MM)).mean())
    single = max(shares.values(), default=0.0)
    return {"single": single, "near": near, "objects": sum(shares.values()),
            "blocked": single > BLOCKED_SINGLE or near > BLOCKED_NEAR}


def test_no_blocked_searched_view(project):
    from wenart.blender import camsearch

    name, scene, render = project
    plans = {c["name"]: c for c in scene["cameras"]}
    out = OUTPUTS / name / "renders"
    blocked, allowed, low, measured = [], [], [], []
    for r in render["renders"]:
        plan = plans.get(r["camera"])
        if plan is None:
            continue
        m = _blocked(r, out)
        measured.append((r["camera"], m, plan))
        if m["objects"] < LOW_OBJECT_SHARE:
            low.append(r["camera"])
        if not m["blocked"]:
            continue
        item = (r["camera"], round(m["single"], 3), round(m["near"], 3))
        if _policy(plan) == "m5":
            allowed.append(item + ("m5 policy",))
        elif camsearch.BLOCKED_WARNING in (plan.get("warning") or ""):
            allowed.append(item + (camsearch.BLOCKED_WARNING,))
        else:
            blocked.append(item)
    searched = [(cam, m, p) for cam, m, p in measured if _policy(p) == "search"]
    if searched:
        building = _building(name, scene)
        model = np.array([sum(camsearch.model_shares(building, p).values()) for _, _, p in searched])
        real = np.array([m["objects"] for _, m, _ in searched])
        r_text = f"{np.corrcoef(model, real)[0, 1]:.3f}" if len(searched) > 2 and real.std() > 0 and model.std() > 0 \
            else "n/a"
        print(f"{name}: ray-cast model vs index pass, object share r = {r_text} over {len(searched)} views")
    print(f"{name}: {len(low)}/{len(measured)} views with < {LOW_OBJECT_SHARE:.0%} object pixels {low}; "
          f"blocked but allowed: {allowed}")
    assert not blocked, f"{name}: searched views blocked without the '{camsearch.BLOCKED_WARNING}' warning " \
                        f"(camera, largest element share, near share): {blocked}"


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
    missing, hidden = [], []
    building = None
    for r in render["renders"]:
        plan = plans[r["camera"]]
        seen = set(r["index_values"])
        absent = []
        for f in plan["visible_furniture"]:
            # Milestone 4 keys furniture by its id (proxies by proxy:<id>): accept both.
            idx = {table[k] for k in (f, f"proxy:{f}") if k in table}
            if idx and not idx <= seen:
                absent.append(f)
        if absent and _policy(plan) == "search":
            # A searched view looks across the room: a piece whose centre is in the frustum can be
            # hidden behind another one. Allowed only when the ray-cast model sees none of it either.
            from wenart.blender import camsearch

            building = building or _building(name, scene)
            shares = camsearch.model_shares(building, plan)
            hidden.extend((r["camera"], f) for f in absent if shares.get(f, 0.0) < MODEL_HIDDEN_SHARE)
            absent = [f for f in absent if shares.get(f, 0.0) >= MODEL_HIDDEN_SHARE]
        if absent:
            missing.append((r["camera"], sorted(absent)))
    if hidden:
        print(f"{name}: pieces in a searched frustum but hidden by the model too (allowed): {hidden}")
    assert not missing, f"{name}: proxies planned in the frustum but absent from the index pass: {missing}"


# --------------------------------------------------------------------------
# Milestone 5
# --------------------------------------------------------------------------

def test_entries_are_m5_renders_with_helper_maps(project):
    from wenart.blender import schemas

    name, _scene, render = project
    schemas.validate_render_manifest(render)
    out = OUTPUTS / name / "renders"
    missing = []
    for r in render["renders"]:
        for key in ("index", "depth_mm", "normal"):
            if not (out / r["files"][key]).is_file():
                missing.append((r["camera"], r["files"][key]))
    assert not missing, f"{name}: helper maps missing: {missing}"
    assert render["view_transform"] == "AgX" and render["look"] == "None"
    assert not render["hidden"] and not render["plugged"], f"{name}: the normal renders hide nothing"


def test_exposure_recorded_and_within_the_clamp(project):
    name, _scene, render = project
    bad = []
    for r in render["renders"]:
        x = r["exposure"]
        lo, hi = x.get("limits") or (-2.0, 8.0)
        ok = (x["mode"] == "auto" and isinstance(x["ev"], (int, float)) and math.isfinite(x["ev"])
              and lo <= x["ev"] <= hi and abs(x["ev"] * 6 - round(x["ev"] * 6)) < 1e-4
              and x["incident_p50"] is not None and x["incident_p50"] > 0
              and x["at_limit"] == (x["ev_raw"] < lo or x["ev_raw"] > hi))
        wp = x["whitepoint"]
        ok = ok and wp is not None and len(wp) == 3 and min(wp) > 0 and \
            abs(0.2126 * wp[0] + 0.7152 * wp[1] + 0.0722 * wp[2] - 1.0) < 1e-3
        if not ok:
            bad.append((r["camera"], x))
    assert not bad, f"{name}: exposure records out of contract: {bad}"
    at_limit = sorted(r["camera"] for r in render["renders"] if r["exposure"]["at_limit"])
    print(f"{name}: EV range {min(r['exposure']['ev'] for r in render['renders']):+.2f} .. "
          f"{max(r['exposure']['ev'] for r in render['renders']):+.2f}, at the clamp: {at_limit}")


def test_uint16_index_stats_match_the_index_maps(project):
    from wenart import views

    name, _scene, render = project
    out = OUTPUTS / name / "renders"
    bad = []
    for r in render["renders"]:
        stats = {int(k): v for k, v in r["index_stats"].items()}
        index = views.read_index(out / r["files"]["index"])
        if sorted(stats) != r["index_values"] or views.compute_index_stats(index) != stats:
            bad.append(r["camera"])
        elif index.shape != (r["resolution"][1], r["resolution"][0]):
            bad.append(r["camera"])
    assert not bad, f"{name}: index_stats disagree with index_values or the uint16 map: {bad}"


def test_white_plaster_walls_are_neutral(project):
    """synthetic-01 (white plaster walls): display R/B of the wall pixels <= 1.10."""
    from wenart import views

    name, scene, render = project
    if name != "synthetic-01":
        pytest.skip("the white-wall check is for synthetic-01")
    assert scene["style_profile"]["walls"]["material"] == "plaster_white"
    wet = {o["wenart_id"] for o in scene["objects"] if o["kind"] == "floor" and o.get("wet")}
    table = views.index_table(scene)
    loaded = views.load_views(OUTPUTS / name / "renders")
    total = np.zeros(3)
    per_view = {}
    for cam, v in loaded.items():
        if v.room_id in wet:
            continue  # tiled walls
        regions = views.regions(v.read_index(), v.read_depth_mm(), v.read_normal(), table)
        mask = regions.masks.get(views.STRUCT_WALLS)
        if mask is None or mask.sum() < 0.01 * mask.size:
            continue
        rgb = v.read_rgb()[mask].astype(np.float64)
        total += rgb.sum(axis=0)
        mean = rgb.mean(axis=0)
        per_view[cam] = round(float(mean[0] / max(mean[2], 1e-6)), 3)
    assert per_view, f"{name}: no view with plaster wall pixels"
    ratio = float(total[0] / max(total[2], 1e-6))
    print(f"{name}: white wall display R/B {ratio:.3f} over {len(per_view)} views; per view {per_view}")
    assert ratio <= WHITE_WALL_MAX_RB, f"{name}: white walls render warm (R/B {ratio:.3f}); per view {per_view}"
