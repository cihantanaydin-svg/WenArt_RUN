"""The one mirror decision of a level (``generic.mirror.halves``, ``generic.core._halves``; 5 Nov 2026, UL276 and its
other side): a plan is two mirrored halves only when the layout inside the building's shell is mirrored, not only the
shell. Review of 5 Nov 2026: a garden wall all round the house or a terrace parapet must not make a single house look
mirrored, walls on the axis (their own mirror) are no proof, one wall read too thick or one wall missing must not
refuse two mirrored flats, the core is left out, labels of the same room family agree, and a mirror copy that the
reader no longer makes never shifts another element's id. CPU only: hand-made walls, and the synthetic-19 house read
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


# --- the user's corrections keep naming their elements (stable mirror-copy ids, 5 Nov 2026) ------------------------

ID_FIXTURE = ROOT / "tests" / "fixtures" / "reading_ids.json"
CORRECTED = ("real06", "real07", "real10")


def _named(project: str) -> list[tuple]:
    t = json.loads((ROOT / "results" / "reading_truth" / f"{project}.json").read_text(encoding="utf-8"))
    return [(lid, k, e) for lid, lv in t["per_level"].items() for k, v in lv.items() if isinstance(v, list)
            for e in v if e.get("source") == "user_correction" and not e.get("absent")]


def _near(kind: str, truth_el: dict, read_el: dict) -> bool:
    from wenart.reading_check import score as SC
    if kind == "walls":
        return all(min(math.dist(truth_el[a], read_el[b]) for b in ("start", "end")) <= SC.WALL_LATERAL_M
                   for a in ("start", "end"))
    tol = {"rooms": SC.ROOM_CENTROID_M, "stairs": SC.STAIR_CENTER_M}.get(kind, SC.OPENING_CENTER_M)
    f = "centroid" if kind == "rooms" else "center"
    return math.dist(truth_el[f], read_el[f]) <= tol


def _check(project: str, read: dict) -> list:
    """The user_correction elements of the truth with no reading element of the same id within the score's
    tolerance of its place (``read``: ``{(level, id): element}``)."""
    bad = []
    for lid, kind, e in _named(project):
        r = read.get((lid, e["id"]))
        if r is None or not _near(kind, e, r):
            bad.append((lid, kind, e["id"], e.get("correction")))
    return bad


@pytest.mark.parametrize("project", CORRECTED)
def test_every_user_corrected_element_keeps_its_id(project):
    """Every user_correction element of the truth names an element of the branch's reading (the fixture: its ids and
    places, ``tests/fixtures/reading_ids.json``) at its place, within the score's tolerance: a change of the reader's
    numbering never leaves a correction on an empty or a different element (real10 C0043 moved from o_Lk_033/034 to
    o_Lk_030/031 with the stable mirror-copy ids; scripts/migrate_reading_ids.py renamed them)."""
    rows = json.loads(ID_FIXTURE.read_text(encoding="utf-8"))["projects"][project]
    read = {(r["level"], r["id"]): r for r in rows}
    assert _check(project, read) == []


@pytest.mark.slow
@pytest.mark.parametrize("project", CORRECTED)
def test_user_corrected_ids_on_a_fresh_reading(project, tmp_path):
    """The same on a fresh CPU reading of the project (minutes; real10 about 15)."""
    from wenart.ingest import pipeline as PL
    from wenart.reading_check import truth as TR

    b = PL.run_project(ROOT / "projects" / project, tmp_path / project, no_ai=True)[0]
    read = {(lid, e["id"]): e for lid, lv in TR.extract(b)["per_level"].items() for v in lv.values()
            if isinstance(v, list) for e in v}
    assert _check(project, read) == []
