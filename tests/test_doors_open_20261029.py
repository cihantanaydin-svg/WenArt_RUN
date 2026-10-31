"""Doors as a designer shows them and see-through walk-ins (29 Oct 2026; lessons UL116, UL117, UL120, UL122, UL125,
UL126; docs/reference_details_20261029.md D1-D5, R1, R28, R31, R37).

The user: "Also we need better doors, not all the doors needs to be closed in default", "Not every single one of them
with the same dimension we can change the dimentions", "look at this dressing room solution see through why we are not
using some similar in our projects?", "Doors looks without frames they need frames", "this dressing could be a see
through dressing room in the both sides argus should have think of this", "You can leave the right door open and show
the dressing room, not all the doors should be closed".

- ``door_states``: open by default (D1), sizes by role and family (D5), the views (UL126), the checks (M29 / U33);
- ``parametric``: the posed leaf, the lock rose, fine vertical grooves, divided lites, the pivot entrance, the frame of
  a door whose leaf is not ours; ``opening_build``: a library model's leaf measured, framed, turned; ``looks``: the
  family's finishes (D2), the divided-lite door (D3), the frameless rule;
- ``wardrobe_fronts`` / ``modules``: see-through wardrobes with garments, the walk-in's bench and mirror;
- the camera model, the architect's D7 / D8, the model review's M29, Argus' U33 and the lessons;
- the real06 run 20261029-100801-full as built: which doors open, their sizes, which wardrobes are see-through.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart.audit import kinds as K
from wenart.audit import lessons as L
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as AR
from wenart.blender import cameras as CAM
from wenart.blender import camsearch as CS
from wenart.blender import door_states as DS
from wenart.blender import looks as LK
from wenart.blender import model_review as MR
from wenart.blender import modules as MOD
from wenart.blender import opening_build as OB
from wenart.blender import opening_models as OM
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.blender import wardrobe_fronts as WF
from wenart.blender import geom2d

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("/home/user/WenArt_RUN")
REAL06 = MAIN / "runs" / "20261029-100801-full" / "results" / "renders" / "real06"
LESSONS = ROOT / "wenart" / "blender" / "architect_lessons.json"

SCANDI = {"family": "scandinavian", "door": {"material": "wood_oak_light"}, "trim": {"material": "painted_wood_white"}}
MODERN = {"family": "modern", "door": {"material": "painted_wood_white"}, "trim": {"material": "painted_wood_white"}}
NO_FAMILY = {"door": {"material": "wood_oak_light"}}


def _door(oid, wall, centre, width=0.8, swing=None, **extra):
    return dict({"id": oid, "type": "door", "level_id": "L0", "wall_id": wall, "center": list(centre),
                 "width": width, "height": 2.1, "assumed": ["height"], "swing_side": swing}, **extra)


def _house():
    """Living | hall | bedroom over bathroom (from the hall), a storage room off the living room, the entrance in the
    south facade into the hall."""
    rooms = [{"id": "r_liv", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [5, 0], [5, 7], [0, 7]]},
             {"id": "r_hall", "level_id": "L0", "room_type": "hall", "polygon": [[5, 0], [7, 0], [7, 7], [5, 7]]},
             {"id": "r_bed", "level_id": "L0", "room_type": "bedroom", "polygon": [[7, 0], [11, 0], [11, 4], [7, 4]]},
             {"id": "r_bath", "level_id": "L0", "room_type": "bathroom", "polygon": [[7, 4], [11, 4], [11, 7], [7, 7]]},
             {"id": "r_sto", "level_id": "L0", "room_type": "storage", "polygon": [[0, 7], [2, 7], [2, 8.5], [0, 8.5]]}]
    walls = [{"id": "w5", "level_id": "L0", "start": [5, 0], "end": [5, 7], "thickness": 0.1},
             {"id": "w7", "level_id": "L0", "start": [7, 0], "end": [7, 7], "thickness": 0.1},
             {"id": "ws", "level_id": "L0", "start": [0, 0], "end": [11, 0], "thickness": 0.3, "exterior": True},
             {"id": "wn", "level_id": "L0", "start": [0, 7], "end": [7, 7], "thickness": 0.1}]
    openings = [_door("d_liv", "w5", (5, 3), 0.9, "r_liv"), _door("d_bed", "w7", (7, 2), 0.8, "r_bed"),
                _door("d_bath", "w7", (7, 5.5), 0.77, "r_bath"), _door("d_sto", "wn", (1, 7), 0.7, "r_sto"),
                _door("d_ent", "ws", (6, 0), 0.8, "r_hall")]
    return {"project": {"id": "house_t"}, "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "walls": walls, "rooms": rooms, "openings": openings, "furniture": [], "decor": [],
            "site": {"entrances": [{"door_id": "d_ent", "main": True}]}}


def _by_id(b):
    return {o["id"]: o for o in b["openings"]}


# ------------------------------------------------------------------------------------------------- D1: open doors

def test_every_interior_door_opens_by_default_the_entrance_does_not():
    """UL116, UL127 ("Leaving all the doors open in default could be a good approach")."""
    b = _house()
    states = DS.plan_states(b, SCANDI)
    for oid in ("d_bed", "d_liv", "d_bath", "d_sto"):
        assert states[oid]["state"] == "open" and states[oid]["angle_deg"] == DS.OPEN_DEG, oid
        assert "UL127" in states[oid]["reason"], oid
    assert states["d_liv"]["role"] == "day" and states["d_bath"]["role"] == "wet"
    assert states["d_ent"]["state"] == "closed" and states["d_ent"]["role"] == "entrance"
    # every choice recorded with its reason, and assumed
    assert all(r["reason"] and r["assumed"] for r in states.values())
    # a style without a family keeps its closed doors (the Milestone 3-9 scenes)
    assert DS.plan_states(b, NO_FAMILY) == {}
    # the documents or an answer (the architect's D9) fix a state; the brief closes them all
    b2 = _house()
    _by_id(b2)["d_bed"]["open_state"] = "closed"
    assert DS.plan_states(b2, SCANDI)["d_bed"]["state"] == "closed"
    b3 = _house()
    b3["project"]["brief"] = {"doors_open": False}
    s3 = DS.plan_states(b3, SCANDI)
    assert all(r["state"] == "closed" for r in s3.values()) and s3["d_bed"]["by"] == "brief"
    q = AR.door_states_rule(AA.Plan(_house()), "scandinavian")[0]
    opened = {a["element"]: a for a in q["answers"] if a.get("open")}
    assert set(opened) == {"d_liv", "d_bed", "d_bath", "d_sto"} and opened["d_bed"]["default"] == "door_state:open"
    b4 = _house()
    res = AA.apply_answers(b4, {"D9:d_bath": {"option": "door_state", "params": {"door_id": "d_bath",
                                                                                  "state": "closed"}, "by": "user"},
                                "D9:d_bed": {"option": "door_state", "params": {"door_id": "d_bed", "state": "open"},
                                             "by": "architect"}})
    assert all(r["ok"] for r in res) and _by_id(b4)["d_bath"]["open_state"] == "closed"
    assert "open_state" not in _by_id(b4)["d_bed"]                                     # the default: the rule opens it
    s4 = DS.plan_states(b4, SCANDI)
    assert s4["d_bath"]["state"] == "closed" and s4["d_bed"]["state"] == "open"


def test_the_open_leaf_stands_square_by_the_wall_in_the_room_it_opens_into():
    b = _house()
    rec = DS.plan_states(b, SCANDI)["d_bed"]
    (poly,) = rec["leaf_polys"]
    # the bedroom lies at x > 7: the leaf runs 0.69 m into it, square to the wall (x changes, y barely)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    assert min(xs) >= 7.0 - 1e-6 and max(xs) == pytest.approx(7.0 + 0.02 + 0.69, abs=0.01)
    assert max(ys) - min(ys) == pytest.approx(DS.LEAF_T_M, abs=1e-3)
    assert rec["hinge"] in ("start", "end") and rec["hinge_side"] in ("left", "right") and rec["hinge_assumed"]
    assert rec["into"] == "r_bed" and rec["side"] == -1


def test_a_piece_in_the_swing_turns_the_hinge_or_keeps_the_door_closed():
    b = _house()
    # a small chest in the start jamb's sweep only: the leaf hinges at the other jamb
    b["furniture"].append({"id": "f_chest", "type": "nightstand", "level_id": "L0", "room_id": "r_bed",
                           "footprint": {"center": [7.55, 1.70], "size": [0.2, 0.1], "rotation_deg": 0.0}})
    rec = DS.plan_states(b, SCANDI)["d_bed"]
    assert rec["state"] == "open" and rec["hinge"] == "end"
    # UL127: a chest half a metre into the room stops the leaf of either jamb: it stands ajar at the widest free angle
    ajar = _house()
    ajar["furniture"].append({"id": "f_chest2", "type": "dresser", "level_id": "L0", "room_id": "r_bed",
                              "footprint": {"center": [7.55, 2.0], "size": [0.2, 0.9], "rotation_deg": 0.0}})
    rec = DS.plan_states(ajar, SCANDI)["d_bed"]
    assert rec["state"] == "ajar" and 15.0 <= rec["angle_deg"] < 90.0 and "ajar at" in rec["reason"]
    assert "f_chest2" in rec["stopped_by"] and not DS._hits(rec["leaf_polys"][0], DS.piece_polys(ajar, "L0"))
    # a wardrobe across both sweeps: closed (not even 15 degrees), with the piece named
    b["furniture"].append({"id": "f_robe", "type": "wardrobe", "level_id": "L0", "room_id": "r_bed",
                           "footprint": {"center": [7.4, 2.0], "size": [0.5, 1.2], "rotation_deg": 0.0}})
    rec = DS.plan_states(b, SCANDI)["d_bed"]
    assert rec["state"] == "closed" and "f_robe" in rec["reason"] and rec["blocked"]
    # a drawn hinge side is kept: the other jamb is never tried (the chest stops it: ajar)
    b3 = _house()
    b3["furniture"].append(dict(b["furniture"][0]))
    _by_id(b3)["d_bed"]["hinge_side"] = DS.hinge_side_of("start", -1)
    rec3 = DS.plan_states(b3, SCANDI)["d_bed"]
    assert rec3["hinge"] == "start" and rec3["state"] == "ajar"


def test_swing_leaf_geometry_and_the_parametric_pose_agree():
    wall = {"start": [0, 0], "end": [4, 0], "thickness": 0.12}
    o = {"id": "d", "type": "door", "center": [2, 0], "width": 0.9}
    fr = DS.leaf_frame(o, wall)
    for hinge in ("start", "end"):
        leaf = DS.swing_leaf(fr, 1, hinge, 90.0)
        look = dict(LK.door_look(SCANDI, {"id": "d", "type": "door"}), side=1.0,
                    leaf_state={"state": "open", "angle_deg": 90.0, "hinge": hinge})
        parts, rec = P.door_parts(look, 0.9, 2.1, 0.12)
        assert rec["pose"]["hinge"] == hinge and rec["pose"]["angle_deg"] == 90.0
        body = [v for p in parts if p["role"] == "leaf" for v in p["verts"]]
        xs, ys = [v[0] for v in body], [v[1] for v in body]
        pxs, pys = [p[0] - 2.0 for p in leaf["poly"]], [p[1] for p in leaf["poly"]]
        assert min(ys) >= 0.02 - 1e-6 and max(ys) == pytest.approx(max(pys), abs=1e-3)      # into the +y room
        assert min(xs) == pytest.approx(min(pxs), abs=0.006) and max(xs) == pytest.approx(max(pxs), abs=0.006)
        # the frame, the stops and the architrave stay where they were
        closed, _ = P.door_parts(dict(look, leaf_state=None), 0.9, 2.1, 0.12)
        fixed = sorted(tuple(v) for p in parts if p["role"] in P.FIXED_ROLES for v in p["verts"])
        assert fixed == sorted(tuple(v) for p in closed if p["role"] in P.FIXED_ROLES for v in p["verts"])
        # the lever ends at the free edge
        lever = [v for p in parts if p["role"] == "handle" for v in p["verts"]]
        assert min(v[1] for v in lever) > 0.4
    # a sliding leaf slides along its face, a pocket leaf into its pocket
    slide_look = dict(LK.door_look(SCANDI, {"id": "d", "type": "door", "operation": "sliding"}), side=1.0,
                      leaf_state={"state": "open", "slide_m": 0.9})
    parts, rec = P.door_parts(slide_look, 0.9, 2.1, 0.12)
    assert rec["pose"]["slide_m"] == 0.9
    assert min(v[0] for p in parts if p["role"] == "leaf" for v in p["verts"]) > 0.3
    assert any(p["role"] == "rail" for p in parts)
    pocket, prec = P.door_parts(dict(LK.door_look(SCANDI, {"id": "d", "type": "door", "operation": "pocket"}),
                                     side=1.0, leaf_state={"state": "open"}), 0.9, 2.1, 0.12)
    assert prec["pose"]["slide_m"] > 0.5
    # a closed pose builds the door as before
    _parts, crec = P.door_parts(dict(slide_look, leaf_state={"state": "closed"}), 0.9, 2.1, 0.12)
    assert "pose" not in crec


def test_a_view_keeps_the_open_leaf_out_of_its_doorway_and_shows_no_closed_doors_only():
    """UL126: a view that shows only closed doors to a room worth showing is a finding; an open leaf that hides the
    doorway from a view turns to its other jamb, recorded with the camera; private doors are no finding."""
    b = _house()
    DS.apply_states(b, SCANDI)
    doors = _by_id(b)
    ls = doors["d_bed"]["leaf_state"]
    wall = next(w for w in b["walls"] if w["id"] == "w7")
    fr = DS.leaf_frame(doors["d_bed"], wall)
    # a camera in the bedroom on the hinge's side, a metre into the room: the leaf stands between it and the doorway
    lat = -1.0 if ls["hinge"] == "start" else 1.0
    cx, cy = fr["c"][0] + fr["u"][0] * lat - fr["n"][0] * 1.0, fr["c"][1] + fr["u"][1] * lat - fr["n"][1] * 1.0
    cam = {"name": "cam_r_bed_1", "kind": "interior", "room_id": "r_bed", "level_id": "L0", "position": [cx, cy, 1.25],
           "target": [fr["c"][0], fr["c"][1], 1.25], "visible_openings": ["d_bed"]}
    assert DS.leaf_hides(cam["position"], ls["leaf_polys"][0], fr)
    got = DS.revise_for_cameras(b, SCANDI, [cam], "L0")
    new = doors["d_bed"]["leaf_state"]
    assert new["hinge"] != ls["hinge"] and new["hinge"] == DS.camera_hinge(fr, new["side"], cam["position"])
    assert not DS.leaf_hides(cam["position"], new["leaf_polys"][0], fr)
    assert got and got[0]["camera"] == "cam_r_bed_1" and new["by"] == "camera"
    # the house as it was built before (no leaf states): a hall view of closed doors to the living room is a finding
    old = _house()
    hall = {"name": "cam_r_hall_1", "kind": "interior", "room_id": "r_hall", "level_id": "L0",
            "position": [6.5, 3.0, 1.25], "target": [4.0, 3.0, 1.25], "visible_openings": ["d_liv"]}
    assert [p["kind"] for p in DS.view_problems(old, [hall])] == ["view_closed_doors"]
    assert DS.view_problems(b, [hall]) == []
    # a bathroom seen from the hall is a private door: no finding even closed
    bath = dict(hall, visible_openings=["d_bath"], target=[8.0, 5.5, 1.25])
    assert DS.view_problems(old, [bath]) == []
    assert DS.worth_showing(b, {"room_type": "hall"}, {"room_type": "living"}) == "the living beyond"
    # an en-suite seen from its bedroom is worth showing
    b["rooms"].append({"id": "r_ens", "level_id": "L0", "room_type": "bathroom",
                       "polygon": [[11, 0], [13, 0], [13, 4], [11, 4]]})
    b["walls"].append({"id": "w11", "level_id": "L0", "start": [11, 0], "end": [11, 4], "thickness": 0.1})
    b["openings"].append(_door("d_ens", "w11", (11, 3), 0.8, "r_ens"))
    DS.apply_states(b, SCANDI)
    rooms = {r["id"]: r for r in b["rooms"]}
    assert DS.worth_showing(b, rooms["r_bed"], rooms["r_ens"]) == "the en-suite beyond"
    assert DS.worth_showing(b, rooms["r_hall"], rooms["r_bath"]) is None


def test_the_camera_model_sees_an_open_doorway_and_the_open_leaf():
    b = _house()
    DS.apply_states(b, SCANDI)
    bed = next(r for r in b["rooms"] if r["id"] == "r_bed")
    model = CS.RoomModel(bed, b)
    kinds = {e["id"]: e["kind"] for e in model.elements}
    assert kinds["d_bed"] == "doorway" and kinds["d_bed#leaf"] == "door"
    assert any(box[0] == model.elements.index(next(e for e in model.elements if e["id"] == "d_bed#leaf"))
               + CS.FIRST_ELEMENT for box in model.boxes)
    segs = {s[0] for s in CAM.door_segments(bed, b)}
    assert {"d_bed", "d_bed#leaf"} <= segs
    # a closed door is its leaf as before
    closed = _house()
    model2 = CS.RoomModel(next(r for r in closed["rooms"] if r["id"] == "r_bed"), closed)
    assert {e["id"]: e["kind"] for e in model2.elements}["d_bed"] == "door"


# -------------------------------------------------------------------------------------------------- D5: door sizes

def test_door_sizes_by_role_and_family():
    b = _house()
    changes, assumed = DS.apply_sizes(b, SCANDI)
    doors = _by_id(b)
    ent = doors["d_ent"]
    assert ent["width"] == 0.9 and ent["height"] == DS.ENTRANCE_HEIGHT_M and ent["drawn_width"] == 0.8
    assert ent["adjusted_by_ai"]["rule"] == "D5 door sizes" and ent["door_size"]["role"] == "entrance"
    assert doors["d_bath"]["width"] == 0.75 and doors["d_bath"]["drawn_width"] == 0.77     # the nearest product
    assert doors["d_bed"]["width"] == 0.8 and "drawn_width" not in doors["d_bed"]          # a product: kept
    assert doors["d_liv"]["height"] == DS.STANDARD_HEIGHT_M                                # Scandinavian: 2.10 m
    assert {a["kind"] for a in assumed} == {"door_size"} and len(changes) == len(assumed)
    # the modern families: a pivot entrance, full-height doors between day rooms
    m = _house()
    DS.apply_sizes(m, MODERN)
    md = _by_id(m)
    assert md["d_ent"]["width"] == 1.0 and md["d_ent"]["height"] == DS.PIVOT_HEIGHT_M and md["d_ent"]["door_size"]["pivot"]
    assert md["d_liv"]["height"] == pytest.approx(2.7) and md["d_bed"]["height"] == DS.STANDARD_HEIGHT_M
    assert LK.door_look(MODERN, dict(md["d_ent"], door_type="entrance", door_style="entrance"))["pivot"]
    # a height the documents give stays; a wall with no room keeps the width
    d = _house()
    _by_id(d)["d_ent"]["assumed"] = []
    d["openings"].append(_door("w_win", "ws", (6.75, 0.0), 0.6, type="window"))
    DS.apply_sizes(d, MODERN)
    dd = _by_id(d)
    assert dd["d_ent"]["height"] == 2.1 and dd["d_ent"]["width"] == pytest.approx(0.8)
    assert DS.plan_sizes(_house(), NO_FAMILY) == []
    # the parametric pivot door: one leaf, a long bar pull, no hinges
    parts, rec = P.door_parts(dict(LK.door_look(MODERN, {"id": "e", "type": "door", "door_style": "entrance",
                                                         "door_size": {"pivot": True}}), side=1.0), 1.0, 2.4, 0.3)
    assert rec["pivot"] and not [p for p in parts if p["role"] == "hinge"]
    assert max(max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"]) for p in parts
               if p["role"] == "handle") == pytest.approx(P.PIVOT_PULL_M)


def test_all_doors_one_size_and_every_door_closed_are_findings():
    b = _house()
    for o in b["openings"]:
        o["width"] = 0.8
    DS.apply_states(b, SCANDI)
    for o in b["openings"]:
        o["leaf_state"]["state"] = "closed"
    kinds = {p["kind"] for p in DS.state_problems(b)}
    assert {"all_closed", "one_size"} <= kinds
    DS.apply_sizes(b, SCANDI)
    DS.apply_states(b, SCANDI)
    kinds = {p["kind"] for p in DS.state_problems(b)}
    assert "all_closed" not in kinds and "one_size" not in kinds
    # an open leaf in a piece (a piece the build placed after the plan)
    leaf = _by_id(b)["d_bed"]["leaf_state"]["leaf_polys"][0]
    cx, cy = sum(p[0] for p in leaf) / 4, sum(p[1] for p in leaf) / 4
    b["furniture"].append({"id": "f_late", "type": "dresser", "level_id": "L0", "room_id": "r_bed",
                           "footprint": {"center": [cx, cy], "size": [0.4, 0.4], "rotation_deg": 0.0}})
    assert any(p["kind"] == "leaf_in_piece" and p["target"] == "d_bed" for p in DS.state_problems(b))


# --------------------------------------------------------------------------------------------- D2 / D3: the looks

def test_family_finishes_divided_lites_and_the_product_details():
    look = LK.door_look(MODERN, {"id": "d", "type": "door", "joins": ["hall", "bedroom"]})
    assert look["colour"] == "black" and look["handle"] == "black" and look["lock_rose"]
    assert look["frame_look"]["colour"] == "black"                                     # black frames (D2)
    assert LK.door_frame_look({"family": "industrial"})["material"] == "metal_black"
    assert LK.door_frame_look(SCANDI)["material"] == "painted_wood_white"
    contemporary = {"family": "contemporary", "door": {"material": "wood_oak_light"}}
    assert LK.door_look(contemporary, {"id": "d", "type": "door"})["leaf_detail"] == {"kind": "fine_vertical"}
    parts, rec = P.door_parts(dict(LK.door_look(contemporary, {"id": "d", "type": "door"}), side=1.0), 0.9, 2.1, 0.12)
    assert rec["leaf_detail"] == "fine_vertical" and rec["lock_rose"]
    boards = sorted({round(min(v[0] for v in p["verts"]), 4) for p in parts if p["role"] == "leaf"
                     and min(v[1] for v in p["verts"]) > 0})
    assert len(boards) >= 10                                                            # fine grooves every 6 cm
    assert len([p for p in parts if p["role"] == "lock_rose"]) == 2
    # D3: a wide door between day rooms is a glazed divided-lite door in the family's accent colour
    wide = {"id": "w", "type": "door", "width": 1.6, "operation": "sliding", "joins": ["living", "dining"]}
    lite = LK.divided_lite(wide, SCANDI, "sliding")
    assert lite["door_style"] == "glazed_sliding" and lite["colour"] == "sage" and lite["lites"] == [2, 4]
    dl = LK.door_look(SCANDI, wide)
    assert dl["door_style"] == "glazed_sliding" and dl["glazed"] and dl["colour"] == "sage"
    parts, rec = P.door_parts(dict(dl, side=1.0), 1.6, 2.1, 0.12)
    assert rec["lites"] == [2, 4] and len([p for p in parts if p["role"] == "muntin"]) == rec["leaves"] * 4
    assert LK.divided_lite(dict(wide, joins=["living", "bedroom"]), SCANDI, "sliding") is None
    assert LK.divided_lite(dict(wide, width=1.0), SCANDI, "sliding") is None
    rec_in = {"opening": dict(wide, door_style="sliding"), "joins": ["living", "dining"]}
    assert OM.inside_role(rec_in, SCANDI)[0] is None                                    # the parametric door


def test_frameless_only_by_decision_or_style_key():
    o = {"id": "d", "type": "door"}
    assert LK.frameless_reason(MODERN, o, "flush") is None                              # framed by default
    assert LK.frameless_reason({"family": "minimal", "door": {"frameless": True}}, o, "flush")
    assert LK.frameless_reason({"family": "scandinavian", "door": {"frameless": True}}, o, "flush") is None
    ai = dict(o, frame_decision={"frameless": True, "by": "ai", "key": "D7:d", "reason": "x"})
    assert "concealed" in LK.frameless_reason(MODERN, ai, "flush")
    look = dict(LK.door_look(MODERN, ai), side=1.0, architrave_faces=(1.0, -1.0))
    parts, rec = P.door_parts(look, 0.9, 2.1, 0.12)
    assert not [p for p in parts if p["role"] == "architrave"] and rec["frame"]["frameless"]
    assert DS.frame_problems({"objects": [{"kind": "door", "element_id": "d", "frame": rec["frame"]}]}) == []
    # the architect's D7: framed by default in a minimal or modern house, frameless as an option
    b = _house()
    qs = AR.door_frames_rule(AA.Plan(b), "modern")[0]
    opened = [a for a in qs["answers"] if a.get("open")]
    assert opened and all(a["default"] == "door_frames:framed" for a in opened)
    assert "d_ent" not in {a["element"] for a in opened}                               # the facade door: not asked
    assert AR.door_frames_rule(AA.Plan(b), "scandinavian")[0]["answers"] == []
    res = AA.apply_answers(b, {"D7:d_bed": {"option": "door_frames", "params": {"door_id": "d_bed",
                                                                                 "frame": "frameless"}, "by": "ai"}})
    assert res[0]["ok"] and _by_id(b)["d_bed"]["frame_decision"]["frameless"]


# ----------------------------------------------------------------------------------------- UL122: frames for all

def _box_mesh(boxes):
    verts, faces = [], []
    for c, s in boxes:
        v, f = geom2d.box(c, s)
        faces += [[i + len(verts) for i in face] for face in f]
        verts += v
    return verts, faces


def test_a_library_model_is_measured_framed_and_its_leaf_turned():
    import numpy as np

    # a bare leaf: its leaf face reaches its box at both jambs and the head
    verts, faces = _box_mesh([((0.0, 0.0, 1.0), (0.8, 0.04, 2.0))])
    bare = OB.leaf_panel(np.asarray(verts), faces)
    assert bare["framed"] is False and max(bare["margins"]) < OB.BARE_LEAF_MARGIN_M
    # a framed model: jambs and a head round a recessed leaf
    verts, faces = _box_mesh([((0.0, 0.0, 0.99), (0.7, 0.04, 1.98)), ((-0.375, 0.0, 1.025), (0.05, 0.10, 2.05)),
                              ((0.375, 0.0, 1.025), (0.05, 0.10, 2.05)), ((0.0, 0.0, 2.025), (0.70, 0.10, 0.05))])
    framed = OB.leaf_panel(np.asarray(verts), faces)
    assert framed["framed"] is True and framed["margins"][0] == pytest.approx(0.05, abs=1e-3)
    mask = OB.leaf_mask(np.asarray(verts), faces, framed)
    assert mask[:6].all() and not mask[6:].any()                                      # the leaf's six faces only
    loc, faces2 = OB.turn_leaf(np.asarray(verts), faces, mask, (framed["x0"], framed["half_t"]), 90.0)
    assert np.allclose(loc[8:], np.asarray(verts)[8:])                                # the frame stays
    assert loc[:8, 1].max() == pytest.approx(0.02 + 0.7, abs=1e-6)                    # the leaf turned square
    # a frame round a bare leaf, the architrave alone round a framed model
    full = P.door_frame_parts(0.9, 2.1, 0.12, 0.02, 1.0, (1.0, -1.0))
    assert {p["role"] for p in full} == {"frame", "stop", "architrave"}
    only = P.door_frame_parts(0.9, 2.1, 0.12, None, 1.0, (1.0,), frame_w=0.04, lining=False)
    assert {p["role"] for p in only} == {"architrave"} and len(only) == 3
    # the added levers turn with the leaf
    pieces = SH.door_handle_parts(0.9, 2.1)
    rec = [{"pose": {"state": "open", "angle_deg": 90.0, "hinge": "start"}}]
    posed = OB.posed_handle_parts(pieces, rec, 1.0, 0.79, 0.02)
    assert min(v[1] for vs, _f in posed for v in vs) > 0.3


def test_every_door_and_passage_is_framed_or_says_why_not():
    man = {"objects": [
        {"kind": "door", "element_id": "a", "frame": {"lining": True, "architrave": [1], "indoor_faces": [1]}},
        {"kind": "door", "element_id": "b", "frame": {"lining": False, "architrave": [], "indoor_faces": [1]}},
        {"kind": "door", "element_id": "c"},
        {"kind": "door", "element_id": "d", "frame": {"lining": True, "architrave": [], "indoor_faces": [1, -1]}},
        {"kind": "door", "element_id": "e", "frame": {"lining": False, "frameless": "a concealed door"}}]}
    got = {(p["target"], p["kind"]) for p in DS.frame_problems(man)}
    assert got == {("b", "no_frame"), ("c", "no_frame"), ("d", "no_architrave")}
    lining = SH.passage_lining_parts(1.2, 2.4, 0.2, head=True)
    assert len(lining) == 3 and all(abs(v[1]) < 0.1 for vs, _f in lining for v in vs)
    assert len(SH.passage_lining_parts(1.2, 2.4, 0.2, head=False)) == 2
    # a sliding door's opening is lined, its architrave on the face its leaf does not cover
    look = dict(LK.door_look(SCANDI, {"id": "s", "type": "door", "operation": "sliding"}), side=1.0,
                architrave_faces=(1.0, -1.0))
    parts, rec = P.door_parts(look, 0.9, 2.1, 0.12)
    arch = [p for p in parts if p["role"] == "architrave"]
    assert arch and all(max(v[1] for v in p["verts"]) < 0 for p in arch)
    assert rec["frame"]["lining"] and rec["frame"]["architrave_why"]
    # the model review's M20 names a library door built without its frame
    lib = {"objects": [{"kind": "door", "element_id": "x", "library_model": {"asset_id": "m"},
                        "frame": {"lining": False, "architrave": [], "indoor_faces": [1]}}]}
    assert [p["kind"] for p in OM.door_product_problems(lib)] == ["library_door_without_frame"]


# ------------------------------------------------------------------------------- R31 / R37: see-through wardrobes

def _dressing(label="Dressing", rtype="storage", w=2.4, d=2.45):
    room = {"id": "r_dr", "level_id": "L0", "room_type": rtype, "label": label,
            "polygon": [[0, 0], [w, 0], [w, d], [0, d]]}
    robes = [{"id": "f_a", "type": "wardrobe", "level_id": "L0", "room_id": "r_dr", "height": 2.3, "front_deg": 0.0,
              "footprint": {"center": [0.3, d / 2], "size": [2.27, 0.6], "rotation_deg": 90.0}},
             {"id": "f_b", "type": "wardrobe", "level_id": "L0", "room_id": "r_dr", "height": 2.3, "front_deg": 180.0,
              "footprint": {"center": [w - 0.3, d / 2], "size": [2.27, 0.6], "rotation_deg": 90.0},
              "asset": {"asset_id": "abo_x", "method": "library", "library": "abo"}}]
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.6}], "rooms": [room], "walls": [],
            "openings": [], "furniture": robes, "decor": []}


def test_a_walk_in_is_see_through_on_both_sides():
    b = _dressing()
    assert WF.walk_in(b, b["rooms"][0]) == "a dressing room"
    chosen, assumed = WF.apply(b, SCANDI)
    assert set(chosen) == {"f_a", "f_b"} and all(v["kind"] == "slats" and v["walk_in"] for v in chosen.values())
    robe = b["furniture"][1]
    assert robe["asset"]["method"] == "module" and robe["see_through"]["replaced"]["asset_id"] == "abo_x"
    # 31 Oct 2026 (user: "it needs to be wall to wall"): the runs' 9 cm gaps to the end walls close (logged)
    assert {a["kind"] for a in assumed} == {"see_through_front", "built_in_wardrobe"}
    assert all(f["adjusted_by_ai"]["rule"].startswith("built-in wardrobe") and f["drawn_footprint"]["size"][0] == 2.27
               and f["footprint"]["size"][0] > 2.4 for f in b["furniture"])
    # facing runs make a walk-in whatever the label; the family picks the front; the architect's answer wins
    anon = _dressing(label="Oda", rtype="other")
    assert "face each other" in WF.walk_in(anon, anon["rooms"][0])
    assert {v["kind"] for v in WF.plan(anon, {"family": "minimal"}).values()} == {"smoked_glass"}
    assert {v["kind"] for v in WF.plan(anon, {"family": "rustic"}).values()} == {"open"}
    anon["rooms"][0]["wardrobe_fronts"] = {"kind": "closed", "by": "user"}
    assert WF.plan(anon, SCANDI) == {}
    assert WF.plan(_dressing(), NO_FAMILY) == {}
    # the architect's D8: the family's front as the safe default
    q = AR.walk_in_rule(AA.Plan(_dressing()), "japandi")[0]
    assert q["answers"][0]["default"] == "wardrobe_fronts:slats" and q["answers"][0]["open"]
    b2 = _dressing()
    res = AA.apply_answers(b2, {"D8:r_dr": {"option": "wardrobe_fronts", "params": {"room_id": "r_dr",
                                                                                     "kind": "open"}, "by": "ai"}})
    assert res[0]["ok"] and WF.walk_in_front(b2, b2["rooms"][0], SCANDI)[0] == "open"


def test_the_master_bedrooms_run_and_not_every_wardrobe():
    b = _dressing()
    b["rooms"] = [{"id": "r_m", "level_id": "L0", "room_type": "bedroom", "label": "Master bedroom",
                   "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]},
                  {"id": "r_k", "level_id": "L0", "room_type": "bedroom", "label": "Kids",
                   "polygon": [[5, 0], [9, 0], [9, 4], [5, 4]]}]
    # 31 Oct 2026 (user: "it needs to be wall to wall or from wall to middle"): both runs start at a wall
    b["furniture"] = [{"id": "f_m", "type": "wardrobe", "level_id": "L0", "room_id": "r_m", "front_deg": 90.0,
                       "footprint": {"center": [1.0, 0.3], "size": [2.0, 0.6], "rotation_deg": 0.0}},
                      {"id": "f_k", "type": "wardrobe", "level_id": "L0", "room_id": "r_k", "front_deg": 90.0,
                       "footprint": {"center": [5.75, 0.3], "size": [1.5, 0.6], "rotation_deg": 0.0}}]
    # 30 Oct 2026 (UL182, UL207 "This is not mandatory it is optional"): the master the family's (slats), another
    # bedroom only when its room scheme asks for a see-through front, then a front of its own
    got = WF.plan(b, SCANDI)
    assert set(got) == {"f_m"} and got["f_m"]["kind"] == "slats"
    b["rooms"][1]["scheme"] = {"kind": "bedroom", "bundle": "panel"}
    got = WF.plan(b, SCANDI)
    assert set(got) == {"f_m", "f_k"} and got["f_k"]["kind"] != "slats"
    assert WF.plan(b, {"family": "classic"}) == {}                                     # a period house: closed


def test_see_through_parts_hold_garments_folded_stacks_drawers_and_a_light():
    for kind in ("slats", "smoked_glass", "open"):
        piece = {"id": "f_a", "type": "wardrobe", "height": 2.3, "see_through": {"kind": kind},
                 "footprint": {"center": [0, 0], "size": [2.27, 0.6], "rotation_deg": 0.0}}
        plan = MOD.module_plan(piece)
        assert plan["see_through"]["kind"] == kind
        parts = MOD.module_parts(plan)
        roles = {p["role"] for p in parts}
        assert {"garment", "hanger", "rail", "folded", "led", "body", "shelf"} <= roles
        assert ("slat" in roles) == (kind == "slats") and ("glass" in roles) == (kind == "smoked_glass")
        # the open run's shoe racks; shoes on the lowest shelf or under the hems of every run since UL135
        assert ("shoe_rack" in roles) == (kind == "open") and ("panel_frame" in roles) == (kind != "open")
        assert "shoe" in roles and {"sleeve", "collar"} <= roles
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x0 >= -2.27 / 2 - 0.008 and x1 <= 2.27 / 2 + 0.008 and y0 >= -0.3 - 0.008 and y1 <= 0.3 + 0.008
        assert z0 >= -1e-9 and z1 <= 2.3 + 1e-6
        keys = {p["key"] for p in parts}
        plain = {k.split(":", 1)[1] if k.startswith("lit:") else ("fabric" if k.startswith("cloth:") else k)
                 for k in keys}
        assert plain <= set(P.MATERIAL_KEYS)
        colours = {k for k in keys if k.startswith("cloth:")}
        assert len(colours) >= 4                                                       # varied garment colours
        # 30 Oct 2026 (UL135): cloth:<look>:<colour>, the look one of the woven fabrics (wardrobe_contents)
        from wenart.blender import wardrobe_contents as WC
        assert all(WC.parse_cloth_key(k)[1] in __import__("wenart.style.colours", fromlist=["COLOURS"]).COLOURS
                   and WC.parse_cloth_key(k)[0] in WC.LOOKS for k in colours)
    # one wardrobe always gets the same garments; the garments are part lists (one mesh with the wardrobe): each a
    # hanger of several parts, a body, sleeves and a collar where its kind has them (UL135)
    a = MOD.garment_parts(-0.5, 0.5, 0.0, 2.0, 7, 1.0)
    assert a == MOD.garment_parts(-0.5, 0.5, 0.0, 2.0, 7, 1.0) and len(a) >= 60
    assert sum(1 for p in a if p["role"] == "garment") >= 10


def test_the_walk_in_gets_a_bench_and_a_mirror_where_the_walkway_allows():
    b = _dressing(w=3.0, d=4.0)
    b["furniture"] = [b["furniture"][0]]                                              # one run on the west wall
    b["furniture"][0]["footprint"]["center"] = [0.3, 2.0]
    extra = WF.walk_in_extras(b, b["rooms"][0])
    bench, mirror = extra["bench"], extra["mirror"]
    assert bench is not None and bench["type"] == "bench" and bench["source"] == "added_by_ai"
    assert bench["added_by_ai"]["rule"].startswith("walk-in") and bench["completes_room"]
    poly = [tuple(p) for p in __import__("wenart.geometry", fromlist=["x"]).rotated_rectangle(
        bench["footprint"]["center"], bench["footprint"]["size"], bench["footprint"]["rotation_deg"])]
    assert all(0.0 <= x <= 3.0 and 0.0 <= y <= 4.0 for x, y in poly)
    assert mirror is not None and mirror["height"] <= 2.6 - 0.05 and mirror["width"] == WF.MIRROR_M[0]
    parts = WF.mirror_parts(mirror["width"], mirror["height"])
    assert {p["key"] for p in parts} == {"dark", "mirror"}
    # the 2.4 m dressing room with a run on each side: the 1.2 m aisle leaves no walkway beside a bench
    tight = _dressing()
    assert WF.walk_in_extras(tight, tight["rooms"][0])["bench"] is None


def test_a_walk_in_with_closed_fronts_is_a_design_finding_with_its_fix():
    b = _dressing()
    probs = DS.dressing_problems(b, SCANDI)
    assert [p["kind"] for p in probs] == ["dressing_closed_fronts"] and probs[0]["fix_choice"] == "wardrobe_fronts:slats"
    WF.apply(b, SCANDI)
    assert DS.dressing_problems(b, SCANDI) == []
    # Argus U33 carries the architect's answer as its fix; the model review's M29 the same finding
    closed = _dressing()
    u33 = L.doors_as_designed(closed, {"objects": [], "style_profile": {"family": "scandinavian"}, "cameras": []})
    assert u33 and u33[0]["check"] == "U33" and "D8:r_dr wardrobe_fronts:slats" in u33[0]["fix"]
    m29, _n = MR.doors_as_designed(closed, {"objects": [], "style_profile": {"family": "scandinavian"}})
    assert m29 and m29[0]["check"] == "M29" and m29[0]["metrics"]["fix_choice"] == "wardrobe_fronts:slats"
    assert K.kind_of(m29[0]) == "reference_missed" and "reference_missed" in K.KINDS
    assert "M29" in MR.CHECKS and L.CHECK_LESSONS["U33"] == ("UL116", "UL117", "UL120", "UL122", "UL125", "UL126", "UL127")
    assert L.audit(closed, {"objects": [], "cameras": []})["checked"]["U33"] == 1


def test_the_lessons_are_built_with_their_checks():
    rows = {r["id"]: r for r in json.loads(LESSONS.read_text(encoding="utf-8"))["lessons"]}
    for lid in ("UL116", "UL117", "UL120", "UL122", "UL125", "UL126", "UL127"):
        assert rows[lid]["status"] == "built" and rows[lid]["checks"] == ["build"], lid
        assert "M29" in rows[lid]["lesson"] and "U33" in rows[lid]["lesson"], lid


# ------------------------------------------------------------------------------------ the real06 run as built

def test_real06_doors_and_wardrobes_as_built():
    path = REAL06 / "building_built.json"
    if not path.is_file():
        pytest.skip(f"{path} not here")
    b = json.loads(path.read_text(encoding="utf-8"))
    style = json.loads((REAL06 / "style.json").read_text(encoding="utf-8"))
    for o in b["openings"]:
        o.pop("leaf_state", None)
    from wenart.blender import build as BLD
    got = BLD.doors_as_designed(b, style, [])
    man = json.loads((REAL06 / "scene_manifest.json").read_text(encoding="utf-8"))
    DS.revise_for_cameras(b, style, man.get("cameras") or [])
    rows = []
    for o in b["openings"]:
        if o["type"] != "door":
            continue
        ls = o.get("leaf_state") or {}
        rows.append((o["id"], ls.get("state"), round(float(o["width"]), 3), round(float(o.get("height") or 2.1), 3),
                     ls.get("role"), ls.get("reason")))
    print("\nreal06 doors (id, state, width, height, role, why):")
    for r in rows:
        print("  ", r)
    print("see-through wardrobes:", {k: (v["kind"], v["room_id"]) for k, v in got["fronts"].items()})
    states = {r[0]: r[1] for r in rows}
    assert states["d_L0_004"] == "closed"                                              # the entrance
    assert states["win_L1_003"] == "open"                                              # the bedroom to the dressing room
    assert sum(1 for s in states.values() if s == "open") >= 3
    assert {k for k, v in got["fronts"].items() if v["room_id"] == "r_L1_soyunma_odasi"} == {"f_L1_011", "f_L1_012"}
    sizes = {(r[2], r[3]) for r in rows}
    assert len(sizes) >= 3                                                              # not one size
    probs = {p["kind"] for p in DS.state_problems(b, man)}
    assert not probs & {"all_closed", "one_size", "dressing_closed_fronts", "view_closed_doors"}, probs
    # the run as it was built: every inside door closed, no frames: M29 / U33 name it
    old = json.loads(path.read_text(encoding="utf-8"))
    kinds = {f["evidence"]["problem"] for f in L.doors_as_designed(old, man)}
    print("U33 on the run as it was built:", sorted(kinds))
    assert {"all_closed", "dressing_closed_fronts", "no_frame"} <= kinds
