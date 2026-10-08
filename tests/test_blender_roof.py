"""CPU tests of the roof of the whole building (wenart/blender/roof.py, docs/milestone10.md §3.2 items 2-3):
``planes_for`` for every roof type (the example's gable reproduced from its parameters, a real02-like mansard
with two pitches 40 / 13 degrees, eaves 0.50 m above the attic floor and 0.50 m outside the wall), the model the
scene builds, the roof solid, walls cut by the roof underside, sloped ceilings, the terrace parapet cuts, the
knee-wall cross-check, the assumed flat roof of ``roof: null`` and the angle convention (docs/milestone10.md §1.6b
rows 1 and 13: the example frame with its origin at the outer wall faces; aspect counter-clockwise from +X)."""
import copy
import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender import roof as R

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
T40, T13 = math.tan(math.radians(40.0)), math.tan(math.radians(13.0))


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _v(value, method="vector"):
    return {"value": value, "method": method, "confidence": 1.0 if method != "assumed" else 0.0}


def _attic(floor=3.15):
    return {"levels": [{"id": "L1", "elevation": floor, "ceiling_height": 3.0, "kind": "attic"}], "walls": []}


def _real02_roof(floor=3.15, **extra):
    """real02 (docs/milestone10.md §0.1): roof outline 16.17 x 13.00 m, break line 11.77 x 8.60 m (2.20 m in),
    40 degrees at the eaves and 13 degrees above, eaves 0.50 m above the attic floor and 0.50 m outside the wall."""
    roof = {"type": "mansard", "type_source": "plan_roof_lines", "over_level_id": "L1",
            "outline": _rect(-0.5, -1.25, 15.67, 11.75), "break_line": _rect(1.7, 0.95, 13.47, 9.55),
            "pitches_deg": [_v(40.0), _v(13.0)], "eaves_height": _v(floor + 0.5), "overhang": _v(0.5),
            "ridge_lines": [], "planes": [], "evidence": []}
    roof.update(extra)
    return roof


def _by_id(planes):
    return {p["id"]: p for p in planes}


def _z_range(plane):
    zs = [p[2] for p in plane["points"]]
    return min(zs), max(zs)


# --------------------------------------------------------------------------
# planes_for
# --------------------------------------------------------------------------

def test_planes_for_reproduces_the_example_gable_from_its_parameters():
    roof = copy.deepcopy(EXAMPLE["roof"])
    drawn = roof["planes"]
    roof["planes"] = []                     # the pipeline leaves them empty
    planes = R.planes_for(roof, EXAMPLE)
    same, why = R.equivalent_planes(planes, drawn)
    assert same, why
    south = _by_id(planes)["rp_south"]
    assert south["slope_deg"] == pytest.approx(35.0) and south["aspect_deg"] == pytest.approx(270.0)   # down to -Y
    assert south["source"] == "derived" and _z_range(south) == pytest.approx((3.65, 6.888), abs=1e-3)
    assert _by_id(planes)["rp_north"]["aspect_deg"] == pytest.approx(90.0)
    for p in planes:                        # counter-clockwise seen from above (outer surface, normal up)
        assert G.polygon_signed_area([q[:2] for q in p["points"]]) > 0


def test_example_knee_wall_matches_the_eaves():
    # knee wall 1.00 m to the drawn roof line at the outer wall face (0.50 m inside the eaves)
    roof = copy.deepcopy(EXAMPLE["roof"])
    roof["planes"], roof["eaves_height"] = [], None
    same, why = R.equivalent_planes(R.planes_for(roof, EXAMPLE), EXAMPLE["roof"]["planes"])
    assert same, why


