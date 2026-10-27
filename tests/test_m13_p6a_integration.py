"""Fix round after P6a, part I1 (22-23 Oct 2026; pod P6a, real04): the agent, edit and fit side of the round's asks.

Checked, each against BASE 52d4bb8 (the tests fail there: a missing helper or keyword, or the old verdict) or a
mutation named in its docstring:

1. the fit keeps a library model ``fit.CEILING_MARGIN_M`` under the sloped ceiling over its piece (``fit.fit_piece``
   / ``fit_building`` with ``fit.piece_ceiling``; the decor track's ask, verify:agent:4 part 2), and the agent's refits
   (``edit_ops._build_retyped``, the swap check, ``loop.dry_fit``) pass the same ceiling;
2. ``swap_model`` refuses a generated model the refit refuses (P6a seq 6069 / 6075 / 6076);
3. ``mark_not_furniture`` marks an untyped piece only with its own crop (P6a seq 5968: a whole sheet);
4. ``change_type`` reads the room's types with their aliases (P6a seq 6008 / 6014: an ``other`` room aliased living);
5. an exterior ``set_camera`` / ``add_camera`` has its X6 measured on the scene the next build makes (P6a seq 6668:
   ext_front_entrance counted "no frontal view" as gone);
6. a vision X3 / X6 claim on an exterior view the agent placed goes to that camera (P6a seq 6856: dropped "facade");
7. ``free_strip_hint`` names a free stretch only where an eye-level view fits, and the camera-role guards read X6's
   frontal view with its frame measured (the exterior track's asks);
8. the scheduler rewrites the agent stage's note after the final round (P6a: "net 32" against metrics.json's 34);
9. two overlapping drawn lamp symbols are one lamp (``infer.duplicate_symbols``; real04's salons);
10. metric 12 names an agent exterior view that frames only part of the building or no sky.

The committed real04 buildings (results/furniture/real04) carry the L1 mansard roof and the copy b2 in front of the
entrance facade; the P6a / P5 run folders (``runs/...``, not in git) are used only by the tests marked ``needs_p6a``.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

import _m11_room as M
import test_run_agent as TRA
from test_agent_helpers import FakeEdits, write_json
from test_agent_loop_p4a import make
from test_m13_agent import FINISH, log_of
from wenart.agent import causes as CS
from wenart.agent import critic_code as CC
from wenart.agent import critic_vision as CV
from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import model as MM
from wenart.agent import overrides as OV
from wenart.agent import tools as TL
from wenart.blender import exterior_checks as X
from wenart.furniture import decor as D
from wenart.furniture import edit_ops as E
from wenart.furniture import fit as F
from wenart.furniture import infer as INF
from wenart.furniture import schemas
from wenart.furniture import solver as SV

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04"
P6A = ROOT / "runs" / "20261022-135644-m13_p6" / "results"
models = TRA.models             # the orchestrated run's fixture (pytest finds it by name)
needs_real04 = pytest.mark.skipif(not (REAL04 / "building_furnished.json").is_file(),
                                  reason="results/furniture/real04 not committed")
needs_p6a = pytest.mark.skipif(not (P6A / "furniture" / "real04" / "building_agent.json").is_file(),
                               reason="the P6a run folder runs/20261022-135644-m13_p6 is not on this machine")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(b: dict, pid: str) -> dict:
    return next(f for f in b["furniture"] if f["id"] == pid)


@pytest.fixture(scope="module")
def catalog():
    from wenart.furniture import catalog as C

    return C.load()


@pytest.fixture(scope="module")
def furnished():
    return read(REAL04 / "building_furnished.json")


def edit(op, **args):
    return dict({"op": op, "reason": "test", "round": 1, "log_seq": 1, "model": "mock"}, **args)


# --------------------------------------------------------------------------
# 1. the fit's ceiling cap under the sloped roof
# --------------------------------------------------------------------------

@needs_real04
def test_piece_ceiling_reads_the_roof_as_the_decor_and_the_solver_do(furnished):
    """``fit.piece_ceiling`` is ``decor.ceiling_over`` with the level's ``decor.ceiling_planes`` (the committed
    building carries no ``level["ceiling_planes"]``), less a wall cabinet's mount height; None on a flat level. The
    fit's margin is the solver's headroom margin (one rule)."""
    assert not any(lv.get("ceiling_planes") for lv in furnished["levels"])
    console = by_id(furnished, "f_L1_045")                     # the console table the completion put at the knee wall
    fp = console["footprint"]
    over = D.ceiling_over(furnished, "L1", fp["center"], fp["size"], fp["rotation_deg"])
    assert F.piece_ceiling(furnished, console) == pytest.approx(over) == pytest.approx(0.8212, abs=1e-3)
    cabinet = dict(console, type="wall_cabinet")
    assert F.piece_ceiling(furnished, cabinet) == pytest.approx(over - 1.45, abs=1e-4)
    flat = next(f for f in furnished["furniture"] if f.get("level_id") == "L0")
    assert F.piece_ceiling(furnished, flat) is None and F.piece_ceiling(None, console) is None
    assert F.CEILING_MARGIN_M == SV.HEADROOM_MARGIN_M
    # one rule: the fit's planes (no decor import in the fit stage's code) are the decor's and the solver's
    for level in ("L-1", "L0", "L1"):
        assert F.ceiling_planes_of(furnished, level) == D.ceiling_planes(furnished, level) == \
            SV.headroom_planes(furnished, level)
    assert F.ceiling_planes_of(furnished, "L1") and not F.ceiling_planes_of(furnished, "L0")
    for p in furnished["furniture"]:
        if p.get("level_id") == "L1" and p.get("type") not in schemas.MOUNTED_TYPES:
            fp = p["footprint"]
            over = D.ceiling_over(furnished, "L1", fp["center"], fp["size"], fp["rotation_deg"])
            assert F._slope_ceiling(furnished, p) == pytest.approx(over, abs=1e-4), p["id"]
            # 27 Oct 2026: a window's sill may cap a piece in front of it lower still (fit.window_cap)
            assert F.piece_ceiling(furnished, p) <= over + 1e-4, p["id"]
    assert F.under_ceiling(0.77, 0.8212) and not F.under_ceiling(0.84, 0.8212) and F.under_ceiling(9.0, None)


@needs_real04
def test_the_fit_keeps_a_library_model_under_the_sloped_ceiling(furnished, catalog, monkeypatch):
    """Fails on BASE: the fit had no ceiling input, so the console table under the 0.82 m slope took the 0.84 m
    abo_B07GZY278M (P6a's critical X2 through the roof); the twin bookshelf of P6a took a 2.02 m model under a 1.44 m
    slope. Now every library model under the roof stays 0.05 m under the ceiling over its piece; with no model under
    the cap the ladder's module or parametric piece names the slope."""
    console = by_id(furnished, "f_L1_045")
    ceiling = F.piece_ceiling(furnished, console)
    free = F.fit_piece(dict(console, build=True), catalog, mode="relaxed", style_family="modern")
    capped = F.fit_piece(dict(console, build=True), catalog, mode="relaxed", style_family="modern", ceiling=ceiling)
    assert free["method"] == "library" and free["bbox_m"][2] > ceiling - F.CEILING_MARGIN_M
    assert capped["method"] == "library" and capped["bbox_m"][2] <= ceiling - F.CEILING_MARGIN_M + 1e-9
    assert any(t.get("under_ceiling") is False for t in capped["candidates"])
    low = F.fit_piece(dict(console, build=True), catalog, mode="relaxed", style_family="modern", ceiling=0.3)
    assert low["method"] in ("module", "parametric")
    assert "the sloped ceiling leaves over the piece (0.30 m - 0.05 m)" in low["library_gap"]["reason"]
    # a pin taller than the slope is refused with the reason
    pinned = F.fit_piece(dict(console, build=True, asset_pin=free["asset_id"]), catalog, mode="relaxed",
                         style_family="modern", ceiling=ceiling)
    assert pinned["pin_refused"].startswith(f"{free['asset_id']}: fails the fit rules (caps, height, at most 0.77 m "
                                            f"high under the sloped ceiling)")
    # fit_building passes the cap per piece: no library model under the roof reaches the slope
    fitted = F.fit_building(furnished, catalog, mode="relaxed", style_family="modern")
    under = [(p["id"], p["asset"]["bbox_m"][2], F.piece_ceiling(fitted, p)) for p in fitted["furniture"]
             if (p.get("asset") or {}).get("method") == "library" and F.piece_ceiling(fitted, p) is not None]
    assert under and all(h <= c - F.CEILING_MARGIN_M + 1e-9 for _pid, h, c in under), under
    assert by_id(fitted, "f_L1_045")["asset"]["asset_id"] == capped["asset_id"]
    # mutation: no ceiling per piece -> the 0.84 m console again (what this test catches)
    monkeypatch.setattr(F, "piece_ceiling", lambda building, piece, planes=None: None)
    again = F.fit_building(furnished, catalog, mode="relaxed", style_family="modern")
    assert by_id(again, "f_L1_045")["asset"]["bbox_m"][2] == pytest.approx(free["bbox_m"][2])


@needs_real04
def test_the_agents_refits_pass_the_pieces_ceiling(furnished, monkeypatch, tmp_path):
    """Fails on BASE (no ``ceiling`` keyword): the retype refit (``edit_ops._build_retyped``), the generated-pin check
    of ``swap_model`` and the dry re-check's ``loop.dry_fit`` fit a piece under the slope with its ceiling, as
    ``fit_building`` does (the decor track's ask: edit_ops ~line 1252, loop ~line 1358)."""
    seen = []
    real = F.fit_piece

    def spy(piece, catalog, *a, **kw):
        seen.append((piece.get("id"), kw.get("ceiling")))
        return real(piece, catalog, *a, **kw)

    monkeypatch.setattr(F, "fit_piece", spy)

    class Cat:                                   # one generated fridge model: the swap check fits it
        def entry(self, asset_id):
            return {"id": asset_id, "type": "console_table", "source": F.GENERATED}

        def candidates(self, ftype):
            return []

        parametric_types = ()

    b = copy.deepcopy(furnished)
    console = by_id(b, "f_L1_045")
    want = F.piece_ceiling(b, console)
    E._build_retyped(b, console, {"type": "console_table", "reason": "x"}, Cat())
    E.generated_pin_refusal(b, console, "gen_console_1", Cat().entry("gen_console_1"), Cat())
    out = tmp_path / "p"
    write_json(out / "building_decor.json", b)
    loop = LP.AgentLoop(out, MM.MockModel(), out=lambda s: None)
    ctx = TL.ToolContext(project_out=out, building=b, catalog_loader=Cat)
    loop.dry_fit(ctx, console, b)
    calls = [c for pid, c in seen if pid == "f_L1_045"]
    assert len(calls) >= 3 and all(c == pytest.approx(want) for c in calls), seen


# --------------------------------------------------------------------------
# 2. swap_model: a generated model the refit refuses
# --------------------------------------------------------------------------

def _kitchen_with_fridge(real_id: str) -> dict:
    fridge = M.fp("f1", "fridge", (0.35, 3.6), (0.6, 0.65), rotation=180.0, status="verified",
                  asset={"method": "library", "asset_id": real_id, "style_family": "modern"})
    b = M.building(room_type="kitchen", furniture=[fridge])
    b["project"] = {"name": "m11", "licence_mode": "relaxed"}
    return b


def test_swap_model_refuses_a_generated_model_the_refit_refuses(catalog):
    """Fails on BASE (accepted): P6a seq 6069 pinned gen_fridge_classic_3 on the fridge f_L-1_090 (0.6 x 0.65 m); the
    refit refused the pin ("a generated model (units guessed) while a real product of the type fits") and built the
    real model, while the edit was accepted and its vision finding counted as removed. A real model the fit takes is
    still pinned."""
    piece = M.fp("f1", "fridge", (0.35, 3.6), (0.6, 0.65), rotation=180.0)
    ranked = F.fit_piece(dict(piece, build=True), catalog, mode="relaxed", style_family="modern")
    gen = next(e["id"] for e in catalog.candidates("fridge") if e.get("source") == F.GENERATED)
    b = _kitchen_with_fridge(ranked["asset_id"])
    res = E.apply_edit(b, edit("swap_model", piece_id="f1", asset_id=gen), catalog=catalog)
    assert not res["accepted"] and res["building"] is None
    why = res["failed_checks"][0]
    assert why.startswith(f"pin_refused: f1: {gen}: a generated model (units guessed) while a real product of the "
                          f"type fits within the caps") and why.endswith("the real model stays; swap to a real model "
                                                                          "of the type or use another tool"), why
    pinnable = [e["id"] for e in catalog.candidates("fridge") if e.get("source") != F.GENERATED
                and e["id"] != ranked["asset_id"] and F.fit_piece(dict(piece, asset_pin=e["id"]), catalog,
                                                                  mode="relaxed", style_family="modern").get("pinned")]
    # 27 Oct 2026: a swap never takes a lower-rated model (edit_ops.lower_quality_refusal): from one pinnable model to
    # another of its rating
    rated = {}
    for i in pinnable:
        rated.setdefault(E.model_rating(catalog.entry(i)), []).append(i)
    first, other = next(v for v in rated.values() if len(v) >= 2)[:2]
    b = _kitchen_with_fridge(first)
    ok = E.apply_edit(b, edit("swap_model", piece_id="f1", asset_id=other), catalog=catalog)
    assert ok["accepted"], ok["failed_checks"]
    assert by_id(ok["building"], "f1")["asset_pin"] == other


@needs_p6a
def test_p6a_phantom_swaps_are_refused_at_validation(catalog):
    """P6a's three accepted swaps (seq 6069 / 6075 / 6076) on the P6a building before the agent (building_decor.json,
    in the refit's licence mode): each is refused now."""
    b = read(P6A / "furniture" / "real04" / "building_decor.json")
    final = read(P6A / "furniture" / "real04" / "building_final.json")
    b["project"] = dict(b.get("project") or {}, licence_mode=(final.get("project") or {}).get("licence_mode"))
    for pid, gen in (("f_L-1_090", "gen_fridge_classic_3_25281fe9"), ("f_L0_003", "gen_washbasin_modern_1_833baa60"),
                     ("f_L0_016", "gen_toilet_japandi_1_42fdb46f")):
        if catalog.entry(gen) is None:
            pytest.skip(f"{gen} is not in this catalogue")
        res = E.dry_run(b, edit("swap_model", piece_id=pid, asset_id=gen), catalog=catalog)
        assert not res["accepted"] and res["failed_checks"][0].startswith(f"pin_refused: {pid}: {gen}: "), \
            (pid, res["failed_checks"])


# --------------------------------------------------------------------------
# 3. mark_not_furniture: an untyped piece only with its own crop
# --------------------------------------------------------------------------

def _untyped(question: str | None = None) -> dict:
    blob = M.fp("u1", "unknown", (2.5, 2.0), (1.63, 1.52), front=None, status="unverified")
    if question:
        blob["evidence"].append({"file": "deneme.dwg", "method": "ai", "entity": f"recognition:{question}",
                                 "confidence": 0.5, "text": "unknown"})
    return M.building(furniture=[blob])


def test_an_untyped_piece_is_marked_only_with_its_own_crop():
    """Fails on BASE (accepted): P6a seq 5968 marked the untyped 5.14 x 2.37 m cluster f_L-1b_002 (no question, no
    crop) as not furniture with the whole sheet ``final/debug/deneme1_dwg_s1.jpg``; a room's camera crop or another
    symbol's crop was taken the same way. Its own question's crop or the crop its review entry records is taken; a
    typed piece keeps the old rule."""
    b = _untyped()
    for evidence in ("final/debug/deneme1_dwg_s1.jpg", "plan crop check/cam_r_L0_oda_1_plan.jpg",
                     "recognition/crops/sym_L0_009_ctx.png: an outline"):
        res = E.apply_edit(b, edit("mark_not_furniture", piece_id="u1", kind="dimension_outline", evidence=evidence))
        assert not res["accepted"], evidence
        why = res["failed_checks"][0]
        assert why.startswith("no_crop: u1 is an untyped drawn piece: it is marked as not furniture only with its own "
                              "recognition crop") and "it has none, so it stays listed for review" in why, why
        assert "is not its crop" in why
    own = _untyped("sym_L0_009")
    ok = E.apply_edit(own, edit("mark_not_furniture", piece_id="u1", kind="dimension_outline",
                                evidence="recognition/crops/sym_L0_009_ctx.png: an outline"))
    assert ok["accepted"], ok["failed_checks"]
    assert ok["building"]["symbols"][0]["crop"] == "recognition/crops/sym_L0_009_ctx.png"
    no_named = E.apply_edit(own, edit("mark_not_furniture", piece_id="u1", kind="other", evidence="an outline"))
    assert not no_named["accepted"] and "it has none" not in no_named["failed_checks"][0]
    recorded = _untyped()
    recorded["needs_review"] = [{"id": "u1", "kind": "untyped_piece", "crop": "recognition/crops/sym_L0_010_ctx.png"}]
    ok2 = E.apply_edit(recorded, edit("mark_not_furniture", piece_id="u1", kind="other", evidence="final/debug/x.jpg"))
    assert ok2["accepted"] and ok2["building"]["symbols"][0]["crop"] == "recognition/crops/sym_L0_010_ctx.png"
    # a typed piece outside the mark lock (an AI-typed outline): the camera crop is still its evidence, as before
    typed = M.building(furniture=[M.fp("s1", "sofa", (2.5, 2.0), (1.63, 1.52), status="unverified",
                                       type_method="ai_two_pass")])
    ok3 = E.apply_edit(typed, edit("mark_not_furniture", piece_id="s1", kind="other",
                                   evidence="plan crop check/cam_r_L0_oda_1_plan.jpg: a rug outline"))
    assert ok3["accepted"], ok3["failed_checks"]
    assert ok3["building"]["symbols"][0]["crop"] == "check/cam_r_L0_oda_1_plan.jpg"


@needs_p6a
def test_p6a_seq_5968_is_refused():
    b = read(P6A / "furniture" / "real04" / "building_decor.json")
    res = E.dry_run(b, edit("mark_not_furniture", piece_id="f_L-1b_002", kind="dimension_outline",
                            evidence="final/debug/deneme1_dwg_s1.jpg"))
    assert not res["accepted"] and res["failed_checks"][0].startswith("no_crop: f_L-1b_002 is an untyped drawn piece")


# --------------------------------------------------------------------------
# 4. change_type: the room's alias types
# --------------------------------------------------------------------------

@needs_real04
def test_change_type_reads_the_rooms_alias_types(furnished):
    """Fails on BASE: real04's play rooms are ``other`` rooms aliased living (``plausibility.room_types``); retype_piece
    offered console_table and sideboard for the drawn bench f_L1_035 (``group_checks.allowed_types_at`` reads the
    alias) and change_type refused them "not a piece a other room may hold" (P6a seq 6008 / 6014)."""
    room = next(r for r in furnished["rooms"] if r["id"] == "r_L1_oyun_aktivite_ve_dinlenme_odasi")
    assert room["room_type"] == "other" and E.room_types_of(furnished, room) == ["other", "living"]
    drawn = E.room_allowed(furnished, room, schemas.change_types)
    assert {"console_table", "sideboard", "tv_unit"} <= drawn and not drawn & set(schemas.UNCHANGEABLE_TYPES)
    assert "console_table" not in schemas.change_types("other")
    b = copy.deepcopy(furnished)
    bench = M.fp("f_t1", "bench", (5.6, 7.2), (1.4, 0.42), rotation=0.0)
    bench.update(level_id="L1", room_id=room["id"])
    b["furniture"].append(bench)
    res = E.dry_run(b, edit("change_type", piece_id="f_t1", type="console_table"))
    assert not any(c.startswith("room_type") for c in res["failed_checks"]), res["failed_checks"]
    res = E.dry_run(b, edit("change_type", piece_id="f_t1", type="bed_double"))
    assert res["failed_checks"][0] == "room_type: bed_double is not a piece a other (other / living) room may hold here"


# --------------------------------------------------------------------------
# 5. the X6 of an exterior camera edit is measured on the trial scene
# --------------------------------------------------------------------------

P3_EXT = [
    {"name": "ext_1", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["left", "front"],
     "position": [-5.8495, -11.6912, -2.5414], "target": [2.5802, -1.1466, -2.5414], "lens_mm": 26.0},
    {"name": "ext_2", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["right", "front"],
     "position": [23.0225, -11.6912, -0.7169], "target": [14.5926, -1.1468, -0.7169], "lens_mm": 26.0},
    {"name": "ext_4", "kind": "exterior", "room_id": None, "view": "corner", "sides": ["left", "back"],
     "position": [-5.8495, 23.6914, 0.0517], "target": [2.5815, 13.1478, 0.0517], "lens_mm": 26.0},
]
MAIN_Y = {"axis": "+y", "direction": [0.0, 1.0], "source": "entrance doors"}


def real04_ctx(tmp_path: Path, cameras=P3_EXT):
    out = tmp_path / "real04"
    out.mkdir(parents=True)
    (out / "building_decor.json").write_bytes((REAL04 / "building_decor.json").read_bytes())
    write_json(out / "scene" / "scene_manifest.json", {"cameras": copy.deepcopy(list(cameras)),
                                                       "whole_building": {"main_facade": MAIN_Y}})
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=LG.AgentLog(out, "real04", "m", "r"),
                               overrides=OV.Overrides(out), apply_edit=FakeEdits())


