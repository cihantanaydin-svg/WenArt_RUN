"""Audit fix round 5b (27 Nov 2026): copied storeys against the section (R22), stair floor openings from the stair and
the plan above, the roof's written pitch against its drawn heights (R07 d-g), a roof-terrace level's drawn edge ring
(R23), steps at doors between floors of different height, and upper outdoor spaces past the walls under them. Every test
builds its case in code; each fails on the code before this round (2475714f)."""
from __future__ import annotations

import copy
import math
from types import SimpleNamespace

import pytest

from wenart.ingest.generic.model import Stroke
from wenart.sheets.model import Ent, Region, Sheet, Txt


# --------------------------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------------------------

def _line(eid: str, a, b, layer: str = "0") -> Ent:
    st = Stroke(id=eid, kind="line", pts=[tuple(a), tuple(b)], layer=layer)
    return Ent(id=eid, kind="LINE", layer=layer, box=(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]),
                                                      max(a[1], b[1])), strokes=[st])


def _txt(tid: str, text: str, x, y, h: float = 0.2) -> Txt:
    w = max(len(text), 1) * h * 0.6
    return Txt(id=tid, text=text, box=(x - w / 2, y - h / 2, x + w / 2, y + h / 2), height=h)


def _sheet() -> Sheet:
    return Sheet(id="s1", space="model", file="x.dxf", page=1)


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _walls(level_id: str, x0, y0, x1, y1, t: float = 0.2, prefix: str = "w") -> list:
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for k, (a, b) in enumerate(zip(pts, pts[1:] + pts[:1])):
        out.append({"id": f"{prefix}_{level_id}_{k + 1:03d}", "level_id": level_id, "start": list(a), "end": list(b),
                    "thickness": t, "exterior": True, "height": None, "status": "verified", "evidence": []})
    return out


def _room(rid, level_id, poly, rtype="living", label=None):
    return {"id": rid, "level_id": level_id, "label": label or rid, "label_raw": label or rid, "room_type": rtype,
            "polygon": poly, "status": "verified", "evidence": []}


# --------------------------------------------------------------------------------------------------------------------
# R22: a jogged cut line is a cut line
# --------------------------------------------------------------------------------------------------------------------

def _plan_with_jogged_marks(jog: float) -> Region:
    """A 12 x 8 m building; its section marks 'A' left and right, the right one ``jog`` m higher (a jogged cut), both
    triangles standing on their line with the apex +y (the view)."""
    x0, y0 = 9.0, 6.0
    ents = [_line("w1", (x0, y0), (x0 + 12, y0)), _line("w2", (x0 + 12, y0), (x0 + 12, y0 + 8)),
            _line("w3", (x0 + 12, y0 + 8), (x0, y0 + 8)), _line("w4", (x0, y0 + 8), (x0, y0)),
            _line("w5", (x0 + 6, y0), (x0 + 6, y0 + 8))]
    texts = []
    for k, (x, yc) in enumerate(((x0 - 1.5, y0 + 3.0), (x0 + 13.5, y0 + 3.0 + jog))):
        pts = [(x - 0.2, yc), (x + 0.2, yc), (x, yc + 0.3464)]
        ents += [_line(f"t{k}a", pts[0], pts[1]), _line(f"t{k}b", pts[1], pts[2]), _line(f"t{k}c", pts[2], pts[0])]
        texts.append(_txt(f"A{k}", "A", x, yc - 0.35, 0.3))
    return Region(id="r4", file="x.dxf", sheet=_sheet(), box=(0, 0, 30, 20), geometry_box=(0, 0, 30, 20), ents=ents,
                  texts=texts, metres_per_unit=1.0, transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])


def test_r22_a_jogged_cut_line_gives_the_cut_axis_and_both_places():
    from wenart.sheets import register as RG
    sec = SimpleNamespace(title={"text": "A-A KESİTİ"})
    cut = RG.cut_line([_plan_with_jogged_marks(2.0)], sec)
    assert cut is not None and cut["axis"] == "x" and cut.get("jogged") is True
    assert cut["view"] == [0.0, 1.0] and cut["flipped"] is False
    assert [round(e[1], 2) for e in cut["ends"]] == [8.65, 10.65]        # each half of the cut at its own mark
    # a straight pair stays a straight cut (no jog record)
    straight = RG.cut_line([_plan_with_jogged_marks(0.0)], sec)
    assert straight is not None and not straight.get("jogged")


def _plan_with_bay_and_marks(bottom, top, label="A", interior=False) -> Region:
    """A 12 x 8 m plan whose south facade (y 0) has a pointed bay (x 4-8, its tip at y -2: it widens the outline's box);
    the letters ``label`` at ``bottom`` and ``top`` with a triangle each, its base along the cut (x = const), apex +x.
    ``interior``: the letters stand inside rooms beside a floor-level triangle (two wet rooms' labels, no cut)."""
    ents = [_line("w1", (0, 0), (4, 0)), _line("w2", (4, 0), (6, -2)), _line("w3", (6, -2), (8, 0)),
            _line("w4", (8, 0), (12, 0)), _line("w5", (12, 0), (12, 8)), _line("w6", (12, 8), (0, 8)),
            _line("w7", (0, 8), (0, 0)), _line("w8", (6, 0), (6, 8)), _line("w9", (0, 4), (12, 4))]
    texts = []
    for k, (x, y) in enumerate((bottom, top)):
        pts = [(x + 0.35, y - 0.2), (x + 0.35, y + 0.2), (x + 0.35 + 0.3464, y)]
        ents += [_line(f"t{k}a", pts[0], pts[1]), _line(f"t{k}b", pts[1], pts[2]), _line(f"t{k}c", pts[2], pts[0])]
        texts.append(_txt(f"m{k}", label, x, y, 0.3))
    return Region(id="r9", file="x.dxf", sheet=_sheet(), box=(-5, -5, 17, 13), geometry_box=(-5, -5, 17, 13), ents=ents,
                  texts=texts, metres_per_unit=1.0, transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])


def test_r22_cut_letters_stand_outside_the_outline_never_two_labels_inside_it():
    """Round 5b fix-up (SECTIONS-3): a letter at the facade line inside the outline's box (a pointed bay widens it) is a
    cut mark when it stands outside the outline polygon; two labels inside the plan, each by a floor-level triangle, on
    opposite sides of the centre, are no cut."""
    from wenart.sheets import register as RG
    sec = SimpleNamespace(title={"text": "KESİT"})
    cut = RG.cut_line([_plan_with_bay_and_marks((2.0, -0.6), (2.0, 9.6))], sec)
    assert cut is not None and cut["axis"] == "y" and cut["letter"] == "A"
    assert cut["view"] == [1.0, 0.0]
    # two 'WC' labels 1.15 m inside the end walls, on one line across the plan and 0.8 of its extent apart
    inside = RG.cut_line([_plan_with_bay_and_marks((1.15, 6.0), (10.85, 6.0), label="WC")], sec)
    assert inside is None
    # the pure test: each letter outside the polygon or within the beyond band of its boundary
    from shapely.geometry import Polygon
    poly = Polygon([(0, 0), (4, 0), (6, -2), (8, 0), (12, 0), (12, 8), (0, 8)])
    assert RG._outside_both(poly, (2.0, -0.6), (2.0, 9.6), 1, 1.0) is True
    assert RG._outside_both(poly, (1.15, 6.0), (10.85, 6.0), 0, 1.0) is False
    assert RG._outside_both(poly, (0.5, 6.0), (11.5, 6.0), 0, 1.0) is True       # within the band of the end walls
    assert RG._outside_both(poly, (-0.5, 6.0), (10.85, 6.0), 0, 1.0) is False    # one letter inside the plan


# --------------------------------------------------------------------------------------------------------------------
# R22: a copied storey against the section
# --------------------------------------------------------------------------------------------------------------------

def _copied_block():
    """Three storeys of a 10 x 12 m block (y 0-12); L0 copies the typical plan of L1 and L2. The plan draws a stair
    room (y 0-4) with a stair, a window on the facade and a door from the hall (y 4-12)."""
    levels, rooms, walls, furn, ops = [], [], [], [], []
    for k, lid in enumerate(("L0", "L1", "L2")):
        levels.append({"id": lid, "order": k, "elevation": 3.0 * k, "ceiling_height": 2.7, "label": lid,
                       "evidence": [{"file": "x.dxf"}], "typical_of": "L0" if k else None})
        rooms += [_room(f"r_{lid}_stair", lid, _rect(4, 0, 7, 4), "stair"), _room(f"r_{lid}_hall", lid, _rect(0, 4, 10, 12),
                                                                                  "hall")]
        walls += _walls(lid, 0, 0, 10, 12)
        furn.append({"id": f"f_{lid}_stair", "level_id": lid, "type": "stair", "room_id": f"r_{lid}_stair",
                     "footprint": {"center": [5.5, 2.0], "size": [1.2, 3.0], "rotation_deg": 0.0}, "evidence": []})
        ops += [{"id": f"win_{lid}_1", "level_id": lid, "type": "window", "center": [5.5, 0.0], "width": 1.5,
                 "wall_id": f"w_{lid}_001"},
                {"id": f"d_{lid}_1", "level_id": lid, "type": "door", "center": [5.5, 4.0], "width": 1.0,
                 "wall_id": None}]
    slabs = [{"id": f"sl_{lid}", "above_level_id": lid, "below_level_id": None, "outline": _rect(0, 0, 10, 12),
              "openings": [], "variants": []} for lid in ("L0", "L1", "L2")]
    slabs[2]["openings"].append({"id": "sv_L2_001", "kind": "stair_void", "furniture_id": "f_L1_stair",
                                 "polygon": _rect(5, 0.5, 6, 3.5), "source": "derived"})
    slabs[1]["openings"].append({"id": "sv_L1_001", "kind": "stair_void", "furniture_id": "f_L0_stair",
                                 "polygon": _rect(5, 0.5, 6, 3.5), "source": "derived"})
    b = {"levels": levels, "rooms": rooms, "walls": walls, "furniture": furn, "openings": ops, "slabs": slabs}
    return b


def _sheets(l0_gap=True, above_drawn=True, stair_strokes_l0=0, flipped=False, cut=True):
    """The sheets record: L0 inferred from the typical plan of L0-L2; a section along y at x 5.5, 12 m wide, its slab
    bands at 0, 3, 6 and 9 m: the band at L0's floor stops 4 m from the min end (a double-height space) when
    ``l0_gap``; the strokes of a stair over s 0.5-3.5 in the storeys of L1 and L2 and ``stair_strokes_l0`` in L0's."""
    def band(z, cover):
        return {"z": z, "thickness": 0.3, "cover_top": cover, "cover_bottom": cover}
    full = [[0.0, 12.0]]
    stretch = (lambda a, b: [[12.0 - b, 12.0 - a]]) if flipped else (lambda a, b: [[a, b]])
    l0 = stretch(4.0, 12.0) if l0_gap else full
    l1 = full if above_drawn else stretch(4.0, 12.0)
    stairs = {str(k): 6 for k in range(int((12 - 3.5 if flipped else 0.5) / 0.25),
                                       int((12 - 0.5 if flipped else 3.5) / 0.25))}
    few = dict(list(stairs.items())[:stair_strokes_l0]) if stair_strokes_l0 else {}
    ev = {"region_id": "r1", "z_frame": "level_marks", "s_width": 12.0, "bin_m": 0.25,
          "bands": [band(0.0, l0), band(3.0, l1), band(6.0, full), band(9.0, full)],
          "storeys": [{"z_floor": 0.0, "z_ceiling": 2.7, "strokes": few},
                      {"z_floor": 3.0, "z_ceiling": 5.7, "strokes": stairs},
                      {"z_floor": 6.0, "z_ceiling": 8.7, "strokes": stairs}],
          "cut": {"axis": "y", "at": 5.5, "flipped": flipped} if cut else None}
    return {"levels": [{"id": "L0", "order": 0, "typical": {"levels": ["L0", "L1", "L2"], "inferred": ["L0"]}},
                       {"id": "L1", "order": 1}, {"id": "L2", "order": 2}],
            "heights": {"section_evidence": ev}}


