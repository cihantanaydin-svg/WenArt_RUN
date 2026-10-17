"""Milestone 13, track T8 (docs/milestone13.md §6, §7, §12 D4, §13.2): ATTRIBUTION.md with its four sections in
both licence modes, the commercial-safe line per view and the "built below library level" section of the final
report, the pack3d README, the 17 metrics (on a fake run and on the committed real02 results) and the before | after
sheets. Every test here fails on the Milestone 12 code (no sections, no fields, no modules).

Fix round after P3 (16-17 Oct 2026): metrics 6 and 7 of the latest run of an appended orchestrator log
(``run_first_seq``), metric 2 without the explained non-furniture, and the previews and plan crops of cameras a run
does not have moved out of ``final/``. Part 2 (17 Oct 2026): the needs-review report moves them as well, and the
results copy before and after the report holds only the views of this run's manifest.

Fix round after P4a (17 Oct 2026, the library lens of the P4a analysis): the sheets' labels sit on a dark box and a grey
tile's text below it, long commercial-safe lines wrap instead of being cut, a baseline preview is used only for a
camera the baseline report lists, "not recorded" is no flagged colour; metric 11 counts the scene's inferred trees when
none is drawn; the report's Attribution section leaves out "AI-retouched" when no view was polished.

Fix round after P4b (17 Oct 2026, the library lens of the P4b analysis): ATTRIBUTION.md section 1 names
GLM-4.6V-Flash (the second recognition pass) with check.yaml's licence; the report's models table (and so the run's
ATTRIBUTION.md) lists the recognition models with their revisions and answer counts; metric 12 counts a
dropped-then-re-added camera once and lists a rendered camera no plan names apart; metric 11 measures black pixels
only in an aerial or site view (no data with the drop reason when there is none)."""
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
    # fix round after P3: metric 2 also says the share without the explained non-furniture (7 details, 4 rug
    # outlines, 1 symbol both AI passes call not furniture)
    assert m["m1"]["text"] == "29 of 30 (97 %)" and m["m2"]["text"] == "185 of 210 (88 %); without the 12 explained " \
        "non-furniture pieces: 185 of 198 (93 %)"
    assert m["m2"]["parts"]["explained_by"] == {"detail": 7, "not_furniture": 1, "rug": 4}
    assert m["m3"]["value"] == 0 and m["m4"]["parts"]["grey_boxes"] == 21
    assert m["m9"]["value"] == 9 and m["m9"]["parts"]["interior_views"] == 35
    assert m["m12"]["text"] == "6 of 6 (0 dropped)" and m["m13"]["parts"]["hall_views"] == 9
    assert m["m14"]["value"] == 0 and m["m15"]["value"] == 1.9 and m["m15"]["parts"]["views"] == 41
    assert m["m16"]["value"] == 0.0                              # a run before Milestone 13: no line
    assert m["m10"]["parts"]["shell_slots_pbr"] == MX.NO_DATA    # maps not recorded in the M11 scene manifest
    assert isinstance(m["m17"]["value"], float) and m["m17"]["value"] > 0
    assert len(result["views"]) == 41 and all(r["score"] != MX.NO_DATA for r in result["views"])


def appended_log(log: dict) -> dict:
    """The toy log after an older run of the same project (``AgentLog`` appends to the volume's ``log.json``): an
    older run of rounds 1-3 with 4 findings in its round 3 and one accepted edit, then the toy run renumbered after
    it with ``run_first_seq`` = its first seq."""
    old = [{"seq": 1, "round": 1, "kind": "finding", "source": "code", "checklist": "F8", "severity": "major",
            "target": "f_5", "evidence": {"metrics": {}}},
           {"seq": 2, "round": 1, "kind": "edit", "tool": "move_piece", "target": "f_5", "checklist": "F8",
            "validation": {"accepted": True}},
           {"seq": 3, "round": 2, "kind": "finding", "source": "code", "checklist": "F8", "severity": "major",
            "target": "f_5", "evidence": {"metrics": {}}}]
    old += [{"seq": 4 + i, "round": 3, "kind": "finding", "source": "code", "checklist": c, "severity": "major",
             "target": t, "evidence": {"metrics": {"depth_m": 0.2}}}
            for i, (c, t) in enumerate((("F8", "f_5"), ("LG", "f_3"), ("LG", "f_6"), ("S2", "f_2")))]
    shift = len(old)
    new = [dict(e, seq=int(e["seq"]) + shift) for e in log["events"]]
    return dict(log, events=old + new, run_first_seq=shift + 1)


def test_metrics_6_and_7_read_the_latest_run_of_an_appended_log(tmp_path):
    """Fix round after P3: the volume's orchestrator log keeps every run (P3's real04 log.json: run_first_seq 2925 of
    4363 events). The old code read every event: m6 came from the older run's last round (round 3 here; P3: the M12
    round 7, 123 as the baseline) and m7 counted the older run's edits. Now only seq >= run_first_seq counts."""
    out = make_run(tmp_path)
    path = out / "orchestrator" / "log.json"
    path.write_text(json.dumps(appended_log(agent_log())), encoding="utf-8")
    m = MX.metrics(out)["metrics"]
    assert m["m6"]["parts"]["round"] == 2 and m["m6"]["value"] == 3 and m["m6"]["parts"]["LG"] == 1
    assert m["m6"]["parts"]["run_first_seq"] == 8 and m["m7"]["parts"]["run_first_seq"] == 8
    assert m["m7"]["parts"]["judged"] == 2 and m["m7"]["parts"]["accepted"] == 2 and m["m7"]["parts"]["gone"] == 1
    run = MX.locate(out)
    assert run.log_first_seq == 8 and len(run.log["events"]) == len(agent_log()["events"])
    assert any("the latest run from seq 8" in w for w in run.warnings)
    # a log without run_first_seq (or 1) keeps every event, also events without a seq (a hand-built log)
    plain = agent_log()
    for e in plain["events"]:
        e.pop("seq")
    path.write_text(json.dumps(plain), encoding="utf-8")
    m2 = MX.metrics(out)["metrics"]
    assert m2["m6"]["value"] == 3 and m2["m7"]["parts"]["judged"] == 2 and m2["m6"]["parts"]["run_first_seq"] == 1


@pytest.mark.skipif(not (ROOT / "runs" / "20261016-172855-full" / "results" / "agent" / "real04" / "log.json").is_file(),
                    reason="the P3 run folder is not here (runs/ is not committed)")
def test_metrics_2_6_7_on_the_p3_results():
    """P3 attempt 2 (real04): the analysis numbers of docs/milestone13.md §14.8 (m6 38 in round 4, m7 29 of 39, m2
    178 of 202 without the explained non-furniture) instead of the M12 round 7 (123) and 52 of 199."""
    m = MX.metrics(ROOT / "runs" / "20261016-172855-full" / "results" / "final" / "real04")["metrics"]
    assert m["m6"]["value"] == 38 and m["m6"]["parts"]["round"] == 4 and m["m6"]["parts"]["run_first_seq"] == 2925
    # fix round after P4a (integration): metric 7 follows the agent's own rule (edits_removing_finding of
    # edits_with_target); the old 29 of 39 counted an edit whose (checklist, target) its round did not have as gone
    assert m["m7"]["text"].startswith("22 of 39 (56 %)") and m["m7"]["parts"]["accepted"] == 39
    assert m["m2"]["text"] == "178 of 240 (74 %); without the 38 explained non-furniture pieces: 178 of 202 (88 %)"
    assert m["m2"]["parts"]["explained_by"] == {"column": 10, "decor": 4, "detail": 18, "not_furniture": 2, "rug": 4}


