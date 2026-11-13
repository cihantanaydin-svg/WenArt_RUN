"""12 Nov 2026 (the architect's audit of 8 buildings, second series; user: "Make sense of the building", "This is for all
the projects"): ``wenart.ingest.sense_rules`` on small hand-made buildings (no project data).

What (the exterior flags moved to ``wenart.ingest.exterior``, tests/test_exterior_facades_20261112.py): a stair whose storey above does not cover it
is not built upward and loses its void, one under the storey above stays; a small face holding a shaft word is a shaft
with its void through the storeys; a balcony reached only through a window gets that window as its door, one with no
opening gets an inferred door, one with a door is left alone.
"""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart.ingest import sense_rules as SR


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level="L0"):
    return {"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
            "area_computed": round(Polygon(poly).area, 3)}


def wall(wid, a, b, level="L0", t=0.2, exterior=True):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def flat(level="L0", order=0, w=10.0):
    """A w x 6 m flat: a bedroom (west) and a living room (east) with a door between them."""
    walls = [wall(f"w_{level}_1", (0, 0), (w, 0), level), wall(f"w_{level}_2", (w, 0), (w, 6), level),
             wall(f"w_{level}_3", (w, 6), (0, 6), level, exterior=False), wall(f"w_{level}_4", (0, 6), (0, 0), level),
             wall(f"w_{level}_5", (w / 2, 0), (w / 2, 6), level, exterior=True)]
    rooms = [room(f"r_{level}_oda", "Oda", "bedroom", rect(0.1, 0.1, w / 2 - 0.1, 5.9), level),
             room(f"r_{level}_living", "Salon", "living", rect(w / 2 + 0.1, 0.1, w - 0.1, 5.9), level)]
    ops = [{"id": f"d_{level}_001", "type": "door", "level_id": level, "wall_id": f"w_{level}_5",
            "center": [w / 2, 3.0], "width": 0.9}]
    lv = {"id": level, "label": f"{order}. Kat", "order": order, "elevation": 3.0 * order, "ceiling_height": 2.7}
    return lv, walls, rooms, ops


def building(*parts, site=None):
    b = {"levels": [], "walls": [], "rooms": [], "openings": [], "furniture": [], "slabs": [], "warnings": [],
         "site": site or {}, "level_inference": {}}
    for lv, w, rooms, ops in parts:
        b["levels"].append(lv)
        b["walls"] += w
        b["rooms"] += rooms
        b["openings"] += ops
    return b


def test_the_exterior_flag_follows_the_building_outline():
    """The stage-1 rule (the staged per-stretch rule exterior_spans is off until its review, 13 Nov 2026)."""
    b = building(flat())
    b["walls"].append(wall("w_L0_free", (12, 0), (12, 6)))            # a free-standing wall keeps its flag
    changes = {c["wall"]: c["exterior"] for c in SR.exterior_flags(b)}
    assert changes == {"w_L0_3": True, "w_L0_5": False}
    w5 = next(w for w in b["walls"] if w["id"] == "w_L0_5")
    assert w5["exterior"] is False and w5["drawn_exterior"] is True and w5["adjusted_by_ai"]["rule"]
    assert next(w for w in b["walls"] if w["id"] == "w_L0_free")["exterior"] is True


def test_a_wall_onto_a_terrace_inside_the_outline_keeps_its_drawn_flag():
    """Review MF8: an open-air room inside the outline is unknown, never a room: the drawn flag stays either way."""
    b = building(flat())
    b["walls"] += [wall("w_L0_t1", (10, 6), (10, 9)), wall("w_L0_t2", (10, 9), (0, 9)), wall("w_L0_t3", (0, 9), (0, 6))]
    b["rooms"].append(room("r_L0_teras", "Teras", "balcony", rect(0.1, 6.1, 9.9, 8.9)))
    changes = {c["wall"]: c["exterior"] for c in SR.exterior_flags(b)}
    assert "w_L0_3" not in changes and changes.get("w_L0_5") is False
    next(w for w in b["walls"] if w["id"] == "w_L0_3")["exterior"] = True
    assert "w_L0_3" not in {c["wall"] for c in SR.exterior_flags(b)}


