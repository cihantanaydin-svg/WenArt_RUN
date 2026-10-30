"""30 Oct 2026, the user's review of real04 run 20261030-112241-full. UL196 "Better road section and fencing area is needed
on the outside": the streets were bare asphalt strips, the neighbours' plots had low two-rail ranch fences. UL198
"Understand that the cars should be able to enter to this location and exit": the drive's ends met the streets behind a
kerb. A street is a real section (kerbs, a pavement, a centre line, lamps), a neighbour's fence a board fence with a
gate, and a car drives into every parking from a street and out again. Pure tests; real04 is only the test case."""
import json
from pathlib import Path

import pytest
from shapely.geometry import Point, Polygon

from wenart import geometry as G
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "baseline" / "latest" / "furniture" / "real04" / "building_final.json"
FLAT = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _l_drive():
    return {"id": "drive", "kind": "parking", "polygon": [(19, -4), (24, -4), (24, 35), (-1, 35), (-1, 30), (19, 30)]}


def _roads():
    return S.outside_roads([_l_drive()], _rect(-6, -4, 25, 36), _rect(-60, -60, 90, 100), _rect(0, 0, 15, 12))


def test_a_street_has_kerbs_a_pavement_a_centre_line_and_lamps():
    out = _roads()
    road = [Polygon(a["polygon"]) for a in out["areas"] if a["kind"] == "road"]
    walk = [a for a in out["areas"] if a["kind"] == "pavement"]
    assert road and walk and all(a["material"] == "paving" and a["lift"] > S.PAVING_LIFT for a in walk)
    st = out["streets"]
    assert st["kerbs"] and st["edgings"] and st["dashes"] and st["lamps"] and st["centrelines"]
    links = [Polygon(ln["polygon"]) for ln in out["links"]]
    # no kerb across a drive's crossover: every kerb run stays clear of the links (the kerb is dropped there)
    for a, b in st["kerbs"]:
        mid = Point(G.segment_midpoint(a, b))
        assert all(ln.buffer(-0.05).distance(mid) > 0.05 for ln in links)
    # the pavement lies between the plot and the carriageway: its strip south of the plot is pave_m deep
    assert any(Polygon(a["polygon"]).contains(Point(10.0, -4.0 - S.STREET["pave_m"] / 2.0)) for a in walk)
    assert any(r.contains(Point(10.0, -4.0 - S.STREET["pave_m"] - 1.0)) for r in road)
    # dashes on the carriageway, lamps on the pavement away from the crossovers
    for d in st["dashes"]:
        assert any(r.buffer(0.01).contains(Polygon(d)) for r in road)
    walks = [Polygon(a["polygon"]) for a in walk]
    for lp in st["lamps"]:
        p = Point(lp["at"])
        assert any(w.contains(p) for w in walks) and all(ln.distance(p) > S.STREET["lamp_clear_m"] for ln in links)
    assert "lesson UL196" in st["reason"]


def test_street_parts_are_meshes_of_real_size():
    parts = S.street_parts(_roads()["streets"], FLAT)
    assert set(parts) == {"kerb", "edging", "line", "lamp"}
    kv, _kf = parts["kerb"]
    assert max(v[2] for v in kv) >= S.PAVING_LIFT + S.STREET["pave_lift_m"]          # the kerb tops the pavement
    lv, _lf = parts["lamp"]
    assert abs(max(v[2] for v in lv) - (S.PAVING_LIFT + S.STREET["pave_lift_m"] + S.STREET["lamp_h"])) < 0.05
    dv, _df = parts["line"]
    assert max(v[2] for v in dv) < 0.05                                                # paint on the asphalt


def test_a_neighbours_fence_is_a_board_fence_with_a_gate():
    v, f, info = S.fence_product_parts({"kind": "fence", "start": (0.0, 0.0), "end": (6.0, 0.0)}, FLAT)
    assert info["kind"] == "fence" and info["posts"] == 4 and info["height"] == S.FENCE["height_m"] >= 1.2
    zs = [p[2] for p in v]
    assert max(zs) == pytest.approx(S.FENCE["height_m"], abs=1e-6) and min(zs) < 0.0       # posts set in the ground
    assert len(f) > 100                                                                # posts, boards and caps
    gv, gf, ginfo = S.fence_product_parts({"kind": "gate", "start": (0.0, 0.0), "end": (3.0, 0.0)}, FLAT)
    assert ginfo["kind"] == "gate" and gf and max(p[2] for p in gv) > S.FENCE["height_m"]
    nbs = _roads()["neighbours"]
    assert nbs and all(sum(1 for s in nb["fence"] if s["kind"] == "gate") == 1 for nb in nbs)


