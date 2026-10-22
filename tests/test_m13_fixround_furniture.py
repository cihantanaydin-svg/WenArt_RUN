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

Fix round after P4b (17 Oct 2026; the review of the P4a fix round, pod P4b, real03), every test of that section
fails on commit 11949a9:

- the mark lock lets a duplicate outline of the same family through (a seat segment of a corner sofa read as a
  sofa) and a plan crop as evidence; a top-down render is never recorded as the plan crop; the program adds nothing
  around such a duplicate and ``complete_group`` refuses a group the program does not complete;
- F1 lets a drawn washing machine stand in a hall; the solver keeps the open side of a drawn washer that faces a wall
  free; the chaise of a drawn corner sofa without its L goes to the side away from the drawn coffee table.

Pass before P5 (17 Oct 2026; the review of the fix round after P4b), every test of that kind fails on commit adc3004:

- the plan-crop way out of the mark lock takes only the piece's own recognition crop (its question's crop, or one
  recorded for its id in ``needs_review`` / ``conflicts``), never a room's camera plan crop or another symbol's crop;
  the refusal names no crop path pattern; the marked piece's symbol records its own crop.
"""
from __future__ import annotations

import copy
import json

import pytest
from shapely.geometry import Polygon

import _m11_room as M
import vc_toy as T
from wenart import views as V
from wenart.furniture import complete as C
from wenart.furniture import edit_ops as E
from wenart.furniture import groups as GR
from wenart.furniture import infer as INF
from wenart.furniture import locked as LK
from wenart.furniture import placer as P
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


# --------------------------------------------------------------------------
# Fix round after P4b: the mark lock, the plan crop, the program
# --------------------------------------------------------------------------

def _salon_l(twin: bool = False) -> dict:
    """real02's basement salon (P4a building_fitted.json): the drawn corner sofa f_L-1_053 (an L, chaise right) and
    the 1.30 m "sofa" f_L-1_061 the group-member rule typed, the seat segment of the corner sofa's block (84 % inside
    its box). ``twin``: the mirrored salon_2, whose L f_L-1_054 kept the same rotation (the reading lost its front),
    so its "sofa" f_L-1_062 stands in the L's open corner."""
    if twin:
        corner = M.fp("f_L-1_054", "sofa_corner", (3.0797, 3.2721), (4.3761, 1.9657), rotation=90.0, front=None,
                      status="unverified", type_method="none", shape="L", chaise_side="left")
        cx = 3.0797 + (12.8641 - 12.0934)
        pid = "f_L-1_062"
    else:
        corner = M.fp("f_L-1_053", "sofa_corner", (3.0797, 3.2721), (4.3761, 1.9657), rotation=90.0, front=None,
                      status="unverified", type_method="none", shape="L", chaise_side="right")
        cx, pid = 2.309, "f_L-1_061"
    sofa = M.fp(pid, "sofa", (cx, 3.1748), (1.3, 0.85), rotation=90.0, front=None, status="unverified",
                type_method="group_member" if not twin else "twin", inferred=True,
                drawn_footprint={"center": [cx, 3.1748], "size": [1.2958, 0.6314], "rotation_deg": 90.0})
    sofa["evidence"] = [{"file": "one_building.dwg", "method": "vector", "confidence": 0.9, "entity": "INSERT:365FB/0"}]
    return M.building(w=9.0, h=6.0, room_type="living", door_x=7.0, window=None, furniture=[corner, sofa])


SALON_F9 = {"check": "F9", "severity": "major", "message": "sofa overlaps sofa_corner by 0.83 m²"}


