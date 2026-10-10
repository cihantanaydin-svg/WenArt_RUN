"""Milestone 12 track S (docs/milestone12.md §4.6 D12, §4.7; contract §13.2): the scene checks S1-S6 on triangle meshes
(``scene_checks.measure_pure``, the pure-Python ray caster; the build runs the same ``measure`` with Blender's BVH):
S1 floor contact (-0.005 .. +0.010 m, the room's floor offset included), S2 no cut through walls or pieces
(<= 0.010 m; kitchen run members and wall-hung pieces excepted), S3 built front vs planned (<= 10 deg), S4 built size
vs the size table (+-15 %), S5 decor rests on its host (gap, penetration hard/soft, support share) or the floor,
S6 every built piece a usable library model or a by-design parametric type."""
from __future__ import annotations

import json

import pytest

from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import scene_checks as SC
from wenart.blender import textiles as T

from test_decor_rest import boxes_mesh

LIB = {"method": "library", "asset_id": "abo_x", "licence": "CC-BY-4.0", "library": "abo"}


def piece(pid, ftype, center, size, rot=0.0, room="r1", asset=None, **extra):
    return dict({"id": pid, "type": ftype, "level_id": "L0", "room_id": room, "status": "verified",
                 "source": "from_documents", "front_deg": (270.0 + rot) % 360.0,
                 "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
                 "asset": dict(asset or {"method": "parametric", "asset_id": f"parametric:{ftype}"})}, **extra)


def parametric_mesh(p, lift=0.0, base=0.0):
    fp = p["footprint"]
    h = P.proxy_height(p["type"], p.get("height"))[0]
    v, f, _k = P.world_mesh(P.build_parts(p["type"], *fp["size"], h, piece=p), fp["center"], fp["rotation_deg"],
                            base + lift)
    return {"verts": v, "faces": f}


def building(furniture, decor=()):
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "rooms": [{"id": "r1", "level_id": "L0"}, {"id": "r2", "level_id": "L0", "floor_offset_m": 0.15}],
            "walls": [{"id": "w1", "level_id": "L0", "start": [0.0, 0.0], "end": [8.0, 0.0], "thickness": 0.2,
                       "height": 2.7}],
            "furniture": list(furniture), "decor": list(decor)}


def checks_of(report, check):
    return [v for v in report["violations"] if v["check"] == check]


def test_contract_and_violation_format():
    assert SC.CHECKS == ("S1", "S2", "S3", "S4", "S5", "S6")
    sofa = piece("s1", "sofa", (2.0, 1.5), (2.0, 0.9), asset=LIB)
    report = SC.measure_pure({"s1": parametric_mesh(sofa, lift=0.03)}, building([sofa]))
    assert set(report) == {"violations", "counts", "measured"}
    (v,) = checks_of(report, "S1")
    assert set(v) == {"check", "severity", "target", "room_id", "message", "metrics"}
    assert v["target"] == "s1" and v["room_id"] == "r1" and v["severity"] == "major"
    assert report["counts"]["S1"] == {"checked": 1, "failed": 1} and report["counts"]["failed_build"] is False
    json.dumps(report)


@pytest.mark.parametrize("lift, ok", [(0.0, True), (0.008, True), (0.02, False), (-0.004, True), (-0.01, False)])
def test_s1_floor_contact(lift, ok):
    sofa = piece("s1", "sofa", (2.0, 1.5), (2.0, 0.9), asset=LIB)
    report = SC.measure_pure({"s1": parametric_mesh(sofa, lift=lift)}, building([sofa]))
    assert (not checks_of(report, "S1")) == ok
    assert report["measured"]["s1"]["floor_gap_m"] == pytest.approx(lift, abs=1e-6)


