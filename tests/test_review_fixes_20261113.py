"""13 Nov 2026 (the stage-1 review of the building-sense rules, 61 confirmed findings): each fix is a general rule, tested
here on small hand-made buildings (no project data).

What: the crash on a superscript tread number (CS1-08); the levels model keeps the completion's records (CS1-04); the
flat-core gaps judged against the openings still left, virtual separators as links, a bedroom's only link kept, a
window drawn in a gap kept as that window, a flat never cut off the core (MF5, CS1-01, CL-02, CS1-02, CL-01, MF9,
CL-06); a lift never opens into a shop that holds its own stair, its second derived landing opening goes, a flat's
hinged door marked a lift door gets its swing back, stacked landing pieces take the drawn jambs (MF3, MF4, REG-01,
REG-03, MF7, MF6, S1-20a, CL-05); machine-room words (MF13); the party wall bounded to its facade (CS1-06, MF12); a
storey of two blocks (CS1-10); a thin partition takes no inferred window (REG-02); the stair head only over a used
flat roof (REG-08, S1-all-a); one main entrance, an entrance into the core on any storey answers the building's
entrance, the inferred one in ``site.entrances`` (R09: S1-09b, S1-10a, POD-05, CL-04, CS1-05); the storey rule's
words, titles, height texts and tread runs (S1-03a, MF10, MF11, CS1-07), a plan that does not stack is not copied
(REG-04); RC12 against the drawn storey (S1-21d); a shaft the guard stops gets no void (CS1-09).
"""
from __future__ import annotations

import math
from types import SimpleNamespace

from shapely.geometry import Polygon

from wenart import building as B
from wenart.ingest import completion as CP
from wenart.ingest import core_rules as CR
from wenart.ingest import sense_rules as SR
from wenart.reading_check import sense as SN
from wenart.sheets import storeys as ST


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def room(rid, label, rtype, poly, level="L0", **kw):
    return dict({"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
                 "area_computed": round(Polygon(poly).area, 3)}, **kw)


def wall(wid, a, b, level="L0", t=0.2, exterior=False):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def op(oid, kind, wall_id, c, w, level="L0", **kw):
    return dict({"id": oid, "type": kind, "level_id": level, "wall_id": wall_id, "center": list(c), "width": w,
                 "evidence": [{"method": "vector"}]}, **kw)


def gap(oid, wall_id, c, w, level="L0"):
    return {"id": oid, "type": "opening", "level_id": level, "wall_id": wall_id, "center": list(c), "width": w,
            "evidence": [{"method": "derived"}]}


def building(levels=("L0",), **kw):
    b = {"levels": [{"id": lid, "label": lid, "order": k, "elevation": 3.0 * k, "ceiling_height": 2.7}
                    for k, lid in enumerate(levels)],
         "walls": [], "rooms": [], "openings": [], "furniture": [], "symbols": [], "slabs": [], "warnings": [],
         "site": {"entrances": []}, "level_inference": {}}
    b.update(kw)
    return b


def box_walls(x0, y0, x1, y1, level="L0", t=0.2, prefix="w"):
    return [wall(f"{prefix}_s", (x0, y0), (x1, y0), level, t, True), wall(f"{prefix}_e", (x1, y0), (x1, y1), level, t, True),
            wall(f"{prefix}_n", (x1, y1), (x0, y1), level, t, True), wall(f"{prefix}_w", (x0, y1), (x0, y0), level, t, True)]


# --------------------------------------------------------------------------------------------- CS1-08, CS1-04
def test_a_superscript_or_circled_digit_in_a_stair_box_is_no_tread_number_and_no_crash():
    p = Polygon(rect(0, 0, 2, 4))
    texts = [{"text": t, "x": 1.0, "y": 0.2 + 0.2 * k} for k, t in enumerate(["²", "③", "12", "x"])]
    assert CR.stair_evidence(p, [], texts) is None


def test_the_levels_model_keeps_the_records_the_completion_rules_wrote():
    from wenart.blender import architect_storeys as ASTO
    from wenart.levels import model as LM

    b = building(("L0", "L1"))
    b["walls"] = box_walls(0, 0, 8, 6) + box_walls(0, 0, 8, 6, "L1", prefix="w1")
    b["rooms"] = [room("r0", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9)),
                  room("r1", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9), "L1")]
    b["level_inference"] = {
        "storeys": {"count": 5, "rule": "type_default", "guess": True, "inferred": [{"level_id": "L1"}],
                    "open_point": {"key": ST.OPEN_POINT_KEY, "default": 5, "options": [4, 5], "severity": "major",
                                   "question": "How many storeys?"}},
        "windows": {"party_walls": {"L0": ["w_e"]}}, "rules_off": ["R16"], "conflicts_copied": True,
        "edits": [{"kind": "x"}]}
    out = LM.infer_levels(b)
    li = out["level_inference"]
    assert li["storeys"]["open_point"]["key"] == ST.OPEN_POINT_KEY and li["windows"]["party_walls"] == {"L0": ["w_e"]}
    assert li["rules_off"] == ["R16"] and "conflicts_copied" not in li and li["edits"] == [{"kind": "x"}]
    assert li["version"] == "m12" and ASTO.review(out)["id"] == "N1"


