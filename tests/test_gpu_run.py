"""CPU tests for the runner (no network): pure logic, the collection from a fake status server on
127.0.0.1 (python http.server serving a token link to a job folder, as scripts/pod_entry.sh does), and
``run`` end to end against a fake RunPod API (stop right after the collection, gpu-log wording)."""
import argparse
import functools
import http.server
import importlib.util
import json
import os
import sys
import threading
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

**Total spent so far: $0.00** (budget: $100; limits: $5.00/GPU-hour, $10/day, 2 h/run)
"""
ROW = {"date": "2026-10-01 12:00", "pod_id": "abc", "gpu": "L4", "minutes": 12, "cost": 0.1,
       "purpose": "smoke", "result": "ok"}


def test_pick_gpu_prefers_priority_order_and_stock():
    # A 115-min pod may cost at most $5 without the user's OK: $2.61/h, so the H100 ($2.69) is skipped.
    g = gpu_run.pick_gpu(CATALOG, None, None, max_price=gpu_run.action_price_limit(115))
    assert g["name"] == "RTX 4090"  # PRO 4500 / PRO 4000 not in the catalog, never L4 (docs/milestone6.md §0)
    # With the user's OK for a bigger action the faster H100 is taken (per-hour limit $5).
    g = gpu_run.pick_gpu(CATALOG, None, None, max_price=gpu_run.action_price_limit(115, over_5_ok=True))
    assert g["name"] == "H100 SXM"


def test_price_limits_of_3_oct_2026():
    """User decision of 3 Oct 2026: $5 per GPU-hour; CLAUDE.md still asks before any action over $5."""
    assert gpu_run.MAX_PRICE_PER_H == 5.00 and gpu_run.MAX_ACTION_USD == 5.00 and gpu_run.MAX_PER_DAY == 30.00
    assert gpu_run.action_price_limit(115) == pytest.approx(5.0 * 60 / 115)          # $2.61/h
    assert gpu_run.action_price_limit(60) == 5.0 and gpu_run.action_price_limit(30) == 5.0
    assert gpu_run.action_price_limit(115, over_5_ok=True) == 5.0


def test_gpu_priority_fastest_first():
    """User decisions of 3 Oct 2026: the fastest GPU in stock under $5/h (never L4, no AMD, no MIG slices)."""
    assert gpu_run.GPU_PRIORITY[:2] == ["RTX PRO 6000", "RTX PRO 6000 WK"]
    assert gpu_run.GPU_PRIORITY.index("RTX 4090") < gpu_run.GPU_PRIORITY.index("RTX PRO 4500")
    assert not {"L4", "MI300X", "PRO 6000 MIG 48GB", "PRO 6000 MIG 24GB"} & set(gpu_run.GPU_PRIORITY)
    cat = CATALOG + [{"name": "RTX PRO 4500", "id": "NVIDIA RTX PRO 4500 Blackwell", "memory": 32,
                      "price": {"secure": 0.69}, "availability": "LOW"}]
    limit = gpu_run.action_price_limit(115)
    assert gpu_run.pick_gpu(cat, None, None, max_price=limit)["name"] == "RTX 4090"
    fast = cat + [{"name": "RTX PRO 6000", "id": "NVIDIA RTX PRO 6000 Blackwell Server Edition", "memory": 96,
                   "price": {"secure": 2.09}, "availability": "LOW"}]
    assert gpu_run.pick_gpu(fast, None, None, max_price=limit)["name"] == "RTX PRO 6000"
    too_dear = cat + [{"name": "RTX PRO 6000", "id": "NVIDIA RTX PRO 6000 Blackwell Server Edition", "memory": 96,
                       "price": {"secure": 5.09}, "availability": "HIGH"}]
    assert gpu_run.pick_gpu(too_dear, None, None, max_price=5.0)["name"] == "H100 SXM"   # over the $5/h limit
    assert gpu_run.pick_gpu(cat, {"RTX 4090": "LOW"}, None)["name"] == "RTX 4090"   # the 4500 has no stock here
    with pytest.raises(RuntimeError, match="L4 is not allowed"):
        gpu_run.pick_gpu(CATALOG, None, "L4")
    only_l4 = [g for g in CATALOG if g["name"] == "L4"]
    with pytest.raises(RuntimeError, match="no allowed GPU"):
        gpu_run.pick_gpu(only_l4, None, None)


def test_pick_gpu_uses_dc_availability():
    g = gpu_run.pick_gpu(CATALOG, {"RTX A5000": "LOW"}, None)
    assert g["name"] == "RTX A5000"
    with pytest.raises(RuntimeError, match="no stock"):
        gpu_run.pick_gpu(CATALOG, {}, None)


def test_pick_gpu_refuses_expensive():
    dear = CATALOG + [{"name": "H200 SXM", "id": "NVIDIA H200", "memory": 141, "price": {"secure": 5.49},
                       "availability": "HIGH"}]
    with pytest.raises(RuntimeError, match="over the"):                     # over the $5/h limit
        gpu_run.pick_gpu(dear, None, "H200 SXM")
    with pytest.raises(RuntimeError, match="over the"):                     # a 115-min pod over $5 without OK
        gpu_run.pick_gpu(CATALOG, None, "H100 SXM", max_price=gpu_run.action_price_limit(115))
    assert gpu_run.pick_gpu(CATALOG, None, "H100 SXM",
                            max_price=gpu_run.action_price_limit(115, over_5_ok=True))["name"] == "H100 SXM"


def test_check_limits():
    gpu_run.check_limits(0.27, 120, 0.0)
    gpu_run.check_limits(1.01, 10, 0.0)                     # allowed since 3 Oct 2026 ($5/h limit)
    with pytest.raises(RuntimeError):
        gpu_run.check_limits(5.01, 10, 0.0)
    with pytest.raises(RuntimeError):
        gpu_run.check_limits(0.5, 121, 0.0)
    gpu_run.check_limits(0.9, 120, 19.0)                     # $20.80 a day: allowed since 4 Oct 2026 ($30/day)
    with pytest.raises(RuntimeError, match="day"):
        gpu_run.check_limits(0.9, 120, 29.0)


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


# --------------------------------------------------------------------------
# A fake status server (python http.server, as on the pod) and a fake RunPod API
# --------------------------------------------------------------------------

TOKEN = "tok3n"
POD_ID = "pod1"
PROXY_HOST = f"https://{POD_ID}-8000.proxy.runpod.net/"
PROXY_URL = f"{PROXY_HOST}{TOKEN}/"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):          # no access log, like the server of pod_entry.sh
        pass


def write_file(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


def make_job_dir(root: Path, private: bool = True, results: bool = True, job_log: bool = True) -> Path:
    """$JOB_DIR as pod_entry.sh and full.sh leave it: status.json, job.log, results/ and results-private/
    with the alias linked to the volume's results-private/<alias> (here a folder outside the job dir)."""
    job = root / "jobs" / "job1"
    job.mkdir(parents=True)
    (job / "status.json").write_text(json.dumps({"job_id": "job1", "state": "done", "exit_code": 0}))
    if job_log:
        (job / "job.log").write_text("real-01 report ok 1.0s\n")
    if results:
        for rel, data in {"run_manifest.json": "{}", "final/synthetic-04/final_report.md": "# ok",
                          "final/synthetic-04/a b_final_preview.jpg": "jpg", "run/synthetic-04/logs/layout.log": "x",
                          "renders/synthetic-04/controls/hide_f_1/render_manifest.json": "{}"}.items():
            write_file(job / "results" / rel, data)
    if private:
        volume = root / "volume" / "results-private" / "real-01"
        for rel, data in {"final/final_report.md": "# private", "final/contact_L0.jpg": "jpg",
                          "run/pipeline.json": "{}"}.items():
            write_file(volume / rel, data)
        (job / "results-private").mkdir()
        os.symlink(volume, job / "results-private" / "real-01")
        write_file(job / "results-private" / "_run_manifest.json", "{}")
        write_file(job / "results-private" / "_logs" / "orchestrator.log", "trace")
    return job