def _site(parking, gaps=None, extra=None):
    pf = dict(parking, z=0.0, sloped=True, edge="kerb", kerb_gaps=gaps or [])
    site = {"terrain": FLAT, "platforms": [pf], "areas": [{"id": "street_1", "kind": "road",
                                                            "polygon": _rect(-20, -12, 60, -6)}]}
    site.update(extra or {})
    return site


def test_a_car_drives_in_over_a_dropped_kerb_and_turns_at_the_corner():
    l_drive = {"id": "p", "kind": "parking", "polygon": geom_l()}
    blocked = S.vehicle_access(_site(l_drive))[0]
    assert not blocked["ok"] and "a kerb across it" in blocked["problems"][0]
    poly = S.geom2d.ccw(l_drive["polygon"])
    edge = S._edge_index(poly, (21.5, -6.0))
    row = S.vehicle_access(_site(l_drive, gaps=[[edge, 0.0, 5.0]]))[0]
    assert row["ok"] and row["turn"] == "hammerhead" and row["connections"][0]["width_m"] >= S.CAR["width_m"]
    # a fence across the way in, or a straight dead end with no room to turn
    fence = {"neighbours": [{"id": "n1", "fence": [{"kind": "fence", "start": (18.0, -6.5), "end": (26.0, -6.5)}]}]}
    fenced = S.vehicle_access(_site(l_drive, gaps=[[edge, 0.0, 5.0]], extra=fence))[0]
    assert not fenced["ok"] and "fence n1" in fenced["problems"][0]
    strip = {"id": "s", "kind": "parking", "polygon": _rect(19, -6, 24, 20)}
    se = S._edge_index(S.geom2d.ccw(strip["polygon"]), (21.5, -6.0))
    dead = S.vehicle_access(_site(strip, gaps=[[se, 0.0, 5.0]]))[0]
    assert not dead["ok"] and dead["turn"] is None and "no room to turn" in dead["problems"][0]
    assert S.turning_room(_rect(0, 0, 8, 8)) == "turning head"


def test_a_way_in_steeper_than_a_car_takes_is_no_way_in(monkeypatch):
    l_drive = {"id": "p", "kind": "parking", "polygon": geom_l()}
    edge = S._edge_index(S.geom2d.ccw(l_drive["polygon"]), (21.5, -6.0))
    monkeypatch.setattr(S, "ground_z", lambda terrain, x, y: 0.25 * y)
    row = S.vehicle_access(_site(l_drive, gaps=[[edge, 0.0, 5.0]]))[0]
    assert not row["ok"] and "gradient of" in row["problems"][0] and "(at most 15 %)" in row["problems"][0]


def geom_l():
    """An L drive 5 m wide from the street at y = -6: up x = 19-24 and west along y = 30-35."""
    return [(19, -6), (24, -6), (24, 35), (-1, 35), (-1, 30), (19, 30)]


def test_real04_parking_is_reachable_by_car():
    if not BASE.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    from wenart.blender import build as B
    from wenart.blender import site_sense as SS

    site = B.prepare(json.loads(BASE.read_text(encoding="utf-8")))["site"]
    rows = S.vehicle_access(site)
    assert rows and all(r["ok"] for r in rows), rows
    assert any(len([c for c in r["connections"] if not c["problems"]]) >= 1 for r in rows)
    assert not [f for f in SS.access(site) if f["severity"] == "major"]
    st = site["streets"]
    assert st["kerbs"] and st["dashes"] and st["lamps"] and [a for a in site["areas"] if a["kind"] == "pavement"]


# ---------------------------------------------------------------- UL202: walkways walkable; UL203: a step into the house

def test_route_legs_meet_on_a_level_corner_landing_edge_to_edge():
    from wenart.blender import architect as AR

    areas = AR.path_areas("t", [(0.0, 0.0), (0.0, 6.0), (8.0, 6.0)], 0.6, "a route (inferred)")
    corner = [a for a in areas if a.get("landing")]
    legs = [a for a in areas if not a.get("landing")]
    assert len(corner) == 1 and len(legs) == 2 and areas[0] is corner[0]           # the landing is planned first
    polys = [Polygon(a["polygon"]) for a in areas]
    for i, p in enumerate(polys):                                                    # edge to edge, never one over
        assert all(p.intersection(q).area < 1e-6 for q in polys[i + 1:])
    assert abs(Polygon(corner[0]["polygon"]).area - 1.44) < 1e-6


def _slope_site(areas, trees=()):
    return {"terrain": FLAT, "outline": [], "copy_holes": [], "pools": [], "wells": [], "platforms": [],
            "areas": areas, "trees": list(trees)}


