"""Milestone 8 decor (docs/milestone8.md §4; wenart/furniture/decor.py): rugs under the sofa + coffee table group,
the lower two thirds of a double bed and dining tables, wall art above a sofa, a bed's headboard or a dresser,
on hand-made rooms (exact geometry) and the synthetic buildings; the building schema of decor; and how the
scene's consumers treat rugs and wall art (decor elements, never furniture): views, the vision check
categories, the detector groups and the camera search.
"""
from __future__ import annotations

import copy
import json
import math

import jsonschema
import numpy as np
import pytest
from shapely.geometry import LineString, Point, Polygon

from wenart import building as B
from wenart.furniture import decor as D
from wenart.furniture import placer as PL

from conftest import load_truth

RID = "r_L0_room"
EV = [{"file": "x.dxf", "method": "vector", "confidence": 1.0}]


def room_building(width: float = 6.0, depth: float = 5.0, room_type: str = "living", furniture=(), doors=(),
                  windows=(), ceiling: float = 2.7, brief=None) -> dict:
    """One ``width x depth`` room (inner faces x in [0, width], y in [0, depth], walls 0.2 m). ``furniture``:
    (type, centre, rotation, size[, status]); ``doors`` / ``windows``: (id, wall s/e/n/w, along, width[,
    swing into this room])."""
    t = 0.2
    h = t / 2
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-t, -h], "end": [width + t, -h], "thickness": t},
        {"id": "w_e", "level_id": "L0", "start": [width + h, -t], "end": [width + h, depth + t], "thickness": t},
        {"id": "w_n", "level_id": "L0", "start": [width + t, depth + h], "end": [-t, depth + h], "thickness": t},
        {"id": "w_w", "level_id": "L0", "start": [-h, depth + t], "end": [-h, -t], "thickness": t},
    ]
    where = {"s": lambda a: [a, -h], "e": lambda a: [width + h, a], "n": lambda a: [a, depth + h],
             "w": lambda a: [-h, a]}
    b = B.empty_building("t", "t", "0")
    if brief is not None:
        b["project"]["brief"] = brief
    b["levels"] = [{"id": "L0", "label": "L0", "order": 0, "elevation": 0.0, "ceiling_height": ceiling,
                    "ceiling_height_source": "assumed_default", "evidence": []}]
    b["walls"] = [dict(w, status="verified", evidence=EV, exterior=True) for w in walls]
    for oid, wall, along, w, *swing in doors:
        b["openings"].append({"id": oid, "type": "door", "level_id": "L0", "wall_id": f"w_{wall}",
                              "center": where[wall](along), "width": w, "height": None, "sill_height": None,
                              "swing_side": RID if (swing and swing[0]) else "r_other", "status": "verified",
                              "evidence": EV})
    for oid, wall, along, w in windows:
        b["openings"].append({"id": oid, "type": "window", "level_id": "L0", "wall_id": f"w_{wall}",
                              "center": where[wall](along), "width": w, "height": None, "sill_height": 0.9,
                              "status": "verified", "evidence": EV})
    b["rooms"] = [{"id": RID, "level_id": "L0", "label": "Room", "room_type": room_type,
                   "polygon": [[0, 0], [width, 0], [width, depth], [0, depth]], "area_computed": width * depth,
                   "has_documented_furniture": True, "status": "verified", "evidence": EV}]
    for i, (ftype, center, rot, size, *status) in enumerate(furniture, 1):
        b["furniture"].append({"id": f"f_L0_{i:03d}", "level_id": "L0", "room_id": RID, "type": ftype,
                               "type_raw": None, "source": "from_documents",
                               "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
                               "front_deg": (270 + rot) % 360, "height": None, "asset": None,
                               "status": status[0] if status else "verified", "evidence": EV})
    B.validate(b)
    return b


def of_type(out: dict, dtype: str) -> list[dict]:
    return [d for d in out["decor"] if d["type"] == dtype]


def local_box(item: dict, frame: dict) -> tuple[float, float, float, float]:
    """The rug's corners in the frame of a piece (``frame``: its footprint): (x0, y0, x1, y1)."""
    fp = frame["footprint"]
    poly = D._to_local(D.rug_polygon(item), fp["center"], fp["rotation_deg"])
    return tuple(round(v, 3) for v in poly.bounds)


