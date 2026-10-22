"""Fix round after P5 (22 Oct 2026; pod P5, real04, the review of its agent log; track A_agent).

Checked, each against BASE 29e54d0 (the tests fail there) or a mutation:

- the memory is scoped to the building (``building_decor.json``'s sha) and the code: an earlier run's records (P5's
  memory.json holds M12, P3 and P5) neither refuse nor steer an edit, nothing is deleted, the views keep their shapes;
  a rejection about the round's finding list ("no target finding") refuses its repeat in that round only;
- the dry re-check measures the fitted boxes of ``building_final.json`` (``loop.fitted_view``): P5's console table
  f_L1_056 under the 0.82 m slope keeps its X2 and the shoe cabinet f_L1_050 gets no false X2 at its proxy height;
- an edit that re-creates the removed piece of its target finding under a new id keeps the finding
  (``causes.accept_edit`` with ``added``);
- a stale scene-manifest box of a piece an accepted edit removed is no "new critical finding" for the next edit
  (``ctx.round_changed``, the key-not-before rule while the roof is kept); a roof override still meets every box;
- a ``max_tries`` refusal closes the steps on its target and a session that keeps sending refused edits ends;
- ``dry_run`` of a level tool reaches the level validator (no ``target_finding`` schema error);
- the code critic reports a blocked preview (``camera_blocked``) and routes it to the camera tools;
- a placement finding that a drawn, code-typed piece does not fit its room is offered ``retype_piece``, never
  ``mark_not_furniture`` (P5: the coffee table f_L1_021 marked "a stair");
- an exterior camera refused inside a building gets the free stretch of its view line (P5's ext_front_y);
- the prompts and tool descriptions name the user's decisions of 22 Oct 2026.

The P5 run folder (``runs/20261017-224848-full``) is not in git; the tests that read it skip without it.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from test_agent_helpers import (FakeEdits, FixesWhatItTouched, ScriptedCritic, fake_validators, project, violation,
                                write_json)
from test_m13_agent import Clock, ctx_for, log_of
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import memory as MEM
from wenart.agent import model as MM
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.blender import exterior_checks as X

ROOT = Path(__file__).resolve().parents[1]
P5 = ROOT / "runs" / "20261017-224848-full" / "results"
P5_FURNITURE = P5 / "furniture" / "real04"
P5_AGENT = P5 / "agent" / "real04"
P5_RENDERS = P5 / "renders" / "real04"
REAL02 = ROOT / "results" / "furniture" / "real02" / "building_final.json"
needs_p5 = pytest.mark.skipif(not (P5_FURNITURE / "building_final.json").is_file(),
                              reason="the P5 run folder runs/20261017-224848-full is not on this machine")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# 1. The memory is scoped to the building and the code
# --------------------------------------------------------------------------

REJECTED = {"accepted": False, "failed_checks": ["front_into_wall: 0.01 m to the wall"]}


def test_records_of_another_building_neither_refuse_nor_steer(tmp_path):
    """Fails on BASE: memory.json had no run scope, so P5 refused 19 edits for M12 / P3 rejections."""
    out = project(tmp_path)
    m = MEM.Memory(out)
    m.visit("r1", 1)
    m.record("r1", 1, "rotate_piece", {"piece_id": "f1", "front_deg": 355}, REJECTED)
    m.record("r1", 1, "fix_fixture", {"piece_id": "f2"}, {"accepted": False,
                                                           "failed_checks": ["no valid spot within 0.50 m"]})
    m.tried("r1", 2)
    m.set_open("r1", ["move_group on g1"])
    m.refused()
    assert m.repeat_of("r1", "rotate_piece", {"piece_id": "f1", "front_deg": 355}) is not None
    # the decor stage made another building (another reading of the plan): a new run on it starts clean
    b = read(out / "building_decor.json")
    b["furniture"][0]["footprint"]["center"] = [2.1, 2.45]
    write_json(out / "building_decor.json", b)
    again = MEM.Memory(out)
    assert again.repeat_of("r1", "rotate_piece", {"piece_id": "f1", "front_deg": 355}) is None
    assert again.visits("r1") == 0 and again.no_spot("r1") == {} and again.refused_repeats == 0
    assert again.room("r1") == {"visits": [], "accepted": [], "rejected": [], "candidates_tried": [], "open": [],
                                "plans": []}
    s = again.summary("r1")
    assert s["visits"] == 0 and s["rejected"] == [] and s["candidates_tried"] == [] and s["open"] == []
    # nothing is deleted from the file; the old records come back with their building
    again.visit("r1", 1)
    raw = read(MEM.memory_path(out))["rooms"]["r1"]
    assert len(raw["rejected"]) == 2 and len(raw["visits"]) == 2
    write_json(out / "building_decor.json", read(out / "building_final.json"))
    back = MEM.Memory(out)
    assert back.repeat_of("r1", "rotate_piece", {"piece_id": "f1", "front_deg": 355})["reasons"] == \
        REJECTED["failed_checks"]
    assert back.visits("r1") == 1 and back.room("r1")["candidates_tried"] == [2]
    assert back.room("r1")["open"] == ["move_group on g1"] and back.no_spot("r1") == {
        "f2": {"round": 1, "reason": "no valid spot within 0.50 m"}}


def test_records_of_other_rules_are_not_repeated(tmp_path, monkeypatch):
    """Fails on BASE: a rejection made by older accept/refuse rules was refused again after a fix round."""
    out = project(tmp_path)
    MEM.Memory(out).record("r1", 1, "rotate_piece", {"piece_id": "f1", "front_deg": 355}, REJECTED)
    monkeypatch.setattr(MEM, "code_version", lambda: "another-code")
    assert MEM.Memory(out).repeat_of("r1", "rotate_piece", {"piece_id": "f1", "front_deg": 355}) is None


def test_a_version_1_memory_without_scopes_is_an_earlier_run(tmp_path):
    """Fails on BASE: the plain records of M12 / P3 / P5 (version 1) were read as this run's."""
    out = project(tmp_path)
    write_json(MEM.memory_path(out), {"version": 1, "refused_repeats": 71, "rooms": {"r1": {
        "visits": [1, 2, 3, 1, 2, 3], "candidates_tried": [1], "open": ["move_piece on f1: old"], "plans": [],
        "accepted": [], "rejected": [{"round": 6, "tool": "rotate_piece", "args": {"piece_id": "f1", "front_deg": 355},
                                      "key": MEM.edit_key("rotate_piece", {"piece_id": "f1", "front_deg": 355}),
                                      "reasons": ["old rule"]}]}}})
    m = MEM.Memory(out)
    assert m.repeat_of("r1", "rotate_piece", {"piece_id": "f1", "front_deg": 355}) is None
    assert m.visits("r1") == 0 and m.refused_repeats == 0
    assert m.summary("r1")["candidates_tried"] == [] and m.summary("r1")["open"] == []
    m.visit("r1", 1)
    data = read(MEM.memory_path(out))
    assert data["version"] == MEM.VERSION and data["refused_repeats"] == 0 and data["refused_repeats_legacy"] == 71
    assert data["rooms"]["r1"]["visits"][:6] == [1, 2, 3, 1, 2, 3]          # kept, not deleted
    assert len(data["rooms"]["r1"]["rejected"]) == 1 and MEM.Memory(out).data["refused_repeats_legacy"] == 71


