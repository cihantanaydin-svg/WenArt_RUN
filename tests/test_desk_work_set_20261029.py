"""29 Oct 2026, the user on real06 run 20261028-154514-full (lesson UL93): "Computer on the table would have been nice or a
laptop" (a bedroom desk with its office chair had nothing on it).

General rules, tested on hand-made rooms (real06 is only the case that showed it):

- every desk, in any room type, and every writing table (a table with an office chair at it, the table of a home office
  without a desk) gets one work set by rule (``tabletop.work_set`` through ``dress_tops``): an open laptop on the side
  its seat stands at, its screen facing the seat; a home office desk a monitor on its stand, a keyboard and a mouse at
  the user's right; inside the top, clear of the other decor (which makes room, else is left out and listed); under a
  window behind the desk the laptop's screen may rise ``WORK_SILL_OVER_M`` over the sill, a monitor never does;
- the set is parametric, real product sizes with PBR keys (``parametric.work_set_parts``): an aluminium base 15-18 mm
  thick, a lid opened 105-115 degrees, a dark glossy screen with a faint lit wallpaper (key ``screen``);
- the decor of a piece the solver re-places (the agent's ``relayout_room``, ``move_group``) goes to its successor
  (``decor.hand_over``): real06's child's room desk lost its plant and books that way and rendered bare;
- Argus's lessons line flags a desk with no work set (U17, lesson UL93); the inspector's Q15 asks for it.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart.agent import prompts as AP
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import handover as HO
from wenart.furniture import solver as SV
from wenart.furniture import tabletop as TT

from test_decor_m8 import RID, room_building

ROOT = Path(__file__).resolve().parents[1]
DESK = (1.0, 0.5)


def _new_id():
    n = [0]

    def make(level_id):
        n[0] += 1
        return f"dec_{level_id}_{800 + n[0]}"
    return make


def _desk_room(rot=0.0, chair=True, room_type="bedroom", size=DESK, chair_side="front", windows=(), label=None):
    """A 4 x 3.5 m room with a desk against a wall (its back on the wall, front = local -Y) turned by ``rot`` and an
    office chair in front of it (``chair_side`` front, or ``end``: at its local +X end)."""
    w, d = size
    centres = {0.0: (2.0, 3.5 - d / 2.0), 90.0: (4.0 - d / 2.0, 1.75), 180.0: (2.0, d / 2.0), 270.0: (d / 2.0, 1.75)}
    c = centres[rot]
    furniture = [("desk", c, rot, size)]
    if chair:
        if chair_side == "front":
            local = (0.0, -d / 2.0 - 0.35)
        else:
            local = (w / 2.0 + 0.35, 0.0)
        r = math.radians(rot)
        p = (c[0] + local[0] * math.cos(r) - local[1] * math.sin(r), c[1] + local[0] * math.sin(r) + local[1] * math.cos(r))
        furniture.append(("office_chair", p, (rot + 180.0) % 360.0, (0.6, 0.6)))
    b = room_building(4.0, 3.5, room_type, furniture=furniture, windows=windows)
    if label:
        b["rooms"][0]["label"] = label
    return b, b["rooms"][0], b["furniture"]


def _faces(item: dict, point) -> float:
    """The cosine between an item's front (its local -Y) and the direction to ``point``."""
    r = math.radians(float(item["rotation_deg"]))
    fx, fy = math.sin(r), -math.cos(r)
    dx, dy = point[0] - item["center"][0], point[1] - item["center"][1]
    return (fx * dx + fy * dy) / math.hypot(dx, dy)