def test_a_wall_onto_a_light_well_is_exterior():
    """Review POD-07: a light well is open air for the flags as for the windows (one definition, the amended R14)."""
    b = building(flat())
    b["walls"] += [wall("w_L0_t1", (10, 6), (10, 8)), wall("w_L0_t2", (10, 8), (0, 8)), wall("w_L0_t3", (0, 8), (0, 6))]
    b["rooms"].append(room("r_L0_lw", "Aydınlık", "shaft", rect(0.1, 6.1, 9.9, 7.9)))
    changes = {c["wall"]: c["exterior"] for c in SR.exterior_flags(b)}
    assert changes.get("w_L0_3") is True


def test_a_wall_partly_on_the_outline_keeps_its_drawn_flag():
    b = building(flat())
    b["walls"] += [wall("w_L0_n1", (0, 6), (0, 9)), wall("w_L0_n2", (0, 9), (5, 9)), wall("w_L0_n3", (5, 9), (5, 6))]
    b["rooms"].append(room("r_L0_oda2", "Oda", "bedroom", rect(0.1, 6.1, 4.9, 8.9)))
    changes = {c["wall"]: c["exterior"] for c in SR.exterior_flags(b)}
    assert "w_L0_3" not in changes and next(w for w in b["walls"] if w["id"] == "w_L0_3")["exterior"] is False


def test_a_stair_with_no_storey_over_it_is_not_built_upward():
    b = building(flat("L0", 0, 10.0), flat("L1", 1, 5.0))              # the upper storey covers the west half only
    b["furniture"] = [
        {"id": "f_east", "level_id": "L0", "type": "stair",
         "footprint": {"center": [8.0, 3.0], "size": [1.0, 2.5], "rotation_deg": 0.0}},
        {"id": "f_west", "level_id": "L0", "type": "stair",
         "footprint": {"center": [2.0, 3.0], "size": [1.0, 2.5], "rotation_deg": 0.0}}]
    b["slabs"] = [{"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1",
                   "openings": [{"id": "sv_1", "kind": "stair_void", "furniture_id": "f_east", "polygon": []},
                                {"id": "sv_2", "kind": "stair_void", "furniture_id": "f_west", "polygon": []}]}]
    rec = SR.stairs_over_nothing(b)
    assert [r["stair"] for r in rec] == ["f_east"]
    assert b["furniture"][0]["build"] is False and b["furniture"][1].get("build") is not False
    assert [o["id"] for o in b["slabs"][0]["openings"]] == ["sv_2"]


