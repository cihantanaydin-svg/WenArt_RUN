"""6 Nov 2026 (Milestone 14 R6, RC14): the architectural-sense checks of a reading.

What: one hit and one clean case per rule on hand-made building dicts; the four known errors of the current readings
on small fixtures shaped like them (a 16 m2 lift; a fire-lobby label in a 99 m2 face with a car park label; frame
walls on a region box with a paper room; a level with 8 labels and 3 walls); the trust file lowering a rule; the wiring
into ``wenart.reading_check.check`` as advisory findings.
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
    far = SN.stair_links(_two_levels((12.0, 2.0)))
    assert len(far) == 1 and "apart in plan" in far[0]["message"]


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
    assert rta["by_status"] == {"accepted": {"findings": 1, "judged_right": 1}, "open": {"findings": 1, "judged_right": 0}}
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
