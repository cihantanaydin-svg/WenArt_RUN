"""The outdoor walk (31 Oct 2026, user on real04 run 20261030-181158-full: "we need to develop a log that is checking
the a person can walk around the house using the designated pathways and able to reach the area, the pathways must be
logical) Looked at the marked area it is not making sense the person going to jump to reach the pool?").

Pure tests, no Blender, on a synthetic site: a stepped side path comes down beside the house and stops short of a sunken
pool terrace (no flight, no door): the walk check finds the dead end at the drop and the terrace nobody reaches, the
architect runs the path on to the terrace (its steps make up the level), the walk is connected afterwards. The real04
replay reads the committed latest baseline (the marked area: the path from the house started 15 cm under the foot
landing of the pool terrace's flight)."""
import json
from pathlib import Path

import pytest

from wenart.blender import architect_walk as AW
from wenart.blender import grading as GR
from wenart.blender import site as S
from wenart.blender import site_sense as SS
from wenart.blender import site_walk as SW
from wenart.levels import terrain as T

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "baseline" / "latest" / "furniture" / "real04" / "building_final.json"


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _terrain(a: float = 0.0, b: float = 0.1, c: float = -0.8) -> dict:
    """The ground z = a x + b y + c: here falling 1:10 to the south (0.0 m at the house's north face, y = 8)."""
    r = 40.0
    surface = T.fit_surface([(x, y, a * x + b * y + c) for x, y in ((-r, -r), (r, -r), (r, r), (-r, r))])
    return {"kind": "planar", "surface": surface, "z": {}, "rect": [-10, -10, 10, 10]}


def _path(pid, poly):
    return {"id": pid, "kind": "path", "polygon": [list(p) for p in poly], "z": None, "inferred": True,
            "source": "assumed", "reason": "test"}


def _site(gap: float = 0.3) -> dict:
    """A house (0..10 x 0..8) on a slope falling to the south, its entrance d1 on the north face at the ground (a level
    landing), a pavement along the plot's north edge, a front path from the landing to the pavement, a link from the
    landing east to a stepped side path running down beside the house, and a sunken pool terrace at -2.50 m whose north
    edge lies ``gap`` past the side path's lower end: no flight, no door (the ground stands 0.4-1.4 m over it)."""
    top = -3.0 - gap
    pool = _rect(10.0, -11.0, 14.0, top - 1.5)
    terrace = {"id": "t1", "kind": "terrace", "polygon": _rect(9.0, -12.0, 15.0, top), "z": -2.5,
               "holes": [pool], "sloped": False, "pools": ["pool_1"], "steps_edge": None,
               "against_edges": [], "edge": "retaining", "railing_edges": [],
               # the platform's level less the ground at each edge (site.platforms): the ground over it all round
               "edge_drops": {0: -0.5, 1: -0.9, 2: round(-2.5 - (0.1 * top - 0.8), 3), 3: -0.9}}
    return {"mode": "full", "terrain": _terrain(), "outline": _rect(0.0, 0.0, 10.0, 8.0),
            "plot": _rect(-3, -16, 20, 14), "copy_holes": [], "wells": [], "hedges": [], "trees": [],
            "pools": [{"id": "pool_1", "polygon": pool}],
            "platforms": [terrace],
            "areas": [_path("path_front", _rect(4.4, 9.2, 5.6, 14.0)),
                      _path("path_side", _rect(11.0, -3.0, 12.2, 9.8)),
                      _path("path_link", _rect(5.7, 8.2, 11.0, 9.4)),
                      {"id": "pavement_1", "kind": "pavement", "polygon": _rect(-5.0, 14.0, 20.0, 16.0)}],
            "inferred": {"entrances": [], "main": {"opening_ids": ["d1"]}, "paths": [],
                         "steps": [{"opening_id": "d1", "level_threshold": True,
                                    "blocks": [{"polygon": _rect(4.3, 8.0, 5.7, 9.2), "z_top": 0.0}]}]},
            "outside_doors": [{"id": "d1", "point": [5.0, 8.5], "z": 0.0, "main": True}]}


def _problems(found):
    return sorted((f["metrics"]["problem"], str(f["target"])) for f in found)


