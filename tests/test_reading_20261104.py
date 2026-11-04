"""4 Nov 2026: real17 (user: "go ahead with real17"; then "Stop wasting time trying to correct the real17"). The
general rules its basement showed: a hatch's text island is no hole in the wall, a window in a slanted wall follows
the wall's angle, a window block across a gap is that window, two free ends casting at each other face one gap, a box
round a label is no wall, and a balcony's parapet does not hold a wing. CPU only."""
from __future__ import annotations

from types import SimpleNamespace

import ezdxf


def test_a_hatch_text_box_island_is_no_hole(tmp_path):
    """real17 L-1: the "25" thickness texts inside the slanted outer wall sit in text-box islands of its hatch; the
    wall mask had 0.41 m holes there and the outer wall broke into parts."""
    from wenart.ingest import dxf_generic as DG

    doc = ezdxf.new()
    msp = doc.modelspace()
    h = msp.add_hatch(color=7, dxfattribs={"layer": "DUVAR"})
    h.dxf.hatch_style = 1
    h.paths.add_polyline_path([(0, 0), (25, 0), (25, 500), (0, 500)], is_closed=True, flags=1)
    h.paths.add_polyline_path([(5, 200), (20, 200), (20, 240), (5, 240)], is_closed=True, flags=1 | 8)
    path = tmp_path / "h.dxf"
    doc.saveas(path)
    page = DG.read_page(path, "h.dxf")
    hatch = [st for st in page.strokes if st.id.startswith("HATCH")]
    assert len(hatch) == 1 and max(p[1] for p in hatch[0].pts) == 500


def _gap(O, slant=0.0):
    p = O.Piece(k=0, axis="v", c=19.14, t=0.26, a=9.776, b=10.052, wall=None)
    q = O.Piece(k=1, axis="v", c=19.085, t=0.27, a=10.542, b=12.806, wall=None)
    return O.Gap("end", "v", p.c, p.t, p.b, q.a, [p, q], free=(p, "end"), hit=q, slant=slant), p, q


def test_a_gap_between_the_steps_of_a_slanted_wall_carries_the_walls_angle():
    from wenart.ingest.generic import openings as O

    g, p, q = _gap(O)
    s = O._slant(p, q)
    assert 1.5 < s < 2.1                                   # the wall runs at 91.8 deg: x falls as y grows
    assert O._slant(q, p) == s                             # either piece first
    same = O.Piece(k=2, axis="v", c=19.15, t=0.26, a=11.0, b=12.0, wall=None)
    assert O._slant(p, same) == 0.0                        # one line
    far = O.Piece(k=3, axis="v", c=19.6, t=0.26, a=10.5, b=11.0, wall=None)
    assert O._slant(p, far) == 0.0                         # two walls side by side, not a slant
    # a window line drawn at the wall's angle is parallel to the gap with the slant, not without it
    a, b = (19.12, 10.135), (19.108, 10.455)
    assert not O._parallel(a, b, "v") and O._parallel(a, b, "v", s)


def test_a_window_block_across_a_gap_is_that_window():
    """real17: the WC windows are "fm-win1" blocks on the "pencere" layer whose glass covers 62 % of the gap."""
    from wenart.ingest.generic import openings as O

    g, _p, _q = _gap(O, 1.8)

    def item(sid, pts, block="fm-win1", layer="0"):
        return SimpleNamespace(st=SimpleNamespace(id=sid, block=block, layer=layer, closed=False), pts=pts)

    zone = [item("INSERT:E35D/2", [(19.12, 10.135), (19.108, 10.455)]),
            item("INSERT:E35D/7", [(19.133, 10.536), (19.098, 10.535)]),
            item("INSERT:E35D/8", [(19.148, 10.056), (19.113, 10.055)])]
    found = O._named_window(g, zone)
    assert found is not None and found[1] == "fm-win1" and len(found[0]) == 3
    # a block on a window layer counts; a door block, a block running past the gap or one outside the band does not
    assert O._named_window(g, [item(x.st.id, x.pts, "BLK1", "PENCERE") for x in zone]) is not None
    assert O._named_window(g, [item(x.st.id, x.pts, "KAPI-WIN") for x in zone]) is None
    assert O._named_window(g, zone + [item("INSERT:E35D/9", [(19.12, 9.5), (19.12, 11.2)])]) is None
    assert O._named_window(g, [item(x.st.id, [(px + 0.5, py) for px, py in x.pts]) for x in zone]) is None
    assert O._window_name("fm-win1") and O._window_name("Pencere 150") and not O._window_name("WINE_RACK")


def test_a_box_round_a_label_is_no_wall():
    """real17 L-1: the "8 NOLU DÜKKAN AİT DEPO" label boxes (2.83 x 0.3 m) were read as walls; a "25" thickness text in
    a wall outline keeps the wall."""
    from wenart.ingest.generic import walls as W
    from wenart.ingest.generic.model import GenericPage, Stroke, TextRun

    box = Stroke(id="ent:1", kind="polyline", pts=[(0, 0), (283, 0), (283, 30), (0, 30)], closed=True)
    wall = Stroke(id="ent:2", kind="polyline", pts=[(0, 100), (300, 100), (300, 125), (0, 125)], closed=True)
    label = TextRun(id="t1", text="8 NOLU DUKKAN AIT DEPO", box=(10, 5, 270, 25), height=15, rotation_deg=0,
                    source="vector")
    thick = TextRun(id="t2", text="25", box=(140, 105, 160, 120), height=12, rotation_deg=0, source="vector")
    page = GenericPage(file="x.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=0.01, size=(400, 200),
                       strokes=[box, wall], texts=[label, thick])
    prims = W._outline_walls(page, 0.01, set())
    assert [p.entity for p in prims] == ["ent:2"]


