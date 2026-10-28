"""28 Oct 2026, the user on real04 run 20261028-005318-full: "still flying pillows all around" (the two sofas of
r_L1_oyun_aktivite_ve_dinlenme_odasi), "More flying pillows" (the dressed bed f_L0_007), "I did not like this bed"
(f_L0_021: a cream throw over the model's own bedding), "Light is flying in the air needs to be connected to ceiling"
(the salon's dining pendant dec_L-1_008) and "More decor pieces needed, plates on tables for example".

General rules tested on hand-made meshes (pure ray casts, the code the scene builder runs on Blender's BVH): a leaning
cushion touches its back in its upper part (``rest.measure_back``, S5, the model review's M13); on a sofa the back rays
skip the seat's own dome; on a dressed bed the cushion stands on the pillows against the headboard (or leans back on
the pillows) and is measured on the bedding as built; no throw on a bed model with its own made bedding, and a cloth
the host pokes through or whose drape tore is not built; every hung light reaches the ceiling (``furniture.hang_plan``,
S5 ``hang_gap``, M13); dining tables are set at every chair and tops carry a small group (``tabletop.dress_tops``)."""
from __future__ import annotations

import pytest

from wenart.audit import kinds as K
from wenart.blender import furniture as F
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import scene_checks as SC
from wenart.blender import textiles as T
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import tabletop as TT

from test_decor_m8 import RID, room_building
from test_decor_rest import SOFA_FP, boxes_mesh, merge, piece, prism_mesh

TOL = R.REST_TOLERANCES


# --------------------------------------------------------------------------------------------------------- cushions
def domed_sofa():
    """A sofa like real04's abo_B075X4F5CS: its seat cushion domed (0.535 m at its front, 0.47 m at the back joint),
    a back reclined from y = 0.20 at the seat to 0.32 at 0.90 m, 0.2 m arms up to 0.65 m."""
    c, r = SOFA_FP["center"], SOFA_FP["rotation_deg"]
    base = boxes_mesh([(-0.8, -0.475, 0.0, 0.8, 0.475, 0.30), (-1.0, -0.475, 0.0, -0.8, 0.475, 0.65),
                       (0.8, -0.475, 0.0, 1.0, 0.475, 0.65)], c, r)
    seat = prism_mesh([(-0.475, 0.30), (0.20, 0.30), (0.20, 0.47), (-0.10, 0.51), (-0.35, 0.535), (-0.475, 0.50)],
                      -0.8, 0.8, c, r)
    back = prism_mesh([(0.20, 0.30), (0.475, 0.30), (0.475, 0.90), (0.32, 0.90)], -0.8, 0.8, c, r)
    return merge(base, seat, back)


def _measured(caster, verts, faces, foot, soft=True, wall=None):
    m = R.measure_rest(verts, faces, caster, foot, soft)
    m.update(R.measure_back(verts, faces, caster, foot, wall=wall))
    return m


def test_a_cushion_starts_at_the_styled_lean_then_falls_back_further_then_smaller():
    """The decor stage's host frame carries Milestone 12's 12 degrees: it was the only lean tried, so every planned
    cushion stood almost upright; it is the least one now."""
    assert R.lean_steps("back", 12.0) == [R.LEAN_DEG, *R.LEAN_STEEPER_DEG, *R.LEAN_FALLBACK_DEG]
    assert R.lean_steps("headboard", 12.0)[0] == R.HEADBOARD_LEAN_DEG and R.lean_steps("back", 0.0)[-1] == 12.0
    assert R.lean_steps("back", 34.0)[:2] == [34.0, 38.0] and 20.0 in R.lean_steps("back", 34.0)


