#!/usr/bin/env python3
"""Turn files the user dropped somewhere into a committed project ``projects/<name>/`` (docs/intake.md).

What: ``python scripts/add_project.py <name> <file or folder or .zip> [...] [--style "..."] [--replace]``

Why: the easy path for a real project whose privacy does not matter. The user drops the files into the
project chat (they land under ``/mnt/project-files/uploads/``, often named by an id with no extension)
or uploads them with GitHub's web page; Claude runs this script, commits ``projects/<name>/`` and runs
it like the synthetic projects (``RUN_PROJECTS=<name>``). No S3 key, no AWS tool, no volume upload.

How:
- every source is copied into a scratch folder: a folder keeps its layout, a ``.zip`` (also one without
  the suffix) is unpacked (unsafe member paths are skipped), a file without a known suffix gets one from
  its first bytes (PDF, DXF, DWG, PNG, JPEG, TIFF);
- the scratch folder goes through the same rules as the private intake (``wenart.intake.walk_upload``):
  junk and unused file types skipped, NFC names, subfolder plans moved to the top level as
  ``<folder>__<name>``, a DWG next to a DXF skipped, name collisions and caps refused;
- the kept files are written to ``projects/<name>/``; ``--style`` writes ``brief.yaml`` (``style: ...``)
  when the files hold none. Without a brief every value is the default (``wenart/defaults.yaml``).

Exit codes: 0 written; 4 nothing written (no document, collision, cap, bad name); 2 refused request
(bad name, a private alias such as ``real-01``, the project exists without ``--replace``); 1 other error.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wenart import intake as I  # noqa: E402
from wenart.run.projects import ALIAS_RE, ProjectError, check_name  # noqa: E402

KNOWN_SUFFIXES = set(I.ALLOWED_SUFFIXES) | {".zip"}
EXIT_OK, EXIT_ERROR, EXIT_REFUSED, EXIT_NEEDS_REVIEW = 0, 1, 2, 4


class Refused(ValueError):
    """A request this script refuses (exit 2)."""


def sniff_suffix(path: Path) -> str | None:
    """The suffix that the first bytes of ``path`` show, or None when unknown."""
    with open(path, "rb") as f:
        head = f.read(4096)
    if head.startswith(b"%PDF"):
        return ".pdf"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head.startswith((b"II*\x00", b"MM\x00*")):
        return ".tif"
    if head.startswith(b"AC10"):
        return ".dwg"
    if head.startswith(b"PK\x03\x04"):
        return ".zip"
    if head.startswith(b"AutoCAD Binary DXF"):
        return ".dxf"
    lines = [ln.strip() for ln in head.decode("latin-1").splitlines()[:4]]
    if len(lines) >= 2 and lines[0] == "0" and lines[1] == "SECTION":
        return ".dxf"
    return None


def safe_member(name: str) -> PurePosixPath | None:
    """A zip member path that stays inside the target folder, else None."""
    p = PurePosixPath(name.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or not p.parts:
        return None
    return p


def unpack_zip(src: Path, dest: Path) -> list[str]:
    """Unpack ``src`` into ``dest``; returns the skipped member names (unsafe paths, links)."""
    skipped = []
    with zipfile.ZipFile(src) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            rel = safe_member(info.filename)
            if rel is None or (info.external_attr >> 16) & 0o170000 == 0o120000:
                skipped.append(info.filename)
                continue
            target = dest.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as fin, open(target, "wb") as fout:
                shutil.copyfileobj(fin, fout)
    return skipped


def gather(sources: list[Path], scratch: Path) -> list[str]:
    """Copy every source into ``scratch`` (see the module docstring); returns notes for the user."""
    notes = []
    for src in sources:
        if src.is_symlink():
            raise Refused(f"{src} is a symbolic link")
        if src.is_dir():
            shutil.copytree(src, scratch / src.name if len(sources) > 1 else scratch, dirs_exist_ok=True,
                            symlinks=True)
            continue
        if not src.is_file():
            raise Refused(f"{src} does not exist")
        suffix = src.suffix.lower()
        if suffix not in KNOWN_SUFFIXES:
            sniffed = sniff_suffix(src)
            if sniffed:
                notes.append(f"{src.name}: no known suffix, read as {sniffed}")
                suffix = sniffed
        if suffix == ".zip":
            for name in unpack_zip(src, scratch):
                notes.append(f"{src.name}: zip member skipped (unsafe path or link): {name}")
            continue
        name = src.name if src.suffix.lower() == suffix else src.name + suffix
        shutil.copy2(src, scratch / name)
    return notes


def add_project(name: str, sources: list[Path], projects: Path, style: str | None = None,
                replace: bool = False) -> tuple[int, list[str]]:
    """Write ``projects/<name>/`` from ``sources``; returns (exit code, report lines)."""
    try:
        check_name(name)
    except ProjectError as exc:
        raise Refused(str(exc)) from exc
    if ALIAS_RE.match(name):
        raise Refused(f"{name!r} is a private alias name (real-NN); use for example {name.replace('-', '')!r}")
    target = projects / name
    if target.exists() and not replace:
        raise Refused(f"{target} exists; add --replace to rebuild it")
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "in"
        scratch.mkdir()
        report += gather(sources, scratch)
        entries = I.walk_upload(scratch)
        reasons = I.review_reasons(entries)
        for e in entries:
            if not e.kept:
                report.append(f"skipped {e.path}: {e.reason}")
            elif e.note:
                report.append(f"note {e.path}: {e.note}")
        if reasons:
            report.append("nothing written: " + "; ".join(reasons))
            return EXIT_NEEDS_REVIEW, report
        build = projects / (name + ".tmp")
        if build.exists():
            shutil.rmtree(build)
        build.mkdir(parents=True)
        for e in entries:
            if e.kept:
                (build / e.staged).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(e.source, build / e.staged)
                report.append(f"kept {e.staged} ({e.size} bytes)")
        brief = build / I.BRIEF_NAME
        if style and not brief.exists():
            import yaml
            brief.write_text(yaml.safe_dump({"style": style}, allow_unicode=True, sort_keys=False), encoding="utf-8")
            report.append(f"wrote {I.BRIEF_NAME} (style: {style})")
        elif not brief.exists():
            report.append(f"no {I.BRIEF_NAME}: every brief value is the default (wenart/defaults.yaml)")
        if target.exists():
            shutil.rmtree(target)
        build.rename(target)
    docs = sum(1 for e in entries if e.kept and e.document)
    report.append(f"project {name}: {docs} documents -> {target}")
    return EXIT_OK, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("name", help="project name, e.g. real01 (not real-01: that form is for private uploads)")
    ap.add_argument("sources", nargs="+", type=Path, help="files, folders or .zip files")
    ap.add_argument("--style", help="style text for brief.yaml when the files hold no brief.yaml")
    ap.add_argument("--replace", action="store_true", help="rebuild projects/<name> when it exists")
    ap.add_argument("--projects", type=Path, default=ROOT / "projects", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    try:
        code, report = add_project(a.name, a.sources, a.projects, a.style, a.replace)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return EXIT_REFUSED
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print("\n".join(report))
    return code


if __name__ == "__main__":
    sys.exit(main())
