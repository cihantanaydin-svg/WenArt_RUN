"""The garden on a slope as a landscape architect lays it out, and the outdoor floors as a designed set (28 Oct 2026).

User, on real04 run 20261028-005318-full: "There could be better outside solutions to the grade slope" (bare concrete
box planters stacked like stairs, steps cutting through boxes, a tilted paved ramp running diagonally down the slope
with a strip of lawn inside it, grey retaining walls), "Better solutions needed for the elevation difference outside"
(a bare concrete retaining box beside the terrace with loose bars lying across the grass like floating step treads) and
"I am not liking this is the only outside flooring" (the garden path, the entrance steps, the terraces and the drive
all in one large grey slab with mossy joints). wenart/blender/grading.py holds the general rules; these tests run them
on synthetic slopes (the rules) and on the committed real04 building (the case that showed the problem)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender import grading as GR
from wenart.blender import site as S
from wenart.levels import terrain as T

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_final.json"


def _planar(a: float, b: float, c: float = 0.0, r: float = 40.0) -> dict:
    """A planar ground surface z = a x + b y + c (fit through four far points)."""
    return T.fit_surface([(x, y, a * x + b * y + c) for x, y in ((-r, -r), (r, -r), (r, r), (-r, r))])


def _site(surface: dict, paving: list, marks: list = (), plot=None) -> dict:
    site = {"ground": {"surface": surface, "points": list(marks), "levels": []}, "paving": paving, "parking": [],
            "pools": []}
    if plot is not None:
        site["plot"] = {"polygon": [list(p) for p in plot], "source": "test"}
    return site


def _terrain(surface: dict) -> dict:
    return {"kind": "planar", "surface": surface, "z": {}, "rect": [-10, -10, 10, 10]}


# --------------------------------------------------------------------------
# Terraces: one level per tier along a side, planted, closed ends
# --------------------------------------------------------------------------

def test_run_steps_give_every_edge_of_a_run_the_run_s_step():
    excess = [("down", 2.0), ("down", 1.3), None, ("up", 1.5), ("up", 1.4), ("down", 1.9)]
    st = GR.run_steps(excess, 1.2)
    # the run wraps from the last edge to the first: edges 5, 0, 1 (down), 2.0 m over ceil(2.0 / 1.2) = 2 tiers
    assert st[5] == st[0] == st[1] == pytest.approx(1.0)
    assert st[3] == st[4] == pytest.approx(0.75)                  # the up run: 1.5 over 2
    assert 2 not in st
    assert GR.run_steps([None, None], 1.2) == {} and GR.run_steps([], 1.2) == {}
    assert GR.run_steps([("down", 1.5)] * 4, 1.2) == {i: pytest.approx(0.75) for i in range(4)}   # all around


def test_the_tiers_of_one_side_share_their_levels_close_their_ends_and_are_planted():
    """real04 sp_001's west side stepped in six bands at six levels (-3.66 .. -4.16 m, a staircase of boxes); a side
    whose ground falls along it now steps in continuous tiers, one level per tier, every band end with no band of its
    level beyond it walled, every tier planted."""
    surface = _planar(0.4, 0.15)                                 # falls to -x and to -y
    site = _site(surface, [{"id": "t1", "polygon": [[-3, -6], [3, -6], [3, 6], [-3, 6]], "build": True}])
    pfs = S.platforms(site)
    t1 = next(p for p in pfs if p["id"] == "t1")
    bands = [p for p in pfs if p.get("parent") == "t1"]
    down = [b for b in bands if b["stepped_from"]["direction"] == "down"]
    assert len(down) >= 4
    for k in {b["step"] for b in down}:
        assert len({b["z"] for b in down if b["step"] == k}) == 1, k          # one level per tier
    assert all(st["step_m"] <= S.RETAINING_MAX_M + 1e-9 and st["run_level"] for st in t1["stepped"])
    # every open (shared) band end has a band of its level beyond it; the others got their walls (closed_ends)
    for b in bands:
        poly = b["polygon"]
        for j in b["shared_edges"]:
            if j == b["inner_edge"]:
                continue
            a, c = poly[j], poly[(j + 1) % len(poly)]
            length = G.distance(a, c)
            m = G.segment_midpoint(a, c)
            probe = (m[0] + (c[1] - a[1]) / length * 0.05, m[1] - (c[0] - a[0]) / length * 0.05)
            assert any(o is not b and abs(o["z"] - b["z"]) <= S.PLATFORM["level_tol"]
                       and G.point_in_polygon(probe, o["polygon"]) for o in bands), (b["id"], j)
    assert any(b.get("closed_ends") for b in bands)
    # planted beds: a shrub along the middle of every tier, clear of the given footprints
    plants = GR.tier_plants(pfs, avoid=[])
    assert plants and all(b.get("planting", {}).get("plants") for b in bands)
    assert all(p["kind"] == "plant" and p["inferred"] and p["source"] == "planting_bed" for p in plants)
    for p in plants:
        host = next(b for b in bands if b["id"] == p["parent"])
        assert G.point_in_polygon(p["center"], host["polygon"])
    # a drawn shrub on a tier plants it: no inferred plant needed there
    b0 = bands[0]
    drawn = {"id": "sd_1", "kind": "tree", "center": list(G.polygon_centroid(b0["polygon"])), "size": [0.7, 0.7]}
    assert GR.drawn_on(b0, [drawn]) == ["sd_1"]
    GR.tier_plants(pfs, avoid=[], existing=[drawn])
    assert "sd_1" in b0["planting"]["plants"] and b0["planting"]["drawn"] == ["sd_1"]


# --------------------------------------------------------------------------
# Flights: solid treads that land on the ground, cheek walls, a hole in the lawn
# --------------------------------------------------------------------------

def _raised_terrace(surface, z: float = 0.0):
    site = _site(surface, [{"id": "t1", "polygon": [[-3, -2], [3, -2], [3, 2], [-3, 2]], "build": True}],
                 marks=[{"x": 0.0, "y": 0.0, "z": z, "kind": "ground_finished", "mark_id": "lm"}])
    pfs = S.platforms(site)
    return site, pfs, next(p for p in pfs if p["id"] == "t1")


def test_a_flight_down_lands_on_the_ground_with_solid_treads_cheeks_and_a_hole():
    """real04's flights on sp_001 / sp_004 ran ceil(drop / 0.16) treads straight out from the edge's lowest ground:
    every tread lay 5-23 cm under the cross-falling ground (loose bars in the grass). The flight now runs out until its
    last riser lands on the highest ground under its foot landing, risers by the levels' outdoor rule."""
    surface = _planar(0.06, -0.2)                              # falls away to +y (the flight's way) and across
    terrain = _terrain(surface)
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    site, pfs, t1 = _raised_terrace(surface)
    assert t1["steps_edge"] is not None and t1.get("steps_dir") != "up"
    fl = GR.down_flight(t1, gz)
    rules = GR.level_rules()
    assert fl["riser"] <= float(rules["riser_max_outdoor"]) + 1e-6
    assert fl["count"] * fl["riser"] == pytest.approx(fl["rise"], abs=2e-3)
    assert fl["rise"] == pytest.approx(t1["z"] - fl["foot_z"], abs=2e-3)
    # the foot landing never lies under the lawn; every cheek stands over the ground beside it
    assert max(gz(*q) for q in fl["foot"]) <= fl["foot_z"] + 1e-3
    assert all(c["z_top"] >= c["ground_max"] + GR.GRADE["cheek_over_ground_m"] - 1e-3 for c in fl["cheeks"])
    # the old straight flight (ceil(edge drop / 0.16) treads of 0.30 m) ended over falling ground: this one is longer
    i = t1["steps_edge"]
    old_count = max(1, math.ceil(t1["edge_drops"][i] / S.PLATFORM["step_rise"] - 1e-9))
    assert fl["end"] + GR.GRADE["foot_m"] > old_count * S.PLATFORM["step_tread"]
    # as built: solid blocks from under the ground, the footprint a hole in the ground mesh, no finding
    fm = GR.flight_meshes(fl, gz, S.PLATFORM["below"])
    assert fm["treads"] and all(r["z_bottom"] <= r["ground_min"] + 1e-6 for r in fm["treads"])
    plan = {"outline": [(20, 20), (21, 20), (21, 21)], "wells": [], "copy_holes": [], "pools": [], "platforms": pfs,
            "terrain": terrain, "areas": []}
    holes = S.ground_holes(plan)
    assert any(GR._same(fl["footprint"], h) for h in holes)
    assert GR.tread_findings("f", "t1", fm["treads"], True) == []
    # the platform's parts: the steps edge's wall leaves the flight's place free; every wall has its coping
    parts = {q["part"]: q for q in S.platform_parts(t1, terrain)}
    assert parts["steps"]["treads"] and "coping" in parts and "wall" in parts
    # the edge's wall stands in two stretches beside the flight (the second stretch's pieces numbered from 100)
    walls_on_edge = [w for w in parts["wall"]["walls"] if w["edge"] == i]
    assert walls_on_edge and any(w["piece"] >= 100 for w in walls_on_edge)


