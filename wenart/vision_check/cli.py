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

Realism A/B (docs/milestone6.md §6, ``wenart.vision_check.realism``; these
read no scene of the project, only its ``ab/`` folder):

- ``realism-pairs [--controls]``: ``ab/pairs.json`` from the files under
  ``--project-out`` (``--controls``: also the control sets of the control
  project, and their ``null_reencode`` files); exit 1 when the AB render
  manifest or ``ab/cameras_check.json`` is missing or no pair could be made;
- ``realism --model-key ... --server ... [--sets s,...] [--skip-sets s,...]``:
  every pair in both orders, sets in the order of §6.2, into
  ``check/realism/answers_<slug>.json`` (resumable; exit 1 without
  ``ab/pairs.json``);
- ``realism-combine [--models qwen,glm]``: ``check/realism/realism_ab.json``,
  ``realism_report.md``, ``contact_realism_<set>_<n>.jpg`` (no decision);
- ``realism-summary --project-outs OUT [OUT ...] --controls-project <p>
  --out DIR``: ``DIR/realism_summary.json`` and ``.md`` with the decision per
  set and aspect (``--project-out`` is not used; exit 1 when no project has
  a ``realism_ab.json``).

``--deadline`` (default env ``WENART_DEADLINE``, epoch seconds): ``run``,
``preference``, ``realism`` and ``style-photo`` start no new call after it
and wait for no call past it (a call still running is left for the next
run), mark their file ``incomplete`` and exit 0. ``run``, ``preference`` and
``realism`` send ``--workers`` calls at once (default ``check.yaml:
calls.workers``, 2).
``main(argv=None, client_factory=None)``:
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
from wenart.vision_check import realism as RZ
from wenart.vision_check import report as R
from wenart.vision_check.project import CONTROLS_JSON, EXPECTED_JSON, Project, read_json, rel, sha256_file, write_json

DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
MANIFEST = "check_manifest.json"
CALIBRATION = "check_calibration.json"
REPORT = "check_report.md"
REALISM_COMMANDS = ("realism-pairs", "realism", "realism-combine", "realism-summary")


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
                                            "combine", "calibrate", "style-photo", *REALISM_COMMANDS])
    parser.add_argument("--project-out", help="outputs/<project> (every command but realism-summary)")
    parser.add_argument("--render-dir", help="render folder (default <project-out>/renders)")
    parser.add_argument("--model-key", help="qwen | glm (check.yaml models)")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"vLLM base URL (default {DEFAULT_SERVER})")
    parser.add_argument("--kinds", help="run: cycles,polished,controls,plan_ab (default cycles,polished); "
                                        "preference: polished|sweep (default polished)")
    parser.add_argument("--models", help="combine, realism-combine, realism-summary: model keys "
                                         "(default CHECK_MODELS, else 'qwen glm')")
    parser.add_argument("--deadline", type=float, default=None, help="epoch seconds (default env WENART_DEADLINE)")
    parser.add_argument("--max-side", type=int, default=None, help="longest image side sent (default: the client's)")
    parser.add_argument("--workers", type=int, default=None,
                        help="run/preference/realism: calls at once (default check.yaml calls.workers)")
    parser.add_argument("--photo", action="append", default=[], help="style-photo: photo file (repeatable)")
    parser.add_argument("--out", help="style-photo: output JSON (default <project-out>/check/style_photos.json); "
                                      "realism-summary: output folder ($RESULTS/realism)")
    parser.add_argument("--no-debug", action="store_true", help="combine: no debug images; realism-combine: no "
                                                                "contact sheets")
    parser.add_argument("--controls", action="store_true",
                        help="realism-pairs: also the control sets (the --ab-controls project)")
    parser.add_argument("--sets", help=f"realism: only these sets (comma list of {', '.join(RZ.SET_ORDER)})")
    parser.add_argument("--skip-sets", help="realism: leave these sets out (e.g. look_alt near the deadline)")
    parser.add_argument("--project-outs", nargs="+", default=[],
                        help="realism-summary: the project outputs of every A/B project (space or comma separated)")
    parser.add_argument("--controls-project", help="realism-summary: the control project (name or output folder)")
    args = parser.parse_args(argv)
    if args.command != "realism-summary" and not args.project_out:
        parser.error(f"{args.command}: --project-out is required")
    if args.command == "realism-summary" and not (args.project_outs and args.out):
        parser.error("realism-summary: --project-outs and --out are required")
    return args


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
    return _client_for(project.cfg, args, client_factory)


