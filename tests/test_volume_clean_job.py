"""The volume cleanup job (user OK of 12 Oct 2026: "clean old outputs"): on a fake workspace it deletes the old project
outputs and job folders, keeps the newest real04 run, this job, the assets, the growth downloads, the model caches and
the private projects; DRY_RUN=1 only lists."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "volume_clean.sh"


def _ws(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    for d in ("outputs/real03/scene", "outputs/real04/scene", "outputs/synthetic-01", "repo/outputs/real02/scene",
              "repo/outputs/real04/scene", "repo/wenart", "jobs/20261010-000000-full/results",
              "jobs/20261011-153030-full/results", "jobs/clean-1", "outputs-archive/x", ".repo-broken-1/a",
              "assets/models", "library-growth/abo", "hf/hub", "projects-private/p1", "results-private/p1"):
        (ws / d).mkdir(parents=True, exist_ok=True)
        (ws / d / "f.bin").write_bytes(b"x" * 1024)
    return ws


def _run(ws: Path, tmp_path: Path, **env) -> subprocess.CompletedProcess:
    e = dict(os.environ, WENART_WS=str(ws), WENART_RESULTS=str(tmp_path / "results"), JOB_ID="clean-1", **env)
    return subprocess.run(["bash", str(JOB)], env=e, capture_output=True, text=True, timeout=120)


def test_old_outputs_go_and_everything_else_stays(tmp_path):
    ws = _ws(tmp_path)
    dry = _run(ws, tmp_path, DRY_RUN="1")
    assert dry.returncode == 0, dry.stderr
    assert (ws / "outputs/real03").exists() and "would delete" in (tmp_path / "results/volume_clean.txt").read_text()
    res = _run(ws, tmp_path)
    assert res.returncode == 0, res.stderr
    gone = ("outputs/real03", "outputs/synthetic-01", "repo/outputs/real02", "jobs/20261010-000000-full", "outputs-archive", ".repo-broken-1")
    kept = ("outputs/real04", "repo/outputs/real04", "repo/wenart", "jobs/20261011-153030-full", "jobs/clean-1", "assets/models", "library-growth/abo",
            "hf/hub", "projects-private/p1", "results-private/p1")
    assert not any((ws / g).exists() for g in gone)
    assert all((ws / k).exists() for k in kept)
    report = (tmp_path / "results/volume_clean.txt").read_text()
    assert "######## BEFORE" in report and "######## AFTER" in report and "deleted" in report
