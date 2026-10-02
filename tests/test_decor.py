"""Decor rules (docs/milestone4.md section 4) on the synthetic buildings and hand-made rooms."""
import json

import pytest
from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart.furniture import decor as D
from wenart.furniture import placer as P

from conftest import load_truth
from test_placer import ROOM_ID, make_building


def footprint(item):
    return P.Piece(item["type"], tuple(item["center"]), item["rotation_deg"], tuple(item["size"]), False).polygon()


@pytest.fixture(scope="module")
def decorated():
    building = load_truth("synthetic-01")
    out, rows = D.add_decor(building)
    return building, out, rows


def test_decor_list_shape_and_sizes(decorated):
    building, out, rows = decorated
    B.validate(out)
    assert out["decor"] and json.dumps(building["furniture"]) == json.dumps(out["furniture"])
    ids = [d["id"] for d in out["decor"]]
    assert len(ids) == len(set(ids))
    for d in out["decor"]:
        assert d["type"] in D.DECOR_TYPES and d["kind"] == "decor" and d["asset"] is None
        assert d["source"] == "added_by_ai" and d["method"] == "rule" and d["reason"]
        assert max(d["size"]) <= D.MAX_DECOR_M
        assert d["id"].startswith(f"dec_{d['level_id']}_")
        room = next(r for r in out["rooms"] if r["id"] == d["room_id"])
        assert Polygon(room["polygon"]).contains(Point(d["center"]))


def test_hosted_decor_sits_on_its_host(decorated):
    _b, out, _rows = decorated
    hosts = {f["id"]: f for f in out["furniture"]}
    hosted = [d for d in out["decor"] if d["host_id"]]
    assert hosted
    for d in hosted:
        host = hosts[d["host_id"]]
        assert d["room_id"] == host["room_id"] and d["level_id"] == host["level_id"]
        assert D.HOST_TYPES[host["type"]] == d["type"]
        assert P.piece_from_furniture(host).polygon().buffer(1e-6).contains(footprint(d))
        assert d["rotation_deg"] == host["footprint"]["rotation_deg"]
    expected = sum(len(D.host_decor(f)) for f in out["furniture"] if f["status"] == "verified" and f["type"] in D.HOST_TYPES)
    assert len(hosted) == expected
    sofa = next(f for f in out["furniture"] if f["type"] == "sofa")
    assert len([d for d in hosted if d["host_id"] == sofa["id"]]) == 2


def test_plants_only_in_living_and_bedrooms_and_off_walkways(decorated):
    _b, out, rows = decorated
    plants = [d for d in out["decor"] if d["type"] == "plant"]
    assert plants, rows
    for plant in plants:
        room = next(r for r in out["rooms"] if r["id"] == plant["room_id"])
        assert room["room_type"] in D.PLANT_ROOM_TYPES and plant["host_id"] is None
        ctx = P.room_context(out, room)
        pieces = [P.piece_from_furniture(f, i) for i, f in enumerate(out["furniture"]) if f["room_id"] == room["id"]]
        poly = footprint(plant)
        assert ctx.shrunk.buffer(1e-6).contains(poly)
        assert all(poly.intersection(p.polygon()).area < P.AREA_EPS for p in pieces)
        for door in ctx.doors:
            assert poly.intersection(door.zone).area < P.AREA_EPS
            assert door.swing is None or poly.intersection(door.swing).area < P.AREA_EPS
        plant_piece = P.Piece("plant", tuple(plant["center"]), 0.0, tuple(plant["size"]), False, index=len(pieces))
        assert not P.walkway_failures(pieces + [plant_piece], ctx)
    assert len(plants) == len({p["room_id"] for p in plants})     # one per room
    for row in rows:
        if row["plant"] == "none":
            assert row["note"].startswith("no free corner")


def test_brief_decor_false_gives_nothing():
    building = load_truth("synthetic-01")
    building["project"]["brief"] = {"decor": False}
    out, rows = D.add_decor(building)
    assert out["decor"] == [] and rows[0]["note"].startswith("brief.decor is false")
    assert D.decor_allowed(load_truth("synthetic-01")) is True


def test_add_decor_is_idempotent(decorated):
    _b, out, _rows = decorated
    again, _ = D.add_decor(out)
    assert json.dumps(again, sort_keys=True) == json.dumps(out, sort_keys=True)


