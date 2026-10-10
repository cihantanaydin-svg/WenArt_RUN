"""Milestone 12 track S (docs/milestone12.md §4.7 D13, §6.4, B7): decor rests on the built host mesh. Pure-Python ray
casts (``wenart.blender.rest``, the same code the scene builder runs on Blender's BVH) on hand-made host meshes: a
cushion against the real (reclined) back of a sofa model at its real seat height, off the arms; pillows on the
mattress against the headboard; books on a shelf board; vases on a top; throws and duvets draped on the host (our
procedural cloth, ``wenart.blender.textiles``); check S5 and the re-placement; the Milestone 11 placement (type
height, drawn footprint) fails the same check."""
from __future__ import annotations

import math
from collections import Counter

import pytest

from wenart.blender import geom2d, rest as R, textiles as T
from wenart.blender import parametric as P


def boxes_mesh(boxes, center=(0.0, 0.0), rot=0.0):
    """World mesh of local boxes ``(x0, y0, z0, x1, y1, z1)`` (host frame) placed at ``center`` turned by ``rot``."""
    verts, faces = [], []
    for x0, y0, z0, x1, y1, z1 in boxes:
        v, f = geom2d.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), 0.0)
        off = len(verts)
        verts += [(*R.to_world(center, rot, p[0], p[1]), p[2]) for p in v]
        faces += [[i + off for i in face] for face in f]
    return verts, faces


def prism_mesh(profile_yz, x0, x1, center=(0.0, 0.0), rot=0.0):
    """A convex prism along X of a (y, z) profile (counter-clockwise seen from +X), placed like ``boxes_mesh``."""
    n = len(profile_yz)
    local = [(x0, y, z) for y, z in profile_yz] + [(x1, y, z) for y, z in profile_yz]
    verts = [(*R.to_world(center, rot, x, y), z) for x, y, z in local]
    faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    return verts, faces


def merge(*meshes):
    verts, faces = [], []
    for v, f in meshes:
        off = len(verts)
        verts += list(v)
        faces += [[i + off for i in face] for face in f]
    return verts, faces


SOFA_FP = {"center": [3.0, 4.0], "size": [2.0, 0.95], "rotation_deg": 30.0}


def sofa_model():
    """A sofa model as a library one is built: a 0.48 m seat (not the 0.45 m type table), a back reclined from
    y = 0.20 at the seat to y = 0.32 at 0.90 m, 0.2 m arms up to 0.65 m."""
    c, r = SOFA_FP["center"], SOFA_FP["rotation_deg"]
    base = boxes_mesh([(-0.8, -0.475, 0.0, 0.8, 0.475, 0.30), (-0.8, -0.475, 0.30, 0.8, 0.20, 0.48),
                       (-1.0, -0.475, 0.0, -0.8, 0.475, 0.65), (0.8, -0.475, 0.0, 1.0, 0.475, 0.65)], c, r)
    back = prism_mesh([(0.20, 0.30), (0.475, 0.30), (0.475, 0.90), (0.32, 0.90)], -0.8, 0.8, c, r)
    return merge(base, back)


def piece(ftype, fp, pid="h1"):
    return {"id": pid, "type": ftype, "footprint": fp}


def old_cushion_center(fp, x):
    """Milestone 11: the cushion at y = d/2 - 0.075 - 0.1 of the drawn footprint."""
    return R.to_world(fp["center"], fp["rotation_deg"], x, fp["size"][1] / 2.0 - 0.075 - 0.1)


