"""Fix round after P4a (17 Oct 2026): the agent's cameras over the replayed cameras of ``--cameras-from``.

What: CPU tests of ``build.merge_agent_cameras`` (the replayed and the planned cameras merged first, then the agent's
entries applied, inside and outside), ``overrides.replaced_replayed_of`` (the replayed record a set keeps on file),
``build.agent_exterior_view`` / ``finish_agent_exterior_plans`` (the view of an agent exterior camera follows its own
pose), ``build.dedupe_camera_names`` and ``build.check_camera_objects`` (never two cameras with one name) and the
``cameras_from`` summary (``agent``, ``agent_replaced``, the agent's removals in ``dropped``). The last test builds
the example building twice in Blender (WENART_BLENDER): once to get a scene manifest, once with ``--cameras-from``
it and agent entries on a replayed exterior and interior camera.
Why: pod P4a (real02, the M11 cameras replayed): the agent's three ``set ext_6`` were applied to the empty planned
exterior set, ``ext_6`` was added a second time and Blender named the object ``ext_6.001``; the agent's move never
reached the view it judged, X6 stayed every round, two GPU tests failed on the unknown name and the corner pose was
recorded as the frontal view of the back facade. Every test fails on commit 03881bc (or on the mutation named in
its docstring).
How: P4a's replayed exterior records and agent entries (``runs/20261017-072801-full/results``, not committed) copied
below; small hand-made inputs; no Blender but in the last test.
"""
from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest

from wenart.blender import build as B
from wenart.blender import cameras as CA
from wenart.blender import cli
from wenart.blender import exterior_checks as X
from wenart.blender import overrides as O
from wenart.blender import schemas

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")

P4A_FINGERPRINT = "e3ae6cf09c9d49a9a4ce07632a22fda0eae633bad3f5adfd1b4c12792e2456f8"


def _ext(name, index, view, sides, position, target):
    return {"name": name, "kind": "exterior", "room_id": None, "level_id": None, "index": index, "view": view,
            "sides": sides, "position": position, "target": target, "lens_mm": 26.0, "sensor_mm": 36.0,
            "resolution": [1920, 1080], "shift_x": 0.0, "shift_y": 0.0, "variant": "base", "region_id": None,
            "dropped_reason": None, "visible_openings": [], "visible_furniture": [], "warning": None,
            "placement": "12.5 m from the building corner"}


# P4a's replayed exterior set (scene_manifest.json of runs/20261017-072801-full/results/renders/real02, from M11)
P4A_EXT = [_ext("ext_1", 1, "corner", ["left", "front"], [-6.3495, -10.8243, 1.6], [1.5159, -1.1091, 1.6]),
           _ext("ext_2", 2, "corner", ["right", "front"], [21.5225, -10.8243, 1.6], [13.6571, -1.1091, 1.6]),
           _ext("ext_3", 3, "corner", ["right", "back"], [21.5225, 22.8263, 1.6], [13.6571, 13.1111, 1.6]),
           _ext("ext_4", 4, "corner", ["left", "back"], [-6.3495, 22.8263, 1.6], [1.5159, 13.1111, 1.6]),
           _ext("ext_5", 5, "aerial", ["left", "front"], [-14.3356, -11.2061, 9.6339], [7.1726, 6.517, 1.8195]),
           _ext("ext_6", 6, "frontal", ["back"], [7.5865, 29.501, 1.6], [7.5865, 12.001, 1.6])]
# P4a's accepted set_camera edits (orchestrator/overrides.json seq 15, 23, 25) as agent_overrides.agent_overrides
# writes them (wenart/agent/overrides.py)
P4A_ENTRIES = [
    {"action": "set", "view_id": "ext_6", "kind": "exterior", "position": [18.5, 24.0, 1.6], "target": [7.5865, 6.0, 1.6],
     "lens_mm": 26, "reason": "Reposition ext_6 from a direct frontal single-facade shot to a 3/4 corner view", "seq": 15},
    {"action": "set", "view_id": "ext_6", "kind": "exterior", "position": [24.0, 22.0, 1.6], "target": [7.5865, 6.0, 1.6],
     "lens_mm": 26, "reason": "Move ext_6 from a direct frontal angle to a 3/4 corner position", "seq": 23},
    {"action": "set", "view_id": "ext_6", "kind": "exterior", "position": [24.0, 22.0, 1.6], "target": [7.5865, 6.0, 1.6],
     "lens_mm": 26, "reason": "Move to a 3/4 corner angle so two facades are visible", "seq": 25}]
