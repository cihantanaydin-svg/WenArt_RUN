"""Fix round after P5 (22 Oct 2026; pod P5, real04), track F_reading: the reading and furniture fixes.

Every test here fails on BASE (commit 29e54d0) or names the mutation it guards:

- the group-member rule waits for an untyped L outline (the room's corner sofa to be) and gives a coffee table or a TV
  unit only at its role's place; the reading types the drawn L corner sofas before the code typing, so the 1.30 m
  outline in the L's open corner is its coffee table, never "the missing sofa", and a lamp symbol by the window is
  never the coffee table (P5 f_L-1_061/063);
- a seat drawn in a corner sofa's open corner that the AI or the group rule typed is retyped as its coffee table by
  code (user decision of 22 Oct 2026: ``adjusted_by_ai`` by code, ``drawn_type`` and the plan crop kept);
- a sofa or armchair block is never fronted by the bed-pillow rule; its back strip and arms give the front, else it
  faces its coffee table (P5: the oyun sofas faced away from their table);
- an AI front on the short side of a sofa is a reading error: the long side (P5: f_L-1b_045 built 0.82 m wide);
- a desk symbol that holds its chair is split (P5: four 1.45 x 0.91 m desks built 0.85 m deep with no chair);
- a seat cushion read as an ottoman on an armchair's seat is not built (P5 f_L-1_075..078);
- a coat closet drawn with a hanging rail and hangers is one wardrobe, never a table with two chairs (P5 f_L1_021);
- a bath or shower 1-5 cm longer than its bay is shrunk to the nearest real product that fits, at the reading and by
  ``fix_fixture`` (user decision of 22 Oct 2026; P4b real03: four tubs and four showers);
- the mark lock: when the AI passes typed the piece as furniture too, a type_disagreement conflict or an RC finding
  no longer lifts it (P5 seq 5021); an untyped piece is marked only with its plan crop (P5 seq 5388).

Fix round after P5 (22 Oct 2026), review (``test_review_*``, each fails before its fix): no bed-pillow front for an
AI-typed seat; no desk split for a real desk depth or a drawn chair; no short-side front for a long-front type from the
wall rules; no seat cushion in a box corner sofa's open corner; a second code correction keeps the first record; an
agreed ottoman stays; a bath shrunk without a question crop gets a plan crop drawn at the reading.
"""
from __future__ import annotations

import copy
from types import SimpleNamespace

import pytest

import _m11_room as M
from wenart.furniture import edit_ops as E
from wenart.furniture import infer as INF
from wenart.ingest.generic import reading as RD
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic.model import Stroke
from wenart.ingest.pipeline import ProjectBuild

TABLE = SY.FALLBACK_SIZE_TABLE
L_NOTE = ("L outline 3.00 x 1.80 m: main seat 0.80 m deep, chaise 0.80 x 1.80 m on the left (seen from the front), "
          "open corner 2.20 x 1.00 m")
L_DETAILS = {"l_outline": {"chaise_side": "left", "chaise_depth": 1.8, "seat_depth": 0.8, "chaise_width": 0.8},
             "l_front": 270.0}


def _piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def _works(**details):
    items = [SimpleNamespace(element_id=pid, details=dict(det)) for pid, det in details.items()]
    return {"page": SimpleNamespace(extraction=SimpleNamespace(furniture=items, report={}, level_id="L0"))}


def edit(op, **args):
    return dict({"op": op, "reason": "test", "round": 1, "log_seq": 1, "model": "test"}, **args)


# --------------------------------------------------------------------------
# The corner sofa's open corner: its coffee table, never the room's missing sofa
# --------------------------------------------------------------------------

def _salon(l_typed: bool = False) -> dict:
    """A 6 x 5 m living room: the drawn L corner sofa along the north wall (box 3.0 x 1.8 m, chaise on the west, the
    open corner to the south-east), a 1.30 x 0.63 m outline in its open corner (P5 f_L-1_061) and a 0.59 m round
    symbol by the south-east window corner (f_L-1_063, a floor lamp)."""
    sofa = M.fp("l1", "sofa_corner" if l_typed else "unknown", (3.0, 4.1), (3.0, 1.8), front=270.0 if l_typed else None)
    sofa["evidence"][0]["note"] = L_NOTE
    if l_typed:
        sofa.update(shape="L", chaise_side="left", chaise_depth=1.8, seat_depth=0.8, chaise_width=0.8,
                    type_method="rule")
    phantom = M.fp("p1", "unknown", (3.4, 3.7), (1.3, 0.63), front=None)
    lamp = M.fp("lp", "unknown", (5.5, 0.6), (0.59, 0.59), front=None)
    return M.building(w=6.0, h=5.0, room_type="living", window=None, furniture=[sofa, phantom, lamp])


def test_group_member_waits_for_an_untyped_l_outline():
    """Fails on BASE: the room-kind rule typed the outline in the L's open corner as "the living room's missing sofa"
    while the L itself (its note on the vector evidence) was still untyped, and the lamp then became that phantom
    sofa's coffee table (P5 real04 and P4a real02: f_L-1_061 sofa, f_L-1_063 table_coffee)."""
    props = {p["piece_id"]: p["type"] for p in INF.code_types(_salon())}
    assert props.get("p1") != "sofa" and props.get("lp") != "table_coffee"
    assert INF._l_outline_waits(_salon(), _piece(_salon(), "p1"), _salon()["rooms"][0]) == "l1"
    # mutation guard: without the L note the room really misses its sofa (the rule is kept for other rooms)
    plain = _salon()
    _piece(plain, "l1")["evidence"][0]["note"] = "cluster"
    assert {p["piece_id"]: p["type"] for p in INF.code_types(plain)}.get("p1") == "sofa"


