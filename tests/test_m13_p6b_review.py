"""Fix round after P6b (23 Oct 2026), review: track A_agent and D_data findings and two open asks of the integration.

Checked, each against HEAD 86cdeff (the tests fail there) or a mutation:

1. a ``set_room_type`` changes its room's render (floor, walls, light), so a vision R1 on the room (whose only tool is
   set_room_type) is cleared, while a vision "the room is empty" (``empty_room``) stays in the dry re-check
   (``loop.room_type_kept``) and the edit aimed at it is refused with ``ROOM_TYPE_NOTE``;
2. an edit accepted under ``causes.critical_cleared`` (a critical gone, a major kept) counts as removing its finding in
   metric 7 (``metrics.edit_target_keys`` leaves out ``evidence.acceptance.kept``); the acceptance's ``kept`` is
   ``accept_edit``'s own keys (``causes.kept_targets``: an S2 target without its cut stands for its cuts);
3. ``causes.fixture_layout_blocked`` counts only the drawn pieces as obstacles: a drawn fridge in a door swing whose
   only free spots an AI-added sideboard covers keeps fix_fixture (a drawn sideboard there still holds it);
4. the prep job's GPU test ``test_attribution_is_complete`` compares the decoded credit (``copy.plain_text``) and
   asks for a licence flag only when it limits the use (``none`` is no flag);
5. ``PLANNER_SYSTEM_M12`` says that complete_group takes a drawn anchor typed by code from the drawing too;
6. the solver's front partner (the coffee table) tries its next (size, gap) options when no candidate passes the final
   check; a solve that passes keeps its first-fit table (P4a real02: f_L-1b_041 gets a 0.8 x 0.5 table, its F3 and G2
   go with no new finding; on the committed real02 / real03 / real04 buildings and P4a's real02 only that group
   changes).

The P4a run folder (``runs/...``) is not in git; the test that reads it skips without it.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

import _m11_room as M
from test_m13_p6b_agent import _loop, finding
from wenart.agent import causes as CS
from wenart.agent import loop as LP
from wenart.agent import metrics as AM
from wenart.agent import prompts as P
from wenart.assets import objaverse as OV
from wenart.furniture import edit_ops as E
from wenart.furniture import groups as GR
from wenart.furniture import placer
from wenart.furniture import plausibility as PL
from wenart.furniture import solver as SV
from wenart.run import copy as CP

ROOT = Path(__file__).resolve().parents[1]
P4A = ROOT / "runs" / "20261017-072801-full" / "results" / "furniture" / "real02" / "building_final.json"
needs_p4a = pytest.mark.skipif(not P4A.is_file(), reason="the P4a run folder runs/20261017-072801-full is not here")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# 1. set_room_type: the room's render changes, its furnishing claims stay
# --------------------------------------------------------------------------

R1_TEXT = "The room has a bathtub and a toilet but is typed as a bedroom"
EMPTY_TEXT = "The room is completely empty; the render shows only bare walls and floor"


def test_set_room_type_clears_a_vision_r1_while_an_empty_room_claim_stays(tmp_path):
    """Fails on HEAD: the room of a set_room_type was no changed target, so a vision R1 (cause room_type, only tool
    set_room_type) was refused 'still there' and could never be fixed."""
    loop, ctx = _loop(tmp_path)
    r1 = dict(finding("R1", "major", "r1", message=R1_TEXT, source="vision"), id="v:R1:r1")
    empty = dict(finding("F1", "critical", "r1", message=EMPTY_TEXT, source="vision"), id="v:F1:r1")
    after = copy.deepcopy(ctx.building)
    after["rooms"][0]["room_type"] = "bathroom"
    args = {"room_id": "r1", "room_type": "bathroom"}
    ctx.findings = [r1]
    verdict = loop.acceptance(ctx, "set_room_type", args, {"changed_ids": ["r1"]}, after)
    assert verdict["accepted"], verdict["reason"]
    assert "r1" in verdict["changed"] and verdict["removed"] == 1
    # both on the room: the R1 is the target (room_type), the empty-room claim is carried, not counted as removed
    ctx.findings = [r1, empty]
    verdict = loop.acceptance(ctx, "set_room_type", args, {"changed_ids": ["r1"]}, after)
    assert verdict["accepted"] and verdict["target"] == ["R1:r1"], verdict["reason"]
    assert "F1:r1" in verdict["carried"] and verdict["removed"] == 1
    assert any(CS.finding_key(f) == ("F1", "r1") for f in verdict["after_findings"])
    # aimed at the empty-room claim: refused with the note that names place_group / relayout_room
    ctx.findings = [empty]
    verdict = loop.acceptance(ctx, "set_room_type", args, {"changed_ids": ["r1"]}, after)
    assert not verdict["accepted"] and verdict["reason"].startswith("finding F1:r1 is still there")
    assert verdict["reason"].endswith(LP.ROOM_TYPE_NOTE)


def test_room_type_kept_names_only_the_furnishing_claims():
    b = {"furniture": [{"id": "f1", "type": "bed_double", "room_id": "r1"}], "rooms": [{"id": "r1"}]}
    empty = finding("F1", "critical", "r1", message=EMPTY_TEXT, source="vision")
    stale = dict(empty, cause="wrong_type")               # a cause given before the empty_room rule
    before = [finding("R1", "major", "r1", message=R1_TEXT, source="vision"), empty, stale,
              finding("R4", "minor", "r1", message="the floor looks like carpet", source="vision"),
              finding("F1", "major", "r1", message=EMPTY_TEXT),          # a code finding: re-measured
              finding("F1", "major", "r2", room="r2", message=EMPTY_TEXT, source="vision")]
    kept = LP.room_type_kept("set_room_type", {"room_id": "r1", "room_type": "bedroom"}, before, b)
    assert [(f["check"], f["target"], f["cause"]) for f in kept] == [("F1", "r1", "empty_room")] * 2
    assert LP.room_type_kept("relayout_room", {"room_id": "r1"}, before, b) == []
    assert LP.render_unchanged("set_room_type", {"room_id": "r1", "room_type": "study"}, b, b) == {}


# --------------------------------------------------------------------------
# 2. metric 7 and the kept targets of an accepted edit
# --------------------------------------------------------------------------

def _event(kind, seq, rnd, **kw) -> dict:
    return dict({"kind": kind, "seq": seq, "round": rnd}, **kw)


def _fridge_events(kept) -> list[dict]:
    """P6b seq 1844: fix_fixture on the fridge 'fr', target F7 (critical) + G8 + G12, G12 kept; round 2 has G12 only."""
    acc = {"target": ["F7:fr", "G8:fr", "G12:fr"]}
    if kept is not None:
        acc["kept"] = kept
    found = [_event("finding", 1, 1, checklist="F7", target="fr", severity="critical"),
             _event("finding", 2, 1, checklist="G8", target="fr", severity="major"),
             _event("finding", 3, 1, checklist="G12", target="fr", severity="major"),
             _event("finding", 5, 2, checklist="G12", target="fr", severity="major")]
    return found + [_event("edit", 4, 1, tool="fix_fixture", checklist="F7", target="fr",
                           evidence={"acceptance": acc})]


def test_an_edit_accepted_with_a_kept_major_counts_as_removing_its_finding():
    """Fails on HEAD: edit_target_keys took every target, so the kept G12 (still in round 2) made the edit count as
    not removing its finding (0 of 1) while the round removed 2."""
    m = AM.findings_removed_metrics(_fridge_events(["G12:fr"]), [1, 2])
    assert (m["edits_removing_finding"], m["edits_with_target"], m["total"]) == (1, 1, 2)
    # a log without the kept field (before the rule) counts as before
    m = AM.findings_removed_metrics(_fridge_events(None), [1, 2])
    assert (m["edits_removing_finding"], m["edits_with_target"]) == (0, 1)
    assert AM.edit_target_keys(_fridge_events(["G12:fr"])[-1]) == [("F7", "fr"), ("G8", "fr")]


def test_a_cut_less_s2_target_is_kept_by_its_cuts():
    """Fails on HEAD (no causes.kept_targets; the acceptance's kept compared the target's own key, so an S2 target
    without its cut was never listed): the kept targets are accept_edit's expanded keys."""
    before = [finding("F7", "critical", "fr"), finding("S2", "major", "fr", wall_id="w1"),
              finding("S2", "major", "fr", other="ch")]
    after = [finding("S2", "major", "fr", wall_id="w1")]
    edit = {"target_finding": [{"check": "F7", "target": "fr"}, {"check": "S2", "target": "fr"}]}
    assert CS.accept_edit(before, after, edit)[0]
    assert CS.kept_targets(before, after, edit) == [("S2", "fr/w1")]
    # metric 7 leaves the cut-less S2 out when a cut of it is kept
    e = {"kind": "edit", "evidence": {"acceptance": {"target": ["F7:fr", "S2:fr"], "kept": ["S2:fr/w1"]}}}
    assert AM.edit_target_keys(e) == [("F7", "fr")]


