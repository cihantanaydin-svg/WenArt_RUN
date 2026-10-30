"""UL201 (30 Oct 2026): "This is inspration for shower solutions" (the user's photo: a level-access shower behind
frameless clear glass, a black sliding door on a top rail with round rollers, a square rain head, a hand shower on a
slide bar, a bar mixer, a linear drain, the floor tiles running in). Every walk-in shower is built so: level access, the
glass on every open side, the way in on an open side. Pure tests on the hand-made bathroom of the bathroom tests."""
import test_bathroom_details_20261029 as T
from wenart.blender import bath_parts as BT
from wenart.blender import modules as MOD
from wenart.furniture import bath_details as BD


def _xs(parts, role):
    return [x for p in parts if p["role"] == role for x, _y, _z in p["verts"]]


def test_level_access_by_default_the_tray_only_when_asked():
    level = BT.walk_in_shower_parts(1.83, 0.8, 2.2, {"level_access": True})
    roles = {p["role"] for p in level}
    assert "tray" not in roles and {"drain", "glass", "rail", "roller", "head", "hand_shower", "mixer"} <= roles
    drain = [z for p in level if p["role"] == "drain" for _x, _y, z in p["verts"]]
    assert max(drain) <= BT.DRAIN_T_M + 1e-9                        # flush with the floor
    glass = [z for p in level if p["role"] == "glass" for _x, _y, z in p["verts"]]
    assert min(glass) <= 0.011                                       # the glass stands on the floor itself
    tray = BT.walk_in_shower_parts(1.83, 0.8, 2.2, {"level_access": False})
    assert "tray" in {p["role"] for p in tray}
    assert "tray" not in {p["role"] for p in BT.walk_in_shower_parts(1.83, 0.8, 2.2)}     # the default: level


def test_an_open_end_gets_its_glass_panel_and_the_sliding_door_a_bar_pull():
    w, d = 1.2, 0.9
    shut = BT.walk_in_shower_parts(w, d, 2.2, {"shower_sides": {"left": "wall", "right": "wall"}})
    corner = BT.walk_in_shower_parts(w, d, 2.2, {"shower_sides": {"left": "glass", "right": "wall"}})
    assert "clamp" not in {p["role"] for p in shut} and "clamp" in {p["role"] for p in corner}
    side = [p for p in corner if p["role"] == "glass" and max(x for x, _y, _z in p["verts"]) < -w / 2.0 + 0.05]
    assert len(side) == 1
    ys = [y for _x, y, _z in side[0]["verts"]]
    assert max(ys) - min(ys) > d * 0.8                               # from the front glass to the back wall
    pulls = [p for p in corner if p["role"] == "handle"]
    assert len(pulls) == 3                                           # the bar and its two stand-offs
    for parts in (shut, corner):
        assert all(-w / 2.0 - 1e-6 <= x <= w / 2.0 + 1e-6 and -d / 2.0 - 1e-6 <= y <= d / 2.0 + 1e-6
                   for p in parts for x, y, _z in p["verts"])
        assert all(T.volume(p) > -1e-9 for p in parts)
        assert sum(len(p["verts"]) for p in parts) < 2500


def test_the_plan_records_the_open_sides_and_level_access():
    b = T.bathroom(T.toilet(), T.basin(), T.shower(), T.column())   # the shower in the north-east corner
    BD.plan_building(b, T.style_of("modern"))
    sh = next(f for f in b["furniture"] if f["id"] == "s1")
    look = BT.bath_look(sh)
    assert look["level_access"] is True and look["shower_sides"] == {"left": "glass", "right": "wall",
                                                                     "front": "glass"}
    assert "level-access" in look["reason"] and "UL201" in look["reason"]
    plan = MOD.plan_bath_made(sh) if hasattr(MOD, "plan_bath_made") else None
    if plan is not None:
        assert "level access" in plan["products"][0] and "left end" in plan["products"][0]


def test_a_shower_whose_front_stands_on_a_wall_opens_on_its_free_side():
    # 0.6 wide, 1.4 deep against the east wall, its front read on the north wall: the long west side is the way in
    s = T.M.fp("s2", "shower", (2.7, 1.9), (0.6, 1.4), rotation=180.0, front=90.0)
    b = T.bathroom(s)
    room = b["rooms"][0]
    sides = BD.shower_sides(s, room)
    assert sides["front"] == "wall" and sides["left"] == "wall" and sides["right"] == "glass"
    after = BD.shower_entry(s, room)
    assert after["front"] == "glass" and s["adjusted_by_ai"]["rule"] == "bath_details.shower_entry"
    assert s["drawn_front_deg"] == 90.0 and s["front_deg"] == 180.0
    w, d = s["footprint"]["size"]
    assert w > d                                                     # the long side is the way in now
