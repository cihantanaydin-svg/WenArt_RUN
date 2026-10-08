"""CPU tests of the AI typing of unnamed drawn objects (docs/milestone7.md §3.2, §3.3, §11 Y).

- the size table (``wenart/recognition/size_table.yaml``): covers every furniture type of the building schema, has
  sane ranges, and every synthetic block size, layout size and real01 reference piece fits its type;
- the symbol question (request item shape);
- the two-pass table: agree, disagree, size veto, ``not_furniture`` kept with ``build: false``, room veto (and the
  types allowed everywhere / in halls), empty answers never agree, the confidence rule, the front rule, and the
  evidence and conflict shapes against the building schema.

No model runs here: the answers are hand-made dicts in the answer schema.
"""
from pathlib import Path

import jsonschema
import pytest
import yaml

from wenart import building as B
from wenart.recognition import answers as A
from wenart.recognition import prompts
from wenart.recognition import schemas
from wenart.recognition import symbols as S

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "tests" / "fixtures" / "real01_reference.yaml"
FT = 0.3048

MODELS = A.load_models()
QWEN_ID = MODELS["qwen"]["id"]
GLM_ID = MODELS["glm"]["id"]


def answer(ftype, front="none", confidence=0.8, reason="seen from above"):
    return {"type": ftype, "front": front, "confidence": confidence, "reason": reason}


def candidate(size=(1.6, 2.0), rotation=0.0, **extra):
    w, d = size
    cand = {"key": "sym_L0_1", "file": "plan.pdf", "page": 1, "level": "L0", "element_id": "f_L0_001",
            "footprint": {"center": [2.0, 2.0], "size": [w, d], "rotation_deg": rotation},
            "strokes": [[[2.0 - w / 2, 2.0 - d / 2], [2.0 + w / 2, 2.0 - d / 2], [2.0 + w / 2, 2.0 + d / 2],
                         [2.0 - w / 2, 2.0 + d / 2], [2.0 - w / 2, 2.0 - d / 2]]],
            "bbox": [2.0 - w / 2, 2.0 - d / 2, 2.0 + w / 2, 2.0 + d / 2]}
    cand.update(extra)
    return cand


@pytest.fixture(scope="module")
def table():
    return S.load_size_table()


# --------------------------------------------------------------------------
# Size table
# --------------------------------------------------------------------------

def test_size_table_covers_every_schema_furniture_type(table):
    enum = B.load_schema()["$defs"]["furniture"]["properties"]["type"]["enum"]
    assert set(table) == set(enum) - {"unknown"}, "unknown has no size range on purpose (it fits nothing)"
    data = yaml.safe_load(S.SIZE_TABLE_PATH.read_text(encoding="utf-8"))
    assert data["tolerance"] == S.SIZE_TOLERANCE
    for name, spec in data["types"].items():
        assert spec.get("source"), f"{name}: no source noted"
        (w0, w1), (d0, d1) = table[name]
        assert 0 < w0 <= w1 and 0 < d0 <= d1, name
    # The new M7 types are in the table.
    for name in ("stair", "side_table", "floor_lamp", "potted_plant"):
        assert name in table


def test_fits_either_orientation_with_the_tolerance(table):
    assert S.fits(table, "bed_double", (1.6, 2.0))
    assert S.fits(table, "bed_double", (2.0, 1.6))                    # either orientation
    assert S.fits(table, "bed_double", (2.0 * 1.149, 2.25 * 1.149))   # +15 % on top of the range
    assert not S.fits(table, "bed_double", (0.5, 0.5))
    assert not S.fits(table, "chair", (0.65 * 1.16, 0.5))
    assert not S.fits(table, "unknown", (1.0, 1.0))
    assert not S.fits(table, "not_furniture", (1.0, 1.0))
    # The core's tuple form and the YAML dict form give the same answers.
    yaml_form = {"chair": {"width": [0.35, 0.65], "depth": [0.35, 0.65]}}
    assert S.fits(yaml_form, "chair", (0.45, 0.45)) and not S.fits(yaml_form, "chair", (1.0, 1.0))