def test_a_no_target_rejection_refuses_its_repeat_in_its_round_only(tmp_path):
    """Fails on BASE: P5 refused remove_piece f_L1_048 / f_L1_049 in later rounds for a round-1 "no target finding"
    (the finding list of round 1 had lost the X2 the dry re-check could not measure)."""
    out = project(tmp_path)
    m = MEM.Memory(out)
    args = {"piece_id": "f1"}
    m.record("r1", 1, "remove_piece", args, {"accepted": False, "failed_checks": [
        "acceptance: no target finding: an edit must name the finding it fixes (check id and target id)"]})
    m.record("r1", 1, "move_piece", {"piece_id": "f2", "center": [1, 1]}, {"accepted": False, "failed_checks": [
        "acceptance: target finding F6:f2 is not among the findings before the edit: nothing to fix there"]})
    assert m.repeat_of("r1", "remove_piece", args, round_no=1) is not None
    assert m.repeat_of("r1", "remove_piece", args, round_no=2) is None
    assert m.repeat_of("r1", "move_piece", {"piece_id": "f2", "center": [1, 1]}, round_no=2) is None
    # any other rejection is refused in every round of the scope
    m.record("r1", 1, "rotate_piece", {"piece_id": "f1", "front_deg": 355}, REJECTED)
    assert m.repeat_of("r1", "rotate_piece", {"piece_id": "f1", "front_deg": 355}, round_no=3) is not None
    # the tools pass the round
    reg = TL.build_registry()
    ctx = ctx_for(tmp_path / "t", memory=None)
    ctx.memory = MEM.Memory(ctx.project_out)
    ctx.memory.record("r1", 1, "rotate_piece", {"piece_id": "f2", "front_deg": 90}, {
        "accepted": False,
        "failed_checks": ["acceptance: no target finding: an edit must name the finding it fixes (check id and "
                          "target id)"]})
    ctx.round = 2
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f2", "front_deg": 90, "reason": "to the room"})
    assert not res.get("refused_by_memory") and res["accepted"]


@needs_p5
def test_p5s_memory_no_longer_refuses_the_stale_edits(tmp_path):
    """P5's memory.json (M12 + P3 + P5): seq 4673 refused remove_piece f_L1_048 citing P3 seq 3662, 5145 refused
    set_terrain planar citing M12 seq 377; the room r_L-1_salon had 12 visits. A run on another building starts
    clean; the file keeps every record."""
    out = project(tmp_path)
    src = P5_AGENT / "memory.json"
    write_json(MEM.memory_path(out), read(src))
    m = MEM.Memory(out)
    assert m.repeat_of("r_L1_koridor_2", "remove_piece", {"piece_id": "f_L1_048"}) is None
    assert m.repeat_of("building", "set_terrain", {"kind": "planar"}) is None
    assert m.visits("r_L-1_salon") == 0 and m.refused_repeats == 0 and m.summary("r_L-1_salon")["open"] == []
    old = read(src)
    assert len(old["rooms"]["r_L-1_salon"]["visits"]) == 12 and old["refused_repeats"] == 71
    m.visit("r_L-1_salon", 1)
    assert len(read(MEM.memory_path(out))["rooms"]["r_L-1_salon"]["visits"]) == 13      # nothing deleted


