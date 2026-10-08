"""The locked check of drawn furniture (docs/milestone10.md §2.7) and the anchors of drawn pieces (§2.2).

Source: the M10 example building (docs/examples/building_m10.example.json) with the AI-made pieces stripped
(``drawn_building``); final: the example itself (a drawn sofa changed into a corner sofa at its anchor, AI
pieces added). Every bad final is the good one with one thing broken.
"""
import copy
import json
from pathlib import Path

import pytest

from wenart.furniture import locked as LK

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "examples" / "building_m10.example.json"


def example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def drawn_building(final: dict) -> dict:
    """The example as the documents give it: AI pieces removed, changed pieces back to their drawn values."""
    b = copy.deepcopy(final)
    keep = []
    for f in b["furniture"]:
        if f["source"] != "from_documents":
            continue
        if f.get("modified_by_ai"):
            f["type"], f["footprint"], f["height"] = f["drawn_type"], f["drawn_footprint"], f["drawn_height"]
            for key in ("modified_by_ai", "drawn_type", "drawn_footprint", "drawn_height", "shape", "chaise_side",
                        "chaise_depth", "design", "type_proposal", "mirrored_from"):
                f.pop(key, None)
            f["evidence"] = [e for e in f["evidence"] if e["method"] != "ai"]
        f.pop("anchor", None)
        keep.append(f)
    b["furniture"] = keep
    b["decor"] = []
    return b


@pytest.fixture
def pair():
    final = example()
    return drawn_building(final), final


def piece(b: dict, pid: str) -> dict:
    return next(f for f in b["furniture"] if f["id"] == pid)


# --------------------------------------------------------------------------
# Anchors
# --------------------------------------------------------------------------

def test_anchor_of_a_piece_against_a_wall_is_its_back_edge_midpoint(pair):
    source, final = pair
    sofa = piece(source, "f_L-1_002")
    assert LK.anchor_of(sofa, source) == {"kind": "back_edge", "point": [3.0, 7.85], "wall_id": "w_L-1_003"}
    assert LK.anchor_of(sofa, source) == piece(final, "f_L-1_002")["anchor"]      # the example's own anchor
    bed = piece(source, "f_L0_002")
    assert LK.anchor_of(bed, source) == {"kind": "back_edge", "point": [3.0, 7.85], "wall_id": "w_L0_003"}


def test_anchor_of_a_free_piece_and_of_a_piece_without_a_front_is_the_centre(pair):
    source, _final = pair
    sofa = copy.deepcopy(piece(source, "f_L-1_002"))
    sofa["footprint"]["center"] = [3.0, 6.0]                                        # 1.4 m off the wall
    assert LK.anchor_of(sofa, source) == {"kind": "centre", "point": [3.0, 6.0], "wall_id": None}
    shower = piece(source, "f_L0_008")                                              # front_deg null
    assert shower["front_deg"] is None
    assert LK.anchor_of(shower, source)["kind"] == "centre"
    sofa["footprint"]["center"] = [3.0, 7.37]                                       # back edge 5.5 cm off the face
    assert LK.anchor_of(sofa, source)["kind"] == "centre"
    sofa["footprint"]["center"] = [3.0, 7.38]                                       # 4.5 cm: touches
    assert LK.anchor_of(sofa, source)["kind"] == "back_edge"


def test_anchor_follows_the_front_not_the_footprint_rotation(pair):
    """A footprint drawn with a rotation a quarter turn off its front: the back edge is the side opposite the front."""
    source, _final = pair
    basin = piece(source, "f_L0_007")             # size [0.6, 0.5], rotation 90, front 180: back on the east wall
    a = LK.anchor_of(basin, source)
    assert a == {"kind": "back_edge", "point": [9.85, 1.2], "wall_id": "w_L0_002"}
    turned = copy.deepcopy(basin)
    turned["footprint"].update(size=[0.5, 0.6], rotation_deg=0.0)                   # the same rectangle
    assert LK.anchor_of(turned, source) == a
    toilet = piece(source, "f_L0_006")            # 12.5 cm off the east wall: a free piece
    assert LK.anchor_of(toilet, source) == {"kind": "centre", "point": [9.4, 2.5], "wall_id": None}


