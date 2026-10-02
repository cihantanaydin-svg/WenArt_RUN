"""CLI of the final vision check (docs/milestone5.md §5.7).

    python -m wenart.vision_check <subcommand> --project-out outputs/<p> [options]

Subcommands (in job order):

- ``expected``: ``check/expected_views.json`` (expected elements, roles,
  JSON cross-check) of every Cycles view;
- ``plan-crops``: ``check/<cam>_plan.jpg`` + ``check/plan_crops.json``;
- ``select-controls``: ``check/controls.json``; prints
  ``CONTROL\\t<id>\\t<camera>\\t<0|1>\\t<dir>`` per control and one
  ``HIDE_SETS\\t<cam:id[+plug];...>`` line for ``wenart.blender.cli render --hide-sets``;
- ``run --model-key qwen|glm --server URL [--kinds cycles,polished,controls,plan_ab]``:
  the element checks of one model into ``check/answers_<slug>.json``
  (resumable, rewritten after every call);
- ``preference --model-key ... --server ... [--kinds polished|sweep]``: the
  realism preference, both orders, same answers file;
- ``style-photo --model-key ... --server ... [--photo PATH ...] [--out PATH]``:
  one pass of ``wenart.style.photos.read_style_photo`` with this server's
  model per style photo, appended to ``<out>.json`` (default
  ``check/style_photos.json``);
- ``combine [--models qwen,glm]``: ``check/check_manifest.json``, the
  ``<cam>_<kind>_check.jpg`` debug images and ``check_report.md``
  (models default to ``CHECK_MODELS``, else ``qwen glm``);
- ``calibrate``: ``check/check_calibration.json``; copies ``advisory`` into
  the manifest and rewrites the report.

``--deadline`` (default env ``WENART_DEADLINE``, epoch seconds): ``run``,
``preference`` and ``style-photo`` start no new call after it, mark their
file ``incomplete`` and exit 0. ``main(argv=None, client_factory=None)``:
``client_factory(model_key, base_url)`` returns an object with ``.model``
and ``.run_schema`` (default: ``wenart.vision_check.config.client_factory``).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

from wenart.vision_check import calibrate as CAL
from wenart.vision_check import calls as C
from wenart.vision_check import combine as CB
from wenart.vision_check import controls as CT
from wenart.vision_check import report as R
from wenart.vision_check.project import CONTROLS_JSON, EXPECTED_JSON, Project, read_json, rel, sha256_file, write_json

DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
MANIFEST = "check_manifest.json"
CALIBRATION = "check_calibration.json"
REPORT = "check_report.md"


def deadline_of(value: Optional[float]) -> Optional[float]:
    """``--deadline`` or the ``WENART_DEADLINE`` env (epoch seconds), None when neither is set."""
    if value is not None:
        return float(value)
    env = os.environ.get("WENART_DEADLINE", "").strip()
    return float(env) if env else None


def _kinds(text: str) -> list[str]:
    return [k.strip() for k in text.split(",") if k.strip()]


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.vision_check",
                                     description="final vision check of the renders (docs/milestone5.md §5)")
    parser.add_argument("command", choices=["expected", "plan-crops", "select-controls", "run", "preference",
                                            "combine", "calibrate", "style-photo"])
    parser.add_argument("--project-out", required=True, help="outputs/<project>")
    parser.add_argument("--render-dir", help="render folder (default <project-out>/renders)")
    parser.add_argument("--model-key", help="qwen | glm (check.yaml models)")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"vLLM base URL (default {DEFAULT_SERVER})")
    parser.add_argument("--kinds", help="run: cycles,polished,controls,plan_ab (default cycles,polished); "
                                        "preference: polished|sweep (default polished)")
    parser.add_argument("--models", help="combine: model keys (default CHECK_MODELS, else 'qwen glm')")
    parser.add_argument("--deadline", type=float, default=None, help="epoch seconds (default env WENART_DEADLINE)")
    parser.add_argument("--max-side", type=int, default=None, help="longest image side sent (default: the client's)")
    parser.add_argument("--photo", action="append", default=[], help="style-photo: photo file (repeatable)")
    parser.add_argument("--out", help="style-photo: output JSON (default <project-out>/check/style_photos.json)")
    parser.add_argument("--no-debug", action="store_true", help="combine: no debug images")
    return parser.parse_args(argv)


# --------------------------------------------------------------------------
# Subcommands
# --------------------------------------------------------------------------

def cmd_expected(project: Project, args) -> int:
    exp = project.expected_all()
    data = {"schema_version": "0.1", "project": project.project,
            "render_dir": rel(project.render_dir, project.check_dir), "views": exp, "warnings": list(project.warnings)}
    path = write_json(project.check_dir / EXPECTED_JSON, data)
    req = sum(1 for v in exp.values() for e in v["elements"] if e["role"] == "required")
    cc = sum(len(v["json_crosscheck"].get(k) or []) for v in exp.values()
             for k in ("in_json_not_rendered", "misplaced", "rendered_not_in_json"))
    print(f"vision_check expected: {len(exp)} views, {req} required elements, {cc} cross-check finding(s) -> {path}")
    for w in project.warnings:
        print(f"vision_check expected: warning: {w}")
    return 0 if exp else 1


def cmd_plan_crops(project: Project, args) -> int:
    from wenart.vision_check.plan_crop import write_plan_crops
    out = write_plan_crops(project)
    made = sum(1 for v in out["views"].values() if v.get("plan"))
    print(f"vision_check plan-crops: {made} of {len(out['views'])} views -> {project.check_dir}")
    return 0


def cmd_select_controls(project: Project, args) -> int:
    selection = CT.select_controls(project.expected_all(), project.cfg)
    selection["project"] = project.project
    selection["hide_sets"] = CT.hide_sets(selection)
    path = write_json(project.check_dir / CONTROLS_JSON, selection)
    for line in CT.control_lines(selection):
        print(line)
    print(f"HIDE_SETS\t{selection['hide_sets']}")
    print(f"vision_check select-controls: {len(selection['controls'])} control(s), {len(selection['swaps'])} "
          f"swap(s) -> {path}", file=sys.stderr)
    return 0


def _client(project: Project, args, client_factory):
    """The client of ``--model-key`` at ``--server`` (UsageError for a missing or unknown key)."""
    models = project.cfg["models"]
    if not args.model_key or args.model_key not in models:
        raise C.UsageError(f"--model-key must be one of {', '.join(models)} (got {args.model_key!r})")
    factory = client_factory
    if factory is None:
        from wenart.vision_check.config import client_factory as factory
    return factory(args.model_key, args.server)


def _store(project: Project, key: str, model: str) -> C.AnswerStore:
    models = project.cfg["models"]
    if key not in models:
        raise C.UsageError(f"model key {key!r} not in check.yaml (known: {', '.join(models)})")
    slug = models[key]["slug"]
    return C.AnswerStore(C.answers_path(project.check_dir, slug), key, slug, model)


def _run(project: Project, args, client_factory, check: list, prefs: list, what: str) -> int:
    deadline = deadline_of(args.deadline)
    client = _client(project, args, client_factory)
    model = str(client.model)
    store = _store(project, args.model_key, model)
    specs = C.build_specs(project, check, prefs, model)
    stats = C.run_specs(specs, store, client, deadline=deadline, max_side=args.max_side)
    print(f"vision_check {what} [{args.model_key}]: {len(specs)} call(s): {stats['asked']} asked "
          f"({stats['failed']} failed), {stats['reused']} reused, {stats['left']} left"
          f"{' (deadline: incomplete)' if stats['incomplete'] else ''} -> {store.path}")
    for w in project.warnings:
        print(f"vision_check {what}: warning: {w}")
    return 0


def cmd_run(project: Project, args, client_factory) -> int:
    kinds = _kinds(args.kinds or "cycles,polished")
    return _run(project, args, client_factory, C.check_kinds(project, kinds), [], "run")


def cmd_preference(project: Project, args, client_factory) -> int:
    kinds = _kinds(args.kinds or "polished")
    return _run(project, args, client_factory, [], C.preference_kinds(project, kinds), "preference")


def write_outputs(project: Project, manifest: dict, calibration: Optional[dict], debug: bool) -> None:
    """Manifest, debug images and report of ``combine`` / ``calibrate``."""
    write_json(project.check_dir / MANIFEST, manifest)
    if debug:
        from wenart.vision_check.debug import write_check_image
        for cam, kinds in manifest["views"].items():
            for kind, entry in kinds.items():
                if not isinstance(entry, dict) or "verdict" not in entry or entry.get("preference_only"):
                    continue
                image = project.check_dir / entry["images"][0]
                if image.is_file():
                    write_check_image(image, entry, cam, kind,
                                      project.check_dir / f"{cam}_{C.kind_slug(kind)}_check.jpg")
    expected = {cam: project.expected(cam) for cam in manifest["views"] if cam in project.views()}
    (project.check_dir / REPORT).write_text(R.check_report(manifest, calibration, expected), encoding="utf-8")


def cmd_combine(project: Project, args) -> int:
    keys = CB.model_keys(args.models)
    manifest = CB.combine_project(project, keys)
    if not manifest["views"]:
        print(f"vision_check combine: no current views in {project.render_dir} ({'; '.join(project.warnings)})",
              file=sys.stderr)
        return 1
    write_outputs(project, manifest, None, not args.no_debug)
    verdicts = {}
    for v in manifest["views"].values():
        verdict = (v.get("cycles") or {}).get("verdict", "-")
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
    rejected = sum(1 for v in manifest["views"].values() if v.get("polished_rejected"))
    print(f"vision_check combine [{', '.join(keys)}]: {len(manifest['views'])} views, Cycles verdicts {verdicts}, "
          f"{rejected} polished rejected -> {project.check_dir / MANIFEST}")
    return 0


def cmd_calibrate(project: Project, args) -> int:
    manifest = read_json(project.check_dir / MANIFEST)
    if manifest is None:
        print(f"vision_check calibrate: no {MANIFEST} (run combine first)", file=sys.stderr)
        return 2
    cal = CAL.calibrate(manifest, project.cfg)
    write_json(project.check_dir / CALIBRATION, cal)
    manifest["advisory"] = cal["advisory"]
    manifest["advisory_reason"] = "; ".join(cal["advisory_reasons"]) or None
    write_outputs(project, manifest, cal, debug=False)
    print(f"vision_check calibrate: advisory={cal['advisory']} ({len(cal['missed'])} target(s) missed), plan A/B "
          f"{'adopted' if cal['plan_ab']['adopted'] else 'not adopted'} -> {project.check_dir / CALIBRATION}")
    return 0


def style_photos(project: Project, args) -> list[Path]:
    """``--photo`` files, else the brief's ``style_photos`` in ``<project>/style_photos/``, else every image
    there (the rule and file types of ``wenart.style.photos.style_photo_paths``). A listed photo that is
    missing stays in the list, so its call is recorded as ``photo not found`` instead of vanishing."""
    if args.photo:
        return [Path(p) for p in args.photo]
    from wenart.style.photos import PHOTO_DIR, style_photo_paths
    brief = project.paths.get("brief")
    brief = brief if isinstance(brief, dict) else None
    names = list(((brief or {}).get("values") or {}).get("style_photos") or [])
    if names:
        return [project.project_dir / PHOTO_DIR / str(n) for n in names]
    return style_photo_paths(project.project_dir, brief)[0]


def jsonable(value):
    """``value`` as plain JSON data (objects with ``to_dict()`` such as ``VLMResult`` are converted, others to text)."""
    def default(obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if isinstance(obj, Path):
            return obj.as_posix()
        return str(obj)
    return json.loads(json.dumps(value, default=default, ensure_ascii=False))


def cmd_style_photo(project: Project, args, client_factory) -> int:
    out = Path(args.out) if args.out else project.check_dir / "style_photos.json"
    if out.suffix != ".json":
        out = out.with_name(out.name + ".json")
    data = read_json(out) or {"schema_version": "0.1", "kind": "style_photo_passes", "calls": []}
    data["incomplete"] = False
    photos = style_photos(project, args)
    if not photos:
        print("vision_check style-photo: no style photos")
        write_json(out, data)
        return 0
    deadline = deadline_of(args.deadline)
    client = _client(project, args, client_factory)
    model = str(client.model)
    slug = project.cfg["models"][args.model_key]["slug"]
    try:
        from wenart.style.photos import read_style_photo
    except ImportError as exc:
        read_style_photo = None
        missing = f"wenart.style.photos is not available ({exc})"
    for photo in photos:
        if deadline is not None and time.time() >= deadline:
            data["incomplete"] = True
            print("vision_check style-photo: deadline reached")
            break
        sha = sha256_file(photo) if photo.is_file() else None
        name = rel(photo, out.parent)
        done = next((c for c in data["calls"] if c.get("file") == name and c.get("model_key") == args.model_key
                     and c.get("sha256") == sha and c.get("model") == model and not c.get("error")), None)
        if done is not None:
            continue
        rec = {"file": name, "sha256": sha, "model_key": args.model_key, "model": model, "slug": slug,
               "result": None, "error": None, "seconds": None}
        t0 = time.time()
        if sha is None:
            rec["error"] = "photo not found"
        elif read_style_photo is None:
            rec["error"] = missing
        else:
            try:
                rec["result"] = jsonable(read_style_photo(photo, {args.model_key: client}))
            except Exception as exc:  # noqa: BLE001 - recorded, never silently dropped
                rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["seconds"] = round(time.time() - t0, 2)
        data["calls"] = [c for c in data["calls"]
                         if not (c.get("file") == name and c.get("model_key") == args.model_key)]
        data["calls"].append(rec)
        write_json(out, data)
        print(f"vision_check style-photo [{args.model_key}]: {photo.name}: {rec['error'] or 'ok'}")
    write_json(out, data)
    return 0


def main(argv=None, client_factory=None) -> int:
    args = parse_args(argv)
    project = Project(args.project_out, render_dir=args.render_dir)
    try:
        if args.command == "expected":
            return cmd_expected(project, args)
        if args.command == "plan-crops":
            return cmd_plan_crops(project, args)
        if args.command == "select-controls":
            return cmd_select_controls(project, args)
        if args.command == "run":
            return cmd_run(project, args, client_factory)
        if args.command == "preference":
            return cmd_preference(project, args, client_factory)
        if args.command == "style-photo":
            return cmd_style_photo(project, args, client_factory)
        if args.command == "combine":
            return cmd_combine(project, args)
        return cmd_calibrate(project, args)
    except C.UsageError as exc:
        print(f"vision_check {args.command}: {exc}", file=sys.stderr)
        return 2
