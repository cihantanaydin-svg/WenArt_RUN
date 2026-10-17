"""Fix round after P4a (17 Oct 2026; pod P4a, real02 with the M11 cameras replayed), track F_furniture.

Every test here fails on the code of commit 03881bc (or names the mutation it guards):

- F9: a sink built into its kitchen run (both sides) or a stove in its run's gap is no overlap; the "through the
  room outline" finding carries its depth;
- ``mark_not_furniture`` is a reading-error tool: a drawn, code-typed piece of a real size is never marked to clear
  a wall cut or a wrong-room finding; the crop is the first image path anywhere in the evidence;
- code typing: a group member type only when the group takes the piece in; a drawn lamp of a nightstand's size at
  a bed's head is its nightstand;
- a code-typed (unverified) drawn bed gets its nightstands; a re-solved drawn group places its drawn members at
  their own box;
- the JSON cross-check does not report a piece the scene built into its host.
"""
from __future__ import annotations

import copy
import json

import pytest

import _m11_room as M
import vc_toy as T
from wenart import views as V
from wenart.furniture import edit_ops as E
from wenart.furniture import groups as GR
from wenart.furniture import infer as INF
from wenart.furniture import locked as LK
from wenart.furniture import plausibility as PL
from wenart.furniture import program as PR
from wenart.furniture import solver as SV
from wenart.vision_check import expected as X

ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    """A drawn piece whose front is ``front`` (the footprint's local -Y)."""
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def edit(op, **args):
    return dict({"op": op, "reason": "test", "round": 1, "log_seq": 1, "model": "test"}, **args)


def f9(b) -> list[tuple[str, str]]:
    room = b["rooms"][0]
    return sorted((v["target"], str(v["metrics"].get("other"))) for v in PL.room_violations(b, room)
                  if v["check"] == "F9" and "overlaps" in v["message"])


# --------------------------------------------------------------------------
# F9: the pieces a kitchen run holds
# --------------------------------------------------------------------------

def _kitchen() -> dict:
    """The real02 L-1 kitchen pairs (P4a building_agent.json), moved 9 m south: counter f_L-1_002 with the stove
    f_L-1_008 in its gap, counter f_L-1_003 with the sink f_L-1_067 built in."""
    run1 = M.fp("f_L-1_002", "kitchen_counter", (1.3613, 2.501), (2.3213, 0.5999), rotation=0.0, front=270.0,
                asset={"method": "module", "module_plan": {"builder": "kitchen_run",
                                                           "gaps": [{"id": "f_L-1_008", "kind": "range"}]}})
    stove = M.fp("f_L-1_008", "stove", (1.5832, 2.4681), (0.75, 0.5491), rotation=0.0, front=270.0,
                 asset={"method": "library", "asset_id": "hssd_stove"})
    run2 = M.fp("f_L-1_003", "kitchen_counter", (0.5007, 1.2627), (1.8766, 0.6), rotation=90.0, front=0.0,
                asset={"method": "module", "module_plan": {"builder": "kitchen_run",
                                                           "built_ins": [{"id": "f_L-1_067", "kind": "sink"}]}})
    sink = M.fp("f_L-1_067", "sink_kitchen", (0.4507, 1.2601), (0.7885, 0.5), rotation=90.0, front=0.0,
                asset={"method": "module", "built_in": "f_L-1_003", "by_design": True,
                       "module_plan": {"builder": "kitchen_run", "built_into": "f_L-1_003", "kind": "sink"}})
    return M.building(w=4.0, h=2.81, room_type="kitchen", door_x=3.0, window=None,
                      furniture=[run1, stove, run2, sink])