def test_s1_uses_the_room_floor_offset_and_skips_wall_hung_pieces():
    raised = piece("s2", "sofa", (2.0, 4.0), (2.0, 0.9), room="r2", asset=LIB)
    cabinet = piece("wc", "wall_cabinet", (5.0, 1.0), (1.2, 0.35), mount_bottom_m=1.45)
    meshes = {"s2": parametric_mesh(raised, base=0.15), "wc": parametric_mesh(cabinet, base=1.45)}
    report = SC.measure_pure(meshes, building([raised, cabinet]))
    assert not checks_of(report, "S1") and report["counts"]["S1"]["checked"] == 1
    sunk = SC.measure_pure({"s2": parametric_mesh(raised)}, building([raised]))      # on the level, 15 cm low
    assert checks_of(sunk, "S1")[0]["metrics"]["floor_gap_m"] == pytest.approx(-0.15)


def test_s2_walls_pieces_and_the_exceptions():
    through = piece("t1", "sideboard", (3.0, 0.2), (1.2, 0.45), asset=LIB)            # 0.125 m into wall w1
    clear = piece("t2", "sideboard", (5.5, 0.35), (1.2, 0.45), asset=LIB)              # its back on the wall face
    report = SC.measure_pure({"t1": parametric_mesh(through), "t2": parametric_mesh(clear)},
                             building([through, clear]))
    (v,) = checks_of(report, "S2")
    assert v["target"] == "t1" and v["metrics"]["wall_id"] == "w1" and v["metrics"]["depth_m"] > 0.05
    assert report["measured"]["t2"]["wall_depth_m"] <= 0.010
    a = piece("a", "armchair", (2.0, 3.0), (0.9, 0.9), asset=LIB)
    b = piece("b", "armchair", (2.7, 3.0), (0.9, 0.9), asset=LIB)                     # 0.2 m into each other
    c = piece("c", "armchair", (3.91, 3.0), (0.9, 0.9), asset=LIB)                    # 1 cm apart from b
    report = SC.measure_pure({k: parametric_mesh(p) for k, p in (("a", a), ("b", b), ("c", c))},
                             building([a, b, c]))
    cuts = checks_of(report, "S2")
    assert len(cuts) == 1 and cuts[0]["target"] == "a" and cuts[0]["metrics"]["other"] == "b"
    run = piece("k1", "kitchen_counter", (6.0, 3.0), (2.4, 0.6))
    sink = piece("k2", "sink_kitchen", (6.2, 3.0), (0.8, 0.6))                        # drawn inside its run
    report = SC.measure_pure({"k1": parametric_mesh(run), "k2": parametric_mesh(sink)}, building([run, sink]))
    assert not checks_of(report, "S2")


def test_s3_built_front_against_the_planned_one():
    sofa = piece("s1", "sofa", (2.0, 1.5), (2.0, 0.9), asset=LIB)
    mesh = parametric_mesh(sofa)
    assert not checks_of(SC.measure_pure({"s1": mesh}, building([sofa])), "S3")
    turned = dict(sofa, front_deg=0.0)                                   # planned facing +X, built facing -Y
    (v,) = checks_of(SC.measure_pure({"s1": mesh}, building([turned])), "S3")
    assert v["metrics"]["built_front_deg"] == pytest.approx(270.0) and "90 deg off" in v["message"]
    assert not checks_of(SC.measure_pure({"s1": dict(mesh, front_deg=5.0)}, building([turned])), "S3")
    no_front = dict(sofa, front_deg=None)
    assert SC.measure_pure({"s1": mesh}, building([no_front]))["counts"]["S3"]["checked"] == 0


