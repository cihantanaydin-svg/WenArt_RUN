"""CPU tests of the vision-check schema, prompt, labels and decoy (docs/milestone5.md §5.3).

The categories are generated from the building schema and the decor stage,
the per-view schema is strict (every label once, nothing else, bounded
extras, boxes and counts), inconsistent answers become ``unsure``, the
decoy sits over bare structure with the lowest-centre tie-break, and the
prompt lines have the spec's exact form.
"""
import numpy as np
import pytest

from wenart.building import load_schema
from wenart.furniture.decor import DECOR_TYPES
from wenart.recognition.vlm_client import grammar_of, schema_errors
from wenart.vision_check import preference as R
from wenart.vision_check import prompts as P
from wenart.vision_check import schemas as S


# --------------------------------------------------------------------------
# Categories and classes
# --------------------------------------------------------------------------

def test_categories_are_generated_from_the_enums():
    furniture = load_schema()["$defs"]["furniture"]["properties"]["type"]["enum"]
    assert S.FURNITURE_TYPES == tuple(t for t in furniture if t != "unknown") and "unknown" not in S.CATEGORIES
    assert S.OPENING_TYPES == ("door", "window")
    assert S.CATEGORIES == ("door", "window") + S.FURNITURE_TYPES + tuple(DECOR_TYPES) + (
        "lamp", "textile", "other_furniture", "other_object")
    assert S.SEEN_AS == S.CATEGORIES + ("nothing",) and len(set(S.CATEGORIES)) == len(S.CATEGORIES)
    # Milestone 8 (docs/milestone8.md §4): the decor stage adds rugs and wall art.
    assert set(DECOR_TYPES) == {"plant", "cushion", "book_set", "rug", "wall_art",
                                "vase", "bowl", "plant_small", "table_lamp", "mirror"}     # Milestone 9


def test_every_category_has_a_hint():
    assert set(P.HINTS) == set(S.CATEGORIES)


@pytest.mark.parametrize("category, box, cls", [
    ("door", None, "door"), ("window", None, "window"), ("sofa", None, "furniture"),
    ("other_furniture", None, "furniture"), ("plant", None, "decor"), ("cushion", None, "decor"),
    ("book_set", None, "decor"), ("textile", None, "decor"), ("other_object", None, "decor"),
    ("lamp", [400, 10, 450, 120], "fixture"), ("lamp", [400, 500, 450, 900], "furniture"),
    ("nothing", None, None),
    # Milestone 7 types (docs/milestone7.md §0): an added potted plant never rejects, as "plant".
    ("stair", None, "furniture"), ("side_table", None, "furniture"), ("floor_lamp", None, "furniture"),
    ("potted_plant", None, "decor"),
])
def test_category_classes(category, box, cls):
    assert S.category_class(category, box) == cls


def test_element_categories():
    assert S.element_category("door", "door") == "door"
    assert S.element_category("furniture", "sofa") == "sofa"
    assert S.element_category("furniture", "unknown") is None
    assert S.element_category("furniture", "sofa", type_unverified=True) is None
    assert S.element_category("decor", "plant") == "plant"


# --------------------------------------------------------------------------
# Schema strictness
# --------------------------------------------------------------------------

def good_answer() -> dict:
    return {"elements": {"E1": {"status": "present", "seen_as": "window", "confidence": 0.9},
                         "E2": {"status": "different", "seen_as": "sofa", "confidence": 0.7},
                         "E3": {"status": "absent", "seen_as": "nothing", "confidence": 0.8}},
            "extras": [{"category": "plant", "box": [10, 600, 90, 900], "confidence": 0.6}],
            "door_count": 1, "window_count": 2}


def test_view_schema_accepts_a_good_answer_and_drops_schema_id_for_the_grammar():
    schema = S.view_schema(["E1", "E2", "E3"])
    assert schema_errors(schema, good_answer()) == []
    assert "$schema" in schema and "$schema" not in grammar_of(schema)
    assert schema["properties"]["elements"]["required"] == ["E1", "E2", "E3"]


@pytest.mark.parametrize("mutate", [
    lambda a: a["elements"].pop("E3"),                                          # a label missing
    lambda a: a["elements"].update(E9=dict(a["elements"]["E1"])),              # an unknown label
    lambda a: a["elements"]["E1"].update(status="maybe"),                       # bad status
    lambda a: a["elements"]["E1"].update(seen_as="unknown"),                    # not a category
    lambda a: a["elements"]["E1"].update(confidence=1.5),
    lambda a: a["elements"]["E1"].update(extra="x"),                            # no extra fields
    lambda a: a.update(extras=[dict(a["extras"][0]) for _ in range(9)]),        # more than 8 extras
    lambda a: a["extras"][0].update(box=[0, 0, 1200, 10]),                      # box beyond 1000
    lambda a: a["extras"][0].update(box=[0, 0, 10]),                            # 3 numbers
    lambda a: a["extras"][0].update(category="nothing"),                        # extras need a category
    lambda a: a.update(door_count=1.5),                                         # counts are integers
    lambda a: a.update(window_count=21),
    lambda a: a.pop("door_count"),
    lambda a: a.update(comment="hi"),
])
def test_view_schema_rejects(mutate):
    answer = good_answer()
    mutate(answer)
    assert schema_errors(S.view_schema(["E1", "E2", "E3"]), answer)


