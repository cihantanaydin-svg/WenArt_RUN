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
    assert n == len(new) >= 4 and all(w["parapet"] and w["height"] == 0.9 and w["level_id"] == "L1" for w in new)
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
