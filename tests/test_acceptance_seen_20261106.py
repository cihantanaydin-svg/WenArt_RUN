"""An acceptance is the user's acceptance of a reading they saw (6 Nov 2026, user: "I have never reviewed real21 with
my eyes"): real21's and real19's truths had been built from words about something else (splitting two buildings,
naming the plan levels). ``accepted_seen`` names what the user looked at; a withdrawn acceptance is none, and a
project whose acceptance was withdrawn leaves the score's full run without counting as a fall."""
import json
from pathlib import Path

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

REPO = Path(__file__).resolve().parents[1]
BASE = {"accepted_by_user": True, "accepted_on": "2026-11-04", "accepted_scope": "all",
        "accepted_note": "user: 'yes accept the baselines'"}


def test_words_without_a_seen_reading_are_no_acceptance():
    assert TR.acceptance(BASE) is None
    assert TR.acceptance(dict(BASE, accepted_seen="  ")) is None
    acc = TR.acceptance(dict(BASE, accepted_seen="structure run 20261104-144248"))
    assert acc["seen"] == "structure run 20261104-144248" and acc["scope"] == "all"


def test_a_withdrawn_acceptance_is_none():
    withdrawn = dict(BASE, accepted_seen="the sheets", acceptance_withdrawn={"on": "2026-11-06", "reason": "x"})
    assert TR.acceptance(withdrawn) is None


def test_accepted_projects_need_the_seen_reading(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(dict(BASE, accepted_seen="the drawings")))
    (tmp_path / "b.json").write_text(json.dumps(BASE))
    assert TR.accepted_projects(tmp_path) == ["a"]


def test_a_withdrawn_project_is_no_fall_in_a_full_run():
    last = {"projects": {"p1": {"total": 96.0}, "p2": {"total": 100.0}}, "overall": 98.0}
    new = {"projects": {"p1": {"total": 96.0}}, "overall": 96.0}
    assert SC.falls(last, new, full=True) == ["p2: 100.00 -> not scored"]
    assert SC.falls(last, new, full=True, withdrawn=["p2"]) == []


def test_the_repository_keeps_no_truth_without_a_seen_reading():
    """Every real project with a truth file rests on an acceptance that names what the user saw; real21 and real19
    were withdrawn on 6 Nov 2026."""
    for path in sorted((REPO / "results" / "reading_truth").glob("*.json")):
        if TR.synthetic_truth_file(path.stem) is not None:
            continue
        base = TR.load_baseline(path.stem)
        assert TR.acceptance(base) is not None, f"{path.stem}: a truth without an acceptance of a seen reading"
    for p in ("real21", "real19"):
        assert not (REPO / "results" / "reading_truth" / f"{p}.json").exists()
        assert TR.acceptance(TR.load_baseline(p)) is None
