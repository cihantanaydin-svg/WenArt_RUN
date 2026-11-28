"""Audit fix round 5a (27 Nov 2026): R09 one size-tag grammar and its binding step, R08 entrances from drawn evidence,
R16 outdoor-space checks, R28 room names, R21 block typing, R18 fixed equipment in its room's context, and the check
pod's queue (the schedule words Argus counted as rooms, real15's balconies with no door, real17's shower doors).
Synthetic buildings, texts and blocks built in code; real06, real07, real15 and real17 are read once each (skipped
without a DWG converter). 28 Nov 2026: the round's fix-up (``test_fixup_*``, the independent review's findings and weak
tests, the coordinator's decisions on R08, R09, R16, R21, R28 and the porch)."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------------------------------------------------
# R09: one size-tag parser
# --------------------------------------------------------------------------------------------------------------------

def test_r09_the_parser_table():
    from wenart.ingest import tag_grammar as TG
    t = TG.parse("CK3 350/220")
    assert (t.w_cm, t.h_cm, t.code, t.number, t.kind, t.glazed) == (350, 220, "CK", "3", "door", True)
    t = TG.parse("K3-100/210")
    assert (t.w_cm, t.h_cm, t.code, t.kind) == (100, 210, "K", "door")
    t = TG.parse("180/210 FRANSIZ PENCERE")
    assert (t.w_cm, t.h_cm, t.kind, t.floor_level) == (180, 210, "french_window", True)
    t = TG.parse("70/150")
    assert (t.w_cm, t.h_cm, t.kind, t.bare) == (70, 150, None, True)
    t = TG.parse("P2:60/60")
    assert (t.w_cm, t.h_cm, t.kind) == (60, 60, "window")
    t = TG.parse("200/210 SÜRGÜ KAPI")
    assert (t.kind, t.operation) == ("door", "sliding")
    # 28 Nov 2026 (fix-up TAGS-1): a type number glued to a 3-digit width reads both ways, the type number first
    # ('K290/210' = K2 + 90/210 or 2.90 m); a glued 4-digit group is the type number and a 3-digit width
    t = TG.parse("K290/210")
    assert (t.number, t.w_cm, t.w_alt_cm, t.ambiguous) == ("2", 90, 290, True)
    assert TG.parse("K2100/210").w_cm == 100 and not TG.parse("K2100/210").ambiguous
    assert TG.parse("P3130/150").w_cm == 130
    assert TG.parse("K 290/210").w_cm == 290 and not TG.parse("K 290/210").ambiguous   # spaced: no type number
    assert TG.parse("K100/210").w_cm == 100 and not TG.parse("K100/210").ambiguous     # 'K1' + 00 is no width
    assert TG.glued_convention(["K290/210", "P3130/150"]) == "type_number"
    assert TG.glued_convention(["K290/210", "K1-80/210"]) is None
    t = TG.parse("K290/210", convention="type_number")
    assert (t.w_cm, t.ambiguous) == (90, False)
    assert TG.parse("K290/210").pick(0.88).w_cm == 90 and TG.parse("K290/210").pick(2.85).w_cm == 290
    assert TG.parse("K290/210").pick(1.5, tol=0.15) is None
    assert TG.parse("120/150 TİP A").kind is None                  # a type note keeps the tag (no door, no window)
    assert TG.parse("120/150 TÜR A").kind is None                  # TAGS-9: the Turkish TÜR is a type, never 'Tür'
    for text in ("(19X17.36Rh=330/27)", "Rh=330/27", "17X17.64Rh=300/27", "(17x 17.65 / 28)", "1/50",
                 "120/90 TEZGAH", "SALON", "A=12/30"):
        assert TG.parse(text) is None, text
    assert TG.parse("120/210", layer="OLCU") is None              # a dimension layer's text is no tag
    assert TG.parse("120/210", layer="KAPI") is not None


def test_r09_every_reader_asks_the_one_parser():
    from wenart.blender import architect_actions as AA
    from wenart.ingest import core_rules, sense_rules, twins
    from wenart.ingest.generic import core, decisions
    from wenart.reading_check import crossdoc
    for mod, name in ((core, "SIZE_TAG_RE"), (core, "K_TAG_RE"), (core, "WINDOW_TAG_RE"), (core, "OPENING_TAG_RE"),
                      (decisions, "SIZE_TAG_RE"), (sense_rules, "TAG_RE"), (twins, "DOOR_SIZE_TAG_RE"),
                      (core_rules, "SIZE_TAG_RE"), (core_rules, "WINDOW_TAG_RE"), (AA, "DOOR_TAG_RE")):
        assert not hasattr(mod, name), f"{mod.__name__}.{name} is a second tag grammar"
    assert sense_rules._tag_cm("CK3 260/240", door=True) == (260, 240)
    assert sense_rules._tag_cm("P1-120/150", door=True) is None
    assert AA._tag_cm("K3-100/210") == (100, 210)
    assert crossdoc.size_tag_re().match("CK3 350/220").group(1) == "350"
    assert decisions._classify_text(_Run("K1-80/210")).size_tag == (0.8, 2.1)


class _Run:
    def __init__(self, text, x=0.0, y=0.0, h=0.1, layer=None):
        self.text, self.height = text, h
        self.box = (x - 0.2, y - h / 2, x + 0.2, y + h / 2)
        self.evidence = [{"layer": layer}] if layer else []
        self.rotation_deg = 0.0


def _wall(wid, a, b, t=0.2, lid="L1"):
    return {"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t, "height": 3.0}


def _box_building(lid="L1", z=3.0, order=1):
    return {"levels": [{"id": lid, "elevation": z, "order": order}], "site": {"outdoor_spaces": []},
            "rooms": [{"id": "r1", "level_id": lid, "polygon": [[0.1, 0.1], [5.9, 0.1], [5.9, 4.9], [0.1, 4.9]],
                       "label": "SALON", "label_raw": "SALON", "room_type": "living"}],
            "walls": [_wall("w_s", (0, 0), (6, 0), lid=lid), _wall("w_e", (6, 0), (6, 5), lid=lid),
                      _wall("w_n", (6, 5), (0, 5), lid=lid), _wall("w_w", (0, 5), (0, 0), lid=lid)],
            "openings": []}


def _win(oid, wall, c, w, lid="L1"):
    return {"id": oid, "level_id": lid, "type": "window", "wall_id": wall, "center": list(c), "width": w,
            "height": 1.2, "sill_height": 0.9, "assumed": ["height", "sill_height"], "evidence": [{"file": "x"}]}


def test_r09_a_glass_door_tag_on_the_window_layer_makes_the_balcony_reachable():
    from wenart.ingest import tag_binding as TBN
    b = _box_building()
    b["site"]["outdoor_spaces"] = [{"id": "os_b", "level_id": "L1", "kind": "balcony",
                                   "polygon": [[0, -1.5], [6, -1.5], [6, -0.1], [0, -0.1]]}]
    b["openings"] = [_win("w1", "w_s", (3.0, 0.0), 2.55)]
    TBN.bind(b, {"L1": [{"text": "CK3 260/240", "x": 3.0, "y": -0.35, "entity": "T1", "layer": "pencere"}]})
    o = b["openings"][0]
    assert (o["type"], o["width"], o["height"], o["sill_height"]) == ("door", 2.6, 2.4, None)
    assert o["door_tags"] == ["CK3 260/240"] and o["adjusted_by_ai"]["rule"] == "size_tag_door"
    assert TBN.space_doors(b) == [{"space": "os_b", "door": "w1"}] and b["site"]["outdoor_spaces"][0]["doors"] == ["w1"]


def test_r09_a_french_window_split_at_its_mullion_is_one_floor_level_opening():
    from wenart.ingest import tag_binding as TBN
    b = _box_building()
    b["openings"] = [_win("w2", "w_n", (2.6, 5.0), 0.80), _win("w3", "w_n", (3.5, 5.0), 0.80)]
    TBN.bind(b, {"L1": [{"text": "180/210 FRANSIZ PENCERE", "x": 3.05, "y": 5.4, "entity": "T2",
                         "layer": "pencere"}]})
    assert [o["id"] for o in b["openings"]] == ["w2"] and b["openings_merged"][0]["id"] == "w3"
    o = b["openings"][0]
    assert (o["type"], o["width"], o["height"], o["sill_height"], o["french_window"]) == \
        ("window", 1.8, 2.1, 0.0, True)
    assert o["sill_height_source"].startswith("size tag") and "sill_height" not in o["assumed"]


def test_r09_one_tag_on_two_garage_bays_gives_one_type():
    from wenart.ingest import tag_binding as TBN
    b = _box_building(lid="L0", z=0.0, order=0)
    b["rooms"][0].update(label="GARAJ", label_raw="GARAJ", room_type="garage")
    door = {"id": "d1", "level_id": "L0", "type": "door", "wall_id": "w_n", "center": [1.8, 5.0], "width": 3.45,
            "height": 2.1, "assumed": ["height"], "evidence": [{"file": "x"}]}
    b["openings"] = [door, _win("w4", "w_s", (1.3, 0.0), 1.62, "L0"), _win("w5", "w_s", (3.05, 0.0), 1.70, "L0")]
    texts = [{"text": "CK3 350/220", "x": 1.8, "y": 5.4, "entity": "T1", "layer": "pencere"},
             {"text": "CK3 350/220", "x": 2.2, "y": -0.4, "entity": "T2", "layer": "pencere"}]
    TBN.bind(b, {"L0": texts})
    types = sorted(o["type"] for o in b["openings"])
    host = next(o for o in b["openings"] if o["id"] != "d1")
    assert types == ["door", "door"] and len(b["openings_merged"]) == 1 and abs(host["width"] - 3.5) < 1e-6


def test_r09_a_second_smaller_leaf_in_the_gap_makes_one_unequal_double_door():
    from wenart.ingest import tag_binding as TBN
    b = _box_building(lid="L0", z=0.0, order=0)
    b["walls"].append(_wall("w_g", (8.0, 0.0), (8.0, 1.5), lid="L0"))
    d = {"id": "d1", "level_id": "L0", "type": "door", "wall_id": "w_g", "center": [8.0, 0.97], "width": 0.9,
         "height": 2.1, "operation": "swing", "evidence": [{"file": "x", "method": "vector",
                                                             "entity": "LWPOLYLINE:C19C:1,LWPOLYLINE:C19C:0"}]}
    b["openings"] = [d]
    b["symbols"] = [{"id": "sy1", "kind": "door_arc", "level_id": "L0",
                     "footprint": {"center": [7.73, 0.35], "size": [0.63, 0.13]},
                     "evidence": [{"entity": "LWPOLYLINE:C19C:2"}]}]
    TBN.bind(b, {"L0": [{"text": "150/210", "x": 7.8, "y": 0.75, "entity": "T1", "layer": "kapi"}]})
    assert (d["width"], d["operation"], d["leaves"]) == (1.5, "double", [0.9, 0.6])
    assert abs(d["center"][1] - 0.75) < 1e-6                     # the door fills its 1.5 m wall gap


def test_r09_a_door_takes_no_window_height_tag():
    from wenart.ingest import tag_binding as TBN
    from wenart.ingest import tag_grammar as TG
    assert not TBN.kind_agrees(TG.parse("70/140"), {"type": "door"})
    assert TBN.kind_agrees(TG.parse("K1-80/210"), {"type": "door"})
    assert not TBN.kind_agrees(TG.parse("P1-120/220"), {"type": "door"})
    assert not TBN.kind_agrees(TG.parse("90/210"), {"type": "window"})       # a bare door-like tag is a door's
    assert TBN.kind_agrees(TG.parse("150/210"), {"type": "window"})
    b = _box_building()
    b["openings"] = [{"id": "d1", "level_id": "L1", "type": "door", "wall_id": "w_s", "center": [3.0, 0.0],
                      "width": 0.54, "height": 2.1, "assumed": ["height"], "evidence": [{"file": "x"}]}]
    TBN.bind(b, {"L1": [{"text": "70/140", "x": 3.0, "y": 0.4, "entity": "T1", "layer": "yazi"}]})
    assert b["openings"][0]["height"] == 2.1 and "size_tag" not in b["openings"][0]


# --------------------------------------------------------------------------------------------------------------------
# R08: entrances from drawn evidence
# --------------------------------------------------------------------------------------------------------------------

def _porch_building():
    """L0 at +0.50 over a ±0.00 ground: an ANTRE (x 3-7), a 1.15 x 1.85 m unlabelled recess (x 7.25-8.4) east of it
    behind a 1.88 m facade gap the levels model typed a window, the door between them, the ground mark 1.6 m out."""
    lid = "L0"
    rooms = [{"id": "r_antre", "level_id": lid, "polygon": [[3.1, 8.0], [7.0, 8.0], [7.0, 12.0], [3.1, 12.0]],
              "label": "Antre", "label_raw": "ANTRE", "room_type": "hall"},
             {"id": "r_oda", "level_id": lid, "polygon": [[7.25, 9.35], [8.4, 9.35], [8.4, 11.2], [7.25, 11.2]],
              "label": "Oda", "label_raw": None, "room_type": "hall", "area_computed": 2.13}]
    walls = [_wall("w_s", (3.0, 7.9), (8.5, 7.9), lid=lid), _wall("w_n", (3.0, 12.1), (8.5, 12.1), lid=lid),
             _wall("w_w", (3.0, 7.9), (3.0, 12.1), lid=lid), _wall("w_mid", (7.125, 7.9), (7.125, 12.1), 0.25, lid),
             _wall("w_ps", (7.0, 9.25), (8.5, 9.25), lid=lid), _wall("w_pn", (7.0, 11.3), (8.5, 11.3), lid=lid),
             _wall("w_e", (8.5, 7.9), (8.5, 12.1), lid=lid)]
    gap = {"id": "o_gap", "level_id": lid, "type": "window", "drawn_type": "opening", "wall_id": "w_e",
           "center": [8.5, 10.28], "width": 1.876, "height": 1.5, "sill_height": 0.7, "drawn_height": None,
           "drawn_sill_height": None, "type_inferred": {"method": "facade_gap", "reason": "a window"},
           "evidence": [{"file": "x"}]}
    door = {"id": "d_in", "level_id": lid, "type": "door", "wall_id": "w_mid", "center": [7.125, 9.925],
            "width": 1.0, "height": 2.1, "evidence": [{"file": "x"}]}
    return {"project": {"id": "t"}, "levels": [{"id": lid, "elevation": 0.5, "order": 0}],
            "rooms": rooms, "walls": walls, "openings": [gap, door],
            "level_marks": [{"id": "lm_g", "level_id": lid, "kind": "ground_finished", "z": 0.0, "raw": "±0,00",
                             "point": [9.5, 8.9]}],
            "site": {"ground": {"levels": [{"z": {"value": 0.0}}]}, "entrances": [], "outdoor_spaces": []}}


def test_r08_a_facade_gap_before_a_small_recess_with_a_ground_mark_outside_is_an_open_porch():
    from wenart.ingest import porches as PCH
    b = _porch_building()
    recs = PCH.open_porches(b)
    gap, door = b["openings"]
    room = b["rooms"][1]
    assert recs and gap["type"] == "opening" and gap["sill_height"] is None
    assert gap["type_inferred"]["method"] == "open_porch"
    assert (room["room_type"], room["label"], room["label_inferred"]["role"]) == ("porch", "Giriş", "porch")
    ent = next(e for e in b["site"]["entrances"] if e["door_id"] == "d_in")
    assert ent["main"] and ent["solution"] == "steps" and abs(ent["rise"] - 0.5) < 1e-6


def test_r08_garden_steps_next_to_a_real_window_open_nothing():
    from wenart.ingest import porches as PCH
    b = _porch_building()
    gap = b["openings"][0]
    gap.update(drawn_type="window", type_inferred=None)      # a drawn window symbol: its bottom is no floor
    assert PCH.open_porches(b) == [] and gap["type"] == "window"
    b = _porch_building()
    b["levels"][0]["elevation"] = 2.5                          # 2.5 m over the ground: no small drop
    b["level_marks"] = []
    assert PCH.open_porches(b) == []


def test_r08_entrance_words_outside_the_walls_name_the_nearest_door_only():
    from wenart.ingest import porches as PCH
    b = _box_building(lid="L0", z=0.0, order=0)
    d1 = {"id": "d_bina", "level_id": "L0", "type": "door", "wall_id": "w_e", "center": [6.0, 3.0], "width": 1.5,
          "height": 2.1, "evidence": [{"file": "x"}]}
    d2 = {"id": "d_shop", "level_id": "L0", "type": "door", "wall_id": "w_w", "center": [0.0, 2.0], "width": 1.0,
          "height": 2.1, "evidence": [{"file": "x"}]}
    b["openings"] = [d1, d2]
    b["site"]["entrances"] = [{"door_id": "d_shop", "main": True, "level_id": "L0"},
                              {"door_id": "d_bina", "main": False, "level_id": "L0"}]
    texts = [{"text": "BİNA", "x": 7.3, "y": 3.15, "entity": "T1"}, {"text": "GİRİŞİ", "x": 7.3, "y": 2.95, "entity": "T2"},
             {"text": "DÜKKAN", "x": -1.3, "y": 2.15, "entity": "T3"},
             {"text": "GİRİŞİ", "x": -1.3, "y": 1.95, "entity": "T4"},
             {"text": "GİRİŞ HOLÜ", "x": 3.0, "y": 2.5, "entity": "T5"}]
    PCH.entrance_words(b, {"L0": texts})
    main = {e["door_id"]: e["main"] for e in b["site"]["entrances"]}
    assert main == {"d_bina": True, "d_shop": False}
    assert d1["entrance_of"] == "building" and d2["entrance_of"] == "shop"
    assert d1["entrance_word"]["text"] == "BİNA GİRİŞİ"


# --------------------------------------------------------------------------------------------------------------------
# R16: outdoor-space checks
# --------------------------------------------------------------------------------------------------------------------

def _levels():
    return {"L0": {"id": "L0", "elevation": 0.0}, "L1": {"id": "L1", "elevation": 3.0}}


def test_r16_a_rectangle_far_off_its_stated_area_is_built_with_a_finding():
    """28 Nov 2026 (fix-up decision, GENERAL-4): a labelled space is never dropped for a poor fallback outline."""
    from wenart.ingest import outdoor_checks as OC
    why, finding = OC.verdict({"anchor": [5.5, 10.4]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner",
                              [[5.05, 9.35], [6.3, 9.35], [6.3, 11.0], [5.05, 11.0]], 3.78, ["d1"], [], [])
    assert why is None and finding and "stated 3.78" in finding
    why, finding = OC.verdict({"anchor": [5.5, 10.4]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner",
                              [[5.05, 9.35], [6.3, 9.35], [6.3, 11.0], [5.05, 11.0]], 3.78, [], [], [])
    assert why is None and finding                     # no door either: still built (a finding), its label is drawn
    assert OC.verdict({"anchor": [5.5, 10.4]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner",
                      [[5.0, 8.3], [6.4, 8.3], [6.4, 11.0], [5.0, 11.0]], 3.78, ["d1"], [], []) == (None, None)


def test_r16_an_upper_label_with_the_lower_floor_mark_and_no_door_is_the_lower_space_seen_from_above():
    from wenart.ingest import outdoor_checks as OC
    from wenart.levels import outdoor as OD
    area = {"anchor": [2.08, 12.89], "label": "TERAS", "id": "sa_L1_teras"}
    marks = [{"id": "lm_022", "level_id": "L1", "z": 0.0, "raw": "+0.50", "point": [2.25, 12.61]}]
    poly = [[-5.5, 5.0], [9.7, 5.0], [9.7, 20.7], [-5.5, 20.7]]
    why = OC.refuse(area, "terrace", "L1", _levels(), "L0", "rectangle in the inner corner", poly, None, [],
                    [], marks, OD.space_kind)
    assert why and "seen from above" in why
    # ENTRANCES-5: a door lands on it: never dropped
    assert OC.refuse(area, "terrace", "L1", _levels(), "L0", "rectangle in the inner corner", poly, None, ["d1"],
                     [], marks, OD.space_kind) is None
    # ENTRANCES-5: the mark inside the storey's own outline is no lower storey's mark printed over the space
    outline = [[0, 10], [5, 10], [5, 15], [0, 15]]
    assert OC.refuse(area, "terrace", "L1", _levels(), "L0", "rectangle in the inner corner", poly, None, [],
                     [], marks, OD.space_kind, outline) is None
    # no mark, no door, a same-kind space under it: a stacked space, kept (unreached judges it with its twin)
    lower = {"anchor": [2.07, 12.9], "label": "TERAS", "level_id": "L0"}
    assert OC.refuse(area, "terrace", "L1", _levels(), "L0", "rectangle in the inner corner", poly, None, [],
                     [lower, area], [], OD.space_kind) is None
    # a drawn upper balcony is kept whatever its mark
    assert OC.refuse(area, "balcony", "L1", _levels(), "L0", "strokes", poly, None, [], [], marks, OD.space_kind) is None
    # the refusal is recorded once per area (a re-run of the levels model replaces it: ENTRANCES-6)
    b = {"site": {}}
    OC.record_refusal(b, area, "L1", poly, "rectangle", why)
    OC.record_refusal(b, area, "L1", poly, "rectangle", why)
    assert len(b["site"]["outdoor_spaces_refused"]) == 1


def test_r16_a_door_beside_an_inferred_balcony_reaches_it_even_when_the_landing_probe_missed():
    from wenart.ingest import outdoor_checks as OC
    poly = [[0.0, -1.4], [3.0, -1.4], [3.0, -0.1], [0.0, -0.1]]
    b = {"openings": [{"id": "d1", "level_id": "L1", "type": "door", "center": [1.5, 0.3], "width": 0.9},
                      {"id": "w1", "level_id": "L1", "type": "window", "center": [2.5, 0.0], "width": 1.2,
                       "sill_height": 0.9}]}
    assert OC.doors_near(b, "L1", poly) == ["d1"]
    assert OC.facing_window(b, "L1", poly) is None                  # a 0.90 m sill is no door
    b["openings"][1]["sill_height"] = 0.1
    assert OC.facing_window(b, "L1", poly)["id"] == "w1"


def test_r16_at_the_end_of_the_reading_a_space_no_door_reaches_is_a_finding_naming_its_probable_door():
    """28 Nov 2026 (fix-up decision): never a silent drop; a facing low-sill window is named; a stacked twin a door
    reaches gives its status."""
    from wenart.ingest import outdoor_checks as OC
    rect = [[0.0, -1.4], [3.0, -1.4], [3.0, -0.1], [0.0, -0.1]]
    far = [[10.0, -1.4], [13.0, -1.4], [13.0, -0.1], [10.0, -0.1]]
    b = {"levels": [{"id": "L0", "elevation": 0.0, "order": 0}, {"id": "L1", "elevation": 3.0, "order": 1},
                    {"id": "L2", "elevation": 6.0, "order": 2}],
         "openings": [{"id": "d1", "level_id": "L1", "type": "door", "center": [1.5, 0.0], "width": 0.9},
                      {"id": "w9", "level_id": "L1", "type": "window", "center": [11.5, 0.0], "width": 1.6,
                       "sill_height": 0.0}],
         "site": {"outdoor_spaces": [
             {"id": "os1", "level_id": "L1", "kind": "balcony", "label": "BALKON", "method": "rectangle in the inner "
              "corner", "polygon": rect, "doors": []},
             {"id": "os2", "level_id": "L1", "kind": "balcony", "label": "BALKON", "method": "rectangle in the inner "
              "corner", "polygon": far, "doors": []},
             {"id": "os3", "level_id": "L2", "kind": "balcony", "label": "BALKON", "method": "rectangle in the inner "
              "corner", "polygon": rect, "doors": []}]}}
    got = {r["space"]: r for r in OC.unreached(b)}
    assert [s["id"] for s in b["site"]["outdoor_spaces"]] == ["os1", "os2", "os3"]     # nothing dropped
    assert "os1" not in got
    assert got["os2"]["probable_door"] == "w9" and "probable balcony door" in got["os2"]["reason"]
    assert b["site"]["outdoor_spaces"][1]["finding"]["probable_door"] == "w9"
    assert got["os3"]["twin"] == "os1" and "stacked twin" in got["os3"]["reason"]
    assert not b["site"].get("outdoor_spaces_refused")
    # a purely inferred space (no label, no door, no window, no twin) is not built, as a finding
    b["site"]["outdoor_spaces"].append({"id": "os4", "level_id": "L1", "kind": "balcony", "label": "",
                                        "method": "rectangle", "polygon": [[20, -1.4], [23, -1.4], [23, -0.1],
                                                                           [20, -0.1]], "doors": []})
    got = {r["space"]: r for r in OC.unreached(b)}
    assert got["os4"].get("refused") and b["site"]["outdoor_spaces_refused"][0]["id"] == "os4"


def test_r16_an_inferred_upper_space_stays_within_2_m_of_the_storeys_under_it():
    from wenart.ingest import outdoor_checks as OC
    outline = [[0, 0], [10, 0], [10, 10], [0, 10]]
    poly, why = OC.clip_upper([[-5.5, 2.0], [3.0, 2.0], [3.0, 6.0], [-5.5, 6.0]], "L1", _levels(), {"L0": outline},
                              "L0")
    assert why and min(p[0] for p in poly) >= -2.0 - 1e-6
    # a basement's space is no upper space
    levels = dict(_levels(), **{"L-1": {"id": "L-1", "elevation": -3.0}, "L-2": {"id": "L-2", "elevation": -6.0}})
    assert OC.clip_upper([[-5.5, 2.0], [3.0, 2.0], [3.0, 6.0], [-5.5, 6.0]], "L-1", levels, {"L-2": outline},
                         "L0")[1] is None
    assert OC.refuse({"anchor": [0, 3]}, "terrace", "L-1", levels, "L0", "rectangle against the facade",
                     [[-5.5, 2.0], [3.0, 2.0], [3.0, 6.0], [-5.5, 6.0]], None, [], [], []) is None
    # GENERAL-13: a basement wider than the storeys over the ground (a car park under the garden) widens nothing
    wide = [[-20, -20], [30, -20], [30, 30], [-20, 30]]
    poly, why = OC.clip_upper([[-5.5, 2.0], [3.0, 2.0], [3.0, 6.0], [-5.5, 6.0]], "L1", levels,
                              {"L0": outline, "L-1": wide}, "L0")
    assert why and min(p[0] for p in poly) >= -2.0 - 1e-6


# --------------------------------------------------------------------------------------------------------------------
# R28: room names
# --------------------------------------------------------------------------------------------------------------------

def test_r28_an_area_unit_written_apart_goes_to_the_area_never_to_the_name():
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.generic.model import TextRun
    runs = [TextRun(id="T1", text="ANTRE", box=(0, 0.3, 0.5, 0.4), height=0.1),
            TextRun(id="T2", text="7,20", box=(0, 0.15, 0.25, 0.25), height=0.1),
            TextRun(id="T3", text="m²", box=(0.27, 0.15, 0.4, 0.25), height=0.1)]
    blocks = LB.merge_label_blocks(runs)
    assert [(bl.name, bl.area_m2) for bl in blocks] == [("ANTRE", 7.2)]
    blocks = LB.merge_label_blocks([TextRun(id="T1", text="ANTRE m²", box=(0, 0.3, 0.6, 0.4), height=0.1)])
    assert [bl.name for bl in blocks] == ["ANTRE"]
    # real06's boxes: the unit's box overlaps the number's (its centre stands right of the number's)
    runs = [TextRun(id="T1", text="ANTRE", box=(4.88, 10.74, 5.40, 10.88), height=0.14),
            TextRun(id="T2", text="7,20", box=(4.905, 10.514, 5.325, 10.654), height=0.14),
            TextRun(id="T3", text="m²", box=(5.26, 10.514, 5.47, 10.654), height=0.14)]
    assert [(bl.name, bl.area_m2) for bl in LB.merge_label_blocks(runs)] == [("ANTRE", 7.2)]


def test_r21_a_small_walled_face_is_read_by_its_words_shower_toilet_heater_laundry_never_storage():
    """28 Nov 2026 (fix-up decision, WET-1 / GENERAL-7): only a shower or bath word makes a shower cell; a heater,
    boiler or drain word a technical closet, a laundry word a laundry, a toilet word a WC; a drawn shower in a cell no
    text names makes it a shower cell after the furniture is read."""
    from shapely.geometry import box
    from wenart.ingest import fixed_context as FXC
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.model import OpeningItem, WallItem

    def wall(a, b):
        return WallItem(start=a, end=b, thickness=0.1, box=[0, 0, 0, 0], entity="w", evidence={})
    walls = [wall((0, 0), (1.4, 0)), wall((1.4, 0), (1.4, 1.3)), wall((1.4, 1.3), (0, 1.3)), wall((0, 1.3), (0, 0))]
    door = OpeningItem(kind="door", width=0.7, center=(0.7, 0.0), rotation_deg=0.0, box=[0.35, -0.05, 1.05, 0.05],
                       entity="d", evidence={})
    face = box(0.05, 0.05, 1.35, 1.25)
    for text, rtype, label in (("E.ŞOFBEN", "technical", "Teknik Hacim"), ("KOMBİ", "technical", "Teknik Hacim"),
                               ("SÜZGEÇ", "technical", "Teknik Hacim"), ("BOYLER", "technical", "Teknik Hacim"),
                               ("ÇAMAŞIR", "other", "Çamaşırlık"), ("DUŞ", "bathroom", "Duş"),
                               ("DUŞAKABİN", "bathroom", "Duş"), ("DUŞ TEKNESİ", "bathroom", "Duş"),
                               ("KÜVET", "bathroom", "Duş"), ("WC", "wc", "WC")):
        got, why = TP.unlabelled_face_type(face, walls, [door], texts=[(text, (0.7, 0.9))])
        assert (got, TP.wet_cell_label(why, True)) == (rtype, label), text
    rtype, why = TP.unlabelled_face_type(face, walls, [door], texts=[])
    assert rtype == "storage"
    # a heater closet with a drawn shower tray in it is a shower cell once the furniture is read (real15)
    b = {"rooms": [{"id": "r1", "level_id": "L0", "label": "Teknik Hacim", "label_raw": None, "room_type": "technical",
                    "label_role": True, "polygon": [[0, 0], [1.4, 0], [1.4, 1.3], [0, 1.3]]},
                   {"id": "r2", "level_id": "L0", "label": "Teknik Hacim", "label_raw": None, "room_type": "technical",
                    "label_role": True, "polygon": [[2, 0], [3.4, 0], [3.4, 1.3], [2, 1.3]]}],
         "furniture": [{"id": "f1", "type": "shower", "room_id": "r1", "source": "from_documents",
                        "footprint": {"center": [0.5, 0.5], "size": [0.8, 0.8], "rotation_deg": 0}}]}
    recs = FXC.wet_cells(b)
    assert [r["room"] for r in recs] == ["r1"] and b["rooms"][0]["room_type"] == "bathroom"
    assert b["rooms"][0]["label"] == "Duş" and b["rooms"][1]["room_type"] == "technical"


def test_r28_an_unnamed_face_takes_its_open_neighbours_label_or_a_role_name_never_oda():
    from wenart.ingest import room_names as RN
    from wenart.reading_check import sense
    rooms = [{"id": "r_hol", "level_id": "L1", "label": "Hol", "label_raw": "HOL", "room_type": "hall",
              "polygon": [[0, 0], [3, 0], [3, 3], [0, 3]]},
             {"id": "r_oda", "level_id": "L1", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[3, 0], [4.4, 0], [4.4, 3], [3, 3]]},
             {"id": "r_oda_2", "level_id": "L1", "label": "Oda", "label_raw": None, "room_type": "hall",
              "polygon": [[6, 0], [12, 0], [12, 1.2], [6, 1.2]]},
             {"id": "r_bed", "level_id": "L1", "label": "Ebeveyn Y.Odası", "label_raw": "EBEVEYN Y.ODASI",
              "room_type": "bedroom", "polygon": [[0, 5], [4, 5], [4, 9], [0, 9]]},
             {"id": "r_soy", "level_id": "L1", "label": "Soyunma Odası", "label_raw": "SOYUNMA ODASI",
              "room_type": "other", "polygon": [[4, 5], [6, 5], [6, 9], [4, 9]]}]
    b = {"rooms": rooms, "openings": [
        {"id": "o1", "level_id": "L1", "type": "opening", "center": [3.0, 1.5], "width": 1.4},
        {"id": "d1", "level_id": "L1", "type": "door", "center": [4.0, 7.0], "width": 0.8}]}
    RN.name_faces(b)
    assert rooms[1]["label"] == "Hol" and rooms[1]["label_inferred"]["method"] == "open_neighbour"
    assert rooms[2]["label"] == "Koridor" and rooms[2]["label_role"] is True
    assert all(r["label"] != "Oda" for r in rooms)
    assert rooms[1]["label_raw"] is None and sense._label(rooms[1]) == ""
    assert rooms[4]["room_use"] == "dressing" and rooms[4]["dressing_of"] == "r_bed"


# --------------------------------------------------------------------------------------------------------------------
# R21: block typing
# --------------------------------------------------------------------------------------------------------------------

def test_r21_block_name_abbreviations_type_by_whole_tokens():
    from wenart.ingest.generic import symbols as SY
    for name, want in (("KLO", "toilet"), ("klo-01", "toilet"), ("KLOZET1", "toilet"), ("LAV_2", "washbasin"),
                       ("KÜVET", "bathtub"), ("kuv", "bathtub"), ("EVİYE", "sink_kitchen"), ("DUŞ TEKNE", "shower")):
        assert SY.keyword_type(name) == want, name
    for name in ("LAVANTA", "BLOCK_LAVAL", "KUVVET", "KLASOR", "199"):
        assert SY.abbreviation_type(name) is None, name


def test_r21_copies_of_one_block_typed_differently_take_the_strongest_majority():
    from wenart.furniture import infer as IF

    def piece(pid, ftype, method):
        return {"id": pid, "type": ftype, "type_method": method, "source": "from_documents", "level_id": "L0",
                "footprint": {"center": [0, 0], "size": [0.36, 0.52], "rotation_deg": 0},
                "evidence": [{"method": "vector", "entity": f"INSERT:{pid}/1", "block": "KLO"}]}
    pieces = [piece("a", "toilet", "block_name"), piece("b", "toilet", "block_name"), piece("c", "bidet", "ai_two_pass"),
              piece("d", "unknown", None)]
    got = IF._same_block_type({"furniture": pieces}, pieces[3])
    assert got and got["type"] == "toilet" and "majority" in got["reason"]


# --------------------------------------------------------------------------------------------------------------------
# R18: fixed equipment in its room's context
# --------------------------------------------------------------------------------------------------------------------

def test_r18_a_counter_run_along_a_bedroom_wall_is_a_wardrobe_and_a_kitchen_keeps_its_counter():
    from wenart.ingest import fixed_context as FXC
    rooms = [{"id": "r_bed", "label": "Yatak Odası", "label_raw": "YATAK ODASI", "room_type": "bedroom",
              "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]},
             {"id": "r_kit", "label": "Mutfak", "label_raw": "MUTFAK", "room_type": "kitchen",
              "polygon": [[4, 0], [8, 0], [8, 4], [4, 4]]}]

    def counter(pid, room, x, method="ai_two_pass"):
        return {"id": pid, "type": "kitchen_counter", "type_method": method, "source": "from_documents",
                "room_id": room, "footprint": {"center": [x, 0.3], "size": [2.4, 0.6], "rotation_deg": 0}}
    furn = [counter("f1", "r_bed", 2.0), counter("f2", "r_kit", 6.0), counter("f3", "r_bed", 2.0, "block_name")]
    b = {"rooms": rooms, "furniture": furn}
    recs = FXC.kitchen_context(b)
    assert [r["piece"] for r in recs] == ["f1"]
    assert (furn[0]["type"], furn[0]["drawn_type"]) == ("wardrobe", "kitchen_counter")
    assert furn[1]["type"] == "kitchen_counter" and furn[2]["type"] == "kitchen_counter"


def test_r18_a_drawn_tub_stays_a_tub_in_every_bathroom():
    from wenart.furniture import infer as IF
    rooms = [{"id": f"r{i}", "level_id": lv, "room_type": t} for i, (lv, t) in
             enumerate([("L1", "bathroom"), ("L1", "bedroom"), ("L1", "bedroom"), ("L0", "bathroom")])]

    def tub(pid, room, method):
        return {"id": pid, "type": "bathtub", "type_method": method, "source": "from_documents", "room_id": room,
                "footprint": {"center": [0, 0], "size": [1.7, 0.75], "rotation_deg": 0}, "front_deg": 0}
    furn = [tub("t1", "r0", "ai_two_pass"), tub("t2", "r3", "ai_two_pass")]
    IF.bath_or_shower({"rooms": rooms, "furniture": furn, "project": {}})
    assert [f["type"] for f in furn] == ["bathtub", "bathtub"]
    assert IF.tub_drawn({"type_method": "ai_two_pass"}) and not IF.tub_drawn({"type_method": "inferred"})
    furn = [tub("t1", "r0", "inferred"), tub("t2", "r3", "inferred")]
    IF.bath_or_shower({"rooms": rooms, "furniture": furn, "project": {}})
    assert [f["type"] for f in furn] == ["bathtub", "shower"]          # a box the code typed by size: UL200


# --------------------------------------------------------------------------------------------------------------------
# the check pod's queue: schedule words are no rooms; a door word between jambs is a door
# --------------------------------------------------------------------------------------------------------------------

def test_queue_a_room_schedules_words_are_a_note_for_argus():
    from wenart.audit import ledger as LG
    row = {"text": "SALON", "role": "schedule", "layer": "Z_yazı"}
    assert LG.classify_text(row) == "note"
    assert LG.classify_text(dict(row, role="room_label")) == "space_name"


def test_queue_a_door_word_without_a_size_is_door_evidence():
    from wenart.ingest.generic import core
    from wenart.ingest.generic.model import TextRun
    t = TextRun(id="T1", text="SÜRGÜ KAPI", box=(0.0, 0.0, 0.4, 0.1), height=0.1, evidence=[{"layer": "kapi"}])
    ev = core._door_evidence([t], [])
    assert len(ev) == 1 and ev[0][1] is None and ev[0][4]["door_word"] == "SÜRGÜ KAPI"
    t2 = TextRun(id="T2", text="KAPI GÖRÜNÜŞÜ VE DETAYLARI", box=(0.0, 0.0, 0.4, 0.1), height=0.1,
                 evidence=[{"layer": "kapi"}])
    assert core._door_evidence([t2], []) == []


# --------------------------------------------------------------------------------------------------------------------
# real projects (read once each)
# --------------------------------------------------------------------------------------------------------------------

def _converter() -> bool:
    from wenart.ingest import dwg
    return dwg.find_tool("dwg2dxf") is not None


@pytest.fixture(scope="module")
def reading(tmp_path_factory):
    cache: dict = {}

    def read(project: str) -> dict:
        if project not in cache:
            import json
            pdir = ROOT / "projects" / project
            if not pdir.is_dir() or not _converter():
                pytest.skip(f"{project}: no DWG or no converter")
            from wenart.reading_check import regress as R
            out = R.read_project(project, tmp_path_factory.mktemp(project))
            shutil.rmtree(out / "converted", ignore_errors=True)
            cache[project] = (json.loads((out / "building.json").read_text(encoding="utf-8")),
                              json.loads((out / "source_items.json").read_text(encoding="utf-8")))
        return cache[project]
    return read


def test_real15_glass_doors_reach_the_balconies_and_the_upper_terrace_label_is_not_built(reading):
    """28 Nov 2026 (weak test 31): no outdoor-space ids pinned (a refusal elsewhere renumbers them): every first-floor
    balcony is reached; the two 'CK3 260/240' glass doors open onto balconies."""
    b, items = reading("real15")
    spaces = [s for s in b["site"]["outdoor_spaces"]]
    balconies = [s for s in spaces if s["level_id"] == "L1" and s.get("kind") == "balcony"]
    assert len(balconies) >= 4 and all(s["doors"] for s in balconies)
    landed = {d for s in balconies for d in s["doors"]}
    glass = [o for o in b["openings"] if o.get("door_tags") == ["CK3 260/240"] and o["level_id"] == "L1"]
    assert len(glass) >= 2 and all(o["type"] == "door" and o.get("sill_height") is None and o["id"] in landed
                                   for o in glass)
    assert not any(s["level_id"] == "L1" and s.get("kind") == "terrace" for s in spaces)
    teras = next(a for a in b["site"]["areas"] if a.get("level_id") == "L1" and a.get("label") == "TERAS")
    assert teras["space"]["built"] is False and "seen from above" in teras["space"]["reason"]
    assert any(x.get("area_id") == teras.get("id") for x in b["site"].get("outdoor_spaces_refused") or [])
    assert b["status"] == "ok" or not any(w.startswith("schema") for w in b["warnings"])
    sched = [t for t in items["texts"] if t["text"] in ("SALON", "O. ODASI") and t["pos"][0] > 21]
    assert sched and all(t["role"] == "schedule" for t in sched)


def test_real17_french_windows_the_building_entrance_and_no_kitchen_door_into_the_air(reading):
    """ENTRANCES-5 / GENERAL-4 (28 Nov 2026): the SW corner balconies of L1 / L2 (a rectangle off its stated area)
    are built with their finding, so the kitchen doors land on them."""
    b, _items = reading("real17")
    fr = [o for o in b["openings"] if o["level_id"] == "L1" and o.get("type") == "window"
          and abs(float(o["center"][0]) - 5.29) < 0.1 and float(o["width"]) > 1.7]
    assert len(fr) == 2 and all(o["sill_height"] == 0.0 and abs(o["height"] - 2.1) < 1e-6 for o in fr)
    main = [e["door_id"] for e in b["site"]["entrances"] if e.get("main")]
    assert main == ["d_L0_001"]
    d = next(o for o in b["openings"] if o["id"] == "d_L0_001")
    assert d["entrance_word"]["text"].upper().startswith("B") and abs(float(d["width"]) - 1.5) < 1e-6
    for lid in ("L1", "L2"):
        corner = [s for s in b["site"]["outdoor_spaces"] if s["level_id"] == lid and s.get("finding")
                  and "stated 3.78" in s["finding"]["reason"]]
        assert corner and all(s["doors"] for s in corner), lid


def test_real06_the_east_porch_is_open_air_and_its_door_the_main_entrance(reading):
    """Weak tests 14 / 21: the porch carries ``label_role`` and gets no indoor furniture program."""
    from wenart.furniture import program as PR
    b, _items = reading("real06")
    porch = next(r for r in b["rooms"] if r["level_id"] == "L0" and r.get("room_type") == "porch")
    mouth = next(o for o in b["openings"] if (o.get("type_inferred") or {}).get("method") == "open_porch")
    assert mouth["type"] == "opening" and porch["label"] == "Giriş" and porch["label_role"] is True
    main = next(e for e in b["site"]["entrances"] if e.get("main"))
    door = next(o for o in b["openings"] if o["id"] == main["door_id"])
    assert door["door_tags"] == ["K3-100/210"] and abs(float(door["width"]) - 1.0) < 1e-6
    assert sum(1 for e in b["site"]["entrances"] if e.get("main")) == 1
    assert not any(r.get("label") == "Oda" and not r.get("label_raw") for r in b["rooms"])
    assert not PR.room_program(b, porch["id"])["groups"]


def test_real07_the_wide_passage_into_the_vestibule_is_no_entrance_door(reading):
    """Weak test 13 / ENTRANCES-1: o_L0_011 (a 2.31 m gap between the hall and the vestibule, the ground mark +0.50
    2.26 m out at its floor's level; truth: an open passage) never becomes a door."""
    b, _items = reading("real07")
    o = next(o for o in b["openings"] if o["id"] == "o_L0_011")
    assert o["type"] != "door"
    assert not any(e["door_id"] == "o_L0_011" for e in b["site"]["entrances"])


# ====================================================================================================================
# 28 Nov 2026: the round 5a fix-up (the independent review's findings; every case its own synthetic test)
# ====================================================================================================================

def _ex():
    class _E:
        notes: list = []
    e = _E()
    e.notes = []
    return e


def _trun(text, x, y, layer="KAPI", tid="t"):
    from wenart.ingest.generic.model import TextRun
    return TextRun(id=tid, text=text, box=(x - 0.2, y - 0.05, x + 0.2, y + 0.05), height=0.1,
                   evidence=[{"layer": layer, "entity": tid}])


def _op(kind, x, w, y=0.0, rot=0.0, **kw):
    import math
    from wenart.ingest.model import OpeningItem
    r = math.radians(rot)
    return OpeningItem(kind=kind, width=w, center=(x, y), rotation_deg=rot,
                       box=[x - w / 2 * math.cos(r), y - 0.1, x + w / 2 * math.cos(r), y + 0.1],
                       entity=f"{kind}{x}", evidence=kw.pop("evidence", {"method": "vector"}), **kw)


def test_fixup_tags1_real14s_tag_mix_binds_each_tag_to_its_own_door_with_the_type_number_convention():
    """TAGS-1 (real14's POZ layer: 'K290/210', 'K180/210', 'K280/240', 'P150/50' beside 'K2100/210', 'P3130/150'):
    the binding reads K2 + 90, K1 + 80, K2 + 80; no gap becomes a 1.80 or 2.90 m door; a 3-digit glued tag never sets a
    width alone."""
    from wenart.ingest import core_rules as CR
    from wenart.ingest import tag_binding as TBN
    from wenart.reading_check import crossdoc as XD
    b = _box_building(lid="L1", z=3.0, order=1)
    b["walls"].append(_wall("w_i", (3.0, 0.0), (3.0, 5.0), lid="L1"))

    def door(oid, wall, c, w):
        return {"id": oid, "level_id": "L1", "type": "door", "wall_id": wall, "center": list(c), "width": w,
                "height": 2.1, "assumed": ["height"], "evidence": [{"file": "x"}]}
    b["openings"] = [door("d1", "w_i", (3.0, 1.0), 0.90), door("d2", "w_i", (3.0, 3.0), 0.80),
                     door("d3", "w_n", (1.5, 5.0), 0.80), _win("w1", "w_s", (1.5, 0.0), 1.30),
                     {"id": "o1", "level_id": "L1", "type": "opening", "wall_id": "w_s", "center": [4.5, 0.0],
                      "width": 0.25, "evidence": [{"file": "x"}]}]
    texts = [{"text": "K290/210", "x": 3.3, "y": 1.0, "layer": "POZ", "entity": "T1"},
             {"text": "K180/210", "x": 3.3, "y": 3.0, "layer": "POZ", "entity": "T2"},
             {"text": "K280/240", "x": 1.5, "y": 5.3, "layer": "POZ", "entity": "T3"},
             {"text": "P3130/150", "x": 1.5, "y": -0.3, "layer": "POZ", "entity": "T4"},
             {"text": "K180/210", "x": 4.5, "y": -0.3, "layer": "POZ", "entity": "T5"},
             {"text": "K2100/210", "x": 30.0, "y": 30.0, "layer": "POZ", "entity": "T6"}]
    recs = TBN.bind(b, {"L1": texts})
    ops = {o["id"]: o for o in b["openings"]}
    assert [ops[k]["width"] for k in ("d1", "d2", "d3", "w1", "o1")] == [0.9, 0.8, 0.8, 1.3, 0.25]
    assert ops["d1"]["door_tags"] == ["K290/210"] and ops["d2"]["door_tags"] == ["K180/210"]
    assert ops["d3"]["door_tags"] == ["K280/240"] and ops["d3"]["height"] == 2.4
    assert ops["w1"]["height"] == 1.5 and ops["o1"]["type"] == "opening"
    assert sum(1 for r in recs if r.get("finding")) == 1                        # o1: 'read gap kept', nothing else
    # without the drawing's 4-digit proof the glued tag reads both ways and the opening's width chooses
    b2 = _box_building(lid="L1", z=3.0, order=1)
    b2["walls"].append(_wall("w_i", (3.0, 0.0), (3.0, 5.0), lid="L1"))
    b2["openings"] = [door("d1", "w_i", (3.0, 1.0), 0.90)]
    TBN.bind(b2, {"L1": texts[:1]})
    assert b2["openings"][0]["width"] == 0.9 and b2["openings"][0]["door_tags"] == ["K290/210"]
    # own_door_tags and RC11 accept either reading
    b3 = {"openings": [door("d9", "w_i", (3.0, 1.0), 0.90)]}
    assert CR.own_door_tags(b3, {"L1": texts[:1]})[0]["opening"] == "d9"
    tags = XD.size_tags([dict(texts[0], x=3.3, y=1.0)])
    walls = [{"id": "w_i", "start": [3.0, 0.0], "end": [3.0, 5.0], "thickness": 0.2}]
    assert XD.rc11("L1", tags, walls, [dict(b3["openings"][0])]) == []


def test_fixup_tags1_the_reader_makes_no_wide_door_of_a_glued_tag_by_a_narrow_or_a_wide_gap():
    """TAGS-1 / GENERAL-2: real14's 'K180/210' by a 0.25 m and a 1.55 m gap gave 1.80 m doors (33 of them): a
    glued tag the page does not decide takes a gap only when a reading agrees with it."""
    from wenart.ingest.generic import core as GC
    ops = [_op("opening", 1.0, 0.25), _op("opening", 4.0, 1.55)]
    texts = [_trun("K180/210", 1.0, 0.3, "POZ", "t1"), _trun("K180/210", 4.0, 0.3, "POZ", "t2")]
    out = GC._door_tags(_ex(), "L1", [], ops, texts, 1.0)
    assert out is None or all(o.kind != "door" or o.width < 1.0 for o in out)
    # a 0.80 m gap takes the K1 + 80 reading
    out = GC._door_tags(_ex(), "L1", [], [_op("opening", 1.0, 0.80)], [_trun("K180/210", 1.0, 0.3, "POZ", "t1")], 1.0)
    assert out is not None and out[0].kind == "door" and abs(out[0].width - 0.8) < 1e-9


def test_fixup_general2_a_door_coded_tag_on_a_text_layer_never_turns_a_drawn_window_into_a_door():
    """GENERAL-2 (the swiss-b1128 bench fall: 'K:85/210' on the text layer '03_Yazı' made the drawn 0.80 m window
    beside its door a door): off a door layer the code decides the kind, not the layer's authority."""
    from wenart.ingest.generic import core as GC
    win = _op("window", 1.0, 0.80, evidence={"method": "vector", "layer": "PENCERE"})
    out = GC._door_tags(_ex(), "L0", [], [win], [_trun("K:85/210", 1.3, 0.3, "03_Yazı", "t1")], 1.0)
    assert out is None or out[0].kind == "window"
    # on a door layer the door-high tag may still take a window of about its width (real16's shower doors)
    out = GC._door_tags(_ex(), "L0", [], [win], [_trun("85/210", 1.3, 0.3, "KAPI", "t1")], 1.0)
    assert out is not None and out[0].kind == "door"


def test_fixup_tags3_a_door_read_narrower_than_its_tag_keeps_it_against_a_window_of_the_tags_width():
    """TAGS-3: the nearest opening first; the width only breaks a near tie; a drawn window stays a window."""
    from wenart.ingest import tag_binding as TBN
    b = _box_building(lid="L1", z=3.0, order=1)
    b["site"]["outdoor_spaces"] = [{"id": "os_b", "level_id": "L1", "kind": "balcony",
                                   "polygon": [[0, -1.5], [6, -1.5], [6, -0.1], [0, -0.1]]}]
    d = {"id": "d_balk", "level_id": "L1", "type": "door", "wall_id": "w_s", "center": [2.0, 0.0], "width": 0.72,
         "height": 2.1, "assumed": ["height"], "evidence": [{"file": "x"}]}
    w = dict(_win("w_kit", "w_s", (3.05, 0.0), 0.90), evidence=[{"file": "x", "layer": "PENCERE",
                                                                   "entity": "INSERT:PENC", "method": "vector"}])
    b["openings"] = [d, w]
    TBN.bind(b, {"L1": [{"text": "K1 90/210", "x": 2.0, "y": -0.3, "entity": "T1", "layer": "yazi"}]})
    assert w["type"] == "window" and "size_tag" not in w
    assert d.get("size_tag", {}).get("text") == "K1 90/210"


def test_fixup_tags4_a_second_leaf_never_widens_a_door_across_a_wall_that_meets_its_wall():
    from wenart.ingest import tag_binding as TBN
    b = _box_building(lid="L0", z=0.0, order=0)
    b["walls"].append(_wall("w_p", (3.0, 0.0), (3.0, 3.0), lid="L0"))                   # a partition meeting w_s at 3.0
    d = {"id": "d1", "level_id": "L0", "type": "door", "wall_id": "w_s", "center": [2.35, 0.0], "width": 0.8,
         "height": 2.1, "operation": "swing", "evidence": [{"file": "x", "method": "vector"}]}
    b["openings"] = [d]
    b["symbols"] = [{"id": "sy_bath", "kind": "door_arc", "level_id": "L0",
                     "footprint": {"center": [3.1, 0.3], "size": [0.6, 0.1]}, "evidence": [{"entity": "ARC:A2"}]}]
    TBN.bind(b, {"L0": [{"text": "150/210", "x": 2.35, "y": 0.3, "entity": "T1", "layer": "kapi"}]})
    assert d["width"] == 0.8 and d.get("operation") == "swing"


def test_fixup_tags5_one_tag_one_product_never_makes_an_upper_french_window_a_door_into_the_air():
    """TAGS-5 / GENERAL-6: on an upper storey the window onto the balcony becomes a door, the one over the drop stays a
    French window; the copied operation names its source (TAGS-8)."""
    from wenart.ingest import tag_binding as TBN
    b = _box_building(lid="L2", z=6.0, order=2)
    b["site"]["outdoor_spaces"] = [{"id": "os_b", "level_id": "L2", "kind": "balcony",
                                   "polygon": [[0, -1.5], [6, -1.5], [6, -0.1], [0, -0.1]]}]
    b["openings"] = [_win("w_balc", "w_s", (3.0, 0.0), 2.6, "L2"), _win("w_east", "w_e", (6.0, 2.5), 2.6, "L2")]
    texts = [{"text": "CK3 260/240", "x": 3.0, "y": -0.3, "entity": "T1", "layer": "pencere"},
             {"text": "CK3 260/240", "x": 6.3, "y": 2.5, "entity": "T2", "layer": "pencere"}]
    TBN.bind(b, {"L2": texts})
    ops = {o["id"]: o for o in b["openings"]}
    assert ops["w_balc"]["type"] == "door" and ops["w_east"]["type"] == "window"
    assert ops["w_east"]["french_window"] and ops["w_east"]["sill_height"] == 0.0
    assert ops["w_balc"]["operation_source"] in ("assumed", "size_tag")
    if ops["w_balc"]["operation_source"] == "size_tag":
        assert ops["w_balc"].get("operation") in ("sliding", "folding")


def test_fixup_tags6_and_7_a_window_tag_on_a_gap_is_a_window_at_its_sill_and_the_head_rule_sets_the_sill():
    from wenart.ingest import tag_binding as TBN
    b = _box_building()
    b["openings"] = [{"id": "o1", "level_id": "L1", "type": "opening", "wall_id": "w_s", "center": [2.0, 0.0],
                      "width": 1.18, "evidence": [{"file": "x"}]}, _win("w2", "w_n", (3.0, 5.0), 1.5)]
    TBN.bind(b, {"L1": [{"text": "P1 120/150", "x": 2.0, "y": -0.3, "entity": "T1", "layer": "yazi"},
                        {"text": "150/150", "x": 3.0, "y": 5.3, "entity": "T2", "layer": "yazi"}]})
    ops = {o["id"]: o for o in b["openings"]}
    assert ops["o1"]["type"] == "window" and abs(ops["o1"]["sill_height"] - 0.7) < 1e-9 and ops["o1"]["height"] == 1.5
    assert ops["o1"]["drawn_type"] == "opening" and ops["o1"]["adjusted_by_ai"]["rule"] == "size_tag_gap_window"
    assert abs(ops["w2"]["sill_height"] - 0.7) < 1e-9 and "sill_height" not in ops["w2"]["assumed"]   # head at 2.20


def test_fixup_general11_pieces_merge_only_along_one_wall_run_and_stay_inside_it():
    """GENERAL-11: pieces on walls that are not one run (a gap between them, another line) are never one window; on
    a run of collinear walls joined end to end they are, seated on the run's wall that holds the middle."""
    from wenart.ingest import tag_binding as TBN
    from wenart.ingest import tag_grammar as TG
    walls = {"w_a": _wall("w_a", (0, 0), (2.6, 0)), "w_b": _wall("w_b", (2.7, 0), (6, 0))}      # 0.10 m apart
    ops = [_win("o1", "w_a", (2.2, 0.0), 0.8), _win("o2", "w_b", (3.1, 0.0), 0.8)]
    assert TBN.merge_pieces(ops, walls, TG.parse("170/150"), (2.65, -0.3)) is None
    walls = {"w_a": _wall("w_a", (0, 0), (2.6, 0)), "w_b": _wall("w_b", (2.6, 0), (6, 0))}
    ops = [_win("o1", "w_a", (2.2, 0.0), 0.8), _win("o2", "w_b", (3.05, 0.0), 0.8)]
    got = TBN.merge_pieces(ops, walls, TG.parse("165/150"), (2.6, -0.3))
    assert got is not None and got[1] == [ops[1]]
    b = {"walls": [dict(w, level_id="L1") for w in walls.values()], "openings": list(ops)}
    TBN._merge(b, got[0], got[1], walls["w_a"], TG.parse("165/150"), "test")
    assert b["openings"][0]["wall_id"] == "w_b" and abs(b["openings"][0]["width"] - 1.65) < 1e-6
    walls = {"w_a": _wall("w_a", (0, 0), (2.6, 0)), "w_c": _wall("w_c", (2.6, 0.31), (6, 0.31))}   # another line
    ops = [_win("o1", "w_a", (2.2, 0.0), 0.8), _win("o2", "w_c", (3.05, 0.31), 0.8)]
    assert TBN.merge_pieces(ops, walls, TG.parse("165/150"), (2.6, -0.3)) is None


def test_fixup_r08_steps_in_front_of_the_gap_count_garden_steps_beside_it_and_flush_or_walled_marks_do_not():
    """ENTRANCES-1 / -7 / GENERAL-3: a mark counts in front of the gap, at least a step under the floor, with no wall
    between; steps count when their run overlaps the band in front of the gap (the gap faces east at x 8.5)."""
    from shapely.geometry import box as sbox
    from wenart.ingest import porches as PCH

    def labelled(marks=True):
        b = _porch_building()
        b["rooms"][1]["label_raw"] = "SALON"            # a labelled room behind: an entrance door, never a porch
        if not marks:
            b["level_marks"] = []
        return b, b["openings"][0]
    b, gap = labelled(False)
    assert PCH.open_porches(b, {"L0": [{"polygon": sbox(8.8, 12.6, 10.0, 13.6)}]}) == []     # garden steps beside
    b, gap = labelled(False)
    got = PCH.open_porches(b, {"L0": [{"polygon": sbox(8.8, 9.9, 10.2, 10.7)}]})
    assert got and got[0].get("door") == gap["id"] and gap["type"] == "door"
    b, gap = labelled()
    b["level_marks"][0]["z"] = 0.45                      # 5 cm under the floor: flush, no step
    assert PCH.open_porches(b, {}) == []
    b, gap = labelled()
    b["walls"].append(_wall("w_par", (9.0, 8.0), (9.0, 12.0), lid="L0"))    # a parapet between the gap and the mark
    assert PCH.open_porches(b, {}) == []
    b, gap = labelled()
    b["level_marks"][0]["point"] = [9.5, 13.5]          # 3.2 m along the facade: not in front of the gap
    assert PCH.open_porches(b, {}) == []


def test_fixup_r08_a_wc_or_a_furnished_recess_is_never_a_porch_and_a_drawn_main_entrance_is_kept():
    """ENTRANCES-2: a typed WC, a room with fixtures, or a copied label are no porch (a WC gets no entrance door
    either); a porch's door never takes the main entrance from a drawn door."""
    from wenart.ingest import porches as PCH
    b = _porch_building()
    b["rooms"][1]["room_type"] = "wc"
    assert PCH.open_porches(b, {}) == []
    b = _porch_building()
    b["furniture"] = [{"id": "f1", "type": "toilet", "room_id": "r_oda", "source": "from_documents"}]
    assert not any(r.get("porch") for r in PCH.open_porches(b, {}))
    b = _porch_building()
    b["rooms"][1]["label_inferred"] = {"method": "mirror", "of": "r_x"}
    assert not any(r.get("porch") for r in PCH.open_porches(b, {}))
    b = _porch_building()
    b["openings"].append({"id": "d_front", "level_id": "L0", "type": "door", "wall_id": "w_w", "center": [3.0, 10.0],
                          "width": 1.0, "height": 2.1, "entrance_of": "building",
                          "entrance_word": {"text": "BİNA GİRİŞİ"},
                          "evidence": [{"file": "x", "method": "vector", "entity": "ARC:7,LINE:8"}]})
    b["site"]["entrances"] = [{"door_id": "d_front", "level_id": "L0", "room_id": "r_antre", "main": True,
                               "width": 1.0, "outward": [-1.0, 0.0]}]
    recs = PCH.open_porches(b, {})
    assert any(r.get("porch") for r in recs)
    main = [e["door_id"] for e in b["site"]["entrances"] if e.get("main")]
    assert main == ["d_front"]                                   # the main entrance the documents name stays
    assert b["rooms"][1]["label_role"] is True                                  # ROOMS-3: a role name


def test_fixup_r08_a_corner_porch_with_two_mouths_is_one_porch_whatever_the_order():
    """ENTRANCES-10: the evidence of every gap first, then each room decides once."""
    from wenart.ingest import porches as PCH
    for order in (0, 1):
        b = _porch_building()
        south = {"id": "o_south", "level_id": "L0", "type": "opening", "drawn_type": "opening", "wall_id": "w_ps",
                 "center": [7.8, 9.25], "width": 0.9, "evidence": [{"file": "x"}]}
        walls = {w["id"]: w for w in b["walls"]}
        walls["w_s"]["end"] = [7.125, 7.9]                 # the corner south of the recess is outside
        walls["w_e"]["start"] = [8.5, 9.25]
        b["level_marks"].append({"id": "lm_s", "level_id": "L0", "kind": "ground_finished", "z": 0.0, "raw": "±0,00",
                                 "point": [7.8, 8.4]})
        b["openings"] = ([south] + b["openings"]) if order else (b["openings"] + [south])
        PCH.open_porches(b, {})
        ops = {o["id"]: o for o in b["openings"]}
        assert b["rooms"][1]["room_type"] == "porch", order
        assert ops["o_gap"]["type"] == "opening" and ops["o_south"]["type"] == "opening", order


def test_fixup_r08_an_upper_storey_of_a_hillside_house_gets_no_porch():
    """ENTRANCES-8: open entrances only on the entrance level."""
    from wenart.ingest import porches as PCH
    b = _porch_building()
    for lv in b["levels"]:
        lv["order"] = 1
    b["levels"].insert(0, {"id": "Lm1", "elevation": -2.6, "order": 0})
    b["site"].setdefault("ground", {})["levels"] = [{"z": {"value": -2.6}}, {"z": {"value": 0.0}}]
    assert PCH.entrance_levels(b) == {"Lm1"}
    assert PCH.open_porches(b, {}) == []


def test_fixup_r08_vehicle_service_and_garden_words_never_name_the_main_entrance_a_plain_giris_does():
    """ENTRANCES-4 / GENERAL-9: 'OTOPARK / ARAÇ / SERVİS / BAHÇE GİRİŞİ' are secondary entrances; a garage door is
    never main (C0045); a bare 'GİRİŞ' names the main entrance."""
    from wenart.ingest import porches as PCH
    for word, main in (("OTOPARK GİRİŞİ", False), ("ARAÇ GİRİŞİ", False), ("SERVİS GİRİŞİ", False),
                       ("BAHÇE GİRİŞİ", False), ("GİRİŞ", True)):
        assert (PCH._word_kind(word) in ("building", "entrance")) is main, word
    b = _box_building(lid="L0", z=0.0, order=0)
    b["rooms"][0].update(room_type="garage", label="Garaj", label_raw="GARAJ")
    d1 = {"id": "d_gar", "level_id": "L0", "type": "door", "wall_id": "w_e", "center": [6.0, 3.0], "width": 2.5,
          "height": 2.2, "evidence": [{"file": "x"}]}
    b["openings"] = [d1]
    b["site"]["entrances"] = [{"door_id": "d_gar", "main": False, "level_id": "L0", "room_id": "r1",
                               "solution": "drive"}]
    recs = PCH.entrance_words(b, {"L0": [{"text": "GİRİŞ", "x": 7.3, "y": 3.05, "entity": "T1"}]})
    assert not b["site"]["entrances"][0].get("main") and recs[0].get("not_main")


def test_fixup_r18_a_kitchen_run_with_its_sink_is_a_kitchen_and_a_retype_clears_the_zone():
    """FIX-1 / FIX-2 / FIX-3 / FIX-4 / GENERAL-8: a counter run with a sink or hob is a kitchen (an unlabelled 'hall'
    by its doors too); a bedroom's lone counter becomes a wardrobe, its kitchen zone goes, the earlier label is merged,
    and other kitchen kit there is not built."""
    from wenart.ingest import fixed_context as FXC
    from wenart.ingest.generic import reading as RDG
    poly = [[0, 0], [4, 0], [4, 4], [0, 4]]

    def piece(pid, ftype, room, x, size=(2.4, 0.6), method="ai_two_pass", **kw):
        return dict({"id": pid, "type": ftype, "type_method": method, "source": "from_documents", "room_id": room,
                     "footprint": {"center": [x, 0.3], "size": list(size), "rotation_deg": 0}}, **kw)
    rooms = [{"id": "r_hall", "label": "Oda", "label_raw": None, "room_type": "hall", "polygon": poly},
             {"id": "r_hol", "label": "Hol", "label_raw": "HOL", "room_type": "hall",
              "polygon": [[10, 0], [14, 0], [14, 4], [10, 4]]},
             {"id": "r_bed", "label": "Yatak Odası", "label_raw": "YATAK ODASI", "room_type": "bedroom",
              "polygon": [[20, 0], [24, 0], [24, 4], [20, 4]],
              "zones": [{"zone_id": "r_bed_kitchen", "kind": "kitchen", "piece_ids": ["f_c3", "f_h3"],
                         "evidence": [{"rule": RDG.ZONE_RULE}]}]}]
    furn = [piece("f_c1", "kitchen_counter", "r_hall", 2.0), piece("f_s1", "sink_kitchen", "r_hall", 2.0, (0.6, 0.5)),
            piece("f_c2", "kitchen_counter", "r_hol", 12.0), piece("f_s2", "stove", "r_hol", 12.5, (0.6, 0.6),
                                                                   "block_name"),
            piece("f_c3", "kitchen_counter", "r_bed", 22.0, adjusted_by_ai={"by": "code", "rule": "product_size",
                                                                           "reason": "snapped"}),
            piece("f_h3", "hood", "r_bed", 23.0, (0.6, 0.5))]
    b = {"rooms": rooms, "furniture": furn}
    recs = FXC.kitchen_context(b)
    by = {f["id"]: f for f in furn}
    assert by["f_c1"]["type"] == "kitchen_counter" and by["f_c2"]["type"] == "kitchen_counter"
    assert by["f_c3"]["type"] == "wardrobe" and by["f_c3"]["type_method"] == "inferred"
    assert by["f_c3"]["adjusted_by_ai"]["rules"] == ["product_size", "kitchen_context"]
    assert any(e.get("rule") == "kitchen_context" for e in by["f_c3"]["evidence"])
    assert by["f_h3"]["build"] is False and by["f_h3"]["not_built_reason"]
    assert rooms[2]["zones"] == [] and any(r.get("zone") == "r_bed_kitchen" for r in recs)
    assert FXC.KITCHEN_WORD_RE.search("aksam mutfagi") and FXC.KITCHEN_WORD_RE.search("mutf.")


def test_fixup_wet_room_cluster_is_the_missing_shower_and_a_counter_in_a_bathroom_is_its_vanity():
    """The real10 'Duş' rooms L0-L6 (14 critical M7): one untyped 2.45 x 1.40 m arc cluster over the fixture wall, the
    toilet and the basin read on their own: the cluster is the shower the room misses, seated in the free part; a
    kitchen counter typed by the AI in a bathroom is the vanity (drawn_type kept)."""
    from wenart.furniture import infer as IF
    from wenart.ingest.generic import reading as RDG
    room = {"id": "r_dus", "level_id": "L0", "label": "Duş", "label_raw": "duş", "room_type": "bathroom",
            "polygon": [[7.55, 12.5], [10.1, 12.5], [10.1, 14.0], [7.55, 14.0]]}

    def piece(pid, ftype, c, size, method="ai_two_pass", **kw):
        return dict({"id": pid, "type": ftype, "type_method": method, "source": "from_documents", "room_id": "r_dus",
                     "level_id": "L0", "footprint": {"center": list(c), "size": list(size), "rotation_deg": 0.0},
                     "build": True}, **kw)
    cluster = piece("f_c", "unknown", (8.82, 13.24), (2.45, 1.40), "none", build=False,
                    not_built_reason="untyped (CLAUDE.md: no untyped piece is built)",
                    evidence=[{"entity": "ARC:1,ARC:2,LINE:3", "method": "vector"}])
    b = {"rooms": [room], "furniture": [piece("f_w", "washbasin", (9.63, 12.89), (0.75, 0.62)),
                                        piece("f_t", "toilet", (9.58, 13.61), (0.58, 0.36), front_deg=270.0),
                                        cluster], "openings": [], "walls": [], "levels": [{"id": "L0"}],
         "project": {}}
    props = IF.wet_cluster_members(b)
    assert [(p["piece_id"], p["type"]) for p in props] == [("f_c", "shower")]
    fp = props[0]["footprint"]
    assert fp["center"][0] < 9.0 and max(fp["size"]) <= 1.2               # seated in the part the fixtures leave
    out = IF.apply_inferences(b, props)
    c = next(f for f in out["furniture"] if f["id"] == "f_c")
    assert c["type"] == "shower" and c["build"] is not False and c["drawn_footprint"]["size"] == [2.45, 1.4]
    assert c["adjusted_by_ai"]["rule"] == IF.WET_CLUSTER_RULE

    class _B:
        building = {"rooms": [room], "furniture": [piece("f_k", "kitchen_counter", (9.6, 12.9), (0.7, 0.57))]}
        def warn(self, msg):
            pass
    bb = _B()
    assert RDG.wet_room_vanities(bb) == ["f_k"]
    k = bb.building["furniture"][0]
    assert (k["type"], k["drawn_type"]) == ("washbasin", "kitchen_counter")


def test_fixup_the_bath_role_is_placed_first_where_only_one_member_of_a_bathroom_set_fits():
    from wenart.furniture import solver as SV
    assert SV.SET_ANCHOR_ROLES["bathroom_set"] == "bath" and SV.SET_ANCHOR_WEIGHT > 1.0


def test_fixup_block1_a_counter_block_with_a_sink_word_stays_a_counter():
    from wenart.ingest.generic import symbols as SY
    assert SY.keyword_type("TEZGAH EVIYE") == SY.keyword_type("TEZGAH")
    assert SY.keyword_type("KLO-01") == "toilet"


def test_fixup_block2_derived_copies_are_no_votes_and_a_zone_label_counts_like_a_name():
    from wenart.furniture import infer as IF

    def piece(pid, t, m):
        return {"id": pid, "type": t, "type_method": m, "source": "from_documents", "block": "BLK_X",
                "footprint": {"center": [0, 0], "size": [0.6, 0.5], "rotation_deg": 0}, "evidence": []}
    pieces = [piece("a", "washbasin", "rule"), piece("b", "washbasin", "level"), piece("c", "washbasin", "twin"),
              piece("d", "sink_kitchen", "ai_two_pass"), piece("e", "unknown", None)]
    got = IF._same_block_type({"furniture": pieces}, pieces[4])
    assert got is None                        # one rule against one AI answer: the copies of 'a' are no votes
    pieces[3]["type_method"] = "zone_label"
    got = IF._same_block_type({"furniture": pieces}, pieces[4])
    assert got and got["type"] == "sink_kitchen"


def test_fixup_tub1_a_storeys_copy_of_a_size_typed_tub_is_typed_like_its_source():
    from wenart.furniture import infer as IF
    src = {"id": "t0", "type": "bathtub", "type_method": "inferred", "evidence": []}
    cp = {"id": "t1", "type": "bathtub", "type_method": "level", "evidence": [{"source_id": "t0"}]}
    b = {"furniture": [src, cp]}
    assert not IF.tub_drawn(cp, b)
    src["type_method"] = "ai_two_pass"
    assert IF.tub_drawn(cp, b) and IF.tub_drawn({"drain": True}) and IF.tub_drawn(
        {"evidence": [{"method": "vector", "entity": "LINE:1,CIRCLE:2"}]})


def test_fixup_r28_role_names_are_no_labels_for_every_consumer_and_keep_the_furnishing():
    """ROOMS-1 / -2 / -4 / -5: a bathroom open to a hall keeps its role name; plan-vs-model, the critic's and the
    architect's facts read no label; the score and the furniture program read the placeholder as before."""
    from wenart.furniture import program as PR
    from wenart.ingest import room_names as RN
    from wenart.reading_check import truth as TR
    rooms = [{"id": "r_hol", "level_id": "L1", "label": "Hol", "label_raw": "HOL", "room_type": "hall",
              "polygon": [[0, 0], [3, 0], [3, 3], [0, 3]]},
             {"id": "r_ba", "level_id": "L1", "label": "Oda", "label_raw": None, "room_type": "bathroom",
              "polygon": [[3, 0], [5, 0], [5, 3], [3, 3]]},
             {"id": "r_big", "level_id": "L1", "label": "Oda", "label_raw": None, "room_type": "other",
              "polygon": [[10, 0], [13, 0], [13, 3], [10, 3]]}]
    b = {"rooms": rooms, "openings": [{"id": "g", "level_id": "L1", "type": "opening", "center": [3.0, 1.5],
                                       "width": 0.9}], "furniture": []}
    RN.name_faces(b)
    assert rooms[1]["label"] == "Banyo" and rooms[1]["label_inferred"]["method"] == "role"      # never 'Hol'
    assert RN.label_of(rooms[2]) == "" and RN.reader_label(rooms[2]) == "Oda"
    assert TR._room(rooms[2], "read")["label"] == "Oda"
    assert PR.room_kind(b, rooms[2]) == "bedroom"                       # 9 m² 'Oda' as before R28 (ROOMS-4)
    assert not RN.DRESSING_RE.search("walk-in shower") and RN.DRESSING_RE.search("walk-in closet")
    assert not RN.DRESSING_RE.search("vestiyer")


def test_fixup_a_porch_is_open_air_in_every_consumer():
    from wenart.blender import render, shell
    from wenart.furniture import program as PR
    from wenart.reading_check import critic_checks as CC
    from wenart.reading_check import structure as ST
    assert render.open_air("porch") and "porch" in shell.OUTDOOR_ROOM_TYPES
    assert "porch" in CC.OPEN_AIR_TYPES and "porch" in ST.OPEN_AIR_TYPES
    room = {"id": "r_p", "level_id": "L0", "label": "Giriş", "label_role": True, "room_type": "porch",
            "polygon": [[0, 0], [2, 0], [2, 1.5], [0, 1.5]]}
    prog = PR.room_program({"rooms": [room], "furniture": [], "openings": []}, "r_p")
    assert not prog["groups"] and "porch" in prog["reason"]


def test_fixup_queue_a_door_word_between_two_jambs_opens_the_cut_span():
    """Weak test 25: the door word's branch of ``doors_in_cut_spans`` (a door between jamb lines across the wall)."""
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import WallItem
    wall = WallItem(start=(0.0, 0.0), end=(6.0, 0.0), thickness=0.2, box=[0, -0.1, 6, 0.1], entity="w", evidence={})
    jambs = [Stroke(id="j1", kind="line", layer="DUVAR", pts=[(2.0, -0.1), (2.0, 0.1)]),
             Stroke(id="j2", kind="line", layer="DUVAR", pts=[(2.8, -0.1), (2.8, 0.1)])]
    out = GC.doors_in_cut_spans([wall], [], jambs, [_trun("SÜRGÜ KAPI", 2.4, 0.35, "YAZI", "t1")], 1.0)
    assert out is not None and len(out) == 1 and abs(out[0].width - 0.8) < 1e-6 and out[0].kind == "door"


def test_fixup_queue_schedule_texts_get_the_schedule_role_from_their_layout():
    """Weak test 22: the texts of a room schedule the reading found keep the role ``schedule`` in the inventory, without
    the real15 reading."""
    from types import SimpleNamespace as NS
    from wenart.ingest import source_items as SI

    def run(tid, text):
        return NS(text=text, entity=tid, evidence={"layer": "Z_yazı"}, box=[0, 0, 1, 0.2], start=(0, 0), height=0.2,
                  rotation_deg=0.0, role="label")
    ex = NS(report={"schedules": [{"run_ids": ["T1", "T2"]}]}, texts=[run("T1", "SALON"), run("T2", "O. ODASI"),
                                                                      run("T3", "MUTFAK")], labels=[])
    rows = {r["id"]: r["role"] for r in SI.text_rows(ex, "p1", None)}
    assert rows == {"T1": "schedule", "T2": "schedule", "T3": "label"}


def test_fixup_r16_only_a_drawn_door_that_lands_on_no_other_drawn_space_keeps_an_upper_rectangle():
    """real15's L1 'TERAS' rectangle: its gap o_L1_006 is the drawn balcony's (ENTRANCES-5 narrowed: a gap or another
    space's door is no landing door of the rectangle)."""
    from wenart.ingest import outdoor_checks as OC
    rect = [[0.0, -6.0], [10.0, -6.0], [10.0, -0.1], [0.0, -0.1]]
    b = {"openings": [{"id": "g1", "level_id": "L1", "type": "opening", "center": [2.0, 0.0], "width": 0.9},
                      {"id": "d2", "level_id": "L1", "type": "door", "center": [5.0, 0.0], "width": 0.9},
                      {"id": "d3", "level_id": "L1", "type": "door", "center": [8.0, 0.0], "width": 0.9}]}
    other = {"id": "sa_b", "level_id": "L1", "label": "BALKON",
             "outline_inferred": {"polygon": [[4.0, -1.2], [6.0, -1.2], [6.0, -0.1], [4.0, -0.1]]}}
    area = {"id": "sa_t", "level_id": "L1", "label": "TERAS"}
    assert OC.landing_doors(b, area, "L1", rect, ["g1"], [area, other]) == ["d3"]


def test_fixup_r09_a_drawn_garage_bay_at_grade_is_its_door_a_drawn_living_room_window_stays_a_window():
    """R09 decision with the room's use: real15's two garage bay windows (window layer) merged by 'CK3 350/220' are the
    garage's vehicle door (a car passes it); the same tag on a drawn living-room window at grade leaves it a window."""
    from wenart.ingest import tag_binding as TBN
    win_ev = [{"file": "x", "layer": "PENCERE", "method": "vector", "entity": "LINE:1,LINE:2"}]
    for room_type, label, want in (("garage", "GARAJ", "door"), ("living", "SALON", "window")):
        b = _box_building(lid="L0", z=0.0, order=0)
        b["rooms"][0].update(label=label, label_raw=label, room_type=room_type)
        b["openings"] = [dict(_win("w4", "w_s", (1.3, 0.0), 1.62, "L0"), evidence=win_ev),
                         dict(_win("w5", "w_s", (3.05, 0.0), 1.70, "L0"), evidence=win_ev)]
        TBN.bind(b, {"L0": [{"text": "CK3 350/220", "x": 2.2, "y": -0.4, "entity": "T2", "layer": "pencere"}]})
        assert len(b["openings"]) == 1 and b["openings"][0]["type"] == want, room_type