def strip_pose(b: dict, pitch_deg: float = 10.0) -> dict:
    """A 26 mm eye-level pose in real04's strip between the entrance facade (y 12) and b2, pitched up: it has sky
    (11 %) so the validator takes it, and it frames 2.34 widths of the facade (P6a's ext_front_entrance place)."""
    z = round(CV.ground_z(b, None, 8.5, 17.5) + 1.6, 4)
    return {"view_id": "ext_front_entrance", "kind": "exterior", "room_id": None, "position": [8.5, 17.5, z],
            "target": [8.5, 12.5, round(z + 5.0 * math.tan(math.radians(pitch_deg)), 3)], "lens_mm": 26,
            "reason": "frontal view of the entrance facade"}


@needs_real04
def test_an_exterior_camera_edit_has_its_x6_measured_on_the_next_scene(tmp_path):
    """Fails on BASE (accepted, "X6:exterior gone"): X6 is in ``loop.NOT_REMEASURED``, so P6a's add_camera
    ext_front_entrance (seq 6668) counted "no frontal view of the entrance (+y) facade" as removed. Now the dry
    re-check measures X6 on the scene the next build makes with the camera at its new pose: the view frames 2.34
    widths of the facade, "no frontal view" stays and the add is refused."""
    ctx = real04_ctx(tmp_path)
    b = ctx.building
    x6 = [CC.finding(v) for v in X.check_exterior(b, ctx.scene, None)["violations"] if v["check"] == "X6"]
    assert [(f["target"], f["severity"]) for f in x6] == [("exterior", "major")]
    ctx.findings = x6
    args = strip_pose(b)
    assert X.validate_camera_override(b, dict(args, action="add"))["ok"]
    loop = LP.AgentLoop(ctx.project_out, MM.MockModel(), recheck=lambda bb, s, m: [], out=lambda s: None)
    verdict = loop.acceptance(ctx, "add_camera", {k: v for k, v in args.items()}, {"accepted": True}, b)
    assert not verdict["accepted"]
    assert verdict["reason"].startswith("finding X6:exterior is still there after the edit"), verdict["reason"]
    mine = {(f["target"], f["severity"]) for f in verdict["after_findings"] if f["check"] == "X6"}
    assert ("exterior", "major") in mine and ("ext_front_entrance", "major") in mine
    assert any("frames only part of the building" in f["message"] for f in verdict["after_findings"])
    assert "X6 measured on the scene the next build makes" in verdict["note"]
    # the trial scene: the new view planned as the build plans it, the others as they are
    trial = LP.camera_scene(ctx, "add_camera", args)
    cam = next(c for c in trial["cameras"] if c["name"] == "ext_front_entrance")
    assert cam["policy"] == "agent" and cam["view"] == "agent" and cam["position"] == args["position"]
    assert [c["name"] for c in trial["cameras"]][:3] == ["ext_1", "ext_2", "ext_4"]
    assert LP.camera_scene(ctx, "set_camera", {"view_id": "cam_r1_1", "kind": "interior", "position": [1, 1, 1],
                                               "target": [2, 2, 1]}) is None
    assert LP.camera_scene(ctx, "set_lighting", {"room_id": "r1"}) is None