def test_a_balcony_label_does_not_hold_a_wing():
    from wenart.ingest.generic import topology as TP

    assert TP._outdoor_label(SimpleNamespace(room_type="balcony", name="x"))
    assert TP._outdoor_label(SimpleNamespace(room_type=None, name="BALKON"))
    assert not TP._outdoor_label(SimpleNamespace(room_type="bedroom", name="YATAK ODASI"))


def test_a_plan_at_a_detail_scale_or_named_details_is_a_detail_drawing():
    """real17: the 'DETAYLAR' sheet with its 'PLAN 1:20' of a window and a door was read as the 1st floor."""
    from wenart.sheets import titles as T

    assert T.class_of("PLAN 1:20")[0] == "detail" and T.class_of("DETAYLAR")[0] == "detail"
    assert T.class_of("BASAMAK DETAYI (ÖLÇEK 1/5)")[0] == "detail"
    assert T.class_of("PLAN 1/50")[0] == "floor_plan" and T.class_of("NORMAL KAT PLANI 1/100")[0] == "floor_plan"


def test_a_title_listing_its_floors_stands_for_those_floors():
    """real17: '1.2. NORMAL KAT PLANI' was read as the 2nd floor only."""
    from wenart.sheets.levels import level_of

    assert level_of("1.2. NORMAL KAT PLANI").orders == (1, 2)
    assert level_of("2-3-4. KAT PLANI").orders == (2, 3, 4)
    assert level_of("1-3 NORMAL KAT").orders == (1, 2, 3)
    lw = level_of("3. NORMAL KAT PLANI")
    assert lw.order == 3 and not lw.typical and lw.orders == ()
    assert level_of("NORMAL KAT PLANI").orders == () and level_of("2.BODRUM KAT PLANI").order == -2


def test_a_notation_layer_is_never_a_wall_layer():
    from wenart.ingest.generic import layer_names as LN
    from wenart.ingest.generic import walls as W

    assert LN.layer_role("YAZILAR") in W.NOTATION_ROLES and LN.layer_role("OLCULER") in W.NOTATION_ROLES
    assert LN.layer_role("DUVAR") not in W.NOTATION_ROLES


def test_a_ground_mark_on_the_line_puts_the_ground_in_the_storey_marks_frame():
    """real10 (user: "is there a reason for the elevations in real10?"): the slab bands mapped the levels one storey off;
    the ground line drawn at the 1st basement's floor read -6.00 m and was not used. The section's '-0.50' mark (0.144 m
    above the line, like all its marks) with the ground floor's '+2.50' puts it at -3.00 m."""
    from wenart.sheets import heights as H

    out = {"levels": [], "slabs": [], "ground": [{"side": "all", "z": {"value": -6.0, "method": "vector"}}],
           "_mark_frame": [(-0.5, -5.856), (2.5, -2.856), (5.5, 0.144), (8.5, 3.144)]}
    levels = [{"id": "L-1", "order": -1}, {"id": "L0", "order": 0}, {"id": "L1", "order": 1}]
    H.apply_storey_marks(out, levels, {-1: -0.5, 0: 2.5, 1: 5.5}, 0.2, "x.dwg", "r1")
    assert out["ground"][0]["z"]["value"] == -3.0 and "_mark_frame" not in out
    assert H._frame_shift([(2.5, -2.856), (5.5, 0.144)], 2.5) == 2.856 and H._frame_shift([], 0.0) is None


def test_an_open_roof_terrace_edge_gets_a_parapet():
    """real10 (user: "putting a bit parapet would be nice so people on the last floor can walk safely")."""
    from wenart.sheets import to_building as TB

    def wall(wid, lv, a, c, t=0.25):
        return {"id": wid, "level_id": lv, "start": list(a), "end": list(c), "thickness": t, "exterior": True}

    sq = [(0, 0), (10, 0), (10, 8), (0, 8)]
    b = {"levels": [{"id": "L0", "order": 0}, {"id": "L1", "order": 1, "roof_terrace": True}],
         "walls": [wall(f"w{k}", "L0", sq[k], sq[(k + 1) % 4]) for k in range(4)]
         + [wall("p1", "L1", (3, 0), (6, 0), 0.2)]}
    n = TB._edge_parapets(b, b["levels"][1], 0.9, "section mark")
    new = [w for w in b["walls"] if "edge_parapet" in w["id"]]
    # user: "Too much wall on top a little wall with handrails should have been enough"
    assert n == len(new) >= 4 and all(w["parapet"] and w["height"] == 0.5 and w["level_id"] == "L1"
                                      and w["guard"]["top_m"] == 1.1 for w in new)
    import math
    total = sum(math.dist(w["start"], w["end"]) for w in new)
    assert 30.0 < total < 36.0                        # the 36 m edge less the drawn 3 m piece and its reach


def test_a_code_typed_gap_is_typed_the_same_on_every_floor_of_its_plan():
    """real10 (user: "Why there is not window here"): the bedroom window was a window on L0 only."""
    from wenart.blender import architect_actions as AA

    def gap(oid, lv):
        return {"id": oid, "level_id": lv, "type": "opening", "type_raw": "unclassified gap content",
                "center": [8.59, 17.99], "width": 1.5}

    o = dict(gap("o_L0_016", "L0"), type="window", sill_height=0.9, height=1.2)
    b = {"levels": [{"id": "L0", "region_id": "r8"}, {"id": "L1", "region_id": "r8"}, {"id": "L-1", "region_id": "r7"}],
         "openings": [o, gap("o_L1_016", "L1"), gap("o_L-1_016", "L-1")]}
    out = AA._same_on_typical_floors(b, o, "reason")
    assert len(out) == 1 and b["openings"][1]["type"] == "window" and b["openings"][2]["type"] == "opening"


