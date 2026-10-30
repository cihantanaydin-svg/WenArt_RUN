"""Soft seats as soft, well-made products (30 Oct 2026, lessons UL131 and UL140; user on real04 run
20261029-201533-full: "I did not like these sofa models" and "I like this sofa but it needs more details, also the gaps
need a rework"). The rules are general (every project, every soft seat); real04's models are only the test case:

- the quality grade of an upholstered library model and its place in the fit's rank (``soft_seats.grade``,
  ``fit.soft_steps``), and the texture-map key that now reads the audit's ``pbr_maps``;
- the flat upholstery slots the build dresses in a real fabric (``soft_seats.fabric_slots``);
- the loose parts of a model joined without changing the fitted width (``soft_seats.join_parts``,
  ``furniture.fit_vertices``) and the file's own normals carried through the rebuild (``fit_normals``,
  ``corner_normal_list``);
- the check (model review M32, Argus U36) on the run's own scene manifest."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from wenart.agent import causes as CA
from wenart.audit import kinds as K
from wenart.audit import lessons as AL
from wenart.blender import architect_lessons as L
from wenart.blender import furniture as FU
from wenart.blender import model_review as MR
from wenart.blender import soft_seats as SS
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.style import colours as CL

from test_furniture_fit_v2 import FakeCatalog, model, piece

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "real04_soft_seats_20261030.json"
REJECTED = "3dwh_291de1594f740b645143a321"       # "Crate and Barrel sofa": the user's "I did not like these sofa models"
LIKED = "3dwh_bc790e2f62189290d277caa7"          # "Sofa en L": "I like this sofa but it needs more details"


def _notes(*notes):
    return {"status": "keep", "notes": list(notes)}


# --------------------------------------------------------------------------
# 1. the grade and the fit's rank
# --------------------------------------------------------------------------

def test_the_grade_reads_the_catalogue_fields_of_the_two_real04_sofas():
    # the records of the two models as the catalogue holds them (the fields the grade reads)
    rejected = model("crate", "sofa", 2.164, 0.92, 0.80, polycount=18110, textured=True,
                     pbr_maps={"base_colour": True, "normal": False, "metallic_roughness": False, "materials": 6},
                     audit=_notes("26% non-manifold edges", "largest texture 256 px (< 512)"))
    liked = model("sofa_l", "sofa_corner", 4.68, 1.86, 0.77, polycount=45140, textured=False,
                  pbr_maps={"base_colour": False, "normal": False, "metallic_roughness": False, "materials": 4},
                  audit=_notes("98% non-manifold edges", "untextured (material colours only)"))
    abo = model("lawson", "sofa", 1.98, 0.9, 0.85, polycount=104893, textured=True,
                pbr_maps={"base_colour": True, "normal": True, "metallic_roughness": True})
    g = SS.grade(rejected)
    assert g["grade"] == "poor" and g["points"] == 3 and g["steps"] == SS.POOR_STEPS and "256 px" in g["reasons"][0]
    g = SS.grade(liked)
    assert g["grade"] == "fair" and g["points"] == 2 and g["steps"] == 2 * SS.STEPS_PER_POINT
    assert any("flat material colours" in r for r in g["reasons"]) and any("98 %" in r for r in g["reasons"])
    assert SS.grade(abo) == {"grade": "good", "points": 0, "reasons": [], "steps": 0}


def test_the_grade_of_the_committed_catalogue_entries():
    cat = C.load()
    assert SS.grade(cat.entry(REJECTED))["grade"] == "poor"
    assert SS.grade(cat.entry(LIKED))["grade"] == "fair"
    assert SS.grade(cat.entry("abo_B075X4F5CS"))["grade"] == "good"     # the ABO Lawson sofa (normal + roughness maps)
    # the curated sources are good almost everywhere: no ABO soft seat is poor
    abo = [e for e in cat.models if e["type"] in SS.SOFT_SEAT_TYPES and e["source"] == "abo" and C.usable(e, "relaxed")]
    assert abo and all(SS.grade(e)["grade"] != "poor" for e in abo)


def test_coarse_needs_a_record_without_a_normal_map_and_low_poly_and_judges_count():
    box = dict(polycount=5000)                    # 5,000 faces on a 2 x 0.9 x 0.8 box: 1,060 faces per m²
    unknown = model("u", "sofa", 2.0, 0.9, 0.8, **box)
    assert SS.grade(unknown)["points"] == 0          # an older entry without a map record is not judged coarse
    no_normal = model("n", "sofa", 2.0, 0.9, 0.8, pbr_maps={"base_colour": True, "normal": False}, **box)
    assert SS.grade(no_normal)["points"] == 1 and "coarse" in SS.grade(no_normal)["reasons"][0]
    mapped = model("m", "sofa", 2.0, 0.9, 0.8, pbr_maps={"base_colour": True, "normal": True}, **box)
    assert SS.grade(mapped)["points"] == 0
    low = model("l", "sofa", 2.0, 0.9, 0.8, polycount=1500)
    assert SS.grade(low)["points"] == 2 and "low poly" in SS.grade(low)["reasons"][0]
    judged = model("j", "sofa", 2.0, 0.9, 0.8, quality=[2, 3])
    assert SS.grade(judged)["points"] == 1
    seen = model("v", "sofa", 2.0, 0.9, 0.8, audit={"status": "keep", "vision": {"quality": 2}})
    assert SS.grade(seen)["points"] == 2
    assert SS.grade(model("t", "sofa", 2.0, 0.9, 0.8, audit=_notes("largest texture 400 px (< 512)")))["points"] == 1


def test_the_texture_map_key_reads_the_audits_pbr_maps():
    pbr = {"base_colour": True, "normal": True, "metallic_roughness": True, "materials": 1, "images": 3}
    e = model("p", "sofa", 2.0, 0.9, 0.8, textured=True, pbr_maps=pbr)
    maps = F.texture_maps_of(e)
    assert maps["normal"] is True and maps["metallic_roughness"] is True and "materials" not in maps
    assert F.maps_rank(e) == 0                          # was 1: the PBR record never reached the rank
    flat = model("f", "sofa", 2.0, 0.9, 0.8, pbr_maps={"base_colour": False, "normal": False, "materials": 4})
    assert F.maps_rank(flat) == 2
    assert F.texture_maps_of(model("x", "sofa", 2.0, 0.9, 0.8, pbr_maps={"materials": 2})) is None


def test_a_good_model_wins_over_a_poor_one_of_a_better_size_and_the_asset_says_why():
    # the poor model is the drawn size exactly; the good one must grow by 12 % (two size steps): good wins
    poor = model("poor", "sofa", 2.0, 0.9, 0.8, source="objaverse", polycount=18000,
                 audit=_notes("largest texture 256 px (< 512)"), real_product=True)
    good = model("good", "sofa", 1.786, 0.80, 0.72, polycount=60000, real_product=True,
                 pbr_maps={"base_colour": True, "normal": True})
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([poor, good]))
    assert fit["asset_id"] == "abo_good"
    assert fit["upholstery"] == {"grade": "good", "points": 0, "reasons": []}
    tried = {t["id"]: t for t in fit["candidates"]}
    assert tried["abo_good"]["upholstery"] == "good"
    ranked = F.rank_candidates([poor, good], 2.0, 0.9)
    assert [e["id"] for e in ranked] == ["abo_good", "objaverse_poor"]
    assert F.rank_key(poor, 2.0, 0.9)[2] == SS.POOR_STEPS and F.soft_steps(poor) == SS.POOR_STEPS
    # a ranking, never a gate: alone, the poor model is still the drawn piece's model, and the asset says so
    alone = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([poor]))
    assert alone["asset_id"] == "objaverse_poor" and alone["upholstery"]["grade"] == "poor"
    assert any(r.startswith("upholstery poor") for r in alone["ranking"]["reasons"])
    assert "upholstered model adds its quality grade" in F.RANKING_RULE


def test_other_types_take_no_upholstery_steps():
    table = model("t", "table_dining", 1.8, 0.9, 0.75, polycount=900, textured=False)
    assert F.soft_steps(table) == 0 and "upholstery" not in F.fit_piece(piece("table_dining", 1.8, 0.9),
                                                                         FakeCatalog([table]))
    assert set(SS.SOFT_SEAT_TYPES) <= set(F.UPHOLSTERED_TYPES)


# --------------------------------------------------------------------------
# 2. the flat upholstery slots
# --------------------------------------------------------------------------

def slot(i, name, share, textured=False, rule="type:sofa", metallic=0.0, alpha=1.0):
    return {"index": i, "name": name, "share": share, "textured": textured, "rule": rule, "metallic": metallic,
            "alpha": alpha}


def test_the_corner_sofas_unnamed_flat_slots_the_largest_is_its_upholstery():
    # real04's corner sofa: four flat materials with export names (the scene manifest's materials)
    slots = [slot(0, "02 - Default1", 0.62), slot(1, "default_face_material", 0.04), slot(2, "02 - Default1.001", 0.24),
             slot(3, "01 - Default1", 0.10)]
    got = SS.fabric_slots(slots)
    assert [g["index"] for g in got] == [0, 2]
    assert "largest flat slot" in got[0]["why"] and "upholstery too" in got[1]["why"]


def test_hard_named_metallic_and_see_through_slots_are_never_upholstery():
    slots = [slot(0, "Fabric_Grey", 0.05, rule="fabric"), slot(1, "Steel", 0.5, rule="metal"),
             slot(2, "frame", 0.3, metallic=1.0), slot(3, "glass top", 0.1, alpha=0.3),
             slot(4, "Leather_Brown", 0.6, rule="leather")]
    assert [g["index"] for g in SS.fabric_slots(slots)] == [0]          # only the slot named for a fabric


def test_a_textured_upholstery_keeps_its_texture_and_its_flat_frame():
    # HSSD-like chair: the textured seat covers 70 %, a flat unnamed base 30 %: the base is no upholstery
    slots = [slot(0, "seat", 0.7, textured=True), slot(1, "Material.001", 0.3)]
    assert SS.fabric_slots(slots) == []
    # a small flat slot alone (legs) is no upholstery either
    assert SS.fabric_slots([slot(0, "Color_A01", 0.05)]) == []


def test_material_shares_and_face_areas():
    verts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (2, 0, 0), (2, 1, 0)]
    faces = [[0, 1, 2, 3], [1, 4, 5, 2]]
    assert SS.face_areas(verts, faces) == pytest.approx([1.0, 1.0])
    assert SS.material_shares(verts, faces, [0, 1], 3) == pytest.approx([0.5, 0.5, 0.0])


def test_the_nearest_colour_name_keeps_the_models_own_colour():
    assert CL.nearest(CL.linear_rgb("light grey")) == "light grey"
    assert CL.nearest((1.0, 1.0, 1.0)) == "white"
    assert CL.nearest(CL.linear_rgb("navy")) == "navy"


# --------------------------------------------------------------------------
# 3. the loose parts joined, the width kept, the normals carried
# --------------------------------------------------------------------------

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


def gaps_between_modules():
    """A modular sofa in the piece frame (front -Y): a 2-seat module, a 1-seat module 2 cm to its right, a chaise
    module 3 cm further, a back cushion floating 1.5 cm over the 2-seat module's seat, and two legs under it."""
    return mesh((-1.2, -0.45, 0.10, 0.4, 0.45, 0.45),          # 2-seat module (the largest part)
                (0.42, -0.45, 0.10, 1.2, 0.45, 0.45),           # 1-seat module: 2 cm apart along x
                (1.23, -0.45, 0.10, 2.0, 0.45, 0.45),           # chaise: 3 cm from the 1-seat module
                (-1.2, 0.20, 0.465, 0.4, 0.45, 0.85),           # back cushion: 1.5 cm over the 2-seat module
                (-1.1, -0.40, 0.0, -1.0, -0.30, 0.10),          # a leg: on the floor, under the module (touching)
                (0.2, -0.40, 0.0, 0.3, -0.30, 0.08))            # a leg 2 cm short of the module: never lifted


