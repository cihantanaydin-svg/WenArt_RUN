"""30 Oct 2026 (lesson UL155, kitchen_details K16): a proper dishwasher. CPU only.

The user on real04 run 20261030-043021-full (cam_r_L-1_mutfak_*): "still not a proper dishwasher correct it". What the
run showed: no kitchen run ever held a dishwasher (``modules.plan_kitchen_run`` built sink, hob, oven and fridge units
only), and the under-counter fridge f_L-1_090 of the run f_L-1_004 was a bare steel slab between framed taupe fronts (a
steel bar handle on steel, hardly seen), read as a dishwasher, the 30 cm door beside it with its handle against it.

Now (a general rule for every kitchen): a run with a sink unit gets a dishwasher in the base unit beside the sink (60
cm, else 45 cm; never opening into a corner with another run when the other side is free; the stretch is composed
with a unit of a machine's width on the sink's side); the family's ``appliances`` look dresses it and the under-counter
fridge: ``integrated`` (a semi-integrated machine: a steel control strip with a display and buttons over a front that
matches the run with the run's handle; the fridge behind a matching front with a vent grille in the plinth) or
``steel`` (the industrial family, no style: a black glass strip, a steel door with a recessed panel and a long bar
handle); every front in the plane of the run's fronts; a single door beside an appliance has its handle on its far side.
"""
from __future__ import annotations

from wenart.blender import kitchen_details as KD
from wenart.blender import modules as MOD
from wenart.furniture import fit as F

DESIGN = {"front_style": "shaker", "colour": "muted taupe", "handle": "black", "worktop": "stone"}


def _run(w: float = 2.4, hints: dict | None = None, rid: str = "f_run", center=(0.0, 0.0), rot: float = 0.0,
         room: str = "r_k") -> dict:
    return {"id": rid, "type": "kitchen_counter", "level_id": "L0", "room_id": room, "height": 0.9,
            "footprint": {"center": list(center), "size": [w, 0.6], "rotation_deg": rot},
            "design": dict(DESIGN), "module_hints": dict(hints or {})}


def _plan(w: float = 2.4, family: str | None = "modern", **hints) -> dict:
    return MOD.plan_kitchen_run(_run(w, hints), {"family": family} if family else None)


def _unit(plan: dict, holds: str) -> dict:
    return next(m for m in plan["modules"] if m.get("holds") == holds)


def _parts(plan: dict, m: dict) -> list[dict]:
    return MOD._base_unit_parts(m, plan.get("design") or {}, plan["footprint_m"][1])


def _span(m: dict) -> tuple[float, float]:
    return m["pos_m"][0] - m["size_m"][0] / 2.0, m["pos_m"][0] + m["size_m"][0] / 2.0


def _front_plane(parts: list[dict]) -> float:
    return min(v[1] for p in parts if p["role"] == "front" for v in p["verts"])


def _xs(p: dict) -> tuple[float, float]:
    return min(v[0] for v in p["verts"]), max(v[0] for v in p["verts"])


# --------------------------------------------------------------------------
# the plan: a dishwasher beside every sink unit
# --------------------------------------------------------------------------

def test_a_sink_run_gets_a_dishwasher_in_the_unit_beside_the_sink():
    plan = _plan(sink_x_m=0.0, sink_w_m=0.6)
    sink, dw = _unit(plan, "sink"), _unit(plan, "dishwasher")
    s0, s1 = _span(sink)
    d0, d1 = _span(dw)
    assert abs(dw["size_m"][0] - 0.60) < 1e-6                 # a 60 cm machine first
    assert abs(d1 - s0) < 1e-6 or abs(d0 - s1) < 1e-6         # right beside the sink unit
    assert dw["front"] == "dishwasher" and dw["appliance"] == "integrated"
    assert "dishwasher 60 cm, semi-integrated" in plan["products"]
    assert plan["dishwasher"]["look"] == "integrated"
    assert any(a["detail"] == "K16" for a in plan["details"]["applied"])
    assert any("dishwasher" in n and "K16" in n for n in plan["notes"])


def test_a_narrow_stretch_beside_the_sink_takes_a_slimline_machine_and_none_without_a_sink():
    # real04's sink run f_L-1_003: 1.88 m, an 80 cm sink unit in its middle, 45 cm units beside it
    plan = _plan(1.8766, sink_x_m=0.0, sink_w_m=0.7885)
    dw = _unit(plan, "dishwasher")
    assert abs(dw["size_m"][0] - 0.45) < 1e-6 and "dishwasher 45 cm, semi-integrated" in plan["products"]
    assert not any(m.get("holds") == "dishwasher" for m in _plan(2.4)["modules"])
    assert not any(m.get("holds") == "dishwasher" for m in _plan(2.4, sink_x_m=0.0, dishwasher=False)["modules"])


