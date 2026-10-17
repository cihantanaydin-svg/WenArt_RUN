"""Milestone 13 fix round after P3 (16-17 Oct 2026), track I_ingest: the secondary plan page, the stale wait, the
camera model.

What:
1. ``pipeline._merge_secondary``: an extra element of a secondary page is added (unverified) only when it neither
   repeats nor crosses the master's: a wall on the line of a master wall is trimmed and not added when nothing is
   left or what is left runs through a master room; a door beside a master door on the same wall, a piece over a
   master piece or the same piece drawn elsewhere are not added; the ``count_mismatch`` conflict lists them
   (``not_added`` with the entity ids, "not added" in the resolution). A garden wall outside every room and a piece
   the master lacks are still added.
2. ``reading``: a secondary page's questions are never asked (``NOT_ASKED_KEY``): nothing waits for them, its items
   never stand for the master's piece, none of its keys is withdrawn; ``never_a_box`` clears the waiting reason of a
   piece that no longer waits. The pipeline writes a secondary page's crops to its own folder and publishes them
   when the page is asked after all.
3. ``camsearch.RoomModel``: a wall of the level standing inside a room outline is a wall of the model (both faces,
   its openings) and an obstacle of the camera points.
Why: P3 (real04): the second plan region r16 of the ground floor sealed a bedroom bay with a drawn desk in it (the
search planned a view of the hidden desk, model share 0.088), added second copies of doors, wardrobes, beds and
desks, kept six bedroom pieces "waiting for the answers" in the run with the answers, and wrote its crops over the
master's crops of the same key (the AI read r16's shower for r5's desk question). Every test fails on the old code.
Fix round part 2 (17 Oct 2026, after the review of part 1): the rules alone (a quarter of a missed piece, one extra
per missed piece, a door whose span overlaps the master's), real04's 46 % beds in the two-page run, an unknown
piece only the never-asked page drew, the crops through ``run_project`` (the master's under its keys, a furniture
plan's and a second master's published), the camera points of the bay without its desk and the fallback point
beside a wall stub; each fails when the part of the fix it covers is taken out. 4. ``scripts/jobs/full.sh``
``RUN_FRESH_RECOGNITION`` (lead decision for pod P5): real04's stored answers, given on the wrong crops, are moved
aside once so their questions are asked again (fails on the old full.sh).
How: synthetic DXF pages (wenart.synthetic), generic DXF pages from tests/fixtures/synthetic-06-titled, the hand-made
rooms of tests/_m11_room.py, a hand-made L room, the full.sh sandbox of tests/test_full_job.py.
"""
import copy
import dataclasses
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import _m11_room as M
from wenart.blender import camsearch as C
from wenart.blender import geom2d
from wenart.ingest import pipeline as PL
from wenart.ingest.generic import reading as RD
from wenart.ingest.model import FurnitureItem, LevelExtraction
from wenart.synthetic.dxf_writer import write_dxf
from wenart.synthetic.model import Furniture, Wall
from wenart.synthetic.projects import level_01_zemin

MODEL_HIDDEN_SHARE = 0.005          # tests/gpu/test_render.py: a listed piece may be absent below this model share


# --------------------------------------------------------------------------
# 1. The secondary page's extras
# --------------------------------------------------------------------------

def _write(project: Path, level, file: str) -> None:
    project.mkdir(parents=True, exist_ok=True)
    write_dxf(level, project / file, file, title_raw=level.title_raw, page_class="floor_plan")


def _conflict(building: dict, what: str) -> dict:
    return next(c for c in building["conflicts"] if c["kind"] == "count_mismatch" and f" {what}" in c["description"])


@pytest.fixture(scope="module")
def two_pages(tmp_path_factory):
    """The master DXF (synthetic-01 ground floor without its sofa) and a second DXF of the level that draws: the
    Hol | Banyo wall run on 2.35 m into the bedroom, the Salon | Mutfak wall 11 mm off, a garden wall outside the
    house, the bathroom door 0.15 m along its wall, the wardrobe 0.12 m along, the double bed 1.08 m along (46 % of
    it over the master's bed, real04's r16 beds), one nightstand at another place in the bedroom and a second one
    beside it (fix round part 2, 17 Oct 2026: the master's one missed nightstand explains one of them only) and the
    sofa the master lacks."""
    tmp = tmp_path_factory.mktemp("fixround")
    level = level_01_zemin()
    master = copy.deepcopy(level)
    master.furniture = level.furniture[1:]
    second = copy.deepcopy(level)
    second.walls[7] = dataclasses.replace(second.walls[7], start=(7.0, 1.5))
    second.walls[5] = dataclasses.replace(second.walls[5], start=(0.25, 5.211), end=(5.25, 5.211))
    second.walls.append(Wall(start=(10.5, 0.0), end=(10.5, 3.0), thickness=0.2, exterior=False, id="w_garden"))
    door = next(k for k, o in enumerate(second.openings) if o.wall_index == 7)
    second.openings[door] = dataclasses.replace(second.openings[door], center=(7.0, 5.55))
    for k, f in enumerate(second.furniture):
        if f.block == "DOLAP":
            second.furniture[k] = dataclasses.replace(f, center=(9.0, 1.62))
        elif f.block == "KOMIDIN" and f.center == (6.65, 3.5):
            second.furniture[k] = Furniture("KOMIDIN", (6.0, 1.0), 0.0)
        elif f.block == "YATAK_CIFT":
            second.furniture[k] = dataclasses.replace(f, center=(7.8, 1.62))
    second.furniture.append(Furniture("KOMIDIN", (6.0, 2.0), 0.0))
    project = tmp / "p"
    _write(project, master, "zemin_kat.dxf")
    _write(project, second, "zemin_kat_b.dxf")
    seconds = []
    merge = PL._merge_secondary

    def spy(build, level_id, label, master_work, work, *rest):
        seconds.append(work)
        return merge(build, level_id, label, master_work, work, *rest)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(PL, "_merge_secondary", spy)
        building, build = PL.run_project(project, tmp / "out")
    return building, build, seconds