@pytest.mark.skipif(not (ROOT / "runs" / "20261017-072801-full" / "results" / "agent" / "real02" / "log.json").is_file(),
                    reason="the P4a run folder is not here (runs/ is not committed)")
def test_metric_7_on_the_p4a_results_is_the_agents_own_count():
    """Fix round after P4a (integration of the agent track's ask): metric 7 keys an edit as the agent's metric does
    (``agent.metrics.edit_target_keys``): P4a's 4 set_lighting edits log the room while their findings are on cameras.
    The report and the agent's metrics now give the same 17 of 24 (the old metric 7: 17 of 25, the old agent metric:
    13 of 25)."""
    from wenart.agent import metrics as AM

    out = ROOT / "runs" / "20261017-072801-full" / "results" / "final" / "real02"
    m = MX.metrics(out)["metrics"]
    assert m["m7"]["text"].startswith("17 of 24 (71 %)") and m["m7"]["parts"]["accepted"] == 25
    run = MX.locate(out)
    events = [e for e in run.log["events"] if isinstance(e, dict)]
    rounds = sorted({int(e.get("round") or 0) for e in events if e.get("kind") == "round"})
    removed = AM.findings_removed_metrics(events, rounds)
    assert (removed["edits_removing_finding"], removed["edits_with_target"]) == (17, 24)


def test_metric_2_leaves_out_the_explained_non_furniture(tmp_path):
    """Fix round after P3 (the analysis of metric 2): unbuilt drawn pieces that the pipeline explained as no
    furniture (an outline, a detail, a column, decor; both AI passes not_furniture; a counter-leg detail) are left
    out of the second number. An untyped piece, one AI pass alone, or a built piece stays in. The §7 number stays the
    value. Fails on the old code (no such part)."""
    from wenart.ingest.generic import reading as RD

    assert MX.EXPLAINED_AS == RD.EXPLAINED_AS
    out = make_run(tmp_path)
    b = json.loads((out / "building_final.json").read_text(encoding="utf-8"))
    none = {"library": "none", "asset_id": "none:x", "method": "none", "licence": "n/a"}
    para = {"library": "parametric", "asset_id": "parametric:unknown", "method": "parametric", "licence": "n/a"}
    nf = [{"type": "not_furniture", "pass": 1}, {"type": "not_furniture", "pass": 2}]
    b["furniture"] += [
        piece("f_8", "sink_kitchen", "r_mutfak", build=False, asset=none, inferred_as="detail"),
        piece("f_9", "unknown", "r_salon", build=False, asset=para, type_candidates=nf),
        piece("f_10", "unknown", "r_mutfak", build=False, asset=para,
              not_built_reason="detail inside a kitchen counter leg (an appliance front or drawers, M11 split): "
                               "not built"),
        piece("f_11", "unknown", "r_salon", build=False, asset=para,
              not_built_reason="untyped (CLAUDE.md: no untyped piece is built)"),
        piece("f_12", "unknown", "r_salon", build=False, asset=para,
              type_candidates=[{"type": "not_furniture", "pass": 1}, {"type": "sofa", "pass": 2}]),
        piece("f_13", "rug", "r_salon", asset=asset_abo("abo_B0RUG01", "Wool Rug"), inferred_as="rug"),
    ]
    (out / "building_final.json").write_text(json.dumps(b), encoding="utf-8")
    m = MX.metrics(out)["metrics"]["m2"]
    # drawn: 5 + 6 = 11; built: 4 + the rug = 5; explained: f_8, f_9, f_10 (the built rug f_13 is never left out)
    assert m["value"] == round(100 * 5 / 11, 1) and m["parts"]["explained"] == 3
    assert m["parts"]["explained_by"] == {"detail": 2, "not_furniture": 1}
    assert m["parts"]["furniture"] == 8 and m["parts"]["built_of_furniture"] == 62.5
    assert m["text"] == "5 of 11 (45 %); without the 3 explained non-furniture pieces: 5 of 8 (62 %)"
    assert MX.explained_not_furniture(b["furniture"][-1]) is None


def test_final_moves_previews_and_plans_of_cameras_this_run_does_not_have(tmp_path):
    """Fix round after P3: P3's final/ on the volume kept the M12 previews and plan crops of cam_r_L0_koridor_2/3 (no
    such cameras in the P3 scene); the old code only listed them, so the results copy took them as P3 renders. Now
    they move to final/earlier_run/ (never deleted, a second one with the same name gets _2), the warning and the
    manifest name them, and the results copy holds only this run's views. Contact sheets stay listed."""
    from wenart.run.projects import ProjectRef

    out = make_run(tmp_path)
    F.write_final(out)
    final = out / "final"
    for name in ("cam_gone_final_preview.jpg", "cam_gone_plan.jpg", "contact_L9.jpg"):
        (final / name).write_bytes(b"old")
    manifest = F.write_final(out)
    assert not (final / "cam_gone_final_preview.jpg").exists() and not (final / "cam_gone_plan.jpg").exists()
    assert (final / "earlier_run" / "cam_gone_final_preview.jpg").read_bytes() == b"old"
    assert (final / "earlier_run" / "cam_gone_plan.jpg").is_file()
    assert manifest["earlier_run_files"] == ["cam_gone_final_preview.jpg", "cam_gone_plan.jpg"]
    assert "final/cam_gone_final_preview.jpg is from an earlier run (not part of this report): moved to " \
        "final/earlier_run/cam_gone_final_preview.jpg" in manifest["warnings"]
    assert (final / "contact_L9.jpg").is_file()                                   # listed, not moved
    assert "final/contact_L9.jpg is from an earlier run (not part of this report)" in manifest["warnings"]
    assert (final / "cam_salon_1_final_preview.jpg").is_file()                    # this run's views stay
    assert F.validate_final_manifest(manifest) == []
    # a second stale file of the same name never overwrites the first; a clean re-run moves nothing
    (final / "cam_gone_plan.jpg").write_bytes(b"older")
    again = F.write_final(out)
    assert again["earlier_run_files"] == ["cam_gone_plan.jpg"]
    assert (final / "earlier_run" / "cam_gone_plan_2.jpg").read_bytes() == b"older"
    assert F.write_final(out)["earlier_run_files"] == []
    # the results copy takes this run's previews only (earlier_run/ is no copy rule's folder)
    results = tmp_path / "results"
    ref = ProjectRef(name="toy", private=False, project_dir=tmp_path / "projects" / "toy", out_dir=out,
                     results_dir=results)
    CP.copy_project(ref)
    copied = {f.name for f in (results / "final" / "toy").iterdir()}
    assert "cam_salon_1_final_preview.jpg" in copied and not any(n.startswith("cam_gone") for n in copied)
    assert not (results / "final" / "toy" / "earlier_run").exists()


