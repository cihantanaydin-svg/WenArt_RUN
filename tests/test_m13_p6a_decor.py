"""Fix round after P6a (22 Oct 2026; pod P6a, real04), track D_decor: what stands and hangs under the sloped roof.

What: CPU tests of
- the window decor under the roof (``decor_ai.window_items``): the window is read as the build clips it under the
  roof (``decor.roof_clips`` = ``roof.clip_openings_to_roof`` on ``roof.roof_model``, as ``build.prepare``), the
  curtain rod and the blind roller stay ``decor.WINDOW_DECOR_CEILING_CLEAR_M`` under the sloped ceiling over their
  own footprint and above the clipped window top, the item's reason carries the change, and a curtain or blind with
  no room left under the slope is left out with a note; a flat ceiling keeps the 2.25 m rod;
- a twin room's copy of a curtain or blind is not copied where it would reach the sloped ceiling
  (``decor.copy_partner_decor``);
- the group solver's headroom (``solver.Space``: the sloped ceiling from ``decor.ceiling_planes``, the layer and the
  exact test; a re-solved drawn piece never asked for more than its drawn place gives) and the twin copy of added
  pieces (``complete.copy_added`` with ``solver.headroom_short``).
Why: P6a's curtains dec_L1_005 / dec_L1_014 (top 2.25 m at windows the build clipped to a 1.71 m top, under a 1.83 m
slope) poked through the mansard roof in four exterior views, the two critical findings left after the agent; the
completion put two 1.8 m bookshelves and a 0.8 m console table under the 0.82 m slope of the L1 oyun rooms and hall
(critical / major X2 in every agent round), and the twin's mirrored bookshelf could not be moved. Every test fails on
52d4bb8 (BASE) or on the mutation its docstring names.
How: the committed real04 buildings (results/furniture/real04: building_fitted.json, the layout's input, and
building_furnished.json, the decor's input; their L1 sits under the drawn mansard roof, with no agent override, as
in P6a) and small hand-made changes of them. No Blender, no model.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.blender import roof as R
from wenart.furniture import complete as C
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import group_checks as GC
from wenart.furniture import placer
from wenart.furniture import program as PR
from wenart.furniture import solver as SV

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04"
OYUN = "r_L1_oyun_aktivite_ve_dinlenme_odasi"
OYUN_2 = "r_L1_oyun_aktivite_ve_dinlenme_odasi_2"
HALL = "r_L1_koridor"
CLIPPED_TOP_M = 0.9 + 0.8144          # win_L1_001 / 002 as the build clips them (P6a: 0.8144 m tall, sill 0.90 m)


def _load(name: str) -> dict:
    return json.loads((REAL04 / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def furnished():
    return _load("building_furnished.json")


@pytest.fixture(scope="module")
def fitted():
    return _load("building_fitted.json")


def _room(building: dict, room_id: str) -> dict:
    return next(r for r in building["rooms"] if r["id"] == room_id)


def _pieces(building: dict, room_id: str) -> list[dict]:
    return next(p for r, p in D.rooms_with_pieces(building) if r["id"] == room_id)


def _window_slot(building: dict, room_id: str, window_id: str):
    slots, notes = DA.room_slots(_room(building, room_id), _pieces(building, room_id), building)
    return next(s for s in slots if s.id == f"window:{window_id}"), notes


def _ceiling_over(building: dict, item: dict) -> float:
    return D.ceiling_over(building, "L1", item["center"][:2], item["size"][:2], item["rotation_deg"])


def _top(item: dict) -> float:
    return float(item["center"][2]) + float(item["size"][2])


# --------------------------------------------------------------------------
# Window decor under the roof
# --------------------------------------------------------------------------

def test_roof_clips_read_the_windows_as_the_build_clips_them(furnished):
    """The decor reads the same clip as ``build.prepare`` (P6a: win_L1_001 built 0.8144 m tall, top 1.71 m).
    BASE has no ``decor.roof_clips``."""
    clips = D.roof_clips(furnished, "L1")
    model = R.roof_model(furnished["roof"], furnished)
    level = next(lv for lv in furnished["levels"] if lv["id"] == "L1")
    assert clips == {c["opening_id"]: c for c in R.clip_openings_to_roof(furnished, level, model)}
    for wid in ("win_L1_001", "win_L1_002"):
        assert clips[wid]["height"] == pytest.approx(0.8144, abs=1e-3)
        assert DA._window_heights({"sill_height": 0.9, "height": 1.2}, clips[wid]) == pytest.approx(
            (0.9, CLIPPED_TOP_M), abs=1e-3)
    assert D.roof_clips(furnished, "L0") == {}            # only the level under the roof


@pytest.mark.parametrize("room_id,window_id", [(OYUN, "win_L1_001"), (OYUN_2, "win_L1_002")])
def test_curtain_and_blind_stay_under_the_slope_and_above_the_clipped_window(furnished, room_id, window_id):
    """P6a's dec_L1_005 / dec_L1_014: the curtain top 2.25 m under a 1.83 m slope. Now the rod and the roller stay
    0.02 m under the ceiling over their own footprint and above the window as the build clips it; the blind's drop
    comes from the clipped window. Fails on BASE (curtain top 2.25 m, blind top 2.16 m)."""
    slot, notes = _window_slot(furnished, room_id, window_id)
    curtain, blind = slot.items["curtain"], slot.items["blind"]
    for item in (curtain, blind):
        assert _top(item) <= _ceiling_over(furnished, item) - D.WINDOW_DECOR_CEILING_CLEAR_M + 1e-3
        assert _top(item) >= CLIPPED_TOP_M - 1e-3           # the rod / the roller never crosses the glass
    assert _top(curtain) == pytest.approx(1.808, abs=0.005)
    assert curtain["center"][2] == pytest.approx(0.8)       # furniture under the window: sill length, as before
    assert blind["size"][2] == pytest.approx(0.8144 * DA.P.BLIND_DOWN_SHARE + DA.BLIND_ROLLER_ABOVE_M, abs=2e-3)
    assert "kept under the sloped ceiling" in curtain["reason"] and "clipped by the roof" in curtain["reason"]
    assert any(n.startswith(f"window {window_id}: curtain (kept under the sloped ceiling") for n in notes)


def test_a_flat_ceiling_keeps_the_rod_0_15_m_over_the_window(furnished):
    """Under the flat L0 ceiling nothing changes: a curtain rod 0.15 m above the drawn window top (at most 0.10 m
    under the ceiling), the blind roller 0.06 m above it, no note (guards the slope-only branch)."""
    seen = 0
    for room, pieces in D.rooms_with_pieces(furnished):
        if room["level_id"] != "L0":
            continue
        slots, notes = DA.room_slots(room, pieces, furnished)
        ops = {o["id"]: o for o in furnished["openings"]}
        for s in (s for s in slots if s.kind == "window"):
            sill, top = DA._window_heights(ops[s.id.split(":", 1)[1]])
            ceiling = DA._ceiling(furnished, room)
            if "curtain" in s.items:
                seen += 1
                assert _top(s.items["curtain"]) == pytest.approx(min(top + 0.15, ceiling - 0.10), abs=1e-3)
                assert "sloped" not in s.items["curtain"]["reason"] and "note" not in s.items["curtain"]
            if "blind" in s.items:
                assert _top(s.items["blind"]) == pytest.approx(min(top + 0.06, ceiling - 0.02), abs=1e-3)
        assert not any("sloped ceiling" in n for n in notes)
    assert seen >= 2


def test_with_no_room_under_the_slope_the_curtain_and_the_blind_are_left_out(furnished, monkeypatch):
    """A slope 1 cm over the window top leaves no room for a rod or a roller above the glass: both are left out with
    a note (no slot). Fails on BASE (the window decor ignored the slope)."""
    monkeypatch.setattr(D, "ceiling_over", lambda *a, **k: CLIPPED_TOP_M + 0.01)
    room = _room(furnished, OYUN)
    ctx = placer.room_context(furnished, room)
    made, notes = DA.window_items(room, _pieces(furnished, OYUN), furnished, ctx, DA._ceiling(furnished, room))
    assert not [wid for wid, items in made if wid == "win_L1_001"]
    assert any(n.startswith("window win_L1_001: no curtain under the sloped ceiling") for n in notes)
    assert any(n.startswith("window win_L1_001: no blind under the sloped ceiling") for n in notes)


def test_the_ai_curtain_carries_the_change_in_its_reason(furnished):
    """The agreed AI curtain keeps the AI's reason and adds the code's change; the slot's internal ``note`` does not
    reach the building. Fails on BASE (no note) and on the mutation that drops the note in ``build_items``."""
    rq = next(q for q in DA.room_questions(furnished, "modern") if q.room["id"] == OYUN)
    choice = {"slot": "window:win_L1_001", "type": "curtain", "colour": "cream",
              "reasons": ["Softens the light.", "Softens the light."]}
    items, refused = DA.build_items(rq, [choice], "m", furnished, lambda lv: f"dec_{lv}_900")
    assert not refused and len(items) == 1
    item = items[0]
    assert item["reason"].startswith("Softens the light. (kept under the sloped ceiling, 1.83 m over it")
    assert "note" not in item and _top(item) == pytest.approx(1.808, abs=0.005)


# --------------------------------------------------------------------------
# The twin's copy of window decor
# --------------------------------------------------------------------------

def _curtain(top: float) -> dict:
    """P6a's dec_L1_005 (the oyun room's curtain at win_L1_001), with its top at ``top``."""
    return {"id": "dec_L1_005", "kind": "decor", "type": "curtain", "level_id": "L1", "room_id": OYUN,
            "center": [2.901, 4.571, 0.8], "rotation_deg": 90.0, "size": [2.4, 0.08, round(top - 0.8, 3)],
            "window_id": "win_L1_001", "wall_point": [2.8, 4.571], "source": "added_by_ai", "method": "ai",
            "host_id": None}


def test_a_twin_copy_of_a_curtain_through_the_slope_is_not_copied(furnished):
    """P6a's twin copy dec_L1_014 took dec_L1_005's 2.25 m top under the 1.83 m slope. A copy that would reach the
    slope is not copied (a note); the fixed curtain (top 1.808 m) is copied as before. Fails on BASE (copied)."""
    t = C.given_transform(_room(furnished, OYUN_2))          # the twin's mirror (x -> 17.173 - x), as in P6a
    assert t is not None and D.partner_rooms(furnished)[OYUN_2] == (OYUN, "twin")
    only = {OYUN_2: (OYUN, "twin", t)}
    ids = iter(range(900, 999))
    new_id = lambda lv: f"dec_{lv}_{next(ids)}"   # noqa: E731
    copies, notes = D.copy_partner_decor(furnished, [_curtain(2.25)], only, new_id)
    assert copies == [] and any("not copied" in n and "sloped ceiling" in n for n in notes)
    copies, notes = D.copy_partner_decor(furnished, [_curtain(1.808)], only, new_id)
    assert len(copies) == 1 and not notes
    assert copies[0]["window_id"] == "win_L1_002" and copies[0]["mirrored_from"] == "dec_L1_005"


# --------------------------------------------------------------------------
# The group solver's headroom
# --------------------------------------------------------------------------

def test_the_layout_building_has_no_ceiling_planes_so_the_solver_reads_the_roof(fitted):
    """The layout and fit buildings carry no ``level["ceiling_planes"]`` (only ``build.prepare`` writes them), so the
    solver must derive the slope itself (``decor.ceiling_planes``). BASE has no ``Space.headroom``."""
    level = next(lv for lv in fitted["levels"] if lv["id"] == "L1")
    assert not level.get("ceiling_planes")
    assert SV.headroom_planes(fitted, "L1") == D.ceiling_planes(fitted, "L1") != []
    space = SV.Space(fitted, _room(fitted, OYUN), [])
    assert space.headroom is not None and space.headroom.min() < 1.0 < space.headroom.max()
    flat = SV.Space(fitted, next(r for r in fitted["rooms"] if r["level_id"] == "L0"), [])
    assert flat.headroom is None and flat.planes == []


def test_need_height_new_and_re_solved_drawn_pieces(fitted):
    """A new piece needs its type's height + 0.05 m; a re-solved drawn piece at most what its drawn place gives less
    0.05 m (it may stay where it is drawn). The exact test refuses the low slope and keeps the high part. Fails on
    BASE (no ``need_height``); the mutation that drops the drawn cap refuses a drawn bookshelf at its drawn place."""
    space = SV.Space(fitted, _room(fitted, OYUN), [])
    low = SV.Spot("bookshelf", (2.9715, 0.6211), 90.0, (0.8, 0.3), "storage", True)
    high = SV.Spot("bookshelf", (8.2155, 2.4211), 270.0, (0.8, 0.3), "storage", True)
    assert space.need_height(low) == pytest.approx(GC.effective_height({"type": "bookshelf"}) + 0.05)
    assert not space.exact_ok(low, low.piece().polygon())
    assert space.exact_ok(high, high.piece().polygon())
    assert space.layer_for("bookshelf").hit(space.spot_fps(low)[0])
    drawn = {"id": "f_L1_999", "type": "bookshelf", "level_id": "L1", "room_id": OYUN, "source": "from_documents",
             "footprint": {"center": [2.9715, 0.6211], "size": [0.8, 0.3], "rotation_deg": 90.0}}
    moved = SV.Spot("bookshelf", (2.9715, 0.6211), 90.0, (0.8, 0.3), "anchor", True, existing_id="f_L1_999",
                    drawn=drawn)
    here = space.ceiling_over(moved.piece().polygon())
    assert here == pytest.approx(0.8212, abs=2e-3)
    assert space.need_height(moved) == pytest.approx(here - SV.DRAWN_HEADROOM_TOL_M, abs=1e-3)
    assert space.exact_ok(moved, moved.piece().polygon()) and space.spot_free(moved)


@pytest.mark.parametrize("room_id", [OYUN, HALL])
def test_the_solver_puts_no_piece_under_a_slope_lower_than_it(fitted, room_id):
    """P6a: the completion put the 1.8 m bookshelf f_L1_048 and the 0.8 m console table f_L1_049 under the 0.82 m
    slope. Every piece of every candidate now has its type's height + 0.05 m of ceiling over its footprint (the
    bookshelf moves under 1.86 m). Fails on BASE (0.82 m over the bookshelf and the console)."""
    prog = PR.room_program(fitted, room_id)
    cands = SV.solve_room(fitted, room_id, prog, k=3)
    assert cands and any(c["pieces"] for c in cands)
    for c in cands:
        for p in c["pieces"]:
            fp = p["footprint"]
            here = D.ceiling_over(fitted, "L1", fp["center"], fp["size"], fp["rotation_deg"])
            assert here >= GC.effective_height({"type": p["type"]}) + SV.HEADROOM_MARGIN_M - 1e-6, (p["id"], here)


def test_headroom_short_and_the_twin_copy_of_an_added_piece(fitted):
    """The twin room copies its partner's added pieces through the placer, not the solver: a copy without headroom is
    dropped (the room is then completed itself), one with headroom is copied. Fails on BASE (P6a: the mirrored
    bookshelf f_L1_056 copied under the 0.82 m slope)."""
    rooms = {r["id"]: r for r in fitted["rooms"]}
    r1, r2 = rooms[OYUN], rooms[OYUN_2]
    t = C.given_transform(r2)
    assert t is not None

    def added(centre, rot):
        return {"id": "f_L1_900", "type": "bookshelf", "level_id": "L1", "room_id": OYUN, "source": "added_by_ai",
                "footprint": {"center": list(centre), "size": [0.8, 0.3], "rotation_deg": rot}, "height": 1.8,
                "layout": {"against_wall": True}}

    for centre, rot, copied in (((2.9715, 0.6211), 90.0, False), ((8.2155, 2.4211), 270.0, True)):
        out = copy.deepcopy(fitted)
        ctx = placer.room_context(fitted, r2)
        got, dropped = C.copy_added(r2, r1["id"], [added(centre, rot)], t, C.floor_pieces(C.classify_drawn(r2, out)),
                                    out, ctx)
        assert bool(got) is copied and bool(dropped) is not copied
        if dropped:
            assert dropped[0]["reason"].startswith("the copy lacks headroom here")
    low = placer.Piece("bookshelf", (14.2015, 0.6211), 270.0, (0.8, 0.3), True).polygon()
    assert "a bookshelf needs 1.85 m" in SV.headroom_short(fitted, "L1", "bookshelf", low)
    assert SV.headroom_short(fitted, "L0", "bookshelf", low) is None          # flat level: no check