def test_mark_lock_lets_the_seat_segment_of_a_corner_sofa_through():
    """Fails on 11949a9 (review of the P4a fix round, major): ``_duplicate_of`` counted only a host of the identical
    type, so the lock refused marking real02's phantom sofa f_L-1_061 in every case (apply_edit, dry_run and
    allowed_edits) and the agent moved the drawn corner sofa instead."""
    for twin in (False, True):
        b = _salon_l(twin)
        pid = "f_L-1_062" if twin else "f_L-1_061"
        host = "f_L-1_054" if twin else "f_L-1_053"
        assert E.family_host_of(b, _by(b, pid)) == host and E._duplicate_of(b, _by(b, pid)) == host
        for fn in (E.apply_edit, E.dry_run):
            res = fn(b, edit("mark_not_furniture", piece_id=pid, kind="other",
                             target_finding=dict(SALON_F9, target=pid),
                             evidence=f"drawn inside the corner sofa {host}: the seat segment of its block"))
            assert res["accepted"], res["failed_checks"]
        assert E.allowed_edits(b, pid)["mark_not_furniture"]["allowed"] is True
    # the larger outline holds the duplicate, never the smaller one: an armchair inside a sofa is no host of it
    sofa = fp("s1", "sofa", (2.5, 0.6), (1.3, 0.85), 90.0, type_method="rule")
    chair = fp("a1", "armchair", (2.5, 0.6), (1.0, 1.0), 90.0, type_method="rule")
    b2 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[sofa, chair])
    assert E.family_host_of(b2, _by(b2, "a1")) == "s1" and E.family_host_of(b2, _by(b2, "s1")) is None
    # other families stay locked: a chair tucked under its table, a nightstand inside a bed block
    table = fp("t1", "table_dining", (2.5, 2.0), (1.6, 0.9), 90.0, type_method="rule")
    tucked = fp("c1", "chair", (2.5, 2.35), (0.45, 0.45), 90.0, type_method="rule")
    bed = fp("b1", "bed_double", (2.5, 2.97), (2.55, 2.0), 270.0, type_method="block_name")
    stand = fp("n1", "nightstand", (1.475, 3.745), (0.5, 0.45), 270.0, type_method="block_name")
    for room_type, items, pid in (("dining", [table, tucked], "c1"), ("bedroom", [bed, stand], "n1")):
        b3 = M.building(w=5.0, h=4.0, room_type=room_type, window=None, furniture=items)
        assert E._duplicate_of(b3, _by(b3, pid)) is None
        assert E.mark_lock_refusal(b3, _by(b3, pid), {"check": "F9"}) is not None
    # the P4a wardrobe with a 2 cm cut stays refused
    b4 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[_dolap()])
    assert E.mark_lock_refusal(b4, _by(b4, "f_L-1_024"), OUTLINE_F9, "plan crop r_L-1_salon: strip") is not None


def _round_table(pid="f_L1_015", key="sym_L1_001") -> dict:
    """P3 real04's f_L1_015: a drawn round coffee table typed by the group-member rule (vector ARC + CIRCLE) whose
    own question ``recognition:<key>`` the reading asked (the passes said unknown / potted_plant)."""
    t = fp(pid, "table_coffee", (2.5, 2.0), (1.027, 0.6932), 90.0, type_method="group_member", status="unverified")
    t["evidence"] = [{"file": "deneme1.dwg", "method": "vector", "confidence": 0.9, "entity": "ARC:36BA5,CIRCLE:36BA6"},
                     {"file": "deneme1.dwg", "method": "ai", "confidence": 0.85, "entity": f"recognition:{key}",
                      "pass": 1, "text": "unknown"}]
    return t


def _mark(b, pid, ev, target, fn=None):
    return (fn or E.apply_edit)(b, edit("mark_not_furniture", piece_id=pid, kind="dimension_outline", evidence=ev,
                                        target_finding=target))