# --------------------------------------------------------------------------
# check(): complete mode
# --------------------------------------------------------------------------

def test_the_example_final_passes(pair):
    source, final = pair
    assert LK.check(source, final, "complete") == []


@pytest.mark.parametrize("mutate, expect", [
    (lambda f: f["footprint"]["center"].__setitem__(1, f["footprint"]["center"][1] - 0.06), "anchor (back_edge) moved"),
    (lambda f: f["footprint"]["center"].__setitem__(0, f["footprint"]["center"][0] + 0.06), "anchor (back_edge) moved"),
    (lambda f: f.update(front_deg=272.0), "front 270.0 -> 272.0"),
    (lambda f: f.update(source="added_by_ai"), "source changed"),
    (lambda f: f.update(room_id="r_L-1_mutfak"), "room_id"),
    (lambda f: f.pop("modified_by_ai"), "without modified_by_ai"),
    (lambda f: f.update(drawn_type="armchair"), "do not hold the drawn values"),
    (lambda f: f.update(drawn_footprint={"center": [3.0, 7.0], "size": [2.2, 0.9], "rotation_deg": 0.0}),
     "do not hold the drawn values"),
])
def test_a_changed_piece_that_breaks_a_locked_rule_fails(pair, mutate, expect):
    source, final = pair
    mutate(piece(final, "f_L-1_002"))
    problems = LK.check(source, final, "complete")
    assert any(p.startswith("f_L-1_002") and expect in p for p in problems), problems


def test_moved_6_cm_fails_and_4_cm_passes(pair):
    source, final = pair
    bed = piece(final, "f_L0_002")                 # drawn, against the north wall; changed by AI here
    bed.update(modified_by_ai=True, drawn_type="bed_double", drawn_footprint=copy.deepcopy(bed["footprint"]),
               drawn_height=bed["height"])
    bed["footprint"]["center"][0] += 0.04          # along the wall: the anchor moves 4 cm
    assert LK.check(source, final, "complete") == []
    bed["footprint"]["center"][0] += 0.02
    assert any("f_L0_002: anchor (back_edge) moved 0.060 m" in p for p in LK.check(source, final, "complete"))
    final = example()                              # a drawn piece moved 1 cm without the AI labels
    piece(final, "f_L0_002")["footprint"]["center"][0] -= 0.01
    assert LK.check(source, final, "complete") == [
        "f_L0_002: type, footprint or height changed without modified_by_ai"]


def test_turned_2_degrees_fails(pair):
    source, final = pair
    bed = piece(final, "f_L0_002")
    bed["front_deg"] = 272.0
    bed["modified_by_ai"], bed["drawn_type"] = True, "bed_double"
    bed["drawn_footprint"], bed["drawn_height"] = copy.deepcopy(bed["footprint"]), bed["height"]
    assert any("f_L0_002: front 270.0 -> 272.0" in p for p in LK.check(source, final, "complete"))


def test_a_piece_pulled_off_its_wall_fails(pair):
    source, final = pair
    sofa = piece(final, "f_L-1_002")
    sofa["footprint"]["center"][1] -= 0.04         # 4 cm (within the anchor tolerance) but now 6.5 cm off the wall
    problems = LK.check(source, final, "complete")
    assert any("f_L-1_002: no longer against wall w_L-1_003" in p for p in problems), problems


def test_a_removed_drawn_piece_fails(pair):
    source, final = pair
    final["furniture"] = [f for f in final["furniture"] if f["id"] != "f_L0_002"]
    assert "f_L0_002: drawn bed_double removed" in LK.check(source, final, "complete")


