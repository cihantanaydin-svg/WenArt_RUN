"""Reading fixes of 26 Oct 2026 (user: "fix should be general, it is not a fix for real06, it must be a fix for the
project"): real06 is the test case, every rule below holds for any project.

What is pinned, each on a synthetic drawing or building that reproduces the real06 case (the DWG strokes were not
available in this session: no LibreDWG; the numbers are those of results/baseline/latest/furniture/real06):

1. An armchair drawn as its seat cushion with the arms and the back is one seat, not a "table with two chairs"
   (``symbols.seat_part`` / ``split_table_chairs``; real06 f_L0_017/020/023, f_L1_021, 0.77 x 0.62 m "tables"); a
   dining table with its chairs is still split. One block drawn again elsewhere gets one type
   (``infer._same_block_type``). A round piece ringed by three seats facing it is their table, not a lamp
   (``infer.ringed_tables``; f_L0_028).
2. Nested outlines of one piece are one piece; the strongest evidence stays (``reading.nested_outlines``; f_L1_003,
   f_L1_018, f_L1_019).
3. A straight counter-like run with no sink, hob or fridge is no kitchen counter (``symbols.counter_run_evidence``).
4. Two AI answers of one run group (kitchen_counter / sink_kitchen) make the run holding the named member, its depth
   the product depth (``reading.tie_break``, f_L0_027); a kitchen outline holding sink and hob circles is the kitchen
   run (``reading.kitchen_outlines``, ``symbols.kitchen_signs``; f_L0_002).
5. A wall type typed by code needs its back on a wall (``infer.placeable``; f_L1_020, f_L0_016); a round piece is never
   a chair (f_L1_026).
6. A room named only "Oda" takes the type its agreed drawn anchors name when no bed is drawn
   (``reading.generic_rooms``; r_L1_oda_2).
"""
import copy
import math
from types import SimpleNamespace

import pytest
from shapely.geometry import box as sbox

import _m11_room as M
import _real01_page as R
from wenart import building as B
from wenart.furniture import infer as INF
from wenart.ingest.generic import reading as RD
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.pipeline import ProjectBuild

TABLE = SY.load_size_table()[0]


def _poly(sid, pts, closed=True, block=None):
    return Stroke(id=sid, kind="polyline", pts=[tuple(map(float, p)) for p in pts], closed=closed, block=block)


def _rect(sid, x0, y0, x1, y1, block=None):
    return _poly(sid, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], block=block)


def _line(sid, a, b, block=None):
    return Stroke(id=sid, kind="line", pts=[tuple(map(float, a)), tuple(map(float, b))], block=block)


