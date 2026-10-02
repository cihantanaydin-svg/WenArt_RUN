"""Repository guards for private projects (docs/milestone6.md §7.2, docs/intake.md).

The repository is public, so a private project (alias ``real-NN``) and its results must never be
committed. The alias itself is public text by design (job log, run manifest, gpu-log, commit
messages), so these guards look for private *data* in the repository, not for the word:

- every ``results/<area>/<p>/`` folder (areas of ``wenart.run.projects.RESULT_AREAS``) has a
  ``projects/<p>/`` in the repository: a private alias never has one, so an accidental copy of
  private results into ``results/`` fails here before a commit;
- ``git check-ignore`` holds for the three private roots ``projects-private/``, ``results-private/``
  and ``outputs-private/`` at the repo root;
- no file path in the repository has a part named after a private alias (``selftest-02``, the
  synthetic self-test, is the only allowed one);
- no text file outside ``tests/`` points into a private volume folder of a real alias
  (``projects-private/real-01/...``; documentation uses ``<alias>`` or ``$ALIAS``; tests build such
  paths in tmp folders on purpose);
- no file under ``results/`` or ``projects/`` names a private alias, except the job-level
  ``results/run_manifest.json`` (it lists private aliases with their state only, §2.3).

"In the repository" = tracked files plus untracked files that are not ignored
(``git ls-files --cached --others --exclude-standard``), so the guard fires before ``git add``.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest

from wenart.run.projects import ALIAS_RE, RESERVED_ALIASES, RESULT_AREAS

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOTS = ("projects-private", "results-private", "outputs-private")
ALIAS_WORD = re.compile(r"\breal-[0-9]{2,3}\b")
PRIVATE_VOLUME_PATH = re.compile(r"(?:projects|outputs|results)-private/real-[0-9]{2,3}(?![0-9])")
TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml", ".py", ".sh", ".toml", ".csv", ".log", ".xml", ".html",
                 ".cfg", ".ini", ".gitignore", ""}
ALIAS_MENTION_ALLOWED = {"results/run_manifest.json"}

pytestmark = pytest.mark.skipif(shutil.which("git") is None or not (ROOT / ".git").exists(),
                                reason="needs a git checkout")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


@pytest.fixture(scope="module")
def repo_files() -> list[str]:
    out = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted({f for f in out.split("\0") if f and (ROOT / f).exists()})


def result_project_folders(files: list[str]) -> set[tuple[str, str]]:
    """``(area, p)`` of every ``results/<area>/<p>/...`` path (folders only, not files of the area)."""
    out = set()
    for f in files:
        parts = PurePosixPath(f).parts
        if len(parts) >= 4 and parts[0] == "results" and parts[1] in RESULT_AREAS:
            out.add((parts[1], parts[2]))
    return out


def private_alias(name: str) -> bool:
    """True for a private alias other than the reserved self-test aliases."""
    return bool(ALIAS_RE.match(name)) and name not in RESERVED_ALIASES


def test_every_result_folder_has_a_committed_project(repo_files):
    projects = {PurePosixPath(f).parts[1] for f in repo_files
                if f.startswith("projects/") and len(PurePosixPath(f).parts) >= 3}
    folders = result_project_folders(repo_files)
    assert folders, "no results/<area>/<p>/ folder found: is this the repo root?"
    orphans = sorted(f"results/{area}/{p}/" for area, p in folders if p not in projects)
    assert not orphans, (f"result folders without a committed projects/<p>/ (a private project's results must "
                         f"never be in results/; they belong in runs/<job>/results-private/): {orphans}")


def test_result_folder_rule_catches_a_private_copy():
    files = ["projects/synthetic-01/brief.yaml", "results/final/synthetic-01/final_report.md",
             "results/final/real-01/final_report.md", "results/furniture/junit-render.xml",
             "results/realism/realism_summary.json", "results/bakeoff/x/y.json"]
    folders = result_project_folders(files)
    assert folders == {("final", "synthetic-01"), ("final", "real-01")}


@pytest.mark.parametrize("path", [f"{root}/real-01/plan.pdf" for root in PRIVATE_ROOTS]
                         + [f"{root}/" for root in PRIVATE_ROOTS]
                         + ["results-private/real-01/final/final_report.md",
                            "outputs-private/selftest-02/input/selftest-02/plan_scan.png",
                            "results-private/_run_manifest.json"])
def test_private_roots_are_ignored(path):
    rc = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode
    assert rc == 0, (f"{path} is not ignored by .gitignore "
                     "(add /projects-private/, /results-private/, /outputs-private/)")


def test_no_path_is_named_after_a_private_alias(repo_files):
    bad = []
    for f in repo_files:
        for part in PurePosixPath(f).parts:
            if private_alias(part) or private_alias(PurePosixPath(part).stem):
                bad.append(f)
                break
    assert not bad, f"files named after a private alias are in the repository: {bad[:20]}"


def _text_files(files: list[str]):
    for f in files:
        p = ROOT / f
        if PurePosixPath(f).suffix.lower() not in TEXT_SUFFIXES or not p.is_file() or p.is_symlink():
            continue
        try:
            yield f, p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


def test_no_file_points_into_a_private_volume_folder(repo_files):
    scoped = [f for f in repo_files if not f.startswith("tests/")]
    bad = [f"{f}: {m.group(0)}" for f, text in _text_files(scoped) for m in PRIVATE_VOLUME_PATH.finditer(text)]
    assert not bad, f"paths into a private project's volume folder (use <alias> in docs): {bad[:20]}"


def test_results_and_projects_never_name_a_private_alias(repo_files):
    scoped = [f for f in repo_files if f.startswith(("results/", "projects/")) and f not in ALIAS_MENTION_ALLOWED]
    bad = [f"{f}: {m.group(0)}" for f, text in _text_files(scoped) for m in ALIAS_WORD.finditer(text)]
    assert not bad, f"private aliases in committed results or projects: {bad[:20]}"


def test_alias_patterns():
    assert private_alias("real-01") and private_alias("real-123")
    assert not private_alias("selftest-02") and not private_alias("real-1") and not private_alias("synthetic-01")
    assert PRIVATE_VOLUME_PATH.search("/workspace/outputs-private/real-07/building.json")
    assert PRIVATE_VOLUME_PATH.search("s3://h9er811d55/projects-private/real-01/a.pdf")
    assert not PRIVATE_VOLUME_PATH.search("s3://h9er811d55/projects-private/$ALIAS/")
    assert not PRIVATE_VOLUME_PATH.search("/workspace/results-private/selftest-02/final")
    assert not ALIAS_WORD.search("surreal-01") and ALIAS_WORD.search("project real-02 ended needs_review")