# the bounding-box centre of real02's outline (the corner targets span x 1.52-13.66, y -1.11-13.11)
P4A_CENTRE = (7.5865, 6.001)


def _replay(records):
    return CA.replay_cameras({"cameras": copy.deepcopy(records), "build_fingerprint": P4A_FINGERPRINT,
                              "camera_policy": "search"})


def test_p4a_set_on_a_replayed_exterior_camera_replaces_it():
    """P4a's three ``set ext_6`` over the replayed ext_1..6 give six cameras with six names, results ``replaced``
    three times; ext_6 is the agent's pose (``policy: agent``, ``source: searched``: the frozen sources) and keeps
    the replayed record in ``replaced_replayed``; every record validates against ``schemas.SCENE_CAMERA``.
    Mutation: applying the entries before the merge (the order of 03881bc) gives two ext_6 and ``added`` first."""
    replay = _replay(P4A_EXT)
    plans, applied = B.merge_agent_cameras(replay["plans"], [], P4A_ENTRIES, replay=replay)
    names = [p["name"] for p in plans]
    assert names == ["ext_1", "ext_2", "ext_3", "ext_4", "ext_5", "ext_6"] and len(set(names)) == 6
    assert [a["result"] for a in applied] == ["replaced"] * 3
    assert [a["seq"] for a in applied] == [15, 23, 25] and all(a["replayed"] for a in applied)
    ext6 = plans[-1]
    assert ext6["policy"] == "agent" and ext6["source"] == "searched" and ext6["position"] == [24.0, 22.0, 1.6]
    old = ext6["replaced_replayed"]
    assert old["position"] == [7.5865, 29.501, 1.6] and old["target"] == [7.5865, 12.001, 1.6]
    assert old["view"] == "frontal" and old["sides"] == ["back"] and old["lens_mm"] == 26.0
    assert old["replayed_from"]["build_fingerprint"] == P4A_FINGERPRINT
    assert all(p["source"] == "replayed" and "replaced_replayed" not in p for p in plans[:5])
    assert replay["dropped"] == []
    B.finish_agent_exterior_plans(plans, "base", P4A_CENTRE)
    for p in plans:
        jsonschema.validate(p, schemas.SCENE_CAMERA)
        assert p["source"] in schemas.CAMERA_SOURCES == ("searched", "replayed")


def test_the_build_merges_before_it_applies_the_agent_entries():
    """The build's two camera paths call ``merge_agent_cameras`` with the replayed and the planned cameras and no
    longer put the replayed ones in front afterwards (03881bc: ``plans = replayed + plans`` and ``ext_plans =
    ext_replayed + ext_plans`` after ``apply_cameras``). The Blender test below runs the real build."""
    src = inspect.getsource(B.main)
    assert "merge_agent_cameras(replayed, plans, entries" in src
    assert "merge_agent_cameras(ext_replayed, ext_plans, entries" in src
    assert "replayed + plans" not in src and "ext_replayed + ext_plans" not in src
    assert src.count("dedupe_camera_names(") == 2 and src.count("check_camera_objects(") == 2


def test_agent_corner_pose_is_not_recorded_as_the_frontal_view():
    """P4a's agent ext_6 stands at a corner ([24, 22] aimed at [7.59, 6.0], 45.7 degrees off the back facade's
    normal): its view is ``agent`` with the side of its nearest axis (``right``), the agent record keeps
    ``view_was`` / ``sides_was``, a log line says so, and exterior_checks no longer counts it as the frontal view
    (``_faces`` on the back facade is false, so X6 can report a lost entrance view). A lens-only set keeps
    ``frontal``. Mutation: without ``agent_exterior_view`` the plan stays "frontal, back" (fixed_plan's copy)."""
    replay = _replay(P4A_EXT)
    plans, _ = B.merge_agent_cameras(replay["plans"], [], P4A_ENTRIES, replay=replay)
    lines = B.finish_agent_exterior_plans(plans, "base", P4A_CENTRE)
    ext6 = plans[-1]
    assert ext6["view"] == "agent" and ext6["sides"] == ["right"]
    assert ext6["agent"]["view_was"] == "frontal" and ext6["agent"]["sides_was"] == ["back"]
    assert ext6["index"] == 6 and ext6["variant"] == "base"
    assert lines == ["ext_6: the agent's pose is no longer the frontal view of back; recorded as view agent (right)"]
    assert not X._faces(ext6, (0.0, 1.0))
    # the same pose with only a new lens stays the frontal view of the entrance
    lens_only = [dict(P4A_ENTRIES[0], position=[7.5865, 29.501, 1.6], target=[7.5865, 12.001, 1.6], lens_mm=24.0)]
    replay = _replay(P4A_EXT)
    plans, _ = B.merge_agent_cameras(replay["plans"], [], lens_only, replay=replay)
    assert B.finish_agent_exterior_plans(plans, "base", P4A_CENTRE) == []
    assert plans[-1]["view"] == "frontal" and plans[-1]["sides"] == ["back"] and plans[-1]["lens_mm"] == 24.0
    assert "view_was" not in plans[-1]["agent"]