def test_a_shared_hall_is_a_common_area_never_furnished():
    """real10 (user: "here 26 is not a living area, this is common use area ... flooring roofing and any furniture
    should be different, this is a general rule")."""
    from wenart import common_areas as CA
    from wenart.furniture import decor as DC

    hall = {"id": "r_L1_oda_5_hall", "label": "Kat Holü", "room_type": "hall", "status": "verified",
            "label_inferred": {"method": "shared_hall"}}
    antre = {"id": "r_L1_antre", "label": "Antre", "room_type": "hall", "status": "verified"}
    assert CA.is_common_room(hall) and CA.is_common_room({"label": "BİNA GİRİŞİ"}) and not CA.is_common_room(antre)
    assert CA.is_common_room({"label": "x", "room_subtype": "common"})
    assert not DC.room_takes_decor(hall) and DC.room_takes_decor(antre)
    assert CA.COMMON_FLOOR["material"] != "" and CA.COMMON_WALLS["colour"] == "greige"


def test_a_lift_shaft_gets_a_sliding_landing_door():
    """real10 (user: "here is for the elevator (asansor) there should be a door for the elevator like sliding door")."""
    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": "L1", "label": label, "room_type": rtype, "polygon": poly}

    shaft = room("r_L1_asansor", "Asansör", "shaft", [[0, 0], [1.6, 0], [1.6, 1.8], [0, 1.8]])
    hall = room("r_L1_hall", "Kat Holü", "hall", [[0, 2.0], [4, 2.0], [4, 4], [0, 4]])
    hall["label_inferred"] = {"method": "shared_hall"}
    walls = [{"id": "w1", "level_id": "L1", "start": [-0.1, 1.9], "end": [4.1, 1.9], "thickness": 0.2}]
    openings: list = []
    notes = TW.lift_doors([shaft, hall], openings, walls)
    assert len(openings) == 1 and openings[0]["operation"] == "sliding" and openings[0]["wall_id"] == "w1"
    assert openings[0]["type"] == "door" and abs(openings[0]["center"][1] - 1.9) < 1e-6 and notes
    # a drawn door in the shaft's wall is that door, made sliding; a machine room is no shaft
    drawn = [{"id": "d1", "level_id": "L1", "type": "opening", "center": [0.8, 1.9], "width": 0.9}]
    TW.lift_doors([shaft, hall], drawn, walls)
    assert drawn[0]["type"] == "door" and drawn[0]["operation"] == "sliding" and len(drawn) == 1
    machine = dict(shaft, id="m", label="Asansör Mahali")
    none: list = []
    TW.lift_doors([machine, hall], none, walls)
    assert none == []


def test_a_numbered_stair_whose_end_number_stands_on_the_landing_keeps_both_arms():
    """real10's fire escape stair (user: "There should have been fire escape ladders here"): its number 16 stands by the
    arrow, off the right arm's line; the run back from it turned at once and the stair was not read."""
    from wenart.ingest.generic import stair_numbers as SN

    pts = [(0.0, 0.0), (-0.007, -0.189), (-0.007, -0.399), (-0.011, -0.597), (0.0, -0.814), (0.065, -0.98),
           (0.212, -1.122), (0.376, -1.171), (0.556, -1.16), (0.451, -0.975), (0.867, -0.872), (0.873, -0.664),
           (0.871, -0.468), (0.874, -0.27), (0.872, -0.068), (1.016, 0.144)]
    arms = SN._arms(pts)
    assert len(arms) == 2 and arms[0][:5] == [0, 1, 2, 3, 4] and arms[1] == [10, 11, 12, 13, 14]
    straight = [(0.0, 0.25 * k) for k in range(8)]
    assert SN._arms(straight) == [list(range(8))]


def test_a_second_stair_off_the_common_hall_is_a_fire_escape_stair():
    """real10 (user: "Fire stairs should be like fire stairs not like regular stairs")."""
    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly, **kw):
        return dict({"id": rid, "level_id": "L1", "label": label, "room_type": rtype, "polygon": poly}, **kw)

    rooms = [room("lift", "Asansör", "shaft", [[0, 0], [1.6, 0], [1.6, 1.6], [0, 1.6]]),
             room("core", "Merdiven", "stair", [[1.8, 0], [4.5, 0], [4.5, 2.5], [1.8, 2.5]],
                  label_inferred={"method": "stair_core"}),
             room("hall", "Kat Holü", "hall", [[0, 2.7], [4.5, 2.7], [4.5, 4.5], [0, 4.5]],
                  label_inferred={"method": "shared_hall"}),
             room("fire", "Merdiven", "stair", [[1.0, 6.0], [3.0, 6.0], [3.0, 9.0], [1.0, 9.0]],
                  label_inferred={"method": "stair_core"}),
             room("kitchen", "Mutfak", "kitchen", [[3.2, 6.0], [6.0, 6.0], [6.0, 9.0], [3.2, 9.0]])]
    stairs = [{"id": "s1", "level_id": "L1", "type": "stair", "footprint": {"center": [3.1, 1.2], "size": [2.7, 2.3]}},
              {"id": "s2", "level_id": "L1", "type": "stair", "footprint": {"center": [2.0, 7.5], "size": [1.7, 2.8]}}]
    window_gap = [{"id": "o1", "level_id": "L1", "type": "opening", "center": [3.1, 7.0], "width": 0.64}]
    notes = TW.fire_stairs(rooms, window_gap, stairs)
    assert len(notes) == 1 and stairs[1]["details"]["stair"]["fire_escape"] and "details" not in stairs[0]
    assert rooms[3]["room_subtype"] == "common"
    # a stair with a door into a flat's room is that flat's own stair
    stairs[1].pop("details")
    door = [{"id": "d1", "level_id": "L1", "type": "door", "center": [3.1, 7.0], "width": 0.8}]
    assert TW.fire_stairs(rooms, door, stairs) == []


