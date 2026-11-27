"""Audit fix round 2 (26 Nov 2026): the general reading rules R27, R03, R01 and R05 found in the re-rendered real17,
real06, real10 and real15 (CPU; synthetic cases and, where the drawings are here, a fresh reading of the project)."""
import copy
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"


def _wall(wid, a, b, t=0.2, lid="L0", **kw):
    return dict({"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t, "evidence": []}, **kw)


@pytest.fixture(scope="module")
def real06(tmp_path_factory):
    """A fresh CPU reading of real06 (no AI), shared by the rules' regression checks."""
    if not (PROJECTS / "real06").is_dir():
        pytest.skip("the real06 drawings are not here")
    from wenart.ingest import pipeline as PL

    out = tmp_path_factory.mktemp("real06")
    return PL.run_project(PROJECTS / "real06", out, no_ai=True)[0]


def _near(building, kind, level, x, y, tol=0.4):
    import math
    return [o for o in building.get("openings") or [] if o.get("level_id") == level and o.get("type") == kind
            and o.get("center") and math.dist(o["center"][:2], (x, y)) <= tol]


# ------------------------------------------------------------------------------------- R27 twin merge ranking
def _twin(door_ev, operation="sliding", door_w=1.95):
    """real06's kitchen wall: the kept wall w_9 (0.30 m) carries a 2.90 m unclassified gap, its copy w_10 (0.25 m,
    2.5 cm off) the door read from the drawn leaves."""
    return {"walls": [_wall("w_9", (0.45, 9.2), (4.6, 9.2), 0.3), _wall("w_10", (0.95, 9.225), (3.85, 9.225), 0.25)],
            "openings": [{"id": "o_1", "type": "opening", "level_id": "L0", "wall_id": "w_9", "center": [2.4, 9.2],
                          "width": 2.9, "evidence": [{"method": "derived", "note": "unclassified gap content: ..."}]},
                         {"id": "d_2", "type": "door", "level_id": "L0", "wall_id": "w_10", "center": [2.275, 9.225],
                          "width": door_w, "operation": operation, "evidence": door_ev}]}


def test_r27_sliding_leaves_on_a_door_layer_outrank_the_gap_read_over_them():
    from wenart.ingest.generic import twin_walls as TW

    b = _twin([{"method": "vector", "layer": "KAPI", "door_layer": True,
                "note": "6 leaf/leaves drawn parallel to the wall without a swing arc: a sliding door"}])
    TW.merge_twin_walls(b)
    (door,) = b["openings"]
    assert door["id"] == "d_2" and door["wall_id"] == "w_9"
    assert door["center"] == pytest.approx([2.275, 9.2]) and door["width"] == pytest.approx(1.95)   # its own width
    (gap,) = b["openings_merged"]
    assert gap["id"] == "o_1" and gap["merged_into"] == "d_2" and "door layer 'KAPI'" in gap["corrected_by_ai"]["reason"]
    assert [w["id"] for w in b["walls"]] == ["w_9"]                    # the piers stay wall: the kept wall is whole


def test_r27_a_door_block_and_a_size_tag_type_the_door_too():
    from wenart.ingest.generic import twin_walls as TW

    named = _twin([{"method": "vector", "note": "door by its block name 'SURGU KAPI' (sliding, no swing arc)"}])
    TW.merge_twin_walls(named)
    assert [o["id"] for o in named["openings"]] == ["d_2"]
    tagged = _twin([{"method": "vector", "rule": "size_tag", "reason": "the door size tag '200/210'"}], None, 2.0)
    TW.merge_twin_walls(tagged)
    assert [o["id"] for o in tagged["openings"]] == ["d_2"]


def test_r27_untyped_leaf_lines_and_inferred_doors_still_lose_to_the_gap():
    """Leaf lines on no door layer (a frame's or a counter's lines read so), or a door with inferred evidence, are no
    typed door: the gap stays and the door is merged into it (the 29 Oct rule for them stands)."""
    from wenart.ingest.generic import twin_walls as TW

    for ev in ([{"method": "vector", "layer": "MOBILYA", "door_layer": False, "note": "6 leaf/leaves drawn ..."}],
               [{"method": "vector", "door_layer": True}, {"method": "inferred", "note": "placed by the architect"}],
               []):
        b = _twin(ev)
        TW.merge_twin_walls(b)
        assert [o["id"] for o in b["openings"]] == ["o_1"], ev
        assert b["openings_merged"][0]["id"] == "d_2"
    assert TW.typed_door({"type": "door", "operation": "swing", "evidence": [{"method": "vector"}]}) == "its drawn swing"
    assert TW.typed_door({"type": "door", "operation": "sliding", "evidence": [{"method": "derived",
                                                                                 "door_layer": True}]}) is None


def test_r27_the_sliding_door_record_holds_on_real06(real06):
    """C0100 (the user, 26 Nov 2026: "sliding door"): a 2.0 m door at (2.275, 9.2) on L0 and no 2.9 m opening; C0065
    (same place): one wall, the copy not built, its opening the kept wall's opening read twice."""
    doors = _near(real06, "door", "L0", 2.275, 9.2)
    assert len(doors) == 1 and doors[0]["operation"] == "sliding" and 1.9 <= doors[0]["width"] <= 2.05
    assert not _near(real06, "opening", "L0", 2.4, 9.2, 0.6)
    walls = [w["id"] for w in real06["walls"] if w.get("level_id") == "L0"]
    assert doors[0]["wall_id"] in walls
    merged = {w["id"]: w.get("merged_into") for w in real06.get("walls_merged") or []}
    assert merged.get("w_L0_010") == doors[0]["wall_id"]


# ------------------------------------------------------------------------------------------ R03 gap stroke roles
def _gap_run(walls, strokes, **kw):
    from wenart.ingest.generic import openings as O

    return O.gaps_and_openings(walls, strokes, "test.dxf", None, **kw)


def _pair_walls(gap_a, gap_b, t=0.1):
    import _real01_page as R

    return [R.wall((0, 0), (gap_a, 0), t), R.wall((gap_b, 0), (5, 0), t)]


def _line(a, b, layer=None, linetype=None, block=None):
    import _real01_page as R

    st = R.stroke([a, b], block=block)
    st.layer, st.linetype = layer, linetype
    return st


def test_r03_dotted_lintel_lines_make_no_window_solid_window_lines_do():
    """real06 L0/L1: a 1.0 m gap whose only content is two lines on the overhead layer IZDOT (drawn DOT3: the head of a
    passage, above the cut) was a window; the same lines on PENCERE are one, dashed too (a high window above the cut);
    dotted lines on a layer that says nothing stay window lines (real10 draws its corner windows' glass so)."""
    walls = _pair_walls(2.0, 3.0)
    for layer, lt, kind in (("IZDOT", "DOT3", "opening"), ("PENCERE", None, "window"), ("PENCERE", "DASHED", "window"),
                            ("0", "ACAD_ISO07W100", "window"), ("IZDOT", None, "opening"), ("A-BEAM", None, "opening"),
                            ("KİRİŞ", None, "opening")):
        lines = [_line((2.0, -0.03), (3.0, -0.03), layer, lt), _line((2.0, 0.02), (3.0, 0.02), layer, lt)]
        _w, openings, log, _o = _gap_run(walls, lines)
        assert [o.kind for o in openings] == [kind], (layer, lt)
        if kind == "opening":
            assert [e["class"] for e in log if e["kind"] == "run"] == ["empty"]       # a passage, not unclassified


def test_r03_fixture_arcs_are_no_swings_and_a_swing_is_a_leaf():
    """real15: the kitchen sink block 'EVYE 5' (bowl and tap arcs of 0.08-0.10 m, hinges 0.18 m apart) made a 0.60 m
    double door into the bathroom (``_framed_double``). Neither the block's arcs nor such small arcs anywhere are a
    door's swing; a door block's arcs and a real leaf's swing stay doors."""
    import _real01_page as R
    from wenart.ingest.generic import openings as O

    walls = _pair_walls(2.0, 2.6, 0.3)
    for block in ("EVYE 5", None):
        arcs = [R.arc((2.2, 0.2), 0.09, 0, 90), R.arc((2.38, 0.2), 0.09, 90, 180)]
        for a in arcs:
            a.block, a.layer = block, "Z_tefriş"
        _w, openings, _l, _o = _gap_run(walls, arcs)
        assert not [o for o in openings if o.kind == "door"], block
    assert O.fixture_block(R.stroke([(0, 0), (1, 0)], block="DAIRE/LAVABO2")) == "LAVABO2"
    assert O.fixture_block(R.stroke([(0, 0), (1, 0)], block="KAPI_90/EVYE")) is None      # a door block's own
    assert O.fixture_block(R.stroke([(0, 0), (1, 0)], block="*U12")) is None              # real03's anonymous door
    assert not O.swing_arc_ok(R.stroke([(0, 0), (1, 0)], block="KLO"))
    # a real 0.9 m swing in a block on the furniture layer stays a door (real03's TEFRIS doors)
    walls = _pair_walls(2.0, 2.9)
    swing = R.arc((2.0, 0.05), 0.88, 0, 90)
    swing.block, swing.layer = "*U7", "SAA_TEFRİS"
    _w, openings, _l, _o = _gap_run(walls, [swing])
    assert [o.kind for o in openings] == ["door"]


def test_r03_framed_double_needs_leaves_of_half_the_gap_less_a_frame():
    """real10's entrance (two 0.93 m leaves hinged 0.27 m in from the jambs of a 2.40 m gap) stays a double door; two
    0.40 m arcs hinged 0.80 m apart in the same gap are no door (each leaf at least half the gap less a frame)."""
    import _real01_page as R

    walls = [R.wall((-2, 0), (0, 0), 0.2), R.wall((2.4, 0), (5, 0), 0.2)]
    ok = [R.arc((0.27, 0.1), 0.93, 0, 90), R.arc((2.13, 0.1), 0.93, 90, 180)]
    _w, openings, _l, _o = _gap_run(walls, ok)
    assert [(o.kind, round(o.width, 2)) for o in openings] == [("door", 2.4)]
    small = [R.arc((0.27, 0.1), 0.40, 0, 90), R.arc((1.07, 0.1), 0.40, 90, 180)]
    _w, openings, _l, _o = _gap_run(walls, small)
    assert not [o for o in openings if o.kind == "door"]


def test_r03_wall_layer_lines_never_form_an_open_leaf():
    """real06 L1: the sides of two shaft boxes on the wall layer DUVAR, standing across the wall at a 0.5 m gap, made
    a door drawn open at 90 degrees onto the stair void; the same lines on the door layer are a leaf."""
    walls = _pair_walls(2.0, 2.5, 0.15)
    for layer, door in (("DUVAR", False), ("KOLON", False), ("KAPI", True)):
        leaf = [_line((2.02, 0.075), (2.02, 0.575), layer), _line((2.05, 0.075), (2.05, 0.575), layer)]
        _w, openings, _l, _o = _gap_run(walls, leaf)
        assert bool([o for o in openings if o.kind == "door"]) is door, layer
    # a door wide enough to be one keeps a leaf drawn on the wall layer (real18's 0.80 m door)
    walls = _pair_walls(2.0, 2.8, 0.15)
    leaf = [_line((2.02, 0.075), (2.02, 0.875), "DUVAR"), _line((2.05, 0.075), (2.05, 0.875), "DUVAR")]
    _w, openings, _l, _o = _gap_run(walls, leaf)
    assert [o.kind for o in openings] == ["door"]


def test_r03_a_column_covering_most_of_a_gap_closes_it():
    """real17 L1-L3: a 0.3 m column covers 0.634 m of a 0.648 m gap in the kitchen partition (a cross wall's face the
    last 1.4 cm): wall material, no opening. A piece leaving a passable part (>= GAP_MIN_M) open does not close it."""
    import _real01_page as R

    walls = _pair_walls(2.0, 2.648) + [R.wall((2.0, 0.1), (2.634, 0.1), 0.3, entity="column")]
    _w, openings, log, _o = _gap_run(walls, [])
    assert openings == [] and [e.get("rule") for e in log if e["kind"] == "run"] == ["inside_wall"]
    walls = [R.wall((0, 0), (2.0, 0), 0.1), R.wall((3.3, 0), (5, 0), 0.1), R.wall((2.0, 0.1), (3.0, 0.1), 0.3)]
    _w, openings, _l, _o = _gap_run(walls, [])
    assert [o.kind for o in openings] == ["opening"]          # 1.0 of 1.3 m covered, 0.30 m left: a way through
    # a square column read on the other axis covers the gap too
    walls = _pair_walls(2.0, 2.3) + [R.wall((2.15, -0.15), (2.15, 0.15), 0.3, entity="column")]
    _w, openings, _l, _o = _gap_run(walls, [])
    assert openings == []


def test_r03_another_doors_arc_and_tag_cast_no_door_vote():
    """real17: the ranker typed the covered gap a door on the bathroom door's swing arc and its '80/210' tag."""
    from types import SimpleNamespace

    import _real01_page as R
    from wenart.ingest.generic import decisions as DEC
    from wenart.ingest.generic import openings as O

    swing = R.arc((2.25, 0.05), 0.78, 90, 180)        # the next door's swing, hinged at the shared jamb
    index = O.StrokeIndex([swing], 0.0)
    door = O.Gap("run", "h", 0.0, 0.1, 2.2, 3.0, [], cls="door")
    door.found = {"arcs": [index.items[0]]}
    gap = O.Gap("run", "h", 0.0, 0.1, 1.55, 2.2, [], cls="unclassified")
    gap.decision = {"features": {"arcs_swing": 0, "arcs_door_like": 1, "tag_door_like": True, "tag_distance": 0.72}}
    tag = DEC._Text(at=(2.6, 0.4), text="80/210", height=0.1, size_tag=(0.8, 2.1), outdoor=False, label=None)
    log = SimpleNamespace(texts_aligned=lambda: [tag])
    notes = O.unbind_votes([door, gap], index, log)
    f = gap.decision["features"]
    assert len(notes) == 1 and f["arcs_door_like"] == 0 and not f["tag_door_like"]
    assert "belong to another door" in gap.decision["votes_bound"] and "'80/210'" in gap.decision["votes_bound"]


def test_r03_a_door_never_cuts_a_column():
    from wenart.blender import shell

    def w(wid, a, b, t, layer=None):
        return {"id": wid, "start": list(a), "end": list(b), "thickness": t,
                "evidence": [{"file": "x", "method": "vector", "confidence": 1, "layer": layer}]}
    host = w("w_p", (11.72, 8.57), (11.72, 22.0), 0.1)
    assert shell.column_piece(w("c", (11.82, 9.36), (11.82, 9.99), 0.3), host)          # short and thicker
    assert shell.column_piece(w("c", (0, 0), (0.6, 0), 0.1, "KOLON"), host)              # a structure layer's piece
    assert not shell.column_piece(w("c", (0, 0), (3.0, 0), 0.3, "KOLON"), host)          # a shear wall: long
    assert not shell.column_piece(w("c", (0, 0), (0.6, 0), 0.1), host)                   # a short copy of the wall
    door = {"id": "o_3", "type": "door", "wall_id": "w_p", "center": [11.72, 9.68], "width": 0.65, "height": 2.1}
    column = w("w_c", (11.82, 9.36), (11.82, 9.99), 0.3)
    assert shell.foreign_cuts(column, {"w_p": host, "w_c": column}, [door]) == []


def _two_storeys(l0_marks, l1_marks=(), source="section"):
    """tests/_levels_fixture's house split into three L0 rooms (living, bedroom, hall) and copied as L1 at 3.00 m."""
    from tests import _levels_fixture as F

    b = F.building()
    b["levels"][0]["elevation_source"] = source
    b["walls"].append(F._wall("w_6", (3, 0), (3, 8), exterior=False))
    b["rooms"] = [F._room("r_living", [(0.1, 0.1), (2.9, 0.1), (2.9, 7.9), (0.1, 7.9)], "living", label="Salon"),
                  F._room("r_bed", [(3.1, 0.1), (5.9, 0.1), (5.9, 7.9), (3.1, 7.9)], "bedroom", label="Yatak"),
                  F._room("r_hall", [(6.1, 0.1), (9.9, 0.1), (9.9, 7.9), (6.1, 7.9)], "hall", label="Hol")]
    up = copy.deepcopy(b)
    b["levels"].append(dict(b["levels"][0], id="L1", order=1, elevation=3.0, label="1. Kat", elevation_source="section"))
    for key in ("walls", "rooms", "openings"):
        for x in up[key]:
            b[key].append(dict(x, id=x["id"] + "_up", level_id="L1",
                               **({"wall_id": x["wall_id"] + "_up"} if key == "openings" else {})))
    b["slabs"] = [{"id": "sl_L0", "z_top": 0.0, "thickness": 0.2, "thickness_source": "assumed_default",
                   "outline": [[-0.1, -0.1], [10.1, -0.1], [10.1, 8.1], [-0.1, 8.1]], "evidence": [dict(F.EV)]}]
    centre = {"r_living": (1.5, 4.0), "r_bed": (4.5, 4.0), "r_hall": (8.0, 6.0)}
    marks = [F.mark(f"lm_{i}", v, kind="floor", point=centre[r], room_id=r) for i, (r, v) in enumerate(l0_marks)]
    marks += [F.mark(f"lm_u{i}", v, kind="floor", point=centre[r], room_id=r + "_up", level="L1")
              for i, (r, v) in enumerate(l1_marks)]
    b["level_marks"] = marks
    return b


def _offsets(b):
    return {r["id"]: r["floor_offset_m"] for r in b["rooms"]}


def test_r01_one_height_frame_from_the_ground_floor_marks():
    """real15: the section set L0 at 0, its rooms read '+0.50' (one '+0.35'), L1's '+3.50': one frame (+0.50) for
    every mark, every room at its storey's floor but the hall (-0.15), no inner steps but the hall's."""
    from wenart.levels import model as M

    b = M.infer_levels(_two_storeys([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.35)],
                                    [("r_living", 3.5), ("r_bed", 3.5), ("r_hall", 3.5)]))
    off = _offsets(b)
    assert off == {"r_living": 0.0, "r_bed": 0.0, "r_hall": -0.15, "r_living_up": 0.0, "r_bed_up": 0.0,
                   "r_hall_up": 0.0}
    assert b["level_inference"]["frame"]["value"] == 0.5
    assert all(m["frame_shift"] == 0.5 for m in b["level_marks"])
    assert [s["opening_id"] for s in b["level_inference"]["inner_steps"]] == ["d_inner"]   # hall to bedroom only
    g = b["site"]["ground"]                     # nothing about the ground drawn: the plans' ±0.00 under the '+0.50'
    assert g["source"] == "frame" and g["levels"][0]["z"]["value"] == -0.5
    from wenart import building as B
    assert not [e for e in B.validation_errors(b) if "ground" in e]          # a schema value (method derived)
    again = M.infer_levels(b)                   # a second run reads the frame again, never as a drawn section line
    assert again["site"]["ground"]["source"] == "frame" and not again["level_inference"].get("ground_gate")
    # an assumed ground floor moves to its marks instead (the old rule): no frame
    b = M.infer_levels(_two_storeys([("r_living", 0.5), ("r_bed", 0.5)], source=None))
    assert not b["level_inference"].get("frame") and b["levels"][0]["elevation"] == 0.5


def test_r01_a_shared_offset_of_a_storey_is_its_frame_never_a_step_per_room():
    from wenart.levels import model as M

    b = M.infer_levels(_two_storeys([], [("r_living", 3.5), ("r_bed", 3.5), ("r_hall", 3.35)]))
    off = _offsets(b)
    assert (off["r_living_up"], off["r_bed_up"], off["r_hall_up"]) == (0.0, 0.0, -0.15)
    assert b["level_inference"]["level_frames"]["L1"]["value"] == 0.5


def test_r01_disagreeing_marks_are_never_averaged_and_a_shaft_head_is_not_the_room_floor():
    """real10 L7: '+23.50' by the lift machine room's door, '+24.70' over the lift shaft below: the room is at the level
    floor, no step at its door; two marks of which neither is the level's or a neighbour's floor keep the level floor."""
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = _two_storeys([], [("r_hall", 3.0)])
    b["rooms"].append(F._room("r_shaft", [(8.4, 5.0), (9.5, 5.0), (9.5, 7.5), (8.4, 7.5)], "shaft", label="Asansör"))
    b["level_marks"].append(F.mark("lm_head", 4.2, kind="floor", point=(8.7, 6.2), room_id="r_hall_up", level="L1"))
    n = M.infer_levels(b)
    assert _offsets(n)["r_hall_up"] == 0.0
    c = next(x for x in n["conflicts"] + n["level_inference"]["conflicts"] if x["kind"] == "level_mark_mismatch")
    assert "never averaged" in c["resolution"] and "shaft" in c["resolution"]
    assert not [s for s in n["level_inference"]["inner_steps"] if s["opening_id"] == "d_inner_up"]
    b = _two_storeys([], [("r_hall", 3.6), ("r_hall", 4.1)])
    n = M.infer_levels(b)
    assert _offsets(n)["r_hall_up"] == 0.0 and any("the level floor is kept" in w
                                                   for w in n["level_inference"]["warnings"])


def test_r01_a_mark_in_a_terrace_is_its_floor_never_the_ground():
    """real15: '+0.50' written inside the TERAS outlines were ground marks; a mark beside a terrace's outline stays the
    ground's (a sloping site's garden), a mark by the label of a space without an outline is that space's."""
    from tests import _levels_fixture as F
    from wenart.levels import model as M
    from wenart.levels import read as RD

    b = F.building()
    b["site"] = {"areas": [
        {"id": "sa_L0_teras", "level_id": "L0", "label": "TERAS", "anchor": [3.0, -1.5], "polygon": None,
         "outline_inferred": {"polygon": [[0.0, -0.1], [6.0, -0.1], [6.0, -3.0], [0.0, -3.0]]}},
        {"id": "sa_L0_balkon", "level_id": "L0", "label": "BALKON", "anchor": [12.0, 4.0], "polygon": None},
        {"id": "sa_L0_bahce", "level_id": "L0", "label": "BAHÇE", "anchor": [-2.0, 4.0],
         "polygon": [[-5.0, 0.0], [-0.2, 0.0], [-0.2, 8.0], [-5.0, 8.0]]},
        {"id": "sa_L0_sacak", "level_id": "L0", "label": "GİRİŞ SAÇAĞI", "anchor": [8.0, 9.5], "polygon": None}]}
    marks = [F.mark("lm_t", 0.5, point=(2.0, -1.0)), F.mark("lm_g", 0.0, point=(7.0, -2.0)),
             F.mark("lm_b", 0.5, point=(12.3, 4.2)), F.mark("lm_garden", -0.3, point=(-2.0, 2.0)),
             F.mark("lm_canopy", 0.0, point=(8.2, 9.6))]
    for m in marks:
        m["kind"] = None
    RD.classify(marks, b, M.level_params())
    kinds = {m["id"]: m["kind"] for m in marks}
    # (real13: the '+2.50' under the entrance canopy is the ground there, not a raised space's floor)
    assert kinds == {"lm_t": "floor", "lm_g": "ground_finished", "lm_b": "floor", "lm_garden": "ground_finished",
                     "lm_canopy": "ground_finished"}
    assert marks[0]["outdoor_area"]["label"] == "TERAS" and marks[0].get("room_id") is None


def test_r01_the_ground_never_stands_over_the_floor_its_entrances_and_garage():
    """real15: three terrace marks made the ground 0.5 m over the floor; such ground marks are refused: the ground
    then comes from the plans' ±0.00 (a frame applied) or the default."""
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = F.building()
    b["level_marks"] = [F.mark(f"lm_{i}", 0.5, kind="ground_finished", point=p)
                        for i, p in enumerate([(-1.0, 2.0), (5.0, -1.0), (11.0, 5.0)])]
    n = M.infer_levels(b)
    g = n["site"]["ground"]
    assert g["source"] == "D3a" and not any(p["used"] for p in g["points"])
    assert n["level_inference"]["ground_gate"]["refused"] == ["lm_0", "lm_1", "lm_2"]
    assert all(e["ground_z"] <= e["threshold_z"] for e in n["site"]["entrances"])
    # a sloping site keeps its marks: one of them under the floor
    b["level_marks"][0]["z"] = b["level_marks"][0]["value"] = -0.6
    n = M.infer_levels(b)
    assert n["site"]["ground"]["source"] == "marks" and not n["level_inference"].get("ground_gate")
    # with the plans' frame (+0.50) the ground falls to the printed ±0.00
    b = _two_storeys([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.5)], [("r_hall", 3.5)])
    b["level_marks"] += [F.mark(f"lm_g{i}", 0.6, kind="ground_finished", point=p)
                         for i, p in enumerate([(-1.0, 2.0), (5.0, -1.0), (11.0, 5.0)])]
    n = M.infer_levels(b)
    assert n["site"]["ground"]["source"] == "frame" and n["site"]["ground"]["levels"][0]["z"]["value"] == -0.5