def test_a_typical_floors_copy_keeps_its_storey_height_over_the_copied_floor_marks():
    """real03 (three storeys read from its ground plan): the copies re-read the plan's ±0.00 marks; their elevation
    stays the storey's, never the copied floor's."""
    from wenart.levels import model as LM

    b = building(("L0", "L1"))
    b["levels"][1]["typical_of"] = "L0"
    for lv in b["levels"]:
        lv["elevation_source"] = "assumed_default"
    b["rooms"] = [room("r0", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9)),
                  room("r1", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9), "L1")]
    marks = [{"kind": "floor", "room_id": rid, "z": 0.0, "value": 0.0, "id": f"m_{rid}", "raw": "±0.00"}
             for rid in ("r0", "r1")]
    LM._level_elevations(b, marks, {"mark_tol": 0.05}, [], [])
    assert b["levels"][1]["elevation"] == 3.0 and b["levels"][0]["elevation"] == 0.0


# ------------------------------------------------------------------------------------------------ the core gaps
def core_storey(level="L0"):
    """A 14 x 8 m storey: a core hall (x 4-8) with a lift, a west flat (kitchen + living room joined by a door) and an
    east flat (an antre, a bedroom and a bathroom)."""
    walls = box_walls(0, 0, 14, 8, level, prefix=f"w{level}") + [
        wall(f"{level}_4", (4, 0), (4, 8), level), wall(f"{level}_8", (8, 0), (8, 8), level),
        wall(f"{level}_k", (0, 4), (4, 4), level), wall(f"{level}_l1", (6.4, 6), (8, 6), level),
        wall(f"{level}_l2", (6.4, 6), (6.4, 8), level), wall(f"{level}_e", (8, 4), (14, 4), level),
        wall(f"{level}_e2", (11, 4), (11, 8), level)]
    hall = [[4.1, 0.1], [7.9, 0.1], [7.9, 5.9], [6.3, 5.9], [6.3, 7.9], [4.1, 7.9]]
    rooms = [room(f"{level}_kit", "Mutfak", "kitchen", rect(0.1, 0.1, 3.9, 3.9), level),
             room(f"{level}_liv", "Salon", "living", rect(0.1, 4.1, 3.9, 7.9), level),
             room(f"{level}_hall", "Kat Holü", "hall", hall, level),
             room(f"{level}_lift", "Asansör", "shaft", rect(6.5, 6.1, 7.9, 7.9), level),
             room(f"{level}_antre", "Antre", "hall", rect(8.1, 0.1, 13.9, 3.9), level),
             room(f"{level}_bed", "Yatak Odası", "bedroom", rect(8.1, 4.1, 10.9, 7.9), level),
             room(f"{level}_bath", "Banyo", "bathroom", rect(11.1, 4.1, 13.9, 7.9), level)]
    ops = [op(f"{level}_kl", "door", f"{level}_k", (2.0, 4.0), 0.9, level),
           op(f"{level}_ea", "door", f"{level}_8", (8.0, 2.0), 1.0, level),          # the east flat's entrance
           op(f"{level}_ab", "door", f"{level}_e", (9.5, 4.0), 0.9, level),
           op(f"{level}_ah", "door", f"{level}_e", (12.5, 4.0), 0.8, level),
           op(f"{level}_ld", "door", f"{level}_l1", (7.2, 6.0), 0.9, level, operation="sliding", lift_door=True)]
    return walls, rooms, ops


def core_building(levels=("L0", "L1")):
    b = building(levels)
    for lid in levels:
        w, r, o = core_storey(lid)
        b["walls"] += w
        b["rooms"] += r
        b["openings"] += o
    b["rooms"].append(room("L0_kit2", "Mutfak", "kitchen", rect(0.2, 0.2, 0.6, 0.6)))   # two kitchens: several flats
    return b


def test_two_gaps_of_an_open_plan_flat_keep_one_link_to_the_core():
    """MF5, CS1-01, CL-03: each gap is judged against the gaps still left; the flat keeps exactly one."""
    b = core_building(("L0",))
    b["openings"] += [gap("g_kit", "L0_4", (4.0, 2.0), 1.0), gap("g_liv", "L0_4", (4.0, 6.0), 1.0)]
    out = CR.close_core_gaps(b)
    left = {o["id"] for o in b["openings"]} & {"g_kit", "g_liv"}
    assert len(out["closed"]) == 1 and len(left) == 1


