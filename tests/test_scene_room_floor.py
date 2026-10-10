"""Milestone 12 track S with track L's room floors (lead follow-up of 10 Oct 2026): every furniture piece and decor
item stands on its room's floor, ``wenart.blender.shell.room_floor_z(room, level)`` (the level's elevation + the
room's ``floor_offset_m``, sunken or raised), not on the level's elevation: the builder (``furniture.piece_floor_z``,
``decor_floor``, ``fit_vertices`` / ``world_mesh`` at that floor), the textiles' floor fallback (``textiles.drape``),
and the scene checks (S1 floor gap, S5 floor decor, S2 wall boxes from the sunken floor)."""
from __future__ import annotations

import pytest

from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import scene_checks as SC
from wenart.blender import shell as SH
from wenart.blender import textiles as T

from test_decor_rest import boxes_mesh

LIB = {"method": "library", "asset_id": "abo_x", "licence": "CC-BY-4.0", "library": "abo",
       "front_axis": "-Y", "up_axis": "+Z", "fit_scale": [1.0, 1.0, 1.0]}
LEVEL = {"id": "L1", "elevation": 3.0, "ceiling_height": 2.7}
SUNK = {"id": "sunk", "level_id": "L1", "floor_offset_m": -0.30,
        "polygon": [[0.0, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]]}
FLAT = {"id": "flat", "level_id": "L1", "polygon": [[5.0, 0.0], [9.0, 0.0], [9.0, 4.0], [5.0, 4.0]]}
RAISED = {"id": "raised", "level_id": "L1", "floor_offset_m": 0.15,
          "polygon": [[0.0, 4.0], [5.0, 4.0], [5.0, 8.0], [0.0, 8.0]]}


def piece(pid, ftype, center, size, rot=0.0, room="sunk", asset=None, **extra):
    out = dict({"id": pid, "type": ftype, "level_id": "L1", "status": "verified", "source": "from_documents",
                "front_deg": (270.0 + rot) % 360.0,
                "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
                "asset": dict(asset or {"method": "parametric", "asset_id": f"parametric:{ftype}"})}, **extra)
    if room is not None:
        out["room_id"] = room
    return out


def building(furniture=(), decor=()):
    return {"levels": [dict(LEVEL)], "rooms": [dict(SUNK), dict(FLAT), dict(RAISED)],
            "walls": [{"id": "w_sunk", "level_id": "L1", "start": [0.0, 0.0], "end": [5.0, 0.0], "thickness": 0.2,
                       "height": 2.7},
                      {"id": "w_flat", "level_id": "L1", "start": [5.0, 0.0], "end": [9.0, 0.0], "thickness": 0.2,
                       "height": 2.7}],
            "furniture": list(furniture), "decor": list(decor)}


def parametric_on(p, floor_z):
    """The builder's parametric mesh of a piece on ``floor_z`` (``_parametric_object``: ``P.world_mesh``)."""
    fp = p["footprint"]
    h = P.proxy_height(p["type"], p.get("height"))[0]
    v, f, _k = P.world_mesh(P.build_parts(p["type"], *fp["size"], h, piece=p), fp["center"], fp["rotation_deg"],
                            floor_z)
    return {"verts": v, "faces": f}


