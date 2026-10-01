#!/usr/bin/env python3
"""RunPod runner for WenArt_RUN. Every GPU job goes through here.

Hard rules (CLAUDE.md): max $1.00/GPU-hour, max $10/day, max 2 h per run, one pod
at a time. Pods stop themselves (watchdog + end of job, see scripts/pod_entry.sh);
this runner only collects results and terminates the stopped pod.

Usage:
  gpu_run.py status                      pods, volumes, today's spend
  gpu_run.py gpus [--dc EU-RO-1]         live prices and availability of the allowed GPUs
  gpu_run.py volume-create [--size 120]  create the Network Volume (asks first)
  gpu_run.py run --job scripts/jobs/smoke.sh [--gpu "RTX A5000"] [--max-minutes 120] [--no-volume]
  gpu_run.py logs POD_ID | stop POD_ID | terminate POD_ID | sweep
Only stdlib; works in the cloud session (HTTPS proxy) and on the Mac.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
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
# Allowed GPUs in order of preference: 24 GB+, RT cores, under $1/h.
GPU_PRIORITY = ["RTX A5000", "A40", "RTX A6000", "RTX PRO 4000", "L4", "RTX 4090", "RTX PRO 4500"]
GPU_IDS = {  # catalog ids (GET /v2/catalog/gpus)
    "RTX A5000": "NVIDIA RTX A5000", "A40": "NVIDIA A40", "RTX A6000": "NVIDIA RTX A6000",
    "RTX PRO 4000": "NVIDIA RTX PRO 4000 Blackwell", "L4": "NVIDIA L4", "RTX 4090": "NVIDIA GeForce RTX 4090",
    "RTX PRO 4500": "NVIDIA RTX PRO 4500 Blackwell",
}
POLL_S = 20
BOOT_TIMEOUT_S = 15 * 60  # pod RUNNING but no status server -> stop it
UA = "wenart-gpu-run/0.1 (+https://github.com/cihantanaydin-svg/WenArt_RUN)"  # Cloudflare bans urllib's default UA


# ----------------------------------------------------------------------------- API
class ApiError(RuntimeError):
    pass


def api(method: str, path: str, body: dict | None = None, timeout: int = 60) -> dict | list | None:
    key = os.environ.get("RUNPOD_API_KEY", "")
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json")
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:800]
        raise ApiError(f"{method} {path} -> HTTP {e.code}: {detail}") from None


def fetch(url: str, timeout: int = 20) -> bytes | None:
    """GET through the RunPod HTTP proxy; None while the pod is not reachable yet."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, OSError):
        return None


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


# ---------------------------------------------------------------------- pure logic
def pick_gpu(catalog: list[dict], dc_avail: dict[str, str] | None, want: str | None,
            max_price: float = MAX_PRICE_PER_H) -> dict:
    """Choose a GPU from the live catalog. Raises with a clear message if none fits."""
    by_name = {g["name"]: g for g in catalog}
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


def append_gpu_log(text: str, row: dict) -> str:
    """Insert a row into the gpu-log table and recompute the total. Returns new text."""
    lines = text.splitlines()
    last_row = max(i for i, l in enumerate(lines) if l.startswith("|"))
    new = (f"| {row['date']} | {row['pod_id']} | {row['gpu']} | {row['minutes']} | "
           f"{row['cost']:.2f} | {row['purpose']} | {row['result']} |")
    lines.insert(last_row + 1, new)
    total = 0.0
    for l in lines:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) == 7 and cells[0] not in ("Date (UTC)", "---"):
            try:
                total += float(cells[4])
            except ValueError:
                pass
    for i, l in enumerate(lines):
        if l.startswith("**Total spent so far:"):
            rest = l.split("**", 2)[2]
            lines[i] = f"**Total spent so far: ${total:.2f}**{rest}"
    return "\n".join(lines) + "\n"


