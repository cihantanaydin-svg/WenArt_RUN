"""Drawn sofas with their cushion marks are sofas, not rugs (27 Oct 2026; pod run 20261026-224516-full, real06's salon:
a 2.12 x 0.78 m and a 1.52 x 0.78 m drawn sofa each held 0.21 x 0.20 m cushion marks; two of the marks were typed
potted plants, the sofas became "rug outlines" and were never built, and the judge saw "a 55 m2 salon with no sofa").

- ``infer.small_mark`` / ``outline_holds``: a mark smaller than 0.30 m both ways is never a piece an outline is drawn
  around;
- ``infer.drawn_host_of``: a small mark inside a larger drawn outline (typed or not) is a detail of it (not built);
- ``names.zone_types_elsewhere``: the anchor type of a labelled zone the piece is not in (a dining table where the
  documents put the dining area elsewhere in the room) is never its type;
- ``infer._position_ok``: a sofa (back ``wall_or_group``) stands on a wall or in its group.
"""
from __future__ import annotations

import _m11_room as M
from wenart.furniture import infer as INF
from wenart.furniture import names as NM


def unknown(pid, center, size, rotation=0.0, **kw):
    return M.fp(pid, "unknown", center, size, rotation=rotation, front=None, status="unverified",
                type_method="none", **kw)


def test_cushion_marks_never_make_a_sofa_a_rug():
    sofa = unknown("u1", (3.0, 0.6), (2.12, 0.78), rotation=180.0,
                   type_candidates=[{"type": "unknown", "pass": 1}, {"type": "sofa", "pass": 2}])
    marks = [unknown("m1", (2.5, 0.5), (0.21, 0.20)), unknown("m2", (3.5, 0.5), (0.21, 0.20))]
    b = M.building(w=7.0, h=5.0, room_type="living", furniture=[sofa, *marks])
    props = {p["piece_id"]: p for p in INF.infer_types(b)}
    assert props["u1"]["type"] == "sofa" and props["u1"].get("build") is not False          # no rug
    for m in ("m1", "m2"):
        assert props[m]["type"] == INF.DETAIL_TYPE and props[m]["build"] is False
        assert "cushion" in props[m]["reason"] and "u1" in props[m]["reason"]
    assert INF.small_mark(marks[0]) and not INF.small_mark(sofa)
    # a real outline around real pieces stays a rug
    table = M.fp("t1", "table_coffee", (3.0, 2.5), (1.0, 0.6), front=None)
    rug = unknown("r1", (3.0, 2.4), (3.0, 2.2))
    b = M.building(w=7.0, h=5.0, room_type="living", furniture=[table, rug])
    assert [(p["piece_id"], p["type"]) for p in INF.infer_types(b)] == [("r1", "rug")]


def test_a_typed_host_or_an_untyped_one_holds_the_mark():
    sofa = M.fp("s1", "sofa", (3.0, 0.5), (2.2, 0.9), rotation=180.0, front=90.0)
    mark = unknown("m1", (3.0, 0.5), (0.21, 0.20))
    pieces = [sofa, mark]
    poly = INF.placer.drawn_piece(mark).polygon()
    assert INF.drawn_host_of(mark, poly, [sofa])["id"] == "s1"
    far = unknown("m2", (3.0, 3.0), (0.21, 0.20))
    assert INF.drawn_host_of(far, INF.placer.drawn_piece(far).polygon(), pieces) is None
    big = unknown("u9", (3.0, 3.0), (0.5, 0.5))                       # not a small mark: no host rule
    assert INF.drawn_host_of(big, INF.placer.drawn_piece(big).polygon(), pieces) is None


def test_a_labelled_zone_elsewhere_in_the_room_rules_out_its_anchor():
    b = M.building(w=9.0, h=6.0, room_type="living")
    b["zone_labels"] = [{"id": "TEXT:1", "room_id": M.ROOM_ID, "kind": "dining", "anchors": ["table_dining"],
                         "zone": [[0, 3], [4, 3], [4, 6], [0, 6]]}]
    seat = unknown("u1", (6.5, 0.6), (1.52, 0.78), rotation=180.0,
                   type_candidates=[{"type": "table_dining", "pass": 1}, {"type": "sofa", "pass": 2}])
    inside = unknown("u2", (2.0, 4.5), (1.6, 0.9))
    assert NM.zone_types_elsewhere(b, seat) == {"table_dining"}
    assert NM.zone_types_elsewhere(b, inside) == set()                # in the dining zone: its own anchor stays
    armchair = M.fp("a1", "armchair", (5.0, 1.8), (0.9, 0.8), front=0.0)
    b["furniture"] = [seat, armchair, M.fp("s9", "sofa", (8.0, 3.0), (2.0, 0.9), rotation=90.0, front=180.0)]
    props = {p["piece_id"]: p for p in INF.infer_types(b)}
    assert props["u1"]["type"] == "sofa"


