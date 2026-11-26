"""24 Nov 2026, render audit of the structure pod (the user: "real17 terrible results", "Renders have lots of mistakes";
docs/progress.md "24 Nov 2026, render audit of the structure pod"). One test per general class fixed, with the cases
that must not fire."""
from types import SimpleNamespace

import pytest

from wenart import building as B
from wenart.sheets import exterior as EX
from wenart.sheets import heights as H
from wenart.sheets import levels as LV


# --- class 1: section storey names in brackets and abbreviated (real17 '(1.BODRUM KAT)', '(3.NOR. KAT)') ---

@pytest.mark.parametrize("text,order,kind", [
    ("(ZEMİN KAT)", 0, "floor"), ("(1.BODRUM KAT)", -1, "basement"), ("(1.NOR. KAT)", 1, "floor"),
    ("(3.NOR. KAT)", 3, "floor"), ("2.NOR.KAT", 2, "floor"), ("ÇATI ARASI KATI", None, "attic"),
    ("ÇATI ARASI PLANI", None, "attic")])
def test_storey_names_in_brackets_and_abbreviated(text, order, kind):
    lw = LV.level_of(text)
    assert lw is not None and lw.order == order and lw.kind == kind and not lw.typical


def test_roof_space_label_titles_no_level():
    # review of f706c8a1 (real12: 'ÇATI ARASI' inside its sections became the title of an attic plan)
    assert LV.level_of("ÇATI ARASI") is None and LV.level_of("(ÇATI ARASI DÖŞEMESİ)") is None


def test_level_marks_in_brackets_still_left_out():
    # must not fire: real13's titles keep their bracketed level marks out of the words
    assert LV.level_of("1.(+5.20 KOTU) KAT PLANI").order == 1
    assert LV.level_of("ZEMİN (+2.50 KOTU)").order == 0
    assert LV.level_of("3.BODRUM (-5.50 KOTU)").order == -3
    assert LV.level_of("TERAS.(+13.30 KOTU) KAT PLANI").kind == "roof_terrace"
    assert LV.level_of("NOR. KAT PLANI").typical


def _text(s, y, x=0.0, h=0.2):
    return SimpleNamespace(text=s, point=(x, y), height=h, id=f"T:{s}")


def test_storey_elevations_fit_relative_marks_beside_absolute_ones():
    # real17's section: absolute levels (161.18 ...) printed beside the relative storey marks; the storey names sit
    # just under their marks (1 unit = 1 m)
    texts = []
    for v, name in ((-2.80, "(1.BODRUM KAT)"), (0.20, "(ZEMİN KAT)"), (3.50, "(1.NOR. KAT)"), (6.50, "(2.NOR. KAT)"),
                    (9.50, "(3.NOR. KAT)")):
        texts += [_text(f"{v:+.2f}", v + 0.1), _text(name, v - 0.15)]
    texts += [_text("161.18", 0.0, x=5.0), _text("160.64", 0.5, x=-5.0), _text("161.64", 0.5, x=8.0)]
    texts += [_text("+12.50", 12.6), _text("(ÇATI ARASI DÖŞEMESİ)", 12.35)]
    region = SimpleNamespace(texts=texts, strokes=lambda: [], id="r8")
    notes = []
    got = LV.storey_elevations([region], notes)
    assert got == {-1: -2.8, 0: 0.2, 1: 3.5, 2: 6.5, 3: 9.5, "top": 12.5}
    assert notes and "161.18" in notes[0] and "left out of the storey fit" in notes[0]


def test_named_roof_storey_outranks_a_roof_space_label():
    # review of f706c8a1 (real13: a roof-space label lower down took the roof storey's mark)
    texts = []
    for v, name in ((0.0, "ZEMİN KAT"), (3.0, "1.KAT"), (6.0, "2.KAT"), (9.0, "ÇATI KAT")):
        texts += [_text(f"{v:+.2f}", v + 0.1), _text(name, v - 0.15)]
    texts += [_text("+7.80", 7.9), _text("ÇATI ARASI DÖŞEMESİ", 7.65)]
    got = LV.storey_elevations([SimpleNamespace(texts=texts, strokes=lambda: [], id="r1")])
    assert got["top"] == 9.0