# --------------------------------------------------------------------------
# 2. The dry re-check measures the fitted boxes
# --------------------------------------------------------------------------

def _x2_pieces(b: dict) -> list[str]:
    prep = X._prep(b)
    out: list = []
    X._x2(b, prep, None, out)
    return sorted(v["target"] for v in out if str(v["target"]).startswith("f_"))


@needs_p5
def test_the_dry_recheck_sees_the_fitted_console_table_under_the_slope():
    """Fails on BASE (no fitted_view): the working building measured the console table at its 0.80 m parametric box
    and the shoe cabinet at its 1.00 m proxy height (false X2), the critic measured the fitted 0.84 m (X2 under the
    0.82 m slope) and 0.44 m."""
    agent, final = read(P5_FURNITURE / "building_agent.json"), read(P5_FURNITURE / "building_final.json")
    assert _x2_pieces(agent) == ["f_L1_050"]
    view, note = LP.fitted_view(agent, final)
    assert _x2_pieces(view) == _x2_pieces(final) == ["f_L1_056"]
    assert note["overlaid"] == len(agent["furniture"]) and note["refit"] == []
    # a 1 cm move keeps the fitted box (same id, type, size, pin and build flag)
    moved = copy.deepcopy(agent)
    p = next(f for f in moved["furniture"] if f["id"] == "f_L1_056")
    p["footprint"]["center"] = [p["footprint"]["center"][0] + 0.01, p["footprint"]["center"][1]]
    assert "f_L1_056" in _x2_pieces(LP.fitted_view(moved, final)[0])
    # only the copy changes
    assert next(f for f in agent["furniture"] if f["id"] == "f_L1_056").get("asset") != \
        next(f for f in view["furniture"] if f["id"] == "f_L1_056")["asset"]


def test_fitted_view_matches_by_id_type_size_pin_and_fits_the_rest():
    """A reused id of another type or size gets no overlay but the fit; a final without fitted pieces (a test
    project) changes nothing."""
    after = {"furniture": [
        {"id": "a", "type": "console_table", "footprint": {"center": [1, 1], "size": [0.9, 0.3]}},
        {"id": "b", "type": "console_table", "footprint": {"center": [2, 1], "size": [0.9, 0.3]}},
        {"id": "c", "type": "bookshelf", "footprint": {"center": [3, 1], "size": [0.8, 0.3]}, "build": False}]}
    final = {"furniture": [
        {"id": "a", "type": "console_table", "footprint": {"center": [1.5, 1], "size": [0.9, 0.3]},
         "asset": {"method": "library", "bbox_m": [0.9, 0.3, 0.84]}},
        {"id": "b", "type": "bookshelf", "footprint": {"center": [2, 1], "size": [0.9, 0.3]},
         "asset": {"method": "library", "bbox_m": [0.9, 0.3, 2.0]}}]}
    calls = []

    def fit(piece, building):
        calls.append(piece["id"])
        return {"method": "library", "bbox_m": [0.9, 0.3, 0.83]}
    view, note = LP.fitted_view(after, final, fit=fit)
    by = {f["id"]: f for f in view["furniture"]}
    assert by["a"]["asset"]["bbox_m"][2] == 0.84 and by["b"]["asset"]["bbox_m"][2] == 0.83
    assert "asset" not in by["c"] and calls == ["b"] and note == {"overlaid": 1, "refit": ["b"]}
    assert "asset" not in after["furniture"][0]                       # the input is never changed
    bare = {"furniture": [dict(f, asset=None) for f in final["furniture"]]}
    same, note = LP.fitted_view(after, bare, fit=fit)
    assert same is after and note["refit"] == []


def test_the_acceptance_rechecks_the_fitted_building(tmp_path):
    """Fails on BASE: AgentLoop.acceptance gave the dry re-check the working building without the fitted assets."""
    out = project(tmp_path)
    final = read(out / "building_final.json")
    final["furniture"][0]["asset"] = {"method": "library", "asset_id": "m1", "bbox_m": [1.6, 2.0, 1.1]}
    write_json(out / "building_final.json", final)
    seen = []

    def recheck(building, scene, manifest):
        seen.append(copy.deepcopy(building))
        return []
    loop = LP.AgentLoop(out, MM.MockModel(), clock=Clock(), recheck=recheck, apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, fit_fn=lambda p, b: None)
    ctx = loop.context(1)
    ctx.findings = [CC.finding(violation("F4", "major", "f1", "r1"))]
    after = copy.deepcopy(ctx.building)
    after["furniture"][0]["front_deg"] = 90.0
    verdict = loop.acceptance(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0}, {"changed_ids": ["f1"]},
                              after)
    assert seen and seen[0]["furniture"][0]["asset"]["bbox_m"] == [1.6, 2.0, 1.1]
    assert "asset" not in ctx.building["furniture"][0]                 # ctx.building is never changed
    assert verdict["accepted"] and verdict["fitted"]["overlaid"] == 1 and verdict["changed"] == ["f1"]


# --------------------------------------------------------------------------
# 3. A re-created piece keeps its finding
# --------------------------------------------------------------------------