def test_face_parts_and_vertex_parts():
    verts, faces = gaps_between_modules()
    parts = SS.face_parts(verts, faces)
    assert len(set(parts)) == 6 and parts[:6] == [0] * 6
    vp, areas = SS.vertex_parts(len(verts), faces, parts, verts)
    assert vp[:8] == [0] * 8 and max(areas, key=areas.get) == 0
    # two faces sharing a position (glTF splits vertices at seams) are one part
    v, f = cube(0, 0, 0, 1, 1, 1)
    dup = v + [v[0]]
    assert len(set(SS.face_parts(dup, f[:-1] + [[8, 3, 7, 4]]))) == 1


def test_the_modules_are_joined_the_floating_cushion_rests_the_legs_stay_on_the_floor():
    verts, faces = gaps_between_modules()
    vp, areas = SS.vertex_parts(len(verts), faces, SS.face_parts(verts, faces), verts)
    joined, rec = SS.join_parts(verts, vp, areas)
    assert rec["parts"] == 6 and rec["gaps"] >= 3 and rec["max_gap_m"] == pytest.approx(0.03, abs=1e-4)
    # three bodies moved; the short leg's 2 cm stays (never lifted off the floor) and is reported (M32 names it)
    assert rec["joined"] == 3 and rec["max_gap_after_m"] == pytest.approx(0.02, abs=1e-4) and rec["gaps_after"] == 1
    boxes = SS.part_boxes(joined, vp)
    assert boxes[1][0] == pytest.approx(boxes[0][3]) and boxes[2][0] == pytest.approx(boxes[1][3])
    assert boxes[3][2] == pytest.approx(boxes[0][5])                     # the cushion rests on the seat
    assert boxes[5][2] == pytest.approx(0.0) and boxes[4][2] == pytest.approx(0.0)   # no leg lifted off the floor
    assert rec["width_before_m"] == pytest.approx(3.2) and rec["width_after_m"] == pytest.approx(3.15)
    assert any("not lifted" in s for s in rec.get("stayed") or [])