def test_an_extra_wall_on_a_master_walls_line_or_through_a_room_is_not_added(two_pages):
    building, _build, _seconds = two_pages
    walls = building["walls"]
    added = [w for w in walls if w["status"] == "unverified"]
    # Only the garden wall outside every room is added; the old code added all three extras.
    assert [(w["start"], w["end"]) for w in added] == [([10.5, 0.0], [10.5, 3.0])]
    conflict = _conflict(building, "walls")
    reasons = sorted(e["reason"] for e in conflict["not_added"])
    assert len(reasons) == 2 and "1 extra from DXF added as unverified" in conflict["resolution"]
    assert "2 extra from DXF not added" in conflict["resolution"]
    through = next(e for e in conflict["not_added"] if "runs through" in e["reason"])
    assert "r_L0_yatak_odasi" in through["reason"] and "2.35 m left after the trim" in through["reason"]
    assert through["kind"] == "wall" and through["entity"].startswith("LWPOLYLINE:")
    again = next(e for e in conflict["not_added"] if "the same wall drawn again" in e["reason"])
    assert again["entity"].startswith("LWPOLYLINE:") and again["element_ids"]
    # The conflict names the master walls and the room the extras repeat or cross.
    assert "r_L0_yatak_odasi" in conflict["element_ids"] and set(through["element_ids"]) <= set(conflict["element_ids"])
    assert any("not added" in w and "runs through" in w for w in building["warnings"])


def test_an_extra_door_beside_the_masters_and_pieces_drawn_again_are_not_added(two_pages):
    building, _build, _seconds = two_pages
    assert not [o for o in building["openings"] if o["status"] == "unverified"]
    doors = _conflict(building, "doors")
    assert "1 extra from DXF not added" in doors["resolution"] and "added as unverified" not in doors["resolution"]
    (entry,) = doors["not_added"]
    assert entry["kind"] == "door" and "0.15 m from the master's door" in entry["reason"]
    assert entry["entity"].startswith("INSERT:") and entry["element_ids"][0] in doors["element_ids"]
    furniture = _conflict(building, "furniture pieces")
    extra = [f for f in building["furniture"] if f["status"] == "unverified"]
    # The piece the master lacks is still added, and so is the second nightstand beside the one drawn elsewhere:
    # the master's one missed nightstand explains one extra only (fix round part 2: the ``used`` bookkeeping).
    assert sorted(f["type"] for f in extra) == ["nightstand", "sofa"]
    assert "2 extra from DXF added as unverified" in furniture["resolution"]
    assert "3 extra from DXF not added" in furniture["resolution"]
    reasons = [e["reason"] for e in furniture["not_added"]]
    wardrobe = next(r for r in reasons if "wardrobe" in r)
    assert wardrobe.startswith("it overlaps the master's wardrobe") and "drawn again" in wardrobe
    stand = next(r for r in reasons if "nightstand" in r)
    assert "drawn elsewhere" in stand and stand.startswith("the same nightstand footprint")
    # Fix round part 2: real04's duplicate beds: 46 % over the master's bed, which the second page does not draw at
    # its place, is under the 50 % rule; the quarter rule for a missed piece refuses it (not the size rule).
    (bed,) = [r for r in reasons if "bed_double" in r]
    assert bed.startswith("it overlaps the master's bed_double") and "by 46% of the smaller footprint" in bed
    assert "which the page does not draw at its place" in bed
    assert len([f for f in building["furniture"] if f["type"] == "wardrobe"]) == 1
    assert len([f for f in building["furniture"] if f["type"] == "nightstand"]) == 3
    assert len([f for f in building["furniture"] if f["type"] == "bed_double"]) == 1


def test_the_secondary_page_is_marked_as_never_asked(two_pages):
    """The second DXF's questions are never written to requests.json (only ``furniture_works`` are): its report says so,
    so the reading step waits for none of them; the master's report does not."""
    _building, build, seconds = two_pages
    (second,) = seconds
    assert second.extraction.report[RD.NOT_ASKED_KEY].startswith("secondary page of L0")
    assert all(RD.NOT_ASKED_KEY not in w.extraction.report for w in build.furniture_works)
    assert all(w is not second for w in build.furniture_works)


def test_extra_wall_problem_trims_collinear_parts_and_measures_what_is_left_in_rooms():
    """The rule alone, on real04's numbers: r16's 10.1 m wall on the line of r5's 7.5 m w_L0_012 leaves 2.6 m in the
    bedroom bay (not added); r16's near-duplicate of the north wall (1 mm off) leaves nothing; a wall that only
    touches a room outline (its centre line on the outline) is added."""
    room = {"id": "r_L0_yatak_odasi_4", "polygon": [[0.2, 9.2], [1.2, 9.2], [1.2, 7.142], [4.218, 7.142],
                                                     [4.218, 11.8], [0.2, 11.8]]}
    w012 = {"id": "w_L0_012", "start": [1.1, 1.7], "end": [1.1, 9.2], "thickness": 0.2}
    w009 = {"id": "w_L0_009", "start": [0.0, 11.9], "end": [17.172, 11.9], "thickness": 0.2}
    item = SimpleNamespace(start=(1.1, 1.6991), end=(1.1, 11.7991), thickness=0.2)
    reason, ids = PL._extra_wall_problem(item, [w012, w009], [room])
    assert ids == ["w_L0_012", "r_L0_yatak_odasi_4"] and "2.60 m left" in reason
    near = SimpleNamespace(start=(1.0, 11.8991), end=(16.172, 11.8991), thickness=0.2)
    reason, ids = PL._extra_wall_problem(near, [w012, w009], [room])
    assert ids == ["w_L0_009"] and "the same wall drawn again" in reason
    along = SimpleNamespace(start=(4.218, 7.142), end=(4.218, 11.8), thickness=0.1)
    assert PL._extra_wall_problem(along, [w012, w009], [room]) is None


