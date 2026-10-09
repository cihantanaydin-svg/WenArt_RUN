#!/usr/bin/env python3
"""RunPod runner for WenArt_RUN. Every GPU job goes through here.

Hard rules (CLAUDE.md): max $5.00/GPU-hour, max $30/day, max 2 h per run, one pod
at a time. Pods stop themselves (watchdog + end of job, see scripts/pod_entry.sh).
The runner collects the results (results/ and, for private projects, results-private/
into runs/<job>/), stops the pod right after a successful collection instead of
paying for the grace period (docs/milestone6.md §7.2; the in-pod watchdog and
job-end stop stay armed) and terminates the stopped pod.

Usage:
  gpu_run.py status                      pods, volumes, today's spend
  gpu_run.py gpus [--dc EU-RO-1]         live prices and availability of the allowed GPUs
  gpu_run.py volume-create [--size 120]  create the Network Volume (asks first)
  gpu_run.py volume-resize --size N      grow the network volume (user's OK first; never shrinks)
  gpu_run.py run --job scripts/jobs/smoke.sh [--gpu "RTX PRO 6000"] [--max-minutes 120] [--no-volume]
  gpu_run.py logs POD_ID | stop POD_ID | terminate POD_ID | sweep [--yes]
  gpu_run.py attach POD_ID [--purpose TEXT]  re-attach after the runner died: wait, collect, stop, log
Only stdlib; works in the cloud session (HTTPS proxy) and on the Mac.

Safety notes:
- Only pods named `wenart-*` are ever stopped or terminated; other pods on the account
  are reported, never touched.
- Today's spend = max(billing API, rows of docs/gpu-log.md dated today) + worst case of
  live wenart pods, because the billing API lags by minutes to hours.
- A provisional gpu-log row is written before the pod exists and corrected at the end,
  so a crashed runner still leaves a trace. SIGTERM unwinds through the cleanup.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import http.client
import json
import os
import re
import secrets
import signal
import socket
import subprocess
import threading
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API = "https://api.runpod.io"  # paths below carry /v2
ROOT = Path(__file__).resolve().parent.parent
GPU_LOG = ROOT / "docs" / "gpu-log.md"
RUNS_DIR = ROOT / "runs"

MAX_PRICE_PER_H = 5.00          # user decision of 3 Oct 2026 (was $1.00)
MAX_ACTION_USD = 5.00           # CLAUDE.md: ask the user before any single action costing more than $5
MAX_PER_DAY = 30.00                 # raised from $10 to $20, then $30, by the user on 4 Oct 2026
MAX_MINUTES = 120
IMAGE = "runpod/pytorch:1.4.0-cu1281-torch291-ubuntu2404"
DATACENTER = "EU-RO-1"
VOLUME_NAME = "wenart"
VOLUME_SIZE_GB = 120
CONTAINER_DISK_GB = 30
POD_PREFIX = "wenart-"
# Allowed GPUs, fastest first (user decisions of 3 Oct 2026: "for faster job finish choose a better GPU",
# limit $5/h). NVIDIA only (the stack is CUDA), 24 GB+, whole GPUs (no MIG slices). Cards with RT cores come
# first because Cycles renders use them; the data-centre cards without RT cores (H200/H100/A100) follow the
# fast RTX cards. Measured: the RTX 4090 renders and polishes 25-30 % faster than the RTX PRO 4500 (M5 runs
# 1a/2). Not measured yet: everything else; the RTX PRO 6000 (96 GB) has the same Blackwell architecture as the
# PRO 4500 (the lowest-risk upgrade; in stock in EU-RO-1 on 3 Oct 2026, $2.09/h).
GPU_PRIORITY = ["RTX PRO 6000", "RTX PRO 6000 WK", "RTX 5090", "RTX PRO 5000", "L40S", "H200 SXM", "H200 NVL",
                "H100 SXM", "H100 NVL", "H100 PCIe", "RTX 4090", "RTX 6000 Ada", "L40", "A100 SXM", "A100 PCIe",
                "RTX PRO 4500", "RTX 5000 Ada", "RTX PRO 4000", "RTX A6000", "A40", "RTX A5000"]
EXCLUDED_GPUS = ("L4",)       # never, not even with --gpu (docs/milestone6.md §0)
POLL_S = 20
BOOT_TIMEOUT_S = 15 * 60  # pod RUNNING but no status server -> stop it
API_FAIL_LIMIT = 30  # consecutive failed polls (~10 min) before the runner gives up watching
UA = "wenart-gpu-run/0.2 (+https://github.com/cihantanaydin-svg/WenArt_RUN)"  # Cloudflare bans urllib's default UA
JOB_RE = re.compile(r"^scripts/jobs/[A-Za-z0-9_.-]+\.sh$")


# ----------------------------------------------------------------------------- API
class ApiError(RuntimeError):
    pass


def api(method: str, path: str, body: dict | None = None, timeout: int = 60, retries: int = 3) -> dict | list | None:
    """Call the REST API. Network and HTTP errors become ApiError; GETs and the
    stop/terminate calls are retried with backoff, pod creation is not (orphan risk)."""
    key = os.environ.get("RUNPOD_API_KEY", "")
    data = json.dumps(body).encode() if body is not None else None
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(API + path, method=method)
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", UA)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
                raw = r.read()
                return json.loads(raw) if raw.strip() else None
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:800]
            last = ApiError(f"{method} {path} -> HTTP {e.code}: {detail}")
            if e.code < 500 and e.code != 429:
                break
        except (urllib.error.URLError, socket.timeout, TimeoutError, OSError, http.client.HTTPException) as e:
            last = ApiError(f"{method} {path} -> network error: {e}")
        if attempt + 1 < retries:
            time.sleep(2 ** attempt)
    raise last  # type: ignore[misc]


def fetch(url: str, timeout: int = 20) -> bytes | None:
    """GET through the RunPod HTTP proxy; None while the pod is not reachable yet."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, OSError, http.client.HTTPException):
        return None


