"""The fixes of the stage-1 fix check (13 Nov 2026, findings S1F-POD-*, FC-*, CODE-*): CPU only, synthetic fixtures."""
from types import SimpleNamespace

import pytest
from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart.blender import parametric as P
from wenart.ingest import completion as CP
from wenart.ingest import core_rules as CR
from wenart.ingest import ground_lines as GL
from wenart.levels import model as LM


# --------------------------------------------------------------------------- S1F-POD-P01: the inferred U stair
@pytest.mark.parametrize("length", [3.6, 4.0, 4.4, 4.75, 5.2, 6.0])
@pytest.mark.parametrize("rot", [0.0, 90.0, 33.0])
def test_inferred_u_stair_flights_stand_on_the_landing(length, rot):
    """Both flights of an inferred U stair end on the landing's near edge at the landing's level (riser line to riser
    line), the landing is as deep as stair_dict made it (no lane added), and the stair passes RC16."""
    fp = {"center": [6.37, 14.0], "size": [1.8, length], "rotation_deg": rot}
    st = CR.stair_dict(fp, "test", "U", 3.0)
    piece = {"id": "s", "type": "stair", "level_id": "L0", "stair": st, "footprint": dict(fp)}
    plan = P.stair_plan(piece, 3.0, 2.8, 2.8 + P.STAIR_SHAFT_CAP_M, [])
    assert plan["integrity"] == []
    lp = Polygon(plan["landing"]["polygon"])
    f0, f1 = plan["flights"]
    assert lp.distance(Point(f0["nosings"][-1])) <= 0.03 and abs(f0["top_z"] - plan["landing"]["z"]) < 1e-6
    assert lp.distance(Point(f1["nosings"][0])) <= 0.03 and abs(f1["base_z"] - plan["landing"]["z"]) < 1e-6
    assert lp.area == pytest.approx(1.8 * st["landing"]["depth"], rel=0.02)
    assert plan["risers"] == CR.risers_for(3.0)


@pytest.mark.parametrize("length", [3.6, 4.75, 6.0])
def test_inferred_stairs_without_rise_and_straight_pass_rc16(length):
    for turn, width in (("U", 1.8), ("straight", 1.1)):
        for rise in (None, 2.8):
            fp = {"center": [0.0, 0.0], "size": [width, length], "rotation_deg": 0.0}
            st = CR.stair_dict(fp, "test", turn, rise)
            piece = {"id": "s", "type": "stair", "level_id": "L0", "stair": st, "footprint": dict(fp)}
            plan = P.stair_plan(piece, rise or 3.0, (rise or 3.0) - 0.2, (rise or 3.0) - 0.2 + P.STAIR_SHAFT_CAP_M, [])
            assert plan["integrity"] == [], (turn, rise, plan["integrity"])


# --------------------------------------------------------------------------- S1F-POD-P03: the ground and the doors
def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _storey(lid, order, z, doors=True, kind=None):
    walls = [{"id": f"w_{lid}_{s}", "level_id": lid, "start": list(a), "end": list(e), "thickness": 0.2,
              "exterior": True}
             for s, a, e in (("s", (0, 0), (10, 0)), ("e", (10, 0), (10, 8)), ("n", (10, 8), (0, 8)), ("w", (0, 8), (0, 0)))]
    rooms = [{"id": f"r_{lid}", "level_id": lid, "label": "SALON", "room_type": "living", "polygon": _rect(0, 0, 10, 8)}]
    ops = [{"id": f"d_{lid}_1", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_s", "center": [5.0, 0.0],
            "width": 1.0, "height": 2.1, "evidence": [{"method": "vector"}]}] if doors else []
    lv = {"id": lid, "label": lid, "order": order, "elevation": z, "ceiling_height": 2.7}
    if kind:
        lv["kind"] = kind
    return lv, walls, rooms, ops


