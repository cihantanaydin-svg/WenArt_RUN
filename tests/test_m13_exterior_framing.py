"""CPU tests of the fix round after P5 (22 Oct 2026), track E_exterior: the closer framing of a long, low building's
exterior views (user decision (2) of 22 Oct 2026, CLAUDE.md: "exterior views of long, low buildings may use a wider or
tilted framing"; wenart/blender/exterior.py ``long_low``, ``eye_distances``, ``LONG_LOW_*``; the X6 fill range of
wenart/blender/exterior_checks.py ``fill_range``).

What is pinned: the rule is read from the building's proportions (the outline rectangle's long side over the model's
height, ``LONG_LOW_RATIO``) and fires on a 33 x 15 m bungalow, not on a 10 x 8 m box or a two-storey house; the corner
and frontal views of a long, low building move in along their own view lines (same corner, same 30 degrees, square to
the entrance facade) to ``LONG_LOW_FILL`` of the frame width and stay level at eye height with the 26 mm lens, so the
horizon and the sky stay in the frame (CLAUDE.md); the rule only adds candidates in front of the Milestone 11 list, so
a view whose close places are all refused keeps its Milestone 11 place; X6 takes ``LONG_LOW_FILL_RANGE`` for those
views only. On P4b's real03 (runs/20261017-091212-full, not committed: that test skips without it) the corner views go
from 11-12 % of the frame to 23-25 % and the frontal view from 7.6 % to 15 %; the committed real02 fixture and real04
building do not fire the rule. Pure Python, no Blender."""
import copy
import gzip
import json
import math
from pathlib import Path

import pytest

from wenart.blender import build as B
from wenart.blender import exterior as E
from wenart.blender import exterior_checks as X
from wenart.blender import geom2d
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
REAL02 = ROOT / "tests" / "fixtures" / "m11_f1b" / "real02_building_final.json.gz"
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_final.json"
P4B = ROOT / "runs" / "20261017-091212-full" / "results"
P4B_REAL03 = P4B / "furniture" / "real03" / "building_final.json"
P4B_BRIEF = P4B / "renders" / "real03" / "build_brief.json"
SHARE_GAIN = 1.5            # the least gain in the building's frame share of a closer view (box: 1.6-2.0)


def _box(length=10.0, depth=8.0, ceiling=2.8, levels=1):
    """A ``length`` x ``depth`` m box of ``levels`` storeys (``ceiling`` + 0.3 m each) on flat ground, as
    tests/test_blender_exterior.py ``_box_building``."""
    pts = [(0, 0), (length, 0), (length, depth), (0, depth)]
    lvs = [{"id": f"L{k}", "elevation": round(k * (ceiling + 0.3), 3), "ceiling_height": ceiling} for k in range(levels)]
    walls = [{"id": f"w{k}_{i}", "level_id": lv["id"], "start": list(pts[i]), "end": list(pts[(i + 1) % 4]),
              "thickness": 0.25, "exterior": True} for k, lv in enumerate(lvs) for i in range(4)]
    site = {"ground": {"levels": [{"side": "all", "z": {"value": 0.0, "method": "vector"}}]}, "decor": [],
            "boundary_walls": []}
    return {"levels": lvs, "walls": walls, "openings": [], "rooms": [], "slabs": [], "site": site, "facade": {}}


def _model(b):
    outline, _ = geom2d.wall_outline([w for w in b["walls"] if w["level_id"] == b["levels"][0]["id"]])
    plan = S.site_plan(b, b["levels"], outline, "full")
    return E.build_model(b, b["levels"], None, plan), plan


def _plans(b, monkeypatch=None, rule_off=False):
    m, plan = _model(b)
    if rule_off:                                                # the Milestone 11 framing of the same building
        with monkeypatch.context() as mp:
            mp.setattr(E, "LONG_LOW_RATIO", 1e9)
            plans, dropped = E.plan_exterior(m, b, b["levels"], plan["plot"], variant="base")
    else:
        plans, dropped = E.plan_exterior(m, b, b["levels"], plan["plot"], variant="base")
    return m, {p["name"]: p for p in plans}, dropped


