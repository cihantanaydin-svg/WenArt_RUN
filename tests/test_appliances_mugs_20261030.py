"""UL212 and UL213 (30 Oct 2026, user on real06 run 20261029-100801-full): "Try to improve the plain small item models
more maybe kitchen needs a kettle a coffee machine etc, or study rooms requires some other items, model them as much
detail as you can"; "coffee mugs around the house also is a good decor item book and on top of a book coffee mug".

Every project's kitchen appliances (a kettle, an espresso or a bean-to-cup machine, a toaster, a microwave, a knife
block, salt and pepper mills) and a desk's organiser set are real products in the style family's finish
(``wenart.blender.appliance_parts``), placed by kitchen logic (``decor.kitchen_worktop_decor``) and on wide desks
(``tabletop.desk_extras``); a few coffee mugs stand around the house (``wenart.furniture.mugs``,
``wenart.blender.mug_parts``): on books by a seat, by a laptop, beside a bedside book, a pair by the coffee machine.
CPU only."""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import pytest

import _m11_room as M
from wenart.blender import appliance_parts as AP
from wenart.blender import furniture as F
from wenart.blender import mug_parts as MG
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import small_parts as SM
from wenart.furniture import decor as D
from wenart.furniture import mugs as MU
from wenart.furniture import tabletop as TT

ROOT = Path(__file__).resolve().parents[1]
SIZES = {"kettle": (0.22, 0.16, 0.25), "coffee_machine": (0.24, 0.38, 0.35), "toaster": (0.28, 0.17, 0.19),
         "microwave": (0.46, 0.36, 0.27), "knife_block": (0.12, 0.20, 0.33), "pepper_mills": (0.14, 0.07, 0.22),
         "desk_organiser": TT.ORGANISER_SIZE}


def _closed(part) -> bool:
    """Every edge used once in each direction: a closed, consistently wound mesh."""
    edges = Counter((f[i], f[(i + 1) % len(f)]) for f in part["faces"] for i in range(len(f)))
    return all(n == 1 and edges[(b, a)] == 1 for (a, b), n in edges.items())


def _check(parts, box, closed=True):
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 <= box[0] + 1e-6 and y1 - y0 <= box[1] + 1e-6 and z1 - z0 <= box[2] + 1e-6
    assert abs(z0) < 1e-9 and abs(x0 + x1) <= box[0] + 1e-6
    keys, _assumed = F.style_material_keys({"floor": {"material": "wood_oak_light"}})
    plain = {P.plain_key(p["key"]) for p in parts}
    assert plain <= set(P.MATERIAL_KEYS) and plain <= set(keys)
    assert all(SM.signed_volume(p) > 0 for p in parts)                       # wound outwards
    if closed:
        assert all(_closed(p) for p in parts), [p["role"] for p in parts if not _closed(p)]


def _roles(parts) -> Counter:
    return Counter(p["role"] for p in parts)


# --------------------------------------------------------------------------
# UL212: the appliances and the desk set as real products
# --------------------------------------------------------------------------

@pytest.mark.parametrize("family", sorted(AP.FAMILY_FINISH) + [None])
@pytest.mark.parametrize("dtype", sorted(SIZES))
def test_every_appliance_is_a_real_product_in_its_box_in_every_family(dtype, family):
    box = SIZES[dtype]
    parts = P.decor_parts(dtype, *box, {"appliance": AP.record(family, dtype)})
    _check(parts, box)
    roles = _roles(parts)
    assert len(parts) >= 8 and sum(len(p["verts"]) for p in parts) < 2400
    if dtype == "kettle":
        assert {"base", "body", "lid", "spout", "spout_mouth", "handle", "switch", "window", "cord"} <= set(roles)
    elif dtype == "coffee_machine" and AP.finish(family)["coffee"] == "espresso":
        assert {"group_head", "portafilter", "portafilter_handle", "steam_wand", "gauge", "tray", "warmer"} \
            <= set(roles) and roles["grid"] >= 6 and roles["cup"] >= 2
    elif dtype == "coffee_machine":
        assert {"hopper_lid", "spout_unit", "display", "tray"} <= set(roles)
    elif dtype == "toaster":
        assert roles["slot"] == 2 and {"lever", "dial", "crumb_tray", "cord"} <= set(roles)
    elif dtype == "microwave":
        assert {"door", "window", "handle", "display", "dial"} <= set(roles) and roles["button"] >= 4
    elif dtype == "knife_block":
        assert roles["knife_handle"] >= 4 and roles["rivet"] >= 2 * roles["knife_handle"]
    elif dtype == "pepper_mills":
        assert roles["mill"] == 2 and roles["finial"] == 2
    else:
        assert roles["folder"] >= 4 and {"clock", "clock_face", "hand", "stapler", "pot", "leaf"} <= set(roles)


