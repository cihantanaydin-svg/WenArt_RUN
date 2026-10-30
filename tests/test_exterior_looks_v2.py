"""Exterior upgrade of 24 Oct 2026 (user request: facade materials, no slab 'balcony', library doors and windows):
the facade scheme, the railing posts and the library opening plan (CPU, pure)."""
import math

from wenart.blender import exterior as E
from wenart.blender import facade as FA
from wenart.blender import opening_models as OM
from wenart.blender import shell as SH

LEVELS = [{"id": "L-1", "elevation": -3.0, "height": 3.0, "kind": "basement"},
          {"id": "L0", "elevation": 0.0, "height": 3.0, "kind": "floor"},
          {"id": "L1", "elevation": 3.0, "height": 3.0, "kind": "floor"}]


def _building():
    return {"walls": [{"id": "w1", "level_id": "L0", "start": [0.0, 0.0], "end": [10.0, 0.0]}],
            "openings": [{"id": "d1", "type": "door", "wall_id": "w1", "center": [4.0, 0.0], "width": 1.0}],
            "site": {"entrances": [{"door_id": "d1", "level_id": "L0", "main": True}]}}


def test_scheme_of_falls_back_to_the_default_family():
    assert FA.scheme_of({"family": "industrial"})["base"] == "brick_red"
    sch = FA.scheme_of({"family": "unknown"})
    assert sch["family"] == "unknown" and sch["main"] == FA.FACADE_SCHEMES["default"]["main"]
    assert FA.scheme_of(None)["family"] == "default"


def test_scheme_faces_frame_the_entrance_and_clad_the_basement():
    faces = FA.scheme_faces(_building(), {"family": "modern"}, LEVELS)
    accent, base, upper = faces          # 29 Oct 2026 (UL100): the top storey of a two-storey house is clad
    assert upper["level_id"] == "L1" and upper["material"] == "wood_cladding" and upper["upper"]
    assert accent["material"] == "wood_cladding" and accent["wall_id"] == "w1" and accent["inferred"]
    (x0, _), (x1, _) = accent["span"]
    assert math.isclose(x0, 2.5) and math.isclose(x1, 5.5)              # door 1.0 m + 1.0 m margin each side
    assert accent["z_range"] == [-0.5, 3.0]                            # up to the next level
    assert base["level_id"] == "L-1" and base["material"] == "stone_wall_ledgestone"
    assert FA.on_span([4.0, 0.3], accent["span"]) and not FA.on_span([6.0, 0.0], accent["span"])


def test_scheme_without_an_accent_or_an_entrance_clads_only_the_basement():
    assert [f.get("level_id") for f in FA.scheme_faces(_building(), {"family": "industrial"}, LEVELS)] == ["L-1", "L1"]
    b = dict(_building(), site={})
    assert [f.get("level_id") for f in FA.scheme_faces(b, {"family": "modern"}, LEVELS)] == ["L-1", "L1"]
    assert [f.get("level_id") for f in FA.scheme_faces(b, {"family": "classic"}, LEVELS)] == ["L-1"]


def test_resolve_looks_takes_the_scheme_when_nothing_names_the_facade():
    looks = E.resolve_looks({"facade": {}}, {"family": "rustic"})
    assert looks["facade"]["source"] == "fallback" and looks["facade"]["colour"] == "cream"
    assert looks["facade"]["rgb"] is not None and looks["facade"]["scheme"]["base"] == "stone_wall_rubble"


def test_railing_posts_reach_both_ends_and_stay_within_the_spacing():
    posts = SH.railing_posts((0.0, 0.0), (4.0, 0.0), 0.0)
    assert len(posts) == 4                                             # 4.0 m / 1.5 m -> 3 bays, 4 posts
    xs = sorted(sum(v[0] for v in verts) / len(verts) for verts, _ in posts)
    assert math.isclose(xs[0], SH.RAILING["post"] / 2) and math.isclose(xs[-1], 4.0 - SH.RAILING["post"] / 2)
    assert max(b - a for a, b in zip(xs, xs[1:])) <= SH.RAILING["post_every"] + 1e-9
    assert SH.railing_posts((0.0, 0.0), (0.0, 0.0), 0.0) == []


