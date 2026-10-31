"""Dormers over drawn doors the roof leaves too low (31 Oct 2026; the user on real04 run 20261030-181158-full, the attic
bathroom render cam_r_L1_banyo_1: "There is something seriously wrong here, investigate what happened and fix it, the
door the toilet not making sense at all"). The bathroom doors d_L1_004 / d_L1_005 (2.10 m drawn, 1.00 m of head room
under the inferred mansard) were lowered to 1 m hatches; a drawn door is source evidence that a full-height door fits,
so the build now raises a shed dormer over it (wenart/blender/dormers.py).

CPU tests on a synthetic attic: a gable roof (30 degrees, eaves 1.0 m over the attic floor at 3.0 m, ridge along x at
y = 5), its outer walls x, y in [0, 10], a wall ``w5`` square to the north eaves (x = 5, y 6 .. 10) between the hall
(x < 5) and the bath (x > 5), and the real04 building when it is on this machine."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import door_states as DS
from wenart.blender import dormers as DM
from wenart.blender import geom2d
from wenart.blender import model_review as MR
from wenart.blender import roof as R
from wenart.blender import under_roof as UR

TAN = math.tan(math.radians(30.0))
SOUTH = (0.0, TAN, 4.0 + 0.5 * TAN)            # rises from the south eaves (y = -0.5) to the ridge
NORTH = (0.0, -TAN, 4.0 + 10.5 * TAN)          # falls to the north eaves (y = 10.5)
OUTLINE = [(-0.5, -0.5), (10.5, -0.5), (10.5, 10.5), (-0.5, 10.5)]


def roof_model(openings=()) -> dict:
    ridge = SOUTH[2] + 5.0 * TAN
    planes = [{"id": "rp_south", "points": [(-0.5, -0.5, 4.0), (10.5, -0.5, 4.0), (10.5, 5.0, ridge),
                                             (-0.5, 5.0, ridge)]},
              {"id": "rp_north", "points": [(-0.5, 5.0, ridge), (10.5, 5.0, ridge), (10.5, 10.5, 4.0),
                                             (-0.5, 10.5, 4.0)]}]
    return {"type": "gable", "over_level_id": "L1", "planes": planes, "planes_source": "derived",
            "equations": [SOUTH, NORTH], "outline": list(OUTLINE), "openings": list(openings), "thickness": 0.2,
            "convex": True, "eaves_z": 4.0, "ridge_z": ridge, "assumed": [], "warnings": [], "notes": []}


def wall(wid, a, b, t=0.2, exterior=False) -> dict:
    return {"id": wid, "level_id": "L1", "start": list(a), "end": list(b), "thickness": t, "exterior": exterior}


def door(oid, x, y, wall_id="w5", height=2.1, assumed=True, width=0.8) -> dict:
    return {"id": oid, "type": "door", "level_id": "L1", "wall_id": wall_id, "center": [x, y], "width": width,
            "height": height, "sill_height": None, "assumed": ["height"] if assumed else []}


def attic(openings, model=None) -> tuple[dict, dict, dict]:
    """``(building, level, roof model)``: the level's ceiling planes as the build sets them."""
    model = model or roof_model()
    level = {"id": "L1", "elevation": 3.0, "ceiling_height": 2.6}
    level["ceiling_planes"] = [list(p) for p in R.ceiling_planes(model, level)]
    walls = [wall("wS", (0, 0), (10, 0), exterior=True), wall("wE", (10, 0), (10, 10), exterior=True),
             wall("wN", (10, 10), (0, 10), exterior=True), wall("wW", (0, 10), (0, 0), exterior=True),
             wall("w5", (5, 6), (5, 9.9), t=0.1), wall("w6", (5, 6), (9.9, 6), t=0.1)]
    rooms = [{"id": "hall", "level_id": "L1", "room_type": "hall",
              "polygon": [[0.1, 0.1], [4.95, 0.1], [4.95, 9.9], [0.1, 9.9]]},
             {"id": "bath", "level_id": "L1", "room_type": "bathroom",
              "polygon": [[5.05, 6.05], [9.9, 6.05], [9.9, 9.9], [5.05, 9.9]]},
             {"id": "bed", "level_id": "L1", "room_type": "bedroom",
              "polygon": [[5.05, 0.1], [9.9, 0.1], [9.9, 5.95], [5.05, 5.95]]}]
    b = {"levels": [level], "walls": walls, "rooms": rooms, "openings": list(openings), "furniture": [], "decor": []}
    return b, level, model


