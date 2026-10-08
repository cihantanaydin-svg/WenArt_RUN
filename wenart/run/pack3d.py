"""Hand over a project's 3D files (Milestone 9, docs/milestone9.md §5a; Milestone 10 §1.6, §3.2 item 8).

The export stage writes ``<p>.blend`` and ``<p>.glb`` (75 and 151 MB for real01); the Claude app refused single
uploads of that size (HTTP 502 on 4 Oct 2026) and took 24 MiB parts. This packs a project's result folder
(``results/final/<p>/`` as the runner collected it, or the volume's ``outputs/<p>/``) into one zip with the
``.blend`` (stored: Blender compresses it already), the ``.glb`` (deflated: about 60 % smaller),
``export_manifest.json`` and ``ATTRIBUTION.md``, split into parts of ``--part-mb`` MiB, with the zip's sha256
and a README that says how to join the parts::

    python -m wenart.run.pack3d --src runs/<job>/results/final/real01 --out runs/<job>/delivery [--part-mb 24]

Milestone 10: a building with alternative plans has one 3D set per variant: ``<p>.blend`` / ``.glb`` (the base,
the whole building) and ``<p>-<id>.blend`` / ``.glb`` per alternative, next to the base files or in
``variants/<id>/export/`` (``variants/<id>/3d/``) of the project folder (``wenart.blender.cli export
--variant``). Each set becomes its own zip (``<p>_3d.zip.partNN``, ``<p>-<id>_3d.zip.partNN``), so the base can
be downloaded alone; the README lists every set.

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
MODELS = (".blend", ".glb")


def _folder(src: Path) -> Path:
    return src / "3d" if (src / "3d").is_dir() else src


def variant_folders(src: Path) -> list[Path]:
    """The export folders of the alternatives: ``<src>/variants/<id>/{3d,export}`` (a results folder or the
    volume's ``outputs/<p>``) or, when ``src`` is the volume's ``outputs/<p>/export``,
    ``<src>/../variants/<id>/export``."""
    src = Path(src)
    roots = [src / "variants"]
    if src.name in ("export", "3d"):
        roots.append(src.parent / "variants")
    out = []
    for root in roots:
        if not root.is_dir():
            continue
        for vdir in sorted(p for p in root.iterdir() if p.is_dir()):
            for sub in ("3d", "export"):
                if (vdir / sub).is_dir():
                    out.append(vdir / sub)
    return out


def files_of(src: Path) -> list[Path]:
    """The files that go into the base zip: ``3d/*.blend``, ``3d/*.glb``, ``3d/export_manifest.json`` (or the same
    names directly in ``src``, the volume's ``export/`` folder) and ``ATTRIBUTION.md`` next to them. With
    variant files beside the base files (``<p>-<id>.*``) only the base stem's files are listed here."""
    groups = sets_of(src)
    return groups[0][1] if groups else []


def sets_of(src: Path, name: str | None = None) -> list[tuple[str, list[Path]]]:
    """``[(stem, files)]``: the base set first (``<name>``: the given name, else the shortest model stem of the
    base folder), then one set per alternative (``<name>-<id>``) with its export manifest; every set carries
    ``ATTRIBUTION.md`` when the project has one."""
    src = Path(src)
    folder = _folder(src)
    base_models = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix in MODELS) if folder.is_dir() else []
    variant_models = [(vf, sorted(p for p in vf.iterdir() if p.is_file() and p.suffix in MODELS))
                      for vf in variant_folders(src)]
    if not base_models and not any(m for _, m in variant_models):
        return []
    stems = [p.stem for p in base_models] or [p.stem for _, m in variant_models for p in m]
    base = name or min(stems, key=lambda s: (len(s), s))
    if name is None and any(p.stem != base and not p.stem.startswith(base + "-") for p in base_models):
        base = base_models[0].stem if base_models else base
    attribution = [p for p in (src / "ATTRIBUTION.md", folder / "ATTRIBUTION.md") if p.is_file()][:1]
    sets: dict[str, list[Path]] = {}
    manifests: dict[str, Path] = {}
    for p in base_models:
        stem = p.stem if p.stem == base or p.stem.startswith(base + "-") else base
        sets.setdefault(stem, []).append(p)
    if (folder / "export_manifest.json").is_file():
        manifests[base] = folder / "export_manifest.json"
    for vf, models in variant_models:
        for p in models:
            sets.setdefault(p.stem, []).append(p)
            if (vf / "export_manifest.json").is_file():
                manifests[p.stem] = vf / "export_manifest.json"
    order = ([base] if base in sets else []) + sorted(s for s in sets if s != base)
    out = []
    for stem in order:
        files = sorted(sets[stem])
        if stem in manifests:
            files.append(manifests[stem])
        files += attribution
        out.append((stem, files))
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def readme(name: str, parts: list[str], digest: str, contents: list[str], more: list[tuple] = ()) -> str:
    joined = "+".join(parts)
    lines = [
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
    ]
    if more:
        lines += ["Other variants of the building (alternative plans, docs/milestone10.md §1.6), each its own set:", ""]
        for stem, vparts, vdigest, vcontents in more:
            lines += [(f"- {stem}: join {stem}_3d.zip.part* into {stem}_3d.zip (copy /b {'+'.join(vparts)} "
                       f"{stem}_3d.zip on Windows), sha256 {vdigest}; inside: {', '.join(vcontents)}")]
        lines.append("")
    return "\n".join(lines)


def _zip_parts(stem: str, files: list[Path], out: Path, part_mb: int) -> tuple[list[Path], str]:
    archive = out / f"{stem}_3d.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for p in files:
            mode = zipfile.ZIP_STORED if p.suffix in STORED else zipfile.ZIP_DEFLATED
            z.write(p, f"{stem}/{p.name}", compress_type=mode)
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
    return parts, digest


def pack(src: Path, out: Path, part_mb: int = DEFAULT_PART_MB, name: str | None = None) -> list[Path]:
    """Write ``<name>_3d.zip.partNN``, ``<name>_3d.zip.sha256`` (and the same per variant set,
    ``<name>-<id>_3d.zip...``) and README_3d.txt into ``out``; returns them."""
    sets = sets_of(src, name)
    if not sets:
        raise FileNotFoundError(f"no .blend or .glb in {src} or {Path(src) / '3d'}")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    stem0, files0 = sets[0]
    parts0, digest0 = _zip_parts(stem0, files0, out, part_mb)
    written += parts0 + [out / f"{stem0}_3d.zip.sha256"]
    more = []
    for stem, files in sets[1:]:
        parts, digest = _zip_parts(stem, files, out, part_mb)
        written += parts + [out / f"{stem}_3d.zip.sha256"]
        more.append((stem, [p.name for p in parts], digest, [p.name for p in files]))
    (out / README).write_text(readme(stem0, [p.name for p in parts0], digest0, [p.name for p in files0], more),
                              encoding="utf-8")
    return written + [out / README]


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