def test_the_finish_follows_the_style_family():
    assert AP.record("scandinavian", "kettle")["body"] == "ceramic"
    assert AP.record("scandinavian", "kettle")["grip"] == "wood"
    assert AP.record("modern", "toaster")["body"] == "steel"
    assert AP.finish("minimal")["coffee"] == "bean_to_cup" and AP.finish("modern")["coffee"] == "espresso"
    assert AP.record("classic", "kettle")["body"].startswith(P.ACCENT_PREFIX)
    # the decor stage records it, and a tinted body gets its colour
    item = D.appliance_record({"type": "kettle"}, "classic")
    assert item["appliance"]["lesson"] == "UL212" and item["colour"] == AP.finish("classic")["colour"]
    assert D.appliance_record({"type": "vase"}, "classic") == {"type": "vase"}
    station = D.appliance_record({"type": "coffee_station"}, "minimal")
    assert station["appliance"]["coffee"] == "bean_to_cup"
    # an unknown family takes the default
    assert AP.finish("baroque") == AP.finish(AP.DEFAULT_FAMILY)


def test_a_loop_handle_never_pinches():
    """SM.tube's ring frame turned half round where the path turned from steep to flat (a kettle's handle, a cup's):
    every ring now keeps the turn of the ring before it."""
    for parts in (AP.parts("kettle", *SIZES["kettle"]), MG.mug(0.0, 0.0, 0.0)):
        for p in parts:
            if p["role"] not in ("handle", "mug_handle"):
                continue
            sides = len(p["faces"][-1])
            rings = [p["verts"][k:k + sides] for k in range(0, len(p["verts"]), sides)]
            cen = [[sum(v[i] for v in r) / sides for i in range(3)] for r in rings]
            offs = [[r[0][i] - c[i] for i in range(3)] for r, c in zip(rings, cen)]
            assert all(sum(a * b for a, b in zip(u, v)) > 0.0 for u, v in zip(offs, offs[1:]))


def test_the_coffee_station_carries_the_familys_machine():
    from wenart.blender import kitchen_details as KD

    w, d, h = KD.STYLING_SIZES["coffee_station"]
    for family, role in (("modern", "group_head"), ("minimal", "hopper_lid")):
        parts = P.decor_parts("coffee_station", w, d, h, {"appliance": AP.record(family, "coffee_machine")})
        assert role in _roles(parts), family


def _kitchen(island: bool = False) -> dict:
    """4.0 x 3.0 m: run A (3.4 m) on the north wall with the sink, run B (2.4 m) on the east wall with the stove;
    an island in the middle."""
    def fp(pid, ftype, center, size, front, **kw):
        return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)

    pieces = [fp("kA", "kitchen_counter", (1.7, 2.7), (3.4, 0.6), 270.0),
              fp("kB", "kitchen_counter", (3.7, 1.5), (2.4, 0.6), 180.0),
              fp("sk", "sink_kitchen", (1.2, 2.7), (0.8, 0.5), 270.0),
              fp("st", "stove", (3.72, 1.2), (0.6, 0.55), 180.0)]
    if island:
        pieces.append(fp("is", "kitchen_island", (1.6, 1.2), (1.6, 0.9), 270.0))
    return M.building(w=4.0, h=3.0, room_type="kitchen", window=None, door_x=1.0, furniture=pieces)


def _worktop(b: dict) -> list[dict]:
    room = b["rooms"][0]
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{n[0]:03d}"

    return D.kitchen_worktop_decor(b, room, b["furniture"], new_id)


