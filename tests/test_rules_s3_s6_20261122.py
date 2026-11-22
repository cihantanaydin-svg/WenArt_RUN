"""22 Nov 2026 (the user's pick "build S5, S3, S4, S6", ``results/rule_suggestions.md``): four reader rules, each with
its synthetic project read end to end through the CPU pipeline (generated into a temporary folder) and its checks.

- S5 (``ingest.generic.layer_geometry``, ``layer_names`` registry): a drawing whose layer names say nothing reads its
  layers' roles from their geometry; a name always wins; synthetic-31 (the base flat, layers L1..L10) and synthetic-24
  drawn with plain layers read as with the names.
- S3 (``sense_rules.doors_onto_nothing``): an upper-floor door onto nothing, with no swing or door block, on the window
  layer is a window; a swung door onto a drawn balcony stays a door (synthetic-29).
- S4 (``sense_rules.fire_stairs``): a fire stair's empty gap to a flat closes, its tagged door to the hall stays a door
  on every floor (synthetic-30).
- S6 (``openings.sliding_window_by_text``): door-layer sliding leaves with a window-high tag are a window, the lift's
  tagged sliding door stays a door (synthetic-32).
"""
from __future__ import annotations

import math

import pytest

from wenart.ingest.generic import layer_geometry as LG
from wenart.ingest.generic import layer_names as LN
from wenart.synthetic import failure_classes as FC
from wenart.synthetic import weak_projects as WP


def _read(project, root):
    from wenart.ingest import pipeline as PL

    FC.generate_failure_project(project, root)
    building, _build = PL.run_project(root / project.name, root / f"{project.name}-out", no_ai=True)
    return building


def _score(project, root, building):
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    truth = TR.synthetic_truth(project.name, root / project.name / FC.TRUTH_FILE)
    return SC.match(truth, TR.extract(building, project=project.name), building)["total"]


def _near(building, lid, at, kind=None, tol=0.35):
    return [o for o in building["openings"] if o["level_id"] == lid and math.dist(o["center"][:2], at) <= tol
            and (kind is None or o["type"] == kind)]


@pytest.fixture(scope="module")
def root(tmp_path_factory):
    return tmp_path_factory.mktemp("rules_s3_s6")


@pytest.fixture(autouse=True)
def _clean_registry():
    LN.clear_geometry_roles()
    yield
    LN.clear_geometry_roles()


# --- S5 -------------------------------------------------------------------------------------------------------------

def test_s5_the_registry_fills_only_layers_whose_name_says_nothing():
    assert LN.layer_role("L3") is None and not LN.names_silent()
    LN.set_geometry_roles("a.dxf", {"L3": {"role": "plaster", "why": "test"}, "DUVAR": "door"})
    assert LN.names_silent()
    assert LN.layer_role("L3") == "plaster" and LN.draws_walls("L3") and LN.layer_roles("L3") == {"plaster"}
    assert LN.layer_role("DUVAR") == "wall"                     # the name always wins
    LN.set_geometry_roles("b.dxf", {"L3": "door"})              # two documents disagree: no role
    assert LN.layer_role("L3") is None
    LN.set_geometry_roles("b.dxf", None)
    assert LN.layer_role("L3") == "plaster"


def test_s5_a_drawing_with_named_layers_is_not_touched(root):
    from wenart.ingest import dxf_generic as DG

    project = WP.project_24()
    FC.generate_failure_project(project, root)
    page, _info = DG.read_page_info(root / project.name / FC.DXF_FILE, "plan.dxf")
    assert not LG.names_say_nothing(page.strokes, page.texts)
    assert LG.roles_for(page.strokes, page.texts) is None


def test_s5_the_geometry_gives_the_plain_layers_their_roles(root):
    from wenart.ingest import dxf_generic as DG

    project = WP.project_31()
    FC.generate_failure_project(project, root)
    page, _info = DG.read_page_info(root / project.name / FC.DXF_FILE, "plan.dxf")
    assert LG.names_say_nothing(page.strokes, page.texts)
    roles = {k: v["role"] for k, v in LG.roles_for(page.strokes, page.texts, unit=0.01).items()}
    # the base flat's table order: DUVAR, KAPI, PENCERE, YAZI ... -> L1, L2, L3, L4
    assert roles == {"L1": "wall", "L2": "door", "L3": "window", "L4": "text"}


def test_s5_synthetic_31_reads_as_the_named_flat(root):
    project = WP.project_31()
    b = _read(project, root)
    assert _score(project, root, b) == 100.0
    sheets = (root / f"{project.name}-out" / "sheets.json").read_text(encoding="utf-8")
    assert "layer_roles_geometry" in sheets


def test_s5_sliding_sashes_on_a_plain_window_layer_stay_windows(root):
    project = WP.project_24()
    project.name, project.plain_layers = "synthetic-24-plain", True
    b = _read(project, root)
    assert _score(project, root, b) == 100.0


# --- S3 -------------------------------------------------------------------------------------------------------------

def test_s3_an_upper_floor_door_onto_nothing_on_the_window_layer_is_a_window(root):
    project = WP.project_29()
    b = _read(project, root)
    assert _score(project, root, b) == 100.0
    salon = _near(b, "L1", (2.0, 0.125))
    assert [o["type"] for o in salon] == ["window"]
    assert salon[0]["adjusted_by_ai"]["rule"] == "door_onto_nothing" and salon[0]["drawn_type"] == "door"
    assert [o["type"] for o in _near(b, "L1", (9.5, 0.125))] == ["door"]      # onto the drawn balcony
    assert [o["type"] for o in _near(b, "L0", (2.0, 0.125))] == ["window"]
    recs = b["level_inference"]["sense_rules"]["doors_onto_nothing"]
    assert [r["how"] for r in recs] == ["door to window"]


# --- S4 -------------------------------------------------------------------------------------------------------------

def test_s4_a_fire_stair_enclosure_has_no_doorless_gap_on_every_floor(root):
    project = WP.project_30()
    b = _read(project, root)
    assert _score(project, root, b) == 100.0
    for lid in ("L0", "L1", "L2", "L3"):
        assert not _near(b, lid, (4.0, 7.4)), lid                       # the empty gap to the MUTFAK closes
        assert [o["type"] for o in _near(b, lid, (5.2, 5.8))] == ["door"], lid   # the tagged door to the hall
    closed = [r for r in b["level_inference"]["sense_rules"]["fire_stairs"] if r["how"] == "closed"]
    assert len(closed) == 4
    assert all(m.get("closed") for m in b["openings_merged"] if m.get("corrected_by_ai", {}).get("rule")
               == "fire_stair_closed")


# --- S6 -------------------------------------------------------------------------------------------------------------

def test_s6_door_layer_sliding_leaves_with_a_window_tag_are_a_window_the_lift_keeps_its_door(root):
    project = WP.project_32()
    b = _read(project, root)
    assert _score(project, root, b) == 100.0
    win = _near(b, "L0", (5.0, 0.125))
    assert [o["type"] for o in win] == ["window"] and win[0].get("operation") == "sliding"
    assert [o["type"] for o in _near(b, "L0", (2.0, 5.8))] == ["door"]          # the lift's sliding door
