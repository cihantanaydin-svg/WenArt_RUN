"""The walls of the attic after their opening booleans (pod F2, synthetic-07: tests/gpu/test_render.py
``test_passes_exist_and_depth_is_plausible`` failed on ``cam_r_L1_hol_3``, which looked out through a missing wall).

synthetic-07's L1 east wall ``w_L1_006`` runs under the roof terrace ``ro_001`` (a 1.00 m parapet, s 0-3.75) and
then up to the gable under the roof (6.80 m at the ridge); it is built from ``shell.wall_pieces`` (two closed pieces
that touch at s 3.75) and the window ``win_L1_002`` is cut out of it. The exact solver returned that mesh empty
(parapet, gable and window lost) and nothing said so. Now the boolean runs with ``use_self`` on a wall built from
pieces, and ``shell.wall_cut_problems`` (pure) compares every cut wall with the solid it came from: no faces left,
more volume lost than the cutters hold, or an extent lost where no cutter reaches stops the build
(``shell.WallLost``) with the wall id; the manifest records ``after_cuts`` (faces, z range).

CPU: the guard on synthetic-07's east wall (empty -> error, lost parapet piece -> error, the window cut -> ok) and on
a turned plain wall; the parapet piece keeps its top above a lower roof underside (the M10 example's ``w_L1_001``:
the roof-clipped box would lower it). Blender (``WENART_BLENDER``): synthetic-07's attic built, ``w_L1_006`` stands
with its parapet at 4.00 m, its gable at 6.80 m and the window hole."""
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart import views as V
from wenart.blender import build as B
from wenart.blender import cli, geom2d, shell
from wenart.blender import roof as R

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                                           "/workspace/tools/blender, /opt/wenart/blender, PATH)")
EV = [{"file": "sheet.dxf", "page": 1, "method": "vector", "confidence": 1.0}]
GABLE_TOP = 7.106 - 0.25 / math.cos(math.radians(35.0))       # the roof underside at the ridge: 6.8008


def _v(value, method="vector"):
    return {"value": value, "method": method, "confidence": 1.0 if method != "assumed" else 0.0, "evidence": []}


