"""30 Oct 2026 (real04 run 20261029-201533-full, the basement kitchen r_L-1_mutfak): no counter run left bare in its
view, and an under-counter fridge that reads as a fridge. CPU only.

What the run showed (furniture/real04/building_final.json, renders/real04/scene_manifest.json):

- The fridge f_L-1_090 (added_by_ai, the completion's under-counter fridge) was built: a 0.60 m unit with an appliance
  door in the module plan of the run f_L-1_004 (``built_ins``), no object of its own. Its steel door had a long bar
  along its top, a dishwasher's look, and the judge, told only "f_L-1_090 fridge", said it was missing.
- The styling sets of 29 Oct ran (the modern family's kitchen): eleven items, all on the hob run f_L-1_002 and the run
  f_L-1_001. The sink run f_L-1_003 / f_L-1_004 stands under the 4.16 m ribbon window win_L-1_003, its sill at
  0.90 m on a 0.90 m worktop: ``worktop_item_ok`` refused every item there, even a 2 cm board (the sill 0.00 m over
  the worktop), so the views of that run showed a bare worktop ("completely bare", judge D3 / Q13).

Now: a low item (``WORKTOP_WINDOW_LOW_M``, 0.15 m: a board, a fruit bowl, plates) may stand before a window, at
decor and at build (``modules.worktop_item_window``); a set for a free stretch goes to the run with the fewest items;
a run the sets leave bare gets one low set (``decor.bare_run_sets``); the under-counter fridge's handle stands
upright at its opening edge; the vision models are told a piece is built into a run.
"""
from __future__ import annotations

import json
from pathlib import Path

import _m11_room as M
from wenart.agent import critic_vision as CV
from wenart.agent import judge as J
from wenart.blender import modules as MOD
from wenart.furniture import decor as D

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "tests" / "fixtures" / "real04_kitchen_20261030.json"
ROOM = "r_L-1_mutfak"
RUNS = ("f_L-1_001", "f_L-1_002", "f_L-1_003", "f_L-1_004")


def _real04() -> dict:
    return json.loads(REAL04.read_text(encoding="utf-8"))


def _dress(b: dict, room_id: str, family: str = "modern") -> list[dict]:
    room = next(r for r in b["rooms"] if r["id"] == room_id)
    pieces = [f for f in b["furniture"] if f.get("room_id") == room_id]
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{n[0]:03d}"

    items = D.kitchen_worktop_decor(b, room, pieces, new_id)
    return items + D.kitchen_styling_decor(b, room, pieces, new_id, existing=items, family=family)


def _by_id(b: dict) -> dict:
    return {f["id"]: f for f in b["furniture"]}


# --------------------------------------------------------------------------
# real04's basement kitchen
# --------------------------------------------------------------------------

def test_real04_every_run_of_the_kitchen_is_dressed_and_the_sink_run_only_with_low_sets():
    b = _real04()
    room = next(r for r in b["rooms"] if r["id"] == ROOM)
    pieces = _by_id(b)
    items = _dress(b, ROOM)
    hosts = {i["host_id"] for i in items}
    assert set(RUNS) <= hosts                                        # no run bare in its view
    for item in items:
        host = pieces[item["host_id"]]
        windows = D.worktop_windows(host, b, room)
        others = [o for o in items if o is not item]
        if item["type"] != "cookware":                               # the pot and pan stand on the hob
            assert D.worktop_item_ok(item, host, b["furniture"], windows, others) is None, item
        if D.before_window(item, host, windows):
            # before the ribbon window (its sill on the worktop line): only a low set
            assert item["size"][2] <= D.WORKTOP_WINDOW_LOW_M + 1e-9, item
            assert MOD.worktop_item_window(item, host, b) is None     # the build keeps it where the decor put it
        assert item["source"] == "added_by_ai" and item["method"] == "rule" and item["reason"]
    sink_run = [i for i in items if i["host_id"] == "f_L-1_003"]
    # one low set (UL212: the fruit bowl now comes with the appliances, the styling pass dresses the sink run first)
    assert len(sink_run) == 1 and sink_run[0]["type"] in D.BARE_RUN_SETS
    assert "window" in sink_run[0]["reason"]
    kettle = next(i for i in items if i["type"] == "kettle")
    assert kettle["host_id"] != "f_L-1_003" and "by the sink;" not in kettle["reason"]   # it says where it stands
    # dressed once
    b["decor"] = items
    assert _dress(b, ROOM) == []


def test_real04_the_fridge_is_built_into_its_run_and_named_so_for_the_judge():
    b = _real04()
    fridge = _by_id(b)["f_L-1_090"]
    assert fridge["type"] == "fridge" and fridge["built_into"] == "f_L-1_004" and fridge["height"] < 1.0
    assert CV.piece_fact(fridge) == "f_L-1_090 fridge (an under-counter unit built into f_L-1_004)"
    assert CV.piece_fact(_by_id(b)["f_L-1_001"]) == "f_L-1_001 kitchen_counter"
    text, _allowed = J.view_facts(b, {"name": "cam_r_L-1_mutfak_2", "room_id": ROOM})
    assert "f_L-1_090 fridge (an under-counter unit built into f_L-1_004)" in text


