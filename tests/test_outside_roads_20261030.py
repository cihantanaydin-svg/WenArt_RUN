"""UL162 (30 Oct 2026, real04 run 20261030-043021-full): "in the project roads going to nowhere we can increase the
roads outside, first the project section and closed off sections and outside roads". A drive's dead end runs on to the
plot's edge in its paving and joins a street outside the plot."""
from wenart import geometry as G
from wenart.blender import site as S


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def test_a_drive_dead_end_runs_to_the_plot_edge_and_meets_a_street_outside():
    # an L drive: a strip along x = 19-24 from the plot's south edge, a strip along y = 30-35 ending 5 m short of x = -6
    drive = {"id": "drive", "kind": "parking", "polygon": [(19, -4), (24, -4), (24, 35), (-1, 35), (-1, 30),
                                                           (19, 30)]}
    plot = _rect(-6, -4, 25, 36)
    extent = _rect(-40, -40, 60, 70)
    ends = S.road_dead_ends([drive], [_rect(0, 0, 15, 12)])
    assert {round(e["mid"][0], 1) for e in ends} == {21.5, -1.0}
    out = S.outside_roads([drive], plot, extent, _rect(0, 0, 15, 12))
    links = [a for a in out["areas"] if a["kind"] == "parking"]
    streets = [a for a in out["areas"] if a["kind"] == "road"]
    assert len(links) == 1 and min(p[0] for p in links[0]["polygon"]) <= -6 + 1e-6      # on to the plot's west edge
    assert streets and all(a["material"] == "asphalt" for a in streets)
    from shapely.geometry import Polygon
    for st in streets:                                                                   # outside the plot only
        assert Polygon(st["polygon"]).intersection(Polygon(plot)).area < 0.01
    # the street meets the drive's south end and the link's west end
    assert any(G.point_in_polygon((21.5, -5.0), st["polygon"]) for st in streets)
    assert any(G.point_in_polygon((-8.0, 32.5), st["polygon"]) for st in streets)


def test_a_drive_that_leads_somewhere_is_no_dead_end():
    drive = {"id": "drive", "kind": "parking", "polygon": _rect(0, 0, 5, 20)}
    garage = {"id": "garage_apron", "kind": "terrace", "polygon": _rect(-1, 20, 6, 26)}
    ends = S.road_dead_ends([drive, garage], [])
    assert all(e["mid"][1] < 10 for e in ends)                     # the end at the apron leads somewhere
    assert S.road_dead_ends([{"id": "t", "kind": "terrace", "polygon": _rect(0, 0, 5, 20)}], []) == []
