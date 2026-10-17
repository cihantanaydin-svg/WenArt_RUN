"""Milestone 13 track T2 GPU test (docs/milestone13.md §13.1, pod P1): the module builders and the parametric
families v2 built in Blender.

Runs on the pod (``pytest -m gpu tests/gpu/test_m13_modules.py``; skipped without a Blender binary): one piece per
module builder (``wenart.blender.modules.MODULE_BUILDERS``, its ``asset.method == "module"`` with the plan the fit
would store) and one per family (``parametric.FAMILY_TYPES``) in one room, built by the real build script
(``wenart/blender/build.py``) with the style of tests/fixtures/blender_style.json and no textures. Checks, per
built object: at least two material slots, a Bevel modifier (the one ``furniture.add_bevel`` adds; limit method
WEIGHT) or bevelled geometry, and a bounding box equal to the plan's (``modules.plan_bbox``) or the family's
(``parametric.parts_bbox``) box within 1.1 cm; the manifest counts the module pieces under ``by_method.module``
and records ``module`` (builder, products, fit) on their entries. Round 4: the chair family v2 is built in its
default look and in three design variants (``CHAIR_VARIANTS``: sled, wooden seat, rattan seat), each with one
material slot per part key.

Fix round after P3 (16-17 Oct 2026): a second scene (``KITCHEN_DOORS``) checks in Blender what the CPU tests check
on the pure parts: a kitchen run with a drawn sink built into it (no object of its own, the run's manifest entry
names it) and a drawn stove in a gap of the run (a ray down onto the gap meets the stove, not the worktop; scene
check S2 has no finding), and the door stops (rays across the wall through the old 5 mm slit at the jambs, the
head and the meeting stiles meet the door, for the Milestone 6 swing door and a Milestone 10 double door; P3's
cam_r_L1_koridor_2_2 saw the terrace through that slit).
"""
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

import pytest

from wenart.blender import cli
from wenart.blender import modules as M
from wenart.blender import parametric as P
from wenart.blender.proxies import proxy_height
from wenart.furniture import schemas as SC

pytestmark = pytest.mark.gpu
if cli.find_blender() is None:
    # Skipped at import on a CPU machine (as tests/gpu/test_look_m6.py and test_generate.py do): pytest keys test
    # modules by basename here (no test packages), so the CPU twin tests/test_m13_modules.py of docs/milestone13.md
    # §13.1 can only be collected when this module is not; the pods run `pytest -m gpu tests/gpu/<file>` explicitly.
    pytest.skip("no Blender binary (WENART_BLENDER, /workspace/tools/blender, /opt/wenart/blender)",
                allow_module_level=True)

ROOT = Path(__file__).resolve().parents[2]
STYLE = ROOT / "tests" / "fixtures" / "blender_style.json"
TOL_M = 0.011                  # handles stand 8 mm proud of a front (parametric.PROUD)

DUMP_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.name.startswith("furn_"):
            continue
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        rows[ob.name] = {
            "wenart_id": ob.get("wenart_id"), "method": ob.get("wenart_method"), "module": ob.get("wenart_module"),
            "type": ob.get("wenart_type"), "asset": ob.get("wenart_asset"),
            "slots": [m.name if m else None for m in ob.data.materials],
            "modifiers": [(m.name, m.type, getattr(m, "limit_method", None), getattr(m, "segments", None),
                           getattr(m, "width", None)) for m in ob.modifiers],
            "bevel_weights": int(sum(1 for v in ob.data.attributes["bevel_weight_edge"].data if v.value > 0))
                             if "bevel_weight_edge" in ob.data.attributes else 0,
            "bounds": [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)],
            "smooth_faces": sum(1 for p in ob.data.polygons if p.use_smooth),
        }
    json.dump(rows, open(out, "w"))