def test_r03_real06_passages_are_no_windows_and_no_door_opens_onto_the_void(real06):
    """real06: win_L1_001 (dressing room) and win_L0_001 (hall to living room), read from dotted IZDOT lines, are no
    windows; d_L1_009, read from two DUVAR lines of the shaft boxes, is no door."""
    assert not _near(real06, "window", "L1", 7.125, 6.675) and _near(real06, "opening", "L1", 7.125, 6.675)
    assert not _near(real06, "window", "L0", 5.625, 9.275)
    assert not _near(real06, "door", "L1", 5.87, 14.05, 0.3)


# ------------------------------------------------------------------------------------------------ R05 door validity
def _flats():
    """Two mirrored flats (axis x = 10): each a kitchen/salon wall; the left flat's kitchen door at the wall's end, the
    right flat's door read 0.58 m past the end of a cross wall, in the salon (real10's d_L0_028)."""
    walls = [_wall("w_out_s", (0, 0), (20, 0), 0.2), _wall("w_out_n", (0, 8), (20, 8), 0.2),
             _wall("w_out_w", (0, 0), (0, 8), 0.2), _wall("w_out_e", (20, 0), (20, 8), 0.2),
             _wall("w_mid", (10, 0), (10, 8), 0.2),
             _wall("w_k_l", (5.0, 0), (5.0, 6.4), 0.16), _wall("w_k_r", (15.0, 0), (15.0, 6.4), 0.16),
             _wall("w_x_r", (13.3, 6.48), (14.95, 6.48), 0.18), _wall("w_x_l", (5.05, 6.48), (6.7, 6.48), 0.18)]
    rooms = [{"id": "r_k_l", "level_id": "L0", "polygon": [[0.1, 0.1], [4.9, 0.1], [4.9, 7.9], [0.1, 7.9]]},
             {"id": "r_s_l", "level_id": "L0", "polygon": [[5.1, 0.1], [9.9, 0.1], [9.9, 7.9], [5.1, 7.9]]},
             {"id": "r_s_r", "level_id": "L0", "polygon": [[10.1, 0.1], [14.9, 0.1], [14.9, 7.9], [10.1, 7.9]]},
             {"id": "r_k_r", "level_id": "L0", "polygon": [[15.1, 0.1], [19.9, 0.1], [19.9, 7.9], [15.1, 7.9]]}]
    ops = [{"id": "d_l", "type": "door", "level_id": "L0", "wall_id": "w_k_l", "center": [5.0, 6.0], "width": 0.8},
           {"id": "d_r", "type": "door", "level_id": "L0", "wall_id": "w_x_r", "center": [15.53, 6.48], "width": 1.1}]
    return {"levels": [{"id": "L0", "order": 0, "elevation": 0.0}], "walls": walls, "rooms": rooms, "openings": ops}


