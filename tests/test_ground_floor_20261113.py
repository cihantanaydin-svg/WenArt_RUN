"""13 Nov 2026 (the coordinator after the stage-1 review; amended R10 (4) and R43; review S1-21a, S1-20b, S1-21c): the
ground floor of a block whose ground floor is not drawn, on a hand-made storey (no project data).

What: a 12 x 10 m typical floor read as the ground floor: a west and an east flat, the core (a lift and the Kat Holü)
in the middle band and the front flat's salon between the core and the north (street) facade. The footprint is drawn
as four dashed BINA strokes, 1.5 m short of the north facade (102 m2, the area table's OTURUM). The rule cuts the
storey to it (new facade wall on the footprint line, rooms and walls clipped, the north wall gone, the copies' model
rooms re-pointed), makes the salon the building's entrance hall with an inferred entrance door on the street facade
and its site.entrances record, and asks N1. Negatives: no matching outline cuts nothing; the street unknown asks.
"""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Polygon

from wenart import building as B
from wenart.blender import architect_storeys as ASTO
from wenart.ingest import ground_floor as GF


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level="L0"):
    return {"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
            "area_computed": round(Polygon(poly).area, 3)}


def wall(wid, a, b, t=0.2, exterior=False, level="L0"):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": exterior,
            "status": "verified", "evidence": [{"file": "x.dxf", "method": "vector", "confidence": 0.8}]}


def storey(level="L0"):
    walls = [wall("s", (0, 0), (12, 0), 0.25, True), wall("e", (12, 0), (12, 10), 0.25, True),
             wall("n", (12, 10), (0, 10), 0.25, True), wall("w", (0, 10), (0, 0), 0.25, True),
             wall("x4", (4, 0), (4, 10)), wall("x8", (8, 0), (8, 10)), wall("y6", (4, 6), (8, 6)),
             wall("y2", (4, 2), (6, 2)), wall("l6", (6, 0), (6, 2))]
    walls = [dict(w, id=f"w_{level}_{w['id']}", level_id=level) for w in walls]
    rooms = [room(f"r_{level}_west", "Salon", "living", rect(0.15, 0.15, 3.9, 9.85), level),
             room(f"r_{level}_lift", "Asansör", "shaft", rect(4.1, 0.15, 5.9, 1.9), level),
             room(f"r_{level}_hall", "Kat Holü", "hall", [[6.1, 0.15], [7.9, 0.15], [7.9, 5.9], [4.1, 5.9], [4.1, 2.1],
                                                           [6.1, 2.1]], level),
             room(f"r_{level}_front", "Salon", "living", rect(4.1, 6.1, 7.9, 9.85), level),
             room(f"r_{level}_east", "Salon", "living", rect(8.1, 0.15, 11.85, 9.85), level)]
    ops = [{"id": f"d_{level}_w", "type": "door", "level_id": level, "wall_id": f"w_{level}_x4", "center": [4.0, 4.0],
            "width": 0.9, "evidence": [{"method": "vector"}]},
           {"id": f"d_{level}_e", "type": "door", "level_id": level, "wall_id": f"w_{level}_x8", "center": [8.0, 4.0],
            "width": 0.9, "evidence": [{"method": "vector"}]},
           {"id": f"d_{level}_f", "type": "door", "level_id": level, "wall_id": f"w_{level}_y6", "center": [6.0, 6.0],
            "width": 0.9, "evidence": [{"method": "vector"}]},
           {"id": f"d_{level}_l", "type": "door", "level_id": level, "wall_id": f"w_{level}_y2", "center": [5.0, 2.0],
            "width": 0.9, "evidence": [{"method": "vector"}], "lift_door": True, "operation": "sliding"}]
    return walls, rooms, ops


def building():
    b = {"levels": [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "ceiling_height": 2.7},
                    {"id": "L1", "label": "1. Kat", "order": 1, "elevation": 3.0, "ceiling_height": 2.7,
                     "typical_of": "L0"}],
         "walls": [], "rooms": [], "openings": [], "furniture": [], "slabs": [], "warnings": [], "symbols": [],
         "site": {"entrances": []}, "level_inference": {}}
    for lid in ("L0", "L1"):
        w, r, o = storey(lid)
        b["walls"] += w
        b["rooms"] += r
        b["openings"] += o
    for r in b["rooms"]:
        if r["level_id"] == "L1":
            r["same_as"] = r["id"].replace("L1", "L0")
    b["slabs"] = [{"id": "sl_L0", "below_level_id": None, "above_level_id": "L0", "outline": rect(0, 0, 12, 10)}]
    b["furniture"] = [{"id": "f_sofa", "level_id": "L0", "room_id": "r_L0_front", "type": "sofa",
                       "footprint": {"center": [6.0, 9.3], "size": [2.0, 0.9], "rotation_deg": 0.0}}]
    return b


