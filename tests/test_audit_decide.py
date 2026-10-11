"""Milestone 12 track B: keep / fix / remove (docs/milestone12.md §6.1 D21, ``decide.py``) and the catalogue writer
(§6.2 D22, U3, B2, contract §13.3, ``write.py``)."""
import copy
import json

import pytest

from wenart.assets.audit import checks as CK
from wenart.assets.audit import decide as D
from wenart.assets.audit import items as I
from wenart.assets.audit import load_config
from wenart.assets.audit import write as W
from wenart.furniture import catalog as C

CFG = load_config()
KNOWN = {"sofa", "wardrobe", "tall_cabinet", "bed_double", "bunk_bed", "cushion", "throw"}
YES = {"is_type": True, "type_guess": "sofa", "single_object": True, "real_product": True, "indoor": "indoor",
       "upright": True, "size_plausible": True, "parts_open": False, "styles": ["modern"], "quality": 4,
       "front_shown": "front", "has_bedding": None, "has_pillows": None, "has_cushions": True, "contact": None}


def item(**kw):
    base = {"id": "abo_x", "type": "sofa", "kind": "furniture", "source": "abo", "licence": "CC-BY-4.0",
            "title": "Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa", "bbox_m": [1.97, 0.83, 0.83],
            "units_known": True, "front_axis": "-Y", "front_axis_confidence": "high", "up_axis": "+Z",
            "bbox_min_m": [-0.985, -0.415, 0.0], "bbox_max_m": [0.985, 0.415, 0.83], "origin_offset": [0.0, 0.0, 0.0],
            "polycount": 20000, "quality": [4, 4]}
    base.update(kw)
    return base


def decide(it, a1=None, a2=None):
    return D.decide(it, CK.item_checks(it, CFG, KNOWN), a1, a2, CFG)


def test_a_clean_product_waits_for_the_vision_check_then_is_kept():
    d = decide(item())
    assert d["status"] == "pending" and D.expected_status(d) == "keep?"
    d = decide(item(), YES)
    assert d["status"] == "keep" and d["reasons"] == [] and d["flags"]["real_product"] is True


def test_licence_removes_without_any_vision():
    d = decide(item(licence="CC-BY-NC-4.0", source="objaverse"))
    assert d["status"] == "removed" and "not allowed" in d["reasons"][0]


@pytest.mark.parametrize("change,word", [({"upright": False}, "side"), ({"parts_open": True}, "drawer")])
def test_vision_answers_that_remove(change, word):
    """The specific findings remove; the other vision-only findings keep the model with a doubt (decision 1a)."""
    d = decide(item(), dict(YES, **change))
    assert d["status"] == "removed" and any(word in r for r in d["reasons"]), d["reasons"]


def test_not_a_real_product_needs_quality_four():
    obj = item(id="objaverse_x", source="objaverse", title="Sofa", licence="CC-BY-4.0")
    d = decide(obj, dict(YES, real_product=False, quality=3))
    assert d["status"] == "keep" and d["vision_doubt"]               # decision 1a: a doubt, not a removal
    d = decide(obj, dict(YES, real_product=False, quality=4))
    assert d["status"] == "keep" and not d["vision_doubt"]


def test_the_front_answer_turns_the_front():
    """Only where code is unsure of the front (pod P3: 179 of 188 vision turns overrode agreed fronts)."""
    d = decide(item(front_axis_confidence="low"), dict(YES, front_shown="back"))
    assert d["status"] == "fix" and d["fixes"] == {"front_quarter_turns": 2}
    d = decide(item(), dict(YES, front_shown="right"))             # an agreed (high confidence) front stays
    assert d["status"] == "keep" and not d["fixes"] and any("agreed front is kept" in n for n in d["notes"])


