"""The one mirror decision of a level (``generic.mirror.halves``, ``generic.core._halves``; 5 Nov 2026, UL276 and its
other side): a plan is two mirrored halves only when the layout inside the building's shell is mirrored, not only the
shell. Review of 5 Nov 2026: a garden wall all round the house or a terrace parapet must not make a single house look
mirrored, walls on the axis (their own mirror) are no proof, one wall read too thick or one wall missing must not
refuse two mirrored flats, the core is left out, labels of the same room family agree, and the user's corrections
stand on the reading's elements by place. CPU only: hand-made walls, and the synthetic-19 house read
through the pipeline with a garden wall or a parapet added (the reviewers' variants)."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart import building as B
from wenart.ingest.generic import labels as LB
from wenart.ingest.generic import mirror as MR
from wenart.ingest.generic.model import TextRun
from wenart.ingest.model import OpeningItem, WallItem

ROOT = Path(__file__).resolve().parents[1]


def _walls(xy, t=0.2):
    out = []
    for k, item in enumerate(xy):
        a, b = item[0], item[1]
        th = item[2] if len(item) > 2 else t
        out.append(WallItem(start=a, end=b, thickness=th, box=[0, 0, 1, 1], entity=f"LINE:{k}",
                            evidence=B.evidence("x.dxf", "vector", 0.95, page=1, entity=f"LINE:{k}")))
    return out


def _blocks(labels):
    runs = [TextRun(id=f"T{k}", text=name, box=(x - 0.4, y - 0.1, x + 0.4, y + 0.1), height=0.2)
            for k, (name, x, y) in enumerate(labels)]
    return LB.merge_label_blocks(runs, "x.dxf", 1)


SHELL = [((0.0, 0.0), (20.0, 0.0), 0.3), ((20.0, 0.0), (20.0, 10.0), 0.3), ((20.0, 10.0), (0.0, 10.0), 0.3),
         ((0.0, 10.0), (0.0, 0.0), 0.3)]
PARTY = [((10.0, 0.0), (10.0, 10.0), 0.3)]                             # on the axis: its own mirror
# two mirrored flats: per flat a wall across at y 6 and two partitions
FLAT_L = [((0.0, 6.0), (10.0, 6.0)), ((4.0, 0.0), (4.0, 6.0)), ((7.0, 6.0), (7.0, 10.0))]
FLAT_R = [((10.0, 6.0), (20.0, 6.0)), ((16.0, 0.0), (16.0, 6.0)), ((13.0, 6.0), (13.0, 10.0))]
LABELS = [("SALON", 2.0, 3.0), ("SALON", 18.0, 3.0), ("YATAK ODASI", 7.0, 3.0), ("YATAK ODASI", 13.0, 3.0)]


def test_two_mirrored_flats_are_halves_also_with_a_thick_or_a_missing_wall():
    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    h = MR.halves(walls, [], _blocks(LABELS))
    assert h["axis"] == ("x", pytest.approx(10.0)) and h["share"] == pytest.approx(1.0)
    # one partition read 0.7 m thick, its centre 0.25 m off (a counter fused with it): the centre lines still pair
    thick = _walls(SHELL + PARTY + FLAT_L + [FLAT_R[0], ((16.25, 0.0), (16.25, 6.0), 0.7), FLAT_R[2]])
    assert MR.halves(thick, [], _blocks(LABELS))["axis"] is not None
    # one partition missing on the right: the missing step's slip, left out of the share
    missing = _walls(SHELL + PARTY + FLAT_L + FLAT_R[:2])
    h = MR.halves(missing, [], _blocks(LABELS))
    assert h["axis"] is not None and h["missing"] == 1


def test_a_single_house_whose_only_symmetric_walls_cross_the_axis_is_no_halves():
    """synthetic-07's ground floor kind: walls across the whole plan and a wall on the axis pair with themselves in
    any layout; the partitions that do not cross the axis have no twin."""
    walls = _walls(SHELL + [((0.0, 6.0), (20.0, 6.0)), ((10.0, 6.0), (10.0, 10.0)), ((4.0, 0.0), (4.0, 6.0)),
                            ((15.0, 0.0), (15.0, 6.0))])
    h = MR.halves(walls, [], [])
    assert h["axis"] is None and h["self_mirror"] == 2 and h["paired"] == 0 and "one layout" in h["note"]


def test_a_garden_wall_or_a_parapet_is_not_the_shell():
    """A symmetric garden wall 3 m off the house (an enclosure: the garden face holds the house's rooms) and a
    terrace parapet joined to the facade do not turn the house's outer walls into 'walls inside the shell'."""
    house = SHELL + [((0.0, 6.0), (20.0, 6.0)), ((4.0, 0.0), (4.0, 6.0)), ((15.0, 0.0), (15.0, 6.0))]
    garden = [((-3.0, -3.0), (23.0, -3.0)), ((23.0, -3.0), (23.0, 13.0)), ((23.0, 13.0), (-3.0, 13.0)),
              ((-3.0, 13.0), (-3.0, -3.0))]
    labels = _blocks([("SALON", 2.0, 3.0), ("MUTFAK", 9.0, 3.0), ("YATAK ODASI", 18.0, 3.0), ("HOL", 10.0, 8.0)])
    plain = MR.halves(_walls(house), [], labels)
    h = MR.halves(_walls(house + garden), [], labels)
    assert h["axis"] is None and h["walls_inside"] == plain["walls_inside"] == 3, h
    parapet = [((0.0, -2.0), (20.0, -2.0), 0.15), ((0.0, -2.0), (0.0, 0.0), 0.15), ((20.0, -2.0), (20.0, 0.0), 0.15)]
    h = MR.halves(_walls(house + parapet), [], labels)
    assert h["axis"] is None, h


def test_the_core_is_left_out_and_labels_of_one_family_agree():
    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    lift = _blocks(LABELS + [("ASANSÖR", 4.5, 3.0)])
    h = MR.halves(walls, [], lift)
    assert h["walls_inside"] < MR.halves(walls, [], _blocks(LABELS))["walls_inside"]
    # 'BANYO' and 'BANYO / WC' (bathroom, wc), 'MUTFAK' and 'SALON + AÇIK MUTFAK' are the same rooms of two flats
    same = _blocks([("BANYO", 2.0, 3.0), ("BANYO / WC", 18.0, 3.0), ("MUTFAK", 7.0, 3.0),
                    ("SALON + AÇIK MUTFAK", 13.0, 3.0)])
    assert MR.label_pairs(walls, [], ("x", 10.0), same) == (2, 0)
    # one pair of different rooms decides nothing; two (and more than agree) refuse
    one = _blocks([("BANYO", 2.0, 3.0), ("YATAK ODASI", 18.0, 3.0), ("MUTFAK", 7.0, 3.0), ("MUTFAK", 13.0, 3.0)])
    assert MR.halves(walls, [], one)["axis"] is not None
    two = _blocks([("BANYO", 2.0, 3.0), ("YATAK ODASI", 18.0, 3.0), ("MUTFAK", 7.0, 3.0), ("YATAK ODASI", 13.0, 3.0)])
    h = MR.halves(walls, [], two)
    assert h["axis"] is None and h["labels"] == [0, 2]


def test_an_opening_is_never_copied_onto_itself():
    """An opening on a wall across the axis, or so near it that its mirror overlaps it (the twin match's radius), is
    its own twin: real09, real10 and real11 got exact duplicates on the axis."""
    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    on_axis = OpeningItem(kind="window", width=2.5, center=(10.3, 0.0), rotation_deg=0.0, box=[], entity="LINE:w",
                          evidence={"method": "vector"})
    res = MR.consistency(walls, [on_axis], ("x", 10.0), steps=("openings",))
    assert res is None                                   # nothing to copy


def _window(x, w=1.0, ent="LINE:w"):
    return OpeningItem(kind="window", width=w, center=(x, 0.0), rotation_deg=0.0, box=[], entity=ent,
                       evidence={"method": "vector"})


def test_a_copy_never_lands_on_an_opening_of_its_wall_nor_on_drawn_solid_wall():
    """Review of 5 Nov 2026 (real11 L-1: a 1.5 m opening copied onto the outer wall over its drawn window, where the
    drawing has solid wall): the openings step refuses a copy whose span overlaps an opening of the host wall, and a
    copy whose span has the wall's two faces drawn continuous; each refusal is a log line."""
    from types import SimpleNamespace

    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    # the left window at 2.5 m; its mirror at 17.5 m
    w5, o5, log = MR.consistency(walls, [_window(2.5)], ("x", 10.0), steps=("openings",))
    assert [o.center for o in o5 if "mirror_twin" in o.entity] == [(17.5, 0.0)]
    # a drawn 1.4 m window at 18.4 m already holds part of that span (centre 0.9 m off: no twin by the centre rule)
    res = MR.consistency(walls, [_window(2.5), _window(18.4, 1.4, "LINE:x")], ("x", 10.0), steps=("openings",))
    assert res is not None and res[2] and all(e.startswith("refused") and "overlap" in e for e in res[2])
    assert not any("mirror_twin" in o.entity for o in res[1])
    # an inferred (guessed) window there is replaced by the copy, as at the centre (real09's balcony door)
    guess = _window(18.4, 1.4, "LINE:g")
    guess.evidence, guess.inferred = {"method": "inferred"}, True
    res = MR.consistency(walls, [_window(2.5), guess], ("x", 10.0), steps=("openings",))
    assert [o.entity for o in res[1]] == ["LINE:w", "inferred:mirror_twin:LINE:w"]
    # the drawing has solid wall there: the bottom wall's own lines (LINE:0) run along both faces over 16-19 m
    faces = [SimpleNamespace(id="LINE:0", pts=[(16.0, y), (19.0, y)]) for y in (-0.15, 0.15)]
    res = MR.consistency(walls, [_window(2.5)], ("x", 10.0), steps=("openings",), strokes=faces)
    assert res is not None and any("solid wall" in e for e in res[2])
    assert not any("mirror_twin" in o.entity for o in res[1])
    # lines that are not the wall's own (a window frame drawn along the faces) say nothing: the copy is made
    frames = [SimpleNamespace(id="LINE:frame", pts=[(16.0, y), (19.0, y)]) for y in (-0.15, 0.15)]
    res = MR.consistency(walls, [_window(2.5)], ("x", 10.0), steps=("openings",), strokes=frames)
    assert [o.center for o in res[1] if "mirror_twin" in o.entity] == [(17.5, 0.0)]
    # a real gap: the wall's face lines stop at the jambs (17.0 and 18.0): the copy is made
    jambs = [SimpleNamespace(id="LINE:0", pts=[(14.0, y), (17.0, y)]) for y in (-0.15, 0.15)] + \
        [SimpleNamespace(id="LINE:0", pts=[(18.0, y), (19.0, y)]) for y in (-0.15, 0.15)]
    res = MR.consistency(walls, [_window(2.5)], ("x", 10.0), steps=("openings",), strokes=jambs)
    assert [o.center for o in res[1] if "mirror_twin" in o.entity] == [(17.5, 0.0)]


@pytest.fixture(scope="module")
def variants(tmp_path_factory):
    """The reviewers' synthetic-19 variants (gen19.py): a garden wall all round, and a front terrace parapet with a
    rear garden wall, drawn on the wall layer; read through the pipeline."""
    from wenart.ingest import pipeline as PL
    from wenart.synthetic import failure_classes as FC
    from wenart.synthetic import failure_projects as FP
    from wenart.synthetic.failure_classes import Label, Wall

    out = tmp_path_factory.mktemp("s19_variants")
    garden = [Wall("g1", (-3.0, -3.0), (15.0, -3.0), 0.2), Wall("g2", (15.0, -3.0), (15.0, 12.0), 0.2),
              Wall("g3", (15.0, 12.0), (-3.0, 12.0), 0.2), Wall("g4", (-3.0, 12.0), (-3.0, -3.0), 0.2)]
    parapet = [Wall("p1", (0.0, -2.0), (12.0, -2.0), 0.15), Wall("p2", (0.0, -2.0), (0.0, 0.0), 0.15),
               Wall("p3", (12.0, -2.0), (12.0, 0.0), 0.15), Wall("g3", (0.0, 11.0), (12.0, 11.0), 0.2)]
    read = {}
    for name, extra, labels in (("s19-garden", garden, []), ("s19-garden-bahce", garden, [Label("BAHÇE", (-1.5, 10.5))]),
                                ("s19-parapet-rear", parapet, [Label("TERAS", (6.0, -1.0))])):
        p = copy.deepcopy(FP.project_19())
        p.name = name
        p.plans[0].walls = p.plans[0].walls + extra
        p.plans[0].labels = p.plans[0].labels + labels
        FC.generate_failure_project(p, out)
        read[name] = PL.run_project(out / name, out / f"{name}_out", no_ai=True)[0]
    return read


@pytest.mark.parametrize("name", ["s19-garden", "s19-garden-bahce", "s19-parapet-rear"])
def test_the_reviewers_variants_get_nothing_mirrored(variants, name):
    b = variants[name]
    copies = [o["id"] for o in b["openings"] if "mirror_twin" in str((o.get("evidence") or [{}])[0].get("rule"))]
    copies += [w["id"] for w in b["walls"] if (w.get("evidence") or [{}])[0].get("rule") == "mirror_twin"]
    assert copies == []
    # the house's 6 doors and 9 windows (synthetic-19's truth), each once
    ops = [o for o in b["openings"] if o["type"] in ("door", "window")]
    assert sum(o["type"] == "door" for o in ops) == 6 and sum(o["type"] == "window" for o in ops) == 9
    assert not any(o is not q and o["type"] == q["type"] and math.dist(o["center"], q["center"]) <= 0.05
                   for o in ops for q in ops)


# --- the user's corrections stand on the reading's elements by place (5 Nov 2026) ---------------------------------

ID_FIXTURE = ROOT / "tests" / "fixtures" / "reading_ids.json"
CORRECTED = ("real06", "real07", "real10")


def _named(project: str) -> list[tuple]:
    t = json.loads((ROOT / "results" / "reading_truth" / f"{project}.json").read_text(encoding="utf-8"))
    return [(lid, k, e) for lid, lv in t["per_level"].items() for k, v in lv.items() if isinstance(v, list)
            for e in v if e.get("source") == "user_correction" and not e.get("absent")]


def _unplaced(project: str, read: dict) -> list:
    """The user_correction elements of the truth with no reading element at their place (the score's rules,
    ``truth.same_place_pairs``; doors, windows and openings as one class; ``read``: ``{(level, type): [elements]}``)."""
    from wenart.reading_check import truth as TR
    ops = ("doors", "windows", "openings")
    bad = []
    for lid, kind, e in _named(project):
        # a retype (the reader's opening is the user's door) stands on the reading's element of another opening class
        cands = [c for k in ops for c in read.get((lid, k)) or []] if kind in ops else read.get((lid, kind)) or []
        if not TR.same_place_pairs("openings" if kind in ops else kind, [e], cands):
            bad.append((lid, kind, e["id"], e.get("reader_id"), e.get("correction")))
    return bad


@pytest.mark.parametrize("project", CORRECTED)
def test_every_user_corrected_element_stands_on_a_reading_element(project):
    """Every user_correction element of the truth has an element of the branch's reading of its class at its place
    (the fixture ``tests/fixtures/reading_ids.json``: the reading's elements at those places). The truth's identity is
    the place (``truth.same_place_pairs``), so a renumbering of the reader's ids never leaves a correction on an empty
    or a different element; the reader's id is only a hint (``reader_id``)."""
    rows = json.loads(ID_FIXTURE.read_text(encoding="utf-8"))["projects"][project]
    read: dict = {}
    for r in rows:
        read.setdefault((r["level"], r["kind"]), []).append(r)
    assert _unplaced(project, read) == []


@pytest.mark.slow
@pytest.mark.parametrize("project", CORRECTED)
def test_user_corrected_elements_on_a_fresh_reading(project, tmp_path):
    """The same on a fresh CPU reading of the project (minutes; real10 about 15)."""
    from wenart.ingest import pipeline as PL
    from wenart.reading_check import truth as TR

    b = PL.run_project(ROOT / "projects" / project, tmp_path / project, no_ai=True)[0]
    read = {(lid, t): els for lid, lv in TR.extract(b)["per_level"].items() for t, els in lv.items()
            if isinstance(els, list)}
    assert _unplaced(project, read) == []


def test_the_audit_finds_mirror_copy_ids():
    """The audit's opening ids include the mirror copies' own numbers (d_L0_m001, o_L-1_m002)."""
    from wenart.audit import calls as CA
    from wenart.audit import consistency as CO

    text = "doors d_L0_m001 and d_L0_012, opening o_L-1_m002, window win_L1b_003"
    for rx in (CA.OPENING_RE, CO.OPENING_RE):
        assert rx.findall(text) == ["d_L0_m001", "d_L0_012", "o_L-1_m002", "win_L1b_003"]


def test_an_inferred_wall_is_never_drawn_solid_wall():
    """Review of round 3: a wall inferred from room outlines names drawn strokes as its entity; it is no drawn wall,
    so its 'faces' never make a copy's span solid."""
    from types import SimpleNamespace

    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    walls[0].inferred, walls[0].evidence = True, {"method": "inferred", "rule": "room_outlines"}
    faces = [SimpleNamespace(id="LINE:0", pts=[(16.0, y), (19.0, y)]) for y in (-0.15, 0.15)]
    assert not MR.solid_span(walls[0], (17.5, 0.0), 1.0, faces)
    res = MR.consistency(walls, [_window(2.5)], ("x", 10.0), steps=("openings",), strokes=faces)
    assert [o.center for o in res[1] if "mirror_twin" in o.entity] == [(17.5, 0.0)]


def test_the_mirror_decision_cache_sees_labels_and_openings():
    """Review of round 3: the same walls with other labels or other openings are another decision."""
    from types import SimpleNamespace

    from wenart.ingest.generic import core as C

    ex = SimpleNamespace(report={}, notes=[])
    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    same = _blocks(LABELS)
    other = _blocks([("BANYO", 2.0, 3.0), ("YATAK ODASI", 18.0, 3.0), ("MUTFAK", 7.0, 3.0),
                     ("YATAK ODASI", 13.0, 3.0)])
    assert C._halves(ex, walls, [], same, "L0", "a") == ("x", pytest.approx(10.0))
    assert C._halves(ex, walls, [], other, "L0", "b") is None                  # two different-room pairs refuse
    assert C._halves(ex, walls, [_window(2.5)], same, "L0", "c") == ("x", pytest.approx(10.0))
    assert len(ex.report["mirror"]) == 3 and [r["by"] for r in ex.report["mirror"]] == ["a", "b", "c"]
    C._halves(ex, walls, [], same, "L0", "d")                                  # the same input: the cached decision
    assert len(ex.report["mirror"]) == 3


def test_a_step_with_only_refusals_is_not_kept_after_a_kept_step(monkeypatch):
    """Review of round 3: the log of a step holds the kept steps' lines too; a step whose own lines are all refusals
    keeps nothing (its refusals are noted)."""
    from types import SimpleNamespace

    from wenart.ingest.generic import core as C

    walls = _walls(SHELL + PARTY + FLAT_L + FLAT_R)
    calls = []

    def fake(w, o, axis, steps=MR.STEPS, keep_out=None, strokes=None):
        calls.append(steps)
        log = ["wall inferred:mirror_twin:1 inferred: the mirror of LINE:x (1.00 m)"] if "missing" in steps else []
        if "openings" in steps:
            log.append("refused: the mirror of door LINE:d (0.90 m) would land on drawn solid wall (LINE:0)")
        return (list(w), list(o), log) if log else None

    monkeypatch.setattr(MR, "consistency", fake)
    monkeypatch.setattr(MR, "mirrored_face_pairs", lambda w, o, axis: len(w))   # the copied wall pairs one more
    ex = SimpleNamespace(report={}, notes=[])
    res = C._mirror_consistency(ex, "p", walls, [], _blocks(LABELS), "L0", [], None)
    note = next(n for n in ex.notes if "mirror check about" in n)
    assert "steps kept missing;" in note and "refused: the mirror of door" in note and "openings" not in \
        note.split("steps kept")[1].split(";")[0]
    assert res is not None