def test_a_sofa_stands_on_a_wall_or_in_its_group():
    sofa = INF.placer.drawn_piece(M.fp("s", "sofa", (3.0, 2.0), (2.0, 0.85), front=90.0))
    chair = ("armchair", INF.placer.drawn_piece(M.fp("a", "armchair", (5.0, 2.0), (0.9, 0.8), front=180.0)))
    assert INF._position_ok("sofa", sofa, True, [])
    assert INF._position_ok("sofa", sofa, False, [chair])                 # free, beside its armchair
    lone = ("armchair", INF.placer.drawn_piece(M.fp("a", "armchair", (9.0, 9.0), (0.9, 0.8), front=180.0)))
    assert not INF._position_ok("sofa", sofa, False, [lone])
    assert not INF._position_ok("bed_double", sofa, False, [chair])      # a bed: on a wall only


def test_a_gap_the_drawing_puts_furniture_in_front_of_is_a_window():
    """27 Oct 2026 (``architect_actions.gaps_behind_furniture``): real06's east windows were read as 1.55 m doorless
    gaps; the drawn sofa in front of one "blocked a door" and could not be built. A reading gap in an outer wall with
    drawn furniture across its approach is a window (the level's usual sill and height), corrected_by_ai by code with
    the drawn values kept; a gap with a free approach, a gap between two rooms, a rug or a cushion mark change nothing."""
    from wenart.blender import architect_actions as AA

    def gap(oid, x, width=1.55):
        return {"id": oid, "type": "opening", "level_id": "L0", "wall_id": "w_n", "center": [x, 4.05],
                "width": width, "height": 2.1, "sill_height": None, "status": "unverified",
                "type_raw": "unclassified gap content", "evidence": []}

    sofa = M.fp("s1", "sofa", (1.5, 3.55), (2.0, 0.85), rotation=180.0, front=270.0)
    rug = M.fp("r1", "unknown", (4.0, 3.5), (1.5, 0.9), inferred_as="rug", build=False)
    mark = M.fp("m1", "unknown", (6.5, 3.85), (0.2, 0.2))
    b = M.building(w=8.0, h=4.0, room_type="living", window=None, furniture=[sofa, rug, mark])
    b["openings"] += [gap("o1", 1.5), gap("o2", 4.0), gap("o3", 6.5)]
    reasons = AA.gaps_behind_furniture(b)
    by = {o["id"]: o for o in b["openings"]}
    assert len(reasons) == 1 and "o1" in reasons[0] and "s1" in reasons[0]
    o1 = by["o1"]
    assert o1["type"] == "window" and o1["sill_height"] == 0.9 and o1["height"] == 1.2
    assert o1["drawn_type"] == "opening" and o1["drawn_height"] == 2.1
    assert o1["corrected_by_ai"]["rule"] == "gap_behind_furniture" and o1["evidence"][-1]["method"] == "inferred"
    assert by["o2"]["type"] == "opening" and by["o3"]["type"] == "opening"      # a rug, a cushion mark: no passage lost


class _Build:
    def __init__(self, building):
        self.building, self.warnings = building, []

    def warn(self, text):
        self.warnings.append(text)


def test_a_named_bedroom_piece_keeps_a_generic_oda_a_bedroom():
    """27 Oct 2026 (real06's r_L1_oda_2: "*SIFONIYER" written in it, a drawn single bed typed "sofa" by two AI passes):
    the furniture name text of a bedroom piece in a room named only "ODA" keeps it a bedroom (text outranks the AI
    passes); without it the drawn sofa makes it a living room as before."""
    from wenart.ingest.generic import reading as RD

    sofa = M.fp("s1", "sofa", (2.0, 0.5), (2.0, 0.9), type_method="ai_two_pass")
    b = M.building(room_type="bedroom", furniture=[sofa])
    b["rooms"][0].update(label="ODA", label_raw="ODA")
    text = {"id": "TEXT:1", "room_id": M.ROOM_ID, "text": "*SIFONIYER", "type": "dresser", "types": ["dresser"]}
    named = dict(b, furniture_texts=[text], rooms=[dict(b["rooms"][0])])
    assert RD.generic_rooms(_Build(named)) == [] and named["rooms"][0]["room_type"] == "bedroom"
    plain = dict(b, rooms=[dict(b["rooms"][0])])
    assert RD.generic_rooms(_Build(plain)) == [M.ROOM_ID] and plain["rooms"][0]["room_type"] == "living"


