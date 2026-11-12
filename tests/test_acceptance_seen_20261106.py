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


def test_no_real_truth_rests_on_an_accepted_reading_while_the_acceptances_are_withdrawn():
    """6 Nov 2026 (user: "Only consider my revision with the screenshot I have given into previous projects others I
    have not seen"): every real acceptance is withdrawn (the baselines keep the old fields under
    ``acceptance_withdrawn``), so no real truth is built from a stored accepted reading: every real truth file is
    sparse (the user's corrections only), names no accepted reading and holds only entries of the user's records."""
    for path in sorted((REPO / "results" / "reading_baseline").glob("real*.json")):
        base = json.loads(path.read_text(encoding="utf-8"))
        assert TR.acceptance(base) is None, f"{path.stem}: an acceptance still stands"
        if (base.get("acceptance_withdrawn") or {}).get("was"):
            assert base["accepted_by_user"] is False and base["acceptance_withdrawn"]["on"] == "2026-11-06"
    assert [p for p in TR.accepted_projects() if TR.synthetic_truth_file(p) is None] == []   # synthetic ones stay
    records = TR.load_corrections()
    for path in sorted((REPO / "results" / "reading_truth").glob("*.json")):
        if TR.synthetic_truth_file(path.stem) is not None:
            continue
        truth = json.loads(path.read_text(encoding="utf-8"))
        assert TR.is_sparse(truth) and truth["source"] == TR.SOURCE_CORRECTIONS, path.stem
        assert truth["built_from"]["reading"] is None and truth["built_from"]["reading_commit"] is None, path.stem
        mine = {r["id"] for r in records if r["project"] == path.stem and TR.correction_applicable(r) is None}
        assert mine, f"{path.stem}: a truth without an applicable record of the user"
        for lv in truth["per_level"].values():
            for els in lv.values():
                for e in els:
                    assert e["source"] == TR.SOURCE_USER and set(e["corrections"]) <= mine, (path.stem, e["id"])
        for a in truth["project_assertions"]:
            assert set(a["corrections"]) <= mine, (path.stem, a["id"])
        acc, _ = TR.accepted_of(path.stem)
        assert acc is None, f"{path.stem}: an accepted reading would be used"
    for p in ("real21", "real19", "real01", "real02", "real03", "real15"):        # no applicable record: no truth
        if p not in TR.sparse_projects(records):
            assert not (REPO / "results" / "reading_truth" / f"{p}.json").exists(), p