def _x2(target, severity="major", room="r_L1_koridor_2"):
    return CC.finding({"check": "X2", "severity": severity, "target": target, "room_id": room,
                       "message": f"{target}: console_table with its top 0.84 m above the floor stands where the "
                                  f"sloped ceiling is 0.82 m high", "metrics": {}})


def test_a_relayout_that_recreates_the_piece_under_a_new_id_keeps_its_finding():
    """Fails on BASE: P5's relayout_room (seq 5383) "removed" X2:f_L1_049 by re-creating the console table as
    f_L1_056 at the same centre; round 4 measured X2:f_L1_056."""
    before = [_x2("f_L1_049")]
    after = [_x2("f_L1_056")]
    room = "r_L1_koridor_2"
    edit = {"target_finding": [{"check": "X2", "target": "f_L1_049"}],
            "removed": [{"id": "f_L1_049", "type": "console_table", "room_id": room}],
            "added": [{"id": "f_L1_056", "type": "console_table", "room_id": room}]}
    ok, why = CS.accept_edit(before, after, edit)
    assert not ok and why.startswith("finding X2:f_L1_049 is still there after the edit as X2:f_L1_056")
    assert "re-created console_table f_L1_049 as f_L1_056" in why
    # another type, another room, or no finding on the new piece: gone
    for added in ([{"id": "f_L1_056", "type": "bookshelf", "room_id": room}],
                  [{"id": "f_L1_056", "type": "console_table", "room_id": "r_L1_koridor"}]):
        assert CS.accept_edit(before, after, dict(edit, added=added))[0]
    assert CS.accept_edit(before, [], edit)[0]


def test_added_pieces_is_the_mirror_of_removed_pieces():
    before = {"furniture": [{"id": "a", "type": "console_table", "room_id": "r"},
                            {"id": "b", "type": "bookshelf", "room_id": "r", "build": False},
                            {"id": "c", "type": "chair", "room_id": "r"}]}
    after = {"furniture": [{"id": "a", "type": "console_table", "room_id": "r"},
                           {"id": "b", "type": "bookshelf", "room_id": "r"},
                           {"id": "c", "type": "armchair", "room_id": "r"},
                           {"id": "d", "type": "console_table", "room_id": "r"}]}
    assert [p["id"] for p in CS.added_pieces(before, after)] == ["b", "c", "d"]
    assert [p["id"] for p in CS.removed_pieces(after, before)] == ["b", "c", "d"]


# --------------------------------------------------------------------------
# 4. The stale scene-manifest box of a removed piece
# --------------------------------------------------------------------------

P4A_BOOKSHELF = {"id": "f_L1_058", "type": "bookshelf", "level_id": "L1",
                 "room_id": "r_L1_oyun_aktivite_ve_dinlenme_odasi_2", "source": "added_by_ai",
                 "footprint": {"center": [13.2015, 0.622], "size": [0.8, 0.3], "rotation_deg": 270.0},
                 "front_deg": 180.0, "height": 1.8, "status": "verified",
                 "asset": {"method": "library", "asset_id": "hssd_4ff59e80", "bbox_m": [0.8, 0.3289, 2.02],
                           "fit_scale": [1.0, 1.0, 1.0]}}
MANIFEST = {"objects": [{"name": "furn_f_L1_058", "wenart_id": "f_L1_058", "kind": "furniture",
                         "box3d": {"center": [13.1871, 0.622, 4.16], "size": [0.8, 0.3289, 2.02],
                                   "rotation_deg": 270.0}}]}


def _real02() -> dict:
    b = read(REAL02)
    b["furniture"] = [f for f in b["furniture"] if f.get("id") != "f_L1_058"] + [copy.deepcopy(P4A_BOOKSHELF)]
    return b


def _findings(b: dict, manifest: dict = MANIFEST) -> list[dict]:
    return [CC.finding(v) for v in X.check_exterior(b, manifest, None)["violations"]]


@pytest.mark.skipif(not REAL02.is_file(), reason="results/furniture/real02 not committed")
def test_a_removed_pieces_manifest_box_is_no_new_critical_for_the_next_edit():
    """Fails on BASE: after the accepted remove of f_L1_056 (P5 seq 4681) its manifest box came back as "new critical
    finding X2:f_L1_056" and rejected 8 edits in four other rooms (seq 4691-4757)."""
    b = _real02()
    room = P4A_BOOKSHELF["room_id"]
    other = CC.finding(violation("F6", "major", "f_x", "r_other", "no walkway"))
    before = _findings(b) + [other]
    assert any(f["target"] == "f_L1_058" and f["severity"] == "critical" for f in before)
    removed = copy.deepcopy(b)
    removed["furniture"] = [f for f in removed["furniture"] if f["id"] != "f_L1_058"]
    first = LP.after_findings(_findings(removed), before, {"f_L1_058", room}, removed, building_before=b)
    ok, why = LP.accept_edit(before, first, {"target_finding": [{"check": "X2", "target": "f_L1_058"}]})
    assert ok, why
    # the next, unrelated edit: the manifest still holds the box; it is neither new nor kept
    first = first + [other]
    after = LP.after_findings(_findings(removed), first, {"f_x", "r_other"}, removed, building_before=removed)
    assert not any(f["target"] == "f_L1_058" for f in after)
    ok, why = LP.accept_edit(first, after, {"target_finding": [{"check": "F6", "target": "f_x"}]})
    assert ok, why
    # the same through the round's changed ids alone (a roof edit after the remove)
    roofed = copy.deepcopy(removed)
    roofed["agent_overrides"] = {"exterior": {"roof": {"type": "mansard", "pitch_deg": 30}}}
    after = LP.after_findings(_findings(roofed), first, {"building"}, roofed, building_before=removed,
                              override={"roof": {"type": "mansard", "pitch_deg": 30}},
                              round_changed={"f_L1_058", room})
    assert not any(f["target"] == "f_L1_058" for f in after)