def _mirror(walls):
    from wenart.ingest.generic import facade as FC

    return FC.mirror_axis(walls, FC.MIRROR_SHARE)


def test_r05_a_door_past_its_walls_end_takes_its_twins_place_or_is_not_built():
    """27 Nov 2026 (audit O3): a mirror twin is a door of the same width on a parallel wall that holds the whole door, at
    the plan's strict mirror axis (``MIRROR_FIX_SHARE``); real10's 1.10 m door no longer takes the place of a 0.80 m door
    on a perpendicular wall (tests/test_audit_round2b_20261127.py has the full rule)."""
    from wenart.ingest import door_validity as DV
    from wenart.ingest.generic import facade as FC

    def strict(walls):
        return FC.mirror_axis(walls, FC.MIRROR_FIX_SHARE)

    b = _flats()
    assert DV.check(copy.deepcopy(b))["not_built"] == ["d_r"]          # without the plan's mirror axis: no twin
    out = DV.check(b, mirror_axis=strict)                               # the 0.80 m door on a perpendicular wall: none
    assert out["not_built"] == ["d_r"] and not out["reseated"]
    b = _flats()
    b["openings"][0] = {"id": "d_l", "type": "door", "level_id": "L0", "wall_id": "w_x_l", "center": [5.6, 6.48],
                        "width": 1.1}
    b["openings"][1]["center"] = [15.2, 6.48]
    out = DV.check(b, mirror_axis=strict)
    d = next(o for o in b["openings"] if o["id"] == "d_r")
    assert out["reseated"] == ["d_r"] and d["wall_id"] == "w_x_r" and d["center"] == pytest.approx([14.4, 6.48])
    assert d["drawn_center"] == [15.2, 6.48] and d["corrected_by_ai"]["rule"] == DV.RULE
    b = _flats()
    b["openings"] = [o for o in b["openings"] if o["id"] != "d_l"]           # no twin: never a frame in free space
    out = DV.check(b, mirror_axis=strict)
    assert out["not_built"] == ["d_r"] and not b["openings"] and b["openings_not_built"][0]["id"] == "d_r"
    assert b["needs_review"][0]["kind"] == "door_outside_wall"
    # a door read from its own swing drawn there keeps its place (synthetic-16: between a stub's end and the next wall)
    b = _flats()
    b["openings"][1]["evidence"] = [{"file": "p.dxf", "method": "vector", "confidence": 0.95, "entity": "ARC:AB,LINE:AA"}]
    out = DV.check(b, mirror_axis=strict)
    assert not out["reseated"] and not out["not_built"] and b["openings"][1]["center"] == [15.53, 6.48]