def test_synthetic_block_and_layout_sizes_fit_their_type(table):
    from wenart.furniture.schemas import SIZE_OPTIONS
    from wenart.synthetic.blocks import BLOCKS
    for name, (ftype, w, d) in BLOCKS.items():
        assert S.fits(table, ftype, (w, d)), f"block {name} {w} x {d} does not fit {ftype}"
    for ftype, sizes in SIZE_OPTIONS.items():
        for w, d in sizes:
            assert S.fits(table, ftype, (w, d)), f"layout size {w} x {d} does not fit {ftype}"


def test_real01_reference_pieces_fit_an_accepted_type(table):
    ref = yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))
    checked = 0
    for piece in ref["furniture"]:
        if piece.get("not_a_piece") or "size_wd_ft" not in piece:
            continue
        size = [v * FT for v in piece["size_wd_ft"]]
        accepted = [t for t in piece.get("type_accept") or [] if t in table]
        assert accepted, piece["id"]
        assert any(S.fits(table, t, size) for t in accepted), f"{piece['id']} {size} fits none of {accepted}"
        assert S.fits(table, piece["type"], size) or piece["type"] not in table, piece["id"]
        checked += 1
    assert checked == 20


# --------------------------------------------------------------------------
# Question
# --------------------------------------------------------------------------

def test_question_is_the_request_item_of_the_rendered_crops(tmp_path):
    from wenart.recognition import crops
    cand = candidate(room_type="bedroom", room_id="r_L0_bed")
    rendered = crops.render_pair(cand, {"walls": [], "others": []}, tmp_path / "crops", cand["key"])
    item = S.question(cand, rendered)
    assert item["key"] == "sym_L0_1" and item["task"] == "symbol_type" and item["page"] == 1
    assert item["images"] == ["crops/sym_L0_1_ctx.png", "crops/sym_L0_1_iso.png"]
    assert item["input_sha256"] == rendered["input_sha256"]
    assert item["context"]["footprint"]["size"] == [1.6, 2.0] and item["context"]["crop"]["ctx_box"]
    A.check_item(item)
    # The candidate may carry its crops instead.
    assert S.question(dict(cand, crops=rendered)) == item
    with pytest.raises(ValueError):
        S.question(cand)
    # The item carries its question facts (prep pod P5): what answers.call_args asks is what was hashed.
    assert item["question"] == rendered["question"] == S.question_facts(cand, "vector")
    assert item["question"]["choices"] == S.choices_for((1.6, 2.0))
    # A room type without a printed label is not stated (it would be a guess): "an unlabelled room".
    assert item["question"]["room"] == {"label": None, "type": None}


# --------------------------------------------------------------------------
# The question facts (prep pod finding P5)
# --------------------------------------------------------------------------

def test_choices_are_the_types_whose_size_fits_plus_unknown_and_not_furniture(table):
    chair = S.choices_for((0.4618, 0.3824), table)          # a real01 dining chair
    assert chair[-2:] == ["unknown", "not_furniture"]
    assert "chair" in chair and "nightstand" in chair and "side_table" in chair
    for wrong in ("armchair", "bed_double", "sofa", "tv_unit", "table_dining", "wardrobe"):
        assert wrong not in chair, wrong
    assert all(S.fits(table, t, (0.4618, 0.3824)) for t in chair[:-2])
    order = list(schemas.SYMBOL_TYPE_CHOICES)
    assert chair == sorted(chair, key=order.index)           # the schema's order: deterministic
    night = S.choices_for((0.4956, 0.4868), table)          # a real01 nightstand (GLM said tv_unit)
    assert "nightstand" in night and "tv_unit" not in night
    assert S.choices_for((2.0295, 1.7795), table)[:1] == ["bed_double"]
    assert S.choices_for((1.4966, 0.0), table) == ["unknown", "not_furniture"]       # a sliver fits nothing
    assert S.choices_for(None, table) == list(schemas.SYMBOL_TYPE_CHOICES)          # no footprint: the full list
    # Sub-millimetre noise does not change the list.
    assert S.choices_for((0.46184, 0.38236), table) == chair


