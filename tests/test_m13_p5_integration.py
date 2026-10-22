"""CPU tests of the integration of the fix round after P5 (22 Oct 2026): the cross-track asks of the seven build tracks
and the size table's intermediate bath and shower products (the user's decision of 22 Oct 2026: a bath or shower up
to 5 cm too long for its bay is shrunk to the NEAREST real product size that fits). Each test names the ask it pins;
the behaviour tests fail on the tree before the integration (the WIP snapshot 320d719). Pure Python, no Blender; the
tests that read the P4b / P5 run folders (runs/, git-ignored) skip without them."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

import _m11_room as M
from test_camera_override_free_floor import bathroom, cam
from test_furniture_fit_v2 import model
from wenart.agent import loop as LP
from wenart.agent import metrics as MX
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.blender import cameras as C
from wenart.blender import exterior_checks as X
from wenart.blender import furniture as BF
from wenart.blender import schemas as BS
from wenart.furniture import edit_ops as E
from wenart.furniture import fit as F
from wenart.furniture import locked as L
from wenart.furniture import plausibility as PL
from wenart.furniture import sizes as SZ
from wenart.ingest.generic import core as CORE
from wenart.ingest.generic import reading as RD
from wenart.levels import edits as LE

ROOT = Path(__file__).resolve().parents[1]
P4B_REAL03 = ROOT / "runs" / "20261017-091212-full" / "results" / "furniture" / "real03" / "building_decor.json"
P5_REAL04 = ROOT / "runs" / "20261017-224848-full" / "results" / "furniture" / "real04" / "building_decor.json"


def edit(op, **args):
    return dict({"op": op, "reason": "test", "round": 2, "log_seq": 7, "model": "test-model"}, **args)


def _piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


# --------------------------------------------------------------------------
# (2) the size table's intermediate tubs and trays: the bay shrink is a few cm
# --------------------------------------------------------------------------

def test_the_size_table_lists_the_intermediate_tubs_and_trays_with_their_sources():
    """User decision of 22 Oct 2026: the NEAREST real product that fits. The table lacked the products between
    1.50 x 0.70 and 1.70 x 0.75 m, so a 1.62 x 0.80 m tub in a 1.57 m bay dropped to 1.50 x 0.70 m."""
    tubs = {tuple(p) for p in SZ.products("bathtub")}
    assert {(1.50, 0.75), (1.55, 0.70), (1.55, 0.75), (1.60, 0.75)} <= tubs
    assert (0.90, 0.80) in {tuple(p) for p in SZ.products("shower")}
    assert SZ.products("bathtub")[0] == (1.70, 0.75)                     # the default product stays first
    rows = json.loads((ROOT / "wenart" / "recognition" / "size_table.json").read_text(encoding="utf-8"))["types"]
    assert "p5 (fix round after P5" in rows["bathtub"]["source"] and "Saniform Plus" in rows["bathtub"]["source"]
    assert "Superplan" in rows["shower"]["source"]
    # the agent's fix_fixture and the reading take the same nearest product: 7 cm shorter, 5 cm narrower
    tub = M.fp("tub", "bathtub", (0.785, 2.1), (1.62, 0.8), front=270.0, type_method="block_name")
    b = M.building(w=1.57, h=2.5, room_type="bathroom", window=None, door_x=0.8, furniture=[tub])
    res = E.apply_edit(b, edit("fix_fixture", piece_id="tub"))
    assert res["accepted"] and _piece(res["building"], "tub")["footprint"]["size"] == [1.55, 0.75]


@pytest.mark.skipif(not P4B_REAL03.is_file(), reason="P4b's real03 run (runs/20261017-091212-full) is not on this disk")
def test_real03s_tubs_and_shower_shrink_by_a_few_cm():
    """real03 (P4b building): the four 1.62 x 0.80 m tubs (clear bay 1.57 m) become 1.55 x 0.75 m (were 1.50 x 0.70);
    the shower f_L0_145 (0.85 x 1.02 m, clear 0.85 x 0.97 m) becomes 0.80 x 0.90 m (was 0.80 x 0.80); the other three
    showers keep their shrink (0.90 x 0.90, 1.00 x 0.80)."""
    from shapely.geometry import Polygon

    b = json.loads(P4B_REAL03.read_text(encoding="utf-8"))
    rooms = {r["id"]: r for r in b["rooms"] if len(r.get("polygon") or []) >= 3}
    got = {}
    for f in b["furniture"]:
        if f.get("type") in RD.BAY_TYPES and f.get("source") == "from_documents" and f.get("room_id") in rooms:
            fix = RD.bay_fit(f, Polygon(rooms[f["room_id"]]["polygon"]).buffer(0))
            if fix is not None:
                got[f["id"]] = tuple(round(v, 2) for v in fix["size"])
    assert got == {"f_L0_184": (1.55, 0.75), "f_L0_185": (1.55, 0.75), "f_L0_186": (1.55, 0.75),
                   "f_L0_187": (1.55, 0.75), "f_L0_145": (0.80, 0.90), "f_L0_179": (0.90, 0.90),
                   "f_L0_180": (0.90, 0.90), "f_L0_054": (1.00, 0.80)}


def test_the_locked_check_accepts_the_agents_bay_shrink_and_nothing_wider():
    """F_reading's ask (locked._fixture_fix_problems): the refit's locked check refused fix_fixture's bay shrink
    ("resized although its drawn size is only 0 % outside the real range"). Now accepted when the overrun is at most
    5 cm and the new size is a real product inside the drawn box; anything else is still refused."""
    tub = M.fp("tub", "bathtub", (0.785, 2.1), (1.62, 0.8), front=270.0, type_method="block_name")
    src = M.building(w=1.57, h=2.5, room_type="bathroom", window=None, door_x=0.8, furniture=[tub])
    res = E.apply_edit(src, edit("fix_fixture", piece_id="tub"))
    assert res["accepted"] and L.check(src, res["building"], "complete") == []
    assert L.BAY_OVERRUN_MAX_M == RD.BAY_OVERRUN_M[1]
    for change, words in (({"size": [1.52, 0.75]}, "not a real bathtub product"),
                          ({"center": [0.785, 1.9]}, "no longer inside its drawn box"),
                          ({"overrun_m": 0.08}, "at most 0.05 m")):
        b = copy.deepcopy(res["building"])
        t = _piece(b, "tub")
        if "overrun_m" in change:
            t["adjusted_by_ai"]["fix_fixture"]["bay"]["overrun_m"] = change["overrun_m"]
        else:
            t["footprint"].update(change)
        assert any(words in v for v in L.check(src, b, "complete")), change


# --------------------------------------------------------------------------
# Asks of K_ceiling, L_render, E_exterior and the agent camera checks
# --------------------------------------------------------------------------

def test_an_agent_camera_in_a_room_without_free_floor_keeps_off_the_floor_decor():
    """K_ceiling's ask (exterior_checks.free_floor_problems): in a room with no free point only the pieces at camera
    height counted, so an agent camera inside a 1.6 m plant passed; the search's fallback avoids the decor too."""
    from wenart.blender import camsearch as CS

    b = bathroom()
    b["decor"] = [{"id": "dec_1", "room_id": "r_L0_banyo_2", "type": "plant_large", "center": [27.65, 4.35, 0.0],
                   "size": [0.4, 0.4, 1.6], "rotation_deg": 0.0}]
    (p,), warning = CS.candidate_positions(b["rooms"][0], b)
    assert warning
    msg = X.free_floor_problems(b, cam([27.65, 4.35, 1.5]))
    assert msg and "from floor decor" in msg[0]
    assert X.free_floor_problems(b, cam([p[0], p[1], 1.5])) == []          # the search's own point still passes