def test_after_findings_replaces_the_rounds_x6_with_the_measured_one():
    """``after_findings(x6_after=...)`` drops every code X6 of the round and takes the measured ones; without it (an
    X6 that cannot be measured) the old rule holds: an X6 on a changed target counts as gone."""
    gone = {"id": "c:X6:exterior", "check": "X6", "severity": "major", "target": "exterior", "source": "code",
            "message": "no frontal view", "evidence": {"metrics": {}}}
    other = dict(gone, id="c:X6:ext_2", target="ext_2", message="ext_2 pitched", severity="minor")
    old = LP.after_findings([], [gone, other], {"exterior", "ext_9"})
    assert [f["target"] for f in old] == ["ext_2"]
    measured = [dict(gone), dict(gone, id="c:X6:ext_9", target="ext_9", message="ext_9: no sky in the frame")]
    new = LP.after_findings([], [gone, other], {"exterior", "ext_9"}, x6_after=measured)
    assert sorted(f["target"] for f in new) == ["ext_9", "exterior"]
    assert all(f["cause"] == "exterior_camera" for f in new)
    ok, why = LP.accept_edit([gone, other], new, {"target_finding": [gone]})
    assert not ok and why.startswith("finding X6:exterior is still there")


# --------------------------------------------------------------------------
# 6. a vision claim on the agent's own exterior view goes to that camera
# --------------------------------------------------------------------------