def test_question_facts_vector_and_raster(table):
    cand = candidate(size=(0.4618, 0.3824), room_type="dining", room_label=" Dining\n",
                     neighbours={"similar": 6, "next_to": [1.2383, 0.7353], "around": 6})
    facts = S.question_facts(cand, "vector", table)
    assert facts == {"kind": "vector", "choices": S.choices_for((0.4618, 0.3824), table), "size_m": [0.46, 0.38],
                     "room": {"label": "Dining", "type": "dining"},
                     "neighbours": {"similar": 6, "next_to": [1.24, 0.74], "around": 6}}
    # Raster: room names and clusters on a raster page may change with the label answers of the same round
    # (review raster-1/raster-2), so the symbol question never depends on them.
    raster = S.question_facts(cand, "raster", table)
    assert raster == {"kind": "raster", "choices": facts["choices"], "size_m": [0.46, 0.38], "room": None,
                      "neighbours": None}
    # No room: nothing said about one; a face without a label: unlabelled, no guessed type.
    assert S.question_facts(candidate(size=(0.46, 0.38)), "vector", table)["room"] is None
    unl = S.question_facts(candidate(size=(0.46, 0.38), room_index=3, room_type="hall"), "vector", table)
    assert unl["room"] == {"label": None, "type": None}
    # A label whose room type has no plain words (other, unknown, an exterior area): the label alone.
    ext = S.question_facts(candidate(size=(0.46, 0.38), room_label="Parking", room_type=None), "vector", table)
    assert ext["room"] == {"label": "Parking", "type": None}
    with pytest.raises(ValueError):
        S.question_facts(cand, "photo", table)


def _piece(key, centre, size, room=0, rotation=0.0):
    return {"key": key, "footprint": {"center": list(centre), "size": list(size), "rotation_deg": rotation},
            "room_index": room}


def test_neighbour_facts_count_similar_pieces_around_a_larger_one():
    table = _piece("t", (10.0, 10.0), (1.24, 0.74), rotation=90.0)       # 0.74 wide in x, 1.24 in y
    chairs = [_piece("c1", (10.0, 9.18), (0.46, 0.38), rotation=90.0), _piece("c2", (10.0, 10.82), (0.46, 0.38),
                                                                               rotation=90.0),
              _piece("c3", (9.40, 9.70), (0.46, 0.38)), _piece("c4", (9.40, 10.30), (0.465, 0.379)),
              _piece("c5", (10.60, 9.70), (0.46, 0.38)), _piece("c6", (10.60, 10.30), (0.465, 0.38))]
    bed = _piece("b", (3.0, 3.0), (2.03, 1.78), room=1, rotation=90.0)
    stands = [_piece("n1", (1.85, 3.6), (0.4956, 0.4868), room=1), _piece("n2", (4.15, 3.6), (0.4956, 0.4456),
                                                                           room=1)]
    far = _piece("x", (20.0, 20.0), (0.46, 0.38), room=2)                # same size, another room
    facts = S.neighbour_facts([table] + chairs + [bed] + stands + [far])
    for c in chairs:
        assert facts[c["key"]] == {"similar": 6, "next_to": [1.24, 0.74], "around": 6}, c["key"]
    assert facts["t"] == {"similar": None, "next_to": None, "around": None}
    for n in stands:
        assert facts[n["key"]] == {"similar": 2, "next_to": [2.03, 1.78], "around": 2}
    assert facts["b"] == {"similar": None, "next_to": None, "around": None}
    assert facts["x"] == {"similar": None, "next_to": None, "around": None}
    # Deterministic: the input order does not matter.
    assert S.neighbour_facts(list(reversed([table] + chairs + [bed] + stands + [far]))) == facts
    # Similar pieces without a larger one next to them: only the count.
    sofas = [_piece("s1", (0.0, 0.0), (1.89, 0.71)), _piece("s2", (5.0, 0.0), (1.90, 0.70), rotation=90.0)]
    assert S.neighbour_facts(sofas)["s1"] == {"similar": 2, "next_to": None, "around": None}


# --------------------------------------------------------------------------
# A typed piece without a front: the type's width/depth convention (review ingest-6)
# --------------------------------------------------------------------------

