"""Milestone 12 track B: the audit's code checks (docs/milestone12.md §6.1, ``checks.py``) and mesh measurements
(``meshstats.py``) on hand-made items and meshes."""
import numpy as np
import pytest

from wenart.assets.audit import checks as CK
from wenart.assets.audit import load_config
from wenart.assets.audit import meshstats as M

CFG = load_config()


def item(**kw):
    base = {"id": "x", "type": "sofa", "kind": "furniture", "source": "abo", "licence": "CC-BY-4.0", "title": "Sofa",
            "bbox_m": [2.0, 0.9, 0.85], "units_known": True, "front_axis": "-Y", "front_axis_confidence": "high",
            "up_axis": "+Z", "bbox_min_m": [-1.0, -0.45, 0.0], "bbox_max_m": [1.0, 0.45, 0.85],
            "origin_offset": [0.0, 0.0, 0.0], "polycount": 20000, "quality": [4, 4]}
    base.update(kw)
    return base


@pytest.mark.parametrize("licence,removed", [("CC0", False), ("CC-BY-4.0", False), ("generated (TRELLIS.2-4B, MIT)",
                                             False), ("CC-BY-NC-4.0", True), ("CC-BY-SA-4.0", True),
                                             ("CC-BY-NC-SA-4.0", True), ("CC-BY-ND-4.0", True), ("unknown", True)])
def test_licence(licence, removed):
    assert (CK.licence_check(item(licence=licence))["status"] == "remove") is removed


def test_size_ok_and_rescale_and_remove():
    assert CK.size_check(item(), CFG)["status"] == "ok"
    r = CK.size_check(item(bbox_m=[2.5, 1.40, 1.25]), CFG)                # a real product 23 % deep
    assert r["status"] == "fix" and r["fix"]["rescale"] < 1.0
    r = CK.size_check(item(bbox_m=[3.6, 1.6, 1.5]), CFG)                  # known units, far off: not a sofa
    assert r["status"] == "remove"
    r = CK.size_check(item(bbox_m=[3.6, 1.6, 1.5], units_known=False), CFG)   # a unit guess: rescale
    assert r["status"] == "fix" and r["fix"]["rescale"] < 0.85


def test_size_proportions_and_side_and_front():
    tub = item(type="bathtub", bbox_m=[1.32, 0.74, 0.80], units_known=False, source="generated")
    assert CK.size_check(tub, CFG)["status"] == "remove"                 # generated tubs (§1.6)
    side = item(type="wardrobe", bbox_m=[1.2, 2.0, 0.6], front_axis_confidence="low")
    r = CK.size_check(side, CFG)
    assert r["status"] == "remove" and "on its side" in r["reason"]
    bunk = item(type="bunk_bed", bbox_m=[2.0, 1.0, 1.6], front_axis="-Y",
                front_axis_note="geometry: back_taller: the top 30 % of the vertices sit toward -X (-0.4)")
    r = CK.size_check(bunk, CFG)                                         # every bunk bed faced its long side
    assert r["status"] == "fix" and r["fix"]["front_quarter_turns"] == 1
    assert CK.geometric_front(bunk) == "+X" and CK.rotate_axis("-Y", 1) == "+X"


def test_pivot_and_up():
    assert CK.pivot_check(item(), CFG)["status"] == "ok"
    r = CK.pivot_check(item(origin_offset=[0.0, 0.0, 0.2]), CFG)
    assert r["status"] == "fix" and r["fix"]["origin_offset"] == [0.0, 0.0, 0.0]
    m = {"model_box_min": [-1.0, -0.45, -0.1], "model_box_max": [1.0, 0.45, 0.75]}
    r = CK.pivot_check(item(), CFG, m)
    assert r["status"] == "fix" and r["fix"]["origin_offset"] == [0.0, 0.0, -0.1]
    assert CK.up_check(item(up_axis="+Y"))["status"] == "remove"


def test_title_checks_flags_and_retype():
    recs = CK.title_check(item(type="bench", title="Simple Park Bench"), {"bench"})
    assert any(r["check"] == "title_flag" and r["status"] == "remove" for r in recs)
    recs = CK.title_check(item(type="tall_cabinet", title="Movian armadio a 2 ante Mira", bbox_m=[0.98, 0.58, 1.93]),
                          {"wardrobe", "tall_cabinet"})
    assert recs[0]["status"] == "review" and recs[0]["metrics"]["suggested_type"] == "wardrobe"
    recs = CK.title_check(item(type="curtain", kind="decor", title="Window"), {"curtain"})
    assert recs[0]["status"] == "remove"