def test_real02_like_mansard_two_pitches_and_a_level_break_line():
    floor = 3.15
    d = R.derive(_real02_roof(floor), _attic(floor))
    assert not d["assumed"] and not d["warnings"]
    planes = d["planes"]
    assert len(planes) == 8
    lower = [p for p in planes if p["id"].endswith("_lower")]
    upper = [p for p in planes if p["id"].endswith("_upper")]
    assert len(lower) == 4 and len(upper) == 4
    assert all(p["slope_deg"] == pytest.approx(40.0) for p in lower)
    assert all(p["slope_deg"] == pytest.approx(13.0) for p in upper)
    eaves, brk = floor + 0.5, floor + 0.5 + 2.2 * T40
    for p in lower:
        assert _z_range(p) == pytest.approx((eaves, brk), abs=1e-3)
    # the upper hip over the 11.77 x 8.60 m break line: ridge along the long side, 4.30 m x tan 13 above it
    ridge = brk + 4.3 * T13
    assert max(_z_range(p)[1] for p in upper) == pytest.approx(ridge, abs=1e-3)
    assert d["ridge_z"] == pytest.approx(ridge, abs=1e-3)
    # the eaves run around the whole outline at the eaves height
    outline_pts = [tuple(q[:2]) for p in lower for q in p["points"] if abs(q[2] - eaves) < 1e-6]
    assert {(-0.5, -1.25), (15.67, -1.25), (15.67, 11.75), (-0.5, 11.75)} <= {(round(x, 3), round(y, 3)) for x, y in outline_pts}


def test_real02_mansard_from_the_knee_wall_alone():
    floor = 3.15
    knee = 0.5 + 0.5 * T40                  # to the roof line at the outer wall face, 0.50 m inside the eaves
    a = R.planes_for(_real02_roof(floor), _attic(floor))
    b = R.planes_for(_real02_roof(floor, eaves_height=None, knee_wall=_v(knee)), _attic(floor))
    assert R.equivalent_planes(a, b)[0]


def test_real02_mansard_ridge_on_the_party_wall_and_the_drawn_ridge_height():
    floor = 3.15
    roof = _real02_roof(floor, ridge_lines=[[[7.585, 0.95], [7.585, 9.55]]], ridge_height=_v(floor + 3.64))
    d = R.derive(roof, _attic(floor))
    upper = [p for p in d["planes"] if p["id"].endswith("_upper")]
    # the ridge runs along the drawn line (across the pair, on the party wall): the upper slopes face east and west
    assert sorted(p["aspect_deg"] for p in upper) == pytest.approx([0.0, 180.0])
    assert d["ridge_z"] == pytest.approx(floor + 0.5 + 2.2 * T40 + 5.885 * T13, abs=1e-3)
    assert any("drawn ridge height" in w for w in d["warnings"])          # 6 cm off the section: listed
    assert R.is_convex(d["planes"])


def _real02_section(floor=3.15):
    """real02's section (docs/milestone10.md §0.1; the pipeline's ``roof.profile``): cut along x across the pair,
    eaves 0.50 m above the attic floor at the outline, 40 degrees for 2.00 m to the break, 13 degrees to the
    ridge on the party wall (x 7.585)."""
    e = floor + 0.5
    b = e + 2.0 * T40
    p = b + 6.085 * T13
    return {"region_id": "r6", "cut_axis": "x", "method": "vector",
            "points": [[-0.5, e], [1.5, b], [7.585, p], [13.67, b], [15.67, e]]}