def _unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


# --------------------------------------------------------------------------
# The rule: measured on the building's proportions
# --------------------------------------------------------------------------

def test_long_low_reads_the_length_over_the_height():
    """Fails on BASE (no ``exterior.long_low``) and on a flipped or dropped ratio test."""
    low = E.long_low(_model(_box(33.0, 15.0))[0])
    assert low is not None and low["fill_target"] == E.LONG_LOW_FILL == 0.9
    assert low["length_m"] == pytest.approx(33.25, abs=0.01)          # the outer outline (0.25 m walls)
    assert low["height_m"] == pytest.approx(3.1, abs=1e-6)             # floor to the top level's ceiling + 0.3 m
    assert low["ratio"] == pytest.approx(33.25 / 3.1, abs=1e-3) and low["ratio"] >= E.LONG_LOW_RATIO
    assert E.long_low(_model(_box(10.0, 8.0))[0]) is None              # ratio 3.3: the M11 framing
    assert E.long_low(_model(_box(33.0, 15.0, levels=3))[0]) is None   # 33 m long but 9.3 m high: ratio 3.6
    # the threshold itself: just under and just over LONG_LOW_RATIO times the height (3.1 m)
    assert E.long_low(_model(_box(5.0 * 3.1 - 0.35, 6.0))[0]) is None
    assert E.long_low(_model(_box(5.0 * 3.1 - 0.15, 6.0))[0]) is not None
    assert E.long_low(E.ExteriorModel()) is None                        # no outline


def test_eye_distances_only_add_closer_places_in_front_of_the_m11_list():
    """The rule adds candidates, it removes none (fails on BASE: no ``eye_distances``)."""
    m11 = [(19.0 + s, False) for s in E.MOVE_STEPS_M]
    assert E.eye_distances(19.0) == m11
    assert E.eye_distances(19.0, None) == m11
    assert E.eye_distances(19.0, 11.0) == [(11.0, True), (13.0, True), (15.0, True), (17.0, True)] + m11
    assert all(s >= 0.0 for s in E.LONG_LOW_STEPS_M)                    # a step in would cut the building
    # a close place at the scan's start; M11 steps under DISTANCE_SCAN_M[0] are left out, as before (7 - 1.5 m)
    assert E.eye_distances(7.0, 6.0) == [(6.0, True), (7.0, False), (9.0, False), (11.0, False), (13.0, False),
                                         (16.0, False), (19.0, False)]


# --------------------------------------------------------------------------
# The views of a long, low box
# --------------------------------------------------------------------------