def test_s4_built_size_against_the_size_table():
    sofa = piece("s1", "sofa", (2.0, 1.5), (2.2, 0.9), asset=LIB)
    long = piece("s2", "sofa", (2.0, 4.5), (3.8, 0.9), asset=LIB)                     # 3.8 m > 3.0 m x 1.15
    report = SC.measure_pure({"s1": parametric_mesh(sofa), "s2": parametric_mesh(long)}, building([sofa, long]))
    (v,) = checks_of(report, "S4")
    assert v["target"] == "s2" and "width 3.80 m outside 1.20-3.00 m" in v["message"]
    assert report["measured"]["s1"]["built_size_m"][:2] == pytest.approx([2.2, 0.9], abs=0.01)
    counter = piece("k1", "kitchen_counter", (6.0, 3.0), (6.0, 0.6))                  # by design: sized to the drawing
    assert not checks_of(SC.measure_pure({"k1": parametric_mesh(counter)}, building([counter])), "S4")


def test_s6_audited_models_or_by_design_parametric_only():
    rows = [piece("s1", "sofa", (2.0, 2.0), (2.0, 0.9), asset=LIB),
            piece("s2", "sofa", (2.0, 4.0), (2.0, 0.9)),                                 # a parametric sofa
            piece("s3", "sofa", (2.0, 6.0), (2.0, 0.9), asset=dict(LIB, licence="CC-BY-NC-4.0",
                                                                    licence_flag="non_commercial")),
            piece("s4", "sofa", (6.0, 2.0), (2.0, 0.9), asset=dict(LIB, audit={"status": "removed"})),
            piece("k1", "kitchen_counter", (6.0, 4.0), (2.4, 0.6)),
            piece("w1", "washing_machine", (6.0, 6.0), (0.6, 0.6)),
            piece("u1", "unknown", (9.0, 2.0), (0.8, 0.8))]
    meshes = {p["id"]: {"verts": boxes_mesh([(-0.4, -0.4, 0.0, 0.4, 0.4, 0.8)], p["footprint"]["center"])[0],
                        "faces": boxes_mesh([(-0.4, -0.4, 0.0, 0.4, 0.4, 0.8)])[1]} for p in rows}
    report = SC.measure_pure(meshes, building(rows))
    failed = {v["target"] for v in checks_of(report, "S6")}
    assert failed == {"s2", "s3", "s4", "u1"} and report["counts"]["S6"] == {"checked": 7, "failed": 4}
    assert report["measured"]["k1"]["s6"] == "ok" and report["measured"]["w1"]["s6"] == "ok"


def sofa_scene():
    sofa = piece("s1", "sofa", (3.0, 3.0), (2.0, 0.9), rot=30.0, asset=LIB)
    mesh = parametric_mesh(sofa)
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    item = {"id": "dec_1", "type": "cushion", "host_id": "s1", "room_id": "r1", "level_id": "L0",
            "center": list(R.to_world((3.0, 3.0), 30.0, -0.5, 0.45 - 0.075 - 0.1)), "rotation_deg": 30.0,
            "size": [0.45, 0.15, 0.45],
            "host_frame": {"support": "back", "lean_deg": 12.0}}
    plan = R.plan_decor(item, sofa, R.MeshCaster(mesh["verts"], mesh["faces"]), cushion["verts"], cushion["faces"],
                        "back", lean_deg=12.0)
    return sofa, mesh, item, plan, cushion


