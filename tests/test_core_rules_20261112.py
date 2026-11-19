"""12 Nov 2026 (the architect's audit of 8 buildings; user: "Make sense of the building", "This is for all the
projects"): the common core completed by general rules (``wenart.ingest.core_rules``) and checked (RC14).

What: a 12 x 8 m storey of a building with a lift: a west flat's kitchen, the core hall with a stroke box the reading
set aside as notation and a lift, an east flat's bedroom and kitchen. The reading has no stair, a derived lift door
opens into the east bedroom, the west kitchen opens onto the core hall through an unclassified gap, and the only
"entrance" is a door from the east bedroom. The rules: the box becomes the stair (with its slab void) when stair
strokes stand in it (tread numbers or tread lines; the misfire hunters' guard G3), else no stair is built and a question
is asked (G2); the lift loses its derived door into the bedroom and gets a landing door onto the hall, while a drawn
door is kept for review (R16 G6); the pieces of one landing door are merged and made a sliding door (R19, C0034); the
kitchen's gap closes when the kitchen has its own door to the core and stays as an open-plan flat's only link (G4);
the core hall gets the building entrance on the facade it reaches. Negatives: a house of one storey needs no stair; a
lift door onto the hall stays; a box over the lifts is never the stair; a pit level gets no landing door.
"""
from __future__ import annotations

import math
from types import SimpleNamespace

from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart.ingest import completion as CP
from wenart.ingest import core_rules as CR
from wenart.reading_check import sense as SN

HALL = [[4.1, 0.1], [7.9, 0.1], [7.9, 5.9], [6.3, 5.9], [6.3, 7.9], [4.1, 7.9]]


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level):
    return {"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
            "area_computed": round(Polygon(poly).area, 3)}


def wall(wid, a, b, level, t=0.2):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": False}


def storey(lid, order):
    w = [wall(f"w_{lid}_s", (0, 0), (12, 0), lid), wall(f"w_{lid}_e", (12, 0), (12, 8), lid),
         wall(f"w_{lid}_n", (12, 8), (0, 8), lid), wall(f"w_{lid}_w", (0, 8), (0, 0), lid),
         wall(f"w_{lid}_4", (4, 0), (4, 8), lid), wall(f"w_{lid}_8", (8, 0), (8, 8), lid),
         wall(f"w_{lid}_l1", (6.4, 6.0), (8, 6.0), lid), wall(f"w_{lid}_l2", (6.4, 6.0), (6.4, 8), lid),
         wall(f"w_{lid}_k", (8, 4.0), (12, 4.0), lid)]
    rooms = [room(f"r_{lid}_west", "Mutfak", "kitchen", rect(0.1, 0.1, 3.9, 7.9), lid),
             room(f"r_{lid}_hall", "Hol", "hall", HALL, lid),
             room(f"r_{lid}_lift", "Asansör", "shaft", rect(6.5, 6.1, 7.9, 7.9), lid),
             room(f"r_{lid}_east", "Oda", "bedroom", rect(8.1, 0.1, 11.9, 3.9), lid),
             room(f"r_{lid}_ek", "Mutfak", "kitchen", rect(8.1, 4.1, 11.9, 7.9), lid)]
    ops = [{"id": f"d_{lid}_lift", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_8", "center": [8.0, 7.0],
            "width": 1.0, "evidence": [{"method": "derived", "rule": "lift_door"}]},
           {"id": f"o_{lid}_gap", "type": "opening", "level_id": lid, "wall_id": f"w_{lid}_4", "center": [4.0, 3.0],
            "width": 1.2},
           {"id": f"d_{lid}_flat", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_8", "center": [8.0, 2.0],
            "width": 0.9},
           {"id": f"d_{lid}_out", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_e", "center": [12.0, 2.0],
            "width": 0.9}]
    lv = {"id": lid, "label": f"{order}. Kat", "order": order, "elevation": 3.0 * order, "ceiling_height": 2.7}
    sym = {"id": f"sy_{lid}_001", "kind": "dimension_outline", "level_id": lid, "room_id": f"r_{lid}_hall",
           "footprint": {"center": [5.2, 3.0], "size": [1.8, 4.5], "rotation_deg": 0.0}, "evidence": []}
    return lv, w, rooms, ops, sym


