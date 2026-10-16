"""A/B preparation of the orchestrator (docs/milestone6.md §6.3): M5 files from git and the camera check."""
from __future__ import annotations

import json
import subprocess

import pytest

from wenart.run import ab as AB
from wenart.run.__main__ import main as run_main
from wenart.run.projects import REPO_ROOT
from wenart.run.stages import M5_LOOK_COMMIT


def cam(name, pos=(1.0, 2.0, 1.4), target=(3.0, 2.0, 1.3)):
    return {"name": name, "position": list(pos), "target": list(target)}


def test_cameras_check_rules():
    m5 = {"cameras": [cam("a"), cam("b"), cam("c"), cam("d"), cam("gone")]}
    ab = {"cameras": [cam("a", pos=(1.0009, 2.0, 1.4)), cam("b", pos=(1.0011, 2.0, 1.4)),
                      cam("c", target=(3.0, 2.0, 1.3011)), cam("d"), cam("new")]}
    render = {"renders": [{"camera": n, "preview": f"{n}_preview.jpg"} for n in ("a", "b", "c", "new")]}
    out = AB.cameras_check(m5, ab, render)
    assert out["kept"] == ["a"]
    reasons = {d["cam"]: d["reason"] for d in out["dropped"]}
    assert reasons == {"b": "position differs from M5 by more than 1 mm",
                       "c": "target differs from M5 by more than 1 mm",
                       "d": "not rendered in the A/B render", "gone": "not in the A/B scene",
                       "new": "not an M5 camera"}
    assert AB.cameras_check(m5, ab)["kept"] == ["a", "d"]              # no render manifest: render not checked
    assert out["kind"] == "cameras_check" and out["tolerance_m"] == 0.001


def test_write_cameras_check(tmp_path):
    ab = tmp_path / "ab"
    for sub, data in (("m5/scene_manifest.json", {"cameras": [cam("a"), cam("b")]}),
                      ("scene/scene_manifest.json", {"cameras": [cam("a"), cam("b")]}),
                      ("renders/render_manifest.json", {"renders": [{"camera": "a", "preview": "a_preview.jpg"}]})):
        (ab / sub).parent.mkdir(parents=True, exist_ok=True)
        (ab / sub).write_text(json.dumps(data))
    result = AB.write_cameras_check(tmp_path)
    assert json.loads((ab / "cameras_check.json").read_text()) == result
    assert result["kept"] == ["a"] and result["dropped"][0]["cam"] == "b"
    assert AB.m5_cameras(tmp_path) == ["a", "b"] and AB.m5_cameras(tmp_path / "none") == []


def test_m13_variant_names_keep_the_summary_and_sheets_working(tmp_path):
    """Milestone 13 round 3 (docs/milestone13.md §14.3): the A/B variants are the light variants with ``m11`` (the
    Milestone 11 look) first and ``base`` (production) second; a results folder without a variant's folder (a P1
    folder has no ``m11``) gives a "not rendered" row per view and a grey tile, never an error."""
    from PIL import Image

    from wenart.blender import lighting as L

    assert AB.M13_AB_VARIANTS == L.LIGHT_VARIANTS and AB.M13_AB_VARIANTS[:2] == ("m11", "base")
    res = tmp_path / "ab_m13"
    cam = AB.m13_views("real03")[0]
    d = res / "base" / "real03"
    d.mkdir(parents=True)
    Image.new("RGB", (64, 36), (120, 100, 80)).save(d / f"{cam}_preview.jpg")
    (d / "render_manifest.json").write_text(json.dumps({
        "renders": [{"camera": cam, "seconds": 5.1, "samples": 128, "preview": f"{cam}_preview.jpg", "vram_mib": 2000,
                     "exposure": {"ev": 2.5, "ev_raw": 2.46, "at_limit": False, "incident_p50": 0.16,
                                  "wb_temperature": 5406.0, "wb_mode": "project", "lighting_dark": None}}],
        "light_variant": {"render": "base", "build": "base"}, "exposure_limits": [-2, 3]}))
    summary = AB.lever_summary(res, ("real03",), ("m11", "base"))
    rows = summary["rows"]
    assert [(r["variant"], r["status"]) for r in rows if r["camera"] in (None, cam)] == \
        [("m11", "not rendered"), ("base", "rendered")]
    base_row = next(r for r in rows if r["variant"] == "base" and r["camera"] == cam)
    assert base_row["ev"] == 2.5 and base_row["lighting_dark"] is None and base_row["light_variant"] == "base"
    md = (res / "summary.md").read_text()
    assert "| real03 | m11 | - | not rendered |" in md and f"| real03 | base | {cam} | 5.1 | 2.5 | 2.46 | - |" in md
    sheets = AB.lever_sheets(res, "real03", ("m11", "base"), views=[cam])
    assert len(sheets) == 1 and sheets[0].is_file()
    with Image.open(sheets[0]) as im:
        assert im.width > 2 * 600                                  # the m11 tile (grey) and the base tile


def _has_m5_commit() -> bool:
    proc = subprocess.run(["git", "-C", str(REPO_ROOT), "cat-file", "-e", f"{M5_LOOK_COMMIT}^{{commit}}"],
                          capture_output=True)
    return proc.returncode == 0


@pytest.mark.skipif(not _has_m5_commit(), reason="the M5 look commit is not in this clone")
def test_prepare_m5_from_git(tmp_path):
    from PIL import Image

    info = AB.prepare_m5("synthetic-01", tmp_path)
    assert info["cameras"] == 30 and info["previews"] == 30 and info["missing"] == []
    m5 = tmp_path / "ab" / "m5"
    scene = json.loads((m5 / "scene_manifest.json").read_text())
    assert len(scene["cameras"]) == 30 and (m5 / "render_manifest.json").is_file()
    assert (tmp_path / "ab" / "building_m5.json").read_bytes() == (m5 / "building_final.json").read_bytes()
    committed = AB.git_show(M5_LOOK_COMMIT, "results/furniture/synthetic-01/building_final.json")
    assert (m5 / "building_final.json").read_bytes() == committed
    with Image.open(m5 / f"{scene['cameras'][0]['name']}_preview.jpg") as im:
        assert im.size == (1920, 1080)
    # The CLI the orchestrator starts.
    out2 = tmp_path / "second"
    assert run_main(["ab-m5", "--project", "synthetic-01", "--project-out", str(out2)]) == 0
    assert len(list((out2 / "ab" / "m5").glob("*_preview.jpg"))) == 30


def test_prepare_m5_missing_files(tmp_path, capsys):
    files = {"results/furniture/p/building_final.json": b"{}",
             "results/renders/p/scene_manifest.json": json.dumps({"cameras": [cam("a"), cam("b")]}).encode(),
             "results/renders/p/render_manifest.json": b"{}", "results/renders/p/a_preview.jpg": b"jpg"}

    def show(commit, path):
        if path not in files:
            raise FileNotFoundError(path)
        return files[path]

    info = AB.prepare_m5("p", tmp_path, show=show)
    assert info["previews"] == 1 and info["missing"] == ["b"]
    with pytest.raises(FileNotFoundError):
        AB.prepare_m5("q", tmp_path, show=show)
    assert run_main(["ab-m5", "--project", "no-such-project", "--project-out", str(tmp_path / "x")]) == 1
    assert "ab-m5:" in capsys.readouterr().err