def test_the_reading_types_the_corner_sofa_first_and_its_open_corner_holds_the_coffee_table():
    """Fails on BASE (``read_furniture``: the code typing ran before the corner-sofa rule): the drawn L becomes the
    corner sofa, the outline in its open corner its coffee table, and the lamp symbol by the window is no coffee table
    (left for review / the AI, P3's two passes said floor_lamp)."""
    build = ProjectBuild(_salon())
    RD.read_furniture(build, _works(l1=L_DETAILS))
    b = build.building
    assert _piece(b, "l1")["type"] == "sofa_corner" and _piece(b, "l1").get("shape") == "L"
    assert _piece(b, "p1")["type"] == "table_coffee"
    assert _piece(b, "lp")["type"] != "table_coffee"
    assert RD.corner_sofa_pass(ProjectBuild(_salon()), {}) == []      # no L outline in the details: nothing


SALON = [[1.2, 0.2], [8.386, 0.2], [8.386, 7.422], [5.618, 7.422], [5.618, 7.507], [4.242, 7.507], [4.242, 7.042],
         [1.2, 7.042]]
# P5 real04 r_L-1_salon (building.json): (id, type as the drawing named it or None, centre, size, rotation, front)
SALON_PIECES = [("f_L-1_024", "wardrobe", (6.902, 7.071), (2.568, 0.743), 0.0, 270.0),
                ("f_L-1_027", "table_dining", (7.045, 4.226), (3.35, 1.0), 90.0, None),
                ("f_L-1_049", "armchair", (3.659, 6.234), (0.992, 0.843), 180.0, 90.0),
                ("f_L-1_053", None, (4.08, 3.271), (4.376, 1.966), 270.0, None),
                ("f_L-1_059", None, (2.279, 0.698), (0.593, 0.593), 180.0, None),
                ("f_L-1_060", None, (1.884, 0.992), (0.79, 0.79), 90.0, None),
                ("f_L-1_061", None, (3.309, 3.174), (1.296, 0.631), 90.0, None),
                ("f_L-1_063", None, (5.3, 0.74), (0.593, 0.593), 0.0, None),
                ("f_L-1_064", None, (5.677, 1.017), (0.445, 0.445), 270.0, None),
                ("f_L-1_073", None, (7.117, 1.003), (0.559, 0.559), 270.0, None),
                ("f_L-1_087", None, (3.24, 5.633), (0.712, 0.405), 143.557, None)]
SALON_CHAIRS = [((7.596, y), 270.0, 180.0) for y in (5.422, 4.224, 3.633, 3.042, 4.837)] + \
               [((6.479, y), 90.0, 0.0) for y in (5.422, 4.224, 3.633, 3.042, 4.837)]


def _p5_salon(l_typed: bool) -> dict:
    """P5's basement salon in the reading's first-pass state: the block-named and split pieces typed, the rest
    untyped boxes; the corner sofa f_L-1_053 untyped with its L note, or (``l_typed``) typed as the reading's
    corner-sofa rule types it now, before the code typing."""
    pieces = []
    for pid, ftype, c, size, rot, front in SALON_PIECES:
        f = M.fp(pid, ftype or "unknown", c, size, rotation=rot, front=front,
                 type_method="block_name" if ftype else "none")
        pieces.append(f)
    for k, (c, rot, front) in enumerate(SALON_CHAIRS):
        pieces.append(M.fp(f"f_L-1_c{k}", "chair", c, (0.5, 0.45), rotation=rot, front=front, type_method="rule"))
    sofa = next(f for f in pieces if f["id"] == "f_L-1_053")
    sofa["evidence"][0]["note"] = ("L outline 4.38 x 1.97 m: main seat 0.75 m deep, chaise 0.76 x 1.97 m on the right "
                                   "(seen from the front), open corner 1.22 x 3.62 m")
    if l_typed:
        sofa.update(type="sofa_corner", type_method="rule", shape="L", chaise_side="right", chaise_depth=1.9657,
                    seat_depth=0.7473, chaise_width=0.7572, front_deg=180.0)
    b = M.building(w=8.4, h=7.6, room_type="living", window=None, door_x=6.0, furniture=pieces)
    b["rooms"][0]["polygon"] = SALON
    return b


def test_p5_salon_first_pass_gives_no_phantom_sofa_and_no_lamp_coffee_tables():
    """Fails on BASE (P5's code typing on this room gave f_L-1_061 sofa and f_L-1_063 table_coffee): with the corner
    sofa still an untyped L, nothing is "the missing sofa"; with the L typed first (the reading's order now), the
    outline in its open corner is its coffee table and none of the window lamps (f_L-1_059/060/063/064) is."""
    props = {p["piece_id"]: p["type"] for p in INF.code_types(_p5_salon(False))}
    assert props.get("f_L-1_061") != "sofa"
    assert not {pid for pid, t in props.items() if t == "table_coffee"} & {"f_L-1_059", "f_L-1_060", "f_L-1_063",
                                                                           "f_L-1_064"}
    typed = {p["piece_id"]: p["type"] for p in INF.code_types(_p5_salon(True))}
    assert typed.get("f_L-1_061") == "table_coffee"
    assert not {pid for pid, t in typed.items() if t == "table_coffee"} & {"f_L-1_059", "f_L-1_060", "f_L-1_063",
                                                                           "f_L-1_064"}