@pytest.mark.parametrize("flipped", [False, True])
def test_r22_rooms_over_a_double_height_space_are_not_built_on_the_copy(flipped):
    from wenart.sheets import typical_check as TCK
    b = _copied_block()
    rec = TCK.check(b, _sheets(flipped=flipped))
    ids = {r["id"] for r in b["rooms"]}
    assert "r_L0_stair" not in ids and "r_L1_stair" in ids and "r_L0_hall" in ids
    assert "f_L0_stair" not in {f["id"] for f in b["furniture"]}
    gone = {o["id"] for o in b["openings"]}
    assert "win_L0_1" not in gone and "d_L0_1" not in gone and "win_L1_1" in gone      # facade window and door go
    sl0 = next(s for s in b["slabs"] if s["id"] == "sl_L0")
    assert [o["kind"] for o in sl0["openings"]] == ["void"] and sl0["openings"][0]["rule"] == "typical_vs_section"
    # the stair not built on the copy cuts no opening in the slab above it
    assert not any(o.get("furniture_id") == "f_L0_stair" for s in b["slabs"] for o in s["openings"])
    assert rec["dropped"][0]["room"] == "r_L0_stair"


def _corrections_file(tmp_path, rows):
    import json
    path = tmp_path / "reading_corrections.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


def test_r22_the_section_acts_but_a_users_correction_on_the_storey_vetoes_the_whole_stretch(tmp_path, monkeypatch):
    """Fix-up (SECTIONS-4): R22 acts (``ACT``); a double-height stretch holding anything a correction of the user asserts
    present on that copied storey is left whole as it is (the room, its stair, its openings), listed as a conflict naming
    the correction; a correction of another project, another storey or a brief input vetoes nothing."""
    from wenart.sheets import typical_check as TCK
    assert TCK.ACT is True
    orig = TCK.user_assertions

    def run(rows):
        path = _corrections_file(tmp_path, rows)
        monkeypatch.setattr(TCK, "user_assertions", lambda project, lid, path_=None: orig(project, lid, path))
        b = _copied_block()
        b["project"] = {"id": "pX"}
        warns, conflicts = [], []
        build = SimpleNamespace(building=b, sheets=_sheets(), frame_shift=(0.0, 0.0), warn=warns.append,
                                conflict=lambda *a: conflicts.append(a))
        return b, TCK.apply(build), warns, conflicts

    # no correction: the section wins, every removal carries the section crop's evidence
    b, rec, warns, conflicts = run([])
    assert rec["acted"] is True and [d["room"] for d in rec["dropped"]] == ["r_L0_stair"]
    assert "r_L0_stair" not in {r["id"] for r in b["rooms"]} and not rec.get("vetoed")
    assert rec["dropped"][0]["evidence"]["rule"] == "typical_vs_section"
    # the user asserts the stair on L0 (its place on the stair): nothing of the stretch changes
    row = {"id": "C9", "project": "pX", "status": "accepted", "level": "L0", "place": {"x": 5.5, "y": 2.0},
           "user_words": "the stair is here"}
    b, rec, warns, conflicts = run([row])
    before = _copied_block()
    assert {r["id"] for r in b["rooms"]} == {r["id"] for r in before["rooms"]}
    assert {o["id"] for o in b["openings"]} == {o["id"] for o in before["openings"]}
    assert next(f for f in b["furniture"] if f["id"] == "f_L0_stair").get("build") is not False
    assert rec["dropped"] == [] and rec["stairs"] == []
    assert {c for v in rec["vetoed"] for c in v["corrections"]} == {"C9"}
    assert any("left as it is" in w and "C9" in w for w in warns)
    assert any("C9" in a[2] for a in conflicts)
    # the correction's place in the room, away from its stair: the stair of the kept room stays too (no partial removal)
    b, rec, _w, _c = run([dict(row, place={"x": 4.2, "y": 3.8})])
    assert "r_L0_stair" in {r["id"] for r in b["rooms"]} and rec["stairs"] == []
    assert next(f for f in b["furniture"] if f["id"] == "f_L0_stair").get("build") is not False
    # a correction of another project, another storey, or a brief input: the section acts
    for other in (dict(row, project="pY"), dict(row, level="L1"), dict(row, truth_role="brief_input"),
                  dict(row, status="rejected")):
        b, rec, _w, _c = run([other])
        assert [d["room"] for d in rec["dropped"]] == ["r_L0_stair"], other


def test_r22_user_assertions_read_the_corrections_and_their_elements(tmp_path):
    from wenart.sheets import typical_check as TCK
    rows = [{"id": "C1", "project": "pX", "status": "accepted", "level": "L0", "place": {"x": 1.0, "y": 2.0}},
            {"id": "C2", "project": "pX", "status": "accepted", "level": "L2",
             "truth_action": {"elements": [{"op": "add", "level": "L0", "center": [3.0, 4.0],
                                            "polygon": _rect(2, 3, 4, 5)},
                                           {"op": "remove", "level": "L0", "center": [9.0, 9.0]}]}}]
    got = TCK.user_assertions("pX", "L0", _corrections_file(tmp_path, rows))
    assert [(a["id"], a["points"]) for a in got] == [("C1", [(1.0, 2.0)]), ("C2", [(3.0, 4.0)])]
    assert got[1]["polygons"] == [_rect(2, 3, 4, 5)]
    assert TCK.user_assertions(None, "L0", _corrections_file(tmp_path, rows)) == []


def test_r22_the_frame_stands_on_the_copied_storeys_own_outline():
    """Fix-up (SECTIONS-5): a basement longer than the storeys the section's walls bound does not move the stretch; a
    section whose ends lie more than ``END_TOL_M`` from the storey's facades is not placed."""
    from wenart.sheets import typical_check as TCK
    b = _copied_block()
    b["levels"].insert(0, {"id": "L-1", "order": -1, "elevation": -3.0, "ceiling_height": 2.7, "label": "L-1",
                           "evidence": [{"file": "x.dxf"}]})
    b["walls"] += _walls("L-1", 0, -3.0, 10, 15.0)                           # 6 m longer along the cut
    b["rooms"].append(_room("r_Lm1_hall", "L-1", _rect(0, -3.0, 10, 15.0), "hall"))
    rec = TCK.check(b, _sheets())
    assert [d["room"] for d in rec["dropped"]] == ["r_L0_stair"]
    # the section 1 m wider than the storey: each end 0.5 m off its facade: not checked
    sh = _sheets()
    sh["heights"]["section_evidence"]["s_width"] = 13.2
    b2 = _copied_block()
    rec2 = TCK.check(b2, sh)
    assert rec2["dropped"] == [] and any("cannot be placed" in n for n in rec2["notes"])


def test_r22_a_split_level_is_no_double_height_space():
    """Fix-up (SECTIONS-6): where the section draws the copy's floor at another height over the stretch (its own slab
    lines, a split level or a sunken floor), nothing is removed."""
    from wenart.sheets import typical_check as TCK
    sh = _sheets()
    sh["heights"]["section_evidence"]["bands"][0]["near_slabs"] = [{"s": [0.0, 4.0], "z": -0.45}]
    b = _copied_block()
    rec = TCK.check(b, sh)
    dh = rec["checked"][0]["double_height"]
    assert rec["dropped"] == [] and dh and dh[0]["used"] is False and "split level" in dh[0]["why"]


def test_r22_section_evidence_reads_a_lower_slab_beside_the_band():
    """The section's own lines of a floor 0.45 m under the band (a split level) are the band's ``near_slabs``."""
    from wenart.sheets import heights as HT
    from wenart.sheets import section_evidence as SEV
    ents = []
    for k, (a, b_) in enumerate([((0, -1.5), (0, 9.0)), ((12, -1.5), (12, 9.0)), ((0.25, -1.5), (0.25, 9.0)),
                                 ((11.75, -1.5), (11.75, 9.0)), ((0, -0.3), (7, -0.3)), ((0, 0.0), (7, 0.0)),
                                 ((7, -0.75), (12, -0.75)), ((7, -0.45), (12, -0.45)), ((7, -0.45), (7, 0.0))]):
        ents.append(_line(f"l{k}", a, b_))
    for k, y in enumerate((2.7, 5.7, 8.7)):
        ents += [_line(f"f{k}a", (0, y), (12, y)), _line(f"f{k}b", (0, y + 0.3), (12, y + 0.3))]
    reg = Region(id="r1", file="x.dxf", sheet=_sheet(), box=(-5, -5, 20, 15), geometry_box=(-5, -5, 20, 15), ents=ents,
                 texts=[], metres_per_unit=1.0, transform_to_building=None)
    sec = HT.read_section(reg, 1.0)
    ev = SEV.read(sec, {"_bands": [(sec.bands[0][0], sec.bands[0][1])]}, {"axis": "y", "at": 5.0, "flipped": False})
    near = ev["bands"][0].get("near_slabs") or []
    assert near and min(q["s"][0] for q in near) <= 7.5 and max(q["s"][1] for q in near) >= 11.0


def test_r22_nothing_changes_when_the_section_does_not_say_so_clearly():
    from wenart.sheets import typical_check as TCK
    for kw in ({"l0_gap": False}, {"above_drawn": False}, {"cut": False}):
        b = _copied_block()
        before = copy.deepcopy(b)
        rec = TCK.check(b, _sheets(**kw))
        assert b["rooms"] == before["rooms"] and b["openings"] == before["openings"], kw
        if kw.get("cut") is False:
            assert rec["notes"] and "no cut line" in rec["notes"][0]


def test_r22_a_stair_the_section_does_not_draw_in_the_copys_storey_is_not_built():
    from wenart.sheets import typical_check as TCK
    b = _copied_block()
    rec = TCK.check(b, _sheets(l0_gap=False))
    f0 = next(f for f in b["furniture"] if f["id"] == "f_L0_stair")
    assert f0["build"] is False and rec["stairs"][0]["stair"] == "f_L0_stair"
    assert next(f for f in b["furniture"] if f["id"] == "f_L1_stair").get("build") is not False
    assert not any(o.get("furniture_id") == "f_L0_stair" for s in b["slabs"] for o in s["openings"])
    # the section draws the stair in the copy's storey too: kept
    b2 = _copied_block()
    TCK.check(b2, _sheets(l0_gap=False, stair_strokes_l0=12))
    assert next(f for f in b2["furniture"] if f["id"] == "f_L0_stair").get("build") is not False


# --------------------------------------------------------------------------------------------------------------------
# stair floor openings: from the stair, clipped to the rooms of the level above; a stair that does not stack cuts none
# --------------------------------------------------------------------------------------------------------------------

