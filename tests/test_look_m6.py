"""Milestone 6 Cycles realism package (docs/milestone6.md §5, §9): CPU tests.

One test (or more) per row of §5, pure parts first, then Blender parts
(skipped without a Blender binary) on two hand-made buildings and one level
of synthetic-03:

- ``flat``: a 4 x 3 m bedroom (small window: a dim room) and a 3.5 x 3 m
  kitchen (a wide window) under one north wall, a door between them, a
  parametric double bed with a cushion, a nightstand and a kitchen counter;
  built with fake Poly Haven veneer and linen maps (no wet-wall image, so
  the kitchen walls get the procedural tiles). The kitchen camera that looks
  at the window is rendered in one Blender process that then checks the
  window pull, the alt look and the EXR passes against fresh saves of the
  same Render Result.
- ``hall``: an L-shaped windowless hall and a small windowless storage room
  with an unverified wardrobe, built with ``--no-textures``: the light at the
  pole of inaccessibility, skirting gaps, and the camera-only stripes
  rendered three ways (as built, stripes for every ray, no stripes).
- synthetic-03 L1 without furniture, ``--no-textures``: wall ``w_L1_006``
  (hall | bedroom + bathroom) is split at the room corners; the bathroom
  tiles stay a flat colour without textures.

Pinned contracts: ``piece_bbox`` / ``obstacle_rect`` of every parametric
type equal the Milestone 5 values, and the ``m5`` cameras of the committed
synthetic-01 / -03 buildings equal their committed scene manifests.
"""
import json
import math
import subprocess
import textwrap
import time
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart import geometry as G
from wenart.blender import build as B
from wenart.blender import cameras as C
from wenart.blender import cli, lighting, schemas, shell
from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.blender import render as R

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "tests" / "fixtures" / "blender_style.json"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                   "/workspace/tools/blender, /opt/wenart/blender, PATH)")
EV = [{"file": "flat.dxf", "method": "vector", "confidence": 1.0}]
KITCHEN_CAM, STORE_CAM = "cam_r_kit_1", "cam_r_st_2"


# ==========================================================================
# Pinned boxes: piece_bbox / obstacle_rect of Milestone 5 (the m5 cameras depend on them)
# ==========================================================================

def _m5_box_table() -> dict:
    """``{"<type>|<w>x<d>|<height>": [w, d, h, source, obstacle w, obstacle d]}``: piece_bbox and
    obstacle_rect of every parametric type and ``unknown``, recorded with the Milestone 5
    parametric.py (a2adcef) for footprints 1.6 x 2.0 and 0.9 x 0.6 turned by 30 degrees, at the
    type height (None) and at 1.1 m."""
    path = ROOT / "tests" / "fixtures" / "m5_piece_boxes.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_piece_boxes_of_every_type_are_the_milestone_5_boxes():
    """docs/milestone6.md §5 row 8: the bedding, fronts and bevel change no box of any type."""
    table = _m5_box_table()
    # Milestone 7 types (docs/milestone7.md §6.4) are newer than the M5 table; every M5 box still matches.
    types = (set(P.PARAMETRIC_TYPES) - {"stair", "side_table", "floor_lamp", "potted_plant"}) | {"unknown"}
    assert {k.split("|")[0] for k in table} == types
    for key, want in table.items():
        ftype, size, height = key.split("|")
        w, d = (float(v) for v in size.split("x"))
        piece = {"type": ftype, "footprint": {"center": [1.0, 2.0], "size": [w, d], "rotation_deg": 30.0},
                 "height": None if height == "None" else float(height)}
        box = P.piece_bbox(piece)
        rect = P.obstacle_rect(piece)
        assert [round(v, 6) for v in box[:3]] + [box[3]] == want[:4], key
        assert [round(v, 6) for v in rect["size"]] == want[4:], key
        assert rect["center"] == [1.0, 2.0] and rect["rotation_deg"] == 30.0
    for ftype in P.BED_TYPES:                                   # the bed box of the spec: 1.6 x 2.0 x 1.0 m
        assert table[f"{ftype}|1.6x2.0|None"][:3] == [1.6, 2.0, 1.0]


def test_library_pieces_keep_their_catalogue_box():
    catalog = json.loads((ROOT / "wenart" / "furniture" / "catalog.json").read_text(encoding="utf-8"))
    entries = [e for e in catalog["entries"] if e.get("bbox_m")]
    assert len(entries) >= 20
    for entry in entries:
        bw, bd, bh = entry["bbox_m"]
        piece = {"type": entry["type"], "footprint": {"center": [0, 0], "size": [bw, bd], "rotation_deg": 0.0},
                 "asset": {"method": "library", "bbox_m": [bw, bd, bh]}}
        assert P.piece_bbox(piece) == (bw, bd, bh, "library"), entry["id"]
        assert entry["type"] in P.PARAMETRIC_TYPES