def _attic07() -> dict:
    """synthetic-07's attic L1 as the F2 run read it (runs/20261009-092258-full building_final.json): six walls, the
    hall, the play room and the roof terrace, two doors, two windows, the gable roof (eaves 3.955, ridge 7.106 at
    y 4.0, 35 degrees) with the terrace opening ``ro_001`` whose parapet runs on the south and east walls."""
    def wall(wid, start, end, thickness, exterior):
        return {"id": wid, "level_id": "L1", "start": start, "end": end, "thickness": thickness, "height": 3.801,
                "exterior": exterior, "status": "verified", "evidence": EV}

    def room(rid, label, room_type, polygon):
        return {"id": rid, "level_id": "L1", "label": label, "room_type": room_type, "polygon": polygon,
                "area_computed": round(abs(G.polygon_signed_area(polygon)), 2), "status": "verified", "evidence": EV}

    def opening(oid, kind, wall_id, center, width, height, sill, **extra):
        return {"id": oid, "type": kind, "level_id": "L1", "wall_id": wall_id, "center": center, "width": width,
                "height": height, "sill_height": sill, "status": "verified", "evidence": EV, **extra}

    return {"schema_version": "0.1", "status": "ok", "project": {"id": "s07-attic", "brief": {}}, "documents": [],
            "levels": [{"id": "L1", "label": "Cati Kati", "order": 1, "elevation": 3.0, "ceiling_height": 3.801,
                        "kind": "attic", "evidence": EV}],
            "walls": [wall("w_L1_001", [0.0, 0.125], [10.0, 0.125], 0.25, True),
                      wall("w_L1_002", [6.15, 4.0], [9.75, 4.0], 0.1, False),
                      wall("w_L1_003", [0.0, 7.875], [10.0, 7.875], 0.25, True),
                      wall("w_L1_004", [0.125, 0.25], [0.125, 7.75], 0.25, True),
                      wall("w_L1_005", [6.1, 0.25], [6.1, 7.75], 0.1, False),
                      wall("w_L1_006", [9.875, 0.25], [9.875, 7.75], 0.25, True)],
            "openings": [opening("d_L1_001", "door", "w_L1_002", [7.6, 4.0], 0.8, 2.1, None, swing_side="r_L1_teras",
                                 operation="swing"),
                         opening("win_L1_001", "window", "w_L1_004", [0.125, 4.0], 1.2, 1.2, 0.9),
                         opening("d_L1_002", "door", "w_L1_005", [6.1, 6.0], 0.9, 2.1, None,
                                 swing_side="r_L1_oyun_odasi", operation="swing"),
                         opening("win_L1_002", "window", "w_L1_006", [9.875, 6.0], 0.6, 1.2, 0.9)],
            "rooms": [room("r_L1_oyun_odasi", "Oyun Odasi", "other",
                           [[0.25, 0.25], [6.05, 0.25], [6.05, 7.75], [0.25, 7.75]]),
                      room("r_L1_teras", "Teras", "balcony", [[6.15, 0.25], [9.75, 0.25], [9.75, 3.95], [6.15, 3.95]]),
                      room("r_L1_hol", "Hol", "hall", [[6.15, 4.05], [9.75, 4.05], [9.75, 7.75], [6.15, 7.75]])],
            "furniture": [], "decor": [], "conflicts": [], "unverified": [], "warnings": [],
            "roof": {"type": "gable", "type_source": "section", "over_level_id": "L1",
                     "eaves_height": _v(3.955), "ridge_height": _v(7.106), "pitches_deg": [_v(35.0)],
                     "overhang": _v(0.5), "thickness": _v(0.25),
                     "profile": {"cut_axis": "y", "points": [[-0.5, 3.955], [4.0, 7.106], [8.5, 3.955]],
                                 "method": "vector"},
                     "outline": [[-0.5, -0.5], [10.5, -0.5], [10.5, 8.5], [-0.5, 8.5]], "break_line": None,
                     "ridge_lines": [[[-0.5, 4.0], [10.5, 4.0]]], "planes": [],
                     "openings": [{"id": "ro_001", "kind": "terrace", "room_id": "r_L1_teras",
                                   "polygon": [[6.1, -0.5], [10.5, -0.5], [10.5, 4.0], [6.1, 4.0]],
                                   "parapet_height": _v(None, "assumed"),
                                   "parapet_wall_ids": ["w_L1_001", "w_L1_006"], "source": "derived"}],
                     "covering": "clay_tiles", "status": "verified", "evidence": EV}}


def _east_wall() -> dict:
    """``w_L1_006`` as ``build_walls`` hands it to the booleans: the built line, the roof cut, its parapet stretch,
    the solid from ``wall_pieces`` and the cutter of ``win_L1_002`` (same steps as ``build_walls``)."""
    b = _attic07()
    level = b["levels"][0]
    model = R.roof_model(b["roof"], b)
    cut = R.wall_cut(model)
    ext = shell.corner_extensions(b["walls"])
    trims = shell.trim_wall_overlaps([dict(w, **ext.get(w["id"], {})) for w in b["walls"]])
    wall = next(w for w in b["walls"] if w["id"] == "w_L1_006")
    start, end = trims[wall["id"]]["start"], trims[wall["id"]]["end"]
    parapets = shell.trimmed_spans(wall, start, end, R.parapet_cuts(model, b, level)[wall["id"]])
    height = float(cut["top"]) + 0.5 - 3.0
    solid = shell.wall_pieces(start, end, 0.25, 3.0, height, cut["planes"], parapets)
    window = next(o for o in b["openings"] if o["id"] == "win_L1_002")
    bottom, top, _ = shell.opening_vertical(window, level, False)
    cx, cy, _ = shell.opening_centre_on_wall(window, wall)
    cutter = geom2d.box((cx, cy, (bottom + top) / 2.0), (0.6, 0.25 + shell.DEFAULTS["cutter_extra"], top - bottom),
                        G.segment_angle_deg(start, end))
    return {"start": start, "end": end, "planes": cut["planes"], "height": height, "parapets": parapets,
            "solid": solid, "cutter": cutter, "window": (bottom, top)}