def test_tread_findings_find_loose_and_floating_treads():
    buried = [{"z_top": -3.12, "z_bottom": -3.67, "ground_min": -3.37, "ground_max": -3.07}]
    got = GR.tread_findings("the flight on sp_001 edge 4", "sp_001", buried, in_hole=False)
    assert len(got) == 1 and got[0]["check"] == "M15" and got[0]["metrics"]["rule"] == "G2"
    assert "loose tread in the grass" in got[0]["message"] and got[0]["kind"] == "geometry"
    assert GR.tread_findings("f", "x", buried, in_hole=True) == []          # a hole with cheek walls holds the ground
    floating = [{"z_top": 0.3, "z_bottom": 0.2, "ground_min": 0.0, "ground_max": 0.05}]
    assert "floats over the ground" in GR.tread_findings("f", "x", floating, in_hole=True)[0]["message"]


def test_the_architect_s_access_steps_never_run_through_another_platform():
    """A2's new flight down to the garden (architect.access_edge) takes no edge whose flight would run into another
    platform, a band or a hedge."""
    from wenart.blender import architect as AR

    flat = T.fit_surface([(-40, -40, 0.0), (40, -40, 0.0), (40, 40, 0.0), (-40, 40, 0.0)])
    site = _site(flat, [{"id": "t1", "polygon": [[0, 0], [6, 0], [6, 3], [0, 3]], "build": True},
                        {"id": "t2", "polygon": [[0, -3.0], [6, -3.0], [6, -0.5], [0, -0.5]], "build": True}],
                 marks=[{"x": 3.0, "y": 1.5, "z": 0.6, "kind": "ground_finished", "mark_id": "lm"}])
    pfs = S.platforms(site)
    t1 = next(p for p in pfs if p["id"] == "t1")
    plan = {"terrain": _terrain(flat), "platforms": pfs, "hedges": []}
    i = AR.access_edge(t1, plan)
    assert i is not None
    fl = GR.down_flight(dict(t1, steps_edge=i, steps_dir=None), lambda x, y: 0.0)
    t2 = next(p for p in pfs if p["id"] == "t2")
    assert fl is None or not S.convex_overlap(fl["footprint"], t2["polygon"], tol=0.01)
    # without the plan the old choice may face t2 (the smallest drop, then the longest edge)
    assert AR.access_edge(t1) is not None