def test_wide_gaps_side_by_side_offsets_and_a_clash_are_left_alone():
    # 10 cm apart: apart by design (a side table between two modules)
    verts, faces = mesh((0, 0, 0, 1, 1, 0.5), (1.10, 0, 0, 2.0, 1, 0.5))
    vp, areas = SS.vertex_parts(len(verts), faces, SS.face_parts(verts, faces), verts)
    _, rec = SS.join_parts(verts, vp, areas)
    assert rec["gaps"] == 0 and rec["joined"] == 0
    # a cushion that overlaps its neighbour's face over less than half of its own is no facing pair
    verts, faces = mesh((0, 0, 0, 1, 1, 0.5), (1.02, 0.8, 0, 2.0, 1.8, 0.5))
    vp, areas = SS.vertex_parts(len(verts), faces, SS.face_parts(verts, faces), verts)
    assert SS.join_parts(verts, vp, areas)[1]["joined"] == 0
    # a thin slab 5 mm from both modules between them: the far module closing its 3 cm on the first would cross the
    # slab, so it stays there and closes on the slab instead (the chain: 5 mm + 5 mm)
    boxes = {0: [0, 0, 0, 2.0, 1, 0.5], 1: [2.03, 0, 0, 3.0, 1, 0.5], 2: [2.005, 0.2, 0.1, 2.025, 0.8, 0.4]}
    plan = SS.join_plan(boxes, {0: 3.0, 1: 1.0, 2: 0.1})
    assert plan["shift"][2] == pytest.approx((-0.005, 0.0, 0.0)) and plan["shift"][1] == pytest.approx((-0.01, 0, 0))
    assert plan["record"]["max_gap_after_m"] == pytest.approx(0.02)     # beside the slab the modules stay 2 cm apart
    # a move into another body is refused: a strip in the gap that faces neither module (it overlaps their sides by
    # 5 cm of its 55) would be crossed by the far module
    boxes = {0: [0, 0, 0, 2.0, 1, 0.5], 1: [2.03, 0, 0, 3.0, 1, 0.5], 2: [2.005, 0.95, 0.1, 2.025, 1.5, 0.4]}
    plan = SS.join_plan(boxes, {0: 3.0, 1: 1.0, 2: 0.1})
    assert 1 not in plan["shift"] and any("push it into another body" in s for s in plan["record"]["stayed"])


