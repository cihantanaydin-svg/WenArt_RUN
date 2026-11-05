"""5 Nov 2026 (Milestone 14 R5): the cross-document checks join the reading check as advisory findings. What: ``write``
renders an ``info`` advisory finding and keeps it out of the verdict counts; ``check`` on a reading output carries
``counts["advisory"]``. Why: the user asked for the machine to give the feedback itself; its new checks must be seen
without stopping a pod run until they earn trust."""
from __future__ import annotations

import json

from wenart import reading_check as RC


def test_write_renders_advisory_info_findings_and_keeps_the_verdict(tmp_path):
    result = {"project": "p", "levels_checked": ["L0"], "reference": "L0", "conventions": {}, "notes": [],
              "findings": [{"check": "RC8", "name": "elevation openings against the plan", "severity": "info",
                            "level_id": None, "message": "no north arrow: compass sides placed by fit", "advisory": True},
                           {"check": "RC8", "name": "elevation openings against the plan", "severity": "major",
                            "level_id": "L1", "message": "an opening 1.60 m wide at x 1.70 m: the plan has none",
                            "advisory": True},
                           {"check": "RC3", "name": RC.CHECKS["RC3"], "severity": "major", "level_id": "L0",
                            "message": "Salon: the drawing says 33.50 m2, the model has 19.1 m2"}],
              "counts": {"critical": 0, "major": 1, "minor": 0, "advisory": {"major": 1, "minor": 0, "info": 1}},
              "verdict": "ready", "levels": ["L0", "L1"], "levels_left_out": []}
    d = RC.write(tmp_path, result)
    md = (d / "reading_check.md").read_text(encoding="utf-8")
    assert "advisory: 1 major, 0 minor, 1 info (not in the verdict)" in md
    assert "| RC8 elevation openings against the plan (advisory) | info |" in md
    assert md.index("| RC3 ") < md.index("| RC8 elevation openings against the plan (advisory) | major |")
    assert json.loads((d / "reading_check.json").read_text(encoding="utf-8"))["counts"]["advisory"]["info"] == 1