BLANK_WALL = {"check": "X3", "severity": "major", "target": "building", "evidence_image": 1,
              "message": "The entrance facade is a long, blank wall with no visible entrance door at grade."}


def test_mark_agent_views_routes_a_claim_on_the_agents_view_to_its_camera():
    """Fails on BASE (no ``mark_agent_views``; the cause stayed ``facade``, no tool): P6a seq 6856."""
    cams = [{"name": "ext_front_entrance", "kind": "exterior", "room_id": None, "view": "agent", "policy": "agent"},
            {"name": "ext_1", "kind": "exterior", "room_id": None, "view": "corner"}]
    b = {"openings": [{"id": "d_L0_005"}], "walls": [{"id": "w_1"}]}
    on_agent = {"id": "v:1", "source": "vision", "check": "X3", "severity": "major", "target": "building",
                "message": BLANK_WALL["message"], "evidence": {"view": "ext_front_entrance"}}
    on_planner = dict(on_agent, id="v:2", evidence={"view": "ext_1"})
    on_door = dict(on_agent, id="v:3", target="d_L0_005")
    x6_self = {"id": "v:4", "source": "vision", "check": "X6", "severity": "major", "target": "ext_front_entrance",
               "message": "only a blank wall", "evidence": {}}
    code = dict(on_agent, id="c:X3:building", source="code")
    found = [copy.deepcopy(f) for f in (on_agent, on_planner, on_door, x6_self, code)]
    CS.mark_agent_views(found, cams, b)
    assert [f["target"] for f in found] == ["ext_front_entrance", "building", "d_L0_005", "ext_front_entrance",
                                            "building"]
    assert CS._metrics(found[0]) == {"agent_view": "ext_front_entrance", "claimed_target": "building"}
    assert [CS.cause_of(f, b) for f in found] == ["exterior_camera", "facade", "facade", "exterior_camera", "facade"]
    assert set(CS.tools_for_finding(found[0])) >= {"set_camera", "remove_camera"}
    assert CS.agent_view(cams[0]) and not CS.agent_view(cams[1]) and not CS.agent_view(None)


