"""Fix round after P6b (23 Oct 2026), part J1: the agent, furniture and report side of the integration.

Checked, each against BASE 620997b (the tests fail there: a missing name, the old verdict or a mutation named in the
docstring):

1. complete_group completes a drawn anchor the reading typed by code (``edit_ops.unsure_group_anchor``): the review of
   the fix round after P6a gave the F3 of the drawn basement sofas f_L-1b_041 / 042 the cause missing_member, while
   complete_group refused their groups "unverified (retype_piece first)" and the acceptance refuses a same-type confirm:
   a deadlock. The validator's sofa clearance counts its coffee table as the score's F6 does
   (``edit_ops.seat_front_free``), a group edit's new F4 is counted by finding (``finding_identity``) and an F4 of
   another group's anchor is reported, not held against the edit (``other_group_front``). The brief offers the tool and
   names why a group cannot be completed (``brief.completion_lock``, the dry run's refusal);
2. the asks of the build tracks for these files: the fit report's credits decode HTML entities (D_data); S2 sees a
   piece that passes right through a wall (A_agent); an F7 of drawn fixed equipment at a doorless opening's edge that
   leaves the passage clear, and an S2 / F9 wall or outline cut of drawn fixed equipment with no valid spot, are the
   drawn layout (F_reading); the final report marks blocked views (G_render) and lists the replayed cameras the build
   moved or re-pitched (C_cam).

The P6a / P4a / P6b run folders (``runs/...``) are not in git; the tests that read them skip without them.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import _m11_room as M
from test_decor_rest import boxes_mesh
from wenart.agent import brief as BR
from wenart.agent import causes as CS
from wenart.blender import scene_checks as SC
from wenart.furniture import edit_ops as E
from wenart.furniture import fit as F
from wenart.furniture import placer
from wenart.furniture import plausibility as PL
from wenart.report import agent as AG
from wenart.report import final as FR

ROOT = Path(__file__).resolve().parents[1]
P6A = ROOT / "runs" / "20261022-135644-m13_p6" / "results" / "furniture" / "real04" / "building_final.json"
P4A = ROOT / "runs" / "20261017-072801-full" / "results" / "furniture" / "real02" / "building_final.json"
P6B = ROOT / "runs" / "20261022-235127-fetch_results" / "results"
P6B_BUILDING = P6B / "furniture" / "real03" / "building_final.json"
P6B_LOG = P6B / "agent" / "real03" / "log.json"
needs_p6a = pytest.mark.skipif(not P6A.is_file(), reason="the P6a run folder runs/20261022-135644-m13_p6 is not here")
needs_p4a = pytest.mark.skipif(not P4A.is_file(), reason="the P4a run folder runs/20261017-072801-full is not here")
needs_p6b = pytest.mark.skipif(not P6B_BUILDING.is_file(),
                               reason="the P6b run folder runs/20261022-235127-fetch_results is not here")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def piece_of(b: dict, pid: str) -> dict:
    return next(f for f in b["furniture"] if f["id"] == pid)


def code_finding(v: dict, room_id: str) -> dict:
    """A score violation as the loop's code finding (``critic_code.finding``'s fields)."""
    return {"check": v["check"], "severity": v["severity"], "target": v["target"], "room_id": room_id,
            "message": v["message"], "source": "code", "evidence": {"metrics": dict(v.get("metrics") or {})}}


def checks_on(b: dict, room_id: str, target: str) -> set:
    room = next(r for r in b["rooms"] if r["id"] == room_id)
    return {v["check"] for v in PL.room_violations(b, room) if v["target"] == target}


def front_gap(sofa: dict, table: dict) -> float:
    """The gap from the sofa's drawn front to the coffee table (the table in its front zone)."""
    s, t = placer.drawn_piece(sofa), placer.drawn_piece(table)
    return float(s.polygon().distance(t.polygon()))


# --------------------------------------------------------------------------
# 1. complete_group and a drawn anchor typed by code
# --------------------------------------------------------------------------

SEATING = f"{M.ROOM_ID}.seating"


def living(status: str = "unverified", method: str = "group_member") -> dict:
    """A 4.6 x 4.0 m living room with a drawn sofa 1.15 m off the west wall, facing +x (F3: its back is not on a wall;
    no coffee table or TV unit: the missing members)."""
    sofa = M.fp("s1", "sofa", (1.6, 2.0), (2.0, 0.9), rotation=90.0, front=0.0, status=status, type_method=method)
    return M.building(w=4.6, h=4.0, room_type="living", door_x=0.6, window=None, furniture=[sofa])


