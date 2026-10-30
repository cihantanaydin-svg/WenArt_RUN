"""30 Oct 2026 (lesson UL167): a sofa's rests touch its sitting. CPU only.

The user on real04 run 20261030-043021-full, the living room's low white L sofa ("Sofa en L", 3dwh_bc790e2f62189290d277
caa7): "I like this sofa but resting pieces seems like not connected to sitting, requires fixing". The model is nine
loose parts; the build's joining (``soft_seats.join_plan``, UL140) found one body and no gap ("parts": 9, "bodies": 1,
"gaps": 0) because every part's box touches the L seat's or the L base's box, while the back panels stood on the base
behind the seat cushion and the corner's backs did not meet.

Now (every soft seat, ``soft_seats.rest_plan``): the rests (back panels, back cushions standing behind the seat, arms)
are measured on their vertices against the seat they stand beside and slide to touch it (no gap over 5 mm), with
their piping and what lies on them; a rest held over its base comes down onto it; the two backs of an L's corner meet;
the model review M33 / Argus U36 name a rest left apart (``rest_apart``). The parametric and module sofas pass the
same measure.
"""
from __future__ import annotations

import pytest

from wenart.blender import furniture as FU
from wenart.blender import model_review as MR
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import soft_seats as SS
from wenart.audit import lessons as AL


