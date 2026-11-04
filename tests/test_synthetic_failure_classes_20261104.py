"""The synthetic failure classes (synthetic-08 ...): generated the same every time, committed, and read through the
pipeline against their truth.

What (4 Nov 2026, Milestone 14 track R7): for every project of ``wenart.synthetic.failure_projects``: the generator
is deterministic (two runs, identical bytes) and the committed files under ``projects/`` are current; the truth is
well formed (the format of ``truth/reading_truth.json``) and consistent with the drawing's layout; and a CPU reading
(``wenart.ingest.pipeline.run_project``, ``no_ai=True``) gives the truth's per-level counts of rooms, doors, windows and
stairs, every truth room and opening at its place, and what the project's failure class is about (spaced labels read
as words, the pool found, the mirrored flat's rooms named, the elevation title giving the storey, the winders, the
recess left open air, the garage door ...).

Why: the user's goal, "I want structure recognition to be cumulatively better with the feedbacks I am giving": every
class the user found in a real drawing becomes a measured target. Where the reader does not handle a class yet, its
test is a strict xfail naming the class and its lesson, so a reader change that fixes it turns the test into an
XPASS failure and the mark has to go (the expected numbers are the truth, never weakened to make a test pass).

How: one module-scoped generation into a temporary folder; one reading per project, cached (the 4 CPU cores are
shared, so the readings run one at a time).
"""
from __future__ import annotations

import collections
import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart.synthetic import failure_classes as FC
from wenart.synthetic.failure_projects import failure_projects
from wenart.synthetic.generate import generate_project, main

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "projects"
RESULTS = ROOT / "results" / "synthetic"
PROJECTS = {p.name: p for p in failure_projects()}
NAMES = list(PROJECTS)
FILES = [FC.DXF_FILE, "brief.yaml", FC.TRUTH_FILE]
CENTRE_TOL_M = 0.2          # a read opening is the truth's when its centre is this close ...
WIDTH_TOL_M = 0.1           # ... and its width this close
AREA_TOL = 0.05             # a read room is the truth room when it holds its inner point, at this area share


def _xfail(cls: str, lesson: str, what: str = ""):
    return pytest.mark.xfail(strict=True, reason=f"failure class {cls}: the reader does not handle it yet ({lesson})"
                             + (f": {what}" if what else ""))


# What the reader does not handle yet (4 Nov 2026, measured on the generated projects): per test, per project.
XFAIL_COUNTS = {
    "synthetic-10-glazed-facade": _xfail("glazed_facade", "UL274", "the frames become one 6.3 m window"),
    "synthetic-12-mirrored-halves": _xfail("mirrored_halves", "UL276", "unswung door gaps are openings or a window"),
    "synthetic-14-elevation-title": _xfail("elevation_title", "UL271", "the two plans are read as one level"),
    "synthetic-17-garage-lift": _xfail("garage_lift", "UL320", "the 3.4 m garage opening is read as a window"),
}
XFAIL_GEOMETRY = dict(XFAIL_COUNTS)


def _params(names, marks: dict):
    return [pytest.param(n, marks=marks[n]) if n in marks else n for n in names]


# --------------------------------------------------------------------------
# Generation: files, determinism, currency
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    out = tmp_path_factory.mktemp("failure_projects")
    for project in failure_projects():
        generate_project(project, out, None)
    return out


def truth_of(generated, name) -> dict:
    return json.loads((generated / name / FC.TRUTH_FILE).read_text(encoding="utf-8"))


EXPECTED_NAMES = [
    "synthetic-08-spaced-labels",
    "synthetic-09-jamb-stubs",
    "synthetic-10-glazed-facade",
    "synthetic-11-dimension-chains",
    "synthetic-12-mirrored-halves",
    "synthetic-13-typical-floor",
    "synthetic-14-elevation-title",
    "synthetic-15-winder-stair",
    "synthetic-16-open-recess",
    "synthetic-17-garage-lift",
    "synthetic-18-sheet-frame",
]


def test_the_failure_classes_in_order():
    assert NAMES == EXPECTED_NAMES


@pytest.mark.parametrize("name", NAMES)
def test_files_exist(generated, name):
    for rel in FILES:
        assert (generated / name / rel).is_file(), rel


def test_deterministic(generated, tmp_path):
    for project in failure_projects():
        generate_project(project, tmp_path, None)
    for name in NAMES:
        for rel in FILES:
            assert (generated / name / rel).read_bytes() == (tmp_path / name / rel).read_bytes(), \
                f"{name}/{rel} differs between runs"


