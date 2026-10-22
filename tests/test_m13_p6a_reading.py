"""Fix round after P6a (22 Oct 2026; pod P6a, real04), track F_reading: the coat closet and the rug group.

Every test here fails on BASE (commit 52d4bb8) or names the mutation it guards. The shapes are measured on real04's
strokes (``projects/real04/deneme1.dwg`` converted with LibreDWG 0.14 in this session):

- a hanger is the group of pieces that touch, judged as a whole: real04 draws each hanger as a hook loop around a
  double rail (0.05 x 0.07 m) and two bulged arms ending on the loop, short of the rail; the P5 rule tested one
  piece at a time and found none, so the corridor coat closets f_L1_021 / f_L1_024 stayed a coffee table with two
  "chairs" (one through the wall into the terrace);
- a table with its chairs drawn on a rug outline is read as the table (round when a circle fits it), its chairs and a
  rug mark (not built, ``inferred_as: rug``), also when the whole block is one part whose box fits a type (real04's
  play-room sets f_L1_017/018: 1.63 x 1.52 m, asked as bed / stair, left unknown, marked not furniture by the agent);
  a bed, a table without a rug, an L sofa with its cushions and a rug with one chair are read as before;
- a chair whose centre lies within a round table's box (diagonal) faces the side its offset points to, so the chairs
  of mirrored twin blocks are mirror images and the twin rooms still pair (the U16 copy types the twin's bench);
- a candidate the AI passes leave unknown is read whole before the re-read when it is a coat closet or a rug set
  (real02's first closet: its hanger inserts were cut off as two "details" and it stayed a table with two chairs).

Checked on the real strokes (CPU replays of the ingest with the runs' answers, LibreDWG 0.14 here): real04 with P6a's
answers changes only f_L1_017/018 (table, two chairs, rug mark each) and the closets f_L1_021/024 (two wardrobes, 14
hangers each, no chairs); its 74 other questions keep their input and crop hashes (8 L1 keys renumber, their answers
follow by input hash); real03 with P4b's answers is unchanged; real02 with P4a's answers gets the same rug sets and
both closets as wardrobes.
"""
from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

import _m11_room as M
import _real01_page as R
from wenart.ingest.generic import core as CORE
from wenart.ingest.generic import reading as RD
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.pipeline import ProjectBuild

TABLE = SY.FALLBACK_SIZE_TABLE


def _poly(sid, pts, closed=False, block=None, kind="polyline"):
    return Stroke(id=sid, kind=kind, pts=[(float(x), float(y)) for x, y in pts], closed=closed, block=block)


# --------------------------------------------------------------------------
# The coat closet: a hanger is the group of pieces that touch
# --------------------------------------------------------------------------

def _hanger(prefix: str, x: float) -> list[Stroke]:
    """One real04 hanger at ``x`` (INSERT:37516/3, /4:0..2, /5:0..2): a closed hook loop 0.046 x 0.072 m around the
    double rail (y 0.29 / 0.31), a lower arm (three pieces: line, arc, line) from the loop down to y 0.08 and back,
    an upper arm up to y 0.49 and back; no single piece crosses the rail line."""
    hook = [(x + 0.023 * math.cos(2 * math.pi * k / 24), 0.297 + 0.036 * math.sin(2 * math.pi * k / 24))
            for k in range(24)]
    low = [[(x - 0.010, 0.265), (x + 0.007, 0.174), (x + 0.033, 0.085)],
           [(x + 0.033, 0.085), (x + 0.049, 0.078), (x + 0.055, 0.095)],
           [(x + 0.055, 0.095), (x + 0.023, 0.177), (x + 0.005, 0.262)]]
    up = [[(x - 0.010, 0.329), (x + 0.004, 0.408), (x + 0.028, 0.486)],
          [(x + 0.028, 0.486), (x + 0.045, 0.493), (x + 0.050, 0.475)],
          [(x + 0.050, 0.475), (x + 0.020, 0.406), (x + 0.005, 0.331)]]
    out = [_poly(f"{prefix}/0", hook, closed=True)]
    out += [_poly(f"{prefix}/1:{j}", pts, kind="arc" if j == 1 else "polyline") for j, pts in enumerate(low)]
    out += [_poly(f"{prefix}/2:{j}", pts, kind="arc" if j == 1 else "polyline") for j, pts in enumerate(up)]
    return out


