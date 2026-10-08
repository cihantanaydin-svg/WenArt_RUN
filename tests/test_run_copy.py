"""``python -m wenart.run copy``: public mapping and filters, the private allow-list, ``--since`` stamps and the
count-only output (docs/milestone6.md §2.1); the Milestone 7 rules (debug and rectified PNGs, recognition
questions, answers and crops, detections, pairs_v2) and ATTRIBUTION.md (docs/milestone7.md §9.1, §7.3)."""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import pytest

from wenart.run import copy as CP
from wenart.run.__main__ import main as run_main
from wenart.run.projects import REPO_ROOT, private_project, public_project

KB = 1024


def put(path: Path, data=b"x", size=None, age=None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if size is not None:
        path.write_bytes(b"x" * size)
    elif isinstance(data, (dict, list)):
        path.write_text(json.dumps(data), encoding="utf-8")
    elif isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)
    if age is not None:
        t = time.time() - age
        os.utime(path, (t, t))
    return path


def fill(out: Path) -> None:
    """An out folder with every kind of file a full run writes."""
    put(out / "building.json", {"rooms": []})
    put(out / "building_final.json", {"rooms": []})
    put(out / "report.md", "# r")
    put(out / "layout_report.md", "# l")
    put(out / "style.json", {})
    put(out / "style_2.json", {})
    put(out / "intake_manifest.json", {"files": ["Yilmaz villa.dxf"]})
    put(out / "huge.json", size=8100 * KB)
    put(out / "style_photos" / "passes.json", {"calls": []})
    put(out / "style_photos" / "photo.jpg", size=10)
    put(out / "layout_debug" / "r1.json", {})
    put(out / "layout_debug" / "r1.png", size=10)
    put(out / "layout_debug" / "r1.jpg", size=10)
    put(out / "debug" / "page_p1.png", size=10)
    put(out / "scene" / "scene_manifest.json", {})
    put(out / "scene" / "scene.blend", size=10)
    put(out / "scene" / "build.log", "\n".join(f"b{i}" for i in range(500)) + "\n")
    put(out / "scene" / "level_L0_top.png", size=10)
    put(out / "renders" / "render_manifest.json", {})
    put(out / "renders" / "cam_a_preview.jpg", size=100 * KB)
    put(out / "renders" / "cam_a_alt_preview.jpg", size=100 * KB)
    put(out / "renders" / "cam_b_preview.jpg", size=301 * KB)       # too big
    put(out / "renders" / "cam_a.png", size=10)
    put(out / "renders" / "cam_a_passes.exr", size=10)
    put(out / "renders" / "render.log", "r\n")
    put(out / "controls" / "render.log", "c\n")
    put(out / "controls" / "hide_f1" / "render_manifest.json", {})
    put(out / "controls" / "hide_f1" / "cam_a_preview.jpg", size=10)
    put(out / "polish" / "polish_manifest.json", {})
    put(out / "polish" / "cam_a_gate.jpg", size=10)
    put(out / "polish" / "sweep" / "sweep.json", {})
    put(out / "gate" / "gate_calibration.json", {})
    put(out / "check" / "answers_qwen3-vl-8b.json", {})
    put(out / "check" / "cam_a_cycles_check.jpg", size=10)
    put(out / "check" / "cam_a_plan.jpg", size=10)
    put(out / "check" / "random.jpg", size=10)
    put(out / "final" / "final_report.md", "# f")
    put(out / "final" / "final_manifest.json", {})
    put(out / "final" / "cam_a_final_preview.jpg", size=10)
    put(out / "final" / "contact_1.jpg", size=10)
    put(out / "final" / "cam_a_plan.jpg", size=10)
    put(out / "final" / "debug" / "page_p1.jpg", size=10)
    put(out / "run" / "pipeline.json", {"kind": "stage_record", "stage": "pipeline", "status": "ok",
                                        "inputs": {"/workspace/projects-private/real-01/a.dxf": "x"}})
    put(out / "run" / "logs" / "pipeline.log", "\n".join(f"p{i}" for i in range(450)) + "\n")
    put(out / "ab" / "renders" / "render_manifest.json", {})
    put(out / "ab" / "renders" / "cam_a_alt_preview.jpg", size=10)
    put(out / "ab" / "cameras_check.json", {"kept": []})
    put(out / "ab" / "pairs.json", {"pairs": []})
    put(out / "ab" / "control_views.json", {})
    put(out / "ab" / "m5" / "scene_manifest.json", {})
    put(out / "check" / "realism" / "answers_qwen3-vl-8b.json", {})
    put(out / "check" / "realism" / "contact_realism_m5_vs_m6_1.jpg", size=10)
    put(out / "input" / "real-01" / "a.dxf", "x")
    # Milestone 7 (§9.1)
    put(out / "debug" / "big_p2.png", size=3 * 1024 * KB + 1)          # over 3 MB
    put(out / "rectified" / "plan_scan_p1.png", size=10)
    put(out / "rectified" / "notes.txt", "x")
    put(out / "recognition" / "requests.json", {"items": []})
    put(out / "recognition" / "answers_glm-4.6v-flash.json", {"calls": {}})
    put(out / "recognition" / "other.json", {})
    put(out / "recognition" / "crops" / "sym_L0_001_ctx.png", size=10)
    put(out / "detect" / "detect_manifest.json", {"views": {}})
    put(out / "detect" / "cam_a.json", {"images": {}})
    put(out / "ab" / "pairs_v2.json", {"pairs": []})
    put(out / "converted" / "plan.dxf", "x")