def _piece(e: dict, s0: float, s1: float, z0: float, z1: float | None):
    """A closed piece of the east wall from s0 to s1 along it and z0 up to z1 (None: the roof underside)."""
    start, end = e["start"], e["end"]
    length = G.distance(start, end)
    c = G.point_along_segment(start, end, (s0 + s1) / 2.0 / length)
    top = 3.0 + e["height"]
    verts, faces = geom2d.box((c[0], c[1], (z0 + top) / 2.0), (s1 - s0, 0.25, top - z0),
                              G.segment_angle_deg(start, end))
    return geom2d.clip_solid_below(verts, faces, [(0.0, 0.0, z1)] if z1 is not None else e["planes"])


def _window_cut(e: dict, with_parapet: bool = True):
    """The east wall as a right cut leaves it: the parapet piece, the gable piece around the window hole."""
    (s0, s1), (z0, z1) = (5.75 - 0.3, 5.75 + 0.3), e["window"]          # win_L1_002: y 6.0 = s 5.75 on the wall
    parts = [_piece(e, 3.75, s0, 3.0, None), _piece(e, s1, 7.5, 3.0, None),
             _piece(e, s0, s1, 3.0, z0), _piece(e, s0, s1, z1, None)]
    if with_parapet:
        parts.insert(0, _piece(e, 0.0, 3.75, 3.0, 4.0))
    return geom2d.merge(parts)


# --------------------------------------------------------------------------
# Pure parts (CPU)
# --------------------------------------------------------------------------

def test_the_east_wall_of_synthetic07_is_two_touching_pieces():
    e = _east_wall()
    assert e["start"] == pytest.approx([9.875, 0.25]) and e["end"] == pytest.approx([9.875, 7.75])
    assert e["parapets"] == [pytest.approx((0.0, 3.75, 4.0))]
    verts, faces = e["solid"]
    assert (len(verts), len(faces)) == (16, 12)                        # two closed boxes, merged, not welded
    zs = sorted({round(v[2], 4) for v in verts})
    assert zs[0] == 3.0 and 4.0 in zs and zs[-1] == pytest.approx(GABLE_TOP, abs=1e-3)
    # the end faces at s 3.75 (y 4.0) lie on each other, opposite: why the boolean needs use_self
    ends = [geom2d.face_normal(verts, f)[1] for f in faces
            if all(abs(verts[i][1] - 4.0) < 1e-9 for i in f)]
    assert sorted(round(n) for n in ends) == [-1, 1]
    parapet = 3.75 * 0.25 * 1.0
    assert shell.mesh_volume(verts, faces) == pytest.approx(parapet + 2.3323, abs=1e-3)


def test_the_guard_finds_an_empty_wall():
    e = _east_wall()
    problems = shell.wall_cut_problems(e["solid"], ([], []), [e["cutter"]])
    assert problems and problems[0] == "no faces left after the cuts (had 12)"
    assert any(p.startswith("lost 3.2698 m³ of 3.2698 m³, more than its cutters hold (0.1944 m³)") for p in problems)
    assert any(p.startswith("its y extent shrank") for p in problems)


def test_the_guard_finds_a_lost_parapet_piece():
    e = _east_wall()
    after = _window_cut(e, with_parapet=False)
    problems = shell.wall_cut_problems(e["solid"], after, [e["cutter"]])
    assert any(p.startswith("lost 1.1175 m³") for p in problems)                 # parapet 0.9375 + window 0.18
    assert "its y extent shrank from [0.250, 7.750] to [4.000, 7.750] where no cutter reaches" in problems


def test_the_guard_finds_a_lost_gable():
    e = _east_wall()
    after = geom2d.merge([_piece(e, 0.0, 3.75, 3.0, 4.0), _piece(e, 3.75, 7.5, 3.0, 4.0)])
    problems = shell.wall_cut_problems(e["solid"], after, [e["cutter"]])
    assert any(p.startswith("its z extent shrank from [3.000, 6.801] to [3.000, 4.000]") for p in problems)


