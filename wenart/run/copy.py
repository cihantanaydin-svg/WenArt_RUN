"""Copy the small result files of a full run into the results layout (docs/milestone6.md §2.1).

What: ``python -m wenart.run copy --projects ... [--private ...] [--ab ...]
--results $RESULTS [--since STAMP]`` copies, per project, the small files of
``<out_dir>`` into ``$RESULTS/<area>/<p>/`` (the committed layout):

| From ``out/`` | To ``$RESULTS/`` |
|---|---|
| ``*.json``, ``*.md``, ``style_photos/*.json`` | ``furniture/<p>/`` (``style*.json`` also ``renders/<p>/``) |
| ``layout_debug/*.json``, ``layout_debug/*.jpg`` | ``furniture/<p>/layout_debug/`` |
| ``scene/*.json``, ``scene/*.log``, ``renders/`` | ``renders/<p>/`` |
| ``controls/``, ``controls/hide_*/`` | ``renders/<p>/controls/``, ``.../hide_*/`` |
| ``polish/`` (+ ``sweep/``, ``smoke/``), ``gate/``, ``check/`` | ``polish/<p>/``, ``gate/<p>/``, ``check/<p>/`` |
| ``final/``, ``final/debug/`` | ``final/<p>/``, ``final/<p>/debug/`` |
| ``run/*.json``, ``run/logs/*.log`` (tails) | ``run/<p>/``, ``run/<p>/logs/`` |
| ``ab/renders/*``, ``ab/cameras_check.json``, ``ab/pairs.json``, ``check/realism/*`` | ``realism/<p>/`` |

Public filter (as ``polish.sh copy_files``): ``*.json`` and ``*.md`` below
8 MB; ``*_preview.jpg``, ``*_alt_preview.jpg``, ``*_gate.jpg``,
``*_check.jpg``, ``*_plan.jpg``, ``contact_*.jpg`` (and every ``*.jpg`` of a
``debug`` folder) up to 300 KB; the last 400 lines of ``*.log``. Only the
files directly in each folder.

Private projects use an allow-list only, into
``<results-private>/<alias>/<area>/``: ``final/final_report.md``,
``final/final_manifest.json``, ``final/*_final_preview.jpg``,
``final/contact_*.jpg`` and ``run/<stage>.json`` without its ``inputs`` map.
Nothing else (documents, plan crops, debug overlays, building JSON, check
answers, logs) ever leaves ``/workspace/outputs-private/<alias>/``.

``--since STAMP``: only files newer than the stamp file (a full copy when it
does not exist yet); the stamp is renewed after the copy, 2 s back (the
volume's timestamps may have 1 s steps). The command prints only file counts
(nothing about a private project's files reaches the job log).

Why: the runner collects ``$RESULTS`` (and ``results-private``) over HTTP;
full-size PNGs, EXR passes and scenes stay on the volume.
"""
from __future__ import annotations

import fnmatch
import json
import os
import shutil
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from wenart.run.projects import ProjectRef
from wenart.run.state import private_record

KIB = 1024
MAX_TEXT_BYTES = 7999 * KIB        # find -size -8000k (rounded up to KiB, less than 8000)
MAX_JPEG_BYTES = 300 * KIB         # find -size -301k
LOG_TAIL_LINES = 400
STAMP_OVERLAP_S = 2
PREVIEW_PATTERNS = ("*_preview.jpg", "*_alt_preview.jpg", "*_gate.jpg", "*_check.jpg", "*_plan.jpg", "contact_*.jpg")


@dataclass(frozen=True)
class Rule:
    src: str          # folder relative to out/ ("" = out itself; may end in a glob such as controls/hide_*)
    area: str         # result area
    dst: str          # sub-folder of the area folder ("{name}" = the matched folder's name)
    kind: str         # general | style | json | debug | scene | names:<a>,<b> | private_final | private_run


PUBLIC_RULES = (
    Rule("", "furniture", "", "general"),
    Rule("", "renders", "", "style"),
    Rule("style_photos", "furniture", "style_photos", "json"),
    Rule("layout_debug", "furniture", "layout_debug", "debug"),
    Rule("scene", "renders", "", "scene"),
    Rule("renders", "renders", "", "general"),
    Rule("controls", "renders", "controls", "general"),
    Rule("controls/hide_*", "renders", "controls/{name}", "general"),
    Rule("polish", "polish", "", "general"),
    Rule("polish/sweep", "polish", "sweep", "general"),
    Rule("polish/smoke", "polish", "smoke", "general"),
    Rule("gate", "gate", "", "general"),
    Rule("check", "check", "", "general"),
    Rule("final", "final", "", "general"),
    Rule("final/debug", "final", "debug", "debug"),
    Rule("run", "run", "", "general"),
    Rule("run/logs", "run", "logs", "general"),
    Rule("ab/renders", "realism", "", "general"),
    Rule("ab", "realism", "", "names:cameras_check.json,pairs.json"),
    Rule("check/realism", "realism", "", "general"),
)
PRIVATE_RULES = (
    Rule("final", "final", "", "private_final"),
    Rule("run", "run", "", "private_run"),
)