def test_a_virtual_separator_is_a_link_for_the_core_gap_rule():
    """CL-02: the antre and its corridor split by a virtual separator; the living room reaches the core through them,
    so its derived gap onto the core is a second link and closes."""
    b = core_building(("L0",))
    b["rooms"] = [r for r in b["rooms"] if r["id"] != "L0_antre"] + [
        room("L0_antre", "Antre", "hall", rect(8.1, 0.1, 10.9, 3.9)), room("L0_cor", "Koridor", "hall",
                                                                          rect(11.1, 0.1, 13.9, 3.9))]
    b["openings"] += [{"id": "v1", "type": "opening", "virtual": True, "level_id": "L0", "wall_id": None,
                       "line": [[11.0, 0.1], [11.0, 3.9]], "center": [11.0, 2.0], "width": 3.8},
                      op("d_cl", "door", "L0_e", (12.5, 4.0), 0.9)]
    b["rooms"] = [r for r in b["rooms"] if r["id"] != "L0_bath"] + [room("L0_liv2", "Salon", "living",
                                                                         rect(11.1, 4.1, 13.9, 7.9))]
    b["openings"] = [o for o in b["openings"] if o["id"] != "L0_ah"]
    level = CP.Level(b, "L0")
    core = CR.core_rooms(b, level)
    assert CR._reaches(level, core, "L0_liv2")
    assert "L0_antre" not in core and "L0_cor" not in core


def test_a_bedrooms_only_link_is_kept_for_review_and_a_flat_is_never_cut_off():
    """CS1-02: a bedroom's gap that is its only link is a review record; CL-06: a closing that cuts the flat off the
    core is undone."""
    b = core_building(("L0",))
    b["openings"] = [o for o in b["openings"] if o["id"] != "L0_ab"]
    b["openings"].append(gap("g_bed", "L0_8", (8.0, 5.0), 0.9))
    out = CR.close_core_gaps(b)
    assert out["closed"] == [] and [r["opening"] for r in out["review"]] == ["g_bed"]
    assert "g_bed" in {o["id"] for o in b["openings"]}
    # the flat's entrance read as a gap too: closing the bedroom gap would cut the flat off
    b = core_building(("L0",))
    b["openings"] = [o for o in b["openings"] if o["id"] != "L0_ea"]
    b["openings"] += [gap("g_bed", "L0_8", (8.0, 5.0), 0.9)]
    out = CR.close_core_gaps(b)
    assert "g_bed" in {o["id"] for o in b["openings"]} and out["review"]


def test_a_window_drawn_in_a_gap_stays_that_window_and_the_rest_closes():
    """CL-01, MF9: a 1.9 m gap between a bathroom and the core holding a 0.5 m window (two strokes on 'pencere')."""
    b = core_building(("L0",))
    b["openings"].append(gap("g_bath", "L0_8", (8.0, 6.2), 1.4))
    b["rooms"] = [r for r in b["rooms"] if r["id"] != "L0_bed"] + [room("L0_bath2", "Banyo", "bathroom",
                                                                        rect(8.1, 4.1, 10.9, 7.9))]
    segs = [{"a": (7.95, 6.0), "b": (7.95, 6.5), "length": 0.5, "id": "L1", "layer": "pencere"},
            {"a": (8.05, 6.0), "b": (8.05, 6.5), "length": 0.5, "id": "L2", "layer": "pencere"}]
    drawn = SimpleNamespace(segments=lambda poly: [s for s in segs if poly.contains(
        Polygon([s["a"], s["b"], (s["b"][0] + 1e-3, s["b"][1]), (s["a"][0] + 1e-3, s["a"][1])]).centroid)])
    out = CR.close_core_gaps(b, {"L0": drawn}, {})
    win = next(o for o in b["openings"] if o["id"] == "g_bath")
    assert out["windows"] and win["type"] == "window" and math.isclose(win["width"], 0.5, abs_tol=0.01)
    assert win["drawn_type"] == "opening" and win["sill_height"] > 1.0


def test_a_gap_holding_a_door_size_tag_is_a_door_not_read_and_stays():
    """A door's size tag (100/210, high) in a gap onto the core: a flat's entrance the reading missed: kept, to review
    (a window's tag is under 1.8 m high)."""
    b = core_building(("L0",))
    b["openings"].append(gap("g_bed", "L0_8", (8.0, 5.0), 1.2))
    out = CR.close_core_gaps(b, {}, {"L0": [{"text": "100/210", "x": 8.0, "y": 5.2}]})
    assert out["closed"] == [] and out["windows"] == [] and "100/210" in out["review"][0]["reason"]
    assert next(o for o in b["openings"] if o["id"] == "g_bed")["type"] == "opening"