def test_the_walk_check_finds_a_side_path_that_stops_at_a_drop_above_a_sunken_pool_terrace():
    site = _site()
    rec = SW.analyse(site)
    g = rec["graph"]
    # the starts: the street, the door's landing and the front path at the plot's edge (a way in)
    assert "street" in g["starts"] and "entrance:d1" in g["starts"] and "path:path_front" in g["starts"]
    assert {"path:path_front", "path:path_link", "path:path_side", "entrance:d1"} <= rec["reached"]
    assert "platform:t1" not in rec["reached"]
    probs = _problems(rec["findings"])
    assert ("dead_end_drop", "path_side") in probs and ("unreachable", "t1") in probs
    drop = next(f for f in rec["findings"] if f["metrics"]["problem"] == "dead_end_drop")
    assert drop["severity"] == "major" and "jump" in drop["message"]
    assert drop["metrics"]["dz_m"] == pytest.approx(-2.5 - GR.graded_paths(site)[1]["slices"][0]["z0"], abs=0.05)
    assert abs(drop["metrics"]["dz_m"]) > 1.2 and drop["metrics"]["at"][1] == pytest.approx(-3.0, abs=0.01)
    lost = next(f for f in rec["findings"] if f["metrics"]["problem"] == "unreachable")
    assert lost["metrics"]["nearest"]["node"] == "path:path_side" and lost["metrics"]["nearest"]["gap_m"] < 0.5
    # G15 is part of the model review's M15 (site_sense) and of the walk's log
    found, _n = SS.review(site)
    assert {("dead_end_drop", "path_side"), ("unreachable", "t1")} <= {
        (f["metrics"].get("problem"), str(f["target"])) for f in found if f["metrics"]["rule"] == "G15"}
    log = SW.walk_log(site, rec)
    json.dumps(log)
    assert log["areas"] == 2 and log["areas_reached"] == 1
    assert any(j["a"] == "entrance:d1" and j["b"] == "path:path_front" and j["walkable"] for j in log["joints"])


def test_the_architect_runs_the_path_on_to_the_terrace_and_the_walk_is_connected():
    site = _site()
    prep = {"site": site}
    q = AW.review_walk({"levels": []}, prep)
    assert q["status"] == "fixed", q["answers"]
    fixed = [a for a in q["answers"] if a.get("fixed")]
    assert fixed and "runs on" in fixed[0]["change"]
    side = next(a for a in site["areas"] if a["id"] == "path_side")
    assert side["adjusted_by_ai"]["by"] == "architect" and side["adjusted_by_ai"]["drawn_polygon"]
    assert min(p[1] for p in side["polygon"]) < -3.3                   # it reaches the terrace's edge now
    rec = next(r for r in GR.graded_paths(site) if r["id"] == "path_side")
    # the steps make up the 2.7 m: flights with landings, level across, the end met at the terrace's level
    assert rec["kind"] == "stepped" and not rec.get("too_steep") and len(rec["flights"]) >= 2
    assert rec["slices"][0]["z0"] == pytest.approx(-2.5, abs=1e-6) and max(rec["flights"]) <= 12
    assert any(j["kind"] == "surface" and j["to"] == "platform:t1" for j in rec["joins"])
    again = SW.analyse(site)
    assert "platform:t1" in again["reached"] and not again["findings"]
    assert site["walk"]["first_findings"] >= 2 and site["walk"]["fixes"][0]["fix"] == "extend"
    assert site["walk"]["areas_reached"] == site["walk"]["areas"] == 2 and not site["walk"]["findings"]
    json.dumps(site["walk"])
    # no new crude grading: no path under a surface, no flight into a wall, the walkways walkable
    assert not [f for f in SS.fragments(site) + SS.flights_meet(site) + SS.walkways(site) if f["severity"] == "major"]


def test_a_terrace_out_of_reach_gets_a_flight_and_a_path_when_no_path_runs_on_to_it():
    """The side path ends 4 m short of the sunken terrace (too far to run on): the architect gives the terrace a flight
    up into the higher ground on the edge nearest the paths and a path from its top to the side path."""
    site = _site(gap=4.0)
    rec = SW.analyse(site)
    assert ("unreachable", "t1") in _problems(rec["findings"])
    q = AW.review_walk({"levels": []}, {"site": site})
    t1 = site["platforms"][0]
    assert t1["steps_edge"] is not None and t1["steps_dir"] == "up" and t1.get("flight")
    again = SW.analyse(site)
    assert "platform:t1" in again["reached"], q["answers"]
    assert not [f for f in again["findings"] if f["severity"] == "major"]
    assert any(a.get("fixed") and "a flight up" in a["change"] for a in q["answers"])