def _by(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def test_f9_a_kitchen_run_holds_its_built_in_sink_and_the_stove_in_its_gap():
    """Fails on 03881bc: P4a logged 8 major F9 per round for the 4 built-in sinks and 4 stoves of the real02 kitchens
    (each overlap the whole drawn footprint, 0.41 and 0.39 m²) and the agent spent 8 swap_model edits on them."""
    b = _kitchen()
    assert f9(b) == []
    # (b) the sink's asset no longer names the run, though the run's plan lists it: F9 again (built_in_ids rule)
    lone = copy.deepcopy(b)
    _by(lone, "f_L-1_067")["asset"].pop("built_in")
    assert f9(lone) == [("f_L-1_067", "f_L-1_003")]
    other = copy.deepcopy(b)
    _by(other, "f_L-1_067")["asset"]["built_in"] = "f_L-1_002"
    assert f9(other) == [("f_L-1_067", "f_L-1_003")]
    # ... and a run plan refitted without the sink holds nothing
    refit = copy.deepcopy(b)
    _by(refit, "f_L-1_003")["asset"]["module_plan"]["built_ins"] = []
    assert f9(refit) == [("f_L-1_067", "f_L-1_003")]
    # (c) a stove the run's plan gives no gap is an overlap
    nogap = copy.deepcopy(b)
    _by(nogap, "f_L-1_002")["asset"]["module_plan"]["gaps"] = []
    assert f9(nogap) == [("f_L-1_008", "f_L-1_002")]
    # (d) the held stove still overlaps a piece that is not its run
    extra = copy.deepcopy(b)
    extra["furniture"].append(M.fp("f_fridge", "fridge", (1.9, 2.2), (0.6, 0.65), rotation=0.0, front=270.0))
    assert ("f_fridge", "f_L-1_008") in f9(extra)


def test_f9_outline_finding_carries_how_deep_the_piece_reaches_past_the_outline():
    """Fails on 03881bc (no ``depth_m``): P4a's wardrobe f_L-1_024 reached 0.05 m² through the outline, a 0.020 m cut
    along its 2.57 m back; the area alone read like a misplaced piece and the agent removed the drawn anchor."""
    wardrobe = fp("w1", "wardrobe", (2.5, 3.72), (2.5685, 0.6), 270.0)       # back 0.02 m into the north wall
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[wardrobe])
    found = [v for v in PL.room_violations(b, b["rooms"][0]) if v["check"] == "F9" and v["target"] == "w1"]
    assert len(found) == 1
    assert found[0]["metrics"]["outside_m2"] == pytest.approx(0.051, abs=0.002)
    assert found[0]["metrics"]["depth_m"] == pytest.approx(0.02, abs=1e-3)
    assert "0.020 m deep" in found[0]["message"]
    assert PL.outside_depth(PL.placer.drawn_piece(wardrobe).polygon(), PL._Room(b, b["rooms"][0]).polygon) == \
        pytest.approx(0.02, abs=1e-3)


# --------------------------------------------------------------------------
# mark_not_furniture: a reading-error tool
# --------------------------------------------------------------------------

def _dolap(pid="f_L-1_024", center=(2.5, 3.72), **kw) -> dict:
    """The seq 647 shape: a drawn block_name wardrobe (block dolap01, vector 0.9) 0.020 m through the wall."""
    w = fp(pid, "wardrobe", center, (2.5685, 0.6), 270.0, type_method="block_name", **kw)
    w["evidence"] = [{"file": "one_building.dwg", "method": "vector", "confidence": 0.9, "block": "dolap01",
                      "entity": "INSERT:dolap01"}]
    return w


OUTLINE_F9 = {"check": "F9", "target": "f_L-1_024", "severity": "major", "metrics": {"outside_m2": 0.052},
              "message": "wardrobe reaches 0.05 m² through the room outline"}