# --- class 1: a drawing frame is no outer wall and no slab band ---

def _ln(a, b, k):
    return H.Line(a, b, f"E{k}", f"E{k}#0")


def test_frame_lines_found_on_four_sides():
    box = (0.0, 0.0, 100.0, 140.0)
    lines = [_ln((0, 0), (0, 140), 1), (_ln((100, 0), (100, 140), 2)), _ln((0, 0), (100, 0), 3),
             _ln((0, 140), (100, 140), 4), _ln((1, 1), (1, 139), 5), _ln((20, 30), (20, 90), 6),
             _ln((20, 30), (80, 30), 7)]
    keys = H.frame_keys(lines, box)
    assert keys == {"E1#0", "E2#0", "E3#0", "E4#0", "E5#0"}


def test_tightly_cropped_section_is_no_frame():
    # must not fire (review of f706c8a1): the outer faces, raft and roof slab of a section cropped to the building
    # reach the box's edges and the section's own lines run into them
    box = (0.0, 0.0, 100.0, 140.0)
    lines = [_ln((0, 0), (0, 140), 1), _ln((100, 0), (100, 140), 2), _ln((0, 0), (100, 0), 3),
             _ln((0, 140), (100, 140), 4)]
    lines += [_ln((0, y), (100, y), 10 + y) for y in range(30, 130, 30)]                # slab lines into the walls
    lines += [_ln((30, 0), (30, 140), 9)]
    assert H.frame_keys(lines, box) == set()


def test_high_ground_line_is_no_terrain():
    out = {"levels": [{"level_id": "L0", "floor_z": {"value": 0.0}, "ceiling_height": {"value": 2.8}}],
           "ground": [{"side": "left", "z": {"value": 2.86, "lines": [{"z": 2.86, "entity": "L:1"},
                                                                       {"z": 0.04, "entity": "L:2"}]}},
                      {"side": "right", "z": {"value": -0.55, "lines": [{"z": -0.55, "entity": "L:3"}]}}]}
    lines = H.high_ground(out, [{"id": "L0", "order": 0}])
    assert out["ground"][0]["z"]["value"] == 0.04 and out["ground"][1]["z"]["value"] == -0.55 and len(lines) == 1
    # must not fire: a hillside where every line stands high keeps its upper line
    out["ground"][0]["z"] = {"value": 2.86, "lines": [{"z": 2.86, "entity": "L:1"}]}
    assert H.high_ground(out, [{"id": "L0", "order": 0}]) == [] and out["ground"][0]["z"]["value"] == 2.86


def test_storey_takes_the_slab_band_at_its_floor_mark_by_height():
    # review of f706c8a1 (real07: '4 slab bands for 2 plan levels' were mapped by order): bands are matched by height
    levels = [{"id": "L0", "order": 0}, {"id": "L1", "order": 1}]
    out = {"levels": [], "slabs": [{"between": [None, "L0"], "thickness": {"value": 0.3}},
                                   {"between": ["L0", "L1"], "thickness": {"value": 0.3}}],
           "_mark_frame": [(0.5, 0.0), (3.5, 3.0)],
           "_bands": [(-1.0, -0.6, "f0", "f1"), (-0.1, 0.0, "a", "b"), (2.75, 3.0, "c", "d"), (6.0, 6.1, "e", "f")]}
    lines = H.apply_storey_marks(out, levels, {0: 0.5, 1: 3.5, "top": 6.5}, 0.2, "x.dwg", "r5")
    by = {e["level_id"]: e for e in out["levels"]}
    ceil = by["L0"]["ceiling_height"]
    assert ceil["value"] == pytest.approx(2.75) and ceil["method"] == "vector"
    assert out["slabs"][0]["thickness"]["method"] == "assumed"                   # a 0.10 m band: a finish, no slab
    assert out["slabs"][1]["thickness"]["value"] == pytest.approx(0.25)
    assert any("not by order" in ln for ln in lines)