def test_a_coffee_table_or_tv_unit_by_group_member_only_at_its_place():
    """Fails on BASE: the group-member rule gave the seating's coffee table and TV unit to any footprint of the
    right size in the room. A square in a far corner is no coffee table and a strip on the side wall no TV unit (the
    plan crop decides); the table in front of the sofa and the strip on the wall it faces still are."""
    sofa = M.fp("s", "sofa", (2.5, 3.55), (2.2, 0.9), front=270.0, type_method="block_name")
    far = M.fp("far", "unknown", (4.6, 0.4), (0.59, 0.59), front=None)
    side = M.fp("side", "unknown", (0.225, 2.0), (1.6, 0.45), rotation=90.0, front=None)
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, door_x=4.0, furniture=[sofa, far, side])
    room = b["rooms"][0]
    assert INF.coffee_zone_anchor(b, far, room) is None and INF.tv_place_anchor(b, side, room) is None
    props = {p["piece_id"]: p["type"] for p in INF.code_types(b)}
    assert props.get("far") != "table_coffee" and props.get("side") != "tv_unit"
    ct = M.fp("ct", "unknown", (2.5, 2.4), (1.0, 0.6), front=None)
    tv = M.fp("tv", "unknown", (2.5, 0.225), (1.6, 0.45), front=None)
    b2 = M.building(w=5.0, h=4.0, room_type="living", window=None, door_x=4.0, furniture=[sofa, ct, tv])
    props2 = {p["piece_id"]: p["type"] for p in INF.code_types(b2)}
    assert props2 == {"ct": "table_coffee", "tv": "tv_unit"}


def test_a_seat_in_the_corner_sofas_open_corner_is_retyped_as_its_coffee_table():
    """Fails on BASE (no such rule; user decision of 22 Oct 2026): a drawn piece the AI passes (or the group rule)
    typed as a sofa, standing in the open corner of a drawn L corner sofa, is that sofa's coffee table: retyped by code,
    ``adjusted_by_ai`` with ``by: code``, ``drawn_type`` and the plan crop; a block-named piece is left as drawn."""
    b = _salon(l_typed=True)
    p1 = _piece(b, "p1")
    p1.update(type="sofa", type_method="ai_two_pass")
    p1["evidence"].append({"file": "plan.dxf", "method": "ai", "confidence": 0.8, "entity": "recognition:sym_L0_009"})
    props = [p for p in INF.infer_types(b) if p["piece_id"] == "p1"]
    assert [p["type"] for p in props] == ["table_coffee"]
    out = _piece(INF.apply_inferences(b, props), "p1")
    assert out["type"] == "table_coffee" and out["type_method"] == "inferred" and out["drawn_type"] == "sofa"
    adj = out["adjusted_by_ai"]
    assert adj["by"] == "code" and adj["rule"] == INF.CORNER_TABLE_METHOD
    assert adj["crop"] == "recognition/crops/sym_L0_009_ctx.png" and "open corner" in adj["reason"]
    named = _salon(l_typed=True)
    _piece(named, "p1").update(type="sofa", type_method="block_name")
    assert INF.corner_tables(named) == []
    lamp = _salon(l_typed=True)
    _piece(lamp, "lp").update(type="sofa", type_method="ai_two_pass")        # not in the open corner
    assert INF.corner_tables(lamp) == []


# --------------------------------------------------------------------------
# Seat fronts
# --------------------------------------------------------------------------

def _line(sid, a, b, block="koltuk022"):
    return Stroke(id=sid, kind="line", pts=[tuple(map(float, a)), tuple(map(float, b))], block=block)


def _square(sid, x0, y0, x1, y1, block="koltuk022"):
    return Stroke(id=sid, kind="polyline", pts=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, block=block)


def _koltuk_sofa():
    """A 2.1 x 0.9 m koltuk sofa block (x 1.0-3.1, y 2.0-2.9): the back strip 0.2 m in along the north side, the two
    arms 0.2 m in along the ends, the seat open to the south, and two small leaning cushions near the south edge (the
    "two small closed shapes" the bed-pillow rule took for a head)."""
    strokes = [_square("o", 1.0, 2.0, 3.1, 2.9), _line("back", (1.2, 2.7), (2.9, 2.7)),
               _line("arm_w", (1.2, 2.0), (1.2, 2.7)), _line("arm_e", (2.9, 2.0), (2.9, 2.7)),
               _square("c1", 1.3, 2.05, 1.5, 2.25), _square("c2", 2.6, 2.05, 2.8, 2.25)]
    return SY.Cluster(SY._segments(strokes, set()))


def test_a_sofa_block_is_never_fronted_by_the_bed_pillow_rule():
    """Fails on BASE: the pillow rule ("head = side with >= 2 small closed shapes") ran on every block and turned
    real04's koltuk sofas f_L1_009..012 to face away from their coffee table; now the block's back strip and arms give
    the front (the open side), and a bed's pillows still give its head."""
    part = _koltuk_sofa()
    fp = SY.footprint([p for s in part.segs for p in s.pts], 0.0)
    ctx = SY._Ctx("t.dxf", None, None, 0.0, "L0")
    item = SY._block_item(part, fp, ctx, False, TABLE, None, [], [])
    assert item.type == "sofa" and item.front_deg == 270.0
    assert "head = side" not in (item.evidence.get("note") or "")
    assert SY.seat_back_front(part.segs, fp[0], fp[4], 0.0) == 270.0
    # mutation guard: without the back strip the front is open on two sides: no seat rule front
    loose = SY.Cluster([s for s in part.segs if s.stroke.id != "back"])
    assert SY.seat_back_front(loose.segs, fp[0], fp[4], 0.0) is None