""")


def _piece(pid, ftype, center, size, **extra):
    piece = {"id": pid, "type": ftype, "level_id": "L0", "room_id": "r_L0_hall", "source": "from_documents",
             "status": "verified", "footprint": {"center": list(center), "size": list(size), "rotation_deg": 0.0},
             "front_deg": 270.0, "height": None, "asset": None,
             "evidence": [{"file": "plan.dxf", "method": "vector", "confidence": 1.0}]}
    piece.update(extra)
    return piece


# Round 4 (§14.8): the chair family v2 in its design variants besides the default one of FAMILY_TYPES (a wooden frame
# with an upholstered pad): a steel sled base, a wooden seat, a rattan seat.
CHAIR_VARIANTS = [["metal"], ["wood"], ["rattan", "wood"]]

MODULE_PIECES = [
    ("wardrobe", (3.11, 0.6), {}), ("table_dining", (2.3, 1.6), {}),
    ("sofa_corner", (3.2, 2.2), {"shape": "L", "chaise_side": "left", "chaise_depth": 2.2}),
    ("kitchen_counter", (3.0, 0.6), {"module_hints": {"sink_x_m": 0.6, "hob_x_m": -0.9, "wall_units": True}}),
    ("kitchen_island", (2.13, 0.9), {}), ("washbasin", (1.0, 0.55), {}), ("shower", (1.2, 0.8), {}),
]


def _building() -> dict:
    W, D, t = 16.0, 12.0, 0.25
    ev = [{"file": "plan.dxf", "method": "vector", "confidence": 1.0}]
    walls = [{"id": "w_s", "start": [-t, -t / 2], "end": [W + t, -t / 2]},
             {"id": "w_e", "start": [W + t / 2, -t], "end": [W + t / 2, D + t]},
             {"id": "w_n", "start": [W + t, D + t / 2], "end": [-t, D + t / 2]},
             {"id": "w_w", "start": [-t / 2, D + t], "end": [-t / 2, -t]}]
    walls = [dict(w, level_id="L0", thickness=t, status="verified", evidence=ev, exterior=True) for w in walls]
    room = {"id": "r_L0_hall", "level_id": "L0", "label": "hall", "room_type": "living",
            "polygon": [[0, 0], [W, 0], [W, D], [0, D]], "area_computed": W * D, "status": "verified",
            "has_documented_furniture": True, "evidence": ev}
    furniture, plans = [], {}
    x, y = 2.0, 1.6
    for i, (ftype, size, extra) in enumerate(MODULE_PIECES):
        piece = _piece(f"m_{i:02d}", ftype, (x, y), size, **extra)
        plan = M.module_plan(piece)
        assert plan is not None, ftype
        piece["asset"] = {"method": "module", "library": "module",
                          "asset_id": f"module:{ftype}:{plan['builder']}",       # fit.module_fit's spelling
                          "licence": "ours", "module_plan": plan, "fit_scale": [1.0, 1.0, 1.0],
                          "bbox_m": list(M.plan_bbox(plan))}
        furniture.append(piece)
        plans[piece["id"]] = plan
        x += size[0] + 0.8
        if x > W - 3.0:
            x, y = 2.0, y + 3.0
    x, y = 2.0, y + 3.2
    for i, ftype in enumerate(P.FAMILY_TYPES):
        size = SC.SIZE_OPTIONS[ftype][SC.DEFAULT_SIZE_INDEX] if ftype in SC.SIZE_OPTIONS else (1.4, 2.0)
        if x + size[0] > W - 1.0:
            x, y = 2.0, y + 2.8
        furniture.append(_piece(f"p_{i:02d}", ftype, (x + size[0] / 2.0, y), size))
        x += size[0] + 0.6
    for i, tags in enumerate(CHAIR_VARIANTS):
        size = SC.SIZE_OPTIONS["chair"][SC.DEFAULT_SIZE_INDEX]
        if x + size[0] > W - 1.0:
            x, y = 2.0, y + 2.8
        furniture.append(_piece(f"c_{i:02d}", "chair", (x + size[0] / 2.0, y), size,
                                design={"material_tags": list(tags)}))
        x += size[0] + 0.6
    return {"schema_version": "0.1", "status": "ok", "project": {"id": "m13-modules-test"},
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls, "openings": [],
            "rooms": [room], "furniture": furniture, "decor": [], "warnings": [], "unverified": []}, plans


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    pytest.importorskip("jsonschema")
    if cli.find_blender() is None:
        pytest.skip("no Blender binary (WENART_BLENDER, /workspace/tools/blender, /opt/wenart/blender)")
    tmp = tmp_path_factory.mktemp("m13_modules")
    building, plans = _building()
    path = tmp / "building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    (tmp / "assets").mkdir()
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--style", str(STYLE), "--assets",
                                             str(tmp / "assets"), "--out", str(out), "--no-textures", "--no-preview",
                                             "--no-glb"], log_path=out / "build.log")
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    (tmp / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(tmp / "dump.json")], blend=str(out / "scene.blend"))
    dump = json.loads((tmp / "dump.json").read_text(encoding="utf-8"))
    return {"building": building, "plans": plans, "manifest": manifest, "objects": dump}


def _extent(bounds):
    return tuple(hi - lo for lo, hi in bounds)


def _bevel_ok(row: dict) -> bool:
    """A Bevel modifier with weight-limited edges (``furniture.add_bevel``), or bevelled geometry (smooth faces of
    the rounded cushions and cloth)."""
    bevels = [m for m in row["modifiers"] if m[1] == "BEVEL"]
    if bevels and row["bevel_weights"] > 0:
        return True
    return row["smooth_faces"] > 0


def test_manifest_counts_the_module_pieces(built):
    from wenart.blender import schemas

    m = built["manifest"]
    schemas.validate_scene_manifest(m)
    assert m["furniture"]["by_method"].get("module") == len(MODULE_PIECES)
    assert m["furniture"]["by_method"].get("parametric") == len(P.FAMILY_TYPES) + len(CHAIR_VARIANTS)
    assert not [w for w in m["warnings"] if "parametric family used" in w or "module build failed" in w]
    entries = {o["element_id"]: o for o in m["objects"] if o["kind"] == "furniture"}
    for pid, plan in built["plans"].items():
        e = entries[pid]
        assert e["method"] == "module" and e["fallback_reason"] is None
        assert e["module"]["builder"] == plan["builder"] and e["module"]["products"] == plan["products"]
        assert e["module"]["fit"]["within_cap"] and e["bevel"] and e["bevel"]["edges"] > 0
        assert len(e["materials"]) >= 2 and set(e["material_keys"]) == set(M.material_keys(plan))
        assert "modules" in e["assumed"]
    details = [a for a in m["assumed"] if a.get("kind") == "modules"]
    assert {a["parent"] for a in details} == set(built["plans"])


def test_every_module_object_has_slots_a_bevel_and_the_plan_box(built):
    objects = built["objects"]
    for piece in built["building"]["furniture"]:
        if piece["id"] not in built["plans"]:
            continue
        plan = built["plans"][piece["id"]]
        row = objects[f"furn_{piece['id']}"]
        assert row["method"] == "module" and row["module"] == plan["builder"] and row["type"] == piece["type"]
        assert row["asset"] == f"module:{piece['type']}:{plan['builder']}"      # the fit's asset_id, one spelling
        assert len([s for s in row["slots"] if s]) >= 2, piece["id"]
        assert _bevel_ok(row) and any(mod[1] == "BEVEL" and mod[2] == "WEIGHT" for mod in row["modifiers"]), piece["id"]
        want = M.plan_bbox(plan)
        got = _extent(row["bounds"])
        assert got == pytest.approx(want, abs=TOL_M), (piece["id"], got, want)
        (x0, x1), (y0, y1), (z0, z1) = row["bounds"]
        c = piece["footprint"]["center"]
        assert ((x0 + x1) / 2.0, (y0 + y1) / 2.0) == pytest.approx(tuple(c), abs=TOL_M) and z0 == pytest.approx(0.0, abs=1e-4)


def test_every_family_object_has_slots_a_bevel_and_its_box(built):
    objects = built["objects"]
    for piece in built["building"]["furniture"]:
        if piece["id"] in built["plans"]:
            continue
        row = objects[f"furn_{piece['id']}"]
        assert row["method"] == "parametric" and row["asset"] == "parametric"
        assert len([s for s in row["slots"] if s]) >= 2, piece["type"]
        assert _bevel_ok(row) and any(mod[1] == "BEVEL" for mod in row["modifiers"]), piece["type"]
        w, d = piece["footprint"]["size"]
        h, _ = proxy_height(piece["type"], None)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(P.build_parts(piece["type"], w, d, h, piece=piece))
        want = (x1 - x0, y1 - y0, z1 - z0)
        got = _extent(row["bounds"])
        assert got == pytest.approx(want, abs=TOL_M), (piece["type"], got, want)
        assert math.isclose(row["bounds"][2][0], 0.0, abs_tol=1e-4)
        if piece["type"] == "chair":                 # round 4: the chair v2's slots are its design's keys
            keys = {p["key"] for p in P.build_parts("chair", w, d, h, piece=piece)}
            assert len([s for s in row["slots"] if s]) == len(keys) >= 2, (piece["id"], row["slots"], keys)


# --------------------------------------------------------------------------
# Fix round after P3: the kitchen run's built-in sink and stove gap, the door stops
# --------------------------------------------------------------------------

RAYS_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    from mathutils import Vector
    args = sys.argv[sys.argv.index("--") + 1:]
    rays = json.load(open(args[0]))
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    out = {}
    for name, r in rays.items():
        hit, loc, _n, _i, ob, _m = scene.ray_cast(depsgraph, Vector(r["origin"]), Vector(r["direction"]),
                                                  distance=r["distance"])
        out[name] = {"hit": bool(hit), "object": ob.name if hit and ob is not None else None,
                     "z": float(loc[2]) if hit else None}
    json.dump(out, open(args[1], "w"))
""")


