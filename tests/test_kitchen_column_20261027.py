"""A built-in fridge at a run end stands as a fridge-freezer column (27 Oct 2026; pod run 20261026-224516-full, real06:
the judge saw "no fridge": the completion's built-in fridge was a 60 cm steel door under the worktop, read as a
dishwasher). The fit says when the column may stand (``fridge_column``: no wall cabinet over the fridge); the module
plan builds it at a run end up to the wall units' top, the worktop, plinth and wall units stopping at its side."""
from __future__ import annotations

from wenart.blender import modules as MOD
from wenart.furniture import fit as F


def run(hints: dict, width: float = 2.4) -> dict:
    piece = {"id": "k1", "type": "kitchen_counter", "front_deg": 270.0,
             "footprint": {"center": [0.0, 0.0], "size": [width, 0.6], "rotation_deg": 0.0},
             "module_hints": dict({"fridge_w_m": 0.6, "fridge_piece": "f9", "hob_x_m": -0.6, "hob_w_m": 0.6,
                                   "hob_piece": "h1", "wall_units": True}, **hints)}
    return MOD.module_plan(piece)


def test_a_fridge_at_the_run_end_is_a_column():
    plan = run({"fridge_x_m": 0.9, "fridge_column": True})
    [col] = [m for m in plan["modules"] if m["kind"] == "tall_unit"]
    assert col["front"] == "fridge_column" and col["pos_m"][0] == 0.9 and col["size_m"][0] == 0.6
    assert col["z_m"] + col["size_m"][2] == MOD.KITCHEN_COLUMN_TOP_M and plan["height_m"] == MOD.KITCHEN_COLUMN_TOP_M
    for kind in ("worktop", "plinth"):
        for m in [m for m in plan["modules"] if m["kind"] == kind]:
            assert m["pos_m"][0] + m["size_m"][0] / 2.0 <= 0.6 + 1e-6            # they stop at its side
    walls = [m for m in plan["modules"] if m["kind"] == "wall_unit"]
    assert walls and max(m["pos_m"][0] + m["size_m"][0] / 2.0 for m in walls) <= 0.6 + 1e-6
    assert not [m for m in plan["modules"] if m["kind"] == "base_unit" and m.get("holds") == "fridge"]
    rec = next(r for r in plan["built_ins"] if r["kind"] == "fridge")
    assert rec["column"] is True and any("fridge-freezer column" in n for n in plan["notes"])
    parts = MOD.module_parts(plan)
    doors = [p for p in parts if p.get("key") == "steel" and p.get("role") == "front"]
    assert len(doors) == 2                                                      # the fridge over the freezer


def test_no_column_in_the_middle_of_a_run_or_under_a_wall_cabinet():
    middle = run({"fridge_x_m": 0.3, "fridge_column": True})
    assert not [m for m in middle["modules"] if m["kind"] == "tall_unit"]
    assert [m for m in middle["modules"] if m["kind"] == "base_unit" and m.get("front") == "fridge"]
    under = run({"fridge_x_m": 0.9, "fridge_column": False})
    assert not [m for m in under["modules"] if m["kind"] == "tall_unit"]
    short = run({"fridge_x_m": 0.3, "fridge_column": True}, width=1.0)       # too little counter would stay
    assert not [m for m in short["modules"] if m["kind"] == "tall_unit"]


def test_the_fit_says_whether_a_wall_cabinet_hangs_over_the_fridge():
    fridge = {"id": "f9", "type": "fridge", "room_id": "r", "footprint": {"center": [0.9, 0.0], "size": [0.6, 0.6],
                                                                         "rotation_deg": 0.0}}
    over = {"id": "w1", "type": "wall_cabinet", "room_id": "r",
            "footprint": {"center": [0.8, 0.12], "size": [0.6, 0.35], "rotation_deg": 0.0}}
    beside = dict(over, id="w2", footprint={"center": [-0.5, 0.12], "size": [0.6, 0.35], "rotation_deg": 0.0})
    assert F._wall_cabinet_over([fridge, over], fridge) is True
    assert F._wall_cabinet_over([fridge, beside], fridge) is False
    assert F._wall_cabinet_over([fridge, dict(over, room_id="other")], fridge) is False
