"""Fix round after P4a (17 Oct 2026): the replayed cameras and the agent's cameras in a full run's outputs.

Run on the pod after the renders (``pytest -m gpu tests/gpu/test_camera_replay.py``; the scheduler's "full" group,
``RENDER_TEST_PROJECTS``), on the manifests under ``$WENART_OUTPUTS`` (default /workspace/repo/outputs) as
tests/gpu/test_render.py reads them. CPU twin: tests/test_m13_camera_replay.py.

- ``test_one_camera_per_name_and_a_plan_per_render``: the scene manifest names every camera once, the render
  manifest renders exactly the scene's cameras and no name carries Blender's ``.NNN`` suffix (P4a: two records named
  ``ext_6`` and a render of ``ext_6.001`` that no plan described).
- ``test_replayed_cameras_follow_the_camera_file``: with ``--cameras-from`` (the scene manifest's ``cameras_from``),
  every record of the camera file is a replayed camera of the scene (its pose and lens unchanged, or the build's
  re-pitch with ``replay``), a camera the agent moved (``cameras_from.agent_replaced``) or a dropped record with its
  reason; ``replayed`` + ``searched`` count the scene's cameras.
- ``test_agent_cameras_record_their_pose``: every camera that replaces a replayed record has ``policy: agent``,
  ``source: searched`` and the replaced record (``replaced_replayed``); an agent exterior camera's ``view`` matches
  its own pose (``build.agent_exterior_view`` changes nothing: P4a's corner pose was recorded as the frontal view of
  the back facade).
"""
from __future__ import annotations

import copy
import json
import math
import os
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("RENDER_TEST_PROJECTS", "synthetic-01 synthetic-03").split() if p]
BLENDER_SUFFIX = re.compile(r"\.\d{3}$")
POSE_TOLERANCE_M = 1e-4


def _load(project: str, name: str) -> dict:
    path = OUTPUTS / project / name
    assert path.exists(), f"{path} missing: did the job run the build/render stages for {project}?"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    return (request.param, _load(request.param, "scene/scene_manifest.json"),
            _load(request.param, "renders/render_manifest.json"))


def _camera_file(name: str, scene: dict) -> dict | None:
    """The camera file of ``--cameras-from`` as the build read it (its sha256 checked), else None."""
    import hashlib

    from wenart import views

    cf = scene.get("cameras_from") or {}
    if not cf.get("path") or cf.get("missing"):
        return None
    path = views._resolve_repo_path(cf["path"], OUTPUTS / name)
    if path is None or not path.is_file():
        return None
    data = path.read_bytes()
    if cf.get("sha256") and hashlib.sha256(data).hexdigest() != cf["sha256"]:
        return None
    return json.loads(data.decode("utf-8"))


def test_one_camera_per_name_and_a_plan_per_render(project):
    name, scene, render = project
    names = [c["name"] for c in scene.get("cameras") or []]
    twice = sorted({n for n in names if names.count(n) > 1})
    assert not twice, f"{name}: camera names used twice in the scene manifest: {twice}"
    rendered = [r["camera"] for r in render["renders"]]
    assert len(set(rendered)) == len(rendered), f"{name}: a camera rendered twice"
    assert set(rendered) == set(names), (f"{name}: renders without a scene camera {sorted(set(rendered) - set(names))},"
                                         f" scene cameras without a render {sorted(set(names) - set(rendered))}")
    suffixed = sorted(n for n in set(names) | set(rendered) if BLENDER_SUFFIX.search(n))
    assert not suffixed, f"{name}: Blender renamed camera objects: {suffixed}"


def test_replayed_cameras_follow_the_camera_file(project):
    from wenart.blender import cameras as CA

    name, scene, _render = project
    cf = scene.get("cameras_from")
    if not cf:
        pytest.skip(f"{name}: built without --cameras-from")
    cams = scene["cameras"]
    assert cf["replayed"] + cf["searched"] == len(cams), f"{name}: cameras_from counts {cf} vs {len(cams)} cameras"
    data = _camera_file(name, scene)
    if data is None:
        pytest.skip(f"{name}: the camera file {cf.get('path')} is not readable here (or its sha256 changed)")
    by = {c["name"]: c for c in cams}
    agent_replaced = set(cf.get("agent_replaced") or [])
    dropped = {d["name"]: d.get("reason") for d in cf.get("dropped") or [] if d.get("name")}
    bad = []
    for rec in CA.replay_cameras(data)["plans"]:
        n = rec["name"]
        cam = by.get(n)
        if n in dropped:
            if not dropped[n]:
                bad.append((n, "dropped without a reason"))
            continue
        if cam is None:
            bad.append((n, "a record of the camera file is neither in the scene nor dropped"))
        elif n in agent_replaced:
            old = cam.get("replaced_replayed")
            if not isinstance(old, dict) or (old.get("replayed_from") or {}).get("build_fingerprint") \
                    != data.get("build_fingerprint"):
                bad.append((n, "moved by the agent without the replayed record of this camera file"))
        elif cam.get("source") != "replayed":
            bad.append((n, f"source {cam.get('source')} for a replayed record"))
        elif (cam.get("replay") or {}).get("status") != "repitched":
            moved = max(abs(float(a) - float(b)) for a, b in zip(cam["position"], rec["position"]))
            if moved > POSE_TOLERANCE_M or abs(float(cam["lens_mm"]) - rec["lens_mm"]) > 1e-6:
                bad.append((n, f"pose or lens changed ({moved:.4f} m)"))
    assert not bad, f"{name}: replayed cameras that do not follow the camera file: {bad}"


def test_agent_cameras_record_their_pose(project):
    from wenart.blender import build as B
    from wenart.blender import site as S

    name, scene, _render = project
    agent = [c for c in scene.get("cameras") or [] if c.get("policy") == "agent" and c.get("source") != "replayed"]
    if not agent:
        pytest.skip(f"{name}: no agent camera")
    north, src = S.north_deg(_building(name, scene))
    known = not src.startswith("assumed")
    bad = []
    for c in agent:
        if c.get("source") != "searched":
            bad.append((c["name"], f"source {c.get('source')}"))
        if c.get("replaced_replayed") is not None and not isinstance(c["replaced_replayed"].get("position"), list):
            bad.append((c["name"], "replaced_replayed without the old pose"))
        if c.get("kind") == "exterior" and c.get("sides"):
            probe = copy.deepcopy(c)
            change = B.agent_exterior_view(probe, (math.nan, math.nan), north, known)
            if change is not None:
                bad.append((c["name"], f"view {c.get('view')} of {c.get('sides')} does not match its pose"))
    replaced = sorted(c["name"] for c in agent if c.get("replaced_replayed") is not None)
    if scene.get("cameras_from"):
        assert sorted(scene["cameras_from"].get("agent_replaced") or []) == replaced, f"{name}: agent_replaced"
    print(f"{name}: agent cameras {sorted(c['name'] for c in agent)}; over replayed ones {replaced}")
    assert not bad, f"{name}: agent cameras with an inconsistent record: {bad}"


def _building(name: str, scene: dict) -> dict:
    from wenart import views

    path = views._resolve_repo_path(scene.get("building"), OUTPUTS / name)
    if path is None or not path.is_file():
        path = OUTPUTS / name / "building_final.json"
    assert path.is_file(), f"{name}: building JSON of the scene not found ({scene.get('building')})"
    return json.loads(path.read_text(encoding="utf-8"))