@pytest.mark.parametrize("name,position,target,view", [
    ("ext_1", [-7.0, -12.0, 1.6], [1.5159, -1.1091, 1.6], "corner"),      # a step back: still both facades
    ("ext_1", [1.5159, -14.0, 1.6], [1.5159, -1.1091, 1.6], "agent"),     # square to the front: no left facade
    ("ext_5", [-16.0, -13.0, 12.0], [7.1726, 6.517, 1.8195], "aerial"),   # higher: still an aerial
    ("ext_5", [-16.0, -13.0, 1.6], [7.1726, 6.517, 1.6], "agent"),        # down to eye level: no aerial
])
def test_agent_view_follows_the_pose(name, position, target, view):
    """A corner pose that still looks at both of its facades stays ``corner``; one square to a single facade becomes
    ``agent``. An aerial that still looks down stays ``aerial``; one brought to eye level becomes ``agent``."""
    replay = _replay(P4A_EXT)
    entry = {"action": "set", "view_id": name, "kind": "exterior", "position": position, "target": target,
             "reason": "test", "seq": 1}
    plans, _ = B.merge_agent_cameras(replay["plans"], [], [entry], replay=replay)
    B.finish_agent_exterior_plans(plans, "base", P4A_CENTRE)
    plan = next(p for p in plans if p["name"] == name)
    assert plan["view"] == view and plan["sides"]


def test_remove_of_a_replayed_camera_is_dropped_with_the_agent_reason():
    """A ``remove`` of a replayed camera now removes it (03881bc: ``not found`` on the empty planned set, the
    camera stayed) and lists it in ``cameras_from.dropped`` with the agent's reason and seq, so
    ``unused_replayed`` gives no false reason ("the build has no exterior views") for it."""
    replay = _replay(P4A_EXT)
    entries = [{"action": "remove", "view_id": "ext_2", "kind": "exterior", "reason": "a near-duplicate of ext_1",
                "seq": 7}]
    plans, applied = B.merge_agent_cameras(replay["plans"], [], entries, replay=replay)
    assert [p["name"] for p in plans] == ["ext_1", "ext_3", "ext_4", "ext_5", "ext_6"]
    assert applied == [{"view_id": "ext_2", "action": "remove", "kind": "exterior", "reason": "a near-duplicate of ext_1",
                        "seq": 7, "replayed": True, "result": "removed"}]
    assert replay["dropped"] == [{"name": "ext_2",
                                  "reason": "removed by the agent (overrides seq 7): a near-duplicate of ext_1"}]
    assert B.unused_replayed(replay["plans"], plans, replay["dropped"]) == []
    # a set and then a remove of the same replayed name: still the replayed record the agent removed
    replay = _replay(P4A_EXT)
    entries = [P4A_ENTRIES[1], dict(entries[0], view_id="ext_6", seq=26)]
    plans, applied = B.merge_agent_cameras(replay["plans"], [], entries, replay=replay)
    assert "ext_6" not in [p["name"] for p in plans] and [d["name"] for d in replay["dropped"]] == ["ext_6"]


