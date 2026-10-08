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
  with plaster walls have a display R/B of at most 1.12 (1.10 until
  Milestone 8: the AgX Punchy warmth was accepted by the user on 4 Oct 2026).

Milestone 6 (docs/milestone6.md §4.2), cameras by policy (a scene-manifest
camera without ``policy`` is an M5 camera):

- policy ``m5``: three views per room; policy ``search``: 1-3 views per room
  by the area rule (``camsearch.room_view_count``; Milestone 7: a room with
  nothing to show at most one view, none below 2.5 m2, listed in the scene
  manifest's ``rooms_without_view``) and every other room of the
  building at least one;
- no searched view is blocked (index pass: one element over 0.55 of the
  frame, or depth pass: over 0.35 of the pixels nearer than 0.9 m, at 24 mm) unless its
  plan carries the warning ``blocked unavoidable`` (listed); the share of
  views with under 10 % object pixels is printed, with the correlation of the
  ray-cast model's object share against the index pass;
- a piece planned inside a searched camera's frustum may be missing from the
  index pass only when the ray-cast model also sees none of it (hidden
  behind another piece; listed).

Milestone 8 (docs/milestone8.md §5): every view is rendered with its plan's
lens (searched: 18 mm, 16 mm in rooms narrower than 2.2 m, or the brief's
lens; m5: 24 mm) and the render entry records it; the near distance of the
blocked rule is 0.9 m x lens / 24 (camsearch.near_distance: 0.675 m at 18 mm,
0.6 m at 16 mm).
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
# AgX Punchy warmth accepted by the user, 4 Oct 2026 (docs/milestone8.md decision 5); pod B measured 1.104.
WHITE_WALL_MAX_RB = 1.12
BLOCKED_SINGLE = 0.55        # one element over this share of the frame (index pass)
BLOCKED_NEAR = 0.35          # over this share of the pixels nearer than the camera's near distance (depth pass)
NEAR_MM = 900                # at 24 mm; Milestone 8: times lens / 24 (camsearch.near_distance), 675 mm at 18 mm
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
    ``m5`` three views per room, ``search`` 1-3 views per room by the area rule, every room at least one,
    except (Milestone 7, docs/milestone7.md §6.2) rooms with nothing to show: at most one view, none below
    2.5 m2, and those are listed in the scene manifest's ``rooms_without_view`` with the reason."""
    from wenart.blender import camsearch

    name, scene, render = project
    rendered = {r["camera"] for r in render["renders"]}
    planned = {c["name"] for c in scene["cameras"]}
    assert planned <= rendered, f"{name}: missing renders {sorted(planned - rendered)}"
    by_room: dict = {}
    interior = [c for c in scene["cameras"] if c.get("kind", "interior") != "exterior"]   # M10: no ext_* view
    for c in interior:
        by_room.setdefault(c["room_id"], []).append(c)
    policies = {_policy(c) for c in interior}
    assert len(policies) == 1, f"{name}: cameras of two policies in one scene: {sorted(policies)}"
    if policies == {"m5"}:
        for room in by_room:
            assert {f"cam_{room}_{i}" for i in (1, 2, 3)} <= rendered
        return
    building = _building(name, scene)
    levels = {lv["id"] for lv in scene["levels"]}
    # Milestone 10 (§1.6b row 10): the rooms this variant renders (no second twin, an alternative's changed rooms).
    from wenart.views import views_for
    shown = set(views_for(building, scene.get("variant") or "base")["rooms"])
    rooms = {r["id"]: r for r in building["rooms"] if r["level_id"] in levels and r["id"] in shown}
    listed = {r["room_id"]: r for r in scene.get("rooms_without_view") or [] if r["room_id"] in rooms}
    expected = {r["room_id"] for lv in levels for r in camsearch.rooms_without_view(building, lv)} & set(rooms)
    assert set(listed) == expected, f"{name}: rooms_without_view {sorted(listed)}, the rule gives {sorted(expected)}"
    assert all(r.get("reason") for r in listed.values()), f"{name}: a room without a view has no reason"
    assert set(by_room) == set(rooms) - expected, \
        f"{name}: rooms without a view {sorted(set(rooms) - expected - set(by_room))}, unexpected views " \
        f"{sorted(set(by_room) & expected)}"
    empty = sorted(r for r in by_room if not camsearch.shown_pieces(rooms[r], building))
    print(f"{name}: rooms with nothing to show (one view): {empty}; without a view: {sorted(expected)}")
    for room_id, cams in by_room.items():
        n = camsearch.room_view_count(rooms[room_id], building)
        names = sorted(c["name"] for c in cams)
        assert 1 <= len(cams) <= n, f"{name}: {room_id} has {len(cams)} views, the view rule allows 1..{n}"
        assert names == sorted(f"cam_{room_id}_{i}" for i in range(1, len(cams) + 1)), names


def _blocked(render_entry: dict, out: Path, lens_mm: float = 24.0) -> dict:
    """Index/depth measures of one view: largest element share, near share (nearer than ``NEAR_MM`` x lens / 24,
    the camera search's ``near_distance`` of the view's lens), object share."""
    from wenart import views

    W, H = render_entry["resolution"]
    total = float(W * H)
    shares = {int(k): v["pixels"] / total for k, v in render_entry["index_stats"].items() if int(k) != 0}
    depth = views.read_depth_mm(out / render_entry["files"]["depth_mm"])
    near = float(((depth > 0) & (depth < NEAR_MM * float(lens_mm) / 24.0)).mean())
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
        if plan is None or plan.get("kind") == "exterior":      # M10: a facade fills an exterior view by design
            continue
        m = _blocked(r, out, plan.get("lens_mm") or 24.0)
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


def test_cameras_render_with_their_own_lens(project):
    """Milestone 8 (docs/milestone8.md §5): every render entry records the lens it was rendered with, the lens of
    its scene plan; searched cameras have 18 mm, 16 mm in a room narrower than 2.2 m (``cameras.room_lens``), or
    every one the brief's lens (the scene manifest's ``lens_mm``); m5 cameras keep 24 mm."""
    from wenart.blender import cameras

    name, scene, render = project
    plans = {c["name"]: c for c in scene["cameras"]}
    building = _building(name, scene) if any(_policy(c) == "search" for c in plans.values()) else None
    rooms = {r["id"]: r for r in (building or {}).get("rooms") or []}
    bad, lenses = [], {}
    for r in render["renders"]:
        plan = plans.get(r["camera"])
        if plan is None or plan.get("kind") == "exterior":      # M10: the exterior lens rule is tests/gpu/test_m10.py's
            continue
        if _policy(plan) == "m5":
            want = cameras.M5_LENS_MM
        else:
            want = cameras.room_lens(rooms[plan["room_id"]], scene.get("lens_mm"))[0]
        lenses[want] = lenses.get(want, 0) + 1
        if abs(float(plan["lens_mm"]) - want) > 1e-6 or r.get("lens_mm") is None \
                or abs(float(r["lens_mm"]) - want) > 1e-3 or abs(float(r.get("sensor_mm") or 0) - 36.0) > 1e-3:
            bad.append((r["camera"], plan.get("lens_mm"), r.get("lens_mm"), want))
    print(f"{name}: views per lens (mm) {dict(sorted(lenses.items()))}")
    assert not bad, f"{name}: (camera, plan lens, rendered lens, rule) that disagree: {bad}"


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
    # Milestone 7 (docs/milestone7.md §6.1, user decision 6): the default look is AgX - Punchy.
    assert render["view_transform"] == "AgX" and render["look"] == "AgX - Punchy"
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
    """synthetic-01 (white plaster walls): display R/B of the wall pixels <= WHITE_WALL_MAX_RB (1.12)."""
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
