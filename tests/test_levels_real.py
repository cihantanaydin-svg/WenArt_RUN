"""Regression of the levels on the committed real buildings (docs/milestone12.md §1.5, §3; the pipeline's own
building.json of real03 run 3 and real02 G2d in results/furniture/): no DWG converter is needed. real03 (one drawn
ground floor, user decision of 10 Oct 2026) becomes a whole building with a flat_cut roof, its site and entrance
steps (D3a: nothing about the ground in that JSON); real02 keeps its drawn ground and gets entrances, plinth and its
basement courts recorded."""
import json
from pathlib import Path

import pytest

from wenart import building as B
from wenart.blender import build as BB
from wenart.levels import checks as C
from wenart.levels import model as M

ROOT = Path(__file__).resolve().parents[1]


def _load(project):
    path = ROOT / "results" / "furniture" / project / "building.json"
    if not path.is_file():
        pytest.skip(f"{path} not committed")
    return json.loads(path.read_text(encoding="utf-8"))


def test_real03_ground_floor_becomes_a_whole_building():
    b0 = _load("real03")
    assert not BB.is_whole_building(b0)                         # before: no ground, site or exterior (§1.5)
    b = M.infer_levels(b0)
    assert BB.is_whole_building(b) and b["roof"]["kind"] == "flat_cut" and b["roof"]["note"] == "upper floors not drawn"
    li = b["level_inference"]
    assert li["single_level_whole"] and li["ground_source"] == "D3a"
    ents = b["site"]["entrances"]
    assert len(ents) == 2 and all(e["solution"] == "steps" and e["rise"] == 0.15 for e in ents)
    assert sum(e["main"] for e in ents) == 1
    assert sum(1 for o in b["openings"] if o.get("threshold_z") is not None) == 47
    assert not B.validation_errors(b)
    assert not [f for f in C.check_levels(b) if f["severity"] in ("critical", "major")]


def test_real02_keeps_its_drawn_ground_and_records_its_basement():
    b = M.infer_levels(_load("real02"))
    li = b["level_inference"]
    assert li["ground_source"] == "section" and not li["single_level_whole"]
    assert [(g["side"], g["z"]["value"]) for g in b["site"]["ground"]["levels"]] == [("left", 0.0), ("right", 0.0)]
    ents = {e["door_id"]: e for e in b["site"]["entrances"]}
    assert set(ents) >= {"d_L0_011", "d_L0_012"} and ents["d_L0_011"]["solution"] == "none"
    assert li["basements"][0]["level_id"] == "L-1" and li["basements"][0]["light_wells"] == 3
    wells = b["site"]["ground"]["light_wells"]
    assert len(wells) == 3 and all(w["source"] == "assumed" and w["inferred"] for w in wells)
    assert b["site"]["plinth"]["top_z"] == 0.0
    assert not B.validation_errors(b)
