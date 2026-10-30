"""Site elements only where they make sense (30 Oct 2026; lessons UL129, UL141, UL142, UL143, UL144 of the user's review
of real04 run 20261029-201533-full). Pure tests, no Blender: every rule is general, real04 is only the test case."""
import math

from wenart import geometry as G
from wenart.assets.audit import write as AW
from wenart.audit import conservation as C
from wenart.blender import architect as AR
from wenart.blender import grading as GR
from wenart.blender import pool_extras as PX
from wenart.blender import site as S
from wenart.blender import site_models as SM
from wenart.blender import site_sense as SS

FLAT = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _inside(p, poly):
    return G.point_in_polygon(p, poly)


# ---------------------------------------------------------------- UL129: stray blocks (a flight under a surface)

def _sunken_and_drive():
    """A pool terrace 0.7 m under a draped drive beside it, its flight up out of it running under the drive (real04's
    sp_002 / spk_001 in small)."""
    terrace = {"id": "t1", "kind": "terrace", "polygon": _rect(0, 0, 4, 6), "holes": [], "z": -0.7, "sloped": False,
               "flight": {"footprint": _rect(4, 2, 5.5, 3.7), "mid": (4.0, 2.85), "out": (1.0, 0.0), "length": 1.5,
                          "half_w": 0.6, "count": 5, "rise": 0.7}}
    drive = {"id": "d1", "kind": "parking", "polygon": _rect(4, -2, 9, 10), "holes": [], "z": 0.0, "sloped": True,
             "edge": "kerb"}
    return terrace, drive


def test_a_flight_up_onto_a_surface_is_cut_into_it():
    terrace, drive = _sunken_and_drive()
    site = {"terrain": FLAT, "platforms": [terrace, drive], "areas": []}
    assert any(f["metrics"]["rule"] == "G8" and "under d1" in f["message"] for f in SS.fragments(site))
    made = S.cut_flights([terrace, drive])
    assert made and drive["cuts"][0]["by"] == "t1" and terrace["flight"]["cut_into"] == ["d1"]
    assert not [f for f in SS.fragments(site) if "under d1" in f["message"]]
    # the drive's paving has a hole where the flight is: no face of its slab lies over the treads
    slab = next(q for q in S.platform_parts(drive, FLAT) if q["part"] == "slab")
    for face in slab["faces"]:
        pts = [slab["verts"][i] for i in face]
        c = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        assert not (4.05 < c[0] < 5.45 and 2.05 < c[1] < 3.65)


def test_no_kerb_between_two_surfaces():
    terrace, drive = _sunken_and_drive()
    gaps = S.kerb_gaps(drive, [terrace])
    assert gaps and all(g[2] - g[1] > 5.0 for g in gaps)          # the 6 m the terrace shares with the drive
    drive["kerb_gaps"] = gaps
    kerb = next(q for q in S.platform_parts(drive, FLAT) if q["part"] == "kerb")
    for k in range(0, len(kerb["verts"]), 8):
        box = kerb["verts"][k:k + 8]
        cx, cy = sum(p[0] for p in box) / 8.0, sum(p[1] for p in box) / 8.0
        assert not (cx < 4.0 and 0.2 < cy < 5.8)                  # no kerb piece on the terrace's side of the edge
    # the review finds a plan that still builds the kerb there
    drive.pop("kerb_gaps")
    site = {"terrain": FLAT, "platforms": [terrace, drive], "areas": []}
    assert any("kerb" in f["message"] for f in SS.fragments(site))


def test_a_path_ends_where_it_arrives_and_never_runs_into_a_building():
    stops = [{"kind": "building", "id": "copy", "polygon": _rect(-2, 8, 6, 14)},
             {"kind": "surface", "id": "drive", "polygon": _rect(-2, 20, 6, 24)}]
    end, stop = S.path_stop((1.0, 0.0), (0.0, 1.0), 0.0, 30.0, 0.6, stops)
    assert stop["id"] == "copy" and 7.0 < end < 8.0               # before the building's wall
    end, stop = S.path_stop((1.0, 15.0), (0.0, 1.0), 0.0, 30.0, 0.6, stops)
    assert stop["id"] == "drive" and abs(end - 5.05) < 0.11       # just inside the drive's edge
    dropped = []
    ents = [{"opening_id": "d1", "outward": (0.0, 1.0), "centre": (1.0, 7.5)}]
    got = S.entrance_paths(ents, {}, _rect(-5, -5, 10, 30), stops=stops, dropped=dropped)
    assert got == [] and dropped and dropped[0]["stop"] == "copy"
    # the review: a path through a building or on under a surface is a stray fragment
    site = {"terrain": FLAT, "platforms": [{"id": "drive", "kind": "parking", "polygon": _rect(-2, 20, 6, 24),
                                            "sloped": True}],
            "copy_holes": [_rect(-2, 8, 6, 14)], "outline": _rect(20, 0, 30, 10),
            "areas": [{"id": "p1", "kind": "path", "polygon": _rect(0.4, 0, 1.6, 23)}]}
    msgs = [f["message"] for f in SS.fragments(site)]
    assert any("runs into building copy 1" in m for m in msgs) and any("under drive" in m for m in msgs)


