"""Shared fakes of the M11 agent tests (docs/milestone11.md §10): a two-room project output, a fake edit validator
(``edit_ops.apply_edit`` of track B), fake exterior / view validators (track C) and a scripted code critic.

The other ``tests/test_agent_*.py`` import from here (pytest puts ``tests/`` on the path); the one test below
checks the fixture itself."""
from __future__ import annotations

import copy
import json
import types
from pathlib import Path

from PIL import Image

ROOMS = {
    "r1": {"id": "r1", "level_id": "L0", "label": "Yatak", "room_type": "bedroom", "area_computed": 14.0,
           "polygon": [[0, 0], [4, 0], [4, 3.5], [0, 3.5]], "status": "verified"},
    "r2": {"id": "r2", "level_id": "L0", "label": "Salon", "room_type": "living", "area_computed": 14.0,
           "polygon": [[4, 0], [8, 0], [8, 3.5], [4, 3.5]], "status": "verified"},
}


def wall(wid, a, b, exterior=True):
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": 0.2, "height": 2.7,
            "exterior": exterior, "status": "verified"}


def piece(pid, room, ftype, center, size, rotation, front, source="from_documents"):
    return {"id": pid, "level_id": "L0", "room_id": room, "type": ftype, "source": source,
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation}, "front_deg": front,
            "height": None, "status": "verified"}


def building() -> dict:
    return {
        "schema_version": "0.1", "project": {"id": "toy"}, "status": "ok",
        "levels": [{"id": "L0", "label": "Zemin", "elevation": 0.0, "ceiling_height": 2.7}],
        "walls": [wall("w1", (0, 0), (4, 0)), wall("w2", (4, 0), (4, 3.5), False), wall("w3", (4, 3.5), (0, 3.5)),
                  wall("w4", (0, 3.5), (0, 0)), wall("w5", (4, 0), (8, 0)), wall("w6", (8, 0), (8, 3.5)),
                  wall("w7", (8, 3.5), (4, 3.5)), wall("w8", (0.0, 0.08), (2.0, 0.08))],
        "openings": [{"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w1", "center": [3.2, 0.0],
                      "width": 0.9, "height": 2.1, "sill_height": None, "swing_side": "r1"},
                     {"id": "win1", "type": "window", "level_id": "L0", "wall_id": "w3", "center": [2.0, 3.5],
                      "width": 1.2, "height": 2.2, "sill_height": 0.9},
                     {"id": "win2", "type": "window", "level_id": "L0", "wall_id": "w6", "center": [8.06, 1.5],
                      "width": 1.2, "height": 2.2, "sill_height": 0.9}],
        "rooms": [copy.deepcopy(ROOMS["r1"]), copy.deepcopy(ROOMS["r2"])],
        "furniture": [piece("f1", "r1", "bed_double", (2.0, 2.45), (1.6, 2.0), 0.0, 270.0),
                      piece("f2", "r1", "nightstand", (0.9, 3.25), (0.4, 0.4), 0.0, 270.0),
                      piece("f3", "r2", "sofa", (6.0, 3.0), (2.0, 0.9), 0.0, 270.0, "added_by_ai")],
        "conflicts": [], "unverified": [], "warnings": [],
    }


CAMERAS = [{"name": "cam_r1_1", "room_id": "r1", "level_id": "L0", "position": [3.5, 0.5, 1.3],
            "target": [1.0, 3.0, 1.2], "lens_mm": 18.0, "visible_furniture": ["f1", "f2"]},
           {"name": "cam_r2_1", "room_id": "r2", "level_id": "L0", "position": [7.5, 0.5, 1.3],
            "target": [5.0, 3.0, 1.2], "lens_mm": 18.0, "visible_furniture": ["f3"]},
           {"name": "ext_1", "room_id": None, "level_id": None, "kind": "exterior", "position": [-8, -8, 1.6],
            "target": [4, 2, 1.6], "lens_mm": 28.0}]


def write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return path


def jpg(path: Path, colour=(120, 140, 160)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (96, 54), colour).save(path, quality=80)
    return path


def project(tmp_path: Path, name: str = "toy", previews: bool = True) -> Path:
    """A project output after round 0: building_decor.json, building_final.json, style.json, the scene manifest
    and (``previews``) the round-0 previews in agent/previews."""
    out = tmp_path / name
    b = building()
    write_json(out / "building_decor.json", b)
    write_json(out / "building_final.json", b)
    write_json(out / "building.json", b)
    write_json(out / "style.json", {"palette": {}})
    write_json(out / "scene" / "scene_manifest.json", {"cameras": copy.deepcopy(CAMERAS)})
    if previews:
        for c in CAMERAS:
            jpg(out / "agent" / "previews" / f"{c['name']}_preview.jpg")
        write_json(out / "agent" / "previews" / "render_manifest.json",
                   {"renders": [{"camera": c["name"], "preview": f"{c['name']}_preview.jpg"} for c in CAMERAS]})
    return out


