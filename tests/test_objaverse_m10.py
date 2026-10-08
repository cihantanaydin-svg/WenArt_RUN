"""CPU tests of the Milestone 10 library configs and steps for the 14 new furniture and 12 new decor types
(docs/milestone10.md §4.5, §4.6, §7 pods L1 and L2).

Covered: every new type has a source (an ABO rule, an Objaverse category or a TRELLIS.2 prompt), judge words, a size
range and a height range that hold real products; the survey's new category entries (``lvis`` alias, ``require_words``,
decor kind); the judge questions (the Milestone 9 ones byte-identical, so stored answers stay valid; the new ones name
their type and front); how ``decide`` treats the new front rules; the shared judging spec; ``furniture_types``.
"""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_objaverse import Mirror, answer, obj, quiet
from wenart.assets import abo as A
from wenart.assets import generate as G
from wenart.assets import objaverse as OV

ROOT = Path(__file__).resolve().parents[1]
CFG = OV.load_config()
ACFG = A.load_config()
GCFG = G.load_config()
NEW_FURNITURE = ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
                 "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
NEW_DECOR = ("curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture", "plant_large",
             "pendant_light", "ceiling_light")
NEW = NEW_FURNITURE + NEW_DECOR
FRONT_RULES = {"back_taller", "detail_side", "open_side", "none", "documented"}


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def test_every_new_type_has_a_source_judge_words_sizes_and_a_prompt():
    abo_types = {r["types"][0] for r in ACFG["rules"]}
    objaverse_types = {t for spec in CFG["categories"].values() for t in spec["types"]}
    table, tol = OV.library_size_table(CFG)
    heights = OV.heights_of(CFG)
    for t in NEW:
        assert t in abo_types or t in objaverse_types, f"{t}: no ABO rule and no Objaverse category"
        assert t in G.target_types(GCFG) and GCFG["type_words"][t].strip(), f"{t}: no TRELLIS.2 prompt words"
        assert t in table and t in heights and t in CFG["types"], t
        assert CFG["types"][t]["front"] in FRONT_RULES, t
    for t in NEW_FURNITURE:
        assert t in OV.TYPE_WORDS and t in OV.furniture_types() and t in CFG["furniture_sizes"], t
        assert t not in OV.DECOR_TYPES and t not in OV.DECOR_WORDS
    for t in NEW_DECOR:
        assert t in OV.DECOR_TYPES and t in OV.DECOR_WORDS and t in CFG["decor_sizes"], t
        assert t not in OV.TYPE_WORDS
    # a type with a front has the words that name it
    for t in NEW_FURNITURE:
        if CFG["types"][t]["front"] != "none":
            assert t in OV.FRONT_WORDS_BY_TYPE, t
    assert CFG["types"]["clock"]["front"] == OV.DOCUMENTED_RULE and "clock" in OV.DECOR_FRONT_WORDS