def test_r05_a_door_with_one_room_on_both_sides_and_a_wall_glued_to_its_face_are_found():
    """real17 d_L1_018 (a 5 cm slit joined the landing to the flat's hall); real10 d_L0_003 (a 7 cm wall 4 cm behind
    the escape stair's 1.40 m door): both listed; the build cuts the door through the glued wall (foreign_cuts)."""
    from wenart.blender import shell
    from wenart.ingest import door_validity as DV

    b = _flats()
    b["rooms"][1]["polygon"] = [[0.1, 0.1], [9.9, 0.1], [9.9, 7.9], [0.1, 7.9]]      # the slit: one face both sides
    b["rooms"].pop(0)
    out = DV.check(b)
    assert out["same_room"] == ["d_l"] and any(r["kind"] == "door_same_room" for r in b["needs_review"])
    host = _wall("w_h", (9.78, 6.29), (12.6, 6.29), 0.30)
    glued = _wall("w_g", (9.78, 6.065), (12.6, 6.065), 0.07)
    door = {"id": "d_3", "type": "door", "level_id": "L0", "wall_id": "w_h", "center": [11.19, 6.29], "width": 1.4}
    b = {"walls": [host, glued], "rooms": [], "openings": [door]}
    assert DV.check(b)["blocked"] == [["d_3", "w_g"]]
    (o, _c, depth), = shell.foreign_cuts(glued, {"w_h": host, "w_g": glued}, [door])
    assert o["id"] == "d_3" and depth == pytest.approx(0.30 / 2 + 0.225 + 0.035)
    win = dict(door, id="win_3", type="window")                     # a window is not cut through a wall behind it
    assert shell.foreign_cuts(glued, {"w_h": host, "w_g": glued}, [win]) == []