def test_the_terraces_keep_out_of_their_own_flight():
    """No steps through a planter: the platform's own flight is a keep-out of its bands."""
    surface = _planar(0.45, 0.0)
    site = _site(surface, [{"id": "t1", "polygon": [[-3, -3], [3, -3], [3, 3], [-3, 3]], "build": True}])
    pfs = S.platforms(site)
    terrain = _terrain(surface)
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    for pf in (p for p in pfs if not p.get("parent")):
        fl = GR.down_flight(pf, gz)
        if fl is None:
            continue
        for b in (q for q in pfs if q.get("parent") == pf["id"]):
            assert not S.convex_overlap(fl["footprint"], b["polygon"], tol=0.01), b["id"]


# --------------------------------------------------------------------------
# Banks: the ground graded to the terrace at the natural angle of its finish
# --------------------------------------------------------------------------

def test_a_raised_terrace_with_room_meets_the_ground_by_banks_not_walls():
    surface = _planar(0.05, 0.0)                               # a gentle 1:20 slope
    plot = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
    site = _site(surface, [{"id": "t1", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]], "build": True}],
                 marks=[{"x": 3.0, "y": 2.0, "z": 0.6, "kind": "ground_finished", "mark_id": "lm"}], plot=plot)
    pfs = S.platforms(site)
    t1 = next(p for p in pfs if p["id"] == "t1")
    banks = t1["embankments"]
    assert banks and all(e["finish"] == "lawn" and e["slope"] == pytest.approx(1.0 / 3.0) for e in banks)
    assert t1["steps_edge"] not in {e["edge"] for e in banks}               # the flight keeps its edge
    terrain = GR.graded_terrain(_terrain(surface), pfs)
    natural = _terrain(surface)
    assert terrain["grading"] and "grading" not in natural
    for e in banks:
        ax, ay = e["a"]
        ux, uy = e["u"]
        nx, ny = e["n"]
        mid = (ax + ux * e["length_m"] / 2.0, ay + uy * e["length_m"] / 2.0)
        assert S.ground_z(terrain, mid[0] + nx * 0.01, mid[1] + ny * 0.01) == pytest.approx(t1["z"], abs=0.01)
        for d in (0.3, 0.6, 0.9):                             # never steeper than 1:3 from the edge to the toe
            z0 = S.ground_z(terrain, mid[0] + nx * d, mid[1] + ny * d)
            z1 = S.ground_z(terrain, mid[0] + nx * (d + 0.3), mid[1] + ny * (d + 0.3))
            assert abs(z1 - z0) / 0.3 <= 1.0 / 3.0 + 1e-6
        far = (mid[0] + nx * (e["width_m"] + 0.5), mid[1] + ny * (e["width_m"] + 0.5))
        assert S.ground_z(terrain, *far) == pytest.approx(S.ground_z(natural, *far), abs=1e-6)   # the natural ground
        assert e["edge"] not in t1["railing_edges"] and "inferred" in e["reason"]
    # no wall on a banked edge (the walls measured on the graded ground); the wing walls hold the ends without a cone
    walls = S.platform_wall_edges(t1, lambda x, y: S.ground_z(terrain, x, y))
    assert not set(walls) & {e["edge"] for e in banks if e["length_m"] >= e["edge_length_m"] - 1e-6}
    wings = GR.wing_walls(t1, lambda x, y: S.ground_z(natural, x, y), lambda x, y: S.ground_z(terrain, x, y))
    assert all(w["height_m"] <= GR.GRADE["embank_max_m"] + 0.05 for w in wings)
    # the zones are what a path keeps out of (architect.site_keep_out)
    zones = GR.bank_zones(terrain)
    assert len(zones) == len(banks) and all(G.polygon_area(z) > 0.1 for z in zones)