# -------------------------------------------------------------------------------------------------- the builders
def test_the_work_set_is_parametric_at_real_sizes_with_pbr_keys():
    assert P.WORK_DECOR_TYPES == D.WORK_DECOR_TYPES == TT.WORK_TYPES == ("laptop", "monitor", "keyboard",
                                                                          "computer_mouse")
    assert not set(P.WORK_DECOR_TYPES) & set(P.KITCHEN_DECOR_TYPES)
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    enum = schema["$defs"]["decor"]["properties"]["type"]["enum"]
    keys, _assumed = F.style_material_keys({"floor": {"material": "wood_oak_light"}})
    assert "screen" in P.MATERIAL_KEYS and "screen" in keys
    boxes = {"laptop": P.laptop_box(*TT.LAPTOP_BASES[0]), "monitor": TT.MONITOR_SIZE, "keyboard": TT.KEYBOARD_SIZE,
             "computer_mouse": TT.MOUSE_SIZE}
    for t, box in boxes.items():
        assert t in D.DECOR_TYPES and t in P.DECOR_TYPES and t in enum and t in P.SURFACE_DECOR_TYPES
        assert t not in DA.AI_TYPES                           # the rules place them: the AI's questions stay as they were
        assert P.DECOR_DEFAULT_HEIGHT[t] == pytest.approx(box[2], abs=0.003)
        parts = P.decor_parts(t, *box)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= box[0] + 1e-9 and y1 - y0 <= box[1] + 1e-9 and z1 - z0 <= box[2] + 1e-9 and z0 == 0.0
        assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS) and len({p["key"] for p in parts}) >= (
            1 if t == "computer_mouse" else 2)                # several PBR materials, never one grey box
        mesh = F.local_decor_mesh({"type": t, "size": list(box)}, t, "top")
        assert mesh["verts"] and mesh["faces"]


def test_the_laptop_is_open_like_a_real_one_and_its_screen_faces_the_user():
    for base in TT.LAPTOP_BASES:
        assert 0.32 - 1e-9 <= base[0] <= 0.36 + 1e-9 and 0.22 - 1e-9 <= base[1] <= 0.24 + 1e-9
    parts = P.decor_parts("laptop", *P.laptop_box(*TT.LAPTOP_BASES[0]))
    by = {p["role"]: p for p in parts}
    base, lid, screen = by["base"], by["lid"], by["screen"]
    zs = [v[2] for v in base["verts"]]
    assert 0.015 - 1e-9 <= max(zs) - min(zs) <= 0.018 + 1e-9
    xs, ys = [v[0] for v in base["verts"]], [v[1] for v in base["verts"]]
    assert max(xs) - min(xs) == pytest.approx(TT.LAPTOP_BASES[0][0]) and max(ys) - min(ys) == pytest.approx(
        TT.LAPTOP_BASES[0][1], abs=0.005)
    # the lid's inner (front) face: from the hinge at the base's back edge up and back; the opening angle to the base
    hinge = min(lid["verts"], key=lambda v: (round(v[2], 4), v[1]))
    top = max(lid["verts"], key=lambda v: (round(v[2], 4), -v[1]))
    up = (top[1] - hinge[1], top[2] - hinge[2])
    opening = math.degrees(math.acos((-up[0]) / math.hypot(*up)))   # between the base (towards -Y) and the lid
    assert 105.0 <= opening <= 115.0
    assert screen["key"] == "screen" and by["bezel"]["key"] == "dark" and lid["key"] == base["key"] == "steel"
    # the screen lies on the lid's inner face, towards the user (-Y)
    mean = lambda part, k: sum(v[k] for v in part["verts"]) / len(part["verts"])    # noqa: E731
    assert mean(screen, 1) < mean(lid, 1) and by["keys"]["key"] == by["trackpad"]["key"] == "dark"
    # the monitor's screen on the front of its panel, the keys above the keyboard's plate
    mon = {p["role"]: p for p in P.decor_parts("monitor", *TT.MONITOR_SIZE)}
    assert min(v[1] for v in mon["screen"]["verts"]) < min(v[1] for v in mon["panel_back"]["verts"])
    assert min(v[2] for v in mon["foot"]["verts"]) == 0.0
    kb = P.decor_parts("keyboard", *TT.KEYBOARD_SIZE)
    plate = max(v[2] for p in kb if p["role"] == "base" for v in p["verts"])
    assert all(min(v[2] for v in p["verts"]) >= plate - 1e-9 for p in kb if p["role"] in ("key", "space_bar"))
    assert sum(1 for p in kb if p["role"] == "space_bar") == 1 and sum(1 for p in kb if p["role"] == "key") >= 60


