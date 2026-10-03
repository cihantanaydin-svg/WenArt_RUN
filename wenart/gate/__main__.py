"""CLI of the change gate (docs/milestone5.md §4).

``python -m wenart.gate calibrate --project-out outputs/<p> [--out DIR] [--views N|cam,...] [--deadline S]``
    benign and negative controls, rates and threshold proposals
    (``gate/gate_calibration.json`` + ``.md``; see ``wenart.gate.calibrate``).
``python -m wenart.gate validate --project-out outputs/<p> [--out DIR] [--config validation.yaml]``
    per-project validation of that calibration (docs/milestone6.md §7.3):
    ``gate/gate_validation.json`` with the decision ``ok | flagged |
    polish_disabled | not_validated`` (see ``wenart.gate.validate``); exit 0
    whenever the file was written.
``python -m wenart.gate compare --render-dir outputs/<p>/renders --camera CAM --test polished.png
[--debug out.jpg] [--json out.json]``
    one comparison of an image with a rendered view (prints the decision and
    the reasons; exit 0 for accept, 1 for reject).
``python -m wenart.gate detect <out> --manifest <out>/polish/polish_manifest.json --out <out>/detect/
[--no-controls] [--force] [--deadline S] [--device cuda]``
    OWLv2 boxes of the Cycles render and the chosen polish attempt of every
    polished view, and of the hidden render of every control of
    ``check/controls.json`` (docs/milestone7.md §8.1, ``wenart.gate.detect``):
    ``detect/<cam>.json`` + ``detect/detect_manifest.json``; reused per image
    while its detection key holds. Exit 0 when the manifest was written
    (also when the polish was not allowed or the deadline cut it), 1 without
    the polish manifest.
``python -m wenart.gate detect-calibrate (--pairs <list.json> | --project-outs OUT [OUT ...]) --out DIR
[--pairs-only] [--cache DIR] [--device cuda]``
    the detector thresholds: with ``--project-outs`` the pair list is built
    from those outputs (the M6 insertion controls, accepted polishes and
    benign perturbations) and written to ``DIR/detect_pairs.json``
    (``--pairs-only``: stop there, no model); then ``DIR/detector_calibration.json``
    with ``t_det``, ``t_strong``, the rates and ``check_yaml_block`` (copy it
    into ``check.yaml detector:`` only when ``usable``). Exit 0 when written,
    1 without any pair.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _detector(args, detector):
    if detector is not None:
        return detector
    from wenart.gate.models import Detector
    return Detector(device=args.device)


def _deadline(value):
    import os
    if value is not None:
        return float(value)
    env = os.environ.get("WENART_DEADLINE", "").strip()
    return float(env) if env else None


def run_detect_command(args, detector=None) -> int:
    from wenart.gate import detect as D
    out = Path(args.out_dir)
    manifest = Path(args.manifest) if args.manifest else out / "polish" / "polish_manifest.json"
    if not manifest.is_file():
        print(f"gate detect: no polish manifest at {manifest}", file=sys.stderr)
        return 1
    det_dir = Path(args.out) if args.out else out / D.DETECT_DIR
    doc = D.run_detect(out, manifest, det_dir, _detector(args, detector), controls=not args.no_controls,
                       deadline=_deadline(args.deadline), force=args.force)
    if doc.get("skipped"):
        print(f"gate detect: skipped: {doc['skipped']}")
    for w in doc.get("warnings") or []:
        print(f"gate detect: warning: {w}")
    return 0


def run_calibrate_command(args, detector=None) -> int:
    from wenart.gate import detect as D
    out = Path(args.out)
    if args.pairs:
        pairs = D.read_json(Path(args.pairs))
        if pairs is None:
            print(f"gate detect-calibrate: no pair list at {args.pairs}", file=sys.stderr)
            return 1
    else:
        outs = [v for text in args.project_outs for v in str(text).replace(",", " ").split() if v]
        pairs = D.build_pairs(outs)
        D.write_json(out / D.PAIRS_JSON, pairs)
        print(f"gate detect-calibrate: {len(pairs['pairs'])} pair(s) {pairs['counts']} -> {out / D.PAIRS_JSON}")
        for w in pairs["warnings"]:
            print(f"gate detect-calibrate: warning: {w}")
    if not pairs.get("pairs"):
        print("gate detect-calibrate: no calibration pair", file=sys.stderr)
        return 1
    if args.pairs_only:
        return 0
    D.run_calibration(pairs, out, _detector(args, detector), cache_dir=args.cache)
    return 0


def main(argv=None, gate=None, expected_api=None, detector=None) -> int:
    from wenart.gate import calibrate, validate

    parser = argparse.ArgumentParser(prog="python -m wenart.gate", description="change gate (milestones 5 to 7)")
    sub = parser.add_subparsers(dest="command", required=True)
    cal = sub.add_parser("calibrate", help="benign/negative controls and threshold proposals for one project")
    calibrate.add_arguments(cal)
    val = sub.add_parser("validate", help="decide from the project's calibration whether its polish may run")
    validate.add_arguments(val)
    cmp_ = sub.add_parser("compare", help="compare one image with a rendered view")
    cmp_.add_argument("--render-dir", required=True, help="folder with render_manifest.json")
    cmp_.add_argument("--camera", required=True)
    cmp_.add_argument("--test", required=True, help="image to compare (render size)")
    cmp_.add_argument("--debug", default=None, help="write the debug JPEG here")
    cmp_.add_argument("--json", default=None, help="write the result JSON here")
    cmp_.add_argument("--device", default="cuda")
    cmp_.add_argument("--thresholds", default=None, help="thresholds.yaml (default: the package one)")
    det = sub.add_parser("detect", help="OWLv2 boxes of the Cycles and the polished images (M7 §8.1)")
    det.add_argument("out_dir", metavar="OUT", help="the project output (outputs/<p>)")
    det.add_argument("--manifest", default=None, help="polish manifest (default OUT/polish/polish_manifest.json)")
    det.add_argument("--out", default=None, help="output folder (default OUT/detect)")
    det.add_argument("--no-controls", action="store_true", help="leave out the control renders")
    det.add_argument("--force", action="store_true", help="detect every image again")
    det.add_argument("--deadline", type=float, default=None, help="epoch seconds (default env WENART_DEADLINE)")
    det.add_argument("--device", default="cuda")
    dcal = sub.add_parser("detect-calibrate", help="detector thresholds from insertion controls and accepted polishes")
    src = dcal.add_mutually_exclusive_group(required=True)
    src.add_argument("--pairs", default=None, help="a pair list (detect_pairs.json)")
    src.add_argument("--project-outs", nargs="+", default=None, help="build the pair list from these outputs")
    dcal.add_argument("--out", required=True, help="output folder ($RESULTS/detect)")
    dcal.add_argument("--pairs-only", action="store_true", help="write the pair list only (no model)")
    dcal.add_argument("--cache", default=None, help="box cache per image (default DIR/boxes; outside the results "
                                                    "folder on the pod, e.g. /workspace/cache/detect)")
    dcal.add_argument("--device", default="cuda")
    args = parser.parse_args(argv)

    if args.command == "calibrate":
        return calibrate.run_from_args(args, gate=gate, expected_api=expected_api)
    if args.command == "validate":
        return validate.run_from_args(args)
    if args.command == "detect":
        return run_detect_command(args, detector)
    if args.command == "detect-calibrate":
        return run_calibrate_command(args, detector)

    from wenart import views as V
    from wenart.gate.api import Gate

    gate = gate if gate is not None else Gate(thresholds=args.thresholds, device=args.device)
    view = V.load_views(args.render_dir, [args.camera])[args.camera]
    ref = gate.prepare(view, view.read_rgb())
    test = V.read_rgb(args.test)
    result = gate.compare(ref, test)
    if args.debug:
        gate.write_debug(ref, test, result, args.debug)
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"GATE {args.camera} {result['decision']} key {result['gate_key']}")
    for r in result["reasons"]:
        print(f"  reason {r['check']} {r['region']}: {r['value']} (limit {r['op']} {r['threshold']})")
    for r in result["notes"]:
        print(f"  note   {r['check']} {r['region']}: {r['value']} (limit {r['op']} {r['threshold']})")
    return 0 if result["decision"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