def fetch_to(url: str, path: Path, timeout: int = 900, max_bytes: int = 0) -> tuple[int | None, str]:
    """GET ``url`` into ``path`` in 1 MB chunks (through ``<path>.part``, renamed when complete): ``(bytes, "")``,
    or ``(None, "too big")`` when the file is larger than ``max_bytes`` (0: no limit), or ``(None, "failed")``. A
    local file of the announced size is kept, so a repeated collection does not download it again."""
    tmp = path.with_name(path.name + ".part")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            size = int(r.headers.get("Content-Length") or -1)
            if max_bytes and size > max_bytes:
                return None, "too big"
            if size >= 0 and path.is_file() and path.stat().st_size == size:
                return size, ""
            n = 0
            with tmp.open("wb") as fh:
                for chunk in iter(lambda: r.read(1 << 20), b""):
                    n += len(chunk)
                    if max_bytes and n > max_bytes:
                        raise ValueError("too big")
                    fh.write(chunk)
        if size >= 0 and n != size:
            raise OSError(f"short read: {n} of {size} bytes")
        tmp.replace(path)
        return n, ""
    except ValueError:
        tmp.unlink(missing_ok=True)
        return None, "too big"
    except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, OSError, http.client.HTTPException):
        tmp.unlink(missing_ok=True)
        return None, "failed"


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


# ---------------------------------------------------------------------- pure logic
def action_price_limit(minutes: int, over_5_ok: bool = False) -> float:
    """$/h limit for one pod of ``minutes``: the per-hour limit, and (unless the user OK'd a bigger action with
    ``--over-5-ok``) the price at which the pod's worst case stays within MAX_ACTION_USD."""
    if over_5_ok or minutes <= 0:
        return MAX_PRICE_PER_H
    return min(MAX_PRICE_PER_H, MAX_ACTION_USD * 60.0 / minutes)


def pick_gpu(catalog: list[dict], dc_avail: dict[str, str] | None, want: str | None,
            max_price: float = MAX_PRICE_PER_H) -> dict:
    """Choose a GPU from the live catalog. Raises with a clear message if none fits."""
    by_name = {g["name"]: g for g in catalog}
    if want in EXCLUDED_GPUS:
        raise RuntimeError(f"{want} is not allowed (excluded GPUs: {', '.join(EXCLUDED_GPUS)})")
    order = [want] if want else GPU_PRIORITY
    reasons = []
    for name in order:
        g = by_name.get(name)
        if not g:
            reasons.append(f"{name}: not in catalog")
            continue
        price = g["price"]["secure"]
        if price is None or price > max_price:
            reasons.append(f"{name}: ${price}/h over the ${max_price:.2f}/h limit")
            continue
        avail = dc_avail.get(name, "NONE") if dc_avail is not None else g.get("availability", "NONE")
        if avail == "NONE":
            reasons.append(f"{name}: no stock")
            continue
        return {"name": name, "id": g["id"], "price": price, "availability": avail, "memory": g["memory"]}
    raise RuntimeError("no allowed GPU available now:\n  " + "\n  ".join(reasons))


def check_limits(price: float, minutes: int, spent_today: float) -> None:
    if price > MAX_PRICE_PER_H:
        raise RuntimeError(f"${price}/h is over the ${MAX_PRICE_PER_H}/h limit")
    if minutes > MAX_MINUTES:
        raise RuntimeError(f"{minutes} min is over the {MAX_MINUTES} min limit per run")
    worst = price * minutes / 60
    if spent_today + worst > MAX_PER_DAY:
        raise RuntimeError(f"today's spend ${spent_today:.2f} + worst case ${worst:.2f} "
                           f"would pass the ${MAX_PER_DAY:.2f}/day limit")


def our_pods(pods: list[dict]) -> list[dict]:
    """Pods created by this runner (name prefix). Everything else belongs to someone else."""
    return [p for p in pods if str(p.get("name", "")).startswith(POD_PREFIX)]


def validate_job_path(job: str) -> str:
    """A job is a committed shell script under scripts/jobs/; the path is passed to the pod as is."""
    job = job.replace("\\", "/")
    if not JOB_RE.match(job):
        raise RuntimeError(f"job must look like scripts/jobs/<name>.sh, got {job!r}")
    if not (ROOT / job).is_file():
        raise RuntimeError(f"job script not found: {job}")
    return job


def gpu_log_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 7 and cells[0] not in ("Date (UTC)", "---"):
            rows.append(cells)
    return rows


def local_spent_on(text: str, day: str) -> float:
    """Sum of the Cost cells of gpu-log rows whose date starts with `day` (YYYY-MM-DD)."""
    total = 0.0
    for cells in gpu_log_rows(text):
        if cells[0].startswith(day):
            try:
                total += float(cells[4])
            except ValueError:
                pass
    return total


def upsert_gpu_log(text: str, row: dict, key: str | None = None) -> str:
    """Insert a row into the gpu-log table (or replace the row whose Pod ID cell equals
    `key`) and recompute the total. Returns the new text."""
    lines = text.splitlines()
    new = (f"| {row['date']} | {row['pod_id']} | {row['gpu']} | {row['minutes']} | "
           f"{row['cost']:.2f} | {row['purpose']} | {row['result']} |")
    replaced = False
    if key:
        for i, l in enumerate(lines):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cells) == 7 and cells[1] == key:
                lines[i] = new
                replaced = True
                break
    if not replaced:
        last_row = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last_row + 1, new)
    total = 0.0
    for cells in gpu_log_rows("\n".join(lines)):
        try:
            total += float(cells[4])
        except ValueError:
            pass
    for i, l in enumerate(lines):
        if l.startswith("**Total spent so far:"):
            rest = l.split("**", 2)[2]
            lines[i] = f"**Total spent so far: ${total:.2f}**{rest}"
    return "\n".join(lines) + "\n"


def append_gpu_log(text: str, row: dict) -> str:
    return upsert_gpu_log(text, row)


def pod_create_body(name: str, gpu_id: str, volume_id: str | None, env: dict, dc: str | None,
                    disk_gb: int = CONTAINER_DISK_GB) -> dict:
    body = {
        "name": name,
        "image": IMAGE,
        "cloud": "SECURE",
        "gpu": {"id": gpu_id, "count": 1, "minCudaVersion": "12.8"},
        "disk": disk_gb,
        "ports": ["8000/http"],
        "env": env,
        "cmd": ["bash", "-c", "echo \"$WENART_ENTRY\" | base64 -d > /tmp/pod_entry.sh && bash /tmp/pod_entry.sh"],
    }
    if volume_id:
        body["mounts"] = {"network": [{"volumeId": volume_id, "path": "/workspace"}]}
    if dc:
        body["dataCenterIds"] = [dc]
    return body


