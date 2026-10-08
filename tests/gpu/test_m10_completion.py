"""Milestone 10 GPU tests, Feature 1 (docs/milestone10.md §2, §5 row 6): run on the pod after a full run
(``pytest -m gpu tests/gpu/test_m10_completion.py``). They read what the layout stage wrote under
$WENART_OUTPUTS (default /workspace/repo/outputs) for the projects in $COMPLETION_TEST_PROJECTS (default
``real01 real02``):

- ``completion.json`` exists, the layout ran with the real model, and the locked check passed: recomputed here
  with ``wenart.furniture.locked.check`` from the drawn building (``building.json``, else
  ``building_fitted.json``) to ``building_furnished.json`` and, when the run got that far, to
  ``building_final.json``: every drawn piece keeps its anchor (± 5 cm) and front (± 1°), 0 violations;
- every furnished bedroom and living room that misses an expected type (or its main piece) got at least one
  added piece (``completes_room``), itself or through its twin / same_as partner;
- every change is listed: each ``modified_by_ai`` piece has its entry in ``completion.json`` with the drawn type
  and size and appears in ``completion_report.md``; each ``completes_room`` piece is listed too;
- 0 placer violations by AI changes or additions: every added piece passes the six checks in its room with the
  drawn pieces as obstacles; a changed piece fails no check its drawn layout did not already fail.
"""
import json
import os
from pathlib import Path

import pytest

from wenart.furniture import locked as LK
from wenart.furniture import placer as P
from wenart.furniture import schemas

pytestmark = pytest.mark.gpu
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PROJECTS = [p for p in os.environ.get("COMPLETION_TEST_PROJECTS", "real01 real02").split() if p]
EXPECTED_MODEL = os.environ.get("FURNISH_MODEL", "Qwen/Qwen3-VL-8B-Instruct")
COMPLETED_TYPES = ("bedroom", "living")


def _load(project: str, name: str):
    path = OUTPUTS / project / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


@pytest.fixture(scope="module", params=PROJECTS)
def run(request):
    project = request.param
    furnished = _load(project, "building_furnished.json")
    completion = _load(project, "completion.json")
    assert furnished is not None and completion is not None, \
        f"{OUTPUTS / project}: building_furnished.json / completion.json missing: did the layout stage run?"
    source = _load(project, "building.json") or _load(project, "building_fitted.json")
    assert source is not None, f"{project}: no building.json / building_fitted.json"
    return project, source, furnished, completion


def _mode(completion: dict) -> str:
    return "keep" if completion["settings"]["furnished_rooms"] == "keep" else "complete"


def test_the_locked_check_passes(run):
    project, source, furnished, completion = run
    keep = [r["room_id"] for r in completion["rooms"] if r["state"] == "kept"]
    assert completion["locked_violations"] == [], completion["locked_violations"]
    assert LK.check(source, furnished, _mode(completion), keep) == []
    final = _load(project, "building_final.json")
    if final is not None:
        assert LK.check(source, final, _mode(completion), keep) == []
    models = {e.get("model") for f in furnished["furniture"] for e in f["evidence"]
              if e.get("method") == "ai" and (f.get("completes_room") or f.get("modified_by_ai"))}
    assert models <= {EXPECTED_MODEL}, models
    assert completion["model"] == EXPECTED_MODEL or not any(r["passes"] for r in completion["rooms"])


def test_rooms_missing_an_expected_type_got_an_added_piece(run):
    project, _source, furnished, completion = run
    if _mode(completion) != "complete":
        pytest.skip(f"{project}: furnished_rooms is keep")
    rooms = {r["room_id"]: r for r in completion["rooms"]}
    added = {}
    for f in furnished["furniture"]:
        if f.get("completes_room"):
            added.setdefault(f["room_id"], []).append(f["type"])
    problems = []
    for rid, r in rooms.items():
        if r["room_type"] not in COMPLETED_TYPES or r["state"] not in ("completed", "copied", "mirrored"):
            continue
        partner = (r.get("partner") or {}).get("id")
        record = rooms.get(partner, r) if r["state"] != "completed" else r
        misses = bool(record.get("missing")) or bool(record.get("anchor_missing"))
        if misses and not added.get(rid):
            problems.append((rid, r["room_type"], record.get("missing"), r["state"], r.get("reason")))
    assert not problems, f"{project}: rooms that miss an expected type and got nothing: {problems}"


def test_every_change_and_every_added_piece_is_listed(run):
    project, source, furnished, completion = run
    report = (OUTPUTS / project / "completion_report.md").read_text(encoding="utf-8")
    drawn = {f["id"]: f for f in source["furniture"]}
    changes = {c["id"]: c for r in completion["rooms"] for c in r["changes"] if c["status"] in ("applied", "reverted")}
    listed = {a["id"] for r in completion["rooms"] for a in r["added"]} | \
        {w["id"] for r in completion["rooms"] for w in r["wall_cabinets"]}
    for f in furnished["furniture"]:
        if f.get("modified_by_ai"):
            assert f["id"] in changes, (project, f["id"])
            c = changes[f["id"]]
            assert c["drawn_type"] == drawn[f["id"]]["type"] == f["drawn_type"], (project, f["id"])
            assert f["drawn_footprint"] == drawn[f["id"]]["footprint"], (project, f["id"])
            assert f"| {f['id']} |" in report, (project, f["id"])
        if f.get("completes_room"):
            assert f["source"] == "added_by_ai" and f["id"] in listed, (project, f["id"])
            assert f"| {f['id']} |" in report, (project, f["id"])


def test_no_placer_violation_by_ai_changes_or_additions(run):
    project, _source, furnished, completion = run
    records = {r["room_id"]: r for r in completion["rooms"]}
    problems = []
    for room in furnished["rooms"]:
        rec = records.get(room["id"])
        if rec is None or rec["state"] not in ("completed", "copied", "mirrored"):
            continue
        items = [f for f in furnished["furniture"] if f.get("room_id") == room["id"]
                 and f["type"] not in schemas.MOUNTED_TYPES]
        ctx = P.room_context(furnished, room)
        drawn = [(f, P.drawn_piece(f, i, against_wall=(f.get("anchor") or {}).get("kind") == "back_edge"))
                 for i, f in enumerate(items) if f["source"] == "from_documents"]
        obstacles = P.obstacles_for([p for _f, p in drawn], ctx)
        excused = rec["drawn_layout"].get("pieces", {})
        drawn_checks = P.check_all([p for _f, p in drawn], ctx)
        for (f, _p), c in zip(drawn, drawn_checks):
            new = set(P.failed_checks(c)) - set(excused.get(f["id"], []))
            if f.get("modified_by_ai") and new:
                problems.append((room["id"], f["id"], "changed", sorted(new)))
        added = [f for f in items if f["source"] == "added_by_ai"]
        pieces = [P.Piece(f["type"], tuple(f["footprint"]["center"]), float(f["footprint"]["rotation_deg"]),
                          tuple(f["footprint"]["size"]), bool((f.get("layout") or {}).get("against_wall")))
                  for f in added]
        ctx2 = P.drawn_context(ctx, obstacles) if obstacles else ctx
        checks = P.obstacle_checks(obstacles + pieces, ctx2)[len(obstacles):]
        for f, c in zip(added, checks):
            if P.failed_checks(c):
                problems.append((room["id"], f["id"], f["type"], P.failed_checks(c)))
    assert not problems, f"{project}: placer violations: {problems}"
