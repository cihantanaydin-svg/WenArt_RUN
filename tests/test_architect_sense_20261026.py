"""What a visitor sees at once (user, 26 Oct 2026: "why there is that many rain gutters in real06, why the sink is so
low, why doors are up ... real06 windows second floor: are the people going to jump off from it? ... I need ai models
to see understand and fix everything before even I look at it"): the architect's new questions and their default
fixes, the eaves past facade jogs, the building-wide downpipes, the glass guard and the fixtures at their working
height. CPU only; the building is a trimmed copy of real06's latest run (job 20261025-195332-full)."""
import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import build as BB
from wenart.blender import facade as FA
from wenart.blender import geom2d
from wenart.furniture import fit as FIT

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"


@pytest.fixture(scope="module")
def prep():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"          # no user answers
    return BB.prepare(b, "base", None)


def _opening(prep, oid):
    return next((o for o in prep["building"]["openings"] if o["id"] == oid), None)


def test_upper_floor_doors_and_bare_gaps_into_the_air_become_windows_by_default(prep):
    d = _opening(prep, "d_L1_001")                     # a 2.15 m "door" 3 m over the garden, no balcony drawn
    assert d["type"] == "window" and d["drawn_type"] == "door" and d["sill_height"] == pytest.approx(0.9)
    assert d["corrected_by_ai"]["answer_by"] == "architect" and "nothing outside" in d["corrected_by_ai"]["reason"]
    g = _opening(prep, "o_L1_006")                     # a bare gap in the upper facade
    assert g["type"] == "window" and g["drawn_type"] == "opening"
    by = {q["id"]: q for q in prep["architect"]["questions"]}
    assert not any(a.get("open") for a in by["E1"]["answers"])
    # a door into the air is never widened as a door (D1 asked it before E1 settled it)
    assert not any(a["element"] == "d_L1_010" and a.get("open") for a in by["D1"]["answers"])
    assert "E1:d_L1_010" in prep["architect_defaults"] and "D1:d_L1_010" not in prep["architect_defaults"]


def test_wall_hung_basins_hang_at_their_working_height(prep):
    pieces = {f["id"]: f for f in prep["building"]["furniture"]}
    for pid in ("f_L0_038", "f_L1_025", "f_L1_033"):          # 0.54, 0.50, 0.57 m models stood on the floor
        f = pieces[pid]
        top = AA.fitted_height(f) + float(f["mount_bottom_m"])
        assert top == pytest.approx(AA.BASIN_RIM_M, abs=0.005), pid
    h1 = next(q for q in prep["architect"]["questions"] if q["id"] == "H1")
    bowl = next(a for a in h1["answers"] if a["element"] == "f_L1_029")       # a 0.10 m bowl cannot hang alone
    assert bowl.get("open") and "mount_fixture" not in [o["id"] for o in bowl["options"]]


def test_a_room_no_door_reaches_gets_its_door_from_the_window_between_them(prep):
    w = _opening(prep, "win_L1_001")                   # dressing room <-> master bedroom
    assert w["type"] == "door" and w["drawn_type"] == "window" and w["corrected_by_ai"]["answer_by"] == "architect"
    c1 = next(q for q in prep["architect"]["questions"] if q["id"] == "C1")
    assert not any(a.get("open") and a["element"] == "r_L1_soyunma_odasi" for a in c1["answers"])


def test_the_defaults_are_the_lowest_source_the_ai_and_the_user_win():
    b = {"architect_defaults": {"E1:d1": {"option": "door_to_window", "by": "architect"}},
         "agent_overrides": {"architect": {"E1:d1": {"option": "french_window", "by": "ai"}}}}
    assert AA.answers_of(b)["E1:d1"]["option"] == "french_window"
    assert AA.answers_of(b, {"E1:d1": {"option": "keep"}})["E1:d1"]["option"] == "keep"
    rec = {"questions": [{"id": "E1", "answers": [
        {"element": "d1", "open": True, "default": "door_to_window",
         "options": [AA.option("door_to_window"), AA.option("keep")]},
        {"element": "d2", "open": True, "options": [AA.option("keep")]}]}]}
    assert set(AR.defaults_of(rec, {})) == {"E1:d1"} and AR.defaults_of(rec, {"E1:d1": {}}) == {}


def test_a_door_off_its_floor_snaps_to_it():
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}],
         "rooms": [{"id": "a", "level_id": "L0", "room_type": "kitchen", "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]},
                   {"id": "b", "level_id": "L0", "room_type": "bathroom",
                    "polygon": [[4, 0], [7, 0], [7, 4], [4, 4]]}],
         "walls": [{"id": "w", "level_id": "L0", "start": [4, 0], "end": [4, 4], "thickness": 0.1}],
         "openings": [{"id": "d", "type": "door", "level_id": "L0", "wall_id": "w", "center": [4, 2], "width": 0.8,
                       "height": 2.1, "threshold_z": 0.5}]}
    out = AA.apply_answers(b, {"D4:d": {"option": "snap_threshold", "by": "architect"}})
    assert out[0]["ok"] and b["openings"][0]["threshold_z"] == 0.0 and b["openings"][0]["drawn_threshold_z"] == 0.5