def _circle(sid, c, r, block=None):
    pts = [(c[0] + r * math.cos(2 * math.pi * k / 24), c[1] + r * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    return Stroke(id=sid, kind="circle", pts=pts, closed=True, block=block,
                  arc={"center": [c[0], c[1]], "radius": r, "start_deg": 0.0, "end_deg": 360.0})


def _room(x0=0.0, y0=0.0, x1=6.0, y1=5.0, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _furn(strokes, walls=None, faces=(), notes=None):
    walls = walls or _room()
    outline = TP.building_outline(walls, [])
    return SY.furniture(strokes, set(), walls, [], [], [], outline, list(faces), level_id="L0", file_rel="t.dxf",
                        page_no=None, size_table=TABLE, notes=notes)


def _rot(strokes, deg, about=(0.0, 0.0)):
    """The strokes turned by ``deg`` about ``about`` (real06 draws its armchair blocks at 29.5 deg)."""
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)

    def f(p):
        x, y = p[0] - about[0], p[1] - about[1]
        return (about[0] + c * x - s * y, about[1] + s * x + c * y)
    out = []
    for st in strokes:
        arc = None
        if st.arc:
            arc = dict(st.arc, center=list(f(st.arc["center"])))
        out.append(Stroke(id=st.id, kind=st.kind, pts=[f(p) for p in st.pts], closed=st.closed, block=st.block,
                          arc=arc))
    return out


def _armchair(x=2.0, y=2.0, prefix="A", back=0.12, gap=0.01):
    """real06's armchair block: a 0.77 x 0.62 m seat cushion (its own closed outline), a back strip along its back
    (``back`` deep) and two 0.08 m arms along its sides, ``gap`` off the cushion (so they are no part of its outline)
    and 3 cm short of the next part: the M11 split found a 'table' (the cushion) with 'chairs' (the arms and back),
    each 'chair' grown to 0.45 m cutting the 'table' by about 0.32 m."""
    w, d, arm = 0.77, 0.62, 0.08
    x0, x1, y0, y1 = x - w / 2, x + w / 2, y - d / 2, y + d / 2
    return [_rect(f"{prefix}:cushion", x0, y0, x1, y1),
            _rect(f"{prefix}:back", x0, y1 + gap, x1, y1 + gap + back),
            _rect(f"{prefix}:arm_l", x0 - gap - arm, y0, x0 - gap, y1 - 0.03),
            _rect(f"{prefix}:arm_r", x1 + gap, y0, x1 + gap + arm, y1 - 0.03)]


def _build(furniture, **kw):
    return ProjectBuild(M.building(furniture=furniture, **kw))


def _works(**details):
    items = [SimpleNamespace(element_id=pid, details=dict(det)) for pid, det in details.items()]
    ex = SimpleNamespace(furniture=items, report={}, level_id="L0")
    return {"page": SimpleNamespace(extraction=ex)}


def _piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def _answers(*types):
    return [{"type": t, "model": f"m{k}", "model_key": f"m{k}", "pass": k + 1, "confidence": 0.9, "front": "none",
             "reason": "test"} for k, t in enumerate(types)]


# --------------------------------------------------------------------------
# 1. One seat, not a table with chairs; one block, one type; a ringed table
# --------------------------------------------------------------------------

@pytest.mark.parametrize("turn", [0.0, 29.458])
def test_an_armchair_drawn_as_cushion_arms_and_back_is_one_seat(turn):
    """real06: the 0.77 x 0.62 m cushion fits a table (with the tolerance) and the back and arms touched it: the M11
    split made a dining table and two chairs of it, each 'chair' cutting the 'table' by 0.32-0.39 m. The parts hug the
    cushion and reach less than 0.25 m from it: one armchair, its front the free side (the -Y side before the turn)."""
    strokes = _rot(_armchair(), turn, (2.0, 2.0))
    part = SY.Cluster(SY._segments(strokes, set()))
    split = SY.split_table_chairs(part, TABLE, 0.0)
    assert split is not None and split.get("seat") and split["chairs"] == []
    seat = split["seat"]
    assert seat["type"] == "armchair" and seat["record"]["parts"] == 3
    assert seat["front"] == pytest.approx((270.0 + turn) % 360.0, abs=0.5)
    made = SY.table_chair_items(split, SY._Ctx("t.dxf", None, None, 0.0, "L0"), False, TABLE)
    assert len(made) == 1 and made[0].type == "armchair" and made[0].type_method == "rule"
    assert made[0].status == "verified" and SY.SEAT_NOTE in made[0].evidence["note"]
    assert sorted(made[0].size) == pytest.approx([0.62 + 0.13, 0.77 + 0.18], abs=0.02)
    assert made[0].front_deg == pytest.approx((270.0 + turn) % 360.0, abs=0.5)
    assert {sid.split(":")[1] for sid in SY.expand_ids(made[0].evidence["entity"])} >= {"cushion", "back", "arm_l",
                                                                                        "arm_r"}


def test_real06_f_L0_004_is_one_armchair_without_a_guessed_front():
    """The building's numbers of f_L0_004 (the 0.62 x 0.77 m 'table') and its 'chairs' f_L0_005 / f_L0_006 (grown to
    0.45 m, each cutting the 'table' by 0.30 m): two 0.14-0.15 m strips along its west and south sides. One armchair
    of 0.77 x 0.92 m (as f_L0_026, the same block typed by the AI); two free sides at a corner and two strips of one
    length: no front is guessed (the reading turns it to its coffee table)."""
    strokes = [_rect("L:t", 4.815, 2.676, 5.435, 3.449), _rect("L:w", 4.663, 2.71, 4.805, 3.242),
               _rect("L:s", 4.869, 2.533, 5.405, 2.666)]
    split = SY.split_table_chairs(SY.Cluster(SY._segments(strokes, set())), TABLE, 0.0)
    assert split is not None and split["seat"]["type"] == "armchair" and split["seat"]["front"] is None
    assert sorted(split["seat"]["fp"][1:3]) == pytest.approx([0.772, 0.916], abs=0.01)


def test_a_seat_part_hugs_the_outline_a_chair_does_not():
    cushion = sbox(0.0, 0.0, 0.77, 0.62)
    arm = SY.Cluster(SY._segments([_rect("a", 0.77, 0.0, 0.845, 0.59)], set()))
    assert "an arm or a back" in SY.seat_part(arm, cushion, 0.0)
    # A dining chair drawn open towards its table touches it at two line ends: 6 cm along it, no seat part.
    chair = SY.Cluster(SY._segments([_line("c1", (0.1, 0.0), (0.1, -0.3)), _line("c2", (0.1, -0.3), (0.55, -0.3)),
                                     _line("c3", (0.55, -0.3), (0.55, 0.0))], set()))
    assert SY.seat_part(chair, cushion, 0.0) is None
    # A closed chair abutting the table edge runs along it but stands 0.45 m deep: a chair.
    deep = SY.Cluster(SY._segments([_rect("d", 0.15, -0.45, 0.6, 0.0)], set()))
    assert SY.seat_part(deep, cushion, 0.0) is None


def test_a_small_table_with_two_closed_chairs_abutting_is_still_a_table_with_chairs():
    """The whole (0.8 x 1.7 m) is sofa-sized, but the chairs are 0.45 m deep: they are chairs (as before)."""
    strokes = [_rect("t", 1.0, 1.0, 1.8, 1.8), _rect("c1", 1.175, 0.55, 1.625, 1.0), _rect("c2", 1.175, 1.8, 1.625, 2.25)]
    split = SY.split_table_chairs(SY.Cluster(SY._segments(strokes, set())), TABLE, 0.0)
    assert split is not None and not split.get("seat") and len(split["chairs"]) == 2


def test_a_table_with_tucked_chairs_drawn_as_closed_boxes_is_still_a_table_with_chairs():
    """1.6 x 0.8 m table, four chairs tucked in, each drawn as a closed 0.45 x 0.20 m box against a long side: the
    whole (1.6 x 1.2 m) is sofa-sized and the boxes are shallow, but each covers 28 % of its side: chairs."""
    strokes = [_rect("t", 1.0, 1.0, 2.6, 1.8)]
    for k, x in enumerate((1.15, 1.95)):
        strokes += [_rect(f"s{k}", x, 0.8, x + 0.45, 1.0), _rect(f"n{k}", x, 1.8, x + 0.45, 2.0)]
    split = SY.split_table_chairs(SY.Cluster(SY._segments(strokes, set())), TABLE, 0.0)
    assert split is not None and not split.get("seat") and len(split["chairs"]) == 4


def test_a_seat_sized_group_with_one_hugging_part_is_no_table_with_chairs():
    """One part hugs the outline (an arm), the other stands off it: ambiguous, so no split (it stays one piece)."""
    w = _armchair()
    strokes = [w[0], w[2], _rect("A:free", 2.47, 1.69, 2.62, 2.0)]        # cushion, left arm, a block 8 cm off
    assert SY.split_table_chairs(SY.Cluster(SY._segments(strokes, set())), TABLE, 0.0) is None


def test_the_dining_sets_of_milestone_11_still_split():
    import test_m11_split as T

    split = SY.split_table_chairs(SY.Cluster(SY._segments(T._table_with_chairs(), set())), TABLE, 0.0)
    assert split is not None and len(split["chairs"]) == 6 and not split.get("seat")


def test_an_armchair_re_read_is_one_armchair():
    """The path real06's armchairs took: an AI candidate left unknown by its answers is re-read (``core``'s
    ``_reread_unknowns`` -> ``symbols.reread``), whose loose part went through the table + chairs split; now one
    armchair rule piece. On the page the armchair is an AI candidate (it fits a type), as before."""
    walls = _room()
    pieces, cands, _ = _furn(_rot(_armchair(), 29.458, (2.0, 2.0)), walls=walls)
    assert not pieces and len(cands) == 1 and "armchair" in cands[0]["fits"]
    notes = []
    ctx = SY._Ctx("t.dxf", None, None, 0.0, "L0")
    part = SY.Cluster(SY._segments(_rot(_armchair(), 29.458, (2.0, 2.0)), set()))
    got = SY.reread(part, ctx, TABLE, walls, [], [TP.wall_polygon(w) for w in walls], [], notes,
                    why="AI candidate still unknown after its answers")
    assert [it.type for it in got["items"]] == ["armchair"] and got["items"][0].type_method == "rule"
    assert got["items"][0].front_deg == pytest.approx(299.458, abs=0.5)


def _drawn(pid, ftype, centre, size, rot=0.0, entity=None, level="L0", room=M.ROOM_ID, **kw):
    f = M.fp(pid, ftype, centre, size, rotation=rot, front=None, **kw)
    f.update(level_id=level, room_id=room)
    if entity is not None:
        f["evidence"][0]["entity"] = entity
    return f


def test_one_block_drawn_again_elsewhere_gets_one_type():
    """real06's armchair block (0.92 x 0.77 m) is drawn in the salon (typed armchair) and again in the bedroom upstairs
    (untyped): the same footprint within 1 cm and the same strokes per kind anywhere in the project: one type."""
    strokes = "LINE:2A01,LINE:2A02,LINE:2A03,LINE:2A04,ARC:2A05,ARC:2A06"
    typed = _drawn("f_L0_026", "armchair", (2.0, 2.0), (0.917, 0.769), rot=330.59, entity=strokes,
                   type_method="ai_two_pass")
    other = _drawn("f_L1_020", "unknown", (3.0, 1.2), (0.917, 0.770), rot=60.497,
                   entity="LINE:3B01,LINE:3B02,LINE:3B03,LINE:3B04,ARC:3B05,ARC:3B06", level="L1",
                   status="unverified", type_method="none")
    b = M.building(furniture=[typed, other])
    found = INF.type_by_code(b, other)
    assert found is not None and found["type"] == "armchair" and found["method"] == INF.SAME_BLOCK_METHOD
    assert "f_L0_026" in found["reason"] and found["evidence"]["source_id"] == "f_L0_026"
    out, props = INF.apply_code_types(b)
    piece = _piece(out, "f_L1_020")
    assert piece["type"] == "armchair" and piece["type_method"] == "same_block" and piece["inferred"]
    # Other strokes (two more lines than the four), or two copies of other types: no type.
    other2 = dict(other, evidence=[dict(other["evidence"][0], entity="LINE:3B01,LINE:3B02,LINE:3B03,LINE:3B04,"
                                                                     "LINE:3B08,LINE:3B09,ARC:3B05,ARC:3B06")])
    assert INF._same_block_type(M.building(furniture=[typed, other2]), other2) is None
    # A few strokes more in a large block (real06's armchair copies: 301 and 306 lines) is the same block.
    assert INF.same_block(((), (("LINE", 301),), None), ((), (("LINE", 306),), None))
    assert not INF.same_block(((), (("LINE", 301),), None), ((), (("LINE", 320),), None))
    assert not INF.same_block(((), (("LINE", 301),), None), ((), (("LINE", 301),), "round"))
    sofa = _drawn("x", "sofa", (4.0, 3.0), (0.917, 0.769), entity=strokes, type_method="ai_two_pass")
    assert INF._same_block_type(M.building(furniture=[typed, sofa, other]), other) is None
    # A plain box (fewer than 4 strokes) says nothing.
    assert INF.block_signature(_drawn("p", "unknown", (1, 1), (0.5, 0.5), entity="LINE:1,LINE:2")) is None


def test_entity_counts_read_ranges_and_handles():
    assert INF.entity_counts("LINE:295C60,LINE:295C61,ARC:298801-298804,CIRCLE:29877F") == {"LINE": 2, "ARC": 4,
                                                                                         "CIRCLE": 1}
    assert INF.entity_counts("recognition:sym_L0_001") == {}


def _seat(pid, centre, front):
    rot = (front + 90.0) % 360.0
    return M.fp(pid, "armchair", centre, (0.92, 0.77), rotation=rot, front=front, type_method="rule")


def test_a_round_lamp_ringed_by_seats_is_their_coffee_table():
    """real06's salon: four armchairs at 1.0 m around a round 0.66 m symbol both passes called a floor lamp."""
    c = (2.5, 2.0)
    lamp = M.fp("f_L0_028", "floor_lamp", c, (0.66, 0.66), front=None, type_method="ai_two_pass", shape="round",
                circle_fit={"share": 1.0, "radius": 0.33},
                evidence=[{"file": "p.dxf", "method": "vector", "confidence": 0.9, "entity": "CIRCLE:1"},
                          {"file": "p.dxf", "method": "ai", "confidence": 0.9, "entity": "recognition:sym_L0_015"}])
    seats = []
    for k, bearing in enumerate((304.0, 53.0, 121.0, 242.0)):
        t = math.radians(bearing)
        sc = (c[0] + 0.95 * math.cos(t), c[1] + 0.95 * math.sin(t))
        seats.append(_seat(f"s{k}", sc, round((bearing + 180.0) % 360.0)))
    b = M.building(w=5.0, h=4.0, room_type="living", furniture=[lamp] + seats)
    props = INF.ringed_tables(b)
    assert [(p["piece_id"], p["type"]) for p in props] == [("f_L0_028", "table_coffee")]
    assert "4 seats around it" in props[0]["reason"] and props[0]["crop"].endswith("sym_L0_015_ctx.png")
    out = INF.apply_inferences(b, props)
    t = _piece(out, "f_L0_028")
    assert t["type"] == "table_coffee" and t["drawn_type"] == "floor_lamp" and t["type_method"] == "inferred"
    assert t["adjusted_by_ai"]["by"] == "code" and t["adjusted_by_ai"]["rule"] == INF.RING_TABLE_METHOD
    # Two seats only, or three on one side of it: a lamp beside seats stays a lamp.
    assert INF.ringed_tables(M.building(room_type="living", furniture=[lamp] + seats[:2])) == []
    side = [_seat(f"t{k}", (c[0] + dx, c[1] - 0.9), 90.0) for k, dx in enumerate((-0.95, 0.0, 0.95))]
    assert INF.ringed_tables(M.building(room_type="living", furniture=[lamp] + side)) == []


# --------------------------------------------------------------------------
# 2. Nested outlines of one piece
# --------------------------------------------------------------------------

def _oda2():
    """real06 r_L1_oda_2's wardrobe: three outlines with one centre (f_L1_018 two passes, f_L1_003 the counter rule,
    f_L1_019 the passes disagreed), at the east wall of a 3.35 x 3.95 m room."""
    w18 = M.fp("f_L1_018", "wardrobe", (3.01, 1.95), (1.805, 0.676), rotation=270.0, front=180.0,
               type_method="ai_two_pass", type_candidates=_answers("wardrobe", "wardrobe"))
    c03 = M.fp("f_L1_003", "kitchen_counter", (3.059, 1.95), (1.76, 0.482), rotation=270.0, front=180.0,
               type_method="rule", status="unverified")
    u19 = M.fp("f_L1_019", "unknown", (3.05, 1.935), (1.558, 0.362), rotation=270.0, front=None,
               type_method="none", status="unverified", type_candidates=_answers("dresser", "bookshelf"))
    return [w18, c03, u19]


def test_nested_outlines_of_one_wardrobe_are_one_piece():
    build = _build(_oda2(), w=3.35, h=3.95, room_type="bedroom", window=None)
    merged = RD.nested_outlines(build, {})
    b = build.building
    assert merged == ["f_L1_003", "f_L1_019"]
    keep = _piece(b, "f_L1_018")
    assert keep.get("build") is not False and keep["merged_outlines"] == ["f_L1_003", "f_L1_019"]
    for pid in merged:
        f = _piece(b, pid)
        assert f["build"] is False and f["inferred_as"] == "detail" and f["merged_into"] == "f_L1_018"
        assert f["adjusted_by_ai"]["by"] == "code" and f["adjusted_by_ai"]["rule"] == RD.NEST_RULE
        assert f["adjusted_by_ai"]["not_furniture"] == "nested_outline" and f["drawn_footprint"] == f["footprint"]
        assert "stronger evidence" in f["inferred_reason"]
    # A piece whose question still waits: nothing is merged yet (its answers decide its strength).
    build2 = _build(_oda2(), w=3.35, h=3.95, room_type="bedroom", window=None)
    assert RD.nested_outlines(build2, {}, pending={"f_L1_019"}) == []


def test_a_sink_in_its_counter_and_a_table_on_its_rug_are_not_nested_outlines():
    counter = M.fp("k", "kitchen_counter", (1.5, 3.7), (0.9, 0.6), type_method="rule")
    sink = M.fp("s", "sink_kitchen", (1.5, 3.72), (0.8, 0.5), type_method="block_name")
    rug = M.fp("r", "unknown", (2.5, 2.0), (2.0, 1.4), type_method="none", front=None)
    table = M.fp("t", "table_coffee", (2.5, 2.0), (1.1, 0.6), type_method="ai_two_pass", front=None)
    build = _build([counter, sink, rug, table], room_type="kitchen", window=None)
    assert RD.nested_outlines(build, {}) == []
    # A rug drawn 0.2 m round a dining table holds the chairs too: a group outline, not a nested outline of the table.
    rug2 = M.fp("r2", "unknown", (2.5, 2.0), (2.0, 1.3), type_method="none", front=None)
    dining = M.fp("d", "table_dining", (2.5, 2.0), (1.6, 0.9), type_method="ai_two_pass", front=None)
    chairs = [M.fp(f"c{k}", "chair", (x, y), (0.45, 0.45), type_method="rule") for k, (x, y) in
              enumerate(((2.1, 1.4), (2.9, 1.4), (2.1, 2.6), (2.9, 2.6)))]
    build2 = _build([rug2, dining] + chairs, room_type="living", window=None)
    assert RD.nested_outlines(build2, {}) == []
    # Without its chairs the rug 0.2 m round the table is the table's outer outline: one piece.
    build3 = _build([copy.deepcopy(rug2), copy.deepcopy(dining)], room_type="living", window=None)
    assert RD.nested_outlines(build3, {}) == ["r2"]


def test_the_reading_merges_nested_outlines_before_the_code_typing():
    build = _build(_oda2(), w=3.35, h=3.95, room_type="bedroom", window=None)
    RD.read_furniture(build, {})
    b = build.building
    assert build.reading["nested_outlines"] == ["f_L1_003", "f_L1_019"]
    assert _piece(b, "f_L1_019")["type"] == "unknown" and _piece(b, "f_L1_019")["build"] is False
    assert not [r for r in b["needs_review"] if r["id"] in ("f_L1_003", "f_L1_019")]


# --------------------------------------------------------------------------
# 3. A counter needs a sink, hob or fridge, or an L / U run
# --------------------------------------------------------------------------

def _straight_run():
    """A 2.5 m run along the north wall of a 4 x 4 m room: end cap, front line 0.6 m off the wall, end cap."""
    return [_line("s0", (0.8, 3.9), (0.8, 3.3)), _line("s1", (0.8, 3.3), (3.3, 3.3)), _line("s2", (3.3, 3.3), (3.3, 3.9))]


def test_a_straight_run_without_sink_hob_or_fridge_is_no_kitchen_counter():
    """real06 r_L1_oda_2: f_L1_003 / f_L1_004 were kitchen counters by the chain rule alone (no sink, hob or fridge in
    the room): a wardrobe, a shelf or a sideboard by size and room."""
    walls = _room(0, 0, 4, 4)
    notes = []
    pieces, cands, _ = _furn(_straight_run(), walls=walls, notes=notes)
    assert not [p for p in pieces if p.type == "kitchen_counter"]
    assert any("no sink, hob or fridge drawn: no kitchen counter" in n for n in notes)
    assert cands and "wardrobe" in cands[0]["fits"]                      # asked like any other drawn piece


def test_a_straight_run_with_a_sink_drain_or_a_kitchen_block_is_a_counter():
    walls = _room(0, 0, 4, 4)
    drain = [_circle("CIRCLE:d1", (2.0, 3.6), 0.03)]
    pieces, _, _ = _furn(_straight_run() + drain, walls=walls)
    counters = [p for p in pieces if p.type == "kitchen_counter"]
    assert len(counters) == 1 and "kitchen fixture drawn on the run (sink: 1 circles)" in counters[0].evidence["note"]
    hob = [_rect("INSERT:H1/0", 1.6, 3.35, 2.2, 3.85, block="ocak_")]
    pieces, _, _ = _furn(_straight_run() + hob, walls=walls)
    assert [p.type for p in pieces if p.type == "kitchen_counter"] == ["kitchen_counter"]


def test_counter_run_evidence_wants_legs_that_meet_at_a_corner():
    north = {"rect_f": (0.8, 3.3, 3.9, 3.9), "front_f": (0.0, -1.0)}
    east = {"rect_f": (3.3, 2.0, 3.9, 3.3), "front_f": (-1.0, 0.0)}
    far_west = {"rect_f": (0.1, 0.2, 0.7, 1.4), "front_f": (1.0, 0.0)}
    assert "meet at a corner" in SY.counter_run_evidence([north, east], [], 0.0)
    assert SY.counter_run_evidence([north, far_west], [], 0.0) is None        # two legs 2 m apart: no L
    assert SY.counter_run_evidence([north], [], 0.0) is None


def test_kitchen_signs_count_drains_and_burners():
    segs = SY._segments([_circle("d", (1.0, 1.0), 0.03)] + [_circle(f"b{k}", (2.0 + 0.25 * k, 1.0), 0.09)
                                                            for k in range(4)], set())
    assert SY.kitchen_signs(segs) == {"sink": 1, "hob": 4}
    assert SY.kitchen_signs(segs, sbox(1.8, 0.8, 3.0, 1.2)) == {"hob": 4}
    assert SY.kitchen_signs(segs[1:3]) == {}                             # two burners are no hob


# --------------------------------------------------------------------------
# 4. Two answers of one run group; a kitchen run drawn as one outline
# --------------------------------------------------------------------------

def test_two_answers_of_the_kitchen_run_make_a_counter_holding_the_sink():
    """real06 f_L0_027: a 1.20 x 0.45 m strip at the kitchen's west wall, Qwen kitchen_counter, GLM sink_kitchen; both
    fixed types the room does not miss, so the tie-break left it unknown (and the agent unbuilt it)."""
    strip = M.fp("f_L0_027", "unknown", (0.225, 1.2), (1.2, 0.45), rotation=90.0, status="unverified",
                 type_method="none", type_candidates=_answers("kitchen_counter", "sink_kitchen"))
    build = _build([strip], w=3.0, h=2.4, room_type="kitchen", window=None)
    assert RD.tie_break(build, {}) == ["f_L0_027"]
    f = _piece(build.building, "f_L0_027")
    assert f["type"] == "kitchen_counter" and f["holds"] == ["sink_kitchen"] and f["inferred"]
    assert f["footprint"]["size"] == pytest.approx([1.2, 0.6])
    assert f["footprint"]["center"] == pytest.approx([0.3, 1.2])          # the back stays on the west wall
    assert f["drawn_footprint"]["size"] == [1.2, 0.45] and f["adjusted_by_ai"]["rule"] == RD.RUN_DEPTH_RULE
    assert f["module_hints"]["sink_pos_m"] == pytest.approx([0.3, 1.2])
    assert "kitchen_run group" in f["inferred_reason"] or "holds" in f["inferred_reason"]


def test_two_answers_of_a_bath_set_are_not_one_piece_holding_another():
    piece = M.fp("p", "unknown", (1.0, 0.3), (0.8, 0.45), status="unverified", type_method="none",
                 type_candidates=_answers("washbasin", "toilet"))
    assert RD._one_group(["washbasin", "toilet"], {"room_type": "bathroom"}) is None
    assert RD._one_group(["kitchen_counter", "sink_kitchen"], {"room_type": "kitchen"}) == \
        ("kitchen_counter", "sink_kitchen", "kitchen_run")
    assert piece["type"] == "unknown"


def test_a_kitchen_outline_holding_sink_and_hob_is_the_kitchen_run():
    """real06 f_L0_002: one 3.99 x 2.40 m outline (LINEs) with its sink and hob circles, wall to wall across the
    kitchen: 'fits no size-table type', not built. Its two wall sides become counter legs 0.60 m deep."""
    box = M.fp("f_L0_002", "unknown", (1.5, 2.0), (3.99, 2.4), rotation=90.0, front=None, status="unverified",
               type_method="none")
    build = _build([box], w=3.4, h=4.0, room_type="kitchen", window=None)
    items = {"f_L0_002": SimpleNamespace(element_id="f_L0_002", details={"kitchen_signs": {"sink": 1, "hob": 4}})}
    legs = RD.kitchen_outlines(build, items)
    b = build.building
    assert len(legs) == 2
    for lid in legs:
        leg = _piece(b, lid)
        assert leg["type"] == "kitchen_counter" and leg["source"] == "from_documents" and leg["inferred"]
        assert leg["drawn_footprint"] == box["footprint"] and leg["adjusted_by_ai"]["rule"] == RD.KITCHEN_OUTLINE_RULE
        assert leg["footprint"]["size"][1] == pytest.approx(0.6)
    fronts = sorted(_piece(b, lid)["front_deg"] for lid in legs)
    assert fronts == [90.0, 270.0]                                      # the south and north legs face the room
    outline = _piece(b, "f_L0_002")
    assert outline["build"] is False and outline["inferred_as"] == "detail" and outline["replaced_by"] == legs
    # Without the sink or hob circles nothing happens (left for review).
    build2 = _build([copy.deepcopy(box)], w=3.4, h=4.0, room_type="kitchen", window=None)
    assert RD.kitchen_outlines(build2, {}) == []
    # Against three walls it is a U: three legs, the corners to the longer legs.
    box3 = M.fp("u", "unknown", (1.2, 2.0), (3.99, 2.4), rotation=90.0, front=None, status="unverified",
                type_method="none")
    build3 = _build([box3], w=3.4, h=4.0, room_type="kitchen", window=None)
    items3 = {"u": SimpleNamespace(element_id="u", details={"kitchen_signs": {"sink": 1}})}
    legs3 = RD.kitchen_outlines(build3, items3)
    sizes3 = sorted(tuple(round(v, 2) for v in _piece(build3.building, lid)["footprint"]["size"]) for lid in legs3)
    assert sizes3 == [(1.8, 0.6), (1.8, 0.6), (3.99, 0.6)]              # the 3.99 m leg along the west wall


# --------------------------------------------------------------------------
# 5. A wall type needs its back on a wall; a round piece is never a chair
# --------------------------------------------------------------------------

def test_code_never_types_a_diagonal_piece_as_a_wall_type():
    """real06 f_L1_020: a 0.92 x 0.77 m armchair drawn at 60.5 deg in the master bedroom was 'the bedroom's missing
    wardrobe'. Turned square to the east wall it would be one."""
    bed = M.fp("bed", "bed_double", (1.5, 2.0), (1.6, 2.0), rotation=90.0, front=0.0, type_method="block_name")
    diag = M.fp("x", "unknown", (4.0, 1.0), (0.917, 0.77), rotation=60.497, front=None, status="unverified",
                type_method="none")
    b = M.building(w=5.0, h=4.0, room_type="bedroom", furniture=[bed, diag])
    assert INF.placeable("wardrobe", diag, b["rooms"][0]) is not None
    found = INF.type_by_code(b, diag)
    assert found is None or found["type"] != "wardrobe"
    square = M.fp("x", "unknown", (4.615, 2.5), (0.917, 0.77), rotation=90.0, front=None, status="unverified",
                  type_method="none")
    assert INF.placeable("wardrobe", square, b["rooms"][0]) is None


def test_the_tie_break_never_puts_a_wall_type_in_the_middle_of_the_room():
    """real06 f_L0_016: 0.87 x 0.52 m at 135 deg, Qwen table_coffee, GLM bookshelf; 'the room misses' a bookshelf, so
    a lone bookshelf stood diagonal in the salon. Its back cannot stand on a wall: the coffee table."""
    sofa = M.fp("sofa", "sofa", (2.5, 0.5), (2.2, 0.9), front=90.0, type_method="ai_two_pass")
    piece = M.fp("f_L0_016", "unknown", (2.5, 1.9), (0.865, 0.517), rotation=135.0, front=None, status="unverified",
                 type_method="none", type_candidates=_answers("table_coffee", "bookshelf"))
    build = _build([sofa, piece], w=5.0, h=4.0, room_type="living", window=None)
    assert RD.tie_break(build, {}) == ["f_L0_016"]
    f = _piece(build.building, "f_L0_016")
    assert f["type"] == "table_coffee" and "needs its back on a wall" in f["inferred_reason"]


def test_a_round_piece_by_a_dining_table_is_never_a_chair():
    """real06 f_L1_026: a round 0.58 m table beside the 'dining table' (an armchair) became a chair."""
    table = M.fp("t", "table_dining", (2.5, 2.0), (1.2, 0.8), front=None, type_method="block_name")
    roundp = M.fp("r", "unknown", (2.5, 2.7), (0.58, 0.58), front=None, status="unverified", type_method="none",
                  shape="round")
    square = M.fp("q", "unknown", (2.5, 1.3), (0.45, 0.45), front=None, status="unverified", type_method="none")
    build = _build([table, roundp, square], room_type="living", window=None)
    RD.context_types(build, {})
    assert _piece(build.building, "r")["type"] != "chair" and _piece(build.building, "q")["type"] == "chair"
    assert INF.placeable("chair", roundp, None) == "a round piece is never a chair"


# --------------------------------------------------------------------------
# 6. A room named only by a generic word
# --------------------------------------------------------------------------

def test_a_room_named_only_oda_takes_the_type_of_its_agreed_anchors():
    """real06 r_L1_oda_2 'ODA' (read as a bedroom) holds a sofa both passes agreed on and no bed: a living room."""
    sofa = M.fp("sofa", "sofa", (0.9, 2.0), (2.65, 0.925), rotation=270.0, front=0.0, type_method="ai_two_pass")
    build = _build([sofa], w=3.35, h=3.95, room_type="bedroom", window=None)
    build.building["rooms"][0].update(label="Oda", label_raw="ODA")
    assert RD.generic_rooms(build) == [M.ROOM_ID]
    room = build.building["rooms"][0]
    assert room["room_type"] == "living" and room["corrected_by_ai"]["before"] == {"room_type": "bedroom"}
    assert room["corrected_by_ai"]["evidence"]["pieces"] == ["sofa"] and "generic word" in room["corrected_by_ai"]["reason"]
    assert room["evidence"][-1]["rule"] == RD.GENERIC_ROOM_RULE


@pytest.mark.parametrize("extra,label,want", [
    ("bed", "ODA", "bedroom"),                 # a bed is drawn: the bedroom stands
    ("single", "Yatak Odası", "bedroom"),      # no generic name: never changed
    ("counter", "ODA", "bedroom"),             # a counter alone does not make a kitchen
    ("sink", "ODA", "kitchen"),                # a counter with a drawn sink does
])
def test_a_generic_room_keeps_its_type_unless_its_anchors_say_otherwise(extra, label, want):
    pieces = {"bed": [M.fp("b", "bed_double", (1.5, 2.0), (1.6, 2.0), type_method="block_name"),
                      M.fp("s", "sofa", (1.5, 3.5), (2.0, 0.9), type_method="ai_two_pass")],
              "single": [M.fp("s", "sofa", (1.5, 3.5), (2.0, 0.9), type_method="ai_two_pass")],
              "counter": [M.fp("k", "kitchen_counter", (1.5, 3.65), (2.4, 0.6), type_method="block_name")],
              "sink": [M.fp("k", "kitchen_counter", (1.5, 3.65), (2.4, 0.6), type_method="block_name"),
                       M.fp("s", "sink_kitchen", (1.5, 3.65), (0.8, 0.5), type_method="block_name")]}[extra]
    build = _build(pieces, room_type="bedroom", window=None)
    build.building["rooms"][0].update(label=label, label_raw=label.upper())
    RD.generic_rooms(build)
    assert build.building["rooms"][0]["room_type"] == want


def test_generic_room_labels():
    assert all(B.generic_room_label(x) for x in ("ODA", "Oda 2", "ODA-01", "room 3"))
    assert not any(B.generic_room_label(x) for x in ("Yatak Odası", "Çalışma Odası", "SALON", "", None))
    assert B.room_type_for("ODA") == "bedroom"                           # the ingest's default stays
