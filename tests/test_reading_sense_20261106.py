"""6 Nov 2026 (Milestone 14 R6, RC14): the architectural-sense checks of a reading.

What: one hit and one clean case per rule on hand-made building dicts; the four known errors of the current readings
on small fixtures shaped like them (a 16 m2 lift; a fire-lobby label in a 99 m2 face with a car park label; frame
walls on a region box with a paper room; a level with 8 labels and 3 walls); the trust file lowering a rule; the wiring
into ``wenart.reading_check.check`` as advisory findings. Round 2 (6 Nov 2026): the float edge of a door's reach, the
untyped hall of two flats, and one hit and one clean case for each rule made from the user's past corrections
(facade_recess, false_stair, stair_stacking, mirror_twins, wall_across_passage, wall_mass).
Why: the user (4 Nov 2026): "some AI or something else to give the feedbacks by itself instead of me at some point";
these are the faults an architect sees at a glance.
"""
from __future__ import annotations

import json

import pytest

from wenart import reading_check as RC
from wenart.reading_check import sense as SN

NO_TRUST = {"threshold": 0.7, "rules": {r: {"findings": 10, "judged_right": 10, "precision": 1.0, "trusted": True}
                                        for r in SN.RULES}}


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level="L0", **kw):
    from shapely.geometry import Polygon
    return dict({"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
                 "area_computed": round(Polygon(poly).area, 3)}, **kw)


def wall(wid, a, b, level="L0", t=0.2, exterior=False):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def box_walls(x0, y0, x1, y1, level="L0", prefix="w"):
    return [wall(f"{prefix}1", (x0, y0), (x1, y0), level, exterior=True),
            wall(f"{prefix}2", (x1, y0), (x1, y1), level, exterior=True),
            wall(f"{prefix}3", (x1, y1), (x0, y1), level, exterior=True),
            wall(f"{prefix}4", (x0, y1), (x0, y0), level, exterior=True)]


def building(rooms=(), walls=(), openings=(), levels=None, furniture=(), documents=()):
    return {"levels": levels or [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0}],
            "rooms": list(rooms), "walls": list(walls), "openings": list(openings), "furniture": list(furniture),
            "documents": list(documents), "site": {}}


def rules_of(found, rule):
    return [f for f in found if f["rule"] == rule]


# ---------------------------------------------------------------------------------------------- 1. room type, area
def test_a_12_m2_lift_is_a_finding_and_a_lift_car_is_clean():
    b = building(rooms=[room("r_lift", "Asansör", "shaft", rect(0, 0, 3.0, 4.0)),             # 12 m2
                        room("r_lift2", "Asansör", "shaft", rect(10, 0, 11.8, 2.0)),         # 3.6 m2
                        room("r_void", "Galeri Boşluğu", "shaft", rect(20, 0, 30, 5))])      # a void: no range
    f = rules_of(SN.room_type_area(b), "room_type_area")
    assert [x["element_ids"] for x in f] == [["r_lift"]]
    assert f[0]["severity"] == "minor" and f[0]["sense_type"] == "lift"
    assert "'Asansör'" in f[0]["message"] and "12.0 m2" in f[0]["message"] and "8.00 m2" in f[0]["message"]
    assert f[0]["check"] == "RC14" and f[0]["advisory"] is True and len(f[0]["place"]) == 2


def test_the_16_m2_lift_with_a_stair_in_its_face_is_a_major_finding():
    # real20 L0: 'Asansör' closed as a 16.2 m2 face with the stair standing in it
    b = building(rooms=[room("r_lift", "Asansör", "shaft", rect(0, 0, 4.03, 4.03))],
                 furniture=[{"id": "f1", "level_id": "L0", "type": "stair",
                             "footprint": {"center": [2.5, 2.0], "size": [2.5, 2.3]}}])
    found = [f for f in SN.run(b, {}, trust=NO_TRUST) if "r_lift" in f["element_ids"]]
    sizes = [f for f in found if f["rule"] in ("room_type_area", "label_names_larger_face")]
    assert len(sizes) == 1 and sizes[0]["severity"] == "major"
    assert "16.2 m2" in sizes[0]["message"] and "the stair f1" in sizes[0]["message"]


def test_a_room_a_little_outside_its_range_is_minor():
    b = building(rooms=[room("r_bed", "Yatak Odası", "bedroom", rect(0, 0, 2.0, 2.2))])        # 4.4 m2 (min 6)
    f = SN.room_type_area(b)
    assert len(f) == 1 and f[0]["severity"] == "minor"