def test_complete_group_completes_a_drawn_sofa_the_reading_typed_by_code():
    """Fails on BASE: "the anchor s1 is unverified (retype_piece first)" (and, with that lock gone, "s1:
    clearance_ok": the coffee table at the designer gap stood in the sofa's 0.6 m front zone). The group gets its TV
    unit and coffee table, the F3 and the G2 go, nothing fails the placer checks; a sofa the reading could not agree on
    (type_method inferred) keeps the lock, a verified one is completed as before."""
    b = living()
    assert {"F3", "G2"} <= checks_on(b, M.ROOM_ID, "s1")
    res = E.apply_edit(b, {"op": "complete_group", "group_id": SEATING, "reason": "the seating group misses its "
                                                                                  "coffee table"})
    assert res["accepted"], res["failed_checks"]
    new = res["building"]
    added = {piece_of(new, pid)["type"]: piece_of(new, pid) for pid in res["changed_ids"]}
    assert set(added) == {"tv_unit", "table_coffee"}
    assert all(p["source"] == "added_by_ai" and p["group"]["anchor_id"] == "s1" for p in added.values())
    assert not {"F3", "G2"} & checks_on(new, M.ROOM_ID, "s1")
    assert 0.30 - 1e-6 <= front_gap(piece_of(new, "s1"), added["table_coffee"]) <= 0.45 + 1e-6   # coffee_gap
    assert E._new_failures(E.room_checks(b, M.ROOM_ID), E.room_checks(new, M.ROOM_ID)) == []
    assert piece_of(new, "s1")["status"] == "unverified"        # the anchor itself is not touched
    unsure = E.apply_edit(living(method="inferred"), {"op": "complete_group", "group_id": SEATING, "reason": "t"})
    assert not unsure["accepted"] and unsure["failed_checks"][0].startswith("unverified:")
    assert "not typed by code" in unsure["failed_checks"][0]
    assert E.apply_edit(living(status="verified"), {"op": "complete_group", "group_id": SEATING,
                                                    "reason": "t"})["accepted"]


def test_the_lock_follows_the_program_s_unsure_anchor():
    """``unsure_group_anchor`` is ``program.unsure_anchor``: a vector-drawn piece typed by code (twin, level, block,
    group_member) is no lock; an inferred one, a type proposal of the completion or one without vector evidence is."""
    for method in ("twin", "level", "block", "group_member"):
        assert not E.unsure_group_anchor(piece_of(living(method=method), "s1"))
    assert E.unsure_group_anchor(piece_of(living(method="inferred"), "s1"))
    proposal = dict(piece_of(living(), "s1"), type_proposal=True)
    assert E.unsure_group_anchor(proposal)
    raster = dict(piece_of(living(), "s1"), evidence=[{"file": "plan.pdf", "method": "ai", "confidence": 0.8}])
    assert E.unsure_group_anchor(raster)
    assert not E.unsure_group_anchor(piece_of(living(status="verified", method="inferred"), "s1"))
    assert not E.unsure_group_anchor(None)


def test_the_brief_offers_complete_group_for_a_code_typed_sofa_and_names_why_not():
    """Fails on BASE (the brief locked every unverified anchor: "misses nothing, or its anchor is unverified"): the F3
    of the code-typed sofa is fixable with complete_group; for an inferred sofa the reason names the anchor; for a group
    whose dry run fails the reason is the refusal."""
    def f3(b):
        # the F3 as ``causes.mark_drawn_layout`` marks a sofa no wall place within the drawn lock clears (P6a's)
        f = {"check": "F3", "severity": "major", "target": "s1", "room_id": M.ROOM_ID, "message": "sofa: its back is "
             "not on a wall (1.15 m off)", "source": "code",
             "evidence": {"metrics": {CS.DRAWN_LAYOUT_FLAG: CS.MISSING_FRONT}}}
        assert CS.cause_of(f, b) == "missing_member"
        return [dict(f, id="c1", cause="missing_member")]
    b = living()
    brief = BR.room_brief(b, M.ROOM_ID, findings=f3(b))
    (fixable,) = brief["findings"]["fixable"]
    assert fixable["tools"][0] == "complete_group", brief["findings"]
    b = living(method="inferred")
    brief = BR.room_brief(b, M.ROOM_ID, findings=f3(b))
    assert "complete_group" not in [t for x in brief["findings"]["fixable"] for t in x["tools"]]
    group = {"group_id": SEATING, "missing": ["tv_unit", "table_coffee"]}
    why = BR.completion_lock(group, piece_of(b, "s1"))
    assert "its anchor s1 is unverified and not typed by code" in why and "retype_piece first" in why
    assert BR.completion_lock(group, piece_of(living(), "s1")) is None
    # a refused dry run (the real tracks' default, ``complete_dry_run_result``): not offered, and its refusal is the
    # reason a finding with no other tool gets
    refused = {"accepted": False, "message": "complete_group rejected: no place passes the checks (G11 ...)"}
    b = living()
    brief = BR.room_brief(b, M.ROOM_ID, findings=f3(b), complete_fn=lambda bb, gid: refused)
    assert "complete_group" not in [t for x in brief["findings"]["fixable"] for t in x["tools"]]
    _fix, not_yours = BR.classify(f3(b), b, M.ROOM_ID, {}, {"s1": SEATING},
                                  {"complete_group": False, "place_group": False, "relayout_room": False},
                                  completable=frozenset(), complete_why={SEATING: f"{SEATING}: its dry run is refused "
                                                                                  f"({refused['message']})"})
    assert not_yours[0]["why"].startswith(f"locked: complete_group: {SEATING}: its dry run is refused (complete_group "
                                          f"rejected: no place passes the checks")
    res = BR.complete_dry_run_result(living(), SEATING)
    assert res["accepted"] and BR.complete_dry_run(living(), SEATING)
    assert BR.completion_lock({"group_id": "g", "missing": []}, None) == "g misses nothing"


