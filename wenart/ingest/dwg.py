"""DWG -> DXF with LibreDWG 0.14 (docs/milestone7.md §5.1).

What: ``convert(dwg, out_dir)`` runs LibreDWG's ``dwg2dxf -y -o <out_dir>/<stem>.dxf <dwg>`` and checks the
result; ``dwg_to_dxf`` is the ``(dxf_path, converter_string)`` form the classifier uses.

Why these rules (measured in the session on 3 Oct 2026, LibreDWG tag ``0.14`` = commit d9468ae, built from git
with cmake/ninja as a static binary; there is no 0.14.1 release):
- ``dwg2dxf`` **without** ``--as`` writes the DXF in the DWG's own version and reproduces LibreDWG's AutoCAD
  reference DXFs; with ``--as r2018`` the model space comes out *empty* while the exit code is 0 and the ezdxf
  audit is clean. So ``--as`` is never passed, and a converted file whose model space holds no entity is a
  ``ConversionError`` (the pipeline then stops that project with ``needs_review``), never an empty plan.
- ``dwg2dxf --version`` prints only the program name, so the version comes from the ``VERSION`` file the setup
  scripts write next to the binaries (``"0.14 d9468ae"``); it goes into the converter string and the pipeline
  fingerprint (``libredwg_version``).
- Every result is read back with ``ezdxf.recover`` (tolerant reader + audit). Audit *errors* are reported with
  the converter string; the pipeline marks that file's elements ``unverified``. Fixes are only counted.
- The per-type entity counts of the model space and the DWG's own ``$ACADVER`` (the 6-byte magic at the start of
  the file, ``AC1015`` = R2000) are returned for ``documents[]``.
- The DXF is written into ``out_dir`` (the pipeline passes ``<out>/converted``), never next to the DWG: a DXF of the
  same stem in the project folder would be read as a document of its own on the next run.
- ezdwg (the earlier fallback) is not used: 0.12.12 could not read the synthetic DWGs.

Where the binaries are looked for, in order: ``$WENART_LIBREDWG_BIN`` (a folder), ``/workspace/tools/libredwg/bin``
(the pod, ``scripts/pod_setup_recognition.sh`` part ``libredwg``), ``~/.cache/wenart/libredwg/bin`` (the cloud
session, ``scripts/cloud-setup.sh``), then ``PATH``. LibreDWG is GPL-3.0: it is called as a separate program and
never shipped with the repository.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ezdxf import recover

LIBREDWG_TAG = "0.14"
LIBREDWG_COMMIT = "d9468ae948b8f07a08efa756c19f8916052358c0"
BIN_ENV = "WENART_LIBREDWG_BIN"
POD_BIN = Path("/workspace/tools/libredwg/bin")
SESSION_BIN = Path("~/.cache/wenart/libredwg/bin")
TOOLS = ("dwg2dxf", "dxf2dwg", "dwgread")
TIMEOUT_S = 600
DXF_ADVICE = "if it fails, export DXF from the CAD program"

# DWG file magic -> AutoCAD release (the first six bytes of every DWG).
ACADVER_RELEASES = {
    "AC1012": "R13", "AC1014": "R14", "AC1015": "R2000", "AC1018": "R2004", "AC1021": "R2007",
    "AC1024": "R2010", "AC1027": "R2013", "AC1032": "R2018",
}


class ConverterNotFound(RuntimeError):
    """LibreDWG ``dwg2dxf`` is not installed in any of the searched places."""


class ConversionError(RuntimeError):
    """``dwg2dxf`` ran but gave no usable DXF (failed, unreadable, or an empty model space)."""


@dataclass
class Conversion:
    """The result of one DWG conversion (what ``documents[]`` and the report record)."""
    dxf_path: Path
    converter: str                         # "libredwg dwg2dxf 0.14 d9468ae; audit: 0 errors, 3 fixes"
    version: str                           # contents of VERSION, "unknown" without one
    acadver: Optional[str]                 # magic of the source DWG, e.g. "AC1015"
    release: Optional[str]                 # "R2000" (None for an unknown magic)
    entity_counts: dict = field(default_factory=dict)   # model space DXF type -> count, sorted by type
    audit_errors: int = 0
    audit_fixes: int = 0
    audit_messages: list = field(default_factory=list)  # first audit error messages

    def to_json(self) -> dict:
        return {"converter": self.converter, "libredwg_version": self.version, "acadver": self.acadver,
                "release": self.release, "entity_counts": dict(self.entity_counts),
                "audit": {"errors": self.audit_errors, "fixes": self.audit_fixes,
                          "messages": list(self.audit_messages)}}


# --------------------------------------------------------------------------
# Finding the binaries
# --------------------------------------------------------------------------

def search_dirs() -> list[Path]:
    """Folders searched for the LibreDWG programs, in order (``PATH`` comes after these)."""
    dirs = []
    env = os.environ.get(BIN_ENV)
    if env:
        dirs.append(Path(env).expanduser())
    dirs.append(POD_BIN)
    dirs.append(SESSION_BIN.expanduser())
    return dirs


def find_tool(name: str) -> Optional[Path]:
    """Path of a LibreDWG program (``dwg2dxf``, ``dxf2dwg``, ``dwgread``) or None."""
    for folder in search_dirs():
        candidate = folder / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    found = shutil.which(name)
    return Path(found) if found else None


def available_converters() -> list[str]:
    """``["dwg2dxf"]`` when LibreDWG's converter is found, else ``[]``."""
    return ["dwg2dxf"] if find_tool("dwg2dxf") else []