def test_sense_type_refines_the_schema_type_by_the_label():
    assert SN.sense_type({"label": "Yangın Holü", "room_type": "hall"}) == "fire_lobby"
    assert SN.sense_type({"label": "Asansör Makn.dairesi", "room_type": "shaft"}) == "technical"
    assert SN.sense_type({"label": "Işıklık", "room_type": "shaft"}) == "light_well"
    assert SN.sense_type({"label": "Duş", "room_type": "bathroom"}) == "shower"
    assert SN.sense_type({"label": "Banyo Wc", "room_type": "wc"}) == "bathroom"
    assert SN.sense_type({"label": "Sığınak", "room_type": "storage"}) is None
    assert SN.sense_type({"label": "Otopark", "room_type": "garage"}) == "car_park"
    assert SN.sense_type({"label": "Galeri", "room_type": "shaft"}) is None
    assert SN.sense_type({"label": "Room", "room_type": "unknown"}) is None


# ------------------------------------------------------------------------------- 2. a label naming a larger face
def test_a_fire_lobby_label_in_a_99_m2_face_with_a_car_park_label_is_named_with_both_labels():
    poly = rect(0, 0, 9.0, 11.04)                                                            # 99.4 m2 (real18 L-2)
    b = building(rooms=[room("r_fl", "Yangın Holü", "hall", poly, label_raw="YANGIN HOLÜ",
                             evidence=[{"entity": "TEXT:1", "text": "YANGIN"}, {"entity": "TEXT:2", "text": "HOLÜ"},
                                       {"entity": "TEXT:3", "text": "OTOPARK"}])])
    texts = {"L0": [{"text": "YANGIN", "x": 4.0, "y": 9.0, "entity": "TEXT:1"},
                    {"text": "HOLÜ", "x": 4.0, "y": 8.7, "entity": "TEXT:2"},
                    {"text": "OTOPARK", "x": 4.5, "y": 3.0, "entity": "TEXT:3"},
                    {"text": "OTO 2", "x": 2.0, "y": 1.0, "entity": "TEXT:4"}]}
    f = SN.label_names_larger_face(b, texts)
    assert len(f) == 1 and f[0]["severity"] == "major"
    assert "'Yangın Holü'" in f[0]["message"] and "'OTOPARK' (car park)" in f[0]["message"]
    assert "OTOPARK" in f[0]["other_labels"] and "YANGIN" not in f[0]["other_labels"]
    # the run reports the room once: rule 1 leaves a room rule 2 named
    found = SN.run(b, texts, trust=NO_TRUST)
    assert [x["rule"] for x in found if "r_fl" in x["element_ids"]
            and x["rule"] in ("room_type_area", "label_names_larger_face")] == ["label_names_larger_face"]


def test_a_fire_lobby_of_its_own_size_is_clean():
    b = building(rooms=[room("r_fl", "Yangın Holü", "hall", rect(0, 0, 3.0, 4.0))])
    assert SN.label_names_larger_face(b, {}) == []
    assert SN.room_type_area(b) == []


# ------------------------------------------------------------------------------------- 3. frame walls, paper rooms
def _framed(inner_margin):
    """A level read from a region box 22 x 21 m (drawing units cm); walls on the box edges or ``inner_margin`` inside
    them; one room filling what the walls enclose (real19 L3)."""
    tf = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0]
    doc = {"file": "p.dwg", "pages": [{"level_id": "L0", "region_box": [0, 0, 2200, 2100],
                                       "transform_to_building": tf}]}
    m = inner_margin + 0.1
    walls = box_walls(m, m, 22.0 - m, 21.0 - m) + [wall("w5", (5, 5), (12, 5)), wall("w6", (12, 5), (12, 9))]
    rooms = [room("r_normal", "Normal", "other", rect(m + 0.1, m + 0.1, 22.0 - m - 0.1, 21.0 - m - 0.1),
                  area_label=253.0)]
    return building(rooms=rooms, walls=walls, documents=[doc])


def test_the_sheet_frame_read_as_walls_and_a_paper_room_are_major():
    f = SN.frame_walls_and_paper_rooms(_framed(0.0))
    frame = [x for x in f if not x["element_ids"] or x["element_ids"][0].startswith("w")]
    paper = [x for x in f if x["element_ids"] == ["r_normal"]]
    assert len(frame) == 1 and sorted(frame[0]["element_ids"]) == ["w1", "w2", "w3", "w4"]
    assert frame[0]["frame_share"] >= 0.95 and frame[0]["severity"] == "major"
    assert len(paper) == 1 and paper[0]["severity"] == "major" and "253 m2" in paper[0]["message"]


