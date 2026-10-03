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


def test_size_veto_when_both_say_a_type_the_footprint_cannot_be(table):
    res = S.decide(candidate(size=(0.5, 0.5)), {"qwen": answer("bed_double"), "glm": answer("bed_double")}, table,
                   "bedroom")
    assert res["type"] == "unknown" and res["status"] == "unverified" and res["type_method"] == "none"
    assert res["conflict"]["kind"] == "symbol_type_disagreement" and "size range" in res["conflict"]["description"]
    assert any("size veto" in w for w in res["warnings"])
    assert [c["type"] for c in res["type_candidates"]] == ["bed_double", "bed_double"]


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
    # A unique deterministic front is kept when one pass names it and none names another side.
    det = candidate(size=sofa, front_deg=270.0)
    assert S.decide(det, both("bottom", "none"), table, "living")["front"] == 270.0
    assert S.decide(det, both("bottom", "bottom"), table, "living")["front"] == 270.0
    res = S.decide(det, both("bottom", "top"), table, "living")
    assert res["front"] is None and any("disagrees with the drawn front" in w for w in res["warnings"])
    assert S.decide(det, both("none", "none"), table, "living")["front"] is None
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