@pytest.mark.parametrize("project", ["synthetic-01", "synthetic-03"])
def test_m5_cameras_of_the_m5_buildings_are_unchanged(project):
    """The M5 building and scene manifest (commit a2adcef; results/ now holds the M6 runs)."""
    def show(path):
        try:
            out = subprocess.run(["git", "-C", str(ROOT), "show", f"a2adcef:{path}"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            pytest.skip("git history with the M5 results not available")
        return json.loads(out.stdout.decode("utf-8"))
    building = show(f"results/furniture/{project}/building_final.json")
    scene = show(f"results/renders/{project}/scene_manifest.json")
    want = {c["name"]: c for c in scene["cameras"]}
    got = {p["name"]: p for lv in building["levels"] for p in C.plan_cameras(building, lv["id"], policy="m5")}
    assert set(got) == set(want)
    for name, cam in want.items():
        assert got[name]["position"] == pytest.approx(cam["position"], abs=1e-3), name
        assert got[name]["target"] == pytest.approx(cam["target"], abs=1e-3), name


# ==========================================================================
# Row 2: kitchen counter fronts
# ==========================================================================

@pytest.mark.parametrize("ftype", P.COUNTER_TYPES)
def test_counter_fronts_stand_proud_of_the_carcass(ftype):
    w, d, h = 2.4, 0.6, 0.9
    parts = P.build_parts(ftype, w, d, h)
    carcass = next(p for p in parts if p["role"] == "body")
    fronts = [p for p in parts if p["role"] == "front"]
    handles = [p for p in parts if p["role"] == "handle"]
    assert len(fronts) == len(handles) == 4
    cy0 = min(v[1] for v in carcass["verts"])
    for front in fronts:
        fy0, fy1 = min(v[1] for v in front["verts"]), max(v[1] for v in front["verts"])
        # 1 mm gap: no face of a front lies in a carcass face plane (they rendered black when coplanar).
        assert fy1 == pytest.approx(cy0 - P.FRONT_GAP) and fy1 < cy0
        carcass_planes = {round(v[i], 9) for v in carcass["verts"] for i in (1,)}
        assert not {round(fy0, 9), round(fy1, 9)} & carcass_planes
    for handle, front in zip(handles, fronts):
        hy1 = max(v[1] for v in handle["verts"])
        assert hy1 == pytest.approx(min(v[1] for v in front["verts"]))           # on the front face
        assert min(v[1] for v in handle["verts"]) >= -d / 2.0 - 1e-9              # inside the footprint
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert (x1 - x0, y1 - y0, z1 - z0) == pytest.approx((w, d, h))
    details = F.design_details(ftype, parts)
    assert [(e["kind"], e["field"]) for e in details] == [("counter_fronts", "counter_fronts")]
    assert "4 front(s) 1 mm proud" in details[0]["value"] and details[0]["reason"]


# ==========================================================================
# Row 8: soft bedding, bevel radii, rest height, materials
# ==========================================================================

def test_soft_bedding_stays_inside_the_bed_box():
    w, d, h = 1.6, 2.0, 0.55
    parts = P.build_parts("bed_double", w, d, h)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert (x0, y0, z0, x1, y1, z1) == pytest.approx((-0.8, -1.0, 0.0, 0.8, 1.0, 1.0))
    roles = [p["role"] for p in parts]
    assert roles == ["body", "back", "mattress", "duvet", "turndown", "pillow", "pillow"]
    soft = [p for p in parts if p.get("smooth")]
    assert {p["role"] for p in soft} == {"mattress", "duvet", "turndown", "pillow"}
    assert {p["key"] for p in soft} == {"bedding", "duvet"}
    back = next(p for p in parts if p["role"] == "back")
    back_y = min(v[1] for v in back["verts"])
    for p in soft:
        xs, ys, zs = zip(*p["verts"])
        assert min(xs) >= -0.8 and max(xs) <= 0.8 and min(ys) >= -1.0 and max(ys) < back_y and max(zs) < 1.0
        assert min(zs) >= 0.3 - 1e-9                                       # on or above the frame
    duvet = next(p for p in parts if p["role"] == "duvet")
    assert min(v[2] for v in duvet["verts"]) < h - 0.1 < max(v[2] for v in duvet["verts"])  # drapes over the sides
    assert max(v[0] for v in duvet["verts"]) > max(v[0] for p in parts if p["role"] == "mattress" for v in p["verts"])
    # Pillows lean 14 degrees, their top towards the headboard (+Y).
    pillow = next(p for p in parts if p["role"] == "pillow")
    top = max(pillow["verts"], key=lambda v: v[2])
    bottom = min(pillow["verts"], key=lambda v: v[2])
    assert top[1] > bottom[1]
    # Closed meshes with outward normals.
    from wenart.blender import geom2d
    for p in soft:
        cx, cy, cz = (sum(v[i] for v in p["verts"]) / len(p["verts"]) for i in range(3))
        out = 0
        for f in p["faces"]:
            n = geom2d.face_normal(p["verts"], f)
            c = geom2d.face_center(p["verts"], f)
            out += n[0] * (c[0] - cx) + n[1] * (c[1] - cy) + n[2] * (c[2] - cz) > 0
        assert out >= 0.97 * len(p["faces"]), p["role"]
    assert P.build_parts("bed_double", w, d, h) == parts                     # deterministic (wrinkles too)


def test_superellipsoid_box_is_exact():
    part = P._superellipsoid(0.3, -0.2, 0.5, 1.2, 0.8, 0.4, 0.2, 0.1, "bedding", "mattress")
    xs, ys, zs = zip(*part["verts"])
    assert (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)) == pytest.approx((-0.3, 0.9, -0.6, 0.2, 0.5, 0.9))
    edges = {}
    for f in part["faces"]:
        for a, b in zip(f, f[1:] + f[:1]):
            edges[(min(a, b), max(a, b))] = edges.get((min(a, b), max(a, b)), 0) + 1
    assert set(edges.values()) == {2}                                         # closed (manifold) surface


def test_bevel_radius_per_part():
    box = P._box(0.0, 0.0, 0.0, 1.0, 0.5, 0.3, "wood", "body")
    assert P.part_bevel_radius(box) == P.BEVEL_BY_ROLE["body"]
    assert P.part_bevel_radius(dict(box, key="fabric")) == P.BEVEL_SOFT_KEYS["fabric"]
    thin = P._box(0.0, 0.0, 0.0, 1.0, 0.012, 0.3, "fabric", "cushion")
    assert P.part_bevel_radius(thin) == pytest.approx(0.004)                  # a third of the smallest side
    assert P.part_bevel_radius(dict(box, key="glass")) == 0.0
    assert P.part_bevel_radius(dict(box, role="mystery")) == P.BEVEL_DEFAULT_M
    assert P.part_bevel_radius(dict(box, key="ceramic", role="bowl")) == P.BEVEL_BY_KEY["ceramic"]
    for ftype in P.PARAMETRIC_TYPES:
        for part in P.build_parts(ftype, 1.2, 0.8, 0.9):
            r = P.part_bevel_radius(part)
            xs, ys, zs = zip(*part["verts"])
            smallest = min(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
            assert 0.0 <= r <= min(P.BEVEL_WIDTH_M, smallest / 3.0 + 1e-12), (ftype, part["role"])
            if part.get("smooth"):
                assert r == 0.0


def test_edge_bevel_weights_skip_smooth_edges():
    normals = [(0, 0, 1), (1, 0, 0), (0.99, 0.141, 0.0)]
    radii = [0.006, 0.006, 0.006]
    weights = F.edge_bevel_weights(radii, normals, [[0, 1], [1, 2], [0], []])
    assert weights == pytest.approx([0.006 / P.BEVEL_WIDTH_M, 0.0, 0.006 / P.BEVEL_WIDTH_M, 0.0])
    assert F.edge_bevel_weights([0.0, 0.2], normals, [[0, 1], [1]]) == pytest.approx([1.0, 1.0])   # capped at 1


def test_bedding_details_and_rest_height():
    parts = P.build_parts("bed_double", 1.6, 2.0, 0.55)
    (detail,) = F.design_details("bed_double", parts)
    assert detail["kind"] == detail["field"] == "bedding" and "2 pillow(s) leaning 14 degrees" in detail["value"]
    assert F.design_details("sofa", P.build_parts("sofa", 2.0, 0.9, 0.85)) == []
    top = P.bedding_top(1.6, 2.0, 0.55)
    assert top == pytest.approx(max(v[2] for p in parts if p["key"] in ("bedding", "duvet") for v in p["verts"]))
    host = {"id": "b", "type": "bed_double", "height": None,
            "footprint": {"center": [0, 0], "size": [1.6, 2.0], "rotation_deg": 0.0}}
    assert F.decor_height_above_floor({"type": "cushion"}, host, True)[0] == pytest.approx(round(top, 4))
    assert F.decor_height_above_floor({"type": "cushion"}, host, False)[0] == pytest.approx(0.55)  # library bed
    assert F.decor_height_above_floor({"type": "cushion", "center": [0, 0, 0.7]}, host, True)[0] == 0.7


def test_veneer_and_fabric_materials_in_the_vocabulary():
    from wenart.style import vocabulary as V

    assert V.veneer_for("wood_oak_light") == "wood_veneer_oak" and V.veneer_for("wood_walnut") == "wood_veneer_walnut"
    assert V.veneer_for("wood_parquet") == "wood_veneer_oak" and V.veneer_for("marble") is None
    assert V.FURNITURE_MATERIALS["wood_veneer_oak"]["asset"] == "oak_veneer_01"
    assert V.FURNITURE_MATERIALS["wood_veneer_walnut"]["asset"] == "walnut_veneer"
    assert V.FURNITURE_MATERIALS["fabric_linen"]["asset"] == V.FURNITURE_MATERIALS["fabric_white"]["asset"] == \
        "rough_linen"
    # Real sizes of the Poly Haven API (``dimensions`` in mm, checked 2026-10-02).
    assert V.FURNITURE_MATERIALS["wood_veneer_oak"]["size_m"] == [1.83, 1.83]
    assert V.FURNITURE_MATERIALS["wood_veneer_walnut"]["size_m"] == [1.8, 1.8]
    assert V.FURNITURE_MATERIALS["fabric_linen"]["size_m"] == [0.2707, 0.2713]
    assert V.albedo_mode("fabric_linen") == ("flat", 0.5) and V.albedo_mode("fabric_white") == ("flat", 0.35)
    assert V.albedo_mode("wood_veneer_oak") == ("texture", None)
    assert V.METALLIC == {"steel_brushed": 1.0}
    assert V.furniture_textures() == [("polyhaven", "rough_linen", "fabric_linen"),
                                      ("polyhaven", "oak_veneer_01", "wood_veneer_oak"),
                                      ("polyhaven", "walnut_veneer", "wood_veneer_walnut")]
    for slug in V.FURNITURE_MATERIALS:
        assert slug in V.FLAT_COLOURS and slug in V.ROUGHNESS
    from wenart.blender import materials as M
    assert M.metallic("steel_brushed") == 1.0 and M.metallic("wood_veneer_oak") == 0.0
    assert M.albedo_mode("fabric_linen") == ("flat", 0.5)


def test_assets_fetch_the_furniture_textures(monkeypatch, tmp_path):
    from wenart.assets import fetch, web
    from wenart.style.profile import default_profile

    calls = []

    def fake_texture(asset_id, out_dir, size="2k", source=None, licence=None):
        calls.append((asset_id, source))
        if asset_id == "walnut_veneer":
            raise web.NetworkError("blocked host (simulated)")
        return {"id": asset_id, "source": source, "licence": "CC0", "size_m": [1.0, 1.0], "files": {}}

    monkeypatch.setattr(fetch, "fetch_texture", fake_texture)
    monkeypatch.setattr(fetch, "fetch_hdri", lambda *a, **k: {"file": "x.hdr"})
    result = fetch.fetch_for_style(default_profile(), tmp_path, log=lambda *_: None)
    assert ("oak_veneer_01", "polyhaven") in calls and ("rough_linen", "polyhaven") in calls
    assert [c[0] for c in calls].count("rough_linen") == 1
    assert "walnut_veneer" in result["failed"] and "oak_veneer_01" in result["textures"]   # failures: flat colour
    assert fetch.source_of_texture("oak_veneer_01") == fetch.source_of_texture("rough_linen") == "polyhaven"


def test_verify_lists_the_furniture_textures_with_their_sizes(monkeypatch):
    from wenart.assets import ambientcg, fetch, polyhaven

    listing = {"oak_veneer_01": {"dimensions": [1830.0000429, 1830.0000429]},
               "walnut_veneer": {"dimensions": [1799.9999523, 1799.9999523]},
               "rough_linen": {"dimensions": [270.708, 271.3]}}
    monkeypatch.setattr(polyhaven, "list_assets", lambda kind="textures": listing if kind == "textures" else {})
    monkeypatch.setattr(ambientcg, "infos", lambda ids: {})
    rows = [r for r in fetch.verify_vocabulary() if r["kind"] == "furniture_texture"]
    assert {r["id"] for r in rows} == {"oak_veneer_01", "walnut_veneer", "rough_linen"}
    assert all(r["exists"] and r["size_ok"] for r in rows), rows
    listing["rough_linen"]["dimensions"] = [500.0, 500.0]
    rows = [r for r in fetch.verify_vocabulary() if r["id"] == "rough_linen"]
    assert rows and not any(r["size_ok"] for r in rows)


# ==========================================================================
# Rows 3, 9: wall splits, door handles, skirting (pure)
# ==========================================================================

def test_wall_split_positions_at_the_room_corners():
    wall = {"start": [-0.2, 3.1], "end": [7.8, 3.1], "thickness": 0.2}
    rooms = [{"polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}, {"polygon": [[4.1, 0], [7.6, 0], [7.6, 3], [4.1, 3]]},
             {"polygon": [[0, 3.2], [8, 3.2], [8, 6], [0, 6]]}]           # a room on the other side
    assert shell.wall_split_positions(wall, rooms) == [0.2, 4.2, 4.3, 7.8]
    assert shell.wall_split_positions(dict(wall, end=[-0.2, 3.1]), rooms) == []
    far = [{"polygon": [[0, 0], [1, 0], [1, 1], [0, 1]]}]                   # corners 2 m off the wall line
    assert shell.wall_split_positions(wall, far) == []


def test_door_handles_sit_on_both_faces_at_lever_height():
    width, height = 0.9, 2.1
    from wenart.blender import geom2d
    verts, _faces = geom2d.merge(shell.door_handle_parts(width, height))
    xs, ys, zs = zip(*verts)
    lt = shell.DEFAULTS["leaf_thickness"]
    fw = shell.DEFAULTS["frame_width"]
    assert min(xs) > -width / 2.0 + fw and max(xs) < width / 2.0 - fw                  # on the leaf
    assert max(abs(y) for y in ys) == pytest.approx(lt / 2.0 + shell.HANDLE_DEPTH)    # door box + handle depth
    assert min(ys) < -lt / 2.0 and max(ys) > lt / 2.0                                 # both faces
    assert all(abs(y) >= lt / 2.0 - 1e-9 for y in ys)                                 # never inside the leaf
    levers = shell.door_handle_parts(width, height)[2::3]
    assert all(sum(v[2] for v in lv[0]) / 8 == pytest.approx(shell.HANDLE_HEIGHT) for lv in levers)
    assert 0.0 < min(zs) and max(zs) < height - fw
    low = shell.door_handle_parts(0.8, 2.1, sill=0.15)
    assert sum(v[2] for v in low[2][0]) / 8 == pytest.approx(shell.HANDLE_HEIGHT - 0.15)


def test_skirting_spans_leave_gaps_at_doors():
    poly = [(0, 0), (4, 0), (4, 3), (0, 3)]
    spans = shell.skirting_spans(poly, [((4.05, 1.5), 0.9), ((2.0, -0.1), 0.6)])
    assert spans == [(0, 0.0, 1.7), (0, 2.3, 4.0), (1, 0.0, 1.05), (1, 1.95, 3.0), (2, 0.0, 4.0), (3, 0.0, 3.0)]
    # A door at a corner and a gap longer than the edge.
    spans = shell.skirting_spans(poly, [((0.3, 3.05), 0.6), ((4.05, 1.5), 4.0)])
    assert (1, 0.0, 3.0) not in spans and all(e != 1 for e, _, _ in spans)
    assert (2, 0.0, 3.4) in spans                    # edge 2 runs from (4, 3) to (0, 3): the door at 3.4 .. 4.0
    verts, faces = shell.skirting_boxes(poly, shell.skirting_spans(poly, []), 0.0)
    assert len(faces) == 4 * 6
    for x, y, z in verts:                                       # inside the room, 12 mm deep, 8 cm tall
        assert -1e-9 <= x <= 4 + 1e-9 and -1e-9 <= y <= 3 + 1e-9 and -1e-9 <= z <= shell.SKIRTING_H + 1e-9
        assert min(x, 4 - x, y, 3 - y) <= shell.SKIRTING_T + 1e-9
    # L-shaped hall: every board along its own edge, inside the polygon.
    hall = [(0, 0), (4.4, 0), (4.4, 1.2), (1.6, 1.2), (1.6, 3.1), (0, 3.1)]
    verts, _ = shell.skirting_boxes(hall, shell.skirting_spans(hall, []), 0.0)
    assert all(G.point_in_polygon((x, y), hall) or min(G.point_segment_distance((x, y), hall[i], hall[(i + 1) % 6])
                                                       for i in range(6)) < 1e-6 for x, y, _ in verts)


# ==========================================================================
# Rows 5, 6: light at the pole of inaccessibility, dim rooms
# ==========================================================================

L_HALL = [(0, 0), (4.4, 0), (4.4, 1.2), (1.6, 1.2), (1.6, 3.1), (0, 3.1)]


def _square_inside(plan, polygon) -> bool:
    cx, cy = plan["center"]
    h = plan["size"] / 2.0
    corners = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    return all(G.point_in_polygon(c, polygon) for c in corners)


def test_polylabel_finds_the_pole_of_inaccessibility():
    x, y, d = lighting.polylabel(L_HALL)
    assert G.point_in_polygon((x, y), L_HALL)
    assert d == pytest.approx(0.8, abs=lighting.POLYLABEL_PRECISION_M + 0.04)     # the 1.6 m arm is the limit
    assert lighting.polylabel(L_HALL) == (x, y, d)                                    # deterministic
    # The centroid of this L lies near the reflex corner: a light there would be half in the wall.
    cx, cy = G.polygon_centroid(L_HALL)
    assert lighting._signed_distance(cx, cy, L_HALL) < d
    assert lighting.polylabel([(0, 0), (4, 0), (4, 3), (0, 3)]) == pytest.approx((2.0, 1.5, 1.5), abs=0.01)
    u = [(0, 0), (3, 0), (3, 3), (2, 3), (2, 1), (1, 1), (1, 3), (0, 3)]             # a U: not the centroid
    x, y, d = lighting.polylabel(u)
    assert G.point_in_polygon((x, y), u) and d > 0.45
    assert not G.point_in_polygon(G.polygon_centroid(u), u) or lighting._signed_distance(
        *G.polygon_centroid(u), u) < d


def test_area_light_square_lies_inside_the_room():
    plan = lighting.area_light_plan(L_HALL)
    assert _square_inside(plan, L_HALL) and plan["size"] <= math.sqrt(2) * plan["boundary_distance"] + 1e-9
    for poly in ([(0, 0), (4, 0), (4, 3), (0, 3)], [(0, 0), (0.9, 0), (0.9, 1.4), (0, 1.4)],
                 [(0, 0), (6, 0), (6, 0.8), (0, 0.8)]):
        plan = lighting.area_light_plan(poly)
        assert _square_inside(plan, poly), (poly, plan)
        assert lighting.AREA_LIGHT_MIN_SIZE * 0 < plan["size"] <= lighting.AREA_LIGHT_MAX_SIZE
    # A plain rectangle keeps the Milestone 5 light: centroid, half the short side.
    assert lighting.area_light_plan([(0, 0), (4, 0), (4, 3), (0, 3)]) == \
        {"center": [2.0, 1.5], "size": 1.5, "boundary_distance": 1.5}


def test_dim_room_rule():
    level = {"elevation": 0.0, "ceiling_height": 2.7}
    small = [{"type": "window", "width": 0.6, "height": 1.2, "sill_height": 0.9}]
    big = [{"type": "window", "width": 1.6, "height": 1.4, "sill_height": 0.9}]
    assert lighting.window_floor_ratio(small, level, False, 12.0) == pytest.approx(0.06)
    assert lighting.window_floor_ratio(big, level, False, 10.5) == pytest.approx(2.24 / 10.5)
    assert lighting.fill_light_reason([], None) == "room has no window"
    assert "0.060 < 0.08" in lighting.fill_light_reason(small, 0.06)
    assert lighting.fill_light_reason(big, 0.21) is None
    assert lighting.fill_light_reason(small, lighting.DIM_ROOM_RATIO) is None          # the limit itself is not dim


# ==========================================================================
# Rows 7, 10-12: window pull, flags, deadline (pure)
# ==========================================================================

def test_pane_mask_takes_the_glass_not_the_frame():
    index = np.zeros((6, 8), dtype=np.uint16)
    index[1:5, 2:7] = 9                                  # window frame + glass
    albedo = np.full((6, 8, 3), 0.8)
    albedo[2:4, 3:6] = 0.0                               # glass: no diffuse albedo
    mask = R.pane_mask(index, albedo, {9})
    assert mask.sum() == 6 and mask[2:4, 3:6].all()
    assert not R.pane_mask(index, albedo, {4}).any()


def test_feather_weights_stay_inside_the_mask():
    mask = np.zeros((12, 12), dtype=bool)
    mask[2:10, 2:10] = True
    w = R.feather_weights(mask)
    assert (w[~mask] == 0).all() and w.max() == 1.0
    assert w[2, 5] == pytest.approx(1 / 3) and w[3, 5] == pytest.approx(2 / 3) and w[4, 5] == 1.0
    assert w[5, 5] == 1.0
    edge = np.zeros((6, 6), dtype=bool)
    edge[:, :3] = True                                   # touches the image border: no fade there
    w = R.feather_weights(edge)
    assert w[3, 0] == 1.0 and w[3, 2] == pytest.approx(1 / 3)


def test_choose_pull_rules():
    def c(k, clip, median):
        return {"k": k, "clip": clip, "median": median}
    cands = [c(1, 0.30, 0.95), c(2, 0.05, 0.85), c(3, 0.004, 0.70), c(4, 0.0, 0.50)]
    assert R.choose_pull(cands, 0.6)[0] == 3                          # first with clip <= 1 % and above the walls
    assert R.choose_pull(cands, 0.75)[0] == 2                         # k 3 too dark: the lowest clip that stays brighter
    assert R.choose_pull(cands, 0.99)[0] == 0                         # nothing stays brighter: no pull
    assert R.choose_pull(cands, None)[0] == 3                         # no walls: the clip rule alone
    assert R.choose_pull([c(1, 0.3, 0.9), c(2, 0.2, 0.8)], None)[0] == 2
    assert R.choose_pull([c(1, 0.0, 0.9)], 0.5) == (1, "smallest k with pane clip <= 1 % and panes brighter than "
                                                       "the walls")
    assert R.choose_pull([], 0.5)[0] == 0
    assert R.pull_qualifies(c(1, 0.01, 0.6), 0.5) and not R.pull_qualifies(c(1, 0.011, 0.6), 0.5)


def test_blend_pull_changes_only_the_masked_pixels():
    rng = np.random.default_rng(3)
    main = rng.integers(0, 256, (10, 12, 3), dtype=np.uint8)
    pulled = (main // 4).astype(np.uint8)
    mask = np.zeros((10, 12), dtype=bool)
    mask[3:8, 2:9] = True
    w = R.feather_weights(mask)
    out = R.blend_pull(main, pulled, w)
    assert out.dtype == np.uint8 and np.array_equal(out[w == 0], main[w == 0])
    assert np.array_equal(out[w == 1], pulled[w == 1])
    assert R.clip_share(np.full((4, 4, 3), 255, np.uint8), np.ones((4, 4), bool)) == 1.0
    assert R.clip_share(main, np.zeros((10, 12), bool)) is None
    assert R.display_luminance(np.full((1, 1, 3), 255, np.uint8))[0, 0] == pytest.approx(1.0)


def test_control_flags_are_checked():
    args = R.parse_args(["--out", "x"])
    assert args.alt_look is None and args.max_bounces is None and args.ev_offset == 0.0
    assert args.preview_quality is None and not args.no_denoise
    args = R.parse_args(["--out", "x", "--alt-look", "AgX - Punchy", "--max-bounces", "0", "--ev-offset", "0.3",
                         "--preview-quality", "85", "--no-denoise"])
    R.check_control_flags(args)
    assert (args.alt_look, args.max_bounces, args.ev_offset, args.preview_quality) == ("AgX - Punchy", 0, 0.3, 85)
    for bad in (["--max-bounces", "-1"], ["--preview-quality", "0"], ["--preview-quality", "101"],
                ["--ev-offset", "nan"], ["--alt-look", " "]):
        with pytest.raises(R.UsageError):
            R.check_control_flags(R.parse_args(["--out", "x", *bad]))


def test_max_bounces_limits_indirect_light_but_keeps_the_glass_transmitting():
    # Review L1: --max-bounces 0 (ctl_direct) set only Cycles max_bounces = 0, so camera rays could not pass
    # the two refracting faces of the window glass and every pane rendered black.
    assert R.bounce_settings(0) == {"max_bounces": 2, "diffuse_bounces": 0, "glossy_bounces": 0,
                                    "volume_bounces": 0, "transmission_bounces": 2}
    assert R.bounce_settings(1)["transmission_bounces"] == 2 and R.bounce_settings(1)["diffuse_bounces"] == 1
    assert R.bounce_settings(4) == {"max_bounces": 4, "diffuse_bounces": 4, "glossy_bounces": 4,
                                    "volume_bounces": 4, "transmission_bounces": 4}
    base = dict(samples=16, resolution=(64, 36), denoiser=None, exposure_mode="auto", exposure_value=None,
                target=0.9, wb_mode="auto", wb_fixed=None, hidden=[], plugged=[])
    settings = R.key_settings(**base, max_bounces=0)
    assert settings["max_bounces"] == 0 and settings["bounces"] == R.bounce_settings(0)   # flag value kept
    assert "bounces" not in R.key_settings(**base)                         # a normal render's key is unchanged
    old_rule = {k: v for k, v in settings.items() if k != "bounces"}
    assert R.render_key(settings) != R.render_key(old_rule)                # black-pane renders are not reused

    class Cycles:
        max_bounces = diffuse_bounces = glossy_bounces = transmission_bounces = volume_bounces = 12

    class Layer:
        pass

    class Render:
        pass

    class Scene:
        cycles, render, view_layers = Cycles(), Render(), [Layer()]

    scene = Scene()
    R.configure_render(scene, 4, (32, 18), "CPU", False, max_bounces=0)
    assert {k: getattr(scene.cycles, k) for k in R.bounce_settings(0)} == R.bounce_settings(0)


def test_deadline_from_the_environment():
    assert R.deadline_from_env({}) == (None, None)
    assert R.deadline_from_env({"WENART_DEADLINE": "1790000000"}) == (1790000000.0, None)
    value, note = R.deadline_from_env({"WENART_DEADLINE": "soon"})
    assert value is None and "ignored" in note
    assert R.deadline_from_env({"WENART_DEADLINE": "inf"})[0] is None
    assert R.deadline_passed(100.0, now=100.0) and not R.deadline_passed(100.0, now=99.9)
    assert not R.deadline_passed(None)


def test_cli_passes_the_new_render_flags_and_exit_3(monkeypatch, tmp_path):
    seen = {}

    def fake_run(script, args, blend=None, log_path=None, timeout=7200, cwd=None):
        seen["args"] = list(args)
        if "--force" in args:
            raise cli.BlenderFailed("cut", 3)
        return None

    monkeypatch.setattr(cli, "run_blender", fake_run)
    cli.render("s.blend", str(tmp_path), alt_look="AgX - Punchy", max_bounces=0, no_denoise=True, ev_offset=0.3,
               preview_quality=85)
    a = seen["args"]
    assert a[a.index("--alt-look") + 1] == "AgX - Punchy" and a[a.index("--max-bounces") + 1] == "0"
    assert "--no-denoise" in a and a[a.index("--ev-offset") + 1] == "0.3" and a[a.index("--preview-quality") + 1] == "85"
    assert cli.main(["render", "--scene", "s.blend", "--out", str(tmp_path), "--force"]) == 3
    assert cli.main(["render", "--scene", "s.blend", "--out", str(tmp_path), "--ev-offset", "0.3",
                     "--preview-quality", "70", "--max-bounces", "2", "--alt-look", "AgX - Punchy"]) == 0
    a = seen["args"]
    assert a[a.index("--max-bounces") + 1] == "2" and a[a.index("--preview-quality") + 1] == "70"
    monkeypatch.setattr(cli, "run_blender", lambda *a, **k: (_ for _ in ()).throw(cli.BlenderFailed("x", 5)))
    assert cli.main(["render", "--scene", "s.blend", "--out", str(tmp_path)]) == 1


# ==========================================================================
# Row 13: camera policy and the canonical building hash
# ==========================================================================

def _fp_files(tmp_path: Path) -> dict:
    building = flat_building()
    building["created_utc"] = "2026-10-02T10:00:00Z"
    (tmp_path / "building.json").write_text(json.dumps(building), encoding="utf-8")
    (tmp_path / "style.json").write_text(STYLE.read_text(encoding="utf-8"), encoding="utf-8")
    return B.fingerprint_args(str(tmp_path / "building.json"), str(tmp_path / "style.json"), None, None)


def test_fingerprint_ignores_volatile_keys_and_follows_the_camera_policy(tmp_path):
    args = _fp_files(tmp_path)
    assert args["camera_policy"] == "m5"
    fp = B.build_fingerprint(args)
    building = json.loads((tmp_path / "building.json").read_text(encoding="utf-8"))
    building["created_utc"] = "2026-10-03T11:11:11Z"
    building["rooms"][0]["seconds"] = 12.5
    (tmp_path / "building.json").write_text(json.dumps(building, indent=3), encoding="utf-8")   # other bytes
    assert B.build_fingerprint(args) == fp
    building["rooms"][0]["label"] = "Another"
    (tmp_path / "building.json").write_text(json.dumps(building), encoding="utf-8")
    assert B.build_fingerprint(args) != fp
    building["rooms"][0]["label"] = flat_building()["rooms"][0]["label"]
    (tmp_path / "building.json").write_text(json.dumps(building), encoding="utf-8")
    assert B.build_fingerprint(args) == fp
    assert B.build_fingerprint(dict(args, camera_policy="search")) != fp
    assert cli.build_fingerprint(args["building"], args["style"], camera_policy="search") == \
        B.build_fingerprint(dict(args, camera_policy="search"))
    assert cli.build_fingerprint(args["building"], args["style"]) == fp
    ids = B.referenced_asset_ids(flat_building(), json.loads(STYLE.read_text(encoding="utf-8")))
    assert {"oak_veneer_01", "walnut_veneer", "rough_linen"} <= set(ids)
    assert B.parse_args(["--building", "b", "--out", "o"]).camera_policy == "m5"
    with pytest.raises(SystemExit):
        B.parse_args(["--building", "b", "--out", "o", "--camera-policy", "best"])


def test_cli_build_passes_the_camera_policy(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(cli, "run_blender", lambda script, args, **kw: seen.append(list(args)))
    cli.build("b.json", str(tmp_path))
    cli.build("b.json", str(tmp_path), camera_policy="search")
    assert cli.main(["build", "--building", "b.json", "--out", str(tmp_path), "--camera-policy", "search"]) == 0
    assert [a[a.index("--camera-policy") + 1] for a in seen] == ["m5", "search", "search"]


# ==========================================================================
# Hand-made buildings
# ==========================================================================

def _wall(wid, start, end, thickness=0.2, exterior=True):
    return {"id": wid, "level_id": "L0", "start": list(start), "end": list(end), "thickness": thickness,
            "height": 2.7, "exterior": exterior, "status": "verified", "evidence": EV}


def _opening(oid, kind, wall, center, width, height=None, sill=None):
    return {"id": oid, "type": kind, "level_id": "L0", "wall_id": wall, "center": list(center), "width": width,
            "height": height, "sill_height": sill, "swing_side": None, "status": "verified", "evidence": EV}


def _room(rid, label, rtype, polygon):
    return {"id": rid, "level_id": "L0", "label": label, "room_type": rtype, "polygon": [list(p) for p in polygon],
            "area_computed": abs(G.polygon_area(polygon)), "area_label": None, "has_documented_furniture": True,
            "status": "verified", "evidence": EV}


def _piece(fid, room, ftype, center, size, rotation, front, status="verified"):
    return {"id": fid, "level_id": "L0", "room_id": room, "type": ftype, "source": "from_documents",
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation}, "front_deg": front,
            "height": None, "asset": None, "status": status, "evidence": EV}


def _building(pid, walls, openings, rooms, furniture, decor=()) -> dict:
    return {"schema_version": "0.1", "status": "ok", "project": {"id": pid, "source_folder": f"projects/{pid}",
                                                                 "brief": {}},
            "documents": [], "levels": [{"id": "L0", "label": "L0", "order": 0, "elevation": 0.0,
                                         "ceiling_height": 2.7, "ceiling_height_source": "dimension", "evidence": EV}],
            "walls": walls, "openings": openings, "rooms": rooms, "furniture": furniture, "decor": list(decor),
            "conflicts": [], "unverified": [], "warnings": []}


def flat_building() -> dict:
    """Bedroom (4 x 3 m, 0.6 x 1.2 m window: window/floor 0.06, dim) and kitchen (3.5 x 3 m, 1.6 x 1.4 m
    window) under one north wall ``w_n``; a door in the partition; bed, nightstand, kitchen counter."""
    walls = [_wall("w_s", (-0.2, -0.1), (7.8, -0.1)), _wall("w_n", (-0.2, 3.1), (7.8, 3.1)),
             _wall("w_w", (-0.1, -0.2), (-0.1, 3.2)), _wall("w_e", (7.7, -0.2), (7.7, 3.2)),
             _wall("w_p", (4.05, 0.0), (4.05, 3.0), thickness=0.1, exterior=False)]
    openings = [_opening("win_bed", "window", "w_s", (2.0, -0.1), 0.6, 1.2, 0.9),
                _opening("win_kit", "window", "w_s", (5.85, -0.1), 1.6, 1.4, 0.9),
                _opening("door_p", "door", "w_p", (4.05, 1.5), 0.9)]
    rooms = [_room("r_bed", "Yatak Odasi", "bedroom", [(0, 0), (4, 0), (4, 3), (0, 3)]),
             _room("r_kit", "Mutfak", "kitchen", [(4.1, 0), (7.6, 0), (7.6, 3), (4.1, 3)])]
    furniture = [_piece("f_bed", "r_bed", "bed_double", (2.0, 1.95), (1.6, 2.0), 0.0, 270.0),
                 _piece("f_night", "r_bed", "nightstand", (0.45, 2.75), (0.5, 0.4), 0.0, 270.0),
                 _piece("f_counter", "r_kit", "kitchen_counter", (7.3, 1.5), (2.4, 0.6), -90.0, 180.0)]
    decor = [{"host_id": "f_bed", "type": "cushion", "size": [0.5, 0.3], "center": [2.0, 2.55]}]
    return _building("flat", walls, openings, rooms, furniture, decor)


def hall_building() -> dict:
    """An L-shaped windowless hall (8.32 m2) and a small windowless storage room (1.9 x 1.8 m) with an
    unverified wardrobe facing its door."""
    walls = [_wall("h1", (-0.05, -0.05), (4.45, -0.05), 0.1), _wall("h2", (4.45, -0.05), (4.45, 1.25), 0.1),
             _wall("h3", (4.45, 1.25), (1.65, 1.25), 0.1, exterior=False),
             _wall("h4", (1.65, 1.25), (1.65, 3.15), 0.1, exterior=False),
             _wall("h5", (1.65, 3.15), (-0.05, 3.15), 0.1), _wall("h6", (-0.05, 3.15), (-0.05, -0.05), 0.1),
             _wall("s1", (3.65, 1.25), (3.65, 3.15), 0.1), _wall("s2", (3.65, 3.15), (1.65, 3.15), 0.1)]
    openings = [_opening("d_in", "door", "h1", (3.5, -0.05), 0.9), _opening("d_st", "door", "h4", (1.65, 2.2), 0.7)]
    rooms = [_room("r_hall", "Hol", "hall", L_HALL),
             _room("r_st", "Kiler", "storage", [(1.7, 1.3), (3.6, 1.3), (3.6, 3.1), (1.7, 3.1)])]
    furniture = [_piece("f_wardrobe", "r_st", "wardrobe", (3.35, 2.2), (1.2, 0.5), -90.0, 180.0,
                        status="unverified")]
    return _building("hall", walls, openings, rooms, furniture)


def _fake_maps(root: Path, asset_id: str, size_m: float, rgb=(150, 110, 70)) -> dict:
    tex = root / "textures" / asset_id
    tex.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(len(asset_id))
    noise = rng.integers(-20, 20, (32, 32, 1))
    Image.fromarray(np.clip(np.asarray(rgb)[None, None, :] + noise, 0, 255).astype(np.uint8), "RGB").save(
        tex / "albedo.png")
    Image.new("RGB", (16, 16), (128, 128, 255)).save(tex / "normal.png")
    Image.new("L", (16, 16), 140).save(tex / "roughness.png")
    return {"id": asset_id, "source": "polyhaven", "licence": "CC0", "size_m": [size_m, size_m],
            "files": {k: f"textures/{asset_id}/{k}.png" for k in ("albedo", "normal", "roughness")}}


def _fake_assets(root: Path) -> Path:
    textures = {"oak_veneer_01": _fake_maps(root, "oak_veneer_01", 1.83),
                "rough_linen": _fake_maps(root, "rough_linen", 0.27, (60, 80, 160))}   # dyed blue, like Poly Haven's
    (root / "manifest.json").write_text(json.dumps({"schema_version": "0.1", "textures": textures, "hdris": {},
                                                    "models": {}}), encoding="utf-8")
    return root


def test_hand_made_cameras_see_what_the_blender_tests_need():
    flat = flat_building()
    plans = {p["name"]: p for p in C.plan_cameras(flat, "L0")}
    assert "win_kit" in plans[KITCHEN_CAM]["visible_openings"]
    hall = hall_building()
    plans = {p["name"]: p for p in C.plan_cameras(hall, "L0")}
    assert "f_wardrobe" in plans[STORE_CAM]["visible_furniture"]


DUMP = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    from mathutils import Vector
    from wenart.blender import materials as M
    out = sys.argv[sys.argv.index("--") + 1]
    dg = bpy.context.evaluated_depsgraph_get()
    rows = {}
    for ob in bpy.data.objects:
        row = {"type": ob.type, "kind": ob.get("wenart_kind"), "wenart_id": ob.get("wenart_id"),
               "status": ob.get("wenart_status"), "pass_index": ob.pass_index}
        if ob.type == "MESH":
            mw = ob.matrix_world
            pts = [mw @ v.co for v in ob.data.vertices]
            row["bounds"] = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
            ev = ob.evaluated_get(dg).to_mesh()
            epts = [mw @ v.co for v in ev.vertices]
            row["eval_bounds"] = [[min(p[i] for p in epts), max(p[i] for p in epts)] for i in range(3)]
            ob.evaluated_get(dg).to_mesh_clear()
            row["materials"] = [m.name if m else None for m in ob.data.materials]
            row["modifiers"] = [{"type": m.type, "width": getattr(m, "width", None),
                                 "segments": getattr(m, "segments", None), "limit": getattr(m, "limit_method", None),
                                 "harden": getattr(m, "harden_normals", None)} for m in ob.modifiers]
            attr = ob.data.attributes.get("bevel_weight_edge")
            row["bevel_weights"] = [d.value for d in attr.data] if attr else []
            if ob.get("wenart_kind") in ("door", "wall") or ob.name.startswith("skirting"):
                row["verts"] = [list(p) for p in pts]
            if ob.get("wenart_kind") in ("wall", "door"):
                uv = ob.data.uv_layers.get("box_m")
                faces = []
                for poly in ob.data.polygons:
                    vs = [mw @ ob.data.vertices[i].co for i in poly.vertices]
                    uvs = [uv.data[li].uv for li in poly.loop_indices] if uv else []
                    faces.append({"normal": list(mw.to_3x3() @ poly.normal), "center": list(mw @ poly.center),
                                  "min": [min(v[i] for v in vs) for i in range(3)],
                                  "max": [max(v[i] for v in vs) for i in range(3)],
                                  "material": ob.data.materials[poly.material_index].name,
                                  "uv_min": [min(u[i] for u in uvs) for i in range(2)] if uvs else None,
                                  "uv_max": [max(u[i] for u in uvs) for i in range(2)] if uvs else None})
                row["faces"] = faces
        if ob.type == "LIGHT":
            row.update(light_type=ob.data.type, size=getattr(ob.data, "size", None), energy=ob.data.energy,
                       location=list(ob.matrix_world.translation), visible_camera=ob.visible_camera,
                       portal=bool(ob.data.cycles.is_portal) if ob.data.type == "AREA" else False)
        rows[ob.name] = row
    mats = {}
    for m in bpy.data.materials:
        if not m.node_tree:
            continue
        nodes = m.node_tree.nodes
        bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
        group = next((n for n in nodes if n.bl_idname == "ShaderNodeGroup"), None)
        cam = nodes.get(M.STRIPES_CAMERA_NODE)
        mats[m.name] = {
            "metallic": bsdf.inputs["Metallic"].default_value if bsdf else None,
            "group": group.node_tree.name if group else None,
            "group_links": sorted(l.to_socket.name for l in m.node_tree.links if group and l.from_node == group),
            "stripes_inputs": sorted(l.from_socket.name for i in cam.inputs for l in i.links) if cam else None,
            "images": sorted(n.image.name for n in nodes if n.bl_idname == "ShaderNodeTexImage" and n.image),
            "rgb_to_bw": any(n.bl_idname == "ShaderNodeRGBToBW" for n in nodes)}
    json.dump({"objects": rows, "materials": mats}, open(out, "w"))
""")


def _build(tmp: Path, building: dict, assets: Path | None, extra=()) -> dict:
    path = tmp / "building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    out = tmp / "scene"
    args = ["--building", str(path), "--style", str(STYLE), "--out", str(out), "--no-preview", "--no-glb", *extra]
    if assets is not None:
        args += ["--assets", str(assets)]
    cli.run_blender(cli.BUILD_SCRIPT, args, log_path=out / "build.log", timeout=900)
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    (tmp / "dump.py").write_text(DUMP, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(tmp / "dump.json")], blend=str(out / "scene.blend"), timeout=600)
    dump = json.loads((tmp / "dump.json").read_text(encoding="utf-8"))
    return {"tmp": tmp, "building": building, "path": path, "scene": out, "manifest": manifest, **dump}


@pytest.fixture(scope="module")
def flat(tmp_path_factory):
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("m6_flat")
    return _build(tmp, flat_building(), _fake_assets(tmp / "assets"))


@pytest.fixture(scope="module")
def hall(tmp_path_factory):
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("m6_hall")
    return _build(tmp, hall_building(), None, ["--no-textures"])


def _faces(scene: dict, name: str, normal) -> list[dict]:
    return [f for f in scene["objects"][name]["faces"]
            if sum(a * b for a, b in zip(f["normal"], normal)) > 0.99]


# ==========================================================================
# Blender: scene build
# ==========================================================================

@needs_blender
def test_flat_manifest_validates_and_records_the_policy(flat):
    m = flat["manifest"]
    schemas.validate_scene_manifest(m)
    assert m["camera_policy"] == "m5" and m["build_args"]["camera_policy"] == "m5"
    assert all(c["policy"] == "m5" for c in m["cameras"])
    assert len(m["cameras"]) == 6


@needs_blender
def test_row1_stripes_mix_for_camera_rays_only(hall):
    wardrobe = hall["objects"]["furn_f_wardrobe"]["materials"]
    assert wardrobe and all(name.endswith("__unverified") for name in wardrobe)
    for name in wardrobe:
        assert hall["materials"][name]["stripes_inputs"] == ["Is Camera Ray", "Value"], name


@needs_blender
def test_row3_wall_faces_split_at_the_room_corners(flat):
    """w_n runs along the bedroom (dry) and the kitchen (wet): tiles on the kitchen span only."""
    room_side = _faces(flat, "w_n", (0, -1, 0))
    assert room_side
    for f in room_side:
        x0, x1 = f["min"][0], f["max"][0]
        assert x1 <= 4.0 + 1e-4 or x0 >= 4.1 - 1e-4 or (x0 >= 4.0 - 1e-4 and x1 <= 4.1 + 1e-4), f  # no face spans both
        if x0 >= 4.1 - 1e-4 and x1 <= 7.6 + 1e-4:
            assert f["material"].startswith("tiles_light"), f
        elif x0 >= -1e-4 and x1 <= 4.0 + 1e-4:
            assert f["material"].startswith("plaster_white"), f
    kitchen = [f for f in room_side if f["min"][0] >= 4.1 - 1e-4 and f["max"][0] <= 7.6 + 1e-4]
    bedroom = [f for f in room_side if f["min"][0] >= -1e-4 and f["max"][0] <= 4.0 + 1e-4]
    assert kitchen and bedroom
    wall = next(o for o in flat["manifest"]["objects"] if o["name"] == "w_n")
    assert wall["split_at_m"] == pytest.approx([0.2, 4.2, 4.3, 7.8])
    outside = {f["material"] for f in _faces(flat, "w_n", (0, 1, 0))}
    assert outside == {"plaster_exterior"}


@needs_blender
def test_row3_synthetic_03_wall_w_L1_006(tmp_path):
    """The hall | bedroom + bathroom wall of synthetic-03 L1 (furniture left out: faster)."""
    building = json.loads((ROOT / "projects" / "synthetic-03" / "truth" / "building.json").read_text("utf-8"))
    building["furniture"], building["decor"] = [], []
    scene = _build(tmp_path, building, None, ["--no-textures", "--level", "L1"])
    faces = _faces(scene, "w_L1_006", (1, 0, 0))                     # the side of r_L1_yatak_odasi and r_L1_banyo
    bath = [f for f in faces if f["min"][1] >= 4.25 - 1e-4]
    bed = [f for f in faces if f["max"][1] <= 4.15 + 1e-4]
    assert bath and bed and len(bath) + len(bed) + sum(
        1 for f in faces if f["min"][1] >= 4.15 - 1e-4 and f["max"][1] <= 4.25 + 1e-4) == len(faces)
    assert all(f["material"].startswith("tiles_light") for f in bath)
    assert not any(f["material"].startswith("tiles_light") for f in bed)
    hall_side = _faces(scene, "w_L1_006", (-1, 0, 0))
    assert hall_side and not any(f["material"].startswith("tiles_light") for f in hall_side)
    # Row 4 with --no-textures: flat colours only, no procedural tiles either.
    tiles = scene["manifest"]["materials"]["tiles_light"]
    assert tiles["procedural"] is None and scene["materials"]["tiles_light"]["group"] is None


@needs_blender
def test_row4_procedural_tiles_and_flat_mode(flat):
    m = flat["manifest"]["materials"]
    tiles = m["tiles_light"]
    assert tiles["procedural"] == "glazed_tiles" and not tiles["textured"]
    assert flat["materials"]["tiles_light"]["group"] == "wenart_glazed_tiles"
    assert flat["materials"]["tiles_light"]["group_links"] == ["Base Color", "Normal", "Roughness"]
    kitchen_walls = {f["material"] for f in _faces(flat, "w_e", (-1, 0, 0)) if 0 < f["center"][1] < 3}
    assert kitchen_walls == {"tiles_light"}
    # Flat albedo mode still works: the dyed linen photo gives only its weave to the vocabulary colour.
    linen = m["fabric_linen__rough_linen"]
    assert linen["textured"] and linen["albedo_mode"] == "flat" and linen["detail"] == 0.5
    assert flat["materials"]["fabric_linen__rough_linen"]["rgb_to_bw"]
    assert m["plaster_white"]["albedo_mode"] == "flat"
    from wenart.blender import materials as M
    assert M.procedural_for("tiles_light", False, False) is None                 # --no-textures (see w_L1_006)
    assert M.procedural_for("tiles_light", True, True) is None and M.procedural_for("marble", False, True) is None


@needs_blender
def test_row5_hall_light_inside_the_l(hall):
    light = hall["objects"]["light_r_hall"]
    plan = lighting.area_light_plan(L_HALL)
    assert light["location"][:2] == pytest.approx(plan["center"], abs=1e-4)
    assert light["size"] == pytest.approx(plan["size"]) and _square_inside(plan, L_HALL)
    assert light["location"][2] == pytest.approx(2.7 - lighting.AREA_LIGHT_CEILING_GAP)
    assert light["energy"] == pytest.approx(12.0 * 8.32) and light["visible_camera"] is False
    entry = next(o for o in hall["manifest"]["objects"] if o["name"] == "light_r_hall")
    assert entry["assumed"]["reason"] == "room has no window" and entry["parent"] == "r_hall"
    assert hall["objects"]["light_r_st"]["energy"] == pytest.approx(12.0 * 1.9 * 1.8)


@needs_blender
def test_row6_dim_bedroom_gets_a_half_power_light(flat):
    light = flat["objects"]["light_r_bed"]
    assert light["energy"] == pytest.approx(6.0 * 12.0) and light["visible_camera"] is False
    assert light["location"][:2] == pytest.approx([2.0, 1.5])
    assert "light_r_kit" not in flat["objects"]                       # 2.24 m2 of window for 10.5 m2: daylight
    (entry,) = [a for a in flat["manifest"]["assumed"] if a.get("kind") == "dim_room_light"]
    assert entry["parent"] == "r_bed" and "0.060 < 0.08" in entry["reason"] and entry["value"] == pytest.approx(72.0)
    obj = next(o for o in flat["manifest"]["objects"] if o["name"] == "light_r_bed")
    assert obj["assumed"]["w_per_m2"] == 6.0 and obj["assumed"]["window_floor_ratio"] == pytest.approx(0.06)


@needs_blender
def test_row8_bed_bevel_veneer_and_metal(flat):
    def flat_list(bounds):
        return [v for pair in bounds for v in pair]

    bed = flat["objects"]["furn_f_bed"]
    assert flat_list(bed["bounds"]) == pytest.approx([1.2, 2.8, 0.95, 2.95, 0.0, 1.0], abs=1e-6)
    assert flat_list(bed["eval_bounds"]) == pytest.approx(flat_list(bed["bounds"]), abs=1e-4)   # bevel cuts inwards
    (mod,) = bed["modifiers"]
    assert mod == {"type": "BEVEL", "width": pytest.approx(0.05), "segments": 3, "limit": "WEIGHT", "harden": True}
    assert 0 < max(bed["bevel_weights"]) <= 1.0
    assert "wood_veneer_oak__oak_veneer_01" in bed["materials"] and "fabric_white__rough_linen" in bed["materials"]
    assert "fabric_linen__rough_linen" in bed["materials"]                        # the duvet
    m = flat["manifest"]["materials"]
    assert m["wood_veneer_oak__oak_veneer_01"]["textured"] and m["wood_veneer_oak__oak_veneer_01"]["size_m"] == [
        1.83, 1.83]
    counter = flat["objects"]["furn_f_counter"]
    steel = [name for name in counter["materials"] if name.startswith("steel_brushed")]
    assert steel and all(flat["materials"][name]["metallic"] == 1.0 for name in steel)
    assert flat_list(counter["eval_bounds"]) == pytest.approx(flat_list(counter["bounds"]), abs=1e-4)
    # The cushion lies on the bedding, not inside the pillows.
    cushion = flat["objects"]["decor_f_bed_1"]
    assert cushion["bounds"][2][0] == pytest.approx(round(P.bedding_top(1.6, 2.0, 0.55), 4), abs=1e-4)
    entry = next(o for o in flat["manifest"]["objects"] if o["name"] == "furn_f_bed")
    assert entry["bbox_m"] == [1.6, 2.0, 1.0] and entry["bevel"]["segments"] == 3


@needs_blender
def test_row9_door_veneer_handles_and_skirting(flat, hall):
    leaf = flat["objects"]["door_p_leaf"]
    assert leaf["materials"] == ["wood_veneer_oak__oak_veneer_01"]
    # Box UVs: on the leaf's big faces v runs with the height, so the veneer's grain (along v) is vertical.
    big = [f for f in leaf["faces"] if abs(f["normal"][0]) > 0.99]
    assert big and all(f["uv_max"][1] - f["uv_min"][1] == pytest.approx(f["max"][2] - f["min"][2], abs=1e-4)
                       for f in big)
    handle = flat["objects"]["door_p_handle"]
    assert handle["kind"] == "door" and handle["wenart_id"] == "door_p" and handle["status"] == "assumed"
    assert handle["pass_index"] == flat["manifest"]["pass_index"]["door_p"] == leaf["pass_index"]
    assert handle["materials"] == ["steel_brushed"]
    xs = [v[0] for v in handle["verts"]]
    ys = [v[1] for v in handle["verts"]]
    lt = shell.DEFAULTS["leaf_thickness"]
    assert min(xs) < 4.05 - lt / 2 and max(xs) > 4.05 + lt / 2                      # both faces
    assert max(abs(x - 4.05) for x in xs) <= lt / 2 + shell.HANDLE_DEPTH + 1e-6      # door box + handle depth
    assert 1.05 <= min(ys) and max(ys) <= 1.95                                      # within the opening
    lever_z = [v[2] for v in handle["verts"] if abs(abs(v[0] - 4.05) - (lt / 2 + shell.HANDLE_DEPTH)) < 1e-6]
    assert lever_z and sum(lever_z) / len(lever_z) == pytest.approx(shell.HANDLE_HEIGHT, abs=1e-6)
    # Skirting along the dry bedroom only, interrupted at the door, inside the room.
    assert "skirting_r_bed" in flat["objects"] and "skirting_r_kit" not in flat["objects"]
    sk = flat["objects"]["skirting_r_bed"]
    assert sk["pass_index"] == 0 and sk["status"] == "assumed" and sk["kind"] == "wall"
    assert sk["materials"] == ["painted_wood_white"]
    for x, y, z in sk["verts"]:
        assert -1e-6 <= x <= 4.0 + 1e-6 and -1e-6 <= y <= 3.0 + 1e-6 and -1e-6 <= z <= shell.SKIRTING_H + 1e-6
        assert not (x > 3.9 and 1.05 + 1e-6 < y < 1.95 - 1e-6)                    # the door gap
    hall_sk = hall["objects"]["skirting_r_hall"]
    assert not any(3.05 + 1e-6 < x < 3.95 - 1e-6 and y < 0.1 for x, y, _ in hall_sk["verts"])   # entrance gap
    assert not any(x < 1.6 + 1e-6 and x > 1.5 and 1.85 + 1e-6 < y < 2.55 - 1e-6 for x, y, _ in hall_sk["verts"])
    store_sk = hall["objects"]["skirting_r_st"]                                # a storage room is dry
    assert not any(x < 1.75 and 1.85 + 1e-6 < y < 2.55 - 1e-6 for x, y, _ in store_sk["verts"])


@needs_blender
def test_assumed_entries_of_every_design_detail(flat, hall):
    """One entry per bedding set, counter-front set, door-handle pair, skirting run and dim-room light,
    each with parent, kind and reason; none of them is an element of the building."""
    entries = [a for a in flat["manifest"]["assumed"] if "kind" in a]
    by_kind = {}
    for a in entries:
        assert a["parent"] and a["reason"] and a["object"] and "value" in a, a
        by_kind.setdefault(a["kind"], []).append(a["parent"])
    assert by_kind == {"bedding": ["f_bed"], "counter_fronts": ["f_counter"], "door_handles": ["door_p"],
                       "skirting": ["r_bed"], "dim_room_light": ["r_bed"]}
    hall_kinds = sorted((a["kind"], a["parent"]) for a in hall["manifest"]["assumed"] if "kind" in a)
    assert hall_kinds == [("door_handles", "d_in"), ("door_handles", "d_st"), ("skirting", "r_hall"),
                          ("skirting", "r_st"), ("windowless_room_light", "r_hall"),
                          ("windowless_room_light", "r_st")]
    building = json.loads(flat["path"].read_text(encoding="utf-8"))
    assert building == flat_building()                                   # nothing written back
    element_ids = {f["id"] for f in building["furniture"]} | {o["id"] for o in building["openings"]} | \
        {w["id"] for w in building["walls"]}
    details = [o for o in flat["manifest"]["objects"] if o.get("parent")]
    assert details and all(o["status"] == "assumed" for o in details)
    assert not {o["name"] for o in details} & element_ids


# ==========================================================================
# Blender: renders (window pull, alt look, passes, stripes, flags, deadline)
# ==========================================================================

PULL_SCRIPT = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    from pathlib import Path
    import numpy as np
    import OpenImageIO as oiio
    from wenart import views
    from wenart.blender import render as R
    spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
    out = Path(spec["out"])
    code = R.main(["--out", str(out), "--cameras", spec["camera"], "--samples", "8", "--res", "128x72",
                   "--device", "cpu", "--alt-look", "None", "--preview-quality", "85"])
    res = {"code": code}
    scene = bpy.context.scene
    result = bpy.data.images["Render Result"]
    entry = json.load(open(out / "render_manifest.json"))["renders"][0]
    ev = entry["exposure"]["ev"]
    channels = R.read_exr(out / entry["exr"])
    res["channels"] = sorted(channels)
    products = R.pass_products(channels)
    albedo = R.find_rgb(channels, "Diffuse Color", "DiffCol")
    mask = R.pane_mask(products["index"], albedo, R.window_indices(scene))
    weights = R.feather_weights(mask)
    res["mask_px"] = int(mask.sum())
    tmp = out / "check.png"
    plain = R.save_display(scene, result, tmp, ev)
    final = R.read_display_png(out / entry["png"])
    outside = weights == 0
    res["outside_max_diff"] = int(np.abs(final[outside].astype(int) - plain[outside].astype(int)).max())
    res["inside_changed"] = int((final[mask] != plain[mask]).any(axis=-1).sum())
    pull = entry["window_pull"]
    if pull and pull["k"]:
        pulled = R.save_display(scene, result, tmp, ev - pull["k"])
        res["final_is_blend"] = bool(np.array_equal(R.blend_pull(plain, pulled, weights), final))
        res["clip_after"] = R.clip_share(final, mask)
    # Alt look (M7: None, the old default): outside the mask (grown by two JPEG blocks) the alt preview
    # equals a plain alt-look save.
    vs = scene.view_settings
    res["main_look"] = vs.look
    vs.look, vs.exposure = "None", ev
    R.save_preview(scene, result, out / "plain_alt.jpg", 85)
    vs.look = R.LOOK
    def jpeg(p):
        return np.asarray(oiio.ImageBuf(str(p)).get_pixels(oiio.UINT8))[:, :, :3].astype(int)
    alt, plain_alt = jpeg(out / entry["alt_preview"]), jpeg(out / "plain_alt.jpg")
    far = views.erode(~mask, 24)
    res["alt_far_max_diff"] = int(np.abs(alt[far] - plain_alt[far]).max())
    res["alt_mask_diff"] = float(np.abs(alt[mask] - plain_alt[mask]).mean()) if mask.any() else 0.0
    res["alt_vs_main_far_diff"] = float(np.abs(alt[far] - jpeg(out / entry["preview"])[far]).mean())
    # The M5 pass set (no Diffuse Color): every other pass is the same.
    scene.view_layers[0].use_pass_diffuse_color = False
    R.set_output(scene, "OPEN_EXR_MULTILAYER")
    scene.render.filepath = str(out / "m5_passes.exr")
    bpy.ops.render.render(write_still=True)
    m5 = R.read_exr(out / "m5_passes.exr")
    res["m5_channels"] = sorted(m5)
    res["pass_max_diff"] = max(float(np.abs(channels[n] - m5[n]).max()) for n in m5)
    json.dump(res, open(spec["result"], "w"))
""")


@pytest.fixture(scope="module")
def pulled(flat):
    tmp = flat["tmp"]
    out = tmp / "pull"
    spec = tmp / "pull_spec.json"
    spec.write_text(json.dumps({"out": str(out), "camera": KITCHEN_CAM, "result": str(tmp / "pull.json")}),
                    encoding="utf-8")
    (tmp / "pull.py").write_text(PULL_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "pull.py", [str(spec)], blend=str(flat["scene"] / "scene.blend"), timeout=900,
                    log_path=tmp / "pull.log")
    result = json.loads((tmp / "pull.json").read_text(encoding="utf-8"))
    manifest = json.loads((out / "render_manifest.json").read_text(encoding="utf-8"))
    return {"out": out, "result": result, "manifest": manifest, "entry": manifest["renders"][0]}


@needs_blender
def test_row7_window_pull_changes_only_the_panes(pulled):
    r, e = pulled["result"], pulled["entry"]
    assert r["code"] == 0
    schemas.validate_render_manifest(pulled["manifest"])
    pull = e["window_pull"]
    assert pull is not None and r["mask_px"] == pull["pane_px"] > 50
    assert pull["k"] in (1, 2, 3, 4) and pull["ev"] == -pull["k"] and pull["pane_ev"] == pytest.approx(
        e["exposure"]["ev"] - pull["k"])
    assert pull["clip_after"] <= pull["clip_before"] and pull["clip_after"] == r["clip_after"]
    assert pull["rule"] and pull["tried"][-1]["k"] == pull["k"] or pull["rule"].startswith("lowest")
    assert r["outside_max_diff"] == 0 and r["inside_changed"] > 0             # pixels outside the mask unchanged
    assert r["final_is_blend"]
    assert pulled["manifest"]["render_code_version"] == "m7.1" and pulled["manifest"]["look"] == "AgX - Punchy"
    assert r["main_look"] == R.LOOK == "AgX - Punchy"                         # the pull saved with the main look
    assert e["exposure"]["window_clip_frac"] is not None and e["exposure"]["ev_offset"] == 0.0


@needs_blender
def test_row7_exr_gains_the_diffuse_color_layer_only(pulled):
    r = pulled["result"]
    added = sorted(set(r["channels"]) - set(r["m5_channels"]))
    assert added == ["ViewLayer.Diffuse Color.B", "ViewLayer.Diffuse Color.G", "ViewLayer.Diffuse Color.R"]
    assert r["pass_max_diff"] == 0.0                                         # Combined, depth, normal, index: same


@needs_blender
def test_row10_alt_preview_has_the_same_pull(pulled):
    r, e = pulled["result"], pulled["entry"]
    assert e["alt_preview"] == f"{KITCHEN_CAM}_alt_preview.jpg" and (pulled["out"] / e["alt_preview"]).is_file()
    assert e["alt_preview_bytes"] == (pulled["out"] / e["alt_preview"]).stat().st_size
    assert pulled["manifest"]["alt_look"] == "None" and pulled["manifest"]["preview_quality"] == 85
    assert r["alt_far_max_diff"] == 0                                        # outside the mask: a plain alt save
    assert r["alt_mask_diff"] > 1.0                                          # the panes are pulled
    assert r["alt_vs_main_far_diff"] > 0.5                                   # another look than the main preview


@needs_blender
def test_row11_control_flags_reach_the_manifest_and_the_look(flat, pulled, tmp_path):
    source = pulled["out"] / "render_manifest.json"
    path = cli.render(flat["scene"] / "scene.blend", tmp_path / "ctl", cameras=KITCHEN_CAM, samples=2, res="32x18",
                      device="cpu", look_from=source, max_bounces=0, no_denoise=True, ev_offset=0.3,
                      preview_quality=85)
    m = json.loads(path.read_text(encoding="utf-8"))
    schemas.validate_render_manifest(m)
    (e,) = m["renders"]
    assert m["max_bounces"] == 0 and m["ev_offset"] == 0.3 and m["preview_quality"] == 85 and m["denoiser"] is None
    assert e["exposure"]["mode"] == "from" and e["exposure"]["ev_offset"] == 0.3
    assert e["exposure"]["ev"] == pytest.approx(pulled["entry"]["exposure"]["ev"] + 0.3)
    assert e["render_key"] != pulled["entry"]["render_key"] and e["alt_preview"] is None
    with Image.open(tmp_path / "ctl" / e["preview"]) as im:
        assert im.format == "JPEG" and im.size == (32, 18)
    for bad in (["--alt-look", "No Such Look"], ["--preview-quality", "0"], ["--max-bounces", "-2"]):
        assert cli.main(["render", "--scene", str(flat["scene"] / "scene.blend"), "--out", str(tmp_path / "bad"),
                         "--cameras", KITCHEN_CAM, "--res", "16x9", "--samples", "1", "--device", "cpu", *bad]) == 2


@needs_blender
def test_row11_max_bounces_0_keeps_the_sky_in_the_window_panes(flat, pulled, tmp_path):
    # Review L1: the ctl_direct render (--max-bounces 0, the look of the normal render) must differ from the
    # normal one by its lighting only. With Cycles max_bounces = 0 the panes were pitch black (pane median 0,
    # no pull); now they keep the sky while the walls get direct light only (darker than the normal render).
    normal = pulled["entry"]["window_pull"]
    path = cli.render(flat["scene"] / "scene.blend", tmp_path / "direct", cameras=KITCHEN_CAM, samples=8,
                      res="128x72", device="cpu", look_from=pulled["out"] / "render_manifest.json", max_bounces=0,
                      preview_quality=85)
    m = json.loads(path.read_text(encoding="utf-8"))
    schemas.validate_render_manifest(m)
    assert m["max_bounces"] == 0 and m["bounces"] == R.bounce_settings(0)
    pull = m["renders"][0]["window_pull"]
    assert pull is not None and pull["pane_px"] > 50
    assert pull["pane_median"] > 0.5 * normal["pane_median"] > 0.1
    assert pull["wall_median"] < normal["wall_median"]                      # no bounce light on the walls


@needs_blender
def test_row12_render_stops_at_the_deadline(flat, pulled, tmp_path, monkeypatch):
    monkeypatch.setenv("WENART_DEADLINE", str(time.time() - 5))
    out = tmp_path / "late"
    argv = ["render", "--scene", str(flat["scene"] / "scene.blend"), "--out", str(out), "--cameras",
            f"{KITCHEN_CAM},cam_r_kit_2", "--res", "16x9", "--samples", "1", "--device", "cpu"]
    assert cli.main(argv) == 3
    m = json.loads((out / "render_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_render_manifest(m)
    assert m["incomplete"] is True and m["not_rendered"] == [KITCHEN_CAM, "cam_r_kit_2"] and m["renders"] == []
    assert m["deadline"] < time.time() and any("WENART_DEADLINE" in w for w in m["warnings"])
    assert not list(out.glob("*.png"))
    with pytest.raises(cli.BlenderFailed) as err:
        cli.render(flat["scene"] / "scene.blend", out, cameras=KITCHEN_CAM, res="16x9", samples=1, device="cpu")
    assert err.value.returncode == 3
    # Cameras whose files can be reused still count: nothing new to render, so the run is complete.
    path = cli.render(flat["scene"] / "scene.blend", pulled["out"], cameras=KITCHEN_CAM, samples=8, res="128x72",
                      device="cpu", alt_look="None", preview_quality=85)
    m = json.loads(path.read_text(encoding="utf-8"))
    assert m["incomplete"] is False and m["renders"][0]["skipped"] is True and m["not_rendered"] == []
    monkeypatch.setenv("WENART_DEADLINE", "not a time")
    path = cli.render(flat["scene"] / "scene.blend", tmp_path / "ignored", cameras=KITCHEN_CAM, samples=1,
                      res="16x9", device="cpu")
    assert json.loads(path.read_text(encoding="utf-8"))["incomplete"] is False
    assert "ignored" in (tmp_path / "ignored" / "render.log").read_text(encoding="utf-8")


STRIPES_SCRIPT = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, os.environ["WENART_REPO_ROOT"])
    from pathlib import Path
    import numpy as np
    from wenart.blender import materials as M
    from wenart.blender import render as R
    spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
    out = Path(spec["out"])
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.camera = bpy.data.objects[spec["camera"]]
    R.configure_device(scene, "cpu")
    R.configure_render(scene, 16, (96, 54), "CPU", False)
    nodes = [m.node_tree.nodes[M.STRIPES_CAMERA_NODE] for m in bpy.data.materials
             if m.node_tree and m.node_tree.nodes.get(M.STRIPES_CAMERA_NODE)]

    def render(name):
        R.set_output(scene, "OPEN_EXR_MULTILAYER")
        scene.render.filepath = str(out / f"{name}.exr")
        bpy.ops.render.render(write_still=True)
        return R.read_exr(out / f"{name}.exr")

    as_built = render("as_built")
    for n in nodes:                                   # no stripes at all
        n.inputs[1].links and n.id_data.links.remove(n.inputs[1].links[0])
        n.inputs[1].default_value = 0.0
    none = render("none")
    for n in nodes:                                   # Milestone 5: stripes for every ray
        n.inputs[1].default_value = 1.0
    every = render("every")
    rgb = lambda ch: R.find_rgb(ch, "Combined")
    idx = np.rint(R.find_channel(as_built, "Object Index.X"))
    nz = R.find_channel(as_built, "Normal.Z")
    depth = R.find_channel(as_built, "Depth.Z")
    piece = idx == spec["index"]
    # Wall pixels 3 px or more from the piece: the pixel filter sends some samples of the pixels
    # next to it onto the (camera-visible) stripes.
    from wenart import views
    wall = (idx == 0) & (np.abs(nz) < 0.3) & (depth < 1e9) & views.erode(~piece, 3)
    a, n0, e = rgb(as_built), rgb(none), rgb(every)
    red = lambda img: ((img[..., 0] > 2 * img[..., 1]) & (img[..., 0] > 2 * img[..., 2]) & piece).sum()
    json.dump({"nodes": len(nodes), "wall_px": int(wall.sum()), "piece_px": int(piece.sum()),
               "wall_diff_as_built": float(np.abs(a[wall] - n0[wall]).max()),
               "wall_red_ratio_every": float(e[wall][:, 0].mean() / n0[wall][:, 0].mean()),
               "wall_rg_every": float((e[wall][:, 0] / np.maximum(e[wall][:, 1], 1e-6)).mean()),
               "wall_rg_none": float((n0[wall][:, 0] / np.maximum(n0[wall][:, 1], 1e-6)).mean()),
               "red_px_as_built": int(red(a)), "red_px_none": int(red(n0))}, open(spec["result"], "w"))
""")


@needs_blender
def test_row1_stripes_stay_visible_and_light_nothing(hall):
    """A small windowless storage room with an unverified wardrobe: the wall pixels are the same as without
    stripes, the stripes are still on the wardrobe; Milestone 5's stripes (every ray) turned the walls red."""
    tmp = hall["tmp"]
    spec = tmp / "stripes_spec.json"
    spec.write_text(json.dumps({"out": str(tmp / "stripes"), "camera": STORE_CAM, "result": str(tmp / "stripes.json"),
                                "index": hall["manifest"]["pass_index"]["f_wardrobe"]}), encoding="utf-8")
    (tmp / "stripes.py").write_text(STRIPES_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "stripes.py", [str(spec)], blend=str(hall["scene"] / "scene.blend"), timeout=900)
    r = json.loads((tmp / "stripes.json").read_text(encoding="utf-8"))
    assert r["nodes"] >= 1 and r["wall_px"] > 300 and r["piece_px"] > 300
    assert r["wall_diff_as_built"] == 0.0                                     # walls neutral: no red light
    assert r["wall_red_ratio_every"] > 1.02 and r["wall_rg_every"] > r["wall_rg_none"]
    assert r["red_px_as_built"] > 0.1 * r["piece_px"] and r["red_px_none"] == 0