def test_a_floor_band_runs_on_a_straightened_outline():
    """real10 (user: "Make these details better", the floor bands): jogs of a few cm and notches under 0.2 m are
    straightened onto the outer line; a real recess stays."""
    from wenart.blender import facade as F

    o = [[0, 0], [10, 0], [10, 5], [10.03, 5], [10.03, 9], [6, 9], [6, 6], [4.2, 6], [4.2, 9], [0.06, 9], [0.06, 5],
         [0, 5]]
    clean = F.band_outline(o)
    assert len(clean) == 8 and [10.03, 0.0] in clean and [4.2, 6.0] in clean
    boxes = F._band_boxes(clean, 2.9, 3.1, 0.03, [], "band", "L1", inset=0.1)
    assert all(abs(b["size"][1] - 0.13) < 1e-9 for b in boxes)
    assert F.band_outline([[0, 0], [5, 0], [5, 4], [0, 4]]) == [[5.0, -0.0], [5.0, 4.0], [0.0, 4.0], [0.0, -0.0]] or \
        len(F.band_outline([[0, 0], [5, 0], [5, 4], [0, 4]])) == 4


def test_a_wall_item_with_no_ceiling_read_over_it_takes_the_level_ceiling(monkeypatch):
    """real07 structure run 20261104-120732-full: a WC's fluted panel got a height of -0.22 m (no ceiling read over its
    spot), the building JSON failed its schema and the run stopped."""
    from wenart.furniture import bath_details as BD

    class D:
        @staticmethod
        def ceiling_over(*a, **k):
            return 0.0
    monkeypatch.setattr(BD, "_decor_module", lambda: D)
    monkeypatch.setattr(BD, "_ceiling", lambda building, room: 2.6)
    assert BD.ceiling_at({}, {"level_id": "L0"}, (0, 0), (0.5, 0.02), 0.0) == 2.6
    assert BD.FEATURE_PANEL_MIN_H_M > 0


def test_a_common_area_room_subtype_is_valid_in_the_schema():
    """real10 structure run 20261104-122252-full: the fire stair's room_subtype 'common' failed the building schema, the
    reading needed review and nothing was built."""
    import json
    from pathlib import Path

    s = json.loads((Path(__file__).resolve().parents[1] / "wenart" / "schema" / "building.schema.json").read_text())
    assert "common" in s["$defs"]["room"]["properties"]["room_subtype"]["enum"]


def test_storey_marks_that_do_not_rise_with_the_storeys_are_no_storey_frame():
    """real07: the section named the ground floor and the 1st floor at the same mark -34.23; L1 stood on L0 and L0's
    walls were -0.20 m high."""
    from wenart.sheets import heights as H

    out = {"levels": [{"level_id": "L0", "floor_z": {"value": 0.0}}], "slabs": [], "ground": []}
    levels = [{"id": "L0", "order": 0}, {"id": "L1", "order": 1}]
    lines = H.apply_storey_marks(out, levels, {0: -34.23, 1: -34.23}, 0.2, "x.dwg", "r1")
    assert lines and "do not rise" in lines[0] and out["levels"][0]["floor_z"]["value"] == 0.0
    ok = H.apply_storey_marks({"levels": [], "slabs": [], "ground": []}, levels, {0: 0.0, 1: 3.0}, 0.2, "x", "r1")
    assert ok and "heights from the storeys" in ok[0]


def test_section_heights_outside_a_storey_are_implausible():
    """real07: the section's slab bands put L1 35.66 m over L0 (a 35.46 m ceiling): such heights are no storeys."""
    from wenart.sheets import heights as H

    levels = [{"id": "L0", "order": 0}, {"id": "L1", "order": 1}]
    v = lambda x: {"value": x, "method": "vector"}
    bad = {"levels": [{"level_id": "L0", "floor_z": v(0.0), "ceiling_height": v(35.46)},
                      {"level_id": "L1", "floor_z": v(35.66), "ceiling_height": v(2.7)}]}
    assert "ceiling" in H.implausible(bad, levels)
    step = {"levels": [{"level_id": "L0", "floor_z": v(0.0), "ceiling_height": v(2.7)},
                       {"level_id": "L1", "floor_z": v(0.4), "ceiling_height": v(2.7)}]}
    assert "L0 -> L1" in H.implausible(step, levels)
    ok = {"levels": [{"level_id": "L0", "floor_z": v(0.0), "ceiling_height": v(2.7)},
                     {"level_id": "L1", "floor_z": v(3.0), "ceiling_height": v(2.7)}]}
    assert H.implausible(ok, levels) is None