def _room_with(*pieces) -> dict:
    return M.building(w=5.0, h=4.0, room_type="living", door_x=4.4, window=None, furniture=list(pieces))


SOFA = M.fp("s1", "sofa", (2.5, 0.47), (2.0, 0.9), rotation=180.0, front=90.0)          # back on the south wall


def test_a_sofa_front_zone_holds_its_coffee_table_but_not_an_armchair():
    """Fails on BASE (``room_checks`` gave the placer's verdict: a coffee table 0.35 m in front of a sofa failed
    ``clearance_ok``; P6a seq 6308 / 6309 / 6312 / 6600 / 6645 / 6649 were refused "<sofa>: clearance_ok"). The
    score's F6 exemption (``plausibility.EXTRA_EXEMPT``) is the rule: a coffee table or an ottoman may stand there; an
    armchair, a chair or a zone out of the room still fail; a bed keeps the placer's verdict."""
    table = M.fp("c1", "table_coffee", (2.5, 0.92 + 0.35 + 0.30), (1.0, 0.6), rotation=180.0, front=90.0)
    assert "clearance_ok" not in E.room_checks(_room_with(SOFA, table), M.ROOM_ID)["s1"]
    ottoman = M.fp("o1", "ottoman", (2.5, 1.4), (0.6, 0.6))
    assert "clearance_ok" not in E.room_checks(_room_with(SOFA, ottoman), M.ROOM_ID)["s1"]
    arm = M.fp("a1", "armchair", (2.5, 1.5), (0.8, 0.8), rotation=0.0, front=270.0)
    assert "clearance_ok" in E.room_checks(_room_with(SOFA, arm), M.ROOM_ID)["s1"]
    assert "clearance_ok" in E.room_checks(_room_with(SOFA, table, arm), M.ROOM_ID)["s1"]
    out = M.fp("s2", "sofa", (2.5, 0.47), (2.0, 0.9), rotation=0.0, front=270.0)            # faces the wall
    assert "clearance_ok" in E.room_checks(_room_with(out), M.ROOM_ID)["s2"]
    bed = M.fp("b1", "bed_double", (2.5, 1.02), (1.6, 2.0), rotation=180.0, front=90.0)
    foot = M.fp("c2", "table_coffee", (2.5, 2.4), (1.0, 0.6), rotation=180.0, front=90.0)
    assert "clearance_ok" in E.room_checks(_room_with(bed, foot), M.ROOM_ID)["b1"]
    # the score agrees: no F6 for the table, an F6 for the armchair
    room = _room_with(SOFA, table)["rooms"][0]
    assert "F6" not in {v["check"] for v in PL.room_violations(_room_with(SOFA, table), room)}
    assert "F6" in {v["check"] for v in PL.room_violations(_room_with(SOFA, arm), room)}


def test_a_group_edit_s_findings_are_counted_by_finding():
    """Fails on BASE (no ``finding_identity``: the F4 of P6a's chair f_L-1b_053 "does not face its group (f_L-1b_051,
    f_L-1b_054)" read as new when the new coffee table joined its list). Only the F4 list is left out."""
    a = {"check": "F4", "target": "c", "message": "chair does not face its group (f_1, f_2)"}
    b = {"check": "F4", "target": "c", "message": "chair does not face its group (f_1, f_2, f_9)"}
    assert E.finding_identity(a) == E.finding_identity(b) == ("F4", "c", "chair does not face its group")
    behind = {"check": "F4", "target": "c", "message": "armchair stands behind the back of f_1, looking at it"}
    assert E.finding_identity(behind)[2] == behind["message"]
    g6 = {"check": "G6", "target": "c", "message": "chair c: 0.09 m from the table edge (f_1)"}
    assert E.finding_identity(g6)[2] == g6["message"]
    assert E.finding_identity(dict(a, target="d")) != E.finding_identity(a)