def test_fit_vertices_joins_the_parts_and_keeps_the_drawn_width():
    verts, faces = gaps_between_modules()
    vp, areas = SS.vertex_parts(len(verts), faces, SS.face_parts(verts, faces), verts)
    asset = {"fit_scale": [3.0 / 3.2] * 3, "scaling": "uniform", "front_axis": "-Y", "up_axis": "+Z"}
    fp = {"center": [5.0, 5.0], "size": [3.0, 0.9], "rotation_deg": 0.0}
    plain, info0 = FU.fit_vertices(verts, asset, fp, 0.0)
    world, info = FU.fit_vertices(verts, asset, fp, 0.0, join=(vp, areas))
    assert "parts" not in info0 and info0["bbox_m"][0] == pytest.approx(3.0)
    assert info["bbox_m"][0] == pytest.approx(3.0, abs=1e-4)                      # the drawn width kept
    assert info["parts"]["joined"] == 3 and info["parts"]["width_kept_scale"] == pytest.approx(3.2 / 3.15, abs=1e-4)
    assert info["fit_scale"][0] == pytest.approx(3.0 / 3.15, abs=1e-4)
    after = SS.part_boxes(world, vp)
    assert after[1][0] == pytest.approx(after[0][3]) and min(b[2] for b in after.values()) == pytest.approx(0.0)


