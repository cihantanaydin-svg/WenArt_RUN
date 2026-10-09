"""The agent models in check.yaml (docs/milestone11.md §11, decisions D2 and D8, contract §17.3): ids, revisions and
licences equal the §11 table (parsed from the markdown, so the spec and the config cannot drift, as
tests/test_m5_config.py does for the M5 table), the serving flags of §11, and the ``vllm serve`` command the
scheduler builds from them (pre-quantized FP8: no ``--quantization``; the model's own size flags; 0.55 of the VRAM;
4 images; sleep mode only when asked)."""
from __future__ import annotations

import re
from pathlib import Path

from wenart.run import servers as SV
from wenart.vision_check.config import load_config

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "milestone11.md"
FLAGS = "--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3"


def table_11() -> dict:
    """``{repo id: (revision, licence)}`` of the §11 model table."""
    text = SPEC.read_text(encoding="utf-8")
    start = text.index("## 11. Model choice")
    section = text[start:text.index("## 12.", start)]
    rows = {}
    for line in section.splitlines():
        m = re.match(r"\|\s*\**`([^`]+)`\** @`([0-9a-f]{40})`[^|]*\|\s*([^|]+?)\s*\|", line)
        if m:
            rows[m.group(1)] = (m.group(2), m.group(3).strip())
    return rows


def test_the_agent_models_equal_the_section_11_table():
    table = table_11()
    models = load_config()["models"]
    assert set(models) >= {"qwen", "glm", "agent", "agent_fast"}
    for key, repo in (("agent", "Qwen/Qwen3.8-27B-FP8"), ("agent_fast", "Qwen/Qwen3.6-35B-A3B-FP8")):
        m = models[key]
        assert m["id"] == repo and (m["revision"], m["licence"]) == table[repo], key
        assert m["server_flags"].startswith(FLAGS) and "--max-model-len 32768 --max-num-seqs 4" in m["server_flags"]
        assert (m["gpu_memory_utilization"], m["limit_mm"], m["prequantized"], m["max_seqs"]) == (0.55, 4, "fp8", 4)
    assert models["agent"]["size_gb"] == 31
    assert models["agent"]["revision"] == "017b9c7af6b5689d5dd426a76e0bc077eb5ca20a"
    assert models["agent_fast"]["revision"] == "95a723d08a9490559dae23d0cff1d9466213d989"
    assert models["agent_fast"]["env"] == {"VLLM_USE_DEEP_GEMM": "0"}


def test_the_agent_serve_command_matches_section_11():
    cmd = SV.VLMServer("agent", seqs=4, mem_mib=97887, vllm="VLLM").command()
    assert cmd == ["VLLM", "serve", "Qwen/Qwen3.8-27B-FP8", "--revision", "017b9c7af6b5689d5dd426a76e0bc077eb5ca20a",
                   "--served-model-name", "Qwen/Qwen3.8-27B-FP8", "--port", "8001", "--limit-mm-per-prompt",
                   '{"image":4}', "--gpu-memory-utilization", "0.55", "--enable-auto-tool-choice",
                   "--tool-call-parser", "qwen3_coder", "--reasoning-parser", "qwen3", "--max-model-len", "32768",
                   "--max-num-seqs", "4"]
    small = SV.VLMServer("agent", seqs=2, mem_mib=24000, vllm="VLLM", sleep_mode=True).command()
    assert "--quantization" not in small and small[-1] == "--enable-sleep-mode"
    # pre-quantized checkpoints never get --quantization fp8, even in the small size tier
    assert "--quantization" not in SV.serve_command("V", "m", "", "", 2, prequantized=True)
    assert "--quantization" in SV.serve_command("V", "m", "", "", 2)
    assert SV.limit_mm_text(None) == '{"image":2}' and SV.limit_mm_text(4) == '{"image":4}'


def test_sleep_and_wake_endpoints(monkeypatch):
    seen = []

    class Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout):
        seen.append((req.full_url, req.get_method()))
        return Resp()

    monkeypatch.setattr(SV.urllib.request, "urlopen", fake_urlopen)
    assert SV.server_control("http://127.0.0.1:8001/v1", "sleep") and SV.server_control("http://127.0.0.1:8001/v1",
                                                                                        "wake")
    assert seen == [("http://127.0.0.1:8001/sleep?level=1", "POST"), ("http://127.0.0.1:8001/wake_up", "POST")]