def test_r05_a_door_onto_a_floor_void_is_not_built():
    """real06 d_L1_009: its stair-side face over the stair void of the floor under L1."""
    from wenart.ingest import door_validity as DV

    b = {"walls": [_wall("w_1", (5.87, 13.0), (5.87, 15.0), 0.15, lid="L1")], "rooms": [],
         "openings": [{"id": "d_9", "type": "door", "level_id": "L1", "wall_id": "w_1", "center": [5.87, 14.05],
                       "width": 0.5},
                      {"id": "d_10", "type": "door", "level_id": "L1", "wall_id": "w_1", "center": [5.87, 13.3],
                       "width": 0.8}]}
    slabs = {"by_level": {"L1": {"under": {"voids": [[[4.0, 13.7], [5.78, 13.7], [5.78, 15.5], [4.0, 15.5]]]}}}}
    notes = DV.voids_check(b, slabs)
    assert [o["id"] for o in b["openings"]] == ["d_10"] and len(notes) == 1 and "d_9" in notes[0]
    assert b["needs_review"][0]["kind"] == "door_over_void"


RUNS = Path(os.environ.get("WENART_RUNS") or ROOT / "runs")       # the runs' collected results (not in git)
REAL10_RUN = RUNS / "20261126-114512-full" / "results" / "furniture" / "real10" / "building.json"
REAL17_RUN = RUNS / "20261126-110510-full" / "results" / "furniture" / "real17" / "building.json"


