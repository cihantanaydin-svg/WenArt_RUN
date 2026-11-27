"""Audit fix round 2b (27 Nov 2026): the defects an independent review confirmed in audit fix round 2 (O1-O6, G1, H1-H9),
each fixed as a general rule (CPU; synthetic cases, the reviewers' probes, the real06 fixture of 25 Oct and, where the
drawings are here, a fresh reading of real10)."""
import copy
import math
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"


def _wall(wid, a, b, t=0.2, lid="L0", **kw):
    return dict({"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t, "evidence": []}, **kw)


def _door(oid, wall, c, w, lid="L0", ev=None, **kw):
    return dict({"id": oid, "type": "door", "level_id": lid, "wall_id": wall, "center": list(c), "width": w,
                 "evidence": ev if ev is not None else
                 [{"file": "t.dxf", "method": "vector", "confidence": 0.9, "rule": "size_tag", "entity": "TEXT:1"}]},
                **kw)


# ---------------------------------------------------------------------------------------------------- O1 Blender
def test_o1_the_layer_roles_and_the_outdoor_rules_import_without_jsonschema():
    """``shell.column_piece`` reads layer roles inside Blender (no jsonschema there): ``layer_names`` folds on
    ``wenart.textfold``; the architect's ``act_cover_space`` reads ``levels.outdoor``, whose slugs come from there too."""
    code = r'''
import sys
sys.modules["jsonschema"] = None
from wenart.ingest.generic import layer_names as LN
from wenart.levels import outdoor as OD
from wenart import textfold
assert LN.name_role("KOLON") == "structure" and LN.name_role("Sıva") == "plaster"
assert textfold.slugify("Yatak Odası") == "yatak_odasi"
print("ok")
'''
    res = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    assert res.returncode == 0 and res.stdout.strip() == "ok", res.stderr[-2000:]
    from wenart import building as B
    from wenart import textfold
    assert B.slugify is textfold.slugify and B.slugify("") == "room"


# ------------------------------------------------------------------------------------------- O2 / G1 / O3 doors
def test_o2_a_size_tag_keeps_the_drawn_doors_own_evidence():
    """real10 d_L0_028: read from its swing ARC:14F743 (1.03 m), re-sized by its '110/230': the tag's evidence first, the
    door's own after it, so the door check sees a drawn door and leaves its place."""
    from wenart.ingest import door_validity as DV
    from wenart.ingest.generic import core as C
    from wenart.ingest.generic.model import TextRun
    from wenart.ingest.model import OpeningItem

    drawn = {"file": "real10.dwg", "method": "vector", "confidence": 0.95, "entity": "ARC:14F743,LINE:14F752"}
    door = OpeningItem(kind="door", width=1.034, center=(16.07, 6.48), rotation_deg=0.0, box=[0, 0, 1, 1], entity="d",
                       evidence=dict(drawn))
    tag = TextRun(id="T110", text="110/230", box=(15.6, 5.62, 16.0, 5.72), height=0.1, rotation_deg=90.0,
                  evidence=[{"layer": "TEXT", "entity": "TEXT:14F593"}])
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [door], [tag], 1.0)
    assert got[0].width == pytest.approx(1.1) and got[0].evidence["rule"] == "size_tag"
    assert got[0].extra_evidence == [drawn]
    ev = [got[0].evidence] + got[0].extra_evidence           # as the reading writes the opening (pipeline)
    assert DV.drawn_symbol({"evidence": ev}) and not DV.drawn_symbol({"evidence": ev[:1]})
    # a gap the tag makes a door keeps the tag's evidence alone (no symbol of its own)
    gap = OpeningItem(kind="opening", width=1.1, center=(16.07, 6.48), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g",
                      evidence={"method": "derived", "entity": "gap:LINE:1"}, type_raw="unclassified gap content")
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [gap], [tag], 1.0)
    assert got[0].kind == "door" and got[0].extra_evidence == []