def files(root: Path) -> set:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} if root.exists() else set()


PUBLIC_WANT = {
    "furniture/p/building.json", "furniture/p/building_final.json", "furniture/p/report.md",
    "furniture/p/layout_report.md", "furniture/p/style.json", "furniture/p/style_2.json",
    "furniture/p/intake_manifest.json", "furniture/p/style_photos/passes.json", "furniture/p/layout_debug/r1.json",
    "furniture/p/layout_debug/r1.jpg",
    "renders/p/style.json", "renders/p/style_2.json", "renders/p/scene_manifest.json", "renders/p/build.log",
    "renders/p/render_manifest.json", "renders/p/cam_a_preview.jpg", "renders/p/cam_a_alt_preview.jpg",
    "renders/p/render.log", "renders/p/controls/render.log", "renders/p/controls/hide_f1/render_manifest.json",
    "renders/p/controls/hide_f1/cam_a_preview.jpg",
    "polish/p/polish_manifest.json", "polish/p/cam_a_gate.jpg", "polish/p/sweep/sweep.json",
    "gate/p/gate_calibration.json",
    "check/p/answers_qwen3-vl-8b.json", "check/p/cam_a_cycles_check.jpg", "check/p/cam_a_plan.jpg",
    "final/p/final_report.md", "final/p/final_manifest.json", "final/p/cam_a_final_preview.jpg",
    "final/p/contact_1.jpg", "final/p/cam_a_plan.jpg", "final/p/debug/page_p1.jpg",
    "run/p/pipeline.json", "run/p/logs/pipeline.log",
    "realism/p/render_manifest.json", "realism/p/cam_a_alt_preview.jpg", "realism/p/cameras_check.json",
    "realism/p/pairs.json", "realism/p/answers_qwen3-vl-8b.json", "realism/p/contact_realism_m5_vs_m6_1.jpg",
    # Milestone 7 (§9.1)
    "furniture/p/debug/page_p1.png", "furniture/p/rectified/plan_scan_p1.png", "recognition/p/requests.json",
    "recognition/p/answers_glm-4.6v-flash.json", "recognition/p/crops/sym_L0_001_ctx.png",
    "check/p/detect/detect_manifest.json", "check/p/detect/cam_a.json", "realism/p/pairs_v2.json",
}
PRIVATE_WANT = {"final/final_report.md", "final/final_manifest.json", "final/cam_a_final_preview.jpg",
                "final/contact_1.jpg", "run/pipeline.json"}


