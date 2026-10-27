"""Tall windows (user on real06, 27 Oct 2026: "In some of the rooms the full windows from top to bottom (with a bit of
remaining wall of course) could look better"). The architect's rule W5: in a style family that favours large glazing,
the windows of a living, dining or bed room (and of a dry room onto a terrace) whose sill and head no document fixes
become tall windows (a 0.20 m upstand, the head 0.25 m under the ceiling or the roof), drawn width and position kept,
the same on every facade of the room; never in a wet room, never where a wall-backed piece stands in front (the fit
caps that piece at the sill: ``fit.window_cap``), with the house's guard over a drop. CPU only; synthetic buildings
(``tests/test_decor_m8.room_building``) and the trimmed real06 copy of 25 Oct 2026."""
import copy
import json
from pathlib import Path

import pytest

from test_decor_m8 import room_building
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RR
from wenart.blender import build as BB
from wenart.furniture import fit as FIT
from wenart.furniture import infer as INF
from wenart.furniture import schemas as SC
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"


def _assumed(b):
    """The ingest's default windows: no sill and no head in the documents (``assumed``)."""
    for o in b["openings"]:
        if o["type"] == "window":
            o["sill_height"], o["height"] = 0.9, 1.2
            o["assumed"] = ["height", "sill_height"]
    return b


def _w(b, oid):
    return next(o for o in b["openings"] if o["id"] == oid)


def _decide(b, family="scandinavian"):
    """W5 asked, its safe defaults carried out (as ``build.prepare`` does), W5 asked again."""
    q = RR.tall_windows_rule(AA.Plan(b), family)
    answers = AR.defaults_of({"questions": q}, {})
    applied = AA.apply_answers(b, answers)
    return q, answers, applied, RR.tall_windows_rule(AA.Plan(b), family)


def living(**kw):
    # two windows on the south wall, one on the east wall
    kw.setdefault("windows", (("win_1", "s", 1.5, 1.2), ("win_2", "s", 4.5, 1.2), ("win_3", "e", 2.5, 1.0)))
    return _assumed(room_building(**kw))


def test_style_families_and_pins():
    for family, _slots in V.STYLE_FAMILIES:
        assert family in AA.GLAZING, family
    for f in ("scandinavian", "japandi", "modern", "minimal", "modern minimal", "contemporary", "Scandinavian"):
        assert AA.tall_glazing(f), f
    for f in ("classic", "rustic", "mediterranean", "industrial", None, "", "modern classic", "unknown"):
        assert not AA.tall_glazing(f), f
    # the window-front geometry is the fit's (the two rules agree), the wall-backed types cover infer.needs_wall and
    # the fixed equipment, the decor clearance is the build's
    assert (AA.WINDOW_FRONT_M, AA.WINDOW_OVERLAP_M) == (FIT.WINDOW_FRONT_M, FIT.WINDOW_OVERLAP_M)
    assert {t for t in SC.ORIENTATION_RULES if INF.needs_wall(t)} <= set(AA.WALL_BACKED_TYPES)
    assert set(SC.FIXED_TYPES) <= set(AA.WALL_BACKED_TYPES)
    assert AA.WINDOW_DECOR_CLEAR_M == BB.WINDOW_DECOR_CEILING_CLEAR_M
    assert "tall_window" in AA.ACTIONS and any(r["id"] == "W5" for r in RR.RULES)


def test_living_room_windows_become_tall():
    b = living()
    q, answers, applied, again = _decide(b)
    assert q[0]["status"] == "open" and answers["W5:r_L0_room"]["option"] == "tall_window"
    assert applied[0]["ok"], applied
    for oid, width, centre in (("win_1", 1.2, [1.5, -0.1]), ("win_2", 1.2, [4.5, -0.1]), ("win_3", 1.0, [6.1, 2.5])):
        o = _w(b, oid)
        assert o["sill_height"] == pytest.approx(AA.TALL_SILL_M)
        assert o["sill_height"] + o["height"] == pytest.approx(2.7 - AA.LINTEL_M)     # 0.25 m under the ceiling
        assert o["width"] == width and o["center"] == centre                         # drawn width and place kept
        assert o["drawn_sill_height"] == 0.9 and o["drawn_height"] == 1.2
        assert o["adjusted_by_ai"]["by"] == "architect" and "tall window" in o["adjusted_by_ai"]["reason"]
        assert o["evidence"][-1]["method"] == "inferred"
        assert o["tall_window"]["guard"] is False and "guard" not in o              # a ground floor: no drop
    assert again[0]["status"] == "ok" and "tall" in again[0]["answers"][0]["found"]