def test_stair_opening_is_clipped_to_the_rooms_a_stair_arrives_in():
    from wenart.sheets import to_building as TB
    rooms = [_room("r_L1_hall", "L1", _rect(0, 0, 4, 4), "hall"), _room("r_L1_bath", "L1", _rect(4, 0, 6, 4), "bathroom")]
    fit = TB.void_fit(_rect(1, 1, 5, 3), "L1", rooms)
    assert fit["stacks"] is True and fit["clipped"] == ["r_L1_bath"] and abs(fit["clipped_m2"] - 2.0) < 0.05
    from shapely.geometry import Polygon
    assert abs(Polygon(fit["polygon"]).area - 6.0) < 0.05
    # mostly in a bedroom: the stair does not stack with the plan above
    rooms2 = [_room("r_L1_hall", "L1", _rect(0, 0, 2, 4), "hall"), _room("r_L1_bed", "L1", _rect(2, 0, 6, 4), "bedroom")]
    assert TB.void_fit(_rect(1, 1, 5, 3), "L1", rooms2)["stacks"] is False
    # no closed room under it: as before
    assert TB.void_fit(_rect(1, 1, 5, 3), "L1", rooms[:1])["clipped"] == []
    # a stair the plan above draws there (in the bedroom) stacks: its place stays open
    from shapely.geometry import Polygon as _P
    fit3 = TB.void_fit(_rect(1, 1, 5, 3), "L1", rooms2, [_P(_rect(2.0, 0.8, 5.2, 3.2))])
    assert fit3["stacks"] is True and fit3["clipped"] == []


def test_the_build_keeps_a_clipped_opening_and_cuts_none_for_a_stair_that_does_not_stack():
    from wenart.blender import shell as SH
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}, {"id": "L1", "elevation": 3.0,
                                                                           "ceiling_height": 2.7}],
         "walls": _walls("L0", 0, 0, 8, 6) + _walls("L1", 0, 0, 8, 6), "rooms": [], "openings": [],
         "furniture": [{"id": "f_L0_1", "level_id": "L0", "type": "stair",
                        "footprint": {"center": [2.0, 3.0], "size": [1.0, 3.6], "rotation_deg": 90.0}}],
         "slabs": [{"id": "sl_L1", "above_level_id": "L1", "below_level_id": "L0", "z_top": 3.0, "thickness": 0.2,
                    "outline": _rect(0, 0, 8, 6), "openings": [], "variants": [],
                    "stairs_not_stacked": [{"stair": "f_L0_1"}]}]}
    plan = SH.slab_plan(b, b["levels"], 0.2)
    rec = plan["by_level"]["L1"]["under"]
    assert rec["voids"] == [] and "f_L0_1" not in rec["stairs"]
    clipped = _rect(1.5, 1.5, 2.5, 3.0)
    b["slabs"][0].pop("stairs_not_stacked")
    b["slabs"][0]["openings"] = [{"id": "sv_L1_001", "kind": "stair_void", "furniture_id": "f_L0_1",
                                  "polygon": clipped, "source": "derived", "clipped_rooms": ["r_L1_bath"]}]
    rec2 = SH.slab_plan(b, b["levels"], 0.2)["by_level"]["L1"]["under"]
    assert len(rec2["voids"]) == 1 and not any("widened" in a for a in rec2["assumed"])