def test_mark_lock_lifts_only_for_the_pieces_own_crop():
    """Fails on adc3004 (review of the fix round after P4b, major): any crop-like path lifted the lock, so a room's
    camera plan crop (the agent's evidence in P3 real04 seq 3282 / 3689 / 3692: "plan crop check/cam_r_L1_koridor_2_1_
    plan.jpg: ... it pokes through wall w_L1_006") or the crop of an unrelated symbol let a drawn, code-typed piece of
    a real size be marked as not furniture for a placement finding (P4a seq 647 again; P4a's real02 f_L1_021 and
    f_L-1_024). Only the piece's own recognition crop lifts it; top-down renders never do (P4a seq 264, 276, 331,
    350)."""
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[_dolap()])
    for ev in ("plan crop recognition/crops/sym_L-1_009_ctx.png: a 2.57 x 0.6 m strip, no cabinet doors",
               "plan crop recognition/crops/sym_L-1_024_ctx.png: strip",     # the symbol numbering is not the pieces'
               "plan crop check/cam_r_L-1_salon_1_plan.jpg shows a dimension strip",
               "top-down image r1_044_topdown_r_L-1_salon_2.png: a 5.54 x 0.60 m band along the top wall",
               "top-down r1_091_topdown_r_L1_teras.png: the chair straddles the wall",
               "plan crop r_L-1_salon: 2.57 x 0.6 m strip along the wall"):
        for target in (OUTLINE_F9, {"check": "S2", "target": "f_L-1_024"}):
            for fn in (E.apply_edit, E.dry_run):
                res = _mark(b, "f_L-1_024", ev, target, fn)
                assert not res["accepted"] and res["failed_checks"][0].startswith("drawn_lock: f_L-1_024"), (ev, fn)
                assert "its own recognition crop, when it has one" in res["failed_checks"][0]
                assert "<key>" not in res["failed_checks"][0] and "crops/" not in res["failed_checks"][0]
    assert E.own_crops(b, _by(b, "f_L-1_024")) == set()
    # P4a real02: the coffee table f_L1_021 (rule; drawn 1.52 x 0.60 m, snapped to 1.20 x 0.70 m) with the corridor's
    # camera plan crop and an F9 target stays refused
    table = fp("f_L1_021", "table_coffee", (2.5, 2.0), (1.2, 0.7), 90.0, type_method="rule",
               drawn_footprint={"center": [2.5, 2.0], "size": [1.52, 0.6], "rotation_deg": 90.0})
    b2 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[table])
    res = _mark(b2, "f_L1_021", "plan crop check/cam_r_L1_koridor_1_plan.jpg: a thin outline, not a built table",
                {"check": "F9", "target": "f_L1_021"})
    assert not res["accepted"] and res["failed_checks"][0].startswith("drawn_lock: f_L1_021")
    # the piece's own question crop (_ctx or _iso, in any crops/ folder) lifts the lock and is the symbol's crop, also
    # when a room crop comes first; another symbol's crop or a room crop alone does not
    b3 = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[_round_table()])
    assert E.mark_lock_refusal(b3, _by(b3, "f_L1_015"), {"check": "F9"}) is not None
    for ev, crop in (("plan crop recognition/crops/sym_L1_001_ctx.png: a round outline, a planter, no table",
                      "recognition/crops/sym_L1_001_ctx.png"),
                     ("plan crop recognition/L1/crops/sym_L1_001_iso.png: a round planter",
                      "recognition/L1/crops/sym_L1_001_iso.png"),
                     ("plan crop check/cam_r_L1_salon_1_plan.jpg and recognition/crops/sym_L1_001_ctx.png: a planter",
                      "recognition/crops/sym_L1_001_ctx.png")):
        for fn in (E.dry_run, E.apply_edit):
            res = _mark(b3, "f_L1_015", ev, {"check": "F9", "target": "f_L1_015"}, fn)
            assert res["accepted"], (ev, res["failed_checks"])
        assert res["building"]["symbols"][-1]["crop"] == crop
    for ev in ("plan crop recognition/crops/sym_L1_002_ctx.png: a planter",
               "plan crop recognition/crops/xsym_L1_001_ctx.png: a planter",
               "plan crop check/cam_r_L1_salon_1_plan.jpg: a planter",
               "plan crop sym_L1_001_ctx.png: a planter"):              # no crops/ folder: not a recognition crop
        res = _mark(b3, "f_L1_015", ev, {"check": "F9", "target": "f_L1_015"})
        assert not res["accepted"] and res["failed_checks"][0].startswith("drawn_lock: f_L1_015"), ev
    assert E.allowed_edits(b3, "f_L1_015")["mark_not_furniture"]["allowed"] is False
    assert E.own_crops(b3, _by(b3, "f_L1_015")) == {"sym_L1_001_ctx.png", "sym_L1_001_iso.png", "sym_L1_001.png"}