# Living room 6 x 5: sofa against the north wall (rotation 0: back = local +Y = north, facing south), coffee
# table in front.
SOFA = ("sofa", (3.0, 4.53), 0.0, (2.2, 0.9))
TABLE = ("table_coffee", (3.0, 3.38), 0.0, (1.2, 0.6))


# --------------------------------------------------------------------------
# Rugs
# --------------------------------------------------------------------------

def test_living_rug_covers_the_sofa_and_coffee_table_group_grown_by_the_margin():
    out, rows = D.add_decor(room_building(furniture=[SOFA, TABLE]))
    (rug,) = of_type(out, "rug")
    sofa, table = out["furniture"]
    assert rug["anchor_ids"] == [sofa["id"], table["id"]] and rug["host_id"] is None
    assert rug["source"] == "added_by_ai" and rug["method"] == "rule" and rug["kind"] == "decor"
    assert rug["rotation_deg"] == 0.0 and rug["reason"].startswith("rug under the sofa and coffee table group")
    # group box in the sofa frame (front = -Y local = south): x +-1.1, y from the sofa back (+0.45) to the far
    # table edge; + 0.3 m everywhere, but the back is cut at the room shrunk by 0.3 m (sofa back at 0.02 m
    # from the wall).
    x0, y0, x1, y1 = local_box(rug, sofa)
    assert (x0, x1) == (-1.4, 1.4)
    assert y0 == pytest.approx((3.08 - 0.3) - 4.53, abs=0.001)              # the far table edge + 0.3
    assert y1 == pytest.approx((5.0 - 0.3) - 4.53, abs=0.021)               # cut at 0.3 m from the wall
    shrunk = Polygon([[0, 0], [6, 0], [6, 5], [0, 5]]).buffer(-0.3, join_style="mitre")
    assert shrunk.buffer(1e-3).contains(D.rug_polygon(rug))
    assert D.rug_polygon(rug).contains(Point(table["footprint"]["center"]))
    row = next(r for r in rows if r["room_id"] == RID)
    assert row["rugs"] == 1


def test_rugs_never_cover_a_door_swing_and_say_they_were_cut():
    # A door at the south-west, opening into the room: its 0.9 m swing reaches under the group's corner.
    b = room_building(furniture=[("sofa", (2.0, 4.53), 0.0, (2.2, 0.9)), ("table_coffee", (2.0, 3.38), 0.0, (1.2, 0.6))],
                      doors=[("d1", "w", 3.0, 0.9, True)])
    out, _rows = D.add_decor(b)
    (rug,) = of_type(out, "rug")
    ctx = PL.room_context(out, out["rooms"][0])
    (door,) = ctx.doors
    assert door.swing is not None and door.swing.area > 0.5
    assert D.rug_polygon(rug).intersection(door.swing).area < 1e-4
    assert "cut from" in rug["reason"]
    # the same group without the door: a larger rug
    out2, _ = D.add_decor(room_building(furniture=[("sofa", (2.0, 4.53), 0.0, (2.2, 0.9)),
                                                   ("table_coffee", (2.0, 3.38), 0.0, (1.2, 0.6))]))
    assert D.rug_polygon(of_type(out2, "rug")[0]).area > D.rug_polygon(rug).area + 0.1


def test_bedroom_rug_lies_under_the_lower_two_thirds_of_a_double_bed_only():
    bed = ("bed_double", (3.0, 3.98), 0.0, (1.6, 2.0))       # head against the north wall, foot south
    out, _ = D.add_decor(room_building(room_type="bedroom", furniture=[bed]))
    (rug,) = of_type(out, "rug")
    piece = out["furniture"][0]
    assert rug["anchor_ids"] == [piece["id"]] and "lower two thirds" in rug["reason"]
    x0, y0, x1, y1 = local_box(rug, piece)
    assert (x0, x1) == (-1.1, 1.1)
    assert y0 == pytest.approx(-1.0 - 0.3, abs=1e-3)                         # 0.3 m past the foot
    assert y1 == pytest.approx(-1.0 + 2.0 * 2 / 3 + 0.3, abs=1e-3)           # 2/3 of the bed + 0.3 m
    # a single bed gets none; neither does a double bed in a living room
    out, _ = D.add_decor(room_building(room_type="bedroom", furniture=[("bed_single", (3.0, 3.98), 0.0, (0.9, 2.0))]))
    assert not of_type(out, "rug")
    out, _ = D.add_decor(room_building(room_type="living", furniture=[bed]))
    assert not of_type(out, "rug")


