"""vLLM server sessions of a full run (docs/milestone6.md §1.4).

What: ``with server("qwen", deadline) as url: ...`` starts ``vllm serve`` for
``check.yaml models.<key>``, waits until ``/health`` answers, yields the
OpenAI base URL and stops the server afterwards. It is a port of
``scripts/jobs/polish.sh`` ``start_server`` / ``stop_server`` /
``server_args`` / ``server_seqs`` / ``check_field`` (the proven reference):

- command: ``vllm serve <id> --revision <rev> --served-model-name <id>
  --port 8001 --limit-mm-per-prompt '{"image":2}' --gpu-memory-utilization
  0.90 <server_flags of check.yaml> <size flags>``; size flags below 40 GB of
  VRAM ``--quantization fp8 --max-model-len 8192 --max-num-seqs 2``, else
  ``--max-model-len 16384 --max-num-seqs 4``; env
  ``VLLM_USE_FLASHINFER_SAMPLER=0`` (FlashInfer's sampler failed on sm_120);
- log ``/workspace/logs/vllm-<key>.log`` (the job's EXIT trap copies a
  200-line tail); ``/health`` every 10 s; an early exit writes the last 40
  log lines to ``$WENART_JOB_DIR/server-<key>.log`` (and prints them only
  when no private project is in the run); gives up after ``SERVER_WAIT_S``
  (1500 s) or at the deadline; stop = TERM, wait 60 s, KILL;
- the pid goes to ``$WENART_JOB_DIR/vllm.pid`` (the bash EXIT trap kills it
  if the orchestrator dies), removed after the stop.

``seqs`` (2 or 4) is the ``--workers`` of every VLM stage. ``--vlm-url``
(smoke profile) uses an external server instead (``external_server``).

How: the process start (``spawn``), the health probe, the clock and the
sleep are injectable, so the CPU tests drive a fake process.
"""
from __future__ import annotations

import os
import shlex
import signal
import subprocess
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_YAML = REPO_ROOT / "wenart" / "vision_check" / "check.yaml"
VLM_PORT = 8001
SERVER_WAIT_S = 1500.0
HEALTH_EVERY_S = 10.0
HEALTH_TIMEOUT_S = 5.0
STOP_WAIT_S = 60.0
EARLY_EXIT_LINES = 40
VRAM_SPLIT_MIB = 40000            # below: fp8, 8192 context, 2 sequences (bake-off sizes)
LIMIT_MM = '{"image":2}'          # render + source-plan crop (check), A + B (realism)
GPU_MEMORY_UTILIZATION = "0.90"


class ServerError(RuntimeError):
    """The server did not become ready. ``reason``: early_exit | timeout | deadline | config | spawn."""

    def __init__(self, key: str, reason: str, message: str):
        super().__init__(f"vllm {key}: {message}")
        self.key = key
        self.reason = reason


def check_models(check_yaml: Path = CHECK_YAML) -> dict:
    """``check.yaml models`` (key -> {id, revision, slug, server_flags, ...})."""
    import yaml
    data = yaml.safe_load(Path(check_yaml).read_text(encoding="utf-8")) or {}
    return dict(data.get("models") or {})


def check_field(key: str, field_name: str, check_yaml: Path = CHECK_YAML) -> str:
    """One value of ``check.yaml models.<key>`` as text ('' when unset); KeyError for an unknown key."""
    value = check_models(check_yaml)[key].get(field_name)
    return "" if value is None else str(value)


def server_seqs(mem_mib: Optional[int]) -> int:
    """Sequences the server takes at once: 2 below 40 GB of VRAM (or unknown), else 4."""
    return 4 if (mem_mib or 0) >= VRAM_SPLIT_MIB else 2


def server_args(seqs: int) -> list[str]:
    if seqs <= 2:
        return ["--quantization", "fp8", "--max-model-len", "8192", "--max-num-seqs", "2"]
    return ["--max-model-len", "16384", "--max-num-seqs", "4"]


