"""Stage records, fingerprints, reuse and project states (docs/milestone6.md §1.2)."""
from __future__ import annotations

import json
import subprocess

import pytest

from wenart import canonical
from wenart.run import state as ST
from wenart.run.projects import REPO_ROOT


def rec(stage, status, **kw):
    return ST.StageRecord(project="p", stage=stage, status=status, **kw)


def test_canonical_hash_is_re_exported():
    assert ST.canonical_sha256 is canonical.canonical_sha256
    assert ST.VOLATILE_KEYS == canonical.VOLATILE_KEYS


def test_record_round_trip_and_status_check(tmp_path):
    r = rec("layout", "ok", rc=0, seconds=91.234, fingerprint="f" * 64, inputs={"a.json": "1"},
            outputs=["building_furnished.json"], started_utc="2026-10-02T10:00:00Z", git_commit="abc",
            log="logs/layout.log", run_id="job-1", steps=[{"name": "layout", "rc": 0, "seconds": 91.2}])
    path = ST.write_record(tmp_path, r)
    assert path == tmp_path / "run" / "layout.json"
    data = json.loads(path.read_text())
    assert data["schema_version"] == "0.1" and data["kind"] == "stage_record" and data["seconds"] == 91.23
    assert list(data)[:6] == ["schema_version", "kind", "project", "stage", "rc", "status"]
    back = ST.read_record(tmp_path, "layout")
    assert back.to_dict() == data
    assert ST.read_record(tmp_path, "missing") is None
    (tmp_path / "run" / "bad.json").write_text("{not json")
    assert ST.read_record(tmp_path, "bad") is None
    with pytest.raises(ValueError):
        rec("x", "done")
    assert ST.log_path(tmp_path, "build") == tmp_path / "run" / "logs" / "build.log"
    assert not list((tmp_path / "run").glob("*.tmp"))


def test_private_record_has_no_inputs():
    data = rec("pipeline", "ok", inputs={"/workspace/outputs-private/real-01/input/real-01": "x"}).to_dict()
    out = ST.private_record(data)
    assert "inputs" not in out and out["status"] == "ok" and "inputs" in data


def test_fingerprint_parts():
    base = ST.fingerprint("fit", "1", ["--out", "a"], {"x.json": "1", "y.json": "2"}, "code")
    assert base == ST.fingerprint("fit", "1", ["--out", "a"], {"y.json": "2", "x.json": "1"}, "code")
    for other in (ST.fingerprint("refit", "1", ["--out", "a"], {"x.json": "1", "y.json": "2"}, "code"),
                  ST.fingerprint("fit", "2", ["--out", "a"], {"x.json": "1", "y.json": "2"}, "code"),
                  ST.fingerprint("fit", "1", ["--out", "b"], {"x.json": "1", "y.json": "2"}, "code"),
                  ST.fingerprint("fit", "1", ["--out", "a"], {"x.json": "1", "y.json": "3"}, "code"),
                  ST.fingerprint("fit", "1", ["--out", "a"], {"x.json": "1", "y.json": "2"}, "code2")):
        assert other != base
    assert len(base) == 64


def test_file_hashes_ignore_volatile_keys(tmp_path):
    a = tmp_path / "building.json"
    a.write_text(json.dumps({"created_utc": "2026-10-01", "rooms": [{"id": "r", "seconds": 1}]}))
    h1 = ST.file_hashes([a])
    a.write_text(json.dumps({"rooms": [{"seconds": 9, "id": "r"}], "created_utc": "2026-10-02"}))
    assert ST.file_hashes([a]) == h1
    a.write_text(json.dumps({"rooms": [{"id": "r2"}]}))
    assert ST.file_hashes([a]) != h1
    assert list(ST.file_hashes([tmp_path / "missing.json"]).values()) == [None]
    # Paths outside the repo are recorded absolute, inside it repo-relative.
    assert list(h1) == [a.resolve().as_posix()]
    assert list(ST.file_hashes([REPO_ROOT / "pyproject.toml"])) == ["pyproject.toml"]


def test_code_hash_patterns(tmp_path):
    (tmp_path / "pkg" / "sub").mkdir(parents=True)
    (tmp_path / "pkg" / "a.py").write_text("a")
    (tmp_path / "pkg" / "sub" / "b.py").write_text("b")
    (tmp_path / "pkg" / "__pycache__").mkdir()
    (tmp_path / "pkg" / "__pycache__" / "a.cpython-311.pyc").write_bytes(b"x")
    (tmp_path / "one.py").write_text("1")
    h = ST.code_hash(["pkg/**", "one.py"], tmp_path)
    assert h == ST.code_hash(["pkg", "one.py"], tmp_path) == ST.code_hash(["one.py", "pkg/**"], tmp_path)
    (tmp_path / "pkg" / "__pycache__" / "a.cpython-311.pyc").write_bytes(b"y")
    assert ST.code_hash(["pkg/**", "one.py"], tmp_path) == h            # caches do not count
    (tmp_path / "pkg" / "sub" / "b.py").write_text("b2")
    assert ST.code_hash(["pkg/**", "one.py"], tmp_path) != h
    assert ST.code_hash(["pkg/*.py"], tmp_path) == ST.code_hash(["pkg/a.py"], tmp_path)
    assert ST.code_hash(["missing.py"], tmp_path) == ST.code_hash([], tmp_path)