def test_the_new_render_fields_are_typed():
    """L_render's ask (schemas): the sky pull's edge_dot_px / edge_px and the exposure's wb_day_green /
    wb_view_tint_gain are typed (optional; older manifests have none)."""
    pull = {"ev": -1.0, "k": 2, "sky_px": 100, "sky_share": 0.2, "median_before": 0.5, "median_after": 0.4,
            "rule": "r", "edge_dot_px": 4, "edge_px": 1924}
    jsonschema.validate(pull, BS.SKY_PULL)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(dict(pull, edge_dot_px=-1), BS.SKY_PULL)
    exposure = {"type": "object", "properties": BS.EXPOSURE["properties"]}
    jsonschema.validate({"wb_day_green": 1.402, "wb_view_tint_gain": 1.243064}, exposure)
    jsonschema.validate({"wb_day_green": None, "wb_view_tint_gain": round(1 / 1.3, 6)}, exposure)
    for bad in ({"wb_view_tint_gain": 1.5}, {"wb_view_tint_gain": 0.5}, {"wb_day_green": 0.0}):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, exposure)


def test_a_long_low_view_is_told_it_is_framed_close_by_design_and_keeps_it_through_a_replay():
    """E_exterior's ask (prompts.camera_note): the critic is told the closer framing of a long, low building is by
    design (user decision (2) of 22 Oct 2026). A replayed camera keeps ``long_low`` (cameras.REPLAY_OPTIONAL), so its
    X6 fill range and the note survive a replay."""
    corner = {"name": "ext_1", "view": "corner", "sides": ["south", "east"],
              "long_low": {"length_m": 33.3, "height_m": 3.2, "ratio": 10.4, "fill_target": 0.9}}
    note = P.camera_note(corner)
    assert "framed close by design" in note and "90%" in note and "too close" in note
    assert "framed close" not in P.camera_note(dict(corner, long_low=None))
    assert "framed close" not in P.camera_note(dict(corner, view="aerial"))
    rec = {"name": "ext_1", "position": [1.0, 2.0, 1.6], "target": [5.0, 5.0, 1.6], "lens_mm": 26.0,
           "kind": "exterior", "view": "corner", "long_low": corner["long_low"]}
    plan = C.replay_cameras({"cameras": [rec]})["plans"][0]
    assert plan["long_low"] == corner["long_low"]