def test_sofa_cushions_lean_on_the_back_never_on_the_domed_seat(monkeypatch):
    """real04 run 005318: both sofas' cushions stood 4-9 cm behind the seat's front edge (rest footprint local y -0.40
    of +-0.45), some 0.3 m in front of the backrest, and S5 passed them (one touching point under them)."""
    v, f = domed_sofa()
    caster = R.MeshCaster(v, f)
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    planned = R.to_world(SOFA_FP["center"], 30.0, -0.45, 0.2)
    # the 27 Oct placement: the lowest back ray 1.3 cm over the seat took the dome for the back
    with monkeypatch.context() as mp:
        mp.setattr(R, "SEAT_PROBE_MIN_Z_M", 0.0)
        mp.setattr(R, "BACK_MAX_NZ", 1.01)
        mp.setattr(R, "BACK_MIN_RISE_M", -1.0)
        old = R.place_leaning(caster, SOFA_FP, planned, (0.45, 0.15, 0.45), 12.0)
    old_y = R.to_local(SOFA_FP["center"], 30.0, *old["center"])[1]
    assert old_y < -0.2                                                        # at the seat's front edge
    old = dict(old, z=old["z"] - R.SOFT_SINK_M)
    world = R.pose_vertices(cushion["verts"], old)
    foot = {"center": old["center"], "size": [0.45, 0.15], "rotation_deg": 30.0}
    m = _measured(caster, world, cushion["faces"], foot)
    ok, why = R.rest_ok(m)
    assert not ok and (m["back_gap_m"] is None or m["back_gap_m"] > 0.15), m      # its back 0.6 m from the back
    assert any("does not lean on its back" in w or "stands free" in w for w in why), why
    # now: the back rays skip the seat's own surfaces and the cushion rests on the seat against the back
    item = {"id": "c", "type": "cushion", "center": list(planned), "rotation_deg": 30.0,
            "host_frame": {"support": "back", "lean_deg": 12.0}}
    plan = R.plan_decor(item, piece("sofa", SOFA_FP), caster, cushion["verts"], cushion["faces"], "back",
                        lean_deg=12.0)
    assert "not_rested" not in plan, plan
    y = R.to_local(SOFA_FP["center"], 30.0, *plan["pose"]["center"])[1]
    assert y > 0.0 and plan["pose"]["lean_deg"] >= R.LEAN_DEG                  # in the back half, leaning
    assert plan["rest"]["back_gap_m"] <= TOL["decor_back_gap_m"] and plan["rest"]["gap_m"] <= TOL["decor_gap_m"]
    assert plan["rest"]["penetration_m"] <= TOL["decor_pen_soft_m"]


def dressed_bed(headboard: float | None = 0.85):
    """A 1.6 x 2.0 m bed (mattress 0.42 m, a headboard up to ``headboard`` or none) dressed with our duvet and two
    lying pillows (``textiles.duvet_and_pillows``); ``(bed, lean, full)`` casters as the build makes them."""
    fp = {"center": [2.0, 3.0], "size": [1.6, 2.0], "rotation_deg": 90.0}
    boxes = [(-0.8, -1.0, 0.0, 0.8, 1.0, 0.42)] if headboard is None else \
        [(-0.8, -1.0, 0.0, 0.8, 0.94, 0.42), (-0.8, 0.94, 0.0, 0.8, 1.0, headboard)]
    v, f = boxes_mesh(boxes, fp["center"], fp["rotation_deg"])
    bed = R.MeshCaster(v, f)
    got = T.duvet_and_pillows(bed, fp, 0.0)
    pv, pf = T.lean_parts(got["parts"])
    lean = R.MultiCaster([bed, R.MeshCaster(pv, pf)])
    full = R.MeshCaster(*merge((v, f), *[(p["verts"], p["faces"]) for p in got["parts"]]))
    return fp, got, bed, lean, full