def refs(tmp_path):
    results = tmp_path / "results"
    pub = public_project("synthetic-01", results, REPO_ROOT)
    from dataclasses import replace
    pub = replace(pub, name="p", out_dir=tmp_path / "out" / "p")
    priv = private_project("real-01", tmp_path / "pp", tmp_path / "po", tmp_path / "pr", REPO_ROOT)
    return results, pub, priv


def test_public_mapping_and_filters(tmp_path):
    results, pub, _priv = refs(tmp_path)
    fill(pub.out_dir)
    n = CP.copy_project(pub)
    got = files(results)
    assert got == PUBLIC_WANT, (sorted(got - PUBLIC_WANT), sorted(PUBLIC_WANT - got))
    assert n == len(PUBLIC_WANT) + 0
    # Log tails: the last 400 lines.
    tail = (results / "renders/p/build.log").read_text().splitlines()
    assert tail[0] == "b100" and tail[-1] == "b499" and len(tail) == 400
    assert len((results / "run/p/logs/pipeline.log").read_text().splitlines()) == 400
    # The public stage record keeps its inputs.
    assert "inputs" in json.loads((results / "run/p/pipeline.json").read_text())


def test_private_allow_list_only(tmp_path):
    results, _pub, priv = refs(tmp_path)
    fill(priv.out_dir)
    n = CP.copy_project(priv)
    got = files(tmp_path / "pr" / "real-01")
    assert got == PRIVATE_WANT and n == len(PRIVATE_WANT)
    record = json.loads((tmp_path / "pr/real-01/run/pipeline.json").read_text())
    assert "inputs" not in record and record["status"] == "ok"
    assert not results.exists()
    # Nothing that names an uploaded file left the private outputs.
    for path in (tmp_path / "pr").rglob("*"):
        if path.is_file():
            assert b"Yilmaz" not in path.read_bytes() and b"projects-private" not in path.read_bytes()


def test_since_stamp(tmp_path):
    results, pub, priv = refs(tmp_path)
    old = put(pub.out_dir / "building.json", {"a": 1}, age=3600)
    stamp = tmp_path / "logs" / "copy.stamp"
    first = CP.copy_results([pub, priv], stamp)                 # no stamp yet: a full copy
    assert first == {"public": 1, "private": 0, "full": True}
    assert stamp.is_file() and not stamp.with_name("copy.stamp.next").exists()
    assert stamp.stat().st_mtime <= time.time() - 1.5           # 2 s back
    (results / "furniture/p/building.json").unlink()
    put(pub.out_dir / "style.json", {"b": 2})                     # new since the stamp
    put(priv.out_dir / "final" / "final_report.md", "# private")
    second = CP.copy_results([pub, priv], stamp)
    assert second == {"public": 2, "private": 1, "full": False}  # style.json -> furniture/ and renders/
    assert not (results / "furniture/p/building.json").exists() and old.exists()
    assert (results / "renders/p/style.json").is_file()
    full = CP.copy_results([pub, priv])
    assert full["full"] and full["public"] == 3