def _real04_closet(n: int = 14, plank_at: float | None = None):
    """real04's corridor coat closet (f_L1_021 + f_L1_022/023): a 1.517 x 0.60 m outline, a double rail 2 cm apart
    on its centre line, ``n`` hangers 0.095 m apart, two chair-sized parts at its ends (the M11 split's "chairs");
    ``plank_at``: a line across the whole depth touching the first hanger's loop."""
    strokes = [_poly("o", [(0.0, 0.0), (1.517, 0.0), (1.517, 0.6), (0.0, 0.6)], closed=True),
               _poly("rail_a", [(0.02, 0.29), (1.497, 0.29)]), _poly("rail_b", [(0.02, 0.31), (1.497, 0.31)]),
               _poly("c1", [(-0.45, 0.1), (-0.05, 0.1), (-0.05, 0.5), (-0.45, 0.5)], closed=True),
               _poly("c2", [(1.57, 0.1), (1.97, 0.1), (1.97, 0.5), (1.57, 0.5)], closed=True)]
    for k in range(n):
        strokes += _hanger(f"INSERT:h{k}", 0.10 + 0.095 * k)
    if plank_at is not None:
        strokes.append(_poly("plank", [(plank_at, 0.0), (plank_at, 0.6)]))
    return SY.Cluster(SY._segments(strokes, set()))


def _outline(part):
    return max(SY.top_contours(part), key=lambda tm: tm[0].area)[0]


def test_a_real04_coat_closet_with_hook_and_arm_hangers_is_one_wardrobe():
    """Fails on BASE: no piece of a real04 hanger crosses the rail and spans 30 % of the depth on its own (the hook is
    0.07 m, the arms end short of the rail), so BASE counted 0 hangers and split the closet into a coffee table and
    two chairs. Now each touching group is one hanger: 14, one wardrobe of the outline's size, no chairs."""
    part = _real04_closet()
    rail = SY.hanging_rail(part.segs, _outline(part), 0.0)
    assert rail is not None and rail["hangers"] == 14 and rail["rail"] in ("rail_a", "rail_b")
    split = SY.split_table_chairs(part, TABLE, 0.0)
    assert split is not None and split.get("wardrobe") and split["chairs"] == []
    made = SY.table_chair_items(split, SY._Ctx("t.dxf", None, None, 0.0, "L1"), False, TABLE)
    assert [m.type for m in made] == ["wardrobe"] and made[0].type_method == "rule"
    assert sorted(round(v, 3) for v in made[0].size) == [0.6, 1.517]
    # Below HANGER_MIN hangers the closet rule does not fire: a table outline with a rail and three hangers stays a
    # table with its chairs.
    few = SY.split_table_chairs(_real04_closet(n=3), TABLE, 0.0)
    assert few is not None and not few.get("wardrobe") and len(few["chairs"]) == 2


def test_a_wall_to_wall_line_never_joins_a_hanger():
    """Mutation guard (``wall_to_wall`` in ``hanging_rail``): a line across the whole depth (an outline end, a plank)
    touching a hanger's loop would join it into one group spanning the depth and lose that hanger (13)."""
    part = _real04_closet(plank_at=0.10 + 0.023)
    assert SY.hanging_rail(part.segs, _outline(part), 0.0)["hangers"] == 14


def test_neighbouring_hangers_that_touch_are_one_place_and_the_synthetic_p5_closet_still_counts_twelve():
    """The P5 pin (V-shaped hangers, each piece ending on the rail) still gives 12; two hangers whose loops touch
    are one group (one place along the rail), so they never count twice."""
    from test_m13_p5_furniture import _closet

    assert SY.split_table_chairs(_closet(), TABLE, 0.0)["wardrobe"]["hangers"] == 12
    strokes = [_poly("o", [(0.0, 0.0), (1.517, 0.0), (1.517, 0.6), (0.0, 0.6)], closed=True),
               _poly("rail", [(0.02, 0.30), (1.497, 0.30)])]
    for k in range(5):
        strokes += _hanger(f"INSERT:h{k}", 0.10 + 0.25 * k)
    strokes += _hanger("INSERT:twin", 0.10 + 0.25 * 4 + 0.040)          # its loop touches hanger 4's loop
    part = SY.Cluster(SY._segments(strokes, set()))
    assert SY.hanging_rail(part.segs, _outline(part), 0.0)["hangers"] == 5