def test_ranges_are_sane():
    """Footprints and heights are positive, ordered ranges in metres that a real product of the type fits."""
    table, tol = OV.library_size_table(CFG)
    for t in NEW:
        (w0, w1), (d0, d1) = table[t]
        h0, h1 = CFG["types"][t]["height"]
        assert 0 < w0 < w1 <= 4.5 and 0 < d0 < d1 <= 4.5 and 0 < h0 < h1 <= 3.2, t
        assert w1 / w0 < 40 and d1 / d0 < 80 and h1 / h0 < 40, f"{t}: a range this wide holds anything"   # flat decor: thin
    # Real product boxes (m, x y h in the importer's frame; the ABO listings of 8 Oct 2026 and common sizes).
    fits = {
        "sofa_corner": [(2.44, 1.62, 0.99), (3.2, 2.2, 0.9)], "chaise": [(0.68, 1.38, 0.79), (0.89, 1.78, 0.86)],
        "ottoman": [(0.82, 0.61, 0.48), (0.45, 0.45, 0.46)], "bench": [(1.02, 0.49, 0.47), (1.6, 0.4, 0.45)],
        "bar_stool": [(0.48, 0.57, 1.11), (0.43, 0.42, 0.69)], "office_chair": [(0.61, 0.64, 1.03), (0.7, 0.78, 1.15)],
        "console_table": [(0.9, 0.34, 0.73), (1.2, 0.4, 0.8)], "crib": [(0.7, 1.32, 0.95), (0.62, 1.25, 0.9)],
        "bunk_bed": [(1.0, 2.0, 1.7), (1.11, 2.01, 1.21)], "sideboard": [(1.45, 0.38, 0.9), (1.6, 0.45, 0.8)],
        "shoe_cabinet": [(0.75, 0.25, 1.28), (1.17, 0.23, 0.35)], "display_cabinet": [(0.66, 0.42, 1.98)],
        "tall_cabinet": [(0.57, 0.40, 1.85), (1.25, 0.48, 2.16)], "wall_cabinet": [(0.49, 0.18, 0.59), (0.8, 0.3, 0.7)],
        "curtain": [(1.4, 0.15, 2.5), (0.6, 0.1, 2.2)], "blind": [(1.2, 0.08, 1.4), (0.6, 0.05, 1.0)],
        "throw": [(0.5, 0.4, 0.15), (1.5, 1.0, 0.1)], "books": [(0.25, 0.2, 0.15), (0.3, 0.22, 0.06)],
        "candle": [(0.1, 0.1, 0.24), (0.35, 0.18, 0.26)], "basket": [(0.35, 0.35, 0.36), (0.5, 0.4, 0.4)],
        "tray": [(0.44, 0.30, 0.084), (0.54, 0.44, 0.07)], "clock": [(0.29, 0.04, 0.29), (0.84, 0.03, 0.84)],
        "sculpture": [(0.17, 0.22, 0.33), (0.4, 0.3, 0.9)], "plant_large": [(0.6, 0.6, 1.6), (0.5, 0.5, 1.2)],
        "pendant_light": [(0.34, 0.34, 0.85), (0.49, 0.43, 1.76)], "ceiling_light": [(0.35, 0.36, 0.10),
                                                                                    (0.28, 0.28, 0.27)],
    }
    heights = OV.heights_of(CFG)
    assert set(fits) == set(NEW)
    for t, boxes in fits.items():
        for box in boxes:
            assert OV.fits_type(box, t, table, tol, heights), (t, box)
    # ... and the boxes of a neighbouring type do not: a corner sofa is not a sofa, a crib is no single bed
    assert not OV.fits_type((2.44, 1.62, 0.99), "sofa", table, tol, heights)
    assert OV.fits_type((2.44, 1.62, 0.99), "sofa_corner", table, tol, heights)
    assert not OV.fits_type((0.7, 1.32, 0.95), "bed_single", table, tol, heights)
    assert not OV.fits_type((0.45, 0.45, 0.45), "bar_stool", table, tol, heights)       # a low stool is not a bar stool


def test_furniture_types_follow_the_catalogue_then_the_schema():
    from wenart.furniture import catalog as C
    types = OV.furniture_types()
    assert set(C.FURNITURE_TYPES) <= set(types) and set(NEW_FURNITURE) <= set(types)
    assert types[-1] == "unknown" and len(types) == len(set(types))
    assert list(types[:len(C.FURNITURE_TYPES) - 1]) == list(C.FURNITURE_TYPES[:-1])     # the catalogue's order first


def test_new_decor_types_are_the_schema_decor_types_but_the_parametric_book_set():
    from wenart import building as B
    schema = set(B.load_schema()["$defs"]["decor"]["properties"]["type"]["enum"])
    library = set(OV.DECOR_TYPES)
    assert library == schema - {"book_set"}                        # book_set stays parametric; `books` is the library type


# --------------------------------------------------------------------------
# The judge questions
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind, ftype, dims, front, normalised, digest", [
    ("furniture", "sofa", [2.0, 0.9, 0.85], True, False, "00ef17c8311d1d32"),
    ("furniture", "bed_double", [1.8, 2.0, 1.0], True, False, "651002b6e987e3c9"),
    ("furniture", "table_coffee", [1.1, 0.6, 0.45], False, False, "1b441a6fc8dc25bf"),
    ("furniture", "toilet", [0.4, 0.7, 0.8], True, True, "d47e6f3c448cbc2e"),
    ("furniture", "tv_unit", [1.5, 0.4, 0.5], True, False, "3d2ff547818bd481"),
    ("decor", "rug", [2.0, 1.4, 0.02], False, False, "18e46d883a84cc2b"),
    ("decor", "wall_art", [0.6, 0.03, 0.8], True, False, "a42bb4210ccb6473"),
    ("decor", "mirror", [0.6, 0.04, 0.9], True, False, "ae4ce022c9ddc03b"),
])
def test_the_milestone_9_questions_are_unchanged(kind, ftype, dims, front, normalised, digest):
    """The stored judge answers of M8 and M9 hash the question text (input_sha256): a changed word would make the
    pod ask them all again. The digests are the sha256 prefixes of the questions at commit 55174db."""
    make = OV.judge_prompt if kind == "furniture" else OV.decor_prompt
    assert hashlib.sha256(make(ftype, dims, front, normalised).encode()).hexdigest()[:16] == digest