def test_no_bank_where_there_is_no_room_the_slope_is_too_steep_or_the_edge_is_asked_a_guard():
    marks = [{"x": 3.0, "y": 2.0, "z": 0.6, "kind": "ground_finished", "mark_id": "lm"}]
    poly = [[0, 0], [6, 0], [6, 4], [0, 4]]
    # the plot ends 0.5 m beyond the terrace: no bank fits inside it (nor the way past it)
    tight = _site(_planar(0.05, 0.0), [{"id": "t1", "polygon": poly, "build": True}], marks=marks,
                  plot=[(-0.5, -0.5), (6.5, -0.5), (6.5, 4.5), (-0.5, 4.5)])
    assert next(p for p in S.platforms(tight) if p["id"] == "t1")["embankments"] == []
    # the house beside the terrace: no bank within embank_facade_m of it
    site = _site(_planar(0.05, 0.0), [{"id": "t1", "polygon": poly, "build": True}], marks=marks)
    house = [(6.2, -5), (16, -5), (16, 9), (6.2, 9)]
    t1 = next(p for p in S.platforms(site, keep_out=[house]) if p["id"] == "t1")
    assert all(G.point_in_polygon(e["a"], house) is False for e in t1["embankments"])
    east = [e for e in t1["embankments"] if abs(e["n"][0] - 1.0) < 1e-6]
    assert east == []
    # the ground falls away as steeply as a bank would (1:2.2): no lawn or planted bank on the downhill side
    steep = _site(_planar(0.45, 0.0), [{"id": "t1", "polygon": poly, "build": True}],
                  marks=[{"x": 3.0, "y": 2.0, "z": 1.0, "kind": "ground_finished", "mark_id": "lm"}])
    t1 = next(p for p in S.platforms(steep) if p["id"] == "t1")
    assert not [e for e in t1["embankments"] if e["n"][0] < -0.9]
    # a labelled outdoor space keeps its built base (a veranda is no garden bank)
    assert GR.plan_embankments([dict(next(p for p in S.platforms(site) if p["id"] == "t1"), source="outdoor_space")],
                               lambda x, y: 0.05 * x) == []


