"""CPU tests of the Milestone 9 GPU test logic with Milestone 10 variants (tests/gpu/test_m9.py).

Milestone 10 builds an alternative's levels only in that alternative's own scene (``variants/<id>/scene``,
docs/milestone10.md §1.6), so the AI decor of an alternative level is never in the base scene. The GPU test module is
imported with its environment pointing at hand-made outputs in tmp_path (the ``_import_gpu_test`` pattern of
tests/test_m5_gpu_logic.py) and its test functions are called directly: a two-variant toy (base levels A and S, the
alternative B and S, B replacing A) passes; dropping the alternative's decor object, its level B, the shared level's
object in either scene or the alternative's scene fails; a project without variants is checked on its one scene as
before; surface decor is checked on its host in every variant scene.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "p"
AI_EV = [{"file": "building.json", "method": "ai", "confidence": 0.9, "pass": 1},
         {"file": "building.json", "method": "ai", "confidence": 0.9, "pass": 2}]


def _decor(did: str, level: str, dtype: str, host: str | None = None) -> dict:
    return {"id": did, "level_id": level, "room_id": f"r_{level}", "type": dtype, "host_id": host, "method": "ai",
            "kind": "decor", "source": "added_by_ai", "slot": f"r_{level}.s", "confidence": 0.9,
            "evidence": copy.deepcopy(AI_EV)}


def _object(item: dict, center=(1.0, 1.0, 0.0), size=(0.3, 0.3, 0.3)) -> dict:
    return {"name": f"decor_{item['id']}", "kind": "decor", "element_id": item["id"], "host_id": item["host_id"],
            "level_id": item["level_id"], "type": item["type"], "decor_method": "ai", "center": list(center),
            "size": list(size), "evidence": copy.deepcopy(AI_EV)}


def _host(fid: str, level: str, top: float = 0.45) -> dict:
    """A built table: bottom at 0, ``top`` high."""
    return {"name": fid, "kind": "furniture", "element_id": fid, "level_id": level, "type": "table_coffee",
            "center": [1.0, 1.0, top / 2.0], "size": [1.0, 0.6, top]}


def _scene(levels: list[str], objects: list[dict]) -> dict:
    return {"levels": [{"id": lv} for lv in levels], "objects": objects, "furniture": {"decor_skipped": []}}


def _write(root: Path, rel: str, doc: dict) -> None:
    path = root / PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")


def _toy() -> tuple[dict, dict, dict]:
    """The building (base: A + S; alternative ``alt``: B + S, B replaces A) and its two scenes. A holds a free-standing
    plant, B a vase on the table f_B_001 (hosted), S a pendant (in both scenes)."""
    a, b, s = _decor("dec_A_001", "A", "plant_large"), _decor("dec_B_001", "B", "vase", "f_B_001"), \
        _decor("dec_S_001", "S", "pendant_light")
    building = {"levels": [{"id": "A"}, {"id": "S"}, {"id": "B", "base_level_id": "A"}], "decor": [a, b, s],
                "variants": [{"id": "base", "base": True, "levels": ["A", "S"]},
                             {"id": "alt", "base": False, "levels": ["B", "S"],
                              "changes": [{"level_id": "B", "replaces": "A"}]}]}
    base = _scene(["A", "S"], [_object(a), _object(s, center=(2.0, 2.0, 2.4))])
    alt = _scene(["B", "S"], [_host("f_B_001", "B"), _object(b, center=(1.0, 1.0, 0.45 + 0.1), size=(0.2, 0.2, 0.2)),
                              _object(s, center=(2.0, 2.0, 2.4))])
    return building, base, alt


def _module(tmp_path, monkeypatch, building: dict, base: dict, alt: dict | None):
    """tests/gpu/test_m9.py imported against the toy outputs in ``tmp_path`` (its env is read at import)."""
    _write(tmp_path, "building_final.json", building)
    _write(tmp_path, "scene/scene_manifest.json", base)
    if alt is not None:
        _write(tmp_path, "variants/alt/scene/scene_manifest.json", alt)
    monkeypatch.setenv("WENART_OUTPUTS", str(tmp_path))
    monkeypatch.setenv("RENDER_TEST_PROJECTS", PROJECT)
    spec = importlib.util.spec_from_file_location("gpu_test_m9_cpu", ROOT / "tests" / "gpu" / "test_m9.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ai_decor_is_checked_in_every_variant_scene(tmp_path, monkeypatch):
    building, base, alt = _toy()
    m = _module(tmp_path, monkeypatch, building, base, alt)
    m.test_ai_decor_is_built(PROJECT)                  # B's vase is built in the alternative's scene only
    m.test_surface_decor_rests_on_its_host(PROJECT)


@pytest.mark.parametrize("defect", ["alt_object_dropped", "alt_level_dropped", "shared_object_dropped_in_alt",
                                    "shared_object_dropped_in_base", "alt_scene_missing", "alt_evidence_one_pass"])
def test_a_missing_variant_decor_fails(tmp_path, monkeypatch, defect):
    building, base, alt = _toy()
    if defect == "alt_object_dropped":
        alt["objects"] = [o for o in alt["objects"] if o.get("element_id") != "dec_B_001"]
    elif defect == "alt_level_dropped":                # B built in no scene: its decor is on no built level
        alt["levels"] = [lv for lv in alt["levels"] if lv["id"] != "B"]
        alt["objects"] = [o for o in alt["objects"] if o.get("level_id") != "B"]
    elif defect == "shared_object_dropped_in_alt":
        alt["objects"] = [o for o in alt["objects"] if o.get("element_id") != "dec_S_001"]
    elif defect == "shared_object_dropped_in_base":
        base["objects"] = [o for o in base["objects"] if o.get("element_id") != "dec_S_001"]
    elif defect == "alt_evidence_one_pass":
        next(o for o in alt["objects"] if o.get("element_id") == "dec_B_001")["evidence"].pop()
    m = _module(tmp_path, monkeypatch, building, base, None if defect == "alt_scene_missing" else alt)
    with pytest.raises(AssertionError):
        m.test_ai_decor_is_built(PROJECT)


def test_a_skipped_item_in_the_variant_scene_passes(tmp_path, monkeypatch):
    building, base, alt = _toy()
    alt["objects"] = [o for o in alt["objects"] if o.get("element_id") != "dec_B_001"]
    alt["furniture"]["decor_skipped"] = [{"id": "dec_B_001", "reason": "no library model"}]
    m = _module(tmp_path, monkeypatch, building, base, alt)
    m.test_ai_decor_is_built(PROJECT)


def test_a_project_without_variants_is_checked_on_its_one_scene(tmp_path, monkeypatch):
    """The Milestone 9 projects: no ``variants``, one base variant of every level that is no alternative."""
    building, base, _alt = _toy()
    building.pop("variants")
    building["decor"] = [d for d in building["decor"] if d["level_id"] != "B"]
    building["levels"] = [lv for lv in building["levels"] if lv["id"] != "B"]
    m = _module(tmp_path, monkeypatch, building, base, None)
    m.test_ai_decor_is_built(PROJECT)
    base["objects"] = base["objects"][1:]
    m = _module(tmp_path, monkeypatch, building, base, None)
    with pytest.raises(AssertionError):
        m.test_ai_decor_is_built(PROJECT)


def test_surface_decor_floating_over_its_host_in_a_variant_scene_fails(tmp_path, monkeypatch):
    building, base, alt = _toy()
    vase = next(o for o in alt["objects"] if o.get("element_id") == "dec_B_001")
    vase["center"][2] = 0.45 + 0.5                     # bottom 0.4 m above the table top
    m = _module(tmp_path, monkeypatch, building, base, alt)
    with pytest.raises(AssertionError):
        m.test_surface_decor_rests_on_its_host(PROJECT)
