"""CPU tests of the variants and the views to render (wenart/views.py, docs/milestone10.md §1.6, §1.6a, §3.2
items 6-7, §1.6b rows 8-11): ``variant_building``, the room and outside diff of an alternative
(``variant_changes``: the pipeline's values, computed when null), ``views_for`` (the contract's fields and
reasons) with mirrored twins, the brief keys the builder reads without PyYAML, the object kinds that never count
as furniture and the variant path helpers of the CLI (the 3D sets per variant: tests/test_pack3d.py)."""
import copy
import json
from pathlib import Path

import pytest
import yaml

from wenart import views as V
from wenart.blender import cli

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
ALT = "l-1b-acik-mutfak"


def _blank_changes(b):
    """The building without the pipeline's rooms_changed / exterior_changed (null: the build computes them)."""
    b = copy.deepcopy(b)
    for v in b["variants"]:
        v["rooms_changed"], v["exterior_changed"] = None, None
    return b


def test_brief_defaults_match_wenart_defaults_yaml():
    brief = yaml.safe_load((ROOT / "wenart" / "defaults.yaml").read_text(encoding="utf-8"))["brief"]
    for key, value in V.BRIEF_DEFAULTS.items():
        cur = brief
        for part in key.split("."):
            cur = cur[part]
        assert cur == value, key


def test_brief_setting_reads_the_building_brief_else_the_defaults():
    assert V.brief_setting(EXAMPLE, "render.twin_rooms") == ("one", False)
    assert V.brief_setting(EXAMPLE, "site") == ("full", False)
    assert V.brief_setting(EXAMPLE, "slab_thickness") == (0.20, True)
    stored = {"project": {"brief": {"values": {"site": "ground"}, "assumed": ["site"]}}}
    assert V.brief_setting(stored, "site") == ("ground", True)


def test_variant_building_of_the_alternative():
    vb = V.variant_building(EXAMPLE, ALT)
    assert [lv["id"] for lv in vb["levels"]] == ["L-1b", "L0", "L1"]
    assert {w["level_id"] for w in vb["walls"]} == {"L-1b", "L0", "L1"}
    assert not any(r["level_id"] == "L-1" for r in vb["rooms"])
    slabs = {s["id"]: (s["above_level_id"], s["below_level_id"]) for s in vb["slabs"]}
    assert slabs == {"sl_L-1": ("L-1b", None), "sl_L0": ("L0", "L-1b"), "sl_L1": ("L1", "L0")}
    face = vb["facade"]["faces"][0]                     # the stone plinth (a side, no wall) moves to the alternative
    assert face["wall_id"] is None and face["level_id"] == "L-1b" and face["level_moved_from"] == "L-1"
    walled = copy.deepcopy(EXAMPLE)                     # a face drawn on one wall moves to the wall on its line
    walled["facade"]["faces"][0]["wall_id"] = "w_L-1_001"
    face = V.variant_building(walled, ALT)["facade"]["faces"][0]
    assert face["wall_id"] == "w_L-1b_001" and face["moved_from"] == "w_L-1_001"
    assert vb["_variant"]["replacements"] == {"L-1": "L-1b"} and not vb["_variant"]["warnings"]
    base = V.variant_building(EXAMPLE, "base")
    assert [lv["id"] for lv in base["levels"]] == ["L-1", "L0", "L1"] and base["facade"]["faces"][0]["level_id"] == "L-1"
    with pytest.raises(KeyError):
        V.variant_building(EXAMPLE, "nope")


def test_legacy_buildings_have_one_base_variant():
    legacy = {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}], "rooms": [], "walls": []}
    assert V.building_variants(legacy) == [{"id": "base", "label": "Base", "levels": ["L0", "L1"], "base": True,
                                            "changes": [], "rooms_changed": [], "exterior_changed": False}]


