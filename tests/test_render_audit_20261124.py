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
    ("(3.NOR. KAT)", 3, "floor"), ("2.NOR.KAT", 2, "floor"), ("(ÇATI ARASI DÖŞEMESİ)", None, "attic")])
def test_storey_names_in_brackets_and_abbreviated(text, order, kind):
    lw = LV.level_of(text)
    assert lw is not None and lw.order == order and lw.kind == kind and not lw.typical


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
    region = SimpleNamespace(texts=texts, strokes=lambda: [])
    got = LV.storey_elevations([region])
    assert got == {-1: -2.8, 0: 0.2, 1: 3.5, 2: 6.5, 3: 9.5}


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


# --- class 5: a kitchen outline whose free part is deeper than any counter or island is no counter ---

def test_over_deep_kitchen_block_is_no_counter():
    from wenart.ingest.generic import symbols as SY
    table, _ = SY.load_size_table()
    hatch, island = ["hatch strokes"], ["island strokes"]
    split = {"legs": [], "blocks": [((0.0, 0.0, 3.71, 2.12), hatch), ((0.0, 3.0, 2.4, 4.0), island)]}
    assert SY.no_counter_outlines(split, table) == {id(hatch)}


# --- class 6: abbreviated room names ---

@pytest.mark.parametrize("label,area,rtype", [
    ("S.ODASI", 9.34, "bedroom"), ("M.ODASI", 8.0, "bedroom"), ("Lav.", 2.0, "wc"),
    # must not fire
    ("S.odası", 5.58, "other"), ("T.ODASI", 9.0, "other"), ("G.ODASI", 8.0, "other"), ("SPOR ODASI", 43.0, "other"),
    ("Lavanta", 3.0, "other"), ("ELK. PANO ODASI", 6.0, "technical"), ("YEMEK ODASI", 12.0, "other")])
def test_abbreviated_room_names(label, area, rtype):
    assert B.room_type_for(label, area) == rtype


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


# --- class 4: a stair turn only between flights within reach ---

def _flight(start, end, width=1.0):
    import math
    d = math.dist(start, end)
    r = ((end[0] - start[0]) / d, (end[1] - start[1]) / d)
    return {"nosings": [start, end], "width": width, "rise_dir": r}


def test_flights_far_apart_are_no_turn():
    from wenart.blender import parametric as P
    # real17 f_L0_001: flight 3 ends at (16.02, 13.91), flight 4 (the core stair's) starts 2.4 m away
    assert not P.flights_join(_flight((16.02, 14.39), (16.02, 13.91), 0.9), _flight((13.87, 15.03), (14.17, 15.03), 1.2))


def test_l_u_and_in_line_turns_join():
    from wenart.blender import parametric as P
    assert P.flights_join(_flight((0, 0), (0, 3)), _flight((0.7, 3.6), (3.0, 3.6)))          # an L
    assert P.flights_join(_flight((0, 0), (0, 3)), _flight((1.3, 3.0), (1.3, 0.0)))          # a U with its well
    assert P.flights_join(_flight((0, 0), (0, 3)), _flight((0, 5.2), (0, 7.0)))              # in line, 2.2 m landing


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
    furniture = [shop_below, shop, core, core_up]
    assert TB.arrival_only(shop, "L-1", "L1", furniture, rooms)
    # must not fire: the core stair itself goes on up
    assert not TB.arrival_only(core, "L-1", "L1", furniture, rooms)


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