def test_the_round_keeps_a_claim_on_the_agents_view_for_its_camera(tmp_path):
    """Fails on BASE: the round dropped the vision X3 on the agent's view ("no agent tool for the cause facade"); the
    loop now names the critique's view (``evidence.view``) and routes the claim to the camera."""
    loop, out, model = make(tmp_path, [FINISH], [[]], vision=True, max_rounds=1,
                            critic=[{"findings": []}, {"findings": []}, {"findings": [dict(BLANK_WALL)]}])
    scene_path = out / "scene" / "scene_manifest.json"
    scene = read(scene_path)
    for c in scene["cameras"]:
        if c["name"] == "ext_1":
            c.update(view="agent", policy="agent")
    write_json(scene_path, scene)
    loop.run()
    x3 = [e for e in log_of(out)["events"] if e["kind"] == "finding" and e["checklist"] == "X3"]
    assert len(x3) == 1 and x3[0]["target"] == "ext_1" and x3[0]["cause"] == "exterior_camera", x3
    assert not x3[0].get("dropped") and x3[0]["evidence"]["view"] == "ext_1"


# --------------------------------------------------------------------------
# 7. the tools: the free stretch and the frontal role by X6's measured frame
# --------------------------------------------------------------------------

R04_FRONTAL = {"name": "ext_8", "kind": "exterior", "room_id": None, "view": "agent", "sides": ["back"],
               "position": [8.6, 17.5, 1.6], "target": [8.6, 6.0, 1.6], "lens_mm": 26.0, "policy": "agent"}