def test_other_families_keep_their_sills():
    for family in ("classic", "rustic", "mediterranean", None):
        b = living()
        q, answers, applied, _ = _decide(b, family)
        assert not q[0]["answers"] and not answers and not applied
        assert all(o["sill_height"] == 0.9 for o in b["openings"])


def test_documented_heights_stay():
    b = living()
    _w(b, "win_3")["assumed"] = []                    # the drawing gives win_3's sill and head: its facade keeps them
    b["openings"].append(dict(copy.deepcopy(_w(b, "win_1")), id="win_4", center=[1.5, 5.1], wall_id="w_n",
                              sill_height_source="section"))
    q, _answers, _applied, _ = _decide(b)
    assert _w(b, "win_3")["sill_height"] == 0.9 and _w(b, "win_4")["sill_height"] == 0.9
    assert _w(b, "win_1")["sill_height"] == pytest.approx(AA.TALL_SILL_M)
    found = q[0]["answers"][0]["found"]
    assert "the documents fix it" in found and "section" in found
    assert AA.heights_given(b, _w(b, "win_3")) and AA.heights_given(b, _w(b, "win_4"))
    # a door the reading turned into a window: its 0.90 m sill was set by code (the drawing gave none)
    conv = {"sill_height": 0.9, "height": 1.2, "assumed": ["height"], "drawn_sill_height": None}
    assert AA.heights_given(b, conv) is None
    # an elevation that draws the level's openings fixes them
    b2 = living()
    b2["facade"] = {"elevations": [{"side": "south", "positions_m": [{"x": 1.0, "sill": 0.9, "head": 2.1}]}]}
    assert "elevation" in AA.heights_given(b2, _w(b2, "win_1"))


def test_piece_in_front_keeps_the_facade_and_agrees_with_the_fit():
    # a dresser (wall-backed) in front of win_1: the whole south facade keeps its sills, the east window grows
    b = living(furniture=(("dresser", (1.5, 0.25), 0, (1.0, 0.45)),))
    dresser = b["furniture"][0]
    cap = FIT.window_cap(b, dresser)
    assert cap == pytest.approx(0.9 - FIT.WINDOW_SILL_GAP_M)
    q, _answers, applied, _ = _decide(b)
    assert "win_1: f_L0_001 (dresser) stands in front of it" in q[0]["answers"][0]["found"]
    assert _w(b, "win_1")["sill_height"] == 0.9 and _w(b, "win_2")["sill_height"] == 0.9     # one language
    assert _w(b, "win_3")["sill_height"] == pytest.approx(AA.TALL_SILL_M)
    assert "kept: win_1" in applied[0]["change"]
    assert FIT.window_cap(b, dresser) == pytest.approx(cap)          # the fit's cap still holds under the kept sill
    # a free-standing piece (an armchair) is no reason to keep a sill
    b = living(furniture=(("armchair", (1.5, 0.6), 0, (0.8, 0.8)),))
    _decide(b)
    assert _w(b, "win_1")["sill_height"] == pytest.approx(AA.TALL_SILL_M)


def test_never_in_wet_rooms_and_kitchens_only_onto_a_terrace():
    for rtype in ("bathroom", "wc", "hall", "storage"):
        b = living(room_type=rtype)
        q, answers, _applied, _ = _decide(b)
        assert not answers and all(o["sill_height"] == 0.9 for o in b["openings"]), rtype
    b = living(room_type="kitchen")
    q, answers, _applied, _ = _decide(b)
    assert not answers and "onto no terrace or garden" in q[0]["answers"][0]["found"]
    # a terrace outside the south wall: the kitchen's south windows open onto it
    b = living(room_type="kitchen")
    b["rooms"].append({"id": "r_terrace", "level_id": "L0", "label": "Terrace", "room_type": "terrace",
                       "polygon": [[0, -3.0], [6.0, -3.0], [6.0, -0.2], [0, -0.2]], "status": "verified",
                       "evidence": []})
    _decide(b)
    assert _w(b, "win_1")["sill_height"] == pytest.approx(AA.TALL_SILL_M)
    assert _w(b, "win_2")["sill_height"] == pytest.approx(AA.TALL_SILL_M)
    assert _w(b, "win_3")["sill_height"] == 0.9                       # the east window looks onto no terrace


