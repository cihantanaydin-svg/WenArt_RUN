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


def test_r22_the_pipeline_lists_what_the_section_says_and_waits_for_the_user():
    """The score gate (a correction of the user asks for a stair on a copied storey the section draws as a
    double-height hall): the pipeline's default lists the section's verdict and changes nothing (``ACT``)."""
    from wenart.sheets import typical_check as TCK
    assert TCK.ACT is False
    b = _copied_block()
    before = copy.deepcopy(b)
    warns, conflicts = [], []
    build = SimpleNamespace(building=b, sheets=_sheets(), frame_shift=(0.0, 0.0), warn=warns.append,
                            conflict=lambda *a: conflicts.append(a))
    rec = TCK.apply(build)
    assert rec["acted"] is False and [d["room"] for d in rec["dropped"]] == ["r_L0_stair"]
    assert {k: b[k] for k in before} == before
    assert any("listed, not carried out" in w for w in warns) and conflicts
    assert b["level_inference"]["typical_checks"]["acted"] is False


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
    ("EĞİM 30", False, 30.0, "percent"), ("EĞİM:35", False, 35.0, "percent"), ("EĞİM 7", False, 12.278, "degrees"),
    ("%30 EĞİM", False, 30.0, "percent")])
def test_r07f_written_slopes_in_degrees_and_bare_numbers(text, roof, pct, unit):
    from wenart.sheets import titles as T
    rd = T.slope_reading(text, roof)
    assert rd is not None and abs(rd["pct"] - pct) < 0.01 and rd["unit"] == unit
    assert abs(T.slope_pct(text, roof) - pct) < 0.01


def test_r07f_no_slope_from_a_bare_angle_off_a_roof_plan_or_a_length():
    from wenart.sheets import titles as T
    assert T.slope_pct("30°", roof=False) is None and T.slope_pct("EĞİM 30 cm", roof=True) is None
    assert T.slope_pct("EĞİM 2", roof=True) is None and T.slope_reading("EĞİM 2 m") is None


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
    g = _section([("±0.00", 0.0, 0.0), ("+5.80", 5.80, 5.75), ("+7.45", 7.45, 7.40)])
    out, _w = HT.heights(g, levels, None, {}, "x.dxf", lambda *a, **k: "c1", None)
    assert out["roof"]["eaves_z"]["value"] == pytest.approx(5.80) and "snapped" in out["roof"]["eaves_z"]["note"]
    assert out["roof"]["ridge_z"]["value"] == pytest.approx(7.30)        # +7.45 is 0.15 m off: not snapped
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


def test_r07g_drawn_heights_win_when_their_pitch_is_plausible():
    from wenart.blender import roof as RF
    b = _roof_building()
    d = RF.derive(_roof(5.8, 7.8, 60.0), b)          # drawn 20.8 deg, written 31 deg: the drawn heights win
    assert d["eaves_z"] == pytest.approx(5.8) and d["ridge_z"] == pytest.approx(7.8, abs=0.01)
    assert any("drawn heights win" in w for w in d["warnings"])


def test_r07g_a_ridge_mark_that_cannot_stand_with_the_full_storeys_eaves_is_the_wrong_reading():
    from wenart.blender import roof as RF
    b = _roof_building()
    d = RF.derive(_roof(5.8, 6.4, 30.0), b)          # drawn 5.9 deg (< 10 for tiles); 30 % with the ridge: eaves 4.7
    assert d["eaves_z"] == pytest.approx(5.8)
    assert d["pitches"][0] == pytest.approx(16.7, abs=0.1) and d["ridge_z"] > 6.4 + 0.5
    assert any("wrong reading" in w for w in d["warnings"])


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


def test_steps_are_built_in_the_lower_room_and_a_garage_vehicle_door_gets_a_ramp():
    from wenart.blender import shell as SH
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    b, steps = _two_rooms(0.35)
    res = DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
    st = b["openings"][0]["steps"]
    assert res["built"] and st["kind"] == "steps" and st["risers"] == 2 and st["room_id"] == "r_low"
    assert len(st["blocks"]) == 1 and st["blocks"][0]["z1"] == pytest.approx(-0.175)
    assert all(p[1] <= 4.0 + 1e-6 for p in st["blocks"][0]["polygon"])          # in front of the door, low side
    verts, faces = SH.door_step_blocks(b["openings"][0])
    assert len(verts) == 8 and len(faces) >= 6
    b2, steps2 = _two_rooms(0.25, width=2.4, low_depth=6.0)
    DS.place(b2, steps2, dict(RU.BUILTIN_PARAMS))
    assert b2["openings"][0]["steps"]["kind"] == "ramp"