def test_the_worktop_gets_the_appliances_the_knife_block_and_the_mills_by_kitchen_logic():
    b = _kitchen(island=True)
    items = _worktop(b)
    types = [i["type"] for i in items]
    assert len(types) == len(set(types))                                     # one of each
    assert {"kettle", "coffee_machine", "knife_block"} <= set(types)
    room = b["rooms"][0]
    pieces = {p["id"]: p for p in b["furniture"]}
    for it in items:
        host = pieces[it["host_id"]]
        assert D.worktop_item_ok(it, host, b["furniture"], D.worktop_windows(host, b, room),
                                 [o for o in items if o is not it]) is None, it
        if it["type"] in D.NOT_ON_ISLAND_TYPES:
            assert host["type"] != "kitchen_island", it                     # against a splashback, never mid-island
        if it["type"] in AP.APPLIANCE_TYPES:
            assert it["appliance"]["lesson"] == "UL212" and it["reason"]
    # the knife block at the free spot nearest the hob when its turn comes (here the hob's run is full: the sink's)
    k = next(n for n, i in enumerate(items) if i["type"] == "knife_block")
    ctx = D._worktop_context(b, room, b["furniture"])
    cands = D._worktop_candidates(ctx, "knife_block", items[:k])
    assert cands and items[k]["center"] == cands[0][3]["center"]
    assert items[k]["host_id"] == "kB" or not any(c[1] == "kB" for c in cands)
    assert "hob" in items[k]["reason"] and len(items) <= D.KITCHEN_DECOR_MAX


def test_a_wide_desk_gets_the_organiser_set_a_narrow_one_a_note():
    for width, wanted in ((1.6, True), (1.0, False)):
        desk = M.fp("dk", "desk", (2.5, 3.6), (width, 0.7), rotation=180.0, front=90.0)
        chair = M.fp("ch", "office_chair", (2.5, 3.0), (0.6, 0.6), rotation=0.0)
        b = M.building(w=5.0, h=4.0, room_type="other", furniture=[desk, chair], window=None)
        room = b["rooms"][0]
        got = TT.work_set(room, desk, b["furniture"], [], 2.0, None, office=True)
        organisers = [i for i in got["items"] if i["type"] == "desk_organiser"]
        assert bool(organisers) == wanted, (width, got.get("notes"))
        for it in got["items"]:
            assert TT.inside_top(desk, TT.local_box(desk, it))
        boxes = [TT.local_box(desk, i) for i in got["items"]]
        assert all(TT.boxes_clear(a, c, 0.0) for k, a in enumerate(boxes) for c in boxes[k + 1:])
        if not wanted:
            assert any("no organiser set" in n for n in got.get("notes") or [])


# --------------------------------------------------------------------------
# UL213: the mugs
# --------------------------------------------------------------------------

def test_the_mug_is_a_real_ceramic_mug():
    parts = MG.mug(0.0, 0.0, 0.0, coffee=True)
    _check(parts, (0.12, 0.09, 0.097))
    body = next(p for p in parts if p["role"] == "mug")
    vs = body["verts"]
    m = MG.MUG
    # a foot ring: it stands on a ring, the base inside it recessed
    ground = [math.hypot(v[0], v[1]) for v in vs if abs(v[2]) < 1e-9]
    assert ground and min(ground) > m["foot_r"] - 0.007 and max(ground) <= m["foot_r"]
    assert min(v[2] for v in vs if math.hypot(v[0], v[1]) < 0.01) > 0.002
    # a slight taper (wider at the rim) and a rolled lip
    assert MG._r_at(m["h"] - 0.006) > MG._r_at(0.01) + 0.003
    assert max(math.hypot(v[0], v[1]) for v in vs) > m["r"]
    # a real loop handle: a finger's room between it and the body
    assert MG.handle_hole(parts) >= 0.02
    # the coffee a centimetre under the rim, inside the wall
    coffee = next(p for p in parts if p["role"] == "coffee")
    assert coffee["key"] == MG.COFFEE_KEY == "coffee"
    top = max(v[2] for v in coffee["verts"])
    assert 0.005 <= m["h"] - top <= 0.015
    assert max(math.hypot(v[0], v[1]) for v in coffee["verts"]) < MG.inner_r(top)
    assert sum(len(p["verts"]) for p in parts) < 1200
    assert "coffee" not in _roles(MG.mug(0.0, 0.0, 0.0, coffee=False))


