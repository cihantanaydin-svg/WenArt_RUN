"""real03 follow-up (10 Oct 2026): the flats of tekkat.dwg read, room types, misplaced fixed equipment, lighting.

The user saw only the core of real03 rendered. The flats were in the DWG all along: LibreDWG's dwg2dxf left blocks
out of the DXF (patched in the setup scripts), the flats are clipped block references (XCLIP), their walls are
closed outlines on the wall layer (one around the flat, one per room), the core walls are concrete (``MYD - BA``).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from shapely.geometry import Polygon

from wenart import building as B
from wenart.blender import lighting as LT
from wenart.blender import overrides as BO
from wenart.furniture import schemas
from wenart.ingest import dxf_generic as DG
from wenart.ingest import rooms as R
from wenart.ingest.generic import labels as LB
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import GenericPage, Stroke, TextRun

ROOT = Path(__file__).resolve().parents[1]


# --- LibreDWG patch ---------------------------------------------------------

@pytest.mark.parametrize("script", ["scripts/pod_setup_recognition.sh", "scripts/cloud-setup.sh"])
def test_libredwg_blocks_patch_is_applied_in_both_setups(script):
    text = (ROOT / script).read_text(encoding="utf-8")
    assert 'LIBREDWG_VERSION_STRING="0.14 d9468ae p1"' in text
    assert "patch_libredwg() {" in text and 'git -C "$LIBREDWG_SRC" apply' in text
    assert "int j = i;" in text and "dxf_block_write (dat, obj, mspace, pspace, &j);" in text
    # applied after the jsmn submodule, before cmake
    assert text.index("submodule update --init --depth 1 jsmn") < text.rindex("patch_libredwg ") < text.index("cmake -S")


# --- XCLIP --------------------------------------------------------------------

CLIP = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])


def _st(pts, closed=False, sid="INSERT:1/2/3"):
    return Stroke(id=sid, kind="polyline", pts=pts, closed=closed, layer="L")


def test_clip_keeps_inside_drops_outside_and_cuts_crossing_lines():
    inside = _st([(1, 1), (2, 2)])
    assert DG._clip_stroke(inside, CLIP) == [inside]
    assert DG._clip_stroke(_st([(11, 1), (12, 2)]), CLIP) == []
    cut = DG._clip_stroke(_st([(5, 5), (15, 5)]), CLIP)
    assert len(cut) == 1 and cut[0].pts == [(5.0, 5.0), (10.0, 5.0)] and not cut[0].closed


def test_clip_cuts_a_closed_outline_mostly_inside_and_drops_one_mostly_outside():
    outer = _st([(-10, 0), (10, 0), (10, 5), (-10, 5)], closed=True)          # half inside: cut
    pieces = DG._clip_stroke(outer, CLIP)
    assert len(pieces) == 1 and pieces[0].closed and Polygon(pieces[0].pts).area == pytest.approx(50.0)
    sliver = _st([(9.8, 0), (14, 0), (14, 4), (9.8, 4)], closed=True)        # 5 % inside: a hidden room
    assert DG._clip_stroke(sliver, CLIP) == []


# --- walls --------------------------------------------------------------------

def test_concrete_layers_are_wall_layers_only_as_the_last_word():
    for name in ("D BLOK_STA_NK$0$MYD - BA", "MYD - B-H", "xref|MYD - BA", "PERDE"):
        assert DG.is_wall_hint_layer(name), name
    for name in ("MYD - BANYO", "BALKON", "TABA", "MYD - TEXT"):
        assert not DG.is_wall_hint_layer(name), name


def _ring_page():
    # A flat drawn as an outline around it and one outline per room (wall layer, one block instance), metres.
    outer = [(0, 0), (6.2, 0), (6.2, 4.2), (0, 4.2)]
    room_a = [(0.1, 0.1), (3.0, 0.1), (3.0, 4.1), (0.1, 4.1)]
    room_b = [(3.1, 0.1), (6.1, 0.1), (6.1, 4.1), (3.1, 4.1)]
    strokes = [Stroke(id=f"INSERT:A/{k}/{j}", kind="polyline", pts=pts, closed=True, layer="X$0$MYD - DUVAR",
                      block="ZK/FLAT") for j, pts in enumerate((outer, room_a, room_b)) for k in (5,)]
    return GenericPage(file="f.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=1.0, size=(7, 5),
                       strokes=strokes, wall_hint_layers=("X$0$MYD - DUVAR",))


def test_ring_walls_fill_the_outlines_of_one_block_even_odd():
    page = _ring_page()
    prims = W._ring_walls(page, 1.0, set())
    assert len(prims) == 1 and prims[0].kind == "ring" and len(prims[0].polygons) == 3
    filled = Polygon(prims[0].polygons[0])
    for p in prims[0].polygons[1:]:
        filled = filled.symmetric_difference(Polygon(p))
    assert filled.area == pytest.approx(6.2 * 4.2 - 2.9 * 4.0 - 3.0 * 4.0)


def test_ring_walls_need_nested_outlines_of_wall_thickness():
    page = _ring_page()
    page.strokes = page.strokes[1:]                       # two rooms side by side, no outline around them
    assert W._ring_walls(page, 1.0, set()) == []


# --- labels and room types ------------------------------------------------------

def test_services_layer_texts_are_no_room_labels():
    ev = [{"layer": "xref_1+1_B_TEXT$0$____MEK_MEKANİK ÇALIŞMA"}]
    run = TextRun(id="t1", text="SUBSTATİON", box=(0, 0, 1, 0.2), height=0.2, evidence=ev)
    room = TextRun(id="t2", text="KAT HOLÜ", box=(0, 1, 1, 1.2), height=0.2, evidence=[{"layer": "MYD - TEXT"}])
    names = [b.name for b in LB.merge_label_blocks([run, room])]
    assert names == ["KAT HOLÜ"]
    assert not LB._services_text(TextRun(id="t3", text="SALON", box=(0, 0, 1, 1), height=0.2,
                                         evidence=[{"layer": "MYD - MEKAN"}]))


@pytest.mark.parametrize("label,expected", [
    ("YAŞAMA", "living"), ("KAT MERDİVENİ", "stair"), ("YANGIN MERDİVENİ", "stair"), ("Hava Bacası", "shaft"),
    ("Elektrik Şaftı", "shaft"), ("ODA-01", "bedroom"), ("ODA", "bedroom"), ("RÜZGARLIK", "hall"),
    ("GÜVENLİK HOLÜ", "hall"), ("YEMEK ODASI", "other"), ("EBEVEYN ODASI", "bedroom"), ("Staircase", "stair"),
])
def test_room_types_of_real03_labels(label, expected):
    assert B.room_type_for(label) == expected


def test_stair_and_shaft_rooms_are_never_furnished():
    for rtype in ("stair", "shaft"):
        assert rtype in B.ROOM_TYPES and rtype in schemas.NOT_FURNISHED_ROOM_TYPES


# --- topology -----------------------------------------------------------------

def test_a_free_standing_piece_inside_the_building_does_not_open_the_outer_loop():
    ring = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], [[(0.2, 0.2), (9.8, 0.2), (9.8, 9.8), (0.2, 9.8)]])
    stub = Polygon([(4, 4), (4.7, 4), (4.7, 4.1), (4, 4.1)])
    from shapely.ops import unary_union
    kept = R.drop_inner_pieces(unary_union([ring, stub]))
    assert kept.geom_type == "Polygon" and kept.area == pytest.approx(ring.area)


# --- misplaced fixed equipment -------------------------------------------------

def test_misplaced_fixed_equipment():
    assert schemas.misplaced_fixed("kitchen_counter", "stair")
    assert schemas.misplaced_fixed("toilet", "shaft")
    assert schemas.misplaced_fixed("stove", "bedroom")
    assert not schemas.misplaced_fixed("kitchen_counter", "living")      # an open kitchen
    assert not schemas.misplaced_fixed("stair", "stair")
    assert not schemas.misplaced_fixed("toilet", "bathroom")


def _misplaced_building():
    room = {"id": "r1", "level_id": "L0", "label": "Kat Merdiveni", "room_type": "stair",
            "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]], "status": "verified"}
    piece = {"id": "f1", "level_id": "L0", "room_id": "r1", "type": "kitchen_counter", "source": "from_documents",
             "footprint": {"center": [2.0, 0.4], "size": [2.4, 0.6], "rotation_deg": 0.0}, "front_deg": 90.0,
             "height": 0.9, "status": "unverified", "evidence": []}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [room], "walls": [],
            "openings": [], "furniture": [piece]}


def test_locked_check_accepts_the_agent_removing_misplaced_fixed_equipment():
    from wenart.furniture import locked
    src = _misplaced_building()
    fin = _misplaced_building()
    fin["furniture"][0].update(build=False, adjusted_by_ai={"reason": "stair flights read as a counter",
                                                           "changed": ["build"]})
    assert locked.check(src, fin, "complete") == []
    moved = _misplaced_building()
    moved["furniture"][0]["footprint"]["center"] = [2.5, 0.4]
    moved["furniture"][0].update(adjusted_by_ai={"reason": "x", "changed": ["footprint"]},
                                 drawn_footprint=src["furniture"][0]["footprint"])
    assert any("moved or resized" in p for p in locked.check(src, moved, "complete"))


# --- lighting -----------------------------------------------------------------

def test_a_long_corridor_gets_one_light_per_three_metres():
    corridor = [(0, 0), (20, 0), (20, 2), (0, 2)]
    plans = LT.area_light_plans(corridor)
    assert len(plans) == 7 and all(0.0 < p["center"][0] < 20.0 for p in plans)
    assert len(LT.area_light_plans([(0, 0), (4, 0), (4, 3), (0, 3)])) == 1
    power, per_m2 = LT.light_power(40.0, len(plans), dim=False)
    assert per_m2 == LT.AREA_LIGHT_W_PER_M2 and power == pytest.approx(480.0 / 7)
    stronger, _ = LT.light_power(40.0, len(plans), dim=False, factor=2.0)
    assert stronger == pytest.approx(2 * power)


def test_agent_lighting_override_is_read_within_its_range():
    b = {"agent_overrides": {"lighting": {"r1": {"factor": 2.0, "reason": "dark hall"},
                                          "r2": {"factor": 9.0, "reason": "too much"}}}}
    assert BO.lighting_of(b) == {"r1": {"factor": 2.0, "reason": "dark hall"}}
    assert BO.lighting_of({}) == {}


# --- pod run 1 (n6bh2aag0y2amy): layout debug drawing, drawn marks --------------------------------------------

def test_polygon_parts_of_odd_geometries():
    from shapely.geometry import MultiPolygon, box
    from wenart.furniture import placer
    assert placer.polygon_parts(None) == [] and placer.polygon_parts(Polygon()) == []
    assert len(placer.polygon_parts(MultiPolygon([box(0, 0, 1, 1), box(2, 2, 3, 3)]))) == 2
    assert placer.polygon_parts(box(0, 0, 1, 1))[0].area == 1.0


def test_small_or_thin_unknowns_that_fit_no_type_are_drawn_marks():
    from wenart.furniture import infer
    room = {"id": "r1", "level_id": "L0", "label": "Banyo", "room_type": "bathroom",
            "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]}

    def piece(pid, size):
        return {"id": pid, "level_id": "L0", "room_id": "r1", "type": "unknown", "source": "from_documents",
                "footprint": {"center": [1.0, 1.0], "size": size, "rotation_deg": 0.0}, "front_deg": None,
                "status": "unverified", "evidence": []}
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [room], "walls": [],
         "openings": [], "furniture": [piece("tap", [0.25, 0.12]), piece("line", [1.1, 0.1])]}
    props = {p["piece_id"]: p for p in infer.infer_types(b)}
    assert props["tap"]["type"] == "detail" and props["tap"]["build"] is False
    assert props["line"]["build"] is False and "thinner than" in props["line"]["reason"]


# --- pod run 2 (wxj7cj91tloewx): dark core rooms, the agent's time budget -----------------------------------------

def test_only_windows_in_outer_walls_bring_daylight():
    walls = {"w1": {"id": "w1", "exterior": True}, "w2": {"id": "w2", "exterior": False}}
    assert LT.daylight_window({"wall_id": "w1"}, walls, True)
    assert not LT.daylight_window({"wall_id": "w2"}, walls, True)       # glazing between the hall and the stair
    assert LT.daylight_window({"wall_id": "w2"}, walls, False)          # no exterior flags at all: as before


def test_the_final_estimate_without_polish_uses_its_own_factor():
    from wenart.run import stages as S
    with_polish = S.est_final(84, 4, polish=True)
    without = S.est_final(84, 4, polish=False)
    assert without / S.EST_FINAL_FACTOR_NO_POLISH * S.EST_FINAL_FACTOR > without
    assert without < with_polish and S.EST_FINAL_FACTOR_NO_POLISH < S.EST_FINAL_FACTOR


def test_overrides_of_another_building_are_not_replayed(tmp_path):
    import json as _json
    from wenart.agent import overrides as OV
    out = tmp_path / "p"
    (out / "orchestrator").mkdir(parents=True)
    (out / "building_decor.json").write_text(_json.dumps({"furniture": [], "rooms": []}), encoding="utf-8")
    ov = OV.Overrides(out, "p")
    ov.add(1, "set_material", {"slot": "walls", "look_id": "a", "reason": "r"}, {"accepted": True})
    assert len(ov.accepted()) == 1 and ov.stale() == []
    (out / "building_decor.json").write_text(_json.dumps({"furniture": [{"id": "x"}], "rooms": []}), encoding="utf-8")
    again = OV.Overrides(out, "p")
    assert again.accepted() == [] and len(again.stale()) == 1
    summary = OV.apply(out)
    assert summary["not_replayed"][0]["failed_checks"] == ["stale_source"]
