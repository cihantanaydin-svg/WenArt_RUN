"""28 Oct 2026 (real06 run 20261028-154514-full): Argus raised findings on things the run had built, and the AI architect
removed a piece on a reason that described another one.
- conservation C3: a hob or fridge built into its counter run (``built_into``) has the run's object, not its own;
- plan_vs_model: a counter outline read twice and built once as the run (``built_as``) is no missing piece;
- architect_ai: "f_L0_034 is a second dining table" removed the salon's bookshelf f_L0_034; a decision whose reason
  says its piece is another type is refused (``wrong_piece``) and asked again."""
from __future__ import annotations

from wenart.agent import architect_ai as AIA
from wenart.audit import conservation as CV
from wenart.audit import plan_vs_model as PV
from wenart.blender import architect_actions as AA

from test_decor_m8 import room_building


def _kitchen():
    b = room_building(4.0, 3.0, "kitchen", furniture=[("kitchen_counter", (2.0, 0.3), 0.0, (2.4, 0.6)),
                                                      ("kitchen_counter", (2.0, 0.3), 0.0, (0.9, 0.5)),
                                                      ("stove", (1.4, 0.3), 0.0, (0.6, 0.6))])
    run, twice, hob = b["furniture"]
    run["asset"] = {"method": "module"}
    twice.update(build=False, not_built_reason=f"architect F5: {twice['id']} (kitchen_counter) lies inside {run['id']} "
                                               f"(kitchen_counter): one object read twice; built once")
    hob.update(built_into=run["id"], asset={"method": "module"})
    return b, run, twice, hob


def test_an_appliance_built_into_its_run_has_the_runs_object():
    b, run, _twice, hob = _kitchen()
    man = {"objects": [{"kind": "furniture", "element_id": run["id"], "name": f"furn_{run['id']}"}]}
    pieces = lambda: [f["target"] for f in CV.in_scene(b, man) if f["evidence"]["collection"] == "furniture"]
    assert pieces() == []
    hob["built_into"] = "f_nope"
    assert pieces() == [hob["id"]]


def test_a_piece_built_as_another_is_no_missing_piece():
    b, run, twice, _hob = _kitchen()
    idx = PV.element_index(b)
    assert PV.built_as(twice["id"], idx) == run["id"] and PV.built_as(run["id"], idx) is None
    claim = {"kind": "fixture", "change": "missing_in_model", "aspect": "presence", "target": twice["id"],
             "room": "", "label": "", "severity": "major", "message": "the plan shows a counter that is not built"}
    kept, dropped = PV.check_plan_claims([claim], b, "L0")
    assert kept == [] and f"is built as {run['id']}" in dropped[0]["reason"]
    twice["not_built_reason"] = "the answer to AI.remove_piece: not built"       # a real loss stays a finding
    kept, _dropped = PV.check_plan_claims([claim], b, "L0")
    assert [f["target"] for f in kept] == [twice["id"]]


def test_a_decision_whose_reason_describes_another_piece_is_refused():
    assert AIA.wrong_piece("f_L0_034", "bookshelf", "f_L0_034 is a second dining table in the kitchen") == \
        "table_dining"
    assert AIA.wrong_piece("f_L0_034", "bookshelf", "f_L0_034 is a bookshelf in front of the window") is None
    assert AIA.wrong_piece("f_L0_034", "bookshelf", "f_L0_034 blocks the sofa's walkway") is None
    assert AIA.wrong_piece("f_L0_037", "armchair", "f_L0_037 is an armchair facing the wall") is None
    assert AIA.wrong_piece("f_L0_037", "chair", "f_L0_037 (an armchair) faces the wall") == "armchair"
    b = room_building(furniture=[("bookshelf", (3.0, 0.3), 0.0, (1.0, 0.35))])
    b["furniture"][0]["source"] = "added_by_ai"
    plan = AA.Plan(b)
    pid = b["furniture"][0]["id"]
    key, _ans, why = AIA._decision({"action": "remove_piece", "element": pid,
                                    "reason": f"{pid} is a second dining table in the kitchen"}, plan, b, "L0")
    assert key is None and why.startswith(f"{pid} is a bookshelf, not a table_dining")
    key, _ans, why = AIA._decision({"action": "remove_piece", "element": pid,
                                    "reason": f"{pid} is a bookshelf that blocks the window"}, plan, b, "L0")
    assert key == f"{AIA.AI_RULE}.remove_piece:{pid}", why