def test_variant_changes_computed_like_the_example_says():
    b = _blank_changes(EXAMPLE)
    ch = V.variant_changes(b, ALT)
    assert ch["rooms_changed"] == ["r_L-1b_salon_acik_mutfak"] and ch["exterior_changed"] is False
    assert ch["source"] == {"rooms_changed": "computed", "exterior_changed": "computed"}
    assert ch["same_as"] == {"r_L-1b_hol": "r_L-1_hol"} and ch["why"]["r_L-1b_salon_acik_mutfak"] == "polygon differs"
    given = V.variant_changes(EXAMPLE, ALT)
    assert given["source"] == {"rooms_changed": "building", "exterior_changed": "building"} and not given["warnings"]
    assert V.variant_changes(EXAMPLE, "base")["rooms_changed"] == []


def test_a_moved_door_or_window_changes_a_room_and_the_outside():
    b = _blank_changes(EXAMPLE)
    for o in b["openings"]:
        if o["id"] == "d_L-1b_002":
            o["center"] = [6.0, 6.5]                     # the hall door moved by 0.5 m
        if o["id"] == "win_L-1b_002":
            o["width"] = 1.5                            # an outer window drawn wider
    ch = V.variant_changes(b, ALT)
    assert set(ch["rooms_changed"]) == {"r_L-1b_salon_acik_mutfak", "r_L-1b_hol"}
    assert ch["why"]["r_L-1b_hol"] == "openings differ" and ch["exterior_changed"] is True
    # 1 cm is the same room (2 cm tolerance)
    b = _blank_changes(EXAMPLE)
    for r in b["rooms"]:
        if r["id"] == "r_L-1b_hol":
            r["polygon"] = [[x + 0.01, y] for x, y in r["polygon"]]
    assert V.variant_changes(b, ALT)["rooms_changed"] == ["r_L-1b_salon_acik_mutfak"]
    # a different drawn piece changes the room
    for p in b["furniture"]:
        if p["id"] == "f_L-1b_001":
            p["footprint"] = dict(p["footprint"], center=[9.35, 5.5])
    assert "r_L-1b_hol" in V.variant_changes(b, ALT)["rooms_changed"]


def test_given_values_win_and_a_disagreement_is_a_warning():
    b = copy.deepcopy(EXAMPLE)
    alt = next(v for v in b["variants"] if v["id"] == ALT)
    alt["exterior_changed"] = True
    ch = V.variant_changes(b, ALT)
    assert ch["exterior_changed"] is True and any("exterior_changed" in w for w in ch["warnings"])


def test_views_for_base_and_alternative():
    base = V.views_for(EXAMPLE, "base")
    assert base["rooms"] == [r["id"] for r in EXAMPLE["rooms"] if r["level_id"] in ("L-1", "L0", "L1")]
    assert base["exterior"] is True and base["skipped"] == [] and base["assumed"] == []
    alt = V.views_for(EXAMPLE, ALT)
    assert alt["rooms"] == ["r_L-1b_salon_acik_mutfak"] and alt["exterior"] is False
    assert "base exterior views are listed" in alt["exterior_reason"]
    skipped = {s["room_id"]: s["reason"] for s in alt["skipped"]}
    assert skipped["r_L-1b_hol"] == "same as r_L-1_hol" and skipped["r_L0_hol"] == "unchanged in variant"
    assert len(skipped) == 7 and all(set(s) == {"room_id", "reason"} for s in alt["skipped"])
    assert alt["base_views"]["r_L-1b_hol"] == "r_L-1_hol" and alt["base_views"]["r_L0_hol"] == "r_L0_hol"
    assert V.views_for(EXAMPLE, "base", exterior_views=False)["exterior"] is False
    b = _blank_changes(EXAMPLE)
    for o in b["openings"]:
        if o["id"] == "win_L-1b_001":
            o["sill_height"] = 0.5
    own = V.views_for(b, ALT)
    assert own["exterior"] is True and own["exterior_from"] == ALT   # an outer window differs: own exterior views


