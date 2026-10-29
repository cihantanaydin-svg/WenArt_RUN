"""29 Oct 2026: a cushion on any bed with a headboard stands on its bedding against the headboard, whatever the bedding
is made of (``rest.place_leaning(stand=True)``, ``rest.stand_modes``, ``rest._rail_hit``; module docstring of
``wenart/blender/rest.py``).

The Blender-backed tests (skipped without Blender) built no cushion on the parametric bed (``test_blender_furniture``:
"no headboard found on the built host") nor on a library bed frame made up with ``parametric.frame_bedding``
(``test_blender_bedframe_decor``: "gap 0.305 m behind its upper part"): those beds are one mesh with their lying
pillows, so the dressed bed's caster without the pillows (``furniture.BED_CASTER``) does not exist for them and only
the lean in front of the pillows was tried, which the 28 Oct rule (``measure_back``: a leaning cushion touches its back
in its upper part) refuses for pillows lower than a cushion's upper part. Pure ray casts on hand-made meshes, the code
the scene builder runs on Blender's BVH."""
from __future__ import annotations

import pytest

from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import textiles as T

from test_decor_rest import boxes_mesh, merge, piece

TOL = R.REST_TOLERANCES
FP = {"center": [6.5, 1.02], "size": [1.6, 2.0], "rotation_deg": 180.0}     # head at local +Y (here the south wall)


def frame_bed():
    """The library bed frame of ``test_blender_bedframe_decor`` as the fit places it (its back on the footprint's back
    edge): rails, a deck at 0.30 m and a 1.6 x 0.06 x 1.0 m headboard, made up with ``parametric.frame_bedding`` (the
    mattress on the deck, the duvet over the foot, two lying pillows), one mesh as the build makes it."""
    boxes = [(-0.8, -1.1, 0.15, -0.74, 0.94, 0.38), (0.74, -1.1, 0.15, 0.8, 0.94, 0.38),
             (-0.8, -1.1, 0.15, 0.8, -1.04, 0.38), (-0.74, -1.04, 0.25, 0.74, 0.94, 0.30),
             (-0.8, 0.94, 0.0, 0.8, 1.0, 1.0)]
    frame = boxes_mesh(boxes, FP["center"], FP["rotation_deg"])
    parts = P.frame_bedding(1.6, 2.0, 0.30)
    v, f, _keys = P.world_mesh(parts, FP["center"], FP["rotation_deg"], 0.0)
    return R.MeshCaster(*merge(frame, (v, f))), P.frame_bedding_info(1.6, 2.0, 0.30)


def parametric_bed():
    """The parametric double bed (``parametric._bed``: a headboard, two lying pillows 4 cm apart), one mesh."""
    parts = P.build_parts("bed_double", 1.6, 2.0, 0.55, {"id": "b", "type": "bed_double", "footprint": FP})
    v, f, _keys = P.world_mesh(parts, FP["center"], FP["rotation_deg"], 0.0)
    return R.MeshCaster(v, f)


def cube(w, t, h):
    verts = [(x, y, z) for x in (-w / 2, w / 2) for y in (-t / 2, t / 2) for z in (0.0, h)]
    faces = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return {"verts": verts, "faces": faces}


def local_y(pose):
    return R.to_local(FP["center"], FP["rotation_deg"], *pose["center"])[1]


def test_a_bed_tries_standing_against_the_headboard_first_then_the_lean():
    assert R.stand_modes("headboard") == (True, False)
    assert R.stand_modes("back") == (False,)                  # a sofa's cushion leans on its back, as before
    assert set(R.BED_STAND_SHARES) <= set(R.BACK_PROBE_SHARES) and min(R.BED_STAND_SHARES) >= 0.5


def test_frame_bedding_cushion_stands_on_the_pillows_against_the_headboard(monkeypatch):
    """Measured in the built scene: the lowest back rays met the lying pillows' front (local y 0.467, 3 cm over the
    mattress), the upper ones the headboard (0.94); the nearest put the cushion on the mattress in front of the
    pillows (top 0.70 m) and its upper part stood 0.29-0.34 m before the headboard at every lean."""
    caster, rec = frame_bed()
    cushion = T.cushion_mesh(0.5, 0.15, 0.5)
    item = {"id": "dec_L0_003", "type": "cushion", "rotation_deg": 180.0,
            "center": list(R.to_world(FP["center"], 180.0, -0.4, 0.8)), "host_frame": {"support": "headboard"}}
    with monkeypatch.context() as mp:                         # the lean of before only
        mp.setattr(R, "stand_modes", lambda support: (False,))
        old = R.plan_decor(item, piece("bed_double", FP), caster, cushion["verts"], cushion["faces"], "headboard",
                           lean_deg=12.0)
    assert "not_rested" in old and "does not lean on its back" in old["not_rested"]["reason"], old
    assert old["not_rested"]["measured"]["back_gap_m"] > 0.2
    plan = R.plan_decor(item, piece("bed_double", FP), caster, cushion["verts"], cushion["faces"], "headboard",
                        lean_deg=12.0)
    assert "not_rested" not in plan, plan
    rest, pose = plan["rest"], plan["pose"]
    assert pose["how"].startswith("standing on the bedding against the backrest behind its upper part")
    assert rest["back"] == "host" and rest["back_gap_m"] <= TOL["decor_back_gap_m"]
    assert rest["gap_m"] <= TOL["decor_gap_m"] and rest["penetration_m"] <= TOL["decor_pen_soft_m"]
    low = min(v[2] for v in plan["verts"])
    assert rec["mattress_top_m"] + 0.05 < low < rec["top_m"]                     # on the pillows, sunk into them
    assert 1.0 - R.BED_HEAD_ZONE_M <= local_y(pose) < 0.94                       # at the head, before the headboard