def test_interior_set_on_a_replayed_camera_replaces_it():
    """Inside the same: a ``set`` on a replayed room camera replaces it (``replaced_replayed`` with the M11 pose), an
    ``add`` in that room takes the next free index (the replayed cameras count), a searched camera of another room
    stays, every record validates. Mutation: the 03881bc order gives two ``cam_r_L0_salon_2`` and index 1 for the
    added one."""
    def cam(name, room, index, pos):
        return {"name": name, "room_id": room, "level_id": "L0", "index": index, "position": pos,
                "target": [pos[0] + 1.0, pos[1], 1.3], "lens_mm": 24.0, "sensor_mm": 36.0, "resolution": [1920, 1080],
                "policy": "search", "kind": "interior", "visible_openings": [], "visible_furniture": [], "warning": None}
    replay = _replay([cam("cam_r_L0_salon_1", "r_L0_salon", 1, [1.0, 1.0, 1.4]),
                      cam("cam_r_L0_salon_2", "r_L0_salon", 2, [2.0, 3.0, 1.4])])
    searched = [dict(cam("cam_r_L0_banyo_1", "r_L0_banyo", 1, [8.0, 1.0, 1.4]), source="searched", lens_mm=16.0)]
    entries = [{"action": "set", "view_id": "cam_r_L0_salon_2", "kind": "interior", "room_id": "r_L0_salon",
                "position": [2.5, 3.5, 1.4], "target": [4.0, 3.5, 1.3], "reason": "show the sofa", "seq": 3},
               {"action": "add", "view_id": "cam_r_L0_salon_9", "kind": "interior", "room_id": "r_L0_salon",
                "position": [3.0, 1.0, 1.4], "target": [3.0, 3.0, 1.3], "reason": "the window", "seq": 4}]
    plans, applied = B.merge_agent_cameras(replay["plans"], searched, entries, "L0", {"r_L0_salon", "r_L0_banyo"},
                                           replay)
    names = [p["name"] for p in plans]
    assert names == ["cam_r_L0_salon_1", "cam_r_L0_salon_2", "cam_r_L0_banyo_1", "cam_r_L0_salon_9"]
    assert [a["result"] for a in applied] == ["replaced", "added"] and applied[0]["replayed"] is True
    assert "replayed" not in applied[1]
    moved = plans[1]
    assert moved["policy"] == "agent" and moved["source"] == "searched" and moved["index"] == 2
    assert moved["replaced_replayed"]["position"] == [2.0, 3.0, 1.4] and moved["replaced_replayed"]["lens_mm"] == 24.0
    assert plans[3]["index"] == 3 and plans[3]["source"] == "searched" and "replaced_replayed" not in plans[3]
    assert plans[0]["source"] == "replayed" and plans[2]["source"] == "searched"
    for p in plans:
        jsonschema.validate(B.interior_camera_fields(p, "base"), schemas.SCENE_CAMERA)


def test_merge_without_entries_or_replay_is_the_old_order():
    """No replay and no entries (synthetic projects, real04): the planned list as it was; entries without a replay:
    ``apply_cameras`` on the planned list, as before the fix."""
    planned = [{"name": "ext_1", "source": "searched"}, {"name": "ext_2", "source": "searched"}]
    plans, applied = B.merge_agent_cameras([], planned, [])
    assert plans == planned and applied == []
    entries = [{"action": "set", "view_id": "ext_2", "kind": "exterior", "position": [0, -9, 1.6],
                "target": [0, 0, 1.6], "reason": "x"}]
    assert B.merge_agent_cameras([], copy.deepcopy(planned), entries)[1] == O.apply_cameras(planned, entries)[1]


def test_never_two_cameras_with_one_name():
    """``dedupe_camera_names`` renames a clash ``<name>_dup<k>`` with ``renamed_from`` and one log line (against
    the build's earlier cameras and earlier plans of the list); ``check_camera_objects`` stops the build when
    Blender renamed an object (P4a: ``ext_6.001``)."""
    plans = [{"name": "ext_6", "source": "replayed"}, {"name": "ext_6", "policy": "agent"},
             {"name": "ext_6", "policy": "agent"}, {"name": "cam_r_1", "source": "searched"}]
    lines = B.dedupe_camera_names(plans, {"cam_r_1"})
    assert [p["name"] for p in plans] == ["ext_6", "ext_6_dup2", "ext_6_dup3", "cam_r_1_dup2"]
    assert plans[1]["renamed_from"] == "ext_6" and "renamed_from" not in plans[0]
    assert lines[0] == "ext_6: a second camera of this name (agent) renamed ext_6_dup2; never two cameras with one name"
    assert len(lines) == 3
    assert B.dedupe_camera_names([{"name": "a"}, {"name": "b"}], {"c"}) == []
    ok = [{"name": "ext_6"}]
    B.check_camera_objects([SimpleNamespace(name="ext_6")], ok)
    with pytest.raises(RuntimeError, match=r"ext_6 -> ext_6\.001"):
        B.check_camera_objects([SimpleNamespace(name="ext_6"), SimpleNamespace(name="ext_6.001")],
                               [{"name": "ext_6"}, {"name": "ext_6"}])
    with pytest.raises(RuntimeError, match="1 camera objects"):
        B.check_camera_objects([SimpleNamespace(name="ext_6")], [{"name": "ext_6"}, {"name": "ext_7"}])