def test_the_screen_is_dark_glass_with_a_faint_lit_wallpaper():
    from wenart.blender import lighting as LI
    from wenart.blender import materials as M

    assert max(M.SCREEN_BASE_RGB) < 0.02 and M.SCREEN_ROUGHNESS <= 0.1          # a switched-off panel: dark, glossy
    brightest = max(max(rgb) for _pos, rgb in M.SCREEN_WALLPAPER) * M.SCREEN_EMISSION
    assert 0.05 <= brightest <= LI.SHADE_EMISSION_WM2SR / 4.0                     # lit, never a lamp
    assert [pos for pos, _rgb in M.SCREEN_WALLPAPER] == sorted(pos for pos, _rgb in M.SCREEN_WALLPAPER)
    assert len({rgb for _pos, rgb in M.SCREEN_WALLPAPER}) == len(M.SCREEN_WALLPAPER)   # an image, not one colour


# ------------------------------------------------------------------------------------------------- the placement
@pytest.mark.parametrize("rot", [0.0, 90.0, 180.0, 270.0])
def test_every_desk_gets_a_laptop_facing_its_chair(rot):
    b, room, pieces = _desk_room(rot)
    desk, chair = pieces
    made = TT.dress_tops(room, pieces, b, [], _new_id())
    laptops = [i for i in made if i["type"] == "laptop"]
    assert len(laptops) == 1 and not [i for i in made if i["type"] in ("monitor", "keyboard")]
    lap = laptops[0]
    assert lap["host_id"] == desk["id"] and lap["slot"] == f"{desk['id']}.work"
    assert lap["source"] == "added_by_ai" and lap["method"] == "rule" and TT.WORK_REASON_TAG in lap["reason"]
    assert lap["work_set"] == {"set": lap["work_set"]["set"], "user_side": "-y", "seat_id": chair["id"]}
    assert _faces(lap, chair["footprint"]["center"]) > 0.99                 # its screen and keyboard face the chair
    assert lap["rotation_deg"] == pytest.approx(rot)
    box = TT.local_box(desk, lap)
    assert TT.inside_top(desk, box)
    assert box[1] - box[3] / 2.0 == pytest.approx(-DESK[1] / 2.0 + TT.WORK_EDGE_M, abs=0.002)   # at the chair's edge
    assert abs(box[0]) < 0.002                                                # centred on the chair
    others = [TT.local_box(desk, i) for i in made if i is not lap and i["host_id"] == desk["id"]]
    assert others and all(TT.boxes_clear(box, o) for o in others)           # books beside it, in the side strip


def test_the_seat_side_turns_the_set_and_a_desk_without_a_seat_gets_it_at_its_front():
    b, room, pieces = _desk_room(0.0, chair_side="end", size=(1.4, 0.7))
    desk, chair = pieces
    lap = next(i for i in TT.dress_tops(room, pieces, b, [], _new_id()) if i["type"] == "laptop")
    assert lap["work_set"]["user_side"] == "+x" and lap["rotation_deg"] == pytest.approx(90.0)
    assert _faces(lap, chair["footprint"]["center"]) > 0.99
    lx, _ly = TT._local(desk, *lap["center"])
    assert lx > 0.4                                                           # at the end the user sits at
    b, room, pieces = _desk_room(90.0, chair=False)
    lap = next(i for i in TT.dress_tops(room, pieces, b, [], _new_id()) if i["type"] == "laptop")
    assert lap["work_set"]["seat_id"] is None and lap["work_set"]["user_side"] == "-y"
    assert lap["rotation_deg"] == pytest.approx(90.0) and "no seat" in lap["reason"]


