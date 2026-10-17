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

Milestone 10 (docs/milestone10.md §1.6b row 10, §3.2, §3.3; fixed after pod F1,
9 Oct 2026; CPU replays in tests/test_render_gpu_logic_m10.py):

- the interior views are counted for the rooms the variant renders
  (``views.views_for`` of the ``id`` of the scene manifest's ``variant``
  record, the object ``build.variant_summary`` writes; its stored ``views``
  must name the same rooms); the exterior views are tests/gpu/test_m10.py's;
- depth: every view is checked and every bad one listed in one failure. An
  exterior view: 0.1 m < min < max < the exterior clip end
  (``exterior.CLIP_END``, 3000 m) and over 0.25 of the pixels hit (the sky
  fills the rest by design); an interior view of a room open to the sky (a
  roof terrace: ``roof.openings[].room_id``) keeps the interior depth range
  and has no coverage bound; every other view keeps 0.1 m < min < max < 60 m
  and coverage over 0.9;
- index pass: a library piece (``asset.method`` library) the model sees only
  at the outer edge of its fitted box (``asset.bbox_m``: the mesh lies inside
  it and fills it only at some heights) may be absent: its model share falls
  under ``MODEL_HIDDEN_SHARE`` once the box shrinks by ``LIBRARY_BOX_SLACK_M``
  per side, and the scene manifest's ``box3d`` of the built mesh has the
  footprint centre and the fitted width and depth (± ``BOX3D_TOLERANCE_M``).
  Listed as "library box edge only"; parametric pieces and proxies, which fill
  their boxes, keep the strict rule.

Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8; render code m13.2): every view keeps the project
white point or mixes it with the rig by its rig share (real04's anchor stays P3's 5,635 K within 250 K); the walls of
rig-lit views have a display R/B of at most 1.5; open-air views render under the exterior world with no black sky;
the sky pulls meet their targets and the pulled panes sit under the AgX shoulder; rooms whose rig adds to the fill
light are not dark, and at most a quarter of the hall / stair views pass the +3 cap.

Fix round part 2 (17 Oct 2026; CPU replays in tests/test_m13_light.py): the views under the exterior sky keep the
project white point exactly (no rig share), the rooms whose rig replaces the fill light are corrected toward the rig
(a share stuck at 0 fails); the open-air views carry the exterior clip end and no dark band of below-horizon sky
(rays under the horizon that hit nothing, darker than half the sky); the shaded-facade exteriors of real04 / real02
(``SKY_PULLED_VIEWS``) are pulled, and some view is pulled whenever a sky is over the shoulder with a qualifying k;
the windowless bedrooms of ``FILL_LIGHT_ROOMS`` keep their fill light next to their bedside rig.

Fix round part 3 (17 Oct 2026; CPU replays in tests/test_m13_light.py): a pulled sky keeps the saturation floor
within ``SKY_PULL_SAT_ALLOWANCE`` and its mask is coherent (``full_weight_share`` at least
``SKY_MASK_FULL_WEIGHT_MIN``): the haze shell no longer leaves a random half of the sky out of the mask.
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
# Milestone 10 (pod F1): a library mesh lies inside its fitted box (asset.bbox_m) and fills it only at some heights
# (cornice, plinth, feet, rounded corners); the model draws the whole box.
LIBRARY_BOX_SLACK_M = 0.02   # per side: the box the model must still see a library piece in when it is absent
BOX3D_TOLERANCE_M = 0.01     # the built mesh's box3d against the footprint centre and the fitted width and depth
MIN_DEPTH_M = 0.1            # every view: nearest surface (interior clip start 0.05 m, exterior 0.1 m)
MAX_INDOOR_DEPTH_M = 60.0    # interior views: farthest surface
MIN_COVERAGE = 0.9           # interior views: share of the pixels that hit a surface
EXTERIOR_MIN_COVERAGE = 0.25  # exterior views: the sky fills the rest by design (pod F1 real02: 0.646-0.864)
MAX_PREVIEW_BYTES = 300_000


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
    # Milestone 11/12: a camera the agent moved or added (set_camera / add_camera) carries the policy "agent"; the
    # scene's own policy is that of the others (pod P5: real03 had 76 searched views and one moved by the agent)
    policies = {_policy(c) for c in interior if _policy(c) != "agent"} or {"search"}
    assert len(policies) == 1, f"{name}: cameras of two policies in one scene: {sorted(policies)}"
    if policies == {"m5"}:
        for room in by_room:
            assert {f"cam_{room}_{i}" for i in (1, 2, 3)} <= rendered
        return
    building = _building(name, scene)
    levels = {lv["id"] for lv in scene["levels"]}
    # Milestone 10 (§1.6b row 10): the rooms this variant renders (no second twin, an alternative's changed rooms).
    # The scene manifest's ``variant`` is the build's variant record (build.variant_summary: id, levels, views, ...);
    # a manifest from before Milestone 10 has none (the base).
    from wenart.views import views_for
    record = scene.get("variant")
    variant = (record.get("id") if isinstance(record, dict) else record) or "base"
    shown = set(views_for(building, variant)["rooms"])
    if isinstance(record, dict) and isinstance(record.get("views"), dict):
        stored = sorted(record["views"].get("rooms") or [])
        assert stored == sorted(shown), \
            f"{name}: the scene's variant {variant} renders the rooms {stored}, views_for gives {sorted(shown)}"
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
        # the planned views (searched, or moved by the agent under their name); a view the agent added is extra
        planned_views = [c for c in cams if _policy(c) != "agent" or c["name"].startswith(f"cam_{room_id}_")]
        names = sorted(c["name"] for c in planned_views)
        assert 1 <= len(planned_views) <= n, \
            f"{name}: {room_id} has {len(planned_views)} views, the view rule allows 1..{n}"
        assert names == sorted(f"cam_{room_id}_{i}" for i in range(1, len(planned_views) + 1)), names


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
        elif _policy(plan) == "agent":
            want = float(plan["lens_mm"])          # the agent's set_camera lens: rendered as planned
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
    # Milestone 12 (pod P7): after an edit the changed rooms' views are rendered again (--cameras); the others keep
    # their files from the earlier build and are listed as such by the render
    carried = set(render.get("carried_from_earlier_build") or [])
    stale = sorted(r["camera"] for r in render["renders"]
                   if r.get("scene_sha256") != fingerprint and r["camera"] not in carried)
    assert not stale, f"{name}: renders of another scene build (re-render them): {stale}"
    assert render["pass_index"] == scene["pass_index"], f"{name}: the two pass index tables differ"