def test_the_eaves_run_straight_past_wall_piers():
    # a 10 x 6 m house with 1.2 m wide piers standing 0.33 m proud every 3 m along its south facade
    pts = [(0.0, 0.0)]
    for x0 in (1.5, 4.5, 7.5):
        pts += [(x0, 0.0), (x0, -0.30), (x0 + 1.2, -0.30), (x0 + 1.2, 0.0)]
    pts += [(10.0, 0.0), (10.0, 6.0), (0.0, 6.0)]
    out, closed = geom2d.close_jogs(pts, 0.6, inward_max=0.475 - 0.15)
    assert closed >= 3 and len(out) == 4 and geom2d.simple_polygon(out)
    assert G.polygon_area(out) == pytest.approx(60.0, abs=0.01)          # the eaves follow the facade line
    # a small overhang cannot cover the piers: the eaves line moves out to the pier fronts instead
    out2, _ = geom2d.close_jogs(pts, 0.6, inward_max=0.1)
    assert len(out2) == 4 and G.polygon_area(out2) == pytest.approx(63.0, abs=0.01)
    deep, _ = geom2d.close_jogs([(0, 0), (4, 0), (4, 3), (6, 3), (6, 0), (10, 0), (10, 6), (0, 6)], 0.6)
    assert len(deep) == 8                                                  # a 3 m notch stays open


def test_downpipes_stand_at_the_corners_three_metres_apart_one_per_50_m2():
    # a hip roof's eaves all round a 15 x 9 m outline (one closed gutter system)
    c = [(0.0, 0.0), (15.0, 0.0), (15.0, 9.0), (0.0, 9.0)]
    edges = [{"p": c[i], "q": c[(i + 1) % 4], "z": 6.0, "length": G.distance(c[i], c[(i + 1) % 4])} for i in range(4)]
    plan = FA.downpipe_plan(edges, 135.0)
    assert 2 <= len(plan) <= 3
    xy = [FA._edge_point(edges[i], t) for i, t in plan]
    assert all(math.hypot(a[0] - b[0], a[1] - b[1]) >= 3.0 for k, a in enumerate(xy) for b in xy[k + 1:])
    # a gable roof: two open eaves of 15 m: a pipe at each end of each (long runs drain both ways)
    g = [{"p": (0.0, 0.0), "q": (15.0, 0.0), "z": 5.0, "length": 15.0},
         {"p": (15.0, 9.0), "q": (0.0, 9.0), "z": 5.0, "length": 15.0}]
    assert len(FA.downpipe_plan(g, 135.0)) == 3                           # capped by the roof area
    assert len(FA.gutter_systems(g)) == 2 and len(FA.gutter_systems(edges)) == 1


def test_real06_gets_a_few_downpipes_not_twenty(prep):
    edges = FA.eaves_edges(prep["roof"])
    assert len(edges) <= 6
    area = G.polygon_area(prep["roof"]["outline"])
    assert len(FA.downpipe_plan(edges, area)) <= max(2, math.ceil(area / FA.KIT["area_per_pipe_m2"]))


def test_a_guard_is_one_glass_pane_across_the_whole_opening():
    boxes = FA.guard_boxes((0.0, 0.0), (2.0, 0.0), 3.0, 4.1, "L1", "w1")
    kinds = sorted(b["kind"] for b in boxes)
    assert kinds == ["guard_glass", "railing", "railing"]
    glass = next(b for b in boxes if b["kind"] == "guard_glass")
    assert glass["size"][0] >= 1.95 and glass["center"][2] + glass["size"][2] / 2.0 >= 4.07
    top = max(b["center"][2] + b["size"][2] / 2.0 for b in boxes)
    assert top == pytest.approx(4.1, abs=1e-6)


def test_the_fit_takes_a_basin_that_can_work_and_hangs_a_wall_hung_one():
    assert not FIT.working_top_ok("washbasin", 0.10)      # a bowl needs a counter
    assert FIT.working_top_ok("washbasin", 0.54) and FIT.working_top_ok("washbasin", 0.86)
    assert FIT.working_top_ok("washbasin", 1.10)          # a basin with its mirror (the size table bounds it)
    assert FIT.mount_for("washbasin", 0.54) == pytest.approx(0.31)
    assert FIT.mount_for("washbasin", 0.86) is None and FIT.mount_for("sofa", 0.4) is None


def test_doors_onto_terraces_and_roof_terraces_stay_doors():
    """real04 (a villa with roof terraces and pool decks): no door that lands on something becomes a window."""
    b = json.loads((ROOT / "results" / "furniture" / "real04" / "building_agent.json").read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"
    prep = BB.prepare(b, "base", None)
    assert not [k for k, v in prep["architect_defaults"].items() if v["option"] in ("door_to_window", "gap_to_door")]
    e1 = next(q for q in prep["architect"]["questions"] if q["id"] == "E1")
    assert e1["answers"] and not any(a.get("open") for a in e1["answers"])     # ground-floor doors with steps