def block(storeys=2, symbol=True):
    b = {"levels": [], "walls": [], "rooms": [], "openings": [], "furniture": [], "symbols": [], "warnings": [],
         "slabs": [], "site": {"entrances": [{"door_id": "d_L0_out", "level_id": "L0", "room_id": "r_L0_east",
                                              "face": [12.1, 2.0], "outward": [1.0, 0.0]}]},
         "level_inference": {}}
    for k in range(storeys):
        lv, w, rooms, ops, sym = storey(f"L{k}", k)
        b["levels"].append(lv)
        b["walls"] += w
        b["rooms"] += rooms
        b["openings"] += ops
        if symbol:
            b["symbols"].append(sym)
        if k:
            b["slabs"].append({"id": f"sl_L{k}", "below_level_id": f"L{k - 1}", "above_level_id": f"L{k}",
                               "openings": []})
    return b


def treads(b):
    """The tread numbers 1-16 drawn in every storey's stroke box (stair strokes, R08 G3)."""
    return {s["level_id"]: [{"text": str(i), "x": 5.2, "y": 1.0 + 0.25 * i} for i in range(1, 17)]
            for s in b["symbols"]}


def run(b, texts=None, strokes=None):
    build = SimpleNamespace(building=b, ids=B.IdCounter(), warn=lambda *_: None)
    return CR.apply(build, treads(b) if texts is None else texts, {}, strokes)


def flat_door(b):
    """The west kitchen's own (drawn) entrance door onto the core hall on every storey."""
    for lv in b["levels"]:
        b["openings"].append({"id": f"d_{lv['id']}_west", "type": "door", "level_id": lv["id"],
                              "wall_id": f"w_{lv['id']}_4", "center": [4.0, 6.5], "width": 0.9,
                              "evidence": [{"method": "vector", "entity": "ARC:1"}]})
    return b


NO_TRUST = {"threshold": 0.7, "rules": {r: {"findings": 10, "judged_right": 10, "precision": 1.0, "trusted": True}
                                        for r in SN.RULES}}


def rules(b, *names):
    return [f for f in SN.run(b, {}, trust=NO_TRUST) if f["rule"] in names]


def test_the_checks_see_what_the_reading_left_out():
    b = flat_door(block())
    assert [f["level_id"] for f in rules(b, "stair_missing")] == ["L0"]
    assert {f["element_ids"][-1] for f in rules(b, "lift_doors")} >= {"d_L0_lift"}
    assert {f["element_ids"][0] for f in rules(b, "core_gap")} == {"o_L0_gap", "o_L1_gap"}


def test_a_stroke_box_in_the_core_is_the_missed_stair_with_its_slab_void():
    b = block()
    rec = run(b)
    st = [f for f in b["furniture"] if f["type"] == "stair"]
    assert [s["level_id"] for s in st] == ["L0"] and rec["stairs"][0]["how"] == "stroke box"
    assert st[0]["source"] == "from_documents" and st[0]["inferred"] and st[0]["stair"]["turn"] == "U"
    assert b["slabs"][0]["openings"][0]["kind"] == "stair_void" and b["slabs"][0]["openings"][0]["furniture_id"] == \
        st[0]["id"]
    assert not rules(b, "stair_missing")
    # the stair arrives on the top storey through its void: L1 is reached (no flight rises into the roof)
    assert not [f for f in rules(b, "circulation") if "cannot be reached" in f["message"]]


def test_without_stair_strokes_no_stair_is_built_and_a_question_is_asked():
    """G2: geometry only from drawn strokes. The box without strokes is named in the question."""
    b = block()
    rec = run(b, texts={})
    assert rec["stairs"] == [] and not [f for f in b["furniture"] if f["type"] == "stair"]
    assert [(x["level_id"], x["candidate"]) for x in rec["stairs_open"]] == [("L0", "sy_L0_001")]
    item = next(n for n in b["needs_review"] if n["kind"] == "stair_not_drawn")
    assert "sy_L0_001" in item["reason"] and "no stair is built" in item["reason"]
    rec = run(block(symbol=False), texts={})
    assert rec["stairs"] == [] and rec["stairs_open"][0]["candidate"] is None


def sign_drawing(*segments, rects=()):
    """A drawing that holds only these segments and closed rectangles (``drawn_strokes.Drawn``'s query)."""
    segs = [{"a": a, "b": b2, "length": math.dist(a, b2), "id": f"LINE:{k}", "layer": "DIM"}
            for k, (a, b2) in enumerate(segments)]
    return SimpleNamespace(segments=lambda poly: [s for s in segs if poly.contains(
        Point((s["a"][0] + s["b"][0]) / 2.0, (s["a"][1] + s["b"][1]) / 2.0))], arcs=lambda poly: [],
        rectangles=lambda poly: [r for r in rects if poly.contains(Point(r["center"]))])