def test_argus_suspects_a_vision_typed_piece_the_room_cannot_hold():
    """27 Oct 2026: N5's suspects include a drawn piece the vision passes typed as a type its room may not hold (a sofa
    in a bedroom with no bed); the code fix retypes it to the missing member by its size."""
    from wenart.audit import argus_ai as AX
    from wenart.audit import sense as SN

    sofa = M.fp("s1", "sofa", (2.0, 0.5), (2.0, 0.92), type_method="ai_two_pass",
                evidence=[{"method": "vector", "entity": "LINE:1"}])
    block = M.fp("s2", "sofa", (2.0, 2.5), (2.0, 0.92), type_method="block_name",
                 evidence=[{"method": "vector", "entity": "INSERT:1"}])
    b = M.building(room_type="bedroom", furniture=[sofa, block])
    assert [f["id"] for f in SN.misfits(b, M.ROOM_ID, b["furniture"])] == ["s1"]     # a block name stands
    finding = {"check": "N5", "line": "sense", "severity": "major", "target": "s1", "message": "misses its bed",
               "evidence": {"room": M.ROOM_ID, "missing": "bed_double|bed_single"}}
    actions, _work, _rev = AX.code_actions({"findings": [finding]}, b)
    assert [(a["tool"], a["args"]["type"]) for a in actions] == [("retype_piece", "bed_single")]
    assert AX.missing_for({"footprint": {"size": [2.0, 1.6]}}, "bed_double|bed_single") == "bed_double"
    assert AX.missing_for({"footprint": {"size": [1.7, 0.75]}}, "shower|bathtub") == "bathtub"


def test_a_passage_with_a_walkway_left_or_onto_a_terrace_stays_and_a_sliding_door_read_from_lines_may_go():
    """27 Oct 2026: two armchairs flanking a gap with 0.8 m free between them leave a walkway (it stays); a sliding door
    read only from its lines (no swing arc, no block name) with a sofa across it is a window; a passage onto a drawn
    terrace stays whatever stands in front of it."""
    from wenart.blender import architect_actions as AA

    def gap(oid, x, width=2.15, **kw):
        return dict({"id": oid, "type": "opening", "level_id": "L0", "wall_id": "w_n", "center": [x, 4.05],
                     "width": width, "height": 2.1, "sill_height": None, "status": "unverified",
                     "type_raw": "unclassified gap content", "evidence": []}, **kw)

    chairs = [M.fp("a1", "armchair", (0.9, 3.55), (0.9, 0.8), front=270.0),
              M.fp("a2", "armchair", (2.6, 3.55), (0.9, 0.8), front=270.0)]
    sofa = M.fp("s1", "sofa", (6.0, 3.55), (2.0, 0.85), rotation=180.0, front=270.0)
    b = M.building(w=12.0, h=4.0, room_type="living", window=None, furniture=chairs + [sofa])
    sliding = gap("d1", 6.0, type="door", operation="sliding", operation_source="geometry", type_raw=None,
                  evidence=[{"method": "vector", "note": "2 leaf/leaves drawn parallel to the wall without a swing arc"}])
    named = dict(sliding, id="d2", center=[10.0, 4.05],
                 evidence=[{"method": "vector", "note": "door by its block name 'SLIDE' (sliding)"}])
    b["furniture"].append(M.fp("s2", "sofa", (10.0, 3.55), (2.0, 0.85), rotation=180.0, front=270.0))
    b["openings"] += [gap("o1", 1.75), sliding, named]
    reasons = AA.gaps_behind_furniture(b)
    by = {o["id"]: o for o in b["openings"]}
    assert by["o1"]["type"] == "opening"                         # 0.8 m free between the armchairs
    assert by["d1"]["type"] == "window" and by["d1"]["drawn_operation"] == "sliding"
    assert by["d2"]["type"] == "door"                            # a block name says sliding door
    assert len(reasons) == 1 and "sliding door read from its lines" in reasons[0]
    # onto a drawn terrace: stays
    t = M.building(w=8.0, h=4.0, room_type="living", window=None, furniture=[M.fp("s1", "sofa", (1.5, 3.55), (2.0, 0.85),
                                                                                  rotation=180.0, front=270.0)])
    t["openings"].append(gap("o1", 1.5, width=1.55))
    t["site"] = {"outdoor_spaces": [{"id": "os1", "level_id": "L0", "polygon": [[0, 4.1], [8, 4.1], [8, 7], [0, 7]]}]}
    assert AA.gaps_behind_furniture(t) == [] and t["openings"][-1]["type"] == "opening"