def test_long_low_views_move_in_on_their_own_view_lines(monkeypatch):
    """The corner and frontal views of a 33 x 15 m bungalow fill about 0.9 of the frame width, on the same lines as
    the Milestone 11 views, level at eye height with the 26 mm lens (horizon and sky in the frame), and the building
    fills a larger share of the frame. Fails on BASE (fill 0.7, no ``long_low`` in the plan)."""
    b = _box(33.0, 15.0)
    m, on, dropped = _plans(b)
    _m, off, _ = _plans(b, monkeypatch, rule_off=True)
    assert set(on) == set(off) and not [d for d in dropped if d["view"] in ("corner", "frontal")]
    corners = geom2d.rectangle_corners(geom2d.oriented_rectangle(m.outline))
    eye_views = [n for n, p in on.items() if p["view"] in ("corner", "frontal")]
    assert len(eye_views) == 5
    for n in eye_views:
        p, q = on[n], off[n]
        assert p["long_low"] == E.long_low(m) and "long_low" not in q
        assert E.LONG_LOW_FILL - 0.05 <= p["fill"] <= E.LONG_LOW_FILL + 1e-9
        assert E.FILL_RANGE[0] <= q["fill"] <= E.FILL_RANGE[1]
        assert p["lens_mm"] == q["lens_mm"] == E.EYE_LENS_MM
        assert p["pitch_deg"] == 0.0 and p["position"][2] == pytest.approx(E.EYE_HEIGHT, abs=1e-6)
        # the horizon (eye level) lies in the middle part of the frame: 0.5 - shift_y * W / H of the height
        horizon = 0.5 - p["shift_y"] * E.RESOLUTION[0] / E.RESOLUTION[1]
        assert 0.3 <= horizon <= 0.7
        assert p["score"]["building_share"] >= SHARE_GAIN * q["score"]["building_share"]
        assert "framed to 90% of the width" in p["placement"] and "long, low building" in p["placement"]
        if p["view"] == "corner":
            c = corners[p["corner"] - 1]
            dp = (p["position"][0] - c[0], p["position"][1] - c[1])
            dq = (q["position"][0] - c[0], q["position"][1] - c[1])
            assert math.hypot(*dp) < math.hypot(*dq) - 3.0              # closer ...
            assert _unit(dp) == pytest.approx(_unit(dq), abs=1e-4)      # ... on the same line
            assert p["sides"] == q["sides"] and p["faces"] == q["faces"]
        else:                                                           # frontal: still square to the facade
            cx, cy = geom2d.oriented_rectangle(m.outline)["center"]
            dp = (p["position"][0] - cx, p["position"][1] - cy)
            dq = (q["position"][0] - cx, q["position"][1] - cy)
            assert math.hypot(*dp) < math.hypot(*dq) - 3.0
            assert min(abs(p["position"][0] - q["position"][0]), abs(p["position"][1] - q["position"][1])) < 1e-3
            assert p["sides"] == q["sides"] and p["main_facade"] == q["main_facade"]
    small = _plans(_box(10.0, 8.0))[1]                                  # the rule leaves other buildings alone
    assert all("long_low" not in p for p in small.values())


def test_a_long_low_view_whose_close_places_are_refused_keeps_its_m11_place(monkeypatch):
    """The fallback: every candidate but the Milestone 11 places refused by the view check (as a tree, a wall or a
    hedge above the eye would) -> each corner and frontal view keeps its Milestone 11 place, as before the rule.
    Fails on a mutation that drops the M11 list from ``eye_distances`` (the views would be dropped)."""
    b = _box(33.0, 15.0)
    _m, off, _ = _plans(b, monkeypatch, rule_off=True)
    allowed = [p["position"] for p in off.values()]
    real_check = E.view_check

    def check(model, position, target, lens, shift_y, aim):
        rec = real_check(model, position, target, lens, shift_y, aim)
        if not any(math.dist(position, q) < 0.25 for q in allowed):
            return dict(rec, ok=False, why="a test obstacle in front of the camera", blocked=0.9)
        return rec

    monkeypatch.setattr(E, "view_check", check)
    _m, on, dropped = _plans(b)
    far = {n: p["position"] for n, p in off.items() if p["view"] in ("corner", "frontal")}
    assert len(far) == 5
    for n, pos in far.items():
        assert on[n]["position"] == pytest.approx(pos, abs=1e-6), n
        assert "a test obstacle" in on[n]["warning"] and "moved" in on[n]["warning"]
        assert "framed to" not in on[n]["placement"]                   # the M11 place says nothing of the rule
        assert on[n]["long_low"]["fill_target"] == E.LONG_LOW_FILL      # the building is still long and low


# --------------------------------------------------------------------------
# X6
# --------------------------------------------------------------------------

def _x6(cams):
    out = []
    X._x6({}, {}, {"cameras": cams}, None, out)
    return [v for v in out if "frame width" in v["message"]]