def test_the_dishwasher_never_opens_into_a_corner_when_the_other_side_is_free():
    plan = _plan(1.8766, sink_x_m=0.0, sink_w_m=0.7885, end_kinds={"left": "join", "right": "corner"})
    assert _unit(plan, "dishwasher")["pos_m"][0] < 0.0
    plan = _plan(1.8766, sink_x_m=0.0, sink_w_m=0.7885, end_kinds={"left": "corner", "right": "wall"})
    assert _unit(plan, "dishwasher")["pos_m"][0] > 0.0


def test_the_stretch_beside_the_sink_is_composed_with_a_machine_width_unit_next_to_it():
    # a 0.90 m stretch left of the sink: a 90 cm pair of doors before, now 30 + 60 (the 60 at the sink)
    assert MOD.dishwasher_order([0.9], 0.9, -1.2, -0.3, (-0.3, 0.3)) == [0.3, 0.6]
    assert MOD.dishwasher_order([0.9], 0.9, 0.3, 1.2, (-0.3, 0.3)) == [0.6, 0.3]
    assert MOD.dishwasher_order([0.6, 0.4], 1.0, -1.3, -0.3, (-0.3, 0.3)) == [0.4, 0.6]
    assert MOD.dishwasher_order([0.4], 0.4, -0.7, -0.3, (-0.3, 0.3)) == [0.4]   # no machine fits: as composed
    assert MOD.dishwasher_order([0.9], 0.9, -1.2, -0.3, None) == [0.9]


# --------------------------------------------------------------------------
# the look: a real product, flush with the run
# --------------------------------------------------------------------------

def test_an_integrated_dishwasher_has_a_control_strip_a_matching_front_and_the_runs_handle():
    plan = _plan(sink_x_m=0.0, sink_w_m=0.6)
    dw = _unit(plan, "dishwasher")
    parts = _parts(plan, dw)
    strip = [p for p in parts if p["role"] == "front" and p["key"] == "steel"]
    assert len(strip) == 1
    sz = [v[2] for v in strip[0]["verts"]]
    assert abs((max(sz) - min(sz)) - MOD.KITCHEN_DISHWASHER_STRIP_M) < 1e-6
    assert any(p["key"] == "screen" for p in parts)                  # the display
    assert len([p for p in parts if p["role"] == "button"]) >= 4     # its buttons
    fronts = [p for p in parts if p["role"] == "front" and p["key"] == "front"]
    assert len(fronts) == 5                                          # the shaker door: a panel in a frame of four
    handles = [p for p in parts if p["key"] == "handle"]
    assert len(handles) == 1
    hx0, hx1 = _xs(handles[0])
    assert hx1 - hx0 > 0.1                                           # a horizontal bar over the door
    # the machine stands in a 0.82-0.875 m niche under the worktop: plinth to strip
    top = max(v[2] for p in parts for v in p["verts"] if p["role"] == "front")
    assert 0.80 <= top + MOD.KITCHEN_WORKTOP_M <= 0.90 + 1e-6


def test_a_steel_dishwasher_has_a_black_strip_a_recessed_steel_door_and_a_long_bar_handle():
    plan = _plan(family="industrial", sink_x_m=0.0, sink_w_m=0.6)
    dw = _unit(plan, "dishwasher")
    assert dw["appliance"] == "steel" and "dishwasher 60 cm, built-under steel" in plan["products"]
    parts = _parts(plan, dw)
    assert any(p["role"] == "front" and p["key"] == "dark" for p in parts)     # the black glass strip
    door = [p for p in parts if p["role"] == "front" and p["key"] == "steel"]
    assert len(door) == 5                                                       # a recessed panel in a frame
    assert max(min(v[1] for v in p["verts"]) for p in door) > _front_plane(door) + 0.002  # the panel sits back
    bars = [p for p in parts if p["role"] == "handle" and p["key"] == "steel"]
    long_bar = max(bars, key=lambda p: _xs(p)[1] - _xs(p)[0])
    assert _xs(long_bar)[1] - _xs(long_bar)[0] >= 0.75 * (dw["size_m"][0] - 0.004)
    assert any(p["key"] == "screen" for p in parts)


def test_every_appliance_front_is_flush_with_the_runs_fronts():
    for family in ("modern", "industrial"):
        plan = _plan(family=family, sink_x_m=0.0, sink_w_m=0.6, fridge_x_m=0.9)
        doors = [m for m in plan["modules"] if m["kind"] == "base_unit" and not m.get("holds")]
        plane = _front_plane(_parts(plan, doors[0]))
        for holds in ("dishwasher", "fridge"):
            got = _front_plane(_parts(plan, _unit(plan, holds)))
            assert abs(got - plane) < 1e-6, (family, holds, got, plane)


