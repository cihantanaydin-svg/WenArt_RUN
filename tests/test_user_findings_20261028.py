"""28 Oct 2026, the user's look at real06 run 222248 and real04 run 005318 (general rules, the projects are the cases):
a drawn column takes the size of its own outline, not of its hatch and axis cross ("columns under is too thick"); a
house roof that reaches far over a space gets posts at its corners ("There is no column supporting the roof"); a lower
roof the roof plan draws is built sloped ("no sloped roof next to the balcony"); a door read as a window loses its
entrance ("Enterence to the window?"); a wall-backed piece never leaves its wall to clear a window, and storage closes
a tall window ("If this is a full window this thing here closing the window"); a floor texture never clads a wall
("What kind of a kitchen is this"); a door model opens as the drawing does ("This window / door should have been
sliding as indicated in the plan")."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.blender import architect_actions as AA
from wenart.blender import exterior_checks as X
from wenart.blender import opening_models as OM
from wenart.blender import site as S
from wenart.levels import outdoor as O

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"


def _column(boxes, size=(0.525, 0.44)):
    return {"id": "sd_x", "kind": "other", "center": [1.0, 1.0], "size": list(size), "inferred_as": "column",
            "evidence": [{"layer": "TARAMA,aks merkezleri,KOLON", "entity": "CIRCLE:1,LINE:2,LINE:3",
                          **({"layer_boxes": boxes} if boxes else {})}]}


def test_a_drawn_column_takes_the_size_of_its_column_layer_outline():
    boxes = {"KOLON": {"center": [1.02, 1.0], "size": [0.4, 0.4]},
             "TARAMA": {"center": [1.0, 1.0], "size": [0.525, 0.44]}}
    item = _column(boxes)
    assert O.core_box(item) == boxes["KOLON"]
    assert O.column_look(item) == {"shape": "round", "size_m": 0.4, "size_xy": [0.4, 0.4], "rotation_deg": 0.0}
    # without the reading's layer boxes (one layer, an older reading) the symbol's own size stays
    assert O.core_box(_column(None)) is None and O.column_look(_column(None))["size_m"] == 0.525


def test_the_reading_records_each_layers_footprint():
    src = (ROOT / "wenart" / "ingest" / "generic" / "symbols.py").read_text(encoding="utf-8")
    assert 'ev["layer_boxes"] = boxes' in src


def _real06_spaces():
    from wenart.levels import model as M

    b = json.loads(REAL06.read_text(encoding="utf-8"))
    n = M.infer_levels(b)
    return b, {s["id"]: s for s in n["site"]["outdoor_spaces"]}


@pytest.mark.skipif(not REAL06.is_file(), reason="no real06 fixture")
def test_the_house_roof_over_a_balcony_stands_on_posts_over_the_columns_below():
    _b, spaces = _real06_spaces()
    bal = spaces.get("os_L1_balkon")
    if bal is None or bal.get("cover_source") != "building_roof":
        pytest.skip("this reading has no balcony under the drawn roof")
    posts = [q for q in bal.get("posts") or [] if "building's roof" in str(q.get("carries"))]
    assert posts, bal.get("posts")
    cols = {tuple(c["center"]) for c in bal.get("columns") or []}
    assert all(tuple(q["center"]) in cols or not cols for q in posts)      # the columns below carry on up
    assert all(q["z1"] - q["z0"] >= 2.1 and q["source"] == "inferred" and "no cantilever" in q["reason"]
               for q in posts)


def test_house_roof_posts_only_where_the_roof_reaches_far_out():
    walls = [[0, 0], [6, 0], [6, 6], [0, 6]]
    building = {"roof": {"outline": [[-0.5, -3.0], [6.5, -3.0], [6.5, 6.5], [-0.5, 6.5]],
                         "outline_source": "roof_plan", "eaves_height": {"value": 6.0},
                         "roof_plan_outline": {"region_id": "r6", "others": []}}}
    deep = {"id": "os_deep", "level_id": "L1", "z": 3.0, "polygon": [[1, -2.5], [4, -2.5], [4, 0], [1, 0]],
            "cover_source": "building_roof", "columns": []}
    shallow = {"id": "os_flat", "level_id": "L1", "z": 3.0, "polygon": [[1, -1.0], [4, -1.0], [4, 0], [1, 0]],
               "cover_source": "building_roof", "columns": []}
    O.house_roof_posts([deep, shallow], building, {"L1": walls})
    assert len(deep["posts"]) == 2 and all(q["z0"] == 3.0 and q["z1"] == 6.0 for q in deep["posts"])
    assert not shallow.get("posts")                                            # 1.0 m: within post_reach


@pytest.mark.skipif(not REAL06.is_file(), reason="no real06 fixture")
def test_a_lower_roof_the_roof_plan_draws_is_built_sloped_away_from_the_house():
    b, spaces = _real06_spaces()
    ver = spaces.get("os_L0_veranda")
    roof = (ver or {}).get("roof") or {}
    if not roof.get("drawn"):
        pytest.skip("this reading draws no lower roof over the veranda")
    assert roof["kind"] == "pitched" and O.PITCHED["min_deg"] <= roof["pitch_deg"] <= O.drawn_pitch(b) + 1e-6
    assert roof["covering"] == "roof" and roof["fall"] == pytest.approx(
        __import__("math").tan(__import__("math").radians(roof["pitch_deg"])), abs=1e-6)
    low = min(S.roof_z(roof, p) for p in ver["polygon"]) - roof["thickness"]
    assert low - float(ver["z"]) >= O.SPACE["min_clear"] - 0.35        # the walking area keeps its clear height
    parts = S.cover_parts({"roof": roof, "posts": roof["posts"]})
    assert {p["part"] for p in parts} >= {"roof", "posts"}


def test_the_slope_takes_an_axis_away_from_the_house():
    poly = [[0, 0], [2, 0], [2, 5], [0, 5]]
    assert O.axis_dirs_away((0.0, -2.0), poly)[0] == (0.0, -1.0)
    assert set(O.axis_dirs_away((-1.0, -1.0), poly)) == {(0.0, -1.0), (-1.0, 0.0)}
    assert O.drawn_pitch({"roof": {"pitches_deg": [{"value": 18.3}]}}) == 18.3
    assert O.drawn_pitch({}) == O.PITCHED["default_deg"]


def test_a_door_read_as_a_window_loses_its_entrance_steps_and_canopy():
    b = {"openings": [{"id": "d1", "type": "window", "level_id": "L0"}, {"id": "d2", "type": "door", "level_id": "L0"}],
         "site": {"entrances": [{"door_id": "d1", "level_id": "L0", "centre": [0, 0], "outward": [0, -1],
                                 "threshold_z": 0.0, "ground_z": 0.0},
                                {"door_id": "d2", "level_id": "L0", "centre": [3, 0], "outward": [0, -1],
                                 "threshold_z": 0.0, "ground_z": 0.0}]}}
    got = S.record_entrances(b, [{"id": "L0", "elevation": 0.0}])
    assert [e["opening_id"] for e in got] == ["d2"]
    assert AA.drop_entrance(b, "d1", "code gap_behind_furniture") == 1
    assert [e["door_id"] for e in b["site"]["entrances"]] == ["d2"]
    assert b["site"]["entrances_removed"][0]["removed_by"] == "code gap_behind_furniture"


def test_the_door_widening_skips_a_window():
    b = {"walls": [{"id": "w", "level_id": "L0", "start": [0, 0], "end": [5, 0], "thickness": 0.2}],
         "openings": [{"id": "d1", "type": "window", "level_id": "L0", "wall_id": "w", "center": [2.5, 0],
                       "width": 0.65}], "rooms": [], "levels": [{"id": "L0", "elevation": 0.0}]}
    plan = AA.Plan(b)
    ok, text = AA.act_widen_door(plan, "D1:d1", {"by": "ai"}, "d1")
    assert ok and "is a window now" in text and plan.openings["d1"]["width"] == 0.65


@pytest.mark.skipif(not (ROOT / "results/baseline/latest/furniture/real06/building_final.json").is_file(),
                    reason="no committed real06 building")
def test_a_wall_backed_piece_keeps_its_wall_when_asked_to_clear_a_window():
    b = json.loads((ROOT / "results/baseline/latest/furniture/real06/building_final.json").read_text())
    if not any(f.get("id") == "f_L1_005" and f.get("type") == "dresser" for f in b.get("furniture") or []):
        pytest.skip("this building has no drawn dresser f_L1_005")
    plan = AA.Plan(copy.deepcopy(b))
    before = copy.deepcopy(next(f for f in plan.b["furniture"] if f["id"] == "f_L1_005")["footprint"])
    ok, text = AA.act_move_piece(plan, "AI.move_piece:f_L1_005", {"by": "argus"}, "f_L1_005", "d_L1_005")
    after = next(f for f in plan.b["furniture"] if f["id"] == "f_L1_005")["footprint"]
    if ok:                                     # slid along its wall: its distance to that wall is unchanged
        assert "along its wall" in text
    else:
        assert "keeps its back on the wall" in text and after == before


def test_storage_closes_a_tall_window_whatever_share_it_covers():
    from wenart.furniture import group_checks as GC

    assert "dresser" in GC.TALL_WINDOW_BLOCKERS and "nightstand" not in GC.TALL_WINDOW_BLOCKERS


def test_a_floor_texture_never_clads_a_wall():
    bad = X.validate_material_override({}, {"kitchen_walls": "wood_oak_light"})
    assert not bad["ok"] and "floor finish" in bad["failed"][0]
    assert X.validate_material_override({}, {"kitchen_walls": "wood_veneer_oak"})["ok"]
    assert X.validate_material_override({}, {"floor": "wood_oak_light"})["ok"]
    assert X.floor_texture({"asset": "WoodFloor051"}) and not X.floor_texture({"asset": "oak_veneer_01"})


def test_a_door_model_opens_as_the_drawing_does():
    assert OM.model_operation({"title": "Valdi - Folding Sliding Door - 4 Door Ti"}) == "folding"
    assert OM.model_operation({"title": "Lift Slide Patio Door"}) == "sliding"
    assert OM.model_operation({"title": "Glass Door"}) is None
    assert OM.opening_operation({"type": "door", "door_type": "glazed_sliding"}) == "sliding"
    assert OM.opening_operation({"type": "door", "operation": "swing"}) == "hinged"
    assert OM.opening_operation({"type": "window"}) is None
    kept, wrong = OM.operation_fit([{"id": "a", "title": "Folding Sliding Door"}, {"id": "b", "title": "Sliding door"},
                                    {"id": "c", "title": "Glass door"}], {"sliding"})
    assert [e["id"] for e in kept] == ["b", "c"] and "folding door" in wrong["a"]
    kept, _w = OM.operation_fit([{"id": "b", "title": "Sliding door"}, {"id": "c", "title": "Glass door"}],
                                {"sliding", "hinged"})
    assert [e["id"] for e in kept] == ["c"]


def test_a_veranda_roof_is_designed_not_traced_from_its_floor():
    # 28 Oct 2026 (user on real06: "This should not supposed to be 1 to one with what is under, it is a veranda this
    # roof of veranda needs to make sense")
    from shapely.geometry import Polygon

    house = Polygon([(0, 0), (10, 0), (10, 8), (0, 8)])
    floor = Polygon([(2, 0), (2, -3), (4, -3), (4, -2.7), (4.4, -2.7), (4.4, -3), (7, -3), (7, -0.25), (6.9, -0.25),
                     (6.9, 0)])                       # a 0.4 m notch at the front, a 0.1 m jog at the wall
    roof, post, how = O.cover_shape(floor, [house])
    oh = O.COVER_SHAPE["overhang_m"]
    assert len(roof.exterior.coords) == 5 and "rectangle" in how and "1 side(s) against the house" in how
    assert roof.bounds == pytest.approx((2 - oh, -3 - oh, 7 + oh, 0.0), abs=1e-6)   # flush with the facade
    assert post.area >= floor.area and post.contains(floor.buffer(-0.01))
    ell = Polygon([(0, 0), (0, -4), (6, -4), (6, -2), (3, -2), (3, 0)])            # an L stays an L
    roof, _post, how = O.cover_shape(ell, [house])
    assert "notches filled" in how and roof.area > ell.area and roof.area < 6 * 4
    assert O._corner_inset((0, 0), (4, 0), (4, 3), 0.2) == pytest.approx((3.8, 0.2))
    assert O._corner_inset((0, 0), (4, 0), (4, -3), 0.2) is None                   # a notch's corner frames no post


def test_a_light_roof_is_covered_with_a_roofing_never_the_facade_cladding():
    looks = {"facade": {"material": "wood_cladding"}, "window_frame": {"colour": "black"},
             "roof": {"material": "clay_tiles"}}
    top = S.cover_top_look({"kind": "light_roof"}, looks)
    assert top["material"] == S.COVER_TOP_MATERIAL == "standing_seam" and top["colour"] == "black"
    assert S.cover_top_look({"kind": "pitched", "covering": "roof"}, looks) == {"material": "clay_tiles"}


def test_inside_doors_vary_by_the_rooms_they_join():
    # 28 Oct 2026 (user: "I want better doors inside the house and the outside ... some variation is needed")
    from wenart.blender import looks
    from wenart.blender import shell

    style = {"door": {"material": "wood_oak_light"}, "family": "scandinavian"}
    living = looks.door_look(style, {"id": "d", "type": "door", "joins": ["hall", "living"]})
    bed = looks.door_look(style, {"id": "d", "type": "door", "joins": ["hall", "bedroom"]})
    assert living["door_style"] == "glazed" and "daylight" in living["reason"]
    assert bed["door_style"] == "flush"
    classic = looks.door_look(dict(style, family="classic"), {"id": "d", "type": "door", "joins": ["bathroom", "hall"]})
    assert classic["door_style"] == "shaker_panel"
    assert looks.door_look(style, {"id": "d", "type": "door"})["door_style"] == "flush"          # no rooms known
    assert looks.door_look(dict(style, door={"style": "shaker_panel"}),
                           {"id": "d", "type": "door", "joins": ["living", "hall"]})["door_style"] == "shaker_panel"
    slide = looks.door_look(style, {"id": "d", "type": "door", "operation": "sliding", "joins": ["living", "hall"]})
    assert slide["door_style"] == "sliding"                                # the drawn operation still wins
    wall = {"start": [0, 0], "end": [4, 0], "thickness": 0.2}
    rooms = [{"room_type": "living", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]},
             {"room_type": "hall", "polygon": [[0, -2], [4, -2], [4, 0], [0, 0]]}]
    assert shell.door_sides((2.0, 0.0), wall, rooms) == ["living", "hall"]


def test_the_best_looking_door_family_comes_first():
    a = {"id": "a", "title": "Door A", "audit_quality": 3, "textured": True}
    b = {"id": "b", "title": "Door B", "audit_quality": 4, "textured": False}
    extras = [dict(a, audit_quality=None), dict(b, audit_quality=None)]
    assert OM.audit_quality(extras, {"items": [{"id": "a", "vision": {"quality": 3}},
                                               {"id": "b", "vision": {"quality": 4}}]}) == 2
    assert [e["audit_quality"] for e in extras] == [3, 4]


def test_every_basin_gets_a_mirror_even_under_a_window():
    # 28 Oct 2026 (user: "Mirrors in the baths is missing sometimes"; real06: basins under a window, an inferred basin)
    from test_decor_m8 import room_building
    from wenart.furniture import decor_ai as DA

    b = room_building(3.0, 2.5, "bathroom", furniture=[("washbasin", (1.0, 0.25), 0.0, (0.6, 0.45)),
                                                       ("toilet", (2.4, 0.4), 0.0, (0.4, 0.7))],
                      windows=(("win1", "s", 1.0, 1.2),))
    rq = DA.room_questions(b, "modern")[0]
    slot = next(s for s in rq.slots if s.id == "f_L0_001.wall")
    mirror = slot.items["mirror"]
    assert "beside the basin" in mirror["reason"] and mirror["size"][0] == DA.SIDE_MIRROR_W
    n = iter(range(1, 99))
    got = DA.required_items(rq, [], b, lambda lv: f"dec_{lv}_{next(n):03d}")
    assert [i["type"] for i in got] == ["mirror"] and got[0]["method"] == "rule"
    assert DA.required_items(rq, got, b, lambda lv: "x") == []                     # one mirror per basin
    b["furniture"][0]["status"] = "unverified"                                     # an inferred basin: still one
    b["furniture"][1]["status"] = "verified"
    slots, _notes = DA.room_slots(b["rooms"][0], b["furniture"], b)
    assert any(s.host_id == "f_L0_001" and "mirror" in s.types for s in slots)


def test_the_skirting_wraps_the_outside_corners_of_a_room():
    # 28 Oct 2026 (user: "baseboard needs to be all around")
    from wenart.blender import shell

    room = [(0, 0), (4, 0), (4, 3), (2, 3), (2, 2), (0, 2)]        # an L: the corner (2, 2) juts into the room
    assert shell.skirting_reflex_corners(room) == {4}
    assert shell.skirting_reflex_corners(list(reversed(room))) == {1}
    spans = shell.skirting_spans(room, [])
    verts, _faces = shell.skirting_boxes(room, spans, 0.0)
    t = shell.SKIRTING_T
    # both boards run on by their thickness: the corner square (2..2+t, 2-t..2) is closed, no notch
    assert any(abs(v[0] - (2.0 + t)) < 1e-6 and abs(v[1] - (2.0 - t)) < 1e-6 for v in verts)
    assert sum(1 for v in verts if abs(v[0] - (2.0 + t)) < 1e-6 and abs(v[1] - (2.0 - t)) < 1e-6) >= 4


def test_an_inside_door_model_never_goes_on_the_facade():
    # 28 Oct 2026 (real04 and real06 got a "bathroom door" on the facade, real04's terrace doors a "Front Door")
    for title in ("bathroom door", "bedroom door toilet door", "20 HiQ container"):
        assert OM._has(OM._title({"title": title}), OM.NOT_WORDS["door"]), title
        assert OM._has(OM._title({"title": title}), OM.NOT_WORDS["entrance"]), title
    assert OM._has(OM._title({"title": "Front Door"}), OM.NOT_WORDS["terrace_door"])
    assert not OM._has(OM._title({"title": "Balcony door"}), OM.NOT_WORDS["terrace_door"])