def _two_sofas(tag_table: str = "s1", changed=("t1",)):
    """Two sofas, each the anchor of its seating group, and a new coffee table of ``tag_table``'s group."""
    s1 = M.fp("s1", "sofa", (2.0, 0.47), (2.0, 0.9), rotation=180.0, front=90.0)
    s2 = M.fp("s2", "sofa", (4.6, 2.5), (2.0, 0.9), rotation=90.0, front=0.0)
    table = M.fp("t1", "table_coffee", (2.0, 1.57), (1.0, 0.6), rotation=180.0, front=90.0, source="added_by_ai",
                 group={"group_id": f"{M.ROOM_ID}.seating" + ("" if tag_table == "s1" else ".2"),
                        "group": "seating", "role": "partner", "anchor_id": tag_table})
    b = M.building(w=6.0, h=5.0, room_type="living", door_x=5.5, window=None, furniture=[s1, s2, table])
    v = {"check": "F4", "severity": "major", "target": "s2", "message": "sofa does not face its group (t1)",
         "metrics": {"targets": ["t1"]}}
    return b, v, list(changed)


def test_an_f4_of_another_group_s_anchor_is_reported_not_held_against_the_edit():
    """Fails on BASE (no ``other_group_front``; P6a: the coffee table f_L-1b_087 completing f_L-1b_041's group gave the
    second drawn sofa f_L-1b_045 a new F4 within the score's 4.5 m sofa reach and the edit was refused). Only an F4 of a
    piece that anchors its own group, naming only this edit's new pieces of a group with another anchor, is noted."""
    b, v, changed = _two_sofas()
    note = E.other_group_front(b, M.ROOM_ID, v, changed)
    assert note is not None and note.startswith("F4 s2 (major, kept for the next round): it anchors ")
    assert "t1 belongs to r_L0_oda.seating" in note
    # the new piece is of s2's own group, it is not new, the F4 names an older piece, or another check: held
    own_b, own_v, _ = _two_sofas(tag_table="s2")
    assert E.other_group_front(own_b, M.ROOM_ID, own_v, changed) is None
    assert E.other_group_front(b, M.ROOM_ID, v, []) is None
    assert E.other_group_front(b, M.ROOM_ID, dict(v, metrics={"targets": ["t1", "s1"]}), changed) is None
    assert E.other_group_front(b, M.ROOM_ID, dict(v, check="F6"), changed) is None
    assert E.other_group_front(b, M.ROOM_ID, dict(v, severity="critical"), changed) is None
    chair = dict(v, target="t9", message="chair does not face its group (t1)")
    assert E.other_group_front(b, M.ROOM_ID, chair, changed) is None       # t9 anchors nothing


@needs_p6a
def test_p6a_complete_group_adds_the_coffee_table_of_the_salon_sofas():
    """P6a's real04 basement salons (the deadlock of the review of the fix round after P6a): complete_group on the
    drawn sofas f_L-1b_041 (group_member) and f_L-1b_042 (twin) adds a coffee table at the designer gap in front of
    each, their F3 goes, nothing fails the placer checks; the coffee table of f_L-1b_041 gives the second drawn sofa
    f_L-1b_045 (its own seating group) an F4 that is noted for the next round. Fails on BASE ("unverified")."""
    b = read(P6A)
    for gid, sid, note in (("r_L-1b_salon_2.seating", "f_L-1b_041", "F4 f_L-1b_045"),
                           ("r_L-1b_salon.seating", "f_L-1b_042", None)):
        sofa = piece_of(b, sid)
        assert sofa["status"] == "unverified" and not E.unsure_group_anchor(sofa)
        res = E.apply_edit(b, {"op": "complete_group", "group_id": gid, "reason": "the seating group misses its "
                                                                                  "coffee table (F3)"})
        assert res["accepted"], res["failed_checks"]
        new = res["building"]
        tables = [piece_of(new, pid) for pid in res["changed_ids"] if piece_of(new, pid)["type"] == "table_coffee"]
        assert len(tables) == 1 and tables[0]["group"]["anchor_id"] == sid
        assert 0.30 - 1e-6 <= front_gap(piece_of(new, sid), tables[0]) <= 0.45 + 1e-6
        assert "F3" in checks_on(b, sofa["room_id"], sid) and "F3" not in checks_on(new, sofa["room_id"], sid)
        assert E._new_failures(E.room_checks(b, sofa["room_id"]), E.room_checks(new, sofa["room_id"])) == []
        assert (note in res["message"]) if note else ("noted" not in res["message"])
        # the room brief offers the tool for the F3 (it said "unverified: retype_piece first" before)
        f3 = CS.mark_drawn_layout([{"check": "F3", "severity": "major", "target": sid, "room_id": sofa["room_id"],
                                    "message": "wrong", "source": "code", "evidence": {"metrics": {}}}], b)[0]
        brief = BR.room_brief(b, sofa["room_id"], findings=[dict(f3, id="c1", cause=CS.cause_of(f3, b))])
        assert [x["tools"] for x in brief["findings"]["fixable"]] == [["complete_group"]]


