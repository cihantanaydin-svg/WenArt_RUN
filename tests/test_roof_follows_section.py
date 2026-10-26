"""CPU tests of the rule "the roof follows its drawn section" (wenart/blender/roof.py ``follow_section``, 26 Oct 2026,
Argus on real06; CLAUDE.md evidence rules: a drawn section is source geometry and outranks a pitch text, a default and
a ridge direction no line draws). The rule is general; real06 is only the test case:

- the ridge of a derived roof is the highest point of its planes as built (a hip whose axis came from the section
  reported 8.53 m for a roof built 7.61 m high);
- a drawn ridge height more than ``SECTION_TOL`` from the built ridge: an un-drawn ridge direction turns when that keeps
  the drawn pitch, else the pitch is solved so the ridge meets the drawn height; eaves and outline stay;
- a section profile is compared point by point only when it runs one-to-one with the plan as one roof surface
  (``section_reliability``); else only its ridge height is followed and the log says why;
- the derived roof is kept, with the reason, when no pitch in ``SECTION_PITCH_DEG`` reaches the drawn ridge;
- every change is logged in ``section_fit`` (derived, drawn, used, evidence: the section region)."""
import copy
import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import roof as R

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
T30 = math.tan(math.radians(30.0))


def _v(value, method="vector", region="r5"):
    return {"value": value, "method": method, "confidence": 1.0,
            "evidence": [{"file": "p.dwg", "region_id": region, "entity": "LINE:1", "rule": "roof_line",
                          "method": "vector"}]}


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _top(floor=3.0):
    return {"levels": [{"id": "L1", "elevation": floor, "ceiling_height": 2.7}], "walls": []}


def _gable(**extra):
    roof = {"type": "gable", "type_source": "roof_plan", "over_level_id": "L1", "outline": _rect(0, 0, 12, 8),
            "eaves_height": _v(3.0), "pitches_deg": [_v(30.0, "derived")], "ridge_lines": [], "planes": []}
    roof.update(extra)
    return roof


def _real06_roof():
    """real06 as read on 26 Oct 2026 (runs/20261026-170020-full, building_final.json): a hip roof, the roof plan's
    slope texts 33 % (18.3 degrees), eaves 6.00 m and ridge 7.77 m from the section r5 cut along y, whose envelope also
    runs on truss lines and reaches 1.8 m past the plan; the outline the build derived (walls + 0.475 m, jogs
    closed)."""
    profile = [[-0.5, 6.0], [1.507, 6.002], [5.425, 7.19], [5.468, 6.299], [6.368, 7.057], [6.985, 7.675],
               [7.614, 7.187], [8.555, 6.246], [9.508, 7.058], [10.22, 7.77], [10.944, 7.187], [11.861, 7.195],
               [11.878, 7.294], [14.984, 6.494], [15.001, 6.594], [16.8, 6.0]]
    outline = [[-0.6, 2.825], [3.875, 2.825], [3.875, -0.275], [9.126, -0.275], [9.126, 15.025], [2.875, 15.025],
               [2.875, 14.025], [-0.6, 14.025]]
    return {"type": "hip", "type_source": "roof_plan", "over_level_id": "L1", "outline": outline,
            "eaves_height": _v(6.0), "ridge_height": _v(7.77), "pitches_deg": [_v(18.3, "derived", "r6")],
            "overhang": _v(0.475), "knee_wall": _v(3.001), "ridge_lines": [], "planes": [],
            "profile": {"region_id": "r5", "cut_axis": "y", "points": profile, "method": "vector"}}


def _max_z(planes):
    return max(p[2] for pl in planes for p in pl["points"])


# --------------------------------------------------------------------------
# The ridge as built
# --------------------------------------------------------------------------

def test_real06_hip_ridge_is_the_highest_point_built():
    d = R.derive(_real06_roof(), _top())
    # the four 18.3 degree slopes meet over the short half-width (4.86 m): 6.00 + 4.863 x 0.3307 = 7.608 m, not
    # 6.00 + 7.65 x 0.3307 = 8.53 m (the long half-width, as the section's peak had put the ridge across the cut)
    assert d["ridge_z"] == pytest.approx(_max_z(d["planes"]), abs=1e-3)
    assert d["ridge_z"] == pytest.approx(6.0 + 4.8629 * math.tan(math.radians(18.3)), abs=1e-3)
    assert not any("8.53" in w for w in d["warnings"])