# ----------------------------------------------------------------------------------------------- the lift doors
def test_a_lift_beside_a_shop_with_its_own_stair_gets_no_door_into_the_shop():
    """MF3, MF4, REG-01: a stair inside a shop is the shop's own; the lift's only neighbour is the shop: no door
    inferred, a review record."""
    b = building(("L0", "L1"))
    for lid in ("L0", "L1"):
        b["walls"] += box_walls(0, 0, 10, 6, lid, prefix=f"w{lid}") + [wall(f"{lid}_a", (2, 0), (2, 6), lid),
                                                                         wall(f"{lid}_b", (0, 2), (2, 2), lid)]
        b["rooms"] += [room(f"{lid}_lift", "Asansör", "shaft", rect(0.1, 0.1, 1.9, 1.9), lid),
                       room(f"{lid}_shop", "Dükkan", "other", rect(2.1, 0.1, 9.9, 5.9), lid),
                       room(f"{lid}_kit", "Mutfak", "kitchen", rect(0.1, 2.1, 1.9, 5.9), lid),
                       room(f"{lid}_k2", "Mutfak", "kitchen", rect(0.2, 2.2, 0.5, 2.5), lid)]
    b["furniture"].append({"id": "f_st", "level_id": "L0", "type": "stair",
                           "footprint": {"center": [6.0, 3.0], "size": [1.0, 3.0], "rotation_deg": 0.0}})
    b["rooms"].append(room("L0_hol", "Kat Holü", "hall", rect(9.0, 5.0, 9.8, 5.8)))     # a common hall elsewhere
    level = CP.Level(b, "L0")
    assert "L0_shop" not in CR.core_rooms(b, level)
    rec = CR.fix_lift_doors(b, B.IdCounter().next, True)
    assert rec["added"] == [] and any(r["lift"] == "L0_lift" for r in rec["review"] if r.get("lift"))


def test_a_lifts_second_derived_landing_opening_goes_once_it_opens_onto_the_core():
    """REG-03, MF7: the lift opens onto the core hall; its derived door into an unread room goes."""
    b = core_building(("L0",))
    b["walls"].append(wall("L0_lx", (6.4, 8.0), (8.0, 8.0)))
    b["openings"].append({"id": "d_lift_x", "type": "door", "level_id": "L0", "wall_id": "L0_8", "center": [8.0, 7.0],
                          "width": 0.9, "evidence": [{"method": "inferred", "rule": "lift_door"}], "lift_door": True})
    b["rooms"] = [r for r in b["rooms"] if r["id"] != "L0_bed"] + [room("L0_unk", "", "unknown",
                                                                        rect(8.1, 4.1, 10.9, 7.9))]
    rec = CR.fix_lift_doors(b, B.IdCounter().next, True)
    assert "d_lift_x" not in {o["id"] for o in b["openings"]}
    assert any(r["opening"] == "d_lift_x" for r in rec["removed"])
    found = [f for f in SN.lift_doors(b) if "landing openings" in f["message"]]
    assert found == []


def test_a_flats_hinged_door_marked_a_lift_door_gets_its_swing_back():
    """MF6, S1-20a: a lift label on a 16 m2 face holding the stair (the whole core); the flat's drawn door on its edge,
    made a sliding lift door by the earlier rule, is a swing door again (its drawn operation kept), in any building."""
    b = building(("L0",))
    b["walls"] = box_walls(0, 0, 10, 6) + [wall("w_c", (4, 0), (4, 6))]
    b["rooms"] = [room("r_core", "Asansör Merdiven", "shaft", rect(0.1, 0.1, 3.9, 4.1)),
                  room("r_liv", "Salon", "living", rect(4.1, 0.1, 9.9, 5.9))]
    b["openings"] = [op("d_flat", "door", "w_c", (4.0, 2.0), 1.0, operation="sliding", operation_source="assumed",
                        lift_door=True, drawn_operation="swing", drawn_operation_source="geometry",
                        drawn_swing_side="r_liv")]
    rec = CR.fix_lift_doors(b, B.IdCounter().next, False)
    d = b["openings"][0]
    assert [u["opening"] for u in rec["unmarked"]] == ["d_flat"]
    assert d["lift_door"] is False and d["operation"] == "swing" and d["swing_side"] == "r_liv" and d["flat_entrance"]


def test_stacked_landing_pieces_take_the_drawn_jambs():
    """CL-05: three stacked pieces of 1.05, 0.785 and 0.70 m, the drawn jambs 0.90 m apart: one 0.90 m door between
    them."""
    b = core_building(("L0",))
    b["openings"] = [o for o in b["openings"] if o["id"] != "L0_ld"]
    b["walls"] += [wall("L0_l1b", (6.4, 6.25), (8, 6.25), t=0.1), wall("L0_l1c", (6.4, 5.8), (8, 5.8), t=0.1),
                   wall("L0_j1", (6.65, 5.7), (6.65, 6.3), t=0.1), wall("L0_j2", (7.65, 5.7), (7.65, 6.3), t=0.1)]
    b["openings"] += [gap("p1", "L0_l1", (7.15, 6.0), 1.05), gap("p2", "L0_l1b", (7.15, 6.25), 0.785),
                      gap("p3", "L0_l1c", (7.15, 5.8), 0.70)]
    CR.fix_lift_doors(b, B.IdCounter().next, True)
    kept = [o for o in b["openings"] if o["id"] in ("p1", "p2", "p3")]
    assert len(kept) == 1 and math.isclose(kept[0]["width"], 0.90, abs_tol=0.02)
    assert math.isclose(kept[0]["center"][0], 7.15, abs_tol=0.02) and kept[0]["type"] == "door"