# ------------------------------------------------------------------------------------- which doors need a dormer

def test_only_a_door_no_lowering_nor_slide_fixes_needs_a_dormer():
    cases = {"low": 9.2, "slides": 8.6, "lowered": 8.1, "fits": 7.2}
    rooms, needed, changes = {}, {}, {}
    for oid, y in cases.items():
        b, level, model = attic([door(oid, 5.0, y)])
        rooms[oid] = DS.head_room(b["openings"][0], b["walls"][4], level)
        needed[oid] = [it["opening"]["id"] for it in DM.needs(b, level, model)]
        changes[oid] = DS.plan_under_roof(b)
    assert rooms["low"] < DS.MIN_CLEAR_M and rooms["slides"] < DS.MIN_CLEAR_M
    assert DS.MIN_CLEAR_M <= rooms["lowered"] < 2.1 and rooms["fits"] >= 2.1
    assert needed == {"low": ["low"], "slides": [], "lowered": [], "fits": []}
    # the existing rule keeps the others: the slid door slides, the lowered one is lowered (both fit)
    assert changes["slides"][0]["fits"] and changes["slides"][0]["moved_m"] < 0.0
    assert changes["lowered"][0]["fits"] and changes["lowered"][0]["moved_m"] == 0.0
    assert changes["fits"] == []
    b, level, model = attic([door("low", 5.0, 9.2)])
    assert "no spot within 0.5 m" in DM.needs(b, level, model)[0]["why"]
    # a level without a sloped ceiling, a roof over another level, a stepped roof: none
    flat = dict(level, ceiling_planes=None)
    assert DM.needs(b, flat, model) == []
    assert DM.needs(b, level, dict(model, over_level_id="L2")) == []
    assert DM.needs(b, level, dict(model, parts=[{}])) == []


# ------------------------------------------------------------------------------------------------- the dormer box

def test_the_dormer_box_runs_from_the_door_out_to_the_eaves():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    planned = DM.plan(b, level, model)
    assert planned["refused"] == [] and len(planned["dormers"]) == 1
    d = planned["dormers"][0]
    assert d["id"] == "dormer_d1" and d["serves"] == ["d1"] and d["kinds"] == ["door"]
    assert d["by"] == "architect" and d["source"] == "inferred" and d["rule"] == DM.RULE
    assert "source evidence" in d["reason"] and "d1" in d["reason"]
    # aligned with the north plane: downhill +y, the contour along x
    assert d["d"] == pytest.approx([0.0, 1.0]) and abs(d["e"][0]) == pytest.approx(1.0)
    # wide enough: the door's wall (0.1) and 0.75 m past each face, a 0.12 m cheek each side
    xs = sorted(p[0] for p in d["footprint"])
    assert xs[0] == pytest.approx(5.0 - 0.05 - 0.75 - 0.12) and xs[-1] == pytest.approx(5.0 + 0.05 + 0.75 + 0.12)
    assert d["width_m"] == pytest.approx(1.84, abs=1e-3)
    # its front on the facade (the north wall's outer face, y = 10.1), its hole cut out to the eaves
    ys = sorted(p[1] for p in d["footprint"])
    assert d["flush"] and ys[-1] == pytest.approx(10.1) and max(p[1] for p in d["hole"]) == pytest.approx(10.55)
    # the preferred clearance and the steepest roof that fits: the ceiling 0.15 m over the 2.10 m door
    assert d["head_clear_m"] == 0.15 and d["pitch_deg"] == 5.0
    assert d["ceiling_m"] == pytest.approx(2.25, abs=1e-6)
    assert geom2d.plane_z(d["ceiling"], 5.0, d["d_need"] + d["origin"][1]) == pytest.approx(5.25, abs=1e-6)
    # its back is where its roof meets the main roof: there the two tops and the two undersides meet
    yb = ys[0]
    assert geom2d.plane_z(d["top"], 5.0, yb) == pytest.approx(geom2d.plane_z(NORTH, 5.0, yb), abs=2e-3)
    v = 0.2 * math.sqrt(1.0 + TAN * TAN)
    assert geom2d.plane_z(d["under"], 5.0, yb) == pytest.approx(geom2d.plane_z(NORTH, 5.0, yb) - v, abs=2e-3)
    assert 7.0 < yb < 8.0                                       # the 5 degree roof meets the 30 degree one at 7.6
    # the roof falls to the front, never into the main roof
    assert d["top"][1] < 0.0 and geom2d.plane_z(d["top"], 5.0, 10.1) > geom2d.plane_z(NORTH, 5.0, 10.1) + 1.0