@pytest.mark.parametrize("pid, mutate, what", [
    ("f_L0_006", lambda f: f.update(type="washbasin"), "type"),                     # toilet: fixed
    ("f_L0_006", lambda f: f["footprint"].update(size=[0.45, 0.75]), "footprint"),
    ("f_L-1_004", lambda f: f["footprint"]["center"].__setitem__(0, 8.01), "footprint"),   # counter run
    ("f_L-1_001", lambda f: f["footprint"].update(rotation_deg=90.0), "footprint"),        # stair
])
def test_fixed_equipment_must_stay_byte_equal(pair, pid, mutate, what):
    source, final = pair
    mutate(piece(final, pid))
    problems = LK.check(source, final, "complete")
    assert any(p.startswith(pid) and "changed" in p and what in p for p in problems), problems


def test_fixed_equipment_may_change_its_look(pair):
    source, final = pair
    piece(final, "f_L-1_004")["design"] = {"front_style": "flat", "colour": "navy"}
    assert LK.check(source, final, "complete") == []


@pytest.mark.parametrize("block, mutate", [
    ("walls", lambda b: b["walls"][0].update(thickness=0.3)),
    ("walls", lambda b: b["walls"].pop()),
    ("openings", lambda b: b["openings"][0].update(width=1.1)),
    ("rooms", lambda b: b["rooms"][0].update(label="Oturma Odası")),
])
def test_walls_openings_rooms_must_stay_byte_equal(pair, block, mutate):
    source, final = pair
    mutate(final)
    assert any(p.startswith(f"{block}: must stay as drawn") for p in LK.check(source, final, "complete"))


def test_a_new_piece_labelled_from_documents_fails(pair):
    source, final = pair
    fake = copy.deepcopy(piece(final, "f_L-1_003"))
    fake.update(id="f_L-1_099", source="from_documents")
    final["furniture"].append(fake)
    assert "f_L-1_099: labelled from_documents but not in the source building" in LK.check(source, final, "complete")


def test_unverified_pieces_keep_status_and_footprint(pair):
    source, final = pair
    for b in (source, final):
        piece(b, "f_L0_002")["status"] = "unverified"
    piece(final, "f_L0_002").update(type="bed_single", type_proposal=True, modified_by_ai=True, drawn_type="bed_double",
                                    drawn_footprint=copy.deepcopy(piece(source, "f_L0_002")["footprint"]),
                                    drawn_height=0.5, height=0.5)
    assert LK.check(source, final, "complete") == []                    # a type proposal, footprint kept
    piece(final, "f_L0_002")["status"] = "verified"
    assert any("unverified drawn piece became verified" in p for p in LK.check(source, final, "complete"))
    piece(final, "f_L0_002")["status"] = "unverified"
    piece(final, "f_L0_002")["footprint"]["size"] = [0.9, 2.0]
    assert any("unverified drawn piece changed its footprint" in p for p in LK.check(source, final, "complete"))


# --------------------------------------------------------------------------
# keep mode: the old byte rule (fit.FROZEN_KEYS)
# --------------------------------------------------------------------------

def test_keep_mode_refuses_any_change_of_a_drawn_piece(pair):
    source, final = pair
    problems = LK.check(source, final, "keep")
    assert any(p.startswith("f_L-1_002: changed") and "type" in p and "footprint" in p for p in problems), problems
    assert all(not p.startswith("f_L-1_003") for p in problems)        # added pieces are not drawn pieces


def test_keep_mode_passes_when_only_assets_and_looks_are_added(pair):
    source, _final = pair
    final = copy.deepcopy(source)
    for f in final["furniture"]:
        f["asset"] = {"library": "parametric", "asset_id": "x"}
        f["design"] = {"colour": "sage"}
    assert LK.check(source, final, "keep") == []


def test_keep_rooms_use_the_keep_rule_in_complete_mode(pair):
    source, final = pair
    assert LK.check(source, final, "complete", keep_rooms=["r_L0_yatak_odasi"]) == []   # the bed is unchanged
    problems = LK.check(source, final, "complete", keep_rooms=["r_L-1_salon"])
    assert any(p.startswith("f_L-1_002: changed") for p in problems)


def test_unknown_mode_is_an_error(pair):
    source, final = pair
    with pytest.raises(ValueError):
        LK.check(source, final, "loose")