def test_dining_rug_covers_the_chairs_and_never_runs_under_a_counter():
    table = ("table_dining", (3.0, 2.5), 0.0, (1.6, 0.9))
    out, _ = D.add_decor(room_building(room_type="dining", width=6.0, depth=5.0, furniture=[table]))
    (rug,) = of_type(out, "rug")
    x0, y0, x1, y1 = local_box(rug, out["furniture"][0])
    m = D.DINING_CHAIR_M + D.RUG_MARGIN_M
    assert (x0, y0, x1, y1) == pytest.approx((-0.8 - m, -0.45 - m, 0.8 + m, 0.45 + m), abs=1e-3)
    # a kitchen counter along the south wall: the rug stops before it
    counter = ("kitchen_counter", (3.0, 0.3), 0.0, (4.0, 0.6))
    out, _ = D.add_decor(room_building(room_type="kitchen", furniture=[table, counter]))
    (rug,) = of_type(out, "rug")
    counter_poly = PL.piece_from_furniture(out["furniture"][1]).polygon()
    assert D.rug_polygon(rug).intersection(counter_poly).area < 1e-4
    assert D.rug_polygon(rug).contains(Point(3.0, 2.5))


def test_two_rugs_in_one_room_never_overlap():
    b = room_building(width=8.0, depth=5.0, furniture=[SOFA, TABLE, ("table_dining", (6.4, 2.0), 90.0, (1.4, 0.8))])
    out, _ = D.add_decor(b)
    living, dining = of_type(out, "rug")
    assert "sofa" in living["reason"] and "dining" in dining["reason"]
    assert D.rug_polygon(living).intersection(D.rug_polygon(dining)).area < 1e-4


def test_no_rug_or_wall_art_without_a_verified_group_or_when_the_room_is_too_small():
    # an unverified sofa (type unclear): nothing is hung or laid around it
    out, rows = D.add_decor(room_building(furniture=[SOFA + ("unverified",), TABLE]))
    assert not of_type(out, "rug") and not of_type(out, "wall_art")
    # a sofa without a coffee table: no rug, the report says why
    out, rows = D.add_decor(room_building(furniture=[SOFA]))
    assert not of_type(out, "rug") and "no coffee table in front of a sofa" in rows[0]["note"]
    # a tiny dining nook: the rug would be cut below 0.8 m
    out, rows = D.add_decor(room_building(room_type="dining", width=1.3, depth=1.3,
                                          furniture=[("table_dining", (0.65, 0.65), 0.0, (0.6, 0.6))]))
    assert not of_type(out, "rug") and "below 0.8 m" in rows[0]["note"]


def test_fit_rug_cuts_l_shaped_obstacles_and_keeps_the_key_point():
    room = Polygon([[0, 0], [4, 0], [4, 3], [0, 3]])
    # a rectangle sticking out of two sides: the outside is one L-shaped region
    got, why = D.fit_rug((-1.0, -1.0, 3.0, 2.0), room, (1.0, 1.0))
    assert why == "ok" and got == pytest.approx((0.0, 0.0, 3.0, 2.0), abs=0.021)
    # an obstacle in a corner: the cut keeps the most rug (3 x 3 = 9 m2 beats 4 x 2 = 8 m2)
    blocked = room.difference(Polygon([[3, 2], [4, 2], [4, 3], [3, 3]]))
    got, _ = D.fit_rug((0.0, 0.0, 4.0, 3.0), blocked, (1.0, 1.0))
    assert got == pytest.approx((0.0, 0.0, 3.0, 3.0), abs=1e-9)                # grid lines on the obstacle
    got, _ = D.fit_rug((0.0, 0.0, 4.0, 3.0), room.difference(Polygon([[3, 1], [4, 1], [4, 3], [3, 3]])), (1.0, 1.0))
    assert got == pytest.approx((0.0, 0.0, 3.0, 3.0), abs=1e-9)                # 9 m2 beats 4 x 1
    # the key point on an obstacle: no rug
    assert D.fit_rug((0.0, 0.0, 4.0, 3.0), blocked, (3.5, 2.5))[0] is None
    # unobstructed: the rectangle comes back exactly
    assert D.fit_rug((0.5, 0.5, 3.5, 2.5), room, (1.0, 1.0)) == ((0.5, 0.5, 3.5, 2.5), "ok")