@pytest.mark.skipif(not REAL02.is_file(), reason="results/furniture/real02 not committed")
def test_a_roof_override_still_meets_every_manifest_box():
    """The verifier's case: a decor box 0.15 m under the current roof at (3.0, 6.0); a valid flat or mansard 30
    degree override brings it through the roof. That new critical stays and rejects the roof edit (the key-not-before
    rule applies only while the roof is kept)."""
    from wenart.blender import roof as R
    b = _real02()
    roof = X._prep(b)["roof"]
    z = R.surface_z(roof["equations"], 3.0, 6.0)
    box = {"name": "decor_dec_L1_900", "wenart_id": "dec_L1_900", "kind": "decor",
           "box3d": {"center": [3.0, 6.0, z - 0.2], "size": [0.3, 0.3, 0.1], "rotation_deg": 0.0}}
    manifest = {"objects": MANIFEST["objects"] + [box]}
    other = CC.finding(violation("X4", "major", "site", None, "no path to the entrance"))
    before = _findings(b, manifest) + [other]
    assert not any(f["target"] == "dec_L1_900" for f in before)
    for ov in ({"type": "flat"}, {"type": "mansard", "pitch_deg": 30}):
        assert X.validate_exterior_override(b, {"roof": ov})["ok"]
        bb = copy.deepcopy(b)
        bb["agent_overrides"] = {"exterior": {"roof": ov}}
        after = LP.after_findings(_findings(bb, manifest), before, {"building"}, bb, building_before=b,
                                  override={"roof": ov})
        assert any(f["target"] == "dec_L1_900" and f["severity"] == "critical" for f in after)
        ok, why = LP.accept_edit(before, after, {"target_finding": [{"check": "X4", "target": "site"}]})
        assert not ok and why.startswith("new critical finding X2:dec_L1_900"), why
    assert LP.roof_kept(None, b, copy.deepcopy(b)) and not LP.roof_kept({"roof": {"type": "flat"}}, b, b)


def test_the_acceptance_leaves_out_the_boxes_of_the_rounds_earlier_edits(tmp_path):
    """Fails on BASE: AgentLoop.acceptance knew only the edit's own changed targets, so a roof edit after an accepted
    remove met the removed piece's stale box as a new critical (the verifier's "remove, then a roof edit" case)."""
    out = project(tmp_path)
    stale = CC.finding({"check": "X2", "severity": "critical", "target": "f3", "room_id": "r2",
                        "message": "furn_f3 pokes through the roof (top 5.17 m)",
                        "metrics": {"top": 5.17, "source": LP.MANIFEST_SOURCE}})
    loop = LP.AgentLoop(out, MM.MockModel(), clock=Clock(), recheck=lambda b, s, m: [stale], apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, fit_fn=lambda p, b: None)
    ctx = loop.context(1)
    ctx.findings = [CC.finding({"check": "X2", "severity": "major", "target": "roof", "room_id": None,
                                "message": "roof overhang 0.00-0.10 m", "metrics": {}})]
    roof = {"roof": {"type": "gable", "pitch_deg": 30}}
    after = dict(ctx.building, agent_overrides={"exterior": roof})
    verdict = loop.acceptance(ctx, "set_exterior", dict(roof), {"changed_ids": []}, after)
    assert not verdict["accepted"] and verdict["reason"].startswith("new critical finding X2:f3")
    ctx.round_changed = {"f3", "r2"}                    # an accepted remove_piece f3 earlier in the round
    verdict = loop.acceptance(ctx, "set_exterior", dict(roof), {"changed_ids": []}, after)
    assert verdict["accepted"], verdict["reason"]


def test_an_accepted_verdict_adds_its_changed_ids_to_the_round(tmp_path):
    """Fails on BASE: no round_changed; the round's accepted edits were not remembered for the dry re-check."""
    ctx = ctx_for(tmp_path, acceptance=lambda c, t, a, r, b: {"accepted": True, "reason": "gone",
                                                              "after_findings": [], "changed": ["f2", "r1"]})
    ctx.findings = [CC.finding(violation("F4", "major", "f2", "r1"))]
    res = TL.build_registry().call(ctx, "rotate_piece", {"piece_id": "f2", "front_deg": 90, "reason": "to the room"})
    assert res["accepted"] and ctx.round_changed == {"f2", "r1"} and ctx.findings == []
    dry = TL.build_registry().call(ctx, "dry_run", {"tool": "rotate_piece", "args": {"piece_id": "f1",
                                                                                     "front_deg": 90}})
    assert dry["would_accept"] and ctx.round_changed == {"f2", "r1"}       # a dry run changes nothing


# --------------------------------------------------------------------------
# 5. max_tries closes the steps; repeated refusals end the session
# --------------------------------------------------------------------------