def test_a_labelled_area_held_by_its_drawn_surface_is_not_lost():
    final = {"site": {"areas": [{"id": "sa_park", "label": "Otopark alani", "kind": "parking", "build": False,
                                 "anchor": [5, 5]},
                                {"id": "sa_pool", "label": "24m2 havuz", "kind": "pool", "build": False,
                                 "anchor": [21, 1]},
                                {"id": "sa_lost", "label": "Veranda", "kind": "terrace", "build": False}],
                      "parking": [{"id": "spk_1", "area_id": "sa_park", "polygon": _rect(0, 0, 3, 3)}],
                      "pools": [{"id": "pool_1", "polygon": _rect(20, 0, 23, 2)}]}}
    assert C.held_by(final, final["site"]["areas"][0]) == "spk_1"
    assert C.held_by(final, final["site"]["areas"][1]) == "pool_1"
    lost = [f["target"] for f in C.untyped(final) if f["check"] == "C5"]
    assert lost == ["sa_lost"]
    assert S.label_holder(final["site"], final["site"]["areas"][0]) == "spk_1"


# ---------------------------------------------------------------- UL129: better cars

def _car(i, model, fa="+X", before="-Y", poly=40000, notes=(), textured=True, status="fix"):
    from wenart.furniture import catalog as CAT
    return {"id": f"car{i}", "type": "car", "title": "Car", "glb": f"c{i}.glb", "front_axis": fa,
            "bbox_model_m": list(model), "bbox_m": CAT.oriented_bbox(list(model), fa), "polycount": poly,
            "textured": textured, "licence_flag": "none",
            "audit": {"status": status, "before": {"front_axis": before}, "notes": list(notes)}}


def test_a_car_front_is_an_end_of_its_length_and_its_size_is_real():
    # real04's 'CAR': model box 2.21 x 5.0 (long along Y), the audit turned its front to +X onto its side
    e = _car(1, (2.208, 4.9986, 1.5218))
    fa, box, note = SM.car_frame(e)
    assert fa == "-Y" and box == [2.208, 4.9986, 1.5218] and "long side" in note
    w, length, h, s = SM.car_size(e)
    assert 4.2 <= length <= 4.9 and w <= SM.CAR_WIDTH_MAX + 1e-9 and 1.25 <= h <= 1.75
    assert abs(w / length - 2.208 / 4.9986) < 1e-6               # uniform: the proportions are the model's
    # a front already on the long side stands
    assert SM.car_frame(_car(2, (4.7, 2.1, 1.4), fa="-X"))[0] == "-X"
    # a limousine, a toy-scale model and a stretched one are no real car
    assert SM.car_size(_car(3, (2.08, 5.64, 1.26))) is None       # 1.10 m high once 4.9 m long
    assert SM.car_size(_car(4, (0.24, 0.51, 0.14))) is None       # broken units: scale 8.5


def test_car_models_are_well_made_and_distinct():
    good = [_car(1, (2.12, 4.70, 1.42)), _car(2, (2.21, 5.0, 1.52), poly=79000), _car(3, (2.18, 5.29, 1.53), poly=16000)]
    poor = [_car(4, (2.1, 4.6, 1.4), poly=4000), _car(5, (2.1, 4.6, 1.4), notes=["largest texture 64 px (< 512)"]),
            _car(6, (2.1, 4.6, 1.4), textured=False)]
    got = SM.car_models(good + poor)
    assert [c["asset"]["asset_id"] for c in got] == ["car1", "car2", "car3"]
    assert all(c["asset"]["front_axis"] == "-Y" and c["asset"]["scaling"] == "uniform" for c in got)
    assert not SM.car_quality(poor[0])[0] and "toy" in SM.car_quality(poor[1])[1]