# --------------------------------------------------------------------------
# Wall art
# --------------------------------------------------------------------------

def test_wall_art_hangs_centred_above_the_sofa_on_the_wall_behind_it():
    out, rows = D.add_decor(room_building(furniture=[SOFA, TABLE]))
    (art,) = of_type(out, "wall_art")
    sofa = out["furniture"][0]
    assert art["anchor_ids"] == [sofa["id"]] and art["host_id"] is None and art["wall_id"] == "w_n"
    assert art["wall_point"] == [3.0, 5.0]                                   # on the north wall face
    assert art["size"] == [pytest.approx(0.6 * 2.2), D.WALL_ART_DEPTH_M]       # 0.6 x the sofa width
    assert art["center"] == pytest.approx([3.0, 5.0 - D.WALL_ART_DEPTH_M / 2])
    # local -Y (its front) points into the room (south), local +Y to the wall
    rad = math.radians(art["rotation_deg"])
    assert (math.sin(rad), -math.cos(rad)) == pytest.approx((0.0, -1.0), abs=1e-9)
    from wenart.blender import parametric as P
    assert art["bottom_m"] == pytest.approx(P.piece_bbox(sofa)[2] + D.WALL_ART_GAP_M)
    assert art["max_height_m"] == pytest.approx(2.7 - D.WALL_ART_CEILING_M - art["bottom_m"])
    assert row_of(rows)["wall_art"].startswith(f"over {sofa['id']}")


def row_of(rows):
    return next(r for r in rows if r["room_id"] == RID)


def span_on_wall(art: dict) -> tuple[float, float]:
    return art["wall_point"][0] - art["size"][0] / 2, art["wall_point"][0] + art["size"][0] / 2


def test_wall_art_never_hangs_over_a_window_or_a_door():
    # a window centred behind the sofa: no room left on either side within the sofa's span
    out, rows = D.add_decor(room_building(furniture=[SOFA, TABLE], windows=[("win1", "n", 3.0, 1.2)]))
    assert not of_type(out, "wall_art") and "window win1" in row_of(rows)["note"]
    # a window off to one side: the picture narrows (centred) to stay 0.1 m off it
    out, _ = D.add_decor(room_building(furniture=[SOFA, TABLE], windows=[("win1", "n", 4.0, 1.0)]))
    (art,) = of_type(out, "wall_art")
    lo, hi = span_on_wall(art)
    assert hi == pytest.approx(4.0 - 0.5 - D.OPENING_MARGIN_M, abs=1e-3) and art["wall_point"][0] == 3.0
    assert "narrowed for window win1" in art["reason"] and art["size"][0] < 0.6 * 2.2
    # a door in that wall works the same way
    out, _ = D.add_decor(room_building(furniture=[SOFA, TABLE], doors=[("d1", "n", 1.0, 0.9)]))
    (art,) = of_type(out, "wall_art")
    lo, hi = span_on_wall(art)
    assert lo >= 1.0 + 0.45 + D.OPENING_MARGIN_M - 1e-6
    # an opening on another wall does not matter
    out, _ = D.add_decor(room_building(furniture=[SOFA, TABLE], windows=[("win1", "s", 3.0, 1.2)]))
    assert of_type(out, "wall_art")[0]["size"][0] == pytest.approx(1.32)