def test_own_crops_takes_a_recognition_crop_recorded_for_the_piece_and_never_a_room_crop():
    """Pass before P5: a recognition crop recorded for the piece's id in ``needs_review`` or ``conflicts`` is its own;
    a camera plan crop recorded there, or a crop recorded for another piece, is not."""
    piece = _dolap()
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[piece])
    b["conflicts"] = [{"kind": "symbol_front_disagreement", "element_ids": ["f_L-1_024"],
                       "crop": "recognition/crops/sym_L-1_007_ctx.png"},
                      {"kind": "other", "element_ids": ["f_L-1_024"], "crop": "check/cam_r_L-1_salon_1_plan.jpg"},
                      {"kind": "other", "element_ids": ["f_L-1_023"], "crop": "recognition/crops/sym_L-1_008_ctx.png"}]
    b["needs_review"] = [{"id": "f_L-1_023", "kind": "untyped_piece", "crop": "recognition/crops/sym_L-1_009_ctx.png"}]
    for ev in ("plan crop recognition/crops/sym_L-1_008_ctx.png: strip",
               "plan crop recognition/crops/sym_L-1_009_ctx.png: strip",
               "plan crop check/cam_r_L-1_salon_1_plan.jpg: strip"):
        assert E.mark_lock_refusal(b, piece, OUTLINE_F9, ev) is not None, ev
    assert E.mark_lock_refusal(b, piece, OUTLINE_F9, "plan crop recognition/crops/sym_L-1_007_ctx.png: strip") is None
    assert E.own_crops(b, piece) == {"sym_L-1_007_ctx.png"}


def test_crop_of_never_records_a_top_down_render_as_the_plan_crop():
    """Fails on 11949a9 (review of the P4a fix round, minor): ``crop_of`` took the first image of any kind, so P4a's
    symbols for f_L-1_022 and f_L-1b_001 recorded the agent's top-down renders as their plan crop."""
    assert E.crop_of("top-down image r1_044_topdown_r_L-1_salon_2.png: a 5.54 x 0.60 m band") is None
    assert E.crop_of("top-down images/r1_035_topdown_r_L-1b_salon_2.png: the 5.14 x 2.37 m outline") is None
    assert E.crop_of("before image r1_140_rotate_piece_before_r_L0_giris_holu_3.png") is None
    assert E.crop_of("plan crop recognition/crops/sym_L1_003_ctx.png: 1.63 x 1.52 m") == \
        "recognition/crops/sym_L1_003_ctx.png"
    assert E.crop_of("r1_091_topdown_x.png, plan crop recognition/crops/sym_L1_004_iso.png") == \
        "recognition/crops/sym_L1_004_iso.png"
    assert E.crop_of("crops/c1.png") == "crops/c1.png" and E.crop_of("no image") is None
    blob = M.fp("u1", "unknown", (2.5, 2.0), (1.63, 1.52), front=None, status="unverified")
    b = M.building(furniture=[blob])
    text = "top-down image r1_044_topdown_r_L-1_salon_2.png: a 5.54 x 0.60 m band along the top wall"
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="u1", kind="other", evidence=text))
    # Fix round after P5 (changed on purpose, tests/test_m13_p5_furniture.py): an untyped piece is marked only with
    # a plan crop; a top-down render is none, so the mark is refused instead of recording ``crop: null``
    assert not res["accepted"] and res["failed_checks"][0].startswith("no_crop: u1")
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="u1", kind="other",
                               evidence=text + "; plan crop check/cam_r_L-1_salon_2_1_plan.jpg"))
    assert res["accepted"], res["failed_checks"]
    sym = res["building"]["symbols"][0]
    assert sym["crop"] == "check/cam_r_L-1_salon_2_1_plan.jpg"
    assert "r1_044_topdown_r_L-1_salon_2.png" in sym["evidence"][0]["text"]