@pytest.mark.skipif(not COMMITTED.exists(), reason="projects/ not present")
@pytest.mark.parametrize("name", NAMES)
def test_committed_projects_are_current(generated, name):
    for rel in FILES:
        committed = COMMITTED / name / rel
        assert committed.is_file(), f"run python -m wenart.synthetic.generate --out projects ({name}/{rel} missing)"
        assert committed.read_bytes() == (generated / name / rel).read_bytes(), \
            f"{name}/{rel} is stale: run python -m wenart.synthetic.generate --out projects"


@pytest.mark.skipif(not RESULTS.exists(), reason="results/synthetic/ not present")
@pytest.mark.parametrize("name", NAMES)
def test_committed_preview_exists(name):
    assert (RESULTS / FC.PREVIEW.format(name=name)).is_file()


def test_cli_writes_one_failure_project(tmp_path):
    assert main(["--out", str(tmp_path / "p"), "--results", "", "--only", "synthetic-08-spaced-labels"]) == 0
    assert sorted(p.name for p in (tmp_path / "p").iterdir()) == ["synthetic-08-spaced-labels"]
    assert (tmp_path / "p" / "synthetic-08-spaced-labels" / FC.TRUTH_FILE).is_file()


# --------------------------------------------------------------------------
# The truth: format and consistency with the layout
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", NAMES)
def test_truth_format(generated, name):
    t = truth_of(generated, name)
    p = PROJECTS[name]
    assert t["project"] == name and t["source"] == "synthetic" and t["status"] == "accepted"
    assert t["failure_class"] == p.failure_class and t["lesson"] == p.lesson
    assert [lv["id"] for lv in t["levels"]] == list(t["per_level"])
    assert [lv["order"] for lv in t["levels"]] == sorted(lv["order"] for lv in t["levels"])
    for lid, lv in t["per_level"].items():
        assert set(lv) == {"rooms", "doors", "windows", "openings", "walls", "stairs"}
        for r in lv["rooms"]:
            assert set(r) == {"id", "label", "room_type", "area", "centroid", "polygon"}
            assert r["label"] and r["room_type"] == B.room_type_for(r["label"])
            assert Polygon(r["polygon"]).area == pytest.approx(r["area"], abs=1e-3)
        for kind in ("doors", "windows"):
            for o in lv[kind]:
                assert {"id", "width", "center", "type"} <= set(o) and o["type"] == kind[:-1]
        ids = [x["id"] for k in ("rooms", "doors", "windows", "openings", "walls", "stairs") for x in lv[k]]
        assert len(ids) == len(set(ids)), lid


@pytest.mark.parametrize("name", NAMES)
def test_truth_openings_sit_on_their_walls_and_between_rooms(generated, name):
    t = truth_of(generated, name)
    for lid, lv in t["per_level"].items():
        walls = [FC.Wall(w["id"], tuple(w["start"]), tuple(w["end"]), w["thickness"]) for w in lv["walls"]]
        rooms = [Polygon(r["polygon"]) for r in lv["rooms"]]
        for o in lv["doors"] + lv["windows"]:
            c = Point(o["center"])
            assert any(w.rect().buffer(1e-6).contains(c) for w in walls), (lid, o)
            # a door or window touches a room on at least one side
            assert any(r.distance(c) <= 0.2 for r in rooms), (lid, o)


@pytest.mark.parametrize("name", NAMES)
def test_dxf_layers_are_the_cad_office_ones(generated, name):
    import ezdxf.recover
    doc, _ = ezdxf.recover.readfile(str(generated / name / FC.DXF_FILE))
    assert doc.header["$INSUNITS"] == FC.INSUNITS
    used = {e.dxf.layer for e in doc.modelspace()}
    assert {"DUVAR", "KAPI", "PENCERE", "YAZI"} <= used


# --------------------------------------------------------------------------
# The reading
# --------------------------------------------------------------------------

_READS: dict = {}           # project name -> (building, output folder)


@pytest.fixture(scope="module")
def read(generated, tmp_path_factory):
    from wenart.ingest import pipeline as PL

    def _read(name: str) -> dict:
        if name not in _READS:
            out = tmp_path_factory.mktemp(name)
            building, _ = PL.run_project(generated / name, out, no_ai=True)
            _READS[name] = (building, out)
        return _READS[name][0]
    return _read