def test_a_small_face_holding_a_shaft_word_is_a_shaft_through_the_storeys():
    parts = []
    for k in (0, 1):
        lv, w, rooms, ops = flat(f"L{k}", k)
        rooms.append(room(f"r_L{k}_oda_9", "Oda", "unknown", rect(4.2, 5.2, 4.8, 5.8), f"L{k}"))
        parts.append((lv, w, rooms, ops))
    b = building(*parts)
    b["slabs"] = [{"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "openings": []}]
    texts = {lid: [{"text": "ŞAFT", "x": 4.5, "y": 5.5}] for lid in ("L0", "L1")}
    rec = SR.shafts(b, texts)
    assert {r["room"] for r in rec} == {"r_L0_oda_9", "r_L1_oda_9"}
    assert next(r for r in b["rooms"] if r["id"] == "r_L0_oda_9")["room_type"] == "shaft"
    assert b["slabs"][0]["openings"][0]["room_id"] == "r_L1_oda_9"
    assert SR.shafts(building(flat()), {"L0": [{"text": "SALON", "x": 7, "y": 3}]}) == []


def balcony_site():
    return {"outdoor_spaces": [{"id": "os_1", "kind": "balcony", "level_id": "L0", "polygon": rect(5.2, 6.1, 9.8, 7.4)}]}


def drawn(*arcs):
    """A drawing that holds only these arcs (``drawn_strokes.Drawn``'s query)."""
    return SimpleNamespace(arcs=lambda poly: [a for a in arcs if poly.contains(Point(a["center"]))],
                           segments=lambda poly: [])


def test_a_balcony_window_with_a_door_swing_drawn_at_its_jamb_is_the_balcony_door():
    b = building(flat(), site=balcony_site())
    b["openings"].append({"id": "win_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.6, "height": 1.4, "sill_height": 0.9})
    swing = {"center": (6.7, 6.0), "radius": 0.8, "id": "ARC:1", "layer": "kapi"}       # a pair of leaves
    rec = SR.balcony_doors(b, B.IdCounter().next, {"L0": drawn(swing)})
    win = next(o for o in b["openings"] if o["id"] == "win_1")
    assert rec[0]["how"] == "window to door" and win["type"] == "door" and win["drawn_type"] == "window"
    assert win["sill_height"] is None and win["height"] >= 2.1 and "ARC:1" in rec[0]["reason"]


def test_a_balcony_window_without_a_drawn_swing_stays_a_window():
    """The coordinator's decision (real06, real09): a window drawn with sills or glass stays a window; no door is cut
    through the drawn wall either (review POD-01): a review record."""
    b = building(flat(), site=balcony_site())
    b["openings"].append({"id": "win_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.6, "height": 1.4, "sill_height": 0.9})
    far = {"center": (2.0, 6.0), "radius": 0.9, "id": "ARC:2", "layer": "kapi"}         # another opening's swing
    n = len(b["openings"])
    rec = SR.balcony_doors(b, B.IdCounter().next, {"L0": drawn(far)})
    assert next(o for o in b["openings"] if o["id"] == "win_1")["type"] == "window"
    assert rec[0]["how"] == "review" and len(b["openings"]) == n and "win_1 has no door's swing" in rec[0]["reason"]


def test_a_service_balcony_reached_through_its_window_keeps_the_window():
    b = building(flat(), site={"outdoor_spaces": [{"id": "os_ac", "kind": "balcony", "level_id": "L0",
                                                   "polygon": rect(5.2, 6.1, 9.8, 7.0)}]})          # 0.9 m deep
    b["openings"].append({"id": "win_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.6, "height": 1.4, "sill_height": 0.9})
    rec = SR.balcony_doors(b, B.IdCounter().next)
    assert rec[0]["how"] == "service balcony" and rec[0]["opening"] is None
    assert next(o for o in b["openings"] if o["id"] == "win_1")["type"] == "window"


def test_a_balcony_with_no_opening_is_a_review_and_one_with_a_door_is_left_alone():
    """Review POD-01: a door is never cut through a solid drawn wall; a doorless gap onto the balcony is its door."""
    b = building(flat(), site=balcony_site())
    n = len(b["openings"])
    rec = SR.balcony_doors(b, B.IdCounter().next)
    assert rec and rec[0]["how"] == "review" and len(b["openings"]) == n
    b["openings"].append({"id": "o_gap", "type": "opening", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.0})
    rec = SR.balcony_doors(b, B.IdCounter().next)
    gap = next(o for o in b["openings"] if o["id"] == "o_gap")
    assert rec[0]["how"] == "opening to door" and gap["type"] == "door" and gap["drawn_type"] == "opening"
    assert SR.balcony_doors(b, B.IdCounter().next) == []


def test_a_balcony_whose_drawn_door_has_no_room_behind_keeps_its_tagged_window():
    """Review POD-01, CS1-03, MF2 (real20's shape): a door from a room the reading did not build, on a short face, opens
    onto the balcony; the tagged 140/140 bedroom window stays a window and no door is inferred."""
    b = building(flat(), site=balcony_site())
    b["walls"].append(wall("w_L0_x", (9.0, 6.0), (9.0, 7.4), exterior=False))
    b["openings"] += [{"id": "win_tag", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                       "center": [6.5, 6.0], "width": 1.4, "height": 1.4, "sill_height": 0.8},
                      {"id": "d_lost", "type": "door", "level_id": "L0", "wall_id": "w_L0_x",
                       "center": [9.0, 7.0], "width": 0.7}]
    n = len(b["openings"])
    swing = {"center": (5.8, 6.0), "radius": 1.0, "id": "ARC:5", "layer": "kapi", "ends": [(6.8, 6.0), (5.8, 7.0)]}
    rec = SR.balcony_doors(b, B.IdCounter().next, {"L0": drawn(swing)}, {"L0": [{"text": "140/140", "x": 6.5,
                                                                                  "y": 5.6}]})
    assert rec == [] and len(b["openings"]) == n
    assert next(o for o in b["openings"] if o["id"] == "win_tag")["type"] == "window"
    # without the door the tag still keeps the window (a review record, nothing changed)
    b["openings"] = [o for o in b["openings"] if o["id"] != "d_lost"]
    rec = SR.balcony_doors(b, B.IdCounter().next, {"L0": drawn(swing)}, {"L0": [{"text": "140/140", "x": 6.5,
                                                                                  "y": 5.6}]})
    assert rec[0]["how"] == "review" and "140/140" in rec[0]["reason"]
    assert next(o for o in b["openings"] if o["id"] == "win_tag")["type"] == "window"


def test_a_swing_arc_must_sweep_a_quarter():
    b = building(flat(), site=balcony_site())
    b["openings"].append({"id": "win_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.6, "height": 1.4, "sill_height": 0.9})
    tick = {"center": (6.7, 6.0), "radius": 0.8, "id": "ARC:7", "layer": "kapi",
            "ends": [(7.5, 6.0), (7.48, 6.2)]}                                       # about 14 degrees: a tick
    rec = SR.balcony_doors(b, B.IdCounter().next, {"L0": drawn(tick)})
    assert rec[0]["how"] == "review" and next(o for o in b["openings"] if o["id"] == "win_1")["type"] == "window"


def test_a_balcony_on_a_low_confidence_level_is_left_alone():
    b = building(flat(), site=balcony_site())
    b["levels"][0]["reading_confidence"] = "low"
    b["openings"].append({"id": "o_gap", "type": "opening", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.0})
    rec = SR.balcony_doors(b, B.IdCounter().next)
    assert rec[0]["how"] == "review" and next(o for o in b["openings"] if o["id"] == "o_gap")["type"] == "opening"


def test_a_stair_the_storey_above_draws_again_keeps_rising():
    """Review MF1, REG-07: the storey above draws the same stair (here 3 m off: misregistered) or is read too thinly:
    the stair keeps rising, a review record says why."""
    b = building(flat("L0", 0, 10.0), flat("L1", 1, 5.0))
    b["furniture"] = [{"id": "f_east", "level_id": "L0", "type": "stair",
                       "footprint": {"center": [8.0, 3.0], "size": [1.0, 2.5], "rotation_deg": 0.0}},
                      {"id": "f_up", "level_id": "L1", "type": "stair",
                       "footprint": {"center": [5.0, 3.0], "size": [1.1, 2.4], "rotation_deg": 0.0}}]
    rec = SR.stairs_over_nothing(b)
    assert rec[0]["kept"] and "do not register" in rec[0]["reason"] and b["furniture"][0].get("build") is not False
    b["furniture"].pop()
    b["levels"][1]["reading_places"] = [{"kind": "unplaced_label", "text": f"Oda {k}", "at": [1, 1]} for k in range(5)]
    rec = SR.stairs_over_nothing(b)
    assert rec[0]["kept"] and "room labels in no room" in rec[0]["reason"]


def test_a_stair_under_an_open_roof_terrace_that_draws_none_ends_below():
    """S1-10c: the top storey is an open roof terrace that draws no stair or stair head over the stair: it ends on its
    storey (no void in the terrace slab)."""
    b = building(flat("L0", 0, 10.0), flat("L1", 1, 10.0))
    b["levels"][1]["roof_terrace"] = True
    terrace = next(r for r in b["rooms"] if r["id"] == "r_L1_living")
    terrace.update(label="Teras", room_type="terrace")
    b["furniture"] = [{"id": "f_1", "level_id": "L0", "type": "stair",
                       "footprint": {"center": [8.0, 3.0], "size": [1.0, 2.5], "rotation_deg": 0.0}},
                      {"id": "f_2", "level_id": "L0", "type": "stair",          # under an enclosed room: a stair head
                       "footprint": {"center": [2.0, 3.0], "size": [1.0, 2.5], "rotation_deg": 0.0}}]
    b["slabs"] = [{"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1",
                   "openings": [{"id": "sv_1", "kind": "stair_void", "furniture_id": "f_1", "polygon": []},
                                {"id": "sv_2", "kind": "stair_void", "furniture_id": "f_2", "polygon": []}]}]
    rec = SR.stairs_over_nothing(b)
    assert [r["stair"] for r in rec] == ["f_1"] and b["furniture"][0]["build"] is False
    assert [o["id"] for o in b["slabs"][0]["openings"]] == ["sv_2"] and b["furniture"][1].get("build") is not False
