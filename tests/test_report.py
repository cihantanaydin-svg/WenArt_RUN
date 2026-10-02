"""CPU tests for wenart.report (docs/milestone5.md §7): the final decision, final/ files and the sweep report.

A hand-made project output (scene, render, polish, check manifests in the
shapes of §2.5, §3.6, §4.3, §5.7) with five views covers every final
reason: polished, rejected by the vision check (flagged and recomputed),
check incomplete, gate. Missing inputs (no check, no polish, no renders,
results copies without PNGs) must still give a report that says what did
not run. Images are tiny except where the 300 KB limit is tested.

Milestone 6 (docs/milestone6.md §7.4, §9): the gate validation and its effect
on the finals, camera policy/score, window pull, views per room, the stage
table from ``run/*.json``, private projects (no plan crop or debug image
copied), the needs-review report and ``resolve_repo_path`` for the building.
"""
import copy
import json
import re
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart import views as VW
from wenart.report import common as C
from wenart.report import final as F
from wenart.report import sweep as S
from wenart.report.__main__ import main as report_main

W, H = 96, 54
CAMERAS = [("cam_salon_1", "r_L0_salon", "L0"), ("cam_salon_2", "r_L0_salon", "L0"), ("cam_hol_1", "r_L0_hol", "L0"),
           ("cam_yatak_1", "r_L1_yatak", "L1"), ("cam_yatak_2", "r_L1_yatak", "L1")]
INDEX = {"d_1": 1, "win_1": 2, "win_2": 3, "f_1": 4, "f_2": 5, "f_3": 6, "f_9": 7, "dec_1": 8}


def ev(file="plan.dxf", **kw):
    return [{"file": file, "method": "vector", "confidence": 1.0, **kw}]


def building(project_dir: Path) -> dict:
    return {
        "schema_version": "0.1", "status": "ok",
        "project": {"id": "toy", "source_folder": str(project_dir), "brief": {"style": "stale brief"}},
        "documents": [], "walls": [],
        "levels": [{"id": "L0", "label": "Zemin"}, {"id": "L1", "label": "1. Kat"}],
        "rooms": [{"id": "r_L0_salon", "level_id": "L0", "room_type": "living", "status": "verified"},
                  {"id": "r_L0_hol", "level_id": "L0", "room_type": "hall", "status": "verified"},
                  {"id": "r_L1_yatak", "level_id": "L1", "room_type": "bedroom", "status": "verified"}],
        "openings": [{"id": "d_1", "type": "door", "level_id": "L0", "status": "verified",
                      "evidence": ev(layer="KAPI", entity="INSERT:F4")},
                     {"id": "win_1", "type": "window", "level_id": "L0", "status": "verified",
                      "evidence": ev(layer="PENCERE", entity="INSERT:A1")},
                     {"id": "win_2", "type": "window", "level_id": "L1", "status": "verified",
                      "evidence": ev("plan.pdf", page=2, entity="path:12")}],
        "furniture": [{"id": "f_1", "type": "sofa", "level_id": "L0", "room_id": "r_L0_salon",
                       "source": "from_documents", "status": "verified",
                       "evidence": ev(layer="MOBILYA", entity="INSERT:1A"),
                       "asset": {"method": "library", "licence": "CC0"}},
                      {"id": "f_2", "type": "tv_unit", "level_id": "L0", "room_id": "r_L0_salon",
                       "source": "added_by_ai", "status": "verified",
                       "evidence": [{"file": "layout", "method": "ai", "model": "qwen", "confidence": 0.9}],
                       "asset": {"method": "parametric", "licence": "n/a"}},
                      {"id": "f_3", "type": "bed_double", "level_id": "L1", "room_id": "r_L1_yatak",
                       "source": "from_documents", "status": "verified", "evidence": ev(entity="INSERT:2B"),
                       "asset": {"method": "library", "licence": "CC0"}},
                      {"id": "f_9", "type": "unknown", "level_id": "L0", "room_id": "r_L0_hol",
                       "source": "from_documents", "status": "unverified", "evidence": ev(entity="INSERT:9Z")}],
        "decor": [{"id": "dec_1", "type": "plant", "level_id": "L0", "room_id": "r_L0_salon", "source": "added_by_ai",
                   "method": "rule", "reason": "plant in the free corner", "asset": None}],
        "conflicts": [{"id": "c_001", "kind": "count_mismatch", "element_ids": ["win_2"],
                       "description": "plan.dxf has 2 windows, plan.pdf p2 has 1", "resolution": "DXF wins"}],
        "unverified": ["f_9"],
        "warnings": [],
    }


def obj(name, wid, kind, pi, **extra):
    return {"name": name, "wenart_id": wid, "kind": kind, "status": "verified", "level_id": "L0",
            "evidence": ev(), "pass_index": pi, **extra}


def scene(building_path: Path) -> dict:
    return {
        "schema_version": "0.1", "project": "toy", "building": str(building_path),
        "style_profile": {"walls": {"material": "plaster_white"}}, "seconds": 36.4,
        "cameras": [{"name": c, "room_id": r, "level_id": l} for c, r, l in CAMERAS],
        "materials": {"plaster_white__x": {"textured": True, "asset": "white_plaster_02", "licence": "CC0"},
                      "wood__y": {"textured": True, "asset": "WoodFloor051", "licence": "CC0"},
                      "flat": {"textured": False}},
        "pass_index": INDEX,
        "objects": [
            obj("w_1", "w_1", "wall", None),
            obj("d_1_frame", "d_1", "door", 1, room_ids=["r_L0_salon", "r_L0_hol"]),
            obj("win_1_frame", "win_1", "window", 2, room_ids=["r_L0_salon"]),
            obj("win_2_frame", "win_2", "window", 3, room_ids=["r_L1_yatak"], level_id="L1"),
            obj("furn_f_1", "f_1", "furniture", 4, room_id="r_L0_salon", type="sofa", source="from_documents"),
            obj("furn_f_2", "f_2", "furniture", 5, room_id="r_L0_salon", type="tv_unit", source="added_by_ai"),
            obj("furn_f_3", "f_3", "furniture", 6, room_id="r_L1_yatak", type="bed_double", source="from_documents",
                level_id="L1"),
            obj("proxy_f_9", "proxy:f_9", "furniture_proxy", 7, room_id="r_L0_hol", type="unknown",
                source="from_documents", status="unverified"),
            obj("decor_dec_1", "dec_1", "decor", 8, room_id="r_L0_salon", type="plant", source="added_by_ai",
                status="assumed"),
        ],
    }


STATS = {
    "cam_salon_1": {"1": [400, [0, 10, 12, 50]], "2": [300, [40, 5, 60, 25]], "4": [900, [20, 30, 70, 54]],
                    "5": [200, [70, 30, 90, 45]], "8": [50, [5, 40, 10, 50]]},
    "cam_salon_2": {"2": [300, [40, 5, 60, 25]], "4": [800, [20, 30, 70, 54]], "5": [250, [70, 30, 90, 45]]},
    "cam_hol_1": {"1": [500, [30, 5, 50, 54]], "7": [300, [60, 20, 90, 50]]},
    "cam_yatak_1": {"3": [300, [10, 5, 30, 25]], "6": [1200, [20, 25, 80, 54]]},
    "cam_yatak_2": {"3": [300, [50, 5, 70, 25]], "6": [1000, [10, 25, 70, 54]]},
}


def render_entry(cam, room, i):
    stats = {k: {"pixels": v[0], "box": v[1]} for k, v in STATS[cam].items()}
    return {"camera": cam, "png": f"{cam}.png", "exr": f"{cam}_passes.exr", "preview": f"{cam}_preview.jpg",
            "depth_png": f"{cam}_depth.png", "index_png": f"{cam}_index.png", "seconds": 10.0 + i, "samples": 128,
            "resolution": [W, H], "index_values": sorted(int(k) for k in stats), "room_id": room,
            "scene_sha256": "x", "index_stats": stats,
            "files": {"depth_mm": f"{cam}_depth_mm.png", "normal": f"{cam}_normal.png"},
            "render_key": f"{i:016x}", "hidden": [], "plugged": [],
            "exposure": {"mode": "auto", "ev": [1.5, 2.0, 8.0, 0.5, 1.0][i], "ev_raw": 1.5, "at_limit": i == 2,
                         "target": 0.9, "whitepoint": [1.0, 1.0, 0.9], "meter_seconds": 2.0, "source": None}}


def gate(decision, checks=()):
    reasons = [{"check": c, "region": "global", "value": 0.5, "threshold": 0.95, "op": ">="} for c in checks]
    return {"decision": decision, "reasons": reasons, "notes": [],
            "metrics": {"edges": {"global": 0.99 if decision == "accept" else 0.7, "regions": {}, "skipped": {}},
                        "depth": {"global": 0.01, "regions": {}, "skipped": {}},
                        "regions": {}, "seconds": {"edges": 0.5, "depth": 1.5}},
            "gate_key": "g" * 16}


def attempt(cam, k, decision, checks=(), strength=0.375):
    return {"k": k, "role": "ladder", "strength": strength, "control": "depth", "scale": 0.8, "size": "native",
            "mode": "plain", "seed": k, "steps": 8, "sigmas": [0.643, 0.5], "seconds": 6.0, "png": f"{cam}_a{k}.png",
            "sha256": "a" * 64, "attempt_key": "b" * 64, "panes_restored": 1, "gate": gate(decision, checks),
            "debug_jpg": f"{cam}_a{k}_gate.jpg", "gate_seconds": 2.0}