@pytest.mark.skipif(not (REAL10_RUN.is_file() and REAL17_RUN.is_file()), reason="the runs of 26 Nov are not stored here")
def test_r05_the_stored_readings_doors():
    """The run's readings: real10's escape stair door is found blocked by the glued wall; real17's flat door through
    the slit is found; afterwards every door stands in its wall. 27 Nov 2026 (audit O2/O3/G1): real10's salon door
    d_L0..L6_028 is never moved into the kitchen/salon wall (its twin d_L0_026 is a 0.80 m door on a perpendicular wall);
    this older reading lost its drawn swing's evidence, so it is listed, not built (a fresh reading keeps it at its
    drawn place: tests/test_audit_round2b_20261127.py)."""
    import json

    from wenart.ingest import door_validity as DV
    from wenart.ingest.generic import facade as FC

    b = json.loads(REAL10_RUN.read_text(encoding="utf-8"))
    out = DV.check(b, mirror_axis=lambda ws: FC.mirror_axis(ws, FC.MIRROR_FIX_SHARE))
    assert not any(o.endswith("_028") for o in out["reseated"])
    assert {o for o in out["not_built"] if o.endswith("_028")} >= {f"d_L{k}_028" for k in range(0, 7)}
    assert ["d_L0_003", "w_L0_013"] in out["blocked"]
    walls = {w["id"]: w for w in b["walls"]}
    assert all(DV.in_span(o, walls[o["wall_id"]]) for o in b["openings"]
               if o.get("type") in DV.DOOR_TYPES and not o.get("virtual") and o.get("wall_id") in walls)
    b = json.loads(REAL17_RUN.read_text(encoding="utf-8"))
    assert "d_L1_018" in DV.check(b)["same_room"]