def test_mark_not_furniture_never_removes_a_drawn_code_typed_piece_for_a_cut():
    """Fails on 03881bc: P4a's agent marked the drawn wardrobe anchor f_L-1_024 (block dolap01, a 0.020 m wall cut),
    the vector chair f_L1_022 (0.58 x 0.45 m, "half through the wall") and the coffee table f_L1_021 as not furniture
    with text-only evidence; CLAUDE.md removes a drawn piece only when it is clearly not furniture."""
    chair = fp("f_L1_022", "chair", (4.0, 0.15), (0.58, 0.45), 90.0, type_method="rule")
    chair["evidence"] = [{"file": "one_building.dwg", "method": "vector", "confidence": 0.85}]
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[_dolap(), chair])
    for pid, target in (("f_L-1_024", OUTLINE_F9), ("f_L-1_024", {"check": "G14", "target": "f_L-1_024"}),
                        ("f_L-1_024", {"check": "S2"}), ("f_L-1_024", None), ("f_L1_022", {"check": "F9"})):
        for fn in (E.apply_edit, E.dry_run):
            args = {"target_finding": target} if target else {}
            res = fn(b, edit("mark_not_furniture", piece_id=pid, kind="dimension_outline",
                             evidence="plan crop r_L-1_salon: 2.57 x 0.6 m strip along the wall", **args))
            assert not res["accepted"] and res["building"] is None
            assert res["failed_checks"][0].startswith(f"drawn_lock: {pid}: a drawn ")
            assert "mark_not_furniture is for reading errors" in res["failed_checks"][0]
        allowed = E.allowed_edits(b, pid)["mark_not_furniture"]
        assert allowed["allowed"] is False and "reading errors" in allowed["why"]
    # the fit's size snap counts as a real size (P4a: f_L-1_024 drawn 0.74 m deep, snapped to 0.60 m)
    snapped = _dolap(drawn_footprint={"center": [2.5, 3.65], "size": [2.5685, 0.7427], "rotation_deg": 0.0})
    b2 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[snapped])
    assert E.mark_lock_refusal(b2, _by(b2, "f_L-1_024")) is not None


def test_mark_not_furniture_still_takes_the_reading_errors():
    """The guards of the lock: a duplicate outline (real04 seq 2123: wardrobe f_L0_038 drawn inside the run f_L0_026),
    an NR or RC finding, an untyped cluster, an AI-typed piece and a piece far outside its range may still be marked;
    misplaced fixed equipment keeps its own rule."""
    run = fp("f_L0_026", "wardrobe", (2.2454, 3.69), (2.0896, 0.6), 270.0, type_method="ai_two_pass")
    dup = _dolap("f_L0_038", center=(1.9273, 3.69))
    dup["footprint"]["size"] = [1.4533, 0.6]
    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[run, dup])
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="f_L0_038", kind="dimension_outline",
                               evidence="drawn directly inside f_L0_026", target_finding={"check": "F9"}))
    assert res["accepted"], res["failed_checks"]
    lone = _dolap()
    b2 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[lone])
    for target in ({"check": "NR"}, {"check": "RC"}):
        assert E.mark_lock_refusal(b2, lone, target) is None
    b2["conflicts"] = [{"kind": "type_disagreement", "element_ids": ["f_L-1_024"], "description": "x"}]
    assert E.mark_lock_refusal(b2, lone) is None
    b3 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[lone])
    b3["needs_review"] = [{"id": "f_L-1_024", "kind": "untyped_piece"}]
    assert E.mark_lock_refusal(b3, lone) is None
    for change in ({"type": "unknown"}, {"type_method": "ai_two_pass"}, {"type_method": None},
                   {"footprint": {"center": [2.5, 3.72], "size": [5.5427, 0.6012], "rotation_deg": 0.0}},
                   {"evidence": [{"file": "x.png", "method": "ai", "confidence": 0.9}]}):
        item = dict(lone, **change)
        assert E.mark_lock_refusal(M.building(room_type="living", furniture=[item]), item) is None, change


def test_mark_not_furniture_takes_the_crop_from_anywhere_in_the_evidence():
    """Fails on 03881bc: the crop was taken only when the evidence ended with an image path, so P4a's
    "recognition/crops/sym_L1_003_ctx.png: 1.63 x 1.52 m flat untyped outline" left ``crop: null``."""
    blob = M.fp("u1", "unknown", (2.5, 2.0), (1.63, 1.52), front=None, status="unverified")
    b = M.building(furniture=[blob])
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="u1", kind="other",
                               evidence="plan crop recognition/crops/sym_L1_003_ctx.png: 1.63 x 1.52 m flat outline"))
    assert res["accepted"], res["failed_checks"]
    sym = res["building"]["symbols"][0]
    assert sym["crop"] == "recognition/crops/sym_L1_003_ctx.png"
    assert sym["evidence"][0]["file"] == "recognition/crops/sym_L1_003_ctx.png"
    assert E.crop_of("no crop on disk") is None and E.crop_of("crops/c1.png") == "crops/c1.png"


