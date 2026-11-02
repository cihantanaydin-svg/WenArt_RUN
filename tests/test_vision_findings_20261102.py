"""Three general rules of 2 Nov 2026 (real04 run 20261101-093151 was the test case; every project uses them) (CPU).

A. A vision or judge claim that a room's anchor or main group is missing is a minor framing note when code shows the
   anchor built in that room and visible in another view of the room (``critic_vision.downgrade_anchor_claims``).
B. The architect's F2 and the code critic's F7 / R3 measure a doorway the same way (``plausibility.door_measures``),
   and F2's ``move_piece`` moves a piece clear of the critic's approach strip.
C. A vision, judge or Argus finding is tied to the image it was seen on (``image_sha256``); once that view's image
   holds other pixels the finding is dropped as stale, with the reason.
"""
import copy
import json
from types import SimpleNamespace

from wenart.agent import causes as CS
from wenart.agent import critic_vision as CV
from wenart.agent import inspector as INS
from wenart.agent import judge as JD
from wenart.agent import loop as LP
from wenart.audit import argus_ai as AX
from wenart.audit import consistency as CY
from wenart.audit import inputs as AI_
from wenart.audit import report as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RR
from wenart.furniture import plausibility as PL


# --------------------------------------------------------------------------
# A: a missing-anchor claim from one view, the anchor shown by another
# --------------------------------------------------------------------------

def _piece(pid, ptype, room, centre, size, front=-90.0):
    return {"id": pid, "type": ptype, "room_id": room, "level_id": "L0", "build": True, "source": "from_documents",
            "front_deg": front, "footprint": {"center": list(centre), "size": list(size), "rotation_deg": 0.0},
            "height": 0.9}


