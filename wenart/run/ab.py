"""Realism A/B preparation done by the orchestrator (docs/milestone6.md §6.3) and the Milestone 13 lever A/B.

What:
- ``prepare_m5`` (AB prepare part 2): writes ``out/ab/m5/`` from ``git show
  M5_LOOK_COMMIT:``: ``building_final.json`` (also copied to
  ``out/ab/building_m5.json``), ``scene_manifest.json``,
  ``render_manifest.json`` and the ``<cam>_preview.jpg`` of every M5 camera
  (the committed M5 previews: 1920 x 1080, JPEG quality 85). These are the A
  images of the ``m5_vs_m6`` set and the M5 building the B images are
  rendered from (with the M6 look and the M5 cameras).
- ``cameras_check`` (after the A/B render): every camera of the A/B scene is
  compared with the M5 scene manifest (position and target within 1 mm) and
  must have been rendered; ``out/ab/cameras_check.json`` =
  ``{"kept": [...], "dropped": [{"cam", "reason"}]}``. Only kept cameras are
  paired (``vision_check realism-pairs`` reads this file, never git).
- Milestone 13 (docs/milestone13.md §13.2 ab.py, §13.3, decision D6: the committed Milestone 11 runs of real02
  and real03 are the baseline, the committed Milestone 12 run of real04):
  ``prepare_m13(project, project_out, commit)`` writes ``out/ab/m13/`` with the baseline's ``scene_manifest.json``
  (its camera records are what ``build.py --cameras-from`` replays), ``render_manifest.json``, ``building_final.json``,
  the ``<cam>_preview.jpg`` of every camera and a ``style.json`` taken from the scene manifest's ``style_profile``
  (the style the baseline was built with). ``commit`` is a sha for ``git show`` (``M13_BASELINE_COMMITS``) or a
  directory (the pod reads the files of the working tree, which equal the baseline commit's: checked by sha256 on
  15 Oct 2026); a project without camera records (real04: no scene manifest was committed) returns an empty
  camera set with a ``reason``, and its build searches its cameras. ``M13_AB_VIEWS`` are the 8 + 8 fixed interior
  views of the lever A/B (``scripts/jobs/levers_ab.sh``: living, kitchen, bedroom, bath, hall of real02; living,
  bedroom, bath, hall of real03, which has no kitchen), chosen from the committed scene manifests with the
  Milestone 11 exposure of each view (the dark daylight rooms and the lamp-lit rooms both in the set).
  ``lever_sheet`` / ``lever_sheets`` write one contact sheet per view (the variants side by side, PIL) and
  ``lever_summary`` the seconds, VRAM, EV and ``lighting_dark`` per view and variant into ``summary.json`` /
  ``summary.md`` of ``results/ab_m13/``. The variant names are ``lighting.LIGHT_VARIANTS`` (round 3: ``m11`` =
  the Milestone 11 look, ``base`` = the production defaults); a variant folder that is missing is a "not rendered"
  row and a grey tile, so an older results folder (P1: no ``m11`` folder, ``base`` = the Milestone 11 look) still
  summarises and sheets.

Why: the A/B compares the same camera rendered two ways; a camera that moved
(or was not rendered) would compare different pictures.

How: ``prepare_m5`` runs ``git show`` itself (it is started by the
orchestrator as ``python -m wenart.run ab-m5`` through the one runner);
``cameras_check`` is pure. ``python -m wenart.run.ab m13-prepare | m13-sheets | m13-summary`` is the CLI of the
Milestone 13 parts (the job script calls it; ``wenart/run/__main__.py`` is the lead's file).
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from wenart.run.stages import M5_LOOK_COMMIT
from wenart.run.state import REPO_ROOT, write_json

CAMERA_TOLERANCE_M = 0.001


def git_show(commit: str, path: str, repo_root: Path = REPO_ROOT) -> bytes:
    """The bytes of ``<commit>:<path>`` (``git show``); ``FileNotFoundError`` when git has no such file."""
    proc = subprocess.run(["git", "-C", str(repo_root), "show", f"{commit}:{path}"], capture_output=True)
    if proc.returncode != 0:
        raise FileNotFoundError(f"{commit[:12]}:{path}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def prepare_m5(project: str, project_out: Path, commit: str = M5_LOOK_COMMIT, repo_root: Path = REPO_ROOT,
               show: Optional[Callable[[str, str], bytes]] = None) -> dict:
    """Write ``<project_out>/ab/m5/`` and ``ab/building_m5.json`` from ``commit`` (see the module docstring)."""
    show = show or (lambda c, p: git_show(c, p, repo_root))
    out = Path(project_out) / "ab" / "m5"
    out.mkdir(parents=True, exist_ok=True)
    building = show(commit, f"results/furniture/{project}/building_final.json")
    scene = show(commit, f"results/renders/{project}/scene_manifest.json")
    render = show(commit, f"results/renders/{project}/render_manifest.json")
    (out / "building_final.json").write_bytes(building)
    (out / "scene_manifest.json").write_bytes(scene)
    (out / "render_manifest.json").write_bytes(render)
    shutil.copyfile(out / "building_final.json", Path(project_out) / "ab" / "building_m5.json")
    cams = [c["name"] for c in json.loads(scene.decode("utf-8")).get("cameras") or []]
    previews, missing = 0, []
    for cam in cams:
        try:
            data = show(commit, f"results/renders/{project}/{cam}_preview.jpg")
        except FileNotFoundError:
            missing.append(cam)
            continue
        (out / f"{cam}_preview.jpg").write_bytes(data)
        previews += 1
    return {"project": project, "commit": commit, "cameras": len(cams), "previews": previews, "missing": missing}


def _close(a, b, tol: float) -> bool:
    if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)) or len(a) != len(b):
        return False
    return math.dist([float(x) for x in a], [float(x) for x in b]) <= tol + 1e-9


def cameras_check(m5_scene: dict, ab_scene: dict, ab_render: Optional[dict] = None,
                  tol_m: float = CAMERA_TOLERANCE_M) -> dict:
    """Kept and dropped cameras of the A/B (see the module docstring)."""
    m5 = {c["name"]: c for c in m5_scene.get("cameras") or []}
    ab = {c["name"]: c for c in ab_scene.get("cameras") or []}
    rendered = None
    if ab_render is not None:
        rendered = {r.get("camera") for r in ab_render.get("renders") or [] if r.get("preview")}
    kept, dropped = [], []
    for name in sorted(set(m5) | set(ab)):
        if name not in ab:
            dropped.append({"cam": name, "reason": "not in the A/B scene"})
        elif name not in m5:
            dropped.append({"cam": name, "reason": "not an M5 camera"})
        elif not _close(m5[name].get("position"), ab[name].get("position"), tol_m):
            dropped.append({"cam": name, "reason": f"position differs from M5 by more than {tol_m * 1000:.0f} mm"})
        elif not _close(m5[name].get("target"), ab[name].get("target"), tol_m):
            dropped.append({"cam": name, "reason": f"target differs from M5 by more than {tol_m * 1000:.0f} mm"})
        elif rendered is not None and name not in rendered:
            dropped.append({"cam": name, "reason": "not rendered in the A/B render"})
        else:
            kept.append(name)
    return {"schema_version": "0.1", "kind": "cameras_check", "tolerance_m": tol_m, "kept": kept, "dropped": dropped}


def write_cameras_check(project_out: Path) -> dict:
    """``out/ab/cameras_check.json`` from ``ab/m5/scene_manifest.json``, ``ab/scene/scene_manifest.json`` and
    ``ab/renders/render_manifest.json``."""
    ab = Path(project_out) / "ab"
    m5 = json.loads((ab / "m5" / "scene_manifest.json").read_text(encoding="utf-8"))
    scene = json.loads((ab / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    render_path = ab / "renders" / "render_manifest.json"
    render = json.loads(render_path.read_text(encoding="utf-8")) if render_path.is_file() else {"renders": []}
    result = cameras_check(m5, scene, render)
    write_json(ab / "cameras_check.json", result)
    return result


def m5_cameras(project_out: Path) -> list[str]:
    """The camera names of ``out/ab/m5/scene_manifest.json`` in manifest order."""
    path = Path(project_out) / "ab" / "m5" / "scene_manifest.json"
    try:
        return [c["name"] for c in json.loads(path.read_text(encoding="utf-8")).get("cameras") or []]
    except (OSError, ValueError, KeyError):
        return []


# --------------------------------------------------------------------------
# Milestone 13 (docs/milestone13.md §12 D6, §13.2, §13.3): the baseline runs and the lever A/B
# --------------------------------------------------------------------------

# The committed baseline runs (D6, 12 Oct 2026): real02 and real03 = the Milestone 11 run (results/renders/<p>/
# scene_manifest.json carries its cameras), real04 = the Milestone 12 run (no camera records committed).
M13_BASELINE_COMMITS = {"real02": "93aff07ff7ac6c2bf9c1c5c1d33298398fce9bc5",
                        "real03": "93aff07ff7ac6c2bf9c1c5c1d33298398fce9bc5",
                        "real04": "eddde01fa626e9af50e21c68bdd05c124bcc3c66"}
M13_DIR = "ab/m13"
M13_FILES = ("scene_manifest.json", "render_manifest.json")
# The 8 + 8 fixed interior views of the lever A/B (scripts/jobs/levers_ab.sh), from the committed Milestone 11
# scene manifests: the room type and the Milestone 11 exposure (results/final/<p>/final_manifest.json views[].exposure
# .ev) of each view, so the set holds the dark daylight rooms (EV +6..+8) and the lamp-lit rooms (EV about -0.5).
# real03 has no kitchen (its rooms: living, bedroom, bathroom, hall, stair), so it gives two halls and two baths.
M13_AB_VIEWS: dict[str, list[dict]] = {
    "real02": [
        {"camera": "cam_r_L-1_salon_1", "room_type": "living", "m11_ev": 4.17},
        {"camera": "cam_r_L-1_salon_2", "room_type": "living", "m11_ev": 3.67},
        {"camera": "cam_r_L-1_mutfak_1", "room_type": "kitchen", "m11_ev": 8.0},
        {"camera": "cam_r_L-1_mutfak_2", "room_type": "kitchen", "m11_ev": 8.0},
        {"camera": "cam_r_L0_yatak_odasi_1", "room_type": "bedroom", "m11_ev": 7.17},
        {"camera": "cam_r_L0_e_yatak_odasi_1", "room_type": "bedroom", "m11_ev": 6.17},
        {"camera": "cam_r_L0_e_banyo_1", "room_type": "bathroom", "m11_ev": -0.5},
        {"camera": "cam_r_L0_koridor_1", "room_type": "hall", "m11_ev": 0.67},
    ],
    "real03": [
        {"camera": "cam_r_L0_yasama_1", "room_type": "living", "m11_ev": 4.0},
        {"camera": "cam_r_L0_yasama_6_1", "room_type": "living", "m11_ev": 5.83},
        {"camera": "cam_r_L0_ebeveyn_odasi_1", "room_type": "bedroom", "m11_ev": 4.5},
        {"camera": "cam_r_L0_ebeveyn_odasi_4_1", "room_type": "bedroom", "m11_ev": 8.0},
        {"camera": "cam_r_L0_banyo_1", "room_type": "bathroom", "m11_ev": -0.5},
        {"camera": "cam_r_L0_banyo_4_1", "room_type": "bathroom", "m11_ev": -0.5},
        {"camera": "cam_r_L0_giris_holu_1", "room_type": "hall", "m11_ev": 7.83},
        {"camera": "cam_r_L0_kat_holu_1", "room_type": "hall", "m11_ev": -0.33},
    ],
}
# = lighting.LIGHT_VARIANTS (pinned equal in tests/test_m13_light.py). Round 3 (docs/milestone13.md §14.3): ``m11``
# is the Milestone 11 look (the "before"), ``base`` the production defaults (sun 1000 W/m², EV cap, rig, shell);
# the single levers keep their P1 meaning (the Milestone 11 look plus that lever), so a P1 sheet and a round-3
# sheet of the same name compare.
M13_AB_VARIANTS = ("m11", "base", "sun100", "sun300", "sun1000", "evcap", "rig", "shell", "all")
NO_CAMERA_RECORDS = ("no scene_manifest.json with camera records in the baseline (real04: the Milestone 12 run "
                     "committed none); the build searches its cameras and the before/after compares by camera name "
                     "and room")


def m13_views(project: str) -> list[str]:
    """The camera names of the lever A/B of ``project`` (``M13_AB_VIEWS``; ``[]`` for another project)."""
    return [v["camera"] for v in M13_AB_VIEWS.get(project, [])]


def prepare_m13(project: str, project_out: Path, commit: Optional[str] = None, repo_root: Path = REPO_ROOT,
                show: Optional[Callable[[str, str], bytes]] = None) -> dict:
    """Write ``<project_out>/ab/m13/`` from the baseline run of ``project`` (module docstring): ``commit`` a git
    sha (default ``M13_BASELINE_COMMITS[project]``) read with ``show(commit, path)`` (``git_show``), or a directory
    holding the baseline files (``scene_manifest.json``, ``render_manifest.json``, ``<cam>_preview.jpg``,
    ``building_final.json`` or the repo's ``results/furniture/<p>/building_final.json``). Returns ``{"project",
    "commit", "source", "out", "files", "cameras", "camera_records", "previews", "missing", "reason", "views",
    "views_missing"}``; a baseline without camera records gives ``cameras 0`` and the ``reason``."""
    from wenart.blender.cameras import replay_cameras

    out = Path(project_out) / M13_DIR
    out.mkdir(parents=True, exist_ok=True)
    source_dir = Path(commit) if commit and Path(commit).is_dir() else None
    if source_dir is None and commit is None:
        if project not in M13_BASELINE_COMMITS:
            raise ValueError(f"{project}: no baseline commit in M13_BASELINE_COMMITS and no directory given")
        commit = M13_BASELINE_COMMITS[project]
    show = show or (lambda c, p: git_show(c, p, repo_root))

    def read(rel: str) -> Optional[bytes]:
        """The bytes of a baseline file (``rel`` as under results/), None when absent."""
        if source_dir is not None:
            name = Path(rel).name
            candidates = [source_dir / name]
            if rel.startswith("results/furniture/"):
                candidates.append(Path(repo_root) / rel)
            for p in candidates:
                if p.is_file():
                    return p.read_bytes()
            return None
        try:
            return show(commit, rel)
        except FileNotFoundError:
            return None

    files: list[str] = []
    scene_bytes = read(f"results/renders/{project}/scene_manifest.json")
    for name in M13_FILES + ("build_brief.json",):
        data = scene_bytes if name == "scene_manifest.json" else read(f"results/renders/{project}/{name}")
        if data is not None:
            (out / name).write_bytes(data)
            files.append(name)
    building = read(f"results/furniture/{project}/building_final.json")
    if building is not None:
        (out / "building_final.json").write_bytes(building)
        files.append("building_final.json")
    info = {"project": project, "commit": None if source_dir is not None else commit,
            "source": str(source_dir) if source_dir is not None else f"git {str(commit)[:12]}", "out": str(out),
            "files": files, "cameras": 0, "camera_records": False, "previews": 0, "missing": [], "reason": None,
            "views": m13_views(project), "views_missing": list(m13_views(project))}
    if scene_bytes is None:
        info["reason"] = NO_CAMERA_RECORDS
        return info
    scene = json.loads(scene_bytes.decode("utf-8"))
    style = scene.get("style_profile")
    if isinstance(style, dict):
        (out / "style.json").write_text(json.dumps(style, indent=1, ensure_ascii=False), encoding="utf-8")
        files.append("style.json")
    plans = replay_cameras(scene)["plans"]
    names = [p["name"] for p in plans]
    info.update(cameras=len(names), camera_records=bool(names))
    if not names:
        info["reason"] = NO_CAMERA_RECORDS
        return info
    for cam in names:
        data = read(f"results/renders/{project}/{cam}_preview.jpg")
        if data is None:
            info["missing"].append(cam)
            continue
        (out / f"{cam}_preview.jpg").write_bytes(data)
        info["previews"] += 1
    info["views_missing"] = [v for v in m13_views(project) if v not in names]
    return info


def lever_sheet(view: str, tiles: list, out_path: Path, tile_width: int = 640, label_height: int = 28) -> Path:
    """One contact sheet of a view: ``tiles`` = ``[(label, image path or None)]`` side by side (two rows from
    five tiles on), ``tile_width`` px each, the label under each tile; a missing image is a grey tile that says
    so (PIL, no Blender)."""
    from PIL import Image, ImageDraw

    cols = min(len(tiles), 4) if len(tiles) > 4 else max(1, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sized = []
    for label, path in tiles:
        img = None
        if path and Path(path).is_file():
            with Image.open(path) as im:
                img = im.convert("RGB")
                img = img.resize((tile_width, max(1, round(img.height * tile_width / img.width))), Image.Resampling.LANCZOS)
        sized.append((label, img))
    tile_h = max([t.height for _, t in sized if t is not None] or [round(tile_width * 9 / 16)])
    gap = 4
    cell_h = tile_h + label_height
    sheet = Image.new("RGB", (cols * tile_width + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap + label_height),
                      (32, 32, 32))
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 6), view, fill=(230, 230, 230))
    for i, (label, img) in enumerate(sized):
        x = gap + (i % cols) * (tile_width + gap)
        y = label_height + gap + (i // cols) * (cell_h + gap)
        if img is None:
            draw.rectangle([x, y, x + tile_width, y + tile_h], fill=(70, 70, 70))
            draw.text((x + 8, y + tile_h // 2), "not rendered", fill=(220, 220, 220))
        else:
            sheet.paste(img, (x, y))
        draw.text((x + 4, y + tile_h + 6), label, fill=(230, 230, 230))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "JPEG", quality=80)
    return out_path


def lever_sheets(results_dir: Path, project: str, variants=M13_AB_VARIANTS, views: Optional[list] = None,
                 baseline_dir: Optional[Path] = None) -> list[Path]:
    """One sheet per view of the lever A/B: ``results_dir/<variant>/<project>/<cam>_preview.jpg`` of every variant,
    the baseline preview (``baseline_dir/<cam>_preview.jpg``, the committed Milestone 11 render) first; written to
    ``results_dir/sheets/<project>_<cam>.jpg``."""
    results_dir = Path(results_dir)
    out = []
    for cam in views or m13_views(project):
        tiles = []
        if baseline_dir is not None:
            tiles.append(("M11 baseline", Path(baseline_dir) / f"{cam}_preview.jpg"))
        for v in variants:
            tiles.append((v, results_dir / v / project / f"{cam}_preview.jpg"))
        out.append(lever_sheet(f"{project} {cam}", tiles, results_dir / "sheets" / f"{project}_{cam}.jpg"))
    return out


def lever_summary(results_dir: Path, projects=("real02", "real03"), variants=M13_AB_VARIANTS) -> dict:
    """The numbers of the lever A/B per project, variant and view from ``results_dir/<variant>/<project>/
    render_manifest.json`` (seconds, samples, EV, the metered EV, at_limit, lighting_dark, incident p50, the white
    balance, ``vram_mib`` of the entry) and ``vram.json`` (the job's nvidia-smi peak of the variant); written to
    ``results_dir/summary.json`` and ``summary.md``."""
    results_dir = Path(results_dir)
    rows = []
    for project in projects:
        for v in variants:
            folder = results_dir / v / project
            manifest = folder / "render_manifest.json"
            if not manifest.is_file():
                rows.append({"project": project, "variant": v, "camera": None, "status": "not rendered"})
                continue
            data = json.loads(manifest.read_text(encoding="utf-8"))
            peak = None
            if (folder / "vram.json").is_file():
                try:
                    peak = json.loads((folder / "vram.json").read_text(encoding="utf-8")).get("peak_mib")
                except ValueError:
                    peak = None
            entries = {r.get("camera"): r for r in data.get("renders") or []}
            for cam in m13_views(project):
                r = entries.get(cam)
                if r is None:
                    rows.append({"project": project, "variant": v, "camera": cam, "status": "not rendered",
                                 "vram_peak_mib": peak})
                    continue
                ex = r.get("exposure") or {}
                dark = ex.get("lighting_dark") or r.get("lighting_dark")
                rows.append({"project": project, "variant": v, "camera": cam, "status": "rendered",
                             "seconds": r.get("seconds"), "samples": r.get("samples"), "ev": ex.get("ev"),
                             "ev_raw": ex.get("ev_raw"), "at_limit": ex.get("at_limit"),
                             "lighting_dark": None if not dark else dark.get("severity"),
                             "incident_p50": ex.get("incident_p50"), "wb_temperature": ex.get("wb_temperature"),
                             "wb_mode": ex.get("wb_mode"), "vram_mib": r.get("vram_mib"), "vram_peak_mib": peak,
                             "light_variant": (data.get("light_variant") or {}).get("build"),
                             "exposure_limits": data.get("exposure_limits")})
    summary = {"schema_version": "0.1", "kind": "levers_ab_m13", "variants": list(variants),
               "projects": list(projects), "views": {p: m13_views(p) for p in projects}, "rows": rows}
    write_json(results_dir / "summary.json", summary)
    (results_dir / "summary.md").write_text(lever_summary_md(summary), encoding="utf-8")
    return summary


def lever_summary_md(summary: dict) -> str:
    """The Markdown table of ``lever_summary`` (one row per view and variant)."""
    lines = ["# Milestone 13 lever A/B (scripts/jobs/levers_ab.sh)", "",
             "| Project | Variant | View | Seconds | EV used | EV metered | lighting_dark | Incident p50 | WB K | "
             "VRAM MiB (view / peak) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in summary["rows"]:
        if r.get("status") != "rendered":
            lines.append(f"| {r['project']} | {r['variant']} | {r.get('camera') or '-'} | not rendered | | | | | | |")
            continue
        lines.append(f"| {r['project']} | {r['variant']} | {r['camera']} | {r.get('seconds')} | {r.get('ev')} | "
                     f"{r.get('ev_raw')} | {r.get('lighting_dark') or '-'} | {r.get('incident_p50')} | "
                     f"{r.get('wb_temperature')} | {r.get('vram_mib') or '-'} / {r.get('vram_peak_mib') or '-'} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list] = None) -> int:
    """``python -m wenart.run.ab m13-prepare --project p --project-out out [--commit sha | --from dir]``,
    ``m13-sheets --results dir --projects a,b [--variants ...] [--baseline dir-template]``, ``m13-summary --results
    dir [--projects a,b] [--variants ...]``."""
    parser = argparse.ArgumentParser(prog="wenart.run.ab")
    sub = parser.add_subparsers(dest="command", required=True)
    pp = sub.add_parser("m13-prepare", help="the baseline files of a project into <out>/ab/m13/")
    pp.add_argument("--project", required=True)
    pp.add_argument("--project-out", required=True)
    pp.add_argument("--commit", default=None, help="baseline commit (default M13_BASELINE_COMMITS)")
    pp.add_argument("--from", dest="source", default=None, help="a directory with the baseline files instead of git")
    ps = sub.add_parser("m13-sheets", help="one contact sheet per view, the variants side by side")
    ps.add_argument("--results", required=True)
    ps.add_argument("--projects", default="real02,real03")
    ps.add_argument("--variants", default=",".join(M13_AB_VARIANTS))
    ps.add_argument("--baseline", default=None, help="baseline previews, '{name}' = the project (optional)")
    pm = sub.add_parser("m13-summary", help="summary.json / summary.md of the lever A/B")
    pm.add_argument("--results", required=True)
    pm.add_argument("--projects", default="real02,real03")
    pm.add_argument("--variants", default=",".join(M13_AB_VARIANTS))
    args = parser.parse_args(argv)
    if args.command == "m13-prepare":
        try:
            info = prepare_m13(args.project, Path(args.project_out), args.source or args.commit)
        except (ValueError, OSError) as exc:
            print(f"m13-prepare: {exc}", file=sys.stderr)
            return 1
        print(f"m13-prepare {info['project']}: {info['cameras']} cameras, {info['previews']} previews from "
              f"{info['source']} into {info['out']}" + (f"; {info['reason']}" if info["reason"] else "")
              + (f"; views missing: {info['views_missing']}" if info["views_missing"] else ""))
        write_json(Path(args.project_out) / M13_DIR / "prepare_m13.json", info)
        return 0
    variants = [v for v in args.variants.split(",") if v]
    projects = [p for p in args.projects.split(",") if p]
    if args.command == "m13-sheets":
        n = 0
        for p in projects:
            base = Path(args.baseline.replace("{name}", p)) if args.baseline else None
            n += len(lever_sheets(Path(args.results), p, variants, baseline_dir=base))
        print(f"m13-sheets: {n} sheets in {Path(args.results) / 'sheets'}")
        return 0
    summary = lever_summary(Path(args.results), projects, variants)
    rendered = sum(1 for r in summary["rows"] if r.get("status") == "rendered")
    print(f"m13-summary: {rendered} of {len(summary['rows'])} view renders in {Path(args.results) / 'summary.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