def test_the_door_keeps_its_height_under_its_dormer():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    got = DM.raise_dormers(b, level, model)
    o = b["openings"][0]
    assert [d["id"] for d in got["dormers"]] == ["dormer_d1"] and not got["warnings"]
    assert o["dormer"]["id"] == "dormer_d1" and o["dormer"]["by"] == "architect"
    assert any(e.get("rule") == DM.RULE for e in o["evidence"])
    row = next(a for a in got["assumed"] if a["kind"] == "dormer")
    assert row["by"] == "architect" and row["inferred"] and row["parent"] == "d1"
    assert row["value"]["serves"] == ["d1"]
    walls = {w["id"]: w for w in b["walls"]}
    assert DS.head_room(o, walls["w5"], level) >= 2.1
    assert DS.plan_under_roof(b) == []                          # never lowered
    changes, _assumed, warnings = DS.apply_under_roof(b)
    assert changes == [] and warnings == [] and o["height"] == 2.1 and "under_roof" not in o
    # D5's role height under the slope follows the dormer's head room
    h, why = DS._door_height(b, o, walls["w5"], level, DS.STANDARD_HEIGHT_M, "a standard door")
    assert h == DS.STANDARD_HEIGHT_M
    # its open leaf stays under the dormer's ceiling
    states = DS.plan_states(b, {"family": "modern"})
    assert states["d1"]["state"] == "open"
    for poly in states["d1"].get("leaf_polys") or []:
        assert DS.leaf_under_ceiling(poly, DS.leaf_head(o, level)) is None
    assert UR.door_problems(b) == [] and UR.dormer_problems(b) == []
    # planned again (the build's second prepare): the same dormer, from the bare roof
    again = DM.raise_dormers(b, level, model)
    assert [d["id"] for d in again["dormers"]] == ["dormer_d1"] and len(level["ceiling_dormers"]) == 1


def test_without_its_dormer_the_old_rule_lowers_it():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    c = DS.plan_under_roof(b)[0]
    assert not c["fits"] and c["height"] < 1.3 and "dormer" in c["reason"]


# ------------------------------------------------------------------------------- the ceiling planes and the walls

