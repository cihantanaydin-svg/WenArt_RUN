"""Milestone 13, track T8 (docs/milestone13.md §6, §7, §12 D4, §13.2): ATTRIBUTION.md with its four sections in
both licence modes, the commercial-safe line per view and the "built below library level" section of the final
report, the pack3d README, the 17 metrics (on a fake run and on the committed real02 results) and the before | after
sheets. Every test here fails on the Milestone 12 code (no sections, no fields, no modules)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart import views as VW
from wenart.report import common as C
from wenart.report import final as F
from wenart.report import metrics13 as MX
from wenart.report import sheets13 as SH
from wenart.report.__main__ import main as report_main
from wenart.run import copy as CP
from wenart.run import pack3d as K

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
W, H = 96, 54


# --------------------------------------------------------------------------
# A small run in the volume layout: a building with every asset method, a scene with library assets per pass
# index, two flagged models (a tool_nc generated sofa and a CC BY-NC cushion on it), renders, an agent log, stage
# records and a rubric file.
# --------------------------------------------------------------------------

def ev(**kw):
    return [{"file": "plan.dxf", "method": "vector", "confidence": 1.0, **kw}]


def asset_gen():
    return {"library": "generated", "asset_id": "gen_sofa_modern_1_abcd1234", "method": "library",
            "licence": "generated (TRELLIS.2-4B, MIT)", "license": "generated (TRELLIS.2-4B, MIT)",
            "licence_flag": "tool_nc", "commercial_safe": False, "fit_scale": [1.0, 1.0, 1.0], "units_known": True,
            "quality": [4, 4], "attribution": '"generated sofa": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; '
                                              "no third-party credit"}


def asset_abo(aid="abo_B0TABLE01", title="Glass Coffee Table"):
    return {"library": "abo", "asset_id": aid, "method": "library", "licence": "CC-BY-4.0", "license": "CC-BY-4.0",
            "licence_flag": "none", "commercial_safe": True, "fit_scale": [1.0, 1.08, 1.0], "units_known": True,
            "quality": [3, 4], "title": title, "author": "Amazon.com",
            "source_url": "https://amazon-berkeley-objects.s3.amazonaws.com/index.html",
            "attribution": f'"{title}" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), '
                           "https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the "
                           "drawn footprint, re-oriented, rendered, AI-retouched"}


def asset_nc():
    return {"library": "objaverse", "asset_id": "objaverse_nc0001", "uid": "nc0001", "method": "library",
            "licence": "CC-BY-NC-4.0", "license": "CC-BY-NC-4.0", "licence_flag": "non_commercial",
            "commercial_safe": False, "decor_type": "cushion", "title": "NC cushion", "author": "Ana",
            "source_url": "https://sketchfab.com/nc0001", "fit_scale": [1.0, 1.0, 1.0],
            "attribution": '"NC cushion" by Ana (https://sketchfab.com/nc0001), CC BY-NC 4.0 '
                           "(https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, "
                           "ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered"}


def asset_module():
    return {"library": "module", "asset_id": "module:wardrobe:wardrobe_run", "method": "module", "licence": "n/a",
            "license": "n/a", "licence_flag": "none", "commercial_safe": True,
            "module_plan": {"builder": "wardrobe_run", "modules": [{"kind": "wardrobe_module", "size_m": [1.0, 0.6, 2.2]}],
                            "footprint_m": [2.0, 0.6], "height_m": 2.2, "products": ["PAX 100x60x236"]},
            "ladder": [{"step": "library", "result": "no model", "reason": "no wardrobe within the caps"},
                       {"step": "module", "result": "used wardrobe_run", "reason": None}]}


def asset_parametric(ftype, by_design=True):
    a = {"library": "parametric", "asset_id": f"parametric:{ftype}", "method": "parametric", "licence": "n/a",
         "license": "n/a", "licence_flag": "none", "commercial_safe": True, "fit_scale": [1.0, 1.0, 1.0],
         "fallback_reason": f"type {ftype} is parametric in the catalogue"}
    if by_design:
        a["by_design"] = True
    return a


def piece(pid, ftype, room, source="from_documents", build=True, asset=None, **extra):
    return {"id": pid, "type": ftype, "level_id": "L0", "room_id": room, "source": source, "status": "verified",
            "evidence": ev(entity=f"INSERT:{pid}"), "build": build,
            "footprint": {"center": [1.0, 1.0], "size": [1.0, 0.5], "rotation_deg": 0.0}, "front_deg": 0.0,
            "asset": asset, **extra}


def building(project_dir: Path) -> dict:
    return {
        "schema_version": "0.1", "status": "ok",
        "project": {"id": "toy", "source_folder": str(project_dir), "licence_mode": "relaxed",
                    "licence_mode_source": "given to the fit", "brief": {"style": "modern"}},
        "documents": [], "walls": [], "conflicts": [], "unverified": [], "warnings": [],
        "levels": [{"id": "L0", "label": "Zemin"}],
        "rooms": [{"id": "r_salon", "level_id": "L0", "room_type": "living", "status": "verified"},
                  {"id": "r_mutfak", "level_id": "L0", "room_type": "kitchen", "status": "verified"},
                  {"id": "r_hol", "level_id": "L0", "room_type": "hall", "status": "verified"}],
        "openings": [{"id": "win_1", "type": "window", "level_id": "L0", "status": "verified",
                      "evidence": ev(entity="INSERT:W1")}],
        "furniture": [
            piece("f_1", "sofa", "r_salon", asset=asset_gen()),
            piece("f_2", "table_coffee", "r_salon", source="added_by_ai", asset=asset_abo()),
            piece("f_3", "wardrobe", "r_salon", asset=asset_module(),
                  library_gap={"type": "wardrobe", "step": "module", "used": "module builder wardrobe_run (2 module(s))",
                               "reason": "no wardrobe within the caps"}),
            piece("f_4", "kitchen_counter", "r_mutfak", asset=asset_parametric("kitchen_counter")),
            piece("f_5", "bed_double", "r_salon", build=False,
                  asset={"library": "none", "asset_id": "none:bed_double", "method": "none", "licence": "n/a",
                         "licence_flag": "none", "commercial_safe": True}),
            piece("f_6", "tv_unit", "r_salon", source="added_by_ai", asset=asset_parametric("tv_unit", by_design=False)),
            piece("f_7", "armchair", "r_salon", asset=asset_abo("abo_B0CHAIR01", "Linen Armchair")),
        ],
        "decor": [{"id": "dec_1", "kind": "decor", "type": "cushion", "level_id": "L0", "room_id": "r_salon",
                   "source": "added_by_ai", "method": "ai", "reason": "cushions on the sofa", "host_id": "f_1",
                   "asset": asset_nc()},
                  {"id": "dec_2", "kind": "decor", "type": "rug", "level_id": "L0", "room_id": "r_salon",
                   "source": "added_by_ai", "method": "rule", "reason": "rug under the seating", "asset": None}],
        "site": {"decor": [{"id": "sd_1", "level_id": "L0", "kind": "tree", "center": [9.0, 9.0], "size": [0.7, 0.7],
                            "build": True, "evidence": ev(entity="INSERT:T1")}],
                 "hedges": [{"polyline": [[0, 0], [5, 0]], "radius_m": 0.4, "pitch_m": 0.5, "count": 10,
                             "height_class": "low"}]},
    }


def obj(name, wid, kind, pi, **extra):
    return {"name": name, "wenart_id": wid, "kind": kind, "status": "verified", "level_id": "L0",
            "evidence": ev(), "pass_index": pi, **extra}


CAMERAS = [("cam_salon_1", "r_salon", {"1": 300, "4": 800, "5": 200}, 1.5, 0.2),
           ("cam_salon_2", "r_salon", {"5": 700, "6": 300}, 6.0, 0.6),
           ("cam_mutfak_1", "r_mutfak", {"7": 900}, 0.5, 0.3),
           ("cam_hol_1", "r_hol", {}, 2.0, 0.4),
           ("ext_1", None, {}, 0.0, 0.0)]


def scene(building_path: Path) -> dict:
    cams = []
    for cam, room, _stats, _ev, wall in CAMERAS:
        c = {"name": cam, "room_id": room, "level_id": "L0" if room else None, "lens_mm": 18.0, "sensor_mm": 36.0,
             "policy": "search", "score": {"total": 2.0, "shares": {"wall": wall, "furn": 0.3}}}
        if room is None:
            c.update(kind="exterior", view="aerial", status="assumed", variant="base")
        cams.append(c)
    return {
        "schema_version": "0.1", "project": "toy", "building": str(building_path), "seconds": 12.0,
        "style_profile": {"walls": {"material": "plaster_white"}}, "cameras": cams, "cameras_dropped": [],
        "materials": {"paint__x": {"textured": True, "asset": "plastered_wall", "source": "polyhaven", "licence": "CC0",
                                   "slug": "paint", "maps": ["albedo", "normal", "roughness"]},
                      "wood__y": {"textured": True, "asset": "WoodFloor051", "source": "ambientcg", "licence": "CC0",
                                  "slug": "wood", "maps": ["albedo"]},
                      "flat": {"textured": False}},
        "lighting": {"world": {"kind": "hdri", "file": "/workspace/assets/hdris/kloppenheim_06_2k.hdr"}},
        "site": {"built": True, "objects": ["ground", "tree_sd_1", "hedge_1"],
                 "vegetation": [{"id": "sd_1", "kind": "tree", "method": "polyhaven", "species": "oak"}],
                 "hedges": [{"id": "hedge_1", "count": 10}]},
        "pass_index": {"win_1": 1, "f_1": 4, "f_2": 5, "f_3": 6, "f_4": 7, "f_7": 8},
        "objects": [
            obj("w_1", "w_1", "wall", None),
            obj("win_1_frame", "win_1", "window", 1, room_ids=["r_salon"]),
            obj("furn_f_1", "f_1", "furniture", 4, room_id="r_salon", type="sofa", source="from_documents",
                asset=asset_gen(), recolour={"fabric": {"colour": "light grey"}}),
            obj("decor_f_1_1", "f_1", "decor", 4, room_id="r_salon", type="cushion", source="added_by_ai",
                host_id="f_1", element_id="dec_1", asset=asset_nc()),
            obj("furn_f_2", "f_2", "furniture", 5, room_id="r_salon", type="table_coffee", source="added_by_ai",
                asset=asset_abo()),
            obj("furn_f_3", "f_3", "furniture", 6, room_id="r_salon", type="wardrobe", source="from_documents",
                asset=asset_module()),
            obj("furn_f_4", "f_4", "furniture", 7, room_id="r_mutfak", type="kitchen_counter",
                source="from_documents", asset=asset_parametric("kitchen_counter")),
            obj("furn_f_7", "f_7", "furniture", 8, room_id="r_salon", type="armchair", source="from_documents",
                asset=asset_abo("abo_B0CHAIR01", "Linen Armchair")),
        ],
    }


def agent_log() -> dict:
    def finding(seq, rnd, check, target, **metrics):
        return {"seq": seq, "round": rnd, "kind": "finding", "source": "code", "checklist": check,
                "severity": "major", "target": target, "room_id": "r_salon", "finding": f"{check} on {target}",
                "evidence": {"metrics": metrics}}

    def edit(seq, rnd, check, target):
        return {"seq": seq, "round": rnd, "kind": "edit", "tool": "move_piece", "target": target, "checklist": check,
                "validation": {"accepted": True}, "label": "adjusted_by_ai", "reason": "fix"}

    events = [finding(1, 1, "F8", "f_7", partner_m=0.8), finding(2, 1, "S2", "f_1", depth_m=0.05),
              finding(3, 1, "S2", "f_2", depth_m=0.01), finding(4, 1, "G10", "f_4"), finding(5, 1, "LG", "f_3"),
              edit(6, 1, "F8", "f_7"), edit(7, 1, "S2", "f_1"),
              finding(8, 2, "S2", "f_1", depth_m=0.05), finding(9, 2, "G10", "f_4"), finding(10, 2, "LG", "f_3"),
              {"seq": 11, "round": 2, "kind": "stop", "reason": "max rounds reached"}]
    return {"schema_version": "0.1", "kind": "agent_log", "project": "toy", "model": "Qwen/Qwen3.8-27B-FP8",
            "revision": "0" * 40, "stop": {"round": 2, "reason": "max rounds reached"}, "events": events,
            "calls": [{"call_id": "r1-v1", "prompt_tokens": 10, "completion_tokens": 2}]}


def make_run(tmp_path: Path, name: str = "toy", *, evs=None) -> Path:
    """``<tmp>/outputs/<name>`` with the building, scene, renders (tiny PNGs and previews), log, stage records and
    rubric; ``evs``: an EV per camera (default: CAMERAS)."""
    project_dir = tmp_path / "projects" / name
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "brief.yaml").write_text("style: modern\n", encoding="utf-8")
    out = tmp_path / "outputs" / name
    for sub in ("scene", "renders", "orchestrator", "run", "final"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    bpath = out / "building_final.json"
    bpath.write_text(json.dumps(building(project_dir)), encoding="utf-8")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene(bpath)), encoding="utf-8")
    entries = []
    for i, (cam, room, stats, cam_ev, _wall) in enumerate(CAMERAS):
        rgb = np.zeros((H, W, 3), dtype=np.uint8)
        rgb[..., 1] = 60 + 30 * i
        if cam == "ext_1":
            rgb[: H // 2] = 0                    # the upper half black: 50 % black pixels in the site view
            rgb[H // 2:] = 120
        VW.write_png_rgb(out / "renders" / f"{cam}.png", rgb)
        Image.fromarray(rgb).save(out / "renders" / f"{cam}_preview.jpg", quality=80)
        entries.append({"camera": cam, "room_id": room, "level_id": "L0" if room else None, "png": f"{cam}.png",
                        "preview": f"{cam}_preview.jpg", "seconds": 3.0, "samples": 16, "resolution": [W, H],
                        "index_values": sorted(int(k) for k in stats),
                        "index_stats": {k: {"pixels": v, "box": [0, 0, 10, 10]} for k, v in stats.items()},
                        "skipped": False, "scene_sha256": "x", "render_key": f"{i:016x}", "hidden": [], "plugged": [],
                        "exposure": {"mode": "auto", "ev": (evs or {}).get(cam, cam_ev), "ev_raw": cam_ev,
                                     "at_limit": False, "target": 0.9}})
    (out / "renders" / "render_manifest.json").write_text(
        json.dumps({"schema_version": "0.1", "renders": entries, "warnings": []}), encoding="utf-8")
    (out / "orchestrator" / "log.json").write_text(json.dumps(agent_log()), encoding="utf-8")
    (out / "orchestrator" / "overrides.json").write_text(json.dumps({"edits": []}), encoding="utf-8")
    for stage, seconds in (("build", 300.0), ("render", 120.0), ("agent", 600.0)):
        (out / "run" / f"{stage}.json").write_text(json.dumps({
            "kind": "stage_record", "project": name, "stage": stage, "status": "ok", "seconds": seconds,
            "run_id": "20261015-000000-full", "started_utc": "2026-10-15T00:00:00Z"}), encoding="utf-8")
    (out / "final" / "rubric_per_view.json").write_text(json.dumps([
        {"view": "cam_salon_1", "room_type": "living", "tags": ["looks_acceptable"], "client_ready_score": 4},
        {"view": "cam_salon_2", "room_type": "living", "tags": ["bare_material"], "client_ready_score": 2},
        {"view": "cam_mutfak_1", "room_type": "kitchen", "tags": ["empty_room"], "client_ready_score": 1},
        {"view": "cam_hol_1", "room_type": "hall", "tags": ["bad_camera"], "client_ready_score": 1},
        {"view": "ext_1", "room_type": None, "tags": ["flat_outdoor"], "client_ready_score": 2},
        {"view": "cam_stale", "room_type": None, "tags": [], "client_ready_score": 5}]), encoding="utf-8")
    return out


# --------------------------------------------------------------------------
# 1. ATTRIBUTION.md in both modes
# --------------------------------------------------------------------------

def fake_credits() -> list[dict]:
    return [
        {"credit": '"Oak table" by Ana (https://sketchfab.com/u1), CC BY 4.0 (https://creativecommons.org/licenses/'
                   "by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint",
         "pieces": [("f_1", "table_dining")], "source": "objaverse", "asset_id": "objaverse_u1", "kind": "model",
         "licence": "CC-BY-4.0", "licence_flag": "none", "commercial_safe": True,
         "licence_url": "https://creativecommons.org/licenses/by/4.0/"},
        {"credit": '"NC chair" by Bo (https://sketchfab.com/u2), CC BY-NC 4.0', "pieces": [("f_2", "chair")],
         "source": "objaverse", "asset_id": "objaverse_u2", "kind": "model", "licence": "CC-BY-NC-4.0",
         "licence_flag": "non_commercial", "commercial_safe": False,
         "licence_url": "https://creativecommons.org/licenses/by-nc/4.0/"},
        {"credit": '"generated stove": generated with TRELLIS.2-4B (MIT) for WenArt_RUN', "pieces": [("f_3", "stove")],
         "source": "generated", "asset_id": "gen_stove_1", "kind": "model", "licence": "generated (TRELLIS.2-4B, MIT)",
         "licence_flag": "tool_nc", "commercial_safe": False,
         "licence_url": "https://github.com/microsoft/TRELLIS.2/blob/main/LICENSE"},
        {"credit": '"HSSD sofa" (hssd/hssd-models), CC BY-NC 4.0', "pieces": [("f_4", "sofa")], "source": "hssd",
         "asset_id": "hssd_sofa_1", "kind": "model", "licence": "CC-BY-NC-4.0", "licence_flag": "non_commercial",
         "commercial_safe": False, "licence_url": "https://huggingface.co/datasets/hssd/hssd-models"},
        {"credit": '"Rug" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.'
                   "amazonaws.com/index.html; changes: scaled", "pieces": [("d_1", "rug")], "source": "abo",
         "asset_id": "abo_B01", "kind": "model", "licence": "CC-BY-4.0", "licence_flag": "none",
         "commercial_safe": True, "licence_url": "https://creativecommons.org/licenses/by/4.0/"},
        {"credit": "texture set plastered_wall (Poly Haven, CC0)", "pieces": [("paint__x", "paint")],
         "source": "polyhaven", "asset_id": "plastered_wall", "kind": "texture", "licence": "CC0",
         "licence_flag": "none", "commercial_safe": True, "licence_url": "https://polyhaven.com/license",
         "changes": "tiled, tinted and lit in the shell materials"},
    ]


def sections(text: str) -> dict:
    out: dict = {}
    for part in text.split("\n## ")[1:]:
        head, _, body = part.partition("\n")
        out[head.strip()] = body
    return out


def test_attribution_text_has_the_four_sections_in_relaxed_mode():
    text = CP.attribution_text("The images of project p", fake_credits(), mode="relaxed")
    s = sections(text)
    assert list(s) == ["1. Tools and generators", "2. CC0 / CC BY assets (author, source, licence, changes)",
                       "3. PoC-only assets (not commercial-safe)", "4. Dataset notices"]
    assert "Licence mode: relaxed" in text
    tools = s["1. Tools and generators"]
    for name in ("Blender 5.2 LTS", "GNU LibreDWG 0.14", "Qwen/Qwen3.8-27B-FP8", "Qwen/Qwen3-VL-8B-Instruct",
                 "microsoft/TRELLIS.2-4B", "Tongyi-MAI/Z-Image-Turbo", "Poly Haven API"):
        assert name in tools, name
    assert "GPL-3.0" in tools and "Apache-2.0" in tools and "MIT" in tools
    assert "dinov3-vitl16-pretrain-lvd1689m" in tools and "DINOv3 License" in tools
    assert "nvdiffrast" in tools and "Powered by Poly Haven" in tools
    safe = s["2. CC0 / CC BY assets (author, source, licence, changes)"]
    assert '"Oak table" by Ana' in safe and '"Rug" by Amazon.com' in safe and "texture set plastered_wall" in safe
    assert "(used for f_1 (table_dining))" in safe and "tiled, tinted" in safe
    assert "NC chair" not in safe and "generated stove" not in safe
    poc = s["3. PoC-only assets (not commercial-safe)"]
    assert "NC chair" in poc and "[licence flag: non_commercial]" in poc and "forbids commercial use" in poc
    assert "generated stove" in poc and "[licence flag: tool_nc]" in poc and "nvdiffrast" in poc
    assert "https://github.com/NVlabs/nvdiffrast/blob/v0.4.0/LICENSE.txt" in poc
    assert "HSSD sofa" in poc and "https://huggingface.co/datasets/hssd/hssd-models" in poc
    assert "https://creativecommons.org/licenses/by-nc/4.0/" in poc and "WARNING" not in poc
    notices = s["4. Dataset notices"]
    assert "ODC Attribution License" in notices                  # Objaverse
    assert "Amazon Berkeley Objects" in notices and "CC BY 4.0" in notices
    assert "Habitat Synthetic Scenes Dataset" in notices and "CC BY-NC 4.0" in notices and "2306.11290" in notices
    # build round 2: the HSSD notice is built from wenart.assets.hssd.DATASET (the card's terms, the citation)
    from wenart.assets import hssd as H
    assert CP.hssd_notice() in notices and H.GATED_PROMPT in notices and H.CITATION in notices
    assert "Generated models" in notices and "Poly Haven" in notices and "CC0 1.0" in notices


def test_attribution_text_in_commercial_mode_warns_about_flagged_assets_and_is_clean_without_them():
    credits = fake_credits()
    text = CP.attribution_text("The images of project p", credits, mode="commercial")
    s = sections(text)
    assert "Licence mode: commercial" in text
    poc = s["3. PoC-only assets (not commercial-safe)"]
    assert "WARNING: 3 flagged asset(s) in commercial mode" in poc and "NC chair" in poc
    clean = [c for c in credits if c["commercial_safe"]]
    text2 = CP.attribution_text("The images of project p", clean, mode="commercial")
    s2 = sections(text2)
    assert s2["3. PoC-only assets (not commercial-safe)"].strip().startswith(
        "None. Commercial mode: every asset in these images is commercial-safe.")
    assert "WARNING" not in text2 and "Habitat" not in text2
    with pytest.raises(ValueError):
        CP.attribution_text("x", clean, mode="free")


def test_project_credits_carry_the_licence_fields_and_textures_are_credited(tmp_path):
    out = make_run(tmp_path)
    credits = CP.project_credits(out)
    by_id = {c["asset_id"]: c for c in credits}
    assert set(by_id) == {"abo_B0CHAIR01", "abo_B0TABLE01", "gen_sofa_modern_1_abcd1234", "objaverse_nc0001"}
    assert by_id["gen_sofa_modern_1_abcd1234"]["licence_flag"] == "tool_nc"
    assert by_id["gen_sofa_modern_1_abcd1234"]["commercial_safe"] is False
    assert by_id["gen_sofa_modern_1_abcd1234"]["licence_url"] == \
        "https://github.com/microsoft/TRELLIS.2/blob/main/LICENSE"
    assert by_id["objaverse_nc0001"]["licence_flag"] == "non_commercial"
    assert by_id["objaverse_nc0001"]["licence_url"] == "https://creativecommons.org/licenses/by-nc/4.0/"
    assert by_id["abo_B0TABLE01"]["licence_flag"] == "none" and by_id["abo_B0TABLE01"]["commercial_safe"] is True
    assert by_id["abo_B0TABLE01"]["licence_url"] == "https://creativecommons.org/licenses/by/4.0/"
    assert all(c["kind"] == "model" for c in credits)
    textures = CP.texture_credits(out)
    assert {t["asset_id"] for t in textures} == {"plastered_wall", "WoodFloor051", "hdri:kloppenheim_06_2k"}
    assert all(t["licence_flag"] == "none" and t["commercial_safe"] for t in textures)
    assert CP.project_licence_mode(out) == "relaxed"
    text = CP.attribution_text("The images of project toy", credits + textures, mode=CP.project_licence_mode(out))
    s = sections(text)
    assert "HDRI kloppenheim_06_2k" in s["2. CC0 / CC BY assets (author, source, licence, changes)"]
    assert "gen_sofa_modern_1_abcd1234" not in s["2. CC0 / CC BY assets (author, source, licence, changes)"]
    assert "generated sofa" in s["3. PoC-only assets (not commercial-safe)"]
    assert "NC cushion" in s["3. PoC-only assets (not commercial-safe)"]


def test_library_attribution_lists_the_whole_catalogue_in_relaxed_mode(tmp_path):
    lib = tmp_path / "library"
    lib.mkdir()
    (lib / "catalog_library.json").write_text(json.dumps({"kind": "library_catalog", "entries": [
        dict(asset_abo(), id="abo_B0TABLE01", source="abo", type="table_coffee"),
        dict(asset_gen(), id="gen_sofa_modern_1_abcd1234", source="generated", type="sofa")],
        "decor": [dict(asset_nc(), id="objaverse_nc0001", source="objaverse")]}), encoding="utf-8")
    text = CP.library_attribution(lib).read_text(encoding="utf-8")
    s = sections(text)
    assert "Licence mode: relaxed" in text
    assert "Glass Coffee Table" in s["2. CC0 / CC BY assets (author, source, licence, changes)"]
    poc = s["3. PoC-only assets (not commercial-safe)"]
    assert "generated sofa" in poc and "[licence flag: tool_nc]" in poc
    assert "NC cushion" in poc and "[licence flag: non_commercial]" in poc and "WARNING" not in poc


# --------------------------------------------------------------------------
# 2. The final report: commercial-safe per view, the below-library section
# --------------------------------------------------------------------------

def test_final_report_carries_the_commercial_safe_line_per_view_and_the_below_library_section(tmp_path):
    out = make_run(tmp_path)
    manifest = F.write_final(out)
    views = {v["camera"]: v for v in manifest["views"]}
    # cam_salon_1 shows index 4 (the tool_nc sofa and its NC cushion) and 5 (the CC BY table): flagged
    cs = views["cam_salon_1"]["commercial_safe"]
    assert cs["safe"] is False and cs["flagged"] == ["gen_sofa_modern_1_abcd1234", "objaverse_nc0001"]
    assert cs["flags"] == {"gen_sofa_modern_1_abcd1234": "tool_nc", "objaverse_nc0001": "non_commercial"}
    assert cs["pieces"]["objaverse_nc0001"] == ["f_1"]      # the hosted cushion shares its host's index
    # cam_salon_2 shows 5 (CC BY) and 6 (a module: ours): safe; cam_mutfak_1 a parametric run: safe; ext_1: nothing
    assert views["cam_salon_2"]["commercial_safe"] == {"safe": True, "flagged": [], "flags": {}, "pieces": {},
                                                       "assets": 1}
    assert views["cam_mutfak_1"]["commercial_safe"]["safe"] and views["ext_1"]["commercial_safe"]["safe"]
    lic = manifest["licence"]
    assert lic["mode"] == "relaxed" and lic["mode_source"] == "given to the fit"
    assert lic["flagged_assets"] == ["gen_sofa_modern_1_abcd1234", "objaverse_nc0001"]
    assert lic["views_safe"] == 4 and lic["views_flagged"] == 1
    assert lic["line"] == ("commercial-safe: no (flagged assets: gen_sofa_modern_1_abcd1234 [tool_nc], "
                           "objaverse_nc0001 [non_commercial])")
    below = {b["id"]: b for b in manifest["below_library"]}
    assert set(below) == {"f_3", "f_4", "f_6"}                 # the module, the by-design run, the parametric tv unit
    assert below["f_3"]["method"] == "module" and below["f_3"]["builder"] == "wardrobe_run" and below["f_3"]["gap"]
    assert below["f_3"]["room_id"] == "r_salon" and below["f_3"]["room_type"] == "living"
    assert below["f_3"]["used"] == "module builder wardrobe_run (2 module(s))"
    assert below["f_4"]["by_design"] is True and below["f_4"]["gap"] is False
    assert below["f_6"]["method"] == "parametric" and below["f_6"]["builder"] == "parametric:tv_unit" and below["f_6"]["gap"]
    assert F.validate_final_manifest(manifest) == []
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    section = md.split("## Commercial-safe per view (Milestone 13)")[1].split("## Built below library level")[0]
    assert "Licence mode: relaxed (given to the fit)" in section
    assert "- cam_salon_1: commercial-safe: no (flagged assets: gen_sofa_modern_1_abcd1234 [tool_nc], " \
           "objaverse_nc0001 [non_commercial])" in section
    assert "- cam_salon_2: commercial-safe: yes" in section and "- ext_1: commercial-safe: yes" in section
    assert section.count("commercial-safe:") == 1 + len(views)        # the project line and one per view
    gaps = md.split("## Built below library level (Milestone 13)")[1].split("\n## ")[0]
    assert "3 furniture piece(s) built from a module builder or a parametric family" in gaps
    assert "2 library gap(s) to close with a real model, 1 made to the drawing by design" in gaps
    assert "| f_3 | wardrobe | module | wardrobe_run | r_salon | living | from_documents | yes |" in gaps
    assert "| f_4 | kitchen_counter | parametric | parametric:kitchen_counter | r_mutfak | kitchen | from_documents " \
           "| no (by design) |" in gaps
    # relaxed mode: no advisory flag about the flagged views; commercial mode: one
    assert not any("commercial licence mode" in f for f in manifest["advisory_flags"])
    b = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    b["project"]["licence_mode"] = "commercial"
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    manifest2 = F.write_final(out)
    assert any(f.startswith("commercial licence mode but 1 view(s) show flagged assets")
               for f in manifest2["advisory_flags"])


def test_commercial_safe_of_view_uses_the_catalogue_functions_and_a_stricter_catalogue_flag():
    class Cat:
        def entry(self, aid):
            return {"id": aid, "source": "abo", "licence": "CC-BY-4.0", "licence_flag": "regional"} \
                if aid == "abo_B0TABLE01" else None

    by_index = F.assets_by_index(scene(Path("b.json")))
    assert sorted(by_index) == [4, 5, 8]                                # 6 is a module, 7 parametric: ours
    assert [wid for wid, _ in by_index[4]] == ["f_1", "f_1"]           # the sofa and its hosted cushion
    assert 7 not in by_index                                           # a parametric object carries no library asset
    entry = {"camera": "c", "index_values": [5]}
    assert F.commercial_safe_of_view(entry, by_index) == {"safe": True, "flagged": [], "flags": {}, "pieces": {},
                                                          "assets": 1}
    strict = F.commercial_safe_of_view(entry, by_index, Cat())
    assert strict["safe"] is False and strict["flags"] == {"abo_B0TABLE01": "regional"}
    # an asset without licence fields: the licence text and the export tool decide (track T1's rules)
    bare = {4: [("f_x", {"library": "generated", "asset_id": "gen_x", "method": "library",
                         "licence": "generated (TRELLIS.2-4B, MIT)"})]}
    assert F.commercial_safe_of_view({"index_stats": {"4": {"pixels": 9}}}, bare)["flags"] == {"gen_x": "tool_nc"}
    assert F.commercial_safe_line({"safe": True, "flagged": []}) == "commercial-safe: yes"
    assert F.commercial_safe_line(None) == "commercial-safe: not recorded"
    assert F.commercial_safe_line({"safe": False, "flagged": ["a", "b"], "flags": {"a": "tool_nc"}}) == \
        "commercial-safe: no (flagged assets: a [tool_nc], b)"


def test_pack3d_readme_carries_the_licence_line_and_the_below_library_list(tmp_path):
    out = make_run(tmp_path)
    manifest = F.write_final(out)
    final = tmp_path / "results" / "final" / "toy"
    (final / "3d").mkdir(parents=True)
    (final / "3d" / "toy.blend").write_bytes(b"B" * 100)
    (final / "3d" / "export_manifest.json").write_text("{}")
    (final / "final_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    K.pack(final, tmp_path / "delivery", part_mb=1)
    text = (tmp_path / "delivery" / K.README).read_text(encoding="utf-8")
    assert "Licence mode: relaxed" in text
    assert "commercial-safe: no (flagged assets: gen_sofa_modern_1_abcd1234 [tool_nc], objaverse_nc0001 " \
           "[non_commercial])" in text
    assert "Views that are not commercial-safe: cam_salon_1 (gen_sofa_modern_1_abcd1234, objaverse_nc0001)." in text
    assert "Built below library level (module builders and parametric families; 2 library gap(s)" in text
    assert "  - f_3: wardrobe, module, wardrobe_run, room r_salon" in text
    assert "  - f_4: kitchen_counter, parametric, parametric:kitchen_counter, room r_mutfak (by design)" in text
    # the volume layout: outputs/<p>/export next to final/; and no manifest at all
    export = tmp_path / "outputs" / "toy" / "export"
    export.mkdir()
    (export / "toy.glb").write_bytes(b"G" * 10)
    assert K.final_manifest_path(export) == out / "final" / "final_manifest.json"
    assert K.licence_notes(tmp_path / "nowhere")[0].startswith("Licence (Milestone 13): no final_manifest.json")


# --------------------------------------------------------------------------
# 3. The 17 metrics
# --------------------------------------------------------------------------

def test_the_17_metrics_on_the_fake_run_and_the_before_after_shape(tmp_path):
    out = make_run(tmp_path)
    F.write_final(out)
    (out / "final" / "ATTRIBUTION.md").write_text(CP.attribution_text(
        "x", CP.project_credits(out), mode="relaxed"), encoding="utf-8")
    result = MX.metrics(out)
    m = result["metrics"]
    assert sorted(int(k[1:]) for k in m) == list(range(1, 18)) and result["layout"] == "volume"
    for k, v in m.items():
        assert set(v) >= {"id", "name", "value", "baseline", "unit", "source", "text", "parts", "target"}, k
        assert v["value"] == MX.NO_DATA or isinstance(v["value"], (int, float)), k
        assert v["baseline"] is None
    assert m["m1"]["text"] == "2 of 3 (67 %)" and m["m1"]["parts"]["not_built"] == ["f_5"]
    assert m["m2"]["text"].startswith("4 of 5")
    assert m["m3"]["value"] == 1 and m["m3"]["parts"]["ids"] == ["f_5"]
    assert m["m4"]["parts"]["parametric"] == 2 and m["m4"]["parts"]["module"] == 1 and m["m4"]["parts"]["grey_boxes"] == 0
    # the living room has its sofa, coffee table, tv unit and rug; the kitchen only its counter run
    assert m["m5"]["parts"]["by_type"] == {"living": {"complete": 1, "rooms": 1}, "kitchen": {"complete": 0, "rooms": 1}}
    assert m["m5"]["parts"]["missing"] == {"r_mutfak": ["sink", "hob", "fridge"]} and m["m5"]["value"] == 50.0
    assert m["m6"]["parts"]["round"] == 2 and m["m6"]["parts"]["S2"] == 1 and m["m6"]["parts"]["G10"] == 1
    assert m["m6"]["parts"]["LG"] == 1 and m["m6"]["parts"]["F8"] == 0 and m["m6"]["value"] == 3
    assert m["m7"]["text"].startswith("1 of 2 (50 %)")                 # F8 on f_7 gone, S2 on f_1 still there
    # three built library pieces: the sofa (uniform, judges 4/4) and the two ABO pieces (8 % stretch, a judge at 3)
    assert m["m8"]["parts"]["distinct_models"] == 3 and m["m8"]["parts"]["stretch_over_5pct"] == 66.7
    assert m["m8"]["parts"]["quality_le3"] == 66.7 and m["m8"]["parts"]["units_unknown"] == 0.0
    assert m["m8"]["parts"]["top_share"] == 33.3 and m["m8"]["value"] == 33.3
    assert m["m9"]["value"] == 1 and m["m9"]["parts"]["cameras"] == ["cam_salon_2"]
    # rooms without a window (kitchen 0.5, hall 2.0: median 1.25) vs the salon views (1.5, 6.0: median 3.75)
    assert m["m9"]["parts"]["ev_gap"] == 2.5 and m["m9"]["parts"]["median_ev_no_window"] == 1.25
    # one of two textured slots records normal + roughness; the sofa got its fabric recolour, the armchair not
    assert m["m10"]["parts"]["shell_slots_pbr"] == 50.0 and m["m10"]["parts"]["fabric_applied"] == 50.0
    assert m["m10"]["parts"]["upholstered_built"] == 2 and m["m10"]["parts"]["fabric_applied_n"] == 1
    assert m["m11"]["parts"] ["trees_built"] == 1 and m["m11"]["value"] == 100.0
    assert m["m11"]["parts"]["hedges_built"] == 1 and m["m11"]["parts"]["hedges_drawn"] == 1
    assert m["m11"]["parts"]["black_pct"] == 50.0 and m["m11"]["parts"]["site_camera"] == "ext_1"
    assert m["m12"]["text"] == "1 of 1 (0 dropped)"
    assert m["m13"]["parts"]["hall_views"] == 1 and m["m13"]["parts"]["bare_wall_views"] == 1 and m["m13"]["value"] == 2
    assert m["m14"]["value"] == 0
    assert m["m15"]["value"] == 2.0 and m["m15"]["parts"]["views"] == 5 and m["m15"]["parts"]["at_1"] == 2
    assert m["m16"]["value"] == 100.0 and m["m16"]["parts"]["missing_in_attribution"] == 0
    assert m["m17"]["value"] == 17.0 and m["m17"]["parts"]["usd"] == round(17.0 / 60 * MX.PRICE_USD_PER_H, 2)
    rows = {r["camera"]: r for r in result["views"]}
    assert rows["cam_salon_1"]["commercial_safe"].startswith("commercial-safe: no") and rows["cam_salon_1"]["score"] == 4
    assert rows["ext_1"]["kind"] == "exterior" and rows["cam_salon_2"]["bare_wall"] == 0.6
    # before | after: the same run as its own baseline (darker EVs) fills the baseline fields and the view match
    base = make_run(tmp_path / "b", "toy", evs={"cam_salon_2": 1.0})
    F.write_final(base)
    result2 = MX.metrics(out, base)
    assert result2["baseline_project"] == "toy" and result2["metrics"]["m9"]["baseline"] == 0
    assert result2["metrics"]["m9"]["value"] == 1 and result2["metrics"]["m1"]["baseline_text"] == "2 of 3 (67 %)"
    assert all(v["baseline"] is not None for v in result2["metrics"].values())
    assert {r["camera"]: r["before"]["ev"] for r in result2["views"]}["cam_salon_2"] == 1.0
    md = MX.markdown(result2)
    assert "| 9 | interior views at EV >= +5" in md and "| EV before | EV after |" in md
    # no data, never 0, when an input is missing
    (out / "orchestrator" / "log.json").unlink()
    (out / "scene" / "scene_manifest.json").unlink()
    m3 = MX.metrics(out)["metrics"]
    assert m3["m6"]["value"] == MX.NO_DATA and m3["m7"]["value"] == MX.NO_DATA
    assert m3["m10"]["parts"]["shell_slots_pbr"] == MX.NO_DATA and m3["m12"]["parts"]["planned"] == MX.NO_DATA
    assert m3["m13"]["parts"]["bare_wall_views"] == MX.NO_DATA and m3["m1"]["value"] == m["m1"]["value"]


@pytest.mark.skipif(not (RESULTS / "final" / "real02" / "final_manifest.json").is_file(),
                    reason="no committed real02 results")
def test_the_17_metrics_on_the_committed_real02_results():
    """The committed M11 run of real02 (commit 93aff07, the Milestone 13 baseline of D6) in the results layout."""
    result = MX.metrics(RESULTS / "final" / "real02")
    assert result["layout"] == "results" and result["project"] == "real02"
    m = result["metrics"]
    assert len(m) == 17
    for k, v in m.items():
        assert v["value"] == MX.NO_DATA or isinstance(v["value"], (int, float)), (k, v["value"])
        assert v["text"] and v["source"]
    assert m["m1"]["text"] == "29 of 30 (97 %)" and m["m2"]["text"] == "185 of 210 (88 %)"
    assert m["m3"]["value"] == 0 and m["m4"]["parts"]["grey_boxes"] == 21
    assert m["m9"]["value"] == 9 and m["m9"]["parts"]["interior_views"] == 35
    assert m["m12"]["text"] == "6 of 6 (0 dropped)" and m["m13"]["parts"]["hall_views"] == 9
    assert m["m14"]["value"] == 0 and m["m15"]["value"] == 1.9 and m["m15"]["parts"]["views"] == 41
    assert m["m16"]["value"] == 0.0                              # a run before Milestone 13: no line
    assert m["m10"]["parts"]["shell_slots_pbr"] == MX.NO_DATA    # maps not recorded in the M11 scene manifest
    assert isinstance(m["m17"]["value"], float) and m["m17"]["value"] > 0
    assert len(result["views"]) == 41 and all(r["score"] != MX.NO_DATA for r in result["views"])


def test_metrics13_cli_writes_json_and_markdown(tmp_path, capsys):
    out = make_run(tmp_path)
    F.write_final(out)
    js, md = tmp_path / "m.json", tmp_path / "m.md"
    assert report_main(["metrics13", "--out", str(out), "--baseline", str(out), "--json", str(js), "--md", str(md)]) == 0
    data = json.loads(js.read_text(encoding="utf-8"))
    assert data["kind"] == "metrics13" and len(data["metrics"]) == 17 and data["baseline_project"] == "toy"
    assert "# Milestone 13 metrics: toy" in md.read_text(encoding="utf-8")
    assert "report metrics13 toy: 17 metrics, 5 views, baseline toy" in capsys.readouterr().out
    assert report_main(["metrics13", "--out", str(tmp_path / "nope"), "--json", str(js)]) == 2


# --------------------------------------------------------------------------
# 4. Before | after sheets
# --------------------------------------------------------------------------

def test_sheets13_writes_one_jpeg_per_camera_with_the_two_lines(tmp_path):
    after = make_run(tmp_path / "a", "toy")
    F.write_final(after)
    before = make_run(tmp_path / "b", "toy")                 # a run before Milestone 13: no commercial_safe field
    bf = before / "final"
    bf.mkdir(exist_ok=True)
    (bf / "final_manifest.json").write_text(json.dumps({"views": [
        {"camera": c, "room_id": r, "view_kind": "interior" if r else "exterior"} for c, r, *_ in CAMERAS[:4]]}),
        encoding="utf-8")
    for cam, *_ in CAMERAS[:4]:
        Image.new("RGB", (W, H), (200, 50, 50)).save(bf / f"{cam}_final_preview.jpg", quality=80)
    (before / "renders" / "ext_1_preview.jpg").unlink()      # the baseline has no exterior preview at all
    out = tmp_path / "sheets"
    result = SH.sheets(after, before, out)
    assert sorted(result["sheets"]) == sorted(c for c, *_ in CAMERAS)
    assert result["missing_before"] == ["ext_1"] and result["missing_after"] == [] and result["baseline_only"] == []
    for cam, name in result["sheets"].items():
        p = out / name
        assert p.is_file() and p.stat().st_size <= C.MAX_IMAGE_BYTES
        img = Image.open(p)
        assert img.height == SH.TILE_HEIGHT + SH.CAPTION_HEIGHT and img.width > 2 * SH.TILE_HEIGHT
    rec = {r["camera"]: r for r in result["records"]}
    assert rec["cam_salon_1"]["before_line"] == "commercial-safe: not recorded"
    assert rec["cam_salon_1"]["after_line"].startswith("commercial-safe: no (flagged assets: gen_sofa_modern_1_abcd1234")
    assert rec["cam_salon_2"]["after_line"] == "commercial-safe: yes" and rec["cam_salon_1"]["room_type"] == "living"
    # the left tile of ext_1 is the grey "no preview" tile, not a crash
    left = Image.open(out / result["sheets"]["ext_1"]).convert("RGB").getpixel((200, 300))
    assert all(abs(a - b) <= 12 for a, b in zip(left, SH.MISSING_TILE)), left      # JPEG: nearly the tile grey
    index = (out / SH.INDEX_MD).read_text(encoding="utf-8")
    assert "| cam_salon_1 | r_salon | living | commercial-safe: not recorded | commercial-safe: no" in index
    assert "No baseline preview: ext_1." in index
    assert json.loads((out / SH.INDEX_JSON).read_text(encoding="utf-8"))["sheets"] == result["sheets"]


def test_sheets13_cli(tmp_path, capsys):
    after = make_run(tmp_path / "a", "toy")
    F.write_final(after)
    out = tmp_path / "s"
    assert report_main(["sheets13", "--out", str(after), "--baseline", str(after), "--dir", str(out)]) == 0
    assert sorted(p.name for p in out.glob("*.jpg")) == sorted(f"{c}{SH.SUFFIX}" for c, *_ in CAMERAS)
    assert "report sheets13 toy: 5 sheet(s)" in capsys.readouterr().out
    assert report_main(["sheets13", "--out", str(after), "--baseline", str(tmp_path / "nope"), "--dir", str(out)]) == 2