def test_o2_a_door_that_fills_the_bay_at_its_walls_end_keeps_its_place_and_the_wall_reaches_it():
    """A tag-placed door past its wall's end, between that end and the next wall on the line: the bay's door. Its host
    is extended to the next wall (labelled), the door keeps its place; in free space it is not built; a door read
    from its own swing is left as it is."""
    from wenart.ingest import door_validity as DV

    def plan(door_c, far_x=4.0):
        walls = [_wall("w_h", (0.0, 0.0), (3.0, 0.0)), _wall("w_x", (far_x, -2.0), (far_x, 2.0)),
                 _wall("w_s", (-1.0, -2.0), (-1.0, 2.0))]
        return {"walls": walls, "rooms": [], "openings": [_door("d_1", "w_h", door_c, 0.9)]}

    b = plan((3.45, 0.0))
    out = DV.check(b)
    assert out["extended"] == [["d_1", "w_h"]] and not out["not_built"] and not out["reseated"]
    w = next(x for x in b["walls"] if x["id"] == "w_h")
    assert w["end"][0] == pytest.approx(3.87, abs=0.01) and w["corrected_by_ai"]["before"]["end"] == [3.0, 0.0]
    assert b["openings"][0]["center"] == [3.45, 0.0] and DV.in_span(b["openings"][0], w)
    assert "fills the bay" in w["corrected_by_ai"]["reason"]
    # the same before the wall's start (the previous wall at x -1.0)
    b = plan((-0.5, 0.0))
    out = DV.check(b)
    w = next(x for x in b["walls"] if x["id"] == "w_h")
    assert out["extended"] == [["d_1", "w_h"]] and w["start"][0] == pytest.approx(-0.87, abs=0.01)
    # a corner closes the bay too: the next wall stops at the host's face (synthetic-16: 0.08 m short of its line)
    b = plan((3.45, 0.0))
    b["walls"][1] = _wall("w_x", (4.0, 0.1), (4.0, 2.0))
    assert DV.check(b)["extended"] == [["d_1", "w_h"]]
    # a bay much wider than the door is free space: not built, listed
    b = plan((3.45, 0.0), far_x=6.0)
    out = DV.check(b)
    assert out["not_built"] == ["d_1"] and b["needs_review"][0]["kind"] == "door_outside_wall"
    # a drawn door keeps its place, nothing changes
    b = plan((3.45, 0.0), far_x=6.0)
    b["openings"][0]["evidence"].append({"file": "t.dxf", "method": "vector", "confidence": 0.95, "entity": "ARC:1"})
    out = DV.check(b)
    assert not any(out[k] for k in ("extended", "not_built", "reseated")) and b["walls"][0]["end"] == [3.0, 0.0]


def _flats():
    from tests.test_audit_round2_20261126 import _flats as F
    return F()


def _strict(walls):
    from wenart.ingest.generic import facade as FC
    return FC.mirror_axis(walls, FC.MIRROR_FIX_SHARE)


def test_o3_a_mirror_twin_is_a_door_of_the_same_width_on_a_parallel_wall_that_holds_it_whole():
    """real10: the 1.10 m salon door took the place of a 0.80 m kitchen door on a perpendicular wall, 0.5 m past that
    wall's end, keeping its old swing side. Now: the same width, a parallel wall, the whole width on it, the swing side
    taken again; else it is listed."""
    from wenart.ingest import door_validity as DV

    def case(twin_w=1.1, twin_c=5.6, door_c=15.2):
        b = _flats()
        b["openings"][0] = _door("d_l", "w_x_l", (twin_c, 6.48), twin_w)
        b["openings"][1] = _door("d_r", "w_x_r", (door_c, 6.48), 1.1, swing_side="r_k_r")
        return b

    b = case()
    out = DV.check(b, mirror_axis=_strict)
    d = next(o for o in b["openings"] if o["id"] == "d_r")
    assert out["reseated"] == ["d_r"] and d["center"] == pytest.approx([14.4, 6.48]) and DV.span_inside(d, b["walls"][7])
    assert d["corrected_by_ai"]["before"]["swing_side"] == "r_k_r" and "same width" in d["corrected_by_ai"]["reason"]
    assert d["swing_side"] in (None, "r_s_r", "r_k_r")
    assert DV.check(case(twin_w=0.8), mirror_axis=_strict)["not_built"] == ["d_r"]          # another door's width
    # a twin whose mirror would stick out of the wall's end is no place for the door
    assert DV.check(case(twin_c=5.2, door_c=15.6), mirror_axis=_strict)["not_built"] == ["d_r"]
    # the original fixture: the twin stands on a perpendicular wall, 0.80 m wide: never moved
    b = _flats()
    assert DV.check(b, mirror_axis=_strict)["not_built"] == ["d_r"]