@needs_p4a
def test_p4a_real02_salon_sofas_are_no_longer_locked_and_the_brief_names_the_solver_s_refusal():
    """P4a's real02 twins (the data P6c replays): the lock is gone, so complete_group reaches the solver; on this
    building the solver refuses both groups (salon_2: its 1.2 x 0.7 table at the 0.40 m gap cuts the island's walkway,
    G11; salon: the unbuilt 5.14 x 2.37 m cluster f_L-1b_002 is in front of f_L-1b_042), and the brief reports the F3
    with that refusal instead of the lock. A 0.8 x 0.5 table at the 0.30 m minimum gap would clear the F3 and the G2 of
    f_L-1b_041 with no new finding (the solver's size choice: an ask to the solver's owner)."""
    b = read(P4A)
    for gid, sid in (("r_L-1b_salon_2.seating", "f_L-1b_041"), ("r_L-1b_salon.seating", "f_L-1b_042")):
        assert not E.unsure_group_anchor(piece_of(b, sid))
        res = E.apply_edit(b, {"op": "complete_group", "group_id": gid, "reason": "t"})
        assert not res["accepted"] and res["failed_checks"][0].startswith("no_place:"), res["failed_checks"]
        f3 = CS.mark_drawn_layout([{"check": "F3", "severity": "major", "target": sid,
                                    "room_id": piece_of(b, sid)["room_id"], "message": "wrong", "source": "code",
                                    "evidence": {"metrics": {}}}], b)[0]
        assert CS.cause_of(f3, b) == "missing_member"
        brief = BR.room_brief(b, piece_of(b, sid)["room_id"], findings=[dict(f3, id="c1", cause=CS.cause_of(f3, b))])
        why = brief["findings"]["not_yours"][0]["why"]
        assert "its dry run is refused" in why and "no place passes the checks" in why and "unverified" not in why
    sofa = piece_of(b, "f_L-1b_041")
    cx, cy = sofa["footprint"]["center"]
    small = {"id": "f_x", "type": "table_coffee", "room_id": sofa["room_id"], "level_id": sofa["level_id"],
             "source": "added_by_ai", "status": "verified", "front_deg": 0.0, "height": 0.4,
             "footprint": {"center": [cx + 0.45 + 0.30 + 0.25, cy], "size": [0.8, 0.5], "rotation_deg": 90.0}}
    room = next(r for r in b["rooms"] if r["id"] == sofa["room_id"])
    before = {(v["check"], v["target"], v["message"]) for v in PL.room_violations(b, room)}
    after = {(v["check"], v["target"], v["message"]) for v in PL.room_violations(dict(b, furniture=b["furniture"]
                                                                                       + [small]), room)}
    assert after < before and {k[:2] for k in before - after} == {("F3", "f_L-1b_041"), ("G2", "f_L-1b_041")}


# --------------------------------------------------------------------------
# 2. the asks of the build tracks
# --------------------------------------------------------------------------

def test_the_fit_report_credits_name_the_products_as_they_are_called():
    """D_data's ask. Fails on BASE: P6b's building_fitted_report.md and building_final_report.md listed "Knobs &amp;
    Faucet", "Vanity Unit &amp; Basin" and "Cooke &amp; Lewis"; a credit without an entity is unchanged."""
    asset = {"method": "library", "library": "hssd", "asset_id": "hssd_x", "licence": "CC-BY-NC-4.0",
             "attribution": "\"Cooke &amp; Lewis Deluvio &#8211; Tray\" from HSSD", "fit_scale": [1, 1, 1],
             "bbox_m": [0.8, 0.8, 2.0], "aspect_error": 0.01}
    plain = dict(asset, asset_id="hssd_y", attribution="Plain & simple; 5 &x")
    b = M.building(furniture=[M.fp("f1", "shower", (1.0, 1.0), (0.8, 0.8), asset=asset),
                              M.fp("f2", "shower", (3.0, 1.0), (0.8, 0.8), asset=plain)])
    text = F.fit_report(b)
    assert "- hssd_x: \"Cooke & Lewis Deluvio – Tray\" from HSSD" in text and "&amp;" not in text
    assert "- hssd_y: Plain & simple; 5 &x" in text
    assert F.credit_text({}) == "(no attribution recorded)"


@needs_p6b
def test_the_p6b_final_report_credits_are_decoded():
    text = F.fit_report(read(P6B_BUILDING))
    assert "&amp;" not in text and "Knobs & Faucet" in text and "Vanity Unit & Basin" in text


def _wall_building(*pieces) -> dict:
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "rooms": [{"id": "r1", "level_id": "L0"}],
            "walls": [{"id": "w1", "level_id": "L0", "start": [0.0, 0.0], "end": [8.0, 0.0], "thickness": 0.2,
                       "height": 2.7}],
            "furniture": list(pieces), "decor": []}


def _box(pid, ftype, center, depth=0.6, width=1.0, height=2.0):
    p = {"id": pid, "type": ftype, "level_id": "L0", "room_id": "r1", "status": "verified",
         "source": "from_documents", "front_deg": 90.0,
         "footprint": {"center": list(center), "size": [width, depth], "rotation_deg": 180.0},
         "asset": {"method": "library", "asset_id": "abo_x", "licence": "CC-BY-4.0", "library": "abo"}}
    v, f = boxes_mesh([(-width / 2, -depth / 2, 0.0, width / 2, depth / 2, height)], center=center)
    return p, {"verts": v, "faces": f}


