"""CLI of the change gate (docs/milestone5.md §4).

``python -m wenart.gate calibrate --project-out outputs/<p> [--out DIR] [--views N|cam,...] [--deadline S]``
    benign and negative controls, rates and threshold proposals
    (``gate/gate_calibration.json`` + ``.md``; see ``wenart.gate.calibrate``).
``python -m wenart.gate compare --render-dir outputs/<p>/renders --camera CAM --test polished.png
[--debug out.jpg] [--json out.json]``
    one comparison of an image with a rendered view (prints the decision and
    the reasons; exit 0 for accept, 1 for reject).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None, gate=None, expected_api=None) -> int:
    from wenart.gate import calibrate

    parser = argparse.ArgumentParser(prog="python -m wenart.gate", description="change gate (milestone 5)")
    sub = parser.add_subparsers(dest="command", required=True)
    cal = sub.add_parser("calibrate", help="benign/negative controls and threshold proposals for one project")
    calibrate.add_arguments(cal)
    cmp_ = sub.add_parser("compare", help="compare one image with a rendered view")
    cmp_.add_argument("--render-dir", required=True, help="folder with render_manifest.json")
    cmp_.add_argument("--camera", required=True)
    cmp_.add_argument("--test", required=True, help="image to compare (render size)")
    cmp_.add_argument("--debug", default=None, help="write the debug JPEG here")
    cmp_.add_argument("--json", default=None, help="write the result JSON here")
    cmp_.add_argument("--device", default="cuda")
    cmp_.add_argument("--thresholds", default=None, help="thresholds.yaml (default: the package one)")
    args = parser.parse_args(argv)

    if args.command == "calibrate":
        return calibrate.run_from_args(args, gate=gate, expected_api=expected_api)

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
