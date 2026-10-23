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

Fix round after P4a (17 Oct 2026; render code m13.3; CPU replays in tests/test_m13_light.py): every view's white point
is recomputed with the rig part's extra warmth it records (``wb_rig_residual``), so m13.2 manifests no longer pass;
the walls of the rig-lit views are compared with the walls of the same project's daylight views of the same kind
(painted or tiled: ``RIG_ROOM_REL_MAX`` times their median), the fixed ``RIG_ROOM_MAX_RB`` only where the project has
no daylight view of that kind; a pulled sky keeps the floor of the rule its k was chosen by
(``render.sky_pull_floor``) and the views into the sun are listed; the panes of the interior views show the sky
(median pane saturation at least ``PANE_SAT_MIN``; P4a's grey cards 0.00-0.07).

Fix round after P4b (17 Oct 2026; pod P4b, real03; CPU replays in tests/test_m13_light.py):

- the orange check covers the views with a rig share of at least ``RIG_CHECK_SHARE`` (0.4; was 0.8: P4b's mixed
  halls and baths at 0.44-0.65 were not checked) against the project's daylight walls of the same kind plus
  ``RIG_ROOM_ABOVE_DAY`` (the verifier's relative limit; was 1.1 x their median);
- the pane-saturation floor holds only under the clear-sky moods (``PANE_SAT_MOODS``: an overcast, blue-hour or night
  window is grey or dark by design; the review of the P4a fix round);
- a named shaded-facade view passes the sky check when it was pulled to its target or its rendered sky already
  qualifies (``render.sky_pull_qualifies``): the exterior ground cap darkens those views;
- a window pull takes a clip-free k whenever one it tried kept the panes near the walls
  (``test_window_pull_takes_an_unclipped_k_when_one_was_tried``; P4b: 10 views with clipped panes);
- the interior glazing (windows between two rooms, never pulled) of ``INTERIOR_GLAZING_VIEWS`` stays within
  ``INTERIOR_GLAZING_MAX_DELTA`` of the room's walls in display R/B (P4b: 1.82 vs 1.26, 2.15 vs 1.29, 1.02 vs 2.05);
- every exterior view's EV is at most its ground EV plus ``render.EXTERIOR_GROUND_HEADROOM_STOPS`` and its lawn, where
  it fills at least ``LAWN_MIN_SHARE`` of the frame, keeps a saturation of at least ``LAWN_SAT_MIN`` (P4b ext_3 /
  ext_4: about 0.11 / 0.19 on the previews); no horizon-band pin (the haze toward the sun stays white).

Pass before P5 (17 Oct 2026; the review of the fix round after P4b; CPU replays in tests/test_m13_light.py):

- a window pull never takes panes that were unclipped and on target as rendered to or under the wall median
  (``test_window_pull_leaves_panes_that_need_no_pull``, ``render.pull_needed``; the replay of P4a real02
  cam_r_L1_teras_2_2 and P4b real03 yasama_3 / yasama_4_1 with the fix round's rule: k 1 at 0.69-0.84 of the walls);
- every interior-glazing record carries its panes' clip as written; clipped interior panes are pulled to at most
  ``render.PULL_MAX_CLIP`` plus ``PULL_CLIP_FEATHER_ALLOWANCE`` whenever a tried k unclipped them at
  ``render.PULL_WALL_RATIO_MIN`` of the walls, and unclipped ones are not pulled
  (``test_interior_glazing_pull_removes_clipping``; P4b real03 giris_holu_1 / 2 / 3_1: 8-13 % clipped).

Fix round after P5 (22 Oct 2026; pod P5, real04; render code m13.4; CPU replays in tests/test_m13_light.py):

- the orange check sorts the views by the wall finish of their room type (``shell.WET_WALL_ROOM_TYPES``: bathroom and
  wc tiled, every other room painted, a kitchen too: its walls are paint with a 0.6 m splashback) and takes its
  daylight references from unblocked views only (P5: the kitchen mutfak_3, tiled by its wet floor, failed at 1.223
  against the one-view bath reference of the blocked cam_r_L1_banyo_1);
- every interior view's white point is the anchor (or its rig mix) with the tint of its own daylight
  (``render.view_tint_gain`` from the recorded ``wb_day_green``), and the walls of the daylight views are not olive
  (``test_daylight_walls_are_not_olive``: P5's sunlit L0 bedrooms);
- a pulled sky leaves no dotted edge (``test_sky_pull_leaves_no_dotted_edges``: the recorded ``edge_dot_px`` of
  ``render.sky_edge_dots``; P5's ext_1 and teras_2_1 had a dotted white line along every roof and pergola edge).

Fix round after P6a (22 Oct 2026; pod P6a, real04; render code m13.5; CPU replays in tests/test_m13_p6a_render.py):

- a pulled sky's chosen save keeps ``render.SKY_PULL_MEDIAN_MIN`` (``render.sky_pull_candidate_ok``) and the blended
  sky stays within ``SKY_PULL_MEDIAN_ALLOWANCE`` of it (P6a's ext_5: k 6, median 0.109, passed every check);
- the white-point check recomputes each view's tint gain with the rule its record took (``wb_tint_green_residual``;
  m13.4 records, P6a real04 and P6b real03, kept the residual), and a later record says where its green was metered
  (``wb_day_green_source``: the walls since m13.5) and which rule it took;
- the olive check also holds the lower half of the walls to ``DAYLIGHT_LOWER_WALL_GREEN_MIN`` (no pink lower walls
  from a tint that shifts the whole view);
- the index check's ray model gives a library piece seen only as a sliver of its fitted box (at most
  ``LIBRARY_SLIVER_MAX`` of the frame) a slack of ``LIBRARY_BOX_SLACK_SHARE`` per side, fixed equipment excepted (P6a's
  office chair f_L0_041 and oval coffee table f_L1_024: built as fitted, absent from corners of the frame where the
  render shows the desk and the floor);
- the orange and olive checks keep their per-view values in ``CHECK_VALUES_FILE`` (``$WENART_RESULTS`` or the
  project's renders folder), passing or not.

Fix round after P6b (23 Oct 2026; pod P6b, real03 on 8e8cc97; CPU replays in tests/test_m13_p6b_render.py):

- a room the area rule leaves without a view whose views are all replayed from the camera file keeps them
  (``_kept_by_replay``; P4b and P6b real03 failed on the empty halls r_L0_oda_7 and r_L0_oda_10);
- the orange check holds a view lit by the rig alone (``RIG_ALONE_SHARE``) to the daylight median + 0.15 and a mixed
  view to the warmest daylight view of its kind + ``RIG_ROOM_ABOVE_WARMEST_DAY`` (at most ``RIG_ROOM_ABOVE_DAY_MAX``
  over the median): P6b's mixed halls (1.486-1.599) sit inside the daylight views' own spread (1.183-1.582), P4b's
  2700 K views still fail; it keeps the light on the walls of every view it reads (``render.wall_rig_record``, the
  exposure record's ``wb_walls``) with its values, for the next rule (the P6b verifier's step 1: measure first);
- the interior-glazing check keeps its values (``CHECK_VALUES_FILE``); its bound is unchanged.
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
# Fix round after P6a (22 Oct 2026): a library piece the model sees on at most LIBRARY_SLIVER_MAX of the frame with its
# whole fitted box (a sliver of the box in a corner of the frame) gets LIBRARY_BOX_SLACK_SHARE of each side as slack
# (at least LIBRARY_BOX_SLACK_M). P6a real04: the office chair f_L0_041 (its back narrower than its star base; share
# 0.0192, 0.0131 at 2 cm, 0.00125 at 15 %) and the oval glass-top coffee table f_L1_024 (its tips leave the box corners
# empty; 0.0104, 0.0080 at 2 cm, 0.0 at 15 %) were built where the model puts them (box3d within 3 mm) and the renders
# show the desk, the wall and the floor in those corners. A box seen on more of the frame keeps the 2 cm slack (the
# CPU pin's 5 cm wider wardrobe: 0.068), fixed equipment (furniture.schemas.FIXED_TYPES: drawn like walls, its mesh
# fills its footprint) keeps it too (P5's toilet f_L1_013 in cam_r_L1_banyo_1, behind a ceiling light over 55.7 % of
# the frame: share 0.0178, 0.0029 at 15 %, still a failure), and the box3d guard still fails a moved or mis-sized mesh.
LIBRARY_SLIVER_MAX = 0.03
LIBRARY_BOX_SLACK_SHARE = 0.15
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
    # fix round after P6b (23 Oct 2026): a room the rule leaves without a view whose views are all replayed from the
    # camera file is kept (_kept_by_replay; P4b / P6b real03: r_L0_oda_7 and r_L0_oda_10)
    replay_rooms = _replayed_rooms(name, scene)
    kept = _kept_by_replay(expected, by_room, replay_rooms)
    expected -= kept
    if kept:
        print(f"{name}: rooms the rule leaves without a view, kept for their replayed views: {sorted(kept)}")
    assert set(listed) == expected, f"{name}: rooms_without_view {sorted(listed)}, the rule gives {sorted(expected)}"
    assert all(r.get("reason") for r in listed.values()), f"{name}: a room without a view has no reason"
    assert set(by_room) == set(rooms) - expected, \
        f"{name}: rooms without a view {sorted(set(rooms) - expected - set(by_room))}, unexpected views " \
        f"{sorted(set(by_room) & expected)}"
    empty = sorted(r for r in by_room if not camsearch.shown_pieces(rooms[r], building))
    print(f"{name}: rooms with nothing to show (one view): {empty}; without a view: {sorted(expected)}")
    # fix round after P4a (17 Oct 2026): the replayed views of --cameras-from (set 1, docs/milestone13.md §7) keep the
    # baseline's count, bounded by the camera file instead of today's area rule; a hall may count the stair of the
    # next-door stair core it shows (camsearch.STAIR_CORE_REASON: "the hall shows it")
    extra = bool((scene.get("cameras_from") or {}).get("extra"))
    cores = {r["room_id"] for r in listed.values() if r.get("reason") == camsearch.STAIR_CORE_REASON}
    for room_id, cams in by_room.items():
        n = max(camsearch.room_view_count(rooms[room_id], building),
                _view_count_with_stair_cores(rooms[room_id], building, cores))
        # the planned views (searched, or moved by the agent under their name); a view the agent added is extra
        planned_views = [c for c in cams if _policy(c) != "agent" or c["name"].startswith(f"cam_{room_id}_")]
        replayed = [c for c in planned_views if _replayed(c)]
        suffix = ""
        if replayed:
            got = sorted(c["name"] for c in replayed)
            if replay_rooms is not None:
                want = sorted(replay_rooms.get(room_id, ()))
                assert got == want, f"{name}: {room_id} replays {got}, the camera file has {want}"
            searched = [c for c in planned_views if c not in replayed]
            assert extra or not searched, \
                f"{name}: {room_id} has searched views {sorted(c['name'] for c in searched)} next to its replayed " \
                f"ones without --cameras-extra"
            if not searched:
                continue
            planned_views, suffix = searched, "_s"      # --cameras-extra: the searched set of a replayed room
        names = sorted(c["name"] for c in planned_views)
        assert 1 <= len(planned_views) <= n, \
            f"{name}: {room_id} has {len(planned_views)} views, the view rule allows 1..{n}"
        assert names == sorted(f"cam_{room_id}_{i}{suffix}" for i in range(1, len(planned_views) + 1)), names


def _replayed(camera: dict) -> bool:
    """A view replayed from the camera file (``source`` ``replayed``), or the agent's replacement of one
    (``replaced_replayed``)."""
    return camera.get("source") == "replayed" or bool(camera.get("replaced_replayed"))


def _kept_by_replay(expected: set, by_room: dict, replay_rooms) -> set:
    """Fix round after P6b (23 Oct 2026): the rooms of ``expected`` (the area rule leaves them without a view,
    ``camsearch.rooms_without_view``) that have views, all of them replayed (``_replayed``) and named for the room in
    the camera file (``replay_rooms``, ``_replayed_rooms``; None: no room is kept). Why: the replayed views of
    --cameras-from keep the baseline's rooms (docs/milestone13.md §7) and the build leaves such a room out of
    ``rooms_without_view``, but the set equalities used the area rule alone; P4b and P6b real03 failed on the empty
    1.86 / 1.89 m2 halls r_L0_oda_7 and r_L0_oda_10 (one M11 view each). A searched or agent-added view in such a room
    still fails."""
    if replay_rooms is None:
        return set()
    kept = set()
    for room_id in expected:
        cams = by_room.get(room_id) or []
        names = {c["name"] for c in cams}
        if cams and all(_replayed(c) for c in cams) and names <= set(replay_rooms.get(room_id, ())):
            kept.add(room_id)
    return kept


def _replayed_rooms(name: str, scene: dict):
    """Fix round after P4a (17 Oct 2026): ``{room_id: {camera names}}`` of the interior records of the scene's camera
    file (``cameras_from``: ``--cameras-from``) less the records ``cameras_from.dropped`` lists (rooms this build does
    not render, cameras the agent removed), None without a readable file or when its sha256 is not the one the build
    read."""
    import hashlib

    from wenart import views
    from wenart.blender import cameras as CA

    cf = scene.get("cameras_from") or {}
    if not cf.get("path") or cf.get("missing"):
        return None
    path = views._resolve_repo_path(cf["path"], OUTPUTS / name)
    if path is None or not path.is_file():
        return None
    data = path.read_bytes()
    if cf.get("sha256") and hashlib.sha256(data).hexdigest() != cf["sha256"]:
        return None
    gone = {d.get("name") for d in cf.get("dropped") or []}
    out: dict = {}
    for p in CA.replay_cameras(json.loads(data.decode("utf-8")))["plans"]:
        if p.get("kind") != "exterior" and p.get("room_id") and p["name"] not in gone:
            out.setdefault(p["room_id"], set()).add(p["name"])
    return out


def _view_count_with_stair_cores(room: dict, building: dict, cores: set) -> int:
    """Fix round after P4a (17 Oct 2026): the view rule of a hall that shows the stair of a next-door stair core
    (``camsearch.STAIR_CORE_REASON``: "the hall shows it"): ``room_view_count`` with the pieces of the stair cores that
    share an opening with the hall (``cameras.opening_rooms``) counted as the hall's; 0 without such a core. The frustum
    lists of a view hold only its own room's pieces, so the opening is the link (real02: r_L0_koridor and
    r_L0_merdiven share o_L0_001)."""
    from wenart.blender import camsearch
    from wenart.blender import cameras as CA

    if not cores:
        return 0
    near = {r for rooms in CA.opening_rooms(building, room["level_id"]).values() if room["id"] in rooms
            for r in rooms if r in cores}
    ids = {f["id"] for f in building.get("furniture") or [] if f.get("room_id") in near}
    if not ids:
        return 0
    moved = [dict(f, room_id=room["id"]) if f.get("id") in ids else f for f in building["furniture"]]
    return camsearch.room_view_count(room, dict(building, furniture=moved))


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
        plan = plans.get(cam)
        if plan is None:
            # fix round after P4a (17 Oct 2026): a render without a scene camera (P4a: Blender's ext_6.001) is listed;
            # its limits follow the kind of the rendered camera (an exterior view has no room and no level)
            bad.append((cam, "rendered but not in the scene manifest"))
            plan = {"kind": "exterior" if r.get("room_id") is None and r.get("level_id") is None else "interior"}
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


def _library_box_edge_only(building: dict, plan: dict, piece_id: str, box3d: dict, share: float | None = None) -> bool:
    """True when the model sees a library piece only at the outer edge of its fitted box (Milestone 10, pod F1):
    with ``asset.bbox_m`` shrunk by ``LIBRARY_BOX_SLACK_M`` per side (height kept) its model share falls under
    ``MODEL_HIDDEN_SHARE``, and the scene manifest's ``box3d`` of the piece (the built mesh, measured in the piece
    frame) has the footprint centre and the fitted width and depth (± ``BOX3D_TOLERANCE_M``). The mesh then
    stands where the model puts it and reaches its box, so the absence comes from the mesh's shape (a cornice
    wider than the doors), not from where it was placed. Fix round after P6a (22 Oct 2026): when the whole box's model
    ``share`` is at most ``LIBRARY_SLIVER_MAX`` (a sliver of it in the frame) the slack per side is
    ``LIBRARY_BOX_SLACK_SHARE`` of the side (at least ``LIBRARY_BOX_SLACK_M``): a chair back narrower than its base and
    an oval top leave the box's corners empty. Fixed equipment (``furniture.schemas.FIXED_TYPES``) keeps the 2 cm."""
    from wenart.furniture.schemas import FIXED_TYPES
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
    slack_w = slack_d = LIBRARY_BOX_SLACK_M
    if share is not None and share <= LIBRARY_SLIVER_MAX and piece.get("type") not in FIXED_TYPES:
        # fix round after P6a: a sliver of the box of a piece whose shape may leave its corners empty
        slack_w = max(LIBRARY_BOX_SLACK_M, LIBRARY_BOX_SLACK_SHARE * width)
        slack_d = max(LIBRARY_BOX_SLACK_M, LIBRARY_BOX_SLACK_SHARE * depth)
    shrunk = [max(width - 2.0 * slack_w, 0.0), max(depth - 2.0 * slack_d, 0.0)]
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
        plan = plans.get(r["camera"])
        if plan is None:                        # fix round after P4a (17 Oct 2026): P4a's KeyError 'ext_6.001'
            missing.append((r["camera"], ["rendered but not in the scene manifest"]))
            continue
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
            edge_only = [f for f in absent if _library_box_edge_only(building, plan, f, box3d, shares.get(f))]
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

RIG_ROOM_MAX_RB = 1.5           # wall display R/B of a view lit mostly by the rig (P3: 1.86-4.2 under the anchor);
#                                 fix round after P4a: only where the project has no daylight view with such walls
# Fix round after P4a (17 Oct 2026): the rig-lit walls at most this times the median wall R/B of the project's daylight
# views of the same kind. Set before the re-render from a bpy 5.2.2 shim re-render of P4a's real02 scene at P4a's EV
# (480 x 270, 64 spp; its m13.2 hall values match P4a's pod values within 0.04): the painted walls of 10 daylight views
# 1.30-1.55, median 1.36; the 12 halls with m13.2's white point 1.64-1.78 (ratio 1.20-1.30, all over), with m13.3's
# 1.26-1.36 (0.92-1.00); the baths (tiled, no daylight bath: the fixed 1.5) 1.21-1.32 and 1.02-1.08.
RIG_ROOM_REL_MAX = 1.1          # fix round after P4a; replaced by RIG_ROOM_ABOVE_DAY after P4b (kept for the record)
# Fix round after P4b (17 Oct 2026): the orange check covers the views from this rig share (was 0.8, "lit mostly by
# the rig"; P4b's mixed halls and baths at 0.44-0.65 read 1.40-1.69 and were not checked) ...
RIG_CHECK_SHARE = 0.4
# ... at most this much over the median wall R/B of the project's daylight views of the same kind (the verifier's
# relative limit of the P4b analysis; RIG_ROOM_REL_MAX = 1.1 x the median before: the same 1.50-1.51 at real02's 1.36,
# 1.42 against 1.44 at real03's greige 1.29). Its prediction for real03 with the fix-round white point: kat_holu_1
# 1.46, ruzgarlik_1 1.42, giris_holu_3_1 1.49, yangin_merdiveni_1 1.49, oda_7_1 1.29.
RIG_ROOM_ABOVE_DAY = 0.15
# Fix round after P6b (23 Oct 2026; pod P6b, real03, 4000 K hall / stair / bath rig, render code m13.4). The bound
# above holds the views lit by the rig alone (rig share at least RIG_ALONE_SHARE): their white point is the rig lamp's
# colour with the daylight cast. A mixed view (RIG_CHECK_SHARE up to RIG_ALONE_SHARE) may be as warm as the warmest
# daylight view of the same paint plus RIG_ROOM_ABOVE_WARMEST_DAY, at most RIG_ROOM_ABOVE_DAY_MAX over the median (one
# odd daylight view does not lift the bound further; the warmest over the median: P6b 0.277, P5 real04 0.18, the P4a
# real02 shim 0.19). Why: a bpy 5.2.2 shim of P6b's real03.blend (render.py's two metering passes, 240 x 135, 16 spp,
# render.wall_rig_record, 11 views) found the walls' rig share within 0.05 of the frame's (giris_holu_2 0.594 / 0.594,
# giris_holu_1 0.503 / 0.554, yangin_merdiveni_1 0.903 / 0.886) and the warmth in the light itself: on the hall and
# stair walls the daylight arrives at linear R/B 2.65-3.33 and the rig light at 3,266-3,614 K (R/B 3.35-4.28) against
# the anchor's metered daylight (1.98; 1.95 on the walls of its own room) and the 4000 K lamp (2.65), both warmed by the
# oak floors and treads and the greige paint. The daylight-only oda_01_2 gets the same warm light (R/B 3.35) and reads
# 1.582; the halls read 1.49-1.60 at a light R/B of 3.35-4.09. So a mixed view's walls are as warm as the warmest
# daylight room's, not warmer: the rig adds no orange of its own. A view lit by the rig alone keeps the bound since the
# fix round after P4b: P6b's meet it (their white point is the lamp's colour with the daylight cast, and their stair
# and small-hall walls get the least bounce warmth, R/B 3.35-3.37), and it is where a wrong rig colour shows most
# (P4b). Measured, wall display R/B (painted; references: the unblocked daylight views):
#   P6b real03 (m13.4)   daylight 1.183-1.582 (median 1.305); rig alone (0.956-0.985) 1.363-1.442 <= 1.455; mixed
#                        (0.44-0.93) 1.409-1.599 <= 1.632 (10 of them over the old 1.455)
#   P4b real03 (m13.2, 2700 K rig, the same anchor; P4b's daylight walls were not measured, P6b's stand in: the
#                        preview proxy, the mean R/B of the neutral pixels, gives P4b's daylight views a median of 1.21
#                        against P6b's 1.19 and a warmest of 1.28 against 1.37): rig alone (0.975-0.995) 1.562-1.864
#                        > 1.455; mixed (0.83-0.90) 1.648-1.734 > 1.632: all 7 fail as before
#   P4a real02 (m13.2)   halls 1.639-1.808 (0.90-1.0) against the shim's daylight (median 1.36, warmest 1.55): rig alone
#                        > 1.51, mixed > 1.60: all fail
#   P5 real04 (m13.3)    halls 1.306-1.634 (0.71-1.0) against 1.382-1.695 (median 1.515): pass as before
# Every bound is at least the one before (the median + 0.15), so no view that passed before fails now (P6a real04
# passed). The walls' own record (the exposure record's wb_walls) is kept with the values; it does not decide.
RIG_ALONE_SHARE = 0.95
RIG_ROOM_ABOVE_WARMEST_DAY = 0.05
RIG_ROOM_ABOVE_DAY_MAX = 0.35
NEAR_BLACK = 8                  # display value under which a pixel is black (every channel)
OPEN_AIR_MAX_BLACK = 0.02       # black share of an open-air view's sky pixels (P3: 22-31 % of the whole frame)
P3_REAL04_WB_K = 5635.0         # P3's real04 project white point (cam_r_L1_teras_1, daylight only, interior world)
P3_WB_TOLERANCE_K = 250.0
PANE_MEDIAN_MAX = 0.85          # pulled panes at or under the AgX shoulder
PANE_PULLED_SHARE = 0.8         # ... in at least this share of the interior views with a pull
HALL_DARK_MAX_SHARE = 0.25      # hall / stair views still over the +3 cap (P3: 10 of 13 after the agent's x3)
# Fix round after P4a (17 Oct 2026): the median pane saturation of the interior views with a window pull. The shim
# re-render of P4a's real02 scene at P4a's EV: the L0 / L1 windows 0.005 with the haze in the camera's view (P4a's grey
# cards) and 0.14-0.22 without it, the basement windows (light wells, no haze in their view) 0.02-0.17 either way;
# median 0.06 with the haze in view, 0.14 without (M11: 0.13-0.25).
PANE_SAT_MIN = 0.08
# Fix round after P4b (17 Oct 2026; the review of the P4a fix round): the floor holds only under the clear-sky moods
# (wenart/style/finishes.py LIGHTING); overcast, cloudy soft, blue hour, night and interior evening show a grey or dark
# sky through the glass by design (the value is printed for them).
PANE_SAT_MOODS = ("warm daylight", "cool daylight", "bright noon", "golden evening")
# Fix round after P4b: the interior glazing of real03 named by the P4b analysis (a 2700 K hall or stair seen from a
# daylight room and the reverse); the display R/B of the panes within this of the room's walls (the verifier's model:
# only a 4000 K hall / stair / bath rig passes both directions; render.interior_glazing_record)
INTERIOR_GLAZING_VIEWS = {"real03": ("cam_r_L0_yasama_8_3", "cam_r_L0_ebeveyn_odasi_2_1",
                                      "cam_r_L0_yangin_merdiveni_1")}
INTERIOR_GLAZING_MAX_DELTA = 0.3
# Fix round after P4b: an exterior view's lawn (render.lawn_record) where it fills this share of the frame keeps this
# display saturation (P4b real03 previews: 0.35-0.42 in the sunlit views, 0.11 / 0.19 in ext_3 / ext_4).
LAWN_MIN_SHARE = 0.10
LAWN_SAT_MIN = 0.25
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
# Fix round after P6a (22 Oct 2026): a pulled sky's chosen save keeps render.SKY_PULL_MEDIAN_MIN
# (render.sky_pull_candidate_ok) and the blended sky stays within this of it: P6a's ext_5 (k 6, median 0.109, a
# near-black band) passed every check before. The 3 px feather and the ring keep the blend a little brighter than the
# save, never darker (P4a's terrace: save 0.4258, blended 0.4261).
SKY_PULL_MEDIAN_ALLOWANCE = 0.05
# ... and its sky mask is coherent: at least this share of the mask at full feather weight (render.full_weight_share;
# the same shim run: 0.961 / 0.957; eb80db2's mask with the haze shell left out at random: 0.000 / 0.000)
SKY_MASK_FULL_WEIGHT_MIN = 0.8
# The windowless bedrooms whose bedside rig adds to the fill light (the verifier's list of the fix round; P3:
# r_L0_yatak_odasi_4 night-dark at +6.1..+6.5 EV). True: the room must be in the scene (level L0 is always built);
# False: checked where its level is built (L-1b).
FILL_LIGHT_ROOMS = {"real04": {"r_L0_yatak_odasi_3": True, "r_L0_yatak_odasi_4": True, "r_L-1b_oda": False,
                               "r_L-1b_oda_2": False},
                    "real02": {"r_L0_yatak_odasi_3": True, "r_L0_yatak_odasi_4": True}}


def _dark(entry: dict) -> bool:
    """A view over the +3 cap (``lighting_dark``), not counting a ``minor`` one (fix round after P4b: less than one
    exposure step over, ``render.LIGHTING_DARK_MINOR_STOPS``: it renders at the cap)."""
    rec = (entry.get("exposure") or {}).get("lighting_dark") or entry.get("lighting_dark")
    return bool(rec) and rec.get("severity") != "minor"


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
        # fix round after P4a (17 Oct 2026): the rig part's extra warmth the view was mixed with (wb_rig_residual;
        # absent on m13.2 renders, which this check no longer passes: re-run it on m13.3 renders only)
        mixed = share is not None and share >= R.WB_RIG_SHARE_MIN
        want = R.mixed_whitepoint(anchor, x["wb_rig_whitepoint"], share, residual, x.get("wb_rig_residual")) \
            if mixed else anchor
        # fix round after P5 (22 Oct 2026): an interior view with a metered daylight takes the tint of its own daylight
        # (render.view_tint_gain of the recorded wb_day_green; m13.3 renders have no wb_view_tint_gain). Fix round
        # after P6a (22 Oct 2026): the gain is recomputed with the rule the record says it took (wb_tint_green_residual;
        # m13.4 records, P6a real04 and P6b real03, have none: they kept the residual), and a record of a later render
        # code says where its green was metered (wb_day_green_source) and which rule it took
        later = render.get("render_code_version") not in (None, "m13.4")
        if "wb_view_tint_gain" in x and later and x.get("wb_day_green") is not None \
                and (x.get("wb_day_green_source") not in R.WB_TINT_METERS or "wb_tint_green_residual" not in x):
            bad.append((r["camera"], "no wb_day_green_source / wb_tint_green_residual (an m13.4 render in a later "
                                     "manifest?)"))
        if "wb_view_tint_gain" in x:
            gain = R.view_tint_gain(anchor, x.get("wb_day_green"), residual, share if mixed else 0.0,
                                    keep_green_residual=bool(x.get("wb_tint_green_residual", True)))
            if abs(gain - float(x["wb_view_tint_gain"])) > 1e-6:
                bad.append((r["camera"], "tint gain off the recorded daylight green ratio", x.get("wb_day_green"),
                            x["wb_view_tint_gain"], gain))
            if gain != 1.0:
                want = R.tinted_whitepoint(want, gain)
        elif r.get("room_id") is not None and not (exterior_world and r.get("world") == exterior_world):
            bad.append((r["camera"], "no wb_view_tint_gain (rendered before m13.4?)"))
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


# Fix round after P6a (22 Oct 2026): pytest keeps no output of a passing test, and P6a's orange check passed with its
# per-view values lost (junit-full.xml has no system-out). The colour checks also write their values to
# CHECK_VALUES_FILE: in $WENART_RESULTS (the job's results folder, next to its junit XML) when the job sets it, else in
# the project's renders folder; one key per check, then per project. Written before the assertion, so a failing run
# keeps them too.
CHECK_VALUES_FILE = "gpu_check_values.json"


def _keep_values(check: str, name: str, values) -> Path:
    """Merge ``values`` (JSON-able) under ``[check][name]`` of ``CHECK_VALUES_FILE`` and return its path."""
    base = Path(os.environ["WENART_RESULTS"]) if os.environ.get("WENART_RESULTS") else OUTPUTS / name / "renders"
    path = base / CHECK_VALUES_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except ValueError:
        data = {}
    data.setdefault(check, {})[name] = values
    base.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True, default=str), encoding="utf-8")
    return path


def _wall_rb(view, table) -> float | None:
    """Display R/B of the mean of a view's wall pixels (``views.regions`` walls), None under 1 % of the frame."""
    from wenart import views

    mask = views.regions(view.read_index(), view.read_depth_mm(), view.read_normal(), table).masks.get(
        views.STRUCT_WALLS)
    if mask is None or mask.sum() < 0.01 * mask.size:
        return None
    mean = view.read_rgb()[mask].astype(np.float64).mean(axis=0)
    return round(float(mean[0] / max(mean[2], 1e-6)), 3)


def _wall_kind(entry: dict, manifest_types: dict) -> str:
    """``tiled`` or ``painted``: the finish of a view's walls by its room type (fix round after P5, 18 Oct 2026). What:
    ``tiled`` when the room's slot type (``shell.slot_room_type``) is one of ``shell.WET_WALL_ROOM_TYPES`` (bathroom,
    wc), else ``painted``; the type is the render entry's ``room_type``, else the scene manifest's room floors
    (``render.camera_room_type`` / ``room_types_from_manifest``). Why: the wet floor said ``tiled`` before, but a
    kitchen floor is wet while its walls are the style's paint with a 0.6 m splashback (Milestone 11 §1.3 M2,
    ``shell.SPLASHBACK``): P5's real04 kitchen mutfak_3 (about 64 % greige paint at R/B 1.28-1.32, tiles 1.12) read
    1.223 against a tile-only bound of 1.208 and failed with no cast in the image."""
    from wenart.blender import render as R
    from wenart.blender import shell

    room_type = R.camera_room_type(entry.get("room_type"), entry.get("room_id"), manifest_types)
    return "tiled" if shell.slot_room_type(room_type) in shell.WET_WALL_ROOM_TYPES else "painted"


def test_rig_lit_rooms_have_no_orange_cast(project):
    """The walls of a view lit mostly by the rig (``wb_rig_share`` >= 0.8) and metered within the cap have a display
    R/B of at most 1.5 (``views.regions`` walls, as ``test_white_plaster_walls_are_neutral``; P3: 1.86-4.2). Fix round
    after P4a (17 Oct 2026): the fixed 1.5 ignored the wall paint (real02's warm greige, linear R/B 1.34): the walls
    of a rig-lit view are compared with the walls of the same project's daylight views (rig share under
    ``render.WB_RIG_SHARE_MIN``, under the interior world, within the cap) of the same kind, painted or tiled: at most
    ``RIG_ROOM_REL_MAX`` times their median; the fixed ``RIG_ROOM_MAX_RB`` only where the project has no daylight view
    of that kind. Every view's value is printed.
    Fix round after P4b (17 Oct 2026; the verifier's better fix of the P4b orange finding): the views from a rig share
    of ``RIG_CHECK_SHARE`` (0.4) are checked, at most ``RIG_ROOM_ABOVE_DAY`` over the daylight median of their kind
    (P4b's mixed views at 0.44-0.65 were left out at 0.8).
    Fix round after P5 (18 Oct 2026). What: the kind is the wall finish of the room type (``_wall_kind``: bathroom and
    wc tiled, every other room painted, a kitchen too), and the daylight references come only from views that are not
    blocked (``_blocked``); a kind with no unblocked daylight view takes the fixed ``RIG_ROOM_MAX_RB``. Why: P5 real04
    called the kitchen tiled by its wet floor (its walls are paint with a splashback) and its tiled reference was the
    median of one daylight view, the blocked cam_r_L1_banyo_1 (one ceiling light over 55.7 % of the frame), so
    mutfak_3 failed at 1.223 against 1.208 with no orange in the image; as painted its bound is the painted daylight
    median 1.515 + 0.15. The kitchens keep the 2700 K rig (lead decision).
    Fix round after P6b (23 Oct 2026). What: the bound depends on how the view is lit (``_orange_bound``): a view
    lit by the rig alone (rig share at least ``RIG_ALONE_SHARE``) keeps the daylight median + ``RIG_ROOM_ABOVE_DAY``;
    a mixed view may reach the warmest daylight view of its kind + ``RIG_ROOM_ABOVE_WARMEST_DAY``, at most
    ``RIG_ROOM_ABOVE_DAY_MAX`` over the median. The values file also keeps each bound's regime and the light on the
    walls of every view it reads (``wb_walls``, ``_walls_record``; printed, not judged). Why: P6b's 4000 K halls and
    stairs failed 10 mixed views at 1.486-1.599 against 1.455 while the daylight-only oda_01 views of the same paint
    read 1.53-1.58 and the views lit by the rig alone 1.363-1.442; the P6b verifier refuted the white-point change,
    and a shim of P6b's scene found the warmth in the light both sources bring to those walls after the oak and greige
    bounce, not in the share. How: P4b's 2700 K views (1.562-1.864) still fail, each one, and no bound is lower than
    before (the numbers at ``RIG_ALONE_SHARE``)."""
    from wenart import views
    from wenart.blender import render as R

    name, scene, render = project
    if not _project_wb(render):
        pytest.skip(f"{name}: not rendered with --white-balance project")
    exterior_world = (((scene.get("lighting") or {}).get("world_exterior") or {}).get("name"))
    manifest_types = R.room_types_from_manifest(scene)
    entries = {r["camera"]: r for r in render["renders"]}
    indoor = {c: r for c, r in entries.items() if r.get("room_id") is not None and not _dark(r)
              and not (exterior_world and r.get("world") == exterior_world)}
    rig_lit = [c for c, r in indoor.items() if (r["exposure"].get("wb_rig_share") or 0.0) >= RIG_CHECK_SHARE]
    daylight = [c for c, r in indoor.items() if (r["exposure"].get("wb_rig_share") or 0.0) < R.WB_RIG_SHARE_MIN]
    if not rig_lit:
        pytest.skip(f"{name}: no view with a rig share of {RIG_CHECK_SHARE} or more within the cap")
    out = OUTPUTS / name / "renders"
    # fix round after P5: a blocked daylight view (one element over the frame, or the lens on a surface) shows no wall
    # colour to compare with; it is printed and left out of the references
    blocked = [c for c in daylight if _blocked(entries[c], out, entries[c].get("lens_mm") or 24.0)["blocked"]]
    daylight = [c for c in daylight if c not in blocked]
    table = views.index_table(scene)
    loaded = views.load_views(out, cameras=rig_lit + daylight)
    measured = {cam: _wall_rb(v, table) for cam, v in loaded.items()}

    def kind(cam):
        return _wall_kind(entries[cam], manifest_types)
    reference, warmest = {}, {}
    for k in ("painted", "tiled"):
        values = sorted(measured[c] for c in daylight if kind(c) == k and measured.get(c) is not None)
        reference[k] = float(np.median(values)) if values else None
        warmest[k] = values[-1] if values else None                 # fix round after P6b
    per_view, regimes, warm = {}, {}, []
    for cam in rig_lit:
        value = measured.get(cam)
        if value is None:
            continue
        share = entries[cam]["exposure"].get("wb_rig_share")
        bound, regimes[cam] = _orange_bound(share, reference[kind(cam)], warmest[kind(cam)])  # fix round after P6b
        per_view[cam] = (value, kind(cam), bound)
        if value > bound:
            warm.append((cam, value, kind(cam), bound, share, regimes[cam]))
    # fix round after P6b: the light on each view's walls (render wb_walls), the daylight views' too: recorded only
    walls = {c: _walls_record(entries[c]["exposure"]) for c in [*daylight, *per_view]}
    print(f"{name}: daylight wall R/B {[(c, measured.get(c), kind(c)) for c in daylight]}; references {reference}; "
          f"warmest {warmest}; blocked daylight views left out {blocked}")
    print(f"{name}: wall R/B of the rig-lit views (value, kind, bound) {per_view}")
    print(f"{name}: the light on the walls (render wb_walls; recorded, not judged) {walls}")
    # fix round after P6a: the values of a passing run are kept (CHECK_VALUES_FILE); fix round after P6b: with the
    # regime of each bound, the warmest daylight view of each kind and the light on the walls of every view
    _keep_values("rig_lit_rooms_have_no_orange_cast", name, {
        "daylight": {c: {"wall_rb": measured.get(c), "kind": kind(c), **walls[c]} for c in daylight},
        "references": reference, "warmest": warmest, "blocked_daylight": blocked, "above_day": RIG_ROOM_ABOVE_DAY,
        "above_warmest_day": RIG_ROOM_ABOVE_WARMEST_DAY, "above_day_max": RIG_ROOM_ABOVE_DAY_MAX,
        "rig_alone_share": RIG_ALONE_SHARE,
        "rig_lit": {c: {"wall_rb": v, "kind": k, "bound": b, "rig_share": entries[c]["exposure"].get("wb_rig_share"),
                        "regime": regimes[c], **walls[c]}
                    for c, (v, k, b) in per_view.items()},
        "warm": [c for c, *_rest in warm]})
    assert not warm, f"{name}: rig-lit views still orange (wall R/B over the bound): {warm}"


def _orange_bound(share, median, warmest) -> tuple[float, str]:
    """``(bound, regime)`` of the orange check for a rig-lit view of rig share ``share`` whose wall kind has the
    daylight median ``median`` and warmest daylight view ``warmest`` (fix round after P6b, 23 Oct 2026; the numbers
    at ``RIG_ALONE_SHARE``). No daylight view of the kind: the fixed ``RIG_ROOM_MAX_RB`` (``fixed``). Lit by the rig
    alone (``share`` at least ``RIG_ALONE_SHARE``): ``median + RIG_ROOM_ABOVE_DAY`` (``rig alone``, the rule since the
    fix round after P4b). Mixed: the larger of that and ``warmest + RIG_ROOM_ABOVE_WARMEST_DAY``, the latter at most
    ``median + RIG_ROOM_ABOVE_DAY_MAX`` (``mixed``)."""
    if median is None:
        return RIG_ROOM_MAX_RB, "fixed"
    alone = round(float(median) + RIG_ROOM_ABOVE_DAY, 3)
    try:
        s = float(share)
    except (TypeError, ValueError):
        s = 0.0
    if s >= RIG_ALONE_SHARE or warmest is None:
        return alone, "rig alone"
    spread = min(float(warmest) + RIG_ROOM_ABOVE_WARMEST_DAY, float(median) + RIG_ROOM_ABOVE_DAY_MAX)
    return round(max(alone, spread), 3), "mixed"


def _walls_record(exposure: dict) -> dict:
    """The light on a view's walls from its exposure record (``wb_walls``, ``render.wall_rig_record``; fix round after
    P6b, 23 Oct 2026): ``wall_light_rb`` / ``wall_day_rb`` (the linear R/B of the walls' light with everything lit and
    with the rig hidden), ``wall_rig_share``, ``wall_rig_rb`` (the linear R/B of the rig light measured on the walls),
    ``wall_rig_kelvin`` and ``lamp_rb`` (the rig lamp's linear R/B, the colour the white point mixes); None each in a
    record without it (render code before this round, a view without a wall metering). Why: the P6b shim found the
    halls' warmth in that light (the oak and greige bounce), not in the rig share; the next rule is decided from it."""
    rec = exposure.get("wb_walls") or {}

    def rb(rgb):
        return round(float(rgb[0]) / float(rgb[2]), 4) if rgb and len(rgb) == 3 and float(rgb[2]) > 0 else None
    return {"wall_light_rb": rb(rec.get("light_rgb")), "wall_day_rb": rb(rec.get("day_rgb")),
            "wall_rig_share": rec.get("rig_share"), "wall_rig_rb": rec.get("rig_rb"),
            "wall_rig_kelvin": rec.get("rig_kelvin"), "lamp_rb": rec.get("lamp_rb")}


# Fix round after P5 (22 Oct 2026): the wall display G/((R+B)/2) a painted daylight view may reach. P5 real04's sunlit
# L0 bedrooms read olive (1.048-1.066 on the bright near-neutral pixels of the previews; M12 1.007-1.017). bpy 5.2.2
# shim of real04 (the P3 pre-flight scene, 480 x 270, 64 spp, P5's anchor; walls of views.regions): the four daylight
# views 1.037-1.078 with the project white point, 1.019-1.040 with the view's own daylight tint
# (render.view_tint_gain). The warm greige paint itself is 1.047 in linear albedo.
DAYLIGHT_WALL_GREEN_MAX = 1.06
# Fix round after P6a (22 Oct 2026; the P6a verifier's lower bound): a tint that shifts the whole view to pass the wall
# mean must not turn the lower walls pink. The lower half of the wall pixels (by image row) keeps at least this display
# G/((R+B)/2). bpy 5.2.2 shims (480 x 270, meter 240 x 135 as on the pod) of P6a's own real04.blend (18 painted
# daylight views, P6a's anchor; m13.4's wall means within 0.01 of the pod's) and of real02's pre-flight scene (8 views,
# P4a's anchor): lower walls 0.979-1.021 with m13.4's tint, 0.962-1.009 with m13.5's (the walls' green, the residual
# kept), 0.947-1.008 with the verifier's rule without the residual (real04 yatak_odasi_3 0.947; render.WB_TINT_METER has
# every rule's numbers). The verifier's "about 0.97" would fail m13.5 on real04's e_yatak_odasi_2 / _3 (0.962, 0.966)
# on the shim, whose walls read up to 0.01 under the pod's.
DAYLIGHT_LOWER_WALL_GREEN_MIN = 0.95
# ... and the dots on a pulled sky's edge (render.sky_edge_dots, the record's edge_dot_px / edge_px): bpy 5.2.2 shim
# renders (480 x 270, 64 spp; P4a's real02 at its k, real04's P3 pre-flight scene at P5's k) 0.9-3.3 % of the edge
# pixels per view with m13.3's weights (medians 2.0 % and 2.4 %), 0-0.35 % with m13.4's (medians 0 and 0.14 %).
SKY_EDGE_DOT_VIEW_MAX = 0.015
SKY_EDGE_DOT_MEDIAN_MAX = 0.005


def _wall_green(view, table) -> float | None:
    """Display G / ((R + B) / 2) of the mean of a view's wall pixels (``views.regions`` walls), None under 1 % of the
    frame (fix round after P5)."""
    from wenart import views

    mask = views.regions(view.read_index(), view.read_depth_mm(), view.read_normal(), table).masks.get(
        views.STRUCT_WALLS)
    if mask is None or mask.sum() < 0.01 * mask.size:
        return None
    mean = view.read_rgb()[mask].astype(np.float64).mean(axis=0)
    return round(float(mean[1] / max((mean[0] + mean[2]) / 2.0, 1e-6)), 3)


def _lower_wall_green(view, table) -> float | None:
    """Display G / ((R + B) / 2) of the mean of the lower half (by image row, from the median row down) of a view's
    wall pixels (``views.regions`` walls), None under 1 % of the frame (fix round after P6a)."""
    from wenart import views

    mask = views.regions(view.read_index(), view.read_depth_mm(), view.read_normal(), table).masks.get(
        views.STRUCT_WALLS)
    if mask is None or mask.sum() < 0.01 * mask.size:
        return None
    rows = np.nonzero(mask)[0]
    lower = mask & (np.arange(mask.shape[0])[:, None] >= float(np.median(rows)))
    mean = view.read_rgb()[lower].astype(np.float64).mean(axis=0)
    return round(float(mean[1] / max((mean[0] + mean[2]) / 2.0, 1e-6)), 3)


def test_daylight_walls_are_not_olive(project):
    """Fix round after P5 (22 Oct 2026). What: the painted walls of every view lit mostly by daylight (rig share under
    ``RIG_CHECK_SHARE``, the orange check's floor; under the interior world, within the cap, not blocked; the rig's
    warm light only lowers the ratio) have a display G/((R+B)/2) of at most ``DAYLIGHT_WALL_GREEN_MAX``; every value
    is printed with the view's ``wb_day_green`` and ``wb_view_tint_gain``. Why: P5 real04's six sunlit L0 bedroom views read olive under the project anchor (metered
    on the terrace): their daylight is mostly sunlight bounced off the green ground outside. The pin reads the
    pixels, not the white point rule (``test_views_keep_the_project_white_point_or_mix_it_with_the_rig`` checks the
    rule against the record). Fix round after P6a (22 Oct 2026): the lower half of the walls keeps at least
    ``DAYLIGHT_LOWER_WALL_GREEN_MIN`` (``_lower_wall_green``), so a tint that shifts the whole view cannot pass the
    olive pin by turning the lower walls pink; the values are kept (``CHECK_VALUES_FILE``)."""
    from wenart import views
    from wenart.blender import render as R

    name, scene, render = project
    if not _project_wb(render):
        pytest.skip(f"{name}: not rendered with --white-balance project")
    exterior_world = (((scene.get("lighting") or {}).get("world_exterior") or {}).get("name"))
    manifest_types = R.room_types_from_manifest(scene)
    entries = {r["camera"]: r for r in render["renders"]}
    out = OUTPUTS / name / "renders"
    daylight = [c for c, r in entries.items() if r.get("room_id") is not None and not _dark(r)
                and not (exterior_world and r.get("world") == exterior_world)
                and (r["exposure"].get("wb_rig_share") or 0.0) < RIG_CHECK_SHARE
                and _wall_kind(r, manifest_types) == "painted"]
    daylight = [c for c in daylight if not _blocked(entries[c], out, entries[c].get("lens_mm") or 24.0)["blocked"]]
    if not daylight:
        pytest.skip(f"{name}: no painted daylight view")
    table = views.index_table(scene)
    loaded = views.load_views(out, cameras=daylight)
    values = {cam: (_wall_green(v, table), entries[cam]["exposure"].get("wb_day_green"),
                    entries[cam]["exposure"].get("wb_view_tint_gain")) for cam, v in loaded.items()}
    lower = {cam: _lower_wall_green(v, table) for cam, v in loaded.items()}           # fix round after P6a
    olive = [(cam, v) for cam, v in values.items() if v[0] is not None and v[0] > DAYLIGHT_WALL_GREEN_MAX]
    pink = [(cam, v) for cam, v in lower.items() if v is not None and v < DAYLIGHT_LOWER_WALL_GREEN_MIN]
    print(f"{name}: daylight wall G/((R+B)/2), daylight green ratio, tint gain {values}; lower walls {lower}")
    # fix round after P6a: the values of a passing run are kept (CHECK_VALUES_FILE)
    _keep_values("daylight_walls_are_not_olive", name, {
        "bound": DAYLIGHT_WALL_GREEN_MAX, "lower_bound": DAYLIGHT_LOWER_WALL_GREEN_MIN,
        "views": {c: {"wall_green": v[0], "lower_wall_green": lower.get(c), "wb_day_green": v[1],
                      "wb_view_tint_gain": v[2],
                      "wb_day_green_source": entries[c]["exposure"].get("wb_day_green_source"),
                      "wb_day_green_all": entries[c]["exposure"].get("wb_day_green_all"),
                      "wb_tint_green_residual": entries[c]["exposure"].get("wb_tint_green_residual")}
                  for c, v in values.items()},
        "olive": [c for c, _v in olive], "pink": [c for c, _v in pink]})
    assert not olive, f"{name}: olive daylight walls (over {DAYLIGHT_WALL_GREEN_MAX}): {olive}"
    assert not pink, f"{name}: pink lower daylight walls (under {DAYLIGHT_LOWER_WALL_GREEN_MIN}): {pink}"


def test_sky_pull_leaves_no_dotted_edges(project):
    """Fix round after P5 (22 Oct 2026). What: every pulled sky (``sky_pull.k`` at least 1) records the dots on its
    edge (``edge_dot_px`` of ``edge_px``, ``render.sky_edge_dots``): at most ``SKY_EDGE_DOT_VIEW_MAX`` of the edge
    pixels in each view and ``SKY_EDGE_DOT_MEDIAN_MAX`` in their median. Why: P5 real04's ext_1 (k 3) and teras_2_1
    (k 4) had a dotted white line along every roof, gutter and pergola edge: the haze-shell hits at an edge took the
    shell's reference and kept their unpulled sky (``render.sky_pull_weights``). A pull without the record was
    rendered before m13.4 and fails."""
    import statistics

    name, _scene, render = project
    shares, missing = {}, []
    for r in render["renders"]:
        s = r.get("sky_pull") or {}
        if not s.get("k"):
            continue
        if "edge_dot_px" not in s or "edge_px" not in s:
            missing.append(r["camera"])
            continue
        shares[r["camera"]] = (s["edge_dot_px"], s["edge_px"],
                               round(s["edge_dot_px"] / s["edge_px"], 4) if s["edge_px"] else 0.0)
    print(f"{name}: dots on the pulled skies' edges (dots, edge pixels, share) {shares}")
    if not shares and not missing:
        pytest.skip(f"{name}: no pulled sky")
    assert not missing, f"{name}: sky pulls without edge_dot_px (rendered before m13.4?): {missing}"
    over = {c: v for c, v in shares.items() if v[2] > SKY_EDGE_DOT_VIEW_MAX}
    median = statistics.median(v[2] for v in shares.values())
    assert not over and median <= SKY_EDGE_DOT_MEDIAN_MAX, \
        f"{name}: dotted sky edges (view max {SKY_EDGE_DOT_VIEW_MAX}, median {median} max " \
        f"{SKY_EDGE_DOT_MEDIAN_MAX}): {over or shares}"


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
            # fix round after P4b (17 Oct 2026): the exterior ground cap renders these shaded-facade views darker, so
            # their sky may already read as sky as rendered (k 0 by render.choose_sky_pull's first rule): that passes
            if s and not s.get("k") and R.sky_pull_qualifies({"median": s["median_before"],
                                                              "saturation": s["saturation_before"]}):
                continue
            chosen = next((c for c in (s or {}).get("tried") or [] if c["k"] == (s or {}).get("k")), None)
            floor = R.sky_pull_floor(chosen) if chosen else R.SKY_PULL_SAT_MIN    # fix round after P4a: its rule's
            if not s or not s.get("k") or s["median_after"] > R.SKY_PULL_MEDIAN_MAX \
                    or s["median_after"] < R.SKY_PULL_MEDIAN_MIN - SKY_PULL_MEDIAN_ALLOWANCE \
                    or not s["saturation_after"] > s["saturation_before"] \
                    or s["saturation_after"] < floor - SKY_PULL_SAT_ALLOWANCE:
                bad.append((cam, "a shaded-facade view whose sky was not pulled to its target", s))
        # fix round after P6a: a tried k under the median floor is no qualifying k (render.sky_pull_candidate_ok)
        over = [r["camera"] for r in render["renders"] if (r.get("sky_pull") or {}).get("median_before", 0.0)
                > R.SKY_PULL_MEDIAN_MAX and any(R.sky_pull_candidate_ok(c) for c in r["sky_pull"].get("tried") or [])]
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
                # fix round after P6a: the chosen save keeps the median floor (render.sky_pull_candidate_ok)
                if chosen is None or not R.sky_pull_candidate_ok(chosen) or s["median_after"] > s["median_before"] \
                        or s["saturation_after"] < s["saturation_before"]:
                    bad.append((r["camera"], "sky pull off its targets", s))
                if s["median_after"] < R.SKY_PULL_MEDIAN_MIN - SKY_PULL_MEDIAN_ALLOWANCE:
                    bad.append((r["camera"], f"crushed sky: blended median {s['median_after']} under the floor "
                                             f"{R.SKY_PULL_MEDIAN_MIN:g} - {SKY_PULL_MEDIAN_ALLOWANCE:g}", s))
                # fix round after P4a (17 Oct 2026): the floor of the rule the k was chosen by (the mid-tone rule's
                # SKY_PULL_SAT_NEAR, else SKY_PULL_SAT_MIN)
                floor = R.sky_pull_floor(chosen) if chosen else R.SKY_PULL_SAT_MIN
                if s["saturation_after"] < floor - SKY_PULL_SAT_ALLOWANCE:
                    bad.append((r["camera"], f"blended sky saturation {s['saturation_after']} under the floor "
                                             f"{floor:g} - {SKY_PULL_SAT_ALLOWANCE:g}", s))
                full = s.get("full_weight_share")
                if full is None:
                    bad.append((r["camera"], "sky pull without full_weight_share (rendered before fix round part 3?)"))
                elif full < SKY_MASK_FULL_WEIGHT_MIN:
                    bad.append((r["camera"], f"speckled sky mask: {full:.1%} of it at full feather weight (minimum "
                                             f"{SKY_MASK_FULL_WEIGHT_MIN:.0%})", s))
    pulled = [(r["camera"], r["window_pull"].get("pane_median_after")) for r in render["renders"]
              if r.get("room_id") is not None and not r.get("open_air") and (r.get("window_pull") or {}).get("k")]
    over = [(c, m) for c, m in pulled if m is None or m > PANE_MEDIAN_MAX]
    into_sun = [r["camera"] for r in render["renders"] if (r.get("sky_pull") or {}).get("into_sun")]
    print(f"{name}: sky pulls {skies}; views into the sun {into_sun}; pulled panes {len(pulled)}, over "
          f"{PANE_MEDIAN_MAX}: {over}")
    if pulled and (len(pulled) - len(over)) / len(pulled) < PANE_PULLED_SHARE:
        bad.append(("window pull", f"{len(over)} of {len(pulled)} pulled views keep pane medians over "
                                   f"{PANE_MEDIAN_MAX}", over))
    # fix round after P4a (17 Oct 2026): the panes show the sky, not a grey card: the median pane saturation of the
    # interior views as written (after the pull) is at least PANE_SAT_MIN (P4a 0.00-0.07 with the haze in the camera's
    # view through the glass; M11 0.13-0.25). A view whose record has no pane_saturation was rendered before m13.3.
    panes = []
    for r in render["renders"]:
        wp = r.get("window_pull") or {}
        if r.get("room_id") is None or r.get("open_air") or not wp:
            continue
        if "pane_saturation" not in wp:
            bad.append((r["camera"], "window pull without pane_saturation (rendered before m13.3?)"))
            continue
        panes.append((r["camera"], wp.get("pane_saturation_after") if wp.get("k") else wp["pane_saturation"]))
    sats = sorted(v for _c, v in panes if v is not None)
    # fix round after P4b (17 Oct 2026; the review of the P4a fix round): the floor holds under the clear-sky moods only
    moods = {str(m).strip().lower() for m in [scene.get("wenart_mood")] + [(r.get("exposure") or {}).get("mood")
                                                                            for r in render["renders"]] if m}
    clear = bool(moods) and moods <= set(PANE_SAT_MOODS)
    print(f"{name}: pane saturation {panes}; moods {sorted(moods)} ("
          f"{'clear sky: floor ' + str(PANE_SAT_MIN) if clear else 'no clear-sky mood: printed only'})")
    if clear and sats and sats[len(sats) // 2] < PANE_SAT_MIN:
        bad.append(("window panes", f"median pane saturation {sats[len(sats) // 2]} under {PANE_SAT_MIN}: grey "
                                    f"cards, not the sky", panes))
    assert not bad, f"{name}: {bad}"


PULL_CLIP_FEATHER_ALLOWANCE = 0.005  # the 3 px feather keeps part of the unpulled pane at its edge (clip_after)


def test_window_pull_takes_an_unclipped_k_when_one_was_tried(project):
    """Fix round after P4b (17 Oct 2026): P4b left clipped panes in 10 real03 views (yasama_8_3 13.9 % at k 1) because a
    clip-free k made the panes a little darker than the bright greige walls. Whenever a tried k had a pane clip of at
    most ``render.PULL_MAX_CLIP`` and kept the panes at least ``render.PULL_WALL_RATIO_MIN`` of the wall median (or the
    view has no wall), the chosen k is unclipped and the written panes are too (``clip_after`` within the feather's
    ``PULL_CLIP_FEATHER_ALLOWANCE``)."""
    from wenart.blender import render as R

    name, _scene, render = project
    bad, checked = [], []
    for r in render["renders"]:
        wp = r.get("window_pull") or {}
        tried = wp.get("tried") or []
        wall = wp.get("wall_median")
        ok = [c for c in tried if c["clip"] <= R.PULL_MAX_CLIP and (wall is None or
                                                                    c["median"] >= R.PULL_WALL_RATIO_MIN * wall)]
        if not ok:
            continue
        checked.append(r["camera"])
        # no pull is right only when the panes were unclipped as rendered (render.choose_pull's fourth rule)
        chosen = next((c for c in tried if c["k"] == wp.get("k")), None) if wp.get("k") else \
            {"clip": wp.get("clip_after")}
        if chosen is None or chosen["clip"] is None or chosen["clip"] > R.PULL_MAX_CLIP \
                or wp.get("clip_after") is None or wp["clip_after"] > R.PULL_MAX_CLIP + PULL_CLIP_FEATHER_ALLOWANCE:
            bad.append((r["camera"], wp.get("k"), wp.get("clip_after"), wp.get("rule"), ok[0]))
    print(f"{name}: {len(checked)} views with an unclipped k near the walls tried; clipped after the pull: {bad}")
    assert not bad, f"{name}: window pulls that kept clipped panes although a clip-free k was tried: {bad}"


def test_window_pull_leaves_panes_that_need_no_pull(project):
    """Pass before P5 (17 Oct 2026): a window pull takes panes to or under the wall median only when the panes as
    rendered needed a pull (``render.pull_needed``: clipped, or off the pane target). The replay of P4a's real02
    cam_r_L1_teras_2_2 (panes 0.4787 against walls of 0.37, p90 0.65, clip 0) and P4b's real03 yasama_3 / yasama_4_1
    with the fix round's ``choose_pull`` pulled them a stop under their walls."""
    from wenart.blender import render as R

    name, _scene, render = project
    bad, pulled = [], 0
    for r in render["renders"]:
        wp = r.get("window_pull") or {}
        wall = wp.get("wall_median")
        if not wp.get("k") or wall is None:
            continue
        pulled += 1
        chosen = next((c for c in wp.get("tried") or [] if c["k"] == wp["k"]), None)
        median = wp.get("pane_median_after", chosen["median"] if chosen else None)
        if median is None or median > wall:
            continue
        if not R.pull_needed(wp.get("clip_before"), wp.get("pane_median"), wp.get("pane_p90")):
            bad.append((r["camera"], wp["k"], wp.get("clip_before"), wp.get("pane_median"), wp.get("pane_p90"),
                        median, wall, wp.get("rule")))
    print(f"{name}: {pulled} pulled views with walls; panes fine as rendered but pulled under the walls: {bad}")
    assert not bad, f"{name}: window pulls that took unclipped, on-target panes under the walls: {bad}"


def test_interior_glazing_pull_removes_clipping(project):
    """Pass before P5 (17 Oct 2026; the review of the fix round after P4b): the interior glazing (windows between two
    indoor rooms, left out of the window pull) records its panes' clip share as written (``interior_glazing.clip``)
    and its pull (``interior_glazing.pull``, ``render.choose_interior_pull``). Clipped interior panes (over
    ``render.PULL_MAX_CLIP`` as rendered) are written at most ``PULL_MAX_CLIP + PULL_CLIP_FEATHER_ALLOWANCE`` whenever
    a tried k unclipped them with the panes at least ``render.PULL_WALL_RATIO_MIN`` of the wall median (any k without
    a wall); unclipped ones are not pulled (the neighbouring room stays at the view's exposure). P4b real03:
    giris_holu_1 / 2 / 3_1 see only an interior window onto a daylit room and the sunlit outside (8-13 % clipped)."""
    from wenart.blender import render as R

    name, _scene, render = project
    bad, rows = [], {}
    for r in render["renders"]:
        g = r.get("interior_glazing")
        if not g:
            continue
        if g.get("clip") is None or "pull" not in g:
            bad.append((r["camera"], "no clip or pull in interior_glazing (rendered before the pass before P5?)"))
            continue
        p = g["pull"] or {}
        before, k = p.get("clip_before"), p.get("k") or 0
        rows[r["camera"]] = (before, k, g["clip"])
        if before is None:
            bad.append((r["camera"], "no interior pull record", g))
            continue
        if before <= R.PULL_MAX_CLIP:
            if k:
                bad.append((r["camera"], f"unclipped interior panes ({before}) pulled k {k}"))
            continue
        tried, wall = p.get("tried") or [], p.get("wall_median")
        if not tried:
            bad.append((r["camera"], f"interior panes clipped ({before}) and no k tried"))
            continue
        ok = [c for c in tried if c["clip"] is not None and c["clip"] <= R.PULL_MAX_CLIP
              and (wall is None or c["median"] >= R.PULL_WALL_RATIO_MIN * wall)]
        if ok and g["clip"] > R.PULL_MAX_CLIP + PULL_CLIP_FEATHER_ALLOWANCE:
            bad.append((r["camera"], (f"interior panes {g['clip']} clipped as written although k {ok[0]['k']} "
                                      f"unclipped them"), p.get("rule")))
    print(f"{name}: interior glazing (clip before, k, clip as written) {rows}")
    assert not bad, f"{name}: interior glazing clipping: {bad}"


def test_interior_glazing_keeps_one_white_point(project):
    """Fix round after P4b (17 Oct 2026; the verifier's better fix of the P4b interior-glazing finding): a window
    between two indoor rooms is never pulled and its panes are recorded against the camera room's walls
    (``interior_glazing``, ``render.interior_glazing_record``). The named real03 views (``INTERIOR_GLAZING_VIEWS``: a
    daylight room looking into a rig-lit stair or vestibule, and the stair looking back; P4b 1.82 / 2.15 against walls
    of 1.26 / 1.29, 1.02 against 2.05) keep the panes within ``INTERIOR_GLAZING_MAX_DELTA`` of the walls in display
    R/B; every view's values are printed. Fix round after P6b (23 Oct 2026): the values of every view are kept
    (``CHECK_VALUES_FILE``) with the light on its own walls (``_walls_record``), also for a project without named views
    (skipped) and for a passing run; the bound is unchanged (P6b: yasama_8_3 0.692, ebeveyn_odasi_2_1 0.321,
    yangin_merdiveni_1 -0.398, smaller than P4b's 0.86 / 0.56 / -1.03). Why no rule change: no white point can close it
    (one white point per frame keeps the pane-to-wall ratio), the P6b shim found the fire stair's walls lit at a linear
    R/B of 4.09 (rig and daylight both warmed by the oak treads and floors) against 1.76 / 1.95 on the walls of the
    daylight rooms yasama_8_1 and ebeveyn_odasi_2_1, and the pane mean also counts the oak treads behind the glass
    (2.28 on yasama_8_3's preview); the hall and stair rig temperature (``lighting.RIG_NEUTRAL_K``) or the pin is a user
    decision."""
    name, _scene, render = project
    entries = {r["camera"]: r for r in render["renders"]}
    rows = {c: (g["pane_rb"], g["wall_rb"], g["delta_rb"], g["windows"]) for c, e in entries.items()
            if (g := e.get("interior_glazing"))}
    named = [c for c in INTERIOR_GLAZING_VIEWS.get(name, ()) if c in entries]
    print(f"{name}: interior glazing (pane R/B, wall R/B, delta, windows) {rows}")
    # fix round after P6b: the values are kept whatever the verdict (CHECK_VALUES_FILE), with the light on the view's
    # own walls (_walls_record: the stair or vestibule behind the glass is the room of its own views)
    _keep_values("interior_glazing_keeps_one_white_point", name, {
        "views": {c: {"pane_rb": p, "wall_rb": w, "delta_rb": d, "windows": ws,
                      "rig_share": (entries[c].get("exposure") or {}).get("wb_rig_share"),
                      **_walls_record(entries[c].get("exposure") or {})}
                  for c, (p, w, d, ws) in rows.items()},
        "named": named, "max_delta": INTERIOR_GLAZING_MAX_DELTA})
    if not named:
        pytest.skip(f"{name}: none of the named interior-glazing views was rendered")
    bad = []
    for cam in named:
        e = entries[cam]
        if "interior_glazing" not in e:
            bad.append((cam, "no interior_glazing record (rendered before the fix round after P4b?)"))
        elif not e["interior_glazing"]:
            bad.append((cam, "no interior glazing in view (the window's room_ids no longer name two rooms?)"))
        elif e["interior_glazing"]["delta_rb"] is None:
            bad.append((cam, "no wall R/B to compare with", e["interior_glazing"]))
        elif abs(e["interior_glazing"]["delta_rb"]) > INTERIOR_GLAZING_MAX_DELTA:
            bad.append((cam, f"pane R/B {e['interior_glazing']['pane_rb']} against the walls' "
                             f"{e['interior_glazing']['wall_rb']}: two white points in one frame"))
    assert not bad, f"{name}: interior glazing: {bad}"


def test_exterior_views_cap_the_ground_and_keep_the_lawn_green(project):
    """Fix round after P4b (17 Oct 2026; the verifier's better fix of the P4b exterior finding): an exterior view keeps
    its facade exposure unless that would show the sunlit ground more than
    ``render.EXTERIOR_GROUND_HEADROOM_STOPS`` over the target (``render.exterior_exposure``): every metered exterior
    entry has ``ev <= ev_ground + headroom`` (half an exposure step of rounding; an EV held at a limit is exempt). Its
    lawn (``lawn``, ``render.lawn_record``: green albedo facing up in front of the haze shell), where it fills at least
    ``LAWN_MIN_SHARE`` of the frame, keeps a display saturation of at least ``LAWN_SAT_MIN`` (P4b's ext_3 / ext_4:
    cream lawns). No horizon-band pin: the haze toward the sun stays white at any EV, and a view into the sun
    (``sky_pull.into_sun``; lead decision (4) of 17 Oct 2026: such views are only listed) is printed, not pinned (the
    CPU shim render of real02's ext_1, 6 degrees off the sun, capped to -6.17 EV: lawn saturation 0.246)."""
    from wenart.blender import render as R

    name, _scene, render = project
    ext = [r for r in render["renders"] if r.get("room_id") is None and (r.get("exposure") or {}).get("mode") == "auto"
           and ((r["exposure"].get("meter") or {}).get("metered"))]
    if not ext:
        pytest.skip(f"{name}: no metered exterior view")
    bad, rows = [], {}
    for r in ext:
        x, cam = r["exposure"], r["camera"]
        if "ground_cap" not in x or "lawn" not in r:
            bad.append((cam, "no ground cap or lawn record (rendered before the fix round after P4b?)"))
            continue
        lawn = r["lawn"]
        rows[cam] = (x["ev"], x.get("ev_facade"), x.get("ev_ground"), x["ground_cap"],
                     None if not lawn else (lawn["px_share"], lawn["saturation"]))
        ev = float(x["ev"]) - float(x.get("ev_offset") or 0.0)
        if x.get("ev_ground") is not None and not x.get("at_limit") and \
                ev > float(x["ev_ground"]) + float(x["ground_headroom_stops"]) + R.EXPOSURE_STEP / 2 + 1e-6:
            bad.append((cam, f"EV {ev:+.3f} over the ground EV {x['ev_ground']:+.3f} + "
                             f"{x['ground_headroom_stops']:g} stops"))
        into_sun = bool((r.get("sky_pull") or {}).get("into_sun"))     # lead decision (4): only listed
        if lawn and lawn["px_share"] >= LAWN_MIN_SHARE and lawn["saturation"] < LAWN_SAT_MIN and not into_sun:
            bad.append((cam, f"lawn saturation {lawn['saturation']} under {LAWN_SAT_MIN} ({lawn['px_share']:.0%} of "
                             f"the frame): a bleached lawn"))
    print(f"{name}: exterior (ev, ev_facade, ev_ground, capped, lawn share and saturation) {rows}")
    assert not bad, f"{name}: exterior exposure: {bad}"


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
            if r.get("room_id") in adds | set(FILL_LIGHT_ROOMS.get(name, {})) and _dark(r)]
    halls = [r for r in render["renders"] if types.get(r.get("room_id") or "") in ("hall", "stair")]
    dark_halls = [(r["camera"], r["exposure"]["ev_raw"]) for r in halls if _dark(r)]
    print(f"{name}: rooms whose rig adds to the fill light {sorted(adds)}; hall views {len(halls)}, over the cap "
          f"{dark_halls}")
    assert not dark, f"{name}: rooms with the fill light back are still dark: {dark}"
    assert not halls or len(dark_halls) / len(halls) <= HALL_DARK_MAX_SHARE, \
        f"{name}: {len(dark_halls)} of {len(halls)} hall / stair views over the cap: {dark_halls}"
