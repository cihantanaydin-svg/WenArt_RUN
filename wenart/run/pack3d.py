"""Hand over a project's 3D files (Milestone 9, docs/milestone9.md §5a).

The export stage writes ``<p>.blend`` and ``<p>.glb`` (75 and 151 MB for real01); the Claude app refused single
uploads of that size (HTTP 502 on 4 Oct 2026) and took 24 MiB parts. This packs a project's result folder
(``results/final/<p>/`` as the runner collected it, or the volume's ``outputs/<p>/``) into one zip with the
``.blend`` (stored: Blender compresses it already), the ``.glb`` (deflated: about 60 % smaller),
``export_manifest.json`` and ``ATTRIBUTION.md``, split into parts of ``--part-mb`` MiB, with the zip's sha256
and a README that says how to join the parts::

    python -m wenart.run.pack3d --src runs/<job>/results/final/real01 --out runs/<job>/delivery [--part-mb 24]

Prints the written files; exit 0, or 2 when the folder has no 3D file. Only the standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

DEFAULT_PART_MB = 24
README = "README_3d.txt"
STORED = (".blend",)              # already compressed (zstd) by Blender


def files_of(src: Path) -> list[Path]:
    """The files that go into the zip: ``3d/*.blend``, ``3d/*.glb``, ``3d/export_manifest.json`` (or the same
    names directly in ``src``, the volume's ``export/`` folder) and ``ATTRIBUTION.md`` next to them."""
    src = Path(src)
    folder = src / "3d" if (src / "3d").is_dir() else src
    found = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix in (".blend", ".glb"))
    if not found:
        return []
    extra = [folder / "export_manifest.json", src / "ATTRIBUTION.md", folder / "ATTRIBUTION.md"]
    seen = set()
    out = list(found)
    for p in extra:
        if p.is_file() and p.name not in seen:
            seen.add(p.name)
            out.append(p)
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def readme(name: str, parts: list[str], digest: str, contents: list[str]) -> str:
    joined = "+".join(parts)
    return "\n".join([
        f"3D files of project {name} (WenArt_RUN, docs/milestone9.md §5a).",
        "",
        f"1. Join the {len(parts)} parts into {name}_3d.zip:",
        f"   Mac / Linux:  cat {name}_3d.zip.part* > {name}_3d.zip",
        f"   Windows:      copy /b {joined} {name}_3d.zip",
        f"2. Check (optional): the sha256 of {name}_3d.zip is {digest}",
        f"3. Unzip. Inside: {', '.join(contents)}",
        "",
        f"Open {name}.blend in Blender (File > Open): textures packed, the render cameras with their exposure in",
        "the custom property wenart_exposure_ev, the text block WENART_README explains the rest. The .glb opens",
        "with File > Import > glTF 2.0 and in other 3D tools. ATTRIBUTION.md lists the credits of every model.",
        "",
    ])


def pack(src: Path, out: Path, part_mb: int = DEFAULT_PART_MB, name: str | None = None) -> list[Path]:
    """Write ``<name>_3d.zip.partNN``, ``<name>_3d.zip.sha256`` and README_3d.txt into ``out``; returns them."""
    files = files_of(src)
    if not files:
        raise FileNotFoundError(f"no .blend or .glb in {src} or {Path(src) / '3d'}")
    name = name or next(p.stem for p in files if p.suffix in (".blend", ".glb"))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{name}_3d.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for p in files:
            mode = zipfile.ZIP_STORED if p.suffix in STORED else zipfile.ZIP_DEFLATED
            z.write(p, f"{name}/{p.name}", compress_type=mode)
    digest = sha256_file(archive)
    size = max(1, int(part_mb)) * 2**20
    parts: list[Path] = []
    with archive.open("rb") as fh:
        for i, chunk in enumerate(iter(lambda: fh.read(size), b"")):
            part = out / f"{archive.name}.part{i:02d}"
            part.write_bytes(chunk)
            parts.append(part)
    archive.unlink()
    (out / f"{archive.name}.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    (out / README).write_text(readme(name, [p.name for p in parts], digest, [p.name for p in files]),
                              encoding="utf-8")
    return parts + [out / f"{archive.name}.sha256", out / README]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.run.pack3d", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="results/final/<p> (with 3d/) or the volume's outputs/<p>/export")
    ap.add_argument("--out", required=True)
    ap.add_argument("--part-mb", type=int, default=DEFAULT_PART_MB)
    ap.add_argument("--name", default=None, help="file stem (default: the .blend's)")
    args = ap.parse_args(argv)
    try:
        written = pack(Path(args.src), Path(args.out), args.part_mb, args.name)
    except FileNotFoundError as exc:
        print(f"pack3d: {exc}", file=sys.stderr)
        return 2
    for p in written:
        print(f"{p} {p.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
