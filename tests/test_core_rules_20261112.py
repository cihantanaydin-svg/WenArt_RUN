"""12 Nov 2026 (the architect's audit of 8 buildings; user: "Make sense of the building", "This is for all the
projects"): the common core completed by general rules (``wenart.ingest.core_rules``) and checked (RC14).

What: a 12 x 8 m storey of a building with a lift: a west flat's bedroom, the core hall with a stroke box the reading
set aside as notation and a lift, an east flat's bedroom. The reading has no stair, the lift opens into the east
bedroom, the west bedroom opens onto the core hall through an unclassified gap, and the only "entrance" is a door from
the east bedroom. The rules: the box becomes the stair (with its slab void), the lift loses its door into the bedroom
and gets a landing door onto the hall, the gap closes, the bedroom door is no entrance and the core hall gets the
building entrance on the facade it reaches. Negatives: a house of one storey needs no stair; a lift door onto the hall
stays; a gap between two rooms of a flat stays.
"""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Polygon

from wenart import building as B
from wenart import geometry as G
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
            "width": 1.0},
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


def run(b):
    build = SimpleNamespace(building=b, ids=B.IdCounter(), warn=lambda *_: None)
    return CR.apply(build, {}, {})


NO_TRUST = {"threshold": 0.7, "rules": {r: {"findings": 10, "judged_right": 10, "precision": 1.0, "trusted": True}
                                        for r in SN.RULES}}


def rules(b, *names):
    return [f for f in SN.run(b, {}, trust=NO_TRUST) if f["rule"] in names]


def test_the_checks_see_what_the_reading_left_out():
    b = block()
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


def test_without_a_box_a_dog_leg_is_inferred_in_a_core_hall_that_holds_one():
    b = block(symbol=False)
    rec = run(b)
    assert rec["stairs"] and rec["stairs"][0]["how"] == "dog-leg"
    piece = next(f for f in b["furniture"] if f["type"] == "stair")
    assert piece["source"] == "added_by_ai"
    fp = piece["footprint"]
    assert Polygon(HALL).buffer(0.05).contains(Polygon(G.rotated_rectangle(fp["center"], fp["size"],
                                                                           fp["rotation_deg"])))


def test_a_one_storey_house_needs_no_stair():
    b = block(storeys=1)
    b["rooms"] = [r for r in b["rooms"] if r["room_type"] != "shaft" and r["id"] != "r_L0_ek"]
    assert not CR.needs_stair(b)
    assert run(b)["stairs"] == []


def test_the_lift_opens_only_onto_the_common_hall():
    b = block()
    rec = run(b)
    gone = {r["opening"] for r in rec["lift_doors"]["removed"]}
    assert {"d_L0_lift", "d_L1_lift"} <= gone
    added = [o for o in b["openings"] if o.get("inference", {}).get("rule") == "lift_door"]
    assert {o["level_id"] for o in added} == {"L0", "L1"}
    assert all(o["wall_id"].endswith("_l2") or o["wall_id"].endswith("_l1") for o in added)
    assert not rules(b, "lift_doors")


def test_the_landing_door_faces_away_from_the_counterweight():
    b = block(storeys=1)
    b["furniture"].append({"id": "f_L0_cw", "level_id": "L0", "type": "unknown", "room_id": "r_L0_lift",
                           "footprint": {"center": [7.2, 7.7], "size": [0.9, 0.3], "rotation_deg": 0.0}})
    run(b)
    door = next(o for o in b["openings"] if o.get("inference", {}).get("rule") == "lift_door")
    assert door["wall_id"] == "w_L0_l1"          # the south face, opposite the counterweight on the north


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


def test_a_lift_door_onto_the_hall_stays():
    b = block()
    b["openings"].append({"id": "d_L0_land", "type": "door", "level_id": "L0", "wall_id": "w_L0_l2",
                          "center": [6.4, 7.0], "width": 0.9})
    rec = run(b)
    assert "d_L0_land" not in {r["opening"] for r in rec["lift_doors"]["removed"]}
    assert not [o for o in b["openings"] if o["level_id"] == "L0" and o.get("inference", {}).get("rule") == "lift_door"]


def test_a_flat_meets_the_core_only_through_its_door():
    b = block()
    rec = run(b)
    assert {g["opening"] for g in rec["core_gaps"]} == {"o_L0_gap", "o_L1_gap"}
    assert "d_L0_flat" in {o["id"] for o in b["openings"]}
    assert not rules(b, "core_gap")


def test_a_flats_garden_door_stays_and_the_core_still_gets_the_entrance():
    b = block()
    rec = run(b)
    assert rec["entrances"]["refused"] == [] and [e["door_id"] for e in b["site"]["entrances"]] == ["d_L0_out"]
    assert len(rec["entrances"]["added"]) == 1


def test_a_door_from_a_wet_room_is_no_entrance_and_the_core_gets_one():
    b = block()
    next(r for r in b["rooms"] if r["id"] == "r_L0_east")["room_type"] = "bathroom"
    rec = run(b)
    assert [r["door"] for r in rec["entrances"]["refused"]] == ["d_L0_out"]
    assert b["site"]["entrances"] == []
    added = rec["entrances"]["added"]
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