def test_decor_on_the_desk_makes_room_else_it_is_left_out_and_listed():
    b, room, pieces = _desk_room(0.0)
    desk = pieces[0]
    books = {"id": "dec_L0_100", "type": "book_set", "host_id": desk["id"], "center": TT._world(desk, 0.0, -0.05),
             "rotation_deg": 0.0, "size": [0.25, 0.18, 0.22]}
    items = [books]
    made = TT.dress_tops(room, pieces, b, items, _new_id())
    lap = next(i for i in made if i["type"] == "laptop")
    assert books["moved_for"]["slot"] == f"{desk['id']}.work" and books["moved_for"]["from"] == TT._world(desk, 0, -0.05)
    boxes = [TT.local_box(desk, i) for i in items + made]
    assert all(TT.inside_top(desk, x) for x in boxes)
    assert all(TT.boxes_clear(a, c) for k, a in enumerate(boxes) for c in boxes[k + 1:])
    assert abs(TT._local(desk, *lap["center"])[0]) < 0.002                   # the laptop keeps the chair's place
    # a small desk with no free place left for a big tray: the tray is left out and listed with the reason
    b, room, pieces = _desk_room(0.0, size=(0.6, 0.45))
    desk = pieces[0]
    tray = {"id": "dec_L0_101", "type": "tray", "host_id": desk["id"], "center": TT._world(desk, 0.0, 0.0),
            "rotation_deg": 0.0, "size": [0.4, 0.28, 0.05]}
    items = [tray]
    made = TT.dress_tops(room, pieces, b, items, _new_id())
    assert any(i["type"] == "laptop" for i in made) and tray not in items
    assert [x["id"] for x in b["decor_dropped"]] == ["dec_L0_101"] and TT.WORK_REASON_TAG in b["decor_dropped"][0][
        "reason"]
    # a desk that holds its work set already gets no second one
    b, room, pieces = _desk_room(0.0)
    first = TT.dress_tops(room, pieces, b, [], _new_id())
    again = TT.dress_tops(room, pieces, b, first, _new_id())
    assert not [i for i in again if i["type"] in TT.WORK_TYPES]


def test_a_home_office_desk_gets_a_monitor_a_keyboard_and_a_mouse():
    b, room, pieces = _desk_room(0.0, room_type="other", size=(1.4, 0.7), label="Çalışma Odası")
    desk, chair = pieces
    assert TT.home_office(room, pieces)
    made = TT.dress_tops(room, pieces, b, [], _new_id())
    work = {i["type"]: i for i in made if i["type"] in TT.WORK_TYPES}
    assert set(work) == {"monitor", "keyboard", "computer_mouse"}
    loc = {t: TT._local(desk, *i["center"]) for t, i in work.items()}
    assert loc["monitor"][1] > loc["keyboard"][1]                            # the monitor behind the keyboard
    assert loc["computer_mouse"][0] > loc["keyboard"][0] + TT.KEYBOARD_SIZE[0] / 2.0   # the mouse at the user's right
    assert all(_faces(work[t], chair["footprint"]["center"]) > 0.95 for t in ("monitor", "keyboard"))
    assert len({i["rotation_deg"] for i in work.values()}) == 1                # the set turned as one, to the user
    assert loc["monitor"][1] - (-0.35) <= TT.MONITOR_REACH_M + 1e-6
    # a long desk used from its end: the monitor stays within reading distance, not at the far end
    b, room, pieces = _desk_room(0.0, room_type="other", size=(1.6, 0.7), label="Office", chair_side="end")
    mon = next(i for i in TT.dress_tops(room, pieces, b, [], _new_id()) if i["type"] == "monitor")
    assert 0.8 - TT._local(pieces[0], *mon["center"])[0] <= TT.MONITOR_REACH_M + 1e-6
    # a bedroom's desk (no home office) gets the laptop
    b, room, pieces = _desk_room(0.0, size=(1.4, 0.7))
    assert not TT.home_office(room, pieces)
    assert {i["type"] for i in TT.dress_tops(room, pieces, b, [], _new_id())} & set(TT.WORK_TYPES) == {"laptop"}