def _kitchen_doors_building() -> tuple[dict, dict]:
    """An 8 x 6 m level split by an interior wall (x = 4.0, 0.1 m) with a swing door (the Milestone 6 door of the
    fixture style) and a double door (Milestone 10, drawn operation); in r_a a 2.4 m kitchen run with a drawn sink
    built into it and a drawn stove in its gap (the assets as fit.fit_building writes them)."""
    W, D, t = 8.0, 6.0, 0.25
    ev = [{"file": "plan.dxf", "method": "vector", "confidence": 1.0}]
    walls = [{"id": "w_s", "start": [-t, -t / 2], "end": [W + t, -t / 2]},
             {"id": "w_e", "start": [W + t / 2, -t], "end": [W + t / 2, D + t]},
             {"id": "w_n", "start": [W + t, D + t / 2], "end": [-t, D + t / 2]},
             {"id": "w_w", "start": [-t / 2, D + t], "end": [-t / 2, -t]}]
    walls = [dict(w, level_id="L0", thickness=t, status="verified", evidence=ev, exterior=True) for w in walls]
    walls.append({"id": "w_m", "start": [4.0, 0.0], "end": [4.0, D], "level_id": "L0", "thickness": 0.1,
                  "status": "verified", "evidence": ev, "exterior": False})
    rooms = [{"id": "r_a", "label": "kitchen", "room_type": "kitchen", "polygon": [[0, 0], [3.95, 0], [3.95, D], [0, D]]},
             {"id": "r_b", "label": "living", "room_type": "living", "polygon": [[4.05, 0], [W, 0], [W, D], [4.05, D]]}]
    rooms = [dict(r, level_id="L0", status="verified", evidence=ev, area_computed=1.0,
                  has_documented_furniture=True) for r in rooms]
    openings = [{"id": "d_swing", "type": "door", "wall_id": "w_m", "center": [4.0, 1.5], "width": 0.9, "height": 2.1,
                 "sill_height": 0.0, "operation": None, "swing_side": "r_b"},
                {"id": "d_double", "type": "door", "wall_id": "w_m", "center": [4.0, 4.0], "width": 1.3, "height": 2.1,
                 "sill_height": 0.0, "operation": "double", "operation_source": "block_name", "swing_side": "r_b"}]
    openings = [dict(o, level_id="L0", status="verified", evidence=ev) for o in openings]
    run = _piece("k_run", "kitchen_counter", (2.0, 3.0), (2.4, 0.6), room_id="r_a", height=0.9)
    sink = _piece("k_sink", "sink_kitchen", (1.2, 3.0), (0.8, 0.5), room_id="r_a")
    stove = _piece("k_stove", "stove", (2.75, 3.0), (0.6, 0.6), room_id="r_a")
    hints = {"sink_pos_m": [1.2, 3.0], "sink_w_m": 0.8, "sink_piece": "k_sink",
             "ranges": [dict(M.member_in_run(run, stove), id="k_stove", type="stove")]}
    plan = M.module_plan(dict(run, module_hints=hints))
    assert plan["built_ins"][0]["id"] == "k_sink" and plan["gaps"][0]["id"] == "k_stove"
    run["asset"] = {"method": "module", "library": "module", "asset_id": "module:kitchen_counter:kitchen_run",
                    "licence": "n/a", "module_plan": plan, "module_hints": hints, "fit_scale": [1.0, 1.0, 1.0],
                    "bbox_m": list(M.plan_bbox(plan)), "by_design": True}
    sink["asset"] = {"method": "module", "library": "module", "asset_id": "module:kitchen_counter:kitchen_run",
                     "licence": "n/a", "built_in": "k_run", "by_design": True, "fit_scale": [1.0, 1.0, 1.0],
                     "module_plan": {"builder": "kitchen_run", "built_into": "k_run", "kind": "sink"},
                     "bbox_m": [0.8, 0.5, 0.9]}
    stove["asset"] = {"method": "parametric", "library": "parametric", "asset_id": "parametric:stove", "licence": "n/a",
                      "fit_scale": [1.0, 1.0, 1.0], "bbox_m": [0.6, 0.6, 0.9], "by_design": True}
    building = {"schema_version": "0.1", "status": "ok", "project": {"id": "m13-kitchen-doors-test"},
                "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls,
                "openings": openings, "rooms": rooms, "furniture": [run, sink, stove], "decor": [], "warnings": [],
                "unverified": []}
    # rays across the interior wall (x = 4.0) through the old slits: jambs (5 mm; 6 mm for the double door), the
    # head (5 mm), the double door's meeting stiles; and down onto the stove gap and the sink unit
    across = {"direction": [1.0, 0.0, 0.0], "distance": 0.6}
    rays = {"swing_jamb_hi": dict(across, origin=[3.7, 1.5 + 0.4 - 0.0025, 1.2]),
            "swing_jamb_lo": dict(across, origin=[3.7, 1.5 - 0.4 + 0.0025, 1.2]),
            "swing_head": dict(across, origin=[3.7, 1.5, 2.1 - 0.05 - 0.0025]),
            "double_jamb": dict(across, origin=[3.7, 4.0 + 0.6 - 0.003, 1.2]),
            "double_meeting": dict(across, origin=[3.7, 4.0, 1.2]),
            "stove_gap": {"origin": [2.75, 3.0, 1.2], "direction": [0.0, 0.0, -1.0], "distance": 1.2},
            "sink_unit": {"origin": [1.2, 2.9, 1.2], "direction": [0.0, 0.0, -1.0], "distance": 1.2}}
    return building, rays