def _match(name: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(name, p) for p in patterns)


def wanted(rule: Rule, path: Path) -> Optional[str]:
    """How ``path`` is copied under ``rule``: ``copy``, ``tail`` (log), ``record`` (private stage record)
    or None (not copied)."""
    name = path.name
    size = path.stat().st_size
    text = name.endswith((".json", ".md")) and size <= MAX_TEXT_BYTES
    small_jpg = name.endswith(".jpg") and size <= MAX_JPEG_BYTES
    kind = rule.kind
    if kind == "general":
        if text:
            return "copy"
        if small_jpg and _match(name, PREVIEW_PATTERNS):
            return "copy"
        return "tail" if name.endswith(".log") else None
    if kind == "style":
        return "copy" if _match(name, ("style*.json",)) and size <= MAX_TEXT_BYTES else None
    if kind == "json":
        return "copy" if name.endswith(".json") and size <= MAX_TEXT_BYTES else None
    if kind == "debug":
        return "copy" if (name.endswith(".json") and size <= MAX_TEXT_BYTES) or small_jpg else None
    if kind == "scene":
        if name.endswith(".json") and size <= MAX_TEXT_BYTES:
            return "copy"
        return "tail" if name.endswith(".log") else None
    if kind.startswith("names:"):
        return "copy" if name in kind[6:].split(",") and size <= MAX_TEXT_BYTES else None
    if kind == "private_final":
        if name in ("final_report.md", "final_manifest.json") and size <= MAX_TEXT_BYTES:
            return "copy"
        return "copy" if small_jpg and _match(name, ("*_final_preview.jpg", "contact_*.jpg")) else None
    if kind == "private_run":
        return "record" if name.endswith(".json") and size <= MAX_TEXT_BYTES else None
    raise ValueError(f"unknown copy rule kind {kind!r}")


def _sources(out_dir: Path, rule: Rule) -> list[tuple[Path, str]]:
    """``[(source folder, destination sub-folder)]`` of a rule."""
    if any(ch in rule.src for ch in "*?["):
        found = sorted(p for p in out_dir.glob(rule.src) if p.is_dir() and not p.is_symlink())
        return [(p, rule.dst.format(name=p.name)) for p in found]
    folder = out_dir / rule.src if rule.src else out_dir
    return [(folder, rule.dst)] if folder.is_dir() and not folder.is_symlink() else []


def tail_text(path: Path, n: int = LOG_TAIL_LINES) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return "".join(deque(fh, maxlen=n))


def copy_project(ref: ProjectRef, since: Optional[float] = None) -> int:
    """Copy one project's files (public layout or private allow-list); the number of files written."""
    rules = PRIVATE_RULES if ref.private else PUBLIC_RULES
    out_dir = Path(ref.out_dir)
    count = 0
    if not out_dir.is_dir():
        return 0
    for rule in rules:
        for folder, sub in _sources(out_dir, rule):
            dst_dir = ref.results_area(rule.area) / sub if sub else ref.results_area(rule.area)
            for path in sorted(folder.iterdir()):
                if not path.is_file() or path.is_symlink():
                    continue
                how = wanted(rule, path)
                if how is None or (since is not None and path.stat().st_mtime <= since):
                    continue
                dst_dir.mkdir(parents=True, exist_ok=True)
                target = dst_dir / path.name
                if how == "copy":
                    shutil.copyfile(path, target)
                elif how == "tail":
                    target.write_text(tail_text(path), encoding="utf-8")
                else:   # private stage record without its inputs map
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        continue
                    if not isinstance(data, dict) or data.get("kind") != "stage_record":
                        continue
                    target.write_text(json.dumps(private_record(data), indent=1, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
                count += 1
    return count


def _stamp(path: Path) -> None:
    """An empty file whose mtime is the volume's own time minus the overlap (polish.sh ``stamp``)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    t = path.stat().st_mtime - STAMP_OVERLAP_S
    os.utime(path, (t, t))


def copy_results(refs: Iterable[ProjectRef], since_stamp: Optional[Path] = None) -> dict:
    """Copy every project; ``{"public": n, "private": m, "full": bool}``. With ``since_stamp`` only the files
    changed since that stamp's time (all when it does not exist) and the stamp is renewed afterwards."""
    since = None
    nxt = None
    if since_stamp is not None:
        since_stamp = Path(since_stamp)
        if since_stamp.is_file():
            since = since_stamp.stat().st_mtime
        nxt = since_stamp.with_name(since_stamp.name + ".next")
        _stamp(nxt)                    # before the scan: files written during it go next time
    counts = {"public": 0, "private": 0, "full": since is None}
    for ref in refs:
        counts["private" if ref.private else "public"] += copy_project(ref, since)
    if nxt is not None:
        os.replace(nxt, since_stamp)
    return counts


def summary_line(counts: dict) -> str:
    what = "full copy" if counts["full"] else "changed since the last copy"
    return f"copy: {counts['public']} public file(s), {counts['private']} private file(s) ({what})"