def test_outer_walls_well_inside_the_region_box_are_clean():
    b = _framed(2.0)
    b["rooms"] = [room("r1", "Salon", "living", rect(2.2, 2.2, 12, 10))]
    assert SN.frame_walls_and_paper_rooms(b) == []


# ------------------------------------------------------------------------------------------------ 4. unread walls
def test_a_level_with_8_labels_and_3_walls_is_major():
    names = ["SALON", "MUTFAK", "BANYO", "YATAK ODASI", "ÇOCUK ODASI", "ANTRE", "WC", "BALKON"]
    places = [{"kind": "unplaced_label", "text": n, "at": [2.0 * i, 3.0]} for i, n in enumerate(names)]
    b = building(walls=[wall("w1", (0, 0), (5, 0)), wall("w2", (5, 0), (5, 4)), wall("w3", (0, 4), (5, 4))],
                 levels=[{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "reading_places": places}])
    f = SN.unread_walls(b)
    assert len(f) == 1 and f[0]["severity"] == "major"
    assert f[0]["labels"] == 8 and f[0]["walls"] == 3 and "3 walls for 8 room labels" in f[0]["message"]
    # from the drawing's texts too: a name on two lines is one label
    texts = {"L0": [{"text": n, "x": 2.0 * i, "y": 3.0} for i, n in enumerate(names)]
             + [{"text": "ODASI", "x": 6.0, "y": 2.7}, {"text": "100/210", "x": 1.0, "y": 1.0}]}
    f2 = SN.unread_walls(b, texts)
    assert len(f2) == 1 and f2[0]["labels"] == 8


def test_a_level_with_its_labels_in_closed_rooms_is_clean():
    rooms, walls = [], []
    for i, n in enumerate(["Salon", "Mutfak", "Banyo", "Yatak Odası", "Çocuk Odası", "Antre", "WC", "Hol"]):
        rooms.append(room(f"r{i}", n, "living", rect(4 * i, 0, 4 * i + 3.8, 4)))
        walls += box_walls(4 * i, 0, 4 * i + 3.8, 4, prefix=f"w{i}_")
    assert SN.unread_walls(building(rooms=rooms, walls=walls)) == []