def sign_block(*segments, rects=(), strong=True, width=2.0, extra_box=False):
    b = block()
    for s in b["symbols"]:
        s["footprint"] = {"center": [5.2, 3.0], "size": [width, 4.6], "rotation_deg": 0.0}  # stair size, in the hall
    if extra_box:
        b["symbols"].append({"id": "sy_L0_009", "kind": "dimension_outline", "level_id": "L0", "room_id": "r_L0_hall",
                             "footprint": {"center": [7.0, 3.0], "size": [1.8, 4.0], "rotation_deg": 0.0}})
    if strong:                    # the verified R08 tier b: a passenger lift and a typical floor (the area table's)
        b["level_inference"]["storeys"] = {"areas": {"typical": {"value": 96.0, "text": "normal 96"}}}
    rec = CR.apply(SimpleNamespace(building=b, ids=B.IdCounter(), warn=lambda *_: None), {}, {}, None,
                   {"L0": sign_drawing(*segments, rects=rects)})
    return b, rec


def test_a_stair_size_box_with_a_well_line_is_an_inferred_u_stair():
    """The coordinator's decision of 12 Nov 2026 (real21): a building of two or more storeys has a stair; a stair-size
    box beside the core with a well line along its long axis is an inferred U stair, its risers from the storey height,
    listed for review with the evidence strokes."""
    b, rec = sign_block(((5.0, 1.0), (5.0, 5.0)))                       # the well line, 0.2 m off the middle
    assert [s["how"] for s in rec["stairs"]] == ["stair signs"]
    piece = next(f for f in b["furniture"] if f["type"] == "stair")
    st = piece["stair"]
    assert st["turn"] == "U" and st["risers"] == CR.risers_for(3.0) == 16 and [f["lines"] for f in st["flights"]] == [8, 8]
    assert piece["inferred"] and any("LINE:0" in str(e.get("entity")) for e in piece["evidence"])
    assert next(n for n in b["needs_review"] if n["kind"] == "stair_inferred")["id"] == piece["id"]


def test_a_break_diagonal_makes_a_straight_flight_and_an_x_no_stair():
    b, rec = sign_block(((4.4, 1.0), (6.0, 2.6)))                       # one break diagonal
    assert next(f for f in b["furniture"] if f["type"] == "stair")["stair"]["turn"] == "straight"
    b, rec = sign_block(((4.4, 1.0), (6.0, 2.6)), ((4.4, 2.6), (6.0, 1.0)))   # an X: a lift or a void
    assert rec["stairs"] == [] and rec["stairs_open"]
    b, rec = sign_block()                                               # the box alone: a question, no stair
    assert rec["stairs"] == [] and rec["stairs_open"][0]["candidate"] == "sy_L0_001"


def test_tier_b_needs_strong_storey_evidence_one_box_and_no_lift_car():
    """The verified R08 tier b (synthetic-01, -03 and -17 have no such evidence: they never get a stair this way)."""
    well = ((5.0, 1.0), (5.0, 5.0))
    assert sign_block(well, strong=False)[1]["stairs"] == []
    b, rec = sign_block(well, ((6.2, 1.5), (7.8, 3.1)), extra_box=True)   # a well here, a diagonal in the other box
    assert rec["stairs"] == [] and "which is the stair" in rec["stairs_open"][0]["reason"]
    car = {"center": (5.2, 3.0), "size": (1.1, 1.4), "id": "LWPOLYLINE:1", "layer": "ASANSOR"}
    assert sign_block(((4.4, 1.0), (6.0, 2.6)), rects=(car,))[1]["stairs"] == []   # a car and one diagonal: a lift



def test_tread_lines_of_the_sheets_stage_make_the_box_the_stair():
    b = block()
    run_poly = Polygon([[4.6, 1.0], [5.8, 1.0], [5.8, 2.4], [4.6, 2.4]])
    rec = run(b, texts={}, strokes={"L0": [{"polygon": run_poly, "lines": 6, "pitch_m": 0.27}]})
    assert [s["how"] for s in rec["stairs"]] == ["stroke box"] and "6 tread lines" in rec["stairs"][0]["reason"]


def test_a_box_over_the_lifts_or_holding_a_lift_word_is_never_the_stair():
    b = block(storeys=2)
    for s in b["symbols"]:
        s["footprint"] = {"center": [7.2, 7.0], "size": [1.4, 2.5], "rotation_deg": 0.0}   # over the lift box
    texts = {s["level_id"]: [{"text": str(i), "x": 7.2, "y": 5.9 + 0.1 * i} for i in range(1, 17)] for s in b["symbols"]}
    assert run(b, texts=texts)["stairs"] == []
    b = block(storeys=2)
    texts = treads(b)
    texts["L0"].append({"text": "ŞAFT", "x": 5.2, "y": 3.0})
    assert run(b, texts=texts)["stairs"] == []