@pytest.mark.parametrize("ftype", NEW_FURNITURE)
def test_furniture_question_names_the_type_and_its_front(ftype):
    name, what = OV.TYPE_WORDS[ftype]
    has_front = OV.has_front_of(ftype, CFG)
    text = OV.judge_prompt(ftype, [1.0, 0.5, 0.8], has_front)
    assert f"It is offered as a {name} ({what})" in text and f"matches_type: true when the piece is a {name}" in text
    if has_front:
        assert OV.FRONT_WORDS_BY_TYPE[ftype] in text
        assert OV.FRONT_WORDS not in text                          # the older types' sentence is not the new types'
    else:
        assert "null (this type has no front)" in text
    assert "has_mattress: null (this is not a bed)" in text


@pytest.mark.parametrize("dtype", NEW_DECOR)
def test_decor_question_names_the_type_what_it_is_and_what_it_is_not(dtype):
    name, what, counts = OV.DECOR_WORDS[dtype]
    has_front = OV.has_front_of(dtype, CFG)
    text = OV.decor_prompt(dtype, [0.5, 0.1, 0.5], has_front)
    assert f"{name} decor ({what})" in text and f"is_decor_type: true when it is {counts}" in text
    assert "(not " in counts or "is not one" in counts, f"{dtype}: the question says what it is not"
    assert ("the clock face" in text) == (dtype == "clock")


def test_new_types_ask_the_right_schema_and_come_out_in_the_requests(tmp_path):
    """judge-requests asks furniture and decor with their own schema for the new types too."""
    out = tmp_path / "lib"
    for t, kind in (("ottoman", "furniture"), ("clock", "decor"), ("plant_large", "decor"), ("crib", "furniture")):
        dims = {"ottoman": [0.6, 0.6, 0.45], "clock": [0.4, 0.04, 0.4], "plant_large": [0.6, 0.6, 1.6],
                "crib": [0.7, 1.3, 0.95]}[t]
        sheet = out / "judge" / "sheets" / f"{t}.jpg"
        sheet.parent.mkdir(parents=True, exist_ok=True)
        from PIL import Image
        Image.new("RGB", (8, 8), (90, 90, 90)).save(sheet)
        rec = {"uid": t, "type": t, "kind": kind, "decor_type": t if kind == "decor" else None, "title": t,
               "source": "abo", "unit": {"dims_m": dims, "normalised": False}}
        item = OV.request_item(rec, out, CFG)
        assert item["context"]["kind"] == kind and item["images"] == [f"sheets/{t}.jpg"]
        assert (OV.item_kind(item) == "decor") == (kind == "decor")


# --------------------------------------------------------------------------
# Acceptance of the new front rules
# --------------------------------------------------------------------------

def abo_obj(ftype, front="-Y", kind="furniture"):
    return {"uid": "abo_X", "type": ftype, "kind": kind, "decor_type": ftype if kind == "decor" else None,
            "source": "abo", "unit": {"ok": True, "scale": 1.0}, "front_documented": front,
            "geometric_note": "documented", "geometric_front": None}


def decor_answer(front=0, quality=5, **kw):
    return dict({"is_single_object": True, "is_decor_type": True, "photoreal_quality": quality,
                 "styles": ["modern", "neutral"], "front_view": front}, **kw)