def drawn(*lines, layer="BINA_CAMITURBE", linetype="HIDDEN"):
    strokes = [SimpleNamespace(id=f"LINE:{k}", pts=list(pts), closed=False, layer=layer, linetype=linetype, arc=None)
               for k, pts in enumerate(lines)]
    return SimpleNamespace(strokes=strokes, m6=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])


FOOT = [((0, 0), (12, 0)), ((12, 0), (12.0, 8.5)), ((12.05, 8.5), (0, 8.5)), ((0, 8.45), (0, 0.05))]
CANT = {"cantilevers": {"ground_m2": 102.0, "typical_m2": 120.0, "reason": "footprint smaller"}}
STREET = [{"kind": "street", "text": "Kalem Sokağı", "at": [6.0, 13.0]}]


def run(b, d, side=STREET, rec=CANT):
    build = SimpleNamespace(building=b, ids=B.IdCounter(), warn=lambda *_: None)
    return GF.apply(build, b["levels"][0], rec, [], d, side)


def test_the_ground_floor_is_cut_to_the_drawn_footprint():
    b = building()
    out = run(b, drawn(*FOOT))
    assert out["footprint"]["entities"] == ["LINE:0", "LINE:1", "LINE:2", "LINE:3"]
    c = out["cut"]
    assert "w_L0_n" in c["walls_removed"] and {"w_L0_x4", "w_L0_x8", "w_L0_e", "w_L0_w"} <= set(c["walls_cut"])
    new = [w for w in b["walls"] if w["id"] in c["walls_added"]]
    assert new and all(w["inferred"] and w["exterior"] and abs(w["start"][1] - 8.375) < 0.02 for w in new)
    rooms = {r["id"]: r for r in b["rooms"]}
    assert max(y for _x, y in rooms["r_L0_west"]["polygon"]) <= 8.26 and rooms["r_L0_west"]["drawn_polygon"]
    assert max(y for _x, y in rooms["r_L1_west"]["polygon"]) > 9.8                 # the copies keep the typical floor
    assert b["slabs"][0]["outline"][2][1] == 8.5
    assert out["questions"][0]["element"] == "ground_floor"


def test_the_core_gets_an_entrance_hall_from_the_street():
    b = building()
    out = run(b, drawn(*FOOT))
    hall = out["entrance_hall"]
    assert hall["rooms"] == ["r_L0_front"] and hall["street"] == "Kalem Sokağı"
    front = next(r for r in b["rooms"] if r["id"] == "r_L0_front")
    assert front["label"] == GF.LOBBY_LABEL and front["room_type"] == "hall" and front["inferred"]
    assert front["adjusted_by_ai"]["changed"]["room_type"] == "living"
    door = next(o for o in b["openings"] if o["id"] == hall["door"])
    assert door["inference"]["rule"] == "inferred_entrance" and abs(door["center"][1] - 8.375) < 0.02
    ent = b["site"]["entrances"][-1]
    assert ent["door_id"] == door["id"] and ent["main"] and ent["room_id"] == "r_L0_front"
    assert not [f for f in b["furniture"] if f["room_id"] == "r_L0_front"]
    # the copies' salon takes the lowest copy as its model (it is no longer the ground floor's salon)
    assert "same_as" not in next(r for r in b["rooms"] if r["id"] == "r_L1_front")
    # N1 carries the two questions with the safe default 'keep'
    b["level_inference"]["storeys"] = {"count": 2, "rule": "title", "inferred": [{"level_id": "L0"}],
                                       "open_point": {"key": "N1:storeys", "default": 2, "options": [2, 3],
                                                      "severity": "minor", "question": "How many storeys?"},
                                       "ground_floor": out}
    els = [a["element"] for a in ASTO.review(b)["answers"]]
    assert els == ["storeys", "ground_floor", "entrance_hall"]


def test_no_matching_outline_cuts_nothing_and_the_street_unknown_asks():
    b = building()
    out = run(b, drawn(*FOOT[:3]))                  # the chain does not close
    assert out["footprint"] is None and out["cut"] is None
    assert out["entrance_hall"]["rooms"] == [] or out["entrance_hall"]["street"] == "Kalem Sokağı"
    b = building()
    out = run(b, drawn(*FOOT), rec={"cantilevers": {"ground_m2": 80.0, "typical_m2": 120.0, "reason": "x"}})
    assert out["footprint"] is None                 # the area is no OTURUM's
    b = building()
    out = run(b, drawn(*FOOT), side=[])
    assert out["entrance_hall"]["rooms"] == [] and "street side is not known" in out["entrance_hall"]["open"]
    assert [q["element"] for q in out["questions"]] == ["ground_floor", "entrance_hall"]


def test_a_drawn_outline_on_a_stair_layer_is_no_footprint():
    b = building()
    out = run(b, drawn(*FOOT, layer="MERDIVEN", linetype="DASHED2"))
    assert out["footprint"] is None