REAL15_RUN = RUNS / "20261126-114512-full" / "results" / "furniture" / "real15" / "building.json"


@pytest.mark.skipif(not (REAL10_RUN.is_file() and REAL15_RUN.is_file()), reason="the runs of 26 Nov are not stored here")
def test_r01_the_stored_readings_heights():
    """The levels model run again on the run's readings: real15 in one frame (+0.50; every marked room at its floor but
    the garage, -0.25; the ground at the plans' ±0.00, -0.50; no entrance under it); real10's lift machine room at its
    door's floor (d_L7_001 at 21.00, the shaft head's +24.70 listed).

    27 Nov 2026 (audit H3): the run's real15 marks were typed before R01 d (its TERAS marks as ground); they are typed
    again as a fresh reading types them (the marks in the terraces are their floors). Typed as stored, they now stand
    flush with the doors (no door they would bury: the garage has its own way down) and stay the ground."""
    import json

    from wenart.levels import model as M
    from wenart.levels import read as RD

    b = json.loads(REAL15_RUN.read_text(encoding="utf-8"))
    for m in b["level_marks"]:
        m["kind"] = None
    RD.classify(b["level_marks"], b, M.level_params())
    n = M.infer_levels(b)
    assert n["level_inference"]["frame"]["value"] == 0.5
    marked = {r["id"]: r["floor_offset_m"] for r in n["rooms"] if r.get("floor_source") == "mark"}
    assert marked.pop("r_L0_garaj") == -0.25 and set(marked.values()) == {0.0}
    assert n["site"]["ground"]["levels"][0]["z"]["value"] == -0.5
    assert all(e["ground_z"] <= e["threshold_z"] for e in n["site"]["entrances"])
    n = M.infer_levels(json.loads(REAL10_RUN.read_text(encoding="utf-8")))
    assert next(r for r in n["rooms"] if r["id"] == "r_L7_asansor_mahali")["floor_offset_m"] == 0.0
    assert next(o for o in n["openings"] if o["id"] == "d_L7_001")["threshold_z"] == 21.0