def libredwg_version(tool: Optional[Path] = None) -> Optional[str]:
    """The ``VERSION`` string of the LibreDWG install that ``tool`` (default: the found ``dwg2dxf``) belongs to:
    ``<bin>/VERSION``, else ``<bin>/../VERSION`` (older pod layout). ``"unknown"`` for a binary without one (e.g. a
    distribution package on ``PATH``), None when no binary is found. Part of the pipeline fingerprint."""
    tool = tool or find_tool("dwg2dxf")
    if tool is None:
        return None
    for candidate in (tool.parent / "VERSION", tool.parent.parent / "VERSION"):
        try:
            text = candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            return text.splitlines()[0].strip()
    return "unknown"


def dwg_magic(path: str | Path) -> Optional[str]:
    """The ``$ACADVER`` a DWG states in its first six bytes (``AC1015``), None when it is not a DWG magic."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(6)
    except OSError:
        return None
    try:
        text = head.decode("ascii")
    except UnicodeDecodeError:
        return None
    return text if text.startswith("AC") and text[2:].isdigit() else None


# --------------------------------------------------------------------------
# Conversion
# --------------------------------------------------------------------------

def _not_found_message(dwg_path: Path) -> str:
    places = ", ".join([f"${BIN_ENV}"] + [str(p) for p in (POD_BIN, SESSION_BIN)] + ["PATH"])
    return (f"cannot convert {dwg_path.name}: LibreDWG dwg2dxf not found (looked in {places}). The pod builds it "
            f"with scripts/pod_setup_recognition.sh (part libredwg), the cloud session with scripts/cloud-setup.sh; "
            f"or export DXF from the CAD program")


def convert(path: str | Path, out_dir: Optional[str | Path]) -> Conversion:
    """Convert one DWG into ``out_dir/<stem>.dxf`` and check it (see the module docstring).

    Raises ``FileNotFoundError`` (no such DWG), ``ConverterNotFound`` (no ``dwg2dxf``) or ``ConversionError``
    (no output folder, the converter failed, the DXF is unreadable, or its model space is empty)."""
    dwg_path = Path(path)
    if not dwg_path.is_file():
        raise FileNotFoundError(dwg_path)
    if out_dir is None:
        raise ConversionError(f"{dwg_path.name}: no output folder given (a DWG is never converted into the project "
                              "folder)")
    tool = find_tool("dwg2dxf") if available_converters() else None
    if tool is None:
        raise ConverterNotFound(_not_found_message(dwg_path))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dxf_path = out_dir / (dwg_path.stem + ".dxf")
    if dxf_path.exists():
        dxf_path.unlink()                      # a stale DXF of an earlier run must never pass as this run's result
    version = libredwg_version(tool) or "unknown"
    name = f"libredwg dwg2dxf {version}"
    try:
        result = subprocess.run([str(tool), "-y", "-o", str(dxf_path), str(dwg_path)], capture_output=True,
                                text=True, errors="replace", timeout=TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ConversionError(f"{name}: could not run on {dwg_path.name}: {exc}") from exc
    if result.returncode != 0 or not dxf_path.is_file():
        tail = (result.stderr or result.stdout or "").strip()[-500:]
        raise ConversionError(f"{name} failed on {dwg_path.name} (exit {result.returncode}): {tail}; {DXF_ADVICE}")
    try:
        doc, auditor = recover.readfile(str(dxf_path))
    except Exception as exc:  # noqa: BLE001 - ezdxf raises several types for broken files
        raise ConversionError(f"{name}: the DXF written for {dwg_path.name} is not readable by ezdxf: {exc}; "
                              f"{DXF_ADVICE}") from exc
    counts = Counter(entity.dxftype() for entity in doc.modelspace())
    if not counts:
        raise ConversionError(f"{name}: the model space of {dwg_path.name} is empty after the conversion "
                              f"(LibreDWG 0.14 is beta); {DXF_ADVICE}")
    errors = list(auditor.errors)
    audit = f"audit: {len(errors)} errors, {len(auditor.fixes)} fixes"
    messages = [str(e.message) for e in errors[:5]]
    if messages:
        audit += f" ({'; '.join(messages)})"
    magic = dwg_magic(dwg_path)
    return Conversion(dxf_path=dxf_path, converter=f"{name}; {audit}", version=version, acadver=magic,
                      release=ACADVER_RELEASES.get(magic or ""), entity_counts=dict(sorted(counts.items())),
                      audit_errors=len(errors), audit_fixes=len(auditor.fixes), audit_messages=messages)


def dwg_to_dxf(path: str | Path, out_dir: Optional[str | Path]) -> tuple[Path, str]:
    """``(dxf_path, converter_string)`` of ``convert`` (the classifier's interface)."""
    conversion = convert(path, out_dir)
    return conversion.dxf_path, conversion.converter


def dxf_to_dwg(dxf_path: str | Path, dwg_path: str | Path, version: str = "r2000") -> Path:
    """Write a DWG from a DXF with LibreDWG ``dxf2dwg --as <version>`` (synthetic-06 and tests only; the pipeline
    never writes DWGs). Raises ``ConverterNotFound`` or ``ConversionError``."""
    tool = find_tool("dxf2dwg")
    if tool is None:
        raise ConverterNotFound(f"LibreDWG dxf2dwg not found (looked in {', '.join(map(str, search_dirs()))}, PATH)")
    dwg_path = Path(dwg_path)
    dwg_path.parent.mkdir(parents=True, exist_ok=True)
    if dwg_path.exists():
        dwg_path.unlink()
    result = subprocess.run([str(tool), "-y", "--as", version, "-o", str(dwg_path), str(dxf_path)],
                            capture_output=True, text=True, errors="replace", timeout=TIMEOUT_S)
    if result.returncode != 0 or not dwg_path.is_file():
        tail = (result.stderr or result.stdout or "").strip()[-500:]
        raise ConversionError(f"dxf2dwg failed on {Path(dxf_path).name} (exit {result.returncode}): {tail}")
    return dwg_path