def test_oriented_size_follows_the_type_convention(table):
    # real01's bed: footprint [2.03, 1.78] at 90 deg (no-front rule: width = longer side). A bed_double is
    # 1.35-2.0 wide and 1.85-2.25 deep: width = the 1.78 side.
    size, rot, swapped = S.oriented_size((2.0295, 1.7795), 90.0, "bed_double", table)
    assert swapped and size == (1.7795, 2.0295) and rot == 0.0
    # Already in the convention: unchanged.
    assert S.oriented_size((1.9, 0.7), 0.0, "sofa", table) == ((1.9, 0.7), 0.0, False)
    size, rot, swapped = S.oriented_size((0.7, 1.9), 0.0, "sofa", table)
    assert swapped and size == (1.9, 0.7) and rot == 90.0
    # Types with the same width and depth range: nothing to decide.
    assert S.oriented_size((0.46, 0.38), 90.0, "chair", table) == ((0.46, 0.38), 90.0, False)
    assert S.oriented_size((1.0, 2.0), 30.0, "unknown", table) == ((1.0, 2.0), 30.0, False)


# --------------------------------------------------------------------------
# Two-pass rule
# --------------------------------------------------------------------------

def test_both_passes_agree_and_the_size_fits_gives_a_verified_ai_type(table):
    res = S.decide(candidate(), {"qwen": answer("bed_double", "bottom", 0.95), "glm": answer("bed_double", "bottom",
                                                                                              0.7)},
                   table, "bedroom")
    assert res["type"] == "bed_double" and res["status"] == "verified" and res["type_method"] == "ai_two_pass"
    assert res["confidence"] == 0.7 and res["build"] is True and res["conflict"] is None
    assert res["front"] == 270.0
    assert [c["type"] for c in res["type_candidates"]] == ["bed_double", "bed_double"]
    assert [(e["model"], e["pass"], e["method"]) for e in res["ai_evidence"]] == [(QWEN_ID, 1, "ai"), (GLM_ID, 2, "ai")]
    # Confidence = the lower of the two, capped at 0.9.
    res = S.decide(candidate(), {"qwen": answer("bed_double", confidence=1.0), "glm": answer("bed_double",
                                                                                              confidence=0.97)},
                   table, "bedroom")
    assert res["confidence"] == 0.9


def test_disagreeing_passes_keep_unknown_with_both_candidates_and_a_conflict(table):
    res = S.decide(candidate(size=(0.45, 0.45)), {"qwen": answer("chair"), "glm": answer("armchair")}, table,
                   "living")
    assert res["type"] == "unknown" and res["status"] == "unverified" and res["type_method"] == "none"
    assert {c["type"] for c in res["type_candidates"]} == {"chair", "armchair"}
    assert res["conflict"]["kind"] == "symbol_type_disagreement"
    assert res["conflict"]["element_ids"] == ["f_L0_001"]
    assert "chair" in res["conflict"]["description"] and "armchair" in res["conflict"]["description"]
    assert res["build"] is True and len(res["ai_evidence"]) == 2
    # one not_furniture against a type is a disagreement too (the piece is built as unknown)
    res = S.decide(candidate(), {"qwen": answer("not_furniture"), "glm": answer("bed_double")}, table, "bedroom")
    assert res["type"] == "unknown" and res["conflict"] is not None and res["build"] is True


def test_the_size_veto_tests_what_the_choices_offered(table):
    """The offered choices and the size veto test the same sides (rounded to 1 mm): a type the models could not be
    offered is never accepted, and an offered type is never vetoed, by sub-millimetre noise at a range edge."""
    edge = 0.35 / (1.0 + S.SIZE_TOLERANCE)                      # the chair's lower edge, 0.304348 m
    for side in (edge - 0.0004, edge + 0.00001, edge + 0.0004, 0.3046):
        size = (side, 0.40)
        offered = "chair" in S.choices_for(size, table)
        res = S.decide(candidate(size=size), {"qwen": answer("chair"), "glm": answer("chair")}, table, "dining")
        assert (res["type"] == "chair") == offered, (side, offered, res["type"])
    assert "chair" not in S.choices_for((edge + 0.00001, 0.40), table)        # 0.30436 rounds to 0.304: outside
    assert S.sides_mm((0.30436, 0.4)) == (0.304, 0.4)


def test_size_veto_when_both_say_a_type_the_footprint_cannot_be(table):
    res = S.decide(candidate(size=(0.5, 0.5)), {"qwen": answer("bed_double"), "glm": answer("bed_double")}, table,
                   "bedroom")
    assert res["type"] == "unknown" and res["status"] == "unverified" and res["type_method"] == "none"
    assert res["conflict"]["kind"] == "symbol_type_disagreement" and "size range" in res["conflict"]["description"]
    assert any("size veto" in w for w in res["warnings"])
    assert [c["type"] for c in res["type_candidates"]] == ["bed_double", "bed_double"]


