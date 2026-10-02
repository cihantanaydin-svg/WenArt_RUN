"""Where a project's inputs, outputs and results live (docs/milestone6.md §1.1).

Public projects are committed under ``projects/<p>`` and write ``outputs/<p>``
and the committed results layout ``$RESULTS/<area>/<p>/``. Private projects
(the repo is public) are uploaded by the user to the network volume under
``/workspace/projects-private/<alias>``; they are staged with NFC names into
``/workspace/outputs-private/<alias>/input/<alias>`` (``wenart.intake``; the
folder name is the alias, so the building id is the alias), write
``/workspace/outputs-private/<alias>`` and keep their results in
``/workspace/results-private/<alias>/<area>/``, never in the repo.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_ROOT = Path("/workspace/projects-private")
PRIVATE_OUTPUTS = Path("/workspace/outputs-private")
PRIVATE_RESULTS = Path("/workspace/results-private")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
# Private aliases are public text (job log, run manifest, gpu-log, commits), so they
# are neutral by construction: real-01 ... real-999, plus the synthetic self-test.
ALIAS_RE = re.compile(r"^real-[0-9]{2,3}$")
RESERVED_ALIASES = ("selftest-02",)
# Result areas in the committed layout ($RESULTS/<area>/<p>/ for public projects,
# results-private/<alias>/<area>/ for private ones).
RESULT_AREAS = ("renders", "furniture", "polish", "gate", "check", "final", "run", "realism")


class ProjectError(ValueError):
    """A project name or alias that cannot be used."""


@dataclass(frozen=True)
class ProjectRef:
    name: str            # public project name or private alias
    private: bool
    project_dir: Path    # projects/<p>  |  <outputs-private>/<a>/input/<a> (NFC staged copy)
    out_dir: Path        # outputs/<p>   |  <outputs-private>/<a>
    results_dir: Path    # $RESULTS      |  <results-private>/<a>

    def results_area(self, area: str) -> Path:
        """Folder of one result area: ``$RESULTS/<area>/<p>`` or ``<results-private>/<a>/<area>``."""
        if area not in RESULT_AREAS:
            raise ProjectError(f"unknown result area {area!r}")
        if self.private:
            return self.results_dir / area
        return self.results_dir / area / self.name


def check_name(name: str) -> str:
    """``name`` when it is a safe public project name (one path component), else ``ProjectError``."""
    if not isinstance(name, str) or not NAME_RE.match(name):
        raise ProjectError(f"invalid project name {name!r}: use letters, digits, '.', '_' or '-' "
                           "(max 64 characters, starting with a letter or digit)")
    return name


def check_alias(alias: str) -> str:
    """``alias`` when it is a valid private alias (``real-NN``/``real-NNN`` or a reserved
    self-test alias), else ``ProjectError``. The alias is public text: never a client,
    address or project name (docs/milestone6.md §7.1)."""
    if not isinstance(alias, str) or not (ALIAS_RE.match(alias) or alias in RESERVED_ALIASES):
        raise ProjectError(f"invalid private alias {alias!r}: use real-01, real-02, ... (real- and 2-3 digits)")
    return alias


def public_project(name: str, results: Path, repo_root: Path = REPO_ROOT) -> ProjectRef:
    """A committed project ``projects/<name>``."""
    check_name(name)
    project_dir = Path(repo_root) / "projects" / name
    return ProjectRef(name=name, private=False, project_dir=project_dir,
                      out_dir=Path(repo_root) / "outputs" / name, results_dir=Path(results))


def private_project(alias: str, private_root: Path = PRIVATE_ROOT, outputs_root: Path = PRIVATE_OUTPUTS,
                    results_root: Path = PRIVATE_RESULTS, repo_root: Path = REPO_ROOT) -> ProjectRef:
    """A private upload ``<private_root>/<alias>``; refused when ``projects/<alias>`` exists
    (a private alias must never share a name with a committed project)."""
    check_alias(alias)
    if (Path(repo_root) / "projects" / alias).exists():
        raise ProjectError(f"private alias {alias!r} is also a committed project name; choose another alias")
    out_dir = Path(outputs_root) / alias
    return ProjectRef(name=alias, private=True, project_dir=out_dir / "input" / alias, out_dir=out_dir,
                      results_dir=Path(results_root) / alias)


def upload_dir(alias: str, private_root: Path = PRIVATE_ROOT) -> Path:
    """The user's upload folder of a private project (read only for the pipeline)."""
    return Path(private_root) / check_alias(alias)