def test_a_flight_onto_the_lawn_is_found_and_joined_to_the_paths():
    """A deck beside the house (a door onto it) has its flight down to the lawn and no path from its foot: a dead-end
    flight; the architect leads a path from its foot to the site's paths (as A2 does for the decks without a door)."""
    site = _site()
    deck = {"id": "deck", "kind": "terrace", "polygon": _rect(-6.0, 1.0, 0.0, 7.0), "z": 0.0, "holes": [],
            "sloped": False, "pools": [], "steps_edge": 3, "against_edges": [1], "edge": "steps", "railing_edges": [],
            "edge_drops": {0: 0.7, 1: 0.0, 2: 0.1, 3: 0.4}}
    site["platforms"] = [deck]
    site["pools"] = []
    site["plot"] = _rect(-14, -16, 20, 14)
    site["outside_doors"].append({"id": "d2", "point": [-0.5, 4.0], "z": 0.0, "main": False})
    rec = SW.analyse(site)
    assert "platform:deck" in rec["reached"]                     # by its door
    dead = [f for f in rec["findings"] if f["metrics"]["problem"] == "dead_flight"]
    assert dead and dead[0]["target"] == "deck" and dead[0]["severity"] == "major"
    q = AW.review_walk({"levels": []}, {"site": site})
    assert any(a.get("fixed") and "a path from the steps of deck" in a["change"] for a in q["answers"]), q["answers"]
    again = SW.analyse(site)
    assert not [f for f in again["findings"] if f["metrics"]["problem"] == "dead_flight"]
    new = [e for e in again["ends"] if e["path"].startswith("path_access_deck")]
    assert any(e["kind"] in ("joint", "side") and e["to"] == "foot:deck" and abs(e["dz"]) <= SW.STEP_MAX_M
               for e in new)


def test_a_path_from_a_flight_meets_its_foot_landing_level(monkeypatch):
    """real04's marked area in small: a raised terrace's flight down lands on the ground; the path the architect leads
    from it starts at the foot landing's side. Without the planner rule (the path laid on the ground) the check finds
    the raw step at the joint; with it the path starts at the landing's level."""
    terrain = _terrain(a=0.0, b=0.2, c=-1.5)            # the ground rises 1:5 to the north
    deck = {"id": "d1", "kind": "terrace", "polygon": _rect(10.0, 0.0, 16.0, 6.0), "z": 0.0, "holes": [],
            "sloped": False, "pools": [], "steps_edge": 3, "against_edges": [], "edge": "steps",
            "railing_edges": [], "foot_open": "right"}
    site = {"mode": "full", "terrain": terrain, "outline": _rect(30.0, 0.0, 40.0, 8.0), "plot": _rect(-5, -10, 45, 20),
            "copy_holes": [], "wells": [], "hedges": [], "trees": [], "pools": [], "platforms": [deck],
            "inferred": {"entrances": [], "steps": []}, "outside_doors": []}
    fl = GR.down_flight(deck, lambda x, y: 0.2 * y - 1.5)
    assert fl is not None and fl["count"] >= 3 and fl["out"][0] < -0.99      # down to the west, 0.8 m
    # the architect's path from the foot landing's right side (north, its cheek left out), up the slope to the north
    xs = [p[0] for p in fl["foot"]]
    ys = [p[1] for p in fl["foot"]]
    site["areas"] = [_path("p1", _rect(min(xs), max(ys), max(xs), max(ys) + 5.0))]
    monkeypatch.setattr(GR, "walk_surfaces", lambda plan, gz, terrain=None: [])
    rec = SW.analyse(site)
    step = [f for f in rec["findings"] if f["metrics"]["problem"] in ("junction_step", "junction_drop")]
    assert step and step[0]["target"] == "p1" and step[0]["metrics"]["to"] == "foot:d1"
    assert abs(step[0]["metrics"]["dz_m"]) > SW.LEVEL_TOL_M
    monkeypatch.undo()
    rec = SW.analyse(site)
    assert not [f for f in rec["findings"] if f["metrics"]["problem"] in ("junction_step", "junction_drop")]
    p1 = next(r for r in GR.graded_paths(site) if r["id"] == "p1")
    assert p1["joins"][0]["to"] == "foot:d1" and p1["pins"]["start"] == pytest.approx(fl["foot_z"])


