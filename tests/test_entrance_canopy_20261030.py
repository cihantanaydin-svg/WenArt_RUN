"""UL171 (30 Oct 2026, real04 run 20261030-043021-full): "There should be better solution than these things in the house
entrance points make it make sense". Flat white slabs stuck out of the wall over the entrance doors at two heights.
An entrance canopy is a real product, only where nothing shelters the door, under any window above it, and the
canopies of one wall share one height."""
from wenart.blender import facade as FA
from wenart.blender import geom2d


def _vol(v, f):
    s = 0.0
    for face in f:
        a = v[face[0]]
        for i in range(1, len(face) - 1):
            b, c = v[face[i]], v[face[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def test_a_canopy_is_a_framed_slab_with_a_soffit_and_tie_rods():
    parts = FA.canopy_parts((0.0, 0.0), (0.0, -1.0), 1.6, 2.45, "L0", "d1")
    kinds = [p["kind"] for p in parts]
    assert kinds.count("canopy") == 4 and kinds.count("canopy_soffit") == 1 and kinds.count("canopy_rod") == 4
    rods = [p for p in parts if p.get("mesh")]
    assert len(rods) == 2
    for r in rods:
        v, f = r["mesh"]
        assert _vol(v, f) > 0                                         # closed, wound outwards
        ys, zs = [p[1] for p in v], [p[2] for p in v]
        assert max(ys) > -0.05 and min(ys) < -0.8                     # from the wall out to the front
        assert max(zs) > 2.45 + 0.5                                   # up to its plate over the canopy
    fascia = [p for p in parts if p["reason"].startswith("the canopy's front fascia")][0]
    assert fascia["size"][2] > FA.KIT["canopy_thick"]               # the drip edge is deeper than the slab
    assert all(p["inferred"] for p in parts)
    for p in parts:                                                   # every part's mesh is buildable
        v, f = (p["mesh"][0], p["mesh"][1]) if p.get("mesh") else geom2d.box(p["center"], p["size"], p["rotation_deg"])
        assert v and f


def _door_case(rooms=(), openings=()):
    building = {"walls": [{"id": "w", "level_id": "L0", "start": [0, 0], "end": [10, 0], "thickness": 0.2}],
                "openings": [{"id": "d1", "type": "door", "wall_id": "w", "level_id": "L0", "center": [3, 0],
                              "width": 1.0, "height": 2.1, "sill_height": 0.0}] + list(openings),
                "rooms": list(rooms)}
    levels = [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}, {"id": "L1", "elevation": 3.0,
                                                                      "ceiling_height": 2.6}]
    e = {"opening_id": "d1", "level_id": "L0", "centre": [3.0, 0.0], "outward": (0.0, -1.0), "half_t": 0.1,
         "width": 1.0}
    return building, levels, e


def test_no_canopy_where_the_floor_above_or_the_eaves_shelter_the_door():
    b, levels, e = _door_case()
    z, why = FA.canopy_height(e, b["openings"][0], levels[0], 2.1, b, levels, None, (3.0, -0.1))
    assert z is not None and abs(z - (2.1 + FA.KIT["canopy_above"] + FA.KIT["canopy_thick"])) < 1e-9
    balcony = {"id": "r_L1_balkon", "level_id": "L1", "polygon": [(1, -2), (5, -2), (5, 0), (1, 0)]}
    b2, levels, e = _door_case(rooms=[balcony])
    z, why = FA.canopy_height(e, b2["openings"][0], levels[0], 2.1, b2, levels, None, (3.0, -0.1))
    assert z is None and "shelters it" in why
    roof = {"equations": [[0.0, 0.0, 2.6]], "outline": [(-1, -1), (11, -1), (11, 8), (-1, 8)], "thickness": 0.2,
            "type": "hip"}
    z, why = FA.canopy_height(e, b["openings"][0], levels[0], 2.1, b, levels, roof, (3.0, -0.1))
    assert z is None and "eaves" in why


def test_a_window_above_lowers_the_canopy_or_leaves_it_out():
    win = {"id": "w1", "type": "window", "wall_id": "w", "level_id": "L0", "center": [3, 0], "width": 1.2,
           "height": 0.4, "sill_height": 2.55}
    b, levels, e = _door_case(openings=[win])
    z, why = FA.canopy_height(e, b["openings"][0], levels[0], 2.1, b, levels, None, (3.0, -0.1))
    assert z is not None and abs(z - (2.55 - FA.CANOPY["window_gap_m"])) < 1e-9 and "under the window" in why
    low = dict(win, sill_height=2.25)
    b, levels, e = _door_case(openings=[low])
    z, why = FA.canopy_height(e, b["openings"][0], levels[0], 2.1, b, levels, None, (3.0, -0.1))
    assert z is None and "no room" in why
