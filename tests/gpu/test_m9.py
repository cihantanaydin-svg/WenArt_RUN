"""Milestone 9 GPU tests (docs/milestone9.md §4, §5, §8): run on the pod by the full run after the renders and the
3D export (pytest -m gpu tests/gpu/test_m9.py), for the projects in $RENDER_TEST_PROJECTS under $WENART_OUTPUTS:

- AI decor: every room the AI decor asked about ended with AI items or with the rule decor and its reason
  (``decor_ai.json``); every AI item carries both passes as evidence, confidence 0.9, its slot, and was built in
  the scene (or is listed under the summary's ``decor_skipped`` with the reason); a project with decor questions
  has AI decor in at least one room;
- surface decor (vases, bowls, small plants, table lamps, AI books) rests on its host: its bottom lies on the host's
  built box, not on the floor and not above the host;
- Milestone 10 variants (docs/milestone10.md §1.6): an alternative's levels are built only in its own scene
  (``variants/<id>/scene``), so both decor checks run on every variant's scene, the built-decor check on the decor
  of the levels that scene builds, and every AI item must be on a level some variant scene builds;
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


def _variant_scenes(project: str, building: dict) -> list[tuple[str, dict]]:
    """``(variant id, scene manifest)`` of every variant of the building: the base is the project's own scene, an
    alternative's is in its sub-output ``variants/<id>/`` (the scheduler's rule: every id but ``base``,
    ``building.alternative_ids``); a building without ``variants`` has one base variant (the M9 projects)."""
    from wenart import views as VW

    out = []
    for v in VW.building_variants(building):
        folder = "" if v["id"] == "base" else f"variants/{v['id']}/"
        out.append((v["id"], _need(project, f"{folder}scene/scene_manifest.json")))
    return out


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
    ai = [d for d in building.get("decor") or [] if d.get("method") == "ai"]
    covered = set()
    for vid, scene in _variant_scenes(project, building):
        levels = {lv["id"] for lv in scene["levels"]}
        built = {o["element_id"] for o in scene["objects"] if o.get("kind") == "decor" and o.get("host_id") is None}
        hosted = [o for o in scene["objects"] if o.get("kind") == "decor" and o.get("host_id")]
        skipped = {s.get("id") for s in (scene.get("furniture") or {}).get("decor_skipped") or []}
        # M11 pod G2d: decor the build leaves out with a reason (a light under a very low slope, a plant taller than
        # the attic ceiling: build.decor_under_roof) is listed in furniture.not_built
        skipped |= {s.get("id") for s in (scene.get("furniture") or {}).get("not_built") or []}
        for item in ai:
            if item.get("level_id") not in levels:
                continue                    # a level only another variant builds (real02's L-1b is not in the base)
            covered.add(item["id"])
            if item.get("host_id"):
                assert any(o["host_id"] == item["host_id"] and o["type"] == item["type"] for o in hosted) or \
                    item["id"] in skipped, (vid, item["id"])
            else:
                assert item["id"] in built or item["id"] in skipped, (vid, item["id"])
        for o in scene["objects"]:
            if o.get("kind") == "decor" and o.get("decor_method") == "ai":
                assert [e.get("pass") for e in o["evidence"]] == [1, 2], (vid, o["name"])
    missing = sorted({d["id"] for d in ai} - covered)
    assert not missing, f"{project}: AI decor on no level a variant scene builds: {missing}"


@pytest.mark.parametrize("project", PROJECTS)
def test_surface_decor_rests_on_its_host(project):
    building = _need(project, "building_final.json")
    for vid, scene in _variant_scenes(project, building):
        by_id = {o["element_id"]: o for o in scene["objects"] if o.get("kind") in ("furniture", "furniture_proxy")}
        checked = 0
        for o in scene["objects"]:
            if o.get("kind") != "decor" or o.get("type") not in SURFACE or not o.get("host_id"):
                continue
            host = by_id.get(o["host_id"])
            assert host is not None, (vid, o["name"])
            bottom = float(o["center"][2]) - float(o["size"][2]) / 2.0
            host_bottom = float(host["center"][2]) - float(host["size"][2]) / 2.0
            host_top = host_bottom + float((host.get("bbox_m") or host["size"])[2])
            assert host_bottom + 0.15 <= bottom <= host_top + 0.01, (vid, o["name"], bottom, host_bottom, host_top)
            checked += 1
        print(f"{project} ({vid}): {checked} surface decor items on their hosts")


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