def test_cli_prints_counts_only(tmp_path, capsys, monkeypatch):
    out = tmp_path / "outputs"
    fill(out / "synthetic-01")
    fill(tmp_path / "po" / "real-01")
    rc = run_main(["copy", "--projects", "synthetic-01", "--private", "real-01", "--results", str(tmp_path / "R"),
                   "--outputs", str(out), "--private-root", str(tmp_path / "pp"), "--private-outputs",
                   str(tmp_path / "po"), "--private-results", str(tmp_path / "pr"), "--since",
                   str(tmp_path / "stamp")])
    assert rc == 0
    text = capsys.readouterr().out
    assert re.fullmatch(r"copy: \d+ public file\(s\), \d+ private file\(s\) \(full copy\)\n", text), text
    assert files(tmp_path / "pr" / "real-01") == PRIVATE_WANT
    assert (tmp_path / "R" / "final" / "synthetic-01" / "final_report.md").is_file()
    assert not any("real-01" in p for p in files(tmp_path / "R"))
    # A bad alias is refused without being echoed (it may be a client name typed by mistake).
    assert run_main(["copy", "--private", "Client-Villa", "--results", str(tmp_path / "R")]) == 2
    captured = capsys.readouterr()
    assert "Client" not in captured.out + captured.err and "alias #1" in captured.err


def test_rule_kinds():
    with pytest.raises(ValueError):
        CP.wanted(CP.Rule("", "final", "", "nope"), Path(__file__))


def test_copy_lock_is_the_jobs_flock(tmp_path):
    import fcntl
    lock = tmp_path / "logs" / "full-j.copy.lock"
    with CP.copy_lock(None):              # no lock file: no lock
        pass
    with CP.copy_lock(lock):
        assert lock.is_file()
    with open(lock, "a") as fh:           # the copy loop of full.sh holds it (flock 9>"$LOCK")
        fcntl.flock(fh, fcntl.LOCK_EX)
        with pytest.raises(TimeoutError):
            with CP.copy_lock(lock, wait_s=0.2):
                pass


def objaverse_asset(uid, title):
    return {"library": "objaverse", "method": "library", "asset_id": f"objaverse_{uid}", "uid": uid,
            "licence": "CC-BY-4.0", "title": title, "author": "Ana", "source_url": f"https://sketchfab.com/{uid}",
            "attribution": f'"{title}" by Ana (https://sketchfab.com/{uid}), CC BY 4.0 '
                           "(https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, "
                           "ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched"}


def test_recognition_crops_are_capped_at_200(tmp_path):
    results, pub, _priv = refs(tmp_path)
    for i in range(205):
        put(pub.out_dir / "recognition" / "crops" / f"sym_L0_{i:03d}_ctx.png", size=10)
    CP.copy_project(pub)
    crops = sorted(p.name for p in (results / "recognition" / "p" / "crops").iterdir())
    assert len(crops) == CP.MAX_CROPS == 200 and crops[-1] == "sym_L0_199_ctx.png"
    # An incremental copy never adds the crops past the cap either.
    put(pub.out_dir / "recognition" / "crops" / "sym_L0_204_ctx.png", size=11)
    CP.copy_results([pub], tmp_path / "stamp")
    CP.copy_results([pub], tmp_path / "stamp")
    assert len(list((results / "recognition" / "p" / "crops").iterdir())) == 200