def _room(walls_xy, label=("SALON", 2.5, 2.0)):
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.generic.model import TextRun
    from wenart.ingest.model import WallItem

    walls = [WallItem(start=a, end=b, thickness=0.2, box=[0, 0, 1, 1], entity=f"LINE:{k}", evidence={})
             for k, (a, b) in enumerate(walls_xy)]
    name, x, y = label
    blocks = LB.merge_label_blocks([TextRun(id="T1", text=name, box=(x - 0.4, y - 0.1, x + 0.4, y + 0.1),
                                            height=0.2)], "x.dxf", 1)
    bw, site, sw = TP.split_plot(walls, [], blocks, level_id="L0")
    return walls, blocks, sw, TP.outer_loop_problem(bw, [])


def test_a_drawn_wall_stopping_short_of_a_shared_corner_is_joined_to_it():
    """real17 L0: the 4.70 m shopfront and the facade wall both stopped about 0.5 m short of their corner column."""
    from wenart.ingest.generic import core as C

    walls, blocks, sw, prob = _room([((0.5, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)), ((5.0, 4.0), (0.0, 4.0)),
                                     ((0.0, 4.0), (0.0, 0.45))])
    assert C._unclosed(sw) or prob
    ex = SimpleNamespace(notes=[])
    got = C._short_joins(ex, "x", walls, [], blocks, "L0", sw, prob)
    assert got is not None and got[6] is None and not C._unclosed(got[4])
    assert len(got[0]) == 4 and "shared corner" in ex.notes[0]          # no wall added, two lengthened


def test_a_wide_gap_between_drawn_walls_is_never_joined():
    """'There are no walls here why are you imagining these?': an open 1.2 m front stays open."""
    from wenart.ingest.generic import core as C

    walls, blocks, sw, prob = _room([((1.2, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)), ((5.0, 4.0), (0.0, 4.0)),
                                     ((0.0, 4.0), (0.0, 0.0))])
    assert C._short_joins(SimpleNamespace(notes=[]), "x", walls, [], blocks, "L0", sw, prob) is None


def test_a_crack_between_two_drawn_walls_at_a_wall_end_is_filled():
    """real17 L0: a stair wall's corner 9 mm off the facade wall's corner left the shop open to the street."""
    from wenart.ingest.generic import core as C

    walls, blocks, sw, prob = _room([((0.0, 0.0), (5.0, 0.0)), ((0.0, 0.0), (0.0, 2.1)), ((0.0, 2.1), (4.892, 2.1)),
                                     ((5.0, 0.0), (5.0, 1.996))], label=("SALON", 2.5, 1.0))
    walls[3].thickness = 0.21                                  # its top-left corner 5 mm off the top wall's corner
    from wenart.ingest.generic import topology as TP
    bw, site, sw = TP.split_plot(walls, [], blocks, level_id="L0")
    prob = TP.outer_loop_problem(bw, [])
    assert C._unclosed(sw) or prob
    ex = SimpleNamespace(notes=[])
    got = C._short_joins(ex, "x", walls, [], blocks, "L0", sw, prob)
    assert got is not None and not C._unclosed(got[4])
    assert any(w.entity.startswith("joint:") and w.inferred for w in got[0])


def test_shop_entrance_and_buried_tank_labels_outside_never_leave_a_level_out():
    from wenart import building as B
    from wenart.ingest import pipeline as PL

    for t in ("DÜKKAN GİRİŞİ", "BİNA GİRİŞİ", "MAIN ENTRANCE"):
        assert PL.ENTRANCE_WORD_RE.search(" ".join(B.fold_ascii(t).upper().split()))
    assert PL.BURIED_WORD_RE.search(B.fold_ascii("TABİ ZEMİNE GÖMÜLÜ SU DEPOSU").upper())
    assert not PL.ENTRANCE_WORD_RE.search("DUKKAN") and not PL.BURIED_WORD_RE.search("SU DEPOSU")


def test_the_source_drawing_panel_leaves_out_the_grid_and_the_dimensions():
    """User: 'on the top left one marked, remove the coordinate and measurement lines'."""
    from wenart.reading_check import sheets as SH

    assert SH.is_grid_or_dimension("DIMENSION", "DUVAR", "CONTINUOUS")
    assert SH.is_grid_or_dimension("LINE", "AKS", "CONTINUOUS")
    assert SH.is_grid_or_dimension("TEXT", "AKS YAZISI", "CONTINUOUS")
    assert SH.is_grid_or_dimension("LINE", "OLCU", "CONTINUOUS")
    assert SH.is_grid_or_dimension("LINE", "Standart", "CENTER2")
    assert not SH.is_grid_or_dimension("LINE", "DUVAR", "CONTINUOUS")
    assert not SH.is_grid_or_dimension("LINE", "pencere", "HIDDEN")


def test_a_self_touching_room_face_is_split_into_its_spaces():
    """real17 L3: two spaces whose corners touch at one point came as one self-touching ring."""
    from shapely.geometry import Polygon

    from wenart.ingest import rooms as R
    from wenart.ingest.model import WallItem

    shell = [(-1, -1), (5, -1), (5, 5), (-1, 5)]
    hole = [(0, 0), (2, 0), (2, 2), (4, 2), (4, 4), (2, 4), (2, 2), (0, 2)]
    union = Polygon(shell, [hole])
    walls = [WallItem(start=(-0.5, -0.5), end=(4.5, -0.5), thickness=1.0, box=[0, 0, 1, 1], entity="LINE:1",
                      evidence={})]
    res = R.derive_rooms("L0", walls, [], [], union=union)
    polys = [Polygon(r["polygon"]) for r in res.rooms]
    assert len(polys) == 2 and all(q.is_valid and abs(q.area - 4.0) < 1e-6 for q in polys)


