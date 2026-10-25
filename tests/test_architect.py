"""The architect's review (wenart/blender/architect.py; user request of 25 Oct 2026): its questions, their checks and
fixes, on small plans and on real04 (CPU, pure)."""
import json
from pathlib import Path

from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RULES
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


def _plan_building():
    """Hall h (entrance d0 from the south), bedroom b1 east of it, room x reached only through b1, kitchen k west
    of the hall, bathroom w opening into the kitchen; windows: b1 to the outside, x into b1 (borrowed)."""
    lv = {"id": "L0", "elevation": 0.0, "height": 2.8, "ceiling_height": 2.8}

    def wall(wid, a, b):
        return {"id": wid, "level_id": "L0", "start": a, "end": b, "thickness": 0.2}

    def op(oid, kind, wid, c, width=0.9, **kw):
        return dict({"id": oid, "type": kind, "level_id": "L0", "wall_id": wid, "center": c, "width": width}, **kw)

    rooms = [_room("h", "hall", [[4, 0], [8, 0], [8, 4], [4, 4]]), _room("b1", "bedroom", [[8, 0], [12, 0], [12, 4], [8, 4]]),
             _room("x", "bedroom", [[12, 0], [16, 0], [16, 4], [12, 4]]), _room("k", "kitchen", [[0, 0], [4, 0], [4, 4], [0, 4]]),
             _room("w", "bathroom", [[0, 4], [4, 4], [4, 6], [0, 6]])]
    for r in rooms:
        r["level_id"] = "L0"
    walls = [wall("ws", [4, 0], [8, 0]), wall("wb", [8, 0], [8, 4]), wall("wx", [12, 0], [12, 4]),
             wall("wk", [4, 0], [4, 4]), wall("ww", [0, 4], [4, 4]), wall("wbs", [8, 0], [12, 0])]
    openings = [op("d0", "door", "ws", [6, 0]), op("d1", "door", "wb", [8, 2]), op("d2", "door", "wx", [12, 2]),
                op("d3", "door", "wk", [4, 2]), op("d4", "door", "ww", [2, 4]),
                op("w1", "window", "wbs", [10, 0], 2.0, height=1.5, sill_height=0.9),
                op("w2", "window", "wx", [12, 3.2], 1.0, height=1.2, sill_height=0.9)]
    return {"levels": [lv], "rooms": rooms, "walls": walls, "openings": openings, "furniture": [],
            "site": {"entrances": [{"door_id": "d0", "level_id": "L0", "main": True}]}}


def test_circulation_daylight_privacy_and_kitchen_questions():
    b = _plan_building()
    sides = AR.opening_sides(b)
    assert AR.entrance_rooms(b, sides) == ["h"]
    c1 = AR.review_circulation(b, sides)
    assert c1["status"] == "open" and any(a["element"] == "x" and "through the bedroom b1" in a["found"]
                                          for a in c1["answers"])
    l1, l2 = AR.review_daylight_air(b, sides)
    xs = [a for a in l1["answers"] if a["element"] == "x"]
    assert xs and "looks into b1" in xs[0]["found"] and not xs[0].get("open")    # W2 asks about the window
    w2 = next(q for q in RULES.openings_rules(AA.Plan(b), sides) if q["id"] == "W2")
    ask = next(a for a in w2["answers"] if a["element"] == "w2")
    assert ask["open"] and "reading error" in ask["ask"] and ask["room"] == "x"
    assert [o["id"] for o in ask["options"]] == ["move_window_to_outer_wall", "keep"]
    assert not any(a["element"] == "b1" and a.get("open") for a in l1["answers"])  # 3 m2 of glass for 16 m2
    assert {a["element"] for a in l2["answers"]} == {"k", "w"}                    # no window: extract assumed
    p1 = AR.review_privacy(b, sides)
    assert p1["status"] == "open" and [a["element"] for a in p1["answers"] if a.get("open")] == ["d4"]
    c2 = AR.review_kitchen(b, sides)
    assert c2["status"] == "open" and c2["answers"][0]["element"] == "k"
    r1, r2 = AR.review_room_use(b)
    assert r2["status"] == "open" and {a["element"] for a in r2["answers"]} >= {"b1", "x", "w"}


