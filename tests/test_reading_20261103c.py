"""3 Nov 2026, evening: the real10 L-1 right flat (user: "fix the L-1 right flat") and the user's new drawings
real16-real21 (user: "We check also these drawings"; real19 "r3 ground, r4-r6 upper", real20 "Two different
buildings"). CPU only."""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import LineString


def test_a_thick_stub_beside_a_wall_in_a_band_wider_than_any_wall_is_no_wall_piece():
    """real10 L-1: a stair line 0.57 m off the core wall's long face, beside the 0.31 m antre wall, made a 0.88 m band
    that swallowed the antre's wall: the stub goes, the wall stays; a pier beside a long wall keeps its pair."""
    from wenart.ingest.generic import walls as W

    def line(off, s0, s1):
        return W._Line(off, s0, s1, [f"L{off}"])

    u, n = (0.0, 1.0), (-1.0, 0.0)
    lines = [line(12.916, 7.94, 8.79), line(13.486, 7.79, 9.40), line(13.796, 7.79, 9.51)]
    pairs = W._pairs_of(lines, "SIVA", u, n)
    W.stepped_runs(pairs)
    kept = W._drop_wide_bands(pairs)
    widths = sorted(round(p.width, 2) for p in kept)
    assert 0.57 not in widths and 0.31 in widths
    # a 0.25 m pier stub on a long wall face (band 0.45 m): kept
    lines = [line(0.0, 0.0, 4.0), line(0.25, 0.0, 4.0), line(0.45, 1.0, 1.5)]
    pairs = W._pairs_of(lines, "SIVA", u, n)
    W.stepped_runs(pairs)
    assert len(W._drop_wide_bands(pairs)) == len(pairs)


def test_a_band_crossed_by_evenly_spaced_treads_is_a_flight_not_a_wall():
    from wenart.ingest.generic import walls as W

    u, n = (0.0, 1.0), (-1.0, 0.0)
    a, b = W._Line(0.0, 0.0, 2.0, ["a"]), W._Line(0.5, 0.0, 2.0, ["b"])
    pair = W._Pair("SIVA", u, n, 0.0, 2.0, (a, b))
    # n = (-1, 0): the lines sit at x = -0.0 and x = -0.5; treads cross from x -0.6 to 0.1 every 0.28 m
    treads = [LineString([(-0.6, y), (0.1, y)]) for y in (0.2, 0.48, 0.76, 1.04)]
    assert W._drop_flight_pairs([pair], treads) == []
    assert W._drop_flight_pairs([pair], treads[:2]) == [pair]             # two jambs: still a wall


def test_the_core_keeps_out_of_every_mirror_step():
    """real10 L-1: the mirror's thickness step thinned the lift's walls to their twins' (0.77 -> 0.25 m) and the lift
    merged with the stair and the hall; no mirror fix touches the core."""
    from shapely.geometry import Point

    from wenart.ingest.generic import mirror as M
    from wenart.ingest.model import WallItem

    def wall(x0, y0, x1, y1, t):
        return WallItem(start=(x0, y0), end=(x1, y1), thickness=t, box=[], entity=f"w{x0}", evidence={"method": "vector"})

    walls = [wall(0, 0, 10, 0, 0.25), wall(0, 6, 10, 6, 0.25), wall(0, 0, 0, 6, 0.25), wall(10, 0, 10, 6, 0.25),
             wall(2, 2, 2, 4, 0.77), wall(8, 2, 8, 4, 0.25)]
    out = M.consistency([w for w in walls], [], axis=("x", 5.0), steps=("thickness",),
                        keep_out=Point(2, 3).buffer(1.0))
    thick = [w.thickness for w in (out[0] if out else walls) if w.entity == "w2"]
    assert thick == [0.77]


def test_the_users_level_names_an_untitled_plan_by_its_box_or_leaves_it_out():
    from wenart.sheets import levels as LV

    def plan(rid, box):
        return SimpleNamespace(id=rid, file="a.dwg", box=box, title=None, evidence=[], level=None, use="read",
                               ignored_reason=None)

    plans = [plan("r3", [0, 0, 10, 10]), plan("r4", [20, 0, 30, 10]), plan("r5", [40, 0, 50, 10])]
    user = [{"box": [0.2, 0, 10, 10.1], "level": "Zemin Kat"}, {"box": [20, 0, 30, 10], "level": "1. Kat"},
            {"box": [40, 0, 50, 10], "level": "ignore"}]
    needs, warns = [], []
    LV.assign_levels(plans, needs, warns, user_levels=user)
    assert [(r.id, r.level["id"]) for r in plans] == [("r3", "L0"), ("r4", "L1")] and not needs
    assert any("plan_levels" in w for w in warns)


def test_a_unit_one_check_decides_strongly_wins_a_tie_with_a_unit_no_check_decides():
    """real20: no header unit; the door widths say cm from 47 swings (0.98); a wall-thickness share of 0.55, the text
    height and the drawing size fit inches as well."""
    from wenart.sheets import units_check as U

    checks = [U.Check("door_widths", "cm", 0.98, 47, shares={"cm": 0.98}),
              U.Check("wall_thickness", None, 0.55, 569, shares={"cm": 0.49, "in": 0.55}),
              U.Check("text_height", None, None, 234, values=[10.0] * 30)]
    drawings = [SimpleNamespace(geometry_box=[0, 0, w, 100], ents=[0] * 60) for w in (1894, 2922)]
    assert U.tie_break(checks, drawings)[0] == "cm"
    weak = [U.Check("door_widths", "cm", 0.6, 8, shares={"cm": 0.6})] + checks[1:]
    assert U.tie_break(weak, drawings) is None


def test_a_sheet_with_a_plan_the_brief_leaves_out_is_read_by_its_regions():
    from wenart.sheets import multi_region

    sheet = SimpleNamespace(id="s1")
    regions = [SimpleNamespace(file="a.dwg", sheet=sheet, use="read", ignored_reason=None),
               SimpleNamespace(file="a.dwg", sheet=sheet, use="ignored",
                               ignored_reason="the user's brief leaves this plan out (plan_levels: ignore)")]
    assert multi_region(regions)
    regions[1].ignored_reason = "no title and no geometry rule gives a class"
    assert not multi_region(regions)


def test_a_free_end_cast_hits_side_by_side_stubs_and_frame_caps():
    """real10 L-1 (user: "fix the antre and kitchen"): the right kitchen's door jamb is two stubs side by side (7 and 3 cm
    of the 16 cm wall), one of them a frame cap; its left twin's single stub covers 9 cm. Together, and with the cap
    counted, they stop the cast from the wall's free end, so the kitchen door gap is read."""
    from wenart.ingest.generic import openings as O

    wall = O.Piece(k=0, axis="h", c=6.49, t=0.16, a=13.76, b=14.828, wall=None)
    stub = O.Piece(k=1, axis="v", c=15.906, t=0.21, a=6.37, b=6.44, wall=None)        # 3 cm of the band
    cap = O.Piece(k=2, axis="v", c=15.881, t=0.14, a=6.44, b=6.509, wall=None)        # 7 cm of the band
    assert O._cast(wall, "end", [wall, stub]) is None                                 # the stub alone: too little
    hit = O._cast(wall, "end", [wall, stub], [cap])
    assert hit is not None and abs(hit[2] - 15.801) < 0.02 and abs(hit[1] - 14.828) < 1e-9
