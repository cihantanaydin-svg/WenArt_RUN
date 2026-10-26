"""Argus, the auditor (26 Oct 2026, user: "the audit is very weak, only the looks being judged, everything needs to be
judged ... we need a big smart auditor to check everything in the project ... develop a system to understand the
problem kinds and prevent it happening ... this auditor should have no limits ... use open weight AI models, it needs
to be smart, it needs to solve the problems even without me telling it"; the name: Argus, the giant of a hundred eyes
who never slept).

Lines (each a module; every finding in one format, see ``kinds.FINDING_KEYS``):

- ``ledger``: the source documents' items (texts, area labels, blocks, layers, regions) each used by the model or
  explained (code).
- ``conservation``: nothing disappears between stages: every element of a stage is in the next one or has a logged
  reason, every element planned to be built is in the scene, every reason for leaving one out is listed (code).
- ``process``: the run itself: stage failures, every warning matched to a rule (the ones that say something was left
  out or fell short are findings), open questions, failed tests, the scene's own checks, rooms with no view, library
  gaps, time left unused, a big loop that did not improve (code).
- ``plan_vs_model``: the source plan of each floor against the model's view of it, the elevations against the
  exterior renders (open-weight vision model, every claim checked by code).
- ``argus_ai``: the open-weight agent model reads every line's findings and the project's facts, thinks, sorts each
  finding (real or not, kind, the stage that caused it), names the fix the run can carry out (an architect decision
  that code checks and re-checks, a finding for the agent's next round) or the general rule that would prevent it,
  and looks for what the lines missed.
- the model review (``wenart.blender.model_review``), the inspector and the judge (``wenart.agent``) are lines too.
- ``kinds``: every finding's problem kind, where it arose and the guards that catch it; ``report``: one report
  (``orchestrator/argus.md``), the score, and the problem log across runs (``results/argus/problem_log.json``) with
  the kinds that need a new guard.

CLI: ``python -m wenart.audit run --results runs/<job>/results --project <p>`` (a collected run) or
``python -m wenart.audit run --pod outputs/<p>`` (on the pod).
"""
NAME = "Argus"