def _view_files(folder: Path) -> list[str]:
    return sorted(f.name for f in folder.iterdir() if f.name.endswith(("_final_preview.jpg", "_plan.jpg"))) \
        if folder.is_dir() else []


def _toy_ref(tmp_path: Path, out: Path):
    from wenart.run.projects import ProjectRef
    return ProjectRef(name="toy", private=False, project_dir=tmp_path / "projects" / "toy", out_dir=out,
                      results_dir=tmp_path / "results")


def test_results_copies_before_and_after_the_report_hold_only_this_runs_views(tmp_path):
    """Fix round after P3, part 2 (review of part 1): full.sh's first copy runs minutes before the report. It took
    the leftovers of an older run (no manifest names them) and the earlier run's views into the job's results, and the
    copy only added files, so they stayed next to the new views although the report moved them on the volume later.
    Now: the first copy takes only the views the volume's newest manifest names; once this run has a stage record that
    manifest names nothing and those copies move to earlier_run/ of the results; after this run's report the results'
    final folder holds exactly the views of its manifest."""
    out = make_run(tmp_path)
    (out / "check").mkdir()
    for cam in ("cam_salon_1", "cam_hol_1"):
        Image.new("RGB", (64, 48), (255, 255, 255)).save(out / "check" / f"{cam}_plan.jpg")
    earlier = F.write_final(out)                                  # the earlier run (20261015-000000-full)
    final = out / "final"
    for name in ("cam_gone_final_preview.jpg", "cam_gone_plan.jpg"):        # an older run's leftovers
        (final / name).write_bytes(b"m12")
    ref = _toy_ref(tmp_path, out)
    res = tmp_path / "results" / "final" / "toy"
    stamp = tmp_path / "logs" / "copy.stamp"
    named = sorted({v[k] for v in earlier["views"] for k in ("preview", "plan") if v[k]})
    assert "cam_hol_1_plan.jpg" in named and "cam_hol_1_final_preview.jpg" in named
    # the job's first copy (the pod setup: no record of this run yet): the earlier manifest's views, no leftover
    CP.copy_results([ref], stamp)
    assert _view_files(res) == named
    # this run's stages: their records carry its run id, and its render drops cam_hol_1
    rm = json.loads((out / "renders" / "render_manifest.json").read_text(encoding="utf-8"))
    rm["renders"] = [e for e in rm["renders"] if e["camera"] != "cam_hol_1"]
    (out / "renders" / "render_manifest.json").write_text(json.dumps(rm), encoding="utf-8")
    (out / "check" / "cam_hol_1_plan.jpg").unlink()
    for stage in ("build", "render", "agent"):
        path = out / "run" / f"{stage}.json"
        rec = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps(dict(rec, run_id="20261017-000000-full", started_utc="2026-10-17T00:00:00Z")),
                        encoding="utf-8")
    CP.copy_results([ref], stamp)
    assert _view_files(res) == [] and _view_files(res / "earlier_run") == named     # moved, never deleted
    manifest = F.write_final(out)                                 # this run's report
    assert manifest["run_id"] == "20261017-000000-full"
    assert manifest["earlier_run_files"] == ["cam_gone_final_preview.jpg", "cam_gone_plan.jpg",
                                             "cam_hol_1_final_preview.jpg", "cam_hol_1_plan.jpg"]
    CP.copy_results([ref], stamp)
    this = sorted({v[k] for v in manifest["views"] for k in ("preview", "plan") if v[k]})
    assert _view_files(res) == this and "cam_hol_1_final_preview.jpg" not in this and "cam_salon_1_plan.jpg" in this
    CP.copy_results([ref])                                        # the EXIT trap's full copy
    assert _view_files(res) == this
    assert json.loads((res / "final_manifest.json").read_text(encoding="utf-8"))["run_id"] == "20261017-000000-full"
    assert not any("cam_gone" in f.name for f in (tmp_path / "results").rglob("*"))


def test_needs_review_report_moves_earlier_previews_and_plans_and_the_copy_takes_none(tmp_path):
    """Fix round after P3, part 2 (review of part 1): part 1 moved an earlier run's previews and plan crops only on
    the rendered path; a later run that ended needs_review left them in final/ and the results copy shipped them. A
    needs-review report writes no view: every preview and plan crop moves to final/earlier_run/, the manifest lists
    them (earlier_run_files, in its schema), contact sheets and debug images stay listed, and the copy takes none (an
    earlier copy of this job in the results moves to earlier_run/ there)."""
    from test_report import make_review_project

    out = make_review_project(tmp_path)
    final = out / "final"
    final.mkdir(parents=True, exist_ok=True)
    for name in ("cam_old_final_preview.jpg", "cam_old_plan.jpg", "contact_L0.jpg"):
        (final / name).write_bytes(b"earlier")
    res = tmp_path / "results" / "final" / "toy"
    res.mkdir(parents=True)
    (res / "cam_old_final_preview.jpg").write_bytes(b"earlier")          # copied earlier in this job
    m = F.write_final(out)
    assert m["status"] == "needs_review" and F.validate_final_manifest(m) == []
    assert _view_files(final) == []
    assert (final / "earlier_run" / "cam_old_final_preview.jpg").read_bytes() == b"earlier"
    assert (final / "earlier_run" / "cam_old_plan.jpg").is_file()
    assert m["earlier_run_files"] == ["cam_old_final_preview.jpg", "cam_old_plan.jpg"]
    assert json.loads((final / "final_manifest.json").read_text(encoding="utf-8"))["earlier_run_files"] == \
        m["earlier_run_files"]
    assert "final/cam_old_plan.jpg is from an earlier run (not part of this report): moved to " \
        "final/earlier_run/cam_old_plan.jpg" in m["warnings"]
    assert (final / "contact_L0.jpg").is_file()                                  # listed, not moved
    assert "final/contact_L0.jpg is from an earlier run (not part of this report)" in m["warnings"]
    assert "moved to final/earlier_run/cam_old_final_preview.jpg" in (final / "final_report.md").read_text("utf-8")
    assert F.validate_final_manifest(dict(m, earlier_run_files=[1]))           # a typed key of the schema
    CP.copy_project(_toy_ref(tmp_path, out))
    assert _view_files(res) == [] and (res / "final_manifest.json").is_file()
    assert _view_files(res / "earlier_run") == ["cam_old_final_preview.jpg"]


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


