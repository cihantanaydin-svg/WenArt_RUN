"""Shared Milestone 6 contracts (docs/milestone6.md §1): canonical hashes, project refs, repo paths."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from wenart import views
from wenart.blender import cameras
from wenart.canonical import canonical_sha256, strip_volatile
from wenart.run.projects import (ProjectError, ProjectRef, check_alias, private_project, public_project,
                                 upload_dir)


def _write(path: Path, obj) -> Path:
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def test_canonical_hash_ignores_volatile_keys_and_key_order(tmp_path):
    a = _write(tmp_path / "a.json", {"created_utc": "2026-10-01", "rooms": [{"id": "r1", "seconds": 3}], "x": 1})
    b = _write(tmp_path / "b.json", {"x": 1, "rooms": [{"seconds": 9, "id": "r1"}], "created_utc": "2026-10-02"})
    c = _write(tmp_path / "c.json", {"x": 2, "rooms": [{"id": "r1"}]})
    assert canonical_sha256(a) == canonical_sha256(b)
    assert canonical_sha256(a) != canonical_sha256(c)
    assert strip_volatile({"a": [{"latency_s": 1, "k": 2}]}) == {"a": [{"k": 2}]}


def test_canonical_hash_raw_files_folders_and_missing(tmp_path):
    (tmp_path / "d").mkdir()
    f = tmp_path / "d" / "x.txt"
    f.write_bytes(b"abc")
    bad = tmp_path / "d" / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    h1 = canonical_sha256(tmp_path / "d")
    assert canonical_sha256(bad) is not None
    f.write_bytes(b"abd")
    assert canonical_sha256(tmp_path / "d") != h1
    assert canonical_sha256(tmp_path / "missing") is None


def test_public_and_private_project_refs(tmp_path):
    repo = tmp_path / "repo"
    (repo / "projects" / "synthetic-01").mkdir(parents=True)
    pub = public_project("synthetic-01", tmp_path / "results", repo_root=repo)
    assert pub == ProjectRef("synthetic-01", False, repo / "projects" / "synthetic-01",
                             repo / "outputs" / "synthetic-01", tmp_path / "results")
    assert pub.results_area("final") == tmp_path / "results" / "final" / "synthetic-01"
    priv = private_project("real-01", private_root=tmp_path / "pp", outputs_root=tmp_path / "po",
                           results_root=tmp_path / "pr", repo_root=repo)
    assert priv.private and priv.project_dir == tmp_path / "po" / "real-01" / "input"
    assert priv.results_area("check") == tmp_path / "pr" / "real-01" / "check"
    assert upload_dir("real-01", tmp_path / "pp") == tmp_path / "pp" / "real-01"
    with pytest.raises(ProjectError):
        private_project("synthetic-01", repo_root=repo)
    with pytest.raises(ProjectError):
        pub.results_area("secrets")


@pytest.mark.parametrize("alias", ["", "..", ".", "a/b", "../x", "-x", "x" * 65, "a b", "çay"])
def test_bad_aliases_are_refused(alias):
    with pytest.raises(ProjectError):
        check_alias(alias)


def test_repo_path_helpers(tmp_path):
    assert views.resolve_repo_path(None) is None
    assert views.resolve_repo_path("outputs/p/b.json") == views.REPO_ROOT / "outputs/p/b.json"
    assert views.resolve_repo_path(str(tmp_path / "b.json")) == tmp_path / "b.json"
    assert views.repo_path_text(views.REPO_ROOT / "outputs" / "p" / "b.json") == "outputs/p/b.json"
    assert views.repo_path_text(tmp_path / "b.json") == (tmp_path / "b.json").resolve().as_posix()


def test_camera_policy_argument():
    with pytest.raises(ValueError):
        cameras.plan_cameras({"levels": [], "rooms": []}, "L0", policy="nope")