def test_the_ceiling_planes_include_the_dormer():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    DM.raise_dormers(b, level, model)
    d = model["dormers"][0]
    raise_ = level["ceiling_dormers"][0]
    assert raise_["id"] == "dormer_d1" and raise_["planes"][0] == pytest.approx(d["ceiling"])
    assert raise_["planes"][1] == pytest.approx([0.0, 0.0, 5.6])
    # under the dormer its ceiling, beside it the slope (the old ceiling)
    inside, beside = (5.0, 9.5), (6.5, 9.5)
    assert geom2d.level_ceiling_z(level, *inside) == pytest.approx(geom2d.plane_z(d["ceiling"], *inside))
    assert geom2d.level_ceiling_z(level, *beside) == pytest.approx(geom2d.surface_z(level["ceiling_planes"], *beside))
    assert geom2d.level_ceiling_z(level, *inside) > geom2d.surface_z(level["ceiling_planes"], *inside) + 0.8
    # every reader of the level's ceiling sees it: the furniture caps, the crossing check
    from wenart.blender import furniture as F
    piece = {"id": "f", "type": "cabinet", "footprint": {"center": [5.4, 9.3], "size": [0.4, 0.4],
                                                         "rotation_deg": 0.0}}
    assert F.under_roof_cap(level, piece, 3.0) == pytest.approx(geom2d.plane_z(d["ceiling"], 5.4, 9.5) - 3.0
                                                                - F.UNDER_ROOF_CLEAR_M, abs=1e-3)
    frame = {"name": "d1_frame", "kind": "door", "element_id": "d1", "level_id": "L1",
             "box3d": {"center": [5.0, 9.2, 4.06], "size": [0.15, 0.9, 2.12], "rotation_deg": 0.0}}
    assert UR.crossings([frame], b, model) == []
    # the room's ceiling: the bath's area exactly, with the dormer's ceiling over the dormer's part
    room = b["rooms"][1]
    cv, cf = DM.room_ceiling(room["polygon"], [], level["ceiling_planes"], level["ceiling_dormers"])
    assert geom2d.faces_area(cv, cf) == pytest.approx(G.polygon_area(room["polygon"]), abs=1e-6)
    under = [f for f in cf if G.point_in_polygon(geom2d.face_center(cv, f)[:2], d["inner"])]
    assert under and all(abs(cv[i][2] - geom2d.plane_z(d["ceiling"], cv[i][0], cv[i][1])) < 1e-3
                         for f in under for i in f)          # (its back edge is shared with the slope's, 0.1 mm)
    flat = DM.room_ceiling(room["polygon"], [], level["ceiling_planes"], [])
    assert geom2d.faces_area(*flat) == pytest.approx(G.polygon_area(room["polygon"]), abs=1e-6)


def test_the_walls_under_the_dormer_rise_to_its_ceiling():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    DM.raise_dormers(b, level, model)
    d = model["dormers"][0]
    walls = [w for w in b["walls"] if w["level_id"] == "L1"]
    cut = R.wall_cut(model, walls)
    spans = cut["wall_spans"]
    assert set(spans) == {"w5", "wN"}                           # the door's wall and the facade under the dormer
    w5 = spans["w5"]
    assert [len(s["planes"]) for s in w5] == [2, 1] and w5[1]["planes"] == [tuple(d["under"])]
    assert w5[0]["t1"] == pytest.approx((d["d_back"] + d["origin"][1] - 6.0) / 3.9, abs=1e-6) and w5[1]["t1"] == 1.0
    assert [len(s["planes"]) for s in spans["wN"]] == [2, 1, 2]
    # the door's head limit at its wall reads the dormer (the roof clip of the openings, E8)
    w5d = next(w for w in walls if w["id"] == "w5")
    assert R.opening_head_limit(model, level, w5d, b["openings"][0]) > 2.15
    assert R.clip_openings_to_roof(b, level, model) == []
    # a caller that gives no walls finds the dormer by the point (cut_planes_for)
    bare = R.wall_cut(model)
    assert R.cut_planes_for(bare, "w5", w5d, (5.05, 9.6)) == [tuple(d["under"])]
    assert R.cut_planes_for(bare, "w5", w5d, (5.05, 6.5)) == bare["planes"]


