"""Milestone 1 GPU smoke tests. Run on a RunPod pod via scripts/gpu_run.py (pytest -m gpu)."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.gpu
RESULTS = Path(os.environ.get("WENART_RESULTS", "/tmp/wenart-results"))
RESULTS.mkdir(parents=True, exist_ok=True)


def test_gpu_visible():
    import torch
    assert torch.cuda.is_available(), "torch sees no CUDA device"
    name = torch.cuda.get_device_name(0)
    a = torch.randn(2048, 2048, device="cuda")
    b = (a @ a).sum().item()
    assert b == b, "NaN from GPU matmul"
    (RESULTS / "gpu.txt").write_text(f"{name}\ntorch {torch.__version__}\ncuda {torch.version.cuda}\n")


def test_workspace_is_volume_and_writable():
    p = Path("/workspace/jobs/.write-test")
    p.write_text("ok")
    assert p.read_text() == "ok"
    p.unlink()
    (RESULTS / "volume.txt").write_text(f"RUNPOD_VOLUME_ID={os.environ.get('RUNPOD_VOLUME_ID', '')}\n")


def test_hf_token_and_cache():
    from huggingface_hub import hf_hub_download
    assert os.environ.get("HF_TOKEN"), "HF_TOKEN missing (RunPod secret hf_token)"
    assert os.environ.get("HF_HOME", "").startswith("/workspace"), "HF_HOME must be on the volume"
    path = hf_hub_download("Qwen/Qwen3-VL-8B-Instruct", "config.json")
    assert path.startswith("/workspace/hf"), path
    assert Path(path).stat().st_size > 100


def test_blender_cycles_gpu_render(tmp_path):
    blender = shutil.which("blender") or "/workspace/tools/blender/blender"
    out = RESULTS / "cube.png"
    proc = subprocess.run(
        [blender, "-b", "--python", "scripts/blender_smoke.py", "--", str(out)],
        capture_output=True, text=True, timeout=600,
    )
    (RESULTS / "blender.txt").write_text(proc.stdout[-4000:] + proc.stderr[-2000:])
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert out.exists() and out.stat().st_size > 10_000
    device = [l for l in proc.stdout.splitlines() if l.startswith("DEVICE=")]
    assert device and device[0] != "DEVICE=CPU", f"Cycles did not use the GPU: {device}"
    from PIL import Image
    Image.open(out).convert("RGB").save(RESULTS / "cube.jpg", quality=85)