def test_a_sofa_in_a_sunken_room_stands_on_the_room_floor_and_s1_measures_against_it():
    sofa = piece("s1", "sofa", (2.5, 2.0), (2.0, 0.9), asset=LIB)
    b = building([sofa])
    floor = F.piece_floor_z(b, LEVEL, sofa)
    assert floor == pytest.approx(SH.room_floor_z(SUNK, LEVEL)) == pytest.approx(2.70)
    # the sofa's bottom: a parametric build and a library model fitted on the footprint
    mesh = parametric_on(sofa, floor)
    assert min(v[2] for v in mesh["verts"]) == pytest.approx(2.70)
    model = boxes_mesh([(-1.0, -0.45, 0.0, 1.0, 0.45, 0.45), (-1.0, 0.25, 0.45, 1.0, 0.45, 0.85)])[0]
    fitted, _info = F.fit_vertices(model, LIB, sofa["footprint"], floor)
    assert min(v[2] for v in fitted) == pytest.approx(2.70)
    # S1: the floor gap against the sunken floor
    report = SC.measure_pure({"s1": mesh}, b)
    assert not [v for v in report["violations"] if v["check"] == "S1"]
    assert report["measured"]["s1"]["floor_gap_m"] == pytest.approx(0.0, abs=1e-6)
    assert SC.floor_z_of(b, sofa) == pytest.approx(2.70)
    # on the level's elevation (before): 30 cm above the room's floor, S1 fails
    old = SC.measure_pure({"s1": parametric_on(sofa, LEVEL["elevation"])}, b)
    (s1,) = [v for v in old["violations"] if v["check"] == "S1"]
    assert s1["metrics"]["floor_gap_m"] == pytest.approx(0.30)


def test_the_room_is_found_by_its_outline_when_the_piece_has_no_room_id():
    b = building()
    assert F.piece_floor_z(b, LEVEL, piece("a", "armchair", (2.0, 1.0), (0.8, 0.8), room=None)) == pytest.approx(2.70)
    assert F.piece_floor_z(b, LEVEL, piece("c", "armchair", (2.0, 6.0), (0.8, 0.8), room=None)) == pytest.approx(3.15)
    assert F.piece_floor_z(b, LEVEL, piece("d", "armchair", (7.0, 1.0), (0.8, 0.8), room=None)) == pytest.approx(3.0)
    assert F.piece_floor_z(b, LEVEL, piece("e", "armchair", (20.0, 1.0), (0.8, 0.8), room=None)) == pytest.approx(3.0)
    rug = {"id": "r", "type": "rug", "level_id": "L1", "center": [1.0, 1.0], "size": [2.0, 1.4]}
    assert F.piece_floor_z(b, LEVEL, rug) == pytest.approx(2.70)                 # decor: its centre
    # a room id wins over the outline; a non-number offset is the level's floor
    assert F.piece_floor_z(b, LEVEL, piece("f", "armchair", (2.0, 1.0), (0.8, 0.8), room="flat")) == 3.0
    bad = dict(b, rooms=[dict(SUNK, floor_offset_m="low")])
    assert F.piece_floor_z(bad, LEVEL, piece("g", "armchair", (2.0, 1.0), (0.8, 0.8))) == pytest.approx(3.0)


def test_decor_stands_on_the_room_floor_lights_hang_from_the_level_ceiling_window_decor_stays_at_its_window():
    b = building()
    rug = {"id": "d1", "type": "rug", "room_id": "sunk", "level_id": "L1", "center": [2.0, 2.0], "size": [2.0, 1.4]}
    floor, out, _how = F.decor_floor(b, LEVEL, rug)
    assert floor == pytest.approx(2.70) and out is rug
    pendant = {"id": "d2", "type": "pendant_light", "room_id": "sunk", "level_id": "L1", "center": [2.0, 2.0, 1.9],
               "size": [0.4, 0.4, 0.8]}
    floor, out, _how = F.decor_floor(b, LEVEL, pendant)
    assert floor == pytest.approx(3.0) and out is pendant                        # 3.0 + 1.9 + 0.8 = the ceiling
    # a floor-length curtain: its rod stays at the window (5.30), its hem reaches the sunken floor (2.71)
    curtain = {"id": "d3", "type": "curtain", "room_id": "sunk", "level_id": "L1", "window_id": "o1",
               "center": [2.0, 0.2, 0.01], "size": [1.6, 0.08, 2.29]}
    floor, out, _how = F.decor_floor(b, LEVEL, curtain)
    assert floor == pytest.approx(2.70) and out["center"][2] == pytest.approx(0.01)
    assert out["size"][2] == pytest.approx(2.59) and floor + out["center"][2] + out["size"][2] == pytest.approx(5.30)
    assert curtain["size"][2] == 2.29                                            # the building's item is unchanged
    # a sill-length curtain and a blind keep their world height at the window
    for item in ({"id": "d4", "type": "curtain", "window_id": "o1", "center": [2.0, 0.2, 0.8],
                  "size": [1.6, 0.08, 1.5]},
                 {"id": "d5", "type": "blind", "window_id": "o1", "center": [2.0, 0.2, 1.4], "size": [1.2, 0.05, 0.9]}):
        item.update(room_id="sunk", level_id="L1")
        floor, out, _how = F.decor_floor(b, LEVEL, item)
        assert floor + out["center"][2] == pytest.approx(3.0 + item["center"][2])
        assert out["size"][2] == item["size"][2]
    # a raised room: the floor-length curtain is shortened to its floor
    raised = dict(curtain, room_id="raised", center=[2.0, 4.2, 0.01])
    floor, out, _how = F.decor_floor(b, LEVEL, raised)
    assert floor == pytest.approx(3.15) and out["size"][2] == pytest.approx(2.14)
    # a level floor room: nothing changes
    flat = dict(curtain, room_id="flat", center=[7.0, 0.2, 0.01])
    assert F.decor_floor(b, LEVEL, flat)[:2] == (3.0, flat)