# --------------------------------------------------------------------------
# Paths: level across; a walk, a sloped walk, a stepped path, a ramp only on an accessible route
# --------------------------------------------------------------------------

def _strip(x0, x1, y0=0.0, w=1.2):
    return [[x0, y0 - w / 2], [x1, y0 - w / 2], [x1, y0 + w / 2], [x0, y0 + w / 2]]


def test_a_path_on_the_flat_is_a_walk_with_an_edging_and_a_steep_one_is_stepped_level_across():
    flat = {"id": "p_flat", "kind": "path", "polygon": _strip(0, 10)}
    rec = GR.path_plan(flat, lambda x, y: 0.0)
    assert not rec["graded"] and rec["kind"] == "walk"
    assert len(GR.walk_edging(flat, lambda x, y: 0.0)) == 2 * 5                       # both sides, 2 m pieces
    gentle = GR.path_plan({"id": "p_g", "kind": "path", "polygon": _strip(0, 10)}, lambda x, y: x / 15.0)
    assert gentle["graded"] and gentle["kind"] == "sloped_walk"
    assert all(abs(s["z1"] - s["z0"]) / (s["t1"] - s["t0"]) <= 1.0 / 12.0 + 1e-6 for s in gentle["slices"])
    # 25 % along and 30 % across (real04's path_access_sp_001_1: 25 % with a 31 % cross fall)
    gz = (lambda x, y: 0.25 * x + 0.3 * y)
    steep = {"id": "p_s", "kind": "path", "polygon": _strip(0, 11.5)}
    rec = GR.path_plan(steep, gz)
    rules = GR.level_rules()
    assert rec["graded"] and rec["kind"] == "stepped"
    assert rec["riser"] <= float(rules["riser_max_outdoor"]) + 1e-6 and rec["tread"] >= GR.GRADE["garden_tread_m"] - 1e-9
    assert all(2 <= k <= int(rules["landing_every_risers"]) for k in rec["flights"])
    landings = [s for s in rec["slices"] if s["kind"] == "landing"][1:-1]
    assert landings and all(s["t1"] - s["t0"] >= GR.GRADE["landing_min_m"] - 1e-6 for s in landings)
    assert all(s["z0"] == s["z1"] for s in rec["slices"])                              # every slice level
    zs = [s["z0"] for s in rec["slices"]]
    assert zs == sorted(zs) and zs[-1] - zs[0] == pytest.approx(rec["rise"], abs=0.02)
    meshes = GR.path_meshes(rec, gz, S.PLATFORM["below"])
    risers = sum(1 for s in rec["slices"] if s["riser"] or s.get("riser_end"))
    assert len(meshes["step_edge"]) == risers
    assert meshes["edge_wall"] and meshes["edging"]                  # the uphill side held, the downhill side edged
    assert meshes["rail"] if any(k * rec["riser"] > float(rules["handrail_from"]) for k in rec["flights"]) else True
    assert all(r["z_bottom"] <= r["ground_max"] for r in meshes["records"])
    # the same strip drawn the other way round is the same path (from its lower end)
    back = GR.path_plan({"id": "p_b", "kind": "path", "polygon": _strip(0, 11.5)}, lambda x, y: -0.25 * x)
    assert back["kind"] == "stepped" and back["slices"][0]["z0"] > back["slices"][-1]["z0"]


def test_a_ramp_only_on_an_accessible_route_and_within_the_ramp_rule():
    gz = (lambda x, y: 0.06 * x)                                  # 6 % along, 0.6 m over 10 m
    area = {"id": "path_d1", "kind": "path", "polygon": _strip(0, 10)}
    assert GR.path_plan(area, gz)["kind"] == "sloped_walk"                   # no accessibility asked: a garden walk
    ramp = GR.path_plan(area, gz, accessible=True)
    assert ramp["kind"] == "ramp" and ramp["handrails"] and ramp["slope"] <= 0.0625 + 1e-6
    plan = {"inferred": {"steps": [{"opening_id": "d1", "doors": ["d1"], "ramp": {"polygon": []}}],
                         "paths": [{"opening_ids": ["d1"]}]}}
    assert GR.accessible_paths(plan) == {"path_d1"}
    steep = GR.path_plan(area, lambda x, y: 0.2 * x, accessible=True)        # too steep for a straight ramp
    assert steep["kind"] == "stepped" and "ramp needs" in steep["accessible_open"]