def test_a_crib_or_bunk_bed_front_is_documented_by_abo_or_agreed_by_the_judges():
    # ABO documents the front: the documented front stays unless both judges name another view
    dec = OV.decide(abo_obj("crib"), {"qwen": answer(front=0), "glm": answer(front=0)}, CFG)
    assert dec["accepted"] and dec["front_axis"] == "-Y" and dec["front_axis_confidence"] == "high"
    dec = OV.decide(abo_obj("crib"), {"qwen": answer(front=1), "glm": answer(front=1)}, CFG)
    assert not dec["accepted"] and dec["code"] == "front_not_agreed"
    # Objaverse: the geometry cannot tell the open side of a crib and no source documents it: both judges naming the
    # same view decide (front_by_judges), with the confidence medium; judges that differ or abstain refuse it
    o = obj("crib", geo=None)
    o.update(source="objaverse", geometric_note="documented: only the source's front decides")
    dec = OV.decide(o, {"qwen": answer(front=3), "glm": answer(front=3)}, CFG)
    assert dec["accepted"] and dec["front_axis"] == "-X" and dec["front_axis_confidence"] == "medium"
    assert "judges' agreement decides" in dec["front_axis_note"]
    for a, b in ((0, 2), (1, None), (None, None)):
        dec = OV.decide(o, {"qwen": answer(front=a), "glm": answer(front=b)}, CFG)
        assert not dec["accepted"] and dec["code"] == "front_not_agreed", (a, b)
    # wall art and mirrors keep the M8 / M9 rule: only a documented front decides
    art = obj("wall_art", geo=None)
    art.update(source="objaverse", kind="decor", decor_type="wall_art")
    dec = OV.decide(art, {"qwen": decor_answer(front=0), "glm": decor_answer(front=0)}, CFG)
    assert not dec["accepted"] and dec["code"] == "front_not_agreed"
    # a generated model: both judges agreeing decide, as before
    g = obj("bunk_bed", geo=None)
    g.update(source="generated")
    dec = OV.decide(g, {"qwen": answer(front=2), "glm": answer(front=2)}, CFG)
    assert dec["accepted"] and dec["front_axis"] == OV.VIEW_SIDES[2] and dec["front_axis_confidence"] == "high"
    assert {t for t, spec in CFG["types"].items() if spec.get("front_by_judges")} == {"crib", "bunk_bed", "clock"}


def test_decor_without_a_front_and_a_wall_clock_with_one():
    plain = {"uid": "u", "type": "candle", "kind": "decor", "decor_type": "candle", "source": "objaverse",
             "unit": {"ok": True, "scale": 1.0}}
    dec = OV.decide(plain, {"qwen": decor_answer(front=None), "glm": decor_answer(front=None)}, CFG)
    assert dec["accepted"] and dec["front_axis"] == "-Y" and dec["front_axis_confidence"] == "low"
    assert dec["decor_type"] == "candle" and dec["kind"] == "decor"
    clock = abo_obj("clock", kind="decor")
    ok = OV.decide(clock, {"qwen": decor_answer(front=0), "glm": decor_answer(front=3)}, CFG)
    assert ok["accepted"] and ok["front_axis"] == "-Y" and "did not agree" in ok["front_axis_note"]   # source decides
    not_a_clock = OV.decide(clock, {"qwen": decor_answer(is_decor_type=False), "glm": decor_answer()}, CFG)
    assert not not_a_clock["accepted"] and not_a_clock["code"] == "not_decor_type"


def test_per_type_limits_hold_for_the_new_types(tmp_path):
    """accept: 20 per furniture type, 20 per decor type, the style spread first (docs/milestone9.md §1) - here a
    new furniture type and a new decor type with 25 judged models each."""
    out = tmp_path / "lib"
    objects, cands = {}, []
    for t, kind in (("ottoman", "furniture"), ("tray", "decor")):
        for n in range(25):
            uid = f"abo_{t}{n:02d}"
            objects[uid] = {"uid": uid, "type": t, "kind": kind, "decor_type": t if kind == "decor" else None,
                            "source": "abo", "status": "ready", "unit": {"ok": True, "scale": 1.0},
                            "front_documented": "-Y" if t == "ottoman" else None, "geometric_note": "x",
                            "geometric_front": None}
            cands.append({"uid": uid, "group": t, "types": [t], "source": "abo", "kind": kind,
                          "decor_type": t if kind == "decor" else None, "rank": n + 1})
    OV.write_json(out / OV.THUMBS_JSON, {"objects": objects})
    OV.write_json(out / "survey_abo.json", {"candidates": cands})
    answers = {u: {"qwen": answer(front=None, styles=("modern", "neutral")) if o["kind"] == "furniture"
                   else decor_answer(front=None),
                   "glm": answer(front=None, styles=("modern", "neutral")) if o["kind"] == "furniture"
                   else decor_answer(front=None)} for u, o in objects.items()}
    import wenart.assets.objaverse as ov
    orig = ov.load_judgements
    ov.load_judgements = lambda *_a, **_k: answers
    try:
        doc = ov.accept(out, CFG)
    finally:
        ov.load_judgements = orig
    kept = {}
    for d in doc["accepted"]:
        kept[d["type"]] = kept.get(d["type"], 0) + 1
    assert kept == {"ottoman": 20, "tray": 20}
    assert doc["counts"]["over_type_limit"] == 10