@pytest.mark.parametrize("books,books_h", [(1, 0.035), (2, 0.07), (3, 0.12)])
def test_the_mug_on_books_stands_on_the_top_cover(books, books_h):
    item = {"type": "mug_on_books", "size": [0.25, 0.18, 0.0], "mug": {"books": books, "books_h": books_h,
                                                                     "coffee": True}}
    h = MU.books_height(item)
    parts = P.decor_parts("mug_on_books", 0.25, 0.18, h, item)
    _check(parts, (0.25, 0.18, h), closed=False)
    assert MG.on_cover(parts) is None
    cup = [p for p in parts if p["role"].startswith("mug")]
    assert cup and _roles(parts)["book"] >= books
    # the mug's foot on the cover: no book part reaches over it
    zt = min(v[2] for p in cup for v in p["verts"])
    assert max(v[2] for p in parts if not p["role"].startswith("mug") and p["role"] != "coffee"
               for v in p["verts"]) <= zt + 1e-9
    # a mug that would reach past the cover is checked
    moved = [dict(p, verts=[(x + 0.2, y, z) for x, y, z in p["verts"]]) if p["role"].startswith("mug") else p
             for p in parts]
    assert MG.on_cover(moved) == "the mug reaches past the top cover"


def test_the_pair_of_mugs_side_by_side_on_a_tray_or_one_behind_the_other():
    for size, rec in ((MU.PAIR_SIZE[True], {"tray": True}), (MU.PAIR_SIZE[False], {}), (MU.PAIR_DEEP, {})):
        parts = P.decor_parts("mug_pair", *size, {"mug": rec})
        _check(parts, size)
        roles = _roles(parts)
        assert roles["mug"] == 2 and roles["mug_handle"] == 2 and roles["coffee"] == 1
        assert ("tray" in {p["role"] for p in parts}) == bool(rec.get("tray")) or rec.get("tray")
        assert {p["key"] for p in parts if p["role"] == "mug"} == {MG.GLAZE_KEY, MG.WHITE_KEY}
        boxes = [P.parts_bbox([p]) for p in parts if p["role"] == "mug"]
        apart = boxes[0][3] <= boxes[1][0] + 1e-9 or boxes[1][3] <= boxes[0][0] + 1e-9 \
            or boxes[0][4] <= boxes[1][1] + 1e-9 or boxes[1][4] <= boxes[0][1] + 1e-9
        assert apart                                                          # two mugs, never one in the other


def _seat_room(books: bool = True, subtype=None) -> dict:
    sofa = M.fp("so", "sofa", (2.5, 3.4), (2.2, 0.9), rotation=180.0, front=270.0)
    table = M.fp("tc", "table_coffee", (2.5, 2.2), (1.1, 0.6), rotation=0.0, front=None)
    b = M.building(w=5.0, h=4.0, room_type="living", furniture=[sofa, table], window=None, subtype=subtype)
    if books:
        b["decor"].append({"id": "dec_L0_001", "kind": "decor", "type": "books", "level_id": "L0",
                           "room_id": M.ROOM_ID, "host_id": "tc", "center": [2.3, 2.2], "size": [0.25, 0.18, 0.12],
                           "rotation_deg": 0.0, "source": "added_by_ai", "method": "rule", "slot": "tc.group",
                           "reason": "a styled table coffee"})
    b["decor"].append({"id": "dec_L0_002", "kind": "decor", "type": "bowl", "level_id": "L0", "room_id": M.ROOM_ID,
                       "host_id": "tc", "center": [2.8, 2.2], "size": [0.32, 0.32, 0.12], "rotation_deg": 0.0,
                       "source": "added_by_ai", "method": "rule", "slot": "tc.group", "reason": "a bowl"})
    return b


def _ids():
    n = [10]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{n[0]:03d}"

    return new_id


def _top_checks(b: dict, item: dict) -> None:
    host = next(p for p in b["furniture"] if p["id"] == item["host_id"])
    box = TT.local_box(host, item)
    assert TT.inside_top(host, box, TT.TOP_MARGIN_M - MU.ROUND_TOL_M), item
    others = [TT.local_box(host, o) for o in b["decor"] if o is not item and o.get("host_id") == host["id"]]
    assert all(TT.boxes_clear(box, o) for o in others), item


def test_the_books_by_the_sofa_take_a_mug_of_coffee_on_their_cover():
    b = _seat_room()
    notes = MU.place_mugs(b, _ids(), family="scandinavian")
    item = next(d for d in b["decor"] if d["id"] == "dec_L0_001")
    assert item["type"] == "mug_on_books" and item["mug"]["was"]["type"] == "books"
    assert item["mug"]["coffee"] is True and item["colour"] == MU.FAMILY_GLAZE["scandinavian"]
    assert item["size"][:2] == [0.25, 0.18] and item["size"][2] == MU.books_height(item) > MG.MUG["h"] + 0.03
    assert MG.on_cover(P.decor_parts("mug_on_books", *item["size"], item)) is None
    assert item["reason"].endswith(f"({MU.REASON_TAG})") and any("take a mug" in n for n in notes)
    _top_checks(b, item)
    assert MU.place_mugs(b, _ids()) == []                                    # dressed once