def test_the_program_adds_nothing_around_a_duplicate_outline():
    """Fails on 11949a9 (review of the P4a fix round): the code-typed phantom f_L-1_061 counted as a sure anchor, so
    its seating group was marked for a re-solve (a TV unit and a coffee table around a phantom sofa)."""
    b = _salon_l()
    entry = next(g for g in PR.room_program(b, ROOM)["groups"] if g["anchor_id"] == "f_L-1_061")
    assert entry["note"].startswith("duplicate outline: drawn inside the sofa_corner f_L-1_053")
    assert entry["missing"] == [] and not entry.get("resolve")
    assert PR.duplicate_anchor(b, _by(b, "f_L-1_061")) == "f_L-1_053"
    assert PR.duplicate_anchor(b, _by(b, "f_L-1_053")) is None
    group = next(g for g in GR.group_members(b, ROOM) if g["anchor_id"] == "f_L-1_061")
    if group.get("missing"):
        res = E.apply_edit(b, edit("complete_group", group_id=group["group_id"]))
        assert not res["accepted"] and res["failed_checks"][0].startswith("no_completion:")


# --------------------------------------------------------------------------
# Fix round after P4b: the drawn washing machines of real03's entrance halls
# --------------------------------------------------------------------------

def _wall(wid, a, c, t=0.1) -> dict:
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(c), "thickness": t, "exterior": False,
            "status": "verified", "evidence": []}


def _hall(washer_front: float = 0.0) -> dict:
    """real03's r_L0_giris_holu_3 (P4b building_fitted.json, moved by -28.1039, -7.5503): a hall that ends in a 0.45 m
    strip with the drawn washer f_L0_076 (block TEF - BANYO - ÇAMAŞIR MAKİNESİ) at its end, its drawn front towards the
    strip's east wall; the entrance door d_L0_007, two doors to other rooms and the window band win_L0_028."""
    washer = M.fp("f_L0_076", "washing_machine", (1.5169, 2.3002), (0.65, 0.6), rotation=(washer_front + 90.0) % 360,
                  front=washer_front, type_method="block_name")
    b = M.building(w=1.4196, h=1.9, room_type="hall", window=None, furniture=[washer])
    b["rooms"][0].update(polygon=[[0.0, 0.0], [1.4196, 0.0], [1.4196, 0.8202], [1.6483, 0.8202], [1.6483, 2.65],
                                  [1.2, 2.65], [1.2, 1.9], [0.0, 1.9]], area_computed=3.28, label="Giriş Holü",
                         label_raw="Giriş Holü")
    b["walls"] = [_wall("w_s", (0.0, -0.075), (1.6483, -0.075), 0.15), _wall("w_w", (-0.05, 0.0), (-0.05, 1.9)),
                  _wall("w_n", (0.0, 1.95), (1.2, 1.95)), _wall("w_e", (1.8058, 0.0), (1.8058, 2.65), 0.315),
                  _wall("w_n2", (1.2, 2.70), (1.6483, 2.70)), _wall("w_m", (1.25, 1.9), (1.25, 2.65)),
                  _wall("w_k", (1.4196, -0.075), (1.4196, 0.8202)), _wall("w_k2", (1.4196, 0.8202), (1.6483, 0.8202))]
    b["openings"] = [
        {"id": "d_007", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [0.6991, -0.075], "width": 0.9,
         "swing_side": ROOM, "status": "verified", "evidence": []},
        {"id": "d_008", "type": "door", "level_id": "L0", "wall_id": "w_w", "center": [-0.05, 1.1503], "width": 0.7,
         "swing_side": "r_other", "status": "verified", "evidence": []},
        {"id": "d_009", "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [0.5491, 1.95], "width": 0.8,
         "swing_side": "r_other_2", "status": "verified", "evidence": []},
        {"id": "win_028", "type": "window", "level_id": "L0", "wall_id": "w_e", "center": [1.8058, 1.3351],
         "width": 2.6298, "sill_height": 0.9, "status": "verified", "evidence": []}]
    return b