def test_o3_the_reading_reads_the_strict_mirror_axis():
    import inspect

    from wenart.ingest import pipeline as PL
    src = inspect.getsource(PL)
    line = next(x for x in src.splitlines() if "DV.check(building" in x)
    assert "MIRROR_FIX_SHARE" in line


@pytest.fixture(scope="module")
def real10(tmp_path_factory):
    """A fresh CPU reading of real10 (no AI)."""
    if not (PROJECTS / "real10").is_dir():
        pytest.skip("the real10 drawings are not here")
    from wenart.ingest import pipeline as PL

    out = tmp_path_factory.mktemp("real10")
    return PL.run_project(PROJECTS / "real10", out, no_ai=True)[0]


def test_g1_real10s_salon_door_stays_at_its_drawn_place(real10):
    """real10 d_L0..L6_028 (tag 110/230, swing ARC:14F743): at (16.07, 6.48), never moved into the solid wall w_L0_203;
    its drawn swing's evidence kept beside the tag's."""
    for k in range(0, 7):
        d = next(o for o in real10["openings"] if o["id"] == f"d_L{k}_028")
        assert math.dist(d["center"][:2], (16.07, 6.48)) <= 0.15, d
        assert not d.get("corrected_by_ai") and any(str(e.get("entity") or "").startswith("ARC:")
                                                    for e in d["evidence"])
    # every drawn door past its wall's end in no bay is listed (built where the drawing has it); the L-1 frame mostly
    # in free space (a 45° door read straight; the separator o_L-1_013 is that door) is listed too
    listed = {r["id"] for r in real10.get("needs_review") or [] if r.get("kind") == "door_outside_wall"}
    assert {f"d_L{k}_028" for k in range(0, 7)} <= listed
    l1 = [o for o in (real10["openings"] + (real10.get("openings_not_built") or [])) if o.get("level_id") == "L-1"
          and o.get("type") == "door" and math.dist(o["center"][:2], (6.06, 6.48)) < 0.2]
    assert l1 and all(o["id"] in listed for o in l1)
    assert not any((o.get("corrected_by_ai") or {}).get("rule") == "reading.door_validity" for o in real10["openings"])


# ---------------------------------------------------------------------------------------------------- O4 voids
def _void_case(rooms=(), stairs=(), voids=None):
    b = {"walls": [_wall("w_1", (5.87, 13.0), (5.87, 15.0), 0.15, lid="L1")], "rooms": list(rooms),
         "furniture": list(stairs),
         "openings": [_door("d_9", "w_1", (5.87, 14.05), 0.5, lid="L1"), _door("d_10", "w_1", (5.87, 13.3), 0.8,
                                                                                lid="L1")]}
    slabs = {"by_level": {"L1": {"under": {"voids": voids or [[[4.0, 13.7], [5.78, 13.7], [5.78, 15.5], [4.0, 15.5]]]}}}}
    return b, slabs


ROOM = {"id": "r_hall", "level_id": "L1", "room_type": "hall", "polygon": [[3.0, 12.0], [5.8, 12.0], [5.8, 16.0],
                                                                            [3.0, 16.0]]}
STAIR = {"id": "f_L1_1", "level_id": "L1", "type": "stair", "footprint": {"center": [4.9, 14.6], "size": [1.8, 2.0],
                                                                          "rotation_deg": 0.0}}


