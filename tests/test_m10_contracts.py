"""Milestone 10 contracts (docs/milestone10.md §1): the building JSON additions, sheets.json, the brief keys.

These pin the frozen contract every M10 track builds against; a change here is a lead change of the spec.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from wenart import brief as BR
from wenart import building as B

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"
SHEETS_EXAMPLE = ROOT / "docs" / "examples" / "sheets.example.json"
SHEETS_SCHEMA = ROOT / "wenart" / "schema" / "sheets.schema.json"

NEW_FURNITURE_TYPES = ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
                       "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
NEW_DECOR_TYPES = ("curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture", "plant_large",
                   "pendant_light", "ceiling_light")
REGION_CLASSES = ("floor_plan", "alternative_floor_plan", "furniture_plan", "section", "elevation", "roof_plan", "site_plan",
                  "detail", "3d_view", "title_block", "legend", "other")


def _sheets_errors(doc: dict) -> list[str]:
    schema = json.loads(SHEETS_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(doc)]


def test_building_m10_example_validates():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert B.validation_errors(example) == []
    kinds = {lv["id"]: lv.get("kind") for lv in example["levels"]}
    assert kinds == {"L-1": "basement", "L-1b": "basement", "L0": "floor", "L1": "attic"}
    assert [v["id"] for v in example["variants"]] == ["base", "l-1b-acik-mutfak"]
    assert {s["id"] for s in example["slabs"]} == {"sl_L-1", "sl_L0", "sl_L1"}
    assert example["roof"]["type"] == "gable" and example["roof"]["openings"][0]["kind"] == "terrace"


def test_building_m10_example_covers_feature_1_labels():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    pieces = {p["id"]: p for p in example["furniture"]}
    changed = pieces["f_L-1_002"]
    assert changed["source"] == "from_documents" and changed["modified_by_ai"] is True
    assert changed["drawn_type"] == "sofa" and changed["type"] == "sofa_corner" and changed["shape"] == "L"
    assert changed["anchor"]["kind"] == "back_edge"
    added = [p for p in pieces.values() if p.get("completes_room")]
    assert added and all(p["source"] == "added_by_ai" for p in added)
    assert any(p.get("method") == "rule" and p["type"] == "wall_cabinet" for p in added)


@pytest.mark.parametrize("mutate, where", [
    (lambda b: b["variants"][1].pop("levels"), "variants"),
    (lambda b: b["slabs"][0].update(thickness_source="guess"), "slabs"),
    (lambda b: b["roof"].update(type="dome"), "roof"),
    (lambda b: b["furniture"][0].update(anchor={"kind": "corner", "point": [0, 0]}), "furniture"),
    (lambda b: b["levels"][0].update(kind="cellar"), "levels"),
    (lambda b: b["site"]["ground"]["levels"][0]["z"].update(method="guess"), "site"),
    (lambda b: b["decor"][1].update(species="cactus"), "decor"),
])
def test_building_m10_broken_copies_fail(mutate, where):
    broken = copy.deepcopy(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    mutate(broken)
    errors = B.validation_errors(broken)
    assert errors and any(where in e for e in errors), errors


def test_schema_has_the_new_types():
    schema = B.load_schema()
    furniture_types = schema["$defs"]["furniture"]["properties"]["type"]["enum"]
    decor_types = schema["$defs"]["decor"]["properties"]["type"]["enum"]
    assert set(NEW_FURNITURE_TYPES) <= set(furniture_types) and furniture_types[-1] == "unknown"
    assert set(NEW_DECOR_TYPES) <= set(decor_types)
    page_classes = schema["$defs"]["document"]["properties"]["pages"]["items"]["properties"]["class"]["enum"]
    assert {"roof_plan", "3d_view", "title_block", "legend"} <= set(page_classes)


def test_sheets_example_validates_and_broken_copy_fails():
    doc = json.loads(SHEETS_EXAMPLE.read_text(encoding="utf-8"))
    assert _sheets_errors(doc) == []
    schema = json.loads(SHEETS_SCHEMA.read_text(encoding="utf-8"))
    assert tuple(schema["$defs"]["region"]["properties"]["class"]["enum"]) == REGION_CLASSES
    broken = copy.deepcopy(doc)
    broken["regions"][1]["class"] = "plan"
    assert _sheets_errors(broken)
    broken = copy.deepcopy(doc)
    broken["heights"]["levels"][0]["floor_z"]["method"] = "guess"
    assert _sheets_errors(broken)


def test_examples_are_reproducible():
    """The committed examples are what docs/examples/make_m10_examples.py writes."""
    before = (EXAMPLE.read_bytes(), SHEETS_EXAMPLE.read_bytes())
    subprocess.run([sys.executable, str(ROOT / "docs" / "examples" / "make_m10_examples.py")], cwd=ROOT, check=True,
                   env={"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"}, capture_output=True)
    assert (EXAMPLE.read_bytes(), SHEETS_EXAMPLE.read_bytes()) == before


def test_brief_m10_defaults():
    values = BR.merge_brief({})["values"]
    assert values["furnished_rooms"] == "complete"
    assert values["furnished_rooms_keep"] == [] and values["furnished_rooms_keep_size"] is False
    assert values["variants"] == "all" and values["failed_levels"] == "leave_out" and values["site"] == "full"
    assert values["slab_thickness"] == pytest.approx(0.20)
    assert values["render"]["twin_rooms"] == "one" and values["render"]["exterior_views"] is True
    assert set(values["exterior"]) == {"facade", "roof", "window_frame", "door", "paving", "garden"}


@pytest.mark.parametrize("raw, key, expect, warned", [
    ({"furnished_rooms": "keep"}, "furnished_rooms", "keep", False),
    ({"furnished_rooms": "yes"}, "furnished_rooms", "complete", True),
    ({"variants": ["Açık mutfak"]}, "variants", ["Açık mutfak"], False),
    ({"variants": "some"}, "variants", "all", True),
    ({"variants": []}, "variants", "all", True),
    ({"failed_levels": "stop"}, "failed_levels", "stop", False),
    ({"site": "ground"}, "site", "ground", False),
    ({"site": "garden"}, "site", "full", True),
    ({"furnished_rooms_keep": ["Salon", "r_L0_hol"]}, "furnished_rooms_keep", ["Salon", "r_L0_hol"], False),
    ({"furnished_rooms_keep": "Salon"}, "furnished_rooms_keep", [], True),
    ({"render": {"twin_rooms": "all"}}, "render.twin_rooms", "all", False),
    ({"render": {"twin_rooms": "two"}}, "render.twin_rooms", "one", True),
])
def test_brief_m10_value_rules(raw, key, expect, warned):
    out = BR.merge_brief(raw)
    assert BR.value(out, key) == expect
    assert bool(out["warnings"]) is warned
    assert (key in out["assumed"]) is warned


def test_brief_exterior_words_merge_key_by_key():
    out = BR.merge_brief({"exterior": {"roof": "clay tiles", "facade": "white render"}})
    assert BR.value(out, "exterior.roof") == "clay tiles" and BR.value(out, "exterior.facade") == "white render"
    assert "exterior.paving" in out["assumed"] and "exterior.roof" not in out["assumed"]