# ------------------------------------------------------------------------ helpers
def all_pods() -> list[dict]:
    return api("GET", "/v2/pods")["pods"]


def live_pods(pods: list[dict] | None = None) -> list[dict]:
    """Live pods of ours. Foreign live pods are printed as a warning, never touched."""
    pods = all_pods() if pods is None else pods
    live = [p for p in pods if p["status"] not in ("EXITED", "TERMINATED")]
    foreign = [p for p in live if p not in our_pods(live)]
    for p in foreign:
        print(f"warning: foreign pod {p['id']} ({p.get('name')}) is {p['status']} on this account; not ours, left alone")
    return our_pods(live)


def billing_today() -> float:
    """Pod spend in the current UTC day bucket from the billing API. A billing error refuses the run."""
    try:
        d = api("GET", "/v2/billing/pods?bucketSize=day&lastN=1")
        return float(d["metadata"]["totals"]["totalAmount"])
    except (ApiError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"cannot read today's spend from /v2/billing/pods: {e}") from None


def spent_today(pods: list[dict] | None = None) -> float:
    """max(billing, local log for today) + worst case of every live wenart pod (2 h at its rate)."""
    billing = billing_today()
    local = local_spent_on(GPU_LOG.read_text(), utc_now().strftime("%Y-%m-%d")) if GPU_LOG.exists() else 0.0
    live = sum(float(p.get("cost") or 0) * MAX_MINUTES / 60 for p in live_pods(pods))
    if billing < local:
        print(f"note: billing API says ${billing:.2f} today but docs/gpu-log.md has ${local:.2f} (billing lags); using the larger")
    return max(billing, local) + live


def catalog() -> list[dict]:
    return api("GET", "/v2/catalog/gpus?include=AVAILABILITY&product=POD&cloud=SECURE")["gpus"]


def dc_availability(dc: str) -> dict[str, str]:
    d = api("GET", f"/v2/catalog/datacenters/{dc}?include=GPU_AVAILABILITY")
    return {g["name"]: g["availability"] for g in d.get("gpuAvailability", [])}


def find_volume() -> dict | None:
    for v in api("GET", "/v2/network-volumes")["networkVolumes"]:
        if v["name"] == VOLUME_NAME:
            return v
    return None


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def pod_logs(pod_id: str, tail: int = 2000, idle_s: float = 6.0, cap_s: float = 60.0) -> str:
    """Read the SSE log stream until it goes quiet (idle cutoff) or the cap is reached."""
    key = os.environ.get("RUNPOD_API_KEY", "")
    req = urllib.request.Request(f"{API}/v2/pods/{pod_id}/logs?source=container&tail={tail}")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("User-Agent", UA)
    out: list[str] = []
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.fp.raw._sock.settimeout(idle_s)  # type: ignore[attr-defined]
            while time.time() - t0 < cap_s:
                line = r.readline()
                if not line:
                    break
                s = line.decode(errors="replace").rstrip("\n")
                if s.startswith("data:"):
                    try:
                        d = json.loads(s[5:])
                        out.append(str(d.get("line", d.get("message", s[5:]))))
                    except (json.JSONDecodeError, AttributeError):
                        out.append(s[5:].strip())
    except Exception:  # noqa: BLE001 - best effort, return what was read
        pass
    return "\n".join(out)


def terminate(pod_id: str) -> bool:
    try:
        api("DELETE", f"/v2/pods/{pod_id}")
        print(f"pod {pod_id} terminated")
        return True
    except ApiError as e:
        print(f"terminate failed: {e}")
        return False


def stop(pod_id: str) -> bool:
    try:
        api("POST", f"/v2/pods/{pod_id}/action", {"action": "stop"})
        print(f"pod {pod_id} stop requested")
        return True
    except ApiError as e:
        print(f"stop failed: {e}")
        return False


def log_run(pod_id: str, gpu: str, minutes: float, cost: float, purpose: str, result: str,
            key: str | None = None) -> None:
    row = {"date": utc_now().strftime("%Y-%m-%d %H:%M"), "pod_id": pod_id, "gpu": gpu,
           "minutes": int(round(minutes)), "cost": cost, "purpose": purpose, "result": result}
    GPU_LOG.write_text(upsert_gpu_log(GPU_LOG.read_text(), row, key))
    print(f"logged to docs/gpu-log.md: {row}")


# ----------------------------------------------------------------------- commands
def cmd_status(_: argparse.Namespace) -> int:
    pods = all_pods()
    print(f"pods: {len(pods)}")
    for p in pods:
        mine = "ours" if p in our_pods(pods) else "NOT ours"
        print(f"  {p['id']} {p['status']} {p.get('name')} {p.get('gpu', {}).get('id', '-')} ${p.get('cost', 0)}/h {p.get('dataCenterId')} [{mine}]")
    vols = api("GET", "/v2/network-volumes")["networkVolumes"]
    print(f"network volumes: {len(vols)}")
    for v in vols:
        print(f"  {v['id']} {v['name']} {v['size']} GB {v['dataCenter']}")
    print(f"spent today (UTC): ${spent_today(pods):.2f} of ${MAX_PER_DAY:.2f} "
          f"(billing ${billing_today():.2f}, local log ${local_spent_on(GPU_LOG.read_text(), utc_now().strftime('%Y-%m-%d')):.2f})")
    return 0


def cmd_gpus(a: argparse.Namespace) -> int:
    cat = catalog()
    avail = dc_availability(a.dc) if a.dc else None
    print(f"{'GPU':<14}{'VRAM':>5}{'$/h':>7}  {'availability' + (' in ' + a.dc if a.dc else ' (any DC)')}")
    for name in GPU_PRIORITY:
        g = next((x for x in cat if x["name"] == name), None)
        if not g:
            print(f"{name:<14} not in catalog"); continue
        av = avail.get(name, "NONE") if avail is not None else g.get("availability")
        print(f"{name:<14}{g['memory']:>5}{g['price']['secure']:>7}  {av}")
    return 0


