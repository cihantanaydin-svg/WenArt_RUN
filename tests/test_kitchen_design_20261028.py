"""The kitchen reads as one designed kitchen (28 Oct 2026; user on real04 run 20261028-005318-full: "Kitchen design could
have been a lot better this is terrible"; on real06 run 20261027-222248-full: "What kind of a kitchen is this", "Why is
this closing the window"; and "More decor pieces needed ... kettle in the kitchen, microwave in the kitchen etc").

The rules are general (every project); the two runs are only the test cases:

- a drawn stove in a counter run is the run's hob: a hob unit at the drawn span with an oven under it, set into one
  continuous worktop (before: a gap of the run with a freestanding library cooker standing lower than the worktop);
  an agent pin of a library model does not take a hob or a fridge out of its run;
- every hob gets a cooker hood sized to it (chimney, under-cabinet or island hood) in the style's metal;
- the completion's wall cabinets are stretches of one wall run: exact edges, stopping at the hood (the hood between
  them), never over a window or a door, joined at the corners; the fit builds them of real wall units on the base
  units' joints; the build cuts them at the windows of the building as built (the architect may move one);
- a counter outline drawn inside a run is part of it, not a second run;
- the model review's M13 flags what is left (a hob without a hood, an appliance off the worktop line, wall cabinets
  over a window, odd boxes and gaps), M2 reads a run's worktop line, not its tap or hood;
- the worktop is dressed modestly (a microwave, a coffee machine or toaster, a kettle, a utensil pot, a board, a fruit
  bowl), every item checked: on the worktop, off the hob and its side gap and the sink, never in front of a window or
  a pass-through it would reach.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

import _m11_room as M
from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.blender import looks as LO
from wenart.blender import model_review as MR
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.furniture import complete as C
from wenart.furniture import decor as D
from wenart.furniture import fit as F
from wenart.furniture import placer as PL

ROOT = Path(__file__).resolve().parents[1]
ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def kitchen(window=(0.8, 1.0), sill=1.0, stove_x=2.3, extra=(), stove=True) -> dict:
    """A 4.0 x 3.0 m kitchen: counter A (3.4 m) on the north wall with a drawn sink under the window and a drawn
    0.75 x 0.55 m stove, counter B (2.4 m) on the east wall from the north-east corner, the door on the south wall."""
    a = fp("kA", "kitchen_counter", (1.7, 2.7), (3.4, 0.6), 270.0)
    b = fp("kB", "kitchen_counter", (3.7, 1.8), (2.4, 0.6), 180.0)
    sink = fp("sk", "sink_kitchen", (0.8, 2.7), (0.8, 0.5), 270.0)
    pieces = [a, b, sink]
    if stove:
        pieces.append(fp("st", "stove", (stove_x, 2.72), (0.75, 0.55), 270.0))
    return M.building(w=4.0, h=3.0, room_type="kitchen", window=window, sill=sill, door_x=1.0,
                      furniture=pieces + list(extra))


def by_id(b: dict) -> dict:
    return {f["id"]: f for f in b["furniture"]}


@pytest.fixture(scope="module")
def library():
    from wenart.furniture import catalog as CAT
    return CAT.load()


# --------------------------------------------------------------------------
# 1. The drawn stove is the run's hob, with an oven, in one worktop
# --------------------------------------------------------------------------

def test_a_drawn_stove_in_a_run_is_its_hob_at_the_drawn_span_with_an_oven():
    b = kitchen()
    found = F.kitchen_built_ins(b)
    assert found["sinks"] == {"sk": "kA", "st": "kA"}
    hints = found["hints"]["kA"]
    assert hints["hob_piece"] == "st" and hints["oven"] is True and hints["hood_kind"] == "chimney"
    assert hints["hob_span_m"] == [pytest.approx(0.225, abs=1e-3), pytest.approx(0.975, abs=1e-3)]
    assert hints["hood_top_m"] == pytest.approx(2.7)                  # the level's ceiling
    plan = MOD.plan_kitchen_run(dict(by_id(b)["kA"], module_hints=hints))
    assert "gaps" not in plan                                           # no freestanding cooker in a gap
    hob = next(m for m in plan["modules"] if m.get("holds") == "hob")
    assert hob["front"] == "oven" and hob["size_m"][0] == pytest.approx(0.75) and hob["pos_m"][0] == pytest.approx(0.6)
    rec = next(r for r in plan["built_ins"] if r["kind"] == "hob")
    assert rec["drawn_span"] and rec["shift_m"] == pytest.approx(0.0) and rec["hood"] == "chimney"
    tops = [m for m in plan["modules"] if m["kind"] == "worktop"]
    assert len(tops) == 1 and tops[0]["size_m"][0] == pytest.approx(3.4)  # one continuous worktop
    assert {c["kind"] for c in tops[0]["cutouts"]} == {"sink", "hob"}
    assert plan["worktop_m"] == pytest.approx(0.9)
    parts = MOD.module_parts(plan)
    assert {"hob", "ring", "hood", "chimney", "filter", "handle_post"} <= {p["role"] for p in parts}


def test_the_hob_plate_is_the_real_class_of_its_unit_and_a_wide_unit_gets_oven_side_fronts():
    assert [MOD.hob_plate_for(w) for w in (0.45, 0.60, 0.75, 0.80, 0.90)] == [0.30, 0.58, 0.70, 0.75, 0.80]
    five = MOD.hob_plate_parts(0.0, 0.90, 0.6, 0.9)
    four = MOD.hob_plate_parts(0.0, 0.60, 0.6, 0.9)
    rings = lambda parts: [p for p in parts if p["role"] == "ring" and len(p["verts"]) > 8]  # noqa: E731
    assert len(rings(five)) == 5 and len(rings(four)) == 4
    unit = MOD._module("base_unit", (0.75, 0.6, 0.76), (0.0, 0.0), "front", z_m=0.1, front="oven", holds="hob")
    parts = MOD._base_unit_parts(unit, {}, 0.6)
    fronts = [p for p in parts if p["role"] == "front"]
    xs = [v[0] for p in fronts for v in p["verts"]]
    assert min(xs) < -0.30 and max(xs) > 0.30                         # side fronts beside the 60 cm oven
    oven = [p for p in parts if p["key"] == "dark" and p["role"] == "front"]
    assert all(max(v[0] for v in p["verts"]) - min(v[0] for v in p["verts"]) <= MOD.KITCHEN_OVEN_W_M + 1e-6
               for p in oven)


def test_a_drawn_hob_wins_its_span_over_a_wide_sink_unit_and_a_second_stove_keeps_a_gap():
    run = fp("k1", "kitchen_counter", (1.5, 2.7), (3.0, 0.6), 270.0)
    plan = MOD.plan_kitchen_run(dict(run, module_hints={"sink_x_m": -0.3, "sink_w_m": 0.9, "hob_span_m": [0.2, 0.8]}))
    sink = next(m for m in plan["modules"] if m.get("holds") == "sink")
    hob = next(m for m in plan["modules"] if m.get("holds") == "hob")
    assert hob["pos_m"][0] == pytest.approx(0.5) and hob["size_m"][0] == pytest.approx(0.6)
    assert sink["pos_m"][0] + sink["size_m"][0] / 2.0 <= 0.2 + 1e-6            # the sink took a smaller real width
    b = kitchen(extra=[fp("st2", "stove", (3.0, 2.72), (0.6, 0.55), 270.0)])
    hints = F.kitchen_built_ins(b)["hints"]["kA"]
    assert hints["hob_piece"] == "st" and [r["id"] for r in hints["ranges"]] == ["st2"]


def test_a_pinned_hob_or_fridge_stays_built_into_its_run_and_the_agent_cannot_swap_it_out():
    b = kitchen(stove=False)
    hob = fp("h1", "stove", (2.3, 2.7), (0.6, 0.6), 270.0, source="added_by_ai", built_into="kA",
             built_in={"kind": "hob", "host": "kA", "oven": True}, asset_pin="hssd_some_stove")
    fridge = fp("fr", "fridge", (3.7, 1.0), (0.6, 0.6), 180.0, source="added_by_ai", built_into="kB",
                built_in={"kind": "fridge", "host": "kB"}, asset_pin="3dwh_some_fridge")
    b["furniture"] += [hob, fridge]
    found = F.kitchen_built_ins(b)
    assert found["sinks"]["h1"] == "kA" and found["sinks"]["fr"] == "kB"
    assert found["hints"]["kA"]["pins_not_used"] == ["h1"] and found["hints"]["kB"]["pins_not_used"] == ["fr"]
    from wenart.furniture import edit_ops as EO
    with pytest.raises(EO.EditRejected) as err:
        EO._swap_model(b, {"piece_id": "h1", "asset_id": "hssd_other"}, _OneStoveCatalog())
    assert err.value.check == "built_in"


class _OneStoveCatalog:
    def entry(self, asset_id):
        return {"id": asset_id, "type": "stove"}


def test_a_fridge_column_never_stands_in_front_of_a_window_or_a_pass_through():
    b = kitchen()
    fridge = fp("fr", "fridge", (0.8, 2.7), (0.6, 0.6), 270.0)
    assert F._opening_behind(b, fridge) is True                      # under the north window
    clear = dict(fridge, footprint=dict(fridge["footprint"], center=[2.9, 2.7]))
    assert F._opening_behind(b, clear) is False
    b["openings"].append({"id": "o1", "type": "opening", "level_id": "L0", "wall_id": "w_n", "center": [2.9, 3.05],
                          "width": 1.0})
    assert F._opening_behind(b, clear) is True                       # a pass-through counts


# --------------------------------------------------------------------------
# 2. The cooker hood
# --------------------------------------------------------------------------

def test_every_hob_gets_a_hood_sized_to_it_of_its_kind():
    assert [MOD.hood_width_for(w) for w in (0.45, 0.60, 0.75, 0.80, 0.90, 1.10)] == [0.60, 0.60, 0.75, 0.90, 0.90,
                                                                                        1.20]
    chimney = MOD.hood_module((-0.3, 0.3), 0.6, 0.9, False, {"hood_top_m": 2.7})
    assert chimney["hood"] == "chimney" and chimney["z_m"] == pytest.approx(0.9 + MOD.HOOD_CLEAR_M)
    assert chimney["pos_m"][1] + chimney["size_m"][1] / 2.0 == pytest.approx(0.3)   # its back on the wall
    assert chimney["chimney_top_m"] == pytest.approx(2.7) and chimney["material"] == "handle"
    island = MOD.hood_module((-0.3, 0.3), 0.9, 0.9, True, {"hood_top_m": 2.6})
    assert island["hood"] == "island" and island["pos_m"][1] == 0.0
    assert island["z_m"] == pytest.approx(0.9 + MOD.HOOD_ISLAND_CLEAR_M)
    under = MOD.hood_module((-0.3, 0.3), 0.6, 0.9, False, {"hood_kind": "under_cabinet", "hood_under_m": 1.55})
    assert under["hood"] == "under_cabinet" and under["z_m"] + under["size_m"][2] == pytest.approx(1.55)
    parts = MOD._hood_parts(under)
    assert "chimney" not in {p["role"] for p in parts}
    # the fit says which: a wall cabinet hung over the hob makes it an under-cabinet hood
    b = kitchen(extra=[fp("wc", "wall_cabinet", (2.3, 2.825), (0.8, 0.35), 270.0, height=0.6, mount_bottom_m=1.55)])
    hints = F.kitchen_built_ins(b)["hints"]["kA"]
    assert hints["hood_kind"] == "under_cabinet" and hints["hood_under_m"] == pytest.approx(1.55)


# --------------------------------------------------------------------------
# 3. The wall cabinets: one wall run of real units
# --------------------------------------------------------------------------

def hung(b: dict) -> list:
    out = copy.deepcopy(b)
    return C.hang_wall_cabinets(out["rooms"][0], b, out)


def x_span(piece: dict) -> tuple[float, float]:
    xs = [x for x, _y in PL.drawn_piece(piece).polygon().exterior.coords]
    return min(xs), max(xs)


def y_span(piece: dict) -> tuple[float, float]:
    ys = [y for _x, y in PL.drawn_piece(piece).polygon().exterior.coords]
    return min(ys), max(ys)


def test_wall_cabinets_stop_at_the_hood_and_the_window_and_meet_at_the_corner():
    b = kitchen()
    cabs = hung(b)
    north = sorted((c for c in cabs if c["rule"]["run"] == "kA"), key=lambda c: x_span(c)[0])
    east = [c for c in cabs if c["rule"]["run"] == "kB"]
    assert len(north) == 2 and len(east) == 1
    left, right = north
    # never over the window (0.3-1.3 m) or within 0.3 m of it; the hood's span (the 0.75 m hob) between them
    assert x_span(left)[0] >= 1.3 + C.WALL_CABINET_WINDOW_GAP_M - 1e-3
    assert x_span(left)[1] == pytest.approx(1.925, abs=1e-3) and x_span(right)[0] == pytest.approx(2.675, abs=1e-3)
    assert left["rule"]["ends"] == ["window", "hood"] and right["rule"]["ends"][0] == "hood"
    # the north run reaches past its counter's end to the east run's front: a butt, and a blind corner behind it
    assert x_span(right)[1] == pytest.approx(4.0 - C.WALL_CABINET_DEPTH_M, abs=1e-3)
    assert right["rule"]["ends"][1] == "corner_butt"
    assert "corner_blind" in east[0]["rule"]["ends"] and y_span(east[0])[1] == pytest.approx(3.0, abs=1e-3)
    assert all(c["mount_bottom_m"] == 1.45 and c["height"] == pytest.approx(0.7) for c in cabs)   # one line


def test_a_window_over_the_whole_wall_leaves_it_free_and_a_short_stretch_gets_no_lone_box():
    b = kitchen(window=(1.7, 3.4))
    assert not [c for c in hung(b) if c["rule"]["run"] == "kA"]
    assert C._spans_minus(0.0, 1.0, [(0.2, 0.4, "hood", "h"), (0.3, 0.5, "window", "w")]) == [
        (0.0, 0.2, "end", "hood"), (0.5, 1.0, "window", "end")]


def test_the_wall_run_is_built_of_real_units_on_the_base_joints(library):
    b = kitchen()
    out = copy.deepcopy(b)
    C.hang_wall_cabinets(out["rooms"][0], b, out)
    fitted = F.fit_building(out, library, style_family="modern", mode="relaxed")
    F.assert_only_assets_changed(out, fitted)
    after = by_id(fitted)
    run = after["kA"]["asset"]["module_plan"]
    joints = sorted({round(m["pos_m"][0] + s * m["size_m"][0] / 2.0, 3) for m in run["modules"]
                     if m["kind"] in ("base_unit", "filler") for s in (-1, 1)})
    for cab in (f for f in fitted["furniture"] if f["type"] == "wall_cabinet"):
        plan = cab["asset"]["module_plan"]
        assert cab["asset"]["method"] == "module" and plan["builder"] == "wall_run"
        units = [m for m in plan["modules"] if m["kind"] == "wall_unit"]
        for m in units:
            w = m["size_m"][0]
            assert m.get("corner") == "blind" or any(abs(w - s) <= MOD.WALL_RUN_TOL_M for s in MOD.WALL_RUN_WIDTHS_M)
            assert m["size_m"][1] == pytest.approx(C.WALL_CABINET_DEPTH_M) and m["z_m"] == 0.0
        assert plan["misaligned"] == 0
        if cab["rule"]["run"] == "kA":
            # the unit joints of the north run lie on the base joints (the cabinet's frame is the run's, shifted)
            shift = cab["footprint"]["center"][0] - after["kA"]["footprint"]["center"][0]
            inner = [round(m["pos_m"][0] - m["size_m"][0] / 2.0 + shift, 3) for m in units[1:]]
            assert all(min(abs(j - k) for k in joints) <= 0.011 for j in inner)
        if "corner_blind" in cab["rule"]["ends"]:
            assert any(m.get("corner") == "blind" for m in units)
        if "corner_butt" in cab["rule"]["ends"]:
            ends = [m for m in plan["modules"] if m["kind"] in ("wall_unit", "filler")]
            assert max(m["pos_m"][0] + m["size_m"][0] / 2.0 for m in ends) == pytest.approx(
                cab["footprint"]["size"][0] / 2.0, abs=1e-3)               # flush at the other run's front
    stove = after["st"]["asset"]
    assert stove["built_in"] == "kA" and "chimney hood" in stove["fallback_reason"].replace("-", " ")


def test_compose_aligned_keeps_hard_ends_flush_and_never_makes_a_lone_odd_box():
    got = MOD.compose_aligned(-0.85, -0.1531, [-0.5531], "window", "hood")
    assert [round(x1 - x0, 3) for x0, x1, _k in got["units"]] == [0.297, 0.4] and got["misaligned"] == 0
    assert got["units"][-1][1] == pytest.approx(-0.1531)              # flush at the hood
    butt = MOD.compose_aligned(0.5969, 1.4113, [1.0469, 1.1607], "hood", "corner_butt")
    covered = sum(x1 - x0 for x0, x1, _k in butt["units"]) + sum(x1 - x0 for x0, x1 in butt["fillers"])
    assert covered == pytest.approx(1.4113 - 0.5969, abs=1e-3) and all(x1 - x0 <= 0.08 + 1e-6 for x0, x1 in butt["fillers"])
    blind = MOD.compose_aligned(-1.0, 0.6, [-0.1, 0.2], "corner_blind", "door")
    assert blind["units"][0][2] == "corner_blind" and blind["units"][0][0] == pytest.approx(-1.0)
    assert MOD.compose_aligned(0.0, 0.25, [], "hood", "wall")["units"] == []      # no lone 25 cm box
    assert MOD.plan_wall_run(fp("w", "wall_cabinet", (0, 0), (0.25, 0.35), 270.0, height=0.7)) is None


def test_the_build_cuts_a_wall_cabinet_at_a_window_of_the_building_as_built():
    b = kitchen(window=None)
    cab = fp("wc", "wall_cabinet", (1.6, 2.825), (1.2, 0.35), 270.0, height=0.7, mount_bottom_m=1.45,
             rule={"run": "kA", "ends": ["open", "open"]})
    q, rec = MOD.clear_windows(cab, b)
    assert q is cab and rec is None                                       # no window: built as it is
    b["openings"].append({"id": "winX", "type": "window", "level_id": "L0", "wall_id": "w_n", "center": [1.6, 3.05],
                          "width": 0.5, "sill_height": 0.9, "height": 1.2})
    q, rec = MOD.clear_windows(cab, b)
    plan = q["asset"]["module_plan"]
    assert rec["windows"] == ["winX"] and rec["built"] and q["asset"]["method"] == "module"
    for m in (m for m in plan["modules"] if m["kind"] == "wall_unit"):
        x0, x1 = m["pos_m"][0] - m["size_m"][0] / 2.0, m["pos_m"][0] + m["size_m"][0] / 2.0
        assert x1 <= -0.25 - MOD.WALL_RUN_WINDOW_MARGIN_M + 1e-6 or x0 >= 0.25 + MOD.WALL_RUN_WINDOW_MARGIN_M - 1e-6
    wide = dict(b, openings=b["openings"][:-1] + [dict(b["openings"][-1], width=1.2)])
    q, rec = MOD.clear_windows(cab, wide)
    assert q is None and rec["built"] is False and "not built" in rec["reason"]
    high = dict(b, openings=b["openings"][:-1] + [dict(b["openings"][-1], sill_height=2.3, height=0.3)])
    assert MOD.clear_windows(cab, high)[1] is None                       # a window over the cabinet's top line


def test_a_counter_outline_drawn_inside_a_run_is_part_of_it():
    b = kitchen()
    b["furniture"].append(fp("kN", "kitchen_counter", (2.3, 2.72), (0.9, 0.48), 270.0))
    assert F.nested_counters(b) == {"kN": "kA"}
    found = F.kitchen_built_ins(b)
    assert found["sinks"]["kN"] == "kA" and found["hints"]["kA"]["outlines"] == ["kN"]
    plan = MOD.plan_kitchen_run(dict(by_id(b)["kA"], module_hints=found["hints"]["kA"]))
    assert {"id": "kN", "kind": "outline"} in plan["built_ins"]
    host = dict(by_id(b)["kA"], asset={"module_plan": plan})
    asset = F.built_in_fit(by_id(b)["kN"], host, "relaxed")
    assert asset["built_in"] == "kA" and "part of the kitchen run kA" in asset["fallback_reason"]
    assert not [c for c in hung(b) if c["rule"]["run"] == "kN"]          # no wall band of its own


# --------------------------------------------------------------------------
# 4. The model review: M13 kitchen design, M2 on the worktop line
# --------------------------------------------------------------------------

def _plan_of(b, run_id, hints):
    return MOD.plan_kitchen_run(dict(by_id(b)[run_id], module_hints=hints))


def test_m13_flags_a_hob_without_a_hood_a_cooker_in_a_gap_and_an_appliance_off_the_worktop_line():
    b = kitchen()
    old = MOD.plan_kitchen_run(dict(by_id(b)["kA"], module_hints={"ranges": [
        {"id": "st", "type": "stove", "x0_m": 0.225, "x1_m": 0.975}]}))
    by_id(b)["kA"]["asset"] = {"method": "module", "module_plan": old}
    by_id(b)["kB"]["asset"] = {"method": "module", "module_plan": _plan_of(b, "kB", {})}
    by_id(b)["st"]["asset"] = {"method": "library", "bbox_m": [0.75, 0.55, 0.77]}
    # an under-counter fridge with its own model beside the run's end, its top under the worktop line
    b["furniture"].append(fp("fr", "fridge", (3.7, 0.3), (0.6, 0.6), 180.0,
                             asset={"method": "library", "bbox_m": [0.6, 0.6, 0.82]}))
    got, n = MR.kitchen_design(b)
    rules = sorted(f["metrics"]["rule"] for f in got if f["target"] == "st")
    assert rules == ["hood", "worktop_line"] and n >= 3                 # no hood; a cooker in a gap of the run
    assert all(f["check"] == "M13" and f["severity"] == "major" for f in got if f["target"] == "st")
    off = [f for f in got if f["target"] == "fr"]
    assert len(off) == 1 and off[0]["metrics"]["top_m"] == pytest.approx(0.82) and off[0]["metrics"]["run"] == "kB"
    # the new kitchen: the hob built in with its hood: nothing for the stove
    hints = F.kitchen_built_ins(b)["hints"]["kA"]
    by_id(b)["kA"]["asset"] = {"method": "module", "module_plan": _plan_of(b, "kA", hints)}
    by_id(b)["st"]["asset"] = {"method": "module", "built_in": "kA"}
    got, _n = MR.kitchen_design(b)
    assert not [f for f in got if f["target"] == "st"]


def test_m13_flags_wall_cabinets_over_a_window_of_odd_widths_with_gaps_and_off_one_line():
    b = kitchen(window=(2.0, 0.6), sill=1.0)
    cabs = [fp("w1", "wall_cabinet", (0.6, 2.825), (0.69, 0.35), 270.0, height=0.7, mount_bottom_m=1.45),
            fp("w2", "wall_cabinet", (2.0, 2.825), (0.6, 0.35), 270.0, height=0.7, mount_bottom_m=1.45),
            fp("w3", "wall_cabinet", (3.0, 2.825), (0.6, 0.35), 270.0, height=0.6, mount_bottom_m=1.5)]
    b["furniture"] += cabs
    got, _n = MR.kitchen_design(b)
    by_rule = {}
    for f in got:
        by_rule.setdefault(f["metrics"]["rule"], []).append(f)
    assert [f["target"] for f in by_rule["covers_window"]] == ["w2"] and by_rule["covers_window"][0]["severity"] == \
        "critical"
    assert [f["target"] for f in by_rule["odd_width"]] == ["w1"] and K.kind_of(by_rule["odd_width"][0]) == "taste"
    assert by_rule["one_line"] and "gap" not in by_rule                  # the gaps beside the window are explained
    assert K.kind_of(by_rule["covers_window"][0]) == "no_sense"
    bare = kitchen(window=None)
    bare["furniture"] += [fp("w4", "wall_cabinet", (0.6, 2.825), (0.6, 0.35), 270.0, height=0.7, mount_bottom_m=1.45),
                          fp("w5", "wall_cabinet", (1.6, 2.825), (0.6, 0.35), 270.0, height=0.7, mount_bottom_m=1.45)]
    gaps = [f for f in MR.kitchen_design(bare)[0] if f["metrics"]["rule"] == "gap"]
    assert len(gaps) == 1 and gaps[0]["metrics"]["gap_m"] == pytest.approx(0.4)
    assert CS.cause_of(by_rule["covers_window"][0]) == "kitchen_design" and CS.REPORT_TO["kitchen_design"] == "fit"
    assert "kitchen_design" in CS.NO_TOOL_REASON and "M13" in MR.CHECKS


def test_m2_reads_a_module_run_at_its_worktop_line():
    manifest = {"objects": [{"kind": "furniture", "type": "kitchen_counter", "element_id": "kA", "room_id": ROOM,
                             "box3d": {"center": [0, 0, 1.4], "size": [3.4, 0.6, 2.8]},
                             "module": {"builder": "kitchen_run", "worktop_m": 0.9}}]}
    got, n = MR.working_heights(manifest, {ROOM: 0.0})
    assert n == 1 and got == []
    manifest["objects"][0].pop("module")
    got, _n = MR.working_heights(manifest, {ROOM: 0.0})
    assert got and "over its working height" in got[0]["message"]
    assert MOD.module_record({"builder": "kitchen_run", "modules": [], "footprint_m": [1, 1], "height_m": 0.9,
                              "worktop_m": 0.9})["worktop_m"] == 0.9


# --------------------------------------------------------------------------
# 5. The worktop, dressed modestly
# --------------------------------------------------------------------------

def _dress(b: dict) -> list:
    room = b["rooms"][0]
    pieces = [f for f in b["furniture"] if f.get("room_id") == room["id"]]
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{n[0]:03d}"

    return D.kitchen_worktop_decor(b, room, pieces, new_id)


def test_the_worktop_takes_small_appliances_and_decor_that_pass_the_code_checks():
    b = kitchen()
    items = _dress(b)
    types = [i["type"] for i in items]
    assert 3 <= len(items) <= D.KITCHEN_DECOR_MAX and len(set(types)) == len(types)
    # Argus (wenart/audit/lessons.py, U11) looks for these names in a kitchen
    assert {"microwave", "kettle"} <= set(types) and ({"coffee_machine", "toaster"} & set(types))
    pieces = by_id(b)
    for item in items:
        host = pieces[item["host_id"]]
        assert item["source"] == "added_by_ai" and item["method"] == "rule" and "worktop" in item["reason"]
        assert item["room_id"] == ROOM and host["type"] == "kitchen_counter" and len(item["size"]) == 3
        assert D.worktop_item_ok(item, host, b["furniture"], D.worktop_windows(host, b, b["rooms"][0]), items) is None
        assert tuple(item["size"]) == D.KITCHEN_DECOR_SIZES[item["type"]]
        assert item["type"] in P.SURFACE_DECOR_TYPES                    # the build rests it on the built worktop
    # off the hob and its side gap (the stove at 1.925-2.675 m), off the sink (0.4-1.2 m)
    for item in items:
        x0, x1 = item["center"][0] - item["size"][0] / 2.0, item["center"][0] + item["size"][0] / 2.0
        if item["host_id"] == "kA":
            assert x1 <= 1.925 - D.WORKTOP_HOB_CLEAR_M + 1e-6 or x0 >= 2.675 + D.WORKTOP_HOB_CLEAR_M - 1e-6
            assert x1 <= 0.4 - D.WORKTOP_SINK_CLEAR_M + 1e-6 or x0 >= 1.2 + D.WORKTOP_SINK_CLEAR_M - 1e-6
    b["decor"] = items
    assert _dress(b) == []                                              # dressed once


def test_no_worktop_item_stands_in_front_of_a_low_window_or_a_pass_through_and_none_without_a_run():
    low = kitchen(window=(1.7, 3.4), sill=0.92)                         # the whole north wall glazed from 0.92 m
    for item in _dress(low):
        assert item["host_id"] != "kA" or item["type"] == "chopping_board"
    b = kitchen(window=(3.15, 0.4), sill=0.95)
    host = by_id(b)["kA"]
    probe = {"type": "kettle", "center": [3.15, 2.88], "size": [0.22, 0.16, 0.25], "host_id": "kA",
             "rotation_deg": 0.0}
    assert "window" in D.worktop_item_ok(probe, host, b["furniture"], D.worktop_windows(host, b, b["rooms"][0]))
    board = dict(probe, type="chopping_board", size=[0.4, 0.25, 0.02], center=[3.15, 2.8])
    assert D.worktop_item_ok(board, host, b["furniture"], D.worktop_windows(host, b, b["rooms"][0])) is None
    b["openings"].append({"id": "o1", "type": "opening", "level_id": "L0", "wall_id": "w_n", "center": [3.0, 3.05],
                          "width": 0.8})
    assert any(s < 0.25 for _a, _b, s in D.worktop_windows(host, b, b["rooms"][0]))
    empty = M.building(w=4.0, h=3.0, room_type="kitchen", window=None, furniture=[])
    assert _dress(empty) == []


def test_the_build_slides_a_worktop_item_off_a_window_the_architect_moved_and_checks_it():
    b = kitchen(window=None)
    host = by_id(b)["kA"]
    hints = F.kitchen_built_ins(b)["hints"]["kA"]
    host = dict(host, asset={"module_plan": MOD.plan_kitchen_run(dict(host, module_hints=hints))})
    item = {"id": "dec_1", "type": "kettle", "center": [3.0, 2.88], "size": [0.22, 0.16, 0.25], "host_id": "kA",
            "rotation_deg": 0.0, "level_id": "L0"}
    assert MOD.worktop_item_window(item, host, b) is None
    built = copy.deepcopy(b)
    built["openings"].append({"id": "winM", "type": "window", "level_id": "L0", "wall_id": "w_n",
                              "center": [3.0, 3.05], "width": 0.6, "sill_height": 0.9, "height": 1.2})
    assert MOD.worktop_item_window(item, host, built) == "winM"
    slid = MOD.slide_worktop_item(item, host, built)
    assert slid is not None and MOD.worktop_item_window(slid, host, built) is None
    sx = slid["center"][0]
    assert abs(sx - 3.0) >= 0.3 + 0.11 - 1e-6                           # off the window
    assert sx - 0.11 >= 2.675 + MOD.WORKTOP_HOB_CLEAR_M - 1e-6 or sx + 0.11 <= 1.925 - MOD.WORKTOP_HOB_CLEAR_M + 1e-6


def test_the_kitchen_items_are_parametric_with_pbr_keys_inside_their_real_box():
    assert set(P.KITCHEN_DECOR_TYPES) == set(D.KITCHEN_DECOR_TYPES)
    for t in D.KITCHEN_DECOR_TYPES:
        w, d, h = D.KITCHEN_DECOR_SIZES[t]
        assert P.DECOR_DEFAULT_HEIGHT[t] == pytest.approx(h) and t in D.DECOR_TYPES and t in P.DECOR_TYPES
        parts = P.decor_parts(t, w, d, h)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= w + 1e-9 and y1 - y0 <= d + 1e-9 and z1 - z0 <= h + 1e-9 and z0 == 0.0
        assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS)
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    enum = schema["$defs"]["decor"]["properties"]["type"]["enum"]
    assert set(D.KITCHEN_DECOR_TYPES) <= set(enum)


# --------------------------------------------------------------------------
# 6. Fronts and handles follow the style
# --------------------------------------------------------------------------

def test_a_silent_style_takes_its_family_kitchen_look_for_the_kitchen_cabinets_only():
    style = {"family": "modern", "cabinets": {"front_style": None, "handle": None, "worktop": None}}
    counter = fp("k1", "kitchen_counter", (1.5, 2.7), (3.0, 0.6), 270.0)
    design, notes = LO.design_for(counter, style)
    assert (design["front_style"], design["handle"], design["worktop"]) == ("flat", "black", "stone")
    assert any("family's kitchen look" in n for n in notes)
    wall, _n = LO.design_for(fp("w1", "wall_cabinet", (1, 2.8), (0.6, 0.35), 270.0), style)
    assert "worktop" not in wall and wall["handle"] == "black"
    sideboard, _n = LO.design_for(fp("s1", "sideboard", (1, 1), (1.6, 0.45), 270.0), style)
    assert "handle" not in sideboard
    given = dict(style, cabinets={"front_style": "shaker", "handle": "brass", "worktop": "wood"})
    assert LO.design_for(counter, given)[0]["handle"] == "brass"         # the style's own look wins
    b = kitchen()
    assert C.rule_design(counter, b, style)["handle"] == "black"
    assert C.rule_design(counter, b, given)["front_style"] == "shaker"


def test_the_kitchen_handles_stand_on_feet():
    run = fp("k1", "kitchen_counter", (1.5, 2.7), (3.0, 0.6), 270.0)
    parts = MOD.module_parts(MOD.plan_kitchen_run(run))
    bars = [p for p in parts if p["role"] == "handle" and p["key"] == "handle"]
    posts = [p for p in parts if p["role"] == "handle_post"]
    assert bars and len(posts) == 2 * len(bars)
    for bar in bars:
        back = max(v[1] for v in bar["verts"])
        near = [p for p in posts if math.isclose(min(v[1] for v in p["verts"]), back, abs_tol=1e-6)]
        assert len(near) >= 2                                            # the feet carry the bar off the front
