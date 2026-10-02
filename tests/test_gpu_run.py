"""CPU tests for the runner's pure logic (no network)."""
import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("gpu_run", Path(__file__).resolve().parents[1] / "scripts" / "gpu_run.py")
gpu_run = importlib.util.module_from_spec(spec)
sys.modules["gpu_run"] = gpu_run
spec.loader.exec_module(gpu_run)

CATALOG = [
    {"name": "RTX A5000", "id": "NVIDIA RTX A5000", "memory": 24, "price": {"secure": 0.27}, "availability": "NONE"},
    {"name": "L4", "id": "NVIDIA L4", "memory": 24, "price": {"secure": 0.49}, "availability": "LOW"},
    {"name": "RTX 4090", "id": "NVIDIA GeForce RTX 4090", "memory": 24, "price": {"secure": 0.74}, "availability": "LOW"},
    {"name": "H100 SXM", "id": "NVIDIA H100", "memory": 80, "price": {"secure": 2.69}, "availability": "HIGH"},
]
LOG_FIXTURE = """# GPU run log

| Date (UTC) | Pod ID | GPU | Minutes | Cost (USD) | Purpose | Result |
|---|---|---|---|---|---|---|

**Total spent so far: $0.00** (budget: $100; limits: $1.00/GPU-hour, $10/day, 2 h/run)
"""
ROW = {"date": "2026-10-01 12:00", "pod_id": "abc", "gpu": "L4", "minutes": 12, "cost": 0.1,
       "purpose": "smoke", "result": "ok"}


def test_pick_gpu_prefers_priority_order_and_stock():
    g = gpu_run.pick_gpu(CATALOG, None, None)
    assert g["name"] == "L4"  # A5000 has no stock, A40/A6000/PRO 4000 not in catalog


def test_pick_gpu_uses_dc_availability():
    g = gpu_run.pick_gpu(CATALOG, {"RTX A5000": "LOW"}, None)
    assert g["name"] == "RTX A5000"
    with pytest.raises(RuntimeError, match="no stock"):
        gpu_run.pick_gpu(CATALOG, {}, None)


def test_pick_gpu_refuses_expensive():
    with pytest.raises(RuntimeError, match="over the"):
        gpu_run.pick_gpu(CATALOG, None, "H100 SXM")


def test_check_limits():
    gpu_run.check_limits(0.27, 120, 0.0)
    with pytest.raises(RuntimeError):
        gpu_run.check_limits(1.01, 10, 0.0)
    with pytest.raises(RuntimeError):
        gpu_run.check_limits(0.5, 121, 0.0)
    with pytest.raises(RuntimeError, match="day"):
        gpu_run.check_limits(0.9, 120, 9.0)


def test_append_gpu_log_keeps_table_and_total():
    out = gpu_run.append_gpu_log(LOG_FIXTURE, ROW)
    out = gpu_run.append_gpu_log(out, dict(ROW, pod_id="def", cost=0.25))
    assert "| abc |" in out and "| def |" in out
    assert "**Total spent so far: $0.35** (budget: $100;" in out
    lines = out.splitlines()
    i = lines.index("|---|---|---|---|---|---|---|")
    assert lines[i + 1].startswith("| 2026-10-01 12:00 | abc |")
    assert lines[i + 2].startswith("| 2026-10-01 12:00 | def |")


def test_upsert_replaces_provisional_row():
    out = gpu_run.upsert_gpu_log(LOG_FIXTURE, dict(ROW, pod_id="pending:job1", cost=0.98, result="creating"))
    assert "pending:job1" in out and "$0.98" in out
    out = gpu_run.upsert_gpu_log(out, dict(ROW, pod_id="realpod", cost=0.05), key="pending:job1")
    assert "pending:job1" not in out and "| realpod |" in out
    assert "**Total spent so far: $0.05**" in out
    # a missing key falls back to insert
    out = gpu_run.upsert_gpu_log(out, dict(ROW, pod_id="other", cost=0.10), key="nope")
    assert "| other |" in out and "**Total spent so far: $0.15**" in out