def reader_counts(b: dict) -> dict:
    per = collections.defaultdict(lambda: {"rooms": 0, "doors": 0, "windows": 0, "stairs": 0})
    for lv in b["levels"]:
        per[lv["id"]]
    for r in b["rooms"]:
        per[r["level_id"]]["rooms"] += 1
    for o in b["openings"]:
        if o["type"] in ("door", "window"):
            per[o["level_id"]][o["type"] + "s"] += 1
    for f in b["furniture"]:
        if f.get("type") == "stair":
            per[f["level_id"]]["stairs"] += 1
    return dict(per)


@pytest.mark.parametrize("name", _params(NAMES, XFAIL_COUNTS))
def test_reader_counts_per_level(generated, read, name):
    t = truth_of(generated, name)
    b = read(name)
    assert [(lv["id"], round(lv["elevation"], 2)) for lv in b["levels"]] == \
        [(lv["id"], round(lv["elevation"], 2)) for lv in t["levels"]]
    assert reader_counts(b) == FC.counts(t)


def geometry_misses(t: dict, b: dict) -> list[str]:
    """What of the truth the reading misses: a door or window with no read one of its type at its centre and width,
    a room with no read room holding its inner point at its area and room type."""
    misses = []
    for lid, lv in t["per_level"].items():
        ops = [o for o in b["openings"] if o["level_id"] == lid]
        for kind in ("door", "window"):
            for o in lv[kind + "s"]:
                if not any(r["type"] == kind and math.dist(r["center"], o["center"]) <= CENTRE_TOL_M
                           and abs(r["width"] - o["width"]) <= WIDTH_TOL_M for r in ops):
                    misses.append(f"{lid} {kind} {o['center']} {o['width']} m")
        rooms = [r for r in b["rooms"] if r["level_id"] == lid]
        for r in lv["rooms"]:
            inner = Polygon(r["polygon"]).representative_point()
            hit = [q for q in rooms if Polygon(q["polygon"]).contains(inner)]
            if not hit or abs(hit[0]["area_computed"] - r["area"]) > AREA_TOL * r["area"] \
                    or hit[0]["room_type"] != r["room_type"]:
                misses.append(f"{lid} room {r['label']} ({r['room_type']}, {r['area']:.2f} m²): "
                              + (f"read {hit[0]['label']} ({hit[0]['room_type']}, {hit[0]['area_computed']:.2f} m²)"
                                 if hit else "not read"))
    return misses


@pytest.mark.parametrize("name", _params(NAMES, XFAIL_GEOMETRY))
def test_reader_finds_every_truth_room_and_opening(generated, read, name):
    assert geometry_misses(truth_of(generated, name), read(name)) == []


def _fold(text: str) -> str:
    return " ".join(B.fold_ascii(text or "").lower().split())


# --- synthetic-08-spaced-labels ------------------------------------------------------------------------------------

def test_08_spaced_labels_are_one_text_per_letter(generated):
    import ezdxf.recover
    doc, _ = ezdxf.recover.readfile(str(generated / "synthetic-08-spaced-labels" / FC.DXF_FILE))
    texts = [e.dxf.text for e in doc.modelspace().query("TEXT")]
    assert "SALON" not in texts and "HAVUZ" not in texts
    assert all(texts.count(c) >= 1 for c in "HAVUZ")


@pytest.mark.xfail(strict=True, reason="failure class spaced_labels: the reader does not handle it yet (UL323): a "
                                       "letter-spaced label of two words loses its word gap ('Yatakodası')")
def test_08_spaced_room_labels_read_as_their_words(generated, read):
    t = truth_of(generated, "synthetic-08-spaced-labels")
    b = read("synthetic-08-spaced-labels")
    want = sorted(_fold(r["label"]) for r in t["per_level"]["L0"]["rooms"])
    assert sorted(_fold(r["label"]) for r in b["rooms"]) == want


def test_08_spaced_room_labels_give_the_room_types(generated, read):
    t = truth_of(generated, "synthetic-08-spaced-labels")
    b = read("synthetic-08-spaced-labels")
    assert sorted(r["room_type"] for r in b["rooms"]) == sorted(r["room_type"] for r in t["per_level"]["L0"]["rooms"])


@pytest.mark.xfail(strict=True, reason="failure class spaced_labels: the reader does not handle it yet (UL323): the "
                                       "site plan's 'H A V U Z' is not read, so no pool")
