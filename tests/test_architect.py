"""The architect's review (wenart/blender/architect.py; user request of 25 Oct 2026): its questions, their checks and
fixes, on small plans and on real04 (CPU, pure)."""
import json
from pathlib import Path

from wenart.blender import architect as AR
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"
SQUARE = [[0.0, 0.0], [6.0, 0.0], [6.0, 4.0], [0.0, 4.0]]


def _deck(**kw):
    pf = {"id": "t1", "kind": "terrace", "polygon": SQUARE, "z": -1.4, "sloped": False, "pools": ["p1"],
          "steps_edge": None, "railing_edges": [0, 1], "against_edges": [2], "edge_floor": {},
          "edge_drops": {0: 1.0, 1: 2.5, 2: 0.0, 3: 0.6}}
    pf.update(kw)
    return pf


def test_steps_closed_by_a_railing_get_a_gap():
    pf = _deck(steps_edge=1)
    assert not AR.steps_open(pf)
    q = AR.review_access({"site": {"platforms": [pf]}}, [])
    assert q["status"] == "fixed" and pf["railing_gaps"] == [1] and AR.steps_open(pf)
    assert "railing" in q["answers"][0]["change"]
    runs = S.railing_runs((6.0, 0.0), (6.0, 4.0), 1, pf)                # the flight in the middle of the edge
    assert len(runs) == 2 and all(abs(a[0] - 6.0) < 1e-9 for a, _b in runs)


def test_a_closed_deck_gets_a_flight_on_its_lowest_free_edge():
    pf = _deck()
    q = AR.review_access({"site": {"platforms": [pf]}}, [])
    assert pf["steps_edge"] == 3 and 3 not in pf.get("railing_gaps", [])      # 0.6 m: the smallest drop, no railing
    assert q["answers"][0]["fixed"] and "flight of steps" in q["answers"][0]["change"]
    walled = _deck(edge_drops={0: 3.5, 1: 4.0, 2: 0.0, 3: 3.2})
    q = AR.review_access({"site": {"platforms": [walled]}}, [])
    assert q["status"] == "open" and walled["steps_edge"] is None


def test_a_door_from_the_house_is_access_enough():
    pf = _deck()
    door = {"opening": {"id": "d1"}, "centre": (3.0, 4.2), "outward": (0.0, -1.0), "bottom": -1.35, "half_t": 0.1}
    assert AR.doors_onto(pf, [door]) == ["d1"]
    q = AR.review_access({"site": {"platforms": [pf]}}, [door])
    assert q["status"] == "ok" and "door d1" in q["answers"][0]["found"] and pf["steps_edge"] is None
    assert AR.doors_onto(pf, [dict(door, bottom=0.0)]) == []                    # a floor 1.4 m up: no door to it


def _room(rid, rtype, poly):
    return {"id": rid, "level_id": "L1", "room_type": rtype, "polygon": poly}


def test_a_door_to_a_terrace_room_becomes_an_outside_door():
    b = {"levels": [{"id": "L1", "elevation": 3.0, "height": 2.8, "ceiling_height": 2.8}],
         "walls": [{"id": "w1", "level_id": "L1", "start": [4.0, 0.0], "end": [4.0, 4.0], "thickness": 0.2}],
         "rooms": [_room("hall", "hall", [[0, 0], [4, 0], [4, 4], [0, 4]]),
                   _room("teras", "balcony", [[4, 0], [8, 0], [8, 4], [4, 4]])],
         "openings": [{"id": "d1", "type": "door", "level_id": "L1", "wall_id": "w1", "center": [4.0, 2.0],
                       "width": 0.82}]}
    q, recs = AR.review_outside_doors(b)
    assert q["status"] == "fixed" and b["openings"][0]["outside_door"]["outside_room"] == "teras"
    assert recs[0]["outward"][0] > 0.9                                         # toward the terrace (+x)
    q2, _ = AR.review_outside_doors(b)
    assert q2["status"] == "ok"                                                # already an outside door