def test_final_report_without_a_scene_reads_the_run_building_for_the_licence_mode(tmp_path):
    """Fails on the old code: when the build failed (no scene manifest) the report loaded no building, so it stated
    "Licence mode: commercial" for a relaxed run with HSSD pieces and listed nothing as built below library level
    (CPU pre-flight of 16 Oct 2026, the real02/03/04 outputs without a scene)."""
    out = tmp_path / "real04"
    out.mkdir()
    building = {"project": {"id": "real04", "licence_mode": "relaxed", "licence_mode_source": "given to the fit"},
                "rooms": [{"id": "r_salon", "room_type": "living"}],
                "furniture": [{"id": "f_1", "type": "sofa", "room_id": "r_salon", "source": "from_documents",
                               "asset": {"method": "library", "asset_id": "hssd_x", "licence_flag": "non_commercial"}},
                              {"id": "f_2", "type": "tv_unit", "room_id": "r_salon", "source": "added_by_ai",
                               "asset": {"method": "parametric", "asset_id": "parametric:tv_unit"}}]}
    (out / "building_final.json").write_text(json.dumps(building), encoding="utf-8")
    inp = F.load_inputs(out)
    assert inp.scene is None and inp.building is not None
    assert F.licence_mode_of(inp.building) == ("relaxed", "given to the fit")
    manifest = F.write_final(out)
    assert manifest["licence"]["mode"] == "relaxed"
    assert [b["id"] for b in manifest["below_library"]] == ["f_2"]
    # Review: nothing was rendered, so the project line claims nothing (it said "commercial-safe: yes" over no view
    # for a building with an HSSD piece) and names the building's flagged assets.
    assert manifest["licence"]["line"] == ("commercial-safe: not determined (no rendered view; the building holds 1 "
                                           "flagged asset(s))")
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "Project: commercial-safe: not determined" in md and "Project: commercial-safe: yes" not in md


# --------------------------------------------------------------------------
# Round 4 (before pod P3's second attempt): the views too dark for the EV cap
# --------------------------------------------------------------------------

def darken(out: Path) -> None:
    """Give the toy run two views the +3 cap held, with the render's own records (``render.lighting_dark_entry``):
    the hall at the CPU pre-flight's real04 basement salon numbers (wanted +6.37 EV, incident p50 0.010868: critical)
    and the kitchen at +3.87 (major); the hall's room got the agent's set_lighting x3."""
    from wenart.blender import render as R
    path = out / "renders" / "render_manifest.json"
    rm = json.loads(path.read_text(encoding="utf-8"))
    rm["exposure_limits"] = [-2.0, 3.0]
    wanted = {"cam_hol_1": (6.3718, 0.010868), "cam_mutfak_1": (3.8672, 0.05)}
    rm["lighting_dark"] = []
    for e in rm["renders"]:
        if e["camera"] in wanted:
            raw, p50 = wanted[e["camera"]]
            rec = R.lighting_dark_entry(e["camera"], e["room_id"], raw, 3.0, (-10.3808, 3.0), p50)
            e["exposure"].update(ev=3.0, ev_raw=raw, at_limit=True, lighting_dark=rec)
            e["lighting_dark"] = rec
            rm["lighting_dark"].append(rec)
    path.write_text(json.dumps(rm), encoding="utf-8")
    bpath = out / "building_final.json"
    b = json.loads(bpath.read_text(encoding="utf-8"))
    b["agent_overrides"] = {"lighting": {"r_hol": {"factor": 3.0, "reason": "the hall is dark"}}}
    bpath.write_text(json.dumps(b), encoding="utf-8")


def test_the_final_report_lists_the_views_too_dark_for_the_ev_cap(tmp_path):
    """Fails on the old code: render.py writes lighting_dark per view and in the manifest's list (§13.2: "for the T8
    report"), but the report did not read it; a view held at +3 showed "+3.00 (limit)" like any other."""
    from wenart.blender import render as R
    assert F.LIGHTING_DARK_CHECK == R.LIGHTING_DARK_CHECK
    out = make_run(tmp_path)
    darken(out)
    manifest = F.write_final(out)
    assert F.validate_final_manifest(manifest) == []
    block = manifest["lighting"]
    assert block["cap_ev"] == 3.0 and block["critical"] == 1 and block["major"] == 1 and block["recorded"]
    rows = {r["camera"]: r for r in block["views"]}
    assert list(rows) == ["cam_mutfak_1", "cam_hol_1"]                                   # the views' order
    hol = rows["cam_hol_1"]
    assert (hol["severity"], hol["ev_wanted"], hol["ev_used"], hol["ev_cap"], hol["stops_over_cap"]) == \
        ("critical", 6.3718, 3.0, 3.0, 3.3718)
    assert hol["room_id"] == "r_hol" and hol["set_lighting_factor"] == 3.0 and hol["incident_p50"] == 0.010868
    assert rows["cam_mutfak_1"]["severity"] == "major" and rows["cam_mutfak_1"]["set_lighting_factor"] is None
    assert manifest["summary"]["lighting_dark"] == {"views": 2, "critical": 1, "major": 1}
    views = {v["camera"]: v for v in manifest["views"]}
    assert views["cam_hol_1"]["lighting_dark"]["check"] == "lighting_dark" and views["cam_salon_1"]["lighting_dark"] \
        is None
    assert any(f.startswith("2 view(s) too dark for the EV cap (lighting_dark: 1 critical, 1 major): cam_mutfak_1 "
                            "metered +3.87 EV, cam_hol_1 metered +6.37 EV") for f in manifest["advisory_flags"])
    text = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "| views too dark for the EV cap (lighting_dark) | 2 (1 critical, 1 major) |" in text
    assert "## Views too dark for the EV cap (Milestone 13)" in text
    assert "2 view(s) whose metered exposure passed the cap +3.00 EV (1 critical, 1 major" in text
    assert "| cam_hol_1 | r_hol | critical | +6.37 | +3.00 | +3.00 | 3.37 | 0.01087 | x3 |" in text
    assert "| cam_mutfak_1 | r_mutfak | major | +3.87 | +3.00 | +3.00 | 0.87 | 0.05000 | - |" in text
    assert "+3.00 (cap; metered +6.37)" in text                                          # the per-view EV column
    # a run without the records (Milestone 11 / 12): nothing listed, said so
    plain = make_run(tmp_path / "plain")
    m2 = F.write_final(plain)
    assert m2["lighting"]["views"] == [] and m2["summary"]["lighting_dark"] == {"views": 0, "critical": 0, "major": 0}
    assert "a run before Milestone 13" in (plain / "final" / "final_report.md").read_text(encoding="utf-8")


def test_metric_9_reads_the_lighting_dark_records(tmp_path):
    """Fails on the old code: metric 9 read the EV used, so a view the +3 cap held never reached the "EV >= +5" count
    and the gap between lit and daylight rooms shrank to the cap (P1: the real02 kitchen metered +9.2, capped +3.0).
    Now the lighting_dark record's metered EV is counted, from the final manifest or the render manifest."""
    out = make_run(tmp_path)
    darken(out)
    m = MX.metrics(out)["metrics"]["m9"]                         # the render manifest (no final manifest yet)
    # cam_salon_2 (6.0, as before) and the hall metered +6.37: 2 of 4 interior views at EV >= +5
    assert m["value"] == 2 and m["parts"]["cameras"] == ["cam_salon_2", "cam_hol_1"]
    assert m["parts"]["lighting_dark"] == 2 and m["parts"]["lighting_dark_critical"] == 1
    assert m["parts"]["lighting_dark_cameras"] == ["cam_hol_1", "cam_mutfak_1"]
    # rooms without a window (kitchen 3.87, hall 6.37: median 5.12) vs the salon views (1.5, 6.0: median 3.75)
    assert m["parts"]["median_ev_no_window"] == 5.12 and m["parts"]["ev_gap"] == 1.37
    assert m["text"].endswith("; 2 view(s) held at the EV cap (lighting_dark: 1 critical, 1 major), counted at their "
                              "metered EV")
    F.write_final(out)
    result = MX.metrics(out)
    assert result["metrics"]["m9"]["parts"]["cameras"] == ["cam_salon_2", "cam_hol_1"]   # the final manifest's views
    rows = {r["camera"]: r for r in result["views"]}
    assert rows["cam_hol_1"]["ev"] == 3.0 and rows["cam_hol_1"]["ev_metered"] == 6.37
    assert rows["cam_hol_1"]["lighting_dark"] == "critical" and rows["cam_salon_1"]["lighting_dark"] is None