def test_unverified_pieces_get_no_decor():
    building = load_truth("synthetic-03")
    out, _rows = D.add_decor(building)
    unverified = {f["id"] for f in out["furniture"] if f["status"] != "verified" or f["type"] == "unknown"}
    assert unverified
    assert not [d for d in out["decor"] if d["host_id"] in unverified]


def wrap(building_parts, room, furniture):
    """A minimal valid building dict around the hand-made test room."""
    b = B.empty_building("t", "t", "0")
    b["levels"] = [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "ceiling_height": 2.7,
                    "ceiling_height_source": "assumed_default", "evidence": []}]
    ev = [B.evidence("x.dxf", "vector", 1.0)]
    for w in building_parts["walls"]:
        b["walls"].append(dict(w, status="verified", evidence=ev, exterior=w.get("exterior", True)))
    for o in building_parts["openings"]:
        b["openings"].append(dict(o, status="verified", evidence=ev, height=None, sill_height=o.get("sill_height")))
    b["rooms"] = [dict(room, evidence=ev)]
    for i, (ftype, center, rot, size) in enumerate(furniture, 1):
        b["furniture"].append({"id": f"f_L0_{i:03d}", "level_id": "L0", "room_id": ROOM_ID, "type": ftype,
                               "type_raw": None, "source": "from_documents",
                               "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
                               "front_deg": (270 + rot) % 360, "height": None, "asset": None,
                               "status": "verified", "evidence": ev})
    B.validate(b)
    return b


def test_plant_skips_blocked_corners_and_reports():
    parts, room = make_building()
    room["room_type"] = "living"
    room["has_documented_furniture"] = True
    # Corners: (0,0) near the south door swing, (4,0) and (4,3) by the window band / free, (0,3) wardrobe.
    b = wrap(parts, room, [("wardrobe", (0.9, 2.679), 0.0, (1.8, 0.6)), ("sofa", (1.5, 1.5), 0.0, (2.2, 0.9))])
    out, rows = D.add_decor(b)
    plants = [d for d in out["decor"] if d["type"] == "plant"]
    assert len(plants) == 1
    assert plants[0]["center"] in ([3.75, 0.25], [3.75, 2.75])
    # Fill every corner: no plant, and the row says why.
    b2 = wrap(parts, room, [("wardrobe", (0.9, 2.679), 0.0, (1.8, 0.6)), ("wardrobe", (3.1, 0.321), 180.0, (1.8, 0.6)),
                            ("bookshelf", (3.5, 2.8), 0.0, (1.0, 0.35)), ("chair", (0.3, 0.3), 0.0, (0.45, 0.45))])
    out2, rows2 = D.add_decor(b2)
    assert not [d for d in out2["decor"] if d["type"] == "plant"]
    row = next(r for r in rows2 if r["room_id"] == ROOM_ID)
    assert row["plant"] == "none" and "no free corner" in row["note"]
    assert row["cushions"] == 0 and row["books"] == 1


def test_cli_writes_building_and_report(tmp_path):
    src = tmp_path / "building.json"
    B.save(load_truth("synthetic-01"), src)
    out = tmp_path / "out" / "building_decor.json"
    assert D.main([str(src), "--out", str(out)]) == 0
    result = B.load(out)
    assert result["decor"]
    report = (out.parent / "decor_report.md").read_text(encoding="utf-8")
    assert report.startswith("# Decor: synthetic-01") and "| Salon (r_L0_salon) |" in report


def test_plant_never_stands_in_another_pieces_clearance():
    """A free corner inside a desk's 0.6 m front clearance is not free."""
    parts, room = make_building(doors=[], windows=[])
    room["room_type"] = "living"
    room["has_documented_furniture"] = True
    # Desk 1.2 x 0.6 facing the south wall, front edge 0.6 m from it: corner (0.25, 0.25) is in its clearance.
    b = wrap(parts, room, [("desk", (0.7, 0.9), 0.0, (1.2, 0.6)),          # front = -Y: faces the south wall
                           ("wardrobe", (3.1, 0.321), 180.0, (1.8, 0.6)), ("wardrobe", (3.1, 2.679), 0.0, (1.8, 0.6)),
                           ("bookshelf", (0.5, 2.8), 0.0, (1.0, 0.35))])
    out, rows = D.add_decor(b)
    assert not [d for d in out["decor"] if d["type"] == "plant"]
    row = next(r for r in rows if r["room_id"] == ROOM_ID)
    assert "clearance of another piece" in row["note"]