F3_F1 = violation("F3", "critical", "f1", "r1", "the bed's headboard is in the middle of the room")
F3_F2 = violation("F3", "critical", "f2", "r1", "the nightstand's back is off the wall")


def _move(center, reason="move the bed"):
    return {"tool_calls": [{"name": "move_piece", "arguments": {"piece_id": "f1", "center": center,
                                                                "reason": reason}}]}


def test_a_max_tries_refusal_closes_the_targets_steps_and_repeats_end_the_session(tmp_path):
    """Fails on BASE: P5's r2-s13 sent move_piece f_L1_024 six times after its max_tries refusal; the refusal neither
    closed the step nor ended the session, so every scripted call ran."""
    out = project(tmp_path)
    chat = [_move([2.0, 2.5], "reject: onto the wall")] + [_move([2.0, 2.5 + 0.1 * k]) for k in range(1, 8)]
    model = MM.MockModel(chat=chat)
    critic = ScriptedCritic([[F3_F1, F3_F2], [F3_F1, F3_F2]])
    loop = LP.AgentLoop(out, model, rerun=lambda s, v, r, f: {"status": "ok", "views": list(v)}, clock=Clock(),
                        code_critic=critic, recheck=FixesWhatItTouched(critic), vision=False, apply_edit=FakeEdits(),
                        validators=fake_validators(), out=lambda s: None, workers=1, max_rounds=1, max_tries=1)
    loop.run()
    # 1 validated + 1 max_tries (new refused target) + 2 repeats on it -> the session ends
    assert len(model.chat_requests()) == 2 + LP.REFUSALS_END_SESSION
    events = log_of(out)["events"]
    rej = [e["validation"]["failed_checks"][0].split(":")[0] for e in events if e["kind"] == "rejected_edit"]
    assert rej == ["score_drop", "max_tries", "max_tries", "max_tries"]
    end = [e for e in events if e["kind"] == "check" and e.get("tool") == LP.REFUSALS_CHECK]
    assert len(end) == 1 and end[0]["status"] == "session_end" and "f1" in end[0]["note"]
    opened = MEM.Memory(out).room("r1")["open"]
    assert any("on f1" in s and "[closed: max_tries: f1" in s for s in opened)
    assert any("on f2" in s and "closed" not in s for s in opened)
    assert LG.validate_log(log_of(out)) == []


def test_the_max_tries_refusal_says_the_target_is_done_for_the_round(tmp_path):
    ctx = ctx_for(tmp_path, max_tries=1)
    reg = TL.build_registry()
    assert reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 90, "reason": "x x"})["accepted"]
    res = reg.call(ctx, "rotate_piece", {"piece_id": "f1", "front_deg": 180, "reason": "x x"})
    assert not res["accepted"] and res["failed_checks"][0].startswith("max_tries: f1")
    assert res["step_closed"] and res["max_tries_target"] == "f1" and TL.refused_unvalidated(res)
    assert "every further edit of f1 is refused until the next round" in res["message"]
    assert not TL.refused_unvalidated({"accepted": False, "failed_checks": ["score_drop"]})


# --------------------------------------------------------------------------
# 6. dry_run of a level tool
# --------------------------------------------------------------------------

def test_a_dry_run_of_a_level_tool_reaches_the_level_validator(tmp_path):
    """Fails on BASE: the dry run added target_finding to every edit; the level schema (additionalProperties false)
    refused it: P5 seq 5142 "schema: <args>: Additional properties are not allowed ('target_finding' was
    unexpected)", and the repeat counted as a try."""
    from wenart.levels import edits as LE
    seen = []

    def level_edit(building, edit):
        seen.append(dict(edit))
        return LE.apply_level_edit(building, edit)
    ctx = ctx_for(tmp_path, level_edit=level_edit)
    ctx.findings = [CC.finding({"check": "L6", "severity": "major", "target": "terrain", "room_id": None,
                                "message": "the terrain slope 1:0.3 is over 1:3", "metrics": {}})]
    assert TL.target_findings(ctx, "set_terrain", {"kind": "flat"})
    res = TL.build_registry().call(ctx, "dry_run", {"tool": "set_terrain", "args": {"kind": "flat"}})
    assert seen and "target_finding" not in seen[0]
    assert not any("target_finding" in str(f) or str(f).startswith("schema") for f in res["failed_checks"]), res
    # a furniture dry run still carries its finding to the validator, as the real edit does
    edits = FakeEdits()
    ctx2 = ctx_for(tmp_path / "f", apply_edit=edits)
    ctx2.findings = [CC.finding(violation("F4", "major", "f1", "r1"))]
    TL.build_registry().call(ctx2, "dry_run", {"tool": "rotate_piece", "args": {"piece_id": "f1", "front_deg": 90}})
    assert edits.calls[-1]["target_finding"]["target"] == "f1"


# --------------------------------------------------------------------------
# 7. The code critic reports a blocked preview
# --------------------------------------------------------------------------

def _render(cam, room, depth_min, shares, start=0.05, resolution=(960, 540)):
    total = resolution[0] * resolution[1]
    return {"camera": cam, "room_id": room, "lens_mm": 16.0, "resolution": list(resolution),
            "clip": {"start_m": start}, "depth": {"min": depth_min},
            "index_stats": {str(k): {"pixels": int(v * total)} for k, v in shares.items()}}


