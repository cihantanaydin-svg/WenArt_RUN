"""Realism A/B preparation done by the orchestrator (docs/milestone6.md §6.3).

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

Why: the A/B compares the same camera rendered two ways; a camera that moved
(or was not rendered) would compare different pictures.

How: ``prepare_m5`` runs ``git show`` itself (it is started by the
orchestrator as ``python -m wenart.run ab-m5`` through the one runner);
``cameras_check`` is pure.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
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