def test_attribution_goes_into_every_image_folder(tmp_path):
    results, pub, priv = refs(tmp_path)
    fill(pub.out_dir)
    building = {"furniture": [
        {"id": "f_L0_001", "type": "sofa", "asset": objaverse_asset("u1", "Grey sofa")},
        {"id": "f_L0_002", "type": "sofa", "asset": objaverse_asset("u1", "Grey sofa")},
        {"id": "f_L0_003", "type": "bed_double", "asset": {"library": "polyhaven", "method": "library",
                                                           "asset_id": "GothicBed_01", "licence": "CC0"}},
        {"id": "f_L0_004", "type": "chair", "asset": {"library": "objaverse", "method": "parametric",
                                                      "asset_id": "objaverse_u9"}}]}
    put(pub.out_dir / "building_final.json", building)
    put(pub.out_dir / "gate" / "cam_a_gate.jpg", size=10)
    n = CP.copy_project(pub)
    got = files(results)
    want = {f"{area}/p/{CP.ATTRIBUTION}" for area in ("renders", "polish", "gate", "check", "realism", "final")}
    assert want <= got and n == len(PUBLIC_WANT) + 1 + len(want)
    assert "furniture/p/ATTRIBUTION.md" not in got                     # no rendered image there
    (results / "gate" / "p" / "cam_a_gate.jpg").unlink()
    (results / "gate" / "p" / CP.ATTRIBUTION).unlink()
    (pub.out_dir / "gate" / "cam_a_gate.jpg").unlink()
    CP.copy_project(pub)
    assert not (results / "gate" / "p" / CP.ATTRIBUTION).exists()      # a folder without images gets none
    text = (results / "final" / "p" / CP.ATTRIBUTION).read_text()
    assert text.count('"Grey sofa" by Ana') == 1 and "f_L0_001 (sofa), f_L0_002 (sofa)" in text
    assert "GothicBed_01" not in text and "objaverse_u9" not in text   # CC0 Poly Haven and parametric: no credit
    assert "ODC Attribution License" in text and "CC BY 4.0" in text
    # Unchanged credits are not rewritten (an incremental copy counts nothing new).
    assert CP.write_attributions(pub) == 0
    # A private project: only its final folder, which the allow-list copies.
    fill(priv.out_dir)
    put(priv.out_dir / "building_final.json", building)
    CP.copy_project(priv)
    assert files(tmp_path / "pr" / "real-01") == PRIVATE_WANT | {"final/ATTRIBUTION.md"}
    # A project without Objaverse models gets no file.
    put(pub.out_dir / "building_final.json", {"furniture": [building["furniture"][2]]})
    (results / "final" / "p" / CP.ATTRIBUTION).unlink()
    CP.copy_project(pub)
    assert not (results / "final" / "p" / CP.ATTRIBUTION).exists()


def test_library_attribution_from_the_objaverse_catalogue(tmp_path):
    lib = tmp_path / "library"
    assert CP.library_attribution(lib) is None
    entry = dict(objaverse_asset("u2", "Oak table"), id="objaverse_u2", type="table_dining")
    put(lib / "catalog_objaverse.json", {"kind": "objaverse_catalog", "entries": [entry]})
    path = CP.library_attribution(lib)
    assert path == lib / "ATTRIBUTION.md" and '"Oak table" by Ana' in path.read_text()
    # An entry without the credit line gets one built from its fields, or a visible gap.
    del entry["attribution"]
    entry["licence"] = "CC0"
    put(lib / "catalog_objaverse.json", {"entries": [entry, {"id": "objaverse_u3"}]})
    text = CP.library_attribution(lib).read_text()
    assert '"Oak table" by Ana (https://sketchfab.com/u2), CC0 1.0' in text
    assert "objaverse_u3: no attribution recorded" in text


ABO_LINE = ('"Oak Rug" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), '
            "https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, "
            "re-oriented, rendered, AI-retouched")


