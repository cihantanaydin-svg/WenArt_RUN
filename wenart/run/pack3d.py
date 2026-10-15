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

Milestone 13 (docs/milestone13.md §6, §12 D4; track T8): the README carries the project's licence line
(``commercial-safe: yes`` / ``no (flagged assets: ...)`` with the licence mode) and the list of the pieces built below
the library level (module builders and parametric families: id, type, method, builder, room), read from the final
manifest next to the 3D files (``<src>/final_manifest.json`` of ``results/final/<p>/``, or ``../final/
final_manifest.json`` of the volume's ``outputs/<p>/export``; ``licence_notes``). Without a manifest the README
says so.

Milestone 13 (T6, the vegetation): the README also says what the .glb carries of the site's vegetation. The leaf
cards of the hedges and card trees and the grass clumps are geometry-nodes instances; the glTF export writes an
object's evaluated mesh only, so they reach the .glb when the export realized them under the polygon cap
(``wenart.blender.site.realize_site_instances``, recorded as ``realized_instances`` in ``export_manifest.json``);
without that record the README says the pack carries the hedge cores, trunks and crown cards only (the .blend
keeps every instance; ``vegetation_notes``).

Prints the written files; exit 0, or 2 when the folder has no 3D file. Only the standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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


def final_manifest_path(src: Path) -> Path | None:
    """The final manifest that belongs to the 3D files: ``<src>/final_manifest.json`` (a results folder, where
    ``3d/`` sits next to it), ``<src>/../final_manifest.json`` (``src`` is the ``3d`` folder itself) or
    ``<src>/../final/final_manifest.json`` (the volume's ``outputs/<p>/export``); None when none exists."""
    src = Path(src)
    for p in (src / "final_manifest.json", src.parent / "final_manifest.json",
              src.parent / "final" / "final_manifest.json"):
        if p.is_file():
            return p
    return None


def licence_notes(src: Path) -> list[str]:
    """Milestone 13: the README lines of the licence state: the project's commercial-safe line with its licence
    mode (``licence`` of the final manifest), the views that are not commercial-safe, and every piece built below
    the library level (``below_library``). One line says so when the manifest is missing or older than
    Milestone 13."""
    path = final_manifest_path(src)
    if path is None:
        return ["Licence (Milestone 13): no final_manifest.json next to the 3D files; the commercial-safe line and "
                "the list of pieces built below the library level are in final_report.md of the run."]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return [f"Licence (Milestone 13): {path.name} is not readable; see final_report.md of the run."]
    if not isinstance(manifest, dict) or not isinstance(manifest.get("licence"), dict):
        return ["Licence (Milestone 13): the final manifest carries no licence block (a run before Milestone 13): "
                "see the Attribution section of final_report.md and ATTRIBUTION.md."]
    lic = manifest["licence"]
    lines = [f"Licence mode: {lic.get('mode') or 'unknown'} ({lic.get('mode_source') or 'source not recorded'}). "
             f"Project: {lic.get('line') or 'commercial-safe: not recorded'}."]
    flagged_views = [v for v in manifest.get("views") or []
                     if isinstance(v, dict) and not (v.get("commercial_safe") or {}).get("safe", True)]
    if flagged_views:
        lines.append("Views that are not commercial-safe: " + ", ".join(
            f"{v.get('camera')} ({', '.join((v.get('commercial_safe') or {}).get('flagged') or [])})"
            for v in flagged_views) + ".")
    below = [b for b in manifest.get("below_library") or [] if isinstance(b, dict)]
    gaps = [b for b in below if b.get("gap")]
    if not below:
        lines.append("Built below library level: none (every furniture piece is a library model).")
    else:
        lines.append(f"Built below library level (module builders and parametric families; {len(gaps)} library "
                     f"gap(s) to close with a real model, {len(below) - len(gaps)} by design):")
        lines += [f"  - {b.get('id')}: {b.get('type')}, {b.get('method')}, {b.get('builder')}, room "
                  f"{b.get('room_id') or '-'}" + ("" if b.get("gap") else " (by design)") for b in below]
    return lines


def vegetation_notes(src: Path) -> list[str]:
    """Milestone 13 (T6): the README lines on the site's vegetation in the .glb, from the export manifest next to
    the 3D files (``<folder>/export_manifest.json``, key ``realized_instances`` = the record of
    ``wenart.blender.site.realize_site_instances``: ``cap``, ``polygons``, ``realized`` [group names], ``skipped``
    [{group, polygons, reason}]). Without the record (an export before Milestone 13, or one that did not realize)
    the lines say the pack carries the hedge cores, trunks and crown cards only."""
    folder = _folder(Path(src))
    path = folder / "export_manifest.json"
    record = None
    if path.is_file():
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            record = doc.get("realized_instances") if isinstance(doc, dict) else None
        except (OSError, ValueError):
            record = None
    base = ("The hedges, the card trees and the lawn are built as geometry-nodes instances (leaf cards, grass clumps) "
            "over a hedge core, a trunk with crown cards and the ground; the .blend keeps every instance.")
    if not isinstance(record, dict):
        return [base, "The .glb carries the hedge cores, the trunks and crown cards and the lawn surface only: the "
                      "export did not realize the instances (no realized_instances record in export_manifest.json), "
                      "and a glTF export writes an object's evaluated mesh without its instances."]
    realized = [str(g) for g in record.get("realized") or []]
    skipped = [s for s in record.get("skipped") or [] if isinstance(s, dict)]
    lines = [base, f"Realized for the .glb under a cap of {record.get('cap')} polygons: {len(realized)} vegetation "
                   f"node group(s), {record.get('polygons')} polygons"
                   + (": " + ", ".join(realized) if realized else "") + "."]
    if skipped:
        lines.append("Left as instances (in the .blend, not in the .glb): " + "; ".join(
            f"{s.get('group')} ({s.get('polygons')} polygons)" for s in skipped) + ".")
    lines.append("The Poly Haven hero trees are collection instances of the imported models (not geometry nodes): "
                 "the cap does not apply to them.")
    return lines


def readme(name: str, parts: list[str], digest: str, contents: list[str], more: list[tuple] = (),
           notes: list[str] = (), vegetation: list[str] = ()) -> str:
    """The README text; ``notes`` (Milestone 13: ``licence_notes``) and ``vegetation`` (``vegetation_notes``) go
    at the end."""
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
    if notes:
        lines += ["Licence (Milestone 13, docs/milestone13.md §6):", ""] + list(notes) + [""]
    if vegetation:
        lines += ["Vegetation in the 3D files (Milestone 13, docs/milestone13.md §13.2 T6):", ""] + list(vegetation) + [""]
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
    (out / README).write_text(readme(stem0, [p.name for p in parts0], digest0, [p.name for p in files0], more,
                                     licence_notes(Path(src)), vegetation_notes(Path(src))), encoding="utf-8")
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
