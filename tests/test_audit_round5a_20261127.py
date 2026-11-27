"""Audit fix round 5a (27 Nov 2026): R09 one size-tag grammar and its binding step, R08 entrances from drawn evidence,
R16 outdoor-space checks, R28 room names, R21 block typing, R18 fixed equipment in its room's context, and the check
pod's queue (the schedule words Argus counted as rooms, real15's balconies with no door, real17's shower doors).
Synthetic buildings, texts and blocks built in code; real06, real15 and real17 are read once each (skipped without a
DWG converter)."""
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
    assert TG.parse("K290/210").w_cm == 290                       # never K2 + 90/210
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


def test_r16_a_rectangle_far_off_its_stated_area_is_a_finding_not_a_space():
    from wenart.ingest import outdoor_checks as OC
    why = OC.refuse({"anchor": [5.5, 10.4]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner",
                    [[5.05, 9.35], [6.3, 9.35], [6.3, 11.0], [5.05, 11.0]], 3.78, ["d1"], [], [])
    assert why and "stated 3.78" in why
    assert OC.refuse({"anchor": [5.5, 10.4]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner",
                     [[5.0, 8.3], [6.4, 8.3], [6.4, 11.0], [5.0, 11.0]], 3.78, ["d1"], [], []) is None


def test_r16_an_upper_label_with_the_lower_floor_mark_is_the_lower_space_seen_from_above():
    from wenart.ingest import outdoor_checks as OC
    from wenart.levels import outdoor as OD
    area = {"anchor": [2.08, 12.89], "label": "TERAS"}
    marks = [{"id": "lm_022", "level_id": "L1", "z": 0.0, "raw": "+0.50", "point": [2.25, 12.61]}]
    poly = [[-5.5, 5.0], [9.7, 5.0], [9.7, 20.7], [-5.5, 20.7]]
    why = OC.refuse(area, "terrace", "L1", _levels(), "L0", "rectangle in the inner corner", poly, None, ["d1"],
                    [], marks, OD.space_kind)
    assert why and "seen from above" in why
    # no mark, no door, a same-kind space under it: seen from above too
    lower = {"anchor": [2.07, 12.9], "label": "TERAS", "level_id": "L0"}
    why = OC.refuse(area, "terrace", "L1", _levels(), "L0", "rectangle in the inner corner", poly, None, [],
                    [lower, area], [], OD.space_kind)
    assert why and "seen from above" in why
    # a drawn upper balcony with no door is kept (its door may still be misread)
    assert OC.refuse(area, "balcony", "L1", _levels(), "L0", "strokes", poly, None, [], [], [], OD.space_kind) is None


def test_r16_a_door_beside_an_inferred_balcony_reaches_it_even_when_the_landing_probe_missed():
    from wenart.ingest import outdoor_checks as OC
    poly = [[0.0, -1.4], [3.0, -1.4], [3.0, -0.1], [0.0, -0.1]]
    b = {"openings": [{"id": "d1", "level_id": "L1", "type": "door", "center": [1.5, 0.3], "width": 0.9},
                       {"id": "w1", "level_id": "L1", "type": "window", "center": [2.5, 0.0], "width": 1.2}]}
    assert OC.doors_near(b, "L1", poly) == ["d1"]
    assert OC.refuse({"anchor": [1.5, -0.7]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner", poly,
                     None, OC.doors_near(b, "L1", poly), [], []) is None
    b["openings"].pop(0)
    assert OC.refuse({"anchor": [1.5, -0.7]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner", poly,
                     None, OC.doors_near(b, "L1", poly), [], [])


def test_r16_at_the_end_of_the_reading_an_inferred_upper_space_no_door_reaches_is_a_finding_not_a_space():
    from wenart.ingest import outdoor_checks as OC
    rect = [[0.0, -1.4], [3.0, -1.4], [3.0, -0.1], [0.0, -0.1]]
    far = [[10.0, -1.4], [13.0, -1.4], [13.0, -0.1], [10.0, -0.1]]
    b = {"levels": [{"id": "L0", "elevation": 0.0, "order": 0}, {"id": "L1", "elevation": 3.0, "order": 1}],
         "openings": [{"id": "d1", "level_id": "L1", "type": "door", "center": [1.5, 0.0], "width": 0.9}],
         "site": {"areas": [{"id": "sa1", "label": "BALKON", "anchor": [1.5, -0.7], "space": {"built": True, "id": "os1"}},
                           {"id": "sa2", "label": "BALKON", "anchor": [11.5, -0.7], "space": {"built": True, "id": "os2"}}],
                  "outdoor_spaces": [{"id": "os1", "level_id": "L1", "kind": "balcony", "label": "BALKON",
                                       "method": "rectangle in the inner corner", "polygon": rect, "doors": []},
                                      {"id": "os2", "level_id": "L1", "kind": "balcony", "label": "BALKON",
                                       "method": "rectangle in the inner corner", "polygon": far, "doors": []}]}}
    got = OC.unreached(b)
    assert [s["id"] for s in b["site"]["outdoor_spaces"]] == ["os1"] and [r["space"] for r in got] == ["os2"]
    assert b["site"]["areas"][1]["space"]["built"] is False and b["site"]["outdoor_spaces_refused"][0]["id"] == "os2"
    # while the doors are not all read (the levels model), no door decides nothing
    assert OC.refuse({"anchor": [11.5, -0.7]}, "balcony", "L1", _levels(), "L0", "rectangle in the inner corner", far,
                     None, None, [], []) is None


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


def test_r21_a_small_walled_face_with_a_water_heater_is_a_wet_cell_never_storage():
    from shapely.geometry import box
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.model import OpeningItem, WallItem
    def wall(a, b):
        return WallItem(start=a, end=b, thickness=0.1, box=[0, 0, 0, 0], entity="w", evidence={})
    walls = [wall((0, 0), (1.4, 0)), wall((1.4, 0), (1.4, 1.3)), wall((1.4, 1.3), (0, 1.3)), wall((0, 1.3), (0, 0))]
    door = OpeningItem(kind="door", width=0.7, center=(0.7, 0.0), rotation_deg=0.0, box=[0.35, -0.05, 1.05, 0.05],
                       entity="d", evidence={})
    face = box(0.05, 0.05, 1.35, 1.25)
    rtype, why = TP.unlabelled_face_type(face, walls, [door], texts=[("E.ŞOFBEN", (0.7, 0.9))])
    assert rtype == "bathroom" and why.startswith("wet cell") and TP.wet_cell_label(why, True) == "Duş"
    rtype, why = TP.unlabelled_face_type(face, walls, [door], texts=[])
    assert rtype == "storage"


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
    b, items = reading("real15")
    spaces = {s["id"]: s for s in b["site"]["outdoor_spaces"]}
    for sid in ("os_L1_balkon_2", "os_L1_balkon_4", "os_L1_balkon_5"):
        assert spaces[sid]["doors"], sid
    ops = {o["id"]: o for o in b["openings"]}
    for sid in ("os_L1_balkon_4", "os_L1_balkon_5"):
        d = ops[spaces[sid]["doors"][0]]
        assert d["type"] == "door" and d.get("sill_height") is None and d["door_tags"] == ["CK3 260/240"]
    assert not any(s["level_id"] == "L1" and s.get("kind") == "terrace" for s in spaces.values())
    teras = next(a for a in b["site"]["areas"] if a.get("level_id") == "L1" and a.get("label") == "TERAS")
    assert teras["space"]["built"] is False and "seen from above" in teras["space"]["reason"]
    assert b["status"] == "ok" or not any(w.startswith("schema") for w in b["warnings"])
    sched = [t for t in items["texts"] if t["text"] in ("SALON", "O. ODASI") and t["pos"][0] > 21]
    assert sched and all(t["role"] == "schedule" for t in sched)


def test_real17_french_windows_and_the_building_entrance(reading):
    b, _items = reading("real17")
    fr = [o for o in b["openings"] if o["level_id"] == "L1" and o.get("type") == "window"
          and abs(float(o["center"][0]) - 5.29) < 0.1 and float(o["width"]) > 1.7]
    assert len(fr) == 2 and all(o["sill_height"] == 0.0 and abs(o["height"] - 2.1) < 1e-6 for o in fr)
    main = [e["door_id"] for e in b["site"]["entrances"] if e.get("main")]
    assert main == ["d_L0_001"]
    d = next(o for o in b["openings"] if o["id"] == "d_L0_001")
    assert d["entrance_word"]["text"].upper().startswith("B") and abs(float(d["width"]) - 1.5) < 1e-6


def test_real06_the_east_porch_is_open_and_its_door_the_main_entrance(reading):
    b, _items = reading("real06")
    porch = next(r for r in b["rooms"] if r["level_id"] == "L0" and r.get("room_type") == "porch")
    mouth = next(o for o in b["openings"] if (o.get("type_inferred") or {}).get("method") == "open_porch")
    assert mouth["type"] == "opening" and porch["label"] == "Giriş"
    main = next(e for e in b["site"]["entrances"] if e.get("main"))
    door = next(o for o in b["openings"] if o["id"] == main["door_id"])
    assert door["door_tags"] == ["K3-100/210"] and abs(float(door["width"]) - 1.0) < 1e-6
    assert not any(r.get("label") == "Oda" and not r.get("label_raw") for r in b["rooms"])
