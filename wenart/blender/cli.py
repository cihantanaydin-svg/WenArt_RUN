"""Run the Blender build and render scripts from outside Blender.

Finds the Blender binary (``WENART_BLENDER`` env, then
``/workspace/tools/blender/blender`` on the pod, then
``/opt/wenart/blender/blender`` in the cloud session, then ``blender`` on
PATH) and starts ``blender -b [scene.blend] --python <script> -- <args>``.
The tests and the job scripts go through this module so the command line is
written once.

CLI::

    python -m wenart.blender.cli build --building outputs/p/building_final.json --style outputs/p/style.json \
        --assets assets --out outputs/p/scene [--level L0] [--no-textures] [--preview-samples N] [--reuse]
    python -m wenart.blender.cli render --scene outputs/p/scene/scene.blend --out outputs/p/renders \
        [--cameras all|cam_a,cam_b] [--samples N] [--res WxH] [--force] [--device auto|cpu] \
        [--exposure auto|off|<EV>] [--exposure-target T] [--white-balance auto|off|fixed:r,g,b] \
        [--look-from <render_manifest.json>] [--hide ID[,ID] [--plug]] [--hide-sets 'cam:id;cam:id+plug']

``build --reuse`` (docs/milestone5.md §2.7) skips Blender when
``scene.blend`` and ``scene_manifest.json`` exist and the manifest's
``build_fingerprint`` equals the fingerprint of the current inputs, code
and arguments (``build.build_fingerprint``, pure Python); it prints
``BUILD_REUSED <fingerprint>``. Exit codes: 0 done, 2 when the Blender
script refused the request (unknown camera or id, a ``--look-from``
manifest without the camera, a building that needs review), 1 for any
other failure.
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


class BlenderFailed(RuntimeError):
    """Blender exited with a non-zero code (``returncode``; 2 = request refused by the script)."""

    def __init__(self, message: str, returncode: int):
        super().__init__(message)
        self.returncode = returncode


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
    """Run a script inside Blender in background mode. Raises ``BlenderFailed``
    (a RuntimeError) on failure with the tail of the output; the full output
    goes to ``log_path`` when given."""
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
        raise BlenderFailed(f"blender exited with {proc.returncode} running {script.name}:\n{tail}", proc.returncode)
    return proc


def build_fingerprint(building: str, style: str | None = None, assets: str | None = None, level: str | None = None,
                      no_textures: bool = False, preview_samples: int | None = None, proxies: bool = False) -> str:
    """The fingerprint build.py writes for these arguments (computed without Blender)."""
    from wenart.blender import build as build_script

    args = build_script.fingerprint_args(building, style, assets, level, no_textures, preview_samples, False, False,
                                         proxies)
    return build_script.build_fingerprint(args)


def build(building: str, out: str, style: str | None = None, assets: str | None = None, level: str | None = None,
          no_textures: bool = False, preview_samples: int | None = None, timeout: int = 3600,
          proxies: bool = False, reuse: bool = False) -> Path:
    """Build the scene; returns the path of ``scene_manifest.json``.
    ``proxies`` keeps the Milestone 3 proxy boxes for every furniture piece.
    ``reuse`` skips Blender when the finished build in ``out`` has the
    fingerprint of these inputs (prints ``BUILD_REUSED <fp>``)."""
    if reuse:
        from wenart.blender import build as build_script

        fp = build_fingerprint(str(building), str(style) if style else None, str(assets) if assets else None, level,
                               no_textures, preview_samples, proxies)
        ok, why = build_script.reusable_build(Path(out), fp)
        if ok:
            print(f"BUILD_REUSED {fp}")
            return Path(out) / "scene_manifest.json"
        print(f"BUILD_NEEDED: {why}")
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
    if proxies:
        args.append("--proxies")
    run_blender(BUILD_SCRIPT, args, log_path=Path(out) / "build.log", timeout=timeout)
    return Path(out) / "scene_manifest.json"


def render(scene: str, out: str, cameras: str = "all", samples: int | None = None, res: str | None = None,
           force: bool = False, device: str = "auto", timeout: int = 7200, hide: str | list | None = None,
           plug: bool = False, hide_sets: str | None = None, look_from: str | None = None,
           exposure: str | float | None = None, white_balance: str | None = None,
           exposure_target: float | None = None) -> Path:
    """Render cameras of a built scene; returns the path of ``render_manifest.json``
    (with ``hide_sets`` the folder that holds the ``hide_<id>/`` folders).
    ``exposure`` / ``white_balance`` default to render.py's ``auto``;
    ``look_from`` copies the per-camera look of another render manifest;
    ``hide`` (ids, a list or a comma string) + ``plug`` hide objects for
    every camera; ``hide_sets`` (``'cam:id;cam:id+plug'``) renders controls."""
    args = ["--out", str(out), "--cameras", cameras, "--device", device]
    if samples is not None:
        args += ["--samples", str(samples)]
    if res:
        args += ["--res", res]
    if force:
        args.append("--force")
    if exposure is not None:
        args += ["--exposure", str(exposure)]
    if exposure_target is not None:
        args += ["--exposure-target", str(exposure_target)]
    if white_balance is not None:
        args += ["--white-balance", str(white_balance)]
    if look_from:
        args += ["--look-from", str(look_from)]
    if hide:
        args += ["--hide", hide if isinstance(hide, str) else ",".join(hide)]
    if plug:
        args.append("--plug")
    if hide_sets:
        args += ["--hide-sets", hide_sets]
    run_blender(RENDER_SCRIPT, args, blend=str(scene), log_path=Path(out) / "render.log", timeout=timeout)
    return Path(out) if hide_sets else Path(out) / "render_manifest.json"


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
    b.add_argument("--proxies", action="store_true", help="Milestone 3 proxy boxes instead of furniture assets")
    b.add_argument("--reuse", action="store_true", help="skip Blender when the build fingerprint matches")
    r = sub.add_parser("render", help="render cameras of a built scene with Cycles")
    r.add_argument("--scene", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--cameras", default="all")
    r.add_argument("--samples", type=int)
    r.add_argument("--res")
    r.add_argument("--force", action="store_true")
    r.add_argument("--device", default="auto", choices=["auto", "cpu"])
    r.add_argument("--exposure", help="auto (default) | off | <EV>")
    r.add_argument("--exposure-target", type=float)
    r.add_argument("--white-balance", help="auto (default) | off | fixed:r,g,b")
    r.add_argument("--look-from", help="render_manifest.json to copy the per-camera EV and whitepoint from")
    r.add_argument("--hide", help="wenart ids to hide, comma separated")
    r.add_argument("--plug", action="store_true", help="close the wall holes of hidden doors/windows")
    r.add_argument("--hide-sets", help="'cam:id;cam:id+plug;...': control renders into <out>/hide_<id>/")
    sub.add_parser("which", help="print the Blender binary that would be used")
    ns = parser.parse_args(argv)
    try:
        if ns.command == "which":
            path = find_blender()
            print(path or "")
            return 0 if path else 1
        if ns.command == "build":
            path = build(ns.building, ns.out, ns.style, ns.assets, ns.level, ns.no_textures, ns.preview_samples,
                         proxies=ns.proxies, reuse=ns.reuse)
        else:
            path = render(ns.scene, ns.out, ns.cameras, ns.samples, ns.res, ns.force, ns.device, hide=ns.hide,
                          plug=ns.plug, hide_sets=ns.hide_sets, look_from=ns.look_from, exposure=ns.exposure,
                          white_balance=ns.white_balance, exposure_target=ns.exposure_target)
    except BlenderFailed as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2 if exc.returncode == 2 else 1
    except (BlenderNotFound, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