def test_local_spent_on_sums_only_that_day():
    out = gpu_run.append_gpu_log(LOG_FIXTURE, ROW)
    out = gpu_run.append_gpu_log(out, dict(ROW, date="2026-09-30 23:59", pod_id="old", cost=1.5))
    assert gpu_run.local_spent_on(out, "2026-10-01") == pytest.approx(0.1)
    assert gpu_run.local_spent_on(out, "2026-09-30") == pytest.approx(1.5)
    assert gpu_run.local_spent_on(out, "2026-10-02") == 0.0


def test_our_pods_filters_by_name_prefix():
    pods = [{"id": "1", "name": "wenart-20261001-smoke", "status": "RUNNING"},
            {"id": "2", "name": "someone-elses-pod", "status": "RUNNING"},
            {"id": "3", "name": None, "status": "EXITED"}]
    assert [p["id"] for p in gpu_run.our_pods(pods)] == ["1"]
    assert [p["id"] for p in gpu_run.live_pods(pods)] == ["1"]


def test_validate_job_path():
    assert gpu_run.validate_job_path("scripts/jobs/smoke.sh") == "scripts/jobs/smoke.sh"
    for bad in ("scripts/jobs/../pod_entry.sh", "/etc/passwd", "scripts/jobs/x.sh; rm -rf /", "scripts/jobs/missing.sh"):
        with pytest.raises(RuntimeError):
            gpu_run.validate_job_path(bad)


def test_pod_create_body():
    b = gpu_run.pod_create_body("n", "NVIDIA L4", "vol1", {"A": "1"}, "EU-RO-1")
    assert b["mounts"]["network"][0] == {"volumeId": "vol1", "path": "/workspace"}
    assert b["dataCenterIds"] == ["EU-RO-1"] and b["ports"] == ["8000/http"]
    assert b["gpu"]["count"] == 1 and b["cloud"] == "SECURE"
    b2 = gpu_run.pod_create_body("n", "NVIDIA L4", None, {}, None)
    assert "mounts" not in b2 and "dataCenterIds" not in b2


def test_parse_listing_separates_files_and_dirs():
    html = ('<ul><li><a href="summary.md">summary.md</a></li><li><a href="synthetic-01/">synthetic-01/</a></li>'
            '<li><a href="a%20b.jpg">a b.jpg</a></li><li><a href="../">../</a></li><li><a href="?C=M">x</a></li></ul>')
    files, dirs = gpu_run.parse_listing(html)
    assert files == ["summary.md", "a b.jpg"] and dirs == ["synthetic-01"]


def test_collect_fetches_the_results_tree_in_parallel(tmp_path, monkeypatch):
    """M5 runs 0/0b: one file at a time took 0.81 s per file through the pod proxy, so the
    500-1000 files of an M5 run outlasted the grace period; files now download in parallel."""
    import threading
    import time as _time

    base = "https://pod-8000.proxy.runpod.net/tok/"
    tree = {"": (["a.json", "b.md"], ["p1"]), "p1/": (["c 1.jpg", "d.jpg", "e.jpg"], ["sub"]),
            "p1/sub/": (["f.json"], [])}
    content = {f"{rel}{name}": f"{rel}{name}".encode() for rel, (files, _) in tree.items() for name in files}
    state = {"active": 0, "peak": 0}
    lock = threading.Lock()

    def listing(files, dirs):
        links = [f'<a href="{gpu_run.urllib.parse.quote(n)}">{n}</a>' for n in files]
        links += [f'<a href="{d}/">{d}/</a>' for d in dirs]
        return ("<html><body>" + "".join(links) + "</body></html>").encode()

    def fake_fetch(url, timeout=20):
        if url in (base + "status.json", base + "job.log"):
            return b"{}"
        rel = gpu_run.urllib.parse.unquote(url[len(base + "results/"):])
        if rel == "" or rel.endswith("/"):
            files, dirs = tree[rel]
            return listing(files, dirs)
        with lock:
            state["active"] += 1
            state["peak"] = max(state["peak"], state["active"])
        _time.sleep(0.05)
        with lock:
            state["active"] -= 1
        return content[rel]

    monkeypatch.setattr(gpu_run, "fetch", fake_fetch)
    n = gpu_run.collect(base, tmp_path, workers=4)
    assert n == len(content) == 6
    for rel, data in content.items():
        assert (tmp_path / "results" / rel).read_bytes() == data
    assert state["peak"] > 1                      # downloads overlapped