def test_attribution_of_every_library_source(tmp_path):
    """docs/milestone8.md §2: the credits cover ABO, Objaverse (with its licence flag) and generated models, the
    furniture pieces and the decor items of building_final.json, and the notices of the sources present."""
    results, pub, _priv = refs(tmp_path)
    fill(pub.out_dir)
    nc = dict(objaverse_asset("u5", "NC chair"), licence="CC-BY-NC-4.0", licence_flag="non_commercial")
    building = {"furniture": [
        {"id": "f_L0_001", "type": "sofa", "asset": {"library": "abo", "method": "library",
                                                     "asset_id": "abo_B072PZ4LVN", "licence": "CC-BY-4.0",
                                                     "attribution": ABO_LINE.replace("Oak Rug", "Revolve Sofa")}},
        {"id": "f_L0_002", "type": "chair", "asset": nc},
        {"id": "f_L0_003", "type": "chair", "asset": {"library": "generated", "method": "library",
                                                      "asset_id": "gen_chair_modern_1_ab12cd34",
                                                      "licence": "generated (TRELLIS.2-4B, MIT)",
                                                      "attribution": '"generated chair": generated with TRELLIS.2-4B '
                                                                     "(MIT) for WenArt_RUN; no third-party credit"}}],
        "decor": [{"id": "d_001", "type": "rug", "asset": {"source": "abo", "asset_id": "abo_B071777YN3",
                                                           "licence": "CC-BY-4.0", "attribution": ABO_LINE}}]}
    put(pub.out_dir / "building_final.json", json.dumps(building).encode())
    credits = CP.project_credits(pub.out_dir)
    assert [c["source"] for c in credits] == ["abo", "abo", "generated", "objaverse"]          # by catalogue id
    CP.copy_project(pub)
    text = (results / "final" / "p" / CP.ATTRIBUTION).read_text()
    assert f"- {ABO_LINE} (used for d_001 (rug))" in text
    assert "Revolve Sofa" in text and "(used for f_L0_001 (sofa))" in text
    assert "NC chair" in text and "[licence flag: non_commercial]" in text
    assert "generated with TRELLIS.2-4B" in text
    assert "Amazon Berkeley Objects, Objaverse 1.0, generated models" in text
    for notice in ("ODC Attribution License", "Contains 3D models and product data from Amazon Berkeley Objects",
                   "Generated models (docs/milestone8.md §3)"):
        assert notice in text, notice


def test_library_attribution_prefers_the_library_catalogue_and_lists_decor(tmp_path):
    lib = tmp_path / "library"
    put(lib / "catalog_objaverse.json", {"entries": [dict(objaverse_asset("u2", "Old table"), id="objaverse_u2")]})
    assert '"Old table" by Ana' in CP.library_attribution(lib).read_text()     # the M7 file alone
    put(lib / "catalog_library.json", {"kind": "library_catalog", "entries": [
        dict(objaverse_asset("u4", "Flagged sofa"), id="objaverse_u4", source="objaverse", licence="CC-BY-SA-4.0",
             licence_flag="share_alike")],
        "decor": [{"id": "abo_B071777YN3", "source": "abo", "licence": "CC-BY-4.0", "attribution": ABO_LINE}]})
    text = CP.library_attribution(lib).read_text()
    assert "Old table" not in text and "Flagged sofa" in text and "[licence flag: share_alike]" in text
    assert f"- {ABO_LINE}" in text and "Amazon Berkeley Objects" in text and "ODC Attribution License" in text
    assert CP.library_catalog_path(lib) == lib / "catalog_library.json"


def test_library_files_leave_model_files_out(tmp_path):
    lib = tmp_path / "library"
    for rel in ("survey_abo.json", "judge/sheets/abo_X.jpg", "generate/plan.json", "generate/images/x.png"):
        put(lib / rel)
    for rel in ("generate/gen_x.glb", "survey.json.tmp", "generate/x.part"):
        put(lib / rel)
    put(lib / "big.json", size=CP.MAX_TEXT_BYTES + 1)
    got = sorted(f.relative_to(lib).as_posix() for f in CP.library_files(lib))
    assert got == ["generate/images/x.png", "generate/plan.json", "judge/sheets/abo_X.jpg", "survey_abo.json"]
    assert CP.library_files(tmp_path / "nowhere") == []