def test_fit_normals_turn_with_the_piece_and_the_corner_list_for_blender():
    asset = {"front_axis": "-Y", "up_axis": "+Z"}
    fp = {"center": [0, 0], "size": [2, 1], "rotation_deg": 90.0}
    got = FU.fit_normals([[(1.0, 0.0, 0.0)] * 3, None], asset, fp)
    assert got[1] is None and got[0][0] == pytest.approx((0.0, 1.0, 0.0), abs=1e-9)
    # a front +X model is turned to front -Y first: its +X normal becomes -Y, then the 90 degree footprint turn
    turned = FU.fit_normals([[(1.0, 0.0, 0.0)]], {"front_axis": "+X", "up_axis": "+Z"}, fp)
    assert turned[0][0] == pytest.approx((1.0, 0.0, 0.0), abs=1e-9)
    # a non-uniform scale bends a slanted normal (the inverse transpose), renormalised
    slanted = FU.fit_normals([[(math.sqrt(0.5), 0.0, math.sqrt(0.5))]], asset, dict(fp, rotation_deg=0.0),
                             scale=(2.0, 1.0, 1.0))
    n = slanted[0][0]
    assert math.isclose(sum(c * c for c in n), 1.0) and n[2] > n[0]
    flags, loops = FU.corner_normal_list([[0, 1, 2], [2, 3, 0], [4, 5, 6]], [[(0, 0, 1)] * 3, None])
    assert flags == [True, False, False] and loops[:3] == [(0.0, 0.0, 1.0)] * 3 and loops[3:] == [(0.0, 0.0, 0.0)] * 6


# --------------------------------------------------------------------------
# 4. the check on the run's own scene (model review M32, Argus U36)
# --------------------------------------------------------------------------

def manifest():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_the_check_finds_what_the_user_saw_on_real04():
    got, n = SS.review(manifest())
    assert n == 18                                    # the run's library soft seats (the not-built ottomans are none)
    by = {(g["target"], g["problem"]) for g in got}
    assert ("f_L-1_053", "flat_fabric") in by          # the corner sofa in its flat export white (UL140)
    assert {("f_L1_017", "poor_model"), ("f_L1_020", "poor_model")} <= by   # the two Crate and Barrel sofas (UL131)
    flat = next(g for g in got if g["problem"] == "flat_fabric")
    assert flat["severity"] == "major" and flat["lesson"] == "UL140" and "02 - Default1" in flat["metrics"]["materials"]
    assert all(g["target"] not in ("f_L-1_049", "f_L1_018") for g in got)   # the ABO chair and sofa are fine