def test_08_spaced_pool_label_gives_the_pool(generated, read):
    t = truth_of(generated, "synthetic-08-spaced-labels")
    b = read("synthetic-08-spaced-labels")
    pools = (b.get("site") or {}).get("pools") or []
    assert len(pools) == 1
    assert Polygon(pools[0]["polygon"]).symmetric_difference(Polygon(t["site"]["pools"][0]["polygon"])).area < 0.1


# --- synthetic-09-jamb-stubs ---------------------------------------------------------------------------------------

def test_09_jamb_stubs_are_drawn(generated):
    import ezdxf.recover
    doc, _ = ezdxf.recover.readfile(str(generated / "synthetic-09-jamb-stubs" / FC.DXF_FILE))
    walls = list(doc.modelspace().query('LWPOLYLINE[layer=="DUVAR"]'))
    small = [e for e in walls if e.closed and len(e) == 4 and _box_size(e) in ((5.0, 7.0), (3.0, 5.0))]
    assert len(small) == 2 * 5                 # two stubs at one jamb of each of the five inner doors
    assert any(not e.closed for e in walls)    # the wall faces stop open at the jambs
    caps = doc.modelspace().query('LINE[layer=="KAPI"]')
    assert sum(1 for e in caps if round(math.dist(e.dxf.start, e.dxf.end), 3) == 16.0) == 5


def _box_size(e) -> tuple:
    xs = [p[0] for p in e.get_points()]
    ys = [p[1] for p in e.get_points()]
    return tuple(sorted((round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3))))


def test_09_doors_in_stub_jambs_are_read(generated, read):
    t = truth_of(generated, "synthetic-09-jamb-stubs")
    b = read("synthetic-09-jamb-stubs")
    doors = [o for o in b["openings"] if o["type"] == "door"]
    for d in t["per_level"]["L0"]["doors"]:
        assert any(math.dist(o["center"], d["center"]) <= CENTRE_TOL_M for o in doors), d


# --- synthetic-10-glazed-facade ------------------------------------------------------------------------------------

@_xfail("glazed_facade", "UL274", "the frames of the facade are read as one wide inferred window")
def test_10_glazed_facade_frames_are_its_door_and_windows(generated, read):
    b = read("synthetic-10-glazed-facade")
    on_facade = sorted((o["type"], round(o["width"], 1)) for o in b["openings"]
                       if o["center"][1] < 0.5 and o["center"][0] < 7.0)
    assert on_facade == [("door", 2.4), ("window", 1.1), ("window", 2.2)]


# --- synthetic-11-dimension-chains ---------------------------------------------------------------------------------

def test_11_notation_is_never_a_wall(generated, read):
    b = read("synthetic-11-dimension-chains")
    outline = Polygon([(0, 0), (12, 0), (12, 9), (0, 9)]).buffer(0.05)
    for w in b["walls"]:
        assert outline.contains(Point(w["start"])) and outline.contains(Point(w["end"])), w["id"]
    for o in b["openings"]:
        assert outline.contains(Point(o["center"])), o["id"]


# --- synthetic-12-mirrored-halves ----------------------------------------------------------------------------------

@_xfail("mirrored_halves", "UL276", "the unlabelled flat's rooms stay 'Oda'")
def test_12_mirrored_flat_rooms_take_their_twins_names(generated, read):
    b = read("synthetic-12-mirrored-halves")
    right = sorted(_fold(r["label"]) for r in b["rooms"] if Polygon(r["polygon"]).centroid.x > 7.0)
    assert right == ["banyo", "hol", "salon", "yatak odasi"]


# --- synthetic-13-typical-floor ------------------------------------------------------------------------------------

def test_13_typical_floor_truth_levels(generated):
    t = truth_of(generated, "synthetic-13-typical-floor")
    assert [(lv["id"], lv["elevation"]) for lv in t["levels"]] == [(f"L{k}", 3.0 * k) for k in range(7)]
    assert all(FC.counts(t)[f"L{k}"] == FC.counts(t)["L1"] for k in range(1, 7))
    assert t["typical_plan"]["levels"] == [f"L{k}" for k in range(1, 7)]


def test_13_typical_plan_stands_for_six_storeys(generated, read):
    b = read("synthetic-13-typical-floor")
    assert [(lv["id"], lv["elevation"]) for lv in b["levels"]] == [(f"L{k}", 3.0 * k) for k in range(7)]
    assert [_fold(lv["label"]) for lv in b["levels"]] == ["zemin kat"] + [f"{k}. normal kat" for k in range(1, 7)]