def test_m10_variants_are_copied_with_their_project(tmp_path):
    """Milestone 10 (§1.6b row 9): an alternative's sub-output goes to variants/<id>/ of each area folder; only
    the alternatives that building_final.json lists now."""
    results, pub, priv = refs(tmp_path)
    vid = "l-1b-acik-mutfak"
    for ref in (pub, priv):
        out = ref.out_dir
        put(out / "building_final.json", {"rooms": [], "variants": [{"id": "base"}, {"id": vid}]})
        put(out / "renders" / "render_manifest.json", {"renders": []})
        v = out / "variants" / vid
        put(v / "renders" / "cam_r1_1_preview.jpg", size=10 * KB)
        put(v / "renders" / "render_manifest.json", {"renders": []})
        put(v / "export" / f"p-{vid}.glb", size=10 * KB)
        put(v / "final" / "final_report.md", "# variant")
        put(v / "run" / "build.json", {"kind": "stage_record", "status": "ok", "inputs": {"a": "b"}})
        put(out / "variants" / "l-1c-old" / "final" / "final_report.md", "# an older run's variant")
    CP.copy_project(pub)
    got = files(results)
    assert {f"renders/p/variants/{vid}/cam_r1_1_preview.jpg", f"renders/p/variants/{vid}/render_manifest.json",
            f"final/p/variants/{vid}/3d/p-{vid}.glb", f"final/p/variants/{vid}/final_report.md",
            f"run/p/variants/{vid}/build.json"} <= got
    assert not any("l-1c-old" in f for f in got)
    CP.copy_project(priv)
    got = files(tmp_path / "pr" / "real-01")
    assert {f"final/variants/{vid}/final_report.md", f"run/variants/{vid}/build.json"} <= got
    assert not any(f.endswith(".glb") or "renders" in f for f in got)
    assert "inputs" not in json.loads((tmp_path / "pr" / "real-01" / "run" / "variants" / vid / "build.json")
                                      .read_text())


def test_m10_library_files_copy_the_recolour_folder(tmp_path):
    """Milestone 10 (docs/milestone10.md §4.5): the prep job's copy takes ``<library>/recolour/`` (the judging sheets,
    slots.json, the requests, both models' answers and tags.json, which write-catalog reads on a pod that did not
    make it); the Blender renders of a ``--work`` folder inside the library (model files) stay out."""
    lib = tmp_path / "library"
    keep = ["recolour/slots.json", "recolour/requests.json", "recolour/answers_qwen3-vl-8b.json",
            "recolour/answers_glm-4.6v-flash.json", "recolour/tags.json", "recolour/sheets/u1.jpg",
            "recolour/sheets/u1_p1.jpg"]
    for rel in keep:
        put(lib / rel)
    for rel in ("work/recolour/u1/model.glb", "work/recolour/u1/jobs.tmp"):
        put(lib / rel)
    put(lib / "recolour" / "slots_big.json", size=CP.MAX_TEXT_BYTES + 1)
    got = sorted(f.relative_to(lib).as_posix() for f in CP.library_files(lib))
    assert got == sorted(keep)


def test_m10_sheet_questions_answers_and_debug_images_are_copied(tmp_path):
    """Milestone 10: the sheet_region questions and answers go to recognition/<p>/sheets/ (the next run's seeds),
    the sheet debug images to furniture/<p>/sheets_debug/; a private project copies none of them."""
    results, pub, priv = refs(tmp_path)
    for ref in (pub, priv):
        out = ref.out_dir
        put(out / "sheets.json", {"kind": "sheets"})
        put(out / "sheets_report.md", "# sheets")
        put(out / "sheets" / "requests.json", {"items": []})
        put(out / "sheets" / "answers_qwen3-vl-8b.json", {"answers": {}})
        put(out / "sheets" / "crops" / "sheet_a_r1.png", size=10 * KB)
        put(out / "sheets_debug" / "plan_s1.png", size=10 * KB)
        put(out / "sheets_debug" / "big_s2.png", size=4 * 1024 * KB)
    CP.copy_project(pub)
    got = files(results)
    assert {"furniture/p/sheets.json", "furniture/p/sheets_report.md", "recognition/p/sheets/requests.json",
            "recognition/p/sheets/answers_qwen3-vl-8b.json", "recognition/p/sheets/crops/sheet_a_r1.png",
            "furniture/p/sheets_debug/plan_s1.png"} <= got
    assert "furniture/p/sheets_debug/big_s2.png" not in got                     # over 3 MB
    CP.copy_project(priv)
    assert not any("sheets" in f for f in files(tmp_path / "pr" / "real-01"))