def cube(x0, y0, z0, x1, y1, z1, base=0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return v, [[i + base for i in q] for q in f]


def mesh(*boxes):
    verts, faces = [], []
    for b in boxes:
        v, f = cube(*b, base=len(verts))
        verts += v
        faces += f
    return verts, faces


BASE = ((-2.3, -0.2, 0.0, 1.5, 0.9, 0.18), (1.5, -0.9, 0.0, 2.3, 0.9, 0.18))       # one L part (shared corner)
SEAT = ((-2.29, -0.19, 0.18, 1.5, 0.62, 0.42), (1.5, -0.89, 0.18, 2.06, 0.62, 0.42))  # one L cushion on it


def sofa_en_l(side_back_rear: float = 0.64, back_bottom: float = 0.18):
    """The real04 "Sofa en L" as the user saw it (piece frame, front -Y): an L base under everything, an L seat
    cushion on it, the long back standing on the base 4 cm behind the cushion, the chaise's side back 4 cm beside it,
    a piping strip inside the long back's box and a tray lying on its top."""
    return mesh(*BASE, *SEAT,
                (-2.29, 0.66, back_bottom, 2.29, 0.86, back_bottom + 0.59),       # 4: the long back
                (2.10, -0.89, 0.18, 2.29, side_back_rear, 0.70),                  # 5: the chaise's side back
                (-2.0, 0.66, back_bottom + 0.52, 2.0, 0.67, back_bottom + 0.53),  # 6: piping inside the back's box
                (-0.3, 0.70, back_bottom + 0.59, 0.3, 0.84, back_bottom + 0.61))  # 7: a tray on the back's top


def _parts(verts, faces):
    vp, areas = SS.vertex_parts(len(verts), faces, SS.face_parts(verts, faces), verts)
    return vp, areas


def _ids(boxes):
    """{name: part} of ``sofa_en_l`` by the boxes' places."""
    by = {}
    for p, b in boxes.items():
        if b[2] < 0.01:
            by["base"] = p
        elif b[5] == pytest.approx(0.42, abs=1e-6):
            by["seat"] = p
        elif b[3] - b[0] > 4.0 and b[4] - b[1] > 0.1:
            by["back"] = p
        elif b[4] - b[1] > 1.0:
            by["side"] = p
        elif b[4] - b[1] < 0.02:
            by["piping"] = p
        else:
            by["tray"] = p
    return by


def test_the_boxes_saw_no_gap_on_the_real_sofa_but_the_vertices_do():
    verts, faces = sofa_en_l()
    vp, areas = _parts(verts, faces)
    boxes = SS.part_boxes(verts, vp)
    assert len(boxes) == 6
    plan = SS.join_plan(boxes, areas)
    assert plan["record"]["bodies"] == 1 and plan["record"]["gaps"] == 0      # what the run recorded
    seats, rests = SS.seat_roles(boxes)
    by = _ids(boxes)
    assert seats == [by["seat"]] and sorted(rests) == sorted([by["back"], by["side"]])
    rec = SS.rest_plan(verts, vp)["record"]
    assert rec["max_gap_m"] == pytest.approx(0.04, abs=1e-6)


def test_the_backs_slide_against_the_seat_with_their_piping_and_tray_and_the_corner_meets():
    verts, faces = sofa_en_l()
    vp, areas = _parts(verts, faces)
    joined, rec = SS.join_parts(verts, vp, areas)
    rests = rec["rests"]
    assert rests["moved"] == 2 and rests["max_gap_after_m"] <= SS.REST_TOUCH_M and rec["joined"] == 2
    before, after = SS.part_boxes(verts, vp), SS.part_boxes(joined, vp)
    by = _ids(before)
    assert after[by["back"]][1] == pytest.approx(0.62)                   # the long back against the cushion
    assert after[by["side"]][0] == pytest.approx(2.06)                   # the side back against the chaise
    assert after[by["back"]][2] == pytest.approx(0.18)                   # still on the base
    for p in ("piping", "tray"):                                         # they went with the back
        assert after[by[p]][1] - before[by[p]][1] == pytest.approx(-0.04)
    assert after[by["seat"]] == before[by["seat"]] and after[by["base"]] == before[by["base"]]
    # the corner: the side back's rear end reaches the long back (they meet, no gap)
    assert after[by["side"]][4] >= after[by["back"]][1] - 1e-9
    assert rests.get("corner_gap_after_m", 0.0) <= SS.REST_TOUCH_M


def test_a_short_side_back_slides_along_to_close_the_corner():
    verts, faces = sofa_en_l(side_back_rear=0.55)
    vp, areas = _parts(verts, faces)
    joined, rec = SS.join_parts(verts, vp, areas)
    after = SS.part_boxes(joined, vp)
    by = _ids(SS.part_boxes(verts, vp))
    assert after[by["side"]][4] == pytest.approx(after[by["back"]][1])    # its rear end on the long back's face
    assert after[by["side"]][0] == pytest.approx(2.06)
    assert rec["rests"]["corner_gap_after_m"] == pytest.approx(0.0)


def test_a_back_held_over_its_base_comes_down_onto_it():
    verts, faces = sofa_en_l(back_bottom=0.21)
    vp, areas = _parts(verts, faces)
    joined, rec = SS.join_parts(verts, vp, areas)
    after = SS.part_boxes(joined, vp)
    by = _ids(SS.part_boxes(verts, vp))
    assert after[by["back"]][2] == pytest.approx(0.18) and after[by["back"]][1] == pytest.approx(0.62)
    assert after[by["tray"]][2] == pytest.approx(after[by["back"]][5])   # the tray stays on it


def test_a_rest_apart_by_design_a_back_cushion_on_the_seat_and_the_floor_stay():
    # a console 20 cm behind the seat: apart by design
    verts, faces = mesh((-1.0, -0.4, 0.0, 1.0, 0.4, 0.42), (-1.0, 0.6, 0.0, 1.0, 0.8, 0.85))
    vp, areas = _parts(verts, faces)
    plan = SS.rest_plan(verts, vp)
    assert plan["shift"] == {} and plan["record"]["items"][0].get("apart_by_design")
    # a back cushion standing on the seat (its centre over the seat): not a rest beside it
    verts, faces = mesh((-1.0, -0.45, 0.0, 1.0, 0.45, 0.45), (-0.9, 0.15, 0.45, 0.9, 0.40, 0.85))
    vp, areas = _parts(verts, faces)
    assert SS.rest_plan(verts, vp)["shift"] == {}
    # an arm standing on the floor 3 cm from the seat slides in; it is never lifted nor lowered under the floor
    verts, faces = mesh((-1.0, -0.45, 0.0, 1.0, 0.45, 0.45), (1.03, -0.45, 0.0, 1.23, 0.45, 0.70))
    vp, areas = _parts(verts, faces)
    joined, rec = SS.join_parts(verts, vp, areas)
    b = SS.part_boxes(joined, vp)
    assert b[1][0] == pytest.approx(1.0) and b[1][2] == pytest.approx(0.0)


def test_the_parametric_and_module_sofas_pass_the_same_measure():
    for parts in (P._sofa(2.2, 0.95, 0.85), P._sofa_corner(2.8, 1.9, 0.85)):
        rec = SS.parts_rest_record(parts)
        assert rec["rests"] >= 1 and rec["seats"] >= 1
        assert rec["max_gap_m"] <= SS.REST_TOUCH_M and rec["moved"] == 0
    plan = MOD.module_plan({"id": "s", "type": "sofa_corner", "height": 0.85, "chaise_side": "right",
                            "footprint": {"center": [0, 0], "size": [3.0, 1.9], "rotation_deg": 0}})
    assert plan["builder"] == "sofa_l"
    rec = SS.parts_rest_record(MOD.module_parts(plan))
    assert rec["max_gap_m"] <= SS.REST_TOUCH_M and rec["moved"] == 0
    # their back cushions lean back a few degrees on the deck behind the seat cushion
    assert 5.0 <= P.BACK_CUSHION_LEAN_DEG <= 12.0


def test_fit_vertices_closes_the_rests_and_keeps_the_drawn_width():
    verts, faces = sofa_en_l()
    vp, areas = _parts(verts, faces)
    asset = {"fit_scale": [4.3761 / 4.6] * 3, "scaling": "uniform", "front_axis": "-Y", "up_axis": "+Z"}
    fp = {"center": [3.0, 3.0], "size": [4.3761, 1.9657], "rotation_deg": 270.0}
    world, info = FU.fit_vertices(verts, asset, fp, 0.0, join=(vp, areas), align="back")
    assert info["parts"]["rests"]["moved"] == 2 and info["parts"]["rests"]["max_gap_after_m"] <= SS.REST_TOUCH_M
    assert info["bbox_m"][0] == pytest.approx(4.3761, abs=1e-3)         # the drawn width kept


def test_the_review_names_a_rest_left_apart():
    base = {"kind": "furniture", "type": "sofa_corner", "method": "library", "wenart_id": "f_1", "room_id": "r",
            "textured": True, "asset": {"asset_id": "3dwh_x"}, "shading": {"file_smooth": 4, "smooth": 4}}
    ok = dict(base, parts={"max_gap_after_m": 0.0, "rests": {"rests": 2, "max_gap_after_m": 0.0}})
    assert SS.review({"objects": [ok]}) == ([], 1)
    bad = dict(base, parts={"max_gap_after_m": 0.0, "rests": {"rests": 2, "max_gap_after_m": 0.03,
                                                              "corner_gap_after_m": 0.01}})
    got = SS.review({"objects": [bad]})[0]
    assert [g["problem"] for g in got] == ["rest_apart"] and got[0]["severity"] == "major"
    assert got[0]["lesson"] == "UL167" and got[0]["metrics"]["gap_m"] == pytest.approx(0.03)
    assert "rest_plan" in got[0]["fix"]
    mr = MR.soft_seats_review({"objects": [bad]})[0]
    assert mr[0]["kind"] == "detached" and mr[0]["owner"] == "build"
    u36 = AL.soft_seats({}, {"objects": [bad]})
    assert u36[0]["kind"] == "detached" and u36[0]["check"] == "U36"