def test_blocked_previews_are_code_findings_for_the_camera_tools():
    """Fails on BASE: nothing read the previews' depth or index; P5's cam_r_L1_banyo_1 (depth 0.0502 at clip 0.05,
    one element 55.7 %) passed every round and failed three GPU tests."""
    manifest = {"pass_index": {"dec_L1_011": 251, "f_L1_007": 12},
                "renders": [_render("cam_a_1", "ra", 0.0502, {0: 0.3, 251: 0.557, 12: 0.1}),
                            _render("cam_b_1", "rb", 0.8, {251: 0.52}),
                            _render("cam_c_1", "rc", 0.8, {12: 0.4, 0: 0.6}),
                            _render("cam_d_1", "rd", 0.055, {12: 0.2}),
                            _render("ext_1", None, 0.06, {5: 0.9}, start=0.1)]}
    scene = {"cameras": [{"name": "cam_d_1", "room_id": "rd", "kind": "interior",
                          "warning": "no free camera point; blocked unavoidable"},
                         {"name": "ext_1", "kind": "exterior"}]}
    got = {v["target"]: v for v in CC.blocked_items(manifest, scene)}
    assert sorted(got) == ["cam_a_1", "cam_b_1", "cam_d_1"]
    a = got["cam_a_1"]
    assert a["check"] == CC.CAMERA_BLOCKED_CHECK == CS.CAMERA_BLOCKED_CHECK and a["severity"] == "critical"
    assert a["metrics"]["largest_element"] == "dec_L1_011" and "the lens touches a surface" in a["message"]
    assert got["cam_b_1"]["severity"] == "major" and "fills 52.0 %" in got["cam_b_1"]["message"]
    d = got["cam_d_1"]
    assert d["severity"] == "minor" and d["metrics"]["blocked_unavoidable"] and "reported only" in d["message"]
    fa, fd = CC.finding(a), CC.finding(d)
    assert CS.cause_of(fa) == "interior_camera" and CS.tools_for_finding(fa) == ["set_camera", "remove_camera"]
    assert CS.cause_of(fd) == "blocked_unavoidable" and CS.tools_for_finding(fd) == []
    assert CS.REPORT_TO["blocked_unavoidable"] == "cameras"
    # a replayed (set 1) camera is frozen
    fr = CS.mark_replayed([CC.finding(a)], [{"name": "cam_a_1", "source": "replayed"}])[0]
    assert CS.cause_of(fr) == "replayed_camera"
    # the family runs in the critic; without a manifest it is unavailable
    res = CC.run({"furniture": []}, scene, manifest, plausibility_fn=lambda x: {"rooms": {}},
                 exterior_fn=lambda *a: {"violations": []}, views_fn=lambda *a: {"views": {}},
                 groups_fn=lambda x: {"rooms": {}}, levels_fn=lambda *a: [])
    assert {c["source"]: c["status"] for c in res["checks"]}["blocked"] == "ok"
    assert {f["target"] for f in res["findings"] if f["check"] == "camera_blocked"} == set(got)
    # the dry re-check cannot measure it: kept on an untouched view, gone on the moved one
    after = LP.after_findings([fa], [fa], {"cam_a_1"})
    assert after == [] and LP.after_findings([fa], [fa], {"f1"})[0]["target"] == "cam_a_1"
    # a vision V1 on the same view duplicates it
    from wenart.agent import critic_vision as CV
    answer = {"findings": [{"check": "V1", "severity": "major", "target": "cam_a_1", "message": "a lamp fills the view",
                            "evidence_image": 1}]}
    kept, dropped = CV.screen(answer, {"cam_a_1"}, 1, {"findings": [fa], "checks": []}, "ra")
    assert kept == [] and dropped[0]["dropped"] == "duplicate of a code finding"


@needs_p5
def test_p5s_blocked_bathroom_view_is_the_one_finding():
    rm = read(P5_AGENT / "previews" / "render_manifest.json")
    sm = read(P5_RENDERS / "scene_manifest.json")
    got = CC.blocked_items(rm, sm)
    assert [(v["target"], v["severity"]) for v in got] == [("cam_r_L1_banyo_1", "critical")]
    # a view carried from an earlier build keeps its index values: the name is marked uncertain
    assert got[0]["metrics"]["largest_element"] == "index 254 (an earlier build's index: the name may differ)"
    final = CC.blocked_items(read(P5_RENDERS / "render_manifest.json"), sm)
    assert [v["metrics"]["largest_element"].split(" ")[0] for v in final] == ["dec_L1_011"]


# --------------------------------------------------------------------------
# 8. A drawn, code-typed piece whose type does not fit its room is retyped, never marked
# --------------------------------------------------------------------------

def _code_typed_table():
    from test_agent_helpers import building
    b = building()
    p = b["furniture"][1]                     # f2, drawn in the bedroom
    p.update(type="table_coffee", type_method="rule",
             evidence=[{"file": "plan.dwg", "method": "vector", "confidence": 0.9}],
             footprint={"center": [0.9, 3.0], "size": [1.2, 0.6], "rotation_deg": 0.0})
    return b