# --- synthetic-14-elevation-title ----------------------------------------------------------------------------------

@_xfail("elevation_title", "UL271", "a plan titled only '+3.00 KOTU KAT PLANI' is not a storey of its own")
def test_14_elevation_title_gives_the_storey(generated, read):
    b = read("synthetic-14-elevation-title")
    assert [(lv["id"], lv["elevation"]) for lv in b["levels"]] == [("L0", 0.0), ("L1", 3.0)]


# --- synthetic-15-winder-stair -------------------------------------------------------------------------------------

def _stair(b: dict) -> dict:
    stairs = [f for f in b["furniture"] if f.get("type") == "stair"]
    assert len(stairs) == 1
    return stairs[0].get("stair") or {}


@_xfail("winder_stair", "UL282", "the winders are read as a flat landing and the tread numbers are not used")
def test_15_winders_and_seventeen_treads(generated, read):
    t = truth_of(generated, "synthetic-15-winder-stair")
    st = _stair(read("synthetic-15-winder-stair"))
    assert t["per_level"]["L0"]["stairs"][0]["risers"] == 17
    assert not st.get("landing")                                   # the turn is winders, not a landing
    assert (st.get("risers") or st.get("treads")) == 17


# --- synthetic-16-open-recess --------------------------------------------------------------------------------------

def test_16_open_recess_is_outside_in_the_truth(generated):
    t = truth_of(generated, "synthetic-16-open-recess")
    recess = Polygon(t["open_air"][0]["polygon"])
    assert recess.area == pytest.approx(1.2 * 3.0)
    assert not any(Polygon(r["polygon"]).intersection(recess).area > 1e-6 for r in t["per_level"]["L0"]["rooms"])


def test_16_open_recess_is_no_room(generated, read):
    t = truth_of(generated, "synthetic-16-open-recess")
    b = read("synthetic-16-open-recess")
    recess = Polygon(t["open_air"][0]["polygon"])
    assert not any(Polygon(r["polygon"]).intersection(recess).area > 0.1 for r in b["rooms"])


# --- synthetic-17-garage-lift --------------------------------------------------------------------------------------

@_xfail("garage_lift", "UL320", "the garage's 3.4 m opening is read as a window")
def test_17_garage_has_its_wide_door(generated, read):
    b = read("synthetic-17-garage-lift")
    garage = [r for r in b["rooms"] if r["room_type"] == "garage"]
    assert len(garage) == 1
    wide = [o for o in b["openings"]
            if abs(o["width"] - 3.4) <= WIDTH_TOL_M and math.dist(o["center"], (9.5, 0.125)) < CENTRE_TOL_M]
    assert len(wide) == 1 and wide[0]["type"] == "door"


def test_17_lift_shaft_has_its_landing_door(generated, read):
    b = read("synthetic-17-garage-lift")
    shafts = [r for r in b["rooms"] if r["room_type"] == "shaft"]
    assert len(shafts) == 1
    poly = Polygon(shafts[0]["polygon"])
    doors = [o for o in b["openings"] if o["type"] == "door" and poly.exterior.distance(Point(o["center"])) < 0.2]
    assert len(doors) == 1 and doors[0]["width"] == pytest.approx(0.9, abs=WIDTH_TOL_M)


# --- synthetic-18-sheet-frame --------------------------------------------------------------------------------------

def test_18_sheet_frame_levels_from_the_plan_titles(generated, read):
    b = read("synthetic-18-sheet-frame")
    assert [(lv["id"], lv["elevation"]) for lv in b["levels"]] == [("L0", 0.0), ("L1", 3.0)]


@_xfail("sheet_frame", "UL268", "the section 1.5 m beside the plans inside the frame is no region of its own")
def test_18_sheet_frame_holds_three_titled_drawings(generated, read):
    read("synthetic-18-sheet-frame")
    t = truth_of(generated, "synthetic-18-sheet-frame")
    sheets = json.loads((_READS["synthetic-18-sheet-frame"][1] / "sheets.json").read_text(encoding="utf-8"))
    read_titles = {(r.get("title") or {}).get("text"): r["class"] for r in sheets["regions"]}
    for d in t["drawings"]:
        assert read_titles.get(d["title"]) == d["class"], d