def pod_create_body(name: str, gpu_id: str, volume_id: str | None, env: dict, dc: str | None) -> dict:
    body = {
        "name": name,
        "image": IMAGE,
        "cloud": "SECURE",
        "gpu": {"id": gpu_id, "count": 1, "minCudaVersion": "12.8"},
        "disk": CONTAINER_DISK_GB,
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
def live_pods() -> list[dict]:
    return [p for p in api("GET", "/v2/pods")["pods"] if p["status"] not in ("EXITED", "TERMINATED")]


def spent_today() -> float:
    start = utc_now().strftime("%Y-%m-%dT00:00:00Z")
    try:
        d = api("GET", f"/v2/billing/pods?startTime={start}&bucketSize=day")
        return float(d["metadata"]["totals"]["totalAmount"])
    except (ApiError, KeyError, TypeError):
        return 0.0


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


def pod_logs(pod_id: str, tail: int = 2000) -> str:
    """Read the SSE log stream until it goes quiet."""
    key = os.environ.get("RUNPOD_API_KEY", "")
    req = urllib.request.Request(f"{API}/v2/pods/{pod_id}/logs?source=container&tail={tail}")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("User-Agent", UA)
    out = []
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            while True:
                line = r.readline()
                if not line:
                    break
                s = line.decode(errors="replace").rstrip("\n")
                if s.startswith("data:"):
                    try:
                        out.append(json.loads(s[5:]).get("message", s[5:]))
                    except (json.JSONDecodeError, AttributeError):
                        out.append(s[5:].strip())
    except (socket.timeout, TimeoutError, urllib.error.URLError, OSError):
        pass
    return "\n".join(str(x) for x in out)


def terminate(pod_id: str) -> None:
    try:
        api("DELETE", f"/v2/pods/{pod_id}")
        print(f"pod {pod_id} terminated")
    except ApiError as e:
        print(f"terminate failed: {e}")


def stop(pod_id: str) -> None:
    try:
        api("POST", f"/v2/pods/{pod_id}/action", {"action": "stop"})
        print(f"pod {pod_id} stop requested")
    except ApiError as e:
        print(f"stop failed: {e}")


def log_run(pod_id: str, gpu: str, minutes: float, cost: float, purpose: str, result: str) -> None:
    row = {"date": utc_now().strftime("%Y-%m-%d %H:%M"), "pod_id": pod_id, "gpu": gpu,
           "minutes": int(round(minutes)), "cost": cost, "purpose": purpose, "result": result}
    GPU_LOG.write_text(append_gpu_log(GPU_LOG.read_text(), row))
    print(f"logged to docs/gpu-log.md: {row}")


# ----------------------------------------------------------------------- commands
def cmd_status(_: argparse.Namespace) -> int:
    pods = api("GET", "/v2/pods")["pods"]
    print(f"pods: {len(pods)}")
    for p in pods:
        print(f"  {p['id']} {p['status']} {p.get('gpu', {}).get('id', '-')} ${p.get('cost', 0)}/h {p.get('dataCenterId')}")
    vols = api("GET", "/v2/network-volumes")["networkVolumes"]
    print(f"network volumes: {len(vols)}")
    for v in vols:
        print(f"  {v['id']} {v['name']} {v['size']} GB {v['dataCenter']}")
    print(f"spent today (UTC): ${spent_today():.2f} of ${MAX_PER_DAY:.2f}")
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


def cmd_run(a: argparse.Namespace) -> int:
    job_path = Path(a.job)
    if not (ROOT / job_path).exists():
        raise RuntimeError(f"job script not found: {job_path}")
    commit = git("rev-parse", "HEAD")
    if not a.allow_dirty:
        if git("status", "--porcelain"):
            raise RuntimeError("working tree not clean; commit and push first (or --allow-dirty)")
        if not git("branch", "-r", "--contains", commit):
            raise RuntimeError("HEAD is not pushed; the pod clones from GitHub (or --allow-dirty)")
    minutes = min(a.max_minutes, MAX_MINUTES)

    running = live_pods()
    if running:
        raise RuntimeError("a pod is already live (one at a time): " + ", ".join(p["id"] for p in running))

    volume = None if a.no_volume else find_volume()
    if not a.no_volume and volume is None:
        raise RuntimeError(f"no network volume '{VOLUME_NAME}'; run 'volume-create' or use --no-volume")
    dc = volume["dataCenter"] if volume else None
    gpu = pick_gpu(catalog(), dc_availability(dc) if dc else None, a.gpu)
    today = spent_today()
    check_limits(gpu["price"], minutes, today)
    worst = gpu["price"] * minutes / 60
    print(f"GPU {gpu['name']} ({gpu['memory']} GB) ${gpu['price']}/h, stock {gpu['availability']}, "
          f"DC {dc or 'any'}, max {minutes} min -> worst case ${worst:.2f}; spent today ${today:.2f}")
    if a.dry_run:
        print("dry run, no pod created"); return 0

    job_id = utc_now().strftime("%Y%m%d-%H%M%S") + "-" + job_path.stem
    token = secrets.token_urlsafe(24)
    entry = base64.b64encode((ROOT / "scripts" / "pod_entry.sh").read_bytes()).decode()
    env = {
        "WENART_ENTRY": entry, "JOB_ID": job_id, "JOB_TOKEN": token,
        "JOB_CMD": f"bash {job_path.as_posix()}",
        "REPO_URL": a.repo_url, "REPO_COMMIT": commit,
        "MAX_RUNTIME_S": str(minutes * 60), "GRACE_S": str(a.grace),
        "HF_TOKEN": "{{ RUNPOD_SECRET_hf_token }}", "HF_HOME": "/workspace/hf",
    }
    body = pod_create_body(f"wenart-{job_id}", gpu["id"], volume["id"] if volume else None, env, dc)
    pod = api("POST", "/v2/pods", body)
    pod_id = pod["id"]
    t0 = time.time()
    run_dir = RUNS_DIR / job_id
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"pod {pod_id} created ({pod['status']}); job {job_id}; local dir runs/{job_id}")
    status_url = f"https://{pod_id}-8000.proxy.runpod.net/{token}/"
    result = "unknown"
    gpu_name = gpu["name"]
    price = gpu["price"]
    last_state = None
    final_status: dict | None = None
    self_stopped = False
    first_running = None
    seen_status = False
    try:
        deadline = t0 + minutes * 60 + a.grace + 600
        while time.time() < deadline:
            p = api("GET", f"/v2/pods/{pod_id}")
            if p["status"] == "RUNNING" and first_running is None:
                first_running = time.time()
            if first_running and not seen_status and time.time() - first_running > BOOT_TIMEOUT_S:
                result = "no status server after boot timeout"
                print(f"{result}; stopping the pod")
                break
            price = p.get("cost") or price
            gpu_name = (p.get("gpu") or {}).get("id", gpu_name)
            st = None
            raw = fetch(status_url + "status.json") if p["status"] == "RUNNING" else None
            if raw:
                try:
                    st = json.loads(raw)
                    seen_status = True
                except json.JSONDecodeError:
                    st = None
            state = f"{p['status']}/{st['state'] if st else '-'}"
            if state != last_state:
                print(f"[{int(time.time() - t0):5d}s] {state}  ${price}/h")
                last_state = state
            if st and st.get("state") == "done" and final_status is None:
                final_status = st
                print(f"job done, exit code {st['exit_code']}; collecting results")
                collect(status_url, run_dir)
            if p["status"] in ("EXITED", "TERMINATED"):
                self_stopped = final_status is not None
                break
            if p["status"] == "ERROR":
                result = "pod ERROR"
                break
            time.sleep(POLL_S)
        else:
            result = "runner timeout"
    except KeyboardInterrupt:
        result = "interrupted"
    finally:
        minutes_used = (time.time() - t0) / 60
        (run_dir / "pod.log").write_text(pod_logs(pod_id))
        p = api("GET", f"/v2/pods/{pod_id}")
        if p["status"] not in ("EXITED", "TERMINATED"):
            print(f"pod still {p['status']} -> stopping it from here")
            stop(pod_id)
            for _ in range(30):
                time.sleep(5)
                if api("GET", f"/v2/pods/{pod_id}")["status"] in ("EXITED", "TERMINATED"):
                    break
        if final_status is not None:
            code = final_status["exit_code"]
            result = ("ok" if code == 0 else f"exit {code}") + (", self-stop ok" if self_stopped else ", stopped by runner")
        cost = price * minutes_used / 60
        log_run(pod_id, gpu_name, minutes_used, cost, a.purpose or job_path.stem, result)
        if not a.keep:
            terminate(pod_id)
        print(f"result: {result}; {minutes_used:.1f} min, ~${cost:.2f}; files in runs/{job_id}/")
    return 0 if final_status and final_status["exit_code"] == 0 else 1