def test_lift_machine_room_words_are_no_lift():
    sq = rect(0, 0, 1.6, 1.6)
    for label in ("ASANSÖR MAKİNA HİDROLİK", "Asansör Makine Odası", "Lift machine room"):
        assert not CP.is_lift({"label": label, "polygon": sq}), label
    for label in ("Makine Dairesiz Asansör", "Hidrolik Asansör 4 Kişiliktir", "Asansör"):
        assert CP.is_lift({"label": label, "polygon": sq}), label


# ------------------------------------------------------------------------------------------------ party walls
def u_plan():
    """A U plan open to the north: arms x 0-4 and x 10-14 (y 0-10), a base y 0-4."""
    ring = [(0, 0), (14, 0), (14, 10), (10, 10), (10, 4), (4, 4), (4, 10), (0, 10)]
    b = building(("L0",))
    b["walls"] = [wall(f"w{k}", ring[k], ring[(k + 1) % len(ring)], t=0.2, exterior=True) for k in range(len(ring))]
    b["rooms"] = [room("r_w", "Salon", "living", rect(0.1, 0.1, 3.9, 9.9)),
                  room("r_e", "Salon", "living", rect(10.1, 0.1, 13.9, 9.9)),
                  room("r_b", "Hol", "hall", rect(4.1, 0.1, 9.9, 3.9))]
    return b


def test_the_party_wall_is_bounded_to_the_facade_the_text_names():
    """CS1-06, MF12: a 'bitişik' text beside the west arm's outer face marks that facade only; the other arm's inner
    face on the same infinite line... is not on the outline run."""
    b = u_plan()
    level = CP.Level(b, "L0")
    party = CP.party_walls(level, [{"kind": "party", "text": "bitişik", "at": [-1.0, 5.0]}])
    assert set(party) == {"w7"}
    side = party["w7"]["side"]
    assert math.isclose(min(side[0][1], side[1][1]), -0.1, abs_tol=0.15)


def test_a_split_facade_is_marked_whole():
    """CS1-06: one facade cut into pieces by tiny jogs (CAD rounding) is one party side."""
    b = building(("L0",))
    ring = [(0, 0), (10, 0), (10, 6), (0, 6)]
    b["walls"] = [wall("s", (0, 0), (10, 0), exterior=True), wall("e1", (10, 0), (10, 3), exterior=True),
                  wall("e2", (10.0002, 3), (10.0002, 6), exterior=True), wall("n", (10, 6), (0, 6), exterior=True),
                  wall("w", (0, 6), (0, 0), exterior=True)]
    del ring
    b["rooms"] = [room("r", "Salon", "living", rect(0.1, 0.1, 9.9, 5.9))]
    level = CP.Level(b, "L0")
    party = CP.party_walls(level, [{"kind": "party", "text": "bitişik", "at": [11.0, 1.5]}])
    assert {"e1", "e2"} <= set(party)


# ------------------------------------------------------------------------------- two blocks, thin partitions
def test_a_probe_in_the_smaller_block_of_two_reads_void_not_outside():
    """CS1-10: a storey of two separate blocks; inside the smaller one, in no room, is the building."""
    b = building(("L0",))
    b["walls"] = box_walls(0, 0, 10, 8, prefix="a") + box_walls(20, 0, 26, 6, prefix="b")
    level = CP.Level(b, "L0")
    assert level.kind_at((23.0, 3.0), "") == "void" and level.kind_at((15.0, 3.0), "") == "outside"


def test_a_thin_partition_takes_no_inferred_window():
    """REG-02: a 0.10 m wall on a level of 0.25 m facades never takes an inferred window, whatever lies behind it."""
    b = building(("L0",))
    b["walls"] = box_walls(0, 0, 10, 6, t=0.25) + [wall("thin", (5, 0), (5, 6), t=0.10)]
    b["rooms"] = [room("r_bed", "Oda", "bedroom", rect(0.15, 0.15, 4.95, 5.85))]
    new = CP.infer_level(b, "L0", {}, dict(CP.DEFAULT_SIZES), "defaults", B.IdCounter().next)
    assert new and all(o["wall_id"] != "thin" for o in new)


# ----------------------------------------------------------------------------------------------- stair head
def head_building(roof_type, top_kind=None, texts=None):
    b = building(("L0", "L1"))
    for lid in ("L0", "L1"):
        b["walls"] += box_walls(0, 0, 8, 6, lid, prefix=f"w{lid}")
        b["rooms"].append(room(f"{lid}_r", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9), lid))
        b["furniture"].append({"id": f"f_{lid}", "level_id": lid, "type": "stair",
                               "footprint": {"center": [2.0, 3.0], "size": [1.0, 3.0], "rotation_deg": 0.0}})
    if top_kind:
        b["levels"][1]["kind"] = top_kind
    b["roof"] = {"type": roof_type, "type_source": "section"} if roof_type else None
    return b