def test_railings_cheeks_and_buildings_stop_the_walk():
    """Two surfaces at one level beside each other are joined unless a railing, a cheek wall or a building stands
    between them; a drop of more than a step never joins them."""
    flat = {"kind": "flat", "z": {"+x": 0.0, "-x": 0.0, "+y": 0.0, "-y": 0.0}}
    a = {"id": "a", "kind": "terrace", "polygon": _rect(0, 0, 4, 4), "z": 0.3, "holes": [], "sloped": False,
         "pools": [], "steps_edge": None, "railing_edges": [], "against_edges": []}
    b = dict(a, id="b", polygon=_rect(4.12, 0, 8, 4), z=0.4)        # a 12 cm joint between them, 10 cm higher
    site = {"terrain": flat, "platforms": [a, b], "areas": [], "inferred": {}, "outline": [], "copy_holes": []}
    g = SW.walk_graph(site)
    assert g["edges"][("platform:a", "platform:b")]["dz"] == pytest.approx(0.1)
    a["railing_edges"] = [1]                       # the edge x = 4 of a (counter-clockwise: 0 bottom, 1 right)
    assert ("platform:a", "platform:b") not in SW.walk_graph(site)["edges"]
    a["railing_edges"] = []
    b["z"] = 0.75                                            # 0.45 m: a drop, no step
    g = SW.walk_graph(site)
    assert ("platform:a", "platform:b") in g["contacts"] and ("platform:a", "platform:b") not in g["edges"]
    b["z"] = 0.4
    site["outline"] = _rect(4.02, -1, 4.10, 5)               # the wall of a building in the joint
    assert ("platform:a", "platform:b") not in SW.walk_graph(site)["edges"]


def test_the_walk_uses_the_project_step_rules():
    """One step between two surfaces rises at most the drawn riser limit (site.DRAWN_RISER_MAX_M, 0.20 m); two walks
    that meet differ at most the joint tolerance of the walkways (grading.JOIN_TOL_M)."""
    assert SW.STEP_MAX_M == S.DRAWN_RISER_MAX_M and SW.LEVEL_TOL_M == GR.JOIN_TOL_M
    assert GR.RULES["G15"] and SW.RULE == "G15"


def test_a_garden_without_designated_paths_needs_none():
    """A site with no paths and no streets: the garden is the way; its flights land on the lawn without a finding."""
    site = _site()
    site["areas"] = []
    site["inferred"]["steps"] = []
    rec = SW.analyse(site)
    assert not [f for f in rec["findings"] if f["metrics"]["problem"] in ("dead_end", "dead_flight", "dead_end_drop")]


def test_real04_walk_is_connected_after_the_architect():
    """real04 (latest baseline): from the street, the parking and the two back doors a person walks to the four pool
    terraces and the parking; the path from the house meets the foot landing of sp_001's flight at its level (the
    marked area of run 20261030-181158-full), the corner landing at sp_002's flight meets its top step."""
    if not BASE.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    from wenart.blender import build as B

    prep = B.prepare(json.loads(BASE.read_text(encoding="utf-8")))
    site = prep["site"]
    a6 = next(q for q in prep["architect"]["questions"] if q["id"] == "A6")
    assert a6["status"] in ("ok", "fixed") and not [a for a in a6["answers"] if a.get("open")]
    walk = site["walk"]
    assert walk["areas"] >= 5 and walk["areas_reached"] == walk["areas"]
    assert {d["id"] for d in walk["doors"]} >= {"d_L0_011", "d_L0_012"}
    recs = {r["id"]: r for r in GR.graded_paths(site)}
    p = recs.get("path_access_sp_001_0")
    if p is not None:
        terrain = GR.plan_terrain(site)
        foot = GR.down_flight(next(pf for pf in site["platforms"] if pf["id"] == "sp_001"),
                              lambda x, y: S.ground_z(terrain, x, y))
        assert any(j["to"] == "foot:sp_001" for j in p["joins"])
        assert p["pins"]["start"] == pytest.approx(foot["foot_z"])
    found, _n = GR.review(site)
    assert not [f for f in found if f["metrics"]["rule"] == "G15" and f["severity"] == "major"]


def test_one_riser_under_the_outdoor_minimum_has_no_cheek_walls():
    """Lesson UL227 (real04's sp_001: one riser of 6.8 cm whose cheek walls stood like blocks in the lawn): a flight of
    one riser under ``riser_min_outdoor`` (L5) holds no ground back, so it has no cheek walls and its foot landing is
    open on every side; a real flight keeps its cheeks."""
    pf = {"id": "t", "polygon": _rect(0, 0, 4, 4), "z": 0.06, "steps_edge": 0}
    low = GR.down_flight(pf, lambda x, y: 0.0)
    assert low is not None and low["count"] == 1 and low["riser"] < 0.10
    assert low["low_step"] and low["cheeks"] == [] and "no cheek walls" in low["reason"]
    high = GR.down_flight(dict(pf, z=0.45), lambda x, y: 0.0)
    assert high is not None and not high["low_step"] and high["cheeks"]