def test_car_bays_line_an_l_shaped_parking_near_its_label_clear_of_the_flights():
    lot = [(0, 0), (5, 0), (5, 30), (25, 30), (25, 35), (0, 35)]         # an L: a 5 m strip and a 5 m strip
    keep = [_rect(0, 10, 2.5, 13)]                                      # a flight cut into the strip
    slots = SM.car_slots(lot, anchor=(2.5, 12.0), keep_out=keep)
    assert len(slots) == SM.MAX_CARS
    for s in slots:
        assert _inside(tuple(s["center"]), lot)
        ang = math.radians(s["rotation_deg"])
        front = (math.sin(ang), -math.cos(ang))                         # the car's -Y turned by the rotation
        along = s["bay"][0] if s["layout"] == "parallel" else s["bay"][1]
        if s["layout"] == "parallel":                                    # parked in the bay's direction
            assert abs(abs(front[1]) - 1.0) < 1e-6 or abs(abs(front[0]) - 1.0) < 1e-6
        assert along > 0
        assert not _inside(tuple(s["center"]), keep[0])
    near = min(G.distance(tuple(s["center"]), (2.5, 12.0)) for s in slots)
    assert near < 6.0                                                     # the first bay by the drawn label


def test_site_library_models_are_credited(tmp_path):
    import json

    from wenart.run import copy as CP
    (tmp_path / "scene").mkdir()
    (tmp_path / "scene" / "scene_manifest.json").write_text(json.dumps({"objects": [
        {"name": "car_spk_1_0", "element_id": "car_spk_1_0", "site_part": "car", "veg_method": "library",
         "asset": "3dwh_867427c8bc03ecda3fbb809a"}]}), encoding="utf-8")
    rows = [r for r in CP.vegetation_credits(tmp_path) if r["asset_id"] == "3dwh_867427c8bc03ecda3fbb809a"]
    assert rows and rows[0]["kind"] == "model" and rows[0]["pieces"] == [("car_spk_1_0", "car")]
    assert "CAR" in rows[0]["credit"] and rows[0]["licence_flag"] == "non_commercial"


def test_the_audit_never_turns_a_cars_front_onto_its_side():
    e = {"type": "car", "front_axis": "-Y", "bbox_model_m": [2.2, 5.0, 1.5]}
    assert not AW.end_front_turn_ok(e, 1) and AW.end_front_turn_ok(e, 2)
    assert AW.end_front_turn_ok({"type": "sofa", "front_axis": "-Y", "bbox_model_m": [2.2, 0.9, 0.8]}, 1)
    e2 = {"id": "c", "type": "car", "front_axis": "-Y", "bbox_model_m": [2.2, 5.0, 1.5], "bbox_m": [2.2, 5.0, 1.5]}
    AW.fix_entry(e2, {"front_quarter_turns": 1})
    assert e2["front_axis"] == "-Y" and "refused" in e2["front_axis_note"]


# ---------------------------------------------------------------- UL141: a flight never meets a wall or a block

def _terrace_by_plot_edge():
    """A terrace 1.0 m over flat ground, its flight down on its west edge ending 0.2 m from the plot edge, a path to
    the north (real04's sp_001 and its access path in small)."""
    pf = {"id": "t1", "kind": "terrace", "polygon": [(0, 0), (4, 0), (4, 4), (0, 4)], "holes": [], "z": 1.0,
          "sloped": False, "steps_edge": 3, "edge": "steps", "pools": []}
    fl = GR.down_flight(pf, lambda x, y: 0.0)
    plot_x = fl["mid"][0] + fl["out"][0] * (fl["end"] + GR.GRADE["foot_m"]) - 0.2
    site = {"terrain": FLAT, "platforms": [pf], "outline": _rect(10, 0, 20, 10), "copy_holes": [], "pools": [],
            "wells": [], "plot": _rect(plot_x, -10, 30, 30),
            "areas": [{"id": "p0", "kind": "path", "polygon": _rect(plot_x + 0.1, 8.0, plot_x + 1.3, 16.0)}]}
    return site, pf, fl