def test_the_window_cut_passes_the_guard():
    e = _east_wall()
    after = _window_cut(e)
    assert shell.mesh_volume(*after) == pytest.approx(shell.mesh_volume(*e["solid"]) - 0.6 * 0.25 * 1.2, abs=1e-6)
    assert shell.wall_cut_problems(e["solid"], after, [e["cutter"]]) == []
    # a cut never adds volume
    grown = geom2d.merge([after, geom2d.box((9.875, 2.0, 3.5), (0.25, 1.0, 1.0))])
    assert shell.wall_cut_problems(e["solid"], grown, [e["cutter"]]) == ["gained 0.0700 m³ (3.2698 -> 3.3398 m³)"]


def test_the_guard_on_a_turned_plain_wall_and_a_wall_wholly_cut():
    angle = 30.0
    u = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))

    def at(s, z, size):
        return geom2d.box((2.0 + u[0] * s, 1.0 + u[1] * s, z), size, angle)

    before = at(0.0, 1.5, (4.0, 0.2, 3.0))
    cutter = at(0.5, 1.5, (1.0, 0.22, 1.2))                                    # a window 1.0 x 1.2 at s 0.5
    after = geom2d.merge([at(-1.0, 1.5, (2.0, 0.2, 3.0)), at(1.5, 1.5, (1.0, 0.2, 3.0)),
                          at(0.5, 0.45, (1.0, 0.2, 0.9)), at(0.5, 2.55, (1.0, 0.2, 0.9))])
    assert shell.mesh_volume(*after) == pytest.approx(2.4 - 0.24, abs=1e-9)
    assert shell.wall_cut_problems(before, after, [cutter]) == []
    # a short wall wholly inside its cutter (an opening as wide and high as the wall) may go
    short = at(0.5, 1.5, (0.8, 0.2, 1.0))
    assert shell.wall_cut_problems(short, ([], []), [cutter]) == []
    # the same wall with the cutter elsewhere may not
    assert shell.wall_cut_problems(short, ([], []), [at(3.0, 1.5, (1.0, 0.22, 1.2))])


def test_the_parapet_piece_keeps_its_top_above_a_lower_roof_underside():
    # the M10 example's south attic wall: the roof underside lies at 3.70-3.87 m along the terrace, the parapet top
    # stays at 4.00 m (no roof is over a parapet); a box clipped by the roof planes would lower it
    roof = B.prepare(EXAMPLE)["roof"]
    cut = R.wall_cut(roof)
    vb = V.variant_building(EXAMPLE, "base")
    level = next(lv for lv in vb["levels"] if lv["id"] == roof["over_level_id"])
    walls = [w for w in vb["walls"] if w["level_id"] == level["id"]]
    ext = shell.corner_extensions(walls)
    trims = shell.trim_wall_overlaps([dict(w, **ext.get(w["id"], {})) for w in walls])
    wall = next(w for w in walls if w["id"] == "w_L1_001")
    start, end = trims[wall["id"]]["start"], trims[wall["id"]]["end"]
    spans = shell.trimmed_spans(wall, start, end, R.parapet_cuts(roof, vb, level)[wall["id"]])
    assert spans == [pytest.approx((6.125, 10.25, 4.0))]
    under = geom2d.surface_z(cut["planes"], 8.0, 0.125)
    assert under == pytest.approx(3.7824, abs=1e-3)
    verts, faces = shell.wall_pieces(start, end, float(wall["thickness"]), 3.0, float(cut["top"]) + 0.5 - 3.0,
                                     cut["planes"], spans)
    tops = [geom2d.face_center(verts, f) for f in faces if geom2d.face_normal(verts, f)[2] > 0.9]
    over = [c for c in tops if c[0] > 6.125]
    assert over and all(c[2] == pytest.approx(4.0, abs=1e-9) for c in over)


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