def _ground_building(ground_z, lines, basement_doors=True):
    parts = [_storey("L-1", -1, -2.5, basement_doors, "basement"), _storey("L0", 0, 0.0), _storey("L1", 1, 3.0),
             _storey("L2", 2, 6.0)]
    b = {"levels": [p[0] for p in parts], "walls": [w for p in parts for w in p[1]],
         "rooms": [r for p in parts for r in p[2]], "openings": [o for p in parts for o in p[3]], "furniture": [],
         "warnings": [], "level_inference": {},
         "site": {"ground": {"levels": [{"side": "all", "azimuth_deg": None,
                                         "z": {"value": ground_z, "method": "vector", "confidence": 1.0,
                                               "evidence": [{"file": "x.dwg", "entity": "LINE:TOP", "method": "vector",
                                                             "rule": "ground_line", "region_id": "r6"}],
                                               "lines": lines}}],
                             "surface": {"kind": "flat", "flat_z": ground_z, "source": "section"}}}}
    conflicts = []
    build = SimpleNamespace(building=b, conflict=lambda *a: conflicts.append(a), warn=b["warnings"].append)
    return build, conflicts


LINES = [{"side": s, "z": z, "entity": f"LINE:{s[0]}{k}"} for k, z in enumerate((11.11, 9.03, 6.03, 3.03, 0.03, -0.1,
                                                                                  -2.47)) for s in ("left", "right")]


def test_a_ground_burying_storeys_with_doors_takes_the_line_beside_the_doors_at_grade():
    build, conflicts = _ground_building(11.11, LINES)
    rec = GL.apply(build)
    b = build.building
    assert rec is not None and rec["z"] == -2.47 and rec["at"] == "L-1" and rec["chosen"]["both_sides"]
    assert {"L0", "L1", "L2"} <= set(rec["storeys"]) and rec["refused"][0]["value"] == 11.11
    (entry,) = b["site"]["ground"]["levels"]
    assert entry["z"]["value"] == -2.47 and entry["z"]["method"] == "vector"
    assert entry["adjusted_by_ai"]["rule"] == "ground_doors" and b["site"]["ground"]["surface"]["flat_z"] == -2.47
    assert conflicts and not b.get("needs_review")
    assert CP.below_ground(b, b["levels"][1]) is None                      # L0 is no longer under the ground


def test_without_basement_doors_the_ground_floor_line_is_the_ground():
    build, _ = _ground_building(11.11, LINES, basement_doors=False)
    rec = GL.apply(build)
    assert rec["z"] == 0.03 and rec["at"] == "L0"


def test_no_line_beside_the_doors_assumes_a_step_and_asks():
    lines = [ln for ln in LINES if ln["z"] > 5]
    build, _ = _ground_building(11.11, lines)
    rec = GL.apply(build)
    b = build.building
    assert rec["chosen"] is None and rec["z"] == -0.15
    assert b["site"]["ground"]["levels"][0]["z"]["method"] == "assumed"
    assert [x["kind"] for x in b["needs_review"]] == ["ground_doors"]


def test_a_ground_at_the_doors_or_a_basement_under_the_ground_stays():
    for gz in (-2.5, -0.15, 1.0):          # 1.0: buries the basement's doors only (a basement may be under the ground)
        build, conflicts = _ground_building(gz, LINES)
        assert GL.apply(build) is None and not conflicts
        assert build.building["site"]["ground"]["levels"][0]["z"]["value"] == gz


def test_the_ground_rule_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("WENART_RULES_OFF", "ground_doors")
    build, _ = _ground_building(11.11, LINES)
    assert GL.apply(build) is None
    assert build.building["site"]["ground"]["levels"][0]["z"]["value"] == 11.11


# --------------------------------------------------------------------------- FC-01, FC-02, FC-03: lift landing doors
def _room(rid, label, rtype, poly, level="L0"):
    return {"id": rid, "level_id": level, "label": label, "room_type": rtype, "polygon": poly,
            "area_computed": round(Polygon(poly).area, 3)}


