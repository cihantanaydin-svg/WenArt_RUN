"""12 Nov 2026 (the architect's audit of 8 buildings, second series; user: "Make sense of the building", "This is for all
the projects"): ``wenart.ingest.sense_rules`` on small hand-made buildings (no project data).

What: the exterior flag follows the building outline (a partition flagged exterior becomes interior, an outer wall
flagged interior becomes exterior, a free-standing wall keeps its flag); a stair whose storey above does not cover it
is not built upward and loses its void, one under the storey above stays; a small face holding a shaft word is a shaft
with its void through the storeys; a balcony reached only through a window gets that window as its door, one with no
opening gets an inferred door, one with a door is left alone.
"""
from __future__ import annotations

from shapely.geometry import Polygon

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
    b = building(flat())
    b["walls"].append(wall("w_L0_free", (12, 0), (12, 6)))            # a free-standing wall keeps its flag
    changes = {c["wall"]: c["exterior"] for c in SR.exterior_flags(b)}
    assert changes == {"w_L0_3": True, "w_L0_5": False}
    w5 = next(w for w in b["walls"] if w["id"] == "w_L0_5")
    assert w5["exterior"] is False and w5["drawn_exterior"] is True and w5["adjusted_by_ai"]["rule"]
    assert next(w for w in b["walls"] if w["id"] == "w_L0_free")["exterior"] is True


def test_a_wall_onto_a_terrace_inside_the_outline_stays_interior():
    """R14: a terrace (an open-air room) inside the level's outline is one of its rooms (synthetic-07's attic)."""
    b = building(flat())
    b["walls"] += [wall("w_L0_t1", (10, 6), (10, 9)), wall("w_L0_t2", (10, 9), (0, 9)), wall("w_L0_t3", (0, 9), (0, 6))]
    b["rooms"].append(room("r_L0_teras", "Teras", "balcony", rect(0.1, 6.1, 9.9, 8.9)))
    changes = {c["wall"]: c["exterior"] for c in SR.exterior_flags(b)}
    assert "w_L0_3" not in changes and changes.get("w_L0_5") is False


def test_a_wall_partly_on_the_outline_keeps_its_drawn_flag():
    """The north wall meets a room over its west half and the outside over its east half: no clear side, the drawn
    flag stays (its stretches are not split yet)."""
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


def test_a_balcony_reached_only_through_a_window_gets_that_window_as_its_door():
    b = building(flat(), site=balcony_site())
    b["openings"].append({"id": "win_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.6, "height": 1.4, "sill_height": 0.9})
    rec = SR.balcony_doors(b, B.IdCounter().next)
    win = next(o for o in b["openings"] if o["id"] == "win_1")
    assert rec[0]["how"] == "window to door" and win["type"] == "door" and win["drawn_type"] == "window"
    assert win["sill_height"] is None and win["height"] >= 2.1


def test_a_service_balcony_reached_through_its_window_keeps_the_window():
    b = building(flat(), site={"outdoor_spaces": [{"id": "os_ac", "kind": "balcony", "level_id": "L0",
                                                   "polygon": rect(5.2, 6.1, 9.8, 7.0)}]})          # 0.9 m deep
    b["openings"].append({"id": "win_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_3",
                          "center": [7.5, 6.0], "width": 1.6, "height": 1.4, "sill_height": 0.9})
    rec = SR.balcony_doors(b, B.IdCounter().next)
    assert rec[0]["how"] == "service balcony" and rec[0]["opening"] is None
    assert next(o for o in b["openings"] if o["id"] == "win_1")["type"] == "window"


def test_a_balcony_with_no_opening_gets_an_inferred_door_and_one_with_a_door_none():
    b = building(flat(), site=balcony_site())
    rec = SR.balcony_doors(b, B.IdCounter().next)
    assert rec and rec[0]["how"] == "inferred door"
    again = SR.balcony_doors(b, B.IdCounter().next)
    assert again == []