def test_a_placement_wrong_type_on_a_code_typed_piece_offers_retype_not_a_removal():
    """Fails on BASE: F1 'table_coffee is not a piece of a hall room' on P5's f_L1_021 offered mark_not_furniture
    (a type_disagreement conflict lifts the mark lock) and the planner marked the drawn table 'a stair'."""
    b = _code_typed_table()
    f1 = CC.finding(violation("F1", "major", "f2", "r1", "table_coffee is not a piece of a bedroom"))
    allowed = {"f2": {t: {"allowed": True, "why": ""} for t in BR.PIECE_TOOLS}}
    fixable, not_yours = BR.classify([f1], b, "r1", allowed, {}, {})
    assert fixable and fixable[0]["tools"] == ["retype_piece", "set_room_type"]
    # an F9 duplicate outline keeps the mark; an AI-typed piece keeps every tool
    f9 = CC.finding(violation("F9", "major", "f2", "r1", "duplicate outline of the sofa"))
    assert "mark_not_furniture" in BR.classify([f9], b, "r1", allowed, {}, {})[0][0]["tools"]
    b["furniture"][1]["type_method"] = "ai"
    assert "mark_not_furniture" in BR.classify([f1], b, "r1", allowed, {}, {})[0][0]["tools"]
    assert BR.code_typed(_code_typed_table()["furniture"][1]) and not BR.code_typed(b["furniture"][1])


@needs_p5
def test_p5s_coffee_table_in_the_hall_is_offered_retype_only():
    dec = read(P5_FURNITURE / "building_decor.json")
    p = next(f for f in dec["furniture"] if f["id"] == "f_L1_021")
    f1 = {"id": "c:F1:f_L1_021", "check": "F1", "severity": "major", "target": "f_L1_021", "room_id": p["room_id"],
          "message": "table_coffee is not a piece of a hall room", "source": "code"}
    brief = BR.room_brief(dec, p["room_id"], findings=[f1])
    fx = next(f for f in brief["findings"]["fixable"] if f["id"] == f1["id"])
    assert "mark_not_furniture" not in fx["tools"] and fx["tools"][0] == "retype_piece"


# --------------------------------------------------------------------------
# 9. An exterior camera refused inside a building gets the free stretch
# --------------------------------------------------------------------------

@needs_p5
def test_a_camera_refused_inside_the_other_building_gets_the_free_stretch():
    """Fails on BASE (no hint): P5's add_camera ext_front_y at y 28 and y 20 stood inside b2 (y 18.57-30.57); the 6 m
    in front of the +y facade (y 12-18.27) were free and X6 'no frontal view' stayed open in all 4 rounds."""
    final = read(P5_FURNITURE / "building_final.json")
    ctx = TL.ToolContext(project_out=P5_FURNITURE, building=final)
    for y, z in ((28.0, 3.4), (20.0, 3.4)):
        entry = {"action": "add", "view_id": "ext_front_y", "kind": "exterior", "position": [8.5, y, z],
                 "target": [8.5, 12.5, 1.5], "lens_mm": 24, "reason": "frontal view"}
        failed = X.validate_camera_override(final, entry)["failed"]
        assert any("inside the building b2" in f for f in failed)
        hint = TL.free_strip_hint(ctx, entry, failed)[-1]
        assert hint.startswith("free on the view line from the target: (8.50, 12.50) to (8.50, 18.20)"), hint
        assert "a close view may be framed wider or tilted" in hint
    entry = {"action": "add", "view_id": "ext_9", "kind": "exterior", "position": [8.5, 16.0, 1.6],
             "target": [8.5, 12.5, 1.5]}
    assert TL.free_strip_hint(ctx, entry, ["eye height 2.96 m"]) == ["eye height 2.96 m"]


# --------------------------------------------------------------------------
# 10. The prompts and tools name the user's decisions of 22 Oct 2026
# --------------------------------------------------------------------------

def test_the_prompts_and_tools_name_the_decisions_of_22_oct():
    rule2 = P.PLANNER_SYSTEM_M12.split("\n2. ", 1)[1].split("\n3. ", 1)[0]
    rule3 = P.PLANNER_SYSTEM_M12.split("\n3. ", 1)[1].split("\n4. ", 1)[0]
    rule7 = P.PLANNER_SYSTEM_M12.split("\n7. ", 1)[1].split("\n8. ", 1)[0]
    assert "bathtub or shower up to 5 cm longer than its bay is a misread size" in rule2
    assert "(F1, G14), retype_piece gives it a type that fits" in rule3 and "never mark it or remove it" in rule3
    assert "retyped from its size, room and neighbours (adjusted_by_ai by code, drawn_type kept)" in rule3
    assert "An exterior view of a long, low building may be framed wider or tilted" in rule7
    assert "camera_blocked view" in rule7
    # the older rules stay
    assert "The room's plan crop or a view is no evidence" in rule3 and "move, snap or turn it" in rule3
    d = TL.DESCRIPTIONS
    assert "up to 5 cm longer than its bay" in d["fix_fixture"]
    assert "(F1, G14)" in d["retype_piece"] and "adjusted_by_ai by code" in d["retype_piece"]
    assert "never for a type that only does not fit the room" in d["mark_not_furniture"]
    assert "long, low building" in d["add_camera"] and "camera_blocked" in d["set_camera"]
    specs = {s["function"]["name"]: s["function"]["description"] for s in TL.build_registry().specs()}
    assert specs["fix_fixture"] == d["fix_fixture"]
