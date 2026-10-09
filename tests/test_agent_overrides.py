"""overrides.json and ``python -m wenart.agent apply`` (docs/milestone11.md §2, §10 "overrides", contract §17.3):
applying twice gives the same file as once, the file (a refit input) changes the refit fingerprint exactly when the
accepted edits change, the camera / exterior / material / geometry overrides land in ``agent_overrides``, an edit
that no longer validates is listed, never forced, and the M10 refit command is unchanged without the agent."""
from __future__ import annotations

import json

from test_agent_helpers import FakeEdits, project
from wenart.agent import __main__ as CLI
from wenart.agent import overrides as OV
from wenart.run import stages as S
from wenart.run import state as ST
from wenart.run.projects import REPO_ROOT, public_project


def seed(out, entries):
    ov = OV.Overrides(out, "toy")
    for rnd, tool, args, accepted in entries:
        ov.add(rnd, tool, args, {"accepted": accepted, "failed_checks": [], "score_before": 50, "score_after": 70,
                                 "rerun_from": "refit", "changed_ids": []}, "mock/agent")
    return ov


def test_apply_twice_equals_once_and_replays_in_order(tmp_path, monkeypatch):
    out = project(tmp_path)
    seed(out, [(1, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0, "reason": "head on the wall"}, True),
               (1, "move_piece", {"piece_id": "f3", "center": [6.0, 2.9], "reason": "back to the wall"}, True),
               (2, "set_camera", {"view_id": "cam_r1_1", "kind": "interior", "room_id": "r1",
                                  "position": [3, 1, 1.4], "target": [1, 3, 1.2], "lens_mm": 20,
                                  "reason": "see the bed"}, True),
               (2, "set_exterior", {"roof": {"type": "hip"}, "reason": "close the roof"}, True),
               (2, "set_exterior", {"roof": {"pitch_deg": 30}, "sun": {"elevation_deg": 35}, "reason": "sun"}, True),
               (2, "set_material", {"slot": "floor", "look_id": "oak_light", "reason": "brief"}, True),
               (2, "rerun_stage", {"stage": "polish", "settings": {"enabled": False}, "reason": "lamp"}, True)])
    fake = FakeEdits()
    first = OV.apply(out, apply_edit=fake)
    text1 = (out / "building_agent.json").read_bytes()
    second = OV.apply(out, apply_edit=fake)
    assert (out / "building_agent.json").read_bytes() == text1 and first == second
    assert first["replayed"] == [1, 2] and first["not_replayed"] == []
    assert [c["op"] for c in fake.calls[:2]] == ["rotate", "move"]
    assert fake.calls[0]["log_seq"] == 1 and fake.calls[0]["model"] == "mock/agent" and fake.calls[0]["round"] == 1
    b = json.loads(text1)
    assert next(f for f in b["furniture"] if f["id"] == "f1")["front_deg"] == 90.0
    ao = b["agent_overrides"]
    assert ao["round"] == 2 and ao["cameras"][0]["action"] == "set" and ao["cameras"][0]["view_id"] == "cam_r1_1"
    assert ao["exterior"] == {"roof": {"type": "hip", "pitch_deg": 30}, "sun": {"elevation_deg": 35}}
    assert ao["materials"] == {"floor": "oak_light"} and ao["reruns"] == {"polish": {"enabled": False}}
    # the decor stage's output is never changed
    assert json.loads((out / "building_decor.json").read_text())["furniture"][0]["front_deg"] == 270.0


def test_the_overrides_change_the_refit_fingerprint(tmp_path):
    out = project(tmp_path)
    fake = FakeEdits()
    seed(out, [(1, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0, "reason": "a"}, True)])
    OV.apply(out, apply_edit=fake)
    ref = public_project("synthetic-01", tmp_path / "results", REPO_ROOT)
    cmd = S.refit(S.Tools(py="PY", polish_py="P", assets=tmp_path), ref, source=S.AGENT_BUILDING)

    def fp():
        return ST.fingerprint("refit", "1", cmd[1:], ST.file_hashes([out / S.AGENT_BUILDING]), "code")

    before = fp()
    OV.apply(out, apply_edit=fake)
    assert fp() == before                                     # nothing changed: the same fingerprint
    seed(out, [(2, "rotate_piece", {"piece_id": "f2", "front_deg": 0.0, "reason": "b"}, True)])
    OV.apply(out, apply_edit=fake)
    assert fp() != before
    # the M10 refit command is unchanged (golden: building_decor.json)
    assert S.refit(S.Tools(py="PY", polish_py="P", assets=tmp_path), ref)[3].endswith("building_decor.json")
    assert cmd[3].endswith("building_agent.json")


def test_rejected_and_stale_edits_are_never_forced(tmp_path):
    out = project(tmp_path)
    seed(out, [(1, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0, "reason": "a"}, False),
               (1, "rotate_piece", {"piece_id": "f9", "front_deg": 90.0, "reason": "gone"}, True),
               (1, "correct_geometry", {"kind": "fix_opening_on_wall", "opening_id": "win2", "evidence": "6 cm",
                                        "reason": "off"}, True)])
    summary = OV.apply(out, apply_edit=FakeEdits())
    assert summary["edits"] == 2 and summary["replayed"] == []
    assert summary["not_replayed"] == [{"seq": 2, "failed_checks": ["unknown_piece"], "message": ""}]
    b = json.loads((out / S.AGENT_BUILDING).read_text())
    assert b["agent_overrides"]["not_replayed"][0]["seq"] == 2
    assert b["agent_overrides"]["geometry"][0]["applied"] is False
    assert b["walls"] == json.loads((out / "building_decor.json").read_text())["walls"]


def test_the_cli(tmp_path, monkeypatch, capsys):
    out = project(tmp_path)
    from wenart.furniture import edit_ops
    monkeypatch.setattr(edit_ops, "apply_edit", FakeEdits())
    seed(out, [(1, "rotate_piece", {"piece_id": "f1", "front_deg": 90.0, "reason": "a"}, True)])
    assert CLI.main(["apply", str(out)]) == 0
    assert "1 furniture edit(s) replayed" in capsys.readouterr().out
    assert CLI.main(["apply", str(tmp_path / "missing")]) == 1
    # without track B's validator (its stub) the edit is listed as not replayed, the file is still written
    monkeypatch.setattr(edit_ops, "apply_edit", lambda *a, **k: (_ for _ in ()).throw(NotImplementedError("B")))
    assert CLI.main(["apply", str(out)]) == 0
    assert json.loads((out / S.AGENT_BUILDING).read_text())["agent_overrides"]["not_replayed"][0][
        "failed_checks"] == ["validator_unavailable"]
    # no overrides at all: building_agent.json = the decor building + empty overrides
    out2 = project(tmp_path / "b")
    assert CLI.main(["apply", str(out2)]) == 0
    b = json.loads((out2 / S.AGENT_BUILDING).read_text())
    assert b["agent_overrides"]["cameras"] == [] and b["furniture"] == json.loads(
        (out2 / "building_decor.json").read_text())["furniture"]