def test_under_a_window_the_laptop_rises_over_the_sill_but_no_monitor_does():
    b, room, pieces = _desk_room(0.0, room_type="other", size=(1.4, 0.7), label="Office",
                                 windows=(("win1", "n", 2.0, 1.2),))
    under_ceiling, under_sill = DA.top_room(pieces[0], room, b)
    assert under_sill == pytest.approx(0.9 - 0.75) and under_ceiling > 1.5
    made = TT.dress_tops(room, pieces, b, [], _new_id())
    work = [i for i in made if i["type"] in TT.WORK_TYPES]
    assert [i["type"] for i in work] == ["laptop"]                           # a monitor would cover the window
    assert "over the sill" in work[0]["reason"] and work[0]["size"][2] <= under_sill + TT.WORK_SILL_OVER_M
    b["openings"][0]["sill_height"] = 0.8                                     # 5 cm over the top: nothing fits
    notes: list = []
    made = TT.dress_tops(room, pieces, b, [], _new_id(), notes=notes)
    assert not [i for i in made if i["type"] in TT.WORK_TYPES]
    assert notes and "no work set fits" in notes[0] and "a window behind it" in notes[0]


def test_writing_tables_take_the_set_and_dining_tables_keep_their_plates():
    b = room_building(5.0, 4.0, "living", furniture=[("table_dining", (2.5, 3.6), 0.0, (1.2, 0.6)),
                                                     ("office_chair", (2.5, 2.95), 180.0, (0.6, 0.6)),
                                                     ("table_dining", (2.5, 1.5), 0.0, (1.6, 0.9)),
                                                     ("chair", (2.1, 0.75), 0.0, (0.45, 0.5)),
                                                     ("chair", (2.9, 0.75), 0.0, (0.45, 0.5))])
    room, pieces = b["rooms"][0], b["furniture"]
    assert [p["id"] for p in TT.work_hosts(room, pieces)] == ["f_L0_001"]   # the table with the office chair
    made = TT.dress_tops(room, pieces, b, [], _new_id())
    on = lambda hid: {i["type"] for i in made if i["host_id"] == hid}       # noqa: E731
    assert "laptop" in on("f_L0_001") and not on("f_L0_001") & {"plate", "glass"}
    assert "plate" in on("f_L0_003") and not on("f_L0_003") & set(TT.WORK_TYPES)
    # a home office without a desk: its table with one chair is the writing table; outdoors no work set at all
    b = room_building(4.0, 3.5, "other", furniture=[("table_dining", (2.0, 3.0), 0.0, (1.2, 0.7)),
                                                    ("chair", (2.0, 2.3), 180.0, (0.45, 0.5))])
    b["rooms"][0]["label"] = "Study"
    assert [p["id"] for p in TT.work_hosts(b["rooms"][0], b["furniture"])] == ["f_L0_001"]
    b, room, pieces = _desk_room(0.0, room_type="balcony")
    assert TT.work_hosts(room, pieces) == []


def test_the_decor_stage_dresses_every_desk_whatever_way_the_room_is_dressed():
    for brief in (None, {"decor": "rules"}):
        b, room, pieces = _desk_room(0.0)
        if brief:
            b["project"]["brief"] = brief
        out, records = DA.apply(b, "modern", {"answers": {}})
        work = [d for d in out["decor"] if d["type"] in TT.WORK_TYPES]
        assert [d["type"] for d in work] == ["laptop"] and work[0]["host_id"] == pieces[0]["id"], brief
        assert isinstance(work[0].get("host_frame"), dict) and work[0]["host_frame"]["support"] == "top"
        assert work[0]["host_frame"]["turn_deg"] == pytest.approx(0.0)
    b, room, pieces = _desk_room(0.0)
    b["project"]["brief"] = {"decor": False}
    out, _records = DA.apply(b, "modern", {"answers": {}})
    assert out["decor"] == []