class FakeEdits:
    """``edit_ops.apply_edit`` (contract §17.2): rotate / move / resize / change_type / remove / add / set_room_type;
    rejects a front of 355 (a "wall" check; 999 is refused by track B's schema before), an unknown piece and a ``reject`` reason; score 50 -> 70."""

    def __init__(self):
        self.calls: list[dict] = []

    def __call__(self, building, edit, *, catalog=None):
        self.calls.append(copy.deepcopy(edit))
        b = copy.deepcopy(building)
        op = edit["op"]
        res = {"accepted": False, "failed_checks": [], "score_before": 50.0, "score_after": 50.0, "building": None,
               "changed_ids": [], "rerun_from": "layout" if op in ("relayout_room", "set_room_type") else "refit",
               "message": ""}
        if "reject" in str(edit.get("reason")):
            res["failed_checks"] = ["score_drop"]
            return res
        if op in ("relayout_room", "set_room_type", "add", "add_group"):
            room = next((r for r in b["rooms"] if r["id"] == edit.get("room_id")), None)
            if room is None:
                res["failed_checks"] = ["unknown_room"]
                return res
            if op == "set_room_type":
                room["room_type"] = edit["type"]
            if op == "add":
                b["furniture"].append(piece(f"f_ai_{len(b['furniture']) + 1}", room["id"], edit["type"],
                                            (5.0, 1.0), (0.8, 0.8), 0.0, 270.0, "added_by_ai"))
            res.update(accepted=True, building=b, changed_ids=[room["id"]], score_after=70.0)
            return res
        p = next((f for f in b["furniture"] if f["id"] == edit.get("piece_id")), None)
        if p is None:
            res["failed_checks"] = ["unknown_piece"]
            return res
        if op == "rotate":
            if edit["front_deg"] == 355:
                res["failed_checks"] = ["front_into_wall"]
                return res
            p["front_deg"] = edit["front_deg"]
            p["footprint"]["rotation_deg"] = (edit["front_deg"] + 90.0) % 360.0
        elif op == "move":
            p["footprint"]["center"] = list(edit.get("center") or p["footprint"]["center"])
        elif op == "resize":
            p["footprint"]["size"] = list(edit["size"][:2])
        elif op == "change_type":
            p["type"] = edit["type"]
        elif op == "remove":
            b["furniture"] = [f for f in b["furniture"] if f["id"] != p["id"]]
        if op != "remove" and p.get("source") == "from_documents":
            p["adjusted_by_ai"] = {"reason": edit.get("reason"), "round": edit.get("round"),
                                   "log_seq": edit.get("log_seq"), "model": edit.get("model"), "changed": {op: True}}
        res.update(accepted=True, building=b, changed_ids=[p["id"]], score_after=70.0)
        return res


def fake_validators(exterior=(), views=None):
    """``wenart.blender.exterior_checks`` (contract §17.2) with fixed answers: a camera below the floor and the
    look ``nope`` are refused."""
    def camera(building, cam):
        bad = cam.get("position") and float(cam["position"][2]) < 0
        return {"ok": not bad, "failed": ["camera below the floor"] if bad else []}

    return types.SimpleNamespace(
        validate_camera_override=camera,
        validate_exterior_override=lambda building, ov: {"ok": True, "failed": []},
        validate_material_override=lambda style, ov: {"ok": "nope" not in ov.values(),
                                                      "failed": ["unknown look"] if "nope" in ov.values() else []},
        check_exterior=lambda b, s=None, r=None: {"score": 90, "violations": list(exterior)},
        check_views=lambda b, r: {"views": dict(views or {})})


def violation(check, severity, target, room_id=None, message="wrong"):
    return {"check": check, "severity": severity, "target": target, "room_id": room_id, "message": message,
            "metrics": {"m": 1}}


class ScriptedCritic:
    """A code critic (``critic_code.run``-shaped) that answers round by round from a list of violation lists."""

    def __init__(self, rounds):
        self.rounds = list(rounds)
        self.calls = 0

    def __call__(self, building, scene, manifest):
        from wenart.agent import critic_code as CC
        items = self.rounds[min(self.calls, len(self.rounds) - 1)] if self.rounds else []
        self.calls += 1
        return {"findings": [CC.finding(v) for v in items],
                "checks": [{"source": "plausibility", "status": "ok", "note": None, "counts": {}}],
                "scores": {}, "mean": None}


def test_the_fixture_is_a_valid_two_room_output(tmp_path):
    out = project(tmp_path)
    b = json.loads((out / "building_decor.json").read_text())
    assert [r["id"] for r in b["rooms"]] == ["r1", "r2"] and len(b["furniture"]) == 3
    assert (out / "agent" / "previews" / "cam_r1_1_preview.jpg").is_file()
    res = FakeEdits()(b, {"op": "rotate", "piece_id": "f1", "front_deg": 90.0, "reason": "x"})
    assert res["accepted"] and res["building"]["furniture"][0]["front_deg"] == 90.0 and b["furniture"][0][
        "front_deg"] == 270.0