def files_under(folder: Path) -> list[str]:
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())


@pytest.fixture
def status_server(tmp_path, monkeypatch):
    """Serve <public>/<token> -> $JOB_DIR on 127.0.0.1 (as pod_entry.sh does) and route the runner's
    proxy URL to it through the real ``fetch``."""
    public = tmp_path / "public"
    public.mkdir()
    (public / "index.html").write_text("")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                                             functools.partial(_QuietHandler, directory=str(public)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    for var in ("NO_PROXY", "no_proxy"):
        monkeypatch.setenv(var, "127.0.0.1,localhost")
    real_fetch = gpu_run.fetch
    requests: list[str] = []

    def routed_fetch(url, timeout=20):
        requests.append(url)
        assert url.startswith(PROXY_HOST), url
        return real_fetch(base + url[len(PROXY_HOST):], timeout=timeout)

    real_fetch_to = gpu_run.fetch_to

    def routed_fetch_to(url, path, timeout=900, max_bytes=0):
        requests.append(url)
        assert url.startswith(PROXY_HOST), url
        return real_fetch_to(base + url[len(PROXY_HOST):], path, timeout=timeout, max_bytes=max_bytes)

    monkeypatch.setattr(gpu_run, "fetch", routed_fetch)
    monkeypatch.setattr(gpu_run, "fetch_to", routed_fetch_to)
    monkeypatch.setattr(gpu_run.time, "sleep", lambda s: None)

    def link(job_dir: Path) -> None:
        if (public / TOKEN).is_symlink():
            (public / TOKEN).unlink()
        os.symlink(job_dir, public / TOKEN)

    yield {"link": link, "requests": requests, "root": tmp_path}
    server.shutdown()
    server.server_close()


def new_dir(path: Path) -> Path:
    path.mkdir(parents=True)
    return path


def test_collect_walks_results_and_results_private(status_server, tmp_path):
    status_server["link"](make_job_dir(status_server["root"]))
    run_dir = new_dir(tmp_path / "runs" / "job1")
    col = gpu_run.collect_all(PROXY_URL, run_dir, workers=4)
    assert col["ok"] and col["job_log"] and not col["capped"] and col["files"] == 10
    assert col["trees"] == {"results-private": {"listed": True, "files": 5}, "results": {"listed": True, "files": 5}}
    assert files_under(run_dir / "results-private") == [
        "_logs/orchestrator.log", "_run_manifest.json", "real-01/final/contact_L0.jpg",
        "real-01/final/final_report.md", "real-01/run/pipeline.json"]
    assert (run_dir / "results-private" / "real-01" / "final" / "final_report.md").read_text() == "# private"
    assert "final/synthetic-04/a b_final_preview.jpg" in files_under(run_dir / "results")
    assert "renders/synthetic-04/controls/hide_f_1/render_manifest.json" in files_under(run_dir / "results")
    assert (run_dir / "job.log").is_file() and (run_dir / "status.json").is_file()
    assert gpu_run.collect(PROXY_URL, new_dir(tmp_path / "again"), workers=1) == 10


def test_collect_without_private_results(status_server, tmp_path):
    status_server["link"](make_job_dir(status_server["root"], private=False))
    run_dir = new_dir(tmp_path / "run")
    col = gpu_run.collect_all(PROXY_URL, run_dir)
    assert col["ok"] and set(col["trees"]) == {"results"} and not (run_dir / "results-private").exists()
    assert not any("results-private" in u for u in status_server["requests"])   # not in the job listing


def test_collect_caps_are_shared_by_both_trees(status_server, tmp_path, monkeypatch):
    status_server["link"](make_job_dir(status_server["root"]))
    monkeypatch.setattr(gpu_run, "COLLECT_MAX_TOTAL", 10)     # one total over results-private/ and results/
    col = gpu_run.collect_all(PROXY_URL, new_dir(tmp_path / "capped"), workers=1)
    assert col["capped"] and col["files"] < 10 and col["bytes"] <= 10 + len("# private")
    monkeypatch.setattr(gpu_run, "COLLECT_MAX_TOTAL", 400_000_000)
    monkeypatch.setattr(gpu_run, "COLLECT_MAX_FILE", 3)        # files of 3 bytes or more are left out
    col = gpu_run.collect_all(PROXY_URL, new_dir(tmp_path / "small"))
    assert col["ok"] and col["files"] == 5                     # the four 2-byte {} files and the 1-byte "x"


# The layout of the prep job's $RESULTS (docs/milestone7.md §9.2; wenart/run/prep.py): every file within
# COLLECT_MAX_DEPTH folders of results/.
PREP_RESULTS = ("prep_manifest.json", "setup_polish.json", "timing/gpu_speed.json",
                "detect/detector_calibration.json", "detect/detect_pairs.json",
                "library/catalog_objaverse.json", "library/library_report.md", "library/ATTRIBUTION.md",
                "library/judge/answers_qwen3-vl-8b.json", "library/judge/sheets/u1.jpg", "library/thumbs/sofa/u1.jpg",
                "library/thumbs/NOTICE.md", "recognition/real01/answers_glm-4.6v-flash.json",
                "recognition/real01/requests.json", "recognition/real01/crops/sym_L0_1_ctx.png",
                "furniture/real01-scan/debug/real01-scan_p1.png", "furniture/real01/building.json",
                "tests/pytest-recognition.log", "logs/vllm-qwen.log")


def test_collect_takes_the_whole_prep_results_tree_and_names_files_left_out_for_size(
        status_server, tmp_path, monkeypatch):
    job = tmp_path / "jobs" / "prep"
    (job / "results").mkdir(parents=True)
    (job / "status.json").write_text(json.dumps({"job_id": "prep", "state": "done", "exit_code": 0}))
    (job / "job.log").write_text("prep ok\n")
    for rel in PREP_RESULTS:
        write_file(job / "results" / rel, "{}")
    write_file(job / "results" / "library" / "survey.json", "x" * 64)          # over the (patched) size limit
    status_server["link"](job)
    monkeypatch.setattr(gpu_run, "COLLECT_MAX_FILE", 32)
    run_dir = new_dir(tmp_path / "runs" / "prep")
    col = gpu_run.collect_all(PROXY_URL, run_dir, workers=4)
    assert col["ok"] and set(col["trees"]) == {"results"} and col["files"] == len(PREP_RESULTS)
    assert files_under(run_dir / "results") == sorted(PREP_RESULTS)
    assert col["too_big"] == ["results/library/survey.json (0.0 MB)"]
    assert (run_dir / "collect_too_big.txt").read_text() == "results/library/survey.json (0.0 MB)\n"
    assert max(rel.count("/") for rel in PREP_RESULTS) <= gpu_run.COLLECT_MAX_DEPTH


def test_collect_streams_the_3d_files_past_the_small_file_caps(status_server, tmp_path, monkeypatch):
    """Milestone 9: results/final/<p>/3d/<p>.blend and .glb (the export stage) are collected whatever
    COLLECT_MAX_FILE and COLLECT_MAX_TOTAL say, after the small files, and not again when already complete."""
    job = make_job_dir(status_server["root"], private=False)
    blend, glb = b"B" * 5000, b"G" * 3000
    (job / "results" / "final" / "synthetic-04" / "3d").mkdir(parents=True)
    (job / "results" / "final" / "synthetic-04" / "3d" / "synthetic-04.blend").write_bytes(blend)
    (job / "results" / "final" / "synthetic-04" / "3d" / "synthetic-04.glb").write_bytes(glb)
    write_file(job / "results" / "final" / "synthetic-04" / "3d" / "export_manifest.json", "{}")
    status_server["link"](job)
    monkeypatch.setattr(gpu_run, "COLLECT_MAX_FILE", 100)
    monkeypatch.setattr(gpu_run, "COLLECT_MAX_TOTAL", 1000)
    run_dir = new_dir(tmp_path / "runs" / "export")
    col = gpu_run.collect_all(PROXY_URL, run_dir, workers=1)
    assert col["ok"] and not col["capped"] and not col["too_big"] and col["files"] == 6
    assert (col["big_files"], col["big_bytes"]) == (2, 8000)
    got = run_dir / "results" / "final" / "synthetic-04" / "3d"
    assert (got / "synthetic-04.blend").read_bytes() == blend and (got / "synthetic-04.glb").read_bytes() == glb
    assert (got / "export_manifest.json").read_text() == "{}" and not list(got.glob("*.part"))
    fetched = [u for u in status_server["requests"] if not u.endswith("/")]
    assert all(u.endswith((".blend", ".glb")) for u in fetched[-2:])       # after every small file
    # A second collection keeps the complete local copies; a file over the big-file cap is named, not fetched.
    (got / "synthetic-04.blend").write_bytes(b"x" * 5000)                   # same size: kept as it is
    monkeypatch.setattr(gpu_run, "COLLECT_BIG_MAX_FILE", 4000)
    col = gpu_run.collect_all(PROXY_URL, run_dir, workers=2)
    assert (got / "synthetic-04.blend").read_bytes() == b"x" * 5000
    assert col["too_big"] == ["results/final/synthetic-04/3d/synthetic-04.blend (over 0 MB)"]
    assert col["ok"] and col["big_files"] == 1


def test_big_results_are_only_the_3d_files():
    assert gpu_run.is_big_result("final/synthetic-04/3d/synthetic-04.blend")
    assert gpu_run.is_big_result("real-01/final/3d/real-01.glb")                # private layout
    assert not gpu_run.is_big_result("final/synthetic-04/3d/export_manifest.json")
    assert not gpu_run.is_big_result("library/models/abo/x.glb") and not gpu_run.is_big_result("x.blend")


def test_collect_is_not_ok_without_job_log_or_results(status_server, tmp_path):
    status_server["link"](make_job_dir(status_server["root"], job_log=False))
    assert gpu_run.collect_all(PROXY_URL, new_dir(tmp_path / "r"))["ok"] is False
    status_server["link"](make_job_dir(status_server["root"] / "b", results=False))
    col = gpu_run.collect_all(PROXY_URL, new_dir(tmp_path / "r2"))
    assert col["ok"] is False and col["trees"]["results"]["listed"] is False


def failing_fetch(monkeypatch, fails, inner=None):
    """Wrap the routed ``fetch`` (or ``inner``): ``fails(url, n)`` -> True makes the n-th request of that
    URL (from 1) return None, as a proxy 502/524 or a timeout does."""
    inner = inner or gpu_run.fetch
    seen: dict[str, int] = {}

    def fetch(url, timeout=20):
        seen[url] = seen.get(url, 0) + 1
        return None if fails(url, seen[url]) else inner(url, timeout=timeout)

    monkeypatch.setattr(gpu_run, "fetch", fetch)
    return seen


def test_collect_is_not_ok_when_a_file_download_failed(status_server, tmp_path, monkeypatch):
    # Review F2 (a): a failed download (fetch -> None) was dropped silently and ok stayed True, so the
    # runner stopped the pod without the final reports.
    status_server["link"](make_job_dir(status_server["root"]))
    failing_fetch(monkeypatch, lambda url, n: url.endswith("final_report.md"))
    run_dir = new_dir(tmp_path / "r")
    col = gpu_run.collect_all(PROXY_URL, run_dir, workers=2)
    assert col["ok"] is False and col["failed"] == 2 and col["files"] == 8
    assert all(t["listed"] for t in col["trees"].values()) and col["job_log"] and col["job_listed"]
    assert not (run_dir / "results" / "final" / "synthetic-04" / "final_report.md").exists()


def test_collect_retries_the_job_listing_and_is_not_ok_without_it(status_server, tmp_path, monkeypatch):
    # Review F2 (b): the job-folder listing was tried once; when it and the one quiet results-private/
    # try failed, the private tree was dropped without a word and ok stayed True.
    status_server["link"](make_job_dir(status_server["root"]))
    routed = gpu_run.fetch
    seen = failing_fetch(monkeypatch, lambda url, n: url in (PROXY_URL, PROXY_URL + "results-private/"))
    col = gpu_run.collect_all(PROXY_URL, new_dir(tmp_path / "down"))
    assert col["ok"] is False and col["job_listed"] is False and set(col["trees"]) == {"results"}
    assert seen[PROXY_URL] == gpu_run.COLLECT_LISTING_TRIES == 5
    # A glitch on the first tries only: the listing is retried and the private tree is collected.
    seen = failing_fetch(monkeypatch, lambda url, n: url == PROXY_URL and n <= 2, inner=routed)
    run_dir = new_dir(tmp_path / "glitch")
    col = gpu_run.collect_all(PROXY_URL, run_dir)
    assert col["ok"] is True and col["job_listed"] and col["failed"] == 0 and seen[PROXY_URL] == 3
    assert col["trees"]["results-private"] == {"listed": True, "files": 5}
    assert (run_dir / "results-private" / "real-01" / "final" / "final_report.md").is_file()


class FakeRunPod:
    """The REST v2 calls cmd_run makes, in memory. ``exit_after_polls``: the pod stops itself after that
    many GET /v2/pods/<id> calls (None: only a stop request stops it)."""

    def __init__(self, exit_after_polls=None):
        self.status = "RUNNING"
        self.exit_after_polls = exit_after_polls
        self.polls = 0
        self.calls: list[tuple[str, str]] = []
        self.stop_sent_at = None
        self.terminated = False

    def api(self, method, path, body=None, timeout=60, retries=3):
        self.calls.append((method, path))
        if method == "GET" and path == "/v2/pods":
            return {"pods": []}
        if path == "/v2/network-volumes":
            return {"networkVolumes": [{"id": "vol1", "name": "wenart", "size": 120, "dataCenter": "EU-RO-1"}]}
        if path.startswith("/v2/catalog/gpus"):
            return {"gpus": [{"name": "RTX PRO 4500", "id": "NVIDIA RTX PRO 4500 Blackwell", "memory": 32,
                              "price": {"secure": 0.69}, "availability": "LOW"}]}
        if path.startswith("/v2/catalog/datacenters/"):
            return {"gpuAvailability": [{"name": "RTX PRO 4500", "availability": "LOW"}]}
        if path.startswith("/v2/billing/pods"):
            return {"metadata": {"totals": {"totalAmount": 0.0}}}
        if method == "POST" and path == "/v2/pods":
            return {"id": POD_ID, "status": "RUNNING"}
        if method == "GET" and path == f"/v2/pods/{POD_ID}":
            self.polls += 1
            if self.exit_after_polls is not None and self.polls > self.exit_after_polls:
                self.status = "EXITED"
            return {"id": POD_ID, "status": self.status, "cost": 0.69, "gpu": {"id": "RTX PRO 4500"}}
        if method == "POST" and path == f"/v2/pods/{POD_ID}/action":
            assert body == {"action": "stop"}
            self.stop_sent_at = len(self.calls) - 1
            self.status = "EXITED"
            return {}
        if method == "DELETE" and path == f"/v2/pods/{POD_ID}":
            self.terminated = True
            return None
        raise AssertionError(f"unexpected API call {method} {path}")


def run_args(**over) -> argparse.Namespace:
    args = dict(job="scripts/jobs/smoke.sh", allow_dirty=True, max_minutes=10, no_volume=False, gpu=None,
                dry_run=False, purpose="M6 test", repo_url="https://example.invalid/repo.git", grace=600, env=None,
                disk=30, keep=False)
    args.update(over)
    return argparse.Namespace(**args)


@pytest.fixture
def runner(status_server, tmp_path, monkeypatch):
    """``run(fake, job_dir)`` -> (exit code, gpu-log Result cell) of a full ``cmd_run`` against the fakes."""
    log = tmp_path / "gpu-log.md"
    log.write_text(LOG_FIXTURE)
    monkeypatch.setattr(gpu_run, "GPU_LOG", log)
    monkeypatch.setattr(gpu_run, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(gpu_run, "git", lambda *a: "abc123")
    monkeypatch.setattr(gpu_run, "pod_logs", lambda *a, **k: "")
    monkeypatch.setattr(gpu_run.signal, "signal", lambda *a: None)
    monkeypatch.setattr(gpu_run.secrets, "token_urlsafe", lambda n: TOKEN)

    def run(fake: FakeRunPod, job_dir: Path) -> tuple[int, str]:
        monkeypatch.setattr(gpu_run, "api", fake.api)
        status_server["link"](job_dir)
        rc = gpu_run.cmd_run(run_args())
        rows = [r for r in gpu_run.gpu_log_rows(log.read_text()) if r[1] == POD_ID]
        assert len(rows) == 1 and "pending:" not in log.read_text()
        return rc, rows[0][6]

    return run


def test_runner_stops_the_pod_right_after_collecting(runner, status_server, tmp_path):
    fake = FakeRunPod()
    rc, result = runner(fake, make_job_dir(status_server["root"]))
    assert rc == 0
    assert result == "ok, stopped by runner after collect (watchdog and job-end stop armed)"
    assert fake.stop_sent_at is not None and fake.terminated
    run_dir = next((tmp_path / "runs").iterdir())
    assert (run_dir / "results-private" / "real-01" / "final" / "final_report.md").is_file()
    assert (run_dir / "results" / "final" / "synthetic-04" / "final_report.md").is_file()
    # One stop request, sent after the collection (every file was already on disk), then the terminate.
    assert fake.calls.count(("POST", f"/v2/pods/{POD_ID}/action")) == 1
    assert fake.calls.index(("DELETE", f"/v2/pods/{POD_ID}")) > fake.stop_sent_at


def test_runner_reports_self_stop_when_the_pod_was_already_exited(runner, status_server):
    # GET #1: RUNNING (status.json says done: collection); GET #2 in stop_after_collect: EXITED already.
    fake = FakeRunPod(exit_after_polls=1)
    rc, result = runner(fake, make_job_dir(status_server["root"]))
    assert rc == 0 and result == "ok, self-stop ok"
    assert fake.stop_sent_at is None and fake.terminated


def test_runner_does_not_stop_early_when_the_collection_failed(runner, status_server):
    # No job.log: COLLECT_TRIES incomplete collections, then the pod stops itself (after its grace period).
    fake = FakeRunPod(exit_after_polls=5)
    rc, result = runner(fake, make_job_dir(status_server["root"], job_log=False))
    assert rc == 0 and result == "ok, self-stop ok"
    assert fake.stop_sent_at is None
    assert sum(1 for u in status_server["requests"] if u.endswith("/job.log")) == gpu_run.COLLECT_TRIES


def test_runner_retries_a_collection_with_a_failed_download_before_stopping(runner, status_server, tmp_path,
                                                                             monkeypatch):
    # Review F2: the first collection loses the private final report (proxy glitch); the runner must not
    # stop the pod after it, but collect again at the next poll and stop only after the complete one.
    report = "results-private/real-01/final/final_report.md"
    failing_fetch(monkeypatch, lambda url, n: url.endswith(report) and n == 1)
    fake = FakeRunPod()
    rc, result = runner(fake, make_job_dir(status_server["root"]))
    assert rc == 0 and result == "ok, stopped by runner after collect (watchdog and job-end stop armed)"
    assert sum(1 for u in status_server["requests"] if u.endswith("/job.log")) == 2      # two collections
    assert fake.calls.count(("POST", f"/v2/pods/{POD_ID}/action")) == 1
    run_dir = next((tmp_path / "runs").iterdir())
    assert (run_dir / report).read_text() == "# private"
    # The retry fetches only what the first attempt did not write (Milestone 10, pod L2c).
    fetched = [u for u in status_server["requests"] if u.endswith(report)]
    assert len(fetched) == 1                         # the failed first fetch never reached the server
    others = [u for u in status_server["requests"] if "results/" in u and not u.endswith("/") and not u.endswith(report)]
    assert len(others) == len(set(others)), "a file the first collection wrote was fetched again"


def test_run_result_wording():
    done = {"state": "done", "exit_code": 0}
    assert gpu_run.run_result(done, "runner", False, "unknown") == \
        "ok, stopped by runner after collect (watchdog and job-end stop armed)"
    assert gpu_run.run_result(done, "self", False, "unknown") == "ok, self-stop ok"
    assert gpu_run.run_result({"state": "done", "exit_code": 1}, None, True, "x") == "exit 1, self-stop ok"
    assert gpu_run.run_result({"state": "timeout", "exit_code": 124}, None, False, "x") == \
        "timeout (watchdog), stopped by runner"
    assert gpu_run.run_result(None, None, False, "runner timeout") == "runner timeout"


class FakeAttachPod(FakeRunPod):
    """A running pod that an earlier runner created (its env holds the job id and the status token)."""

    def api(self, method, path, body=None, timeout=60, retries=3):
        out = super().api(method, path, body, timeout, retries)
        if method == "GET" and path == f"/v2/pods/{POD_ID}":
            out = dict(out, name="wenart-job1", createdAt="2026-10-04T07:07:06.667Z",
                       env={"JOB_ID": "job1", "JOB_TOKEN": TOKEN, "MAX_RUNTIME_S": "7200", "GRACE_S": "600",
                            "HF_TOKEN": "{{ RUNPOD_SECRET_hf_token }}"})
        return out


def test_attach_collects_stops_logs_and_terminates_a_pod_whose_runner_died(status_server, tmp_path, monkeypatch,
                                                                            capsys):
    log = tmp_path / "gpu-log.md"
    log.write_text(LOG_FIXTURE)
    monkeypatch.setattr(gpu_run, "GPU_LOG", log)
    monkeypatch.setattr(gpu_run, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(gpu_run, "pod_logs", lambda *a, **k: "")
    monkeypatch.setattr(gpu_run, "POLL_S", 0)
    created = gpu_run.pod_created({"createdAt": "2026-10-04T07:07:06.667Z"})
    monkeypatch.setattr(gpu_run.time, "time", lambda: created + 3600.0)          # one hour after the start
    fake = FakeAttachPod()
    monkeypatch.setattr(gpu_run, "api", fake.api)
    status_server["link"](make_job_dir(status_server["root"]))
    rc = gpu_run.cmd_attach(argparse.Namespace(pod_id=POD_ID, purpose="M8 pod L2 (re-attached)"))
    assert rc == 0
    assert (tmp_path / "runs" / "job1" / "results" / "final" / "synthetic-04" / "final_report.md").is_file()
    assert fake.calls.count(("POST", f"/v2/pods/{POD_ID}/action")) == 1 and fake.terminated
    rows = [r for r in gpu_run.gpu_log_rows(log.read_text()) if r[1] == POD_ID]
    assert len(rows) == 1 and rows[0][3] == "60" and "re-attached" in rows[0][6]
    assert TOKEN not in capsys.readouterr().out                                  # the status token is never printed


def test_attach_leaves_a_foreign_pod_alone(monkeypatch):
    fake = FakeRunPod()
    monkeypatch.setattr(gpu_run, "api", lambda m, p, *a, **k: {"id": POD_ID, "name": "someone-else", "status": "RUNNING"})
    assert gpu_run.cmd_attach(argparse.Namespace(pod_id=POD_ID, purpose="x")) == 1


def test_volume_resize_only_grows_and_needs_the_ok(monkeypatch, capsys):
    calls = []
    vol = {"id": "vol1", "name": gpu_run.VOLUME_NAME, "size": 120, "dataCenter": "EU-RO-1"}

    def api(method, path, body=None, *a, **k):
        calls.append((method, path, body))
        if method == "GET":
            return {"networkVolumes": [vol]}
        return {**vol, "size": body["size"]}

    monkeypatch.setattr(gpu_run, "api", api)
    run = lambda *argv: gpu_run.main(["volume-resize", *argv])
    assert run("--size", "100", "--yes") == 1 and "only grows" in capsys.readouterr().out
    monkeypatch.setattr("builtins.input", lambda prompt="": "no")
    assert run("--size", "250") == 1 and "cancelled" in capsys.readouterr().out
    assert not [c for c in calls if c[0] == "PATCH"]
    assert run("--size", "250", "--yes") == 0
    assert calls[-1] == ("PATCH", "/v2/network-volumes/vol1", {"size": 250})
    out = capsys.readouterr().out
    assert "from 120 to 250 GB (+~$9.10/month" in out and "now 250 GB" in out
