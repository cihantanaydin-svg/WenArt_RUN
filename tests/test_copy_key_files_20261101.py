"""1 Nov 2026 (real04 run 20261101-093151-full): building_final.json and scene_manifest.json grew past the 8 MB text
limit, the results copy left them out, and the copy of the job's first minutes (made from the volume's outputs of the
run before) stayed in the results, so the metrics and Argus read the run before's building. The project's key records
now go up to MAX_KEY_TEXT_BYTES (under the runner's 20 MB file cap), and a results copy whose source is left out moves
to ``earlier_run/`` (never deleted). CPU only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from test_run_copy import put, refs  # noqa: E402

from wenart.run import copy as CP  # noqa: E402


def test_key_records_have_the_larger_limit_under_the_runner_cap():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gpu_run", ROOT / "scripts" / "gpu_run.py")
    G = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(G)
    assert CP.MAX_TEXT_BYTES < CP.MAX_KEY_TEXT_BYTES < G.COLLECT_MAX_FILE
    for name in ("building_final.json", "scene_manifest.json", "render_manifest.json", "building_agent.json"):
        assert CP.text_limit(name) == CP.MAX_KEY_TEXT_BYTES
    assert CP.text_limit("decor_report.md") == CP.MAX_TEXT_BYTES


def test_a_key_record_over_8_mb_is_copied(tmp_path):
    results, pub, _ = refs(tmp_path)
    put(pub.out_dir / "building_final.json", size=CP.MAX_TEXT_BYTES + 10)
    put(pub.out_dir / "scene" / "scene_manifest.json", size=CP.MAX_TEXT_BYTES + 10)
    CP.copy_project(pub)
    assert (results / "furniture" / "p" / "building_final.json").stat().st_size == CP.MAX_TEXT_BYTES + 10
    assert (results / "renders" / "p" / "scene_manifest.json").stat().st_size == CP.MAX_TEXT_BYTES + 10


def test_an_earlier_copy_of_a_file_now_over_its_limit_moves_aside(tmp_path):
    results, pub, _ = refs(tmp_path)
    src = put(pub.out_dir / "notes.json", data={"run": "before"})
    CP.copy_project(pub)                                   # the job's first copy: the run before's small file
    copied = results / "furniture" / "p" / "notes.json"
    assert copied.is_file()
    put(src, size=CP.MAX_TEXT_BYTES + 1)                   # this run writes it again, over the limit
    CP.copy_project(pub)
    assert not copied.exists()                             # no stale copy beside this run's files
    moved = results / "furniture" / "p" / CP.STALE_COPY_DIR / "notes.json"
    assert moved.is_file() and "before" in moved.read_text()
    put(src, size=CP.MAX_TEXT_BYTES + 2)                   # a later copy: nothing more to move, nothing lost
    CP.copy_project(pub)
    assert moved.is_file() and not copied.exists()


def test_a_file_within_its_limit_is_never_moved(tmp_path):
    results, pub, _ = refs(tmp_path)
    put(pub.out_dir / "notes.json", data={"run": "this"})
    CP.copy_project(pub)
    CP.copy_project(pub)
    assert (results / "furniture" / "p" / "notes.json").is_file()
    assert not (results / "furniture" / "p" / CP.STALE_COPY_DIR).exists()
