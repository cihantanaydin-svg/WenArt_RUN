"""Milestone 13, pass before P5 (17 Oct 2026): the integration step after the six tracks applied their small asks.

What (each with the file it changes):
1. ``wenart/report/final.py`` (track L's ask): a view's ``interior_glazing`` record goes into the final manifest, the
   per-view "pull EV" cell names the interior pull next to the window pull, and the exposure summary counts it
   (``interior_pull``), so clipped interior panes are visible in the report.
2. ``wenart/agent/tools.py`` (track F's ask): ``plan_crop`` with a ``piece_id`` also shows the piece's own recognition
   crop (``piece_crop``), the only crop that lifts the mark lock (``edit_ops.own_crop_named``).
3. ``wenart/agent/prompts.py`` (track F's ask): rule 3 of the planner the loop uses says that the room's plan crop is
   no evidence to remove a drawn piece typed from the drawing.
4. ``wenart/ingest/pipeline.py`` (track I's ask): a piece ``_infer_types`` types and builds leaves the review list.
Why: see the module docstrings of those files ("Pass before P5, integration"). How: the toy projects of
``tests/test_report.py``, ``tests/test_agent_helpers.py`` and ``tests/_m11_room.py``; where P3's real04 job results
are on disk (``runs/20261016-172855-full/results``, not committed), the same functions on its data. Every test here
fails on adc3004 (the code before this pass).
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import _m11_room as M
from test_agent_helpers import FakeEdits, fake_validators, project
from test_report import by_cam, make_project
from wenart.agent import log as LG
from wenart.agent import overrides as OV
from wenart.agent import prompts as P
from wenart.agent import tools as TL
from wenart.furniture import edit_ops as EO
from wenart.furniture import infer as INF
from wenart.ingest import pipeline as PL
from wenart.ingest.generic import reading as RD
from wenart.report import final as F

P3 = Path(__file__).resolve().parents[1] / "runs" / "20261016-172855-full" / "results"


# --------------------------------------------------------------------------
# 1. The interior glazing pull in the final report
# --------------------------------------------------------------------------

def _glazing(clip, k=0, clip_before=None):
    pull = None if k is None else {"ev": -float(k), "k": k, "clip_before": clip_before if k else clip,
                                   "clip_after": clip, "pane_px": 400, "rule": "test", "tried": []}
    return {"windows": ["win_i1"], "pane_px": 400, "pane_rb": 1.3, "wall_rb": 1.28, "delta_rb": 0.02, "clip": clip,
            "pull": pull, "rule": "interior glazing"}


def test_the_report_shows_the_interior_glazing_pull(tmp_path):
    out = make_project(tmp_path)
    rm_path = out / "renders" / "render_manifest.json"
    rm = json.loads(rm_path.read_text(encoding="utf-8"))
    rm["renders"][0]["interior_glazing"] = _glazing(0.004, k=3, clip_before=0.12)     # pulled: 12 % -> 0.4 %
    rm["renders"][1]["interior_glazing"] = _glazing(0.05, k=0)                        # clipped, no k chosen
    rm["renders"][2]["interior_glazing"] = _glazing(0.0, k=None)                      # unclipped, not searched
    rm["renders"][1]["window_pull"] = {"ev": -2, "clip_before": 0.2, "clip_after": 0.01, "pane_px": 900}
    rm_path.write_text(json.dumps(rm), encoding="utf-8")
    manifest = F.write_final(out)
    v = by_cam(manifest)
    cams = [r["camera"] for r in rm["renders"]]
    assert v[cams[0]]["interior_glazing"]["pull"]["k"] == 3 and v[cams[3]]["interior_glazing"] is None
    assert manifest["summary"]["exposure"]["interior_pull"] == {"views": 3, "pulled": 1, "clipped": 1, "k_min": 3,
                                                               "k_max": 3}
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| interior k3, clip 12.0 % -> 0.4 % |" in md
    assert "| -2; interior clip 5.0 % (not pulled) |" in md
    assert "| interior glazing pull | 3 view(s) with interior glazing, 1 pulled (k 3), 1 still clipped over 1.0 % |" \
        in md
    # unclipped interior glazing adds nothing to the cell; a view without any pull stays "-"
    assert F._pull_text(None, _glazing(0.0, k=None)) == "-" and F._pull_text({"ev": -1}, None) == "-1"


def test_a_manifest_without_interior_glazing_reads_as_before(tmp_path):
    out = make_project(tmp_path)
    manifest = F.write_final(out)
    assert manifest["summary"]["exposure"]["interior_pull"] == {"views": 0, "pulled": 0, "clipped": 0, "k_min": None,
                                                               "k_max": None}
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| interior glazing pull | - |" in md


def test_the_report_clip_bound_is_the_renders():
    from wenart.blender import render as R
    assert F.INTERIOR_CLIP_MAX == R.PULL_MAX_CLIP


@pytest.mark.skipif(not (P3 / "renders" / "real04" / "render_manifest.json").is_file(),
                    reason="P3's real04 job results are not on disk")
def test_p3_real04_renders_have_no_interior_glazing_record_and_keep_their_cells():
    """P3 ran before the record existed: every cell is the window pull alone, the summary counts no view."""
    rm = json.loads((P3 / "renders" / "real04" / "render_manifest.json").read_text(encoding="utf-8"))
    entries = rm["renders"]
    assert entries and F.interior_pull_summary(e.get("interior_glazing") for e in entries)["views"] == 0
    for e in entries:
        wp = e.get("window_pull")
        assert F._pull_text(wp, e.get("interior_glazing")) == ("-" if not wp or wp.get("ev") is None
                                                              else f"{float(wp['ev']):g}")


# --------------------------------------------------------------------------
# 2. plan_crop shows the piece's own recognition crop
# --------------------------------------------------------------------------

def _ctx(tmp_path):
    out = project(tmp_path)
    log = LG.AgentLog(out, "toy", "mock/agent", "rev")
    return TL.ToolContext.load(out, round=1, model_id="mock/agent", log=log, overrides=OV.Overrides(out),
                               apply_edit=FakeEdits(), validators=fake_validators())


def test_plan_crop_shows_the_pieces_own_recognition_crop(tmp_path):
    ctx = _ctx(tmp_path)
    reg = TL.build_registry()
    (ctx.project_out / "final").mkdir(exist_ok=True)
    (ctx.project_out / "final" / "cam_r1_1_plan.jpg").write_bytes(b"jpg")
    f1 = ctx.piece("f1")
    f1.setdefault("evidence", []).append({"file": "plan.dxf", "method": "ai", "confidence": 0.9,
                                          "entity": "recognition:sym_L0_001"})
    crops = ctx.project_out / TL.RECOGNITION_CROP_DIR
    crops.mkdir(parents=True)
    for name in ("sym_L0_001_iso.png", "sym_L0_001_ctx.png", "sym_L0_009_ctx.png"):
        (crops / name).write_bytes(b"png")
    res = reg.call(ctx, "plan_crop", {"piece_id": "f1"})
    assert res["image"] == "final/cam_r1_1_plan.jpg" and res["piece_crop"] == "recognition/crops/sym_L0_001_ctx.png"
    assert res["piece_crop_note"] == TL.PIECE_CROP_NOTE
    assert [p.name for p in ctx.pending_images[-2:]] == ["cam_r1_1_plan.jpg", "sym_L0_001_ctx.png"]
    # the crop the tool hands out is the one that lifts the mark lock; the room's plan crop is not
    assert EO.own_crop_named(ctx.building, f1, f"plan crop {res['piece_crop']}: a rug outline") == res["piece_crop"]
    assert EO.own_crop_named(ctx.building, f1, f"plan crop {res['image']}: a rug outline") is None
    # a piece without a crop of its own, or a room: the room's crop only, as before
    assert "piece_crop" not in reg.call(ctx, "plan_crop", {"piece_id": "f2"})
    assert "piece_crop" not in reg.call(ctx, "plan_crop", {"room_id": "r1"})
    # a secondary page's crop: where the piece's review entry records it, before the default folder
    ctx.building.setdefault("needs_review", []).append(
        {"id": "f2", "kind": "untyped_piece", "reason": "x", "crop": "recognition/r16/crops/sym_L0_009_ctx.png"})
    (ctx.project_out / "recognition" / "r16" / "crops").mkdir(parents=True)
    (ctx.project_out / "recognition" / "r16" / "crops" / "sym_L0_009_ctx.png").write_bytes(b"png")
    assert reg.call(ctx, "plan_crop", {"piece_id": "f2"})["piece_crop"] == "recognition/r16/crops/sym_L0_009_ctx.png"
    # no file on disk: no piece crop
    f1["evidence"][-1]["entity"] = "recognition:sym_L0_404"
    assert ctx.own_crop_path("f1") is None


def test_the_tools_crop_folder_is_the_readings():
    assert TL.RECOGNITION_CROP_DIR == RD.CROP_DIR


@pytest.mark.skipif(not (P3 / "recognition" / "real04" / "crops").is_dir(),
                    reason="P3's real04 job results are not on disk")
def test_p3_real04_own_crops_on_disk(tmp_path):
    """P3 real04: the round coffee tables f_L1_015 / f_L1_016 (typed by code) have their own crop on disk, which
    lifts their mark lock; the coffee table f_L1_024 the agent removed with the room's crop has none."""
    b = json.loads((P3 / "furniture" / "real04" / "building_agent.json").read_text(encoding="utf-8"))
    (tmp_path / "recognition").mkdir()
    (tmp_path / "recognition" / "crops").symlink_to(P3 / "recognition" / "real04" / "crops")
    by_id = {f["id"]: f for f in b["furniture"]}
    stub = SimpleNamespace(building=b, project_out=tmp_path, piece=by_id.get)
    found = {pid: TL.ToolContext.own_crop_path(stub, pid) for pid in by_id}
    assert found["f_L1_015"].name == "sym_L1_001_ctx.png" and found["f_L1_016"].name == "sym_L1_002_ctx.png"
    assert found["f_L1_024"] is None
    rel = str(found["f_L1_015"].relative_to(tmp_path))
    assert EO.own_crop_named(b, by_id["f_L1_015"], f"plan crop {rel}") == rel
    assert EO.own_crop_named(b, by_id["f_L1_015"], "plan crop check/cam_r_L1_koridor_2_1_plan.jpg") is None
    assert sum(p is not None for p in found.values()) == 80