def test_stair_opening_counts_uncovered_area_as_open_and_keeps_a_closed_room_inside_it_as_a_hole():
    """Fix-up (SLABS-1, SLABS-3): the part of the opening no room covers is open (a stair well); 'does not stack' needs
    closed rooms over more than half of it; a closed room inside the opening is cut round (no hole quietly open)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from wenart.sheets import to_building as TB
    # a 2 m2 bedroom strip over an 8 m2 opening, the rest in no room: the strip is clipped, the well stays open
    fit = TB.void_fit(_rect(1, 1, 5, 3), "L1", [_room("r_L1_bed", "L1", _rect(4, 0, 6, 4), "bedroom")])
    assert fit["stacks"] is True and fit["clipped"] == ["r_L1_bed"] and fit["open_m2"] == pytest.approx(6.0, abs=0.05)
    assert Polygon(fit["polygon"]).area == pytest.approx(6.0, abs=0.05)
    # a 1 m2 WC inside a 24 m2 opening: the opening is the rest, in pieces without holes
    fit2 = TB.void_fit(_rect(0, 0, 6, 4), "L1", [_room("r_L1_wc", "L1", _rect(2, 1.5, 3, 2.5), "wc")])
    polys = [Polygon(q) for q in fit2["polygons"]]
    assert fit2["clipped"] == ["r_L1_wc"] and len(polys) >= 2 and all(not q.interiors for q in polys)
    assert unary_union(polys).area == pytest.approx(23.0, abs=0.1)
    assert not unary_union(polys).intersects(Polygon(_rect(2.05, 1.55, 2.95, 2.45)))
    # a store near the opening's edge: no piece of the opening round it is lost (its narrow side piece is 0.38 m2)
    fit3 = TB.void_fit(_rect(0, 0, 6, 4), "L1", [_room("r_L1_depo", "L1", _rect(0.05, 0.2, 0.95, 3.8), "storage")])
    u3 = unary_union([Polygon(q) for q in fit3["polygons"]])
    assert fit3["clipped"] == ["r_L1_depo"] and u3.area == pytest.approx(24.0 - 0.9 * 3.6, abs=0.05)


def test_open_plan_kitchens_generic_rooms_garages_and_stores_close_an_opening_only_where_their_walls_cross_it():
    """Fix-up (SLABS-5): an open-plan kitchen, a generic 'ODA', a garage or a store is a common arrival: it closes the
    opening only where one of its edges (a wall) crosses the flights."""
    from wenart.sheets import to_building as TB
    for rtype, label in (("kitchen", "MUTFAK-SALON"), ("bedroom", "ODA"), ("garage", "GARAJ"), ("storage", "DEPO")):
        whole = [_room("r_L1_x", "L1", _rect(0, 0, 8, 6), rtype, label)]
        fit = TB.void_fit(_rect(1, 1, 5, 3), "L1", whole)
        assert fit["stacks"] is True and fit["closed"] == [], (rtype, label)
        # its wall crosses the flights (the room covers only half the opening): closed there
        half = [_room("r_L1_x", "L1", _rect(3, 0, 8, 6), rtype, label)]
        assert TB.void_fit(_rect(1, 1, 5, 3), "L1", half)["closed"] == ["r_L1_x"], (rtype, label)
    # a closed kitchen (no open-plan word) closes it
    assert TB.void_fit(_rect(1, 1, 5, 3), "L1", [_room("r_L1_k", "L1", _rect(0, 0, 8, 6), "kitchen",
                                                       "MUTFAK")])["stacks"] is False


def _flight_stair(fid="f_L0_1", level="L0", x=1.0, y0=0.5):
    """One straight flight along +y at ``x``, 1.0 m wide, from ``y0`` (17 lines, 0.25 m going: 4 m)."""
    return {"id": fid, "level_id": level, "type": "stair", "room_id": f"r_{level}_hall", "source": "from_documents",
            "footprint": {"center": [x, y0 + 2.0], "size": [1.0, 4.2], "rotation_deg": 0.0}, "build": True,
            "stair": {"flights": [{"start": [x, y0], "end": [x, y0 + 4.0], "width": 1.0, "lines": 17,
                                   "spacing": 0.25}],
                      "direction": [0.0, 1.0], "direction_assumed": False, "turn": "straight", "turn_assumed": False,
                      "void_assumed": True, "riser_m": None, "riser_source": None, "reason": "test"}}


def _slab_case(rooms_l1, furniture=None):
    from shapely.geometry import box
    from wenart.sheets import to_building as TB
    levels = [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.8},
              {"id": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.8}]
    unions = {"L0": box(-0.1, -0.1, 8.1, 6.1), "L1": box(-0.1, -0.1, 8.1, 6.1)}
    furn = furniture or [_flight_stair()]
    rooms = [_room("r_L0_hall", "L0", _rect(0, 0, 8, 6), "hall")] + rooms_l1
    warns = []
    slabs = TB.slabs_block({"heights": {}}, levels, unions, furn, 0.2, warns.append, rooms=rooms)
    b = {"levels": levels, "furniture": furn, "slabs": slabs, "rooms": rooms, "openings": [],
         "walls": _walls("L0", -0.1, -0.1, 8.1, 6.1) + _walls("L1", -0.1, -0.1, 8.1, 6.1)}
    return b, warns


def test_slabs_block_blocks_a_stair_that_does_not_stack_and_the_checks_see_it():
    """Fix-up (SLABS-2, integration): a stair under a bedroom of the plan above gets no opening, is blocked (the level
    above cannot be reached by it): the slab lists it, RC17 raises it as critical, M9 judges the stair cut off and the
    build-time fix leaves it open (never 'fixed')."""
    from wenart.blender import stair_access as SA
    from wenart.reading_check import structure as ST
    b, warns = _slab_case([_room("r_L1_bed", "L1", _rect(0, 0, 4, 6), "bedroom"),
                           _room("r_L1_hall", "L1", _rect(4, 0, 8, 6), "hall")])
    f = b["furniture"][0]
    sl = next(x for x in b["slabs"] if x["id"] == "sl_L1")
    assert f["stair_blocked"]["level_above"] == "L1" and f["stair_blocked"]["closed_rooms"] == ["r_L1_bed"]
    assert sl["openings"] == [] and sl["stairs_not_stacked"][0]["stair"] == "f_L0_1"
    assert any("does not stack" in w for w in warns)
    rc = ST.stairs_blocked(b)
    assert [(x["rule"], x["severity"]) for x in rc] == [("stair_blocked", "critical")]
    assert "cannot be reached" in rc[0]["message"]
    m9 = SA.walk_review(b)
    assert [(x["stair"], x["ok"]) for x in m9["stairs"]] == [("f_L0_1", False)]
    assert "cannot be reached" in SA.cut_off_text(m9["stairs"][0])
    assert [(x["stair"], x["status"]) for x in SA.fix_arrivals(b)["stairs"]] == [("f_L0_1", "open")]
    # Argus's sense (N3): with an entrance on L0, the level above is reached by no stair
    from wenart.audit import sense as AS
    b["openings"] = [{"id": "d_in", "level_id": "L0", "type": "door", "wall_id": "w_L0_001", "width": 0.9,
                      "center": [6.0, -0.1]}]
    b["walls"].append({"id": "w_L1_mid", "level_id": "L1", "start": [4, 0], "end": [4, 6], "thickness": 0.1})
    b["openings"].append({"id": "d_bed", "level_id": "L1", "type": "door", "wall_id": "w_L1_mid", "width": 0.9,
                          "center": [4.0, 5.0]})
    assert ("N3", "critical") in [(x["check"], x["severity"]) for x in AS.audit(b)["findings"]]
    # the plan above draws a hall there: the stair stacks again and the stale block is cleared on a re-read
    b2, _w = _slab_case([_room("r_L1_hall", "L1", _rect(0, 0, 8, 6), "hall")], furniture=b["furniture"])
    assert "stair_blocked" not in b2["furniture"][0]
    assert [o["kind"] for o in next(x for x in b2["slabs"] if x["id"] == "sl_L1")["openings"]] == ["stair_void"]


def test_a_clipped_opening_reports_the_headroom_over_the_flights_left_under_the_slab():
    """Fix-up (SLABS-4): a bathroom over the top of the flight: the opening is clipped and says how much clear height
    the flights under the bathroom keep (under 2.00 m: RC17 stair_headroom)."""
    from shapely.geometry import Polygon
    from wenart.reading_check import structure as ST
    b, warns = _slab_case([_room("r_L1_hall", "L1", _rect(0, 0, 8, 3.6), "hall"),
                           _room("r_L1_bath", "L1", _rect(0, 3.6, 3, 6), "bathroom")])
    sl = next(x for x in b["slabs"] if x["id"] == "sl_L1")
    o = sl["openings"][0]
    assert o["clipped_rooms"] == ["r_L1_bath"] and o["headroom_short"] is True and o["headroom_m"] < 0.5
    assert Polygon(o["polygon"]).bounds[3] <= 3.6 + 1e-6
    assert "clear height" in o["reason"] and any("clear height" in w for w in warns)
    assert [(x["rule"], x["severity"]) for x in ST.stairs_blocked(b)] == [("stair_headroom", "major")]


def test_the_same_stair_offset_on_the_level_above_is_a_registration_finding_and_keeps_the_opening():
    """Fix-up (SLABS-4, real19 L2): the plan above draws the same stair 1.70 m off (its levels registered off): the
    opening over the stair below is kept, a registration finding (RC17 major), never a blocked stair."""
    from wenart.reading_check import structure as ST
    up = _flight_stair("f_L1_1", "L1", x=2.7)
    b, warns = _slab_case([_room("r_L1_bed", "L1", _rect(0, 0, 2.2, 6), "bedroom"),
                           _room("r_L1_hall", "L1", _rect(2.2, 0, 8, 6), "hall")], furniture=[_flight_stair(), up])
    f = b["furniture"][0]
    sl = next(x for x in b["slabs"] if x["id"] == "sl_L1")
    assert "stair_blocked" not in f
    ops = [o for o in sl["openings"] if o.get("furniture_id") == "f_L0_1"]
    assert ops and ops[0]["registration"]["stair"] == "f_L1_1" and ops[0]["registration"]["offset_m"] == 1.7
    assert any("registered off" in w for w in warns)
    assert ("stair_registration", "major") in [(x["rule"], x["severity"]) for x in ST.stairs_blocked(b)]


# --------------------------------------------------------------------------------------------------------------------
# R07: section roof heights in a rejected frame, slopes in degrees, marks snapped, written pitch vs drawn heights
# --------------------------------------------------------------------------------------------------------------------

def test_r07e_roof_heights_go_with_rejected_storey_heights():
    from wenart.sheets import heights as HT
    out = {"roof": {"eaves_z": {"value": 13.62, "method": "vector"}, "ridge_z": {"value": 15.74, "method": "vector"},
                    "knee_wall": None, "overhang": {"value": 2.9, "method": "vector"},
                    "pitches_deg": [{"value": 6.4, "method": "vector"}], "profile": [[0, 13.6], [5, 15.7]]}}
    line = HT.reject_roof(out, "the section's heights are no storeys (L-1 ceiling 14.05 m)")
    r = out["roof"]
    assert line and r["eaves_z"]["value"] is None and r["eaves_z"]["method"] == "assumed"
    assert r["ridge_z"]["value"] is None and r["overhang"]["value"] is None and r["profile"] == []
    assert r["pitches_deg"][0]["value"] == 6.4 and r["rejected"]["eaves_z"] == 13.62
    assert HT.reject_roof({"roof": {"eaves_z": None, "ridge_z": None, "profile": []}}, "x") is None


@pytest.mark.parametrize("text,roof,pct,unit", [
    ("EĞİM 30°", False, 57.735, "degrees"), ("EĞİM 30 DERECE", False, 57.735, "degrees"), ("30°", True, 57.735, "degrees"),
    ("EĞİM 30", False, 30.0, "percent"), ("EĞİM:35", False, 35.0, "percent"), ("%30 EĞİM", False, 30.0, "percent"),
    # fix-up (SECTIONS-7): a bare number is per cent over its whole range: 9.9 is flatter than 10, never 17 %
    ("EĞİM 7", False, 7.0, "percent"), ("EĞİM 9.9", True, 9.9, "percent"), ("EĞİM 10", True, 10.0, "percent"),
    ("RAMP SLOPE 8", False, 8.0, "percent")])
def test_r07f_written_slopes_in_degrees_and_bare_numbers(text, roof, pct, unit):
    from wenart.sheets import titles as T
    rd = T.slope_reading(text, roof)
    assert rd is not None and abs(rd["pct"] - pct) < 0.01 and rd["unit"] == unit
    assert abs(T.slope_pct(text, roof) - pct) < 0.01


def test_r07f_no_slope_from_a_bare_angle_off_a_roof_plan_or_a_length():
    from wenart.sheets import titles as T
    assert T.slope_pct("30°", roof=False) is None and T.slope_pct("EĞİM 30 cm", roof=True) is None
    assert T.slope_pct("EĞİM 2", roof=True) is None and T.slope_reading("EĞİM 2 m") is None
    # fix-up (SECTIONS-7): every length word, and a plan's 45 or 90 degree angle, is no slope
    for text in ("EĞİM 30 MT", "EĞİM 30 METRE", "EĞİM 30 mt", "SLOPE 12 METERS", "EĞİM 12 M2", "EĞİM 30 ADET"):
        assert T.slope_reading(text, roof=True) is None, text
    assert T.slope_reading("45°", roof=True) is None and T.slope_reading("90°", roof=True) is None
    assert T.slope_reading("EĞİM 45°", roof=True)["deg"] == 45.0          # a slope word says it is a pitch
    # monotonic: a larger bare number is never a flatter roof
    vals = [T.slope_pct(f"EĞİM {v}") for v in (5, 7, 9.5, 9.99, 10, 12, 30, 60)]
    assert vals == sorted(vals)


def test_r07f_a_bare_angle_votes_only_inside_the_eaves_loop_and_never_on_a_dimension_layer():
    """Fix-up (SECTIONS-7): two '45°' angles at the corners of a roof plan (or any bare angle on a dimension layer) never
    outvote its two '%30' slope texts."""
    from wenart.sheets import exterior as EX
    from wenart.sheets import titles as T

    def plan(texts, layer=None):
        ents = [_line("h1", (0, 0), (4, 4)), _line("h2", (20, 0), (16, 4)), _line("h3", (0, 12), (4, 8)),
                _line("h4", (20, 12), (16, 8))]
        txts = []
        for k, (t, x, y) in enumerate(texts):
            tx = _txt(f"s{k}", t, x, y)
            if layer and "°" in t:
                tx.layer = layer
            txts.append(tx)
        return Region(id="r4", file="x.dxf", sheet=_sheet(), box=(0, -1, 20, 12), geometry_box=(0, -1, 20, 12),
                      ents=ents, texts=txts, metres_per_unit=1.0, features={"hip_lines": 4}, cls="roof_plan",
                      use="exterior")
    corners = [("45°", 0.5, 0.5), ("45°", 19.5, 11.5)]
    hip = EX.roof_from_roof_plan([plan([("%30 EĞİM", 3, 6), ("%30 EĞİM", 17, 6)] + corners)])
    assert hip is not None and hip["slope_pct"] == 30.0
    # a bare 35 degree angle on a dimension layer: listed, not counted
    dims = [("35°", 0.5, 0.5), ("35°", 19.5, 11.5), ("35°", 10, 6)]
    hip2 = EX.roof_from_roof_plan([plan([("%30 EĞİM", 3, 6), ("%30 EĞİM", 17, 6)] + dims, layer="OLCU")])
    assert hip2 is not None and hip2["slope_pct"] == 30.0 and "dimension layer" in hip2["note"]
    assert T.slope_reading("35°", roof=True)["form"] == "bare angle"


def _section(marks):
    from wenart.sheets.heights import SectionGeometry
    reg = SimpleNamespace(id="r5", file="x.dxf")
    g = SectionGeometry(region=reg, mpu=1.0, walls=(0.0, 10.0), wall_ids=("wl", "wr"), wall_inner=(0.2, 9.8),
                        bands=[(-0.2, 0.0, "b0", "b0t"), (2.8, 3.0, "b1", "b1t")],
                        profile=[(-0.5, 5.70), (5.0, 7.30), (10.5, 5.70)], profile_ids=["p1", "p2"])
    for k, (txt, val, y) in enumerate(marks):
        g.marks.append((SimpleNamespace(id=f"m{k}", text=txt), val, (11.0, y), "line",
                        {"value": val, "relative": True, "absolute": None}))
    return g


def test_r07d_eaves_and_ridge_snap_to_the_sections_own_printed_marks():
    from wenart.sheets import heights as HT
    levels = [{"id": "L0", "order": 0, "kind": "floor"}, {"id": "L1", "order": 1, "kind": "floor"}]
    g = _section([("±0.00", 0.0, 0.0), ("+5.80", 5.80, 5.75), ("+7.50", 7.50, 7.45)])
    out, _w = HT.heights(g, levels, None, {}, "x.dxf", lambda *a, **k: "c1", None)
    assert out["roof"]["eaves_z"]["value"] == pytest.approx(5.80) and "snapped" in out["roof"]["eaves_z"]["note"]
    assert out["roof"]["ridge_z"]["value"] == pytest.approx(7.30)        # +7.50 is 0.20 m off: not snapped
    g2 = _section([("±0.00", 0.0, 0.0), ("+7.40", 7.40, 7.35)])
    out2, _w = HT.heights(g2, levels, None, {}, "x.dxf", lambda *a, **k: "c1", None)
    assert out2["roof"]["ridge_z"]["value"] == pytest.approx(7.40)


def _roof_building(top_ceiling=2.7, top_kind="floor"):
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7, "kind": "floor"},
                    {"id": "L1", "elevation": 3.0, "ceiling_height": top_ceiling, "kind": top_kind}],
         "walls": _walls("L0", 0, 0, 20, 10) + _walls("L1", 0, 0, 20, 10), "openings": [], "rooms": [],
         "furniture": []}
    return b


def _roof(eaves, ridge, pct):
    ev = [{"rule": "roof_slope_text", "region_id": "r4"}]
    return {"type": "gable", "over_level_id": "L1", "outline": _rect(-0.5, -0.5, 20.5, 10.5),
            "eaves_height": {"value": eaves, "method": "vector", "evidence": [{"region_id": "r5"}]},
            "ridge_height": {"value": ridge, "method": "vector", "evidence": [{"region_id": "r4"}]},
            "pitches_deg": [{"value": math.degrees(math.atan(pct / 100.0)), "method": "derived", "evidence": ev}],
            "ridge_lines": [[[-0.5, 5.0], [20.5, 5.0]]]}


def _roof_drawn(eaves, ridge, pct, profile=None, plan_ridge=False, outline=None):
    """``_roof`` with the section's own profile (cut across the ridge), the ridge height from the roof plan's mark, or
    another outline."""
    r = _roof(eaves, ridge, pct)
    if profile:
        r["profile"] = {"region_id": "r5", "cut_axis": "y", "points": profile, "method": "vector"}
    if plan_ridge:
        r["ridge_height"]["evidence"] = [{"rule": "roof_plan_mark", "region_id": "r4"}]
    if outline:
        r["outline"] = outline
    return r


L_OUTLINE = [[-0.5, -0.5], [20.5, -0.5], [20.5, 10.5], [10, 10.5], [10, 4], [-0.5, 4]]


def test_r07g_drawn_heights_win_when_their_pitch_is_plausible():
    from wenart.blender import roof as RF
    b = _roof_building()
    d = RF.derive(_roof(5.8, 7.8, 60.0), b)          # drawn 20.8 deg, written 31 deg: the drawn heights win
    assert d["eaves_z"] == pytest.approx(5.8) and d["ridge_z"] == pytest.approx(7.8, abs=0.01)
    assert any("drawn heights win" in w for w in d["warnings"])
    # fix-up (SECTIONS-2): an L outline (it does not fill its rectangle) and no drawn profile: the span is unknown, the
    # written pitch is not judged (no conflict, a note)
    dl = RF.derive(_roof_drawn(5.8, 7.8, 60.0, outline=L_OUTLINE), b)
    assert not any("R07 g" in w for w in dl["warnings"]) and any("not judged" in n for n in dl["notes"])
    assert dl["pitches"][0] == pytest.approx(30.96, abs=0.01)
    # ... with the section's profile its own run is the span (5.5 m: 20 degrees, the drawn heights win)
    dp = RF.derive(_roof_drawn(5.8, 7.8, 60.0, profile=[[0, 5.8], [5.5, 7.8], [11, 5.8]], outline=L_OUTLINE), b)
    assert any("give 20.0 degrees: the drawn heights win" in w for w in dp["warnings"])


def test_r07g_drawn_rafters_that_agree_with_the_text_say_one_roof_over_several():
    """Fix-up (SECTIONS-2, real06): the section's own rafters draw the written pitch: the one roof's span is the wrong
    reading (several drawn roofs), the written pitch and the drawn eaves stay, listed."""
    from wenart.blender import roof as RF
    b = _roof_building()
    prof = [[0, 5.0], [3.0, 6.0], [4.0, 7.55], [5.5, 7.55], [11, 5.0]]      # a rafter of 18.4 degrees from the eaves
    d = RF.derive(_roof_drawn(5.0, 7.55, 33.0, profile=prof), b)
    assert d["pitches"][0] == pytest.approx(18.26, abs=0.01) and d["eaves_z"] == pytest.approx(5.0)
    assert any("one roof over several drawn roofs (multi-part roofs not built)" in w and "rafters draw 18.4" in w
               for w in d["warnings"])
    assert not any(w.startswith("conflict") for w in d["warnings"])


def test_r07g_a_ridge_mark_that_cannot_stand_with_the_full_storeys_eaves_is_the_wrong_reading():
    from wenart.blender import roof as RF
    b = _roof_building()
    d = RF.derive(_roof(5.8, 6.4, 30.0), b)          # drawn 5.9 deg (< 10 for tiles); 30 % with the ridge: eaves 4.7
    assert d["eaves_z"] == pytest.approx(5.8)
    assert d["pitches"][0] == pytest.approx(16.7, abs=0.1) and d["ridge_z"] > 6.4 + 0.5
    assert any("wrong reading" in w for w in d["warnings"])
    # fix-up (SECTIONS-1, real15): the roof plan's ridge mark and the section's ridge agree: the ridge is right, the one
    # roof's span is the wrong reading: the drawn eaves and ridge are kept, listed, never a conflict on the ridge
    prof = [[0, 5.8], [5.5, 6.4], [11, 5.8]]
    d2 = RF.derive(_roof_drawn(5.8, 6.4, 30.0, profile=prof, plan_ridge=True), b)
    assert d2["eaves_z"] == pytest.approx(5.8) and d2["ridge_z"] == pytest.approx(6.4, abs=0.01)
    assert any("one roof over several drawn roofs" in w and "agree" in w for w in d2["warnings"])
    assert not any("wrong reading (another roof part" in w for w in d2["warnings"])
    assert any(a.get("value") == "multi_part_roof" for a in d2["assumed"])


def test_r07g_the_written_pitch_wins_with_the_drawn_ridge_when_the_eaves_may_come_down():
    from wenart.blender import roof as RF
    b = _roof_building(top_kind="attic")
    d = RF.derive(_roof(4.2, 4.7, 30.0), b)          # an attic: the eaves may stand low
    assert d["ridge_z"] == pytest.approx(4.7, abs=0.02) and d["pitches"][0] == pytest.approx(16.7, abs=0.1)
    assert d["eaves_z"] < 4.2 and any("written pitch wins" in w for w in d["warnings"])


# --------------------------------------------------------------------------------------------------------------------
# steps at a door between floors of different height
# --------------------------------------------------------------------------------------------------------------------

def _two_rooms(rise: float, low_type="garage", width=0.8, low_depth=4.0):
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
         "rooms": [_room("r_low", "L0", _rect(0, 0, 4, low_depth), low_type),
                   _room("r_high", "L0", _rect(0, low_depth + 0.2, 4, low_depth + 4.2), "hall")],
         "walls": [{"id": "w_mid", "level_id": "L0", "start": [0, low_depth + 0.1], "end": [4, low_depth + 0.1],
                    "thickness": 0.2}],
         "openings": [{"id": "d_1", "level_id": "L0", "type": "door", "wall_id": "w_mid", "width": width,
                       "center": [2.0, low_depth + 0.1]}]}
    b["rooms"][0]["floor_offset_m"] = -rise
    steps = [{"opening_id": "d_1", "rise": rise, "low_room": "r_low", "risers": 2, "riser": rise / 2}]
    return b, steps


def _outward_faces(verts, faces) -> list:
    """For each face of a closed convex mesh: does its winding (Newell normal) point away from the mesh's centre?"""
    cx = sum(v[0] for v in verts) / len(verts)
    cy = sum(v[1] for v in verts) / len(verts)
    cz = sum(v[2] for v in verts) / len(verts)
    out = []
    for f in faces:
        n = [0.0, 0.0, 0.0]
        for i in range(len(f)):
            a, c = verts[f[i]], verts[f[(i + 1) % len(f)]]
            n[0] += (a[1] - c[1]) * (a[2] + c[2])
            n[1] += (a[2] - c[2]) * (a[0] + c[0])
            n[2] += (a[0] - c[0]) * (a[1] + c[1])
        fc = [sum(verts[k][j] for k in f) / len(f) for j in range(3)]
        out.append(n[0] * (fc[0] - cx) + n[1] * (fc[1] - cy) + n[2] * (fc[2] - cz) > 0)
    return out