def test_upper_floor_gets_the_guard_and_w3_passes():
    b = living(room_type="bedroom")
    b["levels"][0]["elevation"] = 3.0
    b["levels"].insert(0, {"id": "Lg", "label": "Lg", "order": -1, "elevation": 0.0, "ceiling_height": 2.7,
                           "ceiling_height_source": "assumed_default", "evidence": []})
    _decide(b)
    for oid in ("win_1", "win_2", "win_3"):
        o = _w(b, oid)
        assert o["sill_height"] == pytest.approx(AA.TALL_SILL_M)
        assert o["guard"]["top_m"] == AA.GUARD_TOP_M and o["tall_window"]["guard"] is True
    sides = [{"opening": o, "a": "r_L0_room", "b": None} for o in b["openings"]]
    w3 = next(q for q in RR.openings_rules(AA.Plan(b), sides) if q["id"] == "W3")
    assert w3["status"] == "ok" and all("with a guard" in a["found"] for a in w3["answers"])


def test_curtains_and_blinds_follow_the_window():
    b = living()
    b["decor"] = [{"id": "dec_1", "type": "curtain", "room_id": "r_L0_room", "window_id": "win_1",
                   "center": [1.5, 0.05, 0.8], "size": [1.8, 0.08, 1.45], "rotation_deg": 0.0},
                  {"id": "dec_2", "type": "blind", "room_id": "r_L0_room", "window_id": "win_2",
                   "center": [4.5, 0.05, 1.68], "size": [1.3, 0.06, 0.48], "rotation_deg": 0.0},
                  {"id": "dec_3", "type": "curtain", "room_id": "r_L0_room", "window_id": "win_3",
                   "center": [5.9, 2.5, 0.01], "size": [1.6, 0.08, 2.24], "rotation_deg": 90.0}]
    _decide(b)
    head = 2.7 - AA.LINTEL_M
    c1, bl, c3 = b["decor"]
    assert c1["center"][2] + c1["size"][2] == pytest.approx(head + 0.15, abs=1e-3)   # the rod as far over the head
    assert c1["center"][2] == pytest.approx(AA.TALL_SILL_M - 0.1, abs=1e-3)          # as far under the sill
    assert bl["center"][2] + bl["size"][2] == pytest.approx(head + 0.06, abs=1e-3)
    assert bl["size"][2] == pytest.approx(0.48 / 1.2 * (head - AA.TALL_SILL_M), abs=1e-3)
    assert c3["center"][2] == 0.01 and c3["size"][2] == pytest.approx(head + 0.15 - 0.01, abs=1e-3)
    assert all(d["adjusted_by_ai"]["by"] == "architect" for d in b["decor"])


def test_ai_architect_may_keep_the_sills():
    b = living()
    q = RR.tall_windows_rule(AA.Plan(b), "japandi")
    a = q[0]["answers"][0]
    assert a["default"] == "tall_window" and {o["id"] for o in a["options"]} == {"tall_window", "keep"}
    AA.apply_answers(b, {"W5:r_L0_001": {"option": "keep", "by": "ai"}})
    assert all(o["sill_height"] == 0.9 for o in b["openings"])


@pytest.mark.skipif(not REAL06.is_file(), reason="no real06 fixture")
def test_real06_scandinavian_living_room():
    drawn = json.loads(REAL06.read_text(encoding="utf-8"))
    drawn["project"]["source_folder"] = "projects/no_such_project"          # no user answers
    tall = BB.prepare(copy.deepcopy(drawn), "base", None, style_family="scandinavian")
    plain = BB.prepare(copy.deepcopy(drawn), "base", None, style_family="classic")
    made = [o for o in tall["building"]["openings"] if o.get("tall_window")]
    assert made and not any(o.get("tall_window") for o in plain["building"]["openings"])
    plan = AA.Plan(tall["building"])
    for o in made:
        assert not AA.front_pieces(plan, o)                     # never behind a wall-backed piece
        assert AA.heights_given(tall["building"], o) is None or o.get("drawn_sill_height") is not None
        rooms = [str((r or {}).get("room_type") or "") for r in AA.window_sides(plan, o)]
        assert not set(rooms) & set(RR.WET)
    w5 = next(q for q in tall["architect"]["questions"] if q["id"] == "W5")
    assert any(a.get("change") for a in w5["answers"])
    assert not tall.get("architect_refused_defaults", {}).get("W5")