def _extra(i, kind, w, d, h, title, status="keep", flag="none", textured=True):
    return {"id": f"x{i}", "type": kind, "title": title, "glb": f"x{i}.glb", "bbox_m": [w, d, h],
            "audit": {"status": status}, "licence_flag": flag, "textured": textured}


EXTRAS = [_extra(1, "door", 0.95, 0.16, 2.05, "Front Door"),
          _extra(2, "door", 2.4, 0.18, 2.1, "Sliding Double Door"),
          _extra(3, "window", 1.2, 0.12, 1.2, "Window 3"),
          _extra(4, "window", 1.2, 0.12, 1.2, "Window pack", ),                     # a pack: never
          _extra(5, "window", 0.6, 0.1, 1.2, "Casement window", flag="no_derivatives"),
          _extra(6, "door", 0.9, 0.1, 2.0, "Closet door")]


def _outer(oid, kind, width, bottom, top):
    return {"opening": {"id": oid, "type": kind, "width": width}, "bottom": bottom, "top": top}


def test_opening_plan_picks_one_model_per_category_and_panels_long_windows():
    outer = [_outer("d1", "door", 1.0, 0.0, 2.1), _outer("d2", "door", 2.4, 0.0, 2.1),
             _outer("w1", "window", 3.6, 0.9, 2.1), _outer("w2", "window", 0.3, 1.8, 2.1)]
    plan = OM.plan(_building(), outer, EXTRAS)
    assert plan["d1"]["category"] == "entrance" and plan["d1"]["asset"]["asset_id"] == "x1"
    assert plan["d2"]["category"] == "glazed_door" and plan["d2"]["asset"]["asset_id"] == "x2"
    assert plan["w1"]["asset"]["asset_id"] == "x3" and plan["w1"]["panels"] == 3
    assert "w2" not in plan                                             # 0.3 x 0.3: no model of that shape
    assert plan["d1"]["panels"] == 1 and "not its product" in plan["d1"]["reason"]


def test_opening_candidates_respect_audit_licence_and_words():
    assert [e["id"] for e in OM.candidates(EXTRAS, "window", "relaxed")] == ["x3"]
    nc = [_extra(7, "window", 1.2, 0.1, 1.2, "Window", flag="non_commercial")]
    assert OM.candidates(nc, "window", "relaxed") and not OM.candidates(nc, "window", "commercial")
    assert not OM.candidates([_extra(8, "window", 1.2, 0.1, 1.2, "Window", status="drop")], "window", "relaxed")
    assert [e["id"] for e in OM.candidates(EXTRAS, "door", "relaxed")] == ["x1"]


from wenart.blender import site as S
from wenart.blender import site_models as SM


def _plant(i, kind, w, d, h, title, poly=5000, textured=True):
    return {"id": f"p{i}", "type": kind, "title": title, "glb": f"p{i}.glb", "bbox_m": [w, d, h], "polycount": poly,
            "audit": {"status": "keep"}, "licence_flag": "none", "textured": textured}


PLANTS = [_plant(1, "tree", 6.0, 6.0, 8.0, "Oak Tree"), _plant(2, "tree", 4.0, 4.0, 10.0, "Pine tree"),
          _plant(3, "tree", 28.0, 16.0, 10.0, "PLANT COLLECTION PART 1"), _plant(4, "tree", 5.0, 5.0, 6.0, "tree"),
          _plant(5, "palm", 4.0, 4.0, 5.0, "Palm tree"), _plant(6, "palm", 6.4, 0.7, 6.7, "Palm trees"),
          _plant(7, "hedge", 1.6, 1.3, 1.1, "Small bush or hedge"), _plant(8, "tree", 2.0, 2.0, 2.0, "Plant in pot")]


def test_plant_model_matches_species_then_crown_then_kind():
    pick = SM.plant_model({"name": "oak", "crown": "spreading"}, PLANTS)
    assert pick["match"] == "species" and pick["asset"]["asset_id"] == "p1"
    assert SM.plant_model({"name": "conifer", "crown": "conical"}, PLANTS)["asset"]["asset_id"] == "p2"
    assert SM.plant_model({"name": "olive", "crown": "round"}, PLANTS)["match"] == "kind"     # no olive, no pine
    assert SM.plant_model({"name": "palm", "crown": "palm"}, PLANTS)["asset"]["asset_id"] == "p5"   # not the row
    assert SM.plant_model({"name": "oleander", "crown": "shrub"}, PLANTS)["asset"]["asset_id"] == "p7"
    assert SM.plant_model({"name": "boxwood", "crown": "hedge"}, PLANTS) is None
    assert SM.plant_kind(PLANTS[2]) is None and SM.plant_kind(PLANTS[7]) is None