def _client_for(cfg: dict, args, client_factory):
    """The client of ``--model-key`` at ``--server`` for the check config ``cfg`` (UsageError for a bad key)."""
    models = cfg["models"]
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
    workers = args.workers or int((project.cfg.get("calls") or {}).get("workers", 1))
    stats = C.run_specs(specs, store, client, deadline=deadline, max_side=args.max_side, workers=workers)
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
    print(f"vision_check calibrate: advisory={cal['advisory']} ({len(cal['missed'])} target(s) missed), plan A/B: "
          f"{cal['plan_ab']['text']} -> {project.check_dir / CALIBRATION}")
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


def style_call_error(result) -> Optional[str]:
    """The error of a ``read_style_photo`` result: None only when every pass has an answer.

    ``read_style_photo`` never raises for a transport problem or a bad answer:
    it returns the pass with ``data: null`` and its error, so the call is
    judged by its passes (a failed call is asked again on the next run).
    """
    passes = result.get("passes") if isinstance(result, dict) else None
    if isinstance(passes, dict):
        passes = list(passes.values())
    passes = [p for p in passes or [] if isinstance(p, dict)]
    if not passes:
        return "no pass in the result"
    failed = [p for p in passes if p.get("error") or not isinstance(p.get("data"), dict)]
    return "; ".join(f"{p.get('model_key') or '?'}: {p.get('error') or 'no answer'}" for p in failed) or None


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
    client = C.bound_client(_client(project, args, client_factory), deadline)
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
                     and c.get("sha256") == sha and c.get("model") == model and not c.get("error")
                     and style_call_error(c.get("result")) is None), None)
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
                # Waited for until the deadline only: a wedged server cannot hold the job past it.
                answered, result = C.call_before_deadline(
                    lambda photo=photo: read_style_photo(photo, {args.model_key: client}), deadline)
                if not answered:
                    data["incomplete"] = True
                    print(f"vision_check style-photo [{args.model_key}]: {photo.name}: deadline reached before "
                          "the answer; left for the next run")
                    break
                rec["result"] = jsonable(result)
                rec["error"] = style_call_error(rec["result"])
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


# --------------------------------------------------------------------------
# Realism A/B (docs/milestone6.md §6)
# --------------------------------------------------------------------------

def _split(values) -> list[str]:
    return [v for text in values or [] for v in str(text).replace(",", " ").split() if v]


def cmd_realism_pairs(args) -> int:
    out = Path(args.project_out).resolve()
    try:
        doc = RZ.build_pairs(out, controls=args.controls)
    except FileNotFoundError as exc:
        print(f"vision_check realism-pairs: {exc}", file=sys.stderr)
        return 1
    path = write_json(out / RZ.PAIRS_JSON, doc)
    sets = ", ".join(f"{s} {n}" for s, n in doc["sets"].items()) or "none"
    print(f"vision_check realism-pairs: {len(doc['pairs'])} pair(s) ({sets}), {len(doc['dropped'])} dropped "
          f"camera(s), {len(doc['skipped'])} skipped pair(s) -> {path}")
    for w in doc["warnings"]:
        print(f"vision_check realism-pairs: warning: {w}")
    return 0 if doc["pairs"] else 1