def polish_manifest(sha: dict) -> dict:
    def view(cam, room, final, k, attempts, reason=None):
        return {"camera": cam, "room_id": room, "source_png": f"../renders/{cam}.png", "source_sha256": sha[cam],
                "prompt": "Photorealistic interior photograph", "controls": {"depth": f"{cam}_control_depth.png"},
                "attempts": attempts, "final": final, "final_attempt": k, "reason": reason}
    model = {"repo": "r", "revision": "0" * 40, "licence": "Apache-2.0"}
    return {
        "schema_version": "0.1", "kind": "run", "project": "toy", "incomplete": False,
        "models": {"base": {**model, "repo": "Tongyi-MAI/Z-Image-Turbo", "files": []},
                   "controlnet": {**model, "repo": "alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1"},
                   "gate": {"depth": {**model, "repo": "depth-anything/Depth-Anything-V2-Small-hf"},
                            "sam": {**model, "repo": "facebook/sam2.1-hiera-large"},
                            "dino": {**model, "repo": "facebook/dinov2-base"}}},
        "config": {}, "thresholds": {"calibration": {"source": None, "accepted_shortfall": None}},
        "device": "cuda", "torch": "2.9.1", "diffusers": "0.40.0", "memory_mode": "resident",
        "peak_vram_gib": 17.9, "load_seconds": 30.0, "seconds_per_forward": 3.0,
        "views": [
            view("cam_salon_1", "r_L0_salon", "polished", 1, [attempt("cam_salon_1", 1, "accept")]),
            view("cam_salon_2", "r_L0_salon", "polished", 2,
                 [attempt("cam_salon_2", 1, "reject", ["edges"]), attempt("cam_salon_2", 2, "accept", strength=0.25)]),
            view("cam_hol_1", "r_L0_hol", "cycles", None,
                 [attempt("cam_hol_1", k, "reject", ["depth"]) for k in (1, 2, 3)], reason="gate"),
            view("cam_yatak_1", "r_L1_yatak", "polished", 2,
                 [attempt("cam_yatak_1", 1, "reject", ["colour"]), attempt("cam_yatak_1", 2, "accept", strength=0.25)]),
            view("cam_yatak_2", "r_L1_yatak", "polished", 2,
                 [attempt("cam_yatak_2", 1, "reject", ["colour"]), attempt("cam_yatak_2", 2, "accept", strength=0.25)]),
        ],
        "rooms": {"r_L0_salon": {"rule": "ok", "rung": None}, "r_L1_yatak": {"rule": "downgraded", "rung": 2}},
        "warnings": [],
    }


def element(label, role, kind, type_, source, result, statuses=("present", "present")):
    passes = {k: {"status": s, "seen_as": type_, "confidence": 0.9} for k, s in zip(("qwen", "glm"), statuses)}
    return {"label": label, "role": role, "kind": kind, "type": type_, "type_unverified": type_ == "unknown",
            "source": source, "box_1000": [0, 0, 100, 100], "passes": passes, "result": result, "single": None}


def check_entry(elements, verdict="ok", extras=(), counts=None, not_computed=(), unreliable=(), images=()):
    return {"verdict": verdict, "prompt_kind": "check", "elements": elements, "extras": list(extras),
            "extras_dropped": {}, "counts": counts or {"door": {"expected": [0, 1], "passes": {"qwen": 0, "glm": 0},
                                                               "result": "ok"}},
            "unreliable": list(unreliable), "not_computed": list(not_computed), "decoy": None, "images": list(images)}


def check_manifest() -> dict:
    ok_salon = {"f_1": element("E1", "required", "furniture", "sofa", "from_documents", "ok"),
                "win_1": element("E2", "required", "window", "window", "from_documents", "ok"),
                "f_2": element("E3", "optional", "furniture", "tv_unit", "added_by_ai", "ok")}
    lost = copy.deepcopy(ok_salon)
    lost["f_1"].update(result="missing", passes={"qwen": {"status": "absent"}, "glm": {"status": "absent"}})
    yatak = {"f_3": element("E1", "required", "furniture", "bed_double", "from_documents", "ok"),
             "win_2": element("E2", "required", "window", "window", "from_documents", "ok")}
    yatak_lost = copy.deepcopy(yatak)
    yatak_lost["f_3"]["result"] = "changed"
    hol = {"f_9": element("E1", "required", "furniture", "unknown", "from_documents", "ok"),
           "d_1": element("E2", "required", "door", "door", "from_documents", "missing", ("absent", "absent"))}
    extra = {"class": "furniture", "categories": {"qwen": "armchair", "glm": "armchair"}, "box_px": [5, 5, 30, 30],
             "iou": 0.6, "confirmed": True, "passes": ["qwen", "glm"], "info": False}
    pref = {"votes": 3, "answers": 4, "asked": 4, "min_votes": 3, "preferred": True, "calls": {}}
    views = {
        "cam_salon_1": {"cycles": check_entry(ok_salon),
                        "polished": {**check_entry(ok_salon, images=["../polish/cam_salon_1_a1.png"]),
                                     "preference": pref},
                        "json_crosscheck": {"level_id": "L0", "in_json_not_rendered": [], "rendered_not_in_json": [],
                                            "misplaced": []},
                        "polished_rejected": False, "polished_reason": None, "polished_reasons": [],
                        "needs_review": False, "needs_review_reasons": []},
        "cam_salon_2": {"cycles": check_entry(ok_salon), "polished": check_entry(lost, "mismatch"),
                        "json_crosscheck": {"in_json_not_rendered": [], "rendered_not_in_json": [], "misplaced": []},
                        "polished_rejected": True, "polished_reason": "vision_check",
                        "polished_reasons": [{"reason": "vision_check", "what": "element", "id": "f_1", "type": "sofa",
                                              "source": "from_documents", "cycles": "ok", "polished": "missing"}],
                        "needs_review": False, "needs_review_reasons": []},
        "cam_hol_1": {"cycles": check_entry(hol, "mismatch", extras=[extra]),
                      "json_crosscheck": {"in_json_not_rendered": [
                          {"id": "f_9", "kind": "furniture", "type": "unknown", "source": "from_documents",
                           "status": "unverified", "visible_share": 0.6, "area_frac": 0.05, "box_px": [1, 2, 3, 4]}],
                          "rendered_not_in_json": [], "misplaced": []},
                      "polished_rejected": False, "polished_reasons": [], "needs_review": True,
                      "needs_review_reasons": ["d_1 (door, from_documents): missing"]},
        "cam_yatak_1": {"cycles": check_entry(yatak), "polished": check_entry(yatak, "not_computed",
                                                                               not_computed=["glm"]),
                        "polished_rejected": True, "polished_reason": "check_incomplete",
                        "polished_reasons": [{"reason": "check_incomplete", "image": "polished",
                                              "detail": "not computed: glm"}],
                        "needs_review": False, "needs_review_reasons": []},
        # The manifest did not flag it, but the elements show a loss: recomputed as vision_check.
        "cam_yatak_2": {"cycles": check_entry(yatak), "polished": check_entry(yatak_lost, "mismatch"),
                        "polished_rejected": False, "polished_reasons": [], "needs_review": False},
    }
    return {"schema_version": "0.1", "project": "toy", "advisory": True, "advisory_reason": "decoy_accept[glm] 0.2",
            "single_pass": False, "model_keys": ["qwen", "glm"],
            "models": {"qwen": {"id": "Qwen/Qwen3-VL-8B-Instruct", "slug": "qwen3-vl-8b", "revision": "0c35",
                                "licence": "Apache-2.0"},
                       "glm": {"id": "zai-org/GLM-4.6V-Flash", "slug": "glm-4.6v-flash", "revision": "411b"}},
            "views": views, "warnings": []}


def expected_views() -> dict:
    views = {}
    for cam, room, level in CAMERAS:
        els = []
        for idx, (pixels, box) in STATS[cam].items():
            wid = {v: k for k, v in INDEX.items()}[int(idx)]
            src = "added_by_ai" if wid in ("f_2", "dec_1") else "from_documents"
            els.append({"index": int(idx), "wenart_id": wid, "kind": "decor" if wid == "dec_1" else "furniture",
                        "type": "unknown" if wid == "f_9" else "x", "source": src,
                        "status": "unverified" if wid == "f_9" else "verified", "pixels": pixels,
                        "role": "ignore" if pixels < 60 else "required", "box_px": box})
        views[cam] = {"camera": cam, "room_id": room, "size": [W, H], "elements": els,
                      "json_crosscheck": {"level_id": level, "in_json_not_rendered": [], "rendered_not_in_json": [],
                                          "misplaced": []}}
    return {"schema_version": "0.1", "project": "toy", "views": views, "warnings": []}


