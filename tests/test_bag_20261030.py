"""UL160 (30 Oct 2026): "I did not understand what this is if this is a bag it requires a lot more detail in the model"
(real04 run 20261030-043021-full: the ``bag`` decor was a grey blob with two black triangles). The weekend bag is a
real-looking holdall (``wenart.blender.holdall``)."""
from __future__ import annotations

import math

from wenart.blender import detail_parts as DP
from wenart.blender import holdall as HD
from wenart.blender import parametric as P

BOX = (0.55, 0.30, 0.30)          # room_details.BAG_SIZE


def _bag(box=BOX, item=None):
    return P.decor_parts("bag", *box, item if item is not None else {"colour": "charcoal"})


def _roles(parts):
    out: dict = {}
    for p in parts:
        out.setdefault(p["role"], []).append(p)
    return out


def test_the_bag_has_the_parts_of_a_real_holdall():
    roles = _roles(_bag())
    assert len(roles["body"]) == 1 and len(roles["base"]) == 1                    # the body over its base band
    assert len(roles["handle"]) == 2 and len(roles["wrap"]) == 1                  # two rolled handles, one wrap
    # 31 Oct 2026: both end panels and both edges of the base band piped (tests/test_bedding_sofa_bag_20261031.py)
    assert len(roles["piping"]) == 4
    assert len(roles["strap"]) == 1 and len(roles["clip"]) == 2 and len(roles["ring"]) == 2
    assert len(roles["pocket"]) == 1 and len(roles["zip"]) >= 4                    # main zip and the pocket's
    assert len(roles["foot"]) == 4                                                 # base feet
    assert len(roles["tab"]) >= 4 + 2 + 2                                          # handle tabs, garages, D-ring tabs
    assert len(roles["button"]) >= 8                                               # rivets, sliders
    keys = {p["key"] for p in _bag()}
    # 31 Oct 2026 (user: "black leather like suite"): a leather bag in its colour, brass hardware, stitching
    assert keys == {HD.LEATHER_COLOURED, HD.BRASS, HD.TAPE, HD.THREAD}
    canvas = {p["key"] for p in _bag(item={"colour": "charcoal", "bag_material": "canvas"})}
    assert canvas == {HD.CANVAS, HD.LEATHER, HD.METAL, HD.TAPE, HD.THREAD}           # the canvas bag of before


def test_closed_outward_and_inside_its_box():
    parts = _bag()
    assert all(HD.volume(p) > 0.0 for p in parts if p["role"] not in ("body", "base"))
    body = next(p for p in parts if p["role"] == "body")
    base = next(p for p in parts if p["role"] == "base")
    assert HD.volume({"verts": body["verts"] + base["verts"],
                      "faces": body["faces"] + [[i + len(body["verts"]) for i in f] for f in base["faces"]]}) > 0.0
    for box in (BOX, (0.4, 0.3, 0.2), (0.7, 0.4, 0.4)):
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(_bag(box))
        assert x1 - x0 <= box[0] + 1e-9 and y1 - y0 <= box[1] + 1e-9 and z1 - z0 <= box[2] + 1e-9
        assert abs(z0) < 1e-9
        assert not any(math.isnan(c) for p in _bag(box) for v in p["verts"] for c in v)


def test_real_proportions_in_the_box_of_room_details():
    parts = _bag()
    body = next(p for p in parts if p["role"] == "body")
    bx0, by0, bz0, bx1, by1, bz1 = DP.bbox([body])
    assert 0.40 <= bx1 - bx0 <= 0.56                         # a 40-55 cm holdall
    assert 0.18 <= by1 - by0 <= 0.28 and 0.17 <= bz1 - bz0 <= 0.27
    handles = _roles(parts)["handle"]
    top = max(v[2] for p in handles for v in p["verts"])
    assert top > bz1 + 0.03                                  # the handles arch over the top
    # the strap lies on the floor in front of the body
    strap = _roles(parts)["strap"][0]
    floor = [v for v in strap["verts"] if v[2] < 0.01]
    assert floor and min(v[1] for v in floor) < by0
    # the pocket stands on the front, the zip runs on the top
    pocket = _roles(parts)["pocket"][0]
    assert min(v[1] for v in pocket["verts"]) < by0 + 0.002
    zips = [p for p in parts if p["role"] == "zip" and max(v[2] for v in p["verts"]) > bz1 - 0.03]
    assert zips and max(max(v[0] for v in p["verts"]) - min(v[0] for v in p["verts"]) for p in zips) > 0.6 * (bx1 - bx0)


def test_soft_parts_are_smooth_and_leather_has_a_material():
    from wenart.blender import furniture as F
    from wenart.style import vocabulary as V

    roles = _roles(_bag())
    for r in ("body", "base", "handle", "piping"):
        assert all(p.get("smooth") for p in roles[r]), r
    assert HD.LEATHER in P.MATERIAL_KEYS
    keys, _ = F.style_material_keys({})
    assert keys["leather"][0] == "leather_tan" and "leather_tan" in V.FLAT_COLOURS and "leather_tan" in V.ROUGHNESS
    assert P.part_bevel_radius(roles["tab"][0]) <= 0.001 + 1e-9


def test_the_old_blob_is_gone():
    parts = _bag()
    assert len(parts) >= 30 and sum(len(p["faces"]) for p in parts) >= 1500
    assert not [p for p in parts if p["role"] == "strap" and len(p["verts"]) <= 12]   # no stick handles