def test_a_retype_needs_title_size_and_vision():
    wardrobe = item(type="tall_cabinet", title="Marchio Amazon - Movian, armadio a 2 ante modello Mira",
                    bbox_m=[0.98, 0.58, 1.93], bbox_min_m=[-0.49, -0.29, 0.0], bbox_max_m=[0.49, 0.29, 1.93])
    assert decide(wardrobe)["status"] == "pending"
    assert D.expected_status(decide(wardrobe)) == "fix?"
    d = decide(wardrobe, dict(YES, is_type=False, type_guess="wardrobe"))
    assert d["status"] == "fix" and d["fixes"]["type"] == "wardrobe"
    d = decide(wardrobe, dict(YES, is_type=True, type_guess="tall_cabinet"))
    assert d["status"] == "removed"                             # title and vision disagree: it does not stay


def test_models_without_title_evidence_need_two_passes():
    gen = item(id="gen_x", source="generated", licence="generated (TRELLIS.2-4B, MIT)",
               title="Generated modern sofa (1)", units_known=False)
    assert D.expected_status(decide(gen)) == "vision?"
    assert decide(gen, YES)["status"] == "pending"              # pass 2 not asked yet
    assert decide(gen, YES, {"type_guess": "sofa"})["status"] == "keep"
    assert decide(gen, YES, {"type_guess": "sofa_corner"})["status"] == "keep"     # a near type agrees
    d = decide(gen, YES, {"type_guess": "bench"})                    # decision 1a: the passes disagree: a doubt
    assert d["status"] == "keep" and "disagree" in d["vision_doubt"][0]
    d = decide(gen, dict(YES, is_type=False, type_guess="bench"))     # pass 1 no: no pass 2, a doubt
    assert d["status"] == "keep" and "not a sofa" in d["vision_doubt"][0]
    assert decide(gen, dict(YES, is_type=False))["status"] == "pending"   # "not a sofa", guess sofa: pass 2 decides
    assert decide(gen, YES, {"type_guess": "sofa"})["flags"]["real_product"] is False


def test_crude_real_products_are_expected_to_stay_crude_uploads_to_go():
    abo = item(polycount=1500)
    assert D.expected_status(decide(abo)) == "keep?"
    # pod P3: a textured real product with few faces stays with quality 3 (D21: quality <= 2 removes)
    assert decide(abo, dict(YES, quality=3))["status"] == "keep"
    assert decide(abo, dict(YES, quality=2))["status"] == "removed"
    obj = item(id="objaverse_y", source="objaverse", title="Old sofa", polycount=1500)
    assert D.expected_status(decide(obj)) == "removed?"
    assert decide(obj, dict(YES, quality=3))["status"] == "removed"
    assert decide(obj, dict(YES, quality=4))["status"] == "keep"


def deco(dtype, title):
    return item(id=f"abo_{dtype}", type=dtype, kind="decor", title=title, bbox_m=[0.3, 0.3, 0.3],
                bbox_min_m=[-0.15, -0.15, 0.0], bbox_max_m=[0.15, 0.15, 0.3], polycount=20000)


def test_lights_hanging_from_their_top_are_not_upside_down():
    """Pod P3: the sheets show a pendant light standing on the floor; the vision check called 23 lights upside down."""
    for dtype in ("pendant_light", "ceiling_light"):
        d = decide(deco(dtype, "Pendant Light"), dict(YES, type_guess=dtype, upright=False))
        assert not any("upside down" in r for r in d["reasons"]), d["reasons"]
    d = decide(deco("clock", "Wall Clock"), dict(YES, type_guess="clock", upright=False))
    assert d["status"] == "removed"                              # a wall clock lying on its back stays a reason


def test_decor_that_is_a_group_by_nature_may_be_several_objects():
    for dtype, title in (("books", "Stack of Books"), ("candle", "Candle Set"), ("tray", "Serving Tray"),
                         ("bowl", "Fruit Bowl"), ("basket", "Storage Basket")):
        d = decide(deco(dtype, title), dict(YES, type_guess=dtype, single_object=False))
        assert not any("more than one" in r for r in d["reasons"] + d["vision_doubt"]), (dtype, d)
    d = decide(deco("vase", "Vase"), dict(YES, type_guess="vase", single_object=False))
    assert any("more than one" in r for r in d["vision_doubt"])