def test_a_one_storey_house_needs_no_stair():
    b = block(storeys=1)
    b["rooms"] = [r for r in b["rooms"] if r["room_type"] != "shaft" and r["id"] != "r_L0_ek"]
    assert not CR.needs_stair(b)
    assert run(b)["stairs"] == []






def test_a_copy_of_a_typical_floor_takes_its_floors_stair_and_the_top_storey_none():
    b = block(storeys=3)
    for lv in b["levels"][1:]:
        lv["typical_of"] = "L0"
    b["symbols"] = [s for s in b["symbols"] if s["level_id"] == "L0"]
    b["slabs"] = [{"id": f"sl_L{k}", "below_level_id": f"L{k - 1}", "above_level_id": f"L{k}", "openings": []}
                  for k in (1, 2)]
    rec = run(b)
    assert [(s["level_id"], s["how"]) for s in rec["stairs"]] == [("L0", "stroke box"), ("L1", "typical copy")]
    assert all(s["openings"] for s in b["slabs"])






def test_a_lift_door_mark_outside_the_shaft_wall_is_undone():
    """R19/R16: an opening marked the lift's door (by the older reach test) that lies in no shaft wall loses the mark; a
    derived gap is an opening again (real10 o_L0_019)."""
    b = block(storeys=1)
    b["rooms"].append(room("r_L0_ek2", "Mutfak", "kitchen", rect(0.1, 0.1, 1.0, 1.0), "L0"))
    b["openings"].append({"id": "o_L0_far", "type": "door", "level_id": "L0", "wall_id": "w_L0_k", "center": [10.0, 4.0],
                          "width": 1.0, "operation": "sliding", "lift_door": True,
                          "evidence": [{"method": "derived"}, {"method": "inferred", "rule": "lift_door"}]})
    rec = run(b)
    o = next(x for x in b["openings"] if x["id"] == "o_L0_far")
    assert [u["opening"] for u in rec["lift_doors"]["unmarked"]] == ["o_L0_far"]
    assert o["lift_door"] is False and o["type"] == "opening" and o["adjusted_by_ai"]["rule"] == "lift_door_unmark"


def test_a_pit_level_gets_no_landing_door_and_a_machine_room_is_no_lift():
    b = block(storeys=1)
    b["rooms"].append(room("r_L0_ek2", "Mutfak", "kitchen", rect(0.1, 0.1, 1.0, 1.0), "L0"))
    next(r for r in b["rooms"] if r["id"] == "r_L0_lift")["label"] = "Asansör Kuyusu"
    assert run(b)["lift_doors"]["added"] == []
    lift = {"label": "Asansör", "polygon": rect(0, 0, 1.6, 1.8)}
    assert CP.is_lift(lift) and CP.is_lift(dict(lift, label="Makine Dairesiz Asansör"))
    for label in ("Asansör Makn.dairesi", "Asansör Holü", "Araç Asansörü", "ASANSÖR ÖNÜ"):
        assert not CP.is_lift(dict(lift, label=label)), label
    assert not CP.is_lift(dict(lift, polygon=rect(0, 0, 4.0, 4.0)))          # a 16 m2 face: the whole core
    assert not CP.is_lift(dict(lift, label="Elek.şoh. Asansör", polygon=rect(0, 0, 0.5, 0.6)))


def test_a_lift_door_onto_the_hall_stays():
    b = block()
    b["openings"].append({"id": "d_L0_land", "type": "door", "level_id": "L0", "wall_id": "w_L0_l2",
                          "center": [6.4, 7.0], "width": 0.9})
    rec = run(b)
    assert "d_L0_land" not in {r["opening"] for r in rec["lift_doors"]["removed"]}
    assert not [o for o in b["openings"] if o["level_id"] == "L0" and o.get("inference", {}).get("rule") == "lift_door"]


def test_a_flat_meets_the_core_only_through_its_door():
    b = flat_door(block())
    rec = run(b)
    assert {g["opening"] for g in rec["core_gaps"]} == {"o_L0_gap", "o_L1_gap"}
    assert "d_L0_flat" in {o["id"] for o in b["openings"]}
    assert not rules(b, "core_gap")


def test_an_open_plan_flats_only_link_stays_and_a_bedroom_gap_never():
    """G4: a kitchen or living room may be a flat's only, open-plan, entrance; a bedroom never opens onto the core."""
    b = block()
    b["openings"].append({"id": "o_L0_bed", "type": "opening", "level_id": "L0", "wall_id": "w_L0_8",
                          "center": [8.0, 3.3], "width": 0.8})
    rec = run(b)
    assert {g["opening"] for g in rec["core_gaps"]} == {"o_L0_bed"}
    assert {"o_L0_gap", "o_L1_gap"} <= {o["id"] for o in b["openings"]}
    assert not [f for f in rules(b, "core_gap") if "o_L0_gap" in f["element_ids"]]