def _candidate(part, key="sym_L1_005", ai=("unknown", "bench")):
    from wenart.ingest.model import FurnitureItem

    fp = SY.footprint([p for s in part.segs for p in s.pts], 0.0)
    item = FurnitureItem(type="unknown", type_raw=None, center=fp[0], size=(fp[1], fp[2]), rotation_deg=0.0,
                         front_deg=None, box=[0, 0, 1, 1], entity=part.stroke_ids()[0], evidence={"entity": "x"},
                         status="unverified", type_method="none", details={"candidate_key": key},
                         type_candidates=[{"type": t, "model": m, "pass": k + 1, "confidence": 0.8}
                                          for k, (t, m) in enumerate(zip(ai, ("qwen", "glm")))])
    return {"key": key, "item": item, "_part": part}


def test_a_closet_candidate_left_unknown_by_its_answers_is_read_whole_before_the_re_read():
    """Fails on BASE: real02's first corridor closet was asked (its box fits a type), the passes said unknown / bench,
    and the re-read cut the part by block instance: the hanger inserts became two not-built "details" and the
    outline a coffee table with two chairs (unlike its twin, read whole at the gate). Now the whole part is read
    first: one wardrobe, the question unchanged (``reread_of``). A plain table with chairs still goes to the re-read
    (it splits there by block instance and stroke group, as before)."""
    from wenart.ingest.model import LevelExtraction

    strokes = [_poly("o", [(0.0, 0.0), (1.517, 0.0), (1.517, 0.6), (0.0, 0.6)], closed=True),
               _poly("rail_a", [(0.02, 0.29), (1.497, 0.29)]), _poly("rail_b", [(0.02, 0.31), (1.497, 0.31)]),
               _poly("c1", [(-0.45, 0.1), (-0.05, 0.1), (-0.05, 0.5), (-0.45, 0.5)], closed=True),
               _poly("c2", [(1.57, 0.1), (1.97, 0.1), (1.97, 0.5), (1.57, 0.5)], closed=True)]
    for k in range(14):
        strokes += [Stroke(id=st.id, kind=st.kind, pts=st.pts, closed=st.closed, block="askilik")
                    for st in _hanger(f"INSERT:{37516 + k // 7}/{k % 7}", 0.10 + 0.095 * k)]
    part = SY.Cluster(SY._segments(strokes, set()))
    ex = LevelExtraction(file="t.dxf", page=1, level_id="L1", units="mm", report={"pending": [], "answers_applied": 2})
    replaced, _loose = CORE._reread_unknowns(ex, [_candidate(part)], [], [], [], [], [], [], "L1", "t.dxf", None, 1.0,
                                             False, False, strokes_m=strokes)
    made = replaced["sym_L1_005"]
    assert [m.type for m in made] == ["wardrobe"] and made[0].details["reread_of"] == "sym_L1_005"
    assert made[0].details["hanging_rail"]["hangers"] == 14
    assert any("coat closet" in n and "one wardrobe" in n for n in ex.notes)
    from test_m11_split import _table_with_chairs
    plain = SY.Cluster(SY._segments(_table_with_chairs(prefix="g"), set()))
    ex2 = LevelExtraction(file="t.dxf", page=1, level_id="L1", units="mm", report={"pending": [], "answers_applied": 2})
    replaced2, _ = CORE._reread_unknowns(ex2, [_candidate(plain, "sym_L1_006")], [], [], [], [], [], [], "L1",
                                         "t.dxf", None, 1.0, False, False, strokes_m=_table_with_chairs(prefix="g"))
    assert not any("fix round after P6a" in n for n in ex2.notes)


# --------------------------------------------------------------------------
# A table with its chairs on a rug outline
# --------------------------------------------------------------------------