def test_cushion_rests_on_the_real_seat_against_the_real_back():
    verts, faces = sofa_model()
    caster = R.MeshCaster(verts, faces)
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    for x in (-0.5, 0.5):
        item = {"id": "c", "type": "cushion", "center": list(old_cushion_center(SOFA_FP, x)), "rotation_deg": 30.0}
        plan = R.plan_decor(item, piece("sofa", SOFA_FP), caster, cushion["verts"], cushion["faces"], "back",
                            lean_deg=12.0)
        assert "not_rested" not in plan, plan
        m = plan["rest"]
        assert m["gap_m"] <= 0.010 and m["penetration_m"] <= 0.030 and m["support_share"] >= 0.8
        pose = plan["pose"]
        assert pose["z"] == pytest.approx(0.48, abs=1e-3) and pose["lean_deg"] == 12.0      # the model's seat
        assert "backrest found" in pose["how"]
        low = min(v[2] for v in plan["verts"])
        assert low == pytest.approx(0.48, abs=2e-3)
        # its back touches the reclined back (within 2 cm) at the probe heights, never deeper than the soft limit
        local = [R.to_local(SOFA_FP["center"], 30.0, v[0], v[1]) + (v[2],) for v in plan["verts"]]
        for z in (0.55, 0.7):
            front_of_back = 0.20 + (z - 0.30) / 0.60 * 0.12 if z > 0.30 else 0.20
            near = [y for _x, y, zz in local if abs(zz - z) < 0.03]
            assert max(near) <= front_of_back + 0.03 and max(near) >= front_of_back - 0.06


def test_the_milestone_11_cushion_fails_the_same_check():
    """§1.3: a type height of 0.45 m and the drawn footprint's offset: inside the back and in the seat."""
    verts, faces = sofa_model()
    caster = R.MeshCaster(verts, faces)
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    c = old_cushion_center(SOFA_FP, -0.5)
    pose = {"center": list(c), "z": 0.45, "rotation_deg": 30.0, "lean_deg": 0.0}
    world = R.pose_vertices(cushion["verts"], pose)
    m = R.measure_rest(world, cushion["faces"], caster, {"center": list(c), "size": [0.45, 0.15],
                                                         "rotation_deg": 30.0}, True)
    ok, why = R.rest_ok(m)
    assert not ok and m["penetration_m"] > 0.03, m


def test_cushions_keep_off_the_arms_and_narrow_or_give_up():
    verts, faces = sofa_model()
    caster = R.MeshCaster(verts, faces)
    near_arm = R.to_world(SOFA_FP["center"], 30.0, 0.75, 0.2)            # planned against the right arm
    pose = R.place_leaning(caster, SOFA_FP, near_arm, (0.45, 0.15, 0.45))
    lx, _ = R.to_local(SOFA_FP["center"], 30.0, *pose["center"])
    assert lx + 0.45 / 2 <= 0.8 + 1e-6 and "shifted off the arm" in pose["how"]
    narrow = {"center": [0.0, 0.0], "size": [0.8, 0.95], "rotation_deg": 0.0}      # an armchair: 0.4 m between arms
    v, f = boxes_mesh([(-0.2, -0.475, 0.0, 0.2, 0.2, 0.45), (-0.2, 0.2, 0.0, 0.2, 0.475, 0.9),
                       (-0.4, -0.475, 0.0, -0.2, 0.475, 0.65), (0.2, -0.475, 0.0, 0.4, 0.475, 0.65)])
    pose = R.place_leaning(R.MeshCaster(v, f), narrow, (0.0, 0.1), (0.45, 0.15, 0.45))
    assert pose["size"][0] == pytest.approx(0.4 - 2 * R.ARM_GAP_M, abs=1e-3) and "narrowed" in pose["how"]
    v, f = boxes_mesh([(-0.1, -0.475, 0.0, 0.1, 0.2, 0.45), (-0.1, 0.2, 0.0, 0.1, 0.475, 0.9),
                       (-0.3, -0.475, 0.0, -0.1, 0.475, 0.65), (0.1, -0.475, 0.0, 0.3, 0.475, 0.65)])
    assert R.place_leaning(R.MeshCaster(v, f), narrow, (0.0, 0.1), (0.45, 0.15, 0.45)) is None    # 0.2 m: no room


BED_FP = {"center": [1.0, 1.5], "size": [1.6, 2.0], "rotation_deg": 90.0}


