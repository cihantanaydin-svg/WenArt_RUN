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
How: synthetic DXF pages (wenart.synthetic), the hand-made rooms of tests/_m11_room.py, a hand-made L room.
"""
import copy
import dataclasses
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import _m11_room as M
from wenart import geometry as G
from wenart.blender import camsearch as C
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
    house, the bathroom door 0.15 m along its wall, the wardrobe 0.12 m along, one nightstand at another place in
    the bedroom and the sofa the master lacks."""
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
    assert [f["type"] for f in extra] == ["sofa"]                 # the piece the master lacks is still added
    assert "1 extra from DXF added as unverified" in furniture["resolution"]
    assert "2 extra from DXF not added" in furniture["resolution"]
    reasons = {e["reason"].split(" ")[0]: e for e in furniture["not_added"]}
    assert "overlaps the master's wardrobe" in reasons["it"]["reason"] and "drawn again" in reasons["it"]["reason"]
    assert "drawn elsewhere" in reasons["the"]["reason"] and "nightstand" in reasons["the"]["reason"]
    assert len([f for f in building["furniture"] if f["type"] == "wardrobe"]) == 1
    assert len([f for f in building["furniture"] if f["type"] == "nightstand"]) == 2


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
    points, warning = C.candidate_positions(room, b)
    assert warning is None and points
    for p in points:
        assert geom_distance_to_band(p) >= C.OBSTACLE_CLEARANCE - 1e-9, p     # old code: (1.0, 2.5) ... in the band
    model = C.RoomModel(room, b)
    dirs = np.array([[-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
    labels, depth = model.cast((3.5, 3.0, 1.0), dirs[:1])
    assert labels[0] == C.OPENING and depth[0] == pytest.approx(2.3)          # the door in the bay wall, x = 1.2
    labels, depth = model.cast((3.5, 2.3, 1.0), dirs[:1])
    assert labels[0] == C.WALL and depth[0] == pytest.approx(2.3)             # the wall face beside the door


def geom_distance_to_band(p) -> float:
    from wenart.blender import geom2d

    return geom2d.distance_to_rect(p, (1.1, 3.0), (2.0, 0.2), 90.0)