def test_a_seat_without_a_front_faces_its_coffee_table():
    """Fails on BASE (``reading._front_of`` had no seat rule): a free-standing sofa or armchair without a front faces
    the nearest coffee table within 1.2 m (P5: the oyun sofas once the pillow fronts are gone: f_L1_009 0, f_L1_012
    270); a table at the sofa's short end gives no short-side front."""
    sofa = M.fp("s", "sofa", (2.5, 2.5), (2.0, 0.9), front=None)
    table = M.fp("t", "table_coffee", (2.5, 1.55), (1.0, 0.5), front=None)
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[sofa, table])
    front, why = RD._front_of(sofa, b["rooms"][0], [table])
    assert front == 270.0 and "coffee table t" in why
    end = M.fp("t2", "table_coffee", (4.1, 2.5), (0.6, 0.6), front=None)
    assert RD._front_of(sofa, b["rooms"][0], [end])[0] is None


def test_an_ai_front_on_a_sofas_short_side_goes_to_its_long_side():
    """Fails on BASE (no such step): P5's twin sofas f_L-1b_045/046 (0.82 x 1.64 m, both passes said 'left') were built
    as 0.82 m wide sofas (a false library gap). The front goes to the long side facing the room, labelled
    ``adjusted_by_ai`` by code with the drawn front kept; a block-named sofa is left to the reader's own rule."""
    sofa = M.fp("s", "sofa", (2.5, 3.0), (0.82, 1.64), rotation=270.0, front=180.0, type_method="inferred")
    build = ProjectBuild(M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[sofa]))
    assert RD.long_side_fronts(build, {}) == ["s"]
    f = _piece(build.building, "s")
    assert f["front_deg"] == 270.0 and sorted(f["footprint"]["size"]) == [0.82, 1.64]
    assert f["footprint"]["size"][0] == pytest.approx(1.64)
    assert f["drawn_front_deg"] == 180.0 and f["adjusted_by_ai"]["by"] == "code"
    assert f["adjusted_by_ai"]["rule"] == RD.LONG_FRONT_RULE
    named = M.fp("s", "sofa", (2.5, 3.0), (0.82, 1.64), rotation=270.0, front=180.0, type_method="block_name")
    assert RD.long_side_fronts(ProjectBuild(M.building(room_type="living", furniture=[named])), {}) == []


# --------------------------------------------------------------------------
# Desks with their chair, seat cushions
# --------------------------------------------------------------------------

def test_a_desk_symbol_that_holds_its_chair_is_split():
    """Fails on BASE (no such step): real04's desks f_L0_023..026 (1.45 x 0.91 m: a 0.6 m desk at the wall and the
    chair drawn in front, crop sym_L0_007) were built 0.85 m deep with no chair. The desk keeps 0.60 m at its wall
    (``adjusted_by_ai`` by code, ``drawn_footprint`` kept) and its chair is a drawn office chair facing it."""
    desk = M.fp("d", "desk", (2.5, 3.545), (1.45, 0.91), front=270.0, type_method="inferred")
    build = ProjectBuild(M.building(room_type="bedroom", window=None, furniture=[desk]))
    made = RD.desk_chairs(build, {})
    assert len(made) == 1
    b = build.building
    d, chair = _piece(b, "d"), _piece(b, made[0])
    assert d["footprint"]["size"] == [1.45, RD.DESK_DEPTH_M]
    assert d["footprint"]["center"][1] == pytest.approx(4.0 - RD.DESK_DEPTH_M / 2.0)
    assert d["drawn_footprint"]["size"] == [1.45, 0.91] and d["adjusted_by_ai"]["by"] == "code"
    assert chair["type"] == "office_chair" and chair["front_deg"] == 90.0 and chair["source"] == "from_documents"
    assert chair["footprint"]["center"][1] == pytest.approx(4.0 - 0.91 + RD.DESK_CHAIR_M[1] / 2.0)
    free = M.fp("d", "desk", (2.5, 2.0), (1.45, 0.91), front=270.0)            # not at a wall: as drawn
    assert RD.desk_chairs(ProjectBuild(M.building(room_type="bedroom", furniture=[free])), {}) == []


def test_a_seat_cushion_read_as_an_ottoman_is_not_built():
    """Fails on BASE (no such step): real04's 0.47 x 0.48 m "ottomans" f_L-1_075..078 lie 85 % inside the armchairs
    f_L-1_069..072 (their seat cushions; CLAUDE.md "a cushion read as a sofa"): not built, labelled by code; a real
    ottoman in front of the armchair stays."""
    chair = M.fp("a", "armchair", (2.0, 2.0), (0.64, 0.57), rotation=270.0, front=180.0, type_method="rule")
    cushion = M.fp("o", "ottoman", (1.88, 2.0), (0.47, 0.48), rotation=90.0, front=0.0, type_method="ai_two_pass")
    stool = M.fp("o2", "ottoman", (1.2, 2.0), (0.45, 0.45), front=None, type_method="ai_two_pass")
    build = ProjectBuild(M.building(room_type="living", window=None, furniture=[chair, cushion, stool]))
    assert RD.seat_cushions(build, {}) == ["o"]
    o = _piece(build.building, "o")
    assert o["build"] is False and o["inferred_as"] == "detail" and o["drawn_type"] == "ottoman"
    assert o["adjusted_by_ai"]["not_furniture"] == "seat_cushion" and o["adjusted_by_ai"]["by"] == "code"
    assert _piece(build.building, "o2").get("build") is not False


# --------------------------------------------------------------------------
# The coat closet: a hanging rail with hangers
# --------------------------------------------------------------------------