CHAIR_ANGLES = (90.0, 270.0)
# An irregular rug outline (radius by angle, every 30 deg): about 1.50 x 1.70 m, its box fits a double bed.
RUG_RADII = (0.74, 0.80, 0.88, 0.86, 0.90, 0.78, 0.76, 0.82, 0.92, 0.84, 0.86, 0.80)
RUG = [(r * math.cos(math.radians(30 * k)), r * math.sin(math.radians(30 * k))) for k, r in enumerate(RUG_RADII)]


def _chair(prefix: str, first: int, cx: float, cy: float, angle: float, block: str) -> list[Stroke]:
    """A real04 chair (INSERT:37081/1..9) at ``angle`` deg from the table centre ``(cx, cy)``: its curved back drawn
    as a thin closed crescent (0.53 x 0.04 m: no top-level contour) and its two sides as lines from the back towards
    the table; ids ``<prefix>/<first>..+2``."""
    a = math.radians(angle)

    def at(r, d):
        return (cx + r * math.cos(a + math.radians(d)), cy + r * math.sin(a + math.radians(d)))

    back = [at(0.77, d) for d in range(-20, 21, 4)] + [at(0.73, d) for d in range(20, -21, -4)]
    return [_poly(f"{prefix}/{first}", back, closed=True, block=block, kind="curve"),
            _poly(f"{prefix}/{first + 1}", [at(0.73, -16), at(0.47, -16)], block=block, kind="arc"),
            _poly(f"{prefix}/{first + 2}", [at(0.73, 16), at(0.47, 16)], block=block, kind="arc")]


def _rug_set(cx: float = 3.0, cy: float = 2.5, gap: float | None = 0.015, chairs: int = 2, block: str = "rgtghbh",
             prefix: str = "INSERT:37081", rug: list | None = None) -> list[Stroke]:
    """real04's play-room block (f_L1_017): an irregular 1.52 x 1.65 m rug outline (one open curve whose ends are
    ``gap`` apart, or closed with ``gap`` None), a 0.80 m round table (a 16-gon) and ``chairs`` chairs."""
    pts = [(cx + x, cy + y) for x, y in (rug or RUG)]
    if gap is not None:
        pts = pts + [(pts[0][0] + gap, pts[0][1])]
    out = [_poly(f"{prefix}/0", pts, closed=gap is None, block=block, kind="curve"),
           _poly(f"{prefix}/10", [(cx + 0.4 * math.cos(2 * math.pi * k / 16), cy + 0.4 * math.sin(2 * math.pi * k / 16))
                                  for k in range(16)], closed=True, block=block, kind="circle")]
    for k, angle in enumerate(CHAIR_ANGLES[:chairs]):
        out += _chair(prefix, 1 + 10 * k, cx, cy, angle, block)
    return out


def _furn(strokes, notes=None):
    walls = [R.wall((0, 0), (6, 0), 0.2), R.wall((6, 0), (6, 5), 0.2), R.wall((6, 5), (0, 5), 0.2),
             R.wall((0, 5), (0, 0), 0.2)]
    return SY.furniture(strokes, set(), walls, [], [], [], TP.building_outline(walls, []), [], level_id="L1",
                        file_rel="t.dxf", page_no=None, size_table=TABLE, notes=notes)