def test_s2_sees_a_piece_that_passes_right_through_a_wall():
    """A_agent's ask (verify:agent:0). Fails on BASE: a box from 0.03 m beyond the wall's far face into the room has
    no vertex inside the wall box, so ``depth_in_wall`` gave 0 and S2 said nothing (P6b's wardrobe f_L0_098). Now the
    depth is the wall's thickness with ``through``; a cut from one side keeps its vertex depth and message; a box
    beside the wall's end or above a low wall is not through it."""
    through, m1 = _box("t1", "wardrobe", (3.0, 0.17))                 # y -0.13 .. 0.47 across the wall's -0.1 .. 0.1
    cut, m2 = _box("t2", "wardrobe", (5.5, 0.35))                     # y 0.05 .. 0.65: 0.05 m into the wall
    beyond, m3 = _box("t3", "wardrobe", (8.7, 0.17))                  # past the wall's end (x 8.2 .. 9.2)
    rep = SC.measure_pure({"t1": m1, "t2": m2, "t3": m3}, _wall_building(through, cut, beyond))
    s2 = {v["target"]: v for v in rep["violations"] if v["check"] == "S2"}
    assert set(s2) == {"t1", "t2"}
    assert s2["t1"]["metrics"]["depth_m"] == pytest.approx(0.2) and s2["t1"]["metrics"]["through"] is True
    assert "passes through wall w1" in s2["t1"]["message"] and rep["measured"]["t1"]["wall_through"] == "w1"
    assert s2["t2"]["message"] == "wardrobe t2 cuts wall w1 by 0.050 m (allowed 0.010 m for a default piece)"
    assert "through" not in s2["t2"]["metrics"]
    low = _wall_building(through)
    low["walls"][0]["height"] = 0.9
    tall_over, m4 = _box("t1", "wardrobe", (3.0, 0.17))
    m4["verts"] = [(x, y, z + 1.0) for x, y, z in m4["verts"]]       # standing above a 0.9 m parapet
    assert SC.through_wall(m4["verts"], m4["faces"], SC.wall_boxes(low, "L0")[0]) == 0.0
    assert SC.through_wall(m1["verts"], m1["faces"], SC.wall_boxes(low, "L0")[0]) == pytest.approx(0.2)


@needs_p6b
def test_s2_sees_the_p6b_wardrobe_through_the_front_wall():
    """P6b seq 2588 moved the drawn wardrobe f_L0_098 0.28 m through w_L0_001 (0.15 m thick): its box (as built at its
    footprint) passes through the wall; at its drawn place it does not."""
    b = read(P6B_BUILDING)
    wardrobe = piece_of(b, "f_L0_098")
    fp = wardrobe["footprint"]
    v, f = boxes_mesh([(-0.55, -0.30, 0.0, 0.55, 0.30, 2.0)], center=tuple(fp["center"]), rot=fp["rotation_deg"])
    rep = SC.measure_pure({"f_L0_098": {"verts": v, "faces": f}}, dict(b, furniture=[wardrobe], decor=[]))
    (s2,) = [x for x in rep["violations"] if x["check"] == "S2"]
    assert s2["metrics"]["wall_id"] == "w_L0_001" and s2["metrics"]["through"] is True
    drawn = dict(wardrobe, footprint=wardrobe["drawn_footprint"])
    dfp = drawn["footprint"]
    v, f = boxes_mesh([(-0.55, -0.30, 0.0, 0.55, 0.30, 2.0)], center=tuple(dfp["center"]), rot=dfp["rotation_deg"])
    rep = SC.measure_pure({"f_L0_098": {"verts": v, "faces": f}}, dict(b, furniture=[drawn], decor=[]))
    assert [x for x in rep["violations"] if x["check"] == "S2"] == []


def _kitchen(kind: str = "opening", into: float = 0.12) -> dict:
    """A 4 x 3 m kitchen with a 1.05 m opening (or door) in the south wall at x 2.0 and a drawn fridge against the
    wall reaching ``into`` metres past its left jamb (P6b's real03 passages: 0.12 m, 0.93 m clear)."""
    x1 = 2.0 - 1.05 / 2 + into
    fridge = M.fp("fr", "fridge", (x1 - 0.3, 0.325), (0.6, 0.65), rotation=180.0, front=90.0)
    b = M.building(w=4.0, h=3.0, room_type="kitchen", door_x=3.4, window=None, furniture=[fridge])
    b["openings"].append({"id": "o1", "type": kind, "level_id": "L0", "wall_id": "w_s", "center": [2.0, -0.05],
                          "width": 1.05, "status": "verified", "evidence": []})
    return b