def test_a_window_size_tag_sets_its_window():
    """real17 L0 (user: "these sections could be full windows glass"): '200/240' on the window text layer beside a facade
    is one 2.00 m window, 2.40 m high from the floor, in place of the two small windows read from its frame; it moves
    off the column it would overlap; '100/50' is a high window."""
    from wenart.ingest.generic import core as C
    from wenart.ingest.generic.model import TextRun
    from wenart.ingest.model import OpeningItem, WallItem

    def wall(a, b, t=0.2, e="LINE:1"):
        return WallItem(start=a, end=b, thickness=t, box=[0, 0, 1, 1], entity=e, evidence={})

    def win(x, w=0.44):
        return OpeningItem(kind="window", width=w, center=(x, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1],
                           entity=f"w{x}", evidence={})

    walls = [wall((0.0, 0.0), (8.0, 0.0)), wall((4.0, 0.0), (4.4, 0.0), t=0.4, e="INSERT:col")]   # a column
    tags = [TextRun(id="T1", text="200/240", box=(2.6, -0.45, 3.6, -0.3), height=0.15,
                    evidence=[{"layer": "penc-yazi"}]),
            TextRun(id="T2", text="100/50", box=(6.0, -0.45, 6.8, -0.3), height=0.15,
                    evidence=[{"layer": "PENCERE"}]),
            TextRun(id="T3", text="100/210", box=(0.5, -0.45, 1.3, -0.3), height=0.15,
                    evidence=[{"layer": "kapi-yazi"}])]              # a door tag: not a window
    ex = SimpleNamespace(notes=[])
    got = C._window_tags(ex, "x", walls, [win(2.5), win(3.4)], tags, 1.0)
    w = sorted([o for o in got if o.kind == "window"], key=lambda o: o.center[0])
    assert len(w) == 2
    assert abs(w[0].width - 2.0) < 1e-6 and w[0].height == 2.4 and w[0].sill == 0.0
    assert w[0].center[0] + w[0].width / 2.0 <= 4.0 + 1e-6                 # clear of the column
    assert abs(w[1].width - 1.0) < 1e-6 and abs(w[1].sill - 1.7) < 1e-6 and "sill_height" in w[1].assumed


def test_grid_bubbles_and_dimension_dots_on_layer_0_are_left_out_of_the_source_panel():
    """real10: the bubbles, dimension dots and ticks sit on layer '0'; a round column on a grid line and the furniture
    stay."""
    from wenart.reading_check import sheets as SH

    doc = ezdxf.new()
    msp = doc.modelspace()
    for name in ("AKS", "DIMH", "TEFRIS"):
        doc.layers.add(name)
    msp.add_line((0, 0), (10, 0), dxfattribs={"layer": "AKS"})
    bubble = msp.add_circle((10.5, 0), 0.5, dxfattribs={"layer": "0"})
    column = msp.add_circle((5, 0), 0.3, dxfattribs={"layer": "0"})
    msp.add_line((0, -3), (4, -3), dxfattribs={"layer": "DIMH"})
    msp.add_text("400", height=0.2, dxfattribs={"layer": "DIMH", "insert": (2, -2.8)})
    dot = msp.add_circle((4.0, -3.05), 0.04, dxfattribs={"layer": "0"})
    tick = msp.add_line((-0.1, -3.1), (0.1, -2.9), dxfattribs={"layer": "0"})
    chair = msp.add_circle((4.0, -3.0), 0.1, dxfattribs={"layer": "TEFRIS"})
    wall = msp.add_line((0, -3.2), (0, 5), dxfattribs={"layer": "0"})
    hidden = SH.grid_and_dimension_marks(doc, list(msp))
    assert {id(bubble), id(dot), id(tick)} <= hidden
    assert not {id(column), id(chair), id(wall)} & hidden


def test_a_stair_arriving_from_below_under_a_room_cuts_no_hole_above():
    """real17: the shops' stairs go down to their basement stores; the first floor's bedrooms over them got holes."""
    from wenart.sheets import to_building as TB

    def stair(level, x=2.0):
        return {"id": f"f_{level}", "level_id": level, "type": "stair",
                "footprint": {"center": [x, 1.0], "size": [3.0, 1.4], "rotation_deg": 0.0}}

    room = {"id": "r_L1_oda", "level_id": "L1", "label": "Oda", "room_type": "bedroom",
            "polygon": [[0, -1], [5, -1], [5, 3], [0, 3]]}
    f = stair("L0")
    assert TB.arrival_only(f, "L-1", "L1", [stair("L-1"), f], [room])
    assert not TB.arrival_only(f, "L-1", "L1", [stair("L-1"), f, stair("L1")], [room])   # it goes on up
    assert not TB.arrival_only(f, "L-1", "L1", [f], [room])                               # it starts here
    assert not TB.arrival_only(f, "L-1", "L1", [stair("L-1"), f], [])                    # nothing drawn above


def test_a_wall_outside_the_roof_keeps_its_own_height():
    """real10 (user: "Too much wall on top"): the terrace parapets were raised to the stair house's roof."""
    from wenart.blender import shell as SH

    cut = {"outline": [[7, 6], [14, 6], [14, 11], [7, 11]]}
    assert SH.outside_roof({"start": [0, 0], "end": [5, 0]}, cut)
    assert not SH.outside_roof({"start": [8, 7], "end": [12, 7]}, cut)
    assert not SH.outside_roof({"start": [0, 0], "end": [5, 0]}, {"outline": None})