@pytest.mark.parametrize("gap", [0.015, None])
def test_a_table_with_two_chairs_on_a_rug_outline_is_read_as_the_table_the_chairs_and_a_rug_mark(gap):
    """Fails on BASE: the block is one part whose 1.52 x 1.65 m box fits a double bed, so the M11 split never ran and
    it was asked (real04 f_L1_017/018: bed / stair / unknown / not_furniture; the agent marked both not furniture).
    Now, never asked: the round table, two chairs facing it and a rug mark (not furniture, as "rug")."""
    notes = []
    pieces, cands, _ = _furn(_rug_set(gap=gap), notes)
    assert cands == []
    assert sorted(p.type for p in pieces) == ["chair", "chair", "table_dining", "unknown"]
    table = next(p for p in pieces if p.type == "table_dining")
    assert table.type_method == "rule" and table.details["shape"] == "round"
    assert sorted(table.size) == pytest.approx([0.8, 0.8], abs=0.02)            # a 16-gon of radius 0.40 m
    assert table.center == pytest.approx((3.0, 2.5), abs=0.01)
    assert "rug outline" in table.evidence["note"] and table.entity == "INSERT:37081/10"
    for chair in (p for p in pieces if p.type == "chair"):
        to_table = math.degrees(math.atan2(2.5 - chair.center[1], 3.0 - chair.center[0])) % 360.0
        assert min(abs(chair.front_deg - to_table) % 360.0, 360.0 - abs(chair.front_deg - to_table) % 360.0) <= 45.0
    rug = next(p for p in pieces if p.type == "unknown")
    assert rug.details["not_furniture"]["as"] == "rug" and rug.entity == "INSERT:37081/0"
    assert rug.details["rug_outline"]["fill"] < SY.RUG_FILL_MAX
    assert any("rug outline is a rug mark" in n for n in notes)


def test_the_chairs_of_mirrored_twin_rug_sets_are_mirror_images():
    """Fails on BASE: a chair whose centre lies within the round table's box on both axes (real04's play-room chairs
    sit diagonally) always faced 180 deg and grew west, so the chairs of the mirrored twin block were 3-5 cm off their
    mirror images and the twin rooms no longer paired (the U16 copy then left the other room's bench untyped). Now it
    stands on the side its offset from the table's centre points to: twins mirror exactly."""
    table = SY.Cluster(SY._segments(_rug_set(chairs=0)[1:], set()))
    tpoly = SY.top_contours(table)[0][0]
    # real04 f_L1_017's chair INSERT:37081/1..9 (box 0.41 x 0.43 m, its centre 0.38 m west and 0.30 m north of the
    # table's centre: inside the table's box) and its mirror image in the twin block
    box = (-0.580, 0.087, -0.175, 0.521)
    left = SY.Cluster(SY._segments([_poly("l", [(3.0 + box[0], 2.5 + box[1]), (3.0 + box[2], 2.5 + box[1]),
                                                (3.0 + box[2], 2.5 + box[3]), (3.0 + box[0], 2.5 + box[3])],
                                         closed=True)], set()))
    right = SY.Cluster(SY._segments([_poly("r", [(3.0 - box[0], 2.5 + box[1]), (3.0 - box[2], 2.5 + box[1]),
                                                 (3.0 - box[2], 2.5 + box[3]), (3.0 - box[0], 2.5 + box[3])],
                                          closed=True)], set()))
    (lc, lw, lh, _la, _), lf = SY.chair_footprint(left, tpoly, 0.0)
    (rc, rw, rh, _ra, _), rf = SY.chair_footprint(right, tpoly, 0.0)
    assert rc[0] == pytest.approx(6.0 - lc[0], abs=1e-6) and rc[1] == pytest.approx(lc[1], abs=1e-6)
    assert sorted((lw, lh)) == pytest.approx(sorted((rw, rh)), abs=1e-6)
    assert (lf, rf) == (0.0, 180.0)                     # the west chair faces east, its twin west


def test_the_rug_mark_is_not_built_and_explained_at_the_reading():
    """The rug mark leaves the reading not built, ``inferred_as: rug`` with its reason and evidence (the decor stage
    lays the rugs; the solver and complete treat it as an outline, never an obstacle), and is not listed for review."""
    pieces, _, _ = _furn(_rug_set())
    item = next(p for p in pieces if p.type == "unknown")
    f = M.fp("f_L1_017", "unknown", item.center, item.size, front=None, status="unverified", type_method="none")
    build = ProjectBuild(M.building(w=6.0, h=5.0, room_type="other", window=None, furniture=[f]))
    RD.move_symbols(build, {"f_L1_017": SimpleNamespace(details=item.details)}, {})
    out = build.building["furniture"][0]
    assert out["build"] is False and out["inferred_as"] == "rug" and out["inferred"] is True
    assert "rug mark" in out["inferred_reason"] and out["evidence"][-1]["rule"] == RD.SYMBOL_RULE
    assert "rug" in RD.EXPLAINED_AS