def test_the_under_counter_fridge_matches_the_run_or_keeps_its_steel_door():
    plan = _plan(sink_x_m=-0.6, sink_w_m=0.6, fridge_x_m=0.9)
    fridge = _unit(plan, "fridge")
    assert fridge["appliance"] == "integrated" and fridge["product"].endswith("integrated")
    parts = _parts(plan, fridge)
    assert not any(p["role"] == "front" and p["key"] == "steel" for p in parts)
    assert len([p for p in parts if p["role"] == "front" and p["key"] == "front"]) == 5
    assert len([p for p in parts if p["key"] == "handle"]) == 1
    vent = [p for p in parts if p["role"] == "grille"]
    assert vent and max(v[2] for p in vent for v in p["verts"]) < MOD.KITCHEN_PLINTH_M   # in the plinth
    steel = MOD.plan_kitchen_run(_run(2.4, {"sink_x_m": -0.6, "sink_w_m": 0.6, "fridge_x_m": 0.9}), None)
    sparts = _parts(steel, _unit(steel, "fridge"))
    assert any(p["role"] == "front" and p["key"] == "steel" for p in sparts)          # no style: as before


def test_no_neighbour_handle_stands_against_an_appliance():
    for family in ("modern", "industrial"):
        plan = _plan(2.4, family=family, sink_x_m=-0.6, sink_w_m=0.6, fridge_x_m=0.9)
        apps = [m for m in plan["modules"] if m.get("holds") in ("dishwasher", "fridge")]
        for m in plan["modules"]:
            if m["kind"] != "base_unit" or m.get("holds"):
                continue
            for p in _parts(plan, m):
                if p["key"] != "handle":
                    continue
                hx0, hx1 = _xs(p)
                for a in apps:
                    a0, a1 = _span(a)
                    assert hx1 <= a0 - 0.02 or hx0 >= a1 + 0.02, (family, m, a)
    # a door with an appliance on its right only has its handle on its left half (real04: the 30 cm door beside the
    # under-counter fridge of f_L-1_004)
    plan = _plan(2.1808, fridge_x_m=0.7904)
    fridge = _unit(plan, "fridge")
    door = next(m for m in plan["modules"] if m["kind"] == "base_unit" and m.get("front") == "door"
                and abs(_span(m)[1] - _span(fridge)[0]) < 1e-6)
    assert door["handle_side"] == -1.0
    handle = next(p for p in _parts(plan, door) if p["key"] == "handle")
    assert _xs(handle)[1] < door["pos_m"][0]


def test_a_single_door_beside_an_appliance_turns_its_handle_away():
    units = [{"kind": "base_unit", "size_m": [0.3, 0.6, 0.76], "pos_m": [0.0, 0.0], "front": "door"},
             {"kind": "base_unit", "size_m": [0.6, 0.6, 0.76], "pos_m": [0.45, 0.0], "front": "fridge",
              "holds": "fridge"},
             {"kind": "base_unit", "size_m": [0.45, 0.6, 0.76], "pos_m": [-0.375, 0.0], "front": "door"}]
    MOD.handle_sides(units)
    assert units[0]["handle_side"] == -1.0 and "handle_side" not in units[2]


# --------------------------------------------------------------------------
# the family table, the fit's end kinds, the review
# --------------------------------------------------------------------------

def test_every_family_has_an_appliance_look():
    for fam, row in KD.FAMILY_KITCHEN.items():
        assert row["appliances"] in KD.APPLIANCE_LOOKS, fam
    assert KD.family_rule("industrial")["appliances"] == "steel"
    assert KD.family_rule("modern")["appliances"] == "integrated"
    assert KD.appliance_look(None) == "steel" and KD.appliance_look(KD.family_rule("japandi")) == "integrated"


def test_a_run_drawn_in_two_pieces_meets_at_a_join_a_perpendicular_one_at_a_corner():
    a = _run(2.0, rid="a", center=(0.0, 0.0))
    b = _run(1.8, rid="b", center=(1.9, 0.0))                       # on the same line, its end at a's
    c = _run(1.6, rid="c", center=(3.1, 1.1), rot=90.0)             # across b's right end
    runs = [a, b, c]
    building = {"walls": [], "furniture": runs}
    assert F.run_end_kind(building, b, runs, "left") == "corner"    # the K1 reading stays as it was
    assert F.run_end_meets(building, b, runs, "left") == "join"
    assert F.run_end_meets(building, b, runs, "right") == "corner"
    assert F.run_end_meets(building, a, runs, "left") == "open"


def _built(plan: dict, rid: str = "f_run") -> dict:
    return {"id": rid, "type": "kitchen_counter", "room_id": "r_k", "build": True,
            "footprint": {"center": [0.0, 0.0], "size": [2.4, 0.6], "rotation_deg": 0.0},
            "asset": {"module_plan": plan, "style_family": "modern"}}


def test_the_review_names_a_sink_with_no_dishwasher():
    plan = _plan(sink_x_m=0.0, sink_w_m=0.6, fridge_x_m=0.9)
    found, n = KD.review({"furniture": [_built(plan)], "decor": []})
    assert n == 1 and not [f for f in found if f["problem"] == "dishwasher"]
    old = dict(plan, modules=[dict(m, holds=None, front="door") if m.get("holds") == "dishwasher" else m
                              for m in plan["modules"]])
    found, _n = KD.review({"furniture": [_built(old)], "decor": []})
    dw = [f for f in found if f["problem"] == "dishwasher"]
    assert len(dw) == 1 and dw[0]["severity"] == "minor" and dw[0]["lesson"] == "UL155"