def test_s5_floor_decor_rests_on_the_sunken_floor():
    rug = {"id": "d1", "type": "rug", "host_id": None, "room_id": "sunk", "level_id": "L1", "center": [2.0, 2.0],
           "size": [2.0, 1.4], "rotation_deg": 0.0}
    verts, faces = boxes_mesh([(-1.0, -0.7, 2.70, 1.0, 0.7, 2.712)], (2.0, 2.0))
    report = SC.measure_pure({"d1": {"verts": verts, "faces": faces}}, building(decor=[rug]))
    assert not [v for v in report["violations"] if v["check"] == "S5"]
    assert report["measured"]["d1"]["gap_m"] == pytest.approx(0.0, abs=1e-6)
    verts, faces = boxes_mesh([(-1.0, -0.7, 3.0, 1.0, 0.7, 3.012)], (2.0, 2.0))     # on the level's elevation
    report = SC.measure_pure({"d1": {"verts": verts, "faces": faces}}, building(decor=[rug]))
    (s5,) = [v for v in report["violations"] if v["check"] == "S5"]
    assert s5["metrics"]["gap_m"] == pytest.approx(0.30)


def test_wall_boxes_start_at_the_sunken_floor_as_the_shell_builds_them():
    boxes = {w["id"]: w for w in SC.wall_boxes(building(), "L1")}
    assert boxes["w_sunk"]["z0"] == pytest.approx(2.70) and boxes["w_sunk"]["z1"] == pytest.approx(5.70)
    assert boxes["w_flat"]["z0"] == pytest.approx(3.0)
    # a sofa pushed 5 cm into the wall, all of it below the level's floor (a low bench): S2 sees it
    bench = piece("b1", "bench", (2.5, 0.35), (1.2, 0.4))
    low = boxes_mesh([(-0.6, -0.2, 2.70, 0.6, 0.2, 2.98)], (2.5, 0.25))
    report = SC.measure_pure({"b1": {"verts": low[0], "faces": low[1]}}, building([bench]))
    assert [v for v in report["violations"] if v["check"] == "S2" and v["target"] == "b1"]


def test_a_throw_hangs_down_to_the_sunken_floor_not_the_level_floor():
    bench = piece("b1", "bench", (2.0, 2.0), (1.2, 0.4))
    floor = F.piece_floor_z(building([bench]), LEVEL, bench)
    verts, faces = boxes_mesh([(-0.6, -0.2, floor, 0.6, 0.2, floor + 0.25)], (2.0, 2.0))
    caster = R.MeshCaster(verts, faces)
    rect = (-0.6, -0.2, 0.6, 0.2 + 0.6)              # 0.6 m past the back edge: hangs down to the floor
    got = T.drape(caster, bench["footprint"], rect, floor)
    lowest = float(got["grid"][:, :, 2].min())
    assert floor + 0.02 - 1e-6 <= lowest < LEVEL["elevation"]