# --------------------------------------------------------------------------
# Code typing: group members, nightstand symbols
# --------------------------------------------------------------------------

def _salon() -> dict:
    """A living room: a corner sofa with its coffee table at the west end, a second sofa at the east end without
    one, three untyped 0.59 m squares beside the corner sofa (P4a r_L-1_salon: 7 coffee tables)."""
    corner = fp("s1", "sofa_corner", (1.6, 0.5), (2.8, 0.9), 90.0, chaise_side="right")
    coffee = fp("c1", "table_coffee", (1.6, 1.6), (1.0, 0.6), 90.0)
    sofa2 = fp("s2", "sofa", (8.0, 0.5), (2.0, 0.9), 90.0)
    squares = [M.fp(f"u{k}", "unknown", (0.5 + 0.8 * k, 2.6), (0.59, 0.59), front=None, status="unverified")
               for k in range(3)]
    return M.building(w=9.0, h=5.0, room_type="living", door_x=5.0, window=None,
                      furniture=[corner, coffee, sofa2] + squares)


def _three_calls(b: dict) -> dict:
    for _ in range(3):                      # code_pass, infer_types and the completion each run the code typing
        b, _props = INF.apply_code_types(b)
    return b


def test_group_member_type_only_when_the_group_takes_the_piece_in():
    """Fails on 03881bc: every small square was 'the only missing member' of the far sofa's group, joined the corner
    sofa's group instead and left the coffee table missing for the next one: 3 coffee tables here (P4a: 7 in each
    basement salon, 2-3 in each L1 play room)."""
    b = _three_calls(_salon())
    typed = [f["id"] for f in b["furniture"] if f.get("type_method") == "group_member"]
    assert typed == []
    assert [g["missing"] for g in GR.group_members(b, ROOM) if g["anchor_id"] == "s2"] == [["tv_unit",
                                                                                            "table_coffee"]]
    # a square in front of the second sofa is its coffee table, and only one is
    near = _salon()
    near["furniture"] += [M.fp("u8", "unknown", (7.6, 1.75), (0.59, 0.59), front=None, status="unverified"),
                          M.fp("u9", "unknown", (8.4, 1.75), (0.59, 0.59), front=None, status="unverified")]
    b2 = _three_calls(near)
    typed2 = sorted((f["id"], f["type"]) for f in b2["furniture"] if f.get("type_method") == "group_member")
    assert typed2 == [("u8", "table_coffee")]
    assert [g["missing"] for g in GR.group_members(b2, ROOM) if g["anchor_id"] == "s2"] == [["tv_unit"]]


def _lamp(pid, center, key):
    lamp = fp(pid, "floor_lamp", center, (0.5, 0.45), 270.0, type_method="ai_two_pass")
    lamp["evidence"] = [{"file": "one_building.dwg", "method": "vector", "confidence": 0.9},
                        {"file": "one_building.dwg", "method": "ai", "confidence": 0.95, "entity": f"recognition:{key}",
                         "text": "floor_lamp"}]
    return lamp