def test_o4_a_door_at_a_stair_head_or_before_a_room_over_an_unconfirmed_opening_is_built():
    """real14 d_L1_006 (the fire stair's door at the top of its flight), real18's bathroom doors and real19's hall
    doors (the openings of the levels below's stairs under their rooms) are built; a door over an opening its own plan
    draws the stair in, or with no room there, is not (the round's real06 case)."""
    from wenart.ingest import door_validity as DV

    b, slabs = _void_case()                                       # no room, no stair: a certain drop
    DV.voids_check(b, slabs)
    assert [o["id"] for o in b["openings"]] == ["d_10"] and b["needs_review"][0]["kind"] == "door_over_void"
    b, slabs = _void_case()                                       # the level below's stair head is there
    notes = DV.voids_check(b, slabs, stair_z=lambda lid, p: -0.2)
    assert len(b["openings"]) == 2 and not notes
    b, slabs = _void_case(stairs=[])
    notes = DV.voids_check(b, slabs, stair_z=lambda lid, p: -1.6)   # mid-flight, no room: a drop
    assert [o["id"] for o in b["openings"]] == ["d_10"]
    b, slabs = _void_case(rooms=[ROOM])                           # a room of L1 there, its plan draws no stair: built
    notes = DV.voids_check(b, slabs, stair_z=lambda lid, p: -1.6)
    assert len(b["openings"]) == 2 and len(notes) == 1 and "the drawn room wins" in notes[0]
    b, slabs = _void_case(rooms=[ROOM], stairs=[STAIR])           # ... and its plan draws the stair there: a drop
    DV.voids_check(b, slabs, stair_z=lambda lid, p: -1.6)
    assert [o["id"] for o in b["openings"]] == ["d_10"]
    # two of three probes across the width over the drop: listed, built
    b, slabs = _void_case(voids=[[[4.0, 13.95], [5.78, 13.95], [5.78, 15.5], [4.0, 15.5]]])
    notes = DV.voids_check(b, slabs)
    assert len(b["openings"]) == 2 and "most of its width" in notes[0] and b["needs_review"][0]["id"] == "d_9"


def test_o4_real06s_25_oct_fixture_door_over_the_stairs_turn_is_still_not_built():
    """real06 (25 Oct fixture): d_L1_004's inner side stands over the re-read stair's winders (1.4-1.6 m under L1),
    where L1's plan draws the stair: a drop, not built, as round 2 intended."""
    import json

    from wenart.blender import build as BB

    b = json.loads((ROOT / "tests" / "fixtures" / "real06_building_20261025.json").read_text(encoding="utf-8"))
    out = BB.prepare_once(b, "base", None)
    assert any(n.startswith("d_L1_004") and "not built" in n for n in out["door_checks"]["over_void"])
    assert not any(o["id"] == "d_L1_004" for o in out["building"]["openings"])


# ----------------------------------------------------------------------------------------------------- O5 column
def test_o5_a_column_glued_behind_a_door_is_said_not_cut():
    """real11: 14 doors listed 'the door is cut through it' while the build refused to cut the 0.73 m, 0.31 m piece
    (a column): one rule decides both, the finding says so."""
    from wenart.blender import shell
    from wenart.ingest import door_validity as DV

    host = _wall("w_h", (0.0, 0.0), (4.0, 0.0), 0.26)
    col = _wall("w_c", (1.6, 0.315), (2.33, 0.315), 0.31)
    wall = _wall("w_g", (0.5, 0.20), (3.5, 0.20), 0.07)
    for glued, cut in ((col, False), (wall, True)):
        b = {"walls": [host, glued], "rooms": [], "openings": [_door("d_1", "w_h", (2.0, 0.0), 1.0)]}
        out = DV.check(b)
        assert out["blocked"] == [["d_1", glued["id"]]]
        reason = b["needs_review"][0]["reason"]
        assert ("cut through it" in reason) is cut and ("never cut" in reason) is (not cut)
        assert DV.column_piece(glued, host) is (not cut) and shell.column_piece(glued, host) is (not cut)
        assert bool(shell.foreign_cuts(glued, {"w_h": host, glued["id"]: glued}, b["openings"])) is cut


# --------------------------------------------------------------------------------------------- H1/H2/G4 frames
def _two(l0, l1=(), source="section"):
    from tests.test_audit_round2_20261126 import _two_storeys
    return _two_storeys(l0, l1, source=source)