def test_drainage_answer_names_runs_without_a_pipe():
    boxes = [{"kind": "gutter", "size": [10, 0.12, 0.1]}, {"kind": "downpipe", "size": [0.1, 0.1, 6.0]}]
    q = AR.drainage_answer({"downpipes_not_placed": [{"station_m": None, "reason": "no wall"}]}, boxes)
    assert q["status"] == "open" and "1 downpipe" in q["answers"][0]["found"]
    assert AR.drainage_answer(None, [])["answers"][0]["found"].startswith("no gutter")


def test_a_deck_reached_only_by_steps_gets_a_path_to_the_site_paths():
    deck = {"id": "t1", "kind": "terrace", "polygon": SQUARE, "z": -1.0, "sloped": False, "pools": [],
            "steps_edge": 0, "railing_edges": [], "edge_drops": {0: 0.3}}    # steps down the south edge (y = 0)
    house = [[8.0, -10.0], [20.0, -10.0], [20.0, 10.0], [8.0, 10.0]]
    site = {"platforms": [deck], "outline": house, "pools": [], "wells": [],
            "areas": [{"id": "p0", "kind": "path", "polygon": [[-3.0, 12.0], [-1.8, 12.0], [-1.8, 30.0], [-3.0, 30.0]]}]}
    landing = AR.steps_landing(deck)
    assert abs(landing[0] - 3.0) < 1e-9 and landing[1] < 0                       # out from the middle of the edge
    q = AR._q("A2")
    AR._path_from_outside(deck, site, "terrace t1", q)
    new = [a for a in site["areas"] if a["id"].startswith("path_access_t1")]
    assert deck["outside_access"] == "path" and new and all(a["inferred"] for a in new)
    for a in new:                                                               # around the deck, never over it
        cx = sum(p[0] for p in a["polygon"]) / 4.0
        cy = sum(p[1] for p in a["polygon"]) / 4.0
        assert not (0.0 < cx < 6.0 and 0.0 < cy < 4.0)
    walled = dict(site, outline=[[-20.0, -20.0], [20.0, -20.0], [20.0, -0.5], [-20.0, -0.5]], areas=site["areas"][:1])
    q = AR._q("A2")
    AR._path_from_outside(dict(deck, id="t2"), walled, "terrace t2", q)      # the landing lies in the house
    assert q["status"] == "open"


def test_real04_review_asks_and_fixes():
    from wenart.blender import build as BU

    prep = BU.prepare(json.loads(REAL04.read_text(encoding="utf-8")), "base", None)
    rec = prep["architect"]
    by = {q["id"]: q for q in rec["questions"]}
    assert by["A3"]["status"] == "fixed" and {a["element"] for a in by["A3"]["answers"]} == {"d_L1_003", "d_L1_006"}
    decks = {pf["id"]: pf for pf in prep["site"]["platforms"]}
    assert all(AR.steps_open(decks[i]) for i in ("sp_001", "sp_002", "sp_003", "sp_004"))
    assert any(a["element"] == "win_L-1_003" and a.get("fixed") for a in by["A4"]["answers"])
    # 25 Oct 2026: every deck is reached from outside by its steps and a path; no window is asked to become a door
    assert all(decks[i].get("outside_access") in ("path", "on_path") for i in ("sp_001", "sp_002", "sp_003", "sp_004"))
    assert by["A5"]["status"] == "ok" and not any(a.get("ask") for a in by["A5"]["answers"])
    paths = [a for a in prep["site"]["areas"] if a["id"].startswith("path_access_")]
    keep = AR.site_keep_out(prep["site"], "none")
    assert paths and all(not any(S.G.point_in_polygon((sum(p[0] for p in a["polygon"]) / 4,
                                                       sum(p[1] for p in a["polygon"]) / 4), k) for k in keep)
                         for a in paths)
    md = AR.report_md(rec, "real04")
    assert md.startswith("# Architect's review: real04") and "How do people get" in md