# --------------------------------------------------------------------------
# Fix round after P4a (17 Oct 2026): sheets, metric 11, the report's Attribution section
# --------------------------------------------------------------------------

def test_sheet_labels_sit_on_a_dark_box_and_the_grey_tile_text_below_them(tmp_path):
    """Fails on the old code: on P4a's ext_5 sheet the "after" label (light text, no backing) vanished on the white
    sky, and on ext_6.001 "before" and "before: no preview" were drawn over each other at the same spot."""
    white = tmp_path / "white.jpg"
    Image.new("RGB", (W, H), (250, 250, 250)).save(white, quality=95)
    sheet = np.asarray(SH.compose(None, white, [("cam", SH.TEXT)])).astype(int)
    x0 = round(SH.TILE_HEIGHT * 16 / 9) + SH.GAP + SH.MARGIN          # where the "after" label starts
    assert sheet[10:22, x0 - 3:x0 - 1].max() < 40                     # the dark box around it, on a white image
    assert sheet[10:22, x0:x0 + 40].min() < 40 and sheet[10:22, x0:x0 + 40].max() > 200   # light text on the box
    left = np.asarray(SH._tile(None, "before")).astype(int)
    band = left[:SH.TILE_TEXT_Y - 4, 80:400]                           # right of the label box, above the tile text
    assert (np.abs(band - np.array(SH.MISSING_TILE)) <= 1).all()     # nothing drawn over the label row
    assert left[SH.TILE_TEXT_Y:SH.TILE_TEXT_Y + 22, SH.MARGIN:300].max() > 200    # the tile's own text below it


def test_long_caption_lines_wrap_instead_of_being_cut():
    """Fails on the old code: P4a's salon, banyo_2 and mutfak captions were cut with "..." after 150 characters, so
    flagged asset ids of the commercial-safe line were missing on the sheet."""
    ids = [f"hssd_{i:040d}" for i in range(3)]
    line = "after:  commercial-safe: no (flagged assets: " + ", ".join(f"{a} [non_commercial]" for a in ids) + ")"
    font = SH._font(16)
    width = 2 * round(SH.TILE_HEIGHT * 16 / 9) + SH.GAP - 2 * SH.MARGIN
    lines = SH.wrap(line, font, width)
    assert 2 <= len(lines) <= SH.CAPTION_MAX_LINES and not any(x.endswith("...") for x in lines)
    assert " ".join(x.strip() for x in lines) == line                # nothing cut: every id is on the sheet
    assert all(x.startswith(SH.CAPTION_INDENT) for x in lines[1:])
    sheet = SH.compose(None, None, [("cam_r_L-1_salon_1  (r_L-1_salon, living)", SH.TEXT),
                                    ("before: commercial-safe: not recorded", SH.NOT_RECORDED_COLOUR),
                                    (line, SH.FLAGGED_COLOUR)])
    assert sheet.height == SH.TILE_HEIGHT + 6 + SH.LINE_HEIGHT * (2 + len(lines)) + 3 > \
        SH.TILE_HEIGHT + SH.CAPTION_HEIGHT
    # a line longer than three sheet lines ends with the pointer to sheets13.md
    many = SH.wrap(" ".join(f"hssd_{i:040d} [non_commercial]," for i in range(40)), font, width)
    assert len(many) == SH.CAPTION_MAX_LINES and many[-1].endswith(SH.MORE)


def test_commercial_safe_colours_tell_not_recorded_from_flagged():
    """Fails on the old code: "commercial-safe: not recorded" contains ": no" and was drawn in the flagged orange."""
    assert SH._colour("commercial-safe: not recorded") == SH.NOT_RECORDED_COLOUR
    assert SH._colour("no view in this run") == SH.NOT_RECORDED_COLOUR
    assert SH._colour("commercial-safe: no (flagged assets: x [tool_nc])") == SH.FLAGGED_COLOUR
    assert SH._colour("commercial-safe: yes") == SH.SAFE_COLOUR


def test_sheets_use_only_previews_of_the_baseline_reports_views(tmp_path):
    """Fails on the old code: the M11 baseline folder holds cam_r_L1_koridor_2_1/2/3 previews of an earlier run (its
    final manifest has 41 views without them); the sheets showed them as "before" while the caption said "no view in
    this run". Now only a camera of the baseline's views gets its preview; the file found by name is named as left out
    on the sheet, in the record and in the index."""
    after = make_run(tmp_path / "a", "toy")
    F.write_final(after)
    before = make_run(tmp_path / "b", "toy")                 # renders/ holds a preview of every camera
    bf = before / "final"
    (bf / "final_manifest.json").write_text(json.dumps({"views": [
        {"camera": c, "room_id": r, "view_kind": "interior"} for c, r, *_ in CAMERAS[:3]]}), encoding="utf-8")
    for cam, *_ in CAMERAS[:3]:
        Image.new("RGB", (W, H), (200, 50, 50)).save(bf / f"{cam}_final_preview.jpg", quality=80)
    out = tmp_path / "sheets"
    result = SH.sheets(after, before, out)
    rec = {r["camera"]: r for r in result["records"]}
    assert result["missing_before"] == ["cam_hol_1", "ext_1"]
    assert [(r["camera"], Path(r["file"]).name) for r in result["before_left_out"]] == \
        [("cam_hol_1", "cam_hol_1_preview.jpg"), ("ext_1", "ext_1_preview.jpg")]
    assert rec["cam_hol_1"]["before"] is None and rec["cam_hol_1"]["before_left_out"].endswith("cam_hol_1_preview.jpg")
    assert rec["cam_salon_1"]["before"].endswith("cam_salon_1_final_preview.jpg") and \
        rec["cam_salon_1"]["before_left_out"] is None
    left = Image.open(out / result["sheets"]["cam_hol_1"]).convert("RGB").getpixel((400, 300))
    assert all(abs(a - b) <= 12 for a, b in zip(left, SH.MISSING_TILE)), left      # the grey tile, not the old file
    index = (out / SH.INDEX_MD).read_text(encoding="utf-8")
    assert "Baseline previews left out" in index and "- cam_hol_1: `" in index