def test_the_path_from_a_flight_leaves_its_foot_landing_by_an_open_side():
    site, pf, fl = _terrace_by_plot_edge()
    areas = AR.outside_access(pf, site)
    assert areas, "a path from the flight's foot landing to the site's path"
    assert pf["foot_open"] in ("left", "right")
    fl2 = GR.down_flight(pf, lambda x, y: 0.0)
    assert len(fl2["cheeks"]) == len(fl["cheeks"]) - 1             # the foot landing's cheek on the path's side
    site["areas"] += areas
    assert not [f for f in SS.flights_meet(site) if "cheek" in f["message"]]
    # the old layout: the path laid over the foot landing, its first steps cut by the cheek wall
    pf.pop("foot_open")
    foot = fl["foot"]
    xs, ys = [p[0] for p in foot], [p[1] for p in foot]
    site["areas"] = [{"id": "p_old", "kind": "path", "polygon": _rect(min(xs), min(ys) + 0.3, max(xs), 9.0)}]
    msgs = [f["message"] for f in SS.flights_meet(site)]
    assert any("cheek wall of the flight of t1" in m for m in msgs)


# ---------------------------------------------------------------- UL144: one continuous handrail

def _stair():
    area = {"id": "st", "kind": "path", "polygon": _rect(0, 0, 12, 1.2)}
    gz = (lambda x, y: 0.28 * x)
    rec = GR.path_plan(area, gz)
    assert rec["kind"] == "stepped" and rec["handrails"] and len(rec["flights"]) >= 2
    return rec, gz


def test_an_outdoor_stair_has_one_continuous_handrail_on_its_steps():
    rec, gz = _stair()
    rail = GR.stair_rail(rec, gz)
    assert rail is not None and rail["flights"] == len(rec["flights"])
    ts = [p[0] for p in rail["points"]]
    assert ts == sorted(ts)                                         # one polyline along the stair
    nos = rail["nosings"]
    # 0.9 m over the first and the last nosing, reaching 0.3 m past them
    assert abs(rail["t_range"][0] - (nos[0][0] - 0.3)) < 1e-6 or rail["t_range"][0] == 0.02
    assert abs(rail["t_range"][1] - (nos[-1][0] + 0.3)) < 1e-6 or abs(rail["t_range"][1] - (12 - 0.02)) < 1e-6
    assert abs(rail["points"][1][2] - (nos[0][1] + 0.9)) < 1e-6
    # posts at most 1.4 m apart, each standing on the path's treads
    assert rail["spacing_m"] <= GR.RAIL["post_max_m"] + 1e-6 and len(rail["posts"]) >= 3
    for foot, top in rail["posts"]:
        assert 0.0 <= foot[1] <= 1.2 and 0.0 <= foot[0] <= 12.0
        assert 0.85 <= top[2] - foot[2] <= 0.9 + 0.2
    meshes = GR.path_meshes(rec, gz, 0.3)
    assert len(meshes["rail"]) == len(rail["points"]) - 1 + len(rail["posts"])
    assert not SS.rails({"terrain": FLAT, "areas": [], "platforms": []}, None)


def test_the_review_finds_rails_built_flight_by_flight():
    manifest = {"site": {"paths": [{"id": "path_x", "kind": "stepped", "handrails": True}]}}
    got = SS.rails({"terrain": FLAT, "areas": [], "platforms": []}, manifest)
    assert got and got[0]["metrics"]["rule"] == "G10"


# ---------------------------------------------------------------- UL143: a ladder and seating at every pool

def _pool_site(deck_poly):
    pool = {"id": "pool_1", "polygon": _rect(2, 2, 5, 10), "depth": 1.5}
    deck = {"id": "d1", "kind": "terrace", "polygon": deck_poly, "holes": [pool["polygon"]], "z": 0.0,
            "pools": ["pool_1"], "sloped": False}
    return {"terrain": FLAT, "pools": [pool], "platforms": [deck], "outline": _rect(14, 0, 24, 12), "copy_holes": [],
            "areas": []}


def test_every_pool_gets_a_ladder_and_seating_facing_the_water():
    site = _pool_site(_rect(0, 0, 10, 12))
    rec = PX.plan(site)[0]
    lad, seat = rec["ladder"], rec["seating"]
    assert lad and lad["long_side"] and lad["edge"] in (1, 3)
    assert seat and seat["set"] == "loungers" and [p["type"] for p in seat["pieces"]] == \
        ["sun_lounger", "side_table", "sun_lounger"]
    for p in seat["pieces"]:
        c = tuple(p["center"])
        # facing the water: the front points at the pool; a free walkway along the coping
        f = math.radians(p["front_deg"])
        ahead = (c[0] + math.cos(f) * 3.0, c[1] + math.sin(f) * 3.0)
        assert _inside(ahead, _rect(2, 2, 5, 10))
        gap = min(abs(c[0] - 5.0), abs(c[0] - 2.0)) - p["size"][1] / 2.0
        assert gap >= S.POOL_COPING_M + PX.WALKWAY_M - 1e-6 or p["type"] == "side_table"
    m = PX.ladder_meshes(lad)
    assert len(m["treads"]) == PX.LADDER["treads"] and m["rails"]
    zs = [v[2] for verts, _f in m["rails"] for v in verts]
    assert max(zs) > 0.8 and min(zs) < -0.9                        # over the coping and down into the water
    parts = PX.seat_meshes(seat["pieces"][0], 0.0)
    top = max(v[2] for verts, _f in parts["cushion"] for v in verts)
    assert 0.35 < top < 0.9