def test_real06_follows_the_drawn_ridge_within_tolerance_and_says_why_the_points_are_not_compared():
    d = R.derive(_real06_roof(), _top())
    fit = d["section_fit"]
    assert fit["status"] == "within_tolerance" and fit["follows_section"] is True and d["follows_section"]
    assert fit["change"] is None and fit["region_id"] == "r5"
    assert fit["drawn"]["ridge_z"] == pytest.approx(7.77) and fit["used"]["ridge_z"] == pytest.approx(7.608, abs=1e-3)
    assert fit["used"]["pitch_deg"] == pytest.approx(18.3)            # the roof plan's 33 % stays: 16 cm under 7.77
    # the profile runs on truss lines (a 1.43 m drop on the way up) and 1.77 m past the plan: not compared point by
    # point
    assert fit["points_compared"] is False
    assert any("drops 1.43 m" in r for r in fit["reasons"])
    assert any("16.80 m and the roof outline's at -0.28 / 15.03 m along y" in r for r in fit["reasons"])
    assert not any(w.startswith("roof vs the drawn section at s") for w in d["warnings"])
    assert sum("is not checked point by point against the roof" in w for w in d["warnings"]) == 1
    assert any(w.startswith("roof ridge 7.608 m built vs the drawn ridge height 7.770 m (-16 cm): within the 0.25 m")
               for w in d["warnings"])
    assert {"region_id": "r5", "rule": "section_profile", "cut_axis": "y", "points": 16, "method": "vector"} \
        in fit["evidence"]
    assert d["eaves_z"] == pytest.approx(6.0)


# --------------------------------------------------------------------------
# Following the drawn heights
# --------------------------------------------------------------------------

def test_the_roof_follows_the_drawn_section_over_a_pitch_text():
    # the example gable (35 degrees, eaves 3.65 m, ridge 6.888 m in the section r6) read with a wrong 30 degree pitch
    roof = copy.deepcopy(EXAMPLE["roof"])
    drawn = roof["planes"]
    roof["planes"], roof["pitches_deg"] = [], [_v(30.0, "ocr")]
    d = R.derive(roof, EXAMPLE)
    fit = d["section_fit"]
    assert fit["status"] == "followed" and fit["change"] == "pitch" and fit["follows_section"] is True
    assert fit["derived"]["pitch_deg"] == pytest.approx(30.0)
    assert fit["used"]["pitch_deg"] == pytest.approx(35.0, abs=0.01)
    assert fit["derived"]["ridge_z"] == pytest.approx(3.65 + 4.625 * T30, abs=1e-3)
    assert fit["used"]["ridge_z"] == pytest.approx(6.888, abs=1e-3) and fit["misfit_m"]["after"] <= R.SECTION_TOL
    assert fit["points_compared"] is True and fit["region_id"] == "r6"
    assert R.equivalent_planes(d["planes"], drawn)[0]                          # the drawn roof again
    assert d["pitches"][0] == pytest.approx(35.0, abs=0.01) and d["eaves_z"] == pytest.approx(3.65)
    assert any(w.startswith("roof adjusted to follow the drawn section r6: pitch 30.0 -> 35.0 degrees") for w in d["warnings"])
    assert not any("vs the drawn section at s" in w for w in d["warnings"])
    m = R.roof_model(roof, EXAMPLE)                                               # the model carries the record
    assert m["section_fit"] == fit and m["follows_section"] is True and m["ridge_z"] == pytest.approx(6.888, abs=1e-3)
    assert R.roof_model(EXAMPLE["roof"], EXAMPLE)["section_fit"] is None         # drawn planes stay as drawn


def test_the_ridge_turns_when_only_the_other_direction_meets_the_drawn_pitch_and_heights():
    ridge = 3.0 + 6.0 * T30                       # a 30 degree gable over the 12 m side: the ridge runs along y
    d = R.derive(_gable(ridge_height=_v(ridge)), _top())
    fit = d["section_fit"]
    assert fit["status"] == "followed" and fit["change"] == "ridge_direction"
    assert fit["used"]["ridge_turned"] is True and fit["used"]["pitch_deg"] == pytest.approx(30.0)
    assert d["ridge_z"] == pytest.approx(ridge, abs=1e-6)
    assert sorted(p["aspect_deg"] for p in d["planes"]) == pytest.approx([0.0, 180.0])     # slopes east and west
    (rec,) = [a for a in d["assumed"] if a["field"] == "ridge_direction"]
    assert rec["value"] == "along the short side" and "follow_section" in rec["reason"]