def _offsets(b):
    return {r["id"]: r["floor_offset_m"] for r in b["rooms"]}


def _types(b, **types):
    for r in b["rooms"]:
        base = r["id"].replace("_up", "")
        if base in types:
            r["room_type"] = types[base]
    return b


def test_h1_no_building_frame_from_sunken_rooms_a_split_level_or_a_printed_storey_mark():
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    # (1) the reviewers' h1: only the sunken garage and store marked; the storey from its title or a section
    for source in ("level_mark", "section"):
        b = _types(_two([("r_living", -0.45), ("r_bed", -0.45)], [("r_living", 3.0), ("r_bed", 3.0), ("r_hall", 3.0)],
                        source=source), r_living="garage", r_bed="storage")
        b["levels"][1]["elevation_source"] = source
        b["level_marks"] += [F.mark("lm_g0", -0.15, kind="ground_finished", point=(-1.0, 2.0)),
                             F.mark("lm_g1", -0.15, kind="ground_finished", point=(5.0, -1.0))]
        n = M.infer_levels(b)
        assert not n["level_inference"].get("frame") and not n["level_inference"].get("level_frames")
        off = _offsets(n)
        assert (off["r_living"], off["r_bed"], off["r_living_up"], off["r_hall_up"]) == (-0.45, -0.45, 0.0, 0.0)
        assert any(s["opening_id"] == "d_inner" for s in n["level_inference"]["inner_steps"])
        assert not n["level_inference"].get("ground_gate") and n["site"]["ground"]["source"] == "marks"
    # (2) the skeptic's s1: the hall marked at the floor once, garage and store -0.45: no frame (a room confirms it)
    b = _types(_two([("r_living", -0.45), ("r_bed", -0.45), ("r_hall", 0.0)], [("r_hall", 3.0)]),
               r_living="garage", r_bed="storage")
    n = M.infer_levels(b)
    assert not n["level_inference"].get("frame") and _offsets(n)["r_hall"] == 0.0 and _offsets(n)["r_hall_up"] == 0.0
    # (3) wet rooms 3 cm down, the salon at the floor
    b = _types(_two([("r_living", 0.0), ("r_bed", -0.03), ("r_hall", -0.03)], [("r_living", 3.0)]),
               r_bed="bathroom", r_hall="wc")
    n = M.infer_levels(b)
    assert not n["level_inference"].get("frame") and _offsets(n)["r_living"] == 0.0
    # (4) a split-level ground floor whose title prints ±0.00: the raised half keeps its +0.75
    b = _two([("r_living", 0.75), ("r_bed", 0.75), ("r_hall", 0.0)], [("r_hall", 3.0)], source="level_mark")
    b["levels"][1]["elevation_source"] = "level_mark"
    n = M.infer_levels(b)
    assert not n["level_inference"].get("frame") and _offsets(n)["r_living"] == 0.75 and _offsets(n)["r_hall_up"] == 0.0
    # (5) the elevation from a section's storey marks (elevation_rule) is a printed storey mark too
    b = _two([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.5)], [("r_hall", 3.5)])
    b["levels"][0]["elevation_rule"] = "section_storey_marks"
    assert M.printed_storey(b["levels"][0]) and not M.infer_levels(b)["level_inference"].get("frame")


def test_h1_the_real15_frame_holds_and_is_a_conflict():
    """real15's case (the section's ground floor, most of its rooms by area '+0.50', main rooms among them): one frame,
    recorded as a level_mark_mismatch naming the storey's title and the marks."""
    from wenart.levels import model as M

    n = M.infer_levels(_two([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.35)], [("r_hall", 3.5)]))
    assert n["level_inference"]["frame"]["value"] == 0.5 and n["level_inference"]["frame"]["rule"] == "set_frame_once"
    c = next(x for x in n["level_inference"]["conflicts"] if x["kind"] == "level_mark_mismatch" and "L0" in x["element_ids"])
    assert "Zemin Kat" in c["description"] and "+0.50" in c["description"] and "one height frame" in c["resolution"]