# --------------------------------------------------------------------------
# The survey: lvis alias, require_words, decor kind
# --------------------------------------------------------------------------

def test_categories_with_words_pick_by_title_or_tags_and_win_over_the_plain_entry(tmp_path):
    m = Mirror(tmp_path / "mirror")
    plain = m.add("sofa", name="Oak Sofa")
    corner = m.add("sofa", name="Big Sectional Couch")
    tagged = m.add("sofa", name="Cloud", tags=("L-shaped",))
    sideboard = m.add("cabinet", name="Oak Sideboard")
    shoe = m.add("cabinet", name="Hall cabinet", tags=("shoes",))
    nothing = m.add("cabinet", name="Storage thing")                 # no word of any entry: no type, not refused
    both = m.add("cabinet", name="Tall wall cabinet")                # two entries of different types
    console = m.add("table", name="Hall table")
    other_table = m.add("table", name="Plain thing")
    office = m.add("chair", name="Gaming chair")
    dining = m.add("chair", name="Dining chair")
    pendant = m.add("lamp", name="Glass pendant")
    ceiling = m.add("lamp", name="Flush ceiling light")
    floor = m.add("lamp", name="Arc lamp", tags=("floor",))
    clock = m.add("clock", name="Wall clock", faces=800, textured=False)    # decor: low faces and flat colours taken
    blind = m.add("curtain", name="Roller blind")
    curtain = m.add("curtain", name="Velvet drape")
    palm = m.add("flowerpot", name="Areca palm in pot")
    pot = m.add("flowerpot", name="Clay pot")
    doc = OV.survey(m.write(), tmp_path / "lib", CFG, download=False, log=quiet)
    group = {c["uid"]: c["group"] for c in doc["candidates"]}
    assert group[plain] == "sofa" and group[corner] == "sofa_corner" and group[tagged] == "sofa_corner"
    assert group[sideboard] == "sideboard" and group[shoe] == "shoe_cabinet" and group[console] == "console_table"
    assert group[office] == "office_chair" and group[dining] == "chair"
    assert group[pendant] == "pendant_light" and group[ceiling] == "ceiling_light" and group[floor] == "floor_lamp"
    assert group[clock] == "clock" and group[blind] == "blind" and group[curtain] == "curtain"
    assert group[palm] == "plant_large" and group[pot] == "potted_plant"
    absent = {nothing, other_table}
    assert not absent & set(group) and both not in group
    refused = {r["uid"]: r for r in doc["refused"]}
    assert refused[both]["code"] == "several_types" and set(refused[both]["categories"]) == {"cabinet_tall", "cabinet_wall"}
    assert doc["lvis"]["word_filtered"] == len(absent)
    kinds = {c["uid"]: (c["kind"], c["decor_type"]) for c in doc["candidates"]}
    assert kinds[clock] == ("decor", "clock") and kinds[blind] == ("decor", "blind")
    assert kinds[sideboard] == ("furniture", None) and kinds[palm] == ("decor", "plant_large")
    assert doc["counts"]["sofa_corner"]["lvis"] == 2 and doc["counts"]["sofa"]["lvis"] == 1
    assert doc["lvis"]["found"]["sofa_corner"] == 3 and doc["lvis"]["found"]["sofa"] == 3     # both entries read `sofa`
    assert OV.normalise_record(next(c for c in doc["candidates"] if c["uid"] == clock), "objaverse")["kind"] == "decor"


