"""Final vision check of every render with two vision models (docs/milestone5.md §5; area D).

Modules:

- ``expected``: expected elements per view, roles, visibility and the
  building-JSON cross-check (the role logic the polish and the gate use too);
- ``plan_crop``: the source-plan crop of every view;
- ``schemas`` / ``prompts`` / ``preference``: categories, the strict
  per-view schema, labels, the sentinel decoy and the prompts;
- ``project`` / ``calls``: what to ask for each image kind, the resumable
  ``answers_<slug>.json`` and the run loop with the deadline;
- ``combine``: two-model verdicts, extras, counts and the differential
  polish decision; ``calibrate``: false alarms, decoys, controls, plan A/B;
- ``controls``: removal/insertion/type-swap controls (select-controls);
- ``debug`` / ``report``: debug images and ``check_report.md``;
- ``cli``: ``python -m wenart.vision_check <subcommand>``.

Importing the package imports nothing heavy (no PIL, OpenCV or torch).
"""