def test_steps_are_built_in_the_lower_room_and_a_garage_vehicle_door_gets_a_ramp():
    from shapely.geometry import Polygon
    from wenart.blender import shell as SH
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    b, steps = _two_rooms(0.35)
    res = DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
    o = b["openings"][0]
    st = o["steps"]
    assert res["built"] and st["kind"] == "steps" and st["risers"] == 2 and st["room_id"] == "r_low"
    assert "blocks" not in st and st["side"] == -1.0 and st["wall_id"] == "w_mid"      # relative to the door
    blocks = DS.plan_blocks(o)
    assert len(blocks) == 1 and blocks[0]["z1"] == pytest.approx(-0.175) and blocks[0]["z0"] == pytest.approx(-0.35)
    assert all(q[1] <= 4.0 + 1e-6 for q in blocks[0]["polygon"])                # in front of the door, low side
    assert Polygon(blocks[0]["polygon"]).area == pytest.approx(0.8 * st["tread"], abs=1e-6)
    verts, faces = SH.door_step_blocks(o)
    assert len(verts) == 8 and len(faces) >= 6 and all(_outward_faces(verts, faces))
    # a garage's vehicle door: a ramp 0.25 / 0.12 m long, inside the garage, its faces wound outwards (STEPS-5) with
    # the garage on either side of the wall
    for low_depth, flip in ((6.0, False), (6.0, True)):
        b2, steps2 = _two_rooms(0.25, width=2.4, low_depth=low_depth)
        if flip:                                       # the wall drawn the other way round
            w = b2["walls"][0]
            w["start"], w["end"] = w["end"], w["start"]
        DS.place(b2, steps2, dict(RU.BUILTIN_PARAMS))
        o2 = b2["openings"][0]
        assert o2["steps"]["kind"] == "ramp" and o2["steps"]["run"] == pytest.approx(0.25 / 0.12, abs=1e-3)
        ramp = DS.plan_blocks(o2)
        assert len(ramp) == 1 and all(q[1] <= low_depth + 1e-6 for q in ramp[0]["polygon"])
        v2, f2 = SH.door_step_blocks(o2)
        assert v2 and all(_outward_faces(v2, f2)), flip
    # STEPS-6: one garage predicate (levels.model.is_garage_door): a 2.1 m garage door lets no car pass: steps
    from wenart.ingest.twins import GARAGE_DOOR_MIN_M
    b3, steps3 = _two_rooms(0.25, width=GARAGE_DOOR_MIN_M - 0.1, low_depth=6.0)
    DS.place(b3, steps3, dict(RU.BUILTIN_PARAMS))
    assert b3["openings"][0]["steps"]["kind"] == "steps"


def test_steps_follow_their_door_and_never_outlive_a_reinference():
    """Fix-up (STEPS-1, STEPS-2, GENERAL-4): the plan is relative to the door: a door moved along its wall carries its
    steps; a door moved to another wall loses them; a re-inference where the floors became flush leaves none behind."""
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    b, steps = _two_rooms(0.35)
    DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
    o = b["openings"][0]
    xs = [q[0] for q in DS.plan_blocks(o)[0]["polygon"]]
    assert min(xs) == pytest.approx(1.6) and max(xs) == pytest.approx(2.4)
    o["center"] = [3.0, 4.1]                            # a later stage moves the door 1 m along its wall
    xs2 = [q[0] for q in DS.plan_blocks(o)[0]["polygon"]]
    assert min(xs2) == pytest.approx(2.6) and max(xs2) == pytest.approx(3.4)
    o["wall_id"] = "w_other"                            # ... or onto another wall: no blocks there
    assert DS.plan_blocks(o) == []
    o["wall_id"] = "w_mid"
    DS.place(b, [], dict(RU.BUILTIN_PARAMS))           # the floors flush now: no inner step record
    assert "steps" not in b["openings"][0]


def test_a_rerun_of_infer_levels_plans_the_steps_again_and_leaves_none_behind():
    """Integration (GENERAL-4): the level model plans a door's steps (the hall 0.35 m lower); a second run where the
    floors are flush (the hall's mark gone) leaves no step plan on any opening."""
    from tests import _levels_fixture  # noqa: F401 - the fixture module the helper below imports
    from tests.test_audit_round2_20261126 import _two_storeys
    from wenart.levels import model as M
    b = M.infer_levels(_two_storeys([("r_living", 0.5), ("r_bed", 0.5), ("r_hall", 0.15)],
                                    [("r_living", 3.5), ("r_bed", 3.5), ("r_hall", 3.5)]))
    assert [(o["id"], o["steps"]["room_id"]) for o in b["openings"] if o.get("steps")] == [("d_inner", "r_hall")]
    b["level_marks"] = [m for m in b["level_marks"] if m.get("room_id") != "r_hall"]
    b = M.infer_levels(b)
    assert b["level_inference"]["inner_steps"] == [] and not any(o.get("steps") for o in b["openings"])


def test_steps_that_do_not_fit_are_a_finding_not_a_build():
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    b, steps = _two_rooms(0.90, low_type="hall", low_depth=0.6)
    res = DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
    assert res["unbuilt"] and b["openings"][0].get("steps") is None and steps[0]["placed"] is None
    assert "does not fit" in steps[0]["reason"]


def _corridor_case(with_wc=True, with_stair=True, width=1.0):
    """A corridor ``width`` wide (floor -0.50) under a room door on its north wall; a WC door on its south wall opposite,
    a stair at its west end."""
    b = {"levels": [{"id": "L0", "elevation": 0.0}],
         "rooms": [dict(_room("r_cor", "L0", _rect(0, 0, 6, width), "hall"), floor_offset_m=-0.5),
                   _room("r_room", "L0", _rect(0, width + 0.2, 6, 5), "living")],
         "walls": [{"id": "w_n", "level_id": "L0", "start": [0, width + 0.1], "end": [6, width + 0.1], "thickness": 0.2},
                   {"id": "w_s", "level_id": "L0", "start": [0, -0.1], "end": [6, -0.1], "thickness": 0.2}],
         "openings": [{"id": "d_room", "level_id": "L0", "type": "door", "wall_id": "w_n", "width": 0.9,
                       "center": [1.2, width + 0.1]}],
         "furniture": []}
    if with_wc:
        b["openings"].append({"id": "d_wc", "level_id": "L0", "type": "door", "wall_id": "w_s", "width": 0.8,
                              "center": [1.2, -0.1]})
    if with_stair:
        b["furniture"].append({"id": "f_stair", "level_id": "L0", "type": "stair",
                               "footprint": {"center": [1.2, width / 2], "size": [0.9, 0.5], "rotation_deg": 0}})
    return b