def test_a_missing_lvis_name_is_listed_by_the_name_the_entry_reads(tmp_path):
    cfg = copy.deepcopy(CFG)
    cfg["categories"] = {"sofa": {"types": ["sofa"]}, "sofa_corner": {"lvis": "no_such_name", "types": ["sofa_corner"],
                                                                      "require_words": ["sectional"]}}
    m = Mirror(tmp_path / "mirror")
    m.add("sofa")
    lines = []
    doc = OV.survey(m.write(), tmp_path / "lib", cfg, download=False, log=lines.append)
    assert doc["lvis"]["missing"] == ["sofa_corner"] and doc["lvis"]["found"] == {"sofa": 1}
    assert any("'no_such_name'" in line for line in lines)


def test_two_entries_with_words_of_one_type_are_not_a_conflict(tmp_path):
    """`cabinet` and `cupboard` both hold shoe cabinets: an object in both is one type (several_types only when the
    type sets differ)."""
    m = Mirror(tmp_path / "mirror")
    both_lvis = m.add(["cabinet", "cupboard"], name="Shoe cabinet")
    doc = OV.survey(m.write(), tmp_path / "lib", CFG, download=False, log=quiet)
    chosen = [c for c in doc["candidates"] if c["uid"] == both_lvis]
    assert [c["group"] for c in chosen] == ["shoe_cabinet"] and set(chosen[0]["categories"]) == {"cabinet_shoe",
                                                                                                 "cupboard_shoe"}


def test_decor_categories_take_low_poly_flat_coloured_models_with_40_candidates(tmp_path):
    m = Mirror(tmp_path / "mirror")
    low = m.add("candle", faces=600, textured=False)
    tiny = m.add("candle", faces=300, textured=False)
    sofa_low = m.add("sofa", faces=600)
    doc = OV.survey(m.write(), tmp_path / "lib", CFG, download=True, log=quiet)
    chosen = {c["uid"] for c in doc["candidates"]}
    assert low in chosen and tiny not in chosen and sofa_low not in chosen
    codes = {r["uid"]: r["code"] for r in doc["refused"]}
    assert codes[tiny] == "face_count" and codes[sofa_low] == "face_count"
    cand = next(c for c in doc["candidates"] if c["uid"] == low)
    assert cand["glb_info"]["flat_colours"] is True and cand["kind"] == "decor" and cand["decor_type"] == "candle"


# --------------------------------------------------------------------------
# The shared judging spec
# --------------------------------------------------------------------------

def test_the_library_judging_spec_is_the_default_and_a_spec_of_another_task_does_not_mix(tmp_path):
    assert OV.LIBRARY_SPEC.dir_name == "judge" and OV.LIBRARY_SPEC.task == OV.TASK == "library_judge"
    assert OV.LIBRARY_SPEC.system == OV.SYSTEM_PROMPT and OV.LIBRARY_SPEC.requests_kind == "objaverse_judge_requests"
    item = {"context": {"kind": "decor"}}
    assert OV.LIBRARY_SPEC.schema_of(item) == OV.judge_schema("decor")
    assert OV.LIBRARY_SPEC.valid_of(item, decor_answer()) and not OV.LIBRARY_SPEC.valid_of(item, answer())
    other = OV.JudgeSpec(dir_name="recolour", requests_kind="recolour_requests")
    OV.write_json(tmp_path / "recolour" / "requests.json", {"kind": "recolour_requests", "items": []})
    assert OV.read_requests(tmp_path, other)["kind"] == "recolour_requests"
    with pytest.raises(ValueError, match="not a objaverse_judge_requests"):
        OV.write_json(tmp_path / "judge" / "requests.json", {"kind": "recolour_requests", "items": []})
        OV.read_requests(tmp_path)
    assert OV.read_requests(tmp_path / "nowhere") is None


# --------------------------------------------------------------------------
# End to end: survey, thumbnails, judging, accept, catalogue for new types (Objaverse, fake Blender and judges)
# --------------------------------------------------------------------------