def bare_bed(mattress_top=0.58):
    """A mattress model (§1.3: the library beds chosen were bare mattresses): frame, mattress, headboard at +Y."""
    return boxes_mesh([(-0.8, -1.0, 0.0, 0.8, 0.94, 0.30), (-0.78, -0.98, 0.30, 0.78, 0.92, mattress_top),
                       (-0.8, 0.94, 0.0, 0.8, 1.0, 1.10)], BED_FP["center"], BED_FP["rotation_deg"])


@pytest.mark.parametrize("top", [0.45, 0.62, 0.75])
def test_bed_cushions_rest_on_the_mattress_whatever_its_height(top):
    """§1.3: every cushion on a library bed sat at 0.55 m whatever the mattress (0.71-1.46 m beds)."""
    v, f = bare_bed(top)
    caster = R.MeshCaster(v, f)
    cushion = T.cushion_mesh(0.5, 0.15, 0.5)
    item = {"id": "p", "type": "cushion", "rotation_deg": 90.0,
            "center": list(R.to_world(BED_FP["center"], 90.0, -0.4, 1.0 - 0.175))}
    plan = R.plan_decor(item, piece("bed_double", BED_FP), caster, cushion["verts"], cushion["faces"], "headboard",
                        lean_deg=12.0)
    assert "not_rested" not in plan
    assert plan["pose"]["z"] == pytest.approx(top, abs=1e-3) and plan["rest"]["gap_m"] <= 0.010
    old = {"center": item["center"], "z": 0.55, "rotation_deg": 90.0, "lean_deg": 0.0}
    m = R.measure_rest(R.pose_vertices(cushion["verts"], old), cushion["faces"], caster,
                       {"center": item["center"], "size": [0.5, 0.15], "rotation_deg": 90.0}, True)
    assert not R.rest_ok(m)[0]                                       # floats or sinks at the type height


def test_bare_bed_gets_a_duvet_and_pillows_draped_on_it():
    v, f = bare_bed(0.58)
    caster = R.MeshCaster(v, f)
    got = T.duvet_and_pillows(caster, BED_FP, 0.0)
    roles = Counter(p["role"] for p in got["parts"])
    assert roles == {"pillow": 2, "duvet": 1, "turndown": 1} and got["record"]["pillows"] == 2
    for p, pose in zip([q for q in got["parts"] if q["role"] == "pillow"], got["pillows"]):
        m = R.measure_rest(p["verts"], p["faces"], caster, {"center": pose["center"], "size": [pose["size"][0], 0.15],
                                                            "rotation_deg": pose["rotation_deg"]}, True)
        assert R.rest_ok(m)[0], m
        head = max(R.to_local(BED_FP["center"], 90.0, x, y)[1] for x, y, _z in p["verts"])
        assert 0.94 - 0.03 <= head <= 0.94 + 0.005                    # against the headboard
    duvet = next(p for p in got["parts"] if p["role"] == "duvet")
    zs = [z for _x, _y, z in duvet["verts"]]
    assert min(zs) < 0.58 - 0.15 and max(zs) <= 0.58 + T.CLOTH_OFFSET_M + T.DUVET_THICKNESS_M + 0.008
    assert R.penetration(caster, duvet["verts"]) <= 0.010              # hangs outside the frame, never through it
    assert got["record"]["on_top_share"] > 0.4
    # a single bed narrower than 1.3 m takes one pillow (two do not fit side by side)
    single = {"center": [0.0, 0.0], "size": [0.9, 2.0], "rotation_deg": 0.0}
    sv, sf = boxes_mesh([(-0.45, -1.0, 0.0, 0.45, 0.94, 0.5), (-0.45, 0.94, 0.0, 0.45, 1.0, 1.0)])
    assert T.duvet_and_pillows(R.MeshCaster(sv, sf), single, 0.0)["record"]["pillows"] == 1