def test_steps_never_block_another_door_a_stair_or_the_walkway():
    """Fix-up (STEPS-3): the flight is an obstacle check: on another door's approach, on a stair, or leaving less than a
    walkway beside it, it is not built (a finding naming what it would block)."""
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    for kw, word in (({"with_stair": False}, "approach of d_wc"), ({"with_wc": False}, "the stair f_stair")):
        b = _corridor_case(**kw)
        steps = [{"opening_id": "d_room", "rise": 0.5, "low_room": "r_cor"}]
        res = DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
        assert res["unbuilt"] and not res["built"] and word in steps[0]["reason"], kw
        assert "steps" not in b["openings"][0]
    # nothing in the way in a wide hall: built
    b = _corridor_case(with_wc=False, with_stair=False, width=3.0)
    steps = [{"opening_id": "d_room", "rise": 0.5, "low_room": "r_cor"}]
    assert DS.place(b, steps, dict(RU.BUILTIN_PARAMS))["built"]


def test_drawn_short_steps_at_the_door_are_its_steps_and_outdoor_steps_use_outdoor_risers():
    """Fix-up (STEPS-4, STEPS-6): a short run of steps the plan draws at the door is its steps (no inferred blocks);
    a storey's stair beside the door is not; a lower outdoor room (a balcony) takes the outdoor riser."""
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    b, steps = _two_rooms(0.34, low_type="living")
    b["furniture"] = [{"id": "f_L0_steps", "level_id": "L0", "type": "stair", "stair": {"short_steps": 2},
                       "footprint": {"center": [2.0, 3.7], "size": [1.2, 0.6], "rotation_deg": 0.0}}]
    res = DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
    st = b["openings"][0]["steps"]
    assert res["built"] and st["source"] == "drawn" and st["piece"] == "f_L0_steps" and DS.plan_blocks(b["openings"][0]) == []
    assert steps[0]["kind"] == "drawn"
    # a storey's stair (17 steps) by the door is no door step: the steps are inferred (they do not overlap it)
    b3, steps3 = _two_rooms(0.34, low_type="living")
    b3["furniture"] = [{"id": "f_L0_st", "level_id": "L0", "type": "stair",
                        "stair": {"flights": [{"start": [0.5, 0.5], "end": [0.5, 3.5], "width": 0.9, "lines": 17}]},
                        "footprint": {"center": [0.5, 2.0], "size": [0.9, 3.0], "rotation_deg": 0.0}}]
    DS.place(b3, steps3, dict(RU.BUILTIN_PARAMS))
    assert b3["openings"][0]["steps"]["source"] == "inferred"
    params = dict(RU.BUILTIN_PARAMS)
    b4, steps4 = _two_rooms(0.36, low_type="balcony")
    DS.place(b4, steps4, params)
    b5, steps5 = _two_rooms(0.36, low_type="living")
    DS.place(b5, steps5, params)
    r_out, r_in = b4["openings"][0]["steps"]["riser"], b5["openings"][0]["steps"]["riser"]
    assert r_out <= float(params["riser_max_outdoor"]) + 1e-9 and r_in <= float(params["riser_max_indoor"]) + 1e-9
    assert (b4["openings"][0]["steps"]["risers"], b5["openings"][0]["steps"]["risers"]) == (3, 2)


# --------------------------------------------------------------------------------------------------------------------
# an upper outdoor space past the walls under it
# --------------------------------------------------------------------------------------------------------------------

def _upper_case(roof=True):
    """Two storeys: L0 10 x 10 m, L1 10 x 6 m (y 0-6); the levels by id, their outlines (outer faces)."""
    b = {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}],
         "walls": _walls("L0", 0, 0, 10, 10) + _walls("L1", 0, 0, 10, 6), "furniture": [], "rooms": [],
         "roof": {"type": "hip", "outline": _rect(-0.5, -0.5, 10.5, 10.5)} if roof else None, "site": {}}
    levels = {lv["id"]: lv for lv in b["levels"]}
    outlines = {"L0": _rect(-0.1, -0.1, 10.1, 10.1), "L1": _rect(-0.1, -0.1, 10.1, 6.1)}
    return b, levels, outlines


def test_upper_reach_one_rule_one_reference_one_threshold_and_a_round_join():
    """Fix-up (UPS-1/-3, GENERAL-1/-2/-8/-9; round 5b's upper support folded into R16's ``outdoor_checks``): an upper
    space is judged against the storey directly under it; an inferred rectangle is cut to 2.0 m beyond its walls with a
    round join (no corner 2.83 m out; a second check finds nothing to do); a written area never exempts it."""
    from shapely.geometry import Point, Polygon
    from wenart.ingest import outdoor_checks as OC
    b, levels, outlines = _upper_case(roof=False)
    area = {"id": "sa_L1_teras", "label": "TERAS", "anchor": [-1.0, 8.0]}
    rect = _rect(-4, 6.1, 10, 12)
    up = OC.upper_reach(b, area, "L1", levels, "L0", "rectangle in the inner corner", rect, outlines, [])
    assert up["action"] == "clipped" and up["below"] == "L0" and up["reach_m"] == pytest.approx(4.34, abs=0.01)
    under = Polygon(outlines["L0"])
    assert max(under.distance(Point(q)) for q in up["polygon"]) <= OC.UPPER_REACH_M + 0.01
    again = OC.upper_reach(b, area, "L1", levels, "L0", "rectangle in the inner corner", up["polygon"], outlines, [])
    assert again["action"] is None                              # the same geometry for the trigger and the clip
    # 5a's helper gives the same geometry (one geometry)
    poly2, why2 = OC.clip_upper(rect, "L1", levels, outlines, "L0")
    assert why2 and Polygon(poly2).symmetric_difference(Polygon(up["polygon"])).area < 0.01
    # the stated area sized the rectangle: still cut (it confirms the size, it never exempts)
    area_w = dict(area, label_raw="TERAS A:82.60m²")
    assert OC.upper_reach(b, area_w, "L1", levels, "L0", "rectangle against the facade (scaled to the stated area)",
                          rect, outlines, [])["action"] == "clipped"


def test_upper_reach_never_judges_a_ground_floor_space_and_keeps_what_is_drawn_supported_or_labelled():
    """Fix-up (GENERAL-1, GENERAL-2, 5a's R16 contract): a ground-floor terrace over a basement stands on the ground; a
    drawn outline is kept and listed; walls or columns under the part make it supported; a labelled rectangle with no
    part within the reach is kept as read (listed); only a purely inferred space is refused."""
    from wenart.ingest import outdoor_checks as OC
    b, levels, outlines = _upper_case(roof=False)
    levels["L-1"] = {"id": "L-1", "elevation": -3.0}
    outlines["L-1"] = _rect(-0.1, -0.1, 10.1, 6.1)
    far = _rect(-6, 0, -0.1, 10)
    area = {"id": "sa_L0_teras", "label": "TERAS", "anchor": [-3.0, 5.0]}
    assert OC.upper_reach(b, area, "L0", levels, "L0", "rectangle against the facade", far, outlines,
                          [])["action"] is None
    up_area = {"id": "sa_L1_teras", "label": "TERAS", "anchor": [-1.0, 8.0]}
    rect = _rect(-4, 6.1, 10, 12)
    kept = OC.upper_reach(b, up_area, "L1", levels, "L0", "strokes", rect, outlines, [])
    assert kept["action"] == "kept" and kept["polygon"] == rect and "needs supports" in kept["reason"]
    b["furniture"] = [{"id": "f_col", "level_id": "L0", "type": "column",
                       "footprint": {"center": [-3.0, 11.0], "size": [0.3, 0.3], "rotation_deg": 0}}]
    assert OC.upper_reach(b, up_area, "L1", levels, "L0", "rectangle", rect, outlines, [])["action"] == "supported"
    b["furniture"] = []
    off = _rect(-12, 4, -8, 8)                                      # nothing of it within 2 m of L0
    assert OC.upper_reach(b, up_area, "L1", levels, "L0", "rectangle", off, outlines, [])["action"] == "kept"
    assert OC.upper_reach(b, dict(up_area, label=""), "L1", levels, "L0", "rectangle", off, outlines,
                          [])["action"] == "refused"
    assert OC.upper_reach(b, dict(up_area, label=""), "L1", levels, "L0", "rectangle", off, outlines,
                          ["d_L1_1"])["action"] == "kept"
    # the drawn roof over its part above L0 is named in the finding
    b2, levels2, outlines2 = _upper_case(roof=True)
    named = OC.upper_reach(b2, up_area, "L1", levels2, "L0", "rectangle", rect, outlines2, [])
    assert named["action"] == "clipped" and "the drawn roof covers" in named["reason"]


def _upper_building(label_raw="TERAS"):
    from tests import _levels_fixture  # noqa: F401 - the fixture module the helper below imports
    from tests.test_audit_round2_20261126 import _two_storeys
    b = _two_storeys([("r_living", 0.0), ("r_bed", 0.0), ("r_hall", 0.0)])
    b["site"] = dict(b.get("site") or {}, areas=[{"id": "sa_L1_teras", "level_id": "L1", "label": "TERAS",
                                                   "label_raw": label_raw, "anchor": [-3.5, 4.0], "build": False,
                                                   "evidence": [{"file": "x.dxf", "method": "vector",
                                                                 "text": label_raw}]}])
    return b


def test_upper_reach_runs_inside_the_levels_model_and_survives_a_rerun():
    """Fix-up (UPS-1, UPS-2): the one rule runs inside ``infer_levels`` before the space's floor, roof and posts: the
    space, its site area, the inferred entry and the report agree; a second run gives the same verdict and polygon;
    no separate ``level_inference.upper_support`` record is left."""
    from shapely.geometry import Polygon
    from wenart.levels import model as M
    from wenart.report import final as RF
    b = M.infer_levels(_upper_building())
    os_ = b["site"]["outdoor_spaces"]
    assert [s["id"] for s in os_] == ["os_L1_teras"] and os_[0]["upper_support"]["action"] == "clipped"
    first = Polygon(os_[0]["polygon"])
    assert first.bounds[0] == pytest.approx(-2.1, abs=0.01) and os_[0]["area_m2"] == pytest.approx(first.area, abs=0.01)
    area = b["site"]["areas"][0]
    assert area["space"] == {"built": True, "id": "os_L1_teras"}
    inf = [i for i in b["level_inference"]["inferred"] if i["item"] == "outdoor space os_L1_teras"]
    assert len(inf) == 1 and Polygon(inf[0]["value"]).equals_exact(first, 1e-6)
    assert "upper_support" not in b["level_inference"]
    summ = RF.site_summary(b)
    assert next(x for x in summ["areas"] if x["id"] == "sa_L1_teras")["space"] == "os_L1_teras"
    b = M.infer_levels(b)
    again = b["site"]["outdoor_spaces"]
    assert len(again) == 1 and Polygon(again[0]["polygon"]).equals_exact(first, 1e-6)
    assert again[0]["upper_support"]["action"] == "clipped"