def cmd_volume_create(a: argparse.Namespace) -> int:
    v = find_volume()
    if v:
        print(f"volume exists: {v['id']} {v['size']} GB {v['dataCenter']}"); return 0
    print(f"creating {a.size} GB STANDARD volume '{VOLUME_NAME}' in {a.dc} (~${a.size * 0.07:.2f}/month)")
    if not a.yes and input("type 'yes' to confirm: ").strip() != "yes":
        print("cancelled"); return 1
    v = api("POST", "/v2/network-volumes", {"name": VOLUME_NAME, "size": a.size, "dataCenter": a.dc, "type": "STANDARD"})
    print(f"created {v['id']}")
    return 0


def cmd_volume_resize(a: argparse.Namespace) -> int:
    """Grow the project volume (REST v2 ``PATCH /v2/network-volumes/{id}``; a volume only grows). It changes the
    monthly storage cost, so it runs only with ``--yes`` after the user's OK (CLAUDE.md)."""
    v = find_volume()
    if not v:
        print(f"no volume named '{VOLUME_NAME}'"); return 1
    if a.size <= v["size"]:
        print(f"volume {v['id']} is {v['size']} GB; a network volume only grows (asked {a.size} GB)"); return 1
    extra = (a.size - v["size"]) * 0.07
    print(f"growing volume {v['id']} from {v['size']} to {a.size} GB (+~${extra:.2f}/month, ~${a.size * 0.07:.2f}/month)")
    if not a.yes and input("type 'yes' to confirm: ").strip() != "yes":
        print("cancelled"); return 1
    r = api("PATCH", f"/v2/network-volumes/{v['id']}", {"size": a.size}, retries=1)
    print(f"volume {v['id']} is now {(r or {}).get('size', '?')} GB")
    return 0


COLLECT_MAX_DEPTH = 4
COLLECT_WORKERS = 16          # parallel result downloads (one at a time: 0.81 s per file; M10: ~10000 library files)
COLLECT_MAX_FILE = 20_000_000
COLLECT_MAX_TOTAL = 400_000_000   # one total over results/ and results-private/
COLLECT_TRIES = 3             # collection attempts while the pod runs (a failed one is retried at the next poll)
COLLECT_LISTING_TRIES = 5     # tries of the job folder listing and of each tree's root listing (10 s apart)
# Private results first: a small allow-listed set (docs/milestone6.md §2.1) that exists nowhere else
# in the session; both trees share the caps.
COLLECT_TREES = ("results-private", "results")
# Milestone 9: the 3D files of a project (results/final/<p>/3d/<p>.blend and .glb, written by the export stage) are
# the deliverable and larger than COLLECT_MAX_FILE: they are streamed to disk after every small file, under their own
# caps (not counted in COLLECT_MAX_TOTAL).
COLLECT_BIG_SUFFIXES = (".blend", ".glb")
COLLECT_BIG_MAX_FILE = 2_000_000_000
COLLECT_BIG_MAX_TOTAL = 8_000_000_000
COLLECT_BIG_TIMEOUT = 900
RUNNER_STOP_RESULT = "stopped by runner after collect (watchdog and job-end stop armed)"


def is_big_result(rel_name: str) -> bool:
    """A 3D file of the export stage: ``.../3d/<name>.blend`` or ``.glb`` (public ``final/<p>/3d/``, private
    ``<alias>/final/3d/``)."""
    parts = rel_name.split("/")
    return len(parts) >= 2 and parts[-2] == "3d" and parts[-1].endswith(COLLECT_BIG_SUFFIXES)


def parse_listing(html: str) -> tuple[list[str], list[str]]:
    """Files and sub-directories of a python http.server directory listing (names unquoted)."""
    files, dirs = [], []
    for href in re.findall(r'href="([^"?]+)"', html):
        if href.startswith(("/", "..", "?")) or "/" in href.rstrip("/"):
            continue
        name = urllib.parse.unquote(href)
        (dirs if href.endswith("/") else files).append(name.rstrip("/"))
    return files, dirs