def test_x6_takes_the_long_low_fill_range_for_those_views_only():
    """Fails on BASE: X6 flagged every closer view as "fills 89% of the frame width (wanted 60%-80%)"."""
    low = {"length_m": 33.3, "height_m": 3.2, "ratio": 10.4, "fill_target": 0.9}
    assert X.fill_range({"view": "corner", "long_low": low}) == E.LONG_LOW_FILL_RANGE == (0.6, 0.9)
    assert X.fill_range({"view": "frontal", "long_low": low}) == E.LONG_LOW_FILL_RANGE
    assert X.fill_range({"view": "corner"}) == X.FILL_RANGE == E.FILL_RANGE
    assert X.fill_range({"view": "elevation", "long_low": low}) == X.FILL_RANGE
    cam = {"name": "ext_1", "kind": "exterior", "view": "corner", "position": [-5.0, -9.0, 1.6],
           "target": [5.0, 0.0, 1.6], "sides": ["front", "left"], "fill": 0.89}
    assert len(_x6([cam])) == 1                                         # no rule: out of 60-80 % (+5 %)
    assert _x6([dict(cam, long_low=low)]) == []
    assert len(_x6([dict(cam, long_low=low, fill=0.97)])) == 1          # past 90 % (+5 %): still a finding
    msg = _x6([dict(cam, long_low=low, fill=0.5)])[0]["message"]
    assert "wanted 60%-90%" in msg


# --------------------------------------------------------------------------
# The committed real02 / real04 buildings and P4b's real03
# --------------------------------------------------------------------------

def _prep_model(building, brief=None):
    prep = B.prepare(copy.deepcopy(building), "base", brief)
    vb = prep["building"]
    levels = sorted(vb["levels"], key=lambda lv: float(lv["elevation"]))
    return prep, vb, levels, E.build_model(vb, levels, prep["roof"], prep["site"])


def test_real02_and_real04_are_not_long_and_low():
    """real02 (ratio 1.55) and real04 (1.49) keep the Milestone 11 framing (their plans do not change)."""
    real02 = json.loads(gzip.decompress(REAL02.read_bytes()).decode("utf-8"))
    assert E.long_low(_prep_model(real02)[3]) is None
    if REAL04.is_file():
        assert E.long_low(_prep_model(json.loads(REAL04.read_text(encoding="utf-8")))[3]) is None


@pytest.mark.skipif(not (P4B_REAL03.is_file() and P4B_BRIEF.is_file()),
                    reason="P4b's real03 run (runs/20261017-091212-full) is not committed")
def test_p4b_real03_exterior_views_fill_more_of_the_frame(monkeypatch):
    """P4b look lens (d), user decision (2) of 22 Oct 2026: real03 (33.3 x 3.2 m) filled 11-12 % of each corner view
    and 7.6 % of the frontal view (kept under the 8 % floor). Now: corners >= 22 %, frontal >= 14 %, the frontal view
    no longer kept by the share floor, the entrance view as before, no X6 fill finding."""
    building = json.loads(P4B_REAL03.read_text(encoding="utf-8"))
    brief = json.loads(P4B_BRIEF.read_text(encoding="utf-8"))
    prep, vb, levels, model = _prep_model(building, brief)
    low = E.long_low(model)
    assert low is not None and low["ratio"] == pytest.approx(10.42, abs=0.01)
    plot = (prep["site"] or {}).get("plot") or []
    plans = {p["name"]: p for p in E.plan_exterior(model, vb, levels, plot, variant="base")[0]}
    monkeypatch.setattr(E, "LONG_LOW_RATIO", 1e9)
    before = {p["name"]: p for p in E.plan_exterior(model, vb, levels, plot, variant="base")[0]}
    corners = [n for n, p in plans.items() if p["view"] == "corner"]
    assert len(corners) == 4
    for n in corners:
        assert before[n]["score"]["building_share"] < 0.13 and plans[n]["score"]["building_share"] >= 0.22
        assert plans[n]["score"]["blocked"] <= E.MAX_BLOCKED and plans[n]["pitch_deg"] == 0.0
    front = next(p for p in plans.values() if p["view"] == "frontal")
    assert before[front["name"]].get("share_kept") and before[front["name"]]["score"]["building_share"] < 0.08
    assert not front.get("share_kept") and front["score"]["building_share"] >= 0.14
    entrance = next(p for p in plans.values() if p["view"] == "entrance")
    assert entrance == before[entrance["name"]] and "long_low" not in entrance
    out = []
    X._x6(building, X._prep(building) or {}, {"cameras": list(plans.values())}, None, out)
    assert not [v for v in out if "frame width" in v["message"]]