def test_throw_is_draped_across_the_bed_foot_and_hangs_over_its_edge():
    v, f = bare_bed(0.58)
    caster = R.MeshCaster(v, f)
    item = {"id": "t", "type": "throw", "size": [1.52, 0.5, 0.05],
            "center": list(R.to_world(BED_FP["center"], 90.0, 0.0, -1.0 + 0.25 - 0.1))}   # 0.1 m past the foot
    plan = R.plan_throw(item, piece("bed_double", BED_FP), caster, 0.0)
    assert "not_rested" not in plan and plan["rest"]["gap_m"] <= 0.010
    zs = [p[2] for p in plan["verts"]]
    assert max(zs) < 0.58 + 0.03 and min(zs) < 0.58 - 0.05               # lies on top, falls over the foot
    assert R.penetration(caster, plan["verts"]) <= 0.010


def test_throw_on_a_sofa_seat_end_is_never_a_squashed_model():
    verts, faces = sofa_model()
    caster = R.MeshCaster(verts, faces)
    item = {"id": "t", "type": "throw", "size": [0.5, 0.45, 0.05],
            "center": list(R.to_world(SOFA_FP["center"], 30.0, -0.5, -0.1))}
    plan = R.plan_throw(item, piece("sofa", SOFA_FP), caster, 0.0)
    assert "not_rested" not in plan
    zs = [p[2] for p in plan["verts"]]
    assert min(zs) >= 0.48 - 1e-6 - 0.002 and max(zs) - min(zs) < 0.05           # a thin cloth on the seat


def shelf_mesh():
    """A bookshelf 0.8 x 0.3 x 1.8 m: two sides, a back, boards at 0, 0.35, 0.70, 1.05, 1.40, 1.78 m (2 cm)."""
    boards = [(-0.38, -0.15, z, 0.38, 0.15, z + 0.02) for z in (0.0, 0.35, 0.70, 1.05, 1.40, 1.78)]
    return boxes_mesh(boards + [(-0.4, -0.15, 0.0, -0.38, 0.15, 1.8), (0.38, -0.15, 0.0, 0.4, 0.15, 1.8),
                                (-0.38, 0.13, 0.0, 0.38, 0.15, 1.8)], (5.0, 5.0), 0.0)


def test_books_take_a_shelf_board_with_room_for_them():
    caster = R.MeshCaster(*shelf_mesh())
    boards = R.board_tops(caster, 5.0, 5.0)
    assert [round(b["z"], 3) for b in boards] == [0.02, 0.37, 0.72, 1.07, 1.42, 1.8]
    assert boards[1]["clearance"] == pytest.approx(0.33, abs=1e-6)
    pose = R.place_on_shelf(caster, (5.0, 5.0), (0.3, 0.2, 0.22), 0.0, shelf=1)
    assert pose["z"] == pytest.approx(0.37) and pose["shelf"] == 1
    assert R.place_on_shelf(caster, (5.0, 5.0), (0.3, 0.2, 0.22), 0.0, shelf=1, attempt=1)["z"] == pytest.approx(0.72)
    assert R.place_on_shelf(caster, (5.0, 5.0), (0.3, 0.2, 0.22), 0.0, shelf=9)["shelf"] == 5     # the top
    assert R.place_on_shelf(caster, (5.0, 5.0), (0.3, 0.2, 0.40), 0.0, shelf=1)["z"] == pytest.approx(1.8)