# --------------------------------------------------------------------------
# The rules on a synthetic kitchen
# --------------------------------------------------------------------------

def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def _kitchen(window=(1.7, 3.4), sill=0.90) -> dict:
    """4.0 x 3.0 m: counter A (3.4 m) on the north wall under a ribbon window from the worktop line with a drawn sink,
    counter B (2.4 m) on the east wall with the stove (its hob)."""
    pieces = [fp("kA", "kitchen_counter", (1.7, 2.7), (3.4, 0.6), 270.0),
              fp("kB", "kitchen_counter", (3.7, 1.5), (2.4, 0.6), 180.0),
              fp("sk", "sink_kitchen", (1.2, 2.7), (0.8, 0.5), 270.0),
              fp("st", "stove", (3.72, 1.2), (0.6, 0.55), 180.0)]
    return M.building(w=4.0, h=3.0, room_type="kitchen", window=window, sill=sill, door_x=1.0, furniture=pieces)


def test_a_low_item_may_stand_before_a_window_a_tall_one_never():
    b = _kitchen()
    room = b["rooms"][0]
    host = _by_id(b)["kA"]
    windows = D.worktop_windows(host, b, room)
    assert windows and all(abs(s) < 1e-6 for _a, _b, s in windows)      # the sill on the worktop line
    for dtype, ok in (("fruit_bowl", True), ("plate_stack", True), ("chopping_board", True), ("kettle", False),
                      ("storage_jars", False), ("dried_grass_vase", False)):
        size = list(D.KITCHEN_DECOR_SIZES[dtype])
        item = {"type": dtype, "center": [2.6, 2.7 + 0.3 - size[1] / 2.0 - D.WORKTOP_BACK_M], "size": size,
                "host_id": "kA", "rotation_deg": host["footprint"]["rotation_deg"]}
        got = D.worktop_item_ok(item, host, b["furniture"], windows)
        assert (got is None) == ok, (dtype, got)
        assert (MOD.worktop_item_window(item, host, b) is None) == ok, dtype


def test_no_run_is_left_bare_and_the_free_stretch_sets_spread_over_the_runs():
    b = _kitchen()
    items = _dress(b, b["rooms"][0]["id"])
    on_a = [i for i in items if i["host_id"] == "kA"]
    assert on_a and all(i["size"][2] <= D.WORKTOP_WINDOW_LOW_M + 1e-9 for i in on_a)
    assert {i["host_id"] for i in items} == {"kA", "kB"}
    # a set for a free stretch goes to the run with the fewest items
    ctx = D._worktop_context(b, b["rooms"][0], b["furniture"])
    placed = [{"host_id": "kB", "center": [3.85, 0.5], "size": [0.2, 0.2, 0.2]}]
    got = D._worktop_candidates(ctx, "plate_stack", placed)
    assert got[0][1] == "kA"
    placed = [{"host_id": "kA", "center": [0.3, 2.85], "size": [0.2, 0.2, 0.2]},
              {"host_id": "kA", "center": [3.0, 2.85], "size": [0.2, 0.2, 0.2]}]
    assert D._worktop_candidates(ctx, "plate_stack", placed)[0][1] == "kB"


def test_the_under_counter_fridge_has_an_upright_handle_at_its_opening_edge():
    parts = MOD._appliance_fronts("fridge", 0.4, 0.6, -0.28, 0.1, 0.76, {})
    handles = [p for p in parts if p["role"] == "handle"]
    bar = max(handles, key=lambda p: max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"]))
    xs, zs = [v[0] for v in bar["verts"]], [v[2] for v in bar["verts"]]
    assert max(zs) - min(zs) > 5 * (max(xs) - min(xs))               # upright, not along the top (a dishwasher)
    assert max(zs) - min(zs) <= MOD.UNDER_FRIDGE_HANDLE_M + 1e-9
    assert (min(xs) + max(xs)) / 2.0 < 0.4                            # on the run's middle side of the door
    mirrored = MOD._appliance_fronts("fridge", -0.4, 0.6, -0.28, 0.1, 0.76, {})
    bar2 = max((p for p in mirrored if p["role"] == "handle"),
               key=lambda p: max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"]))
    assert sum(v[0] for v in bar2["verts"]) / len(bar2["verts"]) > -0.4


def test_the_shared_constants_agree():
    assert MOD.WORKTOP_WINDOW_LOW_M == D.WORKTOP_WINDOW_LOW_M
    assert all(D.KITCHEN_DECOR_SIZES[t][2] <= D.WORKTOP_WINDOW_LOW_M for t in ("fruit_bowl", "plate_stack",
                                                                               "chopping_board"))
    assert set(D.BARE_RUN_SETS) <= set(D.KITCHEN_DECOR_TYPES)