def serve_command(vllm: str, model: str, revision: str, flags: str, seqs: int, port: int = VLM_PORT) -> list[str]:
    """The ``vllm serve`` command line (polish.sh start_server)."""
    cmd = [vllm, "serve", model]
    if revision:
        cmd += ["--revision", revision]
    cmd += ["--served-model-name", model, "--port", str(port), "--limit-mm-per-prompt", LIMIT_MM,
            "--gpu-memory-utilization", GPU_MEMORY_UTILIZATION]
    return cmd + shlex.split(flags or "") + server_args(seqs)


def base_url(port: int = VLM_PORT) -> str:
    return f"http://127.0.0.1:{port}/v1"


def http_health(port: int = VLM_PORT) -> bool:
    """True when ``GET /health`` answers 200 within 5 s."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=HEALTH_TIMEOUT_S) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def default_vllm() -> str:
    fast = os.environ.get("WENART_FAST", "/opt/wenart")
    return os.environ.get("WENART_VLLM") or str(Path(fast) / "venv-vllm" / "bin" / "vllm")


class _Proc:
    """A started server process; TERM/KILL go to its whole process group (vLLM starts engine children)."""

    def __init__(self, popen: subprocess.Popen, log) -> None:
        self.popen = popen
        self.pid = popen.pid
        self._log = log

    def poll(self):
        return self.popen.poll()

    def _signal(self, sig) -> None:
        try:
            os.killpg(self.pid, sig)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                self.popen.send_signal(sig)
            except (ProcessLookupError, OSError):
                pass

    def terminate(self) -> None:
        self._signal(signal.SIGTERM)

    def kill(self) -> None:
        self._signal(signal.SIGKILL)

    def wait(self, timeout: Optional[float] = None):
        try:
            return self.popen.wait(timeout=timeout)
        finally:
            if self.popen.poll() is not None and not self._log.closed:
                self._log.close()


def popen_spawn(cmd: list[str], env: dict, log_path: Path) -> _Proc:
    """Start ``cmd`` in its own session with stdout+stderr into ``log_path`` (truncated)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = open(log_path, "wb")
    try:
        popen = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env, stdin=subprocess.DEVNULL,
                                 start_new_session=True)
    except OSError:
        log.close()
        raise
    return _Proc(popen, log)


def tail_lines(path: Path, n: int) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
    except OSError:
        return []