def test_bedroom_wall_art_over_the_headboard_else_over_a_dresser():
    bed = ("bed_double", (3.0, 3.98), 0.0, (1.6, 2.0))
    dresser = ("dresser", (0.27, 1.5), 90.0, (1.0, 0.5))          # back (local +Y) against the west wall
    out, _ = D.add_decor(room_building(room_type="bedroom", furniture=[bed, dresser]))
    (art,) = of_type(out, "wall_art")
    assert art["anchor_ids"] == [out["furniture"][0]["id"]] and "headboard" in art["reason"]
    assert art["size"][0] == pytest.approx(0.96) and art["wall_point"] == [3.0, 5.0]
    # the bed in the middle of the room (no wall behind it): the dresser takes the picture
    free_bed = ("bed_double", (3.5, 2.5), 0.0, (1.6, 2.0))
    out, rows = D.add_decor(room_building(room_type="bedroom", furniture=[free_bed, dresser]))
    (art,) = of_type(out, "wall_art")
    assert art["anchor_ids"] == [out["furniture"][1]["id"]] and "dresser" in art["reason"]
    assert art["wall_point"] == pytest.approx([0.0, 1.5]) and art["size"][0] == pytest.approx(0.6)
    rad = math.radians(art["rotation_deg"])
    assert (math.sin(rad), -math.cos(rad)) == pytest.approx((1.0, 0.0), abs=1e-9)   # faces east, into the room
    # a low ceiling: nothing fits above the headboard
    out, rows = D.add_decor(room_building(room_type="bedroom", furniture=[bed], ceiling=1.5))
    assert not of_type(out, "wall_art") and "under the ceiling" in row_of(rows)["note"]
    # only living rooms, bedrooms and dining rooms
    out, _ = D.add_decor(room_building(room_type="hall", furniture=[SOFA]))
    assert not of_type(out, "wall_art")


# --------------------------------------------------------------------------
# Brief, prayer rooms, schema, synthetic buildings
# --------------------------------------------------------------------------

def test_brief_decor_off_or_a_prayer_room_gives_no_rug_and_no_wall_art():
    out, rows = D.add_decor(room_building(furniture=[SOFA, TABLE], brief={"decor": False}))
    assert out["decor"] == [] and rows[0]["note"].startswith("brief.decor is false")
    b = room_building(furniture=[SOFA, TABLE])
    b["rooms"][0]["room_type"] = "prayer"
    out, _ = D.add_decor(b)
    assert out["decor"] == []


def test_schema_accepts_the_new_decor_and_refuses_broken_items():
    out, _ = D.add_decor(room_building(furniture=[SOFA, TABLE]))
    B.validate(out)
    rug, art = of_type(out, "rug")[0], of_type(out, "wall_art")[0]
    for mutate in (lambda o: of_type(o, "rug")[0].update(host_id="f_L0_001"),
                   lambda o: of_type(o, "wall_art")[0].pop("wall_point"),
                   lambda o: of_type(o, "rug")[0].pop("anchor_ids"),
                   lambda o: of_type(o, "rug")[0].update(type="carpet"),
                   lambda o: of_type(o, "rug")[0].update(source="from_documents"),
                   lambda o: of_type(o, "wall_art")[0].update(kind="furniture")):
        broken = copy.deepcopy(out)
        mutate(broken)
        with pytest.raises(jsonschema.ValidationError):
            B.validate(broken)
    assert rug["size"][0] > D.MAX_DECOR_M and art["size"][0] > D.MAX_DECOR_M     # large decor is allowed
    schema_types = B.load_schema()["$defs"]["decor"]["properties"]["type"]["enum"]
    assert tuple(schema_types) == D.DECOR_TYPES