def collect_all(status_url: str, run_dir: Path, workers: int = COLLECT_WORKERS, skip_existing: bool = False) -> dict:
    """Download status.json, job.log, results/ and (when the job wrote it) results-private/ from the
    pod into ``run_dir``, recursively (depth <= COLLECT_MAX_DEPTH). Small files only: a file of
    COLLECT_MAX_FILE bytes or more is left out, and the downloads stop at COLLECT_MAX_TOTAL bytes
    over both trees. The exception are the 3D files of the export stage (``is_big_result``, Milestone 9):
    streamed to disk after the small files, under COLLECT_BIG_MAX_FILE and COLLECT_BIG_MAX_TOTAL.

    The folders are listed first, then the files are fetched with ``workers`` parallel requests:
    one at a time took 0.81 s per file through the pod proxy (M5 runs 0 and 0b), so the 500-1000
    result files of an M5 run would outlast the grace period.

    ``results-private/`` is walked when the job folder's listing shows it (or, when that listing
    still fails after ``COLLECT_LISTING_TRIES`` tries, tried once quietly); the private aliases inside
    it are symlinks the status server follows.

    Returns ``{"files", "bytes", "capped", "failed", "too_big", "ok", "job_log", "job_listed", "trees": {tree:
    {"listed", "files"}}}``; ``too_big`` lists the files left out for their size (printed, and written to
    ``<run_dir>/collect_too_big.txt``, so a result the prep or full job wrote is never missed silently);
    ``ok`` (a successful collection, after which the runner may stop the pod)
    = job.log fetched, the job folder listed (without it the runner cannot know whether
    results-private/ exists), every tree that exists listed completely and no listed file failed to
    download (``failed``: fetch gave None; a file left out for its size is not a failure). The size
    cap (``capped``) stays a warning: it is deliberate, and a retry would only hit it again. A failed
    collection is retried at the next poll (``COLLECT_TRIES``), so a proxy glitch never lets the runner
    stop the pod with files missing (review F2). ``skip_existing`` (a retry, Milestone 10): a result file an earlier
    attempt of this run already wrote is not fetched again (the job has ended, its files no longer change; pod L2c
    of 9 Oct 2026 fetched 6500 files three times over for two failed ones and ran out of grace).
    """
    got = {}
    for name in ("status.json", "job.log"):
        raw = fetch(status_url + name, timeout=60)
        if raw:
            (run_dir / name).write_bytes(raw)
        got[name] = raw is not None
    job_listing = None
    for i in range(COLLECT_LISTING_TRIES):
        job_listing = fetch(status_url, timeout=30)
        if job_listing:
            break
        if i + 1 < COLLECT_LISTING_TRIES:
            time.sleep(10)
    if not job_listing:
        print("warning: could not list the job folder on the pod (results-private/ may be missed)")
    present = set(parse_listing(job_listing.decode(errors="replace"))[1]) if job_listing else None
    todo: list[tuple[str, str]] = []
    trees: dict[str, dict] = {}

    def walk(tree: str, rel: str, depth: int, tries: int, quiet: bool = False) -> bool:
        listing = None
        for i in range(tries):
            listing = fetch(status_url + urllib.parse.quote(f"{tree}/{rel}"), timeout=30)
            if listing:
                break
            if i + 1 < tries:
                time.sleep(10)
        if not listing:
            if not quiet:
                print(f"warning: could not list {tree}/{rel} on the pod")
            return False
        files, dirs = parse_listing(listing.decode(errors="replace"))
        (run_dir / tree / rel).mkdir(parents=True, exist_ok=True)
        todo.extend((tree, rel + name) for name in files)
        ok = True
        if depth < COLLECT_MAX_DEPTH:
            for d in dirs:
                ok = walk(tree, rel + d + "/", depth + 1, 2) and ok
        return ok

    for tree in COLLECT_TREES:
        if tree == "results-private" and present is not None and tree not in present:
            continue
        quiet = tree == "results-private" and present is None
        n_before = len(todo)
        listed = walk(tree, "", 0, 1 if quiet else COLLECT_LISTING_TRIES, quiet=quiet)
        if quiet and not listed:
            continue                                   # no private results (the usual public job)
        trees[tree] = {"listed": listed, "files": len(todo) - n_before}

    lock = threading.Lock()
    state = {"n": 0, "total": 0, "capped": False, "failed": [], "too_big": [], "big": 0, "big_bytes": 0, "kept": 0}

    def get_big(tree: str, rel_name: str) -> None:
        with lock:
            if state["big_bytes"] > COLLECT_BIG_MAX_TOTAL:
                state["capped"] = True
                return
        n, why = fetch_to(status_url + urllib.parse.quote(f"{tree}/{rel_name}"), run_dir / tree / rel_name,
                          timeout=COLLECT_BIG_TIMEOUT, max_bytes=COLLECT_BIG_MAX_FILE)
        with lock:
            if n is None and why == "too big":
                state["too_big"].append(f"{tree}/{rel_name} (over {COLLECT_BIG_MAX_FILE / 1e6:.0f} MB)")
            elif n is None:
                state["failed"].append(f"{tree}/{rel_name}")
            else:
                state["big"] += 1
                state["big_bytes"] += n

    def get(item: tuple[str, str]) -> None:
        tree, rel_name = item
        if skip_existing and (run_dir / tree / rel_name).is_file():
            with lock:
                state["kept"] += 1
            return
        if is_big_result(rel_name):
            get_big(tree, rel_name)
            return
        with lock:
            if state["total"] > COLLECT_MAX_TOTAL:
                state["capped"] = True
                return
        raw = fetch(status_url + urllib.parse.quote(f"{tree}/{rel_name}"), timeout=120)
        if raw is None:
            with lock:
                state["failed"].append(f"{tree}/{rel_name}")
            return
        if len(raw) >= COLLECT_MAX_FILE:
            with lock:                                 # left out for its size: deliberate, not a failure
                state["too_big"].append(f"{tree}/{rel_name} ({len(raw) / 1e6:.1f} MB)")
            return
        with lock:
            if state["total"] > COLLECT_MAX_TOTAL:
                state["capped"] = True
                return
            state["n"] += 1
            state["total"] += len(raw)
        (run_dir / tree / rel_name).write_bytes(raw)

    todo.sort(key=lambda item: is_big_result(item[1]))          # the small files first (stable order otherwise)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        list(pool.map(get, todo))
    if state["capped"]:
        print("warning: result size cap reached, not every file was downloaded")
    failed = sorted(state["failed"])
    if failed:
        print(f"warning: {len(failed)} result file(s) failed to download, e.g. {', '.join(failed[:3])}")
    too_big = sorted(state["too_big"])
    if too_big:
        print(f"warning: {len(too_big)} result file(s) of {COLLECT_MAX_FILE / 1e6:.0f} MB or more left out: "
              f"{', '.join(too_big[:5])}" + (" ..." if len(too_big) > 5 else ""))
        (run_dir / "collect_too_big.txt").write_text("\n".join(too_big) + "\n")
    private = trees.get("results-private", {}).get("files", 0)
    print(f"collected {state['n']} result files ({state['total'] / 1e6:.1f} MB)"
          + (f", {state['kept']} kept from the earlier attempt" if state["kept"] else "")
          + (f", {private} of them listed under results-private/" if "results-private" in trees else "")
          + (f"; {state['big']} 3D file(s) ({state['big_bytes'] / 1e6:.1f} MB)" if state["big"] else ""))
    ok = (got["job.log"] and job_listing is not None and "results" in trees
          and all(t["listed"] for t in trees.values()) and not failed)
    return {"files": state["n"], "bytes": state["total"], "big_files": state["big"], "big_bytes": state["big_bytes"],
            "capped": state["capped"], "failed": len(failed),
            "too_big": too_big, "ok": bool(ok), "job_log": got["job.log"], "job_listed": job_listing is not None,
            "trees": trees}


def collect(status_url: str, run_dir: Path, workers: int = COLLECT_WORKERS) -> int:
    """``collect_all`` returning only the number of downloaded files."""
    return collect_all(status_url, run_dir, workers)["files"]