def _closet(rail: bool = True, planks: bool = False):
    """A 1.52 x 0.60 m outline (a table size) with two chair-sized parts at its ends (P5 f_L1_021..023), holding a
    rail along its centre line crossed by 12 hangers (a coat closet), or plank lines wall to wall (a table)."""
    strokes = [Stroke(id="o", kind="polyline", pts=[(0.0, 0.0), (1.52, 0.0), (1.52, 0.6), (0.0, 0.6)], closed=True),
               Stroke(id="c1", kind="polyline", pts=[(-0.45, 0.1), (-0.05, 0.1), (-0.05, 0.5), (-0.45, 0.5)],
                      closed=True),
               Stroke(id="c2", kind="polyline", pts=[(1.57, 0.1), (1.97, 0.1), (1.97, 0.5), (1.57, 0.5)],
                      closed=True)]
    if rail:
        strokes.append(Stroke(id="rail", kind="line", pts=[(0.05, 0.3), (1.47, 0.3)]))
        for k in range(12):
            x = 0.12 + 0.11 * k
            strokes.append(Stroke(id=f"h{k}", kind="polyline", pts=[(x - 0.03, 0.08), (x, 0.3), (x - 0.03, 0.52)]))
    if planks:
        for k in range(6):
            x = 0.2 + 0.22 * k
            strokes.append(Stroke(id=f"p{k}", kind="line", pts=[(x, 0.0), (x, 0.6)]))
    return SY.Cluster(SY._segments(strokes, set()))


def test_a_coat_closet_with_its_hanging_rail_is_one_wardrobe():
    """Fails on BASE: the M11 split read real04's / real02's corridor coat closet (a rail with hangers) as a coffee
    table and two chairs (one through the wall into the terrace). Now one wardrobe rule item, no chairs; a table with
    chairs (and a table drawn with plank lines) still splits."""
    split = SY.split_table_chairs(_closet(), TABLE, 0.0)
    assert split is not None and split.get("wardrobe") and split["chairs"] == []
    assert split["wardrobe"]["hangers"] == 12
    ctx = SY._Ctx("t.dxf", None, None, 0.0, "L1")
    made = SY.table_chair_items(split, ctx, False, TABLE)
    assert [m.type for m in made] == ["wardrobe"] and made[0].type_method == "rule"
    assert "coat closet" in made[0].evidence["note"]
    assert sorted(round(v, 2) for v in made[0].size) == [0.6, 1.52]
    for table_like in (_closet(rail=False), _closet(rail=False, planks=True)):
        plain = SY.split_table_chairs(table_like, TABLE, 0.0)
        assert plain is not None and not plain.get("wardrobe") and len(plain["chairs"]) == 2
        assert [m.type for m in SY.table_chair_items(plain, ctx, False, TABLE)] == ["table_coffee", "chair", "chair"]


# --------------------------------------------------------------------------
# A bath or shower a few cm longer than its bay (user decision of 22 Oct 2026)
# --------------------------------------------------------------------------

def _bay(length: float) -> dict:
    """A 1.57 m wide bathroom bay (P4b real03: drawn tubs of 1.62 m) with a drawn bathtub along the north wall."""
    tub = M.fp("tub", "bathtub", (0.785, 2.1), (length, 0.8), front=270.0, type_method="block_name")
    return M.building(w=1.57, h=2.5, room_type="bathroom", window=None, door_x=0.8, furniture=[tub])


def test_a_tub_a_few_cm_longer_than_its_bay_is_shrunk_to_a_real_product_at_the_reading():
    """Fails on BASE: a drawn tub 5 cm longer than its bay was built through both walls (S2 every round, P4b). Now
    the nearest real product that fits the clear bay, its back on its wall, ``drawn_footprint`` kept,
    ``adjusted_by_ai`` by code with "misread size"; a tub 13 cm too long is no misread of this kind."""
    build = ProjectBuild(_bay(1.62))
    assert RD.fix_fixed(build, {}) == ["tub"]
    tub = _piece(build.building, "tub")
    # pin changed on purpose at the integration of the fix round after P5: the size table now lists 1.55 x 0.75 m
    # (and the other intermediate tubs), so the nearest real product that fits the 1.57 m bay is a few cm smaller
    assert tub["footprint"]["size"] == [1.55, 0.75]
    assert tub["footprint"]["center"] == pytest.approx([0.785, 2.5 - 0.375])
    assert tub["drawn_footprint"]["size"] == [1.62, 0.8] and tub["adjusted_by_ai"]["by"] == "code"
    assert tub["adjusted_by_ai"]["rule"] == RD.BAY_RULE and "misread size" in tub["adjusted_by_ai"]["reason"]
    over = RD.bay_overrun(_piece(_bay(1.62), "tub"), M_poly(_bay(1.62)))
    assert over["overrun_m"] == pytest.approx(0.05, abs=1e-3) and over["clear"][0] == pytest.approx(1.57, abs=1e-3)
    assert RD.bay_overrun(_piece(_bay(1.70), "tub"), M_poly(_bay(1.70))) is None
    assert RD.bay_overrun(_piece(_bay(1.56), "tub"), M_poly(_bay(1.56))) is None


def M_poly(b):
    from shapely.geometry import Polygon
    return Polygon(b["rooms"][0]["polygon"])