def _f7(b: dict) -> list[dict]:
    room = b["rooms"][0]
    return [code_finding(v, room["id"]) for v in PL.room_violations(b, room) if v["check"] == "F7"]


def test_an_f7_at_a_doorless_opening_s_edge_that_leaves_the_passage_clear_is_the_drawn_layout():
    """F_reading's ask (verify:library:2 better_fix (c)). Fails on BASE (no ``passage_clear``: the critical F7 kept
    fix_fixture; P6b spent 30 refused calls on the fridges f_L0_200 / 202 / 206): reported with the clear width; a door
    with a leaf, or a passage left under the 0.80 m main walkway, keeps its tools."""
    b = _kitchen()
    (f,) = CS.mark_drawn_layout(_f7(b), b)
    m = CS._metrics(f)
    assert m[CS.DRAWN_LAYOUT_FLAG] == CS.PASSAGE_CLEAR and m["passage_clear_m"] == pytest.approx(0.93, abs=0.005)
    assert m["passage_width_m"] == pytest.approx(1.05) and m["passage_need_m"] == pytest.approx(0.80)
    assert CS.cause_of(f, b) == "drawn_layout" and CS.tools_for_finding(dict(f, cause="drawn_layout")) == []
    assert "leaves 0.93 m of the 1.05 m passage clear" in CS.no_tool_reason(f)
    assert "leaves at least the main walkway" in CS.no_tool_reason(
        {"check": "F7", "evidence": {"metrics": {CS.DRAWN_LAYOUT_FLAG: CS.PASSAGE_CLEAR}}})     # a dry re-check's copy
    for b in (_kitchen(kind="door"), _kitchen(into=0.30)):
        (f,) = CS.mark_drawn_layout(_f7(b), b)
        assert CS._metrics(f).get(CS.DRAWN_LAYOUT_FLAG) is None and CS.tools_for_finding(f), f


@needs_p6b
def test_p6b_fridge_f7s_and_the_cuts_of_drawn_fixtures_with_no_spot_are_reported():
    """F_reading's asks on P6b's final building: the F7 of the fridges f_L0_200 / 202 / 206 (0.93 m of the 1.05 m
    passages clear) and the F9 outline cuts of drawn fixed equipment fix_fixture finds no spot for (the counter
    f_L0_010, the washers f_L0_074-077) are the drawn layout; an S2 wall cut of such a piece too; an S2 with another
    piece keeps its tools. Fails on BASE (F7: blocked_opening; F9 / S2: collision)."""
    b = read(P6B_BUILDING)
    found = []
    for r in b["rooms"]:
        found += [code_finding(v, r["id"]) for v in PL.room_violations(b, r) if v["check"] in ("F7", "F9")]
    CS.mark_drawn_layout(found, b)
    by = {(f["check"], f["target"]): f for f in found}
    for pid in ("f_L0_200", "f_L0_202", "f_L0_206"):
        f = by[("F7", pid)]
        assert CS._metrics(f)[CS.DRAWN_LAYOUT_FLAG] == CS.PASSAGE_CLEAR and CS.cause_of(f, b) == "drawn_layout"
        assert CS._metrics(f)["passage_clear_m"] == pytest.approx(0.93, abs=0.01)
    for pid in ("f_L0_010", "f_L0_074", "f_L0_075", "f_L0_076", "f_L0_077"):
        f = by[("F9", pid)]
        assert CS._metrics(f)[CS.DRAWN_LAYOUT_FLAG] == CS.FIXTURE_LAYOUT and CS.cause_of(f, b) == "drawn_layout"
    assert CS.cause_of(by[("F9", "f_L0_098")], b) == "collision"           # a wardrobe: no fixture, its tools stay
    wall = {"check": "S2", "severity": "major", "target": "f_L0_074", "room_id": piece_of(b, "f_L0_074")["room_id"],
            "message": "washing_machine f_L0_074 cuts wall w by 0.120 m", "source": "code",
            "evidence": {"metrics": {"depth_m": 0.12, "wall_id": "w_L0_001"}}}
    pair = copy.deepcopy(wall)
    pair["evidence"]["metrics"] = {"depth_m": 0.12, "other": "f_L0_075"}
    CS.mark_drawn_layout([wall, pair], b)
    assert CS.cause_of(wall, b) == "drawn_layout" and CS.cause_of(pair, b) == "collision"