def test_a_drawn_lamp_of_a_nightstand_size_at_the_bed_head_is_its_nightstand():
    """Fails on 03881bc: real02's YATAK blocks draw a nightstand with its table lamp on each side of the head; both
    VLMs answered floor_lamp, the lamps held the nightstand places and r_L0_e_yatak_odasi and _2 got none."""
    bed = fp("b1", "bed_double", (2.5, 2.97), (1.6, 2.0), 270.0, type_method="block_name")   # head on the north wall
    left = _lamp("l1", (1.43, 3.745), "sym_L0_013")
    right = _lamp("l2", (3.57, 3.745), "sym_L0_014")
    far = _lamp("l3", (4.6, 0.4), "sym_L0_015")                                               # a real floor lamp
    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed, left, right, far])
    props = [p for p in INF.infer_types(b) if p.get("type_method") == INF.NIGHTSTAND_METHOD]
    assert sorted((p["piece_id"], p["bed_id"]) for p in props) == [("l1", "b1"), ("l2", "b1")]
    out = INF.apply_inferences(b, props)
    ns = _by(out, "l1")
    assert ns["type"] == "nightstand" and ns["type_method"] == INF.NIGHTSTAND_METHOD and ns["inferred"] is True
    assert ns["drawn_type"] == "floor_lamp" and ns["drawn_footprint"] == left["footprint"]
    assert ns["adjusted_by_ai"]["by"] == "code" and ns["adjusted_by_ai"]["changed"]["type"] == "floor_lamp"
    assert ns["adjusted_by_ai"]["crop"] == "recognition/crops/sym_L0_013_ctx.png"
    assert "nightstand" in ns["adjusted_by_ai"]["reason"] and ns["front_deg"] == 270.0
    assert _by(out, "l3")["type"] == "floor_lamp"
    assert [g["member_ids"] for g in GR.group_members(out, ROOM) if g["anchor_id"] == "b1"] == [["l1", "l2"]]
    # a bed already with its nightstand on one side: only the other side's lamp
    stand = fp("n1", "nightstand", (1.43, 3.745), (0.5, 0.45), 270.0)
    b2 = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed, stand, right])
    assert [p["piece_id"] for p in INF.nightstand_symbols(b2)] == ["l2"]
    # a lamp at the foot of the bed or of another size stays a lamp
    foot = _lamp("l4", (1.43, 2.2), "k")
    big = _lamp("l5", (3.57, 3.745), "k")
    big["footprint"]["size"] = [0.8, 0.8]
    b3 = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed, foot, big])
    assert INF.nightstand_symbols(b3) == []


# --------------------------------------------------------------------------
# Program and solver: code-typed beds, drawn members at their own box
# --------------------------------------------------------------------------

def _code_bed(method="group_member") -> dict:
    bed = fp("b1", "bed_double", (2.5, 2.97), (1.6, 2.0), 270.0, status="unverified", type_method=method,
             inferred=True)
    return M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed])


def test_a_code_typed_unverified_bed_gets_its_nightstands():
    """Fails on 03881bc: code typing keeps ``status: unverified``; real02's beds f_L0_019-022 (typed "the bedroom
    misses its bed" and by their twins) got "unverified anchor: nothing added" and the solver used no unverified
    drawn anchor, so four bedrooms had no nightstands (m5 bedroom 2/8)."""
    b = _code_bed()
    entry = next(g for g in PR.room_program(b, ROOM)["groups"] if g["anchor_id"] == "b1")
    assert entry["missing"] == ["nightstand", "nightstand"] and not entry["note"].startswith("unverified")
    best = SV.solve_room(b, ROOM, k=1)[0]
    assert [p["type"] for p in best["pieces"]].count("nightstand") == 2, best["not_placed"]
    assert PR.unsure_anchor(_by(b, "b1")) is False
    # a bed the two AI passes could not agree on stays unsure: nothing is added around it
    ai = _code_bed(method="ai_disagreement")
    entry = next(g for g in PR.room_program(ai, ROOM)["groups"] if g["anchor_id"] == "b1")
    assert entry["missing"] == [] and entry["note"] == "unverified anchor: nothing added"
    assert PR.unsure_anchor(_by(ai, "b1")) is True
    no_vector = _code_bed()
    _by(no_vector, "b1")["evidence"] = [{"file": "x.png", "method": "ai", "confidence": 0.6}]
    assert PR.unsure_anchor(_by(no_vector, "b1")) is True
    # a type proposal of the completion stays a proposal (tests/test_complete.py: nothing added beside it)
    proposal = _code_bed()
    _by(proposal, "b1")["type_proposal"] = True
    assert PR.unsure_anchor(_by(proposal, "b1")) is True


