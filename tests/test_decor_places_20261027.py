"""27 Oct 2026 (run 160846 on real06: the salon's recipe wanted wall art and plants, yet the only art place was above
the sofa, where a window left 0.00 m, and no plant place passed): art on any free wall (``decor.free_wall_art``), plants
along the walls beside the seating or a window (``decor_ai.wall_spots``), and a plant fails the walkway check only for a
walkway it blocks itself."""
from __future__ import annotations

from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import placer

from test_decor_m8 import RID, room_building


def _room(furniture, doors=(("d1", "w", 2.5, 0.9),), windows=(("win1", "s", 3.0, 2.4),)):
    b = room_building(6.0, 5.0, "living", furniture=furniture, doors=doors, windows=windows)
    room = b["rooms"][0]
    return b, room, [f for f in b["furniture"] if f["room_id"] == RID]


def test_art_hangs_on_a_free_wall_when_the_wall_behind_the_sofa_has_a_window():
    b, room, pieces = _room([("sofa", (3.0, 0.45), 180.0, (2.2, 0.9)),
                             ("wardrobe", (5.7, 2.5), 90.0, (2.0, 0.6))])
    ctx = placer.room_context(b, room)
    level = b["levels"][0]
    item, why = D.wall_art_for_host(pieces[0], ctx, b, level)
    assert item is None and "win1" in why
    art = D.free_wall_art(room, pieces, b, ctx, level)
    assert len(art) == 2 and all(a["free_wall"] and "anchor_ids" not in a for a in art)
    first = art[0]
    assert abs(first["wall_point"][1] - 5.0) < 1e-6                     # the north wall: the longest free stretch
    assert D.WALL_ART_MIN_W <= first["size"][0] <= D.WALL_ART_MAX_W and first["bottom_m"] >= D.FREE_WALL_ART_BOTTOM_M
    assert first["max_height_m"] >= D.WALL_ART_MIN_H and first["rotation_deg"] is not None
    for a in art:
        x, y = a["wall_point"]
        assert not (abs(y) < 1e-6 and abs(x - 3.0) < 1.2 + D.OPENING_MARGIN_M)          # never on the window
        assert not (abs(x - 6.0) < 1e-6 and abs(y - 2.5) < 1.0 + a["size"][0] / 2.0)   # never behind the wardrobe
        assert not (abs(x) < 1e-6 and abs(y - 2.5) < 0.45 + a["size"][0] / 2.0)        # never on the door
    assert len({(round(a["wall_point"][0], 2) if abs(a["wall_point"][0]) in (0.0, 6.0) else None,
                 round(a["wall_point"][1], 2) if abs(a["wall_point"][1]) in (0.0, 5.0) else None) for a in art}) == 2
    # the slots offer it, and the schema takes it without a piece to hang over
    slots, _notes = DA.room_slots(room, pieces, b)
    walls = [s for s in slots if s.id.startswith(f"{RID}.wall")]
    assert len(walls) == 2 and all(s.kind == "wall" and s.types == ("wall_art",) for s in walls)


def test_a_low_piece_in_front_raises_the_picture():
    b, room, pieces = _room([("sideboard", (3.0, 4.8), 0.0, (1.6, 0.4))], windows=())
    art = D.free_wall_art(room, pieces, b)
    north = next(a for a in art if abs(a["wall_point"][1] - 5.0) < 1e-6)
    top = D.placer_bbox_height(pieces[0])
    assert north["bottom_m"] >= max(D.FREE_WALL_ART_BOTTOM_M, top + D.WALL_ART_GAP_M) - 1e-9


def test_a_plant_stands_beside_the_sofa_when_the_corners_are_taken():
    corners = [("armchair", (0.45, 0.45), 0.0, (0.8, 0.8)), ("armchair", (5.55, 0.45), 0.0, (0.8, 0.8)),
               ("armchair", (5.55, 4.55), 0.0, (0.8, 0.8)), ("armchair", (0.45, 4.55), 0.0, (0.8, 0.8))]
    b, room, pieces = _room([("sofa", (3.0, 4.55), 0.0, (2.0, 0.9))] + corners, windows=())
    ctx = placer.room_context(b, room)
    assert DA.free_corners(room, pieces, b, ctx) == []
    spots = DA.wall_spots(room, pieces, b, ctx, [])
    assert spots
    seats = [tuple(p["footprint"]["center"]) for p in pieces]
    near = min(((spots[0][0] - x) ** 2 + (spots[0][1] - y) ** 2) ** 0.5 for x, y in seats)
    assert near <= DA.PLANT_BESIDE_M + 0.9                          # beside a seat first (the sofa or an armchair)
    for i, a in enumerate(spots):
        for c in spots[i + 1:]:
            assert ((a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2) ** 0.5 >= DA.PLANT_SPACING_M - 1e-9
    made = DA.floor_items(room, pieces, b, ctx, {"plant", "plant_large"}, 2.7)
    assert made and made[0][0] == f"{RID}.floor1" and "beside the seating" in made[0][1]["plant"]["reason"]


def test_a_walkway_blocked_before_the_plant_is_no_reason_against_it(monkeypatch):
    b, room, pieces = _room([("sofa", (3.0, 0.45), 180.0, (2.2, 0.9))])
    ctx = placer.room_context(b, room)
    old = ("door", "d1", "window", "win1")
    monkeypatch.setattr(placer, "walkway_failures", lambda ps, c: [old])
    assert DA.free_corners(room, pieces, b, ctx)                     # the old block stays a layout finding
    monkeypatch.setattr(placer, "walkway_failures",
                        lambda ps, c: [old] + ([("door", "d1", "plant", "x")] if any(p.type == "plant" for p in ps)
                                               else []))
    assert DA.free_corners(room, pieces, b, ctx) == []               # a block the plant makes itself