def test_real02_mansard_follows_its_section_ridge_on_the_party_wall():
    # review #22: the section peaks on the party wall, so the ridge runs along y at x 7.585 at the drawn height;
    # the plan's break line (2.20 m in) and the section's break (2.00 m in) disagree: listed, the section kept
    floor = 3.15
    prof = _real02_section(floor)
    peak = prof["points"][2][1]
    roof = _real02_roof(floor, profile=prof, ridge_height=_v(peak))
    d = R.derive(roof, _attic(floor))
    upper = [p for p in d["planes"] if p["id"].endswith("_upper")]
    assert sorted(p["aspect_deg"] for p in upper) == pytest.approx([0.0, 180.0])        # slopes east and west
    assert all(p["slope_deg"] == pytest.approx(13.0, abs=0.01) for p in upper)
    assert all(p["slope_deg"] == pytest.approx(40.0, abs=0.01) for p in d["planes"] if p["id"].endswith("_lower"))
    assert d["ridge_z"] == pytest.approx(peak) and d["eaves_z"] == pytest.approx(floor + 0.5)
    ridge = {round(q[0], 3) for p in upper for q in p["points"] if abs(q[2] - peak) < 1e-3}
    assert ridge == {7.585}
    for s, z in prof["points"]:                                       # the built roof along the cut = the section
        assert R.surface_z(d["equations"], s, 5.25) == pytest.approx(z, abs=1e-6)
    fields = {a["field"] for a in d["assumed"]}
    assert {"ridge_direction", "mansard_ends"} <= fields
    assert sum("break line: the section breaks" in w for w in d["warnings"]) == 2
    assert not any("vs the drawn section" in w or "derived ridge" in w for w in d["warnings"])
    assert R.is_convex(d["planes"])
    # a section that disagrees with the planes is listed (here: a gable along x against a section peaking in x)
    gable = _real02_roof(floor, type="gable", ridge_lines=[[[0.0, 5.25], [15.0, 5.25]]], profile=prof)
    assert any("vs the drawn section" in w for w in R.derive(gable, _attic(floor))["warnings"])


def test_ridge_direction_from_the_section_or_assumed():
    floor = 3.15
    gable = R.derive(_real02_roof(floor, type="gable"), _attic(floor))
    assert any(a["field"] == "ridge_direction" and a["value"] == "along the long side" for a in gable["assumed"])
    prof = {"cut_axis": "x", "points": [[-0.5, 3.65], [7.585, 6.0], [15.67, 3.65]]}
    gable = R.derive(_real02_roof(floor, type="gable", profile=prof, pitches_deg=[]), _attic(floor))
    assert sorted(p["aspect_deg"] for p in gable["planes"]) == pytest.approx([0.0, 180.0])   # ridge along y
    assert any(a["field"] == "ridge_direction" and a["value"] == "across the section cut" for a in gable["assumed"])
    assert R.section_profile({"profile": dict(prof, points=[[0, 3], [5, 6], [10, 6]])}, {"u": (1, 0), "v": (0, 1)}) \
        is None                                                       # a flat top gives no single ridge


@pytest.mark.parametrize("rtype, count, aspects", [
    ("gable", 2, [90.0, 270.0]),
    ("hip", 4, [0.0, 90.0, 180.0, 270.0]),
    ("gambrel", 4, [90.0, 90.0, 270.0, 270.0]),
    ("shed", 1, [270.0]),
    ("flat", 1, [None]),
])
def test_every_roof_type(rtype, count, aspects):
    floor = 3.15
    roof = _real02_roof(floor, type=rtype)
    d = R.derive(roof, _attic(floor))
    planes = d["planes"]
    assert len(planes) == count
    got = sorted((p["aspect_deg"] for p in planes), key=lambda a: -1 if a is None else a)
    assert got == aspects
    assert R.is_convex(planes)
    area = sum(G.polygon_area([q[:2] for q in p["points"]]) for p in planes)
    assert area == pytest.approx(16.17 * 13.0, rel=1e-6)          # the planes cover the outline once
    if rtype == "hip":
        top = max(_z_range(p)[1] for p in planes)
        assert top == pytest.approx(floor + 0.5 + 6.5 * T40, abs=1e-3)
        ridge = [q for p in planes for q in p["points"] if abs(q[2] - top) < 1e-6]
        xs = sorted({round(q[0], 3) for q in ridge})
        assert xs[-1] - xs[0] == pytest.approx(16.17 - 13.0, abs=1e-3)   # ridge length L - W
    if rtype == "shed":
        assert any(a["field"] == "shed_direction" for a in d["assumed"])
    if rtype == "flat":
        assert _z_range(planes[0]) == pytest.approx((floor + 0.5, floor + 0.5))