def test_two_paths_meet_level_and_nothing_stands_in_a_walk(monkeypatch):
    from wenart.blender import grading as GR
    from wenart.blender import site_sense as SS

    monkeypatch.setattr(S, "ground_z", lambda terrain, x, y: 0.3 * y)                # a 30 % slope up +y
    trunk = {"id": "trunk", "kind": "path", "polygon": _rect(0, 0, 1.2, 12)}
    recs = GR.graded_paths(_slope_site([trunk]))
    land = next(s for s in recs[0]["slices"] if s["kind"] == "landing" and s["t1"] - s["t0"] >= 1.2
                and 0.5 < s["t0"] < 11.0 - 1.2)
    y = GR._at(recs[0]["frame"], (land["t0"] + land["t1"]) / 2.0)[1]
    branch = {"id": "branch", "kind": "path", "polygon": _rect(1.2, y - 0.6, 6.0, y + 0.6)}    # ends at its side
    site = _slope_site([trunk, branch])
    recs = {r["id"]: r for r in GR.graded_paths(site)}
    assert recs["branch"]["joins"][0]["to"] == "trunk" and recs["trunk"]["branches"][0]["path"] == "branch"
    assert abs(GR.level_on(recs["branch"], (1.25, y)) - GR.level_on(recs["trunk"], (0.6, y))) <= GR.JOIN_TOL_M
    assert SS.walkways(site) == []
    # the old layout: the branch laid over the trunk on its steps; a shrub in the walk
    over = {"id": "branch", "kind": "path", "polygon": _rect(-0.6, 2.4, 6.0, 3.6)}
    msgs = [f["message"] for f in SS.walkways(_slope_site([trunk, over], trees=[
        {"id": "sh1", "kind": "tree", "center": [3.0, 3.0], "size": [0.7, 0.7]}]))]
    assert any("run one over the other" in m for m in msgs) and any("tree sh1 stands in the walk" in m for m in msgs)


def test_a_flush_entrance_gets_a_step_up_into_the_house():
    from wenart.blender import grading as GR

    e = {"opening_id": "d1", "level_id": "L0", "centre": (5.0, 0.0), "outward": (0.0, -1.0), "half_t": 0.1,
         "width": 0.9, "bottom": 0.0, "ground_z": 0.0, "rise": 0.0,
         "record": {"door_id": "d1", "room_id": "hall", "solution": "none", "main": True}}
    b = {"rooms": [{"id": "hall", "room_type": "hall"}], "level_marks": [], "site": {}}
    th = S.entrance_threshold(e, b)
    assert th["kind"] == "step_up" and abs(th["riser"] - 0.15) < 1e-9 and "UL203" in th["reason"]
    st = S.entrance_steps(dict(e, threshold=th))
    assert abs(st["blocks"][0]["z_top"] + 0.15) < 1e-9 and st["thresholds"][0]["z_top"] == 0.0 and st["end"] == 1.2
    assert S.flight_spec(e, st) is None
    pads = S.entrance_pads([st])
    assert abs(GR.grade_z(pads, 5.0, -0.6, 0.0) + 0.15) < 1e-9                          # the landing at its level
    assert -0.15 < GR.grade_z(pads, 5.0, -2.2, 0.0) < 0.0                                # the ground falls away from it
    assert -0.6 < GR.grade_z(pads, 5.0, -1.4, -0.6) < -0.15                              # a lower ground meets it
    # the documents give the level at the door, a garage door, an accessible entrance
    marked = dict(b, level_marks=[{"id": "m1", "kind": "ground_finished", "z": 0.0, "point": [5.5, -1.0],
                                   "level_id": "L0", "raw": "43.00"}])
    assert S.entrance_threshold(e, marked)["kind"] == "keep"
    garage = dict(b, rooms=[{"id": "hall", "room_type": "garage"}])
    assert S.entrance_threshold(e, garage)["kind"] == "keep"
    acc = dict(b, project={"brief": {"levels": {"accessible_entrance": True}}})
    th2 = S.entrance_threshold(e, acc)
    st2 = S.entrance_steps(dict(e, threshold=th2))
    assert th2["kind"] == "level" and st2["drains"] and st2["blocks"][0]["z_top"] == 0.0


def test_real04_entrances_step_up_and_its_walkways_are_walkable():
    if not BASE.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    from wenart.blender import build as B
    from wenart.blender import site_sense as SS

    prep = B.prepare(json.loads(BASE.read_text(encoding="utf-8")))
    site = prep["site"]
    ups = [s for s in site["inferred"]["steps"] if s.get("step_up")]
    assert len(ups) == 2 and all(abs(s["blocks"][0]["z_top"] + 0.15) < 1e-6 and s["thresholds"] for s in ups)
    assert SS.walkways(site) == []
    a2 = next(q for q in prep["architect"]["questions"] if q["id"] == "A2")
    assert any("steps of sp_002" in str(a.get("change")) for a in a2["answers"])          # walkable, round the shrubs
