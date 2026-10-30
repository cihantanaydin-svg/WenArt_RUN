"""UL158 (30 Oct 2026, real04 run 20261030-043021-full): "I did not like this white thing extending like this, what I
was asking the same as old one but reaching all the way to the other pool". An Argus edit had set the site's
front_court to yes: the paved strip at the foot of the basement glazing (sill 3 cm under the lawn) became a 3 m sunken
court with 0.9 m white parapets. Pure tests: the rules are general, real04 is only the test case."""
from wenart.blender import exterior_checks as X
from wenart.blender import site as S

FLAT = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _house(sill: float):
    """A basement level at -3 m with a long window on its south wall, the ground outside at 0 (flat terrain)."""
    building = {"walls": [{"id": "w1", "level_id": "L-1", "start": [0, 0], "end": [16, 0], "thickness": 0.2}],
                "openings": [{"id": "win_b", "type": "window", "wall_id": "w1", "level_id": "L-1", "center": [11.4, 0],
                              "position": [11.4, 0], "width": 7.0, "sill_height": sill, "height": 2.4}]}
    levels = [{"id": "L-1", "elevation": -3.0, "ceiling_height": 2.8},
              {"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}]
    return building, levels, _rect(0, 0, 16, 12)


def test_yes_never_sinks_a_court_in_front_of_glazing_at_grade():
    building, levels, outline = _house(sill=2.97)                    # the sill 3 cm under the ground
    wells, _ = S.light_wells(building, levels, FLAT, outline, front_court="yes")
    assert len(wells) == 1 and wells[0].get("kind") != "front_court"
    assert "no sunken court at grade" in wells[0]["reason"]
    b2, l2, o2 = _house(sill=1.2)
    deep, _ = S.light_wells(b2, l2, FLAT, o2, front_court="yes")
    assert len(deep) == 1 and deep[0]["kind"] == "front_court"   # a window 1.8 m under the ground still gets one
    assert S.COURT["yes_min_below"] <= 0.5


def test_the_strip_runs_on_along_its_facade_to_the_next_paved_floor_and_meets_it():
    building = {"walls": [{"id": "w1", "level_id": "L0", "start": [0, 0], "end": [20, 0], "thickness": 0.2}],
                "openings": [{"id": "win_a", "type": "window", "wall_id": "w1", "level_id": "L0", "center": [6.0, 0],
                              "width": 4.0},
                             {"id": "win_b", "type": "window", "wall_id": "w1", "level_id": "L0", "center": [11.0, 0],
                              "width": 4.0}]}
    levels = [{"id": "L0", "elevation": 0.0}]
    outline = _rect(0, 0, 20, 12)
    well = {"opening_id": "win_b", "polygon": [(8.8, -0.9), (13.2, -0.9), (13.2, -0.1), (8.8, -0.1)],
            "outward": [0.0, -1.0], "source": "assumed"}
    pool_deck = {"id": "deck_w", "polygon": _rect(-4.0, -4.0, 1.3, 0.0)}      # 2.5 m past the run's west end
    far_deck = {"id": "deck_e", "polygon": _rect(22.0, -4.0, 26.0, 0.0)}      # past the house's corner: never
    aprons, runs = S.facade_aprons(building, levels, outline, None, [well], [pool_deck, far_deck])
    xs = sorted(round(x, 2) for a in aprons for x, _y in a["polygon"])
    assert xs[0] <= 1.3 and xs[0] >= 1.3 - 0.02                    # meets the deck's edge: no lawn between
    east = max(x for a in aprons for x, _y in a["polygon"])
    assert east <= 20.1 + 1e-6                                       # never past the corner towards deck_e
    assert runs[0]["covered_ids"] == ["win_a", "win_b"]


def test_an_edit_may_not_force_front_courts():
    out = X.front_court_problems({"path": True, "fence": "hedge", "trees": 8, "front_court": "yes"})
    assert out and "never an edit's" in out[0]
    assert X.front_court_problems({"front_court": "auto"}) == [] and X.front_court_problems({}) == []
    verdict = X.validate_exterior_override({"walls": [], "levels": []},
                                           {"site": {"path": True, "front_court": "yes"}})
    assert not verdict["ok"] and any("front_court" in f for f in verdict["failed"])