def test_s5_decor_rests_on_its_host_and_the_floor():
    sofa, mesh, item, plan, cushion = sofa_scene()
    rug = {"id": "dec_2", "type": "rug", "host_id": None, "room_id": "r2", "level_id": "L0", "center": [3.0, 1.5],
           "size": [2.0, 1.4], "rotation_deg": 0.0}
    curtain = {"id": "dec_3", "type": "curtain", "host_id": None, "room_id": "r1", "level_id": "L0",
               "center": [1.0, 0.2, 0.01], "size": [1.4, 0.08, 2.4], "rotation_deg": 0.0}
    rug_mesh = {"verts": boxes_mesh([(-1.0, -0.7, 0.15, 1.0, 0.7, 0.162)], (3.0, 1.5))[0],
                "faces": boxes_mesh([(-1.0, -0.7, 0.0, 1.0, 0.7, 0.012)])[1]}
    meshes = {"s1": mesh, "dec_1": {"verts": plan["verts"], "faces": plan["faces"], "rest_footprint": plan["footprint"]},
              "dec_2": rug_mesh, "dec_3": {"verts": [(0, 0, 0), (1, 0, 0), (0, 0, 1)], "faces": [[0, 1, 2]]}}
    report = SC.measure_pure(meshes, building([sofa], [item, rug, curtain]))
    assert not checks_of(report, "S5") and report["counts"]["S5"] == {"checked": 2, "failed": 0}
    assert report["measured"]["dec_1"]["s5"] == "ok" and report["measured"]["dec_2"]["gap_m"] == pytest.approx(0.0)
    assert report["measured"]["dec_3"]["s5"].startswith("not measured")
    # Milestone 11's cushion: the type height and the drawn offset -> a critical violation, the build fails
    old = R.pose_vertices(cushion["verts"], {"center": item["center"], "z": 0.45, "rotation_deg": 30.0})
    meshes["dec_1"] = {"verts": old, "faces": cushion["faces"]}
    meshes["dec_2"] = dict(rug_mesh, verts=[(x, y, z + 0.03) for x, y, z in rug_mesh["verts"]])
    report = SC.measure_pure(meshes, building([sofa], [item, rug, curtain]))
    bad = {v["target"]: v for v in checks_of(report, "S5")}
    assert set(bad) == {"dec_1", "dec_2"} and bad["dec_1"]["severity"] == "critical"
    assert "penetration" in bad["dec_1"]["message"] and bad["dec_2"]["metrics"]["gap_m"] == pytest.approx(0.03)
    assert report["counts"]["failed_build"] is True


def test_s5_measures_on_the_host_and_its_dressing():
    bed = piece("b1", "bed_double", (2.0, 2.0), (1.6, 2.0), asset=LIB)
    frame = {"verts": boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 0.94, 0.30), (-0.8, 0.94, 0.0, 0.8, 1.0, 1.1)], (2.0, 2.0))[0],
             "faces": boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 0.94, 0.30), (-0.8, 0.94, 0.0, 0.8, 1.0, 1.1)])[1]}
    mattress = {"verts": boxes_mesh([(-0.78, -0.98, 0.30, 0.78, 0.92, 0.55)], (2.0, 2.0))[0],
                "faces": boxes_mesh([(-0.78, -0.98, 0.30, 0.78, 0.92, 0.55)])[1]}
    v, f, _k = P.world_mesh(P.decor_parts("vase", 0.18, 0.18, 0.4), (2.0, 1.5), 0.0, 0.55)
    item = {"id": "dec_9", "type": "vase", "host_id": "b1", "room_id": "r1", "level_id": "L0", "center": [2.0, 1.5],
            "size": [0.18, 0.18, 0.4], "rotation_deg": 0.0}
    meshes = {"b1": frame, "b1#dressing": mattress, "dec_9": {"verts": v, "faces": f}}
    report = SC.measure_pure(meshes, building([bed], [item]))
    assert report["measured"]["dec_9"]["s5"] == "ok"                      # on the mattress the build dressed it with
    del meshes["b1#dressing"]
    assert checks_of(SC.measure_pure(meshes, building([bed], [item])), "S5")


def test_write_report(tmp_path):
    out = tmp_path / "checks" / "scene_L0.json"
    SC.write_report({"violations": [], "counts": {}, "measured": {}}, out)
    assert json.loads(out.read_text(encoding="utf-8")) == {"counts": {}, "measured": {}, "violations": []}
    merged = SC.merge_meshes([{"verts": [(0, 0, 0)], "faces": [[0]], "front_deg": 5.0},
                              {"verts": [(1, 0, 0)], "faces": [[0]], "method": "library"}])
    assert merged["faces"] == [[0], [1]] and merged["front_deg"] == 5.0 and merged["method"] == "library"