def test_a_re_solved_bed_block_keeps_its_drawn_nightstands_at_their_own_size():
    """Fails on 03881bc: the drawn members of a re-solved group took places searched at the template's sizes; a
    0.45 m deep drawn nightstand on a place made for a 0.40 m one reached into the headboard wall, so the misread
    2.55 m bed block with its two nightstands (real02 YATAK) got no candidate and stayed as drawn."""
    block = fp("b1", "bed_double", (2.5, 2.97), (2.55, 2.0), 270.0)                       # bed + nightstands, misread
    left = fp("n1", "nightstand", (1.475, 3.745), (0.5, 0.45), 270.0)
    right = fp("n2", "nightstand", (3.525, 3.745), (0.5, 0.45), 270.0)
    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[block, left, right])
    entry = next(g for g in PR.room_program(b, ROOM)["groups"] if g["anchor_id"] == "b1")
    assert entry.get("resolve") and sorted(entry["resolve"]["members"]) == ["n1", "n2"]
    best = SV.solve_room(b, ROOM, k=1)[0]
    assert sorted(best["resolved"]) == ["b1", "n1", "n2"], best["not_placed"]
    placed = {p["id"]: p for p in best["pieces"]}
    assert placed["b1"]["footprint"]["size"][0] < 2.1                                   # a real bed width
    for nid in ("n1", "n2"):
        assert sorted(placed[nid]["footprint"]["size"]) == [0.45, 0.5]
        assert placed[nid]["drawn_group"]["anchor_id"] == "b1"
    members = {"members": [(left, "nightstand"), (right, "nightstand"), (block, "anchor")]}
    assert SV._member_boxes(members, "nightstand") == [(0.5, 0.45)]


# --------------------------------------------------------------------------
# The JSON cross-check and a piece built into its host
# --------------------------------------------------------------------------

def _toy(tmp_path):
    out = T.write_toy_project(tmp_path)
    view = V.load_views(out / "renders")[T.CAMERA["name"]]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    sofa = _by(building, "f_sofa")
    sink = {"id": "f_sink", "level_id": sofa["level_id"], "room_id": sofa.get("room_id"), "type": "sink_kitchen",
            "source": "from_documents", "status": "verified",
            "footprint": {"center": [2.5, 0.55], "size": [0.8, 0.9], "rotation_deg": 0.0},
            "front_deg": sofa.get("front_deg"), "height": 0.9, "asset": {"method": "module", "built_in": "f_sofa"}}
    building["furniture"].append(sink)
    return view, scene, building


def test_crosscheck_does_not_report_a_piece_the_scene_built_into_its_host(tmp_path):
    """Fails on 03881bc: P4a reported the built-in sink f_L-1_067 as in_json_not_rendered in all three mutfak views
    (metric 14) although the scene built it into its run (scene manifest ``furniture.built_in``)."""
    view, scene, building = _toy(tmp_path)
    cc = X.expected_view(view, scene, building)["json_crosscheck"]
    assert "f_sink" in [x["id"] for x in cc["in_json_not_rendered"]]          # no scene record: still reported
    built = copy.deepcopy(scene)
    built.setdefault("furniture", {})["built_in"] = [{"id": "f_sink", "type": "sink_kitchen", "host": "f_sofa",
                                                      "reason": "built into its kitchen run"}]
    cc = X.expected_view(view, built, building)["json_crosscheck"]
    assert cc["in_json_not_rendered"] == [] and cc["misplaced"] == []
    assert "f_sink" not in cc["projected"]


def test_crosscheck_still_reports_a_missing_host(tmp_path):
    out = T.write_toy_project(tmp_path, drop=("f_sofa",))
    view = V.load_views(out / "renders")[T.CAMERA["name"]]
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    building = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    scene.setdefault("furniture", {})["built_in"] = [{"id": "f_sink", "type": "sink_kitchen", "host": "f_sofa"}]
    cc = X.expected_view(view, scene, building)["json_crosscheck"]
    assert "f_sofa" in [x["id"] for x in cc["in_json_not_rendered"]]