@needs_real04
def test_the_free_stretch_is_named_only_where_an_eye_level_view_fits(tmp_path):
    """Fails on BASE: the hint sent the agent into the 5.7 m strip between real04's entrance facade and b2 ("a camera
    there stands at eye height"), where P6a's ext_front_entrance showed a blank wall with no sky. Now it says no
    eye-level view fits there, how far the facade needs a camera, and that the frontal view is decision 16."""
    ctx = real04_ctx(tmp_path)
    entry = {"action": "add", "view_id": "ext_9", "kind": "exterior", "position": [8.5, 20.0, 1.6],
             "target": [8.5, 12.5, 1.5], "lens_mm": 26, "reason": "frontal view"}
    failed = X.validate_camera_override(ctx.building, entry)["failed"]
    assert any("inside the building b2" in f for f in failed)
    hint = TL.free_strip_hint(ctx, entry, failed)[-1]
    assert hint.startswith("no eye-level view fits the free stretch on the view line from the target: (8.50, "
                           "12.50) to (8.50, 18."), hint
    assert "does not fit" in hint and "0% of its rays look up into the sky" in hint and "decision 16" in hint
    # a model that cannot be made keeps the old hint (the stretch named as before)
    assert TL.strip_frame_problem(None, (8.5, 12.5), (0.0, 1.0), 5.7, X.exterior_model) is None