def test_the_main_roof_is_cut_where_the_dormer_sits():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    DM.raise_dormers(b, level, model)
    d = model["dormers"][0]
    verts, faces, slots = R.roof_solid(model)
    for f, s in zip(faces, slots):
        c = geom2d.face_center(verts, f)
        if s in (R.SLOT_COVERING, R.SLOT_SOFFIT):
            assert not (G.point_in_polygon(c[:2], d["hole"]) and geom2d.distance_to_polygon_edges(c[:2], d["hole"])
                        > 1e-3)
    # the eaves' cut edges in front of the dormer get the fascia
    x0, x1 = min(p[0] for p in d["hole"]), max(p[0] for p in d["hole"])
    cut_edges = [f for f, s in zip(faces, slots) if s == R.SLOT_FASCIA
                 and all(abs(verts[i][0] - x0) < 1e-6 or abs(verts[i][0] - x1) < 1e-6 for i in f)]
    assert cut_edges
    # the roof's top over the door is the dormer's, the underside its underside
    assert R.top_z(model, 5.0, 9.5) == pytest.approx(geom2d.plane_z(d["top"], 5.0, 9.5))
    assert R.underside_z(model, 5.0, 9.5) == pytest.approx(geom2d.plane_z(d["under"], 5.0, 9.5))
    assert R.base_top_z(model, 5.0, 9.5) == pytest.approx(geom2d.plane_z(NORTH, 5.0, 9.5))
    # no gutter across its front, the chimneys keep clear of it
    from wenart.blender import chimney as CH
    from wenart.blender import facade as FA
    north = [e for e in FA.eaves_edges(model) if abs(e["p"][1] - 10.5) < 1e-6]
    assert north and all(not (min(e["p"][0], e["q"][0]) < 5.0 < max(e["p"][0], e["q"][0])) for e in north)
    assert any(h == d["roof_poly"] for h in CH.context(model, b)["holes"])


def test_the_dormer_mesh_has_its_parts():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    DM.raise_dormers(b, level, model)
    d = model["dormers"][0]
    verts, faces, slots = DM.meshes(d, model)
    assert set(slots) == {DM.SLOT_COVER, DM.SLOT_SOFFIT, DM.SLOT_FASCIA, DM.SLOT_CLAD, DM.SLOT_FLASHING}
    # the cheeks stand on the main roof's underside and reach the dormer's underside
    clad = [verts[i] for f, s in zip(faces, slots) if s == DM.SLOT_CLAD for i in f]
    assert max(v[2] for v in clad) == pytest.approx(geom2d.plane_z(d["under"], 5.0, d["d_back"] + d["origin"][1]),
                                                    abs=0.05)
    # the cheeks' outer faces in the facade look, their inner faces in the ceiling's (inside the dormer)
    inner = [f for f, s in zip(faces, slots) if s == DM.SLOT_SOFFIT]
    assert any(abs(abs(verts[f[0]][0] - 5.0) - 0.8) < 1e-6 for f in inner)
    looks = DM.looks_of(d, {"facade": {"material": "render", "colour": "white"},
                            "roof": {"material": "clay_tiles"}})
    assert looks["cover"]["material"] == "standing_seam" and looks["clad"]["material"] == "render"
    rec = DM.manifest_record(d)
    assert rec["serves"] == ["d1"] and rec["by"] == "architect" and rec["source"] == "inferred"
    assert DM.summary(model)["dormers"][0]["id"] == "dormer_d1"


# --------------------------------------------------------------------------------------- windows, merges, refusals

def test_a_drawn_window_crossing_the_roof_gets_a_dormer_an_assumed_one_is_clipped():
    win = {"id": "wn", "type": "window", "level_id": "L1", "wall_id": "wN", "center": [2.5, 10.0], "width": 1.0,
           "height": 1.4, "sill_height": 0.9, "assumed": []}
    b, level, model = attic([win])
    got = DM.needs(b, level, model)
    assert [it["opening"]["id"] for it in got] == ["wn"] and "drawn top" in got[0]["why"]
    planned = DM.plan(b, level, model)
    d = planned["dormers"][0]
    assert d["serves"] == ["wn"] and d["kinds"] == ["window"] and d["flush"]
    DM.apply(b, level, model, planned)
    wall_n = next(w for w in b["walls"] if w["id"] == "wN")
    assert R.opening_head_limit(model, level, wall_n, win) >= 2.3 - 1e-3
    # the same window of assumed height: the roof clip keeps it usable (lower), no dormer
    b2, level2, model2 = attic([dict(win, assumed=["height", "sill_height"])])
    assert DM.needs(b2, level2, model2) == []