def test_car_models_need_a_real_car_size():
    # 30 Oct 2026 (lesson UL129): ``bbox_m`` is the piece frame (width, depth); c1's front +X lies across its 4.7 m
    # long side, so the build turns it back to the long side (+Y) and keeps its real size, uniformly scaled
    cars = [{"id": "c1", "type": "car", "title": "Car", "glb": "c1.glb", "bbox_m": [4.7, 2.1, 1.4], "front_axis": "+X",
             "audit": {"status": "fix"}, "licence_flag": "none", "textured": True, "polycount": 40000},
            {"id": "c2", "type": "car", "title": "Car Turntable", "glb": "c2.glb", "bbox_m": [5.2, 5.4, 2.0],
             "front_axis": "+X", "audit": {"status": "keep"}, "licence_flag": "none", "textured": True,
             "polycount": 40000},
            {"id": "c3", "type": "car", "title": "Car", "glb": "c3.glb", "bbox_m": [0.5, 0.2, 0.1], "front_axis": "+X",
             "audit": {"status": "keep"}, "licence_flag": "none", "textured": True, "polycount": 40000}]
    got = SM.car_models(cars)
    assert [c["asset"]["asset_id"] for c in got] == ["c1"]
    assert got[0]["size"] == [2.1, 4.7, 1.4] and got[0]["asset"]["front_axis"] == "+Y"


def test_car_slots_fit_inside_the_parking():
    perp = SM.car_slots([[0, 0], [12, 0], [12, 6], [0, 6]])
    assert len(perp) == SM.MAX_CARS and {s["layout"] for s in perp} == {"perpendicular"}
    assert all(0 < s["center"][0] < 12 and 0 < s["center"][1] < 6 for s in perp)
    par = SM.car_slots([[0, 0], [12, 0], [12, 3], [0, 3]])
    assert par[0]["layout"] == "parallel" and par[0]["rotation_deg"] == 90.0     # the front along +x
    assert SM.car_slots([[0, 0], [3, 0], [3, 3], [0, 3]]) == []


def test_parkings_and_car_ground_follow_the_terrain():
    terrain = {"kind": "flat", "z": {k: 1.0 for k in S.AXES}}
    plan = {"terrain": terrain, "platforms": [{"id": "p1", "kind": "parking", "polygon": [[0, 0], [6, 0], [6, 6]],
                                               "z": 0.5, "sloped": False}],
            "areas": [{"id": "a1", "kind": "parking", "polygon": [[0, 0], [6, 0], [6, 6]]}]}
    lots = S.parkings(plan)
    assert [(lot["id"], lot["z"]) for lot in lots] == [("p1", 0.5), ("a1", None)]
    assert S.car_ground(plan, lots[0], {"center": [3, 3]}) == (0.5, 0.0, 0.0)
    z, gx, gy = S.car_ground(plan, lots[1], {"center": [3, 3]})
    assert abs(z - 1.0 - S.CAR_LIFT_M) < 1e-9 and gx == gy == 0.0


from wenart.blender import vegetation as VG


class _Img:
    def __init__(self, alphas, channels=4, mode="STRAIGHT"):
        self.channels, self.alpha_mode = channels, mode
        self.pixels = [v for a in alphas for v in (1.0, 1.0, 1.0, a)]


def test_image_cutout_is_found_by_its_transparent_texels():
    assert VG._image_has_cutout(_Img([1.0] * 50 + [0.0] * 50))
    assert not VG._image_has_cutout(_Img([1.0] * 100))
    assert not VG._image_has_cutout(_Img([0.0] * 10, mode="NONE")) and not VG._image_has_cutout(None)


