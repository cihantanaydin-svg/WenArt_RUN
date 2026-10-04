"""Milestone 4 GPU tests: run on the pod by scripts/jobs/furnish.sh after the
layout stage (pytest -m gpu tests/gpu/test_furnish.py). They read what the job
wrote under $WENART_OUTPUTS (default /workspace/repo/outputs) for the projects
in $FURNISH_TEST_PROJECTS (default synthetic-01):

- every room of synthetic-01 L1 without documented furniture was asked, and
  every bedroom got a bed, the bathroom a washbasin or toilet (the hall may
  stay empty);
- every added piece passes the six placer checks, recomputed here from the
  furnished building, and no piece lies on a door approach or swing;
- the layout came from the real server: the model is the Qwen checkpoint, the
  server latency is logged per room and per pass (> 0) in layout.json and the
  report lists it.

Milestone 7 (docs/milestone7.md §0, §6.3, §6.5):

- an empty prayer room is never sent to the model; layout.json lists it as
  skipped with the reason (no passes);
- refit (``building_final.json``, when the run got that far): every library
  model's catalogue ``styles`` hold the project's style family (``style.json``)
  or ``neutral``, no bed model without a mattress, every CC BY model with its
  credit line.
"""
import json
import os
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from wenart.furniture import placer as P
from wenart.furniture import schemas

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("FURNISH_TEST_PROJECTS", "synthetic-01").split() if p]
EXPECTED_MODEL = os.environ.get("FURNISH_MODEL", "Qwen/Qwen3-VL-8B-Instruct")


def _load(project: str, name: str) -> dict:
    path = OUTPUTS / project / name
    assert path.exists(), f"{path} missing: did the layout stage run for {project}?"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=PROJECTS)
def project(request):
    return request.param, _load(request.param, "building_furnished.json"), _load(request.param, "layout.json")


def ai_pieces_by_room(building: dict) -> dict:
    rooms = {}
    for f in building["furniture"]:
        if f["source"] == "added_by_ai":
            rooms.setdefault(f["room_id"], []).append(f)
    return rooms


def test_every_empty_room_was_laid_out(project):
    name, building, summary = project
    empty = [r for r in building["rooms"] if not r["has_documented_furniture"]
             and r["room_type"] in schemas.FURNISHABLE_ROOM_TYPES]
    assert empty, f"{name}: no empty room to furnish"
    done = {r["room_id"] for r in summary["rooms"]}
    missing = sorted(r["id"] for r in empty if r["id"] not in done)
    assert not missing, f"{name}: rooms never sent to the model: {missing}"
    for entry in summary["rooms"]:
        if entry["room_type"] in schemas.NOT_FURNISHED_ROOM_TYPES:
            assert entry["passes"] == [] and "never furnished by AI" in (entry["skipped"] or ""), entry
            continue
        assert len(entry["passes"]) == 2, entry["room_id"]
    prayer = [r["id"] for r in building["rooms"] if not r["has_documented_furniture"]
              and r["room_type"] in schemas.NOT_FURNISHED_ROOM_TYPES]
    assert not [f for f in building["furniture"] if f["source"] == "added_by_ai" and f["room_id"] in prayer]


def test_rooms_got_what_their_type_calls_for(project):
    name, building, summary = project
    rooms = ai_pieces_by_room(building)
    problems = []
    for r in building["rooms"]:
        if r["has_documented_furniture"] or r["room_type"] not in schemas.ANCHOR_TYPES:
            continue
        if name == "synthetic-01" and r["level_id"] != "L1":
            continue
        types = {f["type"] for f in rooms.get(r["id"], [])}
        if not types & set(schemas.ANCHOR_TYPES[r["room_type"]]):
            entry = next((e for e in summary["rooms"] if e["room_id"] == r["id"]), {})
            problems.append((r["id"], r["room_type"], sorted(types), entry.get("skipped")))
    assert not problems, f"{name}: rooms without their anchor piece: {problems}"