def test_bed_cushions_stand_on_the_pillows_against_the_headboard_on_the_bedding_as_built():
    """real04 run 005318, f_L0_007 (views cam_r_L0_e_yatak_odasi_1 and _3): the cushions were placed and measured on
    the bed and its pillows only; the scene check on the bedding as built found them 4.9 cm in the duvet (S5 critical)
    and their upper part stood free in front of the lying pillows."""
    fp, got, bed, lean, full = dressed_bed(0.85)
    cushion = T.cushion_mesh(0.5, 0.15, 0.5)
    item = {"id": "c", "type": "cushion", "rotation_deg": 90.0, "center": list(R.to_world(fp["center"], 90.0, -0.3,
                                                                                            0.775))}
    # the 27 Oct pose (the lean caster for everything, the frame's 12 degrees) measured on the bedding as built
    old = R.place_leaning(lean, fp, item["center"], (0.5, 0.15, 0.5), 12.0, bed=True)
    old = dict(old, z=old["z"] - R.SOFT_SINK_M)
    world = R.pose_vertices(cushion["verts"], old)
    foot = {"center": old["center"], "size": [0.5, 0.15], "rotation_deg": 90.0}
    m = _measured(full, world, cushion["faces"], foot, wall=fp)
    assert not R.rest_ok(m)[0] and m["back_gap_m"] > 0.1, m
    plan = R.plan_decor(item, piece("bed_double", fp), full, cushion["verts"], cushion["faces"], "headboard",
                        lean_deg=12.0, back_caster=[bed, lean])
    assert "not_rested" not in plan, plan
    rest = plan["rest"]
    assert rest["back_gap_m"] <= TOL["decor_back_gap_m"] and rest["gap_m"] <= TOL["decor_gap_m"]
    assert rest["penetration_m"] <= TOL["decor_pen_soft_m"]
    assert plan["pose"]["z"] > 0.42 + 0.05                                      # on the pillows, not on the mattress
    assert R.to_local(fp["center"], 90.0, *plan["pose"]["center"])[1] > 0.5   # at the head, before the headboard


def test_bed_cushions_lean_back_on_the_pillows_of_a_bed_without_headboard():
    fp, got, bed, lean, full = dressed_bed(None)
    cushion = T.cushion_mesh(0.5, 0.15, 0.5)
    item = {"id": "c", "type": "cushion", "rotation_deg": 90.0, "center": list(R.to_world(fp["center"], 90.0, -0.3,
                                                                                            0.775))}
    plan = R.plan_decor(item, piece("bed_double", fp), full, cushion["verts"], cushion["faces"], "headboard",
                        lean_deg=12.0, back_caster=[bed, lean])
    assert "not_rested" not in plan, plan
    assert plan["rest"]["back_gap_m"] <= TOL["decor_back_gap_m"] and plan["pose"]["lean_deg"] > R.HEADBOARD_LEAN_DEG


def test_a_cushion_with_nothing_behind_it_stands_free_and_fails():
    seat = R.MeshCaster(*boxes_mesh([(-0.5, -0.4, 0.0, 0.5, 0.4, 0.45)]))      # a bench seat: no back at all
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    pose = {"center": [0.0, 0.1], "z": 0.43, "rotation_deg": 0.0, "lean_deg": 20.0}
    world = R.pose_vertices(cushion["verts"], pose)
    foot = {"center": [0.0, 0.1], "size": [0.45, 0.15], "rotation_deg": 0.0}
    m = _measured(seat, world, cushion["faces"], foot)
    ok, why = R.rest_ok(m)
    assert m["back_gap_m"] is None and not ok and any("stands free" in w for w in why)
    # against a wall (the host footprint's back edge) it leans on the wall
    wall = {"center": [0.0, 0.0], "size": [1.0, 0.8], "rotation_deg": 0.0}
    back = max(v[1] for v in world)
    m = _measured(seat, R.pose_vertices(cushion["verts"], dict(pose, center=[0.0, 0.1 + 0.4 - back])),
                  cushion["faces"], dict(foot, center=[0.0, 0.1 + 0.4 - back]), wall=wall)
    assert m["back"].startswith("wall") and m["back_gap_m"] <= TOL["decor_back_gap_m"]