def test_the_planner_and_the_tools_name_the_plan_crop_and_the_confirm_path():
    """F_reading's and A_agent's asks (prompts / tools): an untyped piece is marked only with the plan crop image it
    was read from (else no_crop); retype_piece with the piece's own type confirms an unverified piece."""
    assert "no_crop" in P.PLANNER_SYSTEM_M12 and "check/<view>_plan.jpg" in P.PLANNER_SYSTEM_M12
    assert "confirms an unverified piece" in P.PLANNER_SYSTEM_M12
    assert "no_crop" in TL.DESCRIPTIONS["mark_not_furniture"]
    assert "confirms an unverified" in TL.DESCRIPTIONS["retype_piece"]


# --------------------------------------------------------------------------
# Asks of D_data and P_report
# --------------------------------------------------------------------------

def test_a_doubt_free_model_wins_a_tie_of_its_size_step():
    """D_data's ask (fit.rank_key): two models equal in everything but a vision doubt other than the quality text
    (here the type) -> the doubt-free one ranks first; the size step stays rank_key(...)[2]; a quality-only doubt is
    no other doubt (the vision quality key ranks it)."""
    base = dict(real_product=True, audit={"status": "keep", "vision_quality": 4})
    doubtful = model("doubt", "fridge", 0.6, 0.65, 1.8, **copy.deepcopy(base))
    doubtful["audit"]["vision_doubt"] = ["the vision check says it is not a fridge (a tall_cabinet)"]
    plain = model("plain", "fridge", 0.6, 0.65, 1.8, **dict(base, audit={"status": "keep", "vision_quality": 3}))
    assert [e["id"] for e in F.rank_candidates([doubtful, plain], 0.6, 0.65)] == ["abo_plain", "abo_doubt"]
    assert F.rank_key(doubtful, 0.6, 0.65)[2] == F.rank_key(plain, 0.6, 0.65)[2] == 0
    assert F.other_doubt_of({"audit": {"vision_doubt": ["vision quality 2 (<= 2)"]}}) == 0
    assert F.other_doubt_of({"audit": {"vision_doubt": ["the vision check sees more than one object"]}}) == 1
    assert "no other audit vision doubt" in F.RANKING_RULE


def test_the_scene_manifest_names_the_real_reason_a_piece_is_not_built():
    """P_report's ask (blender/furniture.py not_built): every unbuilt piece carried "a drawn symbol both
    recognition passes call not_furniture"; now the reason of the building, in the report's order."""
    from wenart.report import final as FN

    pieces = [{"id": "a", "build": False, "not_built_reason": "untyped (CLAUDE.md: no untyped piece is built)"},
              {"id": "b", "build": False, "inferred_reason": "a column of the A-BA grid (no furniture)"},
              {"id": "c", "build": False, "adjusted_by_ai": {"not_furniture": "other", "reason": "a stair line",
                                                             "model": "qwen", "round": 3}},
              {"id": "d", "build": False, "type_candidates": [{"type": "not_furniture"}, {"type": "not_furniture"}]},
              {"id": "e", "build": False}]
    got = [BF.not_built_reason(p) for p in pieces]
    assert got[0].startswith("untyped") and got[1].startswith("a column")
    assert got[4] == "build false, no reason recorded"
    assert got[2] == "marked not furniture (other) by qwen, round 3: a stair line"
    assert got[3] == BF.NOT_BUILT_REASON
    assert got[:3] + got[4:] == [FN.not_built_text(p) for p in pieces[:3] + pieces[4:]]