@needs_real04
def test_the_role_guards_read_x6s_frontal_view_with_its_frame(tmp_path):
    """Fails on BASE: the role guards judged the next build's plan by its pose alone, so an agent view square to the
    entrance facade that frames 2.34 widths of it and no sky (P6a's ext_front_entrance place) kept the frontal role
    and could not be moved to a better pose or removed. X6 counts it as no frontal view, so neither do the guards."""
    ctx = real04_ctx(tmp_path, P3_EXT + [R04_FRONTAL])
    assert CV.x6_frontal(R04_FRONTAL, MAIN_Y)                         # the pose rule alone
    assert not TL.x6_frontal_of(ctx, R04_FRONTAL, MAIN_Y)              # X6's rule with its frame
    assert not TL.x6_frontal_now(ctx, "ext_8", MAIN_Y)
    assert TL.exterior_of(ctx) is TL.exterior_of(ctx) and TL.exterior_model_of(ctx) is TL.exterior_model_of(ctx)
    corner = {"view_id": "ext_8", "kind": "exterior", "position": [-4.0, 30.0, 1.6], "target": [8.0, 12.0, 1.6]}
    assert TL.role_problem(ctx, "set", "ext_8", corner) is None
    assert TL.role_problem(ctx, "remove", "ext_8", {}) is None
    # a frame recorded on the camera (the build records it on the agent's plans) is read as X6 reads it
    framed = dict(R04_FRONTAL, fill=0.7, fits=True, sky_share=0.3, frame_target=[8.6, 6.0, 1.6])
    assert TL.x6_frontal_of(ctx, framed, MAIN_Y)


# --------------------------------------------------------------------------
# 8. the scheduler: the agent stage's note after the final round
# --------------------------------------------------------------------------

def test_the_final_round_rewrites_the_agent_stage_note(tmp_path, models):
    """Fails on BASE: the agent stage record kept the note written when the rounds ended ("stop: max rounds
    reached" / "no open finding") after the final round for critical findings had run; P6a's stage table said net 32
    while metrics.json said 34. The final round's numbers are written whatever it accepted."""
    r = TRA.orchestrated(tmp_path, [TRA.CHANGE, TRA.FINISH], [[TRA.F1], []])
    assert r.run(**r.kwargs) == 0
    rec = r.record("p1", "agent")
    loop = r.orch.runs[0].agent_loop
    assert rec["status"] == "ok" and rec["note"].endswith(f"stop: {LP.STOPS[loop.stop['reason']]}; {LP.FINAL_DONE}"), \
        rec["note"]
    assert rec["note"].startswith(f"{len(r.orch.runs[0].agent_loop.rounds)} round(s), ")