# --------------------------------------------------------------------------
# 3. Rule 3 of the planner
# --------------------------------------------------------------------------

def test_planner_rule_3_says_the_room_crop_is_no_removal_evidence():
    rule3 = P.PLANNER_SYSTEM_M12.split("\n3. ", 1)[1].split("\n4. ", 1)[0]
    assert "The room's plan crop or a view is no evidence that a drawn piece typed from the drawing is not " \
           "furniture" in rule3
    assert "plan_crop with its piece_id" in rule3 and "(F9, S2, G*)" in rule3 and "move, snap or turn it" in rule3


# --------------------------------------------------------------------------
# 4. A piece _infer_types types leaves the review list
# --------------------------------------------------------------------------

UNTYPED = "untyped (CLAUDE.md: no untyped piece is built)"


def _review(pid):
    return {"id": pid, "kind": PL.UNTYPED_REVIEW_KIND, "reason": "drawn piece in r has no type: not built",
            "crop": f"recognition/crops/{pid}_ctx.png", "room_id": M.ROOM_ID, "level_id": "L0"}


def test_infer_types_drops_the_review_entry_of_a_piece_it_types(monkeypatch):
    u = M.fp("u", "unknown", (3.5, 1.0), (0.45, 0.40), front=None, status="unverified", type_method="none",
             build=False, not_built_reason=UNTYPED)
    v = M.fp("v", "unknown", (1.0, 3.0), (0.50, 0.50), front=None, status="unverified", type_method="none",
             build=False, not_built_reason=UNTYPED)
    build = PL.ProjectBuild(M.building(furniture=[u, v]))
    b = build.building
    b["needs_review"] = [_review("u"), _review("v"), {"id": "u", "kind": "other", "reason": "kept"}]
    build.reading = {"needs_review": 2}
    prop = {"piece_id": "u", "type": "nightstand", "type_method": "twin", "reason": "the twin room's nightstand",
            "confidence": 0.9, "evidence": {"file": "plan.dxf", "method": "inferred", "confidence": 0.9,
                                            "entity": "twin:f9"}}
    monkeypatch.setattr(INF, "infer_types", lambda view: [dict(prop)])
    monkeypatch.setattr(RD, "withdraw_questions", lambda *a, **k: {})
    PL._infer_types(build)
    typed = next(f for f in b["furniture"] if f["id"] == "u")
    assert (typed["type"], typed["type_method"], typed.get("build")) == ("nightstand", "twin", True)
    assert [(n["id"], n["kind"]) for n in b["needs_review"]] == [("v", PL.UNTYPED_REVIEW_KIND), ("u", "other")]
    assert build.reading["needs_review"] == 1


def test_drop_typed_reviews_keeps_pieces_still_unknown_or_not_built():
    a = M.fp("a", "table_coffee", (2.0, 2.0), (1.2, 0.6), type_method="twin")
    rug = M.fp("rug", "rug", (2.0, 2.0), (2.0, 1.5), build=False, inferred_as="rug")
    still = M.fp("s", "unknown", (1.0, 1.0), (0.4, 0.4), build=False, not_built_reason=UNTYPED)
    unknown = M.fp("x", "unknown", (3.0, 1.0), (0.4, 0.4))             # no build flag: still no type
    build = PL.ProjectBuild(M.building(furniture=[a, rug, still, unknown]))
    build.building["needs_review"] = [_review("a"), _review("rug"), _review("s"), _review("x")]
    assert PL._drop_typed_reviews(build, {"a", "rug", "s", "x"}) == 1
    assert [n["id"] for n in build.building["needs_review"]] == ["rug", "s", "x"]
    assert PL._drop_typed_reviews(build, set()) == 0