# --------------------------------------------------------------------------
# Looks: walls in the house's base stone; floors by use and style
# --------------------------------------------------------------------------

def test_walls_take_the_house_s_base_stone_and_floors_differ_by_use():
    from wenart.blender import facade as FA
    from wenart.blender import materials as M

    for fam in list(FA.FACADE_SCHEMES) + [None]:
        wl = GR.wall_look({}, fam)
        assert wl["material"] not in GR.CONCRETE_SLUGS and wl["assumed"] and "inferred" in wl["reason"]
    b = {"levels": [{"id": "L-1", "elevation": -3.0}, {"id": "L0", "elevation": 0.0}],
         "facade": {"faces": [{"material": "brick_red", "level_id": "L-1", "source": "drawn"}]}}
    assert GR.wall_look(b, "modern")["material"] == "brick_red" and GR.wall_look(b)["source"] == "documents"
    for fam in GR.FLOOR_SETS:
        fs = GR.floor_set(None, fam)
        slugs = {fs[u]["material"] for u in ("terrace", "steps", "path", "drive")}
        assert len(slugs) >= 2 and fs["path"]["material"] != fs["terrace"]["material"], fam
        assert "paving" not in (fs["terrace"]["material"], fs["path"]["material"], fs["steps"]["material"])
        for u in GR.FLOOR_USES:
            assert M.ENTRIES.get(fs[u]["material"]), (fam, u, fs[u]["material"])
    named = GR.floor_set({"paving": {"material": "travertine", "source": "brief", "assumed": False}}, "modern")
    assert named["terrace"]["material"] == named["steps"]["material"] == "travertine"
    assert named["path"]["material"] == "gravel" and named["drive"]["material"] == "paving"
    assert GR.slab_use({"kind": "terrace", "pools": ["p"]}) == "pool_deck" and GR.slab_use({"kind": "parking"}) == "drive"
    # the assets stage fetches the family's floors (exterior.build_finish_slugs)
    from wenart.blender import exterior as E
    slugs = {s for s, _part in E.build_finish_slugs({"family": "mediterranean"})}
    assert {"travertine", "terracotta", "paving_stone"} <= slugs


# --------------------------------------------------------------------------
# The check (model review M15) and the architect's G2 / G3
# --------------------------------------------------------------------------