def test_the_corner_sofa_needs_an_l_outline(table):
    """Milestone 10: ``sofa_corner`` is offered and accepted only for a footprint the core found L-shaped."""
    assert "sofa_corner" not in S.choices_for((2.6, 1.6), table)
    assert "sofa_corner" in S.choices_for((2.6, 1.6), table, "L")
    plain = S.question_facts(candidate(size=(2.6, 1.6)), "vector", table)
    assert "shape" not in plain and "sofa_corner" not in plain["choices"]          # other items' facts unchanged
    cand = candidate(size=(2.6, 1.6))
    cand["footprint"]["shape"] = "L"
    facts = S.question_facts(cand, "vector", table)
    assert facts["shape"] == "L" and "sofa_corner" in facts["choices"]
    assert "Its outline is L-shaped" in prompts.symbol_type_prompt(facts)
    both = {"qwen": answer("sofa_corner"), "glm": answer("sofa_corner")}
    res = S.decide(cand, both, table, None)
    assert res["type"] == "sofa_corner" and res["type_method"] == "ai_two_pass" and res["status"] == "verified"
    veto = S.decide(candidate(size=(2.6, 1.6)), both, table, None)
    assert veto["type"] == "unknown" and "not L-shaped" in veto["conflict"]["description"]
    assert any("shape veto" in w for w in veto["warnings"])


def test_new_types_have_hints_and_size_ranges(table):
    for ftype in ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
                  "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet"):
        assert ftype in table and ftype in prompts.SYMBOL_HINTS and ftype in prompts.SYMBOL_TYPE_HINTS
    assert S.fits(table, "sofa_corner", (4.38, 1.97))                     # real02's basement corner sofa
    assert "bar_stool" in S.choices_for((0.42, 0.42), table) and "crib" in S.choices_for((0.7, 1.4), table)


def test_not_furniture_by_both_is_kept_unbuilt(table):
    res = S.decide(candidate(size=(0.9, 0.3)), {"qwen": answer("not_furniture"), "glm": answer("not_furniture")},
                   table, "living")
    assert res["type"] == "unknown" and res["status"] == "unverified"
    assert res["build"] is False and res["note"] == "drawn symbol, not built"
    assert res["conflict"] is None and res["front"] is None
    assert len(res["type_candidates"]) == 2 and len(res["ai_evidence"]) == 2


def test_room_veto_keeps_the_type_unverified(table):
    res = S.decide(candidate(size=(1.7, 0.75)), {"qwen": answer("bathtub"), "glm": answer("bathtub")}, table,
                   "bedroom")
    assert res["type"] == "bathtub" and res["type_method"] == "ai_two_pass" and res["status"] == "unverified"
    assert any("not a type allowed in a bedroom" in w for w in res["warnings"])
    assert res["conflict"] is None


@pytest.mark.parametrize("ftype,size,room", [
    ("side_table", (0.45, 0.45), "bathroom"),      # allowed everywhere
    ("floor_lamp", (0.43, 0.43), "living"),
    ("potted_plant", (0.5, 0.5), "kitchen"),
    ("chair", (0.4, 0.45), "dining"),              # dining (§6.5) even before the layout table has it
    ("table_dining", (1.24, 0.73), "dining"),
    ("sofa", (1.9, 0.7), None),                    # unknown room: no veto possible
    ("sofa", (1.9, 0.7), "unknown"),
])
def test_types_allowed_in_the_room_stay_verified(table, ftype, size, room):
    res = S.decide(candidate(size=size), {"qwen": answer(ftype), "glm": answer(ftype)}, table, room)
    assert res["type"] == ftype and res["status"] == "verified", res["warnings"]


def test_a_stair_named_by_both_passes_is_never_verified(table):
    both = {"qwen": answer("stair"), "glm": answer("stair")}
    res = S.decide(candidate(size=(2.44, 1.53)), both, table, "hall")
    assert res["type"] == "stair" and res["status"] == "unverified"
    assert not any("not a type allowed" in w for w in res["warnings"])        # stair is allowed in halls
    assert any("no treads" in w for w in res["warnings"])
    res = S.decide(candidate(size=(2.44, 1.53)), both, table, "bedroom")
    assert res["status"] == "unverified" and any("not a type allowed" in w for w in res["warnings"])