def test_no_frame_without_all_four_sides():
    # must not fire: a tightly cropped section (its walls reach the box's sides, nothing closes the top)
    box = (0.0, 0.0, 100.0, 140.0)
    lines = [_ln((0, 0), (0, 140), 1), _ln((100, 0), (100, 140), 2), _ln((0, 0), (100, 0), 3)]
    assert H.frame_keys(lines, box) == set()


# --- class 2: a roof profile of one pitch in pieces is a gable ---

def test_profile_of_one_pitch_in_pieces_is_gable():
    sec = SimpleNamespace(profile=[(-0.5, 12.3), (0.0, 12.5), (1.486, 13.094), (7.543, 15.517), (13.6, 13.094),
                                   (15.086, 12.5), (15.586, 12.3)], bands=[1], roof_lines=6)
    assert EX.roof_from_section(sec)[0] == "gable"


def test_profile_that_changes_pitch_is_gambrel():
    sec = SimpleNamespace(profile=[(0.0, 0.0), (1.0, 2.0), (4.0, 3.0), (7.0, 2.0), (8.0, 0.0)], bands=[1],
                          roof_lines=4)
    assert EX.roof_from_section(sec)[0] == "gambrel"


def test_hips_counted_at_convex_corners_only():
    # review of f706c8a1: the two valleys of a T cross gable end at reflex corners, a hip roof's hips at convex ones
    from shapely.geometry import Polygon
    t_plan = Polygon([(0, 0), (12, 0), (12, 4), (8, 4), (8, 10), (4, 10), (4, 4), (0, 4)])
    valleys = [((8, 4), (6, 2)), ((4, 4), (6, 2))]
    assert EX.convex_corner_hips(t_plan, valleys, 0.1) == 0
    box = Polygon([(0, 0), (10, 0), (10, 6), (0, 6)])
    hips = [((0, 0), (3, 3)), ((10, 0), (7, 3)), ((10, 6), (7, 3)), ((0, 6), (3, 3))]
    assert EX.convex_corner_hips(box, hips, 0.1) == 4


# --- class 1: an elevation reads its first mark in the datum's frame, not the first mark it prints ---

def test_elevation_takes_the_first_mark_in_the_datum_frame(monkeypatch):
    from wenart.sheets import units_check as UC
    texts = [_text("161.64", 10.0), _text("+0.20", 4.0)]
    region = SimpleNamespace(metres_per_unit=1.0, ents=[], texts=texts, geometry_box=(0, 0, 20, 20), id="r10",
                             sheet=SimpleNamespace(page=1),
                             file="x.dwg")
    monkeypatch.setattr(UC, "mark_point", lambda t, segs: (t.point[0], t.point[1], "apex"))
    z = EX.elevation_z(region, 0.2, None)
    assert z["method"] == "vector" and z["y_ref"] == 4.0 and z["z_ref"] == 0.0


# --- class 5: a kitchen floor hatch deeper than any counter or island is no counter run ---

def _segs(*ids):
    from types import SimpleNamespace as NS
    return [NS(stroke=NS(id=i)) for i in ids]


def test_over_deep_kitchen_hatch_is_no_counter():
    from wenart.ingest.generic import symbols as SY
    table, _ = SY.load_size_table()
    hatch, island = _segs("HATCH:FC33#0", "HATCH:FC33#1"), _segs("HATCH:AA#0")
    split = {"legs": [], "blocks": [((0.0, 0.0, 3.71, 2.12), hatch), ((0.0, 3.0, 2.4, 4.0), island)]}
    got = SY.no_counter_outlines(split, table)
    assert list(got) == [id(hatch)] and got[id(hatch)] == (["HATCH:FC33"], (2.12, 3.71))


def test_deep_peninsula_drawn_in_lines_keeps_its_run():
    # must not fire (review of f706c8a1): a real U or L run with a deep peninsula drawn in lines is listed, not dropped
    from wenart.ingest.generic import symbols as SY
    table, _ = SY.load_size_table()
    run = _segs("LWPOLYLINE:B95B#0", "LWPOLYLINE:B95B#1")
    assert SY.no_counter_outlines({"legs": [], "blocks": [((0.0, 0.0, 3.71, 2.12), run)]}, table) == {}


