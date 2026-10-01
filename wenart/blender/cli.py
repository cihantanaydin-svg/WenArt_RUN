"""Run the Blender build and render scripts from outside Blender.

Finds the Blender binary (``WENART_BLENDER`` env, then
``/workspace/tools/blender/blender`` on the pod, then
``/opt/wenart/blender/blender`` in the cloud session, then ``blender`` on
PATH) and starts ``blender -b [scene.blend] --python <script> -- <args>``.
The tests and ``scripts/jobs/render.sh`` go through this module so the
command line is written once.

CLI::

    python -m wenart.blender.cli build --building outputs/p/building.json --style outputs/p/style.json \
        --assets assets --out outputs/p/scene [--level L0] [--no-textures] [--preview-samples N]
    python -m wenart.blender.cli render --scene outputs/p/scene/scene.blend --out outputs/p/renders \
        [--cameras all|cam_a,cam_b] [--samples N] [--res WxH] [--force] [--device auto|cpu]
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
BUILD_SCRIPT = HERE / "build.py"
RENDER_SCRIPT = HERE / "render.py"
CANDIDATES = ("/workspace/tools/blender/blender", "/opt/wenart/blender/blender")


class BlenderNotFound(RuntimeError):
    pass


def find_blender() -> str | None:
    """Path of the Blender binary or None."""
    env = os.environ.get("WENART_BLENDER")
    if env and Path(env).is_file() and os.access(env, os.X_OK):
        return env
    for cand in CANDIDATES:
        if Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return shutil.which("blender")


def run_blender(script: Path, args: list[str], blend: str | None = None, log_path: Path | None = None,
                timeout: int = 7200, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a script inside Blender in background mode. Raises on failure with
    the tail of the output; the full output goes to ``log_path`` when given."""
    blender = find_blender()
    if blender is None:
        raise BlenderNotFound("no Blender binary: set WENART_BLENDER or install it under /opt/wenart/blender")
    cmd = [blender, "-b"]
    if blend:
        cmd.append(str(blend))
    # Without --python-exit-code Blender exits 0 after an unhandled exception
    # in the script, so failures would pass unnoticed.
    cmd += ["--python-exit-code", "1", "--python", str(script), "--", *args]
    env = dict(os.environ)
    env.setdefault("WENART_REPO_ROOT", str(REPO_ROOT))
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, cwd=cwd or str(REPO_ROOT))
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(f"$ {' '.join(cmd)}\n\n{proc.stdout}\n--- stderr ---\n{proc.stderr}", encoding="utf-8")
    if proc.returncode != 0:
        tail = (proc.stdout[-3000:] + "\n" + proc.stderr[-3000:]).strip()
        raise RuntimeError(f"blender exited with {proc.returncode} running {script.name}:\n{tail}")
    return proc


def build(building: str, out: str, style: str | None = None, assets: str | None = None, level: str | None = None,
          no_textures: bool = False, preview_samples: int | None = None, timeout: int = 3600) -> Path:
    """Build the scene; returns the path of ``scene_manifest.json``."""
    args = ["--building", str(building), "--out", str(out)]
    if style:
        args += ["--style", str(style)]
    if assets:
        args += ["--assets", str(assets)]
    if level:
        args += ["--level", level]
    if no_textures:
        args.append("--no-textures")
    if preview_samples is not None:
        args += ["--preview-samples", str(preview_samples)]
    run_blender(BUILD_SCRIPT, args, log_path=Path(out) / "build.log", timeout=timeout)
    return Path(out) / "scene_manifest.json"


def render(scene: str, out: str, cameras: str = "all", samples: int | None = None, res: str | None = None,
           force: bool = False, device: str = "auto", timeout: int = 7200) -> Path:
    """Render cameras of a built scene; returns the path of ``render_manifest.json``."""
    args = ["--out", str(out), "--cameras", cameras, "--device", device]
    if samples is not None:
        args += ["--samples", str(samples)]
    if res:
        args += ["--res", res]
    if force:
        args.append("--force")
    run_blender(RENDER_SCRIPT, args, blend=str(scene), log_path=Path(out) / "render.log", timeout=timeout)
    return Path(out) / "render_manifest.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wenart.blender.cli", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="build scene.blend / scene.glb / manifests from a building JSON")
    b.add_argument("--building", required=True)
    b.add_argument("--style")
    b.add_argument("--assets")
    b.add_argument("--out", required=True)
    b.add_argument("--level")
    b.add_argument("--no-textures", action="store_true")
    b.add_argument("--preview-samples", type=int)
    r = sub.add_parser("render", help="render cameras of a built scene with Cycles")
    r.add_argument("--scene", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--cameras", default="all")
    r.add_argument("--samples", type=int)
    r.add_argument("--res")
    r.add_argument("--force", action="store_true")
    r.add_argument("--device", default="auto", choices=["auto", "cpu"])
    w = sub.add_parser("which", help="print the Blender binary that would be used")
    ns = parser.parse_args(argv)
    try:
        if ns.command == "which":
            path = find_blender()
            print(path or "")
            return 0 if path else 1
        if ns.command == "build":
            path = build(ns.building, ns.out, ns.style, ns.assets, ns.level, ns.no_textures, ns.preview_samples)
        else:
            path = render(ns.scene, ns.out, ns.cameras, ns.samples, ns.res, ns.force, ns.device)
    except (BlenderNotFound, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
