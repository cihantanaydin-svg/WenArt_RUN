"""UL162 (30 Oct 2026, real04 run 20261030-043021-full): "these 2 sections still not solved properly, it needs to be
only road". The pool terraces' flights up onto the drive were cut into the drive (UL129): steps and cheek blocks stood
in the road. A flight up onto a road is set into the sunken platform itself; the road stays whole."""
from wenart import geometry as G
from wenart.blender import site as S

FLAT = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def test_a_flight_up_onto_a_road_runs_down_into_its_own_platform():
    deck = {"id": "deck", "kind": "terrace", "z": -0.8, "polygon": _rect(0, 0, 5, 8), "steps_dir": "up",
            "steps_edge": 1, "flight_inward": True}
    gz = lambda x, y: 0.0                                           # noqa: E731 the road at the ground beside it
    fl = S.up_flight(deck, gz=gz)
    assert fl["inward"] and fl["count"] >= 4 and abs(fl["rise"] - 0.8) < 1e-6
    fp = fl["footprint"]
    assert all(G.point_in_polygon(p, deck["polygon"]) or min(abs(p[0] - 5.0), abs(p[0])) < 1e-6 for p in fp)
    steps, cheeks = S.up_flight_parts(fl, deck["z"], gz)
    xs = [v[0] for s in steps + cheeks for v in s[0]]
    zs = [v[2] for s in steps + cheeks for v in s[0]]
    assert max(xs) <= 5.0 + 1e-6                                     # nothing past the edge into the road
    assert max(zs) <= 0.0 + 1e-6                                     # nothing stands over the road's level
    tops = [max(v[2] for v in s[0]) for s in steps]
    assert tops == sorted(tops) and abs(tops[-1]) < 1e-6             # rising towards the edge, the top flush
    # the railing on that edge leaves the flight's gap
    runs = S.railing_runs((5, 0), (5, 8), 1, deck)
    assert len(runs) == 2


def test_the_drive_beside_a_sunken_deck_gets_no_cut():
    deck = {"id": "deck", "kind": "terrace", "z": -0.8, "polygon": _rect(0, 0, 5, 8), "steps_dir": "up",
            "steps_edge": 1, "flight_inward": True}
    drive = {"id": "drive", "kind": "parking", "z": 0.0, "polygon": _rect(5, -2, 10, 10), "sloped": True}
    deck["flight"] = S.up_flight(deck, gz=lambda x, y: 0.0)
    assert S.cut_flights([deck, drive]) == [] and not drive.get("cuts")
    assert "parking" in S.ROAD_KINDS