def _open_sky_rooms(building: dict) -> set:
    """Rooms open to the sky: the rooms of the roof's openings (Milestone 10, docs/milestone10.md §3.2: a roof
    terrace has no ceiling, its views see the sky over the parapet)."""
    return {o["room_id"] for o in (building.get("roof") or {}).get("openings") or [] if o.get("room_id")}


def test_passes_exist_and_depth_is_plausible(project):
    """Files and depth range of every view, all bad views listed in one failure. Interior views: MIN_DEPTH_M <
    min < max < MAX_INDOOR_DEPTH_M and coverage over MIN_COVERAGE; Milestone 10: an interior view of a room open
    to the sky has no coverage bound; an exterior view: MIN_DEPTH_M < min < max < ``exterior.CLIP_END`` and
    coverage over EXTERIOR_MIN_COVERAGE (sky by design)."""
    from wenart.blender import exterior

    name, scene, render = project
    out = OUTPUTS / name / "renders"
    plans = {c["name"]: c for c in scene.get("cameras") or []}
    open_sky = None                     # read from the building only when an interior view needs it
    bad, sky = [], []
    for r in render["renders"]:
        cam = r["camera"]
        lost = [r[k] for k in ("png", "exr", "preview") if not (out / r[k]).exists()]
        if lost:
            bad.append((cam, f"missing {lost}"))
        elif (out / r["preview"]).stat().st_size > MAX_PREVIEW_BYTES:
            bad.append((cam, f"preview over {MAX_PREVIEW_BYTES} bytes"))
        depth = r.get("depth")
        if depth is None:
            bad.append((cam, "no depth statistics"))
            continue
        plan = plans.get(cam) or {}
        if plan.get("kind") == "exterior":
            far, coverage = exterior.CLIP_END, EXTERIOR_MIN_COVERAGE
        else:
            far, coverage = MAX_INDOOR_DEPTH_M, MIN_COVERAGE
            if open_sky is None:
                open_sky = _open_sky_rooms(_building(name, scene))
            if (plan.get("room_id") or r.get("room_id")) in open_sky or r.get("open_air"):
                # M11 (pod G2b): a room open to the sky (a roof terrace) sees the ground to the horizon (site
                # HORIZON_M): the exterior clip end applies, and no coverage bound. Fix round part 2 (17 Oct 2026):
                # also every view the render marked open-air (render.open_air: a balcony type without a roof
                # opening), rendered with the exterior clip end (render.view_clip_end).
                far = exterior.CLIP_END
                if not depth["coverage"] > coverage:
                    sky.append((cam, round(depth["coverage"], 3)))
                    coverage = None
        if not MIN_DEPTH_M < depth["min"] < depth["max"] < far:
            bad.append((cam, f"depth not {MIN_DEPTH_M:g} < min < max < {far:g} m", depth))
        if coverage is not None and not depth["coverage"] > coverage:
            bad.append((cam, f"coverage not over {coverage:g}", depth))
    if sky:
        print(f"{name}: views of rooms open to the sky, no coverage bound (camera, coverage): {sky}")
    assert not bad, f"{name}: views with missing files or an implausible depth pass: {bad}"