def test_reusable_rules(tmp_path):
    (tmp_path / "building_fitted.json").write_text("{}")
    fp = "f" * 64
    ok = rec("fit", "ok", fingerprint=fp, outputs=["building_fitted.json"])
    assert ST.reusable(ok, fp, tmp_path)
    assert ST.reusable(rec("fit", "warning", fingerprint=fp, outputs=["building_fitted.json"]), fp, tmp_path)
    assert ST.reusable(rec("fit", "reused", fingerprint=fp, outputs=["building_fitted.json"]), fp, tmp_path)
    assert not ST.reusable(ok, "e" * 64, tmp_path)                                    # inputs changed
    assert not ST.reusable(rec("fit", "failed", fingerprint=fp, outputs=[]), fp, tmp_path)
    assert not ST.reusable(rec("fit", "incomplete", fingerprint=fp, outputs=[]), fp, tmp_path)
    assert not ST.reusable(None, fp, tmp_path)
    (tmp_path / "building_fitted.json").unlink()
    assert not ST.reusable(ok, fp, tmp_path)                                          # output missing


def test_project_states():
    assert ST.project_state([rec("intake", "skipped"), rec("pipeline", "needs_review"),
                             rec("report", "failed")]) == "needs_review"
    assert ST.project_state([rec("intake", "needs_review")]) == "needs_review"
    assert ST.project_state([rec("pipeline", "ok"), rec("layout", "failed"), rec("render", "incomplete")]) == "failed"
    assert ST.project_state([rec("pipeline", "ok"), rec("polish", "incomplete")]) == "incomplete"
    assert ST.project_state([rec("pipeline", "reused"), rec("assets", "warning"), rec("gate", "skipped")]) == "ok"
    # needs_review of a later stage is not the building's review: a failure.
    assert ST.project_state([rec("pipeline", "ok"), rec("build", "needs_review")]) == "failed"
    assert ST.project_state([]) == "ok"


def test_status_vocabulary():
    assert ST.STATUSES == ("ok", "reused", "warning", "skipped", "failed", "needs_review", "incomplete")
    assert set(ST.SKIP_REASONS) == {"private only", "no style photos", "polish off", "no empty room",
                                    "smoke profile", "gate not validated", "not in this phase"}
    assert ST.worst(["ok", "incomplete", "warning"]) == "incomplete"
    assert ST.worst(["ok", "failed", "incomplete"]) == "failed" and ST.worst([]) is None


def test_git_commit_of_this_checkout():
    sha = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    if sha.returncode != 0:
        pytest.skip("no git checkout")
    assert ST.git_commit(REPO_ROOT) == sha.stdout.strip()


def test_git_commit_layouts(tmp_path):
    sha = "a" * 40
    detached = tmp_path / "d"
    (detached / ".git").mkdir(parents=True)
    (detached / ".git" / "HEAD").write_text(sha + "\n")
    assert ST.git_commit(detached) == sha
    branch = tmp_path / "b"
    (branch / ".git" / "refs" / "heads").mkdir(parents=True)
    (branch / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
    (branch / ".git" / "refs" / "heads" / "main").write_text("b" * 40 + "\n")
    assert ST.git_commit(branch) == "b" * 40
    packed = tmp_path / "p"
    (packed / ".git").mkdir(parents=True)
    (packed / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
    (packed / ".git" / "packed-refs").write_text("# pack-refs\n" + "c" * 40 + " refs/heads/main\n")
    assert ST.git_commit(packed) == "c" * 40
    # A worktree: .git is a file pointing at its gitdir, whose commondir holds the refs.
    common = tmp_path / "main" / ".git"
    (common / "refs" / "heads").mkdir(parents=True)
    (common / "refs" / "heads" / "wt").write_text("d" * 40 + "\n")
    gitdir = common / "worktrees" / "wt"
    gitdir.mkdir(parents=True)
    (gitdir / "HEAD").write_text("ref: refs/heads/wt\n")
    (gitdir / "commondir").write_text("../..\n")
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / ".git").write_text(f"gitdir: {gitdir}\n")
    assert ST.git_commit(wt) == "d" * 40
    assert ST.git_commit(tmp_path / "none") is None