def test_the_scene_check_fails_a_floating_cushion():
    """A cushion standing on the seat 0.3 m in front of the back: the old S5 (the gap under it, its penetration, its
    support) passed it; S5 fails it now."""
    from test_decor_rest import sofa_model

    v, f = sofa_model()                                   # a flat 0.48 m seat, the back from y = 0.20
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    front = {"center": list(R.to_world(SOFA_FP["center"], 30.0, -0.45, -0.25)), "z": 0.48 - R.SOFT_SINK_M,
             "rotation_deg": 30.0, "lean_deg": 12.0}
    world = R.pose_vertices(cushion["verts"], front)
    foot = {"center": front["center"], "size": [0.45, 0.15], "rotation_deg": 30.0}
    assert R.rest_ok(R.measure_rest(world, cushion["faces"], R.MeshCaster(v, f), foot, True))[0]   # the old S5
    building = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": [], "rooms": [],
                "furniture": [{"id": "f1", "type": "sofa", "level_id": "L0", "room_id": "r1", "footprint": SOFA_FP,
                               "asset": {"method": "parametric"}}],
                "decor": [{"id": "dec_1", "type": "cushion", "host_id": "f1", "level_id": "L0", "room_id": "r1",
                           "center": front["center"], "host_frame": {"support": "back"}}]}
    meshes = {"f1": {"verts": v, "faces": f},
              "dec_1": {"verts": R.pose_vertices(cushion["verts"], front), "faces": cushion["faces"],
                        "rest_footprint": {"center": front["center"], "size": [0.45, 0.15], "rotation_deg": 30.0}}}
    rep = SC.measure_pure(meshes, building)
    s5 = [x for x in rep["violations"] if x["check"] == "S5" and x["target"] == "dec_1"]
    assert s5 and "does not lean on its back" in s5[0]["message"] and rep["counts"]["failed_build"]
    assert K.kind_of(s5[0]) == "detached"


# --------------------------------------------------------------------------------------------------------- the bed
def test_no_throw_on_a_bed_model_with_its_own_made_bedding():
    """real04 f_L0_021 (hssd "Full Saddle Back Upholstered Bed", has_bedding true): a cream throw over its own white
    duvet and grey blanket showed the blanket through it in dark patches."""
    made = {"id": "b", "type": "bed_double", "asset": {"has_bedding": True}}
    bare = {"id": "b", "type": "bed_double", "asset": {"has_bedding": False}}
    sofa = {"id": "s", "type": "sofa", "asset": {"has_bedding": True}}
    assert R.own_bedding(made) and not R.own_bedding(bare) and not R.own_bedding(sofa)
    assert not D.takes_throw(made) and D.takes_throw(bare) and D.takes_throw(sofa)
    b = room_building(4.0, 4.0, "bedroom", furniture=[("bed_double", (2.0, 2.0), 0.0, (1.6, 2.0))])
    pieces = [p for p in b["furniture"] if p["room_id"] == RID]
    assert any(s.id.endswith(".throw") for s in DA.room_slots(b["rooms"][0], pieces, b)[0])
    pieces[0]["asset"] = {"has_bedding": True}
    assert not any(s.id.endswith(".throw") for s in DA.room_slots(b["rooms"][0], pieces, b)[0])


BED_FP = {"center": [1.0, 1.5], "size": [1.6, 2.0], "rotation_deg": 90.0}


def test_a_throw_the_host_pokes_through_or_whose_drape_tears_is_not_built():
    # a made bed whose duvet has a 2 cm fold ridge across the foot, between two rows of the 5 cm cloth grid
    ridge = boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 1.0, 0.55), (-0.8, -0.735, 0.55, 0.8, -0.715, 0.60)],
                       BED_FP["center"], BED_FP["rotation_deg"])
    item = {"id": "t", "type": "throw", "size": [1.52, 0.5, 0.05],
            "center": list(R.to_world(BED_FP["center"], 90.0, 0.0, -0.7))}
    plan = R.plan_throw(item, piece("bed_double", BED_FP), R.MeshCaster(*ridge), 0.0)
    assert "not_rested" in plan, plan["rest"]
    why = plan["not_rested"]["reason"]
    assert "pokes" in why or "penetration" in why
    # a deep fold (a 0.15 m wide trench 0.25 m deep) under the cloth: the drape tears
    trench = boxes_mesh([(-0.8, -1.0, 0.0, 0.8, -0.78, 0.55), (-0.8, -0.63, 0.0, 0.8, 1.0, 0.55),
                         (-0.8, -0.78, 0.0, 0.8, -0.63, 0.30)], BED_FP["center"], BED_FP["rotation_deg"])
    plan = R.plan_throw(item, piece("bed_double", BED_FP), R.MeshCaster(*trench), 0.0)
    assert "not_rested" in plan
    assert plan["not_rested"]["measured"]["cloth_edge_m"] > TOL["decor_cloth_edge_m"] or \
        "pokes" in plan["not_rested"]["reason"]
    # a flat made bed keeps its throw: nothing through it, no tear
    flat = R.MeshCaster(*boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 1.0, 0.55)], BED_FP["center"], BED_FP["rotation_deg"]))
    plan = R.plan_throw(item, piece("bed_double", BED_FP), flat, 0.0)
    assert "not_rested" not in plan
    assert plan["rest"]["poke_m"] <= TOL["decor_cloth_poke_m"] and plan["rest"]["cloth_edge_m"] <= 0.25