def test_synthetic_buildings_get_rugs_and_wall_art_by_the_rules():
    seen = {"rug": 0, "wall_art": 0}
    for name in ("synthetic-01", "synthetic-03", "synthetic-05"):
        building = load_truth(name)
        out, rows = D.add_decor(building)
        B.validate(out)
        assert json.dumps(building["furniture"]) == json.dumps(out["furniture"])
        rooms = {r["id"]: r for r in out["rooms"]}
        pieces = {f["id"]: f for f in out["furniture"]}
        for d in out["decor"]:
            if d["type"] not in D.LARGE_DECOR_TYPES:
                continue
            seen[d["type"]] += 1
            room = rooms[d["room_id"]]
            ctx = PL.room_context(out, room)
            anchors = [pieces[a] for a in d["anchor_ids"]]
            assert all(a["status"] == "verified" and a["room_id"] == room["id"] for a in anchors)
            if d["type"] == "rug":
                poly = D.rug_polygon(d)
                assert ctx.polygon.buffer(-D.RUG_ROOM_INSET_M + 1e-3, join_style="mitre").contains(poly)
                for door in ctx.doors:
                    assert door.swing is None or poly.intersection(door.swing).area < 1e-4
                assert min(d["size"]) >= D.RUG_MIN_SIDE_M
            else:
                assert room["room_type"] in D.WALL_ART_ROOM_TYPES
                assert anchors[0]["type"] in D.WALL_ART_HOST_TYPES
                assert d["size"][0] <= D.WALL_ART_WIDTH_SHARE * anchors[0]["footprint"]["size"][0] + 1e-6
                assert ctx.ring.distance(Point(d["wall_point"])) < 1e-3
                art = LineString(_art_ends(d))
                doors, windows = PL.room_openings(out, room)
                for op in doors + windows:
                    if ctx.ring.distance(Point(op["center"])) > 0.2:
                        continue
                    assert art.distance(Point(op["center"])) >= op["width"] / 2 + D.OPENING_MARGIN_M - 0.12
        again, _ = D.add_decor(out)
        assert json.dumps(again, sort_keys=True) == json.dumps(out, sort_keys=True)     # idempotent
    assert seen["rug"] >= 3 and seen["wall_art"] >= 3


def _art_ends(d: dict):
    rad = math.radians(d["rotation_deg"])
    ux, uy = math.cos(rad), math.sin(rad)
    x, y = d["wall_point"]
    h = d["size"][0] / 2
    return [(x - ux * h, y - uy * h), (x + ux * h, y + uy * h)]


def test_report_lists_rugs_and_wall_art():
    out, rows = D.add_decor(room_building(furniture=[SOFA, TABLE]))
    report = D.decor_report(out, rows)
    assert "| Room | Cushions | Books | Plant | Rugs | Wall art | Note |" in report
    assert "| Room (r_L0_room) | 2 | 0 |" in report and "over f_L0_001" in report


# --------------------------------------------------------------------------
# The consumers: views, vision check, detector, camera search
# --------------------------------------------------------------------------

def _manifest_with_rug_and_art() -> dict:
    def obj(name, wid, kind, pi, **extra):
        return dict({"name": name, "wenart_id": wid, "kind": kind, "status": "verified", "pass_index": pi,
                     "evidence": EV, "material": None, "textured": False, "assumed": {}}, **extra)

    return {"objects": [
        obj("furn_f_1", "f_1", "furniture", 1, room_id="r", type="sofa", source="from_documents",
            box3d={"center": [3, 4.5, 0.4], "size": [2.2, 0.9, 0.85], "rotation_deg": 180.0}),
        obj("decor_f_1_1", "f_1", "decor", 1, host_id="f_1", room_id="r", type="cushion", source="added_by_ai",
            status="assumed"),
        obj("decor_dec_L0_003", "dec_L0_003", "decor", 2, host_id=None, room_id="r", type="rug",
            source="added_by_ai", status="assumed", anchor_ids=["f_1", "f_2"],
            box3d={"center": [3, 3.5, 0.006], "size": [2.8, 2.4, 0.012], "rotation_deg": 180.0}),
        obj("decor_dec_L0_004", "dec_L0_004", "decor", 3, host_id=None, room_id="r", type="wall_art",
            source="added_by_ai", status="assumed", anchor_ids=["f_1"],
            box3d={"center": [3, 4.98, 1.5], "size": [1.3, 0.03, 0.9], "rotation_deg": 180.0}),
    ], "pass_index": {"f_1": 1, "dec_L0_003": 2, "dec_L0_004": 3}}


