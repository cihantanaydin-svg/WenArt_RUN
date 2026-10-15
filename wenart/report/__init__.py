"""Final report (docs/milestone5.md §7, docs/milestone6.md §7.4, docs/milestone7.md §9.4; areas E / IE / R).

- ``final``: ``final_manifest.json``, final previews, plan-crop copies,
  contact sheets, side-by-side sheets (Cycles | polished per room, M7) and
  ``final_report.md`` in ``outputs/<p>/final/``; the final decision per view
  (polished only when the brief and the project's gate validation allow the
  polish, the gate accepted it and the vision check, incl. the added-object
  detector, did not reject it); units, recognition, site, separators, assumed
  values and attribution (M7); the needs-review report of a project that
  stopped with ``needs_review``; private projects never get plan crops or
  debug images copied into ``final/``.
- ``sweep``: ``final/sweep_report.md`` from the polish sweep, the gate
  calibration and the vision-check calibration.
- ``common``: JSON input, the 300 KB JPEG writer, markdown helpers.
- Milestone 13 (docs/milestone13.md §7, §13.2): ``metrics13`` (the 17 before/after metrics of a run) and
  ``sheets13`` (one before | after JPEG per camera); ``final`` adds the commercial-safe line per view and the
  pieces built below the library level (docs/milestone13.md §6, D4).

CLI: ``python -m wenart.report final|sweep --project-out outputs/<p> [--out DIR] [--private]``;
``python -m wenart.report metrics13 --out <run> [--baseline <run>] --json <path> [--md <path>]``;
``python -m wenart.report sheets13 --out <run> --baseline <run> --dir <folder>``.
"""