def test_h2_a_level_frame_only_from_most_of_a_storey_never_against_its_printed_mark():
    """real13 L-2: its title '2.BODRUM (-3.00 KOTU)' gives its elevation; its two rooms marked '-3.50' keep -0.50 (no
    level frame). A storey that marks only two sunken rooms keeps their steps; a raised half of an upper storey keeps
    its rise. A frame that is taken is a conflict, its rooms floor_source level_frame with the overruled marks."""
    from wenart.levels import model as M

    b = _two([], [("r_living", 2.5), ("r_bed", 2.5)])
    b["levels"][1]["elevation_source"] = "level_mark"                  # the storey's title prints its elevation
    n = M.infer_levels(b)
    assert not n["level_inference"].get("level_frames")
    assert (_offsets(n)["r_living_up"], _offsets(n)["r_bed_up"]) == (-0.5, -0.5)
    # only two sunken rooms marked (-0.60) on a storey from a section (the reviewers' h2 c): the hall is most of it
    n = M.infer_levels(_types(_two([], [("r_living", 2.4), ("r_bed", 2.4)]), r_living="storage", r_bed="technical"))
    assert not n["level_inference"].get("level_frames") and _offsets(n)["r_living_up"] == -0.6
    # a raised half (+0.45) and the hall at the floor (h2 b): the hall confirms the floor
    n = M.infer_levels(_two([], [("r_living", 3.45), ("r_bed", 3.45), ("r_hall", 3.0)]))
    assert not n["level_inference"].get("level_frames")
    assert (_offsets(n)["r_living_up"], _offsets(n)["r_hall_up"]) == (0.45, 0.0)
    # a frame taken: most of the storey, main rooms, no room at the floor
    n = M.infer_levels(_two([], [("r_living", 3.5), ("r_bed", 3.5), ("r_hall", 3.35)]))
    assert n["level_inference"]["level_frames"]["L1"]["value"] == 0.5
    rooms = {r["id"]: r for r in n["rooms"]}
    assert rooms["r_living_up"]["floor_source"] == "level_frame" and rooms["r_living_up"]["floor_offset_m"] == 0.0
    assert [m["raw"] for m in rooms["r_living_up"]["floor_overruled"]] == ["+3.50"]
    assert rooms["r_hall_up"]["floor_source"] == "mark" and rooms["r_hall_up"]["floor_offset_m"] == -0.15
    assert any(c["kind"] == "level_mark_mismatch" and c["element_ids"][0] == "L1" and "level's frame" in c["resolution"]
               for c in n["level_inference"]["conflicts"])
    from wenart import building as B
    assert not [e for e in B.validation_errors(n) if "floor_source" in e]


# ----------------------------------------------------------------------------------------------------- H3 gate
def test_h3_a_sunken_garage_never_refuses_the_drawn_ground_and_the_default_keeps_the_limit():
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    # the reviewers' h3: a garage 0.60 m down (its own drive), a garden sloping -0.15 / -0.45 / -0.30
    b = _types(_two([("r_living", -0.6), ("r_bed", 0.0), ("r_hall", 0.0)], [("r_hall", 3.0)]), r_living="garage")
    b["level_marks"] += [F.mark("lm_g0", -0.15, kind="ground_finished", point=(-1.0, 2.0)),
                         F.mark("lm_g1", -0.45, kind="ground_finished", point=(5.0, -1.0)),
                         F.mark("lm_g2", -0.30, kind="ground_finished", point=(11.0, 5.0))]
    n = M.infer_levels(b)
    assert not n["level_inference"].get("ground_gate") and n["site"]["ground"]["source"] == "marks"
    assert all(p["used"] for p in n["site"]["ground"]["points"])
    # the front door's hall 0.30 m down, the garden marks over it all round: refused; the default ground (0.15 m under
    # the storey) would still bury the door: held to its threshold
    b = _two([("r_living", 0.0), ("r_bed", 0.0), ("r_hall", -0.3)], [("r_hall", 3.0)])
    b["level_marks"] += [F.mark(f"lm_g{i}", 0.2, kind="ground_finished", point=p)
                         for i, p in enumerate([(-1.0, 2.0), (5.0, -1.0), (11.0, 5.0)])]
    n = M.infer_levels(b)
    gate = n["level_inference"]["ground_gate"]
    assert gate["refused"] == ["lm_g0", "lm_g1", "lm_g2"] and gate["buried"] == ["d_front"] and gate["limit"] == -0.3
    lv = n["site"]["ground"]["levels"][0]["z"]
    assert n["site"]["ground"]["source"] == "D3a" and lv["value"] == -0.3 and "held to" in lv["note"]
    # marks that bury no door stay, even over the plinth top elsewhere: the front door's hall raised 0.50 m, the garden
    # 0.20 m over the other rooms' floor (the terrain stands under the door's threshold)
    b = _two([("r_hall", 0.5)], [("r_hall", 3.0)])
    b["level_marks"] += [F.mark(f"lm_g{i}", 0.2, kind="ground_finished", point=p)
                         for i, p in enumerate([(-1.0, 2.0), (5.0, -1.0), (11.0, 5.0)])]
    n = M.infer_levels(b)
    assert not n["level_inference"].get("ground_gate") and n["site"]["ground"]["source"] == "marks"