def test_views_index_table_makes_rugs_and_wall_art_their_own_decor_elements():
    from wenart import views as V

    table = V.index_table(_manifest_with_rug_and_art())
    assert table[1]["kind"] == "furniture" and table[1]["host_decor"] == ["cushion"]      # not the rug
    assert (table[2]["kind"], table[2]["type"], table[2]["wenart_id"]) == ("decor", "rug", "dec_L0_003")
    assert (table[3]["kind"], table[3]["type"]) == ("decor", "wall_art")


def test_vision_check_treats_rugs_and_wall_art_as_decor_never_as_furniture():
    from wenart.vision_check import expected as E
    from wenart.vision_check import schemas as S

    for t in ("rug", "wall_art"):
        assert t in S.DECOR_CATEGORIES and t in S.CATEGORIES and t not in S.FURNITURE_TYPES
        assert S.category_class(t) == "decor" and S.element_category("decor", t) == t
        assert not E.is_type_unverified("decor", t, "assumed")
    roles = E.load_cfg(None)["roles"]
    # a big own-room rug filling a third of the frame is still only optional (never a required furniture piece)
    assert E.role_of("decor", True, 0.35, 1.0, roles) == "optional"
    # the rug seen as a "textile" is the same object
    answer, changed = S.normalise_answer({"status": "different", "seen_as": "textile", "confidence": 0.8}, "rug")
    assert answer["status"] == "present" and changed
    from wenart.vision_check import prompts as Pr
    assert "rug" in Pr.HINTS["rug"] and "wall" in Pr.HINTS["wall_art"]


def test_detector_rug_and_picture_boxes_on_the_building_decor_are_covered_and_never_reject():
    from wenart.gate import detect as Dt

    table = {1: {"wenart_id": "f_1", "kind": "furniture", "type": "sofa", "host_decor": ["cushion"]},
             2: {"wenart_id": "dec_L0_003", "kind": "decor", "type": "rug", "host_decor": []},
             3: {"wenart_id": "dec_L0_004", "kind": "decor", "type": "wall_art", "host_decor": []}}
    idx = np.zeros((1000, 1000), np.uint16)
    idx[500:800, 100:400] = 1
    idx[800:1000, 50:900] = 2
    idx[100:300, 200:500] = 3
    assert Dt.element_matches("rug", table[2]) and Dt.element_matches("picture_frame", table[3])
    assert not Dt.element_matches("rug", table[1]) and not Dt.element_matches("sofa", table[2])
    polished = [{"group": "rug", "score": 0.9, "box_px": [60, 810, 890, 990], "class": "decor"},
                {"group": "picture_frame", "score": 0.9, "box_px": [210, 110, 490, 290], "class": "decor"},
                {"group": "sofa", "score": 0.9, "box_px": [60, 810, 890, 990], "class": "furniture"}]
    got = Dt.added_candidates(polished, [], 0.1, idx, table)
    assert [c["group"] for c in got] == ["sofa"]          # a sofa box on the rug is still an added object
    assert Dt.GROUP_BY_NAME["rug"].cls == Dt.GROUP_BY_NAME["picture_frame"].cls == "decor"
    assert not Dt.non_decor("decor")


def test_camera_search_ignores_rugs_and_wall_art():
    from wenart.blender import cameras, camsearch

    out, _ = D.add_decor(room_building(furniture=[SOFA, TABLE], doors=[("d1", "e", 1.0, 0.9, True)],
                                       windows=[("win1", "s", 3.0, 1.6)]))
    assert of_type(out, "rug") and of_type(out, "wall_art")
    bare = copy.deepcopy(out)
    bare["decor"] = []
    room = out["rooms"][0]
    assert camsearch.shown_pieces(room, out) == camsearch.shown_pieces(room, bare) == out["furniture"]
    model = camsearch.RoomModel(room, out)
    assert [e["id"] for e in model.elements if e["kind"] == "furniture"] == [f["id"] for f in out["furniture"]]
    with_decor = cameras.plan_cameras(out, "L0", policy="search")
    without = cameras.plan_cameras(bare, "L0", policy="search")
    strip = lambda plans: [{k: v for k, v in p.items() if k != "search_seconds"} for p in plans]  # noqa: E731
    assert strip(with_decor) == strip(without)