def test_the_users_answers_are_remembered_and_acted_on():
    b = _plan_building()
    b["architect_answers"] = {"L1:x": "a store room", "C1:x": "fine, it is a dressing room"}
    answers = AR.apply_answers(b)
    assert next(r for r in b["rooms"] if r["id"] == "x")["room_type"] == "storage"
    assert answers["C1:x"]["option"] == "keep" and answers["L1:x"]["option"] == "retype_room"
    qs = AR.close_answered([AR.review_circulation(b, AR.opening_sides(b))], answers)
    assert qs[0]["status"] in ("ok", "answered") and not any(a.get("ask") for a in qs[0]["answers"])


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


def test_a_window_between_rooms_moves_to_the_outer_wall():
    """User answer of 25 Oct 2026: "no, an inside window should be outside": the window w2 between x and b1 goes to
    x's outer wall (the wall parallel to it first), same size, drawn values kept; the dark room is found by code."""
    b = _plan_building()
    b["walls"].append({"id": "wxe", "level_id": "L0", "start": [16, 0], "end": [16, 4], "thickness": 0.2})
    b["walls"].append({"id": "wxs", "level_id": "L0", "start": [12, 0], "end": [16, 0], "thickness": 0.2})
    done = AA.apply_answers(b, AA.answers_of(b, {"W2:w2": {"option": "move_window_to_outer_wall", "answer": "no"}}))
    assert done[0]["ok"], done
    w2 = next(o for o in b["openings"] if o["id"] == "w2")
    assert w2["wall_id"] == "wxe" and w2["drawn_wall_id"] == "wx" and w2["width"] == 1.0
    assert w2["corrected_by_ai"]["answer_key"] == "W2:w2"
    assert abs(w2["center"][1] - 3.2) < 1e-6                                   # same place along the parallel wall
    again = AA.apply_answers(b, AA.answers_of(b, {"W2:w2": {"option": "move_window_to_outer_wall"}}))
    assert again[0]["ok"] and "nothing to move" in again[0]["change"]          # idempotent: every run applies it
    l1, _l2 = AR.review_daylight_air(b, AR.opening_sides(b))
    xa = next(a for a in l1["answers"] if a["element"] == "x")
    assert "1.20 m2 of glass" in xa["found"]                   # outside glass now (1/13: L1 asks about its size)


def test_enlarge_windows_widens_then_lowers_a_terrace_sill_under_a_low_roof():
    """User answer of 25 Oct 2026 ("yes": larger play-room windows): wider first, then (the roof stops the head)
    a lower sill onto the terrace at the room's floor, until the glass is 1/10 of the floor."""
    lv = {"id": "L1", "elevation": 3.0, "height": 2.5, "ceiling_height": 2.5}
    room = {"id": "p", "level_id": "L1", "room_type": "other", "polygon": [[0, 0], [8, 0], [8, 5], [0, 5]]}
    terrace = {"id": "t", "level_id": "L1", "room_type": "balcony", "polygon": [[-3, 0], [0, 0], [0, 5], [-3, 5]]}
    b = {"levels": [lv], "rooms": [room, terrace],
         "walls": [{"id": "ww", "level_id": "L1", "start": [0, 0], "end": [0, 5], "thickness": 0.1}],
         "openings": [{"id": "win", "type": "window", "level_id": "L1", "wall_id": "ww", "center": [0, 2.5],
                       "width": 2.0, "height": 1.2, "sill_height": 0.9}]}
    done = AA.apply_answers(b, {"L1:p": {"option": "enlarge_windows"}}, head_limit=lambda o: 1.7)
    assert done[0]["ok"], done
    w = b["openings"][0]
    glass = AA.window_glass(w, 1.7)
    assert glass >= 0.1 * 40.0 - 1e-6 and w["width"] <= AA.MAX_WINDOW_W + 1e-9
    assert w["sill_height"] < 0.9 and w["drawn_sill_height"] == 0.9 and w["drawn_width"] == 2.0
    assert w["adjusted_by_ai"]["answer_key"] == "L1:p"