def test_a_narrow_deck_gets_a_pair_of_lounge_chairs_and_the_review_finds_bare_pools():
    site = _pool_site(_rect(0, 0, 7.6, 12))                        # 2.6 m of deck beside the pool's long side
    rec = PX.plan(site)[0]
    assert rec["seating"] and rec["seating"]["set"] == "chairs"
    got, n = PX.review(site, {"objects": []})
    assert n == 1 and {f["metrics"]["rule"] for f in got} == {"G11"} and len(got) == 2
    objs = [{"site_part": "pool_ladder", "pool_id": "pool_1"}, {"site_part": "pool_seat", "pool_id": "pool_1"}]
    assert PX.review(site, {"objects": objs}) == ([], 1)


def test_the_build_records_every_pool_piece_as_added_by_ai(monkeypatch):
    from wenart.blender import common

    made = []
    monkeypatch.setattr(common, "new_mesh_object", lambda name, v, f, **kw: made.append((name, len(f), kw)))
    monkeypatch.setattr(PX, "library_entries", lambda: [])         # no library model: the parametric pieces
    site = _pool_site(_rect(0, 0, 10, 12))
    objs, assumed = [], []
    out = S.build_pool_extras(site, None, lambda look: look["material"], objs, assumed)
    names = [m[0] for m in made]
    assert names == ["pool_1_ladder", "pool_1_sun_lounger_0", "pool_1_side_table_1", "pool_1_sun_lounger_2"]
    assert all(n > 0 for _name, n, _kw in made)
    assert {o["site_part"] for o in objs} == {"pool_ladder", "pool_seat"}
    assert all(o["pool_id"] == "pool_1" and o["source"] == "added_by_ai" and o["inferred"] for o in objs)
    assert any("library gap" in o["reason"] for o in objs if o["site_part"] == "pool_seat")
    assert len(out) == 4 and len(assumed) == 4
    # and the review of that scene finds the pool furnished
    assert PX.review(site, {"objects": objs}) == ([], 1)


# ---------------------------------------------------------------- UL142: the apron runs the whole glazing run

def test_a_light_wells_paving_runs_the_whole_glazed_facade():
    building = {"walls": [{"id": "w1", "level_id": "L0", "start": [0, 0], "end": [16, 0], "thickness": 0.2}],
                "openings": [{"id": "win_a", "type": "window", "wall_id": "w1", "level_id": "L0", "center": [3.8, 0],
                              "width": 7.0},
                             {"id": "win_b", "type": "window", "wall_id": "w1", "level_id": "L0", "center": [11.4, 0],
                              "width": 7.0}]}
    levels = [{"id": "L0", "elevation": 0.0}]
    outline = _rect(0, 0, 16, 12)
    well = {"opening_id": "win_b", "polygon": [(7.7, -0.9), (15.1, -0.9), (15.1, -0.1), (7.7, -0.1)],
            "outward": [0.0, -1.0], "source": "assumed"}
    aprons, runs = S.facade_aprons(building, levels, outline, None, [well])
    assert len(aprons) == 1 and aprons[0]["opening_ids"] == ["win_a"]
    xs = [p[0] for p in aprons[0]["polygon"]]
    assert min(xs) <= 0.1 and abs(max(xs) - 7.7) < 1e-6            # from the run's end to the well, no lawn between
    assert runs[0]["covered_ids"] == ["win_a", "win_b"]
    assert not SS.aprons({"glazing_runs": runs})
    # a platform in front of a window covers it; the review finds a run the plan left uncovered
    pf = {"id": "t", "polygon": _rect(-1, -3, 4, 0.0)}
    aprons2, runs2 = S.facade_aprons(building, levels, outline, None, [well], [pf])
    assert min(p[0] for p in aprons2[0]["polygon"]) >= 4.0 - S.APRON["piece_m"]
    assert SS.aprons({"glazing_runs": [{"well": "win_b", "run_ids": ["win_a", "win_b"], "covered_ids": ["win_b"]}]})