# Fix round after P3 (16-17 Oct 2026; G_geometry's ask): P3's cam_r_L1_koridor_2_2 looked through the slit between a
# closed door leaf and its frame (no door stops) into the far site: depth past the 60 m interior bound. With the
# stops (shell.door_m6_parts, parametric.door_stop_boxes) the view ends on the door. P3: max 196.3 m, coverage
# 0.99966 (the slit's sky pixels); the other corridor views: coverage 1.0.
CLOSED_DOOR_VIEWS = ("cam_r_L1_koridor_2_2",)
CLOSED_DOOR_MIN_COVERAGE = 0.9999


def test_closed_door_views_end_on_the_door(project):
    name, _scene, render = project
    entries = {r["camera"]: r for r in render["renders"] if r["camera"] in CLOSED_DOOR_VIEWS}
    if not entries:
        pytest.skip(f"{name}: none of {CLOSED_DOOR_VIEWS} rendered")
    for cam, r in entries.items():
        depth = r.get("depth") or {}
        assert depth.get("max") is not None and depth["max"] < MAX_INDOOR_DEPTH_M, (cam, depth)
        assert depth.get("coverage", 0.0) >= CLOSED_DOOR_MIN_COVERAGE, (cam, depth)


def _library_box_edge_only(building: dict, plan: dict, piece_id: str, box3d: dict) -> bool:
    """True when the model sees a library piece only at the outer edge of its fitted box (Milestone 10, pod F1):
    with ``asset.bbox_m`` shrunk by ``LIBRARY_BOX_SLACK_M`` per side (height kept) its model share falls under
    ``MODEL_HIDDEN_SHARE``, and the scene manifest's ``box3d`` of the piece (the built mesh, measured in the piece
    frame) has the footprint centre and the fitted width and depth (± ``BOX3D_TOLERANCE_M``). The mesh then
    stands where the model puts it and reaches its box, so the absence comes from the mesh's shape (a cornice
    wider than the doors), not from where it was placed."""
    from wenart.blender import camsearch

    pieces = building.get("furniture") or []
    piece = next((f for f in pieces if f.get("id") == piece_id), None)
    asset = (piece or {}).get("asset") or {}
    box = box3d.get(piece_id)
    if asset.get("method") != "library" or not asset.get("bbox_m") or not box:
        return False
    width, depth = (float(v) for v in asset["bbox_m"][:2])
    if math.dist([float(v) for v in box["center"][:2]], [float(v) for v in piece["footprint"]["center"][:2]]) \
            > BOX3D_TOLERANCE_M:
        return False
    if abs(float(box["size"][0]) - width) > BOX3D_TOLERANCE_M or abs(float(box["size"][1]) - depth) > BOX3D_TOLERANCE_M:
        return False
    shrunk = [max(width - 2.0 * LIBRARY_BOX_SLACK_M, 0.0), max(depth - 2.0 * LIBRARY_BOX_SLACK_M, 0.0)]
    smaller = dict(piece, asset=dict(asset, bbox_m=shrunk + list(asset["bbox_m"][2:])))
    model = dict(building, furniture=[smaller if f is piece else f for f in pieces])
    return camsearch.model_shares(model, plan).get(piece_id, 0.0) < MODEL_HIDDEN_SHARE


def test_index_pass_contains_every_visible_proxy(project):
    name, scene, render = project
    table = scene["pass_index"]
    plans = {c["name"]: c for c in scene["cameras"]}
    box3d = {o["wenart_id"]: o.get("box3d") for o in scene.get("objects") or [] if o.get("kind") == "furniture"}
    missing, hidden, edge = [], [], []
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
            # Milestone 10: a library mesh is smaller than its fitted box; seen only at the box's edge it may be
            # outside the frame (the box3d guard keeps a misplaced or mis-scaled mesh a failure).
            edge_only = [f for f in absent if _library_box_edge_only(building, plan, f, box3d)]
            edge.extend((r["camera"], f, round(shares[f], 4)) for f in edge_only)
            absent = [f for f in absent if f not in edge_only]
        if absent:
            missing.append((r["camera"], sorted(absent)))
    if hidden:
        print(f"{name}: pieces in a searched frustum but hidden by the model too (allowed): {hidden}")
    if edge:
        print(f"{name}: library box edge only, pieces the model sees only at the edge of their fitted box "
              f"(allowed; camera, piece, model share): {edge}")
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


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026, docs/milestone13.md §14.8): the light and colour of the views. P3 (real04)
# rendered 24 of 48 views with an orange cast (the 2700 K rig under the 5,635 K daylight point), the roof terraces
# under the interior HDRI (22-31 % black pixels), the windows as a blank pale plane (pane medians 0.86-0.97), a
# windowless bedroom night-dark and 10 hall views over the +3 cap. These checks read the run's own manifests; a
# project rendered before the fix (render code m13.1) fails them by design.
# --------------------------------------------------------------------------