def make_project(tmp_path, *, polish=True, check=True, brief="style: Scandinavian\n", pngs=True) -> Path:
    """outputs/toy with every manifest; returns the project output folder."""
    project_dir = tmp_path / "projects" / "toy"
    project_dir.mkdir(parents=True)
    if brief is not None:
        (project_dir / "brief.yaml").write_text(brief, encoding="utf-8")
    out = tmp_path / "outputs" / "toy"
    for sub in ("scene", "renders", "polish", "check", "gate"):
        (out / sub).mkdir(parents=True)
    bpath = out / "building_final.json"
    bpath.write_text(json.dumps(building(project_dir)), encoding="utf-8")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene(bpath)), encoding="utf-8")
    entries, sha = [], {}
    for i, (cam, room, _) in enumerate(CAMERAS):
        entries.append(render_entry(cam, room, i))
        rgb = np.zeros((H, W, 3), dtype=np.uint8)
        rgb[..., 0] = 40 * i
        rgb[..., 1] = 120
        if pngs:
            VW.write_png_rgb(out / "renders" / f"{cam}.png", rgb)
            sha[cam] = C.sha256_file(out / "renders" / f"{cam}.png")
        else:
            sha[cam] = "c" * 64
        Image.fromarray(rgb).save(out / "renders" / f"{cam}_preview.jpg", quality=80)
    (out / "renders" / "render_manifest.json").write_text(
        json.dumps({"schema_version": "0.1", "renders": entries, "warnings": []}), encoding="utf-8")
    if polish:
        pm = polish_manifest(sha)
        (out / "polish" / "polish_manifest.json").write_text(json.dumps(pm), encoding="utf-8")
        for v in pm["views"]:
            for a in v["attempts"]:
                rgb = np.full((H, W, 3), 200, dtype=np.uint8)
                if pngs:
                    VW.write_png_rgb(out / "polish" / a["png"], rgb)
                Image.fromarray(rgb).save(out / "polish" / f"{v['camera']}_a{a['k']}_preview.jpg", quality=80)
    if check:
        cm = check_manifest()
        pviews = {v["camera"]: v for v in polish_manifest(sha)["views"]}
        for cam, entry in cm["views"].items():
            # The check manifest records the hash of every image it checked (vision_check combine).
            entry["cycles"]["image_sha256"] = [sha[cam]]
            k = pviews[cam]["final_attempt"]
            if "polished" in entry and k is not None:
                png = out / "polish" / f"{cam}_a{k}.png"
                entry["polished"]["image_sha256"] = [C.sha256_file(png) if png.is_file() else "a" * 64]
        (out / "check" / "check_manifest.json").write_text(json.dumps(cm), encoding="utf-8")
        (out / "check" / "expected_views.json").write_text(json.dumps(expected_views()), encoding="utf-8")
        (out / "check" / "check_calibration.json").write_text(json.dumps({
            "metrics": {"fa_missing": 0.02, "fa_extra": 0.05, "models": {"qwen": {"decoy_accept": 0.0},
                                                                         "glm": {"decoy_accept": 0.2}}},
            "targets": {"fa_missing_max": 0.05, "decoy_accept_max": 0.1},
            "missed": [{"target": "decoy_accept_max", "metric": "decoy_accept[glm]", "value": 0.2, "threshold": 0.1,
                        "op": "<="}], "advisory": True, "plan_ab": {"adopted": False}}), encoding="utf-8")
        (out / "check" / "answers_qwen3-vl-8b.json").write_text(json.dumps({
            "model": "Qwen/Qwen3-VL-8B-Instruct", "slug": "qwen3-vl-8b",
            "calls": {"k1": {"latency_s": 5.0}, "k2": {"latency_s": 4.5}}}), encoding="utf-8")
        for cam in ("cam_salon_1", "cam_hol_1"):
            Image.new("RGB", (64, 48), (255, 255, 255)).save(out / "check" / f"{cam}_plan.jpg")
    return out


def by_cam(manifest):
    return {v["camera"]: v for v in manifest["views"]}


# --------------------------------------------------------------------------
# The decision rule
# --------------------------------------------------------------------------

POLISHED = {"final": "polished", "final_attempt": 2, "reason": None, "source_sha256": "s",
            "attempts": [{"k": 2, "png": "cam_a2.png", "sha256": "p", "gate": gate("accept")}]}
OK_ENTRY = check_entry({"f_1": element("E1", "required", "furniture", "sofa", "from_documents", "ok")})
# The check saw the render with sha256 "s" and the polished image with sha256 "p".
CHECK_OK = {"cycles": {**OK_ENTRY, "image_sha256": ["s"]},
            "polished": {**OK_ENTRY, "images": ["../polish/cam_a2.png"], "image_sha256": ["p"]}}


@pytest.mark.parametrize("pview, cview, kw, final, reason", [
    (POLISHED, CHECK_OK, {}, "polished", None),
    (POLISHED, CHECK_OK, {"allowed": False}, "cycles", "brief"),
    (POLISHED, CHECK_OK, {"polish_ran": False}, "cycles", "not_run"),
    (None, CHECK_OK, {}, "cycles", "not_run"),
    ({**POLISHED, "final": "cycles", "reason": "gate", "final_attempt": None}, CHECK_OK, {}, "cycles", "gate"),
    ({**POLISHED, "final": "cycles", "reason": "room"}, CHECK_OK, {}, "cycles", "room"),
    ({**POLISHED, "final": "cycles", "reason": "deadline"}, CHECK_OK, {}, "cycles", "deadline"),
    ({**POLISHED, "final": "cycles", "reason": "weird"}, CHECK_OK, {}, "cycles", "error"),
    ({**POLISHED, "final": None, "reason": None}, CHECK_OK, {}, "cycles", "not_run"),
    ({**POLISHED, "final_attempt": 9}, CHECK_OK, {}, "cycles", "error"),
    (POLISHED, CHECK_OK, {"source_sha256": "other"}, "cycles", "error"),
    (POLISHED, None, {"check_ran": False}, "cycles", "check_incomplete"),
    (POLISHED, None, {}, "cycles", "check_incomplete"),
    (POLISHED, {"cycles": OK_ENTRY}, {}, "cycles", "check_incomplete"),
    (POLISHED, {"polished": OK_ENTRY}, {}, "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "polished": {**OK_ENTRY, "not_computed": ["glm"], "verdict": "not_computed"}}, {},
     "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "polished": {**OK_ENTRY, "unreliable": ["qwen"]}}, {}, "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "cycles": {**OK_ENTRY, "unreliable": ["glm"]}}, {}, "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "polished": {**OK_ENTRY, "preference_only": True}}, {}, "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "polished": {**CHECK_OK["polished"], "images": ["../polish/cam_a1.png"]}}, {},
     "cycles", "check_incomplete"),
    # The same file name with other pixels, on either image, or no hash recorded at all.
    (POLISHED, {**CHECK_OK, "polished": {**CHECK_OK["polished"], "image_sha256": ["old"]}}, {}, "cycles",
     "check_incomplete"),
    (POLISHED, {**CHECK_OK, "cycles": {**OK_ENTRY, "image_sha256": ["old"]}}, {}, "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "polished": {**OK_ENTRY, "images": ["../polish/cam_a2.png"]}}, {}, "cycles",
     "check_incomplete"),
    (POLISHED, {**CHECK_OK, "cycles": OK_ENTRY}, {}, "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "cycles": OK_ENTRY}, {"source_sha256": None}, "polished", None),
    (POLISHED, {**CHECK_OK, "polished_rejected": True, "polished_reason": "vision_check"}, {}, "cycles",
     "vision_check"),
    (POLISHED, {**CHECK_OK, "polished_rejected": True, "polished_reasons": [{"reason": "check_incomplete"}]}, {},
     "cycles", "check_incomplete"),
    (POLISHED, {**CHECK_OK, "polished_rejected": True, "polished_reasons": [{"reason": "vision_check",
                                                                             "what": "added_by_polish"}]}, {},
     "cycles", "vision_check"),
])
def test_decide_rule_table(pview, cview, kw, final, reason):
    args = {"polish_ran": True, "check_ran": True, "allowed": True, "source_sha256": "s", **kw}
    out = F.decide(pview, cview, **args)
    assert (out["final"], out["reason"]) == (final, reason), out
    assert out["final"] == "cycles" or out["detail"] is None


def test_decide_recomputes_the_differential_rule():
    lost = copy.deepcopy(CHECK_OK["polished"])                   # the check saw the polished image "p"
    lost["elements"]["f_1"]["result"] = "missing_or_changed"
    out = F.decide(POLISHED, {"cycles": OK_ENTRY, "polished": lost}, polish_ran=True, check_ran=True)
    assert out["reason"] == "vision_check" and "did not flag" in out["detail"] and "f_1" in out["detail"]
    # Missing on both images is a Cycles mismatch (needs review), not a polish loss.
    both = {"cycles": lost, "polished": lost}
    assert F.decide(POLISHED, both, polish_ran=True, check_ran=True)["final"] == "polished"
    # Unverified on Cycles, confirmed changed on the polished image: rejected.
    unv = copy.deepcopy(OK_ENTRY)
    unv["elements"]["f_1"]["result"] = "unverified"
    assert F.decide(POLISHED, {"cycles": unv, "polished": lost}, polish_ran=True,
                    check_ran=True)["reason"] == "vision_check"


def test_decide_checks_the_polished_file(tmp_path):
    out = F.decide(POLISHED, CHECK_OK, polish_ran=True, check_ran=True, polish_dir=tmp_path)
    assert out["reason"] == "error" and "not found" in out["detail"]
    (tmp_path / "cam_a2.png").write_bytes(b"x")
    # The file on disk is hashed (not the manifest's sha256 "p"): it is not what the check saw.
    out = F.decide(POLISHED, CHECK_OK, polish_ran=True, check_ran=True, polish_dir=tmp_path)
    assert out["reason"] == "check_incomplete" and "sha256 differs" in out["detail"]
    seen = {**CHECK_OK, "polished": {**CHECK_OK["polished"], "image_sha256": [C.sha256_file(tmp_path / "cam_a2.png")]}}
    assert F.decide(POLISHED, seen, polish_ran=True, check_ran=True, polish_dir=tmp_path)["final"] == "polished"


