"""12 Nov 2026 (stage 2 of the building-sense audit, with the misfire hunters' amendments and the coordinator's
decisions): exterior per stretch of wall (R14, ``wenart.ingest.exterior``), the facades of a storey (R45 notes, R24
buried or exposed, R46 plot line and internal party wall: ``wenart.ingest.facades``) and no eaves over a party side
(``wenart.blender.party_eaves``), on small hand-made buildings (no project data).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from shapely.geometry import Polygon

from wenart.blender import party_eaves as PE
from wenart.ingest import completion as CP
from wenart.ingest import exterior as EX
from wenart.ingest import facades as FC
from wenart.ingest import rule_guards as RG


@pytest.fixture(autouse=True)
def _staged_rules_on(monkeypatch):
    """The stage-2 rules are staged (off until their review, 13 Nov 2026): these tests switch them on."""
    monkeypatch.setenv("WENART_RULES_ON", ",".join(sorted(RG.STAGED)))


def test_the_staged_rules_are_off_unless_switched_on(monkeypatch):
    monkeypatch.delenv("WENART_RULES_ON", raising=False)
    b = {"level_inference": {}}
    assert all(not RG.active(k, b) for k in RG.STAGED)
    assert "staged" in RG.switched_off("party_eaves", b)
    assert RG.active("party_eaves", {"project": {"brief": {"rules_on": ["party_eaves"]}}})
    assert RG.active("party_refuse", {"level_inference": {"rules_on": "party_refuse"}})
    assert not RG.active("core_gap", {"project": {"brief": {"rules_off": "R16"}}})
    # the build follows the reading's record (it imports no reading code)
    ring = [[0, 0], [10, 0], [10, 6], [0, 6]]
    b = {"walls": [{"id": "w", "level_id": "L0", "start": [10, 0], "end": [10, 6], "thickness": 0.2,
                    "party_wall": {"inferred": True}}], "level_inference": {"rules_staged": {"party_eaves": False}}}
    assert PE.clip(ring, b, "L0") == (ring, [])


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level="L0", **kw):
    return dict({"id": rid, "level_id": level, "label": label, "label_raw": label, "room_type": rtype,
                 "polygon": poly, "area_computed": round(Polygon(poly).area, 3)}, **kw)


def wall(wid, a, b, level="L0", t=0.25, exterior=True, **kw):
    return dict({"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t,
                 "exterior": exterior}, **kw)


def flat(level="L0", order=0, elevation=0.0):
    """A 10 x 6 m flat: a bedroom (west) and a living room (east); the partition w_5 is flagged exterior and the north
    wall w_3 interior (the reading's whole-wall flags)."""
    walls = [wall(f"w_{level}_1", (0, 0), (10, 0), level), wall(f"w_{level}_2", (10, 0), (10, 6), level),
             wall(f"w_{level}_3", (10, 6), (0, 6), level, exterior=False), wall(f"w_{level}_4", (0, 6), (0, 0), level),
             wall(f"w_{level}_5", (5, 0), (5, 6), level, t=0.1)]
    rooms = [room(f"r_{level}_oda", "Oda", "bedroom", rect(0.15, 0.15, 4.95, 5.85), level),
             room(f"r_{level}_salon", "Salon", "living", rect(5.05, 0.15, 9.85, 5.85), level)]
    ops = [{"id": f"d_{level}_1", "type": "door", "level_id": level, "wall_id": f"w_{level}_5", "center": [5.0, 3.0],
            "width": 0.9}]
    lv = {"id": level, "label": f"{order}. Kat", "order": order, "elevation": elevation, "ceiling_height": 2.7,
          "kind": "basement" if order < 0 else "floor"}
    return lv, walls, rooms, ops


def building(*parts, site=None, roof=None):
    b = {"levels": [], "walls": [], "rooms": [], "openings": [], "furniture": [], "slabs": [], "warnings": [],
         "site": site or {}, "level_inference": {}, "roof": roof}
    for lv, w, rooms, ops in parts:
        b["levels"].append(lv)
        b["walls"] += w
        b["rooms"] += rooms
        b["openings"] += ops
    return b


def run_ext(b, texts=None):
    build = SimpleNamespace(building=b, warn=lambda *_: None)
    rec = EX.apply(build, texts or {})
    b["level_inference"]["exterior"] = rec
    return rec, {w["id"]: w for w in b["walls"]}


# ------------------------------------------------------------------------------------------------------------ R14
def test_the_flags_follow_the_walls_faces_and_the_stretches_are_kept():
    b = building(flat())
    rec, walls = run_ext(b)
    assert walls["w_L0_5"]["exterior"] is False and walls["w_L0_5"]["drawn_exterior"] is True
    assert walls["w_L0_3"]["exterior"] is True and {s["kind"] for s in walls["w_L0_3"]["exterior_spans"]} == {"exterior"}
    assert walls["w_L0_5"]["exterior_spans"][0]["kind"] == "interior"
    assert {c["wall"] for c in rec["changed"]} == {"w_L0_3", "w_L0_5"}


def test_a_wall_partly_on_the_outline_is_exterior_on_that_stretch_only():
    """R14: the wall record stays whole; its stretches: exterior along the outside, interior between rooms."""
    b = building(flat())
    b["walls"] += [wall("w_L0_n1", (0, 6), (0, 9)), wall("w_L0_n2", (0, 9), (5, 9)), wall("w_L0_n3", (5, 9), (5, 6))]
    b["rooms"].append(room("r_L0_oda2", "Oda", "bedroom", rect(0.15, 6.15, 4.85, 8.85)))
    _, walls = run_ext(b)
    kinds = [(s["kind"], s["t0"] < 5.0) for s in walls["w_L0_3"]["exterior_spans"]]
    assert ("exterior", True) in kinds and any(k == "interior" for k, _ in kinds)
    assert walls["w_L0_3"]["exterior"] is True                 # any stretch exterior


def terrace_building(outer_t=0.25, roof=None):
    lv, walls, rooms, ops = flat()
    walls += [wall("w_L0_t1", (10, 6), (10, 9), t=outer_t), wall("w_L0_t2", (10, 9), (0, 9), t=outer_t),
              wall("w_L0_t3", (0, 9), (0, 6), t=outer_t)]
    rooms.append(room("r_L0_teras", "Teras", "balcony", rect(0.15, 6.15, 9.85, 8.85)))
    return building((lv, walls, rooms, ops), roof=roof)


def test_an_enclosed_terrace_is_a_room_and_one_with_a_parapet_or_outside_the_roof_is_outdoor():
    """The coordinator's decision of 12 Nov 2026 (synthetic-07's attic Teras keeps its truth)."""
    _, walls = run_ext(terrace_building())
    assert walls["w_L0_3"]["exterior"] is False                # between the flat and an enclosed terrace
    _, walls = run_ext(terrace_building(outer_t=0.1))          # thin outer walls: a parapet, the terrace is open
    assert walls["w_L0_3"]["exterior"] is True
    roof = {"over_level_id": "L0", "outline": rect(-0.5, -0.5, 10.5, 6.2)}   # the roof stops before the terrace
    _, walls = run_ext(terrace_building(roof=roof))
    assert walls["w_L0_3"]["exterior"] is True


def test_a_stretch_facing_a_lost_room_label_is_unknown():
    """The east half of the north wall faces the lost label SALON: unknown (no inferred opening); the west half not."""
    b = building(flat())
    b["levels"][0]["reading_places"] = [{"kind": "unplaced_label", "text": "SALON", "at": [7.5, 8.0]}]
    _, walls = run_ext(b)
    spans = walls["w_L0_3"]["exterior_spans"]                  # the wall runs from x 10 to x 0
    assert spans[0]["kind"] == "unknown" and spans[0].get("label") == "SALON"
    assert not EX.allows(walls["w_L0_3"], 0.5, 4.5) and EX.allows(walls["w_L0_3"], 5.5, 9.5)


def test_a_level_whose_rooms_cover_little_does_not_qualify_and_takes_no_window():
    b = building(flat())
    b["rooms"] = [r for r in b["rooms"] if r["id"] != "r_L0_salon"]     # rooms cover under 60 % of the outline
    rec, walls = run_ext(b)
    assert "L0" in rec["not_qualified"] and walls["w_L0_5"]["exterior"] is True     # the flag stays
    go, why = CP.window_decision(b, b["levels"][0], 0, {"draws_windows": False})
    assert not go and "R14" in why


# ------------------------------------------------------------------------------------------------- R24 and R45
def facade_texts(*items):
    return [{"text": t, "x": x, "y": y, "entity": f"TEXT:{k}"} for k, (t, x, y) in enumerate(items)]


def grounds(b, lid="L0", texts=None):
    lv = next(x for x in b["levels"] if x["id"] == lid)
    level = CP.Level(b, lid, texts)
    edges = FC.edges_of(level)
    notes = FC.notes(level, edges, texts, [])
    return edges, notes, FC.ground(b, level, lv, edges, texts, notes)


def side(edges, rows, at):
    """The row of the facade nearest the point ``at`` (the outline runs on the walls' outer faces)."""
    from shapely.geometry import LineString, Point
    k = min(range(len(edges)), key=lambda i: LineString(edges[i]).distance(Point(at)))
    return rows[k]


def test_a_basement_facade_is_buried_by_soil_freed_by_an_outside_door_and_by_a_low_ground_mark():
    """R24 as verified, in its order: soil labels, then exposure (a drawn outside door, wide glazing, an entrance label,
    a ±0.00 mark at a door), then a sane terrain; a side with no evidence under the entrance storey is unknown."""
    b = building(flat("L-1", -1, -3.0), flat("L0", 0, 0.0))
    b["openings"].append({"id": "d_L-1_out", "type": "door", "level_id": "L-1", "wall_id": "w_L-1_2",
                          "center": [10.0, 3.0], "width": 0.9, "evidence": [{"method": "vector", "entity": "ARC:1"}]})
    texts = facade_texts(("TOPRAK", 5.0, -1.5), ("-2.80", 5.0, 7.5))
    edges, _, rows = grounds(b, "L-1", texts)
    south, east, north, west = (side(edges, rows, at) for at in ((5, 0), (10, 3), (5, 6), (0, 3)))
    assert south["buried"] is True and south["rung"] == "soil"
    assert east["buried"] is False and east["rung"] == "exposure" and "d_L-1_out" in east["why"]
    assert north["rung"] == "terrain" and north["buried"] is False     # -2.80 lies below the sill (-2.10)
    assert west["buried"] == "unknown" and west["rung"] == "level"


def test_a_drawn_window_or_a_bare_dolgu_decides_nothing_and_toprak_temasli_is_no_soil():
    b = building(flat("L-1", -1, -3.0), flat("L0", 0, 0.0))
    b["openings"].append({"id": "win_L-1_1", "type": "window", "level_id": "L-1", "wall_id": "w_L-1_2",
                          "center": [10.0, 3.0], "width": 1.2, "evidence": [{"method": "vector", "entity": "LINE:1"}]})
    texts = facade_texts(("TOPRAK TEMASLI DÖŞEME", 5.0, -1.5), ("DOLGU", 5.0, 7.5))
    edges, _, rows = grounds(b, "L-1", texts)
    assert {r["buried"] for r in rows} == {"unknown"}


def test_the_terrain_never_buries_the_entrance_storey_nor_two_storeys():
    b = building(flat("L-1", -1, -3.0), flat("L0", 0, 0.0), flat("L1", 1, 3.0))
    edges, _, rows = grounds(b, "L0", facade_texts(("+2.90", 5.0, 7.5)))
    north = side(edges, rows, (5, 6))
    assert north["buried"] is False and north["rung"] == "terrain_rejected"
    edges, _, rows = grounds(b, "L-1", facade_texts(("+2.90", 5.0, 7.5)))     # would bury L-1 and L0
    assert side(edges, rows, (5, 6))["buried"] == "unknown"


def test_the_entrance_storey_is_the_lowest_with_a_building_entrance_phrase():
    b = building(flat("L-1", -1, -3.0), flat("L0", 0, 0.0))
    texts = {"L-1": facade_texts(("DAİRE GİRİŞİ", 2.0, 2.0)), "L0": facade_texts(("BİNA GİRİŞİ", 2.0, 2.0))}
    assert FC.entrance_storey(b, texts) == "L0"
    assert FC.entrance_storey(b, {"L-1": facade_texts(("DAİRE GİRİŞİ", 2.0, 2.0))}) is None


def test_a_ground_within_0_3_m_of_the_next_floor_counts_as_above_the_ceiling():
    b = building(flat("L-1", -1, -3.0), flat("L0", 0, 0.0))
    edges, _, rows = grounds(b, "L-1", facade_texts(("-0.25", 5.0, 7.5)))
    north = side(edges, rows, (5, 6))
    assert north["buried"] is True and north["rung"] == "terrain"


def test_margin_notes_belong_to_the_facade_they_face():
    b = building(flat())
    texts = facade_texts(("Kalem Sokağı", 5.0, -1.2), ("BAHÇE", 11.5, 3.0), ("ARKA CEPHE", 5.0, 7.0),
                         ("AYRIK", -1.0, 3.0), ("Kalem Sokağı", 5.0, -9.0))
    edges, notes, _ = grounds(b, texts=texts)
    assert side(edges, notes, (5, 0)) == {"street": "Kalem Sokağı"}
    assert side(edges, notes, (10, 3)) == {"garden": "BAHÇE"} and side(edges, notes, (5, 6)) == {"front": "ARKA CEPHE"}
    assert side(edges, notes, (0, 3)) == {"free": "AYRIK"}


# ------------------------------------------------------------------------------------------------------------ R46
def test_a_facade_on_a_plot_edge_with_a_neighbour_parcel_behind_it_is_a_party_facade():
    b = building(flat(), site={"plot": {"polygon": rect(-0.05, -6.0, 14.0, 14.0)}})
    level = CP.Level(b, "L0")
    edges = FC.edges_of(level)
    found = FC.plot_party(b, level, edges, facade_texts(("125 PARSEL", -3.0, 3.0)))
    assert [edges[i] for i in found] == [e for e in edges if abs(e[0][0] + 0.125) < 1e-6 and abs(e[1][0] + 0.125) < 1e-6]
    assert FC.plot_party(b, level, edges, facade_texts(("125 PARSEL", -3.0, 3.0), ("Kalem Sokağı", -3.0, 1.0))) == {}
    assert FC.plot_party(building(flat()), level, edges, facade_texts(("125 PARSEL", -3.0, 3.0))) == {}


def house_pair(door_through=False):
    """Two 5 x 6 m houses side by side, each a kitchen, a bathroom and an outer door; the wall between them runs the
    whole depth (spans interior)."""
    walls = [wall("w_1", (0, 0), (10, 0)), wall("w_2", (10, 0), (10, 6)), wall("w_3", (10, 6), (0, 6)),
             wall("w_4", (0, 6), (0, 0)), wall("w_mid", (5, 0), (5, 6), exterior=False),
             wall("w_a", (0, 3), (5, 3), t=0.1, exterior=False), wall("w_b", (5, 3), (10, 3), t=0.1, exterior=False)]
    rooms = [room("r_k1", "Mutfak", "kitchen", rect(0.15, 0.15, 4.9, 2.95)), room("r_b1", "Banyo", "bathroom",
                                                                                   rect(0.15, 3.05, 4.9, 5.85)),
             room("r_k2", "Mutfak", "kitchen", rect(5.1, 0.15, 9.85, 2.95)), room("r_b2", "Banyo", "bathroom",
                                                                                   rect(5.1, 3.05, 9.85, 5.85))]
    ops = [{"id": "d_1", "type": "door", "level_id": "L0", "wall_id": "w_1", "center": [2.5, 0.0], "width": 0.9},
           {"id": "d_2", "type": "door", "level_id": "L0", "wall_id": "w_1", "center": [7.5, 0.0], "width": 0.9}]
    if door_through:
        ops.append({"id": "d_mid", "type": "door", "level_id": "L0", "wall_id": "w_mid", "center": [5.0, 1.5],
                    "width": 0.9})
    lv = {"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "ceiling_height": 2.7}
    return building((lv, walls, rooms, ops))


def test_the_full_depth_wall_of_a_house_pair_is_an_internal_party_wall():
    b = house_pair()
    run_ext(b)
    found = FC.internal_party(b)
    assert [x["walls"] for x in found] == [["w_mid"]]
    b = house_pair(door_through=True)
    run_ext(b)
    assert FC.internal_party(b) == []


def test_the_eaves_stop_at_a_party_walls_outer_face():
    b = building(flat())
    b["level_inference"]["rules_staged"] = {"party_eaves": True}                 # the reading switched it on
    b["walls"][3]["party_wall"] = {"inferred": True, "text": "bitişik"}            # the west wall
    outline = [(-0.5, -0.5), (10.5, -0.5), (10.5, 6.5), (-0.5, 6.5)]
    cut, notes = PE.clip(outline, b, "L0")
    assert min(x for x, _ in cut) == -0.125 and max(x for x, _ in cut) == 10.5 and notes
    b["walls"][3]["party_wall"]["internal"] = True                                 # an internal one keeps the roof
    assert PE.clip(outline, b, "L0")[0] == outline


def test_a_kept_exterior_flag_between_two_rooms_is_a_finding():
    """R14 D1 (RC14 exterior_between_rooms): on a level that does not qualify the flags stay; the partition flagged
    exterior with rooms on both faces is asked about."""
    from wenart.reading_check import sense as SN

    b = building(flat())
    b["levels"][0]["reading_confidence"] = "low"
    _, walls = run_ext(b)
    assert walls["w_L0_5"]["exterior"] is True
    assert [f["element_ids"] for f in SN.exterior_between_rooms(b)] == [["w_L0_5"]]


def test_a_window_between_two_rooms_is_asked_about_and_a_paper_level_gives_one_finding():
    """R14 D3 (RC14 window_on_interior): a drawn window on an interior stretch is a question, never deleted; onto a
    light well no finding; on a level that does not qualify one level finding."""
    from wenart.reading_check import sense as SN

    b = building(flat())
    b["openings"].append({"id": "win_mid", "type": "window", "level_id": "L0", "wall_id": "w_L0_5",
                          "center": [5.0, 1.5], "width": 0.8, "evidence": [{"method": "vector"}]})
    run_ext(b)
    found = SN.window_on_interior(b)
    assert [f["element_ids"][0] for f in found] == ["win_mid"] and "never deleted" in found[0]["message"]
    next(r for r in b["rooms"] if r["id"] == "r_L0_salon").update(room_type="shaft", room_subtype="light_well")
    assert SN.window_on_interior(b) == []
    b = building(flat())
    b["openings"].append({"id": "win_mid", "type": "window", "level_id": "L0", "wall_id": "w_L0_5",
                          "center": [5.0, 1.5], "width": 0.8})
    run_ext(b)
    b["level_inference"]["exterior"]["not_qualified"] = {"L0": ["a paper room or frame walls (RC14)"]}
    found = SN.window_on_interior(b)
    assert len(found) == 1 and found[0]["element_ids"] == ["win_mid"] and "does not qualify" in found[0]["message"]