def test_a_wall_drawn_outside_an_upper_floor_is_no_garden_wall():
    """real10 (user: "What are these white thing on the ground"): the AC boxes beside the typical floor's balconies
    stood on the ground as 1.2 m white walls."""
    from wenart.blender import site as ST

    terrain = {"kind": "flat", "z": {"+x": -3.0, "-x": -3.0, "+y": -3.0, "-y": -3.0}}
    levels = [{"id": "L-1", "elevation": -3.0}, {"id": "L0", "elevation": 0.0}]
    up = {"id": "sw_L0_005", "level_id": "L0", "start": [4.39, 18.1], "end": [5.51, 18.1]}
    low = dict(up, id="sw_L-1_001", level_id="L-1")
    outline = [[0, 0], [20, 0], [20, 18], [0, 18]]
    assert "facade" in ST.upper_floor_wall(up, levels, terrain, outline)
    assert ST.upper_floor_wall(low, levels, terrain, outline) is None
    far = dict(up, start=[4.39, 25.0], end=[5.51, 25.0])            # a garden wall away from the house
    assert ST.upper_floor_wall(far, levels, terrain, outline) is None
    assert ST.upper_floor_wall(dict(up, kind="plot"), levels, terrain, outline) is None


def test_a_door_from_the_common_hall_into_a_flat_is_the_flats_entrance_door():
    """real10 (user: "the Doors to this place from the actual living areas needs to be outside doors, kinda doors you
    can use to enter to the flat")."""
    from wenart.ingest import twins as TW

    hall = {"id": "r_L1_kat_holu", "level_id": "L1", "label": "Kat Holü", "room_type": "hall",
            "polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]}
    antre = {"id": "r_L1_antre", "level_id": "L1", "label": "Antre", "room_type": "hall",
             "polygon": [[3, 0], [6, 0], [6, 2], [3, 2]]}
    lift = {"id": "r_L1_asansor", "level_id": "L1", "label": "Asansör", "room_type": "shaft",
            "polygon": [[0, 2], [2, 2], [2, 4], [0, 4]]}
    d1 = {"id": "d1", "level_id": "L1", "type": "door", "center": [3.0, 1.0], "width": 1.0}
    d2 = {"id": "d2", "level_id": "L1", "type": "door", "center": [1.0, 2.0], "width": 0.9}    # into the lift
    d3 = {"id": "d3", "level_id": "L1", "type": "door", "center": [4.5, 0.0], "width": 0.9}    # the flat's own door
    notes = TW.flat_entrance_doors([hall, antre, lift], [d1, d2, d3])
    assert d1["door_style"] == "entrance" and d1["flat_entrance"] and len(notes) == 1
    assert "door_style" not in d2 and "door_style" not in d3


def test_the_common_hall_has_finishes_no_flat_uses():
    """real10 (user: "needs to have unique flooring and ceiling and walls")."""
    from wenart import common_areas as CA
    from wenart.style import finishes as F

    for slot in (CA.COMMON_FLOOR, CA.COMMON_WALLS, CA.COMMON_CEILING):
        assert slot["material"] in F.MATERIALS
    assert len({CA.COMMON_FLOOR["material"], CA.COMMON_WALLS["material"], CA.COMMON_CEILING["material"]}) == 3


def test_floor_bands_die_into_pilasters():
    """real10 (user: "all these details on the outside of the building is not good enough ... All details must be a
    lot better"): the band wrapped every pilaster in short pieces (knots)."""
    from wenart.blender import facade as F

    outline = [(0, 0), (4, 0), (4, -0.3), (4.5, -0.3), (4.5, 0), (10, 0), (10, 8), (0, 8)]
    assert F.pier_edges(outline) == {1, 2, 3}
    wrap = F._band_boxes(outline, 2.9, 3.1, 0.03, [], "band", "L1")
    clean = F._band_boxes(outline, 2.9, 3.1, 0.03, [], "band", "L1", piers=True)
    assert len(wrap) == 8 and len(clean) == 5
    assert all(b["size"][0] > 1.0 for b in clean)


def test_a_flat_roof_has_a_flat_covering_and_a_metal_fascia():
    """real07 (user: "I did not like these outside details, give some more modern details"): the flat roof's tile
    edge read as a dentil course."""
    from wenart.blender import build as BU

    cov, fascia, note = BU.roof_slot_looks({"type": "flat"}, {"roof": {"material": "concrete_tiles"}})
    assert cov["material"] == "gravel" and fascia["material"] == "aluminium_anthracite" and note
    cov, fascia, _ = BU.roof_slot_looks({"type": "flat"}, {"roof": {"material": "green_roof"}})
    assert cov["material"] == "green_roof"
    cov, _, _ = BU.roof_slot_looks({"type": "hip"}, {"roof": {"material": "concrete_tiles"}})
    assert cov["material"] == "concrete_tiles"


def test_a_garage_gets_its_sectional_garage_door():
    """real07 (user: "If this is a garage (garaj) there will be a car inside ... it requires a garage door")."""
    from wenart import building as B
    from wenart.ingest import twins as TW

    assert B.normalise_room_label("GARAJ")[1] == "garage" and B.normalise_room_label("KAT KAL.")[1] == "technical"
    room = {"id": "r_L0_garaj", "level_id": "L0", "room_type": "garage", "polygon": [[0, 0], [3.5, 0], [3.5, 6.5],
                                                                                     [0, 6.5]]}
    walls = [{"id": "w1", "level_id": "L0", "exterior": True}]
    gap = {"id": "o1", "level_id": "L0", "type": "window", "width": 3.0, "center": [1.75, 0.0], "wall_id": "w1",
           "height": 1.2}
    small = {"id": "o2", "level_id": "L0", "type": "window", "width": 1.0, "center": [0.0, 3.0], "wall_id": "w1"}
    notes = TW.garage_doors([room], [gap, small], walls)
    assert notes and gap["type"] == "door" and gap["door_type"] == "garage_sectional" and gap["height"] == 2.25
    assert small["type"] == "window"


def test_a_door_size_tag_makes_its_gap_a_door():
    """real07 (user: "where is the entrance to the bus wc you missed the door"): the 80/210 door read as a gap."""
    from wenart.ingest.generic import core as C
    from wenart.ingest.generic.model import TextRun
    from wenart.ingest.model import OpeningItem

    gap = OpeningItem(kind="opening", width=0.52, center=(2.0, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g",
                      evidence={}, type_raw="unclassified gap content")
    win = OpeningItem(kind="window", width=1.2, center=(6.0, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="w",
                      evidence={})
    tag = TextRun(id="T", text="80/210", box=(2.2, 0.2, 2.8, 0.35), height=0.12, rotation_deg=45.0,
                  evidence=[{"layer": "kapi-yazi"}])
    ex = SimpleNamespace(notes=[])
    got = C._door_tags(ex, "x", [], [gap, win], [tag], 1.0)
    assert got[0].kind == "door" and abs(got[0].width - 0.8) < 1e-6 and got[0].height == 2.1
    assert got[1].kind == "window"


def test_a_u_stairs_numbers_jump_the_landing_past_a_dimension_text():
    """real07 (user: "Stairs are missing in the project"): steps 1-9 on one arm, a wall-thickness text '10' beside
    step 9, the real 10-18 on the arm across the landing."""
    from wenart.ingest.generic import stair_numbers as SN

    def t(v, x, y):
        return SimpleNamespace(text=str(v), height=0.1, box=(x - 0.05, y - 0.05, x + 0.05, y + 0.05))

    lower = [t(k, 4.5 - 0.27 * (k - 1), 0.0) for k in range(1, 10)]          # 1 at x 4.5 ... 9 at x 2.34
    dim = [t(10, 2.1, 0.25)]                                                  # the wall-thickness text
    upper = [t(k, 2.34 + 0.27 * (k - 10), 2.4) for k in range(10, 19)]       # 10 ... 18 across the landing
    chain = SN.chains(lower + dim + upper)[0]
    assert [v for v, _p, _t in chain] == list(range(1, 19))


def test_an_open_chamfer_between_hall_and_living_room_gets_a_glazed_frame():
    """real10 (user: "This door frame must be angled and same needs to be on the other mirror side")."""
    from wenart.ingest import twins as TW

    hall = {"id": "r_hall", "level_id": "L0", "room_type": "hall", "polygon": [[2, 0], [6, 0], [6, 4], [2, 4], [0, 2]]}
    living = {"id": "r_liv", "level_id": "L0", "room_type": "living", "polygon": [[-4, -4], [2, -4], [2, 0], [0, 2],
                                                                                  [-4, 2]]}
    walls = [{"id": "w1", "level_id": "L0", "start": [-4, -4], "end": [6, -4], "thickness": 0.2}]
    sep = {"id": "o1", "level_id": "L0", "type": "opening", "virtual": True, "line": [[0, 2], [1, 1]]}
    notes = TW.chamfer_frames([hall, living], [sep], walls)
    assert notes and sep["type"] == "door" and sep["glazed"] and not sep["virtual"]
    assert any(w["id"].endswith("chamfer_01") for w in walls)


def test_the_top_down_cut_closes_wall_sections_never_the_floor_loop():
    """real07 (user: "2nd floor not modeled properly check it"): the L1 view showed a solid block."""
    from wenart.blender import topdown as TD

    class M:                                      # identity world matrix
        def __matmul__(self, co):
            return co

    class Obj:                                    # hashable like bmesh's verts and edges
        def __init__(self, **kw):
            self.__dict__.update(kw)

    def loop(pts, base):
        vs = [Obj(co=SimpleNamespace(x=x, y=y), index=base + k, link_edges=[]) for k, (x, y) in enumerate(pts)]
        es = []
        for k in range(len(vs)):
            e = Obj(verts=(vs[k], vs[(k + 1) % len(vs)]))
            es.append(e)
            vs[k].link_edges.append(e)
            vs[(k + 1) % len(vs)].link_edges.append(e)
        return es

    wall = loop([(0, 0), (10, 0), (10, 0.25), (0, 0.25)], 0)
    floor = loop([(0, 0), (12, 0), (12, 10), (0, 10)], 10)
    loops = TD._edge_loops(wall + floor)
    assert len(loops) == 2
    thick = sorted(TD._loop_thickness(lp, M()) for lp in loops)
    assert thick[0] <= TD.CAP_MAX_THICK_M < thick[1]


def test_a_doorless_opening_into_a_dressing_room_is_an_open_passage():
    """real07 (user: "there is no wall here and the section on the left ... is giyinme soyunma")."""
    from wenart.ingest import twins as TW

    dress = {"id": "r_d", "level_id": "L1", "label": "Giyinme-soyunma", "polygon": [[0, 0], [2, 0], [2, 4], [0, 4]]}
    bed = {"id": "r_b", "level_id": "L1", "label": "Yatak Od.", "polygon": [[2, 0], [6, 0], [6, 4], [2, 4]]}
    o = {"id": "o1", "level_id": "L1", "type": "opening", "center": [2.0, 0.6], "width": 0.8, "height": 2.1}
    notes = TW.open_passages([dress, bed], [o], [{"id": "L1", "ceiling_height": 2.7}])
    assert notes and o["height"] == 2.7 and o["open_passage"]
