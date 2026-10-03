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

CLI: ``python -m wenart.report final|sweep --project-out outputs/<p> [--out DIR] [--private]``.
"""