RIG_ROOM_MAX_RB = 1.5           # wall display R/B of a view lit mostly by the rig (P3: 1.86-4.2 under the anchor)
RIG_DOMINANT_SHARE = 0.8        # wb_rig_share from which a view counts as lit by the rig
NEAR_BLACK = 8                  # display value under which a pixel is black (every channel)
OPEN_AIR_MAX_BLACK = 0.02       # black share of an open-air view's sky pixels (P3: 22-31 % of the whole frame)
P3_REAL04_WB_K = 5635.0         # P3's real04 project white point (cam_r_L1_teras_1, daylight only, interior world)
P3_WB_TOLERANCE_K = 250.0
PANE_MEDIAN_MAX = 0.85          # pulled panes at or under the AgX shoulder
PANE_PULLED_SHARE = 0.8         # ... in at least this share of the interior views with a pull
HALL_DARK_MAX_SHARE = 0.25      # hall / stair views still over the +3 cap (P3: 10 of 13 after the agent's x3)
# Fix round part 2 (17 Oct 2026)
RIG_ONLY_MEDIAN_SHARE = 0.5     # median rig share of the views of rooms whose rig replaces the fill light (no
#                                 daylight window, a ceiling fixture; shim: real02 hall 0.78, synthetic-01 bath 0.82)
OPEN_AIR_BAND_MAX = 0.002       # share of the frame: rays under the horizon that hit nothing and are darker than ...
OPEN_AIR_BAND_SKY_RATIO = 0.5   # ... this share of the sky's median luminance (P3's terraces with the 200 m clip:
#                                 the ground ended 1.3 degrees under the horizon, about 19 rows of 1080 = 1.8 %)
HORIZON_MARGIN_PX = 2.0         # rays this close to the horizon (in pixels at the frame centre) count as on it
# The shaded-facade exteriors whose sky must be pulled: P3's real04 ext_2 / ext_4 (sky median 0.84 / 0.81, saturation
# 0.06-0.13 at the facade EV); real02's ext_2 was pulled k 2 in the part-1 shim run (240 x 135, median 0.84 -> 0.77).
SKY_PULLED_VIEWS = {"real04": ("ext_2", "ext_4"), "real02": ("ext_2",)}
# Fix round part 3 (17 Oct 2026): the blended sky of a pulled view keeps the saturation floor (render.SKY_PULL_SAT_MIN)
# within this allowance (the 3 px feather keeps part of the rendered sky along the silhouettes and the hill line; shim,
# real02 at 480 x 270, 128 spp: terrace chosen save 0.1481 -> blended 0.1463, ext_2 0.1285 -> 0.1279; eb80db2 blended
# them at a third of the pull on a speckled mask: 0.057 and 0.079) ...
SKY_PULL_SAT_ALLOWANCE = 0.02
# ... and its sky mask is coherent: at least this share of the mask at full feather weight (render.full_weight_share;
# the same shim run: 0.961 / 0.957; eb80db2's mask with the haze shell left out at random: 0.000 / 0.000)
SKY_MASK_FULL_WEIGHT_MIN = 0.8
# The windowless bedrooms whose bedside rig adds to the fill light (the verifier's list of the fix round; P3:
# r_L0_yatak_odasi_4 night-dark at +6.1..+6.5 EV). True: the room must be in the scene (level L0 is always built);
# False: checked where its level is built (L-1b).
FILL_LIGHT_ROOMS = {"real04": {"r_L0_yatak_odasi_3": True, "r_L0_yatak_odasi_4": True, "r_L-1b_oda": False,
                               "r_L-1b_oda_2": False},
                    "real02": {"r_L0_yatak_odasi_3": True, "r_L0_yatak_odasi_4": True}}


def _project_wb(render: dict) -> bool:
    return render.get("white_balance_mode") == "project" and bool((render.get("white_balance_project") or {})
                                                                  .get("whitepoint"))