@pytest.fixture(scope="module")
def kitchen_doors(tmp_path_factory):
    pytest.importorskip("jsonschema")
    if cli.find_blender() is None:
        pytest.skip("no Blender binary (WENART_BLENDER, /workspace/tools/blender, /opt/wenart/blender)")
    tmp = tmp_path_factory.mktemp("m13_kitchen_doors")
    building, rays = _kitchen_doors_building()
    path = tmp / "building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    (tmp / "assets").mkdir()
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--style", str(STYLE), "--assets",
                                             str(tmp / "assets"), "--out", str(out), "--no-textures", "--no-preview",
                                             "--no-glb"], log_path=out / "build.log")
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    (tmp / "rays.py").write_text(RAYS_SCRIPT, encoding="utf-8")
    (tmp / "rays.json").write_text(json.dumps(rays), encoding="utf-8")
    cli.run_blender(tmp / "rays.py", [str(tmp / "rays.json"), str(tmp / "hits.json")], blend=str(out / "scene.blend"))
    (tmp / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(tmp / "dump.json")], blend=str(out / "scene.blend"))
    scene_checks = json.loads((out / "checks" / "scene_L0.json").read_text(encoding="utf-8"))
    return {"manifest": manifest, "hits": json.loads((tmp / "hits.json").read_text(encoding="utf-8")),
            "objects": json.loads((tmp / "dump.json").read_text(encoding="utf-8")), "scene_checks": scene_checks}