# --------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------

def links(md: str) -> list[str]:
    return re.findall(r"\]\(([^)]+)\)", md)


def test_final_report_end_to_end(tmp_path):
    out = make_project(tmp_path)
    assert report_main(["final", "--project-out", str(out)]) == 0
    final = out / "final"
    manifest = json.loads((final / "final_manifest.json").read_text(encoding="utf-8"))
    assert F.validate_final_manifest(manifest) == []
    v = by_cam(manifest)
    assert [x["camera"] for x in manifest["views"]] == [c for c, _, _ in CAMERAS]
    assert (v["cam_salon_1"]["final"], v["cam_salon_1"]["reason"]) == ("polished", None)
    assert v["cam_salon_1"]["image"] == "../polish/cam_salon_1_a1.png"
    assert (v["cam_salon_2"]["final"], v["cam_salon_2"]["reason"]) == ("cycles", "vision_check")
    assert v["cam_salon_2"]["image"] == "../renders/cam_salon_2.png"
    assert (v["cam_hol_1"]["final"], v["cam_hol_1"]["reason"]) == ("cycles", "gate")
    assert "no ladder attempt passed the gate" in v["cam_hol_1"]["detail"]
    assert (v["cam_yatak_1"]["final"], v["cam_yatak_1"]["reason"]) == ("cycles", "check_incomplete")
    assert (v["cam_yatak_2"]["final"], v["cam_yatak_2"]["reason"]) == ("cycles", "vision_check")
    s = manifest["summary"]
    assert s["views"] == 5 and s["polished"] == 1 and s["cycles"] == 4
    assert s["cycles_by_reason"] == {"check_incomplete": 1, "gate": 1, "vision_check": 2}
    assert s["needs_review"] == 1 and v["cam_hol_1"]["needs_review"]
    assert s["exposure"]["min"] == 0.5 and s["exposure"]["max"] == 8.0 and s["exposure"]["at_limit"] == 1
    assert s["seconds"] == {"build": 36.4, "render": 60.0, "meter": 10.0, "polish": 90.0, "gate": 20.0, "check": 9.5}
    # Settings and gate summary of the chosen attempt; check verdicts of both images; preference.
    a = v["cam_salon_2"]["attempt"]
    assert a["k"] == 2 and a["strength"] == 0.25 and a["control"] == "depth" and a["png"] == "cam_salon_2_a2.png"
    assert v["cam_salon_2"]["gate"]["decision"] == "accept" and v["cam_salon_2"]["gate"]["global"]["edges"] == 0.99
    vc = v["cam_salon_2"]["vision_check"]
    assert vc["cycles"]["verdict"] == "ok" and vc["polished"]["verdict"] == "mismatch" and vc["polished_rejected"]
    assert v["cam_salon_1"]["preference"]["preferred"] is True
    assert v["cam_hol_1"]["attempt"] is None and v["cam_hol_1"]["vision_check"]["polished"] is None
    # Ids per source, unverified pieces in view (ignored slivers left out).
    assert v["cam_salon_1"]["ids_by_source"] == {"added_by_ai": ["f_2"], "from_documents": ["d_1", "f_1", "win_1"]}
    assert v["cam_hol_1"]["unverified"] == ["f_9"] and v["cam_salon_1"]["unverified"] == []
    # Mismatches with source and evidence; the added_by_ai note; never fixed.
    hol = {(m["what"], m["id"] or m["type"]): m for m in v["cam_hol_1"]["mismatches"]}
    door = hol[("element", "d_1")]
    assert door["result"] == "missing" and "KAPI INSERT:F4 vector 1.00" in door["evidence"]
    assert hol[("extra", "armchair")]["kind"] == "furniture"
    assert hol[("crosscheck", "f_9")]["result"] == "in_json_not_rendered"
    assert v["cam_hol_1"]["final_mismatches"] == 2                 # door missing + confirmed extra
    sal2 = [m for m in v["cam_salon_2"]["mismatches"] if m["image"] == "polished"]
    assert sal2[0]["id"] == "f_1" and sal2[0]["evidence"].startswith("plan.dxf MOBILYA INSERT:1A")
    # Rooms mixing polished and Cycles; building unverified/conflicts; models and licences.
    assert manifest["rooms_mixed"] == ["r_L0_salon"] and manifest["rooms"]["r_L1_yatak"]["polish_rule"] == "downgraded"
    assert manifest["building"]["unverified"] == ["f_9"] and manifest["building"]["conflicts"][0]["id"] == "c_001"
    roles = {m["role"]: m for m in manifest["models"]}
    assert set(roles) == {"polish base", "polish controlnet", "gate depth", "gate sam", "gate dino", "check qwen",
                          "check glm"}
    assert roles["check glm"]["licence"] == "MIT"                   # filled from check.yaml
    assert manifest["assets"] == {"textures": {"CC0": 2}, "models": {"CC0": 2}}
    assert any("decoy_accept[glm]" in f for f in manifest["advisory_flags"])
    assert any("not calibrated" in f for f in manifest["advisory_flags"])
    assert manifest["advisory"] is True and manifest["stages"]["check"] == "run"
    # Files: previews, plan copies, contact sheets, all <= 300 KB.
    for x in manifest["views"]:
        assert x["preview"] == f"{x['camera']}_final_preview.jpg" and (final / x["preview"]).is_file()
    assert v["cam_salon_1"]["plan"] == "cam_salon_1_plan.jpg" and v["cam_salon_2"]["plan"] is None
    assert manifest["contact_sheets"] == {"L0": "contact_L0.jpg", "L1": "contact_L1.jpg"}
    for f in final.glob("*.jpg"):
        assert f.stat().st_size <= 300_000
    with Image.open(final / "contact_L0.jpg") as im:
        assert im.width == 3 * 480 + 4 * 4                         # 3 views on L0, 480 px tiles
    # The polished preview shows the polished image, the Cycles one the render.
    assert VW.read_rgb(final / "cam_salon_1_final_preview.jpg")[..., 0].mean() > 150
    assert VW.read_rgb(final / "cam_hol_1_final_preview.jpg")[..., 0].mean() == pytest.approx(80, abs=8)
    # The report: every table, links only to files in final/ that exist.
    md = (final / "final_report.md").read_text(encoding="utf-8")
    assert "| A1 D3 |" not in md and "| D3 A1 |" in md
    for heading in ("# Final report: toy", "## Summary", "## Advisory flags and open items", "## Views",
                    "## Mismatches (never auto-fixed)", "## Needs review",
                    "## Building JSON: unverified items and conflicts", "## Rooms mixing polished and Cycles views",
                    "## Models and licences", "## Contact sheets"):
        assert heading in md, heading
    assert links(md) and all("/" not in l and (final / l).is_file() for l in links(md))
    assert "| cam_salon_2 | r_L0_salon | L0 | cycles | vision_check |" in md
    assert "added_by_ai: render/polish issue, not a document conflict" not in md or "f_2" in md
    assert "c_001" in md and "Qwen/Qwen3-VL-8B-Instruct" in md and "Apache-2.0" in md
    assert "r_L0_salon" in md.split("## Rooms mixing polished and Cycles views")[1]