def _wall(wid, a, b, level="L0", t=0.2, exterior=False):
    return {"id": wid, "level_id": level, "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def _box(x0, y0, x1, y1, level, prefix):
    return [_wall(f"{prefix}_s", (x0, y0), (x1, y0), level, 0.2, True),
            _wall(f"{prefix}_e", (x1, y0), (x1, y1), level, 0.2, True),
            _wall(f"{prefix}_n", (x1, y1), (x0, y1), level, 0.2, True),
            _wall(f"{prefix}_w", (x0, y1), (x0, y0), level, 0.2, True)]


def _bld(levels):
    return {"levels": [{"id": lid, "label": lid, "order": k, "elevation": 3.0 * k, "ceiling_height": 2.7}
                       for k, lid in enumerate(levels)],
            "walls": [], "rooms": [], "openings": [], "furniture": [], "symbols": [], "slabs": [], "warnings": [],
            "site": {"entrances": []}, "level_inference": {}}


def test_a_stair_hall_labelled_after_a_shaft_is_the_core_and_takes_the_landing_door():
    """FC-01 (real19): the stair hall reads 'Şaft' (a small shaft drawn in its corner); it holds the core stair and
    touches the lift: it is the core; the landing door goes onto it and the inferred door into the unknown room goes."""
    b = _bld(("L0",))
    b["walls"] = _box(0, 0, 14, 8, "L0", "wb") + [
        _wall("L0_4", (4, 0), (4, 8)), _wall("L0_8", (8, 0), (8, 8)), _wall("L0_k", (0, 4), (4, 4)),
        _wall("L0_l1", (6.4, 6), (8, 6)), _wall("L0_l2", (6.4, 6), (6.4, 8)), _wall("L0_e", (8, 4), (14, 4))]
    hall = [[4.1, 0.1], [7.9, 0.1], [7.9, 5.9], [6.3, 5.9], [6.3, 7.9], [4.1, 7.9]]
    b["rooms"] = [_room("r_kit", "Mutfak", "kitchen", _rect(0.1, 0.1, 3.9, 3.9)),
                  _room("r_liv", "Salon", "living", _rect(0.1, 4.1, 3.9, 7.9)),
                  _room("r_saft", "Şaft", "shaft", hall),
                  _room("r_lift", "Asansör", "shaft", _rect(6.5, 6.1, 7.9, 7.9)),
                  _room("r_antre", "Antre", "hall", _rect(8.1, 0.1, 13.9, 3.9)),
                  _room("r_oda", "Oda", "unknown", _rect(8.1, 4.1, 13.9, 7.9))]
    b["furniture"] = [{"id": "f_st", "level_id": "L0", "type": "stair",
                       "footprint": {"center": [5.2, 3.0], "size": [1.8, 4.0], "rotation_deg": 0.0}}]
    b["openings"] = [
        {"id": "d_w", "type": "door", "level_id": "L0", "wall_id": "L0_4", "center": [4.0, 2.0], "width": 1.0,
         "evidence": [{"method": "vector"}]},
        {"id": "d_e", "type": "door", "level_id": "L0", "wall_id": "L0_8", "center": [8.0, 2.0], "width": 1.0,
         "evidence": [{"method": "vector"}]},
        {"id": "d_r_lift_lift", "type": "door", "level_id": "L0", "wall_id": "L0_8", "center": [8.0, 7.0],
         "width": 0.9, "operation": "sliding", "lift_door": True,
         "evidence": [{"method": "inferred", "rule": "lift_door"}]}]
    level = CP.Level(b, "L0")
    assert "r_saft" in CR.core_rooms(b, level)
    rec = CR.fix_lift_doors(b, B.IdCounter().next, True)
    ids = {o["id"] for o in b["openings"]}
    assert "d_r_lift_lift" not in ids and len(rec["added"]) == 1
    new = next(o for o in b["openings"] if o["id"] == rec["added"][0]["opening"])
    assert new["wall_id"] in ("L0_l1", "L0_l2") and new["lift_door"]


def _shop_storey(lid, door):
    walls = _box(0, 0, 10, 6, lid, f"w{lid}") + [_wall(f"{lid}_x2", (2, 0), (2, 6), lid),
                                                 _wall(f"{lid}_n", (2, 2), (4, 2), lid),
                                                 _wall(f"{lid}_x4", (4, 0), (4, 6), lid)]
    rooms = [_room(f"{lid}_shop", "Dükkan", "other", _rect(0.1, 0.1, 1.9, 5.9), lid),
             _room(f"{lid}_kit", "Mutfak", "kitchen", _rect(2.1, 2.1, 3.9, 5.9), lid),
             _room(f"{lid}_lift", "Asansör", "shaft", _rect(2.1, 0.1, 3.9, 1.9), lid),
             _room(f"{lid}_saft", "Şaft", "shaft", _rect(4.1, 0.1, 9.9, 5.9), lid)]
    ops = [{"id": f"d_{lid}_lift", "type": "door", "level_id": lid, "wall_id": f"{lid}_x4", "center": [4.0, 1.0],
            "width": 0.9, "operation": "sliding", "lift_door": True, "evidence": [{"method": "vector"}]}] if door else []
    return walls, rooms, ops


def test_the_lift_door_goes_where_the_storey_above_has_it_whatever_the_hall_is_read_as():
    """FC-02 (real17): the entrance hall beside the lift reads as a shaft; the storey above has the lift's door on that
    face: the door goes there (stacked), never into the shop with its own stair or the kitchen."""
    b = _bld(("L0", "L1"))
    for lid, door in (("L0", False), ("L1", True)):
        w, r, o = _shop_storey(lid, door)
        b["walls"] += w
        b["rooms"] += r
        b["openings"] += o
    b["furniture"] = [{"id": "f_shop", "level_id": "L0", "type": "stair",
                       "footprint": {"center": [1.0, 4.0], "size": [1.0, 2.5], "rotation_deg": 0.0}}]
    rec = CR.fix_lift_doors(b, B.IdCounter().next, True)
    added = [o for o in b["openings"] if o["level_id"] == "L0"]
    assert len(added) == 1 and added[0]["wall_id"] == "L0_x4" and added[0].get("landing_stacked")
    assert abs(added[0]["center"][1] - 1.0) < 0.05
    assert any(r.get("room") == "L0_saft" for r in rec["review"])
    core = CR.core_rooms(b, CP.Level(b, "L0"))
    assert "L0_saft" in core and "L0_shop" not in core
    assert not [x for x in b.get("needs_review") or [] if x["kind"] == "lift_no_landing_door"]


def test_a_lift_with_no_face_to_take_a_door_is_asked():
    b = _bld(("L0",))
    w, r, _o = _shop_storey("L0", False)
    r = [x for x in r if x["id"] != "L0_saft"] + [_room("L0_bed", "Yatak Odası", "bedroom", _rect(4.1, 0.1, 9.9, 5.9))]
    b["walls"], b["rooms"] = w, r
    CR.fix_lift_doors(b, B.IdCounter().next, True)
    assert [x["kind"] for x in b["needs_review"]] == ["lift_no_landing_door"]


def test_plaster_stubs_are_no_jambs():
    """FC-03 (real10 C0034): a 3.5 cm panel stub and a 4 cm plaster piece beside a landing gap are no jambs."""
    b = _bld(("L0",))
    b["walls"] = [_wall("L0_l1", (6.0, 6.0), (9.0, 6.0)), _wall("st1", (7.07, 6.06), (7.105, 6.06), t=0.05),
                  _wall("st2", (7.99, 6.14), (7.99, 6.18), t=0.04)]
    b["rooms"] = [_room("r_lift", "Asansör", "shaft", _rect(6.6, 6.1, 8.4, 7.9))]
    gapo = {"id": "g", "type": "opening", "level_id": "L0", "wall_id": "L0_l1", "center": [7.47, 6.0], "width": 0.9,
            "evidence": [{"method": "derived"}]}
    b["openings"] = [gapo]
    assert CR._jambs(CP.Level(b, "L0"), gapo) is None


# --------------------------------------------------------------------------- S1F-POD-R01, FC-05, P02, R03, CODE-02
def _copy_building(elevation=3.0):
    b = _bld(("L0", "L1"))
    b["levels"][1].update(typical_of="L0", storey_inference={"rule": "type_default"}, elevation=elevation,
                          reading_places=[{"kind": "unplaced_label", "text": "ANTRE", "at": [2.0, -1.0]}])
    for lid in ("L0", "L1"):
        b["walls"] += _box(0, 0, 10, 6, lid, f"w{lid}") + [_wall(f"{lid}_m", (5, 0), (5, 6), lid),
                                                           _wall(f"{lid}_f", (12, 0), (12, 3), lid, 0.2, True)]
        b["rooms"] += [_room(f"{lid}_bed", "Yatak Odası", "bedroom", _rect(0.1, 0.1, 4.9, 5.9), lid),
                       _room(f"{lid}_liv", "Salon", "living", _rect(5.1, 0.1, 9.9, 5.9), lid)]
        b["openings"] += [
            {"id": f"d_{lid}_lost", "type": "door", "level_id": lid, "wall_id": f"w{lid}_s", "center": [2.0, 0.0],
             "width": 0.9, "height": 2.1, "evidence": [{"method": "vector"}]},
            {"id": f"d_{lid}_out", "type": "door", "level_id": lid, "wall_id": f"w{lid}_e", "center": [10.0, 3.0],
             "width": 0.9, "height": 2.1, "evidence": [{"method": "vector"}]},
            {"id": f"d_{lid}_air", "type": "door", "level_id": lid, "wall_id": f"{lid}_f", "center": [12.0, 1.5],
             "width": 0.9, "height": 2.1, "evidence": [{"method": "vector"}]}]
    return b


def test_copied_storey_doors_keep_lost_rooms_lose_doors_into_the_air():
    b = _copy_building()
    rec = CP.copy_doors(b)
    by = {o["id"]: o for o in b["openings"]}
    acts = {x["opening"]: x["action"] for x in rec}
    assert acts == {"d_L1_lost": "kept", "d_L1_out": "window", "d_L1_air": "removed"}
    assert by["d_L1_lost"]["type"] == "door" and by["d_L1_out"]["type"] == "window" and "d_L1_air" not in by
    assert next(w for w in b["walls"] if w["id"] == "L1_f")["facade_remnant"]["rule"] == "copy_door_window"
    assert [x["kind"] for x in b["needs_review"]] == ["copy_door_lost_room"]
    assert {o["id"] for o in b["openings"] if o["level_id"] == "L0" and o["type"] == "door"} == \
        {"d_L0_lost", "d_L0_out", "d_L0_air"}                                     # the drawn storey is never touched


def test_copied_doors_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("WENART_RULES_OFF", "copy_door_window")
    b = _copy_building()
    rec = CP.copy_doors(b)
    assert {x["opening"]: x["action"] for x in rec} == {"d_L1_lost": "kept"}
    assert all(o["type"] == "door" for o in b["openings"])
    assert any(g["rule"] == "copy_door_window" for g in b["level_inference"]["guarded"])


def test_a_copied_storey_at_the_ground_or_the_main_entrance_is_never_made_a_window():
    b = _copy_building()
    b["site"]["ground"] = {"levels": [{"side": "all", "z": {"value": 2.9, "method": "vector"}}]}
    assert CP.copy_doors(b) == []                                             # L1 stands at the street
    b = _copy_building()
    b["site"]["entrances"] = [{"door_id": "d_L1_out", "level_id": "L1", "main": True}]
    rec = CP.copy_doors(b)
    assert "d_L1_out" not in {x["opening"] for x in rec}
    assert next(o for o in b["openings"] if o["id"] == "d_L1_out")["type"] == "door"
    assert b["site"]["entrances"][0]["door_id"] == "d_L1_out"


# --------------------------------------------------------------------------- S1F-POD-P05: balcony doors
def test_a_door_onto_a_balcony_is_no_way_into_the_building():
    from wenart.reading_check import sense as SN

    b = _bld(("L0",))
    b["walls"] = _box(0, 0, 10, 6, "L0", "w")
    b["rooms"] = [_room("r_liv", "Salon", "living", _rect(0.1, 0.1, 9.9, 5.9))]
    b["openings"] = [{"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [5.0, 0.0],
                      "width": 0.9, "evidence": [{"method": "vector"}], "entrance_refused": "x"}]
    b["site"]["outdoor_spaces"] = [{"id": "os_L0_balkon", "kind": "balcony"}]
    b["site"]["entrances"] = [{"door_id": "d1", "level_id": "L0", "rise": 0.15, "onto": "os_L0_balkon",
                               "main": False}]
    found = SN.no_entrance(b)
    assert [f["rule"] for f in found] == ["no_entrance"] and found[0]["severity"] == "major"
    b["site"]["outdoor_spaces"][0]["kind"] = "porch"                            # a porch is an entrance's landing
    assert SN.no_entrance(b) == []


# --------------------------------------------------------------------------- FC-04: thin partitions flagged exterior
def test_a_thin_partition_flagged_exterior_takes_no_inferred_window():
    b = _bld(("L0",))
    b["walls"] = [dict(w, thickness=0.25) for w in _box(0, 0, 10, 6, "L0", "w")] + \
        [_wall("thin", (5, 0), (5, 6), t=0.10, exterior=True)]            # the leaking outline's flag
    b["rooms"] = [_room("r_bed", "Oda", "bedroom", _rect(0.15, 0.15, 4.95, 5.85))]
    new = CP.infer_level(b, "L0", {}, dict(CP.DEFAULT_SIZES), "defaults", B.IdCounter().next)
    assert new and all(o["wall_id"] != "thin" for o in new)


# --------------------------------------------------------------------------- CODE-01: the levels model's rebuild
def _ent(door, main=False, rule=None):
    return {"door_id": door, "level_id": "L0", "main": main, "main_reason": "x" if main else None,
            "evidence": [{"rule": rule}] if rule else []}


def test_a_rebuild_of_the_entrances_keeps_the_completions_decisions():
    b = _bld(("L0",))
    b["openings"] = [{"id": d, "type": "door", "level_id": "L0"} for d in ("d1", "d2", "d3")]
    b["openings"][0]["entrance_refused"] = {"reason": "a room behind it"}
    old = [_ent("d2", True, "inferred_entrance"), _ent("d3")]
    b["site"]["entrances"] = [_ent("d1", True), _ent("d3")]                    # what infer_levels made again
    LM.keep_completion_entrances(b, old)                                               # no completion record yet: unchanged
    assert [e["door_id"] for e in b["site"]["entrances"]] == ["d1", "d3"]
    b["level_inference"]["core_rules"] = {"entrances": {"refused": [], "added": [], "main": None, "open": None}}
    LM.keep_completion_entrances(b, old)
    ents = {e["door_id"]: e for e in b["site"]["entrances"]}
    assert set(ents) == {"d2", "d3"} and ents["d2"]["main"] and not ents["d3"]["main"]
    b["site"]["entrances"] = [_ent("d3", True)]
    LM.keep_completion_entrances(b, [_ent("d3")])                                       # the completion left no main
    assert not b["site"]["entrances"][0]["main"]


# --------------------------------------------------------------------------- FC-07, CODE-06, CODE-04, CODE-07, FC-06
def _rf():
    from tests import test_review_fixes_20261113 as RF
    return RF


def test_a_window_drawn_in_a_flats_only_link_is_that_window_and_the_entrance_is_asked():
    """FC-07: the flat's entrance door is not read; its bathroom's 1.6 m gap to the core holds a drawn 0.5 m window:
    the gap is that window, and the flat's missing entrance is a review record."""
    RF = _rf()
    b = RF.core_building(("L0",))
    b["openings"] = [o for o in b["openings"] if o["id"] != "L0_ea"]           # the east flat's entrance not read
    b["openings"].append(RF.gap("g_bath", "L0_8", (8.0, 5.0), 1.6))
    b["rooms"] = [r for r in b["rooms"] if r["id"] != "L0_bed"] + [RF.room("L0_bath2", "Banyo", "bathroom",
                                                                           RF.rect(8.1, 4.1, 10.9, 7.9))]
    out = CR.close_core_gaps(b, {}, {"L0": [{"text": "P150/50", "x": 8.0, "y": 5.1}]})    # an upper-case tag
    win = next(o for o in b["openings"] if o["id"] == "g_bath")
    assert out["windows"] and win["type"] == "window" and win["drawn_type"] == "opening"
    assert any(r["opening"] == "g_bath" and "entrance door" in r["reason"] for r in out["review"])


def test_a_record_of_a_removed_door_or_a_lift_door_is_no_entrance():
    """CODE-04: the record's door is gone (a core rule removed it) or is the lift's landing door: the entrance rule
    still infers the building's entrance."""
    RF = _rf()
    b = RF.entrance_building()
    b["site"]["entrances"] = [{"door_id": "gone", "level_id": "L-1", "room_id": "L-1_hall", "rise": 0.0,
                               "main": True},
                              {"door_id": "L-1_ld", "level_id": "L-1", "room_id": "L-1_lift", "rise": 0.0}]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert [a["level_id"] for a in rec["added"]] == ["L-1"]
    assert {e["door_id"] for e in b["site"]["entrances"]} == {rec["added"][0]["door"]}


def test_a_refused_main_entrance_hands_main_to_the_best_way_in():
    """CODE-07: the main entrance is a bathroom's door (refused): the core hall's door becomes the main one."""
    RF = _rf()
    b = RF.entrance_building()
    b["openings"] += [RF.op("d_bath", "door", "wL-1_n", (12.5, 8.0), 0.8, "L-1"),
                      RF.op("d_hall", "door", "wL-1_s", (6.0, 0.0), 1.2, "L-1")]
    b["site"]["entrances"] = [
        {"door_id": "d_bath", "level_id": "L-1", "room_id": "L-1_bath", "rise": 0.0, "main": True},
        {"door_id": "d_hall", "level_id": "L-1", "room_id": "L-1_hall", "rise": 0.1, "main": False}]
    rec = CR.fix_entrances(b, B.IdCounter().next, {})
    assert rec["main"]["was"] == "d_bath" and rec["main"]["now"] == "d_hall"
    assert [e["door_id"] for e in b["site"]["entrances"] if e["main"]] == ["d_hall"]


def test_a_drawn_door_named_bina_girisi_is_the_entrance_whatever_the_ground_says():
    """FC-06 (real17): the ground is misread metres up; the drawn door beside the stacked texts 'BİNA' 'GİRİŞİ' is
    the building's entrance: no question, no inferred door."""
    RF = _rf()
    b = RF.core_building(("L0", "L1"))
    b["site"] = {"ground": {"levels": [{"z": {"value": 3.4}}]}, "entrances": []}
    b["openings"].append(RF.op("d_front", "door", "wL0_s", (6.0, 0.0), 1.5))
    b["site"]["entrances"] = [{"door_id": "d_front", "level_id": "L0", "room_id": "L0_shaft", "rise": 0.0,
                               "below_ground": True}]
    texts = {"L0": [{"text": "BİNA", "x": 6.2, "y": -0.6}, {"text": "GİRİŞİ", "x": 6.2, "y": -0.9}]}
    rec = CR.fix_entrances(b, B.IdCounter().next, {}, texts)
    assert rec["open"] is None and rec["added"] == [] and rec["main"]["now"] == "d_front"


# --------------------------------------------------------------------------- CODE-05: one machine-room test
LIFTS = ("MAKİNESİZ ASANSÖR", "Makinasız Asansör", "Makine Dairesiz Asansör", "ASANSÖR (MAKİNE DAİRESİZ)",
         "MRL Asansör", "Asansör")
MACHINES = ("Asansör Makine Dairesi", "Asansör Makina Dairesi", "Asansör Makine Odası", "Lift machine room",
            "Asansör Mahali", "ASANSÖR MAKİNA HİDROLİK")


@pytest.mark.parametrize("label", LIFTS + MACHINES)
def test_one_machine_room_test_in_the_reader_the_storeys_and_the_completion(label):
    from wenart.ingest import twins as TW
    from wenart.sheets import storeys as ST

    lift = label in LIFTS
    sq = _rect(0, 0, 1.6, 1.6)
    assert CP.is_lift({"label": label, "polygon": sq}) is lift
    assert ST.plan_signals(SimpleNamespace(texts=[SimpleNamespace(text=label)], features={}))["lifts"] == int(lift)
    rooms = [{"id": "s", "level_id": "L0", "label": label, "room_type": "shaft", "polygon": sq},
             {"id": "h", "level_id": "L0", "label": "Kat Holü", "room_type": "hall", "polygon": _rect(1.7, 0, 5, 3)}]
    walls = [{"id": "w", "level_id": "L0", "start": [1.65, 0.0], "end": [1.65, 3.0], "thickness": 0.1}]
    openings = []
    TW.lift_doors(rooms, openings, walls, [])
    assert bool(openings) is lift


# --------------------------------------------------------------------------- FC-09: a section roof of another datum
def test_a_roof_from_a_section_of_another_datum_keeps_its_own_rise_on_the_added_top_storey():
    b = _bld(("L0", "L1", "L2", "L3", "L4", "L5"))
    b["warnings"] = ["the section's heights are no storeys (L-1 ceiling 14.05 m): the floors take the assumed heights"]
    b["roof"] = {"type": "gambrel", "over_level_id": "L1",
                 "eaves_height": {"value": 13.622, "note": "3.27 m above the top floor"},
                 "ridge_height": {"value": 15.744, "note": "5.39 m above the top floor"},
                 "planes": [{"id": "p1", "points": [[0, 0, 13.622], [1, 1, 15.744]]}]}
    build = SimpleNamespace(building=b, warn=lambda m: None)
    why = CP._rebase_roof(build, b, {"L2", "L3", "L4", "L5"})
    assert why and "datum" in why and b["roof"]["over_level_id"] == "L5"
    assert abs(b["roof"]["eaves_height"]["value"] - 18.27) < 0.01
    assert abs(b["roof"]["ridge_height"]["value"] - (18.27 + 2.122)) < 0.01