def test_tabletop_items_take_the_highest_hit_and_move_in_from_the_edge():
    table = boxes_mesh([(-0.5, -0.3, 0.70, 0.5, 0.3, 0.74)] + [(sx * 0.45 - 0.02, sy * 0.25 - 0.02, 0.0,
                                                                  sx * 0.45 + 0.02, sy * 0.25 + 0.02, 0.70)
                                                                 for sx in (-1, 1) for sy in (-1, 1)])
    caster = R.MeshCaster(*table)
    pose = R.place_on_top(caster, (0.1, 0.0), (0.18, 0.18, 0.4), 0.0, False, host_center=(0.0, 0.0))
    assert pose["z"] == pytest.approx(0.74) and pose["share"] == 1.0
    edge = R.place_on_top(caster, (0.48, 0.0), (0.18, 0.18, 0.4), 0.0, False, host_center=(0.0, 0.0))
    assert edge["center"][0] < 0.48 and "moved" in edge["how"]
    assert R.place_on_top(caster, (3.0, 3.0), (0.18, 0.18, 0.4), 0.0, False, host_center=(3.0, 3.0)) is None


def test_s5_tolerances_hard_and_soft_hosts():
    table = R.MeshCaster(*boxes_mesh([(-0.5, -0.3, 0.0, 0.5, 0.3, 0.74)]))
    vase = P.decor_parts("vase", 0.18, 0.18, 0.4)
    v, f, _k = P.world_mesh(vase, (0.0, 0.0), 0.0, 0.0)
    foot = {"center": [0.0, 0.0], "size": [0.18, 0.18], "rotation_deg": 0.0}

    def at(z):
        return [(x, y, zz + z) for x, y, zz in v]

    assert R.rest_ok(R.measure_rest(at(0.74), f, table, foot, False))[0]
    assert R.rest_ok(R.measure_rest(at(0.748), f, table, foot, False))[0]              # 8 mm gap: within 1 cm
    floating = R.measure_rest(at(0.76), f, table, foot, False)
    assert not R.rest_ok(floating)[0] and floating["gap_m"] == pytest.approx(0.02, abs=1e-3)
    sunk = R.measure_rest(at(0.72), f, table, foot, False)                              # 2 cm into a hard top
    assert not R.rest_ok(sunk)[0] and sunk["penetration_m"] == pytest.approx(0.02, abs=2e-3)
    assert R.rest_ok(R.measure_rest(at(0.72), f, table, foot, True))[0]                # a soft mattress gives 3 cm
    off = R.measure_rest([(x + 0.55, y, z) for x, y, z in at(0.74)], f, table,
                         {"center": [0.55, 0.0], "size": [0.18, 0.18], "rotation_deg": 0.0}, False)
    assert not R.rest_ok(off)[0] and off["support_share"] < 0.8                        # half off the table


def test_an_item_that_cannot_rest_is_placed_once_more_then_not_built():
    frame = R.MeshCaster(*boxes_mesh([(-0.5, -0.3, 0.70, -0.45, 0.3, 0.74), (0.45, -0.3, 0.70, 0.5, 0.3, 0.74)]))
    v, f, _k = P.world_mesh(P.decor_parts("vase", 0.18, 0.18, 0.4), (0.0, 0.0), 0.0, 0.0)
    host = {"id": "t1", "type": "table_coffee", "footprint": {"center": [0.0, 0.0], "size": [1.0, 0.6],
                                                              "rotation_deg": 0.0}}
    plan = R.plan_decor({"id": "dec_1", "type": "vase", "center": [0.0, 0.0], "rotation_deg": 0.0}, host, frame,
                        v, f, "top")
    nr = plan["not_rested"]
    assert nr["id"] == "dec_1" and nr["host_id"] == "t1" and nr["attempts"] == 2 and "no top" in nr["reason"]


