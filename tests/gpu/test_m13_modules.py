"""Milestone 13 track T2 GPU test (docs/milestone13.md §13.1, pod P1): the module builders and the parametric
families v2 built in Blender.

Runs on the pod (``pytest -m gpu tests/gpu/test_m13_modules.py``; skipped without a Blender binary): one piece per
module builder (``wenart.blender.modules.MODULE_BUILDERS``, its ``asset.method == "module"`` with the plan the fit
would store) and one per family (``parametric.FAMILY_TYPES``) in one room, built by the real build script
(``wenart/blender/build.py``) with the style of tests/fixtures/blender_style.json and no textures. Checks, per
built object: at least two material slots, a Bevel modifier (the one ``furniture.add_bevel`` adds; limit method
WEIGHT) or bevelled geometry, and a bounding box equal to the plan's (``modules.plan_bbox``) or the family's
(``parametric.parts_bbox``) box within 1.1 cm; the manifest counts the module pieces under ``by_method.module``
and records ``module`` (builder, products, fit) on their entries.
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
    assert m["furniture"]["by_method"].get("parametric") == len(P.FAMILY_TYPES)
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