def test_two_doors_side_by_side_share_one_dormer():
    walls_extra = [wall("w7", (6.6, 6), (6.6, 9.9), t=0.1)]
    b, level, model = attic([door("d1", 5.0, 9.2), door("d2", 6.6, 9.2, wall_id="w7")])
    b["walls"] += walls_extra
    planned = DM.plan(b, level, model)
    assert len(planned["dormers"]) == 1 and sorted(planned["dormers"][0]["serves"]) == ["d1", "d2"]
    DM.apply(b, level, model, planned)
    assert DS.plan_under_roof(b) == []


def test_a_dormer_into_a_roof_terrace_is_refused_and_the_door_keeps_the_old_rule():
    terrace = {"id": "ro_1", "kind": "terrace", "room_id": None, "polygon": [(3.0, 8.0), (7.0, 8.0), (7.0, 10.5),
                                                                              (3.0, 10.5)]}
    b, level, model = attic([door("d1", 5.0, 9.2)], model=roof_model([terrace]))
    got = DM.raise_dormers(b, level, model)
    assert got["dormers"] == [] and got["refused"][0]["id"] == "d1"
    assert "ro_1" in got["refused"][0]["reason"] and "no dormer could be raised" in got["warnings"][0]
    assert "ceiling_dormers" not in level and model["dormers"] == []
    c = DS.plan_under_roof(b)[0]
    assert not c["fits"] and "no dormer could be raised over it" in c["reason"] and "ro_1" in c["reason"]


def test_the_review_finds_a_dormer_the_scene_lacks():
    b, level, model = attic([door("d1", 5.0, 9.2)])
    DM.raise_dormers(b, level, model)
    manifest = {"objects": [{"name": "roof", "wenart_id": "roof", "kind": "roof"}]}
    probs = UR.dormer_problems(b, manifest)
    assert [p["problem"] for p in probs] == ["dormer_not_built"]
    manifest["objects"].append({"name": "dormer_d1", "wenart_id": "dormer_d1", "kind": "roof", "detail": "dormer"})
    assert UR.dormer_problems(b, manifest) == []
    found, _n = MR.roof_crossings(b, {"objects": manifest["objects"][:1]}, model)
    assert any(f.get("evidence", {}).get("problem") == "dormer_not_built" or "dormer_d1" in f["message"]
               for f in found)


# ----------------------------------------------------------------------------------------------- the real04 case

REAL04 = Path("/home/user/WenArt_RUN/results/baseline/latest/furniture/real04/building_final.json")


def test_real04_bathroom_doors_get_dormers_not_hatches():
    """real04 (the run 20261030-181158-full's building): d_L1_004 / d_L1_005 had 1.00 m of head room under the
    mansard's steep north slope; each gets a dormer on the north facade and keeps its 2.10 m; the play room doors
    d_L1_001 / 002 (1.80 m of head room) keep the old rule (lowered by the clip, no dormer)."""
    if not REAL04.is_file():
        pytest.skip(f"{REAL04} not on this machine")
    from wenart.blender import build as B

    prep = B.prepare(json.loads(REAL04.read_text(encoding="utf-8")), "base", None, style_family="modern")
    ds = {d["id"]: d for d in prep["dormers"]["dormers"]}
    assert set(ds) == {"dormer_d_L1_004", "dormer_d_L1_005"} and prep["dormers"]["refused"] == []
    for d in ds.values():
        assert d["flush"] and d["ceiling_m"] >= 2.10 + 0.05 and 1.5 < d["width_m"] < 2.2
    assert not any(c["opening_id"] in ("d_L1_004", "d_L1_005") for c in prep["clips"])
    vb = prep["building"]
    doors = B.doors_as_designed(vb, {"family": "modern"}, [])
    by = {o["id"]: o for o in vb["openings"]}
    for oid in ("d_L1_004", "d_L1_005"):
        assert by[oid]["height"] == pytest.approx(2.1) and "under_roof" not in by[oid]
        assert by[oid]["leaf_state"]["state"] == "open"
    assert not any("d_L1_004" in w or "d_L1_005" in w for w in doors["warnings"])
    assert by["d_L1_001"]["height"] < 1.85 and "dormer" not in by["d_L1_001"]
    assert UR.door_problems(vb) == []