# --------------------------------------------------------------------------------------------- H4 idempotence
def test_h4_infer_levels_run_again_changes_nothing():
    """The reviewers' h4: no section, the ground floor assumed, '+0.50' in one room and at the front door: the plans'
    frame is recorded (rule plan_frame) and a run again (an agent's level edit) keeps the levels, the ground and the
    entrances."""
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = _two([("r_living", 0.5)], [("r_hall", 3.5)], source="assumed_default")
    b["levels"][1]["elevation_source"] = "assumed_default"
    b["level_marks"].append(F.mark("lm_thr", 0.5, kind="threshold", point=(8.0, -0.3), door_id="d_front"))
    n1 = M.infer_levels(b)
    n2 = M.infer_levels(copy.deepcopy(n1))
    n3 = M.infer_levels(copy.deepcopy(n2))
    assert n1["level_inference"]["frame"]["rule"] == "plan_frame" and n2["level_inference"]["frame"]["again"]
    for n in (n2, n3):
        assert [(lv["id"], lv["elevation"]) for lv in n["levels"]] == [(lv["id"], lv["elevation"]) for lv in n1["levels"]]
        assert n["site"]["ground"]["levels"] == n1["site"]["ground"]["levels"]
        assert n["site"]["ground"]["source"] == n1["site"]["ground"]["source"]
        assert [(e["door_id"], e["solution"], e["ground_z"], e["rise"]) for e in n["site"]["entrances"]] == \
            [(e["door_id"], e["solution"], e["ground_z"], e["rise"]) for e in n1["site"]["entrances"]]
    # R01 a's frame run again keeps its record and its ground
    m1 = M.infer_levels(_two([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.5)], [("r_hall", 3.5)]))
    m2 = M.infer_levels(copy.deepcopy(m1))
    assert m2["level_inference"]["frame"]["rule"] == "set_frame_once" and m2["level_inference"]["frame"]["again"]
    assert m2["site"]["ground"]["levels"] == m1["site"]["ground"]["levels"]


# ---------------------------------------------------------------------------------------------------- H5 terrace
def _terrace_building(label="BAHÇE TERASI"):
    b = _two([], [("r_hall", 3.0)])
    b["site"] = {"areas": [{"id": "sa_L0_t", "level_id": "L0", "label": label, "anchor": [3.0, -1.5],
                            "polygon": [[0.0, -0.1], [6.0, -0.1], [6.0, -3.0], [0.0, -3.0]]}],
                 "boundary_walls": [], "decor": [], "openings": []}
    return b