@pytest.mark.parametrize("other", [None, {}, {"type": ""}, {"type": "couch", "front": "top", "confidence": 0.9,
                                                              "reason": ""}, "sofa"])
def test_empty_or_invalid_answers_never_agree(table, other):
    res = S.decide(candidate(size=(1.9, 0.7)), {"qwen": answer("sofa"), "glm": other}, table, "living")
    assert res["type"] == "unknown" and res["status"] == "unverified" and res["type_method"] == "none"
    assert res["conflict"] is None
    assert [c["type"] for c in res["type_candidates"]] == ["sofa"]
    assert len(res["ai_evidence"]) == 1
    assert any("pass 2" in w for w in res["warnings"])
    res = S.decide(candidate(), {}, table, "living")
    assert res["type"] == "unknown" and res["ai_evidence"] == [] and len(res["warnings"]) == 2
    res = S.decide(candidate(), None, table, "living")
    assert res["type"] == "unknown"


def test_both_unknown_leaves_the_type_open_without_a_conflict(table):
    res = S.decide(candidate(), {"qwen": answer("unknown"), "glm": answer("unknown")}, table, "living")
    assert res["type"] == "unknown" and res["status"] == "unverified" and res["conflict"] is None
    assert any("type left open" in w for w in res["warnings"])


def test_front_rule(table):
    both = lambda f1, f2: {"qwen": answer("sofa", f1), "glm": answer("sofa", f2)}   # noqa: E731
    sofa = (1.9, 0.7)
    # No deterministic front: both passes must name the same side.
    assert S.decide(candidate(size=sofa), both("top", "top"), table, "living")["front"] == 90.0
    assert S.decide(candidate(size=sofa), both("top", "left"), table, "living")["front"] is None
    assert S.decide(candidate(size=sofa), both("top", "none"), table, "living")["front"] is None
    # A unique deterministic front is kept when a pass names a side; a pass naming another side does not remove it
    # (trust order: vector > AI; pod B: both models named one fixed side for every bed): the disagreement is a listed
    # conflict (this assertion was 'front is None' before, changed on purpose).
    det = candidate(size=sofa, front_deg=270.0)
    assert S.decide(det, both("bottom", "none"), table, "living")["front"] == 270.0
    res = S.decide(det, both("bottom", "bottom"), table, "living")
    assert res["front"] == 270.0 and res["front_conflict"] is None
    for answers in (both("bottom", "top"), both("top", "top"), both("top", "none")):
        res = S.decide(det, answers, table, "living")
        assert res["front"] == 270.0 and res["front_assumed"] is False
        assert any("disagrees with the drawn front 270" in w and "drawn front is kept" in w for w in res["warnings"])
        fc = res["front_conflict"]
        assert fc["kind"] == "symbol_front_disagreement" and fc["resolution"] == S.FRONT_CONFLICT_RESOLUTION
    # Both passes 'none' (no pass contradicts it) and the type accepted: the drawn front stays, marked assumed
    # (review ingest-6; this assertion was 'front is None' before, changed on purpose).
    res = S.decide(det, both("none", "none"), table, "living")
    assert res["front"] == 270.0 and res["front_assumed"] is True
    assert any("front assumed" in w for w in res["warnings"])
    assert S.decide(det, both("bottom", "none"), table, "living")["front_assumed"] is False   # a pass names it
    # The generic core's candidates carry the rule that found the drawn front: an assumed front names it.
    wall = "only side within 0.25 m of a wall is the back"
    ruled = candidate(size=sofa, front_candidates=[{"front_deg": 270.0, "rule": wall}, 270.0])
    res = S.decide(ruled, both("none", "none"), table, "living")
    assert res["front"] == 270.0 and res["front_assumed"] is True and res["front_rule"] == wall
    assert any("front assumed" in w and wall in w for w in res["warnings"])
    assert S.decide(ruled, both("bottom", "bottom"), table, "living")["front_rule"] is None    # agreed: not assumed
    assert S.decide(candidate(size=sofa, front_candidates=[{"front_deg": 270.0, "rule": wall},
                                                           {"front_deg": 90.0, "rule": "pillows"}]),
                    both("none", "none"), table, "living")["front"] is None                    # two drawn fronts
    # Two different deterministic candidates are not unique: the passes decide.
    two = candidate(size=sofa, front_candidates=[0.0, 180.0])
    assert S.decide(two, both("left", "left"), table, "living")["front"] == 180.0
    # A rotated footprint: the side snaps to the nearest footprint axis.
    rot = candidate(size=sofa, rotation=30.0)
    assert S.decide(rot, both("top", "top"), table, "living")["front"] == 120.0
    assert S.decide(rot, both("right", "right"), table, "living")["front"] == 30.0