def test_no_stair_head_under_a_pitched_roof_and_a_hatch_text_is_a_ceiling_hatch():
    """REG-08, S1-all-a: a hip-roofed two-storey house: no stair head; 'çatıya çıkış' on the top plan: a hatch."""
    rec = CP.core_record(head_building("hip"))
    assert rec["stair_head"]["needed"] is False and "pitched" in rec["stair_head"]["reason"]
    rec = CP.core_record(head_building("flat"), {"L1": [{"text": "çatıya çıkış", "x": 2, "y": 3, "entity": "T1"}]})
    assert rec["roof_access"]["kind"] == "ceiling_hatch_ladder" and rec["stair_head"]["needed"] is False
    rec = CP.core_record(head_building("flat"))
    assert rec["stair_head"]["needed"] is False and "arrival" in rec["stair_head"]["reason"]
    b = head_building("flat")
    b["rooms"].append(room("L1_ter", "Teras", "terrace", rect(4, 0.1, 7.9, 5.9), "L1"))
    assert CP.core_record(b)["stair_head"]["needed"] is True


# ------------------------------------------------------------------------------------------------- entrances
def entrance_building():
    """Several flats with a common core on two storeys: L-1 at the street (-3.0), L0 a storey up."""
    b = core_building(("L-1", "L0"))
    for lv, el, order in zip(b["levels"], (-3.0, 0.0), (-1, 0)):
        lv.update(elevation=el, order=order)
    b["site"] = {"ground": {"levels": [{"z": {"value": -3.0}}]}, "entrances": []}
    return b


def test_a_main_entrance_into_the_core_on_the_storey_at_the_street_answers_the_building():
    """S1-10a, POD-05, CL-04: the drawn main door on L-1 into its core hall; L0 is 3 m over the ground: no door is
    inferred, no open point, no RC14 no_entrance."""
    b = entrance_building()
    b["walls"].append(wall("wL-1_s2", (4, 0), (8, 0), "L-1", exterior=True))
    b["openings"].append(op("d_main", "door", "wL-1_s", (6.0, 0.0), 1.2, "L-1"))
    b["site"]["entrances"] = [{"door_id": "d_main", "level_id": "L-1", "room_id": "L-1_hall", "rise": 0.0,
                               "main": True, "face": [6.0, -0.1], "outward": [0.0, -1.0]}]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["added"] == [] and rec["open"] is None
    assert SN.no_entrance(b) == []


def test_an_entrance_is_inferred_only_on_a_storey_at_the_ground_with_its_site_record():
    """R09, CS1-05: no entrance drawn; the core hall of the storey at the ground reaches the facade: a door there, in
    site.entrances with its rise; none on the storey 3 m up."""
    b = entrance_building()
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert [a["level_id"] for a in rec["added"]] == ["L-1"]
    ent = b["site"]["entrances"][-1]
    assert ent["level_id"] == "L-1" and ent["inferred"] and ent["main"] and ent["rise"] == 0.0


def test_a_drawn_entrance_into_a_wind_lobby_before_the_core_answers_the_building():
    """S1-03b (real03): the drawn front door opens into the Rüzgarlık, whose door leads into the core hall: no
    inferred entrance into the core."""
    b = core_building(("L0", "L1"))
    for r in b["rooms"]:
        if r["id"] == "L0_hall":
            r["polygon"] = [[4.1, 1.6], [7.9, 1.6], [7.9, 5.9], [6.3, 5.9], [6.3, 7.9], [4.1, 7.9]]
    b["walls"].append(wall("L0_rz", (4, 1.5), (8, 1.5)))
    b["rooms"].append(room("L0_rz", "Rüzgarlık", "other", rect(4.1, 0.1, 7.9, 1.4)))
    b["openings"] += [op("d_rz", "door", "L0_rz", (6.0, 1.5), 1.0), op("d_front", "door", "wL0_s", (6.0, 0.0), 1.2)]
    b["site"]["entrances"] = [{"door_id": "d_front", "level_id": "L0", "room_id": "L0_rz", "rise": 0.0, "main": True}]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["added"] == [] and rec["open"] is None


def test_no_door_is_inferred_metres_over_the_ground_only_a_question():
    """R09: the ground floor stands 1.5 m over the only ground height read: no door there, an open point."""
    b = core_building(("L0", "L1"))
    b["site"] = {"ground": {"levels": [{"z": {"value": -1.5}}]}, "entrances": []}
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["added"] == [] and rec["open"] and b["site"]["entrances"] == []