def test_fix_fixture_shrinks_a_tub_a_few_cm_longer_than_its_bay():
    """Fails on BASE: ``fix_fixture`` refused ("no valid spot within 0.50 m": a tub longer than its bay fits nowhere)
    and the model then tried centres in 5 cm steps; now it takes the nearest real product that fits the bay. A centre
    that is still in the wall is refused with a text that says no centre will do."""
    b = _bay(1.62)
    res = E.apply_edit(b, edit("fix_fixture", piece_id="tub"))
    assert res["accepted"], res["failed_checks"]
    tub = _piece(res["building"], "tub")
    # 1.55 x 0.75 since the integration of the fix round after P5 (intermediate tubs in the size table; was 1.50 x 0.70)
    assert tub["footprint"]["size"] == [1.55, 0.75] and tub["adjusted_by_ai"]["fix_fixture"]["bay"]["overrun_m"] > 0.04
    assert tub["drawn_footprint"]["size"] == [1.62, 0.8]
    far = _bay(1.70)
    res = E.apply_edit(far, edit("fix_fixture", piece_id="tub", center=[0.80, 2.1]))
    assert not res["accepted"] and "do not try centres" in res["failed_checks"][0]


# --------------------------------------------------------------------------
# The mark lock and the plan crop
# --------------------------------------------------------------------------

def _closet_table() -> dict:
    """P5's f_L1_021: the M11 split's coffee table (rule, vector) in a hall, which the AI passes typed 'bench'."""
    t = M.fp("f_L1_021", "table_coffee", (1.2, 3.6), (1.5175, 0.6), front=None, type_method="rule")
    b = M.building(w=5.0, h=4.0, room_type="hall", window=None, furniture=[t])
    b["conflicts"] = [{"kind": "type_disagreement", "element_ids": ["f_L1_021"],
                       "description": "f_L1_021: the AI passes typed it bench; split rule",
                       "resolution": "typed table_coffee (trust order: vector geometry and block names > AI)"}]
    return b


def test_the_mark_lock_holds_when_the_ai_passes_typed_the_piece_as_furniture_too():
    """Fails on BASE: P5 seq 5021 marked the drawn coffee table f_L1_021 as not furniture ("a stair", a camera plan
    crop) because the type_disagreement conflict lifted the lock. Both readings call it furniture, so the doubt is
    which piece it is (retype_piece): the conflict and an RC finding no longer lift the lock; NR and the piece's own
    crop still do; a conflict that names no AI type keeps the old rule."""
    b = _closet_table()
    item = _piece(b, "f_L1_021")
    cam = "plan crop check/cam_r_L1_koridor_1_plan.jpg: identical to the drawn stair"
    assert E.ai_furniture_dispute(b, item) == "bench"
    for target in (None, {"check": "F1"}, {"check": "RC"}):
        refusal = E.mark_lock_refusal(b, item, target, cam)
        assert refusal is not None and "retype_piece" in refusal and "bench" in refusal, target
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="f_L1_021", kind="other", evidence=cam,
                               target_finding={"check": "F1", "target": "f_L1_021"}))
    assert not res["accepted"] and res["failed_checks"][0].startswith("drawn_lock")
    assert E.mark_lock_refusal(b, item, {"check": "NR"}, cam) is None
    own = copy.deepcopy(b)
    _piece(own, "f_L1_021")["evidence"].append({"file": "x", "method": "ai", "entity": "recognition:sym_L1_001"})
    assert E.mark_lock_refusal(own, _piece(own, "f_L1_021"), None, "recognition/crops/sym_L1_001_ctx.png") is None
    plain = copy.deepcopy(b)
    plain["conflicts"][0]["description"] = "f_L1_021: page 1 and page 2 disagree"
    assert E.mark_lock_refusal(plain, _piece(plain, "f_L1_021"), None, cam) is None


def test_an_untyped_piece_is_marked_only_with_its_plan_crop():
    """Fails on BASE: P5 seq 5388 marked the untyped 5.14 x 2.37 m cluster f_L-1b_001 with "plan crop of
    r_L-1b_salon_2" and no image (symbol crop null). Now refused without an image; a crop recorded for the piece in
    the review list is used when the evidence names none."""
    blob = M.fp("f_L-1b_001", "unknown", (2.5, 2.0), (4.0, 2.37), front=None, status="unverified", build=False,
                not_built_reason="untyped")
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[blob])
    text = "plan crop of r_L-1b_salon_2: a 5.14 x 2.37 m untyped cluster of lines, no furniture"
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="f_L-1b_001", kind="other", evidence=text))
    assert not res["accepted"] and res["failed_checks"][0].startswith("no_crop")
    b["needs_review"] = [{"id": "f_L-1b_001", "kind": "untyped_piece",
                          "crop": "recognition/crops/sym_L-1b_001_ctx.png"}]
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="f_L-1b_001", kind="other", evidence=text))
    assert res["accepted"], res["failed_checks"]
    assert res["building"]["symbols"][0]["crop"] == "recognition/crops/sym_L-1b_001_ctx.png"


# --------------------------------------------------------------------------
# Fix round after P5 (22 Oct 2026), review: the reading track's review findings
# --------------------------------------------------------------------------

def _ai(ftype: str, front: str) -> dict:
    from wenart.recognition import answers as A
    ans = {"type": ftype, "front": front, "confidence": 0.8, "reason": "seen from above"}
    return {k: dict(ans) for k in A.MODEL_KEYS}


def _pillow_candidate(size=(2.0, 0.9), rule: str = INF.PILLOW_FRONT_NOTE) -> dict:
    w, d = size
    return {"key": "sym_L0_1", "file": "plan.dxf", "page": 1, "element_id": "f_L0_001",
            "footprint": {"center": [2.0, 2.0], "size": [w, d], "rotation_deg": 0.0}, "strokes": [],
            "bbox": [2.0 - w / 2, 2.0 - d / 2, 2.0 + w / 2, 2.0 + d / 2],
            "front_candidates": [{"front_deg": 90.0, "rule": rule}]}