def test_evidence_and_conflict_follow_the_building_schema(table):
    defs = B.load_schema()["$defs"]
    res = S.decide(candidate(size=(0.45, 0.45)), {"qwen": answer("chair", "top"), "glm": answer("armchair")},
                   table, "living")
    for ev in res["ai_evidence"]:
        jsonschema.validate(ev, defs["evidence"])
        assert ev["file"] == "plan.pdf" and ev["page"] == 1 and ev["entity"] == "recognition:sym_L0_1"
        assert ev["text"] in ("chair", "armchair") and "reason" in ev and "front" in ev
    conflict = dict(res["conflict"], id="c_001")
    jsonschema.validate(conflict, defs["conflict"])
    assert res["conflict"]["kind"] in defs["conflict"]["properties"]["kind"]["enum"]


def test_decide_reads_the_model_ids_and_passes_from_check_yaml():
    assert A.MODEL_KEYS == ("qwen", "glm")
    assert A.model_info("qwen")["pass"] == 1 and A.model_info("glm")["pass"] == 2
    assert A.model_info("qwen")["slug"] == MODELS["qwen"]["slug"]
    with pytest.raises(A.UsageError):
        A.model_info("llava")
    assert set(schemas.SYMBOL_TYPE_CHOICES) == set(schemas.FURNITURE_TYPES) | {"not_furniture"}


# --------------------------------------------------------------------------
# The core applies the decision (review ingest-6) and asks the improved question (prep pod P5): real01
# --------------------------------------------------------------------------

def _bed_item(front_candidates=None):
    from wenart.ingest.model import FurnitureItem
    return FurnitureItem(type="unknown", type_raw=None, center=(5.86, 9.38), size=(2.0295, 1.7795), rotation_deg=90.0,
                         front_deg=None, box=[0, 0, 1, 1], entity="path:1", evidence={"method": "vector"},
                         status="unverified", type_method="none",
                         details={"candidate_key": "sym_L0_001", "front_candidates": front_candidates or []})


def test_core_keeps_the_drawn_front_assumed_when_both_passes_answer_none(table):
    from wenart.ingest.generic import core
    pillows = "head = side with >= 2 small closed shapes"
    fronts = [{"front_deg": 270.0, "rule": pillows}]
    cand = candidate(size=(2.0295, 1.7795), rotation=90.0, front_candidates=core._front_values(
        {"front_candidates": fronts}))
    res = S.decide(cand, {"qwen": answer("bed_double"), "glm": answer("bed_double")}, table, "bedroom")
    item = _bed_item(fronts)
    assert core._apply_decision(item, res, table) == []           # the result's own warning names the assumed front
    assert (item.type, item.status) == ("bed_double", "verified")
    assert item.front_deg == 270.0 and item.rotation_deg == 0.0 and item.size == (1.7795, 2.0295)
    assert item.details["front_assumed"] is True and item.details["front_rule"] == pillows
    assert any("front assumed" in w and pillows in w for w in res["warnings"])