def test_new_types_go_from_the_survey_to_the_catalogue(tmp_path, monkeypatch):
    """An ottoman (no front), a crib and a wall clock (a front the judges agree on: confidence medium), a large plant and a
    candle (decor). The catalogue module still lacks the
    new types (track F adds them), so the test gives it the schema's types for the run; write-catalog then sorts,
    validates and merges them."""
    from test_objaverse import box, fake_runner
    from wenart.furniture import catalog as C
    m = Mirror(tmp_path / "mirror")
    uids = {"ottoman": m.add("ottoman", likes=5, name="Velvet Pouf"),
            "crib": m.add("crib", likes=4, name="White Crib", textured=False),
            "clock": m.add("wall_clock", likes=3, name="Round wall clock", textured=False, faces=900),
            "plant": m.add("flowerpot", likes=2, name="Areca palm in a pot"),
            "candle": m.add("candle", likes=1, name="Pillar candle", textured=False, faces=700)}
    out = tmp_path / "lib"
    OV.survey(m.write(), out, CFG, log=quiet)
    shapes = {uids["ottoman"]: (box(-0.4, -0.3, 0, 0.4, 0.3, 0.45), []),
              uids["crib"]: (box(-0.35, -0.65, 0, 0.35, 0.65, 0.95), []),
              uids["clock"]: (box(-0.2, -0.015, 0, 0.2, 0.015, 0.4), []),
              uids["plant"]: (box(-0.3, -0.3, 0, 0.3, 0.3, 1.5), []),
              uids["candle"]: (box(-0.05, -0.05, 0, 0.05, 0.05, 0.2), [])}
    doc, rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=fake_runner(shapes, []), log=quiet)
    assert rc == 0 and all(o["status"] == "ready" for o in doc["objects"].values()), doc["objects"]
    objs = doc["objects"]
    assert (objs[uids["ottoman"]]["type"], objs[uids["ottoman"]]["kind"]) == ("ottoman", "furniture")
    assert (objs[uids["clock"]]["type"], objs[uids["clock"]]["kind"]) == ("clock", "decor")
    assert objs[uids["plant"]]["decor_type"] == "plant_large" and objs[uids["crib"]]["type"] == "crib"
    assert all(o["unit"]["scale"] == 1.0 for o in objs.values())                    # metres fit: no unit factor guessed
    lib = SimpleNamespace(out=out, doc=doc)
    answers = {uids["ottoman"]: answer(front=None), uids["crib"]: answer(front=0),
               uids["clock"]: decor_answer(front=0), uids["plant"]: decor_answer(front=None),
               uids["candle"]: decor_answer(front=None)}
    from test_objaverse import run_judges
    clients = {k: (lambda images, _p: answers[Path(images[0]).stem]) for k in OV.MODEL_KEYS}
    assert run_judges(lib, clients=clients)["qwen"] == 0
    acc = OV.accept(out, CFG)
    assert {d["uid"] for d in acc["accepted"]} == set(uids.values()) and not acc["refused"]
    by_uid = {d["uid"]: d for d in acc["accepted"]}
    assert by_uid[uids["crib"]]["front_axis_confidence"] == by_uid[uids["clock"]]["front_axis_confidence"] == "medium"
    assert by_uid[uids["ottoman"]]["front_axis_confidence"] == "low"
    monkeypatch.setattr(C, "FURNITURE_TYPES", OV.furniture_types())
    monkeypatch.setattr(C, "DECOR_TYPES", OV.DECOR_TYPES)
    base = json.loads(C.CATALOG_PATH.read_text(encoding="utf-8"))
    have = {e["type"] for e in base["entries"]}                 # track F's catalog.json has the new types already
    base["entries"] += [{"type": t, "parametric": True, "reason": "test"} for t in NEW_FURNITURE if t not in have]
    base_path = tmp_path / "catalog.json"
    base_path.write_text(json.dumps(base), encoding="utf-8")
    cat = OV.write_catalog(out, tmp_path / "assets", CFG, base_catalog=base_path, log=quiet)
    assert [e["type"] for e in cat["entries"]] == ["ottoman", "crib"]               # catalogue type order
    assert [e["decor_type"] for e in cat["decor"]] == ["candle", "clock", "plant_large"]    # OV.DECOR_TYPES order
    plant = cat["decor"][2]
    assert next(e for e in cat["entries"] if e["type"] == "crib")["front_axis_confidence"] == "medium"
    assert plant["type"] == "decor_plant_large" and plant["kind"] == "decor" and plant["front_axis_confidence"] == "low"
    assert cat["entries"][0]["front_axis_confidence"] == "low" and cat["entries"][0]["bbox_model_m"] == [0.8, 0.6, 0.45]
    assert cat["counts"]["entries"] == 2 and cat["counts"]["decor"] == 3 and cat["counts"]["material_tagged"] == 0
    assert (tmp_path / "assets" / plant["glb"]).is_file()