def test_preference_schema():
    assert schema_errors(R.schema(), {"choice": "first", "confidence": 0.6}) == []
    assert schema_errors(R.schema(), {"choice": "both", "confidence": 0.6})
    assert schema_errors(R.schema(), {"choice": "same"})


# --------------------------------------------------------------------------
# Post-validation
# --------------------------------------------------------------------------

@pytest.mark.parametrize("answer, category, unverified, status", [
    ({"status": "present", "seen_as": "sofa"}, "sofa", False, "present"),
    ({"status": "present", "seen_as": "armchair"}, "sofa", False, "unsure"),       # present but another type
    ({"status": "present", "seen_as": "nothing"}, "sofa", False, "unsure"),
    ({"status": "different", "seen_as": "armchair"}, "sofa", False, "different"),
    ({"status": "different", "seen_as": "sofa"}, "sofa", False, "unsure"),         # different but the same type
    ({"status": "different", "seen_as": "nothing"}, "sofa", False, "unsure"),
    ({"status": "absent", "seen_as": "nothing"}, "sofa", False, "absent"),
    ({"status": "absent", "seen_as": "sofa"}, "sofa", False, "unsure"),
    ({"status": "unsure", "seen_as": "sofa"}, "sofa", False, "unsure"),
    ({"status": "present", "seen_as": "wardrobe"}, None, True, "present"),         # type unverified: any piece
    ({"status": "present", "seen_as": "nothing"}, None, True, "unsure"),
    ({"status": "different", "seen_as": "wardrobe"}, None, True, "different"),
    # Milestone 7: a drawn potted plant seen as the decor "plant" (a floor lamp as a "lamp") is the same object.
    ({"status": "present", "seen_as": "plant"}, "potted_plant", False, "present"),
    ({"status": "present", "seen_as": "potted_plant"}, "potted_plant", False, "present"),
    ({"status": "different", "seen_as": "plant"}, "potted_plant", False, "present"),
    ({"status": "different", "seen_as": "lamp"}, "floor_lamp", False, "present"),
    ({"status": "different", "seen_as": "side_table"}, "floor_lamp", False, "different"),
    # ... and the other way round (review vision-2): the decor plant seen as potted_plant, a lamp as floor_lamp.
    ({"status": "present", "seen_as": "potted_plant"}, "plant", False, "present"),
    ({"status": "different", "seen_as": "potted_plant"}, "plant", False, "present"),
    ({"status": "different", "seen_as": "floor_lamp"}, "lamp", False, "present"),
    ({"status": "different", "seen_as": "vase"}, "plant", False, "different"),
])
def test_normalise_answer(answer, category, unverified, status):
    out, changed = S.normalise_answer(dict(answer, confidence=0.5), category, unverified)
    assert out["status"] == status
    assert changed == (status != answer["status"])
    if changed:
        assert out["raw"]["status"] == answer["status"]


# --------------------------------------------------------------------------
# Decoy
# --------------------------------------------------------------------------

def test_place_decoy_over_bare_structure_lowest_then_central():
    H, W = 100, 200
    index = np.ones((H, W), dtype=np.uint16)                 # everything indexed ...
    depth = np.full((H, W), 3000, dtype=np.uint16)
    index[10:40, 20:120] = 0                                   # ... but two bare patches
    index[60:95, 100:200] = 0
    box = P.place_decoy(index, depth)
    bw, bh = round(0.18 * W), round(0.25 * H)
    assert box[2] - box[0] == bw and box[3] - box[1] == bh
    assert (index[box[1]:box[3], box[0]:box[2]] == 0).mean() >= 0.98
    assert box[1] >= 60                                        # the lower patch wins
    # Among the lowest windows the one nearest the horizontal centre.
    x0s = [x for x in range(0, W - bw + 1, 10) if (index[box[1]:box[1] + bh, x:x + bw] == 0).mean() >= 0.98]
    assert box[0] == min(x0s, key=lambda x: (abs(x + bw / 2 - W / 2), x))
    # Background (depth 0) is not bare structure; nothing bare -> no decoy.
    assert P.place_decoy(index, np.zeros_like(depth)) is None
    assert P.place_decoy(np.ones((H, W), np.uint16), depth) is None


def test_decoy_type_first_allowed_absent_then_fallback():
    assert P.decoy_type("living", {"sofa", "armchair"}, ["armchair", "desk"]) == "table_coffee"
    living = {"sofa", "armchair", "table_coffee", "tv_unit", "bookshelf", "table_dining", "chair"}
    assert P.decoy_type("living", living, ["armchair", "desk", "bookshelf", "bathtub"]) == "desk"
    assert P.decoy_type("storage", set(), ["armchair", "desk", "bookshelf", "bathtub"]) == "armchair"
    assert P.decoy_type("balcony", {"armchair"}, ["armchair", "desk"]) == "desk"
    assert P.decoy_type(None, {"armchair", "desk"}, ["armchair", "desk"]) is None


