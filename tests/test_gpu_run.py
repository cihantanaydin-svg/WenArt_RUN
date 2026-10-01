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
    text = (gpu_run.GPU_LOG).read_text()
    row = {"date": "2026-10-01 12:00", "pod_id": "abc", "gpu": "L4", "minutes": 12, "cost": 0.1,
           "purpose": "smoke", "result": "ok"}
    out = gpu_run.append_gpu_log(text, row)
    out = gpu_run.append_gpu_log(out, dict(row, pod_id="def", cost=0.25))
    assert "| abc |" in out and "| def |" in out
    assert "**Total spent so far: $0.35**" in out
    lines = out.splitlines()
    i = lines.index("|---|---|---|---|---|---|---|")
    assert lines[i + 1].startswith("| 2026-10-01 12:00 | abc |")


def test_pod_create_body():
    b = gpu_run.pod_create_body("n", "NVIDIA L4", "vol1", {"A": "1"}, "EU-RO-1")
    assert b["mounts"]["network"][0] == {"volumeId": "vol1", "path": "/workspace"}
    assert b["dataCenterIds"] == ["EU-RO-1"] and b["ports"] == ["8000/http"]
    assert b["gpu"]["count"] == 1 and b["cloud"] == "SECURE"
    b2 = gpu_run.pod_create_body("n", "NVIDIA L4", None, {}, None)
    assert "mounts" not in b2 and "dataCenterIds" not in b2