def test_r16_records_survive_a_rerun_of_the_levels_model():
    """Fix-up (OPENINGS2-8): the first run refuses an upper 'TERAS' whose own mark is the floor below (seen from above);
    an agent edit adds a door onto it and the second run builds it, its refusal gone; the 'no door reaches it' finding of
    a drawn balcony is written again by every run (it lived only in the completion)."""
    import copy as _copy
    from tests import _levels_fixture as F
    from tests.test_audit_round2_20261126 import _two_storeys
    from wenart.levels import model as M
    b = _two_storeys([("r_living", 0.0), ("r_bed", 0.0), ("r_hall", 0.0)])
    b["level_marks"].append(F.mark("lm_t", 0.0, point=(-1.6, 4.3), level="L1", raw="+0.00"))
    b["site"] = dict(b.get("site") or {}, areas=[
        {"id": "sa_L1_teras", "level_id": "L1", "label": "TERAS", "label_raw": "TERAS", "anchor": [-1.5, 4.0],
         "build": False, "evidence": [{"file": "t.dxf", "method": "vector", "text": "TERAS"}]},
        {"id": "sa_L1_balkon", "level_id": "L1", "label": "BALKON", "label_raw": "BALKON", "anchor": [10.8, 3.5],
         "polygon": [[10.1, 2.0], [11.5, 2.0], [11.5, 5.0], [10.1, 5.0]], "build": False,
         "evidence": [{"file": "t.dxf", "method": "vector", "text": "BALKON"}]}])
    b1 = M.infer_levels(b)
    s1 = b1["site"]
    assert [r["area_id"] for r in s1["outdoor_spaces_refused"]] == ["sa_L1_teras"]
    assert s1["areas"][0]["space"]["built"] is False and s1["areas"][0]["space"]["finding"] == "R16"
    balk = next(o for o in s1["outdoor_spaces"] if o["id"] == "os_L1_balkon")
    assert balk["finding"]["unreached"] and "no door or opening of L1 reaches it" in balk["finding"]["reason"]
    assert [r["space"] for r in b1["level_inference"]["outdoor_spaces_unreached"]] == ["os_L1_balkon"]
    b2 = _copy.deepcopy(b1)
    b2["openings"].append({"id": "d_L1_teras", "level_id": "L1", "type": "door", "wall_id": "w_4_up", "width": 0.9,
                           "height": 2.1, "center": [0.0, 4.0], "status": "verified", "evidence": [dict(F.EV)]})
    b2 = M.infer_levels(b2)
    s2 = b2["site"]
    assert "os_L1_teras" in [o["id"] for o in s2["outdoor_spaces"]] and not s2.get("outdoor_spaces_refused")
    assert s2["areas"][0]["space"] == {"built": True, "id": "os_L1_teras"}
    balk2 = next(o for o in s2["outdoor_spaces"] if o["id"] == "os_L1_balkon")
    assert balk2["finding"]["unreached"] and "base" not in balk2["finding"]           # written once, not nested
    assert [r["space"] for r in b2["level_inference"]["outdoor_spaces_unreached"]] == ["os_L1_balkon"]
    # a door onto the balcony: its finding goes (the space keeps no stale finding)
    b3 = _copy.deepcopy(b2)
    b3["openings"].append({"id": "d_L1_balkon", "level_id": "L1", "type": "door", "wall_id": "w_2_up", "width": 0.9,
                           "height": 2.1, "center": [10.0, 3.5], "status": "verified", "evidence": [dict(F.EV)]})
    b3 = M.infer_levels(b3)
    assert not next(o for o in b3["site"]["outdoor_spaces"] if o["id"] == "os_L1_balkon").get("finding")
    assert "outdoor_spaces_unreached" not in b3["level_inference"]


def test_a_refused_upper_space_follows_the_refused_contract_and_argus_agrees():
    """Fix-up (GENERAL-3): a refusal moves the space to ``site.outdoor_spaces_refused`` with its rule and reason, sets
    the site area's ``space`` (built False, its reason and finding) and leaves no inferred entry; Argus reports the
    rule's verdict (never 'build the outdoor space') and the report names the reason."""
    from wenart.audit import conservation as CV
    from wenart.ingest import outdoor_checks as OC
    from wenart.report import final as RF
    b = {"site": {"areas": [{"id": "sa_L1_x", "level_id": "L1", "label": "TERAS", "build": False,
                             "space": {"built": False, "reason": "no part within reach", "finding": "R16"},
                             "evidence": [{"method": "vector", "entity": "TEXT:1"}]}],
                  "outdoor_spaces": []}}
    OC.record_refusal(b, b["site"]["areas"][0], "L1", _rect(0, 0, 2, 2), "rectangle", "no part within reach")
    assert b["site"]["outdoor_spaces_refused"][0]["refused"] == {"rule": OC.RULE, "reason": "no part within reach"}
    f = [x for x in CV.untyped(b) if x["check"] == "C5"]
    assert len(f) == 1 and f[0]["severity"] == "major" and f[0]["fix"] is None and "no part within reach" in \
        f[0]["message"]
    summ = RF.site_summary(dict(b, site=dict(b["site"], boundary_walls=[], decor=[], openings=[])))
    row = next(x for x in summ["areas"] if x["id"] == "sa_L1_x")
    assert row["not_built_reason"] == "no part within reach" and row["rule"] == "R16"


# --------------------------------------------------------------------------------------------------------------------
# R23: a roof-terrace level takes its slab and parapets from its own drawn edge ring
# --------------------------------------------------------------------------------------------------------------------

def _terrace_region():
    """A roof-terrace plan: an edge ring on layer '0.3' (12 x 10 m with a 1.0 x 0.6 m slot on the north edge and a
    2 x 2 m recess on the south edge), its inner face 0.15 m inside, and a stair house box on layer '0'."""
    ring = [(0, 0), (5, 0), (5, 2), (7, 2), (7, 0), (12, 0), (12, 10), (6.5, 10), (6.5, 9.4), (5.5, 9.4), (5.5, 10),
            (0, 10)]
    ents = [_line(f"e{k}", a, b, "0.3") for k, (a, b) in enumerate(zip(ring, ring[1:] + ring[:1]))]
    house = [(4, 4), (8, 4), (8, 7), (4, 7)]
    ents += [_line(f"h{k}", a, b, "0") for k, (a, b) in enumerate(zip(house, house[1:] + house[:1]))]
    return Region(id="r9", file="x.dxf", sheet=_sheet(), box=(-1, -1, 13, 11), geometry_box=(-1, -1, 13, 11),
                  ents=ents, texts=[], metres_per_unit=1.0, transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])


def test_r23_the_terrace_slab_and_parapets_follow_the_drawn_ring():
    from shapely.geometry import Polygon
    from wenart.sheets import terrace_ring as TRG
    from wenart.sheets import to_building as TB
    cands = TRG.rings(_terrace_region())
    assert cands and cands[0]["layer"] == "0.3"
    b = {"levels": [{"id": "L6", "order": 6, "elevation": 18.0, "ceiling_height": 2.7},
                    {"id": "L7", "order": 7, "elevation": 21.0, "ceiling_height": 3.0, "roof_terrace": True,
                     "region_id": "r9", "evidence": [{"file": "x.dxf"}]}],
         # the floor below: 12 x 10 m with a 2 x 3 m light well notch on the north edge
         "walls": [w for w in _walls("L6", 0, 0, 12, 10)],
         "rooms": [_room("r_L7_stair", "L7", _rect(4, 4, 8, 7), "stair")],
         "slabs": [{"id": "sl_L7", "above_level_id": "L7", "below_level_id": "L6", "outline": [
             [0, 0], [12, 0], [12, 10], [7, 10], [7, 7.5], [5, 7.5], [5, 10], [0, 10]], "openings": [], "variants": []}],
         "openings": [], "furniture": []}
    sheets = {"levels": [{"id": "L7", "edge_rings": cands}], "regions": []}
    warns = []
    ring = TB.drawn_ring(b, sheets, b["levels"][1], [Polygon(_rect(4, 4, 8, 7))], warns.append)
    assert ring is not None and ring["layer"] == "0.3"
    slab = Polygon(b["slabs"][0]["outline"])
    assert slab.area == pytest.approx(120.0 - 4.0 - 0.6, abs=0.05)          # the light well covered, slot and recess open
    assert b["slabs"][0]["outline_source"] == "roof_terrace_ring"
    n = TB._edge_parapets(b, b["levels"][1], 1.1, "assumed", ring=ring)
    pars = [w for w in b["walls"] if w.get("parapet")]
    assert n == len(pars) > 0 and all(w["rule"] == "roof_terrace_ring" for w in pars)
    assert any(abs(w["start"][1] - 2.0) < 0.15 or abs(w["end"][1] - 2.0) < 0.15 for w in pars)  # round the recess


def _terrace_building(rooms_below=()):
    return {"levels": [{"id": "L6", "order": 6, "elevation": 18.0, "ceiling_height": 2.7},
                       {"id": "L7", "order": 7, "elevation": 21.0, "ceiling_height": 3.0, "roof_terrace": True,
                        "region_id": "r9", "evidence": [{"file": "x.dxf"}]}],
            "walls": [w for w in _walls("L6", 0, 0, 12, 10)],
            "rooms": [_room("r_L7_stair", "L7", _rect(4, 4, 8, 7), "stair")] + list(rooms_below),
            "slabs": [{"id": "sl_L7", "above_level_id": "L7", "below_level_id": "L6", "outline": [
                [0, 0], [12, 0], [12, 10], [7, 10], [7, 7.5], [5, 7.5], [5, 10], [0, 10]], "openings": [],
                "variants": []}],
            "openings": [], "furniture": []}


def test_r23_a_ring_never_leaves_a_closed_room_below_open_to_the_sky():
    """Fix-up (RING-1): the ring's south recess stands over a bedroom of the floor below: the floor below's outline stays
    there (a finding naming the room); over a light well the recess stays open."""
    from shapely.geometry import Polygon
    from wenart.sheets import terrace_ring as TRG
    from wenart.sheets import to_building as TB
    cands = TRG.rings(_terrace_region())
    b = _terrace_building([_room("r_L6_bed", "L6", _rect(4, 0, 8, 3), "bedroom", "YATAK ODASI")])
    warns = []
    ring = TB.drawn_ring(b, {"levels": [{"id": "L7", "edge_rings": cands}], "regions": []}, b["levels"][1],
                         [Polygon(_rect(4, 4, 8, 7))], warns.append)
    slab = Polygon(b["slabs"][0]["outline"])
    assert slab.area == pytest.approx(120.0 - 0.6, abs=0.1)              # the recess over the bedroom stays covered
    assert ring["kept_below"] and ring["kept_below"][0][0] == "r_L6_bed"
    assert any("r_L6_bed" in w and "open to the sky" in w for w in warns)
    b2 = _terrace_building([_room("r_L6_lw", "L6", _rect(4.5, 0, 7.5, 2.5), "other", "IŞIKLIK")])
    warns2 = []
    TB.drawn_ring(b2, {"levels": [{"id": "L7", "edge_rings": cands}], "regions": []}, b2["levels"][1],
                  [Polygon(_rect(4, 4, 8, 7))], warns2.append)
    assert Polygon(b2["slabs"][0]["outline"]).area == pytest.approx(120.0 - 4.0 - 0.6, abs=0.1)
    assert not any("open to the sky" in w for w in warns2)