def test_a_house_pair_with_no_lift_and_no_common_hall_has_no_common_core():
    """R16 G1/G2: two kitchens alone make no common core (real02/real04, twin villas with a stair each); a drawn
    common-hall word or a lift does."""
    b = block()
    b["rooms"] = [r for r in b["rooms"] if r["room_type"] != "shaft"]
    assert CR.several_flats(b) and CR.common_core(b) is None and not CR.flat_core(b)
    rec = run(flat_door(b))
    assert rec["core_gaps"] == [] and not rules(b, "core_door", "core_gap")
    next(r for r in b["rooms"] if r["id"] == "r_L0_hall").update(label="Kat Holü", label_raw="KAT HOLÜ")
    assert CR.common_core(b) and CR.flat_core(b)
    inferred = dict(next(r for r in b["rooms"] if r["id"] == "r_L0_hall"), label_raw=None,
                    label_inferred={"method": "shared_hall"})
    assert CR.common_core({"rooms": [inferred]}) is None              # an inferred common label is no evidence


def test_a_drawn_door_from_a_bedroom_into_the_core_is_a_finding():
    """RC14 core_door (R16): the east bedroom's drawn door opens straight into the core hall."""
    b = block()
    assert [f["element_ids"][0] for f in rules(b, "core_door") if f["level_id"] == "L0"] == ["d_L0_flat"]
    next(r for r in b["rooms"] if r["id"] == "r_L0_east")["room_type"] = "hall"          # an antre: the flat's own hall
    assert not [f for f in rules(b, "core_door") if f["level_id"] == "L0"]


def test_a_flats_garden_door_stays_and_the_core_still_gets_the_entrance():
    b = block()
    rec = run(b)
    added = rec["entrances"]["added"]
    assert rec["entrances"]["refused"] == [] and len(added) == 1
    # 13 Nov 2026 (review CS1-05): the inferred entrance enters site.entrances with its threshold and steps
    assert [e["door_id"] for e in b["site"]["entrances"]] == ["d_L0_out", added[0]["door"]]
    ent = b["site"]["entrances"][-1]
    assert ent["inferred"] and ent["room_id"] == "r_L0_hall" and ent["rise"] == 0.0 and ent["main"]


def test_a_door_from_a_wet_room_is_no_entrance_and_the_core_gets_one():
    b = block()
    next(r for r in b["rooms"] if r["id"] == "r_L0_east")["room_type"] = "bathroom"
    rec = run(b)
    assert [r["door"] for r in rec["entrances"]["refused"]] == ["d_L0_out"]
    added = rec["entrances"]["added"]
    assert [e["door_id"] for e in b["site"]["entrances"]] == [added[0]["door"]]
    assert len(added) == 1 and added[0]["level_id"] == "L0"
    door = next(o for o in b["openings"] if o["id"] == added[0]["door"])
    assert door["wall_id"] == "w_L0_s" and door["inference"]["rule"] == "inferred_entrance"


def test_an_entrance_whose_far_side_holds_a_lost_room_label_is_refused():
    b = block(storeys=1)
    b["rooms"] = [r for r in b["rooms"] if r["room_type"] != "shaft"]
    b["levels"][0]["reading_places"] = [{"kind": "unplaced_label", "text": "SALON", "at": [12.8, 2.2]}]
    rec = run(b)
    assert [r["door"] for r in rec["entrances"]["refused"]] == ["d_L0_out"]
    assert "SALON" in rec["entrances"]["refused"][0]["reason"]


def test_the_same_box_read_twice_is_one_box():
    """real21 reads its stair box five times (sy_L0_001 to 005 at one place): one box, so tier b still holds."""
    b = block()
    for s in b["symbols"]:
        s["footprint"] = {"center": [5.2, 3.0], "size": [2.0, 4.6], "rotation_deg": 0.0}
    b["symbols"].append(dict(b["symbols"][0], id="sy_L0_002"))
    b["level_inference"]["storeys"] = {"areas": {"typical": {"value": 96.0}}}
    rec = CR.apply(SimpleNamespace(building=b, ids=B.IdCounter(), warn=lambda *_: None), {}, {}, None,
                   {"L0": sign_drawing(((5.0, 1.0), (5.0, 5.0)))})
    assert [s["how"] for s in rec["stairs"]] == ["stair signs"]