def _no_drawn_trees(out: Path, vegetation=None, tree_objects=()) -> None:
    """The toy run without drawn trees; the scene holds ``vegetation`` records and tree objects (``(id, veg_method)``)."""
    bpath = out / "building_final.json"
    b = json.loads(bpath.read_text(encoding="utf-8"))
    b["site"]["decor"] = []
    b["site"]["hedges"] = []
    bpath.write_text(json.dumps(b), encoding="utf-8")
    spath = out / "scene" / "scene_manifest.json"
    sc = json.loads(spath.read_text(encoding="utf-8"))
    if vegetation is None:
        sc["site"].pop("vegetation", None)
    else:
        sc["site"]["vegetation"] = vegetation
    sc["objects"] += [obj(tid, tid, "site_decor", None, site_kind="tree", **({"veg_method": m} if m else {}))
                      for tid, m in tree_objects]
    spath.write_text(json.dumps(sc), encoding="utf-8")


def test_metric_11_counts_the_inferred_trees_when_none_is_drawn(tmp_path):
    """Fails on the old code: P4a's real02 has no drawn tree; its two inferred olive trees are Poly Haven models, but
    metric 11 said "no data" (the CLI listed it so) and "trees built 2 of 0". The M11 lollipop trees (tree objects
    without a vegetation record) were never counted as primitives."""
    p4a = make_run(tmp_path / "p4a")
    _no_drawn_trees(p4a, [{"id": "tree_tree_inferred_1", "kind": "tree", "method": "polyhaven", "species": "olive"},
                          {"id": "tree_tree_inferred_2", "kind": "tree", "method": "polyhaven", "species": "olive"}],
                    [("tree_tree_inferred_1", "polyhaven"), ("tree_tree_inferred_2", "polyhaven")])
    m = MX.metrics(p4a)["metrics"]["m11"]
    assert m["value"] == 100.0 and m["parts"]["tree_basis"] == "scene"
    assert (m["parts"]["trees_scene"], m["parts"]["trees_scene_real"], m["parts"]["trees_drawn"]) == (2, 2, 0)
    assert m["text"].startswith("no drawn tree; trees in the scene (inferred) as real geometry 2 of 2 (100 %); "
                                "hedges 1 built of 0 drawn rows; black pixels in the site view 50.0 % (ext_1)")
    m11 = make_run(tmp_path / "m11")                         # M11: parametric trees, no vegetation record
    _no_drawn_trees(m11, None, [("tree_tree_inferred_1", None), ("tree_tree_inferred_2", None)])
    m = MX.metrics(m11)["metrics"]["m11"]
    assert m["value"] == 0.0 and m["text"].startswith("no drawn tree; trees in the scene (inferred) as real geometry "
                                                      "0 of 2 (0 %)")
    bare = make_run(tmp_path / "bare")                       # no tree drawn or built: still no share
    _no_drawn_trees(bare, [])
    m = MX.metrics(bare)["metrics"]["m11"]
    assert m["value"] == MX.NO_DATA and m["parts"]["tree_basis"] is None
    assert m["text"].startswith("no drawn tree; no tree in the scene; ")
    # drawn trees: the drawn basis, as before (the fake run's oak)
    assert MX.metrics(make_run(tmp_path / "drawn"))["metrics"]["m11"]["parts"]["tree_basis"] == "drawn"


@pytest.mark.skipif(not (RESULTS / "renders" / "real02" / "scene_manifest.json").is_file(),
                    reason="no committed real02 results")
def test_metric_11_on_the_committed_m11_baseline_counts_its_primitive_trees():
    """The M11 run of real02 (the D6 baseline): its two inferred trees are parametric lollipops: 0 of 2 (was "no
    data")."""
    m = MX.metrics(RESULTS / "final" / "real02")["metrics"]["m11"]
    assert m["value"] == 0.0 and m["parts"]["trees_scene"] == 2 and m["parts"]["black_pct"] == 0.0


def test_the_reports_attribution_leaves_out_ai_retouched_when_no_view_was_polished(tmp_path):
    """Fails on the old code: P4a's report listed its Objaverse credits with "changes: ..., rendered, AI-retouched"
    while it shows 48 views and 0 polished (AI polish is off in Milestone 13)."""
    out = make_run(tmp_path)
    bpath = out / "building_final.json"
    b = json.loads(bpath.read_text(encoding="utf-8"))
    b["decor"][0]["asset"]["attribution"] += ", AI-retouched"
    bpath.write_text(json.dumps(b), encoding="utf-8")
    manifest = F.write_final(out)
    assert manifest["summary"]["polished"] == 0 and manifest["summary"]["views"] == 5 and F.no_view_polished(manifest)
    assert manifest["attribution"]["credits"][0]["credit"].endswith("rendered, AI-retouched")   # the data is kept
    text = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    section = text.split("## Attribution", 1)[1].split("## Added-object detector", 1)[0]
    assert "rendered, AI-retouched" not in section and "changes: scaled to the drawn footprint, re-oriented, " \
        "rendered (used for dec_1)" in section
    assert "No view of this run was AI-retouched (0 of 5 views polished)" in section
    # a report with a polished view keeps the catalogue's change list
    polished = dict(manifest, summary=dict(manifest["summary"], polished=1))
    assert not F.no_view_polished(polished)
    assert any("rendered, AI-retouched (used for dec_1)" in line for line in F.m7_model_lines(polished))


def test_sheet_note_names_a_camera_the_agent_moved_off_its_replayed_pose():
    """Integration of the fix round after P4a: P4a's ext_6 (replayed from M11) was moved by the agent's set_camera;
    the build keeps the old pose in ``replaced_replayed`` and the sheet says the two frames are two poses."""
    moved = {"name": "ext_6", "kind": "exterior", "source": "searched", "policy": "agent",
             "position": [-14.42, 7.08, 1.6], "target": [3.0, 2.0, 2.5],
             "agent": {"action": "set", "reason": "a 3/4 corner view"},
             "replaced_replayed": {"position": [5.21, 19.88, 1.6], "target": [5.2, 4.0, 2.5], "lens_mm": 26.0,
                                   "view": "frontal", "sides": ["back"]},
             "replay": {"status": "repitched", "pitch_deg_old": -10, "pitch_deg": -5, "lens_mm": 26,
                        "lens_mm_old": 26, "horizon_frac_old": 0.6, "horizon_frac": 0.5}}
    note = SH.camera_note(moved)
    assert note == ("camera moved by the agent from (5.2, 19.9, 1.6) to (-14.4, 7.1, 1.6): not the baseline pose "
                    "(a 3/4 corner view)")
    no_pose = dict(moved, position=None, agent={})
    assert SH.camera_note(no_pose) == "camera moved by the agent: not the baseline pose"
    plain = {k: v for k, v in moved.items() if k != "replaced_replayed"}
    assert SH.camera_note(plain).startswith("replayed aerial re-pitched")    # the re-pitch note is unchanged
    assert SH.camera_note({"name": "ext_1", "source": "replayed"}) is None


