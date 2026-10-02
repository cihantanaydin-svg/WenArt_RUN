"""vLLM server sessions with a fake process and a fake clock (docs/milestone6.md §1.4)."""
from __future__ import annotations

import subprocess
import sys
import time

import pytest

from wenart.run import servers as SV
from wenart.vision_check.config import load_config


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


class FakeProc:
    def __init__(self, exit_after=None, ignore_term=False):
        self.pid = 4242
        self.exit_after = exit_after          # poll() returns 1 after this many polls
        self.ignore_term = ignore_term
        self.polls = 0
        self.rc = None
        self.signals = []

    def poll(self):
        self.polls += 1
        if self.exit_after is not None and self.polls > self.exit_after:
            self.rc = 1
        return self.rc

    def terminate(self):
        self.signals.append("TERM")
        if not self.ignore_term:
            self.rc = -15

    def kill(self):
        self.signals.append("KILL")
        self.rc = -9

    def wait(self, timeout=None):
        if self.rc is None:
            raise subprocess.TimeoutExpired("vllm", timeout)
        return self.rc


class Spawner:
    def __init__(self, proc):
        self.proc = proc
        self.calls = []

    def __call__(self, cmd, env, log_path):
        self.calls.append((cmd, env, log_path))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("\n".join(f"line {i}" for i in range(100)) + "\n")
        return self.proc


def make(tmp_path, proc, healthy_after=None, **kw):
    clock = FakeClock()
    checks = {"n": 0}

    def health():
        checks["n"] += 1
        return healthy_after is not None and checks["n"] > healthy_after

    lines = []
    spawn = Spawner(proc)
    srv = SV.VLMServer(kw.pop("key", "qwen"), logs_dir=tmp_path / "logs", job_dir=tmp_path / "job", spawn=spawn,
                       health=health, clock=clock, sleep=clock.sleep, out=lines.append, vllm="VLLM", **kw)
    return srv, spawn, clock, lines


def test_serve_command_from_check_yaml():
    models = load_config()["models"]
    q, g = models["qwen"], models["glm"]
    assert SV.serve_command("VLLM", q["id"], q["revision"], q["server_flags"], 2) == [
        "VLLM", "serve", q["id"], "--revision", q["revision"], "--served-model-name", q["id"], "--port", "8001",
        "--limit-mm-per-prompt", '{"image":2}', "--gpu-memory-utilization", "0.90", "--quantization", "fp8",
        "--max-model-len", "8192", "--max-num-seqs", "2"]
    assert SV.serve_command("VLLM", g["id"], g["revision"], g["server_flags"], 4)[13:] == [
        "--reasoning-parser", "glm45", "--max-model-len", "16384", "--max-num-seqs", "4"]
    assert "--revision" not in SV.serve_command("VLLM", "m", "", "", 2)
    assert SV.check_field("glm", "server_flags") == "--reasoning-parser glm45"
    assert SV.check_field("qwen", "id") == q["id"] and SV.check_field("qwen", "nope") == ""
    with pytest.raises(KeyError):
        SV.check_field("llama", "id")


def test_sequences_follow_the_vram():
    assert SV.server_seqs(32607) == 2 and SV.server_seqs(24564) == 2 and SV.server_seqs(None) == 2
    assert SV.server_seqs(40000) == 4 and SV.server_seqs(97887) == 4
    assert SV.server_args(2) == ["--quantization", "fp8", "--max-model-len", "8192", "--max-num-seqs", "2"]
    assert SV.server_args(4) == ["--max-model-len", "16384", "--max-num-seqs", "4"]
    assert SV.gpu_mem_from_text("[wenart.run] x\n32607\n") == 32607 and SV.gpu_mem_from_text("") == 0
    assert SV.NVIDIA_SMI_QUERY == ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"]


def test_ready_pid_file_env_and_stop(tmp_path):
    proc = FakeProc()
    srv, spawn, clock, lines = make(tmp_path, proc, healthy_after=3)
    url = srv.start()
    assert url == "http://127.0.0.1:8001/v1"
    assert srv.seconds_to_ready == 30.0                      # health every 10 s, ready at the 4th check
    cmd, env, log_path = spawn.calls[0]
    assert cmd[:3] == ["VLLM", "serve", "Qwen/Qwen3-VL-8B-Instruct"] and env["VLLM_USE_FLASHINFER_SAMPLER"] == "0"
    assert log_path == tmp_path / "logs" / "vllm-qwen.log"
    assert (tmp_path / "job" / "vllm.pid").read_text().strip() == "4242"
    srv.stop()
    assert proc.signals == ["TERM"] and not (tmp_path / "job" / "vllm.pid").exists()


