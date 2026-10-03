#!/usr/bin/env python3
"""RunPod runner for WenArt_RUN. Every GPU job goes through here.

Hard rules (CLAUDE.md): max $1.00/GPU-hour, max $10/day, max 2 h per run, one pod
at a time. Pods stop themselves (watchdog + end of job, see scripts/pod_entry.sh).
The runner collects the results (results/ and, for private projects, results-private/
into runs/<job>/), stops the pod right after a successful collection instead of
paying for the grace period (docs/milestone6.md §7.2; the in-pod watchdog and
job-end stop stay armed) and terminates the stopped pod.

Usage:
  gpu_run.py status                      pods, volumes, today's spend
  gpu_run.py gpus [--dc EU-RO-1]         live prices and availability of the allowed GPUs
  gpu_run.py volume-create [--size 120]  create the Network Volume (asks first)
  gpu_run.py run --job scripts/jobs/smoke.sh [--gpu "RTX PRO 4500"] [--max-minutes 120] [--no-volume]
  gpu_run.py logs POD_ID | stop POD_ID | terminate POD_ID | sweep [--yes]
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

MAX_PRICE_PER_H = 1.00
MAX_PER_DAY = 10.00
MAX_MINUTES = 120
IMAGE = "runpod/pytorch:1.4.0-cu1281-torch291-ubuntu2404"
DATACENTER = "EU-RO-1"
VOLUME_NAME = "wenart"
VOLUME_SIZE_GB = 120
CONTAINER_DISK_GB = 30
POD_PREFIX = "wenart-"
# Allowed GPUs, fastest first (user decision of 3 Oct 2026: "for faster job finish choose a better GPU"):
# 24 GB+, RT cores, under the $1/h limit. Measured: the RTX 4090 renders and polishes 25-30 % faster than
# the RTX PRO 4500 (M5 runs 1a/2); the RTX 5090, RTX PRO 5000, RTX 6000 Ada and L40 are not measured yet
# (expected faster or equal; they had no stock in EU-RO-1 on 3 Oct 2026). Ampere cards last.
GPU_PRIORITY = ["RTX 5090", "RTX PRO 5000", "RTX 4090", "RTX 6000 Ada", "L40", "RTX PRO 4500", "RTX 5000 Ada",
                "RTX PRO 4000", "RTX A6000", "A40", "RTX A5000"]
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


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


# ---------------------------------------------------------------------- pure logic
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


COLLECT_MAX_DEPTH = 4
COLLECT_WORKERS = 8           # parallel result downloads (one at a time: 0.81 s per file)
COLLECT_MAX_FILE = 20_000_000
COLLECT_MAX_TOTAL = 400_000_000   # one total over results/ and results-private/
COLLECT_TRIES = 3             # collection attempts while the pod runs (a failed one is retried at the next poll)
COLLECT_LISTING_TRIES = 5     # tries of the job folder listing and of each tree's root listing (10 s apart)
# Private results first: a small allow-listed set (docs/milestone6.md §2.1) that exists nowhere else
# in the session; both trees share the caps.
COLLECT_TREES = ("results-private", "results")
RUNNER_STOP_RESULT = "stopped by runner after collect (watchdog and job-end stop armed)"


def parse_listing(html: str) -> tuple[list[str], list[str]]:
    """Files and sub-directories of a python http.server directory listing (names unquoted)."""
    files, dirs = [], []
    for href in re.findall(r'href="([^"?]+)"', html):
        if href.startswith(("/", "..", "?")) or "/" in href.rstrip("/"):
            continue
        name = urllib.parse.unquote(href)
        (dirs if href.endswith("/") else files).append(name.rstrip("/"))
    return files, dirs


def collect_all(status_url: str, run_dir: Path, workers: int = COLLECT_WORKERS) -> dict:
    """Download status.json, job.log, results/ and (when the job wrote it) results-private/ from the
    pod into ``run_dir``, recursively (depth <= COLLECT_MAX_DEPTH). Small files only: a file of
    COLLECT_MAX_FILE bytes or more is left out, and the downloads stop at COLLECT_MAX_TOTAL bytes
    over both trees.

    The folders are listed first, then the files are fetched with ``workers`` parallel requests:
    one at a time took 0.81 s per file through the pod proxy (M5 runs 0 and 0b), so the 500-1000
    result files of an M5 run would outlast the grace period.

    ``results-private/`` is walked when the job folder's listing shows it (or, when that listing
    still fails after ``COLLECT_LISTING_TRIES`` tries, tried once quietly); the private aliases inside
    it are symlinks the status server follows.

    Returns ``{"files", "bytes", "capped", "failed", "ok", "job_log", "job_listed", "trees": {tree:
    {"listed", "files"}}}``; ``ok`` (a successful collection, after which the runner may stop the pod)
    = job.log fetched, the job folder listed (without it the runner cannot know whether
    results-private/ exists), every tree that exists listed completely and no listed file failed to
    download (``failed``: fetch gave None; a file left out for its size is not a failure). The size
    cap (``capped``) stays a warning: it is deliberate, and a retry would only hit it again. A failed
    collection is retried at the next poll (``COLLECT_TRIES``), so a proxy glitch never lets the runner
    stop the pod with files missing (review F2).
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
    state = {"n": 0, "total": 0, "capped": False, "failed": []}

    def get(item: tuple[str, str]) -> None:
        tree, rel_name = item
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
            return                                     # left out for its size: deliberate, not a failure
        with lock:
            if state["total"] > COLLECT_MAX_TOTAL:
                state["capped"] = True
                return
            state["n"] += 1
            state["total"] += len(raw)
        (run_dir / tree / rel_name).write_bytes(raw)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        list(pool.map(get, todo))
    if state["capped"]:
        print("warning: result size cap reached, not every file was downloaded")
    failed = sorted(state["failed"])
    if failed:
        print(f"warning: {len(failed)} result file(s) failed to download, e.g. {', '.join(failed[:3])}")
    private = trees.get("results-private", {}).get("files", 0)
    print(f"collected {state['n']} result files ({state['total'] / 1e6:.1f} MB)"
          + (f", {private} of them listed under results-private/" if "results-private" in trees else ""))
    ok = (got["job.log"] and job_listing is not None and "results" in trees
          and all(t["listed"] for t in trees.values()) and not failed)
    return {"files": state["n"], "bytes": state["total"], "capped": state["capped"], "failed": len(failed),
            "ok": bool(ok), "job_log": got["job.log"], "job_listed": job_listing is not None, "trees": trees}


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
    gpu = pick_gpu(catalog(), dc_availability(dc) if dc else None, a.gpu)
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
                col = collect_all(status_url, run_dir)
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
    r.add_argument("--repo-url", default="https://github.com/cihantanaydin-svg/WenArt_RUN.git")
    r.set_defaults(fn=cmd_run)
    for name, fn in (("logs", cmd_logs), ("stop", cmd_stop), ("terminate", cmd_terminate)):
        s = sub.add_parser(name); s.add_argument("pod_id"); s.set_defaults(fn=fn)
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
