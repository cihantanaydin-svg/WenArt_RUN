"""Run the Blender build and render scripts from outside Blender.

Finds the Blender binary (``WENART_BLENDER`` env, then
``/workspace/tools/blender/blender`` on the pod, then
``/opt/wenart/blender/blender`` in the cloud session, then ``blender`` on
PATH) and starts ``blender -b [scene.blend] --python <script> -- <args>``.
The tests and the job scripts go through this module so the command line is
written once.

CLI::

    python -m wenart.blender.cli build --building outputs/p/building_final.json --style outputs/p/style.json \
        --assets assets --out outputs/p/scene [--level L0] [--no-textures] [--preview-samples N] [--reuse] \
        [--proxies] [--camera-policy m5|search] [--lens-mm L] [--variant ID] [--brief projects/p]
    python -m wenart.blender.cli render --scene outputs/p/scene/scene.blend --out outputs/p/renders \
        [--cameras all|cam_a,cam_b] [--samples N] [--res WxH] [--force] [--device auto|cpu] \
        [--exposure auto|off|<EV>] [--exposure-target T] [--white-balance auto|off|fixed:r,g,b] \
        [--look-from <render_manifest.json>] [--hide ID[,ID] [--plug]] [--hide-sets 'cam:id;cam:id+plug'] \
        [--alt-look None] [--max-bounces N] [--no-denoise] [--ev-offset X] [--preview-quality Q]

``build --reuse`` (docs/milestone5.md §2.7) skips Blender when
``scene.blend`` and ``scene_manifest.json`` exist and the manifest's
``build_fingerprint`` equals the fingerprint of the current inputs, code
and arguments (``build.build_fingerprint``, pure Python); it prints
``BUILD_REUSED <fingerprint>``. ``--camera-policy`` (docs/milestone6.md §4.2)
defaults to ``m5``; the full-run orchestrator passes ``search``. ``--lens-mm``
(Milestone 8, docs/milestone8.md §5): the brief's ``render.lens_mm`` for every
searched camera (14-35); without it 18 mm, 16 mm in rooms narrower than 2.2 m.

Render flags of docs/milestone6.md §5 rows 10-12 (render.py): ``--alt-look``
also saves ``<cam>_alt_preview.jpg`` with that look and the same window pull;
``--max-bounces``, ``--no-denoise``, ``--ev-offset`` and ``--preview-quality``
are the control and A/B flags of §6 (all part of the render key;
``--max-bounces N`` limits the diffuse, glossy and volume bounces to N and
keeps >= 2 transmission bounces, so the window panes still show the sky). The render
stops before a new camera once ``WENART_DEADLINE`` (epoch seconds, from the
environment) is past and exits 3.

Exit codes: 0 done, 2 when the Blender script refused the request (unknown
camera or id, a ``--look-from`` manifest without the camera, a building that
needs review, a bad flag, an unknown variant), 3 when the render was cut by
``WENART_DEADLINE`` (its manifest says ``incomplete: true``), 1 for any other
failure.

Milestone 10 (docs/milestone10.md §1.6, §1.6a, §1.6b row 9): ``build|render|export ...
--variant <id>`` (default ``base``). The paths stay explicit: the scheduler
passes ``outputs/<p>/variants/<id>/{scene,renders,export}/`` for an
alternative (``variant_path`` computes them); ``build`` builds that variant
into ``--out`` and ``export`` names the 3D files ``<name>-<id>.blend`` /
``.glb`` (``export_name``). ``build --brief <project dir | brief.yaml |
brief JSON>`` gives the build the brief (``load_brief_arg``, written to
``<out>/build_brief.json``; its values enter the fingerprint).
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
EXPORT_SCRIPT = HERE / "export.py"           # Milestone 9: the 3D files of the results (.blend packed, .glb)
CANDIDATES = ("/workspace/tools/blender/blender", "/opt/wenart/blender/blender")


class BlenderNotFound(RuntimeError):
    pass


class BlenderFailed(RuntimeError):
    """Blender exited with a non-zero code (``returncode``; 2 = request refused by the script,
    3 = render cut by ``WENART_DEADLINE``, manifest ``incomplete: true``)."""

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


BASE_VARIANT = "base"
VARIANTS_DIR = "variants"


def variant_path(path, variant: str | None = BASE_VARIANT, is_file: bool | None = None) -> Path:
    """Where a variant's output goes by the layout of §1.6b row 9 (pure; a helper for the scheduler and the
    tests: the CLI itself keeps the explicit ``--out`` / ``--scene``): the base keeps ``path``; an alternative
    moves the project folder's subfolder into ``variants/<id>/``: ``outputs/<p>/scene`` ->
    ``outputs/<p>/variants/<id>/scene``, ``outputs/<p>/scene/scene.blend`` ->
    ``outputs/<p>/variants/<id>/scene/scene.blend``. ``is_file`` None: a path with a suffix is a file. A path
    already under ``variants/<id>/`` is returned as it is."""
    p = Path(path)
    if not variant or variant == BASE_VARIANT:
        return p
    parts = p.parts
    for i in range(len(parts) - 1):
        if parts[i] == VARIANTS_DIR and parts[i + 1] == variant:
            return p
    file_like = bool(p.suffix) if is_file is None else is_file
    folder = p.parent if file_like else p
    moved = folder.parent / VARIANTS_DIR / variant / folder.name
    return moved / p.name if file_like else moved


def export_name(name: str, variant: str | None = BASE_VARIANT) -> str:
    """The 3D file stem of a variant: ``<p>`` for the base, ``<p>-<id>`` for an alternative (a name that
    already ends in ``-<id>`` is kept)."""
    if not variant or variant == BASE_VARIANT or str(name).endswith(f"-{variant}"):
        return name
    return f"{name}-{variant}"


BRIEF_FILE = "build_brief.json"


def load_brief_arg(value) -> dict | None:
    """The brief of ``build --brief`` (outside Blender, where PyYAML is): a project folder or its
    ``brief.yaml`` (``wenart.brief.load_brief``: the file over ``defaults.yaml``, the defaults listed as
    assumed), or a JSON file (a ``load_brief`` result or a values dict). None without a value."""
    if not value:
        return None
    import json

    p = Path(value)
    if p.is_dir() or p.suffix in (".yaml", ".yml"):
        from wenart.brief import load_brief

        return load_brief(p if p.is_dir() else p.parent)
    return json.loads(p.read_text(encoding="utf-8"))


def build_fingerprint(building: str, style: str | None = None, assets: str | None = None, level: str | None = None,
                      no_textures: bool = False, preview_samples: int | None = None, proxies: bool = False,
                      camera_policy: str = "m5", lens_mm: float | None = None, variant: str = BASE_VARIANT,
                      brief: dict | None = None) -> str:
    """The fingerprint build.py writes for these arguments (computed without Blender); ``brief``: the
    ``load_brief_arg`` result (its values for the build's keys enter the fingerprint)."""
    import json

    from wenart.blender import build as build_script

    path = Path(building)
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    args = build_script.fingerprint_args(building, style, assets, level, no_textures, preview_samples, False, False,
                                         proxies, camera_policy, lens_mm, variant,
                                         build_script.brief_args(data, brief))
    return build_script.build_fingerprint(args)


def build(building: str, out: str, style: str | None = None, assets: str | None = None, level: str | None = None,
          no_textures: bool = False, preview_samples: int | None = None, timeout: int = 3600,
          proxies: bool = False, reuse: bool = False, camera_policy: str = "m5",
          lens_mm: float | None = None, variant: str = BASE_VARIANT, brief=None) -> Path:
    """Build the scene; returns the path of ``scene_manifest.json``.
    ``proxies`` keeps the Milestone 3 proxy boxes for every furniture piece.
    ``camera_policy``: ``m5`` (default, the fixed rules) or ``search``
    (docs/milestone6.md §4); ``lens_mm``: the brief's lens of every searched
    camera (None: 18 mm, 16 mm in narrow rooms). ``reuse`` skips Blender when the finished build
    in ``out`` has the fingerprint of these inputs (prints ``BUILD_REUSED <fp>``).
    ``variant`` (Milestone 10): the variant to build into the explicit ``out`` (the scheduler picks
    ``outputs/<p>/variants/<id>/scene``); ``brief``: a project folder, its ``brief.yaml`` or a brief JSON
    (``load_brief_arg``), written to ``<out>/build_brief.json`` for the build."""
    loaded = load_brief_arg(brief)
    if reuse:
        from wenart.blender import build as build_script

        fp = build_fingerprint(str(building), str(style) if style else None, str(assets) if assets else None, level,
                               no_textures, preview_samples, proxies, camera_policy, lens_mm, variant, loaded)
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
    args += ["--camera-policy", str(camera_policy)]
    if lens_mm is not None:
        args += ["--lens-mm", f"{float(lens_mm):g}"]
    if variant and variant != BASE_VARIANT:
        args += ["--variant", str(variant)]
    Path(out).mkdir(parents=True, exist_ok=True)
    if loaded is not None:
        import json

        brief_json = Path(out) / BRIEF_FILE
        brief_json.write_text(json.dumps(loaded, indent=1, ensure_ascii=False), encoding="utf-8")
        args += ["--brief", str(brief_json)]
    run_blender(BUILD_SCRIPT, args, log_path=Path(out) / "build.log", timeout=timeout)
    return Path(out) / "scene_manifest.json"


def render(scene: str, out: str, cameras: str = "all", samples: int | None = None, res: str | None = None,
           force: bool = False, device: str = "auto", timeout: int = 7200, hide: str | list | None = None,
           plug: bool = False, hide_sets: str | None = None, look_from: str | None = None,
           exposure: str | float | None = None, white_balance: str | None = None,
           exposure_target: float | None = None, alt_look: str | None = None, max_bounces: int | None = None,
           no_denoise: bool = False, ev_offset: float | None = None, preview_quality: int | None = None,
           variant: str = BASE_VARIANT) -> Path:
    """Render cameras of a built scene; returns the path of ``render_manifest.json``
    (with ``hide_sets`` the folder that holds the ``hide_<id>/`` folders).
    ``exposure`` / ``white_balance`` default to render.py's ``auto``;
    ``look_from`` copies the per-camera look of another render manifest;
    ``hide`` (ids, a list or a comma string) + ``plug`` hide objects for
    every camera; ``hide_sets`` (``'cam:id;cam:id+plug'``) renders controls.
    ``alt_look`` (e.g. ``"None"``, the alternative to Milestone 7's main look
    ``AgX - Punchy``) also saves ``<cam>_alt_preview.jpg``;
    ``max_bounces``, ``no_denoise``, ``ev_offset`` and ``preview_quality``
    are the control flags of docs/milestone6.md §6. A render cut by
    ``WENART_DEADLINE`` raises ``BlenderFailed`` with ``returncode`` 3.
    ``variant`` (Milestone 10): accepted for the scheduler's symmetry; the explicit ``scene`` / ``out`` name
    the variant's files (its scene manifest knows the variant)."""
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
    if alt_look:
        args += ["--alt-look", str(alt_look)]
    if max_bounces is not None:
        args += ["--max-bounces", str(int(max_bounces))]
    if no_denoise:
        args.append("--no-denoise")
    if ev_offset is not None:
        args += ["--ev-offset", str(ev_offset)]
    if preview_quality is not None:
        args += ["--preview-quality", str(int(preview_quality))]
    run_blender(RENDER_SCRIPT, args, blend=str(scene), log_path=Path(out) / "render.log", timeout=timeout)
    return Path(out) if hide_sets else Path(out) / "render_manifest.json"


def export(scene: str, out: str, name: str, renders: str | None = None, max_texture: int | None = None,
           no_glb: bool = False, timeout: int = 1800, variant: str = BASE_VARIANT) -> Path:
    """``<out>/<name>.blend`` (textures packed, scaled to ``max_texture`` px) and ``<out>/<name>.glb`` of a built
    scene (Milestone 9, ``wenart/blender/export.py``); returns the path of ``export_manifest.json``.
    ``variant`` (Milestone 10): the file stem ``<name>-<id>`` (``export_name``); the explicit ``scene``,
    ``renders`` and ``out`` name the variant's files."""
    name = export_name(name, variant)
    args = ["--out", str(out), "--name", str(name)]
    if renders:
        args += ["--renders", str(renders)]
    if max_texture is not None:
        args += ["--max-texture", str(int(max_texture))]
    if no_glb:
        args.append("--no-glb")
    Path(out).mkdir(parents=True, exist_ok=True)
    run_blender(EXPORT_SCRIPT, args, blend=str(scene), log_path=Path(out) / "export.log", timeout=timeout)
    return Path(out) / "export_manifest.json"


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
    b.add_argument("--camera-policy", default="m5", choices=["m5", "search"],
                   help="m5 = the fixed Milestone 3-5 camera rules (default); search = ray-cast camera search")
    b.add_argument("--lens-mm", type=float, default=None,
                   help="lens of every searched camera (the brief's render.lens_mm, 14-35 mm); default 18 mm, "
                        "16 mm in rooms narrower than 2.2 m")
    variant_help = "building variant (Milestone 10): base (default) or an alternative's id; --out / --scene stay " \
                   "explicit (outputs/<p>/variants/<id>/... for an alternative)"
    b.add_argument("--variant", default=BASE_VARIANT, help=variant_help)
    b.add_argument("--brief", help="the project brief (Milestone 10): the project folder, its brief.yaml or a brief "
                                   "JSON; default: the building's stored brief and the defaults")
    r = sub.add_parser("render", help="render cameras of a built scene with Cycles")
    r.add_argument("--variant", default=BASE_VARIANT, help=variant_help)
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
    r.add_argument("--alt-look", help="also save <cam>_alt_preview.jpg with this AgX look (e.g. 'None'; "
                                      "the main look is 'AgX - Punchy' since Milestone 7)")
    r.add_argument("--max-bounces", type=int,
                   help="N indirect diffuse/glossy/volume bounces (0 = direct light only; a control); window "
                        "glass still transmits (transmission and total bounces >= 2)")
    r.add_argument("--no-denoise", action="store_true", help="no denoiser (a control)")
    r.add_argument("--ev-offset", type=float, help="stops added to the auto, fixed or --look-from EV")
    r.add_argument("--preview-quality", type=int, help="fixed JPEG quality of the previews, no size step-down")
    e = sub.add_parser("export", help="the 3D files of a built scene: <name>.blend (packed) and <name>.glb")
    e.add_argument("--scene", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--name", required=True)
    e.add_argument("--renders", help="render_manifest.json: the cameras' metered exposure and white point")
    e.add_argument("--max-texture", type=int, help="scale textures down to this many px (default 1024; 0 = none)")
    e.add_argument("--no-glb", action="store_true")
    e.add_argument("--variant", default=BASE_VARIANT, help=variant_help + "; the files are named <name>-<id>")
    sub.add_parser("which", help="print the Blender binary that would be used")
    ns = parser.parse_args(argv)
    try:
        if ns.command == "which":
            path = find_blender()
            print(path or "")
            return 0 if path else 1
        if ns.command == "build":
            path = build(ns.building, ns.out, ns.style, ns.assets, ns.level, ns.no_textures, ns.preview_samples,
                         proxies=ns.proxies, reuse=ns.reuse, camera_policy=ns.camera_policy, lens_mm=ns.lens_mm,
                         variant=ns.variant, brief=ns.brief)
        elif ns.command == "export":
            path = export(ns.scene, ns.out, ns.name, ns.renders, ns.max_texture, ns.no_glb, variant=ns.variant)
        else:
            path = render(ns.scene, ns.out, ns.cameras, ns.samples, ns.res, ns.force, ns.device, hide=ns.hide,
                          plug=ns.plug, hide_sets=ns.hide_sets, look_from=ns.look_from, exposure=ns.exposure,
                          white_balance=ns.white_balance, exposure_target=ns.exposure_target, alt_look=ns.alt_look,
                          max_bounces=ns.max_bounces, no_denoise=ns.no_denoise, ev_offset=ns.ev_offset,
                          preview_quality=ns.preview_quality, variant=ns.variant)
    except BlenderFailed as exc:
        print(f"error: {exc}", file=sys.stderr)
        # 2 = refused request, 3 = cut by WENART_DEADLINE (the orchestrator reads both).
        return exc.returncode if exc.returncode in (2, 3) else 1
    except (BlenderNotFound, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