def cmd_realism(args, client_factory) -> int:
    from wenart.vision_check.config import load_config
    out = Path(args.project_out).resolve()
    cfg = load_config()
    sets = RZ.select_sets(args.sets, args.skip_sets)
    pairs_doc = read_json(out / RZ.PAIRS_JSON)
    if pairs_doc is None:
        print(f"vision_check realism: no {RZ.PAIRS_JSON.as_posix()} in {out} (run realism-pairs first)",
              file=sys.stderr)
        return 1
    deadline = deadline_of(args.deadline)
    client = _client_for(cfg, args, client_factory)
    model = str(client.model)
    slug = cfg["models"][args.model_key]["slug"]
    store = C.AnswerStore(RZ.answers_path(out, slug), args.model_key, slug, model)
    warnings: list[str] = []
    specs = RZ.realism_specs(out, pairs_doc, model, sets=sets, warnings=warnings)
    workers = args.workers or int((cfg.get("calls") or {}).get("workers", 1))
    stats = C.run_specs(specs, store, RZ.RealismClient(client), deadline=deadline, max_side=args.max_side,
                        workers=workers)
    asked = sorted({s.image_kind for s in specs}, key=RZ.SET_ORDER.index)
    print(f"vision_check realism [{args.model_key}]: {len(specs)} call(s) in {len(asked)} set(s): {stats['asked']} "
          f"asked ({stats['failed']} failed), {stats['reused']} reused, {stats['left']} left"
          f"{' (deadline: incomplete)' if stats['incomplete'] else ''} -> {store.path}")
    for w in warnings:
        print(f"vision_check realism: warning: {w}")
    return 0


def cmd_realism_combine(args) -> int:
    out = Path(args.project_out).resolve()
    keys = CB.model_keys(args.models)
    try:
        doc = RZ.combine(out, keys)
    except FileNotFoundError as exc:
        print(f"vision_check realism-combine: {exc}", file=sys.stderr)
        return 1
    path = RZ.write_combine(out, doc, sheets=not args.no_debug)
    sets = ", ".join(f"{s} {st['pairs']}" for s, st in doc["sets"].items()) or "none"
    answered = sum(c["answered"] for c in doc["calls"])
    expected = sum(c["expected"] for c in doc["calls"])
    print(f"vision_check realism-combine [{', '.join(keys)}]: {len(doc['rows'])} pair(s) ({sets}), {answered}/"
          f"{expected} call(s) answered, {sum(len(v) for v in doc['contact_sheets'].values())} contact sheet(s)"
          f"{', controls table' if doc['controls'] else ''} -> {path}")
    for w in doc["warnings"]:
        print(f"vision_check realism-combine: warning: {w}")
    return 0


def cmd_realism_summary(args) -> int:
    keys = CB.model_keys(args.models)
    outs = _split(args.project_outs)
    summary = RZ.summarise(outs, args.controls_project, keys)
    path = RZ.write_summary(Path(args.out), summary)
    decisions = ", ".join(f"{s} {st['decision']}" for s, st in summary["sets"].items()) or "no A/B set"
    signal = ", ".join(f"{k} {'yes' if ok else 'no'}" for k, ok in summary["signal"].items())
    print(f"vision_check realism-summary: {decisions} (signal: {signal}"
          f"{'; single_model' if summary['single_model'] else ''}) -> {path}")
    for w in summary["warnings"]:
        print(f"vision_check realism-summary: warning: {w}")
    return 0 if any(p["found"] for p in summary["projects"]) else 1


def main(argv=None, client_factory=None) -> int:
    args = parse_args(argv)
    if args.command in REALISM_COMMANDS:
        try:
            if args.command == "realism-pairs":
                return cmd_realism_pairs(args)
            if args.command == "realism":
                return cmd_realism(args, client_factory)
            if args.command == "realism-combine":
                return cmd_realism_combine(args)
            return cmd_realism_summary(args)
        except C.UsageError as exc:
            print(f"vision_check {args.command}: {exc}", file=sys.stderr)
            return 2
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