def test_finish_agent_plans_index_stays_valid():
    """The index of an agent camera comes from its name's number, else its own (at least 1): 03881bc gave
    ``ext_6_s`` index 0 (under the schema's minimum) and raised ValueError on ``ext_front_2``."""
    plans = [{"name": "ext_6_s", "policy": "agent", "source": "searched", "index": 6, "position": [20.0, 0.0, 1.6],
              "target": [0.0, 0.0, 1.6], "view": "agent", "sides": []},
             {"name": "ext_front_2", "policy": "agent", "source": "searched", "index": 1,
              "position": [0.0, -20.0, 1.6], "target": [0.0, 0.0, 1.6], "view": "agent", "sides": []},
             {"name": "ext_3", "source": "replayed", "policy": "agent", "index": 3, "position": [0.0, 20.0, 1.6],
              "target": [0.0, 0.0, 1.6], "view": "corner", "sides": ["back"]}]
    B.finish_agent_exterior_plans(plans, "v1", (0.0, 0.0), visible=lambda p: ["w_1"])
    assert [p["index"] for p in plans] == [6, 2, 3]
    assert plans[0]["sides"] == ["right"] and plans[1]["sides"] == ["front"] and plans[0]["visible_openings"] == ["w_1"]
    assert "variant" not in plans[2] and plans[2]["view"] == "corner"     # a replayed M11 agent record is untouched


def test_cameras_from_summary_names_the_agent_cameras():
    """``cameras_from`` lists this build's agent cameras (``agent``) and those that replace a replayed record
    (``agent_replaced``); ``searched`` still counts every camera that is not replayed; it validates."""
    replay = _replay(P4A_EXT)
    plans, _ = B.merge_agent_cameras(replay["plans"], [], P4A_ENTRIES, replay=replay)
    plans.append({"name": "ext_9", "policy": "agent", "source": "searched"})
    plans.append({"name": "cam_r_1", "policy": "agent", "source": "replayed"})      # an M11 agent camera, replayed
    record = {"path": "results/renders/real02/scene_manifest.json", "sha256": "0" * 64, "cameras": 41}
    out = B.cameras_from_summary(record, replay, plans, False)
    assert out["agent"] == ["ext_6", "ext_9"] and out["agent_replaced"] == ["ext_6"]
    assert out["replayed"] == 6 and out["searched"] == 2
    jsonschema.validate(out, schemas.CAMERAS_FROM)


def test_the_schemas_type_the_new_camera_keys():
    """Integration of the fix round after P4a (C_cameras' schema ask): ``replaced_replayed`` and ``renamed_from`` of a
    scene camera and ``cameras_from.agent`` / ``agent_replaced`` are typed in the schemas; the records the build
    writes validate, a wrong type does not (on the schemas of 03881bc the wrong types validate)."""
    replay = _replay(P4A_EXT)
    plans, _ = B.merge_agent_cameras(replay["plans"], [], P4A_ENTRIES, replay=replay)
    B.finish_agent_exterior_plans(plans, "base", P4A_CENTRE)
    ext6 = plans[-1]
    for key in ("replaced_replayed", "renamed_from"):
        assert key in schemas.SCENE_CAMERA["properties"], key
    jsonschema.validate(ext6, schemas.SCENE_CAMERA)
    jsonschema.validate(dict(ext6, renamed_from="ext_6"), schemas.SCENE_CAMERA)
    for bad in (dict(ext6, replaced_replayed="ext_6"), dict(ext6, renamed_from=6),
                dict(ext6, replaced_replayed=dict(ext6["replaced_replayed"], position=[1.0, 2.0]))):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schemas.SCENE_CAMERA)
    record = {"path": "results/renders/real02/scene_manifest.json", "sha256": "0" * 64, "cameras": 41}
    out = B.cameras_from_summary(record, replay, plans, False)
    jsonschema.validate(out, schemas.CAMERAS_FROM)
    for key in ("agent", "agent_replaced"):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(dict(out, **{key: [6]}), schemas.CAMERAS_FROM)


