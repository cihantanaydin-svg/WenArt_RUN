"""13 Nov 2026 (review S1-09b, R37; the coordinator: "find the drawn building entrance into the core if the drawing
shows one; otherwise leave the open point"): the size tags beside the openings of an outer wall decide what they are.

What: a storey with a hall (Kat Holü) and a bedroom on the street facade. The bedroom's outer 'door' carries the tag
P:120/150 (a window: 120 wide, 150 high) and the levels model chose it as the main entrance; the hall's doorless gap
carries K:100/210 and K:50/210 (a double door, 1.5 m). The rule makes the bedroom's door a window (its entrance record
dropped), the hall's gap the double entrance door with its site.entrances record, and that door the main entrance. A
gap into a flat's antre keeps its type; without tags nothing changes.
"""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Polygon

from wenart import building as B
from wenart.ingest import core_rules as CR


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly):
    return {"id": rid, "level_id": "L0", "label": label, "room_type": rtype, "polygon": poly,
            "area_computed": round(Polygon(poly).area, 3)}


def wall(wid, a, b, t=0.2, exterior=True):
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def building():
    walls = [wall("s", (0, 0), (10, 0)), wall("e", (10, 0), (10, 6)), wall("n", (10, 6), (0, 6)),
             wall("w", (0, 6), (0, 0)), wall("m", (5, 0), (5, 6), exterior=False)]
    rooms = [room("r_hol", "Kat Holü", "hall", rect(0.1, 0.1, 4.9, 5.9)),
             room("r_bed", "Yatak Odası", "bedroom", rect(5.1, 0.1, 9.9, 5.9))]
    ops = [{"id": "o_gap", "type": "opening", "level_id": "L0", "wall_id": "s", "center": [2.5, 0.0], "width": 1.5,
            "evidence": [{"method": "derived"}]},
           {"id": "d_bed", "type": "door", "level_id": "L0", "wall_id": "s", "center": [7.5, 0.0], "width": 1.2,
            "evidence": [{"method": "vector"}]}]
    return {"levels": [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0}], "walls": walls,
            "rooms": rooms, "openings": ops, "furniture": [],
            "site": {"entrances": [{"door_id": "d_bed", "level_id": "L0", "room_id": "r_bed", "rise": 0.0,
                                    "main": True, "face": [7.5, -0.1], "outward": [0.0, -1.0]}]},
            "level_inference": {}}


TEXTS = {"L0": [{"text": "P:120/150", "x": 7.6, "y": -0.4}, {"text": "K:100/210", "x": 3.0, "y": 0.5},
                {"text": "K:50/210", "x": 1.9, "y": 0.5}]}


def test_tagged_outer_openings_are_what_their_tags_say_and_the_gap_is_the_main_entrance():
    b = building()
    rec = CR.fix_entrances(b, B.IdCounter().next, {}, TEXTS)
    ops = {o["id"]: o for o in b["openings"]}
    assert ops["d_bed"]["type"] == "window" and ops["d_bed"]["drawn_type"] == "door"
    assert ops["d_bed"]["height"] == 1.5 and ops["d_bed"]["sill_height"] == 0.7
    assert ops["o_gap"]["type"] == "door" and ops["o_gap"]["operation"] == "double"
    assert ops["o_gap"]["door_tags"] == ["K:100/210", "K:50/210"]
    ents = b["site"]["entrances"]
    assert [e["door_id"] for e in ents] == ["o_gap"] and ents[0]["main"] and ents[0]["drawn"]
    assert [w["opening"] for w in rec["windows"]] == ["d_bed"] and rec["main"]["now"] == "o_gap"


def test_a_gap_into_a_flats_antre_and_untagged_openings_stay():
    b = building()
    b["rooms"][0].update(label="Antre")
    CR.fix_entrances(b, B.IdCounter().next, {}, TEXTS)
    assert next(o for o in b["openings"] if o["id"] == "o_gap")["type"] == "opening"
    b = building()
    rec = CR.fix_entrances(b, B.IdCounter().next, {}, {"L0": []})
    assert [o["type"] for o in b["openings"]] == ["opening", "door"]
    # no drawn entrance found: the bedroom's door is no main entrance, the open point stays (S1-09b)
    assert not SimpleNamespace(**b["site"]["entrances"][0]).main and rec["open"]