def test_a_polished_image_the_check_did_not_see_is_not_final(tmp_path):
    """Re-polished under the same attempt name (new pixels) while the old check manifest stays: the check
    never saw this image, so it cannot be final (§5.5, §7: the check checked that very image)."""
    out = make_project(tmp_path)
    assert (by_cam(F.write_final(out))["cam_salon_1"]["final"]) == "polished"
    png = out / "polish" / "cam_salon_1_a1.png"
    rgb = VW.read_rgb(png)
    rgb[: H // 2] = 0
    VW.write_png_rgb(png, rgb)
    pm = json.loads((out / "polish" / "polish_manifest.json").read_text(encoding="utf-8"))
    pm["views"][0]["attempts"][0]["sha256"] = C.sha256_file(png)
    (out / "polish" / "polish_manifest.json").write_text(json.dumps(pm), encoding="utf-8")
    v = by_cam(F.write_final(out))["cam_salon_1"]
    assert (v["final"], v["reason"]) == ("cycles", "check_incomplete") and "sha256" in v["detail"]
    assert v["image"] == "../renders/cam_salon_1.png"
    # A check manifest without image hashes (written before they were recorded) cannot vouch for an image.
    cm = json.loads((out / "check" / "check_manifest.json").read_text(encoding="utf-8"))
    cm["views"]["cam_salon_1"]["polished"]["image_sha256"] = [C.sha256_file(png)]
    del cm["views"]["cam_salon_1"]["cycles"]["image_sha256"]
    (out / "check" / "check_manifest.json").write_text(json.dumps(cm), encoding="utf-8")
    v = by_cam(F.write_final(out))["cam_salon_1"]
    assert (v["final"], v["reason"]) == ("cycles", "check_incomplete") and "re-run" in v["detail"]
    cm["views"]["cam_salon_1"]["cycles"]["image_sha256"] = [C.sha256_file(out / "renders" / "cam_salon_1.png")]
    (out / "check" / "check_manifest.json").write_text(json.dumps(cm), encoding="utf-8")
    assert by_cam(F.write_final(out))["cam_salon_1"]["final"] == "polished"


def test_rerun_is_stable_and_lists_stale_files(tmp_path):
    out = make_project(tmp_path)
    F.write_final(out)
    first = (out / "final" / "final_manifest.json").read_text(encoding="utf-8")
    F.write_final(out)
    assert (out / "final" / "final_manifest.json").read_text(encoding="utf-8") == first
    (out / "final" / "cam_gone_final_preview.jpg").write_bytes(b"x")
    manifest = F.write_final(out)
    assert (out / "final" / "cam_gone_final_preview.jpg").is_file()          # listed, never deleted
    assert any("cam_gone_final_preview.jpg is from an earlier run" in w for w in manifest["warnings"])


def test_crosscheck_error_is_reported(tmp_path):
    out = make_project(tmp_path)
    cm = json.loads((out / "check" / "check_manifest.json").read_text(encoding="utf-8"))
    cm["views"]["cam_salon_1"]["json_crosscheck"] = {"error": "camera not in the scene manifest"}
    (out / "check" / "check_manifest.json").write_text(json.dumps(cm), encoding="utf-8")
    manifest = F.write_final(out)
    assert "cam_salon_1: JSON cross-check not computed (camera not in the scene manifest)" in manifest["warnings"]


def test_added_by_ai_mismatch_is_labelled(tmp_path):
    out = make_project(tmp_path)
    cm = json.loads((out / "check" / "check_manifest.json").read_text(encoding="utf-8"))
    cm["views"]["cam_salon_1"]["cycles"]["elements"]["f_2"]["result"] = "changed"
    (out / "check" / "check_manifest.json").write_text(json.dumps(cm), encoding="utf-8")
    manifest = F.write_final(out)
    item = next(m for m in by_cam(manifest)["cam_salon_1"]["mismatches"] if m["id"] == "f_2")
    assert F.ADDED_BY_AI_NOTE in item["notes"] and item["source"] == "added_by_ai"
    assert "layout ai" in item["evidence"]
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert F.ADDED_BY_AI_NOTE in md


def test_no_check_manifest_keeps_cycles_and_says_not_run(tmp_path):
    out = make_project(tmp_path, check=False)
    manifest = F.write_final(out)
    v = by_cam(manifest)
    assert all(x["final"] == "cycles" for x in manifest["views"])
    assert v["cam_salon_1"]["reason"] == "check_incomplete" and v["cam_salon_1"]["detail"] == "vision check not run"
    assert v["cam_hol_1"]["reason"] == "gate"
    assert manifest["stages"]["check"] == "not_run" and manifest["stages"]["expected"] == "not_run"
    assert any("vision check not run" in f for f in manifest["advisory_flags"])
    # Without the expected lists the ids come from the render's index statistics.
    assert v["cam_salon_1"]["ids_by_source"] == {"added_by_ai": ["dec_1", "f_2"],
                                                 "from_documents": ["d_1", "f_1", "win_1"]}
    assert v["cam_hol_1"]["unverified"] == ["f_9"]
    assert all(x["plan"] is None and x["vision_check"] is None for x in manifest["views"])
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "vision check not run" in md and "| check Cycles |" in md and "not run" in md
    assert "Not computed: the vision check and the expected lists did not run." in md


def test_no_polish_manifest(tmp_path):
    out = make_project(tmp_path, polish=False)
    manifest = F.write_final(out)
    assert {x["reason"] for x in manifest["views"]} == {"not_run"}
    assert manifest["stages"]["polish"] == "not_run" and manifest["models"][0]["role"] == "check qwen"
    assert "polish not run (every view is the Cycles render)" in manifest["advisory_flags"]
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "polish not run" in md


def test_brief_polish_false_wins(tmp_path):
    out = make_project(tmp_path, brief="style: Scandinavian\npolish: false\n")
    manifest = F.write_final(out)
    assert {(x["final"], x["reason"]) for x in manifest["views"]} == {("cycles", "brief")}
    assert manifest["polish_allowed"] is False
    assert any("brief polish: false" in f for f in manifest["advisory_flags"])


def test_missing_brief_is_assumed(tmp_path):
    out = make_project(tmp_path, brief=None)
    manifest = F.write_final(out)
    assert manifest["polish_allowed"] is True and "polish" in manifest["brief_assumed"]
    assert "(default, not in brief.yaml)" in (out / "final" / "final_report.md").read_text(encoding="utf-8")


def test_results_copy_without_pngs_uses_previews(tmp_path):
    """A results/ copy has no PNGs: previews come from the committed JPEGs and the decision says why."""
    out = make_project(tmp_path, pngs=False)
    manifest = F.write_final(out)
    v = by_cam(manifest)
    assert v["cam_salon_1"]["reason"] == "error" and "not found" in v["cam_salon_1"]["detail"]
    assert all(x["preview"] for x in manifest["views"])
    assert any("preview made from" in w for w in manifest["warnings"])


def test_stale_polish_and_unknown_polish_kind(tmp_path):
    out = make_project(tmp_path)
    VW.write_png_rgb(out / "renders" / "cam_salon_1.png", np.zeros((H, W, 3), dtype=np.uint8))
    manifest = F.write_final(out)
    assert "another render" in by_cam(manifest)["cam_salon_1"]["detail"]
    pm = json.loads((out / "polish" / "polish_manifest.json").read_text(encoding="utf-8"))
    pm["kind"] = "smoke"
    (out / "polish" / "polish_manifest.json").write_text(json.dumps(pm), encoding="utf-8")
    manifest = F.write_final(out)
    assert manifest["stages"]["polish"] == "not_run" and any("'smoke'" in w for w in manifest["warnings"])


def test_broken_and_missing_inputs(tmp_path):
    out = make_project(tmp_path)
    (out / "check" / "check_manifest.json").write_text("{broken", encoding="utf-8")
    (out / "scene" / "scene_manifest.json").unlink()
    manifest = F.write_final(out)
    assert manifest["stages"]["check"] == "not_run"
    assert any("check_manifest.json: unreadable" in w for w in manifest["warnings"])
    assert any("scene/scene_manifest.json not readable" in w for w in manifest["warnings"])
    assert manifest["building"]["unverified"] == []                  # no building without the scene manifest
    assert [x["level_id"] for x in manifest["views"]] == [l for _, _, l in CAMERAS]   # from the expected lists
    (out / "check" / "expected_views.json").unlink()
    manifest = F.write_final(out)
    assert all(x["level_id"] == "unknown" for x in manifest["views"])
    assert manifest["contact_sheets"] == {"unknown": "contact_unknown.jpg"}
    (out / "renders" / "render_manifest.json").unlink()
    assert report_main(["final", "--project-out", str(out)]) == 1     # nothing rendered: the stage failed
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "render_manifest.json not found" in md
    assert report_main(["final", "--project-out", str(tmp_path / "nope")]) == 2


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------

def noise(h, w, seed=0):
    return np.random.default_rng(seed).integers(0, 256, size=(h, w, 3), dtype=np.uint8)


def test_save_jpeg_under_steps_quality_then_size(tmp_path):
    info = C.save_jpeg_under(noise(1080, 1920), tmp_path / "a.jpg")
    assert (tmp_path / "a.jpg").stat().st_size == info["bytes"] <= 300_000
    assert info["quality"] < 88 or info["scale"] < 1.0
    small = C.save_jpeg_under(np.full((50, 80, 3), 7, dtype=np.uint8), tmp_path / "b.jpg")
    assert small["quality"] == 88 and small["scale"] == 1.0 and small["size"] == [80, 50]
    with pytest.raises(ValueError):
        C.save_jpeg_under(noise(200, 200), tmp_path / "c.jpg", max_bytes=100)


def test_contact_sheet_size_and_labels(tmp_path):
    tiles = [(f"cam_{i}  {'P' if i % 2 else 'C'}  U{i % 3}", Image.fromarray(noise(540, 960, i))) for i in range(10)]
    sheet = F.contact_sheet(tiles)
    assert sheet.width == 4 * 480 + 5 * 4 and sheet.height == 3 * (270 + F.LABEL_HEIGHT) + 4 * 4
    label_strip = np.asarray(sheet)[4 + 270: 4 + 270 + F.LABEL_HEIGHT, 4:484]
    assert label_strip.max() == 255 and np.median(label_strip) == 0      # white text on black
    info = C.save_jpeg_under(sheet, tmp_path / "contact.jpg")
    assert (tmp_path / "contact.jpg").stat().st_size <= 300_000 and info["bytes"] <= 300_000
    assert F.tile_label({"camera": "cam_x", "final": "polished", "unverified": ["a", "b"]}) == "cam_x  P  U2"


# --------------------------------------------------------------------------
# Sweep report
# --------------------------------------------------------------------------

def sweep_manifest() -> dict:
    grid = [(1, "grid", 0.125, "depth", "native", "plain"), (2, "grid", 0.375, "depth", "native", "plain"),
            (3, "grid", 0.375, "canny", "native", "plain"), (4, "grid", 0.375, "depth", "1536x864", "anchor"),
            (5, "presumed_bad", 0.75, None, "native", "plain")]
    views = []
    for cam in ("cam_salon_1", "cam_yatak_1"):
        atts = []
        for k, role, strength, control, size, mode in grid:
            ok = strength <= 0.375 and not (control == "canny" and cam == "cam_yatak_1")
            a = attempt(cam, k, "accept" if ok else "reject", [] if ok else ["edges", "depth"], strength=strength)
            a.update(role=role, control=control, size=size, mode=mode, scale=None if control is None else 0.8)
            atts.append(a)
        views.append({"camera": cam, "room_id": "r", "attempts": atts, "final": None, "final_attempt": None,
                      "reason": None})
    views[1]["attempts"][1]["error"] = "CUDA out of memory"
    views[1]["attempts"][1]["gate"] = None
    return {"schema_version": "0.1", "kind": "sweep", "project": "toy", "incomplete": False, "views": views,
            "config": {"ladder": [{"strength": 0.375, "control": "depth", "scale": 0.8, "size": "native",
                                   "mode": "plain"}]},
            "thresholds": {"edges": {"hard": True, "global_min": 0.95, "region_min": 0.85}}, "warnings": ["w1"]}


def gate_calibration() -> dict:
    return {"benign": [{"camera": "c1", "control": "jpeg", "magnitude": 75, "decision": "accept", "reasons": []},
                       {"camera": "c1", "control": "blur", "magnitude": 1, "decision": "reject",
                        "reasons": [{"check": "edges"}]}],
            "negative": [{"camera": "c1", "control": "shift", "magnitude": 6, "decision": "accept", "reasons": []},
                         {"camera": "c1", "control": "shift", "magnitude": 25, "decision": "reject",
                          "reasons": [{"check": "edges"}]}],
            "presumed_bad": [{"camera": "c1", "control": "sweep:a5", "magnitude": 0.75, "decision": "reject"}],
            "rates": {"benign_accept": 0.5, "negative_reject": 0.5, "by_control": {"shift": {"n": 2, "rate": 0.5}}},
            "per_metric": {"edges": {"worst_benign": 0.96, "best_small_negative": 0.9, "best_negative": 0.6,
                                     "separates": True, "proposed": 0.945}},
            "smallest_detected": {"shift_px": 12, "scale": 1.08}, "explanations": ["blur softens edges"]}


def test_sweep_report(tmp_path):
    out = make_project(tmp_path)
    (out / "polish" / "sweep").mkdir()
    (out / "polish" / "sweep" / "polish_manifest.json").write_text(json.dumps(sweep_manifest()), encoding="utf-8")
    (out / "gate" / "gate_calibration.json").write_text(json.dumps(gate_calibration()), encoding="utf-8")
    cm = json.loads((out / "check" / "check_manifest.json").read_text(encoding="utf-8"))
    cm["views"]["cam_salon_1"]["sweep:a2"] = {"verdict": "info", "preference_only": True,
                                              "preference": {"preferred": True}}
    (out / "check" / "check_manifest.json").write_text(json.dumps(cm), encoding="utf-8")
    assert report_main(["sweep", "--project-out", str(out)]) == 0
    md = (out / "final" / "sweep_report.md").read_text(encoding="utf-8")
    rows = S.sweep_settings(sweep_manifest(), cm)
    assert [r["label"] for r in rows] == ["s 0.125 depth x0.8", "s 0.375 depth x0.8", "s 0.375 canny x0.8",
                                          "s 0.375 depth x0.8 1536x864 anchor", "s 0.75 no control [presumed_bad]"]
    assert rows[0]["rate"] == 1.0 and rows[1]["gated"] == 1 and rows[1]["errors"] == 1
    assert rows[2]["accepted"] == 1 and rows[2]["failing"] == {"depth": 1, "edges": 1}
    assert rows[1]["preferred"] == 1 and rows[1]["preference_asked"] == 1
    assert rows[4]["rate"] == 0.0 and rows[0]["medians"]["edges"] == 0.99
    assert [r["label"] for r in S.candidate_ladder(rows)] == [
        "s 0.375 depth x0.8", "s 0.375 depth x0.8 1536x864 anchor", "s 0.125 depth x0.8"]
    for text in ("# Sweep report: toy", "## Polish sweep", "### Decisions per view", "## Gate calibration",
                 "## Vision-check calibration", "| cam_yatak_1 | A | err | R (depth, edges) | A |",
                 "Current ladder (polish.yaml)",
                 "benign accepted | 50 %", "c1: blur 1 -> reject (edges)", "c1: shift 6 -> accept",
                 "shift_px 12", "blur softens edges", "| edges | 0.960 | 0.900 | 0.600 | yes | 0.945 |",
                 "global_min 0.950", "decoy_accept", "MISSED", "Plan A/B: not adopted", "sweep: w1"):
        assert text in md, text


def test_sweep_report_says_whether_the_plan_crop_is_used_not_only_favoured():
    from wenart.vision_check import calibrate as CAL
    cases = [({"favours_plan": True, "used": False, "adopted": False, "text": CAL.FAVOURS_TEXT},
              "Plan A/B: favours the plan crop, not adopted (check.yaml plan_image: false): A/B favours the plan "
              "crop: set plan_image: true to adopt."),
             ({"favours_plan": True, "used": True, "adopted": True, "text": CAL.USED_TEXT},
              "Plan A/B: used (check.yaml plan_image: true)"),
             # Written before plan_image existed: "adopted" meant only that the A/B favoured the crop.
             ({"adopted": True, "text": "source-plan crop adopted as Image 2 of the element check"},
              "Plan A/B: favours the plan crop, not adopted")]
    for pab, line in cases:
        md = S.report_markdown("toy", None, None, {"metrics": {}, "targets": {}, "missed": [], "plan_ab": pab})
        assert line in md, md


def test_sweep_report_reads_the_ladder_from_polish_yaml_when_the_manifest_has_none(tmp_path):
    sweep = sweep_manifest()
    sweep["config"] = {}
    md = S.report_markdown("toy", sweep, None, None)
    from wenart.polish.config import load_config
    rungs = "; ".join(f"s {a['strength']} {a['control']} x{a['scale']}" for a in load_config()["ladder"])
    assert f"Current ladder (polish.yaml): {rungs}." in md


def test_broken_brief_does_not_stop_the_report(tmp_path):
    out = make_project(tmp_path, brief="style: [unclosed\n")
    manifest = F.write_final(out)
    assert any(w.startswith("project inputs not fully readable (ParserError") for w in manifest["warnings"])
    assert manifest["polish_allowed"] is True and manifest["summary"]["views"] == 5
    # The scene manifest and the building are still read directly.
    assert manifest["building"]["unverified"] == ["f_9"] and by_cam(manifest)["cam_yatak_1"]["level_id"] == "L1"


def test_sweep_report_with_nothing_run(tmp_path):
    out = tmp_path / "outputs" / "toy"
    out.mkdir(parents=True)
    path = S.write_sweep(out)
    md = path.read_text(encoding="utf-8")
    assert path == out / "final" / "sweep_report.md"
    assert md.count("Not run (") == 3 and "# Sweep report: toy" in md


# --------------------------------------------------------------------------
# Milestone 6 (docs/milestone6.md §7.4): gate validation, cameras, stages, private projects, needs review
# --------------------------------------------------------------------------

def write_json(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def gate_validation(out: Path, decision: str, sha256=None, reasons=None) -> Path:
    return write_json(out / "gate" / "gate_validation.json", {
        "schema_version": "0.1", "kind": "gate_validation", "project": "toy", "decision": decision,
        "benign_accept": 0.9 if decision == "flagged" else 1.0,
        "negative_reject": 0.8 if decision == "polish_disabled" else 0.95, "n_benign": 64, "n_negative": 170,
        "pass_benign": decision != "flagged", "pass_negative": decision != "polish_disabled",
        "reasons": [] if reasons is None else reasons,
        "limits": {"benign_accept_min": 0.95, "negative_reject_min": 0.9},
        "polish_allowed": decision in ("ok", "flagged"),
        "calibration": {"path": "gate_calibration.json", "sha256": sha256, "incomplete": False,
                        "thresholds_match": True}})


def stage_record(out: Path, stage: str, status: str, started: str, seconds=1.0, note=None, **extra) -> Path:
    return write_json(out / "run" / f"{stage}.json", {
        "schema_version": "0.1", "kind": "stage_record", "project": out.name, "stage": stage, "rc": 0,
        "status": status, "seconds": seconds, "fingerprint": "f" * 64, "inputs": {"/x/secret.pdf": "a" * 64},
        "outputs": [], "started_utc": started, "git_commit": "abc", "log": f"logs/{stage}.log", "note": note,
        **extra})


@pytest.mark.parametrize("decision", ["polish_disabled", "not_validated"])
def test_gate_validation_without_polish_gives_cycles_finals(tmp_path, decision):
    out = make_project(tmp_path)
    gate_validation(out, decision, reasons=["negative controls rejected 0.800 < 0.90"])
    manifest = F.write_final(out)
    assert F.validate_final_manifest(manifest) == []
    assert {(v["final"], v["reason"]) for v in manifest["views"]} == {("cycles", "gate_validation")}
    assert manifest["summary"]["cycles_by_reason"] == {"gate_validation": 5}
    assert manifest["stages"]["gate_validation"] == decision
    g = manifest["gate_validation"]
    assert g["decision"] == decision and g["polish_allowed"] is False and "Cycles render" in g["effect"]
    assert any(f.startswith(f"gate validation {decision}: no polish") and "0.800" in f
               for f in manifest["advisory_flags"])
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "## Gate validation" in md and f"| decision | {decision} |" in md
    assert "| negative controls rejected |" in md and "(limit 90 %)" in md
    assert VW.read_rgb(out / "final" / "cam_salon_1_final_preview.jpg")[..., 0].mean() < 150   # the render


def test_gate_validation_ok_and_flagged_keep_the_polish(tmp_path):
    out = make_project(tmp_path)
    gate_validation(out, "ok")
    manifest = F.write_final(out)
    assert by_cam(manifest)["cam_salon_1"]["final"] == "polished"
    assert not any("gate validation" in f for f in manifest["advisory_flags"])
    gate_validation(out, "flagged", reasons=["benign controls accepted 0.900 < 0.95"])
    manifest = F.write_final(out)
    assert by_cam(manifest)["cam_salon_1"]["final"] == "polished"
    assert any(f.startswith("gate validation flagged: polish ran") for f in manifest["advisory_flags"])
    assert "| decision | flagged |" in (out / "final" / "final_report.md").read_text(encoding="utf-8")


def test_gate_validation_older_than_the_calibration_is_not_validated(tmp_path):
    out = make_project(tmp_path)
    cal = write_json(out / "gate" / "gate_calibration.json", {"benign": [], "negative": [], "rates": {}})
    from wenart.canonical import canonical_sha256
    gate_validation(out, "ok", sha256=canonical_sha256(cal))
    assert by_cam(F.write_final(out))["cam_salon_1"]["final"] == "polished"
    write_json(cal, {"benign": [], "negative": [], "rates": {}, "incomplete": True})     # re-calibrated
    manifest = F.write_final(out)
    g = manifest["gate_validation"]
    assert g["decision"] == "not_validated" and g["recorded_decision"] == "ok"
    assert "changed after the validation" in g["reasons"][-1]
    assert {v["reason"] for v in manifest["views"]} == {"gate_validation"}
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| decision | not_validated (recorded ok) |" in md


def test_gate_validation_not_recorded_and_brief_wins(tmp_path):
    out = make_project(tmp_path)
    manifest = F.write_final(out)
    assert manifest["gate_validation"] is None and manifest["stages"]["gate_validation"] == "not_run"
    assert any(f.startswith("gate validation not recorded") for f in manifest["advisory_flags"])
    assert "Not recorded (`gate/gate_validation.json` missing)" in \
        (out / "final" / "final_report.md").read_text(encoding="utf-8")
    out2 = make_project(tmp_path / "b", brief="style: x\npolish: false\n")
    gate_validation(out2, "polish_disabled")
    manifest = F.write_final(out2)
    assert {v["reason"] for v in manifest["views"]} == {"brief"}
    assert not any(f.startswith("gate validation not recorded") for f in manifest["advisory_flags"])


def test_decide_gate_decision_rule():
    args = {"polish_ran": True, "check_ran": True, "allowed": True, "source_sha256": "s"}
    for decision in ("polish_disabled", "not_validated"):
        out = F.decide(POLISHED, CHECK_OK, gate_decision=decision, **args)
        assert (out["final"], out["reason"]) == ("cycles", "gate_validation") and decision in out["detail"]
    for decision in (None, "ok", "flagged"):
        assert F.decide(POLISHED, CHECK_OK, gate_decision=decision, **args)["final"] == "polished"
    assert F.decide(POLISHED, CHECK_OK, gate_decision="not_validated", **{**args, "allowed": False})["reason"] == \
        "brief"


def test_cameras_window_pull_and_views_per_room(tmp_path):
    out = make_project(tmp_path)
    scene_path = out / "scene" / "scene_manifest.json"
    sc = json.loads(scene_path.read_text(encoding="utf-8"))
    for i, cam in enumerate(sc["cameras"]):
        cam.update(policy="search", shift_x=0.0, shift_y=-0.1, placement="search",
                   score={"total": 3.0 + i / 10, "furniture": 0.5, "openings": 0.1, "floor": 0.2, "depth": 0.9,
                          "penalties": 0.0, "blocked": i == 4},
                   warning="blocked unavoidable" if i == 4 else None)
    scene_path.write_text(json.dumps(sc), encoding="utf-8")
    rm_path = out / "renders" / "render_manifest.json"
    rm = json.loads(rm_path.read_text(encoding="utf-8"))
    rm["renders"][0]["window_pull"] = {"ev": 2, "clip_before": 0.2, "clip_after": 0.01, "pane_px": 900}
    rm["renders"][1]["window_pull"] = None
    rm_path.write_text(json.dumps(rm), encoding="utf-8")
    b_path = out / "building_final.json"
    b = json.loads(b_path.read_text(encoding="utf-8"))
    b["rooms"].append({"id": "r_L1_bos", "level_id": "L1", "room_type": "other", "status": "verified"})
    b_path.write_text(json.dumps(b), encoding="utf-8")
    manifest = F.write_final(out)
    v = by_cam(manifest)
    cp = v["cam_salon_1"]["camera_plan"]
    assert cp["policy"] == "search" and cp["score_total"] == 3.0 and cp["shift_y"] == -0.1
    assert v["cam_salon_1"]["window_pull"]["ev"] == 2 and v["cam_salon_2"]["window_pull"] is None
    s = manifest["summary"]
    assert s["cameras"]["policies"] == {"search": 5} and s["cameras"]["score_max"] == 3.4
    assert s["cameras"]["warnings"] == ["cam_yatak_2: blocked unavoidable"]
    assert s["exposure"]["window_pull"] == {"views": 1, "min": 2.0, "max": 2.0}
    assert s["views_per_room"] == {"0": 1, "1": 1, "2": 2}
    assert manifest["rooms"]["r_L1_bos"]["views"] == [] and manifest["rooms"]["r_L0_salon"]["room_type"] == "living"
    assert "camera cam_yatak_2: blocked unavoidable" in manifest["advisory_flags"]
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| EV | pull EV | camera |" in md and "| search 3.00 |" in md and "| search 3.40 blocked |" in md
    assert "## Views per room" in md and "Rooms without a rendered view: r_L1_bos." in md
    assert "| camera policy | search 5 |" in md and "| window pull | 1 view(s), 2 .. 2 EV |" in md
    # M5 manifests carry no policy: their cameras are the m5 rules.
    out2 = make_project(tmp_path / "m5")
    assert by_cam(F.write_final(out2))["cam_salon_1"]["camera_plan"]["policy"] == "m5"


def test_stage_table_from_run_records(tmp_path):
    out = make_project(tmp_path)
    stage_record(out, "render", "ok", "2026-10-02T10:05:00Z", seconds=300.0)
    stage_record(out, "pipeline", "reused", "2026-10-02T10:00:00Z", seconds=0.1)
    stage_record(out, "photos", "skipped", "2026-10-02T10:01:00Z", seconds=0, note="no style photos")
    stage_record(out, "report", "ok", "2026-10-02T09:00:00Z")                    # an earlier report: left out
    write_json(out / "run" / "other.json", {"kind": "something_else", "status": "ok"})
    (out / "run" / "broken.json").write_text("{", encoding="utf-8")
    manifest = F.write_final(out)
    assert [r["stage"] for r in manifest["run_stages"]] == ["pipeline", "photos", "render"]
    assert manifest["run_stages"][1]["note"] == "no style photos" and "inputs" not in manifest["run_stages"][0]
    assert any("broken.json: unreadable" in w for w in manifest["warnings"])
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "## Stages" in md and "| photos | skipped | 0.0 s | no style photos |" in md
    assert "| render | ok | 5.0 min | - |" in md and "secret.pdf" not in md


def test_private_project_never_copies_plan_crops(tmp_path):
    out = make_project(tmp_path)
    write_json(out / "intake_manifest.json", {
        "kind": "intake_manifest", "alias": "real-01", "status": "ok", "reasons": [],
        "totals": {"files": 4, "kept": 3, "skipped": 1, "documents": 2, "style_photos": 1, "notes": 0},
        "skipped_by_reason": {"junk (system metadata file)": 1},
        "files": [{"path": "Gizli Villa Bodrum.pdf", "kept": True}]})
    manifest = F.write_final(out)
    final = out / "final"
    assert manifest["private"] is True
    assert not list(final.glob("*_plan.jpg"))
    v = by_cam(manifest)
    assert v["cam_salon_1"]["plan"] is None and v["cam_salon_1"]["plan_kept"] == "check/cam_salon_1_plan.jpg"
    assert manifest["kept_on_volume"] == ["check/cam_hol_1_plan.jpg", "check/cam_salon_1_plan.jpg"]
    assert manifest["intake"]["totals"]["kept"] == 3 and "files" not in manifest["intake"]
    md = (final / "final_report.md").read_text(encoding="utf-8")
    assert "## Kept on the volume (private project)" in md and "- check/cam_salon_1_plan.jpg" in md
    assert "## Intake (private upload)" in md and "| junk (system metadata file) | 1 |" in md
    assert "Gizli" not in md and "Gizli" not in json.dumps(manifest)
    assert all("plan" not in link for link in links(md))
    # Previews and contact sheets are still made (they are the private allow-list).
    assert (final / "cam_salon_1_final_preview.jpg").is_file() and (final / "contact_L0.jpg").is_file()


def test_private_by_flag_alias_name_or_volume_root(tmp_path, monkeypatch):
    out = make_project(tmp_path)
    assert report_main(["final", "--project-out", str(out), "--private"]) == 0
    assert json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))["private"] is True
    assert not list((out / "final").glob("*_plan.jpg"))
    assert F.is_private(tmp_path / "outputs-private" / "real-07")
    assert F.is_private(tmp_path / "x" / "selftest-02")
    assert not F.is_private(out)
    from wenart.run import projects as P
    monkeypatch.setattr(P, "PRIVATE_OUTPUTS", tmp_path / "outputs")
    assert F.is_private(out)


