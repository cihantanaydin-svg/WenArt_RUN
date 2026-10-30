"""30 Oct 2026, the pod-time item 5 (user: "Only apply the 5"): the pod packs its public results into a few tar parts
at the job's end (scripts/pack_results.py, served at <token>.pack/), the runner downloads the parts in parallel instead
of ~9,300 files one by one (real04 runs 201533, 043021 and 112241 each missed thousands of files when the pod's 120 s
wait ran out mid-download), and the job's full copies skip the result files that are already current. CPU only."""
import importlib.util
import os
import shutil
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_gpu_run as T  # noqa: E402  - the fake status server and job folder of the runner's tests
from test_gpu_run import status_server  # noqa: E402,F401  - fixture

G = T.gpu_run
spec = importlib.util.spec_from_file_location("pack_results", ROOT / "scripts" / "pack_results.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


def _job(root: Path) -> Path:
    job = T.make_job_dir(root)
    T.write_file(job / "results" / "final" / "synthetic-04" / "3d" / "synthetic-04.glb", "glb" * 10)
    T.write_file(job / "results" / "a" / "b" / "c" / "d" / "deep.json", "{}")        # depth 4: walked
    T.write_file(job / "results" / "a" / "b" / "c" / "d" / "e" / "deeper.json", "{}")  # depth 5: never was
    return job


def _serve_pack(server: dict, job: Path) -> Path:
    server["link"](job)
    pack = server["root"] / "container" / "pack"
    P.pack(job, pack)
    os.symlink(pack, server["root"] / "public" / (T.TOKEN + ".pack"))
    return pack


def test_the_pack_holds_what_the_walk_took_records_first():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        job = _job(Path(tmp))
        T.write_file(job / "results" / "big_log.txt", "x" * 64)
        sel = P.select(job)
        names = [rel for rel, _ in sel["packed"]]
        assert "a/b/c/d/deep.json" in names and "a/b/c/d/e/deeper.json" not in names
        assert [rel for rel, _ in sel["big"]] == ["final/synthetic-04/3d/synthetic-04.glb"]
        images = [i for i, n in enumerate(names) if n.endswith(".jpg")]
        assert images and min(images) > max(i for i, n in enumerate(names) if not n.endswith(".jpg"))
        assert P.split([("a", 10), ("b", 10), ("c", 10)], part_bytes=20) == [[("a", 10), ("b", 10)], [("c", 10)]]
        assert P.split([("a", 50)], part_bytes=20) == [[("a", 50)]]
        assert P.grace_s(0) == P.GRACE_BASE_S and P.grace_s(10**12) == P.GRACE_MAX_S
        assert P.grace_s(730_000_000) > 120                       # real04: 330 MB of files + 400 MB of 3D files


def test_the_runner_takes_the_parts_and_the_3d_files(status_server, tmp_path):
    job = _job(status_server["root"])
    pack = _serve_pack(status_server, job)
    man = __import__("json").loads((pack / "manifest.json").read_text())
    assert man["files"] == 6 and man["big"][0]["path"].endswith(".glb")
    run_dir = T.new_dir(tmp_path / "runs" / "job1")
    col = G.collect_all(T.PROXY_URL, run_dir, workers=4)
    assert col["ok"] and col["trees"]["results"]["packed"] and col["big_files"] == 1
    want = sorted(p.relative_to(job / "results").as_posix() for p in (job / "results").rglob("*")
                  if p.is_file() and "/e/" not in p.as_posix())
    assert T.files_under(run_dir / "results") == want
    assert (run_dir / "results" / "final" / "synthetic-04" / "final_report.md").read_text() == "# ok"
    assert len(T.files_under(run_dir / "results-private")) == 5                   # walked as before
    assert (run_dir / "pack_manifest.json").is_file() and not list((run_dir / G.PACK_LOCAL).glob("part-*"))
    walked = [u for u in status_server["requests"] if f"/{T.TOKEN}/results/" in u and not u.endswith(".glb")]
    assert not walked                                         # no file of results/ fetched one by one


def test_a_broken_part_is_completed_by_the_walk(status_server, tmp_path):
    job = _job(status_server["root"])
    pack = _serve_pack(status_server, job)
    part = next(pack.glob("part-*.tar"))
    part.write_bytes(part.read_bytes()[:-10] + b"0123456789")       # same size, wrong checksum
    run_dir = T.new_dir(tmp_path / "run")
    col = G.collect_all(T.PROXY_URL, run_dir, workers=2)
    assert col["ok"] and not col["trees"]["results"]["packed"]
    assert "run_manifest.json" in T.files_under(run_dir / "results")
    assert not (run_dir / "pack_manifest.json").exists()


def test_no_pack_walks_the_files_as_before(status_server, tmp_path):
    status_server["link"](T.make_job_dir(status_server["root"]))
    col = G.collect_all(T.PROXY_URL, T.new_dir(tmp_path / "r"), workers=2)
    assert col["ok"] and col["files"] == 10 and "packed" not in col["trees"]["results"]


def test_unpacking_takes_plain_files_inside_the_results_only(tmp_path):
    bad = tmp_path / "bad.tar"
    src = tmp_path / "f.txt"
    src.write_text("x")
    with tarfile.open(bad, "w") as tar:
        tar.add(src, arcname="../escape.txt")
        absolute = tar.gettarinfo(str(src), arcname="abs.txt")
        absolute.name = "/abs.txt"                               # tarfile.add strips the "/" itself
        with src.open("rb") as fh:
            tar.addfile(absolute, fh)
        tar.add(src, arcname="ok/f.txt")
        link = tarfile.TarInfo("ok/link")
        link.type, link.linkname = tarfile.SYMTYPE, "/etc/passwd"
        tar.addfile(link)
    dest = tmp_path / "dest"
    assert G.extract_part(bad, dest) == (1, 1)
    assert T.files_under(dest) == ["ok/f.txt"] and not (tmp_path / "escape.txt").exists()


def test_the_pack_follows_the_runner_rules_and_runs_before_done():
    assert P.G.COLLECT_MAX_DEPTH == G.COLLECT_MAX_DEPTH and P.G.COLLECT_MAX_FILE == G.COLLECT_MAX_FILE
    assert P.PACK_VERSION == G.PACK_VERSION
    entry = (ROOT / "scripts" / "pod_entry.sh").read_text()
    fin = entry[entry.index("finish() {"):]
    assert fin.index("pack_results") < fin.index('write_status "done"')
    assert 'ln -sfn "$dir" "$PUBLIC/$JOB_TOKEN.pack"' in entry


def test_a_full_copy_skips_a_current_copy(tmp_path):
    from wenart.run import copy as CP
    src, dst = tmp_path / "a.json", tmp_path / "b.json"
    src.write_text('{"a": 1}')
    assert not CP.unchanged_copy(src, dst)
    shutil.copy2(src, dst)
    assert CP.unchanged_copy(src, dst)
    time.sleep(0.01)
    src.write_text('{"a": 2}')                                  # same size, rewritten: copied again
    assert not CP.unchanged_copy(src, dst)