def collect(status_url: str, run_dir: Path) -> None:
    """Download job.log and everything listed in results/ (small files only)."""
    for name in ("status.json", "job.log"):
        raw = fetch(status_url + name, timeout=60)
        if raw:
            (run_dir / name).write_bytes(raw)
    listing = fetch(status_url + "results/", timeout=30)
    if not listing:
        return
    import re
    (run_dir / "results").mkdir(exist_ok=True)
    for name in re.findall(r'href="([^"/?]+)"', listing.decode(errors="replace")):
        raw = fetch(status_url + "results/" + name, timeout=120)
        if raw is not None and len(raw) < 20_000_000:
            (run_dir / "results" / urllib.parse.unquote(name)).write_bytes(raw)
    print(f"collected {len(list((run_dir / 'results').iterdir()))} result files")


def cmd_logs(a: argparse.Namespace) -> int:
    print(pod_logs(a.pod_id)); return 0


def cmd_stop(a: argparse.Namespace) -> int:
    stop(a.pod_id); return 0


def cmd_terminate(a: argparse.Namespace) -> int:
    terminate(a.pod_id); return 0


def cmd_sweep(_: argparse.Namespace) -> int:
    pods = api("GET", "/v2/pods")["pods"]
    for p in pods:
        if p["status"] not in ("EXITED", "TERMINATED"):
            stop(p["id"])
    for p in pods:
        terminate(p["id"])
    print("sweep done" if pods else "nothing to sweep")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    g = sub.add_parser("gpus"); g.add_argument("--dc"); g.set_defaults(fn=cmd_gpus)
    v = sub.add_parser("volume-create"); v.add_argument("--size", type=int, default=VOLUME_SIZE_GB)
    v.add_argument("--dc", default=DATACENTER); v.add_argument("--yes", action="store_true"); v.set_defaults(fn=cmd_volume_create)
    r = sub.add_parser("run")
    r.add_argument("--job", required=True, help="job script path relative to the repo root")
    r.add_argument("--gpu", help="force one GPU name, e.g. 'RTX A5000'")
    r.add_argument("--max-minutes", type=int, default=MAX_MINUTES)
    r.add_argument("--grace", type=int, default=120, help="seconds the pod waits after the job before stopping")
    r.add_argument("--purpose", help="text for docs/gpu-log.md")
    r.add_argument("--no-volume", action="store_true", help="run without the network volume (nothing persists)")
    r.add_argument("--keep", action="store_true", help="do not terminate the stopped pod")
    r.add_argument("--allow-dirty", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--repo-url", default="https://github.com/cihantanaydin-svg/WenArt_RUN.git")
    r.set_defaults(fn=cmd_run)
    for name, fn in (("logs", cmd_logs), ("stop", cmd_stop), ("terminate", cmd_terminate)):
        s = sub.add_parser(name); s.add_argument("pod_id"); s.set_defaults(fn=fn)
    sub.add_parser("sweep", help="stop and terminate every pod").set_defaults(fn=cmd_sweep)
    a = ap.parse_args(argv)
    if not os.environ.get("RUNPOD_API_KEY"):
        print("RUNPOD_API_KEY is not set", file=sys.stderr); return 2
    try:
        return a.fn(a)
    except (RuntimeError, ApiError) as e:
        print(f"error: {e}", file=sys.stderr); return 1


if __name__ == "__main__":
    sys.exit(main())