def test_building_path_is_resolved_against_the_repo_root(tmp_path, monkeypatch):
    """A repo-relative ``building`` in the scene manifest (§1.1) is read with views._resolve_repo_path;
    an absolute one (a private project on the volume) stays as it is."""
    out = make_project(tmp_path, brief="style: [unclosed\n")          # project_paths fails: the report's own path
    building_file = out / "building_final.json"
    elsewhere = write_json(tmp_path / "data" / "b.json", json.loads(building_file.read_text(encoding="utf-8")))
    building_file.unlink()
    scene_path = out / "scene" / "scene_manifest.json"
    sc = json.loads(scene_path.read_text(encoding="utf-8"))
    sc["building"] = "data/b.json"
    scene_path.write_text(json.dumps(sc), encoding="utf-8")
    assert F.write_final(out)["building"]["unverified"] == []          # not found from the real repo root
    monkeypatch.setattr(VW, "REPO_ROOT", tmp_path)
    manifest = F.write_final(out)
    assert manifest["building"]["unverified"] == ["f_9"]
    assert manifest["inputs"]["building"] == C.rel(elsewhere, out / "final")
    sc["building"] = str(elsewhere)                                    # absolute stays absolute
    scene_path.write_text(json.dumps(sc), encoding="utf-8")
    monkeypatch.setattr(VW, "REPO_ROOT", tmp_path / "nowhere")
    assert F.write_final(out)["building"]["unverified"] == ["f_9"]
    assert F._building_path({"building": None}, out) is None