def test_the_review_finds_crude_grading():
    """M15 finds what the user saw: tiers side by side at different levels with nothing planted, bare concrete walls,
    a bank steeper than its finish, a path draped on a slope, one floor look everywhere."""
    surface = _planar(0.0, 0.0)
    terrain = dict(_terrain(surface), grading=[{"a": (0, 0), "u": (1, 0), "n": (0, -1), "length_m": 3.0,
                                               "width_m": 1.0, "z_top": 0.5, "slope": 0.6, "fill": True,
                                               "cone_a": False, "cone_b": False, "platform": "t1", "edge": 0,
                                               "finish": "lawn"}])
    band = {"parent": "t1", "step": 1, "kind": "terrace", "stepped_from": {"direction": "down"}, "sloped": False,
            "holes": [], "pools": []}
    site = {"terrain": terrain, "outline": [(30, 30), (31, 30), (31, 31)], "wells": [], "copy_holes": [], "pools": [],
            "hedges": [], "trees": [], "wall_look": {"material": "concrete_exposed"},
            "platforms": [dict(band, id="t1_s1e0", z=-1.0, polygon=[(0, -1), (3, -1), (3, 0), (0, 0)]),
                          dict(band, id="t1_s1e1", z=-1.3, polygon=[(3, -1), (6, -1), (6, 0), (3, 0)])],
            "areas": [{"id": "p1", "kind": "path", "polygon": [(10, 0), (14, 0), (15, 2), (12, 4), (10, 2)]}]}
    site["terrain"]["surface"] = _planar(0.3, 0.0)
    manifest = {"site": {"floors": {"built": {"terrace": "paving", "path": "paving", "drive": "paving",
                                              "steps": "paving"}}}}
    found, n = GR.review(site, manifest)
    rules = {f["metrics"]["rule"] for f in found}
    assert n > 0 and {"G1", "G3", "G5", "G6", "G7"} <= rules, rules
    assert all(f["check"] == "M15" and f["metrics"]["model_review"] for f in found)
    msgs = " ".join(f["message"] for f in found)
    assert "bare box" in msgs and "stacked like stairs" in msgs and "bare concrete_exposed" in msgs
    # the plain list for Argus's lessons line: the site plan or the whole prepare record, the same problems
    probs = GR.grading_problems(site, manifest)
    assert len(probs) == len(found) and all(set(p) == {"target", "message", "severity", "rule", "kind"} for p in probs)
    assert all(p["severity"] in ("major", "minor") for p in probs)
    assert GR.grading_problems({"site": site, "building": {}}, manifest) == probs
    assert GR.grading_problems(None) == [] and GR.grading_problems({"site": None}) == []
    # Argus reads the kinds and the agent the cause (no agent tool: reported to the site stage)
    from wenart.agent import causes as C
    from wenart.audit import kinds as K
    assert K.kind_of({"check": "M15"}) == "no_sense" and K.kind_of({"check": "M15", "kind": "taste"}) == "taste"
    assert C.CHECK_CAUSE["M15"] == "site_grading" and C.NO_TOOL_REASON["site_grading"]
    assert C.REPORT_TO["site_grading"] == "site" and C.CAUSE_TOOLS["site_grading"] == ()


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_real04_slope_is_graded_and_the_check_finds_the_crude_grading_of_before(monkeypatch):
    """The case: real04's site plan (build.prepare) now steps each side of a terrace in tiers at one level, plants every
    tier, builds its flights on the ground with cheek walls, lays its paths level across and stepped, puts its walls in
    the house's base stone with copings, and the model review's M15 measures it clean; with the per-piece levels and
    bare tiers of before (run_steps and tier_plants switched off) M15 finds the staircase of bare boxes."""
    from wenart.blender import build as BB
    from wenart.blender import model_review as MR

    monkeypatch.delenv(S.SITE_VARIANT_ENV, raising=False)
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    prep = BB.prepare(b, "base", None, style_family="modern")
    site = prep["site"]
    pfs = site["platforms"]
    sp1 = [p for p in pfs if p.get("parent") == "sp_001" and p["stepped_from"]["direction"] == "down"]
    assert len({p["z"] for p in sp1 if p["step"] == 1}) == 1                 # one level along the west side
    assert all((p.get("planting") or {}).get("plants") for p in pfs if p.get("parent"))
    assert site["wall_look"]["material"] == "stone_wall_ledgestone" and site["style_family"] == "modern"
    graded = [r for r in GR.graded_paths(site) if r["graded"]]
    assert len(graded) >= 4 and all(r["kind"] in ("stepped", "sloped_walk") for r in graded)
    assert {r["id"] for r in graded} >= {"path_access_sp_001_0", "path_access_sp_001_1"}
    terrain = site["terrain"]
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    flights = 0
    for pid in ("sp_001", "sp_004"):
        pf = next(p for p in pfs if p["id"] == pid)
        fl = GR.down_flight(pf, gz)
        if fl is None:                       # the edge meets the ground (within 2 cm) at the flight's foot: no steps
            i = pf["steps_edge"]
            p0, p1 = pf["polygon"][i], pf["polygon"][(i + 1) % len(pf["polygon"])]
            assert pf["z"] - gz(*G.segment_midpoint(p0, p1)) <= S.PLATFORM["level_tol"]
            continue
        flights += 1
        assert max(gz(*q) for q in fl["foot"]) <= fl["foot_z"] + 1e-3
        treads = GR.flight_meshes(fl, gz, S.PLATFORM["below"])["treads"]
        assert GR.tread_findings("f", pid, treads, True) == []
    assert flights >= 1
    rec = MR.review(prep["building"], None, prep)
    assert rec["checks"]["M15"]["status"] == "ok" and rec["checks"]["M15"]["checked"] > 20
    assert [f for f in rec["findings"] if f["check"] == "M15"] == []
    arch = {q["id"]: q for q in prep["architect"]["questions"]}
    assert arch["G2"]["status"] == "ok" and arch["G3"]["status"] == "ok"
    # the grading of before: per-piece levels, nothing planted -> M15 finds the boxes stacked like stairs
    monkeypatch.setattr(GR, "run_steps", lambda excess, cap: {})
    monkeypatch.setattr(GR, "tier_plants", lambda *a, **k: [])
    old = BB.prepare(b, "base", None, style_family="modern")["site"]
    found, _n = GR.review(old)
    msgs = [f["message"] for f in found if f["metrics"]["rule"] == "G1"]
    assert any("stacked like stairs" in m for m in msgs) and any("bare box" in m for m in msgs)


