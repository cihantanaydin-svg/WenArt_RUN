"""Drawn sofas with their cushion marks are sofas, not rugs (27 Oct 2026; pod run 20261026-224516-full, real06's salon:
a 2.12 x 0.78 m and a 1.52 x 0.78 m drawn sofa each held 0.21 x 0.20 m cushion marks; two of the marks were typed
potted plants, the sofas became "rug outlines" and were never built, and the judge saw "a 55 m2 salon with no sofa").

- ``infer.small_mark`` / ``outline_holds``: a mark smaller than 0.30 m both ways is never a piece an outline is drawn
  around;
- ``infer.drawn_host_of``: a small mark inside a larger drawn outline (typed or not) is a detail of it (not built);
- ``names.zone_types_elsewhere``: the anchor type of a labelled zone the piece is not in (a dining table where the
  documents put the dining area elsewhere in the room) is never its type;
- ``infer._position_ok``: a sofa (back ``wall_or_group``) stands on a wall or in its group.
"""
from __future__ import annotations

import _m11_room as M
from wenart.furniture import infer as INF
from wenart.furniture import names as NM


def unknown(pid, center, size, rotation=0.0, **kw):
    return M.fp(pid, "unknown", center, size, rotation=rotation, front=None, status="unverified",
                type_method="none", **kw)


def test_cushion_marks_never_make_a_sofa_a_rug():
    sofa = unknown("u1", (3.0, 0.6), (2.12, 0.78), rotation=180.0,
                   type_candidates=[{"type": "unknown", "pass": 1}, {"type": "sofa", "pass": 2}])
    marks = [unknown("m1", (2.5, 0.5), (0.21, 0.20)), unknown("m2", (3.5, 0.5), (0.21, 0.20))]
    b = M.building(w=7.0, h=5.0, room_type="living", furniture=[sofa, *marks])
    props = {p["piece_id"]: p for p in INF.infer_types(b)}
    assert props["u1"]["type"] == "sofa" and props["u1"].get("build") is not False          # no rug
    for m in ("m1", "m2"):
        assert props[m]["type"] == INF.DETAIL_TYPE and props[m]["build"] is False
        assert "cushion" in props[m]["reason"] and "u1" in props[m]["reason"]
    assert INF.small_mark(marks[0]) and not INF.small_mark(sofa)
    # a real outline around real pieces stays a rug
    table = M.fp("t1", "table_coffee", (3.0, 2.5), (1.0, 0.6), front=None)
    rug = unknown("r1", (3.0, 2.4), (3.0, 2.2))
    b = M.building(w=7.0, h=5.0, room_type="living", furniture=[table, rug])
    assert [(p["piece_id"], p["type"]) for p in INF.infer_types(b)] == [("r1", "rug")]


def test_a_typed_host_or_an_untyped_one_holds_the_mark():
    sofa = M.fp("s1", "sofa", (3.0, 0.5), (2.2, 0.9), rotation=180.0, front=90.0)
    mark = unknown("m1", (3.0, 0.5), (0.21, 0.20))
    pieces = [sofa, mark]
    poly = INF.placer.drawn_piece(mark).polygon()
    assert INF.drawn_host_of(mark, poly, [sofa])["id"] == "s1"
    far = unknown("m2", (3.0, 3.0), (0.21, 0.20))
    assert INF.drawn_host_of(far, INF.placer.drawn_piece(far).polygon(), pieces) is None
    big = unknown("u9", (3.0, 3.0), (0.5, 0.5))                       # not a small mark: no host rule
    assert INF.drawn_host_of(big, INF.placer.drawn_piece(big).polygon(), pieces) is None


def test_a_labelled_zone_elsewhere_in_the_room_rules_out_its_anchor():
    b = M.building(w=9.0, h=6.0, room_type="living")
    b["zone_labels"] = [{"id": "TEXT:1", "room_id": M.ROOM_ID, "kind": "dining", "anchors": ["table_dining"],
                         "zone": [[0, 3], [4, 3], [4, 6], [0, 6]]}]
    seat = unknown("u1", (6.5, 0.6), (1.52, 0.78), rotation=180.0,
                   type_candidates=[{"type": "table_dining", "pass": 1}, {"type": "sofa", "pass": 2}])
    inside = unknown("u2", (2.0, 4.5), (1.6, 0.9))
    assert NM.zone_types_elsewhere(b, seat) == {"table_dining"}
    assert NM.zone_types_elsewhere(b, inside) == set()                # in the dining zone: its own anchor stays
    armchair = M.fp("a1", "armchair", (5.0, 1.8), (0.9, 0.8), front=0.0)
    b["furniture"] = [seat, armchair, M.fp("s9", "sofa", (8.0, 3.0), (2.0, 0.9), rotation=90.0, front=180.0)]
    props = {p["piece_id"]: p for p in INF.infer_types(b)}
    assert props["u1"]["type"] == "sofa"


def test_a_sofa_stands_on_a_wall_or_in_its_group():
    sofa = INF.placer.drawn_piece(M.fp("s", "sofa", (3.0, 2.0), (2.0, 0.85), front=90.0))
    chair = ("armchair", INF.placer.drawn_piece(M.fp("a", "armchair", (5.0, 2.0), (0.9, 0.8), front=180.0)))
    assert INF._position_ok("sofa", sofa, True, [])
    assert INF._position_ok("sofa", sofa, False, [chair])                 # free, beside its armchair
    lone = ("armchair", INF.placer.drawn_piece(M.fp("a", "armchair", (9.0, 9.0), (0.9, 0.8), front=180.0)))
    assert not INF._position_ok("sofa", sofa, False, [lone])
    assert not INF._position_ok("bed_double", sofa, False, [chair])      # a bed: on a wall only