# ------------------------------------------------------------------------------------------------------- the lights
def test_a_hung_light_reaches_the_ceiling():
    """dec_L-1_008: planned 0.45 x 0.45 x 1.35 m from 1.50 m; the library model fitted to its own 0.358 m hung 0.99 m
    under the 2.85 m ceiling with no cord."""
    h = F.hang_plan("pendant_light", 1.50, 0.358, 2.85)
    assert h["lift_m"] == 0.0 and h["cord_m"] == pytest.approx(2.85 - 1.858 - P.SUSPENSION_CANOPY_H_M, abs=1e-4)
    assert h["gap_m"] == pytest.approx(0.992, abs=1e-3) and h["gap_left_m"] == pytest.approx(0.0, abs=1e-6)
    near = F.hang_plan("pendant_light", 2.0, 0.9448, 3.0)                     # an ABO pendant 5.5 cm short
    assert near["lift_m"] == pytest.approx(0.0552, abs=1e-4) and near["cord_m"] == 0.0 and near["gap_left_m"] == 0.0
    flush = F.hang_plan("ceiling_light", 3.0 - 0.12, 0.0236, 3.0)             # dec_L0_026: 9.6 cm under the ceiling
    assert flush["lift_m"] == pytest.approx(0.0964, abs=1e-4) and flush["gap_left_m"] == 0.0
    tall = F.hang_plan("pendant_light", 1.5, 1.4, 2.85)                       # taller than the drop: lowered
    assert tall["lift_m"] == pytest.approx(-0.05, abs=1e-4) and tall["gap_left_m"] == 0.0
    parts = P.suspension_parts(h["cord_m"])
    assert {p["role"] for p in parts} == {"cord", "canopy"}
    sv, _sf, _sk = P.world_mesh(parts, (6.0, 4.0), 0.0, -3.0 + h["model_top_m"])
    assert max(v[2] for v in sv) == pytest.approx(-3.0 + 2.85, abs=1e-6)        # its canopy on the ceiling


def _pendant_case(with_cord: bool):
    shade = P.world_mesh(P.decor_parts("vase", 0.32, 0.32, 0.358), (6.0, 4.0), 0.0, -3.0 + 1.5)
    meshes = [(shade[0], shade[1])]
    if with_cord:
        h = F.hang_plan("pendant_light", 1.5, 0.358, 2.85)
        cord = P.world_mesh(P.suspension_parts(h["cord_m"]), F.top_point(shade[0]), 0.0, -3.0 + h["model_top_m"])
        meshes.append((cord[0], cord[1]))
    v, f = merge(*meshes)
    building = {"levels": [{"id": "L-1", "elevation": -3.0, "ceiling_height": 2.85}], "walls": [], "rooms": [],
                "furniture": [], "decor": [{"id": "dec_L-1_008", "type": "pendant_light", "level_id": "L-1",
                                            "room_id": "r_L-1_salon", "host_id": None, "center": [6.0, 4.0, 1.5]}]}
    return {"dec_L-1_008": {"verts": v, "faces": f}}, building