# --------------------------------------------------------------------------
# 3. fixture_layout_blocked: only drawn pieces hold a fixture
# --------------------------------------------------------------------------

def _kitchen(*extra) -> tuple[dict, dict]:
    """A 4 x 4 m kitchen; a drawn fridge 0.30 m into the swing of door d1 (south wall, x 0.55-1.45); its free spots
    within 0.5 m are x 1.95-2.25, y 0.30-0.95 (25 spots)."""
    fridge = M.fp("fr", "fridge", (1.75, 0.5), (0.6, 0.6), front=90.0)
    return M.building(w=4.0, h=4.0, room_type="kitchen", door_x=1.0, window=None, furniture=[fridge, *extra]), fridge


def _sideboard(source: str) -> dict:
    return M.fp("sb", "sideboard", (2.45, 0.7), (1.2, 0.5), rotation=90.0, front=180.0, source=source)


def test_an_added_piece_over_the_only_spots_does_not_make_a_fixture_the_drawn_layout():
    """Fails on HEAD: the 0.5 m search counted the AI-added sideboard as an obstacle, so the fridge's F7 got
    drawn_layout 'fixture' (no tool, reported as a drawing fact) although moving the sideboard clears it."""
    b, fridge = _kitchen()
    assert E.fixture_problems(b, fridge)["place"]["door"] == "d1" and not CS.fixture_layout_blocked(b, fridge)
    added, fridge = _kitchen(_sideboard("added_by_ai"))
    room = added["rooms"][0]
    assert E._nearest_valid(added, room, fridge, placer.drawn_piece(fridge)) is None    # fix_fixture's own search
    assert not CS.fixture_layout_blocked(added, fridge)
    f7 = CS.mark_drawn_layout([finding("F7", "critical", "fr", room=M.ROOM_ID, door="d1")], added)[0]
    assert not CS._metrics(f7).get(CS.DRAWN_LAYOUT_FLAG) and "fix_fixture" in CS.tools_for_finding(f7)
    assert [f["source"] for f in added["furniture"]] == ["from_documents", "added_by_ai"]      # not changed
    # a drawn sideboard there is the drawing: the fixture stays held
    drawn, fridge = _kitchen(_sideboard("from_documents"))
    assert CS.fixture_layout_blocked(drawn, fridge)
    f7 = CS.mark_drawn_layout([finding("F7", "critical", "fr", room=M.ROOM_ID, door="d1")], drawn)[0]
    assert CS._metrics(f7)[CS.DRAWN_LAYOUT_FLAG] == CS.FIXTURE_LAYOUT and CS.cause_of(f7, drawn) == "drawn_layout"


