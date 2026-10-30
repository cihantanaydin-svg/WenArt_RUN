#!/usr/bin/env python3
"""Pack a job's public results into a few tar parts for the runner (30 Oct 2026, user OK of the pod-time item 5:
"Only apply the 5").

What: ``python3 scripts/pack_results.py <job_dir> <pack_dir>`` writes ``<pack_dir>/part-000.tar``, ``part-001.tar`` ...
and, last, ``<pack_dir>/manifest.json`` (its presence means the pack is complete). It prints one line with the files,
the bytes and the seconds the pod should wait for the runner's download (``grace_s``).
Why: real04 runs 20261029-201533, 20261030-043021 and 20261030-112241 ended with about 9,300 result files that the
runner fetched one by one through the pod proxy (0.8 s per request, 16 at a time: about 8 min) while the pod waited
120 s before it stopped itself: each run missed thousands of files (112241: 8,656) and needed a fetch pod. Ten parts of
about 32 MB download in parallel in well under a minute.
How: stdlib only (the pod's system python), the selection and the order of ``scripts/gpu_run.py`` (one source of
truth): the files the runner's walk takes (``results/``, at most ``COLLECT_MAX_DEPTH`` folders deep, no symlinks)
except the 3D files (streamed apart, as before: listed under ``big``) and files of ``COLLECT_MAX_FILE`` bytes or more
(left out and listed under ``too_big``, as the walk did); records first, then images (``collect_order``: the runner's
size cap cuts only images). ``results-private/`` is not packed (the runner walks it as before). Each part is written
under a temporary name and renamed; a second run replaces the pack. Never fatal for the job: ``pod_entry.sh`` runs it
under a time limit and the runner walks the files when no manifest is there.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tarfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gpu_run as G  # noqa: E402 - the runner's collection rules (stdlib only, no side effects on import)

PACK_VERSION = 1
PART_BYTES = 32_000_000       # one part; a real04 run (~330 MB of small files) packs into about ten
GRACE_BASE_S = 60             # the pod's wait for the runner: a base ...
GRACE_MB_PER_S = 4.0          # ... plus the pack and the 3D files at a slow 4 MB/s through the pod proxy
GRACE_MAX_S = 600


def select(job_dir: Path) -> dict:
    """``{"packed": [(rel, bytes)], "big": [(rel, bytes)], "too_big": [text]}`` of ``<job_dir>/results`` as the
    runner's walk sees it (``rel`` relative to ``results/``), ``packed`` in the runner's download order."""
    root = Path(job_dir) / "results"
    out = {"packed": [], "big": [], "too_big": []}

    def walk(folder: Path, rel: str, depth: int) -> None:
        try:
            entries = sorted(os.scandir(folder), key=lambda e: e.name)
        except OSError:
            return
        for e in entries:
            name = rel + e.name
            if e.is_symlink():
                continue
            if e.is_dir(follow_symlinks=False):
                if depth < G.COLLECT_MAX_DEPTH:
                    walk(Path(e.path), name + "/", depth + 1)
                continue
            if not e.is_file(follow_symlinks=False) or e.name.endswith(".part"):
                continue
            size = e.stat(follow_symlinks=False).st_size
            if G.is_big_result(name):
                out["big"].append((name, size))
            elif size >= G.COLLECT_MAX_FILE:
                out["too_big"].append(f"results/{name} ({size / 1e6:.1f} MB)")
            else:
                out["packed"].append((name, size))

    walk(root, "", 0)
    out["packed"].sort(key=lambda item: (G.collect_order(item[0]), item[0]))
    return out


def split(files: list[tuple[str, int]], part_bytes: int = PART_BYTES) -> list[list[tuple[str, int]]]:
    """The files in order, cut into parts of at most ``part_bytes`` (a larger single file gets a part of its own)."""
    parts: list[list[tuple[str, int]]] = []
    cur: list[tuple[str, int]] = []
    n = 0
    for rel, size in files:
        if cur and n + size > part_bytes:
            parts.append(cur)
            cur, n = [], 0
        cur.append((rel, size))
        n += size
    if cur:
        parts.append(cur)
    return parts


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def grace_s(total_bytes: int) -> int:
    """Seconds the pod waits after the job for the runner's download of ``total_bytes`` (the runner stops the pod
    right after a successful collection, so the wait costs nothing while it is attached)."""
    return int(min(GRACE_MAX_S, GRACE_BASE_S + total_bytes / 1e6 / GRACE_MB_PER_S))


def pack(job_dir: Path, pack_dir: Path, part_bytes: int = PART_BYTES) -> dict:
    """Write the parts and the manifest; returns the manifest."""
    t0 = time.time()
    job_dir, pack_dir = Path(job_dir), Path(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "manifest.json").unlink(missing_ok=True)       # no manifest: no pack (the runner walks the files)
    for old in pack_dir.glob("part-*.tar*"):
        old.unlink()
    sel = select(job_dir)
    root = job_dir / "results"
    parts = []
    for i, chunk in enumerate(split(sel["packed"], part_bytes)):
        name = f"part-{i:03d}.tar"
        tmp = pack_dir / (name + ".tmp")
        files, nbytes = 0, 0
        with tarfile.open(tmp, "w", format=tarfile.PAX_FORMAT) as tar:
            for rel, _size in chunk:
                path = root / rel
                try:
                    info = tar.gettarinfo(str(path), arcname=rel)
                    if not info.isfile():
                        continue
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with open(path, "rb") as fh:
                        tar.addfile(info, fh)
                except OSError:
                    continue                 # gone since the scan: the runner's walk would have missed it too
                files += 1
                nbytes += info.size
        os.replace(tmp, pack_dir / name)
        parts.append({"name": name, "bytes": (pack_dir / name).stat().st_size, "sha256": sha256(pack_dir / name),
                      "files": files, "file_bytes": nbytes, "first": chunk[0][0], "last": chunk[-1][0]})
    big_bytes = sum(size for _rel, size in sel["big"])
    total = sum(p["bytes"] for p in parts)
    manifest = {"version": PACK_VERSION, "job_id": job_dir.name, "tree": "results",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "files": sum(p["files"] for p in parts), "file_bytes": sum(p["file_bytes"] for p in parts),
                "bytes": total, "parts": parts,
                "big": [{"path": rel, "bytes": size} for rel, size in sel["big"]], "too_big": sel["too_big"],
                "grace_s": grace_s(total + big_bytes), "seconds": round(time.time() - t0, 1)}
    tmp = pack_dir / "manifest.json.tmp"
    tmp.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, pack_dir / "manifest.json")
    return manifest


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: pack_results.py <job_dir> <pack_dir>", file=sys.stderr)
        return 2
    m = pack(Path(argv[0]), Path(argv[1]))
    print(f"pack: {m['files']} file(s), {m['bytes'] / 1e6:.1f} MB in {len(m['parts'])} part(s), "
          f"{len(m['big'])} 3D file(s) apart, {len(m['too_big'])} too big; {m['seconds']} s; grace_s {m['grace_s']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