def test_added_pieces_pass_every_check(project):
    name, building, _summary = project
    rooms = ai_pieces_by_room(building)
    assert rooms, f"{name}: no AI furniture at all"
    for rid, pieces in rooms.items():
        room = next(r for r in building["rooms"] if r["id"] == rid)
        assert not room["has_documented_furniture"], f"{name}: AI furniture in a documented room {rid}"
        ctx = P.room_context(building, room)
        placed = [P.piece_from_furniture(f, i) for i, f in enumerate(pieces)]
        for f, p, checks in zip(pieces, placed, P.check_all(placed, ctx)):
            assert f["status"] == "verified" and f["evidence"][0]["method"] == "ai"
            assert all(f["checks"][c] for c in P.CHECKS), (rid, f["id"], f["checks"])
            assert not P.failed_checks(checks), (rid, f["id"], checks)
            assert Polygon(room["polygon"]).buffer(-0.019).contains(p.polygon()), (rid, f["id"])
            for door in ctx.doors:
                assert p.polygon().intersection(door.zone).area < P.AREA_EPS, (rid, f["id"], door.id)
                assert door.swing is None or p.polygon().intersection(door.swing).area < P.AREA_EPS, (rid, f["id"])
        assert not P.walkway_failures(placed, ctx), rid


def test_real_model_and_latency_logged(project):
    name, building, summary = project
    assert summary["model"] == EXPECTED_MODEL, f"{name}: layout by {summary['model']!r}"
    assert summary["server"].startswith("http")
    for entry in summary["rooms"]:
        for p in entry["passes"]:
            assert p["model"] == EXPECTED_MODEL and p["latency_s"] > 0, (entry["room_id"], p)
        if entry["room_type"] not in schemas.NOT_FURNISHED_ROOM_TYPES:      # never asked: no latency
            assert entry["latency_s"] > 0
    models = {f["evidence"][0]["model"] for f in building["furniture"] if f["source"] == "added_by_ai"}
    assert models <= {EXPECTED_MODEL}, models
    report = (OUTPUTS / name / "layout_report.md").read_text(encoding="utf-8")
    assert " s)" in report, "latency per pass missing from the report"
    debug = OUTPUTS / name / "layout_debug"
    assert any(debug.glob("*.png")) and any(debug.glob("*.json"))


def test_refit_library_models_fit_the_style(project):
    """docs/milestone7.md §6.3: refit takes a library model only when its styles hold the project's family or
    neutral; no bed without a mattress; every CC BY model carries its credit line."""
    from wenart.furniture import catalog as C
    from wenart.furniture import fit as F

    name, _building, _summary = project
    final, style = OUTPUTS / name / "building_final.json", OUTPUTS / name / "style.json"
    if not final.exists() or not style.exists():
        pytest.skip(f"{name}: no building_final.json / style.json (refit not run in this job)")
    building = json.loads(final.read_text(encoding="utf-8"))
    family, how = F.style_family_of(json.loads(style.read_text(encoding="utf-8")))
    catalog = C.load()
    wrong, library = [], 0
    for f in building["furniture"]:
        asset = f.get("asset") or {}
        if asset.get("method") != "library":
            continue
        library += 1
        entry = catalog.entry(asset["asset_id"])
        assert entry is not None, (f["id"], asset["asset_id"])
        if not C.styles_match(entry, family) or not C.has_mattress(entry):
            wrong.append((f["id"], asset["asset_id"], entry.get("styles"), entry.get("has_mattress")))
        assert asset.get("style_family") == family, (f["id"], asset.get("style_family"), family)
        if asset["licence"] == C.CC_BY:
            assert all(str(asset.get(k) or "").strip() for k in C.CC_BY_FIELDS), (f["id"], asset)
    print(f"{name}: style family {family!r} ({how}); {library} library models")
    assert not wrong, f"{name}: library models of another style or without a mattress: {wrong}"