# --------------------------------------------------------------------------
# 4. the prep job's GPU test of the library attribution
# --------------------------------------------------------------------------

def _gpu_library_test():
    spec = importlib.util.spec_from_file_location("gpu_test_library_p6b_review", ROOT / "tests" / "gpu" /
                                                  "test_library.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_gpu_attribution_test_reads_the_decoded_credits(tmp_path, monkeypatch):
    """Fails on HEAD: ATTRIBUTION.md writes 'Marble & Gold' (copy.plain_text) while the test looked for the raw
    'Marble &amp; Gold', and it asked for '[licence flag: none]', which is never written (Milestone 13: none = no
    flag). Two real entries of the committed catalogue: an ABO table (flag none) and an HSSD shower (non_commercial)."""
    cat = read(ROOT / "wenart" / "furniture" / "catalog_library.json")
    entries = {e["id"]: e for e in cat["entries"] + cat.get("decor", [])}
    picked = [entries["abo_B07DBFQV23"], entries["hssd_762d42fce4ff28d319112e66bde33c3f4329c175"]]
    assert all("&amp;" in e["attribution"] for e in picked)
    lib = tmp_path / "library"
    lib.mkdir()
    (lib / OV.CATALOG_NAME).write_text(json.dumps({"sources": [], "entries": picked, "decor": []}), encoding="utf-8")
    assert CP.library_attribution(lib) is not None
    (lib / OV.REPORT_NAME).write_text("\n".join(f"- {e['attribution']}" for e in picked) + "\n", encoding="utf-8")
    text = (lib / CP.ATTRIBUTION).read_text(encoding="utf-8")
    assert "Marble & Gold" in text and "Marble &amp; Gold" not in text
    mod = _gpu_library_test()
    monkeypatch.setattr(mod, "LIBRARY", lib)
    mod.test_attribution_is_complete(OV.load_config())


# --------------------------------------------------------------------------
# 5. the planner prompt on complete_group's anchor
# --------------------------------------------------------------------------

def test_the_planner_prompt_lets_complete_group_take_a_code_typed_drawn_anchor():
    """Fails on HEAD: rule 3 said 'complete_group needs a verified anchor' only (the tool description and edit_ops
    take a drawn anchor typed by code from the drawing since the fix round after P6b)."""
    rule3 = P.PLANNER_SYSTEM_M12.split("\n3. ", 1)[1].split("\n4. ", 1)[0]
    assert "complete_group needs a verified anchor or a drawn one typed by code from the drawing" in rule3


# --------------------------------------------------------------------------
# 6. the solver's coffee table: the next sizes and gaps when the check fails
# --------------------------------------------------------------------------

def _seating(island_x: float, island_rot: float) -> tuple[dict, dict]:
    """A 6 x 5 m living room: a drawn sofa facing +x 0.55 m off the west wall, a drawn kitchen island east of it, the
    door on the south wall at x 2.0; the seating group misses its TV unit and coffee table."""
    sofa = M.fp("s1", "sofa", (1.0, 2.5), (2.1, 0.9), rotation=90.0, front=0.0)
    island = M.fp("i1", "kitchen_island", (island_x, 2.5), (1.6, 0.6), rotation=island_rot, front=None)
    b = M.building(w=6.0, h=5.0, room_type="living", door_x=2.0, window=None, furniture=[sofa, island])
    group = next(g for g in GR.group_members(b, M.ROOM_ID) if g["group"] == "seating")
    return b, group


def _solve(b: dict, group: dict) -> list[dict]:
    room = b["rooms"][0]
    return SV.solve_room(b, M.ROOM_ID, E._program(b, room, [E._group_entry(room, group)]), k=3,
                         fixed_ids=E._ai_floor_ids(b, M.ROOM_ID))


def _tables(b: dict) -> list[dict]:
    return [f for f in b["furniture"] if f["type"] == "table_coffee"]


def test_complete_group_takes_a_smaller_coffee_table_when_the_first_fit_fails_the_check(monkeypatch):
    """Fails on HEAD: the first fit (1.2 x 0.7 at 0.40 m) cut the walkway to the island, the group was left out of
    every candidate and complete_group was refused 'no place passes the checks'; options 1-6 fail too, option 7
    (0.8 x 0.5 at 0.35 m) passes, clears the sofa's F3 and G2 and adds no finding."""
    b, group = _seating(3.5, 90.0)
    monkeypatch.setattr(SV, "_passes", lambda c: True)          # the first search only (HEAD's answer)
    first = _solve(b, group)
    assert [c["pieces"] for c in first] == [[]] and "front_from" not in first[0]
    monkeypatch.undo()
    cands = _solve(b, group)
    # 25 Oct 2026: a drawn group may take accessory options too: every candidate starts its front partners at 7
    assert {c["front_from"] for c in cands} == {7} and not cands[0]["hard_failures"]
    res = E.apply_edit(b, {"op": "complete_group", "group_id": group["group_id"], "reason": "test"})
    assert res["accepted"], res["failed_checks"]
    (table,) = _tables(res["building"])
    assert table["footprint"]["size"] == [0.8, 0.5] and table["footprint"]["center"] == [2.05, 2.5]
    sofa = next(f for f in b["furniture"] if f["id"] == "s1")
    assert round(placer.drawn_piece(sofa).polygon().distance(placer.drawn_piece(table).polygon()), 3) == 0.35
    room = b["rooms"][0]
    before = {(v["check"], v["target"]) for v in PL.room_violations(b, room)}
    after = {(v["check"], v["target"]) for v in PL.room_violations(res["building"], room)}
    assert before - after == {("F3", "s1"), ("G2", "s1")} and after <= before


def test_a_coffee_table_that_passes_keeps_its_first_fit():
    """The guard: an island 0.1 m further west, turned along x: the first fit (1.2 x 0.7) passes and nothing is searched
    again; with the island along y one search more finds 1.0 x 0.6 at 0.35 m (option 4)."""
    b, group = _seating(3.4, 0.0)
    cands = _solve(b, group)
    assert all("front_from" not in c for c in cands)
    assert [[p["footprint"]["size"] for p in c["pieces"] if p["type"] == "table_coffee"] for c in cands] == \
        [[[1.2, 0.7]]] * 3
    b, group = _seating(3.6, 90.0)
    cands = _solve(b, group)
    assert {c["front_from"] for c in cands} == {4}
    assert [p["footprint"]["size"] for p in cands[0]["pieces"] if p["type"] == "table_coffee"] == [[1.0, 0.6]]


@needs_p4a
def test_p4a_real02_salon_2_gets_the_coffee_table_that_passes():
    """P4a's real02 (the data P6c replays): complete_group of the drawn sofa f_L-1b_041 took 1.2 x 0.7 at 0.40 m,
    which cut the island f_L-1b_005's walkway (G11), and was refused; now it takes 0.8 x 0.5 (option 7, 0.35 m from
    the model's front: 0.31 m from the drawn box) and its F3 and G2 go with no new finding. salon's f_L-1b_042 stays
    refused (the unbuilt cluster f_L-1b_002 in front of it: no table fits at all)."""
    b = read(P4A)
    res = E.apply_edit(b, {"op": "complete_group", "group_id": "r_L-1b_salon_2.seating", "reason": "t"})
    assert res["accepted"], res["failed_checks"]
    (table,) = [f for f in _tables(res["building"]) if f["id"] not in {x["id"] for x in b["furniture"]}]
    assert table["footprint"]["size"] == [0.8, 0.5]
    sofa = next(f for f in b["furniture"] if f["id"] == "f_L-1b_041")
    room = next(r for r in b["rooms"] if r["id"] == sofa["room_id"])
    before = {(v["check"], v["target"]) for v in PL.room_violations(b, room)}
    after = {(v["check"], v["target"]) for v in PL.room_violations(res["building"], room)}
    assert before - after == {("F3", "f_L-1b_041"), ("G2", "f_L-1b_041")} and after <= before
    other = E.apply_edit(b, {"op": "complete_group", "group_id": "r_L-1b_salon.seating", "reason": "t"})
    assert not other["accepted"] and other["failed_checks"][0].startswith("no_place:")