def test_textile_meshes_are_closed_and_inside_their_boxes():
    def closed(part):
        edges = Counter()
        for face in part["faces"]:
            for i in range(len(face)):
                a, b = face[i], face[(i + 1) % len(face)]
                edges[(min(a, b), max(a, b))] += 1
        return all(n == 2 for n in edges.values())

    for part, box in ((T.cushion_mesh(0.45, 0.15, 0.45), (0.45, 0.15, 0.45)),
                      (T.lying_cushion_mesh(0.4, 0.4, 0.12), (0.4, 0.4, 0.12)),
                      (T.flat_cloth(1.2, 0.6, 0.02), (1.2, 0.6, 0.02))):
        x0, y0, z0, x1, y1, z1 = P.parts_bbox([part])
        assert closed(part) and z0 == pytest.approx(0.0)
        assert x1 - x0 <= box[0] + 1e-9 and y1 - y0 <= box[1] + 1e-9 and z1 - z0 <= box[2] + 1e-9
    cushion = T.cushion_mesh(0.45, 0.15, 0.45)
    assert max(v[1] for v in cushion["verts"]) == pytest.approx(0.075, abs=0.005)     # bulging to its thickness
    curtain = T.curtain_parts(2.0, 0.08, 2.4)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(curtain)
    assert x1 - x0 <= 2.0 + 1e-9 and y1 - y0 <= 0.08 + 1e-9 and z1 <= 2.4 + 1e-9
    panels = [p for p in curtain if p["role"] == "panel"]
    assert len(panels) == 2 and all(max(v[1] for v in p["verts"]) - min(v[1] for v in p["verts"]) > 0.02
                                    for p in panels)                                  # pleated, not boxes
    roller = {p["role"] for p in T.blind_parts(1.2, 0.06, 1.0)}
    slats = [p for p in T.blind_parts(1.2, 0.06, 1.0, kind="slats") if p["role"] == "slat"]
    assert roller == {"roller", "panel", "bar"} and len(slats) >= 15
    assert P.decor_parts("blind", 1.2, 0.06, 1.0, {"blind_kind": "slats"})[1]["role"] == "slat"


@pytest.mark.parametrize("project", ["real02", "real03"])
def test_committed_parametric_hosts_before_and_after(project):
    """§1.3 measured on the committed results: cushions on the parametric corner sofa / sofa 50-64 % inside the
    backrest, cushions on parametric beds on the pillow top. The same items placed by rays rest (S5)."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "results" / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip("no committed building")
    b = json.loads(path.read_text(encoding="utf-8"))
    pieces = {p["id"]: p for p in b["furniture"]}
    before_fail = after_ok = n = 0
    for item in b.get("decor") or []:
        host = pieces.get(item.get("host_id"))
        if item.get("type") != "cushion" or host is None or (host.get("asset") or {}).get("method") != "parametric" \
                or host["type"] not in ("sofa", "sofa_corner", "armchair", "bed_double", "bed_single"):
            continue
        fp = host["footprint"]
        h = P.proxy_height(host["type"], host.get("height"))[0]
        v, f, _k = P.world_mesh(P.build_parts(host["type"], *fp["size"], h, piece=host), fp["center"],
                                fp["rotation_deg"], 0.0)
        caster = R.MeshCaster(v, f)
        size = list(item["size"]) if len(item["size"]) > 2 else [item["size"][0], 0.15, item["size"][0]]
        mesh = T.cushion_mesh(*size)
        support = "headboard" if host["type"].startswith("bed") else "back"
        # Milestone 11: the type table (sofa seat, parametric bed: the bedding top) at the drawn footprint's offset
        old_z = P.bedding_top(fp["size"][0], fp["size"][1], h) if support == "headboard" else P.sofa_seat_height(h)
        old = R.pose_vertices(mesh["verts"], {"center": item["center"], "z": old_z,
                                              "rotation_deg": item.get("rotation_deg") or 0.0, "lean_deg": 0.0})
        m = R.measure_rest(old, mesh["faces"], caster, {"center": item["center"], "size": size[:2],
                                                        "rotation_deg": item.get("rotation_deg") or 0.0}, True)
        before_fail += not R.rest_ok(m)[0]
        plan = R.plan_decor(item, host, caster, mesh["verts"], mesh["faces"], support, lean_deg=12.0)
        after_ok += "not_rested" not in plan
        n += 1
    if n == 0:
        pytest.skip("no cushion on a parametric seat or bed")
    assert before_fail >= 0.5 * n and after_ok == n, (n, before_fail, after_ok)