def _master_piece(pid, kind, center, size, room="r"):
    return {"id": pid, "type": kind, "room_id": room,
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": 0.0}}


def test_extra_furniture_problem_a_quarter_of_a_missed_piece_and_one_extra_per_missed_piece():
    """Fix round part 2 (17 Oct 2026), the rule alone: an extra piece 30 % over a master piece the secondary page
    does not draw at its place (``missing``) is that piece drawn again (``EXTRA_FURNITURE_MISSED``, real04's r16 beds
    at 46 %); the same overlap on a piece the page does draw at its place is another piece (under the 50 % rule),
    added. A missed piece explains one extra of its type and size in its room (``used``): the second is added, and
    so is one in another room."""
    rooms = [{"id": "r", "polygon": [[0.0, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]]},
             {"id": "r2", "polygon": [[5.0, 0.0], [9.0, 0.0], [9.0, 4.0], [5.0, 4.0]]}]
    bed = _master_piece("f_L0_009", "bed_double", (2.0, 2.0), (1.6, 2.0))
    stand = _master_piece("f_L0_011", "nightstand", (0.5, 3.5), (0.5, 0.4))
    shifted = SimpleNamespace(type="bed_double", center=(2.0, 0.6), size=(1.6, 2.0), rotation_deg=0.0)  # 30 % over
    reason, ids = PL._extra_furniture_problem(shifted, [bed, stand], [bed], rooms, set())
    assert ids == ["f_L0_009"] and reason.startswith("it overlaps the master's bed_double f_L0_009 by 30%")
    assert "which the page does not draw at its place" in reason
    assert PL._extra_furniture_problem(shifted, [bed, stand], [], rooms, set()) is None
    # One missed nightstand, two extras of its size in its room: the first is it drawn elsewhere, the second is added.
    used: set = set()
    first = SimpleNamespace(type="nightstand", center=(4.5, 0.5), size=(0.5, 0.4), rotation_deg=0.0)
    second = SimpleNamespace(type="nightstand", center=(4.5, 1.5), size=(0.4, 0.5), rotation_deg=90.0)
    reason, ids = PL._extra_furniture_problem(first, [bed, stand], [stand], rooms, used)
    assert ids == ["f_L0_011"] and "drawn elsewhere" in reason and used == {"f_L0_011"}
    assert PL._extra_furniture_problem(second, [bed, stand], [stand], rooms, used) is None
    elsewhere = SimpleNamespace(type="nightstand", center=(6.0, 1.0), size=(0.5, 0.4), rotation_deg=0.0)
    assert PL._extra_furniture_problem(elsewhere, [bed, stand], [stand], rooms, set()) is None


def test_extra_opening_problem_refuses_a_door_whose_span_overlaps_the_masters():
    """Fix round part 2, the rule alone: a wide extra door 0.60 m from a master door on its wall (more than
    ``EXTRA_OPENING_NEAR``) whose span overlaps the master's (two leaves in one place) is that door drawn again; a
    door whose span clears the master's, or a door on another wall, is added."""
    walls = [{"id": "w1", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.2},
             {"id": "w2", "start": [0.0, 3.0], "end": [6.0, 3.0], "thickness": 0.2}]
    door = {"id": "d_L0_001", "type": "door", "wall_id": "w1", "center": [2.0, 0.0], "width": 0.9}
    wide = SimpleNamespace(center=(2.6, 0.0), rotation_deg=0.0, width=1.0)
    reason, ids = PL._extra_opening_problem(wide, [door], walls)
    assert ids == ["d_L0_001"] and reason.startswith("0.60 m from the master's door d_L0_001 on wall w1")
    clear = SimpleNamespace(center=(3.0, 0.0), rotation_deg=0.0, width=0.9)          # 1.00 m: the spans touch not
    assert PL._extra_opening_problem(clear, [door], walls) is None
    across = SimpleNamespace(center=(2.0, 3.0), rotation_deg=0.0, width=0.9)
    assert PL._extra_opening_problem(across, [door], walls) is None


# --------------------------------------------------------------------------
# 2. Pages whose questions are never asked; the stale wait
# --------------------------------------------------------------------------

def _work(report, **details):
    items = [SimpleNamespace(element_id=pid, details=dict(det)) for pid, det in details.items()]
    return SimpleNamespace(extraction=SimpleNamespace(furniture=items, report=dict(report), level_id="L0"))


def _piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def test_a_secondary_pages_open_questions_keep_no_piece_waiting():
    """The master page got its answers (``answers_applied``); the second page of the level (never asked) still lists
    its questions as pending, under the same key numbers. Neither the master's piece the second page drew too (m)
    nor the second page's own piece (s) waits: both go through the rules (here: a drawn mark, a detail). The old code
    left both 'waiting for the answers', not built and not listed."""
    mark_m = M.fp("m", "unknown", (2.5, 2.0), (0.12, 0.05), front=None)
    mark_s = M.fp("s", "unknown", (3.5, 2.0), (0.12, 0.05), front=None)
    build = PL.ProjectBuild(M.building(furniture=[mark_m, mark_s]))
    works = {"master": _work({"questions": [{"key": "sym_L0_003"}], "pending": [], "answers_applied": 1},
                             m={"candidate_key": "sym_L0_003"}),
             "second": _work({"questions": [{"key": "sym_L0_001"}, {"key": "sym_L0_003"}],
                              "pending": ["sym_L0_001", "sym_L0_003"], RD.NOT_ASKED_KEY: "secondary page of L0"},
                             s={"candidate_key": "sym_L0_003"})}
    drawn_too = SimpleNamespace(element_id="m", details={"candidate_key": "sym_L0_001"})   # the second page's m
    works["second"].extraction.furniture.append(drawn_too)
    RD.read_furniture(build, works)
    for pid in ("m", "s"):
        f = _piece(build.building, pid)
        assert f.get("not_built_reason") != RD.WAITS_REASON and f["inferred_as"] == "detail", (pid, f)
    # The master's item stands for m (its key, its crop), not the second page's drawing of it.
    assert RD._items(build, works)["m"].details["candidate_key"] == "sym_L0_003"
    assert RD._pending(build, works) == set()


def test_the_pipelines_pending_pieces_leave_out_a_page_never_asked():
    """``pipeline._pending_piece_ids`` (the inference after the reading step) holds back only the pieces of the pages
    whose questions are asked: real04's r16 kept f_L0_021 / f_L0_024 out of the inference in the run with the
    answers."""
    build = PL.ProjectBuild(M.building())
    master = _work({"pending": ["sym_L0_002"]}, a={"candidate_key": "sym_L0_002"})
    second = _work({"pending": ["sym_L0_001", "sym_L0_002"], RD.NOT_ASKED_KEY: "secondary page of L0"},
                   m={"candidate_key": "sym_L0_001"}, s={"candidate_key": "sym_L0_002"})
    build.generic = [master, second]
    assert PL._pending_piece_ids(build) == {"a"}


def test_a_secondary_pages_key_never_withdraws_the_masters_question():
    """Code typed the second page's own piece s, whose key sym_L0_004 the master uses for another piece (a, still
    asked): nothing is withdrawn (s was never asked). The old code withdrew the master's question of a."""
    build = PL.ProjectBuild(M.building(furniture=[M.fp("a", "unknown", (1.0, 1.0), (0.5, 0.4), front=None),
                                                  M.fp("s", "nightstand", (3.0, 1.0), (0.5, 0.4))]))
    works = {"master": _work({"questions": [{"key": "sym_L0_004"}], "pending": ["sym_L0_004"]},
                             a={"candidate_key": "sym_L0_004"}),
             "second": _work({"questions": [{"key": "sym_L0_004"}], "pending": ["sym_L0_004"],
                              RD.NOT_ASKED_KEY: "secondary page of L0"}, s={"candidate_key": "sym_L0_004"})}
    items = RD._items(build, works)
    assert RD.withdraw_questions(build, works, items, ["s"], {"s": "twin"}) == {}
    assert works["master"].extraction.report["pending"] == ["sym_L0_004"] and build.code_typed == {}
    assert RD.open_questions(build, works, items) == {"a"}
    # Fix round part 2 (17 Oct 2026): when code types the master's a, its question is withdrawn from the master's
    # report only; the never-asked page's report keeps its own list (its key is another piece's).
    assert RD.withdraw_questions(build, works, items, ["a"], {"a": "twin"}) == {"sym_L0_004": "a"}
    assert works["master"].extraction.report["pending"] == [] and build.code_typed == {"sym_L0_004": "a"}
    second = works["second"].extraction.report
    assert second["pending"] == ["sym_L0_004"] and RD.CODE_TYPED_KEY not in second
    assert RD.CODE_METHODS_KEY not in second


def test_open_questions_leave_out_an_unknown_piece_only_a_never_asked_page_drew():
    """Fix round part 2 (17 Oct 2026): the master's a waits for its question sym_L0_004; the never-asked second page
    drew another piece s, still unknown, under the same key number (and the stored answers of that key were applied
    to its own question there). Only a is open: s has no asked question (the old filter-less code held s too, with
    no front and no copies), and an answer applied on a never-asked page decides none of the master's questions."""
    build = PL.ProjectBuild(M.building(furniture=[M.fp("a", "unknown", (1.0, 1.0), (0.5, 0.4), front=None),
                                                  M.fp("s", "unknown", (3.0, 1.0), (0.7, 0.45), front=None)]))
    works = {"master": _work({"questions": [{"key": "sym_L0_004"}], "pending": ["sym_L0_004"]},
                             a={"candidate_key": "sym_L0_004"}),
             "second": _work({"questions": [{"key": "sym_L0_004"}], "pending": [], "answers_applied": 1,
                              RD.NOT_ASKED_KEY: "secondary page of L0"}, s={"candidate_key": "sym_L0_004"})}
    items = RD._items(build, works)
    assert set(items) == {"a", "s"}
    assert RD.answered_keys(build, works) == set()
    assert RD.open_questions(build, works, items) == {"a"}


def test_never_a_box_lists_a_piece_whose_wait_is_over():
    """A piece marked 'waits for the answers' by an earlier pass that no longer waits is listed for review (the old
    code kept the stale reason: not built, not listed)."""
    build = PL.ProjectBuild(M.building(furniture=[M.fp("u", "unknown", (2.5, 2.0), (1.45, 0.91), front=None,
                                                        type_candidates=[{"type": "desk"}, {"type": "sofa"}])]))
    items = {"u": SimpleNamespace(element_id="u", details={"candidate_key": "sym_L0_007"})}
    assert RD.never_a_box(build, items, {"u"}) == 0
    f = _piece(build.building, "u")
    assert f["build"] is False and f["not_built_reason"] == RD.WAITS_REASON
    assert RD.never_a_box(build, items, set()) == 1
    (entry,) = build.building["needs_review"]
    assert entry["id"] == "u" and "(AI passes: desk, sofa)" in entry["reason"]
    assert entry["crop"] == "recognition/crops/sym_L0_007_ctx.png"
    assert f["build"] is False and f["not_built_reason"] != RD.WAITS_REASON


def test_a_secondary_pages_crops_go_to_its_own_folder_and_are_published_when_asked(tmp_path, monkeypatch):
    """``_crop_leads`` picks the first page of each level as the master does; a second page writes its crops to
    recognition/secondary/<page>/crops (``report["crop_dir"]``, each candidate's ``details["crop_dir"]``, which
    ``reading._crop`` reads); ``_publish_crops`` copies them to recognition/crops when that page is asked after all.
    The old code wrote every page's crops to recognition/crops: r16's sym_L0_007 replaced r5's."""
    from wenart.ingest.generic import core

    def rec(region, rank_file="deneme1.dwg", level="L0"):
        return SimpleNamespace(extractor="generic", level_id=level, kind="vector", page_class="floor_plan",
                               level_problem=None, skip_reason=None, region_id=region, format="dwg", file=rank_file,
                               page=1, base_level_id=None, key=(rank_file, 1, region))

    r5, r16, r9 = rec("r5"), rec("r16"), rec("r9", level="L1")
    assert PL._crop_leads([r5, r16, r9], set(), None) == {r5.key, r9.key}
    assert PL._crop_leads([r16, r5], set(), None) == {r16.key}          # the read order breaks the tie, as the master

    seen = {}

    def fake_extract(page, level_id, file, answers=None, no_ai=False, rec_dir=None, origin=None):
        seen["rec_dir"] = rec_dir
        crops = Path(rec_dir) / "crops"
        crops.mkdir(parents=True, exist_ok=True)
        for name in ("sym_L0_007_ctx.png", "sym_L0_007_iso.png"):
            (crops / name).write_bytes(b"r16")
        ex = LevelExtraction(file=file, page=1, level_id=level_id, units="mm")
        ex.furniture = [FurnitureItem("unknown", None, (1.0, 1.0), (1.4, 0.9), 0.0, None, [0, 0, 1, 1], "INSERT:1",
                                      {}, details={"candidate_key": "sym_L0_007"})]
        ex.report = {"questions": [{"key": "sym_L0_007", "images": ["crops/sym_L0_007_ctx.png",
                                                                    "crops/sym_L0_007_iso.png"]}]}
        return ex

    monkeypatch.setattr(core, "extract", fake_extract)
    record = SimpleNamespace(generic_page=object(), region_id=None, region_transform=None, units_override=None,
                             format="dxf", file="plans/b.dxf", page=1, level_id="L0", scale=None)
    ex = PL._extract_generic(record, tmp_path, None, False, None, lead=False)
    assert seen["rec_dir"] == tmp_path / "recognition" / "secondary" / "b_p1"
    assert ex.report["crop_dir"] == "recognition/secondary/b_p1/crops"
    assert RD._crop(ex.furniture[0].details) == "recognition/secondary/b_p1/crops/sym_L0_007_ctx.png"
    assert not (tmp_path / "recognition" / "crops" / "sym_L0_007_ctx.png").exists()
    build = PL.ProjectBuild(M.building())
    build.out_dir = tmp_path
    work = PL.PageWork(record=SimpleNamespace(file="plans/b.dxf", format="dxf", page=1), extraction=ex)
    assert PL._publish_crops(build, work) == 2
    assert (tmp_path / "recognition" / "crops" / "sym_L0_007_ctx.png").read_bytes() == b"r16"
    assert "crop_dir" not in ex.report and RD._crop(ex.furniture[0].details) == "recognition/crops/sym_L0_007_ctx.png"
    record.generic_page = object()                                          # the pipeline drops the page once read
    PL._extract_generic(record, tmp_path, None, False, None)               # the lead page: recognition/crops
    assert seen["rec_dir"] == tmp_path / "recognition"


GENERIC_PLAN = Path(__file__).parent / "fixtures" / "synthetic-06-titled" / "synthetic-06-titled.dxf"
BOX_HERE = ((610.0, 440.0), (12.0, 12.0))      # inches: a 0.30 m square in the lobby (no code rule types it)
BOX_THERE = ((540.0, 560.0), (24.0, 24.0))     # a 0.61 m square in the bed room


def _generic_page(path: Path, box=None, title=None, furniture=True, unscaled=False) -> None:
    """A generic DXF page (not the synthetic convention): synthetic-06's titled ground floor plan (inches). ``box`` =
    (insert point, (width, depth)) adds an untyped block on the furniture layer, which the core asks for (the first
    candidate of a page is ``sym_L0_001`` on every page); ``title`` replaces the plan title; ``furniture`` False
    leaves the drawn pieces out; ``unscaled`` leaves no scale source ($INSUNITS 0, no dimensions)."""
    import ezdxf

    doc = ezdxf.readfile(GENERIC_PLAN)
    msp = doc.modelspace()
    if not furniture:
        for e in list(msp.query("INSERT[layer=='A-FURN']")):
            msp.delete_entity(e)
    if title:
        for e in msp.query("TEXT"):
            if e.dxf.text == "GROUND FLOOR PLAN":
                e.dxf.text = title
    if unscaled:
        doc.header["$INSUNITS"] = 0
        for e in list(msp.query("DIMENSION")):
            msp.delete_entity(e)
    if box is not None:
        (x, y), (w, h) = box
        block = doc.blocks.new("BOX-A")
        block.add_lwpolyline([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], close=True)
        msp.add_blockref("BOX-A", (x, y), dxfattribs={"layer": "A-FURN"})
    doc.saveas(path)


def _crop_run(tmp_path: Path, pages: dict, monkeypatch) -> tuple:
    """``run_project`` on generic pages of one level; returns the building, the build, the output folder and, per
    page, the crop images in the folder its extraction wrote to, read right after that extraction."""
    from wenart.ingest.generic import core

    project = tmp_path / "p"
    project.mkdir()
    for name, kw in pages.items():
        _generic_page(project / name, **kw)
    written: dict = {}
    extract = core.extract

    def spy(page, level_id, file, **kw):
        ex = extract(page, level_id, file, **kw)
        crops = Path(kw["rec_dir"]) / "crops"
        written[file] = {p.name: p.read_bytes() for p in crops.glob("sym_*.png")} if crops.is_dir() else {}
        return ex

    monkeypatch.setattr(core, "extract", spy)
    building, build = PL.run_project(project, tmp_path / "out")
    return building, build, tmp_path / "out", written


CROP_NAMES = ("sym_L0_001_ctx.png", "sym_L0_001_iso.png")


def test_run_project_keeps_the_masters_crops_under_its_keys(tmp_path, monkeypatch):
    """Fix round part 2 (17 Oct 2026), the crop collision through ``run_project``: two generic plan pages of one level,
    each with an untyped block the core asks for under the same key sym_L0_001 (real04: r5 and r16). The asked
    question's crops in recognition/crops are the master's (a.dxf, first by file order); b.dxf's crops of that key
    are in recognition/secondary/b_p1/crops. The old code (and ``lead`` always True) wrote b's over a's."""
    from wenart.recognition import answers as A

    building, build, out, written = _crop_run(tmp_path, {"a.dxf": {"box": BOX_HERE}, "b.dxf": {"box": BOX_THERE}},
                                              monkeypatch)
    assert [q["key"] for q in build.questions] == ["sym_L0_001"]
    (item,) = A.read_requests(out / "recognition")["items"]
    assert [Path(p).name for p in item["images"]] == list(CROP_NAMES)
    main, side = out / "recognition" / "crops", out / "recognition" / "secondary" / "b_p1" / "crops"
    for name in CROP_NAMES:
        assert (main / name).read_bytes() == written["a.dxf"][name]
        assert (side / name).read_bytes() == written["b.dxf"][name] != written["a.dxf"][name]
    assert not any("crop images published" in w for w in building["warnings"])


@pytest.mark.parametrize("case", ["furniture_plan", "first_page_unread"])
def test_run_project_publishes_the_crops_of_an_asked_page_that_is_not_the_first(tmp_path, monkeypatch, case):
    """Fix round part 2: the page whose question is asked is not its level's first page (``_crop_leads``): a furniture
    plan furnishes a level whose floor plan draws no furniture, or the first page cannot be read (no scale source)
    and the second becomes the master. Its crops went to its own folder; ``run_project`` publishes them to
    recognition/crops, where requests.json points, and its piece's crop points there too."""
    second = {"box": BOX_HERE}
    if case == "furniture_plan":
        pages = {"a.dxf": {"furniture": False}, "b.dxf": dict(second, title="GROUND FLOOR FURNITURE PLAN")}
    else:
        pages = {"a.dxf": {"unscaled": True}, "b.dxf": second}
    building, build, out, written = _crop_run(tmp_path, pages, monkeypatch)
    assert [q["key"] for q in build.questions] == ["sym_L0_001"] and written["a.dxf"] == {}
    main, side = out / "recognition" / "crops", out / "recognition" / "secondary" / "b_p1" / "crops"
    for name in CROP_NAMES:
        assert (main / name).read_bytes() == (side / name).read_bytes() == written["b.dxf"][name]
    assert "b.dxf: its recognition questions are asked; 2 crop images published to recognition/crops" \
        in building["warnings"]
    (work,) = build.furniture_works
    assert work.record.file == "b.dxf" and "crop_dir" not in work.extraction.report
    (piece,) = [f for f in work.extraction.furniture if f.details.get("candidate_key") == "sym_L0_001"]
    assert RD._crop(piece.details) == "recognition/crops/sym_L0_001_ctx.png"
    if case == "first_page_unread":
        assert any("a.dxf p1: no scale source" in w for w in building["warnings"])


# --------------------------------------------------------------------------
# 3. The camera model: walls inside a room outline
# --------------------------------------------------------------------------

def _bay_room(door: bool = False) -> dict:
    """real04's bedroom bay in small: an L outline whose bay (x 0..1.2, y 2..4) a wall along x = 1.1 closes; a desk
    stands in the bay. Walls around the outline are 0.2 m thick, centre lines outside it."""
    poly = [[0.0, 2.0], [1.2, 2.0], [1.2, 0.0], [5.0, 0.0], [5.0, 4.0], [0.0, 4.0]]
    walls = [{"id": "w_s", "level_id": "L0", "start": [1.0, -0.1], "end": [5.2, -0.1], "thickness": 0.2},
             {"id": "w_e", "level_id": "L0", "start": [5.1, -0.2], "end": [5.1, 4.2], "thickness": 0.2},
             {"id": "w_n", "level_id": "L0", "start": [5.2, 4.1], "end": [-0.2, 4.1], "thickness": 0.2},
             {"id": "w_w", "level_id": "L0", "start": [-0.1, 4.2], "end": [-0.1, 1.8], "thickness": 0.2},
             {"id": "w_bs", "level_id": "L0", "start": [-0.2, 1.9], "end": [1.2, 1.9], "thickness": 0.2},
             {"id": "w_bay", "level_id": "L0", "start": [1.1, -0.2], "end": [1.1, 4.0], "thickness": 0.2}]
    openings = []
    if door:
        openings.append({"id": "d_in", "level_id": "L0", "type": "door", "wall_id": "w_bay", "center": [1.1, 3.0],
                         "width": 0.9, "sill_height": 0.0, "height": 2.1})
    desk = {"id": "desk", "type": "desk", "room_id": "r", "level_id": "L0", "front_deg": 0.0,
            "footprint": {"center": [0.5, 3.0], "size": [1.4, 0.8], "rotation_deg": 90.0},
            "asset": {"method": "library", "bbox_m": [1.4, 0.8, 0.75]}}
    return {"project": {"id": "bay"}, "status": "ok", "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.6}],
            "walls": walls, "openings": openings,
            "rooms": [{"id": "r", "level_id": "L0", "label": "Oda", "room_type": "bedroom", "polygon": poly}],
            "furniture": [desk]}


def test_a_wall_inside_the_room_outline_hides_the_piece_behind_it():
    b = _bay_room()
    room = b["rooms"][0]
    camera = {"room_id": "r", "position": [3.5, 2.8, 1.25], "target": [2.5, 2.8, 1.25], "lens_mm": 18.0,
              "shift_x": 0.0, "shift_y": -0.1}
    shares = C.score_camera(b, camera)["shares"]
    assert shares["elements"].get("desk", 0.0) < MODEL_HIDDEN_SHARE          # old code: 0.080 of the frame
    assert shares["wall"] > 0.3
    (wall,) = C.inner_walls(room, b)
    assert wall["id"] == "w_bay" and wall["parts"] == [((1.1, 2.0), (1.1, 4.0))]
    # Without the bay wall the same camera sees the desk (the model is not blind there).
    open_bay = copy.deepcopy(b)
    open_bay["walls"] = [w for w in open_bay["walls"] if w["id"] != "w_bay"]
    assert C.score_camera(open_bay, camera)["shares"]["elements"].get("desk", 0.0) > 0.03


def test_a_wall_inside_the_room_outline_keeps_the_camera_points_away_and_carries_its_door():
    b = _bay_room(door=True)
    room = b["rooms"][0]
    # Fix round part 2 (17 Oct 2026): the desk alone keeps the grid off the bay wall, so the points are checked in the
    # room without it (the old code, and a search without the wall obstacle, gave (1.0, 2.5), (1.0, 3.0) and
    # (1.0, 3.5) in the wall band).
    empty = copy.deepcopy(b)
    empty["furniture"] = []
    points, warning = C.candidate_positions(empty["rooms"][0], empty)
    assert warning is None and len(points) > 20
    for p in points:
        assert geom_distance_to_band(p) >= C.OBSTACLE_CLEARANCE - 1e-9, p
    points, warning = C.candidate_positions(room, b)
    assert warning is None and points
    assert all(geom_distance_to_band(p) >= C.OBSTACLE_CLEARANCE - 1e-9 for p in points)
    model = C.RoomModel(room, b)
    dirs = np.array([[-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
    labels, depth = model.cast((3.5, 3.0, 1.0), dirs[:1])
    assert labels[0] == C.OPENING and depth[0] == pytest.approx(2.3)          # the door in the bay wall, x = 1.2
    labels, depth = model.cast((3.5, 2.3, 1.0), dirs[:1])
    assert labels[0] == C.WALL and depth[0] == pytest.approx(2.3)             # the wall face beside the door


def test_the_fallback_camera_point_is_never_inside_a_wall_standing_in_the_room():
    """Fix round part 2 (17 Oct 2026): a room with no free camera point (a low bed fills it) takes the fallback point,
    the room's inner point; a 1 m wall stub standing on that point is a tall obstacle of the fallback too, so the
    camera moves to the nearest point clear of it (the old code, and a fallback without the wall, put the camera at
    (1.0, 1.0), inside the stub)."""
    poly = [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]]
    walls = [{"id": "w_s", "level_id": "L0", "start": [-0.2, -0.1], "end": [2.2, -0.1], "thickness": 0.2},
             {"id": "w_e", "level_id": "L0", "start": [2.1, -0.2], "end": [2.1, 2.2], "thickness": 0.2},
             {"id": "w_n", "level_id": "L0", "start": [2.2, 2.1], "end": [-0.2, 2.1], "thickness": 0.2},
             {"id": "w_w", "level_id": "L0", "start": [-0.1, 2.2], "end": [-0.1, -0.2], "thickness": 0.2},
             {"id": "w_stub", "level_id": "L0", "start": [1.0, 0.5], "end": [1.0, 1.5], "thickness": 0.1}]
    bed = {"id": "bed", "type": "bed_double", "room_id": "r", "level_id": "L0", "front_deg": 0.0,
           "footprint": {"center": [1.0, 1.0], "size": [2.0, 2.0], "rotation_deg": 0.0},
           "asset": {"method": "library", "bbox_m": [2.0, 2.0, 0.5]}}
    b = {"project": {"id": "stub"}, "status": "ok", "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.6}],
         "walls": walls, "openings": [], "furniture": [bed],
         "rooms": [{"id": "r", "level_id": "L0", "label": "Oda", "room_type": "bedroom", "polygon": poly}]}
    room = b["rooms"][0]
    assert C.inner_wall_rects(room, b) == [{"center": [1.0, 1.0], "size": [1.0, 0.1], "rotation_deg": 90.0}]
    (p,), warning = C.candidate_positions(room, b)
    assert warning.startswith("no free camera point in the room") and "nearest point clear of tall proxies" in warning
    assert geom2d.distance_to_rect(p, (1.0, 1.0), (1.0, 0.1), 90.0) >= C.OBSTACLE_CLEARANCE - 1e-9, p


def geom_distance_to_band(p) -> float:
    return geom2d.distance_to_rect(p, (1.1, 3.0), (2.0, 0.2), 90.0)


# --------------------------------------------------------------------------
# 4. scripts/jobs/full.sh: RUN_FRESH_RECOGNITION (pod P5)
# --------------------------------------------------------------------------

FRESH_FAKE_PY = r'''#!__PYTHON__
"""Fake interpreter: the orchestrator's call records the files under WENART_OUTPUTS it sees."""
import json, os, sys
from pathlib import Path

argv = sys.argv[1:]
if argv[:1] in (["-c"], ["-"]):
    os.execv("__PYTHON__", ["__PYTHON__"] + argv)
if argv[:3] == ["-m", "wenart.run", "pod"]:
    out = Path(os.environ["WENART_OUTPUTS"])
    seen = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    with open(os.environ["FAKE_CALLS"], "a") as fh:
        fh.write(json.dumps({"pod": seen}) + "\n")
'''


def _fresh_box(tmp_path: Path):
    """The sandbox of tests/test_full_job.py (fake interpreter, setup and cgroup under tmp_path) with real04's stored
    answers on the "volume": two recognition answer files, one sheets answer file, the requests and a crop, and a
    committed seed in results/recognition/real04/."""
    import sys

    from test_full_job import Box, _exe

    box = Box(tmp_path)
    _exe(box.py, FRESH_FAKE_PY.replace("__PYTHON__", sys.executable))
    out = box.ws / "repo" / "outputs" / "real04"
    for rel, text in {"recognition/answers_qwen3-vl-8b.json": "q", "recognition/answers_glm-4.6v-flash.json": "g",
                      "recognition/requests.json": "r", "recognition/crops/sym_L0_001_ctx.png": "c",
                      "sheets/answers_qwen3-vl-8b.json": "sq", "sheets/requests.json": "sr"}.items():
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_text(text)
    seeds = box.ws / "repo" / "results" / "recognition" / "real04"
    seeds.mkdir(parents=True)
    (seeds / "answers_qwen3-vl-8b.json").write_text("seed")
    return box, out


def test_full_job_sets_the_stored_answers_aside_once_per_project_and_tag(tmp_path):
    """Fix round part 2 (17 Oct 2026, lead decision for pod P5): real04's stored L0 answers were given on the wrong
    crops. ``RUN_FRESH_RECOGNITION`` moves (never deletes) a project's recognition and sheets answer files to
    recognition/set_aside_<UTC stamp>/ before the orchestrator runs, so it asks those questions again; requests.json
    and the crops stay; a log line says so, an id that is no project is skipped, a committed seed is named. The
    resumed command keeps the answers asked since (once per id and tag, the ledger in the logs folder); a new tag
    sets them aside again. A project without outputs yet gets its ledger line and no folder (the orchestrator moves
    an out_dir without run/ to the archive). The old full.sh left every answer in place."""
    import re

    box, out = _fresh_box(tmp_path)
    rec = out / "recognition"
    ledger = box.logs / "fresh_recognition.log"
    (box.ws / "repo" / "projects" / "real02").mkdir(parents=True)
    proc = box.run(RUN_PROJECTS="real04", RUN_FRESH_RECOGNITION="real04, nosuch ../x real02",
                   RUN_VEGETATION_SETUP="0")
    assert proc.returncode == 0, box.output
    (aside,) = sorted(rec.glob("set_aside_*"))
    assert re.fullmatch(r"set_aside_\d{8}T\d{6}Z", aside.name)
    moved = sorted(p.relative_to(aside).as_posix() for p in aside.rglob("*") if p.is_file())
    assert moved == ["answers_glm-4.6v-flash.json", "answers_qwen3-vl-8b.json", "sheets/answers_qwen3-vl-8b.json"]
    assert (aside / "answers_qwen3-vl-8b.json").read_text() == "q"
    assert (aside / "sheets" / "answers_qwen3-vl-8b.json").read_text() == "sq"
    (pod,) = [c["pod"] for c in box.calls() if "pod" in c]
    assert not [p for p in pod if Path(p).name.startswith("answers_") and "/set_aside_" not in p], pod
    assert {"real04/recognition/requests.json", "real04/recognition/crops/sym_L0_001_ctx.png",
            "real04/sheets/requests.json"} <= set(pod)
    log = (box.logs / "full-test.log").read_text()
    assert (f"real04: 2 recognition and 1 sheets answer file(s) moved to recognition/{aside.name}/ "
            f"(RUN_FRESH_RECOGNITION 'fresh'): their questions are asked again") in log
    assert "no project 'nosuch'" in log and "'../x' is no project id[:tag]: skipped" in log
    assert "warning: real04: committed answers in results/recognition/real04/" in log
    assert log.index("their questions are asked again") < log.index("orchestrator exit 0")
    stamp = aside.name[len("set_aside_"):]
    first, second = ledger.read_text().splitlines()
    assert first.split() == ["real04", "fresh", stamp, f"recognition/{aside.name}", "2+1"]
    assert second.split()[:2] == ["real02", "fresh"] and second.split()[3:] == ["-", "0+0"]
    assert "real02: no stored answers to set aside" in log and not (box.ws / "repo" / "outputs" / "real02").exists()
    # The resumed command: the answers asked since stay where they are.
    (rec / "answers_qwen3-vl-8b.json").write_text("new")
    fresh02 = box.ws / "repo" / "outputs" / "real02" / "recognition" / "answers_qwen3-vl-8b.json"
    fresh02.parent.mkdir(parents=True)
    fresh02.write_text("new02")
    proc = box.run(RUN_PROJECTS="real04", RUN_FRESH_RECOGNITION="real04 real02", RUN_VEGETATION_SETUP="0")
    assert proc.returncode == 0, box.output
    assert (rec / "answers_qwen3-vl-8b.json").read_text() == "new" and len(list(rec.glob("set_aside_*"))) == 1
    assert fresh02.read_text() == "new02" and not list(fresh02.parent.glob("set_aside_*"))
    assert f"real04: the stored answers were set aside for 'fresh' before ({stamp} recognition/{aside.name} 2+1)" \
        in box.output
    assert len(ledger.read_text().splitlines()) == 2
    # A new tag sets them aside again, once; nothing is ever deleted.
    for _ in range(2):
        proc = box.run(RUN_PROJECTS="real04", RUN_FRESH_RECOGNITION="real04:p6", RUN_VEGETATION_SETUP="0")
        assert proc.returncode == 0, box.output
    asides = sorted(rec.glob("set_aside_*"))
    assert len(asides) == 2 and not (rec / "answers_qwen3-vl-8b.json").exists()
    assert sorted(p.read_text() for a in asides for p in a.rglob("answers_*.json")) == ["g", "new", "q", "sq"]
    assert [ln.split()[:2] for ln in ledger.read_text().splitlines()] == [["real04", "fresh"], ["real02", "fresh"],
                                                                          ["real04", "p6"]]


def test_full_job_stops_before_the_setup_when_the_answers_cannot_be_set_aside(tmp_path):
    """Fix round part 2: a failed move (here a ``mv`` that fails) stops the job before the setup and the orchestrator
    (exit 1): the run would use the stale answers. Nothing is moved and no set-aside is recorded."""
    box, out = _fresh_box(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "mv").write_text("#!/usr/bin/env bash\nexit 1\n")
    (bin_dir / "mv").chmod(0o755)
    proc = box.run(RUN_PROJECTS="real04", RUN_FRESH_RECOGNITION="real04", PATH=f"{bin_dir}:{box.env['PATH']}")
    assert proc.returncode == 1, box.output
    assert "the stored answers of 'real04' could not be set aside: stopping" in box.output
    assert not [c for c in box.calls() if "pod" in c] and not box.setup_log.exists()
    assert (out / "recognition" / "answers_qwen3-vl-8b.json").read_text() == "q"
    assert not (box.logs / "fresh_recognition.log").exists()


def test_full_job_header_documents_run_fresh_recognition():
    text = (Path(__file__).resolve().parents[1] / "scripts" / "jobs" / "full.sh").read_text(encoding="utf-8")
    header = text[:text.index("\nset -Eeuo pipefail\n")]
    entry = " ".join(header[header.index("#   RUN_FRESH_RECOGNITION"):].replace("#", " ").split())
    for words in ("MOVED, never deleted", "set_aside_<UTC stamp>", "Idempotent: done once per id",
                  "fresh_recognition.log", "\"<p>:<tag>\"",
                  "Committed seeds (results/recognition/<p>/) are not touched"):
        assert words in entry, words