def wait_stopped(pod_id: str, tries: int = 30, delay: float = 5) -> bool:
    """Poll until the API says EXITED/TERMINATED (True) or ``tries`` polls passed (False)."""
    for _ in range(tries):
        time.sleep(delay)
        try:
            if api("GET", f"/v2/pods/{pod_id}")["status"] in ("EXITED", "TERMINATED"):
                return True
        except ApiError:
            pass
    return False


def stop_after_collect(pod_id: str) -> str | None:
    """Stop the pod right after a successful collection (docs/milestone6.md §7.2).

    ``"self"`` when the pod already reached EXITED/TERMINATED before the runner sent a stop (its own
    job-end stop worked); ``"runner"`` when the runner sent the REST stop (then it waits for the API
    to confirm); None when the stop request failed (the caller's final stop takes over).
    """
    try:
        status = api("GET", f"/v2/pods/{pod_id}")["status"]
    except ApiError:
        status = None
    if status in ("EXITED", "TERMINATED"):
        return "self"
    print("results collected; stopping the pod now (the in-pod watchdog and job-end stop stay armed)")
    if not stop(pod_id):
        return None
    wait_stopped(pod_id)
    return "runner"


def run_result(final_status: dict | None, stopped_by: str | None, self_stopped: bool, result: str) -> str:
    """The Result cell of docs/gpu-log.md; ``result`` is kept when the job never reported a final status.

    ``self-stop ok`` only when the pod reached EXITED before the runner sent a stop."""
    if final_status is None:
        return result
    code = final_status["exit_code"]
    tag = "ok" if code == 0 else f"exit {code}"
    if final_status.get("state") == "timeout":
        tag = "timeout (watchdog)"
    if stopped_by == "runner":
        return f"{tag}, {RUNNER_STOP_RESULT}"
    if stopped_by == "self" or self_stopped:
        return f"{tag}, self-stop ok"
    return f"{tag}, stopped by runner"


def cmd_run(a: argparse.Namespace) -> int:
    job = validate_job_path(a.job)
    commit = git("rev-parse", "HEAD")
    if not a.allow_dirty:
        dirty = git("status", "--porcelain", "--", ".", ":!docs/gpu-log.md")
        if dirty:
            raise RuntimeError("working tree not clean; commit and push first (or --allow-dirty)")
        if not git("branch", "-r", "--contains", commit):
            raise RuntimeError("HEAD is not pushed; the pod clones from GitHub (or --allow-dirty)")
        if job not in git("ls-files", "--", job):
            raise RuntimeError(f"{job} is not committed")
    minutes = min(a.max_minutes, MAX_MINUTES)

    pods = all_pods()
    running = live_pods(pods)
    if running:
        raise RuntimeError("a wenart pod is already live (one at a time): " + ", ".join(p["id"] for p in running))
    stale = [p for p in our_pods(pods) if p["status"] in ("EXITED",)]
    for p in stale:
        print(f"warning: stopped wenart pod {p['id']} still exists (disk billing); terminate it with 'terminate {p['id']}'")

    volume = None if a.no_volume else find_volume()
    if not a.no_volume and volume is None:
        raise RuntimeError(f"no network volume '{VOLUME_NAME}'; run 'volume-create' or use --no-volume")
    dc = volume["dataCenter"] if volume else None
    gpu = pick_gpu(catalog(), dc_availability(dc) if dc else None, a.gpu,
                   max_price=action_price_limit(minutes, getattr(a, "over_5_ok", False)))
    today = spent_today(pods)
    check_limits(gpu["price"], minutes, today)
    worst = gpu["price"] * minutes / 60
    print(f"GPU {gpu['name']} ({gpu['memory']} GB) ${gpu['price']}/h, stock {gpu['availability']}, "
          f"DC {dc or 'any'}, max {minutes} min -> worst case ${worst:.2f}; spent today ${today:.2f}")
    if a.dry_run:
        print("dry run, no pod created"); return 0

    job_id = utc_now().strftime("%Y%m%d-%H%M%S") + "-" + Path(job).stem
    purpose = a.purpose or Path(job).stem
    token = secrets.token_urlsafe(24)
    entry = base64.b64encode((ROOT / "scripts" / "pod_entry.sh").read_bytes()).decode()
    env = {
        "WENART_ENTRY": entry, "JOB_ID": job_id, "JOB_TOKEN": token, "JOB_SCRIPT": job,
        "REPO_URL": a.repo_url, "REPO_COMMIT": commit,
        "MAX_RUNTIME_S": str(minutes * 60), "GRACE_S": str(a.grace),
        "HF_TOKEN": "{{ RUNPOD_SECRET_hf_token }}", "HF_HOME": "/workspace/hf",
        "WENART_IMAGE": IMAGE, "WENART_EXPECT_VOLUME": "1" if volume else "0",
    }
    for extra in a.env or []:  # job knobs such as RENDER_SAMPLES=128; reserved names stay ours
        key, _, value = extra.partition("=")
        if not key or key in env or key.startswith(("RUNPOD_", "HF_")):
            raise RuntimeError(f"--env {extra!r}: empty, reserved or already set")
        env[key] = value
    name = f"{POD_PREFIX}{job_id}"
    # Provisional log row before the pod exists: a crashed runner still leaves a trace.
    pending_key = f"pending:{job_id}"
    log_run(pending_key, gpu["name"], minutes, worst, purpose, "creating (provisional, worst case)")
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))

    run_dir = RUNS_DIR / job_id
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pod_id = None
    try:
        pod = api("POST", "/v2/pods", pod_create_body(name, gpu["id"], volume["id"] if volume else None, env, dc, a.disk), retries=1)
        pod_id = pod["id"]
    except ApiError as e:
        print(f"pod creation failed: {e}; checking for an orphan named {name}")
        for p in our_pods(all_pods()):
            if p.get("name") == name:
                pod_id = p["id"]
                print(f"orphan {pod_id} found; terminating it")
                stop(pod_id); terminate(pod_id)
        log_run(pending_key if pod_id is None else pod_id, gpu["name"], 0, 0.0, purpose,
                "pod creation failed" + ("; orphan terminated" if pod_id else ""), key=pending_key)
        return 1
    print(f"pod {pod_id} created ({pod['status']}); job {job_id}; local dir runs/{job_id}")
    status_url = f"https://{pod_id}-8000.proxy.runpod.net/{token}/"
    result = "unknown"
    gpu_name = gpu["name"]
    price = gpu["price"]
    last_state = None
    final_status: dict | None = None
    self_stopped = False
    collected_ok = False
    collect_tries = 0
    stopped_by: str | None = None
    first_running = None
    seen_status = False
    api_fails = 0
    pod_status = pod["status"]

    def save_pod_log(tag: str) -> None:
        text = pod_logs(pod_id)
        if text:
            (run_dir / f"pod-{tag}.log").write_text(text)

    try:
        deadline = t0 + minutes * 60 + a.grace + 600
        while time.time() < deadline:
            try:
                p = api("GET", f"/v2/pods/{pod_id}")
                api_fails = 0
            except ApiError as e:
                api_fails += 1
                if api_fails in (1, 10, 20):
                    print(f"poll failed ({api_fails}x): {e}")
                if api_fails >= API_FAIL_LIMIT:
                    result = "api unreachable (pod self-stops)"
                    break
                time.sleep(POLL_S)
                continue
            pod_status = p["status"]
            price = p.get("cost") or price
            gpu_name = (p.get("gpu") or {}).get("id", gpu_name)
            if pod_status == "RUNNING" and first_running is None:
                first_running = time.time()
            if first_running and not seen_status and time.time() - first_running > BOOT_TIMEOUT_S:
                result = "no status server after boot timeout"
                print(f"{result}; stopping the pod")
                save_pod_log("boot-timeout")
                break
            st = None
            raw = fetch(status_url + "status.json") if pod_status == "RUNNING" else None
            if raw:
                try:
                    st = json.loads(raw)
                    seen_status = True
                except json.JSONDecodeError:
                    st = None
            state = f"{pod_status}/{st['state'] if st else '-'}"
            if state != last_state:
                print(f"[{int(time.time() - t0):5d}s] {state}  ${price}/h")
                last_state = state
            if st and st.get("state") in ("done", "timeout") and final_status is None:
                final_status = st
                print(f"job {st['state']}, exit code {st['exit_code']}; collecting results")
            if final_status is not None and not collected_ok and pod_status == "RUNNING" \
                    and collect_tries < COLLECT_TRIES:
                collect_tries += 1
                col = collect_all(status_url, run_dir, skip_existing=collect_tries > 1)
                collected_ok = col["ok"]
                save_pod_log("done")
                if collected_ok:
                    stopped_by = stop_after_collect(pod_id)
                    if stopped_by is not None:
                        break
                else:
                    print(f"collection {collect_tries}/{COLLECT_TRIES} incomplete (job.log, a listing or "
                          f"{col['failed']} file download(s) missing); the pod is not stopped from here")
            if pod_status in ("EXITED", "TERMINATED"):
                self_stopped = final_status is not None
                break
            if pod_status == "ERROR":
                result = "pod ERROR"
                break
            time.sleep(POLL_S)
        else:
            result = "runner timeout"
    except KeyboardInterrupt:
        result = "interrupted"
        save_pod_log("interrupted")
    except SystemExit:
        result = "runner terminated (SIGTERM)"
        raise
    finally:
        minutes_used = (time.time() - t0) / 60
        try:
            p = api("GET", f"/v2/pods/{pod_id}")
            pod_status = p["status"]
            price = p.get("cost") or price
        except ApiError as e:
            print(f"final status read failed: {e}")
        if pod_status not in ("EXITED", "TERMINATED") and not result.startswith("api unreachable"):
            print(f"pod still {pod_status} -> stopping it from here")
            if stop(pod_id):
                wait_stopped(pod_id)
        result = run_result(final_status, stopped_by, self_stopped, result)
        cost = price * minutes_used / 60
        try:
            log_run(pod_id, gpu_name, minutes_used, cost, purpose, result, key=pending_key)
        except Exception as e:  # noqa: BLE001
            print(f"could not write docs/gpu-log.md: {e}")
        if not a.keep and not result.startswith("api unreachable"):
            terminate(pod_id)
        print(f"result: {result}; {minutes_used:.1f} min, ~${cost:.2f}; files in runs/{job_id}/")
    return 0 if final_status and final_status["exit_code"] == 0 else 1