def test_missing_values_are_assumed_and_listed():
    b = copy.deepcopy(EXAMPLE)
    lv = next(lv for lv in b["levels"] if lv["id"] == "L1")
    roof = {"type": "hip", "type_source": "assumed", "over_level_id": None, "planes": [], "evidence": []}
    d = R.derive(roof, {"levels": [lv], "walls": [w for w in b["walls"] if w["level_id"] == "L1"]})
    fields = {a["field"] for a in d["assumed"]}
    assert {"over_level_id", "outline", "pitch", "eaves_height"} <= fields
    # outline: the walls' outer faces (10.25 x 8.25 m from the origin) grown by the assumed 0.50 m overhang
    xs = [p[0] for p in d["outline"]]
    ys = [p[1] for p in d["outline"]]
    assert (min(xs), max(xs), min(ys), max(ys)) == pytest.approx((-0.5, 10.75, -0.5, 8.75))
    assert all(p["slope_deg"] == pytest.approx(R.DEFAULTS["pitch_deg"]) for p in d["planes"])
    # eaves: an assumed 1.00 m knee wall at the outer wall face
    assert d["eaves_z"] == pytest.approx(3.0 + 1.0)


def test_other_roof_type_builds_a_gable_and_says_so():
    roof = dict(_real02_roof(), type="other")
    d = R.derive(roof, _attic())
    assert len(d["planes"]) == 2 and any(a["field"] == "type" for a in d["assumed"])


def test_equivalent_planes_rejects_another_roof():
    roof = copy.deepcopy(EXAMPLE["roof"])
    roof["planes"] = []
    roof["pitches_deg"] = [_v(30.0)]
    assert not R.equivalent_planes(R.planes_for(roof, EXAMPLE), EXAMPLE["roof"]["planes"])[0]


# --------------------------------------------------------------------------
# The model and its meshes
# --------------------------------------------------------------------------

def test_roof_model_uses_the_drawn_planes_and_lists_the_assumptions():
    m = R.roof_model(EXAMPLE["roof"], EXAMPLE)
    assert m["planes_source"] == "building" and m["derived_check"]["equivalent"] is True
    assert m["convex"] and m["over_level_id"] == "L1" and m["thickness"] == pytest.approx(0.25)
    fields = {a["field"] for a in m["assumed"]}
    assert "thickness" in fields and "parapet_height:ro_001" in fields
    assert [o["room_id"] for o in m["openings"]] == ["r_L1_teras"]
    derived = R.roof_model(dict(EXAMPLE["roof"], planes=[]), EXAMPLE)
    assert derived["planes_source"] == "derived" and R.equivalent_planes(derived["planes"], m["planes"])[0]


def test_roof_solid_z_range_and_the_terrace_hole():
    m = R.roof_model(EXAMPLE["roof"], EXAMPLE)
    verts, faces, slots = R.roof_solid(m)
    zs = [v[2] for v in verts]
    t_vert = 0.25 / math.cos(math.radians(35.0))
    assert max(zs) == pytest.approx(6.888, abs=1e-3)
    assert min(zs) == pytest.approx(3.65 - t_vert, abs=1e-3)              # the eaves underside
    top = [f for f, s in zip(faces, slots) if s == R.SLOT_COVERING]
    area = sum(abs(G.polygon_signed_area([verts[i][:2] for i in f])) for f in top)
    hole = G.polygon_area(m["openings"][0]["polygon"])
    assert area == pytest.approx(11.25 * 9.25 - hole, rel=1e-6)          # the terrace is cut out of the covering
    for f in top:                                                       # covering faces up
        assert geom2d.face_normal(verts, f)[2] > 0.5
    for f, s in zip(faces, slots):
        if s == R.SLOT_SOFFIT:
            assert geom2d.face_normal(verts, f)[2] < -0.5
    # nothing of the covering over the terrace
    for f in top:
        c = geom2d.face_center(verts, f)
        assert not G.point_in_polygon(c[:2], m["openings"][0]["polygon"])