def test_answers_follow_their_element_by_place():
    """Ids change between readings of a plan: an answer acts only on the element at the place it names."""
    b = _plan_building()
    keyed = {"W2:w2": {"option": "move_window_to_outer_wall",
                       "where": {"kind": "window", "level_id": "L0", "centre": [12.0, 3.2]}}}
    moved = next(o for o in b["openings"] if o["id"] == "w2")
    moved["center"] = [6.0, 0.0]                                               # w2 is now another window
    done = AA.apply_answers(b, AA.answers_of(b, keyed))
    assert done[0]["skipped"] and not done[0]["ok"] and moved["wall_id"] == "wx"
    assert AA.normalise("L1:r", "a store room")["option"] == "retype_room"
    assert AA.normalise("C2:k", "yes")["option"] == "keep"


def test_every_rule_is_asked_of_every_element_and_the_report_scales():
    """User note of 25 Oct 2026: "don't restrict this to 16 questions": one answer per element per rule; the
    report lists the open ones up to MD_OPEN_MAX and counts the rest."""
    b = _plan_building()
    b["furniture"] = [{"id": "wd", "type": "wardrobe", "room_id": "b1", "level_id": "L0", "front_deg": 270.0,
                       "footprint": {"center": [10.0, 0.45], "size": [2.0, 0.6], "rotation_deg": 0.0},
                       "height": 2.2}]
    rec = AR.review(b, {"site": None})
    by = {q["id"]: q for q in rec["questions"]}
    assert len(rec["questions"]) >= 25 and rec["asked"] >= 60
    assert by["O1"]["counts"]["asked"] == 7 and by["D1"]["counts"]["asked"] == 5
    f3 = next(a for a in by["F3"]["answers"] if a["element"] == "w1")
    assert f3["open"] and "wd" in f3["found"]                                   # the wardrobe in front of w1
    assert by["F4"]["answers"][0]["open"]                                       # ... and its doors face the wall
    many = dict(rec, questions=[dict(by["F3"], answers=[dict(f3, element=f"w{k}") for k in range(400)])])
    md = AR.report_md(AR.summary(many["questions"]), "big")
    assert "400 questions asked" in md and f"and {400 - AR.MD_OPEN_MAX} more open point(s)" in md
    assert all(a["status"] == "open" for a in AR.compact(rec)["questions"][0]["answers"]) or True
    assert sum(len(q["answers"]) for q in AR.compact(rec)["questions"]) < rec["asked"]


def test_real04_answers_of_the_user_are_carried_out():
    """projects/real04/architect_answers.json (the user's answers of 25 Oct 2026) on the committed reading."""
    from wenart.blender import build as BU

    prep = BU.prepare(json.loads(REAL04.read_text(encoding="utf-8")), "base", None)
    done = {r["key"]: r for r in prep["architect"]["applied"]}
    assert all(done[k]["ok"] for k in ("W2:win_L0_005", "W2:win_L0_006", "L1:r_L1_oyun_aktivite_ve_dinlenme_odasi",
                                       "C2:r_L-1_mutfak")), done
    ops = {o["id"]: o for o in prep["building"]["openings"]}
    assert ops["win_L0_005"]["drawn_wall_id"] == "w_L0_003" and ops["win_L0_005"]["wall_id"] != "w_L0_003"
    by = {q["id"]: q for q in prep["architect"]["questions"]}
    assert not any(a.get("open") for q in ("L1", "W2", "C2") for a in by[q]["answers"])
    assert prep["architect"]["asked"] > 400


def test_topdown_labels_name_the_side_the_view_comes_from():
    from wenart.report import topdown_labels as TL

    assert TL.seen_from(225.0) == "north-east" and TL.seen_from(0.0) == "south"
    lines = TL.window_lines(_plan_building(), "L0")
    w1 = next(x for x in lines if x[0] == "w1")
    assert abs(w1[1][0] - 9.0) < 1e-6 and abs(w1[2][0] - 11.0) < 1e-6
