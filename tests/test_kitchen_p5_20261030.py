"""The P5 kitchen again (30 Oct 2026, lessons UL147 and UL149, user after real04 run 20261029-201533-full: "good
inspiration photo for the kitchen", "this wall seems like missing the texture"): wall units up to the ceiling, the
wall run stops at a tall-unit column an added wall cabinet no longer blocks, the splashback runs into the corner."""
from wenart.blender import kitchen_details as KD
from wenart.blender import lighting as LT
from wenart.blender import modules as MOD
from wenart.blender import shell as SH
from wenart.furniture import fit as F


def _cabinet(w=2.4, hints=None, source="added_by_ai"):
    return {"id": "f_wc", "level_id": "L0", "room_id": "r1", "type": "wall_cabinet", "source": source,
            "footprint": {"center": [0.0, 0.0], "size": [w, 0.35], "rotation_deg": 0.0}, "front_deg": 270.0,
            "height": 0.7, "mount_bottom_m": 1.45, "module_hints": dict(hints or {})}


def test_modern_uppers_reach_the_ceiling():
    plan = MOD.plan_wall_run(_cabinet(hints={"ceiling_m": 2.6}), {"family": "modern"})
    assert abs(plan["height_m"] - (2.6 - 0.01 - 1.45)) < 1e-6
    assert all(abs(m["size_m"][2] - plan["height_m"]) < 1e-6 for m in plan["modules"] if m["kind"] == "wall_unit")
    assert any(a["detail"] == "UL147" for a in plan["details"]["applied"])


def test_uppers_stay_without_a_ceiling_or_in_a_family_without_the_rule():
    assert MOD.plan_wall_run(_cabinet(), {"family": "modern"})["height_m"] == 0.7
    assert MOD.plan_wall_run(_cabinet(hints={"ceiling_m": 2.6}), {"family": "industrial"})["height_m"] == 0.7


def test_a_high_ceiling_keeps_the_stacked_units_real():
    h, note = KD.upper_height(0.7, 1.45, 3.5, KD.family_rule("scandinavian"))
    assert h == KD.UPPER_TOP["max_m"] and "stacked" in note and "stays over them" in note
    plan = MOD.plan_wall_run(_cabinet(hints={"ceiling_m": 3.5}), {"family": "scandinavian"})
    assert all(m.get("stack_top_m") for m in plan["modules"] if m["kind"] == "wall_unit")


def test_the_wall_run_stops_at_the_column():
    plan = MOD.plan_wall_run(_cabinet(hints={"column_m": [[0.6, 1.2]], "ends": ["wall", "open"]}), {"family": "modern"})
    units = [m for m in plan["modules"] if m["kind"] in ("wall_unit", "filler")]
    assert max(m["pos_m"][0] + m["size_m"][0] / 2.0 for m in units) <= 0.6 + 1e-6
    assert plan["column_m"] == [[0.6, 1.2]]
    assert LT._wall_units_span(dict(_cabinet(), asset={"module_plan": plan}))[1] <= 0.6 + 1e-6


def test_an_added_wall_cabinet_no_longer_blocks_the_column():
    column = {"id": "c", "type": "tall_cabinet", "room_id": "r1",
              "footprint": {"center": [0.9, 0.0], "size": [0.6, 0.6], "rotation_deg": 0.0}}
    assert not F._column_blocked([_cabinet()], column)
    assert F._column_blocked([_cabinet(source="from_documents")], column)
    assert F._column_blocked([_cabinet(w=0.7)], dict(column, footprint=dict(column["footprint"], center=[0.1, 0.0])))


def test_the_splashback_runs_into_the_inside_corner():
    room = {"id": "r1", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    back = {"id": "a", "room_id": "r1", "type": "kitchen_counter",
            "footprint": {"center": [2.0, 2.7], "size": [2.8, 0.6], "rotation_deg": 0.0}}
    side = {"id": "b", "room_id": "r1", "type": "kitchen_counter",
            "footprint": {"center": [3.7, 1.8], "size": [2.4, 0.6], "rotation_deg": 90.0}}
    p, q, ids = SH.splashback_corner_ends(back, [back, side], room, (0.6, 3.0), (3.4, 3.0), (0.0, -1.0))
    assert ids == ["b"] and abs(q[0] - 4.0) < 1e-6 and abs(p[0] - 0.6) < 1e-6
    on = {"id": "c", "room_id": "r1", "type": "kitchen_counter",
          "footprint": {"center": [3.7, 2.7], "size": [0.6, 0.6], "rotation_deg": 0.0}}
    assert SH.splashback_corner_ends(back, [back, on], room, (0.6, 3.0), (3.4, 3.0), (0.0, -1.0))[2] == []