def test_r23_a_double_line_parapet_on_one_layer_gives_the_outer_face_and_its_thickness():
    """Fix-up (GENERAL-6): the parapet drawn as two lines on one layer (outer face and inner face 0.20 m inside): the
    ring is the outer face, its thickness the mean offset (a corner never counts as sqrt 2 of it); the parapets are drawn
    (vector) and stand half the thickness inside; in a frame shifted from the sheets the ring moves with it."""
    from shapely.geometry import Polygon
    from wenart.sheets import terrace_ring as TRG
    from wenart.sheets import to_building as TB
    outer = [(0, 0), (12, 0), (12, 10), (0, 10)]
    inner = [(0.2, 0.2), (11.8, 0.2), (11.8, 9.8), (0.2, 9.8)]
    ents = [_line(f"o{k}", a, c, "PARAPET") for k, (a, c) in enumerate(zip(outer, outer[1:] + outer[:1]))]
    ents += [_line(f"i{k}", a, c, "PARAPET") for k, (a, c) in enumerate(zip(inner, inner[1:] + inner[:1]))]
    house = [(4, 4), (8, 4), (8, 7), (4, 7)]
    ents += [_line(f"h{k}", a, c, "0") for k, (a, c) in enumerate(zip(house, house[1:] + house[:1]))]
    reg = Region(id="r9", file="x.dxf", sheet=_sheet(), box=(-1, -1, 13, 11), geometry_box=(-1, -1, 13, 11),
                 ents=ents, texts=[], metres_per_unit=1.0, transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    cands = TRG.rings(reg)
    assert {round(c["area_m2"], 1) for c in cands} >= {120.0, 111.4}       # the outer face and the inner face
    below = Polygon(_rect(0, 0, 12, 10))
    ring = TRG.choose(cands, below, [(6, 5.5)])
    assert ring is not None and ring["polygon"].area == pytest.approx(120.0, abs=0.01)
    assert ring["thickness"] == pytest.approx(0.2, abs=0.01)
    b = _terrace_building()
    n = TB._edge_parapets(b, b["levels"][1], 1.1, "assumed", ring=ring)
    pars = [w for w in b["walls"] if w.get("parapet")]
    assert n == len(pars) > 0 and all(w["status"] == "verified" and w["rule"] == "roof_terrace_ring" for w in pars)
    assert all(w["evidence"][0]["method"] == "vector" for w in pars)
    assert min(min(w["start"][0], w["end"][0]) for w in pars) == pytest.approx(0.1, abs=0.01)
    # the building frame stands 3 m east of the sheets' (building = sheets - shift): the ring is chosen there
    shifted = TRG.choose(cands, Polygon(_rect(-3, 0, 9, 10)), [(3, 5.5)], (3.0, 0.0))
    assert shifted is not None and shifted["polygon"].bounds[0] == pytest.approx(-3.0, abs=0.01)
    # one face only (no inner line): the line, not the thickness: inferred parapets on the ring
    cands1 = [c for c in cands if round(c["area_m2"], 1) == 120.0]
    ring1 = TRG.choose(cands1, below, [(6, 5.5)])
    b1 = _terrace_building()
    TB._edge_parapets(b1, b1["levels"][1], 1.1, "assumed", ring=ring1)
    p1 = [w for w in b1["walls"] if w.get("parapet")]
    assert p1 and all(w["status"] == "unverified" and w["rule"] == "roof_terrace_ring" for w in p1)


def test_r23_a_ring_that_is_no_terrace_edge_is_not_taken():
    from shapely.geometry import Polygon
    from wenart.sheets import terrace_ring as TRG
    below = Polygon(_rect(0, 0, 12, 10))
    far = [{"layer": "FRAME", "area_m2": 400.0, "points": _rect(-5, -5, 15, 15)}]
    assert TRG.choose(far, below, [(6, 5)]) is None                      # a frame round the drawing
    small = [{"layer": "0", "area_m2": 12.0, "points": _rect(4, 4, 8, 7)}]
    assert TRG.choose(small, below, [(6, 5)]) is None                    # the stair house


# --------------------------------------------------------------------------------------------------------------------
# the regression set's new structure lines
# --------------------------------------------------------------------------------------------------------------------

def test_struct_lines_show_slab_openings_door_steps_copies_and_upper_spaces():
    from wenart.reading_check import regress as R
    b = {"slabs": [{"id": "sl_L1", "openings": [{"kind": "stair_void", "furniture_id": "f1", "polygon": _rect(0, 0, 2, 2),
                                                 "clipped_rooms": ["r_bath"]}],
                    "stairs_not_stacked": [{"stair": "f9"}], "outline_source": "roof_terrace_ring"}],
         "level_inference": {"inner_steps": [{"opening_id": "d_1", "rise": 0.25, "risers": 2, "placed": "r_garaj",
                                              "kind": "steps"}],
                             "typical_checks": {"dropped": [{"level_id": "L0", "room": "r_L0_oda"}],
                                                "stairs": [], "notes": []}},
         # 28 Nov 2026 (fix-up): the one upper-reach rule writes its verdict on the space or its refusal
         "site": {"outdoor_spaces": [{"id": "os_L1_teras", "upper_support": {"action": "clipped"}}],
                  "outdoor_spaces_refused": [{"area_id": "sa_L2_balkon",
                                              "refused": {"rule": "A-R16", "reason": "... not built (a purely "
                                                                                     "inferred space)"}}]}}
    lines = R.structure_lines(dict(R.structure_5b(b), levels={}, section={}, roof=None, stairs={}))
    text = "\n".join(lines)
    assert "slab sl_L1: 1 stair void(s), 0 void(s), 4.0 m2 open; clipped f1; not stacked f9; outline roof_terrace_ring" \
        in text
    assert "door step d_1: rise 0.25 m, 2 risers, steps in r_garaj" in text
    assert "copied storeys vs section: rooms dropped L0:r_L0_oda" in text
    b["level_inference"]["typical_checks"]["acted"] = False
    lines2 = R.structure_lines(dict(R.structure_5b(b), levels={}, section={}, roof=None, stairs={}))
    assert "copied storeys vs section: rooms to drop (listed) L0:r_L0_oda" in "\n".join(lines2)
    assert "upper outdoor spaces past the walls below: os_L1_teras:clipped, sa_L2_balkon:refused" in text


def test_struct_lines_from_the_producers_show_blocked_stairs_short_headroom_and_held_copies(tmp_path, monkeypatch):
    """Fix-up (weak test: the struct lines guarded only hand-made records): the records the slab, step and copy rules
    themselves write reach the regression set's lines."""
    from wenart.reading_check import regress as R
    from wenart.sheets import typical_check as TCK

    def lines(b):
        return "\n".join(R.structure_lines(dict(R.structure_5b(b), levels={}, section={}, roof=None, stairs={})))
    b, _w = _slab_case([_room("r_L1_bed", "L1", _rect(0, 0, 4, 6), "bedroom"),
                        _room("r_L1_hall", "L1", _rect(4, 0, 8, 6), "hall")])
    text = lines(b)
    assert "not stacked f_L0_1" in text and "stairs blocked (the level above cannot be reached): L0:f_L0_1" in text
    b2, _w = _slab_case([_room("r_L1_hall", "L1", _rect(0, 0, 8, 3.6), "hall"),
                         _room("r_L1_bath", "L1", _rect(0, 3.6, 3, 6), "bathroom")])
    assert "clipped f_L0_1 (headroom short f_L0_1)" in lines(b2)
    orig = TCK.user_assertions
    path = _corrections_file(tmp_path, [{"id": "C9", "project": "pX", "status": "accepted", "level": "L0",
                                         "place": {"x": 5.5, "y": 2.0}}])
    monkeypatch.setattr(TCK, "user_assertions", lambda project, lid, path_=None: orig(project, lid, path))
    b3 = _copied_block()
    b3["project"] = {"id": "pX"}
    TCK.apply(SimpleNamespace(building=b3, sheets=_sheets(), frame_shift=(0.0, 0.0), warn=lambda *a: None,
                              conflict=lambda *a: None))
    assert "held by the user's corrections L0:f_L0_stair(C9),L0:r_L0_stair(C9)" in lines(b3)


# --------------------------------------------------------------------------------------------------------------------
# the coordinator's check-pod findings: a section line over the ground floor's doors is no ground
# --------------------------------------------------------------------------------------------------------------------

def _ground_case():
    b = {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7}],
         "walls": _walls("L0", 0, 0, 10, 8), "rooms": [_room("r_L0_salon", "L0", _rect(0.1, 0.1, 9.9, 7.9))],
         "openings": [{"id": "d_L0_1", "level_id": "L0", "type": "door", "wall_id": "w_L0_001", "width": 0.9,
                       "center": [5.0, 0.0], "threshold_z": 0.0}],
         "furniture": [], "site": {}}
    return b


def _gline(side, z):
    return {"side": side, "azimuth_deg": None,
            "z": {"value": z, "method": "vector", "evidence": [{"rule": "ground_line"}]}}


def test_a_section_ground_line_over_the_ground_floors_doors_is_refused():
    """A section ground line is refused when it would bury an outside door on its own side (fix-up SECTIONS-8: each
    line stands at its own end of the cut; a door on another facade never refuses it)."""
    from wenart.levels import model as M
    from wenart.levels import rules as RU
    b = _ground_case()                                   # the door d_L0_1 on the front (-y) facade
    outline = M.level_outline(b, "L0")
    gl = b["levels"][0]
    front = [_gline("front", 2.2)]
    rec = M._section_ground_gate(b, [], gl, outline, front, dict(RU.BUILTIN_PARAMS))
    assert rec is not None and "section's ground line" in rec["why"] and rec["refused"] and rec["buried"] == ["d_L0_1"]
    # the same line at the section's other end (the back, +y) or across (right, +x): no door there, kept
    for side in ("back", "right"):
        assert M._section_ground_gate(b, [], gl, outline, [_gline(side, 2.2)], dict(RU.BUILTIN_PARAMS)) is None, side
    # a site sloping across the cut (both ends of a cut along x at +1.0, the door on the front): kept
    assert M._section_ground_gate(b, [], gl, outline, [_gline("left", 1.0), _gline("right", 1.0)],
                                  dict(RU.BUILTIN_PARAMS)) is None
    # one side under the floor (a sloping site): kept
    both = front + [_gline("back", -0.4)]
    assert M._section_ground_gate(b, [], gl, outline, both, dict(RU.BUILTIN_PARAMS)) is None
    low = [_gline("all", -0.5)]
    assert M._section_ground_gate(b, [], gl, outline, low, dict(RU.BUILTIN_PARAMS)) is None
    # a line for every side over the door: refused
    assert M._section_ground_gate(b, [], gl, outline, [_gline("all", 1.0)], dict(RU.BUILTIN_PARAMS)) is not None


def test_the_ground_step_lists_a_refused_section_line_and_takes_the_next_source():
    """The wiring in ``_ground``: a refused section ground line is listed (``refused_levels``, ``level_inference``), it
    is no ground level any more, and the default ground is held to the gate's limit."""
    from wenart.levels import model as M
    from wenart.levels import rules as RU
    b = _ground_case()
    b["site"] = {"ground": {"levels": [_gline("front", 2.2)]}}
    outline = M.level_outline(b, "L0")
    inferred, warnings = [], []
    M._ground(b, [], dict(RU.BUILTIN_PARAMS), b["levels"][0], outline, inferred, warnings)
    g = b["site"]["ground"]
    assert [x["side"] for x in g["refused_levels"]] == ["front"] and "refused" in g["refused_levels"][0]
    assert b["level_inference"]["section_ground_gate"]["buried"] == ["d_L0_1"]
    assert all(lv.get("side") != "front" for lv in g["levels"])
    assert g["source"] == "D3a" and all(float(lv["z"]["value"]) <= 0.0 + 1e-9 for lv in g["levels"])
    assert any("section's ground line" in w for w in warnings)
    # the line at the back (no door there) stays the ground
    b2 = _ground_case()
    b2["site"] = {"ground": {"levels": [_gline("back", 2.2)]}}
    M._ground(b2, [], dict(RU.BUILTIN_PARAMS), b2["levels"][0], outline, [], [])
    assert b2["site"]["ground"]["source"] == "section" and not b2["site"]["ground"].get("refused_levels")