def test_steps_that_do_not_fit_are_a_finding_not_a_build():
    from wenart.levels import door_steps as DS
    from wenart.levels import rules as RU
    b, steps = _two_rooms(0.90, low_type="hall", low_depth=0.6)
    res = DS.place(b, steps, dict(RU.BUILTIN_PARAMS))
    assert res["unbuilt"] and b["openings"][0]["steps"] is None and steps[0]["placed"] is None


# --------------------------------------------------------------------------------------------------------------------
# an upper outdoor space past the walls under it
# --------------------------------------------------------------------------------------------------------------------

def _upper(space_poly, evidence_text, roof=True):
    b = {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}],
         "walls": _walls("L0", 0, 0, 10, 10) + _walls("L1", 0, 0, 10, 6), "furniture": [], "rooms": [],
         "roof": {"type": "hip", "outline": _rect(-0.5, -0.5, 10.5, 10.5)} if roof else None,
         "site": {"outdoor_spaces": [{"id": "os_L1_teras", "level_id": "L1", "label": "TERAS", "kind": "terrace",
                                      "polygon": space_poly,
                                      "evidence": [{"method": "inferred", "text": evidence_text}]}]}}
    return b


def test_an_undrawn_upper_terrace_under_the_drawn_roof_and_far_past_the_walls_is_not_built():
    from wenart.levels import upper_support as US
    b = _upper(_rect(-4, 6, 10, 10), "rectangle in the inner corner: no drawn outline closes around the label")
    rec = US.check(b)
    assert rec and rec[0]["action"] == "dropped" and b["site"]["outdoor_spaces"] == []


def test_an_undrawn_upper_terrace_keeps_its_part_over_the_floor_below_and_within_a_cantilever():
    from wenart.levels import upper_support as US
    from shapely.geometry import Polygon
    b = _upper(_rect(-4, 6, 10, 10), "rectangle in the inner corner: no drawn outline closes around the label",
               roof=False)
    rec = US.check(b)
    assert rec[0]["action"] == "clipped"
    p = Polygon(b["site"]["outdoor_spaces"][0]["polygon"])
    assert p.bounds[0] == pytest.approx(-2.1, abs=0.01) and p.area == pytest.approx(48.4, abs=0.1)  # outer faces
    # a drawn outline is kept as drawn and listed
    b2 = _upper(_rect(-4, 6, 10, 10), "strokes: closed from the 3 stroke(s) on layer 'BALKON'")
    rec2 = US.check(b2)
    assert rec2[0]["action"] == "kept" and len(b2["site"]["outdoor_spaces"][0]["polygon"]) == 4


def test_an_undrawn_upper_balcony_sized_by_its_written_area_is_kept_and_listed():
    from wenart.levels import upper_support as US
    b = _upper(_rect(-3, 6, 3, 10), "rectangle against the facade: no drawn outline closes around the label", roof=False)
    b["site"]["outdoor_spaces"][0]["evidence"].insert(0, {"method": "vector", "text": "A:24.00m²"})
    rec = US.check(b)
    assert rec[0]["action"] == "kept" and len(b["site"]["outdoor_spaces"][0]["polygon"]) == 4
    # the inference's own note with the computed area is no written area
    b2 = _upper(_rect(-3, 6, 3, 10), "rectangle in the inner corner: no drawn outline closes around the label (24.00 "
                                     "m², inferred)", roof=False)
    assert US.check(b2)[0]["action"] == "clipped"


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
                                                "stairs": [], "notes": []},
                             "upper_support": [{"space": "os_L1_teras", "action": "dropped"}]}}
    lines = R.structure_lines(dict(R.structure_5b(b), levels={}, section={}, roof=None, stairs={}))
    text = "\n".join(lines)
    assert "slab sl_L1: 1 stair void(s), 0 void(s), 4.0 m2 open; clipped f1; not stacked f9; outline roof_terrace_ring" \
        in text
    assert "door step d_1: rise 0.25 m, 2 risers, steps in r_garaj" in text
    assert "copied storeys vs section: rooms dropped L0:r_L0_oda" in text
    b["level_inference"]["typical_checks"]["acted"] = False
    lines2 = R.structure_lines(dict(R.structure_5b(b), levels={}, section={}, roof=None, stairs={}))
    assert "copied storeys vs section: rooms to drop (listed) L0:r_L0_oda" in "\n".join(lines2)
    assert "upper outdoor spaces past the walls below: os_L1_teras:dropped" in text
