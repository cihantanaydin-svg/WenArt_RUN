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
    (lambda b: b["variants"][1].update(id="L-1b open"), "variants"),
    (lambda b: b["furniture"][next(i for i, f in enumerate(b["furniture"]) if f.get("modified_by_ai"))].pop("drawn_type"),
     "furniture"),
    (lambda b: b["furniture"][next(i for i, f in enumerate(b["furniture"]) if f["type"] == "wall_cabinet")].pop(
        "mount_bottom_m"), "furniture"),
    (lambda b: b["furniture"][next(i for i, f in enumerate(b["furniture"]) if f.get("completes_room"))].update(
        source="from_documents"), "furniture"),
    (lambda b: b["roof"]["thickness"].pop("note"), "roof"),
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


def test_example_furniture_follows_the_front_convention_and_its_checks():
    """front_deg = (270 + rotation_deg) mod 360 for every piece with a front; every AI-placed piece that records its
    placer checks passes them in the example (docs/milestone10.md §1.1; review of 8 Oct 2026)."""
    from wenart.furniture import placer as P

    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    for f in example["furniture"]:
        if f.get("front_deg") is not None:
            assert f["front_deg"] == pytest.approx((270 + f["footprint"]["rotation_deg"]) % 360), f["id"]
    rooms = {r["id"]: r for r in example["rooms"]}
    for f in example["furniture"]:
        if "checks" not in f:
            continue
        room = rooms[f["room_id"]]
        ctx = P.room_context(example, room)
        others = [P.piece_from_furniture(g, i) for i, g in enumerate(example["furniture"])
                  if g["room_id"] == room["id"] and g["id"] != f["id"] and g.get("mount_bottom_m") is None]
        piece = P.piece_from_furniture(f, len(others))
        piece.against_wall = f.get("front_deg") is not None
        checks = P.check_all(others + [piece], ctx)[-1]
        assert not P.failed_checks(checks), (f["id"], checks)


def test_examples_agree_with_each_other():
    """The building example and the sheets example describe the same project."""
    building = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    sheets = json.loads(SHEETS_EXAMPLE.read_text(encoding="utf-8"))
    assert [v["id"] for v in building["variants"]] == [v["id"] for v in sheets["variants"]]
    regions = {r["id"]: r for r in sheets["regions"]}
    assert len(regions) == len(sheets["regions"])                          # unique in the project
    for lv in building["levels"]:
        assert regions[lv["region_id"]]["use"] == "read", lv["id"]
    for page in building["documents"][0]["pages"]:
        assert regions[page["region_id"]]["use"] in ("read", "heights", "exterior")
        assert page["region_box"] == regions[page["region_id"]]["box"]
    sheet_kinds = set(json.loads(SHEETS_SCHEMA.read_text(encoding="utf-8"))["$defs"]["conflict"]["properties"]["kind"]["enum"])
    building_kinds = set(B.load_schema()["$defs"]["conflict"]["properties"]["kind"]["enum"])
    assert sheet_kinds <= building_kinds
    b_value = B.load_schema()["$defs"]["value"]
    s_value = json.loads(SHEETS_SCHEMA.read_text(encoding="utf-8"))["$defs"]["value"]
    assert b_value["properties"]["method"] == s_value["properties"]["method"] and b_value["allOf"] == s_value["allOf"]
    b_ev = set(B.load_schema()["$defs"]["evidence"]["properties"])
    s_ev = set(json.loads(SHEETS_SCHEMA.read_text(encoding="utf-8"))["$defs"]["evidence"]["properties"])
    assert {"region_id", "rule"} <= b_ev and {"region_id", "rule"} <= s_ev
    # The reference plan's transform puts the outer wall faces' min corner on the building origin.
    walls = [w for w in building["walls"] if w["level_id"] == "L0" and w["exterior"]]
    assert min(min(w["start"][0], w["end"][0]) - w["thickness"] / 2 for w in walls) == pytest.approx(0.0)
    assert min(min(w["start"][1], w["end"][1]) - w["thickness"] / 2 for w in walls) == pytest.approx(0.0)


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
    broken = copy.deepcopy(doc)                                    # an AI-only class never makes a plan
    broken["regions"][1].update(class_method="ai")
    assert _sheets_errors(broken)
    broken = copy.deepcopy(doc)                                    # an assumed value needs its note and confidence 0
    broken["heights"]["roof"]["thickness"].pop("note")
    assert _sheets_errors(broken)


def test_examples_are_reproducible(tmp_path):
    """The committed examples are what docs/examples/make_m10_examples.py writes."""
    subprocess.run([sys.executable, str(ROOT / "docs" / "examples" / "make_m10_examples.py"), "--out-dir", str(tmp_path)],
                   cwd=ROOT, check=True, env={"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"}, capture_output=True)
    assert (tmp_path / EXAMPLE.name).read_bytes() == EXAMPLE.read_bytes()
    assert (tmp_path / SHEETS_EXAMPLE.name).read_bytes() == SHEETS_EXAMPLE.read_bytes()


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