def test_the_built_in_sink_has_no_object_and_the_stove_stands_in_the_gap(kitchen_doors):
    objects, hits = kitchen_doors["objects"], kitchen_doors["hits"]
    assert "furn_k_run" in objects and "furn_k_stove" in objects and "furn_k_sink" not in objects
    entries = {o["element_id"]: o for o in kitchen_doors["manifest"]["objects"] if o["kind"] == "furniture"}
    assert "k_sink" not in entries and entries["k_run"]["built_ins"] == [{"id": "k_sink", "type": "sink_kitchen"}]
    assert entries["k_run"]["module"]["gaps"][0]["id"] == "k_stove"
    assert hits["stove_gap"]["object"] == "furn_k_stove"                 # no worktop over the stove
    assert hits["sink_unit"]["object"] == "furn_k_run"                   # the run's own sink unit
    s2 = [v for v in kitchen_doors["scene_checks"]["violations"] if v["check"] == "S2"]
    assert not s2, s2


def test_closed_doors_have_no_slit_to_see_through(kitchen_doors):
    hits = kitchen_doors["hits"]
    for name in ("swing_jamb_hi", "swing_jamb_lo", "swing_head"):
        assert hits[name]["hit"] and hits[name]["object"].startswith("d_swing_"), (name, hits[name])
    for name in ("double_jamb", "double_meeting"):
        assert hits[name]["hit"] and hits[name]["object"].startswith("d_double_"), (name, hits[name])
    entries = {o["name"]: o for o in kitchen_doors["manifest"]["objects"]}
    assert entries["d_double_leaf"]["door"]["stop_side"] in (1.0, -1.0) and "stop" in entries["d_double_leaf"]["door"]["parts"]
    rays = {r["opening_id"]: r for r in kitchen_doors["manifest"]["checks"]["door_rays"]}
    assert not rays["d_swing"]["hit"] and not rays["d_double"]["hit"]  # both still cut through their wall