def test_h5_a_mark_clearly_under_the_floor_in_a_terrace_is_the_ground_and_its_floor():
    from tests import _levels_fixture as F
    from wenart.levels import model as M
    from wenart.levels import read as RD

    b = _terrace_building()
    marks = [F.mark("lm_t1", -0.45, point=(1.0, -2.0)), F.mark("lm_t2", -0.45, point=(5.0, -2.5)),
             F.mark("lm_t3", 0.0, point=(3.0, -1.0)), F.mark("lm_t4", -0.15, point=(4.0, -1.0))]
    for m in marks:
        m["kind"] = None
    warns = RD.classify(marks, b, M.level_params())
    kinds = {m["id"]: m["kind"] for m in marks}
    # at the floor or a step under it: the terrace's floor; clearly under it: the ground there (and the floor)
    assert kinds == {"lm_t1": "ground_finished", "lm_t2": "ground_finished", "lm_t3": "floor", "lm_t4": "floor"}
    assert all(m.get("outdoor_area") for m in marks) and len([w for w in warns if "R01 d" in w]) == 4
    b["level_marks"] += [m for m in marks if m["id"] in ("lm_t1", "lm_t2")]
    n = M.infer_levels(b)
    assert n["site"]["ground"]["source"] == "marks"
    sp = next(s for s in n["site"]["outdoor_spaces"] if s["area_id"] == "sa_L0_t")
    assert sp["z"] == -0.45
    used = {m["id"]: m["used_for"] for m in n["level_marks"]}
    assert "ground" in used["lm_t1"] and any(u.startswith("outdoor_floor:") for u in used["lm_t1"])


def test_h5_real07s_raised_terrace_mark_stays_its_floor():
    """real07 lm_005 '+0.50' (z 0.00, the floor of the terrace on posts): the floor, marked used by the space."""
    from tests import _levels_fixture as F
    from wenart.levels import model as M
    from wenart.levels import read as RD

    b = _terrace_building("TERAS")
    m = F.mark("lm_005", 0.0, point=(2.0, -1.0))
    m["kind"] = None
    RD.classify([m], b, M.level_params())
    assert m["kind"] == "floor"
    b["level_marks"].append(m)
    n = M.infer_levels(b)
    mk = next(x for x in n["level_marks"] if x["id"] == "lm_005")
    assert any(u.startswith("outdoor_floor:") for u in mk["used_for"]) and "ground" not in mk["used_for"]


# ------------------------------------------------------------------------------------------------ H8 majority
def test_h8_a_clear_majority_of_a_rooms_marks_is_its_floor_the_level_floor_only_on_a_tie():
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = _two([("r_bed", 0.0), ("r_hall", 0.0)], [("r_hall", 3.0)])
    b["level_marks"] += [F.mark("lm_s1", -0.3, kind="floor", point=(1.5, 3.0), room_id="r_living"),
                         F.mark("lm_s2", -0.3, kind="floor", point=(1.5, 5.0), room_id="r_living"),
                         F.mark("lm_s3", 0.0, kind="floor", point=(1.5, 7.5), room_id="r_living")]
    n = M.infer_levels(b)
    assert _offsets(n)["r_living"] == -0.3
    c = next(x for x in n["level_inference"]["conflicts"] if "r_living" in x["element_ids"])
    assert "most of its marks" in c["resolution"]
    b["level_marks"] = [m for m in b["level_marks"] if m["id"] != "lm_s2"]           # a tie: the level floor
    assert _offsets(M.infer_levels(b))["r_living"] == 0.0


# ------------------------------------------------------------------------------------------------ H9 reasons
def test_h9_the_frame_ground_says_why():
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    n = M.infer_levels(_two([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.5)], [("r_hall", 3.5)]))
    g = n["site"]["ground"]
    assert g["source"] == "frame" and g["levels"][0]["z"]["evidence"][0]["rule"] == "plan_frame_zero"
    assert "no ground drawn" in g["surface"]["reason"] and not n["level_inference"].get("ground_gate")
    b = _two([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.5)], [("r_hall", 3.5)])
    b["level_marks"] += [F.mark(f"lm_g{i}", 0.6, kind="ground_finished", point=p)
                         for i, p in enumerate([(-1.0, 2.0), (5.0, -1.0), (11.0, 5.0)])]
    n = M.infer_levels(b)
    g = n["site"]["ground"]
    assert g["source"] == "frame" and g["levels"][0]["z"]["evidence"][0]["rule"] == "ground_gate"
    assert "refused" in g["surface"]["reason"] and n["level_inference"]["ground_gate"]