def test_without_books_a_small_stack_with_its_mug_goes_to_a_free_spot():
    b = _seat_room(books=False)
    MU.place_mugs(b, _ids(), family="modern")
    item = next(d for d in b["decor"] if d["type"] == "mug_on_books")
    assert item["host_id"] == "tc" and item["mug"]["books"] == 2 and item["source"] == "added_by_ai"
    assert item["colour"] == MU.FAMILY_GLAZE["modern"]
    _top_checks(b, item)


def test_a_childs_room_gets_no_coffee_mug():
    b = _seat_room(subtype="child")
    assert MU.place_mugs(b, _ids()) == [] and not any(d["type"] in D.MUG_DECOR_TYPES for d in b["decor"])


def test_a_mug_of_coffee_by_the_laptop():
    desk = M.fp("dk", "desk", (2.5, 3.6), (1.4, 0.7), rotation=180.0, front=90.0)
    chair = M.fp("ch", "office_chair", (2.5, 3.0), (0.6, 0.6), rotation=0.0)
    b = M.building(w=5.0, h=4.0, room_type="other", furniture=[desk, chair], window=None)
    room = b["rooms"][0]
    got = TT.work_set(room, desk, b["furniture"], [], 2.0, None, office=False)
    new_id = _ids()
    for it in got["items"]:
        it["id"] = new_id("L0")
    b["decor"] += got["items"]
    MU.place_mugs(b, new_id)
    mug = next(d for d in b["decor"] if d["type"] == "mug")
    assert mug["host_id"] == "dk" and mug["mug"]["kind"] == "desk" and mug["mug"]["coffee"] is True
    _top_checks(b, mug)
    laptop = next(d for d in b["decor"] if d["type"] == "laptop")
    assert math.dist(mug["center"], laptop["center"]) < 0.6                  # by the laptop
    assert R.support_of("mug", "desk") == "top" and R.floor_class_problem("mug")


def test_a_mug_beside_the_bedside_book_else_on_a_book_of_its_own():
    for with_books in (True, False):
        bed = M.fp("bd", "bed_double", (2.5, 2.9), (1.6, 2.0), rotation=180.0, front=270.0)
        ns = M.fp("ns", "nightstand", (1.35, 3.6), (0.5, 0.45), rotation=180.0, front=270.0)
        b = M.building(w=5.0, h=4.0, room_type="bedroom", furniture=[bed, ns], window=None)
        if with_books:
            b["decor"].append({"id": "dec_L0_001", "kind": "decor", "type": "books", "level_id": "L0",
                               "room_id": M.ROOM_ID, "host_id": "ns", "center": [1.25, 3.6],
                               "size": [0.22, 0.16, 0.10], "rotation_deg": 180.0, "source": "added_by_ai",
                               "method": "rule", "slot": "ns.group", "reason": "books"})
        MU.place_mugs(b, _ids(), family="japandi")
        mug = next(d for d in b["decor"] if d["type"] in ("mug", "mug_on_books"))
        assert mug["host_id"] == "ns" and mug["mug"]["kind"] == "bedside" and mug["mug"]["coffee"] is False
        assert mug["type"] == ("mug" if with_books else "mug_on_books")
        _top_checks(b, mug)


def test_a_pair_of_mugs_by_the_coffee_machine():
    b = _kitchen()
    items = _worktop(b)
    b["decor"] = items
    machine = next(i for i in items if i["type"] == "coffee_machine")
    notes = MU.place_mugs(b, _ids(), family="scandinavian")
    pair = next(d for d in b["decor"] if d["type"] == "mug_pair")
    assert pair["mug"]["tray"] is True and pair["mug"]["beside"] == machine["id"]
    assert math.dist(pair["center"], machine["center"]) <= MU.PAIR_REACH_M + 1e-9
    host = next(p for p in b["furniture"] if p["id"] == pair["host_id"])
    room = b["rooms"][0]
    assert D.worktop_item_ok(pair, host, b["furniture"], D.worktop_windows(host, b, room),
                             [o for o in b["decor"] if o is not pair]) is None
    assert any("mug_pair" in n for n in notes)