def test_walls_under_the_roof_end_at_its_underside():
    m = R.roof_model(EXAMPLE["roof"], EXAMPLE)
    under = R.underside(m)
    # the south wall (centre y = 0.125, 0.25 m thick, x 0.125..10.125): a knee wall
    verts, faces = geom2d.box((5.125, 0.125, 5.0), (10.0, 0.25, 4.0), 0.0)
    v, f = R.clip_solid_below(verts, faces, under)
    top = max(p[2] for p in v)
    assert top == pytest.approx(R.surface_z(under, 5.0, 0.25), abs=1e-6)    # its inner face meets the underside
    t35 = math.tan(math.radians(35.0))
    # (the drawn planes carry the ridge rounded to 1 mm)
    assert top - 3.0 == pytest.approx(3.65 + 0.75 * t35 - 0.25 / math.cos(math.radians(35.0)) - 3.0, abs=1e-3)
    assert top - 3.0 == pytest.approx(0.870, abs=1e-3)                 # the knee wall at the inner face
    assert all(p[2] <= R.surface_z(under, p[0], p[1]) + 1e-6 for p in v)
    # the east gable wall (x = 10.125, y 0..8.25, up to 8 m): a gable end up to the ridge underside
    verts, faces = geom2d.box((10.125, 4.125, 5.5), (0.25, 8.25, 5.0), 0.0)
    v, f = R.clip_solid_below(verts, faces, under)
    assert max(p[2] for p in v) == pytest.approx(6.888 - 0.25 / math.cos(math.radians(35.0)), abs=1e-3)
    assert min(p[2] for p in v) == pytest.approx(3.0)
    for face in f:                                                     # still wound outwards
        n = geom2d.face_normal(v, face)
        c = geom2d.face_center(v, face)
        centre = (10.125, 4.125, 4.5)
        assert sum(n[k] * (c[k] - centre[k]) for k in range(3)) > -1e-6


def test_attic_ceilings_slope_under_the_roof_and_stay_flat_where_the_section_shows_it():
    m = R.roof_model(EXAMPLE["roof"], EXAMPLE)
    level = next(lv for lv in EXAMPLE["levels"] if lv["id"] == "L1")
    planes = R.ceiling_planes(m, level)
    room = next(r for r in EXAMPLE["rooms"] if r["id"] == "r_L1_oyun_odasi")
    verts, faces = R.ceiling_faces(room["polygon"], [], planes)
    zs = [p[2] for p in verts]
    assert max(zs) == pytest.approx(3.0 + 2.4)                         # the flat ceiling of the section
    assert min(zs) == pytest.approx(R.surface_z(R.underside(m), 0.25, 0.25) - R.CEILING_GAP, abs=1e-6)
    normals = [geom2d.face_normal(verts, f) for f in faces]
    assert all(n[2] < 0 for n in normals)                              # facing down
    assert any(abs(n[2]) < 0.99 for n in normals) and any(abs(n[2]) > 0.999 for n in normals)
    area = sum(abs(G.polygon_signed_area([verts[i][:2] for i in f])) for f in faces)
    assert area == pytest.approx(room["area_computed"], abs=0.01)


