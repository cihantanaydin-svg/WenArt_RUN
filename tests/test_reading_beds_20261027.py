"""A drawn single bed in a bedroom is its bed (27 Oct 2026; pod run 20261027-091638-full, real06's r_L1_oda_2: the
judge saw "a bedroom without a bed"). The drawing holds a 0.90 x 1.90 m bed with its turned-down sheet and a
nightstand at its head; the reading made it a 2.65 m "sofa":

- ``symbols.layer_kind`` / ``symbols._drop_opening_lines``: the window sill line ('DENIZLIK', 4 cm off the wall face)
  touched the bed and joined its cluster; a straight stroke on an opening layer (doors, windows, sills, trims) along
  the walls is opening drawing, never furniture;
- ``infer._group_member_type``: the program of an 11 m2 bedroom asks for a double bed, so a single bed's footprint was
  never "the missing bed"; the room's anchor is any of its anchor types (``schemas.anchor_types``);
- ``infer`` / ``conservation.named_left_out``: a mark drawn on a piece (a cushion on its sofa) records ``detail_of``,
  and Argus's C7 never offers it as a lost potted plant.
"""
from __future__ import annotations

import _m11_room as M
import _real01_page as R
from wenart.audit import conservation as CV
from wenart.furniture import infer as INF
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke


def _layer(strokes, layer):
    return [Stroke(id=s.id, kind=s.kind, pts=s.pts, closed=s.closed, colour=s.colour, layer=layer) for s in strokes]


def _room(x0=0.0, y0=0.0, x1=4.0, y1=4.5, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _pieces(strokes, notes):
    walls = _room()
    outline = TP.building_outline(walls, [])
    pieces, cands, _decor = SY.furniture(strokes, set(), walls, [], [], [], outline, [], site_walls=[],
                                         level_id="L0", file_rel="t.dwg", page_no=1,
                                         size_table=SY.FALLBACK_SIZE_TABLE, notes=notes)
    return list(pieces) + [c["item"] for c in cands]


def test_a_sill_line_along_the_wall_never_joins_the_bed():
    assert SY.layer_kind("DENIZLIK") == "door" and SY.layer_kind("A-WINDOW-SILL") == "door"
    assert SY.layer_kind("tefriş") == "furniture"
    bed = _layer(R.edges(R.rect(0.15, 2.4, 1.05, 4.3)), "tefriş")          # 0.90 x 1.90 m against the west wall
    sill = _layer([R.stroke([(0.14, 0.9), (0.14, 2.45)])], "DENIZLIK")     # 4 cm off the face, touching the bed
    notes: list = []
    found = _pieces(bed + sill, notes)
    sizes = sorted(tuple(sorted(round(v, 2) for v in p.size)) for p in found if max(p.size) > 1.0)
    assert sizes == [(0.9, 1.9)], sizes
    assert any("opening layers along the walls" in n for n in notes)
    # a furniture-layer line there stays furniture (only opening layers are opening drawing)
    notes = []
    found = _pieces(bed + _layer(sill, "tefriş"), notes)
    assert any(max(p.size) > 2.5 for p in found)


def test_a_single_bed_is_the_missing_anchor_of_a_bedroom_whose_program_asks_for_a_double():
    bed = M.fp("u1", "unknown", (0.47, 2.5), (1.9, 0.9), rotation=90.0, front=None, status="unverified",
               type_method="none", build=False, not_built_reason="untyped (CLAUDE.md: no untyped piece is built)")
    b = M.building(w=3.0, h=3.8, room_type="bedroom", furniture=[bed])
    props = {p["piece_id"]: p for p in INF.code_types(b)}
    assert props["u1"]["type"] == "bed_single" and props["u1"]["type_method"] == "group_member"
    assert "bed_double | bed_single" in props["u1"]["reason"]
    # a room that already has a bed: no second anchor
    other = M.fp("b1", "bed_double", (2.0, 1.2), (2.0, 1.6), rotation=0.0)
    b = M.building(w=3.0, h=3.8, room_type="bedroom", furniture=[bed, other])
    assert all(p["type"] not in ("bed_single", "bed_double") for p in INF.code_types(b))


def test_a_cushion_mark_records_its_sofa_and_is_no_lost_piece():
    sofa = M.fp("s1", "sofa", (3.0, 0.5), (2.2, 0.9), rotation=180.0, front=90.0)
    mark = M.fp("m1", "unknown", (3.0, 0.5), (0.21, 0.20), front=None, status="unverified", type_method="none",
                type_candidates=[{"type": "potted_plant", "pass": 1}, {"type": "potted_plant", "pass": 2}],
                evidence=[{"file": "t.dwg", "method": "vector", "confidence": 0.9}])
    b = M.building(w=6.0, h=4.0, room_type="living", furniture=[sofa, mark])
    out = INF.apply_inferences(b, INF.infer_types(b))
    m = next(f for f in out["furniture"] if f["id"] == "m1")
    assert m["build"] is False and m["inferred_as"] == INF.DETAIL_TYPE and m["detail_of"] == "s1"
    assert not [f for f in CV.named_left_out(out) if f["target"] == "m1"]
    lost = dict(m, detail_of=None)                                         # a mark of no piece: C7 still looks
    assert [f["target"] for f in CV.named_left_out(dict(out, furniture=[sofa, lost]))] == ["m1"]


def test_argus_n5_names_a_bedrooms_missing_bed_and_the_piece_of_its_size():
    """N5 looked only where a group check named a missing member (kitchens, bathrooms); a bedroom without a bed is
    a gap too (``sense.anchor_gap``), and only a suspect of a bed's size is offered as it."""
    from wenart.audit import sense as SN

    sofa = M.fp("s1", "sofa", (1.0, 1.5), (1.9, 0.9), rotation=90.0, type_method="ai_two_pass",
                evidence=[{"method": "vector", "entity": "LINE:1"}])
    lamp = M.fp("l1", "armchair", (2.5, 3.0), (0.6, 0.6), type_method="ai_two_pass",
                evidence=[{"method": "vector", "entity": "LINE:2"}])
    b = M.building(w=3.0, h=3.8, room_type="bedroom", furniture=[sofa, lamp])
    found = [f for f in SN.set_links(b) if f["check"] == "N5"]
    assert [f["target"] for f in found] == ["s1"] and "bed_double|bed_single" in found[0]["message"]
    assert SN.anchor_gap(dict(b, furniture=[M.fp("b1", "bed_single", (1.0, 1.5), (1.9, 0.9))]), M.ROOM_ID,
                         [M.fp("b1", "bed_single", (1.0, 1.5), (1.9, 0.9))]) is None
