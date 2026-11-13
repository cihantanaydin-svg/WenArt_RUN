"""The fixes of the stage-1 fix check (13 Nov 2026, findings S1F-POD-*, FC-*, CODE-*): CPU only, synthetic fixtures."""
from types import SimpleNamespace

import pytest
from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart.blender import parametric as P
from wenart.ingest import completion as CP
from wenart.ingest import core_rules as CR
from wenart.ingest import ground_lines as GL


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
