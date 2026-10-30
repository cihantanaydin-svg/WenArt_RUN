"""A terrace beside the house takes the floor its doors and windows serve (wenart/blender/site.py ``floor_level``;
25 Oct 2026, user on real04 ext_7: "this section is not making any sense at all"). The east pool deck took the mean
ground under it (-1.40 m), half way between the basement and the ground floor: it buried the basement window, a
front court was cut into the deck and stepped bands stood around it. Now the deck lies at the basement floor like its
marked twin, a flight of steps leads up out of it onto the driveway, the driveway's retaining wall carries a guard and
its top follows the slope. CPU, pure."""
import json
from pathlib import Path

import pytest

from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_agent.json"
G = S.G


def _facades(window_bottom=-2.1, door_bottom=None):
    """A building wall at x = 0 facing +x; its basement floor -3.0, its ground floor 0.0."""
    ops = [{"id": "w", "building": "b", "type": "window", "level_id": "L-1", "bottom": window_bottom,
            "top": window_bottom + 1.2, "probe": (0.4, 3.0)}]
    if door_bottom is not None:
        ops.append({"id": "d", "building": "b", "type": "door", "level_id": "L0", "bottom": door_bottom,
                    "top": door_bottom + 2.1, "probe": (0.4, 5.0)})
    return {"openings": ops, "floors": {"b": [(-3.0, ["L-1"]), (0.0, ["L0"])]}}


DECK = [(0.25, 0.0), (4.0, 0.0), (4.0, 8.0), (0.25, 8.0)]


def test_a_terrace_never_buries_a_window_it_takes_the_floor_below():
    g = {"min": -2.6, "mean": -1.4, "max": -0.5}
    z, why, ids = S.floor_level(DECK, g, _facades())
    assert z == -3.0 and "L-1" in why and ids == ["w"]          # the ground floor (0.0) would bury the window
    assert S.floor_level(DECK, g, None) is None                  # no building facts: the mean ground stays
    far = {"openings": [dict(_facades()["openings"][0], probe=(9.0, 3.0))], "floors": _facades()["floors"]}
    assert S.floor_level(DECK, g, far) is None                   # no opening faces it


def test_a_door_onto_the_terrace_sets_its_level():
    g = {"min": -1.0, "mean": -0.4, "max": 0.2}
    z, why, _ = S.floor_level(DECK, g, _facades(window_bottom=0.9, door_bottom=0.0))
    assert z == 0.0 and "doors d" in why
    # every floor buries something: no snap (the light-well rules handle it)
    assert S.floor_level(DECK, {"min": 0.5, "mean": 0.6, "max": 0.7}, _facades(window_bottom=-3.5)) is None


def test_sloped_pieces_follow_the_ground_and_tall_cut_walls_carry_a_guard():
    v, f = S.sloped_box((0.0, 0.0), 2.0, 0.25, 0.0, -1.0, 0.0, 0.5)
    tops = sorted({round(p[2], 3) for k, p in enumerate(v) if k >= 4})
    assert tops == [0.0, 0.5] and min(p[2] for p in v) == -1.0 and len(f) == 6
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    pf = {"id": "t", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]], "z": -2.0, "sloped": False, "kind": "terrace",
          "edge": "retaining", "holes": [], "pools": []}
    parts = {p["part"]: p for p in S.platform_parts(pf, terrain)}
    assert "railing" in parts and all(w.get("guard") for w in parts["wall"]["walls"])   # a 2 m fall from the lawn
    pf["z"] = -0.8
    parts = {p["part"]: p for p in S.platform_parts(pf, terrain)}
    assert "railing" not in parts and not any(w.get("guard") for w in parts["wall"]["walls"])


def test_a_sunken_terrace_gets_a_flight_up_with_cheeks_and_a_hole_in_the_ground():
    site = {"paving": [{"id": "t", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]], "build": True}],
            "ground": {"points": [{"x": 3.0, "y": 2.0, "z": -0.5, "kind": "ground", "mark_id": "m"}]}}
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    pf = next(p for p in S.platforms(site, terrain) if p["id"] == "t")
    assert pf["z"] == -0.5 and pf["steps_dir"] == "up" and pf["edge"] == "steps"
    fl = pf["flight"]
    assert fl["count"] == 4 and fl["rise"] == pytest.approx(0.5) and len(fl["footprint"]) == 4
    parts = {p["part"]: p for p in S.platform_parts(pf, terrain)}
    assert "steps" in parts and parts["steps"]["verts"]
    top = max(p[2] for p in parts["steps"]["verts"])
    assert top == pytest.approx(0.0, abs=1e-6)                       # the last tread meets the ground
    holes = S.ground_holes({"outline": [], "platforms": [pf], "terrain": terrain})
    assert fl["footprint"] in holes
    # the wall on the steps edge leaves the flight's gap
    i = pf["steps_edge"]
    a, b = pf["polygon"][i], pf["polygon"][(i + 1) % len(pf["polygon"])]
    mid = G.segment_midpoint(a, b)
    pieces = [w for w in parts["wall"]["walls"] if w["edge"] == i]
    assert pieces and len(pieces) < len(S.wall_pieces(a, b, pf["z"], lambda x, y: 0.0))
    assert G.distance(mid, fl["mid"]) < 1e-9


@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_real04_east_pool_deck_lies_at_the_basement_floor_and_is_reached_from_the_driveway():
    from wenart.blender import build as BU

    prep = BU.prepare(json.loads(REAL04.read_text(encoding="utf-8")), "base", None)
    sp = prep["site"]
    by = {p["id"]: p for p in sp["platforms"]}
    assert by["sp_002"]["z"] == by["sp_001"]["z"] == -3.0                       # the twins agree
    assert by["sp_003"]["z"] == by["sp_004"]["z"] == 0.0                        # the copy b2, 3 m higher
    assert not any(w["opening_id"] == "win_L-1_004" for w in sp["wells"])       # no front court in the deck
    for pid in ("sp_002", "sp_003"):
        # 30 Oct 2026 (UL188): the flight up never climbs out onto the drive; (UL202) a walkable path reaches it
        assert by[pid]["steps_dir"] == "up" and by[pid].get("flight_lands_on") != "spk_001"
        assert by[pid]["outside_access"] in ("path", "on_path")
    a5 = next(q for q in prep["architect"]["questions"] if q["id"] == "A5")
    assert not any(a.get("ask") for a in a5["answers"])                         # no window asked to become a door
    bands = [p for p in sp["platforms"] if p.get("parent")]
    for p in bands:                                                              # bands never overlap each other
        c = G.polygon_centroid(p["polygon"])
        assert not any(G.point_in_polygon(c, q["polygon"]) for q in bands if q is not p), p["id"]