def test_a_contradictory_answer_whose_guess_is_the_type_counts_as_the_type():
    """Pod P3: 25 models were removed as "not a clock" by answers whose type guess was "clock"."""
    d = decide(item(), dict(YES, is_type=False, type_guess="sofa"))
    assert d["status"] == "keep" and any("taken as a sofa" in n for n in d["notes"]), d
    d = decide(item(), dict(YES, is_type=False, type_guess="bench"))
    assert d["status"] == "keep" and "not a sofa (a bench)" in d["vision_doubt"][0]     # decision 1a


def test_decor_flags():
    cushion = item(id="abo_c", type="cushion", kind="decor", title="Velvet Throw Pillow", bbox_m=[0.45, 0.15, 0.45],
                   bbox_min_m=[-0.225, -0.075, 0.0], bbox_max_m=[0.225, 0.075, 0.45])
    ans = dict(YES, type_guess="cushion", front_shown="none", has_cushions=None, contact="leans")
    d = decide(cushion, ans)
    assert d["status"] == "keep" and d["flags"]["contact"] == "leans"
    assert D.default_flags(dict(cushion, type="throw"))["contact"] == "drapes"


# --------------------------------------------------------------------------
# write.py on the committed catalogue
# --------------------------------------------------------------------------

NC_SA = {"CC-BY-NC-4.0": 7, "CC-BY-NC-SA-4.0": 5, "CC-BY-SA-4.0": 6}


def library():
    return json.loads(I.LIBRARY_PATH.read_text(encoding="utf-8"))


def entries(doc):
    return [e for s in ("entries", "decor") for e in doc.get(s) or []]


def test_u3_the_18_nc_sa_models_are_removed_in_the_committed_catalogue():
    doc = library()
    # since pod P3 every entry carries its full audit: the licence removals are the removed entries whose reasons
    # name their licence
    licence = [e for e in entries(doc) if (e.get("audit") or {}).get("status") == "removed"
               and f"licence {e['licence']} not allowed (user decision of 10 Oct 2026)" in e["audit"]["reasons"]]
    by = {}
    for e in licence:
        by[e["licence"]] = by.get(e["licence"], 0) + 1
        assert e["audit"]["version"] == "m12" and e["audit"]["checked_utc"]
        assert not C.usable(e)
    assert by == NC_SA
    for e in entries(doc):
        assert C.usable(e) == ((e.get("audit") or {}).get("status") in ("keep", "fix")), e["id"]
    assert W.U3_NOTE in doc["notes"]


def test_b2_generated_entries_name_the_generated_source():
    from wenart.assets.objaverse import GENERATED_VIA
    gen = [e for e in entries(library()) if e["source"] == "generated"]
    # the TRELLIS.2 models; pod P4's Infinigen models (``generated.generator``) keep their own credit line
    trellis = [e for e in gen if (e.get("generated") or {}).get("generator", "trellis") == "trellis"]
    assert len(trellis) == 281 and all(e["via"] == GENERATED_VIA for e in trellis)
    assert not any("Objaverse" in e["via"] for e in gen)
    assert all("Infinigen" in e["via"] for e in gen if e not in trellis)


def test_licence_removals_are_idempotent():
    doc = library()
    assert W.licence_removals(doc, "2026-10-11T00:00:00Z") == []
    fresh = copy.deepcopy(doc)
    for e in entries(fresh):
        e.pop("audit", None)
    ids = W.licence_removals(fresh, "2026-10-11T00:00:00Z")
    assert len(ids) == 18
    assert W.licence_removals(fresh, "2026-10-12T00:00:00Z") == []


