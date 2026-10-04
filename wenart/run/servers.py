"""vLLM server sessions of a full run (docs/milestone6.md §1.4, docs/milestone7.md §9.1).

What: ``with server("qwen", deadline) as url: ...`` starts ``vllm serve`` for
``check.yaml models.<key>``, waits until ``/health`` answers, yields the
OpenAI base URL and stops the server afterwards. It is a port of
``scripts/jobs/polish.sh`` ``start_server`` / ``stop_server`` /
``server_args`` / ``server_seqs`` / ``check_field`` (the proven reference):

- command: ``vllm serve <id> --revision <rev> --served-model-name <id>
  --port 8001 --limit-mm-per-prompt '{"image":2}' --gpu-memory-utilization
  0.90 <server_flags of check.yaml> <size flags>``; size flags by the
  sequences: 2 (below 40 GB of VRAM) ``--quantization fp8 --max-model-len
  8192 --max-num-seqs 2``, up to 4 ``--max-model-len 16384 --max-num-seqs
  N``, above 4 (the >= 80 GB tier of M7) ``--max-model-len 32768
  --max-num-seqs N``; env
  ``VLLM_USE_FLASHINFER_SAMPLER=0`` (FlashInfer's sampler failed on sm_120);
- log ``/workspace/logs/vllm-<key>.log`` (the job's EXIT trap copies a
  200-line tail); ``/health`` every 10 s; an early exit writes the last 40
  log lines to ``$WENART_JOB_DIR/server-<key>.log`` (and prints them only
  when no private project is in the run); gives up after ``SERVER_WAIT_S``
  (1500 s) or at the deadline; stop = TERM, wait 60 s, KILL;
- the pid goes to ``$WENART_JOB_DIR/vllm.pid`` (the bash EXIT trap kills it
  if the orchestrator dies), removed after the stop.

``seqs`` is the ``--workers`` of every VLM stage: ``server_seqs(mem,
max_seqs)`` = min(``check.yaml models.<key>.max_seqs`` when set (probed per
model by the prep pod, M7 §9.2), 8 from 80000 MiB of VRAM, 4 from 40000 MiB,
else 2). There is no runtime fallback: a server that does not start with
these sizes is a server error. ``--vlm-url`` (smoke profile) uses an
external server instead (``external_server``).

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
VRAM_LARGE_MIB = 80000            # from here: 32768 context, 8 sequences (RTX PRO 6000, 96 GB; M7 §9.1)
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


def max_seqs_of(models: dict, key: str) -> Optional[int]:
    """``check.yaml models.<key>.max_seqs`` (None when unset or not a positive integer)."""
    value = (models.get(key) or {}).get("max_seqs") if isinstance(models, dict) else None
    try:
        n = int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
    return n if n and n > 0 else None


def check_field(key: str, field_name: str, check_yaml: Path = CHECK_YAML) -> str:
    """One value of ``check.yaml models.<key>`` as text ('' when unset); KeyError for an unknown key."""
    value = check_models(check_yaml)[key].get(field_name)
    return "" if value is None else str(value)


def server_seqs(mem_mib: Optional[int], max_seqs: Optional[int] = None) -> int:
    """Sequences the server takes at once: 8 from 80000 MiB of VRAM, 4 from 40000 MiB, else 2 (also for an
    unknown size), capped by ``max_seqs`` (``check.yaml models.<key>.max_seqs``, the prep pod's probe) when set."""
    mem = mem_mib or 0
    tier = 8 if mem >= VRAM_LARGE_MIB else 4 if mem >= VRAM_SPLIT_MIB else 2
    try:
        cap = int(max_seqs) if max_seqs is not None and str(max_seqs).strip() != "" else None
    except (TypeError, ValueError):
        cap = None
    return max(1, min(tier, cap)) if cap is not None and cap > 0 else tier


def server_args(seqs: int, mem_mib: Optional[int] = None) -> list[str]:
    """The size flags of ``vllm serve`` for ``seqs`` sequences (module docstring). fp8 only on a GPU below
    40000 MiB (or of unknown size): a large GPU whose model is capped at 2 sequences keeps full precision."""
    if seqs <= 2 and (mem_mib is None or mem_mib < VRAM_SPLIT_MIB):
        return ["--quantization", "fp8", "--max-model-len", "8192", "--max-num-seqs", str(int(seqs))]
    if seqs <= 4:
        return ["--max-model-len", "16384", "--max-num-seqs", str(int(seqs))]
    return ["--max-model-len", "32768", "--max-num-seqs", str(int(seqs))]


def serve_command(vllm: str, model: str, revision: str, flags: str, seqs: int, port: int = VLM_PORT,
                  mem_mib: Optional[int] = None) -> list[str]:
    """The ``vllm serve`` command line (polish.sh start_server)."""
    cmd = [vllm, "serve", model]
    if revision:
        cmd += ["--revision", revision]
    cmd += ["--served-model-name", model, "--port", str(port), "--limit-mm-per-prompt", LIMIT_MM,
            "--gpu-memory-utilization", GPU_MEMORY_UTILIZATION]
    return cmd + shlex.split(flags or "") + server_args(seqs, mem_mib)


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
    mem_mib: Optional[int] = None             # the GPU's VRAM (the size flags; None: by the sequences alone)
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
                             self.seqs, self.port, self.mem_mib)

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


def gpu_from_text(text: str) -> tuple[Optional[str], int]:
    """``(name, total VRAM in MiB)`` of the first GPU in ``nvidia-smi --query-gpu=name,memory.total
    --format=csv,noheader,nounits`` output (``NVIDIA RTX PRO 6000 Blackwell Server Edition, 97887``); a line
    that is only a number gives no name. ``(None, 0)`` when no line ends in a number."""
    for line in text.splitlines():
        parts = [p.strip() for p in line.strip().split(",")]
        if parts and parts[-1].isdigit():
            name = ",".join(parts[:-1]).strip()
            return (name or None), int(parts[-1])
    return None, 0


def gpu_mem_from_text(text: str) -> int:
    """Total VRAM in MiB of the first GPU of the ``nvidia-smi`` output (``gpu_from_text``; 0 when none)."""
    return gpu_from_text(text)[1]


NVIDIA_SMI_QUERY = ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"]

