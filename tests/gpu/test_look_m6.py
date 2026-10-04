"""Milestone 6 Cycles realism GPU tests (docs/milestone6.md §5, §9): run on the
pod after the full run's renders (``pytest -m gpu tests/gpu/test_look_m6.py``)
over the projects in ``$RENDER_TEST_PROJECTS`` (exported by the orchestrator,
empty when no project rendered: then every test is skipped, never a fallback
to old outputs on the volume). They read ``$WENART_OUTPUTS/<p>/scene`` and
``/renders``:

- the renders are Milestone 6 renders with the Milestone 7 look (render
  code ``m7.1``, look ``AgX - Punchy``, a ``window_pull`` record per view);
- views of rooms with an unverified piece have no colour cast from the
  stripes: |white-balance tint| <= 40 (Milestone 5: -92 to -97);
- parametric kitchen counters are not black: the mean display luminance of
  their index pixels is >= 0.15 in the views of their own room (their fronts
  were coplanar with the carcass);
- window pull: ``clip_after`` <= 0.05 in >= 90 % of the views with panes;
- dim rooms (window/floor < 0.08, an assumed half-power ceiling light) are
  metered below +6 EV (Milestone 5: +8, at the limit, noisy); synthetic-03's
  dark basement rooms are among them;
- the ``assumed`` entries: one per bedding set, counter-front set,
  door-handle pair, skirting run and dim-room light, each with ``parent``,
  ``kind`` and ``reason``, none of them an element of the building.
"""
import json
import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("RENDER_TEST_PROJECTS", "").split() if p]
MAX_ABS_TINT = 40.0
COUNTER_MIN_LUMINANCE = 0.15
COUNTER_MIN_PIXELS = 200
PULL_MAX_CLIP = 0.05
PULL_MIN_SHARE = 0.90
DIM_MAX_EV = 6.0
BED_TYPES = ("bed", "bed_single", "bed_double")
COUNTER_TYPES = ("kitchen_counter", "kitchen_island")
NO_SKIRTING_TYPES = ("bathroom", "wc", "kitchen", "balcony")
# The rooms of the four Milestone 5 views metered at the +8 EV limit (synthetic-03 basement).
S03_DARK_ROOMS = {"r_L-1_kiler_2", "r_L-1_yatak_odasi"}

if not PROJECTS:
    pytest.skip("RENDER_TEST_PROJECTS is empty: no project rendered in this run", allow_module_level=True)


def _load(project: str, name: str) -> dict:
    path = OUTPUTS / project / name
    assert path.exists(), f"{path} missing: did the run build and render {project}?"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    scene = _load(request.param, "scene/scene_manifest.json")
    render = _load(request.param, "renders/render_manifest.json")
    return request.param, scene, render


def _furniture(scene: dict) -> list[dict]:
    return [o for o in scene["objects"] if o["kind"] == "furniture"]


def _assumed(scene: dict, kind: str) -> list[dict]:
    return [a for a in scene["assumed"] if a.get("kind") == kind]


def test_renders_are_milestone_6_renders(project):
    name, _scene, render = project
    assert render["render_code_version"] == "m7.1" and render["look"] == "AgX - Punchy", name
    missing = [r["camera"] for r in render["renders"] if "window_pull" not in r]
    assert not missing, f"{name}: entries without a window_pull record: {missing}"


def test_unverified_pieces_cast_no_colour(project):
    name, scene, render = project
    rooms = {o.get("room_id") for o in _furniture(scene) if o["status"] == "unverified"}
    rooms |= {o.get("element_id") for o in scene["objects"] if o["kind"] == "floor" and o["status"] == "unverified"}
    views = [r for r in render["renders"] if r.get("room_id") in rooms]
    if not views:
        pytest.skip(f"{name}: no view of a room with an unverified piece")
    tinted = [(r["camera"], r["exposure"]["wb_tint"]) for r in views
              if r["exposure"].get("wb_tint") is not None and abs(r["exposure"]["wb_tint"]) > MAX_ABS_TINT]
    print(f"{name}: {len(views)} views of rooms with unverified pieces, tints "
          f"{[r['exposure'].get('wb_tint') for r in views]}")
    assert not tinted, f"{name}: white-balance tint beyond +-{MAX_ABS_TINT}: {tinted}"