# --------------------------------------------------------------------------
# 9. two overlapping drawn lamp symbols are one lamp
# --------------------------------------------------------------------------

def _lamps() -> dict:
    a = M.fp("l1", "floor_lamp", (4.3, 0.74), (0.59, 0.59), type_method="ai_two_pass")
    b = M.fp("l2", "floor_lamp", (4.68, 1.02), (0.44, 0.44), type_method="ai_two_pass")
    b["evidence"].append({"file": "deneme.dwg", "method": "ai", "entity": "recognition:sym_L0_012", "confidence": 0.9})
    far = M.fp("l3", "floor_lamp", (0.5, 3.5), (0.44, 0.44))
    chairs = [M.fp("c1", "chair", (2.0, 2.0), (0.71, 0.45)), M.fp("c2", "chair", (2.45, 2.2), (0.71, 0.45))]
    return M.building(room_type="living", furniture=[a, b, far] + chairs)


def test_two_overlapping_drawn_lamp_symbols_are_one_lamp():
    """Fails on BASE: real04's salons kept both lamps of each overlapping pair (f_L-1_063 / 064: 17 % of the smaller
    inside the larger; f_L-1_059 / 060: 33 %), two lamps standing in each other in every render. The smaller is not
    built, labelled by code with its plan crop and the kept piece; chairs that overlap at a table corner keep both."""
    b = _lamps()
    props = INF.duplicate_symbols(b)
    assert [(p["piece_id"], p["kept_id"]) for p in props] == [("l2", "l1")]
    assert props[0]["share"] == pytest.approx(0.173, abs=0.01) and props[0]["build"] is False
    assert props[0]["crop"] == "recognition/crops/sym_L0_012_ctx.png"
    assert [p["piece_id"] for p in INF.infer_types(b) if p.get("type_method") == INF.DUPLICATE_SYMBOL_METHOD] == ["l2"]
    out = INF.apply_inferences(b, props)
    lamp = by_id(out, "l2")
    assert lamp["build"] is False and lamp["inferred_as"] == "detail" and lamp["type"] == "floor_lamp"
    assert lamp["drawn_type"] == "floor_lamp" and lamp["drawn_footprint"] == by_id(b, "l2")["footprint"]
    label = lamp["adjusted_by_ai"]
    assert label["by"] == "code" and label["rule"] == INF.DUPLICATE_SYMBOL_RULE and label["duplicate_of"] == "l1"
    assert label["crop"] == "recognition/crops/sym_L0_012_ctx.png" and label["not_furniture"] == "duplicate_symbol"
    assert lamp["not_built_reason"].startswith("floor_lamp l2 (0.44 x 0.44 m) is drawn 16% inside the larger")
    assert by_id(out, "l1").get("build") is not False and by_id(out, "c2").get("build") is not False
    assert INF.duplicate_symbols(out) == []                                 # idempotent
    # below the share: two lamps side by side stay two lamps
    apart = _lamps()
    by_id(apart, "l2")["footprint"]["center"] = [4.95, 1.02]
    assert INF.duplicate_symbols(apart) == []


@needs_p6a
def test_p6a_salon_lamps_lose_their_duplicates():
    b = read(P6A / "furniture" / "real04" / "building.json")
    got = {p["piece_id"]: p["kept_id"] for p in INF.duplicate_symbols(b)}
    assert got == {"f_L-1_059": "f_L-1_060", "f_L-1_064": "f_L-1_063", "f_L-1_057": "f_L-1_058",
                   "f_L-1_066": "f_L-1_065"}


# --------------------------------------------------------------------------
# 10. metric 12: an agent view that frames part of the building or no sky
# --------------------------------------------------------------------------

def test_metric_12_names_an_agent_view_with_no_sky_or_a_partial_frame(tmp_path):
    """Fails on BASE: P6a's ext_front_entrance (2.34 frame widths, 0 % sky) counted as one more rendered view with no
    sign of what it shows. The frame the build records on the agent's plans names it."""
    from test_m13_report import _scene_cameras_edit, make_run
    from wenart.report import metrics13 as MX

    out = make_run(tmp_path)
    _scene_cameras_edit(out, view="agent", policy="agent", fill=2.3449, fits=False, sky_share=0.0)
    m12 = MX.metrics(out)["metrics"]["m12"]
    assert m12["text"].endswith("; rendered, no sky / partial: ext_1 (2.34 frame widths, cut, 0% sky)"), m12["text"]
    assert m12["parts"]["no_sky_or_partial"] == ["ext_1"] and m12["value"] == 1
    _scene_cameras_edit(out, fits=True, sky_share=0.31)
    assert "no sky / partial" not in MX.metrics(out)["metrics"]["m12"]["text"]
    assert MX.poor_frame({"view": "corner", "fits": False}) is None