def test_f1_lets_a_drawn_washing_machine_stand_in_a_hall():
    """Fails on 11949a9 (P4b, agent lens, refuted: the verifier's better_fix 1): real03's 4 drawn hall washers got
    F1 (and G14) in every round; about 30 tool calls (set_room_type to bathroom, complete_group, fix_fixture) were
    spent on them. An added washer and other drawn fixed types keep F1; a stair room or a shaft never holds one."""
    def f1(b):
        return [(v["target"], v["severity"]) for v in PL.room_violations(b, b["rooms"][0]) if v["check"] == "F1"]

    assert f1(_hall()) == []
    added = _hall()
    added["furniture"][0]["source"] = "added_by_ai"
    assert [t for t, _s in f1(added)] == ["f_L0_076"]
    # a room that never holds a washer (schemas.misplaced_fixed: a stair room, a shaft) is no such room
    assert PL.drawn_anywhere(_hall()["furniture"][0], ["stair"]) is False
    assert PL.drawn_anywhere(_hall()["furniture"][0], ["shaft", "other"]) is False
    bedroom = M.building(w=4.0, h=4.0, room_type="bedroom", window=None,
                         furniture=[fp("t1", "toilet", (1.5, 3.6), (0.4, 0.7), 270.0)])
    assert [t for t, _s in f1(bedroom)] == ["t1"]
    assert PL.drawn_anywhere(_hall()["furniture"][0], ["hall", "other"]) is True


def test_complete_group_refuses_a_group_the_program_does_not_complete():
    """Fails on 11949a9 (P4b, the verifier's better_fix 3): complete_group on the bathroom set of a drawn hall washer
    ran the solver and was refused with "no place passes the checks" (3 halls), and the brief offered the tool."""
    b = _hall()
    group = next(g for g in GR.group_members(b, ROOM) if g["anchor_id"] == "f_L0_076")
    assert group["missing"]                                     # the set misses its toilet, washbasin and shower
    res = E.apply_edit(b, edit("complete_group", group_id=group["group_id"]))
    assert not res["accepted"]
    assert res["failed_checks"][0].startswith("no_completion:") and "does not belong in a hall room" in \
        res["failed_checks"][0]
    allowed = E.allowed_edits(b, "f_L0_076")["complete_group"]
    assert allowed["allowed"] is False and "completes nothing" in allowed["why"]


def test_a_drawn_washer_facing_a_wall_keeps_its_open_side_free():
    """Fails on 11949a9 (P4b, look lens, minor; not verified, checked here on the data): the completion put a 0.9 m
    console in the strip 0.11-0.26 m in front of the washers' only open side (real03's giris_holu_3 at x 1.48,
    y 0.84-1.74 here). The drawn front looks at the wall, so a front clearance in the table would not have helped."""
    b = _hall()
    zone_box = Polygon([(1.2169, 1.4452), (1.6483, 1.4452), (1.6483, 1.9752), (1.2169, 1.9752)])  # 0.53 m south
    for cand in SV.solve_room(b, ROOM, k=2):
        for q in cand["pieces"]:
            poly = P.drawn_piece(q).polygon()
            assert poly.intersection(zone_box).area < 1e-4, (q["type"], q["footprint"])
    room = b["rooms"][0]
    space = SV.Space(b, room, SV._fixed_items(b, ROOM, set()))
    acc = SV.access_zone(space, space.fixed_items[0], space.fixed_pieces[0])
    assert acc is not None and acc[0] == "access"
    poly = SV._zone_poly(acc)
    assert poly.within(space.ctx.polygon.buffer(1e-6)) and poly.bounds[3] <= 1.9752 + 1e-3
    assert any(z[0] == "access" for z in SV.fixed_zones(space))
    # a washer whose drawn front opens into the room keeps its own use zone only
    bath = M.building(w=2.5, h=2.0, room_type="bathroom", window=None,
                      furniture=[fp("w1", "washing_machine", (1.0, 1.7), (0.6, 0.6), 270.0)])
    sp = SV.Space(bath, bath["rooms"][0], SV._fixed_items(bath, ROOM, set()))
    assert SV.access_zone(sp, sp.fixed_items[0], sp.fixed_pieces[0]) is None
    # facing a wall with three open sides: the side is unclear, nothing is reserved
    free = M.building(w=3.0, h=3.0, room_type="other", window=None,
                      furniture=[fp("w2", "washing_machine", (1.5, 2.7), (0.6, 0.6), 90.0)])
    sp = SV.Space(free, free["rooms"][0], SV._fixed_items(free, ROOM, set()))
    assert SV.access_zone(sp, sp.fixed_items[0], sp.fixed_pieces[0]) is None