# --------------------------------------------------------------------------
# Items and prompt
# --------------------------------------------------------------------------

def expected_fixture() -> dict:
    def el(i, wid, kind, typ, px, role, box, border=False, unverified=False, source="from_documents"):
        return {"index": i, "wenart_id": wid, "kind": kind, "type": typ, "pixels": px, "role": role,
                "box_1000": box, "touches_border": border, "type_unverified": unverified, "source": source}
    return {"camera": "cam_r_salon_2", "room_id": "r", "room_type": "living", "elements": [
        el(1, "win_1", "window", "window", 5000, "required", [262, 230, 442, 581]),
        el(2, "f_tv", "furniture", "tv_unit", 4000, "required", [83, 674, 362, 933]),
        el(3, "f_bs", "furniture", "bookshelf", 3000, "optional", [898, 315, 1000, 930], border=True),
        el(4, "f_x", "furniture", "unknown", 2000, "required", [10, 10, 50, 50], unverified=True),
        el(5, "dec_1", "decor", "plant", 10, "ignore", [0, 0, 1, 1], source="added_by_ai"),
    ]}


def test_check_items_labels_by_area_with_the_decoy_shuffled_in():
    exp = expected_fixture()
    decoy = {"type": "armchair", "box_px": [0, 0, 10, 10], "box_1000": [100, 500, 280, 750]}
    items = P.check_items(exp, decoy)
    assert [it["label"] for it in items] == ["E1", "E2", "E3", "E4", "E5"]          # 4 asked + decoy, ignore left out
    real = [it["wenart_id"] for it in items if not it["decoy"]]
    assert real == ["win_1", "f_tv", "f_bs", "f_x"]
    pos = P.camera_hash("cam_r_salon_2") % 5
    assert items[pos]["decoy"] and items[pos]["type"] == "armchair" and items[pos]["wenart_id"] is None
    assert P.check_items(exp, decoy) == items                                        # deterministic
    other = dict(exp, camera="cam_other_9")
    assert [i for i, it in enumerate(P.check_items(other, decoy)) if it["decoy"]] == [P.camera_hash("cam_other_9") % 5]
    assert all(not it["decoy"] for it in P.check_items(exp, None))


def test_swap_replaces_one_type_in_the_list():
    items = P.check_items(expected_fixture(), None, swap={"id": "f_tv", "type": "desk"})
    tv = next(it for it in items if it["wenart_id"] == "f_tv")
    assert tv["type"] == "desk" and tv["category"] == "desk" and tv["swapped_from"] == "tv_unit"


def test_new_furniture_types_have_photo_hints_and_plant_stays_decor():
    for t in ("stair", "side_table", "floor_lamp", "potted_plant"):
        assert t in S.CATEGORIES and t in P.HINTS and P.HINTS[t] != t
    assert "plant" in S.DECOR_CATEGORIES and S.category_class("plant") == "decor"
    assert S.element_category("furniture", "potted_plant") == "potted_plant"
    # Both ways round (review vision-2): the decor plant seen as potted_plant is the same object too.
    # Milestone 8: the decor rug may be seen as a "textile" (its hint: "curtain or rug").
    # Milestone 9: the decor table lamp may be seen as a "lamp", the small plant as a "plant".
    assert S.EQUIVALENT == {"potted_plant": ("plant",), "plant": ("potted_plant", "plant_small"),
                            "floor_lamp": ("lamp",), "lamp": ("floor_lamp", "table_lamp"), "rug": ("textile",),
                            "textile": ("rug",), "table_lamp": ("lamp",), "plant_small": ("plant",)}
    for t in ("vase", "bowl", "plant_small", "table_lamp", "mirror"):
        assert t in S.DECOR_CATEGORIES and S.category_class(t) == "decor" and P.HINTS[t] != t
    line = P.element_line({"label": "E1", "type": "stair", "box_1000": [1, 2, 3, 4]})
    assert line == "- E1: stair (staircase with steps); expected inside box [1, 2, 3, 4]"


def test_prompt_lines_have_the_spec_form():
    items = P.check_items(expected_fixture(), None)
    lines = [P.element_line(it) for it in items]
    assert lines[1] == "- E2: tv_unit (low long cabinet / sideboard); expected inside box [83, 674, 362, 933]"
    assert lines[2].endswith("[898, 315, 1000, 930], cut by the image edge")
    assert lines[3].startswith("- E4: furniture piece (type unverified) (")
    text = P.check_prompt(items, "Salon", "living", (1920, 1080))
    assert "NOT a door" in text and "Do not list walls, floor, ceiling or the view outside a window" in text
    assert "lamp" in text and "curtain" in text                    # lamps and textiles are not excluded
    assert "Image 2" not in text
    plan = P.check_prompt(items, "Salon", "living", (1920, 1080), plan_ab=True)
    assert "Image 2 is the source floor plan" in plan and "from image 1 only" in plan
    for line in lines:
        assert line in text