def test_a_dressed_joined_smooth_sofa_passes_and_each_problem_is_named():
    base = {"kind": "furniture", "type": "sofa", "method": "library", "wenart_id": "f_1", "room_id": "r",
            "textured": False, "asset": {"asset_id": "3dwh_x", "upholstery": {"grade": "fair", "points": 2}}}
    ok = dict(base, fabric_dressing={"slots": [{"slot": "Color_A01"}]}, parts={"max_gap_after_m": 0.0},
              shading={"file_smooth": 400, "smooth": 400})
    assert SS.review({"objects": [ok]}) == ([], 1)
    bad = dict(base, parts={"max_gap_m": 0.03, "max_gap_after_m": 0.025, "parts": 9},
               shading={"file_smooth": 400, "smooth": 0},
               asset={"asset_id": "3dwh_x", "upholstery": {"grade": "poor", "points": 3, "reasons": ["a 256 px"]}})
    probs = {g["problem"]: g for g in SS.review({"objects": [bad]})[0]}
    assert set(probs) == {"flat_fabric", "parts_apart", "faceted", "poor_model"}
    assert probs["parts_apart"]["severity"] == "major" and probs["poor_model"]["severity"] == "minor"
    parametric = dict(base, method="parametric (fallback: no model)")
    assert SS.review({"objects": [parametric]}) == ([], 0)


def test_model_review_m32_and_argus_u36_carry_the_rule():
    assert "M32" in MR.CHECKS and K.CHECK_KIND["M32"] == "taste" and K.CHECK_KIND["U36"] == "taste"
    assert CA.CHECK_CAUSE["M32"] == "wrong_model" and CA.CHECK_CAUSE["M32"] in CA.CAUSES
    got, n = MR.soft_seats_review(manifest())
    assert n == 18 and {v["metrics"]["problem"] for v in got} == {"flat_fabric", "poor_model"}
    flat = next(v for v in got if v["metrics"]["problem"] == "flat_fabric")
    assert flat["check"] == "M32" and flat["owner"] == "build" and "_dress_fabric" in flat["fix"]
    poor = next(v for v in got if v["metrics"]["problem"] == "poor_model")
    assert poor["owner"] == "fit" and K.kind_of(poor) == "taste"
    apart = MR.soft_seats_review({"objects": [{"kind": "furniture", "type": "armchair", "method": "library",
                                               "wenart_id": "f_2", "textured": True, "asset": {"asset_id": "a"},
                                               "parts": {"max_gap_after_m": 0.04}}]})[0]
    assert apart[0]["kind"] == "detached"
    rec = MR.review({"levels": [], "rooms": [], "openings": [], "furniture": [], "walls": []}, manifest())
    assert rec["checks"]["M32"]["checked"] == 18 and rec["checks"]["M32"]["failed"] == len(got)
    out = AL.audit({"levels": [], "rooms": [], "furniture": []}, manifest())
    u36 = [f for f in out["findings"] if f["check"] == "U36"]
    assert out["checked"]["U36"] == len(u36) == len(got) and {f["evidence"]["lesson"] for f in u36} == {"UL131",
                                                                                                         "UL140"}
    assert AL.audit({"levels": [], "rooms": [], "furniture": []}, None)["checked"]["U36"].startswith("no scene")
    assert AL.CHECK_LESSONS["U36"] == ("UL131", "UL140")
    assert AL.coverage()["UL140"]["code"] == ["U36"] and AL.coverage()["UL131"]["code"] == ["U36"]


def test_lessons_ul131_and_ul140_are_built_with_their_checks():
    by = {x["id"]: x for x in L.lessons()}
    for lid in ("UL131", "UL140"):
        x = by[lid]
        assert x["status"] == "built" and x["checks"] == ["build"] and "M32" in x["lesson"] and "U36" in x["lesson"]
    assert "soft_seats" in by["UL131"]["lesson"] and "rejected" in by["UL131"]["lesson"]
    assert "fabric" in by["UL140"]["lesson"] and "joined" in by["UL140"]["lesson"]
    raw = (ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8")
    assert raw.endswith("}\n") and raw == json.dumps(json.loads(raw), indent=1, ensure_ascii=False) + "\n"
