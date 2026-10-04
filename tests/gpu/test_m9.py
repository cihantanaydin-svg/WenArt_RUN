"""Milestone 9 GPU tests (docs/milestone9.md §4, §5, §8): run on the pod by the full run after the renders and the
3D export (pytest -m gpu tests/gpu/test_m9.py), for the projects in $RENDER_TEST_PROJECTS under $WENART_OUTPUTS:

- AI decor: every room the AI decor asked about ended with AI items or with the rule decor and its reason
  (``decor_ai.json``); every AI item carries both passes as evidence, confidence 0.9, its slot, and was built in
  the scene (or is listed under the summary's ``decor_skipped`` with the reason); a project with decor questions
  has AI decor in at least one room;
- surface decor (vases, bowls, small plants, table lamps, AI books) rests on its host: its bottom lies on the host's
  built box, not on the floor and not above the host;
- the 3D files: ``export/<p>.blend`` and ``export/<p>.glb`` exist with the sha256 of ``export_manifest.json``, every
  image of the .blend is packed, every rendered camera is in the file with its metered exposure.
"""
import hashlib
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("RENDER_TEST_PROJECTS", "").split() if p]
SURFACE = ("vase", "bowl", "plant_small", "table_lamp")


def _load(project: str, name: str):
    path = OUTPUTS / project / name
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _need(project: str, name: str) -> dict:
    doc = _load(project, name)
    assert doc is not None, f"{OUTPUTS / project / name} missing"
    return doc


@pytest.mark.parametrize("project", PROJECTS)
def test_ai_decor_records_every_room_and_both_passes(project):
    summary = _load(project, "decor_ai.json")
    if summary is None:
        pytest.skip(f"{project}: no AI decor summary (brief decor off or rules)")
    rooms = summary["rooms"]
    asked = [r for r in rooms if r.get("slots")]
    for r in rooms:
        assert r["items"] or r["fallback"] or not r["slots"], r["room_id"]
        if r["fallback"]:
            assert isinstance(r["fallback"], str) and r["fallback"], r["room_id"]
    if asked:
        assert summary["rooms_ai"] >= 1, f"{project}: the AI decor kept no item in any of {len(asked)} rooms"
    building = _need(project, "building_final.json")
    for item in building.get("decor") or []:
        if item.get("method") != "ai":
            continue
        assert [e["pass"] for e in item["evidence"]] == [1, 2] and item["confidence"] == 0.9, item["id"]
        assert all(e["method"] == "ai" for e in item["evidence"]) and item["slot"], item["id"]
        assert item["source"] == "added_by_ai" and item["kind"] == "decor", item["id"]


@pytest.mark.parametrize("project", PROJECTS)
def test_ai_decor_is_built(project):
    building = _need(project, "building_final.json")
    scene = _need(project, "scene/scene_manifest.json")
    built = {o["element_id"] if o.get("host_id") is None else None for o in scene["objects"] if o.get("kind") == "decor"}
    hosted = [o for o in scene["objects"] if o.get("kind") == "decor" and o.get("host_id")]
    skipped = {s.get("id") for s in (scene.get("furniture") or {}).get("decor_skipped") or []}
    for item in building.get("decor") or []:
        if item.get("method") != "ai":
            continue
        if item.get("host_id"):
            assert any(o["host_id"] == item["host_id"] and o["type"] == item["type"] for o in hosted) or \
                item["id"] in skipped, item["id"]
        else:
            assert item["id"] in built or item["id"] in skipped, item["id"]
    for o in scene["objects"]:
        if o.get("kind") == "decor" and o.get("decor_method") == "ai":
            assert [e.get("pass") for e in o["evidence"]] == [1, 2], o["name"]


@pytest.mark.parametrize("project", PROJECTS)
def test_surface_decor_rests_on_its_host(project):
    scene = _need(project, "scene/scene_manifest.json")
    by_id = {o["element_id"]: o for o in scene["objects"] if o.get("kind") in ("furniture", "furniture_proxy")}
    checked = 0
    for o in scene["objects"]:
        if o.get("kind") != "decor" or o.get("type") not in SURFACE or not o.get("host_id"):
            continue
        host = by_id.get(o["host_id"])
        assert host is not None, o["name"]
        bottom = float(o["center"][2]) - float(o["size"][2]) / 2.0
        host_bottom = float(host["center"][2]) - float(host["size"][2]) / 2.0
        host_top = host_bottom + float((host.get("bbox_m") or host["size"])[2])
        assert host_bottom + 0.15 <= bottom <= host_top + 0.01, (o["name"], bottom, host_bottom, host_top)
        checked += 1
    print(f"{project}: {checked} surface decor items on their hosts")


@pytest.mark.parametrize("project", PROJECTS)
def test_3d_files_are_packed_and_complete(project):
    doc = _need(project, "export/export_manifest.json")
    for kind in ("blend", "glb"):
        entry = doc["files"][kind]
        assert not entry.get("missing"), f"{project}: {entry['file']} missing"
        path = OUTPUTS / project / "export" / entry["file"]
        assert path.stat().st_size == entry["bytes"] > 0
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    assert all(img["packed"] for img in doc["images"]), [i["name"] for i in doc["images"] if not i["packed"]]
    renders = _need(project, "renders/render_manifest.json")
    cams = {r["camera"] for r in renders["renders"]}
    assert cams <= set(doc["cameras"]), sorted(cams - set(doc["cameras"]))
    assert all("ev" in doc["cameras"][c] for c in cams)
    print(f"{project}: {doc['files']['blend']['bytes'] / 2**20:.1f} MB .blend, "
          f"{doc['files']['glb']['bytes'] / 2**20:.1f} MB .glb, {doc['images_scaled']} images scaled")