def test_the_final_report_names_the_views_that_look_into_the_sun(tmp_path):
    """Fix round after P4a (integration of the render track's ask): the render records ``sky_pull.into_sun`` and
    ``sun_offset_deg`` (real02: ext_1 6.0 and ext_5 5.5 degrees off the sun, a white sky at any pull); the report lists
    them in the lighting block and the section, so the white sky reads as the sun's place."""
    out = make_run(tmp_path)
    path = out / "renders" / "render_manifest.json"
    rm = json.loads(path.read_text(encoding="utf-8"))
    for e in rm["renders"]:
        if e["camera"] == "ext_1":
            e["sky_pull"] = {"k": 0, "ev": 0.0, "sun_offset_deg": 6.0, "into_sun": True, "rule": "no pull"}
        elif e["camera"] == "cam_salon_1":
            e["sky_pull"] = {"k": 2, "ev": -2.0, "sun_offset_deg": 95.0, "into_sun": False, "rule": "pulled"}
    path.write_text(json.dumps(rm), encoding="utf-8")
    manifest = F.write_final(out)
    assert F.validate_final_manifest(manifest) == []
    assert manifest["lighting"]["into_sun"] == [{"camera": "ext_1", "sun_offset_deg": 6.0, "k": 0}]
    text = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    assert "Views that look into the sun" in text and "ext_1 (6.0 degrees off the sun, sky pull k 0)" in text
    assert F.validate_final_manifest(dict(manifest, lighting=dict(manifest["lighting"], into_sun=[{"camera": 1}])))


# --------------------------------------------------------------------------
# Fix round after P4b (17 Oct 2026, the library lens of the P4b analysis): the second recognition pass in
# ATTRIBUTION.md and in the report's models table; metric 12 counts a dropped-then-re-added camera once and metric 11
# measures black pixels only in an aerial or site view.
# --------------------------------------------------------------------------

def _check_models() -> dict:
    from wenart.vision_check.config import load_config
    return load_config()["models"]


def _questions(folder: Path, models: dict, answered: dict, n: int = 3) -> None:
    """``folder/requests.json`` with ``n`` symbol questions and the ``models``; ``answers_<slug>.json`` per entry of
    ``answered`` (slug -> how many questions have JSON data; the next one has an error)."""
    folder.mkdir(parents=True, exist_ok=True)
    items = [{"key": f"sym_L0_00{i}", "task": "symbol_type", "input_sha256": f"h{i}"} for i in range(1, n + 1)]
    C.write_json(folder / "requests.json", {"schema_version": "0.1", "kind": "recognition_requests",
                                            "models": models, "items": items})
    for slug, k in answered.items():
        calls = {it["key"]: {"data": {"type": "bed_double", "confidence": 0.9}, "error": None} for it in items[:k]}
        if k < n:
            calls[items[k]["key"]] = {"data": None, "error": "timeout"}
        C.write_json(folder / f"answers_{slug}.json", {"schema_version": "0.1", "kind": "recognition_answers",
                                                        "slug": slug, "calls": calls})


def test_attribution_tools_name_every_recognition_model_with_the_check_yaml_licence():
    """Fails on the old code: P4b's real03 ATTRIBUTION.md listed 9 tools and no GLM-4.6V-Flash, the second recognition
    pass (66 of 72 answers on real03, MIT per the Hugging Face model API and docs/plan.md)."""
    cfg = _check_models()
    tools = {t["name"]: t for t in CP.TOOLS_AND_GENERATORS}
    for key in ("glm", "qwen"):                        # the recognition passes (wenart.recognition.answers MODEL_KEYS)
        row = tools.get(cfg[key]["id"])
        assert row is not None, key
        assert row["licence"] == cfg[key]["licence"] and row["url"] == f"https://huggingface.co/{cfg[key]['id']}"
        assert f"models.{key}" in row["role"]
    tools_text = sections(CP.attribution_text("x", fake_credits(), mode="relaxed"))["1. Tools and generators"]
    assert ("- zai-org/GLM-4.6V-Flash: MIT (https://huggingface.co/zai-org/GLM-4.6V-Flash); recognition of plan "
            "symbols and sheet regions (pass 2") in tools_text


def test_the_final_report_and_attribution_list_the_recognition_models(tmp_path):
    """Fails on the old code: P4b's report table listed only the check agent Qwen3.8-27B-FP8 (the models came from the
    polish and check manifests alone), so the run's ATTRIBUTION.md ("Models recorded by this run's final report") had
    no recognition model either."""
    cfg = _check_models()
    out = make_run(tmp_path)
    models = {key: {"id": cfg[key]["id"], "slug": cfg[key]["slug"], "pass": p} for key, p in (("qwen", 1), ("glm", 2))}
    _questions(out / "recognition", models, {cfg["qwen"]["slug"]: 3, cfg["glm"]["slug"]: 2})
    manifest = F.write_final(out)
    assert F.validate_final_manifest(manifest) == []
    rows = {m["role"]: m for m in manifest["models"]}
    assert rows["recognition pass 2"] == {
        "role": "recognition pass 2", "repo": "zai-org/GLM-4.6V-Flash", "revision": cfg["glm"]["revision"],
        "licence": "MIT", "source": "recognition/requests.json (2 of 3 answered)", "questions": 3, "answered": 2}
    assert rows["recognition pass 1"]["repo"] == cfg["qwen"]["id"] and rows["recognition pass 1"]["answered"] == 3
    assert rows["recognition pass 1"]["licence"] == "Apache-2.0"
    table = (out / "final" / "final_report.md").read_text(encoding="utf-8").split("## Models and licences", 1)[1]
    assert (f"| recognition pass 2 | zai-org/GLM-4.6V-Flash | {cfg['glm']['revision']} | MIT | "
            "recognition/requests.json (2 of 3 answered) |") in table
    text = CP.attribution_text("x", [dict(m, kind="run_model") for m in CP.run_model_rows(out)], mode="relaxed")
    assert (f"- recognition pass 2: zai-org/GLM-4.6V-Flash @ {cfg['glm']['revision'][:12]} (MIT)"
            in sections(text)["1. Tools and generators"])


def test_recognition_model_rows_skip_silent_models_and_unpinned_ids_and_read_the_base_of_a_variant(tmp_path):
    """A model named in requests.json that answered nothing is no model of these images; a model whose id is not the
    one check.yaml pins for its key gets no revision or licence (never a borrowed one); the sheet-region questions of
    the same model add to its row; a variant output with no questions of its own reads its base project's."""
    cfg = _check_models()
    base = tmp_path / "out"
    other = {"id": "zai-org/GLM-other", "slug": "glm-other", "pass": 2}
    _questions(base / "recognition", {"qwen": {"id": cfg["qwen"]["id"], "slug": cfg["qwen"]["slug"], "pass": 1},
                                      "glm": other}, {cfg["qwen"]["slug"]: 0, "glm-other": 1})
    _questions(base / "sheets", {"glm": other}, {"glm-other": 2})
    rows = F.recognition_model_rows(base)
    assert rows == [{"role": "recognition pass 2", "repo": "zai-org/GLM-other", "revision": None, "licence": None,
                     "source": "recognition/requests.json (1 of 3 answered); sheets/requests.json (2 of 3 answered)",
                     "questions": 6, "answered": 3}]
    variant = base / "variants" / "v1"
    variant.mkdir(parents=True)
    assert F.recognition_model_rows(variant, base) == rows and F.recognition_model_rows(variant) == []
    assert F.recognition_model_rows(tmp_path / "none") == []
    _questions(variant / "recognition", {"glm": other}, {"glm-other": 3})     # its own questions win over the base's
    assert [r["source"] for r in F.recognition_model_rows(variant, base)] == \
        ["recognition/requests.json (3 of 3 answered)"]


