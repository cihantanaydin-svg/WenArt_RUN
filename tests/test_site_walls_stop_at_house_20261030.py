"""No site wall through the house (30 Oct 2026, lesson UL148, user on real04 run 20261029-201533-full: "this seems to be
coming from the outside texture, it is in the kitchen": the retaining wall and coping of the stepped band sp_001_s1e2
ran along the house's outer wall and their ends came through it into the basement kitchen)."""
from wenart.blender import site as S

HOUSE = [(0.0, 0.0), (15.0, 0.0), (15.0, 12.0), (0.0, 12.0)]


def test_a_wall_along_the_house_corner_stops_at_its_outline():
    # the band's edge runs north along x = 0 from the house corner (y 11.8, inside the outline up to y 12.0)
    cuts = S.wall_cut_spans((0.0, 11.8), (0.0, 13.0), [HOUSE])
    assert len(cuts) == 1 and cuts[0][0] == 0.0
    t, over = S.PLATFORM["wall_t"], S.GR.GRADE["coping_over"]
    assert cuts[0][1] >= 0.2 + t / 2.0 + over - 1e-6                   # past the outline by the piece's end reach
    assert cuts[0][1] < 1.2                                            # the rest of the wall stays


def test_a_wall_clear_of_the_house_is_not_cut():
    assert S.wall_cut_spans((-3.0, 13.0), (-3.0, 15.0), [HOUSE]) == []
    assert S.wall_cut_spans((0.0, 11.8), (0.0, 13.0), []) == []


def test_the_uncut_stretches_skip_the_cuts():
    parts = S._uncut((0.0, 0.0), (0.0, 4.0), [[0.0, 0.5], [1.5, 2.0]])
    assert [(round(a[1], 3), round(b[1], 3)) for a, b in parts] == [(0.5, 1.5), (2.0, 4.0)]
