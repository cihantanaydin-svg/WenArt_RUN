"""``python -m wenart.run copy``: public mapping and filters, the private allow-list, ``--since`` stamps and the
count-only output (docs/milestone6.md §2.1)."""
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