def _events():
    def finding(r, check, target):
        return {"kind": "finding", "round": r, "check": check, "target": target, "severity": "major",
                "message": f"{check} on {target}"}
    return [finding(1, "F3", "f1"), finding(1, "F6", "f2"), finding(2, "G6", "f3"),
            {"kind": "round", "round": 1, "counts": {"findings_removed": 1}},
            {"kind": "round", "round": 2, "counts": {"findings_removed": 4}}]


def test_the_metrics_and_the_stop_note_count_new_findings_and_compare_the_same_rounds():
    """P_report's asks (agent/metrics.py, loop.py): the new findings, the net and the dry re-checks of the measured
    rounds only. P5 read "23 ... (the dry re-checks predicted 38)": rounds 1-2 measured against rounds 1-3 predicted."""
    fr = MX.findings_removed_metrics(_events(), [1, 2])
    assert fr["total"] == 2 and fr["new_per_round"] == {"1": 1} and fr["new"] == 1 and fr["net"] == 1
    assert fr["dry_recheck_same_rounds"] == 1 and fr["dry_recheck_unmeasured"] == 4
    measured = {"total": 2, "per_round": {"1": 2}, "new": 1, "net": 1, "predicted_same_rounds": 1,
                "predicted_unmeasured": 4}
    assert LP.stop_note(measured, 3, [1, 2]) == (
        "2 critical/major findings removed in round 1 (measured by the next round's critics; the dry re-checks of the "
        "same rounds predicted 1, the last round predicted 4 more, not measured); 1 new, net 1; 3 accepted edits in 2 "
        "rounds")


# --------------------------------------------------------------------------
# edit_ops asks (P_report, A_agent)
# --------------------------------------------------------------------------

def test_an_agent_edit_keeps_the_codes_earlier_record():
    """P_report's ask (edit_ops._label): P5's agent moves overwrote the code's nightstand retypes of
    f_L0_032/034/036/038 (rule nightstand_symbol, reason, plan crop). The earlier record now stays under
    ``previous``."""
    code = {"by": "code", "rule": "nightstand_symbol", "reason": "a nightstand symbol at the bed head",
            "crop": "recognition/crops/sym_L0_015_ctx.png", "changed": {"type": "floor_lamp"}}
    stand = M.fp("n1", "nightstand", (0.3, 3.7), (0.45, 0.4), rotation=0.0, front=270.0, type_method="inferred",
                 adjusted_by_ai=copy.deepcopy(code), drawn_type="floor_lamp")
    b = M.building(furniture=[stand])
    res = E.apply_edit(b, edit("move", piece_id="n1", center=[0.35, 3.7]))
    assert res["accepted"], res["failed_checks"]
    adj = _piece(res["building"], "n1")["adjusted_by_ai"]
    assert adj["reason"] == "test" and adj["previous"] == [code]
    assert adj["changed"]["type"] == "floor_lamp"                    # the first old values, as before
    again = _piece(E.apply_edit(res["building"], edit("move", piece_id="n1", center=[0.3, 3.7]))["building"], "n1")
    assert [r.get("rule") for r in again["adjusted_by_ai"]["previous"]] == ["nightstand_symbol", None]


