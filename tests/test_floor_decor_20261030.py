"""Lesson UL151 (30 Oct 2026; user on real04 run 20261029-201533-full, cam_r_L-1_mutfak_2: "this vase on the floor not
making sense"): table-size decor never rests on the floor; only floor-class decor stands there, tall enough to read as
a floor piece. The case: the kitchen's floor plant dec_L-1_040 (slot ``r_L-1_mutfak.floor1``) took the 3D Warehouse
model "Flowers (Plants)", a table vase of pink flowers, fitted 0.54 m high on the floor beside the counter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from wenart.blender import furniture as F
from wenart.blender import model_review as MR
from wenart.blender import rest as R
from wenart.furniture import fit as FIT

RUN = Path("/home/user/WenArt_RUN/runs/20261029-201533-full/results")


def _entry(eid, dtype, bbox, title, kind="decor"):
    out = {"id": eid, "type": f"decor_{dtype}" if kind == "decor" else dtype, "source": "3dwh",
           "licence": "CC-BY-4.0", "bbox_m": list(bbox), "front_axis": "-Y", "up_axis": "+Z",
           "origin_offset": [0, 0, 0], "front_axis_confidence": "low", "glb": f"models/3dwh/{eid}.glb",
           "sha256_glb": "0" * 64, "styles": ["neutral"], "title": title, "name": title, "kind": kind}
    if kind == "decor":
        out["decor_type"] = dtype
    return out


class _Cat:
    def __init__(self, decor=()):
        self.decor, self.entries = list(decor), []

    def decor_candidates(self, dtype):
        return [e for e in self.decor if e.get("decor_type") == dtype]


def test_what_may_stand_on_the_floor():
    assert "table-size" in R.floor_class_problem("vase")
    assert R.floor_class_problem("bowl") and R.floor_class_problem("books") and R.floor_class_problem("table_lamp")
    assert "table piece" in R.floor_class_problem("plant", 0.54, "Flowers (Plants)")
    assert R.floor_class_problem("plant", 0.40, "Flower pot with plant")
    assert "at least 0.60" in R.floor_class_problem("plant", 0.37, "Plant")
    assert R.floor_class_problem("plant", 0.95, "Monstera in a basket") is None
    assert R.floor_class_problem("floor_vase", 0.40) and R.floor_class_problem("floor_vase", 1.3, "Floor Vase") is None
    for dtype in ("basket", "rug", "toilet_brush", "bag", "floor_lamp", "art_leaning"):
        assert R.floor_class_problem(dtype, 0.3) is None


def test_the_fit_gives_a_floor_plant_a_model_that_reads_as_one():
    flowers = _entry("3dwh_flowers", "plant", (0.30, 0.30, 0.40), "Flowers (Plants)")      # 0.54 m at 0.4 m wide
    tall = _entry("3dwh_ficus", "plant", (0.50, 0.50, 1.20), "Ficus in a pot")
    item = {"type": "plant", "size": [0.4, 0.4], "id": "dec_L-1_040", "slot": "r_L-1_mutfak.floor1"}
    asset = FIT.fit_decor_item(item, _Cat([flowers, tall]), "modern")
    assert asset["asset_id"] == "3dwh_ficus" and asset["bbox_m"][2] >= R.FLOOR_MIN_H_M["plant"]
    assert FIT.fit_decor_item(item, _Cat([flowers]), "modern") is None          # none left: our plant
    # a small plant on a top is no floor piece: the rule is the floor's
    small = _entry("3dwh_small", "plant_small", (0.15, 0.15, 0.25), "Flowers in a vase")
    assert FIT.fit_decor_item({"type": "plant_small", "size": [0.2, 0.2], "host_id": "f1"}, _Cat([small]),
                              "modern") is not None


def test_the_build_never_puts_a_table_item_on_the_floor():
    vase = {"id": "v", "type": "vase", "size": [0.2, 0.2, 0.3], "center": [1.0, 1.0]}
    item, why = F.floor_class_item(vase, None)
    assert why and "table-size" in why
    assert F.floor_class_item(vase, {"id": "f1", "type": "side_table"})[1] is None      # on its host
    assert F.floor_class_item(dict(vase, center=[1.0, 1.0, 0.9]), None)[1] is None      # a height given (a sill)
    plant = {"id": "p", "type": "plant", "size": [0.4, 0.4], "center": [1.0, 1.0],
             "asset": {"method": "library", "asset_id": "3dwh_flowers", "title": "Flowers (Plants)",
                       "bbox_m": [0.4, 0.4, 0.5385]}}
    item, why = F.floor_class_item(plant, None)
    assert why is None and item["asset"] is None and item["size"][2] == pytest.approx(0.6)
    assert "table piece" in item["floor_class_note"]
    tall = dict(plant, asset=dict(plant["asset"], title="Ficus", bbox_m=[0.4, 0.4, 0.9]))
    assert F.floor_class_item(tall, None) == (tall, None)
    rug = {"id": "r", "type": "rug", "size": [2.0, 1.4], "center": [1.0, 1.0]}
    assert F.floor_class_item(rug, None) == (rug, None)
    # our floor sculpture (0.40 m by default) stands as tall as a floor piece; one on a top keeps its size
    sculpture = {"id": "s", "type": "sculpture", "size": [0.3, 0.3], "center": [1.0, 1.0]}
    item, why = F.floor_class_item(sculpture, None)
    assert why is None and item["size"][2] == pytest.approx(R.FLOOR_MIN_H_M["sculpture"])
    assert F.floor_class_item(sculpture, {"id": "f1"}) == (sculpture, None)


def test_the_model_review_names_a_table_piece_on_the_floor():
    built = {"levels": [{"id": "L-1", "elevation": -3.0, "ceiling_height": 2.85}], "openings": []}
    box = {"center": [1.15, 7.39, -3.0 + 0.27], "size": [0.4, 0.4, 0.54], "rotation_deg": 0.0}
    manifest = {"objects": [{"kind": "decor", "type": "plant", "decor_id": "dec_L-1_040", "level_id": "L-1",
                             "room_id": "r_L-1_mutfak", "box3d": box, "asset": {"title": "Flowers (Plants)"}},
                            {"kind": "decor", "type": "plant", "decor_id": "dec_ok", "level_id": "L-1",
                             "box3d": dict(box, size=[0.4, 0.4, 0.9], center=[2, 2, -3.0 + 0.45]),
                             "asset": {"title": "Ficus"}}]}
    found, n = MR.decor_attached(manifest, built)
    assert [f["target"] for f in found] == ["dec_L-1_040"] and found[0]["check"] == "M14"
    assert found[0]["metrics"]["rule"] == "floor_class" and found[0]["kind"] == "no_sense"


def test_real04_kitchen_plant_is_the_case():
    path = RUN / "renders/real04/scene_manifest.json"
    if not path.is_file():
        pytest.skip("the run's records are not on this machine")
    scene = json.loads(path.read_text(encoding="utf-8"))
    built = json.loads((RUN / "renders/real04/building_built.json").read_text(encoding="utf-8"))
    found, _n = MR.decor_attached(scene, built)
    floor = {f["target"] for f in found if f["metrics"].get("rule") == "floor_class"}
    assert "dec_L-1_040" in floor