def test_eaves_from_the_drawn_ridge_a_hip_turns_instead_of_a_meaningless_pitch():
    # no eaves height and no knee wall: the eaves come from the drawn ridge and the pitch. The section (cut along the
    # long side, peaking inside) put the ridge across the cut: eaves 8 m x tan down from the ridge, a roof 1 m too low.
    # A pitch cannot fix it (the ridge does not move with the pitch); the turned ridge meets the section.
    prof = {"region_id": "r5", "cut_axis": "y", "method": "vector",
            "points": [[0.0, 6.0], [5.0, 7.6], [11.0, 7.7], [16.0, 6.0]]}
    roof = {"type": "hip", "type_source": "roof_plan", "over_level_id": "L1", "outline": _rect(0, 0, 10, 16),
            "ridge_height": _v(7.7), "pitches_deg": [_v(18.3, "derived", "r6")], "profile": prof, "ridge_lines": [],
            "planes": []}
    d = R.derive(roof, _top())
    fit = d["section_fit"]
    assert fit["derived"]["ridge_z"] == pytest.approx(7.7 - 3.0 * math.tan(math.radians(18.3)), abs=1e-3)
    assert fit["status"] == "followed" and fit["change"] == "ridge_direction" and fit["points_compared"] is True
    assert d["ridge_z"] == pytest.approx(7.7, abs=1e-3) and d["pitches"][0] == pytest.approx(18.3)
    assert d["eaves_z"] == pytest.approx(7.7 - 5.0 * math.tan(math.radians(18.3)), abs=1e-6)


def test_a_drawn_ridge_line_is_never_turned_the_pitch_follows():
    ridge = 3.0 + 6.0 * T30
    d = R.derive(_gable(ridge_height=_v(ridge), ridge_lines=[[[0.0, 4.0], [12.0, 4.0]]]), _top())
    fit = d["section_fit"]
    assert fit["change"] == "pitch" and fit["used"]["ridge_turned"] is False
    assert d["ridge_z"] == pytest.approx(ridge, abs=1e-3)
    assert fit["used"]["pitch_deg"] == pytest.approx(math.degrees(math.atan(6.0 * T30 / 4.0)), abs=0.01)
    assert sorted(p["aspect_deg"] for p in d["planes"]) == pytest.approx([90.0, 270.0])   # still along the drawn line


def test_a_reliable_profile_without_a_ridge_height_sets_the_ridge():
    prof = {"region_id": "r9", "cut_axis": "x", "method": "vector", "points": [[0, 3.0], [6, 5.0], [12, 3.0]]}
    d = R.derive(_gable(profile=prof, pitches_deg=[_v(40.0, "derived")]), _top())
    fit = d["section_fit"]
    assert fit["status"] == "followed" and fit["drawn"]["ridge_source"] == "profile peak"
    assert d["ridge_z"] == pytest.approx(5.0, abs=1e-3) and fit["points_compared"] is True
    for s, z in prof["points"]:                                    # the built silhouette is the drawn section
        assert R.roof_silhouette(d["equations"], d["outline"], (1.0, 0.0), (0.0, 1.0), s) == pytest.approx(z, abs=2e-3)


def test_a_ridge_no_pitch_can_reach_keeps_the_derived_roof_and_says_why():
    d = R.derive(_gable(ridge_height=_v(20.0)), _top())
    fit = d["section_fit"]
    assert fit["status"] == "kept_derived" and fit["follows_section"] is False and fit["change"] is None
    assert fit["used"] == fit["derived"] and d["ridge_z"] == pytest.approx(3.0 + 4.0 * T30)
    assert any("no pitch from 5 to 60 degrees reaches the drawn ridge 20.000 m" in r for r in fit["reasons"])
    assert any("the pitches are kept: no pitch" in w for w in d["warnings"])


def test_an_assumed_ridge_height_is_no_target():
    d = R.derive(_gable(ridge_height={"value": 9.0, "method": "assumed", "confidence": 0.0}), _top())
    assert d["section_fit"] is None and d["ridge_z"] == pytest.approx(3.0 + 4.0 * T30)


def test_shed_and_mansard_upper_pitch_follow_the_drawn_ridge():
    shed = R.derive(_gable(type="shed", ridge_height=_v(4.0), pitches_deg=[_v(20.0, "derived")]), _top())
    assert shed["section_fit"]["change"] == "pitch" and shed["ridge_z"] == pytest.approx(4.0, abs=1e-3)
    assert shed["pitches"][0] == pytest.approx(math.degrees(math.atan(1.0 / 8.0)), abs=0.01)
    mansard = {"type": "mansard", "type_source": "plan_roof_lines", "over_level_id": "L1",
               "outline": _rect(0, 0, 16, 12),
               "break_line": _rect(2, 2, 14, 10), "eaves_height": _v(3.5), "ridge_height": _v(7.0),
               "pitches_deg": [_v(40.0), _v(30.0)], "ridge_lines": [], "planes": []}
    m = R.derive(mansard, _top())
    fit = m["section_fit"]
    assert fit["change"] == "pitch" and m["ridge_z"] == pytest.approx(7.0, abs=1e-3)
    assert m["pitches"][0] == pytest.approx(40.0) and fit["used"]["pitch_deg"] < 30.0    # the upper pitch moved
    lower = [p for p in m["planes"] if p["id"].endswith("_lower")]
    assert all(p["slope_deg"] == pytest.approx(40.0, abs=0.01) for p in lower)            # the lower tier stays
    assert any(w.startswith("roof adjusted to follow the drawn section r5: upper pitch 30.0 ->") for w in m["warnings"])