def test_retype_piece_with_its_own_type_confirms_an_unverified_piece():
    """A_agent's ask (edit_ops._change_type): complete_group refuses a group whose anchor is unverified ("retype_piece
    first") and retype_piece refused the anchor's own type as no_change (P5 seq 4730/4732, 5111/5113). Now it confirms
    the piece: verified, labelled, the AI candidates kept, the fitted asset kept; a verified piece is still
    no_change."""
    cands = [{"type": "desk", "model": "qwen", "pass": 1}, {"type": "sofa", "model": "glm", "pass": 2}]
    desk = M.fp("d1", "desk", (2.5, 3.6), (1.40, 0.70), front=270.0, status="unverified", type_method="inferred",
                type_candidates=cands, asset={"library": "abo", "asset_id": "abo_desk", "method": "library"})
    b = M.building(furniture=[desk])
    b["needs_review"] = [{"id": "d1", "reason": "the AI passes disagree"}]
    res = E.apply_edit(b, edit("retype_piece", piece_id="d1", type="desk"))
    assert res["accepted"], res["failed_checks"]
    d = _piece(res["building"], "d1")
    assert d["status"] == "verified" and d["adjusted_by_ai"]["confirmed_type"] == "desk"
    assert d["adjusted_by_ai"]["changed"] == {"status": "unverified"} and d["type_candidates"] == cands
    assert d["asset"]["asset_id"] == "abo_desk" and res["building"]["needs_review"] == []
    again = E.apply_edit(res["building"], edit("retype_piece", piece_id="d1", type="desk"))
    assert not again["accepted"] and again["failed_checks"][0].startswith("no_change")


@pytest.mark.skipif(not P5_REAL04.is_file(), reason="P5's real04 run (runs/20261017-224848-full) is not on this disk")
def test_p5s_desks_are_confirmed_and_the_retype_refit_reads_the_briefs_style_family():
    """A_agent's asks on P5's building_decor.json: the desks f_L0_024 / f_L0_026 are confirmed; the retype refit's
    style family is the brief's ("modern", as style.json), not None (the working building's first fit had none)."""
    b = json.loads(P5_REAL04.read_text(encoding="utf-8"))
    assert E._style_family_of(b) == "modern" and E.licence_mode_of(b) == "relaxed"
    for pid in ("f_L0_024", "f_L0_026"):
        res = E.apply_edit(b, edit("retype_piece", piece_id=pid, type="desk"))
        assert res["accepted"] and _piece(res["building"], pid)["status"] == "verified", res["failed_checks"]
    plain = M.building(furniture=[])
    assert E._style_family_of(plain) is None                          # no brief style: no filter, as before


# --------------------------------------------------------------------------
# Reading and plausibility asks (F_reading, A_agent)
# --------------------------------------------------------------------------

def test_a_drawn_wardrobe_in_a_hall_is_no_wrong_room_finding():
    """F_reading's ask (plausibility.DRAWN_ANYWHERE_TYPES): the reader types real04's corridor coat closets as
    wardrobes; F1 called them "not a piece of a hall room". A wardrobe the AI would add to a hall is still not offered
    (the hall rows are unchanged)."""
    closet = M.fp("w1", "wardrobe", (2.5, 3.7), (1.52, 0.6), front=270.0, type_method="rule")
    b = M.building(room_type="hall", window=None, furniture=[closet])
    f1 = [v for v in PL.score_room(b, M.ROOM_ID)["violations"] if v["check"] == "F1"]
    assert f1 == []
    added = dict(closet, source="added_by_ai")
    b2 = M.building(room_type="hall", window=None, furniture=[added])
    assert [v["check"] for v in PL.score_room(b2, M.ROOM_ID)["violations"] if v["check"] == "F1"] == ["F1"]


def test_an_ai_typed_coat_closet_is_reported_as_a_wardrobe():
    """F_reading's ask (ingest core.py): the AI-typed coat closet the vector geometry outranks was reported as "a table
    with chairs drawn around it"; now "a coat closet: hanging rail with hangers"."""
    from test_m13_p5_furniture import TABLE, _closet
    from wenart.ingest.generic import symbols as SY

    split = SY.split_table_chairs(_closet(), TABLE, 0.0)
    reason, note = CORE.split_override_text(split, "c_1", "bench", 1)
    assert reason.startswith("a coat closet: hanging rail with hangers") and "one wardrobe" in note
    plain = SY.split_table_chairs(_closet(rail=False), TABLE, 0.0)
    reason, note = CORE.split_override_text(plain, "c_2", "sofa", 3)
    assert reason.startswith("a table with chairs") and note.endswith("2 chairs: split (M12)")


def test_a_level_edit_with_a_target_finding_is_no_schema_error():
    """A_agent's ask (levels META_KEYS guard): ``target_finding`` is a meta key of level edits too."""
    op, args, meta = LE.normalise({"op": "set_terrain", "kind": "planar", "reason": "the KOT marks fall to the east",
                                   "round": 1, "target_finding": {"check": "L3", "target": "site"}})
    assert "target_finding" not in args and meta["target_finding"] == {"check": "L3", "target": "site"}
    assert not any("target_finding" in e for e in LE.schema_errors(op, args))