def test_a_main_entrance_never_opens_into_a_bedroom():
    """S1-09b: the levels model chose a bedroom's door as the main entrance; the core hall's door is the main one."""
    b = entrance_building()
    b["openings"] += [op("d_bed", "door", "wL-1_n", (9.5, 8.0), 0.9, "L-1"),      # a record needs its door (CODE-04)
                      op("d_hall", "door", "wL-1_s", (6.0, 0.0), 1.2, "L-1")]
    b["site"]["entrances"] = [
        {"door_id": "d_bed", "level_id": "L-1", "room_id": "L-1_bed", "rise": 0.0, "main": True},
        {"door_id": "d_hall", "level_id": "L-1", "room_id": "L-1_hall", "rise": 0.2, "main": False}]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["main"]["was"] == "d_bed" and rec["main"]["now"] == "d_hall"
    assert [e["door_id"] for e in b["site"]["entrances"] if e["main"]] == ["d_hall"]
    # a house (no common core) whose only outer door opens into a bedroom: no main entrance, a question
    h = building(("L0",))
    h["walls"] = box_walls(0, 0, 8, 6)
    h["rooms"] = [room("r_bed", "Yatak Odası", "bedroom", rect(0.1, 0.1, 7.9, 5.9))]
    h["openings"] = [op("d_b", "door", "w_s", (4.0, 0.0), 0.9)]
    h["site"]["entrances"] = [{"door_id": "d_b", "level_id": "L0", "room_id": "r_bed", "rise": 0.0, "main": True}]
    rec = CR.fix_entrances(h, B.IdCounter().next, {})
    assert rec["main"]["now"] is None and rec["open"] and not h["site"]["entrances"][0]["main"]


def test_no_core_read_raises_no_entrance_question():
    b = building(("L0",))
    b["walls"] = box_walls(0, 0, 8, 6)
    b["rooms"] = [room("r", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9))]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["open"] is None and rec["added"] == []


# ----------------------------------------------------------------------------------------------- the storeys
def test_suffixed_stair_words_and_flat_titles_make_an_apartment_block():
    """S1-03a, POD-03: 'KAT MERDİVENİ' and eight 'DAİRE TİPİ' titles; a house with a stair word stays a house."""
    texts = [SimpleNamespace(text="KAT MERDİVENİ")] + [SimpleNamespace(text=f"{k}. DAİRE TİPİ") for k in range(8)]
    sig = ST.plan_signals(SimpleNamespace(texts=texts, features={}))
    assert sig["stair_words"] == 1 and sig["flat_words"] == 8
    assert ST.building_type(sig, False) == "apartment_block"
    house = ST.plan_signals(SimpleNamespace(texts=[SimpleNamespace(text="MERDİVEN"), SimpleNamespace(text="MUTFAK")],
                                            features={}))
    assert ST.building_type(house, False) == "house_stair"
    assert ST.plan_signals(SimpleNamespace(texts=[SimpleNamespace(text="ASANSÖR MAKİNE DAİRESİ")],
                                           features={}))["lifts"] == 0


def test_scales_level_marks_and_area_notes_are_no_floor_list():
    """MF10."""
    def counts(text):
        return [c["count"] for c in ST.title_counts([(SimpleNamespace(text=text, id="t", layer="0"), "a.dxf")])]
    assert counts("1/50 NORMAL KAT PLANI") == []
    assert counts("+3.50 KAT PLANI") == []
    assert counts("2197 m2 /6KAT=366.20M2") == []
    assert counts("1.-4. NORMAL KAT PLANI") == [5]


def test_a_riser_height_at_a_stair_is_no_height_limit():
    """MF11: 'R:17 / B:25 / H:17.6' at a stair; a zoning word always counts."""
    def heights(*texts):
        items = [(SimpleNamespace(text=t, id=f"t{k}", layer="0", point=(0.0, k * 0.5), height=0.25), "a.dxf")
                 for k, t in enumerate(texts)]
        return [h["value"] for h in ST.zoning_items(items)["height"]]
    assert heights("R:17", "B:25", "H:17.60") == []
    assert heights("H=12.50 İRTİFALI YERDE") == [12.5]
    assert heights("HMAX=15.50") == [15.5]


def test_a_flight_drawn_at_an_odd_whole_degree_is_one_run():
    """CS1-07: flights at 45, 135 and 1 degrees, coordinates rounded to 0.1 mm, random origins: one run of 12 lines."""
    for deg, origin in ((45.0, (13.37, -4.2)), (135.0, (-7.9, 2.31)), (1.0, (100.0, 55.5))):
        a = math.radians(deg)
        u, n = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        ents = []
        for k in range(12):
            p = (origin[0] + n[0] * 0.28 * k, origin[1] + n[1] * 0.28 * k)
            q = (p[0] + u[0] * 1.1, p[1] + u[1] * 1.1)
            pts = [(round(p[0], 4), round(p[1], 4)), (round(q[0], 4), round(q[1], 4))]
            ents.append(SimpleNamespace(kind="LINE", strokes=[SimpleNamespace(arc=False, pts=pts)]))
        runs = ST.stair_strokes(SimpleNamespace(metres_per_unit=1.0, ents=ents))
        assert len(runs) == 1 and runs[0]["lines"] == 12, (deg, runs)