# --- class 6: abbreviated room names ---

@pytest.mark.parametrize("label,area,rtype", [
    ("Lav.", 2.0, "wc"), ("LAV.+DUŞ", 4.0, "bathroom"), ("Lav. Duş", 4.0, "bathroom"), ("Lavanta", 3.0, "other"),
    ("S.ODASI", 9.34, "other"), ("SPOR ODASI", 43.0, "other"), ("ELK. PANO ODASI", 6.0, "technical"),
    ("Y.ODASI", 9.0, "bedroom"), ("YEMEK ODASI", 12.0, "other")])
def test_abbreviated_room_names(label, area, rtype):
    assert B.room_type_for(label, area) == rtype


def _flat(with_kitchen=True, with_window=True, area_side=3.0):
    rooms = [{"id": "r_s", "level_id": "L1", "label": "S.odası", "room_type": "other",
              "polygon": [[0, 0], [area_side, 0], [area_side, 3], [0, 3]]},
             {"id": "r_h", "level_id": "L1", "label": "Antre", "room_type": "hall",
              "polygon": [[area_side, 0], [area_side + 2, 0], [area_side + 2, 3], [area_side, 3]]}]
    if with_kitchen:
        rooms.append({"id": "r_k", "level_id": "L1", "label": "Mutfak", "room_type": "kitchen",
                      "polygon": [[area_side + 2, 0], [area_side + 5, 0], [area_side + 5, 3], [area_side + 2, 3]]})
    openings = [{"id": "win1", "type": "window", "level_id": "L1", "center": [area_side / 2, 0.0], "width": 1.2}] \
        if with_window else [{"id": "win2", "type": "window", "level_id": "L1", "center": [area_side, 1.5], "width": 1}]
    return {"rooms": rooms, "openings": openings}


def test_abbreviated_room_is_a_bedroom_in_a_flat_with_daylight():
    b = _flat()
    lines = B.abbreviated_room_types(b)
    r = b["rooms"][0]
    assert r["room_type"] == "bedroom" and r["inferred"] and "win1" in r["type_reason"] and len(lines) == 1


@pytest.mark.parametrize("kw", [{"with_kitchen": False}, {"with_window": False}, {"area_side": 1.8}])
def test_abbreviated_room_without_a_flat_context_stays_other(kw):
    # must not fire: no kitchen or living room on the floor (a plant floor: M., H., P., D.), no window to the outside
    # (the window into the hall), under a bed's size
    b = _flat(**kw)
    lines = B.abbreviated_room_types(b)
    assert b["rooms"][0]["room_type"] == "other" and "listed for review" in lines[0]


# --- class 7: an AI retype the code's daylight measure contradicts ---

