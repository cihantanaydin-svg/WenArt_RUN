"""Stage a private project upload for the pipeline (docs/milestone6.md §7.1).

What: ``python -m wenart.intake stage <alias> --out <out_dir>/input/<alias> [--root /workspace/projects-private]``
copies the user's upload ``<root>/<alias>/`` (sent by the user with the RunPod S3 API, see
``docs/intake.md``) into a clean staged folder that the ingest pipeline reads, and writes
``<out_dir>/intake_manifest.json`` (``--manifest`` overrides the place).

Why: the upload is the user's raw folder. It can hold macOS and Windows metadata, decomposed (NFD)
Turkish file names written by macOS, plans in subfolders (the pipeline reads the top level only,
``wenart.ingest.classify.project_documents``) and file types the pipeline never reads. The staged copy
is derived data and is rebuilt on every run (staged into ``<out>.tmp/``, then swapped in), so a file the
user removed from the upload is never read again. The upload itself is never modified or deleted.

How, per file of the upload (sorted, symlinks never followed):

- junk (``.DS_Store``, ``Thumbs.db``, ``desktop.ini``, ``._*``, everything under ``__MACOSX/``),
  hidden files and folders, symlinks (refused, never followed), special files and file types outside
  ``ALLOWED_SUFFIXES`` are skipped and listed with the reason;
- every path part is NFC-normalised (``unicodedata.normalize("NFC", ...)``);
- a file in a subfolder is staged at the top level as ``<subfolder>__<name>`` (nested folders:
  ``a__b__name``), because the pipeline reads the top level only; ``style_photos/`` keeps its folder
  and holds images only (a nested folder inside it is flattened the same way);
- a DWG is not read by the pipeline (no converter on the pod; users export DXF): a DWG next to a DXF of
  the same stem is skipped ("the DXF of the same name is used"); a DWG alone is staged with the note
  ``DWG is not read; export DXF from the CAD program`` (the pipeline then says ``needs_review``);
- a ``brief.yaml`` that is not at the top level, or a top-level brief with another spelling
  (``Brief.yaml``, ``brief.yml``), is staged with a note: only ``<top>/brief.yaml`` is read.

The project ends ``needs_review`` (nothing is staged and an old staged copy is removed) when the
upload folder does not exist (``not uploaded``), is a symlink, holds no document (``.pdf .dxf .dwg``
or an image outside ``style_photos/``), when two files map to the same staged name, also when they
differ only in letter case (``document name collision``), when a file of an allowed type is over the
per-file cap (500 MB), cannot be read or has a name that cannot be staged (control characters, not
UTF-8, longer than 255 bytes), or when the kept files are over the project cap (2 GB).

``intake_manifest.json``: ``{schema_version, kind: "intake_manifest", alias, status: ok|needs_review,
reasons, upload, staged, caps, totals, skipped_by_reason, files: [{path, path_nfc, staged, size,
sha256, kept, reason, note}], warnings, created_utc, seconds}``; ``path`` is the original relative path
as found (it may be NFD), ``staged`` the path in the staged folder (null when skipped), ``sha256`` the
copied bytes (null when skipped).

Exit codes (the orchestrator maps them to the stage record, §1.2): 0 staged (``ok``); 4 ``needs_review``
(the reason is printed as ``INTAKE <alias> needs_review: <reason>`` and listed in the manifest's
``reasons``; the manifest is written); 2 refused request (invalid alias, an alias that is also a
committed project, an ``--out`` whose last part is not the alias or that overlaps the upload); 1 any
other error. Nothing printed names a file of the upload (the alias is public; file names are not):
stdout carries only the alias, counts and reasons.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import stat
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart.run.projects import PRIVATE_ROOT, REPO_ROOT, ProjectError, private_project

ALLOWED_SUFFIXES = (".pdf", ".dxf", ".dwg", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".yaml", ".yml",
                    ".txt", ".md")
DOCUMENT_SUFFIXES = (".pdf", ".dxf", ".dwg", ".jpg", ".jpeg", ".png", ".tif", ".tiff")
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
JUNK_NAMES = (".ds_store", "thumbs.db", "desktop.ini")
JUNK_DIRS = ("__macosx",)
STYLE_DIR = "style_photos"
BRIEF_NAME = "brief.yaml"
SUBFOLDER_SEP = "__"
FILE_CAP_BYTES = 500_000_000
PROJECT_CAP_BYTES = 2_000_000_000
NAME_MAX_BYTES = 255
DWG_NOTE = "DWG is not read; export DXF from the CAD program"
EXIT_OK, EXIT_ERROR, EXIT_REFUSED, EXIT_NEEDS_REVIEW = 0, 1, 2, 4

# Reasons of a needs_review intake (public text: never a file name).
NOT_UPLOADED = "not uploaded"
ROOT_SYMLINK = "upload folder is a symlink (refused)"
NO_DOCUMENT = "no document in the upload (only skipped files)"
COLLISION = "document name collision"
OVER_FILE_CAP = f"a file is over the {FILE_CAP_BYTES // 1_000_000} MB per-file cap"
OVER_PROJECT_CAP = f"upload over the {PROJECT_CAP_BYTES // 1_000_000_000} GB project cap"
UNREADABLE = "a file could not be read"
BAD_NAME = "a file name cannot be staged (control characters, not UTF-8 or too long)"


class IntakeRefused(ValueError):
    """A request the intake refuses (exit 2): invalid alias, committed project name, unsafe --out."""


@dataclass
class Entry:
    """One file (or refused link / special file) of the upload."""
    path: str                       # original relative POSIX path as found (may be NFD)
    path_nfc: str
    size: Optional[int]
    kept: bool = False
    staged: Optional[str] = None    # relative POSIX path in the staged folder
    sha256: Optional[str] = None
    reason: Optional[str] = None    # why it was skipped
    note: Optional[str] = None
    source: Optional[Path] = None   # absolute path (not serialised)
    document: bool = False
    blocking: Optional[str] = None  # "cap" | "name": a file of an allowed type that cannot be staged

    def to_json(self) -> dict:
        return {"path": self.path, "path_nfc": self.path_nfc, "staged": self.staged, "size": self.size,
                "sha256": self.sha256, "kept": self.kept, "reason": self.reason, "note": self.note}


@dataclass
class Intake:
    """The result of one intake: status, reasons and the per-file entries."""
    alias: str
    upload: Path
    out: Path
    manifest_path: Path
    status: str = "ok"
    reasons: list = field(default_factory=list)
    entries: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def review(self, reason: str) -> None:
        self.status = "needs_review"
        if reason not in self.reasons:
            self.reasons.append(reason)


# --------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------

def nfc(text: str) -> str:
    """NFC form of a name (macOS writes decomposed NFD names: ``İ`` -> ``I`` + U+0307)."""
    return unicodedata.normalize("NFC", text)


def printable_path(rel: str) -> str:
    """A relative path that can be written to JSON: a name that is not UTF-8 keeps its bytes as ``\\x..``."""
    try:
        rel.encode("utf-8")
        return rel
    except UnicodeEncodeError:
        return os.fsencode(rel).decode("utf-8", "backslashreplace")


def name_problem(parts: list[str]) -> Optional[str]:
    """Why a path cannot be staged (None when it can): not UTF-8 or control characters."""
    for part in parts:
        try:
            part.encode("utf-8")
        except UnicodeEncodeError:
            return "file name is not UTF-8"
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in part):
            return "file name has control characters"
    return None


def is_junk(name: str) -> bool:
    low = nfc(name).casefold()
    return low in JUNK_NAMES or low.startswith("._")


def staged_path(parts_nfc: list[str]) -> str:
    """Where a file of the upload goes in the staged folder (relative POSIX path).

    ``a.pdf`` -> ``a.pdf``; ``plans/a.pdf`` -> ``plans__a.pdf``; ``x/y/a.pdf`` -> ``x__y__a.pdf``;
    ``style_photos/p.jpg`` -> ``style_photos/p.jpg``; ``style_photos/s/p.jpg`` -> ``style_photos/s__p.jpg``.
    """
    if len(parts_nfc) > 1 and parts_nfc[0] == STYLE_DIR:
        return f"{STYLE_DIR}/" + SUBFOLDER_SEP.join(parts_nfc[1:])
    return SUBFOLDER_SEP.join(parts_nfc)


def _sha256_copy(src: Path, dst: Path) -> str:
    """Copy ``src`` to ``dst`` and return the sha256 of the copied bytes."""
    h = hashlib.sha256()
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        for chunk in iter(lambda: fin.read(1 << 20), b""):
            h.update(chunk)
            fout.write(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Walk and decide
# --------------------------------------------------------------------------

def walk_upload(upload: Path, file_cap: int = FILE_CAP_BYTES) -> list[Entry]:
    """Every file of the upload as an ``Entry`` with its keep/skip decision (no copy yet).

    Symlinks (to files or folders) are refused and never followed; junk and hidden folders are not
    staged (their files are listed as skipped).
    """
    entries: list[Entry] = []
    upload = Path(upload)
    for dirpath, dirnames, filenames in os.walk(upload, followlinks=False):
        here = Path(dirpath)
        rel_dir = here.relative_to(upload)
        dir_parts = [] if str(rel_dir) == "." else list(rel_dir.parts)
        in_junk = any(nfc(p).casefold() in JUNK_DIRS for p in dir_parts)
        in_hidden = any(p.startswith(".") for p in dir_parts)
        dirnames.sort()
        for d in list(dirnames):
            full = here / d
            if full.is_symlink():
                dirnames.remove(d)
                entries.append(_entry(dir_parts + [d], full, reason="symlink (refused, not followed)"))
        for name in sorted(filenames):
            full = here / name
            parts = dir_parts + [name]
            if full.is_symlink():
                entries.append(_entry(parts, full, reason="symlink (refused, not followed)"))
                continue
            try:
                st = full.lstat()
            except OSError:
                entries.append(_entry(parts, full, reason="cannot read file information"))
                continue
            if not stat.S_ISREG(st.st_mode):
                entries.append(_entry(parts, full, size=st.st_size, reason="not a regular file"))
                continue
            if in_junk:
                entries.append(_entry(parts, full, size=st.st_size, reason="junk (__MACOSX folder)"))
            elif is_junk(name):
                entries.append(_entry(parts, full, size=st.st_size, reason="junk (system metadata file)"))
            elif in_hidden:
                entries.append(_entry(parts, full, size=st.st_size, reason="hidden folder"))
            elif name.startswith("."):
                entries.append(_entry(parts, full, size=st.st_size, reason="hidden file"))
            else:
                entries.append(_decide(parts, full, st.st_size, file_cap))
    entries.sort(key=lambda e: e.path)
    _dwg_rule(entries)
    return entries


def _entry(parts: list[str], full: Path, size: Optional[int] = None, reason: Optional[str] = None) -> Entry:
    rel = printable_path("/".join(parts))
    if size is None:
        try:
            size = full.lstat().st_size
        except OSError:
            size = None
    return Entry(path=rel, path_nfc=nfc(rel), size=size, kept=False, reason=reason, source=full)


def _decide(parts: list[str], full: Path, size: int, file_cap: int = FILE_CAP_BYTES) -> Entry:
    """Keep/skip decision for a regular, visible, non-junk file."""
    entry = _entry(parts, full, size=size)
    suffix = Path(parts[-1]).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        entry.reason = f"file type not used ({suffix or 'no suffix'})"
        return entry
    parts_nfc = [nfc(p) for p in parts]
    in_style = len(parts_nfc) > 1 and parts_nfc[0] == STYLE_DIR
    if in_style and suffix not in IMAGE_SUFFIXES:
        entry.reason = "not an image (style_photos/ holds photos only)"
        return entry
    entry.document = (not in_style) and suffix in DOCUMENT_SUFFIXES
    bad = name_problem(parts)
    if bad:
        entry.reason, entry.blocking = bad, "name"
        return entry
    staged = staged_path(parts_nfc)
    if any(len(p.encode("utf-8")) > NAME_MAX_BYTES for p in staged.split("/")):
        entry.reason, entry.blocking = f"staged name longer than {NAME_MAX_BYTES} bytes", "name"
        return entry
    if size > file_cap:
        entry.reason, entry.blocking = f"over the per-file cap ({file_cap} bytes)", "cap"
        return entry
    entry.kept = True
    entry.staged = staged
    low = parts_nfc[-1].casefold()
    if low in ("brief.yaml", "brief.yml") and not (len(parts_nfc) == 1 and parts_nfc[0] == BRIEF_NAME):
        entry.note = (f"not read: the brief must be {BRIEF_NAME} at the top level of the folder")
    return entry


def _dwg_rule(entries: list[Entry]) -> None:
    """A DWG next to a DXF of the same stem is skipped; a DWG alone gets the DWG note."""
    dxf_stems = set()
    for e in entries:
        if e.kept and e.path_nfc.lower().endswith(".dxf"):
            p = Path(e.path_nfc)
            dxf_stems.add((p.parent.as_posix(), p.stem.casefold()))
    for e in entries:
        if not (e.kept and e.path_nfc.lower().endswith(".dwg")):
            continue
        p = Path(e.path_nfc)
        if (p.parent.as_posix(), p.stem.casefold()) in dxf_stems:
            e.kept, e.staged, e.document = False, None, False
            e.reason = "DWG not read: the DXF of the same name is used"
        else:
            e.note = DWG_NOTE


def review_reasons(entries: list[Entry], project_cap: int = PROJECT_CAP_BYTES) -> list[str]:
    """``needs_review`` reasons that follow from the entries alone (order fixed)."""
    reasons = []
    if any(e.blocking == "cap" for e in entries):
        reasons.append(OVER_FILE_CAP)
    if any(e.blocking == "name" for e in entries):
        reasons.append(BAD_NAME)
    by_name: dict[str, list[Entry]] = {}
    for e in entries:
        if e.kept:
            by_name.setdefault(e.staged.casefold(), []).append(e)
    for group in by_name.values():
        if len(group) > 1:
            if COLLISION not in reasons:
                reasons.append(COLLISION)
            for e in group:
                e.note = (e.note + "; " if e.note else "") + "name collision"
    if not any(e.kept and e.document for e in entries):
        reasons.append(NO_DOCUMENT)
    total = sum(e.size or 0 for e in entries if e.kept)
    if total > project_cap:
        reasons.append(OVER_PROJECT_CAP)
    return reasons


# --------------------------------------------------------------------------
# Stage
# --------------------------------------------------------------------------

def manifest_path_for(out: Path) -> Path:
    """``<out_dir>/intake_manifest.json`` for ``--out <out_dir>/input/<alias>`` (else next to ``--out``)."""
    out = Path(out)
    return out.parent.parent / "intake_manifest.json" if out.parent.name == "input" else \
        out.parent / "intake_manifest.json"


def _inside(a: Path, b: Path) -> bool:
    """True when ``a`` is ``b`` or inside it (both resolved)."""
    try:
        a.relative_to(b)
        return True
    except ValueError:
        return False


def check_request(alias: str, out: Path, upload: Path, repo_root: Path) -> None:
    """Raise ``IntakeRefused`` for a request that must not run (see the module docstring)."""
    try:
        private_project(alias, repo_root=repo_root)
    except ProjectError as exc:
        raise IntakeRefused(str(exc)) from None
    if Path(out).name != alias:
        raise IntakeRefused(f"--out must end with the alias ({alias}): the folder name becomes the building id")
    ro, ru = Path(out).resolve(), Path(upload).resolve()
    if _inside(ro, ru) or _inside(ru, ro):
        raise IntakeRefused("--out and the upload folder overlap; the upload is never modified")


def _remove_tree(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def stage_project(alias: str, out, root=PRIVATE_ROOT, repo_root=REPO_ROOT, manifest=None,
                  file_cap: int = FILE_CAP_BYTES, project_cap: int = PROJECT_CAP_BYTES) -> Intake:
    """Stage ``<root>/<alias>`` into ``out`` and write the manifest; returns the ``Intake``.

    Raises ``IntakeRefused`` for a refused request. ``file_cap``/``project_cap`` exist for tests.
    """
    start = time.time()
    out = Path(out)
    upload = Path(root) / alias
    check_request(alias, out, upload, Path(repo_root))
    manifest_path = Path(manifest) if manifest else manifest_path_for(out)
    intake = Intake(alias=alias, upload=upload, out=out, manifest_path=manifest_path)
    if upload.is_symlink():
        intake.review(ROOT_SYMLINK)
    elif not upload.is_dir():
        intake.review(NOT_UPLOADED)
    else:
        intake.entries = walk_upload(upload, file_cap)
        for reason in review_reasons(intake.entries, project_cap):
            intake.review(reason)
    tmp = out.with_name(out.name + ".tmp")
    old = out.with_name(out.name + ".old")
    for p in (tmp, old):
        if p.exists() or p.is_symlink():
            _remove_tree(p)
    if intake.status == "ok":
        tmp.mkdir(parents=True)
        for e in intake.entries:
            if not e.kept:
                continue
            try:
                e.sha256 = _sha256_copy(e.source, tmp / e.staged)
            except OSError:
                e.kept, e.staged = False, None
                e.reason = "could not be read"
                intake.review(UNREADABLE)
                break
    if intake.status == "ok":
        if out.is_dir() and not out.is_symlink():
            out.rename(old)
        elif out.exists() or out.is_symlink():
            _remove_tree(out)
        tmp.rename(out)
        if old.exists():
            _remove_tree(old)
    else:
        # Nothing is staged for a project that needs review: an older staged copy must never be read.
        for p in (tmp, out):
            if p.exists() or p.is_symlink():
                _remove_tree(p)
        for e in intake.entries:
            e.sha256 = None
    write_manifest(intake, seconds=time.time() - start, caps=(file_cap, project_cap))
    return intake


def totals(intake: Intake) -> dict:
    kept = [e for e in intake.entries if e.kept]
    return {"files": len(intake.entries), "kept": len(kept), "skipped": len(intake.entries) - len(kept),
            "kept_bytes": sum(e.size or 0 for e in kept),
            "documents": sum(1 for e in kept if e.document),
            "style_photos": sum(1 for e in kept if (e.staged or "").startswith(STYLE_DIR + "/")),
            "notes": sum(1 for e in intake.entries if e.note),
            "blocking": sum(1 for e in intake.entries if e.blocking)}


def skipped_by_reason(intake: Intake) -> dict:
    out: dict[str, int] = {}
    for e in intake.entries:
        if not e.kept:
            out[e.reason or "?"] = out.get(e.reason or "?", 0) + 1
    return dict(sorted(out.items()))


def write_manifest(intake: Intake, seconds: float = 0.0, caps=(FILE_CAP_BYTES, PROJECT_CAP_BYTES)) -> Path:
    """Write ``intake_manifest.json`` (see the module docstring); a needs_review intake stages nothing,
    so its files carry ``staged: null`` and ``would_stage_as``."""
    staged = intake.status == "ok"
    data = {
        "schema_version": "0.1",
        "kind": "intake_manifest",
        "alias": intake.alias,
        "status": intake.status,
        "reasons": list(intake.reasons),
        "upload": Path(intake.upload).as_posix(),
        "staged": Path(intake.out).as_posix() if staged else None,
        "caps": {"file_bytes": caps[0], "project_bytes": caps[1]},
        "allowed_suffixes": list(ALLOWED_SUFFIXES),
        "totals": totals(intake),
        "skipped_by_reason": skipped_by_reason(intake),
        "files": [e.to_json() if staged or not e.kept else {**e.to_json(), "staged": None,
                                                               "would_stage_as": e.staged}
                  for e in intake.entries],
        "warnings": list(intake.warnings),
        "created_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": round(seconds, 2),
    }
    path = intake.manifest_path
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def summary_line(intake: Intake) -> str:
    """One line for stdout: alias, status, counts and reasons; never a file name."""
    t = totals(intake)
    counts = (f"{t['kept']} kept ({t['documents']} documents, {t['style_photos']} style photos), "
              f"{t['skipped']} skipped, {t['notes']} with notes")
    if intake.status == "ok":
        return f"INTAKE {intake.alias} ok: {counts} -> {intake.manifest_path}"
    return f"INTAKE {intake.alias} needs_review: {'; '.join(intake.reasons)} ({counts}) -> {intake.manifest_path}"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.intake",
                                     description="stage a private project upload for the pipeline (§7.1)")
    sub = parser.add_subparsers(dest="command", required=True)
    st = sub.add_parser("stage", help="copy <root>/<alias> into --out (NFC names, junk skipped, rebuilt)")
    st.add_argument("alias", help="private alias: real-01, real-02, ... (or the self-test alias selftest-02)")
    st.add_argument("--out", required=True, help="staged folder, <out_dir>/input/<alias>")
    st.add_argument("--root", default=str(PRIVATE_ROOT), help=f"upload root (default {PRIVATE_ROOT})")
    st.add_argument("--manifest", default=None,
                    help="intake_manifest.json path (default <out_dir>/intake_manifest.json)")
    args = parser.parse_args(argv)
    try:
        intake = stage_project(args.alias, Path(args.out), root=Path(args.root), manifest=args.manifest)
    except IntakeRefused as exc:
        print(f"INTAKE refused: {exc}", file=sys.stderr)
        return EXIT_REFUSED
    except OSError as exc:
        print(f"INTAKE {args.alias} error: {type(exc).__name__}", file=sys.stderr)
        return EXIT_ERROR
    print(summary_line(intake))
    return EXIT_OK if intake.status == "ok" else EXIT_NEEDS_REVIEW


if __name__ == "__main__":
    raise SystemExit(main())