@dataclass
class VLMServer:
    """One ``vllm serve`` process for ``check.yaml models.<key>``."""
    key: str
    deadline: Optional[float] = None
    seqs: int = 2
    port: int = VLM_PORT
    logs_dir: Path = Path("/workspace/logs")
    job_dir: Optional[Path] = None
    private: bool = False                     # a private project is in the run: no log lines to stdout
    wait_s: float = SERVER_WAIT_S
    vllm: str = field(default_factory=default_vllm)
    check_yaml: Path = CHECK_YAML
    spawn: Callable = popen_spawn             # (cmd, env, log_path) -> process (pid, poll, terminate, kill, wait)
    health: Optional[Callable] = None         # () -> bool
    clock: Callable[[], float] = time.time
    sleep: Callable[[float], None] = time.sleep
    out: Callable[[str], None] = print
    proc: object = None
    seconds_to_ready: Optional[float] = None
    model: str = ""

    @property
    def url(self) -> str:
        return base_url(self.port)

    @property
    def log_path(self) -> Path:
        return Path(self.logs_dir) / f"vllm-{self.key}.log"

    @property
    def pid_path(self) -> Optional[Path]:
        return Path(self.job_dir) / "vllm.pid" if self.job_dir else None

    def command(self) -> list[str]:
        models = check_models(self.check_yaml)
        if self.key not in models or not models[self.key].get("id"):
            raise ServerError(self.key, "config", f"no model '{self.key}' in {self.check_yaml}")
        m = models[self.key]
        self.model = str(m["id"])
        return serve_command(self.vllm, self.model, str(m.get("revision") or ""), str(m.get("server_flags") or ""),
                             self.seqs, self.port)

    def _is_healthy(self) -> bool:
        return (self.health or (lambda: http_health(self.port)))()

    def start(self) -> str:
        """Start the server and wait for ``/health``; the base URL, or ``ServerError`` (server stopped)."""
        cmd = self.command()
        env = dict(os.environ)
        env["VLLM_USE_FLASHINFER_SAMPLER"] = "0"
        self.out(f"starting vllm serve {self.model} for '{self.key}' (seqs {self.seqs}, log {self.log_path})")
        try:
            self.proc = self.spawn(cmd, env, self.log_path)
        except OSError as exc:      # no vllm binary (setup part 'check' failed)
            self.out(f"vllm could not start for {self.model}: {type(exc).__name__}")
            raise ServerError(self.key, "spawn", f"cannot start {cmd[0]}: {exc}") from exc
        if self.pid_path is not None:
            self.pid_path.parent.mkdir(parents=True, exist_ok=True)
            self.pid_path.write_text(f"{self.proc.pid}\n", encoding="utf-8")
        t0 = self.clock()
        while True:
            if self._is_healthy():
                self.seconds_to_ready = round(self.clock() - t0, 1)
                self.out(f"vllm ready for {self.model} after {self.seconds_to_ready:.0f} s")
                return self.url
            if self.proc.poll() is not None:
                rc = self.proc.poll()
                try:
                    self.proc.wait(timeout=5)       # reap it (and close its log)
                except subprocess.TimeoutExpired:
                    pass
                self._early_exit()
                self.proc = None
                raise ServerError(self.key, "early_exit", f"vllm exited early (rc {rc})")
            if self.clock() - t0 > self.wait_s:
                self.out(f"vllm not ready after {self.wait_s:.0f} s for {self.model}")
                self.stop()
                raise ServerError(self.key, "timeout", f"not ready after {self.wait_s:.0f} s")
            if self.deadline is not None and self.clock() >= self.deadline:
                self.out(f"deadline passed while vllm was starting for {self.model}")
                self.stop()
                raise ServerError(self.key, "deadline", "deadline passed while starting")
            self.sleep(HEALTH_EVERY_S)

    def _early_exit(self) -> None:
        lines = tail_lines(self.log_path, EARLY_EXIT_LINES)
        if self.job_dir is not None:
            target = Path(self.job_dir) / f"server-{self.key}.log"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        if self.private:
            self.out(f"vllm exited early for {self.model}; last log lines in "
                     f"{Path(self.job_dir or '.') / f'server-{self.key}.log'}")
        else:
            self.out(f"vllm exited early for {self.model}; last log lines:")
            for line in lines:
                self.out(line)
        self._remove_pid()

    def stop(self) -> None:
        """TERM, wait up to 60 s, then KILL (polish.sh stop_server)."""
        proc = self.proc
        if proc is not None and proc.poll() is None:
            self.out(f"stopping vllm (pid {proc.pid})")
            proc.terminate()
            try:
                proc.wait(timeout=STOP_WAIT_S)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=STOP_WAIT_S)
                except subprocess.TimeoutExpired:
                    pass
        self._remove_pid()
        self.proc = None

    def _remove_pid(self) -> None:
        if self.pid_path is not None:
            try:
                self.pid_path.unlink()
            except FileNotFoundError:
                pass

    def info(self) -> dict:
        return {"key": self.key, "model": self.model, "seqs": self.seqs, "seconds_to_ready": self.seconds_to_ready}


@contextmanager
def server(key: str, deadline: Optional[float] = None, *, stats: Optional[list] = None, **kwargs):
    """``with server("qwen", deadline) as url:`` (see the module docstring); ``stats`` gets ``info()``."""
    srv = VLMServer(key, deadline=deadline, **kwargs)
    try:
        srv.start()
    except ServerError:
        if stats is not None:
            stats.append(dict(srv.info(), ok=False))
        raise
    if stats is not None:
        stats.append(dict(srv.info(), ok=True))
    try:
        yield srv.url
    finally:
        srv.stop()


@contextmanager
def external_server(url: str, key: str = "", *, stats: Optional[list] = None):
    """``--vlm-url``: a server someone else started (the smoke profile's fake); nothing is started."""
    if stats is not None:
        stats.append({"key": key, "model": None, "seqs": None, "seconds_to_ready": 0.0, "ok": True,
                      "external": True})
    yield url.rstrip("/")


def gpu_mem_from_text(text: str) -> int:
    """Total VRAM in MiB from ``nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits`` output
    (the first line that is a number; 0 when none)."""
    for line in text.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return 0


NVIDIA_SMI_QUERY = ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"]