def test_kitchen_counter_fronts_are_lit(project):
    from wenart import views as V

    name, scene, render = project
    counters = {o["pass_index"]: o["wenart_id"] for o in _furniture(scene)
                if o.get("type") in COUNTER_TYPES and str(o.get("method", "")).startswith("parametric")}
    rooms = {o["pass_index"]: o.get("room_id") for o in _furniture(scene) if o["pass_index"] in counters}
    if not counters:
        pytest.skip(f"{name}: no parametric kitchen counter")
    checked, dark, other_room = 0, [], 0
    for r in render["renders"]:
        idx = [int(i) for i, st in (r.get("index_stats") or {}).items()
               if int(i) in counters and st["pixels"] >= COUNTER_MIN_PIXELS]
        # The views of the counter's own room (M8 F1: real01's counter seen through a door from another room, metered
        # for that room, was darker; the coplanar-front fault shows in the kitchen's own views).
        own = [i for i in idx if not (rooms.get(i) and r.get("room_id") and r["room_id"] != rooms[i])]
        other_room += len(idx) - len(own)
        idx = own
        if not idx:
            continue
        rgb = V.read_rgb(OUTPUTS / name / "renders" / r["png"]).astype(np.float64) / 255.0
        index = V.read_index(OUTPUTS / name / "renders" / r["files"]["index"])
        lum = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
        for i in idx:
            checked += 1
            mean = float(lum[index == i].mean())
            if mean < COUNTER_MIN_LUMINANCE:
                dark.append((r["camera"], counters[i], round(mean, 3)))
    if not checked:
        pytest.skip(f"{name}: no view shows a parametric counter with {COUNTER_MIN_PIXELS}+ pixels")
    print(f"{name}: {checked} counter views checked ({other_room} seen from another room left out)")
    assert not dark, f"{name}: counters darker than {COUNTER_MIN_LUMINANCE} mean display luminance: {dark}"


def test_window_pull_keeps_the_panes_unclipped(project):
    name, _scene, render = project
    with_panes = [r for r in render["renders"] if r.get("window_pull")]
    if not with_panes:
        pytest.skip(f"{name}: no view with window panes")
    over = [(r["camera"], r["window_pull"]["clip_before"], r["window_pull"]["clip_after"], r["window_pull"]["ev"])
            for r in with_panes if r["window_pull"]["clip_after"] is None
            or r["window_pull"]["clip_after"] > PULL_MAX_CLIP]
    share = 1.0 - len(over) / len(with_panes)
    print(f"{name}: {len(with_panes)} views with panes, {share:.0%} with clip_after <= {PULL_MAX_CLIP}; over: {over}")
    assert share >= PULL_MIN_SHARE, f"{name}: only {share:.0%} of the pulled views are unclipped: {over}"


def test_dim_rooms_are_metered_below_six_ev(project):
    name, scene, render = project
    dim = {a["parent"] for a in _assumed(scene, "dim_room_light")}
    if name == "synthetic-03":
        assert S03_DARK_ROOMS <= dim, f"synthetic-03: dim-room lights {sorted(dim)}"
    if not dim:
        pytest.skip(f"{name}: no dim room")
    views = [r for r in render["renders"] if r.get("room_id") in dim]
    assert views, f"{name}: no view of the dim rooms {sorted(dim)}"
    bright = [(r["camera"], r["exposure"]["ev"]) for r in views if r["exposure"]["ev"] >= DIM_MAX_EV]
    print(f"{name}: dim rooms {sorted(dim)}, EVs {[(r['camera'], r['exposure']['ev']) for r in views]}")
    assert not bright, f"{name}: dim-room views at +{DIM_MAX_EV} EV or more: {bright}"


def test_assumed_entries_of_the_design_details(project):
    from wenart import views as V

    name, scene, _render = project
    for a in scene["assumed"]:
        if "kind" in a or "parent" in a:
            assert a.get("parent") and a.get("kind") and a.get("reason"), (name, a)
    parametric = [o for o in _furniture(scene) if str(o.get("method", "")).startswith("parametric")]
    beds = sorted(o["wenart_id"] for o in parametric if o.get("type") in BED_TYPES)
    counters = sorted(o["wenart_id"] for o in parametric if o.get("type") in COUNTER_TYPES)
    doors = sorted({o["wenart_id"] for o in scene["objects"] if o["kind"] == "door" and o["name"].endswith("_leaf")})
    skirting = sorted(o["parent"] for o in scene["objects"] if o["kind"] == "wall" and o.get("parent"))
    lights = sorted(o["parent"] for o in scene["objects"] if o["kind"] == "light" and o.get("parent")
                    and o["assumed"].get("w_per_m2") is not None and o["assumed"].get("window_floor_ratio") is not None)
    assert sorted(a["parent"] for a in _assumed(scene, "bedding")) == beds, name
    assert sorted(a["parent"] for a in _assumed(scene, "counter_fronts")) == counters, name
    assert sorted(a["parent"] for a in _assumed(scene, "door_handles")) == doors, name
    assert sorted(a["parent"] for a in _assumed(scene, "skirting")) == skirting, name
    assert sorted(a["parent"] for a in _assumed(scene, "dim_room_light")) == lights, name
    building_path = V.resolve_repo_path(scene["building"])
    if building_path is None or not building_path.is_file():
        building_path = OUTPUTS / name / "building_final.json"
    building = json.loads(building_path.read_text(encoding="utf-8"))
    rooms = {r["id"]: r for r in building["rooms"]}
    assert all(rooms[p]["room_type"] not in NO_SKIRTING_TYPES for p in skirting), name
    ids = {e["id"] for key in ("walls", "openings", "rooms", "furniture") for e in building.get(key) or []}
    details = [o for o in scene["objects"] if o.get("parent")]
    assert not {o["name"] for o in details} & ids and not {o["wenart_id"] for o in details if o["kind"] == "wall"} & ids
    print(f"{name}: {len(beds)} bedding sets, {len(counters)} counter fronts, {len(doors)} handle pairs, "
          f"{len(skirting)} skirting runs, {len(lights)} dim-room lights")