def test_the_scene_check_and_the_model_review_find_a_light_hanging_in_the_air():
    meshes, building = _pendant_case(False)
    rep = SC.measure_pure(meshes, building)
    s5 = [x for x in rep["violations"] if x["check"] == "S5"]
    assert s5 and s5[0]["metrics"]["hang_gap_m"] == pytest.approx(0.992, abs=0.01) and "hangs in the air" in \
        s5[0]["message"]
    meshes, building = _pendant_case(True)
    assert not [x for x in SC.measure_pure(meshes, building)["violations"] if x["check"] == "S5"]
    # the model review reads the scene manifest: the old record (no hang record, its box) and a new one
    built = {"levels": building["levels"]}
    old = {"kind": "decor", "type": "pendant_light", "decor_id": "dec_L-1_008", "level_id": "L-1",
           "room_id": "r_L-1_salon", "center": [6.045, 4.227, -1.321], "size": [0.3189, 0.45, 0.358]}
    got, n = MR.decor_attached({"objects": [old]}, built)
    assert n == 1 and got and got[0]["check"] == "M13" and got[0]["kind"] == "detached"
    assert got[0]["metrics"]["gap_m"] == pytest.approx(0.992, abs=0.01)
    new = dict(old, hang=F.hang_plan("pendant_light", 1.5, 0.358, 2.85))
    assert MR.decor_attached({"objects": [new]}, built) == ([], 1)
    assert "M13" in MR.CHECKS and K.kind_of({"check": "M13"}) == "detached" and "detached" in K.KINDS


def test_the_model_review_reads_the_rest_records():
    floating = {"kind": "decor", "type": "cushion", "decor_id": "dec_L1_003", "host_id": "f_L1_017", "support": "back",
                "room_id": "r1", "rest": {"gap_m": -0.004, "penetration_m": 0.015, "support_share": 1.0, "soft": True,
                                          "back_gap_m": 0.31}}
    ok = dict(floating, decor_id="dec_L1_004", rest=dict(floating["rest"], back_gap_m=0.004))
    got, n = MR.decor_attached({"objects": [floating, ok]}, {"levels": []})
    assert n == 2 and [g["target"] for g in got] == ["dec_L1_003"] and "does not lean" in got[0]["message"]


# ------------------------------------------------------------------------------------------------- the set tables
def _dining_room(chairs=True, centre=None):
    furniture = [("table_dining", (3.0, 2.5), 0.0, (1.8, 0.9))]
    if chairs:
        furniture += [("chair", (x, y), rot, (0.45, 0.5)) for x in (2.4, 3.0, 3.6)
                      for y, rot in ((1.75, 0.0), (3.25, 180.0))]
    b = room_building(6.0, 5.0, "dining", furniture=furniture)
    pieces = [p for p in b["furniture"] if p["room_id"] == RID]
    items = [] if centre is None else [dict(centre, host_id=pieces[0]["id"])]
    return b, b["rooms"][0], pieces, items


def _new_id():
    n = [0]

    def make(level_id):
        n[0] += 1
        return f"dec_{level_id}_{900 + n[0]}"
    return make


def test_a_dining_table_is_set_at_every_chair():
    b, room, pieces, items = _dining_room()
    table = pieces[0]
    made = TT.dress_tops(room, pieces, b, items, _new_id())
    plates = [i for i in made if i["type"] == "plate"]
    glasses = [i for i in made if i["type"] == "glass"]
    assert len(plates) == 6 and len(glasses) == 6
    assert sum(1 for i in made if i["slot"].endswith("centre_piece")) == 1
    boxes = [TT.local_box(table, i) for i in made]
    assert all(TT.inside_top(table, bx, 0.0) for bx in boxes)
    assert all(TT.boxes_clear(a, c) for k, a in enumerate(boxes) for c in boxes[k + 1:])     # clear of each other
    for p in plates:                                                         # in front of its chair, at the edge
        _x, y = TT._local(table, *p["center"])
        assert abs(abs(y) - (0.45 - TT.SETTING_INSET_M - TT.PLATE_SIZE[0] / 2.0)) < 1e-6
    for i in made:
        assert i["source"] == "added_by_ai" and i["method"] == "rule" and TT.REASON_TAG in i["reason"]
        assert i["host_id"] == table["id"] and i["id"].startswith("dec_") and i["type"] in D.DECOR_TYPES
    # an AI centrepiece already there stays, the settings keep clear of it, no second centre piece
    vase = {"type": "vase", "center": list(table["footprint"]["center"]), "size": [0.18, 0.18, 0.4],
            "rotation_deg": 0.0}
    b, room, pieces, items = _dining_room(centre=vase)
    made = TT.dress_tops(room, pieces, b, items, _new_id())
    assert not any(i["slot"].endswith("centre_piece") for i in made)
    vb = TT.local_box(pieces[0], items[0])
    assert all(TT.boxes_clear(vb, TT.local_box(pieces[0], i)) for i in made)
    # no chairs: no setting
    b, room, pieces, items = _dining_room(chairs=False)
    assert not [i for i in TT.dress_tops(room, pieces, b, items, _new_id()) if i["type"] in TT.SETTING_TYPES]