def _blocked_project(tmp_path):
    from test_report import make_project

    out = make_project(tmp_path, polish=False, check=False)
    rm_path = out / "renders" / "render_manifest.json"
    rm = read(rm_path)
    for e in rm["renders"]:
        if e["camera"] == "cam_hol_1":
            e["exposure"] = dict(e["exposure"], ev=0.0, notes=["no interior block to meter: EV 0 used"])
    rm_path.write_text(json.dumps(rm), encoding="utf-8")
    sc_path = out / "scene" / "scene_manifest.json"
    sc = read(sc_path)
    for c in sc["cameras"]:
        c["source"] = "replayed"
        if c["name"] == "cam_salon_2":
            c["replay"] = {"status": "moved", "moved_m": 0.88, "blocked_by": "f_L0_206", "blocked_by_type": "fridge",
                           "reason": "the lens stood inside fridge f_L0_206 (single share 1.00)"}
        if c["name"] == "cam_yatak_1":
            c["replay"] = {"status": "repitched", "pitch_deg_old": -2.0, "pitch_deg": -12.0,
                           "reason": "the horizon was above the frame"}
    sc["cameras_from"] = {"path": "x", "moved": ["cam_salon_2"], "repitched": ["cam_yatak_1"]}
    sc_path.write_text(json.dumps(sc), encoding="utf-8")
    orch = out / "orchestrator"
    orch.mkdir(parents=True, exist_ok=True)
    blocked = {"kind": "finding", "source": "code", "checklist": "camera_blocked", "severity": "major",
               "room_id": "r_L0_salon", "finding": "cam_salon_2: the view is blocked: f_L0_206 fills 54.0 % of the "
                                                    "frame (over 50 %)"}
    events = [dict(blocked, seq=1, round=1, target="cam_yatak_2"), dict(blocked, seq=2, round=2, target="cam_salon_2"),
              dict(blocked, seq=3, round=2, target="cam_salon_1", dropped="no longer there"),
              {"seq": 4, "round": 2, "kind": "finding", "source": "vision", "checklist": "camera_blocked",
               "severity": "major", "target": "cam_yatak_1", "finding": "a vision claim"}]
    (orch / "log.json").write_text(json.dumps({"schema_version": "0.1", "kind": "agent_log", "project": "toy",
                                               "model": "m", "revision": "r", "events": events, "calls": []}),
                                   encoding="utf-8")
    return out


def test_the_final_report_marks_blocked_views_and_lists_the_cameras_the_build_changed(tmp_path):
    """G_render's and C_cam's asks. Fails on BASE (no ``blocked`` record, no ``camera_replay``): a view is "blocked
    (replayed camera, frozen)" when its exposure notes say no interior block to meter (cam_hol_1) or the last round has
    a code camera_blocked finding on it (cam_salon_2; not a dropped one, not round 1's cam_yatak_2, not a vision one);
    the summary, the views table and an advisory flag say so; the moved and re-pitched cameras are listed with the
    camera record's reason."""
    out = _blocked_project(tmp_path)
    m = FR.write_final(out)
    views = {v["camera"]: v for v in m["views"]}
    assert {c for c, v in views.items() if v.get("blocked")} == {"cam_hol_1", "cam_salon_2"}
    assert views["cam_hol_1"]["blocked"]["text"] == "blocked (replayed camera, frozen)"
    assert "no interior block to meter" in views["cam_hol_1"]["blocked"]["reasons"][0]
    assert "fills 54.0 %" in views["cam_salon_2"]["blocked"]["reasons"][0]
    assert m["summary"]["blocked_views"] == ["cam_salon_2", "cam_hol_1"]
    assert any(f.startswith("2 view(s) blocked") for f in m["advisory_flags"])
    assert [r["camera"] for r in m["camera_replay"]["moved"]] == ["cam_salon_2"]
    assert m["camera_replay"]["repitched"][0]["reason"] == "the horizon was above the frame"
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| blocked views | 2: cam_salon_2, cam_hol_1 |" in md
    assert "| cam_hol_1 | r_L0_hol | L0 | cycles, blocked (replayed camera, frozen) |" in md
    assert "## Replayed cameras the build changed, blocked views" in md
    assert "| cam_salon_2 | moved 0.88 m off f_L0_206 | the lens stood inside fridge f_L0_206 (single share 1.00) |" \
        in md
    assert "| cam_yatak_1 | re-pitched -2.0 -> -12.0 deg | the horizon was above the frame |" in md
    # a searched camera is "blocked" without the replayed note; a report without blocked views has no section
    assert FR.camera_replay(None) == {"moved": [], "repitched": []}
    assert FR.camera_replay_lines({"views": [], "camera_replay": {"moved": [], "repitched": []}}) == []


@needs_p6b
def test_the_p6b_log_names_the_four_blocked_yasama_views():
    """The last round (4) of P6b's real03 run still found yasama_2_2 (54 %) and yasama_3_2 / 5_2 / 6_1 (100 %)
    blocked; the report section marks them."""
    log = read(P6B_LOG)
    first = int(log.get("run_first_seq") or 1)
    got = AG.last_round_blocked([e for e in log["events"] if int(e.get("seq") or 0) >= first])
    assert sorted(got) == ["cam_r_L0_yasama_2_2", "cam_r_L0_yasama_3_2", "cam_r_L0_yasama_5_2",
                           "cam_r_L0_yasama_6_1"]
    assert "54.0 %" in got["cam_r_L0_yasama_2_2"]
