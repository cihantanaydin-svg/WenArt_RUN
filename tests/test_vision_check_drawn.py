"""CPU tests of the drawn-piece check against the source plan (docs/milestone10.md §1.7, §2.7, §2.8).

The Milestone 10 example building is a final building (a sofa the AI made a corner sofa, a console table proposal,
pieces added to the rooms); the source building is rebuilt from its ``drawn_*`` fields. Every drawn piece must keep
its anchor (5 cm), front (1 degree) and wall; a moved, turned, removed or unlabelled piece is a finding.
"""
import copy
import json
from pathlib import Path

import pytest

from wenart.vision_check import drawn as DR
from wenart.vision_check import expected as X

ROOT = Path(__file__).resolve().parents[1]
AI_KEYS = ("modified_by_ai", "anchor", "type_proposal", "design", "shape", "chaise_side", "seat_depth",
           "chaise_width", "chaise_depth")


@pytest.fixture()
def final() -> dict:
    return json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))


def source_of(final: dict) -> dict:
    """The drawn building behind a final one: the AI's pieces dropped, the changed drawn pieces as drawn."""
    src = copy.deepcopy(final)
    keep = []
    for f in src["furniture"]:
        if f["source"] != "from_documents":
            continue
        if f.get("modified_by_ai") or f.get("type_proposal"):
            f["type"] = f.pop("drawn_type", f["type"])
            f["footprint"] = f.pop("drawn_footprint", f["footprint"])
            if "drawn_height" in f:
                f["height"] = f.pop("drawn_height")
            for k in AI_KEYS:
                f.pop(k, None)
        keep.append(f)
    src["furniture"] = keep
    return src


def row(check: dict, pid: str) -> dict:
    return next(r for r in check["pieces"] if r["id"] == pid)


def test_a_faithful_final_building_keeps_every_drawn_piece(final):
    check = DR.drawn_check(final, source_of(final))
    assert check["reference"] == "source building.json" and check["mode"] == "complete"
    assert check["checked"] == check["ok"] == len(check["pieces"]) == 11
    assert check["failed"] == [] and check["violations"] == [] and check["notes"] == []
    corner = row(check, "f_L-1_002")
    assert corner["modified_by_ai"] and (corner["drawn_type"], corner["type"]) == ("sofa", "sofa_corner")
    assert corner["drawn_size"] == [2.2, 0.9] and corner["size"] == [2.6, 1.6]
    assert corner["anchor_kind"] == "back_edge" and corner["anchor_distance_m"] == 0.0
    assert corner["front_turn_deg"] == 0.0 and corner["same_wall"] is True
    assert check["modified"] == ["f_L-1_002"] and row(check, "f_L0_009")["drawn_type"] == "unknown"
    assert [line for line in DR.lines(check)] == []


def test_a_moved_piece_fails_the_anchor_check(final):
    moved = copy.deepcopy(final)
    piece = next(f for f in moved["furniture"] if f["id"] == "f_L0_008")          # the shower: a free piece
    piece["footprint"]["center"][0] += 0.20
    check = DR.drawn_check(moved, source_of(final))
    assert check["failed"] == ["f_L0_008"] and row(check, "f_L0_008")["anchor_distance_m"] == pytest.approx(0.2)
    assert any("f_L0_008" in line and "anchor moved 0.2" in line for line in DR.lines(check))
    assert any("fixed equipment changed footprint" in v for v in check["violations"])     # locked.check agrees


def test_within_five_centimetres_is_still_the_same_place(final):
    moved = copy.deepcopy(final)
    piece = next(f for f in moved["furniture"] if f["id"] == "f_L0_008")
    piece["footprint"]["center"][1] += 0.04
    check = DR.drawn_check(moved, source_of(final))
    assert row(check, "f_L0_008")["ok"] is True and row(check, "f_L0_008")["anchor_distance_m"] == pytest.approx(0.04)


def test_a_turned_front_fails_the_front_check(final):
    turned = copy.deepcopy(final)
    piece = next(f for f in turned["furniture"] if f["id"] == "f_L0_002")           # the bed
    piece["front_deg"] = 275.0
    check = DR.drawn_check(turned, source_of(final))
    r = row(check, "f_L0_002")
    assert r["ok"] is False and r["front_turn_deg"] == pytest.approx(5.0)
    assert any("front 270.0 -> 275.0" in v for v in check["violations"])


def test_a_piece_that_left_its_wall_fails(final):
    off = copy.deepcopy(final)
    piece = next(f for f in off["furniture"] if f["id"] == "f_L0_002")
    piece["footprint"]["center"][1] -= 1.0
    r = row(DR.drawn_check(off, source_of(final)), "f_L0_002")
    assert r["ok"] is False and r["same_wall"] is False and r["anchor_distance_m"] == pytest.approx(1.0)
    assert any("no longer against wall" in n for n in r["notes"])


def test_a_removed_drawn_piece_is_a_violation(final):
    gone = copy.deepcopy(final)
    gone["furniture"] = [f for f in gone["furniture"] if f["id"] != "f_L0_006"]
    check = DR.drawn_check(gone, source_of(final))
    assert "f_L0_006: drawn piece missing from the final building" in check["violations"]
    assert any("drawn toilet removed" in v for v in check["violations"])


def test_a_changed_piece_without_the_ai_label_is_a_violation(final):
    liar = copy.deepcopy(final)
    piece = next(f for f in liar["furniture"] if f["id"] == "f_L0_002")
    piece["footprint"]["size"] = [1.8, 2.0]
    piece["footprint"]["center"][1] += 0.1                       # grows around the back edge, stays on the wall
    check = DR.drawn_check(liar, source_of(final))
    assert row(check, "f_L0_002")["size"] == [1.8, 2.0]
    assert any("changed without modified_by_ai" in v for v in check["violations"])


def test_without_a_source_the_recorded_anchor_is_the_reference(final):
    check = DR.drawn_check(final, None)
    assert check["reference"] == "recorded anchors"
    checked = [r["id"] for r in check["pieces"] if r["checked"]]
    assert checked == ["f_L-1_002", "f_L0_002"] and all(row(check, i)["ok"] for i in checked)
    nothing = row(check, "f_L0_008")
    assert nothing["checked"] is False and nothing["reference"] == "none" and nothing["ok"] is None
    assert row(check, "f_L-1_002")["notes"] == ["no source building.json: the front is not checked"]
    assert check["violations"] == [] and "no source building.json" in check["notes"][0]


def test_the_source_is_found_next_to_the_project_output_or_for_a_variant(tmp_path):
    base = tmp_path / "outputs" / "real02"
    (base / "variants" / "l-1b-x").mkdir(parents=True)
    assert DR.source_path(base) is None
    (base / "building.json").write_text("{}", encoding="utf-8")
    assert DR.source_path(base) == (base / "building.json").resolve()
    assert DR.source_path(base / "variants" / "l-1b-x") == (base / "building.json").resolve()
    assert DR.load_source(base) == {}


def test_expected_elements_carry_what_the_ai_did(final):
    flags = X.piece_flags(final)
    assert flags["f_L-1_002"] == {"modified_by_ai": True, "drawn_type": "sofa", "completes_room": False,
                                  "type_proposal": False}
    assert flags["f_L-1_003"]["completes_room"] is True and not flags["f_L-1_003"]["modified_by_ai"]
    assert flags["f_L0_008"] == {"modified_by_ai": False, "drawn_type": None, "completes_room": False,
                                 "type_proposal": False}