def _bedroom():
    room = {"id": "r_bed", "level_id": "L0", "room_type": "bedroom", "label": "Yatak",
            "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}
    living = {"id": "r_liv", "level_id": "L0", "room_type": "living", "label": "Salon",
              "polygon": [[4, 0], [9, 0], [9, 4], [4, 4]]}
    return {"levels": [{"id": "L0", "elevation": 0.0}], "rooms": [room, living], "walls": [], "openings": [],
            "furniture": [_piece("f_bed", "bed_double", "r_bed", (2.0, 1.0), (1.6, 2.0), 90.0),
                          _piece("f_wardrobe", "wardrobe", "r_bed", (3.5, 3.7), (1.0, 0.6)),
                          _piece("f_arm1", "armchair", "r_liv", (6.0, 2.0), (0.8, 0.8)),
                          _piece("f_sofa", "sofa", "r_liv", (7.5, 3.5), (2.0, 0.9))]}


def _cameras():
    return [{"name": "cam_bed_1", "room_id": "r_bed", "visible_furniture": ["f_wardrobe"],
             "anchors_in_frame": [], "set_in_frame": []},
            {"name": "cam_bed_2", "room_id": "r_bed", "visible_furniture": ["f_bed", "f_wardrobe"],
             "anchors_in_frame": ["f_bed"]},
            {"name": "cam_bed_3", "room_id": "r_bed", "visible_furniture": ["f_bed"], "anchors_in_frame": ["f_bed"]},
            {"name": "cam_liv_1", "room_id": "r_liv", "visible_furniture": ["f_sofa"], "anchors_in_frame": ["f_sofa"]},
            {"name": "cam_liv_2", "room_id": "r_liv", "visible_furniture": ["f_arm1", "f_sofa"],
             "anchors_in_frame": ["f_arm1", "f_sofa"]}]


def _crosscheck(bed_2=0.86, bed_3=0.93, bed_1=None):
    def proj(**shares):
        return {"projected": {pid: {"kind": "furniture", "visible_share": s, "in_view": True}
                              for pid, s in shares.items() if s is not None}}
    return {"cameras": {"cam_bed_1": {"json_crosscheck": proj(f_wardrobe=0.9, f_bed=bed_1)},
                        "cam_bed_2": {"json_crosscheck": proj(f_bed=bed_2, f_wardrobe=0.4)},
                        "cam_bed_3": {"json_crosscheck": proj(f_bed=bed_3)}}}


def _claim(message="The bedroom has no bed; with the wardrobe and the desk it reads as a corner office",
           target="r_bed", view="cam_bed_1", source="judge", check="Q4"):
    return {"id": "j:judge_cam_bed_1:1", "source": source, "check": check, "severity": "critical", "target": target,
            "room_id": target, "message": message, "evidence": {"view": view, "image": 1}}


def test_a_no_bed_claim_from_the_wardrobe_view_is_a_framing_note_when_other_views_show_the_bed():
    b = _bedroom()
    seen = CV.views_seen(_cameras(), CV.crosscheck_of(_crosscheck()))
    out, notes = CV.downgrade_anchor_claims([_claim()], b, seen)
    f = out[0]
    assert f["severity"] == "minor" and f["kind"] == CV.FRAMING and f["cause"] == CS.FRAMING_CAUSE
    m = f["evidence"]["metrics"]
    assert m["framing"] and m["severity_was"] == "critical" and m["seen_on"] == "cam_bed_1"
    assert m["anchor_shown"][0] == {"piece": "f_bed", "type": "bed_double", "view": "cam_bed_3", "share": 0.93,
                                    "source": "the render cross-check (visible share of its front)"}
    assert "f_bed" in f["downgraded"] and "cam_bed_3" in f["downgraded"] and "0.93" in f["downgraded"]
    assert len(notes) == 1 and notes[0]["severity_was"] == "critical"
    # the cause survives a copy without it (the loop's extra_work pops it): no tool, reported to the cameras
    plain = {k: v for k, v in f.items() if k != "cause"}
    assert CS.cause_of(plain, b) == "framing" and CS.tools_for_finding(plain) == []
    assert CS.REPORT_TO["framing"] == "cameras" and CS.no_tool_reason(plain).startswith("a framing note")
    # idempotent: a note is never downgraded twice
    again, notes2 = CV.downgrade_anchor_claims(out, b, seen)
    assert again == out and notes2 == []


def test_the_claim_stands_when_no_other_view_shows_the_anchor_or_its_own_view_does():
    b = _bedroom()
    hidden = CV.views_seen(_cameras(), CV.crosscheck_of(_crosscheck(bed_2=0.2, bed_3=0.3)))
    out, notes = CV.downgrade_anchor_claims([_claim()], b, hidden)
    assert out[0]["severity"] == "critical" and not notes
    # the view the claim was made on shows the bed clearly: the bed does not read as a bed (a look problem), kept
    cams = _cameras()
    cams[0]["visible_furniture"] = ["f_wardrobe", "f_bed"]
    own = CV.views_seen(cams, CV.crosscheck_of(_crosscheck(bed_1=0.8)))
    out, notes = CV.downgrade_anchor_claims([_claim()], b, own)
    assert out[0]["severity"] == "critical" and not notes
    # a bed the build does not make is no answer
    b2 = copy.deepcopy(b)
    b2["furniture"][0]["build"] = False
    out, notes = CV.downgrade_anchor_claims([_claim()], b2, CV.views_seen(_cameras(), CV.crosscheck_of(_crosscheck())))
    assert out[0]["severity"] == "critical" and not notes


def test_only_missing_anchor_claims_by_vision_on_a_room_are_downgraded():
    b = _bedroom()
    seen = CV.views_seen(_cameras(), CV.crosscheck_of(_crosscheck()))
    others = [_claim("The bed has no headboard and no nightstand beside it"),
              _claim("There is no space beside the bed to walk"),
              _claim("The wardrobe has its back to the room", target="f_wardrobe"),
              _claim(source="code"),
              _claim(check="Q5")]
    out, notes = CV.downgrade_anchor_claims(others, b, seen)
    assert out == others and notes == []


def test_a_missing_main_group_claim_is_answered_by_the_group_it_names():
    b = _bedroom()
    seen = CV.views_seen(_cameras(), None)                 # no render cross-check: the camera search's frame lists
    assert seen["cam_liv_2"]["pieces"]["f_arm1"] == {"share": None,
                                                      "source": "the camera search (in the frame, not hidden)"}
    claim = _claim("The main furniture group (armchairs and side table) is missing", target="r_liv", view="cam_liv_1",
                   source="argus", check="Q4")
    out, notes = CV.downgrade_anchor_claims([claim], b, seen)
    assert out[0]["severity"] == "minor" and out[0]["evidence"]["metrics"]["anchor_shown"][0]["piece"] == "f_arm1"
    assert "in its frame" in notes[0]["reason"]
    # the armchairs shown by no other view: the claim stands
    cams = [c for c in _cameras() if c["name"] != "cam_liv_2"]
    out, notes = CV.downgrade_anchor_claims([claim], b, CV.views_seen(cams, None))
    assert out[0]["severity"] == "critical" and not notes


def test_a_cross_check_record_the_current_pose_no_longer_frames_is_not_used():
    cams = _cameras()
    cams[2]["visible_furniture"] = []                       # cam_bed_3 was set to another pose since the check
    seen = CV.views_seen(cams, CV.crosscheck_of(_crosscheck()))
    assert "f_bed" not in seen["cam_bed_3"]["pieces"] and seen["cam_bed_2"]["pieces"]["f_bed"]["share"] == 0.86
    final = {"views": [{"camera": "cam_bed_2", "json_crosscheck": {"projected": {}}}]}
    assert CV.crosscheck_of(final) == {"cam_bed_2": {"projected": {}}}


class _Reply:
    def __init__(self, data):
        self.data, self.errors = data, []


class _Judge:
    def __init__(self, data):
        self.data = data

    def critic(self, messages, schema, call_id=""):
        return _Reply(self.data)


def test_the_judge_downgrades_a_framing_claim_and_records_the_image_it_judged(tmp_path):
    b = _bedroom()
    from PIL import Image

    image = tmp_path / "cam_bed_1_preview.jpg"
    Image.new("RGB", (8, 8), (120, 100, 80)).save(image)
    data = {"client_ready_score": 2, "tags": ["missing_anchor"], "note": "an office, not a bedroom",
            "problems": [{"check": "Q4", "severity": "critical", "target": "r_bed",
                          "message": "The bedroom has no bed; it reads as a corner office"}]}
    seen = CV.views_seen(_cameras(), CV.crosscheck_of(_crosscheck()))
    got = JD.judge_view(_Judge(data), b, {"name": "cam_bed_1", "room_id": "r_bed"}, image, seen=seen)
    f = got["findings"][0]
    assert f["severity"] == "minor" and got["row"]["problems"][0]["severity"] == "minor"
    assert got["row"]["problems"][0]["kind"] == "framing" and got["row"]["framing"]
    sha = CV.file_sha256(image)
    assert f["evidence"]["image_sha256"] == sha and f["evidence"]["image_view"] == "cam_bed_1"
    assert got["row"]["image_sha256"] == sha and got["row"]["image_file"] == image.name
    # without the views the problem stays as the judge said
    plain = JD.judge_view(_Judge(data), b, {"name": "cam_bed_1", "room_id": "r_bed"}, image)
    assert plain["findings"][0]["severity"] == "critical"


# --------------------------------------------------------------------------
# B: F2 and F7 measure a doorway the same way
# --------------------------------------------------------------------------

def _doorway(wardrobe_x0=2.35):
    """A bedroom r1 (y < 4) and a hall r2 (y > 4) with door d_L0_001 (0.9 m) in the wall between them; a wardrobe in r1
    whose left side starts at ``wardrobe_x0`` (the approach strip runs from x 1.55 to 2.45, 0.6 m deep)."""
    w = 1.0
    return {"levels": [{"id": "L0", "elevation": 0.0}],
            "rooms": [{"id": "r1", "level_id": "L0", "room_type": "bedroom",
                       "polygon": [[0, 0], [4, 0], [4, 3.95], [0, 3.95]]},
                      {"id": "r2", "level_id": "L0", "room_type": "hall",
                       "polygon": [[0, 4.05], [4, 4.05], [4, 7], [0, 7]]}],
            "walls": [{"id": "w1", "level_id": "L0", "start": [0, 4], "end": [4, 4], "thickness": 0.1}],
            "openings": [{"id": "d_L0_001", "type": "door", "level_id": "L0", "wall_id": "w1", "center": [2.0, 4.0],
                          "width": 0.9, "height": 2.1}],
            "furniture": [_piece("f1", "wardrobe", "r1", (wardrobe_x0 + w / 2, 3.65), (w, 0.6))]}


def _sides(b):
    return [{"opening": b["openings"][0], "type": "door", "a": "r2", "b": "r1", "area_m2": 1.9}]


def _f2(b):
    rules = RR.furniture_rules(AA.Plan(b), _sides(b))
    q = next(q for q in rules if q["id"] == "F2")
    return next(a for a in q["answers"] if a["element"] == "d_L0_001"), rules


def test_f2_uses_the_critics_approach_strip_and_threshold():
    b = _doorway(2.35)                     # 0.10 x 0.60 m = 0.06 m2 on the strip: 16 % of F2's old 0.8 m box
    m = {x["door"]: x for x in PL.door_measures(b, b["rooms"][0])}["d_L0_001"]
    assert m["blocked"] and m["blockers"] == ["f1"] and abs(m["approach"]["f1"] - 0.06) < 1e-6
    assert any(v["check"] == "F7" and v["target"] == "f1" for v in PL.score_room(b, "r1")["violations"])
    ans, rules = _f2(b)
    assert ans.get("open") and "approach strip" in ans["found"] and "f1" in ans["found"]
    assert ans["options"][0]["choice"].startswith("move_piece") or ans["options"][0].get("action") == "move_piece"
    # the audit's Y2 ("the architect's rule F2 says they are fine") no longer arises: F2 holds the doorway open too
    inspector = {"code": [{"check": "F7", "severity": "critical", "target": "f1", "message": "wardrobe blocks door d_L0_001"}]}
    assert CY.audit(inspector, {"questions": rules})["findings"] == []
    # a piece clear of the strip: both say free
    free = _doorway(2.47)
    assert not {x["door"]: x for x in PL.door_measures(free, free["rooms"][0])}["d_L0_001"]["blocked"]
    assert not any(v["check"] == "F7" for v in PL.score_room(free, "r1")["violations"])
    assert not _f2(free)[0].get("open")


def test_a_small_move_that_leaves_the_piece_on_the_strip_does_not_satisfy_f2():
    b = _doorway(2.40)                     # moved 0.05 m: still 0.03 m2 on the strip (F7), and so F2
    assert any(v["check"] == "F7" for v in PL.score_room(b, "r1")["violations"])
    assert _f2(b)[0].get("open")


def test_f2_move_piece_moves_the_piece_clear_of_the_critics_strip():
    b = _doorway(2.35)
    plan = AA.Plan(copy.deepcopy(b))
    ok, text = AA.act_move_piece(plan, "F2:d1", {"by": "architect"}, "f1", "d_L0_001")
    assert ok, text
    assert not {x["door"]: x for x in PL.door_measures(plan.b, plan.room["r1"])}["d_L0_001"]["blocked"]
    assert not any(v["check"] == "F7" for v in PL.score_room(plan.b, "r1")["violations"])
    # the check after a move names the critic's measure when the piece would still block
    still = AA.still_blocks(AA.Plan(b), b["furniture"][0], ["d_L0_001"])
    assert still and "approach strip of d_L0_001" in still and "F7" in still


# --------------------------------------------------------------------------
# C: a finding is tied to the image it was seen on
# --------------------------------------------------------------------------

def _black_frame(sha, name="ext_1_preview.jpg", source="argus"):
    return {"id": "a:F3", "source": source, "check": "V1", "severity": "critical", "target": "ext_1",
            "message": "Argus: The camera frame is entirely black and empty",
            "evidence": {"image_sha256": sha, "image_file": name, "image_view": "ext_1"}}


def test_stamp_and_stale_findings(tmp_path):
    img = tmp_path / "ext_1_preview.jpg"
    img.write_bytes(b"black frame")
    plan_crop = tmp_path / "ext_1_plan.jpg"
    plan_crop.write_bytes(b"plan")
    found = [{"evidence": {"image": 1}}, {"evidence": {"image": 2}}, {"evidence": {"image": 3}}, {"evidence": {}}]
    CV.stamp_seen(found, [img, plan_crop], ["ext_1", None])
    assert found[0]["evidence"]["image_sha256"] == CV.file_sha256(img) and found[0]["evidence"]["image_view"] == "ext_1"
    assert found[1]["evidence"]["image_file"] == "ext_1_plan.jpg" and "image_view" not in found[1]["evidence"]
    assert "image_sha256" not in found[2]["evidence"] and found[3]["evidence"] == {}
    now = CV.image_shas(tmp_path)
    kept, stale = CV.drop_stale(found, now)
    assert not stale and len(kept) == 4                      # the same pixels: nothing is stale
    img.write_bytes(b"the house in the evening sun")         # the view is re-rendered
    kept, stale = CV.drop_stale(found, CV.image_shas(tmp_path))
    assert len(stale) == 1 and stale[0]["stale"].startswith("stale: seen on ext_1_preview.jpg of view ext_1")
    assert len(kept) == 3                                     # no hash, or an image that did not change: kept
    gone = _black_frame("abc", name="cam_gone_preview.jpg")
    assert CV.drop_stale([gone], CV.image_shas(tmp_path)) == ([gone], [])   # no image now: nothing to compare


def _project(tmp_path, pixels=b"new pixels"):
    (tmp_path / "renders").mkdir(exist_ok=True)
    img = tmp_path / "renders" / "ext_1_preview.jpg"
    img.write_bytes(pixels)
    return img


def test_the_inspector_drops_a_finding_seen_on_other_pixels(tmp_path):
    img = _project(tmp_path, b"old black frame")
    old = CV.file_sha256(img)
    img.write_bytes(b"the final render of ext_1")
    car = dict(_black_frame(old, source="vision"), message="The entrance is obstructed by a car", id="v:1")
    fresh = dict(_black_frame(CV.file_sha256(img), source="vision"), message="the door floats", id="v:2",
                 check="Q1", severity="major")
    nohash = {"source": "vision", "check": "Q7", "severity": "major", "target": "d_L0_001", "message": "a garage door look"}
    rec = INS.report(tmp_path, 3, {"code": [], "vision_kept": [car, fresh, nohash], "vision_dropped": []}, [])
    assert [r["message"] for r in rec["vision"]] == ["the door floats", "a garage door look"]
    assert rec["counts"]["stale"] == 1 and rec["counts"]["dropped"] == 1
    assert rec["dropped"][0]["outcome"].startswith("dropped: stale: seen on ext_1_preview.jpg")
    assert rec["vision"][0]["image_sha256"] == CV.file_sha256(img)          # the row keeps its image for Argus
    assert "stale" in INS.report_md(rec)


def test_argus_lines_drop_stale_inspector_rows_and_judge_rows(tmp_path):
    img = _project(tmp_path, b"old")
    old = CV.file_sha256(img)
    img.write_bytes(b"new")
    new = CV.file_sha256(img)
    inspector = {"round": 2, "code": [], "vision": [
        {"check": "V1", "severity": "critical", "target": "ext_1", "message": "The camera frame is entirely black",
         "source": "vision", "image_sha256": old, "image_file": img.name, "image_view": "ext_1"},
        {"check": "Q1", "severity": "major", "target": "d_L0_001", "message": "the door floats", "source": "vision",
         "image_sha256": new, "image_file": img.name, "image_view": "ext_1"}]}
    rubric = [{"view": "ext_1", "client_ready_score": 1, "note": "black", "tags": [], "image_sha256": old,
               "image_file": img.name, "problems": [{"check": "V1", "severity": "critical", "target": "ext_1",
                                                     "message": "entirely black"}]},
              {"view": "ext_2", "client_ready_score": 2, "note": "plain", "tags": [], "problems": []}]
    inp = AI_.Inputs(project="p", layout="pod", root=tmp_path, inspector=inspector, rubric=rubric)
    line = AR.inspector_line(inp)
    assert [f["message"] for f in line["findings"]] == ["the door floats"]
    assert line["findings"][0]["evidence"]["image_sha256"] == new and "1 stale" in line["note"]
    judge = AR.judge_line(inp)
    assert [f["target"] for f in judge["findings"]] == ["ext_2"] and judge["stale"][0]["view"] == "ext_1"
    rep = AR.run(inp)
    assert {x["line"] for x in rep["stale"]} == {"inspector", "judge"}
    assert "Stale vision findings" in AR.report_md(rep)


def test_argus_work_carries_the_image_and_the_loop_drops_it_once_re_rendered(tmp_path):
    img = _project(tmp_path, b"black")
    old = CV.file_sha256(img)
    odir = tmp_path / "orchestrator"
    odir.mkdir()
    rec = {"work": [{"fix": "agent_round", "check": "V1", "severity": "critical", "target": "ext_1",
                     "message": "Argus: The camera frame is entirely black", "image_sha256": old,
                     "image_file": img.name, "image_view": "ext_1"}]}
    (odir / AX.LOG_JSON).write_text(json.dumps(rec), encoding="utf-8")
    work = AX.work_findings(tmp_path)
    assert work[0]["evidence"]["image_sha256"] == old and work[0]["message"].count("Argus: ") == 1
    assert AX.seen_of({"evidence": {"image_sha256": old, "image_file": img.name}}) == {"image_sha256": old,
                                                                                       "image_file": img.name}
    events = []
    loop = LP.AgentLoop.__new__(LP.AgentLoop)
    loop.project_out, loop.rounds, loop.extra_findings = tmp_path, [], []
    loop.log = SimpleNamespace(event=lambda kind, round_no, **kw: events.append((kind, round_no, kw)))
    assert [f["check"] for f in loop.extra_work(4)] == ["V1"] and not events     # the same pixels: still work
    img.write_bytes(b"the house in daylight")                                   # re-rendered since
    assert loop.extra_work(5) == []
    kind, round_no, kw = events[0]
    assert kind == "check" and round_no == 5 and kw["check"] == CV.STALE_CHECK and kw["status"] == "dropped"
    assert kw["note"].startswith("stale:") and kw["target"] == "ext_1"