# -------------------------------------------------------------------------------------------------- 5. circulation
def _two_levels(upper_stair_at):
    levels = [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0},
              {"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0}]
    furn = [{"id": "f0", "level_id": "L0", "type": "stair", "footprint": {"center": [2, 2], "size": [1.2, 3.0]}}]
    if upper_stair_at is not None:
        furn.append({"id": "f1", "level_id": "L1", "type": "stair",
                     "footprint": {"center": list(upper_stair_at), "size": [1.2, 3.0]}})
    return building(levels=levels, furniture=furn)


def test_a_level_no_stair_reaches_is_major_and_stacked_stairs_are_clean():
    assert SN.stair_links(_two_levels((2.1, 2.0))) == []
    f = SN.stair_links(_two_levels(None))
    assert len(f) == 1 and f[0]["severity"] == "major" and f[0]["level_id"] == "L1"
    assert "no stair is read on L1" in f[0]["message"]
    # 6 Nov 2026, round 2: one core stair on each floor is the stacking rule's question, not the link rule's
    far = _two_levels((12.0, 2.0))
    assert SN.stair_links(far) == []
    stack = SN.stair_stacking(far)
    assert len(stack) == 1 and stack[0]["offset_m"] == pytest.approx(10.0) and stack[0]["severity"] == "major"


def test_a_room_with_no_door_is_minor_and_a_room_with_one_is_clean():
    walls = box_walls(0, 0, 4, 4) + box_walls(4, 0, 8, 4, prefix="v") + [wall("x1", (8, 0), (12, 0))]
    rooms = [room("r_a", "Yatak Odası", "bedroom", rect(0.1, 0.1, 3.9, 3.9)),
             room("r_b", "Salon", "living", rect(4.1, 0.1, 7.9, 3.9)),
             room("r_s", "Şaft", "shaft", rect(9, 0.1, 10, 1.1))]                          # 1 m2: exempt
    door = {"id": "d1", "level_id": "L0", "type": "door", "wall_id": "w2", "center": [4.0, 2.0], "width": 0.9}
    found = rules_of(SN.circulation(building(rooms=rooms, walls=walls, openings=[door])), "circulation")
    rooms_without = [f["element_ids"] for f in found if f["part"] == "room"]
    assert rooms_without == []                       # the door between them reaches both; the shaft is exempt
    found = SN.circulation(building(rooms=rooms, walls=walls))
    assert sorted(f["element_ids"][0] for f in found if f["part"] == "room") == ["r_a", "r_b"]
    assert all(f["severity"] == "minor" for f in found)


def test_a_flat_with_no_door_to_a_stair_hall_or_the_outside_is_minor():
    levels = [{"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0}]
    walls = [wall(w["id"], w["start"], w["end"], "L1")
             for w in box_walls(0, 0, 4, 4) + box_walls(4, 0, 8, 4, prefix="v") + box_walls(8, 0, 11, 4, prefix="h")]
    rooms = [room("r_a", "Yatak Odası", "bedroom", rect(0.1, 0.1, 3.9, 3.9), "L1"),
             room("r_b", "Salon", "living", rect(4.1, 0.1, 7.9, 3.9), "L1"),
             room("r_h", "Kat Holü", "hall", rect(8.1, 0.1, 10.9, 3.9), "L1")]
    doors = [{"id": "d1", "level_id": "L1", "type": "door", "wall_id": "w2", "center": [4.0, 2.0], "width": 0.9},
             {"id": "d3", "level_id": "L1", "type": "door", "wall_id": "h2", "center": [11.0, 2.0], "width": 0.9}]
    furn = [{"id": "f1", "level_id": "L1", "type": "stair", "footprint": {"center": [9.5, 2.0], "size": [1.2, 3.0]}}]
    b = building(rooms=rooms, walls=walls, openings=doors, levels=levels, furniture=furn)
    flats = [f for f in SN.circulation(b) if f.get("part") == "flat"]
    assert len(flats) == 1 and flats[0]["element_ids"] == ["r_a", "r_b"] and flats[0]["severity"] == "minor"
    b["openings"].append({"id": "d2", "level_id": "L1", "type": "door", "wall_id": "v2", "center": [8.0, 2.0],
                          "width": 0.9})
    assert [f for f in SN.circulation(b) if f.get("part") == "flat"] == []


def test_a_floor_that_is_one_flat_is_left_to_the_stair_rule():
    levels = [{"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0}]
    walls = [wall(w["id"], w["start"], w["end"], "L1")
             for w in box_walls(0, 0, 4, 4) + box_walls(4, 0, 8, 4, prefix="v")]
    rooms = [room("r_a", "Yatak Odası", "bedroom", rect(0.1, 0.1, 3.9, 3.9), "L1"),
             room("r_b", "Salon", "living", rect(4.1, 0.1, 7.9, 3.9), "L1")]
    door = {"id": "d1", "level_id": "L1", "type": "door", "wall_id": "w2", "center": [4.0, 2.0], "width": 0.9}
    b = building(rooms=rooms, walls=walls, openings=[door], levels=levels)
    assert [f for f in SN.circulation(b) if f.get("part") == "flat"] == []


# ---------------------------------------------------------------------------------------------- 6. label vocabulary
@pytest.mark.parametrize("label", ["Bına Taban Hattı Yatak Odası", "Tesısat Duvarı H: 1.20 Cm", "Normal",
                                   "Salon +3.00", "Mutfak Saçak İzdüşümü"])
def test_notation_glued_to_a_room_name_is_minor(label):
    f = SN.label_vocabulary(building(rooms=[room("r1", label, "other", rect(0, 0, 3, 4))]))
    assert len(f) == 1 and f[0]["severity"] == "minor" and f[0]["notation"]


@pytest.mark.parametrize("label", ["Yatak Odası", "Kat Holü", "Kat Kal.", "Banyo Wc", "Oda-01", "Dükkan",
                                   "Hidrolik Asansör 4 Kişiliktir"])
def test_plain_room_names_are_clean(label):
    assert SN.label_vocabulary(building(rooms=[room("r1", label, "other", rect(0, 0, 3, 4))])) == []


# --------------------------------------------------------------------------------------------------------- trust
def test_a_rule_below_the_threshold_writes_info_and_one_above_keeps_its_severity():
    b = building(rooms=[room("r_lift", "Asansör", "shaft", rect(0, 0, 1.0, 0.4)),                # 0.4 m2
                        room("r1", "Bına Taban Hattı Yatak Odası", "bedroom", rect(10, 0, 13, 4))])
    trust = {"threshold": 0.7, "rules": {"room_type_area": {"findings": 10, "judged_right": 9, "precision": 0.9},
                                         "label_vocabulary": {"findings": 10, "judged_right": 5, "precision": 0.5}}}
    found = SN.run(b, {}, trust=trust)
    by = {f["rule"]: f for f in found}
    assert by["room_type_area"]["severity"] == "major" and "rule precision 0.90" in by["room_type_area"]["message"]
    assert by["label_vocabulary"]["severity"] == "info" and by["label_vocabulary"]["base_severity"] == "minor"
    assert "info only" in by["label_vocabulary"]["message"]
    tr = SN.trust_from([{"rule": "room_type_area", "right": True, "project_status": "accepted"},
                        {"rule": "room_type_area", "right": False, "project_status": "open"},
                        {"rule": "circulation", "right": True}])
    rta = tr["rules"]["room_type_area"]
    assert {k: rta[k] for k in ("findings", "judged_right", "precision", "trusted")} == \
        {"findings": 2, "judged_right": 1, "precision": 0.5, "trusted": False}
    assert rta["by_status"] == {"accepted": {"findings": 1, "judged_right": 1},
                                "open": {"findings": 1, "judged_right": 0}}
    assert rta["small_sample"] is True
    assert tr["rules"]["circulation"]["trusted"] is True and tr["rules"]["unread_walls"]["precision"] is None


def test_the_trust_file_names_every_rule_with_its_judgements():
    tr = SN.load_trust()
    assert tr is not None and set(tr["rules"]) == set(SN.RULES) and tr["threshold"] == SN.TRUST_MIN
    for rule, v in tr["rules"].items():
        assert set(v) >= {"findings", "judged_right", "precision", "trusted"}
        js = [j for j in tr["judgements"] if j["rule"] == rule]
        assert len(js) == v["findings"] and sum(j["right"] for j in js) == v["judged_right"]
        assert all(j.get("reason") for j in js)


# ------------------------------------------------------------------------- round 2 (6 Nov 2026): the user's past fixes
def test_a_door_on_the_float_edge_of_its_reach_still_opens_into_the_room():
    # real16 L1 d_L1_001: the face 0.15000000000000036 m from the door, the reach 0.05 + 0.10 = 0.15000000000000002
    d = 0.15000000000000036
    walls = [wall("w1", (0.0, -1.0), (0.0, 1.0), t=0.1), wall("w2", (-4.0, -1.0), (-4.0, 1.0), t=0.1)]
    rooms = [room("r_a", "Antre", "hall", rect(-3.9, -0.9, -0.05, 0.9)), room("r_b", "Oda", "unknown",
                                                                            rect(d, -0.9, 3.0, 0.9))]
    door = {"id": "d1", "level_id": "L0", "type": "door", "wall_id": "w1", "center": [0.0, 0.0], "width": 0.9}
    access, links, _outer, _loose = SN.room_access(building(rooms=rooms, walls=walls, openings=[door]), "L0")
    assert access["r_b"] == ["d1"] and ("r_a", "r_b") in links


def test_a_flat_whose_hall_is_an_untyped_room_names_that_room():
    levels = [{"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0}]
    walls = [wall(w["id"], w["start"], w["end"], "L1")
             for w in box_walls(0, 0, 4, 4) + box_walls(4, 0, 8, 4, prefix="v") + box_walls(8, 0, 12, 4, prefix="h")
             + box_walls(12, 0, 16, 4, prefix="k")]
    # two flats (two living rooms) joined through an unnamed room: that room is named as their likely hall (real16 L1)
    rooms = [room("r_a", "Salon", "living", rect(0.1, 0.1, 3.9, 3.9), "L1"),
             room("r_c", "Oda", "unknown", rect(4.1, 0.1, 7.9, 3.9), "L1"),
             room("r_b", "Salon", "living", rect(8.1, 0.1, 11.9, 3.9), "L1"),
             room("r_x", "Kat Holü", "hall", rect(12.1, 0.1, 15.9, 3.9), "L1")]
    doors = [{"id": "d1", "level_id": "L1", "type": "door", "wall_id": "w2", "center": [4.0, 2.0], "width": 0.9},
             {"id": "d2", "level_id": "L1", "type": "door", "wall_id": "v2", "center": [8.0, 2.0], "width": 0.9},
             {"id": "d3", "level_id": "L1", "type": "door", "wall_id": "k2", "center": [16.0, 2.0], "width": 0.9}]
    b = building(rooms=rooms, walls=walls, openings=doors, levels=levels)
    flats = [f for f in SN.circulation(b) if f.get("part") == "flat"]
    assert len(flats) == 1 and flats[0]["element_ids"] == ["r_a", "r_b", "r_c"]
    assert "untyped room r_c 'Oda'" in flats[0]["message"] and "did not close" not in flats[0]["message"]
    # one flat with an unnamed room: that room is a room of the flat, its entrance door is what is missing
    b["rooms"][2] = room("r_b", "Mutfak", "kitchen", rect(8.1, 0.1, 11.9, 3.9), "L1")
    flats = [f for f in SN.circulation(b) if f.get("part") == "flat"]
    assert len(flats) == 1 and "entrance door is not read" in flats[0]["message"]


def _recess(label="", door=False):
    """A named salon with a window onto a small recess closed by a wall with a gap in the facade (real10 C0023)."""
    walls = [wall("w1", (0, 0), (5, 0), exterior=True), wall("w2", (5, 0), (5, 4)),
             wall("w3", (5, 4), (0, 4), exterior=True), wall("w4", (0, 4), (0, 0), exterior=True),
             wall("w5", (5, 1), (6.5, 1), exterior=True), wall("w6", (6.5, 1), (6.5, 3), exterior=True),
             wall("w7", (6.5, 3), (5, 3), exterior=True)]
    rooms = [room("r_salon", "Salon", "living", rect(0.1, 0.1, 4.9, 3.9)),
             room("r_x", label, "hall", rect(5.1, 1.1, 6.4, 2.9))]
    ops = [{"id": "win1", "level_id": "L0", "type": "window", "wall_id": "w2", "center": [5.0, 2.0], "width": 1.2},
           {"id": "o1", "level_id": "L0", "type": "door" if door else "opening", "wall_id": "w6",
            "center": [6.5, 2.0], "width": 1.2}]
    return building(rooms=rooms, walls=walls, openings=ops)


def test_a_facade_recess_closed_into_a_small_unnamed_room_is_major():
    f = SN.facade_recess(_recess("Oda"))
    assert len(f) == 1 and f[0]["severity"] == "major" and f[0]["element_ids"][0] == "r_x"
    assert "win1" in f[0]["message"] and "'Salon'" in f[0]["message"]


@pytest.mark.parametrize("label,door", [("WC", False), ("Oda", True)])
def test_a_named_small_room_or_one_with_a_door_is_no_recess(label, door):
    assert SN.facade_recess(_recess(label, door)) == []


def _stair(sid, centre, size, lines=12, level="L0"):
    return {"id": sid, "level_id": level, "type": "stair", "footprint": {"center": list(centre), "size": list(size)},
            "stair": {"flights": [{"lines": lines}]}}


def test_a_stair_in_a_bathroom_or_too_small_is_false_and_a_core_stair_is_clean():
    rooms = [room("r_b", "Banyo", "bathroom", rect(0, 0, 2, 2)), room("r_h", "Hol", "hall", rect(3, 0, 8, 4))]
    furn = [_stair("f1", (1, 1), (1.2, 1.4), lines=5), _stair("f2", (4, 1), (1.0, 1.2)),
            _stair("f3", (6.5, 2), (1.2, 3.0), lines=14)]
    furn.append({"id": "f4", "level_id": "L0", "type": "stair", "footprint": {"center": [5, 3.4], "size": [1.7, 1.2]},
                 "stair": {"flights": [{"lines": 5}, {"lines": 5}, {"lines": 5}]}})     # real09's kitchen tiles
    found, ids = SN.false_stairs(building(rooms=rooms, furniture=furn))
    assert ids == {"f1", "f2", "f4"} and all(f["severity"] == "major" for f in found)
    by = {f["element_ids"][0]: f for f in found}
    assert "bathroom r_b 'Banyo'" in by["f1"]["message"] and "5 tread lines" in by["f1"]["message"]
    assert "1.20 m2" in by["f2"]["message"] and "3 flights in 2.04 m2" in by["f4"]["message"]


def test_false_stairs_join_no_level():
    levels = [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0},
              {"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0}]
    rooms = [room("r_b", "Banyo", "bathroom", rect(0, 0, 2, 2), "L1")]
    furn = [_stair("f0", (1, 1), (1.2, 3.0)), _stair("f1", (1, 1), (1.2, 1.4), lines=5, level="L1")]
    b = building(rooms=rooms, furniture=furn, levels=levels)
    found = SN.run(b, {}, trust=NO_TRUST)
    links = [f for f in found if f["rule"] == "circulation" and f.get("part") == "levels"]
    assert len(links) == 1 and "no stair is read on L1" in links[0]["message"]
    assert [f["element_ids"][0] for f in found if f["rule"] == "false_stair"] == ["f1"]


def test_stairs_half_a_metre_apart_stack():
    assert SN.stair_stacking(_two_levels((2.4, 2.3))) == []


def _twins(b_doors=1, b_label="Mutfak", b_type="kitchen", b_size=3.0):
    walls = box_walls(0, 0, 3, 4) + box_walls(5, 0, 5 + b_size, 4, prefix="v")
    rooms = [room("r_a", "Mutfak", "kitchen", rect(0.1, 0.1, 2.9, 3.9)),
             room("r_b", b_label, b_type, rect(5.1, 0.1, 5 + b_size - 0.1, 3.9), twin_of="r_a",
                  twin_transform=[-1, 0, 8, 0, 1, 0])]
    ops = [{"id": "d1", "level_id": "L0", "type": "door", "wall_id": "w1", "center": [1.5, 0.0], "width": 0.9}]
    if b_doors:
        ops.append({"id": "d2", "level_id": "L0", "type": "door", "wall_id": "v1", "center": [6.5, 0.0], "width": 0.9})
    return building(rooms=rooms, walls=walls, openings=ops)


def test_a_twin_with_no_door_is_major_one_of_another_type_minor_and_alike_twins_clean():
    assert SN.mirror_twins(_twins()) == []
    f = SN.mirror_twins(_twins(b_doors=0))
    assert len(f) == 1 and f[0]["severity"] == "major" and "ways in 1 / 0" in f[0]["message"]
    f = SN.mirror_twins(_twins(b_label="Oda", b_type="unknown", b_size=4.2))
    assert len(f) == 1 and f[0]["severity"] == "minor" and "type kitchen / untyped" in f[0]["message"]
    assert "area" in f[0]["message"]


def _mirrored_plan(right_last=("Oda", "unknown"), reader_twins=True):
    """Two flats mirrored about x = 5, three rooms a side; the reading paired the bedrooms (``twin_of`` with its
    transform) and nothing else; the right-hand twin of 'Banyo' is ``right_last``."""
    xs = (1.5, 3.0, 4.9, 5.1, 7.0, 8.5)
    walls = box_walls(0, 0, 10, 4) + [wall(f"i{k}", (x, 0), (x, 4)) for k, x in enumerate(xs)]
    twin = {"twin_of": "r_l2", "twin_transform": [-1.0, 0.0, 10.0, 0.0, 1.0, 0.0]} if reader_twins else {}
    rooms = [room("r_l1", "Banyo", "bathroom", rect(0.1, 0.1, 1.4, 3.9)),
             room("r_l2", "Yatak Odası", "bedroom", rect(1.6, 0.1, 2.9, 3.9)),
             room("r_l3", "Salon", "living", rect(3.1, 0.1, 4.8, 3.9)),
             room("r_r3", "Salon", "living", rect(5.2, 0.1, 6.9, 3.9)),
             room("r_r2", "Yatak Odası", "bedroom", rect(7.1, 0.1, 8.4, 3.9), **twin),
             room("r_r1", right_last[0], right_last[1], rect(8.6, 0.1, 9.9, 3.9))]
    return building(rooms=rooms, walls=walls)


def test_twins_found_about_the_readings_own_mirror_axis():
    pairs, axis = SN.mirror_pairs(_mirrored_plan(), "L0")
    assert axis == ("x", 5.0)
    assert sorted(tuple(sorted((a["id"], b["id"]))) for a, b, _ in pairs) == \
        [("r_l1", "r_r1"), ("r_l2", "r_r2"), ("r_l3", "r_r3")]
    f = SN.mirror_twins(_mirrored_plan())
    assert len(f) == 1 and sorted(f[0]["element_ids"]) == ["r_l1", "r_r1"]
    assert "type bathroom / untyped" in f[0]["message"]
    assert SN.mirror_twins(_mirrored_plan(("Banyo", "bathroom"))) == []


def test_no_axis_of_the_reading_no_mirror_pairs():
    # 6 Nov 2026 calibration: an axis searched from the walls alone paired rooms of plans that do not mirror
    assert SN.mirror_pairs(_mirrored_plan(reader_twins=False), "L0") == ([], None)


def test_a_mirror_whose_rooms_mostly_disagree_is_left_alone():
    b = _mirrored_plan(("Mutfak", "kitchen"))
    b["rooms"][3] = room("r_r3", "Oda", "unknown", rect(5.2, 0.1, 6.9, 3.9))
    pairs, axis = SN.mirror_pairs(b, "L0")
    assert axis is None and [(x["id"], y["id"]) for x, y, _ in pairs] == [("r_l2", "r_r2")]


def _passage(kind="opening", width=1.2, arc=False):
    walls = box_walls(0, 0, 3, 4) + box_walls(3, 0, 8, 4, prefix="v")
    rooms = [room("r_h", "Hol", "hall", rect(0.1, 0.1, 2.9, 3.9)), room("r_s", "Salon", "living",
                                                                       rect(3.1, 0.1, 7.9, 3.9))]
    ops = [{"id": "o1", "level_id": "L0", "type": kind, "wall_id": "w2", "center": [3.0, 2.0], "width": width}]
    b = building(rooms=rooms, walls=walls, openings=ops)
    b["walls"] = [dict(w, exterior=False) if w["id"] in ("w2", "v4") else w for w in b["walls"]]
    if arc:
        b["symbols"] = [{"id": "sy1", "kind": "door_arc", "level_id": "L0", "footprint": {"center": [3.3, 2.3]}}]
    return b


def test_a_gap_between_a_hall_and_a_room_with_no_door_symbol_is_minor():
    f = SN.wall_across_passage(_passage())
    assert len(f) == 1 and f[0]["severity"] == "minor" and f[0]["element_ids"][:2] == ["w2", "o1"]


@pytest.mark.parametrize("kind,width,arc", [("door", 1.2, False), ("opening", 3.0, False), ("opening", 1.2, True)])
def test_a_door_a_wide_opening_or_a_gap_with_its_door_symbol_is_no_walled_passage(kind, width, arc):
    assert SN.wall_across_passage(_passage(kind, width, arc)) == []


def test_a_sliver_typed_hall_is_wall_mass_reported_once():
    b = building(rooms=[room("r_s", "Oda", "hall", rect(0, 0, 0.6, 0.6)),             # 0.36 m2 (real10 r_L0_oda_18)
                        room("r_t", "Oda", "hall", rect(2, 0, 2.9, 1.0))])            # 0.9 m2
    found = SN.run(b, {}, trust=NO_TRUST)
    by = {}
    for f in found:
        if f["rule"] in ("wall_mass", "room_type_area"):
            by.setdefault(f["element_ids"][0], []).append(f["rule"])
    assert by == {"r_s": ["wall_mass"], "r_t": ["room_type_area"]}


# ----------------------------------------------------------------------------------------------- wiring into check
def _output(tmp_path):
    b = building(rooms=[room("r_lift", "Asansör", "shaft", rect(0, 0, 3.0, 4.0))])
    b["project"] = {"id": "p"}
    (tmp_path / "building.json").write_text(json.dumps(b), encoding="utf-8")
    return tmp_path


def test_check_carries_rc14_as_advisory_findings_outside_the_verdict(tmp_path):
    res = RC.check(_output(tmp_path))
    rc14 = [f for f in res["findings"] if f["check"] == "RC14"]
    assert rc14 and all(f["advisory"] is True for f in rc14)
    assert any(f["rule"] == "room_type_area" and f["element_ids"] == ["r_lift"] for f in rc14)
    adv = res["counts"]["advisory"]
    assert sum(adv.values()) >= len(rc14)
    assert res["verdict"] == "ready" and res["counts"]["critical"] == 0
    assert res["counts"]["major"] == sum(1 for f in res["findings"] if f["severity"] == "major"
                                         and not f.get("advisory"))
    md = (RC.write(tmp_path, res) / "reading_check.md").read_text(encoding="utf-8")
    assert "| RC14 architectural sense (advisory) |" in md


def test_a_failure_of_the_sense_checks_is_one_info_finding(tmp_path, monkeypatch):
    def boom(out_dir):
        raise RuntimeError("no luck")
    monkeypatch.setattr(SN, "findings", boom)
    res = RC.check(_output(tmp_path))
    rc14 = [f for f in res["findings"] if f["check"] == "RC14"]
    assert len(rc14) == 1 and rc14[0]["severity"] == "info" and "no luck" in rc14[0]["message"]
    assert rc14[0]["advisory"] is True and res["counts"]["advisory"]["info"] >= 1 and res["verdict"] == "ready"