def test_title_size():
    assert CK.title_size("Marchio Amazon - Movian Scrivania Candon, 114,3 x 49,53 x 76,454 cm") == [1.143, 0.4953,
                                                                                                     0.7645]
    assert CK.title_size("Movian Loue Bed Frame, 160 x 200cm, White") == [1.6, 2.0]
    assert CK.title_size("Rivet Chair, 28.3\"W") is None
    it = item(title="Movian Ljungan Desk, 114 x 60 x 90cm", type="desk", bbox_m=[1.143, 0.936, 0.998])
    assert CK.title_size_check(it)["status"] == "warn"


def test_crude_face_count_needs_the_vision_check():
    recs = CK.mesh_check(item(polycount=1200), CFG)
    assert recs[0]["check"] == "crude" and recs[0]["status"] == "review"
    assert CK.mesh_check(item(kind="decor", type="vase", polycount=500), CFG)[0]["status"] == "skip"


def test_mesh_and_texture_checks_on_measurements():
    good = {"ok": True, "faces": 20000, "flipped_share": 0.0, "zero_area_share": 0.0, "nonmanifold_share": 0.0,
            "boundary_share": 0.1, "outside_parts": [], "textures": {"images": 3, "max_px": 2048, "missing": []}}
    assert [r["status"] for r in CK.mesh_check(item(), CFG, good)] == ["ok"]
    assert CK.mesh_check(item(), CFG, dict(good, flipped_share=0.5))[0]["status"] == "remove"
    assert CK.mesh_check(item(), CFG, {"ok": False, "error": "no geometry"})[0]["status"] == "remove"
    drawer = dict(good, outside_parts=[{"share": 0.08, "sticks_out_m": 0.3, "sides": ["-y"]}], front_outside=True)
    assert CK.mesh_check(item(), CFG, drawer)[0]["status"] == "review"
    assert CK.texture_check(item(), CFG, good)["status"] == "ok"
    assert CK.texture_check(item(), CFG, dict(good, textures={"images": 1, "missing": ["a.png"]}))["status"] == "remove"
    assert CK.texture_check(item(), CFG, dict(good, textures={"images": 1, "max_px": 256}))["status"] == "warn"


def test_duplicates_keep_colour_variants():
    a = item(id="abo_a", material_slots=[{"index": 0, "colour_rgb": [10, 10, 10]}])
    b = item(id="abo_b", material_slots=[{"index": 0, "colour_rgb": [10, 10, 10]}], bbox_m=[2.005, 0.9, 0.85])
    c = item(id="abo_c", material_slots=[{"index": 0, "colour_rgb": [200, 10, 10]}])
    g = item(id="gen_d", source="generated", sha256_glb="f" * 64)
    h = item(id="objaverse_e", source="objaverse", sha256_glb="f" * 64)
    dups = CK.duplicates([b, a, c, g, h], CFG)
    assert set(dups) == {"abo_b", "gen_d"}
    assert dups["abo_b"]["metrics"]["of"] == "abo_a"
    assert dups["gen_d"]["metrics"]["of"] == "objaverse_e"


def cube(offset=(0.0, 0.0, 0.0), size=1.0, base=0):
    v = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], float)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7],
                  [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return v * size + np.array(offset), f + base


def test_meshstats_clean_cube():
    v, f = cube()
    r = M.analyse(v, f)
    assert r["ok"] and r["faces"] == 12 and r["parts"] == 1
    assert r["boundary_edges"] == 0 and r["nonmanifold_edges"] == 0 and r["flipped_share"] == 0.0
    assert r["size"] == [1.0, 1.0, 1.0] and r["pivot_offset"] == [0.5, 0.5, 0.0]


def test_meshstats_flipped_face_and_seams():
    v, f = cube()
    f = f.copy()
    f[0] = f[0][::-1]
    assert M.analyse(v, f)["inconsistent_edges"] == 3
    # a UV seam: the same corner twice is one vertex after the merge
    v2 = np.vstack([v, v[:1]])
    f2 = cube()[1].copy()
    f2[0] = [8, 2, 1]
    r = M.analyse(v2, f2)
    assert r["boundary_edges"] == 0 and r["flipped_share"] == 0.0


def test_meshstats_open_drawer_and_zero_area():
    v1, f1 = cube()
    v2, f2 = cube(offset=(0.3, -0.4, 0.3), size=0.3, base=8)
    r = M.analyse(np.vstack([v1, v2]), np.vstack([f1, f2]))
    assert r["parts"] == 2 and r["front_outside"] is True
    assert r["outside_parts"][0]["sides"] == ["-y"]
    v, f = cube()
    f = np.vstack([f, [[0, 1, 1]], [[0, 0, 0]]])
    r = M.analyse(v, f)
    assert r["zero_area_faces"] == 2


def test_meshstats_nonmanifold_edge():
    v, f = cube()
    v = np.vstack([v, [[0.5, -1.0, 0.5]]])
    f = np.vstack([f, [[0, 1, 8]]])                    # a fin on the bottom front edge: 3 faces share it
    assert M.analyse(v, f)["nonmanifold_edges"] == 1