def _twin_building():
    """A semi-detached pair on one level: r_a2 mirrors r_a1 (twin_of), the hall is shared."""
    def room(rid, poly, twin=None):
        return {"id": rid, "level_id": "L0", "label": "Salon", "room_type": "living", "polygon": poly,
                "area_computed": 20.0, "has_documented_furniture": False, "status": "verified", "evidence": [],
                "twin_of": twin}
    return {"project": {"id": "pair", "brief": {}}, "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "walls": [], "openings": [], "furniture": [],
            "rooms": [room("r_a1", [[0, 0], [5, 0], [5, 4], [0, 4]]), room("r_a2", [[5, 0], [10, 0], [10, 4], [5, 4]], "r_a1"),
                      room("r_hall", [[0, 4], [10, 4], [10, 6], [0, 6]])]}


def test_twins_are_rendered_once_and_still_built():
    b = _twin_building()
    v = V.views_for(b)
    assert v["rooms"] == ["r_a1", "r_hall"] and "render.twin_rooms" in v["assumed"]
    assert v["skipped"] == [{"room_id": "r_a2", "reason": "twin of r_a1"}]
    assert V.views_for(b, twin_rooms="all")["rooms"] == ["r_a1", "r_a2", "r_hall"]
    b["project"]["brief"] = {"render": {"twin_rooms": "all"}}
    assert V.views_for(b)["rooms"] == ["r_a1", "r_a2", "r_hall"] and V.views_for(b)["assumed"] == ["render.exterior_views"]
    assert len(V.variant_building(b)["rooms"]) == 3                 # the second twin is built


def test_variant_paths_of_the_cli():
    assert cli.variant_path("outputs/p/scene", "base") == Path("outputs/p/scene")
    assert cli.variant_path("outputs/p/scene", ALT) == Path(f"outputs/p/variants/{ALT}/scene")
    assert cli.variant_path("outputs/p/scene/scene.blend", ALT) == Path(f"outputs/p/variants/{ALT}/scene/scene.blend")
    assert cli.variant_path("outputs/p/renders/render_manifest.json", ALT) == \
        Path(f"outputs/p/variants/{ALT}/renders/render_manifest.json")
    assert cli.variant_path(f"outputs/p/variants/{ALT}/export", ALT) == Path(f"outputs/p/variants/{ALT}/export")
    assert cli.variant_path("outputs/p/export", ALT, is_file=False) == Path(f"outputs/p/variants/{ALT}/export")
    assert cli.export_name("p", "base") == "p" and cli.export_name("p", ALT) == f"p-{ALT}"
    assert cli.export_name(f"p-{ALT}", ALT) == f"p-{ALT}"           # the scheduler may pass the full name


def test_views_for_has_the_contract_fields_and_reads_the_brief():
    v = V.views_for(EXAMPLE, "base")
    assert {"variant", "rooms", "skipped", "exterior", "exterior_from"} <= set(v)
    assert v["variant"] == "base" and v["exterior_from"] == "base"
    alt = V.views_for(EXAMPLE, ALT)
    assert alt["variant"] == ALT and alt["exterior"] is False and alt["exterior_from"] == "base"
    off = {"values": {"render": {"exterior_views": False, "twin_rooms": "all"}}, "assumed": []}
    v = V.views_for(EXAMPLE, "base", brief=off)
    assert v["exterior"] is False and v["twin_rooms"] == "all" and v["assumed"] == []
    assert V.brief_value(EXAMPLE, {"site": "ground"}, "site") == ("ground", False)       # a plain values dict
    assert V.brief_value(EXAMPLE, None, "slab_thickness") == (0.20, True)               # the defaults
    assert set(V.BUILD_BRIEF_KEYS) <= set(V.BRIEF_DEFAULTS)


def test_whole_building_kinds_never_count_as_furniture():
    from wenart.blender import common, schemas

    for kind in schemas.WHOLE_BUILDING_KINDS:
        assert kind in common.KINDS and V.KIND_MAP.get(kind, kind) != "furniture", kind