def test_views_keep_the_project_white_point_or_mix_it_with_the_rig(project):
    """Every view's white point is the project anchor, or the anchor mixed with the rig's colour by the view's rig
    share (``render.mixed_whitepoint``); real04's anchor stays P3's (the terraces are still metered under the
    interior world). Fix round part 2 (17 Oct 2026): the rule alone only checks the code against itself, so two pins
    that do not read the view's own share: every view under the exterior sky (the exterior views and the open-air
    rooms: daylight only) keeps the anchor exactly with no rig share, and the views of the rooms whose rig replaces
    the fill light (no daylight window, a ceiling fixture: ``lighting.rig.rooms``) are corrected toward the rig (each
    share over ``render.WB_RIG_SHARE_MIN``, their median at least ``RIG_ONLY_MEDIAN_SHARE``)."""
    from wenart.blender import render as R

    name, scene, render = project
    if not _project_wb(render):
        pytest.skip(f"{name}: not rendered with --white-balance project")
    anchor = [float(v) for v in render["white_balance_project"]["whitepoint"]]
    residual = render["white_balance_project"].get("residual") or 0.0
    exterior_world = (((scene.get("lighting") or {}).get("world_exterior") or {}).get("name"))
    rig_rooms = {rid for rid, rec in ((((scene.get("lighting") or {}).get("rig") or {}).get("rooms")) or {}).items()
                 if rec.get("replaces_fill_light")}
    bad, rig_only = [], []
    for r in render["renders"]:
        x = r["exposure"]
        if x.get("wb_project_whitepoint") is None:
            bad.append((r["camera"], "no wb_project_whitepoint (rendered before the fix round?)"))
            continue
        if max(abs(a - b) for a, b in zip(x["wb_project_whitepoint"], anchor)) > 1e-6:
            bad.append((r["camera"], "another anchor", x["wb_project_whitepoint"]))
        share = x.get("wb_rig_share")
        want = anchor if share is None or share < R.WB_RIG_SHARE_MIN else \
            R.mixed_whitepoint(anchor, x["wb_rig_whitepoint"], share, residual)
        if max(abs(a - b) for a, b in zip(x["whitepoint"], want)) > 1e-5:
            bad.append((r["camera"], share, x["whitepoint"], want))
        if r.get("room_id") is None or (exterior_world and r.get("world") == exterior_world):
            # daylight only: the project white point itself, no rig share metered
            if share is not None or max(abs(a - b) for a, b in zip(x["whitepoint"], anchor)) > 1e-6 \
                    or abs(x.get("wb_view_shift_mired") or 0.0) > 0.5:
                bad.append((r["camera"], "a view under the exterior sky off the project white point", share,
                            x["whitepoint"], x.get("wb_view_shift_mired")))
        elif r.get("room_id") in rig_rooms:
            rig_only.append((r["camera"], share))
            if share is None or share <= R.WB_RIG_SHARE_MIN:
                bad.append((r["camera"], "a room lit by its rig alone kept the daylight white point", share))
    shares = sorted(s for _c, s in rig_only if s is not None)
    if shares and shares[len(shares) // 2] < RIG_ONLY_MEDIAN_SHARE:
        bad.append(("rig-only rooms", f"median rig share {shares[len(shares) // 2]} under {RIG_ONLY_MEDIAN_SHARE}",
                    rig_only))
    assert not bad, f"{name}: white points off the rule: {bad}"
    if name == "real04":
        kelvin = render["white_balance_project"].get("kelvin")
        assert kelvin is not None and abs(kelvin - P3_REAL04_WB_K) <= P3_WB_TOLERANCE_K, \
            f"real04: the project white point moved from P3's {P3_REAL04_WB_K} K to {kelvin} K"
    print(f"{name}: rig shares " + ", ".join(f"{r['camera']}={r['exposure'].get('wb_rig_share')}"
                                             for r in render["renders"]))


def test_rig_lit_rooms_have_no_orange_cast(project):
    """The walls of a view lit mostly by the rig (``wb_rig_share`` >= 0.8) and metered within the cap have a display
    R/B of at most 1.5 (``views.regions`` walls, as ``test_white_plaster_walls_are_neutral``; P3: 1.86-4.2)."""
    from wenart import views

    name, scene, render = project
    if not _project_wb(render):
        pytest.skip(f"{name}: not rendered with --white-balance project")
    entries = {r["camera"]: r for r in render["renders"]}
    rig_lit = [c for c, r in entries.items() if (r["exposure"].get("wb_rig_share") or 0.0) >= RIG_DOMINANT_SHARE
               and not r["exposure"].get("lighting_dark")]
    if not rig_lit:
        pytest.skip(f"{name}: no view lit mostly by the rig within the cap")
    table = views.index_table(scene)
    loaded = views.load_views(OUTPUTS / name / "renders", cameras=rig_lit)
    per_view, warm = {}, []
    for cam, v in loaded.items():
        mask = views.regions(v.read_index(), v.read_depth_mm(), v.read_normal(), table).masks.get(views.STRUCT_WALLS)
        if mask is None or mask.sum() < 0.01 * mask.size:
            continue
        mean = v.read_rgb()[mask].astype(np.float64).mean(axis=0)
        per_view[cam] = round(float(mean[0] / max(mean[2], 1e-6)), 3)
        if per_view[cam] > RIG_ROOM_MAX_RB:
            warm.append((cam, per_view[cam], entries[cam]["exposure"].get("wb_rig_share")))
    print(f"{name}: wall R/B of the rig-lit views {per_view}")
    assert not warm, f"{name}: rig-lit views still orange (wall R/B > {RIG_ROOM_MAX_RB}): {warm}"


def _euler_xyz(deg) -> np.ndarray:
    """Blender's XYZ Euler rotation matrix (Rz @ Ry @ Rx) from degrees."""
    x, y, z = (math.radians(float(v)) for v in deg)
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return rz @ ry @ rx


def _below_horizon(plan: dict, shape) -> np.ndarray | None:
    """bool H x W: the pixels whose camera ray points under the horizon by more than ``HORIZON_MARGIN_PX`` (fix
    round part 2): the scene manifest's camera plan (position and target, or a replayed record's
    ``rotation_euler_deg``; lens, sensor and lens shift by the §1.3 projection of ``camsearch.ray_grid``) at the
    rendered size. None without a pose or a lens."""
    from wenart.blender import camsearch

    h, w = int(shape[0]), int(shape[1])
    lens, sensor = plan.get("lens_mm"), float(plan.get("sensor_mm") or 36.0)
    if not lens or plan.get("position") is None:
        return None
    a, b = camsearch.ray_grid((w, h), float(lens), sensor, (w, h), float(plan.get("shift_x") or 0.0),
                              float(plan.get("shift_y") or 0.0))
    if plan.get("target") is not None:
        d = camsearch.camera_directions(plan["position"], plan["target"], a, b)
    elif plan.get("rotation_euler_deg") is not None:
        d = np.stack([a, b, -np.ones_like(a)], axis=1) @ _euler_xyz(plan["rotation_euler_deg"]).T
    else:
        return None
    sin_elevation = d[:, 2] / np.linalg.norm(d, axis=1)
    margin = math.sin(HORIZON_MARGIN_PX * sensor / float(lens) / w)
    return (sin_elevation < -margin).reshape(h, w)


def test_open_air_views_render_under_the_exterior_sky(project):
    """A camera of an open-air room (``render.open_air``: real02 / real04's terraces) renders under the exterior
    world when the scene has one, its sun lamp follows the exterior rule, and its sky has no black pixels. Fix round
    part 2 (17 Oct 2026): it renders with the exterior clip end (the entry's ``clip``, ``render.view_clip_end``), and
    there is no dark band under the horizon: the rays that point under the horizon (``_below_horizon``) and hit
    nothing (no normal) show the sky's colour under the horizon (0.004-0.023 against 20-80 above it, bpy 5.2.2);
    those darker than ``OPEN_AIR_BAND_SKY_RATIO`` of the sky's median luminance stay under ``OPEN_AIR_BAND_MAX`` of
    the frame (with the 200 m clip: about 19 rows of 1080 under the horizon of every terrace view)."""
    from wenart import views
    from wenart.blender import exterior
    from wenart.blender import render as R

    name, scene, render = project
    exterior_world = ((scene.get("lighting") or {}).get("world_exterior") or {})
    types = R.room_types_from_manifest(scene)
    open_air = [r for r in render["renders"] if R.open_air(types.get(r.get("room_id") or ""))]
    if not open_air:
        pytest.skip(f"{name}: no view of an open-air room")
    plans = {c["name"]: c for c in scene.get("cameras") or []}
    bad, black, band = [], {}, {}
    for r in open_air:
        if not r.get("open_air"):
            bad.append((r["camera"], "entry without open_air (rendered before the fix round?)"))
        if exterior_world and r.get("world") != exterior_world.get("name"):
            bad.append((r["camera"], f"rendered under {r.get('world')}, not the exterior world "
                                     f"{exterior_world.get('name')}"))
        clip = r.get("clip") or {}
        if exterior_world and not (clip.get("end_m", 0.0) >= exterior.CLIP_END and clip.get("rule")):
            bad.append((r["camera"], f"not rendered with the exterior clip end {exterior.CLIP_END:g} m", clip))
    if exterior_world:
        loaded = views.load_views(OUTPUTS / name / "renders", cameras=[r["camera"] for r in open_air])
        for cam, v in loaded.items():
            rgb = v.read_rgb()
            sky = v.read_depth_mm() == 0                     # no surface within 65 m: the sky and the far ground
            sky[sky.shape[0] // 2:, :] = False                # the upper half: the sky
            if sky.sum() >= 0.01 * sky.size:
                black[cam] = round(float((rgb[sky] < NEAR_BLACK).all(axis=-1).mean()), 4)
                if black[cam] > OPEN_AIR_MAX_BLACK:
                    bad.append((cam, f"{black[cam]:.1%} black sky pixels"))
            below = _below_horizon(plans.get(cam) or {}, rgb.shape[:2])
            if below is None:
                bad.append((cam, "no camera pose in the scene manifest: the horizon band is not checked"))
                continue
            no_hit = ~views.normal_hit(v.read_normal())
            lum = rgb[..., :3].astype(np.float64) @ np.array([0.2126, 0.7152, 0.0722]) / 255.0
            above = no_hit & ~below
            floor = OPEN_AIR_BAND_SKY_RATIO * float(np.median(lum[above])) if above.any() else 1.0
            band[cam] = round(float((no_hit & below & (lum < floor)).mean()), 5)
            if band[cam] > OPEN_AIR_BAND_MAX:
                bad.append((cam, f"{band[cam]:.2%} of the frame: rays under the horizon hit nothing and are dark "
                                 f"(the band of below-horizon sky)"))
    print(f"{name}: open-air views {[r['camera'] for r in open_air]}, black sky share {black}, dark band {band}")
    assert not bad, f"{name}: open-air views: {bad}"


def test_sky_and_window_pulls_reach_their_targets(project):
    """Every view under the exterior sky carries a ``sky_pull`` record, and a chosen sky pull's save reads as sky
    (median under the shoulder, saturation over the floor) and darkens and saturates the blended sky; the pulled
    panes of the interior views are at or under the AgX shoulder in at least 80 % of them (P3: pane medians
    0.86-0.97 after k 1-2). Fix round part 2 (17 Oct 2026): the shaded-facade views of ``SKY_PULLED_VIEWS`` are
    pulled, and some view is pulled whenever a sky over the shoulder has a qualifying k (a pull that never fires
    passed the per-pull checks). Fix round part 3 (17 Oct 2026): the blended sky keeps the saturation floor within
    ``SKY_PULL_SAT_ALLOWANCE``, and a pulled sky's mask is coherent (``full_weight_share`` at least
    ``SKY_MASK_FULL_WEIGHT_MIN``): eb80db2's depth-only mask left the haze shell out on a random half of the sky, every
    pixel got a third of the pull, and the speckled skies passed (real02 shim, 128 spp: terrace 0.034 -> 0.057, ext_2
    0.059 -> 0.079)."""
    from wenart.blender import render as R

    name, scene, render = project
    exterior_world = ((scene.get("lighting") or {}).get("world_exterior") or {})
    bad, skies = [], {}
    entries = {r["camera"]: r for r in render["renders"]}
    if exterior_world:
        # fix round part 2 (17 Oct 2026): the checks below only judge the pulls that happened; a sky pull that never
        # fires must fail too. The named shaded-facade views are pulled (k >= 1, the blended sky under the shoulder,
        # more saturated than rendered and, fix round part 3, at the floor within SKY_PULL_SAT_ALLOWANCE: part 2 let
        # the blended sky off the floor and blamed the feather at the silhouettes; the low blended saturation of its
        # shim run (chosen save 0.129, blended 0.081) came from the speckled mask, every sky pixel at a third of the
        # pull), and whenever a view's sky is over the shoulder and one of its tried k qualifies, some view is pulled.
        for cam in SKY_PULLED_VIEWS.get(name, ()):
            s = (entries.get(cam) or {}).get("sky_pull") if cam in entries else "absent"
            if s == "absent":
                continue
            if not s or not s.get("k") or s["median_after"] > R.SKY_PULL_MEDIAN_MAX \
                    or not s["saturation_after"] > s["saturation_before"] \
                    or s["saturation_after"] < R.SKY_PULL_SAT_MIN - SKY_PULL_SAT_ALLOWANCE:
                bad.append((cam, "a shaded-facade view whose sky was not pulled to its target", s))
        over = [r["camera"] for r in render["renders"] if (r.get("sky_pull") or {}).get("median_before", 0.0)
                > R.SKY_PULL_MEDIAN_MAX and any(R.sky_pull_qualifies(c) for c in r["sky_pull"].get("tried") or [])]
        if over and not any((r.get("sky_pull") or {}).get("k") for r in render["renders"]):
            bad.append(("sky pull", "skies over the shoulder with a qualifying k, and no view pulled", over))
    for r in render["renders"]:
        if exterior_world and (r.get("room_id") is None or r.get("open_air")):
            if "sky_pull" not in r:
                bad.append((r["camera"], "no sky_pull record"))
            elif r["sky_pull"] and r["sky_pull"]["k"]:
                # the chosen save meets the targets; the blended sky is bluer and darker than the rendered one and
                # keeps the floor within the feather's allowance (fix round part 3: on a coherent mask the 3 px
                # feather costs about 0.002 of saturation, shim 128 spp); its mask is coherent (most of it at full
                # feather weight: a mask that misses the haze shell on a random half of the sky has none)
                s = r["sky_pull"]
                chosen = next((c for c in s.get("tried") or [] if c["k"] == s["k"]), None)
                skies[r["camera"]] = (s["k"], s["median_after"], s["saturation_after"], s.get("full_weight_share"))
                if chosen is None or not R.sky_pull_qualifies(chosen) or s["median_after"] > s["median_before"] \
                        or s["saturation_after"] < s["saturation_before"]:
                    bad.append((r["camera"], "sky pull off its targets", s))
                if s["saturation_after"] < R.SKY_PULL_SAT_MIN - SKY_PULL_SAT_ALLOWANCE:
                    bad.append((r["camera"], f"blended sky saturation {s['saturation_after']} under the floor "
                                             f"{R.SKY_PULL_SAT_MIN:g} - {SKY_PULL_SAT_ALLOWANCE:g}", s))
                full = s.get("full_weight_share")
                if full is None:
                    bad.append((r["camera"], "sky pull without full_weight_share (rendered before fix round part 3?)"))
                elif full < SKY_MASK_FULL_WEIGHT_MIN:
                    bad.append((r["camera"], f"speckled sky mask: {full:.1%} of it at full feather weight (minimum "
                                             f"{SKY_MASK_FULL_WEIGHT_MIN:.0%})", s))
    pulled = [(r["camera"], r["window_pull"].get("pane_median_after")) for r in render["renders"]
              if r.get("room_id") is not None and not r.get("open_air") and (r.get("window_pull") or {}).get("k")]
    over = [(c, m) for c, m in pulled if m is None or m > PANE_MEDIAN_MAX]
    print(f"{name}: sky pulls {skies}; pulled panes {len(pulled)}, over {PANE_MEDIAN_MAX}: {over}")
    if pulled and (len(pulled) - len(over)) / len(pulled) < PANE_PULLED_SHARE:
        bad.append(("window pull", f"{len(over)} of {len(pulled)} pulled views keep pane medians over "
                                   f"{PANE_MEDIAN_MAX}", over))
    assert not bad, f"{name}: {bad}"


def test_rooms_whose_rig_adds_to_the_fill_light_and_the_halls_are_lit(project):
    """A room whose rig has no ceiling fixture keeps the fill light (``lighting.rig_replaces_fill``): none of its
    views is ``lighting_dark`` (P3: r_L0_yatak_odasi_4 +6.1..+6.5 EV wanted). The hall and stair views (bulbs for
    450 lm/m², ``lighting.rig_bulbs``) are over the cap in at most a quarter of them (P3: 10 of 13). Fix round part 2
    (17 Oct 2026): the list of rooms came from the manifest's own ``adds_to_fill_light`` flags, so a build that lost
    the flag passed with nothing to check. The windowless bedrooms of ``FILL_LIGHT_ROOMS`` are named: each has its
    fill light ``light_<room>`` and its rig never replaces it; where the rig built fixtures (bedside lamps) the room
    is flagged ``adds_to_fill_light``, has an assumed entry of kind ``rig_adds_to_fill_light`` and its fixtures' lights
    are in the rig's lights."""
    from wenart.blender import render as R

    name, scene, render = project
    rig = (scene.get("lighting") or {}).get("rig") or {}
    if not rig.get("on"):
        pytest.skip(f"{name}: built without the rig")
    rooms = rig.get("rooms") or {}
    adds = {rid for rid, rec in rooms.items() if rec.get("adds_to_fill_light")}
    types = R.room_types_from_manifest(scene)
    objects = {o.get("name") for o in scene.get("objects") or []}
    assumed = scene.get("assumed") or []
    rig_lights = set(rig.get("lights") or [])
    missing = []
    for room, required in FILL_LIGHT_ROOMS.get(name, {}).items():
        if room not in types:
            if required:
                missing.append((room, "not in the scene"))
            continue
        rec = rooms.get(room) or {}
        if f"light_{room}" not in objects:
            missing.append((room, "no fill light light_<room>", rec))
        if rec.get("replaces_fill_light"):
            missing.append((room, "its rig replaces the fill light", rec))
        if rec.get("fixtures"):
            if room not in adds:
                missing.append((room, "rig fixtures without adds_to_fill_light", rec))
            if not any(a.get("kind") == "rig_adds_to_fill_light" and a.get("parent") == room for a in assumed):
                missing.append((room, "no assumed entry of kind rig_adds_to_fill_light"))
            lost = [f for f in rec["fixtures"] if f"{f}_light" not in rig_lights]
            if lost:
                missing.append((room, "rig fixtures without their lights", lost))
    assert not missing, f"{name}: windowless bedrooms without the fill light next to their rig: {missing}"
    dark = [(r["camera"], r["exposure"]["ev_raw"]) for r in render["renders"]
            if r.get("room_id") in adds | set(FILL_LIGHT_ROOMS.get(name, {})) and r["exposure"].get("lighting_dark")]
    halls = [r for r in render["renders"] if types.get(r.get("room_id") or "") in ("hall", "stair")]
    dark_halls = [(r["camera"], r["exposure"]["ev_raw"]) for r in halls if r["exposure"].get("lighting_dark")]
    print(f"{name}: rooms whose rig adds to the fill light {sorted(adds)}; hall views {len(halls)}, over the cap "
          f"{dark_halls}")
    assert not dark, f"{name}: rooms with the fill light back are still dark: {dark}"
    assert not halls or len(dark_halls) / len(halls) <= HALL_DARK_MAX_SHARE, \
        f"{name}: {len(dark_halls)} of {len(halls)} hall / stair views over the cap: {dark_halls}"