def _scene_cameras_edit(out: Path, **ext1) -> None:
    """The fake run's scene manifest with ``ext1`` merged into camera ext_1 (None values remove a key) and the
    ``cameras_dropped`` given as ``dropped``."""
    path = out / "scene" / "scene_manifest.json"
    sc = json.loads(path.read_text(encoding="utf-8"))
    dropped = ext1.pop("dropped", None)
    for c in sc["cameras"]:
        if c["name"] == "ext_1":
            c.update({k: v for k, v in ext1.items() if v is not None})
            for k in [k for k, v in ext1.items() if v is None]:
                c.pop(k, None)
    if dropped is not None:
        sc["cameras_dropped"] = dropped
    path.write_text(json.dumps(sc), encoding="utf-8")


ROOF_REASON = "flat_cut roof (upper floors not drawn): no aerial view"


def test_metric_12_and_11_on_a_re_added_camera_and_no_site_view(tmp_path):
    """Fails on the old code. Metric 12: P4b (real03) reported "6 of 8 (2 dropped)": ext_6 was dropped (frontal, too
    small) and the agent's "set ext_6" re-created it, so it was in both lists; here ext_1 plays ext_6 and ext_5 is the
    aerial view dropped for the flat_cut roof: 1 of 2, 1 dropped, ext_1 re-added. Metric 11: P4b reported "black
    pixels 1.9 % (ext_6)", the window glass of an eye-level 3/4 view, because no aerial or site camera existed; now no
    data, with the drop reason."""
    out = make_run(tmp_path)
    _scene_cameras_edit(out, view="agent", agent={"action": "set", "reason": "a 3/4 corner view"}, dropped=[
        {"name": "ext_5", "kind": "exterior", "view": "aerial", "dropped": True, "dropped_reason": ROOF_REASON},
        {"name": "ext_1", "kind": "exterior", "view": "frontal", "dropped": True,
         "dropped_reason": "35.0 m in front of the front (entrance) facade: the building fills 8% of the frame"}])
    m = MX.metrics(out)["metrics"]
    m12 = m["m12"]
    assert m12["text"] == "1 of 2 (1 dropped: ext_5; re-added after the drop: ext_1 (agent))" and m12["value"] == 1
    assert (m12["parts"]["planned"], m12["parts"]["dropped"], m12["parts"]["re_added"]) == (2, 1, ["ext_1"])
    assert m12["parts"]["dropped_cameras"] == ["ext_5"] and m12["parts"]["not_planned"] == []
    m11 = m["m11"]
    assert m11["parts"]["black_pct"] == MX.NO_DATA and m11["parts"]["site_camera"] is None
    assert m11["parts"]["black_basis"] == "none"
    assert m11["parts"]["black_reason"] == f"no aerial or site view: ext_5 (aerial) dropped: {ROOF_REASON}"
    assert m11["text"].endswith(f"black pixels in the site view no data (no aerial or site view: ext_5 (aerial) "
                                f"dropped: {ROOF_REASON})")
    assert m11["value"] == 100.0                        # the tree share is unchanged (the drawn oak, a real model)
    # no aerial camera planned at all; a long drop reason is cut
    _scene_cameras_edit(out, dropped=[])
    assert MX.metrics(out)["metrics"]["m11"]["parts"]["black_reason"] == \
        "no aerial or site view: no aerial or site camera planned"
    _scene_cameras_edit(out, dropped=[{"name": "ext_9", "view": "site", "dropped_reason": "x" * 400}])
    reason = MX.metrics(out)["metrics"]["m11"]["parts"]["black_reason"]
    assert reason.startswith("no aerial or site view: ext_9 (site) dropped: xxx") and reason.endswith("...")
    assert len(reason) == len("no aerial or site view: ext_9 (site) dropped: ") + MX.DROP_REASON_CHARS


def test_metric_12_lists_a_rendered_camera_that_no_plan_names_apart(tmp_path):
    """Fails on the old code: P4a (real02) reported "7 of 6": a duplicate camera rendered as "ext_6.001" was counted
    as one of the planned exterior views."""
    out = make_run(tmp_path)
    path = out / "renders" / "render_manifest.json"
    rm = json.loads(path.read_text(encoding="utf-8"))
    ext = next(e for e in rm["renders"] if e["camera"] == "ext_1")
    rm["renders"].append(dict(ext, camera="ext_1.001", preview="ext_1_preview.jpg"))
    path.write_text(json.dumps(rm), encoding="utf-8")
    m12 = MX.metrics(out)["metrics"]["m12"]
    assert m12["text"] == "1 of 1 (0 dropped); also rendered, not a planned camera: ext_1.001"
    assert m12["value"] == 1 and m12["parts"]["not_planned"] == ["ext_1.001"]


def test_metric_11_keeps_the_darkest_exterior_only_for_a_run_that_records_no_view_kind(tmp_path):
    """The M12 real04 baseline has no scene manifest and its final views carry no exterior_view: the old rule (the
    exterior preview with most black) stays and the text says so. A site view named only by the final manifest's
    exterior_view is measured as the site view."""
    out = make_run(tmp_path)
    _scene_cameras_edit(out, view=None)
    m11 = MX.metrics(out)["metrics"]["m11"]
    assert (m11["parts"]["black_pct"], m11["parts"]["site_camera"], m11["parts"]["black_basis"]) == \
        (50.0, "ext_1", "darkest exterior")
    assert m11["text"].endswith("black pixels in the site view 50.0 % (ext_1, the darkest exterior: the run records "
                                "no view kinds)")
    _scene_cameras_edit(out, view="aerial")
    F.write_final(out)                                  # the final manifest records exterior_view "aerial"
    (out / "scene" / "scene_manifest.json").unlink()
    m11 = MX.metrics(out)["metrics"]["m11"]
    assert (m11["parts"]["black_pct"], m11["parts"]["site_camera"], m11["parts"]["black_basis"]) == \
        (50.0, "ext_1", "site view")
    assert m11["text"].endswith("black pixels in the site view 50.0 % (ext_1)")


RUN_P4B = ROOT / "runs" / "20261017-091212-full" / "results"


@pytest.mark.skipif(not (RUN_P4B / "final" / "real03" / "final_manifest.json").is_file(),
                    reason="no P4b results in runs/")
def test_metrics_11_and_12_on_the_p4b_real03_results():
    """The P4b run of real03 (runs/20261017-091212-full): 6 of 7 (ext_5 dropped, ext_6 re-added by the agent), no site
    view (the aerial ext_5 was dropped for the flat_cut roof)."""
    m = MX.metrics(RUN_P4B / "final" / "real03")["metrics"]
    assert m["m12"]["text"] == "6 of 7 (1 dropped: ext_5; re-added after the drop: ext_6 (agent))"
    assert m["m11"]["parts"]["black_pct"] == MX.NO_DATA and m["m11"]["parts"]["black_reason"] == \
        "no aerial or site view: ext_5 (aerial) dropped: flat_cut roof (upper floors not drawn): no aerial view"
