"""The fixes of the stage-1 fix check (13 Nov 2026, findings S1F-POD-*, FC-*, CODE-*): CPU only, synthetic fixtures."""
import pytest
from shapely.geometry import Point, Polygon

from wenart.blender import parametric as P
from wenart.ingest import core_rules as CR


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