def test_parametric_bed_cushion_over_the_pillow_gap_stands_against_the_headboard(monkeypatch):
    """Measured in the built scene: the centre ray passed between the two pillows to the headboard (local y 0.944),
    their flanks 0.075 m to each side squeezed the cushion (0.14 m < ``MIN_CUSHION_W``), the three rays met the pillows'
    front (cushion centre 0.336 < 1.0 - ``BED_HEAD_ZONE_M``) and the back edge fallback put it between the pillows again:
    "no headboard found"."""
    caster = parametric_bed()
    box = cube(0.4, 0.25, 0.45)
    item = {"id": "dec_T04", "type": "cushion", "rotation_deg": 180.0, "center": list(FP["center"]),
            "host_frame": {"support": "headboard"}}
    with monkeypatch.context() as mp:
        mp.setattr(R, "stand_modes", lambda support: (False,))
        old = R.plan_decor(item, piece("bed_double", FP), caster, box["verts"], box["faces"], "headboard")
    assert "not_rested" in old and "no headboard found" in old["not_rested"]["reason"], old
    plan = R.plan_decor(item, piece("bed_double", FP), caster, box["verts"], box["faces"], "headboard")
    assert "not_rested" not in plan, plan
    rest, pose = plan["rest"], plan["pose"]
    assert pose["how"].startswith("standing on the bedding") and abs(R.to_local(FP["center"], 180.0,
                                                                                  *pose["center"])[0]) < 1e-6
    assert pose["size"][0] == pytest.approx(0.4)                                  # not narrowed by the pillows
    assert rest["back_gap_m"] <= TOL["decor_back_gap_m"] and rest["gap_m"] <= TOL["decor_gap_m"]
    assert rest["penetration_m"] <= TOL["decor_pen_soft_m"] and rest["support_share"] >= TOL["decor_support_share"]
    # on the pillows (the mattress top is 0.55 m), never on their top as Milestone 11 put it (``bedding_top``)
    assert 0.55 - R.SOFT_SINK_M - 1e-3 <= pose["z"] < P.bedding_top(1.6, 2.0, 0.55) - 0.05
    assert local_y(pose) >= 1.0 - R.BED_HEAD_ZONE_M


def test_a_rail_beside_the_item_rises_over_its_seat_a_pillow_does_not():
    """``_rail_hit``: the flank of a pillow 0.08 m over the item's seat is the bedding it stands on; a rail 0.4 m over it
    is a rail."""
    seat = 0.6
    mesh = R.MeshCaster(*boxes_mesh([(0.1, -0.2, 0.5, 0.5, 0.2, seat + 0.08),          # a pillow beside it
                                     (0.7, -0.2, 0.3, 0.75, 0.2, seat + 0.4)]))       # a rail further out
    top = 2.0
    assert R._horizontal(mesh, (0.0, 0.0, seat + 0.04), (1.0, 0.0, 0.0)) == pytest.approx(0.1)
    assert R._rail_hit(mesh, (0.0, 0.0, seat + 0.04), (1.0, 0.0, 0.0), 1.0, seat, top) == pytest.approx(0.7)
    assert R._rail_hit(mesh, (0.0, 0.0, seat + 0.04), (-1.0, 0.0, 0.0), 1.0, seat, top) is None


def test_no_stand_without_a_headboard_and_never_mid_bed():
    """Nothing behind the cushion's upper part (a bed without headboard, its pillows lower than the cushion): no stand,
    the lean of before follows (28 Oct: leaning back on the pillows); a sofa is never asked to stand."""
    fp = {"center": [2.0, 3.0], "size": [1.6, 2.0], "rotation_deg": 90.0}
    v, f = boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 1.0, 0.42)], fp["center"], fp["rotation_deg"])
    bed = R.MeshCaster(v, f)
    got = T.duvet_and_pillows(bed, fp, 0.0)
    full = R.MeshCaster(*merge((v, f), *[(p["verts"], p["faces"]) for p in got["parts"]]))
    planned = R.to_world(fp["center"], 90.0, -0.3, 0.775)
    assert R.place_leaning(full, fp, planned, (0.5, 0.15, 0.5), 24.0, bed=True, stand=True) is None
    assert R.place_leaning(full, fp, planned, (0.5, 0.15, 0.5), 24.0, bed=True) is not None
    # a headboard further out than the head zone (a "backrest" mid-bed) is no headboard to stand against
    v2, f2 = boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 1.0, 0.42), (-0.8, -0.2, 0.0, 0.8, -0.1, 1.2)], fp["center"],
                        fp["rotation_deg"])
    assert R.place_leaning(R.MeshCaster(v2, f2), fp, planned, (0.5, 0.15, 0.5), 24.0, bed=True, stand=True) is None
    sofa = R.MeshCaster(*boxes_mesh([(-1.0, -0.45, 0.0, 1.0, 0.25, 0.45), (-1.0, 0.25, 0.0, 1.0, 0.45, 0.85)]))
    sofa_fp = {"center": [0.0, 0.0], "size": [2.0, 0.9], "rotation_deg": 0.0}
    assert R.place_leaning(sofa, sofa_fp, (0.0, 0.0), (0.45, 0.15, 0.45), 20.0, stand=True) == \
        R.place_leaning(sofa, sofa_fp, (0.0, 0.0), (0.45, 0.15, 0.45), 20.0)