def test_early_exit_writes_the_log_tail(tmp_path):
    srv, spawn, clock, lines = make(tmp_path, FakeProc(exit_after=2))
    with pytest.raises(SV.ServerError) as err:
        srv.start()
    assert err.value.reason == "early_exit"
    tail = (tmp_path / "job" / "server-qwen.log").read_text().splitlines()
    assert tail == [f"line {i}" for i in range(60, 100)]
    assert "line 99" in lines                                 # no private project: also in the job log
    assert not (tmp_path / "job" / "vllm.pid").exists()


def test_early_exit_private_run_keeps_the_tail_out_of_the_job_log(tmp_path):
    srv, spawn, clock, lines = make(tmp_path, FakeProc(exit_after=0), private=True)
    with pytest.raises(SV.ServerError):
        srv.start()
    assert not any(line.startswith("line ") for line in lines)
    assert (tmp_path / "job" / "server-qwen.log").is_file()


def test_timeout_and_kill(tmp_path):
    proc = FakeProc(ignore_term=True)
    srv, spawn, clock, lines = make(tmp_path, proc, wait_s=100)
    with pytest.raises(SV.ServerError) as err:
        srv.start()
    assert err.value.reason == "timeout" and clock.t - 1000.0 > 100
    assert proc.signals == ["TERM", "KILL"]                   # TERM, wait 60 s, then KILL


def test_deadline_stops_the_start(tmp_path):
    proc = FakeProc()
    srv, spawn, clock, lines = make(tmp_path, proc, deadline=1000.0 + 25)
    with pytest.raises(SV.ServerError) as err:
        srv.start()
    assert err.value.reason == "deadline" and proc.signals == ["TERM"]
    assert 1025 <= clock.t <= 1040


def test_missing_vllm_binary_is_a_server_error(tmp_path):
    def spawn(cmd, env, log_path):
        raise FileNotFoundError(cmd[0])

    srv = SV.VLMServer("qwen", job_dir=tmp_path, logs_dir=tmp_path, spawn=spawn, out=lambda s: None, vllm="/nope")
    with pytest.raises(SV.ServerError) as err:
        srv.start()
    assert err.value.reason == "spawn" and not (tmp_path / "vllm.pid").exists()
    # The real spawner raises the same way for a binary that does not exist.
    with pytest.raises(OSError):
        SV.popen_spawn([str(tmp_path / "no-vllm")], {}, tmp_path / "x.log")


def test_unknown_key_is_a_config_error(tmp_path):
    srv, spawn, clock, lines = make(tmp_path, FakeProc(), key="llama")
    with pytest.raises(SV.ServerError) as err:
        srv.start()
    assert err.value.reason == "config" and not spawn.calls


def test_context_manager_records_stats_and_stops(tmp_path):
    proc = FakeProc()
    clock = FakeClock()
    stats = []
    spawn = Spawner(proc)
    with SV.server("glm", None, stats=stats, logs_dir=tmp_path, job_dir=tmp_path, spawn=spawn, health=lambda: True,
                   clock=clock, sleep=clock.sleep, out=lambda s: None, vllm="VLLM", seqs=4) as url:
        assert url.endswith(":8001/v1") and proc.rc is None
    assert proc.signals == ["TERM"]
    assert stats == [{"key": "glm", "model": "zai-org/GLM-4.6V-Flash", "seqs": 4, "seconds_to_ready": 0.0,
                      "ok": True}]
    assert spawn.calls[0][0][-2:] == ["--max-num-seqs", "4"]
    stats = []
    with pytest.raises(SV.ServerError):
        with SV.server("qwen", None, stats=stats, logs_dir=tmp_path, job_dir=tmp_path, spawn=Spawner(FakeProc(0)),
                       health=lambda: False, clock=clock, sleep=clock.sleep, out=lambda s: None, vllm="VLLM"):
            pass
    assert stats[0]["ok"] is False


def test_external_server():
    stats = []
    with SV.external_server("http://127.0.0.1:9/v1/", "qwen", stats=stats) as url:
        assert url == "http://127.0.0.1:9/v1"
    assert stats[0]["external"] and stats[0]["key"] == "qwen"


def test_real_process_group_is_stopped(tmp_path):
    """popen_spawn + stop on a real child: TERM reaches its process group."""
    proc = SV.popen_spawn([sys.executable, "-c", "import time; time.sleep(60)"], dict(), tmp_path / "x.log")
    assert proc.poll() is None
    srv = SV.VLMServer("qwen", job_dir=tmp_path, out=lambda s: None)
    srv.proc = proc
    t0 = time.time()
    srv.stop()
    assert proc.poll() is not None and time.time() - t0 < 30
    assert not SV.http_health(port=1)                      # nothing listens on port 1