def cmd_logs(a: argparse.Namespace) -> int:
    print(pod_logs(a.pod_id)); return 0


def cmd_stop(a: argparse.Namespace) -> int:
    stop(a.pod_id); return 0


def cmd_terminate(a: argparse.Namespace) -> int:
    terminate(a.pod_id); return 0


def pod_created(p: dict) -> float:
    """Epoch seconds of a pod's ``createdAt`` (REST v2: ISO 8601 with ``Z``)."""
    text = str(p.get("createdAt") or "")
    try:
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return time.time()


def cmd_attach(a: argparse.Namespace) -> int:
    """Re-attach to a running wenart pod whose runner died (the session's container restarted): read the job id
    and the status token from the pod's environment (never printed), wait for the job, collect, stop, correct
    the docs/gpu-log.md row of the pod and terminate it, as ``run`` would have done."""
    pod_id = a.pod_id
    p = api("GET", f"/v2/pods/{pod_id}")
    if not str(p.get("name") or "").startswith("wenart-"):
        print(f"pod {pod_id} ({p.get('name')}) is not a wenart pod: left alone"); return 1
    env = p.get("env") or {}
    job_id, token = env.get("JOB_ID"), env.get("JOB_TOKEN")
    if not job_id or not token:
        print(f"pod {pod_id} has no JOB_ID/JOB_TOKEN in its environment"); return 1
    t0 = pod_created(p)
    price = p.get("cost") or 0.0
    gpu_name = (p.get("gpu") or {}).get("id", "?")
    status_url = f"https://{pod_id}-8000.proxy.runpod.net/{token}/"
    run_dir = RUNS_DIR / job_id
    run_dir.mkdir(parents=True, exist_ok=True)
    max_s = float(env.get("MAX_RUNTIME_S") or 7200) + float(env.get("GRACE_S") or 600) + 600
    print(f"attached to {pod_id}: job {job_id}, running {int((time.time() - t0) / 60)} min, ${price}/h")
    final_status, stopped_by, collected_ok, collect_tries, last_state = None, None, False, 0, None
    self_stopped, result = False, "re-attached; no final status"
    pod_status = p["status"]
    while time.time() < t0 + max_s:
        try:
            p = api("GET", f"/v2/pods/{pod_id}")
        except ApiError as e:
            print(f"poll failed: {e}"); time.sleep(POLL_S); continue
        pod_status = p["status"]
        st = None
        raw = fetch(status_url + "status.json") if pod_status == "RUNNING" else None
        if raw:
            try:
                st = json.loads(raw)
            except json.JSONDecodeError:
                st = None
        state = f"{pod_status}/{st['state'] if st else '-'}"
        if state != last_state:
            print(f"[{int(time.time() - t0):5d}s] {state}  ${price}/h")
            last_state = state
        if st and st.get("state") in ("done", "timeout") and final_status is None:
            final_status = st
            print(f"job {st['state']}, exit code {st['exit_code']}; collecting results")
        if final_status is not None and not collected_ok and pod_status == "RUNNING" and collect_tries < COLLECT_TRIES:
            collect_tries += 1
            collected_ok = collect_all(status_url, run_dir)["ok"]
            if collected_ok:
                stopped_by = stop_after_collect(pod_id)
                if stopped_by is not None:
                    break
        if pod_status in ("EXITED", "TERMINATED"):
            self_stopped = final_status is not None
            break
        if pod_status == "ERROR":
            result = "pod ERROR"; break
        time.sleep(POLL_S)
    p = api("GET", f"/v2/pods/{pod_id}")
    if p["status"] not in ("EXITED", "TERMINATED"):
        print(f"pod still {p['status']} -> stopping it from here")
        if stop(pod_id):
            wait_stopped(pod_id)
    minutes_used = (time.time() - t0) / 60
    result = run_result(final_status, stopped_by, self_stopped, result) + " (runner re-attached)"
    log_run(pod_id, gpu_name, minutes_used, price * minutes_used / 60, a.purpose, result, key=pod_id)
    terminate(pod_id)
    print(f"result: {result}; {minutes_used:.1f} min, ~${price * minutes_used / 60:.2f}; files in runs/{job_id}/")
    return 0 if final_status and final_status["exit_code"] == 0 else 1