def test_review_an_ai_typed_seat_is_never_fronted_by_the_bed_pillow_rule():
    """Fails before the review fix: an unnamed sofa with two cushions near one long side got the pillow front 90
    ('head = side ...') as its drawn front, kept over both AI passes ('bottom'): it faced away from its group. Only
    block-named seats were fixed. Now ``decide`` drops the pillow rule when the passes name types and none is a bed."""
    from wenart.recognition import symbols as RS

    table = RS.load_size_table()
    res = RS.decide(_pillow_candidate(), _ai("sofa", "bottom"), table, "living")
    assert res["type"] == "sofa" and res["front"] == 270.0 and res["front_conflict"] is None
    res = RS.decide(_pillow_candidate(), _ai("sofa", "none"), table, "living")
    assert res["front"] is None and res["front_rule"] is None                    # no assumed pillow front either
    assert any("bed-pillow" in w for w in res["warnings"])
    # a rule the pillow rule agreed with stays (only the pillow part goes)
    wall = "only side within 0.25 m of a wall is the back"
    res = RS.decide(_pillow_candidate(rule=f"{wall}; {INF.PILLOW_FRONT_NOTE}"), _ai("sofa", "none"), table, "living")
    assert res["front"] == 90.0 and res["front_rule"] == wall
    # mutation guard: a bed keeps its pillows' head (the drawn front over the AI), as before
    res = RS.decide(_pillow_candidate(size=(1.6, 2.0)), _ai("bed_double", "bottom"), table, "bedroom")
    assert res["front"] == 90.0 and res["front_conflict"] is not None
    assert RS.HEAD_RULE_TYPES == SY.HEAD_RULE_TYPES


def test_review_a_desk_of_a_real_depth_or_with_its_chair_drawn_is_not_split():
    """Fails before the review fix: a block-named 1.60 x 0.85 m desk (a real desk size) was cut to 0.60 m and a
    second 'from_documents' office chair was added in front of the drawn one. The split is for a desk symbol deeper
    than any real desk (> 0.90 m) with no seat drawn in front; real04's 1.45 x 0.91 m desks still split."""
    desk = M.fp("d2", "desk", (2.5, 3.575), (1.6, 0.85), front=270.0, type_method="block_name")
    build = ProjectBuild(M.building(room_type="bedroom", window=None, furniture=[desk]))
    assert RD.desk_chairs(build, {}) == [] and RD.DESK_SPLIT_DEPTH_M == pytest.approx(0.90)
    desk = M.fp("d", "desk", (2.5, 3.545), (1.45, 0.91), front=270.0, type_method="inferred")
    chair = M.fp("c", "office_chair", (2.5, 2.85), (0.55, 0.55), rotation=180.0, front=90.0,
                 type_method="block_name")
    build = ProjectBuild(M.building(room_type="bedroom", window=None, furniture=[desk, chair]))
    assert RD.desk_chairs(build, {}) == []
    b = build.building
    assert len(b["furniture"]) == 2 and _piece(b, "d")["footprint"]["size"] == [1.45, 0.91]
    assert "adjusted_by_ai" not in _piece(b, "d")
    # mutation guard: the same desk without the drawn chair still splits (real04 f_L0_023..026)
    alone = ProjectBuild(M.building(room_type="bedroom", window=None,
                                    furniture=[M.fp("d", "desk", (2.5, 3.545), (1.45, 0.91), front=270.0)]))
    assert len(RD.desk_chairs(alone, {})) == 1


def test_review_a_sofa_with_one_arm_on_a_wall_faces_along_its_long_side():
    """Fails before the review fix: ``_front_of``'s one-wall rule put the back on the only side on a wall, so a sofa
    standing as a room divider with one arm on the wall faced along its length (front 0, a short side) and nothing
    corrected it later (``long_side_fronts`` skips block-named pieces and runs before the last ``infer_fronts``). A
    type that faces along a long side never gets a short-side front from these rules: the long side facing the most
    room."""
    sofa = M.fp("s", "sofa", (1.0, 1.5), (2.0, 0.9), front=None, type_method="block_name")
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, door_x=4.0, furniture=[sofa])
    front, why = RD._front_of(sofa, b["rooms"][0], [])
    assert front == 90.0 and not RD._short_side_front(sofa["footprint"], front)
    build = ProjectBuild(b)
    assert RD.infer_fronts(build) == 1
    f = _piece(build.building, "s")
    assert f["front_deg"] == 90.0 and not RD._short_side_front(f["footprint"], 90.0)
    # mutation guard: a bed still puts its head (a short side) on the wall
    bed = M.fp("bd", "bed_double", (1.0, 1.5), (2.0, 1.6), front=None)
    bb = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, door_x=4.0, furniture=[bed])
    assert RD._front_of(bed, bb["rooms"][0], [])[0] == 0.0


def _box_corner_sofa_room(l_shape: bool = False) -> dict:
    """A corner sofa typed without its L (real03's f_L0_190/196: a 2.1 x 1.5 m box; ``l_shape`` adds the drawn L:
    the main seat along the north, the chaise on the left seen from the front, the open corner to the south-east)
    with a 0.45 m pouf in the box's open corner."""
    sofa = M.fp("cs", "sofa_corner", (3.0, 3.25), (2.1, 1.5), front=270.0, type_method="group_member")
    if l_shape:
        sofa.update(shape="L", chaise_side="left", chaise_depth=1.5, seat_depth=0.8, chaise_width=0.8)
    pouf = M.fp("pf", "ottoman", (3.7, 2.9), (0.45, 0.45), front=None, type_method="ai_two_pass")
    return M.building(w=5.0, h=4.0, room_type="living", window=None, door_x=4.0, furniture=[sofa, pouf])