def test_tops_get_a_small_group_and_a_plate_rests_on_the_real_top():
    b = room_building(6.0, 5.0, "living", furniture=[("sofa", (3.0, 4.5), 180.0, (2.2, 0.9)),
                                                     ("table_coffee", (3.0, 3.2), 0.0, (1.1, 0.6)),
                                                     ("sideboard", (0.25, 2.5), 90.0, (1.6, 0.45))])
    pieces = [p for p in b["furniture"] if p["room_id"] == RID]
    room = b["rooms"][0]
    made = TT.dress_tops(room, pieces, b, [], _new_id())
    for host in pieces[1:]:
        mine = [i for i in made if i["host_id"] == host["id"]]
        assert 2 <= len(mine) <= TT.GROUPS[host["type"]][0], (host["type"], mine)
        boxes = [TT.local_box(host, i) for i in mine]
        assert all(TT.inside_top(host, bx) for bx in boxes)
        assert all(TT.boxes_clear(a, c) for k, a in enumerate(boxes) for c in boxes[k + 1:])
    # the style's density: a sparse (japandi) room gets smaller groups, a layered one larger
    sparse = TT.dress_tops(room, pieces, b, [], _new_id(), density="sparse")
    layered = TT.dress_tops(room, pieces, b, [], _new_id(), density="layered")
    assert len(sparse) < len(made) < len(layered)
    # a plate on a 0.74 m table top rests on it by rays (S5: nothing floats)
    table = {"id": "t1", "type": "table_dining", "footprint": {"center": [0.0, 0.0], "size": [1.8, 0.9],
                                                               "rotation_deg": 0.0}}
    top = R.MeshCaster(*boxes_mesh([(-0.9, -0.45, 0.70, 0.9, 0.45, 0.74)] + [
        (sx * 0.85 - 0.03, sy * 0.4 - 0.03, 0.0, sx * 0.85 + 0.03, sy * 0.4 + 0.03, 0.70)
        for sx in (-1, 1) for sy in (-1, 1)]))
    plate = F.local_decor_mesh({"type": "plate", "size": list(TT.PLATE_SIZE)}, "plate", "top")
    plan = R.plan_decor({"id": "p", "type": "plate", "center": [0.3, -0.24], "rotation_deg": 0.0}, table, top,
                        plate["verts"], plate["faces"], "top")
    assert "not_rested" not in plan and plan["pose"]["z"] == pytest.approx(0.74)
    assert plan["rest"]["gap_m"] <= TOL["decor_gap_m"] and R.rest_ok(plan["rest"])[0]


def test_the_brief_decor_switch_keeps_the_tables_bare():
    b, room, pieces, items = _dining_room()
    b["project"]["brief"] = {"decor": False}
    out, _records = DA.apply(b, "modern", {"answers": {}})
    assert out["decor"] == []
    b["project"]["brief"] = {"decor": "rules"}
    out, _records = DA.apply(b, "modern", {"answers": {}})
    assert sum(1 for d in out["decor"] if d["type"] == "plate") == 6
    assert not set(TT.SETTING_TYPES) & set(DA.AI_TYPES)                      # the AI never chooses them