# --------------------------------------------------------------------------
# build_site on the CPU (bpy replaced): what the scene gets and records
# --------------------------------------------------------------------------

class _Ob:
    def __init__(self, name, verts=(), faces=(), **kw):
        self.name, self.verts, self.faces, self.kw = name, list(verts), [list(f) for f in faces], kw


def test_build_site_puts_each_floor_s_use_the_walls_in_stone_with_copings_and_builds_the_stepped_path(monkeypatch):
    import jsonschema

    from wenart.blender import common, schemas
    from wenart.blender import vegetation as VG

    monkeypatch.setattr(common, "new_mesh_object", lambda name, verts, faces, **kw: _Ob(name, verts, faces, **kw))
    monkeypatch.setattr(VG, "lawn_material", lambda *a, **k: {"applied": False})
    monkeypatch.setattr(S, "build_cars", lambda *a, **k: [])
    surface = _planar(0.06, -0.2)
    terrain = _terrain(surface)
    site = _site(surface, [{"id": "t1", "polygon": [[-3, -2], [3, -2], [3, 2], [-3, 2]], "build": True}],
                 marks=[{"x": 0.0, "y": 0.0, "z": 0.0, "kind": "ground_finished", "mark_id": "lm"}])
    site["parking"] = [{"id": "pk", "polygon": [[6, -4], [12, -4], [12, 1], [6, 1]], "build": True}]
    pfs = S.platforms(site, terrain)
    path = {"id": "path_x", "kind": "path", "polygon": _strip(-8, 4, y0=7.0), "z": None, "material": None,
            "colour": None, "source": "assumed", "area_id": None, "lift": S.PAVING_LIFT}
    plan = {"mode": "full", "terrain": terrain, "outline": [(30, 30), (34, 30), (34, 34), (30, 34)], "plot": [],
            "plot_source": "test", "extent": [(-20, -20), (40, -20), (40, 40), (-20, 40)], "wells": [],
            "plot_walls": [], "areas": [path], "trees": [], "not_built": [], "assumed": [], "warnings": [],
            "ground_is_grass": True, "inferred": None, "copy_holes": [], "pools": [], "platforms": pfs,
            "climate": {"climate": "temperate"}, "hedges": [], "levers": {"platforms": True}, "species": {},
            "style_family": "modern", "wall_look": GR.wall_look({}, "modern")}
    looks = {k: {"material": k, "colour": None, "source": "fallback", "assumed": True} for k in (
        "garden", "paving", "plot_wall", "light_well", "bark", "foliage", "ground", "railing", "facade")}
    objs, assumed = [], []
    summary = S.build_site(plan, None, looks, lambda look: _Ob(str(look.get("material"))), objs, assumed)
    floors = summary["floors"]["built"]
    assert floors["terrace"] == "paving_stone" and floors["drive"] == "paving" and floors["path"] == "gravel"
    assert len(set(floors.values())) >= 3                                   # never one look for every use
    assert summary["walls"]["material"] == "stone_wall_ledgestone" and summary["walls"]["coping"] == "paving_stone"
    names = {o["name"] for o in objs}
    assert "platform_t1_wall" in names and "platform_t1_coping" in names
    walls = [o for o in objs if o.get("part") == "wall"]
    assert walls and all(o["material"] == "stone_wall_ledgestone" for o in walls)
    graded = next(p for p in summary["paths"] if p["id"] == "path_x")
    assert graded["kind"] in ("stepped", "sloped_walk")
    assert "path_x_tread" in names and ({"path_x_edging", "path_x_edge_wall"} & names)
    if graded["kind"] == "stepped":
        assert "path_x_step_edge" in names
    assert summary["grading"]["tiers"] == sum(1 for p in pfs if p.get("parent"))
    for o in objs:
        jsonschema.validate(o, schemas.SCENE_OBJECT)
    for a in assumed:
        jsonschema.validate(a, schemas.ASSUMED_ENTRY)
    # the review reads the floors as built from the manifest's site block (three looks: no G7) and the walls (stone)
    found, _n = GR.review(plan, {"site": summary, "objects": objs})
    assert not [f for f in found if f["metrics"]["rule"] in ("G6", "G7")]