def _plan(with_window: bool):
    from wenart.blender import architect_actions as AA
    walls = [{"id": "w1", "level_id": "L1", "start": [0, 0], "end": [5, 0], "thickness": 0.25},
             {"id": "w2", "level_id": "L1", "start": [5, 0], "end": [5, 4], "thickness": 0.25},
             {"id": "w3", "level_id": "L1", "start": [5, 4], "end": [0, 4], "thickness": 0.25},
             {"id": "w4", "level_id": "L1", "start": [0, 4], "end": [0, 0], "thickness": 0.25}]
    openings = [{"id": "win1", "type": "window", "level_id": "L1", "wall_id": "w1", "center": [2.5, 0], "width": 2.0,
                 "height": 1.4, "sill_height": 0.9}] if with_window else []
    b = {"levels": [{"id": "L1", "elevation": 3.0, "ceiling_height": 2.7}], "walls": walls, "openings": openings,
         "rooms": [{"id": "r1", "level_id": "L1", "room_type": "living", "label": "Günlük Oda",
                    "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}]}
    return AA.Plan(b)


def test_ai_cannot_make_a_lit_living_room_a_store():
    from wenart.agent import architect_ai as AI
    assert "glass to the outside" in AI.dark_retype_refusal(_plan(True), "r1", "storage")


def test_ai_retype_of_a_dark_room_or_to_a_lived_in_type_goes_on():
    from wenart.agent import architect_ai as AI
    assert AI.dark_retype_refusal(_plan(False), "r1", "storage") == ""
    assert AI.dark_retype_refusal(_plan(True), "r1", "bedroom") == ""


# --- class 4: a stair turn is judged by its own surface, never by the nosings' distance; drawn landings never ---

def _flight(start, end, width=1.0):
    import math
    d = math.dist(start, end)
    r = ((end[0] - start[0]) / d, (end[1] - start[1]) / d)
    return {"nosings": [start, end], "width": width, "rise_dir": r}


@pytest.mark.parametrize("well", [1.0, 1.5, 2.0])
def test_u_turn_with_a_wide_well_is_a_turn(well):
    from wenart.blender import parametric as P
    a, b = _flight((0, 0), (0, 3)), _flight((1.0 + well, 3.0), (1.0 + well, 0.0))
    box = {"center": [(1.0 + well) / 2.0, 2.0], "size": [2.0 + well, 4.2], "rotation_deg": 0.0}
    assert P.turn_misfit(a, b, box) == ""


def test_long_l_landing_is_a_turn():
    from wenart.blender import parametric as P
    a, b = _flight((0, 0), (0, 3)), _flight((1.8, 4.6), (4.5, 4.6))
    box = {"center": [2.0, 2.6], "size": [5.2, 5.4], "rotation_deg": 0.0}
    assert P.turn_misfit(a, b, box) == ""


def test_turn_outside_the_stair_or_through_a_wall_is_no_turn():
    from wenart.blender import parametric as P
    a, far = _flight((0, 0), (0, 3)), _flight((5.0, 6.0), (8.0, 6.0))                    # flights across a room
    only_a = {"center": [0.0, 1.5], "size": [1.2, 3.2], "rotation_deg": 0.0}
    assert "outside the stair's box" in P.turn_misfit(a, far, only_a)
    a, b = _flight((0, 0), (0, 3)), _flight((2.5, 3.0), (2.5, 0.0))
    box = {"center": [1.25, 2.0], "size": [3.5, 4.5], "rotation_deg": 0.0}
    wall = [{"start": [-1.0, 3.6], "end": [4.0, 3.6], "thickness": 1.4}]                  # a wall across the landing
    assert "in walls" in P.turn_misfit(a, b, box, wall)


# --- class 4: the top of a stair from below, drawn again with a flight of the neighbouring stair ---

def _stair(fid, level, center, size, rot=0.0):
    return {"id": fid, "level_id": level, "type": "stair",
            "footprint": {"center": center, "size": size, "rotation_deg": rot}}


def test_arrival_ignores_the_part_another_stair_of_its_level_covers():
    from wenart.sheets import to_building as TB
    shop_below = _stair("f_L-1_001", "L-1", [17.2, 14.8], [3.4, 1.7])
    shop = _stair("f_L0_001", "L0", [16.38, 14.77], [5.03, 1.73])      # reaches into the core stair's box
    core = _stair("f_L0_006", "L0", [13.5, 14.31], [3.25, 2.62])
    core_up = _stair("f_L1_011", "L1", [13.05, 14.32], [2.25, 2.62])
    rooms = [{"id": "r_L1_antre", "level_id": "L1", "room_type": "hall", "label": "Antre",
              "polygon": [[14.6, 13.0], [20.0, 13.0], [20.0, 16.5], [14.6, 16.5]]}]
    shop_below["stair"] = {"steps_drawn": 17}
    furniture = [shop_below, shop, core, core_up]
    assert TB.arrival_only(shop, "L-1", "L1", furniture, rooms, rise_below=3.0)
    # must not fire: the core stair itself goes on up
    assert not TB.arrival_only(core, "L-1", "L1", furniture, rooms, rise_below=3.0)


def test_a_main_stair_over_a_short_step_is_no_arrival():
    # must not fire (review of f706c8a1): a 3-riser step under the stair is no storey's stair, and a stair below that
    # covers less than half of this stair's own box is another stair
    from wenart.sheets import to_building as TB
    step = _stair("f_L-1_009", "L-1", [3.0, 2.0], [1.2, 0.9])
    step["stair"] = {"flights": [{"lines": 3}]}
    main = _stair("f_L0_001", "L0", [3.0, 2.5], [1.2, 3.0])
    rooms = [{"id": "r", "level_id": "L1", "room_type": "hall", "label": "Hol",
              "polygon": [[0, 0], [6, 0], [6, 5], [0, 5]]}]
    assert not TB.arrival_only(main, "L-1", "L1", [step, main], rooms, rise_below=3.0)
    step["stair"] = {"steps_drawn": 17}
    assert not TB.arrival_only(main, "L-1", "L1", [step, main], rooms, rise_below=3.0)   # covers 30 % of its box


# --- class 8: the slab under a smaller top level covers the typical copy under it ---

def test_terrace_slab_covers_the_copy_below():
    from shapely.geometry import Polygon
    from wenart.sheets import to_building as TB
    levels = [{"id": "L0", "order": 0, "elevation": 0.0, "evidence": []},
              {"id": "L1", "order": 1, "elevation": 3.0, "typical_of": "L0", "evidence": []},
              {"id": "L2", "order": 2, "elevation": 6.0, "evidence": []}]
    unions = {"L2": Polygon([(4, 4), (8, 4), (8, 8), (4, 8)])}
    outline = {"L0": [(0, 0), (12, 0), (12, 12), (0, 12)], "L1": None}
    slabs = TB.slabs_block({"heights": {}}, levels, unions, [], 0.2, lambda m: None, outline_of=outline.get)
    sl2 = next(s for s in slabs if s["id"] == "sl_L2")
    assert Polygon(sl2["outline"]).area == pytest.approx(144.0)


def test_top_slab_keeps_its_own_outline_when_the_floor_below_is_smaller():
    # must not fire: a level below smaller than the one above keeps the larger (own) outline
    from shapely.geometry import Polygon
    from wenart.sheets import to_building as TB
    levels = [{"id": "L0", "order": 0, "elevation": 0.0, "evidence": []},
              {"id": "L1", "order": 1, "elevation": 3.0, "evidence": []}]
    unions = {"L1": Polygon([(0, 0), (12, 0), (12, 12), (0, 12)])}
    slabs = TB.slabs_block({"heights": {}}, levels, unions, [], 0.2, lambda m: None,
                           outline_of={"L0": [(4, 4), (8, 4), (8, 8), (4, 8)]}.get)
    sl1 = next(s for s in slabs if s["id"] == "sl_L1")
    assert Polygon(sl1["outline"]).area == pytest.approx(144.0)


# --- class 3: nothing covers a level in its own top-down (the cover test, without Blender) ---

class _V:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class _M:
    def __matmul__(self, v):
        return v

    def to_3x3(self):
        return self


def _mesh_object(faces):
    verts = []
    polys = []
    for pts in faces:
        idx = []
        for p in pts:
            verts.append(SimpleNamespace(co=_V(*p)))
            idx.append(len(verts) - 1)
        polys.append(SimpleNamespace(vertices=idx, normal=_V(0, 0, 1)))
    ev = SimpleNamespace(data=SimpleNamespace(polygons=polys, vertices=verts), matrix_world=_M())
    return SimpleNamespace(evaluated_get=lambda dg: ev)


def test_a_plate_over_the_floor_covers_it_and_a_wall_cap_does_not():
    from wenart.blender import topdown as TD
    box = (0.0, 0.0, 12.0, 12.0)
    samples = [(box[0] + 12 * fx, box[1] + 12 * fy) for fx in (1 / 6, 0.5, 5 / 6) for fy in (1 / 6, 0.5, 5 / 6)]
    plate = _mesh_object([[(-30, -30, 7.5), (40, -30, 7.5), (40, 40, 7.5), (-30, 40, 7.5)]])
    assert len(TD.covering_faces(plate, None, 6.9, samples)) == 9 and TD.covers(TD.covering_faces(plate, None, 6.9,
                                                                                                  samples))
    cap = _mesh_object([[(0, 5.9, 7.5), (12, 5.9, 7.5), (12, 6.1, 7.5), (0, 6.1, 7.5)]])     # a wall's cut top
    held = TD.covering_faces(cap, None, 6.9, samples)
    assert len(held) == 3 and not TD.covers(held)                                         # one row: no surface
    low = _mesh_object([[(-30, -30, 7.0), (40, -30, 7.0), (40, 40, 7.0), (-30, 40, 7.0)]])   # the floor itself
    assert TD.covering_faces(low, None, 6.9, samples) == set()


# --- review follow-ups: an entrance marked outside a facade gap; the roof terrace's floor as an outdoor room ---

def test_ground_mark_outside_a_gap_marks_an_entrance():
    from wenart.levels import model as M
    b = {"level_marks": [{"id": "lm_016", "level_id": "L0", "kind": "ground_finished", "point": [5.95, 16.87],
                          "raw": "-0.35"},
                         {"id": "lm_002", "level_id": "L0", "kind": "ground_finished", "point": [5.79, 9.31],
                          "raw": "+0.54"}]}
    assert M.entrance_mark(b, "L0", (6.18, 16.71), (-1.0, 0.0))["id"] == "lm_016"
    # must not fire: a mark inside the house, or a corner mark far from the gap
    assert M.entrance_mark(b, "L0", (5.0, 16.71), (-1.0, 0.0)) is None
    assert M.entrance_mark(b, "L0", (6.18, 12.5), (-1.0, 0.0)) is None


def test_roof_terrace_floor_becomes_outdoor_rooms():
    from wenart.sheets import to_building as TB
    top = {"id": "L7", "roof_terrace": True, "evidence": []}
    b = {"slabs": [{"id": "sl_L7", "above_level_id": "L7", "variants": [],
                    "outline": [[0, 0], [12, 0], [12, 10], [0, 10]]}],
         "rooms": [{"id": "r_L7_oda", "level_id": "L7", "room_type": "stair",
                    "polygon": [[5, 4], [7, 4], [7, 6], [5, 6]]}]}
    n = TB.terrace_rooms(b, top)
    terr = [r for r in b["rooms"] if r["room_type"] == "balcony"]
    assert n == 2 and len(terr) == 2 and all(r["inferred"] and r["label"] == "Teras" for r in terr)
    assert sum(r["area_computed"] for r in terr) == pytest.approx(120 - 2.3 * 2.3, abs=0.2)
    # must not fire again on a level that already has its terrace room
    assert TB.terrace_rooms(b, top) == 0


def test_short_runs_are_no_stair_below_and_no_arrival():
    # the walls round's short steps (UL381) against the stair-top rule: a short run below never ends a main stair, and
    # a short run over a storey's stair is never that stair's top drawn again
    from wenart.sheets import to_building as TB
    run = _stair("f_L-1_009", "L-1", [3.0, 2.5], [1.2, 3.0])
    run["stair"] = {"short_steps": 3, "steps_drawn": 17}
    main = _stair("f_L0_001", "L0", [3.0, 2.5], [1.2, 3.0])
    rooms = [{"id": "r", "level_id": "L1", "room_type": "hall", "label": "Hol",
              "polygon": [[0, 0], [6, 0], [6, 5], [0, 5]]}]
    assert not TB.arrival_only(main, "L-1", "L1", [run, main], rooms, rise_below=3.0)
    full = _stair("f_L-1_001", "L-1", [3.0, 2.5], [1.2, 3.0])
    full["stair"] = {"steps_drawn": 17}
    top_run = _stair("f_L0_002", "L0", [3.0, 2.5], [1.2, 3.0])
    top_run["stair"] = {"short_steps": 2}
    assert not TB.arrival_only(top_run, "L-1", "L1", [full, top_run], rooms, rise_below=3.0)