def test_replaced_replayed_of():
    """The record a set keeps: a replayed base's pose, lens, view, sides and provenance; an earlier agent plan's own
    ``replaced_replayed`` (chained sets); nothing for a searched camera or no camera."""
    base = dict(_replay(P4A_EXT)["plans"][4])
    base["replay"] = {"status": "repitched"}
    got = O.replaced_replayed_of(base)
    assert set(got) == {"position", "target", "lens_mm", "shift_x", "shift_y", "view", "sides", "replayed_from",
                        "replay"}
    assert O.replaced_replayed_of({"name": "ext_6", "policy": "agent", "replaced_replayed": got}) == got
    assert O.replaced_replayed_of({"name": "ext_6", "source": "searched"}) is None
    assert O.replaced_replayed_of(None) is None


def _build(building: dict, out: Path, extra: list[str]) -> dict:
    path = out.parent / f"{out.name}_building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--out", str(out), "--no-textures",
                                             "--no-preview", "--no-glb", "--camera-policy", "search"] + extra,
                    log_path=out / "build.log")
    return json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))


@needs_blender
def test_example_build_with_replayed_cameras_and_agent_entries(tmp_path):
    """The real build: the example building built once, then again with ``--cameras-from`` that manifest and the
    agent's entries: a ``set`` on a replayed exterior camera, a ``set`` on a replayed interior camera and a
    ``remove`` of another replayed interior camera. One camera per name (03881bc: two of the exterior name, the
    second an object ``<name>.001``), the moved ones ``policy: agent`` with ``replaced_replayed``, the removed one
    in ``cameras_from.dropped`` with the agent's reason, and the scene manifest validates."""
    building = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    first = _build(copy.deepcopy(building), tmp_path / "first", [])
    ext = [c for c in first["cameras"] if c.get("kind") == "exterior"]
    inside = [c for c in first["cameras"] if c.get("kind") != "exterior"]
    assert ext and len(inside) >= 2
    e, i_set, i_rm = ext[0], inside[0], inside[1]
    ex, ey, ez = e["position"]
    ix, iy, iz = i_set["position"]
    building["agent_overrides"] = {"round": 1, "cameras": [
        {"action": "set", "view_id": e["name"], "kind": "exterior", "position": [ex * 1.1, ey * 1.1, ez],
         "target": e["target"], "lens_mm": 26.0, "reason": "a step back", "seq": 1},
        {"action": "set", "view_id": i_set["name"], "kind": "interior", "room_id": i_set["room_id"],
         "position": [ix, iy, iz], "target": [ix + 1.0, iy + 0.5, 1.3], "reason": "turn to the window", "seq": 2},
        {"action": "remove", "view_id": i_rm["name"], "kind": "interior", "room_id": i_rm["room_id"],
         "reason": "a bare wall", "seq": 3}]}
    second = _build(building, tmp_path / "second", ["--cameras-from", str(tmp_path / "first" / "scene_manifest.json")])
    schemas.validate_scene_manifest(second)
    names = [c["name"] for c in second["cameras"]]
    assert len(names) == len(set(names)) and not any("." in n for n in names), names
    assert sorted(names) == sorted(n for n in (c["name"] for c in first["cameras"]) if n != i_rm["name"])
    by = {c["name"]: c for c in second["cameras"]}
    for name in (e["name"], i_set["name"]):
        assert by[name]["policy"] == "agent" and by[name]["source"] == "searched"
        assert by[name]["replaced_replayed"]["replayed_from"]["build_fingerprint"] == first["build_fingerprint"]
    assert by[e["name"]]["replaced_replayed"]["position"] == e["position"]
    cf = second["cameras_from"]
    assert sorted(cf["agent_replaced"]) == sorted([e["name"], i_set["name"]])
    assert {"name": i_rm["name"], "reason": "removed by the agent (overrides seq 3): a bare wall"} in cf["dropped"]
    assert cf["replayed"] == len(first["cameras"]) - 3 and cf["searched"] == 2
    assert sorted(r["result"] for r in second["agent_overrides"]["cameras"]) == ["removed", "replaced", "replaced"]
    cams = [o for o in second["objects"] if o["kind"] == "camera"]
    assert sorted(o["name"] for o in cams) == sorted(names)
