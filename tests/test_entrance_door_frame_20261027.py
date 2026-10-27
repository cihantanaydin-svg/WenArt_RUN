"""A library door fills its opening as a real product does (27 Oct 2026, user on real06's entrance at the top of the
steps: "correct the door": a narrow oak strip with a dark panel beside it in the opening).

Cause: the catalogue writes ``bbox_m`` in the piece frame (``catalog.oriented_bbox``: the model box turned by its front
axis) and ``furniture.fit_vertices`` builds in that frame, but ``opening_models.model_size`` (and the depth of
``opening_build``) swapped width and depth once more for a front along x. "Modern Single Door", whose audit put its
front along the leaf (-X: "a door has no front"), so passed as a 1.07 m leaf and was built turned 90 degrees, its 13 cm
edge stretched 6.1 times to the 0.80 m opening (fit scale 6.1 x 0.1 x 0.9); every door modelled with its face across x
was read 0.25 m wide and never used.

General rules under test: the box is read as the catalogue writes it; a door or window model deeper than wide has its
front turned to its leaf's face at load (``leaf_front``); the build refuses a fit that stretches a model's width and
height by very different factors (``opening_build.stretch_problem``); a one-leaf category takes no model wider than a
real leaf (``SINGLE_LEAF_MAX_M``; wider: the parametric door's side lights or D5's pair) and no model whose title names a
pair or a sliding system. CPU only."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart.blender import architect as AR
from wenart.blender import build as BB
from wenart.blender import furniture as F
from wenart.blender import opening_build as OB
from wenart.blender import opening_models as OM
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "wenart" / "furniture" / "catalog_library.json"
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"


def _door(i, title, box, front="-Y", status="keep", kind="door"):
    return {"id": f"m{i}", "type": kind, "title": title, "glb": f"m{i}.glb", "bbox_m": list(box), "front_axis": front,
            "up_axis": "+Z", "audit": {"status": status}, "licence_flag": "none", "textured": True,
            "styles": ["modern"]}


def _box_verts(x, y, z):
    """The corners of a model box ``x`` x ``y`` x ``z`` in its own frame (centred in x and y, bottom at 0)."""
    return [(sx * x / 2.0, sy * y / 2.0, sz * z) for sx in (-1, 1) for sy in (-1, 1) for sz in (0, 1)]


def test_the_box_is_read_in_the_piece_frame_the_catalogue_writes():
    # a front door modelled with its face across x (front +X): the catalogue's piece box is 1.00 m wide, 0.26 deep
    e = _door(1, "Front Door", [1.0, 0.2553, 2.1], front="+X")
    assert OM.model_size(e) == (1.0, 0.2553, 2.1)
    assert OM.fit(e, "door", 0.95, 2.1) is not None                        # usable now (read 0.26 m wide before)


def test_a_door_whose_front_runs_along_its_leaf_is_turned_to_its_face():
    wrong = _door(2, "Modern Single Door", [0.1302, 1.0668, 2.4384], front="-X")
    fixed = OM.leaf_front(wrong)
    assert fixed["front_axis"] == "-Y" and fixed["bbox_m"] == [1.0668, 0.1302, 2.4384]
    assert fixed["front_axis_fixed"]["was"] == "-X" and "along the leaf" in fixed["front_axis_fixed"]["reason"]
    assert wrong["front_axis"] == "-X"                                     # pure: the entry itself is not changed
    right = _door(3, "Front Door", [1.0, 0.25, 2.1], front="+X")
    assert OM.leaf_front(right) is right
    sofa = dict(_door(4, "Sofa", [0.9, 2.0, 0.8]), type="sofa")
    assert OM.leaf_front(sofa) is sofa                                     # only doors and windows
    # built with the turned front, the leaf stands across the opening at its own proportions
    raw = _box_verts(1.0668, 0.1302, 2.4384)                               # the GLB: leaf along x, face across y
    _w, info = F.fit_vertices(raw, fixed, {"center": [0, 0], "size": [0.8, 0.105], "rotation_deg": 0.0}, 0.0,
                              target_size=[0.8, 0.105, 2.1])
    sx, sy, sz = info["fit_scale"]
    assert info["bbox_raw_m"][0] == pytest.approx(1.0668) and abs(math.log(sx / sz)) < 0.2
    # with the audit's front the same fit turned the leaf and stretched its edge (the render's oak strip)
    _w, bad = F.fit_vertices(raw, wrong, {"center": [0, 0], "size": [0.8, 0.105], "rotation_deg": 0.0}, 0.0,
                             target_size=[0.8, 0.105, 2.1])
    assert bad["fit_scale"][0] > 6.0 and bad["fit_scale"][1] < 0.11


def test_the_build_refuses_a_model_stretched_out_of_its_proportions():
    assert OB.stretch_problem([1.0668, 0.1302, 2.4384], 0.8, 2.1) is None
    assert "deeper" in OB.stretch_problem([0.1302, 1.0668, 2.4384], 0.8, 2.1)
    assert "stretched" in OB.stretch_problem([1.0, 0.1, 2.1], 2.0, 2.1)        # twice as wide, as high
    assert OB.stretch_problem([0.9, 0.14, 1.5], 0.6759 / 1.0, 1.2) is None      # a window's usual fit


def test_one_leaf_takes_no_model_wider_than_a_real_leaf_nor_a_pair_or_a_slide():
    e = _door(5, "Front Door", [1.2, 0.1, 2.1])
    assert OM.fit(e, "entrance", 1.2, 2.1) is not None
    assert OM.fit(e, "entrance", 1.3, 2.1) is None                          # past SINGLE_LEAF_MAX_M: no one leaf
    assert OM.fit(dict(e, type="window"), "window", 1.3, 2.1) is not None    # windows take panels as before
    extras = [_door(6, "Double Lift Slide Door", [1.0, 0.44, 2.5]), _door(7, "Duble Front Door", [1.0, 0.1, 2.1]),
              _door(8, "Front Door", [1.0, 0.1, 2.1])]
    for cat in ("entrance", "door"):
        assert [x["id"] for x in OM.candidates(extras, cat, "relaxed")] == ["m8"]


def test_the_repository_catalogue_has_no_door_or_window_deeper_than_wide_once_loaded():
    extras = OM.load_extras(CATALOGUE)
    if not extras:
        pytest.skip("no extras in the catalogue")
    openings = [e for e in extras if e.get("type") in ("door", "window") and e.get("bbox_m")]
    assert all(float(e["bbox_m"][0]) >= float(e["bbox_m"][1]) for e in openings)
    single = next((e for e in extras if e.get("id") == "3dwh_54d07ce98f9345c95081fc1e"), None)
    if single is not None:                                                  # the model of the render
        assert single["front_axis"] == "-Y" and OM.asset_of(single)["front_axis_fixed"]["was"] == "-X"


def test_real06_every_library_door_fits_its_opening_as_a_product():
    """real06 (the trimmed 25 Oct 2026 building): every outer door and window the plan gives a library model fits it
    within the build's stretch tolerance, with a box wider than deep (the run's back and front doors were the turned
    "Modern Single Door")."""
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"
    prep = BB.prepare(copy.deepcopy(b), "base", None)
    bb = prep["building"]
    outer = S.outer_openings(bb, bb["levels"], prep.get("ground_outline") or [], prep.get("outlines"))
    ids = {r["opening"]["id"] for r in outer}
    outer = list(outer) + [r for r in AR.open_air_doors(bb) if r["opening"]["id"] not in ids
                           and r["opening"].get("outside_door")]
    extras = OM.load_extras(CATALOGUE)
    if not OM.candidates(extras, "door", "relaxed"):
        pytest.skip("no doors in the catalogue")
    plan = OM.plan(bb, outer, extras, "relaxed", style={"family": "scandinavian"})
    sizes = {r["opening"]["id"]: (float(r["opening"]["width"]), float(r["top"]) - float(r["bottom"])) for r in outer}
    assert plan
    for oid, v in plan.items():
        w, h = sizes[oid]
        assert OB.stretch_problem(v["asset"]["bbox_m"], w / v["panels"], h) is None, (oid, v["asset"]["title"])
        if v["category"] in OM.SINGLE_LEAF:
            assert w <= OM.SINGLE_LEAF_MAX_M + 1e-6 and v["panels"] == 1