def test_core_orients_a_typed_piece_without_a_front_by_its_type(table):
    from wenart.ingest.generic import core
    cand = candidate(size=(2.0295, 1.7795), rotation=90.0)                 # no drawn front
    res = S.decide(cand, {"qwen": answer("bed_double", "bottom"), "glm": answer("bed_double", "top")}, table,
                   "bedroom")
    assert res["front"] is None and res["type"] == "bed_double"
    item = _bed_item()
    warned = core._apply_decision(item, res, table)
    assert item.front_deg is None and item.size == (1.7795, 2.0295) and item.rotation_deg == 0.0
    assert "front_assumed" not in item.details and "bed_double" in item.details["front_note"]
    # Never silent: the orientation by the type's convention is a warning (the builder's facing is assumed).
    assert len(warned) == 1 and warned[0].startswith("sym_L0_001: bed_double without an agreed front")
    assert "turned 90 deg" in warned[0]
    # A type without a front (a table, a lamp, a plant): the convention only, nothing assumed to warn about.
    res = S.decide(candidate(size=(0.7353, 1.2383)), {"qwen": answer("table_dining"), "glm": answer("table_dining")},
                   table, "dining")
    table_item = _bed_item()
    table_item.size, table_item.rotation_deg = (0.7353, 1.2383), 0.0
    assert core._apply_decision(table_item, res, table) == []
    assert table_item.size == (1.2383, 0.7353) and table_item.rotation_deg == 90.0
    assert "has no front" in table_item.details["front_note"]
    # An unknown type keeps the no-front convention.
    res = S.decide(cand, {"qwen": answer("bed_double"), "glm": answer("sofa")}, table, "bedroom")
    item = _bed_item()
    core._apply_decision(item, res, table)
    assert item.size == (2.0295, 1.7795) and item.rotation_deg == 90.0 and "front_note" not in item.details


@pytest.fixture(scope="module")
def real01_first():
    pytest.importorskip("pdfplumber")
    from wenart.ingest import cad_pdf
    from wenart.ingest.generic import core
    page = cad_pdf.read_page(ROOT / "projects" / "real01" / "real01.pdf", 1, "real01.pdf")
    return page, core.extract(page, "L0", "real01.pdf")


def test_real01_questions_carry_room_fitting_types_and_neighbours(real01_first):
    _, ex = real01_first
    items = {q["key"]: q for q in ex.report["questions"]}
    assert len(items) == 17
    chair = next(q for q in items.values() if q["question"]["room"] == {"label": "Dining", "type": "dining"}
                 and (q["question"]["neighbours"] or {}).get("around"))
    facts = chair["question"]
    assert facts["kind"] == "vector" and facts["neighbours"]["around"] == 6 and facts["neighbours"]["similar"] == 6
    assert "chair" in facts["choices"] and "armchair" not in facts["choices"]
    beds = [q for q in items.values() if q["question"]["choices"][:1] == ["bed_double"]]
    assert len(beds) == 2 and all(q["question"]["room"]["label"] == "Bed Room" for q in beds)
    stands = [q for q in items.values() if (q["question"]["neighbours"] or {}).get("next_to") == [2.03, 1.78]]
    assert len(stands) == 4 and all(q["question"]["neighbours"]["around"] == 2 for q in stands)
    from wenart.recognition import answers as A
    from wenart.recognition import crops as C
    for q in items.values():
        args = A.call_args(q, ".")
        digest = C.question_digest("symbol_type", q["question"])
        assert args["prompt"] == digest["prompt"] and args["schema"] == digest["schema"]
        assert args["schema"]["properties"]["type"]["enum"] == q["question"]["choices"]


def test_real01_beds_answered_front_none_keep_the_drawn_front(real01_first):
    """Review ingest-6: agreeing answers with front 'none' (as tests/test_real01.py::_answer) must not build the bed
    rotated 90 deg: the drawn front (pillows, wall) is kept, assumed; size [width, depth] = [1.78, 2.03]."""
    from wenart.ingest.generic import core
    page, ex0 = real01_first
    beds = [c["key"] for c in ex0.candidates if c["request"]["question"]["choices"][:1] == ["bed_double"]]
    answers = {c["key"]: {"qwen": answer("bed_double" if c["key"] in beds else "unknown"),
                          "glm": answer("bed_double" if c["key"] in beds else "unknown")} for c in ex0.candidates}
    ex = core.extract(page, "L0", "real01.pdf", answers=answers)
    typed = [f for f in ex.furniture if f.type == "bed_double"]
    assert len(typed) == 2
    for f in typed:
        assert f.status == "verified" and f.details.get("front_assumed") is True
        assert f.front_deg in (90.0, 270.0)
        assert f.rotation_deg == round((f.front_deg + 90.0) % 360.0, 3)
        assert [round(v, 2) for v in f.size] == [1.78, 2.03]
        assert "small closed shapes" in f.details["front_rule"]          # the pillows found it: its evidence
    assumed = [w for w in ex.warnings if "front assumed" in w]
    assert len(assumed) == 2 and all("small closed shapes" in w for w in assumed)
