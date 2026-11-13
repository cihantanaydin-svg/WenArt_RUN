"""The fixes of the stage-1 fix check (13 Nov 2026, findings S1F-POD-*, FC-*, CODE-*): CPU only, synthetic fixtures."""
from types import SimpleNamespace

import pytest
from shapely.geometry import Point, Polygon

from wenart.blender import parametric as P
from wenart.ingest import completion as CP
from wenart.ingest import core_rules as CR
from wenart.ingest import ground_lines as GL


# --------------------------------------------------------------------------- S1F-POD-P01: the inferred U stair
@pytest.mark.parametrize("length", [3.6, 4.0, 4.4, 4.75, 5.2, 6.0])
@pytest.mark.parametrize("rot", [0.0, 90.0, 33.0])
def test_inferred_u_stair_flights_stand_on_the_landing(length, rot):
    """Both flights of an inferred U stair end on the landing's near edge at the landing's level (riser line to riser
    line), the landing is as deep as stair_dict made it (no lane added), and the stair passes RC16."""
    fp = {"center": [6.37, 14.0], "size": [1.8, length], "rotation_deg": rot}
    st = CR.stair_dict(fp, "test", "U", 3.0)
    piece = {"id": "s", "type": "stair", "level_id": "L0", "stair": st, "footprint": dict(fp)}
    plan = P.stair_plan(piece, 3.0, 2.8, 2.8 + P.STAIR_SHAFT_CAP_M, [])
    assert plan["integrity"] == []
    lp = Polygon(plan["landing"]["polygon"])
    f0, f1 = plan["flights"]
    assert lp.distance(Point(f0["nosings"][-1])) <= 0.03 and abs(f0["top_z"] - plan["landing"]["z"]) < 1e-6
    assert lp.distance(Point(f1["nosings"][0])) <= 0.03 and abs(f1["base_z"] - plan["landing"]["z"]) < 1e-6
    assert lp.area == pytest.approx(1.8 * st["landing"]["depth"], rel=0.02)
    assert plan["risers"] == CR.risers_for(3.0)


@pytest.mark.parametrize("length", [3.6, 4.75, 6.0])
def test_inferred_stairs_without_rise_and_straight_pass_rc16(length):
    for turn, width in (("U", 1.8), ("straight", 1.1)):
        for rise in (None, 2.8):
            fp = {"center": [0.0, 0.0], "size": [width, length], "rotation_deg": 0.0}
            st = CR.stair_dict(fp, "test", turn, rise)
            piece = {"id": "s", "type": "stair", "level_id": "L0", "stair": st, "footprint": dict(fp)}
            plan = P.stair_plan(piece, rise or 3.0, (rise or 3.0) - 0.2, (rise or 3.0) - 0.2 + P.STAIR_SHAFT_CAP_M, [])
            assert plan["integrity"] == [], (turn, rise, plan["integrity"])


# --------------------------------------------------------------------------- S1F-POD-P03: the ground and the doors
def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _storey(lid, order, z, doors=True, kind=None):
    walls = [{"id": f"w_{lid}_{s}", "level_id": lid, "start": list(a), "end": list(e), "thickness": 0.2,
              "exterior": True}
             for s, a, e in (("s", (0, 0), (10, 0)), ("e", (10, 0), (10, 8)), ("n", (10, 8), (0, 8)), ("w", (0, 8), (0, 0)))]
    rooms = [{"id": f"r_{lid}", "level_id": lid, "label": "SALON", "room_type": "living", "polygon": _rect(0, 0, 10, 8)}]
    ops = [{"id": f"d_{lid}_1", "type": "door", "level_id": lid, "wall_id": f"w_{lid}_s", "center": [5.0, 0.0],
            "width": 1.0, "height": 2.1, "evidence": [{"method": "vector"}]}] if doors else []
    lv = {"id": lid, "label": lid, "order": order, "elevation": z, "ceiling_height": 2.7}
    if kind:
        lv["kind"] = kind
    return lv, walls, rooms, ops


def _ground_building(ground_z, lines, basement_doors=True):
    parts = [_storey("L-1", -1, -2.5, basement_doors, "basement"), _storey("L0", 0, 0.0), _storey("L1", 1, 3.0),
             _storey("L2", 2, 6.0)]
    b = {"levels": [p[0] for p in parts], "walls": [w for p in parts for w in p[1]],
         "rooms": [r for p in parts for r in p[2]], "openings": [o for p in parts for o in p[3]], "furniture": [],
         "warnings": [], "level_inference": {},
         "site": {"ground": {"levels": [{"side": "all", "azimuth_deg": None,
                                         "z": {"value": ground_z, "method": "vector", "confidence": 1.0,
                                               "evidence": [{"file": "x.dwg", "entity": "LINE:TOP", "method": "vector",
                                                             "rule": "ground_line", "region_id": "r6"}],
                                               "lines": lines}}],
                             "surface": {"kind": "flat", "flat_z": ground_z, "source": "section"}}}}
    conflicts = []
    build = SimpleNamespace(building=b, conflict=lambda *a: conflicts.append(a), warn=b["warnings"].append)
    return build, conflicts


LINES = [{"side": s, "z": z, "entity": f"LINE:{s[0]}{k}"} for k, z in enumerate((11.11, 9.03, 6.03, 3.03, 0.03, -0.1,
                                                                                  -2.47)) for s in ("left", "right")]


def test_a_ground_burying_storeys_with_doors_takes_the_line_beside_the_doors_at_grade():
    build, conflicts = _ground_building(11.11, LINES)
    rec = GL.apply(build)
    b = build.building
    assert rec is not None and rec["z"] == -2.47 and rec["at"] == "L-1" and rec["chosen"]["both_sides"]
    assert {"L0", "L1", "L2"} <= set(rec["storeys"]) and rec["refused"][0]["value"] == 11.11
    (entry,) = b["site"]["ground"]["levels"]
    assert entry["z"]["value"] == -2.47 and entry["z"]["method"] == "vector"
    assert entry["adjusted_by_ai"]["rule"] == "ground_doors" and b["site"]["ground"]["surface"]["flat_z"] == -2.47
    assert conflicts and not b.get("needs_review")
    assert CP.below_ground(b, b["levels"][1]) is None                      # L0 is no longer under the ground


def test_without_basement_doors_the_ground_floor_line_is_the_ground():
    build, _ = _ground_building(11.11, LINES, basement_doors=False)
    rec = GL.apply(build)
    assert rec["z"] == 0.03 and rec["at"] == "L0"


def test_no_line_beside_the_doors_assumes_a_step_and_asks():
    lines = [ln for ln in LINES if ln["z"] > 5]
    build, _ = _ground_building(11.11, lines)
    rec = GL.apply(build)
    b = build.building
    assert rec["chosen"] is None and rec["z"] == -0.15
    assert b["site"]["ground"]["levels"][0]["z"]["method"] == "assumed"
    assert [x["kind"] for x in b["needs_review"]] == ["ground_doors"]


def test_a_ground_at_the_doors_or_a_basement_under_the_ground_stays():
    for gz in (-2.5, -0.15, 1.0):          # 1.0: buries the basement's doors only (a basement may be under the ground)
        build, conflicts = _ground_building(gz, LINES)
        assert GL.apply(build) is None and not conflicts
        assert build.building["site"]["ground"]["levels"][0]["z"]["value"] == gz


def test_the_ground_rule_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("WENART_RULES_OFF", "ground_doors")
    build, _ = _ground_building(11.11, LINES)
    assert GL.apply(build) is None
    assert build.building["site"]["ground"]["levels"][0]["z"]["value"] == 11.11