def test_a_light_well_over_a_lower_terrace_is_dropped_and_one_under_a_higher_terrace_opens_at_it():
    square = [[0.0, 0.0], [4.0, 0.0], [4.0, 2.0], [0.0, 2.0]]
    well = {"opening_id": "w1", "polygon": [[1.0, 0.5], [3.0, 0.5], [3.0, 1.5], [1.0, 1.5]], "source": "assumed",
            "sill_z": -2.1, "top_z": -1.6, "floor_z": -2.3}
    low = [{"id": "t1", "kind": "terrace", "polygon": square, "z": -3.0, "sloped": False}]
    kept, gone = S.wells_on_platforms([well], low)
    assert kept == [] and "no light well" in gone[0]["dropped_reason"]
    high = [dict(low[0], z=-1.4)]
    kept, gone = S.wells_on_platforms([well], high)
    assert gone == [] and kept[0]["top_z"] == -1.4 and kept[0]["platform_id"] == "t1"
    assert S.wells_on_platforms([dict(well, source="drawn")], low)[0][0]["source"] == "drawn"   # drawn stays
    assert S.wells_on_platforms([well], [dict(low[0], sloped=True)])[0] == [well]                 # draped: no level


def test_gutters_stop_where_a_roof_terrace_cuts_the_eaves():
    from wenart.blender import facade as FA
    model = {"type": "hip", "eaves_z": 3.0, "outline": [[0, 0], [10, 0], [10, 6], [0, 6]],
             "equations": [(0.0, 0.5, 3.0), (0.0, -0.5, 6.0), (0.5, 0.0, 3.0), (-0.5, 0.0, 8.0)],
             "openings": [{"polygon": [[0, 0], [3, 0], [3, 6], [0, 6]]}]}
    edges = FA.eaves_edges(model)
    south = [e for e in edges if abs(e["p"][1]) < 1e-9 and abs(e["q"][1]) < 1e-9]
    assert len(south) == 1 and min(south[0]["p"][0], south[0]["q"][0]) >= 3.0 - 1e-6
    assert not any(max(e["p"][0], e["q"][0]) <= 3.0 for e in edges)        # nothing along the terrace
    assert len(FA.eaves_edges(dict(model, openings=[]))) > len(edges)


def test_low_rated_library_models_are_never_picked():
    bush = _plant(9, "hedge", 1.6, 1.3, 1.1, "Small bush or hedge")
    bush["audit"]["vision_doubt"] = ["vision quality 2 (<= 2)"]
    assert SM.vision_quality(bush) == 2 and not SM.usable(bush, "relaxed")
    assert SM.plant_model({"name": "oleander", "crown": "shrub"}, [bush]) is None
    ok = dict(bush, audit={"status": "keep", "vision_doubt": ["vision quality 3"]})
    assert SM.usable(ok, "relaxed") and SM.vision_quality(PLANTS[0]) is None
    win = _extra(10, "window", 1.2, 0.12, 1.2, "Window")
    win["audit"]["vision_doubt"] = ["vision quality 1 (<= 2)"]
    assert OM.candidates([win], "window", "relaxed") == []


def test_a_roof_terrace_parapet_stops_at_the_eaves_with_a_railing_above(monkeypatch):
    import copy
    import gzip
    import json as _json
    from pathlib import Path

    from wenart.blender import build as BU
    from wenart.blender import roof as R

    path = Path(__file__).resolve().parent / "fixtures" / "m11_f1b" / "real02_building_final.json.gz"
    b = _json.load(gzip.open(path))
    prep = BU.prepare(copy.deepcopy(b), "base", None)
    roof, vb = prep["roof"], prep["building"]
    over = next(lv for lv in vb["levels"] if lv["id"] == roof["over_level_id"])
    knee = roof["eaves_z"] - float(over["elevation"])
    for o in roof["openings"]:
        if o["parapet_source"] == "assumed":
            assert o["parapet_height"] == round(knee, 3) and o["guard_height"] == R.DEFAULTS["parapet"]
    runs = BU.terrace_railing_runs(roof, vb, over, R.parapet_cuts(roof, vb, over))
    assert runs and all(abs(r["height"] - (R.DEFAULTS["parapet"] - round(knee, 3))) < 1e-9 for r in runs)
    assert all(abs(r["z"] - (float(over["elevation"]) + round(knee, 3))) < 1e-9 for r in runs)