def test_eaves_outline_and_knee_walls_stay_consistent_and_the_roof_closes_over_every_wall():
    # a 10 x 6 m top level, no roof outline (the walls + 0.50 m), the knee wall drawn 1.00 m at the outer wall face, a
    # 45 degree pitch text against a section ridge of 6.80 m: the pitch follows the section; the eaves come from the
    # same knee wall, so the knee wall holds, the outline is the same and the roof covers every wall
    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 6.0), (0.0, 6.0)]
    walls = [{"id": f"w{i}", "level_id": "L1", "start": list(pts[i]), "end": list(pts[(i + 1) % 4]), "thickness": 0.3,
              "exterior": True} for i in range(4)]
    building = {"levels": [{"id": "L1", "elevation": 3.0, "ceiling_height": 2.6}], "walls": walls}
    roof = {"type": "gable", "type_source": "section", "over_level_id": "L1", "outline": None, "overhang": _v(0.5),
            "knee_wall": _v(1.0), "ridge_height": _v(6.8), "pitches_deg": [_v(45.0, "ocr")], "ridge_lines": [],
            "planes": []}
    before = R.derive(dict(roof, ridge_height=None), building)
    m = R.roof_model(roof, building)
    assert m["section_fit"]["status"] == "followed" and m["ridge_z"] == pytest.approx(6.8, abs=1e-3)
    assert m["outline"] == before["outline"]
    assert m["knee_wall_check"]["difference"] == pytest.approx(0.0, abs=1e-3)
    assert not any("knee wall" in w for w in m["warnings"])
    for w in walls:                                                  # the outer face of every wall is under the roof
        mid = G.segment_midpoint(w["start"], w["end"])
        nx, ny = G.unit_normal_left(w["start"], w["end"])
        for s in (1.0, -1.0):
            assert R.covers(m, mid[0] + s * nx * 0.15, mid[1] + s * ny * 0.15)
    assert R.is_convex(m["planes"])


def test_argus_reads_the_new_roof_lines_by_their_weight():
    # the auditor's warning rules (wenart/audit/process.py): a ridge within tolerance is noise (info), a section that
    # cannot be checked point by point is a minor process point, a roof kept far from its section stays major
    from wenart.audit.process import classify
    real06 = R.derive(_real06_roof(), _top())["warnings"]
    rules = {classify(w)[:2] for w in real06 if "section" in w or "ridge" in w}
    assert rules == {("drawn_mismatch", "info"), ("not_checked", "minor")}
    far = R.derive(_gable(ridge_height=_v(20.0)), _top())["warnings"]
    assert ("drawn_mismatch", "major") in {classify(w)[:2] for w in far}
    adjusted = R.derive(_gable(ridge_height=_v(5.0), pitches_deg=[_v(45.0, "ocr")]), _top())["warnings"]
    assert [classify(w)[:2] for w in adjusted] == [("read_by", "info")]


# --------------------------------------------------------------------------
# The section's reliability
# --------------------------------------------------------------------------

def test_section_reliability():
    outline = _rect(0, 0, 12, 8)
    rect = {"u": (1.0, 0.0), "v": (0.0, 1.0)}

    def check(points):
        prof = R.section_profile({"profile": {"cut_axis": "x", "points": points}}, rect)
        return R.section_reliability(prof, outline, "x")

    assert check([[0, 3.0], [6, 5.0], [12, 3.0]]) == (True, [])
    assert check([[-0.2, 3.0], [6, 5.0], [12.2, 3.0]])[0] is True                 # a longer drawn overhang: within tol
    ok, why = check([[0, 3.0], [3, 4.0], [3.1, 3.2], [6, 5.0], [12, 3.0]])     # a truss line under the roof
    assert not ok and "drops 0.80 m at s 3.10 m" in why[0]
    ok, why = check([[0, 3.0], [7, 5.0], [14, 3.0]])                             # 2 m past the plan
    assert not ok and "2.00 m apart" in why[0]