def test_status_of_a_report_without_renders(tmp_path):
    out = make_project(tmp_path)
    assert F.write_final(out)["status"] == "ok"
    (out / "renders" / "render_manifest.json").unlink()
    assert report_main(["final", "--project-out", str(out)]) == 1
    m = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    assert m["status"] == "not_rendered" and F.validate_final_manifest(m) == []


# --------------------------------------------------------------------------
# Needs-review report
# --------------------------------------------------------------------------

def review_building(source_folder: str, debug=("debug/plan_scan_png_p1.png", "debug/plan_pdf_p2.png"),
                    reasons=("plan.pdf p2: no scale source",), schema_error=False) -> dict:
    pages = [{"file": "plan_scan.png", "format": "image", "pages": [
                 {"page": 1, "class": "other", "kind": "scan", "level_id": None, "scale": None, "confidence": 0.0,
                  "skip_reason": "no text layer", "debug_image": debug[0]}]},
             {"file": "plan.pdf", "format": "pdf", "pages": [
                 {"page": 2, "class": "floor_plan", "kind": "vector", "level_id": "L0",
                  "scale": {"metres_per_unit": 0.0352778, "method": "text"}, "confidence": 1.0, "skip_reason": None,
                  "debug_image": debug[1]}]}]
    warnings = ["plan_scan.png p1: scan page skipped (no text layer)"] + [f"needs review: {r}" for r in reasons]
    if schema_error:
        warnings.append("schema: rooms[0]: 'polygon' is a required property")
    return {"schema_version": "0.1", "status": "needs_review",
            "project": {"id": "toy", "source_folder": source_folder, "created_utc": "2026-10-02T10:00:00Z"},
            "documents": pages, "levels": [], "walls": [], "openings": [], "rooms": [], "furniture": [],
            "conflicts": [], "unverified": [], "warnings": warnings}