def test_review_a_pouf_in_the_open_corner_of_a_corner_sofa_is_no_seat_cushion():
    """Fails before the review fix: a corner sofa without its L counted its whole box as the seat, so a drawn pouf
    in the open corner lay 100 % inside and was removed as a 'seat cushion'. A corner sofa hosts a cushion only on
    its drawn L body."""
    build = ProjectBuild(_box_corner_sofa_room())
    assert RD.seat_cushions(build, {}) == []
    assert _piece(build.building, "pf").get("build") is not False
    build = ProjectBuild(_box_corner_sofa_room(l_shape=True))
    assert RD.seat_cushions(build, {}) == []
    # mutation guard: a cushion on the L's main seat is still its cushion
    b = _box_corner_sofa_room(l_shape=True)
    b["furniture"].append(M.fp("cu", "ottoman", (3.5, 3.6), (0.45, 0.45), front=None, type_method="ai_two_pass"))
    assert RD.seat_cushions(ProjectBuild(b), {}) == ["cu"]


def test_review_a_second_code_correction_keeps_the_first_ones_record():
    """Fails before the review fix: ``_code_label`` replaced the label, so a desk whose short-side AI front
    ``long_side_fronts`` turned lost that record when ``desk_chairs`` split it (changed held no front_deg, the reason
    named only the split); ``_apply_nightstand`` did the same. The records merge: reasons joined, the earliest values
    in ``changed``, every rule listed."""
    desk = M.fp("d", "desk", (2.5, 3.545), (0.91, 1.45), rotation=90.0, front=0.0, type_method="ai_two_pass")
    drawn = copy.deepcopy(desk["footprint"])
    build = ProjectBuild(M.building(room_type="bedroom", window=None, furniture=[desk]))
    assert RD.long_side_fronts(build, {}) == ["d"]
    assert len(RD.desk_chairs(build, {})) == 1
    adj = _piece(build.building, "d")["adjusted_by_ai"]
    assert adj["by"] == "code" and adj["changed"]["front_deg"] == 0.0 and adj["changed"]["footprint"] == drawn
    assert adj["rules"] == [RD.LONG_FRONT_RULE, RD.DESK_RULE] and adj["rule"] == RD.DESK_RULE
    assert "faces along a long side" in adj["reason"] and "holds the chair" in adj["reason"]
    item = M.fp("x", "floor_lamp", (1.0, 1.0), (0.5, 0.5), front=270.0)
    item["adjusted_by_ai"] = {"by": "code", "stage": "reading", "rule": RD.LONG_FRONT_RULE, "reason": "first",
                              "changed": {"front_deg": 90.0}, "crop": "recognition/crops/sym_L0_001_ctx.png"}
    INF._apply_nightstand(item, {"type": "nightstand", "type_method": INF.NIGHTSTAND_METHOD, "reason": "second",
                                 "evidence": {"file": "plan.dxf", "method": "inferred", "confidence": 0.7},
                                 "front_deg": 180.0, "crop": None})
    adj = item["adjusted_by_ai"]
    assert adj["changed"] == {"front_deg": 90.0, "type": "floor_lamp"} and adj["reason"] == "first; second"
    assert adj["rules"] == [RD.LONG_FRONT_RULE, INF.NIGHTSTAND_METHOD]
    assert adj["crop"] == "recognition/crops/sym_L0_001_ctx.png"


def test_review_an_ottoman_both_passes_agreed_on_stays_in_the_corner_sofas_open_corner():
    """Fails before the review fix: ``corner_tables`` retyped an agreed 0.8 m ottoman in a corner sofa's open corner
    as a coffee table (an ottoman there is a normal design: ``plausibility.EXTRA_EXEMPT``); every P5 case was a
    'sofa'. An ottoman is retyped only when the AI passes did not agree on it (the group rule or the tie-break)."""
    b = _salon(l_typed=True)
    p1 = _piece(b, "p1")
    p1.update(type="ottoman", type_method="ai_two_pass", footprint=dict(p1["footprint"], size=[0.8, 0.8]))
    assert INF.corner_tables(b) == []
    p1["type_method"] = "group_member"
    assert [p["piece_id"] for p in INF.corner_tables(b)] == ["p1"]
    _piece(b, "p1").update(type="sofa", type_method="ai_two_pass")           # P5: an agreed 'sofa' still is
    assert [p["piece_id"] for p in INF.corner_tables(b)] == ["p1"]


def test_review_a_bath_shrunk_to_its_bay_without_a_question_gets_a_plan_crop(tmp_path):
    """Fails before the review fix: a block-named shower or tub (no recognition question: real03 f_L0_054) shrunk to
    its bay was labelled with crop None. The reading now draws the plan crop from the vector walls and the drawn
    footprint (``recognition/reading/<piece>_ctx.png``) and records it; a question's own crop still wins."""
    build = ProjectBuild(_bay(1.62))
    build.out_dir = tmp_path
    assert RD.fix_fixed(build, {}) == ["tub"]
    tub = _piece(build.building, "tub")
    crop = tub["adjusted_by_ai"]["crop"]
    assert crop == f"{RD.READING_CROP_DIR}/tub_ctx.png" and (tmp_path / crop).is_file()
    assert any(crop in str(e.get("text") or "") for e in tub["evidence"])
    asked = ProjectBuild(_bay(1.62))
    asked.out_dir = tmp_path
    items = {"tub": SimpleNamespace(element_id="tub", details={"candidate_key": "sym_L0_009"})}
    assert RD.fix_fixed(asked, items) == ["tub"]
    assert _piece(asked.building, "tub")["adjusted_by_ai"]["crop"] == "recognition/crops/sym_L0_009_ctx.png"