DUMP = textwrap.dedent("""
    import bmesh, bpy, json, sys
    from mathutils import Vector
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.get("wenart_kind") != "wall" or not str(ob.get("wenart_id")).startswith("w_"):
            continue                        # the walls, not the skirting boards
        mw = ob.matrix_world
        verts = [list(mw @ v.co) for v in ob.data.vertices]
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        row = {"faces": len(ob.data.polygons), "verts": verts, "volume": bm.calc_volume(signed=True),
               "manifold": all(e.is_manifold for e in bm.edges),
               "tops": [list(mw @ p.center) for p in ob.data.polygons if p.normal.z > 0.9]}
        bm.free()
        hits = {}
        for name, (y, z) in {"window": (6.0, 4.5), "under_sill": (6.0, 3.5), "over_head": (6.0, 5.25),
                             "parapet": (2.0, 3.5), "over_parapet": (2.0, 4.2), "gable": (4.5, 6.0)}.items():
            hit = ob.ray_cast(Vector((11.0, y, z)), Vector((-1.0, 0.0, 0.0)))
            hits[name] = bool(hit[0])
        row["hits"] = hits
        rows[ob.name] = row
    json.dump(rows, open(out, "w"))
""")


@needs_blender
def test_synthetic07_east_wall_stands_with_its_parapet_gable_and_window(tmp_path):
    path = tmp_path / "attic07.json"
    path.write_text(json.dumps(_attic07()), encoding="utf-8")
    manifest_path = cli.build(path, tmp_path / "scene", no_textures=True, preview_samples=1)
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    (tmp_path / "dump.py").write_text(DUMP, encoding="utf-8")
    dump = tmp_path / "walls.json"
    cli.run_blender(tmp_path / "dump.py", [str(dump)], blend=str(manifest_path.parent / "scene.blend"))
    walls = json.loads(dump.read_text(encoding="utf-8"))

    # every wall of the attic stands (pod F2: glTF 'w_L1_006.001 has no primitives')
    ids = {w["id"] for w in _attic07()["walls"]}
    assert {name.split(".")[0] for name in walls} == ids
    assert {name: row["faces"] for name, row in walls.items() if not row["faces"]} == {}
    east = next(row for name, row in walls.items() if name.startswith("w_L1_006"))
    assert east["manifold"]
    # the parapet (s 0-3.75, y 0.25-4.0) tops out at 4.00 m, the gable at the roof underside under the ridge
    parapet_tops = [c for c in east["tops"] if c[1] < 4.0 - 1e-3]
    assert parapet_tops and all(c[2] == pytest.approx(4.0, abs=1e-4) for c in parapet_tops)
    top = max(v[2] for v in east["verts"])
    assert top == pytest.approx(GABLE_TOP, abs=2e-3)
    assert all(abs(v[1] - 4.0) < 1e-3 for v in east["verts"] if v[2] > top - 1e-4)       # at the ridge, y 4.0
    # the window hole: 0.6 x 1.2 x 0.25 m out of the solid; a ray through it passes, around it the wall stands
    assert east["volume"] == pytest.approx(3.75 * 0.25 * 1.0 + 2.3323 - 0.6 * 0.25 * 1.2, abs=2e-3)
    assert east["hits"] == {"window": False, "under_sill": True, "over_head": True, "parapet": True,
                            "over_parapet": False, "gable": True}

    # the manifest: the wall after its cut, no error
    entry = next(o for o in m["objects"] if o["kind"] == "wall" and o["wenart_id"] == "w_L1_006")
    assert entry["parapet"] == [{"s": [0.0, 3.75], "z_top": 4.0}]
    cuts = entry["after_cuts"]
    assert cuts["openings"] == ["win_L1_002"] and cuts["faces"] > 12 and "problems" not in cuts
    assert cuts["z_range"] == pytest.approx([3.0, GABLE_TOP], abs=2e-3)
    assert not any("ERROR" in w for w in m["warnings"])
    assert {o["wenart_id"] for o in m["objects"] if o["kind"] == "wall"} >= ids
    for o in m["objects"]:
        if o["kind"] == "wall" and o.get("after_cuts"):
            assert o["after_cuts"]["faces"] > 0 and "problems" not in o["after_cuts"], o["name"]