def make_review_project(tmp_path, name="toy", building=None, big_debug=True) -> Path:
    out = tmp_path / "outputs" / name
    b = building if building is not None else review_building(f"projects/{name}")
    write_json(out / "building.json", b)
    (out / "report.md").write_text("# Ingest report\n\n## Documents\n\n| File | Page |\n|---|---|\n| plan.pdf | 2 |\n\n"
                                   "## Levels\n", encoding="utf-8")
    for i, rel in enumerate(p["debug_image"] for d in b["documents"] for p in d["pages"]):
        if rel:
            arr = noise(1400, 2000, i) if big_debug and i == 0 else np.full((60, 80, 3), 200, dtype=np.uint8)
            VW.write_png_rgb(out / rel, arr)
    return out


def test_needs_review_report(tmp_path, capsys):
    out = make_review_project(tmp_path)
    write_json(out / "renders" / "render_manifest.json", {"renders": []})          # an earlier run: ignored
    stage_record(out, "pipeline", "needs_review", "2026-10-02T10:00:00Z", note="building needs review")
    assert report_main(["final", "--project-out", str(out)]) == 0
    assert "needs_review (1 reason(s))" in capsys.readouterr().out
    final = out / "final"
    m = json.loads((final / "final_manifest.json").read_text(encoding="utf-8"))
    assert F.validate_final_manifest(m) == []
    assert m["status"] == "needs_review" and m["kind"] == "final" and m["private"] is False
    assert m["reasons"] == ["plan.pdf p2: no scale source"]                      # the record adds nothing new
    assert m["hints"] == ["add a scale (ÖLÇEK 1/50, 1/100 or DXF $INSUNITS) to the plan"]
    assert m["views"] == [] and m["summary"]["views"] == 0 and m["building"]["status"] == "needs_review"
    assert [(d["file"], d["page"], d["debug_preview"]) for d in m["documents"]] == [
        ("plan_scan.png", 1, "debug/plan_scan_png_p1.jpg"), ("plan.pdf", 2, "debug/plan_pdf_p2.jpg")]
    for img in m["debug_images"]:
        path = final / img["preview"]
        assert path.is_file() and path.stat().st_size <= 300_000 and img["bytes"] == path.stat().st_size
    assert any("earlier run's renders" in w for w in m["warnings"])
    md = (final / "final_report.md").read_text(encoding="utf-8")
    for text in ("# Final report: toy (needs review)", "## Reasons", "- plan.pdf p2: no scale source",
                 "## What to do", "## Documents and pages", "| plan.pdf | 2 | floor_plan | vector | L0 | "
                 "0.0352778 m/unit (text) | 1.00 | - | [debug/plan_pdf_p2.jpg](debug/plan_pdf_p2.jpg) |",
                 "## Building JSON", "## Stages", "| pipeline | needs_review | 1.0 s | building needs review |"):
        assert text in md, text
    assert links(md) and all(link.startswith("debug/") and (final / link).is_file() for link in links(md))


def test_needs_review_reasons_from_every_source(tmp_path):
    out = make_review_project(tmp_path, building=review_building("projects/toy", reasons=(), schema_error=True))
    m = F.write_final(out)
    assert m["reasons"] == ["building JSON failed schema validation"]
    b = review_building("projects/toy", reasons=())
    out2 = make_review_project(tmp_path / "2", building=b)
    assert F.write_final(out2)["reasons"] == ["building.json says needs_review (no reason recorded)"]
    # No building at all: a stage record that says needs_review (e.g. a pipeline crash before writing).
    out3 = tmp_path / "3" / "outputs" / "toy"
    stage_record(out3, "pipeline", "needs_review", "2026-10-02T10:00:00Z", note="exit 1, status needs_review")
    m = F.write_final(out3)
    assert m["reasons"] == ["pipeline: exit 1, status needs_review"] and m["documents"] == []
    md = (out3 / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "No document page was classified" in md
    # An ok project is not a needs-review project.
    assert F.review_inputs(make_project(tmp_path / "4")) is None


def test_needs_review_report_md_table_when_building_has_no_documents(tmp_path):
    b = review_building("projects/toy")
    b["documents"] = []
    out = make_review_project(tmp_path, building=b)
    assert F.write_final(out)["documents"] == []
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "From the pipeline's report.md:" in md and "| plan.pdf | 2 |" in md


def test_private_needs_review_never_copies_debug_images(tmp_path):
    out = make_review_project(tmp_path, name="real-01",
                              building=review_building("/workspace/outputs-private/real-01/input/real-01"))
    write_json(out / "intake_manifest.json", {"kind": "intake_manifest", "alias": "real-01", "status": "ok",
                                              "reasons": [], "totals": {"kept": 2, "documents": 2}})
    m = F.write_final(out)
    final = out / "final"
    assert m["private"] is True and not (final / "debug").exists()
    assert [(i["source"], i["preview"]) for i in m["debug_images"]] == [
        ("debug/plan_scan_png_p1.png", None), ("debug/plan_pdf_p2.png", None)]
    md = (final / "final_report.md").read_text(encoding="utf-8")
    assert "debug/plan_pdf_p2.png (on the volume, not copied)" in md and not links(md)
    assert "## Intake (private upload)" in md
    assert sorted(p.name for p in final.iterdir()) == ["final_manifest.json", "final_report.md"]


def test_intake_needs_review_ignores_an_older_building(tmp_path):
    out = make_review_project(tmp_path, name="real-02", building=review_building("x", reasons=("old reason",)))
    write_json(out / "intake_manifest.json", {"kind": "intake_manifest", "alias": "real-02", "status": "needs_review",
                                              "reasons": ["not uploaded"], "totals": {}, "files": []})
    stage_record(out, "intake", "needs_review", "2026-10-02T11:00:00Z", note="not uploaded")
    stage_record(out, "pipeline", "needs_review", "2026-10-01T11:00:00Z", note="old")
    m = F.write_final(out)
    assert m["reasons"] == ["intake: not uploaded"] and m["building"] is None and m["documents"] == []
    assert m["hints"] == ["upload the project folder (docs/intake.md, step 5) and run again"]
    assert any("building.json is from an earlier run" in w for w in m["warnings"])
    assert F.validate_final_manifest(m) == []


def test_review_hints_only_from_known_reasons():
    assert F.review_hints(["a.dwg: DWG conversion failed: no converter", "L0: outer walls do not form a closed loop"]) \
        == ["export DXF (or a vector PDF) from the CAD program; DWG is not read",
            "close the outer walls of the level in the drawing"]
    assert F.review_hints(["something unexpected"]) == []