def test_apply_decisions_once_and_the_catalogue_stays_valid():
    doc = library()
    e = next(x for x in doc["entries"] if x["id"] == "abo_B0718WYQ8D")       # a single bed, front -Y
    box, unit = list(e["bbox_m"]), e["unit_scale"]
    dec = {"status": "fix", "reasons": [], "fixes": {"rescale": 1.1, "front_quarter_turns": 1},
           "flags": {"real_product": True, "has_bedding": False}, "notes": ["test"]}
    stats = W.apply_decisions(doc, {e["id"]: dec}, "2026-10-11T00:00:00Z")
    assert stats["written"] == 1
    assert e["front_axis"] == "+X" and e["unit_scale"] == pytest.approx(unit * 1.1)
    assert e["bbox_m"] == [round(box[1] * 1.1, 4), round(box[0] * 1.1, 4), round(box[2] * 1.1, 4)]
    assert e["audit"]["status"] == "fix" and e["audit"]["fixes"]["front_axis"] == "+X"
    assert e["audit"]["before"]["front_axis"] == "-Y" and e["has_bedding"] is False
    C.validate(doc, complete=False)
    again = W.apply_decisions(doc, {e["id"]: dec}, "2026-10-12T00:00:00Z")
    assert again["unchanged"] == 1 and e["unit_scale"] == pytest.approx(unit * 1.1)     # never rescaled twice


def test_apply_a_retype_and_skip_pending():
    doc = library()
    e = next(x for x in doc["entries"] if x["type"] == "tall_cabinet")
    W.apply_decisions(doc, {e["id"]: {"status": "fix", "reasons": [], "fixes": {"type": "wardrobe"}, "flags": {}}},
                      "2026-10-11T00:00:00Z")
    assert e["type"] == "wardrobe" and e["audit"]["before"]["type"] == "tall_cabinet"
    C.validate(doc, complete=False)
    stats = W.apply_decisions(doc, {e["id"]: {"status": "pending", "reasons": [], "fixes": {}, "flags": {}}}, "t")
    assert stats["skipped_pending"] == 1


def test_vision_only_findings_keep_the_model_with_a_doubt():
    """User decision 1a of 11 Oct 2026 (docs/milestone12.md §14.3): a finding of the vision check alone keeps the
    model with ``vision_doubt``; code evidence and the specific findings (on its side, an open part) still remove."""
    for change, word in (({"single_object": False}, "more than one"), ({"quality": 2}, "quality 2"),
                         ({"is_type": False, "type_guess": "bench"}, "not a sofa"), ({"indoor": "outdoor"}, "outdoor")):
        d = decide(item(), dict(YES, **change))
        assert d["status"] == "keep" and any(word in x for x in d["vision_doubt"]), (change, d)
    for change in ({"upright": False}, {"parts_open": True}):
        d = decide(item(), dict(YES, **change))
        assert d["status"] == "removed" and d["vision_doubt"] == []
    # with code evidence the doubts join the removal reasons
    d = decide(item(licence="CC-BY-NC-4.0", source="objaverse"), dict(YES, quality=2))
    assert d["status"] == "removed" and any("quality 2" in r for r in d["reasons"]) and d["vision_doubt"] == []


def test_the_writer_records_the_doubt_in_the_audit():
    doc = {"entries": [{"id": "abo_x", "type": "sofa", "front_axis": "-Y", "bbox_m": [2, 0.9, 0.8]}]}
    d = decide(item(), dict(YES, single_object=False))
    W.apply_decisions(doc, {"abo_x": d}, "2026-10-11T00:00:00Z")
    audit = doc["entries"][0]["audit"]
    assert audit["status"] == "keep" and audit["vision_doubt"] == ["the vision check sees more than one object"]
    assert C.usable(doc["entries"][0])


def test_pass_two_asks_contradictory_untitled_models():
    from wenart.assets.audit import cli
    gen = item(id="gen_x", source="generated", licence="generated (TRELLIS.2-4B, MIT)",
               title="Generated modern sofa (1)", units_known=False)
    assert cli.second_pass_ids([gen], {"gen_x": dict(YES, is_type=False, type_guess="sofa")}) == {"gen_x"}
    assert cli.second_pass_ids([gen], {"gen_x": dict(YES, is_type=False, type_guess="bench")}) == set()