def test_a_plan_that_does_not_stack_on_the_storey_below_is_not_copied():
    """REG-04: the top plan's outline against the plan below: a 12 x 10 m plan over a 12 x 10 m plan stacks, a
    20 x 6 m plan does not."""
    def plan(rid, poly):
        r = SimpleNamespace(id=rid)
        r._outline_metres = Polygon(poly)
        return r
    low = plan("r_low", rect(0, 0, 12, 10))
    assert ST.stacks(plan("r_top", rect(50, 50, 62, 60)), low)["ok"]
    bad = ST.stacks(plan("r_alt", rect(0, 0, 20, 6)), low)
    assert bad is not None and not bad["ok"] and "r_low" in bad["reason"]


def test_a_section_roof_under_the_added_top_storey_stands_on_it():
    """REG-05: storeys added over the drawn top storey; the section's gambrel eaves (+3.27) cut through them: the roof
    keeps its rise above the drawn storey and stands on the new top storey (assumed, a conflict)."""
    b = building(("L0", "L1", "L2"))
    b["roof"] = {"type": "gambrel", "type_source": "section", "over_level_id": "L0", "eaves_height": {"value": 3.27},
                 "ridge_height": {"value": 5.39}, "planes": [{"id": "p1", "points": [[0, 0, 3.27], [1, 0, 3.27],
                                                                                       [1, 1, 5.39]]}]}
    msgs = []
    build = SimpleNamespace(building=b, warn=msgs.append)
    why = CP._rebase_roof(build, b, {"L1", "L2"})
    assert why and b["roof"]["over_level_id"] == "L2"
    assert math.isclose(b["roof"]["eaves_height"]["value"], 9.27)
    assert math.isclose(b["roof"]["ridge_height"]["value"], 11.39)
    assert b["roof"]["planes"][0]["points"][2][2] == 11.39 and msgs
    assert CP._rebase_roof(build, b, {"L1", "L2"}) is None          # once only (the roof now stands on the top)


def test_a_stair_under_a_stair_head_on_the_roof_terrace_reaches_it():
    """S1-10c (real10): the core stair arrives inside the roof terrace storey's stair head (an enclosed room over it):
    the storey is reached though no flight and no void are drawn there; without the head it is not."""
    b = building(("L0", "L1"))
    b["levels"][1]["roof_terrace"] = True
    b["rooms"] = [room("r0", "Hol", "hall", rect(0.1, 0.1, 7.9, 5.9)),
                  room("r_head", "Oda", "hall", rect(0.1, 0.1, 3.0, 4.0), "L1")]
    b["furniture"] = [{"id": "f0", "level_id": "L0", "type": "stair",
                       "footprint": {"center": [1.5, 2.0], "size": [1.2, 3.0], "rotation_deg": 0.0},
                       "stair": {"flights": [{"lines": 8}]}}]
    found = [f for f in SN.stair_links(b) if f["level_id"] == "L1"]
    assert found == []
    b["rooms"][1]["polygon"] = rect(5.0, 0.1, 7.9, 4.0)
    assert [f["level_id"] for f in SN.stair_links(b)] == ["L1"]


# ----------------------------------------------------------------------------------------------- RC12, CS1-09
def test_rc12_compares_the_copies_with_the_drawn_storey_not_the_inferred_ground_floor():
    """S1-21d: the inferred ground floor L0 (balconies left off) against the drawn L1 is info; L2 against L1."""
    from wenart.reading_check import crossdoc as XD

    b = building(("L0", "L1", "L2"))
    for lv in b["levels"][1:]:
        lv["typical_of"] = "L0"
    for lid in ("L0", "L1", "L2"):
        b["walls"] += box_walls(0, 0, 8, 6, lid, prefix=f"w{lid}")
        b["rooms"].append(room(f"{lid}_r", "Salon", "living", rect(0.1, 0.1, 7.9, 5.9), lid))
        if lid != "L0":
            b["openings"].append(op(f"d_{lid}", "door", f"w{lid}_n", (4.0, 6.0), 0.9, lid))
    b["level_inference"]["storeys"] = {"ground_from_typical": True,
                                       "inferred": [{"level_id": "L0"}, {"level_id": "L2"}],
                                       "ground_floor": {"dropped": [{"id": "os_1"}]}}
    found = XD.rc12(b)
    assert [f["severity"] for f in found] == ["info"] and found[0]["level_id"] == "L0"


def test_a_shaft_the_guard_stops_gets_no_slab_void():
    """CS1-09: every shaft passes the guard before it gets slab voids (here switched off in the brief)."""
    b = building(("L0", "L1"))
    for lid in ("L0", "L1"):
        b["walls"] += box_walls(0, 0, 8, 6, lid, prefix=f"w{lid}")
        b["rooms"].append(room(f"{lid}_sh", "Şaft", "shaft", rect(0.1, 0.1, 0.9, 0.9), lid))
    b["slabs"] = [{"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "openings": []}]
    b["project"] = {"brief": {"rules_off": ["shaft"]}}
    SR.shafts(b, {})
    assert b["slabs"][0]["openings"] == []
    del b["project"]
    SR.shafts(b, {})
    assert len(b["slabs"][0]["openings"]) == 1