def test_beds_tables_l_sofas_and_a_rug_with_one_chair_are_read_as_before():
    """Mutation guards: the rug must be irregular (a bed outline holding a duvet contour and two pillows is a
    rectangle), hold everything else clear of its line (an L sofa's cushions touch it), and what it holds must be a
    table with at least two chairs; a table with chairs and no rug is split as before (no rug, no shape)."""
    bed = [_poly("b/0", [(1.0, 1.0), (2.6, 1.0), (2.6, 3.0), (1.0, 3.0)], closed=True),
           _poly("b/1", [(1.05, 1.05), (2.55, 1.05), (2.55, 2.30), (1.05, 2.30)], closed=True),
           _poly("b/2", [(1.15, 2.45), (1.70, 2.45), (1.70, 2.85), (1.15, 2.85)], closed=True),
           _poly("b/3", [(1.90, 2.45), (2.45, 2.45), (2.45, 2.85), (1.90, 2.85)], closed=True)]
    assert SY.rug_outline(SY.Cluster(SY._segments(bed, set()))) is None
    pieces, cands, _ = _furn(bed)
    assert [c["fits"] for c in cands] == [["bed_double"]] and not any(p.type == "table_dining" for p in pieces)
    l_sofa = [_poly("s/0", [(1.0, 1.0), (3.5, 1.0), (3.5, 1.9), (1.9, 1.9), (1.9, 3.0), (1.0, 3.0)], closed=True),
              _poly("s/1", [(1.0, 1.0), (2.0, 1.0), (2.0, 1.9), (1.0, 1.9)], closed=True),
              _poly("s/2", [(2.0, 1.0), (2.75, 1.0), (2.75, 1.6), (2.0, 1.6)], closed=True),
              _poly("s/3", [(2.75, 1.0), (3.5, 1.0), (3.5, 1.6), (2.75, 1.6)], closed=True)]
    assert SY.rug_outline(SY.Cluster(SY._segments(l_sofa, set()))) is None
    one = SY.Cluster(SY._segments(_rug_set(chairs=1), set()))
    assert SY.rug_outline(one) is not None                       # the outline is a rug ...
    pieces, cands, _ = _furn(_rug_set(chairs=1))                 # ... but one chair is no group: asked as before
    assert len(cands) == 1 and not any(p.details.get("not_furniture") for p in pieces)
    from test_m11_split import _table_with_chairs
    plain = SY.split_table_chairs(SY.Cluster(SY._segments(_table_with_chairs(), set())), TABLE, 0.0)
    assert plain is not None and "rug" not in plain and "table_shape" not in plain and len(plain["chairs"]) == 6


def test_a_named_table_block_on_a_rug_gives_the_rug_mark_too():
    """A table-named block (``_split_named``) whose box the rug makes too large for a table: the named table, its
    chairs and the rug mark (before this round the rug's strokes rode along with the table)."""
    pieces, cands, _ = _furn(_rug_set(block="masa_yuvarlak", prefix="INSERT:M1"))
    assert cands == []
    assert sorted(p.type for p in pieces) == ["chair", "chair", "table_dining", "unknown"]
    assert next(p for p in pieces if p.type == "table_dining").type_method == "block_name"
    rug = next(p for p in pieces if p.type == "unknown")
    assert rug.details["not_furniture"]["as"] == "rug" and rug.entity == "INSERT:M1/0"


def test_an_ai_typed_rug_set_is_reported_with_its_chairs_and_its_rug():
    """``core.split_override_text`` counts the chairs from the split (a rug split also makes the rug mark: BASE said
    "3 chairs" for table + 2 chairs + rug) and says the outline is a rug mark."""
    split = SY.split_table_chairs(SY.Cluster(SY._segments(_rug_set(), set())), TABLE, 0.0)
    made = SY.table_chair_items(split, SY._Ctx("t.dxf", None, None, 0.0, "L1"), False, TABLE)
    assert [m.type for m in made] == ["table_dining", "chair", "chair", "unknown"]
    reason, note = CORE.split_override_text(split, "sym_L1_003", "bed_double", len(made))
    assert "rug outline" in reason and "a table with 2 chairs on a rug outline" in note and "rug mark" in note