# ----------------------------------------------------------------------------------------- the decor follows a desk
def test_a_desk_the_solver_replaces_hands_its_decor_to_the_new_desk():
    b, room, pieces = _desk_room(0.0)
    for p in pieces:
        p["source"] = "added_by_ai"
    out, _records = DA.apply(b, "modern", {"answers": {}})
    desk = next(f for f in out["furniture"] if f["type"] == "desk")
    on_desk = [d for d in out["decor"] if d.get("host_id") == desk["id"]]
    assert any(d["type"] == "laptop" for d in on_desk)
    new_desk = copy.deepcopy(desk)
    new_desk["id"] = "f_L0_050"
    new_desk["footprint"] = {"center": [0.25, 1.75], "size": [1.2, 0.6], "rotation_deg": 270.0}
    new_chair = copy.deepcopy(next(f for f in out["furniture"] if f["type"] == "office_chair"))
    new_chair["id"] = "f_L0_051"
    new_chair["footprint"] = {"center": [0.95, 1.75], "size": [0.6, 0.6], "rotation_deg": 90.0}
    got = SV.apply_candidate(out, RID, {"kept_ids": [], "pieces": [new_desk, new_chair], "rugs": []})
    ids = {f["id"] for f in got["furniture"]}
    assert desk["id"] not in ids
    moved = [d for d in got["decor"] if (d.get("handed_over") or {}).get("from") == desk["id"]]
    assert {d["id"] for d in moved} == {d["id"] for d in on_desk}
    new_id = moved[0]["host_id"]
    assert new_id in ids and next(f for f in got["furniture"] if f["id"] == new_id)["type"] == "desk"
    synced = D.sync_to_hosts(got)
    lap = next(d for d in synced["decor"] if d["type"] == "laptop")
    host = next(f for f in synced["furniture"] if f["id"] == new_id)
    assert TT.inside_top(host, TT.local_box(host, lap), 0.0)                  # on the new desk, as on the old one
    assert lap["rotation_deg"] == pytest.approx(270.0)                         # still facing the desk's front
    # no piece of its type in the candidate: the decor goes with its piece, as before
    got = SV.apply_candidate(out, RID, {"kept_ids": [], "pieces": [new_chair], "rugs": []})
    assert not [d for d in got["decor"] if d.get("host_id") == desk["id"]]


def test_successors_pair_each_gone_piece_with_the_nearest_new_one_of_its_type():
    gone = [{"id": "a", "type": "nightstand", "room_id": "r", "footprint": {"center": [0, 0]}},
            {"id": "b", "type": "nightstand", "room_id": "r", "footprint": {"center": [3, 0]}},
            {"id": "c", "type": "desk", "room_id": "r", "footprint": {"center": [5, 5]}}]
    new = [{"id": "x", "type": "nightstand", "room_id": "r", "footprint": {"center": [2.8, 0.1]}},
           {"id": "y", "type": "nightstand", "room_id": "r", "footprint": {"center": [0.3, 0]}},
           {"id": "z", "type": "desk", "room_id": "other", "footprint": {"center": [5, 5]}}]
    assert HO.successors(gone, new) == {"a": "y", "b": "x"}                 # same type, same room, nearest first


# ----------------------------------------------------------------------------------------------------- Argus U17
def test_argus_flags_a_bare_desk_and_the_line_knows_the_check():
    b, room, pieces = _desk_room(0.0)
    got = LS.bare_desks(b)
    assert [f["check"] for f in got] == ["U17"] and got[0]["target"] == pieces[0]["id"]
    assert got[0]["evidence"]["lesson"] == "UL93" and got[0]["kind"] == "taste" and got[0]["line"] == "lessons"
    assert "laptop" in got[0]["message"] and got[0]["evidence"]["seat"] == pieces[1]["id"]
    b["decor"] = [dict(i, id=f"dec_L0_{k:03d}") for k, i in enumerate(TT.dress_tops(room, pieces, b, [], _new_id()))]
    assert LS.bare_desks(b) == []
    b["decor"] = []
    b["project"]["brief"] = {"decor": False}
    assert LS.bare_desks(b) == []                                             # the brief switched decor off
    res = LS.audit(_desk_room(0.0)[0])
    assert res["checked"]["U17"] == 1 and any(f["check"] == "U17" for f in res["findings"])
    assert "U17" in dict(LS.BUILDING_CHECKS) and LS.CHECK_LESSONS["U17"] == ("UL93",)
    assert K.CHECK_KIND["U17"] == "taste" and K.kind_of({"check": "U17", "line": "lessons"}) == "taste"
    assert LS.coverage()["UL93"]["code"] == ["U17"]
    assert "laptop" in AP.CHECKLIST["Q15"]["what"]                         # the inspector asks for it too