def test_a_few_mugs_per_house_one_per_room():
    assert MU.MUGS_MAX <= 4 and MU.KINDS == ("kitchen", "seat", "desk", "bedside")
    b = _seat_room()
    MU.place_mugs(b, _ids())
    assert sum(1 for d in b["decor"] if d["type"] in D.MUG_DECOR_TYPES) == 1      # one room: one place


def test_the_new_types_are_known_everywhere():
    from wenart.polish import prompt as PR
    from wenart.vision_check import prompts as VP

    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    enum = schema["$defs"]["decor"]["properties"]["type"]["enum"]
    for t in ("knife_block", "pepper_mills", "desk_organiser") + D.MUG_DECOR_TYPES:
        assert t in P.DECOR_TYPES and t in D.DECOR_TYPES and t in P.SURFACE_DECOR_TYPES, t
        assert t in R.TABLETOP_TYPES and t in enum, t
        assert t in PR.DECOR_WORDS and len(VP.HINTS[t].split()) >= 3, t
        assert t in P.DECOR_DEFAULT_HEIGHT, t
    assert MU.MUG_SIZE[2] >= MG.MUG["h"] and MU.MUG_SIZE[0] >= MG.mug_extent()[2] - MG.mug_extent()[0]


def test_an_appliance_the_refit_covers_with_a_tall_unit_slides_along_its_run():
    """UL212 (real04 replay: the coffee machine and the kettle stood where the refit planned the fridge column and the
    oven tower, so the build left them out): the build slides such an item to the nearest free spot of its run
    (``furniture`` build loop: ``kitchen_details.item_blocked``, then ``modules.slide_worktop_item``)."""
    from wenart.blender import kitchen_details as KD
    from wenart.blender import modules as MOD
    host = {"id": "kA", "type": "kitchen_counter",
            "footprint": {"center": [2.0, 0.3], "size": [4.0, 0.6], "rotation_deg": 0.0},
            "asset": {"module_plan": {"builder": "kitchen_run", "footprint_m": [4.0, 0.6], "modules": [
                {"kind": "tall_unit", "pos_m": [1.7, 0.0], "size_m": [0.6, 0.6], "front": "fridge"},
                {"kind": "worktop", "cutouts": [{"kind": "hob", "x_m": 0.0, "w_m": 0.6}]}]}}}
    item = {"id": "dec_cm", "type": "coffee_machine", "host_id": "kA", "center": [3.7, 0.3],
            "size": [0.30, 0.40, 0.38], "rotation_deg": 0.0, "level_id": "L0"}
    assert KD.item_blocked(item, host) is not None                           # in the fridge column
    building = {"openings": [], "walls": [], "levels": [{"id": "L0", "elevation": 0.0}]}
    slid = MOD.slide_worktop_item(item, host, building, [])
    assert slid is not None and KD.item_blocked(slid, host) is None
    x = slid["center"][0] - 2.0                                              # local, along the run
    assert x + 0.15 <= 1.4 + 1e-6 and (x - 0.15 >= 0.3 + MOD.WORKTOP_HOB_CLEAR_M - 1e-6
                                       or x + 0.15 <= -0.3 - MOD.WORKTOP_HOB_CLEAR_M + 1e-6)
    src = (__import__("pathlib").Path(__file__).resolve().parents[1] / "wenart" / "blender" / "furniture.py").read_text()
    assert "slid along {host['id']}: {planned}" in src                      # the build wires it


def test_a_coffee_station_with_no_room_left_takes_its_compact_form():
    from wenart.blender import kitchen_details as KD
    from wenart.furniture import decor as D
    for big, (small, box) in KD.COMPACT_FORMS.items():
        assert tuple(D.KITCHEN_DECOR_SIZES[small]) == box and box[0] < D.KITCHEN_DECOR_SIZES[big][0]
    it = KD.compact_form({"id": "c", "type": "coffee_station", "size": [0.5, 0.38, 0.38], "host_frame": {}})
    assert it["type"] == "coffee_machine" and it["size"] == [0.24, 0.38, 0.35] and it["compact_of"] == "coffee_station"
    assert "host_frame" not in it and KD.compact_form({"type": "kettle"}) is None