def test_parapet_cuts_of_the_example_terrace():
    # docs/milestone10.md §1.6b row 13: the terrace opening reaches over the outer walls to the outline; its
    # walls (parapet_wall_ids) end at the terrace floor + the parapet (1.00 m, assumed) under it
    m = R.roof_model(EXAMPLE["roof"], EXAMPLE)
    level = next(lv for lv in EXAMPLE["levels"] if lv["id"] == "L1")
    cuts = R.parapet_cuts(m, EXAMPLE, level)
    assert set(cuts) == {"w_L1_001", "w_L1_002"}
    south, east = cuts["w_L1_001"], cuts["w_L1_002"]                   # south x 0.125..10.125, east y 0.125..8.125
    assert [(c["t0"], c["t1"]) for c in south] == pytest.approx([(0.6, 1.0)])
    assert [(c["t0"], c["t1"]) for c in east] == pytest.approx([(0.0, 0.5)])
    assert all(c["z_top"] == pytest.approx(3.0 + 1.0) and c["opening_id"] == "ro_001"
               and c["source"] == "parapet_wall_ids" for c in south + east)
    # without parapet_wall_ids: the outer walls whose centre line runs under the opening, the same stretches
    m2 = dict(m, openings=[dict(m["openings"][0], parapet_wall_ids=[])])
    cuts2 = R.parapet_cuts(m2, EXAMPLE, level)
    assert {k: [(c["t0"], c["t1"]) for c in v] for k, v in cuts2.items()} == \
        {k: [(c["t0"], c["t1"]) for c in v] for k, v in cuts.items()}
    assert all(c["source"] == "outer walls under the opening" for v in cuts2.values() for c in v)
    assert R.segment_inside((0, 0), (10, 0), [(2, -1), (4, -1), (4, 1), (2, 1)]) == [(0.2, 0.4)]


def test_knee_wall_cross_check_and_the_profile():
    m = R.roof_model(EXAMPLE["roof"], EXAMPLE)
    # the drawn 1.00 m knee wall: the planes' top surface at the outer wall face, 1.00 m over the attic floor
    assert m["knee_wall_check"]["drawn"] == 1.0
    assert m["knee_wall_check"]["derived"] == pytest.approx(1.0, abs=1e-3)
    assert not any("knee wall" in w for w in m["warnings"])
    assert m["profile"]["cut_axis"] == "y"
    # a knee wall drawn 30 cm off the planes: a warning, the planes are kept
    off = R.roof_model(dict(EXAMPLE["roof"], knee_wall=_v(1.3)), EXAMPLE)
    assert off["knee_wall_check"]["difference"] == pytest.approx(-0.3, abs=1e-3)
    assert any("knee wall 1.30 m drawn" in w for w in off["warnings"])
    assert off["planes"] == m["planes"]


def test_no_roof_evidence_makes_an_assumed_flat_roof_over_the_top_level():
    b = copy.deepcopy(EXAMPLE)
    b["roof"] = None
    m = R.roof_model(R.flat_roof(b), b)
    assert m["type"] == "flat" and m["over_level_id"] == "L1" and len(m["planes"]) == 1
    assert m["planes"][0]["aspect_deg"] is None and m["eaves_z"] == m["ridge_z"]
    xs = [p[0] for p in m["outline"]]
    ys = [p[1] for p in m["outline"]]
    assert (min(xs), max(xs), min(ys), max(ys)) == pytest.approx((0.0, 10.25, 0.0, 8.25))   # no overhang drawn
    assert {"roof", "outline", "eaves_height", "thickness"} <= {a["field"] for a in m["assumed"]}


def test_aspect_and_side_names_follow_the_front_convention():
    # degrees counter-clockwise from +X: downhill -Y = 270 (the south slope with +Y read as north)
    assert R.slope_aspect((0.0, 0.7, 0.0)) == (pytest.approx(35.0, abs=0.01), 270.0)
    assert R.slope_aspect((-0.7, 0.0, 0.0))[1] == 0.0
    assert [R.side_name(a) for a in (0.0, 90.0, 180.0, 270.0, None)] == ["east", "north", "west", "south", "flat"]


def test_not_convex_drawn_planes_are_flagged():
    planes = [{"id": "a", "points": [[0, 0, 3], [5, 0, 3], [5, 5, 6], [0, 5, 6]]},
              {"id": "b", "points": [[5, 0, 3], [10, 0, 3], [10, 5, 1], [5, 5, 1]]}]
    assert not R.is_convex(planes)
    roof = {"type": "other", "type_source": "roof_plan", "outline": _rect(0, 0, 10, 5), "planes": planes, "evidence": []}
    m = R.roof_model(roof, _attic())
    assert m["convex"] is False and any("not convex" in w for w in m["warnings"])