# --------------------------------------------------------------------------
# Fix round after P4b: the chaise side of a corner sofa typed by code
# --------------------------------------------------------------------------

def _yasama(table_y: float = 1.8581) -> dict:
    """real03's r_L0_yasama (P4b building.json): the corner sofa f_L0_190 typed by the group-member rule (no L) and
    its drawn coffee table f_L0_191; ``table_y`` 1.0843 mirrors the table to the sofa's other side (as in
    r_L0_yasama_4)."""
    sofa = M.fp("f_L0_190", "sofa_corner", (7.8788, 1.4712), (2.1, 1.5), rotation=90.0, front=0.0,
                status="unverified", type_method="group_member", inferred=True, height=0.85)
    table = M.fp("f_L0_191", "table_coffee", (8.7014, table_y), (0.8, 0.8), rotation=90.0, front=None,
                 status="unverified", type_method="group_member", inferred=True)
    return M.building(w=10.0, h=5.0, room_type="living", door_x=2.0, window=None, furniture=[sofa, table])


def test_the_chaise_of_a_code_typed_corner_sofa_leaves_its_drawn_coffee_table_free():
    """Fails on 11949a9 (P4b, look lens, refuted: the verifier's better_fix 2, the fallback part): f_L0_190 lost the
    drawn L (typed by code), the fit took a right-chaise model and the chaise covered the coffee table (S2 0.099 m,
    F9 0.26 m², in all 4 agent rounds). Pin: f_L0_190 left, f_L0_196 (yasama_4) right."""
    b = _yasama()
    props = INF.chaise_sides(b)
    assert [(p["piece_id"], p["chaise_side"]) for p in props] == [("f_L0_190", "left")]
    assert "f_L0_191" in props[0]["reason"] and props[0]["evidence"]["rule"] == INF.CHAISE_RULE
    # the table on the other side: the right chaise leaves it free (yasama_4's f_L0_196 kept right by luck)
    mirrored = _yasama(table_y=2 * 1.4712 - 1.8581)
    assert [(p["piece_id"], p["chaise_side"]) for p in INF.chaise_sides(mirrored)] == [("f_L0_190", "right")]
    # the drawing's own L wins; no table, no inference
    measured = _yasama()
    _by(measured, "f_L0_190").update(shape="L", chaise_side="right")
    assert INF.chaise_sides(measured) == []
    alone = _yasama()
    alone["furniture"] = alone["furniture"][:1]
    assert INF.chaise_sides(alone) == []
    # a small table between the two chaise places: either side leaves it free, the documents decide (nothing)
    middle = _yasama()
    _by(middle, "f_L0_191")["footprint"] = {"center": [8.4788, 1.4712], "size": [0.28, 0.28], "rotation_deg": 0.0}
    assert INF.chaise_sides(middle) == []
    # the completion writes it before the solver: shape L, the side, inferred with the evidence, a warning line
    out, _records = C.complete_building(b, "x", object(), C.Settings())
    sofa = _by(out, "f_L0_190")
    assert (sofa["shape"], sofa["chaise_side"], sofa["chaise_depth"]) == ("L", "left", 1.5)
    assert sofa["inferred"] is True and sofa["evidence"][-1]["rule"] == INF.CHAISE_RULE
    assert any(w.startswith("f_L0_190: inferred chaise on the left") for w in out["warnings"])
    assert LK.check(b, out, "complete") == []
    parts = P.drawn_piece(sofa).polygon()
    assert parts.intersection(P.drawn_piece(_by(out, "f_L0_191")).polygon()).area < 1e-6
    kept, _r = C.complete_building(b, "x", object(), C.Settings(mode="keep"))
    assert "shape" not in _by(kept, "f_L0_190")
