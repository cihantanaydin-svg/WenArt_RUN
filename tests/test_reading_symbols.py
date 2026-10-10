"""Milestone 12 track R (docs/milestone12.md §4.1 D7): what the generic core reads before a piece is furniture.

What: layer words (Turkish and English, folded), the Milestone 12 block-name words, the shapes of symbols (a
room-number circle, a door swing, a north arrow), whole-piece symbol decisions, the object groups of a re-read (one
part per block instance; a flat block's own strokes clustered), copy keys across inserts of one block, the content
keys of the extra questions, the stray-line trim of a named block, and the re-read of an oversized cluster.
Why: real03 built 43 unknown boxes, among them room-number circles read as floor lamps, door swings read as consoles
and 5-13 m clusters chained by trace and area lines; its toilets were 1.145 x 0.356 m because of an axis line.
How: synthetic strokes in metres (``tests/_real01_page.py`` helpers); every rule here did not exist before track R.
"""
import math

from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke, TextRun

import _real01_page as R

TABLE = SY.FALLBACK_SIZE_TABLE


def _segs(strokes):
    return SY._segments(list(strokes), set())


def _rect(x0, y0, x1, y1, **kw):
    return R.stroke([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, **kw)


def _circle(c, r):
    return R.arc(c, r, 0.0, 360.0)


def _text(text, centre, h=0.15):
    return TextRun(id=f"t:{text}", text=text, box=(centre[0] - h / 2, centre[1] - h / 2, centre[0] + h / 2,
                                                    centre[1] + h / 2), height=h)


def _on(layer, *strokes):
    for st in strokes:
        st.layer = layer
    return list(strokes)


# --------------------------------------------------------------------------
# Layer words and block words
# --------------------------------------------------------------------------

def test_layer_words_name_symbols_and_furniture_words_win():
    assert SY.layer_kind("MYD - IZ-1") == "other"                       # trace lines along the facades
    assert SY.layer_kind("MYD - ALAN-NET") == "dimension_outline"        # area outlines
    assert SY.layer_kind("Pkapı") == "door"                              # folded, a longer key anywhere in a word
    assert SY.layer_kind("xref$0$MYD - KOLON") == "structure"            # only the layer's own name counts
    assert SY.layer_kind("A-ANNO-TEXT") == "text_frame"
    assert SY.layer_kind("Pvitrifiye") == "furniture"                    # sanitary ware
    assert SY.layer_kind("TEFRIS-KAPI") == "furniture"                   # furniture words win
    assert SY.layer_kind("BAZA") is None                                 # BA (concrete) only as a whole word
    assert SY.layer_kind("0") is None and SY.layer_kind(None) is None


def test_a_furniture_named_block_on_a_services_layer_is_furniture():
    wc = R.stroke([(0, 0), (0.4, 0)], block="PLAN/KLOZET")
    wc.layer = "TESISAT"
    pipe = R.stroke([(0, 1), (2, 1)])
    pipe.layer = "TESISAT"
    assert SY.stroke_kind(wc) == "furniture" and SY.stroke_kind(pipe) == "other"
    keep, out = SY.split_symbol_strokes(_segs([wc, pipe]))
    assert [s.stroke for s in keep] == [wc] and list(out) == ["other"]


def test_m12_block_words_are_folded_turkish_and_english():
    assert SY.keyword_type("KOMODİN_01") == "nightstand"
    assert SY.keyword_type("ÇAMAŞIR MAKİNESİ") == "washing_machine"
    assert SY.keyword_type("evye-2") == "sink_kitchen"
    assert SY.keyword_type("Dishwasher 60") == "kitchen_counter"         # a base unit of the counter run
    assert SY.keyword_type("BERJER") == "armchair"
    assert SY.keyword_type("ORTA SEHPA") == "table_coffee"
    assert SY.keyword_type("GARDİROP") == "wardrobe"
    assert SY.keyword_type("REFRIGERATOR") == "fridge"


def test_m12_words_do_not_change_the_question_decisions_of_earlier_rounds():
    """The composite split and the candidates use the M7-M11 words only (``extended=False``): the parts, keys and
    input hashes of the questions asked before M12 stay as they were, so their answers still apply."""
    for name in ("KOMODİN_01", "Dishwasher 60", "BERJER"):
        assert SY._block_keyword(name) is None and SY.keyword_type(name, extended=False) is None
    assert SY._block_keyword("KOMIDIN") == "nightstand"                  # an M7 word still reads


# --------------------------------------------------------------------------
# Symbol shapes
# --------------------------------------------------------------------------

def test_a_small_circle_with_a_short_number_is_a_room_number_tag():
    circle = _circle((2.0, 2.0), 0.25)
    found = SY.whole_symbol(_segs([circle]), [_text("5", (2.0, 2.0))])
    assert found["kind"] == "room_number" and found["by"] == "shape" and "'5'" in found["reason"]
    assert SY.whole_symbol(_segs([circle]), [_text("SALON", (2.0, 2.0))]) is None
    assert SY.whole_symbol(_segs([circle]), []) is None                  # a round table or a plant without a number
    assert SY.whole_symbol(_segs([_circle((2.0, 2.0), 0.6)]), [_text("5", (2.0, 2.0))]) is None   # too large


def _leaf_and_arc(hinge=(0.0, 0.0), r=0.9):
    arc = R.arc(hinge, r, 0.0, 90.0)
    leaf = _rect(hinge[0], hinge[1], hinge[0] + 0.04, hinge[1] + r)
    return arc, leaf


def test_a_quarter_arc_with_its_leaf_from_the_hinge_is_a_door_swing():
    arc, leaf = _leaf_and_arc()
    found = SY.whole_symbol(_segs([arc, leaf]))
    assert found["kind"] == "door_arc" and "leaf" in found["reason"]
    # The same swing beside a fridge box: the swing is a symbol, the box goes on without it.
    box = _rect(-0.75, -0.7, -0.05, 0.0)
    swing, rest, _ = SY.door_swing(_segs([arc, leaf, box]))
    assert {s.stroke.id for s in swing} == {arc.id, leaf.id} and {s.stroke.id for s in rest} == {box.id}


def test_a_quadrant_shower_and_a_chair_back_are_no_door_swings():
    arc = R.arc((0.0, 0.0), 0.9, 0.0, 90.0)
    sides = [R.stroke([(0.0, 0.0), (0.9, 0.0)]), R.stroke([(0.0, 0.0), (0.0, 0.9)])]
    assert SY.door_swing(_segs([arc] + sides)) is None                  # plain sides, the corner is no jamb
    assert SY.door_swing(_segs([arc] + sides), jambs=[(0.02, 0.0)]) is not None   # hinged at an opening's jamb
    back = R.arc((0.0, 0.0), 0.25, 0.0, 180.0)
    assert SY.door_swing(_segs([back, _rect(-0.25, -0.45, 0.25, 0.0)])) is None
    named = R.arc((0.0, 0.0), 0.9, 0.0, 90.0)
    named.block = "DUS_KOSE"
    leaf = _rect(0.0, 0.0, 0.04, 0.9, block="DUS_KOSE")
    assert SY.door_swing(_segs([named, leaf])) is None                 # a furniture-named block


def test_a_circle_with_an_arrow_and_n_is_a_north_arrow():
    circle = _circle((5.0, 5.0), 0.6)
    arrow = R.stroke([(5.0, 4.5), (5.0, 5.5)])
    found = SY.whole_symbol(_segs([circle, arrow]), [_text("N", (5.0, 5.75))])
    assert found["kind"] == "north_arrow"


def test_pieces_on_symbol_layers_are_symbols_columns_or_decor():
    outline = _on("MYD - ALAN-NET", _rect(0, 0, 4, 3))
    assert SY.whole_symbol(_segs(outline)) == {"kind": "dimension_outline", "by": "layer",
                                               "reason": "drawn on the 'MYD - ALAN-NET' layer(s): "
                                                         "dimension_outline, not furniture"}
    column = SY.whole_symbol(_segs(_on("MYD - KOLON", _rect(0, 0, 0.3, 0.5))))
    assert column["as"] == "column" and column["by"] == "layer"
    assert SY.whole_symbol(_segs(_on("DEKOR", _rect(0, 0, 0.4, 0.4))))["as"] == "decor"
    door = SY.whole_symbol(_segs(_on("MYD - KAPI", R.arc((0, 0), 0.3, 0, 90), _rect(0, 0, 0.3, 0.3))))
    assert door["kind"] == "door_arc"
    mixed = _on("MYD - ALAN-NET", _rect(0, 0, 4, 3)) + _on("TEFRIS", _rect(1, 1, 2, 2))
    assert SY.whole_symbol(_segs(mixed)) is None                        # a furniture stroke among them


# --------------------------------------------------------------------------
# Object groups, copies, keys
# --------------------------------------------------------------------------

def _in_block(pts, block, sid, closed=False):
    return Stroke(id=sid, kind="polyline", pts=[tuple(map(float, p)) for p in pts], closed=closed, block=block)


def test_a_block_holding_no_block_is_one_object_and_a_flat_blocks_own_strokes_are_clustered():
    sink = [_in_block([(0, 0), (0.8, 0), (0.8, 0.5), (0, 0.5)], "FLAT_B/EVYE_01", "INSERT:7C/5/1", True),
            _in_block([(0.1, 0.1), (0.4, 0.1), (0.4, 0.4), (0.1, 0.4)], "FLAT_B/EVYE_01", "INSERT:7C/5/2", True)]
    table = _in_block([(2, 2), (3.2, 2), (3.2, 2.8), (2, 2.8)], "FLAT_B", "INSERT:7C/12", True)
    sofa = _in_block([(5, 2), (7.2, 2), (7.2, 2.9), (5, 2.9)], "FLAT_B", "INSERT:7C/13", True)
    segs = _segs(sink + [table, sofa])
    assert SY.containers_of([s.stroke for s in segs]) == {"INSERT:7C"}
    assert SY._object_key(sink[0]) == "INSERT:7C/5" and SY._object_key(table) == "INSERT:7C"
    parts = SY.object_groups(segs, TABLE, 0.0)
    by_ids = {tuple(p.stroke_ids()): p for p in parts}
    assert set(by_ids) == {("INSERT:7C/5/1", "INSERT:7C/5/2"), ("INSERT:7C/12",), ("INSERT:7C/13",)}
    assert by_ids[("INSERT:7C/5/1", "INSERT:7C/5/2")].note == ["block"]
    # A re-read of the flat's strokes alone still knows the flat is a container (taken over the page).
    alone = SY.object_groups(_segs([table, sofa]), TABLE, 0.0, containers={"INSERT:7C"})
    assert sorted(tuple(p.stroke_ids()) for p in alone) == [("INSERT:7C/12",), ("INSERT:7C/13",)]


def test_copy_keys_match_the_same_entity_in_two_inserts_of_one_block():
    a = _in_block([(0, 0), (1, 0)], "PLAN/FLAT_B", "INSERT:1/7/36")
    b = _in_block([(9, 0), (10, 0)], "PLAN/FLAT_B", "INSERT:1/9/36")
    c = _in_block([(9, 2), (10, 2)], "PLAN/FLAT_B", "INSERT:1/9/37")
    loose = R.stroke([(0, 5), (1, 5)])
    ka, kb, kc = (SY.copy_keys(_segs([s])) for s in (a, b, c))
    assert ka == kb and ka != kc and len(ka) == 1
    assert SY.copy_keys(_segs([loose])) == []


def test_extra_question_keys_are_content_keys():
    key = SY.extra_key("L0", ["INSERT:1/2", "INSERT:1/3", "INSERT:1/2"])
    assert key == SY.extra_key("L0", ["INSERT:1/3", "INSERT:1/2"])
    assert key.startswith("sym_L0_x") and len(key) == len("sym_L0_x") + SY.EXTRA_KEY_HEX
    assert key != SY.extra_key("L0", ["INSERT:1/2"])
    assert SY.expand_ids("path:3-5,curve:9") == ["path:3", "path:4", "path:5", "curve:9"]


# --------------------------------------------------------------------------
# Named blocks and the re-read of untyped clusters
# --------------------------------------------------------------------------

def test_an_axis_line_through_a_toilet_block_is_left_out_of_its_footprint():
    bowl = _in_block([(0, 0), (0.36, 0), (0.36, 0.55), (0, 0.55)], "KLOZET1", "INSERT:4/1", True)
    seat = _in_block([(0.05, 0.1), (0.31, 0.1), (0.31, 0.45), (0.05, 0.45)], "KLOZET1", "INSERT:4/2", True)
    axis = _in_block([(0.18, -0.3), (0.18, 0.85)], "KLOZET1", "INSERT:4/3")
    part = SY.Cluster(_segs([bowl, seat, axis]))
    fp = SY.footprint([p for s in part.segs for p in s.pts], 0.0)
    assert not SY.fits(TABLE, "toilet", (fp[1], fp[2]))                  # 1.15 x 0.36 m with the axis line
    trimmed, note = SY.trim_stray_lines(part, "toilet", TABLE, 0.0)
    assert SY.fits(TABLE, "toilet", (trimmed[1], trimmed[2])) and "INSERT:4/3" in note
    assert math.isclose(max(trimmed[1], trimmed[2]), 0.55, abs_tol=1e-6)


def _room(x0=0.0, y0=0.0, x1=9.0, y1=6.0, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _furniture(strokes, texts=(), notes=None, symbols_out=None, extra_out=None):
    walls = _room()
    outline = TP.building_outline(walls, [])
    return SY.furniture(list(strokes), set(), walls, [], list(texts), [], outline, [], level_id="L0",
                        file_rel="t.dxf", page_no=1, size_table=TABLE, notes=notes, symbols_out=symbols_out,
                        extra_out=extra_out)


def test_an_oversized_cluster_chained_by_trace_lines_is_re_read_into_its_pieces():
    """A sofa and a table joined by a 7 m trace line ('MYD - IZ-1') were one 7 m unknown box: the re-read drops the
    trace strokes (a symbol of kind ``other``) and reads the sofa and the table as their own pieces."""
    sofa = _rect(1.0, 1.0, 3.2, 1.9)
    table = _rect(5.0, 3.0, 6.2, 3.8)
    trace = R.stroke([(0.8, 1.9), (8.0, 1.9)])
    trace.layer = "MYD - IZ-1"
    hook = R.stroke([(6.2, 3.0), (6.2, 1.9)])
    hook.layer = "MYD - IZ-1"
    notes, symbols = [], []
    pieces, cands, _ = _furniture([sofa, table, trace, hook], notes=notes, symbols_out=symbols)
    found = list(pieces) + [c["item"] for c in cands]
    assert all(max(p.size) <= SY.MAX_SIDE_M for p in found)
    sizes = sorted(tuple(sorted((round(v, 2) for v in p.size), reverse=True)) for p in found)
    assert sizes == [(1.2, 0.8), (2.2, 0.9)]
    assert [s["kind"] for s in symbols] == ["other"] and "MYD - IZ-1" in symbols[0]["reason"]


def test_a_room_number_tag_among_the_furniture_is_marked_a_symbol():
    circle = _circle((4.0, 3.0), 0.25)
    pieces, cands, _ = _furniture([circle], texts=[_text("12", (4.0, 3.0))])
    found = list(pieces) + [c["item"] for c in cands]
    assert len(found) == 1 and found[0].details["symbol"]["kind"] == "room_number"


def test_the_unknown_parts_of_a_re_read_that_fit_a_type_are_asked_under_content_keys():
    sofa = _rect(1.0, 1.0, 3.2, 1.9)
    table = _rect(5.0, 3.0, 6.2, 3.8)
    trace = R.stroke([(0.8, 1.9), (8.0, 1.9)])
    hook = R.stroke([(6.2, 3.0), (6.2, 1.9)])
    trace.layer = hook.layer = "MYD - IZ-1"
    extras = []
    pieces, cands, _ = _furniture([sofa, table, trace, hook], extra_out=extras)
    # The M7 split takes the table out as an ordinary candidate (sequential key); the sofa is what the re-read found
    # in the 7 m rest: asked under the hash of its stroke ids.
    assert [c["key"] for c in cands] == ["sym_L0_001"] and c_ids(cands[0]) == [table.id]
    assert [e["key"] for e in extras] == [SY.extra_key("L0", [sofa.id])] and extras[0]["extra"] is True
    assert extras[0]["item"].details["candidate_key"] == extras[0]["key"]
    assert not [p for p in pieces if p.type == "unknown"]               # asked, not left as boxes


def c_ids(cand):
    return SY.expand_ids(cand["item"].evidence.get("entity"))


def _ctx():
    return SY._Ctx("t.dxf", 1, 1.0, 0.0, "L0")


def test_a_counter_drawn_as_one_outline_along_two_walls_is_re_read_as_its_legs_with_the_sink():
    """real03: the counters are loose outlines of the flat block, chained into the living room's cluster."""
    walls = _room()
    counter = R.stroke([(0.1, 5.9), (3.0, 5.9), (3.0, 5.3), (0.7, 5.3), (0.7, 3.0), (0.1, 3.0)], closed=True)
    bowl = _rect(1.2, 5.35, 2.0, 5.85)
    drain = _circle((1.6, 5.6), 0.03)
    notes = []
    got = SY.reread(SY.Cluster(_segs([counter, bowl, drain])), _ctx(), TABLE, walls, [],
                    [TP.wall_polygon(w) for w in walls], [], notes)
    types = sorted(it.type for it in got["items"])
    assert types == ["kitchen_counter", "kitchen_counter", "sink_kitchen"], notes
    sink = next(it for it in got["items"] if it.type == "sink_kitchen")
    assert sink.front_deg == 270.0 and "drain" in sink.evidence["note"]
