"""Final report of Milestone 5 (docs/milestone5.md §7; area E).

- ``final``: ``final_manifest.json``, final previews, plan-crop copies,
  contact sheets and ``final_report.md`` in ``outputs/<p>/final/``; the final
  decision per view (polished only when the gate accepted it and the vision
  check did not reject it).
- ``sweep``: ``final/sweep_report.md`` from the polish sweep, the gate
  calibration and the vision-check calibration.
- ``common``: JSON input, the 300 KB JPEG writer, markdown helpers.

CLI: ``python -m wenart.report final|sweep --project-out outputs/<p> [--out DIR]``.
"""