def cmd_sweep(a: argparse.Namespace) -> int:
    pods = all_pods()
    ours = our_pods(pods)
    foreign = [p for p in pods if p not in ours and p["status"] not in ("EXITED", "TERMINATED")]
    for p in foreign:
        print(f"foreign live pod left alone: {p['id']} {p.get('name')} {p['status']}")
    if not ours:
        print("no wenart pods to sweep"); return 0
    for p in ours:
        print(f"  will stop/terminate {p['id']} {p.get('name')} {p['status']}")
    if not a.yes and input("type 'yes' to confirm: ").strip() != "yes":
        print("cancelled"); return 1
    for p in ours:
        if p["status"] not in ("EXITED", "TERMINATED"):
            stop(p["id"])
    for p in ours:
        terminate(p["id"])
    print("sweep done")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    g = sub.add_parser("gpus"); g.add_argument("--dc"); g.set_defaults(fn=cmd_gpus)
    v = sub.add_parser("volume-create"); v.add_argument("--size", type=int, default=VOLUME_SIZE_GB)
    v.add_argument("--dc", default=DATACENTER); v.add_argument("--yes", action="store_true"); v.set_defaults(fn=cmd_volume_create)
    vr = sub.add_parser("volume-resize", help="grow the project volume (asks first; a volume never shrinks)")
    vr.add_argument("--size", type=int, required=True, help="new size in GB")
    vr.add_argument("--yes", action="store_true"); vr.set_defaults(fn=cmd_volume_resize)
    r = sub.add_parser("run")
    r.add_argument("--job", required=True, help="job script path relative to the repo root (scripts/jobs/<name>.sh)")
    r.add_argument("--gpu", help="force one GPU name, e.g. 'RTX PRO 4500' (L4 is refused)")
    r.add_argument("--max-minutes", type=int, default=MAX_MINUTES)
    r.add_argument("--grace", type=int, default=120,
                   help="seconds the pod waits after the job before stopping itself (the runner stops it "
                        "earlier, right after a successful collection)")
    r.add_argument("--disk", type=int, default=CONTAINER_DISK_GB, help="container disk GB (wiped with the pod; ~$0.10/GB/month)")
    r.add_argument("--env", action="append", metavar="KEY=VALUE", help="extra environment variable for the job (repeatable)")
    r.add_argument("--purpose", help="text for docs/gpu-log.md")
    r.add_argument("--no-volume", action="store_true", help="run without the network volume (nothing persists)")
    r.add_argument("--keep", action="store_true", help="do not terminate the stopped pod")
    r.add_argument("--allow-dirty", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--over-5-ok", action="store_true",
                   help="the user OK'd a pod whose worst case is over $5 (CLAUDE.md: ask before any action over $5)")
    r.add_argument("--repo-url", default="https://github.com/cihantanaydin-svg/WenArt_RUN.git")
    r.set_defaults(fn=cmd_run)
    for name, fn in (("logs", cmd_logs), ("stop", cmd_stop), ("terminate", cmd_terminate)):
        s = sub.add_parser(name); s.add_argument("pod_id"); s.set_defaults(fn=fn)
    at = sub.add_parser("attach", help="re-attach to a running wenart pod whose runner died: wait, collect, "
                                       "stop, log, terminate")
    at.add_argument("pod_id"); at.add_argument("--purpose", default="re-attached run")
    at.set_defaults(fn=cmd_attach)
    sw = sub.add_parser("sweep", help="stop and terminate every wenart-* pod (asks first)")
    sw.add_argument("--yes", action="store_true"); sw.set_defaults(fn=cmd_sweep)
    a = ap.parse_args(argv)
    if not os.environ.get("RUNPOD_API_KEY"):
        print("RUNPOD_API_KEY is not set", file=sys.stderr); return 2
    try:
        return a.fn(a)
    except (RuntimeError, ApiError) as e:
        print(f"error: {e}", file=sys.stderr); return 1


if __name__ == "__main__":
    sys.exit(main())
